from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views import View

from . import forms
from . import models
from . import utils


class WebService(View):
    """Entry point for the suite of webservice OGC implementations"""

    def get(self, request):
        """Handles the mapping of requests to the various service views based on GET parameters"""

        view_mapping = {
            'WCS': {
                'GetCapabilities': GetCapabilities,
                'DescribeCoverage': DescribeCoverage,
                'GetCoverage': GetCoverage
            }
        }
        get_data = {key.lower(): val for key, val in request.GET.items()}
        base_request_form = forms.BaseRequestForm(get_data)
        if not base_request_form.is_valid():
            response = render_to_response('ServiceException.xml', {
                'exception_code': "InvalidParameterValue",
                'error_msg': "Invalid request or service parameter."
            })
            response['Content-Type'] = 'application/vnd.ogc.se_xml'
            return response

        service = base_request_form.cleaned_data.get('service', 'WCS')
        _request = base_request_form.cleaned_data.get('request', 'GetCapabilities')

        return view_mapping[service][_request].as_view()(request)


class GetCapabilities(View):
    """Implements the GetCapabilities functionality as defined by the OGC WCS 1.0 specification

    Each Web Coverage Server must describe its capabilities. This implementation uses the KVP (key-value pair)
    url encoding for simplicity. A finite number of url encoded parameters are used to produce a capabilities
    document.

    """

    def get(self, request):
        """Handles the GET parameters for the GetCapabilities call, returning a formatted capabilities document

        GET data:
            request: request type - fixed to "GetCapabilities"
            version (optional): version number of the WCS server - fixed to 1.0.0
            service: service type - fixed to "WCS"
            section (optional): section of WCS capabilities document to be returned. Values include:
                WCS_Capabilities/Service
                WCS_Capabilities/Capability
                WCS_Capabilities/ContentMetadata
            updatesequence (optional): capabilities version - integer, a timestamp in [ISO 8601:1988] format, or any other number or string

        Returns:
            Validated capabilities document
        """

        get_data = {key.lower(): val for key, val in request.GET.items()}
        get_capabilities_form = forms.GetCapabilitiesForm(get_data)
        if not get_capabilities_form.is_valid():
            response = render_to_response('ServiceException.xml', {
                'exception_code': get_capabilities_form.errors[error][0],
                'error_msg': "Invalid section value."
            })
            response['Content-Type'] = 'application/vnd.ogc.se_xml'
            return response

        section_map = {
            "WCS_Capabilities/Service": "get_capabilities/service.xml",
            "WCS_Capabilities/Capability": "get_capabilities/capability.xml",
            "WCS_Capabilities/ContentMetadata": "get_capabilities/content_metadata.xml"
        }

        context = {
            'base_url': request.build_absolute_uri().split('?')[0],
            'coverage_offerings': models.CoverageOffering.objects.all()
        }
        if 'section' in get_capabilities_form.cleaned_data and get_capabilities_form.cleaned_data['section']:
            context['section'] = section_map[get_capabilities_form.cleaned_data[
                'section']] if get_capabilities_form.cleaned_data['section'] != "/" else None

        response = render_to_response('GetCapabilities.xml', context)
        response['Content-Type'] = 'text/xml; charset=UTF-8;'
        return response


class DescribeCoverage(View):
    """Implements the DescribeCoverage funcitonality as defined by the OGC WCS 1.0 specification

    Once a client has obtained summary descriptions of the coverages available from a par-ticular WCS server,
    it may be able to make simple GetCoverage requests immediately. But in most cases the client will need
    to issue a DescribeCoverage request to obtain a full description of one or more coverages available. The
    server responds to such a request with an XML document describing one or more coverages served by the WCS.

    A finite number of url encoded parameters are used to produce a coverage description.

    """

    def get(self, request):
        """Handles the GET parameters for the DescribeCoverage call, returning a formatted coverage description document

        GET data:
            request: request type - fixed to "DescribeCoverage"
            version (optional): version number of the WCS server - fixed to 1.0.0
            service: service type - fixed to "WCS"
            coverage (optional): comma seperated list of coverages to described - identified using the name values from
                the capabilities document.

        Returns:
            Validated coverage description document

        """

        coverages = models.CoverageOffering.objects.all()
        get_data = {key.lower(): val for key, val in request.GET.items()}
        if 'coverage' in get_data:
            coverages = models.CoverageOffering.objects.filter(name__in=get_data.get('coverage').split(","))
            if len(coverages) != len(get_data.get('coverage').split(",")):
                response = render_to_response('ServiceException.xml', {
                    'exception_code': "CoverageNotDefined",
                    'error_msg': "Invalid coverage value."
                })
                response['Content-Type'] = 'application/vnd.ogc.se_xml'
                return response

        response = render_to_response(
            'DescribeCoverage.xml',
            context={
                'coverage_offerings': coverages,
                'native_crs': forms.NATIVE_CRS,
                'available_input_crs': forms.AVAILABLE_INPUT_CRS,
                'available_output_crs': forms.AVAILABLE_OUTPUT_CRS,
                'interpolation_methods': forms.INTERPOLATION_OPTIONS,
                'valid_formats': forms.AVAILABLE_FORMATS
            })
        response['Content-Type'] = 'text/xml; charset=UTF-8;'
        return response


