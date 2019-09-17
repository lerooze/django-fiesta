ORGANISATION_TYPES = (
    (None, 'None'),
    ('Agency', 'Agency'),
    ('DataConsumer', 'DataConsumer'),
    ('DataProvider', 'DataProvider'),
    ('OrganisationUnit', 'OranisationUnit'),
)

DIMENSION_TYPES = (
    ("dimension", "dimension"),
    ("measureDimension", "measureDimension")
)

OBJECT_TYPES = (
    (None, 'None'),
    ("Any", "Any"),
    ("Agency", "Agency"),
    ("AgencyScheme", "AgencyScheme"),
    ("AttachmentConstraint", "AttachmentConstraint"),
    ("Attribute", "Attribute"),
    ("AttributeDescriptor", "AttributeDescriptor"),
    ("Categorisation", "Categorisation"),
    ("Category", "Category"),
    ("CategorySchemeMap", "CategorySchemeMap"),
    ("CategoryScheme", "CategoryScheme"),
    ("Code", "Code"),
    ("CodeMap", "CodeMap"),
    ("Codelist", "Codelist"),
    ("CodelistMap", "CodelistMap"),
    ("ComponentMap", "ComponentMap"),
    ("Concept", "Concept"),
    ("ConceptMap", "ConceptMap"),
    ("ConceptScheme", "ConceptScheme"),
    ("ConceptSchemeMap", "ConceptSchemeMap"),
    ("Constraint", "Constraint"),
    ("ConstraintTarget", "ConstraintTarget"),
    ("ContentConstraint", "ContentConstraint"),
    ("Dataflow", "Dataflow"),
    ("DataConsumer", "DataConsumer"),
    ("DataConsumerScheme", "DataConsumerScheme"),
    ("DataProvider", "DataProvider"),
    ("DataProviderScheme", "DataProviderScheme"),
    ("DataSetTarget", "DataSetTarget"),
    ("DataStructure", "DataStructure"),
    ("Dimension", "Dimension"),
    ("DimensionDescriptor", "DimensionDescriptor"),
    ("DimensionDescriptorValuesTarget", "DimensionDescriptorValuesTarget"),
    ("GroupDimensionDescriptor", "GroupDimensionDescriptor"),
    ("HierarchicalCode", "HierarchicalCode"),
    ("HierarchicalCodelist", "HierarchicalCodelist"),
    ("Hierarchy", "Hierarchy"),
    ("HybridCodelistMap", "HybridCodelistMap"),
    ("HybridCodeMap", "HybridCodeMap"),
    ("IdentifiableObjectTarget", "IdentifiableObjectTarget"),
    ("Level", "Level"),
    ("MeasureDescriptor", "MeasureDescriptor"),
    ("MeasureDimension", "MeasureDimension"),
    ("Metadataflow", "Metadataflow"),
    ("MetadataAttribute", "MetadataAttribute"),
    ("MetadataSet", "MetadataSet"),
    ("MetadataStructure", "MetadataStructure"),
    ("MetadataTarget", "MetadataTarget"),
    ("Organisation", "Organisation"),
    ("OrganisationMap", "OrganisationMap"),
    ("OrganisationScheme", "OrganisationScheme"),
    ("OrganisationSchemeMap", "OrganisationSchemeMap"),
    ("OrganisationUnit", "OrganisationUnit"),
    ("OrganisationUnitScheme", "OrganisationUnitScheme"),
    ("PrimaryMeasure", "PrimaryMeasure"),
    ("Process", "Process"),
    ("ProcessStep", "ProcessStep"),
    ("ProvisionAgreement", "ProvisionAgreement"),
    ("ReportingCategory", "ReportingCategory"),
    ("ReportingCategoryMap", "ReportingCategoryMap"),
    ("ReportingTaxonomy", "ReportingTaxonomy"),
    ("ReportingTaxonomyMap", "ReportingTaxonomyMap"),
    ("ReportingYearStartDay", "ReportingYearStartDay"),
    ("ReportPeriodTarget", "ReportPeriodTarget"),
    ("ReportStructure", "ReportStructure"),
    ("StructureMap", "StructureMap"),
    ("StructureSet", "StructureSet"),
    ("TimeDimension", "TimeDimension"),
    ("Transition", "Transition"),
)

