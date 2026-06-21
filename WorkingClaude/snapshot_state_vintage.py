#!/usr/bin/env python3
"""snapshot_state_vintage.py — build/maintain a POINT-IN-TIME (vintage) reference of the
5-state series so future backtests are reproducible and free of state-restatement drift.

WHY: the state machine's min_stay_filter(7) is non-causal (needs to know if a segment lasts
>=7 sessions) so historical states get REVISED on each rebuild. The integrity audit
(memory: v5-prodspec-integrity-audit) found this inflated backtests ~3pp. A vintage = the
state series exactly as it was KNOWN on a given as-of date.

CONVENTION:
  state_vintage/vnindex_5state_VINTAGE_YYYYMMDD.csv   — full series (time,state) as-of that date
  state_vintage/MANIFEST.csv                          — index of snapshots
  A backtest "as of date D" loads the latest VINTAGE_<=D snapshot (use load_vintage(D)).

MODES:
  python snapshot_state_vintage.py --init   # create dir, seed 2 historical points + today
  python snapshot_state_vintage.py          # daily: append today's snapshot (idempotent)

Wire the daily mode into papertrade_daily.bat (one extra line) to accumulate true vintage.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, glob
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import bq
VDIR=os.path.join(WORKDIR,"state_vintage"); os.makedirs(VDIR,exist_ok=True)
STATE_TABLE="vnindex_5state"   # the LIVE state series used by SIGNAL_V11 (state5)

def save_snapshot(df, asof, source):
    """df: columns time,state. Writes VINTAGE_<asof>.csv (idempotent) + manifest row."""
    df=df.dropna(subset=["state"]).copy(); df["time"]=pd.to_datetime(df["time"])
    df=df[["time","state"]].sort_values("time")
    fn=f"vnindex_5state_VINTAGE_{asof.replace('-','')}.csv"; path=os.path.join(VDIR,fn)
    if os.path.exists(path):
        print(f"  [skip] {fn} already exists"); return path
    df.to_csv(path,index=False)
    print(f"  [write] {fn}: {len(df)} rows {df['time'].min().date()}->{df['time'].max().date()} (src={source})")
    return path

def rebuild_manifest():
    rows=[]
    for f in sorted(glob.glob(os.path.join(VDIR,"vnindex_5state_VINTAGE_*.csv"))):
        asof=os.path.basename(f).replace("vnindex_5state_VINTAGE_","").replace(".csv","")
        d=pd.read_csv(f); d["time"]=pd.to_datetime(d["time"])
        rows.append({"asof":f"{asof[:4]}-{asof[4:6]}-{asof[6:]}","file":os.path.basename(f),
                     "rows":len(d),"min":d["time"].min().date(),"max":d["time"].max().date()})
    man=pd.DataFrame(rows).sort_values("asof")
    man.to_csv(os.path.join(VDIR,"MANIFEST.csv"),index=False)
    print("\n  MANIFEST:"); print(man.to_string(index=False))
    return man

def current_state():
    d=bq(f"SELECT s.time, s.state FROM tav2_bq.{STATE_TABLE} AS s ORDER BY s.time")
    return d

def pkl_state(pklname):
    df=pickle.load(open(pklname,"rb")); df["time"]=pd.to_datetime(df["time"])
    return df.dropna(subset=["state5"]).groupby("time",as_index=False)["state5"].first().rename(columns={"state5":"state"})

if __name__=="__main__":
    init = "--init" in sys.argv
    today=datetime.now().strftime("%Y-%m-%d")
    if init:
        print("[INIT] seeding vintage reference...")
        # historical point 1: bak pkl (as-of 2026-05-20 build, 2014+ market state5)
        bak="ba_v11_unified_12y_sig.pkl.bak_stale_20260520"
        if os.path.exists(bak):
            save_snapshot(pkl_state(bak), "2026-05-20", "pkl.bak_stale (May20 build)")
        # historical point 2: current rebuilt pkl (as-of 2026-05-28 build)
        if os.path.exists("ba_v11_unified_12y_sig.pkl"):
            save_snapshot(pkl_state("ba_v11_unified_12y_sig.pkl"), "2026-05-28", "pkl current (May28 rebuild, full)")
        # today's authoritative full-history snapshot from BQ LIVE table
        save_snapshot(current_state(), today, f"BQ {STATE_TABLE} (full 2000+)")
        # README
        with open(os.path.join(VDIR,"README.md"),"w",encoding="utf-8") as f:
            f.write("# State vintage reference\n\nPoint-in-time snapshots of the 5-state series "
                    "(`vnindex_5state`) so backtests are reproducible (state machine restates history via "
                    "non-causal min_stay_filter).\n\n"
                    "**Use**: a backtest 'as of date D' should load the latest `VINTAGE_<=D` file.\n"
                    "```python\nfrom state_vintage_loader import load_vintage\nstate_df = load_vintage('2026-05-28')  # or asof=None for latest\n```\n\n"
                    "Daily accumulation: `python snapshot_state_vintage.py` (wire into papertrade_daily.bat).\n"
                    "Seeded 2026-05-28 with 2 historical points (May20 pkl.bak, May28 rebuild) + full BQ snapshot.\n")
        rebuild_manifest()
        print("\n[INIT] done.")
    else:
        print(f"[DAILY] snapshot {today}...")
        save_snapshot(current_state(), today, f"BQ {STATE_TABLE}")
        rebuild_manifest()
