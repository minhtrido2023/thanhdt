#!/usr/bin/env python
"""CAPIT basket selection — DCF as a SECONDARY filter/tiebreaker on top of pb_z.

R&D only (job Taylor_20260720_153003). Does NOT touch production pt_v23_audit_2014.py.

Pre-registered (before any result was seen):
  N_trials = 3 selection variants x 1 primary horizon (fwd +6M), K=5 slots.
    (c) BASE  : top-K by pb_z                                   [control]
    (a) HARD  : drop DCF-RICH (MoS<0) from pool, then top-K pb_z ; DCF N/A = PASS (neutral)
    (b) SOFT  : shortlist top-2K by pb_z, stable-sort DCF-cheap|N/A first, take K
  Secondary (reported, not selection-driving): fwd +2M / +12M.
  Decision metric: mean/median equal-weight basket forward return, per-event and pooled,
  IS 2014-2019 vs OOS 2020+.

Point-in-time discipline: DCF uses ticker_financial rows with time<=asof (time == Release_Date,
verified), deposit rate/CPI as-of. Price = Close on the event date. No forward data in selection.
"""
import os, sys, json
import numpy as np
import pandas as pd
import duckdb

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
import dcf_valuation as dv

OUT = os.path.join(WORKDIR, "mike/agents/Taylor/exp_capit_dcf")
K = 5                      # live CAPIT slot count
PRIMARY_H = 126            # ~6M trading sessions
HORIZONS = {"2M": 42, "6M": 126, "12M": 252}

# 16 CAPIT washout fire dates 2014-2026 (from data/capit_selection_features.csv, production config)
EVENTS = ["2014-05-09", "2015-08-25", "2016-01-19", "2018-05-29", "2018-07-06",
          "2020-02-04", "2020-03-12", "2020-07-28", "2022-04-20", "2022-06-16",
          "2023-10-31", "2024-04-19", "2024-08-06", "2025-04-04", "2025-10-21",
          "2026-03-10"]

con = duckdb.connect(":memory:")
con.execute("PRAGMA threads=1")
PRUNE = f"read_parquet('{WORKDIR}/data/bq_cache/ticker_prune/*.parquet')"


