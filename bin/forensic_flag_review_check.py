#!/usr/bin/env python3
"""forensic_flag_review_check.py — cổng HẾT HẠN cho `data/forensic_flags.csv`.

VÌ SAO TỒN TẠI (user chốt 2026-09-04): cờ forensic là lớp bảo vệ DUY NHẤT cho loại rủi ro
không tự động hoá được (gian lận kế toán, thao túng — `adaptive_exclusion_v3_20260904.md`
chứng minh gate tài chính động KHÔNG thay được nó: false-positive 91,9%, DSR 0,14). Nhưng
lớp thủ công đó trước đây KHÔNG có hạn rà lại ⇒ một mã bị `exclude` nằm mãi không ai nhìn
lại, kể cả khi doanh nghiệp đã sạch. User: "forensic cũng phải đưa thời hạn review xử lý
vào, không được để treo mãi."

CƠ CHẾ (khớp thiết kế đã duyệt ở `adaptive_exclusion_v2_20260904.md` §Việc 3):
  - `review_by` GIÃN theo nhóm (user chốt 2026-09-04, tránh 11 cảnh báo nổ cùng ngày):
    nhóm 1 `exclude` fraud_confirmed/related_party → trước hạn gốc 2 TUẦN;
    nhóm 2 `exclude` còn lại → trước 1 TUẦN; nhóm 3 `watch` → ĐÚNG hạn gốc (date+12 tháng).
    `flag_type=leadership_investigation` (loại mới, xem v2 §Việc 4) dùng date + 3 tháng.
  - Còn ≤ SOON_DAYS ngày  → dòng FYI, KHÔNG mở question (tránh mệt mỏi cảnh báo).
  - GỠ SỚM: có event đóng TRƯỚC hạn ⇒ cờ rời hàng đợi ngay, không chờ tới `review_by`.
  - ĐÃ QUÁ HẠN           → bus `question` topic `forensic-flag-review: <TICKER>`, LẶP LẠI
    mỗi lượt chạy cho tới khi có event đóng (§26 coding_guidelines: không để quyết định
    cần-người treo im lặng).
  - FAIL-CLOSED: quá hạn KHÔNG tự gỡ cờ. Bất đối xứng chi phí đo được — giữ nhầm một mã đã
    sạch chỉ tốn cơ hội CÓ GIỚI HẠN (~0,84pp NAV sleeve, ước ở v2 §Việc 2, và skeptic xác
    nhận đó là ước CAO); gỡ nhầm một mã đang gian lận thật tốn KHÔNG giới hạn.

ĐÓNG một hạn rà: người review ghi bus event topic BẮT ĐẦU bằng `forensic-flag-review: <TICKER>`
(tự do thêm mô tả phía sau), rồi cập nhật `review_by` mới trong CSV:
    bin/append_event.sh <agent> decision "forensic-flag-review: PC1 — giữ exclude, chưa có
      kết luận điều tra" '{"verdict":"keep_exclude","review_by_new":"2028-06-20"}'
Dò bằng `scan_resolved()` — cùng ngữ nghĩa PREFIX của `mike_json.py has-event-prefix`, KHÔNG
khớp tuyệt đối (§26/§28: producer luôn thêm hậu tố tự do; khớp tuyệt đối là đúng lỗi đã cắn ở
`wags_autofix.sh` 2026-08-04→08-11) — nhưng quét bus MỘT LẦN thay vì 198 tiến trình con.

Exit code: 0 = không có gì quá hạn (có thể có FYI); 1 = có ≥1 cờ quá hạn chưa đóng.
`--json <path>` để caller đọc máy. Không tự gửi Discord/ghi bus — caller
(`ops_health_check.sh`) làm việc đó, giữ script này thuần đọc + báo cáo.
"""
import argparse
import csv
import glob
import gzip
import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")  # §16: neo TZ tường minh, không tin TZ của host

