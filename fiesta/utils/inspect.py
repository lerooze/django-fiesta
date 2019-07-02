import inspect

def non_string_iterable(obj):
    """
    Check whether object is iterable but not string.
    """
    isclass = inspect.isclass(obj)
    if isclass: condition = issubclass(obj, str)
    else: condition = isinstance(obj, str)
    return hasattr(obj, '__iter__') and not condition 
