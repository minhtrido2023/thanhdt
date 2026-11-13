# -*- coding: utf-8 -*-
"""
refresh_lagged_caches.py
========================
Refresh the 4 LAGGED-leg caches that the paper-trade V12 sims depend on.

PROBLEM these caches fixed: the original builders (analyze_earnings_reaction.py,
backtest_lagged_pos.py, research_earnings_surprise.py) use a "load-if-exists,
never refresh" pattern — once the .pkl exists they are never re-pulled. So the
daily paper-trade window was frozen at the build date (2026-05-19), because
pt_dates.detect_end_date() caps END_DATE at the lagged_pos_ov.pkl max time.

This script (run as step 0 of papertrade_daily.bat) brings all 4 up to the
latest BQ ticker date:
  1. earnings_px.pkl            — daily Close ĐIỀU CHỈNH, dựng lại toàn lịch sử mỗi ngày (BQ sống)
  2. lagged_pos_ov.pkl          — daily Open ĐIỀU CHỈNH + Volume_3M_P50 + Price THÔ, cùng lần kéo với [1]
     (lagged_cache_adjusted.build: validate độ sâu/độ phủ ⇒ lỗi thì KHÔNG ghi, exit 1 cuối script;
      ghi nguyên tử + .prev; .pre_adj = ảnh chụp 1 lần bản cũ trước khi đổi cơ sở)
  3. earnings_surprise_data.pkl — quarterly NP_P0..P7 (full re-pull, cheap)
  4. earnings_events_classified.csv — recomputed pre/rel/post returns + pattern
     (raw events re-pulled, returns recomputed from the fresh px pivot)

All BQ access via simulate_holistic_nav.bq (same accessor the pt sims use), so
PATH/auth behave identically under the Windows scheduled task.
"""
import os, sys, io, json, pickle, shutil, tempfile, fcntl
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = os.environ.get("LAGCACHE_WORKDIR", r"/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import lagged_cache_adjusted as LCA

# Khoá cả script: 2 lần chạy chồng nhau (cron + tay) không được cùng ghi pkl.
_LOCK = open(os.path.join(WORKDIR, "data/.refresh_lagged_caches.lock"), "w")
try:
    fcntl.flock(_LOCK, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("!! refresh_lagged_caches đang chạy ở tiến trình khác (lock bận) -> thoát, không ghi gì")
    sys.exit(3)

# Dọn *.tmp mồ côi (lần chạy trước bị kill giữa mkstemp và os.replace). Đang giữ lock ⇒ không tiến trình
# refresh nào khác đang ghi; chỉ xoá tmp mang tiền tố file của CHÍNH script này.
_OWN = ("earnings_px.pkl", "lagged_pos_ov.pkl", "earnings_surprise_data.pkl", "earnings_events.pkl",
        "lagged_carried.json", "earnings_events_classified.csv")
for _f in os.listdir(os.path.join(WORKDIR, "data")):
    if _f.endswith(".tmp") and any(_f.startswith(b + ".") for b in _OWN):
        os.remove(os.path.join(WORKDIR, "data", _f)); print(f"  dọn tmp mồ côi: data/{_f}")

print("=" * 80)
print("  REFRESH LAGGED CACHES")
print("=" * 80)


def _prep(obj):
    """datetime64 → ns, StringDtype → object (đọc chéo numpy cũ)."""
    obj = obj.copy()
    for c in obj.columns:
        if pd.api.types.is_datetime64_any_dtype(obj[c]):
            obj[c] = obj[c].astype("datetime64[ns]")
        elif isinstance(obj[c].dtype, pd.StringDtype) or str(obj[c].dtype) in ("string", "StringDtype"):
            obj[c] = obj[c].astype(object)
    return obj


def _save_pickles(items):
    """Ghi nguyên tử nhiều file: dump HẾT ra tmp (mkstemp cùng thư mục + fsync) rồi mới os.replace
    lần lượt + fsync thư mục; .prev = bản trước (1 bản lăn). Lỗi trước bước replace ⇒ không file nào đổi."""
    tmps = []
    try:
        for obj, path in items:
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=os.path.basename(path) + ".", suffix=".tmp")
            tmps.append(tmp)
            with os.fdopen(fd, "wb") as f:
                pickle.dump(_prep(obj), f); f.flush(); os.fsync(f.fileno())
        for (obj, path), tmp in zip(items, tmps):
            if os.path.exists(path): LCA.copy_atomic(path, path + ".prev")
            os.replace(tmp, path)
        dfd = os.open(os.path.dirname(items[0][1]), os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        for tmp in tmps:
            if os.path.exists(tmp): os.remove(tmp)


def _save_json_atomic(obj, path):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=os.path.basename(path) + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=1); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.remove(tmp)


def _save_pickle(obj, path):
    _save_pickles([(obj, path)])
    return path


# ── 1+2. earnings_px.pkl + lagged_pos_ov.pkl — KÉO LẠI TOÀN LỊCH SỬ, giá ĐIỀU CHỈNH ─────────
# Không append nữa (append ⇒ dòng cũ kẹt cơ sở điều chỉnh lúc fetch ⇒ cú rơi giả ngày GDKHQ, và phiên
# fetch lúc BQ chưa đủ thì thưa vĩnh viễn). Mỗi ngày dựng lại cả chuỗi 2011→END từ BQ SỐNG (không
# phải BQ_LOCAL_CACHE: năm cũ trong cache không theo hồi tố) — xem lagged_cache_adjusted.py.
# END = max(time) của tav2_bq.ticker ở CÙNG snapshot `asof` với 16 khúc năm (live, FOR SYSTEM_TIME AS OF).
# State `data/lagged_carried.json` = mã đang được mang sang (BQ cắt lịch sử): chỉ mã MỚI tính vào trần.
# Fail-safe: validate có vấn đề ⇒ KHÔNG ghi gì, giữ pkl cũ, exit 1 CUỐI script (bước 3/4 vẫn chạy).
print("\n[1+2] earnings_px.pkl + lagged_pos_ov.pkl (dựng lại toàn lịch sử, giá điều chỉnh)...")
with open("data/earnings_px.pkl", "rb") as f: px = pickle.load(f)
with open("data/lagged_pos_ov.pkl", "rb") as f: ov = pickle.load(f)
px["time"] = pd.to_datetime(px["time"]); ov["time"] = pd.to_datetime(ov["time"])
print(f"  current: px {len(px):,} / ov {len(ov):,} rows, max {px['time'].max().date()}, {px['ticker'].nunique()} tickers")
ADJ_FAIL = []
CARRY_STATE = os.path.join(WORKDIR, "data/lagged_carried.json")
try:
    with open(CARRY_STATE) as f: _known = set(json.load(f).get("tickers", []))
except (FileNotFoundError, ValueError):
    _known = set()
try:
    _asof = LCA.new_asof(); _lbq = LCA.live_bq(bq)
    _end = pd.Timestamp(_lbq("SELECT MAX(t.time) AS mx FROM tav2_bq.ticker AS t" + LCA.asof_clause(_asof))["mx"].iloc[0])
    npx, nov, problems, stats, carried = LCA.build(_lbq, px, ov, _end, known_carried=_known, asof=_asof)
except Exception as e:
    problems, stats, carried = [f"kéo BQ lỗi: {type(e).__name__}: {str(e)[:300]}"], {}, None
print(f"  stats: {stats}")
if carried is not None and len(carried):
    print(f"  mang sang NGUYÊN TRẠNG dòng cũ của {len(carried)} mã bị BQ cắt lịch sử (cơ sở cũ):")
    print(carried.to_string(index=False))
if problems:
    for p_ in problems: print(f"  !! {p_}")
    print("  !! KHÔNG GHI earnings_px.pkl / lagged_pos_ov.pkl — giữ bản cũ")
    ADJ_FAIL.extend(problems)
else:
    for path in ("data/earnings_px.pkl", "data/lagged_pos_ov.pkl"):   # ảnh chụp 1 lần bản cơ sở-thô cuối
        full = os.path.join(WORKDIR, path)
        if not os.path.exists(full + ".pre_adj"): LCA.copy_atomic(full, full + ".pre_adj")
    _save_pickles([(npx, os.path.join(WORKDIR, "data/earnings_px.pkl")),
                   (nov, os.path.join(WORKDIR, "data/lagged_pos_ov.pkl"))])
    _save_json_atomic({"tickers": sorted(carried["ticker"]) if len(carried) else [], "asof": stats.get("asof"),
                       "end": str(_end.date())}, CARRY_STATE)
    px, ov = npx, nov
    print(f"  ghi: px {len(px):,} / ov {len(ov):,} rows, max {px['time'].max().date()}")


# ── 3. earnings_surprise_data.pkl — full re-pull (cheap, quarterly) ────────
print("\n[3] earnings_surprise_data.pkl (NP_P0..P7)...")
fin = bq("""SELECT f.ticker, f.quarter, f.time, f.Release_Date,
       f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
       f.NP_R, f.Revenue_YoY_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date IS NOT NULL AND f.Release_Date >= '2009-01-01' AND f.NP_P0 IS NOT NULL""")
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin["time"] = pd.to_datetime(fin["time"])
_save_pickle(fin, os.path.join(WORKDIR, "data/earnings_surprise_data.pkl"))
print(f"  re-pulled {len(fin):,} events, Release_Date max {fin['Release_Date'].max().date()}")


# ── 4. earnings_events_classified.csv — recompute from fresh px ────────────
print("\n[4] earnings_events_classified.csv (recompute pre/rel/post)...")
ev = bq("""SELECT f.ticker, f.quarter, f.Release_Date, f.NP_R, f.Revenue_YoY_P0, f.NP_P0, f.NP_P4
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date IS NOT NULL AND f.Release_Date >= '2009-01-01' AND f.NP_R IS NOT NULL""")
ev["Release_Date"] = pd.to_datetime(ev["Release_Date"])
_save_pickle(ev, os.path.join(WORKDIR, "data/earnings_events.pkl"))

px_piv = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
all_dates_arr = np.array(px_piv.index)

def close_offset(tk, ref_dt, off):
    if tk not in px_piv.columns: return np.nan
    pos = np.searchsorted(all_dates_arr, np.datetime64(ref_dt), side="right") - 1
    if pos < 0: return np.nan
    tgt = pos + off
    if tgt < 0 or tgt >= len(all_dates_arr): return np.nan
    return px_piv.iloc[tgt][tk]

def classify(npr, pre, rel, post):
    if pd.isna(npr): return "NO_NPR"
    good, bad = npr >= 15, npr <= -15
    if good:
        if pre >= 10 and rel <= -2: return "LEAK_RUNUP_POS"
        if abs(pre) < 5 and rel >= 3: return "EFFICIENT_POS"
        if abs(pre) < 5 and abs(rel) < 3 and post >= 5: return "LAGGED_POS"
        if pre >= 10 and rel >= 0 and post < 0: return "LEAK_RUNUP_POS"
    if bad:
        if pre <= -10 and rel >= 2: return "LEAK_DUMP_NEG"
        if abs(pre) < 5 and rel <= -3: return "EFFICIENT_NEG"
        if abs(pre) < 5 and abs(rel) < 3 and post <= -5: return "LAGGED_NEG"
    return "NOISE"

rows = []
for _, r in ev.iterrows():
    tk, rdt = r["ticker"], r["Release_Date"]
    if tk not in px_piv.columns: continue
    p_pre30 = close_offset(tk, rdt, -30); p_m1 = close_offset(tk, rdt, -1)
    p_p5 = close_offset(tk, rdt, +5);     p_p30 = close_offset(tk, rdt, +30)
    if any(pd.isna(p) for p in [p_pre30, p_m1, p_p5, p_p30]): continue
    if min(p_pre30, p_m1, p_p5, p_p30) <= 0: continue
    pre = (p_m1/p_pre30 - 1)*100; rel = (p_p5/p_m1 - 1)*100; post = (p_p30/p_p5 - 1)*100
    npr = r["NP_R"]*100 if pd.notna(r["NP_R"]) else np.nan
    rows.append({"ticker": tk, "quarter": r["quarter"], "Release_Date": rdt,
                 "NP_R": npr, "Rev_YoY": r["Revenue_YoY_P0"]*100 if pd.notna(r["Revenue_YoY_P0"]) else np.nan,
                 "pre_ret": pre, "rel_ret": rel, "post_ret": post,
                 "pattern": classify(npr, pre, rel, post)})
evdf = pd.DataFrame(rows)
out_csv = os.path.join(WORKDIR, "data/earnings_events_classified.csv")
def _save_csv_atomic(df, path):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=os.path.basename(path) + ".", suffix=".tmp")
    os.close(fd)
    try:
        df.to_csv(tmp, index=False); os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.remove(tmp)

try:
    _save_csv_atomic(evdf, out_csv)
except PermissionError:
    out_csv = out_csv.replace(".csv", ".new.csv"); _save_csv_atomic(evdf, out_csv)
    print(f"  (locked, wrote {out_csv})")
print(f"  recomputed {len(evdf):,} events with full windows, "
      f"Release_Date max {evdf['Release_Date'].max().date()}")

print("\n" + "=" * 80)
print("  REFRESH COMPLETE")
print(f"  earnings_px max:    {px['time'].max().date()}")
print(f"  lagged_pos_ov max:  {ov['time'].max().date()}")
print(f"  surprise rel max:   {fin['Release_Date'].max().date()}")
print(f"  events_cls rel max: {evdf['Release_Date'].max().date()}")
print("=" * 80)
if ADJ_FAIL:
    print("!! [1+2] KHÔNG cập nhật pkl giá: " + " | ".join(ADJ_FAIL))
    sys.exit(1)
