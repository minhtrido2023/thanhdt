"""r8: bảng áp sửa theo phản biện (không đổi mô hình). Đọc data/dgc_fin_bq.csv + out_r7_*.csv. python3 r8_calc.py"""
import pandas as pd, os
H = os.path.dirname(os.path.abspath(__file__)); o = []
def P(*a): o.append(" ".join(str(x) for x in a)); print(*a)
d = pd.read_csv(f"{H}/data/dgc_fin_bq.csv"); d["cfo"] = d.CF_OA_P0 / 1e9; d["np"] = d.NP_P0 / 1e9
d["y"] = d.quarter.str[:4]; d["q"] = d.quarter.str[-2:]
# --- 1. CFO từng quý (LNST mẹ từ BQ; Q3/26 mẹ 478,162 / hợp nhất 506,68 từ BCTC Q3; CFO Q3 = 755,6 − (−240,47) = 996,07)
q = d[d.quarter.isin(["2025Q4", "2026Q1", "2026Q2"])][["quarter", "cfo", "np"]].copy()
q = pd.concat([q, pd.DataFrame([dict(quarter="2026Q3", cfo=755.6 + 240.47, np=478.162)])], ignore_index=True)
q["cfo_over_np"] = (q.cfo / q.np).round(2); P(q.round(1).to_string(index=False)); q.round(3).to_csv(f"{H}/out_r8_cfo_quarters.csv", index=False)
ttm = q.tail(4); P("TTM Q4/25-Q3/26: CFO", round(ttm.cfo.sum(), 1), "LNST mẹ", round(ttm.np.sum(), 1), "tỷ", round(ttm.cfo.sum() / ttm.np.sum(), 2))
P("9T/2026: CFO 755,6 / LNST hợp nhất 1.369,39 =", round(755.6 / 1369.39, 2), "; 9T/2025 CFO 1.250,2 / LNST hợp nhất 2.532,04 =", round(1250.2 / 2532.04, 2))
fy = d.groupby("y").agg(n=("cfo", "size"), cfo=("cfo", "sum"), np=("np", "sum")); fy = fy[fy.n == 4]; fy["r"] = (fy.cfo / fy.np).round(2)
P(fy.round(1).to_string()); P("năm CFO<NP (2014-2025, 4 quý):", fy[fy.r < 1].index.tolist(), "/", len(fy)); fy.to_csv(f"{H}/out_r8_cfo_base_rate.csv")
# điều kiện đổi nhãn không tự đạt: TTM tại Q4/26 cần CFO Q4 >= ?
for y in (400, 450, 500):
    P(f"TTM tại Q4/26 ≥1,0×: cần CFO Q4 ≥ {1267.1 + y - 755.6:.0f} nếu LNST mẹ Q4 = {y} [UL]")
# --- 2. dự phòng R1/R2 + nghĩa vụ thêm (T1) trên R1
r = pd.read_csv(f"{H}/out_r7_prov_readings.csv"); SH = 379.779286; PX = 32900
rows = []
for _, x in r.iterrows():
    for ex in (0, 200, 500, 1000):
        a = x.ev_A7 - round(ex * 1000 / SH); b = x.ev_B7 - round(ex * 1000 / SH)
        rows.append(dict(reading=x.reading, extra_liab=ex, A7=a, A7_vs_px=round(a / PX - 1, 3), B7=b, B7_vs_px=round(b / PX - 1, 3)))
t = pd.DataFrame(rows); P(t.to_string(index=False)); t.to_csv(f"{H}/out_r8_prov_R1_R2_extra.csv", index=False)
P("100 tỷ dự phòng/quý =", round(100 * 1000 / SH), "đ/cp =", round(100 * 1000 / SH / PX * 100, 2), "% giá")
# --- 3. ZaloPay
cost_pre, div, cost_post, px, nav, sh = 47775, 8000, 39775, 32900, 919.931, 10000
P("lợi suất giá vs giá vốn DNSE sau cổ tức:", round(px / cost_post - 1, 4), "| kinh tế gồm cổ tức:", round((px + div) / cost_pre - 1, 4))
P("vị thế", sh * px / 1e6, "tr =", round(sh * px / 1e6 / nav * 100, 1), "% NAV ; lỗ kinh tế nếu thoát", round(sh * (cost_pre - div - px) / 1e6, 2), "tr =", round(sh * (cost_post - px) / 1e6 / nav * 100, 2), "% NAV")
zr = []
for tgt in (None, 10, 5, 3, 1.5, 0):
    keep = sh if tgt is None else int(tgt / 100 * nav * 1e6 / px) if tgt else 0; keep = min(keep, sh)
    zr.append(dict(muc_NAV_dich="giữ nguyên" if tgt is None else f"{tgt}%", giu_cp=keep, ban_cp=sh - keep, thu_tien_tr=round((sh - keep) * px / 1e6, 1),
                   NAV_mat_neu_A7nghich_21501=round(keep * (px - 21501) / 1e6 / nav * 100, 1), NAV_mat_neu_giam50pct=round(keep * px * 0.5 / 1e6 / nav * 100, 1)))
z = pd.DataFrame(zr); P(z.to_string(index=False)); z.to_csv(f"{H}/out_r8_zalopay.csv", index=False)
# --- 4. time-stop theo §12 (từ 26/06/2026; Close điều chỉnh 39.580)
P("r6m mốc 26/12/2026, r9m mốc 26/03/2027; giá hiện / Close điều chỉnh 26/06 =", round(px / 39580 - 1, 3), "; giá cần > 39.580 =", round(39580 / px - 1, 3), "cao hơn hiện tại")
open(f"{H}/run_stdout_r8.txt", "w").write("\n".join(o))
