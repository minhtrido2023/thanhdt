#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe paper-trial P2 (`expvol_pacing`) — đọc `EXPVOL_SHADOW` trong journal executor LIVE.

P2 = đổi mẫu số pacing của `ceil_allow` từ KL ĐÃ khớp sang max(KL đã khớp, ADV20_cp × f(t)),
kèm clamp fill fleet ≤50% tape thật. Đang **paper-only** (`expected_volume_pacing_live_gate`),
nên trên tiền thật nó KHÔNG đổi hành vi — chỉ ghi lại allowance mà nó SẼ cho ở cùng lệnh /
cùng tape / cùng phút (`trading_bot/executor.py::_expvol_shadow`).

Vì sao nguồn số của trial là journal LIVE chứ không phải paper: account paper `main` chỉ phát
sinh lệnh `book="PROBE"`, mà nhánh ADV20-paced chỉ nhận CAPIT/DISCRETIONARY_SPECIAL buy ⇒ trên
paper P2 KHÔNG BAO GIỜ chạy vào. Đo được ở đây là nhờ đối chứng ghép cặp trên tape thật.

**N = order-day** (date × account × parent_id), KHÔNG phải số dòng: các slice trong cùng một
lệnh của cùng một phiên không độc lập (cùng mã, cùng tape, cùng trần). Số slice in ra là để
biết độ phủ, không phải cỡ mẫu thống kê.

