# -*- coding: utf-8 -*-
"""Regression self-check for the money-path freshness fixes (audit Taylor_20260711_031821,
fix job Taylor_20260711_043508 — user-approved).

Incident recap: BQ cache only syncs 23:45 ICT, so any same-day read of BQ Close is
structurally yesterday's price (coding_guidelines §6 bright-line rule, user 2026-07-09).
The audit found the money path (plan sizing → plan context → dispatch artifacts → P&L
report) still had spots reading stale-by-construction data or failing silently:

  A. F1  compute_active_nav.resolve_prices() — --asof today/empty MUST take the DNSE-live
     branch (sizing basis for excluded_tickers accounts); BQ only for past dates; a ticker
     missing from DNSE falls back to BQ per-ticker and is MARKED 'bq_close_stale' (the
     JSON provenance must not lie).
  B. F2  golive_recommend_v23 rec field 'close' (BQ close of the SIGNAL day) renamed to
     'close_bq_stale_DO_NOT_USE_AS_REFPRICE' — the 07-09 incident proved a prompt-only ban
     does not stop an LLM plan generator from grabbing a handy 'close' as ref_price; after
     the rename there is NO field called 'close' left in the plan context to grab.
     Downstream: Mafee's BQ pusher parses new+old header (BQ column stays 'close' — stable
     audit schema); trading_bot strategies reads new name with old-name fallback.
  C. F5  bq_freshness_check.sh — gate checks the BQ table but DollarBill reads FILES
     (golive_state_today.json + recommendations CSV) written by pipeline steps that only
     WARN on failure. The REAL _assert_fresh_artifact() (extracted from the script) must
     die on stale/missing artifact BEFORE the dispatch loop, pass on fresh, and the
     script's ordering must be: epoch capture → pipeline 1-3 → assertions → dispatch.
  D. F6  verify_account_snapshot.pnl_coverage_warnings() — live broker positions with no
     traceable fill history (legacy, e.g. ZaloPay DGC/VIB/VPB) must produce a LOUD
     per-ticker warning, never a silent skip (first ZaloPay weekly/monthly report trap);
     unreadable positions → explicit "cannot verify coverage" warning.
  E. F7  daily_nav_snapshot._write_nav_history() — atomic tmp+os.replace (executor.py
     _save_state pattern): kill mid-write must leave the previous file byte-intact.

Run: python3 money_path_freshness_selfcheck.py   (exit 0 = all pass)
NOTE: never touches BQ, DNSE, or the bus — everything is sandboxed/mocked in tmp.
"""
import datetime
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
import types

WC = "/home/trido/thanhdt/WorkingClaude"
MIKE_BIN = os.path.join(WC, "mike", "bin")
FRESHNESS_SH = os.path.join(MIKE_BIN, "bq_freshness_check.sh")

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ══════════════════════════════════════════════════════════════════════════════
print("A. F1 — compute_active_nav.resolve_prices: today→DNSE, past→BQ, miss→marked fallback")
# ══════════════════════════════════════════════════════════════════════════════
can = load_module("_sc_compute_active_nav", os.path.join(MIKE_BIN, "compute_active_nav.py"))

calls = {"dnse": 0, "bq": 0}
DNSE_PX = {"DGC": 51.0, "VPB": 22.5}


def fake_dnse_close_prices(tickers, with_source=False):
    """`with_source` thêm 2026-08-11 (job Taylor_20260810_183618): mã đang GDKHQ lấy giá tham
    chiếu phiên hôm nay (secdef.basicPrice) thay giá đóng cửa phiên trước, nên provenance phải
    phân biệt được hai nguồn. Fake phải nhận kwarg này, nếu không nó chỉ đang test chữ ký cũ."""
    calls["dnse"] += 1
    px = {t: DNSE_PX[t] for t in tickers if t in DNSE_PX}
    return (px, {t: "dnse_g1_today" for t in px}) if with_source else px


def fake_bq_close_prices(tickers, as_of_date=None):
    calls["bq"] += 1
    return {t: 99.9 for t in tickers}, None


