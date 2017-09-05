from django.apps import apps
from datetime import datetime, timedelta
import xarray as xr
import numpy as np
import collections
from rasterio.io import MemoryFile

from . import data_access_api


def form_to_data_cube_parameters(form_instance):
    """Converts some of the all caps/other form data parameters to the required Data Cube parameters"""
    individual_dates = form_instance.cleaned_data['times']
    date_ranges = form_instance.cleaned_data['time_ranges']

    return {
        'product': form_instance.cleaned_data['COVERAGE'].name,
        'latitude': form_instance.cleaned_data['latitude'],
        'longitude': form_instance.cleaned_data['longitude'],
        'measurements': form_instance.cleaned_data['measurements'],
        'resolution': (form_instance.cleaned_data['RESY'], form_instance.cleaned_data['RESX']),
        'crs': form_instance.cleaned_data['CRS'],
        'resampling': form_instance.cleaned_data['resampling']
    }, individual_dates, date_ranges


def get_stacked_dataset(parameters, individual_dates, date_ranges):
    """Get a dataset using either a list of single dates or a list of ranges

    Args:
        parameters: dictionary-like containing all the parameters needed for a dc.load call
        individual_dates: list/iterable of datetimes
        date_ranges: list/iterable of two element datetime tuples

    Returns:
        dataset containing all requested data

    """

    def _get_datetime_range_containing(*time_ranges):
        return (min(time_ranges) - timedelta(hours=4, microseconds=1),
                max(time_ranges) + timedelta(hours=4, microseconds=1))

    def _clear_attrs(dataset):
        """Clear out all attributes on an xarray dataset to write to disk."""
        dataset.attrs = collections.OrderedDict()
        for band in dataset:
            dataset[band].attrs = collections.OrderedDict()

    full_date_ranges = [_get_datetime_range_containing(date) for date in individual_dates]
    full_date_ranges.extend(date_ranges)

    data_array = []
    with data_access_api.DataAccessApi() as dc:
        for _range in full_date_ranges:
            product_data = dc.get_dataset_by_extent(time=_range, **parameters)
            if 'time' in product_data:
                data_array.append(product_data.copy(deep=True))

    data = None
    if len(data_array) > 0:
        combined_data = xr.concat(data_array, 'time')
        data = combined_data.reindex({'time': sorted(combined_data.time.values)})
        _clear_attrs(data)

    # if there isn't any data, we can assume that there was no data for the acquisition
    if data is None:
        with data_access_api.DataAccessApi() as dc:
            extents = dc.get_full_dataset_extent(**parameters)
            latitude = extents['latitude']
            longitude = extents['longitude']
            data = xr.Dataset(
                {
                    band: (('latitude', 'longitude'), np.full((len(latitude), len(longitude)), -9999))
                    for band in parameters['measurements']
                },
                coords={'latitude': extents['latitude'],
                        'longitude': extents['longitude']})

    return data


def get_tiff_response(dataset, crs, format):
    """Uses rasterio MemoryFiles in order to return a streamable GeoTiff response"""
    with MemoryFile() as memfile:
        with memfile.open(
                driver=format,
                width=dataset.dims['longitude'],
                height=dataset.dims['latitude'],
                count=len(dataset.data_vars),
                transform=_get_transform_from_xr(dataset),
                crs=crs,
                nodata=-9999,
                dtype='float64') as dst:
            for idx, band in enumerate(dataset.data_vars, start=1):
                dst.write(dataset[band].values, idx)
        return memfile.read()


def get_netcdf_response(dataset, crs, format):
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
