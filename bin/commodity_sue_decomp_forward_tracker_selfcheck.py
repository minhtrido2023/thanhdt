#!/usr/bin/env python3
"""Selfcheck commodity_sue_decomp_forward_tracker.py (+ review). Logic dựng tay; riêng t_repro đọc dữ liệu thật (read-only).
Chạy:  $DNA_PYEXE mike/bin/commodity_sue_decomp_forward_tracker_selfcheck.py            (test)
       $DNA_PYEXE mike/bin/commodity_sue_decomp_forward_tracker_selfcheck.py --mutants  (test + mutation: mỗi mutant phải FAIL)
Nên chạy dưới `env -u TZ` VÀ `TZ=America/New_York`."""
import contextlib
import datetime as dt
import importlib.util
import io
import os
import re
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "agents/Taylor/research/commodity_cycle_te_20261026")
WC = "/home/trido/thanhdt/WorkingClaude"
FORBID = re.compile(r"\d\.\d|\bIC\b|\bmean\b|corr|spearman|\bp=|\bt=|ΔIC|\bTB\b|\bCI\b")
N_OK = 0


def load(src, name="csd"):
    spec = importlib.util.spec_from_file_location(name, src)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.LOCK_DIR = RES                          # mutant chạy ở /tmp
    return m


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def fin_row(**kw):
    base = dict(ticker="AAA", quarter="2026Q4", Release_Date=pd.Timestamp("2027-01-20"), NP_P0=np.nan, NP_P1=np.nan,
                NP_P2=np.nan, NP_P3=np.nan, NP_P4=np.nan, Revenue_P4=np.nan)
    base.update(kw)
    return pd.DataFrame([base]).itertuples().__next__()


CMAP = pd.DataFrame(dict(ticker=["AAA", "BBB", "CCC", "DDD", "EEE"], family=["f1", "f1", "f2", "f2", "f3"],
                         te_metric_key=["k1", "k1", "k2", "k2", "k3"], sign=[1, 1, 1, 1, 1]))


def fixture(seed=3):
    rng = np.random.default_rng(seed)
    tdays = pd.bdate_range("2016-10-03", "2027-01-25")
    te = pd.DataFrame({k: 100 * np.exp(np.cumsum(rng.normal(0, .01, len(tdays)))) for k in ["k1", "k2", "k3"]},
                      index=tdays)
    rows = []
    for t in CMAP.ticker:
        for q in pd.period_range("2016Q1", "2026Q4", freq="Q"):
            np_ = rng.normal(100e9, 30e9, 5)
            rows.append(dict(ticker=t, quarter=str(q), Release_Date=q.end_time.normalize() + pd.Timedelta(days=25),
                             NP_P0=np_[0], NP_P1=np_[1], NP_P2=np_[2], NP_P3=np_[3], NP_P4=np_[4], Revenue_P4=1000e9))
    fin = pd.DataFrame(rows)
    fin.loc[(fin.ticker == "EEE") & (fin.quarter == "2026Q4"), "Release_Date"] = pd.Timestamp("2027-01-05")  # ⇒ LATE
    extra = [dict(ticker="ZZZ", quarter="2026Q4", Release_Date=pd.Timestamp("2027-01-21"), NP_P0=5e9, NP_P1=1e9,
                  NP_P2=1e9, NP_P3=1e9, NP_P4=1e9, Revenue_P4=50e9),
             dict(ticker="YYY", quarter="2026Q4", Release_Date=pd.Timestamp("2027-01-21"), NP_P0=5e9, NP_P1=1e9,
                  NP_P2=1e9, NP_P3=1e9, NP_P4=1e9, Revenue_P4=50e9)]
    fin = pd.concat([fin, pd.DataFrame(extra)], ignore_index=True)
    lagq = pd.DataFrame(dict(ticker=["ZZZ", "AAA"], quarter=["2026Q4", "2026Q4"]))
    days = pd.bdate_range("2026-06-01", "2027-06-30")
    names = list(CMAP.ticker) + ["ZZZ", "YYY", "M1", "M2"]
    close = pd.DataFrame({k: 100 * np.cumprod(1 + rng.normal(0, .01, len(days))) for k in names}, index=days)
    um = pd.Series({d: set(names) - ({"M2"} if d < pd.Timestamp("2027-02-01") else set()) for d in days})
    return te, fin, lagq, close, um


