import sys, json
sys.path.insert(0, '.')
import oshares_live as o
raw = json.load(open('/tmp/osfx/raw.json'))
cases = [('KHP','2026-09-14'),('ASM','2025-10-29'),('MCH','2026-07-26')]
def key(r):
    fa = r.get('forward_absorption') or {}
    return (r['value'], r['method'], r.get('anchor_date'), r.get('anchor_verified'), fa.get('verdict'),
            [e['exright_date'] for e in r['events_applied']], r.get('ambiguous_value_if_rolled'),
            (r.get('absorption_test') or {}).get('verdict'), r.get('fin_fallback'), r.get('fin_anchor_ais_certified'))
def off(tk, asof, cache):
    real = o._forward_absorption_test
    o._forward_absorption_test = lambda *a, **k: ([], None)
    try: return key(o.oshares_at([tk], asof, _cache=cache, live=True)[tk])
    finally: o._forward_absorption_test = real
def sig(tk, asof, cache):
    return (key(o.oshares_at([tk], asof, _cache=cache, live=True)[tk]),
            key(o.oshares_at([tk], asof, _cache=cache, live=False)[tk]), off(tk, asof, cache))
for tk, asof in cases:
    q, c, cn = raw[tk]
    q = [x for x in q if x['time'] <= asof]
    cn = [x for x in cn if (x['effective_date'] or x['exright_date'] or '') <= asof]
    ref = sig(tk, asof, (q, cn))
    changed = True
    while changed:
        changed = False
        for lst in (q, cn):
            for i in range(len(lst)-1, -1, -1):
                trial = lst[:i] + lst[i+1:]
                cache = (trial, cn) if lst is q else (q, trial)
                if sig(tk, asof, cache) == ref:
                    lst.pop(i); changed = True
    print('==', tk, asof, ref)
    for x in sorted(q, key=lambda r: r['time']):
        print(f'    _Q("{tk}", "{x["time"]}", {float(x["OShares"]):_.0f}.0),')
    for x in sorted(cn, key=lambda r: r['effective_date'] or r['exright_date']):
        if x['event_code']=='AIS':
            d = x['shares_delta']; print(f'    _A("{tk}", "{x["effective_date"]}", {float(x["shares_total_after"]):_.0f}.0' + (f', delta={float(d):_.0f}.0' if d else '') + '),')
        else:
            print(f'    _I("{tk}", "{x["exright_date"]}", vol={x["issue_volumn"]}, ratio={x["exercise_ratio"]}, method="{x["issue_method_name_vi"]}", listing={x["listing_date"]!r}),')
