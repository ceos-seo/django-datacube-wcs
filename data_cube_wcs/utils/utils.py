from django.apps import apps
from datetime import datetime, timedelta
import xarray as xr
import collections

from . import data_access_api


def update_coverages():
    """Uses the Data Cube data access api to update database representations of coverages"""

    with data_access_api.DataAccessApi() as dc:
        product_details = dc.dc.list_products()[dc.dc.list_products()['format'] == "NetCDF"]
        product_details['label'] = product_details.apply(
            lambda row: "{} - {}".format(row['platform'], row['name']), axis=1)

        extent_data = {product: dc.get_datacube_metadata(product) for product in product_details['name'].values}

        product_details['min_latitude'] = product_details.apply(
            lambda row: extent_data[row['name']]['lat_extents'][0], axis=1)
        product_details['max_latitude'] = product_details.apply(
            lambda row: extent_data[row['name']]['lat_extents'][1], axis=1)
        product_details['min_longitude'] = product_details.apply(
            lambda row: extent_data[row['name']]['lon_extents'][0], axis=1)
        product_details['max_longitude'] = product_details.apply(
            lambda row: extent_data[row['name']]['lon_extents'][1], axis=1)
        product_details['start_time'] = product_details.apply(
            lambda row: extent_data[row['name']]['time_extents'][0], axis=1)
        product_details['end_time'] = product_details.apply(
            lambda row: extent_data[row['name']]['time_extents'][1], axis=1)

        list_of_dicts = product_details[[
            'name', 'description', 'label', 'min_latitude', 'max_latitude', 'min_longitude', 'max_longitude',
            'start_time', 'end_time'
        ]].to_dict('records')

        for model in list_of_dicts:
            apps.get_model("data_cube_wcs.CoverageOffering").objects.update_or_create(**model)


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
    """
    """

    def _get_datetime_range_containing(*time_ranges):
        return (min(time_ranges) - timedelta(microseconds=1), max(time_ranges) + timedelta(microseconds=1))

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
    return data


def get_tiff_response(dataset):
    """"""
    with MemoryFile() as memfile:
        with memfile.open(
                driver=coverage_data.cleaned_data['FORMAT'],
                width=dataset.dims['longitude'],
                height=dataset.dims['latitude'],
                count=len(dataset.data_vars),
                transform=utils._get_transform_from_xr(dataset),
                crs=coverage_data.cleaned_data['RESPONSE_CRS'],
                nodata=-9999,
                dtype='float64') as dst:
            for idx, band in enumerate(dataset.data_vars, start=1):
                dst.write(dataset[band].values, idx)
        return memfile.read()


def get_netcdf_response(dataset):
    """"""
    return dataset.to_netcdf()


def _get_transform_from_xr(dataset):
    """Create a geotransform from an xarray dataset.
    """

    from rasterio.transform import from_bounds
    geotransform = from_bounds(dataset.longitude[0], dataset.latitude[-1], dataset.longitude[-1], dataset.latitude[0],
                               len(dataset.longitude), len(dataset.latitude))

    return geotransform


def _ranges_intersect(x, y):
    return x[0] <= y[1] and y[0] <= x[1]
