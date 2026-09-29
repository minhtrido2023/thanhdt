#!/usr/bin/env python3
"""vn_realestate_monthly_check.py — interim monthly check cho imbalance tín dụng/BĐS EP-2026-01.

Chạy bởi cron (mike/bin/vn_realestate_monthly_check.sh, ngày 6 hàng tháng tối — khớp lịch GSO đổi
từ 01/08/2024: báo cáo KT-XH tháng công bố ngày 6 tháng kế tiếp, không còn ngày 29 tháng báo cáo).

Việc làm: dispatch native agent macro-strategist (headless, `claude -p --agent macro-strategist`,
KHÔNG-BLIND — mục đích là status-check hiện tại, không phân loại lịch sử) đọc số liệu GSO/SBV tháng
mới nhất, đối chiếu ngưỡng escalate đã chốt trong kb/projects/vn-realestate-structural-risk-20260826.md
mục "Review THÁNG (interim)". Luôn GỬI EMAIL (user yêu cầu 2026-08-31, mỗi tháng không chỉ khi có
bất thường); escalate thêm Discord + bus question CHỈ khi agent tự báo ngưỡng bị chạm.

Idempotent: 1 lần chạy/tháng — nếu artifact tháng đó đã tồn tại, thoát sớm (không gửi email lần 2)
trừ khi --force. Atomic write (tmp + os.replace).
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
MIKE_ROOT = os.path.abspath(os.path.join(ROOT, ".."))
CHECKS_DIR = os.path.join(MIKE_ROOT, "kb", "projects", "vn_realestate_monthly_checks")
TRACKER_FILE = os.path.join(MIKE_ROOT, "kb", "projects", "vn-realestate-structural-risk-20260826.md")

PROMPT_TEMPLATE = """Đây là nhiệm vụ KHÔNG-BLIND (status-check hiện tại, không phân loại lịch sử).
Bạn ĐƯỢC PHÉP dùng mọi thông tin tới thời điểm hiện tại.

BỐI CẢNH: fleet đang theo dõi 1 imbalance tín dụng/bất động sản VN phát hiện ở episode EP-2026-01
(2026-01-13 -> 2026-03-23, VNINDEX giảm -16,38%): lãi suất huy động tăng liên tục 12+ tháng
(4,8%->6,0%->6,8%), tín dụng hệ thống 19% (2025), tín dụng BĐS 36% (2025), SBV cap tín dụng BĐS
Quý 1/2026 rồi lại NỚI (30/05/2026, loại NOXH/KCN khỏi công thức). Lần kiểm tra gần nhất (2026-08-31,
dữ liệu Q2/2026) kết luận: BĐS CHƯA hạ nhiệt (Q2 +12,71% QoQ, nhanh hơn Q1), NPL xấu đi rõ (1,97%
Q2, cao nhất từ 2020), CPI là điểm sáng (đỉnh 5,60% T5 -> 4,69% T6, đã đảo chiều).

VIỆC CẦN LÀM cho kỳ kiểm tra tháng {month_label} này:
1. CPI YoY tháng mới nhất công bố (GSO/Cục Thống kê) — so trần Quốc hội 4,5% + xu hướng 3 tháng
2. Lãi suất huy động Big-4 tháng này so tháng trước (dùng deposit_rate_vn.py nếu đã cập nhật, hoặc
   WebSearch xác nhận)
3. Có tin tức chính sách MỚI về tín dụng/BĐS (thông tư/quyết định mới, siết hay nới) trong tháng
   không
4. Nếu có số liệu tín dụng/BĐS/NPL mới hơn Q2/2026 (thường theo quý, có thể chưa có) thì cập nhật

NGƯỠNG ESCALATE (đã chốt với user 2026-08-31, đọc {tracker_file} mục "Review THÁNG" để chắc chắn
dùng đúng số mới nhất nếu đã sửa):
- CPI YoY vượt lại trần 4,5% SAU KHI đã đảo chiều giảm (relapse)
- Lãi suất huy động Big-4 tăng thêm >=0,3pp trong 1 tháng
- Có thông tư/quyết định SIẾT MỚI (đảo hướng so với xu hướng NỚI đã ghi nhận 30/05/2026)
- Tin NPL/bank-run cụ thể ngoài chu kỳ công bố quý thường lệ

**KHÔNG tự sửa/append vào {tracker_file}** — wrapper script đã tự ghi 1 dòng tổng hợp vào file
đó sau khi bạn trả lời xong; bạn tự ghi thêm sẽ tạo dòng trùng lặp mỗi tháng. Chỉ ĐỌC file đó để
lấy ngưỡng escalate, đừng ghi.

Viết phần phân tích đầy đủ TRƯỚC, trích nguồn rõ ràng. Nếu KHÔNG tìm được số liệu mới trong tháng
(do độ trễ công bố thông thường), nói rõ đó là giới hạn dữ liệu, đừng suy đoán xấu đi khi chỉ là
thiếu dữ liệu.

