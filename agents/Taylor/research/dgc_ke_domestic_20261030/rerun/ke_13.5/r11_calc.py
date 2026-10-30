"""r11 (job Taylor_20261029_131656): Nghi Sơn GĐ1 dựng từ dưới lên + tornado động lực giá trị. Không sửa model.py (override SCN tạm thời như r10).
python3 r11_calc.py  (cần model.py + data/bq_*_20261029.csv cùng thư mục). Đơn vị tỷ đồng trừ khi ghi khác. [UL] = ước lượng, không có nguồn trực tiếp.
Nguồn công suất: NQ HĐQT 34/2026/NQ-HĐQT 15/10/2026 (đọc nguyên văn ảnh PDF). Giá xút/P4: BQ tav2_bq.commodity_prices (SunSirs) đến 28/10/2026."""
import os, copy, pandas as pd, model as M
H = os.path.dirname(os.path.abspath(__file__)); o = []
def P(*a): o.append(" ".join(str(x) for x in a)); print(*a)
pd.set_option("display.width", 250)
A7, B7 = M.per_scn(M.CFG_A7)[0], M.per_scn(M.CFG_B7)[0]; P("tái lập r10: A7", A7, "B7", B7)
SH, KE = M.SH, M.ke()
SCN0 = copy.deepcopy(M.SCN)

def run_ns(ns, cfg):
    """ns = {scn: (ns_np[2027,2028], ns_steady)} ; trả per_scn(cfg) rồi khôi phục SCN."""
    try:
        for k, (npv, st) in ns.items(): M.SCN[k]["ns_np"], M.SCN[k]["ns_steady"] = list(npv), st
        return M.per_scn(cfg)
    finally:
        M.SCN.clear(); M.SCN.update(copy.deepcopy(SCN0))

# ---------------- A3: Nghi Sơn đang nằm trong A7/B7 bao nhiêu
zero = {k: ([0, 0], 0) for k in M.SCN}
a0, b0 = run_ns(zero, M.CFG_A7), run_ns(zero, M.CFG_B7)
r = M.per_scn(M.CFG_A7)
ns_left = 2400 - 1408.8
rows = []
for k in ("thuan", "coso", "nghich"):
    rows.append(dict(scn=k, ns_np_2027_28=SCN0[k]["ns_np"], ns_steady=SCN0[k]["ns_steady"], blend_A7=r[{"thuan": 1, "coso": 2, "nghich": 3}[k]],
                     blend_A7_ns_zero=a0[{"thuan": 1, "coso": 2, "nghich": 3}[k]]))
a3 = pd.DataFrame(rows); a3["ns_contrib_ps"] = a3.blend_A7 - a3.blend_A7_ns_zero
a3.to_csv(f"{H}/out_r11_A3_ns_in_model.csv", index=False)
P("\nA3 — phần LN hoạt động Nghi Sơn trong A7 (capex còn lại %.1f tỷ = %d đ/cp VẪN bị trừ ở cả hai cột):\n" % (ns_left, round(ns_left * 1000 / SH)), a3.to_string(index=False))
P("A7 không có LN Nghi Sơn:", a0[0], "(Δ", A7 - a0[0], ") ; B7:", b0[0], "(Δ", B7 - b0[0], ")")

