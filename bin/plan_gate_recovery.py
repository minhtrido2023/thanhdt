#!/usr/bin/env python3
"""Cổng plan T+1 FAIL vì DỮ LIỆU NỀN ⇒ retry 1 lần có giới hạn + TĂNG CẤP 1 lần (thay vì nhắc lặp).

Sự cố "không ra plan 25/11" (user duyệt B 25/11/2026): cổng 19:00 FAIL (depth ticker_prune + DT5G
publisher-evidence) ⇒ không dispatch DollarBill ⇒ thiếu plan; cổng "KHÔNG tự phục hồi" và
gate_block_question chỉ REMIND lặp, không ai tăng cấp.

--retry    (cron 20 phút/lần 19:40–23:20 và 05:00–07:00 ICT)
  Khi: plan phiên kế (NEXT) còn thiếu cho ≥1 account live, VÀ artifact state/bq_freshness_gate_last.json
  (do bq_freshness_check.sh ghi) cho đúng phiên đó báo FAIL ở cổng dữ liệu nền (prune_depth/dt5g_publisher),
  VÀ điều kiện ĐO LẠI đã hồi phục (bin/prune_depth_gate.py --date <phiên> rc=0 — CÙNG ngưỡng, KHÔNG nới),
  VÀ daily_refresh không đang chạy, VÀ chưa retry cho NEXT ⇒ chạy ĐÚNG MỘT LẦN chuỗi có sẵn:
      [daily_refresh_v34b_linux.sh MIKE_MORNING_RUN=1 nếu DT5G as_of ≠ phiên] → bq_freshness_check.sh
  (bq_freshness tự dispatch DollarBill theo đường hiện có — plan vẫn phải được user duyệt như thường).
  Rồi chờ file plan (≤45') và gửi lại bằng send_plan_report.sh --second-chance --plan-date NEXT.
  Mốc "đã retry" ghi TRƯỚC khi chạy (bị kill giữa chừng vẫn không lặp — §3 idempotent).
--escalate (cron 07:30 + 07:40 ICT T2-T6)
  Hôm nay là ngày giao dịch mà plan hôm nay còn thiếu ⇒ Telegram + Discord MỘT lần kèm nguyên nhân đo được,
  ĐÚNG lệnh khôi phục và hạn giờ. Không giao dịch ⇒ "ngày nghỉ, bỏ qua".
RANH GIỚI CỨNG: KHÔNG tự dựng plan, KHÔNG đặt lệnh, KHÔNG đụng trading_rules.json/BOT_STOP, KHÔNG nới ngưỡng.
rc: 0 ổn/không cần làm · 1 retry chạy nhưng chưa ra plan · 3 tăng cấp không gửi được kênh nào.
Env test: MIKE_NOW_ICT, PGR_WC_ROOT, PGR_STATE_DIR, PGR_BIN (thư mục chứa các script được gọi), PGR_PLAN_WAIT_S.
"""
import argparse
import datetime as dt
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


def live_accounts():
    r = subprocess.run([sys.executable, "-c", "from trading_bot.config import live_dnse_labels;"
                        "print(' '.join(live_dnse_labels()))"], cwd=str(WC), capture_output=True, text=True, timeout=60)
    labs = r.stdout.split()
    if r.returncode != 0 or not labs:
        raise RuntimeError(f"không đọc được account live (rc={r.returncode}): {(r.stderr or r.stdout).strip()[-200:]}")
    return labs


def plan_ok(acct, date):
    p = WC / "data" / "trade_plans" / f"plan_{acct}_{date}.json"
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
        return str(j.get("plan_date", j.get("date"))) == str(date) and isinstance(j.get("orders"), list)
    except (OSError, ValueError, AttributeError):
        return False


