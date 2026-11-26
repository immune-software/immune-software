# scan.py IMAGE_TAR ADDRESS: walk a `docker save` archive layer by layer; report where key material sits, never the key.
import json, re, sys, tarfile
from bit import Key

archive, bounty = sys.argv[1], sys.argv[2]
B58 = rb'[1-9A-HJ-NP-Za-km-z]'
WIF = re.compile(rb'(?<!' + B58 + rb')[5KL]' + B58 + rb'{50,51}(?!' + B58 + rb')')
HEX = re.compile(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])')
OTHER = [
    ('age secret key', re.compile(rb'AGE-SECRET-KEY-(?:PQ-)?1[0-9A-Z]{58}')),
    ('PEM private key', re.compile(rb'-----BEGIN [A-Z ]*PRIVATE KEY-----\s*[A-Za-z0-9+/]{64}')),
    ('BIP32 xprv', re.compile(rb'xprv' + B58 + rb'{107}')),
]

leaks, wif_keys, hex_seen, other, cited = [], set(), set(), [], set()


def opens(text, kind):
    try:
        k = Key(text) if kind == 'WIF' else Key.from_hex(text)
    except Exception:
        return None
    return bounty in (k.address, k.segwit_address)


def scan(data, where, layer=None):
    before = len(leaks) + len(wif_keys) + len(other)
    for m in WIF.finditer(data):
        hit = opens(m.group().decode(), 'WIF')
        if hit:
            leaks.append(('WIF', where))
        elif hit is False:
            wif_keys.add(where)
    for m in HEX.finditer(data):
        h = m.group().decode().lower()
        if h not in hex_seen:
            hex_seen.add(h)
            if opens(h, 'hex'):
                leaks.append(('hex', where))
    for kind, pattern in OTHER:
        if pattern.search(data):
            other.append((kind, where))
    if layer and len(leaks) + len(wif_keys) + len(other) > before:
        cited.add(layer)


outer = tarfile.open(archive)
manifest = json.load(outer.extractfile('manifest.json'))[0]
config = outer.extractfile(manifest['Config']).read()
steps = [re.sub(r'/bin/sh -c |\s*# buildkit$', '', h.get('created_by', ''))[:80]
         for h in json.loads(config).get('history', []) if not h.get('empty_layer')]
scan(config, 'config (env, labels, build history)')

address = seal = None
files = unreadable = 0
for i, name in enumerate(manifest['Layers'], 1):
    try:
        layer = tarfile.open(fileobj=outer.extractfile(name), mode='r|*')
        for m in layer:
            if not m.isfile():
                continue
            files += 1
            path = re.sub(r'^\.?/', '', m.name)
            data = layer.extractfile(m).read()
            scan(data, f'layer {i} {path}', i)
            if path == 'bounty/address':
                address = data.decode().strip()
            elif path == 'bounty/.wh.address':
                address = None
            elif path == 'bounty/seal.sh':
                seal = data.decode()
    except tarfile.TarError:
        unreadable += 1
done = {manifest['Config'], *manifest['Layers']}
for m in outer.getmembers():
    if m.isfile() and m.name not in done:
        scan(outer.extractfile(m).read(), f'archive {m.name}')

print(f'layers   {len(manifest["Layers"])} + config, {files} files' + (f', {unreadable} unreadable' if unreadable else ''))
print(f'address  {address} matches' if address == bounty else f'address  /bounty/address is {address or "missing"}, manifest says {bounty}')
print(f'wif      other keys in {len(wif_keys)} file(s)')
for where in sorted(wif_keys):
    print(f'           {where}')
print(f'hex      {len(hex_seen)} strings tried')
for kind, where in dict.fromkeys(other):
    print(f'other    {kind:16} {where}')
for kind, where in dict.fromkeys(leaks):
    print(f'LEAK     bounty key as {kind}  {where}')
for i in sorted(cited):
    print(f'step     layer {i}: {steps[i - 1] if i <= len(steps) else "?"}')
verdict = 'LEAK' if leaks else 'FAIL' if unreadable or address != bounty else 'CHECK' if other else 'PASS'
print(f'verdict  {verdict}')
if seal:
    print('--- /bounty/seal.sh')
    print(seal, end='')
sys.exit({'PASS': 0, 'LEAK': 1, 'FAIL': 2, 'CHECK': 3}[verdict])
