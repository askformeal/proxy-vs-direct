import pyfiglet

DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
PK_REFRESH_INTERVAL = 0.05 # seconds between status refresh during PK
RULES = '''\
PK Rules:
  1. Each round, Proxy and Direct send one request to the same URL simultaneously.
  2. The side with lower latency wins the round. (-1 = Failed, counts as loss)
  3. If both fail, it is a tie.
  4. If latencies are exactly equal, it is a tie.
  5. Final score = rounds won. Higher score wins the PK.
'''
ENCODING = 'utf-8'

# ANSI color helpers
RESET   = '\033[0m'
BOLD    = '\033[1m'
DIM     = '\033[2m'
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
CYAN    = '\033[36m'
WHITE   = '\033[37m'

ERROR = f'{RED}{BOLD}ERROR:{RESET}'
WARNING = f'{YELLOW}WARNING:{RESET}'
INFO = f'{DIM}INFO:{RESET}'

AFTER_PK_PAUSE = 1

HELP_BANNER =  pyfiglet.figlet_format('P vs D', font='ansi_shadow', width=200)