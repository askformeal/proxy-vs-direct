from urllib.parse import urlparse
import ipaddress
from src.output import output
from src.constants import OPTION_TO_TAG, DISABLED

class Validate:
    def __init__(self):
        self.type_validate_func = {
            'bool': self.valid_bool,
            'str': self.valid_str,
            'pos_float': self.positive_float,
            'optional_timeout': self.optional_timeout,
            'pos_int': self.positive_int,
            'output_mode': self.valid_output_mode,
            'path': self.valid_path
        }

    def __call__(self, name, val):
        option_type = OPTION_TO_TAG[name]
        func = self.type_validate_func[option_type]
        return func(val)

    def positive_float(self, val):
        try:
            val = float(val)
        except ValueError:
            return None
        else:
            if val <= 0:
                return None
            return val

    def optional_timeout(self, val):
        if val == DISABLED:
            return DISABLED
        else:
            valid_val = self.positive_float(val)
            if valid_val is None:
                return None
            else:
                return valid_val

    def positive_int(self, val):
        try:
            val = int(val)
        except ValueError:
            return None
        else:
            if val <= 0:
                return None
            return val

    def valid_url(self, val):
        """Check if URL is valid, auto-add https:// if scheme missing."""
        result = urlparse(val)
        if result.scheme == '':
            try:
                ipaddress.ip_address(result.path.split(':')[0])
            except ValueError:
                scheme = 'https'
            else:
                scheme = 'http'

            val = f'{scheme}://{val}'
            output.warning(f'No scheme found in given URL, and will use {scheme.upper()} scheme. All requests will fail if target server does not support {scheme.upper()} scheme.')
            result = urlparse(val)

        if result.scheme in ('http', 'https') and result.netloc and ' ' not in result.netloc:
            return val
        else:
            return None

    def valid_bool(self, val):
        if isinstance(val, bool):
            return val
        else:
            val = val.lower()
            return {'true': True, 'false': False}.get(val, None)

    def valid_str(self, val):
        if isinstance(val, str):
            return val
        else:
            return None

    def valid_path(self, val):
        if self.valid_str(val) is not None:
            if val == '':
                return DISABLED
            else:
                return val
        else:
            return None

    def valid_output_mode(self, val):
        if val in ('create', 'overwrite', 'append'):
            return val
        else:
            return None

validate = Validate()