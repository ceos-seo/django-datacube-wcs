from django import forms

from dateutil import parser

from . import models
from . import utils

exception_codes = [
    'InvalidFormat', 'CoverageNotDefined', 'CurrentUpdateSequence', 'InvalidUpdateSequence', 'MissingParameterValue',
    'InvalidParameterValue'
]

AVAILABLE_INPUT_CRS = ["EPSG:4326"]
AVAILABLE_OUTPUT_CRS = ["EPSG:4326"]
NATIVE_CRS = ["EPSG:4326"]
ORDERED_FORMATS = ('GeoTIFF')
AVAILABLE_FORMATS = {'GeoTIFF': 'image/tiff', 'netCDF': 'application/x-netcdf'}
INTERPOLATION_OPTIONS = {'nearest neighbor': 'nearest', 'bilinear': 'bilinear', 'bicubic': 'cubic'}


class BaseRequestForm(forms.Form):
    """Base WCS request parameters as defined by the OGC WCS 1.0 specification"""

    request = forms.ChoiceField(
        choices=(("GetCapabilities", "GetCapabilities"), ("DescribeCoverage", "DescribeCoverage"),
                 ("GetCoverage", "GetCoverage")),
        initial="GetCapabilities")
    version = forms.CharField(required=False, initial="1.0.0")
    service = forms.ChoiceField(choices=(("WCS", "WCS"), ("WMS", "WMS")), initial="WCS")


class GetCapabilitiesForm(BaseRequestForm):
    """GetCapabilities request form as defined by the OGC WCS 1.0 specification"""

    section = forms.ChoiceField(
        required=False,
        choices=(("/", "/"), ("/WCS_Capabilities/Service", "/WCS_Capabilities/Service"),
                 ("/WCS_Capabilities/Capability", "/WCS_Capabilities/Capability"),
                 ("/WCS_Capabilities/ContentMetadata", "/WCS_Capabilities/ContentMetadata")),
        error_messages={'invalid_choice': 'InvalidParameterValue'})
    updatesequence = forms.CharField(required=False)

    def clean(self):
        """Basic validation for the capabilities request"""
        cleaned_data = super(GetCapabilitiesForm, self).clean()

        if 'updatesequence' in cleaned_data:
            if cleaned_data['updatesequence'] == "0":
                self.add_error("updatesequence", "CurrentUpdateSequence")
                return
            if cleaned_data['updatesequence'] > "0":
                self.add_error("updatesequence", "InvalidUpdateSequence")
                return


