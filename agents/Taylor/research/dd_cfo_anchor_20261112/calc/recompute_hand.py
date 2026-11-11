# -*- coding: utf-8 -*-
"""recompute_hand.py — tái tính ĐỘC LẬP (không import bases/common) nền A1, B3, C1, D1, D2, E cho 5 mã tại
as-of 2023Q4 từ ticker_financial gốc; so với bases.build(). r/g_exp/g_T/MC0 lấy từ panel (tham số engine, không phải
đối tượng kiểm). Run: $DNA_PYEXE -W ignore recompute_hand.py -> ../out/recompute_hand.csv
"""
import os, sys
import numpy as np, pandas as pd, duckdb
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
WC = "/home/trido/thanhdt/WorkingClaude"
f = duckdb.connect().execute(f"SELECT * FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
f["time"] = pd.to_datetime(f.time)
f = f.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"], keep="last")
pan = pd.read_parquet(os.path.join(HERE, "..", "..", "dd_blend_20261111", "out", "panel.parquet")).reset_index(drop=True)
ASOF = pd.Timestamp("2023-12-29")
TICK = ["FPT", "HPG", "PNJ", "DGC", "REE"]


def dcf(base, g, gT, r, b1, bT):
    s = 0.0
    for y in range(1, 6):
        s += base * (1 + g) ** y * (1 - b1) / (1 + r) ** y
    return s + base * (1 + g) ** 5 * (1 + gT) * (1 - bT) / (r - gT) / (1 + r) ** 5


def raw(tk, ft):
    h = f[(f.ticker == tk) & (f.time <= ft)].copy()
    L = h.iloc[-1]
    ttm = lambda row: sum(float(row[c]) for c in ("NP_P0", "NP_P1", "NP_P2", "NP_P3") if pd.notna(row[c]))
    ni = []
    for k in range(3):   # TTM tại t0, t0-365, t0-730 (như engine _annual_series)
        tgt = L.time - pd.Timedelta(days=365 * k)
        c = h[h.time <= tgt + pd.Timedelta(days=20)]
        ni.append(ttm(c.loc[(c.time - tgt).abs().idxmin()]))
    hq = h.copy(); hq["qp"] = pd.PeriodIndex(hq.quarter, freq="Q"); hq = hq.drop_duplicates("qp", keep="last").set_index("qp")
    q0 = pd.Period(L.quarter, freq="Q")
    cfo = [sum(float(hq.loc[q0 - 4 * j - i, "CF_OA_P0"]) for i in range(4)) for j in range(3)]
    ni_q = sum(float(hq.loc[q0 - i, "NP_P0"]) for i in range(4))
    rev = [sum(float(hq.loc[q0 - 4 * j - i, "Revenue_P0"]) for i in range(4)) for j in range(3)]
    return L, ni, cfo, ni_q, rev


rows = []
sys.path.insert(0, HERE)
import bases as Bm
p, E1, E2, V, M0, A = Bm.build()
for tk in TICK:
    i = int(np.where((p.ticker == tk) & (p["asof"] == ASOF))[0][0])
    pr = p.iloc[i]; L, ni, cfo, ni_q, rev = raw(tk, pr.fin_time)
    assert L.time <= ASOF
    g, gT, r = pr.g_exp, pr.g_T, pr.r
    roe = L.ROE3Y if pd.notna(L.ROE3Y) else L.ROE_Trailing
    roic = L.ROIC3Y if pd.notna(L.ROIC3Y) else roe
    NI3 = sum(ni); NIn = float(np.median(ni)); CFO3 = float(L.CF_OA_3Y); CPX3 = -float(L.CF_Invest_3Y)
    CPX5 = -float(L.CF_Invest_5Y)
    DA = float(L.EBITDA_P0) - float(L.EBITM_P0) * rev[0]
    bE = (min(max(g / roe, 0), .8), min(max(gT / roe, 0), .8)); bI = (min(max(g / roic, 0), .8), min(max(gT / roic, 0), .8))
    A1 = dcf(NIn * min(max(CFO3 / NI3, 0), 1), g, gT, r, *bE)
    B3 = dcf(float(np.median(cfo)), g, gT, r, *bI)
    C1 = dcf(NI3 / 3 + DA - min(CPX3 / 3, DA), g, gT, r, *bE)
    D1 = dcf(CFO3 / 3 - CPX5 / 5, g, gT, r, 0, 0)
    # D2: trung vị ngành độc lập — dựng lại CPX3/DT3 cho mọi mã cùng nhóm, cùng as-of, từ dữ liệu gốc
    peers = p[(p["asof"] == ASOF) & (p.grp == pr.grp)]
    cis = []
    for _, pp in peers.iterrows():
        try:
            Lp, _, _, _, rv = raw(pp.ticker, pp.fin_time)
            if sum(rv) > 0 and pd.notna(Lp.CF_Invest_3Y):
                cis.append(-float(Lp.CF_Invest_3Y) / sum(rv))
        except Exception:
            pass
    m = float(np.median(cis)) if len(cis) >= 5 else np.nan
    D2 = dcf(CFO3 / 3 - m * rev[0], g, gT, r, 0, 0)
    qa = NI3 > 0 and CFO3 / NI3 >= 0.8; qb = all(c > 0 for c in cfo)
    qc = abs(ni_q - cfo[0]) / float(L.totalAsset_P0) <= 0.10
    w = (qa + qb + qc) / 3
    Ve = dcf(NIn, g, gT, r, *bE); Vc = dcf(CFO3 / 3 - min(CPX3 / 3, DA), g, gT, r, 0, 0)
    cb = CFO3 / 3 - min(CPX3 / 3, DA)
    Ev = w * Ve + (1 - w) * Vc if cb > 0 else np.nan   # cổng PRELOCK: nền ≤ 0 ⇒ không định nghĩa
    for k, v in (("A1", A1), ("B3", B3), ("C1", C1), ("D1", D1), ("D2", D2), ("E", Ev)):
        rows.append({"ticker": tk, "base": k, "hand_bnVND": v / 1e9, "pipeline_bnVND": V[k][i] / 1e9,
                     "reldev": v / V[k][i] - 1 if np.isfinite(V[k][i]) else np.nan, "MC0_bn": pr.MC0 / 1e9,
                     "n_peers_D2": len(cis) if k == "D2" else None, "w_E": w if k == "E" else None})
d = pd.DataFrame(rows); d.to_csv(os.path.join(OUT, "recompute_hand.csv"), index=False)
print(d.round(4).to_string()); print("max |reldev|", float(np.nanmax(np.abs(d.reldev))))
