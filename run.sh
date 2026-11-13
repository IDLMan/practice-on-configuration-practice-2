#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3 -m src.main --config config/test.ini "$@"
