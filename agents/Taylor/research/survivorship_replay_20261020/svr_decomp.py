"""Phân rã chênh ALLOC vs chính (KHÔNG prereg) — LAG UB, tập M, X-liq, Z, 1 chân."""
import sys, json, pandas as pd, numpy as np
import svr_replay as R
leg, path = sys.argv[1], sys.argv[2]
met, d, tx = R.load_ledger(path); base = R.calc_metrics(d.combined_nav)
vni = pd.read_csv("data/bq_vni.csv", parse_dates=["time"]).set_index("time"); cal = vni.index
vmax = vni.D_RSI.rolling(60, min_periods=1).max(); fin = R.load_fin()
orig = pd.read_csv(f"{R.KBP}/delisted-big-vanished-prices-20261020.csv").set_index("ticker").exch_orig.to_dict()
w = json.load(open(R.V2))["legs"][leg]["w_median"]; pf = R.book_fraction(d, tx)
tks = {tk: R.Tk(tk, cal, vni.Inflation_7, vmax, d.index, orig[tk]) for tk in R.M}
def dc(F): return (R.calc_metrics(d.combined_nav * F)["cagr"] - base["cagr"]) * 100
res = {}
for sb in [True, False]:
    sig = {tk: R.lag_events(T, d, fin.get(tk), cal, "UB", skip_bear=sb) for tk, T in tks.items()}
    trP = sum((R.simulate(tks[tk], s, d, "LAG", w["LAG"], "liq", "Z") for tk, s in sig.items()), [])
    trA = sum((R.simulate(tks[tk], s, d, "LAG", pf["LAG"], "liq", "Z", tgt_ser=d.nav_lag_ref) for tk, s in sig.items()), [])
    k = "skipBEAR" if sb else "allBEAR"
    res[f"{k}|size=combined|ovl=primary"] = dc(R.overlay(d, trP))
    res[f"{k}|size=combined|ovl=alloc"] = dc(R.overlay_alloc_combined(d, trP)) if hasattr(R, "overlay_alloc_combined") else None
    res[f"{k}|size=book|ovl=alloc"] = dc(R.overlay_alloc(d, trA))
    res[f"{k}|n_trades"] = (len(trP), len(trA)); res[f"{k}|stuck"] = (sum(t["stuck"] for t in trP), sum(t["stuck"] for t in trA))
    if not sb:
        nost = [t for t in trA if not t["stuck"]]; res["allBEAR|size=book|ovl=alloc|no_stuck"] = dc(R.overlay_alloc(d, nost))
# weight comparison: effective combined weight at entry
s = d.cap_lag / d.combined_nav
we = [t["filled_vnd"] / d.nav_lag_ref[t["entry"]] * s[t["entry"]] for t in trA]
res["w_eff_alloc_median"] = float(np.median(we)); res["w_primary"] = w["LAG"]
res["ratio_navlagref_combined_median"] = float((d.nav_lag_ref / d.combined_nav).median())
print(json.dumps(res, indent=1, default=str))