ĐỊNH DẠNG BẮT BUỘC: DÒNG CUỐI CÙNG (và CHỈ MỘT dòng, sau khi đã phân tích xong, đừng viết dòng
này ở đâu khác) của TOÀN BỘ câu trả lời phải là CHÍNH XÁC một trong hai (không viết cả hai, không
viết placeholder rồi sửa lại — quyết định trước rồi mới viết dòng này):
FINAL_STATUS: ESCALATE — <lý do ngắn 1 câu>
FINAL_STATUS: BINH_THUONG — <lý do ngắn 1 câu>"""


def month_label(dt):
    return dt.strftime("%Y-%m")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Chạy lại dù artifact tháng này đã có")
    ap.add_argument("--dry-run", action="store_true", help="In prompt, KHÔNG gọi claude/gửi email")
    args = ap.parse_args()

    now = datetime.now(ICT)
    label = month_label(now)
    os.makedirs(CHECKS_DIR, exist_ok=True)
    artifact_path = os.path.join(CHECKS_DIR, f"{label}.md")

    if os.path.exists(artifact_path) and not args.force:
        print(f"SKIP: artifact tháng {label} đã tồn tại ({artifact_path}) — idempotent, không chạy lại.")
        return 0

    prompt = PROMPT_TEMPLATE.format(month_label=label, tracker_file=TRACKER_FILE)

    if args.dry_run:
        print(prompt)
        return 0

    result = subprocess.run(
        [
            "claude", "-p", "--agent", "macro-strategist", prompt,
            "--output-format", "text",
            "--allowedTools", "Bash,Read,Grep,Glob,WebSearch,WebFetch",
        ],
        cwd=MIKE_ROOT,
        capture_output=True,
        text=True,
        timeout=1200,
    )
    if result.returncode != 0:
        err = result.stderr.strip() or "(stderr rỗng)"
        print(f"LỖI: claude -p --agent macro-strategist thoát mã {result.returncode}. Lỗi thật: {err}", file=sys.stderr)
        return 1

    output = result.stdout.strip()
    if not output:
        print("LỖI: claude -p trả về output rỗng.", file=sys.stderr)
        return 1

    # Đọc từ DÒNG CUỐI lên (không phải dòng đầu) — agent được yêu cầu viết marker SAU KHI đã
    # phân tích xong; nếu agent lỡ viết cả placeholder lẫn kết luận thật, kết luận thật luôn ở
    # SAU cùng nên duyệt ngược đảm bảo lấy đúng cái cuối, không lấy nhầm placeholder ở đầu.
    status, reason = None, None
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.startswith("FINAL_STATUS: ESCALATE"):
            status = "ESCALATE"
            reason = line.split("—", 1)[1].strip() if "—" in line else ""
            break
        if line.startswith("FINAL_STATUS: BINH_THUONG"):
            status = "BINH_THUONG"
            reason = line.split("—", 1)[1].strip() if "—" in line else ""
            break
    if status is None:
        status = "KHONG_XAC_DINH"
        reason = "Agent không tuân theo định dạng dòng FINAL_STATUS bắt buộc — đọc nguyên văn output."

    header = f"# VN Real Estate Interim Check — {label}\n\n> Status: {status} — {reason}\n\n---\n\n"
    tmp_path = artifact_path + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(header + output + "\n")
    os.replace(tmp_path, artifact_path)
    print(f"OK: đã ghi artifact {artifact_path}, status={status}")

    tracker_line = f"- {now.strftime('%Y-%m-%d')}: interim tháng {label} = **{status}** ({reason}) — chi tiết `{artifact_path}`\n"
    with open(TRACKER_FILE, "a") as f:
        f.write(tracker_line)

    subject = f"[VN Macro Watch] Interim tháng {label} — {status}"
    email_rc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "send_macro_note_email.py"), artifact_path, "--subject", subject],
    ).returncode
    if email_rc != 0:
        print("CẢNH BÁO: gửi email thất bại — xem log send_macro_note_email.py ở trên.", file=sys.stderr)

    notify_sh = os.path.join(ROOT, "notify_thread.sh")
    if status == "ESCALATE":
        msg = f"🚨 **VN Macro Watch — Interim tháng {label}: ESCALATE**\n\n{reason}\n\nChi tiết: `{artifact_path}` (đã gửi email)."
    elif status == "BINH_THUONG":
        msg = f"🧭 VN Macro Watch — interim tháng {label}: bình thường, không có ngưỡng nào bị chạm ({reason}). Đã gửi email."
    else:
        msg = f"⚠️ VN Macro Watch — interim tháng {label}: agent KHÔNG tuân theo định dạng dòng đầu, cần Mike xem lại thủ công. Đã gửi email nguyên văn."
    subprocess.run([notify_sh, msg, "vn_macro_watch"])

    append_event = os.path.join(ROOT, "append_event.sh")
    event_type = "question" if status == "ESCALATE" else "finding"
    payload_json = json.dumps({"status": status, "reason": reason, "artifact": artifact_path})
    subprocess.run([
        append_event, "macro-strategist", event_type,
        f"vn-realestate-monthly-check-{label}",
        payload_json,
    ])

    return 0


if __name__ == "__main__":
    sys.exit(main())
