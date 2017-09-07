import unittest
import requests

from bs4 import BeautifulSoup

from .test_wcs_spec import TestWCSSpecification


class TestDescribeCoverage(TestWCSSpecification):
    """"""

    def test_describe_coverage_request(self):
        """Test the DescribeCoverage request operation - Section 8.2

        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#8-DescribeCoverage%20Operation

        """

        params_82 = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", "BOGUS": "SSS"}
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))

        params_82 = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", "BOGUS": "SSS", 'Version': "0.0.0.0"}
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('ServiceExceptionReport'))

        # regarding 823 and 824 - these seem to say the same case, but different results. I'm going with the return all case.
        params_82 = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0"}
        response = self.query_server(params_82)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(len(soup.find_all('CoverageOffering')) > 1)

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
