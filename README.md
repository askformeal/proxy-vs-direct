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
| `--quiet, --no-quiet` | Enable/disable terminal output | auto (TTY) |
| `--animation, --no-animation` | Enable/disable real-time round status animation | auto (TTY) |
| `--color, --no-color` | Enable/disable ANSI colors | auto (TTY) |
| `--show-source, --no-show-source` | Show from which source each option is loaded | off |
| `--show-value, --no-show-value` | Show the value of each option | off |
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
| `python -m src config list` | List options from config file, grouped by TOML section |
| `python -m src config show <option>` | Show value of a specific option |
| `python -m src config set <option> <value>` | Set an option's value in config file |
| `python -m src config unset <option>` | Delete an option from config file |
| `python -m src config where` | Show the path of the config file |
| `python -m src config open` | Open config file with system default app |
| `python -m src config clean` | Remove invalid and undefined options |
| `python -m src config create` | Create an empty config file |
| `python -m src config purge` | Delete the config file |

Invalid values in the config file are reported separately with a description of why they failed validation.

### Examples

```bash
python -m src https://www.google.com -r 10 -t 3
python -m src google.com -r 5
python -m src https://www.google.com --http-proxy http://127.0.0.1:7897 --https-proxy http://127.0.0.1:7897
python -m src https://www.google.com --quiet --output-file result.txt
python -m src https://www.google.com -j result.json
python -m src config list
python -m src config show round
python -m src config set round 15
python -m src config where
```

## Screenshots

### Help

Global help (`python -m src -h`):
```
usage: proxy-vs-direct [--encoding ENCODING] [--quiet | --no-quiet]
                       [--animation | --no-animation] [--color | --no-color]
                       [--show-source | --no-show-source]
                       [--show-value | --no-show-value]
                       [--output-file OUTPUT_FILE]
                       [--output-mode {default,create,overwrite,append}]
                       {pk,config} ...

Proxy vs Direct 0.6.0 - Make your proxy and direct connection PK on latency to a certain URL.

positional arguments:
  {pk,config}
    pk         Start Proxy vs Direct PK to a given URL. This subcommand will
               be used if none is given
    config     Edit and examine configure file

options:
  --encoding ENCODING   File encoding for output (default: utf-8)

Output to Terminal:
  --quiet, --no-quiet   Enable/disable terminal outputs
  --animation, --no-animation
                        Enable/disable animations for better compatibility
  --color, --no-color   Enable/disable colors for better compatibility
  --show-source, --no-show-source
                        Show from which source each option is loaded
  --show-value, --no-show-value
                        Show the value of each option

Output to File:
  --output-file OUTPUT_FILE
                        A path of a file to write outputs into
  --output-mode {default,create,overwrite,append}
                        Output to file modes: [create/overwrite/append]

GitHub Repository:
  https://github.com/askformeal/proxy-vs-direct

If you encounter a problem or want to give a suggestion, please send a feedback by:
  Create an issue at https://github.com/askformeal/proxy-vs-direct/issues
  Send an E-Mail to muzhi1014@outlook.com

Examples:
  python -m src https://example.com -r 10
  python -m src https://example.com --rules
```

PK subcommand help (`python -m src pk -h`):
```
usage: proxy-vs-direct pk [--encoding ENCODING] [--quiet | --no-quiet]
                          [--animation | --no-animation]
                          [--color | --no-color]
                          [--show-source | --no-show-source]
                          [--show-value | --no-show-value]
                          [--output-file OUTPUT_FILE]
                          [--output-mode {default,create,overwrite,append}]
                          [-r ROUND] [-d DECIMALS] [--rules]
                          [-n | --notify | --no-notify] [-j JSON]
                          [--overwrite-json | --no-overwrite-json] [-h] [-v]
                          [--user-agent USER_AGENT] [--http-proxy HTTP_PROXY]
                          [--https-proxy HTTPS_PROXY] [-t TIMEOUT]
                          [url]

Start Proxy vs Direct PK to a given URL. This subcommand will be used if none
is given

positional arguments:
  [url]                 Target URL.

options:
  --encoding ENCODING   File encoding for output (default: utf-8)
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

Output to Terminal:
  --quiet, --no-quiet   Enable/disable terminal outputs
  --animation, --no-animation
                        Enable/disable animations for better compatibility
  --color, --no-color   Enable/disable colors for better compatibility
  --show-source, --no-show-source
                        Show from which source each option is loaded
  --show-value, --no-show-value
                        Show the value of each option

Output to File:
  --output-file OUTPUT_FILE
                        A path of a file to write outputs into
  --output-mode {default,create,overwrite,append}
                        Output to file modes: [create/overwrite/append]

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
Here's the config help (`python -m src config -h`):

```
usage: proxy-vs-direct config [--encoding ENCODING] [--quiet | --no-quiet]
                              [--animation | --no-animation]
                              [--color | --no-color]
                              [--show-source | --no-show-source]
                              [--show-value | --no-show-value]
                              [--output-file OUTPUT_FILE]
                              [--output-mode {default,create,overwrite,append}]
                              [-h]
                              {list,show,where,open,set,unset,clean,create,purge} ...

Edit and examine configure file

positional arguments:
  {list,show,where,open,set,unset,clean,create,purge}
    list                List all options in configure file
    show                Show the value of a given option in configure file
    where               Show the path of configure file
    open                Open configure file with the default application of
                        the current system
    set                 Set the value of a given option in configure file
    unset               Delete a given option in configure file
    clean               Clean configure file by deleting all invalid or
                        undefined options
    create              Create an empty configure file if none exists
    purge               Delete configure file

options:
  --encoding ENCODING   File encoding for output (default: utf-8)
  -h, --help            Show the help message of config subcommand and exit

Output to Terminal:
  --quiet, --no-quiet   Enable/disable terminal outputs
  --animation, --no-animation
                        Enable/disable animations for better compatibility
  --color, --no-color   Enable/disable colors for better compatibility
  --show-source, --no-show-source
                        Show from which source each option is loaded
  --show-value, --no-show-value
                        Show the value of each option

Output to File:
  --output-file OUTPUT_FILE
                        A path of a file to write outputs into
  --output-mode {default,create,overwrite,append}
                        Output to file modes: [create/overwrite/append]
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

Use `python -m src config list` to view the current config, `config set <option> <value>` to modify it, and `config where` to find the file. Use `config clean` to remove invalid or undefined entries, `config create` to bootstrap an empty config, and `config purge` to delete it entirely.

A sample config file (`config.example.toml`) is included in the repository.

## TODO

See [TODO.md](TODO.md) for planned features.
