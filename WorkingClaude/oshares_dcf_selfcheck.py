#!/usr/bin/env python3
"""Selfcheck oshares_dcf + knob DCF_OSHARES_SOURCE của dcf_valuation (job Taylor_20261030_094435;
R2-R5 job Taylor_20261030_155013: C6 nguồn sự thật OSHARES_SOURCE_DEFAULT, C7 khoá khung ex-date,
C8 khối CHECKDCFOS của ops_health_check.sh, C9 script nghiên cứu ép fin).

  python3 oshares_dcf_selfcheck.py          # offline (fixture từ dòng corporate_action thật 30/10)
  python3 oshares_dcf_selfcheck.py --bq     # + đối chiếu BQ thật TCB/NED/DGC/TV1/KSV/HUB

Sau bộ check chính, chạy MUTATION: mỗi mutant phải làm ≥1 check FAIL, không thì bộ check mù.
Chạy được ở TZ=UTC và env -u TZ (không đọc giờ hệ thống: mọi ngày đều truyền tường minh).
"""
import contextlib
import glob
import io
import math
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oshares_dcf as osd           # noqa: E402
PROD = "/home/trido/thanhdt/WorkingClaude"
OPS = os.environ.get("DCF_OS_OPS_HEALTH", os.path.join(PROD, "mike/bin/ops_health_check.sh"))

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


Q = [dict(ticker="TCB", time="2026-07-28", OShares=7086240414.0)]
AIS = [dict(ticker="TCB", event_code="AIS", exright_date=None, effective_date="2026-08-05", listing_date=None,
            exercise_ratio=None, issue_volumn=None, issue_method_name_vi=None, shares_delta=21388675,
            shares_total_after=7086240414, title="fixture")]


def c2_no_announced_branch():
    """R4: nhánh promote `announced` đã bỏ — module không còn đọc ISS announced cho số CP."""
    src = open(osd.__file__, encoding="utf-8").read()
    code = src[src.index('"""', src.index('"""') + 3) + 3:]          # bỏ docstring module
    check("C2 không còn _fetch_announced/_clip/PROMOTE_MAX_AGE_DAYS",
          not any(k in code for k in ("_fetch_announced", "def _clip", "PROMOTE_MAX_AGE_DAYS")))
    check("C2 không truy vấn event_status=\"announced\" cho số CP", 'event_status = "announced"' not in code)


def _prime_fixture(corp):
    osd._CACHE.update(tickers=frozenset({"TCB"}), until="2026-12-31", data=(Q, corp))


def c3_oshares_for():
    from oshares_pit import oshares_pit
    _prime_fixture(AIS)
    r = osd.oshares_for("TCB", "2026-10-30", 7086240414.0)
    ref = oshares_pit(["TCB"], "2026-10-30", {"TCB": 7086240414.0}, cache=(Q, AIS))["TCB"]
    check("C3 oshares_for == oshares_pit trên cùng cache (không bổ sung gì)",
          r["value"] == ref["value"] and r["source"] == ref["source"] and r["method"] == ref["method"],
          f"{r['value']} {r['method']} vs {ref['value']} {ref['method']}")
    check("C3 không còn khoá announced_added", "announced_added" not in r)
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
    check("C4 env=live -> 'live', có khoá oshares_* (gồm oshares_frame_error)",
          out.startswith("live True") and "oshares_source" in out and "oshares_frame_error" in out, out)

    import dcf_valuation as dv
    fin = dv._load_financials()
    real = osd.oshares_for
    calls = []
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        dv.OSHARES_SOURCE = "live"
        osd.oshares_for = lambda t, a, f: (calls.append(f) or {"value": 2 * f, "source": "oshares_live",
                                                               "method": "X"})
        dbl = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-29")
        check("C4 live: số CP ×2 -> FV/cp ÷2 đúng", math.isclose(dbl["fair_value_ps"] * 2, base["fair_value_ps"],
                                                              rel_tol=1e-12), f"{base['fair_value_ps']} {dbl['fair_value_ps']}")
        check("C4 live: ghi oshares_fin/source", dbl.get("oshares_fin") == base["oshares"]
              and dbl.get("oshares_source") == "oshares_live")
        osd.oshares_for = lambda t, a, f: {"value": None, "source": "none", "method": "NO_ANCHOR"}
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
            return {"value": None, "source": "none", "method": "ERROR"}
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
    from oshares_pit import oshares_pit
    osd.prime(["TCB", "DGC"], "2026-10-30")
    r = osd.oshares_for("TCB", "2026-10-30", 7086240414.0)
    ref = oshares_pit(["TCB"], "2026-10-30", {"TCB": 7086240414.0}, cache=osd._CACHE["data"])["TCB"]
    check("C5 BQ TCB oshares_for == oshares_pit (BQ thật)", r["value"] == ref["value"], f"{r['value']} {r['method']}")
    osd._CACHE.update(tickers=frozenset(), until=None, data=None)


