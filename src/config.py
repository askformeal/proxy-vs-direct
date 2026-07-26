import platformdirs
import tomllib
import tomli_w
import os
import sys
import subprocess
import copy

from src.constants import PLATFORM_DIR_NAME, CONFIG_FILE_NAME
from src.constants import GREEN, RESET
from src.constants import OPTIONS, OPTIONS_LITERAL, OPTION_GROUPS, OPTION_TYPES, OPTION_TAG_NAME, OPTION_TYPE_NAME
from src.validate import validate
from src.output import output

def require_valid_file(action):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if args[0].corrupted:
                output.error(f'Can not {action} because configure file is corrupted.')
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

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
        self.corrupted = False

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
                    output.warning(f'Failed to load option \"{name}\" because its value \"{val}\" is not a valid {type_name}.')
                    self.invalid_options[name] = f'{val} is not a valid {type_name}'
                else:
                    self.options[name] = valid_val

    def get_config(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'rb') as f:
                    self.raw_config = tomllib.load(f)
            except (OSError, tomllib.TOMLDecodeError) as e:
                output.warning(f'Failed to read configure file {self.config_path} because ', end='')
                if isinstance(e, PermissionError):
                    output('permission is insufficient.', output_type='warning')
                elif isinstance(e, tomllib.TOMLDecodeError):
                    output('it is not a valid TOML file.', output_type='warning')
                else:
                    output(f'{type(e).__name__}', output_type='warning')
                self.corrupted = True
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

    @require_valid_file('show option list')
    def show_list(self):
        output(f'These following options are set in {CONFIG_FILE_NAME}:')
        options = self._group_options(self.options)
        self._output_options(options, 1)
        if self.invalid_options != {}:
            output(f'These following options are set in {CONFIG_FILE_NAME} but their values are not valid:')
            options = self._group_options(self.invalid_options)
            self._output_options(options, 1)

    @require_valid_file('show option')
    def show_option(self, name):
        if name in self.options:
            output(f'{name}: {self.options[name]}')
        elif name in self.invalid_options:
            output(f'{name}: {self.invalid_options[name]}')

    def show_path(self):
        if os.path.exists(self.config_path):
            output(f'Configure file at {self.config_path}')
        else:
            output(f'Would have load configure file from {self.config_path} but it does not exist.')

    def _apply_to_file(self, content=None): # return value: ok or NOT ok
        if content is None:
            content = self.raw_config

        try:
            with open(self.config_path, 'wb') as f:
                tomli_w.dump(content, f)
        except OSError as e:
            output.error(f'Failed to write into {CONFIG_FILE_NAME} because ', end='')
            if isinstance(e, PermissionError):
                output('permission is insufficient', output_type='error')
            else:
                output(f'\"{e}\"', output_type='error')
            return False
        else:
            return True

    @require_valid_file('set option')
    def set_option(self, name, val):
        valid_val = validate(name, val)
        if valid_val is None:
            output.error(f'\"{val}\" is not a valid {OPTION_TYPE_NAME[name]}')
        else:
            group = OPTION_GROUPS.get(name, None)
            if group is None:
                # not in a group
                self.raw_config[name] = valid_val
            else:
                if group in self.raw_config:
                    # group already exists
                    self.raw_config[group][name] = valid_val
                else:
                    # group does not exists
                    self.raw_config[group] = {name: valid_val}
           
            if self._apply_to_file():
                output(f'{GREEN}Successfully set {name} to {valid_val}.{RESET}')

    @require_valid_file('clean file')
    def clean_file(self):
        save = False
        if len(self.invalid_options) > 0:
            output(f'{len(self.invalid_options)} option(s) with invalid value(s) found in configure file, deleting...')
            for name, _ in self.invalid_options.items():
                self.unset_option(name, False)                    
                output(f'  Deleted {name}')
                save = True
        else:
            output(f'No options with invalid values found.')

        output('Deleting undefined options...')
        undefined_count = 0
        raw_config_copy = copy.deepcopy(self.raw_config)
        for name, _ in raw_config_copy.items():
            if name not in OPTIONS + list(OPTION_GROUPS.values()):
                del self.raw_config[name]
                output(f'  Deleted {name}')
                undefined_count += 1
                save = True

        if undefined_count > 0:
            output(f'Deleted {undefined_count} undefined options.')
        else:
            output(f'No undefined options found.')

        if save:
            if self._apply_to_file():
                output(f'{GREEN}Configure file cleaned{RESET}')
        else:
            output(f'{GREEN}Configure file clean{RESET}')

    @require_valid_file('delete option')
    def unset_option(self, name, apply=True):
        group = OPTION_GROUPS.get(name, None)
        if group is None:
            father = self.raw_config
        else:
            father = self.raw_config.get(group, None)

        if father is not None and name in father:
            del father[name]

            if father == {} and group is not None:
                del self.raw_config[group]

            if apply:
                if self._apply_to_file():
                    output(f'{GREEN}Successfully deleted {name}.{RESET}')
        else:
            output.error(f'Failed to delete {name} because it does not exist in the configure file.')

    def create_file(self):
        if os.path.exists(self.config_path):
            output.error(f'Can not create {self.config_path} because it already exists')
        else:
            self._apply_to_file(content={})
            output(f'Created empty configure file at {self.config_path}')

    def purge_file(self):
        try:
            os.remove(self.config_path)
        except OSError as e:
            output.error(f'Failed to purge {CONFIG_FILE_NAME} because ', end='')
            if isinstance(e, FileNotFoundError):
                output('it does not exist', output_type='error')
            elif isinstance(e, PermissionError):
                output('permission is insufficient', output_type='error')
            else:
                output(f'\"{e}\"', output_type='error')
        else:
            output(f'{GREEN}Successfully purge {self.config_path}.{RESET}')
            

    def open_file(self):
        output(f'Opening {self.config_path} with your system\'s default application...')
        if sys.platform == 'win32':
            os.startfile(self.config_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', self.config_path])
        else:
            result = subprocess.run(['xdg-open', self.config_path], capture_output=True)
            if result.returncode != 0:
                msg = result.stderr.decode().strip()
                output.error(f'Failed to open {self.config_path}: \"{msg}\". Make sure that you have xdg-open installed on your system.')