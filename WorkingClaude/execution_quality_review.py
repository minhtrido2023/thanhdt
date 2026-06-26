"""Execution-quality review harness — run on 2026-06-30 for the fill-timing go/no-go.
Reads paper execution logs (data/execution_logs/exec_*_journal.csv + dnse_raw_*.jsonl) and reports the
metrics that ARE decidable in a ~2-day window: WINDOW ADHERENCE (mechanics) + errors + directional fill
sanity. The bps EDGE itself needs weeks of fills (daily noise std 100-220bps >> 5-17bps edge) -> tracked
ongoing, NOT gated here. Usage: python3 execution_quality_review.py [--since YYYY-MM-DD]

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

def _in(t, win):
    return win[0] <= t <= win[1]

# ---- 1. dnse_raw jsonl: actual fills ----
fills = []
for f in sorted(glob.glob(f"{EXEC}/dnse_raw_*.jsonl")):
    d = os.path.basename(f).replace("dnse_raw_", "").replace(".jsonl", "")
    if d < since: continue
    for line in open(f, encoding="utf-8"):
        try: rec = json.loads(line)
        except Exception: continue
        p = rec.get("payload", {}); resp = p.get("resp", {}) if isinstance(p, dict) else {}
        if not isinstance(resp, dict): continue
        status = resp.get("orderStatus", "")
        side = resp.get("side", "")            # NB=buy, NS=sell
        fq = resp.get("fillQuantity", 0) or 0
        avg = resp.get("averagePrice", 0) or 0
        fills.append({"ts": rec.get("ts"), "kind": rec.get("kind"), "ticker": resp.get("symbol"),
                      "side": "buy" if side == "NB" else ("sell" if side == "NS" else side),
                      "status": status, "fill_qty": fq, "avg_price": avg, "price": resp.get("price", 0),
                      "date": d})
F = pd.DataFrame(fills)

# ---- 2. journal CSVs: ft: window notes + errors ----
jrows = []
for f in sorted(glob.glob(f"{EXEC}/exec_*_journal.csv")):
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
