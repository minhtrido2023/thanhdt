"""r12 (job Taylor_20261029_134234): áp ERRATA r11 (người phản biện vòng 5) lên r11. Không sửa model.py / r11_calc.py.
Chạy: /home/trido/thanhdt/wc_venv/bin/python r12_calc.py  (cần model.py, r11_calc.py, data/ cùng thư mục) → run_stdout_r12.txt + out_r12_*.csv.
Đơn vị tỷ đồng trừ khi ghi khác. [UL] = ước lượng không có nguồn trực tiếp. w = (thuận 0,2 / cơ sở 0,5 / nghịch 0,3) = model.py CFG_A (nhóm tự đặt, chủ quan).
(A) Nghi Sơn trên MỘT cơ sở ròng + đối chiếu P/E-trên-NPAT (model.py ns_value) với DCF FCF; VLĐ 15% doanh thu [UL]; duy tu 1,5% capex [UL];
    thuế theo legal-vn (miễn 4 giảm 9, 10%/15 năm — chưa xác minh điều kiện); điện 110kV QĐ 1279/QĐ-BCT 09/05/2025.
(B) tornado chuẩn hoá Δ so với A7, có định nghĩa 2 đầu mút, không thứ hạng.
(C) quy mô tương đối 400 tỷ/năm: TKV (nhandan.vn 21/08/2022) vs DGC (BCTC Q3/2026).
(D) cổ tức: LCTT 9T (MIKE_EXTRACT_BCTC_Q3_2026.md:43)."""
import os, io, copy, contextlib, pandas as pd, model as M
H = os.path.dirname(os.path.abspath(__file__)); o = []
def P(*a): o.append(" ".join(str(x) for x in a)); print(*a)
pd.set_option("display.width", 250)
with contextlib.redirect_stdout(io.StringIO()):       # tái lập r11 (assert r10 bên trong) — tái dùng pr, S, run_ns, dcf-giả định
    import r11_calc as R
A7, B7 = R.A7, R.B7; P("tái lập r10/r11: A7", A7, "B7", B7)
SH, KE, W = M.SH, M.ke(), dict(thuan=0.2, coso=0.5, nghich=0.3)
assert tuple(M.CFG_A["w"]) == (0.2, 0.5, 0.3)
ps = lambda x: round(x * 1000 / SH)
IDX = {"thuan": 1, "coso": 2, "nghich": 3}

# ============ (A1) Nghi Sơn ròng trong A7
r = M.per_scn(M.CFG_A7); zero = {k: ([0, 0], 0) for k in M.SCN}; z = R.run_ns(zero, M.CFG_A7)
M.CFG.clear(); M.CFG.update(dict(dict(fund=0.0, wc27=300), **M.CFG_A7)); left = M.ns_left()
cap_ps = ps(left)
rows = []
for k in ("thuan", "coso", "nghich"):
    gross = r[IDX[k]] - z[IDX[k]]
    rows.append(dict(scn=k, w=W[k], ns_steady_npat=M.SCN[k]["ns_steady"], pe_mult=M.NS_MULT[k], gross_ps=gross, capex_left_ps=-cap_ps, net_ps=gross - cap_ps,
                     model_ns_value_ps=ps(M.ns_value(k))))
a1 = pd.DataFrame(rows)
wavg = {c: round(sum(a1.set_index("scn")[c][k] * W[k] for k in W)) for c in ("gross_ps", "net_ps", "model_ns_value_ps")}
a1 = pd.concat([a1, pd.DataFrame([dict(scn="TB gia quyền w=0,2/0,5/0,3", w=1.0, gross_ps=wavg["gross_ps"], capex_left_ps=-cap_ps, net_ps=wavg["net_ps"],
                                       model_ns_value_ps=wavg["model_ns_value_ps"])])])
a1.to_csv(f"{H}/out_r12_A1_ns_net_in_A7.csv", index=False)
P("\nA1 — Nghi Sơn RÒNG trong A7 (gộp = LN NS trong mọi dòng tiền model; capex còn lại %.1f tỷ = %d đ/cp):\n" % (left, cap_ps), a1.to_string(index=False))
pass

