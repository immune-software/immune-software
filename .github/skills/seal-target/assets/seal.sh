set -euo pipefail
cd /bounty
python -c 'from bit import Key; k = Key(); print(k.address, k.to_wif())' | {
  read -r ADDRESS WIF
  echo "$ADDRESS" > address
  # keep the public half of a fresh age key pair, drop the private half
  RECIPIENT=$(age-keygen 2>&1 >/dev/null | cut -d' ' -f3)
  echo "$WIF" | age -a -r "$RECIPIENT" > bounty.age
}
