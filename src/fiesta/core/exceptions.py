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
