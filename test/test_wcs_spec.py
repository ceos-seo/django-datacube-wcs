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

    def test_basic_service_elements(self):
        """https://cite.opengeospatial.org/teamengine/about/wcs/1.0.0/site/testreq.html#6-Basic%20Service%20Elements

        Handles section 6 of the test specification, includes the version numbering, exceptions, and basic http requests

        """

        params_62 = dict(self.BASE_PARAMETERS)
        params_62['VERSION'] = ""
        response = self.query_server(params_62)
        soup = BeautifulSoup(response.text, 'xml')
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        response = self.query_server()
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        params_62 = dict(self.BASE_PARAMETERS)
        params_62['VERSION'] = "1.0.2"
        response = self.query_server(params_62)
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        params_62 = dict(self.BASE_PARAMETERS)
        params_62['VERSION'] = "0.8.0"
        response = self.query_server(params_62)
        self.assertTrue(soup.find('WCS_Capabilities').attrs['version'] == "1.0.0")

        params_63 = dict(self.BASE_PARAMETERS)

    def query_server(self, query_dict=None):

        return requests.get(self.BASE_WCS_URL, params=(query_dict if query_dict else self.BASE_PARAMETERS))
