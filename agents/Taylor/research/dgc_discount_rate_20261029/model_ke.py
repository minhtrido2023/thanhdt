"""Chi phí vốn dài hạn cho DCF DGC (job Taylor_20261029_133456). READ-ONLY research — KHÔNG sửa r7.
Import nguyên ../dgc_valuation_20261029_r7/model.py, chỉ thay hàm ke() qua knob KE (monkeypatch module-level).
Tái lập: $DNA_PYEXE model_ke.py  (ghi out_*.csv cùng thư mục). Đơn vị: đ/cp trừ khi ghi khác.
Nhãn: [SRC] có nguồn ; [UL] ước lượng ; [BQ] đo trên BigQuery trong phiên này."""
import os, sys, importlib.util
from datetime import date, timedelta
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
R7 = os.path.join(HERE, "..", "dgc_valuation_20261029_r7", "model.py")
spec = importlib.util.spec_from_file_location("r7", R7); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
WC = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WC)

# ------------------------------------------------------------- INPUTS (rf / ERP / β)
TPCP_NOW = 4.467            # [SRC] ADB AsianBondsOnline, đóng cửa 28/10/2026
DAMO_MATURE, DAMO_CRP, DAMO_DS = 4.23, 3.90, 2.56   # [SRC] Damodaran ctryprem 05/01/2026: VN Ba2, default spread 2,56, CRP 3,90, tổng 8,13
INFL_TARGET = (4.0, 4.5)    # [SRC-thứ cấp] trần CPI Quốc hội giao 2025-2026 ~4,5%; 4,0 cận dưới [UL]
REAL_LR = (2.0, 3.0)        # [UL] lãi thực dài hạn — khoảng thường dùng (McKinsey Valuation: lãi thực dài hạn ~2%; +đến 1pp cho EM)
BETA_RAW_DGC, BETA_RAW_PEER_MED, N_PEER = 1.204, 1.125, 19   # [BQ] β tuần 5Y 29/10/2021-28/10/2026 vs VNINDEX; peer = universe_pit ICB 13xx in_universe 28/10
blume = lambda b: 2 / 3 * b + 1 / 3
VNI_PE_NOW = 12.1883        # [BQ] VNINDEX_PE 2026-10-28
VNI = {"2011-10-28": (422.07, 9.53), "2016-10-28": (682.25, 16.57), "2026-10-28": (1766.65, 12.1883)}   # [BQ] Close, VNINDEX_PE
DIV_YLD = (1.5, 2.0)        # [UL] tỷ suất cổ tức VNINDEX (dcf_valuation.py dùng ~1,7%)
KE_R7 = M.ke()              # 0,149


def tpcp():
    return pd.read_csv(os.path.join(HERE, "data", "tpcp10y_annual.csv"))


def deposit_avg(years):
    import deposit_rate_vn as d
    end = date(2026, 10, 29); st = end - timedelta(days=round(365.25 * years))
    v = [d.current_deposit_rate(str(st + timedelta(days=i))) for i in range((end - st).days)]
    return float(np.mean(v))


def gdp_nominal_growth():
    g = pd.read_csv(os.path.join(WC, "mike", "data", "fiinprox_gdp_nominal_quarterly_20260914.csv"))
    g["year"] = g.iloc[:, 0].astype(str).str[:4].astype(int)
    a = g[g.year.between(2021, 2025)].groupby("year").gdp_bn_vnd.agg(["sum", "count"])
    a = a[a["count"] == 4]["sum"]
    return float((a.iloc[-1] / a.iloc[0]) ** (1 / (len(a) - 1)) - 1), f"{a.index[0]}-{a.index[-1]}"


def run_cfg(cfg, ke_val, g=None):
    """Chạy r7 với Ke cố định; trả DCF 3 kịch bản + EV blend (SOTP/DCF/bội số đều nhận Ke qua ns_value & P/B)."""
    M.ke = lambda: ke_val
    old_g = M.G_BASE
    if g is not None: M.G_BASE = g
    try:
        M.CFG.clear(); M.CFG.update(dict(dict(fund=0.0, wc27=300), **cfg))
        r = M.evaluate(); sm = r["summ"].set_index("scn")
        return dict(ev=round(r["ev"]), **{f"dcf_{k}": int(sm.dcf[k]) for k in ("nghich", "coso", "thuan")},
                    **{f"blend_{k}": int(sm.blend[k]) for k in ("nghich", "coso", "thuan")},
                    **{f"sotp_{k}": int(sm.sotp[k]) for k in ("coso",)}, pb_coso=int(sm.v_pb["coso"]))
    finally:
        M.ke = lambda: KE_R7; M.G_BASE = old_g