METADATA_TARGET_TYPES = (
    (None, 'None'),
    ('KeyDescriptorValuesTarget', 'KeyDescriptorValuesTarget'),
    ('DataSetTarget', 'DataSetTarget'),
    ('ConstraintContentTarget', 'ConstraintContentTarget'),
    ('ReportPeriodTarget', 'ReportPeriodTarget'),
    ('IdentifiableObjectTarget', 'IdentifiableObjectTarget'),
)

TEXT_TYPES = (
    ('name', 'name'),
    ('description', 'description'),
    ('annotation_text', 'annotation_text'),
)

DATA_TYPES = ( 
    (None, 'None'),
    ('String', 'String'),
    ('Alpha', 'Alpha'),
    ('AlphaNumeric', 'AlphaNumeric'),
    ('Numeric', 'Numeric'),
    ('BigInteger', 'BigInteger'),
    ('Integer', 'Integer'),
    ('Long', 'Long'),
    ('Short', 'Short'),
    ('Decimal', 'Decimal'),
    ('Float', 'Float'),
    ('Double', 'Double'),
    ('Boolean', 'Boolean'),
    ('URI', 'URI'),
    ('Count', 'Count'),
    ('InclusiveValueRange', 'InclusiveValueRange'),
    ('ExclusiveValueRange', 'ExclusiveValueRange'),
    ('Incremental', 'Incremental'),
    ('ObservationalTimePeriod', 'ObservationalTimePeriod'),
    ('StandardTimePeriod', 'StandardTimePeriod'),
    ('BasicTimePeriod', 'BasicTimePeriod'),
    ('GregorianTimePeriod', 'GregorianTimePeriod'),
    ('GregorianYear', 'GregorianYear'),
    ('GregorianYearMonth', 'GregorianYearMonth'),
    ('GregorianDay', 'GregorianDay'),
    ('ReportingTimePeriod', 'ReportingTimePeriod'),
    ('ReportingYear', 'ReportingYear'),
    ('ReportingSemester', 'ReportingSemester'),
    ('ReportingTrimester', 'ReportingTrimester'),
    ('ReportingQuarter', 'ReportingQuarter'),
    ('ReportingMonth', 'ReportingMonth'),
    ('ReportingWeek', 'ReportingWeek'),
    ('ReportingDay', 'ReportingDay'),
    ('DateTime', 'DateTime'),
    ('TimeRange', 'TimeRange'),
    ('Month', 'Month'),
    ('MonthDay', 'MonthDay'),
    ('Day', 'Day'),
    ('Time', 'Time'),
    ('Duration', 'Duration'),
    ('XHTML', 'XHTML'),
    ('KeyValues', 'KeyValues'),
    ('IdentifiableReference', 'IdentifiableReference'),
    ('DataSetReference', 'DataSetReference'),
    ('AttachmentConstraintReference', 'AttachmentConstraintReference'),
)


