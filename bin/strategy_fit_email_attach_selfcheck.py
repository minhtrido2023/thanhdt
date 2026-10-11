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
class _SMTP:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def starttls(self): pass
    def login(self, *a): pass
    def sendmail(self, frm, to, raw):
        with open(os.environ["FAKE_SMTP_OUT"], "a", encoding="utf-8") as f:
            f.write(json.dumps({"from": frm, "to": to, "raw": raw}) + "\n")
smtplib.SMTP = _SMTP
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
                        FAKE_SMTP_OUT=str(self.out),
                        REAL_EMAIL_SCRIPT=str(BIN / "send_report_email.py"))

    def sent(self):
        if not self.out.exists():
            return []
        return [json.loads(ln) for ln in self.out.read_text(encoding="utf-8").splitlines()]

    def send(self, report: Path, *extra):
        """Chạy send_report_email.py thật (SMTP giả). → (rc, stderr, message mới nhất | None)."""
        n = len(self.sent())
        p = subprocess.run([sys.executable, str(self.wrapper), str(report),
                            "--skip-return-gate", "selfcheck", *map(str, extra)],
                           env=self.env, capture_output=True, text=True)
        new = self.sent()[n:]
        return p.returncode, p.stderr, (new[-1] if len(new) == 1 else None)


def parts_of(sent):
    msg = email.message_from_string(sent["raw"])
    atts, body = {}, ""
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            atts[part.get_filename()] = part.get_payload(decode=True)
        elif part.get_content_type() == "text/html":
            body = part.get_payload(decode=True).decode("utf-8")
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
                       ("khác", "SpaceX_special_report.md")):
        rep = td / name
        rep.write_text("# Báo cáo nhà đầu tư\n\nNội dung.\n", encoding="utf-8")
        rc, err, s = sb.send(rep, "--attach", dash, "--attach-note", note)
        atts, body = parts_of(s) if s else ({}, "")
        check(f"E6 {kind}: --attach/--attach-note bị BỎ QUA — không file HTML, không dòng 📎, vẫn gửi",
              rc == 0 and list(atts) == [name] and "📎" not in body and "strategy_fit" not in s["raw"]
              and "BỎ QUA" in err, (rc, err, list(atts)))


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
if mode == "sleep":
    time.sleep(30)
if mode == "silent_nofile":
    sys.exit(0)
os.makedirs(out, exist_ok=True)
p = os.path.join(out, "strategy_fit_%s.html" % os.environ["FAKE_DATE"])
open(p, "w").write("<html>fake</html>")
print(p)
'''


def run_eod_fn(td: Path, plan_date: str, mode: str, tz, timeout_s="120"):
    """Chạy NGUYÊN khối _strategy_fit_attach_args trích từ eod_trading_report.sh. → (args, rc, giây, n_gen)."""
    src = block((BIN / "eod_trading_report.sh").read_text(encoding="utf-8"),
                "# STRATEGY_FIT_BEGIN", "# STRATEGY_FIT_END")
    root = td
    (root / "bin").mkdir(exist_ok=True)
    (root / "bin" / "strategy_fit_dashboard.py").write_text(FAKE_GEN, encoding="utf-8")
    script = ("set -uo pipefail\n" + src + "\n_strategy_fit_attach_args\nrc=$?\n"
              "gate_args=(x)\ngate_args+=(\"${STRATEGY_FIT_ARGS[@]}\")\n"       # y như _deliver_eod, dưới set -u
              "printf 'RC=%s\\n' \"$rc\"\nprintf 'ARG=%s\\n' \"${STRATEGY_FIT_ARGS[@]}\"\n")
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    if tz:
        env["TZ"] = tz
    env.update(ROOT=str(root), PLAN_DATE=plan_date, DNA_PYEXE=sys.executable, FAKE_ROOT=str(root),
               FAKE_GEN_MODE=mode, FAKE_DATE=plan_date, STRATEGY_FIT_TIMEOUT_S=timeout_s)
    t0 = time.time()
    p = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)
    secs = time.time() - t0
    args = re.findall(r"^ARG=(.*)$", p.stdout, re.M)
    args = [a for a in args if a != ""] if args != [""] else []
    rc = re.search(r"^RC=(\d+)$", p.stdout, re.M)
    calls = root / "gen_calls"
    n = len(calls.read_text().splitlines()) if calls.exists() else 0
    return args, (int(rc.group(1)) if rc else None), secs, n, p.stdout + p.stderr


def part_eod(td0: Path):
    for tz in (None, "America/New_York", "Asia/Ho_Chi_Minh"):
        tag = f"[TZ={tz or 'unset'}]"
        td = Path(tempfile.mkdtemp(dir=td0))
        dash = td / "reports" / "dashboard" / f"strategy_fit_{TODAY}.html"
        args, rc, _, n, log = run_eod_fn(td, TODAY, "ok", tz)
        check(f"D1 {tag} hôm nay, chưa có file ⇒ SINH rồi --attach đúng đường dẫn",
              rc == 0 and args == ["--attach", str(dash)] and n == 1 and dash.exists(), (args, rc, n, log))
        args, rc, _, n, log = run_eod_fn(td, TODAY, "fail", tz)
        check(f"D2 {tag} account sau: file hôm nay đã có ⇒ DÙNG LẠI, không sinh lần hai",
              rc == 0 and args == ["--attach", str(dash)] and n == 1, (args, rc, n))

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
                 "SpaceX_monthly_report_2026-09.md", "SpaceX_weekly_report_2026-10-09.md"):
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
        for name, fn in (("email", part_email), ("gate", part_gate), ("eod", part_eod), ("sweep", part_sweep)):
            d = td / name
            d.mkdir()
            fn(d)
    n, ok = len(results), sum(results)
    print(f"strategy_fit_email_attach_selfcheck: {'PASS' if ok == n else 'FAIL'} ({ok}/{n}) "
          f"[TZ env={os.environ.get('TZ', '<unset>')}, hôm nay ICT={TODAY}]")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
