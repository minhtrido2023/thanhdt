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
  G. bq_freshness_check.sh RUN-LOCK (arch-review vòng 2 #4): không chạy song song — chạy BẢN SAO trong ROOT tạm với
     notify*/dispatch/bq giả (vòng cuối #3); bị chặn ⇒ báo trading_daily + gate_last bqf_locked (vòng cuối #8).
  E4/H (vòng cuối #5c/#5e): HOLIDAY-SKIP→MORNING-SKIP E2E; late_plan_catchup.check_status approved_by_user.
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
        chk(r.returncode == 2 and "không import được trading_bot.vn_market" in r.stdout and "Traceback" not in r.stderr,
            f"A7 vn_market import hỏng ⇒ --evidence {d} rc=2 (KHÔNG rc=1 'ngày giao dịch', không traceback) §28",
            r.stdout + r.stderr)
    # A8 (vòng cuối #5d): exception TRONG try (ngày sai / tham số sai) ⇒ rc 2, KHÔNG rc 1 (= "ngày giao dịch")
    for args in (["--evidence", "2026-13-45"], ["--upcoming", "abc"]):
        r = subprocess.run([sys.executable, str(HERE / "trading_calendar.py")] + args, env=env_wc(NEW_WC),
                           capture_output=True, text=True, timeout=60)
        chk(r.returncode == 2 and "trading_calendar: ERROR" in r.stdout and "Traceback" not in r.stderr,
            f"A8 {' '.join(args)} ⇒ rc=2 ERROR  [giết: except chung rc 2 → 1]", r.stdout + r.stderr)


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
    chk(r[1] is None, "C6 câu thường + plan HỎNG (orders không phải list) ⇒ KHÔNG đóng (plan_presence.classify ≠ OK, vòng cuối #9)", out)
    code3 = ("import bus_question_housekeeping as H, pathlib;p=pathlib.Path(%r);"
             "print(repr(H.plan_t1_resolved(p,'plan-t1-not-ready-2026-11-25-SpaceX')))") % str(td)
    for body, want, name in (
            ({"plan_date": "2026-11-25", "orders": [], "account": "SpaceX"}, True, "C6b plan OK (orders list, đúng account) ⇒ đóng"),
            ({"plan_date": "2026-11-25", "orders": [], "account": "ZaloPay"}, False, "C6c plan_SpaceX nhưng account=ZaloPay ⇒ KHÔNG đóng"),
            ({"plan_date": "2026-11-26", "orders": []}, False, "C6d plan_date sai ⇒ KHÔNG đóng")):
        (td / "plan_SpaceX_2026-11-25.json").write_text(json.dumps(body))
        rc, out = py(code3, NEW_WC)
        got = out.strip().splitlines()[-1] if rc == 0 else "ERR"
        chk((got != "None" and "exists with plan_date=2026-11-25" in got) if want else got == "None", name, out)


def extract(path, b, e, indented=False):
    lines = path.read_text().splitlines()
    m = (lambda l, x: l.strip().startswith(x)) if indented else (lambda l, x: l.startswith(x))
    i = next(k for k, l in enumerate(lines) if m(l, b))
    j = next(k for k, l in enumerate(lines) if k > i and m(l, e))
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


def part_e2():
    """vòng cuối #5c: khối HOLIDAY-SKIP THẬT cấp cờ cho guard MORNING-SKIP THẬT (không tự gán biến từ ngoài):
    ngày lễ 24/11, SpaceX ĐÃ có plan 25/11, ZaloPay thiếu ⇒ chỉ ZaloPay được dispatch, SpaceX KHÔNG bị ghi đè."""
    hol = extract(HERE / "bq_freshness_check.sh", "# HOLIDAY-SKIP-BEGIN", "# HOLIDAY-SKIP-END")
    ms = extract(HERE / "bq_freshness_check.sh", "# MORNING-SKIP-BEGIN", "# MORNING-SKIP-END", indented=True)
    wc = Path(tempfile.mkdtemp(prefix="pgh_e2e_")); G.TMP.append(wc)
    (wc / "trading_bot").mkdir()
    (wc / "trading_bot" / "__init__.py").write_text("")
    (wc / "trading_bot" / "config.py").write_text("def live_dnse_labels():\n    return ['SpaceX', 'ZaloPay']\n")
    (wc / "data" / "trade_plans").mkdir(parents=True)
    (wc / "data" / "trade_plans" / "plan_SpaceX_2026-11-25.json").write_text('{"plan_date": "2026-11-25", "orders": []}')
    script = (f'ROOT="{HERE.parent}"; WORKDIR="{wc}"; MORNING=0; TODAY=2026-11-24; NEXT_TRADING_DAY=2026-11-25; '
              f'NOW_ICT="19:00 ICT"\n{hol}\nfor ACCT in SpaceX ZaloPay; do\n{ms}\necho "DISPATCH $ACCT"\ndone')
    env = env_wc(NEW_WC)
    for k in ("BQF_SKIP_EXISTING_PLANS", "_HOL_LAPBU", "MIKE_MORNING_FORCE", "MIKE_MORNING_RUN"):
        env.pop(k, None)
    r = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True, timeout=60)
    o = r.stdout + r.stderr
    chk("[SKIP-EXISTING] plan_SpaceX_2026-11-25.json" in o and "holiday=1" in o and "DISPATCH ZaloPay" in o
        and "DISPATCH SpaceX" not in o,
        "E4 E2E lễ 24/11: HOLIDAY-SKIP → MORNING-SKIP thật: SpaceX (có plan) KHÔNG dispatch, ZaloPay dispatch  [giết: xoá _HOL_LAPBU=1]", o)


def part_h():
    """vòng cuối #5e: late_plan_catchup.check_status — approved_by_user là ĐÃ DUYỆT ⇒ APPROVED ⇒ REFUSE."""
    fn = extract(HERE / "late_plan_catchup.sh", "check_status() {", "}")
    src = (HERE / "late_plan_catchup.sh").read_text()
    td = Path(tempfile.mkdtemp(prefix="pgh_lpc_")); G.TMP.append(td)
    cases = (("H1 approved_by_user=true (không approved_by) ⇒ APPROVED  [giết: bỏ approved_by_user]",
              {"plan_date": "2026-11-25", "orders": [], "approved_by_user": True}, "APPROVED"),
             ("H2 approved_by='user' ⇒ APPROVED", {"plan_date": "2026-11-25", "orders": [], "approved_by": "user"}, "APPROVED"),
             ("H3 chưa duyệt, chưa merge ⇒ NEEDS_CHAIN", {"plan_date": "2026-11-25", "orders": []}, "NEEDS_CHAIN"),
             ("H4 orders hỏng ⇒ INVALID", {"plan_date": "2026-11-25", "orders": "x"}, "INVALID"),
             ("H5 không có file ⇒ MISSING", None, "MISSING"))
    for name, body, want in cases:
        f = td / ("p_%d.json" % len(name))
        if body is not None:
            f.write_text(json.dumps(body))
        r = subprocess.run(["bash", "-c", f'ROOT="{HERE.parent}"\n{fn}\ncheck_status "{f}" 2026-11-25'],
                           capture_output=True, text=True, timeout=60)
        chk(r.stdout.strip() == want, name, r.stdout + r.stderr)
    chk('APPROVED|INVALID) echo "[late_plan] $acct $PLAN_DATE — $status, REFUSE."' in src,
        "H6 APPROVED/INVALID ⇒ REFUSE (không chạy chuỗi/gửi lại plan đã duyệt)", "")


def part_f():
    r = subprocess.run([sys.executable, str(HERE / "trading_calendar_watch.py"), "--dry-run"],
                       env=env_wc(NEW_WC, MIKE_NOW_ICT="2026-11-23T08:08:00"), capture_output=True, text=True, timeout=60)
    o = r.stdout
    chk(r.returncode == 0 and "CHƯA XÁC NHẬN" in o and "T4 25/11" in o and "T3 24/11" in o and "SSI/HOSE" in o,
        "F1 watch 23/11: liệt kê ngày chưa xác nhận (25/11…), nêu ngày nghỉ đã khai 24/11, nhắc đối chiếu SSI/HOSE", o)
    src = (HERE / "trading_calendar_watch.py").read_text()
    chk("_VARIABLE_HOLIDAYS.add" not in src and "open(" not in src.split("def send")[0],
        "F2 watch KHÔNG ghi/đổi lịch (chỉ cảnh báo)", "")


FAKE_LOG = '#!/bin/bash\necho "$(basename "$0") $*" >> "%s"\nexit 0\n'


def bqf_sandbox():
    """BẢN SAO bq_freshness_check.sh trong ROOT tạm (KHÔNG kb/discord_channels.json, KHÔNG credential): notify*/
    dispatch.sh giả cạnh nó, bq giả đầu PATH, WC tạm chỉ có vn_market (vòng cuối #3 — mutant xoá flock từng gọi
    8 notify.sh + 19 notify_thread.sh THẬT). KHÔNG BAO GIỜ chạy bin/ thật."""
    td = Path(tempfile.mkdtemp(prefix="pgh_bqf_sb_")); G.TMP.append(td)
    root = td / "mike"; (root / "bin").mkdir(parents=True); (td / "fakebin").mkdir(); (td / "state").mkdir()
    shutil.copy(HERE / "bq_freshness_check.sh", root / "bin" / "bq_freshness_check.sh")
    log = td / "calls.log"
    for n in ("notify.sh", "notify_thread.sh", "notify_discord.sh", "dispatch.sh", "append_event.sh"):
        (root / "bin" / n).write_text(FAKE_LOG % log); (root / "bin" / n).chmod(0o755)
    (td / "fakebin" / "bq").write_text(FAKE_LOG % log); (td / "fakebin" / "bq").chmod(0o755)
    wc = td / "wc"; (wc / "trading_bot").mkdir(parents=True)
    (wc / "trading_bot" / "__init__.py").write_text("")
    shutil.copy(Path(NEW_WC) / "trading_bot" / "vn_market.py", wc / "trading_bot" / "vn_market.py")
    env = env_wc(str(wc), PATH=f"{td / 'fakebin'}:{os.environ['PATH']}", BQF_LOCK_FILE=str(td / "bqf.lock"),
                 BQF_STATE_DIR=str(td / "state"))
    for k in ("BQF_LOCKED_NOTIFY", "MIKE_MORNING_RUN", "BQF_SKIP_EXISTING_PLANS"):
        env.pop(k, None)
    assert not (root / "kb").exists() and not (td / "wc_env.sh").exists()
    return td, root, env, log


def hold_lock(lk):
    h = subprocess.Popen([sys.executable, "-c", "import fcntl,os,sys,time;fd=os.open(sys.argv[1],os.O_RDWR|os.O_CREAT);"
                          "fcntl.flock(fd,fcntl.LOCK_EX);os.ftruncate(fd,0);os.write(fd,str(os.getpid()).encode());"
                          "print('held',flush=True);time.sleep(60)", str(lk)], stdout=subprocess.PIPE, text=True)
    h.stdout.readline()
    return h


def part_g():
    """RUN-LOCK bq_freshness_check.sh (bản sao sandbox): lượt khác giữ khoá ⇒ exit 75, không BQ/dispatch;
    đường cron BÁO trading_daily kèm pid + ghi gate_last bqf_locked (vòng cuối #8)."""
    td, root, env, log = bqf_sandbox()
    h = hold_lock(td / "bqf.lock")
    try:
        r = subprocess.run(["bash", str(root / "bin" / "bq_freshness_check.sh"), "--quiet"], env=env,
                           capture_output=True, text=True, timeout=120)
    finally:
        h.kill()
    calls = log.read_text() if log.exists() else ""
    gl = json.loads((td / "state" / "bq_freshness_gate_last.json").read_text()) if (td / "state" / "bq_freshness_gate_last.json").exists() else {}
    chk(r.returncode == 75 and "BQF_LOCKED" in r.stdout and "BQ Freshness Check" not in r.stdout,
        "G1 (sandbox) lượt khác giữ khoá ⇒ exit 75 BQF_LOCKED, không chạy cổng", r.stdout + r.stderr)
    nt = [l for l in calls.splitlines() if l.startswith("notify_thread.sh ")]
    chk(len(nt) == 1 and nt[0].endswith(" trading_daily") and f"pid {h.pid}" in nt[0] and "notify.sh " not in calls
        and "bq " not in calls and "dispatch.sh" not in calls,
        "G3 đường cron bị chặn ⇒ ĐÚNG 1 tin trading_daily kèm pid giữ khoá; không bq/dispatch/Telegram (vòng cuối #8)", calls)
    chk(gl.get("failed") is True and gl.get("data_fail_kinds") == ["bqf_locked"] and gl.get("locked_by_pid") == str(h.pid)
        and gl.get("next_trading_day"), "G4 ghi gate_last bqf_locked (+pid) để retry không SKIP vô lý", gl)
    keep = dict(gl, locked_by_pid=None, data_fail_kinds=["prune_depth"])
    keep.pop("locked_by_pid")
    (td / "state" / "bq_freshness_gate_last.json").write_text(json.dumps(keep))
    log.unlink(missing_ok=True)
    h = hold_lock(td / "bqf.lock")
    try:
        r = subprocess.run(["bash", str(root / "bin" / "bq_freshness_check.sh"), "--quiet"],
                           env=dict(env, BQF_LOCKED_NOTIFY="0"), capture_output=True, text=True, timeout=120)
    finally:
        h.kill()
    gl2 = json.loads((td / "state" / "bq_freshness_gate_last.json").read_text())
    chk(r.returncode == 75 and not log.exists() and gl2.get("data_fail_kinds") == ["prune_depth"],
        "G5 BQF_LOCKED_NOTIFY=0 (retry tự xử rc 75) ⇒ không báo; gate_last THẬT của lượt giữ khoá cùng phiên KHÔNG bị ghi đè",
        r.stdout + str(gl2))
    src = (HERE / "bq_freshness_check.sh").read_text()
    chk("--bg 9>&-" in src, "G2 dispatch DollarBill --bg đóng fd khoá (khoá nhả khi script xong, không theo job nền)", "")
    chk('exec 9<>"$_BQF_LOCK"' in src, "G6 mở khoá bằng <> (không cắt file) ⇒ lượt bị chặn đọc được pid", "")


if __name__ == "__main__":
    try:
        part_a(); part_b(); part_c(); part_d(); part_e(); part_e2(); part_f(); part_g(); part_h()
    finally:
        for d in G.TMP:
            shutil.rmtree(d, ignore_errors=True)
    print(f"plan_gate_holiday_selfcheck: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    sys.exit(1 if FAILS else 0)
