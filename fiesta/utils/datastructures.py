from dataclasses import field 
from types import MappingProxyType


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def recursive(cls, subject):
        if isinstance(subject, list):
            return [cls.recursive(val) for val in subject]
        if not isinstance(subject, dict):
            return subject
        ret = cls(subject)
        for key, val in ret.items():
            ret[key] = cls.recursive(val)
        return ret

class Empty:
    pass

def metafield(func):
    def wrapper(*args, is_attribute=False, localname=None, namespace_key=None, is_text=False, **kwargs):
        kwargs.setdefault('default', None)
        f = func(*args, **kwargs)
        meta = dict(
            is_attribute=is_attribute,
            localname=localname,
            namespace_key=namespace_key,
            is_text=is_text,
        )
        mapping = dict(SDMX=meta)
        setattr(f, 'metadata', MappingProxyType(AttrDict.recursive(mapping)))
        return f 
    return wrapper

field = metafield(field)
