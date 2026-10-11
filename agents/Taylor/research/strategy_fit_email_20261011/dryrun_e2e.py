#!/usr/bin/env python3
"""Chạy khô end-to-end, KHÔNG gửi thật: hàm bash thật của eod_trading_report.sh → strategy_fit_dashboard.py
THẬT (dữ liệu thật, out-dir tạm) → report_delivery_gate.deliver (sổ tạm) → send_report_email.py THẬT (SMTP giả)."""
import email, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
WT = Path(sys.argv[1]); BIN = WT / "bin"
sys.path.insert(0, str(BIN))
import strategy_fit_email_attach_selfcheck as sc
CANON = Path("/home/trido/thanhdt/WorkingClaude/mike")
td = Path(tempfile.mkdtemp(prefix="sf_dryrun_"))
root = td / "root"; root.mkdir(); (root / "bin").symlink_to(BIN)
src = sc.block((BIN / "eod_trading_report.sh").read_text(encoding="utf-8"), "# STRATEGY_FIT_BEGIN", "# STRATEGY_FIT_END")
script = "set -uo pipefail\n" + src + "\n_strategy_fit_attach_args\nprintf 'ARG=%s\\n' \"${STRATEGY_FIT_ARGS[@]}\"\n"
env = {k: v for k, v in os.environ.items() if k != "TZ"}
env.update(ROOT=str(root), PLAN_DATE=sc.TODAY, DNA_PYEXE="/home/trido/thanhdt/wc_venv/bin/python")
def call(tag):
    t0 = time.time()
    p = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)
    args = [l[4:] for l in p.stdout.splitlines() if l.startswith("ARG=") and l != "ARG="]
    print(f"[{tag}] {time.time()-t0:.1f}s args={args}")
    return args, p
# 2 account chạy SONG SONG khi chưa có file (xấu hơn thực tế: for_each_live_account chạy tuần tự)
import concurrent.futures as cf
with cf.ThreadPoolExecutor(2) as ex:
    r = list(ex.map(call, ["song song A", "song song B"]))
dd = root / "reports" / "dashboard"
print("file trong thư mục dashboard:", sorted(os.listdir(dd)))
for a, p in r:
    assert a and a[0] == "--attach", (a, p.stdout[-800:], p.stderr[-800:])
print("\n".join(l for l in r[0][1].stdout.splitlines() if l.startswith("[ô]")))
print("stderr lượt A:", r[0][1].stderr.strip()[-300:] or "(trống)")
args3, _ = call("account sau — dùng lại")
dash = Path(args3[1]); html = dash.read_bytes()
print(f"dashboard: {dash.name} {len(html)} byte sha256={hashlib.sha256(html).hexdigest()[:16]}")

spec = importlib.util.spec_from_file_location("rdg_dry", BIN / "report_delivery_gate.py")
rdg = importlib.util.module_from_spec(spec); spec.loader.exec_module(rdg)
rdg.LEGACY_EMAIL_STATE = td / "legacy.json"
sb = sc.Sandbox(td)
notify = td / "notify.sh"; notify.write_text("#!/bin/sh\nexit 0\n"); notify.chmod(0o755)
os.environ.update(sb.env)
for acct in ("SpaceX", "ZaloPay"):
    real = sorted((CANON / "reports").glob(f"{acct}_daily_report_2026-*.md"))[-1]
    rep = td / f"{acct}_daily_report_{sc.TODAY}.md"
    shutil.copy(real, rep)
    sha = rdg.digest(rep)
    rc = rdg.deliver(rep, td / "state.json", "trading_report", notify, sb.wrapper, True, (dash,), None)
    s = sb.sent()[-1]; msg = email.message_from_string(s["raw"])
    print(f"\n== {acct}: nội dung lấy từ {real.name}; cổng rc={rc}; To={s['to']}; Subject={msg['Subject']}")
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            b = part.get_payload(decode=True)
            print(f"   đính kèm: {part.get_filename()} {len(b)} byte sha256={hashlib.sha256(b).hexdigest()[:16]}"
                  + ("  == file dashboard" if b == html else "  == artifact .md" if b == rep.read_bytes() else "  ??"))
        elif part.get_content_type() == "text/html":
            body = part.get_payload(decode=True).decode()
            print("   dòng trong thân:", [l[l.index("📎"):l.index("</p>")] for l in body.splitlines() if "📎" in l])
    rec = json.loads((td / "state.json").read_text())["reports"][rep.name]
    print(f"   sổ: sha256==sha(.md) {rec['sha256']==sha}; khoá={sorted(rec)}; email={sorted(rec['email'])}")
print("\nemail giả đã 'gửi':", len(sb.sent()), "| sổ canonical không bị đụng:", not (td / "state.json").samefile(CANON / "state" / "report_delivery.json"))
