#!/usr/bin/env bash
# Wait for a fresh Pages deployment to answer, then run tools/check_live.py on it.
# Usage: tools/wait_and_check.sh <url> [--preview]
set -euo pipefail
url="$1"; shift
for i in $(seq 1 30); do
  if curl -fsS -o /dev/null "$url/.well-known/assetlinks.json"; then break; fi
  sleep 5
done
python tools/check_live.py "$url" "$@"
