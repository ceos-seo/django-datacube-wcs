from django import forms

from dateutil import parser

from . import models
from .utils import utils

exception_codes = [
    'InvalidFormat', 'CoverageNotDefined', 'CurrentUpdateSequence', 'InvalidUpdateSequence', 'MissingParameterValue',
    'InvalidParameterValue'
]

field_exception_map = {
    'REQUEST': 'InvalidParameterValue',
    'VERSION': 'InvalidParameterValue',
    'SERVICE': 'InvalidParameterValue',
    'SECTION': 'InvalidParameterValue',
    'UPDATESEQUENCE': 'InvalidParameterValue',
    'COVERAGE': 'InvalidParameterValue',
    'CRS': 'InvalidParameterValue',
    'RESPONSE_CRS': 'InvalidParameterValue',
    'BBOX': 'InvalidParameterValue',
    'TIME': 'InvalidParameterValue',
    'WIDTH': 'InvalidParameterValue',
    'HEIGHT': 'InvalidParameterValue',
    'RESX': 'InvalidParameterValue',
    'RESY': 'InvalidParameterValue',
    'HEIGHT': 'InvalidParameterValue',
    'WIDTH': 'InvalidParameterValue',
    'INTERPOLATION': 'InvalidParameterValue',
    'FORMAT': 'InvalidFormat',
    'EXCEPTIONS': 'InvalidParameterValue',
    'measurements': 'InvalidParameterValue'
}

AVAILABLE_INPUT_CRS = ["EPSG:4326"]
AVAILABLE_OUTPUT_CRS = ["EPSG:4326"]
NATIVE_CRS = ["EPSG:4326"]
AVAILABLE_FORMATS = {'GTiff': 'image/tiff', 'netCDF': 'application/x-netcdf'}
INTERPOLATION_OPTIONS = {'nearest neighbor': 'nearest', 'bilinear': 'bilinear', 'bicubic': 'cubic'}


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
        choices=(("/", "/"), ("WCS_Capabilities/Service", "WCS_Capabilities/Service"),
                 ("WCS_Capabilities/Capability", "WCS_Capabilities/Capability"),
                 ("WCS_Capabilities/ContentMetadata", "WCS_Capabilities/ContentMetadata")))
    UPDATESEQUENCE = forms.CharField(required=False)

    def clean(self):
        """Basic validation for the capabilities request"""
        cleaned_data = super(GetCapabilitiesForm, self).clean()

        # commented out as I'm not currently messing with the update sequence stuff.
        # if 'UPDATESEQUENCE' in cleaned_data and cleaned_data['UPDATESEQUENCE'] != "0":
        #     self.add_error("UPDATESEQUENCE", "")