def t_units(T):
    te = pd.DataFrame({"k": [1.0] * 39 + [3.0]}, index=pd.bdate_range("2026-01-01", periods=40))
    qa = T.quarter_avgs(te)
    ok(abs(qa.k.iloc[0] - 1.05) < 1e-12, "TB quý đúng khi đủ 40 quan sát")
    ok(T.quarter_avgs(te.iloc[:39]).k.isna().all(), "< 40 quan sát ⇒ NaN")
    qa = pd.DataFrame({"k": [100., 110., 120., 130., 150.]}, index=pd.period_range("2025Q1", periods=5, freq="Q"))
    cy, cm = T.comm_signals(qa, "k", pd.Period("2026Q1", "Q"))
    ok(abs(cy - np.log(150 / 100)) < 1e-12, "c_yoy = log(Q/Q-4)")
    ok(abs(cm - np.log(150 / 115)) < 1e-12, "c_ma = log(Q / TB(Q-1..Q-4))")
    ok(abs(T.comm_signals(qa, "k", pd.Period("2026Q1", "Q"), -1)[0] + cy) < 1e-12, "dấu −1 lật c")
    ok(all(np.isnan(T.comm_signals(qa, "k", pd.Period("2025Q4", "Q")))), "thiếu Q-4 ⇒ NaN cả hai")
    ok(all(np.isnan(T.comm_signals(qa, "zz", pd.Period("2026Q1", "Q")))), "metric không có ⇒ NaN")
    ok(abs(T.sue1(fin_row(NP_P0=30e9, NP_P4=10e9, Revenue_P4=100e9)) - 0.2) < 1e-12, "sue1 = (P0−P4)/Rev_P4")
    ok(T.sue1(fin_row(NP_P0=300e9, NP_P4=0, Revenue_P4=100e9)) == 0.5, "sue1 cắt +0,5")
    ok(np.isnan(T.sue1(fin_row(NP_P0=3e9, NP_P4=1e9, Revenue_P4=0))), "Revenue_P4 ≤ 0 ⇒ NaN")
    r = fin_row(NP_P0=20e9, NP_P1=10e9, NP_P2=10e9, NP_P3=10e9, NP_P4=10e9)
    ok(abs(T.sue2(r) - 1.0) < 1e-12, "sue2 = (P0 − TB(P1..P4))/|TB|")
    ok(abs(T.sue2(fin_row(NP_P0=0.5e9, NP_P1=0.1e9, NP_P2=0.1e9, NP_P3=0.1e9, NP_P4=0.1e9)) - 0.4) < 1e-12,
       "sue2 sàn mẫu 1e9 (như lag_live_schedule)")
    ok(T.sue2(fin_row(NP_P0=100e9, NP_P1=1e9, NP_P2=1e9, NP_P3=1e9, NP_P4=1e9)) == 5, "sue2 cắt ±5")
    # fit_hat: CHỈ sự kiện cùng họ release < ngày công bố (chặt)
    rel = pd.Timestamp("2027-01-20")
    hist = pd.DataFrame(dict(family="f1", quarter=[f"20{y}Q1" for y in range(17, 27)],
                             release=pd.date_range("2017-04-25", periods=10, freq="365D"),
                             c_yoy=np.arange(10) / 10, sue1=np.arange(10) / 5 + np.r_[0, .1] .repeat(5)))
    sib = pd.DataFrame(dict(family="f1", quarter="2026Q4", release=[rel], c_yoy=[5.0], sue1=[-50.0]))
    fut = pd.DataFrame(dict(family="f1", quarter="2027Q1", release=[rel + pd.Timedelta(days=90)], c_yoy=[9.0],
                            sue1=[90.0]))
    oth = pd.DataFrame(dict(family="f2", quarter="2020Q1", release=[pd.Timestamp("2020-01-01")], c_yoy=[1.0],
                            sue1=[-99.0]))
    H_ = pd.concat([hist, sib, fut, oth], ignore_index=True)
    a, b, n, hat = T.fit_hat(H_, "f1", rel, "c_yoy", "sue1", 0.5)
    bb, aa = np.polyfit(hist.c_yoy, hist.sue1, 1)
    ok(n == 10 and abs(a - aa) < 1e-9 and abs(b - bb) < 1e-9, "OLS tay trên 10 sự kiện quá khứ khớp")
    ok(abs(hat - (aa + bb * 0.5)) < 1e-9, "hat = a + b·c")
    ok(T.fit_hat(H_.iloc[:7], "f1", rel, "c_yoy", "sue1", .5) is None, "< 8 sự kiện ⇒ None")
    h5 = hist.assign(quarter=["2017Q1"] * 5 + ["2018Q1"] * 5)
    ok(T.fit_hat(h5, "f1", rel, "c_yoy", "sue1", .5) is None, "< 6 quý ⇒ None")
    ok(T.fit_hat(hist, "f1", rel, "c_yoy", "sue1", np.nan) is None, "c NaN ⇒ None")
    # classify / LATE
    days = pd.bdate_range("2026-09-01", "2031-12-31")
    ok(T.classify("2026Q2", "2026-07-20", "2026-10-26", days) is None, "quý < 2026Q3 không ghi")
    ok(T.classify("2026Q3", "2026-10-20", "2026-10-26", days) == ("PRE_FREEZE_BACKFILL", False, ["PRE_FREEZE"]),
       "2026Q3 ⇒ PRE_FREEZE counts=False")
    ok(T.classify("2026Q4", "2027-01-20", "2027-01-21", days)[:2] == ("FORWARD", True), "2026Q4 kịp ⇒ FORWARD đếm")
    ok(T.classify("2026Q4", "2027-01-20", "2027-02-03", days)[1] is True, "đúng 10 phiên ⇒ chưa LATE")
    c = T.classify("2026Q4", "2027-01-20", "2027-02-04", days)
    ok(c[1] is False and c[2] == ["LATE"], "11 phiên ⇒ LATE counts=False")
    ok(T.classify("2031Q2", "2031-07-20", "2031-07-21", days) is None, "sau 2031Q1 không ghi")
    ok(T.sessions_between(pd.bdate_range("2027-01-01", "2027-01-10"), "2027-01-05", "2027-01-14") == 7,  # 6,7,8 trong lịch + 11..14
       "đếm phiên vượt quá lịch cache dùng ngày làm việc")
    um = pd.Series({pd.Timestamp("2027-01-18"): {"AAA"}, pd.Timestamp("2027-01-19"): {"BBB"}})
    ok(T.member_at(um, "BBB", "2027-01-20") and not T.member_at(um, "AAA", "2027-01-20"), "universe = phiên cuối ≤ ngày")
    ok(not T.member_at(um, "AAA", "2027-01-01"), "trước lịch universe ⇒ không thành viên")


