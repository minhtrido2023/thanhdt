#!/usr/bin/env python3
"""Selfcheck cho `idle_rate_proxy.py` — PIT, forward-fill, tier spot, + mutation testing.

    python3 idle_rate_proxy_selfcheck.py              # assertion
    python3 idle_rate_proxy_selfcheck.py --mutations   # assertion + mutation (moi mutation phai BI GIET)
    python3 idle_rate_proxy_selfcheck.py --haircut     # in bang do haircut (bang chung cho HAIRCUT_PP)

Khong doc dong ho he thong ⇒ khong phu thuoc TZ; test T7 xac nhan dieu do bang cach chay
lai duoi TZ ngoai (verify-before-done skill / coding_guidelines §16).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idle_rate_proxy as M   # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "idle_rate_proxy.py")
N = 0


def ck(cond, label):
    global N
    N += 1
    if not cond:
        raise AssertionError(f"FAIL: {label}")


def tests():
    global N
    tbl = M.monthly_table()

    # --- T1. Bang thang: don vi, pham vi, khong lot dong "Doanh so" (VND) vao cot %
    ck(tbl["sbv_low"].dropna().between(0, 25).all(), "T1 sbv_low trong [0,25]%")
    for c in [c for c in tbl.columns if c.startswith("ib_")]:
        v = tbl[c].dropna()
        ck(v.between(0, 30).all(), f"T1 {c} trong [0,30]% (dong Doanh so VND da bi loc)")
    ck(tbl["sbv_low"].dropna().index[0] == "2011-01", "T1 SBV bat dau 2011-01")
    ck("2026-08" in tbl["sbv_low"].dropna().index, "T1 SBV co 2026-08")
    ck(tbl["ib_1 tháng"].dropna().index[0] == "2014-01", "T1 lien NH bat dau 2014-01")
    ck((tbl["sbv_high"].dropna() >= tbl["sbv_low"].dropna()).all(), "T1 high >= low moi thang")

    # --- T2. Baseline = sbv_low - HAIRCUT_PP, clip >= 0
    m = "2026-06"
    ck(abs(tbl.loc[m, "baseline_pct"] - (tbl.loc[m, "sbv_low"] - M.HAIRCUT_PP)) < 1e-9,
       "T2 baseline = sbv_low - haircut")
    ck((tbl["baseline_pct"].dropna() >= 0).all(), "T2 baseline khong am")
    ck((tbl["floor_pct"].dropna() >= 0).all(), "T2 floor khong am")
    ck(M.FLOOR_TENOR == "1 tháng", "T2 floor dung tenor 1 thang (ke hoach §2.2)")

    # --- T3. PIT: moc thang T KHONG duoc dung trong thang T
    # 2026-08 SBV low = 6.1 -> baseline 4.06; 2026-07 low = 6.0 -> 3.96.
    ck(abs(tbl.loc["2026-08", "sbv_low"] - 6.1) < 1e-9, "T3 fixture 2026-08 sbv_low=6.1")
    ck(abs(tbl.loc["2026-07", "sbv_low"] - 6.0) < 1e-9, "T3 fixture 2026-07 sbv_low=6.0")
    ck(abs(M.r_idle("2026-08-31") - 3.96) < 1e-9,
       "T3 ngay 31/08 dung moc 2026-07 (chua duoc thay 2026-08)")
    ck(abs(M.r_idle("2026-09-01") - 4.06) < 1e-9, "T3 ngay 01/09 moi duoc dung moc 2026-08")
    ck(M.r_idle("2026-08-01") < M.r_idle("2026-09-01"), "T3 khong ro ri nguoc thoi gian")
    # quet toan bo: gia tri tai moi ngay phai bang mot moc <= thang truoc
    for d, mth in (("2020-01-01", "2019-12"), ("2020-01-31", "2019-12"),
                   ("2020-02-01", "2020-01"), ("2022-12-31", "2022-11")):
        ck(abs(M.r_idle(d) - tbl.loc[mth, "baseline_pct"]) < 1e-9, f"T3 {d} -> moc {mth}")
    ck(M._pit_month(date(2020, 1, 15)) == "2019-12", "T3 _pit_month vuot nam")

    # --- T4. Forward-fill: thang khuyet phai lay moc TRUOC gan nhat, khong lay moc sau
    # 2026-09 SBV khuyet (chi co lien NH) -> ngay trong 2026-10 phai roi ve 2026-08.
    ck(tbl.loc["2026-09", "sbv_low"] != tbl.loc["2026-09", "sbv_low"], "T4 fixture 2026-09 SBV NaN")
    ck(abs(M.r_idle("2026-10-15") - tbl.loc["2026-08", "baseline_pct"]) < 1e-9,
       "T4 forward-fill: 2026-10 dung moc 2026-08 (2026-09 khuyet)")
    ck(abs(M.r_idle("2027-06-01") - tbl.loc["2026-08", "baseline_pct"]) < 1e-9,
       "T4 forward-fill giu moc cuoi, khong extrapolate")
    ck(abs(M.r_idle("2026-10-01", "floor") - tbl.loc["2026-09", "floor_pct"]) < 1e-9,
       "T4 floor co 2026-09 nen khong bi ff")

    # --- T5. tier spot: tu choi ngay lich su VA ngay qua xa
    ck(abs(M.r_idle("2026-09-27", "spot") - M.SPOT_RATE_PCT) < 1e-9, "T5 spot tra 8.543 trong khoang")
    ck(abs(M.r_idle(M.SPOT_VALID_FROM, "spot") - M.SPOT_RATE_PCT) < 1e-9, "T5 spot bao gom bien duoi")
    for bad in ("2014-08-01", "2020-03-15", "2026-08-17", "2027-04-01", "2030-01-01"):
        try:
            M.r_idle(bad, "spot")
            ck(False, f"T5 spot PHAI raise cho {bad}")
        except ValueError:
            N += 1
    for bad_tier in ("Baseline", "", "tier1", None):
        try:
            M.r_idle("2026-06-01", bad_tier)
            ck(False, f"T5 tier khong hop le PHAI raise: {bad_tier!r}")
        except (ValueError, TypeError):
            N += 1

    # --- T6. Ngay truoc khi chuoi bat dau phai raise, khong tra 0 im lang
    try:
        M.r_idle("2014-01-15", "floor")
        ck(False, "T6 floor truoc 2014-02 PHAI raise")
    except ValueError:
        N += 1
    try:
        M.r_idle("2010-06-01", "baseline")
        ck(False, "T6 baseline truoc 2011-02 PHAI raise")
    except ValueError:
        N += 1

    # --- T7. r_idle_series == r_idle tung ngay; va cua so backtest chay duoc het
    ds = ["2014-08-01", "2019-06-15", "2022-11-30", "2026-06-15"]
    import numpy as np
    ck(np.allclose(M.r_idle_series(ds), [M.r_idle(d) for d in ds]), "T7 series == scalar")
    win = [f"{y}-{mo:02d}-15" for y in range(2014, 2027) for mo in range(1, 13)]
    win = [d for d in win if "2014-08-15" <= d <= "2026-06-15"]
    b = M.r_idle_series(win, "baseline")
    f = M.r_idle_series(win, "floor")
    ck(len(b) == len(win) and np.isfinite(b).all(), "T7 baseline phu het cua so backtest")
    ck(len(f) == len(win) and np.isfinite(f).all(), "T7 floor phu het cua so backtest")
    ck(b.max() < 7.0, "T7 baseline KHONG bao gio vuot break-even 7.00% (ket luan W1 muc 4)")

    # --- T8. measure_haircut khop hang so dang dung
    h = M.measure_haircut()
    ck(h["n"] == 143 and h["first"] == "2014-01" and h["last"] == "2026-08", "T8 haircut n=143")
    ck(abs(round(h["median"], 2) - M.HAIRCUT_PP) < 1e-9,
       f"T8 HAIRCUT_PP == median do duoc ({h['median']:.4f})")
    ck(h["median"] > 1.0, "T8 haircut do duoc LON HON con so quy uoc 1.0pp")
    print(f"  [ok] {N} assertion")


MUTATIONS = [
    ("M1 bo lag PIT (dung chinh thang cua ngay)",
     'return f"{y:04d}-{m - 1:02d}"', 'return f"{y:04d}-{m:02d}"'),
    ("M2 forward-fill -> lay moc TUONG LAI gan nhat",
     "avail = tbl.loc[:cutoff]", "avail = tbl.loc[cutoff:][::-1]"),
    ("M3 bo cong tier spot theo ngay",
     "if not (SPOT_VALID_FROM <= dd <= SPOT_VALID_TO):", "if False:"),
    ("M4 dao dau haircut (cong thay vi tru)",
     'df["baseline_pct"] = (df["sbv_low"] - HAIRCUT_PP)',
     'df["baseline_pct"] = (df["sbv_low"] + HAIRCUT_PP)'),
    ("M5 bo loc dong 'Doanh so' (VND lot vao cot %)",
     'i = i[i["series"].str.startswith("Lãi suất")].copy()', "i = i.copy()"),
    ("M6 floor doi sang tenor qua dem",
     'FLOOR_TENOR = "1 tháng"', 'FLOOR_TENOR = "qua đêm"'),
    ("M7 haircut dung mean thay median",
     '"median": float(d.median())', '"median": float(d.mean())'),
]


def run_mutations():
    src = open(SRC, encoding="utf-8").read()
    self_src = open(os.path.abspath(__file__), encoding="utf-8").read()
    killed = 0
    for label, old, new in MUTATIONS:
        assert src.count(old) == 1, f"pattern khong duy nhat: {label} / {old!r}"
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "idle_rate_proxy.py"), "w", encoding="utf-8").write(
                src.replace(old, new))
            open(os.path.join(td, "idle_rate_proxy_selfcheck.py"), "w", encoding="utf-8").write(
                re.sub(r'^_DEFAULT_DIR.*$', '', self_src, flags=re.M))
            r = subprocess.run([sys.executable, "idle_rate_proxy_selfcheck.py"],
                               cwd=td, capture_output=True, text=True,
                               env={**os.environ, "IDLE_RATE_PROXY_DIR": M.DATA_DIR})
            ok = r.returncode != 0
            killed += ok
            first = next((l for l in (r.stderr or "").splitlines()[::-1] if l.strip()), "")
            print(f"  [{'KILLED' if ok else 'SURVIVED'}] {label}"
                  + ("" if ok else "   <-- LO HONG TEST") + (f"\n      {first[:110]}" if ok else ""))
    print(f"  mutation: {killed}/{len(MUTATIONS)} bi giet")
    return killed == len(MUTATIONS)


if __name__ == "__main__":
    if "--haircut" in sys.argv:
        import json
        for tn in ("qua đêm", "1 tuần", "2 tuần", "1 tháng", "3 tháng", "6 tháng"):
            print(json.dumps(M.measure_haircut(tenor=tn), ensure_ascii=False))
        raise SystemExit(0)
    print("== assertion ==")
    tests()
    rc = 0
    if "--mutations" in sys.argv:
        print("== mutation ==")
        rc = 0 if run_mutations() else 1
    print("SELFCHECK PASS" if rc == 0 else "SELFCHECK FAIL")
    raise SystemExit(rc)