SOON_DAYS = 14
WC_ROOT = os.environ.get(
    "WC_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
MIKE_ROOT = os.path.join(WC_ROOT, "mike")
CSV_PATH = os.path.join(WC_ROOT, "data", "forensic_flags.csv")
BUS_DIR = os.path.join(MIKE_ROOT, "bus")
TOPIC_PREFIX = "forensic-flag-review: "


CLOSE_TYPES = ("decision", "answer", "finding")


def scan_resolved(bus_dir):
    """Quét bus MỘT LẦN → {ticker: (ts, agent, topic)} cho mọi cờ đã được xử lý.

    Quét một lượt thay vì gọi `mike_json.py has-event-prefix` cho từng (mã × agent × loại):
    11 mã × 6 agent × 3 loại = 198 tiến trình con mỗi lượt cron — quá đắt cho một check chạy
    2 lần/ngày. Ngữ nghĩa giữ y hệt has-event-prefix: khớp topic theo PREFIX
    `forensic-flag-review: <TICKER>` (§26/§28 — producer luôn thêm mô tả tự do phía sau;
    khớp tuyệt đối là đúng lỗi đã cắn ở `wags_autofix.sh` 2026-08-04→08-11).

    Đọc CẢ hot (`inbox/<agent>.jsonl`) lẫn archive (`inbox/archive/<agent>_YYYY-MM.jsonl.gz`)
    — cùng bố cục `mike_json._agent_files`. Bỏ sót archive = báo "chưa xử lý" cho việc đã
    xử lý xong từ tháng trước.

    Trả (resolved: dict, errors: list[str]). Lỗi ĐỌC được trả về, không nuốt (§29).
    """
    resolved, errors = {}, []
    inbox = os.path.join(bus_dir, "inbox")
    files = sorted(glob.glob(os.path.join(inbox, "*.jsonl")))
    files += sorted(glob.glob(os.path.join(inbox, "archive", "*.jsonl.gz")))
    for path in files:
        try:
            opener = gzip.open if path.endswith(".gz") else open
            with opener(path, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or TOPIC_PREFIX not in line:
                        continue  # lọc thô trước khi parse JSON — phần lớn dòng không liên quan
                    try:
                        e = json.loads(line)
                    except ValueError:
                        continue
                    if e.get("event_type") not in CLOSE_TYPES:
                        continue
                    topic = str(e.get("topic") or "")
                    if not topic.startswith(TOPIC_PREFIX):
                        continue
                    rest = topic[len(TOPIC_PREFIX):].strip()
                    tk = rest.split()[0].strip(":,-").upper() if rest else ""
                    if not tk:
                        continue
                    ts = str(e.get("ts") or "")
                    # giữ event MỚI NHẤT cho mỗi mã
                    if tk not in resolved or ts > resolved[tk][0]:
                        resolved[tk] = (ts, str(e.get("agent") or "?"), topic)
        except Exception as ex:
            errors.append(f"{os.path.basename(path)}: {ex!r}")
    return resolved, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=CSV_PATH)
    ap.add_argument("--json", help="ghi kết quả máy-đọc ra file")
    ap.add_argument("--today", help="ISO date, chỉ dùng cho selfcheck")
    args = ap.parse_args()

    today = (
        datetime.strptime(args.today, "%Y-%m-%d").date()
        if args.today
        else datetime.now(_ICT).date()
    )

    if not os.path.exists(args.csv):
        # Thiếu file = KHÔNG kết luận "không có cờ nào". Nói thẳng, để caller cảnh báo.
        out = {"error": f"không đọc được {args.csv}", "overdue": [], "soon": [], "ok": 0}
        print(f"⚠️ forensic-flag review: không đọc được `{args.csv}` — không kết luận được.")
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
        return 1

    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # GỠ SỚM (user chốt 2026-09-04): "nếu chưa đến thời gian review nhưng có sự kiện để loại
    # khỏi danh sách thì cũng có cơ chế để bỏ khỏi thời điểm đến hạn cần xử lý". Quét bus MỘT
    # LẦN cho MỌI dòng — không chỉ dòng đã quá hạn — nên một cờ được xử lý trước hạn sẽ rời
    # hàng đợi ngay, không chờ tới ngày rồi mới báo.
    resolved, scan_errs = scan_resolved(BUS_DIR)

    overdue, soon, missing, early, ok = [], [], [], [], 0
    for r in rows:
        tk = (r.get("ticker") or "").strip()
        rb = (r.get("review_by") or "").strip()
        if not rb:
            missing.append(tk)
            continue
        try:
            rb_d = datetime.strptime(rb, "%Y-%m-%d").date()
        except ValueError:
            missing.append(tk)
            continue
        days = (rb_d - today).days
        rec = {
            "ticker": tk,
            "severity": (r.get("severity") or "").strip(),
            "flag_type": (r.get("flag_type") or "").strip(),
            "flag_date": (r.get("date") or "").strip(),
            "review_by": rb,
            "days_left": days,
        }
        hit = resolved.get(tk.upper())
        # Chỉ tính event ghi SAU ngày gắn cờ — event cũ hơn nói về một lần flag TRƯỚC đó,
        # không đóng được lần này (cùng kỷ luật `since_iso` của has-event-prefix).
        if hit and hit[0] >= f"{rec['flag_date']}T00:00:00Z":
            rec["resolved_at"], rec["resolved_by"] = hit[0], hit[1]
            if days >= 0:
                early.append(rec)   # xử lý TRƯỚC hạn → rời hàng đợi
            else:
                ok += 1
            continue
        if days < 0:
            overdue.append(rec)
        elif days <= SOON_DAYS:
            soon.append(rec)
        else:
            ok += 1

    overdue.sort(key=lambda x: x["days_left"])
    soon.sort(key=lambda x: x["days_left"])

    lines = []
    if overdue:
        det = ", ".join(
            f"{o['ticker']}({o['severity']}, quá {abs(o['days_left'])}d)" for o in overdue
        )
        lines.append(
            f"🚩 forensic-flag QUÁ HẠN rà lại ({len(overdue)}): {det} — cờ VẪN áp "
            f"(fail-closed, không tự gỡ). Đóng bằng bus event topic bắt đầu "
            f"`{TOPIC_PREFIX}<TICKER>` rồi cập nhật `review_by` trong data/forensic_flags.csv."
        )
    if soon:
        det = ", ".join(f"{s['ticker']}({s['days_left']}d)" for s in soon)
        lines.append(f"🗓️ forensic-flag sắp tới hạn rà lại (≤{SOON_DAYS}d): {det}")
    if early:
        det = ", ".join(f"{e['ticker']}(bởi {e['resolved_by']})" for e in early)
        lines.append(
            f"↩️ forensic-flag đã xử lý TRƯỚC hạn ({len(early)}): {det} — đã rời hàng đợi, "
            f"không chờ tới `review_by`. Nhớ cập nhật/xoá dòng trong data/forensic_flags.csv."
        )
    if missing:
        lines.append(
            f"⚠️ forensic-flag thiếu/hỏng `review_by` ({len(missing)}): {', '.join(missing)} "
            f"— điền ngày để cờ không treo vô hạn."
        )
    if scan_errs:
        lines.append(
            f"⚠️ forensic-flag: không đọc được {len(scan_errs)} file bus — có thể BỎ SÓT cờ đã "
            f"xử lý. Lỗi thật: {'; '.join(scan_errs[:3])}"
        )
    if not lines:
        lines.append(f"✅ forensic-flag: {ok}/{len(rows)} cờ còn trong hạn rà lại.")

    print("\n".join(lines))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "today": today.isoformat(),
                    "overdue": overdue,
                    "soon": soon,
                    "missing_review_by": missing,
                    "resolved_early": early,
                    "scan_errors": scan_errs,
                    "ok": ok,
                    "total": len(rows),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

    return 1 if (overdue or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