# ---------------- A2: kinh tế GĐ1 từ dưới lên
cs = pd.read_csv(f"{H}/data/bq_caustic_soda_sunsirs_20261029.csv", parse_dates=["observation_date"])
CNY = 26_300 / 7.10 / 1e6            # tr VND / CNY [UL: FX model 26.300 VND/USD ; 7,10 CNY/USD]
NAOH_LAST = float(cs.value.iloc[-1]) / 0.32 * CNY          # SunSirs lỏng 32% (giả định nồng độ chuỗi prodetail-368 [UL]) → quy 100%
NAOH_3Y = float(cs[cs.observation_date >= "2023-10-01"].value.mean()) / 0.32 * CNY
NAOH_MAX_Q = float(cs.groupby(cs.observation_date.dt.to_period("Q")).value.mean().max()) / 0.32 * CNY
P4_LAST = 28229.33 * CNY            # BQ yellow_phosphorus SunSirs 28/10/2026 (tr VND/t)
P("\nXút quy 100%% (tr/t, TQ nội địa): cuối 28/10 %.2f ; TB 3 năm %.2f ; quý cao nhất %.2f ; P4 TQ %.1f tr/t" % (NAOH_LAST, NAOH_3Y, NAOH_MAX_Q, P4_LAST))
CAP = dict(naoh=50, hcl=15, hcl_by=75, pac=30, javen=30, bleach=20, cl2=5, chlb=1, cacl2=10, h3po3=10)   # nghìn t/năm [NQ 34/2026]
S = {  # giá tr VND/t ; chi phí ; tải
    "thap": dict(px=dict(naoh=NAOH_LAST, hcl=0.5, pac=5.5, javen=2.0, bleach=10, cl2=0.0, chlb=50, cacl2=1.5, h3po3=25), hcl_by_sold=0.0,
                 kwh=2.4, tariff=2300, salt=1.6 * 1.2, oth_mat=0.45, p4_factor=1.0, fixed=200, load=[0.40, 0.55, 0.65, 0.70]),
    "giua": dict(px=dict(naoh=NAOH_3Y * 1.15, hcl=1.0, pac=6.5, javen=3.5, bleach=15, cl2=1.5, chlb=80, cacl2=2.5, h3po3=35), hcl_by_sold=0.3,
                 kwh=2.4, tariff=2100, salt=1.6 * 1.0, oth_mat=0.35, p4_factor=1.0, fixed=150, load=[0.65, 0.70, 0.80, 0.85]),
    "cao": dict(px=dict(naoh=NAOH_MAX_Q, hcl=1.5, pac=7.5, javen=4.0, bleach=17, cl2=3.0, chlb=90, cacl2=3.5, h3po3=40), hcl_by_sold=0.6,
                kwh=2.4, tariff=2000, salt=1.6 * 0.8, oth_mat=0.25, p4_factor=1.0, fixed=130, load=[0.70, 0.85, 0.90, 0.90]),
}
P4_PER_T = 4 * 30.97 / 4 / 82.0      # t P / t H3PO3 = 0,378 (stoichiometry P4→PCl3→H3PO3); P4 tính giá cơ hội = giá TQ (DGC bán được P4)
DA, CAPEX, MAINT = 2400 / 15, 2400, 36   # KH 15 năm [dispatch] ; duy tu 1,5%/năm capex [UL]

def project(sk, tax):
    s = S[sk]; out = []
    for i, y in enumerate(range(2027, 2031)):
        L = s["load"][i]; q = {k: v * L for k, v in CAP.items()}
        run_p = s["px"]["h3po3"] >= P4_PER_T * P4_LAST * s["p4_factor"]   # luật vận hành: không chạy dây chuyền P nếu thua bán P4 thẳng
        if not run_p: q["h3po3"] = q["hcl_by"] = 0.0
        rev_items = {k: q[k] * s["px"][k] for k in ("naoh", "hcl", "pac", "javen", "bleach", "cl2", "chlb", "cacl2", "h3po3")}
        rev_items["hcl_by"] = q["hcl_by"] * s["hcl_by_sold"] * s["px"]["hcl"]
        rev = sum(rev_items.values())
        ecu = q["naoh"] * (s["kwh"] * s["tariff"] / 1000 + s["salt"])                        # điện + muối cho chuỗi xút-clo (tr VND × nghìn t = tỷ)
        mat = s["oth_mat"] * (rev_items["pac"] + rev_items["javen"] + rev_items["bleach"] + rev_items["chlb"] + rev_items["cacl2"])
        p4 = q["h3po3"] * P4_PER_T * P4_LAST * s["p4_factor"]
        ebitda = rev - ecu - mat - p4 - s["fixed"]
        ebit = ebitda - DA; npat = ebit - max(ebit, 0) * tax
        out.append(dict(scn=sk, tax=tax, year=y, load=L, rev=round(rev), rev_naoh=round(rev_items["naoh"]), rev_h3po3=round(rev_items["h3po3"]),
                        cost_power_salt=round(ecu), cost_other_mat=round(mat), cost_p4=round(p4), h3po3_line_margin=round(rev_items["h3po3"] - p4),
                        fixed=s["fixed"], ebitda=round(ebitda), ebitda_m=round(ebitda / rev, 3), da=round(DA), ebit=round(ebit), npat=round(npat),
                        roic_on_2400=round(ebit * (1 - tax) / CAPEX, 3), p_line_run=run_p, npm=round(npat / rev, 3)))
    return out

