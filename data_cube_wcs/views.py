from django.shortcuts import render
from django.http import HttpResponse
from django.views import View


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


class GetCoverage(View):
    """Implements the GetCoverage functionality as defined by the OGC WCS 1.0 specification

    """

    def get(self, request):
        """

        """
