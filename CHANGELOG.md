# Changelog

All notable changes to proxy-vs-direct will be documented here.

## [Unreleased]

## [0.5.1] - 2026-07-25

### Changed
- Average latency display: when all rounds fail, show descriptive text instead of `-1ms`
- Updated TODO.md

## [0.5.0] - 2026-07-23

> **⚠️ Breaking Changes**
> - `--animation` and `--color` changed from `{default,on,off}` choices to `[--animation | --no-animation]` / `[--color | --no-color]` boolean flags
> - `--quiet` changed to `[--quiet | --no-quiet]` toggle
> - `--overwrite-json` changed to `[--overwrite-json | --no-overwrite-json]` toggle
> - `-f / --force` removed (use `--output-mode overwrite` + `--overwrite-json` instead)

### Added
- TOML config file support (`config.toml` in platform config directory)
- 4-layer option loading system (default → auto → config → CLI)
- Output lazy buffer: stash messages before options are fully loaded, flush when ready
- `--encoding` option for output file encoding
- String-based option management via `_assign()` with `option_source` tracking
- `Contest` class: PK logic extracted from `DirectVsProxy`

### Changed
- `--animation` and `--color` changed from `{default,on,off}` choices to `[--animation | --no-animation]` / `[--color | --no-color]` boolean flags
- `--quiet` changed to `[--quiet | --no-quiet]` toggle
- `--overwrite-json` changed to `[--overwrite-json | --no-overwrite-json]` toggle
- `output.encoding` and `output.write_mode` now go through `set_attr()` for proper flush coordination
- `_positive_int`/`_positive_float` error messages preserve the original input value
- `ConfigLoader.get_config()` returns `{}` on read/parse errors with a warning instead of crashing

### Removed
- `-f / --force` flag (use `--output-mode overwrite` + `--overwrite-json` instead)
- Dead `_validate_option()` method in `ConfigLoader`
- Dead `url_scheme_undefined` global in `validate.py`
- Unused `Literal` import in `config.py`

### Fixed
- `ConfigLoader` opening config file with `'rb'` and passing `encoding` parameter (TypeError)
- `Output` stash/flush format: kwargs dictionary flattened into positional args
- `sys_http_proxy` being passed to `https_proxy` in auto-detection (copy-paste error)
- `option_source` lookup using `'http'` key instead of `'http_proxy'` (KeyError)
- `val` referenced before assignment when `father is None` in `ConfigLoader._assign_option`
- `--animation` flag missing `default=UNDEFINED`, allowing `None` from CLI to override lower layers
- `self.animation` (bool) compared to string `'on'`

## [0.4.4] - 2026-07-22

### Added
- `--animation` and `--color` flags to toggle animations and ANSI colors
- Auto-detection: animations/colors disabled for non-TTY environments

### Changed
- Color constants extracted to config
- Non-TTY behavior: info message when auto-disabled

## [0.4.3] - 2026-07-22

### Added
- ANSI color support for terminal output
- Box-drawing borders, bold headers, colored prefixes

### Changed
- PK result display prettified with alignment and color

## [0.4.2] - 2026-07-22

### Added
- `--quiet` mode to suppress terminal output
- `--output-file` to write output to a file
- `--output-mode` with `create`, `overwrite`, `append` modes
- `--encoding` option for file encoding

### Fixed
- Append mode truncating existing file on first write

## [0.4.1] - 2026-07-21

### Added
- URL auto-fill: auto-adds `https://` scheme if missing

## [0.4.0] - 2026-07-21

### Added
- `--rules` flag to show PK rules
- Config module with constants extracted from CLI
- Round-by-round PK with threading

### Changed
- `-c` flag renamed to `-r` for consistency

## [0.3.0] - 2026-07-20

### Added
- Custom HTTP/HTTPS proxy support via `--http-proxy` and `--https-proxy`

### Changed
- System proxy auto-detection as default

## [0.2.0] - 2026-07-20

### Added
- Custom User-Agent header support

### Changed
- Refactored to package structure (`src/`)
- Version tracking via `__init__.py`

## [0.1.0] - 2026-07-19

### Added
- Initial release: proxy vs direct latency comparison
- Basic CLI with URL and timeout arguments
- Single-round comparison
- MIT license