pr = pd.DataFrame([r_ for sk in S for tax in (0.20, 0.0) for r_ in project(sk, tax)])
pr.to_csv(f"{H}/out_r11_A2_nghison_pnl.csv", index=False)
P("\nA2 — P&L GĐ1 (thuế 20% mặc định; 0% = nếu được miễn ưu đãi [UL, chưa xác minh]):\n",
  pr[["scn", "tax", "year", "load", "rev", "rev_naoh", "cost_power_salt", "cost_other_mat", "cost_p4", "h3po3_line_margin", "ebitda", "ebitda_m", "ebit", "npat", "npm", "roic_on_2400", "p_line_run"]].to_string(index=False))
CSVq = pd.read_csv(f"{H}/data/bq_csv_quarters_20261029.csv"); CSVq["y"] = CSVq.quarter.str[:4]; CSVq["gp"] = CSVq.rev_ty * CSVq.gpm
ca = CSVq.groupby("y").agg(rev=("rev_ty", "sum"), gp=("gp", "sum"), np=("np_ty", "sum")); ca["gpm"] = (ca.gp / ca.rev).round(3); ca["npm"] = (ca.np / ca.rev).round(3)
ca.round(1).to_csv(f"{H}/out_r11_csv_comp.csv"); P("\nComp CSV (BQ ticker_financial; 2026 = 2 quý):\n", ca.round(3).to_string())
# rev ở 100% tải (đối chiếu neo CTCK)
for sk, s in S.items():
    full = sum(CAP[k] * s["px"][k] for k in s["px"]) + CAP["hcl_by"] * s["hcl_by_sold"] * s["px"]["hcl"]
    P(f"  {sk}: doanh thu @100% tải = {full:.0f} tỷ ; xút {CAP['naoh'] * s['px']['naoh']:.0f} ; giá xút {s['px']['naoh']:.2f} tr/t")

# đối chiếu comp: doanh thu từ dưới lên × NPM CSV (min / trung vị / max năm 2021-2025, BQ) — KHÔNG dùng cấu trúc chi phí [UL] của A2
npm_c = ca.loc[[str(y) for y in range(2021, 2026)], "npm"]
cmp_ = [dict(scn=sk, year=y, rev=int(pr[(pr.scn == sk) & (pr.tax == 0.2) & (pr.year == y)].rev.iloc[0]),
             npat_csv_min=round(pr[(pr.scn == sk) & (pr.tax == 0.2) & (pr.year == y)].rev.iloc[0] * npm_c.min()),
             npat_csv_med=round(pr[(pr.scn == sk) & (pr.tax == 0.2) & (pr.year == y)].rev.iloc[0] * npm_c.median()),
             npat_csv_max=round(pr[(pr.scn == sk) & (pr.tax == 0.2) & (pr.year == y)].rev.iloc[0] * npm_c.max()),
             npat_bottom_up=int(pr[(pr.scn == sk) & (pr.tax == 0.2) & (pr.year == y)].npat.iloc[0])) for sk in S for y in (2027, 2028, 2030)]
cmp_ = pd.DataFrame(cmp_); cmp_.to_csv(f"{H}/out_r11_A2_comp_anchor.csv", index=False)
P("\nĐối chiếu: doanh thu × NPM CSV 2021-25 (min %.3f / tv %.3f / max %.3f) vs từ dưới lên (thuế 20%%):\n" % (npm_c.min(), npm_c.median(), npm_c.max()), cmp_.to_string(index=False))

