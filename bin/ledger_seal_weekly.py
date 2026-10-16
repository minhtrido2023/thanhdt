#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt sổ đơn vị quỹ ĐỊNH KỲ (tuần) cho SpaceX rồi ZaloPay — vỏ cron của `nav_unit_ledger.py --seal`.

Thiết kế user duyệt 2026-10-16 10:35 ICT, job Taylor_20261016_033549:
  · Lịch: thứ Bảy 07:30 ICT. Chốt tới THỨ SÁU CỦA TUẦN TRƯỚC — chính xác: phiên VN cuối cùng d ≤ thứ
    Sáu tuần trước mà từ sau d tới trước hôm nay có ≥ MIN_LAG_SESSIONS (5) phiên (`seal_asof`). Tuần
    thường = đúng thứ Sáu tuần trước; tuần có lễ/Tết chen giữa ⇒ lùi thêm, không bao giờ chốt dòng
    còn non hơn 5 phiên. Lịch phiên = `account_cash_flows._is_session_day` (CÙNG lịch với cổng
    "thiếu dòng phiên" của nav_unit_ledger, gốc `trading_bot.vn_market.is_holiday`), neo ICT tường minh.
  · Gọi ĐÚNG `nav_unit_ledger.py --account <TK> --seal --real-data --asof <ngày>` — KHÔNG BAO GIỜ thêm
    --accept-preclose / --restate / --force. Env con đã gỡ WC_ROOT (CLI neo theo marker cây của nó).
  · FAIL-CLOSED: TK nào rc≠0 (trừ NothingToSeal) ⇒ dừng, KHÔNG chốt TK sau, in 8 dòng cuối đầu ra THẬT
    của CLI (§29 — không đoán nguyên nhân), rc≠0 để `fund_bench_cron.sh` báo Trading Daily.
  · NothingToSeal (CLI rc=2 + dòng `TỪ CHỐI nav_unit_ledger (<TK>) [NothingToSeal]`) = đã chốt tới mốc
    đó ⇒ bình thường, đi tiếp, rc=0. Mọi rc=2 KHÁC là từ chối thật.
  · Mỗi TK chốt XONG ⇒ ngay lập tức (trước khi sang TK sau): parse đúng một dòng
    `SEAL_MD5 <TK> <md5 sổ> <md5 manifest>` → thêm vào cuối `kb/fund_ledger_anchors.txt` (chỉ-thêm,
    nguyên tử, idempotent: mốc mới nhất của TK đã là dòng đó ⇒ không thêm, không post lại) → post bus
    `append_event.sh Mike finding fund-unit-ledger-seal-<YYYYMMDD>`. TK sau lỗi thì TK trước vẫn có mốc.
    Commit file mốc: `consolidate.sh` (cron :07 mỗi giờ) `git add kb/` + commit `-- kb/` khi có event
    mới — event bus vừa post chính là event mới đó.
  · Chống chạy chồng: flock không chờ `state/ledger_seal_weekly.lock`; từ chối khi đang ở khung ghi
    nav_history 19:00–22:00 ICT hoặc có tiến trình daily_nav_snapshot / nav_snapshot_daily /
    nav_sync_retry / eod_trading_report đang chạy.
  · Code worktree/bản sao KHÔNG được chốt vào cây dữ liệu thật: CLI sẽ ghi vào cây thật mà file này
    không nằm ở `CANONICAL_MIKE/bin` ⇒ từ chối (rc=64) trước khi gọi gì.

Mã thoát: 0 OK (kể cả NothingToSeal) · 1 CLI từ chối/lỗi, thiếu dòng SEAL_MD5, ghi mốc/bus lỗi ·
4 bận (khoá, khung giờ, tiến trình ghi nav_history) · 64 sai cách gọi (code ngoài cây canonical).

