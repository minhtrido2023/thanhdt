#!/usr/bin/env python3
"""Selfcheck oshares_dcf + knob DCF_OSHARES_SOURCE của dcf_valuation (job Taylor_20261030_094435).

  python3 oshares_dcf_selfcheck.py          # offline (fixture từ dòng corporate_action thật 30/10)
  python3 oshares_dcf_selfcheck.py --bq     # + đối chiếu BQ thật TCB/NED/DGC/TV1/KSV/HUB

Sau bộ check chính, chạy MUTATION: mỗi mutant phải làm ≥1 check FAIL, không thì bộ check mù.
Chạy được ở TZ=UTC và env -u TZ (không đọc giờ hệ thống: mọi ngày đều truyền tường minh).
"""
import contextlib
import io
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oshares_dcf as osd           # noqa: E402

SD, BON, RIGHTS = "Trả Cổ tức bằng Cổ phiếu", "Cổ phiếu thưởng", "Quyền mua CP cho Cổ đông hiện hữu"


def iss(ex, ratio, meth=SD, pub=None, status="executed"):
    return {"event_code": "ISS", "exright_date": ex, "exercise_ratio": ratio,
            "issue_method_name_vi": meth, "public_date": pub or ex, "event_status": status}


def div(ex, ratio):
    return {"event_code": "DIV", "exright_date": ex, "exercise_ratio": ratio, "public_date": ex}


# dòng corporate_action thật (truy vấn 2026-10-30), cửa sổ (2026-06-30, 2026-10-29]
FIX = {
    "TCB": (1.0, [iss("2026-10-29", 0.5, pub="2026-10-23", status="announced")], 0.6666, "OSHARES_LAG"),
    "NED": (1.0, [iss("2026-10-29", 0.14, pub="2026-10-23", status="announced")], 0.8769, "OSHARES_LAG"),
    "DGC": (1.0, [div("2026-09-14", 0.3), div("2026-09-14", 0.5)], 0.8289, "CASH_DIV"),
    "TV1": (1.0, [div("2026-10-07", 0.15)], 0.9278, "CASH_DIV"),
    "KSV": (1.5, [div("2026-07-14", 0.405), iss("2026-07-14", 0.5), div("2026-10-23", 0.3)], 0.6326,
            "ISS_REFLECTED"),
    "HUB": (1.05, [div("2026-09-09", 0.1), iss("2026-09-09", 0.05)], 0.8814, "ISS_REFLECTED"),
}

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))


def c1_classifier():
    for tk, (osr, ev, adj, want) in FIX.items():
        v, d = osd.classify_oshares_gap(osr, ev, adj)
        check(f"C1 {tk} -> {want}", v == want, f"got {v} {d.get('expected_ratio')}")
    check("C1 chỉ quyền mua -> RIGHTS_PENDING",
          osd.classify_oshares_gap(1.0, [iss("2026-08-01", 0.5, RIGHTS)], 0.8)[0] == "RIGHTS_PENDING")
    check("C1 thưởng CP tính như cổ tức CP",
          osd.classify_oshares_gap(1.0, [iss("2026-08-01", 0.2, BON)], 0.83)[0] == "OSHARES_LAG")
    check("C1 không sự kiện, giá điều chỉnh -> UNEXPLAINED_PRICE_ADJ",
          osd.classify_oshares_gap(1.0, [], 0.85)[0] == "UNEXPLAINED_PRICE_ADJ")
    check("C1 không sự kiện, giá phẳng -> NO_EVENT", osd.classify_oshares_gap(1.0, [], 0.99)[0] == "NO_EVENT")
    v, d = osd.classify_oshares_gap(1.5, [iss("2026-07-14", 0.5), iss("2026-07-14", 0.5)], 0.66)
    check("C1 dòng ISS trùng (revision) chỉ đếm 1 lần", v == "ISS_REFLECTED" and abs(d["expected_ratio"] - 1.5) < 1e-12,
          f"{v} {d.get('expected_ratio')}")
    v, d = osd.classify_oshares_gap(1.5 * 1.15, [iss("2026-08-11", 0.5), iss("2026-08-11", 0.15, BON)], 0.6)
    check("C1 hai đợt khác phương thức cùng ngày đều đếm", v == "ISS_REFLECTED" and abs(d["expected_ratio"] - 1.725) < 1e-12)
    check("C1 ISS không ratio -> ISS_UNSIZED", osd.classify_oshares_gap(1.0, [iss("2026-08-01", None)])[0] == "ISS_UNSIZED")
    check("C1 biên: đúng 95% kỳ vọng -> REFLECTED",
          osd.classify_oshares_gap(0.95 * 1.5, [iss("2026-08-01", 0.5)])[0] == "ISS_REFLECTED")
    check("C1 biên: dưới 95% kỳ vọng -> LAG",
          osd.classify_oshares_gap(0.949 * 1.5, [iss("2026-08-01", 0.5)])[0] == "OSHARES_LAG")


