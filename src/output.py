import os
import io
import sys
import re
from random import choice
from pathlib import Path

from src.constants import HELP_BANNER_NARROW, HELP_BANNER_WIDE 
from src.constants import DIM, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
from src.constants import ERROR, WARNING, INFO
from src.constants import FORCE_OUTPUT_ERROR, FORCE_OUTPUT_WARNING, FORCE_OUTPUT_INFO
from src.constants import DISABLED


_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi(text):
    return _ANSI_RE.sub('', text)

class Output:
    def __init__(self):
        self.quiet = None
        self.path = None
        self.write_mode = None
        self.encoding = None
        self.color = None

        self.file_ready = False
        self.ready = False
        self.stash = []

    def set_attr(self, **kwargs):
        for name, val in kwargs.items():
            if val is not None:
                setattr(self, name, val)

    def flush(self):
        if not self.ready:
            self.ready = True
            for args, kwargs in self.stash:
                self.__call__(*args, **kwargs)
            self.stash = []
    
    def _write_file(self, content, mode):
        try:
            with open(self.path, mode=mode, encoding=self.encoding) as f:
                f.write(strip_ansi(content))
        except OSError as e:
            self._handle_file_errors(e)

    def _handle_file_errors(self, e):
        if not self.quiet:
            self.warning(f'Failed to write into \"{self.path}\" because ', end='', skip_file=True)
            if isinstance(e, PermissionError):
                self.__call__('permission is insufficient', end='', skip_file=True, output_type='warning')
            elif isinstance(e, IsADirectoryError):
                self.__call__('target path is a directory instead of a file', end='', skip_file=True, output_type='warning')
            else:
                self.__call__(f'"{e}"', end='', skip_file=True, output_type='warning')
            self.__call__('and outputs to file will be disabled.', skip_file=True, output_type='warning')
        self.path = DISABLED

    def _handle_file_write(self, content):
        if self.file_ready:
            self._write_file(content, 'a')
        
        else:
            if self.write_mode == 'create':
                if Path(self.path).exists():
                    self.__call__(f'{WARNING} Output mode is set to "create" but {self.path} already exists, and outputs to file will be disabled. '
                                f'You can use --output-mode overwrite to overwrite this file or use "append" output mode to append to the end of this file.',
                                skip_file=True)
                    self.path = DISABLED
                else:
                    self._write_file(content, 'w')
            
            elif self.write_mode == 'overwrite':
                self._write_file(content, 'w')

            elif self.write_mode == 'append':
                self._write_file(content, 'a')
            
            self.file_ready = True

    def help(self, message):
        try:
            terminal_width = os.get_terminal_size()[0]
            if terminal_width >= 120:
                banner = HELP_BANNER_WIDE
            elif terminal_width >= 45:
                banner = HELP_BANNER_NARROW
            else:
                banner = ''
        except OSError:
            output.warning('Failed to get terminal width, and will use narrow help message banner.')
            banner = HELP_BANNER_NARROW
        banner_color = choice((RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE))
        message = f'\n{banner_color}{banner}{RESET}{message}'
        if self.color:
            message+=f'\n{DIM}P.S. Run this command again, maybe something will different~{RESET}'
        self.__call__(message)

    def __call__(self, *args, force=False, skip_file=False, prefix='', output_type='normal', **kwargs): #types: normal, error, warning, info
        if self.ready:
            type_force_output_filter = {
                'normal': False,
                'error': FORCE_OUTPUT_ERROR,
                'warning': FORCE_OUTPUT_WARNING,
                'info': FORCE_OUTPUT_INFO
            }

            buffer = io.StringIO()
            print(*args, file=buffer, **kwargs)
            text = buffer.getvalue()
            text = f'{prefix}{text}'

            if self.path != DISABLED and not skip_file:
                self._handle_file_write(text)

            if not self.color:
                text = strip_ansi(text)

            if not self.quiet or force or type_force_output_filter[output_type]:
                sys.stdout.write(text)
        else:
            buffered_args = (args, {'force': force, 'skip_file': skip_file, 'prefix': prefix, 'output_type': output_type, **kwargs})
            self.stash.append(buffered_args)

    def error(self, *args, **kwargs):
        self.__call__(*args, prefix=ERROR, output_type='error', **kwargs)

    def warning(self, *args, **kwargs):
        self.__call__(*args, prefix=WARNING, output_type='warning', **kwargs)

    def info(self, *args, **kwargs):
        self.__call__(*args, prefix=INFO, output_type='info', **kwargs)

output = Output()
