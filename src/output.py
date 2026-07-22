import os
import io
import sys

from src.config import ENCODING

class Output:
    def __init__(self):
        self.quiet = False
        self.path = 'disabled'
        self.force_write = False
        self.write_mode = 'overwrite'
        '''
        create: create a new file, can not overwrite existing one.
        overwrite: overwrite an existing file or create a new one
        append: append to the end of a existing or newly created file 

        create: fail if file exists
        overwrite: overwrite if file exists
        append: do nothing if file exists
        '''
        self.file_ready = False
        
    def _handle_file_errors(self, e):
        if not self.quiet:
            print(f'Error: Failed to write into {self.path} because ', end='')
            if isinstance(e, PermissionError):
                print('permission is insufficient', end='')
            elif isinstance(e, IsADirectoryError):
                print('target path is a directory instead of a file', end='')
            else:
                print(f'"{e}"', end='')
            print('and outputs to file will be disabled.')
        self.path = 'disabled'

    def _write_file(self, content, mode):
        try:
            with open(self.path, mode=mode, encoding=ENCODING) as f:
                f.write(content)
        except OSError as e:
            self._handle_file_errors(e)

    def _handle_file_write(self, content):
        if self.write_mode not in ('overwrite', 'create', 'append'):
            self.__call__(f'Output to file mode must be one of the following: create, overwrite or append, not "{self.write_mode}". Outputs to file will be disabled',
                          skip_file=True)
            self.path = 'disabled'

        elif self.file_ready:
            self._write_file(content, 'a')
        
        else:
            if self.write_mode == 'create':
                if os.path.exists(self.path):   
                    self.__call__(f'Output mode is set to "create" but {self.path} already exists, and outputs to file will be disabled. '
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
            
        if not self.quiet or force:
            sys.stdout.write(text)

output = Output()
