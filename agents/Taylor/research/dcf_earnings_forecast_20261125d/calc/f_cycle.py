# -*- coding: utf-8 -*-
"""f_cycle.py — PRELOCK_J3_CYCLE §1–§3 (A' mô tả, B' dự báo có chu kỳ). In: ../out_J3/events.parquet, ../out_J3/fc.parquet, ../in_cycle/*.
Out: ../out_CY/cyc_features.parquet, A2_*.csv, B2_*.csv, cycle_fit.json"""
import os, csv, json
import numpy as np, pandas as pd, duckdb
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, ".."); IN = os.path.join(D, "out_J3"); OUT = os.path.join(D, "out_CY"); os.makedirs(OUT, exist_ok=True)
WC = "/home/trido/thanhdt/WorkingClaude"; SEED = 20261125; B = 2000; LOG = {}
IS_END = pd.Timestamp("2019-12-31")
# ---------------- 1. đặc trưng chu kỳ PIT trên toàn bộ sự kiện của mã ----------------
ev = pd.read_parquet(os.path.join(IN, "events.parquet")).sort_values(["ticker", "qi"]).reset_index(drop=True)
ttm = ev[[f"NP_P{k}" for k in range(4)]].sum(axis=1, min_count=4)
ev["roe_ttm"] = np.where(ev.E > 0, ttm / ev.E, np.nan); ev["roe_ttm"] = ev.roe_ttm.clip(-1, 1)    # chặn cực trị (E rất nhỏ)
g = ev.groupby("ticker").roe_ttm
ev["cyc"] = g.transform(lambda s: s.rolling(32, min_periods=16).std())                    # gồm hiện tại (K ≤ K hiện tại)
ev["tc8"] = g.transform(lambda s: s.rolling(32, min_periods=16).mean())
ev["med_prev"] = g.transform(lambda s: s.shift(1).rolling(32, min_periods=16).median())
ev["sd_prev"] = g.transform(lambda s: s.shift(1).rolling(32, min_periods=16).std())
dev = ev.roe_ttm - ev.med_prev
ev["phase"] = np.where(ev.med_prev.isna() | ev.sd_prev.isna(), "NA", np.where(dev > 0.5 * ev.sd_prev, "PEAK", np.where(dev < -0.5 * ev.sd_prev, "TROUGH", "MID")))
ev["qps"] = ev.qp.astype(str)
ev["cyc_t"] = ev.groupby("qps").cyc.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["LO", "MID", "HI"]).astype(str) if s.notna().sum() >= 9 else pd.Series("NA", index=s.index))
ev.loc[ev.cyc.isna(), "cyc_t"] = "NA"
# COMM (bản đồ đóng băng) & FIN (route PIT tại K)
cm = {r["ticker"]: r["commodity"] for r in csv.DictReader(open(os.path.join(D, "in_cycle", "commodity_map.csv"))) if r["in_primary"] == "Y"}
ev["fam"] = ev.ticker.map(cm)
rat = duckdb.connect().execute(f"SELECT ticker, CAST(time AS DATE) AS rt, route AS route_pit FROM read_parquet('{WC}/data/bq_cache/fa_ratings_8l.parquet')").df()
rat["rt"] = pd.to_datetime(rat.rt).astype(ev.K.dtype)
ev = pd.merge_asof(ev.sort_values("K"), rat.sort_values("rt"), left_on="K", right_on="rt", by="ticker", direction="backward").sort_values(["ticker", "qi"]).reset_index(drop=True)
ev["grp"] = np.where(ev.fam.notna(), "COMM", np.where(ev.route_pit.isin(["BANK", "SECURITIES", "INSURANCE"]), "FIN", np.where(ev.cyc_t != "NA", "CYC_" + ev.cyc_t, "NA")))
# giá hàng hoá WB (PIT: tháng m biết từ cuối tháng m + 35 ngày)
x = pd.read_excel(os.path.join(D, "in_cycle", "CMO-Historical-Data-Monthly.xlsx"), sheet_name="Monthly Prices", header=None)
hdr = [str(h).strip() if isinstance(h, str) else h for h in x.iloc[4].tolist()]
COLS = {"rubber": "Rubber, RSS3", "crude oil": "Crude oil, average", "urea": "Urea", "DAP": "DAP", "sugar": "Sugar, world"}
wb = x.iloc[6:].copy(); wb.columns = ["m"] + hdr[1:]; wb = wb[wb.m.astype(str).str.match(r"^\d{4}M\d{2}$")]
wb["mp"] = pd.PeriodIndex(wb.m.str.replace("M", "-"), freq="M"); wb = wb.set_index("mp")
wbp = pd.DataFrame({k: pd.to_numeric(wb[v], errors="coerce") for k, v in COLS.items()})
known = (wbp.index.to_timestamp(how="end").normalize() + pd.Timedelta(days=35))
LOG["wb_last_month"] = str(wbp.index.max()); LOG["wb_nonnull_from_2006"] = {k: int(wbp.loc["2006-01":, k].notna().sum()) for k in COLS}
ki = np.searchsorted(known.values, ev.K.values.astype("datetime64[ns]"), side="right") - 1        # tháng biết gần nhất ≤ K
c_yoy = np.full(len(ev), np.nan); cph = np.full(len(ev), np.nan)
for fam in COLS:
    p = wbp[fam].values; mm = (ev.fam == fam).values & (ki >= 72)
    for i in np.where(mm)[0]:
        j = ki[i]; a = np.nanmean(p[j - 2:j + 1]); b = np.nanmean(p[j - 14:j - 11]); l = np.nanmean(p[j - 59:j + 1])
        c_yoy[i] = np.log(a / b); cph[i] = np.log(a / l)
