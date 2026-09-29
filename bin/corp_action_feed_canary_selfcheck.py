#!/usr/bin/env python3
"""Selfcheck HERMETIC cho `corp_action_feed_canary.py` — dữ liệu giả trong bộ nhớ, KHÔNG BQ,
KHÔNG Discord (runner/notifier đều bơm vào).

Mỗi nhánh WARN có ca đỏ + ca xanh. Hai ca đọc CODE THẬT (không phải BQ) làm drift-guard: bộ trích
cột/giá trị từ `corp_action_lib.py` / `oshares_live.py` / `corp_action_daily.py` phải khớp pin.

    python3 corp_action_feed_canary_selfcheck.py              # chạy các ca
    python3 corp_action_feed_canary_selfcheck.py --all-tz     # + chạy lại dưới env -u TZ và TZ ngoại
    python3 corp_action_feed_canary_selfcheck.py --mutations  # mỗi nhánh 1 mutation, phải đỏ
    python3 corp_action_feed_canary_selfcheck.py --all        # cả hai
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
TARGET = os.path.join(HERE, "corp_action_feed_canary.py")

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + ("" if cond else f" — {detail}"))


def load(path):
    spec = importlib.util.spec_from_file_location("canary_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── dữ liệu giả ───────────────────────────────────────────────────────────────────────────
def schema_rows(c, drop=(), retype=None):
    rows = [{"column_name": k, "data_type": v} for k, v in c.EXPECTED_TYPES.items() if k not in drop]
    rows += [{"column_name": "category", "data_type": "STRING"}]
    for r in rows:
        if retype and r["column_name"] in retype:
            r["data_type"] = retype[r["column_name"]]
    return rows


def value_rows(overrides=None, drop=()):
    base = {("code", "DIV"): (17175, 160), ("code", "ISS"): (11745, 126),
            ("code", "AIS"): (4928, 58), ("code", "NLIS"): (1371, 4), ("code", "SUSP"): (685, 7),
            ("code", "MOVE"): (431, 0), ("code", "MA"): (17, 0),
            ("status", "executed"): (33000, 300), ("status", "announced"): (820, 60),
            ("status", "not_executed"): (1785, 0)}
    base.update(overrides or {})
    return [{"kind": k, "v": v, "n_all": str(a), "n_recent": str(r)}
            for (k, v), (a, r) in base.items() if (k, v) not in drop]


def pin_rows(c, change=None, drop=(), dup=()):
    rows = []
    for t, d, v in c.AIS_PINS:
        if t in drop:
            continue
        rows.append({"ticker": t, "eff": d, "shares_total_after": str((change or {}).get(t, v))})
        if t in dup:
            rows.append({"ticker": t, "eff": d, "shares_total_after": str(v)})
    return rows


def make_runner(c, schema=None, values=None, activity=None, pins=None, raise_on=None, log=None):
    def runner(sql):
        if log is not None:
            log.append(sql)
        tag = sql.split("*/", 1)[0]
        for key in ("schema", "values", "activity", "pins"):
            if f"canary:{key}" in tag:
                if raise_on and key in raise_on:
                    raise RuntimeError(raise_on[key])
                return {"schema": schema if schema is not None else schema_rows(c),
                        "values": values if values is not None else value_rows(),
                        "activity": activity if activity is not None else [{"iss": "16", "ais": "32"}],
                        "pins": pins if pins is not None else pin_rows(c)}[key]
        raise AssertionError(f"SQL không có tag canary: {sql[:60]}")
    return runner


def fake_source(tmp, sql_body, name="fake_src.py", func="q"):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(f'TABLE = "x"\n\ndef {func}(tk):\n    """doc: SELECT not_a_column FROM y"""\n'
                 f'    return f"""{sql_body} """\n')
    return ((p, func),)


def status_of(results, name):
    return next(r for r in results if r["check"] == name)


def run_cases(c):
    tmp = tempfile.mkdtemp(prefix="canary_sc_")
    today = _dt.date(2026, 9, 15)
    try:
        good_src = fake_source(tmp, "SELECT ticker, event_code, CAST(exright_date AS STRING) "
                                    "exright_date FROM `{TABLE}` WHERE ticker IN ({tk}) AND "
                                    'event_status = "executed" AND event_code IN ("ISS", "AIS")')

        print("== (a) schema ==")
        cols = c.code_columns(good_src)
        check("A0. trích cột từ nguồn giả = {ticker,event_code,exright_date,event_status}, bỏ "
              "docstring/placeholder/alias", set(cols) == {"ticker", "event_code", "exright_date",
                                                           "event_status"}, sorted(cols))
        r = c.check_schema(schema_rows(c), cols)
        check("A1. xanh: đủ cột đúng kiểu ⇒ PASS", r["status"] == "PASS", r)
        r = c.check_schema(schema_rows(c, drop=("exright_date",)), cols)
        check("A2. đỏ: mất cột exright_date ⇒ WARN nêu tên cột",
              r["status"] == "WARN" and "`exright_date` THIẾU" in r["evidence"], r)
        r = c.check_schema(schema_rows(c, retype={"exright_date": "STRING"}), cols)
        check("A3. đỏ: DATE→STRING ⇒ WARN nêu cả 2 kiểu",
              r["status"] == "WARN" and "STRING ≠ pin DATE" in r["evidence"], r)
        extra = fake_source(tmp, "SELECT ticker, brand_new_col FROM `{TABLE}`", name="x2.py")
        r = c.check_schema(schema_rows(c) + [{"column_name": "brand_new_col",
                                              "data_type": "INT64"}], c.code_columns(extra))
        check("A4. đỏ: code đọc cột chưa pin kiểu ⇒ WARN 'chưa pin', kèm kiểu live",
              r["status"] == "WARN" and "chưa pin" in r["evidence"] and "INT64" in r["evidence"], r)
        r = c.check_schema(schema_rows(c), {})
        check("A5. đỏ: trích 0 cột ⇒ WARN (bộ trích hỏng không được thành PASS)",
              r["status"] == "WARN" and "0 cột" in r["evidence"], r)
        real = c.code_columns()
        check("A6. CODE THẬT: cột trích từ 6 hàm SQL production == EXPECTED_TYPES (drift-guard)",
              set(real) == set(c.EXPECTED_TYPES),
              f"thừa={sorted(set(real) - set(c.EXPECTED_TYPES))} "
              f"thiếu={sorted(set(c.EXPECTED_TYPES) - set(real))}")

        print("== (b) values ==")
        need_c = {v: "pin" for v in c.REQUIRED_CODES}
        need_s = {v: "pin" for v in c.REQUIRED_STATUSES}
        r = c.check_values(value_rows(), need_c, need_s)
        check("B1. xanh: tập giá trị bình thường ⇒ PASS", r["status"] == "PASS", r)
        r = c.check_values(value_rows({("status", "done"): (500, 20)}), need_c, need_s)
        check("B2. đỏ: status MỚI `done` ⇒ WARN liệt kê", r["status"] == "WARN"
              and "MỚI status=`done`" in r["evidence"], r)
        r = c.check_values(value_rows({("status", "Executed"): (33000, 300)},
                                      drop=(("status", "executed"),)), need_c, need_s)
        check("B3. đỏ: `executed` đổi tên `Executed` ⇒ WARN cả MỚI lẫn BIẾN MẤT",
              r["status"] == "WARN" and "`Executed`" in r["evidence"]
              and "status=`executed` code cần" in r["evidence"], r)
        r = c.check_values(value_rows({("code", "AIS"): (4928, 0)}), need_c, need_s)
        check("B4. đỏ: AIS còn trong bảng nhưng 0 dòng 45 ngày ⇒ WARN cửa sổ",
              r["status"] == "WARN" and "code=`AIS` 0 dòng trong 45" in r["evidence"], r)
        r = c.check_values(value_rows({("status", "not_executed"): (1785, 0),
                                       ("status", "announced"): (820, 0)}), need_c, need_s)
        check("B5. xanh: not_executed/announced 0 dòng gần đây (thường gặp) ⇒ vẫn PASS",
              r["status"] == "PASS", r)
        r = c.check_values(value_rows(drop=(("code", "NLIS"),)), need_c, need_s)
        check("B5b. xanh: mã code KHÔNG cần (NLIS) biến mất ⇒ không WARN", r["status"] == "PASS", r)
        codes, sts = c.code_values(good_src, ())
        check("B6. trích giá trị từ SQL giả: codes ⊇ {ISS,AIS}, status ⊇ {executed}",
              {"ISS", "AIS"} <= set(codes) and "executed" in sts, (codes, sts))
        v2 = fake_source(tmp, 'SELECT ticker FROM `{TABLE}` WHERE event_status = "executed_v2"',
                         name="x3.py")
        res = c.run_checks(today, make_runner(c), v2, ())
        rb = status_of(res, "b.values")
        check("B7. đỏ: code mới lọc `executed_v2` mà bảng không có ⇒ WARN (giá trị trích từ code)",
              rb["status"] == "WARN" and "`executed_v2`" in rb["evidence"], rb)
        rc_, rs_ = c.code_values()
        check("B8. CODE THẬT: trích được ISS/AIS/DIV + executed/not_executed",
              {"ISS", "AIS", "DIV"} <= set(rc_) and {"executed", "not_executed"} <= set(rs_),
              (rc_, rs_))

        print("== (c) activity + lịch VN ==")
        r = c.check_activity([{"iss": "0", "ais": "1"}], "2026-09-01", "2026-09-14")
        check("C1. xanh: 1 dòng AIS ⇒ PASS", r["status"] == "PASS", r)
        r = c.check_activity([{"iss": "0", "ais": "0"}], "2026-08-27", "2026-09-14")
        check("C2. đỏ: 0 dòng ⇒ WARN kèm cửa sổ", r["status"] == "WARN"
              and "2026-08-27→2026-09-14" in r["evidence"], r)
        s = c.prior_sessions(_dt.date(2026, 9, 3), 3)
        check("C3. lịch: 3 phiên trước T5 03/09/2026 bỏ QK 31/08-02/09 + cuối tuần = 28,27,26/08",
              s == [_dt.date(2026, 8, 28), _dt.date(2026, 8, 27), _dt.date(2026, 8, 26)], s)
        log = []
        c.run_checks(today, make_runner(c, log=log))
        act = next(q for q in log if "canary:activity" in q)
        check("C4. SQL activity 15/09 dùng đúng cửa sổ 10 phiên 2026-08-27→2026-09-14",
              "DATE '2026-08-27'" in act and "DATE '2026-09-14'" in act, act)
        check("C5. SQL activity lọc executed + ISS exright/AIS effective",
              "event_status = 'executed'" in act and "exright_date BETWEEN" in act
              and "effective_date BETWEEN" in act, act)

        print("== (d) AIS pins ==")
        r = c.check_pins(pin_rows(c))
        check("D1. xanh: 5/5 khớp ⇒ PASS", r["status"] == "PASS" and "5/5" in r["evidence"], r)
        r = c.check_pins(pin_rows(c, change={"FPT": 1_703_507_122}))
        check("D2. đỏ: FPT +1 cp ⇒ WARN nêu 2 số", r["status"] == "WARN"
              and "1,703,507,122 ≠ pin 1,703,507,121" in r["evidence"], r)
        r = c.check_pins(pin_rows(c, drop=("ACV",)))
        check("D3. đỏ: ACV biến mất ⇒ WARN 0 dòng", r["status"] == "WARN"
              and "ACV AIS 2025-09-29: 0 dòng" in r["evidence"], r)
        r = c.check_pins(pin_rows(c, dup=("SHS",)))
        check("D4. đỏ: SHS nhân đôi ⇒ WARN 2 dòng", r["status"] == "WARN"
              and "SHS AIS 2025-06-13: 2 dòng" in r["evidence"], r)

        print("== (e) main: warn-only, notify, lỗi canary, TZ ==")
        sent = []

        def notifier(msg):
            sent.append(msg)
            return True, "rc=0"

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = c.main([], runner=make_runner(c), notifier=notifier, today=today)
        out = buf.getvalue().strip().splitlines()
        check("E1. toàn PASS ⇒ rc=0, KHÔNG post, đúng 1 dòng log", rc == 0 and not sent
              and len(out) == 1 and "PASS 4/4" in out[0], (rc, sent, out))
        err = ("bq failed: ERROR: (bq) There was a problem refreshing your current auth tokens: "
               "Reauthentication failed")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = c.main([], runner=make_runner(c, raise_on={"schema": err, "values": err,
                                                            "activity": err, "pins": err}),
                        notifier=notifier, today=today)
        check("E2. đỏ: BQ auth hỏng ⇒ rc=2, post 1 lần, trích NGUYÊN stderr thật",
              rc == 2 and len(sent) == 1 and "Reauthentication failed" in sent[0]
              and "CANARY KHÔNG CHẠY ĐƯỢC" in sent[0], (rc, sent))
        sent.clear()
        with redirect_stdout(io.StringIO()):
            rc = c.main([], runner=make_runner(c, activity=[{"iss": "0", "ais": "0"}]),
                        notifier=notifier, today=today)
        check("E3. đỏ: 1 WARN ⇒ rc=1, post 1 lần có mục c.activity",
              rc == 1 and len(sent) == 1 and "c.activity WARN" in sent[0], (rc, sent))
        sent.clear()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = c.main([], runner=make_runner(c, activity=[{"iss": "0", "ais": "0"}]),
                        notifier=lambda m: (False, "rc=1 stderr=boom"), today=today)
        check("E4. đỏ: post thất bại ⇒ rc=3 + dòng NOTIFY_FAILED có stderr",
              rc == 3 and "NOTIFY_FAILED" in buf.getvalue() and "boom" in buf.getvalue(),
              (rc, buf.getvalue()[-200:]))
        with redirect_stdout(io.StringIO()):
            rc = c.main(["--dry-run"], runner=make_runner(c, activity=[{"iss": "0", "ais": "0"}]),
                        notifier=notifier, today=today)
        check("E5. --dry-run ⇒ rc=1 nhưng KHÔNG post", rc == 1 and not sent, (rc, sent))

        calls = []
        orig_run = c.subprocess.run
        c.subprocess.run = lambda cmd, **kw: (calls.append(cmd),
                                              types.SimpleNamespace(returncode=0, stderr=""))[1]
        try:
            ok, _ = c.default_notifier("hi")
        finally:
            c.subprocess.run = orig_run
        check("E6. notifier mặc định gọi notify_thread.sh với TÊN topic `architecture` (không ID)",
              ok and calls and calls[0][0].endswith("notify_thread.sh")
              and calls[0][2] == "architecture", calls)

        with open(c.__file__, encoding="utf-8") as fh:
            src = fh.read()
        code_only = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        body = code_only.split('"""', 2)[2]
        forbidden = [w for w in ("corp_action_daily_state", "_FAILED.json", "data/corp_action_daily",
                                 "import corp_action_daily", "from corp_action_daily",
                                 "os.replace", "json.dump", ".write(")
                     if w in body]
        writes = re.findall(r"open\([^)]*[\"'][wax+]", body)
        check("E7. WARN-ONLY tĩnh: không import/ghi state/publish/_FAILED của corp_action_daily, "
              "không open() ghi file nào", not forbidden and not writes, (forbidden, writes))

        # TZ: đồng hồ giả = 2026-09-14 23:30 UTC = 2026-09-15 06:30 ICT. now() trần theo TZ tiến trình.
        instant = _dt.datetime(2026, 9, 14, 23, 30, tzinfo=_dt.timezone.utc)

        class FakeDT(_dt.datetime):
            @classmethod
            def now(cls, tz=None):
                return instant.astimezone(tz) if tz else instant.astimezone().replace(tzinfo=None)

        fake_dt = types.SimpleNamespace(date=_dt.date, timedelta=_dt.timedelta, datetime=FakeDT)
        orig_dt = c.dt
        c.dt = fake_dt
        log = []
        try:
            with redirect_stdout(io.StringIO()):
                c.main(["--dry-run"], runner=make_runner(c, log=log), notifier=notifier)
        finally:
            c.dt = orig_dt
        vals = next(q for q in log if "canary:values" in q)
        check(f"E8. TZ={os.environ.get('TZ', '<unset>')}: 06:30 ICT 15/09 ⇒ hôm nay = 2026-09-15 "
              "(cửa sổ public_date từ 2026-08-01)", "DATE '2026-08-01'" in vals, vals[:220])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fails = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} PASS" + (f" — FAIL: {fails}" if fails else ""))
    return 0 if not fails else 1


