#!/usr/bin/env python3
"""send_report_email.py <report.md> [--subject "..."] [--attach FILE]... [--attach-note "..."]

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

--attach / --attach-note (2026-10-11, user chọn gửi dashboard "độ phù hợp chiến lược" kèm EOD):
file đính kèm THÊM, CHỈ cho báo cáo DAILY (tên chứa `_daily_report_`) — với weekly/monthly gửi nhà
đầu tư hai cờ này bị BỎ QUA (dashboard là tài liệu chẩn đoán nội bộ). File đính kèm không thuộc
artifact được gate: thiếu/không đọc được ⇒ email VẪN gửi, thân email thêm một dòng nêu lỗi thật.
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
sys.path.insert(0, ROOT)
import wc_paths  # noqa: E402
# gốc cây neo theo marker `wc_env.sh` (wc_paths) — đếm cấp dirname SAI khi script chạy
# từ worktree `mike/agents/wt-*/bin/` (sự cố 2026-09-12, chặn báo cáo nhà đầu tư).
WC_ROOT = wc_paths.find_wc_root(__file__)
SECRETS_PATH = (
    os.environ.get("SEND_REPORT_SMTP_SECRET")
    or os.environ.get("REPORT_SMTP_SECRET_PATH")
    or os.path.join(WC_ROOT, "secrets", "gmail_smtp_app_password.json")
)

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


# Chốt "daily" dùng chung ý với check_report_cadence.sh (selfcheck so hai mẫu): đúng mẫu tên
# `_daily_report_<ngày>.md` VÀ không chứa weekly/monthly ở bất kỳ đâu trong tên.
_DAILY_RE = r"_daily_report_\d{4}-\d{2}-\d{2}\.md$"


def _is_daily(fname: str) -> bool:
    low = fname.lower()
    return bool(re.search(_DAILY_RE, fname)) and "weekly" not in low and "monthly" not in low


def _clean(s: str) -> str:
    """Chuỗi từ argv/OS có thể mang byte không phải UTF-8 (surrogate) ⇒ MIMEText ném UnicodeEncodeError."""
    return s.encode("utf-8", "surrogateescape").decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_path")
    ap.add_argument("--subject")
    ap.add_argument("--skip-return-gate", metavar="LÝ_DO",
                    help="BỎ QUA cổng tỉ suất (coding_guidelines §21) — chỉ dùng khi đã hiểu vì sao "
                         "cổng báo lệch; lý do được in ra và ghi vào email log")
    ap.add_argument("--attach", action="append", default=[], metavar="FILE",
                    help="file đính kèm thêm (lặp được) — CHỈ áp cho báo cáo daily")
    ap.add_argument("--attach-note", metavar="DÒNG",
                    help="một dòng thêm vào cuối thân email (vd lý do không có file kèm) — CHỈ daily")
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

    # File kèm thêm: đọc TRƯỚC khi dựng thân để dòng ghi chú nói đúng cái thực sự được kèm.
    # Phần THÊM này không bao giờ được làm rơi email: MỌI exception trong khối chỉ làm rơi phần thêm
    # (ghi lỗi thật ra stderr — §29), email + file .md artifact vẫn đi.
    extra_parts, attach_lines = [], []          # attach_lines: (loại, văn bản); loại "ok" = file đã kèm
    if (args.attach or args.attach_note) and not _is_daily(fname):
        print(f"⚠️  --attach/--attach-note chỉ áp cho báo cáo daily — BỎ QUA với {fname}",
              file=sys.stderr)
    else:
        try:
            for path in args.attach:
                aname = _clean(os.path.basename(path))
                try:
                    with open(path, "rb") as f:
                        data = f.read()
                except OSError as exc:
                    print(f"⚠️  Không đính kèm được {_clean(path)}: {_clean(str(exc))}", file=sys.stderr)
                    attach_lines.append(("err", f"📎 KHÔNG kèm được **{aname}**: {type(exc).__name__}: "
                                                f"{_clean(str(exc.strerror or exc))}"))
                    continue
                extra = MIMEApplication(data, Name=aname)
                extra["Content-Disposition"] = f'attachment; filename="{aname}"'
                extra_parts.append(extra)
                attach_lines.append(("ok", f"📎 Kèm theo: **{aname}** — tài liệu chẩn đoán nội bộ, mở bằng "
                                           f"trình duyệt; chỉ để mô tả, không phải tín hiệu giao dịch."))
            if args.attach_note:
                attach_lines.append(("note", f"📎 {_clean(args.attach_note)}"))
        except Exception as exc:  # noqa: BLE001 — chủ đích: lỗi phần thêm không được làm rơi email
            print(f"⚠️  Bỏ phần đính kèm thêm vì lỗi {type(exc).__name__}: {_clean(str(exc))}",
                  file=sys.stderr)
            extra_parts, attach_lines = [], []

    def build_msg(extras, lines):
        # Ghi chú chỉ vào THÂN email; file .md đính kèm bên dưới vẫn là artifact nguyên bản trên đĩa.
        body_md = md_body + ("\n\n---\n\n" + "\n\n".join(lines) + "\n" if lines else "")
        title_line = md_body.split("\n", 1)[0]
        title = re.sub(r"^#+\s*", "", title_line).strip() or fname
        html_body = render_html(body_md, title, os.path.dirname(os.path.abspath(args.report_path)))
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
        for extra in extras:
            msg.attach(extra)
        return msg

    def smtp_send(msg):
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, app_password)
            server.sendmail(from_email, [to_email], msg.as_string())

    try:
        smtp_send(build_msg(extra_parts, [t for _, t in attach_lines]))
    except (smtplib.SMTPException, OSError) as exc:
        if not extra_parts:
            raise
        # Lối lùi ĐÚNG MỘT lần: SMTP từ chối thư có file kèm thêm ⇒ gửi lại KHÔNG kèm chúng
        # (file .md artifact vẫn kèm). Lần hai lỗi ⇒ propagate như cũ (cổng thấy INCOMPLETE).
        real = f"{type(exc).__name__}: {_clean(str(exc))}"
        print(f"⚠️  SMTP từ chối thư có file kèm thêm ({real}) — thử lại một lần không kèm",
              file=sys.stderr)
        lines = [t for k, t in attach_lines if k != "ok"]
        lines.append(f"📎 Dashboard KHÔNG kèm hôm nay — SMTP từ chối thư có file kèm: {real}")
        smtp_send(build_msg([], lines))

    print(f"✅ Đã gửi email '{subject}' tới {to_email}")


if __name__ == "__main__":
    main()
