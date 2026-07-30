from src.output import output
from src.constants import BOLD, DIM, MIN_BAR_WIDTH, RED, GREEN, YELLOW, CYAN, WHITE, RESET
from src.constants import OPTIONS, SHOW_VALUE_MAX_LEN, BAR_COMPLETED, BAR_BLANK, BAR_PAD_WIDTH
import time

class Plot:
    def __init__(self):
        self.decimals = 0

    def show_source(self, sources: dict, values: dict):
        colors = {
            'default': DIM,
            'auto': YELLOW,
            'config': CYAN,
            'cli': GREEN,
        }

        labels = {
            'default': 'Default value',
            'auto': 'Automatic environment detection',
            'config': 'Configure file',
            'cli': 'Command-Line Interface argument', # because apparently "CLI arguments" is too short
        }

        max_value_len = 0
        if values is not None:
            for name in values.keys():
                values[name] = str(values[name])
                val = values[name]
                if len(val) > SHOW_VALUE_MAX_LEN:
                    values[name] = val[:SHOW_VALUE_MAX_LEN-3]+'...'
                    max_value_len = SHOW_VALUE_MAX_LEN
                elif len(val) > max_value_len:
                    max_value_len = len(val)

        max_name_len = 0
        for name in OPTIONS:
            if len(name) > max_name_len:
                max_name_len = len(name)

        width = 50
        output(f'{DIM}{"─" * width}{RESET}')
        output(f'{BOLD}{CYAN}  Option Info{RESET}')
        output(f'{DIM}{"─" * width}{RESET}')
        output()

        for name in OPTIONS:
            pad = ' ' * (max_name_len - len(name) + 2)
            info = f'{name}:{pad}'
            if values is not None:
                val = str(values[name])
                pad = ' ' * (max_value_len - len(val) + 2)
                info += f'{val}{pad}'

            if sources is not None:
                source = sources[name]
                color = colors[source]
                label = labels[source]
                info += f'{color}{label}{RESET}'

            info = info.strip()
            output(info)
        
        output()

    def show_pk_start(self, round, timeout):
        if timeout[0] == timeout[1]:
            timeout_phrase = f'{timeout[0]}s timeout'
        else:
            timeout_phrase = f'{timeout[0]}s connect timeout, {timeout[1]}s read timeout'
        title = f'PROXY vs DIRECT: {round} request(s) each, {timeout_phrase}'
        width = max(len(title) + 4, 50)
        output(f'{DIM}{"─" * width}{RESET}')
        output(f'{BOLD}{CYAN}  {title}{RESET}')
        output(f'{DIM}{"─" * width}{RESET}')
        output()

    def show_pk_result(self, results: dict):
        proxy_average = results['proxy_average']
        direct_average = results['direct_average']
        proxy_score = results['proxy_score']
        direct_score = results['direct_score']

        width = 50
        output(f'{DIM}{"─" * width}{RESET}')
        output(f'{BOLD}{CYAN}  PK Result {results["time"]}{RESET}')
        output(f'{DIM}{"─" * width}{RESET}')

        output(f'  {DIM}Rounds:{RESET}          [{results["completed"]}/{results["total"]}] completed')
        output(f'  {DIM}URL:{RESET}             {results["url"]}')
        output(f'  {DIM}HTTP Proxy:{RESET}      {results["http_proxy"]}')
        output(f'  {DIM}HTTPS Proxy:{RESET}     {results["https_proxy"]}')
        output(f'  {DIM}Connect Timeout:{RESET} {results["connect_timeout"]}s')
        output(f'  {DIM}Read Timeout:{RESET}    {results["read_timeout"]}s')
        output(f'  {DIM}Precision:{RESET}       {results["decimals"]} decimal place(s)')
        output(f'  {DIM}Duration:{RESET}        {results["duration"]}s')
        output()

        # Proxy stats
        colors = {-1: RED, 0: YELLOW, 1: GREEN}
        
        diff = proxy_score - direct_score
        proxy_color = colors[(diff>0) - (diff<0)] # True==1, False==0

        if proxy_average == -1:
            proxy_average = 'All rounds failed, average latency unavailable'
        else:
            proxy_average = f'{proxy_average}ms'

        output(f'  {proxy_color}{BOLD}Proxy{RESET}')
        output(f'    {DIM}Score:{RESET}    {proxy_color}{proxy_score}{RESET}')
        output(f'    {DIM}Failed:{RESET}   [{results["proxy_failed"]}/{results["completed"]}]')
        output(f'    {DIM}Average:{RESET}  {proxy_average}')
        output(f'    {DIM}Minimum:{RESET}  {results["proxy_min"]}')
        output(f'    {DIM}Maximum:{RESET}  {results["proxy_max"]}')
        output()

        # Direct stats
        diff = direct_score - proxy_score
        direct_color = colors[(diff>0) - (diff<0)] # True==1, False==0

        if direct_average == -1:
            direct_average = 'All rounds failed, average latency unavailable'
        else:
            direct_average = f'{direct_average}ms'

        output(f'  {direct_color}{BOLD}Direct{RESET}')
        output(f'    {DIM}Score:{RESET}    {direct_color}{direct_score}{RESET}')
        output(f'    {DIM}Failed:{RESET}   [{results["direct_failed"]}/{results["completed"]}]')
        output(f'    {DIM}Average:{RESET}  {direct_average}')
        output(f'    {DIM}Minimum:{RESET}  {results["direct_min"]}')
        output(f'    {DIM}Maximum:{RESET}  {results["direct_max"]}')
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

    def plot_round_result(self, round_status) -> dict:
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

    def print_round_info(self, round_status, skip_file=True, start_time=0):
        proxy_info = self._gen_round_info('Proxy', round_status['proxy'], start_time)
        direct_info = self._gen_round_info('Direct', round_status['direct'], start_time)
        output(f'  {proxy_info} | {direct_info}', skip_file=skip_file)

    def print_progress_bar(self, results, terminal_width):
        ratio = results['completed']/results['total']
        percent = f' {ratio*100:6.1f}%'

        bar_width = terminal_width - (BAR_PAD_WIDTH * 2) - len(percent)

        if bar_width >= MIN_BAR_WIDTH:
            completed_width = int(round(bar_width * ratio))
            blank_width = bar_width - completed_width

            completed = BAR_COMPLETED * completed_width
            blank = BAR_BLANK * blank_width

            pad = ' ' * BAR_PAD_WIDTH

            output(f'\n{pad}{GREEN}{completed}{WHITE}{blank}{RESET}{percent}{pad}')

            return True
        else:
            return False

    def _gen_round_info(self, name, status, start_time):
        if status is None:
            duration = round((time.time()-start_time) * 1000, self.decimals)
            return f'{name}: {DIM}{duration}ms{RESET}'
        else:
            if status['latency'] != -1:
                return f'{BOLD}{name}{RESET}: {status["latency"]}ms, {DIM}{status["msg"]}{RESET}'
            else:
                return f'{BOLD}{name}{RESET}: {RED}Failed{RESET}, {DIM}{status["msg"]}{RESET}'
