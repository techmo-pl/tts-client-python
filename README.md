# Python implementation of Techmo TTS gRPC client


* [TLDR](#tldr)
* [Docker usage](#docker-usage)
* [Local instance usage](#local-instance-usage)


## TLDR

### a) Docker

Simple synthesis:
```
./docker/run.sh --service-address SERVICE_HOST:SERVICE_PORT --text "Polski tekst do syntezy"
```
Output file:
```
file docker/audio/output.wav
```

### b) Local instance

```
./setup.sh
./install.sh
source .venv/bin/activate
```
Simple synthesis:
```
python3 tts_client_python/tts_client.py --service-address "SERVICE_HOST:SERVICE_PORT" --text "Polski tekst do syntezy"
```
For more examples, see the [Sample queries](#sample-queries) section.

Output file:
```
file output.wav
```


## Docker usage

The easiest way to run the application is to use a ready-made docker image. If the image is not available locally, you can build it manually.
To use the tts-client-python on a Docker container, open terminal in the tts-client-python/docker directory and launch `run.sh` script.

To send a simple request to the TTS service, execute the following command from the docker directory:
```
./run.sh --service-address=IP_ADDRESS:PORT --text="Sample text to be synthesised"
```
The generated audio file will appear in the `tts-client-python/docker/audio` directory.


To synthesize speech from a text file, place it in the `tts-client-python/docker/txt` directory and execute the command:
```
./run.sh --service-address=IP_ADDRESS:PORT --input-text-file /tts_client/txt/FILE_NAME.txt
```

To use an encrypted connection, place the tls certificates received from the service owner in the `tts-client-python/docker/tls` directory and execute the command:
```
./run.sh --service-address=IP_ADDRESS:PORT --text="Sample text to be synthesised" --tls-dir /tts_client/tls
```

To print a complete list of available options, use:
```
./run.sh --help
```

For more information on building and using the docker image, see `doc/dev-guide.md` file.


## Local instance usage

### Dependencies

- Python >=3.8
- `uv` Python package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Required Linux system-level packages:
    - python3-dev
    - python3-pip
    - libportaudio2

Other required dependencies will be installed automatically in the virtual environment.

#### Python version compatibility

| Python | Supported | Notes |
|--------|-----------|-------|
| 3.14   | ✅        | Tested (release candidate) |
| 3.13   | ✅        | |
| 3.12   | ✅        | |
| 3.11   | ✅        | |
| 3.10   | ✅        | |
| 3.9    | ✅        | |
| 3.8    | ✅        | Uses `grpcio<1.71.0` and `protobuf<6.0.0` (see below) |
| 3.7    | ❌        | Not supported (see below) |
| <3.7   | ❌        | Not supported |

**Python 3.8 — lower dependency bounds**

`grpcio 1.71.0` dropped Python 3.8 support, and `protobuf 6.x` requires Python 3.9+.
On Python 3.8 pip/uv will automatically select the compatible versions via PEP 508 environment
markers in `install_requires`:

| Package | Python 3.9+ | Python 3.8 |
|---------|-------------|------------|
| `grpcio` | `>=1.70.0,<2.0.0` | `>=1.70.0,<1.71.0` |
| `protobuf` | `>=5.29.0` | `>=5.29.0,<6.0.0` |

**Why Python 3.7 is not supported**

Three independent blockers make Python 3.7 support impractical:

1. **`grpcio`** — support dropped in `grpcio 1.63.0`; maximum usable version is `1.62.3`.
2. **`protobuf`** — `4.x` and `5.x` require Python 3.8+; maximum version available for
   Python 3.7 is `3.20.3`.
3. **Proto stubs** — the generated `*_pb2.py` files import
   `google.protobuf.runtime_version` (introduced in `protobuf 5.26.0`), which does not
   exist in `protobuf 3.20.3`. This causes an `ImportError` at startup and cannot be
   worked around without maintaining a separate set of legacy stubs generated with an
   entirely different protobuf code-generator (the old `_descriptor`-based API).

Python 3.7 also reached end-of-life in June 2023.

For more information on requirements and setup, see `doc/dev-guide.md` file.

### Setup

To install pre-commit hooks, run once after cloning:
```
./setup.sh
```

To create a virtual environment and install the package:
```
./install.sh
```

Before running the application, activate the virtual environment:
```
source .venv/bin/activate
```

### Run

To send a simple request to the TTS service, execute the command:
```
python3 tts_client_python/tts_client.py --service-address=IP_ADDRESS:PORT --text="Sample text to be synthesised"
```

**Available options:**

| Option                                                           | Description  |
|------------------------------------------------------------------|--------------|
|  -h, --help                                                      | Shows this help message and exits. |
|  --print-service-version                                         | Prints version string of the service.|
|  --print-resources-id                                            | Prints identification string of the resources used by the service.|
|  -s IP:PORT, --service-address IP:PORT                           | An IP address and port (address:port) of a service the client connects to.|
|  -t TEXT, --text TEXT                                            | A text to be synthesized. Each synthesis request must provide the input text using option `--text` (from the command line) or `--input-path` (from a text file).|
|  -i INPUT_FILE, --input-path INPUT_FILE                     | A file with text to be synthesized. Each synthesis request must provide the input text using option `--text` (from the command line) or `--input-path` (from a text file).|
|  -o OUT_PATH, --out-path OUT_PATH                                | A path to output audio file with synthesized speech content.|
|  -l LANGUAGE_CODE, --language-code LANGUAGE_CODE                 | Language ISO 639-1 code of the voice to be used (optional, can be overridden by SSML).|
|  -r RESPONSE_TYPE, --response RESPONSE_TYPE                      | Sets the type of response. Allowed values: "streaming" (default) or "single". According to the set response type, the streaming or non-streaming version of the Synthesize call is used.|
|  --tls-dir TLS_DIR                                               | If set to a path to the directory containing SSL/TLS files (client.crt, client.key, ca.crt), uses SSL/TLS authentication (required for both one-way and mutual authentication). If not set, uses insecure connection.|
|  --play                                                          | Plays synthesized audio. Works only with pcm16 (default) encoding.|
|  --session-id SESSION_ID                                         | A session ID to be passed to the service. If not specified, the service generates a default session ID based on the timestamp of the request (in the form of: 'YYYYMMDD-hhmmss-xxx', where 'xxx' is the counter of sessions handled during the indicated second).|
|  --grpc-timeout GRPC_TIMEOUT                                     | A timeout in milliseconds used to set gRPC deadline - how long the client is willing to wait for a reply from the server (optional).|
|  --sampling-rate SAMPLING_RATE                                   | A sampling rate in Hz of synthesized audio. Set to 0 (default) to use voice's native sampling rate.|
|  --ae ENCODING, --audio-encoding ENCODING                        | An encoding of the output audio, pcm16 (default), ogg-vorbis, ogg-opus, a-law, or mu-law.|
|  --speech-pitch SPEECH_PITCH                                     | Allows adjusting the default pitch of the synthesized speech (optional, can be overridden by SSML).|
|  --speech-range SPEECH_RANGE                                     | Allows adjusting the default range of the synthesized speech (optional, can be overridden by SSML).|
|  --speech-rate SPEECH_RATE                                       | Allows adjusting the default rate (speed) of the synthesized speech (optional, can be overridden by SSML).|
|  --speech-stress SPEECH_STRESS                                   | Allows adjusting the default stress of the synthesized speech (optional, can be overridden by SSML).|
|  --speech-volume SPEECH_VOLUME                                   | Allows adjusting the default volume of the synthesized speech (optional, can be overridden by SSML).|
|  --list-voices                                                   | Lists all available voices.|
|  --vn VOICE_NAME, --voice-name VOICE_NAME                        | A name of the voice to be used (optional, can be overridden by SSML).|
|  --vg VOICE_GENDER, --voice-gender VOICE_GENDER                  | A gender of the voice to be used. Allowed values: 'female', 'male' (optional, can be overridden by SSML).|
|  --va VOICE_AGE, --voice-age VOICE_AGE                           | An age of the voice to be used. Allowed values: 'adult', 'child', 'senile' (optional, can be overridden by SSML).|
|  --voice-variant VOICE_VARIANT                                   | A variant of the selected voice - positive integer (optional, can be overridden by SSML). Default value is 1.|
|  --list-sound-icons                                              | Lists all available sound icons for the requested voice. This request requires also arguments: --voice-name and --language, and may optionally specify --voice-variant (if not specified, the default variant (1) is used).|
|  --list-recordings                                               | Lists all available recordings for the requested voice. This request requires also arguments: --voice-name and --language, and may optionally specify --voice-variant (if not specified, the default variant (1) is used).|
|  --get-recording RECORDING_KEY OUTPUT_PATH                       | Sends back the recording with the requested key for the requested voice in the linear PCM16 format. This request requires also arguments: --voice-name and --language, and may optionally specify --voice-variant (if not specified, the default variant (1) is used).|
|  --put-recording RECORDING_KEY AUDIO_PATH                        | Adds a new recording with the requested key for the requested voice, or overwrites the existing one if there is already such a key defined. The recording has to be PCM16 WAV audio. This request requires also arguments: --voice-name and --language, and may optionally specify --voice-variant (if not specified, the default variant (1) is used).|
|  --delete-recording RECORDING_KEY                                | Removes the recording with the requested key from the list of recordings of the requested voice. This request requires also arguments: --voice-name and --language, and may optionally specify --voice-variant (if not specified, the default variant (1) is used).|
|  --list-lexicons                                                 | Lists all available pronunciation lexicons.|
|  --get-lexicon LEXICON_URI OUTPUT_PATH                           | Saves content of the lexicon from the service-wide list of lexicon.|
|  --put-lexicon LEXICON_URI LEXICON_PATH OUTSIDE_LOOKUP_BEHAVIOUR | Adds lexicon to the service-wide list of lexicons. LEXICON_URI - a custom string identifying a given lexicon at the service level. LEXICON_PATH - path to the lexicon file. OUTSIDE_LOOKUP_BEHAVIOUR - determines whether the service can use the lexicon automatically, without using the SSML <lookup> tag. Must take one of two values: 'allowed' or 'disallowed'.|
|  --delete-lexicon LEXICON_URI                                    | Deletes lexicon from the service-wide list of lexicon.|


#### Sample queries

Simple synthesis:
```
python3 tts_client_python/tts_client.py --service-address "SERVICE_HOST:SERVICE_PORT" --text 'Polski tekst do syntezy'
```

Simple synthesis with language selection:
```
python3 tts_client_python/tts_client.py --service-address "SERVICE_HOST:SERVICE_PORT"  --text 'Die Sprache der Synthese muss definiert werden.' --language-code "de"
```

SSML - simple prosody manipulation:
```
python3 tts_client_python/tts_client.py --service-address "SERVICE_HOST:SERVICE_PORT" --text '<speak><prosody rate="slow">Mówię powoli i <break time="150ms"/> z krótkimi <break time="200ms"/> przerwami.</prosody></speak>'
```

SSML - interpretation control (`<say-as>`):
```
python3 tts_client_python/tts_client.py --service-address "SERVICE_HOST:SERVICE_PORT" --text '<speak> Twój numer to: <say-as interpret-as="characters"> AWS123 </say-as></speak>'
```

SSML - use of `format`:
```
python3 tts_client_python/tts_client.py --service-address "SERVICE_HOST:SERVICE_PORT" --text '<speak> Jest już <say-as interpret-as="time" format="12h"> 16:45 </say-as></speak>'
```

SSML - use of `detail`:
```
python3 tts_client_python/tts_client.py --service-address "SERVICE_HOST:SERVICE_PORT" --text '<speak> Ali Baba i <say-as interpret-as="cardinal" detail="acc:m1"> 40 </say-as>rozbójników</speak>'
```

### Running tests locally

Proto stubs are provided by the `tts-api` dependency and installed automatically.
Run the following once after cloning, then activate the venv and run tests:

```bash
./setup.sh
./install.sh
source .venv/bin/activate
pytest
```

> **Note on scripts:** `setup.sh` is a one-time bootstrapper (pre-commit hooks).
> `install.sh [VENV_PATH]` creates the virtualenv and installs the package —
> run it separately after `setup.sh`, or re-run it whenever you need to refresh
> the Python environment.

> **Multi-version testing** (optional): to run the full matrix across Python
> 3.8–3.14 (mirrors CI), run `uvx --with "tox-uv>=1" tox` instead of `pytest`
> after the setup script above.

### Integration tests (require a live TTS service)

Integration tests connect to a real TTS service and verify end-to-end audio synthesis.
They are excluded from the default `pytest` run and must be enabled explicitly via environment variables.

| Variable | Required | Description |
|---|---|---|
| `TTS_SERVICE_ADDRESS` | Yes | `host:port` of a live TTS service |
| `TTS_VOICE_NAME` | No | Voice name to use (uses service default if unset) |
| `TTS_LANGUAGE_CODE` | No | ISO 639-1 language code (uses service default if unset) |

Run integration tests locally:

```bash
TTS_SERVICE_ADDRESS=host:port pytest -m integration
```

With an explicit voice:

```bash
TTS_SERVICE_ADDRESS=host:port TTS_VOICE_NAME=masza TTS_LANGUAGE_CODE=pl pytest -m integration
```

Via tox (tests the active Python version):

```bash
TTS_SERVICE_ADDRESS=host:port uvx --with "tox-uv>=1" tox -e py312 -- -m integration
```

In CI, set `TTS_SERVICE_ADDRESS` (and optionally `TTS_VOICE_NAME`, `TTS_LANGUAGE_CODE`) as
repository secrets/variables. The integration test job activates automatically when
`TTS_SERVICE_ADDRESS` is defined.
