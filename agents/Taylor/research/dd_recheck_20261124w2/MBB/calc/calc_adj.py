"""E17 tâm kỳ vọng điều chỉnh MBB — PREREG_adj.md (ef5157cb…) + PREREG_adj_v2.md (835dfc1e…). MÙ GIÁ (PX chỉ để mô hình r3 chạy, không dùng).
Chạy lại mô hình r3 (mbb_r3.py khôi phục) với các biến thể hạng mục + TỔ HỢP. Chạy:
  /home/trido/thanhdt/wc_venv/bin/python -I calc_adj.py /tmp/ddrestore_MBB/agents/Taylor/research/dd_redo_20261105 <worktree>"""
import sys, os, io, json, hashlib, runpy, contextlib
ROOT = os.path.abspath(sys.argv[1]); WT = os.path.abspath(sys.argv[2]); HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
PR = os.path.join(WT, 'agents/Taylor/research/dd_adjcenter_20261124')
assert md5(os.path.join(PR, 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(PR, 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
assert md5(os.path.join(ROOT, 'MBB/calc_r3/mbb_r3.py')) == 'f5ad8f9ed0b3761de289f918e17ba679'
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(os.path.join(ROOT, 'MBB/calc_r3/mbb_r3.py'), run_name='__main__')
R2C, base, AXH, SH, PAYOUT, R, D, DAYS, TAX, NCI, BV = (g[k] for k in ('R2C', 'base', 'AXH', 'SH', 'PAYOUT', 'R', 'D', 'DAYS', 'TAX', 'NCI', 'BV'))
C0 = 21069

def ri(path, roeT, ke, bv0, k=0.0, prem=True):
    """= ri_ps của mbb_r3 (gpol npv0) + rò k phần LN sang quỹ KTPL (nợ phải trả, không về cổ đông)."""
    bv = bv0; pv = 0.0
    for i, r in enumerate(path, 1):
        pv += (r * (1 - k) - ke) * bv / (1 + ke) ** i; bv += r * bv * (1 - k - PAYOUT)
    rt = roeT * (1 - k) if prem else ke
    tv = (rt - ke) * bv / ke / (1 + ke) ** len(path)
    return (bv0 + pv + tv) / SH * 1e3 / (1 + ke) ** (DAYS / 365)

def center(k=0.0, dpath=(0, 0, 0), prem=True, ppl=None, cov=0.0, r=R):
    def fn(scen, droe, mbv):
        b = base[scen]
        return ri([x + droe + dp for x, dp in zip(b['path'], dpath)], b['roeT'] + droe, r, b['bv26'] - mbv - cov, k, prem)
    c = R2C.stats(R2C.outcomes(AXH, fn), 19250.0, D)['center']
    if ppl:  # phát hành riêng lẻ 200 tr CP ở giá ppl (đ/cp): (V·SH + 200·P)/(SH+200)
        c = (c * SH + 200 * ppl * (1 - D)) / (SH + 200)
    return c
c0 = center(); assert round(c0) == C0, c0
BVPS = BV / SH * 1e3
def pct(x): return round((x / c0 - 1) * 100, 3)
CASES = {
 'KT_half': dict(k=0.0445), 'KT_full': dict(k=0.089),
 'ROEpath_up': dict(dpath=(0.015, 0.01, 0.01)),
 'PPL_book': dict(ppl=BVPS), 'PPL_1.3x': dict(ppl=1.3 * BVPS),
 'S_no_term_premium': dict(prem=False), 'S_cov_restore_1940': dict(cov=1940 * (1 - TAX) * (1 - NCI)),
 'S_KT_5pct': dict(k=0.05),
}
K = {n: dict(center=round(center(**kw)), d_pct=pct(center(**kw))) for n, kw in CASES.items()}
# hạng mục vào tâm: (tên case điểm m, case m thấp, case m cao, p, plo, phi)
IT = [('KT_half', 'KT_half', 'KT_full', .5, .25, .75), ('ROEpath_up', 'ROEpath_up', 'ROEpath_up', .35, .15, .55), ('PPL_book', 'PPL_1.3x', 'PPL_book', .5, .25, .75)]
lin = sum(p * K[a]['d_pct'] for a, _, _, p, _, _ in IT)
lo_l = sum(min(pp * K[x]['d_pct'] for pp in (plo, phi) for x in (b, c)) for _, b, c, _, plo, phi in IT)
hi_l = sum(max(pp * K[x]['d_pct'] for pp in (plo, phi) for x in (b, c)) for _, b, c, _, plo, phi in IT)
# TỔ HỢP: chạy lại mô hình với tham số nội suy theo p (k×p, dpath×p, xác suất phát hành p) — chạy thật, không cộng tuyến tính
def combo(pk, mk, pr, pp, mppl):
    v = center(k=mk * pk, dpath=tuple(x * pr for x in (0.015, 0.01, 0.01)))
    vp = (v * SH + 200 * mppl * (1 - D)) / (SH + 200)
    return v * (1 - pp) + vp * pp
cc = combo(.5, .0445, .35, .5, BVPS)
cands = [combo(pk, mk, pr, pp, mp) for pk in (.25, .75) for mk in (.0445, .089) for pr in (.15, .55) for pp in (.25, .75) for mp in (BVPS, 1.3 * BVPS)]
out = dict(control_center=round(c0), bvps=round(BVPS), cases=K, sum_lin_pct=round(lin, 3), range_lin_pct=[round(lo_l, 3), round(hi_l, 3)],
           combo=dict(center=round(cc), d_pct=pct(cc), low=round(min(cands)), high=round(max(cands))))
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(os.path.join(HERE, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
