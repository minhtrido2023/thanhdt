"""MBB rev6' — thêm rò 'Quỹ khác: sử dụng' vào k (skeptic r2 killer), tính lại MỌI độ nhạy/trigger trên base mới, dải E17 đối xứng theo k.
MÙ GIÁ (19.250 chỉ là tham số kỹ thuật của R2C.stats, như calc_agm.py). Không sửa calc_agm.py (đã khoá md5 ở commit 7c1fad8a2).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I calc_agm_v2.py /tmp/ddrestore_MBB/agents/Taylor/research/dd_redo_20261105 <worktree>
Nguồn số mới (triệu đồng; ảnh ../src/img):
  HNQ3 TM22.1 (hn_p44.png): Quỹ khác dư đầu 904.382, trích 685.043, SỬ DỤNG (460.531) → dư cuối 1.128.894; cột Sử dụng tổng (29.478.802) GIẢM tổng VCSH.
  RQ3  TM22.1 (cm_p41_n22.png): Quỹ khác sử dụng (460.531); tổng VCSH 130.639.656 + 50.094.629 − 28.799.378 = 151.934.907.
  HN25 TM26.1 (h25_p65.png, năm 2025): Trích quỹ khác 556.625; 'Sử dụng các quỹ trong năm' (620.313) ở CẢ cột Quỹ khác và cột Tổng cộng.
  HN25 TM26.1 (h25_p66b.png, năm 2024): Trích quỹ khác 498.558; 'Sử dụng các quỹ trong năm' (348.289) ở cột Quỹ khác và cột Tổng cộng.
  HN25 TM4.24.4 (h25_pol35.png): 'Các quỹ khác thuộc nguồn vốn chủ sở hữu được phân bổ từ lợi nhuận sau thuế… ĐHĐCĐ phê duyệt' (không nêu mục đích, không hoàn nhập về LNCPP).
"""
import sys, os, io, json, runpy, contextlib, hashlib
ROOT = os.path.abspath(sys.argv[1]); WT = os.path.abspath(sys.argv[2]); HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(ROOT, 'MBB/calc_r3/mbb_r3.py')) == 'f5ad8f9ed0b3761de289f918e17ba679'

# ---------- 1. Số gốc ----------
LN = {2024: 22_633_757, 2025: 26_778_939}       # HN25 TM26.1: LN thuần thuộc MB
LN_9T26 = 23_784_072                            # HNQ3 TM22.1: LNCPP tăng (LN 9T26 thuộc MB)
QK = {  # năm: (dư đầu, trích, sử dụng, dư cuối)
 2024: (817_557, 498_558, 348_289, 967_689),     # + biến động khác (55)+(82) → 967.689 (kiểm dưới)
 2025: (967_689, 556_625, 620_313, 904_382),     # + biến động khác (156) + CLTG 537
 2026: (904_382, 685_043, 460_531, 1_128_894),   # 9T
}
assert QK[2024][0] + QK[2024][1] - QK[2024][2] - 55 - 82 == QK[2024][3]
assert QK[2025][0] + QK[2025][1] - QK[2025][2] - 156 + 537 == QK[2025][3]
assert QK[2026][0] + QK[2026][1] - QK[2026][2] == QK[2026][3]
# rời VCSH: dòng 'Sử dụng' có mặt ở cột Tổng cộng với cùng giá trị (2024, 2025) và cân tổng (2026 HN và riêng)
assert 142_022_525 + 51_597_885 - (88 + 460_531 + 28_462_814 + 555_369) == 164_141_608
assert 130_639_656 + 50_094_629 - (460_531 + 28_338_847) == 151_934_907
K_KTPL = dict(lo=1_866_219 / LN[2024], pt=2_418_617 / LN[2025])  # = calc_agm.py (8,245% / 9,032%)
K_KTPL['hi'] = 2 * K_KTPL['pt'] - K_KTPL['lo']                   # gương xu hướng 8,25→9,03 ⇒ 9,82% (ĐỐI XỨNG)
K_QK = dict(lo=QK[2024][2] / LN[2024],          # sử dụng 2024 / LN 2024 = 1,54% (thấp nhất 3 kỳ)
            pt=QK[2026][1] / LN[2025],          # TRÍCH 2026 / LN 2025 = 2,56% (quyết định ĐHĐCĐ năm gần nhất; quỹ không về cổ đông)
            hi=QK[2025][2] / LN[2024])          # sử dụng 2025 / LN 2024 = 2,74% (cao nhất)
