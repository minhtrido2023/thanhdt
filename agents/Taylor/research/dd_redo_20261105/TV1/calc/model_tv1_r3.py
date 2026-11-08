"""TV1 — DD redo VÒNG 3 (08/11/2026, job Taylor_20261108_142024). Áp TOP5_CORRECTIONS_20261108.md §TV1 sau khi KIỂM từng điểm.
Lõi = tv1_v2_core.py (không sửa; md5 khoá). Khung = model_tv1_r2.py; chỉ đổi:
  (1) Giá tham chiếu = đóng cửa 06/11/2026 (r3data/px_tv1_20261106.csv, tav2_bq.ticker, SQL r3data/px_tv1_r3.sql); CK tính lại trên cửa sổ mới.
  (2) r = 13,5% + 1,0×(lãi huy động 12T hiệu dụng 06/11 − 7,40%) — tính lại tại 2026-11-06.
  (3) HEADLINE: truy thu hồi tố 2022–26 RA KHỎI BASE (không có văn bản đòi; EVN trả ~949 suốt 2022–25 đã kiểm toán; HĐ sửa đổi 05/2018 là
      DỰ THẢO được EVN NQ 286 + Cục ĐTĐL 1374 chấp thuận, chưa thấy bản ký — README 13/10 dòng 17–31). Trọng số 0,10 trả về 'đúng 2027'.
      Trục thời điểm còn 2 chiều có cơ sở dữ liệu: đúng 2027 (lời lãnh đạo, KBSV) vs lùi 1–2 năm (mốc 2022 của dự thảo 2018 đã trôi ≥5 năm — quan sát được).
  (4) Biến thể song song: (S1) truy thu NHẤT QUÁN — chỉ trong nhánh PPA 340, P(truy thu|340)=0,10; (S2) giữ P(truy thu)=0,10 chung, dồn hết vào nhánh 340
      (P(truy thu|340)=0,50); (S3) r2 cơ học (nhân chéo độc lập) trên dữ liệu mới — để bridge; (S4) có cấm thầu p0,35; (S5) KTPL 10/15/25%.
  (5) Giá ngụ ý: PPA phẳng 2027+ làm tâm = giá (ở kỳ vọng tư vấn và ở tư vấn 11%); kiểm biên tư vấn lịch sử đúng cách (EBITM_P0 là TTM ⇒ dùng dòng Q4 × DT năm).
Chạy: $DNA_PYEXE -I model_tv1_r3.py → model_tv1_r3_out.json/.txt + LOCK_r3_md5.txt
"""
import contextlib, csv, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_common_g2r2"))
sys.path.insert(0, WC)
import ddr2 as g
import deposit_rate_vn as dep
with contextlib.redirect_stdout(io.StringIO()):
    import tv1_v2_core as c

ASOF = "2026-11-06"
PX_CSV = os.path.join(HERE, "r3data", "px_tv1_20261106.csv")
g.PX_CSV = PX_CSV                       # ddr2.px_rows đọc biến module tại lúc gọi
L = g.liquidity("TV1"); PX, PX_DATE = L["price"], L["price_date"]
assert PX_DATE == ASOF, PX_DATE
disc = L["ref_discount"]
_a = dep.effective_deposit_rate("2026-11-03"); _c = dep.effective_deposit_rate(ASOF)
r0 = round(0.135 + 1.0 * (_c["rate_pct"] - _a["rate_pct"]) / 100, 6)
R = dict(r=r0, anchor=dict(rate=_a["rate_pct"], date="2026-11-03", source=_a["rate_source"]),
         current=dict(rate=_c["rate_pct"], date=ASOF, source=_c["rate_source"], big4=_c["big4_rate_pct"], cctg=_c["cctg_rate_pct"]))
P_NOW = 949.0