Chạy: python3 mike/bin/expvol_shadow_probe.py [--days N] [--json]
"""
import argparse
import csv
import glob
import os
import statistics as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIVE_ACCOUNTS = ("SpaceX", "ZaloPay", "RocketX")
CLAMP = 0.50          # `expected_volume_tape_clamp` — trần đuôi mà P2 tự áp
ICT = ZoneInfo("Asia/Ho_Chi_Minh")


def today_ict():
    """§16: neo múi giờ TƯỜNG MINH. Journal đặt tên file theo NGÀY GIAO DỊCH ICT; `date.today()`
    trần trên host/cron chạy UTC sẽ lệch 1 ngày suốt 07:00-24:00 ICT ⇒ dòng "hôm nay" của probe
    hoặc trống rỗng hoặc chỉ vào phiên hôm trước."""
    return datetime.now(ICT).date()


def parse_note(note):
    """`k=v;k=v` → dict số. Bỏ qua phần chữ đầu dòng (`P2 OFF (đối chứng...) f(10:00)=0.198`)."""
    out = {}
    for part in note.split(";"):
        if "=" not in part:
            continue
        k, v = part.rsplit("=", 1)
        k = k.strip().split()[-1].lstrip("(").rstrip(")")
        try:
            out[k] = float(v) if "." in v else int(v)
        except ValueError:
            out[k] = v.strip()
    return out


def load_rows(days):
    """[(date, account, row_dict)] — dedupe theo (ngày, account, parent, phút).

    Dedupe cần vì executor chỉ chặn ghi trùng TRONG một tiến trình: restart giữa phiên (đúng
    kịch bản resume state) sẽ ghi lại cùng một phút. Đếm trùng ở đây thổi phồng cỡ mẫu của
    chính trial này.
    """
    cutoff = today_ict() - timedelta(days=days) if days else None
    seen, rows, errs = set(), [], []
    for acc in LIVE_ACCOUNTS:
        for path in sorted(glob.glob(os.path.join(
                WC_ROOT, f"data/execution_logs/exec_{acc}_*_journal.csv"))):
            day = os.path.basename(path)[len(f"exec_{acc}_"):-len("_journal.csv")]
            if "2099" in day:                      # fixture selfcheck, không phải phiên thật
                continue
            try:
                d = datetime.strptime(day, "%Y-%m-%d").date()
            except ValueError:
                continue
            if cutoff and d < cutoff:
                continue
            with open(path, newline="", encoding="utf-8", errors="replace") as f:
                for r in csv.DictReader(f):
                    ev = r.get("event")
                    if ev == "EXPVOL_SHADOW_ERR":
                        errs.append((d, acc, r.get("note", "")))
                        continue
                    if ev != "EXPVOL_SHADOW":
                        continue
                    key = (d, acc, r.get("parent_id"), (r.get("ts") or "")[:16])
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append((d, acc, {**r, **parse_note(r.get("note", ""))}))
    return rows, errs


def summarize(rows, errs, today):
    order_days = {(d, a, r.get("parent_id")) for d, a, r in rows}
    sessions = {d for d, _, _ in rows}
    ceil_rows = [r for _, _, r in rows if r.get("bind") == "ceil"]
    deltas = [r["delta"] for r in ceil_rows if isinstance(r.get("delta"), (int, float))]

    # Kiểm ĐỘC LẬP bất biến an toàn: nếu fleet fill hết p2_allow thì tỷ trọng trên tape thật là
    # (F + X)/(V + X) — phải ≤ CLAMP. Đây là recompute từ số đã ghi, không tin công thức trong
    # executor (§6: đối soát bằng đường đi khác, đừng tin field trông hợp lý).
    worst, breaches = 0.0, 0
    for r in ceil_rows:
        try:
            f_, v_, x_ = r["fleet_filled"], r["tape"], max(0, r["p2_allow"])
        except KeyError:
            continue
        if v_ + x_ <= 0:
            continue
        share = (f_ + x_) / (v_ + x_)
        worst = max(worst, share)
        if share > CLAMP + 1e-9:
            breaches += 1

    t_rows = [r for d, _, r in rows if d == today]
    t_od = {(d, a, r.get("parent_id")) for d, a, r in rows if d == today}
    lines = [
        f"{len(sessions)} phiên có lệnh ADV20-paced · **order-day N={len(order_days)}** · "
        f"{len(rows)} slice quan sát",
        f"bind=ceil {len(ceil_rows)}/{len(rows)}"
        f" ({100 * len(ceil_rows) / len(rows):.1f}%) — chỉ nhóm này P2 mới nới được"
        if rows else "chưa có quan sát nào",
    ]
    if deltas:
        lines.append(f"delta allowance khi bind=ceil (cp): trung vị {st.median(deltas):+,.0f} · "
                     f"tb {st.mean(deltas):+,.0f} · max {max(deltas):+,.0f} · "
                     f"{sum(1 for x in deltas if x > 0)}/{len(deltas)} slice có delta>0")
    lines.append(f"an toàn: %tape tối đa nếu P2 khớp trọn allowance = {100 * worst:.1f}% "
                 f"(trần {100 * CLAMP:.0f}%) · vi phạm clamp **{breaches}** · "
                 f"EXPVOL_SHADOW_ERR **{len(errs)}**")
    lines.append(f"hôm nay ({today}): {len(t_od)} order-day · {len(t_rows)} slice · "
                 f"bind=ceil {sum(1 for r in t_rows if r.get('bind') == 'ceil')}")
    return lines, {"order_days": len(order_days), "sessions": len(sessions), "slices": len(rows),
                   "ceil_slices": len(ceil_rows), "median_delta": st.median(deltas) if deltas else None,
                   "worst_tape_share": worst, "clamp_breaches": breaches, "errors": len(errs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="0 = toàn bộ lịch sử journal")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows, errs = load_rows(a.days)
    if not rows and not errs:
        print("0 dòng EXPVOL_SHADOW — chưa có lệnh CAPIT/DISCRETIONARY_SPECIAL buy nào chạy qua "
              "executor kể từ khi bật shadow log (2026-08-17). Chưa đo được, KHÔNG phải 'không "
              "có edge'.")
        return
    lines, stats = summarize(rows, errs, today_ict())
    if a.json:
        import json
        print(json.dumps(stats, ensure_ascii=False))
        return
    print("\n".join(lines))
    for d, acc, note in errs[:3]:
        print(f"⚠️ ERR {d} {acc}: {note[:160]}")


if __name__ == "__main__":
    main()
