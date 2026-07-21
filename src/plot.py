class Plot:
    def __init__(self, decimals):
        self.decimals = decimals

    def _show_pk_result(self, results: dict):
        proxy_average = results['proxy_average']
        direct_average = results['direct_average']
        proxy_score = results['proxy_score']
        direct_score = results['direct_score']

        print(f'PK Result {results["time"]}:')

        print(f'  [{results["completed"]}/{results["total"]}] round(s) completed')
        print(f'  URL: {results["url"]}')
        print(f'  HTTP Proxy: {results["http_proxy"]}')
        print(f'  HTTPS Proxy: {results["https_proxy"]}')
        print(f'  Timeout: {results["timeout"]}s')
        print(f'  Decimal Precision: {results["decimals"]} decimal place(s)')
        print(f'  Duration: {results["duration"]}s')

        print('  Proxy:')
        print(f'    Score: {proxy_score}')
        print(f'    Failed: [{results["proxy_failed"]}/{results["completed"]}]')
        print(f'    Average Latency: {proxy_average}ms')
        
        print('  Direct:')
        print(f'    Score: {direct_score}')
        print(f'    Failed: [{results["direct_failed"]}/{results["completed"]}]')
        print(f'    Average Latency: {direct_average}ms')

        print('Overall:')
        if proxy_score > direct_score:
            print(f'  Proxy beat Direct {proxy_score}-{direct_score}', end='')
        elif direct_score > proxy_score:
            print(f'  Direct beat Proxy {direct_score}-{proxy_score}', end='')
        elif proxy_score == direct_score:
            print(f'  Proxy tied Direct {proxy_score}-{direct_score}', end='')
        print(f' with {results["tie_count"]} round(s) ended in ties.')

    def _plot_round_result(self, round_status) -> dict:
        proxy_latency = round_status['proxy']['latency']
        direct_latency = round_status['direct']['latency']
        round_result = {
            'msg': '',
            'proxy': 0,
            'direct': 0,
            'tie': 0
        }

        if proxy_latency == -1 and direct_latency == -1:
            round_result['msg'] = '  Both Failed! It\'s a Tie!'
            round_result['tie'] = 1
        
        elif proxy_latency == -1:
            round_result['msg'] = '  Proxy Failed!'
            round_result['direct'] = 1
        
        elif direct_latency == -1:
            round_result['msg'] = '  Direct Failed!'
            round_result['proxy'] = 1
        
        elif proxy_latency > direct_latency:
            lag = round(proxy_latency-direct_latency, self.decimals)
            round_result['msg'] = f'  Direct Won Proxy by {lag}ms!'
            round_result['direct'] = 1
        
        elif direct_latency > proxy_latency:
            lag = round(direct_latency-proxy_latency, self.decimals)
            round_result['msg'] = f'  Proxy Won Direct by {lag}ms!'
            round_result['proxy'] = 1
        
        elif proxy_latency == direct_latency:
            round_result['msg'] = f'  Miracle! Tie at {proxy_latency}ms! Take a screenshot!'
            round_result['tie'] = 1

        return round_result
    
    def _print_round_info(self, round_status):
        proxy_info = self._gen_round_info('Proxy', round_status['proxy'])
        direct_info = self._gen_round_info('Direct', round_status['direct'])
        print(f'  {proxy_info} | {direct_info}')

    def _gen_round_info(self, name, status):
        if status is None:
            return f'{name}: Waiting...'
        else:
            if status['latency'] != -1:
                return f"{name}: {status['latency']}ms, {status['msg']}"
            else:
                return f"{name}: Failed, {status['msg']}"