
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
