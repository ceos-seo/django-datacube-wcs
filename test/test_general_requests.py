import unittest
import requests

from bs4 import BeautifulSoup

from .test_wcs_spec import TestWCSSpecification


class TestGeneralRequests(TestWCSSpecification):
    """"""

    def test_versioning(self):
        """Test the version numbering, exceptions, and basic http requests - Section 6-2

        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#6.2-Version%20Numbering%20and%20Negotiation

        """

        params_62 = {'VERSION': "", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_62)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        response = self.query_server()
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        params_62['VERSION'] = "1.0.2"
        response = self.query_server(params_62)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        params_62['VERSION'] = "0.8.0"
        response = self.query_server(params_62)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

    def test_request_rules(self):
        """Test the standard request and parameter formatting rules of the WCS server - Section 6.3

        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#6.3-General%20HTTP%20Request%20Rules

        """

        # tests 631 and 633
        params_63 = {'ReQuEsT': "GetCapabilities", 'VeRsIoN': "1.0.0", 'SeRvIcE': "WCS"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        params_63 = {'VeRsIoN': "1.0.0", 'SeRvIcE': "wcs", 'ReQuEsT': "getcapabilities"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))

        params_63 = {'ReQuEsT': "GetCapabilities", 'VeRsIoN': "1.0.0", 'SeRvIcE': "WCS", "BOGUS": "SSS"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        params_63 = {'ReQuEsT': "DescribeCoverage", 'VeRsIoN': "1.0.0", 'SeRvIcE': "WCS", "BOGUS": "SSS"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('CoverageDescription').attrs['version'] == "1.0.0")

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

    def test_service_exception(self):
        """Test the standard service exception of the WCS server - Section 6.5

        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#6.5-Service%20Exceptions

        """

        params_65 = {'VeRsIoN': "1.0.0", 'SeRvIcE': "wcs", 'ReQuEsT': "getcapabilities"}
        response = self.query_server(params_65)
        self.assertTrue(response.headers['content-type'] == "application/vnd.ogc.se_xml")
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))
