"""TV2 — DD redo VÒNG 3 (08/11/2026, job Taylor_20261108_142016): áp đính chính fundamental-skeptic (TOP5_CORRECTIONS_20261108.md mục TV2).
Hàm giá trị giữ như r2 (calc/model_tv2_r2.py): (LNST bền × P/E nội tại (1 − g/ROE)/(r − g) − mất CMC)/N; 2 năm LNST trước khi áp trục độ bền.
ĐỔI so r2 (mỗi bước có cơ sở dữ liệu, đo trong chính file này từ fin_tv2_hist.csv / pxhist_tv2.csv / PDF BCTC HN Q3):
  Đ1  P/E khi ROE < r = 1/r (trả hết, không tái đầu tư) thay cho sàn max(...,0). Cơ sở: tỷ lệ chi trả DY/EY 2022Q4–2025Q3 = 0,88–1,27
      (BQ ticker_financial) — khi ROE thấp TV2 THỰC TẾ trả ~100% LN; phải trả cổ tức 67,97 tỷ tại 30/09/2026 (BCTC HN Q3 TM14).
  Đ2  nhánh 'sập' neo MỨC đáy quan sát = TB LNST TTM 2023Q1–2025Q3 (BQ) thay cho ×0,30 áp lên mọi kịch bản (×0,30 × 110 = 33 tỷ < min quan sát 53,0).
  Giá tham chiếu = đóng cửa 06/11/2026 (BQ tav2_bq.ticker, px_tv2_r3_20261106.csv); thanh khoản tính lại trên cửa sổ tới 06/11.
  CMC: phơi nhiễm 666,374 (TM 32.c, tr.36/38) + 188,638 (giá trị ghi sổ đầu tư LK, TM 2a tr.16/38) — đọc lại bằng render PyMuPDF.
Song song (không headline): C = P/E 1/r mọi nhánh (= RONIC=r ⇒ bản 'chặt-3c', user 08/11 chỉ cho là độ nhạy); trần P/E thị trường
  pha đỉnh LN 2017–21; đáy 53,0/74,6; trọng số 30/50/20 & 20/50/30; bỏ trục độ bền; r ±50/100bp.
Chạy: $DNA_PYEXE -I model_tv2_r3.py → model_tv2_r3_out.json/.txt + LOCK_r3_md5.txt
"""
import csv, json, os, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "_common_g2r2"))
import ddr2 as g   # noqa: E402

N = 67.526165
EQ = 19708 * N / 1000
CMC_EXPO_R2 = 666.374 + 188.6
CMC_EXPO = 666.374 + 188.638
TAX = 0.20
HOLD = 2
R = g.r_info(); r0 = R["r"]

# ---- dữ liệu lịch sử (BQ) ----
FIN = os.path.join(HERE, "fin_tv2_hist.csv"); PXH = os.path.join(HERE, "pxhist_tv2.csv")
fin = list(csv.DictReader(open(FIN)))
ttm = {r["quarter"]: float(r["NP_TTM"]) / 1e9 for r in fin}
payout = {r["quarter"]: float(r["DY"]) / float(r["EPS"]) for r in fin if "2022Q4" <= r["quarter"] <= "2025Q3"}
trough_q = [q for q in ttm if "2023Q1" <= q <= "2025Q3"]
TROUGH = st.mean(ttm[q] for q in trough_q); TROUGH_MIN = min(ttm[q] for q in trough_q); TROUGH_MAX = max(ttm[q] for q in trough_q)
pe_peak = [float(r["PE"]) for r in fin if "2017Q3" <= r["quarter"] <= "2021Q4"]
PE_PEAK_MED = st.median(pe_peak); PE_PEAK_MEAN = st.mean(pe_peak)
PE_CAP_SKEPTIC = 7.45   # trung vị pha LN đỉnh 2017–21 do REPORT_v3 01/11 dùng (skeptic CAO-1)
NP_PEAK = max(ttm[q] for q in ttm if "2017Q1" <= q <= "2021Q4")
pxh = list(csv.DictReader(open(PXH)))
MIN_PX_2022 = min(float(r["min_price"]) for r in pxh if int(r["y"]) >= 2022)
PB_MED_2325 = {r["y"]: float(r["pb_med"]) for r in pxh if r["y"] in ("2023", "2024", "2025")}

