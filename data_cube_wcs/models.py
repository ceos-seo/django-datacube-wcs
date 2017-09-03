from django.db import models


class CoverageOffering(models.Model):
    """Contains all information required for formatting coverage offering xml responses"""

    description = models.CharField(max_length=100)
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100)
    min_latitude = models.FloatField()
    max_latitude = models.FloatField()
    min_longitude = models.FloatField()
    max_longitude = models.FloatField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
