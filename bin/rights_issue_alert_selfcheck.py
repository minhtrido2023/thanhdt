#!/usr/bin/env python3
"""Selfcheck rights_issue_alert.py — hàm thuần, fixture số THẬT SCL (tav2_bq.corporate_action).

Chạy chính nó dưới `env -u TZ` + 2 TZ lạ (§16/§19), rồi MUTANT — mỗi mutant PHẢI làm đỏ.
    python3 bin/rights_issue_alert_selfcheck.py
"""
import contextlib
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{detail}]"))


HOL = {dt.date(2025, 9, 1), dt.date(2025, 9, 2)}
is_hol = HOL.__contains__

# SCL 35,714286% — dòng thật (id, ratio, ex, record, volume, total_value) đọc 2026-10-22
SCL25 = {"id": "682291730e8a716db6edd5a4", "ticker": "SCL", "issue_method_code": "Rights",
         "issue_status_code": "D", "event_status": "executed", "exright_date": "2025-10-17",
         "record_date": "2025-10-20", "public_date": "2025-10-10", "exercise_ratio": "0.35714286",
         "value_per_share": None, "total_value": "1.0E11", "issue_volumn": "8000000"}
# SCL 15,38% — trạng thái P, chưa ngày/giá (thật, public 2026-09-08)
SCL26 = {"id": "6a0516165b1fb4c98c3ab2a2", "ticker": "SCL", "issue_method_code": "Rights",
         "issue_status_code": "P", "event_status": "announced", "exright_date": None,
         "record_date": None, "public_date": "2026-09-08", "exercise_ratio": "0.15384615",
         "value_per_share": None, "total_value": "0.0", "issue_volumn": "0"}
POS = {"SpaceX": {"SCL": 14000, "FPT": 100}, "ZaloPay": {"FPT": 50}}


