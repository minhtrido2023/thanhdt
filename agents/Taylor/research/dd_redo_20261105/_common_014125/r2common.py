"""Module chung VONG 2 (job Taylor_20261105_020013) cho MBB FPT HPG HHS — theo STANDARD_r2.md.
- Ket cuc: moi o = to hop gia tri cac truc (deu tat dinh trong o, KHONG co ky vong co dieu kien ben trong o);
  trong so ket cuc = tich trong so cac truc. Phan vi = _shared/wpct.py (mid-block CDF), KHONG tu viet.
- Thanh khoan: luat can bac hai cua common.py, bao ca ADV 250 va 60 phien, co tham chieu 5 ty + sleeve that 10/40 trieu.
- Ban song song truc r: r = 12,5/13,5/14,5% trong so 0,25/0,50/0,25 [UL] (truc r bi loai khoi luoi chinh vi luat r neo lai huy dong)."""
import csv, hashlib, itertools, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_shared'))
from wpct import wpct, weight_below   # noqa: E402

Q_REF = 5e9; Q_SLEEVE = (10e6, 40e6); NAV_SPACEX = 0.94e9
R_AXIS = ((0.125, 0.25), (0.135, 0.50), (0.145, 0.25))


def liq2(tk):
    rows = sorted((r for r in csv.DictReader(open(os.path.join(HERE, 'bq_px_liq_20261104.csv'))) if r['ticker'] == tk), key=lambda r: r['time'])
    out = {}
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        o = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv, sigma_d=sig, disc={}, part={})
        for q in (Q_REF,) + Q_SLEEVE:
            o['disc'][f'{q:.0f}'] = sig * math.sqrt(q / adv); o['part'][f'{q:.0f}'] = q / adv
        out[f'adv{n}'] = o
    out['d_ref'] = out['adv250']['disc'][f'{Q_REF:.0f}']
    out['d_ref_adv60'] = out['adv60']['disc'][f'{Q_REF:.0f}']
    out['d_sleeve'] = {f'{q/1e6:.0f}tr': out['adv250']['disc'][f'{q:.0f}'] for q in Q_SLEEVE}
    # vung hieu chinh luat can bac hai: thuong duoc kiem tren ~0,1%-~20% ADV (uoc luong, theo van lieu market-impact)
    pr = out['adv250']['part']
    def cls(x): return 'DUOI vung (CK that ~ nua spread, chua do)' if x < 0.001 else ('TREN vung (luat can bac hai co the danh gia THAP CK)' if x > 0.20 else 'trong vung')
    out['calib'] = {k: cls(v) for k, v in pr.items()}
    out['calib_note'] = ("Q/ADV250 (vung hieu chinh uoc luong ~0,1%-20% ADV): " +
                         '; '.join(f"{lab} {pr[k]:.3%} -> {cls(pr[k])}" for lab, k in (('5 ty', f'{Q_REF:.0f}'), ('10tr', '10000000'), ('40tr', '40000000')))
                         + f"; 5 ty / ADV60 = {out['adv60']['part'][f'{Q_REF:.0f}']:.2%}")
    return out


def outcomes(axes, fn):
    """axes: list of (name, [(value, weight), ...]); fn(**kw) -> gia tri truoc CK. Tra ve list (combo, value, weight)."""
    names = [a[0] for a in axes]; res = []
    for combo in itertools.product(*[a[1] for a in axes]):
        kw = {n: c[0] for n, c in zip(names, combo)}; w = float(np.prod([c[1] for c in combo]))
        res.append((kw, fn(**kw), w))
    tw = sum(r[2] for r in res); assert abs(tw - 1) < 1e-9, tw
    return res


def stats(res, px, d):
    v = np.array([r[1] for r in res]) * (1 - d); w = np.array([r[2] for r in res])
    q = wpct(v, w, (0.10, 0.25, 0.50, 0.75, 0.90))
    return dict(n=len(res), center=float((v * w).sum()), p10=q[0.10], p25=q[0.25], p50=q[0.50], p75=q[0.75], p90=q[0.90],
                pct_below_px=weight_below(v, w, px), min=float(v.min()), max=float(v.max()))


def label(px, s):
    return 'DƯỚI vùng' if px < s['p10'] else ('TRÊN vùng' if px > s['p90'] else 'TRONG vùng')


def write_grid(path, res):
    keys = list(res[0][0].keys())
    with open(path, 'w', newline='') as fh:
        wr = csv.writer(fh); wr.writerow(keys + ['value_pre', 'weight'])
        for kw, v, w in res: wr.writerow([kw[k] for k in keys] + [f'{v:.4f}', f'{w:.10f}'])


def md5s(paths):
    return {os.path.relpath(p, os.path.join(HERE, '..')): hashlib.md5(open(p, 'rb').read()).hexdigest() for p in paths}


def r1(x):
    return int(round(x))