def t_market(T):
    te, fin, lagq, close, um = fixture()
    mk = T.Market(close, um)
    p = mk.post("AAA", "2027-01-20")
    i = close.index.get_loc(pd.Timestamp("2027-01-21"))
    ok(p["t0"] == "2027-01-21" and p["t60"] == close.index[i + 60].strftime("%Y-%m-%d"), "t0 = phiên đầu ≥ công bố+1 ngày; t60 = +60")
    r = close.pct_change()
    bc = 1.0
    for j in range(i + 1, i + 61):
        mem = [t for t in close.columns if t in um[close.index[j - 1]]]
        bc *= 1 + r.iloc[j][mem].mean()
    ok(abs(p["r_bench"] - (bc - 1)) < 1e-10, "benchmark = kép bình quân đều thành viên t−1 (tính tay)")
    ok(abs(p["post60"] - (close.AAA.iloc[i + 60] / close.AAA.iloc[i] - 1 - (bc - 1))) < 1e-10, "post60 tính tay khớp")
    ok(mk.post("AAA", "2027-05-20") == "pending", "chưa đủ 60 phiên ⇒ pending")
    ok(mk.post("QQQ", "2027-01-20") is None, "không có giá ⇒ None")


def run_pipe(T, d, now, data, extra=()):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = T.main(["--data-dir", d, *extra], data=data, now=now)
    return rc, buf.getvalue()


