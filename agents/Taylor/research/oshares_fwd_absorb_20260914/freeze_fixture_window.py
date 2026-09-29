import sys, json
sys.path.insert(0, '.')
exec(open('/tmp/osfx/min.py').read().split('for tk, asof in cases:')[0])
spec = {'KHP': ('2025-04-01', '2020-01-01'), 'ASM': ('2024-04-01', '2024-01-01'), 'MCH': ('2025-01-01', '2025-01-01')}
for tk, asof in cases:
    q, c, cn = raw[tk]
    q = [x for x in q if x['time'] <= asof]; cn = [x for x in cn if (x['effective_date'] or x['exright_date'] or '') <= asof]
    ref = sig(tk, asof, (q, cn))
    qc, cc = spec[tk]
    qq = [x for x in q if x['time'] >= qc]
    ccs = [x for x in cn if (x['effective_date'] or x['exright_date']) >= cc]
    # add latest AIS before cc
    older = [x for x in cn if x['event_code']=='AIS' and x['effective_date'] < cc]
    s = sig(tk, asof, (qq, ccs)); print(tk, 'window ok' if s == ref else 'window FAIL', len(qq), len(ccs))
    if s != ref and older:
        ccs2 = [max(older, key=lambda r: r['effective_date'])] + ccs
        s2 = sig(tk, asof, (qq, ccs2)); print('  +prev AIS', 'ok' if s2 == ref else 'FAIL', s2 if s2 != ref else '')
        if s2 == ref: ccs = ccs2
    for x in sorted(qq, key=lambda r: r['time']):
        print(f'    _Q("{tk}", "{x["time"]}", {float(x["OShares"]):_.0f}.0),')
    for x in sorted(ccs, key=lambda r: r['effective_date'] or r['exright_date']):
        if x['event_code']=='AIS':
            d = x['shares_delta']; print(f'    _A("{tk}", "{x["effective_date"]}", {float(x["shares_total_after"]):_.0f}.0' + (f', delta={float(d):_.0f}.0' if d else '') + '),')
        else:
            print(f'    _I("{tk}", "{x["exright_date"]}", vol={float(x["issue_volumn"]):_.0f}.0, ratio={x["exercise_ratio"]}, method="{x["issue_method_name_vi"]}")  # listing {x["listing_date"]}')
