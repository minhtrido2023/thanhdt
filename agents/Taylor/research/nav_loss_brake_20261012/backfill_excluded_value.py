#!/usr/bin/env python3
"""Dựng lại MỘT LẦN chuỗi giá trị mã loại trừ cho các ngày đã qua (monitor chỉ ghi được từ nay:
active_nav_{account}.json bị ghi đè mỗi tối nên giá đóng cửa của ngày cũ không còn trên đĩa).

KL: bản ghi positions cuối ngày của broker (dnse_raw_{date}.jsonl, lọc account) — cùng hàm monitor
dùng. Giá: `tav2_bq.ticker.Price` (giá đóng cửa CHƯA điều chỉnh) trong file CSV truyền vào — truy
vấn lịch sử, lấy bằng:
  bq query --use_legacy_sql=false --format=csv --max_rows=500 'SELECT t.time, t.ticker, t.Price,
    t.Close FROM tav2_bq.ticker AS t WHERE t.time BETWEEN "2026-07-06" AND "2026-10-09"
    AND t.ticker = "DGC" ORDER BY t.time'
Ngày KHÔNG phải phiên giao dịch mà nav_history vẫn có dòng (vd 2026-08-31, nghỉ lễ): dùng giá
đóng cửa của phiên gần nhất trước đó, ghi rõ trong `source`. Ngày PHIÊN đang giữ mã loại trừ mà
CSV không có giá ⇒ DỪNG (không điền hộ).

Dùng: python3 backfill_excluded_value.py --price-csv bq_price_DGC_....csv --out-dir seed
"""
import argparse
import csv
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "bin"))
import nav_loss_brake_monitor as m  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--price-csv", required=True)
ap.add_argument("--out-dir", required=True)
args = ap.parse_args()

# Ngày broker raw CHƯA gắn account_no cho bản ghi (trước khi có account thứ hai) ⇒ không lọc được
# theo §12. Chỉ ghi 0 khi có bằng chứng KHÁC nói account không giữ mã loại trừ nào.
ZERO_BY_EVIDENCE = {
    ("SpaceX", "2026-07-01"): "mốc khởi điểm: account clean-slate 1 tỷ tiền mặt (data/account_inception.json)",
    ("SpaceX", "2026-07-02"): "verified_snapshot_SpaceX_2026-07-02.json: 23 mã, không có PNJ",
    ("SpaceX", "2026-07-03"): "verified_snapshot_SpaceX_2026-07-03.json: 23 mã, không có PNJ",
}
price = {}
with open(args.price_csv, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        price[(r["ticker"], r["time"])] = float(r["Price"])

ctx = m.Ctx(state_dir=os.path.abspath(args.out_dir))
profiles = m.load_profiles(ctx.secrets_path)
stamp = ctx.now.isoformat(timespec="seconds")
for account in [k for k in m._read_json(ctx.inception_path, {}) if not k.startswith("_")]:
    prof = profiles[account]
    inc = datetime.date.fromisoformat(m.load_inception(account, ctx.inception_path)["inception_date"])
    dates = sorted({inc} | {r[0] for r in m.load_nav_history(account, ctx.exec_dir)})
    rows, skipped = [], []
    for d in dates:
        positions, ts, why = m.raw_positions(ctx.exec_dir, prof["account_id"], d)
        if positions is None:
            ev = ZERO_BY_EVIDENCE.get((account, d.isoformat()))
            if ev is None:
                skipped.append(f"{d}: {why}")
                continue
            rows.append({"date": d.isoformat(), "excluded_value": "0", "detail": "{}",
                         "positions_ts": "", "recorded_at": stamp,
                         "source": f"backfill: {why}; ghi 0 theo bằng chứng khác — {ev}"})
            continue
        held = m._qty_by_symbol(positions, keep=lambda p: p.get("symbol") in prof["excluded_tickers"])
        detail, total, carried = {}, 0.0, False
        for t, qty in sorted(held.items()):
            pd_ = d
            while not m.is_session(pd_):          # ngày nghỉ: giá chốt của phiên gần nhất trước đó
                pd_ = m.prev_session(pd_)
            if (t, pd_.isoformat()) not in price:
                sys.exit(f"❌ {account} {d}: đang giữ {t} {qty:,.0f} nhưng {args.price_csv} không "
                         f"có giá ngày {pd_}")
            carried = carried or pd_ != d
            detail[t] = {"qty": qty, "price": price[(t, pd_.isoformat())]}
            total += qty * detail[t]["price"]
        rows.append({"date": d.isoformat(), "excluded_value": f"{total:.0f}",
                     "detail": json.dumps(detail, sort_keys=True), "positions_ts": ts,
                     "source": ("backfill: dnse_raw positions × BQ ticker.Price"
                                + (" (ngày nghỉ: giá phiên trước)" if carried else "") if held else
                                "backfill: dnse_raw positions: không giữ mã loại trừ nào"),
                     "recorded_at": stamp})
    path = ctx.excl_path(account)
    if os.path.exists(path):
        os.remove(path)
    m._append_excluded(path, rows)
    nz = sum(1 for r in rows if r["excluded_value"] != "0")
    print(f"{account}: {len(rows)}/{len(dates)} ngày ghi được ({nz} ngày có giữ mã loại trừ) → {path}")
    for s in skipped:
        print(f"   bỏ qua {s}")
