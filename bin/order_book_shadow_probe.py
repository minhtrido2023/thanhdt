#!/usr/bin/env python3
"""Health/evidence probe cho order-book execution shadow v1 (không gọi broker)."""
import csv
import datetime as dt
import glob
import json
import os
import statistics

WC_ROOT = os.environ.get("ORDER_BOOK_WC_ROOT", "/home/trido/thanhdt/WorkingClaude")
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
START = os.environ.get("ORDER_BOOK_START", "2026-08-18")
# Selfcheck/tickcheck fixtures dùng account tag "selfcheck-*"/"tickcheck-*" + plan_date sentinel
# "2099-01-01" (§23 convention) và ghi thẳng vào EXEC_DIR thật khi quên set ORDER_BOOK_TEST_SINK
# (bug xác nhận 2026-08-20: 12 file rác từ 6 selfcheck khác nhau). "2099-01-01" >= START luôn
# đúng nên lọc theo plan_date không chặn được — phải lọc theo account.
_TEST_ACCOUNT_PREFIXES = ("selfcheck-", "tickcheck-")


def parse_ts(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except (TypeError, ValueError):
        return None


def load_observations():
    out = []
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, "orderbook_shadow_*.jsonl"))):
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if str(row.get("account", "")).startswith(_TEST_ACCOUNT_PREFIXES):
                    continue
                if str(row.get("plan_date", "")) >= START:
                    out.append(row)
    # trace_id là khoá immutable; restart không được thổi phồng N.
    return list({r.get("trace_id"): r for r in out if r.get("trace_id")}.values())


def load_l2(dates):
    by_key = {}
    for date in sorted(dates):
        path = os.path.join(EXEC_DIR, f"dnse_raw_{date}.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("kind") != "quote_l2":
                    continue
                p = row.get("payload") or {}
                bids, offers = p.get("bids") or [], p.get("offers") or []
                if not bids or not offers:
                    continue
                try:
                    mid = (float(bids[0]["price"]) + float(offers[0]["price"])) / 2
                except (KeyError, TypeError, ValueError):
                    continue
                ts = parse_ts(p.get("captured_at") or row.get("ts"))
                if ts:
                    by_key.setdefault((row.get("account_label"), p.get("symbol")), []).append((ts, mid))
    for values in by_key.values():
        values.sort()
    return by_key


def load_fills(observations):
    wanted = {(r.get("account"), str(r.get("child_oid"))): r for r in observations}
    fills = {}
    for account, oid in wanted:
        date = wanted[(account, oid)].get("plan_date")
        path = os.path.join(EXEC_DIR, f"exec_{account}_{date}_journal.csv")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                key = (account, str(row.get("child_oid", "")))
                if row.get("event") == "FILL" and key in wanted and key not in fills:
                    fills[key] = row
    return fills


def median(values):
    return statistics.median(values) if values else None


def main():
    obs = load_observations()
    raw_files = glob.glob(os.path.join(EXEC_DIR, "dnse_raw_*.jsonl"))
    if not obs:
        print(f"order-book observations N=0 · valid=0 · sessions=0 · trial bắt đầu {START} · raw L2 files={len(raw_files)}")
        print("WATCH: chưa có child-order opportunity sau mốc start; không được diễn giải là policy không có giá trị.")
        return 0

    valid = [r for r in obs if r.get("snapshot_valid") is True]
    invalid = len(obs) - len(valid)
    policies = {k: 0 for k in ("KEEP", "REDUCE", "DEFER")}
    for row in obs:
        k = (row.get("shadow") or {}).get("recommendation")
        if k in policies:
            policies[k] += 1
    latencies = [r.get("latency_snapshot_to_order_ms") for r in valid
                 if isinstance(r.get("latency_snapshot_to_order_ms"), (int, float))]
    dates = {r.get("plan_date") for r in obs if r.get("plan_date")}
    l2 = load_l2(dates)
    fills = load_fills(obs)
    horizons = {1: [], 5: [], 15: []}
    covered = {1: 0, 5: 0, 15: 0}
    time_to_fill, slippage = [], []
    markout_eligible = 0
    for row in valid:
        fill = fills.get((row.get("account"), str(row.get("child_oid"))))
        if not fill:
            continue
        placed = parse_ts(row.get("recorded_at"))
        filled_at = parse_ts(fill.get("ts"))
        try:
            px = float(fill.get("price"))
            order_px = float((row.get("baseline") or {}).get("price"))
        except (TypeError, ValueError):
            continue
        side = row.get("side")
        if not placed or not filled_at or not px or not order_px:
            continue
        markout_eligible += 1
        time_to_fill.append(max(0, (filled_at - placed).total_seconds()))
        side_sign = 1 if side == "buy" else -1
        slippage.append(side_sign * (px - order_px) / order_px * 10_000)
        series = l2.get((row.get("account"), row.get("ticker")), [])
        for minute in horizons:
            target = filled_at + dt.timedelta(minutes=minute)
            hit = next(((t, m) for t, m in series if target <= t <= target + dt.timedelta(seconds=90)), None)
            if hit:
                # Dương = adverse: BUY xong giá giảm / SELL xong giá tăng.
                horizons[minute].append(side_sign * (px - hit[1]) / px * 10_000)
                covered[minute] += 1

    print(f"order-book observations N={len(obs)} · valid={len(valid)} · sessions={len(dates)}")
    print("policy KEEP={KEEP} REDUCE={REDUCE} DEFER={DEFER}".format(**policies))
    print(f"latency snapshot→order median={median(latencies) if latencies else 'n/a'}ms")
    print(f"fill-linked children={len(fills)}/{len(obs)} · fill-rate={len(fills)/len(obs):.1%}")
    print(f"time-to-first-fill median={median(time_to_fill) if time_to_fill else 'n/a'}s · "
          f"fill-vs-limit slippage median={median(slippage) if slippage else 'n/a'}bps")
    print("outcome coverage " + " · ".join(f"{m}m={covered[m]}/{markout_eligible}" for m in (1, 5, 15)))
    vals = [f"{m}m={median(horizons[m]):+.1f}bps" for m in (1, 5, 15) if horizons[m]]
    print("adverse-selection median " + (" · ".join(vals) if vals else "n/a — chưa đủ snapshot hậu kiểm"))
    if invalid:
        print(f"ERROR telemetry: {invalid}")
    else:
        print("telemetry schema/freshness: PASS")
    print("scope v1: spread + displayed depth + adverse selection; resilience EXCLUDED (60s cadence).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
