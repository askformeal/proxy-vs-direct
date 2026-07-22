# proxy-vs-direct

Compare the latency to a certain URL between proxy and direct connection.

## Usage

```bash
python -m src <url> [-r ROUND] [-t TIMEOUT] [-d DECIMALS] [--rules] [--user-agent USER_AGENT] [--http-proxy HTTP_PROXY] [--https-proxy HTTPS_PROXY] [--quiet] [--output-file PATH] [--output-mode MODE] [-f] [--animation {on,off}] [--color {on,off}]
```

### Arguments

- `url` — Target URL to test (auto-adds `https://` if scheme missing)
- `-r, --round` — Number of rounds to PK (default: 5)
- `-t, --timeout` — Timeout in seconds (default: 5.0)
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

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## TODO

See [TODO.md](TODO.md) for planned features.
