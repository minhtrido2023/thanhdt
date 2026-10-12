#!/usr/bin/env python3
"""Selfcheck: dashboard "độ phù hợp chiến lược" đi kèm email báo cáo DAILY (job Taylor_20261011_151151).

Phủ 4 mắt xích: send_report_email.py (--attach/--attach-note) · report_delivery_gate.py (chuyển
tiếp, sổ/sha không đổi) · eod_trading_report.sh (_strategy_fit_attach_args: sinh có timeout, dùng
lại, lỗi không chặn) · check_report_cadence.sh (gửi bù: kèm file của đúng ngày, không sinh lại).

KHÔNG gửi email thật: send_report_email.py THẬT chạy qua một wrapper thay `smtplib.SMTP` bằng lớp
giả ghi message ra file, với credential giả (`SEND_REPORT_SMTP_SECRET`, địa chỉ .invalid) — kể cả
wrapper hỏng thì đăng nhập SMTP thật cũng không thể thành công. Cổng giao hàng chạy in-process với
`--state` tạm + `LEGACY_EMAIL_STATE` trỏ ra thư mục tạm (cùng cách report_delivery_gate_selfcheck).
Chạy lại dưới `env -u TZ` và `TZ=America/New_York`.
"""
import email
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

BIN = Path(__file__).resolve().parent
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
TODAY = datetime.now(ICT).strftime("%Y-%m-%d")
OLD = (datetime.now(ICT) - timedelta(days=9)).strftime("%Y-%m-%d")
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"\n        {str(detail)[:600]}" if not ok else ""))


def block(src: str, begin: str, end: str) -> str:
    if src.count(begin) != 1 or src.count(end) != 1:
        raise SystemExit(f"FATAL: marker {begin}/{end} không xuất hiện đúng 1 lần")
    return src[src.index(begin):src.index(end)]


WRAPPER = r'''
import json, os, runpy, smtplib, sys
import email.mime.application as _ma
_calls = [0]
class _SMTP:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a):
        # Máy chủ ĐÃ nhận thư (sendmail trả về) rồi lỗi lúc QUIT/đóng kết nối. Chỉ dùng lớp lỗi mà
        # smtplib.SMTP.__exit__ thật KHÔNG tự nuốt (nó nuốt SMTPServerDisconnected):
        #   =1 SMTPResponseException (QUIT trả mã ≠ 221) · =2 OSError từ close()
        if a[0] is None and os.environ.get("FAKE_SMTP_QUIT_FAIL") == "1":
            raise smtplib.SMTPResponseException(421, b"fake QUIT refused")
        if a[0] is None and os.environ.get("FAKE_SMTP_QUIT_FAIL") == "2":
            raise OSError("fake close() error")
        return False
    def starttls(self): pass
    def login(self, *a): pass
    def sendmail(self, frm, to, raw):
        _calls[0] += 1
        with open(os.environ["FAKE_SMTP_ATTEMPTS"], "a") as f:
            f.write("x\n")
        if _calls[0] <= int(os.environ.get("FAKE_SMTP_FAIL", "0")):
            raise smtplib.SMTPDataError(552, b"5.3.4 message too large")
        with open(os.environ["FAKE_SMTP_OUT"], "a", encoding="utf-8") as f:
            f.write(json.dumps({"from": frm, "to": to, "raw": raw}) + "\n")
smtplib.SMTP = _SMTP
_orig_init = _ma.MIMEApplication.__init__
def _boom_init(self, data, *a, **k):
    if str(k.get("Name", "")).startswith("boom_"):
        raise ValueError("mime boom")
    _orig_init(self, data, *a, **k)
_ma.MIMEApplication.__init__ = _boom_init
real = os.environ["REAL_EMAIL_SCRIPT"]
sys.argv = [real] + sys.argv[1:]
runpy.run_path(real, run_name="__main__")
'''


class Sandbox:
    def __init__(self, td: Path):
        self.td = td
        self.wrapper = td / "fake_smtp_email.py"
        self.wrapper.write_text(WRAPPER, encoding="utf-8")
        self.secret = td / "secret.json"
        self.secret.write_text(json.dumps({"from_email": "from@selfcheck.invalid",
                                           "app_password": "x", "to_email": "to@selfcheck.invalid"}))
        self.out = td / "smtp_out.jsonl"
        self.env = dict(os.environ, SEND_REPORT_SMTP_SECRET=str(self.secret),
                        FAKE_SMTP_OUT=str(self.out), FAKE_SMTP_ATTEMPTS=str(td / "attempts"),
                        REAL_EMAIL_SCRIPT=str(BIN / "send_report_email.py"))

    def sent(self):
        if not self.out.exists():
            return []
        return [json.loads(ln) for ln in self.out.read_text(encoding="utf-8").splitlines()]

    def attempts(self):
        f = self.td / "attempts"
        return len(f.read_text().splitlines()) if f.exists() else 0

    def send(self, report: Path, *extra, fail=0, quit_fail=False):
        """Chạy send_report_email.py thật (SMTP giả; `fail`=số lần sendmail đầu bị từ chối).
        → (rc, stderr, message mới nhất | None). `extra` nhận cả bytes (argv không phải UTF-8)."""
        n = len(self.sent())
        env = dict(self.env, FAKE_SMTP_FAIL=str(fail), FAKE_SMTP_QUIT_FAIL="2" if quit_fail == "oserror" else "1" if quit_fail else "0")
        p = subprocess.run([sys.executable, str(self.wrapper), str(report),
                            "--skip-return-gate", "selfcheck",
                            *[a if isinstance(a, bytes) else str(a) for a in extra]],
                           env=env, capture_output=True)
        new = self.sent()[n:]
        return (p.returncode, p.stderr.decode("utf-8", "replace"),
                (new[-1] if len(new) == 1 else None))


