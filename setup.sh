#!/bin/bash

set -euo pipefail

venv_dir=.venv

python3 -m venv "${venv_dir}"
source "${venv_dir}"/bin/activate
pip install -e .
