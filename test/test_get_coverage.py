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

    def setUp(self):
        params = {
            'ReQuEsT': "GetCapabilities",
            'VeRsIoN': "1.0.0",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            "SECTION": "/WCS_Capabilities/ContentMetadata"
        }
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.name = soup.find('name').text

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

        params = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0", "COVERAGE": self.name}
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        position_container = soup.find('gml:Envelope').find_all('gml:pos') if soup.find('gml:Envelope') else soup.find(
            'gml:EnvelopeWithTimePeriod').find_all('gml:pos')
        # format of (x, y), (x, y)
        bbox = list(map(lambda b: b.text.split(" "), position_container))
        bbox = "{},{},{},{}".format(
            min([bbox[0][0], bbox[1][0]]),
            min([bbox[0][1], bbox[1][1]]), max([bbox[0][0], bbox[1][0]]), max([bbox[0][1], bbox[1][1]]))
        # uses the soup from a describe coverage call
        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.VAR_WCS_DEFAULT_FORMAT,
            "CRS": self.VAR_WCS_CRS,
            "BBOX": bbox
        }
        if soup.find('CoverageOffering').find('timePosition'):
            params['TIME'] = soup.find('CoverageOffering').find('timePosition').text
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

        params = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0", "COVERAGE": self.name}
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        position_container = soup.find('gml:Envelope').find_all('gml:pos') if soup.find('gml:Envelope') else soup.find(
            'gml:EnvelopeWithTimePeriod').find_all('gml:pos')
        # format of (x, y), (x, y)
        bbox = list(map(lambda b: b.text.split(" "), position_container))
        bbox = "{},{},{},{}".format(
            min([bbox[0][0], bbox[1][0]]),
            min([bbox[0][1], bbox[1][1]]), max([bbox[0][0], bbox[1][0]]), max([bbox[0][1], bbox[1][1]]))
        # uses the soup from a describe coverage call
        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "0.0.1",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.VAR_WCS_DEFAULT_FORMAT,
            "CRS": self.VAR_WCS_CRS,
            "BBOX": bbox
        }
        if soup.find('CoverageOffering').find('timePosition'):
            params['TIME'] = soup.find('CoverageOffering').find('timePosition').text
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

        params = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0", "COVERAGE": self.name}
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        position_container = soup.find('gml:Envelope').find_all('gml:pos') if soup.find('gml:Envelope') else soup.find(
            'gml:EnvelopeWithTimePeriod').find_all('gml:pos')
        # format of (x, y), (x, y)
        bbox = list(map(lambda b: b.text.split(" "), position_container))
        bbox = "{},{},{},{}".format(
            min([bbox[0][0], bbox[1][0]]),
            min([bbox[0][1], bbox[1][1]]), max([bbox[0][0], bbox[1][0]]), max([bbox[0][1], bbox[1][1]]))
        # uses the soup from a describe coverage call
        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "FORMAT": self.VAR_WCS_DEFAULT_FORMAT,
            "CRS": self.VAR_WCS_CRS,
            "BBOX": bbox
        }
        if soup.find('CoverageOffering').find('timePosition'):
            params['TIME'] = soup.find('CoverageOffering').find('timePosition').text
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))

    def test_valid_coverage(self):
        """
        When a GetCoverage request is made with coverage=name and name is a valid coverage identifier, the server should
        return a content (if other condition satisfied).
        """

        params = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0", "COVERAGE": self.name}
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        position_container = soup.find('gml:Envelope').find_all('gml:pos') if soup.find('gml:Envelope') else soup.find(
            'gml:EnvelopeWithTimePeriod').find_all('gml:pos')
        # format of (x, y), (x, y)
        bbox = list(map(lambda b: b.text.split(" "), position_container))
        bbox = "{},{},{},{}".format(
            min([bbox[0][0], bbox[1][0]]),
            min([bbox[0][1], bbox[1][1]]), max([bbox[0][0], bbox[1][0]]), max([bbox[0][1], bbox[1][1]]))
        # uses the soup from a describe coverage call
        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.VAR_WCS_DEFAULT_FORMAT,
            "CRS": self.VAR_WCS_CRS,
            "BBOX": bbox
        }
        if soup.find('CoverageOffering').find('timePosition'):
            params['TIME'] = soup.find('CoverageOffering').find('timePosition').text
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

        params = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0", "COVERAGE": self.name}
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        position_container = soup.find('gml:Envelope').find_all('gml:pos') if soup.find('gml:Envelope') else soup.find(
            'gml:EnvelopeWithTimePeriod').find_all('gml:pos')
        # format of (x, y), (x, y)
        bbox = list(map(lambda b: b.text.split(" "), position_container))
        bbox = "{},{},{},{}".format(
            min([bbox[0][0], bbox[1][0]]),
            min([bbox[0][1], bbox[1][1]]), max([bbox[0][0], bbox[1][0]]), max([bbox[0][1], bbox[1][1]]))
        # uses the soup from a describe coverage call
        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            'coverage': "asfasfasdfasf",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "FORMAT": self.VAR_WCS_DEFAULT_FORMAT,
            "CRS": self.VAR_WCS_CRS,
            "BBOX": bbox
        }
        if soup.find('CoverageOffering').find('timePosition'):
            params['TIME'] = soup.find('CoverageOffering').find('timePosition').text
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

        params = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0", "COVERAGE": self.name}
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')
        position_container = soup.find('gml:Envelope').find_all('gml:pos') if soup.find('gml:Envelope') else soup.find(
            'gml:EnvelopeWithTimePeriod').find_all('gml:pos')
        # format of (x, y), (x, y)
        bbox = list(map(lambda b: b.text.split(" "), position_container))
        bbox = "{},{},{},{}".format(
            min([bbox[0][0], bbox[1][0]]),
            min([bbox[0][1], bbox[1][1]]), max([bbox[0][0], bbox[1][0]]), max([bbox[0][1], bbox[1][1]]))
        # uses the soup from a describe coverage call
        params = {
            'ReQuEsT': "GetCoverage",
            'SeRvIcE': "WCS",
            'version': "1.0.0",
            "HEIGHT": self.VAR_WCS_COVERAGE_1_HEIGHT,
            "WIDTH": self.VAR_WCS_COVERAGE_1_WIDTH,
            "COVERAGE": self.name,
            "FORMAT": self.VAR_WCS_DEFAULT_FORMAT,
            "BBOX": bbox
        }
        if soup.find('CoverageOffering').find('timePosition'):
            params['TIME'] = soup.find('CoverageOffering').find('timePosition').text
        # TODO: uncomment
        # response = self.query_server(params)
        # self.assertTrue(response.headers['content-type'] == self.VAR_WCS_FORMAT_1_HEADER)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceException'))