def hydro(pk, q, timing, r, ktpl=c.KTPL, p_override=None):
    p = c.PRICE[pk] if p_override is None else p_override
    base = c.hydro_fcfe(p, q, ktpl=ktpl)
    if timing.startswith("delay"):
        n = int(timing[-1])
        cfs = c.hydro_fcfe(P_NOW, q, ktpl=ktpl)[:n] + base[n:]
    else:
        cfs = base
    v = c.pv_mid(cfs, r)
    if timing == "retro":
        v -= c.truy * (1 - c.TAX) / (1 + r)
    return v


def fn(ppa, consult, q, timing, wc, ban=None, r=None, ktpl=c.KTPL, p_override=None):
    rr = r0 if r is None else r
    v = hydro(ppa, q, timing, rr, ktpl, p_override) + c.consult(consult, ke=rr, wc=wc, shock=ban, ktpl=ktpl)[0] + c.BS
    return max(c.ps(v), 0.0)


PPA = [(k, k, c.PROB[k]) for k in c.PRICE]
CON = [(k, k, c.P_CON[k]) for k in c.SCN]
QAX = [(f"Q{x}", x, 1 / 3) for x in (175.0, c.Q_P50, 200.0)]
WCX = [("45%", 0.45, 1 / 3), ("49%", 0.49, 1 / 3), ("53%", 0.53, 1 / 3)]
TIM_H = [("2027", "base", 0.80), ("delay1", "delay1", 0.15), ("delay2", "delay2", 0.05)]
TIM_R2 = [("retro", "retro", 0.10), ("2027", "base", 0.70), ("delay1", "delay1", 0.15), ("delay2", "delay2", 0.05)]
AXES = dict(ppa=PPA, consult=CON, q=QAX, timing=TIM_H, wc=WCX)
AXES_BASIS = dict(
    ppa="giá ròng SB5 2027+ 949/600/520/440/340, xác suất 0,05/0,25/0,30/0,20/0,20 [UL] (SKEPTIC_BLIND B1); 340 = bậc DỰ THẢO HĐ sửa đổi 05/2018 "
        "(EVN NQ 286/NQ-HĐTV 06/08/2018 + Cục ĐTĐL 1374/ĐTĐL-GP 24/08/2018 chấp thuận; chưa thấy bản ký) — mức duy nhất có văn bản; 500–600 = lời lãnh đạo qua KBSV 17/04/2026, chưa kiểm bản gốc",
    consult="biên tư vấn 5/8/11/14%, xác suất 0,20/0,30/0,40/0,10 [UL] (SKEPTIC_BLIND B3)",
    q="sản lượng 175/187,5/200 GWh, đều — đối xứng quanh P50 dài hạn 181–187",
    timing="thời điểm áp bậc thấp: đúng 2027 p0,80 (lời lãnh đạo 'từ 2027', KBSV — chưa kiểm bản gốc) · lùi 1 năm p0,15 · lùi 2 năm p0,05 [UL] "
           "(cơ sở dữ liệu cho chiều lùi: mốc 01/01/2022 của dự thảo 2018 đã trôi ≥5 năm, giá ròng thực 2021–25 ≈ 870–950). Truy thu hồi tố RA KHỎI base (r3) → S1/S2",
    wc="vốn lưu động tư vấn 45/49/53% ΔDT (đo 45–53%), đều — hai chiều",
)
AXES_EXCLUDED = [
    dict(axis="truy thu bậc giá 2022–26 áp hồi tố (r2 có, p0,10 nhân chéo độc lập)",
         reason="r3 (TOP5_CORRECTIONS §TV1 đ.1–3, đã kiểm): không có văn bản đòi; EVN trả ~949 suốt 2022–25 (BCTC kiểm toán); HĐ 05/2018 là dự thảo được chấp thuận, chưa thấy bản ký; "
                "blind + core v2 đều xếp 'không vào tâm' ⇒ khoản lệch khỏi sổ không có cơ sở dữ liệu ⇒ độ nhạy S1/S2 (nhất quán: chỉ trong nhánh 340)"),
    dict(axis="cấm thầu EVN / khởi tố pháp nhân (vụ án 500kV mạch 3)", reason="vụ án ⇒ WARNING (luật user 27/09); báo song song S4: cấm 3 năm DT tư vấn −50% p0,35"),
    dict(axis="buộc nộp tiền 20/50/100 tỷ", reason="vụ án ⇒ WARNING; số ở §6"),
    dict(axis="điện mặt trời nổi 46 MWp", reason="chưa đầu tư ⇒ NPV=0 (luật 03/11), không có số cho cả hai chiều"),
    dict(axis="tỷ lệ KTPL", reason="đo 3 năm (r3): FY2023 30,93/75,64 = 40,9% · FY2024 17,24/87,50 = 19,7% · FY2025 30,10/150,20 = 20,0%; quỹ trích theo THÁNG LƯƠNG (1,5 tháng — BCTC FY25 TM18c), "
                                     "không theo % LN ⇒ khi LN giảm, % có xu hướng TĂNG. Giữ 20%; độ nhạy 10/15/25% ở S5"),
]