# ============ (A2) DCF độc lập: VLĐ, duy tu, lịch thuế ưu đãi, điện 110kV
TAR_110 = dict(normal=1811, off=1146, peak=3266)      # đ/kWh chưa VAT, sản xuất ≥110kV, QĐ 1279/QĐ-BCT 09/05/2025 (luatvietnam.vn)
HRS = dict(normal=96, peak=30, off=42)                # giờ/tuần [UL: khung giờ Mon–Sat 13/5/6, CN 18/0/6 — chưa đối chiếu văn bản gốc]
TAR_BLEND = round(sum(TAR_110[k] * HRS[k] for k in HRS) / 168)
P("\nĐiện 110kV sản xuất: bình thường %d / thấp điểm %d / cao điểm %d ; phụ tải phẳng 24/7 ⇒ ~%d đ/kWh [UL khung giờ] ; r11 dùng 2.300/2.100/2.000" % (TAR_110["normal"], TAR_110["off"], TAR_110["peak"], TAR_BLEND))
S0 = copy.deepcopy(R.S)
def proj(sk, tax, tariff=None, bleach=None):
    try:
        if tariff is not None: R.S[sk]["tariff"] = tariff
        if bleach is not None: R.S[sk]["px"]["bleach"] = bleach
        return pd.DataFrame(R.project(sk, tax)).set_index("year")
    finally:
        R.S.clear(); R.S.update(copy.deepcopy(S0))

def tax_sched(y, kind):
    if kind == "20": return 0.20
    if kind == "0": return 0.0
    # legal-vn 29/10: nếu doanh thu + thu nhập chịu thuế đầu tiên 2027: 0% 2027-30, 5% 2031-39, 10% 2040-41, 20% từ 2042 (chưa xác minh điều kiện 'dự án mới')
    return 0.0 if y <= 2030 else 0.05 if y <= 2039 else 0.10 if y <= 2041 else 0.20

def dcf2(sk, tax_kind="20", wc=0.0, maint=36, tariff=None, bleach=None, life_end=2041, wc_release=True, pe_npat_only=False):
    d = proj(sk, 0.0, tariff, bleach)          # EBITDA/EBIT trước thuế; thuế áp theo lịch
    pv = -left / (1 + KE) ** 0.3; prev_rev, wcb, f = 0.0, 0.0, 0.0
    for j, y in enumerate(range(2027, life_end + 1)):
        e = d.loc[min(y, 2030)]; t = tax_sched(y, tax_kind)
        npat = e.ebit - max(e.ebit, 0) * t
        f = npat if pe_npat_only else e.ebitda - max(e.ebit, 0) * t - maint
        dwc = wc * (e.rev - prev_rev); prev_rev = e.rev; wcb += dwc; f -= dwc
        if y > 2030 and f <= 0: f = 0.0      # tạm dừng nếu dòng tiền âm kéo dài [giả định r11]
        pv += f / (1 + KE) ** (0.68 + j)
    if wc_release and wc: pv += wcb / (1 + KE) ** (0.68 + j)
    return ps(pv)

rows = []
for sk in ("thap", "giua", "cao"):
    rows.append(dict(scn=sk,
        r11_tax20=dcf2(sk), wc15=dcf2(sk, wc=0.15), wc15_norelease=dcf2(sk, wc=0.15, wc_release=False),
        tax_legal=dcf2(sk, "legal"), tax_legal_wc15=dcf2(sk, "legal", wc=0.15),
        tariff110=dcf2(sk, tariff=TAR_BLEND), tariff110_normal=dcf2(sk, tariff=1811),
        maint0=dcf2(sk, maint=0), maint72=dcf2(sk, maint=72),
        ebitda2030=int(proj(sk, 0.2).loc[2030, "ebitda"]), ebitda2030_tariff110=int(proj(sk, 0.2, TAR_BLEND).loc[2030, "ebitda"]),
        ebitda2030_tariff1811=int(proj(sk, 0.2, 1811).loc[2030, "ebitda"]),
        npat2030_legal=int(proj(sk, 0.0).loc[2030, "npat"]), rev2030=int(proj(sk, 0.2).loc[2030, "rev"])))
a2 = pd.DataFrame(rows); pass
a2.to_csv(f"{H}/out_r12_A2_dcf_variants.csv", index=False)
P("\nA2 — NPV độc lập (đ/cp, từ 29/10/26, đã trừ capex còn lại, 15 năm, ke %.3f) — ĐỘ NHẠY theo giá [UL], KHÔNG phải ước tính:\n" % KE, a2.to_string(index=False))