ev["c_yoy"] = c_yoy; ev["cph"] = np.where(np.isnan(cph), "NA", np.where(cph > 0.15, "HIGH", np.where(cph < -0.15, "LOW", "MID")))
LOG["n_COMM_events_with_c"] = int(np.isfinite(c_yoy).sum())
# ---------------- 2. fit φ theo ô (IS, mục tiêu ≤ 2019) & β COMMF ----------------
base = ev.iuK & ev.hist8 & (ev.E > 0) & ev.era.isin(["IS", "OOS"])
ev["rho"] = ttm / ev.E; ev["cell"] = ev.cyc_t.astype(str) + "|" + ev.phase
fit = ev[base & (ev.era == "IS") & ev.KA4.notna() & (ev.KA4 <= IS_END) & ev[["A1", "A2", "A3", "A4"]].notna().all(axis=1) & (ev.cyc_t != "NA") & (ev.phase != "NA")].copy()
fit["y"] = (fit.A1 + fit.A2 + fit.A3 + fit.A4) / fit.E - fit.roe_tc5; fit["x"] = fit.rho - fit.roe_tc5
for c in ("x", "y"):
    lo, hi = fit[c].quantile([0.01, 0.99]); fit[c] = fit[c].clip(lo, hi)
PHI = {}
for cell, s in fit.groupby("cell"):
    PHI[cell] = {"n": int(len(s)), "phi_raw": float((s.x * s.y).sum() / (s.x ** 2).sum())}
    PHI[cell]["phi"] = float(np.clip(PHI[cell]["phi_raw"], 0, 1)) if len(s) >= 100 else 0.65
LOG["phi"] = PHI; LOG["phi_fit_n"] = int(len(fit))
ev["phi"] = ev.cell.map({k: v["phi"] for k, v in PHI.items()}).fillna(0.65)
NP = ev[[f"NP_P{k}" for k in range(8)]].values; RV = ev[[f"Revenue_P{k}" for k in range(8)]].values; E = ev.E.values
BET = {}
for h in (1, 2, 3, 4):
    m = (base & (ev.era == "IS") & ev[f"KA{h}"].notna() & (ev[f"KA{h}"] <= IS_END) & np.isfinite(ev.c_yoy)).values
    rv = RV[m, 4 - h]; ok = rv > 0
    yy = ((ev[f"A{h}"].values[m] - NP[m, 4 - h]) / np.where(ok, rv, np.nan))[ok]; xx = ev.c_yoy.values[m][ok]
    f = np.isfinite(yy) & np.isfinite(xx); yy, xx = yy[f], xx[f]; lo, hi = np.quantile(yy, [0.01, 0.99]); yy = np.clip(yy, lo, hi)
    BET[h] = {"n": int(len(yy)), "beta": float((xx * yy).sum() / (xx ** 2).sum()), "n_tickers": int(ev[m].ticker.nunique())}
LOG["beta_COMMF"] = BET
# ---------------- 3. dự báo B' trên mẫu J2 ----------------
evb = ev[base].copy().reset_index(drop=True)
NP = evb[[f"NP_P{k}" for k in range(8)]].values; RV = evb[[f"Revenue_P{k}" for k in range(8)]].values; E = evb.E.values
tt = NP[:, :4].sum(1); drift = (NP[:, :4] - NP[:, 4:]).mean(1)
with np.errstate(all="ignore"):
    gg = np.clip(RV[:, :4].sum(1) / RV[:, 4:].sum(1) - 1, -0.5, 0.5); mg = np.clip(tt / RV[:, :4].sum(1), -0.5, 0.5)
