import os
import io
import sys
import re

from src.config import ERROR, WARNING, INFO
from src.config import FORCE_OUTPUT_ERROR, FORCE_OUTPUT_WARNING, FORCE_OUTPUT_INFO


_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi(text):
    return _ANSI_RE.sub('', text)

class Output:
    def __init__(self):
        self.quiet = False
        self.path = 'disabled'
        self.force_write = False
        self.write_mode = 'create'
        self.file_ready = False
        self.color = True
        self.encoding = 'utf-8'
        
    def _handle_file_errors(self, e):
        if not self.quiet:
            self.warning(f'Failed to write into {self.path} because ', end='', skip_file=True)
            if isinstance(e, PermissionError):
                self.__call__('permission is insufficient', end='', skip_file=True, output_type='warning')
            elif isinstance(e, IsADirectoryError):
                self.__call__('target path is a directory instead of a file', end='', skip_file=True, output_type='warning')
            else:
                self.__call__(f'"{e}"', end='', skip_file=True, output_type='warning')
            self.__call__('and outputs to file will be disabled.', skip_file=True, output_type='warning')
        self.path = 'disabled'

    def _write_file(self, content, mode):
        try:
            with open(self.path, mode=mode, encoding=self.encoding) as f:
                f.write(strip_ansi(content))
        except OSError as e:
            self._handle_file_errors(e)

    def _handle_file_write(self, content):
        if self.file_ready:
            self._write_file(content, 'a')
        
        else:
            if self.write_mode == 'create':
                if os.path.exists(self.path):   
                    self.__call__(f'{WARNING} Output mode is set to "create" but {self.path} already exists, and outputs to file will be disabled. '
                                f'You can use --output-mode overwrite or --force option to overwrite this file or use "append" output mode to append to the end of this file.',
                                skip_file=True)
                    self.path = 'disabled'
                else:
                    self._write_file(content, 'w')
            
            elif self.write_mode == 'overwrite':
                self._write_file(content, 'w')

            elif self.write_mode == 'append':
                self._write_file(content, 'a')
            
            self.file_ready = True


    def __call__(self, *args, force=False, skip_file=False, prefix='', output_type='normal', **kwargs): #types: normal, error, warning, info
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

        if self.path != 'disabled' and not skip_file:
            self._handle_file_write(text)

        if not self.color:
            text = strip_ansi(text)

        if not self.quiet or force or type_force_output_filter[output_type]:
            sys.stdout.write(text)

    def error(self, *args, **kwargs):
        self.__call__(*args, prefix=ERROR, output_type='error')

    def warning(self, *args, **kwargs):
        self.__call__(*args, prefix=WARNING, output_type='warning')

    def info(self, *args, **kwargs):
        self.__call__(*args, prefix=INFO, output_type='info')

output = Output()
