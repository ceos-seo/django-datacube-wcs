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

    Other skipped tests:
        wcs/1.0.0/getcoverage_operations/getcoverage_request/parameter/get/kvp/2
            This test case directly conflicts with one of the general tests - any 'bogus' params are ignored, and should
            not raise a service exception

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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position

        response = self.query_server(params)
        self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
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
            "BBOX": self.subset_bbox
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
            "BBOX": self.subset_bbox,
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
            "CRS": self.request_crs,
            "RESPONSE_CRS": self.response_crs if self.response_crs else self.request_response_crs,
            "BBOX": self.subset_bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position

        response = self.query_server(params)
        self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

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
            "CRS": self.request_crs,
            "RESPONSE_CRS": "EPSG:5464321385",
            "BBOX": self.subset_bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_bbox_subset(self):
        """
        When a GetCoverage request is made with a BBOX partly contained in the defined Bounding BOX, the server should
        return the requested content.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position

        response = self.query_server(params)
        self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

    def test_invalid_bbox(self):
        """
        When a GetCoverage request is made with a BBOX outside the defined Bounding BOX, the server returns service exception

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
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX_OUTSIDE]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
            Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        subset_bbox = list(map(lambda x: float(x), self.bbox.split(",")))
        subset_bbox = [subset_bbox[2] + 1, subset_bbox[3] + 1, subset_bbox[2] + 10, subset_bbox[3] + 10]
        subset_bbox = "{},{},{},{}".format(subset_bbox[0], subset_bbox[1], subset_bbox[2], subset_bbox[3])

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": subset_bbox
        }
        if self.time_position:
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_missing_bbox_time(self):
        """
        When a GetCoverage request is made without a BBOX and without a TIME, the server returns service exception.

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
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
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
            "CRS": self.request_crs,
        }

        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_time_position(self):
        """
        The server advertises the timePosition.
        When a GetCoverage request is made with a VALID TIME, the server should return the requested content

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
            TIME = [[VAR_WCS_COVERAGE_1_TIME]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
            Content-type header = [[VAR_WCS_FORMAT_1_HEADER

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            params['TIME'] = self.time_position
            response = self.query_server(params)
            self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

    def test_invalid_time(self):
        """
        When a GetCoverage request is made with an invalid TIME, the server returns service exception.


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
            TIME = WCS_TIME_INVALID
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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = "asdfasdfasfasdf"
            response = self.query_server(params)
            soup = BeautifulSoup(response.text, 'xml')
            self.assertTrue(soup.find('ServiceException'))

    def test_invalid_parameter_value(self):
        """
        When a GetCoverage request is made with a PARAMETER name that is listed in the range set, but PARAMETER signed
        a value that is not defined in AxisDescription, the server returns service exception.

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
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
            [[VAR_WCS_PARAMETER]] = WCS_PARAMETER_VALUE_INVALID
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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position
        if self.parameter:
            params[self.parameter] = "asdfasdfasdf"
            response = self.query_server(params)
            soup = BeautifulSoup(response.text, 'xml')
            self.assertTrue(soup.find('ServiceException'))

    def test_correct_parameter(self):
        """
        When a GetCoverage request is made with a PARAMETER name that is listed in the range set, PARAMETER signed
        value that is defined in AxisDescription, the server should return the requested content.

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
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
            [[VAR_WCS_PARAMETER]] = [[VAR_WCS_PARAMETER_VALUE]]
        Results:
        	Content-type header = [[VAR_WCS_COVERAGE_FORMAT

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position
        if self.parameter:
            params[self.parameter] = self.parameter_value
            response = self.query_server(params)
            self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

    def test_missing_grid_size(self):
        """
        When a GetCoverage request is made without a specific grid size and without a grid resolution, the server returns service exception

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
            CRS = [[VAR_WCS_COVERAGE_1_CRS]]
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_grid_resolution(self):
        """
        When a GetCoverage request is made with a specific grid resolution, the server should return the requested content .

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
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            RESX = [[VAR_WCS_COVERAGE_1_RESX]]
            RESY = [[VAR_WCS_COVERAGE_1_RESY]]
            FORMAT = [[VAR_WCS_FORMAT_1]]
        Results:
        	Content-type header = [[VAR_WCS_FORMAT_1_HEADER]]

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "RESX": self.VAR_WCS_COVERAGE_1_RESX,
            "RESY": self.VAR_WCS_COVERAGE_1_RESY,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position

        response = self.query_server(params)
        self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

    def test_invalid_format(self):
        """
        When a GetCoverage request is made with a FORMAT not listed in a supportedFormats/formats under the selected
        coverage offering in the DescribeCoverage reply, the server returns service exception.

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
                BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
                WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
                HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
                FORMAT = WCS_FORMAT_INVALID
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
            "FORMAT": "asdfasdfasdf",
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_missing_format(self):
        """
        When a GetCoverage request is made without a FORMAT, the server returns service exception.

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
            BBOX = [[VAR_WCS_COVERAGE_1_BBOX]]
            WIDTH = [[VAR_WCS_COVERAGE_1_WIDTH]]
            HEIGHT = [[VAR_WCS_COVERAGE_1_HEIGHT]]
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
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    # section 9.2.2.13 Exception doesn't make much sense... skipping

    def test_valid_interpolation(self):
        """
        When a GetCoverage request is made with an INTERPLOATIONMETHOD value that is listed in the CoverageDescription,
        the server should return the requested content

        The request/response docs here are jumbled/not formatted properly on the site.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox,
            'INTERPOLATION': self.interpolations[0]
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position

        response = self.query_server(params)
        self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)

    def test_invalid_interpolation(self):
        """
        When a GetCoverage request is made with a FORMAT not listed in a supportedFormats/formats under the selected
        coverage offering in the DescribeCoverage reply, the server returns service exception.

        The request/response docs here are jumbled/not formatted properly on the site.

        """

        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.request_format,
            "CRS": self.request_crs,
            "BBOX": self.subset_bbox,
            'INTERPOLATION': "asdfasdfasdf"
        }
        # this test is only applicable if the server advertises a time position
        if self.time_position:
            # clearly not a valid time
            params['TIME'] = self.time_position

        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))