# resolve_prices does `from verify_account_snapshot import dnse_close_prices` at call
# time — pre-inject a fake module so the real one (and any broker call) never loads.
fake_vas = types.ModuleType("verify_account_snapshot")
fake_vas.dnse_close_prices = fake_dnse_close_prices
sys.modules["verify_account_snapshot"] = fake_vas
can.bq_close_prices = fake_bq_close_prices

today = datetime.date.today().isoformat()

calls.update(dnse=0, bq=0)
px, src, err = can.resolve_prices(["DGC", "VPB"], None)
check("A1 asof=None → DNSE-live branch, BQ untouched",
      calls == {"dnse": 1, "bq": 0} and px == DNSE_PX
      and set(src.values()) == {"dnse_g1_today"} and err is None,
      f"calls={calls} src={src}")

calls.update(dnse=0, bq=0)
px, src, err = can.resolve_prices(["DGC"], today)
check("A2 asof=today → DNSE-live branch, BQ untouched",
      calls == {"dnse": 1, "bq": 0} and src == {"DGC": "dnse_g1_today"},
      f"calls={calls}")

calls.update(dnse=0, bq=0)
px, src, err = can.resolve_prices(["DGC", "VPB"], "2026-07-01")
check("A3 asof=past date → BQ branch, DNSE untouched",
      calls == {"dnse": 0, "bq": 1} and set(src.values()) == {"bq_close"},
      f"calls={calls} src={src}")

calls.update(dnse=0, bq=0)
_stderr, sys.stderr = sys.stderr, io.StringIO()
try:
    px, src, err = can.resolve_prices(["DGC", "XXX"], None)
    warn_txt = sys.stderr.getvalue()
finally:
    sys.stderr = _stderr
check("A4 DNSE misses a ticker → per-ticker BQ fallback MARKED bq_close_stale + loud warning",
      px == {"DGC": 51.0, "XXX": 99.9}
      and src == {"DGC": "dnse_g1_today", "XXX": "bq_close_stale"}
      and "XXX" in warn_txt and "23:45" in warn_txt,
      f"src={src}")

# ══════════════════════════════════════════════════════════════════════════════
print("B. F2 — rec field 'close' renamed: generator emits no bare 'close'; readers parse new+old")
# ══════════════════════════════════════════════════════════════════════════════
RENAMED = "close_bq_stale_DO_NOT_USE_AS_REFPRICE"

gr_src = read(os.path.join(WC, "deploy_golive_dt5g_v4", "golive_recommend_v23.py"))
m = re.search(r"rec_df = pd\.DataFrame\(recs, columns=\[(.*?)\]\)", gr_src, re.S)
cols = re.findall(r'"([^"]+)"', m.group(1)) if m else []
check("B1 golive_recommend_v23 rec_df columns: renamed field present, bare 'close' gone",
      RENAMED in cols and "close" not in cols, f"cols={cols}")

# newest real CSV (regenerated post-fix 2026-07-11) must carry the new header
outs = sorted(f for f in os.listdir(os.path.join(WC, "deploy_golive_dt5g_v4", "out"))
              if re.match(r"golive_v23_recommendations_\d{4}-\d{2}-\d{2}\.csv$", f))
if outs:
    hdr = read(os.path.join(WC, "deploy_golive_dt5g_v4", "out", outs[-1])).splitlines()[0].split(",")
    check("B2 newest real recommendations CSV header uses renamed field, no bare 'close'",
          RENAMED in hdr and "close" not in hdr, f"{outs[-1]}: {hdr}")
else:
    check("B2 newest real recommendations CSV header uses renamed field", False, "no CSV found")