CLASS_TYPES = (
    (None, 'None'),
    ("Any", "Any"),
    ("Agency", "Agency"),
    ("AgencyScheme", "AgencyScheme"),
    ("AttachmentConstraint", "AttachmentConstraint"),
    ("Attribute", "Attribute"),
    ("AttributeDescriptor", "AttributeDescriptor"),
    ("Categorisation", "Categorisation"),
    ("Category", "Category"),
    ("CategorySchemeMap", "CategorySchemeMap"),
    ("CategoryScheme", "CategoryScheme"),
    ("Code", "Code"),
    ("CodeMap", "CodeMap"),
    ("Codelist", "Codelist"),
    ("CodelistMap", "CodelistMap"),
    ("ComponentMap", "ComponentMap"),
    ("Concept", "Concept"),
    ("ConceptMap", "ConceptMap"),
    ("ConceptScheme", "ConceptScheme"),
    ("ConceptSchemeMap", "ConceptSchemeMap"),
    ("Constraint", "Constraint"),
    ("ConstraintTarget", "ConstraintTarget"),
    ("ContentConstraint", "ContentConstraint"),
    ("Dataflow", "Dataflow"),
    ("DataConsumer", "DataConsumer"),
    ("DataConsumerScheme", "DataConsumerScheme"),
    ("DataProvider", "DataProvider"),
    ("DataProviderScheme", "DataProviderScheme"),
    ("DataSetTarget", "DataSetTarget"),
    ("DataStructure", "DataStructure"),
    ("Dimension", "Dimension"),
    ("DimensionDescriptor", "DimensionDescriptor"),
    ("DimensionDescriptorValuesTarget", "DimensionDescriptorValuesTarget"),
    ("GroupDimensionDescriptor", "GroupDimensionDescriptor"),
    ("HierarchicalCode", "HierarchicalCode"),
    ("HierarchicalCodelist", "HierarchicalCodelist"),
    ("Hierarchy", "Hierarchy"),
    ("HybridCodelistMap", "HybridCodelistMap"),
    ("HybridCodeMap", "HybridCodeMap"),
    ("IdentifiableObjectTarget", "IdentifiableObjectTarget"),
    ("Level", "Level"),
    ("MeasureDescriptor", "MeasureDescriptor"),
    ("MeasureDimension", "MeasureDimension"),
    ("Metadataflow", "Metadataflow"),
    ("MetadataAttribute", "MetadataAttribute"),
    ("MetadataSet", "MetadataSet"),
    ("MetadataStructure", "MetadataStructure"),
    ("MetadataTarget", "MetadataTarget"),
    ("Organisation", "Organisation"),
    ("OrganisationMap", "OrganisationMap"),
    ("OrganisationScheme", "OrganisationScheme"),
    ("OrganisationSchemeMap", "OrganisationSchemeMap"),
    ("OrganisationUnit", "OrganisationUnit"),
    ("OrganisationUnitScheme", "OrganisationUnitScheme"),
    ("PrimaryMeasure", "PrimaryMeasure"),
    ("Process", "Process"),
    ("ProcessStep", "ProcessStep"),
    ("ProvisionAgreement", "ProvisionAgreement"),
    ("ReportingCategory", "ReportingCategory"),
    ("ReportingCategoryMap", "ReportingCategoryMap"),
    ("ReportingTaxonomy", "ReportingTaxonomy"),
    ("ReportingTaxonomyMap", "ReportingTaxonomyMap"),
    ("ReportingYearStartDay", "ReportingYearStartDay"),
    ("ReportPeriodTarget", "ReportPeriodTarget"),
    ("ReportStructure", "ReportStructure"),
    ("StructureMap", "StructureMap"),
    ("StructureSet", "StructureSet"),
    ("TimeDimension", "TimeDimension"),
    ("Transition", "Transition"),
)


PACKAGE_TYPES = (
    (None, 'None'),
    ("base", "base"),
    ("datastructure", "datastructure"),
    ("metadatastructure", "metadatastructure"),
    ("process", "process"),
    ("registry", "registry"),
    ("mapping", "mapping"),
    ("codelist", "codelist"),
    ("categoryscheme", "categoryscheme"),
    ("conceptscheme", "conceptscheme"),
)

DIMENSION_TYPES =(
    ('Dimension', 'Dimension'),
    ('TimeDimension', 'TimeDimension'),
    ('MeasureDimension', 'MeasureDimension')
)

METATDATA_TARGET_COMPONENTS = (
    ('DIMENSION_DESCRIPTOR_VALUES_TARGET', 'KeyDescriptorValuesTarget'),
    ('DATA_SET_TARGET', 'DataSetTarget'),
    ('CONSTRAINT_CONTENT_TARGET', 'ConstraintContentTarget'),
    ('REPORT_PERIOD_TARGET', 'ReportPeriodTarget'),
    ('IDENTIFIABLE_OBJECT_TARGET', 'IdentifiableObjectTarget')
)

TOKENS = (
    ('Value', 'Value'),
    ('Name', 'Name'),
    ('Desription', 'Description')
)

ACTIONS = (
    ('Append', 'Append'),
    ('Replace', 'Replace'),
    ('Delete', 'Delete'),
)