def dcf_decomp(cfg, k, k_e, g):
    """Bản sao KHÔNG sửa logic của r7.dcf_core để tách PV 2027-31 / terminal / tiền; assert tổng = dcf_core."""
    M.CFG.clear(); M.CFG.update(dict(dict(fund=0.0, wc27=300), **cfg)); M.ke = lambda: k_e
    try:
        fc = M.forecasts(); s = M.SCN[k]; r = fc[(fc.scn == k) & (fc.year >= 2027)].set_index("year")
        ebit = [r.loc[2027, "ebit_core"], r.loc[2028, "ebit_core"]]; ebit += [ebit[-1] * (1 + g) ** j for j in (1, 2, 3)]
        out = {}
        for lab, nsf in (("all", 1.0), ("no_ns", 0.0)):
            ns = [x * nsf for x in [s["ns_np"][0], s["ns_np"][1]] + [s["ns_steady"] * (1 + g) ** j for j in (0, 1, 2)]]
            wc = [M.CFG.get("wc27", 300) if k != "nghich" else 0, 0, 0, 0, 0]
            reinv = g / M.RONIC; tt = [0.68 + j for j in range(5)]
            fcff = [(ebit[t] * (1 - M.tax_core(2027 + t)) * (1 - M.CFG["mi_core"]) + ns[t]) * (1 - (reinv if t >= 2 else 0)) + wc[t] for t in range(5)]
            pv = sum(f / (1 + k_e) ** tt[t] for t, f in enumerate(fcff))
            f_T = (ebit[-1] * (1 - M.CFG["term_tax"]) * (1 - M.CFG["mi_core"]) + ns[-1]) * (1 - reinv) + wc[-1]
            tv = f_T * (1 + g) / (k_e - g) / (1 + k_e) ** tt[-1]
            cash = M.cash_adj(k) - M.ns_left()
            out[lab] = dict(pv_27_31=M.per_share(pv), tv=M.per_share(tv), cash=M.per_share(cash), total=M.per_share(pv + tv + cash))
        M.G_BASE_saved = M.G_BASE; M.G_BASE = g
        chk = M.dcf_core(k, k_e, g, fc=fc); M.G_BASE = M.G_BASE_saved
        assert abs(chk - out["all"]["total"]) < 1e-6, (chk, out["all"]["total"])
        return out
    finally:
        M.ke = lambda: KE_R7