def t_pipeline(T):
    te, fin, lagq, close, um = fixture()
    mk = T.Market(close, um)
    data = dict(cmap=CMAP, te=te, fin=fin, lagq=lagq, mk=mk)
    now1 = dt.datetime(2027, 1, 26, 19, 30, tzinfo=T.ICT)
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_pipe(T, d, now1, data)
        ev = pd.read_csv(os.path.join(d, "commodity_sue_decomp_forward_events.csv"))
        ok(rc == 0, "chạy lần 1 rc=0")
        ok(not FORBID.search(out), f"stdout KHÔNG có thống kê: {out!r}")
        A3 = ev[(ev.group == "TIER_A") & (ev.quarter == "2026Q3")]
        ok(len(A3) == 5 and A3.status.eq("PRE_FREEZE_BACKFILL").all() and not A3.counts.any(),
           "2026Q3 của 5 mã ⇒ PRE_FREEZE_BACKFILL counts=False")
        A = ev[(ev.group == "TIER_A") & (ev.quarter == "2026Q4")]
        ok(set(A.ticker) == set(CMAP.ticker) and set(ev.quarter) == {"2026Q3", "2026Q4"}, "chỉ quý ≥2026Q3, 5 mã tier A")
        ok(A[A.ticker != "EEE"].counts.all() and A[A.ticker != "EEE"].status.eq("FORWARD").all(), "4 mã kịp ⇒ đếm")
        e = A[A.ticker == "EEE"].iloc[0]
        ok(not e.counts and "LATE" in e.reason, "EEE thấy muộn 15 phiên ⇒ LATE")
        nc = ev[ev.group == "NO_COMMODITY"]
        ok(list(nc.ticker) == ["ZZZ"] and nc.reason.iloc[0] == "EXCLUDED_NO_COMMODITY" and not nc.counts.iloc[0],
           "mã LAG qualify ngoài danh sách ⇒ NO_COMMODITY, loại, có lý do; mã không qualify không ghi")
        ok(int(A[A.ticker == "AAA"].lag_qualify.iloc[0]) == 1 and int(A[A.ticker == "BBB"].lag_qualify.iloc[0]) == 0,
           "cờ lag_qualify đúng")
        # hat của AAA = OLS tay trên sự kiện f1 công bố TRƯỚC 2027-01-20
        qa = T.quarter_avgs(te)
        hist = T.build_hist(fin, CMAP, qa)
        past = hist[(hist.family == "f1") & (hist.release < pd.Timestamp("2027-01-20"))].dropna(subset=["c_yoy", "sue1"])
        bb, aa = np.polyfit(past.c_yoy, past.sue1, 1)
        r = A[A.ticker == "AAA"].iloc[0]
        past = hist[(hist.family == "f1") & (hist.release < pd.Timestamp(r.release_date))].dropna(subset=["c_yoy", "sue1"])
        bb, aa = np.polyfit(past.c_yoy, past.sue1, 1)
        ok(abs(r.sue1_hat - (aa + bb * r.c_yoy)) < 1e-9 and int(r.sue1_nfit) == len(past), "sue1_hat = OLS quá khứ (tay)")
        ok(abs(r.sue1_res - (r.sue1 - r.sue1_hat)) < 1e-12, "res = sue − hat")
        cy, _ = T.comm_signals(qa, "k1", pd.Period("2026Q4", "Q"))
        ok(abs(r.c_yoy - cy) < 1e-12 and pd.notna(r.sue2_hat), "c_yoy ghi đúng, có sue2_hat")
        ok((ev.prereg_md5 == T.PREREG_MD5).all(), "mỗi dòng mang md5 PREREG")
        # lần 2: dữ liệu bị 'restate' + có sự kiện mới ⇒ dòng cũ giữ nguyên, chỉ nối dòng mới
        fin2 = fin.copy()
        fin2.loc[fin2.quarter == "2026Q4", "NP_P0"] *= 3
        fin2 = pd.concat([fin2, pd.DataFrame([dict(ticker="ZZZ", quarter="2027Q1", Release_Date=pd.Timestamp("2027-01-26"),
                                                   NP_P0=1e9, Revenue_P4=1e9)])], ignore_index=True)
        lag2 = pd.concat([lagq, pd.DataFrame(dict(ticker=["ZZZ"], quarter=["2027Q1"]))])
        rc, out = run_pipe(T, d, now1 + dt.timedelta(days=1), {**data, "fin": fin2, "lagq": lag2})
        ev2 = pd.read_csv(os.path.join(d, "commodity_sue_decomp_forward_events.csv"))
        ok(len(ev2) == len(ev) + 1, "lần 2 chỉ nối 1 dòng mới")
        oc1 = pd.read_csv(os.path.join(d, "commodity_sue_decomp_forward_outcomes.csv"))
        ok(set(oc1.quarter) == {"2026Q3"}, "giá có ngày > hôm nay KHÔNG được dùng: 2026Q4 chưa có outcome ở 2027-01-27")
        ok(ev2.iloc[:len(ev)].astype(str).equals(ev.astype(str)), "append-only: dòng cũ không bị ghi đè dù dữ liệu restate")
        ok(not FORBID.search(out), "stdout lần 2 không có thống kê")
        # kết quả: chạy lúc đủ 60 phiên ⇒ có post60 cho sự kiện 2027-01-20
        rc, out = run_pipe(T, d, dt.datetime(2027, 6, 1, 19, 30, tzinfo=T.ICT), {**data, "fin": fin2, "lagq": lag2})
        oc = pd.read_csv(os.path.join(d, "commodity_sue_decomp_forward_outcomes.csv"))
        rel = A[A.ticker == "AAA"].release_date.iloc[0]
        p = mk.post("AAA", rel)
        ok(abs(oc[(oc.ticker == "AAA") & (oc.quarter == "2026Q4")].post60.iloc[0] - p["post60"]) < 1e-12,
           "outcome AAA = Market.post")
        ok(len(oc) == len(ev2) and oc.post60.notna().all(), "đủ 60 phiên ⇒ mọi sự kiện có outcome")
        ok(not FORBID.search(out), "stdout lần 3 (có outcome) không có thống kê")
        n_oc = len(oc)
        run_pipe(T, d, dt.datetime(2027, 6, 2, 19, 30, tzinfo=T.ICT), {**data, "fin": fin2, "lagq": lag2})
        ok(len(pd.read_csv(os.path.join(d, "commodity_sue_decomp_forward_outcomes.csv"))) == n_oc,
           "outcome đã có ⇒ không tính lại")
    with tempfile.TemporaryDirectory() as d2:
        run_pipe(T, d2, now1, data, ["--dry-run"])
        ok(not os.path.exists(os.path.join(d2, "commodity_sue_decomp_forward_events.csv")), "--dry-run không tạo file")
    # _append trực tiếp: khoá trùng không đè dòng cũ
    with tempfile.TemporaryDirectory() as d3:
        p = os.path.join(d3, "x.csv")
        row = lambda v: pd.DataFrame([dict(group="TIER_A", family="f1", quarter="2026Q4", ticker="AAA", t0="", t60="",  # noqa: E731
                                          r_stock=v, r_bench=0, post60=v, note="", computed_at="")])
        T._append(p, row(0.1), T.OUT_COLS)
        T._append(p, row(0.9), T.OUT_COLS)
        x = pd.read_csv(p)
        ok(len(x) == 1 and x.post60.iloc[0] == 0.1, "_append: khoá đã có ⇒ giữ giá trị đầu, không thêm")
    # tín hiệu hàng hoá phải có TRƯỚC công bố (qend+2)
    fin3 = fin.copy()
    fin3.loc[(fin3.ticker == "BBB") & (fin3.quarter == "2026Q4"), "Release_Date"] = pd.Timestamp("2027-01-02")
    rows = T.new_event_rows(fin3, CMAP, T.quarter_avgs(te), lagq, mk, set(), "2027-01-03")
    b = rows[(rows.ticker == "BBB") & (rows.quarter == "2026Q4")].iloc[0]
    ok("SIGNAL_NOT_BEFORE_RELEASE" in b.reason and not b.counts, "công bố ≤ qend+2 ⇒ loại")
    um2 = um.copy()
    um2[pd.Timestamp("2027-01-25")] = set(um2[pd.Timestamp("2027-01-25")]) - {"CCC"}
    rows = T.new_event_rows(fin, CMAP, T.quarter_avgs(te), lagq, T.Market(close, um2), set(), "2027-01-26")
    ok("NOT_IN_UNIVERSE" in rows[(rows.ticker == "CCC") & (rows.quarter == "2026Q4")].reason.iloc[0], "không thuộc universe_pit ngày công bố ⇒ loại")