def missing_plans(date):
    return [a for a in live_accounts() if not plan_ok(a, date)]


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
    miss = missing_plans(nxt)
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
    if refresh_running():
        print(f"{tag}: WAIT — daily_refresh_v34b_linux.sh đang chạy, đợi lượt sau")
        return 0
    drc, dline = depth(session)
    if drc != 0:
        print(f"{tag}: CHƯA HỒI PHỤC — {dline} (rc={drc}); KHÔNG nới ngưỡng, đợi lượt sau")
        return 0
    asof = dt5g_as_of()
    rec["retry"] = {"started_at": now.isoformat(timespec="seconds"), "session": str(session), "kinds": kinds,
                    "depth": dline, "dt5g_as_of_before": asof, "missing": miss}
    st_save(nxt, rec)   # ghi TRƯỚC khi chạy: bị kill giữa chừng cũng không retry lần 2
    print(f"{tag}: RETRY 1/1 — cổng FAIL {kinds}, đo lại {dline}, DT5G as_of={asof}")
    steps = []
    if asof != str(session):
        rc, out = run([str(WC / "daily_refresh_v34b_linux.sh")], {"MIKE_MORNING_RUN": "1"})
        asof2 = dt5g_as_of()
        steps.append(f"daily_refresh rc={rc} as_of→{asof2}")
        if asof2 != str(session):
            return _retry_done(nxt, rec, tag, steps, f"DT5G vẫn chưa publish phiên {session} (as_of={asof2}): {out[-200:]}")
    morning = now.date() != session
    rc, out = run([str(BIN / "bq_freshness_check.sh"), "--quiet"], {"MIKE_MORNING_RUN": "1"} if morning else None)
    steps.append(f"bq_freshness{' (morning)' if morning else ''} rc={rc}")
    if rc != 0:
        return _retry_done(nxt, rec, tag, steps, f"bq_freshness_check vẫn FAIL: {out[-200:]}")
    t0 = time.time()
    while missing_plans(nxt) and time.time() - t0 < PLAN_WAIT_S:
        time.sleep(30)
    miss2 = missing_plans(nxt)
    if miss2:
        return _retry_done(nxt, rec, tag, steps, f"DollarBill đã dispatch nhưng sau {PLAN_WAIT_S // 60}' vẫn thiếu plan {miss2}")
    for a in miss:
        rc, out = run([str(BIN / "send_plan_report.sh"), "--account", a, "--second-chance", "--plan-date", str(nxt)], timeout=900)
        steps.append(f"send_plan_report {a} rc={rc}")
    return _retry_done(nxt, rec, tag, steps, None)


def _retry_done(nxt, rec, tag, steps, err):
    rec["retry"].update(result="ok" if not err else "fail", steps=steps, error=err,
                        finished_at=now_ict().isoformat(timespec="seconds"))
    st_save(nxt, rec)
    if err:
        msg = (f"🟠 Plan {nxt}: retry tự động 1/1 sau khi dữ liệu nền đo lại đạt ngưỡng — CHƯA ra plan. {err}. "
               f"Các bước: {'; '.join(steps)}. Không retry thêm; 07:30 sẽ tăng cấp kèm lệnh khôi phục nếu vẫn thiếu.")
    else:
        msg = (f"✅ Plan {nxt}: retry tự động 1/1 thành công sau khi dữ liệu nền hồi phục ({'; '.join(steps)}). "
               "Plan đã gửi lại — vẫn cần duyệt như thường lệ.")
    print(f"{tag}: {msg}")
    notify(msg, telegram=bool(err))
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
    cause = [f"depth phiên {session}: {dline}",
             f"DT5G as_of={asof} (cần {session})",
             f"cổng 19:00 gần nhất: phiên {gl.get('session', '?')} failed={gl.get('failed', '?')} kinds={gl.get('data_fail_kinds', '?')}",
             f"retry tự động: {retry.get('result', 'chưa chạy') if retry else 'chưa chạy'}"
             + (f" ({retry.get('error')})" if retry.get("error") else "")]
    cmds = []
    if drc != 0:
        cmds.append(f"⛔ Dữ liệu nền CHƯA đạt ngưỡng ({dline}) — KHÔNG nới ngưỡng; kiểm tra ingest ticker_prune với team dữ liệu, "
                    "đạt ngưỡng rồi mới chạy các lệnh dưới.")
    if asof != str(session):
        cmds.append(f"cd {WC} && MIKE_MORNING_RUN=1 ./daily_refresh_v34b_linux.sh")
    cmds.append(f"MIKE_MORNING_RUN=1 {ROOT}/bin/bq_freshness_check.sh")
    cmds.append("duyệt plan như thường lệ khi DollarBill ghi xong (send_plan_report --second-chance tự gửi nếu cần: "
                + " ; ".join(f"{ROOT}/bin/send_plan_report.sh --account {a} --second-chance" for a in miss) + ")")
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
