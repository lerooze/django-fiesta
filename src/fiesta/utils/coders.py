from dateutil.parser import parse as datetime_convert
from distutils.util import strtobool
from datetime import datetime, date, timedelta
from decimal import Decimal
from isodate import parse_duration, duration_isoformat

def decode(value, value_type):
    if value is None: return
    if value_type == bool:
        return bool(strtobool(value))
    elif value_type in [datetime, date]:
        return datetime_convert(value)
    elif value_type == Decimal:
        return Decimal(value)
    elif value_type == timedelta:
        return parse_duration(value).totimedelta(start=datetime.now())
    elif value_type == int:
        return int(value)
    else:
        return value

def encode(value, value_type):
    if value is None: return 
    if value_type == bool:
        return 'true' if value else 'false'
    elif value_type == datetime:
        return value.strftime('%Y-%m-%dT%H:%M:%S')
    elif value_type == date:
        return value.strftime('%Y-%m-%d')
    elif value_type == Decimal:
        return str(value)
    elif value_type == timedelta:
        return duration_isoformat(value)
    elif value_type == int:
        return str(value)
    else:
        return str(value)
