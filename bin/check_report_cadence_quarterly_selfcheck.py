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


def block(text, tag):
    m = re.search(tag + r"_BEGIN[^\n]*\n(.*?)(?:  )?# ── " + tag + "_END", text, re.S)
    if not m:
        print(f"FATAL: không trích được {tag}"); sys.exit(1)
    return m.group(1)


def run_navguard(text, today, nav_rows, kind="quarterly", overdue="0", pkey="quarterly_2026-Q4", state=None):
    """Chạy NAVCHECK (hàm) + NAVGUARD THẬT. nav_rows: {account: [(ngày, nav_is_estimate)]}.
    Trả dict: dispatched(bool), events([(type, topic)]), state(dict sau chạy), overdue_after."""
    import json as _j
    with tempfile.TemporaryDirectory() as td:
        nd = Path(td) / "nav"; nd.mkdir()
        for a in ACCTS:
            (nd / f"nav_history_{a}.csv").write_text(
                "date,nav,mtm_stock,cash,margin_debt,offbook_assets,egg_assets,balance_ts,cum_dividend_excl,nav_is_estimate,nav_source\n"
                + "".join(f"{d},1,1,1,0,0,0,x,0,{est},live\n" for d, est in nav_rows.get(a, [])))
        bindir = Path(td) / "bin"; bindir.mkdir()
        (bindir / "notify_thread.sh").write_text("#!/bin/bash\nexit 0\n")
        (bindir / "append_event.sh").write_text(f'#!/bin/bash\necho "$2|$3" >> {td}/events.log\n')
        for n in ("notify_thread.sh", "append_event.sh"): (bindir / n).chmod(0o755)
        sf = Path(td) / "state.json"; sf.write_text(_j.dumps(state or {}))
        script = (f'ROOT={td}; WC_ROOT={td}; NAV_DIR={nd}; STATE={sf}; TRADING_REPORT_THREAD=t; KIND={kind}; OVERDUE={overdue}; '
                  f'TODAY={today}; DESC="quý X"; PKEY={pkey}\n{block(text, "NAVCHECK")}\n'
                  f'for i in 1; do\n{block(text, "NAVGUARD")}\necho DISPATCH OVERDUE=$OVERDUE\ndone\n')
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        ev = Path(td) / "events.log"
        events = [tuple(l.split("|", 1)) for l in ev.read_text().splitlines()] if ev.exists() else []
        return {"dispatched": r.returncode == 0 and "DISPATCH" in r.stdout, "events": events,
                "state": _j.loads(sf.read_text()), "rc": r.returncode, "out": r.stdout, "err": r.stderr[-200:]}


