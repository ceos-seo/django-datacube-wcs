import unittest
import requests

from bs4 import BeautifulSoup


class TestWCSSpecification(unittest.TestCase):
    """Unittest framework meant to measure compliance with the OGC standard

    More information found here:
        https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.htm

    Each test case will reference a section of the above mentioned site. There should be a 1:1
    mapping between test cases and the test specification, even if something is stubbed out.

    Assumptions:
        There need to be at least two coverages provided by the tested server.
        The first coverage offering should include all the tested features while the second coverage could be anything.
        The first coverage offering must take one of the 5 formats described in the WCS1.0.0 standard document as the first supported format.
        The first coverage offering should have parameters defined in the axisDescription.
        If the server supports time postion, the first coverage offering should define time feature.

    """

    BASE_WCS_URL = "http://192.168.100.14:8000/web_service"

    VAR_HIGH_UPDATESEQUENCE = 1
    VAR_LOW_UPDATESEQUENCE = -1
    VAR_WCS_COVERAGE_1_RESX = 0.00027
    VAR_WCS_COVERAGE_1_RESY = -0.00027
    VAR_WCS_FORMAT_1_HEADER = 'image/tiff'

    BASE_PARAMETERS = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}

    def setUp(self):
        pass

    def tearDown(self):
        pass

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
            "FORMAT": "GeoTIFF",
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
        print(soup)
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

    def query_server(self, query_dict=None):

        return requests.get(self.BASE_WCS_URL, params=(query_dict if query_dict else self.BASE_PARAMETERS))
