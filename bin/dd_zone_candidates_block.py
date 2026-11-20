#!/usr/bin/env python3
"""dd_zone_candidates_block.py — khối "ứng viên sleeve từ sổ DD" cho báo cáo plan, CHỈ ĐỌC file
data/dd_zone_candidates_latest.json do cron dd_zone_candidates_daily.sh (19:45 ICT) làm mới.
Không gọi DNSE/BQ, không ghi file ⇒ chạy tức thì (trước đây send_plan_report.sh chạy lại cả
dd_price_zone_watch ~2m20s, vượt timeout 75s). User duyệt 2026-11-20 21:31.

Giao diện giữ tương thích lệnh cũ: `dd_zone_candidates_block.py run --report-block` (đối số bị bỏ qua).
rc=1 + stderr khi không đọc được file (send_plan_report in 1 dòng "KHÔNG KIỂM ĐƯỢC"); file CŨ hơn phiên
đã đóng gần nhất ⇒ vẫn in khối nhưng mở bằng dòng ⚠️ (không để danh sách cũ trông như mới)."""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")


def build(path=None, now=None):
    import dd_price_zone_watch as W
    import discretionary_candidate_funnel as F
    now = now or dt.datetime.now(W._ICT)
    path = path or W.CAND_JSON
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    block = F.format_dd_zone_lines(payload, now.date())
    exp, _ = W.default_asof(now)
    try:
        got = dt.date.fromisoformat(str(payload["asof"]))
    except (KeyError, ValueError):
        return block                                   # format_dd_zone_lines đã in cảnh báo asof hỏng
    if got < exp:
        block = (f"⚠️ Danh sách ứng viên CŨ: file asof {got:%d/%m} < phiên đóng cửa gần nhất {exp:%d/%m} "
                 f"(cron dd_zone_candidates_daily 19:45 chưa làm mới được — xem Trading Daily).\n" + block)
    return block


def main(argv):
    try:
        print(build())
    except Exception as e:  # noqa: BLE001 — §29: in lỗi thật; caller tạo 1 dòng cảnh báo, không chặn plan
        print(f"[ddz-block] LỖI: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
