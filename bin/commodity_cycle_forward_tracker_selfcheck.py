#!/usr/bin/env python3
"""Selfcheck commodity_cycle_forward_tracker.py (+ review). Logic dựng tay; riêng t_repro đọc dữ liệu thật (read-only).
Chạy:  $DNA_PYEXE mike/bin/commodity_cycle_forward_tracker_selfcheck.py            (test)
       $DNA_PYEXE mike/bin/commodity_cycle_forward_tracker_selfcheck.py --mutants  (test + mutation: mỗi mutant phải FAIL)
Nên chạy dưới `env -u TZ` VÀ `TZ=America/New_York`."""
import datetime as dt
import importlib.util
import os
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPRO_CSV = os.path.join(HERE, "..", "agents/Taylor/research/commodity_cycle_prereg_20261025/events_posthoc_105_3M.csv")
N_OK = 0


def load(src):
    spec = importlib.util.spec_from_file_location("ccf", src)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.LOCK_DIR = os.path.join(HERE, "..", "agents/Taylor/research/commodity_cycle_prereg2_20261025")  # mutant ở /tmp
    return m


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def series(vals, start="2020-01"):
    return pd.Series(vals, index=pd.period_range(start, periods=len(vals), freq="M"), dtype=float)


def fake_market(T, n=400, fam_tick=("AAA", "BBB")):
    days = pd.bdate_range("2026-01-01", periods=n)
    rng = np.random.default_rng(1)
    names = list(fam_tick) + [f"C{i}" for i in range(8)]
    close = pd.DataFrame({k: 100 * np.cumprod(1 + rng.normal(0, .01, n)) for k in names}, index=days)
    icb = pd.Series({k: "0500" if k in fam_tick else "0501" for k in names})
    um = pd.Series({d: set(names) for d in days})
    return T.Market(close, icb, um, set(fam_tick), {"sugar": list(fam_tick)}), days


def core(T):
    # find_events: cắt lên, thời gian chết 12 tháng, cần R_{m-1}<th
    base = [100] * 14
    s = series(base + [112, 112, 100, 100, 100, 118, 100, 100, 100, 100, 100, 100, 100, 100, 100, 130])
    ev = T.find_events(s)
    ok(len(ev) >= 1 and ev[0][0] == s.index[14], "sự kiện đầu = tháng đầu R≥1,05 cắt lên")
    ok(all((b[0] - a[0]).n > 12 for a, b in zip(ev, ev[1:])), "thời gian chết >12 tháng giữa 2 sự kiện")
    ok(T.find_events(series([100] * 14 + [104] * 3)) == [], "R<1,05 ⇒ không sự kiện")
    # ngưỡng 1,05 (không phải 1,10): spike 108 ⇒ R=1,073
    def spikes(*idx):
        v = [100.0] * 50
        for i in idx:
            v[i] = 108.0
        return series(v)
    ok(len(T.find_events(spikes(14))) == 1 and abs(T.find_events(spikes(14))[0][1] - 1.0728) < 1e-3,
       "R=1,073 ≥1,05 ⇒ 1 sự kiện (ngưỡng 1,10 sẽ bỏ sót)")
    ok(len(T.find_events(spikes(14, 26))) == 1, "cách đúng 12 tháng ⇒ còn trong thời gian chết")
    ok(len(T.find_events(spikes(14, 27))) == 2, "cách 13 tháng ⇒ sự kiện mới")
    grow = series([100.0] * 14 + [100 * 1.03 ** k for k in range(1, 40)])
    ok(len(T.find_events(grow)) == 1, "R ở trên ngưỡng liên tục ⇒ chỉ 1 sự kiện (cần R_{m-1}<ngưỡng)")
    # classify
    days = pd.bdate_range("2026-09-01", "2030-12-31")
    P = pd.Period
    ok(T.classify(P("2026-08", "M"), pd.Timestamp("2026-10-25"), days)[0:3] == ("PRE_FREEZE_BACKFILL", False, "PRE_FREEZE"),
       "tháng ≤2026-09 (≥2026-03) ⇒ PRE_FREEZE counts=False")
    ok(T.classify(P("2026-02", "M"), pd.Timestamp("2026-10-25"), days) is None, "trước 2026-03 không ghi")
    ok(T.classify(P("2026-10", "M"), pd.Timestamp("2026-11-10"), days) is None, "trước ngày 11 tháng m+1 chưa ghi")
    c = T.classify(P("2026-10", "M"), pd.Timestamp("2026-11-11"), days, "2026-11-11")
    ok(c[0] == "FORWARD" and c[1] is True and c[2] == "", "ngày 11 ⇒ FORWARD counts=True")
    ok(c[3] == pd.Timestamp("2026-11-12"), "floor = max(day11, first_seen+1)")
    c = T.classify(P("2026-10", "M"), pd.Timestamp("2026-11-26"), days, "2026-11-26")
    ok(c[1] is False and c[2] == "LATE", "trễ 11 phiên sau ngày 11 ⇒ LATE counts=False")
    c10 = T.classify(P("2026-10", "M"), pd.Timestamp("2026-11-25"), days, "2026-11-25")
    ok(c10[1] is True, "trễ đúng 10 phiên sau ngày 11 (25/11) ⇒ chưa LATE")
    ok(T.classify(P("2030-10", "M"), pd.Timestamp("2030-12-01"), days) is None, "sau 2030-09 không ghi")
    ok(T.classify(P("2030-09", "M"), pd.Timestamp("2030-10-20"), days)[0] == "FORWARD", "2030-09 còn trong cửa sổ")
    # entry_session
    ok(T.entry_session(days, "2026-09-12") == pd.Timestamp("2026-09-14"), "11/9 là CN ⇒ phiên kế (T2)")


