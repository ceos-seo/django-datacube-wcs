from django.db import models
from django.db import IntegrityError
import pytz
import datacube
from . import utils


class CoverageOffering(models.Model):
    """Contains all information required for formatting coverage offering xml responses"""

    description = models.CharField(max_length=250)
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100)
    min_latitude = models.FloatField()
    max_latitude = models.FloatField()
    min_longitude = models.FloatField()
    max_longitude = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    crs = models.CharField(max_length=50)
    available_formats = models.ManyToManyField('Format', blank=True)

    offer_temporal = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_min_point(self):
        """Get a lon lat point as per the gml:pos requirement"""
        return "{} {}".format(self.min_longitude, self.min_latitude)

    def get_max_point(self):
        """Get a lon lat point as per the gml:pos requirement"""
        return "{} {}".format(self.max_longitude, self.max_latitude)

    def get_start_time(self):
        """Get a iso8601 formatted datetime"""
        return self.start_time.isoformat()

    def get_end_time(self):
        """Get a iso8601 formatted datetime"""
        return self.end_time.isoformat()

    def get_temporal_domain(self):
        """The temporal domain is specified as one or more iso8601 datetimes"""
        return [
            date.get_timestring()
            for date in CoverageTemporalDomainEntry.objects.filter(coverage_offering=self).order_by('date')
        ]

    def get_rangeset(self):
        """Get the set of rangeset entries that match this coverage"""
        return CoverageRangesetEntry.objects.filter(coverage_offering=self).order_by('pk')

    def get_measurements(self):
        """Get a list of measurements for the coverage"""
        return self.get_rangeset().values_list('band_name', flat=True)

    def get_nodata_values(self):
        """Get a list of nodata values for the coverage"""
        return self.get_rangeset().values_list('null_value', flat=True)

    def get_available_formats(self):
        """Get all the formats, ordered by pk. GeoTIFF must be first, hence the ordering."""
        return self.available_formats.all().order_by('pk')

    @classmethod
    def update_or_create_coverages(cls, update_aux=False):
        """Uses the Data Cube data access api to update database representations of coverages"""

        with datacube.Datacube(config=utils.config_from_settings()) as dc:
            product_details = dc.list_products()[dc.list_products()['format'] == "NetCDF"]
            product_details['label'] = product_details.apply(
                lambda row: "{} - {}".format(row['platform'], row['name']), axis=1)

            extent_data = {
                product: utils.get_datacube_metadata(dc, product)
                for product in product_details['name'].values
            }

            product_details['min_latitude'] = product_details.apply(
                lambda row: extent_data[row['name']]['lat_extents'][0], axis=1)
            product_details['max_latitude'] = product_details.apply(
                lambda row: extent_data[row['name']]['lat_extents'][1], axis=1)
            product_details['min_longitude'] = product_details.apply(
                lambda row: extent_data[row['name']]['lon_extents'][0], axis=1)
            product_details['max_longitude'] = product_details.apply(
                lambda row: extent_data[row['name']]['lon_extents'][1], axis=1)
            product_details['start_time'] = product_details.apply(
                lambda row: extent_data[row['name']]['time_extents'][0].replace(tzinfo=pytz.UTC), axis=1)
            product_details['end_time'] = product_details.apply(
                lambda row: extent_data[row['name']]['time_extents'][1].replace(tzinfo=pytz.UTC), axis=1)

            list_of_dicts = product_details[[
                'name', 'description', 'label', 'min_latitude', 'max_latitude', 'min_longitude', 'max_longitude',
                'start_time', 'end_time', 'crs'
            ]].to_dict('records')

            for model in list_of_dicts:
                try:
                    new_model = cls(**model)
                    new_model.save()
                    new_model.available_formats.add(Format.objects.get(name="GeoTIFF"))
                    new_model.save()
                except IntegrityError:
                    cls.objects.filter(name=model['name']).update(**model)

        if update_aux:
            cls.create_rangeset()
            cls.create_temporal_domain()

    @classmethod
    def create_temporal_domain(cls):
        """Save off a series of date models for each coverage acquisition date"""

        def get_acquisition_dates(coverage):
            with datacube.Datacube(config=utils.config_from_settings()) as dc:
                return map(lambda d: d.replace(tzinfo=pytz.UTC), utils.list_acquisition_dates(dc, coverage.name))

        for coverage in cls.objects.all():
            temporal_domain = [
                CoverageTemporalDomainEntry(coverage_offering=coverage, date=date)
                for date in get_acquisition_dates(coverage)
                if not CoverageTemporalDomainEntry.objects.filter(coverage_offering=coverage, date=date).exists()
            ]

            CoverageTemporalDomainEntry.objects.bulk_create(temporal_domain)

    @classmethod
    def create_rangeset(cls):
        """Save off a model for each band/nodata value"""
        with datacube.Datacube(config=utils.config_from_settings()) as dc:
            for coverage in cls.objects.all():
                bands = dc.list_measurements().ix[coverage.name]
                nodata_values = bands['nodata'].values
                band_names = bands.index.values

                rangeset = [
                    CoverageRangesetEntry(coverage_offering=coverage, band_name=band_name, null_value=nodata_value)
                    for band_name, nodata_value in zip(band_names, nodata_values)
                    if not CoverageRangesetEntry.objects.filter(
                        coverage_offering=coverage, band_name=band_name, null_value=nodata_value).exists()
                ]

                CoverageRangesetEntry.objects.bulk_create(rangeset)