def parts_of(sent):
    msg = email.message_from_string(sent["raw"])
    atts, body = {}, ""
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            atts[part.get_filename()] = part.get_payload(decode=True)
        elif part.get_content_type() == "text/html":
            raw = part.get_payload(decode=True)
            try:
                body = raw.decode("utf-8")
            except UnicodeDecodeError:               # email gửi đi mang UTF-8 hỏng = lỗi, không phải crash selfcheck
                body = raw.decode("utf-8", "replace") + "<<UTF8-HỎNG>>"
    return atts, body


def part_email(td: Path):
    sb = Sandbox(td)
    daily = td / f"SpaceX_daily_report_{TODAY}.md"
    daily.write_text("# Báo cáo ngày\n\nNội dung.\n", encoding="utf-8")
    dash = td / f"strategy_fit_{TODAY}.html"
    dash.write_bytes("<html><body>ô chẩn đoán</body></html>".encode("utf-8"))
    md_bytes = daily.read_bytes()

    rc, err, s = sb.send(daily)
    atts, body = parts_of(s) if s else ({}, "")
    check("E1 daily KHÔNG cờ: gửi y như cũ (1 file .md, không dòng 📎)",
          rc == 0 and list(atts) == [daily.name] and "📎" not in body, (rc, err, list(atts)))
    base_body = body

    rc, err, s = sb.send(daily, "--attach", dash)
    atts, body = parts_of(s) if s else ({}, "")
    check("E2 daily + --attach: có file HTML kèm, đúng từng byte",
          rc == 0 and atts.get(dash.name) == dash.read_bytes(), (rc, err, list(atts)))
    check("E2b file .md kèm vẫn là artifact nguyên bản (ghi chú chỉ vào thân)",
          atts.get(daily.name) == md_bytes and daily.read_bytes() == md_bytes)
    check("E2c thân có đúng MỘT dòng 📎 nói có file kèm và nó là gì",
          body.count("📎") == 1 and "Kèm theo" in body and dash.name in body
          and "chẩn đoán nội bộ" in body, body[-500:])
    check("E2d chỉ gửi tới đúng to_email của credential", s and s["to"] == ["to@selfcheck.invalid"])
    added = [ln for ln in body.splitlines() if ln not in base_body.splitlines()]
    lost = [ln for ln in base_body.splitlines() if ln not in body.splitlines()]
    check("E2e thân chỉ THÊM đúng 1 đường kẻ + 1 dòng ghi chú, không mất/đổi dòng nào của báo cáo",
          not lost and len(added) == 2 and added[0].startswith("<hr") and "📎" in added[1], (added, lost))

    missing = td / "khong_co.html"
    rc, err, s = sb.send(daily, "--attach", missing)
    atts, body = parts_of(s) if s else ({}, "")
    check("E3 file kèm KHÔNG tồn tại: email VẪN gửi, không kèm, một dòng mang lỗi thật",
          rc == 0 and list(atts) == [daily.name] and body.count("📎") == 1
          and "KHÔNG kèm được" in body and "FileNotFoundError" in body and missing.name in body,
          (rc, err, body[-400:]))

    rc, err, s = sb.send(daily, "--attach", td)          # thư mục: lỗi đọc khác FileNotFound
    atts, body = parts_of(s) if s else ({}, "")
    check("E3b file kèm không đọc được (là thư mục): vẫn gửi, lỗi thật IsADirectoryError",
          rc == 0 and list(atts) == [daily.name] and "IsADirectoryError" in body, (rc, err))

    note = "Dashboard độ phù hợp chiến lược KHÔNG kèm hôm nay — sinh lỗi: rc=1 — Boom thật"
    rc, err, s = sb.send(daily, "--attach-note", note)
    atts, body = parts_of(s) if s else ({}, "")
    check("E4 --attach-note: đúng MỘT dòng, nguyên văn lỗi, không file kèm thêm",
          rc == 0 and list(atts) == [daily.name] and body.count("📎") == 1 and note in body,
          (rc, err, body[-400:]))

    dash2 = td / "khac.html"
    dash2.write_bytes(b"<html>2</html>")
    rc, err, s = sb.send(daily, "--attach", dash, "--attach", dash2)
    atts, body = parts_of(s) if s else ({}, "")
    check("E5 --attach lặp được: kèm đủ 2 file", rc == 0 and set(atts) == {daily.name, dash.name, dash2.name})

    for kind, name in (("weekly", "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"),
                       ("monthly", "SpaceX_monthly_report_2026-09.md"),
                       ("khác", "SpaceX_special_report.md"),
                       ("N3 tên nhân tạo 1", "X_daily_report_weekly.md"),
                       ("N3 tên nhân tạo 2", "Fund_weekly_daily_report_2026-10-09.md"),
                       ("N3 tên nhân tạo 3", "SpaceX_weekly_report_2026-10-05_daily_report_fix.md")):
        rep = td / name
        rep.write_text("# Báo cáo nhà đầu tư\n\nNội dung.\n", encoding="utf-8")
        rc, err, s = sb.send(rep, "--attach", dash, "--attach-note", note)
        atts, body = parts_of(s) if s else ({}, "")
        check(f"E6 {kind}: --attach/--attach-note bị BỎ QUA — không file HTML, không dòng 📎, vẫn gửi",
              rc == 0 and list(atts) == [name] and "📎" not in body and "strategy_fit" not in s["raw"]
              and "BỎ QUA" in err, (rc, err, list(atts)))

    # --- B1b: argv không phải UTF-8 / exception phần thêm không được làm rơi email
    rc, err, s = sb.send(daily, "--attach-note", b"Dashboard l\xe1\xbb\xa0i \xe1\xbb")   # cắt giữa ký tự + byte rác
    atts, body = parts_of(s) if s else ({}, "")
    check("E7 --attach-note mang byte KHÔNG phải UTF-8 ⇒ email VẪN gửi, có đúng 1 dòng 📎",
          rc == 0 and s is not None and body.count("📎") == 1 and "Dashboard l" in body
          and "<<UTF8-HỎNG>>" not in body, (rc, err))
    rc, err, s = sb.send(daily, "--attach", td / "boom_x.html")
    boom = td / "boom_x.html"
    boom.write_bytes(b"<html>b</html>")
    rc, err, s = sb.send(daily, "--attach", boom, "--attach-note", "ghi chú")
    atts, body = parts_of(s) if s else ({}, "")
    check("E8 exception BẤT KỲ trong khối file-kèm (ValueError) ⇒ email VẪN gửi, rơi phần thêm, lỗi thật ra stderr",
          rc == 0 and s is not None and list(atts) == [daily.name] and "📎" not in body
          and "ValueError" in err and "mime boom" in err, (rc, err, list(atts)))

    # --- N4: lối lùi khi SMTP từ chối thư có file kèm
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, "--attach", dash, fail=1)
    atts, body = parts_of(s) if s else ({}, "")
    check("E9 SMTP từ chối lần 1 thư có file HTML ⇒ ĐÚNG 1 email đi ở lần 2, không kèm HTML, thân nêu lỗi thật",
          rc == 0 and s is not None and sb.attempts() - a0 == 2 and list(atts) == [daily.name]
          and "SMTPDataError" in body and "KHÔNG kèm" in body and body.count("📎") == 1
          and "thử lại một lần" in err, (rc, err, sb.attempts() - a0, list(atts)))
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, "--attach", dash, fail=2)
    check("E10 SMTP từ chối CẢ HAI lần ⇒ lỗi như cũ (rc≠0), không email, đúng 2 lần thử (không vòng lặp)",
          rc != 0 and s is None and sb.attempts() - a0 == 2, (rc, sb.attempts() - a0, err[-300:]))
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, fail=1)
    check("E11 không --attach, SMTP từ chối ⇒ hành vi cũ: rc≠0, đúng 1 lần thử, không lùi",
          rc != 0 and s is None and sb.attempts() - a0 == 1, (rc, sb.attempts() - a0))
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, "--attach", td / "khong_co2.html", fail=1)
    check("E12 --attach nhưng không file nào kèm được ⇒ không có gì để bỏ ⇒ không lùi (1 lần thử)",
          rc != 0 and sb.attempts() - a0 == 1, (rc, sb.attempts() - a0))

    # --- gửi trùng: SMTP ĐÃ nhận thư (sendmail trả về) rồi mới lỗi lúc đóng kết nối
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, "--attach", dash, quit_fail=True)
    atts, body = parts_of(s) if s else ({}, "")
    check("E13 có --attach, sendmail OK rồi lỗi lúc đóng kết nối ⇒ ĐÚNG 1 lần gửi (không vào lối lùi), "
          "rc=0, thư đã đi vẫn kèm HTML, lỗi thật ra stderr",
          rc == 0 and s is not None and sb.attempts() - a0 == 1 and set(atts) == {daily.name, dash.name}
          and "KHÔNG kèm" not in body and "SMTPResponseException" in err and "fake QUIT" in err
          and "thử lại một lần" not in err, (rc, sb.attempts() - a0, list(atts), err[-300:]))
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, quit_fail=True)
    check("E14 không --attach, sendmail OK rồi lỗi lúc đóng kết nối ⇒ rc=0 (cổng không retry gửi lần hai), đúng 1 lần gửi",
          rc == 0 and s is not None and sb.attempts() - a0 == 1 and "SMTPResponseException" in err,
          (rc, sb.attempts() - a0, err[-300:]))
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, "--attach", dash, quit_fail="oserror")
    check("E14b sendmail OK rồi close() ném OSError ⇒ rc=0, đúng 1 lần gửi (không gửi trùng), lỗi thật ra stderr",
          rc == 0 and s is not None and sb.attempts() - a0 == 1 and "OSError" in err and "fake close" in err,
          (rc, sb.attempts() - a0, err[-300:]))
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, "--attach", dash, fail=1, quit_fail=True)
    atts, body = parts_of(s) if s else ({}, "")
    check("E15 lần 1 bị TỪ CHỐI thật (trước khi nhận) + lần 2 nhận rồi lỗi đóng ⇒ lối lùi vẫn chạy, đúng 1 email đi, 2 lần thử",
          rc == 0 and s is not None and sb.attempts() - a0 == 2 and list(atts) == [daily.name]
          and "KHÔNG kèm" in body, (rc, sb.attempts() - a0, list(atts), err[-300:]))
    a0 = sb.attempts()
    rc, err, s = sb.send(daily, "--attach", dash, fail=2, quit_fail=True)
    check("E16 sendmail bị từ chối cả hai lần (chưa hề nhận) ⇒ vẫn là THẤT BẠI rc≠0 — nhánh mới không nuốt lỗi gửi thật",
          rc != 0 and s is None and sb.attempts() - a0 == 2, (rc, sb.attempts() - a0, err[-300:]))


