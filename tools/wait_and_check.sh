#!/usr/bin/env bash
# Wait for a fresh Pages deployment to answer, then run tools/check_live.py on it.
# Usage: tools/wait_and_check.sh <url> [--preview]
set -euo pipefail
url="$1"; shift
# A new project's first *.pages.dev certificate can take several minutes.
ready=""
for i in $(seq 1 60); do
  if curl -fsS -o /dev/null "$url/.well-known/assetlinks.json" 2>/dev/null; then ready=1; break; fi
  sleep 10
done
if [ -z "$ready" ]; then
  echo "::error::$url did not answer over HTTPS within 10 minutes"
  exit 1
fi
python tools/check_live.py "$url" "$@"
