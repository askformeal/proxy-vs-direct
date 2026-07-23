# proxy-vs-direct

Compare the latency to a certain URL between proxy and direct connection.

## Usage

```bash
python -m src <url> [-r ROUND] [-t TIMEOUT] [-d DECIMALS] [--rules] [--user-agent USER_AGENT] [--http-proxy HTTP_PROXY] [--https-proxy HTTPS_PROXY] [--quiet] [--output-file PATH] [--output-mode MODE] [-f] [--animation {on,off}] [--color {on,off}]
```

### Arguments

- `url` — Target URL to test (auto-adds `https://` if scheme missing)
- `-r, --round` — Number of rounds to PK (default: 5)
- `-t, --timeout` — Timeout in seconds (default: 5.0). Note: this value is split between connect timeout and read timeout (each gets half), so the actual maximum wait time per request may be up to 2x the value you set.
- `-d, --decimals` — Number of digits to round (default: 2)
- `--rules` — Show PK rules
- `--user-agent` — Custom User-Agent header (default: Chrome 137)
- `--http-proxy` — HTTP proxy to use (default: system proxy)
- `--https-proxy` — HTTPS proxy to use (default: system proxy)
- `--quiet` — Suppress terminal output
- `--output-file PATH` — Write output to a file
- `--output-mode MODE` — File write mode (requires `--output-file`):
  - `create` (default) — Create a new file. Fail if file already exists.
  - `overwrite` — Overwrite existing file or create a new one.
  - `append` — Append to the end of an existing file, or create a new one.
- `-f, --force` — Force overwrite all files (sets mode to `overwrite` unless `--output-mode` is specified)
- `--animation` — Toggle real-time round status animation: `on` or `off` (auto-detected for TTY)
- `--color` — Toggle ANSI colors: `on` or `off` (auto-detected for TTY)
- `-v, --version` — Show version info

### Example

```bash
python -m src https://www.google.com -r 10 -t 3
python -m src google.com -r 5
python -m src https://www.google.com --http-proxy http://127.0.0.1:7897 --https-proxy http://127.0.0.1:7897
python -m src https://www.google.com --quiet --output-file result.txt
```

## Screenshots

### Help
```
usage: proxy-vs-direct [-r ROUND] [-d DECIMALS] [--rules] [-h] [-v]
                       [--user-agent USER_AGENT] [--http-proxy HTTP_PROXY]
                       [--https-proxy HTTPS_PROXY] [-t TIMEOUT] [--quiet]
                       [--animation {default,on,off}]
                       [--color {default,on,off}] [--output-file OUTPUT_FILE]
                       [--output-mode {default,create,overwrite,append}] [-f]
                       url

██████╗     ██╗   ██╗███████╗    ██████╗
██╔══██╗    ██║   ██║██╔════╝    ██╔══██╗
██████╔╝    ██║   ██║███████╗    ██║  ██║
██╔═══╝     ╚██╗ ██╔╝╚════██║    ██║  ██║
██║          ╚████╔╝ ███████║    ██████╔╝
╚═╝           ╚═══╝  ╚══════╝    ╚═════╝

Proxy vs Direct 0.4.5 - Make your proxy and direct connection PK on latency to a certain URL.

positional arguments:
  url                   Target URL.

options:
  -r ROUND, --round ROUND
                        Number of rounds to PK.
  -d DECIMALS, --decimals DECIMALS
                        Decimal precision.
  --rules               Show PK rules
  -h, --help            Show this help message and exit
  -v, --version         Show version info

Request:
  --user-agent USER_AGENT
                        User-Agent to use in request headers.
  --http-proxy HTTP_PROXY
                        HTTP proxy to use. Use system proxy by default.
  --https-proxy HTTPS_PROXY
                        HTTPS proxy to use. Use system proxy by default.
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds.

Output to Terminal:
  --quiet               Disable terminal outputs.
  --animation {default,on,off}
                        Toggle animations for better compatibility: [on/off]
  --color {default,on,off}
                        Toggle colors for better compatibility: [on/off]

Output to File:
  --output-file OUTPUT_FILE
                        A path of a file to write outputs into.
  --output-mode {default,create,overwrite,append}
                        Output to file modes: [create/overwrite/append]
  -f, --force           Force overwrite all files. Will set output mode to
                        "overwrite" unless manually specified with --output-
                        mode option.

Examples:
  python -m src https://example.com -r 10
  python -m src https://example.com --rules
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

## TODO

See [TODO.md](TODO.md) for planned features.
