import unittest
import requests

from bs4 import BeautifulSoup

from .test_wcs_spec import TestWCSSpecification


class TestGeneralRequests(TestWCSSpecification):
    """Responsible for testing the general service elements and exceptions

    Includes topics such as version negotiation, exception types, and parameter formatting.

    Reference:
        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#6-Basic%20Service%20Elements

    """

    def test_without_version(self):
        """
        When a GetCapabilities request is made without a version number, then the response is the highest version
        supported. For wcs1.0.0, it is 1.0.0.

        Request:
            VERSION =
            SERVICE = WCS
            REQUEST = GetCapabilities
        Results:
            Valid XML where /WCS_Capabilities@version = 1.0.0

        """

        params_62 = {'VERSION': "", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_62)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities').attrs['version'] == "1.0.0",
            msg="When version is ommitted for a GetCapabilities request the version returned should be 1.0.0.")

    def test_supported_version(self):
        """
        When a GetCapabilities request is made for a supported version, then the response is the requested version.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
        Results:
            Valid XML where /WCS_Capabilities@version = [[VAR_WCS_VERSION]]

        """

        response = self.query_server()
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities').attrs['version'] == "1.0.0",
            msg="When a GetCapabilities request is made for version 1.0.0 the response should be version 1.0.0.")

    def test_unknown_version(self):
        """
        When a GetCapabilities request is made for a version that is unknown to the server is requested, the server
        sends the highest version it knows that is less than the requested version.

        Request:
            VERSION = 1.0.2
            SERVICE = WCS
            REQUEST = GetCapabilities
        Results:
            Valid XML where /WCS_Capabilities@version = 1.0.0

        """

        params_62 = {'VERSION': "1.0.2", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_62)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities').attrs['version'] == "1.0.0",
            msg="When a higher version is requested in a GetCapabilities call, the response should be version 1.0.0.")

    def test_low_version(self):
        """
        When a GetCapabilities request is made for a version lower than any of those known to the server, the server
        sends the lowest version it knows.

        Request:
            VERSION = 0.8.0
            SERVICE = WCS
            REQUEST = GetCapabilities
        Results:
            Valid XML where / WCS_Capabilities@version = 1.0.0

        """

        params_62 = {'VERSION': "0.8.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}
        response = self.query_server(params_62)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities').attrs['version'] == "1.0.0",
            msg="When a lower version is requested in a GetCapabilities call, the response should be version 1.0.0.")

    def test_parameters_case_sensitivity(self):
        """
        Parameter names are not case sensitive.

        Request:
            ReQuEsT: GetCapabilities
            VeRsIoN: 1.0.0
            SeRvIcE: WCS
        Results:
            Valid XML where / WCS_Capabilities@version = 1.0.0

        """

        params_63 = {'ReQuEsT': "GetCapabilities", 'VeRsIoN': "1.0.0", 'SeRvIcE': "WCS"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities').attrs['version'] == "1.0.0",
            msg="Parameter names should be case insensitive for all requests.")

    def test_parameter_values_case_sensititivity(self):
        """
        Parameter values are case sensitive.

        Request:
            ReQuEsT: getcapabilities
            VeRsIoN: 1.0.0
            SeRvIcE: WCS
        Results:
            Valid XML where content type header is application/vnd.ogc.se_xml and the ServiceExceptionReport tag is
            present.

        """

        params_63 = {'VeRsIoN': "1.0.0", 'SeRvIcE': "wcs", 'ReQuEsT': "getcapabilities"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('ServiceExceptionReport'), msg="Parameter values should be case sensitive for all inputs.")

    def test_unordered_parameters(self):
        """
        Parameters in a request may be specified in any order.

        Request:
            SeRvIcE = WCS
            VeRsIoN = 1.0.0
            ReQuEsT = GetCapabilities
        Results:
            Valid XML where / WCS_Capabilities@version = 1.0.0

        """

        params_63 = {'SeRvIcE': "WCS", 'VeRsIoN': "1.0.0", 'ReQuEsT': "GetCapabilities"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities').attrs['version'] == "1.0.0",
            msg="Parameters can be submitted in any order and the response should be valid.")

    def test_get_capabilities_unsupported_parameters(self):
        """
        When a GetCapabilities request contains a parameter which is not defined by the spec, the result is valid.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCapabilities
            BOGUS = ignored
        Results:
            Valid XML where /WCS_Capabilities exists.

        """

        params_63 = {'ReQuEsT': "GetCapabilities", 'VeRsIoN': "1.0.0", 'SeRvIcE': "WCS", "BOGUS": "SSS"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('WCS_Capabilities').attrs['version'] == "1.0.0",
            msg="Any unsupported parameters should be ignored.")

    def test_describe_coverage_unsupported_parameters(self):
        """
        When a DescribeCoverage request contains a parameter which is not defined by the spec, the result is valid.

        Request:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            BOGUS = ignored
        Results:
            Valid XML where /CoverageDescription exists.

        """

        params_63 = {'ReQuEsT': "DescribeCoverage", 'VeRsIoN': "1.0.0", 'SeRvIcE': "WCS", "BOGUS": "SSS"}
        response = self.query_server(params_63)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('CoverageDescription').attrs['version'] == "1.0.0",
            msg="Any unsupported parameters should be ignored.")

    def test_get_coverage_unsupported_parameters(self):
        """
        When a GetCoverage request contains a parameter which is not defined by the spec, the result is valid.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = GetCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
            BOGUS = ignored
        Results:
            Content-type header = [[VAR_WCS_FORMAT_1_HEADER]]

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
            "TIME": self.time_position,
            "FORMAT": self.request_format,
            "CRS": self.request_crs
        }

        response = self.query_server(params_63)
        self.assertTrue(
            response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER,
            msg="Any unsupported parameters should be ignored.")

    def test_service_exception(self):
        """
        When an Exception is returned from a request, Service Exception must have the MIME type as
        "application/vnd.ogc.se_xml"

        Request:
            SERVICE = WCS
            REQUEST = DescribeCoverage
        Results:
            Valid XML where content type header is application/vnd.ogc.se_xml.

        """

        params_65 = {'SeRvIcE': "wcs", 'ReQuEsT': "DescribeCoverage"}
        response = self.query_server(params_65)
        self.assertTrue(response.headers['content-type'] == "application/vnd.ogc.se_xml")
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(
            soup.find('ServiceExceptionReport'),
            msg="The service exception should be static as per the WCS 1.0 specification.")
