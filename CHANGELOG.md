# Techmo TTS gRPC Python client Changelog

## [3.2.8+1] - 2026-03-30

### Changed
- Replace local proto generation with `tts-api` package dependency (`git+https://github.com/techmo-pl/tts-api-python.git@v3.2.1`).
  No proto submodule, no `setup.py build_grpc` step required.
- All imports updated from `tts_client_python.proto` to `techmo.tts.api.v3`.
- `setup.py`: remove 5 custom build command classes; add `tts-api` to `install_requires`.
- `pyproject.toml`: remove `grpcio-tools` build dependency.
- `setup.sh`: remove submodule init (pre-commit hooks only).
- `install.sh`: remove proto sentinel check.
- `tox.ini`: switch to `skip_install=false`, `extras=test`; remove manual dep list.
- `.github/workflows/test.yml`: remove submodule checkout and `build_grpc` step.

### Added
- `AGENTS.md`: updated to reflect new architecture (no submodule, tts-api dependency).


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