gg = np.where(np.isfinite(gg), gg, np.nan); mg = np.where(np.isfinite(mg), mg, np.nan)
rho = tt / E; rbar = evb.roe_tc5.values; phi = evb.phi.values; isc = evb.fam.notna().values
rows = []
for h in (1, 2, 3, 4):
    F = {"SRW": NP[:, 4 - h], "SRWD": NP[:, 4 - h] + drift, "MxR": RV[:, 4 - h] * (1 + gg) * mg, "MR": E * (rbar + 0.65 ** (h / 4) * (rho - rbar)) / 4}
    F["ENS"] = np.where(np.isfinite(F["SRWD"]) & np.isfinite(F["MxR"]) & np.isfinite(F["MR"]), np.nanmedian(np.vstack([F["SRWD"], F["MxR"], F["MR"]]), axis=0), np.nan)
    F["D0imp"] = rbar * E / 4; F["D0tc8"] = evb.tc8.values * E / 4
    F["MRph"] = E * (rbar + phi ** (h / 4) * (rho - rbar)) / 4
    F["ENSph"] = np.where(np.isfinite(F["SRWD"]) & np.isfinite(F["MxR"]) & np.isfinite(F["MRph"]), np.nanmedian(np.vstack([F["SRWD"], F["MxR"], F["MRph"]]), axis=0), np.nan)
    F["COMMF"] = np.where(isc & np.isfinite(evb.c_yoy.values), NP[:, 4 - h] + BET[h]["beta"] * evb.c_yoy.values * RV[:, 4 - h], np.nan)
    e4 = np.vstack([F["SRWD"], F["MxR"], F["MRph"], F["COMMF"]])
    F["ENScm"] = np.where(np.isfinite(F["COMMF"]) & np.isfinite(F["ENSph"]), np.nanmedian(e4, axis=0), np.where(isc, np.nan, F["ENSph"]))
    A = evb[f"A{h}"].values
    d = pd.DataFrame({"ticker": evb.ticker, "qps": evb.qps, "yr": evb.yr, "era": evb.era, "h": h, "grp": evb.grp, "phase": evb.phase, "cph": evb.cph, "fam": evb.fam.fillna(""), "A": A, "E": E})
    for k, v in F.items():
        d["e_" + k] = (A - v) / E
    rows.append(d)
fc = pd.concat(rows, ignore_index=True)
# kiểm: SRW/ENS/D0imp phải trùng fc J3 (b_forecast) — cùng công thức
o = pd.read_parquet(os.path.join(IN, "fc.parquet"))[["ticker", "qp", "h", "e_SRW", "e_ENS", "e_D0imp"]].rename(columns={"qp": "qps"})
chk = fc.merge(o, on=["ticker", "qps", "h"], suffixes=("", "_b"))
LOG["recompute_vs_b_forecast_maxabs"] = {k: float(np.nanmax(np.abs(chk["e_" + k] - chk["e_" + k + "_b"]))) for k in ("SRW", "ENS", "D0imp")}
fc.to_parquet(os.path.join(OUT, "fc_cy.parquet"))
ev[["ticker", "quarter", "qps", "K", "roe_ttm", "cyc", "cyc_t", "tc8", "phase", "fam", "route_pit", "grp", "c_yoy", "cph", "phi", "roe_tc5", "rho"]].to_parquet(os.path.join(OUT, "cyc_features.parquet"))
# ---------------- 4. A' mô tả: nhóm × pha ----------------
fA = fc[np.isfinite(fc[["e_SRW", "e_ENS", "e_D0imp"]]).all(axis=1) & np.isfinite(fc.A)]
a = []
for (h, era, grp, ph), s in fA[fA.h == 1].groupby(["h", "era", "grp", "phase"]):
    if len(s) < 30:
        continue
    yb = s.groupby("yr").e_D0imp.median()
    a.append({"h": h, "era": era, "grp": grp, "phase": ph, "n": len(s), "n_tk": s.ticker.nunique(), "MdAE_SRW": s.e_SRW.abs().median(), "MdAE_ENS": s.e_ENS.abs().median(), "MdAE_D0imp": s.e_D0imp.abs().median(),
              "bias_ENS": s.e_ENS.median(), "bias_D0imp": s.e_D0imp.median(), "D0imp_bias_yrs_pos": int((yb > 0).sum()), "D0imp_bias_yrs_neg": int((yb < 0).sum()),
              "share_absD0imp_err": float(s.e_D0imp.abs().sum() / fA[(fA.h == 1) & (fA.era == era)].e_D0imp.abs().sum())})
A2 = pd.DataFrame(a); A2.to_csv(os.path.join(OUT, "A2_grp_phase.csv"), index=False)
a = []
for (era, grp), s in fA[fA.h == 1].groupby(["era", "grp"]):
    a.append({"era": era, "grp": grp, "n": len(s), "n_tk": s.ticker.nunique(), "MdAE_ENS": s.e_ENS.abs().median(), "MdAE_D0imp": s.e_D0imp.abs().median(), "R_D0imp_vs_SRW": s.e_D0imp.abs().median() / s.e_SRW.abs().median(),
              "bias_D0imp": s.e_D0imp.median(), "share_n": len(s) / ((fA.h == 1) & (fA.era == era)).sum(), "share_absD0imp_err": float(s.e_D0imp.abs().sum() / fA[(fA.h == 1) & (fA.era == era)].e_D0imp.abs().sum())})
