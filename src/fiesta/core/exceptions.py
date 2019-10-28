# exceptions.py

from rest_framework.exceptions import APIException, ParseError

class NotImplementedError(APIException):
    status_code = '501'

class ParseSerializeError(ParseError):
    pass

class ModuleNotFoundError(Exception):
    pass

class AppNotFoundError(Exception):
    pass

class ClassNotFoundError(Exception):
    pass

class CriticalError(APIException):
    status_code = 1000
    default_code = 'critical_error'
    default_detail = 'A critical Fiesta error occured'

class ExternalError(CriticalError):
    default_code = 'external_error'
    default_detail = 'A critical external error occured'