def run_inner():
    import rights_issue_alert as R
    B = R.build_alerts
    a = B("2025-10-10", POS, [SCL25], set(), is_hol)
    t = a[0]["text"] if a else ""
    ck("SCL 2025 lúc công bố ⇒ 1 cảnh báo", len(a) == 1, a)
    ck("đủ số: 5.000 cp, giá 12.500đ, tiền 62.500.000đ", all(s in t for s in ("5,000 cp", "12,500đ", "62,500,000đ")), t)
    ck("nêu GDKHQ + ngày chốt + thiếu hạn nộp tiền", all(s in t for s in ("2025-10-17", "2025-10-20", "KHÔNG có cột")), t)
    ck("ZaloPay không giữ SCL ⇒ không nêu", "ZaloPay" not in t, t)
    ck("lượt đầu gộp ANNOUNCE+DATED (khoá đủ)", set(a[0]["keys"]) == {f"{SCL25['id']}|announce", f"{SCL25['id']}|dated|2025-10-17"}, a[0]["keys"])
    sent = set(a[0]["keys"])
    ck("cùng ngày chạy lại ⇒ không trùng", B("2025-10-10", POS, [SCL25], sent, is_hol) == [])
    ck("10-10 còn 4 phiên cum; 10-09 còn 5 ⇒ chưa nhắc", R.sessions_until("2025-10-10", "2025-10-17", is_hol) == 4
       and B("2025-10-09", POS, [SCL25], sent, is_hol) == [])
    r = B("2025-10-13", POS, [SCL25], sent, is_hol)
    ck("còn 3 phiên ⇒ REMIND", len(r) == 1 and r[0]["stage"] == "REMIND", r)
    sent |= set(r[0]["keys"]) if r else set()
    r2 = B("2025-10-14", POS, [SCL25], sent, is_hol)
    ck("phiên kế tiếp ⇒ REMIND lại (mỗi phiên 1 lần)", len(r2) == 1 and r2[0]["stage"] == "REMIND", r2)
    ck("ngày GDKHQ trở đi ⇒ im", B("2025-10-17", POS, [SCL25], set(), is_hol) == [])
    ck("ngày lễ không tính là phiên", R.sessions_until("2025-08-29", "2025-09-05", is_hol) == 2)

    p = B("2026-10-22", POS, [SCL26], set(), is_hol)
    tp = p[0]["text"] if p else ""
    ck("SCL 2026 trạng thái P, ngày NULL ⇒ VẪN báo (ANNOUNCE)", len(p) == 1 and p[0]["stage"] == "ANNOUNCE", p)
    ck("P: 2.153 cp, nói rõ CHƯA có ngày/giá", all(s in tp for s in ("2,153 cp", "CHƯA CÓ ngày", "CHƯA CÓ (BQ chưa điền)")), tp)
    sent = set(p[0]["keys"])
    dated = dict(SCL26, exright_date="2026-11-20", record_date="2026-11-23", total_value="1.2E11", issue_volumn="6000000")
    d = B("2026-10-23", POS, [dated], sent, is_hol)
    ck("P → có ngày sau đó ⇒ báo lại DATED dù đã ANNOUNCE", len(d) == 1 and d[0]["stage"] == "DATED", d)
    ck("DATED có giá 20.000 + tiền 43.060.000đ", "43,060,000đ" in (d[0]["text"] if d else ""), d)
    moved = dict(dated, exright_date="2026-11-27")
    ck("đổi ngày GDKHQ ⇒ báo lại", len(B("2026-10-24", POS, [moved], sent | set(d[0]["keys"]), is_hol)) == 1)
    ck("không giữ mã ⇒ im", B("2025-10-10", {"SpaceX": {"FPT": 1}}, [SCL25], set(), is_hol) == [])
    ck("trạng thái N (không thực hiện) ⇒ im", B("2025-10-10", POS, [dict(SCL25, issue_status_code="N")], set(), is_hol) == [])
    ck("không phải Rights (DIV cổ phiếu) ⇒ im", B("2025-10-10", POS, [dict(SCL25, issue_method_code="DIV")], set(), is_hol) == [])
    ck("hồi cứu: sự kiện công bố SAU asof ⇒ im (không nhìn trước)", B("2025-10-13", POS, [SCL26], set(), is_hol) == [])
    ck("value_per_share có ⇒ ưu tiên", R.issue_price(dict(SCL25, value_per_share="10000")) == 10000.0)
    inner_b(R, B)
    inner_main(R)
    n = sum(1 for x in RESULTS if not x)
    print("RESULT:", "PASS" if not n else "FAIL")
    return 0 if not n else 1


# ---- B1: dòng P xác sống — fixture thật đọc từ tav2_bq.corporate_action 2026-10-22
DSC_P1 = {"id": "67f70fd690c07f62ae3f2a46", "ticker": "DSC", "issue_method_code": "Rights", "issue_status_code": "P",
          "event_status": "announced", "exright_date": None, "record_date": None, "public_date": "2025-09-24",
          "exercise_ratio": "0.17251827", "value_per_share": None, "total_value": "0.0", "issue_volumn": "0"}
DSC_P2 = dict(DSC_P1, id="68dc754082ba4d1dc754b816", public_date="2025-09-30")
DSC_D = dict(DSC_P1, id="68dc754082ba4d1dc754b817", issue_status_code="D", event_status="executed",
             exright_date="2025-10-03", public_date="2025-09-30", total_value="3.5338458E11", issue_volumn="35338458")
PAN_P = dict(DSC_P1, id="6708f3f60ec61045ab800500", ticker="PAN", public_date="2022-06-06", exercise_ratio="0.5")
ADG_P = dict(DSC_P1, id="6708f3f70ec61045ab80079c", ticker="ADG", public_date="2022-06-27", exercise_ratio="0.352")


