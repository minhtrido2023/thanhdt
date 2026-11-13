#!/usr/bin/env python3
"""Selfcheck cho TRAN ADV PHIA BAN (`sell_adv_cap`, R&D Luong A7 -> sua A9) trong `simulate_holistic_nav.py`
+ 2 khoi wiring trong `pt_v23_audit_2014.py` (extract-and-test, khong chay ca audit).

    $DNA_PYEXE sell_adv_cap_selfcheck.py              # assertion
    $DNA_PYEXE sell_adv_cap_selfcheck.py --mutations  # assertion + mutation (moi mutation PHAI BI GIET)
    $DNA_PYEXE sell_adv_cap_selfcheck.py --all-tz     # chay lai assertion duoi ICT/UTC/America/New_York + env -u TZ

Quy uoc dang kiem (A9, job Taylor_20261113_153627):
  - Lenh thoat T+1 Open: moi phien ban <= cap x ADV; phan du giu vi the, carry phien sau (moi lat chiu slippage bac
    theo lat/ADV). Qua `sell_adv_maxcarry` phien carry => ban not (forced).
  - ADV cho tran ban: `sell_adv_lookup` DAY {tk: (ns, VND)}, gia tri tai d = ADV BIET TRUOC Open d (pit: median
    Volume t-60..t-1 x PxAdv(t-1)) => tra as-of <= d. Khong co bang day => fallback liquidity_lookup as-of < d
    (phien TRUOC, khong dung ADV cuoi ngay d cho lenh khop Open d).
  - ADV <= 0 / thieu ma / khong co gia tri truoc d => 0 => khong ban duoc phien do (cho forced).
  - Lat CUOI (lat ban not) dung CUNG ADV as-of nhu cac lat truoc (verdict A7 (d)).
  - Ma dang carry khong xep lenh thoat moi (chong trung).
  - OFF (sell_adv_cap=None) = byte-identical ke ca khi truyen sell_adv_lookup.
  - pt_v23: liq_map (bang ADV THUC THI cua BAL) dung TRUOC bo loc SIG_ADV_MIN (verdict A7 (c)); bang pit day khong
    nhin truoc (doi Volume/Price ngay d khong doi ADV tai d).
Khong doc dong ho he thong (moi ngay la tham so) => khong phu thuoc TZ; --all-tz chung minh dieu do.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                      # noqa: E402
import pandas as pd                     # noqa: E402
import simulate_holistic_nav as S       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "simulate_holistic_nav.py")
AUDIT = os.path.join(HERE, "pt_v23_audit_2014.py")
N = 0
NAV0 = 1_000_000_000.0
PX = 10_000.0
DATES = list(pd.bdate_range("2021-01-04", periods=60))
HOLD = 5


def ck(cond, label):
    global N
    N += 1
    if not cond:
        raise AssertionError(f"FAIL {label}")
    print(f"  ok  {label}")


def dense(vals_by_date):
    """{tk: {date: v}} -> {tk: (ns array sorted, float array)} (format sell_adv_lookup)."""
    out = {}
    for tk, m in vals_by_date.items():
        ks = sorted(m)
        out[tk] = (np.array([pd.Timestamp(k).value for k in ks], dtype=np.int64), np.array([float(m[k]) for k in ks]))
    return out


def run(cap=None, sell_tab=None, buy_liq=None, maxcarry=20, pass_kw=True, tiered=True):
    """1 ma AAA, gia/Open co dinh, tin hieu phien 1, giu HOLD phien => lenh TIME xep hang, khop Open phien sau."""
    px = {"AAA": {d: PX for d in DATES}}
    sig = pd.DataFrame([{"time": DATES[1], "ticker": "AAA", "play_type": "SIGNAL_V11", "ta": 1.0, "Close": PX}])
    if buy_liq is None:
        buy_liq = {("AAA", d): 1e13 for d in DATES}
    kw = dict(allowed_tiers=["SIGNAL_V11"], max_positions=1, hold_days=HOLD, stop_loss=-0.99, min_hold=1,
              slippage=0.0, init_nav=NAV0, deposit_annual=0.0, borrow_annual=0.0, reentry_blacklist_days=0,
              force_close_eod=False, name="sellcapchk", open_prices=px, t1_open_exec=True,
              liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=buy_liq,
              exit_slippage_tiered=tiered)
    log, ev = [], []
    if pass_kw:
        kw.update(sell_adv_cap=cap, sell_adv_maxcarry=maxcarry, sell_cap_log=log, sell_adv_lookup=sell_tab)
    nav, tr = S.simulate(sig, px, DATES, event_log=ev, **kw)
    return nav.reset_index(drop=True), pd.DataFrame(tr), pd.DataFrame(log), pd.DataFrame(ev)


def sells(ev):
    return ev[ev["action"] == "sell"].reset_index(drop=True) if len(ev) else ev


def sim_tests():
    # T1 OFF byte-identical (ke ca khi truyen bang day)
    n0, t0, _, e0 = run(pass_kw=False)
    n1, t1, l1, e1 = run(cap=None, sell_tab=dense({"AAA": {DATES[0]: 1.0}}))
    ck(n0.equals(n1) and t0.equals(t1) and e0.equals(e1), "T1 OFF: cap=None (+ sell_adv_lookup) trung tung byte nav/trades/events")
    ck(len(l1) == 0, "T1b OFF: khong ghi sell_cap_log")
    s0 = sells(e0)
    ck(len(s0) == 1, f"T1c OFF: 1 lenh ban tron (do {len(s0)})")
    D_EXIT = s0.loc[0, "ymd"]; iex = DATES.index(D_EXIT)
    sh_tot = float(e0[e0.action == "buy"]["shares"].sum())

    # T2 carry + chia lat: ADV 1e9, cap 0.2 => <= 2e8/phien, 5 lat lien tiep tu D_EXIT
    tab = dense({"AAA": {d: 1e9 for d in DATES}})
    n2, t2, l2, e2 = run(cap=0.2, sell_tab=tab)
    s2 = sells(e2)
    gross = sh_tot * PX
    nsl = int(np.ceil(gross / 2e8 - 1e-9))
    ck(len(s2) == nsl, f"T2a so lat = ceil({gross:.4g}/2e8) = {nsl} (do {len(s2)})")
    ck(list(s2["ymd"]) == DATES[iex:iex + nsl], "T2b lat dau dung phien thoat cu, cac lat LIEN TIEP")
    ck((s2["sell_amount"] <= 2e8 * (1 + 1e-12)).all(), f"T2c moi lat <= 0.2xADV (max {s2['sell_amount'].max():.6g})")
    ck(abs(s2["shares"].sum() - sh_tot) < 1e-6, "T2d tong co phieu ban = co phieu mua (khong mat/khong ban qua)")
    ck(list(l2["carry"]) == list(range(nsl)) and not l2["forced"].any(),
       "T2e log carry 0..n-1 (ca lat cuoi), khong forced")
    last = n2.iloc[-1]
    ck(abs(last["nav"] - last["cash"]) < 1e-3 if "cash" in n2.columns else True, "T2f cuoi ky NAV == cash (vi the da dong)")
    # tien: cash cuoi = cash sau mua + sum(sell_amount - fee)
    cash_after_buy = float(e2[e2.action == "buy"]["cash_after"].iloc[-1])
    ck(abs(cash_after_buy + float((s2["sell_amount"] - s2["fee"]).sum()) - float(s2["cash_after"].iloc[-1])) < 1e-3,
       "T2g self-check 0 VND: cash_after_buy + sum(ban - phi) == cash_after lat cuoi")

    # T3 slippage theo lat: lat rieng = 0.2xADV => bac 0.3%; lat cuoi dung CUNG ADV bang ban (khong phai bang mua)
    sl = t2.sort_values("exit_date")["exit_extra_slip"].to_numpy()
    ck(np.allclose(sl[:-1], 0.003), f"T3a lat rieng 0.2xADV => slip 0.003 (do {sl[:-1]})")
    rem = gross - 2e8 * (nsl - 1)
    exp_last = 0.005 if rem / 1e9 > 0.20 else 0.003 if rem / 1e9 > 0.10 else 0.001 if rem / 1e9 > 0.05 else 0.0
    ck(abs(sl[-1] - exp_last) < 1e-12 and exp_last > 0,
       f"T3b lat cuoi slip theo ADV ban ({rem/1e9:.3f}xADV => {exp_last}), KHONG theo bang mua 1e13 (do {sl[-1]})")

    # T4 ep ban o maxcarry: ADV rat nho, maxcarry 3 => 3 lat nho + phien 4 ban not (forced)
    n4, t4, l4, e4 = run(cap=0.2, sell_tab=dense({"AAA": {d: 1e6 for d in DATES}}), maxcarry=3)
    s4 = sells(e4)
    ck(len(s4) == 4 and list(s4["ymd"]) == DATES[iex:iex + 4], f"T4a 3 lat + 1 forced, lien tiep (do {len(s4)})")
    ck(int(l4["forced"].sum()) == 1 and bool(l4["forced"].iloc[-1]), "T4b dung 1 lan forced, o lat cuoi")
    ck(abs(s4["shares"].sum() - sh_tot) < 1e-6, "T4c forced ban NOT phan con lai")

    # T5 chong trung lenh thoat: dang carry, TIME bat lai moi phien nhung moi phien <= 1 lat
    per_day = s4.groupby("ymd").size()
    ck((per_day == 1).all(), "T5a moi phien dung 1 lenh ban cho ma dang carry")
    ck(not l4.duplicated(["ymd", "ticker"]).any(), "T5b sell_cap_log khong trung (ngay, ma)")

    # T6 liq=0 va thieu ma: khong ban duoc tu den forced
    for lbl, tb in (("liq=0", dense({"AAA": {d: 0.0 for d in DATES}})), ("thieu ma", dense({"BBB": {DATES[0]: 1e12}}))):
        _, _, l6, e6 = run(cap=0.2, sell_tab=tb, maxcarry=3)
        s6 = sells(e6)
        ck(len(s6) == 1 and s6.loc[0, "ymd"] == DATES[iex + 3] and bool(l6["forced"].iloc[-1]),
           f"T6 {lbl}: 0 lat truoc, ban 1 lan o phien forced (thoat+3)")
        ck((l6["liq"] <= 0).all() and (l6["liq_src"] == (1 if lbl == "liq=0" else -1)).all(),
           f"T6b {lbl}: log liq=0, liq_src dung ({'1' if lbl == 'liq=0' else '-1'})")

    # T7 bang day: tra as-of <= d (gia tri TAI d da la ADV truoc Open d); KHONG dung gia tri sau d
    m = {d: 1e13 for d in DATES}
    m[D_EXIT] = 1e9                                    # tai d: nho => phai bi tran
    _, _, l7, e7 = run(cap=0.2, sell_tab=dense({"AAA": m}))
    ck(len(sells(e7)) >= 2 and l7["liq"].iloc[0] == 1e9, "T7a bang day: lat dau dung ADV TAI d (side=right)")
    m2 = {d: v for d, v in ((DATES[iex - 3], 1e9), (DATES[iex + 1], 1e13))}
    _, _, l7b, _ = run(cap=0.2, sell_tab=dense({"AAA": m2}))
    ck(l7b["liq"].iloc[0] == 1e9, "T7b bang day thua: d thieu => lay gia tri <= d gan nhat, KHONG lay d+1")
    # T8 fallback (khong bang day): liquidity_lookup as-of STRICTLY < d
    bl = {("AAA", d): 1e13 for d in DATES}
    bl[("AAA", DATES[iex - 1])] = 1e9                  # phien truoc: nho
    _, _, l8, e8 = run(cap=0.2, sell_tab=None, buy_liq=bl)
    ck(len(l8) and l8["liq"].iloc[0] == 1e9, "T8a fallback: lat dau dung ADV phien TRUOC (d-1), khong dung ADV cuoi ngay d")
    bl2 = {("AAA", d): 1e13 for d in DATES}
    bl2[("AAA", D_EXIT)] = 1e9                         # chi ngay d nho => fallback KHONG duoc thay (nhin truoc)
    _, _, l8b, e8b = run(cap=0.2, sell_tab=None, buy_liq=bl2)
    ck(len(sells(e8b)) == 1 and (len(l8b) == 0), "T8b fallback: ADV cuoi ngay d KHONG anh huong lenh khop Open d")
    return D_EXIT


def _extract(path, start_pat, end_pat):
    src = open(path, encoding="utf-8").read()
    i = src.index(start_pat)
    j = src.index(end_pat, i) + len(end_pat)
    return src[i:j]


def audit_tests():
    # T9 pt_v23: liq_map dung TRUOC bo loc SIG_ADV_MIN
    blk = _extract(AUDIT, 'prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_f.groupby("ticker")}\n',
                   "\n")
    src = open(AUDIT, encoding="utf-8").read()
    i = src.index(blk); blk = src[i:src.index("\nvni = bq(VNI_QUERY", i)]   # tu dong `prices = ...` den truoc `vni = bq`
    sig_f = pd.DataFrame({"ticker": ["A", "A", "B"], "time": pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-04"]),
                          "liq": [3e9, 1.5e9, 1.2e9], "Close": [1.0, 1.0, 1.0]})
    g = {"sig_f": sig_f, "SIG_ADV_MIN": 2e9, "pd": pd}
    exec(blk, g)
    ck(len(g["sig_f"]) == 1 and len(g["liq_map"]) == 3 and g["liq_map"][("A", pd.Timestamp("2021-01-05"))] == 1.5e9,
       "T9 SIG_ADV_MIN loc tin hieu (3->1) nhung liq_map THUC THI giu du 3 key (ADV 1-2 ty con tran mua)")
    # T10 pt_v23: bang ADV pit day — dung cong thuc, khong nhin truoc
    blk2 = _extract(AUDIT, "if _SELLCAP_KW:\n    # A9 (verdict A7 (b)/(d))",
                    '    LIQ_LAG["sell_adv_lookup"] = SELL_ADV_PIT\n')
    days = pd.bdate_range("2020-06-01", "2021-03-31")
    rng = np.random.default_rng(7)
    vol = rng.integers(1_000, 100_000, len(days)).astype(float)
    price = np.where(np.arange(len(days)) % 7 == 0, np.nan, rng.uniform(5_000, 20_000, len(days)))
    close = rng.uniform(5_000, 20_000, len(days))
    base = pd.DataFrame({"ticker": "AAA", "time": days, "Volume": vol, "PxAdv": np.where(np.isnan(price), close, price)})

    def mk(df):
        def fake_bq(sql):
            tks = re.findall(r"'([A-Z0-9]+)'", sql.split("IN (")[-1])
            return df[df["ticker"].isin(tks)].copy()
        gg = {"_SELLCAP_KW": {"x": 1}, "opens_df": pd.DataFrame({"ticker": ["AAA"]}), "lag_universe": ["ZZZ"],
              "START_DATE": "2020-10-01", "END_DATE": "2021-03-31", "bq": fake_bq, "LAG_ADV_MINP": 20,
              "pd": pd, "np": np, "LIQ_FULL": {}, "LIQ_LAG": {}}
        exec(blk2, gg)
        return gg
    gg = mk(base)
    tab = gg["SELL_ADV_PIT"]["AAA"]
    ck(gg["LIQ_FULL"]["sell_adv_lookup"] is gg["LIQ_LAG"]["sell_adv_lookup"], "T10a cung bang pit cho BAL + LAG")
    k = 80
    d = days[k]
    exp = float(np.median(vol[k - 60:k])) * float(base["PxAdv"].iloc[k - 1])
    j = int(np.searchsorted(tab[0], pd.Timestamp(d).value))
    ck(tab[0][j] == pd.Timestamp(d).value and abs(tab[1][j] - exp) < 1e-6,
       f"T10b ADV(d) = median Volume t-60..t-1 x PxAdv(t-1) (do {tab[1][j]:.6g} vs {exp:.6g})")
    bad = base.copy()
    bad.loc[k, ["Volume", "PxAdv"]] = [1e12, 1e9]       # doi du lieu NGAY d
    tab2 = mk(bad)["SELL_ADV_PIT"]["AAA"]
    ck(tab2[1][j] == tab[1][j], "T10c doi Volume/Price NGAY d KHONG doi ADV(d) (khong nhin truoc)")
    ck(tab2[1][j + 1] != tab[1][j + 1], "T10d ... nhung doi ADV(d+1) (bang that su dung du lieu d cho phien sau)")
    ck(pd.Timestamp(tab[0][0]) >= pd.Timestamp("2020-06-01") and len(tab[0]) > 100, "T10e bang day (moi phien co du lieu)")


MUTATIONS = [
    ("M1 lat cuoi quay lai tra exact-key bang MUA (loi A7 (d))", SRC,
     "liq = (_liq_c if _sellcap_on else (liquidity_lookup.get((tk, today)) or 0))",
     "liq = (liquidity_lookup.get((tk, today)) or 0)"),
    ("M2 bang day side=left (bo qua ADV tai d)", SRC,
     '_sc_ser, _sc_side = sell_adv_lookup, "right"', '_sc_ser, _sc_side = sell_adv_lookup, "left"'),
    ("M3 fallback side=right (nhin truoc ADV cuoi ngay d)", SRC,
     '_sc_ser, _sc_side = {}, "left"', '_sc_ser, _sc_side = {}, "right"'),
    ("M4 bo chong trung lenh thoat", SRC,
     "                if tk in _pend_tk:\n                    continue",
     "                if False:\n                    continue"),
    ("M5 khong forced o maxcarry", SRC,
     "                    if _carry < sell_adv_maxcarry:", "                    if True:"),
    ("M6 thieu ma = ADV vo han (khong tran)", SRC,
     "            if a is None:\n                return 0.0, -1", "            if a is None:\n                return 1e18, -1"),
    ("M7 liq_map dung SAU bo loc SIG_ADV_MIN (loi A7 (c))", AUDIT,
     'liq_map = dict(zip(zip(sig_f["ticker"], sig_f["time"]), sig_f["liq"]))\n# A9',
     '# A9'),
    ("M8 bang pit khong shift (nhin truoc ngay d)", AUDIT,
     'x.shift(1).rolling(60, min_periods=LAG_ADV_MINP).median())\n                   * _sg["PxAdv"].shift(1))',
     'x.rolling(60, min_periods=LAG_ADV_MINP).median())\n                   * _sa["PxAdv"])'),
    ("M9 lat rieng khong chiu slippage bac", SRC,
     "                            if _p > 0.20:    extra_slip = 0.005\n                            elif _p > 0.10:  extra_slip = 0.003",
     "                            if _p > 9e9:    extra_slip = 0.005\n                            elif _p > 9e9:  extra_slip = 0.003"),
]


def run_mutations():
    me = open(os.path.abspath(__file__), encoding="utf-8").read()
    killed = 0
    for label, path, old, new in MUTATIONS:
        src = open(path, encoding="utf-8").read()
        assert src.count(old) == 1, f"pattern khong duy nhat ({src.count(old)}x): {label}"
        with tempfile.TemporaryDirectory() as td:
            for f in ("simulate_holistic_nav.py", "pt_v23_audit_2014.py"):
                s = open(os.path.join(HERE, f), encoding="utf-8").read()
                if os.path.join(HERE, f) == path:
                    s = s.replace(old, new)
                    if label.startswith("M7"):   # A7-order: dung liq_map SAU khi loc
                        s = s.replace(" (liq_map giữ {len(liq_map):,} key)", "", 1)
                        s = s.replace("\nvni = bq(VNI_QUERY", '\nliq_map = dict(zip(zip(sig_f["ticker"], sig_f["time"]), sig_f["liq"]))\nvni = bq(VNI_QUERY', 1)
                open(os.path.join(td, f), "w", encoding="utf-8").write(s)
            open(os.path.join(td, "sell_adv_cap_selfcheck.py"), "w", encoding="utf-8").write(me)
            r = subprocess.run([sys.executable, "sell_adv_cap_selfcheck.py"], cwd=td, capture_output=True, text=True,
                               env={**os.environ, "PYTHONPATH": td + os.pathsep + HERE})
            ok = r.returncode != 0
            killed += ok
            first = next((ln for ln in (r.stderr or "").splitlines()[::-1] if ln.strip()), "")
            print(f"  [{'KILLED' if ok else 'SURVIVED'}] {label}" + ("" if ok else "   <-- LO HONG TEST")
                  + (f"\n      {first[:140]}" if ok else ""))
    print(f"  mutation: {killed}/{len(MUTATIONS)} bi giet")
    return killed == len(MUTATIONS)


def run_all_tz():
    me = os.path.abspath(__file__)
    ok = True
    for tz in ("Asia/Ho_Chi_Minh", "UTC", "America/New_York"):
        r = subprocess.run([sys.executable, me], capture_output=True, text=True, env={**os.environ, "TZ": tz}, cwd=HERE)
        print(f"  [{'PASS' if r.returncode == 0 else 'FAIL'}] TZ={tz} {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]}")
        ok &= r.returncode == 0
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    r = subprocess.run([sys.executable, me], capture_output=True, text=True, env=env, cwd=HERE)
    print(f"  [{'PASS' if r.returncode == 0 else 'FAIL'}] env -u TZ")
    return ok and r.returncode == 0


if __name__ == "__main__":
    if "--all-tz" in sys.argv:
        print("== assertion duoi nhieu TZ ==")
        raise SystemExit(0 if run_all_tz() else 1)
    print("== assertion ==")
    sim_tests()
    audit_tests()
    print(f"  {N} assertion PASS")
    if "--mutations" in sys.argv:
        print("== mutation ==")
        if not run_mutations():
            raise SystemExit(1)
    print("OK")
