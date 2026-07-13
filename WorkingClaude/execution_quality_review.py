"""Execution-quality review harness — run on 2026-06-30 for the fill-timing go/no-go.
Reads paper execution logs (data/execution_logs/exec_*_journal.csv + dnse_raw_*.jsonl) and reports the
metrics that ARE decidable in a ~2-day window: WINDOW ADHERENCE (mechanics) + errors + directional fill
sanity. The bps EDGE itself needs weeks of fills (daily noise std 100-220bps >> 5-17bps edge) -> tracked
ongoing, NOT gated here. Usage: python3 execution_quality_review.py [--since YYYY-MM-DD] [--account LABEL]

Decision rule (30-06): apply (flip fill_timing_live_gate=false) if MECHANICS clean — orders release in the
right windows, no API rejects, fills not worse than open per side. Edge validates post-go-live."""
import os, sys, glob, json
from datetime import datetime, time
import pandas as pd

EXEC = "data/execution_logs"
BUY_WIN = (time(10, 45), time(11, 15))     # mirror config.py buy_window
SELL_WIN = (time(9, 15), time(9, 45))      # mirror config.py sell_window
since = "2026-06-26"
if "--since" in sys.argv:
    since = sys.argv[sys.argv.index("--since") + 1]
# --account LABEL: filter on the ORDER OBJECT's accountNo (present in every order record since
# go-live) — the top-level account_no field only exists in files written after the 2026-07-06
# cross-account log fix, so filtering on it would silently drop all 07-01/07-02 go-live data.
ACCT = None
if "--account" in sys.argv:
    label = sys.argv[sys.argv.index("--account") + 1]
    accs = json.load(open("secrets/trading_bot_accounts.json"))["accounts"]
    ACCT = next((a.get("account_id") for a in accs if a.get("label") == label), None)
    if not ACCT:
        sys.exit(f"unknown account label or no account_id: {label}")

def _in(t, win):
    return win[0] <= t <= win[1]

# ---- 1. dnse_raw jsonl: actual fills ----
# Fills live in the `orders` POLL records (payload.orders list) — a place_order resp always has
# fillQuantity=0 at placement, so reading only payload.resp reports zero fills (bug found
# 2026-07-13, job Taylor_20260713_040055). Ingest both, dedup to the LAST state per (date, order
# id); fill timestamp = first poll where fillQuantity > 0.
# Known limitation: an order that fills at ATC AFTER the bot's last poll of the day keeps its
# stale pre-fill state here (e.g. ZaloPay VHC 600sh 2026-07-10, order 502431: last poll "New",
# broker positions confirm it filled) — cross-check next-day positions for full-day accounting.
order_state, first_fill_ts = {}, {}
def _ingest(o, ts, d):
    if not isinstance(o, dict) or not o.get("symbol") or o.get("id") is None: return
    if ACCT and str(o.get("accountNo")) != str(ACCT): return
    key = (d, o["id"])
    side = o.get("side", "")               # NB=buy, NS=sell
    fq = o.get("fillQuantity", 0) or 0
    order_state[key] = {"ticker": o.get("symbol"),
                        "side": "buy" if side == "NB" else ("sell" if side == "NS" else side),
                        "status": o.get("orderStatus", ""), "fill_qty": fq,
                        "avg_price": o.get("averagePrice", 0) or 0, "price": o.get("price", 0),
                        "date": d, "ts": first_fill_ts.get(key, ts)}
    if fq > 0 and key not in first_fill_ts:
        first_fill_ts[key] = ts; order_state[key]["ts"] = ts

for f in sorted(glob.glob(f"{EXEC}/dnse_raw_*.jsonl")):
    d = os.path.basename(f).replace("dnse_raw_", "").replace(".jsonl", "")
    if d < since: continue
    for line in open(f, encoding="utf-8"):
        try: rec = json.loads(line)
        except Exception: continue
        p = rec.get("payload", {})
        if not isinstance(p, dict): continue
        ts = rec.get("ts")
        resp = p.get("resp")
        if isinstance(resp, dict): _ingest(resp, ts, d)
        for o in (p.get("orders") or []):
            _ingest(o, ts, d)
F = pd.DataFrame(list(order_state.values()))

# ---- 2. journal CSVs: ft: window notes + errors ----
jrows = []
# PAPER (exec_main_*) only: live journals carry vacuous "ft:in-window" notes (live_gate forces
# mult=1.0 before the window check — see _fill_timing_mult), which inflated adherence to ~98%
# from live 09:15 buys. Found 2026-07-09 (job Taylor_20260709_101602).
for f in sorted(glob.glob(f"{EXEC}/exec_main_*_journal.csv")):
    try: j = pd.read_csv(f); j["src"] = os.path.basename(f)
    except Exception: continue
    jrows.append(j)
