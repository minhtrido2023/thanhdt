import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11
START="2014-01-01"; END="2026-05-15"
TIER_BAL={'MEGA','MOMENTUM','MOMENTUM_N','MOMENTUM_S','DEEP_VALUE_RECOVERY','RE_BACKLOG_BUY'}
# baseline pkl for schema/column order
base=pickle.load(open("ba_v11_unified_12y_sig.pkl","rb")); base["time"]=pd.to_datetime(base["time"])
print(f"[base] rows={len(base):,} cols={list(base.columns)}")
# EW5 signal: point fa_dated at fa_ratings_ew5
sql=SIGNAL_V11.replace("tav2_bq.fa_ratings AS f","tav2_bq.fa_ratings_ew5 AS f")
assert "fa_ratings_ew5" in sql, "replace failed"
print("[build] running SIGNAL_V11(EW5)...")
new=bq(sql.format(start=START,end=END)); new["time"]=pd.to_datetime(new["time"])
print(f"[ew5] rows={len(new):,} cols={list(new.columns)}")
miss=set(base.columns)-set(new.columns)
print(f"[check] missing cols: {miss if miss else 'none'}")
assert not miss
new=new[list(base.columns)]
new.to_pickle("ba_v11_ew5_sig.pkl")
# compare play_type dist on BA-core
b24=base[base["time"]>="2020-01-01"]; n24=new[new["time"]>="2020-01-01"]
print(f"[base] TIER_BAL 2020+={int(b24['play_type'].isin(TIER_BAL).sum()):,}")
print(f"[ew5 ] TIER_BAL 2020+={int(n24['play_type'].isin(TIER_BAL).sum()):,}")
print("DONE ba_v11_ew5_sig.pkl")
