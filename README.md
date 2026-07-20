# proxy-vs-direct

Compare the latency to a certain URL between proxy and direct connection.

## Usage

```bash
python -m src <url> [-c COUNT] [-t TIMEOUT] [-d DECIMALS] [--user-agent USER_AGENT]
```

### Arguments

- `url` — Target URL to test
- `-c, --count` — Number of requests to send (default: 5)
- `-t, --timeout` — Timeout in seconds (default: 5.0)
- `-d, --decimals` — Number of digits to round (default: 2)
- `--user-agent` — Custom User-Agent header (default: Chrome 137)
- `-v, --version` — Show version info

### Example

```bash
python -m src https://www.google.com -c 10 -t 3
python -m src https://www.google.com --user-agent "MyBot/1.0"
```

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## TODO

See [TODO.md](TODO.md) for planned features.
