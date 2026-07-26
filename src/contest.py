from statistics import mean, StatisticsError
from threading import Thread
import time
from datetime import datetime
import requests

from src.constants import PK_REFRESH_INTERVAL
from src.output import output

class Contest:
    def __init__(self):
        self.url = ''
        self.round = 0
        self.timeout = 0
        self.proxies = {}
        self.headers = {}
        self.decimals = 0
        self.animation = False
        self.plot = None

        self.round_status = {'proxy': None, 'direct': None}

    def pk(self):
        results = {
            'url': self.url,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timeout': self.timeout,
            'decimals': self.decimals,
            'http_proxy': self.proxies['http'],
            'https_proxy': self.proxies['https'],
            'rounds': [],
            'proxy_score': 0,
            'direct_score': 0,
            'tie_count': 0,
            'completed': 0,
            'total': self.round,
            'interrupted': False,
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
                
                Thread(target=self._start_test, args=('proxy', self.proxies), daemon=True).start()
                Thread(target=self._start_test, args=('direct', None), daemon=True).start()
                round_start_time = time.time()
                while True:
                    if self.animation:
                        self.plot.print_round_info(self.round_status, start_time=round_start_time)
                        time.sleep(PK_REFRESH_INTERVAL)
                        output('\033[F\033[K', end='', skip_file=True) # Delete last line
                    else:
                        time.sleep(PK_REFRESH_INTERVAL)
                    if self.round_status['proxy'] is not None and self.round_status['direct'] is not None:
                        break
                results['completed'] += 1
                self.plot.print_round_info(self.round_status, skip_file=False)

                results['rounds'].append({
                    'number': i+1,
                    'proxy': self.round_status['proxy'],
                    'direct': self.round_status['direct'],
                })
                
                round_result = self.plot.plot_round_result(self.round_status)
                output(round_result['msg'])
                results['proxy_score'] += round_result['proxy']
                results['direct_score'] += round_result['direct']
                results['tie_count'] += round_result['tie']

                proxy_latencies.append(self.round_status['proxy']['latency'])
                direct_latencies.append(self.round_status['direct']['latency'])
        except KeyboardInterrupt:
            output.info("PK stopped via keyboard interruption.")
            results['interrupted'] = True

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