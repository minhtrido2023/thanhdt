"""ERP nội địa v2 (job Taylor_20261030_041731) — theo PREREG.md (commit 2e67a6de7). READ-ONLY research.
Dùng lại NGUYÊN cache bất biến vòng 1 (../erp_domestic_20261030/data/) và các hàm đọc/thống kê của erp_domestic.py v1
(chỉ import hàm thuần, không gọi part* của v1 vì chúng ghi file vào thư mục v1).
Tái lập: $DNA_PYEXE erp_v2.py ⇒ out_v2_*.csv + run_v2_stdout.txt. Nhãn: [BQ] cache BQ · [SRC] có nguồn · [UL] ước lượng."""
import os, importlib.util
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(HERE, "..", "erp_domestic_20261030")
spec = importlib.util.spec_from_file_location("erp_v1", os.path.join(V1, "erp_domestic.py"))
v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
DD = v1.DD
out = lambda n: os.path.join(HERE, n)
ASOF, RF_C, PI_C, G_C = v1.ASOF, v1.RF_C, v1.PI_C, v1.G_C
DAMO_MATURE, DAMO_TOTAL = v1.DAMO_MATURE, v1.DAMO_TOTAL
LEND_AVG = 10.7                        # [SRC thứ cấp] VNF 21/09/2026, TB 08/2026
G_T_DOM = 5.5                          # PREREG §2: π 4,25 + thực 1,25 (số user nêu, không tinh chỉnh)
T_BLUME = 10
W = {"2011→": "2011-01-01", "2014→": "2013-12-31", "2016-07→": "2016-07-01"}
ROBUST_SET = ("E2_aggregate", "E4_median", "E6_agg_ex_top10", "E9_agg_ex_bank_re", "E10_median_ex_bank_re")
L = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); L.append(s)


# =================================================================== implied D1/D2 (+ D1-ew)
def baskets(d):
    """Rổ của từng ước lượng (mirror v1.ep_estimators) — cần rổ để tính ROE trọng số vốn chủ."""
    d = d[np.isfinite(d.np) & (d.PE != 0)]
    top = d.sort_values("mcap", ascending=False)
    exbr = d[~d.icb.isin(v1.BANK | v1.RE)]
    return {"E2_aggregate": d, "E4_median": d, "E6_agg_ex_top10": top.iloc[10:],
            "E9_agg_ex_bank_re": exbr, "E10_median_ex_bank_re": exbr}


def roe_ew(x):
    x = x[x.ROE5Y.notna() & (x.PB > 0)]
    bv = x.mcap / x.PB
    return float((x.ROE5Y * bv).sum() / bv.sum())


def implied(s, vni):
    pe_by_date = vni.set_index("time").VNINDEX_PE
    d0 = s[s.time == ASOF].dropna(subset=["PE", "OShares", "Price"])
    est = v1.ep_estimators(d0, pe_by_date.get(ASOF, np.nan))
    B = baskets(d0)
    rows = []
    for k in ROBUST_SET:
        ep, roe_med, n = est[k]
        rew = roe_ew(B[k])
        rows.append(dict(est=k, n=n, ep=round(ep, 3), roe_med=round(roe_med, 4), roe_ew=round(rew, 4),
                         erp_mb=v1.ke_mb(ep, roe_med) - RF_C, erp_mb_ew=v1.ke_mb(ep, rew) - RF_C,
                         erp_mb_g425=v1.ke_mb(ep, roe_med, 4.25) - RF_C, erp_mb_g675=v1.ke_mb(ep, roe_med, 6.75) - RF_C,
                         erp_ma=v1.ke_ma(ep) - RF_C, erp_ma_pi40=v1.ke_ma(ep, 4.0) - RF_C, erp_ma_pi45=v1.ke_ma(ep, 4.5) - RF_C))
    T = pd.DataFrame(rows)
    T.round(4).to_csv(out("out_v2_implied.csv"), index=False)
    P("[1] ERP ngầm định, tập robust (asof", ASOF, ") [BQ cache v1]:")
    P(T.round(3).to_string(index=False))
    med = {c: float(T[c].median()) for c in T.columns if c.startswith("erp_")}
    P(f"  D1 (M-b, ROE trung vị) = {med['erp_mb']:.3f} ; D1-ew (ROE trọng số vốn chủ) = {med['erp_mb_ew']:.3f} ; "
      f"D1 g4,25 = {med['erp_mb_g425']:.3f} ; D1 g6,75 = {med['erp_mb_g675']:.3f}")
    P(f"  D2 (M-a, π 4,25) = {med['erp_ma']:.3f} ; π 4,0 = {med['erp_ma_pi40']:.3f} ; π 4,5 = {med['erp_ma_pi45']:.3f}")
    return med, d0