class GetCoverageForm(BaseRequestForm):
    """GetCoverage request form as defined by the OGC WCS 1.0 specification"""
    COVERAGE = forms.ModelChoiceField(queryset=models.CoverageOffering.objects.all(), to_field_name="name")

    CRS = forms.ChoiceField(choices=((option, option) for option in AVAILABLE_INPUT_CRS), initial="EPSG:4326")
    RESPONSE_CRS = forms.ChoiceField(
        required=False, choices=((option, option) for option in AVAILABLE_OUTPUT_CRS), initial="EPSG:4326")

    # One of the following is required.
    BBOX = forms.CharField(required=False)
    TIME = forms.CharField(required=False)

    # either width/height or resx/resy are required as a pair
    WIDTH = forms.IntegerField(required=False)
    HEIGHT = forms.IntegerField(required=False)
    RESX = forms.FloatField(required=False)
    RESY = forms.FloatField(required=False)

    INTERPOLATION = forms.ChoiceField(
        required=False, choices=((option, option) for option in INTERPOLATION_OPTIONS), initial="nearest neighbor")
    FORMAT = forms.ChoiceField(choices=((option, option) for option in AVAILABLE_FORMATS), initial="GTiff")
    EXCEPTIONS = forms.CharField(required=False, initial="application/vnd.ogc.se_xml")

    #measurements are the only parameters available as an AxisDescription/rangeset
    measurements = forms.CharField(required=False)

    def clean_RESPONSE_CRS(self):
        """Meant to provide actual default values for various form fields if missing from GET"""
        if not self['RESPONSE_CRS'].html_name in self.data:
            return self.fields['RESPONSE_CRS'].initial
        return self.cleaned_data['RESPONSE_CRS']

    def clean_INTERPOLATION(self):
        """Meant to provide actual default values for various form fields if missing from GET"""
        if not self['INTERPOLATION'].html_name in self.data:
            return self.fields['INTERPOLATION'].initial
        return self.cleaned_data['INTERPOLATION']

    def clean(self):
        """Basic validation of the GetCoverage parameters according to the OGC WCS 1.0 specification.

        Pretty monolithic implementation of cleaning - done for a few reasons:
            We don't want to continue validation if we encounter an error, hence the Returns
            Handles the semi-optional parameter sets like the time -or- bbox inputs, resxy or height/width
            Ensures that the ranges entered actually exist in the coverage

        """
        cleaned_data = super(GetCoverageForm, self).clean()

        if 'COVERAGE' not in cleaned_data:
            self.add_error("COVERAGE", "")
            return

        if not (cleaned_data['BBOX'] or cleaned_data['TIME']):
            self.add_error("BBOX", "")
            self.add_error("TIME", "")
            return

        if cleaned_data.get('BBOX', None):
            split_bbox = self.cleaned_data['BBOX'].split(",")
            coverage_offering = self.cleaned_data['COVERAGE']

            latitude_range = (float(split_bbox[1]), float(split_bbox[3]))
            longitude_range = (float(split_bbox[0]), float(split_bbox[2]))

            validation_cases = [
                not utils._ranges_intersect(latitude_range,
                                            (coverage_offering.min_latitude, coverage_offering.max_latitude)),
                not utils._ranges_intersect(longitude_range,
                                            (coverage_offering.min_longitude, coverage_offering.max_longitude)),
                latitude_range != tuple(sorted(latitude_range)), longitude_range != tuple(sorted(longitude_range))
            ]

            # if the ranges are not well formed...
            if True in validation_cases:
                self.add_error('BBOX', "")
                return

            self.cleaned_data['latitude'] = latitude_range
            self.cleaned_data['longitude'] = longitude_range
        else:
            self.cleaned_data['latitude'] = (coverage_offering.min_latitude, coverage_offering.max_latitude)
            self.cleaned_data['longitude'] = (coverage_offering.min_longitude, coverage_offering.max_longitude)

        if cleaned_data.get('TIME', None):
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
        else:
            self.cleaned_data['time_ranges'] = [(coverage_offering.start_time, coverage_offering.end_time)]
            self.cleaned_data['times'] = []

        if (cleaned_data.get('RESX', None) and cleaned_data.get('RESY', None)):
            if cleaned_data['RESX'] < 0 or cleaned_data['RESY'] > 0:
                self.add_error('RESX', "")
                self.add_error('RESY', "")
                return
        elif (cleaned_data.get('WIDTH', None) and cleaned_data.get('HEIGHT', None)):
            if cleaned_data['HEIGHT'] < 0 or cleaned_data['WIDTH'] < 0:
                self.add_error('HEIGHT', "")
                self.add_error('WIDTH', "")
                return
            self.cleaned_data['RESX'] = (
                self.cleaned_data['longitude'][1] - self.cleaned_data['longitude'][0]) / cleaned_data['WIDTH']
            self.cleaned_data['RESY'] = -1 * (
                self.cleaned_data['latitude'][1] - self.cleaned_data['latitude'][0]) / cleaned_data['HEIGHT']
        else:
            self.add_error('RESX', "")
            self.add_error('RESY', "")
            self.add_error('HEIGHT', "")
            self.add_error('WIDTH', "")
            return

        if cleaned_data.get('measurements', None):
            valid_measurements = coverage_offering.get_measurements()
            request_measurements = cleaned_data['measurements'].split(",")
            # if the measurements aren't all valid, raise
            if len(list(set(valid_measurements) & set(request_measurements))) != len(request_measurements):
                self.add_error("measurements", "")
            else:
                self.cleaned_data['measurements'] = request_measurements
        else:
            self.cleaned_data['measurements'] = coverage_offering.get_measurements()

        self.cleaned_data['resampling'] = INTERPOLATION_OPTIONS.get(self.cleaned_data['INTERPOLATION'], 'nearest')
