import platformdirs
import tomllib
import os
from typing import Literal

from src.constants import PLATFORM_DIR_NAME, CONFIG_FILE_NAME, OPTIONS_LITERAL
from src.validate import positive_float, positive_int, valid_bool, valid_output_mode, valid_str
from src.output import output

class ConfigLoader:
    def __init__(self):
        config_dir = platformdirs.user_config_path(PLATFORM_DIR_NAME)
        self.config_path = os.path.join(config_dir, CONFIG_FILE_NAME)
        self.options = {}
        self.raw_config = {}
        self.type_validate_func = {
            'boolean': valid_bool,
            'string': valid_str,
            'positive float': positive_float,
            'positive integer': positive_int,
            'output mode': valid_output_mode,
        }

    def _assign_option(self, name: OPTIONS_LITERAL, option_type, group=''):
        if group == '':
            father = self.raw_config
        else:
            father = self.raw_config.get(group, None)

        if father is not None:
            val = father.get(name, None)
            if val is not None:
                validate_func = self.type_validate_func[option_type]
                valid_val = validate_func(val)
                if valid_val is None:
                    output.warning(f'Failed to load option \"{name}\" because its value is not a valid {option_type}.')
                else:
                    self.options[name] = valid_val

    def get_config(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'rb') as f:
                    self.raw_config = tomllib.load(f)
            except (OSError, tomllib.TOMLDecodeError) as e:
                output.warning(f'Failed to read configure file {self.config_path} because', end='')
                if isinstance(e, PermissionError):
                    output('permission is insufficient.', output_type='warning')
                elif isinstance(e, tomllib.TOMLDecodeError):
                    output('it is not a valid TOML file.', output_type='warning')
                else:
                    output(f'{type(e).__name__}', output_type='warning')
                return {}
            else:                
                self._assign_option('round', 'positive integer')
                self._assign_option('decimals', 'positive integer')
                self._assign_option('notify', 'boolean')
                self._assign_option('encoding', 'string')
                self._assign_option('user_agent', 'string')
                self._assign_option('http_proxy', 'string')
                self._assign_option('https_proxy', 'string')
                self._assign_option('timeout', 'positive float')
                self._assign_option('quiet', 'boolean', 'output_to_terminal')
                self._assign_option('animation', 'boolean', 'output_to_terminal')
                self._assign_option('color', 'boolean', 'output_to_terminal')
                self._assign_option('output_file', 'string', 'output_to_file')
                self._assign_option('output_mode', 'output mode', 'output_to_file')
                self._assign_option('json', 'string', 'output_to_file')
                self._assign_option('overwrite_json', 'boolean', 'output_to_file')
                return self.options
                                    
        else:
            output.info(f'Configure file {self.config_path} not found and will be skipped.')
            return {}