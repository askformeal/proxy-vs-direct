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
from src.config import Config
from src.output import output
from src.contest import Contest
from src.plot import Plot
from src.file_prompt import FilePrompter

class ProxyVsDirect:
    def __init__(self):
        # Just to make things cleaner
        self.notify = None
        self.encoding = None
        self.animation = None
        self.json = None
        self.overwrite_json = None
        self.show_source = None
        self.show_value = None

        self.option_source = {}
        self.option_value = {}
        self.plot = Plot()
        self.parser = Parser()
        self.contest = Contest()
        self.contest.plot = self.plot
        args = self.parser.get_args()
        self.config = Config()
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
        config = self.config.get_config()

        for name, val in config.items():
            self._assign(name, val, 'config')

        # Layer 4: CLI inputs

        for name in OPTIONS:
            val = getattr(args, name, UNDEFINED)
            if val is not UNDEFINED:
                self._assign(name, val, 'cli')

        output.flush()
        self.config.option_source = self.option_source

        self.command = args.command
        self.config_command = getattr(args, 'config_command', None)
        self.show_help = getattr(args, 'help', UNDEFINED)
        self.show_rules = getattr(args, 'rules', UNDEFINED)
        self.contest.url = getattr(args, 'url', UNDEFINED)
        self.name = getattr(args, 'name', None)
        self.value = getattr(args, 'value', None)

        if not is_tty:
            if self.option_source['color'] == 'default':
                output.info('Non-TTY terminal environment detected. Colors will be disabled. You can use "--color" to turn them on if this is a mis-detection')
            if self.option_source['animation'] == 'default':
                output.info('Non-TTY terminal environment detected. Animations will be disabled. You can use "--animation" to turn them on if this is a mis-detection')

    def run(self):
        """Run proxy and direct tests, then compare results."""

        option_info = [None, None]
        if self.show_source:
            option_info[0] = self.option_source
        if self.show_value:
            option_info[1] = self.option_value

        if self.show_value or self.show_source:
            self.plot.show_source(*option_info)

        if self.command == 'pk':
            if self.show_help:
                # Show help message
                output.help(self.parser.help_msg)

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

                if self.animation and not results['interrupted']:
                    time.sleep(AFTER_PK_PAUSE)

                output()
                self.plot.show_pk_result(results)

                if self.json != DISABLED:
                    if os.path.exists(self.json) and not self.overwrite_json:
                        output.warning(f'Failed to write into {self.json} because it already exists. You can use --overwrite-json option to overwrite this file.')
                    else:
                        try:
                            with FilePrompter(self.json, 'w', encoding=self.encoding, prefix=f'Failed to write into {self.json} because') as f:
                                json.dump(results, f, indent=4)
                        except Exception:
                            # Error prompt already sent by FilePrompter. Nothing to do here.
                            ...

                if self.notify:
                    try:
                        notification.notify(title='Proxy vs Direct', message='PK completed')
                    except Exception as e:
                        output.warning(f'Failed to send system notification: {type(e).__name__}')

        elif self.command == 'config':
            if self.config_command == 'list':
                if self.show_help:
                    output.help(self.parser.list_help_msg)
                else:
                    self.config.show_list()

            elif self.config_command == 'show':
                if self.show_help:
                    output.help(self.parser.show_help_msg)
                else:
                    self.config.show_option(self.name)

            elif self.config_command == 'where':
                if self.show_help:
                    output.help(self.parser.where_help_msg)
                else:
                    self.config.show_path()

            elif self.config_command == 'open':
                if self.show_help:
                    output.help(self.parser.open_help_msg)
                else:
                    self.config.open_file()

            elif self.config_command == 'set':
                if self.show_help:
                    output.help(self.parser.set_help_msg)
                else:
                    self.config.set_option(self.name, self.value)

            elif self.config_command == 'unset':
                if self.show_help:
                    output.help(self.parser.unset_help_msg)
                else:
                    self.config.unset_option(self.name)

            elif self.config_command == 'clean':
                if self.show_help:
                    output.help(self.parser.clean_help_msg)
                else:
                    self.config.clean_file()

            elif self.config_command == 'create':
                if self.show_help:
                    output.help(self.parser.create_help_msg)
                else:
                    self.config.create_file()

            elif self.config_command == 'purge':
                if self.show_help:
                    output.help(self.parser.purge_help_msg)
                else:
                    self.config.purge_file()

            elif self.show_help:
                output.help(self.parser.config_help_msg)
    
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
        elif name == 'show_source':
            self.show_source = val
        elif name == 'show_value':
            self.show_value = val

        self.option_source[name] = source
        self.option_value[name] = val