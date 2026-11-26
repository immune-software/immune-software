#!/usr/bin/env bash
# audit.sh IMAGE ADDRESS: scan every layer of a target image without running it.
# Exit 0 PASS, 1 LEAK, 2 FAIL, 3 CHECK (other key material to test by hand), 64 usage, 70 setup.
set -euo pipefail
(( $# == 2 )) || { echo "usage: audit.sh IMAGE ADDRESS" >&2; exit 64; }
image=$1 address=$2
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

docker image inspect "$image" >/dev/null 2>&1 || docker pull -q "$image" >/dev/null
docker save "$image" > "$work/image.tar"
docker run --rm -v "$work/image.tar:/image.tar:ro" -v "$here/scan.py:/scan.py:ro" python:3.13-alpine sh -c '
  pip -q install bit==0.8.0 >/dev/null 2>&1 || { echo "audit: pip install bit failed" >&2; exit 70; }
  exec python /scan.py /image.tar "$1"' _ "$address"