ANN = dict(ticker="TCB", event_code="ISS", exright_date="2026-10-29", effective_date=None, listing_date=None,
           exercise_ratio=0.5, issue_volumn=0, issue_method_name_vi=SD, shares_delta=None,
           shares_total_after=None, title="fixture", public_date="2026-10-23")
Q = [dict(ticker="TCB", time="2026-07-28", OShares=7086240414.0)]
AIS = [dict(ticker="TCB", event_code="AIS", exright_date=None, effective_date="2026-08-05", listing_date=None,
            exercise_ratio=None, issue_volumn=None, issue_method_name_vi=None, shares_delta=21388675,
            shares_total_after=7086240414, title="fixture")]


def c2_clip():
    def added(asof, ann=None, corp=None):
        return [a["exright_date"] for a in osd._clip((Q, corp or AIS, [ann or ANN]), asof)[2]]
    check("C2 ex<=asof & public<=asof -> thêm", added("2026-10-30") == ["2026-10-29"])
    check("C2 ex>asof -> không thêm (PIT)", added("2026-10-28") == [])
    check("C2 public_date>asof -> không thêm (PIT)", added("2026-10-30", {**ANN, "public_date": "2026-10-31"}) == [])
    check("C2 ex quá 45 ngày -> không thêm (dòng mồ côi)", added("2026-12-14") == [])
    check("C2 ex đúng 45 ngày -> còn thêm", added("2026-12-13") == ["2026-10-29"])
    dup = {**ANN, "event_status": "executed"}
    check("C2 trùng một ISS executed -> không thêm", added("2026-10-30", corp=AIS + [dup]) == [])


def _prime_fixture(ann):
    osd._CACHE.update(tickers=frozenset({"TCB"}), until="2026-12-31", data=(Q, AIS, ann))


def c3_oshares_for():
    _prime_fixture([ANN])
    r = osd.oshares_for("TCB", "2026-10-30", 7086240414.0)
    check("C3 TCB 30/10: AIS 7.086.240.414 × 1,5 (ISS announced đã ex)",
          r["value"] is not None and abs(r["value"] - 7086240414 * 1.5) < 1, f"{r['value']} {r['method']} {r['source']}")
    check("C3 TCB 30/10 nguồn oshares_live + ghi announced_added",
          r["source"] == "oshares_live" and r["announced_added"] == ["2026-10-29"])
    r = osd.oshares_for("TCB", "2026-10-28", 7086240414.0)
    check("C3 TCB 28/10 (trước ex) = số AIS", r["value"] == 7086240414.0, f"{r['value']}")
    _prime_fixture([])
    r = osd.oshares_for("TCB", "2026-10-30", 7086240414.0)
    check("C3 không ISS -> số không đổi (ca DGC/TV1)", r["value"] == 7086240414.0, f"{r['value']}")
    osd._CACHE.update(tickers=frozenset(), until=None, data=None)
    real = osd.fetch_cache
    osd.fetch_cache = lambda t, u: None
    try:
        r = osd.oshares_for("TCB", "2026-10-30", 123.0)
    finally:
        osd.fetch_cache = real
    check("C3 lỗi nguồn -> số quý, method ERROR", r["value"] == 123.0 and r["method"] == "ERROR"
          and r["source"] == "ticker_financial")


