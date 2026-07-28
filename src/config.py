import platformdirs
from pathlib import Path
import tomllib
import tomli_w
import os
import sys
import subprocess
import copy

from src.constants import PLATFORM_DIR_NAME, CONFIG_FILE_NAME
from src.constants import GREEN, RESET
from src.constants import OPTIONS, OPTIONS_LITERAL, OPTION_SECTION, OPTION_TO_LABEL
from src.validate import validate
from src.output import output
from src.file_prompt import FilePrompter

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
        self._set_config_path(Path(platformdirs.user_config_path(PLATFORM_DIR_NAME)) / CONFIG_FILE_NAME)
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
        self.skip = False

    def _set_config_path(self, path):
        try:
            self.config_path = Path(path)
        except TypeError:
            output.warning(f'Invalid configure file path: {path}, loading skipped.')
            self.config_dir = ''
            self.filename = ''
            self.skip = True
            self.file_exists = False
        else:
            self.config_dir = self.config_path.parent
            self.filename = self.config_path.name
            self.file_exists = self.config_path.exists()

    def get_config(self) -> dict:
        if not self.skip:
            if self.file_exists:
                try:
                    with FilePrompter(self.config_path, 'rb', prefix=f'Failed to read configure file {self.config_path} because', level='warning') as f:
                        self.raw_config = tomllib.load(f)

                except Exception:
                    self.corrupted = True
                    return {}
                else:
                    for name in OPTIONS:
                        section = OPTION_SECTION.get(name, '')
                        self._assign_option(name, section)
                    return self.options
                                        
            else:
                output.info(f'Configure file {self.config_path} not found and will be skipped.')
                return {}
        else:
            return {}
            

    def _assign_option(self, name: OPTIONS_LITERAL, section=''):
        if section == '':
            father = self.raw_config
        else:
            father = self.raw_config.get(section, None)

        if father is not None:
            val = father.get(name, None)
            if val is not None:
                valid_val = validate(name, val)
                if valid_val is None:
                    type_name = OPTION_TO_LABEL[name]
                    output.warning(f'Failed to load option \"{name}\" because its value \"{val}\" is not a valid {type_name}.')
                    self.invalid_options[name] = f'{val} is not a valid {type_name}'
                else:
                    self.options[name] = valid_val

    def _section_options(self, options: dict) -> dict:
        result = {}
        for name, val in options.items():
            section = OPTION_SECTION.get(name, None)
            if section is None:
                result[name] = val
            else:
                if section in result:
                    result[section][name] = val
                else:
                    result[section] = {name: val}
        return result

    def _output_options(self, options, indent=0):
        pad = '  ' * indent
        for name, val in options.items():
            if isinstance(val, dict):
                output(f'{pad}{name}:')
                self._output_options(val, indent+1)
            else:
                output(f'{pad}{name}: {val}')

    def _apply_to_file(self, content=None): # return value: ok or NOT ok
            if content is None:
                content = self.raw_config

            try:
                with FilePrompter(self.config_path, 'wb', 
                                prefix=f'Failed to write into {self.filename} because', 
                                error_prompt={FileNotFoundError: f'{self.config_dir} does not exist. You can use config create subcommand to create one'}
                                ) as f:
                    tomli_w.dump(content, f)
            except Exception:
                return False
            else:
                return True

    @require_valid_file('show option list')
    def show_list(self):
        output(f'These following options are set in {self.filename}:')
        options = self._section_options(self.options)
        self._output_options(options, 1)
        if self.invalid_options != {}:
            output(f'These following options are set in {self.filename} but their values are not valid:')
            options = self._section_options(self.invalid_options)
            self._output_options(options, 1)

    @require_valid_file('show option')
    def show_option(self, name):
        if name in self.options:
            output(f'{name}: {self.options[name]}')
        elif name in self.invalid_options:
            output(f'{name}: {self.invalid_options[name]}')

    def show_path(self):
        if self.skip:
            output.error('Can not show configure file path because --config option is set to none or is invalid.')
        else:
            if self.file_exists:
                output(f'Configure file at {self.config_path}')
            else:
                output(f'Would have load configure file from {self.config_path} but it does not exist.')

    @require_valid_file('set option')
    def set_option(self, name, val):
        valid_val = validate(name, val)
        if valid_val is None:
            output.error(f'\"{val}\" is not a valid {OPTION_TO_LABEL[name]}')
        else:
            section = OPTION_SECTION.get(name, None)
            if section is None:
                # not in a section
                self.raw_config[name] = valid_val
            else:
                if section in self.raw_config:
                    # section already exists
                    self.raw_config[section][name] = valid_val
                else:
                    # section does not exists
                    self.raw_config[section] = {name: valid_val}
           
            if self._apply_to_file():
                output(f'{GREEN}Successfully set {name} to {valid_val}.{RESET}')

    @require_valid_file('delete option')
    def unset_option(self, name, apply=True):
        section = OPTION_SECTION.get(name, None)
        if section is None:
            father = self.raw_config
        else:
            father = self.raw_config.get(section, None)

        if father is not None and name in father:
            del father[name]

            if father == {} and section is not None:
                del self.raw_config[section]

            if apply:
                if self._apply_to_file():
                    output(f'{GREEN}Successfully deleted {name}.{RESET}')
        else:
            output.error(f'Failed to delete {name} because it does not exist in the configure file.')

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
            if name not in OPTIONS + list(OPTION_SECTION.values()):
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

    def create_file(self):
        if not self.config_dir.is_dir():
            try:
                output.info(f'{self.config_dir} not found, creating...')
                self.config_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                output.error(f'Failed to create directory {self.config_dir} because ', end='')
                if isinstance(e, FileExistsError):
                    output('a file of the same name and path already exists.', output_type='error')
                elif isinstance(e, PermissionError):
                    output('permission is insufficient', output_type='error')
                elif isinstance(e, NotADirectoryError):
                    output('part of the path is file, not directory.', output_type='error')
                else:
                    output(f'\"{e}\".', output_type='error')
                return
            
        if self.file_exists:
            output.error(f'Can not create {self.config_path} because it already exists')
        else:
            if self._apply_to_file(content={}):
                output(f'Created empty configure file at {self.config_path}')

    def purge_file(self):
        try:
            self.config_path.unlink()
        except OSError as e:
            output.error(f'Failed to purge {self.filename} because ', end='')
            if isinstance(e, FileNotFoundError):
                output('it does not exist', output_type='error')
            elif isinstance(e, PermissionError):
                output('permission is insufficient', output_type='error')
            else:
                output(f'\"{e}\"', output_type='error')
        else:
            output(f'{GREEN}Successfully purged {self.config_path}.{RESET}')
            

    def open_file(self):
        if self.file_exists:
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
        else:
            output.error(f'Can not open configure file because none exists.')

    @require_valid_file('freeze arguments')
    def freeze(self, values: dict, sources: dict):
        if not self.file_exists:
            output.warning('Can not freeze arguments because no configure file exists.')
        else:
            for name in OPTIONS:
                if name != 'freeze_args': # easy to accidentally trigger unwanted freezes if write into file with other options
                    if sources[name] == 'cli':
                        self.set_option(name, values[name])