def basket_pool(d):
    """Production `golden` CAPIT pool at date d (capit_basket() golden path, pre-slot-cap)."""
    q = f"""
SELECT p.ticker, (p.PB-p.PB_MA5Y)/NULLIF(p.PB_SD5Y,0) AS pbz, COALESCE(p.Price,p.Close) AS px
FROM {PRUNE} p
WHERE p.time = DATE '{d}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2"""
    e = con.execute(q).df().dropna(subset=["pbz"])
    if e.empty:
        return e
    g = e[e.pbz < -1]
    c = e[e.pbz < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    # stable sort (pbz, ticker) — determinism discipline, see 2026-07-13 view-swap lesson
    return pick.sort_values(["pbz", "ticker"], kind="mergesort").head(15).reset_index(drop=True)


def fwd_returns(ticker, d):
    """Forward Close/Close returns from event date, adjusted Close, causal."""
    q = f"""SELECT p.time, p.Close FROM {PRUNE} p
WHERE p.ticker='{ticker}' AND p.time >= DATE '{d}' ORDER BY p.time"""
    s = con.execute(q).df()
    out = {}
    if s.empty:
        return {k: np.nan for k in HORIZONS}
    p0 = float(s.Close.iloc[0])
    for name, n in HORIZONS.items():
        out[name] = float(s.Close.iloc[n]) / p0 - 1 if len(s) > n and p0 > 0 else np.nan
    return out


def build():
    fin = dv._load_financials()
    rows = []
    for d in EVENTS:
        pool = basket_pool(d)
        for i, r in pool.iterrows():
            res = dv.fair_value(r.ticker, d, price=float(r.px), fin=fin)
            mos = res.get("margin_of_safety") if res.get("ok") else np.nan
            rows.append(dict(event=d, ticker=r.ticker, pbz=float(r.pbz), px=float(r.px),
                             pbz_rank=i, dcf_ok=bool(res.get("ok")),
                             dcf_reason=res.get("reason"), mos=mos, **fwd_returns(r.ticker, d)))
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/capit_dcf_panel.csv", index=False)
    return df


def select(df_ev, variant):
    """Return list of tickers picked under `variant` for one event's pool (already pbz-sorted)."""
    p = df_ev.sort_values(["pbz", "ticker"], kind="mergesort")
    if variant == "BASE":
        return list(p.head(K).ticker)
    if variant == "HARD":
        # DCF N/A (mos NaN) = PASS-THROUGH (neutral), only drop explicit RICH
        keep = p[~(p.mos.notna() & (p.mos < 0))]
        if len(keep) < 3:                      # fail-safe: too thin -> fall back to base
            return list(p.head(K).ticker)
        return list(keep.head(K).ticker)
    if variant == "SOFT":
        short = p.head(2 * K).copy()
        # cheap|N/A first, rich last; stable within group => pb_z order preserved
        short["grp"] = np.where(short.mos.notna() & (short.mos < 0), 1, 0)
        return list(short.sort_values("grp", kind="mergesort").head(K).ticker)
    raise ValueError(variant)


def evaluate(df):
    recs = []
    for d, g in df.groupby("event"):
        for v in ("BASE", "HARD", "SOFT"):
            picks = select(g, v)
            sub = g[g.ticker.isin(picks)]
            rec = dict(event=d, variant=v, n=len(picks), names=",".join(sorted(picks)))
            for h in HORIZONS:
                rec[f"ret_{h}"] = float(sub[h].mean()) if len(sub) else np.nan
            recs.append(rec)
    ev = pd.DataFrame(recs)
    ev.to_csv(f"{OUT}/capit_dcf_events.csv", index=False)
    return ev


def report(df, ev):
    L = []
    P = L.append
    P("# CAPIT basket selection — DCF secondary filter/tiebreaker (R&D)")
    P(f"\nEvents: {len(EVENTS)} | pool-rows: {len(df)} | K={K} slots | primary horizon 6M")
    P(f"\n## DCF coverage on CAPIT pools")
    P(f"- computable (ok): {int(df.dcf_ok.sum())}/{len(df)} = {df.dcf_ok.mean():.1%}")
    rc = df[~df.dcf_ok].dcf_reason.value_counts()
    for k, v in rc.items():
        P(f"  - N/A: {k} — {v}")
    ok = df[df.dcf_ok]
    P(f"- of computable: RICH(MoS<0) {int((ok.mos < 0).sum())} | CHEAP {int((ok.mos >= 0).sum())}")

    P("\n## Per-event basket forward return (equal-weight, %)")
    piv = ev.pivot(index="event", columns="variant", values="ret_6M") * 100
    piv["HARD-BASE"] = piv["HARD"] - piv["BASE"]
    piv["SOFT-BASE"] = piv["SOFT"] - piv["BASE"]
    P("```")
    P(piv.round(2).to_string())
    P("```")

    P("\n## Pooled summary (mean of per-event basket returns)")
    for h in HORIZONS:
        c = f"ret_{h}"
        P(f"\n**{h}**")
        P("```")
        t = ev.pivot(index="event", columns="variant", values=c) * 100
        isx = t[t.index < "2020"]
        oos = t[t.index >= "2020"]
        for label, blk in (("FULL", t), ("IS 2014-19", isx), ("OOS 2020+", oos)):
            P(f"{label:12s} n={len(blk):2d} " + " ".join(
                f"{v}={blk[v].mean():7.2f}%" for v in ("BASE", "HARD", "SOFT")) +
              f"  | dHARD={blk['HARD'].mean()-blk['BASE'].mean():+.2f}pp"
              f" dSOFT={blk['SOFT'].mean()-blk['BASE'].mean():+.2f}pp")
        P("```")

    # how often do the variants even differ?
    diff_h = (ev.pivot(index="event", columns="variant", values="names")["HARD"] !=
              ev.pivot(index="event", columns="variant", values="names")["BASE"]).sum()
    diff_s = (ev.pivot(index="event", columns="variant", values="names")["SOFT"] !=
              ev.pivot(index="event", columns="variant", values="names")["BASE"]).sum()
    P(f"\n## Bite\n- HARD differs from BASE on {diff_h}/{len(EVENTS)} events")
    P(f"- SOFT differs from BASE on {diff_s}/{len(EVENTS)} events")

    # paired t / sign test on the events where it bites
    for v in ("HARD", "SOFT"):
        t = ev.pivot(index="event", columns="variant", values="ret_6M")
        d = (t[v] - t["BASE"]).dropna()
        d = d[d != 0]
        if len(d) > 1:
            tstat = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
            P(f"- {v}: n_diff={len(d)} mean_delta={d.mean()*100:+.2f}pp "
              f"t={tstat:.2f} wins={int((d>0).sum())}/{len(d)}")
        else:
            P(f"- {v}: n_diff={len(d)} — no testable sample")

    # name-level: does MoS predict forward return within CAPIT pools?
    P("\n## Name-level: is DCF MoS informative INSIDE a CAPIT pool?")
    o = df[df.dcf_ok & df["6M"].notna()]
    if len(o) > 5:
        ic = o[["mos", "6M"]].corr(method="spearman").iloc[0, 1]
        P(f"- Spearman(MoS, fwd6M) = {ic:+.3f} on n={len(o)} computable names")
        P(f"- mean fwd6M: RICH {o[o.mos<0]['6M'].mean()*100:+.2f}% (n={(o.mos<0).sum()}) | "
          f"CHEAP {o[o.mos>=0]['6M'].mean()*100:+.2f}% (n={(o.mos>=0).sum()})")
    na = df[~df.dcf_ok & df["6M"].notna()]
    P(f"- mean fwd6M of DCF-N/A names: {na['6M'].mean()*100:+.2f}% (n={len(na)}) "
      f"— sanity check that N/A-as-pass is not silently harmful")
    txt = "\n".join(L)
    open(f"{OUT}/capit_dcf_report.md", "w").write(txt)
    print(txt)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    pan = f"{OUT}/capit_dcf_panel.csv"
    df = pd.read_csv(pan) if (len(sys.argv) > 1 and sys.argv[1] == "--reuse" and os.path.exists(pan)) else build()
    report(df, evaluate(df))
