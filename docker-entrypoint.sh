#!/bin/bash

set -euo pipefail

if [ "$#" -eq 0 ] || [ "${1:0:1}" = '-' ]; then
    set -- python3 tts_client_python/tts_client.py "$@"
fi

exec "$@"
