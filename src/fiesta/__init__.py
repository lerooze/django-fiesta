# # Django SDMX
#
# __title__ = 'Fiesta'
# __version__ = '0.1.0'
# __author__ = 'Antonios Loumiotis'
# __license__ = 'BSD 2-Clause'
# __copyright__ = 'Copyright 2019 Antonios Loumiotis <al459@columbia.edu>'
#
# # Version synonym
# VERSION = __version__
#
# # # Header encoding (see RFC5987)
# # HTTP_HEADER_ENCODING = 'iso-8859-1'
# #
# # # Default datetime input and output formats
# # ISO_8601 = 'iso-8601'
# #
# default_app_config = 'fiesta.config.FiestaConfig'
# #
# #
# # class RemovedInDRF310Warning(DeprecationWarning):
# #     pass
# #
# #
# # class RemovedInDRF311Warning(PendingDeprecationWarning):
# #     pass

# Use 'alpha', 'beta', 'rc' or 'final' as the 4th element to indicate release type.

VERSION = (0, 0, 1, 'alpha', 1)


def get_short_version():
    return f'{VERSION[0]}.{VERSION[1]}'


def get_version():
    version = f'{VERSION[0]}.{VERSION[1]}'
    # Append 3rd digit if > 0
    if VERSION[2]:
        version = f'{version}.{VERSION[2]}'
    elif VERSION[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        version = f'{version}{mapping[VERSION[3]]}'
        if len(VERSION) == 5:
            version = f'{version}{VERSION[4]}'
    return version

default_app_config = 'fiesta.config.FiestaConfig'