def c6_source_of_truth():
    import dcf_valuation as dv
    src = open(dv.__file__, encoding="utf-8").read()
    m = re.search(r'^OSHARES_SOURCE_DEFAULT\s*=\s*"([^"]*)"', src, re.M)
    check("C6 có đúng 1 dòng OSHARES_SOURCE_DEFAULT và = 'fin' (knob TẮT)",
          m is not None and m.group(1) == "fin" and len(re.findall(r"^OSHARES_SOURCE_DEFAULT\s*=", src, re.M)) == 1,
          m.group(1) if m else "none")
    R = dv._resolve_oshares_source
    check("C6 env None/rỗng -> default", R(None) == ("fin", None) and R("  ") == ("fin", None)
          and R(None, "live") == ("live", None))
    v, w = R("live")
    check("C6 env 'live' khác default -> 'live' + cảnh báo OVERRIDE", v == "live" and w and "OVERRIDE" in w, str(w))
    check("C6 env == default -> không cảnh báo", R("fin") == ("fin", None) and R(" live ", "live") == ("live", None))
    for bad in ("LIVE", "bogus", "1"):
        v, w = R(bad, "live")
        check(f"C6 env lạ {bad!r} -> 'fin' + KHONG HOP LE (kể cả khi default=live)", v == "fin" and "KHONG HOP LE" in (w or ""))
    v, w = R(None, "lvie")
    check("C6 hằng số default gõ sai -> 'fin' + kêu", v == "fin" and "OSHARES_SOURCE_DEFAULT" in (w or ""))
    p = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import dcf_valuation as d; print(d.OSHARES_SOURCE)" % HERE],
                       cwd=HERE, env={**os.environ, "DCF_OSHARES_SOURCE": "bogus"}, capture_output=True, text=True, timeout=300)
    check("C6 import với env lạ: không raise, 'fin', kêu stderr", p.returncode == 0 and p.stdout.strip().endswith("fin")
          and "KHONG HOP LE" in p.stderr, p.stderr[-120:])


class _FakeOS:
    """oshares_for giả: số CP đổi tại ex-date `ex` (×mult); ghi lại các ngày được hỏi."""
    def __init__(self, ex="2026-10-20", mult=1.5):
        self.ex, self.mult, self.asked = ex, mult, []

    def __call__(self, t, a, f):
        self.asked.append(a)
        return {"value": f * (self.mult if a >= self.ex else 1.0), "source": "oshares_live", "method": "FAKE"}