# ---- thanh khoản: r2 (04/11, control) và r3 (06/11) ----
L_r2 = g.liquidity("TV2")
g.PX_CSV = os.path.join(HERE, "px_tv2_r3_20261106.csv")
L = g.liquidity("TV2"); PX, PX_DATE = L["price"], L["price_date"]; disc = L["ref_discount"]
assert PX_DATE == "2026-11-06", PX_DATE


def pe(E, gg, r, pol, cap=None, flat=False):
    if flat:
        v = 1 / r                                   # RONIC = r ⇒ P/E = 1/r với mọi g
    elif pol and E / EQ < r:
        v = 1 / r                                   # Đ1: ROE < r ⇒ trả hết (quan sát 2022Q4–25Q3)
    else:
        v = max((1 - gg / (E / EQ)) / (r - gg), 0.0)   # r2: sàn 0 (chỉ còn ở control/bridge)
    return min(v, cap) if cap else v


def make_fn(pol=True, anchor=TROUGH, cap=None, flat=False, expo=CMC_EXPO):
    def fn(scen, mult, gg, cmc, persist, r=None):
        rr = r0 if r is None else r
        E = scen * mult
        if persist == 1.0:
            v = E * pe(E, gg, rr, pol, cap, flat)
        else:
            if persist == "L":
                E2 = min(E, anchor)                  # Đ2: neo mức đáy quan sát
            else:
                E2 = E * persist                     # r2: tỷ lệ
            ann = sum(E / (1 + rr) ** (t + 1) for t in range(HOLD))
            v = ann + E2 * pe(E2, gg, rr, pol, cap, flat) / (1 + rr) ** HOLD
        v -= cmc * expo * (1 - TAX)
        return max(v / N * 1000, 0.0)
    return fn


SCEN = [("tich_cuc", 250.0, 0.25), ("co_so", 177.5, 0.50), ("tieu_cuc", 110.0, 0.25)]
BASE = dict(
    scen=SCEN,
    mult=[("x0.9", 0.9, 1 / 3), ("x1", 1.0, 1 / 3), ("x1.1", 1.1, 1 / 3)],
    gg=[("g3", 0.03, 1 / 3), ("g4", 0.04, 1 / 3), ("g5", 0.05, 1 / 3)],
    cmc=[("0%", 0.0, 0.45), ("15%", 0.15, 0.30), ("30%", 0.30, 0.15), ("50%", 0.50, 0.10)],
)
PERSIST_R2 = [("sap70%", 0.30, 0.25), ("ben", 1.0, 0.50), ("+30%", 1.30, 0.25)]
PERSIST_R3 = [("sap_neo_day", "L", 0.25), ("ben", 1.0, 0.50), ("+30%", 1.30, 0.25)]
AX_R2 = dict(BASE, persist=PERSIST_R2)
AX = dict(BASE, persist=PERSIST_R3)


def run(axes, fn, liq=None):
    lq = liq or L
    return g.dist(g.build_grid(axes, fn), lq["price"], lq["ref_discount"])


def brief(D):
    P = D["P_post"]
    return dict(center=D["center_post"], p10=P["p10"], p50=P["p50"], p90=P["p90"], below=D["pct_w_below_px"], min=D["min_post"])


# ---- control r2 (giá 04/11) phải tái lập 15.832 ----
fn_r2 = make_fn(pol=False, expo=CMC_EXPO_R2)
D_ctrl = run(AX_R2, fn_r2, L_r2)
assert round(D_ctrl["center_post"]) == 15832 and round(D_ctrl["P_post"]["p10"]) == 2726, (D_ctrl["center_post"], D_ctrl["P_post"]["p10"])