pd.DataFrame(a).to_csv(os.path.join(OUT, "A2_grp.csv"), index=False)
a = []   # COMM theo pha giá hàng hoá và theo họ
for (era, cp), s in fA[(fA.h == 1) & (fA.grp == "COMM")].groupby(["era", "cph"]):
    a.append({"era": era, "cut": "cph", "v": cp, "n": len(s), "n_tk": s.ticker.nunique(), "bias_D0imp": s.e_D0imp.median(), "bias_ENS": s.e_ENS.median(), "MdAE_ENS": s.e_ENS.abs().median(), "MdAE_D0imp": s.e_D0imp.abs().median()})
for (era, fm), s in fA[(fA.h == 1) & (fA.grp == "COMM")].groupby(["era", "fam"]):
    a.append({"era": era, "cut": "fam", "v": fm, "n": len(s), "n_tk": s.ticker.nunique(), "bias_D0imp": s.e_D0imp.median(), "bias_ENS": s.e_ENS.median(), "MdAE_ENS": s.e_ENS.abs().median(), "MdAE_D0imp": s.e_D0imp.abs().median()})
pd.DataFrame(a).to_csv(os.path.join(OUT, "A2_comm.csv"), index=False)
# ---------------- 5. B' so sánh cặp ----------------
def ratio(s, k, ref, nmin=20):   # COMM (~15 sự kiện/quý) dùng nmin=8 — khai trong REPORT, chọn trước khi xem số COMM
    s = s[np.isfinite(s["e_" + k]) & np.isfinite(s["e_" + ref]) & np.isfinite(s.A)]
    q = s.groupby("qps").agg(a=("e_" + k, lambda v: np.median(np.abs(v))), b=("e_" + ref, lambda v: np.median(np.abs(v))), yr=("yr", "first"), n=("A", "size"))
    q = q[(q.n >= nmin) & (q.a > 0) & (q.b > 0)]
    if len(q) == 0:
        return None
    lr = np.log(q.a / q.b); ys = q.yr.unique(); rng = np.random.RandomState(SEED); by = {y: lr[q.yr == y].values for y in ys}
    res = np.array([np.concatenate([by[y] for y in rng.choice(ys, len(ys))]).mean() for _ in range(B)])
    yl = lr.groupby(q.yr).mean()
    return {"R": float(np.exp(lr.mean())), "ci99_lo": float(np.exp(np.percentile(res, 0.5))), "ci99_hi": float(np.exp(np.percentile(res, 99.5))), "n_ev": int(q.n.sum()), "n_q": int(len(q)),
            "n_yr": int(len(yl)), "yrs_better": int((yl < 0).sum()), "by_year": {int(k): round(float(np.exp(v)), 3) for k, v in yl.items()}}
out = []
PAIRS = [("ENSph", "ENS"), ("MRph", "MR"), ("D0tc8", "D0imp"), ("ENSph", "SRW"), ("ENS", "SRW"), ("D0tc8", "SRW"), ("COMMF", "SRW"), ("COMMF", "ENS"), ("ENScm", "ENS"), ("ENScm", "SRW")]
for h in (1, 2, 3, 4):
    for era in ("IS", "OOS"):
        for scope in ("ALL", "COMM", "CYC_HI", "CYC_MID", "CYC_LO", "FIN", "COMM+CYC_HI"):
            s = fc[(fc.h == h) & (fc.era == era)]
            s = s if scope == "ALL" else (s[s.grp.isin(["COMM", "CYC_HI"])] if scope == "COMM+CYC_HI" else s[s.grp == scope])
            for k, ref in PAIRS:
                if scope not in ("ALL", "COMM") and k in ("COMMF",):
                    continue
                r = ratio(s, k, ref, 8 if scope == "COMM" else 20)
                if r:
                    out.append({"h": h, "era": era, "scope": scope, "model": k, "ref": ref, **r})
B2 = pd.DataFrame(out); B2.to_csv(os.path.join(OUT, "B2_pairs.csv"), index=False)
json.dump(LOG, open(os.path.join(OUT, "cycle_fit.json"), "w"), indent=1, default=str)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
print(json.dumps(LOG, indent=1, default=str))
print(pd.read_csv(os.path.join(OUT, "A2_grp.csv")).round(4).to_string(index=False))
print(A2.round(4).to_string(index=False))
print(B2[B2.h == 1].drop(columns=["by_year"]).round(3).to_string(index=False))
