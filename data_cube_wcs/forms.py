from django import forms

from . import models


class BaseRequestForm(forms.Form):
    """Base WCS request parameters as defined by the OGC WCS 1.0 specification"""

    REQUEST = forms.ChoiceField(
        choices=(("GetCapabilities", "GetCapabilities"), ("DescribeCoverage", "DescribeCoverage"),
                 ("GetCoverage", "GetCoverage")),
        initial="GetCapabilities")
    VERSION = forms.CharField(required=False, initial="1.0.0")
    SERVICE = forms.ChoiceField(choices=(("WCS", "WCS"), ("WMS", "WMS")), initial="WCS")


class GetCapabilitiesForm(BaseRequestForm):
    """GetCapabilities request form as defined by the OGC WCS 1.0 specification"""

    SECTION = forms.ChoiceField(
        required=False,
        choices=(("WCS_Capabilities/Service", "WCS_Capabilities/Service"),
                 ("WCS_Capabilities/Capability", "WCS_Capabilities/Capability"),
                 ("WCS_Capabilities/ContentMetadata", "WCS_Capabilities/ContentMetadata")))
    UPDATESEQUENCE = forms.CharField(required=False)


class DescribeCoverageForm(BaseRequestForm):
    """DescribeCoverage request form as defined by the OGC WCS 1.0 specification"""
    COVERAGE = forms.ModelMultipleChoiceField(queryset=models.CoverageOffering.objects.all(), to_field_name='name')


class GetCoverageForm(BaseRequestForm):
    """GetCoverage request form as defined by the OGC WCS 1.0 specification"""
    COVERAGE = forms.CharField()
    CRS = forms.CharField()
    RESPONSE_CRS = forms.CharField()
    BBOX = forms.CharField()
    TIME = forms.CharField()
    WIDTH = forms.IntegerField()
    HEIGHT = forms.IntegerField()
    RESX = forms.FloatField()
    RESY = forms.FloatField()

    INTERPOLATION = forms.ChoiceField(choices=(), initial="")
    FORMAT = forms.ChoiceField()
    EXCEPTIONS = forms.CharField()
    PARAMETERS = forms.CharField()
