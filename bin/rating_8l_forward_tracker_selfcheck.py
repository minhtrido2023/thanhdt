#!/usr/bin/env python3
"""Selfcheck rating_8l_forward_tracker.py — dữ liệu tự dựng, không chạm BQ/data thật.
Chạy:  $DNA_PYEXE mike/bin/rating_8l_forward_tracker_selfcheck.py            (test)
       $DNA_PYEXE mike/bin/rating_8l_forward_tracker_selfcheck.py --mutants  (test + mutation: mỗi mutant phải FAIL)
Nên chạy dưới `env -u TZ` VÀ `TZ=America/New_York` (first_seen phải luôn +0700)."""
import contextlib
import hashlib
import importlib.util
import io
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
_ORIG_PS = T.price_source
_REAL_LOCK = (os.path.join(HERE, "..", "agents/Taylor/research/rating_8l_forward_bt_20261020"), dict(T.LOCKED))
_LOCKDIR = tempfile.mkdtemp(prefix="r8f_lock_")
for _n in T.LOCKED:                              # bản khoá giả cho test main(); md5 thật kiểm riêng ở t_locked
    open(os.path.join(_LOCKDIR, _n), "w").write(_n)
T.LOCK_DIR = _LOCKDIR
T.LOCKED = {n: hashlib.md5(n.encode()).hexdigest() for n in T.LOCKED}


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
    ok(not T.coverage_gate(1051, 343, 343)[0], "ca thật 2026-10-20 (1051 mã, n_un 343) ⇒ fail")
    ok(T.coverage_gate(1300, 343, 343)[0], "n_un thật 343, phủ 1,0, 1300 mã ⇒ ok")
    ok(T.coverage_gate(1300, 300, 300)[0] and not T.coverage_gate(1300, 299, 299)[0], "sàn n_un ≥ 300")
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
        except SystemExit as e:
            ok(str(e.code).startswith("❌"), f"SystemExit phải có tiền tố ❌: {e.code!r}")


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
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = T.main()
        out = buf.getvalue()
        ok(rc == 0, "main phải exit 0")
        ok(out.splitlines()[0].startswith("[rating_8l_forward_tracker]") and "+0700" in out.splitlines()[0],
           f"thiếu header giờ ICT: {out.splitlines()[:1]}")
        ok("❌ BLOCKED" in out, "BLOCKED phải in ❌")
        ok(os.path.exists(T.EVENTS_CSV) and not os.path.exists(T.CAR_CSV), "BLOCKED vẫn tạo CAR csv")
        e = pd.read_csv(T.EVENTS_CSV, dtype=str)
        ok(len(e) == 1 and e.first_seen.iloc[0].endswith("+0700"), f"first_seen không neo ICT: {e.first_seen.tolist()}")
    T.price_source = _ORIG_PS