# Ca(OCl)2: giá chào B2B 900–1.200 USD/t (65-70%) ⇒ 23,7–31,6 tr/t ; r11 dùng 10/15/17 [UL]. Độ nhạy kịch bản giữa.
bl = pd.DataFrame([dict(bleach_px=b, npv_giua=dcf2("giua", bleach=b), rev2030=int(proj("giua", 0.2, bleach=b).loc[2030, "rev"]),
                        bleach_share_rev2030=round(proj("giua", 0.2, bleach=b).loc[2030].pipe(lambda e: 20 * 0.85 * b / e.rev), 3)) for b in (5, 10, 15, 23.7, 31.6)])
bl.to_csv(f"{H}/out_r12_A2_bleach_sens.csv", index=False); P("\nĐộ nhạy giá Ca(OCl)2 (tr/t), kịch bản giữa:\n", bl.to_string(index=False))

# ============ (A3) đối chiếu P/E-trên-NPAT (model.py:328) vs DCF FCF — kịch bản giữa/cơ sở
st = {"thap": 0, "giua": 217, "cao": 479}
def pe_val(npat, mult):  # model.py ns_value: steady × P/E / (1+ke)^2 − capex còn lại
    return ps(npat * mult / (1 + KE) ** 2 - left)
steps = [
    ("1 model: NPAT ổn định 165 × P/E 7 /1,149² − capex (chỉ phần ns_value)", pe_val(165, 7)),
    ("2 thay NPAT 165 → 217 (từ dưới lên 2030, thuế 20%)", pe_val(217, 7)),
    ("3 DCF 15 năm trên NPAT (không cộng KH, không VLĐ)", dcf2("giua", pe_npat_only=True)),
    ("4 DCF FCF = EBITDA − thuế − duy tu 36 (= NPAT + KH 160 − 36): r11", dcf2("giua")),
    ("5 + VLĐ 15% doanh thu [UL], thu hồi cuối 2041", dcf2("giua", wc=0.15)),
    ("6 + VLĐ 15%, KHÔNG thu hồi", dcf2("giua", wc=0.15, wc_release=False)),
    ("7 bước 5 + thuế lịch ưu đãi (chưa xác minh điều kiện)", dcf2("giua", "legal", wc=0.15)),
]
a3 = pd.DataFrame(steps, columns=["step", "ps"]); a3["d_vs_prev"] = a3.ps.diff()
a3.to_csv(f"{H}/out_r12_A3_pe_vs_dcf.csv", index=False)
P("\nA3 — cầu nối P/E-trên-NPAT ↔ DCF FCF (kịch bản giữa, đ/cp, đã trừ capex còn lại):\n", a3.to_string(index=False))
P("  P/E 7 ≈ suất lợi nhuận 14,3%% ~ ke %.1f%% (vĩnh viễn, không tăng trưởng) nhưng chiết khấu thêm 2 năm; DCF cộng KH 160 − duy tu 36 = +124 tỷ/năm ⇒ chênh chính do PHƯƠNG PHÁP." % (KE * 100))
# NPAT 217 vào model (cả ns_np 2027-28 từ dưới lên của kịch bản giữa) — đo ròng trong A7 cho cơ sở
ns_mid = {k: (([107, 135], 217) if k == "coso" else (M.SCN[k]["ns_np"], M.SCN[k]["ns_steady"])) for k in M.SCN}
rm = R.run_ns(ns_mid, M.CFG_A7); P("  đưa NPAT từ dưới lên (107/135/217) vào kịch bản CƠ SỞ của model: Nghi Sơn ròng cơ sở =", rm[2] - z[2] - cap_ps, "đ/cp (r10: ", r[2] - z[2] - cap_ps, ")")

# ============ (B) tornado chuẩn hoá Δ so với A7
fg = pd.read_csv(f"{H}/out_r10_final_grid.csv")
g = lambda base, case, tax=0.0: int(fg[(fg.base == base) & (fg.case == case) & (fg.tax_shield == tax)].A7.iloc[0])
r4n0, r2n0, r4x4 = g("r4", "N=0 (Q4 ex-dự phòng, không trích thêm)"), g("R2", "N=0 (Q4 ex-dự phòng, không trích thêm)"), g("r4", "100 × 4 quý")
hc0 = dict(M.HC_LEGAL)
def hc_all(x):
    try:
        for k in M.HC_LEGAL: M.HC_LEGAL[k] = x
        return M.per_scn(M.CFG_A7)[0]
    finally:
        M.HC_LEGAL.update(hc0)
