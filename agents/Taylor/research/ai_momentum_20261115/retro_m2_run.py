#!/usr/bin/env python3
"""Chay THAT 1 lan retro 2 su kien qua M1 -> M2 blind -> M2 challenge (ledger retro rieng, KHONG forward). Do thoi gian/m2_status/flip."""
import sys, time, json, os; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import ai_momentum_daily as m
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
EVENTS = [("HID", "2026-09-17"), ("DXP", "2026-10-12")]
real = m.BQ; t0 = time.time(); stamps = {}
for tk, T in EVENTS:
    def bq(sql, tk=tk):
        r = real(sql)
        return [x for x in r if x.get("ticker") == tk] if "PERCENTILE_CONT" in sql else r
    m.BQ = bq; s = time.time()
    print(json.dumps(m.run_day(T, "retro", str(OUT), seed={}, ff=m.load_ff()), ensure_ascii=False), flush=True)
    stamps[f"{tk}_{T}"] = round(time.time() - s, 1)
print("SECONDS", json.dumps(stamps), "total", round(time.time() - t0, 1))