def t_lock(T):
    with tempfile.TemporaryDirectory() as d:
        bad = T.check_locks(d, {"PREREG-4.md": "0" * 32})
        ok(bad and "MISSING" in bad[0], "thiếu file khoá ⇒ báo")
    ok(T.check_locks() == [], "PREREG-4.md + commodity_map_te.csv khớp md5 khoá")
    with tempfile.TemporaryDirectory() as d:
        old = T.LOCK_DIR
        T.LOCK_DIR = d
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = T.main(["--data-dir", d], data={})
            ok(rc == 2 and not os.path.exists(os.path.join(d, "commodity_sue_decomp_forward_events.csv")),
               "lệch khoá ⇒ rc=2, không ghi")
        finally:
            T.LOCK_DIR = old


def t_tz(T):
    ok(dt.datetime.now(T.ICT).utcoffset() == dt.timedelta(hours=7), "ICT +07")
    te, fin, lagq, close, um = fixture()
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_pipe(T, d, None, dict(cmap=CMAP, te=te, fin=fin, lagq=lagq, mk=T.Market(close, um)), ["--dry-run"])
        ok(out.startswith("[" + dt.datetime.now(T.ICT).strftime("%Y-%m-%d") + " ICT]"), "first_seen = ngày ICT bất kể TZ host")


