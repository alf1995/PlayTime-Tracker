#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v node >/dev/null || ! command -v npm >/dev/null; then
  echo 'Node.js and npm are required (on a development computer, not the Ally).' >&2
  exit 1
fi
npm ci
npm run build
python3 -m unittest discover -s tests -v
python3 scripts/build_zip.py
