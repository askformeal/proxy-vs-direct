import os
from typing import Literal, get_args
import pyfiglet
import sys

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
    'con_timeout',
    'read_timeout',
    'quiet',
    'animation',
    'color',
    'output_file',
    'output_mode',
    'force_error',
    'force_warning',
    'force_info',
    'force_notify',
    'json',
    'overwrite_json',
    'show_source',
    'show_value',
    'freeze_args',
    ]

OPTIONS = []
for name in get_args(OPTIONS_LITERAL):
    OPTIONS.append(str(name))

'''
OPTION = option names (round, user_agent, json, etc)
TAG = in-code type names (pos_int, bool, str, etc)
LABEL = readable type names for output (positive integer, boolean, string, etc)
'''

OPTION_TO_TAG = {
    'round': 'pos_int',
    'decimals': 'pos_int',
    'notify': 'bool',
    'encoding': 'str',
    'user_agent': 'str',
    'http_proxy': 'str',
    'https_proxy': 'str',
    'timeout': 'pos_float',
    'con_timeout': 'optional_timeout',
    'read_timeout': 'optional_timeout',
    'quiet': 'bool',
    'animation': 'bool',
    'color': 'bool',
    'output_file': 'path',
    'output_mode': 'output_mode',
    'force_error': 'bool',
    'force_warning': 'bool',
    'force_info': 'bool',
    'force_notify': 'bool',
    'json': 'path',
    'overwrite_json': 'bool',
    'show_source': 'bool',
    'show_value': 'bool',
    'freeze_args': 'bool',
}

TAG_TO_LABEL = { # type codename -> readable name
    'pos_int': 'positive integer',
    'bool': 'boolean',
    'str': 'string',
    'pos_float': 'positive float',
    'optional_timeout': 'positive float', # Optional timeout is basically positive float that supports DISABLED sentinal
    'output_mode': 'output mode',
    'path': 'file path'
}

OPTION_TO_LABEL = {}
for name, _type in OPTION_TO_TAG.items():
    OPTION_TO_LABEL[name] = TAG_TO_LABEL[_type]

OPTION_SECTION = {
    'quiet': 'output_to_terminal',
    'animation': 'output_to_terminal',
    'color': 'output_to_terminal',
    'output_file': 'output_to_file',
    'output_mode': 'output_to_file',
    'force_error': 'output_to_terminal',
    'force_warning': 'output_to_terminal',
    'force_info': 'output_to_terminal',
    'force_notify': 'output_to_terminal',
    'json': 'output_to_file',
    'overwrite_json': 'output_to_file',
}

DEFAULTS = {
    'round': 5,
    'decimals': 2,
    'notify': False,
    'encoding': 'utf-8',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'http_proxy': None,
    'https_proxy': None,
    'timeout': 5.0,
    'con_timeout': DISABLED,
    'read_timeout': DISABLED,
    'quiet': False,
    'animation': False,
    'color': False,
    'output_file': DISABLED,
    'output_mode': 'create',
    'force_error': False,
    'force_warning': False,
    'force_info': False,
    'force_notify': False,
    'json': DISABLED,
    'overwrite_json': False,
    'show_source': False,
    'show_value': False,
    'freeze_args': False,
}

# ANSI color helpers
RESET    = '\033[0m'
BOLD     = '\033[1m'
DIM      = '\033[2m'
RED      = '\033[31m'
GREEN    = '\033[32m'
YELLOW   = '\033[33m'
BLUE     = '\033[34m'
MAGENTA  = '\033[35m'
CYAN     = '\033[36m'
WHITE    = '\033[37m' 

ERROR = f'{RED}{BOLD}ERROR: {RESET}'
WARNING = f'{YELLOW}WARNING: {RESET}'
INFO = f'{DIM}INFO: {RESET}'

PLATFORM_DIR_NAME = 'proxy-vs-direct'
CONFIG_FILE_NAME = 'config.toml'

AFTER_PK_PAUSE = 1

SHOW_VALUE_MAX_LEN = 35

HELP_BANNER_NARROW =  pyfiglet.figlet_format('P vs D', font='ansi_shadow', width=200)
HELP_BANNER_WIDE =  pyfiglet.figlet_format('Proxy vs Direct', font='ansi_shadow', width=200)

MIN_BAR_WIDTH = 20
BAR_PAD_WIDTH = 5
BAR_DECIMALS = 1

# BAR_COMPLETED = '━' # I might need this
# BAR_BLANK = '─'

BAR_COMPLETED = '█'
BAR_BLANK = '░'

PK_REFRESH_INTERVAL = 0.05 # seconds between status refresh during PK
RULES = '''\
PK Rules:
  1. Each round, Proxy and Direct send one request to the same URL simultaneously.
  2. The side with lower latency wins the round. (-1 = Failed, counts as loss)
  3. If both fail, it is a tie.
  4. If latencies are exactly equal, it is a tie.
  5. Final score = rounds won. Higher score wins the PK.
'''

# This is NOT a for users. This is for developers (me)

option_names = sorted(list(OPTIONS))
tag_names = sorted(list(OPTION_TO_TAG.keys()))
label_names = sorted(list(OPTION_TO_LABEL.keys()))
default_names = sorted(list(DEFAULTS.keys()))

if option_names != tag_names or option_names != label_names or option_names != default_names:
    print('Mismatched names in constants.py:')
    print(f'OPTIONS: {option_names}')
    print(f'OPTION_TO_TAG: {tag_names}')
    print(f'OPTION_TO_LABEL: {label_names}')
    print(f'DEFAULTS: {default_names}')
    sys.exit(1)

'''
Where are options deployed:

Legend: option name → where it's defined / wired / validated

1. Declare     → src/constants.py → OPTIONS_LITERAL (literal type alias)
2. Default val → src/constants.py → DEFAULTS dict
3. Type        → src/constants.py → OPTION_TO_TAG dict   (maps name → type tag)
4. Type label  → src/constants.py → TAG_TO_LABEL dict    (maps type tag → human string)
5. Section       → src/constants.py → OPTION_SECTION dict  (maps name → TOML section)
6. Sentinels   → src/constants.py → UNDEFINED, DISABLED

7. Parsing / validation → src/validate.py  → Validate.validate(name, val)
8. CLI argument         → src/cli.py       → Parser.__init__ (add_argument + type= via _get_validate_func)
9. Wire to attrs        → src/main.py      → ProxyVsDirect._assign(name, val, source)
10. Layer 4 pipeline    → src/main.py      → ProxyVsDirect.__init__ (default → auto → config → CLI)
11. TOML CRUD           → src/config.py    → Config class (read / write / show_list)
12. User docs           → README.md
'''