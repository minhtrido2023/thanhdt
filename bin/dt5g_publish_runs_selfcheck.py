#!/usr/bin/env python3
"""Selfcheck sổ chạy publisher DT5G (`data/dt5g_publish_runs.log`) — job Taylor_20261025_043744.

Phủ 2 đầu, KHÔNG chạm BQ/Discord/bus thật:
  P. deploy_golive_dt5g_v4/publish_gated_state.py chạy THẬT trong sandbox (bản sao, WORKDIR trỏ
     sandbox, `macro_state_live` + `state_publish_immutable` là STUB): publish OK / publish raise /
     get_gated_state raise / thư mục log không ghi được ⇒ START+END đúng, publish không bao giờ
     hỏng vì log. Cộng publish_run_log.log_run: fail-open + 2 tiến trình append song song.
  W. mike/bin/dt5g_writer_watch.py main() với table_lastmod/bq_query_csv/notify/bus bị thay:
     có log khớp ±vài phút ⇒ OURS_MANUAL QUIET 0 ping · không log ⇒ OTHER WARN · lệch 20' ⇒ OTHER ·
     thiếu END ⇒ START+30' · dòng log hỏng bị bỏ qua · trong cửa sổ cron vẫn OURS.
Chạy dưới env -u TZ + 2 TZ lạ (§16). Usage: python3 bin/dt5g_publish_runs_selfcheck.py
Env: DT5G_PUBLISHER_DIR = thư mục chứa publish_gated_state.py (mặc định <WC>/deploy_golive_dt5g_v4).
"""
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
FAILS = []