GATE_RUNNER = r'''
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("rdg_cli", os.environ["RDG_PATH"])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.LEGACY_EMAIL_STATE = Path(os.environ["RDG_LEGACY"])     # KHÔNG ghi sổ legacy canonical
sys.argv = ["report_delivery_gate.py"] + sys.argv[1:]
raise SystemExit(m.main())                                # đi qua argparse + main() như CLI thật
'''


def gate_cli(td: Path, sb, report: Path, *extra):
    """report_delivery_gate.py qua SUBPROCESS + main() (CLI thật). → (rc, out, state dict)."""
    runner = td / "gate_runner.py"
    runner.write_text(GATE_RUNNER, encoding="utf-8")
    notify = td / "notify.sh"
    notify.write_text("#!/bin/sh\necho \"$2\" >> \"$(dirname \"$0\")/notify_calls\"\n")
    notify.chmod(0o755)
    state = td / "state_cli.json"
    env = dict(sb.env, RDG_PATH=str(BIN / "report_delivery_gate.py"), RDG_LEGACY=str(td / "legacy_cli.json"))
    p = subprocess.run([sys.executable, str(runner), str(report), "--state", str(state), "--topic",
                        "trading_report", "--notify-script", str(notify), "--email-script", str(sb.wrapper),
                        "--skip-validation", *[a if isinstance(a, bytes) else str(a) for a in extra]],
                       env=env, capture_output=True)
    st = json.loads(state.read_text()) if state.exists() else {}
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace"), st


