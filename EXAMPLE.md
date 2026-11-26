# Hello world: a bounty sealed with age

**One line.** The target is [age](https://github.com/FiloSottile/age), a file encryption tool: two files make the image, one script makes the board. The idea is in [PROOF_OF_SECURITY.md](PROOF_OF_SECURITY.md).

Tested 2026-11-25 on Docker 29.9 with age 1.3.2. Not exercised: the registry push, the hosted workflow run, real coins.

```bash
command -v docker jq
```

```bash
OWNER=real-immune-software   # ghcr.io namespace: your GitHub user
```

## Vendor: four steps

**1. Seal and package.** The build creates the bounty key, seals it and keeps only the sealed record.

```bash
mkdir hello-age && cd hello-age
cat > seal.sh <<'EOF'
set -euo pipefail
cd /bounty
python -c 'from bit import Key; k = Key(); print(k.address, k.to_wif())' | {
  read -r ADDRESS WIF
  echo "$ADDRESS" > address
  # keep the public half of a fresh age key pair, drop the private half
  RECIPIENT=$(age-keygen 2>&1 >/dev/null | cut -d' ' -f3)
  echo "$WIF" | age -a -r "$RECIPIENT" > bounty.age
}
EOF
cat > Dockerfile <<'EOF'
FROM python:3.13-alpine
RUN apk add --no-cache age && pip -q install bit==0.8.0
COPY seal.sh /bounty/
RUN sh /bounty/seal.sh
CMD ["cat", "/bounty/bounty.age"]
EOF
docker build --no-cache -t ghcr.io/$OWNER/hello-age .
ADDRESS=$(docker run --rm ghcr.io/$OWNER/hello-age cat /bounty/address)
echo "fund $ADDRESS"
```

**expect:** `fund` and an address that starts with `1`.

- The Bitcoin key is in the clear only inside a pipe during the build. No image layer holds it.
- The age private key that opens the record went to `/dev/null`: nobody holds it, the vendor included.
- A scan of the image finds sample keys in the `bit` test suite and the `age-keygen` help text. None opens the record.
- `--no-cache` matters: a cached build reuses an earlier seal, key included, even one made in another folder.
- For real money, pin the base image by digest and build on a machine you trust.

Step 1 alone is a complete dry run on one laptop.

**2. Publish.**

```bash
docker login ghcr.io -u $OWNER
docker push ghcr.io/$OWNER/hello-age
```

- `docker login` asks for a GitHub token with the `write:packages` scope.
- Make the package public: GitHub > Packages > hello-age > Package settings > Change visibility.

**3. Fund.** Send the bounty to `$ADDRESS` from any wallet.

**4. List it.** Write the manifest and open a pull request that adds it to `targets/` in the board repository.

```bash
cat > hello-age.json <<EOF
{
  "image": "$(docker inspect --format '{{index .RepoDigests 0}}' ghcr.io/$OWNER/hello-age)",
  "address": "$ADDRESS",
  "listed": "$(date +%F)"
}
EOF
```

- The manifest holds only what the blockchain cannot prove.
- Optional field: `source`, a link to the code.

## Board: one script

A board is a public GitHub repository that holds three things. This repository is one.

| Path | Job |
|---|---|
| [targets/](targets) | One manifest per target, merged by pull request |
| [board.sh](board.sh) | Reads each bounty address from the blockchain and prints the table |
| [board.yml](.github/workflows/board.yml) | Runs `board.sh` every hour and commits [BOARD.md](BOARD.md) |

`board.sh`

```bash
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
```

`.github/workflows/board.yml`

```yaml
name: board
on:
  schedule:
    - cron: "17 * * * *"
  workflow_dispatch:
permissions:
  contents: write
jobs:
  board:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - run: bash board.sh > BOARD.md
      - run: |
          git add BOARD.md
          git diff --cached --quiet || git -c user.name=board -c user.email=board@localhost commit -m board
          git push
```

`BOARD.md` once 0.01 BTC sits on the address:

> | Target | Bounty (BTC) | Status | Proof |
> |---|---|---|---|
> | hello-age | 0.01 | standing since 2026-11-25 | the address, linked to a block explorer |
>
> Checked 2026-11-25 UTC.

## Challenger: one command

Take a manifest from the board; here it is `hello-age.json`.

```bash
docker run --rm "$(jq -r .image hello-age.json)" > bounty.age
```

- `bounty.age` is the sealed record. The tool and `seal.sh` are in the same image: `docker save` it and take it apart.
- You win when you hold what is inside: a 52-character key that starts with `K` or `L`.
- Import it into any wallet and move the coins (Electrum: Wallet > Private keys > Sweep).
- The board shows `claimed` at its next run.

## Next rungs

| Gap in the hello world | Next rung |
|---|---|
| Nothing checks the image before funding | The [skills](PROOF_OF_SECURITY.md#skills-to-assemble-challenges): pinned base image, control round trip, layer scan |
| The seal is X25519, which is not post-quantum | Use `age-keygen -pq` in `seal.sh`: the record becomes `mlkem768x25519` |
| A file is not a system of record | Seal a store: the SQLCipher and restic [recipes](.github/skills/seal-target/references/recipes.md) |

The gaps of the idea itself: [PROOF_OF_SECURITY.md](PROOF_OF_SECURITY.md#what-it-proves).
