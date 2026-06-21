#!/usr/bin/env python3
"""backtest_pb_floor_exit.py — exit-rule study for the GOLDEN-cell entry.

Entry = quality (ROE_Min5Y>=12% & ROIC5Y>=10% & FSCORE>=6) + sudden drop (Close/HI_3M_T1<=0.80)
        + PB<1.0 + PB_z=(PB-PB_MA5Y)/PB_SD5Y < -1   (cheap absolute AND cheap vs own 5y history)
Episodes deduped: first signal day; same ticker re-arms only after a 60-trading-day gap.

For each entry we walk the forward daily (adjusted) Close path and apply exit rules:
  FIXED_{3,6,9,12,18,24}M   -- hold N trading months then sell
  Z_TO_0                    -- sell when PB_z climbs back to its 5y mean (z>=0)
  Z_TO_1                    -- sell when PB_z overshoots above mean (z>=+1)
  TP_30 / TP_50             -- take-profit at +30% / +50%
  Z0_CAP12 / Z0_CAP24       -- Z_TO_0 but force-exit by 12M / 24M if not hit
Realized return = Close_exit/Close_entry - 1 ; annualized = (1+r)^(252/hold)-1.
Each rule reports only entries with enough forward data for that rule's cap (clean, no censoring bias).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                           f'--project_id={PROJECT} --format=csv --max_rows=10000000',
                           capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if not r.stdout.strip():
        raise RuntimeError("bq no rows. stderr:\n"+r.stderr[-1500:])
    return pd.read_csv(StringIO(r.stdout.strip()))

ENTRY_SQL = """
SELECT t.ticker, t.time
FROM tav2_bq.ticker AS t
WHERE t.time>="2014-01-01"
  AND t.ROE_Min5Y>=0.12 AND t.ROIC5Y>=0.10 AND t.FSCORE>=6
  AND t.PB>0 AND t.PB<1.0 AND t.HI_3M_T1 IS NOT NULL
  AND SAFE_DIVIDE(t.Close,t.HI_3M_T1)<=0.80
  AND SAFE_DIVIDE(t.PB-t.PB_MA5Y,NULLIF(t.PB_SD5Y,0))<-1.0
ORDER BY t.ticker, t.time
"""

def path_sql(tks):
    inlist = "','".join(tks)
    return f"""
SELECT t.ticker, t.time, t.Close,
  SAFE_DIVIDE(t.PB-t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)) AS pbz
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ('{inlist}') AND t.time>="2014-01-01"
ORDER BY t.ticker, t.time
"""

GAP = 60  # trading-day gap to re-arm same ticker

def dedupe_episodes(ent):
    ent = ent.sort_values(["ticker","time"]).copy()
    keep = []
    for tk, g in ent.groupby("ticker"):
        last = None
        for _, row in g.iterrows():
            if last is None or (row["idx"] - last) > GAP:
                keep.append(row);
            last = row["idx"]
    return pd.DataFrame(keep)

def main():
    ent = bq(ENTRY_SQL)
    ent["time"] = pd.to_datetime(ent["time"])
    tks = sorted(ent["ticker"].unique())
    print(f"{len(ent)} raw signals / {len(tks)} tickers")

    path = bq(path_sql(tks))
    path["time"] = pd.to_datetime(path["time"])
    path = path.sort_values(["ticker","time"]).reset_index(drop=True)
    # per-ticker integer index for trading-day offsets
    path["idx"] = path.groupby("ticker").cumcount()
    pos = {(r.ticker, r.time): r.idx for r in path.itertuples()}
    # attach idx to entries
    ent["idx"] = ent.apply(lambda r: pos.get((r["ticker"], r["time"]), np.nan), axis=1)
    ent = ent.dropna(subset=["idx"]); ent["idx"] = ent["idx"].astype(int)
    epi = dedupe_episodes(ent).reset_index(drop=True)
    print(f"{len(epi)} deduped episodes (gap>{GAP} td)")

    series = {tk: g.reset_index(drop=True) for tk, g in path.groupby("ticker")}

    M = 21  # trading days per month approx
    fixed = {"3M":3*M,"6M":6*M,"9M":9*M,"12M":12*M,"18M":18*M,"24M":24*M}
    results = {}

    def realize(tk, i0, i_exit):
        s = series[tk]
        c0 = s.loc[i0,"Close"]; ce = s.loc[i_exit,"Close"]
        if c0 is None or c0<=0 or pd.isna(c0) or pd.isna(ce): return None
        ret = ce/c0 - 1.0; hold = i_exit - i0
        ann = (1+ret)**(252.0/max(hold,1)) - 1 if ret>-1 else -1
        return ret, hold, ann

    def run_rule(name, exit_fn, need):
        rows=[]
        for _, e in epi.iterrows():
            tk=e["ticker"]; i0=int(e["idx"]); s=series[tk]; n=len(s)
            if i0+need >= n:   # not enough forward data for this rule's cap -> skip (no censoring)
                continue
            i_exit = exit_fn(s, i0)
            if i_exit is None: continue
            r = realize(tk, i0, i_exit)
            if r: rows.append(r)
        if not rows: results[name]=None; return
        df=pd.DataFrame(rows, columns=["ret","hold","ann"])
        results[name]=dict(n=len(df),
            med=round(df["ret"].median()*100,1), mean=round(df["ret"].mean()*100,1),
            win=round((df["ret"]>0).mean()*100,1), hold=int(df["hold"].median()),
            ann=round(df["ann"].median()*100,1))

    # fixed-hold rules
    for nm,k in fixed.items():
        run_rule("FIXED_"+nm, (lambda kk: (lambda s,i0: i0+kk))(k), k)
    # z back to mean (z>=0), cap at 24M
    def z_cross(thr, cap):
        def f(s,i0):
            seg=s.loc[i0+1:i0+cap]
            hit=seg.index[seg["pbz"]>=thr]
            return int(hit[0]) if len(hit) else i0+cap
        return f
    run_rule("Z_TO_0",  z_cross(0.0, 24*M), 24*M)
    run_rule("Z_TO_1",  z_cross(1.0, 24*M), 24*M)
    run_rule("Z0_CAP12",z_cross(0.0, 12*M), 12*M)
    run_rule("Z0_CAP24",z_cross(0.0, 24*M), 24*M)
    # take-profit
    def tp(mult, cap):
        def f(s,i0):
            c0=s.loc[i0,"Close"]; seg=s.loc[i0+1:i0+cap]
            hit=seg.index[seg["Close"]>=c0*mult]
            return int(hit[0]) if len(hit) else i0+cap
        return f
    run_rule("TP_30_cap24", tp(1.30,24*M), 24*M)
    run_rule("TP_50_cap24", tp(1.50,24*M), 24*M)

    print(f"\n{'rule':<14}{'n':>4}{'med%':>7}{'mean%':>7}{'win%':>6}{'holdTD':>8}{'ann%':>7}")
    print("-"*54)
    order=["FIXED_3M","FIXED_6M","FIXED_9M","FIXED_12M","FIXED_18M","FIXED_24M",
           "Z_TO_0","Z0_CAP12","Z0_CAP24","Z_TO_1","TP_30_cap24","TP_50_cap24"]
    for k in order:
        v=results.get(k)
        if v: print(f"{k:<14}{v['n']:>4}{v['med']:>7}{v['mean']:>7}{v['win']:>6}{v['hold']:>8}{v['ann']:>7}")
    pd.DataFrame(results).T.to_csv(os.path.join(WORKDIR,"data","pb_floor_exit_rules.csv"))
    print("\nsaved data/pb_floor_exit_rules.csv")

if __name__=="__main__":
    main()