PROGRESS = (
    ('Finished', 'Finished'),
    ('Processing', 'Processing'),
)

LANGUAGES = (
    ('en', 'English'),
    ('gr', 'Greek'),
    ('fr', 'French'),
)

NAMESPACE_MAP = {
    'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common',
    'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
    'query': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/query',
    'registry': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/registry',
    'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
    'data': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
    'dsd': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific',
    'metadata': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/metadata/generic',
    'msd': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/metadata/structurespecific',
    'footer': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message/footer',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    # None: None,
}

# NAMESPACE_CLEAN = {key:val for key, val in NAMESPACE.items() if key}

CLASS2WRAPPER = {
    'AgencySchemeDataclass': 'OrganisationSchemes',
    'DataConsumerSchemeDataclass': 'OrganisationSchemes',
    'DataProviderSchemeDataclass': 'OrganisationSchemes',
    'OrganisationUnitSchemeDataclass': 'OrganisationSchemes',
    'CodelistDataclass': 'Codelists',
    'ConceptSchemeDataclass': 'Concepts',
}

CLASS2RESOURCES = {
    'AgencySchemeDataclass': ['agencyscheme', 'organisationscheme'],
    'DataConsumerSchemeDataclass': ['dataconsumerscheme', 'organisationscheme'],
    'DataProviderSchemeDataclass': ['dataproviderscheme', 'organisationschem'],
    'OrganisationUnitSchemeDataclass': ['organisationunitscheme', 'organisationscheme'],
    'CodelistDataclass': ['codelist'],
    'ConceptSchemeDataclass': ['conceptscheme'],
}

RESOURCES = ['organisationscheme', 'agencyscheme', 'dataproviderscheme',
             'dataconsumerscheme', 'organisationunitscheme', 'codelist',
             'conceptscheme']

RESOURCE2STRUCTURE = {
    'organisationscheme': 'OrganisationSchemes',
    'agencyscheme': 'OrganisationSchemes',
    'dataproviderscheme': 'OrganisationSchemes',
    'dataconsumerscheme': 'OrganisationSchemes',
    'organisationunitscheme': 'OrganisationSchemes',
    'structure': ['OrganisationSchemes']
}

STRUCTURE2MODEL = {
    'organisationscheme': 'base.OrganisationScheme',
    'agencyscheme': 'base.OrganisationScheme',
    'dataproviderscheme': 'base.OrganisationScheme',
    'dataconsumerscheme': 'base.OrganisationScheme',
    'organisationunitscheme': 'base.OrganisationScheme',
}

QUERY_PARAMS = {
    'structure': {
        'detail': ['full', 'allstubs', 'referencestubs'],
        'references': ['none', 'parents', 'parentsandsiblings', 'children',
                       'descendants', 'all'] + RESOURCES 
    }
}

CHANNELS = (
    ('Registry', 'Registry'),
    ('Upload', 'Upload'),
    ('Interactive', 'Interactive'),
    ('RESTful_query', 'RESTful_query'),
    ('SOAP_query', 'SOAP_query'),
    ('RESTful_GUI_query', 'RESTful_GUI_query'),
    ('SOAP_GUI_query', 'SOAP_GUI_query'),
)

STATUSES = (
    ('Success', 'Success'),
    ('Warning', 'Warning'),
    ('Failure', 'Failure')
)

ASSIGNMENT_STATUS = (
    ('Mandatory', 'Mandatory'),
    ('Conditional', 'Conditional')
)

RESOURCE2MAINTAINABLE = {
    'organisationscheme': ('agency_scheme', 'data_consumer_scheme',
                           'data_provider_scheme', 'organisation_unit_scheme'),
    'agencyscheme': 'agency_scheme',
    'dataproviderscheme': 'data_provider_scheme',
    'dataconsumerscheme': 'data_consumer_scheme',
    'organisationunitscheme': 'organisation_unit_scheme',
    'conceptscheme': 'concept_scheme',
    'codelist': 'codelist',
    'datastructure': 'data_structure',
    'dataflow': 'dataflow',
}
