from django import forms

from . import models

exception_codes = [
    'InvalidFormat', 'CoverageNotDefined', 'CurrentUpdateSequence', 'InvalidUpdateSequence', 'MissingParameterValue',
    'InvalidParameterValue'
]

AVAILABLE_INPUT_CRS = ["EPSG:4326"]
AVAILABLE_OUTPUT_CRS = ["EPSG:4326"]
NATIVE_CRS = ["EPSG:4326"]
AVAILABLE_FORMATS = ['GeoTIFF', 'NetCDF']
INTERPOLATION_OPTIONS = ['nearest neighbor', 'bilinear', 'bicubic', 'lost area', 'barycentric']


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


class GetCoverageForm(BaseRequestForm):
    """GetCoverage request form as defined by the OGC WCS 1.0 specification"""
    COVERAGE = forms.ModelChoiceField(queryset=models.CoverageOffering.objects.all(), to_field_name="name")
    CRS = forms.CharField()
    RESPONSE_CRS = forms.CharField(required=False)

    # One of the following is required.
    BBOX = forms.CharField()
    TIME = forms.CharField()

    # either width/height or resx/resy are required as a pair
    WIDTH = forms.IntegerField()
    HEIGHT = forms.IntegerField()
    RESX = forms.FloatField()
    RESY = forms.FloatField()

    INTERPOLATION = forms.ChoiceField(
        required=False, choices=((option, option) for option in INTERPOLATION_OPTIONS), initial="nearest neighbor")
    FORMAT = forms.ChoiceField(choices=((option, option) for option in AVAILABLE_FORMATS), initial="GeoTIFF")
    EXCEPTIONS = forms.CharField(required=False, initial="application/vnd.ogc.se_xml")

    #measurements are the only parameters available as an AxisDescription/rangeset
    measurements = forms.CharField()

    def clean_INTERPOLATION(self):
        if not self['INTERPOLATION'].html_name in self.data:
            return self.fields['INTERPOLATION'].initial
        return self.cleaned_data['INTERPOLATION']

    def clean(self):
        cleaned_data = super(GetCoverageForm, self).clean()