def run_nav_helpers(text, fn, arg):
    script = f'WC_ROOT=/nonexistent\n{block(text, "NAVCHECK")}\n{fn} "{arg}"\n'
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    return r.stdout.strip()


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
    chk("5b state = 2 ngày trước ⇒ chạy lại (rescue)", keys(run_detector(text, "2026-12-31", "quarterly", state={"quarterly_2026-Q4": "2026-12-29"})) == ["quarterly_2026-Q4"])
    chk("5b2 state = hôm qua ⇒ KHÔNG chạy (chống double-dispatch)", keys(run_detector(text, "2026-12-31", "quarterly", state={"quarterly_2026-Q4": "2026-12-30"})) == [])
    chk("5c cả 2 file đã giao ⇒ 0", keys(run_detector(text, "2026-12-31", "quarterly", files=done_files("2026-Q4"))) == [])
    chk("5d chỉ 1/2 file có ⇒ vẫn chạy", keys(run_detector(text, "2026-12-31", "quarterly", files=done_files("2026-Q4")[:1])) == ["quarterly_2026-Q4"])
    # 6. trước go-live (2026-Q4): Q3/2026 KHÔNG backfill; quý chứa ngày khởi điểm của builder là việc của build.py (xem phần builder)
    chk("6 30/09/2026 ⇒ 0 (trước go-live Q4)", keys(run_detector(text, "2026-09-30", "quarterly")) == [])
    # 7. watchdog (không cờ): rescue quý vừa đóng
    o = run_detector(text, "2027-01-01", "")
    qa = [a for a in o["actions"] if a["kind"] == "quarterly"]
    chk("7 watchdog 01/01/2027 chưa có file ⇒ quarterly_2026-Q4 overdue=True", len(qa) == 1 and qa[0]["period_key"] == "quarterly_2026-Q4" and qa[0]["overdue"] is True, str(qa))
    # 7f. double-dispatch: lượt 21:00 31/12 ghi state; watchdog 08:30 01/01 (~11,5h sau) KHÔNG được dispatch lần 2
    wq = lambda today, st, files=(): [a for a in run_detector(text, today, "", files=files, state=st)["actions"] if a["kind"] == "quarterly"]
    chk("7f watchdog sau 21:00 cùng quý (state=hôm qua) ⇒ KHÔNG rescue", wq("2027-01-01", {"quarterly_2026-Q4": "2026-12-31"}) == [])
    chk("7g watchdog state cũ ≥2 ngày ⇒ rescue", len(wq("2027-01-02", {"quarterly_2026-Q4": "2026-12-31"})) == 1)
    chk("7h watchdog không state ⇒ rescue", len(wq("2027-01-01", {})) == 1)
    chk("7i state hỏng (chuỗi rác) ⇒ KHÔNG dispatch (fail-safe chống email trùng)", wq("2027-01-01", {"quarterly_2026-Q4": "rac"}) == [])
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
    # 10. NAVGUARD: kiểm NAV của NGÀY LÀM VIỆC CUỐI ≤ cuối quý (không phải $TODAY), cả watchdog, cả nav_is_estimate
    ok = lambda d: [(d, "False")]
    both = lambda d: {"SpaceX": ok(d), "ZaloPay": ok(d)}
    g = lambda *a, **k: run_navguard(text, *a, **k)
    chk("10 đủ NAV chốt cả 2 ⇒ dispatch", g("2026-12-31", both("2026-12-31"))["dispatched"])
    r = g("2026-12-31", {"SpaceX": ok("2026-12-31"), "ZaloPay": ok("2026-12-30")})
    chk("10b thiếu ZaloPay ⇒ HOÃN + ghi dấu deferred, KHÔNG state dispatch", not r["dispatched"] and "deferred_quarterly_2026-Q4" in r["state"]
        and "quarterly_2026-Q4" not in r["state"] and ("status", "report-cadence-quarterly-deferred-quarterly_2026-Q4") in r["events"], str(r))
    chk("10c thiếu cả 2 ⇒ HOÃN", not g("2026-12-31", {})["dispatched"])
    chk("10d cuối quý T7 (2029-03-31): có NAV thứ Sáu 03-30 ⇒ dispatch", g("2029-03-31", both("2029-03-30"), pkey="quarterly_2029-Q1")["dispatched"])
    chk("10d2 cuối quý T7: THIẾU NAV thứ Sáu ⇒ HOÃN (trước đây bỏ qua T7)", not g("2029-03-31", {}, pkey="quarterly_2029-Q1")["dispatched"])
    chk("10d3 cuối quý CN (2028-12-31): kiểm thứ Sáu 12-29", g("2028-12-31", both("2028-12-29"), pkey="quarterly_2028-Q4")["dispatched"] and not g("2028-12-31", both("2028-12-31"), pkey="quarterly_2028-Q4")["dispatched"])
    chk("10e nav_is_estimate=True ⇒ HOÃN", not g("2026-12-31", {"SpaceX": [("2026-12-31", "True")], "ZaloPay": ok("2026-12-31")})["dispatched"])
    chk("10f kind monthly thiếu NAV ⇒ không bị chặn", g("2026-12-31", {}, kind="monthly", pkey="monthly_2026-12")["dispatched"])
    # watchdog (OVERDUE=1) — trước đây bỏ qua NAVGUARD
    r = g("2027-01-01", {}, overdue="1")
    chk("10g watchdog thiếu NAV ⇒ HOÃN + bus QUESTION (topic overdue-<PKEY> để closer đóng)",
        not r["dispatched"] and ("question", "report-cadence-overdue-quarterly_2026-Q4") in r["events"]
        and "vẫn CHỜ NAV" in r["out"] and "KHÔNG tự soạn" not in r["out"], str(r))
    chk("10h watchdog đủ NAV, KHÔNG dấu deferred ⇒ dispatch, vẫn OVERDUE=1 (cảnh báo đỏ đúng nghĩa)",
        (lambda r: r["dispatched"] and "OVERDUE=1" in r["out"])(g("2027-01-01", both("2026-12-31"), overdue="1")))
    r = g("2027-01-01", both("2026-12-31"), overdue="1", state={"deferred_quarterly_2026-Q4": "2026-12-31"})
    chk("10i watchdog đủ NAV + CÓ dấu hoãn từ 21:00 ⇒ dispatch với OVERDUE=0 (không đỏ 'quá hạn' giả)", r["dispatched"] and "OVERDUE=0" in r["out"], str(r))
    r = g("2027-01-06", {}, overdue="1")
    chk("10j quá 4 ngày vẫn thiếu NAV ⇒ KHÔNG tự dispatch, giữ question hỏi người (fail-safe)",
        not r["dispatched"] and ("question", "report-cadence-overdue-quarterly_2026-Q4") in r["events"] and "NAV đã đủ" not in r["out"], str(r))
    r = g("2027-01-06", {"SpaceX": [("2026-12-31", "True")], "ZaloPay": ok("2026-12-31")}, overdue="1", state={"deferred_quarterly_2026-Q4": "2026-12-31"})
    chk("10j2 quá 4 ngày + dấu hoãn + NAV SpaceX vẫn ước lượng ⇒ KHÔNG dispatch, KHÔNG 'NAV đã đủ', OVERDUE không bị tắt",
        not r["dispatched"] and "NAV đã đủ" not in r["out"] and "OVERDUE=0" not in r["out"] and ("question", "report-cadence-overdue-quarterly_2026-Q4") in r["events"], str(r))
    r = g("2027-01-06", both("2026-12-31"), overdue="1", state={"deferred_quarterly_2026-Q4": "2026-12-31"})
    chk("10j3 quá 4 ngày nhưng NAV nay ĐỦ + có dấu hoãn ⇒ dispatch OVERDUE=0 (đường cứu vẫn chạy)", r["dispatched"] and "OVERDUE=0" in r["out"], str(r))
    chk("10k watchdog hoãn ở hôm nay, hôm qua đã state key ⇒ không ghi nhầm state dispatch", "quarterly_2026-Q4" not in g("2027-01-01", {}, overdue="1")["state"])
    # hàm thuần
    chk("11 _q_nav_check_date(2029-03-31 T7)=2029-03-30", run_nav_helpers(text, "_q_nav_check_date", "2029-03-31") == "2029-03-30")
    chk("11b CN 2028-12-31 ⇒ 2028-12-29", run_nav_helpers(text, "_q_nav_check_date", "2028-12-31") == "2028-12-29")
    chk("11c T4 2026-12-31 ⇒ chính nó", run_nav_helpers(text, "_q_nav_check_date", "2026-12-31") == "2026-12-31")
    # 12. §16: date -d trong script phải ghim TZ=UTC; chạy guard + helper dưới TZ chết `date -d`
    for tz in ("Asia/Beirut", "Atlantic/Azores", "America/Sao_Paulo"):
        old = os.environ.get("TZ"); os.environ["TZ"] = tz
        try:
            gq = [run_guard(text, d) for d in ("2030-03-31", "2030-06-30", "2029-03-31", "2030-03-30")]
            hq = run_nav_helpers(text, "_q_nav_check_date", "2030-03-31")
        finally:
            (os.environ.__setitem__("TZ", old) if old is not None else os.environ.pop("TZ", None))
        chk(f"12 TZ={tz}: guard 2030-03-31/06-30 qua, 03-30 không; helper đúng", gq == [True, True, True, False] and hq == "2030-03-29", f"{gq} {hq}")
    bare = [ln for ln in text.splitlines() if re.search(r"(?<!TZ=UTC )\bdate -d\b", ln) and "TZ=" not in ln.split("date -d")[0][-30:]
            and not ln.lstrip().startswith("#") and "Asia/Ho_Chi_Minh" not in ln]
    chk("12b mọi `date -d` (ngoài comment/ICT) đều ghim TZ=", not bare, str(bare[:3]))
    # 13. sweep gồm *_quarterly_report_*.md + dispatch có write-scope
    chk("13 delivery sweep gồm *_quarterly_report_*.md", '"$ROOT"/reports/*_quarterly_report_*.md; do' in text)
    chk("13b dispatch quý có --write-scope 2 file đích (có điều kiện KIND=quarterly)",
        re.search(r'\[ "\$KIND" = "quarterly" \] && WS_ARGS=\(--write-scope "\$\{TFILE_SX\},\$\{TFILE_ZP\}"\)', text) is not None and "${WS_ARGS[@]+" in text)
    chk("13c prompt không còn claim sai 'builder rc=3' cho thiếu NAV", "THIẾU NAV ngày cuối quý (nav_history chưa có dòng" not in text)
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
        ("M6 bỏ chống double-dispatch (min_age 0)", "def recently_dispatched(pk, min_age_days=2):", "def recently_dispatched(pk, min_age_days=0):"),
        ("M7 chỉ cần 1 account giao là đủ", "    return all(\n        _delivered_any(files, lambda bn, acct=acct: bn.startswith(acct + \"_quarterly_report_\")", "    return any(\n        _delivered_any(files, lambda bn, acct=acct: bn.startswith(acct + \"_quarterly_report_\")"),
        ("M9 NAVGUARD không continue (vẫn dispatch khi thiếu NAV)", "      continue\n    fi\n    if [ \"$OVERDUE\" = \"1\" ]; then", "      :\n    fi\n    if [ \"$OVERDUE\" = \"1\" ]; then"),
        ("M10 NAVGUARD chỉ kiểm 1 account", "for a in SpaceX ZaloPay; do", "for a in SpaceX; do"),
        ("M11 NAVGUARD kiểm $TODAY thay vì ngày làm việc cuối ≤ cuối quý", '_q_nav_problems "$_QCHK"', '_q_nav_problems "$TODAY"'),
        ("M12 bỏ kiểm nav_is_estimate", '      FOUND:True) out=', '      FOUND:Zzz) out='),
        ("M13 NAVGUARD bỏ qua watchdog", '[ -n "$_NAV_MISSING" ] && [ "$_QAGE" -le', '[ "$OVERDUE" = "0" ] && [ -n "$_NAV_MISSING" ] && [ "$_QAGE" -le'),
        ("M14 watchdog không nhận dấu hoãn ⇒ đỏ 'quá hạn' giả", 'then OVERDUE=0; _RESUMED_NOTE', 'then :; _RESUMED_NOTE'),
        ("M15 dispatch quý bỏ --write-scope", 'WS_ARGS=(); [ "$KIND" = "quarterly" ] && WS_ARGS=(--write-scope', 'WS_ARGS=(); [ "$KIND" = "never" ] && WS_ARGS=(--write-scope'),
        ("M16 QGUARD bỏ ghim TZ=UTC", '_Q_NEXT_DOM="$(TZ=UTC date -d', '_Q_NEXT_DOM="$(date -d'),
        ("M17 sweep không gồm quarterly", ' "$ROOT"/reports/*_quarterly_report_*.md; do', '; do'),
        ("M18 hoãn watchdog không phát question", '_EVT=question;', '_EVT=status;'),
        ("M19 quá trần hoãn vẫn tự dispatch dù NAV thiếu/ước lượng (hành vi vòng 1)", '    if [ -n "$_NAV_MISSING" ]; then\n      _NM="🔴', '    if false; then\n      _NM="🔴'),
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
