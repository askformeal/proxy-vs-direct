# proxy-vs-direct

Compare the latency to a certain URL between proxy and direct connection.

## Usage

```bash
python -m src -h                                          # Global help
python -m src pk [url] -r 10 -t 3                         # Run PK (default subcommand)
python -m src config list                                 # List config file contents
python -m src <url>                                       # 'pk' is assumed when no subcommand
```

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--encoding ENCODING` | File encoding for output | `utf-8` |
| `--quiet, --no-quiet` | Suppress/allow terminal output | auto (TTY) |
| `--animation, --no-animation` | Toggle real-time round status animation | auto (TTY) |
| `--color, --no-color` | Toggle ANSI colors | auto (TTY) |
| `--output-file PATH` | Write output to a file | disabled |
| `--output-mode MODE` | File write mode: `create` / `overwrite` / `append` | `create` |

### PK Arguments (`pk` subcommand)

| Argument | Description | Default |
|----------|-------------|---------|
| `url` | Target URL to test (auto-adds `https://` if scheme missing) | required |
| `-r, --round` | Number of rounds to PK | 5 |
| `-t, --timeout` | Timeout in seconds (Note: split between connect and read timeout) | 5.0 |
| `-d, --decimals` | Number of digits to round | 2 |
| `--rules` | Show PK rules | — |
| `--user-agent` | Custom User-Agent header | Chrome 137 |
| `--http-proxy` | HTTP proxy to use | system proxy |
| `--https-proxy` | HTTPS proxy to use | system proxy |
| `-n, --notify, --no-notify` | Send/disable system notification on completion | off |
| `-j, --json PATH` | Write PK result to a JSON file | disabled |
| `--overwrite-json, --no-overwrite-json` | Overwrite/keep existing JSON file | off |
| `-v, --version` | Show version info | — |

### Config Subcommand

| Command | Description |
|---------|-------------|
| `python -m src config list` | List all options from the config file, grouped by TOML section |

Invalid values in the config file are reported separately with a description of why they failed validation.

### Examples

```bash
python -m src https://www.google.com -r 10 -t 3
python -m src google.com -r 5
python -m src https://www.google.com --http-proxy http://127.0.0.1:7897 --https-proxy http://127.0.0.1:7897
python -m src https://www.google.com --quiet --output-file result.txt
python -m src https://www.google.com -j result.json
python -m src config list
```

## Screenshots

### Help

Global help (`python -m src -h`):
```
usage: proxy-vs-direct [--encoding ENCODING] [--quiet | --no-quiet]
                       [--animation | --no-animation] [--color | --no-color]
                       [--output-file OUTPUT_FILE]
                       [--output-mode {default,create,overwrite,append}] [-h]
                       {pk,config} ...

██████╗     ██╗   ██╗███████╗    ██████╗
██╔══██╗    ██║   ██║██╔════╝    ██╔══██╗
██████╔╝    ██║   ██║███████╗    ██║  ██║
██╔═══╝     ╚██╗ ██╔╝╚════██║    ██║  ██║
██║          ╚████╔╝ ███████║    ██████╔╝
╚═╝           ╚═══╝  ╚══════╝    ╚═════╝

Proxy vs Direct 0.5.1 - Make your proxy and direct connection PK on latency to a certain URL.

positional arguments:
  {pk,config}
    pk                  Start Proxy vs Direct PK to a given URL. This
                        subcommand will be used if none is given
    config              Edit and examine configures

options:
  --encoding ENCODING   File encoding for output (default: utf-8)
  -h, --help            Show this help message and exit

Output to Terminal:
  --quiet, --no-quiet   Disable terminal outputs
  --animation, --no-animation
                        Toggle animations for better compatibility
  --color, --no-color   Toggle colors for better compatibility

Output to File:
  --output-file OUTPUT_FILE
                        A path of a file to write outputs into
  --output-mode {default,create,overwrite,append}
                        Output to file modes: [create/overwrite/append]
```

PK subcommand help (`python -m src pk -h`):
```
usage: proxy-vs-direct pk [-r ROUND] [-d DECIMALS] [--rules]
                          [-n | --notify | --no-notify] [-j JSON]
                          [--overwrite-json | --no-overwrite-json] [-h] [-v]
                          [--user-agent USER_AGENT] [--http-proxy HTTP_PROXY]
                          [--https-proxy HTTPS_PROXY] [-t TIMEOUT]
                          [url]

positional arguments:
  [url]                 Target URL.

options:
  -r, --round ROUND     Number of rounds to PK
  -d, --decimals DECIMALS
                        Decimal precision
  --rules               Show PK rules
  -n, --notify, --no-notify
                        Send system notify on completion
  -j, --json JSON       A path of a json file to write PK result into
  --overwrite-json, --no-overwrite-json
                        Overwrite existing json file
  -h, --help            Show this help message and exit
  -v, --version         Show version info

Request:
  --user-agent USER_AGENT
                        User-Agent to use in request headers
  --http-proxy HTTP_PROXY
                        HTTP proxy to use. Use system proxy by default
  --https-proxy HTTPS_PROXY
                        HTTPS proxy to use. Use system proxy by default
  -t, --timeout TIMEOUT
                        Timeout in seconds
```

Config subcommand help (`python -m src config -h`):
```
usage: proxy-vs-direct config [-h] {list} ...

positional arguments:
  {list}
    list      List all options in configure file

options:
  -h, --help  Show help message of config subcommand and exit
```

### PK Result
```
────────────────────────────────────────────────────
  PROXY vs DIRECT: 3 request(s) each, 3.0s timeout
────────────────────────────────────────────────────

Round [1/3] waiting...
  Proxy: 1737.93ms, Code 200 | Direct: Failed, Connection Timeout
  Direct Failed!
Round [2/3] waiting...
  Proxy: 1557.67ms, Code 200 | Direct: Failed, Connection Timeout
  Direct Failed!
Round [3/3] waiting...
  Proxy: 1440.61ms, Code 200 | Direct: Failed, Connection Timeout
  Direct Failed!

──────────────────────────────────────────────────
  PK Result 2026-07-23 13:48:16
──────────────────────────────────────────────────
  Rounds:     [3/3] completed
  URL:        https://www.google.com
  HTTP Proxy: http://127.0.0.1:7897
  HTTPS Proxy:http://127.0.0.1:7897
  Timeout:    3.0s
  Precision:  2 decimal place(s)
  Duration:   18.18s

  Proxy
    Score:   3
    Failed:  [0/3]
    Average: 1578.74ms

  Direct
    Score:   0
    Failed:  [3/3]
    Average: -1ms

──────────────────────────────────────────────────
  Proxy beat Direct 3-0 with 0 round(s) ended in ties.
──────────────────────────────────────────────────
```

### PK Rules
```
PK Rules:
  1. Each round, Proxy and Direct send one request to the same URL simultaneously.
  2. The side with lower latency wins the round. (-1 = Failed, counts as loss)
  3. If both fail, it is a tie.
  4. If latencies are exactly equal, it is a tie.
  5. Final score = rounds won. Higher score wins the PK.
```

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Config File

proxy-vs-direct supports a TOML config file at your platform's config directory (e.g. `~/.config/proxy-vs-direct/config.toml` on Linux, `%LOCALAPPDATA%/proxy-vs-direct/proxy-vs-direct/config.toml` on Windows).

Configuration priority (highest to lowest): CLI arguments > config file > auto-detection > hardcoded defaults.

Use `python -m src config list` to view the current config file contents. Invalid values are reported separately with a description of the failure.

A sample config file (`config.example.toml`) is included in the repository.

## TODO

See [TODO.md](TODO.md) for planned features.
