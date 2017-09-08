from django.contrib import admin

from . import models


class CoverageOfferingAdmin(admin.ModelAdmin):
    list_display = ('name', 'label')


class CoverageRangesetAdmin(admin.ModelAdmin):
    list_display = ('coverage_offering', 'band_name')
    list_filter = ('coverage_offering',)


admin.site.register(models.CoverageOffering, CoverageOfferingAdmin)
admin.site.register(models.CoverageRangesetEntry, CoverageRangesetAdmin)