class GetCoverageForm(BaseRequestForm):
    """GetCoverage request form as defined by the OGC WCS 1.0 specification"""
    coverage = forms.ModelChoiceField(queryset=models.CoverageOffering.objects.all(), to_field_name="name")

    crs = forms.ChoiceField(choices=((option, option) for option in AVAILABLE_INPUT_CRS), initial="EPSG:4326")
    response_crs = forms.ChoiceField(
        required=False, choices=((option, option) for option in AVAILABLE_OUTPUT_CRS), initial="EPSG:4326")

    # One of the following is required.
    bbox = forms.CharField(required=False)
    time = forms.CharField(required=False)

    # either width/height or resx/resy are required as a pair
    width = forms.IntegerField(required=False)
    height = forms.IntegerField(required=False)
    resx = forms.FloatField(required=False)
    resy = forms.FloatField(required=False)

    interpolation = forms.ChoiceField(
        required=False,
        choices=((option, option) for option in INTERPOLATION_OPTIONS),
        initial="nearest neighbor",
        error_messages={"invalid_choice": "InvalidParameterValue"})
    format = forms.ChoiceField(
        choices=((option, option) for option in AVAILABLE_FORMATS),
        initial="GeoTIFF",
        error_messages={"required": "InvalidFormat",
                        "invalid_choice": "InvalidFormat"})
    exceptions = forms.CharField(required=False, initial="application/vnd.ogc.se_xml")

    #measurements are the only parameters available as an AxisDescription/rangeset
    measurements = forms.CharField(required=False)

    def clean_response_crs(self):
        """Meant to provide actual default values for various form fields if missing from GET"""
        if not self['response_crs'].html_name in self.data:
            return self.fields['response_crs'].initial
        return self.cleaned_data['response_crs']

    def clean_interpolation(self):
        """Meant to provide actual default values for various form fields if missing from GET"""
        if not self['interpolation'].html_name in self.data:
            return self.fields['interpolation'].initial
        return self.cleaned_data['interpolation']

    def clean(self):
        """Basic validation of the GetCoverage parameters according to the OGC WCS 1.0 specification.

        Pretty monolithic implementation of cleaning - done for a few reasons:
            We don't want to continue validation if we encounter an error, hence the Returns
            Handles the semi-optional parameter sets like the time -or- bbox inputs, resxy or height/width
            Ensures that the ranges entered actually exist in the coverage

        """
        cleaned_data = super(GetCoverageForm, self).clean()

        if 'coverage' not in cleaned_data:
            self.add_error("coverage", "MissingParameterValue")
            return

        if not (cleaned_data['bbox'] or cleaned_data['time']):
            self.add_error("bbox", "MissingParameterValue")
            self.add_error("time", "MissingParameterValue")
            return

        coverage_offering = self.cleaned_data['coverage']

        if cleaned_data.get('bbox', None):
            split_bbox = self.cleaned_data['bbox'].split(",")

            if len(split_bbox) not in [4, 6]:
                self.add_error('bbox', "InvalidParameterValue")
                return

            try:
                latitude_range = (float(split_bbox[1]), float(split_bbox[3]))
                longitude_range = (float(split_bbox[0]), float(split_bbox[2]))
            except:
                self.add_error('bbox', "InvalidParameterValue")

            validation_cases = [
                not utils._ranges_intersect(latitude_range,
                                            (coverage_offering.min_latitude, coverage_offering.max_latitude)),
                not utils._ranges_intersect(longitude_range,
                                            (coverage_offering.min_longitude, coverage_offering.max_longitude)),
                latitude_range != tuple(sorted(latitude_range)), longitude_range != tuple(sorted(longitude_range))
            ]

            # if the ranges are not well formed...
            if True in validation_cases:
                self.add_error('bbox', "InvalidParameterValue")
                return

            self.cleaned_data['latitude'] = latitude_range
            self.cleaned_data['longitude'] = longitude_range
        else:
            self.cleaned_data['latitude'] = (coverage_offering.min_latitude, coverage_offering.max_latitude)
            self.cleaned_data['longitude'] = (coverage_offering.min_longitude, coverage_offering.max_longitude)

        if cleaned_data.get('time', None):
            time_ranges = []
            times = []
            # time ranges currently not supported really as they don't apply to our usage of the DC
            _time_type_range = '/' in self.cleaned_data['time']
            if _time_type_range:
                time_range = self.cleaned_data['time'].split(",")
                time_ranges = map(lambda r: r.split("/"), time_range)
                try:
                    time_ranges = list(map(lambda r: (parser.parse(r[0]), parser.parse(r[1])), time_ranges))
                except ValueError:
                    self.add_error("time", "InvalidParameterValue")
                    return
            else:
                date_list = self.cleaned_data['time'].split(",")
                try:
                    times = list(map(lambda t: parser.parse(t), date_list))
                except ValueError:
                    self.add_error("time", "InvalidParameterValue")
                    return
                valid_times = coverage_offering.get_temporal_domain()
                if len(list(set(valid_times) & set(date_list))) != len(date_list):
                    self.add_error("time", "InvalidParameterValue")

            self.cleaned_data['time_ranges'] = time_ranges
            self.cleaned_data['times'] = times
        else:
            self.cleaned_data['time_ranges'] = [(coverage_offering.start_time, coverage_offering.end_time)]
            self.cleaned_data['times'] = []

        if (cleaned_data.get('resx', None) and cleaned_data.get('resy', None)):
            if cleaned_data['resx'] < 0 or cleaned_data['resy'] > 0:
                self.add_error('resx', "InvalidParameterValue")
                self.add_error('resy', "InvalidParameterValue")
                return
        elif (cleaned_data.get('width', None) and cleaned_data.get('height', None)):
            if cleaned_data['height'] < 0 or cleaned_data['width'] < 0:
                self.add_error('height', "InvalidParameterValue")
                self.add_error('width', "InvalidParameterValue")
                return
            self.cleaned_data['resx'] = (
                self.cleaned_data['longitude'][1] - self.cleaned_data['longitude'][0]) / cleaned_data['width']
            self.cleaned_data['resy'] = -1 * (
                self.cleaned_data['latitude'][1] - self.cleaned_data['latitude'][0]) / cleaned_data['height']
        else:
            self.add_error('resx', "MissingParameterValue")
            self.add_error('resy', "MissingParameterValue")
            self.add_error('height', "MissingParameterValue")
            self.add_error('width', "MissingParameterValue")
            return

        if cleaned_data.get('measurements', None):
            valid_measurements = coverage_offering.get_measurements()
            request_measurements = cleaned_data['measurements'].split(",")
            # if the measurements aren't all valid, raise
            if len(list(set(valid_measurements) & set(request_measurements))) != len(request_measurements):
                self.add_error("measurements", "InvalidParameterValue")
            else:
                self.cleaned_data['measurements'] = request_measurements
        else:
            self.cleaned_data['measurements'] = coverage_offering.get_measurements()

        if 'interpolation' in self.cleaned_data:
            self.cleaned_data['resampling'] = INTERPOLATION_OPTIONS.get(self.cleaned_data['interpolation'], 'nearest')
