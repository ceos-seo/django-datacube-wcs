import unittest
import requests


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
    VAR_WCS_COVERAGE_1_WIDTH = 100
    VAR_WCS_COVERAGE_1_HEIGHT = 100
    VAR_WCS_DEFAULT_FORMAT = "GeoTIFF"
    VAR_WCS_FORMAT_1_HEADER = 'image/tiff'

    BASE_PARAMETERS = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def query_server(self, query_dict=None):
        """Query the base url with data defined by query dict, else base parameter set"""
        return requests.get(self.BASE_WCS_URL, params=(query_dict if query_dict else self.BASE_PARAMETERS))
