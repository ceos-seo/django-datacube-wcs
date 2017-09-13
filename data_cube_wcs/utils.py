from django.apps import apps
from datetime import datetime, date, timedelta
from django.conf import settings

import xarray as xr
import numpy as np
import collections
from rasterio.io import MemoryFile

from datacube.config import LocalConfig
import datacube
import configparser


def form_to_data_cube_parameters(form_instance):
    """Converts some of the all caps/other form data parameters to the required Data Cube parameters"""
    individual_dates = form_instance.cleaned_data['times']
    date_ranges = form_instance.cleaned_data['time_ranges']

    return {
        'product': form_instance.cleaned_data['coverage'].name,
        'latitude': form_instance.cleaned_data['latitude'],
        'longitude': form_instance.cleaned_data['longitude'],
        'measurements': form_instance.cleaned_data['measurements'],
        'resolution': (form_instance.cleaned_data['resy'], form_instance.cleaned_data['resx']),
        'crs': form_instance.cleaned_data['crs'],
        'resampling': form_instance.cleaned_data['resampling']
    }, individual_dates, date_ranges


def get_stacked_dataset(coverage_offering, parameters, individual_dates, date_ranges):
    """Get a dataset using either a list of single dates or a list of ranges

    Args:
        parameters: dictionary-like containing all the parameters needed for a dc.load call
        individual_dates: list/iterable of datetimes
        date_ranges: list/iterable of two element datetime tuples

    Returns:
        dataset containing all requested data

    """

    def _get_datetime_range_containing(*time_ranges):
        return (min(time_ranges) - timedelta(seconds=1), max(time_ranges) + timedelta(seconds=1))

    def _clear_attrs(dataset):
        """Clear out all attributes on an xarray dataset to write to disk."""
        dataset.attrs = collections.OrderedDict()
        for band in dataset:
            dataset[band].attrs = collections.OrderedDict()

    rangeset = apps.get_model("data_cube_wcs.CoverageRangesetEntry").objects.filter(coverage_offering=coverage_offering)

    full_date_ranges = [_get_datetime_range_containing(date) for date in individual_dates]
    full_date_ranges.extend(date_ranges)

    data_array = []
    with datacube.Datacube(config=config_from_settings()) as dc:
        for _range in full_date_ranges:
            product_data = dc.load(time=_range, **parameters)
            if 'time' in product_data:
                data_array.append(product_data.copy(deep=True))

    data = None
    if len(data_array) > 0:
        combined_data = xr.concat(data_array, 'time')
        data = combined_data.reindex({'time': sorted(combined_data.time.values)})
        if data.dims['time'] > 1:
            data = data.apply(
                lambda ds: ds.where(ds != ds.nodata).mean('time', skipna=True).fillna(ds.nodata), keep_attrs=True)
        _clear_attrs(data)
        if 'time' in data:
            data = data.isel(time=0, drop=True)

    # if there isn't any data, we can assume that there was no data for the acquisition
    if data is None:
        with datacube.Datacube(config=config_from_settings()) as dc:
            extents = dc.load(dask_chunks={}, **parameters)

            latitude_range = (parameters.get('latitude')[0], parameters.get('latitude')[1])
            longitude_range = (parameters.get('longitude')[0], parameters.get('longitude')[1])

            latitude = extents['latitude'] if 'latitude' in extents else np.linspace(
                latitude_range[0],
                latitude_range[1],
                num=abs((latitude_range[1] - latitude_range[0]) / parameters['resolution'][0]))
            longitude = extents['longitude'] if 'longitude' in extents else np.linspace(
                longitude_range[0],
                longitude_range[1],
                num=abs((longitude_range[1] - longitude_range[0]) / parameters['resolution'][1]))
            data = xr.Dataset(
                {
                    band: (('latitude', 'longitude'), np.full(
                        (len(latitude), len(longitude)),
                        rangeset.get(band_name=band).null_value if rangeset.filter(band_name=band).exists() else 0))
                    for band in parameters['measurements']
                },
                coords={'latitude': latitude,
                        'longitude': longitude}).astype('int16')

    return data


