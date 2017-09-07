import unittest
import requests

from bs4 import BeautifulSoup

from .test_wcs_spec import TestWCSSpecification


class TestDescribeCoverage(TestWCSSpecification):
    """Responsible for testing the DescribeCoverage functionality of the WCS server

    Reference:
        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#8-DescribeCoverage%20Operation

    """

    def test_missing_version(self):
        """
        When a DescribeCoverage request is made without version, the server returns service exception.

        Request:
            SERVICE = WCS
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Results:
            Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params_82 = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", "BOGUS": "SSS"}
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))

    def test_invalid_version(self):
        """
        When a DescribeCoverage request is made with an invalid version, the server should return a service exception.

        Request:
            VERSION = 0.0.0
            SERVICE = WCS
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Results:
            Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params_82 = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", "BOGUS": "SSS", 'Version': "0.0.0.0"}
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))

    def test_missing_coverage(self):
        """
        If the Coverage element in the DescribeCoverage request is absent The server returns full descriptions of every
        coverage offering available.

        """
        # regarding 823 and 824 - these seem to say the same case, but different results. I'm going with the return all case.
        params_82 = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0"}
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(len(soup.find_all('CoverageOffering')) > 1)

    def test_multiple_coverages(self):
        """
        When a DescribeCoverage request is made with COVERAGE = name1, name2 (name1, name2 are in the Capabilities XML),
        the server returns CoverageDescription including the wanted coverage description.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            COVERAGE = [[VAR_WCS_COVERAGE_2]]
        Results:
            Valid XML where /*[local-name() = "CoverageDescription"]/*[local-name() = "CoverageOffering"]/*[local-name() = "name"] is the requested.

        """

        params_82 = {
            'ReQuEsT': "GetCapabilities",
            'VeRsIoN': "1.0.0",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            "SECTION": "/WCS_Capabilities/ContentMetadata"
        }
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        names = list(map(lambda n: n.text, soup.find_all('name')[0:2]))
        params_82 = {
            'ReQuEsT': "DescribeCoverage",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            'Version': "1.0.0",
            "COVERAGE": ",".join(names)
        }
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(len(soup.find_all('CoverageOffering')) == len(names))
        for elem in soup.find_all('CoverageOffering'):
            self.assertTrue(elem.find('name').text in names)

    def test_invalid_coverage(self):
        """
        When a DescribeCoverage request is made with COVERAGE = name1 (name1 is not in the Capabilities XML), the
        server returns a service exception.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = DescribeCoverage
            COVERAGE = WCS_COVERAGE_NOT_DEFINED
        Results:
            Valid XML where /ServiceExceptionReport/ServiceException exists.

        """

        params_82 = {
            'ReQuEsT': "DescribeCoverage",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            'Version': "1.0.0",
            "COVERAGE": "asdfasfasdf"
        }
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))

    def test_single_invalid_coverage(self):
        """
        When a DescribeCoverage request is made with COVERAGE = name1, name2 (name1 is in, and name2 is not in the
        Capabilities XML), the server returns a service exception.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
            COVERAGE = WCS_COVERAGE_NOT_DEFINED
        Results:
            Valid XML where /ServiceExceptionReport/ServiceException exists.

        """
        params_82 = {
            'ReQuEsT': "DescribeCoverage",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            'Version': "1.0.0",
            "COVERAGE": names[0] + ",asdfasdfasdf"
        }
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))

    def test_supported_formats_interpolations(self):
        """
        When a DescribeCoverage request is made, supportedFormats in the response XML provides at least one of the
        following format: GeoTIFF, HDF-EOS,DTED,NITF, GML.

        Request:
            VERSION = [[VAR_WCS_VERSION]]
            SERVICE = WCS
            REQUEST = DescribeCoverage
            COVERAGE = [[VAR_WCS_COVERAGE_1]]
        Results:
        	Valid XML where //formats contains one of GeoTIFF, HDF-EOS,DTED,NITF, GML.

        """
        # seperate here
        params_82 = {
            'ReQuEsT': "GetCapabilities",
            'VeRsIoN': "1.0.0",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            "SECTION": "/WCS_Capabilities/ContentMetadata"
        }
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        names = list(map(lambda n: n.text, soup.find_all('name')[0:2]))
        params_82 = {
            'ReQuEsT': "DescribeCoverage",
            'SeRvIcE': "WCS",
            "BOGUS": "SSS",
            'Version': "1.0.0",
            "COVERAGE": names[0]
        }
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        formats = list(map(lambda f: f.text, soup.find_all('formats')))
        self.assertTrue(len(set(["GeoTIFF", "HDF-EOS", "DTED", "NITF", "GML"]).intersection(formats)) > 0)
        interpolations = list(map(lambda f: f.text, soup.find_all('interpolationMethod')))
        self.assertTrue(
            len(
                set(["nearest neighbor", "bilinear", "bicubic", "lost area", "barycentric"]).intersection(
                    interpolations)) > 0)
