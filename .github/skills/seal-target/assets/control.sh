set -euo pipefail
cd "$(mktemp -d)"
python -c 'from bit import Key; k = Key(); print(k.address, k.to_wif())' | {
  read -r ADDRESS WIF
  # control: seal with the secret kept, then open the record with it
  age-keygen -o identity 2>/dev/null
  echo "$WIF" | age -a -r "$(age-keygen -y identity)" > bounty.age
  age -d -i identity bounty.age > opened
  python -c 'from bit import Key; print(Key(open("opened").read().split()[-1]).address)' | grep -qx "$ADDRESS"
}
echo round trip ok
