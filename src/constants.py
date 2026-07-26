from typing import Literal, get_args
import pyfiglet

class Undefined:
    def __repr__(self):
        return 'Undefined'

class Disabled:
    def __repr__(self):
        return 'Disabled'

UNDEFINED = Undefined()
DISABLED = Disabled()

OPTIONS_LITERAL = Literal[
    'round',
    'decimals',
    'notify',
    'encoding',
    'user_agent',
    'http_proxy',
    'https_proxy',
    'timeout',
    'quiet',
    'animation',
    'color',
    'output_file',
    'output_mode',
    'json',
    'overwrite_json'
    ]

OPTIONS = []
for name in get_args(OPTIONS_LITERAL):
    OPTIONS.append(str(name))

DEFAULTS = {
    'round': 5,
    'decimals': 2,
    'notify': False,
    'encoding': 'utf-8',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'http_proxy': None,
    'https_proxy': None,
    'timeout': 5.0,
    'quiet': False,
    'animation': False,
    'color': False,
    'output_file': DISABLED,
    'output_mode': 'create',
    'json': DISABLED,
    'overwrite_json': False
}

OPTION_TYPES = {
    'round': 'pos_int',
    'decimals': 'pos_int',
    'notify': 'bool',
    'encoding': 'str',
    'user_agent': 'str',
    'http_proxy': 'str',
    'https_proxy': 'str',
    'timeout': 'pos_float',
    'quiet': 'bool',
    'animation': 'bool',
    'color': 'bool',
    'output_file': 'path',
    'output_mode': 'output_mode',
    'json': 'path',
    'overwrite_json': 'bool',
}

OPTION_TAG_NAME = {
    'pos_int': 'positive integer',
    'bool': 'boolean',
    'str': 'string',
    'pos_float': 'positive float',
    'output_mode': 'output mode',
    'path': 'file path'
}

OPTION_GROUPS = {
    'quiet': 'output_to_terminal',
    'animation': 'output_to_terminal',
    'color': 'output_to_terminal',
    'output_file': 'output_to_file',
    'output_mode': 'output_to_file',
    'json': 'output_to_file',
    'overwrite_json': 'output_to_file',
}

FORCE_OUTPUT_ERROR = False
FORCE_OUTPUT_WARNING = False
FORCE_OUTPUT_INFO = False


# ANSI color helpers
RESET   = '\033[0m'
BOLD    = '\033[1m'
DIM     = '\033[2m'
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
CYAN    = '\033[36m'
WHITE   = '\033[37m'

ERROR = f'{RED}{BOLD}ERROR: {RESET}'
WARNING = f'{YELLOW}WARNING: {RESET}'
INFO = f'{DIM}INFO: {RESET}'

PLATFORM_DIR_NAME = 'proxy-vs-direct'
CONFIG_FILE_NAME = 'config.toml'

AFTER_PK_PAUSE = 1

HELP_BANNER_NARROW =  pyfiglet.figlet_format('P vs D', font='ansi_shadow', width=200)
HELP_BANNER_WIDE =  pyfiglet.figlet_format('Proxy vs Direct', font='ansi_shadow', width=200)

PK_REFRESH_INTERVAL = 0.05 # seconds between status refresh during PK
RULES = '''\
PK Rules:
  1. Each round, Proxy and Direct send one request to the same URL simultaneously.
  2. The side with lower latency wins the round. (-1 = Failed, counts as loss)
  3. If both fail, it is a tie.
  4. If latencies are exactly equal, it is a tie.
  5. Final score = rounds won. Higher score wins the PK.
'''

'''
Where are an option deployed:

name: remove all prefix hyphens from argument name and use underscore to replace between-word ones

name in constants.py -> OPTIONS_LITERAL
default value in constants.py -> DEFAULTS

wire to attributes in main.py -> DirectVsProxy -> _assign

validate function in validate.py if needed

name, type and group in configure file in config.py -> ConfigLoader -> get_config

auto environment detection in main.py -> DirectVsProxy -> __init__ and corresponding warning/info output if needed

CLI argument in cli.py -> Parser -> __init__
type function in cli.py if needed

references in README.md

Ask Monica to update this

'''