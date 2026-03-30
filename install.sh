#!/bin/bash
#
# usage: ./install.sh [VENV_PATH]
#
# VENV_PATH: Optional path for the virtual environment (default: ./.venv).
#
# Creates a virtualenv with uv and installs the package with test dependencies.

set -euo pipefail

if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is required but not installed." >&2
    echo "Install it with:  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    echo "After installing, open a new shell or run: source ~/.bashrc  (or ~/.zshrc)" >&2
    exit 1
fi

VENV_PATH="${1:-.venv}"

if [ ! -d "${VENV_PATH}" ]; then
    uv venv "${VENV_PATH}"
fi

# shellcheck disable=SC1091
source "${VENV_PATH}/bin/activate"
uv pip install -e ".[test]"

if ! ldconfig -p 2> /dev/null | grep -q 'libportaudio'; then
    echo "" >&2
    echo "Warning: libportaudio2 not found on this system." >&2
    echo "  Install it with: sudo apt-get install libportaudio2" >&2
    echo "  (Required for sounddevice; tests will fail without it.)" >&2
fi
