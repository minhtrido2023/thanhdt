#!/usr/bin/env python3
"""Selfcheck rating_8l_forward_tracker.py — dữ liệu tự dựng, không chạm BQ/data thật.
Chạy:  $DNA_PYEXE mike/bin/rating_8l_forward_tracker_selfcheck.py            (test)
       $DNA_PYEXE mike/bin/rating_8l_forward_tracker_selfcheck.py --mutants  (test + mutation: mỗi mutant phải FAIL)
Nên chạy dưới `env -u TZ` VÀ `TZ=America/New_York` (first_seen phải luôn +0700)."""
import importlib.util
import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("R8F_SRC", os.path.join(HERE, "rating_8l_forward_tracker.py"))
spec = importlib.util.spec_from_file_location("r8f", SRC)
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
N_OK = 0


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def D(s):
    return pd.Timestamp(s)


def t_detect():
    fa = pd.DataFrame([
        # ticker, time(eff), route, rating
        ("A", "2026-05-02", "X", 4), ("A", "2026-08-10", "X", 3),   # G1
        ("B", "2026-05-02", "X", 2), ("B", "2026-08-11", "X", 2),   # G0
        ("C", "2026-05-02", "X", 3), ("C", "2026-08-12", "X", 5),   # G2
        ("H", "2026-05-02", "X", 5), ("H", "2026-08-13", "X", 4),   # G3 (5→4)
        ("K", "2026-04-29", "X", 4), ("K", "2026-07-31", "X", 3),   # eff = mốc ⇒ KHÔNG lấy
        ("E", "2026-05-02", "X", 4), ("E", "2026-08-14", "X", 3),   # RD ≤ RD quý trước ⇒ definite
        ("F", "2026-08-01", "X", 3), ("F", "2026-10-03", "X", 3),   # Q3 RD 3 ngày sau cuối quý ⇒ early7
        ("Q", "2026-08-01", "X", 3), ("Q", "2026-09-30", "X", 3),   # RD == cuối quý ⇒ early7, KHÔNG definite
        ("G", "2026-05-02", "X", 4), ("G", "2026-08-20", "X", 3),   # RD NULL ⇒ eff = time, x_null
        ("Z", "2026-08-25", "X", 1),                                 # forensic/không có dòng tf ⇒ bỏ
    ], columns=["ticker", "time", "route", "rating"])
    fa["time"] = pd.to_datetime(fa.time)
    tf = pd.DataFrame([
        ("A", "2026Q1", "2026-05-02", "2026-05-02"), ("A", "2026Q2", "2026-08-10", "2026-08-10"),
        ("B", "2026Q1", "2026-05-02", "2026-05-02"), ("B", "2026Q2", "2026-08-11", "2026-08-11"),
        ("C", "2026Q1", "2026-05-02", "2026-05-02"), ("C", "2026Q2", "2026-08-12", "2026-08-12"),
        ("H", "2026Q1", "2026-05-02", "2026-05-02"), ("H", "2026Q2", "2026-08-13", "2026-08-13"),
        ("K", "2026Q1", "2026-04-29", "2026-04-29"), ("K", "2026Q2", "2026-07-31", "2026-07-31"),
        ("E", "2026Q1", "2026-08-20", "2026-08-20"), ("E", "2026Q2", "2026-08-14", "2026-08-14"),
        ("F", "2026Q2", "2026-08-01", "2026-08-01"), ("F", "2026Q3", "2026-10-03", "2026-10-03"),
        ("Q", "2026Q2", "2026-08-01", "2026-08-01"), ("Q", "2026Q3", "2026-09-30", "2026-09-30"),
        ("G", "2026Q1", "2026-05-02", "2026-05-02"), ("G", "2026Q2", "2026-08-20", None),
    ], columns=["ticker", "quarter", "time", "Release_Date"])
    tf["time"] = pd.to_datetime(tf.time)
    tf["Release_Date"] = pd.to_datetime(tf.Release_Date)
    ev = T.detect_events(fa, tf, set(), "2026-10-20T13:00:00+0700")
    g = dict(zip(ev.ticker, ev.grp))
    ok(g.get("A") == "G1" and g.get("B") == "G0" and g.get("C") == "G2" and g.get("H") == "G3", f"nhóm sai {g}")
    ok("K" not in g, "eff == 2026-07-31 phải bị loại (cần eff > mốc)")
    ok("Z" not in g, "dòng không khớp ticker_financial phải bị bỏ")
    r = ev.set_index("ticker")
    ok(bool(r.loc["E", "x_definite"]) and bool(r.loc["E", "excl"]), "E: RD ≤ RD quý trước ⇒ x_definite")
    ok(bool(r.loc["F", "x_early7"]) and not bool(r.loc["F", "x_definite"]), "F: early7")
    ok(bool(r.loc["Q", "x_early7"]) and not bool(r.loc["Q", "x_definite"]), "Q: RD == cuối quý ⇒ early7, không definite")
    ok(bool(r.loc["G", "x_null"]) and r.loc["G", "eff_date"] == "2026-08-20", "G: RD NULL ⇒ eff = time, x_null")
    ok(not bool(r.loc["A", "excl"]) and r.loc["A", "rating_prev"] == 4 and r.loc["A", "rating_new"] == 3, "A sạch")
    ok((ev.prereg_md5 == T.PREREG_MD5).all(), "thiếu md5 PREREG")
    ev2 = T.detect_events(fa, tf, {("A", "2026Q2")}, "x")
    ok("A" not in set(ev2.ticker) and "B" in set(ev2.ticker), "khoá đã biết phải bị bỏ qua")