def grid(axes, **kw):
    return g.build_grid(axes, lambda **a: fn(**a, **kw))


outs = grid(AXES)
D = g.dist(outs, PX, disc)
lab = g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"])
central = fn("P3_520", "C_giua", c.Q_P50, "base", 0.49)
n_zero = sum(o["w"] for o in outs if o["v"] == 0.0)
br = dict(p10_ppa=g.branch_share(outs, "ppa", 0.10), p90_ppa=g.branch_share(outs, "ppa", 0.90),
          p10_consult=g.branch_share(outs, "consult", 0.10), p90_consult=g.branch_share(outs, "consult", 0.90))


def joint_grid(p_retro_340, other_tim=TIM_H, tim340_rest=None, **kw):
    """Truy thu CHỈ xảy ra trong nhánh PPA 340 (bậc 2018 ràng buộc ⇒ PPA tương lai = 340). Nhánh khác dùng other_tim."""
    out = []
    for pk, _, pp in PPA:
        if pk == "P5_340":
            rest = tim340_rest or other_tim
            tl = [("retro", "retro", p_retro_340)] + [(a, b, w * (1 - p_retro_340)) for a, b, w in rest]
        else:
            tl = other_tim
        sub = g.build_grid(dict(ppa=[(pk, pk, 1.0)], consult=CON, q=QAX, timing=tl, wc=WCX), lambda **a: fn(**a, **kw))
        for o in sub:
            o["w"] *= pp
        out += sub
    return out


S1 = joint_grid(0.10)                                   # nhất quán, P(truy thu|340)=0,10 ⇒ P chung 0,02
S2 = joint_grid(0.50)                                   # giữ P chung 0,10 ⇒ P(truy thu|340)=0,50
# biến thể skeptic: nhánh khác giữ timing r2 bỏ truy thu (0,70/0,15/0,05 chuẩn hoá) — để đối chiếu số skeptic
TIM_R2_NORETRO = [(a, b, w / 0.9) for a, b, w in TIM_R2[1:]]
S1k = joint_grid(0.10, other_tim=TIM_R2_NORETRO)
S2k = joint_grid(0.50, other_tim=TIM_R2_NORETRO)
S3 = grid(dict(AXES, timing=TIM_R2))                    # r2 cơ học trên dữ liệu mới
S4 = grid(dict(AXES, ban=[("khong", None, 0.65), ("cam3y_-50%", [0.5] * 3, 0.35)]))
S0 = grid(dict(AXES, timing=[("2027", "base", 1.0)]))   # không trục thời điểm
DS = {k: g.dist(v, PX, disc) for k, v in dict(S1_nhatquan_p340_010=S1, S2_nhatquan_p340_050=S2, S1_skeptic_timing=S1k, S2_skeptic_timing=S2k,
                                                 S3_r2_cohoc=S3, S4_cam_thau=S4, S0_khong_thoi_diem=S0).items()}
