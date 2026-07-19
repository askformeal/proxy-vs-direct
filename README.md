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

## Requirements

- Python 3.7+
- `requests` library

Install dependencies:

```bash
pip install -r requirements.txt
```
