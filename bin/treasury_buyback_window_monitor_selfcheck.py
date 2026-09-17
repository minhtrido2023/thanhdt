#!/usr/bin/env python3
"""Selfcheck HERMETIC cho `treasury_buyback_window_monitor.py` — dữ liệu giả trong bộ nhớ, KHÔNG
BQ, KHÔNG Discord (runner/notifier bơm vào), ngày chạy cố định (không phụ thuộc hôm nay thật).

    python3 treasury_buyback_window_monitor_selfcheck.py              # chạy các ca
    python3 treasury_buyback_window_monitor_selfcheck.py --all-tz     # + env -u TZ và TZ ngoại
    python3 treasury_buyback_window_monitor_selfcheck.py --mutations  # mỗi nhánh 1 mutation, phải đỏ
    python3 treasury_buyback_window_monitor_selfcheck.py --all        # cả hai
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "treasury_buyback_window_monitor.py")
TODAY = _dt.date(2026, 9, 17)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f" — {detail}"))


def load(path):
    spec = importlib.util.spec_from_file_location("tbw_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ago(n):
    return (TODAY - _dt.timedelta(days=n)).isoformat()


def ev(t, days_ago, title="Báo cáo kết quả giao dịch mua lại cổ phiếu", short=""):
    return {"ticker": t, "d": ago(days_ago), "id": f"{t}-{days_ago}", "title": title,
            "short_content": short}


def ais(t, days_ago, delta, total, title=None):
    if title is None:
        title = f"{t} - {'Giảm' if (delta or 0) < 0 else 'Niêm yết bổ sung'} niêm yết"
    return {"ticker": t, "id": f"A-{t}-{days_ago}", "d": ago(days_ago),
            "shares_delta": None if delta is None else str(delta),
            "shares_total_after": None if total is None else str(total), "title": title}


def make_runner(events, ais_rows, raise_on=None, log=None):
    def runner(sql):
        if log is not None:
            log.append(sql)
        if raise_on and raise_on in sql:
            raise RuntimeError("bq failed: Access Denied: giả lập")
        if "treasury_window:events" in sql:
            return events
        if "treasury_window:ais" in sql:
            return ais_rows
        raise AssertionError(f"SQL lạ: {sql[:80]}")
    return runner


def run_main(c, events, ais_rows, argv=("--dry-run",), notifier=None, raise_on=None):
    sent = []

    def _notifier(msg):
        sent.append(msg)
        return (True, "ok") if notifier is None else notifier(msg)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = c.main(list(argv), runner=make_runner(events, ais_rows, raise_on),
                    notifier=_notifier, today=TODAY)
    return rc, buf.getvalue(), sent


def run_cases(c):
    W, M = c.CLOSE_WINDOW_DAYS, c.MATCH_MAX_DAYS
    print(f"TARGET={os.path.relpath(c.__file__, HERE)} W={W} M={M} TZ={os.environ.get('TZ', '<unset>')}")

    # A. Đóng / mở / biên
    r = c.evaluate(TODAY, [ev("AAA", W + 30)], [ais("AAA", 400, 1000, 10_000),
                                                ais("AAA", W + 10, -500, 9_500)])
    check("A1. step-down Δ<0 sau buy_done ⇒ closed, không WARN",
          len(r["closed"]) == 1 and not r["warn"] and r["closed"][0]["lag"] == 20, r)
    r = c.evaluate(TODAY, [ev("AAA", W + 1)], [ais("AAA", 400, 1000, 10_000)])
    check("A2. chưa step-down, tuổi W+1 ⇒ WARN", len(r["warn"]) == 1, r)
    r = c.evaluate(TODAY, [ev("AAA", W)], [])
    check("A3. biên: tuổi đúng W ⇒ trong cửa sổ, không WARN",
          len(r["open_in_window"]) == 1 and not r["warn"], r)
    r = c.evaluate(TODAY, [ev("AAA", M + 1)], [])
    check("A4. tuổi M+1 chưa đóng ⇒ STALE (không phải WARN)",
          len(r["stale"]) == 1 and not r["warn"], r)
    r = c.evaluate(TODAY, [ev("AAA", M)], [])
    check("A5. biên: tuổi đúng M ⇒ vẫn WARN", len(r["warn"]) == 1 and not r["stale"], r)

    # B. Định nghĩa step-down
    r = c.evaluate(TODAY, [ev("ELC", 250)], [ais("ELC", 300, 4_163_848, 87_453_925),
                                             ais("ELC", 200, 1_000_000, 83_290_077)])
    check("B1. ca ELC thật: tổng giảm nhưng Δ dương ⇒ KHÔNG đóng (WARN)", len(r["warn"]) == 1, r)
    r = c.evaluate(TODAY, [ev("VHM", 200)], [ais("VHM", 900, 1_004_853_570, 4_354_367),
                                             ais("VHM", 160, -246_955_484, 4_107_412_004)])
    check("B2. ca VHM thật: Δ âm nhưng tổng trước sai đơn vị ⇒ VẪN đóng", len(r["closed"]) == 1, r)
    r = c.evaluate(TODAY, [ev("NUL", 100)], [ais("NUL", 60, None, None, "NUL - Giảm niêm yết 5.000 cổ phiếu")])
    check("B3. Δ NULL + tiêu đề 'Giảm niêm yết' ⇒ đóng", len(r["closed"]) == 1, r)
    r = c.evaluate(TODAY, [ev("NUL", 100)], [ais("NUL", 60, None, None, "NUL - Niêm yết bổ sung")])
    check("B4. Δ NULL + tiêu đề bổ sung ⇒ không đóng", len(r["warn"]) == 1, r)
    r = c.evaluate(TODAY, [ev("BEF", 100)], [ais("BEF", 101, -10, 90)])
    check("B5. step-down TRƯỚC ngày buy_done ⇒ không đóng, nhưng hiện ở 'AIS trước'",
          len(r["warn"]) == 1 and r["warn"][0]["ais_before"]["step_down"], r)
    r = c.evaluate(TODAY, [ev("SAM", 100)], [ais("SAM", 100, -10, 90)])
    check("B6. step-down CÙNG ngày buy_done ⇒ đóng (lag 0)",
          len(r["closed"]) == 1 and r["closed"][0]["lag"] == 0, r)
    r = c.evaluate(TODAY, [ev("FAR", M + 50)], [ais("FAR", 49, -10, 90)])
    check("B7. step-down muộn hơn M ngày ⇒ không tính là đóng", not r["closed"] and r["stale"], r)
    r = c.evaluate(TODAY, [ev("EDG", M + 50)], [ais("EDG", 50, -10, 90)])
    check("B8. biên: step-down đúng M ngày sau ⇒ đóng", len(r["closed"]) == 1, r)

    # C. Phạm vi / gộp / cờ nguồn gốc
    r = c.evaluate(TODAY, [{"ticker": "VRE", "d": "2019-12-19", "id": "x", "title": "", "short_content": ""},
                           {"ticker": "OLD", "d": "2020-12-31", "id": "y", "title": "", "short_content": ""},
                           {"ticker": "NEW", "d": "2021-01-01", "id": "z", "title": "", "short_content": ""}], [])
    check("C1. pre-2021 bị loại kể cả khi SQL trả về; 2021-01-01 giữ",
          r["scope_events"] == 1 and r["stale"][0]["ticker"] == "NEW", r)
    r = c.evaluate(TODAY, [ev("DUP", 80), ev("DUP", 80, "Tin khác"), ev("DUP", 81)], [])
    check("C2. gộp theo (ticker, public_date): 3 dòng ⇒ 2 sự kiện, n_news=2",
          r["scope_events"] == 2 and sorted(i["n_news"] for i in r["warn"]) == [1, 2], r)
    r = c.evaluate(TODAY, [ev("ESO", 80, "Báo cáo kết quả mua lại cổ phiếu ESOP đợt 2"),
                           ev("LAO", 80, "BC mua lại", "cổ phiếu của Người lao động nghỉ việc"),
                           ev("PLN", 80)], [])
    hints = {i["ticker"]: i["hint"] for i in r["warn"]}
    check("C3. cờ ESOP (tiêu đề + short_content, không phân biệt hoa thường) nhưng KHÔNG loại trừ",
          len(r["warn"]) == 3 and hints["ESO"] and hints["LAO"] and hints["PLN"] is None, hints)
    check("C4. SQL events: đúng buy_done + sàn 2021-01-01 + trần hôm nay",
          all(s in c.sql_events(TODAY) for s in ("action_type = 'buy_done'", "DATE '2021-01-01'",
                                                  f"DATE '{TODAY}'")), c.sql_events(TODAY))
    q = c.sql_ais(TODAY)
    check("C5. SQL AIS: executed + AIS + không lấy dòng tương lai",
          all(s in q for s in ("event_code = 'AIS'", "event_status = 'executed'", f"<= DATE '{TODAY}'")), q)

    # D. Nội dung WARN (§29: sự kiện + số liệu, không kết luận)
    rc, out, sent = run_main(c, [ev("KDC", 73)], [ais("KDC", 650, 10_064_960, 289_806_316)],
                             argv=())
    msg = sent[0] if sent else ""
    check("D1. WARN ⇒ rc=1 + post 1 lần", rc == 1 and len(sent) == 1, (rc, sent))
    check("D2. WARN nêu ticker, ngày, số ngày, ngưỡng, AIS trước",
          all(s in msg for s in ("KDC", ago(73), "73 ngày", f"ngưỡng {W}", "289,806,316")), msg)
    check("D3. không kết luận 'vi phạm'", not re.search(r"vi phạm|violat", msg, re.I), msg)
    rc, out, sent = run_main(c, [ev("OK", 80)], [ais("OK", 60, -5, 5)], argv=())
    check("D4. không WARN ⇒ rc=0, không post", rc == 0 and not sent, (rc, sent, out))
    rc, out, sent = run_main(c, [ev("OLD", M + 10)], [], argv=())
    check("D5. chỉ STALE ⇒ rc=0, không post, nhưng có trong log",
          rc == 0 and not sent and "STALE OLD" in out, (rc, sent, out))
    rc, out, sent = run_main(c, [ev("KDC", 73)], [], argv=("--dry-run",))
    check("D6. --dry-run ⇒ không post, rc=1", rc == 1 and not sent, (rc, sent))

    # E. Lỗi
    rc, out, sent = run_main(c, [], [], argv=(), raise_on="treasury_window:ais")
    check("E1. BQ lỗi ⇒ rc=2, post kèm lỗi THẬT", rc == 2 and sent and "Access Denied" in sent[0],
          (rc, sent))
    rc, out, sent = run_main(c, [ev("KDC", 73)], [], argv=(), notifier=lambda m: (False, "rc=7"))
    check("E2. post thất bại ⇒ rc=3 + NOTIFY_FAILED", rc == 3 and "NOTIFY_FAILED" in out, (rc, out))

    with open(c.__file__, encoding="utf-8") as fh:
        body = fh.read()
    import ast
    tree = ast.parse(body)
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names} | {
        n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    code = "\n".join(ln for ln in body.split('"""', 2)[2].splitlines()
                     if not ln.lstrip().startswith("#"))  # bỏ docstring module + comment
    writes = re.findall(r"open\([^)]*[\"'][wax+]", code)
    forbidden = sorted(imported & {"oshares_live", "corp_action_daily", "pandas_gbq"}) + [
        w for w in ("to_gbq", "INSERT ", "UPDATE ", "DELETE ", "MERGE ", "os.replace") if w in code]
    check("E3. WARN-ONLY tĩnh: không ghi file/BQ, không import oshares_live/corp_action_daily",
          not writes and not forbidden and "corp_action_lib" in imported, (writes, forbidden))

    # F. TZ: 2026-09-17 17:30 UTC = 2026-09-18 00:30 ICT. now() trần theo TZ tiến trình ⇒ sai ngày.
    instant = _dt.datetime(2026, 9, 17, 17, 30, tzinfo=_dt.timezone.utc)

    class FakeDT(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz else instant.astimezone().replace(tzinfo=None)

    orig = c.dt
    c.dt = types.SimpleNamespace(date=_dt.date, timedelta=_dt.timedelta, datetime=FakeDT)
    log = []
    try:
        with redirect_stdout(io.StringIO()):
            c.main(["--dry-run"], runner=make_runner([], [], log=log), notifier=lambda m: (True, ""))
    finally:
        c.dt = orig
    q = next((s for s in log if "treasury_window:events" in s), "")
    check(f"F1. TZ={os.environ.get('TZ', '<unset>')}: 00:30 ICT 18/09 ⇒ hôm nay = 2026-09-18",
          "DATE '2026-09-18'" in q, q[-120:])

    fails = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} PASS" + (f" — FAIL: {fails}" if fails else ""))
    return 0 if not fails else 1


