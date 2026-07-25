import os

from src import __version__
import urllib.request
from statistics import mean, StatisticsError
from threading import Thread
import time
from datetime import datetime
import sys
import json
from typing import Literal

import requests
from plyer import notification

from src.constants import DEFAULTS
from src.constants import PK_REFRESH_INTERVAL, AFTER_PK_PAUSE, RULES, UNDEFINED, DISABLED
from src.constants import OPTIONS, OPTIONS_LITERAL
from src.constants import BOLD, DIM, CYAN, RESET
from src.cli import Parser
from src.config import ConfigLoader
from src.output import output
from src.plot import Plot

class DirectVsProxy:
    def __init__(self):
        self.option_source = {}
        self.effective_proxies = {}
        self.plot = Plot()
        self.parser = Parser()
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

        self.url = args.url
        self.show_help = args.help
        self.show_rules = args.rules

        output.flush()

        if not is_tty:
            if self.option_source['color'] == 'default':
                output.info('Non-TTY terminal environment detected. Colors will be disabled. You can use "--color" to turn them on if this is a mis-detection')
            if self.option_source['animation'] == 'default':
                output.info('Non-TTY terminal environment detected. Animations will be disabled. You can use "--animation" to turn them on if this is a mis-detection')

        self.round_status = {'proxy': None, 'direct': None}

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
            title = f'PROXY vs DIRECT: {self.round} request(s) each, {self.timeout}s timeout'
            width = max(len(title) + 4, 50)
            output(f'{DIM}{"─" * width}{RESET}')
            output(f'{BOLD}{CYAN}  {title}{RESET}')
            output(f'{DIM}{"─" * width}{RESET}')
            output()

            results = self.pk()

            if self.animation:
                time.sleep(AFTER_PK_PAUSE)
            output()
            self.plot._show_pk_result(results)

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

    def pk(self):
        results = {
            'url': self.url,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timeout': self.timeout,
            'decimals': self.decimals,
            'http_proxy': self.effective_proxies['http'],
            'https_proxy': self.effective_proxies['https'],
            'rounds': [],
            'proxy_score': 0,
            'direct_score': 0,
            'tie_count': 0,
            'completed': 0,
            'total': self.round,
            "proxy_failed": 0,
            "direct_failed": 0,
            "proxy_average": 0,
            "direct_average": 0,
            "duration": 0
        }
        if results['http_proxy'] is None:
            results['http_proxy'] = 'Undefined, using direct connection'
        if results['https_proxy'] is None:
            results['https_proxy'] = 'Undefined, using direct connection'
        
        '''
        when complete: 
        {
            'proxy': {
                'latency': 123.22,
                'msg': 'Succeeded - Code 200'
                },
            'direct': {
                'latency': -1,
                'msg': 'FAILED - Connection Timeout'
                }
        }
        '''
        start_time = time.time()
        proxy_latencies = []
        direct_latencies = []
        try:
            for i in range(results['total']):
                self.round_status = {'proxy': None, 'direct': None}
                output(f"Round [{i+1}/{results['total']}]", end='')
                if self.animation:
                    output(':')
                else:
                    output(' waiting...')
                
                Thread(target=self._start_test, args=('proxy', self.effective_proxies), daemon=True).start()
                Thread(target=self._start_test, args=('direct', None), daemon=True).start()
                round_start_time = time.time()
                while True:
                    if self.animation:
                        self.plot._print_round_info(self.round_status, start_time=round_start_time)
                        time.sleep(PK_REFRESH_INTERVAL)
                        output('\033[F\033[K', end='', skip_file=True) # Delete last line
                    else:
                        time.sleep(PK_REFRESH_INTERVAL)
                    if self.round_status['proxy'] is not None and self.round_status['direct'] is not None:
                        break
                results['completed'] += 1
                self.plot._print_round_info(self.round_status, skip_file=False)

                results['rounds'].append({
                    'number': i+1,
                    'proxy': self.round_status['proxy'],
                    'direct': self.round_status['direct'],
                })
                
                round_result = self.plot._plot_round_result(self.round_status)
                output(round_result['msg'])
                results['proxy_score'] += round_result['proxy']
                results['direct_score'] += round_result['direct']
                results['tie_count'] += round_result['tie']

                proxy_latencies.append(self.round_status['proxy']['latency'])
                direct_latencies.append(self.round_status['direct']['latency'])
        except KeyboardInterrupt:
            output.info("PK stopped via keyboard interruption.")

        results['proxy_failed'] = proxy_latencies.count(-1)
        results['direct_failed'] = direct_latencies.count(-1)

        proxy_latencies = list(filter(lambda x: x != -1, proxy_latencies))
        direct_latencies = list(filter(lambda x: x != -1, direct_latencies))

        try:
            results['proxy_average'] = round(mean(proxy_latencies), self.decimals)
        except StatisticsError:
            results['proxy_average'] = -1
        try:
            results['direct_average'] = round(mean(direct_latencies), self.decimals)
        except StatisticsError:
            results['direct_average'] = -1

        end_time = time.time()
        results['duration'] = round(end_time-start_time, self.decimals)

        return results

    def _start_test(self, name, proxies):
        result = self.test_url(self.url, proxies, self.timeout, self.headers, self.decimals)
        self.round_status[name] = result

    @staticmethod
    def test_url(url, proxies=None, timeout=5, headers=None, decimals=2) -> dict:
        """Send requests and measure latency for a given URL and proxy config."""
        if proxies is None:
            proxies = {"http": None, "https": None}
        
        if headers is None:
            headers = {}

        result = {
            'latency': 0, # -1 = Failed
            'msg': ''
        }
        start = time.time()
        try:
            code = requests.get(url, timeout=timeout, proxies=proxies, headers=headers).status_code

        except requests.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectTimeout):
                result['latency'] = -1
                result['msg'] = 'Connection Timeout'
            elif isinstance(e, requests.exceptions.ConnectionError):
                result['latency'] = -1
                result['msg'] = 'Connection Failed'
            else:
                result['latency'] = -1
                result['msg'] = f'{type(e).__name__}'

        else:
            end = time.time()
            result['latency'] = round((end - start) * 1000, decimals)
            result['msg'] = f'Code {code}'
        
        return result
    
    def _assign(self, name: OPTIONS_LITERAL, val, source: Literal['default', 'auto', 'config', 'cli']):
        if name == 'round':
            self.round = val
        elif name == 'decimals':
            self.decimals = val
            self.plot.decimals = val
        elif name == 'notify':
            self.notify = val
        elif name == 'encoding':
            self.encoding = val
            output.set_attr(encoding=val)
        elif name == 'user_agent':
            self.headers = {'User-Agent': val}
        elif name == 'http_proxy':
            self.effective_proxies['http'] = val
        elif name == 'https_proxy':
            self.effective_proxies['https'] = val
        elif name == 'timeout':
            self.timeout = val
        elif name =='quiet':
            output.set_attr(quiet=val)
        elif name == 'animation':
            self.animation = val
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