# ---- bridge r2 → r3 ----
D_b1 = run(AX_R2, fn_r2)                                    # giá/thanh khoản 06/11
D_b2 = run(AX_R2, make_fn(pol=False))                       # CMC 188,638 (đọc lại PDF)
D_A = run(AX_R2, make_fn(pol=True))                         # Đ1 (= biến thể A skeptic)
outs = g.build_grid(AX, make_fn(pol=True))                  # Đ2 ⇒ HEADLINE (= B)
D = g.dist(outs, PX, disc)
D_C = run(AX, make_fn(pol=True, flat=True))                 # C: P/E 1/r mọi nhánh
lab = g.label(PX, D["P_post"]["p10"], D["P_post"]["p90"])
lab_C = g.label(PX, D_C["P_post"]["p10"], D_C["P_post"]["p90"])
fnB = make_fn(pol=True)
central = fnB(177.5, 1.0, 0.04, 0.0, 1.0)
p10_s = g.branch_share(outs, "scen", 0.10); p90_s = g.branch_share(outs, "scen", 0.90)
p10_p = g.branch_share(outs, "persist", 0.10); p90_p = g.branch_share(outs, "persist", 0.90)

par = dict(
    A_payout_only=brief(D_A),
    C_pe_1_over_r_all=dict(brief(D_C), label=lab_C),
    cap_pe_745=brief(run(AX, make_fn(pol=True, cap=PE_CAP_SKEPTIC))),
    cap_pe_peak_median=dict(brief(run(AX, make_fn(pol=True, cap=PE_PEAK_MED))), cap=PE_PEAK_MED),
    trough_min=brief(run(AX, make_fn(pol=True, anchor=TROUGH_MIN))),
    trough_max=brief(run(AX, make_fn(pol=True, anchor=TROUGH_MAX))),
    w_30_50_20=brief(run(dict(AX, scen=[("tich_cuc", 250.0, 0.30), ("co_so", 177.5, 0.50), ("tieu_cuc", 110.0, 0.20)]), fnB)),
    w_20_50_30=brief(run(dict(AX, scen=[("tich_cuc", 250.0, 0.20), ("co_so", 177.5, 0.50), ("tieu_cuc", 110.0, 0.30)]), fnB)),
    no_persist_axis=brief(run(dict(AX, persist=[("ben", 1.0, 1.0)]), fnB)),
)
sens_r = {}
for key, rr in g.r_grid(r0).items():
    e = g.dist(g.build_grid(AX, lambda **kw: fnB(r=rr, **kw)), PX, disc)["center_post"]
    sens_r[key] = dict(r=rr, post=e, pct=e / D["center_post"] - 1)

# ---- giá ngụ ý: LNST vĩnh viễn (bền, g 4%, CMC 0, P/E nội tại) để giá trị sau CK = giá ----
def implied_E(gg=0.04, cmc=0.0, target=PX / (1 - disc)):
    lo, hi = 10.0, 2000.0
    for _ in range(200):
        m = (lo + hi) / 2
        if fnB(m, 1.0, gg, cmc, 1.0) < target:
            lo = m
        else:
            hi = m
    return m
E_imp = implied_E(); E_imp_cmcexp = implied_E(cmc=sum(v * p for _, v, p in BASE["cmc"]))
E_imp_flat = PX / (1 - disc) * N / 1000 * r0            # nếu P/E = 1/r (RONIC=r)
FLOAT_SHARE = 0.44
implied = dict(np_perp=E_imp, roe=E_imp / EQ, pe=pe(E_imp, 0.04, r0, True), float_part=E_imp * FLOAT_SHARE,
               np_perp_with_expected_cmc_loss=E_imp_cmcexp, np_perp_if_pe_1_over_r=E_imp_flat, roe_if_pe_1_over_r=E_imp_flat / EQ,
               note="g 4%, CMC 0%, LN bền mãi; 44% = tỷ trọng TC ròng trong LNTT 9T/26 (REPORT_r2 §7)")

gg = 0.04; NP26 = 229.5
gordon_with = EQ * (NP26 / EQ - gg) / (r0 - gg) / N * 1000
gordon_without = EQ * (NP26 * (1 - 0.44) / EQ - gg) / (r0 - gg) / N * 1000
gordon_without_payout = NP26 * (1 - 0.44) / r0 / N * 1000   # ROE<r ⇒ 1/r (Đ1)

