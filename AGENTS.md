# AGENTS.md — tts-client-python

## Project Summary

Python gRPC client for Techmo TTS (Text-to-Speech) service. Provides a CLI tool (`tts_client`) and a Python library for speech synthesis, voice listing, custom recordings, and pronunciation lexicons. Communicates via gRPC using pre-built stubs from the `tts-api` package.

**Version:** `tts_client_python/VERSION.py`
**Python:** 3.8–3.14

## Repo Layout

```
tts_client_python/
  tts_client.py      # CLI entry point & arg parsing
  general.py         # gRPC client, audio player/saver, synthesis functions
  recordings.py      # custom recording CRUD
  lexicons.py        # pronunciation lexicon CRUD
  wave_utils.py      # WAV/A-Law/Mu-Law file writing; AudioFormat enum
  VERSION.py         # single version source
tests/
  conftest.py        # fixtures, sounddevice safety mock
  test_cli.py        # CLI arg validation
  test_channel.py    # gRPC channel creation
  test_helpers.py    # helper/validator functions
  test_wave_utils.py # WAV encoding
  test_integration.py # live service tests (excluded by default)
setup.py             # standard setuptools setup; tts-api in install_requires
pyproject.toml       # build backend (setuptools only, no grpcio-tools)
setup.sh             # one-time: pre-commit hooks only
install.sh           # venv creation + pip install (no proto generation)
```

## Proto Stubs

gRPC stubs are provided by the `tts-api` dependency — no local generation, no submodule.

```python
from techmo.tts.api.v3 import techmo_tts_pb2, techmo_tts_pb2_grpc
```

`tts-api` is pinned to a GitHub tag in `setup.py`:
```
tts-api @ git+https://github.com/techmo-pl/tts-api-python.git@v3.2.1
```
Update the tag in `setup.py` when a new `tts-api-python` release is tagged.

## Environment Setup

```bash
./setup.sh           # one-time: install pre-commit hooks
./install.sh         # create .venv, install package + test deps via uv
source .venv/bin/activate
sudo apt-get install libportaudio2   # required for sounddevice
```

`setup.sh` — pre-commit hooks only. `install.sh` — Python env only. Never mix concerns.

## Running Tests

```bash
pytest                        # unit tests (default, excludes integration)
pytest tests/test_helpers.py  # single file
pytest -m integration         # requires TTS_SERVICE_ADDRESS=host:port env var
uvx --with "tox-uv>=1" tox   # full Python 3.8–3.14 matrix
```

Integration tests require a live TTS service at `TTS_SERVICE_ADDRESS`. sounddevice is mocked at session start only if it causes a SIGSEGV.

## Key Conventions

- **Version:** only in `tts_client_python/VERSION.py`.
- **Dependency bounds:** Python 3.8 has a tighter grpcio constraint (`<1.71.0`); do not widen without verifying.
- **Audio playback:** only PCM16 is supported by `AudioPlayer`; other encodings write files only.
- **Commit messages:** conventional format (`feat:`, `fix:`, `chore:`, `ci:`, `test:`, `refactor:`); no Claude attribution.

## Architecture Notes

- `GrpcRequestConfig` (general.py) holds the gRPC channel, stub, timeout, and metadata. All API calls receive one.
- `create_channel()` builds insecure or TLS channels depending on CLI flags.
- `synthesize()` dispatches to `internal_synthesize()` (unary) or `internal_synthesize_streaming()` (server-streaming) based on the `response` argument.
- `AudioSaver` handles all file output formats; `AudioPlayer` streams PCM16 to PortAudio.
- `recordings.py` and `lexicons.py` are thin gRPC wrappers using the same `GrpcRequestConfig` pattern.
- `lxml` is a declared dependency but not currently imported — likely a leftover or reserved for future SSML validation.

## CI — GitHub Actions

`.github/workflows/test.yml`: Python 3.8–3.13 (required), 3.14 (allowed failure).
Each job: checkout → install libportaudio2 → install uv → tox (installs package including `tts-api`).
No submodule checkout. No proto generation step.

No `.gitlab-ci.yml` — CI runs only on GitHub Actions.

## Dependency Constraints

| Package | Python 3.8 | Python 3.9+ |
|---------|-----------|-------------|
| grpcio | `>=1.70.0,<1.71.0` | `>=1.70.0,<2.0` |
| tts-api | `@ git+https://github.com/techmo-pl/tts-api-python.git@v3.2.1` | same |