def t_review():
    R = load(os.path.join(HERE, "commodity_sue_decomp_forward_review.py"), "csd_review")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok(R.main(["--asof", "2026-01-01", "--data-dir", tempfile.mkdtemp()]) == 3, "trước 2027-09-01 (không phải tương lai) ⇒ từ chối rc=3")
        ok(R.main(["--asof", "2031-09-01", "--data-dir", tempfile.mkdtemp()]) == 3, "asof tương lai (không --peek) ⇒ từ chối rc=3")
        _d = tempfile.mkdtemp()
        R.main(["--asof", "2031-09-01", "--data-dir", _d])
        ok(os.path.exists(os.path.join(_d, "commodity_sue_decomp_review_audit.csv")), "mỗi lần gọi review ghi dòng audit")
    ok(R.stage_of("2027-09-01") == "integrity" and R.stage_of("2028-09-01") == "mid" and R.stage_of("2031-09-01") == "final",
       "giai đoạn theo mốc")
    rng = np.random.default_rng(0)
    rows = []
    for k, q in enumerate(pd.period_range("2027Q1", periods=18, freq="Q")):
        for f in ["f1", "f2", "f3"]:
            for j in range(3):
                x = rng.normal()
                rows.append(dict(quarter=str(q), family=f, sue1=x, sue1_res=x + rng.normal(0, .5), post60=x + rng.normal()))
    ev = pd.DataFrame(rows)
    S = R.season_dic(ev, "sue1")
    ok(len(S) == 18 and (S.n == 9).all(), "mùa hợp lệ ≥6 sự kiện ≥3 họ")
    ok(len(R.season_dic(ev[ev.family != "f3"].groupby("quarter").head(5), "sue1")) == 0, "<6 sự kiện ⇒ bỏ mùa")
    ok(len(R.season_dic(ev[ev.family == "f1"], "sue1")) == 0, "<3 họ ⇒ bỏ mùa")
    hp = R.holm({"S1": 0.02, "S2": 0.04})
    ok(abs(hp["S1"] - 0.04) < 1e-12 and abs(hp["S2"] - 0.04) < 1e-12, "Holm ×2")
    st_bad = dict(n_seasons=8, mean=-0.01, median=0.0, frac_pos=0.4, lofo_min=-0.02, half1=0.0, half2=-0.02)
    ok(R.verdict(st_bad, 0.9, "mid").startswith("FAIL"), "N≥8, TB≤0 ⇒ FAIL sớm")
    ok(R.verdict({**st_bad, "n_seasons": 7}, 0.9, "mid").startswith("TIẾP TỤC"), "N=7 ⇒ chưa FAIL sớm")
    good = dict(n_seasons=18, mean=0.15, median=0.12, frac_pos=0.72, lofo_min=0.1, half1=0.12, half2=0.18)
    ok(R.verdict(good, 0.001, "mid").startswith("TIẾP TỤC"), "đạt nhưng giữa kỳ ⇒ không PASS")
    ok(R.verdict(good, 0.001, "final").startswith("PASS"), "đạt đủ ở mốc cuối ⇒ PASS")
    ok(R.verdict({**good, "n_seasons": 15}, 0.001, "final").startswith("KHÔNG PHÂN BIỆT"), "N<16 cuối ⇒ không phân biệt")
    ok(R.verdict({**good, "lofo_min": -0.01}, 0.001, "final").startswith("FAIL"), "trượt LOFO ⇒ FAIL")
    ok(R.verdict({**good}, 0.06, "final").startswith("FAIL"), "p Holm ≥ 0,05 ⇒ FAIL")
    ok(R.verdict({}, 1.0, "integrity").startswith("KIỂM TOÀN VẸN"), "mốc đầu chỉ kiểm toàn vẹn")


