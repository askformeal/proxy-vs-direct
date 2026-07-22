import os
import io
import sys

class Output:
    def __init__(self):
        self.quiet = False
        self.path = 'disabled'
        self.overwrite = False
        self.file_ready = False
        
    def _handle_file_errors(self, e):
        if not self.quiet:
            print(f'Error: Failed to write into {self.path} because ', end='')
            if isinstance(e, PermissionError):
                print('permission is insufficient', end='')
            elif isinstance(e, IsADirectoryError):
                print('target path is a directory instead of a file', end='')
            else:
                print(f'\"{e}\"', end='')
            print('and outputs to file will be disabled.')
        self.path = 'disabled'

    def _write_to_file(self, content):
        if os.path.exists(self.path) and not self.overwrite and not self.file_ready:
            # path exists, not overwrite and file not prepared
            self.__call__(f'{self.path} already exists, and outputs to file will be disabled. You can use --output-overwrite or --force option to overwrite this file.',
                          skip_file=True)
            self.path = 'disabled'
        
        elif not self.file_ready:
            # file don't exist or should be overwrote. clear/create file.
            try:
                with open(self.path, 'w') as f:
                    ...
                self.file_ready = True
            except OSError as e:
                self._handle_file_errors(e)
        
        else:
            # file is ready. write it.
            try:
                with open(self.path, 'a') as f:
                    f.write(content)
            except OSError as e:
                self._handle_file_errors(e)

    def __call__(self, *args, force=False, skip_file=False, **kwargs):
        buffer = io.StringIO()
        print(*args, file=buffer, **kwargs)
        text = buffer.getvalue()

        if self.path != 'disabled' and not skip_file:
            self._write_to_file(text)
            
        if not self.quiet or force:
            sys.stdout.write(text)

output = Output()