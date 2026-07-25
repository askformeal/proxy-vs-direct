import os

from src import __version__
import urllib.request
import time
import sys
import json
from typing import Literal

from plyer import notification

from src.constants import DEFAULTS
from src.constants import AFTER_PK_PAUSE, RULES, UNDEFINED, DISABLED
from src.constants import OPTIONS, OPTIONS_LITERAL
from src.cli import Parser
from src.config import ConfigLoader
from src.output import output
from src.contest import Contest
from src.plot import Plot

class DirectVsProxy:
    def __init__(self):
        self.option_source = {}
        self.plot = Plot()
        self.parser = Parser()
        self.contest = Contest()
        self.contest.plot = self.plot
        args = self.parser.parse_args()
        self.config_loader = ConfigLoader()

        sys_proxies = urllib.request.getproxies()
        sys_http_proxy = sys_proxies.get('http', None)
        sys_https_proxy = sys_proxies.get('https', None) 

        # Layer 1: Hardcoded default values
        for name in OPTIONS:
            self._assign(name, DEFAULTS[name], 'default')

        # Layer 2: Automatic environment detection
        is_tty = sys.stdout.isatty()
        if is_tty:
            self._assign('animation', True, 'auto')
            self._assign('color', True, 'auto')

        if sys_http_proxy is not None:
            self._assign('http_proxy', sys_http_proxy, 'auto')
        if sys_https_proxy is not None:
            self._assign('https_proxy', sys_https_proxy, 'auto')

        # Layer 3: Configure file
        config = self.config_loader.get_config()

        for name, val in config.items():
            self._assign(name, val, 'config')

        # Layer 4: CLI inputs

        for name, val in vars(args).items():
            if val is not UNDEFINED:
                self._assign(name, val, 'cli')

        self.contest.url = args.url
        self.show_help = args.help
        self.show_rules = args.rules

        output.flush()

        if not is_tty:
            if self.option_source['color'] == 'default':
                output.info('Non-TTY terminal environment detected. Colors will be disabled. You can use "--color" to turn them on if this is a mis-detection')
            if self.option_source['animation'] == 'default':
                output.info('Non-TTY terminal environment detected. Animations will be disabled. You can use "--animation" to turn them on if this is a mis-detection')

    def run(self):
        """Run proxy and direct tests, then compare results."""

        if self.show_help:
            # Show help message
            help_msg = self.parser.get_help_msg()
            output(help_msg)

        elif self.show_rules:
            # Show rules
            output(RULES)

        else:
            # Connection PK
            if self.option_source['http_proxy'] == 'default':
                output.warning('No system HTTP proxy found, and will use direct connection as default. You may want to define one manually using --http-proxy.')
            if self.option_source['https_proxy'] == 'default':
                output.warning('No system HTTPS proxy found, and will use direct connection as default. You may want to define one manually using --https-proxy.')

            self.plot.show_pk_start(self.contest.round, self.contest.timeout)

            results = self.contest.pk()

            if self.animation:
                time.sleep(AFTER_PK_PAUSE)
            output()
            self.plot.show_pk_result(results)

            if self.json != DISABLED:
                if os.path.exists(self.json) and not self.overwrite_json:
                    output.warning(f'Failed to write into {self.json} because it already exists. You can use --overwrite-json option or --force option to overwrite this file.')
                else:
                    try:
                        with open(self.json, 'w', encoding=self.encoding) as f:
                            json.dump(results, f)
                    except OSError as e:
                        output.warning(f'Failed to write into {self.json} because ', end='')
                        if isinstance(e, PermissionError):
                            output('permission is insufficient.', output_type='warning')
                        elif isinstance(e, IsADirectoryError):
                            output('target path is a directory instead of a file.', output_type='warning')
                        else:
                            output(f'\"{e}\".', output_type='warning')

            if self.notify:
                try:
                    notification.notify(title='Proxy vs Direct', message='PK completed')
                except Exception as e:
                    output.warning(f'Failed to send system notification: {type(e).__name__}')
    
    def _assign(self, name: OPTIONS_LITERAL, val, source: Literal['default', 'auto', 'config', 'cli']):
        if name == 'round':
            self.contest.round = val
        elif name == 'decimals':
            self.contest.decimals = val
            self.plot.decimals = val
        elif name == 'notify':
            self.notify = val
        elif name == 'encoding':
            self.encoding = val
            output.set_attr(encoding=val)
        elif name == 'user_agent':
            self.contest.headers = {'User-Agent': val}
        elif name == 'http_proxy':
            self.contest.proxies['http'] = val
        elif name == 'https_proxy':
            self.contest.proxies['https'] = val
        elif name == 'timeout':
            self.contest.timeout = val
        elif name =='quiet':
            output.set_attr(quiet=val)
        elif name == 'animation':
            self.animation = val
            self.contest.animation = val
        elif name =='color':
            output.set_attr(color=val)
        elif name == 'output_file':
            output.set_attr(path=val)
        elif name == 'output_mode':
            output.set_attr(write_mode=val)
        elif name == 'json':
            self.json = val
        elif name == 'overwrite_json':
            self.overwrite_json = val
        self.option_source[name] = source