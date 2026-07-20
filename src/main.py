from src import __version__
import urllib.request
from urllib.parse import urlparse
from statistics import mean, StatisticsError
import requests
import time
import argparse
import sys

class DirectVsProxy:
    def __init__(self):
        self.sys_proxies = urllib.request.getproxies()


        DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        
        parser = argparse.ArgumentParser(description=f'Proxy vs Direct {__version__}')
        parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='Show version info')
        parser.add_argument('url', help='Target URL.')
        parser.add_argument('-c', '--count', type=int, default=5, help='Number of requests to send.')
        parser.add_argument('-t', '--timeout', type=float, default=5.0, help='Timeout in seconds.')
        parser.add_argument('-d', '--decimals', type=int, default=2, help='Number of digits to round.')
        parser.add_argument('--user-agent', type=str, default=DEFAULT_UA, help='User-Agent to use in request headers')

        self.args = parser.parse_args()



        if not self.is_valid_url(self.args.url):
            print('Invalid URL')
            sys.exit()

    def run(self):
        """Run proxy and direct tests, then compare results."""
        print('=' * 50)
        print(f'  PROXY vs DIRECT: {self.args.count} request(s) each, {self.args.timeout}s timeout')
        print('=' * 50)
        print()

        proxy_result = self.test_url(self.args.url, self.sys_proxies)
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

    def test_url(self, url, proxies):
        """Send requests and measure latency for a given URL and proxy config."""

        result = {
            'latencies': [],
            'total': self.args.count,
            'succeeded': 0,
            'failed': 0,
            'completed': 0,
            'average': 0
        }

        headers = {'User-Agent': self.args.user_agent}

        print(f'>> Testing {url}  ({self.args.count} request(s), timeout={self.args.timeout}s)')
        
        for name, address in proxies.items():
            print(f'   proxy[{name}] = {address}')
        print('-' * 50)

        try:
            for i in range(self.args.count):
                start = time.time()
                try:
                    code = requests.get(url, timeout=self.args.timeout, proxies=proxies, headers=headers).status_code

                except requests.RequestException as e:
                    result['failed'] += 1
                    if isinstance(e, requests.exceptions.ConnectTimeout):
                        print(f'  [{i+1:>2}/{self.args.count}] FAILED   - Connection Timeout')
                    elif isinstance(e, requests.exceptions.ConnectionError):
                        print(f'  [{i+1:>2}/{self.args.count}] FAILED   - Connection Failed')
                    else:
                        print(f'  [{i+1:>2}/{self.args.count}] FAILED   - {type(e).__name__}')

                else:
                    end = time.time()
                    latency = (end - start) * 1000
                    print(f'  [{i+1:>2}/{self.args.count}] OK       - {round(latency, self.args.decimals):>8}ms  (status {code})')
                    result['latencies'].append(latency)
                    result['succeeded'] += 1
                result['completed'] += 1

        except KeyboardInterrupt:
            print(f'\n  !! Stopped via keyboard interrupt after [{result["completed"]}/{self.args.count}] completed requests')

        print('-' * 50)
        try:
            average = round(mean(result['latencies']), self.args.decimals)
            print(f'  Average latency: {average}ms\n')
        except StatisticsError:
            average = -1
            print(f'  All requests failed\n')

        result['average'] = average

        return result