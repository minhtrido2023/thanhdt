#!/usr/bin/env python3
"""send_macro_note_email.py <body.md> --subject "..."

Gửi 1 ghi chú vĩ mô ngắn (không phải trading P&L report) qua email — dùng CHUNG credential
Gmail SMTP với send_report_email.py (secrets/gmail_smtp_app_password.json) nhưng KHÔNG qua
return-gate / HTML tear-sheet renderer của script đó (không áp dụng cho nội dung vĩ mô, không
có P&L để gate). Thân email = plain text (nội dung Markdown thô, dễ đọc trên mọi client).

Không tự đoán/tự tạo credential — fail rõ ràng (exit 2) nếu thiếu, giống send_report_email.py.
"""
import argparse
import json
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ROOT = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
SECRETS_PATH = (
    os.environ.get("SEND_REPORT_SMTP_SECRET")
    or os.environ.get("REPORT_SMTP_SECRET_PATH")
    or os.path.join(WC_ROOT, "secrets", "gmail_smtp_app_password.json")
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("body_path")
    ap.add_argument("--subject", required=True)
    args = ap.parse_args()

    if not os.path.exists(SECRETS_PATH):
        print(f"LỖI: thiếu credential SMTP tại {SECRETS_PATH} — không gửi email.", file=sys.stderr)
        sys.exit(2)
    with open(SECRETS_PATH) as f:
        cred = json.load(f)
    for key in ("from_email", "app_password", "to_email"):
        if not cred.get(key):
            print(f"LỖI: credential thiếu trường '{key}'.", file=sys.stderr)
            sys.exit(2)

    if not os.path.exists(args.body_path):
        print(f"LỖI: không tìm thấy file nội dung {args.body_path}.", file=sys.stderr)
        sys.exit(2)
    with open(args.body_path) as f:
        body = f.read()

    msg = MIMEMultipart()
    msg["From"] = cred["from_email"]
    msg["To"] = cred["to_email"]
    msg["Subject"] = args.subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(cred["from_email"], cred["app_password"])
        server.sendmail(cred["from_email"], cred["to_email"], msg.as_string())

    print(f"OK: đã gửi email '{args.subject}' tới {cred['to_email']}.")


if __name__ == "__main__":
    main()
