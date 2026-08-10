import os, sys
from datetime import datetime, timedelta
import pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11
TIER_BAL = ["MEGA","MOMENTUM","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
END = datetime.now().strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
sig = bq(SIGNAL_V11.format(start=START, end=END))
sig["time"] = pd.to_datetime(sig["time"])
b = sig[sig["play_type"].isin(TIER_BAL)].copy()
print(f"BAL rows (TIER_BAL, 365d, TRUOC lop D1/overheat/EXBULL cua golive): {len(b)}")
print(f"  liq in [1e9,2e9) = {int((b['liq']<2e9).sum())} dong = {(b['liq']<2e9).mean()*100:.1f}%")
print(f"  ten rieng bi cat: {sorted(set(b.loc[b['liq']<2e9,'ticker']))}")
print(f"  so phien co it nhat 1 dong bi cat: {b.loc[b['liq']<2e9,'time'].nunique()} / {b['time'].nunique()}")
d = b.groupby("time").size()
print(f"  so dong eligible/phien: median {d.median():.0f}, max {d.max()}, so phien >12: {(d>12).sum()}/{len(d)}")
