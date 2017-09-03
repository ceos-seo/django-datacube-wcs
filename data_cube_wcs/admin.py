from django.contrib import admin

from . import models


class CoverageOfferingAdmin(admin.ModelAdmin):
    list_display = ('name', 'label')


admin.site.register(models.CoverageOffering, CoverageOfferingAdmin)
