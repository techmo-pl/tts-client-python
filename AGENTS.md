# AGENTS.md — tts-client-python

## Project Summary

Python gRPC client for Techmo TTS (Text-to-Speech) service. Provides a CLI tool (`tts_client`) and a Python library for speech synthesis, voice listing, custom recordings, and pronunciation lexicons. Communicates via gRPC using protobuf definitions from the `submodules/tts-service-api` submodule.

**Version:** `tts_client_python/VERSION.py`
**Python:** 3.8–3.14

## Repo Layout

```
tts_client_python/   # main package
  tts_client.py      # CLI entry point & arg parsing
  general.py         # gRPC client, audio player/saver, synthesis functions
  recordings.py      # custom recording CRUD
  lexicons.py        # pronunciation lexicon CRUD
  wave_utils.py      # WAV/A-Law/Mu-Law file writing; AudioFormat enum
  VERSION.py         # single version source
  proto/             # generated — never in git
tests/               # pytest test suite
  conftest.py        # fixtures, sounddevice safety mock
  test_cli.py        # CLI arg validation
  test_channel.py    # gRPC channel creation
  test_helpers.py    # helper/validator functions
  test_wave_utils.py # WAV encoding
  test_integration.py # live service tests (excluded by default)
submodules/
  tts-service-api/   # proto definitions (git submodule)
setup.py             # custom build commands: build_grpc, build_py, develop, install
pyproject.toml       # build backend; grpcio-tools constraint
setup.sh             # one-time: submodules + pre-commit hooks
install.sh           # venv creation + pip install
```

## Environment Setup

```bash
./setup.sh           # init submodules + pre-commit (run once after clone)
./install.sh         # create .venv, install package + test deps via uv
source .venv/bin/activate
sudo apt-get install libportaudio2   # required for sounddevice
```

**Never mix `setup.sh` and `install.sh` concerns.** `setup.sh` = git/hooks only. `install.sh` = Python env only.

## Generating Proto Stubs

Proto stubs are never committed. Regenerate with:
```bash
python setup.py build_grpc
```
This is also triggered automatically by `uv pip install -e ".[test]"`.

Generated files: `tts_client_python/proto/techmo_tts_pb2.py`, `techmo_tts_pb2_grpc.py`

## Running Tests

```bash
pytest                        # unit tests (default, excludes integration)
pytest tests/test_helpers.py  # single file
pytest -m integration         # requires TTS_SERVICE_ADDRESS=host:port env var
uvx --with "tox-uv>=1" tox   # full Python 3.8–3.14 matrix
```

Unit tests do not mock gRPC calls — `test_helpers.py` imports proto stubs directly, so generated stubs must exist before running tests. Only `test_channel.py` uses mocking (for the gRPC channel). sounddevice is mocked at session start only if it causes a SIGSEGV. Integration tests require a live TTS service.

## Key Conventions

- **Proto files**: `*_pb2.py`, `*_pb2_grpc.py` — never commit, always generate.
- **Version**: only in `tts_client_python/VERSION.py`.
- **Dependency bounds**: Python 3.8 has tighter grpcio/protobuf constraints; do not widen without verifying.
- **Audio playback**: only PCM16 is supported by `AudioPlayer`; other encodings write files only.
- **Commit messages**: conventional format (`feat:`, `fix:`, `chore:`, `ci:`, `test:`, `refactor:`); no Claude attribution.

## Architecture Notes

- `GrpcRequestConfig` (general.py) holds the gRPC channel, stub, timeout, and metadata. All API calls receive one.
- `create_channel()` builds insecure or TLS channels depending on CLI flags.
- `synthesize()` is the high-level public function — creates the channel/stub/request, then dispatches to `internal_synthesize()` (unary gRPC call) or `internal_synthesize_streaming()` (streaming gRPC call) based on the `response` argument.
- `AudioSaver` handles all file output formats; `AudioPlayer` streams PCM16 to PortAudio.
- `recordings.py` and `lexicons.py` are thin gRPC wrappers using the same `GrpcRequestConfig` pattern.
- `lxml` is listed as a dependency in `setup.py` but is not currently imported in the codebase — it may be a leftover or intended for future SSML validation.

## CI/CD

GitHub Actions (`.github/workflows/test.yml`):
- Matrix: Python 3.8–3.13 (required pass), 3.14 RC (allowed failure)
- Steps per job: checkout with submodules → install libportaudio2 → install uv → generate protos → tox
- Integration tests activate automatically if `TTS_SERVICE_ADDRESS` secret is set in the repo.

No `.gitlab-ci.yml` exists in this repo — CI runs only on GitHub Actions.

## Dependency Constraints

| Package | Python 3.8 | Python 3.9+ |
|---------|-----------|-------------|
| grpcio | `>=1.70.0,<1.71.0` | `>=1.70.0,<2.0` |
| protobuf | `>=5.29.0,<6.0` | `>=5.29.0` |
| grpcio-tools (build) | `>=1.70.0,<1.71.0` | same |