# =================================================================== historical D3/D4 (Blume)
def blume(G, A, N, T):
    if T is None or N < T:          # T=None ⇒ thuần hình học; N<T ⇒ Blume suy biến về G
        return G
    if T == 1:
        return A
    return G * (T - 1) / (N - 1) + A * (N - T) / (N - 1)


def history(vni):
    build, div_pre, _ = v1.monthly_series(vni)
    eq = build(div_pre)
    pe = vni.copy(); pe["time"] = pd.to_datetime(pe.time); pe_s = pe.set_index("time").VNINDEX_PE.dropna()
    dep_i, _ = v1.rf_daily_index(None)
    rows = []
    for lab, a in W.items():
        r, _ = v1.window_stats(eq, dep_i, pd.Timestamp(a), pd.Timestamp(ASOF), pe_s, lab, "big4_12m")
        rows.append(r)
    H = pd.DataFrame(rows).set_index("window")
    # đối chiếu v1 (cùng hàm, cùng cache) — phải trùng out_erp_history.csv v1
    v1h = pd.read_csv(os.path.join(V1, "out_erp_history.csv"))
    v1h = v1h[(v1h.div_case == "central") & (v1h.leg == "big4_12m")].set_index("window")
    for w in W:
        for c in ("erp_geo", "erp_arith", "rerating_pa", "rf_avg", "years"):
            assert abs(H.loc[w, c] - v1h.loc[w, c]) < 1e-9, (w, c)
    P("[2] cửa sổ lịch sử (chân Big-4 12M; trùng byte v1 out_erp_history.csv — đã assert):")
    P(H[["start", "end", "years", "eq_cagr", "rf_avg", "erp_geo", "erp_arith", "rerating_pa"]].to_string())
    return H


def d34(H, windows, T):
    d3, d4 = [], []
    for w in windows:
        h = H.loc[w]; adj = h.rf_avg - RF_C; N = h.years; rho = h.rerating_pa
        d3.append(blume(h.erp_geo - rho, h.erp_arith - rho, N, T) + adj)
        d4.append(blume(h.erp_geo, h.erp_arith, N, T) + adj)
    return float(np.mean(d3)), float(np.mean(d4)), d3, d4


# =================================================================== rule + robustness
def center(D1, D2, D3, D4, rule="family"):
    if rule == "family":
        return 0.5 * (D1 + D2) / 2 + 0.5 * (D3 + D4) / 2
    if rule == "median4":
        return float(np.median([D1, D2, D3, D4]))
    if rule == "hist":
        return (D3 + D4) / 2
    if rule == "impl":
        return (D1 + D2) / 2
    raise ValueError(rule)


