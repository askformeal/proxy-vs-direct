import platformdirs
import tomllib
import os

from src.constants import PLATFORM_DIR_NAME, CONFIG_FILE_NAME
from src.constants import OPTIONS, OPTIONS_LITERAL, OPTION_GROUPS, OPTION_TYPES, OPTION_TAG_NAME
from src.validate import validate
from src.output import output

class Config:
    def __init__(self):
        config_dir = platformdirs.user_config_path(PLATFORM_DIR_NAME)
        self.config_path = os.path.join(config_dir, CONFIG_FILE_NAME)
        self.options = {}
        self.raw_config = {}
        self.option_source = {}
        self.tag_name = {
            'default': 'default value',
            'auto': 'automatic environment detection',
            'config': 'configure file',
            'cli': 'CLI argument',
            }
        self.invalid_options = {}

    def _assign_option(self, name: OPTIONS_LITERAL, group=''):
        if group == '':
            father = self.raw_config
        else:
            father = self.raw_config.get(group, None)

        if father is not None:
            val = father.get(name, None)
            if val is not None:
                valid_val = validate(name, val)
                if valid_val is None:
                    option_type = OPTION_TYPES[name]
                    type_name = OPTION_TAG_NAME[option_type]
                    output.warning(f'Failed to load option \"{name}\" because its value is not a valid {type_name}.')
                    self.invalid_options[name] = f'not a valid {type_name}'
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
                for name in OPTIONS:
                    group = OPTION_GROUPS.get(name, '')
                    self._assign_option(name, group)
                return self.options
                                    
        else:
            output.info(f'Configure file {self.config_path} not found and will be skipped.')
            return {}

    def _group_options(self, options: dict) -> dict:
        result = {}
        for name, val in options.items():
            group = OPTION_GROUPS.get(name, None)
            if group is None:
                result[name] = val
            else:
                if group in result:
                    result[group][name] = val
                else:
                    result[group] = {name: val}
        return result

    def _output_options(self, options, indent=0):
        pad = '  ' * indent
        for name, val in options.items():
            if isinstance(val, dict):
                output(f'{pad}{name}:')
                self._output_options(val, indent+1)
            else:
                output(f'{pad}{name}: {val}')

    def show_list(self):
        output(f'These following options are set in {CONFIG_FILE_NAME}:')
        options = self._group_options(self.options)
        self._output_options(options, 1)
        if self.invalid_options != {}:
            output(f'These following options are set in {CONFIG_FILE_NAME} but their values are not valid:')
            options = self._group_options(self.invalid_options)
            self._output_options(options, 1)
