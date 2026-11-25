#!/usr/bin/env python3
"""Selfcheck bin/plan_gate_recovery.py (hạng mục 4, 2026-11-25) — sandbox hoàn toàn: script con giả
(prune_depth_gate/daily_refresh/bq_freshness/send_plan_report/notify*) ghi log gọi; lịch THẬT vn_market
(WORKDIR_8L, cần bản có 24/11); account live giả SpaceX+ZaloPay. Không gọi BQ/Discord/Telegram/DollarBill.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = Path(os.environ.get("PGR_TARGET", HERE / "plan_gate_recovery.py"))
NEW_WC = os.environ.get("WORKDIR_8L_NEW", "/home/trido/thanhdt/WorkingClaude")
FAILS = 0
TMP = []


def chk(cond, name, out=""):
    global FAILS
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS += 1
        print("   output:", str(out)[-900:].replace("\n", " | "))


FAKE = {
 "prune_depth_gate.py": '#!/usr/bin/env python3\nimport sys,os\nrc=int(open(os.environ["SB"]+"/depth_rc").read())\n'
     'print("PRUNE_DEPTH %s date=%s n=197 threshold=183" % ({0:"PASS",1:"FAIL"}.get(rc,"UNMEASURABLE"), sys.argv[-1]))\n'
     'open(os.environ["SB"]+"/calls.log","a").write("depth "+sys.argv[-1]+"\\n");sys.exit(rc)\n',
 "bq_freshness_check.sh": '#!/bin/bash\necho "bqf MORNING=${MIKE_MORNING_RUN:-0} SKIP_EXISTING=${BQF_SKIP_EXISTING_PLANS:-0} $*" >> "$SB/calls.log"\n'
     # mốc retry phải có TRƯỚC khi chuỗi chạy (§3/§5) — fake ghi lại điều nó thấy
     '[ -f "$SB/state/plan_gate_recovery/$(cat $SB/next).json" ] && echo "bqf_saw_mark=1" >> "$SB/calls.log"\n'
     # mô phỏng guard thật: SKIP_EXISTING ⇒ không ghi đè file đã có
     'rc=$(cat "$SB/bqf_rc"); [ "$rc" = 0 ] && for a in SpaceX ZaloPay; do f="$SB/wc/data/trade_plans/plan_${a}_$(cat $SB/next).json"; '
     '[ "${BQF_SKIP_EXISTING_PLANS:-0}${MIKE_MORNING_RUN:-0}" != 00 ] && [ -e "$f" ] && continue; echo "dispatch $a" >> "$SB/calls.log"; '
     'echo "{\\"plan_date\\":\\"$(cat $SB/next)\\",\\"orders\\":[]}" > "$f"; done; exit $rc\n',
 "send_plan_report.sh": '#!/bin/bash\necho "send $* NOTE=${PLAN_REPORT_NOTE:+yes}" >> "$SB/calls.log"\n',
 "late_plan_catchup.sh": '#!/bin/bash\necho "late_plan_catchup" >> "$SB/calls.log"\n',
 "notify.sh": '#!/bin/bash\necho "TELEGRAM $1" >> "$SB/calls.log"; exit $(cat "$SB/notify_rc" 2>/dev/null || echo 0)\n',
 "notify_thread.sh": '#!/bin/bash\necho "DISCORD[$2] $1" >> "$SB/calls.log"; exit $(cat "$SB/notify_rc" 2>/dev/null || echo 0)\n',
}
REFRESH = ('#!/bin/bash\necho "refresh MORNING=${MIKE_MORNING_RUN:-0}" >> "$SB/calls.log"\n'
           'echo "{\\"as_of\\": \\"$(cat $SB/session)\\"}" > "$SB/wc/deploy_golive_dt5g_v4/golive_state_today.json"\n')


def sandbox(session, nxt, asof="2026-11-20", kinds=("prune_depth", "dt5g_publisher"), failed=True,
            gl_session=None, depth_rc=0, bqf_rc=0, plans=(), raw_plans=None):
    sb = Path(tempfile.mkdtemp(prefix="pgr_sc_")); TMP.append(sb)
    (sb / "bin").mkdir()
    for n, body in FAKE.items():
        (sb / "bin" / n).write_text(body); (sb / "bin" / n).chmod(0o755)
    wc = sb / "wc"
    (wc / "trading_bot").mkdir(parents=True)
    (wc / "trading_bot" / "__init__.py").write_text("")
    (wc / "trading_bot" / "config.py").write_text("def live_dnse_labels():\n    return ['SpaceX', 'ZaloPay']\n")
    (wc / "data" / "trade_plans").mkdir(parents=True)
    (wc / "deploy_golive_dt5g_v4").mkdir()
    (wc / "deploy_golive_dt5g_v4" / "golive_state_today.json").write_text(json.dumps({"as_of": asof}))
    (wc / "daily_refresh_v34b_linux.sh").write_text(REFRESH); (wc / "daily_refresh_v34b_linux.sh").chmod(0o755)
    for a in plans:
        (wc / "data" / "trade_plans" / f"plan_{a}_{nxt}.json").write_text(json.dumps({"plan_date": nxt, "orders": []}))
    for a, body in (raw_plans or {}).items():
        (wc / "data" / "trade_plans" / f"plan_{a}_{nxt}.json").write_text(body)
    (sb / "state").mkdir()
    (sb / "state" / "bq_freshness_gate_last.json").write_text(json.dumps(
        {"session": gl_session or session, "next_trading_day": nxt, "failed": failed, "data_fail_kinds": list(kinds)}))
    for k, v in (("depth_rc", depth_rc), ("bqf_rc", bqf_rc), ("session", session), ("next", nxt)):
        (sb / k).write_text(str(v))
    return sb


def run(sb, mode, now, **env):
    e = dict(os.environ, SB=str(sb), PGR_WC_ROOT=str(sb / "wc"), PGR_STATE_DIR=str(sb / "state"),
             PGR_BIN=str(sb / "bin"), WORKDIR_8L=NEW_WC, MIKE_NOW_ICT=now, PGR_PLAN_WAIT_S="1",
             PGR_REFRESH_SCRIPT="__no_such_script_pgr_sc__.sh", BQF_LOCK_FILE=str(sb / "bqf.lock"))
    e.update(env)
    r = subprocess.run([sys.executable, str(TARGET), mode], env=e, capture_output=True, text=True, timeout=120)
    calls = (sb / "calls.log").read_text() if (sb / "calls.log").exists() else ""
    return r.returncode, r.stdout + r.stderr, calls


def st(sb, d):
    p = sb / "state" / "plan_gate_recovery" / f"{d}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def sent(c):
    return any(l.startswith("send ") for l in c.splitlines())


def hold(path):
    """Giữ flock trên path trong tiến trình con (mô phỏng lượt khác đang chạy)."""
    return subprocess.Popen([sys.executable, "-c", "import fcntl,os,sys,time;fd=os.open(sys.argv[1],os.O_RDWR|os.O_CREAT);"
                             "fcntl.flock(fd,fcntl.LOCK_EX);print('held',flush=True);time.sleep(60)", str(path)],
                            stdout=subprocess.PIPE, text=True)


def main():
    # R1 ca thật 23/11 20:00 (lịch mới): FAIL dữ liệu nền, đo lại đạt ⇒ retry 1 lần; TRƯỚC 21:00 KHÔNG tự gửi
    sb = sandbox("2026-11-23", "2026-11-25")
    rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    chk(rc == 0 and "refresh MORNING=1" in c and "bqf MORNING=0 SKIP_EXISTING=1 --quiet" in c
        and not sent(c) and not any(l == "late_plan_catchup" for l in c.splitlines())
        and st(sb, "2026-11-25")["retry"]["result"] == "ok" and "DISCORD[trading_daily] ✅" in c,
        "R1 23/11 20:00 cổng FAIL dữ liệu nền + đo lại đạt ⇒ refresh→bq_freshness(skip-existing), KHÔNG tự gửi trước 21:00", out + c)
    chk("bqf_saw_mark=1" in c, "R1b mốc retry đã ghi TRƯỚC khi chuỗi chạy (bq_freshness thấy file mốc) — §3", c)
    # R1c sau 21:00 ⇒ gửi qua late_plan_catchup (chạy chuỗi park/inject/auto_exit rồi mới gửi), không send trực tiếp
    sb = sandbox("2026-11-23", "2026-11-25", asof="2026-11-23")
    rc, out, c = run(sb, "--retry", "2026-11-23T21:20:00")
    chk(rc == 0 and "late_plan_catchup" in c.splitlines() and not sent(c),
        "R1c 21:20 ⇒ bin/late_plan_catchup.sh, KHÔNG send_plan_report trực tiếp", out + c)
    sb = sandbox("2026-11-23", "2026-11-25", asof="2026-11-23")
    rc, out, c = run(sb, "--retry", "2026-11-23T21:05:00")
    chk(rc == 0 and "late_plan_catchup" not in c.splitlines() and not sent(c) and "21:15" in out,
        "R1d 21:05 (cùng giờ cron send_plan_report 21:00) ⇒ KHÔNG gửi, không đua", out + c)
    sb = sandbox("2026-11-23", "2026-11-25", asof="2026-11-23")
    rc, out, c = run(sb, "--retry", "2026-11-24T00:10:00")
    chk(rc == 0 and "send --account SpaceX --second-chance --plan-date 2026-11-25 NOTE=yes" in c
        and "late_plan_catchup" not in c.splitlines(),
        "R1e qua nửa đêm (late_plan_catchup tự no-op) ⇒ gửi kèm cảnh báo chuỗi CHƯA chạy", out + c)
    n_before = c.count("\n")
    rc, out, c = run(sb, "--retry", "2026-11-23T20:20:00")
    chk("OK plan đủ" in out and c.count("\n") == n_before, "R2 lượt sau, plan đã đủ ⇒ không làm gì", out)
    # R3 retry giới hạn 1 lần: chuỗi fail ⇒ lượt sau KHÔNG chạy lại
    sb = sandbox("2026-11-23", "2026-11-25", bqf_rc=1)
    rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    chk(rc == 1 and st(sb, "2026-11-25")["retry"]["result"] == "fail" and "TELEGRAM 🟠" in c,
        "R3 bq_freshness vẫn FAIL ⇒ result=fail, báo Telegram 1 lần, rc=1", out + c)
    n_before = c.count("\n")
    rc, out, c = run(sb, "--retry", "2026-11-23T20:20:00")
    chk("RETRY_ALREADY_DONE" in out and c.count("\n") == n_before, "R4 lượt sau ⇒ RETRY_ALREADY_DONE, không chạy lại gì", out + c)
    # R5 điều kiện chưa hồi phục ⇒ không retry, không ghi mốc (lượt sau thử lại)
    sb = sandbox("2026-11-23", "2026-11-25", depth_rc=1)
    rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    chk("CHƯA HỒI PHỤC" in out and "refresh" not in c and "bqf" not in c and not st(sb, "2026-11-25"),
        "R5 depth đo lại vẫn FAIL ⇒ KHÔNG chạy chuỗi, KHÔNG ghi mốc retry (không nới ngưỡng)", out + c)
    sb = sandbox("2026-11-23", "2026-11-25", depth_rc=2)
    rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    chk("CHƯA HỒI PHỤC" in out and "bqf" not in c, "R6 depth KHÔNG ĐO ĐƯỢC (rc=2) ⇒ fail-closed, không retry", out + c)
    # R7 cổng fail vì lý do KHÁC dữ liệu nền / artifact phiên khác ⇒ không retry
    sb = sandbox("2026-11-23", "2026-11-25", kinds=())
    rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    chk("SKIP" in out and "bqf" not in c, "R7 cổng FAIL nhưng không phải dữ liệu nền ⇒ SKIP", out + c)
    sb = sandbox("2026-11-23", "2026-11-25", gl_session="2026-11-20")
    rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    chk("SKIP" in out and "bqf" not in c, "R8 artifact cổng của phiên CŨ (20/11) ⇒ SKIP (§14 freshness thật)", out + c)
    # R9 daily_refresh đang chạy ⇒ đợi
    sb = sandbox("2026-11-23", "2026-11-25")
    fake = sb / "fake_refresh_pgr.sh"
    fake.write_text("#!/bin/bash\nsleep 30\n"); fake.chmod(0o755)
    holder = subprocess.Popen(["bash", str(fake)])
    try:
        rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00", PGR_REFRESH_SCRIPT="fake_refresh_pgr.sh")
    finally:
        holder.kill()
    chk("WAIT" in out and "bqf" not in c and not st(sb, "2026-11-25"), "R9 daily_refresh đang chạy (bash <script>) ⇒ WAIT, không ghi mốc", out + c)
    mention = subprocess.Popen(["bash", "-c", "sleep 30 # nhắc fake_refresh_pgr.sh trong dòng lệnh"])
    try:
        rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00", PGR_REFRESH_SCRIPT="fake_refresh_pgr.sh")
    finally:
        mention.kill()
    chk("WAIT" not in out, "R9b tiến trình chỉ NHẮC tên script (prompt/heredoc) ⇒ KHÔNG coi là đang chạy", out)
    # R10 sáng 25/11 05:00 (sau lễ 24/11): phiên=23/11, plan=25/11, bq_freshness MORNING=1; as_of đã đúng ⇒ không refresh
    sb = sandbox("2026-11-23", "2026-11-25", asof="2026-11-23")
    rc, out, c = run(sb, "--retry", "2026-11-25T05:00:00")
    chk(rc == 0 and "phiên=2026-11-23 plan=2026-11-25" in out and "refresh" not in c and "bqf MORNING=1" in c
        and "send --account SpaceX --second-chance --plan-date 2026-11-25 NOTE=yes" in c
        and "send --account ZaloPay --second-chance --plan-date 2026-11-25 NOTE=yes" in c
        and "TELEGRAM ✅" in c and "auto_exit_inject" in c and "CHƯA chạy" in c,
        "R10 05:00 25/11: phiên 23/11, bq_freshness morning; gửi kèm cảnh báo chuỗi inject/auto-exit CHƯA chạy (+Telegram)", out + c)
    # R12 1 account ĐÃ có plan (đã duyệt) ⇒ KHÔNG bị ghi đè, chỉ lập + gửi account vắng
    appr = json.dumps({"plan_date": "2026-11-25", "orders": [{"ticker": "AAA"}], "approved_by": "user"})
    sb = sandbox("2026-11-23", "2026-11-25", asof="2026-11-23", raw_plans={"SpaceX": appr})
    rc, out, c = run(sb, "--retry", "2026-11-25T05:00:00")
    sp = (sb / "wc" / "data" / "trade_plans" / "plan_SpaceX_2026-11-25.json").read_text()
    chk(sp == appr and "dispatch SpaceX" not in c and "dispatch ZaloPay" in c and "SKIP_EXISTING=1" in c
        and "send --account ZaloPay" in c and "send --account SpaceX" not in c,
        "R12 SpaceX đã có plan duyệt ⇒ không ghi đè, không gửi lại; chỉ ZaloPay được lập + gửi", out + c)
    # R13 plan CÓ FILE nhưng hỏng ⇒ không retry (không ghi đè), để tăng cấp
    sb = sandbox("2026-11-23", "2026-11-25", plans=("SpaceX",),
                 raw_plans={"ZaloPay": json.dumps({"plan_date": "2026-11-25", "orders": "BROKEN"})})
    rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    chk("INVALID" in out and "bqf" not in c and not st(sb, "2026-11-25"), "R13 plan hỏng (orders không phải list) ⇒ SKIP, không ghi đè", out + c)
    # R14 khoá: retry khác đang chạy ⇒ LOCKED; bq_freshness đang chạy ⇒ WAIT (không đánh dấu)
    sb = sandbox("2026-11-23", "2026-11-25")
    h = hold(sb / "state" / "locks" / "plan_gate_recovery_retry.lock") if (sb / "state" / "locks").mkdir() is None else None
    h.stdout.readline()
    try:
        rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    finally:
        h.kill()
    chk("LOCKED" in out and "bqf" not in c and not st(sb, "2026-11-25"), "R14 flock retry đang bị giữ ⇒ LOCKED, không làm gì", out + c)
    h = hold(sb / "bqf.lock"); h.stdout.readline()
    try:
        rc, out, c = run(sb, "--retry", "2026-11-23T20:00:00")
    finally:
        h.kill()
    chk("WAIT" in out and "bq_freshness_check.sh đang chạy" in out and "bqf" not in c and not st(sb, "2026-11-25"),
        "R15 bq_freshness đang giữ khoá ⇒ WAIT, không đánh dấu retry", out + c)
    # R11 bị kill giữa chừng (mốc retry có, chưa có result) ⇒ không chạy lại
    sb = sandbox("2026-11-23", "2026-11-25")
    (sb / "state" / "plan_gate_recovery").mkdir()
    (sb / "state" / "plan_gate_recovery" / "2026-11-25.json").write_text(json.dumps({"retry": {"started_at": "x"}}))
    rc, out, c = run(sb, "--retry", "2026-11-23T21:00:00")
    chk("RETRY_ALREADY_DONE" in out and "bqf" not in c, "R11 mốc retry ghi TRƯỚC khi chạy ⇒ bị kill giữa chừng vẫn không lặp", out + c)

    # E1 07:30 25/11 thiếu plan ⇒ tăng cấp 1 lần, đủ lệnh khôi phục + hạn
    sb = sandbox("2026-11-23", "2026-11-25")
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk(rc == 0 and "TELEGRAM 🚨 TĂNG CẤP" in c and "DISCORD[trading_daily] 🚨 TĂNG CẤP" in c
        and "SpaceX, ZaloPay" in out and "MIKE_MORNING_RUN=1 ./daily_refresh_v34b_linux.sh" in out
        and "MIKE_MORNING_RUN=1 " in out and "bq_freshness_check.sh" in out and "trước 08:30" in out
        and "depth phiên 2026-11-23" in out and "DT5G as_of=2026-11-20 (cần 2026-11-23)" in out
        and st(sb, "2026-11-25").get("escalated"),
        "E1 07:30 25/11 thiếu plan ⇒ Telegram+Discord, nêu nguyên nhân đo, lệnh khôi phục đúng thứ tự, hạn 08:30", out + c)
    n_before = c.count("\n")
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:40:00")
    chk("ALREADY_ESCALATED" in out and c.count("\n") == n_before, "E2 07:40 ⇒ không gửi lại (1 lần)", out + c)
    sb = sandbox("2026-11-20", "2026-11-24")
    rc, out, c = run(sb, "--escalate", "2026-11-24T07:30:00")
    chk(rc == 0 and "ngày nghỉ, bỏ qua" in out and "is_holiday(2026-11-24)=True" in out and "TELEGRAM" not in c,
        "E3 24/11 (lễ) ⇒ 'ngày nghỉ, bỏ qua', không báo động", out + c)
    sb = sandbox("2026-11-23", "2026-11-25", plans=("SpaceX", "ZaloPay"))
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk("OK plan" in out and "TELEGRAM" not in c, "E4 plan đủ ⇒ không tăng cấp", out + c)
    sb = sandbox("2026-11-23", "2026-11-25", plans=("SpaceX",))
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk("CHƯA CÓ: ZaloPay." in out, "E5 thiếu đúng 1 account ⇒ chỉ nêu ZaloPay", out)
    sb = sandbox("2026-11-23", "2026-11-25")
    (sb / "notify_rc").write_text("1")
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk(rc == 3 and not st(sb, "2026-11-25").get("escalated"), "E6 không kênh nào nhận ⇒ rc=3, KHÔNG đánh dấu (07:40 gửi lại)", out)
    (sb / "notify_rc").write_text("0")
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:40:00")
    chk(rc == 0 and st(sb, "2026-11-25").get("escalated"), "E7 07:40 kênh hồi ⇒ gửi + đánh dấu", out)
    sb = sandbox("2026-11-23", "2026-11-25", depth_rc=1)
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk("KHÔNG nới ngưỡng" in out, "E8 dữ liệu nền vẫn dưới ngưỡng ⇒ tin nói rõ KHÔNG nới ngưỡng", out)
    # E9 plan CÓ FILE nhưng hỏng ⇒ vẫn là THIẾU (kiểm nội dung, không chỉ tồn tại file)
    sb = sandbox("2026-11-23", "2026-11-25", plans=("SpaceX",),
                 raw_plans={"ZaloPay": json.dumps({"plan_date": "2026-11-25", "orders": "BROKEN"})})
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk("CHƯA CÓ: ZaloPay." in out and "TELEGRAM 🚨" in c, "E9 ZaloPay orders hỏng ⇒ tăng cấp đúng ZaloPay", out + c)
    sb = sandbox("2026-11-23", "2026-11-25", raw_plans={"SpaceX": json.dumps({"plan_date": "2026-11-24", "orders": []})},
                 plans=("ZaloPay",))
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk("CHƯA CÓ: SpaceX." in out, "E9b plan_date sai ⇒ coi là thiếu", out)
    # E10 retry ĐANG CHẠY (mốc có, chưa result, khoá bị giữ) ⇒ nói rõ + cấm chạy tay song song
    sb = sandbox("2026-11-23", "2026-11-25")
    (sb / "state" / "plan_gate_recovery").mkdir()
    (sb / "state" / "plan_gate_recovery" / "2026-11-25.json").write_text(json.dumps({"retry": {"started_at": "2026-11-25T07:20:00"}}))
    (sb / "state" / "locks").mkdir()
    h = hold(sb / "state" / "locks" / "plan_gate_recovery_retry.lock"); h.stdout.readline()
    try:
        rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    finally:
        h.kill()
    chk("ĐANG CHẠY (bắt đầu 2026-11-25T07:20:00" in out and "KHÔNG chạy tay bq_freshness_check.sh" in out
        and "chưa chạy" not in out, "E10 retry đang chạy ⇒ không báo 'chưa chạy', cảnh báo không chạy tay song song", out)
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:40:00")
    chk("ALREADY_ESCALATED" in out, "E10b đã tăng cấp ⇒ không lặp", out)
    sb = sandbox("2026-11-23", "2026-11-25")
    (sb / "state" / "plan_gate_recovery").mkdir()
    (sb / "state" / "plan_gate_recovery" / "2026-11-25.json").write_text(json.dumps({"retry": {"started_at": "2026-11-25T07:20:00"}}))
    rc, out, c = run(sb, "--escalate", "2026-11-25T07:30:00")
    chk("bị NGẮT giữa chừng" in out and "KHÔNG chạy tay" not in out, "E11 mốc có, không ai giữ khoá ⇒ 'bị NGẮT giữa chừng'", out)
    src = TARGET.read_text()
    chk(all(x not in src for x in ("bot_execute", "run_bot.sh", "BOT_STOP\"", "trading_rules.json\"", "dispatch.sh")),
        "B1 ranh giới: script không gọi bot/đặt lệnh/BOT_STOP/trading_rules/dispatch trực tiếp", "")


if __name__ == "__main__":
    try:
        main()
    finally:
        for d in TMP:
            shutil.rmtree(d, ignore_errors=True)
    print(f"plan_gate_recovery_selfcheck: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    sys.exit(1 if FAILS else 0)
