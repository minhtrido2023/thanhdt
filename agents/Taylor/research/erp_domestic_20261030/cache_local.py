"""Chụp các nguồn local vào data/ (bất biến) — job Taylor_20261030_034654."""
import os, sys, shutil
from datetime import date, timedelta
import pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WC); os.chdir(WC)
HERE = os.path.dirname(os.path.abspath(__file__)); DD = os.path.join(HERE, "data")
import deposit_rate_vn as d, cctg_rate_vn as c
st, en = date(2011, 1, 1), date(2026, 10, 29)
rows = [(str(st + timedelta(i)), d.current_deposit_rate(str(st + timedelta(i)))) for i in range((en - st).days + 1)]
pd.DataFrame(rows, columns=["date", "big4_12m"]).to_csv(os.path.join(DD, "deposit_big4_12m_daily.csv"), index=False)
shutil.copy(os.path.join(WC, "data/benchmark/vnindex_tr_daily.csv"), os.path.join(DD, "vnindex_tr_daily.csv"))
shutil.copy(os.path.join(WC, "mike/agents/Taylor/research/idle_cash_proxy_20260927/fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv"), DD)
shutil.copy(os.path.join(WC, "mike/agents/Taylor/research/dgc_discount_rate_20261029/data/tpcp10y_annual.csv"), DD)
print("cctg", [f for f in dir(c) if not f.startswith("_")][:30])
print("eff", d.effective_deposit_rate("2026-10-29"), "consumer", d.consumer_deposit_rate("2026-10-29"))
