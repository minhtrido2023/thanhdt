#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "order_book_shadow_probe.py")


def run(root):
    env = dict(os.environ, ORDER_BOOK_WC_ROOT=root, ORDER_BOOK_START="2026-08-18")
    return subprocess.run(["python3", PROBE], env=env, text=True, capture_output=True, check=True).stdout


with tempfile.TemporaryDirectory() as root:
    ex = os.path.join(root, "data", "execution_logs")
    os.makedirs(ex)
    out = run(root)
    assert "N=0" in out and "WATCH" in out
    obs = {
        "schema_version": "orderbook_execution_v1", "trace_id": "A:P:C", "account": "A",
        "plan_date": "2026-08-18", "child_oid": "C", "ticker": "AAA", "side": "buy",
        "recorded_at": "2026-08-18T09:15:01", "snapshot_valid": True,
        "latency_snapshot_to_order_ms": 120, "baseline": {"price": 10000},
        "shadow": {"recommendation": "KEEP"},
    }
    with open(os.path.join(ex, "orderbook_shadow_A_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obs) + "\n")
    with open(os.path.join(ex, "exec_A_2026-08-18_journal.csv"), "w", encoding="utf-8") as fh:
        fh.write("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
        fh.write("2026-08-18T09:15:30,FILL,P,AAA,buy,C,100,10000,100,CAPIT,,\n")
    with open(os.path.join(ex, "dnse_raw_2026-08-18.jsonl"), "w", encoding="utf-8") as fh:
        for minute, mid in ((2, 9900), (6, 10100), (16, 9800)):
            row = {"ts": f"2026-08-18T09:{15+minute:02d}:01", "kind": "quote_l2",
                   "account_label": "A", "payload": {"symbol": "AAA",
                   "bids": [{"price": mid-50}], "offers": [{"price": mid+50}]}}
            fh.write(json.dumps(row) + "\n")
    out = run(root)
    assert "N=1" in out and "valid=1" in out and "fill-linked children=1/1" in out
    assert "1m=1/1" in out and "5m=1/1" in out and "15m=1/1" in out
    assert "telemetry schema/freshness: PASS" in out
print("order_book_shadow_probe_selfcheck: PASS (2 scenarios)")