def _subproc(code, env_extra=None, unset=()):
    env = {k: v for k, v in os.environ.items() if k not in unset}
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, timeout=600)
    return p.stdout.strip().splitlines()[-1] if p.stdout.strip() else f"ERR {p.stderr[-300:]}"


PROBE = ("import sys; sys.path.insert(0, %r); import dcf_valuation as d; "
         "r = d.fair_value('FPT', '2026-10-29', price=100000.0); "
         "print(d.OSHARES_SOURCE, 'oshares_dcf' in sys.modules, sorted(k for k in r if k.startswith('oshares_')))") % HERE


def c4_knob():
    out = _subproc(PROBE, unset=("DCF_OSHARES_SOURCE",))
    check("C4 env trống -> 'fin', không import oshares_dcf, không thêm khoá", out == "fin False []", out)
    out = _subproc(PROBE, {"DCF_OSHARES_SOURCE": "bogus"})
    check("C4 giá trị lạ -> 'fin' (hành vi cũ)", out == "fin False []", out)
    out = _subproc(PROBE, {"DCF_OSHARES_SOURCE": "live"})
    check("C4 env=live -> 'live', có khoá oshares_*", out.startswith("live True") and "oshares_source" in out, out)

    import dcf_valuation as dv
    fin = dv._load_financials()
    real = osd.oshares_for
    calls = []
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        dv.OSHARES_SOURCE = "live"
        osd.oshares_for = lambda t, a, f: (calls.append(f) or {"value": 2 * f, "source": "oshares_live",
                                                               "method": "X", "announced_added": []})
        dbl = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        check("C4 live: số CP ×2 -> FV/cp ÷2 đúng", math.isclose(dbl["fair_value_ps"] * 2, base["fair_value_ps"],
                                                              rel_tol=1e-12), f"{base['fair_value_ps']} {dbl['fair_value_ps']}")
        check("C4 live: ghi oshares_fin/source", dbl.get("oshares_fin") == base["oshares"]
              and dbl.get("oshares_source") == "oshares_live")
        osd.oshares_for = lambda t, a, f: {"value": None, "source": "none", "method": "NO_ANCHOR", "announced_added": []}
        nn = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        check("C4 live: oshares_for trả None -> dùng số quý", nn["fair_value_ps"] == base["fair_value_ps"])
        calls.clear()
        dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, oshares=5e8)
        check("C4 live: caller truyền oshares= thì không gọi oshares_for", calls == [])
        f2 = fin.copy()
        f2.loc[f2.ticker == "FPT", "OShares"] = float("nan")
        calls.clear()
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=f2)
        check("C4 live: thiếu OShares quý -> vẫn 'OShares missing', không gọi live",
              r["reason"] == "OShares missing" and calls == [], f"{r['reason']} {calls}")
        # R1 (arch-review 30/10): chẩn đoán KHÔNG được ra STDOUT (send_plan_report lấy dòng đầu stdout làm STATUS)
        def _noisy(t, a, f):
            print("[oshares_pit] ẩn dụ: lỗi nguồn in ra stdout")
            return {"value": None, "source": "none", "method": "ERROR", "announced_added": []}
        osd.oshares_for = _noisy
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        check("C4 live: oshares_for in ra stdout -> stdout của fair_value vẫn rỗng", buf.getvalue() == "", buf.getvalue()[:80])
        osd.oshares_for = real
        osd._CACHE.update(tickers=frozenset(), until=None, data=None)
        import oshares_live as _ol
        real_fetch = _ol._fetch
        def _boom(*a, **k):
            raise RuntimeError("bq down (simulated)")
        _ol._fetch = _boom
        buf, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        finally:
            _ol._fetch = real_fetch
            osd._CACHE.update(tickers=frozenset(), until=None, data=None)
        check("C4 live + BQ lỗi: stdout rỗng, chẩn đoán ở stderr", buf.getvalue() == "" and "fetch_cache FAILED" in err.getvalue(),
              f"stdout={buf.getvalue()[:60]!r} stderr={err.getvalue()[:60]!r}")
    finally:
        osd.oshares_for = real
        dv.OSHARES_SOURCE = "fin"