def t_locked():
    base, locked = _REAL_LOCK
    ok(not T.locked_mismatches(base, locked), f"file khoá thật lệch md5: {T.locked_mismatches(base, locked)}")
    with tempfile.TemporaryDirectory() as d:
        for n in T.LOCKED:
            open(os.path.join(d, n), "w").write(n)
        ok(not T.locked_mismatches(d, T.LOCKED), "bản khớp phải sạch")
        open(os.path.join(d, "PREREG_FORWARD.md"), "a").write("x")
        os.unlink(os.path.join(d, "event_study_v2_frozen.py"))
        bad = T.locked_mismatches(d, T.LOCKED)
        ok(len(bad) == 2, f"phải báo 2 lỗi (lệch + thiếu): {bad}")
        # main: file khoá lệch ⇒ rc≠0, "❌", không ghi ledger, không chạm BQ
        T.EVENTS_CSV, T.CAR_CSV = os.path.join(d, "e.csv"), os.path.join(d, "c.csv")
        T._bq = lambda: (_ for _ in ()).throw(AssertionError("không được chạm BQ khi md5 lệch"))
        T.LOCK_DIR = d
        sys.argv = ["x"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = T.main()
        T.LOCK_DIR = _LOCKDIR
        ok(rc != 0 and "❌" in buf.getvalue(), f"md5 lệch phải dừng với ❌: rc={rc}")
        ok(not os.path.exists(T.EVENTS_CSV) and not os.path.exists(T.CAR_CSV), "md5 lệch vẫn ghi ledger")


def _fake_q(pins, stats, log):
    """_q giả: pins=[tên bảng pin]; stats={bảng: (n_px, n_un, n_cov)}. Tôn trọng ORDER BY ... DESC/ASC và LIMIT 1."""
    def q(c, sql):
        log.append(sql)
        if "INFORMATION_SCHEMA" in sql:
            names = sorted(pins, reverse="DESC" in sql)
            return pd.DataFrame({"table_name": names[:1] if "LIMIT 1" in sql else names})
        for tbl, (n_px, n_un, n_cov) in stats.items():
            if f"FROM {tbl} " in sql:
                return pd.DataFrame([dict(d="2026-10-19", n_px=n_px, n_un=n_un, n_cov=n_cov)])
        raise AssertionError(f"SQL lạ: {sql[:80]}")
    return q


def t_price_source():
    good, bad_ = (1300, 343, 340), (1051, 343, 343)
    P6, P9 = "ticker_pin_202606", "ticker_pin_202609"
    T._q = _fake_q([P6, P9], {"tav2_bq.ticker": good, f"tav2_pin.{P6}": good, f"tav2_pin.{P9}": good}, [])
    ok(T.price_source(None)[0] == "tav2_bq.ticker", "live qua cổng ⇒ chọn live")
    T._q = _fake_q([P6, P9], {"tav2_bq.ticker": bad_, f"tav2_pin.{P6}": good, f"tav2_pin.{P9}": good}, [])
    tbl, meta, tried = T.price_source(None)
    ok(tbl == f"tav2_pin.{P9}", f"live trượt ⇒ pin MỚI NHẤT (DESC), được {tbl}")
    ok(meta["px_source"].startswith(tbl) and meta["px_n_tickers"] == 1300 and len(tried) == 2, f"meta/tried sai {meta} {tried}")
    T._q = _fake_q([P6, P9], {"tav2_bq.ticker": bad_, f"tav2_pin.{P9}": bad_}, [])
    tbl, meta, tried = T.price_source(None)
    ok(tbl is None and meta is None and len(tried) == 2, f"live + pin đều trượt ⇒ None: {tbl}")
    T._q = _fake_q([], {"tav2_bq.ticker": bad_}, [])
    ok(T.price_source(None)[0] is None, "live trượt, không có pin ⇒ None")


def _world(events, seed=3):
    """BQ giả cho main(): events = [(ticker, giữ-giá-từ-index|None, bỏ-giá-các-index)]. Trả (fa, tf, px, un, clean_close)."""
    rng = np.random.default_rng(seed)
    cal = pd.bdate_range("2026-03-02", periods=200)
    names = [f"T{i:03d}" for i in range(120)] + [e[0] for e in events]
    close = pd.DataFrame(10 * (1 + rng.normal(0, 0.02, (len(cal), len(names)))).cumprod(0), index=cal, columns=names)
    for t, start, gaps in events:
        if start:
            close.loc[cal[:start], t] = np.nan
        close.loc[[cal[g] for g in gaps], t] = np.nan
    px = close.stack().rename("Close").reset_index()
    px.columns = ["time", "ticker", "Close"]
    stray = pd.DataFrame({"time": pd.Timestamp("2026-08-15"), "ticker": [events[0][0], "T000", "T001"], "Close": [99.0, 1.0, 2.0]})
    px = pd.concat([px, stray], ignore_index=True)           # ngày lẻ chỉ 3 mã (thứ Bảy) ⇒ phải bị lọc khỏi lịch
    un = pd.DataFrame([(t, d) for d in cal for t in names], columns=["ticker", "time"])
    fa = pd.DataFrame([(t, d, "X", r) for t in [e[0] for e in events] for d, r in (("2026-05-02", 4), ("2026-08-10", 3))],
                      columns=["ticker", "time", "route", "rating"])
    fa["time"] = pd.to_datetime(fa.time)
    tf = pd.DataFrame([(t, q, d, d) for t in [e[0] for e in events]
                       for q, d in (("2026Q1", "2026-05-02"), ("2026Q2", "2026-08-10"))],
                      columns=["ticker", "quarter", "time", "Release_Date"])
    tf["time"], tf["Release_Date"] = pd.to_datetime(tf.time), pd.to_datetime(tf.Release_Date)
    return fa, tf, px, un, close, cal


def _run_main(d, fa, tf, px, un):
    T.EVENTS_CSV, T.CAR_CSV = os.path.join(d, "e.csv"), os.path.join(d, "c.csv")
    log = []
    stats = {"tav2_bq.ticker": (1051, 343, 343), "tav2_pin.ticker_pin_202609": (1300, 343, 343)}
    base = _fake_q(["ticker_pin_202609"], stats, log)

    def q(c, sql):
        if "fa_ratings_8l" in sql:
            return fa
        if "ticker_financial" in sql:
            return tf
        if "p.Close" in sql:
            log.append(sql)
            return px
        if sql.lstrip().startswith("SELECT u.ticker, u.time"):
            return un
        return base(c, sql)
    T._bq, T._q = (lambda: None), q
    sys.argv = ["x"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = T.main()
    return rc, buf.getvalue(), log


def t_main_e2e():
    # (1) sự kiện sạch: tính CAR đúng 1 dòng; chạy lại ⇒ 0 dòng; nguồn giá = pin (live trượt cổng)
    fa, tf, px, un, close, cal = _world([("A", None, [])])
    with tempfile.TemporaryDirectory() as d:
        rc, out, log = _run_main(d, fa, tf, px, un)
        ok(rc == 0, f"main rc {rc}: {out}")
        c = pd.read_csv(T.CAR_CSV, dtype=str)
        ok(len(c) == 1 and c.ticker.iloc[0] == "A", f"phải ghi đúng 1 dòng CAR: {len(c)}")
        ok(c.px_source.iloc[0].startswith("tav2_pin.ticker_pin_202609"), f"nguồn giá phải là pin: {c.px_source.iloc[0]}")
        ok(any("tav2_pin.ticker_pin_202609" in s and "p.Close" in s for s in log), "truy vấn giá không đi qua pin")
        ev = pd.DataFrame([dict(ticker="A", quarter="2026Q2", eff_date="2026-08-10", grp="G1", excl=False)])
        exp = T.compute_cars(ev, close, un.assign(v=True).pivot(index="time", columns="ticker", values="v"),
                             dict(px_source="t", px_n_tickers=1, px_univ_cover=1), "n")
        for k in ("car[2,20]", "car[2,40]"):
            ok(abs(float(c[k].iloc[0]) - exp[k].iloc[0]) < 1e-12, f"{k} lệch kỳ vọng (lịch phải loại ngày lẻ <100 mã)")
        ok(c.session0.iloc[0] == exp.session0.iloc[0], "session0 lệch")
        rc2, out2, _ = _run_main(d, fa, tf, px, un)
        ok(len(pd.read_csv(T.CAR_CSV, dtype=str)) == 1 and len(pd.read_csv(T.EVENTS_CSV, dtype=str)) == 1,
           "chạy lại lần 2 phải ghi 0 dòng")
    # (2) thiếu giá giữa cửa sổ + niêm yết muộn ⇒ vẫn ghi, n_obs_win nhỏ, CAR hữu hạn
    cal0 = pd.bdate_range("2026-03-02", periods=200)
    i0 = int(cal0.searchsorted(pd.Timestamp("2026-08-10")))
    fa, tf, px, un, close, cal = _world([("M", i0 - 40, [i0 + 5, i0 + 6, i0 + 7])])
    with tempfile.TemporaryDirectory() as d:
        rc, out, _ = _run_main(d, fa, tf, px, un)
        c = pd.read_csv(T.CAR_CSV, dtype=str)
        ok(len(c) == 1, f"ca thiếu giá vẫn phải ghi 1 dòng: {out}")
        ok(int(c.n_obs_win.iloc[0]) == 78 and np.isfinite(float(c["car[2,40]"].iloc[0])),
           f"n_obs_win nhỏ + CAR hữu hạn: {c.n_obs_win.iloc[0]} {c['car[2,40]'].iloc[0]}")


def t_dups():
    fa = pd.DataFrame([("D", "2026-05-02", "X", 4), ("D", "2026-08-10", "X", 3),
                       ("E", "2026-05-02", "X", 4), ("E", "2026-08-10", "X", 3), ("E", "2026-08-10", "Y", 3)],
                      columns=["ticker", "time", "route", "rating"])
    fa["time"] = pd.to_datetime(fa.time)
    tf = pd.DataFrame([("D", "2026Q1", "2026-08-10", "2026-08-10"), ("D", "2026Q2", "2026-08-10", "2026-08-10"),   # vendor chép RD
                       ("E", "2026Q1", "2026-05-02", "2026-05-02"), ("E", "2026Q2", "2026-08-10", "2026-08-10")],
                      columns=["ticker", "quarter", "time", "Release_Date"])
    tf["time"], tf["Release_Date"] = pd.to_datetime(tf.time), pd.to_datetime(tf.Release_Date)
    ev = T.detect_events(fa, tf, set(), "x")
    ok(list(ev[ev.ticker == "D"].quarter) == ["2026Q2"], f"(ticker,eff) trùng ⇒ giữ quý SAU: {ev.to_dict('records')}")
    ok(len(ev[ev.ticker == "E"]) == 1, "dòng fa trùng (ticker,time) ⇒ 1 sự kiện")


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
    ("ORDER BY table_name DESC LIMIT 1", "ORDER BY table_name ASC LIMIT 1"),
    ("coverage_gate(int(s.n_px), int(s.n_un)", "coverage_gate(int(s.n_px) * 10, int(s.n_un)"),
    ("close = close[close.notna().sum(axis=1) >= 100]", "close = close"),
    ("ar = np.where(np.isnan(r), 0.0, r - b3)", "ar = r - b3"),
    ('tf = tf.sort_values("qend").drop_duplicates(["ticker", "eff"], keep="last")', 'tf = tf.sort_values("qend")'),
    ('ev = ev.drop_duplicates(["ticker", "quarter"], keep="first")', "pass"),
    ("if known_keys:", "if False:"),
    ("if bad:", "if False:"),
    ("if n_univ_latest < MIN_UNIV_N:", "if False:"),
    ("❌ BLOCKED", "BLOCKED"),
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
    for fn in (t_detect, t_dups, t_gate, t_car, t_append, t_locked, t_price_source, t_main_fail_closed, t_main_e2e):
        fn()
    print(f"PASS {N_OK} assertion (TZ={os.environ.get('TZ', '<unset>')})")
    if want_mut:
        sys.exit(0 if run_mutants() else 1)
