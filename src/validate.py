from urllib.parse import urlparse
from src.output import output

def positive_float(val):
    try:
        val = float(val)
    except ValueError:
        return None
    else:
        if val <= 0:
            return None
        return val

def positive_int(val):
    try:
        val = int(val)
    except ValueError:
        return None
    else:
        if val <= 0:
            return None
        return val

def valid_url(val):
    """Check if URL is valid, auto-add https:// if scheme missing."""
    result = urlparse(val)
    if result.scheme == '':
        output.warning('No scheme found in given URL, and will use HTTPS scheme. All requests will fail if target server does not support HTTPS scheme.')
        val = 'https://' + val
        result = urlparse(val)
    if result.scheme in ('http', 'https') and result.netloc and ' ' not in result.netloc:
        return val

def valid_bool(val):
    if isinstance(val, bool):
        return val
    else:
        return None

def valid_str(val):
    if isinstance(val, str):
        return val
    else:
        return None

def valid_output_mode(val):
    if val in ('create', 'overwrite', 'append'):
        return val
    else:
        return None