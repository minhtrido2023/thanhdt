# -*- coding: utf-8 -*-
"""
wyckoff_warning_logger.py  —  OBSERVE-ONLY Wyckoff distribution/euphoria warning layer
======================================================================================
Job Taylor_20260701_171827 (Huong 2, warning-layer, observe-only). Builds & AUDITS two
theory-grounded warning signals against known DT5G de-risk onsets 2014+. **Nothing here
is wired into any gate, live or paper.** This is an evidence/dashboard build only.

Two signals (all features causal — lagged 1 session before they can warn about day d):

  A. BREADTH DIVERGENCE (Wyckoff distribution near the high):
     index within X% of its 6M high, WHILE market breadth (% of prune universe > MA200)
     is materially LOWER than 3M ago. Price holds up on fewer and fewer names.

  B. EFFORT-vs-RESULT / VOLUME (Wyckoff up-thrust & buying-climax):
     B-dry  : index advancing over 3M but market-wide volume DRYING (median Volume/Volume_1M
              below 1 on the advance) -> no demand confirmation (distribution).
     B-climax: market-wide volume BLOW-OFF (median Volume/Volume_1M >> 1) on a short-term
              advance -> euphoric climax (relevant to EX-BULL peaks).

Thresholds are THEORY-anchored with a COARSE grid for sensitivity — NOT fitted to the
onsets. We report hit-rate / median lead / precision per threshold and let the evidence
speak. If it does not lead the majority of major episodes at acceptable precision, we say
so plainly and stop at the dashboard level (no auto-trade proposal).

Data: local BQ parquet cache (data/bq_cache), read directly via DuckDB (composition-robust
ratios only, so a growing universe does not bias the series). Ground truth: DT5G onsets
from tav2_bq.vnindex_5state_dt5g_live.
"""
import os, sys, json
import numpy as np, pandas as pd
import duckdb

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "data/bq_cache")
os.chdir(WORKDIR)

CRISIS, BEAR, NEUTRAL, BULL, EXBULL = 1, 2, 3, 4, 5
W = 63          # 3-month momentum window (distribution develops over weeks-months)
HIGH_LB = 126   # 6-month lookback for "near the high"
SHORT = 10      # short-term advance window for the climax mode
LEAD_MAX = 60   # a warning "leads" an onset if it fires within 60 sessions before it
MERGE_GAP = 10  # merge warning days < MERGE_GAP sessions apart into one warning-episode


