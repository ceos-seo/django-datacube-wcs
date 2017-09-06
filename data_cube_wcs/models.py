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

    offer_temporal = models.BooleanField(default=True)

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

    def get_temporal_domain(self, iso8601=True):
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
                'start_time', 'end_time'
            ]].to_dict('records')

            for model in list_of_dicts:
                try:
                    cls(**model).save()
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
