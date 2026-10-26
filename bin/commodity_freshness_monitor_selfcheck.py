#!/usr/bin/env python3
"""Selfcheck commodity_freshness_monitor.py trên dữ liệu GIẢ LẬP (không chạm BQ, không ghi
data/ thật). Chạy dưới `env -u TZ` VÀ một TZ lạ (§16) — case TZ gọi lại CLI dưới cả hai.

    python3 bin/commodity_freshness_monitor_selfcheck.py
"""
import json
import os
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import commodity_freshness_monitor as m  # noqa: E402

REF = date(2026, 10, 26)  # Thứ Hai
P = dict(m.DEFAULTS)
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def weekdays(end, n_days):
    d0 = end - timedelta(days=n_days)
    return [d0 + timedelta(days=i) for i in range(n_days + 1) if (d0 + timedelta(days=i)).weekday() < 5]


def rows(key, dates, values=None, source="trading_economics", cadence="daily"):
    rng = np.random.default_rng(abs(hash(key)) % 2**32)
    if values is None:
        values = 100 + np.cumsum(rng.normal(0, 1, len(dates)))
    return [dict(metric_key=key, source=source, cadence=cadence, observation_date=d.isoformat(),
                 value=float(v)) for d, v in zip(dates, values)]


def build():
    r = []
    r += rows("daily_ok", weekdays(REF - timedelta(days=3), 700))          # cuối = Thứ Sáu
    r += rows("daily_stop", weekdays(REF - timedelta(days=10), 700))
    wk = [REF - timedelta(days=6 + 7 * i) for i in range(80)][::-1]
    r += rows("weekly_ok", wk)
    r += rows("weekly_miss1", [d - timedelta(days=4) for d in wk])          # age 10: chưa báo
    r += rows("weekly_stop", [d - timedelta(days=16) for d in wk])          # age 22: STALE
    fz = weekdays(REF - timedelta(days=1), 700)
    vals = list(100 + np.arange(len(fz), dtype=float))
    vals[-6:] = [vals[-6]] * 6
    r += rows("frozen", fz, vals)
    r += rows("newbie", weekdays(REF - timedelta(days=1), 7))
    # Lễ theo mùa: năm trước có gap 9 ngày quanh REF−364; năm nay đang trễ 9 (OK) / 15 (STALE; gap năm trước = 11 do dính cuối tuần, trần 11+2).
    for name, age in (("season_ok", 9), ("season_late", 15)):
        ds = [d for d in weekdays(REF - timedelta(days=age), 700)
              if not (REF - timedelta(days=364 + 4) < d < REF - timedelta(days=364 + 4 - 9))]
        r += rows(name, ds)
    # Cùng metric_key, 2 cadence: daily tươi, monthly ngừng.
    r += rows("dual", weekdays(REF - timedelta(days=1), 700))
    mo = [date(y, mth, 1) for y in (2024, 2025) for mth in range(1, 13)]
    r += rows("dual", mo, cadence="monthly")
    return pd.DataFrame(r)