hc_hi, hc_lo = hc_all(0.03), hc_all(0.29)
d_thap = {k: ([-258, -220], 0) for k in M.SCN}; d_cao = {k: ([321, 439], 479) for k in M.SCN}
ns_lo, ns_hi = R.run_ns(d_thap, M.CFG_A7)[0], R.run_ns(d_cao, M.CFG_A7)[0]
perp = pd.read_csv(f"{H}/out_r10_perpetual.csv"); R1 = int(perp[perp.per_quarter == 100].ev_A7.iloc[0])
T = [
    ("Biên gộp 2027-28 (giá P4/DAP, lưu huỳnh/NH3, quặng mua ngoài)", r4n0, r2n0,
     "nền r4 biên 16,5/17,5%, Q4 ex-dự phòng, không trích thêm", "nền R2 biên 19,5/20,7% (9T thực 20,7%), giá vốn phẳng, Q4 ex-dự phòng", "BCTC 9T chắc; hướng 2027-28 [UL]"),
    ("Nguồn quặng: khai trường 25/19B", A7, B7, "A7: không mở lại", "B7: mở lại (uplift LN gộp, cơ sở 0,5 năm 2028)", "khai trường 25 tạm dừng phục vụ điều tra; chưa có quyết định mở lại"),
    ("Tiền ròng × haircut pháp lý (cùng mức cho cả 3 kịch bản)", hc_lo, hc_hi, "haircut 29% ở cả 3 kịch bản", "haircut 3% ở cả 3 kịch bản", "số dư tiền chắc (BCTC 30/09); haircut [UL]"),
    ("Nghi Sơn GĐ1 (LN trong model; capex còn lại luôn trừ)", ns_lo, ns_hi, "P&L từ dưới lên 'thấp' (thuế 20%) áp cho cả 3 kịch bản, ổn định = 0 (tạm dừng)", "P&L từ dưới lên 'cao' (thuế 20%) áp cho cả 3 kịch bản", "công suất chắc (NQ 34); giá/biên phần lớn [UL]"),
    ("Dự phòng môi trường hữu hạn (nền r4)", r4x4, r4n0, "thêm 100 tỷ/quý × 4 quý (trước thuế)", "không trích thêm (Q4 ex-dự phòng)", "note 19: 200 tỷ tới 30/09; chưa phân định hữu hạn/lặp"),
    ("Dự phòng 100 tỷ/quý lặp vĩnh viễn (độ nhạy phụ)", A7 + int(perp[perp.per_quarter == 100].d_vs_R2.iloc[0]), A7, "nền r4 + lặp vĩnh viễn (ô thấp nhất 26.117 tuyến tính; 26,1–26,6k theo 3 cách đo)", "A7 (200 tỷ đã trích, không lặp)", "chưa phân định; xem phần C"),
    ("Dự phòng lặp vĩnh viễn trên nền R2 (để đối xứng)", R1, r2n0, "R1 = R2 + 400 tỷ/năm vĩnh viễn", "R2 không trích thêm", "cùng như trên"),
]
tb = pd.DataFrame([dict(driver=a, lo_level=lo, hi_level=hi, d_lo_vs_A7=lo - A7, d_hi_vs_A7=hi - A7, width=abs(hi - lo), lo_def=ld, hi_def=hd, evidence=ev)
                   for a, lo, hi, ld, hd, ev in T])
tb.loc[len(tb)] = dict(driver="Pháp lý: phạt / khắc phục / đình chỉ", lo_level=None, hi_level=None, d_lo_vs_A7=None, d_hi_vs_A7=None, width=None,
                       lo_def="không định lượng", hi_def="", evidence="Đ.235 phạt pháp nhân 6–40 tỷ không phải trần; Đ.82/BLDS 602 không trần; đình chỉ chưa đo")
tb.to_csv(f"{H}/out_r12_B_tornado.csv", index=False)
P("\nB — động lực, Δ so với A7 = %d (đ/cp; KHÔNG xếp hạng; w = 0,2/0,5/0,3 nhóm tự đặt):\n" % A7, tb[["driver", "lo_level", "hi_level", "d_lo_vs_A7", "d_hi_vs_A7", "width"]].to_string(index=False))