class GetCoverage(View):
    """Implements the GetCoverage functionality as defined by the OGC WCS 1.0 specification

    The GetCoverage operation allows retrieval of coverages from a coverage offering. A WCS server processes a
    GetCoverage request and returns a response to the client.

    A finite number of url encoded parameters are used to produce subset of the server dataset

    """

    def get(self, request):
        """Handles the GET parameters for the GetCoverage call, returning a dataset

        GET data:
            request: request type - fixed to "GetCoverage"
            version (optional): version number of the WCS server - fixed to 1.0.0
            service: service type - fixed to "WCS"
            coverage (optional): coverage to return - identified using the name value from the capabilities document.
            crs: Coordinate Reference System in which the request is expressed.
            response_crs (optional): Coordinate Reference System in which to express coverage responses.Defaults to the request crs.
            bbox: Request a subset defined by the specified bounding box, with min/max coordinate pairs ordered according to the Co-ordinate
                Reference System identified by the crs parameter. One of bbox or time is required. Comma seperated string like
                minx, miny, maxx, maxy
            time: Request a subset corresponding to the specified time instants or intervals, expressed in an extended ISO 8601 syntax.
                Optional if a default time (or fixed time, or no time) is de-fined for the selected layer. Comma seperated string like:
                time1,time2,time3... or min/max

            width and height: Request a grid of the specified width (w), height (h), and [for 3D grids] depth (d) (integer number of gridpoints).
                Either these or resx, resy, [for 3D grids] RESZ are required.

            resx and resy: Request a coverage subset with a specific spatial resolution along each axis of the reply crs.
                The values are given in the units appropriate to each axis of the crs. Either these or width, height

            interpolation:Requested spatial interpolation method for resampling cov-erage values into the desired output grid.
                interpolation-method must be one of the values listed in the supportedInterpolations element of the requested
                CoverageOffering. Optional; server-defined default as stated in 8.3.6.
            format: Requested output format of Coverage. Must be one of those listed under the description of the selected coverage.

            exceptions (optional): string fixed to application/vnd.ogc.se_xml

            PARAMETER (optional): any number of optional key/val pairs like band=1,2,3 or age-1,18. The parameter name should match
                the name of an AxisDescription element

        Returns:
            Subsetted dataset

        """

        get_data = {key.lower(): val for key, val in request.GET.items()}
        coverage_data = forms.GetCoverageForm(get_data)
        if not coverage_data.is_valid():
            for error in coverage_data.errors:
                response = render_to_response('ServiceException.xml', {
                    'exception_code': coverage_data.errors[error][0],
                    'error_msg': "Invalid or missing {} value.".format(error)
                })
                response['Content-Type'] = 'application/vnd.ogc.se_xml'
                return response
        dc_parameters, individual_dates, date_ranges = utils.form_to_data_cube_parameters(coverage_data)

        dataset = utils.get_stacked_dataset(dc_parameters, individual_dates, date_ranges)

        response_mapping = {'GeoTIFF': utils.get_tiff_response, 'netCDF': utils.get_netcdf_response}
        return HttpResponse(
            response_mapping[coverage_data.cleaned_data['format']](coverage_data.cleaned_data['coverage'], dataset,
                                                                   coverage_data.cleaned_data['response_crs']),
            content_type=forms.AVAILABLE_FORMATS[coverage_data.cleaned_data['format']])
