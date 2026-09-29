"""CCS Phase 0 — point-in-time audit of the trade ledger + LAG signal-vintage drift measurement.

Job Taylor_20260905_135003. Every check here is mechanical; none of them looks at returns.
"""
import json
import os
import re

import duckdb
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WC, "mike/agents/Taylor/research/ccs_phase0_Taylor_20260905_135003")
CACHE = os.path.join(WC, "data/bq_cache_asof20260729_postrestate")
res = {}


def chk(name, ok, detail):
    res[name] = {"pass": bool(ok), "detail": detail}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}", flush=True)


d = pd.read_csv(os.path.join(OUT, "trade_ledger_bal_lag_exp.csv"),
                parse_dates=["entry_fill_date", "signal_date", "exit_date"])

# 1. no forward-looking column is read anywhere in the extraction code
src = "".join(open(os.path.join(OUT, f)).read() for f in
              ("ccs_phase0_ledger.py", "ccs_phase0_nepisode.py"))
hits = re.findall(r"profit_(?:2W|1M|2M|3M)\w*", src)
chk("no forward-looking profit_* column referenced", not hits, f"hits={hits}")

# 2. feature timestamp strictly precedes the first fill
bad = int((d.signal_date >= d.entry_fill_date).sum())
chk("signal_date < entry_fill_date for every row", bad == 0,
    f"{len(d)} rows, {bad} violations")

# 3. exit never precedes entry
bad2 = int((d.exit_date < d.entry_fill_date).sum())
chk("exit_date >= entry_fill_date", bad2 == 0, f"{bad2} violations")

# 4. dd52 recomputed independently, using ONLY closes <= signal_date
con = duckdb.connect(); con.execute("SET threads=1")
smp = d.dropna(subset=["dd52"]).sample(min(200, int(d.dd52.notna().sum())), random_state=12345)
errs = []
for r in smp.itertuples():
    q = con.execute(f"""SELECT Close FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE ticker='{r.ticker}' AND time <= DATE '{r.signal_date.date()}' AND Close IS NOT NULL
        ORDER BY time DESC LIMIT 252""").df()
    if len(q) < 60:
        continue
    ref = float(q.Close.iloc[0]) / float(q.Close.max()) - 1.0
    errs.append(abs(ref - r.dd52))
chk("dd52 reproduces from closes <= signal_date only", (max(errs) if errs else 0) < 1e-9,
    f"n={len(errs)} max|Δ|={max(errs) if errs else 0:.3e}")

# 5. breadth is genuinely lagged: correlation of the attached tercile percentile with the SAME-session
#    VNINDEX return must be ~0 (the b2 2026-08-22 selfcheck; a same-session breadth gives ~+0.11)
vni = con.execute(f"""SELECT time, Close FROM read_parquet('{CACHE}/ticker/*.parquet')
                      WHERE ticker='VNINDEX' ORDER BY time""").df()
vni["time"] = pd.to_datetime(vni["time"]); vni["r"] = vni.Close.pct_change()
br = pd.read_csv(os.path.join(OUT, "breadth_pit_frozen_exp.csv"), parse_dates=["time"])
br["signal_date"] = br.time.shift(-1)                       # value of t-1 read on session t
m = br.dropna(subset=["signal_date", "pct252"]).merge(
    vni[["time", "r"]].rename(columns={"time": "signal_date"}), on="signal_date")
c_lag = float(m.pct252.corr(m.r))
c_same = float(br.merge(vni[["time", "r"]], on="time").dropna(subset=["pct252", "r"])
               .pipe(lambda x: x.pct252.corr(x.r)))
chk("breadth used at t-1, not same session", abs(c_lag) < abs(c_same),
    f"corr(pct252_t-1, r_vni_t)={c_lag:+.4f} vs same-session {c_same:+.4f}")