def ck(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(name)


def _wc_root():
    sys.path.insert(0, HERE)
    import wc_paths
    return wc_paths.find_wc_root(__file__)


def pub_dir():
    return os.environ.get("DT5G_PUBLISHER_DIR") or os.path.join(_wc_root(), "deploy_golive_dt5g_v4")


STUB_MSL = '''import os, pandas as pd
def get_gated_state(start, end):
    if os.environ.get("STUB_GATED_RAISE"):
        raise RuntimeError("stub get_gated_state hỏng")
    return pd.DataFrame({"time": ["2026-10-22", "2026-10-23"], "state": [2, 2], "base_state": [2, 2],
                         "macro_state": [2, 2], "source": ["DT5G", "DT5G"]})
'''
STUB_SPI = '''import os
class PublishAbort(Exception):
    pass
def publish_immutable(out, table, label):
    if os.environ.get("STUB_PUBLISH_RAISE"):
        raise PublishAbort("stub abort")
    return {"n_sealed_rows": 0, "n_tail_rows": len(out)}
def export_published_csv(table, path):
    open(path, "w").write("time,state,state_raw\\n")
    return 0
'''


def run_publisher(sb, **env_extra):
    env = {k: v for k, v in os.environ.items() if k not in ("STUB_GATED_RAISE", "STUB_PUBLISH_RAISE")}
    env.update(env_extra, PYTHONPATH=sb)
    return subprocess.run([sys.executable, os.path.join(sb, "deploy_golive_dt5g_v4", "publish_gated_state.py")],
                          capture_output=True, text=True, env=env, timeout=120, cwd=sb)


def read_log(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")] if os.path.exists(p) else []


def part_publisher():
    print("=== P. publisher ghi sổ chạy (sandbox, stub BQ) ===")
    src = os.path.join(pub_dir(), "publish_gated_state.py")
    real = 'WORKDIR = r"/home/trido/thanhdt/WorkingClaude"'
    code = open(src, encoding="utf-8").read()
    ck("publisher có đúng 1 dòng WORKDIR hardcode để sandbox thay", code.count(real) == 1)
    sb = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(sb, "deploy_golive_dt5g_v4"))
        os.makedirs(os.path.join(sb, "data"))
        open(os.path.join(sb, "deploy_golive_dt5g_v4", "publish_gated_state.py"), "w", encoding="utf-8") \
            .write(code.replace(real, f'WORKDIR = r"{sb}"'))
        shutil.copy(os.path.join(pub_dir(), "publish_run_log.py"), os.path.join(sb, "deploy_golive_dt5g_v4"))
        open(os.path.join(sb, "macro_state_live.py"), "w").write(STUB_MSL)
        open(os.path.join(sb, "state_publish_immutable.py"), "w").write(STUB_SPI)
        log = os.path.join(sb, "data", "dt5g_publish_runs.log")

        r = run_publisher(sb)
        L = read_log(log)
        ck("publish OK ⇒ rc 0", r.returncode == 0, r.stdout[-300:] + r.stderr[-300:])
        ck("publish OK ⇒ đúng 2 dòng START, END cùng run_id", [x["event"] for x in L] == ["START", "END"]
           and L[0]["run_id"] == L[1]["run_id"], L)
        ck("END ghi publish_ok=true", L and L[-1].get("publish_ok") is True, L)
        st = L[0] if L else {}
        ts = dt.datetime.fromisoformat(st.get("ts", "1970-01-01"))
        ck("ts có offset +07:00 (neo ICT, kể cả khi TZ host khác)", ts.utcoffset() == dt.timedelta(hours=7), st.get("ts"))
        ck("ghi ppid/parent/argv", st.get("ppid") and st.get("parent") and isinstance(st.get("argv"), list), st)
        ck("state JSON vẫn được ghi", os.path.exists(os.path.join(sb, "deploy_golive_dt5g_v4", "golive_state_today.json")))

        os.remove(log)
        r = run_publisher(sb, STUB_PUBLISH_RAISE="1")
        L = read_log(log)
        ck("publish ABORT ⇒ rc 1 (như cũ)", r.returncode == 1, r.stdout[-300:])
        ck("publish ABORT ⇒ END vẫn ghi, publish_ok=false", [x["event"] for x in L] == ["START", "END"]
           and L[-1].get("publish_ok") is False, L)

        os.remove(log)
        r = run_publisher(sb, STUB_GATED_RAISE="1")
        L = read_log(log)
        ck("get_gated_state raise ⇒ rc≠0", r.returncode != 0)
        ck("exception ⇒ END vẫn ghi (atexit), publish_ok=null", [x["event"] for x in L] == ["START", "END"]
           and L[-1].get("publish_ok") is None, L)

        os.remove(log)
        shutil.rmtree(os.path.join(sb, "data"))
        open(os.path.join(sb, "data"), "w").write("data là FILE ⇒ không tạo được log")
        r = run_publisher(sb)
        ck("log KHÔNG ghi được ⇒ publish vẫn rc 0 (fail-open)", r.returncode == 0, r.stderr[-400:])
        ck("log KHÔNG ghi được ⇒ stderr nêu lỗi thật", "publish_run_log" in r.stderr and "dt5g_publish_runs.log" in r.stderr,
           r.stderr[-400:])
        os.remove(os.path.join(sb, "data"))
        os.makedirs(os.path.join(sb, "data"))
        os.remove(os.path.join(sb, "deploy_golive_dt5g_v4", "publish_run_log.py"))
        r = run_publisher(sb)
        ck("thiếu module publish_run_log ⇒ publish vẫn rc 0 + WARN stderr", r.returncode == 0
           and "dt5g_publish_runs.log tắt" in r.stderr, r.stderr[-300:])

        # 2 tiến trình append song song: không dòng nào bị xen/hỏng
        sys.path.insert(0, pub_dir())
        import publish_run_log as prl
        cl = os.path.join(sb, "conc.log")
        prog = ("import sys; sys.path.insert(0, %r); import publish_run_log as p\n"
                "for i in range(300): p.log_run(%r, 'START', sys.argv[1] + str(i), pad='x' * 900)") % (pub_dir(), cl)
        ps = [subprocess.Popen([sys.executable, "-c", prog, n]) for n in ("a", "b", "c")]
        for p in ps:
            p.wait()
        lines = open(cl, encoding="utf-8").read().splitlines()
        ok = sum(1 for x in lines if json.loads(x).get("pad") == "x" * 900)
        ck("3×300 append song song ⇒ 900 dòng JSON nguyên vẹn", len(lines) == 900 and ok == 900, (len(lines), ok))
        ck("log_run đường không ghi được ⇒ False, không raise",
           prl.log_run("/proc/khong_ghi_duoc/x.log", "START", "z") is False)
    finally:
        shutil.rmtree(sb, ignore_errors=True)


def part_watch():
    print("=== W. dt5g_writer_watch phân loại theo sổ chạy ===")
    sb = tempfile.mkdtemp()
    os.makedirs(os.path.join(sb, "data"))
    os.environ["WORKDIR_8L"] = sb
    sys.path.insert(0, HERE)
    import importlib
    import dt5g_writer_watch as W
    W = importlib.reload(W)
    log = W.PUBLISH_RUNS_LOG
    ck("watch đọc log trong WORKDIR_8L (sandbox)", log.startswith(sb), log)
    pings = []
    W.notify = lambda *a: pings.append(("notify",) + a)
    W.bus = lambda *a: pings.append(("bus",) + a)
    rows = [{"time": "2026-10-23", "state": "2", "state_raw": "2", "asof_date": "2026-10-23"}]
    W.bq_query_csv = lambda sql: (rows, None)
    open(W.LOCAL_CSV, "w").write("time,state,state_raw\n2026-10-23,2,2\n")

    def put_log(*recs):
        with open(log, "w", encoding="utf-8") as f:
            for r in recs:
                f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")

    def rec(ev, hhmm, rid="r1", **kw):
        h, m = hhmm
        return dict(event=ev, ts=dt.datetime(2026, 10, 25, h, m, tzinfo=ICT).isoformat(), run_id=rid,
                    parent="bash", parent_cmd="bash -c x", **kw)

    def run(lastmod_hm, label):
        if os.path.exists(W.STATE_CSV):
            os.remove(W.STATE_CSV)
        del pings[:]
        W.table_lastmod = lambda: (dt.datetime(2026, 10, 25, *lastmod_hm, tzinfo=ICT), None)
        sys.argv = ["dt5g_writer_watch.py", "--label", label]
        buf = io.StringIO()
        with redirect_stdout(buf):
            W.main()
        out = buf.getvalue()
        wc = [x for x in out.split() if x.startswith("writer_class=")]
        return (wc[0].split("=", 1)[1] if wc else "?"), out, len(pings)

    try:
        put_log(rec("START", (11, 40)), rec("END", (11, 52), publish_ok=True))
        wc, out, n = run((11, 50), "sc-match")
        ck("log khớp (giữa START..END) ⇒ OURS_MANUAL, QUIET, 0 ping", wc == "OURS_MANUAL" and "QUIET" in out and n == 0, out)
        wc, out, n = run((11, 56), "sc-tol")
        ck("lastmod END+4' (trong ±5') ⇒ OURS_MANUAL", wc == "OURS_MANUAL" and n == 0, out)
        wc, out, n = run((11, 36), "sc-tol2")
        ck("lastmod START−4' ⇒ OURS_MANUAL", wc == "OURS_MANUAL" and n == 0, out)
        wc, out, n = run((11, 58), "sc-tol-edge")
        ck("lastmod END+6' (ngoài ±5') ⇒ OTHER", wc == "OTHER" and n > 0, out)
        wc, out, n = run((12, 12), "sc-far")
        ck("lastmod END+20' ⇒ OTHER, WARN có ping", wc == "OTHER" and "[WARN]" in out and n > 0, out)
        os.remove(log)
        wc, out, n = run((11, 50), "sc-nolog")
        ck("không có sổ chạy ⇒ OTHER, WARN có ping (như cũ)", wc == "OTHER" and "[WARN]" in out and n > 0, out)
        put_log(rec("START", (11, 40)), rec("END", (11, 41), publish_ok=None))
        wc, out, n = run((11, 44), "sc-crashed")
        ck("run chết trước publish (END publish_ok=null) ⇒ KHÔNG che writer lạ: OTHER/WARN", wc == "OTHER" and n > 0, out)
        put_log(rec("START", (11, 40)), rec("END", (11, 52), publish_ok=False))
        wc, out, n = run((11, 50), "sc-abort")
        ck("run publish_ok=false (MERGE có thể đã ghi trước abort) ⇒ vẫn OURS_MANUAL", wc == "OURS_MANUAL", out)
        put_log(rec("START", (11, 40)))
        wc, out, n = run((12, 5), "sc-noend")
        ck("thiếu END ⇒ cửa sổ START+30': lastmod +25' ⇒ OURS_MANUAL", wc == "OURS_MANUAL" and n == 0, out)
        wc, out, n = run((12, 30), "sc-noend-far")
        ck("thiếu END: lastmod +50' ⇒ OTHER", wc == "OTHER" and n > 0, out)
        put_log("{dòng hỏng", '{"event":"START","ts":"2026-10-25T11:40:00","run_id":"naive"}',
                rec("START", (9, 0), rid="old"), rec("END", (9, 10), rid="old"))
        wc, out, n = run((11, 50), "sc-corrupt")
        ck("dòng hỏng + ts không múi giờ bị bỏ qua, không crash ⇒ OTHER", wc == "OTHER" and n > 0, out)
        put_log(rec("START", (11, 40)), rec("END", (11, 52), publish_ok=True))
        wc, out, n = run((18, 40), "sc-cron")
        ck("trong cửa sổ cron ⇒ vẫn OURS (log không đổi nhãn này)", wc == "OURS" and n == 0, out)
        wc, out, n = run((17, 0), "sc-kaffa")
        ck("cửa sổ kaffa ⇒ vẫn KAFFA_KNOWN", wc == "KAFFA_KNOWN" and n == 0, out)
        put_log(rec("START", (16, 55), rid="k"), rec("END", (17, 5), rid="k", publish_ok=True))
        wc, out, n = run((17, 0), "sc-kaffa-log")
        ck("log khớp nhưng trong cửa sổ kaffa ⇒ giữ KAFFA_KNOWN (log chỉ đổi nhãn OTHER)", wc == "KAFFA_KNOWN", out)
        put_log(rec("START", (11, 40)), rec("END", (11, 52), publish_ok=True))
        rows.append(dict(rows[0], time="2026-10-24", state="4"))
        open(W.LOCAL_CSV, "a").write("2026-10-24,2,2\n")
        wc, out, n = run((11, 50), "sc-diff")
        ck("OURS_MANUAL KHÔNG nuốt lệch giá trị: state lệch ⇒ vẫn HIGH", wc == "OURS_MANUAL" and "[HIGH]" in out and n > 0, out)
    finally:
        shutil.rmtree(sb, ignore_errors=True)


def inner():
    part_publisher()
    part_watch()
    print(f"inner: {'PASS' if not FAILS else 'FAIL ' + str(FAILS)}")
    return 1 if FAILS else 0


def main():
    if "--inner" in sys.argv:
        return inner()
    rc = 0
    for label, env in (("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                       ("TZ=Pacific/Kiritimati", dict(os.environ, TZ="Pacific/Kiritimati")),
                       ("TZ=America/New_York", dict(os.environ, TZ="America/New_York"))):
        print(f"##### {label} #####")
        env["MIKE_BOT_TEST_MODE"] = "1"
        rc |= subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env).returncode
    print("TỔNG:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