def c5_bq():
    import pandas as pd
    fr = pd.DataFrame([dict(ticker=t, Close_d0=a, Price_d0=1.0, OShares_d0=1.0, OShares_d1=o)
                       for t, (o, _e, a, _w) in FIX.items()])
    res = osd.oshares_gap_check(fr, "2026-06-30", "2026-10-29")
    for t, (_o, _e, _a, want) in FIX.items():
        check(f"C5 BQ {t} -> {want}", res[t][0] == want, res[t][0])
    osd.prime(["TCB", "DGC"], "2026-10-30")
    r = osd.oshares_for("TCB", "2026-10-30", 7086240414.0)
    check("C5 BQ TCB oshares_for ≈ ×1,5", r["value"] and abs(r["value"] / 7086240414.0 - 1.5) < 1e-6, f"{r['value']}")


SUITE = [c1_classifier, c2_clip, c3_oshares_for, c4_knob]


def run_suite(with_bq=False, quiet=False):
    FAILS.clear()
    sink = io.StringIO() if quiet else sys.stdout
    with contextlib.redirect_stdout(sink):
        for f in SUITE + ([c5_bq] if with_bq else []):
            print(f"[{f.__name__}]")
            f()
    return list(FAILS)


def _mut_div_as_share(evs):
    return [{**e, "event_code": "ISS", "issue_method_name_vi": SD} if e.get("event_code") == "DIV" else e for e in evs]


import dcf_valuation as dv     # noqa: E402 — mutant M7 vá module này
MUTANTS = {
    "M1 DIV coi như ISS cổ phiếu (lỗi quy tắc cũ)": (osd, "_dedup", lambda real: lambda ev: real(_mut_div_as_share(ev))),
    "M2 quyền mua tính là tạo CP": (osd, "SHARE_CREATING_ISS", lambda real: real | {RIGHTS}),
    "M3 bỏ dedup": (osd, "_dedup", lambda real: lambda ev: list(ev)),
    "M4 LAG_TOL = 0": (osd, "LAG_TOL", lambda real: 0.0),
    "M7 bỏ redirect stdout quanh oshares_for (dcf_valuation)": (dv, "contextlib", lambda real: type("NoRedirect", (), {"redirect_stdout": staticmethod(lambda f: real.nullcontext())})),
    "M5 bỏ trần tuổi announced": (osd, "PROMOTE_MAX_AGE_DAYS", lambda real: 100000),
    "M6 bỏ lọc public_date<=asof": (osd, "_clip", lambda real: lambda c, a: real(
        (c[0], c[1], [{**x, "public_date": "0000"} for x in c[2]]), a)),
}


def run_mutants():
    # LAG_TOL là default arg ⇒ vá qua wrapper để mutant thật sự có hiệu lực
    ok = True
    for name, (mod, attr, make) in MUTANTS.items():
        real = getattr(mod, attr)
        real_cls = osd.classify_oshares_gap
        setattr(mod, attr, make(real))
        if attr == "LAG_TOL":
            osd.classify_oshares_gap = lambda r, e, a=None, tol=None: real_cls(r, e, a, tol=0.0)
        try:
            fails = run_suite(quiet=True)
        finally:
            setattr(mod, attr, real)
            osd.classify_oshares_gap = real_cls
        killed = bool(fails)
        ok &= killed
        print(f"  {'KILLED' if killed else 'SURVIVED'}  {name}" + (f" ({len(fails)} FAIL: {fails[0]})" if fails else ""))
    return ok


if __name__ == "__main__":
    fails = run_suite(with_bq="--bq" in sys.argv)
    print(f"\n== {'PASS' if not fails else 'FAIL'}: {len(fails)} FAIL" + (f" {fails}" if fails else ""))
    print("\n[mutation]")
    mut_ok = run_mutants()
    print(f"== mutation: {'mọi mutant bị giết' if mut_ok else 'CÓ MUTANT SỐNG'}")
    sys.exit(0 if not fails and mut_ok else 1)