def part_cli(td: Path):
    sb = Sandbox(td)
    dash = td / f"strategy_fit_{TODAY}.html"
    dash.write_bytes(b"<html>cli</html>")
    daily = td / f"SpaceX_daily_report_{TODAY}.md"
    daily.write_text("# Báo cáo ngày\n\nNội dung.\n", encoding="utf-8")
    rc, out, st = gate_cli(td, sb, daily, "--attach", dash, "--attach-note", "ghi chú CLI")
    sent = sb.sent()
    atts, body = parts_of(sent[-1]) if sent else ({}, "")
    check("C1 CLI (subprocess, main()) với --attach/--attach-note ⇒ COMPLETE, email có HTML kèm + ghi chú",
          rc == 0 and len(sent) == 1 and atts.get(dash.name) == b"<html>cli</html>" and "ghi chú CLI" in body,
          (rc, out[-300:], list(atts)))
    rec = st.get("reports", {}).get(daily.name, {})
    check("C2 CLI: sổ có bằng chứng email + discord khớp sha256 file .md, không dấu vết file kèm",
          rec.get("email", {}).get("sha256") == rec.get("sha256") == rec.get("discord", {}).get("sha256")
          and "strategy_fit" not in json.dumps(rec), rec)


def part_gate(td: Path):
    spec = importlib.util.spec_from_file_location("rdg_sf", BIN / "report_delivery_gate.py")
    rdg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rdg)
    old_legacy = rdg.LEGACY_EMAIL_STATE
    rdg.LEGACY_EMAIL_STATE = td / "legacy.json"
    sb = Sandbox(td)
    notify = td / "notify.sh"
    notify.write_text("#!/bin/sh\necho \"$2\" >> \"$(dirname \"$0\")/notify_calls\"\n")
    notify.chmod(0o755)
    state = td / "state.json"
    dash = td / f"strategy_fit_{TODAY}.html"
    dash.write_bytes(b"<html>dash</html>")
    old_env = dict(os.environ)
    os.environ.update(sb.env)
    try:
        daily = td / f"ZaloPay_daily_report_{TODAY}.md"
        daily.write_text("# Báo cáo ngày ZP\n\nNội dung.\n", encoding="utf-8")
        sha = rdg.digest(daily)
        rc = rdg.deliver(daily, state, "trading_report", notify, sb.wrapper, True, (dash,), None)
        sent = sb.sent()
        atts, body = parts_of(sent[-1]) if sent else ({}, "")
        check("G1 cổng → email THẬT (SMTP giả): COMPLETE và email daily có file HTML kèm",
              rc == 0 and len(sent) == 1 and atts.get(dash.name) == b"<html>dash</html>"
              and daily.name in atts, (rc, list(atts)))
        rec = json.loads(state.read_text())["reports"][daily.name]
        check("G2 sổ giao hàng không đổi hình dạng: sha = sha256(file .md), không khoá nào về file kèm",
              rec["sha256"] == sha == rec["email"]["sha256"] == rec["discord"]["sha256"]
              and set(rec) == {"path", "sha256", "created_at", "delivered_by_tree",
                               "artifact_validated_at", "discord", "email", "completed_at"}
              and set(rec["email"]) == {"status", "delivered_at", "sha256"}
              and "strategy_fit" not in json.dumps(rec), rec)
        rc = rdg.deliver(daily, state, "trading_report", notify, sb.wrapper, True, (dash,), None)
        check("G3 chạy lại có --attach: COMPLETE idempotent, KHÔNG gửi lại kênh nào",
              rc == 0 and len(sb.sent()) == 1
              and (td / "notify_calls").read_text().count("trading_report") == 1)

        data = json.loads(state.read_text())
        data["reports"][daily.name].pop("email")
        state.write_text(json.dumps(data))
        dash.unlink()                                   # gửi bù khi dashboard đã mất
        rc = rdg.deliver(daily, state, "trading_report", notify, sb.wrapper, True, (dash,), None)
        sent = sb.sent()
        atts, body = parts_of(sent[-1])
        check("G4 retry kênh email còn thiếu, file kèm đã mất: vẫn COMPLETE, không gửi lại Discord",
              rc == 0 and len(sent) == 2 and list(atts) == [daily.name] and "KHÔNG kèm được" in body
              and (td / "notify_calls").read_text().count("trading_report") == 1, (rc, list(atts)))

        # Lệnh gọi email khi KHÔNG có tham số kèm phải y nguyên như trước thay đổi này.
        calls = []
        real_run = rdg.run_checked
        rdg.run_checked = calls.append
        try:
            rep = td / "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
            rep.write_text("# w\n", encoding="utf-8")
            rdg.deliver(rep, state, "trading_report", notify, sb.wrapper, True)
            rep2 = td / f"SpaceX_daily_report_{TODAY}.md"
            rep2.write_text("# d\n", encoding="utf-8")
            rdg.deliver(rep2, state, "trading_report", notify, sb.wrapper, True, (td / "a.html",), "ghi chú")
        finally:
            rdg.run_checked = real_run
        w_email, d_email = calls[1], calls[3]
        check("G5 không --attach ⇒ lệnh email y nguyên (kết thúc ở lý do skip-return-gate)",
              w_email[2:4] == [str(rep.resolve()), "--skip-return-gate"] and len(w_email) == 5, w_email)
        check("G6 có --attach/--attach-note ⇒ chuyển tiếp nguyên văn sau các tham số cũ",
              d_email[5:] == ["--attach", str(td / "a.html"), "--attach-note", "ghi chú"]
              and d_email[:5][3] == "--skip-return-gate", d_email)
    finally:
        rdg.LEGACY_EMAIL_STATE = old_legacy
        os.environ.clear()
        os.environ.update(old_env)


