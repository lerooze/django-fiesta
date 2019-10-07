
class ResourceConverter:
    regex = '(?:organisationscheme)|(?:agencyscheme)|(?:dataproviderscheme)|(?:dataconsumerscheme)|(?:organisationunitscheme)|(?:codelist)|(?:conceptscheme)'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

class AgencyConverter:
    regex = '(?:ECB)|(?:SDMX)'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

class ContextConverter:
    regex = '(?:datastructure)|(?:dataflow)|(?:provisionagreement)'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
