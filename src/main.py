from src import __version__
import urllib.request
from urllib.parse import urlparse
from statistics import mean, StatisticsError
from threading import Thread
import requests
import time
from datetime import datetime
import argparse
import sys

from src.plot import Plot

DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'

class DirectVsProxy:
    def __init__(self):
        self.effective_proxies = urllib.request.getproxies()
        
        parser = argparse.ArgumentParser(description=f'Proxy vs Direct {__version__}')
        parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='Show version info')
        parser.add_argument('url', help='Target URL.')
        parser.add_argument('-r', '--round', type=int, default=5, help='Number of rounds to PK.')
        parser.add_argument('-t', '--timeout', type=float, default=5.0, help='Timeout in seconds.')
        parser.add_argument('-d', '--decimals', type=int, default=2, help='Decimal precision.')
        parser.add_argument('--user-agent', type=str, default=DEFAULT_UA, help='User-Agent to use in request headers.')
        parser.add_argument('--http-proxy', type=str, default='default', help='HTTP proxy to use. Use system proxy by default.')
        parser.add_argument('--https-proxy', type=str, default='default', help='HTTPS proxy to use. Use system proxy by default.')

        self.args = parser.parse_args()

        if not self.is_valid_url(self.args.url):
            print('Invalid URL')
            sys.exit()

        self.headers = {'User-Agent': self.args.user_agent}
        
        if self.args.http_proxy != 'default':
            self.effective_proxies['http'] = self.args.http_proxy
        if self.args.https_proxy != 'default':
            self.effective_proxies['https'] = self.args.https_proxy

        self.plot = Plot(self.args.decimals)

        self.round_status = {'proxy': None, 'direct': None}

    def run(self):
        """Run proxy and direct tests, then compare results."""
        print('=' * 50)
        print(f'  PROXY vs DIRECT: {self.args.round} request(s) each, {self.args.timeout}s timeout')
        print('=' * 50)
        print()

        results = self.pk()
        print()
        self.plot._show_pk_result(results)

    @staticmethod
    def is_valid_url(url):
        """Check if URL is valid (http/https only)."""
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except ValueError:
            return False

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
                print(f"Round [{i+1}/{results['total']}]:")
                
                Thread(target=self._start_test, args=('proxy', self.effective_proxies), daemon=True).start()
                Thread(target=self._start_test, args=('direct', None), daemon=True).start()
                
                while True:
                    self.plot._print_round_info(self.round_status)
                    print('\033[F\033[K', end='') # Delete last line
                    if self.round_status['proxy'] is not None and self.round_status['direct'] is not None:
                        break
                results['completed'] += 1
                self.plot._print_round_info(self.round_status)

                results['rounds'].append({
                    'number': i+1,
                    'proxy': self.round_status['proxy'],
                    'direct': self.round_status['direct'],
                })
                
                round_result = self.plot._plot_round_result(self.round_status)
                print(round_result['msg'])
                results['proxy_score'] += round_result['proxy']
                results['direct_score'] += round_result['direct']
                results['tie_count'] += round_result['tie']

                proxy_latencies.append(self.round_status['proxy']['latency'])
                direct_latencies.append(self.round_status['direct']['latency'])
        except KeyboardInterrupt:
            print("PK stopped via keyboard interruption.")

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

    def test_url(self, url, proxies=None, timeout=5, headers={}, decimals=2) -> dict:
        """Send requests and measure latency for a given URL and proxy config."""
        if proxies is None:
            proxies = {"http": None, "https": None}

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