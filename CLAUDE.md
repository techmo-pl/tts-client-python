# CLAUDE.md — tts-client-python

## Project Overview

Python gRPC client for Techmo's Text-to-Speech service. Provides a CLI (`tts_client`) and importable library for streaming/non-streaming speech synthesis, voice management, custom recordings, and pronunciation lexicons.

- **Package:** `tts_client_python`
- **Version:** tracked in `tts_client_python/VERSION.py`
- **Python support:** 3.8–3.14
- **gRPC API proto:** `submodules/tts-service-api/proto/techmo_tts.proto`

## Dev Environment Setup

```bash
./setup.sh          # one-time: init submodules + pre-commit hooks
./install.sh        # creates .venv and installs package with test deps (uv required)
source .venv/bin/activate
```

`setup.sh` — submodules + pre-commit only. `install.sh` — venv + pip only. Never mix these concerns.

System dependency: `sudo apt-get install libportaudio2` (needed by sounddevice; missing it produces a warning but tests still run — conftest handles the absence gracefully).

## Proto Stubs

Generated files (`tts_client_python/proto/*_pb2.py`, `*_pb2_grpc.py`) are **never committed**.
Generate manually: `python setup.py build_grpc`
They are regenerated automatically during `uv pip install -e ".[test]"`.

## Key Source Files

| File | Purpose |
|------|---------|
| `tts_client_python/tts_client.py` | CLI entry point, argument parsing |
| `tts_client_python/general.py` | Core gRPC client, audio player/saver, synthesis logic |
| `tts_client_python/recordings.py` | Custom recording CRUD via gRPC |
| `tts_client_python/lexicons.py` | Pronunciation lexicon CRUD via gRPC |
| `tts_client_python/wave_utils.py` | WAV/A-Law/Mu-Law file writing |
| `tts_client_python/VERSION.py` | Single source of version truth |

## Testing

```bash
pytest                          # unit tests only (default)
pytest -m integration           # requires TTS_SERVICE_ADDRESS=host:port
uvx --with "tox-uv>=1" tox     # full matrix (Python 3.8–3.14)
```

Integration tests are excluded by default (`pytest.ini`). They require a running TTS service at `TTS_SERVICE_ADDRESS`.

`conftest.py` mocks sounddevice only if importing it causes a SIGSEGV (signal-kill crash, e.g. headless PortAudio init). Python-level import errors are intentionally left to fail naturally so dependency problems remain visible.

## Dependency Constraints

Python 3.8 requires tighter bounds:
- `grpcio>=1.70.0,<1.71.0` (3.8) vs `grpcio>=1.70.0,<2.0` (3.9+)
- `protobuf>=5.29.0,<6.0` (3.8) vs `protobuf>=5.29.0` (3.9+)
- `grpcio-tools>=1.70.0,<1.71.0` in `pyproject.toml` (build dep)

Do not widen these bounds without verifying Python 3.8 compatibility.

## CI — GitHub Actions

`.github/workflows/test.yml` runs a matrix across Python 3.8–3.13 (required) and 3.14 (allowed failure). Each job:
1. Checks out with submodules
2. Installs `libportaudio2`
3. Installs `uv`
4. Generates proto stubs: `python setup.py build_grpc`
5. Runs tox

## Versioning

Bump the version in `tts_client_python/VERSION.py` only. This is read by `setup.py` at build time via `exec()`. The package `__init__.py` is empty — there is no `tts_client_python.__version__` attribute.

## Audio Encoding

Supported encodings: `PCM16`, `OGG_VORBIS`, `OGG_OPUS`, `A_LAW`, `MU_LAW`. Audio playback (sounddevice) supports PCM16 only. Other formats are save-to-file only.

## Commit Rules

- Never commit `*_pb2.py`, `*_pb2_grpc.py`, or any protoc-generated file.
- Never include `Co-Authored-By: Claude` in commit messages.
- Conventional commits: `feat:`, `fix:`, `chore:`, `ci:`, `docs:`, `test:`, `refactor:`.
