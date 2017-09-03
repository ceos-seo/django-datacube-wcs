from django.db import models

from utils import data_access_api


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
        with data_access_api.DataAccessApi() as dc:
            return map(lambda d: d.isoformat(), dc.list_acquisition_dates(self.name))
