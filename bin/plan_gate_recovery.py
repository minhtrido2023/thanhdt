#!/usr/bin/env python3
"""Cổng plan T+1 FAIL vì DỮ LIỆU NỀN ⇒ retry 1 lần có giới hạn + TĂNG CẤP 1 lần (thay vì nhắc lặp).

Sự cố "không ra plan 25/11" (user duyệt B 25/11/2026): cổng 19:00 FAIL (depth ticker_prune + DT5G
publisher-evidence) ⇒ không dispatch DollarBill ⇒ thiếu plan; cổng "KHÔNG tự phục hồi" và
gate_block_question chỉ REMIND lặp, không ai tăng cấp.

--retry    (cron 20 phút/lần 19:40–23:20 và 05:00–07:00 ICT)
  Khi: plan phiên kế (NEXT) còn thiếu cho ≥1 account live, VÀ artifact state/bq_freshness_gate_last.json
  (do bq_freshness_check.sh ghi) cho đúng phiên đó báo FAIL ở cổng dữ liệu nền (prune_depth/dt5g_publisher),
  VÀ điều kiện ĐO LẠI đã hồi phục (bin/prune_depth_gate.py --date <phiên> rc=0 — CÙNG ngưỡng, KHÔNG nới),
  VÀ daily_refresh / bq_freshness_check không đang chạy, VÀ chưa retry cho NEXT ⇒ chạy ĐÚNG MỘT LẦN:
      [daily_refresh_v34b_linux.sh MIKE_MORNING_RUN=1 nếu DT5G as_of ≠ phiên] → bq_freshness_check.sh
      với BQF_SKIP_EXISTING_PLANS=1 (CHỈ dispatch DollarBill cho account CHƯA có file plan — không ghi đè
      plan có thể đã duyệt). Plan hỏng (file có, INVALID) KHÔNG retry — cần người, 07:30 tăng cấp.
  Chờ plan của account vắng (≤45'), rồi GỬI theo giờ (arch-review vòng 2 #2 — không bỏ qua chuỗi tối):
      trước 21:00 ⇒ KHÔNG tự gửi: cron 20:20 merge_park/20:30 inject_discretionary/20:40 auto_exit/20:50 drift
                    → 21:00 send_plan_report (+ late_plan_catchup 21:45 nếu plan ra sau chuỗi park) lo;
      21:00–23:59 ⇒ bin/late_plan_catchup.sh (có khoá; chạy park→merge→inject→auto_exit RỒI mới gửi);
      buổi sáng   ⇒ send_plan_report --second-chance --plan-date NEXT cho ĐÚNG account vắng, đầu bản gửi ghi
                    rõ chuỗi inject_discretionary/auto_exit/park CHƯA chạy cho plan này (+ Telegram).
  Mốc "đã retry" ghi TRƯỚC khi chạy (bị kill giữa chừng vẫn không lặp — §3 idempotent); flock
  state/locks/plan_gate_recovery_retry.lock ⇒ 2 lượt cron không chồng nhau.
--escalate (cron 07:30 + 07:40 ICT T2-T6)
  Hôm nay là ngày giao dịch mà plan hôm nay còn thiếu ⇒ Telegram + Discord MỘT lần kèm nguyên nhân đo được,
  ĐÚNG lệnh khôi phục và hạn giờ. Không giao dịch ⇒ "ngày nghỉ, bỏ qua".
RANH GIỚI CỨNG: KHÔNG tự dựng plan, KHÔNG đặt lệnh, KHÔNG đụng trading_rules.json/BOT_STOP, KHÔNG nới ngưỡng.
rc: 0 ổn/không cần làm · 1 retry chạy nhưng chưa ra plan · 3 tăng cấp không gửi được kênh nào.
Env test: MIKE_NOW_ICT, PGR_WC_ROOT, PGR_STATE_DIR, PGR_BIN (thư mục chứa các script được gọi), PGR_PLAN_WAIT_S.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = Path(__file__).resolve().parent.parent
WC = Path(os.environ.get("PGR_WC_ROOT") or os.environ.get("WORKDIR_8L") or ROOT.parent)
BIN = Path(os.environ.get("PGR_BIN") or (ROOT / "bin"))
STATE = Path(os.environ.get("PGR_STATE_DIR") or (ROOT / "state"))
os.environ.setdefault("WORKDIR_8L", str(WC))
sys.path.insert(0, str(ROOT / "bin"))
import trading_calendar as TC  # noqa: E402
import plan_presence as PP  # noqa: E402  — MỘT định nghĩa "plan có" (MISSING/INVALID/OK)

DATA_KINDS = {"prune_depth", "dt5g_publisher"}
PLAN_WAIT_S = int(os.environ.get("PGR_PLAN_WAIT_S", "2700"))
DEADLINE_HM = "08:30"   # expected_session.py GUARD_HM: morning mode từ chối lập plan cho hôm nay sau mốc này


def now_ict():
    raw = os.environ.get("MIKE_NOW_ICT")
    return dt.datetime.fromisoformat(raw) if raw else dt.datetime.now(ICT).replace(tzinfo=None)


def prev_session(d):
    d -= dt.timedelta(days=1)
    while not TC.is_trading_day(d):
        d -= dt.timedelta(days=1)
    return d


def next_session(d):
    d += dt.timedelta(days=1)
    while not TC.is_trading_day(d):
        d += dt.timedelta(days=1)
    return d


def expected_session(now):
    """Như bin/expected_session.py: hôm nay nếu là phiên và đã ≥17:00, ngược lại phiên trước."""
    d = now.date()
    return d if (TC.is_trading_day(d) and now.hour >= 17) else prev_session(d)


def plan_class(acct, date):
    return PP.classify(PP.plan_path(WC, acct, date), date)


def missing_plans(date, accts=None):
    """Account live KHÔNG có plan OK (MISSING + INVALID)."""
    return [a for a in (accts or PP.live_accounts(WC)) if plan_class(a, date) != "OK"]


def dt5g_as_of():
    try:
        return str(json.loads((WC / "deploy_golive_dt5g_v4" / "golive_state_today.json").read_text())["as_of"])
    except (OSError, ValueError, KeyError) as exc:
        return f"? ({type(exc).__name__})"


def depth(session):
    try:
        r = subprocess.run([sys.executable, str(BIN / "prune_depth_gate.py"), "--date", str(session)],
                           capture_output=True, text=True, timeout=300)
        line = next((l for l in r.stdout.splitlines() if l.startswith("PRUNE_DEPTH ")), (r.stdout + r.stderr).strip()[-200:])
        return r.returncode, line
    except Exception as exc:  # noqa: BLE001
        return 2, f"PRUNE_DEPTH UNMEASURABLE ({type(exc).__name__}: {exc})"


def gate_last():
    try:
        return json.loads((STATE / "bq_freshness_gate_last.json").read_text())
    except (OSError, ValueError):
        return None


def st_path(date):
    return STATE / "plan_gate_recovery" / f"{date}.json"


def st_load(date):
    try:
        return json.loads(st_path(date).read_text())
    except (OSError, ValueError):
        return {}


def st_save(date, rec):
    p = st_path(date)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    os.replace(tmp, p)


def refresh_running():
    """daily_refresh đang chạy? Soát argv CHÍNH XÁC trong /proc — KHÔNG `pgrep -f <tên>`: khớp nhầm mọi tiến
    trình chỉ NHẮC tên script trong dòng lệnh (prompt dispatch của agent, `bash -c` chứa heredoc…) — đo thật
    25/11: tiến trình claude của chính job này khớp ⇒ retry sẽ WAIT mãi."""
    name = os.environ.get("PGR_REFRESH_SCRIPT", "daily_refresh_v34b_linux.sh")
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            argv = (d / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        argv = [x.decode("utf-8", "replace") for x in argv if x]
        if not argv:
            continue
        if os.path.basename(argv[0]) == name:
            return True
        if os.path.basename(argv[0]) in ("bash", "sh") and len(argv) > 1 and os.path.basename(argv[1]) == name:
            return True
    return False


LOCK_DIR = STATE / "locks"
BQF_LOCK = Path(os.environ.get("BQF_LOCK_FILE") or (ROOT / "state" / "locks" / "bq_freshness_check.lock"))


def try_lock(path):
    """flock không chặn → fd (giữ tới khi tiến trình thoát) hoặc None nếu đang bị giữ."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError:
        os.close(fd)
        return None