DS_br = dict(S2_p10_ppa=g.branch_share(S2, "ppa", 0.10), S2_p10_timing=g.branch_share(S2, "timing", 0.10),
             S3_p10_timing=g.branch_share(S3, "timing", 0.10))
KT = {f"{k:.0%}": g.dist(grid(AXES, ktpl=k), PX, disc)["center_post"] for k in (0.10, 0.15, 0.20, 0.25)}
sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = g.dist(grid(AXES, r=rr), PX, disc)["center_post"]
    sens_r[key] = dict(r=rr, post=e, pct=e / D["center_post"] - 1)


def implied_ppa(consult_axis):
    """PPA ròng phẳng 2027+ (mọi nhánh) sao cho tâm SAU CK = giá 06/11. Trục khác giữ headline."""
    lo, hi = 200.0, 1500.0
    for _ in range(60):
        m = (lo + hi) / 2
        e = g.dist(g.build_grid(dict(AXES, ppa=[("X", "P3_520", 1.0)], consult=consult_axis),
                                lambda **a: fn(**a, p_override=m)), PX, disc)["center_post"]
        lo, hi = (m, hi) if e < PX else (lo, m)
    return (lo + hi) / 2


imp = dict(ppa_at_consult_expect=implied_ppa(CON), ppa_at_consult_11pct=implied_ppa([("C_giua", "C_giua", 1.0)]),
           ppa_at_consult_14pct=implied_ppa([("C_cao", "C_cao", 1.0)]))

# Biên tư vấn lịch sử — cách ĐÚNG: EBITM_P0 là TTM ⇒ EBIT năm = EBITM_P0(Q4) × Σ DT 4 quý (đối chiếu core §B dùng Σ DT quý × EBITM_P0)
rows = list(csv.DictReader(open(os.path.join(HERE, "v2data", "bq_tv1_quarterly_2022_2025.csv"))))
rev_y, ebit_core, ebit_fix = {}, {}, {}
for rw in rows:
    y = int(rw["quarter"][:4]); rv = float(rw["Revenue_P0"]) / 1e9
    rev_y[y] = rev_y.get(y, 0) + rv; ebit_core[y] = ebit_core.get(y, 0) + rv * float(rw["EBITM_P0"])
    if rw["quarter"].endswith("Q4"):
        ebit_fix[y] = float(rw["EBITM_P0"])
MHX = {}
for y in (2022, 2023, 2024, 2025):
    ef = ebit_fix[y] * rev_y[y]
    hres = c.KQ25 if y == 2025 else c.Qh[y] * c.p_net25 / 1000 - c.om(y) - 38.0
    hdt = c.DT25 if y == 2025 else {2023: 214.59, 2024: 215.941}.get(y, c.Qh[y] * c.p_net25 / 1000 + (c.TN25 + c.Q25 * c.DVMTR / 1000) * c.Qh[y] / c.Q25)
    dtc = rev_y[y] - hdt
    MHX[str(y)] = dict(ebit_core=ebit_core[y], ebit_ttm_q4=ef, margin_core=((ebit_core[y] - hres) / dtc, (ebit_core[y] - hres + 8) / dtc),
                       margin_fix=((ef - hres) / dtc, (ef - hres + 8) / dtc))

EQ = 574.7; NP = 150.2 * (1 - c.KTPL); INT_Y = 198.6 * 0.05 * (1 - c.TAX); gg = 0.03
gordon_with = EQ * (NP / EQ - gg) / (r0 - gg) / c.SH * 1e9
cash_net = 198.6 - 129.9
gordon_without = ((EQ - cash_net) * ((NP - INT_Y) / (EQ - cash_net) - gg) / (r0 - gg) + cash_net) / c.SH * 1e9
KTPL_HIST = dict(FY2023=dict(ktpl=30.933659500, np=75.64, src="BCTC HN FY2025 kiểm toán TM18a (trích quỹ 2024 48,93 − ĐTPT 18,0); LNST 2023 = Σ NP_P0 BQ ticker_financial"),
                 FY2024=dict(ktpl=17.240, np=87.497357693, src="BCTC HN FY2025 TM17/18a/18c (16,91 KTPL + 0,33 quản lý); LNST 2024 kiểm toán 87,50"),
                 FY2025=dict(ktpl=30.100, np=150.197771310, src="BCTC HN H1/2026 TM22 tr.30"))
