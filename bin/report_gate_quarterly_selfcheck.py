#!/usr/bin/env python3
"""Selfcheck: các cổng giao báo cáo phải NHẬN tên báo cáo QUÝ (*_quarterly_report_YYYY-Qn.md).

Vòng 2 arch-review (02/11/2026): _extract_report_date / accounts_asof_from_name không parse YYYY-Qn ⇒ return-gate
ValueError, delivery gate None ⇒ nav-flow BLOCK còn §31 bị WARN-skip IM LẶNG. Selfcheck này chạy CHUỖI VALIDATION
thật (period-return §31, benchmark/livermore skip, nav-flow, return-gate CLI) trên fixture tên quý, rồi MUTATION.
  env -u TZ python3 bin/report_gate_quarterly_selfcheck.py ; TZ=America/Los_Angeles python3 ...
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))
DG = BIN / "report_delivery_gate.py"
RG = BIN / "report_return_gate.py"


def load(path, text):
    ns = {"__file__": str(path), "__name__": "gate_under_test"}
    exec(compile(text, str(path), "exec"), ns)
    return ns


def suite(dg_text, rg_text, full=False):
    res = []
    def chk(n, c, d=""): res.append((n, bool(c), d))
    dg, rg = load(DG, dg_text), load(RG, rg_text)
    Path_ = dg["Path"]
    ext = dg["_extract_report_date"]
    for name, exp in (("SpaceX_quarterly_report_2026-Q4.md", "2026-12-31"), ("ZaloPay_quarterly_report_2027-Q1.md", "2027-03-31"),
                      ("SpaceX_quarterly_report_2026-Q3.md", "2026-09-30"), ("SpaceX_quarterly_report_2028-Q2.md", "2028-06-30"),
                      ("SpaceX_monthly_report_2026-02.md", "2026-02-28"),
                      ("SpaceX_weekly_report_2026-10-26_to_2026-10-30.md", "2026-10-30")):
        chk(f"1 _extract_report_date({name}) = {exp}", ext(name) == exp, str(ext(name)))
    chk("1b quý lạ Q5 ⇒ None", ext("SpaceX_quarterly_report_2026-Q5.md") is None)
    chk("2 _CADENCE_RE KHÔNG khớp quý (quyết định có chủ đích)", dg["_CADENCE_RE"].match("SpaceX_quarterly_report_2026-Q4.md") is None)
    chk("2b _QUARTERLY_RE khớp quý", dg["_QUARTERLY_RE"].match("ZaloPay_quarterly_report_2026-Q4.md") is not None)

    # return gate: tên quý → (nhãn, ngày chốt ≤ cuối quý, trong quý)
    try:
        labels, asof = rg["accounts_asof_from_name"]("/x/SpaceX_quarterly_report_2026-Q3.md")
    except ValueError as e:
        labels, asof = [], str(e)
    chk("3 accounts_asof_from_name quý Q3 ⇒ SpaceX, ngày trong 2026-07-01..09-30",
        labels == ["SpaceX"] and "2026-07-01" <= asof <= "2026-09-30", f"{labels} {asof}")
    try:
        rg["accounts_asof_from_name"]("/x/SpaceX_quarterly_report_2999-Q1.md"); chk("3b quý không có log ⇒ ValueError", False)
    except ValueError:
        chk("3b quý không có log ⇒ ValueError (fail-closed)", True)

    with tempfile.TemporaryDirectory() as td:
        # SpaceX Q3: số canonical từ CLI thật, rồi thử ĐÚNG và SAI
        proc = subprocess.run([sys.executable, str(BIN / "nav_period_returns.py"), "--account", "SpaceX", "--report-date", "2026-09-30"],
                              capture_output=True, text=True)
        import json
        canon = json.loads(proc.stdout)["inception"]["return_pct"]
        def fx(cell, name="SpaceX_quarterly_report_2026-Q3.md"):
            p = Path_(td) / name
            p.write_text(f"# Báo cáo quý\n\n### 3.2 Hiệu suất lũy kế\n\n| Giai đoạn | SpaceX |\n|---|---|\n| Từ khi bắt đầu hoạt động | {cell} |\n", encoding="utf-8")
            return p
        def run(fn, p):
            out, err = io.StringIO(), io.StringIO()
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    fn(p)
                return "OK", out.getvalue() + err.getvalue()
            except Exception as e:                       # noqa: BLE001
                return "RAISE", f"{type(e).__name__}: {e}"
        good = f"{canon:+.2f}%".replace(".", ",").replace("-", "−")
        bad = f"{canon - 3:+.2f}%".replace(".", ",").replace("-", "−")
        st, msg = run(dg["_check_period_returns"], fx(good))
        chk("4 §31 quý SpaceX số ĐÚNG ⇒ PASS thật (không WARN-skip)", st == "OK" and "period-return PASS" in msg and "WARN" not in msg, msg[:200])
        st, msg = run(dg["_check_period_returns"], fx(bad))
        chk("4b §31 quý SpaceX số SAI ⇒ BLOCK", st == "RAISE" and "period-return BLOCK" in msg, msg[:200])
        st, msg = run(dg["_check_benchmark_table"], fx(good))
        chk("5 benchmark-table quý ⇒ SKIP có chủ đích IN RA (không im lặng)", st == "OK" and "SKIP có chủ đích" in msg, msg[:200])
        st, msg = run(dg["_check_livermore_block"], fx(good))
        chk("5b livermore quý ⇒ SKIP có chủ đích IN RA", st == "OK" and "SKIP có chủ đích" in msg, msg[:200])
        st, msg = run(dg["_check_benchmark_table"], fx(good, "SpaceX_monthly_report_2026-09.md"))
        chk("5c monthly KHÔNG bị skip (cổng vẫn áp)", "SKIP có chủ đích" not in msg, msg[:200])
        # return-gate CLI trên tên quý: không được ValueError (rc=1 + 'không suy được ngày chốt')
        if full:                    # ~100s (BQ/đối soát sổ) — chỉ chạy ở BASE, mutation dựa vào ca 3/3b
            r = subprocess.run([sys.executable, str(RG), "--report", str(fx(good))], capture_output=True, text=True, timeout=600)
            chk("6 report_return_gate CLI nhận tên quý: rc=0 + PASS",
                r.returncode == 0 and "PASS" in r.stdout and "ValueError" not in r.stderr, f"rc={r.returncode} " + (r.stdout + r.stderr)[-300:])
        # nav-flow: ngày chốt suy được (không còn 'không suy được report-date')
        st, msg = run(dg["_check_nav_flow_records"], fx(good))
        chk("7 nav-flow quý ⇒ không 'không suy được report-date'", "không suy được report-date" not in msg, msg[:200])
    return res


def main():
    dgt, rgt = DG.read_text(encoding="utf-8"), RG.read_text(encoding="utf-8")
    print(f"selfcheck report gates quarterly — TZ={os.environ.get('TZ')!r}")
    res = suite(dgt, rgt, full=True)
    bad = [r for r in res if not r[1]]
    for n, ok, d in bad: print(f"  ❌ {n} — {d}")
    print(f"BASE: {len(res) - len(bad)}/{len(res)} PASS")
    MUT = [
        ("M1 _extract_report_date bỏ nhánh quý", "dg", 'if q and not full_dates:', 'if False:'),
        ("M2 accounts_asof_from_name bỏ nhánh quý", "rg", '    if qm:  ', '    if False:  '),
        ("M3 _quarterly_skip im lặng", "dg", '        print(f"report_delivery_gate: {gate} SKIP có chủ đích', '        (lambda *a, **k: None)(f"report_delivery_gate: {gate} SKIP có chủ đích'),
        ("M4 _CADENCE_RE gồm quarterly", "dg", '(weekly|monthly)_report_")\n# QUÝ', '(weekly|monthly|quarterly)_report_")\n# QUÝ'),
        ("M5 quý Q → tháng sai (qn*3 → qn*3-1)", "dg", 'calendar.monthrange(year, qn * 3)[1]', 'calendar.monthrange(year, qn * 3 - 1)[1]'),
    ]
    caught = 0
    for name, which, old, new in MUT:
        src = dgt if which == "dg" else rgt
        if src.count(old) != 1:
            print(f"  ❌ mutation không áp được ({src.count(old)}): {name}"); bad.append((name, False, "mut")); continue
        mres = suite(src.replace(old, new) if which == "dg" else dgt, src.replace(old, new) if which == "rg" else rgt)
        mb = [r for r in mres if not r[1]]
        print(f"  {'✅ bắt được' if mb else '❌ KHÔNG bắt được'}: {name} ({len(mb)} ca đỏ)")
        caught += bool(mb)
        if not mb: bad.append((name, False, "sống sót"))
    print(f"MUTATION: {caught}/{len(MUT)} bị bắt")
    print("KẾT QUẢ:", "PASS" if not bad else f"FAIL ({len(bad)})")
    sys.exit(1 if bad else 0)


main()
