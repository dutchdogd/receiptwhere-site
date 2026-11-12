#!/usr/bin/env bash
# Deploy dist/ to Cloudflare Pages. CI only: needs CLOUDFLARE_API_TOKEN and
# CLOUDFLARE_ACCOUNT_ID in the environment (GitHub Actions secrets; never in the repo).
# Usage: tools/pages_deploy.sh <branch> <commit-sha>
# Branch "main" is the Pages production branch; any other branch is a preview.
# Writes url= (this deployment) and alias= (branch alias) to $GITHUB_OUTPUT.
set -euo pipefail

branch="$1"
sha="$2"
project="${PAGES_PROJECT:?}"

# Create the Pages project on first use (Direct Upload, production branch main).
if ! npx wrangler pages project list | grep -qE "(^|[[:space:]│|])${project}([[:space:]│|]|$)"; then
  echo "Creating Pages project ${project}"
  npx wrangler pages project create "$project" --production-branch=main
fi

out="$(npx wrangler pages deploy dist --project-name="$project" --branch="$branch" \
  --commit-hash="$sha" --commit-message="${sha:0:7}" --commit-dirty=true 2>&1)"
echo "$out"

url="$(grep -oE 'https://[a-z0-9]+\.[a-z0-9-]+\.pages\.dev' <<<"$out" | head -n1 || true)"
alias="$(grep -oiE 'alias URL: https://[^[:space:]]+' <<<"$out" | sed -E 's/^[^h]*//' | head -n1 || true)"
if [ -z "$url" ]; then
  echo "::error::No deployment URL in wrangler output"
  exit 1
fi
echo "url=$url" >> "$GITHUB_OUTPUT"
echo "alias=${alias:-$url}" >> "$GITHUB_OUTPUT"