for v in KTPL_HIST.values():
    v["pct"] = v["ktpl"] / v["np"]

base_adj = [
    dict(item="tiền ròng điều chỉnh (−cổ tức phải trả −lãi vay cá nhân phải trả −quỹ KTPL mã 323 −KTPL sẽ trích 9T +LNST Q4 sau KTPL)", effect_dong_per_share=c.ps(c.BS),
         basis="nợ phải trả trên sổ + KTPL 20% đo được; LNST Q4 50 tỷ là ước lượng [UL]", source="BCTC HN Q3/2026 BCĐ (mã 323 = 40,708 tỷ); tv1_v2_core §C"),
    dict(item="quỹ KTPL 20% trên dòng tiền thuỷ điện + tư vấn", effect_dong_per_share=None,
         basis="đo 3 năm 40,9%/19,7%/20,0% (FY23/24/25); quỹ theo tháng lương", source="BCTC FY2025 TM17-18; H1/2026 TM22"),
    dict(item="truy thu bậc giá 2022–26", effect_dong_per_share=0.0, basis="RA KHỎI BASE r3 — không có văn bản đòi; HĐ 05/2018 là dự thảo", source="TOP5_CORRECTIONS_20261108 §TV1; README tv1_sb5_ppa_price_20261013 dòng 17–31"),
]
out = dict(ticker="TV1", round=3, asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L, dist=D, label=lab, w_floor_zero=n_zero,
           center_param=central, center_param_post=central * (1 - disc), branches=br, parallel=DS, parallel_branches=DS_br, ktpl_sens=KT, ktpl_hist=KTPL_HIST,
           sens_r=sens_r, implied=imp, margin_hist_check=MHX,
           gordon=dict(g=gg, with_interest=gordon_with, without_interest=gordon_without, note="LNST 2025 sau KTPL; lãi TG 5% × 198,6 (ước lượng); chưa trừ hạ bậc PPA ⇒ chỉ đối chiếu"),
           truy_thu_dcp=c.ps(-c.truy * (1 - c.TAX) / (1 + r0)), ppa_expect=sum(c.PRICE[k] * c.PROB[k] for k in c.PRICE),
           axes_included=[dict(axis=k_, values=[(a, b, p) for a, b, p in v], basis=AXES_BASIS[k_]) for k_, v in AXES.items()],
           axes_excluded=AXES_EXCLUDED, base_adjustments=base_adj)
json.dump(out, open(os.path.join(HERE, "model_tv1_r3_out.json"), "w"), ensure_ascii=False, indent=1, default=float)
f = g.fmt; P = D["P_post"]
lines = [f"TV1 r3 giá {f(PX)} ({PX_DATE}) | r {r0:.4f} (lãi 12T {R['current']['rate']} @{ASOF}, neo {R['anchor']['rate']}) | n kết cục {D['n']}",
         f"HEADLINE (không truy thu): tâm TRƯỚC {f(D['center_pre'])} SAU CK {f(D['center_post'])} | P50 SAU {f(P['p50'])} | tham số trung tâm SAU {f(central*(1-disc))}",
         "Kết cục SAU CK " + " ".join(f"{k_} {f(v)}" for k_, v in P.items()) + f" | min {f(D['min_post'])} max {f(D['max_post'])}",
         f"% trọng số dưới giá {D['pct_w_below_px']:.1%} | chạm sàn 0 {n_zero:.2%} | nhãn {lab} | giá/tâm {PX/D['center_post']-1:+.1%}",
         f"Nhánh quanh P10: PPA {br['p10_ppa']} tư vấn {br['p10_consult']} | quanh P90: PPA {br['p90_ppa']} tư vấn {br['p90_consult']}",
         f"CK @5 tỷ {disc:.2%} (ADV120 {L['adv120_med_ty']:.2f} tỷ; Q/ADV {L['ref_pct_adv120']:.0%}; vùng √: {L['ref_in_sqrt_zone']}) | ADV250 {L['adv250_med_ty']:.2f} → {L['ref_discount_adv250']:.2%} | ADV60 {L['adv60_med_ty']:.2f} → {L['ref_discount_adv60']:.2%} | sleeve 10/20/40tr " + "/".join(f"{v:.2%}" for v in L['sleeve_discount'].values())]
