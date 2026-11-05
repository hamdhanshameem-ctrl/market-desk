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
    if d.get('removed'): val[t] = None; continue
    if not sn.get('value_gbp') or not sn.get('price') or not d.get('price'): val[t] = None; continue
    v = sn['value_gbp'] * (d['price'] / sn['price'])
    if d.get('ccy') == '$' and sn.get('gbpusd') and fx: v *= sn['gbpusd'] / fx
    val[t] = v
tot = sum(v for v in val.values() if v)
for t, d in docs.items():
    for k in ('units', 'cost_gbp', 'snapshot'): d.pop(k, None)
    d['weight_pct'] = round(val[t] / tot * 100, 2) if val[t] else None
    if d.get('removed'): continue
    json.dump(d, open(f'data/stocks/{t}.json', 'w'), separators=(',', ':'))
# Drop tickers he no longer holds (stocks docs flagged removed) from the public edition
gone = {t for t, d in docs.items() if d.get('removed')}
if gone:
    ed['prices'] = [x for x in ed.get('prices', []) if x.get('ticker') not in gone]
    kept = []
    for st in ed.get('stories', []):
        tk = [t for t in st.get('tickers', []) if t not in gone]
        if st.get('section') == 'holding' and st.get('tickers') and not tk: continue
        st['tickers'] = tk; st['impacts'] = [i for i in st.get('impacts', []) if i.get('ticker') not in gone]; kept.append(st)
    ed['stories'] = kept
    cal = []
    for c in ed.get('calendar', []):
        if c.get('tickers') and not [t for t in c['tickers'] if t not in gone]: continue
        c['affects'] = [x for x in c.get('affects', []) if x.get('ticker') not in gone]; cal.append(c)
    ed['calendar'] = cal
    for t in gone:
        docs.pop(t)
        if os.path.exists(f'data/stocks/{t}.json'): os.remove(f'data/stocks/{t}.json')
json.dump(ed, open(f'data/editions/{date}.json', 'w'), separators=(',', ':'))
eds = sorted((os.path.basename(f)[:-5] for f in glob.glob('data/editions/*.json')), reverse=True)
for old in eds[60:]: os.remove(f'data/editions/{old}.json')
json.dump({"stocks": sorted(docs), "editions": eds[:60]}, open('data/index.json', 'w'))
bad = [f for f in glob.glob('data/stocks/*.json') if any(k in open(f).read() for k in ('cost_gbp', 'value_gbp', '"units"'))]
assert not bad, bad
print('published', date, len(docs), 'stocks;', len(ed.get('stories', [])), 'stories')