# ============ (C) quy mô tương đối
dgc_rev9, dgc_cogs9, dgc_sga9, dgc_np9 = 7009.46, 5558.26, 242.77 + 154.66, 1369.4
tkv_env21, tkv_rev21_total, tkv_rev21_net = 1160, 138813, 113173
C = pd.DataFrame([
    dict(item="TKV 2021: chi BVMT / tổng doanh thu toàn Tập đoàn", num=tkv_env21, den=tkv_rev21_total, ratio=round(tkv_env21 / tkv_rev21_total, 4), src="nhandan.vn 21/08/2022; DT: nhandan/baophapluat (qua tìm kiếm)"),
    dict(item="TKV 2021: chi BVMT / doanh thu thuần hợp nhất", num=tkv_env21, den=tkv_rev21_net, ratio=round(tkv_env21 / tkv_rev21_net, 4), src="viettimes.vn (qua tìm kiếm)"),
    dict(item="DGC: 400 tỷ/năm / doanh thu 9T quy năm", num=400, den=round(dgc_rev9 * 4 / 3), ratio=round(400 / (dgc_rev9 * 4 / 3), 4), src="BCTC Q3/2026"),
    dict(item="DGC: 400 tỷ/năm / giá vốn 9T quy năm", num=400, den=round(dgc_cogs9 * 4 / 3), ratio=round(400 / (dgc_cogs9 * 4 / 3), 4), src="BCTC Q3/2026"),
    dict(item="DGC: 400 tỷ/năm / BH+QLDN 9T quy năm", num=400, den=round(dgc_sga9 * 4 / 3), ratio=round(400 / (dgc_sga9 * 4 / 3), 4), src="BCTC Q3/2026"),
    dict(item="DGC: 400 tỷ/năm / LNST hợp nhất 9T quy năm", num=400, den=round(dgc_np9 * 4 / 3), ratio=round(400 / (dgc_np9 * 4 / 3), 4), src="BCTC Q3/2026"),
    dict(item="DGC: 200 tỷ đã trích / tồn thạch cao ~3 triệu t (đ/t)", num=200e9, den=3e6, ratio=round(200e9 / 3e6), src="baolaocai.vn 12/12/2021 (tồn ~3 triệu t, >600k t/năm)"),
    dict(item="DGC: 400 tỷ/năm / thạch cao phát sinh >600k t/năm (đ/t)", num=400e9, den=600e3, ratio=round(400e9 / 600e3), src="baolaocai.vn 12/12/2021"),
])
C.to_csv(f"{H}/out_r12_C_relative_scale.csv", index=False); P("\nC — quy mô tương đối:\n", C.to_string(index=False))
P("  cường độ DGC (400/DT quy năm) ÷ TKV 2021 (chi BVMT/DT): %.1f× (tổng DT) ; %.1f× (DT thuần) — định nghĩa 'chi BVMT' của TKV không tách đầu tư/vận hành" %
  (C.ratio[2] / C.ratio[0], C.ratio[2] / C.ratio[1]))

# ============ (D) cổ tức / khả năng chi trả
div9, div_0925 = 4213.0, round(8000 * SH / 1000, 1); nc = 9761.2 - 1391.0
D = pd.DataFrame([dict(item="cổ tức đã trả 9T (LCTT, MIKE_EXTRACT_BCTC_Q3_2026.md:43)", ty=div9),
                  dict(item="trong đó đợt 25/09: 8.000 đ/cp × 379,78 triệu cp", ty=div_0925),
                  dict(item="phần còn lại (đợt trước trong 9T)", ty=round(div9 - div_0925, 1)),
                  dict(item="tiền ròng 30/09 (tiền+gửi 9.761,2 − vay 1.391,0)", ty=round(nc, 1)),
                  dict(item="tiền ròng / cổ tức đã trả 9T (lần)", ty=round(nc / div9, 2)),
                  dict(item="tiền ròng / cp (đ)", ty=ps(nc)),
                  dict(item="LNST hợp nhất 9T", ty=1369.4)])
D.to_csv(f"{H}/out_r12_D_dividend.csv", index=False); P("\nD — cổ tức (không dự báo cổ tức mới):\n", D.to_string(index=False))
open(f"{H}/run_stdout_r12.txt", "w").write("\n".join(o))