def dcf(sk, tax, life_end=2041, terminal=False):
    """FCF dự án = EBITDA − thuế − duy tu; 2031+ = 2030 phẳng; capex còn lại trả t=0,3 (Q4/26–2027). t_2027 = 0,68 như model."""
    d = pr[(pr.scn == sk) & (pr.tax == tax)].set_index("year")
    pv = -ns_left / (1 + KE) ** 0.3; pay, cum, paid = None, 0.0, None
    for j, y in enumerate(range(2027, life_end + 1)):
        e = d.loc[min(y, 2030)]; f = e.ebitda - max(e.ebit, 0) * tax - MAINT
        if y > 2030 and f <= 0: f = 0.0                 # tạm dừng nếu dòng tiền âm kéo dài [giả định]
        pv += f / (1 + KE) ** (0.68 + j); cum += f
        if paid is None and cum >= CAPEX: paid = y
    if terminal:
        pv += f / KE / (1 + KE) ** (0.68 + j)
    return pv, paid

rows = []
for sk in S:
    for tax in (0.20, 0.0):
        d = pr[(pr.scn == sk) & (pr.tax == tax)].set_index("year")
        v15, pay = dcf(sk, tax); vT, _ = dcf(sk, tax, terminal=True)
        rows.append(dict(scn=sk, tax=tax, npat_2027=d.loc[2027, "npat"], npat_2028=d.loc[2028, "npat"], npat_2030=d.loc[2030, "npat"],
                         roic_2030=d.loc[2030, "roic_on_2400"], payback_year=pay or ">2041",
                         npv_fwd_15y=round(v15), npv_fwd_15y_ps=round(v15 * 1000 / SH), npv_fwd_perp_ps=round(vT * 1000 / SH),
                         pct_of_px_32900=round(v15 * 1000 / SH / 32900, 3)))
ev = pd.DataFrame(rows); ev.to_csv(f"{H}/out_r11_A2_nghison_value.csv", index=False)
P("\nA2 — giá trị GĐ1 (NPV từ 29/10/2026, ke %.3f, ĐÃ trừ capex còn lại %.1f; 15 năm không terminal / có terminal):\n" % (KE, ns_left), ev.to_string(index=False))

# ---------------- D: thay ns_np/ns_steady trong model bằng kết quả A2 (thuế 20%) ; thấp→nghịch, giữa→cơ sở, cao→thuận
def steady(v, tax):
    e = pr[(pr.scn == v) & (pr.tax == tax) & (pr.year == 2030)].iloc[0]
    return int(e.npat) if e.ebitda > 0 else 0      # EBITDA ≤ 0 kéo dài ⇒ giả định tạm dừng (giá trị vận hành 0) [giả định]
mp = {"nghich": "thap", "coso": "giua", "thuan": "cao"}
ns_new = {k: ([int(pr[(pr.scn == v) & (pr.tax == 0.2) & (pr.year == y)].npat.iloc[0]) for y in (2027, 2028)],
              steady(v, 0.2)) for k, v in mp.items()}
a11, b11 = run_ns(ns_new, M.CFG_A7), run_ns(ns_new, M.CFG_B7)
ns_new0 = {k: ([int(pr[(pr.scn == v) & (pr.tax == 0.0) & (pr.year == y)].npat.iloc[0]) for y in (2027, 2028)],
               steady(v, 0.0)) for k, v in mp.items()}
a11z, b11z = run_ns(ns_new0, M.CFG_A7), run_ns(ns_new0, M.CFG_B7)
dD = pd.DataFrame([dict(case="r10 (ns_np model cũ)", A7=A7, B7=B7, ns=str({k: (SCN0[k]["ns_np"], SCN0[k]["ns_steady"]) for k in SCN0})),
                   dict(case="LN Nghi Sơn = 0 (chỉ trừ capex còn lại)", A7=a0[0], B7=b0[0], ns="0"),
                   dict(case="r11 từ dưới lên, thuế 20%", A7=a11[0], B7=b11[0], ns=str(ns_new)),
                   dict(case="r11 từ dưới lên, thuế 0% [UL ưu đãi]", A7=a11z[0], B7=b11z[0], ns=str(ns_new0))])