def main_rule(med, H):
    D1, D2 = med["erp_mb"], med["erp_ma"]
    D3, D4, d3w, d4w = d34(H, list(W), T_BLUME)
    P(f"  Blume T={T_BLUME}: D3 theo cửa sổ {[round(float(x), 3) for x in d3w]} ⇒ {D3:.3f} ; D4 {[round(float(x), 3) for x in d4w]} ⇒ {D4:.3f}")
    G = {w: (H.loc[w].erp_geo, H.loc[w].erp_arith, H.loc[w].years) for w in W}
    for w, (g, a, n) in G.items():
        P(f"    {w}: N={n:.2f} trọng số số học Blume = {max(0.0, (n - T_BLUME) / (n - 1)):.3f}")
    C = center(D1, D2, D3, D4)
    D = {"D1": D1, "D2": D2, "D3": D3, "D4": D4}
    lo, hi = min(D.values()), max(D.values())
    P(f"[3] LUẬT CHÍNH: D1={D1:.3f} D2={D2:.3f} D3={D3:.3f} D4={D4:.3f} ⇒ C = ½·TB(D1,D2) + ½·TB(D3,D4) = {C:.3f}; dải D {lo:.3f}–{hi:.3f}")
    if C < DAMO_MATURE:
        P(f"  C < sàn {DAMO_MATURE} ⇒ đặt sàn"); C = DAMO_MATURE
    P(f"  kiểm Ke(β1) = {RF_C + C:.2f} vs lãi cho vay TB {LEND_AVG} ⇒ {'≥ (đạt)' if RF_C + C >= LEND_AVG else '< (BÁO)'}")
    # robustness grid (mỗi biến thể đổi MỘT trục)
    R = []
    def add(k, desc, d1=D1, d2=D2, windows=tuple(W), T=T_BLUME, rule="family", crit=True):
        d3, d4, _, _ = d34(H, list(windows), T)
        c = center(d1, d2, d3, d4, rule)
        R.append(dict(k=k, desc=desc, D1=d1, D2=d2, D3=d3, D4=d4, C=c, shift=c - C, in_criterion=crit))
    for i, w in enumerate(W, 1):
        add(f"R{i}", f"bỏ cửa sổ {w}", windows=tuple(x for x in W if x != w))
    add("R4", "thuần hình học", T=None)
    add("R5", "thuần số học", T=1)
    add("R6", "Blume T=5", T=5)
    add("R7", "D1 ROE trọng số vốn chủ", d1=med["erp_mb_ew"])
    add("R8", "D1 g=4,25", d1=med["erp_mb_g425"])
    add("R9", "D1 g=6,75", d1=med["erp_mb_g675"])
    add("R10", "D2 π=4,0", d2=med["erp_ma_pi40"])
    add("R11", "D2 π=4,5", d2=med["erp_ma_pi45"])
    add("R12", "luật trung vị 4 số (v1)", rule="median4")
    add("R13", "chỉ họ lịch sử TB(D3,D4)", rule="hist", crit=False)
    add("R14", "chỉ họ ngầm định TB(D1,D2)", rule="impl", crit=False)
    add("V1", "đặc tả v1 tái tạo: D3 2011→ hình học + D4 2014→ hình học, trung vị", rule="median4", crit=False)
    # V1 đúng nghĩa: D3 chỉ 2011→, D4 chỉ 2014→, hình học
    d3v1 = d34(H, ["2011→"], None)[0]; d4v1 = d34(H, ["2014→"], None)[1]
    R[-1].update(D3=d3v1, D4=d4v1, C=center(D1, D2, d3v1, d4v1, "median4")); R[-1]["shift"] = R[-1]["C"] - C
    T = pd.DataFrame(R); T.round(4).to_csv(out("out_v2_robustness.csv"), index=False)
    P("[4] độ nhạy (mỗi dòng đổi MỘT trục; shift = C_Rk − C):")
    P(T.round(3).to_string(index=False))
    crit = T[T.in_criterion]
    mx = crit.loc[crit["shift"].abs().idxmax()]
    robust = bool((crit["shift"].abs() <= 0.5).all())
    c_lo, c_hi = float(min(crit.C.min(), C)), float(max(crit.C.max(), C))
    up = crit[crit["shift"] > 0.05].sort_values("shift", ascending=False)
    dn = crit[crit["shift"] < -0.05].sort_values("shift")
    P(f"  ĐẨY LÊN: " + "; ".join(f"{r.k} {r.desc} {r.shift:+.2f}" for r in up.itertuples()))
    P(f"  ĐẨY XUỐNG: " + "; ".join(f"{r.k} {r.desc} {r.shift:+.2f}" for r in dn.itertuples()))
    P(f"  tiêu chí bền (|shift| ≤ 0,5 với R1–R12): {'ĐẠT' if robust else 'KHÔNG ĐẠT'} — lớn nhất {mx.k} ({mx.desc}) {mx['shift']:+.3f}")
    P(f"  ⇒ trung tâm {'điểm ' + format(C, '.3f') if robust else f'KHOẢNG {c_lo:.3f}–{c_hi:.3f} (điểm luật chính {C:.3f})'}")
    erp_code = round(C * 4) / 4
    P(f"  giá trị đề xuất cho code = C làm tròn 0,25 = {erp_code:.2f} ⇒ r = {RF_C} + {erp_code:.2f} = {RF_C + erp_code:.2f}%")
    return dict(D1=D1, D2=D2, D3=D3, D4=D4, C=C, d_lo=lo, d_hi=hi, robust=robust, c_lo=c_lo, c_hi=c_hi, erp_code=erp_code)


