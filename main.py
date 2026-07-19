import urllib.request
from urllib.parse import urlparse
import requests
import time
import argparse
import sys


def is_valid_url(url):
    """Check if URL is valid (http/https only)."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False


def test_url(url, proxies, count, timeout, decimals):
    """Send requests and measure latency."""
    print(f'>> Testing {url}  ({count} request(s), timeout={timeout}s)')
    for name, address in proxies.items():
        print(f'   proxy[{name}] = {address}')
    print('-' * 50)

    latencies = []
    try:
        for i in range(count):
            start = time.time()
            try:
                code = requests.get(url, timeout=timeout, proxies=proxies).status_code

            except requests.exceptions.ConnectTimeout:
                print(f'  [{i+1:>2}/{count}] FAILED   - Connection Timeout')
            except requests.exceptions.ConnectionError:
                print(f'  [{i+1:>2}/{count}] FAILED   - Connection Failed')
            except requests.RequestException as e:
                print(f'  [{i+1:>2}/{count}] FAILED   - {type(e).__name__}')

            else:
                end = time.time()
                latency = (end - start) * 1000
                print(f'  [{i+1:>2}/{count}] OK       - {round(latency, decimals):>8}ms  (status {code})')
                latencies.append(latency)

    except KeyboardInterrupt:
        print(f'\n  !! Stopped via keyboard interrupt after [{i}/{count}] requests')

    print('-' * 50)
    try:
        average = round(sum(latencies)/len(latencies), decimals)
        print(f'  Average latency: {average}ms\n')
    except ZeroDivisionError:
        average = -1
        print(f'  All requests failed\n')

    return average


# Get system proxy settings
sys_proxies = urllib.request.getproxies()

# Parse arguments
parser = argparse.ArgumentParser(description='Proxy vs Direct')
parser.add_argument('url', help='Target URL.')
parser.add_argument('-c', '--count', type=int, default=5, help='Number of requests to send.')
parser.add_argument('-t', '--timeout', type=float, default=5.0, help='Timeout.')
parser.add_argument('-d', '--decimals', type=int, default=2, help='Number of digits to round')

args = parser.parse_args()

if not is_valid_url(args.url):
    print('Invalid URL')
    sys.exit()

# Run tests
print('=' * 50)
print(f'  PROXY vs DIRECT: {args.count} request(s) each, {args.timeout}s timeout')
print('=' * 50)
print()

proxy_average = test_url(args.url, sys_proxies, args.count, args.timeout, args.decimals)

print('=' * 50)
print()

direct_average = test_url(args.url, {"http": None, "https": None}, args.count, args.timeout, args.decimals)

# Compare results
print('=' * 50)
if proxy_average == -1 and direct_average == -1:
    print('  RESULT: Both failed!')
elif proxy_average == -1:
    print('  RESULT: Proxy failed!')
elif direct_average == -1:
    print('  RESULT: Direct failed!')
elif proxy_average > direct_average:
    print(f'  RESULT: Direct is faster than proxy by {round(proxy_average - direct_average, args.decimals)}ms')
elif proxy_average < direct_average:
    print(f'  RESULT: Proxy is faster than direct by {round(direct_average - proxy_average, args.decimals)}ms')
elif proxy_average == direct_average:
    print(f'  RESULT: A miracle! Proxy and direct latency are EXACTLY the same at {proxy_average}ms')
print('=' * 50)