J = pd.concat(jrows, ignore_index=True) if jrows else pd.DataFrame()

print(f"=== EXECUTION-QUALITY REVIEW (since {since}) ===")
if F.empty and J.empty:
    print("\nNO execution data yet. Re-run AFTER the 2026-06-29 / 06-30 paper sessions place strategy orders.")
    print("(Today's dnse_raw has API smoke-tests only; strategy fills appear once paper trading runs.)")
    sys.exit(0)

# ---- A. window adherence (the PRIMARY mechanics gate) ----
print("\n--- A. WINDOW ADHERENCE (mechanics: did orders release in the right time-of-day?) ---")
if not J.empty and "note" in J.columns:
    ft = J[J["note"].astype(str).str.contains("ft:", na=False)]
    if len(ft):
        inw = ft["note"].astype(str).str.contains("in-window").mean() * 100
        print(f"   journal ft-notes: {len(ft)} placements | in-window {inw:.0f}% | out-of-window {100-inw:.0f}%")
    else:
        print("   journal present but no ft: notes yet")
else:
    print("   (no journal CSV yet — using fill timestamps below)")
real = F[(F["fill_qty"] > 0) & (F["status"].astype(str).str.contains("Fill", case=False, na=False))] if not F.empty else pd.DataFrame()
if len(real):
    real = real.copy(); real["t"] = pd.to_datetime(real["ts"]).dt.time
    for sd, win, lbl in (("buy", BUY_WIN, "10:45-11:15"), ("sell", SELL_WIN, "09:15-09:45")):
        s = real[real["side"] == sd]
        if len(s):
            adh = s["t"].apply(lambda x: _in(x, win)).mean() * 100
            print(f"   {sd.upper()} fills={len(s)} | in target window ({lbl}): {adh:.0f}%")

# ---- B. errors / rejects ----
print("\n--- B. ERRORS / REJECTS (must be 0 or explained) ---")
if not F.empty:
    bad = F[F["status"].astype(str).str.contains("Reject|Fail|Error", case=False, na=False)]
    print(f"   rejected/failed orders: {len(bad)}")
    for _, r in bad.head(8).iterrows():
        print(f"     {r['ts']} {r['ticker']} {r['side']} status={r['status']}")
if not J.empty and "event" in J.columns:
    jbad = J[J["event"].astype(str).str.contains("FAIL|ERROR|REJECT", case=False, na=False)]
    if len(jbad): print(f"   journal FAIL/ERROR events: {len(jbad)}")

# ---- C. directional fill sanity (buy not > open, sell not < open) ----
print("\n--- C. DIRECTIONAL FILL SANITY (needs day-open; bps EDGE itself needs weeks, not gated here) ---")
if len(real):
    try:
        sys.path.insert(0, os.getcwd()); os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
        from bq_local_cache import get_cache
        lc = get_cache()
        tks = "','".join(sorted(real["ticker"].dropna().unique()))
        opens = lc.query(f"SELECT ticker, time, Open FROM tav2_bq.ticker_1m WHERE ticker IN ('{tks}') AND time >= DATE '{since}'")
        opens["key"] = opens["ticker"] + "|" + pd.to_datetime(opens["time"]).dt.strftime("%Y-%m-%d")
        omap = dict(zip(opens["key"], opens["Open"]))
        real["dopen"] = real.apply(lambda r: omap.get(f"{r['ticker']}|{r['date']}"), axis=1)
        v = real.dropna(subset=["dopen"])
        v = v[v["avg_price"] > 0]
        if len(v):
            v = v.copy(); v["bps_vs_open"] = (v["avg_price"] / v["dopen"] - 1) * 1e4
            for sd in ("buy", "sell"):
                s = v[v["side"] == sd]
                if len(s):
                    good = "lower=better" if sd == "buy" else "higher=better"
                    print(f"   {sd.upper()} fill vs day-open: mean {s['bps_vs_open'].mean():+.1f} bps (n={len(s)}, {good})")
        else:
            print("   day-open not in cache yet for these dates (cache syncs 23:45) — re-run after sync")
    except Exception as e:
        print(f"   (skipped vs-open: {str(e)[:80]})")
else:
    print("   no completed fills yet")

print("\n=== GO/NO-GO CHECKLIST (30-06) ===")
print("  [ ] BUY window adherence high (orders concentrating 10:45-11:15)")
print("  [ ] SELL window adherence high (orders at open 09:15-09:45)")
print("  [ ] 0 rejects/fails (or each explained)")
print("  [ ] BUY fill not materially > open; SELL not materially < open")
print("  -> if mechanics clean: flip fill_timing_live_gate=false. EDGE (+5-17bps) validates over weeks.")
