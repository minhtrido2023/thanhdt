"""FPT DCF theo phạm vi SAU ngừng hợp nhất FPT Telecom (FOX) — job Taylor_20261014_055001.

CHỈ NGHIÊN CỨU. Tổ hợp thận trọng/cơ sở/lạc quan đã khai trước ở PREREG.md (md5 cd17b6dc...).
Input (đều nằm cùng thư mục):
  bq_fin_fpt_fox.csv   — BQ tav2_bq.ticker_financial FPT+FOX 2020Q4..2026Q2 (quarterly, VND)
  dnse_live_raw.json   — DNSE latest_trade G1 14/10/2026 ~11:30 ICT (giá live, KHÔNG BQ)
  bq_peer_pe.csv       — BQ ticker_1m 13/10 PE CMG/ELC/FOX/FPT
Hằng số ngoài BQ đều ghi nguồn ngay cạnh.
Chạy: python3 fpt_deconsol_dcf.py  → out_fpt_deconsol.txt (stdout), matrix_fv.csv, cashflow_scope.csv
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
B = 1e9

# ---------------------------------------------------------------- hằng số có nguồn
STAKE_FOX = 0.4566          # FPT sở hữu FOX — ACBS flash note 23/03/2026 + Mekong ASEAN (31/12/2025)
OSH_FPT = 1714.3e6          # BQ ticker_financial FPT 2026Q2 (shares_outstanding_live: không có dòng FPT)
OSH_FOX = 738.763463e6      # BQ ticker_financial FOX 2026Q2
EAT_2025_CONS = 11232       # ACBS: EAT 2025 hợp nhất cũ (tỷ)
NPATMI_2025 = 9376          # ACBS / BQ: LNST cổ đông mẹ 2025
FOX_EAT_SHARE_2025 = 0.310  # ACBS: FOX đóng góp 31,0% EAT 2025
NETCASH_2025 = 19080        # ACBS: tiền ròng 2025 hợp nhất cũ; FOX đóng góp 29,3%
FOX_NETCASH_SHARE = 0.293
PLAN_PBT_G = 0.15           # ĐHĐCĐ 2026: LNTT 11.629 tỷ, +15% like-for-like
PLAN_PBT_2026 = 11629
H1_26_PBT, H1_26_NPATMI = 5714, 5055   # sơ bộ 16/07/2026 (Mekong ASEAN/CafeF) — NPATMI khớp BQ 2487+2568
NPATMI_8M_26 = 6761         # báo chí, ghi ở README fpt_dd_tech_20261014 (chưa kiểm lại nguồn gốc)
ACBS_NPATMI_26F = 10696     # ACBS 23/03/2026
FOX_DIV_DPS_2025 = 2000     # FOX đề xuất cổ tức 2025 ≥2.000đ/cp (ĐHĐCĐ 2025) — NGÀY TRẢ: KHÔNG TÌM ĐƯỢC
STOP = 50500

# rates đo bằng dcf_valuation/deposit_rate_vn as-of 2026-10-14 (xem out_rates trong README)
RF_NOW, RF_MA12 = 0.074, 0.0625833
GT = {"cap_rf": 0.074, "cpi_gdp_half": 0.0655295, "cpi": 0.0344195}
GT_CAP_MA12 = min(0.0344195 + 0.06222, RF_MA12)   # cap_rf tính lại với rf chậm (khai ở README)
EXPLICIT_YEARS, SHRINK, G_CAP, G_FLOOR = 5, 0.5, 0.20, -0.02   # y hệt dcf_valuation.py

live = json.load(open(os.path.join(HERE, "dnse_live_raw.json")))
PX_FPT = live["FPT_G1"]["trades"][0]["matchPrice"] * 1000
PX_FOX = live["FOX_G1"]["trades"][0]["matchPrice"] * 1000
FOX_VOL_SHARES = live["FOX_G1"]["trades"][0]["totalVolumeTraded"] * 10  # DNSE đơn vị 10 cp

# ---------------------------------------------------------------- dữ liệu quý
d = pd.read_csv(os.path.join(HERE, "bq_fin_fpt_fox.csv"))
d["year"] = d.quarter.str[:4].astype(int)
d["q"] = d.quarter.str[-1].astype(int)
for c in ["NP_P0", "Revenue_P0", "CF_OA_P0", "CF_Invest_P0", "AR_P0", "Cash_P0",
          "StDebt_P0", "LtDebt_P0", "LtInvest_P0"]:
    d[c] = d[c] / B
d["FCF"] = d.CF_OA_P0 + d.CF_Invest_P0
fpt = d[d.ticker == "FPT"].set_index("quarter")
fox = d[d.ticker == "FOX"].set_index("quarter")


def ysum(df, col, year, qs=(1, 2, 3, 4)):
    s = df[(df.year == year) & (df.q.isin(qs))]
    return float(s[col].sum()) if len(s) == len(qs) else np.nan


print(f"Giá live DNSE: FPT {PX_FPT:,.0f} ({live['FPT_G1']['trades'][0]['time']}), "
      f"FOX {PX_FOX:,.0f} ({live['FOX_G1']['trades'][0]['time']}, KL phiên tới lúc đó {FOX_VOL_SHARES:,.0f} cp)")

# ---------------------------------------------------------------- 1) dòng tiền theo phạm vi
rows = []
for y in range(2021, 2027):
    old_scope = y <= 2025
    r = {"year": y}
    for lab, qs in (("H1", (1, 2)), ("FY", (1, 2, 3, 4))):
        f = ysum(fpt, "FCF", y, qs)
        x = ysum(fox, "FCF", y, qs)
        r[f"FPT_reported_{lab}"] = f
        r[f"FOX_{lab}"] = x
        # core = hợp nhất cũ − FOX (2021-25); 2026 = số báo cáo (đã không còn FOX)
        r[f"core_{lab}"] = f - x if old_scope else f
        r[f"CFO_core_{lab}"] = (ysum(fpt, "CF_OA_P0", y, qs) - (ysum(fox, "CF_OA_P0", y, qs) if old_scope else 0))
        r[f"CFI_core_{lab}"] = (ysum(fpt, "CF_Invest_P0", y, qs) - (ysum(fox, "CF_Invest_P0", y, qs) if old_scope else 0))
    np_mi = ysum(fpt, "NP_P0", y)
    np_fox = ysum(fox, "NP_P0", y)
    r["NPATMI"] = np_mi
    r["NPATMI_core"] = np_mi - STAKE_FOX * np_fox      # bỏ phần lãi FOX thuộc FPT (cả 2 phạm vi đều có dòng này)
    r["NPATMI_H1"] = ysum(fpt, "NP_P0", y, (1, 2))
    r["NPATMI_core_H1"] = r["NPATMI_H1"] - STAKE_FOX * ysum(fox, "NP_P0", y, (1, 2))
    rows.append(r)
cf = pd.DataFrame(rows).set_index("year")
cf["H1_share_core"] = (cf.core_H1 / cf.core_FY).round(2)
cf["FCF_over_NP_core"] = cf.core_FY / cf.NPATMI_core
cf.round(1).to_csv(os.path.join(HERE, "cashflow_scope.csv"))
pd.set_option("display.width", 250)
print("\n== 1) FCF (CF_OA+CF_Invest, tỷ) theo phạm vi — 2021-25 core = hợp nhất cũ − FOX; 2026 = báo cáo mới")
print(cf[["FPT_reported_H1", "FOX_H1", "core_H1", "CFO_core_H1", "CFI_core_H1",
          "FPT_reported_FY", "FOX_FY", "core_FY"]].round(0).assign(H1_share_core=cf.H1_share_core).to_string())
print("\nLNST mẹ & core (tỷ):")
print(cf[["NPATMI", "NPATMI_core", "NPATMI_H1", "NPATMI_core_H1", "FCF_over_NP_core"]].round(2).to_string())

fox_div_to_fpt = STAKE_FOX * OSH_FOX * FOX_DIV_DPS_2025 / B
h1_26_core_exdiv = cf.loc[2026, "core_H1"] - fox_div_to_fpt
print(f"\nCổ tức FOX→FPT ước (2.000đ × {OSH_FOX/1e6:,.1f}tr cp × 45,66%) = {fox_div_to_fpt:,.0f} tỷ; "
      f"NẾU nhận trong H1/26 (giả định, ngày trả không tìm được) thì FCF core H1/26 không gồm cổ tức FOX = "
      f"{h1_26_core_exdiv:,.0f} tỷ (so core H1/25 {cf.loc[2025, 'core_H1']:,.0f})")

# DSO core (AR / doanh thu TTM ×365), bóc FOX ở các quý phạm vi cũ
def core_val(qlabel, col):
    v = fpt.loc[qlabel, col]
    if int(qlabel[:4]) <= 2025 and qlabel in fox.index:
        v -= fox.loc[qlabel, col]
    return v


qs_all = list(fpt.index)
print("\nDSO core (ngày) = AR_core / Doanh thu core TTM × 365:")
dso_rows = []
for i in range(3, len(qs_all)):
    ql = qs_all[i]
    if int(ql[:4]) < 2023:
        continue
    rev_ttm = sum(core_val(qs_all[j], "Revenue_P0") for j in range(i - 3, i + 1))
    ar = core_val(ql, "AR_P0")
    rep_ttm = fpt.loc[qs_all[i - 3:i + 1], "Revenue_P0"].sum()
    dso_rows.append((ql, round(ar), round(rev_ttm), round(ar / rev_ttm * 365, 1),
                     round(fpt.loc[ql, "AR_P0"] / rep_ttm * 365, 1)))
print(pd.DataFrame(dso_rows, columns=["quarter", "AR_core", "Rev_core_TTM", "DSO_core", "DSO_reported(mixed)"]).to_string(index=False))

# ---------------------------------------------------------------- 2) FCFE gốc + tăng trưởng
base_core_3y = cf.loc[[2023, 2024, 2025], "core_FY"].mean()
base_core_2y = cf.loc[[2024, 2025], "core_FY"].mean()
conv = cf.loc[[2023, 2024, 2025], "core_FY"].sum() / cf.loc[[2023, 2024, 2025], "NPATMI_core"].sum()
np_core_ttm = (cf.loc[2025, "NPATMI_core"] - cf.loc[2025, "NPATMI_core_H1"]) + cf.loc[2026, "NPATMI_core_H1"]
base_core_norm = conv * np_core_ttm
base_legacy = cf.loc[[2023, 2024, 2025], "FPT_reported_FY"].mean()
print(f"\n== 2) FCFE gốc (tỷ): legacy hợp nhất cũ TB 2023-25 = {base_legacy:,.0f} (control: production 6.335) | "
      f"core TB 3 năm = {base_core_3y:,.0f} | core TB 2 năm = {base_core_2y:,.0f} | "
      f"chuẩn hoá: tỷ lệ FCF/LNST core 2023-25 {conv:.2f} × LNST core TTM Q2/26 {np_core_ttm:,.0f} = {base_core_norm:,.0f}")

g_core3 = (cf.loc[2025, "NPATMI_core"] / cf.loc[2022, "NPATMI_core"]) ** (1 / 3) - 1
g_h1 = cf.loc[2026, "NPATMI_core_H1"] / cf.loc[2025, "NPATMI_core_H1"] - 1
g3c = float(np.clip(g_core3, G_FLOOR, G_CAP))
G_HIST = {"min": min(g3c, PLAN_PBT_G), "mean": (g3c + PLAN_PBT_G) / 2, "max": max(g3c, PLAN_PBT_G)}
print(f"Tăng trưởng LNST mẹ core: CAGR 2022→25 {g_core3:.1%} (clamp {g3c:.1%}); H1/26 vs H1/25 {g_h1:+.1%}; "
      f"kế hoạch LNTT 2026 +{PLAN_PBT_G:.0%} → g_hist min/mean/max = "
      + " / ".join(f"{v:.1%}" for v in G_HIST.values()))

# kiểm thiểu số (đề bài điểm 1)
mi_2025 = EAT_2025_CONS - NPATMI_2025
fox_eat = FOX_EAT_SHARE_2025 * EAT_2025_CONS
print(f"\nThiểu số 2025 = EAT {EAT_2025_CONS:,} − NPATMI {NPATMI_2025:,} = {mi_2025:,} tỷ = {mi_2025/EAT_2025_CONS:.1%} EAT "
      f"(ACBS). FOX đóng góp EAT {fox_eat:,.0f} → phần không thuộc FPT (54,34%) ≈ {0.5434*fox_eat:,.0f} "
      f"⇒ thiểu số ngoài FOX ≈ {mi_2025-0.5434*fox_eat:,.0f} tỷ (≈0, trong sai số làm tròn)")
print(f"Tiền ròng 2025 (ACBS) {NETCASH_2025:,} trong đó FOX {FOX_NETCASH_SHARE:.1%} → core ≈ "
      f"{NETCASH_2025*(1-FOX_NETCASH_SHARE):,.0f} tỷ = {NETCASH_2025*(1-FOX_NETCASH_SHARE)*B/OSH_FPT:,.0f} đ/cp "
      f"(KHÔNG cộng vào FV: lãi tiền gửi + gửi/rút kỳ hạn đã nằm trong CF_Invest)")

# ---------------------------------------------------------------- 3) FOX
fox_mcap = OSH_FOX * PX_FOX / B
fox_np_ttm = fox.NP_P0.iloc[-4:].sum()
print(f"\n== 3) FOX: vốn hoá @ {PX_FOX:,.0f} = {fox_mcap:,.0f} tỷ; LNST TTM Q2/26 {fox_np_ttm:,.0f} → PE {fox_mcap/fox_np_ttm:.1f}; "
      f"phần 45,66% = {STAKE_FOX*fox_mcap:,.0f} tỷ = {STAKE_FOX*fox_mcap*B/OSH_FPT:,.0f} đ/cp FPT (trước chiết khấu); "
      f"giá trị sổ sách LtInvest FPT Q2/26 {fpt.loc['2026Q2','LtInvest_P0']:,.0f} tỷ (gồm cả khoản đầu tư khác)")


# ---------------------------------------------------------------- 4) ma trận
def fv_equity(base, g_hist, g_T, r):
    g_exp = g_T + SHRINK * (g_hist - g_T)
    if r <= g_T:
        g_T = r - 0.01
    f, pv = base, 0.0
    for y in range(1, EXPLICIT_YEARS + 1):
        f *= 1 + g_exp
        pv += f / (1 + r) ** y
    tv = f * (1 + g_T) / (r - g_T)
    return pv + tv / (1 + r) ** EXPLICIT_YEARS, g_exp


R_ROWS = {"rf7.4+ERP6.5": (RF_NOW + 0.065, None), "rf7.4+ERP7.5": (RF_NOW + 0.075, None),
          "rf7.4+ERP8.5": (RF_NOW + 0.085, None), "rfMA12_6.26+ERP6.5": (RF_MA12 + 0.065, "ma12")}
SCOPES = {"legacy_hopnhat_cu": (base_legacy, None), "core+FOX_ck0": (base_core_3y, 0.0),
          "core+FOX_ck15": (base_core_3y, 0.15), "core+FOX_ck30": (base_core_3y, 0.30)}
out = []
for gname, gT in GT.items():
    for rname, (r, flag) in R_ROWS.items():
        gT_use = GT_CAP_MA12 if (flag == "ma12" and gname == "cap_rf") else gT
        for sname, (base, ck) in SCOPES.items():
            eq, g_exp = fv_equity(base, G_HIST["mean"], gT_use, r)
            fox_part = 0.0 if ck is None else STAKE_FOX * fox_mcap * (1 - ck)
            fv = (eq + fox_part) * B / OSH_FPT
            out.append({"g_T_mode": gname, "g_T": round(gT_use, 4), "r_row": rname, "r": round(r, 4),
                        "scope": sname, "g_exp": round(g_exp, 4), "core_ps": round(eq * B / OSH_FPT),
                        "fox_ps": round(fox_part * B / OSH_FPT), "FV": round(fv),
                        "MOS_vs_live": round((fv - PX_FPT) / fv, 3), "stop_below_FV": STOP < fv})
m = pd.DataFrame(out)
m.to_csv(os.path.join(HERE, "matrix_fv.csv"), index=False)
print("\n== 4) MA TRẬN FV (đ/cp), g_hist = mean (cơ sở) cho mọi ô; MOS so giá live", f"{PX_FPT:,.0f}")
pv = m.pivot_table(index=["scope", "r_row"], columns="g_T_mode", values="FV").reindex(columns=["cpi", "cpi_gdp_half", "cap_rf"])
print(pv.round(0).to_string())

# ---------------------------------------------------------------- 5) 3 nhãn khai trước
LABELS = {"Thận trọng": ("cpi", RF_NOW + 0.085, 0.30, "min"),
          "Cơ sở": ("cpi_gdp_half", RF_NOW + 0.075, 0.15, "mean"),
          "Lạc quan": ("cap_rf", RF_NOW + 0.065, 0.0, "max")}
print("\n== 5) 3 TỔ HỢP KHAI TRƯỚC (PREREG.md) — FCFE core TB 3 năm")
lab_rows = []
for lab, (gname, r, ck, gh) in LABELS.items():
    for bname, base in (("TB3y", base_core_3y), ("chuanhoa", base_core_norm)):
        eq, g_exp = fv_equity(base, G_HIST[gh], GT[gname], r)
        fox_part = STAKE_FOX * fox_mcap * (1 - ck)
        fv = (eq + fox_part) * B / OSH_FPT
        lab_rows.append({"label": lab, "base": bname, "g_T": GT[gname], "r": r, "g_hist": G_HIST[gh], "g_exp": g_exp,
                         "FOX_ck": ck, "core_ps": eq * B / OSH_FPT, "fox_ps": fox_part * B / OSH_FPT, "FV": fv,
                         "MOS": (fv - PX_FPT) / fv, "stop<FV": STOP < fv, "FV_minus_stop_pct": fv / STOP - 1})
L = pd.DataFrame(lab_rows)
L.round(4).to_csv(os.path.join(HERE, "labels_fv.csv"), index=False)
print(L.round(3).to_string(index=False))

# ---------------------------------------------------------------- 6) tam giác PE
np26 = {"plan×(NPATMI/PBT H1)": PLAN_PBT_2026 * H1_26_NPATMI / H1_26_PBT,
        "run-rate 8T×12/8": NPATMI_8M_26 * 12 / 8, "ACBS 03/2026": ACBS_NPATMI_26F}
print("\n== 6) PE forward 2026E (LNST mẹ, phạm vi mới — đã gồm lãi FOX theo vốn chủ)")
pe_peers = pd.read_csv(os.path.join(HERE, "bq_peer_pe.csv")).set_index("ticker")
for k, v in np26.items():
    eps = v * B / OSH_FPT
    print(f"  {k}: {v:,.0f} tỷ → EPS {eps:,.0f} → PE @ live {PX_FPT/eps:.1f}")
eps_mid = np.median(list(np26.values())) * B / OSH_FPT
grid = {"ELC trailing (BQ 13/10)": pe_peers.loc["ELC", "PE"], "CMG trailing (BQ 13/10)": pe_peers.loc["CMG", "PE"],
        "FOX trailing (BQ)": pe_peers.loc["FOX", "PE"], "PE 13": 13.0, "PE 15": 15.0,
        "FPT trung vị 5 năm (mỏ neo yếu)": 19.7}
for k, pe in grid.items():
    print(f"  {k:34s} PE {pe:5.1f} × EPS 2026E {eps_mid:,.0f} = {pe*eps_mid:,.0f}")
# SOTP-PE: core × PE + FOX thị trường
np_core26 = np.median(list(np26.values())) - STAKE_FOX * fox_np_ttm * 1.10   # FOX 2026 ≈ TTM×1,10 [GĐ]
for pe in (10, 12, 14):
    for ck in (0.0, 0.15, 0.30):
        v = (np_core26 * pe + STAKE_FOX * fox_mcap * (1 - ck)) * B / OSH_FPT
        print(f"  SOTP: core LNST 2026E {np_core26:,.0f} × PE {pe} + FOX ck{int(ck*100)}% = {v:,.0f}", end=" |")
    print()
