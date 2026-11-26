# Recipes

**One line.** A recipe changes three spots: the package and `CMD` in `Dockerfile`, the product block in `seal.sh`, and the same block plus one open line in `control.sh`.

Tested 2026-11-25 on python:3.13-alpine (Alpine 3.24) with bit 0.8.0: silent seal, control round trip in the built image, audit without a leak.

| Product | Version | `apk add` | `CMD` | Record | Opens with |
|---|---|---|---|---|---|
| age | 1.3.2 | `age` | `["cat", "/bounty/bounty.age"]` | One armored file | An age identity (X25519) |
| restic | 0.18.1 | `restic` | `["tar", "-C", "/bounty", "-c", "repo"]` | A repository, as a tar | A password (scrypt) |
| SQLCipher | 4.6.1 | `sqlcipher` | `["cat", "/bounty/bounty.db"]` | One database file | A raw 256-bit key |

Where the block goes:

- `seal.sh`: replaces the lines after `echo "$ADDRESS" > address`, inside `{ … }`.
- `control.sh`: replaces the lines between `read -r ADDRESS WIF` and the last `python` line.

## age

The template: `assets/seal.sh` and `assets/control.sh` as they are.

Post-quantum: add `-pq` to the first `age-keygen` in both files. The record becomes `mlkem768x25519`.

## restic

`seal.sh`

```sh
  # a random password, held only by this shell
  export RESTIC_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
  restic init --repo repo --quiet
  echo "$WIF" | restic backup --repo repo --stdin --stdin-filename wif --no-cache --quiet
```

`control.sh`

```sh
  export RESTIC_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
  restic init --repo repo --quiet
  echo "$WIF" | restic backup --repo repo --stdin --stdin-filename wif --no-cache --quiet
  restic dump --repo repo --no-cache --quiet latest wif > opened
```

- `--no-cache` keeps restic's cache out of the image.
- Challenger: `docker run --rm IMAGE > repo.tar && tar -xf repo.tar`.

## SQLCipher

`seal.sh`

```sh
  # a random raw 256-bit key, held only by this shell
  KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
  printf "PRAGMA key = \"x'%s'\";\ncreate table bounty (wif text);\ninsert into bounty values ('%s');\n" "$KEY" "$WIF" | sqlcipher bounty.db > /dev/null
```

`control.sh`

```sh
  KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
  printf "PRAGMA key = \"x'%s'\";\ncreate table bounty (wif text);\ninsert into bounty values ('%s');\n" "$KEY" "$WIF" | sqlcipher bounty.db > /dev/null
  printf "PRAGMA key = \"x'%s'\";\nselect wif from bounty;\n" "$KEY" | sqlcipher bounty.db > opened
```

- `> /dev/null`: `PRAGMA key` answers `ok`, and the seal must stay silent.
- The raw key skips the passphrase KDF: the target is the cipher, not a password.

## A new product

| Check | Pass when |
|---|---|
| Qualifies | Only the data owner holds the key; nothing in the image opens the record |
| Secret | Random, 256 bits, made inside the block |
| Key path | The bounty key reaches the tool on stdin, never as a tool argument |
| Silent | Build step 3 counts `0` |
| Opens | Build step 4 prints `round trip ok` |
| Clean | audit-target finds no bounty key |
| Small | One package or one static binary; no service, no daemon |
