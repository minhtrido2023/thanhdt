#!/usr/bin/env python3
"""verify_account_snapshot.py --account SpaceX --date YYYY-MM-DD

Tính NAV/vị thế/giá vốn THẬT cho báo cáo — nguồn duy nhất được phép dùng để viết
báo cáo trading (ngày/tuần/tháng). KHÔNG được đọc trực tiếp các field avg_cost/*
trong eod_account_*.json hay bất kỳ file tóm tắt trung gian nào khác cho mục đích
tính lãi/lỗ — những field đó có thể chỉ là giá tham chiếu ước tính (ref_px_approx),
không phải giá khớp thật.

Nguồn sự thật (ưu tiên theo thứ tự):
  1. data/execution_logs/dnse_raw_{date}.jsonl — log thô từ API broker (authoritative:
     averagePrice + fillQuantity do chính DNSE trả về). Dùng để tính giá vốn bình quân
     gia quyền THẬT cho từng mã, dedupe theo order id (giữ bản ghi mới nhất).
  2. data/execution_logs/exec_{account}_{date}_journal.csv — journal FILL event nội bộ,
     dùng làm cross-check độc lập với (1). Nếu 2 nguồn lệch vượt ngưỡng -> cảnh báo,
     KHÔNG âm thầm chọn một bên.
  3. BigQuery tav2_bq.ticker — giá đóng cửa thị trường mới nhất, dùng để mark-to-market.

Fail-safe: nếu số lượng cổ phiếu tính từ dnse_raw không khớp broker-audited quantities
(khi có file eod_account_{date}.json để đối chiếu), hoặc không tìm thấy dữ liệu nguồn,
script THOÁT với exit != 0 và in cảnh báo rõ ràng — không tự đoán số liệu để báo cáo tiếp.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from collections import defaultdict

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
BQ_PATH_PREFIX = "/home/trido/google-cloud-sdk/bin"


def true_fills_from_dnse_raw(account_no, date):
    """Trả về {ticker: (net_qty, buy_qty, buy_value)} từ log thô broker cho 1 ngày.

    net_qty = buy_qty - sell_qty (KL thật đang nắm giữ, để đối chiếu snapshot broker).
    buy_qty/buy_value CHỈ tính từ lệnh MUA — giá vốn bình quân gia quyền không đổi khi
    bán bớt (weighted-average costing chuẩn kế toán), nên KHÔNG được trộn giá bán vào.
    Bug 2026-07-06 (kb/INCIDENTS.md): bản cũ cộng dồn fillQuantity bất kể side, nên ngày
    có lệnh BÁN (trim 07-06) bị CỘNG thêm thay vì TRỪ, gây báo lệch số lượng giả.
    """
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date}.jsonl")
    if not os.path.exists(path):
        return None, f"missing dnse_raw_{date}.jsonl"
    latest_by_id = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            orders = []
            if rec.get("kind") == "orders":
                orders = rec.get("payload", {}).get("orders") or []
            elif rec.get("kind") == "place_order":
                r = rec.get("payload", {}).get("resp") or {}
                if r.get("id") is not None:
                    orders = [r]
            for o in orders:
                oid = o.get("id")
                if oid is None:
                    continue
                if account_no and o.get("accountNo") not in (None, account_no):
                    continue
                latest_by_id[oid] = o  # ghi đè -> bản ghi mới nhất mỗi order id

    agg = defaultdict(lambda: [0.0, 0.0, 0.0])  # ticker -> [net_qty, buy_qty, buy_value]
    for o in latest_by_id.values():
        fq = o.get("fillQuantity") or 0
        if fq <= 0:
            continue
        sym = o.get("symbol")
        px = o.get("averagePrice") or o.get("price") or 0
        side = str(o.get("side") or "").upper()
        if side.startswith("NS") or side == "SELL":
            agg[sym][0] -= fq
        else:  # NB (Normal Buy) hoặc side khác chưa gặp -> mặc định coi là mua
            agg[sym][0] += fq
            agg[sym][1] += fq
            agg[sym][2] += fq * px
    return {tk: tuple(v) for tk, v in agg.items()}, None


def true_fills_from_journal(account, date):
    """Cross-check độc lập từ journal CSV nội bộ (event=FILL). Cùng nguyên tắc net_qty
    (buy trừ sell) + cost basis chỉ từ buy như true_fills_from_dnse_raw() ở trên.

    QUAN TRỌNG: Executor._sync_fills ghi `qty` = c["filled"] LŨY KẾ của child order tại
    thời điểm đó (executor.py dòng ~386), KHÔNG PHẢI phần fill tăng thêm — 1 child có thể
    xuất hiện nhiều dòng FILL khi khớp từng phần (vd 600 rồi 2100 lũy kế, không phải 600+2100).
    Cộng dồn hết mọi dòng sẽ đếm trùng. Bug 2026-07-06 (kb/INCIDENTS.md): HDB báo lệch vì
    cộng cả dòng lũy kế trung gian lẫn dòng cuối. Fix: chỉ giữ dòng CUỐI (theo ts) mỗi
    child_oid, rồi mới cộng qua các child_oid khác nhau — giống hệt cách
    true_fills_from_dnse_raw() dùng latest_by_id cho cùng lý do.
    """
    path = os.path.join(EXEC_DIR, f"exec_{account}_{date}_journal.csv")
    if not os.path.exists(path):
        return None, f"missing exec_{account}_{date}_journal.csv"
    import csv
    latest_by_child = {}  # child_oid -> (ts, ticker, side, cumulative_qty, price)
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "FILL":
                continue
            child_oid = row.get("child_oid")
            ts = row.get("ts", "")
            prev = latest_by_child.get(child_oid)
            if prev is None or ts >= prev[0]:
                latest_by_child[child_oid] = (
                    ts, row.get("ticker"), str(row.get("side") or "").lower(),
                    float(row.get("qty") or 0), float(row.get("price") or 0))

    agg = defaultdict(lambda: [0.0, 0.0, 0.0])  # ticker -> [net_qty, buy_qty, buy_value]
    for _, tk, side, qty, price in latest_by_child.values():
        if side == "sell":
            agg[tk][0] -= qty
        else:
            agg[tk][0] += qty
            agg[tk][1] += qty
            agg[tk][2] += qty * price
    return {tk: tuple(v) for tk, v in agg.items()}, None


def bq_close_prices(tickers, as_of_date):
    env = dict(os.environ)
    env["PATH"] = BQ_PATH_PREFIX + ":" + env.get("PATH", "")
    tick_list = ",".join(f"'{t}'" for t in sorted(tickers))
    sql = f"""
    SELECT t.ticker, t.Close
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ({tick_list})
    AND t.time = (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2
                  WHERE t2.ticker = '{sorted(tickers)[0]}' AND t2.time <= '{as_of_date}')
    """
    cmd = ["bq", "query", "--use_legacy_sql=false",
           "--project_id=lithe-record-440915-m9", "--format=json",
           "--max_rows=5000", sql]
    out = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if out.returncode != 0:
        return None, out.stderr.strip()
    rows = json.loads(out.stdout)
    return {r["ticker"]: float(r["Close"]) for r in rows}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--account-no", default=None,
                     help="broker account number to filter dnse_raw orders (recommended)")
    ap.add_argument("--dates", required=True,
                     help="comma-separated trading dates with fills, e.g. 2026-07-01,2026-07-02")
    ap.add_argument("--asof", required=True, help="mark-to-market date (BQ close price)")
    ap.add_argument("--broker-snapshot", default=None,
                     help="optional eod_account_{date}.json path to cross-check quantities")
    ap.add_argument("--out", default=None)
    ap.add_argument("--tolerance-pct", type=float, default=0.5,
                     help="max %% diff allowed between dnse_raw and journal cost basis before warning")
    args = ap.parse_args()

    dates = [d.strip() for d in args.dates.split(",") if d.strip()]
    warnings = []

    raw_agg = defaultdict(lambda: [0.0, 0.0, 0.0])      # ticker -> [net_qty, buy_qty, buy_value]
    journal_agg = defaultdict(lambda: [0.0, 0.0, 0.0])
    for date in dates:
        raw, err = true_fills_from_dnse_raw(args.account_no, date)
        if raw is None:
            warnings.append(f"FATAL: {err} — không có nguồn broker thật cho {date}")
            continue
        for tk, (nq, bq, bv) in raw.items():
            raw_agg[tk][0] += nq
            raw_agg[tk][1] += bq
            raw_agg[tk][2] += bv

        jr, jerr = true_fills_from_journal(args.account, date)
        if jr is None:
            warnings.append(f"WARN: {jerr} — bỏ qua cross-check journal cho {date}")
        else:
            for tk, (nq, bq, bv) in jr.items():
                journal_agg[tk][0] += nq
                journal_agg[tk][1] += bq
                journal_agg[tk][2] += bv

    if any(w.startswith("FATAL") for w in warnings):
        print("XÁC MINH THẤT BẠI — không đủ dữ liệu nguồn broker thật:", file=sys.stderr)
        for w in warnings:
            print(" -", w, file=sys.stderr)
        sys.exit(2)

    # cross-check dnse_raw vs journal (2 nguồn độc lập) — so KL NET (mua-bán), giá vốn chỉ từ mua
    for tk in set(raw_agg) | set(journal_agg):
        rq, rbq, rbv = raw_agg.get(tk, (0, 0, 0))
        jq, jbq, jbv = journal_agg.get(tk, (0, 0, 0))
        if rq == 0 and jq == 0:
            continue
        if abs(rq - jq) > 1e-6:
            warnings.append(f"WARN qty mismatch {tk}: dnse_raw={rq:.0f} journal={jq:.0f}")
        r_avg = rbv / rbq if rbq else 0
        j_avg = jbv / jbq if jbq else 0
        if r_avg and j_avg:
            diff_pct = abs(r_avg - j_avg) / r_avg * 100
            if diff_pct > args.tolerance_pct:
                warnings.append(
                    f"WARN cost mismatch {tk}: dnse_raw_avg={r_avg:,.0f} "
                    f"journal_avg={j_avg:,.0f} (diff {diff_pct:.2f}%%)")

    # cross-check quantities vs an independently-audited broker snapshot, if given
    if args.broker_snapshot and os.path.exists(args.broker_snapshot):
        snap = json.load(open(args.broker_snapshot, encoding="utf-8"))
        snap_qty = {p["ticker"]: p["qty"] for p in snap.get("positions", [])}
        for tk, q in snap_qty.items():
            rq = raw_agg.get(tk, (0, 0, 0))[0]
            if abs(rq - q) > 1e-6:
                warnings.append(
                    f"WARN qty vs broker-snapshot {tk}: dnse_raw={rq:.0f} snapshot={q:.0f}")

    tickers = sorted(raw_agg.keys())
    prices, perr = bq_close_prices(tickers, args.asof)
    if prices is None:
        print(f"XÁC MINH THẤT BẠI — không lấy được giá BQ: {perr}", file=sys.stderr)
        sys.exit(3)

    positions = []
    total_cost = total_mtm = 0.0
    for tk in tickers:
        qty, buy_qty, buy_val = raw_agg[tk]
        if qty <= 0:
            continue  # đã bán hết (net_qty<=0) -> không còn nắm giữ, bỏ khỏi báo cáo vị thế
        cost = buy_val / buy_qty if buy_qty else 0  # giá vốn bình quân CHỈ từ lệnh mua
        px = prices.get(tk)
        if px is None:
            warnings.append(f"WARN no BQ price for {tk} as of {args.asof}")
            continue
        cv, mv = qty * cost, qty * px
        total_cost += cv
        total_mtm += mv
        positions.append({"ticker": tk, "qty": qty, "true_avg_cost": round(cost, 1),
                           "mtm_price": px, "cost_value": cv, "mtm_value": mv,
                           "unrealized_pnl": mv - cv,
                           "unrealized_pnl_pct": (mv - cv) / cv * 100 if cv else 0})

    result = {
        "account": args.account,
        "dates_included": dates,
        "asof": args.asof,
        "source": "dnse_raw (broker-native averagePrice/fillQuantity), cross-checked vs journal FILL events",
        "verified": not any(w.startswith("WARN qty") for w in warnings),
        "warnings": warnings,
        "positions": sorted(positions, key=lambda p: -p["unrealized_pnl"]),
        "total_cost_value": total_cost,
        "total_mtm_value": total_mtm,
        "total_unrealized_pnl": total_mtm - total_cost,
    }

    out_path = args.out or os.path.join(
        EXEC_DIR, f"verified_snapshot_{args.account}_{args.asof}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"== Verified snapshot: {args.account} as of {args.asof} ==")
    print(f"Nguồn: {result['source']}")
    print(f"Verified (không có lệch số lượng giữa broker vs journal): {result['verified']}")
    if warnings:
        print(f"\n⚠️  {len(warnings)} cảnh báo:")
        for w in warnings:
            print(" -", w)
    print()
    for p in result["positions"]:
        print(f"{p['ticker']:6s} qty={p['qty']:7.0f} true_cost={p['true_avg_cost']:>10,.0f} "
              f"mtm_px={p['mtm_price']:>9,.0f} PnL={p['unrealized_pnl']:>+14,.0f} "
              f"({p['unrealized_pnl_pct']:+.2f}%)")
    print()
    print(f"TOTAL cost basis (true): {total_cost:>16,.0f}")
    print(f"TOTAL mark-to-market:    {total_mtm:>16,.0f}")
    print(f"Unrealized P&L:          {total_mtm-total_cost:>+16,.0f}")
    print(f"\nGhi ra: {out_path}")

    if not result["verified"]:
        print("\n❌ CÓ LỆCH SỐ LƯỢNG GIỮA 2 NGUỒN ĐỘC LẬP — KHÔNG dùng số liệu này để viết báo cáo "
              "cho đến khi điều tra rõ nguyên nhân.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
