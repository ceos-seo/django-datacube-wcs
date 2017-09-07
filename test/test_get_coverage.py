import unittest
import requests

from bs4 import BeautifulSoup

from .test_wcs_spec import TestWCSSpecification


class TestGetCoverage(TestWCSSpecification):
    """Responsible for testing the GetCoverage functionality of the WCS server

    Reference:
        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#9-GetCoverage%20Operation

    Some of these test cases have 100% overlap and are omitted - Things like valid version/valid crs/valid {other field}
    all just expect all valid params and a valid response, so this is left out.

    """

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

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_response_crs if self.request_response_crs else self.request_crs,
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_invalid_version(self):
        """
        When a GetCoverage request is made with an invalid version, the server returns service exception.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            VERSION = 0.0.1
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

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "0.0.1",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_response_crs if self.request_response_crs else self.request_crs,
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_missing_coverage(self):
        """
        When a GetCoverage request is made without coverage, the server returns service exception.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCoverage
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "FORMAT": self.request_format,
            "CRS": self.request_response_crs if self.request_response_crs else self.request_crs,
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_valid_coverage(self):
        """
        When a GetCoverage request is made with coverage=name and name is a valid coverage identifier, the server should
        return a content (if other condition satisfied).
        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_response_crs if self.request_response_crs else self.request_crs,
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        # TODO: uncomment
        # response = self.query_server(params)
        # self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

    def test_invalid_coverage(self):
        """
        When a GetCoverage request is made with coverage=name and name is not a valid coverage identifier, the server
        returns service exception.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCoverage
            COVERAGE = WCS_COVERAGE_NOT_DEFINED
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            'coverage': "asfasfasdfasf",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "FORMAT": self.request_format,
            "CRS": self.request_response_crs if self.request_response_crs else self.request_crs,
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_missing_crs(self):
        """
        When a GetCoverage request is made without CRS, the server returns service exception.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_unsupported_crs(self):
        """
        When a GetCoverage request is made with a CRS and CRS value is not one of the requestResponseCRSs or requestCRSs
        element under the requested coverage, the server returns service exception.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = GetCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            CRS = WCS_CRS_NOT_IN_REQUEST_OR_REQUESTRESPONSE_CRS
            BBOX = [[VAR_WCS_BBOX_1]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
            Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "BBOX": self.bbox,
            #obviously invalid
            "CRS": "EPSG:456413215"
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_valid_response_crs(self):
        """
        When a GetCoverage request is made with a valid RESPONSE_CRS, the server should return the requested content with this CRS.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            VERSION = 1.0.0
            SERVICE = WCS
            REQUEST = GetCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            RESPONSE_CRS = [[VAR_WCS_COVERAGE_1_RESPONSE_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Content-type header = [[VAR_WCS_FORMAT_1_HEADER]]

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_response_crs if self.request_response_crs else self.request_crs,
            "RESPONSE_CRS": self.response_crs if self.response_crs else self.request_response_crs,
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        # TODO: uncomment
        # response = self.query_server(params)
        # self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

    def test_invalid_response_crs(self):
        """
        When a GetCoverage request is made with an invalid RESPONSE_CRS, the server returns service exception.

        Request#1:
            SERVICE = WCS
            VERSION = [[VAR_WCS_VERSION]]
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Request#2:
            VERSION = 1.0.0
            SERVICE = WCS
            REQUEST = GetCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            RESPONSE_CRS = WCS_COVERAGE_RESPONSE_CRS_INVALID
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Valid XML where /ServiceExceptionReport/ServiceException exists. 

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_response_crs if self.request_response_crs else self.request_crs,
            "RESPONSE_CRS": "EPSG:5464321385",
            "BBOX": self.bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))