# Mafee BQ pusher: load_recommendations parses BOTH headers (BQ column stays 'close')
sys.path.insert(0, os.path.join(WC, "mike", "agents", "Mafee"))
import push_recommend_v23_to_bq as pusher  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    outdir = os.path.join(td, "deploy_golive_dt5g_v4", "out")
    os.makedirs(outdir)
    newcsv = f"book,ticker,play_type,ta,{RENAMED},sector,weight_pct,status\nBAL,FPT,MEGA,85,121.5,1,10.0,FULL\n"
    oldcsv = "book,ticker,play_type,ta,close,sector,weight_pct,status\nBAL,ACB,MEGA,80,24.8,1,10.0,FULL\n"
    with open(os.path.join(outdir, "golive_v23_recommendations_2099-01-01.csv"), "w") as f:
        f.write(newcsv)
    with open(os.path.join(outdir, "golive_v23_recommendations_2099-01-02.csv"), "w") as f:
        f.write(oldcsv)
    _wd, pusher.WORKDIR = pusher.WORKDIR, td
    try:
        rn = pusher.load_recommendations("2099-01-01")
        ro = pusher.load_recommendations("2099-01-02")
    finally:
        pusher.WORKDIR = _wd
check("B3 Mafee pusher: new-header CSV → BQ column close=121.5, renamed col not in extra",
      rn[0]["close"] == 121.5 and (rn[0]["extra"] is None or RENAMED not in rn[0]["extra"]),
      f"row={rn[0]}")
check("B4 Mafee pusher: old-header CSV (pre-rename archive) still parses close=24.8",
      ro[0]["close"] == 24.8, f"row={ro[0]}")

st_src = read(os.path.join(WC, "trading_bot", "strategies.py"))
check("B5 strategies.py paper-mirror reads renamed field (with old-name fallback for archives)",
      RENAMED in st_src and 'r.get("close")' in st_src)

# ══════════════════════════════════════════════════════════════════════════════
print("C. F5 — bq_freshness_check.sh: artifact mtime assertion dies BEFORE DollarBill dispatch")
# ══════════════════════════════════════════════════════════════════════════════
fs_src = read(FRESHNESS_SH)
m = re.search(r"(_assert_fresh_artifact\(\) \{.*?\n\})", fs_src, re.S)
check("C1 _assert_fresh_artifact() exists in the script", bool(m))

if m:
    fn = m.group(1)
    with tempfile.TemporaryDirectory() as td:
        # mocked notify_thread.sh so the alert path is a no-op
        os.makedirs(os.path.join(td, "bin"))
        nt = os.path.join(td, "bin", "notify_thread.sh")
        with open(nt, "w") as f:
            f.write("#!/bin/bash\nexit 0\n")
        os.chmod(nt, 0o755)

        harness = os.path.join(td, "h.sh")
        with open(harness, "w") as f:
            f.write(f"""#!/bin/bash
ROOT={td}; DISCORD_STALE_CHANNEL=x; TODAY=t
PIPELINE_START_EPOCH="$(date +%s)"
{fn}
case "$1" in
  stale)    touch -d '2 hours ago' "$2"; _assert_fresh_artifact L "$2" ;;
  missing)  _assert_fresh_artifact L /no/such/file ;;
  fresh)    sleep 1; touch "$2"; _assert_fresh_artifact L "$2" ;;
  boundary) touch -d @"$PIPELINE_START_EPOCH" "$2"; _assert_fresh_artifact L "$2" ;;
esac
echo REACHED-DISPATCH
""")
        os.chmod(harness, 0o755)

        def run(*args):
            return subprocess.run(["bash", harness, *args], capture_output=True, text=True,
                                  cwd=td)

        art = os.path.join(td, "a.json")
        r = run("stale", art)
        check("C2 stale artifact (pipeline step silently failed) → exit 1, dispatch NOT reached",
              r.returncode == 1 and "REACHED-DISPATCH" not in r.stdout, r.stdout.strip())
        r = run("missing", art)
        check("C3 missing artifact → exit 1, dispatch NOT reached",
              r.returncode == 1 and "REACHED-DISPATCH" not in r.stdout)
        r = run("fresh", art)
        check("C4 fresh artifact → passes through to dispatch (no false positive)",
              r.returncode == 0 and "REACHED-DISPATCH" in r.stdout, r.stdout.strip())
        r = run("boundary", art)
        check("C5 boundary mtime == gate start counts as fresh (>= semantics)",
              r.returncode == 0 and "REACHED-DISPATCH" in r.stdout)

