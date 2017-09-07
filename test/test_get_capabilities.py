import unittest
import requests

from bs4 import BeautifulSoup

from .test_wcs_spec import TestWCSSpecification


class TestGetCapabilities(TestWCSSpecification):
    """"""

    def test_get_capabilities_request(self):
        """Test the GetCapabilities functionality of the WCS server - Section 7.2

        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#7-GetCapabilities%20Operation

        """

        # regarding 721 - our server has a static updatesequence set, so there is no way to test whether or not 721 will pass.

        params_72 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities", "UPDATESEQUENCE": "0"}
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException').attrs['code'] == "CurrentUpdateSequence")

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "UPDATESEQUENCE": self.VAR_LOW_UPDATESEQUENCE
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities'))

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "UPDATESEQUENCE": self.VAR_HIGH_UPDATESEQUENCE
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException').attrs['code'] == "InvalidUpdateSequence")

        # regarding 735 - this is already tested above in previous api calls where no update sequence is provided

        params_72 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities') and soup.find('Capability') and soup.find('ContentMetadata') and
            soup.find('Service'))

        params_72 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities", "SECTION": "/"}
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities') and soup.find('Capability') and soup.find('ContentMetadata') and
            soup.find('Service'))

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "SECTION": "/WCS_Capabilities/Service"
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities') and soup.find('Service'))

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "SECTION": "/WCS_Capabilities/Capability"
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities') and soup.find('Capability'))

        params_72 = {
            'VERSION': "1.0.0",
            'SERVICE': "WCS",
            'REQUEST': "GetCapabilities",
            "SECTION": "/WCS_Capabilities/ContentMetadata"
        }
        response = self.query_server(params_72)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities') and soup.find('ContentMetadata'))

    def test_get_capabilities_response(self):
        """Test the GetCapabilities response - Section 7.3

        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#7.3-GetCapabilities%20Response

        """

        # regarding 7.3.1 - not testable as per spec

        params_73 = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_73)
        soup = BeautifulSoup(response.text, 'xml')
        for entry in soup.find_all('OnlineResource'):
            self.assertTrue(entry.attrs['xlink:href'].endswith("?") and self.BASE_WCS_URL in entry.attrs['xlink:href'])
