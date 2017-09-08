import unittest
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .test_wcs_spec import TestWCSSpecification


class TestGetCapabilities(TestWCSSpecification):
    """Responsible for testing the GetCapabilities functionality of the WCS server

    Reference:
        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#7-GetCapabilities%20Operation

    """

    def test_no_server_updatesequence(self):
        """
        The server does not advertise an UpdateSequence number.
        When a GetCapabilities request is made with an UPDATESEQUENCE parameter, the UPDATESEQUENCE parameter is ignored.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
            UPDATESEQUENCE = ignored
        Results:
            Valid XML where /WC_Capabilities exists

        """

        params_72 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities", "UPDATESEQUENCE": "0"}
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('ServiceException').attrs['code'] == "CurrentUpdateSequence",
            msg="The server should return a service exception with the specified code.")

    def test_current_updatesequence(self):
        """
        The server advertises an UpdateSequence number
        When a GetCapabilities request is made with an UPDATESEQUENCE parameter set to the current update sequence value,
        then the server returns a valid exception (cose = CurrentUpdateSequence).

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
            UPDATESEQUENCE = [[VAR_CURRENT_UPDATESEQUENCE]]
        Results:
         	Valid XML where /ServiceExceptionReport/ServiceException[@code="CurrentUpdateSequence"] exists

        """

        params_72 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities", "UPDATESEQUENCE": "0"}
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('ServiceException').attrs['code'] == "CurrentUpdateSequence",
            msg="The server should return a service exception with the specified code.")

    def test_lower_updatesequence(self):
        """
        The server advertises an UpdateSequence number
        When a GetCapabilities request is made with an UPDATESEQUENCE parameter set to a value lower than the current
        update sequence value, then the server returns capabilities XML.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
            UPDATESEQUENCE = [[VAR_LOW_UPDATESEQUENCE]]
        Results:
         	Valid XML where /WCS_Capabilities exists

        """

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "UPDATESEQUENCE": self.VAR_LOW_UPDATESEQUENCE
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities'), msg="Lower update sequences should be permitted.")

    def test_higher_updatesequence(self):
        """
        The server advertises an UpdateSequence number
        When a GetCapabilities request is made with an UPDATESEQUENCE parameter set to a value higher than the current
        update sequence value, then the server returns a service exception (code="InvalidUpdateSequence ")

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
            UPDATESEQUENCE = [[VAR_HIGH_UPDATESEQUENCE]]
        Results:
         	Valid XML where /ServiceExceptionReport/ServiceException[@code="InvalidUpdateSequence "] exists

        """

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "UPDATESEQUENCE": self.VAR_HIGH_UPDATESEQUENCE
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('ServiceException').attrs['code'] == "InvalidUpdateSequence",
            msg="The server should return a service exception with the specified code.")

    def test_no_request_updatesequence(self):
        """
        The server advertises an UpdateSequence number
        When a GetCapabilities request is made without an UPDATESEQUENCE parameter set, then the server returns most
        recent capabilities XML.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
        Results:
         	Valid XML where /WCS_Capabilities exists

        """

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities'), msg="The update sequence should not be a required parameter.")

    def test_no_section_parameter(self):
        """
        When a GetCapabilities request is made without a SECTION parameter, then the entire capabilities are returned.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
        Results:
            Valid XML where /WCS_Capabilities/Service, /WCS_Capabilities/Capability, and /WCS_Capabilities/ContentMetadata exist.

        """

        params_72 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities') and soup.find('Capability') and soup.find('ContentMetadata') and
            soup.find('Service'),
            msg="Requests without the section parameter should return all sections.")

    def test_slash_section_parameter(self):
        """
        When a GetCapabilities request is made with a SECTION parameter set to a value as "/", then the entire
        capabilities are returned.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
            SECTION = /
        Results:
            Valid XML where /WCS_Capabilities/Service, /WCS_Capabilities/Capability, and /WCS_Capabilities/ContentMetadata exist

        """

        params_72 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities", "SECTION": "/"}
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities') and soup.find('Capability') and soup.find('ContentMetadata') and
            soup.find('Service'),
            msg="Requests with a slash for the section should return all sections.")

    def test_section_service_parameter(self):
        """
        When a GetCapabilities request is made with a SECTION parameter set to a value as "/WCS_Capabilities/Service",
        Capabilities returned includes the only portion: Service.

        """

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "SECTION": "/WCS_Capabilities/Service"
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('Service') and not soup.find('Capability') and not soup.find('ContentMetadata'),
            msg="Requests with a section should return the requested section.")

    def test_section_capability_parameter(self):
        """
        When a GetCapabilities request is made with a SECTION parameter set to a value as "/WCS_Capabilities/Capability",
        Capabilities returned includes the only portion: Capability.

        """

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "SECTION": "/WCS_Capabilities/Capability"
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('Capability') and not soup.find('ContentMetadata') and not soup.find('Service'),
            msg="Requests with a section should return the requested section.")

    def test_section_content_metadata_parameter(self):
        """
        When a GetCapabilities request is made with a SECTION parameter set to a value as "/WCS_Capabilities/ContentMetadata",
        Capabilities returned includes the only portion: ContentMetadata.

        """

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "SECTION": "/WCS_Capabilities/ContentMetadata"
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            not soup.find('Capability') and soup.find('ContentMetadata') and not soup.find('Service'),
            msg="Requests with a section should return the requested section.")

    def test_get_capabilities_updatesequence(self):
        """The response to a GetCapabilities has an increased UpdateSequence value after the update service content.

        Untestable as per the documentation - pass
        """

        pass

    def test_get_capabilities_response(self):
        """
        Each OnlineResource URL intended for HTTP Get requests in the capabilities document is a URL prefix.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
        Results:
            XML where each /WCS_Capabilities/Capability/Request/OnlineResource@xlink:href ends in a ? or both contains a ? and ends in an &.

        """

        params_73 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_73)
        soup = BeautifulSoup(response.text, 'xml')
        for entry in soup.find_all('OnlineResource'):
            self.assertTrue(
                entry.attrs['xlink:href'].endswith("?") and urlparse(entry.attrs['xlink:href']),
                msg="All returned GetCapabilities urls should be valid urls ending with a ?.")