# ── mutation ──────────────────────────────────────────────────────────────────────────────
MUTATIONS = (
    ("close-no-stepdown", 'close = next((a for a in seq if a["step_down"]',
     'close = next((a for a in seq if True'),
    ("close-before-date", "and 0 <= (a[\"d\"] - d).days <= MATCH_MAX_DAYS)",
     "and (a[\"d\"] - d).days <= MATCH_MAX_DAYS)"),
    ("close-unbounded", "and 0 <= (a[\"d\"] - d).days <= MATCH_MAX_DAYS)",
     "and 0 <= (a[\"d\"] - d).days)"),
    ("stepdown-by-total", 'a["step_down"] = (a["delta"] < 0 if a["delta"] is not None',
     'a["step_down"] = (a["total"] < 10**9 if a["delta"] is not None'),
    ("stepdown-null-title", 'else "giảm niêm yết" in a["title"].lower())', "else False)"),
    ("warn-boundary", "        elif elapsed > CLOSE_WINDOW_DAYS:", "        elif elapsed >= CLOSE_WINDOW_DAYS:"),
    ("stale-off", "        elif elapsed > MATCH_MAX_DAYS:", "        elif False:"),
    ("scope-filter", "        if key[1] < SCOPE_START:", "        if False:"),
    ("dedup-off", "key = (r[\"ticker\"], dt.date.fromisoformat(r[\"d\"]))",
     "key = (r[\"ticker\"], dt.date.fromisoformat(r[\"d\"]), r[\"id\"])"),
    ("hint-title-only", "m = ORIGIN_HINT_RE.search(f\"{r.get('title') or ''} {r.get('short_content') or ''}\")",
     "m = ORIGIN_HINT_RE.search(f\"{r.get('title') or ''}\")"),
    ("hint-excludes", "            res[\"warn\"].append(item)",
     "            (None if item[\"hint\"] else res[\"warn\"].append(item))"),
    ("warn-no-before", "AIS trước: {_fmt_ais(item['ais_before'])}", "AIS trước: ?"),
    ("post-on-clean", "        if not res[\"warn\"]:\n            return 0", "        if False:\n            return 0"),
    ("error-no-post", "        rc = 2\n", "        return 2\n"),
    ("notify-fail-ignored", "    if not ok:\n        print(f\"NOTIFY_FAILED", "    if False:\n        print(f\"NOTIFY_FAILED"),
    ("tz-naive-now", "else dt.datetime.now(ICT).date())", "else dt.datetime.now().date())"),
    ("write-state", "    ok, detail = notifier(msg)\n", "    open('/tmp/x', 'w')\n    ok, detail = notifier(msg)\n"),
    ("sql-status", "WHERE event_code = 'AIS' AND event_status = 'executed' ", "WHERE event_code = 'AIS' "),
)