sleeve_center = D["center_pre"] * (1 - L["sleeve_max_discount"])
bridge = [
    dict(step="r2 control (giá 04/11, CK 04/11)", center=D_ctrl["center_post"], p10=D_ctrl["P_post"]["p10"], p90=D_ctrl["P_post"]["p90"]),
    dict(step="giá/CK cửa sổ tới 06/11", center=D_b1["center_post"], p10=D_b1["P_post"]["p10"], p90=D_b1["P_post"]["p90"]),
    dict(step="CMC đầu tư 188,6→188,638 (PDF)", center=D_b2["center_post"], p10=D_b2["P_post"]["p10"], p90=D_b2["P_post"]["p90"]),
    dict(step="Đ1 P/E=1/r khi ROE<r (A)", center=D_A["center_post"], p10=D_A["P_post"]["p10"], p90=D_A["P_post"]["p90"]),
    dict(step="Đ2 sập neo mức đáy TB 2023Q1–25Q3 (B, headline)", center=D["center_post"], p10=D["P_post"]["p10"], p90=D["P_post"]["p90"]),
]
data_checks = dict(payout_2022Q4_2025Q3={k: round(v, 3) for k, v in payout.items()}, trough_mean=TROUGH, trough_min=TROUGH_MIN,
                   trough_max=TROUGH_MAX, trough_quarters=trough_q, pe_peak_2017Q3_2021Q4_median=PE_PEAK_MED,
                   pe_peak_mean=PE_PEAK_MEAN, np_ttm_peak_2017_21=NP_PEAK, min_price_since_2022=MIN_PX_2022,
                   pb_median_2023_25=PB_MED_2325, up_branch_max_np=250 * 1.1 * 1.3,
                   up_branch_vs_peak_note=f"nhánh +30% cao nhất {250*1.1*1.3:.1f} tỷ vs đỉnh TTM 2017–21 {NP_PEAK:.1f} tỷ danh nghĩa; đỉnh ×1,04^8 (2021→2029) = {NP_PEAK*1.04**8:.1f} ⇒ trong dải, không cần neo trên")
out = dict(ticker="TV2", round="r3", asof_price_date=PX_DATE, price=PX, r=r0, r_info=R, liq=L, dist=D, label=lab,
           center_param=central, center_param_post=central * (1 - disc), p10_scen_branch=p10_s, p90_scen_branch=p90_s,
           p10_persist_branch=p10_p, p90_persist_branch=p90_p, parallel=par, sens_r=sens_r, implied=implied, bridge=bridge,
           data_checks=data_checks, sleeve_center=sleeve_center, cmc_expo=CMC_EXPO,
           gordon=dict(g=gg, np2026e=NP26, with_interest=gordon_with, without_interest_r2_formula=gordon_without,
                       without_interest_payout=gordon_without_payout))
json.dump(out, open(os.path.join(HERE, "model_tv2_r3_out.json"), "w"), ensure_ascii=False, indent=1, default=float)

f = g.fmt; P = D["P_post"]
def row(k, b):
    return f"  {k}: tâm {f(b['center'])} P10 {f(b['p10'])} P50 {f(b['p50'])} P90 {f(b['p90'])} | dưới giá {b['below']:.1%}" + (f" | {b['label']}" if 'label' in b else "")
