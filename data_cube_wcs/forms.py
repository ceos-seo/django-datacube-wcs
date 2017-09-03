from django import forms


class BaseRequest(forms.Form):
    """Base WCS request parameters as defined by the OGC WCS 1.0 specification"""

    request = forms.ChoiceField(
        choices=(("GetCapabilities", "GetCapabilities"), ("DescribeCoverage", "DescribeCoverage"),
                 ("GetCoverage", "GetCoverage")),
        initial="GetCapabilities")
    version = forms.CharField(required=False, initial="1.0.0")
    service = forms.ChoiceField(choies=(("WCS", "WCS")), initial="WCS")


class GetCapabilitiesForm(BaseRequest):
    """GetCapabilities request form as defined by the OGC WCS 1.0 specification"""

    section = forms.ChoiceField(
        required=False,
        choices=(("WCS_Capabilities/Service", "WCS_Capabilities/Service"),
                 ("WCS_Capabilities/Capability", "WCS_Capabilities/Capability"),
                 ("WCS_Capabilities/ContentMetadata", "WCS_Capabilities/ContentMetadata")))
    updatesequence = forms.CharField(required=False)


class DescribeCoverageForm(BaseRequest):
    """DescribeCoverage request form as defined by the OGC WCS 1.0 specification"""
    coverage = forms.CharField()


class GetCoverageForm(BaseRequest):
    """GetCoverage request form as defined by the OGC WCS 1.0 specification"""
    coverage = forms.CharField()
    crs = forms.CharField()
    response_crs = forms.CharField()
    bbox = forms.CharField()
    time = forms.CharField()
    width = forms.IntegerField()
    height = forms.IntegerField()
    resx = forms.FloatField()
    resy = forms.FloatField()

    interpolation = forms.ChoiceField(choices=(), initial="")
    format = forms.ChoiceField()
    exceptions = forms.CharField()
    parameters = forms.CharField()
