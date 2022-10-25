#!/bin/bash
# coding=utf-8

# This script sends request to TTS DNN Service using TTS Client inside the docker container
# Requires "techmo-tts-client-python:$IMAGE_VERSION" docker image loaded locally

set -euo pipefail
IFS=$'\n\t'

IMAGE_VERSION=3.0.0

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "${SCRIPT}")
docker_image="techmo-tts-client-python:${IMAGE_VERSION}"

docker run --rm -it -v "${SCRIPTPATH}/wav:/tts_client/wav" -v "${SCRIPTPATH}/txt:/tts_client/txt" -v "${SCRIPTPATH}/tls:/tts_client/tls" --network host \
    "${docker_image}" \
    --out-path "wav/TechmoTTS.wav" \
    "$@"
