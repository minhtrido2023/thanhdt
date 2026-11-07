"""TCH 5F fix (job Taylor_20261107_131628): bien the bien BACKLOG ve TB nganh (skeptic #6). Tai dung model_r2.py nhu model_5f.py.
m_backlog tam = 0,8*(GPM-0,10) (cung quan he s(1-g)=0,8(g-0,1) -> m=0,335 khi GPM=51,9%); luoi m giu lech {-3,5;0;+2,5}pp nhu r2.
(a) chi m ve nganh; (b) m + GM chi phi hoan thanh (cost_bl/rest_old) ve nganh; (c) = (b) + s_old chat-3c cung GPM nganh."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'model_r2.py')).read(); src = src[:src.index('print(f"r = ')]
g = {'__file__': os.path.join(HERE, 'model_r2.py')}; exec(src, g)
R2, nav, grid, PX, LD, Q, W3, proj, HTK, NEW = (g[k] for k in ('R2','nav','grid','PX','LD','Q','W3','proj','HTK','NEW'))
sizes = Q['adv250']['sizes']; GM0 = g['GM']; VAT = g['VAT']; M0 = g['MS']
s_of = lambda gm: (0.8 * gm - 0.08) / (1 - gm)
def set_gm(gm):                                     # tinh lai chi phi hoan thanh backlog + phan con lai HTK dat cu theo GM
    cb = {"me": 0.0, "crv": 0.0, "khac": 0.0}
    for k, (n, sh, y, gg) in proj.items(): cb[gg] += n / VAT * (1 - gm)
    g['cost_bl'].update(cb); g['rest_old'].update({k: HTK[k] - cb[k] - NEW.get(k, 0.0) for k in sorted(HTK)})
def run(name, gm_m=None, gm_cost=None, s_c=None):
    set_gm(gm_cost if gm_cost else GM0)
    if gm_m: m = 0.8 * (gm_m - 0.10); g['MS'] = (m - 0.035, m, m + 0.025)
    else: g['MS'] = M0
    kw = dict(ss=((s_c - 0.15, s_c, s_c + 0.15), W3)) if s_c is not None else {}
    v, w = grid(**kw); out = {}
    for k in sorted(sizes, key=float):
        s = R2.stats(v, w, PX, sizes[k]['disc']); out[k] = dict(center=s['center_post'], p10=s['p10_post'], p50=s['p50_post'], p90=s['p90_post'], below=s.get('pct_below'), label=R2.label(PX, s))
    s = R2.stats(v, w, PX, LD); print(f"{name}: " + R2.fmt(s, PX) + " | nhan theo co: " + ", ".join(f"{float(k)*1000:,.0f}tr {o['label']}" for k, o in out.items()))
    return dict(ref=s, by_size=out, label=R2.label(PX, s))
GPM = dict(med14=0.379, mean14=0.394, med10=0.390, mean10=0.406)
res = {'CONTROL_r2': run('CONTROL_r2')}
for k, gm in GPM.items():
    res[f'a_m_nganh_{k}'] = run(f'(a) chi m backlog = 0,8*({gm:.1%}-0,10) {k}', gm_m=gm)
    res[f'b_m_GM_nganh_{k}'] = run(f'(b) m + GM chi phi HT {gm:.1%} {k}', gm_m=gm, gm_cost=gm)
    res[f'c_chat3c_day_du_{k}'] = run(f'(c) b + s_old chat-3c {s_of(gm):.1%} {k}', gm_m=gm, gm_cost=gm, s_c=s_of(gm))
json.dump(res, open(os.path.join(HERE, 'model_5f_fix_out.json'), 'w'), indent=1, default=float, ensure_ascii=False)
