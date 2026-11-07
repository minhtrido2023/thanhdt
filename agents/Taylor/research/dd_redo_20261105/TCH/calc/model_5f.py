"""TCH 5F addendum (job Taylor_20261107_130208). KHONG ghi de file r2: exec phan dinh nghia cua model_r2.py (truoc dong print dau tien),
roi chay bien the moat. Nguon peer GPM: bq_5f_roic_gpm.csv (ticker_financial, dong cuoi moi nam, GPM_P0 = TTM)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'model_r2.py')).read(); src = src[:src.index('print(f"r = ')]
g = {'__file__': os.path.join(HERE, 'model_r2.py')}; exec(src, g)
R2, nav, grid, PX, LD, Q, W3 = g['R2'], g['nav'], g['grid'], g['PX'], g['LD'], g['Q'], g['W3']
print(f"gia {PX:,.0f} ({Q['price_date']}); CK 5 ty {LD:.2%}")
s_of = lambda gm: (0.8 * gm - 0.08) / (1 - gm)          # dao cong thuc s(1-g)=0,8(g-0,1) (REPORT §8c / skeptic B3)
sizes = Q['adv250']['sizes']
def run(name, **kw):
    v, w = grid(**kw); out = {}
    for k in sorted(sizes, key=float):
        s = R2.stats(v, w, PX, sizes[k]['disc']); out[k] = dict(center=s['center_post'], p10=s['p10_post'], p50=s['p50_post'], p90=s['p90_post'], below=s.get('pct_below'), label=R2.label(PX, s))
    s = R2.stats(v, w, PX, LD); print(f"{name}: " + R2.fmt(s, PX) + " | nhan theo co: " + ", ".join(f"{float(k)*1000:,.0f}tr {o['label']}" for k, o in out.items()))
    return dict(ref=s, by_size=out, label=R2.label(PX, s))
GPM = dict(med14=0.379, mean14=0.394, med10=0.390, mean10=0.406)     # TB 2016-2025 peer (xem ADDENDUM_5F bang peer)
res = {'BASE_r2 (s_old {25;40;55})': run('BASE_r2')}
for k, gm in GPM.items():
    c = s_of(gm); res[f'CHAT3C_s_old_tam_{k}'] = run(f'CHAT3C s_old tam {c:.1%} (GPM nganh {gm:.1%}, {k})', ss=((c - 0.15, c, c + 0.15), W3))
res['WIDE (s_old lich su {40;55;70} + quy dat moi +10%)'] = run('WIDE', ss=((0.40, 0.55, 0.70), W3), s_new=0.10)
res['WIDE_nhe (quy dat moi +10% chi)'] = run('WIDE_nhe', s_new=0.10)
res['NONE_cung (s_old TB TCH hop nhat 29,8% GPM => s 19,1%; quy dat moi -10%)'] = run('NONE_cung', ss=((s_of(0.298) - 0.15, s_of(0.298), s_of(0.298) + 0.15), W3), s_new=-0.10)
json.dump({k: v for k, v in res.items()}, open(os.path.join(HERE, 'model_5f_out.json'), 'w'), indent=1, default=float, ensure_ascii=False)