FAKE_GEN = r'''
import os, sys, time
out = sys.argv[sys.argv.index("--out-dir") + 1]
with open(os.path.join(os.environ["FAKE_ROOT"], "gen_calls"), "a") as f:
    f.write("x\n")
mode = os.environ.get("FAKE_GEN_MODE", "ok")
if mode == "fail":
    print("[ô] edge_ic LỖI: thiếu file")
    print("Boom thật: không dựng được ô dữ liệu nào", file=sys.stderr)
    sys.exit(1)
if mode in ("fail_long", "fail_garbage"):
    pad = "a" * int(os.environ.get("FAKE_PAD", "0"))
    if mode == "fail_long":
        line = pad + "Không dựng được ô dữ liệu nào vì thiếu tệp đầu vào, " * 12
        sys.stderr.buffer.write(line.encode("utf-8") + b"\n")
    else:
        sys.stderr.buffer.write(b"Loi " + b"\xff\xfe\xe1\xbb" * 90 + b"\n")
    sys.exit(1)
if mode == "sleep":
    time.sleep(30)
if mode == "silent_nofile":
    sys.exit(0)
os.makedirs(out, exist_ok=True)
p = os.path.join(out, "strategy_fit_%s.html" % os.environ["FAKE_DATE"])
open(p, "w").write("<html>fake</html>")
print(p)
'''