def lock_busy(path):
    fd = try_lock(path)
    if fd is None:
        return True
    os.close(fd)
    return False


def run(cmd, env_extra=None, timeout=7200):
    env = dict(os.environ, **(env_extra or {}))
    try:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()[-400:]
    except Exception as exc:  # noqa: BLE001
        return 124, f"{type(exc).__name__}: {exc}"


def notify(msg, telegram):
    ok = run([str(BIN / "notify_thread.sh"), msg, "trading_daily"], timeout=60)[0] == 0
    if telegram:
        ok = (run([str(BIN / "notify.sh"), msg], timeout=60)[0] == 0) or ok
    return ok


def cmd_retry(now):
    session = expected_session(now)
    nxt = next_session(session)
    tag = f"[plan_gate_recovery --retry] {now:%Y-%m-%d %H:%M} ICT phiên={session} plan={nxt}"
    lock_fd = try_lock(LOCK_DIR / "plan_gate_recovery_retry.lock")
    if lock_fd is None:
        print(f"{tag}: LOCKED — lượt retry khác đang chạy, không chồng")
        return 0
    accts = PP.live_accounts(WC)
    miss = missing_plans(nxt, accts)
    if not miss:
        print(f"{tag}: OK plan đủ mọi account — không cần retry")
        return 0
    rec = st_load(nxt)
    if rec.get("retry"):
        print(f"{tag}: RETRY_ALREADY_DONE ({rec['retry'].get('result', 'đang/đã chạy')}) — giới hạn 1 lần, không lặp")
        return 0
    gl = gate_last()
    kinds = sorted(set((gl or {}).get("data_fail_kinds") or []) & DATA_KINDS)
    if not gl or str(gl.get("session")) != str(session) or not gl.get("failed") or not kinds:
        print(f"{tag}: SKIP — thiếu plan {miss} nhưng không có bằng chứng cổng 19:00 FAIL vì dữ liệu nền cho phiên "
              f"{session} (gate_last={gl}) — không retry (tăng cấp 07:30 vẫn bắt)")
        return 0
    absent = [a for a in miss if plan_class(a, nxt) == "MISSING"]
    if not absent:
        print(f"{tag}: SKIP — plan {miss} CÓ FILE nhưng HỎNG (INVALID) — không ghi đè, không retry; cần người "
              "(07:30 tăng cấp)")
        return 0
    if refresh_running():
        print(f"{tag}: WAIT — daily_refresh_v34b_linux.sh đang chạy, đợi lượt sau")
        return 0
    if lock_busy(BQF_LOCK):
        print(f"{tag}: WAIT — bq_freshness_check.sh đang chạy (khoá {BQF_LOCK}), đợi lượt sau")
        return 0
    drc, dline = depth(session)
    if drc != 0:
        print(f"{tag}: CHƯA HỒI PHỤC — {dline} (rc={drc}); KHÔNG nới ngưỡng, đợi lượt sau")
        return 0
    asof = dt5g_as_of()
    rec["retry"] = {"started_at": now.isoformat(timespec="seconds"), "pid": os.getpid(), "session": str(session),
                    "kinds": kinds, "depth": dline, "dt5g_as_of_before": asof, "missing": miss, "absent": absent}
    st_save(nxt, rec)   # ghi TRƯỚC khi chạy: bị kill giữa chừng cũng không retry lần 2
    print(f"{tag}: RETRY 1/1 — cổng FAIL {kinds}, đo lại {dline}, DT5G as_of={asof}, lập cho {absent}")
    steps = []
    if asof != str(session):
        rc, out = run([str(WC / "daily_refresh_v34b_linux.sh")], {"MIKE_MORNING_RUN": "1"})
        asof2 = dt5g_as_of()
        steps.append(f"daily_refresh rc={rc} as_of→{asof2}")
        if asof2 != str(session):
            return _retry_done(nxt, rec, tag, steps, f"DT5G vẫn chưa publish phiên {session} (as_of={asof2}): {out[-200:]}")
    morning = now.date() != session
    env = {"BQF_SKIP_EXISTING_PLANS": "1"}
    if morning:
        env["MIKE_MORNING_RUN"] = "1"
    rc, out = run([str(BIN / "bq_freshness_check.sh"), "--quiet"], env)
    steps.append(f"bq_freshness{' (morning)' if morning else ''} skip-existing rc={rc}")
    if rc != 0:
        return _retry_done(nxt, rec, tag, steps, f"bq_freshness_check vẫn FAIL: {out[-200:]}")
    t0 = time.time()
    while missing_plans(nxt, absent) and time.time() - t0 < PLAN_WAIT_S:
        time.sleep(30)
    miss2 = missing_plans(nxt, absent)
    if miss2:
        return _retry_done(nxt, rec, tag, steps, f"DollarBill đã dispatch nhưng sau {PLAN_WAIT_S // 60}' vẫn thiếu plan {miss2}")
    t = now_ict()
    if morning:
        note = (f"⚠️ PLAN LẬP BÙ BUỔI SÁNG ({t:%H:%M} ICT, retry tự động): chuỗi tối park_trim/jit_unpark/merge_park, "
                "inject_discretionary (20:30) và auto_exit_inject (20:40, đề xuất SELL LAG/BAL/CAPIT) CHƯA chạy cho "
                "plan này — kiểm tra lệnh BÁN thoát theo thời gian trước khi duyệt.")
        for a in absent:
            rc, out = run([str(BIN / "send_plan_report.sh"), "--account", a, "--second-chance", "--plan-date", str(nxt)],
                          {"PLAN_REPORT_NOTE": note}, timeout=900)
            steps.append(f"send_plan_report {a} rc={rc}")
        return _retry_done(nxt, rec, tag, steps, None, warn=note)
    if t.date() == session and t.hour >= 21:
        rc, out = run([str(BIN / "late_plan_catchup.sh")], timeout=3600)
        steps.append(f"late_plan_catchup rc={rc}")
        return _retry_done(nxt, rec, tag, steps, None if rc == 0 else f"late_plan_catchup rc={rc}: {out[-200:]}")
    steps.append("KHÔNG tự gửi trước 21:00 — chuỗi cron 20:20→20:50 + send_plan_report 21:00 (+ late_plan_catchup 21:45) lo")
    return _retry_done(nxt, rec, tag, steps, None)


