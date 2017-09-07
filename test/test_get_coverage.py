import unittest
import requests

from bs4 import BeautifulSoup

from .test_wcs_spec import TestWCSSpecification


class TestGetCoverage(TestWCSSpecification):
    """Responsible for testing the GetCoverage functionality of the WCS server

    Reference:
        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#9-GetCoverage%20Operation

    """

    def setUp(self):
        params_82 = {
            'ReQuEsT': "GetCapabilities",
            'VeRsIoN': "1.0.0",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            "SECTION": "/WCS_Capabilities/ContentMetadata"
        }
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.names = list(map(lambda n: n.text, soup.find_all('name')[0:2]))

    def test_missing_version(self):
        """
        When a GetCoverage request is made without version, the server returns service exception.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            SERVICE = WCS
            REQUEST = GetCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Valid XML where /ServiceExceptionReport/ServiceException exists.
        """

        params_63 = {'ReQuEsT': "DescribeCoverage", 'VeRsIoN': "1.0.0", 'SeRvIcE': "WCS", "BOGUS": "SSS"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')

        # uses the soup from a describe coverage call
        params_63 = {
            'ReQuEsT': "GetCoverage",
            'VeRsIoN': "1.0.0",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            "HEIGHT": 10,
            "WIDTH": 10,
            "COVERAGE": soup.find('CoverageOffering').find('name').text,
            "TIME": soup.find('CoverageOffering').find('timePosition').text,
            "FORMAT": self.VAR_WCS_DEFAULT_FORMAT,
            "CRS": "EPSG:4326"
        }
        # TODO: Uncomment this later
        # response = self.query_server(params_63)
        # self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)
