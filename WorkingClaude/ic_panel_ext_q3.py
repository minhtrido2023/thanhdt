#!/usr/bin/env python3
"""ic_panel_ext_q3.py — IC-PANEL EXTENSION (R&D Q3, Taylor, 2026-07-05).

Extends the 2026-06-21 marginal-IC panel (ic_panel_8l.py) with 4 NEW candidate lenses,
measured on the SAME frozen PIT panel + SAME machinery (marginal IC residualized on the
core value block {ey=1/PE, cfy=1/PCF, ps=1/PS, neg_pbz}, in-gate = as-of rating<=3),
split IS(2014-19)/OOS(2020+), plus crash%(profit_2M<-20) by lens quintile.

Kept as a SEPARATE file (does not touch the frozen ic_panel_8l.py deliverable / no production
strategy file changed). Reuses ic_panel_8l.{load, marginal_ic_series, ic_series, summ, CORE_VALUE}.

NEW lenses (all PIT: financial signals merged_asof on Release_Date<=obs time; daily-micro
windows are strictly backward-looking, end-of-day at obs date):
  H4 accruals (Sloan 1996): (NP_TTM - CFO_TTM)/TotalAssets ; expect IC NEGATIVE.
  H5 dividend yield        : DY (cash div yield per data dict) ; expect IC POSITIVE.
  H6a MAX5_1M              : mean of 5 largest daily (adj) returns over trailing 21 sessions ; expect NEGATIVE.
  H6b limit_freq_1M        : freq of raw-price daily return >= 0.065 (HOSE ceiling proxy) over 21 sessions ; expect NEGATIVE.

Survival: H4/H6 = marginal-IC(gate) <= -0.03 in BOTH halves OR crash% monotone by quintile;
          H5    = marginal-IC(gate) >= +0.03 in BOTH halves.
Usage: source ./wc_env.sh && $DNA_PYEXE ic_panel_ext_q3.py
"""
import warnings; warnings.filterwarnings("ignore")
import os, importlib.util
import numpy as np, pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")

# ---- import the frozen panel machinery (no modification) ----
spec = importlib.util.spec_from_file_location("ic8l", os.path.join(WORKDIR, "ic_panel_8l.py"))
ic8l = importlib.util.module_from_spec(spec); spec.loader.exec_module(ic8l)
bq, load, summ = ic8l.bq, ic8l.load, ic8l.summ
ic_series, marginal_ic_series = ic8l.ic_series, ic8l.marginal_ic_series
TARGET, CRASH, N_MIN = ic8l.TARGET, ic8l.CRASH, ic8l.N_MIN
print(f"CORE_VALUE (residualize-against) = {ic8l.CORE_VALUE}")