def run_eod_fn(td: Path, plan_date: str, mode: str, tz, timeout_s="120", extra_env=None, chain=None):
    """Chạy NGUYÊN khối _strategy_fit_attach_args trích từ eod_trading_report.sh. → (args, rc, giây, n_gen)."""
    src = block((BIN / "eod_trading_report.sh").read_text(encoding="utf-8"),
                "# STRATEGY_FIT_BEGIN", "# STRATEGY_FIT_END")
    root = td
    (root / "bin").mkdir(exist_ok=True)
    (root / "bin" / "strategy_fit_dashboard.py").write_text(FAKE_GEN, encoding="utf-8")
    script = ("set -uo pipefail\n" + src + "\n_strategy_fit_attach_args\nrc=$?\n"
              "gate_args=(x)\ngate_args+=(\"${STRATEGY_FIT_ARGS[@]}\")\n"       # y như _deliver_eod, dưới set -u
              "printf 'RC=%s\\n' \"$rc\"\nprintf 'ARG=%s\\n' \"${STRATEGY_FIT_ARGS[@]}\"\n")
    if chain:      # y như _deliver_eod: mảng tham số đi thẳng vào lệnh cổng (CLI thật)
        script += chain
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    if tz:
        env["TZ"] = tz
    env.update(ROOT=str(root), PLAN_DATE=plan_date, DNA_PYEXE=sys.executable, FAKE_ROOT=str(root),
               FAKE_GEN_MODE=mode, FAKE_DATE=plan_date, STRATEGY_FIT_TIMEOUT_S=timeout_s)
    env.update(extra_env or {})
    t0 = time.time()
    p = subprocess.run(["bash", "-c", script], env=env, capture_output=True)
    secs = time.time() - t0
    p.stdout, p.stderr = p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
    args = re.findall(r"^ARG=(.*)$", p.stdout, re.M)
    args = [a for a in args if a != ""] if args != [""] else []
    rc = re.search(r"^RC=(\d+)$", p.stdout, re.M)
    calls = root / "gen_calls"
    n = len(calls.read_text().splitlines()) if calls.exists() else 0
    return args, (int(rc.group(1)) if rc else None), secs, n, p.stdout + p.stderr