class CoverageTemporalDomainEntry(models.Model):
    """Holds the temporal domain of given coverages so they don't need to be fetched by the DC API each call"""

    coverage_offering = models.ForeignKey(CoverageOffering, on_delete=models.CASCADE)
    date = models.DateTimeField()

    class Meta:
        unique_together = (('coverage_offering', 'date'))

    def get_timestring(self):
        return self.date.replace(tzinfo=None).isoformat()


class CoverageRangesetEntry(models.Model):
    """Holds the band name/null value combination needed for a RangeSet Element"""

    coverage_offering = models.ForeignKey(CoverageOffering, on_delete=models.CASCADE)
    band_name = models.CharField(max_length=50)
    null_value = models.FloatField(default=-9999)


class Format(models.Model):
    """Contains a format and the content-type headers for a GetCoverage response"""

    name = models.CharField(max_length=50, unique=True)
    content_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def get_http_response(self, coverage_offering, dataset, crs):
        """Get the binary/bytes-like http response. Defaults to GeoTIFF

        Acts as a passthrough to the proper output formatting func based on self.name

        Args:
            coverage_offering: CoverageOffering model
            dataset: dataset to write to the output
            crs: dataset crs

        Returns:
            Http formatted bytes-like response

        """
        response_mapping = {
            'GeoTIFF': utils.get_tiff_response,
            'RGB_GeoTIFF': utils.get_tiff_response,
            'Filtered_GeoTIFF': utils.get_tiff_response,
            'netCDF': utils.get_netcdf_response
        }
        return response_mapping.get(self.name, utils.get_tiff_response)(
            coverage_offering, self.process_dataset(coverage_offering, dataset), crs)

    def process_dataset(self, coverage_offering, dataset):
        """Apply any preprocessing affiliated with the format type here

        Examples include rgb -> drop all non rgb vars and order the remaining as rgb
        filter -> filter out clouds/etc. and drop all qa bands

        Based on coverage offering name - e.g. different behaviors for landsat/s1/etc.
        and on self.name

        """

        def abs_divide(ds, bands):
            ds["_".join(bands)] = abs(ds[bands[0]] / ds[bands[1]])
            return ds[[*bands, "_".join(bands)]]

        # this is pretty much all bad
        processing_map = {
            'RGB_GeoTIFF': {
                'landsat': lambda ds: ds[['red', 'green', 'blue']],
                'alos': lambda ds: ds.pipe(abs_divide, bands=['hh', 'hv']).fillna(0),
                'sentinel': lambda ds: ds.pipe(abs_divide, bands=['vv', 'vh']).fillna(0)
            },
            'Filtered_GeoTIFF': {
                'landsat': lambda ds: ds[['red', 'green', 'blue','nir','swir1','swir2']]
                                        .where(utils.create_bit_mask(ds['pixel_qa'], valid_bits=[1, 2]))
                                        .fillna(-9999)
            }
        }

        _type = 'landsat' if any(
            ext in coverage_offering.name for ext in ['ls5', 'ls7', 'ls8']
        ) else 'sentinel' if 's1_gamma' in coverage_offering.name else 'alos' if 'alos' in coverage_offering.name else ""

        processing_function = processing_map.get(self.name, {}).get(_type, lambda d: d)

        return dataset.pipe(processing_function)