use_same_year = {2024: QK[2024][2] / LN[2024], 2025: QK[2025][2] / LN[2025], '9T26': QK[2026][2] / LN_9T26}
alloc = {2025: QK[2025][1] / LN[2024], 2026: QK[2026][1] / LN[2025]}
KT = {s: K_KTPL[s] + K_QK[s] for s in ('lo', 'pt', 'hi')}

# ---------- 2. Mô hình RI r3 + k ----------
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(os.path.join(ROOT, 'MBB/calc_r3/mbb_r3.py'), run_name='__main__')
R2C, base, AXH, SH, PAYOUT, R, D, DAYS, TAX, NCI, BV, axes = (g[x] for x in ('R2C', 'base', 'AXH', 'SH', 'PAYOUT', 'R', 'D', 'DAYS', 'TAX', 'NCI', 'BV', 'axes'))
def ri(path, roeT, ke, bv0, k=0.0, prem=True, gT=0.0, gpol='npv0'):
    bv = bv0; pv = 0.0
    for i, r in enumerate(path, 1):
        pv += (r * (1 - k) - ke) * bv / (1 + ke) ** i; bv += r * bv * (1 - k - PAYOUT)
    rt = roeT * (1 - k) if prem else ke
    gr = gT if (gpol == 'r2' and rt >= ke) else 0.0
    tv = (rt - ke) * bv / (ke - gr) / (1 + ke) ** len(path)
    return (bv0 + pv + tv) / SH * 1e3 / (1 + ke) ** (DAYS / 365)
def stats(k=0.0, dpath=(0, 0, 0), prem=True, r=R, droeT=0.0, cov=0.0, ax=None, gpol='npv0'):
    def fn(scen, droe, mbv, dg=0.0, pt=0.0):
        b = base[scen]
        return ri([x + droe + dp for x, dp in zip(b['path'], dpath)], b['roeT'] + droe + droeT, r, b['bv26'] - mbv - pt - cov, k, prem, b['gT'] + dg, gpol)
    return R2C.stats(R2C.outcomes(ax or AXH, fn), 19250.0, D)
def center(**kw): return stats(**kw)['center']
s0 = stats(); assert (round(s0['p10']), round(s0['center']), round(s0['p90'])) == (14729, 21069, 27577), s0   # CONTROL rev5
c_r6 = center(k=K_KTPL['pt']); assert round(c_r6) == 18595, c_r6                                              # CONTROL rev6 (7c1fad8a2)
BVPS = BV / SH * 1e3

# ---------- 3. rev6' ----------
KP = KT['pt']; s6 = stats(k=KP); C = s6['center']
def pc(x): return round((x / C - 1) * 100, 3)
def row(v): return dict(center=round(v), d_pct=pc(v))
both = dict(without_quy_khac=dict(k_pct=round(K_KTPL['pt'] * 100, 3), center=round(c_r6), zone=[13151, 24140]),
            with_quy_khac=dict(k_pct=round(KP * 100, 3), center=round(C), zone=[round(s6['p10']), round(s6['p90'])]))
k_sens = {f'k_{s}': dict(k_pct=round(KT[s] * 100, 3), **row(center(k=KT[s]))) for s in ('lo', 'hi')}
k_sens['k_ktpl_hi_only'] = dict(k_pct=round((K_KTPL['hi'] + K_QK['pt']) * 100, 3), **row(center(k=K_KTPL['hi'] + K_QK['pt'])))
k_sens['k_qk_usage_9T26'] = dict(k_pct=round((K_KTPL['pt'] + use_same_year['9T26']) * 100, 3), **row(center(k=K_KTPL['pt'] + use_same_year['9T26'])))