def inner_b(R, B):
    pd = {"SpaceX": {"DSC": 1000, "PAN": 1000, "ADG": 1000, "SCL": 14000}}
    ck("DSC: D đã GDKHQ cùng tỉ lệ ⇒ 2 dòng P xác sống KHÔNG báo", B("2025-10-14", pd, [DSC_P1, DSC_P2, DSC_D], set(), is_hol) == [])
    ck("DSC: is_zombie_p đúng 2 dòng P, không phải dòng D",
       [R.is_zombie_p(x, [DSC_P1, DSC_P2, DSC_D], "2025-10-14") for x in (DSC_P1, DSC_P2, DSC_D)] == [True, True, False])
    ck("DSC: D CHƯA tới GDKHQ ⇒ dòng P chưa bị coi là xác sống (đúng đặc tả ≤ asof)",
       not R.is_zombie_p(DSC_P2, [DSC_P2, DSC_D], "2025-10-01"))
    ck("DSC: khác tỉ lệ ⇒ không phải xác sống", not R.is_zombie_p(dict(DSC_P2, exercise_ratio="0.3"), [DSC_P2, DSC_D], "2025-10-14"))
    ck("P công bố SAU GDKHQ của D (đợt mới cùng tỉ lệ) ⇒ KHÔNG xác sống",
       not R.is_zombie_p(dict(DSC_P2, public_date="2025-10-20"), [DSC_D], "2025-10-30"))
    st = B("2026-10-22", pd, [PAN_P, ADG_P], set(), is_hol)
    ck("PAN/ADG 2022 ⇒ đúng 1 tin STALE gộp, không ANNOUNCE", len(st) == 1 and st[0]["stage"] == "STALE", st)
    tx = st[0]["text"] if st else ""
    ck("tin STALE nói 'nghi BỎ DỞ' + kiểm VSDC + ngày công bố 2022", all(x in tx for x in ("BỎ DỞ", "VSDC", "2022-06-06", "2022-06-27")), tx)
    ck("STALE dedupe sau khi gửi", B("2026-10-23", pd, [PAN_P, ADG_P], set(st[0]["keys"]), is_hol) == [])
    pa = B("2022-06-10", pd, [PAN_P], set(), is_hol)
    ck("hồi cứu 2022-06-10: PAN còn mới ⇒ ANNOUNCE có public_date", len(pa) == 1 and pa[0]["stage"] == "ANNOUNCE"
       and "công bố 2022-06-06" in pa[0]["text"], pa)
    sc = B("2026-10-22", pd, [SCL25, SCL26], set(), is_hol)
    ck("SCL 2026: D 2025 khác tỉ lệ + P mới ⇒ VẪN đúng 1 ANNOUNCE", len(sc) == 1 and sc[0]["stage"] == "ANNOUNCE"
       and "công bố 2026-09-08" in sc[0]["text"] and "2,153 cp" in sc[0]["text"], sc)
    tt = B("2025-10-10", POS, [SCL25], set(), is_hol)[0]["text"]
    ck("B4: không còn 'Luật 21/10' (máy KHÔNG áp luật)", "Luật 21/10" not in tt, tt)
    ck("B4: nói rõ bot CHƯA giữ lệnh thoát + HOLD TAY + 'nếu là mã LAG'",
       all(x in tt for x in ("CHƯA tự giữ lệnh thoát", "HOLD TAY", "nếu là mã LAG")), tt)
    # B2
    ml = {"SpaceX": {"file": "active_nav_SpaceX.json", "computed_at": "2026-10-20"},
          "ZaloPay": {"file": "active_nav_ZaloPay.json", "computed_at": "2026-10-21"}}
    notes = R.position_health("2026-10-22", ml, ["SpaceX", "ZaloPay"], is_hol)
    ck("tươi: SpaceX 10-20 < phiên trước 10-21 ⇒ cũ; ZaloPay 10-21 ⇒ tươi", ml["SpaceX"]["stale"] and not ml["ZaloPay"]["stale"]
       and len(notes) == 1, notes)
    ck("thiếu account live ⇒ có lý do", any("thiếu" in x and "ZaloPay" in x for x in R.position_health("2026-10-22", {"SpaceX": dict(ml["SpaceX"], computed_at="2026-10-21")}, ["SpaceX", "ZaloPay"], is_hol)))
    ck("labels None ⇒ có lý do", any("danh sách account live" in x for x in R.position_health("2026-10-22", {}, None, is_hol)))
    ck("phiên trước bỏ qua cuối tuần/lễ (T2 10-13-2025 ⇒ T6 10-10)", R.prev_session("2025-10-13", is_hol) == "2025-10-10")
    ml2 = {"SpaceX": {"file": "active_nav_SpaceX.json", "computed_at": "2025-10-01", "stale": True}}
    tm = B("2025-10-10", POS, [SCL25], set(), is_hol, ml2, ["SpaceX: computed_at=2025-10-01 cũ"])[0]["text"]
    ck("tin có computed_at + nguồn + 'VỊ THẾ CÓ THỂ CŨ — tự kiểm trên DNSE'",
       all(x in tm for x in ("computed_at=2025-10-01", "active_nav_SpaceX.json", "VỊ THẾ CÓ THỂ CŨ — tự kiểm trên DNSE")), tm)


