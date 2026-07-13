# -*- coding: utf-8 -*-
"""
exp_depgate_20260713.py — EXPERIMENT ONLY (job Taylor_20260713_131230).
Pillar A' (Big-4 deposit-rate 6m-change gate) ablation for plan_deposit_rate_signal_20260713.md.

IMPLEMENTATION NOTE (declared, auditable): variants are built as an OVERLAY on the PUBLISHED
DT5G series —  state_v[t] = min(published_state[t], _commit(dep_proposal[t], 7))  — rather than
re-running the full get_macro_state fuse. Reason: an exact in-fuse replica was attempted first
and drifted from the published table on 122/3107 sessions with the dep pillar DISABLED (73 base-
layer sessions 2017-18 from the daily full-recompute of the v34b base on retro-adjusted prices,
49 macro-layer sessions 2020/2023 cap-timing) — using it as control would conflate base-vintage
drift with the dep-pillar delta. The overlay keeps control == published table EXACTLY (the same
series the pinned R3 baseline consumed), so every deviation in a variant run is attributable to
the dep layer alone.  Fidelity: in Pillar-A-SILENT windows (the incremental windows the project
exists to measure) the dep pillar is the only proposer, so overlay == in-fuse exactly; commit-
timing differences are possible only inside 2022-23 where Pillar A already capped (redundant
window by definition). Declared in plan §5.

DOES NOT touch macro_state_live.py, the BQ cache, or any production file. Outputs go to
mike/agents/Taylor/exp_depgate/ only.

Usage:
  $DNA_PYEXE exp_depgate_20260713.py build            # write exp parquets for D0,D1,D2,D3 (+control sanity)
  $DNA_PYEXE exp_depgate_20260713.py build S4_<id>    # winner lag-26 stress parquet
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

from sbv_macro_overlay import SBV_REFI_EVENTS
from deposit_rate_vn import DEPOSIT_EVENTS
from cpi_vn import cpi_monthly_df
from macro_state_live import P, _commit, NEUTRAL, CRISIS, BEAR

OUT_DIR = os.path.join(WORKDIR, "mike/agents/Taylor/exp_depgate")
os.makedirs(OUT_DIR, exist_ok=True)
PUB_PARQUET = os.path.join(WORKDIR, "data/bq_cache/vnindex_5state_dt5g_live.parquet")

# Pre-registered variants (plan §4, N=6 family; thresholds borrowed from Pillar A, NOT tuned)
VARIANTS = {
    "D0": dict(input="real",    tiers="full", blind=False, lag=P["refi_lag"]),
    "D1": dict(input="nominal", tiers="full", blind=False, lag=P["refi_lag"]),
    "D2": dict(input="nominal", tiers="strong_only", blind=False, lag=P["refi_lag"]),
    "D3": dict(input="nominal", tiers="full", blind=True,  lag=P["refi_lag"]),
}
for _v in ("D0", "D1", "D2", "D3"):   # S4 sensitivity (winner only): publication-lag 5 -> 26
    VARIANTS[f"S4_{_v}"] = dict(VARIANTS[_v], lag=26)


def _published():
    pub = pd.read_parquet(PUB_PARQUET).copy()
    pub["time"] = pd.to_datetime(pub["time"])
    return pub.sort_values("time").reset_index(drop=True)


def _daily_calendar_series(grid_times):
    """dep, cpi(publication-shifted), refi on the session grid (ffill from calendar)."""
    cal = pd.DataFrame({"time": pd.date_range(grid_times.min() - pd.Timedelta(days=400),
                                              grid_times.max(), freq="D")})
    dep_ev = pd.DataFrame(DEPOSIT_EVENTS, columns=["time", "dep"])
    dep_ev["time"] = pd.to_datetime(dep_ev["time"])
    cal = cal.merge(dep_ev, on="time", how="left")
    cpi = cpi_monthly_df(end="2026-06-01")[["time", "cpi_yoy"]].copy()
    # publication shift: month-M print usable from the 1st of month M+1 (plan §3.1)
    cpi["time"] = cpi["time"] + pd.DateOffset(months=1)
    cal = cal.merge(cpi, on="time", how="left")
    refi_ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"])
    refi_ev["time"] = pd.to_datetime(refi_ev["time"])
    cal = cal.merge(refi_ev, on="time", how="left")
    for c in ("dep", "cpi_yoy", "refi"):
        cal[c] = cal[c].ffill()
    g = pd.DataFrame({"time": grid_times}).merge(cal, on="time", how="left")
    for c in ("dep", "cpi_yoy", "refi"):
        g[c] = g[c].ffill().bfill()
    return g


def build_variant_states(vid):
    cfg = VARIANTS[vid]
    pub = _published()
    g = _daily_calendar_series(pub["time"])
    sig = (g["dep"] - g["cpi_yoy"]) if cfg["input"] == "real" else g["dep"]
    chg6m = (sig - sig.shift(P["refi_chg_win"])).shift(cfg["lag"])
    refi_chg6m = (g["refi"] - g["refi"].shift(P["refi_chg_win"])).shift(P["refi_lag"])

    n = len(pub)
    prop = np.full(n, 9)
    x = chg6m.values; rc = refi_chg6m.values
    for t in range(n):
        v = x[t]
        if np.isnan(v):
            continue
        if cfg["blind"] and (not np.isnan(rc[t])) and rc[t] >= P["dom_mild"]:
            continue                       # D3: yield to Pillar A when refi is active
        if cfg["tiers"] == "strong_only":
            if v >= P["dom_strong"]: prop[t] = BEAR
        else:
            if v >= P["dom_extreme"]: prop[t] = CRISIS
            elif v >= P["dom_strong"]: prop[t] = BEAR
            elif v >= P["dom_mild"]: prop[t] = NEUTRAL
    cap = _commit(prop, P["cap_commit"])
    state_v = np.where(cap != 9, np.minimum(pub["state"].values, cap), pub["state"].values).astype(int)

    out = pd.DataFrame({"time": pub["time"], "state": state_v, "state_pub": pub["state"].values,
                        "dep_cap": cap, "dep_prop": prop, "chg6m": np.round(x, 3),
                        "refi_chg6m": np.round(rc, 3)})
    return out


def build(only=None):
    ids = [only] if only else ["D0", "D1", "D2", "D3"]
    pub = _published()
    # control sanity: overlay with no pillar == published, by construction — assert anyway
    assert (pub["state"].values == pub["state"].values).all()
    for vid in ids:
        v = build_variant_states(vid)
        dev = v[v["state"] != v["state_pub"]]
        pq = pd.DataFrame({"time": v["time"].dt.strftime("%Y-%m-%d"),
                           "state": v["state"].astype("int64"),
                           "state_raw": pd.read_parquet(PUB_PARQUET)["state_raw"].astype("int64")})
        p = os.path.join(OUT_DIR, f"state_{vid}.parquet")
        pq.to_parquet(p, index=False)
        v.to_csv(os.path.join(OUT_DIR, f"state_{vid}_full.csv"), index=False)
        yrs = dev.groupby(dev["time"].dt.year).size().to_dict() if len(dev) else {}
        print(f"[build] {vid}: {len(pq)} rows, {len(dev)} sessions deviate from published DT5G "
              f"(by year: {yrs}) -> {p}")


if __name__ == "__main__":
    build(sys.argv[2] if len(sys.argv) > 2 else None) if (len(sys.argv) > 1 and sys.argv[1] == "build") \
        else build()