def c7_frame_lock():
    import dcf_valuation as dv
    fin = dv._load_financials()
    real = osd.oshares_for
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        fake = _FakeOS()
        osd.oshares_for = fake
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-01")
        check("C7 knob fin: price_date bị bỏ qua, byte-identical, không gọi oshares_for",
              repr(r) == repr(base) and fake.asked == [])
        dv.OSHARES_SOURCE = "live"
        dv._WARNED_ONCE.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
            r2 = dv.fair_value("FPT", "2026-10-28", price=100000.0, fin=fin)
        check("C7 có giá, KHÔNG price_date -> số quý + frame_error", r["oshares"] == base["oshares"]
              and r["oshares_method"] == "FRAME_FALLBACK" and "price_date" in (r["oshares_frame_error"] or ""))
        check("C7 ... và kêu stderr ĐÚNG 1 lần/tiến trình", err.getvalue().count("!!!!! [dcf_valuation] DCF_OSHARES_SOURCE=live") == 1
              and r2["oshares_method"] == "FRAME_FALLBACK", err.getvalue()[:100])
        fake.asked.clear()
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-29")
        check("C7 price_date == asof (sau ex) -> số CP sống ×1,5, khoá OK",
              math.isclose(r["oshares"], base["oshares"] * 1.5) and r["oshares_frame_error"] is None
              and fake.asked == ["2026-10-29"], f"{r['oshares']} {fake.asked}")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-17")
        check("C7 giá TRƯỚC ex, asof SAU ex -> lệch hệ -> số quý + kêu", r["oshares"] == base["oshares"]
              and r["oshares_method"] == "FRAME_FALLBACK" and "giua hai ngay" in r["oshares_frame_error"]
              and "KHONG khoa duoc khung" in err.getvalue(), r.get("oshares_frame_error"))
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-21")
        check("C7 giá và asof cùng phía ex (khác ngày) -> khoá OK, số sống",
              math.isclose(r["oshares"], base["oshares"] * 1.5) and r["oshares_frame_error"] is None)
        r = dv.fair_value("FPT", "2026-10-29", price=None, fin=fin)
        check("C7 không giá -> không cần khoá, số sống ở asof", math.isclose(r["oshares"], base["oshares"] * 1.5)
              and r["oshares_frame_error"] is None and "margin_of_safety" not in r)
        with contextlib.redirect_stderr(io.StringIO()):
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="not-a-date")
        check("C7 price_date không đọc được -> số quý", r["oshares"] == base["oshares"]
              and r["oshares_method"] == "FRAME_FALLBACK")
        r = dv.fair_value("FPT", pd_ts("2026-10-29"), price=100000.0, fin=fin, price_date=pd_ts("2026-10-29"))
        check("C7 price_date kiểu Timestamp == asof -> khoá OK", r["oshares_frame_error"] is None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-17")
        check("C7 nhánh fallback không in ra STDOUT", buf.getvalue() == "", buf.getvalue()[:60])
    finally:
        osd.oshares_for = real
        dv.OSHARES_SOURCE = "fin"


def pd_ts(x):
    import pandas as pd
    return pd.Timestamp(x)


def ops_block():
    src = open(OPS, encoding="utf-8").read()
    m = re.search(r"^# CHECKDCFOS_BEGIN.*?\n(.*?)^# CHECKDCFOS_END", src, re.S | re.M)
    return m.group(1) if m else None


def run_ops(block, wc_root, env_val=None, crontab=""):
    lines, warn = [], [0]

    class _SP:
        @staticmethod
        def run(*a, **k):
            return type("R", (), {"stdout": crontab, "returncode": 0})()
    old = os.environ.pop("DCF_OSHARES_SOURCE", None)
    if env_val is not None:
        os.environ["DCF_OSHARES_SOURCE"] = env_val
    try:
        ns = {"os": os, "re": re, "glob": glob, "subprocess": _SP, "wc_root": wc_root, "account": "SpaceX",
              "runonce_label": "SpaceX",
              "W": lambda m: (warn.__setitem__(0, warn[0] + 1), lines.append("W " + m)),
              "OK": lambda m: lines.append("OK " + m)}
        exec(block, ns)
    finally:
        os.environ.pop("DCF_OSHARES_SOURCE", None)
        if old is not None:
            os.environ["DCF_OSHARES_SOURCE"] = old
    return warn[0], lines


_TMPDIRS = []


def _mkdtemp():
    d = tempfile.mkdtemp(prefix="dcfos_root_")
    _TMPDIRS.append(d)
    return d


def fake_root(default_line='OSHARES_SOURCE_DEFAULT = "fin"', extra=None):
    d = _mkdtemp()
    os.makedirs(os.path.join(d, "mike", "bin"))
    os.makedirs(os.path.join(d, "trading_bot"))
    files = {"dcf_valuation.py": f"# DCF_OSHARES_SOURCE knob\n{default_line}\n",
             "wc_env.sh": "export TZ=Asia/Ho_Chi_Minh\n",
             "mike/bin/x.sh": "#!/bin/bash\n# DCF_OSHARES_SOURCE=live (comment ok)\n",
             "oshares_dcf_selfcheck.py": 'os.environ["DCF_OSHARES_SOURCE"] = "live"\n'}
    files.update(extra or {})
    for rel, txt in files.items():
        open(os.path.join(d, rel), "w").write(txt)
    return d


def c8_ops_block():
    blk = OPS_BLOCK[0]() if OPS_BLOCK else ops_block()
    check("C8 ops_health_check.sh có khối CHECKDCFOS", blk is not None, OPS)
    if blk is None:
        return
    n, ln = run_ops(blk, fake_root())
    check("C8 sạch (default fin, comment + selfcheck bỏ qua) -> 0 WARN, OK nêu 'fin'",
          n == 0 and any(l.startswith("OK") and "= fin" in l for l in ln), str(ln)[:200])
    n, ln = run_ops(blk, fake_root('OSHARES_SOURCE_DEFAULT = "lvie"'))
    check("C8 default gõ sai -> WARN", n == 1 and "lvie" in ln[0], str(ln)[:200])
    n, ln = run_ops(blk, fake_root('X = 1'))
    check("C8 nhắc knob mà thiếu dòng default -> WARN", n == 1 and "KHÔNG có dòng" in ln[0], str(ln)[:200])
    n, ln = run_ops(blk, fake_root(), env_val="live")
    check("C8 env cron mang DCF_OSHARES_SOURCE -> WARN", n == 1 and "môi trường cron" in ln[0], str(ln)[:200])
    n, ln = run_ops(blk, fake_root(), crontab="5 9 * * 1-5 DCF_OSHARES_SOURCE=live /x/run_bot.sh\n# DCF_OSHARES_SOURCE=live\n")
    check("C8 crontab gán -> WARN (dòng comment bỏ qua)", n == 1 and "crontab:" in ln[0] and "1 launcher" in ln[0], str(ln)[:200])
    for rel, txt, tag in (("wc_env.sh", "export DCF_OSHARES_SOURCE=live\n", "wc_env export"),
                          ("mike/bin/y.sh", "DCF_OSHARES_SOURCE=live python3 a.py\n", "mike/bin inline"),
                          ("trading_bot/z.py", 'os.environ["DCF_OSHARES_SOURCE"] = "live"\n', "py environ[]="),
                          ("w.py", 'os.environ.setdefault("DCF_OSHARES_SOURCE", "live")\n', "py setdefault"),
                          ("mike/bin/v.py", 'subprocess.run(c, env={"DCF_OSHARES_SOURCE": "live"})\n', "py dict env")):
        n, ln = run_ops(blk, fake_root(extra={rel: txt}))
        check(f"C8 launcher gán ({tag}) -> WARN", n == 1 and rel in ln[0], str(ln)[:200])
    n, ln = run_ops(blk, fake_root(extra={"trading_bot/q.py": 'x = os.environ.get("DCF_OSHARES_SOURCE")\n'}))
    check("C8 chỉ ĐỌC env trong .py -> không WARN", n == 0, str(ln)[:200])
    d = _mkdtemp()
    open(os.path.join(d, "dcf_valuation.py"), "w").write("# không có knob\n")
    n, ln = run_ops(blk, d)
    check("C8 cây chưa có knob -> im lặng (0 WARN, 0 OK)", n == 0 and ln == [], str(ln))


OPS_BLOCK = []      # mutant hook: [callable trả khối đã sửa]

R3_SCRIPTS = {"dcf_backtest.py": "D", "dcf_rate_robustness.py": "D", "dcf_fv_sens_cache.py": "dcf"}


def c9_research_pinned():
    import dcf_valuation as dv
    for f, al in R3_SCRIPTS.items():
        src = open(os.path.join(HERE, f), encoding="utf-8").read()
        imp = f"import dcf_valuation as {al}\n"
        pin = f"{al}.pin_oshares_source_fin(__file__)"
        ok = imp in src and pin in src and src.index(pin) > src.index(imp) \
            and src.index(pin) < src.index(f"{al}.fair_value(")
        check(f"C9 {f} ép fin ngay sau import, trước mọi fair_value(", ok)
    err = io.StringIO()
    try:
        dv.OSHARES_SOURCE = "live"
        with contextlib.redirect_stderr(err):
            dv.pin_oshares_source_fin("selfcheck")
        check("C9 pin_oshares_source_fin: live -> fin + kêu", dv.OSHARES_SOURCE == "fin" and "EP ve 'fin'" in err.getvalue())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            dv.pin_oshares_source_fin("selfcheck")
        check("C9 pin khi đã fin -> im lặng", err.getvalue() == "")
    finally:
        dv.OSHARES_SOURCE = "fin"


SUITE = [c1_classifier, c2_no_announced_branch, c3_oshares_for, c4_knob, c6_source_of_truth, c7_frame_lock,
         c8_ops_block, c9_research_pinned]


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
    "M8 bỏ khoá khung ex-date (luôn dùng số sống)": (dv, "_live_oshares", lambda real: lambda t, a, p, pdt, f:
        osd.oshares_for(t, a.date().isoformat(), f)),
    "M9 khoá chỉ kiểm có price_date, không so số CP hai ngày": (dv, "_live_oshares", lambda real: lambda t, a, p, pdt, f:
        real(t, a, p, (a if pdt is not None else None), f)),
    "M10 env lạ được nhận nguyên văn": (dv, "_resolve_oshares_source", lambda real: lambda e, default="fin":
        ((e.strip() if e and e.strip() else default), None)),
    "M11 pin_oshares_source_fin no-op": (dv, "pin_oshares_source_fin", lambda real: lambda who: None),
    "M12 kêu mọi lần (bỏ dedupe)": (dv, "_shout_once", lambda real: lambda k, m: dv._shout(m)),
    "M13 ops: bỏ quét .py (regex python không khớp gì)": (sys.modules[__name__], "OPS_BLOCK", lambda real: [
        lambda: ops_block().replace('_os_pat_py if _is_py else _os_pat', 're.compile("(?!x)x") if _is_py else _os_pat')]),
    "M14 ops: bỏ cảnh báo env cron": (sys.modules[__name__], "OPS_BLOCK", lambda real: [
        lambda: ops_block().replace('if _os_env not in (None, ""):', 'if False:')]),
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
    import shutil
    for _d in _TMPDIRS:
        shutil.rmtree(_d, ignore_errors=True)
    print(f"== mutation: {'mọi mutant bị giết' if mut_ok else 'CÓ MUTANT SỐNG'}")
    sys.exit(0 if not fails and mut_ok else 1)