lines = [f"TV2 r3 giá {f(PX)} ({PX_DATE}) | r {r0:.4f} | n kết cục {D['n']} | CMC phơi nhiễm {CMC_EXPO:.3f} tỷ",
         f"KIỂM DỮ LIỆU: chi trả DY/EY 2022Q4–25Q3 {min(payout.values()):.2f}–{max(payout.values()):.2f} | đáy LNST TTM 2023Q1–25Q3 TB {TROUGH:.1f} (min {TROUGH_MIN:.1f} max {TROUGH_MAX:.1f}) | P/E thị trường 2017Q3–21Q4 trung vị {PE_PEAK_MED:.2f} TB {PE_PEAK_MEAN:.2f} | giá thấp nhất từ 2022 {f(MIN_PX_2022)} | P/B trung vị 2023/24/25 " + "/".join(f"{v:.2f}" for v in PB_MED_2325.values()),
         "BRIDGE: " + " → ".join(f"{b['step']}: {f(b['center'])} [P10 {f(b['p10'])}, P90 {f(b['p90'])}]" for b in bridge),
         f"HEADLINE (B) tâm TRƯỚC {f(D['center_pre'])} SAU CK {f(D['center_post'])} | P50 {f(P['p50'])} | tham số trung tâm SAU {f(central*(1-disc))}",
         "Kết cục SAU CK " + " ".join(f"{k_} {f(v)}" for k_, v in P.items()) + f" | min {f(D['min_post'])} max {f(D['max_post'])}",
         f"% trọng số dưới giá {D['pct_w_below_px']:.1%} | nhãn {lab} | giá/tâm {PX/D['center_post']-1:+.1%} | giá/P90 {PX/P['p90']-1:+.1%}",
         f"Quanh P10 kịch bản {p10_s} độ bền {p10_p} | quanh P90 kịch bản {p90_s} độ bền {p90_p}",
         f"CK @5 tỷ {disc:.2%} (ADV120 {L['adv120_med_ty']:.2f} tỷ; Q/ADV {L['ref_pct_adv120']:.0%}; vùng √ {L['ref_in_sqrt_zone']}) | ADV250 {L['adv250_med_ty']:.2f} → {L['ref_discount_adv250']:.2%} | ADV60 {L['adv60_med_ty']:.2f} → {L['ref_discount_adv60']:.2%} | sleeve 10/20/40tr " + "/".join(f"{v:.2%}" for v in L['sleeve_discount'].values()) + f" ⇒ tâm cỡ sleeve {f(sleeve_center)}",
         "SONG SONG:"] + [row(k, b) for k, b in par.items()] + [
         "Độ nhạy r (tâm SAU CK): " + " | ".join(f"{k_} {f(v['post'])} ({v['pct']:+.1%})" for k_, v in sens_r.items()),
         f"GIÁ NGỤ Ý (g4, CMC0, bền mãi): LNST {E_imp:.1f} tỷ (ROE {E_imp/EQ:.1%}, P/E {implied['pe']:.2f}; phần lãi float ~44% = {E_imp*FLOAT_SHARE:.1f}) | kèm mất CMC kỳ vọng: {E_imp_cmcexp:.1f} | nếu P/E=1/r: {E_imp_flat:.1f} (ROE {E_imp_flat/EQ:.1%})",
         f"Gordon g4% (trước CK, LNST 2026E 229,5 ước lượng): có lãi TG {f(gordon_with)} | không lãi TG công thức r2 {f(gordon_without)} | không lãi TG + Đ1 (1/r) {f(gordon_without_payout)}"]
open(os.path.join(HERE, "model_tv2_r3_out.txt"), "w").write("\n".join(lines) + "\n")
files = [os.path.join(ROOT, "_common_g2r2", "ddr2.py"), os.path.join(ROOT, "_common_g2r2", "px_g2r2_20261104.csv"),
         os.path.join(ROOT, "_common_g2r2", "px_g2r2.sql"), g.PX_CSV, os.path.join(HERE, "px_tv2_r3.sql"), FIN,
         os.path.join(HERE, "fin_tv2_hist.sql"), PXH, os.path.join(HERE, "pxhist_tv2.sql"),
         os.path.join(ROOT, "_shared", "wpct.py"), os.path.join(ROOT, "_common_g2", "ddg2.py"),
         "/home/trido/thanhdt/WorkingClaude/deposit_rate_vn.py", "/home/trido/thanhdt/WorkingClaude/cctg_rate_vn.py",
         "/home/trido/thanhdt/WorkingClaude/data/deposit_rate_vn_events.csv", "/home/trido/thanhdt/WorkingClaude/data/cctg_rate_vn_events.csv",
         "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_TV2_20261101/src/q3_hopnhat.pdf",
         os.path.abspath(__file__)]
g.write_lock(os.path.join(HERE, "LOCK_r3_md5.txt"), files, "TV2 r3")
print("\n".join(lines))
