#!/usr/bin/env python3
"""Selfcheck rights_issue_alert.py — hàm thuần, fixture số THẬT SCL (tav2_bq.corporate_action).

Chạy chính nó dưới `env -u TZ` + 2 TZ lạ (§16/§19), rồi MUTANT — mỗi mutant PHẢI làm đỏ.
    python3 bin/rights_issue_alert_selfcheck.py
"""
import datetime as dt
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
    n = sum(1 for x in RESULTS if not x)
    print("RESULT:", "PASS" if not n else "FAIL")
    return 0 if not n else 1


MUTANTS = [
    ('        if (r.get("public_date") or "")[:10] > asof:', '        if False:'),
    ('        if ex and ex <= asof:\n            continue', '        if ex and ex < asof:\n            continue'),
    ("            if left <= REMIND_SESSIONS:", "            if left < REMIND_SESSIONS:"),
    ('        stages = [("ANNOUNCE", f"{r[\'id\']}|announce")]', "        stages = []"),
    ('            stages.append(("DATED", f"{r[\'id\']}|dated|{ex}"))', '            stages.append(("DATED", f"{r[\'id\']}|dated"))'),
    ('f"{r[\'id\']}|remind|{ex}|{asof}"', 'f"{r[\'id\']}|remind|{ex}"'),
    ("            n = math.floor(q * ratio + 1e-9)", "            n = round(q * ratio)"),
    ('        if d.weekday() < 5 and not is_holiday(d):', '        if d.weekday() < 5:'),
    ('or r.get("issue_status_code") == "N" \\', 'or False \\'),
    ("        return tv / vol if tv > 0 and vol > 0 else None", "        return None"),
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