# ---- N1: main() end-to-end trong tmpdir (notify/state/nav đều trỏ vào tmp)
NOTIFY_SH = """#!/bin/bash
D="$(dirname "$0")"; n=$(cat "$D/count" 2>/dev/null || echo 0); n=$((n+1)); echo $n > "$D/count"
[ "$n" = "${MIKE_TEST_FAIL_AT:-0}" ] && { echo "stub fail $n" >&2; exit 7; }
printf '%s\n----\n' "$1" >> "$D/log"
"""


def inner_main(R):
    HPG = dict(SCL25, id="hpgtest0001", ticker="HPG", public_date="2025-10-09")
    td = tempfile.mkdtemp()
    try:
        nav = os.path.join(td, "nav")
        os.makedirs(nav)

        def wnav(acct, qty, ca):
            with open(os.path.join(nav, f"active_nav_{acct}.json"), "w") as fh:
                json.dump({"account": acct, "computed_at": ca,
                           "positions": [{"ticker": t, "qty": q} for t, q in qty.items()]}, fh)
        wnav("SpaceX", {"SCL": 14000, "HPG": 1000}, "2025-10-09")
        wnav("ZaloPay", {"FPT": 50}, "2025-10-09")
        sh = os.path.join(td, "notify.sh")
        open(sh, "w").write(NOTIFY_SH)
        os.chmod(sh, 0o755)
        state = os.path.join(td, "state.json")
        R.fetch_rights = lambda tk: [HPG, SCL25]
        R.live_labels = lambda: ["SpaceX", "ZaloPay"]

        def run(fail_at=0, extra=(), reset=True, st=state):
            if reset:
                for f in ("count", "log"):
                    if os.path.exists(os.path.join(td, f)):
                        os.remove(os.path.join(td, f))
            os.environ["MIKE_RIGHTS_ALERT_NOTIFY"] = f"bash {sh}"
            os.environ["MIKE_TEST_FAIL_AT"] = str(fail_at)
            sys.argv = ["x", "--asof", "2025-10-10", "--send", "--state", st, "--nav-glob", os.path.join(nav, "active_nav_*.json"), *extra]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = R.main()
            cnt = int(open(os.path.join(td, "count")).read()) if os.path.exists(os.path.join(td, "count")) else 0
            log = open(os.path.join(td, "log")).read() if os.path.exists(os.path.join(td, "log")) else ""
            return rc, buf.getvalue(), cnt, log

        rc, out, cnt, log = run(fail_at=1)
        ck("main: gửi lỗi tin đầu ⇒ rc=1, KHÔNG ghi state", rc == 1 and not os.path.exists(state) and "CHƯA ghi state" in out, (rc, out))
        rc, out, cnt, log = run(fail_at=2)
        keys = set(json.load(open(state))["sent"]) if os.path.exists(state) else set()
        ck("main: gửi lỗi GIỮA vòng ⇒ rc=1, state chỉ chứa tin đã gửi (HPG)", rc == 1 and keys == {"hpgtest0001|announce", "hpgtest0001|dated|2025-10-17"}, (rc, keys))
        rc, out, cnt, log = run()
        keys = set(json.load(open(state))["sent"])
        ck("main: chạy lại sau lỗi ⇒ chỉ gửi tin còn thiếu (SCL), rc=0, state đủ", rc == 0 and cnt == 1 and "**SCL**" in log
           and f"{SCL25['id']}|announce" in keys, (rc, cnt, keys))
        rc, out, cnt, log = run()
        ck("main: idempotent lần 2 ⇒ 0 lần gửi, rc=0", rc == 0 and cnt == 0, (rc, cnt))
        rc, out, cnt, log = run(st=os.path.join(td, "fresh_state.json"))
        ck("main: vị thế tươi + đủ account ⇒ rc=0; tin nêu computed_at nguồn", rc == 0 and cnt == 2 and "computed_at=2025-10-09" in log, (rc, cnt))
        wnav("SpaceX", {"SCL": 14000, "HPG": 1000}, "2025-10-01")
        rc, out, cnt, log = run(st=os.path.join(td, "stale_state.json"))
        ck("main: file vị thế CŨ ⇒ VẪN gửi nhưng rc=3 + 'VỊ THẾ CÓ THỂ CŨ'", rc == 3 and cnt == 2 and "VỊ THẾ CÓ THỂ CŨ" in log, (rc, cnt, out))
        wnav("SpaceX", {"SCL": 14000, "HPG": 1000}, "2025-10-09")
        os.remove(os.path.join(nav, "active_nav_ZaloPay.json"))
        rc, out, cnt, log = run(st=os.path.join(td, "miss_state.json"))
        ck("main: thiếu file account live (ZaloPay) ⇒ rc=3 + nêu thiếu", rc == 3 and "thiếu file vị thế account live: ZaloPay" in out, (rc, out))
        def boom():
            raise RuntimeError("accounts.json hỏng")
        R.live_labels = boom
        wnav("ZaloPay", {"FPT": 50}, "2025-10-09")
        rc, out, cnt, log = run(st=os.path.join(td, "boom_state.json"))
        ck("main: live_dnse_labels lỗi ⇒ rc=3 + in lỗi thật (§29)", rc == 3 and "accounts.json hỏng" in out, (rc, out))
        for f in os.listdir(nav):
            os.remove(os.path.join(nav, f))
        rc, out, cnt, log = run(st=os.path.join(td, "none_state.json"))
        ck("main: không có file vị thế nào ⇒ rc=2, không gửi gì", rc == 2 and cnt == 0, (rc, cnt))
    finally:
        shutil.rmtree(td, ignore_errors=True)


