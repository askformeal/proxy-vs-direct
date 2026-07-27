from src.output import output
from tomllib import TOMLDecodeError
from typing import Literal

class FilePrompter:
    def __init__(self, *args, prefix='', suffix='.', error_prompt={}, level: Literal['error', 'warning', 'info']='error', **kwargs):

        self.prompts = {
            PermissionError: "permission is insufficient",
            FileNotFoundError: "it does not exist",
            FileExistsError: "a file of the same name and path already exists",
            IsADirectoryError: 'target path is a directory instead of a file',
            NotADirectoryError: 'part of the path is file, not directory',
            TOMLDecodeError: 'it is not a valid TOML file',
            }

        for error, prompt in error_prompt.items():
            self.prompts[error] = prompt

        self.args = args
        self.kwargs = kwargs
        self.prefix = prefix.strip()
        self.suffix = suffix.strip()
        self.level = level
        self.file = None

    def __enter__(self):
        try:            
            self.file = open(*self.args, **self.kwargs)
        except Exception as e:
            self._prompt_error(e)
            raise
        else:
            return self.file

    def __exit__(self, exc_type, exc, tb):
        if self.file:
            self.file.close()

        if exc_type is not None:
            self._prompt_error(exc)

        return False

    def _prompt_error(self, exc):
        getattr(output, self.level)(self.prefix, end=' ')

        for error, prompt in self.prompts.items():
            if isinstance(exc, error):
                if self.prefix == '':
                    prompt = prompt.capitalize()
                output(prompt, end=' ', output_type=self.level)
                break
        else:
            output(f'{exc}', end=' ', output_type=self.level)

        output(self.suffix, output_type=self.level)