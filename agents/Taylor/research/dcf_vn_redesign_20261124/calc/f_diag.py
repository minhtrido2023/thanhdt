# -*- coding: utf-8 -*-
"""f_diag.py — (a) chẩn đoán nguyên nhân gốc engine FCFE; mẫu ngẫu nhiên 24 mã + ca thất bại; đường tâm 4 ca.
Out: ../out/diag.json, sample_table.csv, cases_paths.csv"""
import os, json
import numpy as np, pandas as pd, duckdb
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out"); WC = "/home/trido/thanhdt/WorkingClaude"
vp = pd.read_parquet(os.path.join(OUT, "vp.parquet")).sort_values(["ticker", "ym"]).reset_index(drop=True)
u = vp[vp.in_universe & (vp.ym >= "2014-01")].copy()
res = {}
# 1. độ phủ engine A
A = pd.read_parquet(os.path.join(OUT, "engine_A.parquet"))
A["why"] = np.where(A.ok, "OK", A.reason.fillna("").str.slice(0, 24))
res["A_coverage"] = A.why.value_counts(normalize=True).round(4).to_dict(); res["A_n"] = len(A)
# 2. phân rã phương sai giữa-mã / trong-mã
def between(col):
    d = u[u[col].notna()]; k = d.groupby("ticker")[col].transform("size"); d = d[k >= 12]
    tot = d[col].var(); bet = d.groupby("ticker")[col].transform("mean").var()
    return {"between_share": float(bet / tot), "sd_total": float(np.sqrt(tot)), "n_tk": int(d.ticker.nunique())}
res["var_decomp"] = {v: between(f"lv_{v}") for v in ("A_fix", "B_fix", "C_fix", "D0_fix", "D_fix", "E_fix", "G1D0_fix")}
# 3. lv_A = lv_D0 + nhiễu riêng FCFE
q = u[u.lv_A_fix.notna() & u.lv_D0_fix.notna() & pd.PeriodIndex(u.ym, freq="M").month.isin([3, 6, 9, 12])].copy()
q["noise"] = q.lv_A_fix - q.lv_D0_fix
res["A_split"] = {"var_A": float(q.lv_A_fix.var()), "var_D0": float(q.lv_D0_fix.var()), "var_noise": float(q.noise.var()),
                  "corr_A_D0": float(np.corrcoef(q.lv_A_fix, q.lv_D0_fix)[0, 1]), "n": len(q)}
for era, (a, b) in {"IS": ("2014-01", "2019-12"), "OOS": ("2020-01", "2099")}.items():
    z = q[(q.ym >= a) & (q.ym <= b) & q.fwd36.notna()]
    for c in ("lv_A_fix", "lv_D0_fix", "noise"):
        res["A_split"][f"ic36_{c}_{era}"] = float(np.mean([spearmanr(g[c], g.fwd36)[0] for _, g in z.groupby("ym") if len(g) >= 30]))
# 4. nhóm luôn-đắt / luôn-rẻ của engine A và của D0: đặc điểm
c = duckdb.connect()
f = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, CF_OA_5Y, CF_Invest_5Y, CF_OA_3Y, CF_Invest_3Y, Debt_Eq_P0, Revenue_YoY_P0
    FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')""").df()
f["time"] = pd.to_datetime(f.time).astype("datetime64[ns]")
u2 = pd.merge_asof(u.sort_values("time"), f.sort_values("time"), on="time", by="ticker", direction="backward")
u2["capex_int"] = (-u2.CF_Invest_5Y / u2.CF_OA_5Y).where(u2.CF_OA_5Y > 0)
u2["pb"] = 1 / u2.bp
def groups(col, lo, hi, minobs=12):
    d = u2[u2[col].notna()]; g = d.groupby("ticker")
    med = g[col].median(); n = g.size(); med = med[n >= minobs]
    lab = pd.Series(np.where(med < np.log(lo), "always_exp", np.where(med > np.log(hi), "always_cheap", "mid")), index=med.index)
    d = d[d.ticker.isin(med.index)].copy(); d["grp"] = d.ticker.map(lab)
    tk = d.groupby("ticker").agg(grp=("grp", "first"), roe_tc=("roe_tc5", "median"), roe_min=("roe_min5", "median"), pb=("pb", "median"), capex_int=("capex_int", "median"),
                                 cfinv5=("CF_Invest_5Y", "median"), cfoa5=("CF_OA_5Y", "median"), payout=("payout", "median"), de=("Debt_Eq_P0", "median"),
                                 tv=("tv", "median"), route=("route", "first"), fwd36=("fwd36", "mean"))
    out = tk.groupby("grp").agg(n=("roe_tc", "size"), roe_tc=("roe_tc", "median"), roe_min=("roe_min", "median"), pb=("pb", "median"), capex_int=("capex_int", "median"),
                                payout=("payout", "median"), de=("de", "median"), tv_bn=("tv", lambda x: np.median(x) / 1e9), fwd36_log=("fwd36", "median")).round(3)
    rt = pd.crosstab(tk.grp, tk.route, normalize="index").round(3)
    return {"share": lab.value_counts(normalize=True).round(3).to_dict(), "traits": out.to_dict("index"), "route_mix": rt.to_dict("index")}
