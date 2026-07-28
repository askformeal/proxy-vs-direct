import argparse
import sys

from src.constants import UNDEFINED, DIM, GREEN, BLUE, RESET
from src.constants import OPTIONS, OPTION_TO_TAG, TAG_TO_LABEL
from src.validate import validate

from src import __version__

def _valid_option(val):
    if val in OPTIONS:
        return val
    else:
        raise argparse.ArgumentTypeError(f'{val} is not a valid option name')

def _get_validate_func(name):
    return lambda val: _option_validate(name, val)

def _option_validate(name, val):
    valid_val = validate(name, val)
    if valid_val is None:
        type_name = TAG_TO_LABEL[OPTION_TO_TAG[name]]
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

class _HelpActionConfigCommand(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, self.dest, True)
        for action in parser._actions:
            if action.dest == 'name':
                action.required = False
            elif action.dest == 'value':
                action.required = False

class Parser(argparse.ArgumentParser):
    def __init__(self, is_sub_parser = False, **kwargs):
        if is_sub_parser:
            super().__init__(**kwargs)
        else:
            # ----- public parser -----
            self.public_parser = argparse.ArgumentParser(add_help=False)
            self.public_parser.add_argument('--encoding', default=UNDEFINED, help='File encoding for output (default: utf-8)')

            group_terminal = self.public_parser.add_argument_group('Output to Terminal')
            group_terminal.add_argument('--quiet', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Enable/disable terminal outputs')
            group_terminal.add_argument('--animation', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Enable/disable animations for better compatibility')
            group_terminal.add_argument('--color', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Enable/disable colors for better compatibility')
            group_terminal.add_argument('--show-source', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Show from which source each option is loaded')
            group_terminal.add_argument('--show-value', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Show the value of each option')
            group_terminal.add_argument('--freeze-args', action=argparse.BooleanOptionalAction, default=UNDEFINED, help='Freeze all given CLI arguments except --freeze-args to configure file. Existing option may be overwrote')
            group_terminal.add_argument('--config', default=UNDEFINED, help='The path of a specific configure file to load. Set to "none" to skip loading configure file') # Special argument, don't go in the 4 layer loading.

            group_file = self.public_parser.add_argument_group('Output to File')
            group_file.add_argument('--output-file', default=UNDEFINED, help='A path of a file to write outputs into')
            group_file.add_argument('--output-mode', default=UNDEFINED, choices=['default', 'create', 'overwrite', 'append'], help='Output to file modes: [create/overwrite/append]')


            epilog = '\n'.join((f'{GREEN}GitHub Repository:{RESET}',
                               f'  {BLUE}https://github.com/askformeal/proxy-vs-direct{RESET}',
                               f'\n{GREEN}If you encounter a problem or want to give a suggestion, please send a feedback by:{RESET}',
                               f'  Create an issue at {BLUE}https://github.com/askformeal/proxy-vs-direct/issues{RESET}',
                               f'  Send an E-Mail to {BLUE}muzhi1014@outlook.com{RESET}',
                               f'\n{GREEN}Examples:{RESET}',
                               '  python -m src https://example.com -r 10',
                               '  python -m src https://example.com --rules'))
            super().__init__(prog='proxy-vs-direct',
                            description=f'Proxy vs Direct {__version__} - Make your proxy and direct connection PK on latency to a certain URL.',
                            parents=[self.public_parser],
                            epilog=epilog,
                            formatter_class=argparse.RawDescriptionHelpFormatter,
                            add_help=False
                            )

            
            command_sub = self.add_subparsers(dest='command', required=False)                

            # ----- default (pk) parser -----
            default_parser = self._get_command_parser(command_sub, 'pk','Start Proxy vs Direct PK to a given URL. This subcommand will be used if none is given')

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
            config_parser = self._get_command_parser(command_sub, 'config', 'Edit and examine configure file')

            config_parser.add_argument('-h', '--help', action=_HelpActionConfig, nargs=0, help='Show the help message of config subcommand and exit')

            config_sub = config_parser.add_subparsers(dest='config_command', required=True)

            list_parser = self._get_command_parser(config_sub, 'list', 'List all options in configure file')
            list_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config list subcommand and exit')

            show_parser = self._get_command_parser(config_sub, 'show', 'Show the value of a given option in configure file')
            show_parser.add_argument('name', type=_valid_option, metavar='[name]', help='name of the option to show')
            show_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config show subcommand and exit')

            where_parser = self._get_command_parser(config_sub, 'where', 'Show the path of configure file')
            where_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config where subcommand and exit')

            open_parser = self._get_command_parser(config_sub, 'open', 'Open configure file with the default application of the current system')
            open_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config open subcommand and exit')

            set_parser = self._get_command_parser(config_sub, 'set', 'Set the value of a given option in configure file')
            set_parser.add_argument('name', type=_valid_option, metavar='[name]', help='name of the option to set')
            set_parser.add_argument('value', type=str, metavar='[value]', help='value of the option to set')
            set_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config set subcommand and exit')

            unset_parser = self._get_command_parser(config_sub, 'unset', 'Delete a given option in configure file')
            unset_parser.add_argument('name', type=_valid_option, metavar='[name]', help='name of the option to set')
            unset_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config unset subcommand and exit')

            clean_parser = self._get_command_parser(config_sub, 'clean', 'Clean configure file by deleting all invalid or undefined options')
            clean_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config clean subcommand and exit')

            create_parser = self._get_command_parser(config_sub, 'create', 'Create an empty configure file if none exists')
            create_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config create subcommand and exit')

            purge_parser = self._get_command_parser(config_sub, 'purge', 'Delete configure file')
            purge_parser.add_argument('-h', '--help', action=_HelpActionConfigCommand, nargs=0, help='Show the help message of config purge subcommand and exit')

            self.help_msg = default_parser.format_help()
            self.config_help_msg = config_parser.format_help()
            self.list_help_msg = list_parser.format_help()
            self.show_help_msg = show_parser.format_help()
            self.where_help_msg = where_parser.format_help()
            self.open_help_msg = open_parser.format_help()
            self.set_help_msg = set_parser.format_help()
            self.unset_help_msg = unset_parser.format_help()
            self.clean_help_msg = clean_parser.format_help()
            self.create_help_msg = create_parser.format_help()
            self.purge_help_msg = purge_parser.format_help()


    def _get_command_parser(self, sub, name, help_msg, description=None):
        if description is None:
            description = help_msg
        return sub.add_parser(name, parents=[self.public_parser], is_sub_parser=True, description=description, help=help_msg, add_help=False)

    def get_args(self):
        if len(sys.argv) == 1:
            args = self.parse_args(['pk', '--help'])
            self.help_msg = self.format_help()
            
        elif sys.argv[1] not in ('pk', 'config'):
            args = self.parse_args(['pk'] + sys.argv[1:])
            self.help_msg = self.format_help()
        else:
            args = self.parse_args()
        return args