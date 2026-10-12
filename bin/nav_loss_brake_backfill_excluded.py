#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá chuỗi giá trị mã loại trừ của nav_loss_brake_monitor.py cho các ngày ĐÃ QUA (monitor chỉ tự
ghi được từ nay: active_nav_{account}.json bị ghi đè mỗi tối nên giá đóng cửa ngày cũ không còn
trên đĩa). Bắt buộc chạy trước lượt monitor đầu tiên — chuỗi không bắt đầu ĐÚNG mốc khởi điểm của
account thì phanh lỗ-từ-đỉnh chỉ ra số tạm tính.

CHỈ THÊM ngày còn thiếu, ghi nguyên tử; dòng đã có KHÔNG bị đụng (muốn sửa một dòng đã ghi:
`nav_loss_brake_monitor.py --correct-excluded`). Script này không gọi broker, không gọi mạng.

KL: bản ghi positions cuối ngày của broker, chụp SAU giờ đóng cửa (dnse_raw_{date}.jsonl, lọc
account) — cùng hàm monitor dùng. Giá: giá đóng cửa CHƯA điều chỉnh (cột `Price` của bảng
`ticker`) trong file CSV truyền vào, cột time,ticker,Price — truy vấn lịch sử, lấy bằng:
  bq query --use_legacy_sql=false --format=csv --max_rows=500 'SELECT t.time, t.ticker, t.Price,
    t.Close FROM tav2_bq.ticker AS t WHERE t.time BETWEEN "2026-07-06" AND "2026-10-09"
    AND t.ticker = "DGC" ORDER BY t.time'
Ngày KHÔNG phải phiên giao dịch mà nav_history vẫn có dòng (vd 2026-08-31, nghỉ lễ): dùng giá
đóng cửa của phiên gần nhất trước đó, ghi rõ trong `source`. Ngày PHIÊN đang giữ mã loại trừ mà
CSV không có giá ⇒ DỪNG (không điền hộ).

Dùng: python3 mike/bin/nav_loss_brake_backfill_excluded.py --price-csv <csv> --out-dir data/loss_brake \\
          [--until <ngày cuối CSV có giá>]
"""
import argparse
import csv
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav_loss_brake_monitor as m  # noqa: E402

# Ngày broker raw CHƯA gắn account_no cho bản ghi (trước khi có account thứ hai) ⇒ không lọc được
# theo §12. Chỉ ghi 0 khi có bằng chứng KHÁC nói account không giữ mã loại trừ nào.
ZERO_BY_EVIDENCE = {
    ("SpaceX", "2026-07-01"): "mốc khởi điểm: account clean-slate 1 tỷ tiền mặt (data/account_inception.json)",
    ("SpaceX", "2026-07-02"): "verified_snapshot_SpaceX_2026-07-02.json: 23 mã, không có PNJ",
    ("SpaceX", "2026-07-03"): "verified_snapshot_SpaceX_2026-07-03.json: 23 mã, không có PNJ",
}


def build_rows(ctx, account, prof, price, have, price_csv, until=None):
    """(dòng mới[], ngày bỏ qua[]) cho các ngày chưa có trong `have` (và <= `until` nếu có)."""
    inc = datetime.date.fromisoformat(m.load_inception(account, ctx.inception_path)["inception_date"])
    stamp = ctx.now.isoformat(timespec="seconds")
    rows, skipped = [], []
    for d in sorted({inc} | {r[0] for r in m.load_nav_history(account, ctx.exec_dir)}):
        if d in have or (until is not None and d > until):
            continue
        positions, ts, why = m.close_positions(ctx, prof["account_id"], d)
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
                raise SystemExit(f"❌ {account} {d}: đang giữ {t} {qty:,.0f} nhưng {price_csv} "
                                 f"không có giá ngày {pd_}")
            carried = carried or pd_ != d
            detail[t] = {"qty": qty, "price": price[(t, pd_.isoformat())]}
            total += qty * detail[t]["price"]
        rows.append({"date": d.isoformat(), "excluded_value": f"{total:.0f}",
                     "detail": json.dumps(detail, sort_keys=True), "positions_ts": ts,
                     "source": ("backfill: dnse_raw positions × BQ ticker.Price"
                                + (" (ngày nghỉ: giá phiên trước)" if carried else "") if held else
                                "backfill: dnse_raw positions: không giữ mã loại trừ nào"),
                     "recorded_at": stamp})
    return rows, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--price-csv", required=True)
    ap.add_argument("--out-dir", required=True, help="state-dir đích (thật: data/loss_brake)")
    ap.add_argument("--data-root", help="mặc định: data/ thật (chỉ ĐỌC)")
    ap.add_argument("--secrets")
    ap.add_argument("--account", action="append")
    ap.add_argument("--until", help="YYYY-MM-DD: chỉ vá tới hết ngày này (ngày sau đó để monitor tự "
                                    "ghi bằng giá active_nav cùng ngày — CSV giá lịch sử chưa có)")
    args = ap.parse_args(argv)

    price = {}
    with open(args.price_csv, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            price[(r["ticker"], r["time"])] = float(r["Price"])
    ctx = m.Ctx(data_root=args.data_root, state_dir=os.path.abspath(args.out_dir),
                secrets_path=args.secrets)
    profiles = m.load_profiles(ctx.secrets_path)
    accounts = args.account or [k for k in m._read_json(ctx.inception_path, {})
                                if not k.startswith("_")]
    with m.state_lock(ctx):
        for account in accounts:
            path = ctx.excl_path(account)
            have = m.read_excluded_history(path)
            rows, skipped = build_rows(ctx, account, profiles[account], price, have,
                                       args.price_csv,
                                       datetime.date.fromisoformat(args.until) if args.until else None)
            if rows:
                m._append_excluded(path, rows)     # nguyên tử, không ghi đè dòng đã có
            nz = sum(1 for r in rows if r["excluded_value"] != "0")
            print(f"{account}: thêm {len(rows)} ngày ({nz} ngày có giữ mã loại trừ), đã có sẵn "
                  f"{len(have)} ngày → {path}")
            for s in skipped:
                print(f"   bỏ qua {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