dD["dA7_vs_r10"] = dD.A7 - A7; dD["dB7_vs_r10"] = dD.B7 - B7
dD.to_csv(f"{H}/out_r11_D_band.csv", index=False); P("\nD — dải A7/B7:\n", dD.to_string(index=False))
P("theo kịch bản (A7 r10 → r11 thuế 20%):", {k: (r[i], a11[i]) for k, i in (("thuan", 1), ("coso", 2), ("nghich", 3))})

# ---------------- B: tornado (đ/cp)
nc = 9761.2 - 1391.0
ps = lambda x: round(x * 1000 / SH)
fg = pd.read_csv(f"{H}/out_r10_final_grid.csv")
lo_grid, hi_grid = fg.A7.min(), fg.A7.max()
torn = pd.DataFrame([
    dict(driver="(2) Biên gộp 2027-28 (giá P4/DAP, lưu huỳnh/NH3, quặng): nền r4 16,5/17,5% ↔ R2 19,5/20,7%", lo=32399, hi=36880, evidence="BCTC 9T thực (biên 20,7%) vs r4; 1pp ≈ 1.420 đ/cp [r9]", src="out_r10_final_grid.csv"),
    dict(driver="(3) Nguồn quặng: khai trường 25/19B mở lại (B7) vs không (A7)", lo=A7, hi=B7, evidence="khai trường 25 tạm dừng phục vụ điều tra; mở lại chưa có quyết định", src="model.py CFG_A7/B7"),
    dict(driver="(1) Tiền ròng 8.370 tỷ: haircut pháp lý 29% (nghịch) ↔ 3% (thuận) trên toàn bộ tiền ròng", lo=-ps(nc * 0.29), hi=-ps(nc * 0.03), evidence="BCTC 30/09: tiền+gửi 9.761,2, vay 1.391,0; haircut [UL]", src="model.py HC_LEGAL"),
    dict(driver="(5) Pháp lý: haircut tiền trong model (đã ở dòng 1) — phạt/khắc phục/đình chỉ KHÔNG có trần, chưa định lượng được", lo=None, hi=None, evidence="Đ.235 BLHS phạt pháp nhân 6–40 tỷ không phải trần; Đ.82/BLDS 602 không trần", src="ERRATA r10 §6"),
    dict(driver="(4) Nghi Sơn GĐ1: LN = 0 ↔ r11 cao (thuế 0%)", lo=a0[0] - A7, hi=a11z[0] - A7, evidence="NQ 34 công suất; giá xút BQ; phần lớn giá [UL]", src="out_r11_D_band.csv"),
    dict(driver="(6a) Dự phòng môi trường: 200 tỷ một lần (đã trừ trong A7) ↔ thêm 100/quý × 4 quý", lo=31439 - 32399, hi=0, evidence="note 19: 200 tỷ tới 30/09", src="out_r10_final_grid.csv"),
    dict(driver="(6b) Dự phòng 100 tỷ/quý lặp VĨNH VIỄN", lo=-6065, hi=0, evidence="chưa có bằng chứng lặp; không tìm được tiền lệ chi môi trường thường xuyên ≥100 tỷ/quý ở VN", src="out_r10_perpetual.csv"),
])
torn["swing"] = (torn.hi - torn.lo).abs()
torn.to_csv(f"{H}/out_r11_B_tornado.csv", index=False); P("\nB — tornado (đ/cp; dòng 2,3,4 là mức A7 hoặc Δ so A7; dòng 1 là Δ giá trị tiền):\n", torn[["driver", "lo", "hi", "swing"]].to_string(index=False))
P("Tiền ròng/cp:", ps(nc), "; cổ tức 8.000 đ/cp trả 25/09 (5.000 còn lại 2025 + 3.000 tạm ứng 2026) ; 3.000/32.900 =", round(3000 / 32900, 3), "; 8.000/32.900 =", round(8000 / 32900, 3))
open(f"{H}/run_stdout_r11.txt", "w").write("\n".join(o))