# ---------- 4. Độ nhạy / trigger trên rev6' ----------
AXA = axes('sym', 'sym')                       # r3 alt A: có trục dg
sens = {
 'ROE_T_-2pp': row(center(k=KP, droeT=-0.02)), 'ROE_T_+2pp': row(center(k=KP, droeT=+0.02)),
 'no_term_premium': row(center(k=KP, prem=False)),
 'Ke_12.3': row(center(k=KP, r=0.123)), 'Ke_13.4': row(center(k=KP, r=0.134)),
 'r_+50bp': row(center(k=KP, r=R + 0.005)), 'r_-50bp': row(center(k=KP, r=R - 0.005)),
 'r_+100bp': row(center(k=KP, r=R + 0.01)), 'r_-100bp': row(center(k=KP, r=R - 0.01)),
 'RONIC_gt_Ke': row(center(k=KP, ax=AXA, gpol='r2')),
 'cov_restore_1940': row(center(k=KP, cov=1940 * (1 - TAX) * (1 - NCI))),
 'PT_MBV_loss30_p020': row(center(k=KP, ax=axes('sym', 'sym', dg=False, pt=True))),
 'weights_r2_035_045_020': row(center(k=KP, ax=axes('r2', 'sym', dg=False))),
 'HARD_ABANDON_CO_SO_MBV15688': row(ri(base['CO_SO']['path'], base['CO_SO']['roeT'], R, base['CO_SO']['bv26'] - 15688, KP) * (1 - D)),
}
# CONTROL độ nhạy cũ (k=0 phải tái lập số rev5 trong LEDGER/adj đợt 2)
assert round(center(ax=AXA, gpol='r2')) == 25317
assert round(ri(base['CO_SO']['path'], base['CO_SO']['roeT'], R, base['CO_SO']['bv26'] - 15688) * (1 - D)) == 18969
assert (round(center(droeT=-0.02)), round(center(droeT=0.02))) == (18742, 23396)

# ---------- 5. E17 trên rev6' (giữ #2, #3; k vào DẢI đối xứng) ----------
def combo(pr, pp, mppl, kk=KP):
    v = center(k=kk, dpath=tuple(x * pr for x in (0.015, 0.01, 0.01)))
    return v * (1 - pp) + (v * SH + 200 * mppl * (1 - D)) / (SH + 200) * pp
m2 = pc(center(k=KP, dpath=(0.015, 0.01, 0.01)))
m3_lo = pc((C * SH + 200 * BVPS * (1 - D)) / (SH + 200)); m3_hi = pc((C * SH + 200 * 1.3 * BVPS * (1 - D)) / (SH + 200))
ca = combo(.35, .5, BVPS)
cands = {(pr, pp, round(mp), s): combo(pr, pp, mp, KT[s]) for pr in (.15, .55) for pp in (.25, .75) for mp in (BVPS, 1.3 * BVPS) for s in ('lo', 'hi')}
trig_roe_up = round((combo(.65, .5, BVPS) / ca - 1) * 100, 3)
out = dict(
 facts=dict(k_ktpl_pct={s: round(v * 100, 3) for s, v in K_KTPL.items()}, k_qk_pct={s: round(v * 100, 3) for s, v in K_QK.items()},
            k_total_pct={s: round(v * 100, 3) for s, v in KT.items()}, qk_use_same_year_pct={str(a): round(b * 100, 3) for a, b in use_same_year.items()},
            qk_alloc_pct={str(a): round(b * 100, 3) for a, b in alloc.items()}, bvps=round(BVPS)),
 control=dict(rev5_center=round(s0['center']), rev5_zone=[round(s0['p10']), round(s0['p90'])], rev6_center=round(c_r6), rev5_RONIC=25317, rev5_HARD=18969, rev5_ROET=[18742, 23396]),
 rev6p=dict(center=round(C), zone_low=round(s6['p10']), zone_high=round(s6['p90']), n=s6['n'], pct_below_19250=round(s6['pct_below_px'], 4),
            d_pct_vs_rev6=round((C / c_r6 - 1) * 100, 3), d_pct_vs_rev5=round((C / s0['center'] - 1) * 100, 3), rule085=round(0.85 * C)),
 both=both, k_sens=k_sens, sens=sens,
 e17=dict(m2_roepath_pct=m2, m3_ppl_pct=[m3_lo, m3_hi], center_adj=round(ca), d_pct_vs_base=pc(ca),
          low=round(min(cands.values())), high=round(max(cands.values())),
          range_k_only=[round(combo(.35, .5, BVPS, KT['hi'])), round(combo(.35, .5, BVPS, KT['lo']))],
          trigger_roe_q4_up_pct=trig_roe_up))
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(os.path.join(HERE, 'calc_agm_v2_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