def part_eod(td0: Path):
    # Pacific/Kiritimati (UTC+14) và Etc/GMT+12 (UTC-12): ở BẤT KỲ giờ nào trong ngày, ít nhất một trong
    # hai lệch NGÀY LỊCH so với ICT ⇒ `date` mất neo TZ luôn bị bắt (không còn tuỳ giờ chạy).
    for tz in (None, "America/New_York", "Asia/Ho_Chi_Minh", "Pacific/Kiritimati", "Etc/GMT+12"):
        tag = f"[TZ={tz or 'unset'}]"
        td = Path(tempfile.mkdtemp(dir=td0))
        dash = td / "reports" / "dashboard" / f"strategy_fit_{TODAY}.html"
        args, rc, _, n, log = run_eod_fn(td, TODAY, "ok", tz)
        check(f"D1 {tag} hôm nay, chưa có file ⇒ SINH rồi --attach đúng đường dẫn",
              rc == 0 and args == ["--attach", str(dash)] and n == 1 and dash.exists(), (args, rc, n, log))
        args, rc, _, n, log = run_eod_fn(td, TODAY, "fail", tz)
        check(f"D2 {tag} account sau: file hôm nay đã có ⇒ DÙNG LẠI, không sinh lần hai",
              rc == 0 and args == ["--attach", str(dash)] and n == 1, (args, rc, n))

        # N1: file "hôm nay" nhưng mtime cũ ⇒ SINH LẠI (không dùng số liệu trước lần publish)
        td = Path(tempfile.mkdtemp(dir=td0))
        dash = td / "reports" / "dashboard" / f"strategy_fit_{TODAY}.html"
        dash.parent.mkdir(parents=True)
        dash.write_text("<html>cu</html>")
        old_t = time.time() - 7200
        os.utime(dash, (old_t, old_t))
        args, rc, _, n, log = run_eod_fn(td, TODAY, "ok", tz)
        check(f"D1b {tag} file hôm nay nhưng mtime 2 giờ trước ⇒ SINH LẠI (n=1) và file được làm mới",
              rc == 0 and args == ["--attach", str(dash)] and n == 1 and dash.read_text() == "<html>fake</html>",
              (args, n, dash.read_text()))
        dash.write_text("<html>cu</html>")
        os.utime(dash, (old_t, old_t))
        args, rc, _, n2, log = run_eod_fn(td, TODAY, "fail", tz)
        check(f"D1c {tag} file hôm nay mtime cũ + sinh lại LỖI ⇒ KHÔNG kèm file cũ, ghi chú mang lỗi thật",
              rc == 0 and len(args) == 2 and args[0] == "--attach-note" and "Boom thật" in args[1], (args, log))
        # N2(i): file rỗng 0 byte, mtime mới
        td = Path(tempfile.mkdtemp(dir=td0))
        dash = td / "reports" / "dashboard" / f"strategy_fit_{TODAY}.html"
        dash.parent.mkdir(parents=True)
        dash.write_bytes(b"")
        args, rc, _, n, log = run_eod_fn(td, TODAY, "ok", tz)
        check(f"D1d {tag} file hôm nay RỖNG 0 byte (mới) ⇒ coi như không có: sinh lại rồi kèm",
              rc == 0 and args == ["--attach", str(dash)] and n == 1 and dash.stat().st_size > 0, (args, n))
        dash.write_bytes(b"")
        os.utime(dash, (old_t, old_t))
        args, rc, _, n, log = run_eod_fn(td, TODAY, "silent_nofile", tz)
        check(f"D4b {tag} file rỗng + script rc=0 không ghi gì ⇒ ghi chú, KHÔNG kèm file 0 byte",
              rc == 0 and len(args) == 2 and args[0] == "--attach-note", (args, log))
        td = Path(tempfile.mkdtemp(dir=td0))
        dash = td / "reports" / "dashboard" / f"strategy_fit_{OLD}.html"
        dash.parent.mkdir(parents=True)
        dash.write_bytes(b"")
        args, rc, _, n, log = run_eod_fn(td, OLD, "ok", tz)
        check(f"D6b {tag} ngày CŨ + file rỗng 0 byte ⇒ không kèm, không sinh lại", rc == 0 and args == [] and n == 0, (args, n))

        td = Path(tempfile.mkdtemp(dir=td0))
        args, rc, _, n, log = run_eod_fn(td, TODAY, "fail", tz)
        check(f"D3 {tag} sinh LỖI ⇒ hàm vẫn rc=0, không --attach, một --attach-note mang lỗi thật",
              rc == 0 and len(args) == 2 and args[0] == "--attach-note" and "rc=1" in args[1]
              and "Boom thật: không dựng được ô dữ liệu nào" in args[1] and n == 1, (args, rc, log))

        td = Path(tempfile.mkdtemp(dir=td0))
        args, rc, secs, n, log = run_eod_fn(td, TODAY, "silent_nofile", tz)
        check(f"D4 {tag} script rc=0 nhưng KHÔNG ra file ⇒ ghi chú, không --attach file ma",
              rc == 0 and len(args) == 2 and args[0] == "--attach-note" and "rc=0" in args[1], (args, log))

        td = Path(tempfile.mkdtemp(dir=td0))
        args, rc, _, n, log = run_eod_fn(td, OLD, "ok", tz)
        check(f"D5 {tag} ngày CŨ, không có file ⇒ KHÔNG sinh lại, không tham số nào (gửi không kèm)",
              rc == 0 and args == [] and n == 0, (args, n, log))
        old_dash = td / "reports" / "dashboard" / f"strategy_fit_{OLD}.html"
        old_dash.parent.mkdir(parents=True, exist_ok=True)
        old_dash.write_text("<html>cũ</html>")
        args, rc, _, n, log = run_eod_fn(td, OLD, "ok", tz)
        check(f"D6 {tag} ngày CŨ, file ngày đó còn ⇒ kèm file đó, không sinh lại",
              rc == 0 and args == ["--attach", str(old_dash)] and n == 0, (args, n))

    # B1c: dòng stderr cuối tiếng Việt > 300 byte, điểm cắt lệch k=0..3 byte, và stderr mang byte rác
    # ⇒ đi hết chuỗi eod-fn → CLI cổng → send_report_email: COMPLETE, đúng 1 email, sổ có bằng chứng email.
    for label, mode, k in [(f"k={k}", "fail_long", k) for k in range(4)] + [("byte rác", "fail_garbage", 0)]:
        td = Path(tempfile.mkdtemp(dir=td0))
        sb = Sandbox(td)
        report = td / f"SpaceX_daily_report_{TODAY}.md"
        report.write_text("# Báo cáo ngày\n\nNội dung.\n", encoding="utf-8")
        (td / "gate_runner.py").write_text(GATE_RUNNER, encoding="utf-8")
        notify = td / "notify.sh"
        notify.write_text("#!/bin/sh\ntrue\n")
        notify.chmod(0o755)
        state = td / "state_chain.json"
        chain = ('"$PY_EXE" "$TD/gate_runner.py" "$TD/' + report.name + '" --state "$TD/state_chain.json" '
                 '--topic trading_report --notify-script "$TD/notify.sh" --email-script "$TD/fake_smtp_email.py" '
                 '--skip-validation "${STRATEGY_FIT_ARGS[@]}"\nprintf \'CHAIN_RC=%s\\n\' "$?"\n')
        args, rc, _, n, log = run_eod_fn(
            td, TODAY, mode, None, chain=chain,
            extra_env=dict({k: sb.env[k] for k in sb.env if k.startswith(('FAKE_SMTP', 'SEND_REPORT', 'REAL_EMAIL'))}, FAKE_PAD=str(k), TD=str(td), PY_EXE=sys.executable,
                           RDG_PATH=str(BIN / "report_delivery_gate.py"), RDG_LEGACY=str(td / "legacy.json")))
        crc = re.search(r"^CHAIN_RC=(\d+)$", log, re.M)
        sent = sb.sent()
        atts, body = parts_of(sent[-1]) if sent else ({}, "")
        rec = json.loads(state.read_text())["reports"].get(report.name, {}) if state.exists() else {}
        check(f"B1c [{label}] lỗi sinh dashboard dài/UTF-8 hỏng ⇒ cổng COMPLETE, đúng 1 email, sổ có bằng chứng email",
              n == 1 and crc and crc.group(1) == "0" and len(sent) == 1 and "KHÔNG kèm hôm nay" in body
              and (mode == "fail_garbage" or "\ufffd" not in body)      # cắt theo KÝ TỰ: không ký tự nào bị vỡ
              and rec.get("email", {}).get("status") == "delivered" and "completed_at" in rec,
              (crc and crc.group(1), len(sent), log[-500:]))

    td = Path(tempfile.mkdtemp(dir=td0))
    args, rc, secs, n, log = run_eod_fn(td, TODAY, "sleep", None, timeout_s="1")
    check("D7 sinh QUÁ timeout ⇒ bị dừng (không chờ 30s), rc=0, ghi chú nói quá giờ",
          rc == 0 and secs < 12 and len(args) == 2 and args[0] == "--attach-note"
          and "quá 1 giây" in args[1] and "rc=124" in args[1], (args, rc, round(secs, 1), log))

    eod = (BIN / "eod_trading_report.sh").read_text(encoding="utf-8")
    body = eod[eod.index("_deliver_eod() {"):eod.index("gate_out=\"$(python3")]
    check("D8 _deliver_eod (dùng cho CẢ 4 nhánh) gọi hàm và nối tham số vào lệnh cổng",
          "_strategy_fit_attach_args\n" in body and 'gate_args+=("${STRATEGY_FIT_ARGS[@]}")' in body)
    check("D9 timeout mặc định 120 giây, có -k để giết hẳn tiến trình treo",
          'tmo="${STRATEGY_FIT_TIMEOUT_S:-120}"' in eod and 'timeout -k 5 "$tmo"' in eod)
    dsrc = (BIN / "strategy_fit_dashboard.py").read_text(encoding="utf-8")
    check("D10 dashboard ghi nguyên tử, file tạm RIÊNG từng tiến trình (2 lượt song song không giẫm nhau)",
          'tmp = f"{path}.{os.getpid()}.tmp"' in dsrc and "os.replace(tmp, path)" in dsrc)


