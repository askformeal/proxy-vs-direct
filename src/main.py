from src import __version__
import urllib.request
from statistics import mean, StatisticsError
from threading import Thread
import time
from datetime import datetime
import sys

import requests
from plyer import notification

from src.config import DEFAULT_UA, PK_REFRESH_INTERVAL, AFTER_PK_PAUSE, BOLD, DIM, CYAN, RESET, ERROR, WARNING, INFO
from src.cli import Parser
from src.output import output
from src.plot import Plot

class DirectVsProxy:
    def __init__(self):
        parser = Parser()
        self.args = parser.get_args()
        help_msg = parser.get_help_msg()

        output.quiet = self.args.quiet
        output.path = self.args.output_file
        if self.args.output_mode == 'default':
            if self.args.force:
                output.write_mode = 'overwrite'
            else:
                output.write_mode = 'create'
        else:
            output.write_mode = self.args.output_mode
        
        is_atty = sys.stdout.isatty()
        if self.args.animation == 'default':
            if not is_atty:
                output(f'{INFO} Non-TTY terminal environment detected. Animations will be disabled. You can use "--animation on" to turn them on if this is a mis-detection')
                self.args.animation = 'off'
            else:
                self.args.animation = 'on'
        
        if self.args.color == 'default':
            if not is_atty:
                output(f'{INFO} Non-TTY terminal environment detected. Colors will be disabled. You can use "--color on" to turn them on if this is a mis-detection')
                output.no_color = True
            else:
                output.no_color = False
        else:
            output.no_color = {'on': False, 'off': True}[self.args.color]

        if self.args.help:
            output(help_msg)
            sys.exit()

        self.headers = {}
        if self.args.user_agent == 'default':
            self.headers['User-Agent'] = DEFAULT_UA
        else:
            self.headers['User-Agent'] = self.args.user_agent
        
        self.effective_proxies = urllib.request.getproxies()
        if self.args.http_proxy != 'default':
            self.effective_proxies['http'] = self.args.http_proxy
        if self.args.https_proxy != 'default':
            self.effective_proxies['https'] = self.args.https_proxy

        # fallback to direct if no system proxy found
        if 'http' not in self.effective_proxies:
            output(f'{WARNING} No system HTTP proxy found, and will use direct connection instead. You may want to define one manually using --http-proxy.')
            self.effective_proxies['http'] = None
        
        # fallback to direct if no system proxy found
        if 'https' not in self.effective_proxies:
            output(f'{WARNING} No system HTTPS proxy found, and will use direct connection instead. You may want to define one manually using --https-proxy.')
            self.effective_proxies['https'] = None
        

        self.plot = Plot(self.args.decimals)

        self.round_status = {'proxy': None, 'direct': None}

    def run(self):
        """Run proxy and direct tests, then compare results."""
        title = f'PROXY vs DIRECT: {self.args.round} request(s) each, {self.args.timeout}s timeout'
        width = max(len(title) + 4, 50)
        output(f'{DIM}{"─" * width}{RESET}')
        output(f'{BOLD}{CYAN}  {title}{RESET}')
        output(f'{DIM}{"─" * width}{RESET}')
        output()

        results = self.pk()
        if self.args.animation == 'on':
            time.sleep(AFTER_PK_PAUSE)
        output()
        self.plot._show_pk_result(results)
        if self.args.notify:
            notification.notify(title='Proxy vs Direct', message='PK completed')

    def pk(self):
        results = {
            'url': self.args.url,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timeout': self.args.timeout,
            'decimals': self.args.decimals,
            'http_proxy': self.effective_proxies['http'],
            'https_proxy': self.effective_proxies['https'],
            'rounds': [],
            'proxy_score': 0,
            'direct_score': 0,
            'tie_count': 0,
            'completed': 0,
            'total': self.args.round,
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
                if self.args.animation == 'on':
                    output(':')
                else:
                    output(' waiting...')
                
                Thread(target=self._start_test, args=('proxy', self.effective_proxies), daemon=True).start()
                Thread(target=self._start_test, args=('direct', None), daemon=True).start()
                round_start_time = time.time()
                while True:
                    if self.args.animation == 'on':
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
            output(f"{INFO} PK stopped via keyboard interruption.")

        results['proxy_failed'] = proxy_latencies.count(-1)
        results['direct_failed'] = direct_latencies.count(-1)

        proxy_latencies = list(filter(lambda x: x != -1, proxy_latencies))
        direct_latencies = list(filter(lambda x: x != -1, direct_latencies))

        try:
            results['proxy_average'] = round(mean(proxy_latencies), self.args.decimals)
        except StatisticsError:
            results['proxy_average'] = -1
        try:
            results['direct_average'] = round(mean(direct_latencies), self.args.decimals)
        except StatisticsError:
            results['direct_average'] = -1

        end_time = time.time()
        results['duration'] = round(end_time-start_time, self.args.decimals)

        return results

    def _start_test(self, name, proxies):
        result = self.test_url(self.args.url, proxies, self.args.timeout, self.headers, self.args.decimals)
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