res["A_groups"] = groups("lv_A_fix", 0.75, 1.33)
res["D0_groups"] = groups("lv_D0_fix", 0.75, 1.33)
res["G1D0_groups"] = groups("lv_G1D0_fix", 0.75, 1.33)
# nhóm engine KHÔNG ra FV (FCFE<=0 / CFO gate): lợi suất 36T so với nhóm có FV
qq = u[pd.PeriodIndex(u.ym, freq="M").month.isin([3, 6, 9, 12]) & u.fwd36.notna() & ~u.route.isin(["BANK", "INSURANCE", "SECURITIES"])]
res["A_noFV_vs_FV_fwd36_median"] = {"noFV": float(qq[qq.lv_A_fix.isna()].fwd36.median()), "FV": float(qq[qq.lv_A_fix.notna()].fwd36.median()),
                                    "n_noFV": int(qq.lv_A_fix.isna().sum()), "n_FV": int(qq.lv_A_fix.notna().sum()),
                                    "ic36_D0_in_noFV": float(np.mean([spearmanr(g.lv_D0_fix, g.fwd36)[0] for _, g in qq[qq.lv_A_fix.isna() & qq.lv_D0_fix.notna()].groupby("ym") if len(g) >= 30]))}
json.dump(res, open(os.path.join(OUT, "diag.json"), "w"), indent=1, default=float)
print(json.dumps(res, indent=0, default=float)[:6000])
# 5. mẫu ngẫu nhiên 24 mã + ca thất bại khai trước
rng = np.random.default_rng(20261124)
ever = vp[vp.in_universe].groupby("ticker").agg(route=("route", "first"), n=("ym", "size"))
pick = []
for r_, g in ever.groupby("route"):
    k = 3 if r_ != "COMPOUNDER" else 6
    pick += list(rng.choice(sorted(g.index), size=min(k, len(g)), replace=False))
FAIL = ["FLC", "ROS", "HVG", "TTF", "HNG", "OGC", "ITA", "HBC", "PVX", "DLG", "HAG", "KSA"]
rows = []
for tk in pick + FAIL + ["VCS", "DGC", "VNM", "HPG"]:
    d = vp[(vp.ticker == tk) & (vp.ym >= "2014-01")]
    rec = {"ticker": tk, "set": "random" if tk in pick else ("fail_list" if tk in FAIL else "case"), "route": d.route.iloc[0] if len(d) else None,
           "months": len(d), "months_in_uni": int(d.in_universe.sum()) if len(d) else 0, "first": d.ym.min() if len(d) else None, "last": d.ym.max() if len(d) else None,
           "close_last_over_first": float(d.Close.iloc[-1] / d.Close.iloc[0]) if len(d) else np.nan}
    for v in ("D0_fix", "G1D0_fix", "A_fix"):
        x = d[f"lv_{v}"].dropna(); s = np.sign(x.values)
        rec[f"{v}_shareV>P"] = float((s > 0).mean()) if len(s) else np.nan
        rec[f"{v}_n_cross"] = int((s[1:] != s[:-1]).sum()) if len(s) > 1 else 0
        run = 0; mx = 0
        for i in range(len(s)):
            run = run + 1 if (i and s[i] == s[i - 1]) else 1; mx = max(mx, run)
        rec[f"{v}_max_run_m"] = mx; rec[f"{v}_medVP"] = float(np.exp(x.median())) if len(x) else np.nan
    rows.append(rec)
T = pd.DataFrame(rows); T.to_csv(os.path.join(OUT, "sample_table.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(T.round(2).to_string())
# 6. đường tâm 4 ca (cuối năm) cho báo cáo
cp = vp[vp.ticker.isin(["VCS", "DGC", "VNM", "HPG"]) & vp.ym.str.endswith(("-06", "-12")) & (vp.ym >= "2010-06") & (vp.ym <= "2022-12")]
o = cp[["ticker", "ym", "Close", "roe", "roe_tc5", "roe_min5"]].copy(); o["PB"] = 1 / cp.bp
for v in ("B_fix", "D0_fix", "H_fix", "G1D0_fix", "E_fix"):
    o[f"V_{v}"] = np.exp(cp[f"lv_{v}"]) * cp.Close
o.round(3).to_csv(os.path.join(OUT, "cases_paths.csv"), index=False)
print(o[o.ym.str.endswith("-12")].round(2).to_string())