def part_sweep(td: Path):
    cad = (BIN / "check_report_cadence.sh").read_text(encoding="utf-8")
    src = block(cad, "# SWEEP_ATTACH_BEGIN", "# SWEEP_ATTACH_END")
    dd = td / "reports" / "dashboard"
    dd.mkdir(parents=True)
    for d in ("2026-10-05", "2026-10-09", "2026-09-30", "2026-08-11"):
        (dd / f"strategy_fit_{d}.html").write_text("<html>x</html>")
    (dd / "strategy_fit_2026-10-06.html").write_text("")          # rỗng = không kèm

    def run(fname):
        script = "set -uo pipefail\n" + src + "\nprintf 'ARG=%s\\n' \"${ATTACH_ARGS[@]}\"\n"
        p = subprocess.run(["bash", "-c", script], env=dict(os.environ, ROOT=str(td), FNAME=fname),
                           capture_output=True, text=True)
        a = re.findall(r"^ARG=(.*)$", p.stdout, re.M)
        return [] if a == [""] else a, p.stderr

    a, err = run("SpaceX_daily_report_2026-10-09.md")
    check("S1 gửi bù daily ngày cũ, dashboard NGÀY ĐÓ còn ⇒ kèm đúng file ngày đó",
          a == ["--attach", str(dd / "strategy_fit_2026-10-09.html")] and not err, (a, err))
    a, err = run("SpaceX_ZaloPay_daily_report_2026-08-11.md")
    check("S2 tên daily gộp 2 account cũng khớp", a == ["--attach", str(dd / "strategy_fit_2026-08-11.html")])
    a, err = run("ZaloPay_daily_report_2026-10-07.md")
    check("S3 gửi bù daily, KHÔNG có dashboard ngày đó ⇒ gửi không kèm (không lấy file ngày khác)",
          a == [] and not err, (a, err))
    a, err = run("ZaloPay_daily_report_2026-10-06.md")
    check("S4 dashboard ngày đó rỗng 0 byte ⇒ không kèm", a == [])
    for name in ("SpaceX_weekly_report_2026-10-05_to_2026-10-09.md", "ZaloPay_weekly_report_2026-10-05_to_2026-10-09.md",
                 "SpaceX_monthly_report_2026-09.md", "SpaceX_weekly_report_2026-10-09.md",
                 "X_daily_report_weekly.md", "Fund_weekly_daily_report_2026-10-09.md",
                 "SpaceX_weekly_report_2026-10-05_daily_report_fix.md", "Fund_monthly_daily_report_2026-10-05.md"):
        a, err = run(name)
        check(f"S5 {name}: KHÔNG BAO GIỜ kèm (dù dashboard các ngày trong tên đều có)", a == [] and not err, (a, err))
    check("S6 lệnh cổng của sweep nhận ATTACH_ARGS; sweep KHÔNG gọi script sinh dashboard",
          'report_delivery_gate.py" "$f" --topic "$TRADING_REPORT_THREAD" "${ATTACH_ARGS[@]}"' in cad
          and "strategy_fit_dashboard.py" not in cad)
    # Mọi lệnh cổng do báo cáo tuần/tháng sinh ra (prompt dispatch) không được mang --attach.
    others = [ln for ln in cad.splitlines() if "report_delivery_gate.py" in ln and "ATTACH_ARGS" not in ln]
    check("S7 không dòng nào khác của check_report_cadence.sh truyền --attach cho cổng",
          all("--attach" not in ln for ln in others) and cad.count("--attach") == 1, cad.count("--attach"))


def main():
    with tempfile.TemporaryDirectory() as td_s:
        td = Path(td_s)
        for name, fn in (("email", part_email), ("cli", part_cli), ("gate", part_gate), ("eod", part_eod), ("sweep", part_sweep)):
            d = td / name
            d.mkdir()
            fn(d)
    n, ok = len(results), sum(results)
    print(f"strategy_fit_email_attach_selfcheck: {'PASS' if ok == n else 'FAIL'} ({ok}/{n}) "
          f"[TZ env={os.environ.get('TZ', '<unset>')}, hôm nay ICT={TODAY}]")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
