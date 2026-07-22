import argparse
from src.output import output
from src.config import RULES

from src import __version__

def positive_float(val):
    try:
        val = float(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f'{val} is not a positive float')
    else:
        if val <= 0:
            raise argparse.ArgumentTypeError(f'{val} is not a positive float')
        return val

def positive_int(val):
    try:
        val = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f'{val} is not a positive integer')
    else:
        if val <= 0:
            raise argparse.ArgumentTypeError(f'{val} is not a positive integer')
        return val

class _ShowRules(argparse.Action):
    """Print PK rules and exit without requiring URL."""
    def __call__(self, parser, namespace, values, option_string=None):
        output(RULES)
        parser.exit()

def get_args():
    parser = argparse.ArgumentParser(
        prog='proxy-vs-direct', 
        description=f'Proxy vs Direct {__version__} - Make your proxy and direct connection PK on latency to a certain URL.',
        epilog='Examples: \n  python -m src https://example.com -r 10\n  python -m src https://example.com --rules',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('url', help='Target URL.')
    parser.add_argument('-r', '--round', type=positive_int, default=5, help='Number of rounds to PK.')
    parser.add_argument('-d', '--decimals', type=positive_int, default=2, help='Decimal precision.')
    parser.add_argument('--rules', action=_ShowRules, nargs=0, help='Show PK rules')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='Show version info')
    
    group_request = parser.add_argument_group('Request')
    group_request.add_argument('--user-agent', type=str, default='default', help='User-Agent to use in request headers.')
    group_request.add_argument('--http-proxy', type=str, default='default', help='HTTP proxy to use. Use system proxy by default.')
    group_request.add_argument('--https-proxy', type=str, default='default', help='HTTPS proxy to use. Use system proxy by default.')
    group_request.add_argument('-t', '--timeout', type=positive_float, default=5.0, help='Timeout in seconds.')
    
    group_terminal = parser.add_argument_group('Output to Terminal')
    group_terminal.add_argument('--quiet', action='store_true', help='Disable terminal outputs.')
    group_terminal.add_argument('--animation', default='default', choices=['default', 'on', 'off'], help='Toggle animations for better compatibility: [on/off]')
    group_terminal.add_argument('--color', default='default', choices=['default', 'on', 'off'], help='Toggle colors for better compatibility: [on/off]')
    
    group_file = parser.add_argument_group('Output to File')
    group_file.add_argument('--output-file', default='disabled', help='A path of a file to write outputs into.')
    group_file.add_argument('--output-mode', default='default', choices=['default', 'create', 'overwrite', 'append'], help='Output to file modes: [create/overwrite/append]')
    group_file.add_argument('-f', '--force', action='store_true', help='Force overwrite all files. Will set output mode to "overwrite" unless manually specified with --output-mode option.')

    return parser.parse_args()