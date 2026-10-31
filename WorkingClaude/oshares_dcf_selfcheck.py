#!/usr/bin/env python3
"""Selfcheck oshares_dcf + knob DCF_OSHARES_SOURCE của dcf_valuation (job Taylor_20261030_094435;
R2-R5 job Taylor_20261030_155013: C6 nguồn sự thật OSHARES_SOURCE_DEFAULT, C7 khoá khung ex-date,
C8 khối CHECKDCFOS của ops_health_check.sh, C9 script nghiên cứu ép fin; R8 job Taylor_20261031_025427:
C7 thêm khoá lịch ex-date [price_date, asof] (H1), C10 oshares_for LỖI kêu + về fin (H2), C4/C6/C12
probe nạp ĐÚNG cây đang test (H3), C11 caller khai price_date (H4)).

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
# H3 (R8): dcf_valuation chèn WORKDIR canonical lên ĐẦU sys.path lúc import (dcf_valuation.py:64) ⇒ mọi
# import SAU nó (oshares_pit, oshares_live, trading_bot, ...) nạp bản PROD thay vì cây đang test. Ghim
# HERE lên đầu lại NGAY sau import; probe subprocess làm đúng như vậy (PIN) và C12 kiểm đường dẫn nạp.
import dcf_valuation as dv          # noqa: E402
sys.path.insert(0, HERE)
PROD = "/home/trido/thanhdt/WorkingClaude"
OPS = os.environ.get("DCF_OS_OPS_HEALTH", os.path.join(PROD, "mike/bin/ops_health_check.sh"))
LAG_DD_PACK = os.environ.get("DCF_OS_LAG_DD_PACK", os.path.join(PROD, "mike/bin/lag_dd_pack.py"))
TESTED_MODS = ("dcf_valuation", "oshares_dcf", "oshares_pit", "oshares_live", "corp_action_lib",
               "trading_bot.strategies", "trading_bot.due_diligence")

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


PIN = ["sys.path.insert(0, %r); "]      # mutant hook M22: [""] = probe không ghim lại cây test (template: %r = cây)


def probe_code(body, here=HERE):
    """Mã probe subprocess: nạp dcf_valuation TỪ `here`, ghim lại `here`, chạy `body` (phải gán `out`),
    in 1 dòng JSON {out, paths: {module: thư mục đã nạp}} để kiểm cây được test là cây nào (H3)."""
    pin = PIN[0] % here if "%r" in PIN[0] else PIN[0]
    return ("import sys, os, json; sys.path.insert(0, %r); import dcf_valuation as d; " % here + pin + body +
            "; print(json.dumps({'out': out, 'paths': {m: os.path.dirname(os.path.abspath(sys.modules[m].__file__)) "
            "for m in %r if m in sys.modules}}))" % (TESTED_MODS,))


def _probe(body, env_extra=None, unset=()):
    import json
    line = _subproc(probe_code(body), env_extra, unset)
    try:
        j = json.loads(line)
    except ValueError:
        return line, {}
    return j["out"], j["paths"]


def _paths_ok(paths):
    return bool(paths) and all(v == HERE for v in paths.values())


PROBE = ("r = d.fair_value('FPT', '2026-10-29', price=100000.0); "
         "out = ' '.join([d.OSHARES_SOURCE, str('oshares_dcf' in sys.modules), "
         "str(sorted(k for k in r if k.startswith('oshares_')))])")
PROBE_LIVE_OSD = ("import oshares_dcf as o; o.oshares_for = lambda t, a, f: {'value': f, 'source': 'x', 'method': 'X'}; "
                  "o.frame_events = lambda t, a, b: []; " + PROBE)


def c4_knob():
    out, paths = _probe(PROBE_LIVE_OSD, unset=("DCF_OSHARES_SOURCE",))
    check("C4 env trống -> 'live' (mặc định sau cutover 31/10), có khoá oshares_*",
          out.startswith("live True") and "oshares_source" in out, out)
    check("C4 probe nạp dcf_valuation của cây đang test (H3)", _paths_ok(paths), str(paths))
    out, paths = _probe(PROBE, {"DCF_OSHARES_SOURCE": "fin"})
    check("C4 env=fin (rollback/override) -> 'fin', không import oshares_dcf, không thêm khoá", out == "fin False []", out)
    out, paths = _probe(PROBE, {"DCF_OSHARES_SOURCE": "bogus"})
    check("C4 giá trị lạ -> 'fin' (hành vi cũ)", out == "fin False []", out)
    out, paths = _probe(PROBE_LIVE_OSD, {"DCF_OSHARES_SOURCE": "live"})
    check("C4 env=live -> 'live', có khoá oshares_* (gồm oshares_frame_error)",
          out.startswith("live True") and "oshares_source" in out and "oshares_frame_error" in out, out)
    check("C4 env=live: oshares_dcf/oshares_pit... nạp từ cây đang test, KHÔNG từ PROD (H3)",
          _paths_ok(paths) and "oshares_dcf" in paths, str(paths))

    import dcf_valuation as dv
    fin = dv._load_financials()
    real, real_fe = osd.oshares_for, osd.frame_events
    calls = []
    _ev_fixture([])
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        dv.OSHARES_SOURCE = "live"
        osd.frame_events = lambda t, d0, d1: []
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
            dv.fair_value("FPT", "2026-10-29", price=None, fin=fin)     # R9: có giá không price_date = không gọi oshares_for
        check("C4 live: oshares_for in ra stdout -> stdout của fair_value vẫn rỗng", buf.getvalue() == "", buf.getvalue()[:80])
        osd.oshares_for = real
        osd._CACHE.update(tickers=frozenset(), until=None, data=None)
        import oshares_live as _ol
        real_fetch = _ol._fetch
        def _boom(*a, **k):
            raise RuntimeError("bq down (simulated)")
        _ol._fetch = _boom
        dv._WARNED_ONCE.clear()
        buf, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                dv.fair_value("FPT", "2026-10-29", price=None, fin=fin)
        finally:
            _ol._fetch = real_fetch
            osd._CACHE.update(tickers=frozenset(), until=None, data=None)
        check("C4 live + BQ lỗi: stdout rỗng, chẩn đoán ở stderr", buf.getvalue() == "" and "fetch_cache FAILED" in err.getvalue(),
              f"stdout={buf.getvalue()[:60]!r} stderr={err.getvalue()[:60]!r}")
    finally:
        osd.oshares_for = real
        osd.frame_events = real_fe
        _ev_clear()
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
    check("C6 có đúng 1 dòng OSHARES_SOURCE_DEFAULT và = 'live' (knob BẬT, cutover 31/10/2026)",
          m is not None and m.group(1) == "live" and len(re.findall(r"^OSHARES_SOURCE_DEFAULT\s*=", src, re.M)) == 1,
          m.group(1) if m else "none")
    R = dv._resolve_oshares_source
    check("C6 env None/rỗng -> default", R(None) == ("live", None) and R("  ") == ("live", None)
          and R(None, "fin") == ("fin", None))
    v, w = R("fin")
    check("C6 env 'fin' khác default -> 'fin' + cảnh báo OVERRIDE", v == "fin" and w and "OVERRIDE" in w, str(w))
    check("C6 env == default -> không cảnh báo", R("live") == ("live", None) and R(" fin ", "fin") == ("fin", None))
    for bad in ("LIVE", "bogus", "1"):
        v, w = R(bad, "live")
        check(f"C6 env lạ {bad!r} -> 'fin' + KHONG HOP LE (kể cả khi default=live)", v == "fin" and "KHONG HOP LE" in (w or ""))
    v, w = R(None, "lvie")
    check("C6 hằng số default gõ sai -> 'fin' + kêu", v == "fin" and "OSHARES_SOURCE_DEFAULT" in (w or ""))
    p = subprocess.run([sys.executable, "-c", probe_code("out = d.OSHARES_SOURCE")],
                       cwd=HERE, env={**os.environ, "DCF_OSHARES_SOURCE": "bogus"}, capture_output=True, text=True, timeout=300)
    check("C6 import với env lạ: không raise, 'fin', kêu stderr", p.returncode == 0 and '"out": "fin"' in p.stdout
          and "KHONG HOP LE" in p.stderr, p.stderr[-120:])
    check("C6 probe nạp dcf_valuation của cây đang test (H3)", f'"dcf_valuation": "{HERE}"' in p.stdout, p.stdout[-160:])


class _FakeOS:
    """oshares_for giả: số CP đổi tại ex-date `ex` (×mult); ghi lại các ngày được hỏi."""
    def __init__(self, ex="2026-10-20", mult=1.5):
        self.ex, self.mult, self.asked = ex, mult, []

    def __call__(self, t, a, f):
        self.asked.append(a)
        return {"value": f * (self.mult if a >= self.ex else 1.0), "source": "oshares_live", "method": "FAKE"}


def _ev_fixture(rows):
    """Nạp _EV_CACHE của oshares_dcf bằng dòng pricing_events giả (FPT) — frame_events THẬT lọc trên đó."""
    osd._EV_CACHE.update(tickers=frozenset({"FPT"}), until="2026-12-31",
                         rows=[{**r, "ticker": "FPT"} for r in rows])


def _ev_clear():
    osd._EV_CACHE.update(tickers=frozenset(), until=None, rows=None)


def c7_frame_lock():
    import dcf_valuation as dv
    fin = dv._load_financials()
    real = osd.oshares_for
    _ev_fixture([])
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

        # ---- R8/H1: kịch bản killer của skeptic + lịch ex-date [price_date, asof]
        fake29 = _FakeOS(ex="2026-10-29")           # vendor ĐÃ executed: số CP ×1,5 từ chính ngày asof
        osd.oshares_for = fake29
        _ev_fixture([iss("2026-10-29", 0.5, BON)])
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-29")
        check("C7/H1 KILLER: ex == asof, giá tham chiếu cũ khai price_date=asof -> số quý + kêu",
              r["oshares"] == base["oshares"] and r["oshares_method"] == "FRAME_FALLBACK"
              and "ISS doi khung gia ex 2026-10-29" in (r["oshares_frame_error"] or "")
              and "KHONG khoa duoc khung" in err.getvalue(), r.get("oshares_frame_error"))
        r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-29")
        check("C7/H1 ex == price_date < asof -> số quý (không chứng minh được giá phiên ex đã điều chỉnh)",
              r["oshares_method"] == "FRAME_FALLBACK", r.get("oshares_frame_error"))
        r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-30")
        check("C7/H1 ex < price_date == asof -> khoá OK, số sống ×1,5 (giá và số CP cùng SAU ex)",
              math.isclose(r["oshares"], base["oshares"] * 1.5) and r["oshares_frame_error"] is None,
              r.get("oshares_frame_error"))
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C7/H1 giá đúng phiên T-1 (trước ex), asof = ex -> số quý (R5 hoặc lịch bắt)",
              r["oshares_method"] == "FRAME_FALLBACK", r.get("oshares_frame_error"))
        stale = _FakeOS(ex="2099-01-01")             # vendor CHƯA lật executed: hai ngày cùng số cũ
        osd.oshares_for = stale
        _ev_fixture([iss("2026-10-29", 0.5, BON, status="announced")])
        r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C7/H1 vendor trễ (số CP hai ngày BẰNG nhau) + ISS announced giữa hai ngày -> số quý (R5 không thấy, lịch thấy)",
              r["oshares_method"] == "FRAME_FALLBACK" and "ISS doi khung gia" in (r["oshares_frame_error"] or ""),
              r.get("oshares_frame_error"))
        _ev_fixture([iss("2026-10-29", 0.0, "Phát hành riêng lẻ"), div("2026-10-29", 0.2)])
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-29")
        check("C7/H1 riêng lẻ / cổ tức TIỀN ex == asof -> không dời khung giá, khoá OK",
              r["oshares_frame_error"] is None, r.get("oshares_frame_error"))
        _ev_fixture([iss("2026-10-29", 0.1, meth=None)])
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-29")
        check("C7/H1 ISS không ghi phương thức ex == asof -> coi như dời khung (fail-closed)",
              r["oshares_method"] == "FRAME_FALLBACK", r.get("oshares_frame_error"))
        _ev_fixture([iss("2026-10-27", 0.5, BON), iss("2026-10-31", 0.5, BON)])
        r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C7/H1 sự kiện ngoài [price_date, asof] (trước và sau) -> khoá OK",
              r["oshares_frame_error"] is None, r.get("oshares_frame_error"))
        _ev_fixture([])
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-30")
        check("C7/H1 price_date SAU asof -> số quý", r["oshares_method"] == "FRAME_FALLBACK"
              and "SAU asof" in (r["oshares_frame_error"] or ""), r.get("oshares_frame_error"))
        real_pe = osd.pricing_events
        def _ev_boom(*a, **k):
            raise RuntimeError("bq down (simulated)")
        real_ue = osd.unexecuted_events
        osd.pricing_events = _ev_boom
        osd.unexecuted_events = lambda t, a, **k: []  # R9: cô lập frame_events (khoá (c) đọc cùng nguồn, có check riêng C13)
        _ev_clear()                                  # frame_events THẬT phải hỏi pricing_events -> lỗi
        try:
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-29")
        finally:
            osd.pricing_events = real_pe
            osd.unexecuted_events = real_ue
        check("C7/H1 không đọc được lịch ex-date -> số quý (fail-closed)", r["oshares_method"] == "FRAME_FALLBACK"
              and "lich ex-date" in (r["oshares_frame_error"] or ""), r.get("oshares_frame_error"))
        _ev_fixture([])
        r = dv.fair_value("FPT", "2026-10-29", price=None, fin=fin)
        check("C7/H1 không giá -> không đọc khung [price_date, asof], số sống", r["oshares_frame_error"] is None)
    finally:
        osd.oshares_for = real
        _ev_clear()
        dv.OSHARES_SOURCE = "fin"


def c10_oshares_error():
    """R8/H2: oshares_for LỖI (method ERROR hoặc raise) -> số quý + kêu stderr 1 lần/tiến trình/MÃ."""
    import dcf_valuation as dv
    fin = dv._load_financials()
    real = osd.oshares_for
    _ev_fixture([])
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-29", price=None, fin=fin)
        base_h = dv.fair_value("VNM", "2026-10-29", price=None, fin=fin)
        dv.OSHARES_SOURCE = "live"
        dv._WARNED_ONCE.clear()
        osd.oshares_for = lambda t, a, f: {"ticker": t, "value": f, "source": "ticker_financial",
                                           "reason": "oshares_dcf lỗi (RuntimeError: x)", "method": "ERROR"}
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            r1 = dv.fair_value("FPT", "2026-10-29", price=None, fin=fin)
            r2 = dv.fair_value("FPT", "2026-10-28", price=None, fin=fin)
            r3 = dv.fair_value("VNM", "2026-10-29", price=None, fin=fin)
        e = err.getvalue()
        check("C10 ERROR -> số quý, method ERROR", r1["oshares"] == base["oshares"] and r1["oshares_method"] == "ERROR"
              and r3["oshares"] == base_h["oshares"], f"{r1.get('oshares_method')}")
        check("C10 ERROR -> kêu stderr 1 lần/MÃ (FPT 2 lời gọi = 1 tiếng, VNM thêm 1)",
              e.count("!!!!! [dcf_valuation] DCF_OSHARES_SOURCE=live FPT asof=2026-10-29: oshares_for LOI") == 1
              and e.count("!!!!! [dcf_valuation] DCF_OSHARES_SOURCE=live VNM asof=2026-10-29: oshares_for LOI") == 1
              and e.count("!!!!! [dcf_valuation]") == 2, e[:300])
        check("C10 ERROR -> stdout sạch", out.getvalue() == "", out.getvalue()[:60])

        def _raise(t, a, f):
            raise ValueError("boom")
        osd.oshares_for = _raise
        dv._WARNED_ONCE.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-29")
        check("C10 oshares_for RAISE -> không raise, số quý + kêu", r["ok"] and r["oshares"] == base["oshares"]
              and r["oshares_method"] == "ERROR" and "!!!!! [dcf_valuation] DCF_OSHARES_SOURCE=live FPT asof=2026-10-29: oshares_for LOI"
              in err.getvalue(), err.getvalue()[:120])
        _ev_fixture([])
        calls = []
        def _err_on_px(t, a, f):
            calls.append(a)
            return ({"value": f, "source": "ticker_financial", "method": "ERROR", "reason": "x"} if a != "2026-10-29"
                    else {"value": f * 1.5, "source": "oshares_live", "method": "OK"})
        osd.oshares_for = _err_on_px
        with contextlib.redirect_stderr(io.StringIO()):
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-20")
        check("C10 oshares_for LỖI ở ngày giá -> không khoá được -> số quý", r["oshares"] == base["oshares"]
              and r["oshares_method"] == "FRAME_FALLBACK" and "LOI" in (r["oshares_frame_error"] or ""),
              r.get("oshares_frame_error"))
    finally:
        osd.oshares_for = real
        _ev_clear()
        dv.OSHARES_SOURCE = "fin"


def c11_callers():
    """R8/H4: caller production khai price_date ĐÚNG phiên của giá — hoặc KHÔNG khai khi không biết."""
    import pandas as pd
    import dcf_valuation as dv
    import trading_bot.strategies as st
    import trading_bot.due_diligence as dd
    seen = []
    real_fv = dv.fair_value
    dv.fair_value = lambda *a, **k: (seen.append(k.get("price_date", "ABSENT")) or real_fv(*a, **k))
    try:
        st._dcf_check_for_order("FPT", 100000.0, "2026-10-29", price_date="2026-10-28")
        st._dcf_check_for_order("FPT", 100000.0, "2026-10-29")
        check("C11 _dcf_check_for_order chuyển price_date nguyên văn (mặc định None)",
              seen == ["2026-10-28", None], str(seen))
        real_row = dd._latest_row
        try:
            dd._latest_row = lambda t, a: pd.Series({"time": pd.Timestamp("2026-10-28"), "Price": 50000.0, "Close": 49000.0})
            check("C11 _ref_price_session: dùng Price -> phiên = time của dòng",
                  dd._ref_price_session("FPT", "2026-10-29") == (50000.0, "2026-10-28")
                  and dd._ref_price_for("FPT", "2026-10-29") == 50000.0)
            dd._latest_row = lambda t, a: pd.Series({"time": pd.Timestamp("2026-10-28"), "Price": float("nan"), "Close": 49000.0})
            check("C11 _ref_price_session: rơi về Close (đã điều chỉnh) -> price_date None",
                  dd._ref_price_session("FPT", "2026-10-29") == (49000.0, None))
            seen.clear()
            dd._latest_row = lambda t, a: pd.Series({"time": pd.Timestamp("2026-10-28"), "Price": 50000.0, "Close": 49000.0,
                                                     "ticker": "FPT"})
            src = open(dd.__file__, encoding="utf-8").read()
            check("C11 due_diligence DD-valuation: tự đọc Price -> price_date=row.time; ctx price -> ctx['price_date']",
                  'px, px_date = row.get("Price"), str(row.get("time"))[:10]' in src
                  and 'px, px_date = ctx.get("price"), ctx.get("price_date")' in src
                  and "_dcf_check_for_order(ticker, float(px), asof, price_date=px_date)" in src)
        finally:
            dd._latest_row = real_row
        src = open(os.path.join(HERE, "custom_basket.py"), encoding="utf-8").read()
        check("C11 custom_basket.dcf_at: price_date = d (Price của đúng phiên d)",
              "fair_value(tk, pd.Timestamp(d), price=px, fin=_fin, price_date=pd.Timestamp(d))" in src
              and "_px_map.get(key)" in src)
        # lag_dd_pack.run_valuation (mike repo) — gọi THẬT với dd/strategies của cây đang test
        import importlib.util
        if os.path.exists(LAG_DD_PACK):
            spec = importlib.util.spec_from_file_location("lag_dd_pack_under_test", LAG_DD_PACK)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            sys.path.insert(0, HERE)
            got = []
            real_rps, real_chk = getattr(dd, "_ref_price_session", None), st._dcf_check_for_order
            try:
                dd._ref_price_session = lambda t, a: (50000.0, "2026-10-28")
                st._dcf_check_for_order = lambda t, p, a, **k: (got.append(k.get("price_date")) or
                                                               {"status": "NOT_COMPUTED", "reason": "x"})
                m.run_valuation("FPT", "2026-10-29")
                dd._ref_price_session = lambda t, a: (49000.0, None)
                m.run_valuation("FPT", "2026-10-29")
            finally:
                if real_rps is not None:
                    dd._ref_price_session = real_rps
                st._dcf_check_for_order = real_chk
            check("C11 lag_dd_pack.run_valuation: khai price_date phiên Price, không khai khi rơi về Close",
                  got == ["2026-10-28", None], f"{got} ({LAG_DD_PACK})")
        else:
            check("C11 lag_dd_pack có ở DCF_OS_LAG_DD_PACK", False, LAG_DD_PACK)
        seen.clear()
        real_lps = dv.latest_price_session
        dv.latest_price_session = lambda t, a=None: (50000.0, "2026-10-28")
        try:
            dv.dcf_check("FPT", "2026-10-29")
            dv.dcf_check("FPT", "2026-10-29", price=51000.0)
        finally:
            dv.latest_price_session = real_lps
        check("C11 dcf_valuation.dcf_check: tự đọc giá -> price_date phiên đó; giá caller -> None",
              seen == ["2026-10-28", None], str(seen))
    finally:
        dv.fair_value = real_fv


def c12_module_paths():
    """H3: mọi module cần test nạp từ cây HERE, không phải PROD (dcf_valuation chèn WORKDIR vào sys.path)."""
    import oshares_pit, oshares_live, corp_action_lib, trading_bot.strategies, trading_bot.due_diligence  # noqa: F401
    paths = {m: os.path.dirname(os.path.abspath(sys.modules[m].__file__)) for m in TESTED_MODS}
    paths["trading_bot.strategies"] = os.path.dirname(paths["trading_bot.strategies"])
    paths["trading_bot.due_diligence"] = os.path.dirname(paths["trading_bot.due_diligence"])
    check("C12 in-process: module nạp từ cây đang test", all(v == HERE for v in paths.values()),
          str({k: v for k, v in paths.items() if v != HERE}))


def pd_ts(x):
    import pandas as pd
    return pd.Timestamp(x)


def ops_block():
    src = open(OPS, encoding="utf-8").read()
    m = re.search(r"^# CHECKDCFOS_BEGIN.*?\n(.*?)^# CHECKDCFOS_END", src, re.S | re.M)
    return m.group(1) if m else None


def run_ops(block, wc_root, env_val=None, crontab="", home=None, ccdb=None, proc=None):
    lines, warn = [], [0]
    ext = {"MIKE_DCFOS_HOME": home or _mkdtemp(), "MIKE_DCFOS_CCDB": ccdb or _mkdtemp(),
           "MIKE_DCFOS_PROC": proc or _mkdtemp()}          # R8/H6: không quét HOME//proc thật
    old_ext = {k: os.environ.get(k) for k in ext}
    os.environ.update(ext)

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
        for k, v in old_ext.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return warn[0], lines


def fake_tree(files):
    d = _mkdtemp()
    for rel, txt in files.items():
        fp = os.path.join(d, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "wb" if isinstance(txt, bytes) else "w").write(txt)
    return d


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
    # ---- R8/H6: launcher ngoài cây WC
    for home_files, tag in (({".config/systemd/user/ccdb-x.service": "[Service]\nEnvironment=DCF_OSHARES_SOURCE=live\n"}, "systemd Environment="),
                            ({".config/systemd/user/paseo.service.d/o.conf": '[Service]\nEnvironment="DCF_OSHARES_SOURCE=live"\n'}, "systemd drop-in"),
                            ({".config/environment.d/10-x.conf": "DCF_OSHARES_SOURCE=live\n"}, "environment.d"),
                            ({".bashrc": "export DCF_OSHARES_SOURCE=live\n"}, "bashrc export"),
                            ({".claude/settings.json": '{"env": {"DCF_OSHARES_SOURCE": "live"}}\n'}, "claude settings env")):
        n, ln = run_ops(blk, fake_root(), home=fake_tree(home_files))
        check(f"C8/H6 ngoài cây ({tag}) -> WARN", n == 1 and list(home_files)[0] in ln[0], str(ln)[:200])
    n, ln = run_ops(blk, fake_root(), ccdb=fake_tree({".env": "MODEL=x\nDCF_OSHARES_SOURCE=live\n"}))
    check("C8/H6 ccdb .env -> WARN", n == 1 and ".env" in ln[0], str(ln)[:200])
    n, ln = run_ops(blk, fake_root(), proc=fake_tree({"4242/environ": b"PATH=/bin\0DCF_OSHARES_SOURCE=live\0", "4242/comm": "python3\n",
                                                      "77/environ": b"PATH=/bin\0"}))
    check("C8/H6 tiến trình đang chạy mang biến -> WARN (nêu pid + comm)", n == 1 and "4242 (python3)" in ln[0], str(ln)[:200])
    n, ln = run_ops(blk, fake_root(), home=fake_tree({".config/systemd/user/a.service": "# Environment=DCF_OSHARES_SOURCE=live\n",
                                                      ".bashrc": "echo $DCF_OSHARES_SOURCE\n"}),
                    proc=fake_tree({"9/environ": b"PATH=/bin\0"}))
    check("C8/H6 comment/chỉ đọc ngoài cây -> 0 WARN; OK nêu số file + tiến trình đã quét",
          n == 0 and any("2 file ngoài cây + 1 tiến trình" in l for l in ln), str(ln)[:240])
    # ---- R9/việc 6: settings JSON chỉ đọc khoá "env"; tiến trình research gắn cờ
    perm = '{"permissions": {"allow": ["Bash(DCF_OSHARES_SOURCE=live python3 oshares_dcf_selfcheck.py)"]}, "env": {"X": "1"}}\n'
    n, ln = run_ops(blk, fake_root(), home=fake_tree({".claude/settings.json": perm}))
    check("C8/R9 settings.json: chuỗi QUYỀN Bash(DCF_OSHARES_SOURCE=...) không phải gán env -> 0 WARN", n == 0, str(ln)[:200])
    root = fake_root()
    os.makedirs(os.path.join(root, ".claude"))
    open(os.path.join(root, ".claude", "settings.local.json"), "w").write('{"env": {"DCF_OSHARES_SOURCE": "live"}}')
    n, ln = run_ops(blk, root)
    check("C8/R9 settings.local.json của WC có env.DCF_OSHARES_SOURCE -> WARN", n == 1 and "env.DCF_OSHARES_SOURCE=live" in ln[0],
          str(ln)[:200])
    n, ln = run_ops(blk, fake_root(), home=fake_tree({".claude/settings.json": '{"env": {"DCF_OSHARES_SOURCE": '}))
    check("C8/R9 settings.json hỏng -> WARN không đọc được (không im lặng)", n == 1 and "không đọc được" in ln[0], str(ln)[:200])
    # ---- R10/việc 4: hooks.*.command + statusLine.command là lệnh shell ⇒ gán kiểu shell ở đó = launcher
    hk = ('{"hooks": {"SessionStart": [{"matcher": "", "hooks": [{"type": "command", '
          '"command": "export DCF_OSHARES_SOURCE=live; bash x.sh"}]}]}, '
          '"statusLine": {"type": "command", "command": "DCF_OSHARES_SOURCE=live python3 s.py"}, '
          '"permissions": {"allow": ["Bash(DCF_OSHARES_SOURCE=live python3 a.py)"]}}\n')
    n, ln = run_ops(blk, fake_root(), home=fake_tree({".claude/settings.json": hk}))
    msg = ln[0] if ln else ""
    check("C8/R10 settings.json hooks.command + statusLine.command gán biến -> WARN (2 launcher, không tính permissions)",
          n == 1 and "2 launcher" in msg and "command export DCF_OSHARES_SOURCE=live" in msg, msg[:300])
    hk0 = '{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo DCF_OSHARES_SOURCE is fin"}]}]}}\n'
    n, ln = run_ops(blk, fake_root(), home=fake_tree({".claude/settings.json": hk0}))
    check("C8/R10 hooks.command chỉ NHẮC tên biến (không gán) -> 0 WARN", n == 0, str(ln)[:200])
    n, ln = run_ops(blk, fake_root(), proc=fake_tree({
        "51/environ": b"DCF_OSHARES_SOURCE=live\0", "51/comm": "python3\n",
        "51/cmdline": b"/home/trido/thanhdt/wc_venv/bin/python\0agents/Taylor/research/oshares_x/measure.py\0",
        "52/environ": b"DCF_OSHARES_SOURCE=live\0", "52/comm": "python3\n", "52/cmdline": b"python3\0/x/run_bot.py\0",
        "53/environ": b"DCF_OSHARES_SOURCE=live\0", "53/comm": "bash\n", "53/cmdline": b"bash\0/x/research/a.sh\0"}))
    msg = ln[0] if ln else ""
    check("C8/R9 /proc: python chạy research -> VẪN WARN nhưng gắn [research override]; khác -> [LAUNCHER]",
          n == 1 and "3 launcher" in msg and "[research override] tiến trình 51 (python3)" in msg
          and "[LAUNCHER] tiến trình 52 (python3)" in msg and "[LAUNCHER] tiến trình 53 (bash)" in msg, msg[:300])


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


# ─────────────────────────────────────────────────────────────── R9 (job Taylor_20261031_042224)
class _Count:
    """Thay một hàm truy vấn BQ: đếm lời gọi, raise để không bao giờ chạm mạng."""
    def __init__(self):
        self.n = 0

    def __call__(self, *a, **k):
        self.n += 1
        raise RuntimeError("BQ bị chặn trong selfcheck (đếm lời gọi)")


def c13_unexecuted():
    """Việc 1: ISS dời khung giá ex ≤ asof (lùi 90 ngày) chưa `executed` ⇒ số quý + kêu, mọi ca."""
    import dcf_valuation as dv
    fin = dv._load_financials()
    real = osd.oshares_for
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-30", price=None, fin=fin)
        dv.OSHARES_SOURCE = "live"
        dv._WARNED_ONCE.clear()
        osd.oshares_for = _FakeOS(ex="2099-01-01")           # vendor chưa lật: số CP hai ngày = số cũ
        _ev_fixture([iss("2026-10-20", 0.5, BON, status="announced")])
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C13 KHE H1: ISS announced ex TRƯỚC price_date (ngoài [price_date, asof]) -> số quý + kêu",
              r["oshares"] == base["oshares"] and r["oshares_method"] == "FRAME_FALLBACK"
              and "chua executed" in (r["oshares_frame_error"] or "") and "2026-10-20:announced" in r["oshares_frame_error"]
              and "KHONG khoa duoc khung" in err.getvalue(), r.get("oshares_frame_error"))
        with contextlib.redirect_stderr(io.StringIO()):
            r = dv.fair_value("FPT", "2026-10-30", price=None, fin=fin)
        check("C13 ... kể cả KHÔNG có giá (số CP sống ở asof còn là số trước sự kiện)",
              r["oshares_method"] == "FRAME_FALLBACK" and "chua executed" in (r["oshares_frame_error"] or ""))
        osd.oshares_for = _FakeOS(ex="2026-10-20")
        _ev_fixture([iss("2026-10-20", 0.5, BON, status="executed")])
        r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C13 cùng sự kiện ĐÃ executed, giá và asof cùng sau ex -> khoá OK, số sống ×1,5",
              math.isclose(r["oshares"], base["oshares"] * 1.5) and r["oshares_frame_error"] is None, r.get("oshares_frame_error"))
        osd.oshares_for = _FakeOS(ex="2099-01-01")
        _ev_fixture([iss("2026-07-31", 0.5, BON, status="announced")])          # 91 ngày trước asof
        r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C13 announced ex NGOÀI 90 ngày lùi -> không xét (khoá OK)", r["oshares_frame_error"] is None,
              r.get("oshares_frame_error"))
        _ev_fixture([iss("2026-08-01", 0.5, BON, status="announced")])          # đúng 90 ngày
        with contextlib.redirect_stderr(io.StringIO()):
            r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C13 announced ex đúng biên 90 ngày -> số quý", r["oshares_method"] == "FRAME_FALLBACK",
              r.get("oshares_frame_error"))
        _ev_fixture([iss("2026-10-20", 0.0, "Phát hành riêng lẻ", status="announced"), div("2026-10-20", 0.2)])
        r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C13 riêng lẻ / cổ tức tiền chưa executed -> không dời khung, khoá OK", r["oshares_frame_error"] is None,
              r.get("oshares_frame_error"))
        _ev_fixture([iss("2026-10-20", 0.1, meth=None, status="")])
        with contextlib.redirect_stderr(io.StringIO()):
            r = dv.fair_value("FPT", "2026-10-30", price=100000.0, fin=fin, price_date="2026-10-28")
        check("C13 ISS không phương thức, status rỗng -> coi như chưa executed (fail-closed)",
              r["oshares_method"] == "FRAME_FALLBACK", r.get("oshares_frame_error"))
        real_ue = osd.unexecuted_events
        def _boom(*a, **k):
            raise RuntimeError("bq down (simulated)")
        osd.unexecuted_events = _boom
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                r = dv.fair_value("FPT", "2026-10-30", price=None, fin=fin)
        finally:
            osd.unexecuted_events = real_ue
        check("C13 không đọc được lịch chưa executed -> số quý (fail-closed)", r["oshares_method"] == "FRAME_FALLBACK"
              and "chua executed" in (r["oshares_frame_error"] or ""), r.get("oshares_frame_error"))
        n = _Count()
        real_pe = osd.pricing_events
        osd.pricing_events = n
        _ev_clear()
        try:
            got = None
            try:
                osd.unexecuted_events("FPT", "2026-10-30")
            except RuntimeError:
                got = "raise"
        finally:
            osd.pricing_events = real_pe
        check("C13 unexecuted_events không cache -> hỏi pricing_events, KHÔNG nuốt lỗi", n.n == 1 and got == "raise", f"{n.n} {got}")
    finally:
        osd.oshares_for = real
        _ev_clear()
        dv.OSHARES_SOURCE = "fin"


def c14_no_bq_without_price_date():
    """Việc 3: có giá mà price_date None/hỏng/> asof ⇒ số quý NGAY, 0 lời gọi oshares_for/BQ (plan 21:00)."""
    import dcf_valuation as dv
    import oshares_live as _ol
    fin = dv._load_financials()
    real = (osd.oshares_for, osd.fetch_cache, osd.pricing_events, _ol._fetch)
    cnt = {"oshares_for": 0}
    n_fc, n_pe, n_ol = _Count(), _Count(), _Count()
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        dv.OSHARES_SOURCE = "live"
        dv._WARNED_ONCE.clear()
        osd._CACHE.update(tickers=frozenset(), until=None, data=None)
        _ev_clear()

        def _osf(t, a, f):
            cnt["oshares_for"] += 1
            return real[0](t, a, f)
        osd.oshares_for, osd.fetch_cache, osd.pricing_events, _ol._fetch = _osf, n_fc, n_pe, n_ol
        out = []
        with contextlib.redirect_stderr(io.StringIO()):
            for pdt in (None, "not-a-date", "2026-10-30"):
                out.append(dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date=pdt))
        calls = cnt["oshares_for"] + n_fc.n + n_pe.n + n_ol.n
        check("C14 có giá, price_date None/hỏng/>asof -> 0 lời gọi oshares_for + 0 BQ",
              calls == 0, f"oshares_for={cnt['oshares_for']} fetch_cache={n_fc.n} pricing_events={n_pe.n} _fetch={n_ol.n}")
        check("C14 ... và kết quả = số quý, FRAME_FALLBACK, nêu lý do",
              all(r["oshares"] == base["oshares"] and r["oshares_method"] == "FRAME_FALLBACK" for r in out)
              and "price_date" in out[0]["oshares_frame_error"] and "khong doc duoc" in out[1]["oshares_frame_error"]
              and "SAU asof" in out[2]["oshares_frame_error"], str([r.get("oshares_frame_error") for r in out]))
        r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        check("C14 fallback không giá-ngày vẫn mang đủ khoá oshares_* (schema không đổi)",
              {"oshares_fin", "oshares_source", "oshares_method", "oshares_frame_error"} <= set(r), str(sorted(r))[:120])
    finally:
        osd.oshares_for, osd.fetch_cache, osd.pricing_events, _ol._fetch = real
        osd._CACHE.update(tickers=frozenset(), until=None, data=None)
        dv.OSHARES_SOURCE = "fin"


def c15_divergence():
    """Việc 2: OShares live lệch số quý > 10% PHẢI hiện: stderr + _dcf_check_for_order + format_dcf_check + lag_dd_pack."""
    import dcf_valuation as dv
    import trading_bot.strategies as st
    fin = dv._load_financials()
    real = osd.oshares_for
    _ev_fixture([])
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        d_fin = st._dcf_check_for_order("FPT", 100000.0, "2026-10-29", price_date="2026-10-28")
        check("C15 fin: _dcf_check_for_order KHÔNG thêm khoá oshares_* (byte-identical)",
              not any(k.startswith("oshares") for k in d_fin), str(sorted(d_fin)))
        check("C15 fin: format_dcf_check không có dòng OShares", "OShares" not in st.format_dcf_check(d_fin))
        dv.OSHARES_SOURCE = "live"
        dv._WARNED_ONCE.clear()
        osd.oshares_for = _FakeOS(ex="2000-01-01", mult=1.3591)       # R10: live < quý nay về số quý (C20) ⇒
        err = io.StringIO()                                           # đo hiển thị lệch bằng chiều live > quý
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-28")
            d = st._dcf_check_for_order("FPT", 100000.0, "2026-10-29", price_date="2026-10-28")
        e = err.getvalue()
        check("C15 live ×1,3591: oshares_divergence ≈ +35,9%", math.isclose(r.get("oshares_divergence") or 0, 0.3591, abs_tol=1e-4)
              and r["oshares_frame_error"] is None, str(r.get("oshares_divergence")))
        check("C15 ... kêu stderr 'OShares live X vs quy Y (+36%)' đúng 1 lần/mã/asof",
              e.count("!!!!! [dcf_valuation] FPT: OShares live") == 1 and "(+36%)" in e and "vs quy" in e, e[:240])
        line = st.format_dcf_check(d)
        check("C15 ... _dcf_check_for_order mang oshares/oshares_fin/divergence, format_dcf_check in '⚠ OShares live … (+36%)'",
              d.get("oshares_fin") == base["oshares"] and "⚠ OShares live" in line and "(+36%)" in line, line)
        osd.oshares_for = _FakeOS(ex="2000-01-01", mult=1.05)
        dv._WARNED_ONCE.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            d = st._dcf_check_for_order("FPT", 100000.0, "2026-10-29", price_date="2026-10-28")
        check("C15 lệch +5% (dưới ngưỡng 10%) -> không kêu, không in", "OShares live" not in err.getvalue()
              and "OShares" not in st.format_dcf_check(d), err.getvalue()[:120])
        check("C15 biên ngưỡng: |lệch| = 10% không kêu, 10,1% kêu",
              "OShares" not in st.format_dcf_check({"status": "CHEAP", "margin_of_safety": 0.1, "oshares_divergence": -0.10,
                                                    "oshares": 90.0, "oshares_fin": 100.0})
              and "OShares" in st.format_dcf_check({"status": "CHEAP", "margin_of_safety": 0.1, "oshares_divergence": -0.101,
                                                    "oshares": 89.9, "oshares_fin": 100.0}))
        import importlib.util
        if os.path.exists(LAG_DD_PACK):
            spec = importlib.util.spec_from_file_location("lag_dd_pack_r9", LAG_DD_PACK)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            sys.path.insert(0, HERE)
            w = m.soft_warnings({"valuation": {"dcf": {"status": "CHEAP", "oshares": 83.6e6, "oshares_fin": 113.6e6,
                                                         "oshares_divergence": -0.2641, "oshares_source": "oshares_live",
                                                         "oshares_method": "AIS"}}})
            w0 = m.soft_warnings({"valuation": {"dcf": {"status": "CHEAP"}}})
            check("C15 lag_dd_pack: WARNING OSHARES_LIVE_LECH (−26%), không có khi fin",
                  [x["code"] for x in w] == ["OSHARES_LIVE_LECH"] and "(-26%)" in w[0]["evidence"] and w0 == [], str(w)[:200])
        else:
            check("C15 lag_dd_pack có ở DCF_OS_LAG_DD_PACK", False, LAG_DD_PACK)
    finally:
        osd.oshares_for = real
        _ev_clear()
        dv.OSHARES_SOURCE = "fin"


def _series(rows):
    return lambda t, pdt, n: [(d, p) for d, p in rows if d <= pdt][:n + 1]


def c16_price_run():
    """Việc 5: vendor lặp Price cũ qua ex-date ⇒ khung khoá mở về đầu chuỗi lặp. Ca tổng hợp: ISS thưởng 50%
    ex 2026-10-28 (executed); Price đứng 60.000 từ 10-27 tới 10-29 (vendor ffill giá TRƯỚC ex); caller khai
    price_date=10-29, asof=10-30. Không có guard: số CP 10-29 = 10-30 (cùng sau ex) và [10-29, 10-30] không có
    ex ⇒ khoá OK sai (giá trước ex × số CP sau ex)."""
    import dcf_valuation as dv
    fin = dv._load_financials()
    real, real_ps = osd.oshares_for, dv._price_series
    _ev_fixture([iss("2026-10-28", 0.5, BON)])
    try:
        dv.OSHARES_SOURCE = "fin"
        base = dv.fair_value("FPT", "2026-10-30", price=None, fin=fin)
        dv.OSHARES_SOURCE = "live"
        dv._WARNED_ONCE.clear()
        osd.oshares_for = _FakeOS(ex="2026-10-28")
        frozen = [("2026-10-29", 60000.0), ("2026-10-28", 60000.0), ("2026-10-27", 60000.0), ("2026-10-24", 58000.0)]
        dv._price_series = _series(frozen)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-30", price=60000.0, fin=fin, price_date="2026-10-29")
        check("C16 Price lặp qua ex (ffill vendor) -> khung mở về 10-27 -> số quý + kêu",
              r["oshares"] == base["oshares"] and r["oshares_method"] == "FRAME_FALLBACK"
              and "2026-10-27" in (r["oshares_frame_error"] or "") and "lap lai tu 2026-10-27" in err.getvalue(),
              f"{r.get('oshares_frame_error')} | {err.getvalue()[:160]}")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-30", price=61000.0, fin=fin, price_date="2026-10-29")
        check("C16 giá caller KHÁC Price phiên đó -> không suy chuỗi, khoá trên price_date (OK)",
              r["oshares_frame_error"] is None and math.isclose(r["oshares"], base["oshares"] * 1.5), r.get("oshares_frame_error"))
        check("C16/R10 ... nhưng guard tắt PHẢI kêu stderr (giá caller != Price)",
              "gia caller 61000 != Price 60000" in err.getvalue() and "KHONG kiem duoc" in err.getvalue(), err.getvalue()[:200])
        dv._price_series = _series([("2026-10-28", 60000.0), ("2026-10-27", 60000.0)])
        dv._WARNED_ONCE.clear()                     # cùng khoá (FPT, 10-29) với check trên
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = dv.fair_value("FPT", "2026-10-30", price=60000.0, fin=fin, price_date="2026-10-29")
        check("C16/R10 không có dòng Price phiên price_date -> guard tắt + kêu stderr",
              "khong co dong Price phien 2026-10-29" in err.getvalue(), err.getvalue()[:200])
        dv._price_series = _series([("2026-10-29", 60000.0), ("2026-10-28", 59000.0), ("2026-10-27", 40000.0)])
        r = dv.fair_value("FPT", "2026-10-30", price=60000.0, fin=fin, price_date="2026-10-29")
        check("C16 Price có giao dịch thật (không lặp) -> khoá OK", r["oshares_frame_error"] is None, r.get("oshares_frame_error"))
        check("C16 trần chuỗi lặp PRICE_RUN_MAX = 20 phiên", dv.PRICE_RUN_MAX == 20, str(dv.PRICE_RUN_MAX))
        long_run = [(f"2026-10-{29 - i:02d}", 60000.0) for i in range(21)]       # cố định, KHÔNG theo hằng số
        dv._price_series = _series(long_run)
        with contextlib.redirect_stderr(io.StringIO()):
            r = dv.fair_value("FPT", "2026-10-30", price=60000.0, fin=fin, price_date="2026-10-29")
        check("C16 Price lặp 21 phiên (> 20) -> không xác định được phiên thật -> số quý",
              r["oshares_method"] == "FRAME_FALLBACK" and "lap lai >" in (r["oshares_frame_error"] or ""), r.get("oshares_frame_error"))
        exact = long_run[:20]
        dv._price_series = _series(exact)
        _ev_fixture([])
        osd.oshares_for = _FakeOS(ex="2000-01-01")
        r = dv.fair_value("FPT", "2026-10-30", price=60000.0, fin=fin, price_date="2026-10-29")
        check("C16 lặp đúng 20 phiên, đọc hết lịch sử, không sự kiện -> khoá OK",
              r["oshares_frame_error"] is None, r.get("oshares_frame_error"))
        def _boom(*a, **k):
            raise OSError("parquet missing (simulated)")
        dv._price_series = _boom
        with contextlib.redirect_stderr(io.StringIO()):
            r = dv.fair_value("FPT", "2026-10-30", price=60000.0, fin=fin, price_date="2026-10-29")
        check("C16 không đọc được chuỗi Price -> số quý (fail-closed)", r["oshares_method"] == "FRAME_FALLBACK"
              and "chuoi Price" in (r["oshares_frame_error"] or ""), r.get("oshares_frame_error"))
        dv.OSHARES_SOURCE = "fin"
        dv._price_series = _boom
        r = dv.fair_value("FPT", "2026-10-30", price=60000.0, fin=fin, price_date="2026-10-29")
        check("C16 knob fin: không đọc chuỗi Price", r["ok"] and "oshares_method" not in r)
    finally:
        osd.oshares_for, dv._price_series = real, real_ps
        _ev_clear()
        dv.OSHARES_SOURCE = "fin"


CB_SRC = []      # mutant hook M33: [callable trả nguồn custom_basket đã sửa]


def c17_custom_basket_pinned():
    """Việc 4 (chọn (a)): custom_basket ép fin ngay sau import dcf_valuation, trước mọi fair_value(."""
    src = CB_SRC[0]() if CB_SRC else open(os.path.join(HERE, "custom_basket.py"), encoding="utf-8").read()
    imp, pin = "import dcf_valuation as _dcfv\n", "_dcfv.pin_oshares_source_fin(__file__)"
    ok = imp in src and pin in src and src.index(imp) < src.index(pin) < src.index("_dcfv.fair_value(") \
        and src.count("import dcf_valuation") == 1
    check("C17 custom_basket: pin_oshares_source_fin ngay sau import, trước fair_value(", ok)


def c18_probe_tree_pinned():
    """Việc 7 / M22: dựng cây TẠM (symlink *.py + trading_bot của cây test) ≠ PROD và chạy probe trên đó —
    probe không ghim lại cây ⇒ module sau dcf_valuation nạp từ PROD ⇒ đường dẫn lệch. Giết được M22 cả khi
    HERE == PROD (cây canonical), vì cây tạm không bao giờ trùng PROD."""
    out, paths = probe_on_tree(HERE)
    check("C18 probe trên cây tạm ≠ PROD: mọi module nạp từ cây tạm (giết M22 cả trên canonical)",
          out == "ok" and bool(paths) and "oshares_dcf" in paths and all(v == paths["dcf_valuation"] for v in paths.values())
          and paths["dcf_valuation"] != PROD, str(paths))


def probe_on_tree(src_tree):
    import json
    tmp = _mkdtemp()
    for f in os.listdir(src_tree):
        if f.endswith(".py") or f == "trading_bot":
            os.symlink(os.path.join(src_tree, f), os.path.join(tmp, f))
    body = "import oshares_dcf, oshares_pit, corp_action_lib, trading_bot.strategies; out = 'ok'"
    p = subprocess.run([sys.executable, "-c", probe_code(body, here=tmp)], cwd=tmp, capture_output=True, text=True,
                       timeout=300, env={k: v for k, v in os.environ.items() if k != "DCF_OSHARES_SOURCE"})
    try:
        j = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return f"ERR {p.stderr[-200:]}", {}
    paths = {m: v for m, v in j["paths"].items()}
    if "trading_bot.strategies" in paths:
        paths["trading_bot.strategies"] = os.path.dirname(paths["trading_bot.strategies"])
    return j["out"], {m: (tmp if v == tmp else v) for m, v in paths.items()}


_LDP = {}


def _ldp():
    """lag_dd_pack nạp MỘT lần (mutant M39-M41 vá thuộc tính module này)."""
    if "m" not in _LDP:
        import importlib.util
        spec = importlib.util.spec_from_file_location("lag_dd_pack_r10", LAG_DD_PACK)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _LDP["m"] = m
    return _LDP["m"]


def c19_rich_gate_both_counts():
    """R10/việc 1 (killer objection R9): live làm MẤT cờ DCF_RICH sâu (MST ×0,7359) ⇒ vẫn FLAG; live
    THÊM cờ (×1,5) ⇒ FLAG; live thiếu MoS số quý ⇒ fail-closed FLAG; fin không đổi hành vi."""
    import dcf_valuation as dv
    import trading_bot.strategies as st
    if not os.path.exists(LAG_DD_PACK):
        check("C19 lag_dd_pack có ở DCF_OS_LAG_DD_PACK", False, LAG_DD_PACK)
        return
    sys.path.insert(0, HERE)
    m = _ldp()
    codes = lambda d: [f["code"] for f in m.basic_flags({"valuation": {"dcf": d, "text": "t"}})]   # noqa: E731
    fin = dv._load_financials()
    real = osd.oshares_for
    _ev_fixture([])
    try:
        dv.OSHARES_SOURCE = "fin"
        fv_fin = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)["fair_value_ps"]
        cases = {}
        tol0 = dv.LIVE_BELOW_FIN_TOL          # cô lập việc 1: tắt guard việc 2 (C20) để live < quý tới được cổng
        dv.LIVE_BELOW_FIN_TOL = 1.0
        for tag, mult, k in (("mst", 0.7359, 2.3), ("rev", 1.5, 1.6)):
            px = round(fv_fin * k)
            dv.OSHARES_SOURCE = "fin"
            d_f = st._dcf_check_for_order("FPT", px, "2026-10-29", price_date="2026-10-28")
            dv.OSHARES_SOURCE = "live"
            osd.oshares_for = _FakeOS(ex="2000-01-01", mult=mult)
            with contextlib.redirect_stderr(io.StringIO()):
                d_l = st._dcf_check_for_order("FPT", px, "2026-10-29", price_date="2026-10-28")
            cases[tag] = (d_f, d_l)
        dv.LIVE_BELOW_FIN_TOL = tol0
        d_f, d_l = cases["mst"]
        check("C19 ca MST (×0,7359, giá 2,3×FV quý): fin RICH sâu, live chỉ RICH nhẹ (tiền đề)",
              d_f["margin_of_safety"] < -1 and -1 <= d_l["margin_of_safety"] < 0
              and math.isclose(d_l.get("margin_of_safety_fin") or 0, d_f["margin_of_safety"], abs_tol=2e-4),
              f"fin {d_f['margin_of_safety']} live {d_l['margin_of_safety']} live_fin {d_l.get('margin_of_safety_fin')}")
        check("C19 ca MST: live làm mất cờ ⇒ basic_flags VẪN DCF_RICH (fail-closed theo số quý)",
              "DCF_RICH" in codes(d_l) and "DCF_RICH" in codes(d_f), str(codes(d_l)))
        ev = [f["evidence"] for f in m.basic_flags({"valuation": {"dcf": d_l, "text": "t"}}) if f["code"] == "DCF_RICH"]
        check("C19 ca MST: bằng chứng nói rõ 'SỐ QUÝ' + 2 số OShares", ev and "SỐ QUÝ" in ev[0] and "vs quý" in ev[0], str(ev))
        d_f, d_l = cases["rev"]
        check("C19 ca ngược (×1,5, giá 1,6×FV quý): live THÊM cờ ⇒ DCF_RICH; fin không cờ",
              "DCF_RICH" in codes(d_l) and "DCF_RICH" not in codes(d_f), f"{codes(d_l)} / {codes(d_f)}")
        check("C19 live thiếu margin_of_safety_fin (CHEAP live) ⇒ fail-closed DCF_RICH",
              "DCF_RICH" in codes({"status": "CHEAP", "margin_of_safety": 0.3, "oshares_source": "oshares_live",
                                   "oshares": 1.0, "oshares_fin": 1.2, "oshares_divergence": -0.17}), "")
        check("C19 live CHEAP cả hai số ⇒ không cờ",
              "DCF_RICH" not in codes({"status": "CHEAP", "margin_of_safety": 0.3, "margin_of_safety_fin": 0.1,
                                       "oshares_source": "oshares_live", "oshares_divergence": -0.2}), "")
        check("C19 fin dict (không oshares_*) CHEAP ⇒ không cờ; RICH sâu ⇒ cờ (hành vi cũ)",
              "DCF_RICH" not in codes({"status": "CHEAP", "margin_of_safety": 0.3})
              and "DCF_RICH" in codes({"status": "RICH", "margin_of_safety": -1.5}), "")
    finally:
        osd.oshares_for = real
        _ev_clear()
        dv.OSHARES_SOURCE = "fin"


def c20_live_below_fin():
    """R10/việc 2: số CP sống < số quý (không biết bên nào đúng: ISS không theo tỷ lệ vendor ghi trễ, HOẶC
    dòng quý ghi đè số CP về sau — MST 2025-10-29 ×0,7359) ⇒ số CP LỚN hơn = số quý, method LIVE_BELOW_FIN,
    kêu stderr; dung sai 0,5%; chiều live > quý giữ live."""
    import dcf_valuation as dv
    import trading_bot.strategies as st
    fin = dv._load_financials()
    real = osd.oshares_for
    _ev_fixture([])
    try:
        dv.OSHARES_SOURCE = "fin"
        b = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin)
        dv.OSHARES_SOURCE = "live"
        got = {}
        for mult in (0.7359, 0.99, 0.996, 1.5):
            dv._WARNED_ONCE.clear()
            osd.oshares_for = _FakeOS(ex="2000-01-01", mult=mult)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                r = dv.fair_value("FPT", "2026-10-29", price=100000.0, fin=fin, price_date="2026-10-28")
                r0 = dv.fair_value("FPT", "2026-10-29", fin=fin)           # không giá
            got[mult] = (r, r0, err.getvalue())
        r, r0, e = got[0.7359]
        check("C20 ca MST ×0,7359 (có giá + không giá): dùng SỐ QUÝ, method LIVE_BELOW_FIN, FV = fin",
              r["oshares"] == b["oshares"] and r.get("oshares_method") == "LIVE_BELOW_FIN"
              and r0["oshares"] == b["oshares"] and r0.get("oshares_method") == "LIVE_BELOW_FIN"
              and math.isclose(r["fair_value_ps"], b["fair_value_ps"], rel_tol=1e-12),
              f"{r.get('oshares_method')} {r['oshares']} vs {b['oshares']}")
        check("C20 ... kêu stderr 'OShares live … < quy … SO QUY' đúng 1 lần/mã/asof",
              e.count("!!!!! [dcf_valuation] DCF_OSHARES_SOURCE=live FPT asof=2026-10-29: OShares live") == 1
              and "< quy" in e and "(-26%)" in e and "SO QUY" in e, e[:300])
        check("C20 live −1% (> dung sai 0,5%) ⇒ số quý", got[0.99][0].get("oshares_method") == "LIVE_BELOW_FIN",
              str(got[0.99][0].get("oshares_method")))
        check("C20 live −0,4% (≤ dung sai, làm tròn) ⇒ giữ live",
              got[0.996][0].get("oshares_method") == "FAKE" and got[0.996][0]["oshares"] < b["oshares"],
              str(got[0.996][0].get("oshares_method")))
        check("C20 live ×1,5 (thưởng chưa vào BCTC — lý do có live) ⇒ giữ live",
              got[1.5][0].get("oshares_method") == "FAKE" and math.isclose(got[1.5][0]["oshares"], 1.5 * b["oshares"]),
              str(got[1.5][0].get("oshares_method")))
        if os.path.exists(LAG_DD_PACK):
            m = _ldp()
            px = round(b["fair_value_ps"] * 2.3)
            osd.oshares_for = _FakeOS(ex="2000-01-01", mult=0.7359)
            with contextlib.redirect_stderr(io.StringIO()):
                d = st._dcf_check_for_order("FPT", px, "2026-10-29", price_date="2026-10-28")
            check("C20 đầu-cuối ca MST (giá 2,3×FV quý): live về số quý ⇒ DCF_RICH vẫn cờ",
                  d.get("oshares_method") == "LIVE_BELOW_FIN"
                  and "DCF_RICH" in [f["code"] for f in m.basic_flags({"valuation": {"dcf": d, "text": "t"}})], str(d)[:200])
    finally:
        osd.oshares_for = real
        _ev_clear()
        dv.OSHARES_SOURCE = "fin"


SUITE = [c1_classifier, c2_no_announced_branch, c3_oshares_for, c4_knob, c6_source_of_truth, c7_frame_lock,
         c8_ops_block, c9_research_pinned, c10_oshares_error, c11_callers, c12_module_paths,
         c13_unexecuted, c14_no_bq_without_price_date, c15_divergence, c16_price_run, c17_custom_basket_pinned,
         c18_probe_tree_pinned, c19_rich_gate_both_counts,
         c20_live_below_fin]


def run_suite(with_bq=False, quiet=False):
    FAILS.clear()
    sink = io.StringIO() if quiet else sys.stdout
    with contextlib.redirect_stdout(sink):
        for f in SUITE + ([c5_bq] if with_bq else []):
            print(f"[{f.__name__}]")
            try:
                f()
            except Exception as e:                   # noqa: BLE001 — một check crash = FAIL (mutant bị giết)
                check(f"{f.__name__} không raise", False, f"{type(e).__name__}: {str(e)[:120]}")
    return list(FAILS)


def _mut_div_as_share(evs):
    return [{**e, "event_code": "ISS", "issue_method_name_vi": SD} if e.get("event_code") == "DIV" else e for e in evs]


class _LdpProxyMeta(type):
    """Mutant R10 vá thuộc tính của lag_dd_pack nạp động (_ldp()) qua getattr/setattr trên lớp này."""
    def __getattr__(cls, a):
        return getattr(_ldp(), a)

    def __setattr__(cls, a, v):
        setattr(_ldp(), a, v)


class _LdpProxy(metaclass=_LdpProxyMeta):
    pass


import trading_bot.strategies as _st     # noqa: E402 — mutant M20 vá module này
import trading_bot.due_diligence as _dd  # noqa: E402 — mutant M21
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
    # ---- R8
    "M15 H1 bỏ khoá lịch ex-date (frame_events luôn rỗng)": (osd, "frame_events", lambda real: lambda t, a, b: []),
    "M16 H1 cửa sổ lịch loại trừ price_date (ex == price_date lọt)": (osd, "frame_events", lambda real: lambda t, a, b:
        [e for e in real(t, a, b) if e["exright_date"] > a]),
    "M17 H1 lỗi đọc lịch bị nuốt thành 'không sự kiện'": (osd, "frame_events", lambda real: lambda t, a, b:
        _swallow(real, t, a, b)),
    "M18 H2 ERROR không kêu": (dv, "_shout_once", lambda real: lambda k, m:
        None if (isinstance(k, tuple) and k[0] == "oshares_error") else real(k, m)),
    "M19 H2 dedupe toàn cục thay vì theo mã": (dv, "_shout_once", lambda real: lambda k, m:
        real(("oshares_error",) if (isinstance(k, tuple) and k[0] == "oshares_error") else k, m)),
    "M20 H4 _dcf_check_for_order bỏ price_date": (_st, "_dcf_check_for_order", lambda real: lambda t, p, a, price_date=None:
        real(t, p, a)),
    "M21 H4 _ref_price_session khai ngày cả khi rơi về Close": (_dd, "_ref_price_session", lambda real: lambda t, a:
        (real(t, a)[0], "2026-10-28")),
    "M22 H3 probe không ghim lại HERE sau import dcf_valuation": (sys.modules[__name__], "PIN", lambda real: [""]),
    "M23 H6 ops: bỏ quét file ngoài cây": (sys.modules[__name__], "OPS_BLOCK", lambda real: [
        lambda: ops_block().replace("for _fp in _os_ext:", "for _fp in []:")]),
    "M24 H6 ops: bỏ quét môi trường tiến trình": (sys.modules[__name__], "OPS_BLOCK", lambda real: [
        lambda: ops_block().replace('os.path.join(_os_proc, "[0-9]*", "environ")', 'os.path.join(_os_proc, "nomatch")')]),
    # ---- R9 (job Taylor_20261031_042224)
    "M25 v1 bỏ kiểm ISS chưa executed (luôn rỗng)": (osd, "unexecuted_events", lambda real: lambda t, a, **k: []),
    "M26 v1 lookback 0 ngày (chỉ ex == asof)": (osd, "unexecuted_events", lambda real: lambda t, a, **k: real(t, a, lookback_days=0)),
    "M27 v1 tính cả ISS đã executed": (osd, "unexecuted_events", lambda real: lambda t, a, **k:
        [e for e in (osd._EV_CACHE["rows"] or []) if e.get("ticker") == t and e.get("event_code") == "ISS"
         and e.get("exright_date", "") <= a] or real(t, a, **k)),
    "M28 v1 lỗi đọc lịch chưa executed bị nuốt": (osd, "unexecuted_events", lambda real: lambda t, a, **k: _swallow(real, t, a)),
    "M29 v3 gọi oshares_for TRƯỚC khi kiểm price_date (thứ tự R8)": (dv, "_live_oshares", lambda real: lambda t, a, p, pdt, f:
        (_swallow(osd.oshares_for, t, a.date().isoformat(), f), real(t, a, p, pdt, f))[1]),
    "M30 v2 ngưỡng lệch OShares 1000%": (dv, "OSHARES_DIVERGENCE_WARN", lambda real: 10.0),
    "M31 v2 format_dcf_check không in lệch OShares": (_st, "_format_oshares_divergence", lambda real: lambda d: ""),
    "M32 v2 fair_value không kêu stderr khi lệch": (dv, "_shout_once", lambda real: lambda k, m:
        None if (isinstance(k, tuple) and k[0] == "oshares_div") else real(k, m)),
    "M33 v4 custom_basket bỏ ép fin": (sys.modules[__name__], "CB_SRC", lambda real: [
        lambda: open(os.path.join(HERE, "custom_basket.py"), encoding="utf-8").read().replace(
            "_dcfv.pin_oshares_source_fin(__file__)", "pass")]),
    "M34 v5 bỏ guard Price lặp (giữ price_date)": (dv, "_price_run_start", lambda real: lambda t, pdt, p: (pdt, None)),
    "M35 v5 chuỗi lặp vượt trần vẫn nhận": (dv, "PRICE_RUN_MAX", lambda real: 10 ** 6),
    "M36 v5 lỗi đọc chuỗi Price bị nuốt (giữ price_date)": (dv, "_price_run_start", lambda real: lambda t, pdt, p:
        _swallow2(real, (pdt, None), t, pdt, p)),
    "M37 v6 ops: settings JSON đọc như văn bản (regex dòng)": (sys.modules[__name__], "OPS_BLOCK", lambda real: [
        lambda: ops_block().replace('if _fp.endswith(".json"):', 'if False:')]),
    "M38 v6 ops: không gắn cờ research override": (sys.modules[__name__], "OPS_BLOCK", lambda real: [
        lambda: ops_block().replace('"[research override] " if _res else', '"[LAUNCHER] " if _res else')]),
    # ---- R10
    "M39 r10 cổng DCF_RICH chỉ nhìn số live": (_LdpProxy, "_rich_deep_fin", lambda real: lambda d: (False, "")),
    "M40 r10 live thiếu MoS số quý không fail-closed": (_LdpProxy, "_rich_deep_fin", lambda real: lambda d:
        (False, "") if not isinstance(d, dict) or d.get("margin_of_safety_fin") is None else real(d)),
    "M41 r10 'số quý' lấy nhầm MoS live": (_LdpProxy, "_rich_deep_fin", lambda real: lambda d:
        real({**d, "margin_of_safety_fin": d.get("margin_of_safety")}) if isinstance(d, dict) else real(d)),
    "M45 r10 ops: settings JSON bỏ quét hooks/statusLine command": (sys.modules[__name__], "OPS_BLOCK", lambda real: [
        lambda: ops_block().replace('for _c in _cmds:', 'for _c in []:')]),
    "M46 r10 guard Price lặp tắt im lặng": (dv, "_shout_once", lambda real: lambda k, m:
        None if isinstance(k, tuple) and k and k[0] == "price_run_skip" else real(k, m)),
    "M42 r10 tắt guard live < quý": (dv, "LIVE_BELOW_FIN_TOL", lambda real: 1.0),
    "M43 r10 guard áp cả chiều live > quý": (dv, "LIVE_BELOW_FIN_TOL", lambda real: -1.0),
    "M44 r10 dung sai 50% (MST −26% lọt)": (dv, "LIVE_BELOW_FIN_TOL", lambda real: 0.5),
}


def _swallow2(f, default, *a):
    try:
        return f(*a)
    except Exception:                                # noqa: BLE001 — chính là lỗi mutant M36 mô phỏng
        return default


def _swallow(f, *a):
    try:
        return f(*a)
    except Exception:                                # noqa: BLE001 — chính là lỗi mutant M17 mô phỏng
        return []


def run_mutants():
    # LAG_TOL là default arg ⇒ vá qua wrapper để mutant thật sự có hiệu lực
    # R10/việc 4: KILLED = có FAIL MỚI so với baseline không-mutant (không chỉ bool(fails)) — một check
    # FAIL sẵn (môi trường) không được tính là giết mutant.
    base = set(run_suite(quiet=True))
    if base:
        print(f"  [baseline] {len(base)} FAIL sẵn không tính: {sorted(base)[:3]}")
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
        new = [f for f in fails if f not in base]
        killed = bool(new)
        ok &= killed
        print(f"  {'KILLED' if killed else 'SURVIVED'}  {name}" + (f" ({len(new)} FAIL mới: {new[0]})" if new else ""))
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