MUTANTS = [
    ('        if (r.get("public_date") or "")[:10] > asof:', '        if False:'),
    ('        if ex and ex <= asof:\n            continue', '        if ex and ex < asof:\n            continue'),
    ("            if left <= REMIND_SESSIONS:", "            if left < REMIND_SESSIONS:"),
    ('        stages = [("ANNOUNCE", f"{r[\'id\']}|announce")]', "        stages = []"),
    ('            stages.append(("DATED", f"{r[\'id\']}|dated|{ex}"))', '            stages.append(("DATED", f"{r[\'id\']}|dated"))'),
    ('f"{r[\'id\']}|remind|{ex}|{asof}"', 'f"{r[\'id\']}|remind|{ex}"'),
    ("            n = math.floor(q * ratio + 1e-9)", "            n = round(q * ratio)"),
    ('        if d.weekday() < 5 and not is_holiday(d):\n            n += 1', '        if d.weekday() < 5:\n            n += 1'),
    ('or r.get("issue_status_code") == "N" \\', 'or False \\'),
    ("        return tv / vol if tv > 0 and vol > 0 else None", "        return None"),
    ("ex <= asof and ex > pub and _same_ratio(o, r):", "ex <= asof and ex > pub:"),
    ("ex <= asof and ex > pub and _same_ratio(o, r):", "ex <= asof and _same_ratio(o, r):"),
    ("    return (dt.date.fromisoformat(asof) - dt.date.fromisoformat(pub)).days > STALE_P_DAYS",
     "    return (dt.date.fromisoformat(asof) - dt.date.fromisoformat(pub)).days > 10 ** 6"),
    ("        if is_zombie_p(r, rows, asof):", "        if False:"),
    ('        m["stale"] = (m.get("computed_at") or "")[:10] < cutoff', '        m["stale"] = False'),
    ("    elif [lb for lb in labels if lb not in meta]:", "    elif False:"),
    ("    stale_rc = 3 if notes else 0", "    stale_rc = 0"),
    ("        return 2\n    try:", "        return 0\n    try:"),
    ("        if r.returncode != 0:", "        if False:"),
    ('        r = subprocess.run(notify + [al["text"], TRADING_DAILY_THREAD], capture_output=True, text=True)',
     '        _save_sent(a.state, sent | set(al["keys"]))\n        r = subprocess.run(notify + [al["text"], TRADING_DAILY_THREAD], capture_output=True, text=True)'),
    ("        _save_sent(a.state, sent)              # ghi NGAY sau mỗi lần gửi (§5)", "        pass"),
    ("    sent = _load_sent(a.state) if a.send else set()", "    sent = set()"),
    ("        labels = None\n", "        labels = []\n"),
    ("        holders = [(lb, p[tk]) for lb, p in sorted(positions.items()) if p.get(tk, 0) > 0]",
     "        holders = [(lb, p.get(tk, 0)) for lb, p in sorted(positions.items())]"),
]


