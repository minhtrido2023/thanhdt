#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sổ cảnh báo căng thẳng vĩ mô (C1, Làn 3/F1 kế hoạch TE 04/11) — DISPLAY + append-only.

KHÔNG cap, KHÔNG sizing, KHÔNG gate, KHÔNG đụng macro_state_live.py/w_LAG. Khuôn: cap_signal_advisory_check.py.
PREREG (khoá 2026-11-19, ngưỡng đúng REPORT arch_8l_dt5g_data_leverage_20261119 §3.2, KHÔNG dò):
  USDVND_60d   USD/VND tăng >= +2,5% trong 60 quan sát (vn_usdvnd)
  TPCP10Y_d60  TPCP 10Y tăng >= +0,75pp (75bp) trong 60 quan sát (vn_bond_10y; chỉ Δ)
  INTERBANK_MINUS_POLICY  liên NH 3T − lãi điều hành >= 2,5pp (policy = quan sát tháng gần nhất <= ngày)
  DXY_60d      DXY tăng >= +5% trong 60 quan sát (us_dxy)
Episode = lần kích hoạt đầu, sau đó chết 126 quan sát. Fail-closed: series ngày có quan sát cuối cũ hơn 7 ngày
lịch => trigger đó n/a(stale), KHÔNG ghi sổ; policy_rate (tháng) cũ hơn 100 ngày => T3 n/a.
Nguồn: tav2_bq.macro_indicator (UNVERIFIED, kb/data_registry/macro/macro_indicator.md).
State DT5G ghi qua macro_state_live.get_gated_state (không đọc bảng vnindex_5state trơn).
"""
import argparse, csv, os, subprocess, sys
from datetime import datetime
from io import StringIO
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
MIKE = os.path.abspath(os.path.join(HERE, "..", ".."))
WC = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude")
LEDGER = os.environ.get("MSL_LEDGER", f"{MIKE}/kb/data_registry/market-state/macro_stress_ledger.csv")
PROJECT = "lithe-record-440915-m9"
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
W, DEAD, STALE_DAYS, POLICY_STALE_DAYS, CLUSTER_GAP_DAYS = 60, 126, 7, 100, 60
UP_CLUSTERS, UP_CLUSTERS_NEUTRAL = 10, 5
SERIES = ["vn_usdvnd", "vn_bond_10y", "vn_interbank_3m", "vn_policy_rate", "us_dxy"]
TRIGGERS = {  # trigger -> (ngưỡng, đơn vị hiển thị)
    "USDVND_60d": (0.025, "%"),
    "TPCP10Y_d60": (0.75, "pp"),
    "INTERBANK_MINUS_POLICY": (2.5, "pp"),
    "DXY_60d": (0.05, "%"),
}
NEED = {"USDVND_60d": ["vn_usdvnd"], "TPCP10Y_d60": ["vn_bond_10y"], "DXY_60d": ["us_dxy"],
        "INTERBANK_MINUS_POLICY": ["vn_interbank_3m", "vn_policy_rate"]}
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}  # macro_state_live: CRISIS=1,BEAR=2,NEUTRAL=3
COLS = ["fire_date", "trigger", "value", "threshold", "dt5g_state", "state_source",
        "cluster_id", "dead_until_approx", "checked_at_ict"]


def fetch_macro(start="2013-06-01"):
    sql = ("SELECT t.series_key AS k, t.observation_date AS d, t.value AS v FROM tav2_bq.macro_indicator AS t "
           f"WHERE t.series_key IN ({','.join(repr(s) for s in SERIES)}) AND t.observation_date >= '{start}' "
           "ORDER BY t.series_key, t.observation_date, t.fetched_at")
    cmd = (f"source {WC}/wc_env.sh && bq query --use_legacy_sql=false --project_id={PROJECT} "
           f"--format=csv --max_rows=100000 \"{sql}\"")
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"bq FAIL: {r.stderr[:400]}")
    df = pd.read_csv(StringIO(r.stdout))
    df["d"] = pd.to_datetime(df["d"])
    return df.drop_duplicates(["k", "d"], keep="last")


def series_of(df, k):
    return df[df["k"] == k].set_index("d")["v"].sort_index()


def trigger_values(df):
    u, b, ib, pol, dx = (series_of(df, k) for k in SERIES)
    p = pol.reindex(ib.index.union(pol.index)).ffill().reindex(ib.index)
    return {"USDVND_60d": u / u.shift(W) - 1, "TPCP10Y_d60": b - b.shift(W),
            "INTERBANK_MINUS_POLICY": ib - p, "DXY_60d": dx / dx.shift(W) - 1}


def episodes(val, thr):
    """Kích hoạt lần đầu + thời gian chết DEAD quan sát."""
    fires, dead = [], -1
    for i, (d, x) in enumerate(val.dropna().items()):
        if i > dead and x >= thr:
            fires.append((d, float(x)))
            dead = i + DEAD
    return fires


def freshness(df, asof):
    res = {}
    for k in SERIES:
        s = series_of(df, k)
        last = s.index.max() if len(s) else None
        age = (pd.Timestamp(asof) - last).days if last is not None else None
        lim = POLICY_STALE_DAYS if k == "vn_policy_rate" else STALE_DAYS
        res[k] = (last, age, age is not None and age <= lim)
    return res


def trig_ok(name, fr):
    return all(fr[k][2] for k in NEED[name])


def dt5g_state(date):
    """(state, source) qua get_gated_state; lỗi => ('UNAVAILABLE', lý do) — không chặn sổ."""
    try:
        sys.path.insert(0, WC)
        from macro_state_live import get_gated_state
        d = pd.Timestamp(date)
        g = get_gated_state((d - pd.Timedelta(days=10)).strftime("%Y-%m-%d"), d.strftime("%Y-%m-%d"))
        g = g.sort_values("time")
        row = g[pd.to_datetime(g["time"]) <= d].iloc[-1]
        return STATE_NAMES.get(int(row["state"]), f"UNKNOWN_{row['state']}"), str(row.get("source", "?"))
    except Exception as e:
        return "UNAVAILABLE", f"{type(e).__name__}:{str(e)[:60]}"


def load_ledger():
    if not os.path.exists(LEDGER):
        return pd.DataFrame(columns=COLS)
    return pd.read_csv(LEDGER, parse_dates=["fire_date"])


def dead_until(fire_date):
    return str(np.busday_offset(pd.Timestamp(fire_date).date(), DEAD, roll="forward"))


def append_row(trigger, fire_date, value, state, src, now=None):
    led = load_ledger()
    if len(led) and ((led["fire_date"] == pd.Timestamp(fire_date)) & (led["trigger"] == trigger)).any():
        return False
    if len(led):
        gap = (pd.Timestamp(fire_date) - led["fire_date"].max()).days
        cid = int(led["cluster_id"].max()) + (0 if gap <= CLUSTER_GAP_DAYS else 1)
    else:
        cid = 1
    row = dict(fire_date=pd.Timestamp(fire_date).date(), trigger=trigger, value=round(float(value), 4),
               threshold=TRIGGERS[trigger][0], dt5g_state=state, state_source=src, cluster_id=cid,
               dead_until_approx=dead_until(fire_date),
               checked_at_ict=(now or datetime.now(_ICT)).strftime("%Y-%m-%dT%H:%M:%S%z"))
    new = not os.path.exists(LEDGER)
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a", newline="") as f:  # append-only
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow(row)
    return True


def cluster_counts(led):
    if not len(led):
        return 0, 0
    ok = led["dt5g_state"].isin(["NEUTRAL", "BULL", "EX-BULL", "EXBULL"])
    return int(led["cluster_id"].nunique()), int(led.loc[ok, "cluster_id"].nunique())


def run(write=True, df=None, asof=None, state_fn=dt5g_state):
    """Tính hôm nay; ghi sổ nếu trigger vừa mở episode MỚI (kích hoạt tại quan sát cuối). Trả (dòng, info)."""
    asof = pd.Timestamp(asof or datetime.now(_ICT).date())
    df = fetch_macro() if df is None else df
    fr = freshness(df, asof)
    vals = trigger_values(df)
    parts, wrote = [], []
    for name, (thr, unit) in TRIGGERS.items():
        if not trig_ok(name, fr):
            parts.append(f"{name}=n/a(stale)")
            continue
        s = vals[name].dropna()
        cur = float(s.iloc[-1])
        eps = episodes(s, thr)
        if write and eps and eps[-1][0] == s.index[-1]:
            st, src = state_fn(eps[-1][0])
            if append_row(name, eps[-1][0], eps[-1][1], st, src):
                wrote.append(name)
        shown = f"{cur*100:+.2f}%" if unit == "%" else f"{cur:+.2f}pp"
        parts.append(f"{name}={shown}" + ("[FIRE]" if cur >= thr else ""))
    n, nn = cluster_counts(load_ledger())
    line = (f"Macro-stress sổ (as-of {asof.date()}): " + " | ".join(parts) +
            f" | cụm {n}/{UP_CLUSTERS}, cụm DT5G≥NEUTRAL {nn}/{UP_CLUSTERS_NEUTRAL} — GIẢ THUYẾT CHƯA KIỂM, "
            "chỉ hiển thị, không phải tín hiệu/cap (nguồn TE UNVERIFIED; TPCP chỉ tin Δ).")
    if all(not trig_ok(k, fr) for k in TRIGGERS):
        line = f"Macro-stress sổ (as-of {asof.date()}): không có dữ liệu tươi (fail-closed >7 ngày)."
    return line, {"wrote": wrote, "fresh": {k: (str(v[0].date()) if v[0] is not None else None, v[1], v[2])
                                            for k, v in fr.items()}}


def replay(df=None):
    """Đếm episode lịch sử 2014-01-02→2026-11-18 (không ghi sổ) để đối chiếu REPORT §3.2."""
    df = fetch_macro() if df is None else df
    res = {}
    for name, v in trigger_values(df).items():
        s = v.dropna()
        s = s[(s.index >= "2014-01-02") & (s.index <= "2026-11-18")]
        res[name] = [str(d.date()) for d, _ in episodes(s, TRIGGERS[name][0])]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-line", action="store_true", help="chỉ in dòng hiển thị (có ghi sổ nếu episode mới)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--replay", action="store_true")
    a = ap.parse_args()
    if a.replay:
        for k, v in replay().items():
            print(k, len(v), v)
        return 0
    line, info = run(write=not a.dry_run)
    print(line)
    if not a.print_line:
        print(info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