# ── mutation ──────────────────────────────────────────────────────────────────────────────
MUTATIONS = (
    ("schema-missing", "        if col not in live:\n", "        if False:\n"),
    ("schema-type", "        elif live[col] != EXPECTED_TYPES[col]:", "        elif False:"),
    ("schema-unpinned", "        elif col not in EXPECTED_TYPES:",
     "        elif False and col not in EXPECTED_TYPES:"),
    ("schema-empty-extract", "    if not code_cols:", "    if False:"),
    ("values-new", "        if v not in known:", "        if False:"),
    ("values-missing-all", "            if n_all == 0:", "            if False:"),
    ("values-recent", "            elif (kind, v) in RECENT_REQUIRED and n_recent == 0:",
     "            elif False:"),
    ("values-from-code", "        need_s.update({v: s for v, s in statuses.items() if v not in need_s})",
     "        pass"),
    ("activity-zero", 'return _res("c.activity", iss + ais > 0, ev)',
     'return _res("c.activity", True, ev)'),
    ("calendar-holiday", "if d.weekday() < 5 and not is_holiday(d):", "if d.weekday() < 5:"),
    ("pins-value", "        elif int(vals[0]) != want:", "        elif False:"),
    ("pins-count", "        if len(vals) != 1:", "        if not vals:"),
    ("error-swallowed", 'if all(r["status"] == "PASS" for r in results):',
     'if all(r["status"] in ("PASS", "ERROR") for r in results):'),
    ("notify-on-pass", "        return 0\n    msg = render(today, results)",
     "    msg = render(today, results)"),
    ("notify-fail-ignored", "    if not ok:\n        print(f\"NOTIFY_FAILED", "    if False:\n        print(f\"NOTIFY_FAILED"),
    ("tz-naive-now", "else dt.datetime.now(ICT).date())", "else dt.datetime.now().date())"),
)


def run_mutations():
    with open(TARGET, encoding="utf-8") as fh:
        orig = fh.read()
    env = dict(os.environ, TZ="UTC", WC_ROOT=os.path.abspath(os.path.join(HERE, "..", "..")))
    # WC_ROOT: find_wc_root kiểm chứng marker wc_env.sh; bản sao ở /tmp không tự đi lên được.
    root = env["WC_ROOT"]
    while root != "/" and not os.path.isfile(os.path.join(root, "wc_env.sh")):
        root = os.path.dirname(root)
    env["WC_ROOT"] = root
    killed, survived = [], []

    def run_copy(text):
        d = tempfile.mkdtemp(prefix="canary_mut_")
        try:
            for f in ("wc_paths.py", "corp_action_daily.py", "notify_thread.sh"):
                shutil.copy(os.path.join(HERE, f), d)
            p = os.path.join(d, "corp_action_feed_canary.py")
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
        fails = [l.strip()[:110] for l in out.splitlines()
                 if l.strip().startswith(("FAIL", "CRASH"))]
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
