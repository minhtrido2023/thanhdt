#!/usr/bin/env python3
"""Health/evidence probe cho order-book execution shadow v1 (không gọi broker).

⚠️ BẪY ĐÃ CẮN — `load_l2()` MỘT MÌNH KHÔNG PHỦ ĐƯỢC MẪU (vá 2026-09-23)
-----------------------------------------------------------------------
Checkpoint 09-23 báo "hậu kiểm 1/5/15′ coverage ~1,6%" và cả hai bên đọc đó là THIẾU MẪU
(⇒ gia hạn thêm phiên). SAI. Đếm lại theo từng nguyên nhân: 259/265 quan sát đủ điều kiện
markout rơi vào nhánh `no_l2_series_for_(account,ticker)` — tức KHÔNG CÓ chuỗi giá nào để
so, chứ không phải chuỗi có mà thiếu điểm.

Gốc cơ học: 91% mẫu là `account=main`, mà `main` chạy **`broker: "phs"`**
(`secrets/trading_bot_accounts.json`). `PHSBroker.get_quote()` DỰNG `l2_snapshot` bằng
`_phs_l2_snapshot()` nhưng **không bao giờ gọi `_log_raw("quote_l2", …)`** — chỉ
`DNSEBroker._log_l2()` mới ghi. Bản ghi `quote_l2` cuối cùng có `account_label="main"` là
**2026-08-17**, tức TRƯỚC ngày trial bắt đầu (08-18). Thêm bao nhiêu phiên cũng không sinh
thêm một điểm markout nào cho nhánh này.

Chuỗi giá CỦA CHÍNH `main` thì vẫn có trên đĩa, chỉ nằm ở file khác:
`probe_ticks_<account>_<date>.csv` (`Executor._probe_tick_log`, ghi mỗi `px_sample_sec`=60s
và sống thêm `probe_linger_min`=30′ sau khi mọi parent đã khớp — đúng bằng cửa sổ 1/5/15′).
Đọc thêm nguồn này: coverage 1m/5m/15m = **1,5%/1,5%/0,8% → 91,7%/91,7%/81,5%** trên ĐÚNG
mẫu 22 phiên đã có, không cần thu thêm ngày nào.

⚠️ HAI CƠ SỞ GIÁ KHÁC NHAU, KHÔNG ĐƯỢC TRỘN IM LẶNG: `dnse_raw` cho **mid** (bid/ask),
`probe_ticks` cho **last** (giá khớp gần nhất). Markout tính trên hai cơ sở này không so
trực tiếp được — nên mỗi quan sát ghi kèm `basis` và báo cáo tách theo basis.

⚠️ TÁCH TẦNG PROBE vs REAL: gộp chung là lý do cả checkpoint đọc nhầm lần hai. Xem `main()`.
"""
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


def load_ticks(dates):
    """Chuỗi giá `last` theo (account, ticker) từ `probe_ticks_<account>_<date>.csv`.

    NGUỒN THỨ HAI cho markout, KHÔNG thay thế `load_l2()`: nó chỉ có `last`, không có
    bid/ask ⇒ không dựng được mid. Dùng làm fallback khi (account, ticker) không có chuỗi
    L2 nào — xem docstring đầu file. Lọc account test giống `load_observations()`.
    """
    by_key = {}
    for date in sorted(dates):
        for path in sorted(glob.glob(os.path.join(EXEC_DIR, f"probe_ticks_*_{date}.csv"))):
            with open(path, encoding="utf-8", errors="replace") as fh:
                for row in csv.DictReader(fh):
                    account = row.get("account")
                    if not account or str(account).startswith(_TEST_ACCOUNT_PREFIXES):
                        continue
                    ts = parse_ts(row.get("ts"))
                    try:
                        px = float(row.get("last") or 0) or None
                    except (TypeError, ValueError):
                        px = None
                    if ts and px:
                        by_key.setdefault((account, row.get("ticker")), []).append((ts, px))
    for values in by_key.values():
        values.sort()
    return by_key


def markout_series(l2, ticks, account, ticker):
    """Trả (chuỗi, basis). Ưu tiên mid của L2; rơi về `last` của probe_ticks nếu không có.

    KHÔNG ghép hai nguồn vào một chuỗi: một quan sát phải được markout trọn vẹn trên MỘT
    cơ sở giá, nếu không `(px_fill − px_sau)` trộn mid với last và con số bps mất nghĩa.
    """
    series = l2.get((account, ticker)) or []
    if series:
        return series, "mid"
    return (ticks.get((account, ticker)) or []), "last"