def main():
    df = build()
    series = m.prepare(df)
    st = m.score_all(series, REF, P)

    def s(k, c="daily"):
        return st[m.series_key(k, "trading_economics", c)]

    check("daily_ok OK (age 3 qua cuối tuần)", s("daily_ok")["status"] == "OK", s("daily_ok"))
    check("daily_ok ngưỡng = p90+2 = 5", s("daily_ok")["threshold"] == 5.0, s("daily_ok"))
    check("daily_stop STALE (age 10)", s("daily_stop")["status"] == "STALE", s("daily_stop"))
    check("weekly_ok OK", s("weekly_ok")["status"] == "OK", s("weekly_ok"))
    check("weekly ngưỡng = 3×7 = 21", s("weekly_ok")["threshold"] == 21.0, s("weekly_ok"))
    check("weekly_miss1 (age 10) CHƯA báo — trade-off K=3 có chủ đích",
          s("weekly_miss1")["status"] == "OK", s("weekly_miss1"))
    check("weekly_stop STALE (age 22)", s("weekly_stop")["status"] == "STALE", s("weekly_stop"))
    check("frozen FROZEN_VALUE (6 giá trùng, lịch sử run=1)",
          s("frozen")["status"] == "FROZEN_VALUE" and s("frozen")["tail_run"] == 6, s("frozen"))
    check("newbie LOW_SAMPLE", s("newbie")["status"] == "LOW_SAMPLE", s("newbie"))
    check("season_ok OK nhờ gap năm trước", s("season_ok")["status"] == "OK"
          and s("season_ok")["seasonal_allow"] is not None, s("season_ok"))
    check("season_late STALE (vượt gap năm trước + pad)",
          s("season_late")["status"] == "STALE", s("season_late"))
    check("khoá tách cadence: dual daily OK", s("dual")["status"] == "OK", s("dual"))
    check("khoá tách cadence: dual monthly STALE", s("dual", "monthly")["status"] == "STALE",
          s("dual", "monthly"))

    # WB: lag công bố CHỈ áp trong backtest; live thấy dòng đã nằm trong bảng.
    wb = pd.DataFrame(rows("wbx", [date(y, mth, 1) for y in (2025, 2026) for mth in range(1, 13)
                                   if date(y, mth, 1) <= date(2026, 10, 1)],
                           source="worldbank_cmo", cadence="monthly"))
    k = m.series_key("wbx", "worldbank_cmo", "monthly")
    live = m.score_all(m.prepare(wb), date(2026, 10, 3), P)[k]
    bt = m.score_all(m.prepare(wb, backtest_lag=True), date(2026, 10, 3), P)[k]
    check("WB live thấy obs 10-01", live["last_obs"] == "2026-10-01", live)
    check("WB backtest ẩn obs chưa công bố (lag 35d)", bt["last_obs"] < "2026-09-01", bt)

    # run_live: báo khi đổi, im khi không đổi, báo hồi phục; ghi atomic.
    with tempfile.TemporaryDirectory() as td:
        sp = os.path.join(td, "state.json")
        _, l1, _ = m.run_live(series, REF, P, sp)
        check("lần đầu báo mọi cảnh báo", any("daily_stop" in x and "STALE" in x for x in l1), l1)
        _, l2, _ = m.run_live(series, REF, P, sp)
        check("không đổi ⇒ không in gì", l2 == [], l2)
        df2 = pd.concat([df, pd.DataFrame(rows("daily_stop", [REF - timedelta(days=1)]))])
        _, l3, _ = m.run_live(m.prepare(df2), REF, P, sp)
        check("hồi phục ⇒ dòng 🟢", any(x.startswith("🟢") and "daily_stop" in x for x in l3), l3)
        check("không để lại file tạm", sorted(os.listdir(td)) == ["state.json"], os.listdir(td))
        js = json.load(open(sp))
        need = {"last_obs", "age", "median_gap", "p90_gap", "status"}
        check("state json đủ trường", all(need <= set(v) for v in js["series"].values()))

        # Backtest: ngừng hẳn ⇒ TRUE_ONGOING; trễ ngắn tự lành ⇒ FALSE.
        d = weekdays(REF, 700)
        cut = REF - timedelta(days=20)
        stop = [x for x in d if x <= cut]
        blip = [x for x in d if not (REF - timedelta(days=60) < x < REF - timedelta(days=52))]
        bdf = pd.DataFrame(rows("stopper", stop) + rows("blip", blip))
        _, eps = m.backtest(m.prepare(bdf, backtest_lag=True), REF - timedelta(days=90), REF, P)
        cls = {e["key"].split("|")[0]: m.classify(e) for e in eps if e["status"] == "STALE"}
        check("backtest: ngừng hẳn ⇒ TRUE_ONGOING", cls.get("stopper") == "TRUE_ONGOING", cls)
        check("backtest: trễ ngắn ⇒ FALSE", cls.get("blip") == "FALSE", cls)

        # TZ (§16): ref mặc định = hôm nay ICT bất kể TZ host.
        csv = os.path.join(td, "h.csv")
        df.to_csv(csv, index=False)
        want = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
        for tz in (None, "Pacific/Kiritimati", "America/Los_Angeles"):
            env = {k2: v for k2, v in os.environ.items() if k2 != "TZ"}
            if tz:
                env["TZ"] = tz
            r = subprocess.run([sys.executable, os.path.join(HERE, "commodity_freshness_monitor.py"),
                                "--hist-csv", csv, "--state-path", os.path.join(td, "tz.json"),
                                "--no-write", "--verbose"], capture_output=True, text=True, env=env)
            check(f"TZ={tz}: ref mặc định = ICT {want}", r.returncode == 0 and
                  f"commodity_freshness {want}" in r.stdout, r.stdout[:200] + r.stderr[-300:])

    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL: {FAILS}'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