def _retry_done(nxt, rec, tag, steps, err, warn=None):
    rec["retry"].update(result="ok" if not err else "fail", steps=steps, error=err,
                        finished_at=now_ict().isoformat(timespec="seconds"))
    st_save(nxt, rec)
    if err:
        msg = (f"🟠 Plan {nxt}: retry tự động 1/1 sau khi dữ liệu nền đo lại đạt ngưỡng — CHƯA ra plan. {err}. "
               f"Các bước: {'; '.join(steps)}. Không retry thêm; 07:30 sẽ tăng cấp kèm lệnh khôi phục nếu vẫn thiếu.")
    else:
        msg = (f"✅ Plan {nxt}: retry tự động 1/1 — DollarBill đã ghi plan sau khi dữ liệu nền hồi phục "
               f"({'; '.join(steps)}). Vẫn cần duyệt như thường lệ." + (f" {warn}" if warn else ""))
    print(f"{tag}: {msg}")
    notify(msg, telegram=bool(err or warn))
    return 1 if err else 0


def cmd_escalate(now):
    today = now.date()
    tag = f"[plan_gate_recovery --escalate] {now:%Y-%m-%d %H:%M} ICT"
    ev = TC.non_trading_evidence(today)
    if ev:
        print(f"{tag}: ngày nghỉ, bỏ qua — {ev}")
        return 0
    miss = missing_plans(today)
    if not miss:
        print(f"{tag}: OK plan {today} đủ mọi account — không tăng cấp")
        return 0
    rec = st_load(today)
    if rec.get("escalated"):
        print(f"{tag}: ALREADY_ESCALATED lúc {rec['escalated'].get('at')} — 1 lần, không lặp")
        return 0
    session = prev_session(today)
    drc, dline = depth(session)
    asof = dt5g_as_of()
    gl = gate_last() or {}
    retry = (rec.get("retry") or {})
    running = bool(retry) and not retry.get("result") and lock_busy(LOCK_DIR / "plan_gate_recovery_retry.lock")
    bqf_busy = lock_busy(BQF_LOCK)
    if not retry:
        rs = "chưa chạy"
    elif retry.get("result"):
        rs = retry["result"] + (f" ({retry.get('error')})" if retry.get("error") else "")
    elif running:
        rs = f"ĐANG CHẠY (bắt đầu {retry.get('started_at')}, chưa có kết quả)"
    else:
        rs = f"bị NGẮT giữa chừng (bắt đầu {retry.get('started_at')}, không có kết quả, tiến trình không còn)"
    cause = [f"depth phiên {session}: {dline}",
             f"DT5G as_of={asof} (cần {session})",
             f"cổng 19:00 gần nhất: phiên {gl.get('session', '?')} failed={gl.get('failed', '?')} kinds={gl.get('data_fail_kinds', '?')}",
             f"retry tự động: {rs}"]
    cmds = []
    if running or bqf_busy:
        cmds.append("⛔ KHÔNG chạy tay bq_freshness_check.sh lúc này — "
                    + ("retry tự động ĐANG CHẠY" if running else "bq_freshness_check.sh đang có lượt chạy")
                    + " (chạy song song = dispatch DollarBill 2 lần). Đợi nó xong rồi kiểm lại data/trade_plans/.")
    if drc != 0:
        cmds.append(f"⛔ Dữ liệu nền CHƯA đạt ngưỡng ({dline}) — KHÔNG nới ngưỡng; kiểm tra ingest ticker_prune với team dữ liệu, "
                    "đạt ngưỡng rồi mới chạy các lệnh dưới.")
    if asof != str(session):
        cmds.append(f"cd {WC} && MIKE_MORNING_RUN=1 ./daily_refresh_v34b_linux.sh")
    cmds.append(f"MIKE_MORNING_RUN=1 {ROOT}/bin/bq_freshness_check.sh   (morning mode tự bỏ qua account đã có file plan)")
    cmds.append("khi DollarBill ghi xong: gửi để duyệt — "
                + " ; ".join(f"{ROOT}/bin/send_plan_report.sh --account {a} --second-chance --plan-date {today}" for a in miss)
                + " — LƯU Ý chuỗi inject_discretionary/auto_exit_inject (đề xuất SELL thoát theo thời gian) CHƯA chạy "
                  "cho plan lập buổi sáng, kiểm tra trước khi duyệt")
    msg = (f"🚨 TĂNG CẤP {now:%H:%M} ICT — PLAN PHIÊN HÔM NAY {today:%d/%m} CHƯA CÓ: {', '.join(miss)}.\n"
           "Nguyên nhân đo được: " + " · ".join(cause) + "\n"
           "Lệnh khôi phục (chạy tay, theo thứ tự):\n" + "\n".join(f"  {i + 1}) {c}" for i, c in enumerate(cmds)) + "\n"
           f"HẠN: trước {DEADLINE_HM} ICT hôm nay (sau mốc này morning mode từ chối lập plan cho hôm nay). "
           "Quá hạn ⇒ phiên hôm nay không có plan duyệt ⇒ bot HOLD (không đặt lệnh). "
           "Hệ thống KHÔNG tự dựng plan/đặt lệnh. Tin này gửi 1 lần.")
    print(msg)
    ok = notify(msg, telegram=True)
    if not ok:
        print(f"{tag}: NOTIFY_FAILED — không kênh nào nhận; lượt cron sau gửi lại", file=sys.stderr)
        return 3
    rec["escalated"] = {"at": now.isoformat(timespec="seconds"), "missing": miss, "cause": cause}
    st_save(today, rec)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--retry", action="store_true")
    g.add_argument("--escalate", action="store_true")
    a = ap.parse_args(argv)
    now = now_ict()
    try:
        return cmd_retry(now) if a.retry else cmd_escalate(now)
    except RuntimeError as exc:
        print(f"[plan_gate_recovery] ERROR {exc}", file=sys.stderr)
        if a.escalate:
            notify(f"🚨 plan_gate_recovery --escalate KHÔNG chạy được ({exc}) — tự kiểm plan hôm nay trước {DEADLINE_HM} ICT.",
                   telegram=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