# ---------------- pull + attach the 4 new lenses (PIT) ----------------
def attach_new_lenses(d):
    tickers = sorted(d.ticker.dropna().unique().tolist())
    dates   = sorted(pd.to_datetime(d.time.dropna().unique()))
    tk_in   = ",".join("'%s'" % t for t in tickers)
    dt_in   = ",".join("'%s'" % pd.Timestamp(x).date() for x in dates)

    # ---- H4 accruals + H5 DY : quarterly financials, known at Release_Date (merge_asof) ----
    fin = bq(f"""
      SELECT f.ticker AS ticker, f.Release_Date AS rel,
             f.NP_P0 AS NP_P0, f.NP_P1 AS NP_P1, f.NP_P2 AS NP_P2, f.NP_P3 AS NP_P3,
             f.CF_OA_P0 AS CF_OA_P0, f.CF_OA_P1 AS CF_OA_P1, f.CF_OA_P2 AS CF_OA_P2, f.CF_OA_P3 AS CF_OA_P3,
             f.totalAsset_P0 AS totalAsset_P0, f.DY AS DY
      FROM tav2_bq.ticker_financial AS f
      WHERE f.time >= '2012-06-01' AND f.Release_Date IS NOT NULL
      ORDER BY f.ticker, f.Release_Date
    """)
    fin["rel"] = pd.to_datetime(fin["rel"])
    for c in fin.columns:
        if c not in ("ticker", "rel"): fin[c] = pd.to_numeric(fin[c], errors="coerce")
    np_ttm  = fin[["NP_P0","NP_P1","NP_P2","NP_P3"]].sum(axis=1, min_count=4)
    cfoa_ttm = fin[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=4)  # = CFO_TTM/Assets
    npa_ttm = np_ttm / fin["totalAsset_P0"].where(fin["totalAsset_P0"] > 0)                # = NP_TTM/Assets
    fin["accruals"] = npa_ttm - cfoa_ttm       # Sloan: high accruals = low earnings quality (expect -IC)
    fin["dy"]       = fin["DY"]
    finm = fin[["ticker","rel","accruals","dy"]].dropna(subset=["rel"]).sort_values("rel")

    d = pd.merge_asof(d.sort_values("time"), finm, by="ticker",
                      left_on="time", right_on="rel", direction="backward")
    d = d.drop(columns=["rel"])

    # ---- H6a MAX5_1M + H6b limit_freq_1M : trailing-21-session daily micro, PIT (end-of-day at obs) ----
    micro = bq(f"""
      WITH base AS (
        SELECT k.ticker AS ticker, k.time AS time,
               SAFE_DIVIDE(k.Close, k.Close_T1)-1 AS ret_adj,
               SAFE_DIVIDE(k.Price, LAG(k.Price) OVER (PARTITION BY k.ticker ORDER BY k.time))-1 AS ret_raw
        FROM tav2_bq.ticker AS k
        WHERE k.ticker IN ({tk_in}) AND k.time >= '2013-06-01'
      ),
      w AS (
        SELECT ticker, time,
               ARRAY_AGG(ret_adj) OVER win AS arr,
               COUNTIF(ret_raw >= 0.065) OVER win AS lh,
               COUNTIF(ret_raw IS NOT NULL) OVER win AS nd
        FROM base
        WINDOW win AS (PARTITION BY ticker ORDER BY time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW)
      )
      SELECT ticker, time,
             (SELECT AVG(x) FROM UNNEST(ARRAY(SELECT r FROM UNNEST(arr) r WHERE r IS NOT NULL ORDER BY r DESC LIMIT 5)) x) AS max5_1M,
             SAFE_DIVIDE(lh, nd) AS limit_freq_1M, nd
      FROM w
      WHERE time IN ({dt_in}) AND nd >= 15
    """)
    micro["time"] = pd.to_datetime(micro["time"])
    for c in ("max5_1M","limit_freq_1M"): micro[c] = pd.to_numeric(micro[c], errors="coerce")
    d = d.merge(micro[["ticker","time","max5_1M","limit_freq_1M"]], on=["ticker","time"], how="left")
    return d

# ---------------- crash% by lens quintile (pooled, in-gate) ----------------
def crash_by_quintile(d, lens, mask):
    g = d[mask & d[lens].notna() & d[TARGET].notna()].copy()
    if len(g) < 100: return None
    try:
        g["Q"] = pd.qcut(g[lens].rank(method="first"), 5, labels=[1,2,3,4,5])
    except Exception:
        return None
    rows = []
    for q in [1,2,3,4,5]:
        sub = g[g["Q"] == q]
        rows.append(dict(Q=int(q), n=len(sub), lens_mean=sub[lens].mean(),
                         fwd2M=sub[TARGET].mean(), crash=(sub[TARGET] < CRASH).mean()*100))
    return pd.DataFrame(rows)

def monotone(series):
    v = series.values
    return bool(np.all(np.diff(v) >= 0)) or bool(np.all(np.diff(v) <= 0))