for k_, d_ in DS.items():
    lines.append(f"SONG SONG {k_}: tâm {f(d_['center_post'])} P10 {f(d_['P_post']['p10'])} P50 {f(d_['P_post']['p50'])} P90 {f(d_['P_post']['p90'])} | dưới giá {d_['pct_w_below_px']:.1%} | nhãn {g.label(PX, d_['P_post']['p10'], d_['P_post']['p90'])}")
lines += [f"Nhánh quanh P10: S2 PPA {DS_br['S2_p10_ppa']} timing {DS_br['S2_p10_timing']} | S3 timing {DS_br['S3_p10_timing']}",
          "KTPL (tâm SAU CK): " + " | ".join(f"{k_} {f(v)}" for k_, v in KT.items()),
          "KTPL lịch sử: " + " | ".join(f"{k_} {v['ktpl']:.2f}/{v['np']:.2f} = {v['pct']:.1%}" for k_, v in KTPL_HIST.items()),
          "Độ nhạy r (tâm SAU CK): " + " | ".join(f"{k_} {f(v['post'])} ({v['pct']:+.1%})" for k_, v in sens_r.items()),
          f"Giá ngụ ý (PPA phẳng 2027+ để tâm SAU CK = {f(PX)}): tư vấn kỳ vọng {imp['ppa_at_consult_expect']:.0f} | tư vấn 11% {imp['ppa_at_consult_11pct']:.0f} | tư vấn 14% {imp['ppa_at_consult_14pct']:.0f} đ/kWh (PPA kỳ vọng lưới {out['ppa_expect']:.0f})",
          "Biên tư vấn lịch sử core (ΣDTq×TTM) vs đúng (TTM Q4×DT năm): " + " | ".join(f"{y} {v['margin_core'][0]:+.0%}…{v['margin_core'][1]:+.0%} → {v['margin_fix'][0]:+.0%}…{v['margin_fix'][1]:+.0%}" for y, v in MHX.items()),
          f"Gordon g3% (trước CK): có lãi TG {f(gordon_with)} | không lãi TG {f(gordon_without)} | truy thu hồi tố đủ {f(out['truy_thu_dcp'])} đ/cp"]
open(os.path.join(HERE, "model_tv1_r3_out.txt"), "w").write("\n".join(lines) + "\n")
LOCK_FILES = [os.path.abspath(g.__file__), os.path.join(os.path.dirname(os.path.abspath(g.__file__)), "..", "_shared", "wpct.py"),
              os.path.join(os.path.dirname(os.path.abspath(g.__file__)), "..", "_common_g2", "ddg2.py"),
              PX_CSV, os.path.join(HERE, "r3data", "px_tv1_r3.sql"), os.path.abspath(__file__), os.path.join(HERE, "tv1_v2_core.py"),
              os.path.join(HERE, "v2data", "bq_tv1_quarterly_2022_2025.csv"),
              f"{WC}/deposit_rate_vn.py", f"{WC}/cctg_rate_vn.py", f"{WC}/data/deposit_rate_vn_events.csv", f"{WC}/data/cctg_rate_vn_events.csv"]
g.write_lock(os.path.join(HERE, "LOCK_r3_md5.txt"), [os.path.normpath(p) for p in LOCK_FILES], "TV1 r3")
print("\n".join(lines))
