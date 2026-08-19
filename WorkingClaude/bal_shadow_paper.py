#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bal_shadow_paper.py — SHADOW paper-track cho tín hiệu BAL bị user HOLD (bắt đầu VPI, 2026-08-19).

BỐI CẢNH (không lặp lại chỗ khác): user quyết định 2026-08-19 (Discord topic 1521183164364754974)
CHƯA mua thật tín hiệu BAL (case VPI) vì (1) chỉ số kỹ thuật thị trường chưa tốt, (2) hiệu suất
GẦN ĐÂY của book BAL cần quan sát thêm. Kiểm tra ARTIFACT (job Taylor_20260819_124845) cho thấy:
  - Account paper `main` KHÔNG chạy chiến lược V2.4 thật — nó là harness bằng chứng tổng hợp
    (`mike/bin/paper_main_probe_plan.py`, basket cố định 6 mã churn mỗi phiên) cho 3 chương trình
    khác (extreme_regime/fill_timing/vol_scale_chase_cap), KHÔNG liên quan BAL.
  - BAL book trên CẢ 2 account live (SpaceX/ZaloPay) hiện RỖNG (0 vị thế, xem
    `bal_analysis.note` trong plan JSON 2026-08-20: "BAL book hiện tại đang RỖNG").
  ⇒ KHÔNG có track paper/live nào sẵn có để đo lại hiệu suất BAL gần đây — phải dựng MỚI, đi
  TỚI (shadow những tín hiệu BAL bị hold từ nay), không phải hồi cứu (không có dữ liệu để hồi cứu).

CƠ CHẾ: mỗi lần chạy --update, đọc rec CSV mới nhất trong deploy_golive_dt5g_v4/out/ (nguồn DUY
NHẤT dùng cho plan thật), lấy các dòng book==BAL status FULL/HALF_SIZE mà book đang RỖNG (tín hiệu
"mở mới" — đúng loại tín hiệu VPI thuộc về, KHÔNG phải mọi dòng BAL — mirror vị thế paper cũ nếu
sau này book không còn rỗng thì cần mở rộng, hiện tại chưa cần vì rỗng), ghi thêm dòng MỚI vào
ledger nếu ticker CHƯA có trong ledger (dedupe theo ticker, không log lại tín hiệu cũ mỗi ngày).
Entry price = BQ Close ngày signal (đúng quy ước MTM proxy đã dùng ở dc_book_waterfall_paper.py —
đây là SHADOW/nghiên cứu, KHÔNG phải lệnh thật, không cần giá DNSE live theo §6 CLAUDE.md).
MTM mỗi lần chạy = Close mới nhất so với entry.

State: data/bal_shadow_paper.csv (append-only ledger, cột: entry_date,ticker,entry_close,
signal_date,status_snapshot). KHÔNG chạm production plan/executor/BAL book thật.

Usage:
  python3 bal_shadow_paper.py --update     # quét rec CSV mới nhất, ghi entry mới nếu có
  python3 bal_shadow_paper.py --section    # update-if-needed rồi in báo cáo markdown
"""
import argparse
import csv
import glob
import os
import sys

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
LEDGER = os.path.join(WC_ROOT, "data", "bal_shadow_paper.csv")
REC_GLOB = os.path.join(WC_ROOT, "deploy_golive_dt5g_v4", "out", "golive_v23_recommendations_*.csv")
BQ_CACHE = os.path.join(WC_ROOT, "data", "bq_cache")
FIELDS = ["entry_date", "ticker", "entry_close", "signal_date", "status_snapshot"]


def latest_rec_csv():
    files = sorted(glob.glob(REC_GLOB))
    return files[-1] if files else None


def load_ledger():
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_ledger(rows):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    os.replace(tmp, LEDGER)


def latest_closes(tickers):
    """{ticker: (Close, time)} — dùng chung quy ước BQ cache parquet với dc_book_waterfall_paper.py."""
    if not tickers:
        return {}
    try:
        import duckdb
        con = duckdb.connect()
        con.execute("SET threads=1")
        q = ",".join(f"'{t}'" for t in sorted(set(tickers)))
        df = con.execute(f"""
            WITH r AS (SELECT ticker, time, Close,
                       ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn
                       FROM read_parquet('{BQ_CACHE}/ticker/*.parquet')
                       WHERE ticker IN ({q}))
            SELECT ticker, time, Close FROM r WHERE rn=1""").df()
        con.close()
        return {str(r["ticker"]): (float(r["Close"]), str(r["time"])) for _, r in df.iterrows()}
    except Exception as exc:                                          # noqa: BLE001
        print(f"[bal-shadow] ⚠️ latest_closes lỗi: {type(exc).__name__}: {exc}")
        return {}


def update():
    path = latest_rec_csv()
    if not path:
        print("[bal-shadow] không tìm thấy recommendations CSV nào — bỏ qua")
        return
    signal_date = os.path.basename(path).replace("golive_v23_recommendations_", "").replace(".csv", "")
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if r.get("book") == "BAL" and r.get("status") in ("FULL", "HALF_SIZE")]
    ledger = load_ledger()
    have = {r["ticker"] for r in ledger}
    px = latest_closes([r["ticker"] for r in rows if r["ticker"] not in have])
    added = []
    for r in rows:
        t = r["ticker"]
        if t in have:
            continue
        close_px, close_date = px.get(t, (None, None))
        if close_px is None:
            continue
        ledger.append({
            "entry_date": signal_date, "ticker": t, "entry_close": close_px,
            "signal_date": signal_date, "status_snapshot": r.get("status", ""),
        })
        added.append(t)
    if added:
        save_ledger(ledger)
        print(f"[bal-shadow] thêm {len(added)} entry mới: {added} (nguồn {os.path.basename(path)})")
    else:
        print(f"[bal-shadow] không có entry mới (đã có: {sorted(have)})")


def section():
    update()
    ledger = load_ledger()
    if not ledger:
        return "### BAL shadow-track (paper, ĐI TỚI — VPI trở đi)\n- Chưa có entry nào."
    px = latest_closes([r["ticker"] for r in ledger])
    lines = ["### BAL shadow-track (paper, ĐI TỚI — VPI trở đi)",
             f"- {len(ledger)} entry shadow tích lũy:"]
    rets = []
    for r in ledger:
        t = r["ticker"]
        entry = float(r["entry_close"])
        cur, cur_date = px.get(t, (None, None))
        if cur is None:
            lines.append(f"  - {t}: entry {entry:,.0f} ({r['entry_date']}) — giá hiện tại không đọc được")
            continue
        ret = cur / entry - 1
        rets.append(ret)
        lines.append(f"  - {t}: entry {entry:,.0f} ({r['entry_date']}) → {cur:,.0f} ({cur_date[:10]}) = {ret:+.2%}")
    if rets:
        lines.append(f"- Bình quân {sum(rets)/len(rets):+.2%}, {sum(1 for x in rets if x>0)}/{len(rets)} dương.")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--section", action="store_true")
    args = ap.parse_args()
    if args.section:
        print(section())
    elif args.update:
        update()
    else:
        ap.print_help()
        sys.exit(1)
