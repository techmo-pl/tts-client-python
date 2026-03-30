#!/bin/bash
# coding=utf-8

# This script sends request to TTS DNN Service using TTS Client inside the docker container
# Requires "ghcr.io/techmo-pl/tts-client-python:$IMAGE_VERSION" docker image.
# Build it locally first if not available: docker build -t ghcr.io/techmo-pl/tts-client-python:$IMAGE_VERSION .

set -euo pipefail
IFS=$'\n\t'

IMAGE_VERSION=3.2.11

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "${SCRIPT}")
docker_image="ghcr.io/techmo-pl/tts-client-python:${IMAGE_VERSION}"

docker run --rm -it -v "${SCRIPTPATH}/audio:/tts_client/audio" -v "${SCRIPTPATH}/txt:/tts_client/txt" -v "${SCRIPTPATH}/tls:/tts_client/tls" --network host \
    "${docker_image}" \
    --out-path "/tts_client/audio/output.wav" \
    "$@"