def run_mutants():
    bad = 0
    for i, (old, new) in enumerate(MUTANTS, 1):
        td = tempfile.mkdtemp()
        try:
            shutil.copy(os.path.join(HERE, "rights_issue_alert.py"), td)
            shutil.copy(os.path.abspath(__file__), td)
            p = os.path.join(td, "rights_issue_alert.py")
            src = open(p).read()
            if src.count(old) != 1:
                print(f"  ❌ mutant {i}: chuỗi gốc không khớp đúng 1 lần — sửa MUTANTS")
                bad += 1
                continue
            open(p, "w").write(src.replace(old, new))
            r = subprocess.run([sys.executable, os.path.join(td, os.path.basename(__file__)), "--inner"],
                               capture_output=True, text=True, timeout=120)
            killed = r.returncode != 0
            print(f"  {'KILLED' if killed else 'SURVIVED'} — mutant {i}: {old.strip()[:70]!r}")
            bad += 0 if killed else 1
        finally:
            shutil.rmtree(td, ignore_errors=True)
    print(f"MUTANTS: {len(MUTANTS) - bad}/{len(MUTANTS)} killed")
    return bad


def main():
    if "--inner" in sys.argv:
        sys.path.insert(0, HERE)
        return run_inner()
    rc = 0
    for label, env in (("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                       ("TZ=Pacific/Kiritimati", dict(os.environ, TZ="Pacific/Kiritimati")),
                       ("TZ=America/New_York", dict(os.environ, TZ="America/New_York"))):
        print(f"=== {label} ===")
        env["MIKE_BOT_TEST_MODE"] = "1"
        rc |= subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env).returncode
    print("=== mutants ===")
    if run_mutants():
        rc |= 1
    print("TỔNG:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