# ordering inside the real script: epoch → pipelines 1-3 → both assertions → dispatch loop
pos = {k: fs_src.find(s) for k, s in {
    "epoch": 'PIPELINE_START_EPOCH="$(date +%s)"',
    "p1": "[pipeline-1] publish_gated_state",
    "p3": "[pipeline-3] push_recommend_v23_to_bq",
    "a_state": '_assert_fresh_artifact "golive_state_today.json',
    "a_recs": '_assert_fresh_artifact "golive_v23_recommendations',
    "dispatch": "[pipeline-4] dispatch DollarBill",
}.items()}
check("C6 ordering: epoch capture < pipeline-1 < pipeline-3 < both assertions < dispatch loop",
      all(v != -1 for v in pos.values())
      and pos["epoch"] < pos["p1"] < pos["p3"] < pos["a_state"] < pos["dispatch"]
      and pos["p3"] < pos["a_recs"] < pos["dispatch"], f"pos={pos}")
check("C7 bash syntax still valid",
      subprocess.run(["bash", "-n", FRESHNESS_SH]).returncode == 0)

# ══════════════════════════════════════════════════════════════════════════════
print("D. F6 — verify_account_snapshot.pnl_coverage_warnings: legacy positions never silent")
# ══════════════════════════════════════════════════════════════════════════════
# load the REAL module under a private name (the fake injected in section A stays in
# sys.modules under the canonical name and must not be clobbered — resolve_prices relies on it)
vas = load_module("_sc_verify_account_snapshot",
                  os.path.join(MIKE_BIN, "verify_account_snapshot.py"))

warns, legacy = vas.pnl_coverage_warnings(["FPT", "ACB"], {"FPT": {}, "ACB": {}, "DGC": {}, "VIB": {}})
check("D1 legacy positions → one loud per-ticker warning each, exact phrase",
      legacy == ["DGC", "VIB"] and len(warns) == 2
      and all("excluded from P&L — no fill history (legacy)" in w for w in warns),
      f"legacy={legacy}")
warns, legacy = vas.pnl_coverage_warnings(["FPT"], {"FPT": {}})
check("D2 full coverage → no warnings, empty legacy list", warns == [] and legacy == [])
warns, legacy = vas.pnl_coverage_warnings(["FPT"], None)
check("D3 unreadable broker positions → explicit cannot-verify warning (not silence)",
      len(warns) == 1 and "KHÔNG xác minh được" in warns[0] and legacy == [])
warns, legacy = vas.pnl_coverage_warnings(["FPT", "GONE"], {"FPT": {}})
check("D4 covered-but-already-sold ticker is NOT flagged (only live-without-fills matters)",
      warns == [] and legacy == [])

# ══════════════════════════════════════════════════════════════════════════════
print("E. F7 — daily_nav_snapshot._write_nav_history: atomic, kill-mid-write leaves old file intact")
# ══════════════════════════════════════════════════════════════════════════════
dns = load_module("_sc_daily_nav_snapshot", os.path.join(MIKE_BIN, "daily_nav_snapshot.py"))
FIELDS = ["date", "nav", "mtm_stock", "cash", "margin_debt", "balance_ts"]
ROW1 = {"date": "2026-07-10", "nav": "1", "mtm_stock": "2", "cash": "3",
        "margin_debt": "0", "balance_ts": "t"}
ROW2 = dict(ROW1, date="2026-07-11")

