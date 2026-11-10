"""Part C — conditional edge by PIT regime variable (PREREG.md). 8 vars x 2 books x 2 outcomes = 32 tests."""
import gzip, io, json, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
WC = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WC)
OUT = f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
FN = f"{WC}/data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz"

df = pd.read_csv(io.BytesIO(gzip.open(FN).read()), low_memory=False)
d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d["ymd"])
d = d.set_index("ymd")[["nav_bal_ref", "nav_lag_ref", "vni_close"]].astype(float)
tx = df[(df.record_type == "TX") & (df.reason == "ENTRY_FILL") & (df.action == "buy")].copy()
tx["ymd"] = pd.to_datetime(tx["ymd"])
first = tx.sort_values("ymd").drop_duplicates("holding_id")            # one entry per holding (first fill)
sess = d.index

# ---- daily PIT variables on ledger sessions
vni = pd.read_csv(f"{OUT}/data/vnindex.csv", parse_dates=["time"]).set_index("time")
dt5 = pd.read_csv(f"{OUT}/data/dt5g.csv", parse_dates=["time"]).set_index("time")
xs = pd.read_csv(f"{OUT}/data/regen_xsec.csv", parse_dates=["time"]).set_index("time")
us = pd.read_csv(f"{WC}/data/us_market_history.csv", parse_dates=["time"]).set_index("time")
from value_radar import load_series
vr = load_series(update=False).set_index("time")
from deposit_rate_vn import deposit_events_df
dep = deposit_events_df().sort_values("time").set_index("time")["deposit_rate"]

V = pd.DataFrame(index=sess)
V["V1_dt5g_state"] = dt5["state"].reindex(sess).ffill()
V["V2_vni_ma200dev"] = (vni.Close / vni.MA200 - 1).reindex(sess)
V["V3_vni_dd252"] = (vni.Close / vni.Close.rolling(252, min_periods=120).max() - 1).reindex(sess)
V["V4_value_radar"] = vr["score"].reindex(sess, method="ffill")
dep_d = dep.reindex(dep.index.union(sess)).ffill()
V["V5_dep_chg6m"] = (dep_d - dep_d.shift(freq="182D").reindex(dep_d.index, method=None)).reindex(sess) if False else \
    pd.Series([dep_d.loc[:t].iloc[-1] - dep_d.loc[:t - pd.Timedelta(days=182)].iloc[-1] if len(dep_d.loc[:t - pd.Timedelta(days=182)]) else np.nan for t in sess], index=sess)
us_lag = us["vix"].copy(); us_lag.index = us_lag.index + pd.Timedelta(days=1)   # US date <= t-1
V["V6_vix"] = us_lag.reindex(us_lag.index.union(sess)).ffill().reindex(sess)
V["V7_disp21"] = xs["disp21"].reindex(sess)
for bk, b in [("BAL", "v23audit_BAL"), ("LAG", "v23audit_LAG")]:
    pass
books_tx = {k: first[first.book.astype(str).str.upper().str.contains(k)] for k in ["BAL", "LAG"]}
for k, t in books_tx.items():
    cnt = t.groupby("ymd").size().reindex(sess).fillna(0)
    V[f"V8_entries63_{k}"] = cnt.rolling(63, min_periods=63).sum()

# ---- monthly panel: signal at last session of m-1, outcome month m
mon = sess.to_period("M"); last = pd.Series(sess, index=sess).groupby(mon).last()
M = pd.DataFrame({"t_end": last.values}, index=last.index)
for k, c in [("BAL", "nav_bal_ref"), ("LAG", "nav_lag_ref")]:
    M[f"Y1_{k}"] = d[c].reindex(M.t_end).values; M[f"Y1_{k}"] = M[f"Y1_{k}"].pct_change()
