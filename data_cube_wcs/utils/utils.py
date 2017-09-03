from . import data_access_api
from ..models import CoverageOffering


def update_coverages():
    """Uses the Data Cube data access api to update database representations of coverages"""

    dc = data_access_api.DataAccessApi()
    product_details = dc.dc.list_products()[dc.dc.list_products()['format'] == "NetCDF"]
    product_details['label'] = product_details.apply(lambda row: "{} - {}".format(row['platform'], row['name']), axis=1)

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
    product_details['end_time'] = product_details.apply(lambda row: extent_data[row['name']]['time_extents'][1], axis=1)

    list_of_dicts = product_details[[
        'name', 'description', 'label', 'min_latitude', 'max_latitude', 'min_longitude', 'max_longitude', 'start_time',
        'end_time'
    ]].to_dict('records')

    for model in list_of_dicts:
        CoverageOffering.objects.update_or_create(**model)