def t_repro(T):
    """Dữ liệu thật (read-only): sue1/c_yoy của tracker khớp np_d/c_yoy của b2_panel; sue2 khớp lag_live_schedule."""
    te = T.load_te(set(T.load_cmap().te_metric_key), os.path.join(RES, "te_daily.parquet"))
    fin = T.load_fin()
    hist = T.build_hist(fin, T.load_cmap(), T.quarter_avgs(te))
    b2 = pd.read_csv(os.path.join(RES, "b2_panel.csv"))
    m = hist.merge(b2[b2.tier == "A"], on=["ticker", "quarter"]).dropna(subset=["c_yoy_x", "c_yoy_y", "sue1", "np_d"])
    ok(len(m) > 500, f"ghép được >500 sự kiện tier A với b2_panel ({len(m)})")
    ok(np.abs(m.c_yoy_x - m.c_yoy_y).max() < 1e-9, "c_yoy khớp b2_panel ≤1e-9")
    ok(np.abs(m.sue1 - m.np_d).max() < 1e-9, "sue1 khớp np_d b2_panel ≤1e-9")
    sys.path.insert(0, WC)
    from lag_live_schedule import live_lag_candidates
    L = live_lag_candidates(start="2025-01-01")
    mm = hist.merge(L[["ticker", "quarter", "surprise_B_MA"]], on=["ticker", "quarter"]).dropna(subset=["sue2"])
    ok(len(mm) > 50 and np.abs(mm.sue2 - mm.surprise_B_MA).max() < 1e-9, f"sue2 khớp surprise_B_MA live ({len(mm)} dòng)")


def run_all(T, repro=True):
    t_units(T)
    t_market(T)
    t_pipeline(T)
    t_lock(T)
    t_tz(T)
    if repro:
        t_repro(T)


MUTANTS = [
    ("(hist.release < pd.Timestamp(release))", "(hist.release <= pd.Timestamp(release))"),      # dùng dữ liệu tới/sau ngày công bố
    ("(hist.family == family) & (hist.release < pd.Timestamp(release))", "(hist.family == family)"),  # fit không expanding
    ("out = pd.concat([old, new.astype(object)], ignore_index=True)[cols] if len(new) else old",
     "out = new if len(new) else old"),                                                           # ghi đè nhật ký
    ("new = new[[k not in keys", "new = new[[True or k not in keys"),                              # ghi đè khoá cũ
    ("(asof is not None and self.days[i + h] > pd.Timestamp(asof))", "False"),                    # dùng giá sau ngày chạy
    ("    print(msg)", "    print(msg + f\" IC={ev_all.sue1.astype(float).mean():.3f}\")"),          # in thống kê
    ('return "PRE_FREEZE_BACKFILL", False', 'return "PRE_FREEZE_BACKFILL", True'),
    ("> LATE_SESSIONS", ">= LATE_SESSIONS"),
    ("H, LATE_SESSIONS, MIN_OBS_Q = 60, 10, 40", "H, LATE_SESSIONS, MIN_OBS_Q = 59, 10, 40"),
    ("<= q.end_time.normalize() + pd.Timedelta(days=SIG_LAG_DAYS)", "< q.end_time.normalize()"),
    ('FIRST_Q, LAST_Q = pd.Period("2026Q3", "Q"), pd.Period("2026Q4", "Q")',
     'FIRST_Q, LAST_Q = pd.Period("2026Q3", "Q"), pd.Period("2026Q3", "Q")'),
]


if __name__ == "__main__":
    SRC = os.path.join(HERE, "commodity_sue_decomp_forward_tracker.py")
    T = load(SRC)
    run_all(T)
    t_review()
    print(f"selfcheck OK — {N_OK} assertion")
    if "--mutants" in sys.argv:
        src = open(SRC).read()
        dead = 0
        for a, b in MUTANTS:
            assert a in src, f"mutant target không còn: {a}"
            p = tempfile.mktemp(suffix=".py")
            open(p, "w").write(src.replace(a, b, 1))
            try:
                run_all(load(p, "mut"), repro=False)
                print(f"  MUTANT SỐNG (xấu): {a!r} → {b!r}")
            except Exception:
                dead += 1
        print(f"mutation: {dead}/{len(MUTANTS)} bị bắt")
        sys.exit(0 if dead == len(MUTANTS) else 1)
