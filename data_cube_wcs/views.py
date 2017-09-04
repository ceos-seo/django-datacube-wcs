from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views import View

import pandas as pd

from . import forms
from . import models
from .utils import utils


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

        base_request_form = forms.BaseRequestForm(request.GET)
        if not base_request_form.is_valid():
            response = render_to_response('ServiceException.xml', {
                'exception_code': "InvalidParameterValue",
                'error_msg': "Invalid request or service parameter."
            })
            response['Content-Type'] = 'text/xml; charset=UTF-8;'
            return response

        service = base_request_form.cleaned_data.get('SERVICE', 'WCS')
        _request = base_request_form.cleaned_data.get('REQUEST', 'GetCapabilities')

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
            REQUEST: request type - fixed to "GetCapabilities"
            VERSION (optional): version number of the WCS server - fixed to 1.0.0
            SERVICE: service type - fixed to "WCS"
            SECTION (optional): section of WCS capabilities document to be returned. Values include:
                WCS_Capabilities/Service
                WCS_Capabilities/Capability
                WCS_Capabilities/ContentMetadata
            UPDATESEQUENCE (optional): capabilities version - integer, a timestamp in [ISO 8601:1988] format, or any other number or string

        Returns:
            Validated capabilities document
        """

        get_capabilities_form = forms.GetCapabilitiesForm(request.GET)
        if not get_capabilities_form.is_valid():
            response = render_to_response('ServiceException.xml', {
                'exception_code': "InvalidParameterValue",
                'error_msg': "Invalid section value."
            })
            response['Content-Type'] = 'text/xml; charset=UTF-8;'
            return response

        section_map = {
            "WCS_Capabilities/Service": "get_capabilities/service.xml",
            "WCS_Capabilities/Capability": "get_capabilities/capability.xml",
            "WCS_Capabilities/ContentMetadata": "get_capabilities/content_metadata.xml"
        }

        context = {
            'base_url': request.build_absolute_uri().split('?')[0],
            'coverage_offerings': models.CoverageOffering.objects.all(),
            'native_crs': forms.NATIVE_CRS,
            'available_input_crs': forms.AVAILABLE_INPUT_CRS,
            'available_output_crs': forms.AVAILABLE_OUTPUT_CRS
        }
        if 'SECTION' in get_capabilities_form.cleaned_data and get_capabilities_form.cleaned_data['SECTION']:
            context['section'] = section_map[get_capabilities_form.cleaned_data['SECTION']]

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
            REQUEST: request type - fixed to "DescribeCoverage"
            VERSION (optional): version number of the WCS server - fixed to 1.0.0
            SERVICE: service type - fixed to "WCS"
            COVERAGE (optional): comma seperated list of coverages to described - identified using the name values from
                the capabilities document.

        Returns:
            Validated coverage description document

        """
        coverages = models.CoverageOffering.objects.all()
        if 'COVERAGE' in request.GET:
            coverages = models.CoverageOffering.objects.filter(name__in=request.GET.get('COVERAGE').split(","))
            if not coverages:
                coverages = models.CoverageOffering.objects.all()

        response = render_to_response('DescribeCoverage.xml', context={'coverage_offerings': coverages})
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
            REQUEST: request type - fixed to "GetCoverage"
            VERSION (optional): version number of the WCS server - fixed to 1.0.0
            SERVICE: service type - fixed to "WCS"
            COVERAGE (optional): coverage to return - identified using the name value from the capabilities document.
            CRS: Coordinate Reference System in which the request is expressed.
            RESPONSE_CRS (optional): Coordinate Reference System in which to express coverage responses.Defaults to the request CRS.
            BBOX: Request a subset defined by the specified bounding box, with min/max coordinate pairs ordered according to the Co-ordinate
                Reference System identified by the CRS parameter. One of BBOX or TIME is required. Comma seperated string like
                minx, miny, maxx, maxy
            TIME: Request a subset corresponding to the specified time instants or intervals, expressed in an extended ISO 8601 syntax.
                Optional if a default time (or fixed time, or no time) is de-fined for the selected layer. Comma seperated string like:
                time1,time2,time3... or min/max

            WIDTH and HEIGHT: Request a grid of the specified width (w), height (h), and [for 3D grids] depth (d) (integer number of gridpoints).
                Either these or RESX, RESY, [for 3D grids] RESZ are required.

            RESX and RESY: Request a coverage subset with a specific spatial resolution along each axis of the reply CRS.
                The values are given in the units appropriate to each axis of the CRS. Either these or WIDTH, HEIGHT

            INTERPOLATION:Requested spatial interpolation method for resampling cov-erage values into the desired output grid.
                interpolation-method must be one of the values listed in the supportedInterpolations element of the requested
                CoverageOffering. Optional; server-defined default as stated in 8.3.6.
            FORMAT: Requested output format of Coverage. Must be one of those listed under the description of the selected coverage.

            EXCEPTIONS (optional): string fixed to application/vnd.ogc.se_xml

            PARAMETER (optional): any number of optional key/val pairs like band=1,2,3 or age-1,18. The parameter name should match
                the name of an AxisDescription element

        Returns:
            Subsetted dataset

        """

        coverage_data = forms.GetCoverageForm(request.GET)
        if not coverage_data.is_valid():
            for error in coverage_data.errors:
                response = render_to_response('ServiceException.xml', {
                    'exception_code': forms.field_exception_map[error],
                    'error_msg': "Invalid or missing {} value.".format(error)
                })
                response['Content-Type'] = 'text/xml; charset=UTF-8;'
                return response
        dc_parameters, individual_dates, date_ranges = utils.form_to_data_cube_parameters(coverage_data)
        print(dc_parameters)
        dataset = utils.get_stacked_dataset(dc_parameters, individual_dates, date_ranges)
        print(dataset)
        return HttpResponse("OK")