# ── 1. Daily market panel from parquet cache (composition-robust) ────────────
def build_panel():
    con = duckdb.connect(); con.execute("SET threads=2")
    q = f"""
    WITH d AS (
      SELECT time,
             AVG(CASE WHEN MA200 IS NOT NULL AND Close>MA200 THEN 1.0
                      WHEN MA200 IS NOT NULL THEN 0.0 END)              AS breadth,
             COUNT(CASE WHEN MA200 IS NOT NULL THEN 1 END)              AS n_univ,
             MEDIAN(CASE WHEN Volume_1M>0 THEN Volume/Volume_1M END)    AS vol_ratio,
             MAX(VNINDEX)                                               AS vni
      FROM read_parquet('{CACHE}/ticker_prune/*.parquet')
      GROUP BY time
    )
    SELECT * FROM d ORDER BY time
    """
    df = con.execute(q).fetchdf()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df["vni"] = df["vni"].ffill()   # a few early days have NaN mirror
    # derived (raw, un-lagged)
    df["breadth_chg_W"] = df["breadth"] - df["breadth"].shift(W)
    df["vni_max_hi"]    = df["vni"].rolling(HIGH_LB, min_periods=HIGH_LB//2).max()
    df["near_high"]     = df["vni"] >= 0.95 * df["vni_max_hi"]          # within 5% of 6M high
    df["price_mom_W"]   = df["vni"] / df["vni"].shift(W) - 1
    df["price_mom_S"]   = df["vni"] / df["vni"].shift(SHORT) - 1
    return df


# ── 2. Signals (CAUSAL: every input lagged 1 session) ────────────────────────
def add_signals(df, a_delta, b_up, b_dry, climax_hi):
    L = df.shift(1)   # all features as-of yesterday -> warn about today, no look-ahead
    ok = L["n_univ"] >= 100                       # fail-safe: nascent/thin universe -> no warn
    # A: distribution divergence — near 6M high but breadth 3M-lower by >= a_delta pp
    df["sigA"] = ok & L["near_high"] & (L["breadth_chg_W"] <= -a_delta)
    # B-dry: advancing but volume below 1M avg (no demand confirmation)
    df["sigB_dry"] = ok & (L["price_mom_W"] >= b_up) & (L["vol_ratio"] <= b_dry)
    # B-climax: short-term advance on blow-off volume
    df["sigB_clx"] = ok & (L["price_mom_S"] > 0) & (L["vol_ratio"] >= climax_hi)
    df["sigB"] = df["sigB_dry"] | df["sigB_clx"]
    df["sig_any"] = df["sigA"] | df["sigB"]
    return df


# ── 3. Ground truth: DT5G onsets & de-risk episodes ──────────────────────────
def load_onsets():
    con = duckdb.connect(); con.execute("SET threads=2")
    s = con.execute(f"SELECT time,state FROM read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet') "
                    f"ORDER BY time").fetchdf()
    s["time"] = pd.to_datetime(s["time"])
    st = s["state"].values; tm = s["time"].values
    onsets = []       # every transition
    for i in range(1, len(st)):
        if st[i] != st[i-1]:
            onsets.append(dict(date=pd.Timestamp(tm[i]), prev=int(st[i-1]), new=int(st[i])))
    # de-risk ONSETS a warning is expected to lead: enter BEAR/CRISIS from a risk-on state (>=NEUTRAL)
    derisk = [o for o in onsets if o["new"] in (BEAR, CRISIS) and o["prev"] >= NEUTRAL]
    exbull = [o for o in onsets if o["new"] == EXBULL]
    # episodes: collapse a run of risk-off into one; episode start = first leave of risk-on
    epis = []
    in_off = False
    for i in range(1, len(st)):
        risk_off = st[i] <= BEAR
        if risk_off and not in_off:
            epis.append(pd.Timestamp(tm[i])); in_off = True
        elif not risk_off and in_off:
            in_off = False
    return s, derisk, exbull, epis


# ── 4. Validation: hit-rate, lead, precision ─────────────────────────────────
def sessions_index(df):
    return {d: i for i, d in enumerate(df["time"])}

def warning_episodes(df, col):
    """Collapse warning DAYS into episodes (fires < MERGE_GAP sessions apart = one)."""
    idx = df.index[df[col]].tolist()
    if not idx:
        return []
    eps = [[idx[0], idx[0]]]
    for j in idx[1:]:
        if j - eps[-1][1] <= MERGE_GAP:
            eps[-1][1] = j
        else:
            eps.append([j, j])
    return eps   # list of [start_pos, end_pos]

def evaluate(df, targets, col, label):
    """For each target onset, did `col` fire within [onset-LEAD_MAX, onset-1]?"""
    pos = sessions_index(df)
    # onset position (map to nearest session index)
    hits, leads = 0, []
    for o in targets:
        d = o["date"] if isinstance(o, dict) else o
        if d not in pos:
            # snap to prior session
            prior = df[df["time"] <= d]
            if prior.empty:
                continue
            oi = prior.index[-1]
        else:
            oi = pos[d]
        win = df.iloc[max(0, oi-LEAD_MAX):oi]
        fired = win.index[win[col]].tolist()
        if fired:
            hits += 1
            leads.append(oi - fired[-1])   # lead of the LAST warning before the onset
    n = len(targets)
    hit_rate = hits / n if n else float("nan")
    med_lead = float(np.median(leads)) if leads else float("nan")
    # precision: warning-episodes that lead SOME de-risk onset within LEAD_MAX
    eps = warning_episodes(df, col)
    onset_pos = []
    for o in targets:
        d = o["date"] if isinstance(o, dict) else o
        prior = df[df["time"] <= d]
        if not prior.empty:
            onset_pos.append(prior.index[-1])
    good = 0
    for st_pos, en_pos in eps:
        # episode "good" if any onset falls in (episode_start, episode_start+LEAD_MAX]
        if any(st_pos < op <= st_pos + LEAD_MAX for op in onset_pos):
            good += 1
    precision = good / len(eps) if eps else float("nan")
    return dict(label=label, col=col, n_targets=n, hits=hits, hit_rate=hit_rate,
                med_lead=med_lead, n_warn_ep=len(eps), precision=precision)


def main():
    df = build_panel()
    aud = df[df["time"] >= "2014-01-01"].copy()   # audit window; 2013 kept only for warmup
    print(f"[panel] {df.time.min().date()}..{df.time.max().date()}  audit rows={len(aud)}  "
          f"breadth[last]={aud.breadth.iloc[-1]:.3f}  vol_ratio[last]={aud.vol_ratio.iloc[-1]:.2f}")

    s, derisk, exbull, epis = load_onsets()
    print(f"[truth] de-risk onsets(from>=NEUTRAL into BEAR/CRISIS)={len(derisk)}  "
          f"EX-BULL peaks={len(exbull)}  distinct risk-off episodes={len(epis)}")
    for o in derisk:
        print(f"   derisk {o['date'].date()}  {o['prev']}->{o['new']}")
    for o in exbull:
        print(f"   exbull {o['date'].date()}  {o['prev']}->{o['new']}")

    # THEORY-anchored coarse grid (NOT fitted): midpoint = first of each list
    grid = []
    for a_delta in (0.10, 0.08, 0.12):
        for b_up in (0.05, 0.08):
            for b_dry in (1.00, 0.90):
                for climax_hi in (1.6, 2.0):
                    grid.append((a_delta, b_up, b_dry, climax_hi))

    rows = []
    for (a_delta, b_up, b_dry, climax_hi) in grid:
        d2 = add_signals(df.copy(), a_delta, b_up, b_dry, climax_hi)
        d2 = d2[d2["time"] >= "2014-01-01"].reset_index(drop=True)
        tag = f"A>={a_delta:.2f}|Bup>={b_up:.0%}|Bdry<={b_dry:.2f}|clx>={climax_hi:.1f}"
        rA  = evaluate(d2, derisk, "sigA",   "A_breadth_div")
        rB  = evaluate(d2, derisk, "sigB",   "B_vol")
        rBx = evaluate(d2, exbull, "sigB_clx", "Bclx_exbull")
        rAll= evaluate(d2, derisk, "sig_any", "ANY_derisk")
        for r in (rA, rB, rBx, rAll):
            r["grid"] = tag; r["warn_days"] = int(d2[r["col"]].sum())
            rows.append(r)

    res = pd.DataFrame(rows)
    # focus print: the THEORY midpoint grid line
    mid = f"A>=0.10|Bup>=5%|Bdry<=1.00|clx>=1.6"
    print("\n==== THEORY-MIDPOINT grid:", mid, "====")
    cols = ["label","n_targets","hits","hit_rate","med_lead","warn_days","n_warn_ep","precision"]
    print(res[res.grid == mid][cols].to_string(index=False))

    print("\n==== SENSITIVITY (ANY_derisk & Bclx_exbull across grid) ====")
    for lab in ("ANY_derisk", "Bclx_exbull"):
        sub = res[res.label == lab][["grid","hit_rate","med_lead","warn_days","precision"]]
        print(f"-- {lab} --")
        print(sub.to_string(index=False))

    # persist artifacts
    outp = os.path.join(WORKDIR, "data/wyckoff_warning_panel.csv")
    d_mid = add_signals(df.copy(), 0.10, 0.05, 1.00, 1.6)
    d_mid[d_mid["time"] >= "2014-01-01"][
        ["time","vni","breadth","breadth_chg_W","vol_ratio","near_high",
         "sigA","sigB_dry","sigB_clx","sigB","sig_any"]
    ].to_csv(outp, index=False)
    res.to_csv(os.path.join(WORKDIR, "data/wyckoff_warning_grid.csv"), index=False)
    print(f"\n[saved] {outp}")
    print(f"[saved] data/wyckoff_warning_grid.csv")
    return res


if __name__ == "__main__":
    main()
