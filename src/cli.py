import argparse
import os
from src.constants import RULES, HELP_BANNER_NARROW, HELP_BANNER_WIDE, CYAN, RESET
from src.constants import UNDEFINED
from src import validate

from src import __version__

def _positive_float(val):
    valid_val = validate.positive_float(val)
    if valid_val is None:
        raise argparse.ArgumentTypeError(f'{val} is not a positive float')
    else:
        return valid_val

def _positive_int(val):
    valid_val = validate.positive_int(val)
    if valid_val is None:
        raise argparse.ArgumentTypeError(f'{val} is not a positive integer')
    else:
        return valid_val

def _valid_url(url):
    new_url = validate.valid_url(url)
    if new_url is None:
        raise argparse.ArgumentTypeError(f'{url} is not a valid URL.')
    else:
        if new_url != url:
            validate.url_scheme_undefined = True
        return new_url

class _ShowRules(argparse.Action):
    """Print PK rules and exit without requiring URL."""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)
        for action in parser._actions:
            if action.dest == 'url':
                action.required = False

class _HelpAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, self.dest, True)
        for action in parser._actions:
            if action.dest == 'url':
                action.required = False


class Parser(argparse.ArgumentParser):
    def __init__(self):
        try:
            terminal_width = os.get_terminal_size()[0]
            if terminal_width >= 120:
                banner = HELP_BANNER_WIDE
            elif terminal_width >= 45:
                banner = HELP_BANNER_NARROW
            else:
                banner = ''
        except OSError:
            banner = HELP_BANNER_NARROW

        super().__init__(prog='proxy-vs-direct',
                         description=f'{CYAN}{banner}{RESET}Proxy vs Direct {__version__} - Make your proxy and direct connection PK on latency to a certain URL.',
                         epilog='Examples: \n  python -m src https://example.com -r 10\n  python -m src https://example.com --rules',
                         formatter_class=argparse.RawDescriptionHelpFormatter,
                         add_help=False
                         )

        self.add_argument('url', type=_valid_url, metavar='[url]', help='Target URL.')
        self.add_argument('-r', '--round', type=_positive_int, default=UNDEFINED, help='Number of rounds to PK')
        self.add_argument('-d', '--decimals', type=_positive_int, default=UNDEFINED, help='Decimal precision')
        self.add_argument('--rules', action=_ShowRules, nargs=0, help='Show PK rules')
        self.add_argument('-n', '--notify', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Send system notify on completion')
        self.add_argument('--encoding', default=UNDEFINED, help='File encoding for output (default: utf-8)')
        self.add_argument('-h', '--help', action=_HelpAction, nargs=0, help='Show this help message and exit')
        self.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='Show version info')

        group_request = self.add_argument_group('Request')
        group_request.add_argument('--user-agent', type=str, default=UNDEFINED, help='User-Agent to use in request headers')
        group_request.add_argument('--http-proxy', type=str, default=UNDEFINED, help='HTTP proxy to use. Use system proxy by default')
        group_request.add_argument('--https-proxy', type=str, default=UNDEFINED, help='HTTPS proxy to use. Use system proxy by default')
        group_request.add_argument('-t', '--timeout', type=_positive_float, default=UNDEFINED, help='Timeout in seconds')

        group_terminal = self.add_argument_group('Output to Terminal')
        group_terminal.add_argument('--quiet', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Disable terminal outputs')
        group_terminal.add_argument('--animation', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Toggle animations for better compatibility: [on/off]')
        group_terminal.add_argument('--color', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Toggle colors for better compatibility: [on/off]')

        group_file = self.add_argument_group('Output to File')
        group_file.add_argument('--output-file', default=UNDEFINED, help='A path of a file to write outputs into')
        group_file.add_argument('--output-mode', default=UNDEFINED, choices=['default', 'create', 'overwrite', 'append'], help='Output to file modes: [create/overwrite/append]')
        group_file.add_argument('-j', '--json', default=UNDEFINED, help='A path of a json file to write PK result into')
        group_file.add_argument('--overwrite-json', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Overwrite existing json file')

    def get_help_msg(self):
        return self.format_help()
