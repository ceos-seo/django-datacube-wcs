from django import forms

from dateutil import parser

from . import models
from .utils import utils

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

    CRS = forms.ChoiceField(choices=((option, option) for option in AVAILABLE_INPUT_CRS), initial="EPSG:4326")
    RESPONSE_CRS = forms.ChoiceField(choices=((option, option) for option in AVAILABLE_OUTPUT_CRS), initial="EPSG:4326")

    # One of the following is required.
    BBOX = forms.CharField(required=False)
    TIME = forms.CharField(required=False)

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
        """Meant to provide actual default values for various form fields if missing from GET"""
        if not self['INTERPOLATION'].html_name in self.data:
            return self.fields['INTERPOLATION'].initial
        return self.cleaned_data['INTERPOLATION']

    def clean_BBOX(self):
        split_bbox = self.cleaned_data['BBOX'].split(",")
        latitude_range = (split_bbox[1], split_bbox[3])
        longitude_range = (split_bbox[0], split_bbox[2])

        validation_cases = [
            not utils._ranges_intersect(latitude_range,
                                        (coverage_offering.min_latitude, coverage_offering.max_latitude)),
            not utils._ranges_intersect(longitude_range, (coverage.min_longitude, coverage.max_longitude)),
            latitude_range != sorted(latitude_range), longitude_range != sorted(longitude_range)
        ]

        # if the ranges are not well formed...
        if True in validation_cases:
            self.add_error('latitude_range', "")
            self.add_error('longitude_range', "")
            return

        self.cleaned_data['latitude'] = latitude_range
        self.cleaned_data['longitude'] = longitude_range

    def clean_TIME(self):
        time_ranges = []
        times = []
        _time_type_range = '/' in self.cleaned_data['TIME']
        if _time_type_range:
            time_range = self.cleaned_data['TIME'].split(",")
            time_ranges = map(lambda r: r.split("/"), time_range)
            time_ranges = list(map(lambda r: (parser.parse(r[0]), parser.parse(r[1])), time_ranges))
        else:
            date_list = self.cleaned_data['TIME'].split(",")
            times = list(map(lambda t: parser.parse(t), date_list))

        self.cleaned_data['time_ranges'] = time_ranges
        self.cleaned_data['times'] = times

    def clean(self):
        cleaned_data = super(GetCoverageForm, self).clean()

        coverage_offering = cleaned_data['COVERAGE']

        if not (cleaned_data['BBOX'] or cleaned_data['TIME']):
            self.add_error("BBOX", "")
            self.add_error("TIME", "")

        if not ('RESX' in cleaned_data and 'RESY' in cleaned_data) or ('WIDTH' in cleaned_data and
                                                                       'HEIGHT' in cleaned_data):
            self.add_error('RESX', "")
            self.add_error('RESY', "")
            self.add_error('HEIGHT', "")
            self.add_error('WIDTH', "")