def t_gate():
    ok(T.coverage_gate(1200, 700, 686)[0], "1200 mã, phủ 0,98 ⇒ ok")
    ok(not T.coverage_gate(1199, 700, 700)[0], "1199 mã ⇒ fail")
    ok(not T.coverage_gate(1300, 700, 685)[0], "phủ 0,9786 ⇒ fail")
    ok(not T.coverage_gate(1051, 770, 657)[0], "ca thật 2026-10-20 (1051 mã) ⇒ fail")
    ok(not T.coverage_gate(1300, 0, 0)[0] and not T.coverage_gate(None, 700, 700)[0], "thiếu số ⇒ fail-closed")


def _panel(n=150, seed=1):
    rng = np.random.default_rng(seed)
    cal = pd.bdate_range("2026-03-02", periods=n)
    r = pd.DataFrame(rng.normal(0, 0.02, (n, 3)), index=cal, columns=["A", "B", "C"])
    close = 10 * (1 + r).cumprod()
    univ = pd.DataFrame(True, index=cal, columns=close.columns)
    return cal, close, univ


def t_car():
    cal, close, univ = _panel()
    i0 = 70
    ev = pd.DataFrame([dict(ticker="A", quarter="2026Q2", eff_date=cal[i0].strftime("%Y-%m-%d"), grp="G1", excl=False)])
    cars = T.compute_cars(ev, close, univ, dict(px_source="t", px_n_tickers=3, px_univ_cover=1.0), "now")
    ok(len(cars) == 1, "phải tính được 1 CAR")
    ret = close.pct_change()
    b3 = (ret.B + ret.C) / 2                               # B3 LOẠI chính mã A
    ar = ret.A - b3
    exp40 = ar.iloc[i0 + 2:i0 + 41].sum()
    exp20 = ar.iloc[i0 + 2:i0 + 21].sum()
    ok(abs(cars["car[2,40]"].iloc[0] - exp40) < 1e-12, f"CAR[2,40] {cars['car[2,40]'].iloc[0]} != {exp40}")
    ok(abs(cars["car[2,20]"].iloc[0] - exp20) < 1e-12, "CAR[2,20] sai")
    # biên 42 phiên: len(cal) = i0+43 ⇒ tính; i0+42 ⇒ chưa
    c43 = T.compute_cars(ev, close.iloc[:i0 + 43], univ, {"px_source": "t", "px_n_tickers": 3, "px_univ_cover": 1}, "n")
    c42 = T.compute_cars(ev, close.iloc[:i0 + 42], univ, {"px_source": "t", "px_n_tickers": 3, "px_univ_cover": 1}, "n")
    ok(len(c43) == 1 and len(c42) == 0, f"biên 42 phiên sai ({len(c43)}, {len(c42)})")


def t_append():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ev.csv")
        a = pd.DataFrame([dict(ticker="A", quarter="2026Q2", v="1"), dict(ticker="B", quarter="2026Q2", v="2")])
        ok(T.append_only(p, a, ["ticker", "quarter", "v"]) == 2, "lần đầu ghi 2")
        b = pd.DataFrame([dict(ticker="A", quarter="2026Q2", v="999"), dict(ticker="C", quarter="2026Q2", v="3")])
        ok(T.append_only(p, b, ["ticker", "quarter", "v"]) == 1, "chỉ thêm khoá mới")
        x = pd.read_csv(p, dtype=str)
        ok(list(x.v) == ["1", "2", "3"], f"dòng cũ bị sửa/trùng: {list(x.v)}")
        ok(T.append_only(p, b, ["ticker", "quarter", "v"]) == 0, "chạy lại ⇒ 0 dòng (idempotent)")
        ok(not [f for f in os.listdir(d) if ".tmp." in f], "còn file tmp")
        try:
            T.append_only(p, b, ["ticker", "quarter", "w"]); ok(False, "header lệch phải dừng")
        except SystemExit:
            ok(True, "")