def stratum(account):
    """PROBE = harness churn tổng hợp (`main`); REAL = lệnh tài khoản thật.

    Gộp hai tầng này là cách checkpoint 09-23 đọc ra "policy gần như không bao giờ lệch
    baseline": 289/298 quan sát hợp lệ là lệnh 100 CP trên 6 mã vốn hoá lớn nhất, nơi
    `touch_depth_ratio` TRUNG VỊ là **763×** — sổ dày gấp 763 lần lệnh. Một policy
    spread+depth KHÔNG THỂ có gì để phân biệt ở đó, và điều đó KHÔNG nói gì về giá trị của
    nó trên lệnh thật (cùng phép đo, tầng REAL: trung vị **2,2×**, p25 **1,3×**).
    """
    return "PROBE" if account == "main" else "REAL"


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
    dates = {r.get("plan_date") for r in obs if r.get("plan_date")}
    l2 = load_l2(dates)
    ticks = load_ticks(dates)
    fills = load_fills(obs)

    # Mọi số tách theo tầng (xem `stratum()`): gộp chung là lỗi đọc của checkpoint 09-23.
    by_stratum = {"PROBE": [], "REAL": []}
    for row in obs:
        by_stratum[stratum(row.get("account"))].append(row)

    latencies = [r.get("latency_snapshot_to_order_ms") for r in valid
                 if isinstance(r.get("latency_snapshot_to_order_ms"), (int, float))]

    horizons = {1: [], 5: [], 15: []}
    covered = {1: 0, 5: 0, 15: 0}
    basis_count = {"mid": 0, "last": 0, "none": 0}
    time_to_fill, slippage = [], []
    markout_eligible = 0
    markout_records = []
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
        series, basis = markout_series(l2, ticks, row.get("account"), row.get("ticker"))
        basis_count[basis if series else "none"] += 1
        marks = {}
        for minute in horizons:
            target = filled_at + dt.timedelta(minutes=minute)
            hit = next(((t, m) for t, m in series if target <= t <= target + dt.timedelta(seconds=90)), None)
            if hit:
                # Dương = adverse: BUY xong giá giảm / SELL xong giá tăng.
                bps = side_sign * (px - hit[1]) / px * 10_000
                horizons[minute].append(bps)
                covered[minute] += 1
                marks[f"markout_{minute}m_bps"] = round(bps, 3)
            else:
                marks[f"markout_{minute}m_bps"] = None
        # Trường hậu kiểm dựng OFFLINE và ghi ra artifact RIÊNG (`orderbook_markout_v1`),
        # nối với quan sát bằng `trace_id`. Không sửa bản ghi `orderbook_execution_v1` đã
        # nằm trên đĩa: nó là bằng chứng immutable của thời điểm đặt lệnh, và 321 bản ghi
        # đã thu theo schema đó phải giữ nguyên để còn so được.
        markout_records.append({
            "schema_version": "orderbook_markout_v1",
            "trace_id": row.get("trace_id"), "account": row.get("account"),
            "stratum": stratum(row.get("account")), "plan_date": row.get("plan_date"),
            "ticker": row.get("ticker"), "side": side,
            "fill_ts": fill.get("ts"), "fill_price": px,
            "slippage_vs_limit_bps": round(side_sign * (px - order_px) / order_px * 10_000, 3),
            "time_to_fill_sec": round(max(0, (filled_at - placed).total_seconds()), 3),
            "markout_basis": basis if series else "none",
            "policy_version": row.get("policy_version"),
            "recommendation": (row.get("shadow") or {}).get("recommendation"),
            **marks,
        })

    out_path = os.path.join(EXEC_DIR, "orderbook_markout.jsonl")
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for rec in markout_records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, out_path)

    print(f"order-book observations N={len(obs)} · valid={len(valid)} · sessions={len(dates)}")
    for name in ("PROBE", "REAL"):
        rows = by_stratum[name]
        pol = {k: 0 for k in ("KEEP", "REDUCE", "DEFER")}
        for row in rows:
            k = (row.get("shadow") or {}).get("recommendation")
            if k in pol:
                pol[k] += 1
        n = len(rows)
        off = (pol["REDUCE"] + pol["DEFER"]) / n if n else 0
        depths = sorted(r["features"]["touch_depth_ratio"] for r in rows
                        if (r.get("features") or {}).get("touch_depth_ratio") is not None)
        dmed = f"{median(depths):.1f}x" if depths else "n/a"
        print(f"  [{name}] N={n} · policy KEEP={pol['KEEP']} REDUCE={pol['REDUCE']} "
              f"DEFER={pol['DEFER']} · khác-baseline={off:.1%} · touch_depth_ratio median={dmed}")
    print(f"latency snapshot→order median={median(latencies) if latencies else 'n/a'}ms")
    print(f"fill-linked children={len(fills)}/{len(obs)} · fill-rate={len(fills)/len(obs):.1%}")
    print(f"time-to-first-fill median={median(time_to_fill) if time_to_fill else 'n/a'}s · "
          f"fill-vs-limit slippage median={median(slippage) if slippage else 'n/a'}bps")
    print("outcome coverage " + " · ".join(f"{m}m={covered[m]}/{markout_eligible}" for m in (1, 5, 15))
          + f" · basis mid={basis_count['mid']} last={basis_count['last']} none={basis_count['none']}")
    vals = [f"{m}m={median(horizons[m]):+.1f}bps" for m in (1, 5, 15) if horizons[m]]
    print("adverse-selection median " + (" · ".join(vals) if vals else "n/a — chưa đủ snapshot hậu kiểm"))
    print(f"markout artifact: {out_path} ({len(markout_records)} bản ghi, schema orderbook_markout_v1)")
    if invalid:
        print(f"ERROR telemetry: {invalid}")
    else:
        print("telemetry schema/freshness: PASS")
    print("scope v1: spread + displayed depth + adverse selection; resilience EXCLUDED (60s cadence).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