def main():
    csv = lambda n: os.path.join(HERE, n)
    L = []
    P = lambda *a: (print(*a), L.append(" ".join(str(x) for x in a)))
    # ---- SELF-CHECK: tái lập r7 ở Ke gốc từng đồng
    assert abs(KE_R7 - 0.149) < 1e-12
    A = run_cfg(M.CFG_A, KE_R7); A7 = run_cfg(M.CFG_A7, KE_R7); B7 = run_cfg(M.CFG_B7, KE_R7)
    sc = [("A dcf nghich", A["dcf_nghich"], 21407), ("A dcf coso", A["dcf_coso"], 32925), ("A dcf thuan", A["dcf_thuan"], 41779),
          ("A ev", A["ev"], 29817), ("A7 dcf coso", A7["dcf_coso"], 33072), ("A7 ev", A7["ev"], 32182), ("B7 ev", B7["ev"], 37060)]
    for lab, got, exp in sc:
        P(f"SELFCHECK {lab}: {got} vs {exp} lệch {got - exp}"); assert got == exp
    # ---- rf ứng viên
    t = tpcp(); w10 = t[t.year.between(2016, 2025)].yield_pct; w10b = t[t.year.between(2017, 2026)].yield_pct; w15 = t[t.year.between(2011, 2025)].yield_pct
    dep10, dep15 = deposit_avg(10), deposit_avg(15)
    gdp_g, gdp_win = gdp_nominal_growth()
    c_lo, c_hi = INFL_TARGET[0] + REAL_LR[0], INFL_TARGET[1] + REAL_LR[1]; c_mid = (c_lo + c_hi) / 2
    b10 = float(w10.median())
    rf_c = (b10 + c_mid) / 2 if abs(b10 - c_mid) <= 1.0 else c_mid       # LUẬT PREREG §3
    rfs = pd.DataFrame([
        dict(cand="a TPCP 10Y hiện tại", rf=TPCP_NOW, note="ADB 28/10/2026 [SRC]"),
        dict(cand="b TPCP 10Y trung vị 2016-25", rf=b10, note=f"TB {w10.mean():.2f}; [UL phần lớn — xem data/tpcp10y_annual.csv]"),
        dict(cand="b' TPCP 10Y trung vị 2017-26", rf=float(w10b.median()), note="[UL]"),
        dict(cand="b TPCP 10Y trung vị 2011-25", rf=float(w15.median()), note="[UL]"),
        dict(cand="c building-block thấp", rf=c_lo, note="lạm phát 4,0 + thực 2,0"),
        dict(cand="c building-block giữa", rf=c_mid, note="4,25 + 2,5"),
        dict(cand="c building-block cao", rf=c_hi, note="4,5 + 3,0"),
        dict(cand="c' Damodaran-literal (TPCP − default spread)", rf=TPCP_NOW - DAMO_DS, note="4,467 − 2,56: THỰC ÂM so lạm phát ⇒ vi phạm K3"),
        dict(cand="d Big-4 12M TB 10 năm", rf=dep10, note="deposit_rate_vn.py, caveat hindsight (b)"),
        dict(cand="d Big-4 12M TB 15 năm", rf=dep15, note="như trên"),
        dict(cand=f"e GDP danh nghĩa CAGR {gdp_win}", rf=gdp_g * 100, note="mốc TRẦN g, không phải rf"),
        dict(cand="f hiện hành (đối chứng)", rf=7.4, note="max(Big-4 12M 6,8 ; CCTG 12M 7,4)")])
    rfs["rf"] = rfs.rf.round(3); P("\n== rf ứng viên ==\n" + rfs.to_string(index=False)); rfs.to_csv(csv("out_rf_candidates.csv"), index=False)
    P(f"LUẬT rf: |b10 {b10:.2f} − c_mid {c_mid:.2f}| = {abs(b10 - c_mid):.2f}pp {'≤' if abs(b10 - c_mid) <= 1 else '>'} 1,0 ⇒ rf trung tâm = {rf_c:.2f}%")
    # ---- β, ERP
    b_dgc, b_peer = blume(BETA_RAW_DGC), blume(BETA_RAW_PEER_MED); beta_c = (b_dgc + b_peer) / 2
    erp_damo = DAMO_MATURE + DAMO_CRP
    P(f"β Blume: DGC {b_dgc:.3f} ; peer {b_peer:.3f} (N={N_PEER}) ⇒ điểm {beta_c:.3f}, khoảng [{min(b_dgc, b_peer):.3f}, {max(b_dgc, b_peer):.3f}]")
    # ---- đối chiếu độc lập (KHÔNG dùng để chọn)
    x = []
    for a, b in (("2011-10-28", "2026-10-28"), ("2016-10-28", "2026-10-28")):
        n = int(b[:4]) - int(a[:4]); (p0, pe0), (p1, pe1) = VNI[a], VNI[b]
        pr = (p1 / p0) ** (1 / n) - 1; rer = (pe1 / pe0) ** (1 / n) - 1
        x.append(dict(check=f"VNINDEX giá CAGR {a[:4]}-{b[:4]}", lo=pr * 100, hi=pr * 100, note="[BQ]"))
        x.append(dict(check=f"VNINDEX TR CAGR {a[:4]}-{b[:4]}", lo=pr * 100 + DIV_YLD[0], hi=pr * 100 + DIV_YLD[1], note="giá [BQ] + cổ tức [UL]"))
        x.append(dict(check=f"  … bỏ đổi P/E ({pe0}→{pe1}: {rer * 100:+.2f}%/năm)", lo=((1 + pr) / (1 + rer) - 1) * 100 + DIV_YLD[0], hi=((1 + pr) / (1 + rer) - 1) * 100 + DIV_YLD[1], note="lợi suất do LN tạo ra"))
    ep = 100 / VNI_PE_NOW
    x.append(dict(check="E/P VNINDEX + lạm phát kỳ vọng (Ke danh nghĩa, tăng trưởng thực=0)", lo=ep + INFL_TARGET[0], hi=ep + INFL_TARGET[1], note=f"E/P {ep:.2f}% [BQ]"))
    x.append(dict(check="Ke thị trường (β=1) theo luật trung tâm", lo=rf_c + erp_damo, hi=rf_c + erp_damo, note="rf_c + 8,13"))
    x.append(dict(check="Ke thị trường r7 / fleet dcf_valuation", lo=7.4 + 6.5, hi=7.4 + 7.5, note="7,4 + 6,5 (fleet) ; 7,4 + 7,5 (DGC r7)"))
    X = pd.DataFrame(x); X[["lo", "hi"]] = X[["lo", "hi"]].round(2); P("\n== Đối chiếu độc lập ==\n" + X.to_string(index=False)); X.to_csv(csv("out_market_xcheck.csv"), index=False)
    imp_erp = (float(X[X.check.str.startswith("E/P")].lo.iloc[0]) + float(X[X.check.str.startswith("E/P")].hi.iloc[0])) / 2 - rf_c
    # ---- Ke ứng viên (khai theo PREREG)
    K = [("f hiện hành r7 (7,4 + 1,0×7,5)", 7.4, 1.0, 7.5),
         ("fleet dcf_valuation (7,4 + 1,0×6,5)", 7.4, 1.0, 6.5),
         ("TRUNG TÂM PREREG: rf_c + β_c × Damodaran 8,13", rf_c, beta_c, erp_damo),
         ("rf_c + β_c × ERP ngầm định thị trường", rf_c, beta_c, imp_erp),
         ("a TPCP hiện tại + β_c × 8,13", TPCP_NOW, beta_c, erp_damo),
         ("b TPCP trung vị 10Y + β_c × 8,13", b10, beta_c, erp_damo),
         ("c' Damodaran-literal (TPCP−DS) + β_c × 8,13", TPCP_NOW - DAMO_DS, beta_c, erp_damo),
         ("d Big-4 TB 10 năm + 1,0×7,5 (làm mượt quy ước cũ)", dep10, 1.0, 7.5),
         ("VÙNG thấp: c_lo + β_lo × ERP ngầm định", c_lo, min(b_dgc, b_peer), imp_erp),
         ("VÙNG cao: c_hi + β_hi × 8,13", c_hi, max(b_dgc, b_peer), erp_damo)]
    rows = []
    for lab, rf, be, erp in K:
        ke_ = round((rf + be * erp) / 100, 4)
        rows.append(dict(cand=lab, rf=round(rf, 2), beta=round(be, 3), erp=round(erp, 2), ke=ke_, **run_cfg(M.CFG_A, ke_)))
    KC = pd.DataFrame(rows); P("\n== Ke ứng viên → tầng A (DCF 3 kịch bản + EV blend) ==\n" + KC.to_string(index=False)); KC.to_csv(csv("out_ke_candidates.csv"), index=False)
    # ---- lưới Ke 10-16%
    G = pd.DataFrame([dict(ke=k / 1000, **run_cfg(M.CFG_A, k / 1000), ev_A7=run_cfg(M.CFG_A7, k / 1000)["ev"], dcf_coso_A7=run_cfg(M.CFG_A7, k / 1000)["dcf_coso"]) for k in range(100, 165, 5)])
    P("\n== Lưới Ke (tầng A; cột A7 để so) ==\n" + G.to_string(index=False)); G.to_csv(csv("out_ke_grid.csv"), index=False)
    # ---- g × Ke (DCF cơ sở tầng A)
    gk = pd.DataFrame([dict(g=g, ke=k / 1000, dcf_coso=run_cfg(M.CFG_A, k / 1000, g=g)["dcf_coso"]) for g in (0.02, 0.03, 0.04, 0.05) for k in range(100, 165, 10) if k / 1000 - g >= 0.03])
    gkp = gk.pivot(index="g", columns="ke", values="dcf_coso"); P("\n== DCF cơ sở: g × Ke (ô trống: Ke − g < 3pp) ==\n" + gkp.to_string()); gk.to_csv(csv("out_g_x_ke.csv"), index=False)
    # ---- phân rã DCF cơ sở
    D = []
    for k_e in (0.11, 0.13, 0.149, round((rf_c + beta_c * erp_damo) / 100, 4)):
        d = dcf_decomp(M.CFG_A, "coso", k_e, 0.03)
        D.append(dict(ke=k_e, **{f"{a}": round(v) for a, v in d["all"].items()}, tv_share=round(d["all"]["tv"] / d["all"]["total"], 3),
                      ns_ops=round(d["all"]["total"] - d["no_ns"]["total"])))
    D = pd.DataFrame(D); P("\n== Phân rã DCF cơ sở tầng A (đ/cp) ==\n" + D.to_string(index=False)); D.to_csv(csv("out_dcf_decomp.csv"), index=False)
    M.CFG.clear(); M.CFG.update(M.CFG_A)
    open(csv("run_stdout.txt"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
