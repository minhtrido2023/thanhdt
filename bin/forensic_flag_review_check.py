#!/usr/bin/env python3
"""forensic_flag_review_check.py — cổng HẾT HẠN cho `data/forensic_flags.csv`.

VÌ SAO TỒN TẠI (user chốt 2026-09-04): cờ forensic là lớp bảo vệ DUY NHẤT cho loại rủi ro
không tự động hoá được (gian lận kế toán, thao túng — `adaptive_exclusion_v3_20260904.md`
chứng minh gate tài chính động KHÔNG thay được nó: false-positive 91,9%, DSR 0,14). Nhưng
lớp thủ công đó trước đây KHÔNG có hạn rà lại ⇒ một mã bị `exclude` nằm mãi không ai nhìn
lại, kể cả khi doanh nghiệp đã sạch. User: "forensic cũng phải đưa thời hạn review xử lý
vào, không được để treo mãi."

CƠ CHẾ (khớp thiết kế đã duyệt ở `adaptive_exclusion_v2_20260904.md` §Việc 3):
  - `review_by` = `date` + 12 tháng (mặc định) hoặc + 3 tháng với
    `flag_type=leadership_investigation` (diễn biến pháp lý nhanh hơn nhiều).
  - Còn ≤ SOON_DAYS ngày  → dòng FYI, KHÔNG mở question (tránh mệt mỏi cảnh báo).
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
Dò bằng `mike_json.py has-event-prefix` — KHÔNG khớp tuyệt đối (§26/§28: producer luôn thêm
hậu tố tự do; khớp tuyệt đối là đúng lỗi đã cắn ở `wags_autofix.sh` 2026-08-04→08-11).

Exit code: 0 = không có gì quá hạn (có thể có FYI); 1 = có ≥1 cờ quá hạn chưa đóng.
`--json <path>` để caller đọc máy. Không tự gửi Discord/ghi bus — caller
(`ops_health_check.sh`) làm việc đó, giữ script này thuần đọc + báo cáo.
"""
import argparse
import csv
import json
import os
import subprocess
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


def _closed(ticker, since_iso):
    """Đã có event đóng cho ticker này (bất kỳ agent nào) kể từ `since_iso` chưa?

    Trả (closed: bool, err: str|None). Lỗi gọi được TRẢ VỀ chứ không nuốt — §29: thông điệp
    chẩn đoán phải trích bằng chứng thật, không đoán hộ.
    """
    topic = f"{TOPIC_PREFIX}{ticker}"
    for agent in ("Mike", "Taylor", "Winston", "Spyros", "Wags", "quant-skeptic"):
        for etype in ("decision", "answer", "finding"):
            cmd = [
                sys.executable,
                os.path.join(MIKE_ROOT, "bin", "mike_json.py"),
                "has-event-prefix",
                BUS_DIR,
                agent,
                since_iso,
                f"{etype}:{topic}",
            ]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            except Exception as e:
                return False, f"gọi has-event-prefix thất bại: {e!r}"
            # HỢP ĐỒNG: has-event-prefix báo qua EXIT CODE (0=khớp, 1=không khớp); stdout là
            # văn bản người đọc ("MATCH ..." / "no match: ..."). Bản nháp đầu kiểm stdout
            # =="1"/"true" nên KHÔNG BAO GIỜ nhận ra cờ đã đóng — bắt được lúc test tay
            # (§19 verify-before-done: chạy thật, đừng tin chữ ký trông có vẻ đúng).
            if r.returncode == 0:
                return True, None
            if r.returncode not in (0, 1):
                return False, (
                    f"has-event-prefix rc={r.returncode} cho {agent}/{etype}: "
                    f"{(r.stderr or r.stdout).strip()[:200]}"
                )
    return False, None


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

    overdue, soon, missing, ok = [], [], [], 0
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
        if days < 0:
            since = f"{rec['flag_date']}T00:00:00Z"
            done, err = _closed(tk, since)
            if err:
                rec["lookup_error"] = err
            if done:
                ok += 1
            else:
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
    if missing:
        lines.append(
            f"⚠️ forensic-flag thiếu/hỏng `review_by` ({len(missing)}): {', '.join(missing)} "
            f"— điền ngày để cờ không treo vô hạn."
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