with tempfile.TemporaryDirectory() as td:
    hist = os.path.join(td, "nav_history_sc.csv")
    dns._write_nav_history(hist, [ROW1], FIELDS)
    baseline = read(hist)
    check("E1 normal write: file has header+row, no .tmp left behind",
          baseline.splitlines()[0] == ",".join(FIELDS) and len(baseline.splitlines()) == 2
          and not os.path.exists(hist + ".tmp"))

    def exploding_rows():
        yield ROW1
        raise RuntimeError("simulated kill mid-write")

    try:
        dns._write_nav_history(hist, exploding_rows(), FIELDS)
        crashed = False
    except RuntimeError:
        crashed = True
    check("E2 kill mid-write → canonical file byte-identical to pre-crash state",
          crashed and read(hist) == baseline)

    dns._write_nav_history(hist, [ROW1, dict(ROW2, stray_old_column="x")], FIELDS)
    check("E3 recovery write succeeds; stray legacy column ignored (extrasaction)",
          len(read(hist).splitlines()) == 3 and "stray_old_column" not in read(hist))

# ══════════════════════════════════════════════════════════════════════════════
print("F. F3 — SIGNAL_V11 state5 source: trackers read DT5G gated, books clean of fake-BULL entries")
# ══════════════════════════════════════════════════════════════════════════════
# Incident: SIGNAL_V11's SQL hardcodes the v3.4b BASE table (vnindex_5state) for state5;
# golive_recommend_v23.py:77 patches it via .replace but pt_v4_dt5g/pt_v22_dt5g consumed it
# raw — the 06-29→07-09 fake-BULL window (EW-leg freeze bug) put 6 fake entries in the
# production signal book. Fix 2026-07-11 (job Taylor_20260711_064350): both trackers apply
# the same .replace; the .replace target string must keep matching or it silently no-ops.
sv_src = read(os.path.join(WC, "signal_v11_sql.py"))
from signal_v11_sql import SIGNAL_V11  # noqa: E402

REPL_TARGET = "tav2_bq.vnindex_5state AS s"
DT5G_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
check("F1 SIGNAL_V11 raw SQL contains the .replace target exactly once (alias drift = silent no-op)",
      SIGNAL_V11.count(REPL_TARGET) == 1, f"count={SIGNAL_V11.count(REPL_TARGET)}")

patched = SIGNAL_V11.replace(REPL_TARGET, DT5G_TABLE + " AS s")
base_left = re.findall(r"tav2_bq\.vnindex_5state\b(?!_)", patched)
check("F2 patched SQL: zero bare base-table reads, exactly one dt5g_live read",
      not base_left and patched.count("vnindex_5state_dt5g_live") == 1,
      f"base_left={len(base_left)}")

for fname in ("pt_v4_dt5g.py", "pt_v22_dt5g.py"):
    src = read(os.path.join(WC, fname))
    check(f"F3 {fname}: STATE_TABLE is dt5g_live AND SIGNAL_V11 goes through the .replace (no raw use)",
          f'STATE_TABLE = "{DT5G_TABLE}"' in src
          and f'SIGNAL_V11.replace("{REPL_TARGET}", STATE_TABLE + " AS s")' in src
          and "bq(SIGNAL_V11.format" not in src)

# Books regenerated post-fix must hold NO position opened on the fake-BULL signal
# (tracker full-replays from START each run, so a clean book must stay clean).
import csv as _csv  # noqa: E402
FAKE_TICKERS = {"PVD", "TVN", "VCG", "TLD", "TPB", "ASP"}
FAKE_LO, FAKE_HI = "2026-06-29", "2026-07-09"
for book in ("pt_v4_dt5g", "pt_v22_dt5g"):
    path = os.path.join(WC, "data", f"{book}_open_positions.csv")
    with open(path, encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))
    bad = [r for r in rows
           if r["ticker"] in FAKE_TICKERS and FAKE_LO <= r["entry_date"] <= FAKE_HI]
    check(f"F4 {book} open book: no fake-BULL-window entry survives replay",
          not bad, f"bad={[(r['ticker'], r['entry_date']) for r in bad]}" if bad else f"{len(rows)} rows clean")

# ══════════════════════════════════════════════════════════════════════════════
print()
if fails:
    print(f"❌ {len(fails)} FAILED: {fails}")
    sys.exit(1)
print("✅ ALL CHECKS PASS")
