#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
echo "| Target | Bounty (BTC) | Status | Proof |"
echo "|---|---|---|---|"
for f in targets/*.json; do
  name=$(basename "$f" .json)
  read -r address listed < <(jq -r '"\(.address) \(.listed)"' "$f")
  # manifests come from strangers: only checked values reach the URL and the table
  [[ $name =~ ^[a-z0-9-]+$ && $address =~ ^[a-zA-Z0-9]{26,62}$ && $listed =~ ^[0-9-]{10}$ ]] || continue
  curl -sf "https://mempool.space/api/address/$address" |
    jq -r --arg n "$name" --arg a "$address" --arg d "$listed" '.chain_stats
      | (if   .funded_txo_sum == 0 then "unfunded"
         elif .spent_txo_sum  == 0 then "standing since \($d)"
         else "claimed" end) as $status
      | "| \($n) | \(.funded_txo_sum / 1e8) | \($status) | [\($a)](https://mempool.space/address/\($a)) |"'
done
printf '\nChecked %s UTC.\n' "$(date -u +%F)"
