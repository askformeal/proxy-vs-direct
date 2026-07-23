from src.output import output
from src.config import BOLD, DIM, RED, GREEN, YELLOW, CYAN, RESET
import time

class Plot:
    def __init__(self, decimals):
        self.decimals = decimals

    def _show_pk_result(self, results: dict):
        proxy_average = results['proxy_average']
        direct_average = results['direct_average']
        proxy_score = results['proxy_score']
        direct_score = results['direct_score']

        width = 50
        output(f'{DIM}{"─" * width}{RESET}')
        output(f'{BOLD}{CYAN}  PK Result {results["time"]}{RESET}')
        output(f'{DIM}{"─" * width}{RESET}')

        output(f'  {DIM}Rounds:{RESET}     [{results["completed"]}/{results["total"]}] completed')
        output(f'  {DIM}URL:{RESET}        {results["url"]}')
        output(f'  {DIM}HTTP Proxy:{RESET} {results["http_proxy"]}')
        output(f'  {DIM}HTTPS Proxy:{RESET}{results["https_proxy"]}')
        output(f'  {DIM}Timeout:{RESET}    {results["timeout"]}s')
        output(f'  {DIM}Precision:{RESET}  {results["decimals"]} decimal place(s)')
        output(f'  {DIM}Duration:{RESET}   {results["duration"]}s')
        output()

        # Proxy stats
        colors = {-1: RED, 0: YELLOW, 1: GREEN}
        
        diff = proxy_score - direct_score
        proxy_color = colors[(diff>0) - (diff<0)] # True==1, False==0
        output(f'  {proxy_color}{BOLD}Proxy{RESET}')
        output(f'    {DIM}Score:{RESET}   {proxy_color}{proxy_score}{RESET}')
        output(f'    {DIM}Failed:{RESET}  [{results["proxy_failed"]}/{results["completed"]}]')
        output(f'    {DIM}Average:{RESET} {proxy_average}ms')
        output()

        # Direct stats
        diff = direct_score - proxy_score
        direct_color = colors[(diff>0) - (diff<0)] # True==1, False==0
        output(f'  {direct_color}{BOLD}Direct{RESET}')
        output(f'    {DIM}Score:{RESET}   {direct_color}{direct_score}{RESET}')
        output(f'    {DIM}Failed:{RESET}  [{results["direct_failed"]}/{results["completed"]}]')
        output(f'    {DIM}Average:{RESET} {direct_average}ms')
        output()

        # Overall
        output(f'{DIM}{"─" * width}{RESET}')
        if proxy_score > direct_score:
            output(f'  {GREEN}{BOLD}Proxy beat Direct {proxy_score}-{direct_score}{RESET}', end='')
        elif direct_score > proxy_score:
            output(f'  {GREEN}{BOLD}Direct beat Proxy {direct_score}-{proxy_score}{RESET}', end='')
        elif proxy_score == direct_score:
            output(f'  {YELLOW}{BOLD}Proxy tied Direct {proxy_score}-{direct_score}{RESET}', end='')
        output(f' with {results["tie_count"]} round(s) ended in ties.')
        output(f'{DIM}{"─" * width}{RESET}')

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
            round_result['msg'] = f'  {YELLOW}Both Failed! It\'s a Tie!{RESET}'
            round_result['tie'] = 1

        elif proxy_latency == -1:
            round_result['msg'] = f'  {RED}Proxy Failed!{RESET}'
            round_result['direct'] = 1

        elif direct_latency == -1:
            round_result['msg'] = f'  {GREEN}Direct Failed!{RESET}'
            round_result['proxy'] = 1

        elif proxy_latency > direct_latency:
            lag = round(proxy_latency - direct_latency, self.decimals)
            round_result['msg'] = f'  {GREEN}Direct Won by {lag}ms!{RESET}'
            round_result['direct'] = 1

        elif direct_latency > proxy_latency:
            lag = round(direct_latency - proxy_latency, self.decimals)
            round_result['msg'] = f'  {GREEN}Proxy Won by {lag}ms!{RESET}'
            round_result['proxy'] = 1

        elif proxy_latency == direct_latency:
            round_result['msg'] = f'  {YELLOW}Miracle! Tie at {proxy_latency}ms! Take a screenshot!{RESET}'
            round_result['tie'] = 1

        return round_result

    def _print_round_info(self, round_status, skip_file=True, start_time=0):
        proxy_info = self._gen_round_info('Proxy', round_status['proxy'], start_time)
        direct_info = self._gen_round_info('Direct', round_status['direct'], start_time)
        output(f'  {proxy_info} | {direct_info}', skip_file=skip_file)

    def _gen_round_info(self, name, status, start_time):
        if status is None:
            duration = round((time.time()-start_time) * 1000, self.decimals)
            return f'{name}: {DIM}{duration}ms{RESET}'
        else:
            if status['latency'] != -1:
                return f'{BOLD}{name}{RESET}: {status["latency"]}ms, {DIM}{status["msg"]}{RESET}'
            else:
                return f'{BOLD}{name}{RESET}: {RED}Failed{RESET}, {DIM}{status["msg"]}{RESET}'
