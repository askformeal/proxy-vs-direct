from src import __version__
import urllib.request
from urllib.parse import urlparse
from statistics import mean, StatisticsError
import requests
import time
import argparse
import sys

DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'

class DirectVsProxy:
    def __init__(self):
        self.effective_proxies = urllib.request.getproxies()
        
        parser = argparse.ArgumentParser(description=f'Proxy vs Direct {__version__}')
        parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='Show version info')
        parser.add_argument('url', help='Target URL.')
        parser.add_argument('-c', '--count', type=int, default=5, help='Number of requests to send.')
        parser.add_argument('-t', '--timeout', type=float, default=5.0, help='Timeout in seconds.')
        parser.add_argument('-d', '--decimals', type=int, default=2, help='Number of digits to round.')
        parser.add_argument('--user-agent', type=str, default=DEFAULT_UA, help='User-Agent to use in request headers.')
        parser.add_argument('--http-proxy', type=str, default='default', help='HTTP proxy to use. Use system proxy by default.')
        parser.add_argument('--https-proxy', type=str, default='default', help='HTTPS proxy to use. Use system proxy by default.')

        self.args = parser.parse_args()

        if self.args.http_proxy != 'default':
            self.effective_proxies['http'] = self.args.http_proxy
        if self.args.https_proxy != 'default':
            self.effective_proxies['https'] = self.args.https_proxy

        if not self.is_valid_url(self.args.url):
            print('Invalid URL')
            sys.exit()

    def run(self):
        """Run proxy and direct tests, then compare results."""
        print('=' * 50)
        print(f'  PROXY vs DIRECT: {self.args.count} request(s) each, {self.args.timeout}s timeout')
        print('=' * 50)
        print()

        proxy_result = self.test_url(self.args.url, self.effective_proxies)
        proxy_average = proxy_result['average']

        print('=' * 50)
        print()

        direct_result = self.test_url(self.args.url, {"http": None, "https": None})
        direct_average = direct_result['average']

        self.compare(proxy_average, direct_average)

    def compare(self, proxy_average, direct_average):
        """Compare proxy and direct averages and print result."""
        print('=' * 50)
        if proxy_average == -1 and direct_average == -1:
            print('  RESULT: Both failed!')
        elif proxy_average == -1:
            print('  RESULT: Proxy failed!')
        elif direct_average == -1:
            print('  RESULT: Direct failed!')
        elif proxy_average > direct_average:
            print(f'  RESULT: Direct is faster than proxy by {round(proxy_average - direct_average, self.args.decimals)}ms')
        elif proxy_average < direct_average:
            print(f'  RESULT: Proxy is faster than direct by {round(direct_average - proxy_average, self.args.decimals)}ms')
        else:
            print(f'  RESULT: A miracle! Proxy and direct latency are EXACTLY the same at {proxy_average}ms. Make sure you get a screenshot of this.')
        print('=' * 50)

    @staticmethod
    def is_valid_url(url):
        """Check if URL is valid (http/https only)."""
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except ValueError:
            return False

    def pk(self, url, proxies):
        ...

    def test_url(self, url, proxies={"http": None, "https": None}, timeout=5, headers={}, decimals=2) -> dict:
        """Send requests and measure latency for a given URL and proxy config."""
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
                result['msg'] = 'FAILED - Connection Timeout'
            elif isinstance(e, requests.exceptions.ConnectionError):
                result['latency'] = -1
                result['msg'] = 'FAILED - Connection Failed'
            else:
                result['latency'] = -1
                result['msg'] = f'FAILED - Connection {{type(e).__name__}}'

        else:
            end = time.time()
            result['latency'] = (end - start) * 1000
            result['msg'] = f'Succeeded - Code {code}'
        
        return result