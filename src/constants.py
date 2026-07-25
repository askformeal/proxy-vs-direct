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