def t_main_fail_closed():
    """main với BQ giả: nguồn giá trượt cổng ⇒ KHÔNG tạo file CAR; first_seen luôn +0700."""
    with tempfile.TemporaryDirectory() as d:
        T.EVENTS_CSV, T.CAR_CSV = os.path.join(d, "e.csv"), os.path.join(d, "c.csv")
        fa = pd.DataFrame({"ticker": ["A", "A"], "time": pd.to_datetime(["2026-05-02", "2026-08-10"]),
                           "route": "X", "rating": [4, 3]})
        tf = pd.DataFrame({"ticker": ["A", "A"], "quarter": ["2026Q1", "2026Q2"],
                           "time": pd.to_datetime(["2026-05-02", "2026-08-10"]),
                           "Release_Date": pd.to_datetime(["2026-05-02", "2026-08-10"])})
        T._bq = lambda: None
        T._q = lambda c, sql: fa if "fa_ratings_8l" in sql else tf
        T.price_source = lambda c: (None, None, ["tav2_bq.ticker: số mã 1051 < 1200"])
        sys.argv = ["x"]
        ok(T.main() == 0, "main phải exit 0")
        ok(os.path.exists(T.EVENTS_CSV) and not os.path.exists(T.CAR_CSV), "BLOCKED vẫn tạo CAR csv")
        e = pd.read_csv(T.EVENTS_CSV, dtype=str)
        ok(len(e) == 1 and e.first_seen.iloc[0].endswith("+0700"), f"first_seen không neo ICT: {e.first_seen.tolist()}")


MUTANTS = [
    ("(ev.rating_prev >= 4) & (ev.rating <= 3)", "(ev.rating_prev >= 4) & (ev.rating <= 4)"),
    ("ev = ev[ev.time > EFF_AFTER]", "ev = ev[ev.time >= EFF_AFTER]"),
    ("if n_tickers_latest < MIN_TICKERS:", "if n_tickers_latest <= MIN_TICKERS:"),
    ("if cover < MIN_UNIV_COVER:", "if cover <= MIN_UNIV_COVER:"),
    ("(S_b[sl] - np.where(own, R[sl, j], 0)) / np.maximum(C_b[sl] - 1, 1)", "S_b[sl] / np.maximum(C_b[sl], 1)"),
    ("i0 + NEED_AFTER >= len(cal)", "i0 + WPOST >= len(cal)"),
    ("if tbl is None:", "if False:"),
    ("not in have for t in", "is not None for t in"),
    ('tf["x_definite"] = (lag < 0)', 'tf["x_definite"] = (lag <= 0)'),
    ("dt.datetime.now(ICT)", "dt.datetime.now()"),
    ("tf.Release_Date.fillna(tf.time)", "tf.Release_Date"),
]


def run_mutants():
    src = open(SRC).read()
    killed = 0
    for a, b in MUTANTS:
        if src.count(a) != 1:
            print(f"  MUTANT KHÔNG ÁP ĐƯỢC (chuỗi xuất hiện {src.count(a)} lần): {a}"); sys.exit(1)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(src.replace(a, b)); mp = f.name
        env = dict(os.environ, R8F_SRC=mp)
        r = subprocess.run([sys.executable, __file__], env=env, capture_output=True, text=True)
        os.unlink(mp)
        dead = r.returncode != 0
        killed += dead
        print(f"  {'KILLED' if dead else 'SỐNG  '} {a[:60]!r} → {b[:40]!r}")
    print(f"mutants: {killed}/{len(MUTANTS)} bị bắt")
    return killed == len(MUTANTS)


if __name__ == "__main__":
    want_mut = "--mutants" in sys.argv          # đọc TRƯỚC: t_main_fail_closed ghi đè sys.argv
    for fn in (t_detect, t_gate, t_car, t_append, t_main_fail_closed):
        fn()
    print(f"PASS {N_OK} assertion (TZ={os.environ.get('TZ', '<unset>')})")
    if want_mut:
        sys.exit(0 if run_mutants() else 1)
