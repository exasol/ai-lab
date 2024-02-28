#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

curl -sSL  https://install.python-poetry.org/ | python3.10 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bash_profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.poetry_path
