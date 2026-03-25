#!/bin/bash
#
# usage: ./setup.sh
#
# Run once after cloning: initialises submodules and installs pre-commit hooks.

set -euo pipefail

git submodule sync --recursive
git submodule update --init --recursive

if [ ! -d pre-commit ]; then
    git clone --depth 1 --branch v3.0.0 https://github.com/techmo-pl/pre-commit.git
fi
./pre-commit/install.sh
