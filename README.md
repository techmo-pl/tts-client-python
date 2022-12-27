# Python implementation of Techmo TTS gRPC client.

The `tts-client-python` can be used on the docker (a dedicated script to handle the docker image: `docker/run_tts_client_python.sh` runs in the bash shell) or directly as a python application (requires configuring the virtual environment first). Details are described below.


## Docker usage

### Build docker image

To prepare a docker image with Python implementation of the TTS Client, open the project's main directory and run following command:

```
docker build -f Dockerfile -t techmo-tts-client-python:3.0.0 .
```
The build process will take several minutes.
When the build process is complete, you will receive a message:
```
Successfully tagged techmo-tts-client-python:3.0.0
```

### Run TTS Client

To use the TTS Client on a Docker container, go to the `tts-client-python/docker` directory and run `run_tts_client_python.sh` script.

To send a simple request to the TTS service, use:
```
./run_tts_client_python.sh --service-address=IP_ADDRESS:PORT --text="Sample text to be synthesised"
```

To print the list of available options, use:
```
./run_tts_client_python.sh --help
```
Output audio files will be created inside `tts-client-python/docker/wav` directory.
Source text files should be placed inside `tts-client-python/docker/txt` directory, if used.

**NOTE:** Unlike a local TTS Client instance, the `run_tts_client_python.sh` script doesn't allow to set custom paths to the input/output files. Instead it uses predefined directories (`wav` and `txt`). When using options: `--input-text-file (-i)` and `--output-file (-o)`, user should only provide filenames.



## Local instance usage

### Before run

#### Dependencies - Linux

Supported Python versions are: 3.6, 3.7, 3.8, 3.9.

Required Linux system-level packages:

- python3-dev
- python3-pip
- libportaudio2

To create the virtual environment and install other requirements, use script:

```
./setup.sh
```

Then activate virtual environment:
```
source .venv/bin/activate
```

#### Dependencies - Windows

Supported Python versions are: 3.6, 3.7, 3.8, 3.9.

To create virtual environment and install dependencies temporarily change the PowerShell's execution policy to allow scripting. Start the PowerShell with `Run as Administrator` and use command:

```
Set-ExecutionPolicy RemoteSigned
```
then confirm your choice.

Use Python 3 with virtual environment and install required packages (supported Python versions are: 3.6, 3.7, 3.8, 3.9):

```
python3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

To switch back PowerShell's execution policy to the default, use command:

```
Set-ExecutionPolicy Restricted
```

#### Proto sources

To build the sources from `.proto`, run:
```
./make_proto.sh
```


### Run

To run the TTS Client, activate the virtual environment first:
- On Linux:
```
source .venv/bin/activate
```
- On Windows:
```
.\.venv\Scripts\activate
```
Then run TTS Client. Sample use:

```
python tts_client.py -s "192.168.1.1:4321" -f 44100 -t "Some text to be synthesized"
```

For each request you have to provide the service address and the input text (directly as argument's value or from text file).


## Usage:
```
Basic usage: tts_client.py --service-address ADDRESS --text INPUT_TEXT
```

Available options:
```
  -h, --help            show this help message and exit
  -s IP:PORT, --service-address IP:PORT
                        An IP address and port (address:port) of a service the
                        client connects to.
  --session-id SESSION_ID
                        A session ID to be passed to the service. If not
                        specified, the service generates a default session ID.
  --grpc-timeout GRPC_TIMEOUT
                        A timeout in milliseconds used to set gRPC deadline -
                        how long the client is willing to wait for a reply
                        from the server (optional).
  --list-voices         Lists all available voices.
  -r RESPONSE_TYPE, --response RESPONSE_TYPE
                        "streaming" or "single", calls the streaming (default)
                        or non-streaming version of Synthesize.
  -t TEXT, --text TEXT  A text to be synthesized.
  -i INPUT_FILE, --input-text-file INPUT_FILE
                        A file with text to be synthesized.
  -o OUT_PATH, --out-path OUT_PATH
                        A path to the output wave file with synthesized audio
                        content.
  -f SAMPLE_RATE, --sample-rate SAMPLE_RATE
                        A sample rate in Hz of synthesized audio. Set to 0
                        (default) to use voice's original sample rate.
  --ae ENCODING, --audio-encoding ENCODING
                        An encoding of the output audio, pcm16 (default) or
                        ogg-vorbis.
  --sp SPEECH_PITCH, --speech-pitch SPEECH_PITCH
                        Allows adjusting the default pitch of the synthesized
                        speech (optional, can be overriden by SSML).
  --sr SPEECH_RANGE, --speech-range SPEECH_RANGE
                        Allows adjusting the default range of the synthesized
                        speech (optional, can be overriden by SSML).
  --ss SPEECH_RATE, --speech-rate SPEECH_RATE
                        Allows adjusting the default rate (speed) of the
                        synthesized speech (optional, can be overriden by
                        SSML).
  --sv SPEECH_VOLUME, --speech-volume SPEECH_VOLUME
                        Allows adjusting the default volume of the synthesized
                        speech (optional, can be overriden by SSML).
  --vn VOICE_NAME, --voice-name VOICE_NAME
                        A name od the voice used to synthesize the phrase
                        (optional, can be overriden by SSML).
  --vg VOICE_GENDER, --voice-gender VOICE_GENDER
                        A gender of the voice - female or male (optional, can
                        be overriden by SSML).
  --va VOICE_AGE, --voice-age VOICE_AGE
                        An age of the voice - adult, child, or senile
                        (optional, can be overriden by SSML).
  -l LANGUAGE, --language LANGUAGE
                        ISO 639-1 language code of the phrase to synthesize
                        (optional, can be overriden by SSML).
  --play                Play synthesized audio. Works only with pcm16
                        (default) encoding.
  --tls-dir TLS_DIR     If set to a path with SSL/TLS credential files
                        (client.crt, client.key, ca.crt), use SSL/TLS
                        authentication. Otherwise use insecure channel
                        (default).
  --list-lexicons       Lists all available lexicons.
  --get-lexicon LEXICON_NAME
                        Sends back the content of the lexicon with the
                        requested name.
  --delete-lexicon LEXICON_NAME
                        Removes the lexicon with the requested name.
  --put-lexicon LEXICON_NAME LEXICON_CONTENT
                        Adds a new lexicon with the requested name or
                        overwrites the existing one if there is already a
                        lexicon with such name. Content of the lexicon, shall
                        comply to https://www.w3.org/TR/pronunciation-
                        lexicon/.
  --put-recording VOICE_NAME RECORDING_KEY AUDIO_PATH
                        Adds a new recording with the requested key for the
                        requested voice, or overwrites the existing one if
                        there is already such a key defined. The recording has
                        to be PCM16 WAV audio.
  --delete-recording VOICE_NAME RECORDING_KEY
                        Removes the recording with the requested key from the
                        list of recordings of the requested voice.
  --get-recording VOICE_NAME RECORDING_KEY OUTPUT_PATH
                        Sends back the recording with the requested key for
                        the requested voice in the linear PCM16 format.
  --list-recordings VOICE_NAME
                        Lists all recording keys for the requested voice.
```
