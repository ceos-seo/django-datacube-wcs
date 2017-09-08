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

    # BASE_WCS_URL = "http://192.168.100.14/web_service"
    BASE_WCS_URL = "http://demo.mapserver.org/cgi-bin/wcs"

    VAR_HIGH_UPDATESEQUENCE = 1
    VAR_LOW_UPDATESEQUENCE = -1
    # VAR_WCS_COVERAGE_1_RESX = 0.00027
    # VAR_WCS_COVERAGE_1_RESY = -0.00027
    VAR_WCS_COVERAGE_1_RESX = 0.1
    VAR_WCS_COVERAGE_1_RESY = -0.1
    VAR_WCS_COVERAGE_1_WIDTH = 100
    VAR_WCS_COVERAGE_1_HEIGHT = 100
    VAR_WCS_COVERAGE_1_FORMAT = "GeoTIFF"
    VAR_WCS_FORMAT_1_HEADER = 'image/tiff'

    BASE_PARAMETERS = {'VERSION': "1.0.0", 'SERVICE': "WCS", 'REQUEST': "GetCapabilities"}

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
        self.names = list(map(lambda n: n.text, soup.find_all('name')[0:2]))

        params = {'ReQuEsT': "DescribeCoverage", 'SeRvIcE': "WCS", 'Version': "1.0.0", "COVERAGE": self.name}
        response = self.query_server(params)
        soup = BeautifulSoup(response.text, 'xml')

        position_container = soup.find('gml:Envelope').find_all('gml:pos') if soup.find('gml:Envelope') else soup.find(
            'gml:EnvelopeWithTimePeriod').find_all('gml:pos')
        # format of (x, y), (x, y)
        bbox = list(map(lambda x: [float(x[0]), float(x[1])], map(lambda b: b.text.split(" "), position_container)))
        self.bbox = "{},{},{},{}".format(
            min([bbox[0][0], bbox[1][0]]),
            min([bbox[0][1], bbox[1][1]]), max([bbox[0][0], bbox[1][0]]), max([bbox[0][1], bbox[1][1]]))

        subset_bbox = list(map(lambda x: float(x), self.bbox.split(",")))
        subset_bbox[2] = subset_bbox[0] + ((subset_bbox[2] - subset_bbox[0]) / 10)
        subset_bbox[3] = subset_bbox[1] + ((subset_bbox[3] - subset_bbox[1]) / 10)
        self.subset_bbox = "{},{},{},{}".format(subset_bbox[0], subset_bbox[1], subset_bbox[2], subset_bbox[3])

        try:
            # we can't rely on the srs of the envelope as it isn't required - try catch.
            self.request_crs = soup.find('gml:Envelope').attrs['srsName'] if soup.find('gml:Envelope') else soup.find(
                'gml:EnvelopeWithTimePeriod').attrs['srsName']
        except:
            self.request_crs = soup.find('requestResponseCRSs').text if soup.find('requestResponseCRSs') else soup.find(
                'requestCRSs').text
        self.response_crs = soup.find('responseCRSs').text if soup.find('responseCRSs') else self.request_crs

        self.request_format = soup.find('formats').text
        coverage_offering = soup.find('CoverageOffering')
        if coverage_offering.find('timePosition'):
            self.time_position = coverage_offering.find('timePosition')
        elif coverage_offering.find('timePeriod'):
            period = coverage_offering.find('timePeriod')
            self.time_position = "{}/{}".format(period.find('beginPosition').text, period.find('endPosition').text)
            if period.find('timeResolution'):
                self.time_position += "/{}".format(period.find('timeResolution').text)

        self.parameter = None
        self.parameter_value = None
        axis_description = coverage_offering.find('AxisDescription')
        if axis_description:
            self.parameter = axis_description.find('name').text
            self.parameter_value = axis_description.find('singleValue').text

        self.interpolations = list(map(lambda f: f.text, soup.find_all('interpolationMethod')))

    def tearDown(self):
        pass

    def query_server(self, query_dict=None):
        """Query the base url with data defined by query dict, else base parameter set"""
        return requests.get(self.BASE_WCS_URL, params=(query_dict if query_dict else self.BASE_PARAMETERS))