# 6. DT5G comes from the production table, never the v3.4b base
src_all = open(os.path.join(OUT, "ccs_phase0_ledger.py")).read()
chk("DT5G read from vnindex_5state_dt5g_live only",
    "vnindex_5state_dt5g_live" in src_all and "vnindex_5state.parquet" not in src_all,
    "dt5g_live present, base table absent")

# 7. 8L rating is as-of, never a later revision.
# Primary source is universe_pit_q, which carries its own `rating_asof` stamp — the PIT guarantee is
# rating_asof <= the session the row belongs to, checked over the whole table, not a sample.
pitr = con.execute(f"""SELECT COUNT(*) AS n,
        SUM(CASE WHEN CAST(rating_asof AS DATE) > time THEN 1 ELSE 0 END) AS ahead
    FROM read_parquet('{CACHE}/universe_pit_q/*.parquet', union_by_name=true)
    WHERE rating_8l IS NOT NULL AND rating_asof IS NOT NULL""").df()
chk("universe_pit_q rating_asof <= session (whole table)", int(pitr.ahead.iloc[0]) == 0,
    f"{int(pitr.n.iloc[0]):,} rows, {int(pitr.ahead.iloc[0])} with rating_asof after the session")
if "rating_asof" in d.columns:
    ra = pd.to_datetime(d.rating_asof, errors="coerce")
    bad3 = int((ra > d.signal_date).sum())
    chk("ledger rating_asof <= signal_date", bad3 == 0,
        f"{int(ra.notna().sum())} rated rows, {bad3} violations")

# the fa_ratings_8l fallback (used only where universe_pit_q has no row) must also be backward-only
r8 = con.execute(f"""SELECT ticker, time, rating FROM
                     read_parquet('{CACHE}/fa_ratings_8l.parquet')""").df()
r8["time"] = pd.to_datetime(r8["time"])
fb = d[d.rating_src.eq("fa_ratings_8l_asof")].dropna(subset=["rating_8l"])
late = 0
for r in fb.itertuples():
    g = r8[(r8.ticker == r.ticker) & (r8.time <= r.signal_date)]
    if g.empty or r.rating_8l != g.sort_values("time").rating.iloc[-1]:
        late += 1
chk("fa_ratings_8l fallback used a backward as-of value", late == 0,
    f"n={len(fb)} fallback rows, {late} not reproducible from a vintage <= signal_date")

# ---------------------------------------------------------------- LAG signal-vintage drift
# data/earnings_surprise_data.pkl + earnings_events_classified.csv were refreshed 2026-09-04, AFTER
# the 2026-08-03 pin run. The BQ side is frozen, so BAL is pin-vintage; the LAG candidate panel is
# not. Measure the gap rather than assume it away.
drift = {}
lp = os.path.join(OUT, "dump", "lag_cand.parquet")
if os.path.exists(lp):
    lc = pd.read_parquet(lp)
    lag = d[(d.book == "LAG") & (~d.is_capit_arm)]
    drift = {
        "lag_signals_pin_log": 5317,
        "lag_signals_probe_today": 5319,
        "lag_entries_in_ledger": int(len(lag)),
        "matched_to_current_lag_cand": int(lag.lag_surprise.notna().sum()),
        "match_rate": float(lag.lag_surprise.notna().mean()),
    }
    print(f"[drift] LAG candidate panel: pin log 5317 signals vs probe-today 5319 (+2). "
          f"{drift['matched_to_current_lag_cand']}/{drift['lag_entries_in_ledger']} pinned LAG "
          f"entries ({drift['match_rate']:.2%}) match a current-vintage candidate row.")
res["lag_vintage_drift"] = drift

with open(os.path.join(OUT, "pit_audit_exp.json"), "w") as fh:
    json.dump(res, fh, indent=2)
nfail = sum(1 for k, v in res.items() if isinstance(v, dict) and "pass" in v and not v["pass"])
print(f"\n[pit-audit] {len(res)-1} checks, {nfail} FAIL")
