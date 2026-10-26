"""Turn the private Market Desk data (ArtifactData out_dir dump) into the public files.
Usage: python3 tools/publish.py <dump_dir> <YYYY-MM-DD>
dump_dir holds editions/<date>.json and stocks/<TICKER>.json. Removes units, cost_gbp and snapshot;
adds weight_pct only (no pound amounts are ever written)."""
import json, glob, os, sys
D, date = sys.argv[1].rstrip('/') + '/', sys.argv[2]
ed = json.load(open(D + f'editions/{date}.json')); ed = ed.get('data', ed)
fx = ed.get('gbpusd')
docs = {}
for f in glob.glob(D + 'stocks/*.json'):
    d = json.load(open(f)); d = d.get('data', d); docs[d['ticker']] = d
val = {}
for t, d in docs.items():
    sn = d.get('snapshot') or {}
    if not sn.get('value_gbp') or not sn.get('price') or not d.get('price'): val[t] = None; continue
    v = sn['value_gbp'] * (d['price'] / sn['price'])
    if d.get('ccy') == '$' and sn.get('gbpusd') and fx: v *= sn['gbpusd'] / fx
    val[t] = v
tot = sum(v for v in val.values() if v)
for t, d in docs.items():
    for k in ('units', 'cost_gbp', 'snapshot'): d.pop(k, None)
    d['weight_pct'] = round(val[t] / tot * 100, 2) if val[t] else None
    json.dump(d, open(f'data/stocks/{t}.json', 'w'), separators=(',', ':'))
json.dump(ed, open(f'data/editions/{date}.json', 'w'), separators=(',', ':'))
eds = sorted((os.path.basename(f)[:-5] for f in glob.glob('data/editions/*.json')), reverse=True)
for old in eds[60:]: os.remove(f'data/editions/{old}.json')
json.dump({"stocks": sorted(docs), "editions": eds[:60]}, open('data/index.json', 'w'))
bad = [f for f in glob.glob('data/stocks/*.json') if any(k in open(f).read() for k in ('cost_gbp', 'value_gbp', '"units"'))]
assert not bad, bad
print('published', date, len(docs), 'stocks;', len(ed.get('stories', [])), 'stories')
