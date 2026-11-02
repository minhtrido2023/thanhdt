#!/usr/bin/env python3
"""Selfcheck cho cờ --scheduled-quarterly của bin/check_report_cadence.sh (user duyệt 02/11/2026).

Trích 2 khối THẬT trong script (không chép logic): detector python (heredoc PYEOF) và QGUARD (bash,
giữa QGUARD_BEGIN/END). Chạy trên fixture, rồi MUTATION TEST: sửa nguồn theo 8 cách và đòi selfcheck
phải ĐỎ ở mỗi cách. Chạy dưới `env -u TZ` và `TZ=America/Los_Angeles` (§16/§19):
  env -u TZ python3 bin/check_report_cadence_quarterly_selfcheck.py
  TZ=America/Los_Angeles python3 bin/check_report_cadence_quarterly_selfcheck.py
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC0 = ROOT / "bin" / "check_report_cadence.sh"
ACCTS = ("SpaceX", "ZaloPay")


def detector_block(text):
    m = re.search(r'PLAN="\$\(python3 - "\$WC_ROOT" "\$TODAY" "\$STATE" "\$DELIVERY_STATE" << \'PYEOF\'\n(.*?)\nPYEOF\n', text, re.S)
    if not m:
        print("FATAL: không trích được detector"); sys.exit(1)
    return m.group(1)


def guard_block(text):
    m = re.search(r"QGUARD_BEGIN[^\n]*\n(.*?)# ── QGUARD_END", text, re.S)
    if not m:
        print("FATAL: không trích được QGUARD"); sys.exit(1)
    return m.group(1)


def run_detector(text, today, kind, files=(), state=None, pending=()):
    with tempfile.TemporaryDirectory() as td:
        rep = Path(td) / "mike" / "reports"; rep.mkdir(parents=True)
        recs = {}
        for fn in files:
            p = rep / fn; p.write_text("fixture", encoding="utf-8")
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            ok = {"status": "delivered", "delivered_at": "x", "sha256": sha}
            recs[fn] = {"sha256": sha, "artifact_validated_at": "x", "discord": ok, "email": ok}
        st = Path(td) / "s.json"; st.write_text(json.dumps(state or {}))
        dl = Path(td) / "d.json"; dl.write_text(json.dumps({"reports": recs}))
        py = Path(td) / "b.py"; py.write_text(detector_block(text), encoding="utf-8")
        env = dict(os.environ, RC_PENDING_TOPICS="\n".join(pending), REPORT_SCHEDULED_KIND=kind,
                   RC_BIN_DIR=str(ROOT / "bin"))
        r = subprocess.run([sys.executable, str(py), td, today, str(st), str(dl)], capture_output=True, text=True, env=env)
        if r.returncode != 0:
            return {"__crash__": r.stderr[-300:]}
        return json.loads(r.stdout)


def run_guard(text, today):
    """True nếu guard CHO QUA (tới được dòng REACHED), False nếu thoát sớm."""
    script = f'SCHEDULED_KIND=quarterly\nTODAY={today}\n{guard_block(text)}\necho REACHED\n'
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    return r.returncode == 0 and "REACHED" in r.stdout and r.stdout.strip() == "REACHED"


def navguard_block(text):
    m = re.search(r"NAVGUARD_BEGIN[^\n]*\n(.*?)  # ── NAVGUARD_END", text, re.S)
    if not m:
        print("FATAL: không trích được NAVGUARD"); sys.exit(1)
    return m.group(1)


def run_navguard(text, today, nav_dates, kind="quarterly", overdue="0"):
    """True nếu vòng lặp ĐI TIẾP TỚI bước dispatch; False nếu NAVGUARD `continue`. nav_dates: {account: [ngày]}"""
    with tempfile.TemporaryDirectory() as td:
        nd = Path(td) / "nav"; nd.mkdir()
        for a in ACCTS:
            (nd / f"nav_history_{a}.csv").write_text("date,nav\n" + "".join(f"{d},1\n" for d in nav_dates.get(a, [])))
        bindir = Path(td) / "bin"; bindir.mkdir()
        for n in ("notify_thread.sh", "append_event.sh"):
            (bindir / n).write_text("#!/bin/bash\nexit 0\n"); (bindir / n).chmod(0o755)
        script = (f'ROOT={td}; WC_ROOT={td}; NAV_DIR={nd}; TRADING_REPORT_THREAD=t; KIND={kind}; OVERDUE={overdue}; '
                  f'TODAY={today}; DESC="quý X"; PKEY=quarterly_X\nfor i in 1; do\n{navguard_block(text)}\necho DISPATCH\ndone\n')
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        return r.returncode == 0 and "DISPATCH" in r.stdout


def done_files(qk):
    return [f"{a}_quarterly_report_{qk}.md" for a in ACCTS]


def suite(text):
    res = []
    def chk(name, cond, detail=""):
        res.append((name, bool(cond), detail))
    def acts(o):
        return o.get("actions", o)
    def keys(o):
        return [a["period_key"] for a in o["actions"]] if "actions" in o else o

    # 1. đúng ngày cuối quý ⇒ đúng 1 action quý, không lẫn weekly/monthly (không file nào ⇒ weekly/monthly sẽ backfill nếu rò)
    o = run_detector(text, "2026-12-31", "quarterly")
    chk("1 31/12/2026 ⇒ đúng [quarterly_2026-Q4]", keys(o) == ["quarterly_2026-Q4"], str(keys(o)))
    a = o.get("actions", [{}])[0]
    chk("1b target_file đúng tên + overdue=False", a.get("target_file_spacex", "").endswith("SpaceX_quarterly_report_2026-Q4.md")
        and a.get("target_file_zalopay", "").endswith("ZaloPay_quarterly_report_2026-Q4.md") and a.get("overdue") is False, str(a))
    # 2. không đúng ngày cuối quý ⇒ detector không ra action (guard bash thoát trước, đây là lớp 2)
    for d in ("2026-12-30", "2026-12-28", "2026-12-01", "2026-11-30", "2027-01-01", "2026-10-31"):
        chk(f"2 {d} (quarterly) ⇒ 0 action", keys(run_detector(text, d, "quarterly")) == [], d)
    # 3. năm nhuận + các quý khác
    chk("3 29/02/2028 (nhuận, KHÔNG phải cuối quý) ⇒ 0", keys(run_detector(text, "2028-02-29", "quarterly")) == [])
    for d, q in (("2027-03-31", "2027-Q1"), ("2028-03-31", "2028-Q1"), ("2028-06-30", "2028-Q2"), ("2027-09-30", "2027-Q3")):
        chk(f"3 {d} ⇒ {q}", keys(run_detector(text, d, "quarterly")) == [f"quarterly_{q}"], d)
    # 4. cuối quý rơi T7/CN: vẫn chạy đúng ngày đó (builder lấy phiên ≤ cuối quý)
    for d, q in (("2029-03-31", "2029-Q1"), ("2028-12-31", "2028-Q4")):
        wd = date.fromisoformat(d).weekday()
        chk(f"4 {d} là {'T7' if wd == 5 else 'CN'} ⇒ {q}", wd >= 5 and keys(run_detector(text, d, "quarterly")) == [f"quarterly_{q}"], f"wd={wd}")
    # 5. idempotent: state hôm nay đã dispatch ⇒ 0; ngày hôm trước ⇒ vẫn chạy (retry tự nhiên)
    chk("5 state = hôm nay ⇒ 0 (chạy 2 lần)", keys(run_detector(text, "2026-12-31", "quarterly", state={"quarterly_2026-Q4": "2026-12-31"})) == [])
    chk("5b state = hôm qua ⇒ vẫn chạy", keys(run_detector(text, "2026-12-31", "quarterly", state={"quarterly_2026-Q4": "2026-12-30"})) == ["quarterly_2026-Q4"])
    chk("5c cả 2 file đã giao ⇒ 0", keys(run_detector(text, "2026-12-31", "quarterly", files=done_files("2026-Q4"))) == [])
    chk("5d chỉ 1/2 file có ⇒ vẫn chạy", keys(run_detector(text, "2026-12-31", "quarterly", files=done_files("2026-Q4")[:1])) == ["quarterly_2026-Q4"])
    # 6. trước go-live (2026-Q4): Q3/2026 KHÔNG backfill; quý chứa ngày khởi điểm của builder là việc của build.py (xem phần builder)
    chk("6 30/09/2026 ⇒ 0 (trước go-live Q4)", keys(run_detector(text, "2026-09-30", "quarterly")) == [])
    # 7. watchdog (không cờ): rescue quý vừa đóng
    o = run_detector(text, "2027-01-01", "")
    qa = [a for a in o["actions"] if a["kind"] == "quarterly"]
    chk("7 watchdog 01/01/2027 chưa có file ⇒ quarterly_2026-Q4 overdue=True", len(qa) == 1 and qa[0]["period_key"] == "quarterly_2026-Q4" and qa[0]["overdue"] is True, str(qa))
    chk("7b watchdog khi đã giao ⇒ không action quý", not [a for a in run_detector(text, "2027-01-01", "", files=done_files("2026-Q4"))["actions"] if a["kind"] == "quarterly"])
    chk("7c watchdog 31/12/2026 (quý chưa đóng) ⇒ không action quý", not [a for a in run_detector(text, "2026-12-31", "")["actions"] if a["kind"] == "quarterly"])
    chk("7d watchdog 02/11/2026 (Q3 trước go-live) ⇒ không action quý", not [a for a in run_detector(text, "2026-11-02", "")["actions"] if a["kind"] == "quarterly"])
    chk("7e cờ monthly/weekly ngày 1/1 KHÔNG sinh action quý",
        not [a for k in ("monthly", "weekly") for a in run_detector(text, "2027-01-01", k)["actions"] if a["kind"] == "quarterly"])
    # 8. closer
    o = run_detector(text, "2027-01-02", "", files=done_files("2026-Q4"), pending=["report-cadence-overdue-quarterly_2026-Q4"])
    chk("8 closable khi quý đã giao", [c[0] for c in o.get("closable", [])] == ["quarterly_2026-Q4"], str(o.get("closable")))
    o = run_detector(text, "2027-01-02", "", pending=["report-cadence-overdue-quarterly_2026-Q4"])
    chk("8b KHÔNG closable khi chưa giao", o.get("closable") == [], str(o.get("closable")))
    # 9. guard bash (lớp 1, thoát im lặng)
    for d, exp in (("2026-12-31", True), ("2026-12-30", False), ("2026-12-28", False), ("2027-01-31", False), ("2026-11-30", False),
                   ("2026-06-30", True), ("2028-02-29", False), ("2028-03-31", True), ("2029-03-31", True), ("2027-09-30", True), ("2027-03-30", False)):
        chk(f"9 guard {d} ⇒ {'qua' if exp else 'thoát rc=0 im lặng'}", run_guard(text, d) is exp)
    # 10. NAVGUARD (21:00 phải có NAV ngày cuối quý của cả 2 account)
    both = {"SpaceX": ["2026-12-31"], "ZaloPay": ["2026-12-31"]}
    chk("10 đủ NAV cả 2 ⇒ dispatch", run_navguard(text, "2026-12-31", both) is True)
    chk("10b thiếu ZaloPay ⇒ HOÃN", run_navguard(text, "2026-12-31", {"SpaceX": ["2026-12-31"], "ZaloPay": ["2026-12-30"]}) is False)
    chk("10c thiếu cả 2 ⇒ HOÃN", run_navguard(text, "2026-12-31", {}) is False)
    chk("10d cuối quý T7 (2029-03-31) không có NAV ⇒ vẫn dispatch", run_navguard(text, "2029-03-31", {}) is True)
    chk("10e watchdog (OVERDUE=1) thiếu NAV ⇒ vẫn dispatch", run_navguard(text, "2027-01-01", {}, overdue="1") is True)
    chk("10f kind monthly thiếu NAV ⇒ không bị chặn", run_navguard(text, "2026-12-31", {}, kind="monthly") is True)
    return res


def report(res, label):
    bad = [r for r in res if not r[1]]
    for n, ok, d in res:
        if not ok:
            print(f"  ❌ [{label}] {n} — {d}")
    return bad


def main():
    text = SRC0.read_text(encoding="utf-8")
    print(f"selfcheck quarterly — TZ={os.environ.get('TZ')!r}")
    res = suite(text)
    bad = report(res, "base")
    print(f"BASE: {len(res) - len(bad)}/{len(res)} PASS")
    # builder: quý chứa ngày khởi điểm (không vỡ) — cadence quarterly của report_v2_selfcheck
    # (chạy riêng, xem hướng dẫn trong báo cáo; không lặp ở đây để selfcheck này không phụ thuộc BQ)
    MUT = [
        ("M1 bỏ điều kiện 'ngày mai sang tháng khác' (đoán d.day>=28)", "(d + timedelta(days=1)).month != d.month", "d.day >= 28"),
        ("M2 guard bash không thoát", "    exit 0\n  fi\nfi\n# ── QGUARD_END", "    :\n  fi\nfi\n# ── QGUARD_END"),
        ("M3 weekly backfill rò sang quarterly", 'if scheduled_kind not in ("weekly", "monthly", "quarterly"):', 'if scheduled_kind not in ("weekly", "monthly"):'),
        ("M4a monthly rò sang quarterly (bỏ CẢ 2 guard, vì chúng dư thừa nhau)", None, None),
        ("M4b chỉ bỏ guard ngoài (guard trong còn chặn ⇒ mutant tương đương, phải SỐNG)", None, None),
        ("M5 go-live lùi về 2026-Q1", "GO_LIVE_QUARTER = (2026, 4)", "GO_LIVE_QUARTER = (2026, 1)"),
        ("M6 bỏ idempotency state", 'if state.get(period_key) != today_s:\n            sx_f, zp_f = quarterly_filenames(qk)', 'if True:\n            sx_f, zp_f = quarterly_filenames(qk)'),
        ("M7 chỉ cần 1 account giao là đủ", "    return all(\n        _delivered_any(files, lambda bn, acct=acct: bn.startswith(acct + \"_quarterly_report_\")", "    return any(\n        _delivered_any(files, lambda bn, acct=acct: bn.startswith(acct + \"_quarterly_report_\")"),
        ("M9 NAVGUARD không continue (vẫn dispatch khi thiếu NAV)", "      continue\n    fi\n  fi\n  # ── NAVGUARD_END", "      :\n    fi\n  fi\n  # ── NAVGUARD_END"),
        ("M10 NAVGUARD chỉ kiểm 1 account", "for _a in SpaceX ZaloPay; do", "for _a in SpaceX; do"),
        ("M11 NAVGUARD đòi NAV cả cuối tuần", '[ "$(date -d "$TODAY" +%u)" -le 5 ]', "true"),
        ("M8 watchdog đánh dấu overdue=False", '"overdue": scheduled_kind == "",\n            })\n\n# ── RC_CLOSE_BEGIN', '"overdue": False,\n            })\n\n# ── RC_CLOSE_BEGIN'),
    ]
    caught = 0
    G1 = ('scheduled_kind != "quarterly" and (today.day >= 5 or scheduled_kind == "monthly")', '(today.day >= 5 or scheduled_kind == "monthly")')
    G2 = ('scheduled_kind not in ("weekly", "quarterly"):', 'scheduled_kind != "weekly":')
    for name, old, new in MUT:
        if name.startswith("M4"):
            mt = text
            for a in ((G1, G2) if name.startswith("M4a") else (G1,)):
                assert mt.count(a[0]) == 1, a[0]
                mt = mt.replace(a[0], a[1])
            mbad = [r for r in suite(mt) if not r[1]]
            if name.startswith("M4a"):
                print(f"  {'✅ bắt được' if mbad else '❌ KHÔNG bắt được'}: {name} ({len(mbad)} ca đỏ)")
                caught += bool(mbad)
                if not mbad: bad.append((name, False, "mutant sống sót"))
            else:
                print(f"  {'✅ tương đương (sống sót đúng như dự kiến)' if not mbad else '⚠️ lẽ ra tương đương'}: {name}")
                caught += not mbad
                if mbad: bad.append((name, False, "không tương đương"))
            continue
        if text.count(old) != 1:
            print(f"  ❌ mutation không áp được ({text.count(old)} khớp): {name}"); bad.append((name, False, "mutation"))
            continue
        mres = suite(text.replace(old, new))
        mbad = [r for r in mres if not r[1]]
        print(f"  {'✅ bắt được' if mbad else '❌ KHÔNG bắt được'}: {name} ({len(mbad)} ca đỏ)")
        caught += bool(mbad)
        if not mbad:
            bad.append((name, False, "mutant sống sót"))
    print(f"MUTATION: {caught}/{len(MUT)} bị bắt")
    print("KẾT QUẢ:", "PASS" if not bad else f"FAIL ({len(bad)})")
    sys.exit(1 if bad else 0)


main()