# =================================================================== terminal multiples + g_T checks
def gordon_table(res, gdp_nom, dep_today):
    r_l = dep_today + 6.5; g_l = min(gdp_nom, dep_today)
    frames = [("L legacy hôm nay", r_l, g_l),
              ("R-only (r mới, g_T cap lãi huy động)", RF_C + res["erp_code"], min(gdp_nom, dep_today)),
              ("R-only (r mới, g_T cap rf_c 6,75)", RF_C + res["erp_code"], min(gdp_nom, RF_C)),
              ("N-lo domestic_v2", RF_C + res["c_lo"], min(gdp_nom, G_T_DOM)),
              ("N-c domestic_v2", RF_C + res["erp_code"], min(gdp_nom, G_T_DOM)),
              ("N-hi domestic_v2", RF_C + res["c_hi"], min(gdp_nom, G_T_DOM))]
    rows = []
    for lab, r, g in frames:
        rows.append(dict(frame=lab, r=round(r, 4), g_T=round(g, 4), r_minus_g=round(r - g, 4),
                         gordon_1pg=round((1 + g / 100) / ((r - g) / 100), 3), inv_rmg=round(1 / ((r - g) / 100), 3)))
    T = pd.DataFrame(rows)
    T["gordon_vs_L_pct"] = (100 * (T.gordon_1pg / T.gordon_1pg.iloc[0] - 1)).round(2)
    T.to_csv(out("out_v2_terminal_multiple.csv"), index=False)
    P("[5] bội số terminal — Gordon đúng code `_fv_per_share`: (1+g)/(r−g); cột inv_rmg = 1/(r−g) của v1 để đối chiếu:")
    P(T.to_string(index=False))