M["VNI"] = d.vni_close.reindex(M.t_end).values; M["VNI"] = M["VNI"].pct_change()
for k in ["BAL", "LAG"]: M[f"Y2_{k}"] = M[f"Y1_{k}"] - M["VNI"]
Vm = V.reindex(M.t_end).set_index(M.index).shift(1)                    # signal known at end of m-1
P = pd.concat([M, Vm], axis=1).iloc[1:]
P = P[P.index <= pd.Period("2026-05", "M")]                            # last full month in ledger (ends 06-19)
P.to_csv(f"{OUT}/engine/part_c_regenxsec_panel.csv")

def circ_p(x, y, min_shift=12):
    ok = ~(np.isnan(x) | np.isnan(y)); x, y = x[ok], y[ok]; n = len(x)
    ic = spearmanr(x, y)[0]
    null = [spearmanr(x, np.roll(y, s))[0] for s in range(min_shift, n - min_shift + 1)]
    return ic, float(np.mean(np.abs(null) >= abs(ic))), n

rows = []
vars_ = ["V1_dt5g_state", "V2_vni_ma200dev", "V3_vni_dd252", "V4_value_radar", "V5_dep_chg6m", "V6_vix", "V7_disp21", "V8"]
IS = P.index <= pd.Period("2019-12", "M")
for k in ["BAL", "LAG"]:
    for y in ["Y1", "Y2"]:
        for v in vars_:
            vc = f"V8_entries63_{k}" if v == "V8" else v
            x = P[vc].values.astype(float); yy = P[f"{y}_{k}"].values.astype(float)
            ic, p, n = circ_p(x, yy)
            ic_is = spearmanr(x[IS], yy[IS], nan_policy="omit")[0]; ic_oos = spearmanr(x[~IS], yy[~IS], nan_policy="omit")[0]
            # tercile description, IS cutoffs
            q = np.nanquantile(x[IS], [1 / 3, 2 / 3]) if v != "V1_dt5g_state" else None
            terc = {}
            if q is not None and q[0] < q[1]:
                lab = np.where(x <= q[0], "T1", np.where(x <= q[1], "T2", "T3")); lab = np.where(np.isnan(x), "na", lab)
            else:
                lab = np.where(np.isnan(x), "na", np.char.add("S", np.nan_to_num(x).astype(int).astype(str)))
            for L in sorted(set(lab) - {"na"}):
                m_ = lab == L
                terc[L] = dict(n=int(m_.sum()), mean=float(np.nanmean(yy[m_])), n_oos=int((m_ & ~IS).sum()),
                               mean_oos=float(np.nanmean(yy[m_ & ~IS])) if (m_ & ~IS).sum() else None)
            rows.append(dict(book=k, y=y, var=v, n=n, ic=ic, p_circ=p, ic_is=ic_is, ic_oos=ic_oos, terciles=terc))
R = pd.DataFrame(rows)
# BH-FDR over 32
p = R.p_circ.values; order = np.argsort(p); m = len(p); q = np.empty(m)
q[order] = np.minimum.accumulate((p[order] * m / np.arange(1, m + 1))[::-1])[::-1]; R["q_bh"] = np.minimum(q, 1)
R["same_sign"] = np.sign(R.ic_is) == np.sign(R.ic_oos)
R["PASS"] = (R.q_bh < 0.10) & R.same_sign & (R.ic_oos.abs() >= 0.10)
R.to_json(f"{OUT}/engine/part_c_regenxsec_results.json", orient="records", indent=1)
pd.set_option("display.width", 200)
print("months", len(P), "IS", int(IS.sum()), "OOS", int((~IS).sum()))
print(R[["book", "y", "var", "n", "ic", "p_circ", "q_bh", "ic_is", "ic_oos", "same_sign", "PASS"]].round(3).to_string(index=False))
# episode counts (independence): number of tercile switches per var
for v in vars_[:-1]:
    x = P[v]; q = np.nanquantile(x[IS], [1 / 3, 2 / 3]) if v != "V1_dt5g_state" else None
    lab = x if q is None else pd.cut(x, [-np.inf, q[0], q[1], np.inf], labels=False, duplicates="drop")
    print(v, "regime_runs", int((lab != lab.shift()).sum()))
