#!/usr/bin/env python3
"""send_report_email.py <report.md> [--subject "..."]

Gửi 1 báo cáo (weekly/monthly .md) qua email — Gmail SMTP với App Password (KHÔNG dùng chung
credential OAuth gmail.readonly hiện có cho DNSE auto-OTP, xem lý do trong kb/incidents/ hoặc
hỏi Mike — tách riêng để không rủi ro tới flow đăng nhập DNSE đang sống).

Credential (CHƯA có, cần user cung cấp trước khi dùng được):
  secrets/gmail_smtp_app_password.json =
    {"from_email": "...", "app_password": "xxxx xxxx xxxx xxxx", "to_email": "..."}
  from_email = tài khoản Gmail dùng để GỬI (cần bật 2FA + tạo App Password riêng cho việc này,
  KHÔNG phải mật khẩu đăng nhập thường). to_email = địa chỉ nhận báo cáo.

Không tự đoán/tự tạo credential này — script CHỦ Ý fail rõ ràng (exit 2 + thông báo) nếu thiếu,
thay vì âm thầm no-op hoặc dùng giá trị mặc định sai.

Thân email = HTML render qua render_report_html.py (bin/), theo chuẩn trình bày ngành quản lý
đầu tư (GIPS/CFA Asset Manager Code/tear-sheet/investor-letter — xem docstring file đó) — KHÔNG
còn gửi markdown thô làm plain text (2026-08-01, user phản ánh format "kiểu LLM khó nhìn"). File
.md gốc vẫn đính kèm để có bản nguồn tham chiếu.
"""
import argparse
import base64
import json
import os
import re
import smtplib
import sys
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ROOT = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
SECRETS_PATH = (
    os.environ.get("SEND_REPORT_SMTP_SECRET")
    or os.environ.get("REPORT_SMTP_SECRET_PATH")
    or os.path.join(WC_ROOT, "secrets", "gmail_smtp_app_password.json")
)

sys.path.insert(0, ROOT)
from render_report_html import render_html  # noqa: E402


def _collect_inline_images(html_body):
    """Replace data:image URIs with cid: links and return the images to attach."""
    counter = {"n": 0}
    images = []

    def _replace(match):
        mime, b64 = match.group(1), match.group(2)
        subtype = mime.split("/", 1)[1] if "/" in mime else "png"
        data = base64.b64decode(b64)
        cid = f"report-image-{counter['n']}"
        images.append({"cid": cid, "subtype": subtype, "data": data})
        counter["n"] += 1
        return f'src="cid:{cid}"'

    new_html = re.sub(r'src="data:([^;]+);base64,([^"]+)"', _replace, html_body)
    return new_html, images


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_path")
    ap.add_argument("--subject")
    ap.add_argument("--skip-return-gate", metavar="LÝ_DO",
                    help="BỎ QUA cổng tỉ suất (coding_guidelines §21) — chỉ dùng khi đã hiểu vì sao "
                         "cổng báo lệch; lý do được in ra và ghi vào email log")
    args = ap.parse_args()

    if not os.path.exists(args.report_path):
        print(f"❌ Không tìm thấy file báo cáo: {args.report_path}", file=sys.stderr)
        sys.exit(1)

    # CỔNG CHẶN CỨNG — tỉ suất per-position phải đã cộng cổ tức (§21). Hai lần lỗi thật trên báo
    # cáo ĐÃ GỬI nhà đầu tư (2026-08-02, 2026-08-10) đều lọt vì §21 chỉ là văn xuôi; §22 yêu cầu
    # chuyển thành code chặn. Fail-closed: cổng lỗi/thiếu dữ liệu ⇒ KHÔNG gửi.
    if args.skip_return_gate:
        print(f"⚠️  BỎ QUA cổng tỉ suất theo yêu cầu — lý do: {args.skip_return_gate}",
              file=sys.stderr)
    else:
        import report_return_gate
        try:
            rc = report_return_gate.run_gate(args.report_path, out=sys.stderr)
        except Exception as exc:
            print(f"❌ Cổng tỉ suất KHÔNG chạy được ({exc}) — KHÔNG gửi báo cáo (fail-closed). "
                  f"Sửa nguyên nhân, hoặc chạy lại với --skip-return-gate '<lý do>'.",
                  file=sys.stderr)
            sys.exit(3)
        if rc != 0:
            print("❌ Cổng tỉ suất CHẶN — báo cáo có tỉ suất per-position chưa cộng cổ tức hoặc "
                  "sai cơ sở giá vốn. KHÔNG gửi. Sửa số rồi chạy lại.", file=sys.stderr)
            sys.exit(3)

    if not os.path.exists(SECRETS_PATH):
        print(f"❌ Thiếu credential {SECRETS_PATH} — chưa thiết lập gửi email. "
              f"Cần user cung cấp Gmail App Password trước (xem docstring script này).",
              file=sys.stderr)
        sys.exit(2)

    cfg = json.load(open(SECRETS_PATH, encoding="utf-8"))
    from_email, app_password, to_email = cfg["from_email"], cfg["app_password"], cfg["to_email"]

    with open(args.report_path, encoding="utf-8") as f:
        md_body = f.read()

    fname = os.path.basename(args.report_path)
    if not args.subject:
        if "daily_report" in fname:
            _prefix = "[Daily report]"
        elif "weekly_report" in fname:
            _prefix = "[Weekly report]"
        elif "monthly_report" in fname:
            _prefix = "[Monthly report]"
        else:
            _prefix = "[Trading Report]"
        subject = f"{_prefix} {fname}"
    else:
        subject = args.subject

    title_line = md_body.split("\n", 1)[0]
    title = re.sub(r"^#+\s*", "", title_line).strip() or fname
    html_body = render_html(md_body, title, os.path.dirname(os.path.abspath(args.report_path)))

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    html_body, inline_images = _collect_inline_images(html_body)
    related = MIMEMultipart("related")
    related.attach(MIMEText(html_body, "html", "utf-8"))
    for image in inline_images:
        img = MIMEImage(image["data"], _subtype=image["subtype"])
        img.add_header("Content-ID", f"<{image['cid']}>")
        img.add_header("Content-Disposition", "inline",
                       filename=f"{image['cid']}.{image['subtype']}")
        related.attach(img)
    msg.attach(related)

    with open(args.report_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=fname)
    part["Content-Disposition"] = f'attachment; filename="{fname}"'
    msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, app_password)
        server.sendmail(from_email, [to_email], msg.as_string())

    print(f"✅ Đã gửi email '{subject}' tới {to_email}")


if __name__ == "__main__":
    main()