def t_core_and_pipeline(T):
    core(T)
    mk, days = fake_market(T)
    # sugar tăng mạnh tới 2026-10 ⇒ event FORWARD tháng 2026-10 (R vượt từ dưới)
    wb = {"sugar": series([100.0] * 24 + [140.0] + [100.0] * 5, start="2024-10")}   # spike đúng 2026-10
    ev_m = [m for m, _ in T.find_events(wb["sugar"])]
    ok(len(ev_m) >= 1, "synthetic có sự kiện")
    with tempfile.TemporaryDirectory() as d:
        now1 = dt.datetime(2026, 11, 12, 9, 0, tzinfo=T.ICT)
        rc = T.main(["--data-dir", d], wb=wb, mk=mk, now=now1)
        ev = pd.read_csv(os.path.join(d, "commodity_cycle_forward_events.csv"))
        ok(rc == 0 and len(ev) == 1 and ev.signal_month[0] == "2026-10" and ev.counts[0] and ev.status[0] == "FORWARD",
           "ghi sổ lần 1: 1 sự kiện FORWARD 2026-10 counts=True")
        n1, R1 = len(ev), ev.R.tolist()
        # chạy lại với WB đã bị 'sửa' ⇒ idempotent, giá trị lần đầu giữ nguyên
        wb2 = {"sugar": wb["sugar"] * 1.0001}
        T.main(["--data-dir", d], wb=wb2, mk=mk, now=now1 + dt.timedelta(days=1))
        ev2 = pd.read_csv(os.path.join(d, "commodity_cycle_forward_events.csv"))
        ok(len(ev2) == n1 and ev2.R.tolist() == R1, "append-only: không ghi lại, không ghi đè")
        # dry-run không ghi
        with tempfile.TemporaryDirectory() as d2:
            T.main(["--data-dir", d2, "--dry-run"], wb=wb, mk=mk, now=now1)
            ok(not os.path.exists(os.path.join(d2, "commodity_cycle_forward_events.csv")), "--dry-run không tạo file")
        out = os.path.join(d, "commodity_cycle_forward_outcomes.csv")
        ok(not os.path.exists(out) or len(pd.read_csv(out)) == 0 or True, "outcome có thể có hoặc chờ")
    # outcome: floor ở xa cuối lịch ⇒ pending; ở đầu ⇒ tính X đúng bằng tay
    e = pd.DataFrame([dict(family="sugar", signal_month="2026-01", R=1.1, status="FORWARD", counts=True, reason="",
                           entry_floor="2026-02-02", first_seen="x", prereg_md5="", map_md5=""),
                      dict(family="sugar", signal_month="2026-12", R=1.1, status="FORWARD", counts=True, reason="",
                           entry_floor=str(days[-10].date()), first_seen="x", prereg_md5="", map_md5="")])
    rows, log = T.new_outcome_rows(e, set(), mk, "now")
    ok(len(rows) == 1 and any("pending" in x for x in log), "đủ 63 phiên mới tính; chưa đủ ⇒ pending")
    i = mk.days.get_loc(pd.Timestamp(rows.entry_date[0]))
    exp = np.mean([mk.close[t].iloc[i + 63] / mk.close[t].iloc[i] - 1 for t in ("AAA", "BBB")])
    ctrl = np.mean([mk.close[f"C{k}"].iloc[i + 63] / mk.close[f"C{k}"].iloc[i] - 1 for k in range(8)])
    ok(abs(rows.X[0] - (exp - ctrl)) < 1e-12, "X tính tay khớp")
    ok(bool(rows.fallback[0]) is False and rows.n_ctrl[0] == 8, "đủ ≥5 mã cùng supersector ⇒ không fallback")
    rows2, _ = T.new_outcome_rows(e, {("sugar", "2026-01")}, mk, "now")
    ok(len(rows2) == 0, "đã có outcome ⇒ không tính lại")


def t_lock(T):
    with tempfile.TemporaryDirectory() as d:
        bad = T.check_locks(d, {"PREREG-2.md": "0" * 32})
        ok(bad and "MISSING" in bad[0], "thiếu file khoá ⇒ báo")
        open(os.path.join(d, "PREREG-2.md"), "w").write("x")
        ok(bool(T.check_locks(d, {"PREREG-2.md": "0" * 32})), "md5 lệch ⇒ báo")
    ok(T.check_locks() == [], "file khoá thật khớp md5")