def finalize(tk, calc_dir, px, pxd, R, axes, fn, central_kw, extra_axes_names):
    """Chay luoi chinh + ban song song (truc r; tung truc moi them bi bo). Ghi grid_<tk>_r2.csv. Tra ve dict ket qua."""
    L = liq2(tk); d = L['d_ref']
    res = outcomes(axes, lambda **kw: fn(R, **kw))
    write_grid(os.path.join(calc_dir, f'grid_{tk.lower()}_r2.csv'), res)
    main = stats(res, px, d); pre = stats(res, px, 0.0)
    rax = [(R + dr, w) for (rr, w), dr in zip(R_AXIS, (-0.01, 0.0, 0.01))]
    res_r = outcomes(axes + [('r', rax)], lambda r, **kw: fn(r, **kw))
    par = {'co_truc_r_pm1pp': stats(res_r, px, d)}
    for nm in extra_axes_names:   # bo tung truc moi them (ve gia tri co so cua no) de thay tac dong
        base_v = central_kw[nm]
        ax2 = [(a[0], [(base_v, 1.0)]) if a[0] == nm else a for a in axes]
        par[f'khong_truc_{nm}'] = stats(outcomes(ax2, lambda **kw: fn(R, **kw)), px, d)
    central = fn(R, **central_kw) * (1 - d)
    # dong gop: o nao quyet dinh P10/P90 (trong so nhanh kich ban cua cac ket cuc quanh P10/P90)
    v = np.array([r[1] for r in res]) * (1 - d); w = np.array([r[2] for r in res])
    def near(q):
        m = np.abs(v - q) <= 0.05 * abs(q); tw = w[m].sum(); out = {}
        for (kw, _, ww), mm in zip(res, m):
            if mm: out[kw['scen']] = out.get(kw['scen'], 0) + ww / tw
        return {k: round(float(x), 3) for k, x in sorted(out.items())}
    drv = dict(p10_scen_mix_pm5pct=near(main['p10']), p90_scen_mix_pm5pct=near(main['p90']))
    return dict(liq=L, main=main, pre=pre, parallel=par, central=central, drivers=drv, label=label(px, main),
                label_ref_size='5 ty (ADV250, Y=1)', d_ref=d)


def fmt(s):
    return (f"n={s['n']} | tam {s['center']:,.0f} | P10 {s['p10']:,.0f} P25 {s['p25']:,.0f} P50 {s['p50']:,.0f} P75 {s['p75']:,.0f} P90 {s['p90']:,.0f} "
            f"| %duoi gia {s['pct_below_px']:.1%} | min {s['min']:,.0f} max {s['max']:,.0f}")


def write_summary(sum_path, base_old, R2, extra):
    import json, shutil
    bk = sum_path.replace('SUMMARY.json', 'SUMMARY_r1.json')
    if not os.path.exists(bk): shutil.copyfile(sum_path, bk)
    old = json.load(open(bk)); m = R2['main']
    new = dict(old)
    new.update(round='r2', job='Taylor_20261105_020013', center_post_liq=r1(m['center']), center_pre_liq=r1(R2['pre']['center']),
               p10_post=r1(m['p10']), p25_post=r1(m['p25']), p50_post=r1(m['p50']), p75_post=r1(m['p75']), p90_post=r1(m['p90']),
               p10_pre=r1(R2['pre']['p10']), p50_pre=r1(R2['pre']['p50']), p90_pre=r1(R2['pre']['p90']),
               p10_out=r1(m['p10']), p50_out=r1(m['p50']), p90_out=r1(m['p90']), pct_weight_below_price=m['pct_below_px'], n_outcomes=m['n'],
               min_outcome=r1(m['min']), central_param_value_post=r1(R2['central']), liq_disc_5ty=R2['d_ref'],
               px_vs_center_post=base_old['price'] / m['center'] - 1, px_vs_p10_post=base_old['price'] / m['p10'] - 1, px_vs_p90_post=base_old['price'] / m['p90'] - 1,
               label=R2['label'], ck_ref_size=dict(size_vnd=Q_REF, disc_adv250=R2['liq']['d_ref'], disc_adv60=R2['liq']['d_ref_adv60'],
                                                     adv250=R2['liq']['adv250']['adv_med'], adv60=R2['liq']['adv60']['adv_med']),
               ck_real_sleeve=dict(sizes_vnd=list(Q_SLEEVE), disc_adv250=R2['liq']['d_sleeve'], nav_spacex_ref=NAV_SPACEX, note=R2['liq']['calib_note']),
               parallel_versions={k: {kk: (r1(vv) if kk not in ('pct_below_px', 'n') else vv) for kk, vv in s.items()} for k, s in R2['parallel'].items()},
               drivers=R2['drivers'], zone_old_r1=dict(center=old['center_post_liq'], p10=old['p10_post'], p90=old['p90_post'], label=old['label']))
    new.update(extra)
    json.dump(new, open(sum_path, 'w'), ensure_ascii=False, indent=1, default=float)
    return new
