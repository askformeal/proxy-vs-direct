# proxy-vs-direct

Compare the latency to a certain URL between proxy and direct connection.

## Usage

```bash
python main.py <url> [-c COUNT] [-t TIMEOUT] [-d DECIMALS]
```

### Arguments

- `url` — Target URL to test
- `-c, --count` — Number of requests to send (default: 5)
- `-t, --timeout` — Timeout in seconds (default: 5.0)
- `-d, --decimals` — Number of digits to round (default: 2)

### Example

```bash
python main.py https://www.google.com -c 10 -t 3
```

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## TODO

See [TODO.md](TODO.md) for planned features.
