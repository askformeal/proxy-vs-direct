import os
import io
import sys
import re

from src.config import ENCODING, ERROR, WARNING, INFO


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
        self.no_color = False
        
    def _handle_file_errors(self, e):
        if not self.quiet:
            self.__call__(f'{WARNING} Failed to write into {self.path} because ', end='', skip_file=True)
            if isinstance(e, PermissionError):
                print('permission is insufficient', end='')
            elif isinstance(e, IsADirectoryError):
                self.__call__('target path is a directory instead of a file', end='', skip_file=True)
            else:
                self.__call__(f'"{e}"', end='', skip_file=True)
            self.__call__('and outputs to file will be disabled.', skip_file=True)
        self.path = 'disabled'

    def _write_file(self, content, mode):
        try:
            with open(self.path, mode=mode, encoding=ENCODING) as f:
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
                                f'You can use --output-mode overwrite or --force option to force overwrite this file or use "append" output mode to append to the end of this file.',
                                skip_file=True)
                    self.path = 'disabled'
                else:
                    self._write_file(content, 'w')
            
            elif self.write_mode == 'overwrite':
                self._write_file(content, 'w')

            elif self.write_mode == 'append':
                self._write_file(content, 'a')
            
            self.file_ready = True


    def __call__(self, *args, force=False, skip_file=False, **kwargs):
        buffer = io.StringIO()
        print(*args, file=buffer, **kwargs)
        text = buffer.getvalue()

        if self.path != 'disabled' and not skip_file:
            self._handle_file_write(text)

        if self.no_color:
            text = strip_ansi(text)

        if not self.quiet or force:
            sys.stdout.write(text)

output = Output()
