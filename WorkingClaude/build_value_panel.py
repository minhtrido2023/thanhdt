# -*- coding: utf-8 -*-
"""
build_value_panel.py  (Stage 0 of 8L valuation v3 research)
============================================================
Monthly research panel 2014->now for IC-testing the valuation composite. Superset of
data/dcf_ic_panel.csv (keeps PE/PB/PB_MA5Y/PB_SD5Y/PCF/ROIC_Trailing/ROIC5Y/ROE_Min5Y/
profit_1M/2M/3M/turnover so dcf_ic_test.py stays drop-in) PLUS the new fields v3 needs:
route (ICB-derived), CF_OA_3Y + CF_OA_P0..P3 (cfo_normy/TTM), Revenue_P0..P3 + OShares
(point-in-time PS = mktcap/TTM-sales), FSCORE, ROE_Min3Y, and the SBV refi rate.

One row per ticker per calendar month (last trading day). Output: data/value_panel_2014.csv
Run:  source wc_env.sh && python build_value_panel.py
"""
import os, sys, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
sys.path.insert(0, WORKDIR)

def bq(sql, max_rows=600000):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'cat "{tmp}" | bq query --quiet --use_legacy_sql=false --project_id={PROJECT} '
                           f'--format=csv --max_rows={max_rows}',
                           capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if not r.stdout.strip():
        raise RuntimeError("bq no rows. stderr:\n" + r.stderr[-2000:])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ---- 1) monthly panel from `ticker` (last trading day per month, 2014+) ----
print("[1] pull monthly ticker panel 2014+ ...")
PANEL_SQL = """
SELECT t.ticker, t.time, t.ICB_Code, t.PE, t.PB, t.PCF, t.PB_MA5Y, t.PB_SD5Y, t.PE_MA5Y, t.PE_SD5Y,
       t.ROIC_Trailing, t.ROIC5Y, t.ROE_Min5Y, t.ROE_Min3Y, t.FSCORE,
       t.CF_OA_5Y, t.CF_OA_P0, t.CF_OA_P1, t.CF_OA_P2, t.CF_OA_P3, t.OShares,
       t.profit_1M, t.profit_2M, t.profit_3M, t.Close, t.Volume,
       SAFE_MULTIPLY(t.Close, t.Volume) AS turnover
FROM tav2_bq.ticker AS t
WHERE t.time >= DATE '2014-01-01'
  AND t.ticker != 'VNINDEX' AND t.ticker != 'VN30' AND t.ticker NOT LIKE 'VN30F%'
QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker, DATE_TRUNC(t.time, MONTH) ORDER BY t.time DESC) = 1
"""
p = bq(PANEL_SQL); p["time"] = pd.to_datetime(p["time"])
print(f"    panel rows={len(p)}  tickers={p.ticker.nunique()}  {p.time.min().date()}->{p.time.max().date()}")

# ---- 2) ticker_financial fields missing from `ticker` (as-of merge) ----
print("[2] pull ticker_financial (PS inputs + CF_OA_3Y) ...")
FIN_SQL = """
SELECT tf.ticker, tf.time, tf.CF_OA_3Y, tf.Revenue_P0, tf.Revenue_P1, tf.Revenue_P2, tf.Revenue_P3
FROM tav2_bq.ticker_financial AS tf WHERE tf.time >= DATE '2012-01-01'
"""
f = bq(FIN_SQL); f["time"] = pd.to_datetime(f["time"])
f = f.sort_values("time")

# ---- 3) as-of merge (latest financial with f.time <= panel.time, per ticker) ----
print("[3] as-of merge financial -> panel ...")
p = p.sort_values("time")
p = pd.merge_asof(p, f, on="time", by="ticker", direction="backward")

# point-in-time PS = market cap (panel-day Close*OShares) / trailing-4Q sales
rev_ttm = p[["Revenue_P0","Revenue_P1","Revenue_P2","Revenue_P3"]].sum(axis=1, min_count=1)
p["PS"] = np.where(rev_ttm > 0, (p["Close"] * p["OShares"]) / rev_ttm, np.nan)
p["pb_z"] = ((p["PB"] - p["PB_MA5Y"]) / p["PB_SD5Y"].replace(0, np.nan)).round(3)

# ---- 4) route (port of rating_8l.route_of) ----
print("[4] route ...")
COMMODITY_MAP = {"DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore",
 "DCM":"urea","DPM":"urea","DDV":"dap","LAS":"dap","DGC":"dap","CSV":"caustic_soda"}
SUGAR_SET = {"SLS","SBT","LSS","KTS","QNS"}
CEMENT_SET = {"CLH","HT1","HOM","BCC","HVX","SCJ","BTS","QNC","CCM"}
HOLDING_OVERRIDE = {"REE"}; REALESTATE_OVERRIDE = {"HHS"}
def _set(path, col="ticker"):
    try: return set(pd.read_csv(os.path.join(WORKDIR,"data",path))[col])
    except Exception as e: print(f"    warn {path}: {e}"); return set()
bank_set  = _set("bank_lens_v3.csv")
power_set = _set("power_lens.csv") - bank_set
def route_of(tk, icb):
    if tk in HOLDING_OVERRIDE: return "COMPOUNDER"
    if tk in REALESTATE_OVERRIDE: return "REALESTATE"
    if tk in bank_set or icb==8355: return "BANK"
    if pd.notna(icb) and 8530<=icb<=8579: return "INSURANCE"
    if pd.notna(icb) and 8770<=icb<=8779: return "SECURITIES"
    if tk in power_set: return "POWER"
    if tk in COMMODITY_MAP or tk in SUGAR_SET or tk in CEMENT_SET: return "CYCLICAL"
    if icb==8633: return "REALESTATE"
    return "COMPOUNDER"
p["route"] = [route_of(t, c) for t, c in zip(p.ticker, p.ICB_Code)]

# ---- 5) SBV refi rate (deposit-rate anchor), forward-filled per month ----
print("[5] refi rate ...")
try:
    from sbv_macro_overlay import SBV_REFI_EVENTS
    ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time","refi_rate"]); ev["time"]=pd.to_datetime(ev["time"])
    ev = ev.sort_values("time")
    p = pd.merge_asof(p.sort_values("time"), ev, on="time", direction="backward")
except Exception as e:
    print(f"    warn refi: {e}"); p["refi_rate"] = np.nan

# ---- 6) write ----
out = os.path.join(WORKDIR, "data", "value_panel_2014.csv")
p.sort_values(["time","ticker"]).to_csv(out, index=False)
print(f"\n[done] {out}  rows={len(p)}  cols={len(p.columns)}")
print("  route dist:", p.route.value_counts().to_dict())
print("  coverage %: " + ", ".join(f"{c}={100*p[c].notna().mean():.0f}"
      for c in ["PE","PCF","pb_z","PS","CF_OA_3Y","FSCORE","refi_rate","profit_2M"]))
print("  by-year rows:", p.groupby(p.time.dt.year).size().to_dict())
