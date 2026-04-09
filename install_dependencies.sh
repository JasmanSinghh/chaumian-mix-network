#!/usr/bin/env bash
set -euo pipefail

# Create a local virtual environment if one does not already exist.
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

# Activate and install required packages.
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Dependencies installed in .venv"
echo "Activate with: source .venv/bin/activate"