# ---------------- main ----------------
def main():
    d = load()
    d = attach_new_lenses(d)
    d["yr"] = d["q"].dt.year
    gate = d["rating"] <= 3
    IS, OOS = d["yr"] <= 2019, d["yr"] >= 2020

    NEW = [
        ("H4_accruals",  "accruals",       "neg", -0.03),
        ("H5_div_yield", "dy",             "pos", +0.03),
        ("H6a_MAX5_1M",  "max5_1M",        "neg", -0.03),
        ("H6b_limit_freq","limit_freq_1M", "neg", -0.03),
    ]

    print(f"\npanel obs {len(d)}  quarters {d.q.nunique()}  gate-obs {int(gate.sum())}")
    for tag, L, exp, thr in NEW:
        print(f"  cov {tag:14} = {d[L].notna().mean():.2f}  (gate cov {d.loc[gate,L].notna().mean():.2f})")

    fmt = lambda v: f"{v:+.3f}" if pd.notna(v) else "  -  "
    print(f"\n=== IC-PANEL EXTENSION — target={TARGET} (T+40), marginal vs {ic8l.CORE_VALUE}, in-gate rating<=3 ===")
    hdr = (f"{'lens':16} {'exp':>3} {'cov':>4} | {'rawIC_gate':>10} | "
           f"{'mIC_g_IS':>9} {'mIC_g_OOS':>10} {'t_IS':>5} {'t_OOS':>6} | {'verdict':>16}")
    print(hdr); print("-"*len(hdr))
    reg_rows, quint_blocks = [], []
    for tag, L, exp, thr in NEW:
        rawg  = summ(ic_series(d, L, TARGET, gate)[0])["ic"]
        mIS   = summ(marginal_ic_series(d, L, TARGET, gate & IS))
        mOOS  = summ(marginal_ic_series(d, L, TARGET, gate & OOS))
        micIS, micOOS = mIS["ic"], mOOS["ic"]
        qb = crash_by_quintile(d, L, gate)
        # survival test
        mono = False; mono_dir = ""
        if qb is not None:
            mono = monotone(qb["crash"])
            mono_dir = "up" if qb["crash"].iloc[-1] >= qb["crash"].iloc[0] else "down"
        if exp == "neg":
            ic_pass  = (pd.notna(micIS) and pd.notna(micOOS) and micIS <= thr and micOOS <= thr)
            mono_ok  = mono and mono_dir == "up"     # crash rises with the (bad) signal
        else:  # pos
            ic_pass  = (pd.notna(micIS) and pd.notna(micOOS) and micIS >= thr and micOOS >= thr)
            mono_ok  = mono and mono_dir == "down"   # crash falls as yield rises
        alive = ic_pass or (exp != "pos" and mono_ok)   # H5(pos) requires the IC gate, not crash-only
        verdict = "ELIGIBLE t2-proxy" if alive else "CLOSED t1"
        print(f"{tag:16} {exp:>3} {d[L].notna().mean():>4.2f} | {fmt(rawg):>10} | "
              f"{fmt(micIS):>9} {fmt(micOOS):>10} {mIS['t']:>5.1f} {mOOS['t']:>6.1f} | {verdict:>16}")
        reg_rows.append(dict(lens=tag, col=L, expect=exp, thr=thr, raw_ic_gate=rawg,
                             mic_gate_IS=micIS, mic_gate_OOS=micOOS,
                             t_IS=mIS["t"], t_OOS=mOOS["t"], nIS=mIS["n"], nOOS=mOOS["n"],
                             crash_monotone=mono, mono_dir=mono_dir, verdict=verdict))
        if qb is not None:
            qb.insert(0, "lens", tag); quint_blocks.append(qb)

    print(f"\n=== crash% (profit_2M<{CRASH:.0f}) by lens quintile, in-gate (Q1..Q5 ascending lens) ===")
    for qb in quint_blocks:
        tag = qb["lens"].iloc[0]
        cells = " ".join(f"Q{int(r.Q)}:{r.crash:4.1f}%(n{int(r.n)})" for _, r in qb.iterrows())
        f2m   = " ".join(f"{r.fwd2M:+5.1f}" for _, r in qb.iterrows())
        print(f"{tag:16} crash: {cells}")
        print(f"{'':16} fwd2M: {f2m}")

    out = pd.DataFrame(reg_rows)
    out.round(4).to_csv(os.path.join(WORKDIR, "data", "ic_panel_ext_q3.csv"), index=False)
    pd.concat(quint_blocks).round(3).to_csv(os.path.join(WORKDIR, "data", "ic_panel_ext_q3_quintile.csv"), index=False)
    print("\nwrote data/ic_panel_ext_q3.csv + data/ic_panel_ext_q3_quintile.csv")
    return out, quint_blocks

if __name__ == "__main__":
    main()