def run_mutations():
    with open(TARGET, encoding="utf-8") as fh:
        orig = fh.read()
    root = HERE
    while root != "/" and not os.path.isfile(os.path.join(root, "wc_env.sh")):
        root = os.path.dirname(root)
    env = dict(os.environ, TZ="UTC", WC_ROOT=root)
    killed, survived = [], []

    def run_copy(text):
        d = tempfile.mkdtemp(prefix="tbw_mut_")
        try:
            shutil.copy(os.path.join(HERE, "wc_paths.py"), d)
            p = os.path.join(d, "treasury_buyback_window_monitor.py")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            r = subprocess.run([sys.executable, __file__, "--target", p], env=env,
                               capture_output=True, text=True, timeout=120)
            return r.returncode, r.stdout + ("" if r.returncode == 0 or "FAIL  " in r.stdout
                                             else "\nCRASH " + (r.stderr.strip().splitlines()
                                                                 or ["?"])[-1])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    rc, out = run_copy(orig)
    print(f"  control (bản gốc chép ra /tmp, TZ=UTC): rc={rc} {out.strip().splitlines()[-1]}")
    if rc != 0:
        print(out)
        return 1
    for name, old, new in MUTATIONS:
        n = orig.count(old)
        if n != 1:
            print(f"  BAD   {name}: chuỗi mutation xuất hiện {n} lần (phải đúng 1)")
            survived.append(name)
            continue
        rc, out = run_copy(orig.replace(old, new))
        fails = [ln.strip()[:110] for ln in out.splitlines()
                 if ln.strip().startswith(("FAIL", "CRASH"))]
        (killed if rc != 0 else survived).append(name)
        print(f"  {'KILLED' if rc else 'SURVIVED'}  {name}: {fails[:3]}")
    print(f"\nmutation: {len(killed)}/{len(MUTATIONS)} bị giết" +
          (f" — SỐNG SÓT: {survived}" if survived else ""))
    return 0 if not survived else 1


def run_all_tz():
    rcs = []
    for label, env in (("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                       ("TZ=America/New_York", dict(os.environ, TZ="America/New_York")),
                       ("TZ=Pacific/Kiritimati", dict(os.environ, TZ="Pacific/Kiritimati")),
                       ("TZ=Asia/Ho_Chi_Minh", dict(os.environ, TZ="Asia/Ho_Chi_Minh"))):
        r = subprocess.run([sys.executable, __file__], env=env, capture_output=True, text=True,
                           timeout=120)
        print(f"  {label:24s} rc={r.returncode} {r.stdout.strip().splitlines()[-1]}")
        rcs.append(r.returncode)
    return 0 if not any(rcs) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=TARGET)
    ap.add_argument("--all-tz", action="store_true")
    ap.add_argument("--mutations", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.all_tz or a.mutations or a.all:
        rc = 0
        if a.all_tz or a.all:
            print("== ma trận TZ ==")
            rc |= run_all_tz()
        if a.mutations or a.all:
            print("== mutation ==")
            rc |= run_mutations()
        return rc
    return run_cases(load(a.target))


if __name__ == "__main__":
    sys.exit(main())
