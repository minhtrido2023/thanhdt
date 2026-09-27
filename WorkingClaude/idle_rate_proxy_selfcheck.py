#!/usr/bin/env python3
"""Selfcheck cho `idle_rate_proxy.py` — PIT, forward-fill, tier spot, + mutation testing.

    python3 idle_rate_proxy_selfcheck.py              # assertion
    python3 idle_rate_proxy_selfcheck.py --mutations   # assertion + mutation (moi mutation phai BI GIET)
    python3 idle_rate_proxy_selfcheck.py --haircut     # in bang do haircut (bang chung cho HAIRCUT_PP)
    python3 idle_rate_proxy_selfcheck.py --dep1m       # in bang do offset cau dep1m + coverage

T9..T14 = tier `dep1m` (user chot 2026-09-27 23:58 ICT), M8..M15 = mutation cua tier do.

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

    # --- T9. tier dep1m — doan THAT (2019-02..2026-09) phai khop CSV tung byte
    import pandas as _pd
    _csv = _pd.read_csv(os.path.join(M.DATA_DIR, M.DEP1M_CSV))
    _csv = _csv[_csv["series"] == "big4_1m_individual"].set_index("period")["rate_pct"]
    ck(len(_csv) == 92 and _csv.index[0] == "2019-02" and _csv.index[-1] == "2026-09",
       "T9 CSV dep1m 92 thang 2019-02..2026-09")
    for _m in ("2019-02", "2020-04", "2022-11", "2023-06", "2026-09"):
        ck(abs(tbl.loc[_m, "dep1m_pct"] - _csv.loc[_m]) < 1e-12,
           f"T9 {_m} dep1m_pct == so THAT trong CSV ({_csv.loc[_m]})")
        ck(tbl.loc[_m, "dep1m_src"] == "real", f"T9 {_m} nhan src=real")
    ck(tbl["dep1m_pct"].dropna().between(0, 20).all(), "T9 dep1m trong [0,20]%")

    # --- T10. doan DUNG LAI = sbv_low + DEP1M_OFFSET_PP, va nhan src=recon
    ck(abs(M.DEP1M_OFFSET_PP - (-2.525)) < 1e-9, "T10 offset mac dinh = median do duoc -2.525")
    for _m in ("2014-01", "2014-08", "2016-05", "2019-01"):
        ck(abs(tbl.loc[_m, "dep1m_pct"] - (tbl.loc[_m, "sbv_low"] + M.DEP1M_OFFSET_PP)) < 1e-9,
           f"T10 {_m} recon = sbv_low + offset")
        ck(tbl.loc[_m, "dep1m_src"] == "recon", f"T10 {_m} nhan src=recon")
    ck(abs(tbl.loc["2014-08", "dep1m_pct"] - 4.975) < 1e-9, "T10 fixture 2014-08 = 7.5-2.525 = 4.975")
    ck((tbl["dep1m_pct"].dropna() >= 0).all(), "T10 dep1m khong am (clip)")
    # KHONG back-fill so THAT ve qua khu: moi thang < 2019-02 phai la recon, khong bao gio real
    _pre = tbl.loc[:"2019-01", "dep1m_src"]
    ck(set(_pre.unique()) <= {"recon", ""}, "T10 truoc 2019-02 KHONG co thang nao nhan 'real'")
    _post = tbl.loc["2019-02":, "dep1m_src"]
    ck("recon" not in set(_post.unique()), "T10 tu 2019-02 KHONG dung recon de lap")

    # --- T11. PIT cho dep1m: bien real/recon va bien thang
    # 2019-02 that = 4.5; 2019-01 recon = 6.6-2.525 = 4.075.
    ck(abs(M.r_idle("2019-02-28", "dep1m") - 4.075) < 1e-9,
       "T11 28/02/2019 con dung moc 2019-01 (recon), chua thay so THAT 2019-02")
    ck(abs(M.r_idle("2019-03-01", "dep1m") - 4.5) < 1e-9,
       "T11 01/03/2019 moi duoc dung so THAT 2019-02")
    ck(abs(M.r_idle("2026-09-30", "dep1m") - tbl.loc["2026-08", "dep1m_pct"]) < 1e-9,
       "T11 30/09/2026 dung moc 2026-08, khong thay 2026-09")
    ck(abs(M.r_idle("2026-10-01", "dep1m") - tbl.loc["2026-09", "dep1m_pct"]) < 1e-9,
       "T11 01/10/2026 moi duoc dung moc 2026-09")
    ck(abs(M.r_idle("2015-03-15", "dep1m") - tbl.loc["2015-02", "dep1m_pct"]) < 1e-9
       if tbl.loc["2015-02", "dep1m_pct"] == tbl.loc["2015-02", "dep1m_pct"]
       else abs(M.r_idle("2015-03-15", "dep1m") - tbl.loc["2015-01", "dep1m_pct"]) < 1e-9,
       "T11 thang khuyet 2015-02 -> ff tu 2015-01, khong lay 2015-03")
    ck(abs(M.r_idle("2015-03-15", "dep1m") - tbl.loc["2015-01", "dep1m_pct"]) < 1e-9,
       "T11 ff lui, tuyet doi khong lay moc tuong lai 2015-03")
    try:
        M.r_idle("2011-01-15", "dep1m")
        ck(False, "T12 dep1m truoc 2011-02 PHAI raise")
    except ValueError:
        N += 1

    # --- T12. cua so backtest phu het + tran break-even
    win2 = [f"{y}-{mo:02d}-15" for y in range(2014, 2027) for mo in range(1, 13)]
    win2 = [d for d in win2 if "2014-08-15" <= d <= "2026-06-15"]
    dd = M.r_idle_series(win2, "dep1m")
    ck(len(dd) == len(win2) and np.isfinite(dd).all(), "T12 dep1m phu het cua so backtest")
    ck(dd.max() < 7.0, f"T12 dep1m KHONG vuot break-even 7.00% (max {dd.max():.3f})")
    ck(dd.min() >= 0.0, "T12 dep1m khong am trong cua so")

    # --- T13. offset override (bang bat dinh cua cau) doi DUNG doan recon, KHONG doi doan that
    _saved = M.DEP1M_OFFSET_PP
    try:
        M.DEP1M_OFFSET_PP = -3.4
        t2 = M.monthly_table()
        ck(abs(t2.loc["2014-08", "dep1m_pct"] - (7.5 - 3.4)) < 1e-9, "T13 offset p25 doi doan recon")
        ck(abs(t2.loc["2022-11", "dep1m_pct"] - tbl.loc["2022-11", "dep1m_pct"]) < 1e-12,
           "T13 offset KHONG duoc doi doan THAT")
    finally:
        M.DEP1M_OFFSET_PP = _saved
    ck(abs(M.monthly_table().loc["2014-08", "dep1m_pct"] - 4.975) < 1e-9, "T13 phuc hoi offset")

    # --- T14. measure_dep1m_offset + dep1m_coverage: bang chung khop hang so
    o = M.measure_dep1m_offset()
    ck(o["n"] == 90 and o["first"] == "2019-02" and o["last"] == "2026-08", "T14 overlap sbv_low n=90")
    ck(abs(round(o["median"], 3) - M.DEP1M_OFFSET_PP) < 1e-9,
       f"T14 DEP1M_OFFSET_PP == median do duoc ({o['median']:.4f})")
    ck(o["corr"] > 0.5, f"T14 sbv_low bac cau duoc: corr {o['corr']:+.3f} > 0.5")
    ck(abs(round(o["p25"], 3) + 3.400) < 1e-9 and abs(round(o["p75"], 3) + 2.300) < 1e-9,
       "T14 p25/p75 khop dai bat dinh dung cho chan sensitivity")
    ib = M.measure_dep1m_offset(ref="ib_1 tháng")
    ck(ib["sd"] > 2.0 and abs(ib["corr"]) < 0.3,
       f"T14 lien NH 1M KHONG bac cau duoc (sd {ib['sd']:.3f}, corr {ib['corr']:+.3f})")
    ck(ib["sd"] > o["sd"] * 2, "T14 sd cau lien NH > 2x sd cau sbv_low")
    cov = M.dep1m_coverage()
    ck(cov["n_real"] == 89 and cov["n_recon"] == 53 and cov["n_ff"] == 8,
       f"T14 coverage 2014-01..2026-06: {cov['n_real']} real / {cov['n_recon']} recon / {cov['n_ff']} ff")
    ck(cov["ff_months"][0] == "2015-02" and len(cov["ff_months"]) == 8, "T14 8 thang ff dung ten")
    ck("dep1m" in M.TIERS, "T14 dep1m nam trong TIERS")

    # --- T15. FIXTURE: neu CSV dep1m mot ngay nao do co them thang TRUOC 2019-02 thi cai
    # mask `df.index >= DEP1M_REAL_FROM` phai CHAN no lai. Khong co fixture nay thi mask la
    # code phong ve khong the kiem chung (mutation M8 song sot) — xem REPORT muc mutation.
    import shutil as _sh
    with tempfile.TemporaryDirectory() as _td:
        for _f in (M.SBV_CSV, M.IB_CSV, M.DEP1M_CSV):
            _sh.copy(os.path.join(M.DATA_DIR, _f), os.path.join(_td, _f))
        _fp = os.path.join(_td, M.DEP1M_CSV)
        with open(_fp, "a", encoding="utf-8") as _fh:
            _fh.write("2014-08,2014-08-15,big4_1m_individual,9.99\n")   # gia dinh nguon bo sung
        M._load.cache_clear()
        _t3 = M.monthly_table(_td)
        ck(_t3.loc["2014-08", "dep1m_src"] == "recon",
           "T15 thang < 2019-02 co so THAT van phai bi CHAN (src=recon)")
        ck(abs(_t3.loc["2014-08", "dep1m_pct"] - 4.975) < 1e-9,
           "T15 gia tri 2014-08 KHONG bi 9.99 de len (khong back-fill nguon moi)")
        ck(abs(M.r_idle("2014-09-01", "dep1m", data_dir=_td) - 4.975) < 1e-9,
           "T15 r_idle cung khong thay 9.99")
        ck(abs(_t3.loc["2019-02", "dep1m_pct"] - 4.5) < 1e-9, "T15 doan THAT khong bi anh huong")
    M._load.cache_clear()
    ck(abs(M.monthly_table().loc["2014-08", "dep1m_pct"] - 4.975) < 1e-9, "T15 cache da reset sach")

    # --- T8. measure_haircut khop hang so dang dung
    h = M.measure_haircut()
    ck(h["n"] == 143 and h["first"] == "2014-01" and h["last"] == "2026-08", "T8 haircut n=143")
    ck(abs(round(h["median"], 2) - M.HAIRCUT_PP) < 1e-9,
       f"T8 HAIRCUT_PP == median do duoc ({h['median']:.4f})")
    ck(h["median"] > 1.0, "T8 haircut do duoc LON HON con so quy uoc 1.0pp")
    print(f"  [ok] {N} assertion")


# HAI mutation UNG VIEN da bi LOAI vi CHUNG MINH DUOC LA TUONG DUONG (equivalent mutant), khong
# phai vi test yeu — ghi lai de nguoi sau khong tuong la thieu:
#   (a) dao thu tu `real.combine_first(recon)` -> `recon.combine_first(real)`: hai mask roi nhau
#       (real chi >= 2019-02, recon chi < 2019-02) ⇒ ket qua y nguyen voi MOI dau vao.
#   (b) bo `.clip(lower=0.0)` o nhanh recon: min(sbv_low) tren doan recon = 6.4 (2015-03), offset
#       am nhat dung trong bat ky chan nao la p25 = -3.4 ⇒ 3.0 > 0, clip KHONG bao gio chan.
#       Clip la phong ve cho du lieu tuong lai, khong phai logic dang chay.
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
     '"median": float(d.median()), "p25": float(d.quantile(0.25)),',
     '"median": float(d.mean()), "p25": float(d.quantile(0.25)),'),
    ("M8 dep1m: back-fill so THAT ve truoc 2019-02 (nhin trom tuong lai)",
     'real = df["dep1m_real"].where(df.index >= DEP1M_REAL_FROM)',
     'real = df["dep1m_real"]'),
    ("M9 dep1m: dao dau offset (cong thay vi tru)",
     'recon = (df["sbv_low"] + DEP1M_OFFSET_PP)',
     'recon = (df["sbv_low"] - DEP1M_OFFSET_PP)'),
    ("M10 dep1m: khai bao sai moc bat dau so THAT (goi ca doan dung lai la 'real')",
     'DEP1M_REAL_FROM = "2019-02"', 'DEP1M_REAL_FROM = "2014-01"'),
    ("M11 thang khuyet -> tra 0% thay vi forward-fill moc da cong bo (BAY 6)",
     "tbl = monthly_table(data_dir)[col].dropna()",
     "tbl = monthly_table(data_dir)[col].fillna(0.0)"),
    ("M12 dep1m: offset mac dinh lay p25 thay median",
     'DEP1M_OFFSET_PP = float(os.environ.get("IDLE_DEP1M_OFFSET_PP", "-2.525"))',
     'DEP1M_OFFSET_PP = float(os.environ.get("IDLE_DEP1M_OFFSET_PP", "-3.400"))'),
    ("M13 dep1m: offset do tren cau LIEN NGAN HANG (cau khong dung duoc)",
     'def measure_dep1m_offset(data_dir: str | None = None, ref: str = "sbv_low") -> dict:',
     'def measure_dep1m_offset(data_dir: str | None = None, ref: str = "ib_1 tháng") -> dict:'),
    ("M14 dep1m: bien PIT lui 1 thang cho rieng dep1m (dung chinh thang)",
     '    col = {"baseline": "baseline_pct", "floor": "floor_pct", "dep1m": "dep1m_pct"}[tier]\n'
     '    tbl = monthly_table(data_dir)[col].dropna()\n'
     '    cutoff = _pit_month(dd)',
     '    col = {"baseline": "baseline_pct", "floor": "floor_pct", "dep1m": "dep1m_pct"}[tier]\n'
     '    tbl = monthly_table(data_dir)[col].dropna()\n'
     '    cutoff = _pit_month(dd) if tier != "dep1m" else f"{dd.year:04d}-{dd.month:02d}"'),
    ("M15 dep1m: loai bo tier khoi TIERS (phai raise khi goi)",
     'TIERS = ("baseline", "floor", "spot", "dep1m")',
     'TIERS = ("baseline", "floor", "spot")'),
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
    if "--dep1m" in sys.argv:
        import json
        print(json.dumps(M.measure_dep1m_offset(), ensure_ascii=False))
        print(json.dumps(M.measure_dep1m_offset(ref="ib_1 tháng"), ensure_ascii=False))
        print(json.dumps(M.dep1m_coverage(), ensure_ascii=False))
        raise SystemExit(0)
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