def g_checks(res, vni, d0, gdp_nom, cpi5, gdp15):
    r_new = RF_C + res["erp_code"]
    P(f"[6] kiểm g_T = {G_T_DOM}: (i) GDP danh nghĩa dài hạn tại asof = CPI5y {cpi5:.3f} + GDP thực 15y {gdp15:.3f} = {gdp_nom:.3f} "
      f"⇒ g_T {'≤' if G_T_DOM <= gdp_nom else '>'} GDP danh nghĩa")
    v = vni.dropna(subset=["VNINDEX_PE"]).copy(); v["time"] = pd.to_datetime(v.time)
    v["eps"] = v.vnindex / v.VNINDEX_PE; v = v.set_index("time")
    rows = []
    for lab, a in W.items():
        e = v[v.index >= a]; n = (e.index[-1] - e.index[0]).days / 365.25
        # EPS đầu/cuối lấy TB 20 phiên để bớt nhiễu PE ngày
        e0, e1 = e.eps.iloc[:20].mean(), e.eps.iloc[-20:].mean()
        rows.append(dict(window=lab, years=round(n, 2), eps_start=round(e0, 2), eps_end=round(e1, 2),
                         eps_cagr=round(100 * ((e1 / e0) ** (1 / n) - 1), 3)))
    E = pd.DataFrame(rows); E.to_csv(out("out_v2_eps_growth.csv"), index=False)
    P("  (ii) tăng trưởng EPS danh nghĩa trên 1 đơn vị VNINDEX (VNINDEX/VNINDEX_PE, TB 20 phiên đầu/cuối) [BQ cache v1]:")
    P(E.to_string(index=False))
    nf = d0[~d0.icb.isin(v1.BANK) & d0.ROE5Y.notna()]
    # phi tài chính: loại cả bảo hiểm/chứng khoán theo ICB (85xx, 87xx) như cấp ngành
    nf = nf[~(nf.icb // 100).isin([85, 87])]
    share = 100 * (nf.ROE5Y * 100 >= r_new).mean(); share_mc = 100 * nf.mcap[nf.ROE5Y * 100 >= r_new].sum() / nf.mcap.sum()
    P(f"  (iii) RONIC≥Ke: phi tài chính universe_pit asof N={len(nf)}: ROE5Y ≥ r {r_new:.2f}% ở {share:.1f}% số mã / {share_mc:.1f}% vốn hoá; "
      f"ROE5Y trung vị {100 * nf.ROE5Y.median():.2f}%")
    P("      lưu ý: FCFE của code không trừ tái đầu tư theo g_T (RONIC ngầm định = ∞) ⇒ g_T cao là lạc quan có hệ thống.")
    return E, share


# =================================================================== DGC
def dgc(res):
    spec2 = importlib.util.spec_from_file_location("mke", os.path.join(HERE, "..", "dgc_discount_rate_20261029", "model_ke.py"))
    K = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(K); M = K.M
    A = K.run_cfg(M.CFG_A, K.KE_R7)
    for lab, got, exp in (("A dcf nghich", A["dcf_nghich"], 21407), ("A dcf coso", A["dcf_coso"], 32925),
                          ("A dcf thuan", A["dcf_thuan"], 41779), ("A ev", A["ev"], 29817)):
        P(f"SELFCHECK {lab}: {got} vs {exp} lệch {got - exp}"); assert got == exp
    rows = [dict(cand="r7 hiện hành", erp=7.5, beta=1.0, ke=14.9, **{k: A[k] for k in ("dcf_nghich", "dcf_coso", "dcf_thuan", "ev")})]
    for lab, e in (("khoảng dưới", res["c_lo"]), ("luật chính C", res["C"]), ("ERP code (làm tròn)", res["erp_code"]),
                   ("khoảng trên", res["c_hi"])):
        ke = RF_C + 1.11 * e
        r = K.run_cfg(M.CFG_A, ke / 100)
        rows.append(dict(cand=lab, erp=round(e, 3), beta=1.11, ke=round(ke, 4), **{k: r[k] for k in ("dcf_nghich", "dcf_coso", "dcf_thuan", "ev")}))
    T = pd.DataFrame(rows); T.to_csv(out("out_v2_dgc.csv"), index=False)
    P("[7] DGC tầng A (model_ke 29/10, β 1,11, g 3% giữ):"); P(T.to_string(index=False))
    M.CFG.clear(); M.CFG.update(M.CFG_A)


def main():
    s = v1.load_snap(); vni = pd.read_csv(os.path.join(DD, "vnindex_daily.csv"))
    med, d0 = implied(s, vni)
    H = history(vni)
    res = main_rule(med, H)
    import sys
    sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
    cwd = os.getcwd()
    import dcf_valuation as Dv                          # chdir WORKDIR khi import — trả lại cwd ngay
    import gdp_growth_vn as _gdp
    os.chdir(cwd)
    cpi5 = 100 * Dv.terminal_growth(ASOF); gdp15 = 100 * _gdp.longrun_real_gdp(ASOF)
    dep_today = 100 * Dv.discount_rate(ASOF) - Dv.ERP
    P(f"  [code] tại asof: consumer_deposit_rate = {dep_today:.3f}, CPI5y = {cpi5:.3f}, GDP thực 15y = {gdp15:.3f}, "
      f"g_T legacy = {100 * Dv.terminal_growth_mode(ASOF):.3f}, r legacy = {100 * Dv.discount_rate(ASOF):.3f}")
    gordon_table(res, cpi5 + gdp15, dep_today)
    g_checks(res, vni, d0, cpi5 + gdp15, cpi5, gdp15)
    dgc(res)
    pd.DataFrame([res]).round(4).to_csv(out("out_v2_erp_choice.csv"), index=False)
    with open(out("run_v2_stdout.txt"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
