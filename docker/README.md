# TTS Client on Docker

To use TTS Client docker version, `techmo-tts-client-python:IMAGE_VERSION` docker image has to be loaded locally.

To build the docker image, run the following command in the project root directory:
```
docker build -f Dockerfile -t techmo-tts-client-python:3.0.0 .
```
To send requests to the TTS DNN Service, use `run_tts_client_python.sh` script.


## Output file

The synthesized audio is saved inside the `wav` directory.
The default audio file name can be overwritten with the option: `--out-path "wav/custom_file_name"`, however the first part of the path should not be changed (the path is set inside the docker container's filesystem, and generated files can be obtained in the local filesystem only in specific directories mounted as docker volumes).


## Input text files

Input text files should be placed inside the `txt` directory. The input path should be set as: `"txt/FILE_NAME"`, e.g.: `--input-text-file "txt/input_file.txt"`

## TLS credencials

If TLS encryption is used, the credencials files should be placed inside `tls` directory, and an additional option: `--tls-dir "tls"` should be used.