Dùng:  python3 mike/bin/ledger_seal_weekly.py [--print-asof]
Selfcheck: python3 mike/bin/ledger_seal_weekly_selfcheck.py (env -u TZ và TZ=Pacific/Kiritimati).
Biến môi trường chỉ để TEST (prod để trống): NAV_UNIT_LEDGER_CLI, LEDGER_ANCHORS_FILE, APPEND_EVENT_CMD,
LEDGER_SEAL_LOCK, LEDGER_SEAL_PROC_DIR, LEDGER_SEAL_NOW_ICT (ISO, giờ ICT), LEDGER_SEAL_CLI_TIMEOUT (giây).
"""
import argparse
import datetime
import fcntl
import json
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# Gỡ WC_ROOT TRƯỚC mọi import/subprocess: dispatch.sh export biến này theo phép đếm cấp; cả lịch phiên
# lẫn CLI con phải neo theo marker cây của chính file, không theo env thừa hưởng.
os.environ.pop("WC_ROOT", None)

import account_cash_flows as _acf  # noqa: E402

ROOT = os.path.dirname(HERE)
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ACCOUNTS = ("SpaceX", "ZaloPay")          # thứ tự cố định: SpaceX rồi ZaloPay
MIN_LAG_SESSIONS = 5
CANONICAL_MIKE = "/home/trido/thanhdt/WorkingClaude/mike"
CANONICAL_REAL_DIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
WRITE_WINDOW = (datetime.time(19, 0), datetime.time(22, 0))   # nav_sync_retry */15 tới 21:45 + biên
# So khớp TÊN FILE của từng đối số (basename ==), không khớp chuỗi con: tiến trình `sh -c "<dòng cron>"`
# mang cả dòng crontab (kể cả comment) trong MỘT đối số — khớp chuỗi con thì comment nhắc tên một
# writer là đủ để mọi lượt tự từ chối.
NAV_WRITERS = ("daily_nav_snapshot.py", "nav_snapshot_daily.sh", "nav_sync_retry.sh", "eod_trading_report.sh")
TAIL_LINES = 8

CLI = os.environ.get("NAV_UNIT_LEDGER_CLI", os.path.join(HERE, "nav_unit_ledger.py"))
ANCHORS = os.environ.get("LEDGER_ANCHORS_FILE", os.path.join(ROOT, "kb", "fund_ledger_anchors.txt"))
APPEND_EVENT = os.environ.get("APPEND_EVENT_CMD", os.path.join(HERE, "append_event.sh"))
LOCK = os.environ.get("LEDGER_SEAL_LOCK", os.path.join(ROOT, "state", "ledger_seal_weekly.lock"))
PROC = os.environ.get("LEDGER_SEAL_PROC_DIR", "/proc")
CLI_TIMEOUT = int(os.environ.get("LEDGER_SEAL_CLI_TIMEOUT", "600"))
ANCHOR_RE = re.compile(r"^SEAL_MD5 (\S+) ([0-9a-f]{32}) ([0-9a-f]{32})$")


class Busy(Exception):
    pass


def now_ict() -> datetime.datetime:
    fake = os.environ.get("LEDGER_SEAL_NOW_ICT")
    if fake:
        return datetime.datetime.fromisoformat(fake).replace(tzinfo=ICT)
    return datetime.datetime.now(ICT)


def seal_asof(today: datetime.date, is_session=_acf._is_session_day,
              min_lag: int = MIN_LAG_SESSIONS) -> datetime.date:
    """Phiên d cuối cùng ≤ thứ Sáu của tuần TRƯỚC tuần chứa `today`, với ≥ `min_lag` phiên nằm
    trong (d, today) — hai đầu không tính."""
    d = today - datetime.timedelta(days=today.weekday() + 3)
    for _ in range(120):
        if is_session(d):
            lag = sum(1 for k in range(1, (today - d).days) if is_session(d + datetime.timedelta(days=k)))
            if lag >= min_lag:
                return d
        d -= datetime.timedelta(days=1)
    raise ValueError(f"không tìm được phiên chốt trong 120 ngày trước {today}")


def _wc_root_of(path: str):
    """Gốc cây (thư mục có wc_env.sh) mà CLI ở `path` sẽ neo vào khi WC_ROOT đã gỡ."""
    d = os.path.dirname(os.path.realpath(path))
    while True:
        if os.path.isfile(os.path.join(d, "wc_env.sh")):
            return d
        up = os.path.dirname(d)
        if up == d:
            return None
        d = up


def guard_tree() -> str:
    """Chuỗi lỗi nếu code ngoài cây canonical sắp chốt vào cây dữ liệu thật, rỗng nếu được."""
    wc = _wc_root_of(CLI)
    target = os.path.realpath(os.path.join(wc, "data", "execution_logs")) if wc else None
    if target != os.path.realpath(CANONICAL_REAL_DIR):
        return ""
    if os.path.realpath(ROOT) == os.path.realpath(CANONICAL_MIKE) and \
            os.path.realpath(os.path.dirname(CLI)) == os.path.realpath(os.path.join(CANONICAL_MIKE, "bin")):
        return ""
    return (f"code ở {ROOT} (CLI {CLI}) không phải cây canonical {CANONICAL_MIKE} nhưng sẽ chốt vào "
            f"cây dữ liệu thật {CANONICAL_REAL_DIR} — chạy mike/bin/ledger_seal_weekly.py của cây canonical")


def nav_writers_running() -> list:
    found = []
    try:
        pids = [p for p in os.listdir(PROC) if p.isdigit() and int(p) != os.getpid()]
    except OSError:
        return found
    for p in pids:
        try:
            with open(os.path.join(PROC, p, "cmdline"), "rb") as f:
                args = [a.decode("utf-8", "replace") for a in f.read().split(b"\0") if a]
        except OSError:
            continue
        if any(os.path.basename(a) in NAV_WRITERS for a in args):
            found.append(f"pid {p}: {' '.join(args)[:160]}")
    return found


def run_cli(account: str, asof: datetime.date):
    env = dict(os.environ, PYTHONUNBUFFERED="1")
    argv = [sys.executable, CLI, "--account", account, "--seal", "--real-data", "--asof", asof.isoformat()]
    try:
        r = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
                           timeout=CLI_TIMEOUT)
    except subprocess.TimeoutExpired as e:
        part = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return 124, part + (f"\n[ledger_seal_weekly: CLI quá {CLI_TIMEOUT}s, đã bị giết — lần chốt dở (nếu "
                            f"có) được CLI tự hoàn tất ở lượt sau; ledger_anchor_check báo LỆCH nếu sổ đổi "
                            f"mà chưa có mốc]")
    return r.returncode, r.stdout


def is_nothing_to_seal(account: str, rc: int, out: str) -> bool:
    return rc == 2 and re.search(rf"^TỪ CHỐI nav_unit_ledger \({re.escape(account)}\) \[NothingToSeal\]",
                                 out, re.M) is not None


def parse_anchor(account: str, out: str):
    lines = [ln.strip() for ln in out.splitlines() if ln.startswith("SEAL_MD5 ")]
    good = [ln for ln in lines if (m := ANCHOR_RE.match(ln)) and m.group(1) == account]
    return good[0] if len(lines) == 1 and len(good) == 1 else None


def parse_rows(out: str):
    m = re.search(r"— (\d+) dòng, tới (\d{4}-\d{2}-\d{2}); vừa THÊM (\d+) dòng", out)
    return (int(m.group(1)), m.group(2), int(m.group(3))) if m else (None, None, None)


def append_anchor(line: str, account: str, comment: str) -> bool:
    """Thêm `line` vào cuối file mốc (nguyên tử). False = mốc mới nhất của TK đã là `line`."""
    with open(ANCHORS, "rb") as f:
        old = f.read()
    latest = None
    seen = set()
    for ln in old.decode("utf-8").splitlines():
        m = ANCHOR_RE.match(ln.strip())
        if m and m.group(1) == account:
            latest = ln.strip()
            seen.add(latest)
    if latest == line:
        return False
    if line in seen:
        raise ValueError(f"mốc {line!r} đã có nhưng KHÔNG phải mốc mới nhất của {account} "
                         f"({latest!r}) — sổ quay về trạng thái cũ? KHÔNG ghi")
    sep = b"" if not old or old.endswith(b"\n") else b"\n"
    data = old + sep + f"# {comment}\n{line}\n".encode("utf-8")
    tmp = f"{os.path.join(os.path.dirname(ANCHORS), '.' + os.path.basename(ANCHORS))}.tmp.{os.getpid()}"
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, os.stat(ANCHORS).st_mode & 0o777)
        os.replace(tmp, ANCHORS)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return True


def post_bus(topic: str, payload: str):
    r = subprocess.run([APPEND_EVENT, "Mike", "finding", topic, payload], capture_output=True,
                       text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def tail(out: str) -> str:
    lines = out.rstrip("\n").splitlines()[-TAIL_LINES:]
    return "\n".join(lines) if lines else "(CLI không in gì)"


def seal_all(now: datetime.datetime) -> int:
    asof = seal_asof(now.date())
    topic = f"fund-unit-ledger-seal-{now:%Y%m%d}"
    sealed = []
    for acct in ACCOUNTS:
        rc, out = run_cli(acct, asof)
        if is_nothing_to_seal(acct, rc, out):
            print(f"{acct}: NothingToSeal — sổ đã chốt tới/qua {asof}, không làm gì", flush=True)
            continue
        anchor = parse_anchor(acct, out) if rc == 0 else None
        if anchor is None:
            why = (f"rc={rc}" if rc != 0 else "rc=0 nhưng KHÔNG có đúng một dòng 'SEAL_MD5 "
                   f"{acct} <md5> <md5>' — sổ có thể đã ghi mà KHÔNG có mốc ngoài kho")
            print(f"🔴 ledger_seal_weekly: {acct} {why} (asof {asof}); đã chốt+ghi mốc: "
                  f"{', '.join(sealed) or 'không TK nào'}; KHÔNG chốt gì thêm. "
                  f"{TAIL_LINES} dòng cuối đầu ra thật của nav_unit_ledger:", flush=True)
            print(tail(out), flush=True)
            return 1
        total, through, added = parse_rows(out)
        try:
            appended = append_anchor(anchor, acct, f"{now:%Y-%m-%d %H:%M} ICT — chốt tuần tự động "
                                                   f"(ledger_seal_weekly.py) {acct} tới {through or asof}")
        except (OSError, ValueError) as e:
            print(f"🔴 ledger_seal_weekly: {acct} ĐÃ CHỐT ({anchor}) nhưng KHÔNG ghi được mốc vào "
                  f"{ANCHORS}: {type(e).__name__}: {e} — chép tay dòng SEAL_MD5 trên vào file mốc "
                  f"+ post bus; KHÔNG chốt gì thêm.", flush=True)
            return 1
        sealed.append(acct)
        if not appended:
            print(f"{acct}: mốc {anchor} đã là mốc mới nhất — không thêm, không post lại", flush=True)
            continue
        payload = json.dumps({
            "summary": f"Chốt sổ đơn vị quỹ tuần (cron ledger_seal_weekly.py) {acct} tới {through or asof}",
            f"SEAL_MD5_{acct}": anchor, "rows": {acct: total}, "rows_added": {acct: added},
            "through": through or asof.isoformat(), "asof": asof.isoformat(),
            "anchors_file": "kb/fund_ledger_anchors.txt",
        }, ensure_ascii=False)
        brc, bout = post_bus(topic, payload)
        print(f"{acct}: ĐÃ CHỐT tới {through} (+{added} dòng, tổng {total}); mốc đã ghi: {anchor}", flush=True)
        if brc != 0:
            print(f"🔴 ledger_seal_weekly: {acct} đã chốt + ghi mốc nhưng post bus LỖI rc={brc}: "
                  f"{bout[-400:]} — post tay finding {topic}; KHÔNG chốt gì thêm.", flush=True)
            return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--print-asof", action="store_true", help="chỉ in ngày sẽ chốt tới rồi thoát")
    args = ap.parse_args()
    now = now_ict()
    if args.print_asof:
        print(seal_asof(now.date()).isoformat())
        return 0
    bad = guard_tree()
    if bad:
        print(f"🔴 ledger_seal_weekly TỪ CHỐI: {bad}", flush=True)
        return 64
    try:
        os.makedirs(os.path.dirname(LOCK), exist_ok=True)
        with open(LOCK, "a", encoding="utf-8") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Busy(f"khoá {LOCK} đang bị lượt khác giữ")
            if WRITE_WINDOW[0] <= now.time() < WRITE_WINDOW[1]:
                raise Busy(f"{now:%H:%M} ICT nằm trong khung ghi nav_history "
                           f"{WRITE_WINDOW[0]:%H:%M}–{WRITE_WINDOW[1]:%H:%M}")
            writers = nav_writers_running()
            if writers:
                raise Busy("đang có tiến trình ghi nav_history: " + "; ".join(writers))
            return seal_all(now)
    except Busy as e:
        print(f"🟡 ledger_seal_weekly KHÔNG chạy (không chốt gì): {e}", flush=True)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
