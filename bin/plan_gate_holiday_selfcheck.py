#!/usr/bin/env python3
"""Selfcheck hạng mục 2+3 (2026-11-25, sự cố "không ra plan 25/11"): cổng báo động BIẾT NGÀY NGHỈ.

Ca thật: lễ 24/11/2026 khai vào vn_market.py lúc 00:01 24/11, SAU khi chuỗi 21:00 ngày 23/11 đã mở
`plan-t1-not-ready-2026-11-24-{SpaceX,ZaloPay}`. Phủ:
  A. trading_calendar: 24/11 không giao dịch (bằng chứng is_holiday), 23/11/25/11 giao dịch, 28/11 cuối tuần;
     upcoming(): ngày nghỉ đã khai + ngày CHƯA xác nhận; CALENDAR_CONFIRMED_THROUGH thu hẹp danh sách.
  B. gate sweep END-TO-END: câu mở khi lịch CŨ (chưa có 24/11) ⇒ probe rc≠0, vẫn mở; lịch CẬP NHẬT ⇒
     sweep tự đóng qua close_bus_question (actor=Mike, KHÔNG --decided-by-user) kèm bằng chứng is_holiday.
  C. bus_question_housekeeping.plan_t1_resolved: đóng câu ngày nghỉ (cả biến thể -r2-), KHÔNG đóng 25/11 thiếu plan.
  D. send_plan_report NONTRADING-GUARD: ngày đích 24/11 ⇒ 'ngày nghỉ, bỏ qua' exit 0; 25/11 ⇒ chạy tiếp.
  E. bq_freshness HOLIDAY-SKIP: 24/11 + plan 25/11 đủ ⇒ 'NGÀY NGHỈ, BỎ QUA' exit 0; thiếu plan ⇒ chạy tiếp cổng.
  F. trading_calendar_watch: liệt kê ngày chưa xác nhận, không tự đổi lịch.
  G. bq_freshness_check.sh RUN-LOCK (arch-review vòng 2 #4): không chạy song song.
Env WORKDIR_8L_NEW = gốc WC có vn_market ĐÃ có 24/11 (mặc định canonical).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEW_WC = os.environ.get("WORKDIR_8L_NEW", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, str(HERE))
import gate_block_question_selfcheck as G  # noqa: E402  (tái dùng stub bus/notify/close)

FAILS = 0


def chk(cond, name, out=""):
    global FAILS
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS += 1
        print("   output:", str(out)[-700:].replace("\n", " | "))


def old_calendar_wc():
    """WC giả có vn_market.py y hệt bản mới NHƯNG chưa có 24/11 (trạng thái 21:00 ngày 23/11)."""
    d = Path(tempfile.mkdtemp(prefix="pgh_oldwc_"))
    G.TMP.append(d)
    (d / "trading_bot").mkdir()
    src = (Path(NEW_WC) / "trading_bot" / "vn_market.py").read_text()
    old = "    dt.date(2026, 11, 24),\n"
    assert old in src, "vn_market.py không có dòng 24/11 — sai WORKDIR_8L_NEW"
    (d / "trading_bot" / "vn_market.py").write_text(src.replace(old, ""))
    (d / "trading_bot" / "__init__.py").write_text("")
    return str(d)


def env_wc(wc, **kw):
    e = {k: v for k, v in os.environ.items()}
    e["WORKDIR_8L"] = wc
    e.update(kw)
    return e


def py(code, wc, **kw):
    r = subprocess.run([sys.executable, "-c", code], env=env_wc(wc, **kw), capture_output=True, text=True,
                       timeout=60, cwd=str(HERE))
    return r.returncode, r.stdout + r.stderr


def part_a():
    code = ("import trading_calendar as T, json;"
            "print(json.dumps([T.non_trading_evidence(x) for x in ('2026-11-24','2026-11-23','2026-11-25','2026-11-28')]))")
    rc, out = py(code, NEW_WC)
    ev = json.loads(out.strip().splitlines()[-1]) if rc == 0 else [None] * 4
    chk(ev[0] and "is_holiday(2026-11-24)=True" in ev[0] and "T3" in ev[0], "A1 24/11 KHÔNG giao dịch, bằng chứng is_holiday=True", out)
    chk(ev[1] is None and ev[2] is None, "A2 23/11 và 25/11 là ngày giao dịch", out)
    chk(ev[3] and "cuối tuần" in ev[3], "A3 28/11 (T7) không giao dịch — cuối tuần", out)
    rc, out = py("import trading_calendar as T;u=T.upcoming('2026-11-23',14);"
                 "print([str(d) for d in u['holidays']],len(u['unconfirmed']),str(u['unconfirmed'][0]))", NEW_WC)
    chk("['2026-11-24'] 9 2026-11-25" in out, "A4 upcoming 23/11: nghỉ=[24/11], 9 ngày chưa xác nhận, đầu tiên 25/11", out)
    cf = Path(tempfile.mkdtemp(prefix="pgh_cf_")); G.TMP.append(cf)
    up = "import trading_calendar as T;u=T.upcoming('2026-11-23',14);print([str(d) for d in u['unconfirmed']])"
    (cf / "ok.json").write_text(json.dumps({"confirmed_through": "2026-12-01", "source": "thông báo HOSE số X"}))
    rc, out = py(up, NEW_WC, TC_CONFIRMED_FILE=str(cf / "ok.json"))
    chk("['2026-12-02', '2026-12-03', '2026-12-04', '2026-12-07']" in out,
        "A5 file mốc confirmed_through=01/12 + source ⇒ chỉ còn ngày SAU 01/12 chưa xác nhận", out)
    (cf / "nosrc.json").write_text(json.dumps({"confirmed_through": "2026-12-01", "source": ""}))
    rc, out = py(up, NEW_WC, TC_CONFIRMED_FILE=str(cf / "nosrc.json"))
    chk("'2026-11-25'" in out and len(out.split(",")) == 9, "A5b mốc KHÔNG có source ⇒ bỏ qua (9 ngày vẫn chưa xác nhận)", out)
    (cf / "bad.json").write_text("{hỏng")
    rc, out = py(up, NEW_WC, TC_CONFIRMED_FILE=str(cf / "bad.json"))
    chk("'2026-11-25'" in out and rc == 0, "A5c file hỏng ⇒ coi như chưa xác nhận (fail-safe cảnh báo), không crash", out)
    shipped = json.loads((HERE.parent / "config" / "trading_calendar_confirmed.json").read_text())
    chk(shipped.get("confirmed_through") is None and shipped.get("source") is None,
        "A5d file giao kèm nhánh CHƯA điền mốc (không bịa xác nhận) — user điền", shipped)
    chk("CALENDAR_CONFIRMED_THROUGH" not in (HERE / "trading_calendar.py").read_text(),
        "A5e mốc KHÔNG còn đọc từ trading_bot/vn_market.py", "")
    rc, out = py("import trading_calendar as T;print(T.non_trading_evidence('2026-11-24'))", old_calendar_wc())
    chk(out.strip() == "None", "A6 lịch CŨ (chưa khai 24/11) ⇒ 24/11 bị coi là ngày giao dịch (đúng hiện trạng sự cố)", out)
    bad = Path(tempfile.mkdtemp(prefix="pgh_badvm_")); G.TMP.append(bad)
    (bad / "trading_bot").mkdir()
    (bad / "trading_bot" / "__init__.py").write_text("")
    (bad / "trading_bot" / "vn_market.py").write_text("<<<<<<< HEAD\n")
    for d in ("2026-11-25", "2026-11-24"):
        r = subprocess.run([sys.executable, str(HERE / "trading_calendar.py"), "--evidence", d], env=env_wc(str(bad)),
                           capture_output=True, text=True, timeout=60)
        chk(r.returncode == 2 and "ERROR" in r.stdout and "Traceback" not in r.stderr,
            f"A7 vn_market import hỏng ⇒ --evidence {d} rc=2 (KHÔNG rc=1 'ngày giao dịch', không traceback) §28",
            r.stdout + r.stderr)


def part_b():
    target = HERE / "gate_block_question.py"
    R = G.mkroot()
    shutil.copy(HERE / "trading_calendar.py", R / "bin" / "trading_calendar.py")
    marker_dir = R / "markers"; marker_dir.mkdir()
    plan_dir = R / "plans"; plan_dir.mkdir()
    probe = (f"python3 {target} probe plan-t1 --account SpaceX --date 2026-11-24 "
             f"--marker-dir {marker_dir} --plan-dir {plan_dir}")
    args = ["open", "--gate", "plan-t1-not-ready", "--key", "2026-11-24-SpaceX",
            "--topic", "plan-t1-not-ready-2026-11-24-SpaceX", "--owner", "Mike (dispatch DollarBill dựng lại plan)",
            "--deadline", "2026-11-24T08:30", "--recover", "x", "--probe", probe,
            "--expires-at", "2026-11-24T23:59", "--max-reminders", "30", "--reason", "Plan T+1 chưa sẵn sàng (MISSING)",
            "--thread", "plan_approval", "--remind-every-min", "60", "--extra", '{"account":"SpaceX"}']
    oldwc = old_calendar_wc()
    rc, out = G.run(target, R, *args, now="2026-11-23T21:01:00+07:00", extra_env={"WORKDIR_8L": oldwc})
    chk("OPENED" in out, "B1 21:01 23/11 lịch CŨ ⇒ mở câu plan-t1-not-ready-2026-11-24-SpaceX (tái hiện sự cố)", out)
    rc, out = G.run(target, R, "sweep", now="2026-11-23T23:30:00+07:00", extra_env={"WORKDIR_8L": oldwc})
    chk("CLOSED" not in out and "close " not in G.calls(R),
        "B2 sweep 23:30 lịch CŨ ⇒ probe rc≠0 (chưa có marker), KHÔNG đóng", out)
    rc, out = G.run(target, R, "sweep", now="2026-11-24T08:00:00+07:00", extra_env={"WORKDIR_8L": NEW_WC})
    c = G.calls(R)
    chk("CLOSED Mike/plan-t1-not-ready-2026-11-24-SpaceX" in out, "B3 sweep 08:00 24/11 lịch ĐÃ cập nhật ⇒ tự CLOSED", out)
    chk("NON_TRADING_DAY" in c and "is_holiday(2026-11-24)=True" in c,
        "B4 evidence đóng chứa bằng chứng is_holiday(2026-11-24)=True", c)
    ans = [e for e in G.events(R, "Mike", "answer") if e["topic"] == "plan-t1-not-ready-2026-11-24-SpaceX"]
    chk(len(ans) == 1, "B5 answer đăng ĐÚNG topic string của câu hỏi (Mike/plan-t1-not-ready-2026-11-24-SpaceX)", ans)
    rec = json.loads((R / "state" / "gate_blocks" / "plan-t1-not-ready__2026-11-24-SpaceX.json").read_text())
    chk(rec["status"] == "closed" and "NON_TRADING_DAY" in rec.get("closed_how", ""), "B6 state record status=closed", rec)
    src = (HERE / "gate_block_question.py").read_text()
    seg = src[src.index("def sweep_one"):src.index("def cmd_sweep")]
    chk("--decided-by-user" not in seg, "B7 đường đóng tự động KHÔNG dùng --decided-by-user", "")
    rc, out = py(f"import subprocess,sys;r=subprocess.run([sys.executable,'{target}','probe','plan-t1','--account','SpaceX',"
                 f"'--date','2026-11-25','--marker-dir','{marker_dir}','--plan-dir','{plan_dir}','--since','2026-11-24T21:00:00+07:00'],"
                 "capture_output=True,text=True);print(r.returncode,r.stdout)", NEW_WC)
    chk(out.startswith("11 ") and "NON_TRADING" not in out, "B8 ngày giao dịch 25/11 chưa marker ⇒ probe rc=11, KHÔNG đóng", out)


def part_c():
    td = Path(tempfile.mkdtemp(prefix="pgh_hk_")); G.TMP.append(td)
    code = ("import bus_question_housekeeping as H, pathlib, json;p=pathlib.Path(%r);"
            "print(json.dumps([H.plan_t1_resolved(p,t) for t in ('plan-t1-not-ready-2026-11-24-SpaceX',"
            "'plan-t1-not-ready-r2-2026-11-24-ZaloPay','plan-t1-not-ready-2026-11-25-SpaceX')]))") % str(td)
    rc, out = py(code, NEW_WC)
    r = json.loads(out.strip().splitlines()[-1]) if rc == 0 else [None] * 3
    chk(r[0] and "is_holiday(2026-11-24)=True" in r[0], "C1 housekeeping đóng plan-t1 24/11 bằng bằng chứng is_holiday", out)
    chk(r[1] and "báo động giả" in r[1], "C2 biến thể -r2- cũng được nhận diện + đóng", out)
    chk(r[2] is None, "C3 25/11 (ngày giao dịch, thiếu plan) KHÔNG bị đóng", out)
    rc, out = py(code, old_calendar_wc())
    r = json.loads(out.strip().splitlines()[-1]) if rc == 0 else ["x"]
    chk(r[0] is None, "C4 lịch CŨ ⇒ housekeeping KHÔNG đóng 24/11 (không đoán lễ)", out)
    # C5/C6 (arch-review vòng 2 #1): r2 mở VÌ plan tồn tại nhưng hỏng ⇒ file có + plan_date khớp KHÔNG đóng r2;
    # câu thường (không r2) giữ hành vi cũ.
    (td / "plan_SpaceX_2026-11-25.json").write_text(json.dumps({"plan_date": "2026-11-25", "orders": "BROKEN", "account": "WRONG"}))
    code2 = ("import bus_question_housekeeping as H, pathlib, json;p=pathlib.Path(%r);"
             "print(json.dumps([H.plan_t1_resolved(p,t) for t in ('plan-t1-not-ready-r2-2026-11-25-SpaceX',"
             "'plan-t1-not-ready-2026-11-25-SpaceX')]))") % str(td)
    rc, out = py(code2, NEW_WC)
    r = json.loads(out.strip().splitlines()[-1]) if rc == 0 else ["x", None]
    chk(r[0] is None, "C5 r2 + plan HỎNG (orders BROKEN, account sai) ⇒ KHÔNG đóng (để probe marker+md5)", out)
    chk(r[1] and "exists with plan_date=2026-11-25" in r[1], "C6 câu thường + file có plan_date khớp ⇒ hành vi cũ giữ nguyên", out)


def extract(path, b, e):
    lines = path.read_text().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(b))
    j = next(k for k, l in enumerate(lines) if l.startswith(e))
    return "\n".join(lines[i:j + 1])


def part_d():
    blk = extract(HERE / "send_plan_report.sh", "# NONTRADING-GUARD", "fi")
    blk = blk[:blk.rindex("\nfi")] + "\nfi"
    for d, want_skip in (("2026-11-24", True), ("2026-11-25", False)):
        script = f'ROOT="{HERE.parent}"; ACCOUNT=SpaceX; EXPECTED_DATE={d}\n{blk}\necho CONTINUED'
        r = subprocess.run(["bash", "-c", script], env=env_wc(NEW_WC), capture_output=True, text=True, timeout=60)
        o = r.stdout + r.stderr
        if want_skip:
            chk(r.returncode == 0 and "ngày nghỉ, bỏ qua" in o and "CONTINUED" not in o,
                "D1 send_plan_report ngày đích 24/11 ⇒ 'ngày nghỉ, bỏ qua', exit 0, không tới bước mở question", o)
        else:
            chk("CONTINUED" in o and "ngày nghỉ" not in o, "D2 send_plan_report ngày đích 25/11 ⇒ chạy tiếp", o)


def part_e():
    blk = extract(HERE / "bq_freshness_check.sh", "# HOLIDAY-SKIP-BEGIN", "# HOLIDAY-SKIP-END")
    for name, plans, want_skip in (("E1 plan 25/11 đủ 2 account ⇒ 'NGÀY NGHỈ, BỎ QUA' exit 0", ("SpaceX", "ZaloPay"), True),
                                   ("E2 thiếu plan ZaloPay ⇒ nói rõ thiếu, chạy tiếp cổng", ("SpaceX",), False)):
        wc = Path(tempfile.mkdtemp(prefix="pgh_bqf_")); G.TMP.append(wc)
        (wc / "trading_bot").mkdir()
        (wc / "trading_bot" / "__init__.py").write_text("")
        (wc / "trading_bot" / "config.py").write_text("def live_dnse_labels():\n    return ['SpaceX', 'ZaloPay']\n")
        (wc / "data" / "trade_plans").mkdir(parents=True)
        for a in plans:
            (wc / "data" / "trade_plans" / f"plan_{a}_2026-11-25.json").write_text('{"plan_date": "2026-11-25", "orders": []}')
        script = (f'ROOT="{HERE.parent}"; WORKDIR="{wc}"; MORNING=0; TODAY=2026-11-24; NEXT_TRADING_DAY=2026-11-25; '
                  f'NOW_ICT="19:00 ICT"\n{blk}\necho CONTINUED')
        r = subprocess.run(["bash", "-c", script], env=env_wc(NEW_WC), capture_output=True, text=True, timeout=60)
        o = r.stdout + r.stderr
        if want_skip:
            chk(r.returncode == 0 and "NGÀY NGHỈ, BỎ QUA" in o and "CONTINUED" not in o, name, o)
        else:
            chk("CONTINUED" in o and "còn thiếu (ZaloPay" in o, name, o)
    script = (f'ROOT="{HERE.parent}"; WORKDIR=/nonexistent; MORNING=0; TODAY=2026-11-25; NEXT_TRADING_DAY=2026-11-26; '
              f'NOW_ICT="19:00 ICT"\n{blk}\necho CONTINUED')
    r = subprocess.run(["bash", "-c", script], env=env_wc(NEW_WC), capture_output=True, text=True, timeout=60)
    chk("CONTINUED" in r.stdout and "NGÀY NGHỈ" not in r.stdout, "E3 ngày giao dịch 25/11 ⇒ không đụng nhánh ngày nghỉ", r.stdout)


def part_f():
    r = subprocess.run([sys.executable, str(HERE / "trading_calendar_watch.py"), "--dry-run"],
                       env=env_wc(NEW_WC, MIKE_NOW_ICT="2026-11-23T08:08:00"), capture_output=True, text=True, timeout=60)
    o = r.stdout
    chk(r.returncode == 0 and "CHƯA XÁC NHẬN" in o and "T4 25/11" in o and "T3 24/11" in o and "SSI/HOSE" in o,
        "F1 watch 23/11: liệt kê ngày chưa xác nhận (25/11…), nêu ngày nghỉ đã khai 24/11, nhắc đối chiếu SSI/HOSE", o)
    src = (HERE / "trading_calendar_watch.py").read_text()
    chk("_VARIABLE_HOLIDAYS.add" not in src and "open(" not in src.split("def send")[0],
        "F2 watch KHÔNG ghi/đổi lịch (chỉ cảnh báo)", "")


def part_g():
    """RUN-LOCK bq_freshness_check.sh: lượt khác đang giữ khoá ⇒ exit 75, không làm gì (không BQ/dispatch)."""
    td = Path(tempfile.mkdtemp(prefix="pgh_lock_")); G.TMP.append(td)
    lk = td / "bqf.lock"
    h = subprocess.Popen([sys.executable, "-c", "import fcntl,os,sys,time;fd=os.open(sys.argv[1],os.O_RDWR|os.O_CREAT);"
                          "fcntl.flock(fd,fcntl.LOCK_EX);print('held',flush=True);time.sleep(60)", str(lk)],
                         stdout=subprocess.PIPE, text=True)
    h.stdout.readline()
    try:
        r = subprocess.run(["bash", str(HERE / "bq_freshness_check.sh"), "--quiet"], env=env_wc(NEW_WC, BQF_LOCK_FILE=str(lk)),
                           capture_output=True, text=True, timeout=60)
    finally:
        h.kill()
    chk(r.returncode == 75 and "BQF_LOCKED" in r.stdout and "BQ Freshness Check" not in r.stdout,
        "G1 bq_freshness_check.sh: lượt khác giữ khoá ⇒ exit 75 BQF_LOCKED, không chạy gì", r.stdout + r.stderr)
    src = (HERE / "bq_freshness_check.sh").read_text()
    chk("--bg 9>&-" in src, "G2 dispatch DollarBill --bg đóng fd khoá (khoá nhả khi script xong, không theo job nền)", "")


if __name__ == "__main__":
    try:
        part_a(); part_b(); part_c(); part_d(); part_e(); part_f(); part_g()
    finally:
        for d in G.TMP:
            shutil.rmtree(d, ignore_errors=True)
    print(f"plan_gate_holiday_selfcheck: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    sys.exit(1 if FAILS else 0)
