# Techmo TTS gRPC Python client Changelog

## [3.2.9] - 2026-03-30

### Changed

- Switch from local proto generation to the `tts-api` package dependency.
  No proto submodule and no `build_grpc` step required anymore — run `./install.sh` and you're ready.

### Fixed

- `install.sh`: false "libportaudio2 not found" warning no longer appears when the library
  is installed (switched from stale `ldconfig` cache check to `dpkg-query`).
- `README.md`: corrected several wrong CLI option names (`--input-path`, `--sampling-rate-hz`,
  `--language-code`) and added missing TLS options and `--max-frame-size` to the options table.
- `docker/run.sh`: updated bundled image version reference.


## [3.2.8] - 2026-03-25

### Fixed

- `tts_client_python/tts_client.py`: legal header corrected from "Techmo ASR Client" to "Techmo TTS Client".
- `README.md`: removed non-existent `-v` short flag from `--print-service-version` option table.
- `tests/conftest.py`: removed dead `asr_service_address` fixture (no test uses it).
- `pytest.ini`: removed dead `asr` marker and `not asr` from `addopts`.
- `tox.ini`: removed `ASR_*` from `passenv` (no ASR tests exist).


## [3.2.7] - 2026-03-23

### Added

- `install.sh`: check for `uv` before use and print install instructions.
- `install.sh`: check for uninitialised `tts-service-api` submodule at startup.
- `install.sh`: warn about missing `libportaudio2` after install completes.
- `README.md`: add `uv` to prerequisites with canonical install command.

### Fixed

- `setup.py`: proto generation now raises a clear `FileNotFoundError` when the
  submodule is absent instead of a bare path error.
- `tests/conftest.py`: print `libportaudio2` install hint to stderr at session
  start instead of relying on pytest's end-of-session warnings summary.