def create_bit_mask(data_array, valid_bits, no_data=-9999):
    """Create a boolean bit mask from a list of valid bits
    Args:
        data_array: xarray data array to extract bit information for.
        valid_bits: array of ints representing what bits should be considered valid.
        nodata: nodata value for the data array.
    Returns:
        Boolean mask signifying valid data.
    """
    assert isinstance(valid_bits, list) and isinstance(valid_bits[0], int), "Valid bits must be a list of integer bits"
    #do bitwise and on valid mask - all zeros means no intersection e.g. invalid else return a truthy value?
    valid_mask = sum([1 << valid_bit for valid_bit in valid_bits])
    clean_mask = (data_array & valid_mask).astype('bool')

    return clean_mask.values


def get_datacube_metadata(dc, product):
    """Get the extents and number of tiles for a given product"""
    dataset = dc.load(product, dask_chunks={})

    if not dataset:
        return {
            'lat_extents': (0, 0),
            'lon_extents': (0, 0),
            'time_extents': (datetime(2000, 1, 1), datetime(2000, 1, 1)),
            'scene_count': 0,
            'pixel_count': 0,
            'tile_count': 0,
            'storage_units': {}
        }

    lon_min, lat_min, lon_max, lat_max = dataset.geobox.extent.envelope
    return {
        'lat_extents': (lat_min, lat_max),
        'lon_extents': (lon_min, lon_max),
        'time_extents': (dataset.time[0].values.astype('M8[ms]').tolist(),
                         dataset.time[-1].values.astype('M8[ms]').tolist()),
        'tile_count':
        dataset.time.size,
        'pixel_count':
        dataset.geobox.shape[0] * dataset.geobox.shape[1],
    }


def list_acquisition_dates(dc, product):
    """Get a list of acquisition dates for a given product"""
    dataset = dc.load(product, dask_chunks={})

    if not dataset:
        return []
    return dataset.time.values.astype('M8[ms]').tolist()


def get_tiff_response(coverage_offering, dataset, crs):
    """Uses rasterio MemoryFiles in order to return a streamable GeoTiff response"""

    supported_dtype_map = {
        'uint8': 1,
        'uint16': 2,
        'int16': 3,
        'uint32': 4,
        'int32': 5,
        'float32': 6,
        'float64': 7,
        'complex': 9,
        'complex64': 10,
        'complex128': 11,
    }

    dtype_list = [dataset[array].dtype for array in dataset.data_vars]
    dtype = str(max(dtype_list, key=lambda d: supported_dtype_map[str(d)]))
    rangeset = apps.get_model("data_cube_wcs.CoverageRangesetEntry").objects.filter(coverage_offering=coverage_offering)

    dataset = dataset.astype(dtype)
    with MemoryFile() as memfile:
        with memfile.open(
                driver="GTiff",
                width=dataset.dims['longitude'],
                height=dataset.dims['latitude'],
                count=len(dataset.data_vars),
                transform=_get_transform_from_xr(dataset),
                crs=crs,
                dtype=dtype) as dst:
            for idx, band in enumerate(dataset.data_vars, start=1):
                dst.write(dataset[band].values, idx)
            dst.set_nodatavals([
                rangeset.get(band_name=band).null_value if rangeset.filter(band_name=band).exists() else 0
                for band in dataset.data_vars
            ])
        return memfile.read()


def get_netcdf_response(coverage_offering, dataset, crs):
    """Uses a standard xarray function to create a bytes-like data stream for http response"""
    dataset.attrs['crs'] = crs
    return dataset.to_netcdf()


def _get_transform_from_xr(dataset):
    """Create a geotransform from an xarray dataset."""

    from rasterio.transform import from_bounds
    geotransform = from_bounds(dataset.longitude[0], dataset.latitude[-1], dataset.longitude[-1], dataset.latitude[0],
                               len(dataset.longitude), len(dataset.latitude))

    return geotransform


def _ranges_intersect(x, y):
    return x[0] <= y[1] and y[0] <= x[1]


def config_from_settings():
    """Create or load a Datacube configuration from the django settings"""
    if hasattr(settings, 'DATACUBE_CONF_PATH'):
        return settings.DATACUBE_CONF_PATH
    config = configparser.ConfigParser()
    config['datacube'] = {
        'db_password': settings.DATABASES['default']['PASSWORD'],
        'db_connection_timeout': '60',
        'db_username': settings.DATABASES['default']['USER'],
        'db_database': settings.DATABASES['default']['NAME'],
        'db_hostname': settings.DATABASES['default']['HOST']
    }

    return LocalConfig(config)
