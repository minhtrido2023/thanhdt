# -*- coding: utf-8 -*-
"""Rate-limited, disk-cached 15m intraday fetcher for the EXTREME-regime backtest.

Guest vnstock limit = 20 req/min. We sleep ~3.5s between calls (≤17/min) and
persist every fetch to data/extreme_cache/*.parquet so the job is resumable —
re-running skips anything already on disk. Auditable: raw bars kept for recompute.
"""
import warnings; warnings.filterwarnings("ignore")
import io, time, os, sys
from contextlib import redirect_stdout
_buf = io.StringIO()
with redirect_stdout(_buf):
    from vnstock.api.quote import Quote
import pandas as pd

CACHE = "data/extreme_cache"
os.makedirs(CACHE, exist_ok=True)
SLEEP = 3.6  # ≤17 req/min, safe under the 20/min guest cap

# One 15m window per episode; keep them tight to minimise calls.
WIN = [("2024-04-10", "2024-04-17"), ("2024-08-01", "2024-08-07"),
       ("2025-04-01", "2025-04-14"), ("2025-07-25", "2025-07-31"),
       ("2025-10-15", "2025-10-22"), ("2026-03-05", "2026-03-12")]
NAMES = ["FPT", "MBB", "ACB", "HDB", "VCB", "CTG", "BID", "VPB", "HPG",
         "SSI", "VND", "MWG", "STB", "TCB", "GAS", "VNM", "VRE", "VHM"]


def _get(tk, s, e, interval, tag):
    fn = os.path.join(CACHE, f"{tk}_{tag}.parquet")
    if os.path.exists(fn):
        return pd.read_parquet(fn)
    q = Quote(symbol=tk, source="VCI")
    try:
        with redirect_stdout(_buf):
            df = q.history(start=s, end=e, interval=interval)
    except Exception as ex:
        if "Rate limit" in str(_buf.getvalue()[-400:]) or "rate" in str(ex).lower():
            print(f"  [{tk} {tag}] RATE-LIMIT — sleeping 60s"); time.sleep(60)
            return _get(tk, s, e, interval, tag)
        print(f"  [{tk} {tag}] ERR {repr(ex)[:80]}"); return None
    time.sleep(SLEEP)
    if df is None or len(df) == 0:
        return None
    df.to_parquet(fn)
    return df


def main():
    for tk in NAMES:
        # daily for prior-close reference (one call, wide window)
        _get(tk, "2024-04-01", "2026-03-12", "1D", "daily")
        for i, (s, e) in enumerate(WIN):
            _get(tk, s, e, "15m", f"w{i}")
        done = len([f for f in os.listdir(CACHE) if f.startswith(tk + "_")])
        print(f"{tk}: {done} files cached", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
