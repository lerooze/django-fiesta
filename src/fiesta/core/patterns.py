import re

# urn:sdmx:org.package-name.class-name=agency-id:(maintainable-parent-object-id[maintainable-parent-object-version].)?(container-object-id.)?object-id([object-version])?

MAINTAINABLE = re.compile(r'(?P<object_id>\.*)(\[(?P<version>.*)\])?')
PARENTABLE = re.compile(r'(?P<maintainable_parent_id>\.*)\[(?P<maintainable_parent_version>.*)\]\.(?P<container_id>.*?\.)?(?P<object_id>\.*)(\[(?P<version>.*)\])?')
