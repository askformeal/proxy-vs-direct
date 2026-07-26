import argparse
import os
import sys

from src.constants import HELP_BANNER_NARROW, HELP_BANNER_WIDE, CYAN, RESET
from src.constants import UNDEFINED
from src.constants import OPTION_TYPES, OPTION_TAG_NAME
from src.validate import validate

from src import __version__

def _get_validate_func(name):
    return lambda val: _option_validate(name, val)

def _option_validate(name, val):
    valid_val = validate(name, val)
    if valid_val is None:
        type_name = OPTION_TAG_NAME[OPTION_TYPES[name]]
        raise argparse.ArgumentTypeError(f'{val} is not a {type_name}')
    else:
        return valid_val


def _valid_url(url):
    new_url = validate.valid_url(url)
    if new_url is None:
        raise argparse.ArgumentTypeError(f'{url} is not a valid URL.')
    else:
        return new_url

class _ShowRules(argparse.Action):
    """Print PK rules and exit without requiring URL."""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)
        for action in parser._actions:
            if action.dest == 'url':
                action.required = False

class _HelpActionDefault(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, self.dest, True)
        for action in parser._actions:
            if action.dest == 'url':
                action.required = False
class _HelpActionConfig(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, self.dest, True)
        for action in parser._actions:
            if action.dest == 'config_command':
                action.required = False

class Parser(argparse.ArgumentParser):
    def __init__(self, is_sub_parser = False, **kwargs):
        if is_sub_parser:
            super().__init__(**kwargs)
        else:
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
                            epilog='Examples: \\n  python -m src https://example.com -r 10\\n  python -m src https://example.com --rules',
                            formatter_class=argparse.RawDescriptionHelpFormatter,
                            add_help=False
                            )

            # ----- public parser -----
            public_parser = argparse.ArgumentParser(add_help=False)
            public_parser.add_argument('--encoding', default=UNDEFINED, help='File encoding for output (default: utf-8)')

            group_terminal = public_parser.add_argument_group('Output to Terminal')
            group_terminal.add_argument('--quiet', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Disable terminal outputs')
            group_terminal.add_argument('--animation', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Toggle animations for better compatibility')
            group_terminal.add_argument('--color', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Toggle colors for better compatibility')

            group_file = public_parser.add_argument_group('Output to File')
            group_file.add_argument('--output-file', default=UNDEFINED, help='A path of a file to write outputs into')
            group_file.add_argument('--output-mode', default=UNDEFINED, choices=['default', 'create', 'overwrite', 'append'], help='Output to file modes: [create/overwrite/append]')

            command_sub = self.add_subparsers(dest='command', required=False)

            # ----- default (pk) parser -----
            default_parser = command_sub.add_parser('pk', parents=[public_parser], is_sub_parser=True, help='Start Proxy vs Direct PK to a given URL. This subcommand will be used if none is given', add_help=False)

            default_parser.add_argument('url', type=_valid_url, metavar='[url]', help='Target URL.')
            default_parser.add_argument('-r', '--round', type=_get_validate_func('round'), default=UNDEFINED, help='Number of rounds to PK')
            default_parser.add_argument('-d', '--decimals', type=_get_validate_func('decimals'), default=UNDEFINED, help='Decimal precision')
            default_parser.add_argument('--rules', action=_ShowRules, nargs=0, help='Show PK rules')
            default_parser.add_argument('-n', '--notify', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Send system notify on completion')
            default_parser.add_argument('-j', '--json', default=UNDEFINED, help='A path of a json file to write PK result into')
            default_parser.add_argument('--overwrite-json', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Overwrite existing json file')
            default_parser.add_argument('-h', '--help', action=_HelpActionDefault, nargs=0, help='Show this help message and exit')
            default_parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='Show version info')

            group_request = default_parser.add_argument_group('Request')
            group_request.add_argument('--user-agent', type=str, default=UNDEFINED, help='User-Agent to use in request headers')
            group_request.add_argument('--http-proxy', type=str, default=UNDEFINED, help='HTTP proxy to use. Use system proxy by default')
            group_request.add_argument('--https-proxy', type=str, default=UNDEFINED, help='HTTPS proxy to use. Use system proxy by default')
            group_request.add_argument('-t', '--timeout', type=_get_validate_func('timeout'), default=UNDEFINED, help='Timeout in seconds')

            # ----- config parser -----
            config_parser = command_sub.add_parser('config', parents=[public_parser], is_sub_parser=True, help='Edit and examine configures', add_help=False)

            config_parser.add_argument('-h', '--help', action=_HelpActionConfig, nargs=0, help='Show help message of config subcommand and exit')

            config_sub = config_parser.add_subparsers(dest='config_command', required=True)
            list_parser = config_sub.add_parser('list', is_sub_parser=True, help='List all options in configure file', add_help=False)
            list_parser.add_argument('-h', '--help', action='store_true', help='Show help message of config list subcommand and exit')

            self.help_msg = default_parser.format_help()
            self.config_help_msg = config_parser.format_help()
            self.list_help_msg = list_parser.format_help()

    def get_args(self):
        if len(sys.argv) > 1 and sys.argv[1] not in ('pk', 'config'):
            args = self.parse_args(['pk'] + sys.argv[1:])
            self.help_msg = self.format_help()
        else:
            args = self.parse_args()
        return args