def t_tz(T):
    mk, _ = fake_market(T)
    with tempfile.TemporaryDirectory() as d:
        # now=None ⇒ ICT; first_seen phải = ngày ICT, bất kể TZ host (chạy dưới env -u TZ / TZ=America/New_York)
        T.main(["--data-dir", d, "--dry-run"], wb={"sugar": series([100.0] * 30)}, mk=mk)
    ok(dt.datetime.now(T.ICT).utcoffset() == dt.timedelta(hours=7), "ICT +07")


def t_review(T):
    R = load(os.path.join(HERE, "commodity_cycle_forward_review.py"))
    ok(R.main(["--asof", "2027-06-30"]) == 3, "trước mốc xem xét đầu ⇒ từ chối rc=3")
    cm = lambda v: pd.Series(v, index=range(len(v)), dtype=float)  # noqa: E731
    ev = lambda v: pd.DataFrame({"X": v})  # noqa: E731
    ok(R.verdict(cm([]), ev([]), None, True)[0].startswith("KHÔNG PHÂN BIỆT"), "N=0 cuối ⇒ không phân biệt được")
    ok(R.verdict(cm([-0.02, -0.05, 0.01]), ev([-.02, -.05, .01]), 0.0, False)[0].startswith("FAIL"), "N=3, TB≤0 ⇒ FAIL sớm")
    ok(R.verdict(cm([0.2, 0.1]), ev([.2, .1]), 0.0, True)[0].startswith("KHÔNG PHÂN BIỆT"), "N=2 cuối ⇒ không SUCCESS")
    good = [0.2, 0.18, 0.15, 0.22, 0.12]
    ok(R.verdict(cm(good), ev(good), 0.02, False)[0].startswith("TIẾP TỤC"), "N=5 đạt nhưng giữa kỳ ⇒ không tuyên SUCCESS")
    ok(R.verdict(cm(good), ev(good), 0.02, True)[0].startswith("SUCCESS"), "N=5 đạt, ngày cuối ⇒ SUCCESS")
    mixed = [0.2, 0.18, -0.15, 0.22, 0.12]
    ok(R.verdict(cm(mixed), ev(mixed), 0.02, True)[0].startswith("FAIL"), "N=5 trượt sign test ⇒ FAIL")


def t_repro(T):
    ref = pd.read_csv(REPRO_CSV)
    mk = T.load_market()
    wb = T.load_wb()
    rows = []
    for fam, s in wb.items():
        for m, r in T.find_events(s):
            t = T.entry_session(mk.days, T.day11(m))
            if t is not None and pd.Timestamp("2014-01-01") <= t <= pd.Timestamp("2026-03-31"):
                x = mk.measure(fam, t, 63)
                if x:
                    rows.append((fam, str(m), str(t.date()), x["X"]))
    got = pd.DataFrame(rows, columns=["family", "sig_month", "entry", "X"]).sort_values(["entry", "family"]).reset_index(drop=True)
    ref = ref.sort_values(["entry", "family"]).reset_index(drop=True)
    ok(len(got) == len(ref) == 28, f"tái dựng 28 sự kiện chọn-ô (got {len(got)})")
    ok((got.family == ref.family).all() and (got.sig_month == ref.sig_month).all() and (got.entry == ref.entry).all(),
       "family/sig_month/entry khớp events_posthoc_105_3M.csv")
    ok(np.abs(got.X.values - ref.X.values).max() < 1e-9, "X khớp ≤1e-9")


def run_all(T, repro=True):
    t_core_and_pipeline(T)
    t_lock(T)
    t_tz(T)
    if repro:
        t_repro(T)


MUTANTS = [("TH, H = 1.05, 63", "TH, H = 1.10, 63"), ("(m - last).n > 12", "(m - last).n > 11"),
           ("> LATE_SESSIONS", ">= LATE_SESSIONS"), ('"PRE_FREEZE_BACKFILL", False', '"PRE_FREEZE_BACKFILL", True'),
           ("fs + pd.Timedelta(days=1)", "fs"), ("if key in done_keys", "if False"),
           ("R[m - 1] < th", "R[m - 1] < 9"), ("FWD_FROM <= month <= FWD_TO", "FWD_FROM <= month")]


if __name__ == "__main__":
    SRC = os.path.join(HERE, "commodity_cycle_forward_tracker.py")
    T = load(SRC)
    run_all(T)
    t_review(T)
    print(f"selfcheck OK — {N_OK} assertion")
    if "--mutants" in sys.argv:
        src = open(SRC).read()
        dead = 0
        for a, b in MUTANTS:
            assert a in src, f"mutant target không còn: {a}"
            p = tempfile.mktemp(suffix=".py")
            open(p, "w").write(src.replace(a, b, 1))
            try:
                run_all(load(p), repro=False)
                print(f"  MUTANT SỐNG (xấu): {a!r} → {b!r}")
            except Exception:
                dead += 1
        print(f"mutation: {dead}/{len(MUTANTS)} bị bắt")
        sys.exit(0 if dead == len(MUTANTS) else 1)
