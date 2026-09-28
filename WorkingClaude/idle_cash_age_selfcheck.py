#!/usr/bin/env python3
"""Selfcheck cho QUY TAC TUOI TIEN (`dep1m_21s`) trong `simulate_holistic_nav.py`.

    $DNA_PYEXE idle_cash_age_selfcheck.py              # assertion
    $DNA_PYEXE idle_cash_age_selfcheck.py --mutations   # assertion + mutation (moi mutation PHAI BI GIET)
    $DNA_PYEXE idle_cash_age_selfcheck.py --all-tz      # chay lai assertion duoi 4 TZ + env -u TZ

Ngu nghia user chot 08:02 ICT 2026-09-28 (Discord): *"rut truoc han coi nhu huong lai 0%"*.
  - Mot LO tien chi duoc tra lai khi DA nam im >= `min_age` phien TINH DEN phien do.
  - Phien 1..min_age cua lo tra 0%; tu phien min_age+1 tro di moi cong r/252 cho lo do.
  - TUYET DOI KHONG TRUY LINH: lo nam 100 phien KHONG duoc tra nguoc cho min_age phien dau.
    Truy linh = phai biet tuong lai lo do co bi tieu khong = NHIN TRUOC.
  - Tien bi TIEU truoc khi du tuoi tu dong huong 0% (chua tung duoc cong) — khong can thu hoi.
  - FIFO (tieu lo CU truoc) = chan PIN vi giet lo da gia => IT lai hon = THAN TRONG.
    LIFO (tieu lo MOI truoc, giu lo gia) = chan do NHAY, cho lai NHIEU hon.

Hai tang test, co y:
  T1..T6 = UNIT tren `idle_lots_reconcile` / `idle_lots_eligible` (ngu nghia so lo).
  T7..T10 = END-TO-END mot lan `simulate()` that tren panel tong hop 60 phien, gia co dinh,
            deposit_annual = 0.0252 (=> r/252 = 1.000e-4 chan) => moi so lai KIEM TAY duoc.
            Tang nay moi la thu chung minh WIRING dung cho: tang tuoi o DAU phien, reconcile
            2 lan/phien, va chi tra cho phan du tuoi.

KHONG doc dong ho he thong (moi ngay la tham so) ⇒ khong phu thuoc TZ; T10 chay lai duoi TZ
ngoai de CHUNG MINH dieu do (coding_guidelines §16 + skill verify-before-done).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                      # noqa: E402
import pandas as pd                     # noqa: E402
import simulate_holistic_nav as S       # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulate_holistic_nav.py")
N = 0

MIN_AGE = 21                 # phien — nguong user chot
RATE = 0.0252                # %/nam dang fraction => RATE/252 = 1.0e-4 chan moi phien
PER = RATE / 252
NAV0 = 1_000_000_000.0


def ck(cond, label):
    global N
    N += 1
    if not cond:
        raise AssertionError(f"FAIL: {label}")


def near(a, b, tol=1e-6):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


# ---------------------------------------------------------------- T1..T6: UNIT
def unit_tests():
    R, E = S.idle_lots_reconcile, S.idle_lots_eligible

    # T1 — tao lo, bat bien tong = cash, tuoi khoi tao = 0
    lots = []
    R(lots, 100.0)
    ck(lots == [[0, 100.0]], "T1a lo dau tien = [age 0, 100]")
    R(lots, 100.0)
    ck(lots == [[0, 100.0]], "T1b reconcile lai cung so tien = khong doi gi")
    R(lots, 150.0)
    ck(len(lots) == 2 and lots[1] == [0, 50.0], "T1c dong vao => lo MOI o CUOI (moi nhat)")
    ck(near(sum(a for _, a in lots), 150.0), "T1d bat bien tong == cash")

    # T2 — eligible theo tuoi: bien 20/21/22 (off-by-one)
    lots = [[MIN_AGE - 1, 10.0], [MIN_AGE, 20.0], [MIN_AGE + 1, 30.0]]
    ck(near(E(lots, MIN_AGE), 50.0), "T2a chi lo tuoi >= 21 duoc tinh (20+30)")
    ck(near(E(lots, MIN_AGE + 1), 30.0), "T2b nguong 22 => chi lo tuoi 22")
    ck(near(E(lots, 0), 60.0), "T2c min_age=0 => toan bo (nhung engine coi 0 = TAT)")
    ck(near(E([], MIN_AGE), 0.0), "T2d chuoi tien = 0 => eligible 0, khong no")

    # T3 — FIFO tieu lo CU truoc; LIFO tieu lo MOI truoc
    base = [[30, 100.0], [0, 40.0]]
    f = R([list(x) for x in base], 100.0, "fifo")
    ck(f == [[0, 40.0]] or f == [[30, 60.0], [0, 40.0]], "T3a fifo dang hop le")
    ck(near(E(f, MIN_AGE), 60.0), "T3b fifo: -40 an vao lo GIA => eligible 60")
    l = R([list(x) for x in base], 100.0, "lifo")
    ck(near(E(l, MIN_AGE), 100.0), "T3c lifo: -40 an vao lo MOI => eligible con nguyen 100")
    ck(near(sum(a for _, a in f), 100.0) and near(sum(a for _, a in l), 100.0),
       "T3d ca hai thu tu deu giu bat bien tong == cash")

    # T4 — "tien ve roi di trong 1 phien": net = 0 nhung FIFO VAN an vao lo gia
    lots = [[30, 100.0]]
    R(lots, 100.0 + 25.0, "fifo")            # tien ve
    R(lots, 100.0, "fifo")                   # tien di ngay trong phien
    ck(near(sum(a for _, a in lots), 100.0), "T4a tong tro ve 100")
    ck(near(E(lots, MIN_AGE), 75.0), "T4b FIFO: lo gia bi an 25 => eligible 75, KHONG phai 100")
    lots = [[30, 100.0]]
    R(lots, 125.0, "lifo"); R(lots, 100.0, "lifo")
    ck(near(E(lots, MIN_AGE), 100.0), "T4c LIFO: lo moi bi an het => lo gia con nguyen")

    # T5 — margin (cash<0) xoa so lo; tien ve sau do la lo MOI (tuoi 0)
    lots = [[40, 100.0]]
    R(lots, -50.0, "fifo")
    ck(lots == [], "T5a cash<0 => so lo rong (khong co lo nao dang nam im)")
    R(lots, 70.0, "fifo")
    ck(lots == [[0, 70.0]], "T5b tien ve sau margin = lo tuoi 0, phai cho lai tu dau")
    ck(near(E(lots, MIN_AGE), 0.0), "T5c => eligible 0")

    # T6 — thu tu la duy nhat; tieu nhieu lo lien tiep; tieu HET
    lots = [[50, 10.0], [40, 10.0], [5, 10.0]]
    R(lots, 5.0, "fifo")
    ck(lots == [[5, 5.0]], "T6a fifo an het 2 lo gia + mot phan lo moi")
    lots = [[50, 10.0], [40, 10.0], [5, 10.0]]
    R(lots, 5.0, "lifo")
    ck(lots == [[50, 5.0]], "T6b lifo an het 2 lo moi + mot phan lo gia")
    lots = [[50, 10.0]]
    R(lots, 0.0, "fifo")
    ck(lots == [], "T6c tieu het => so lo rong")
    try:
        R([], 1.0, "sifo"); ck(False, "T6d thu tu la khong duoc chap nhan")
    except ValueError:
        ck(True, "T6d thu tu la bi raise")


# ------------------------------------------------- panel tong hop cho END-TO-END
def _panel(n_sessions=60, sig_session=30):
    """Panel toi thieu simulate() can: signals(time,ticker,play_type,ta,Close) + prices + vni_dates.

    Gia CO DINH 10.000 => khong co PnL, moi thay doi cash chi den tu phi + carry ⇒ kiem tay duoc.
    """
    dates = list(pd.bdate_range("2020-01-01", periods=n_sessions))
    px = {"AAA": {d: 10_000.0 for d in dates}}
    rows = ([{"time": dates[sig_session], "ticker": "AAA", "play_type": "SIGNAL_V11",
              "ta": 1.0, "Close": 10_000.0}] if sig_session < n_sessions else [])
    sig = pd.DataFrame(rows, columns=["time", "ticker", "play_type", "ta", "Close"])
    return sig, px, dates


def _run(min_age, order, n_sessions=60, sig_session=30, max_positions=4, hold_days=999):
    sig, px, dates = _panel(n_sessions, sig_session)
    log = []
    nav, _tr = S.simulate(
        sig, px, dates, allowed_tiers=["SIGNAL_V11"], max_positions=max_positions,
        hold_days=hold_days, stop_loss=-0.99, min_hold=2, slippage=0.0,
        init_nav=NAV0, deposit_annual=RATE, borrow_annual=0.0,
        deposit_min_age_sessions=min_age, deposit_age_order=order,
        idle_age_log=log, reentry_blacklist_days=0,
        force_close_eod=False, name="agecheck",
    )
    nav = nav.reset_index(drop=True)
    return nav, pd.DataFrame(log)


def e2e_tests():
    # T7 — KHONG TRUY LINH + off-by-one: lai dau tien dung o phien thu 22 cua lo (index 21)
    nav, log = _run(MIN_AGE, "fifo", n_sessions=40, sig_session=99)   # sig_session>n => khong giao dich
    ck(len(nav) == 40, "T7a chay du 40 phien")
    ints = nav["interest"].to_numpy()
    ck(near(ints[:MIN_AGE].sum(), 0.0, 0), f"T7b 21 phien dau (index 0..20) tra 0 VND, do {ints[:MIN_AGE].sum()}")
    ck(ints[MIN_AGE] > 0, "T7c phien index 21 (= phien thu 22 cua lo) BAT DAU duoc tra")
    ck(near(ints[MIN_AGE], NAV0 * PER), f"T7d lai phien dau = NAV0*r/252 = {NAV0*PER:.1f}, do {ints[MIN_AGE]:.1f}")
    # truy linh se tra 22*NAV0*PER o phien nay; khong truy linh thi dung 1x
    ck(ints[MIN_AGE] < 2 * NAV0 * PER, "T7e KHONG truy linh (khong phai 22x mot cuc)")
    # goc cua lo KHONG gop lai (lai la lo moi, phai tu cho tuoi) => phien 22 == phien 23
    ck(near(ints[MIN_AGE + 1], NAV0 * PER), "T7f lai KHONG tu gop vao goc lo (lai la lo MOI tuoi 0)")

    # T8 — control: min_age=0 => duong carry cu (tra tu phien dau, gop lai)
    nav0, _ = _run(0, "fifo", n_sessions=40, sig_session=99)
    i0 = nav0["interest"].to_numpy()
    ck(i0[0] > 0, "T8a min_age=0 => tra ngay phien dau (duong cu)")
    ck(near(i0[0], NAV0 * PER), "T8b lai phien dau duong cu = NAV0*r/252")
    ck(nav0["nav"].iloc[-1] > nav["nav"].iloc[-1],
       "T8c NAV cuoi cua chan KHONG co age-gate PHAI cao hon chan co age-gate")
    ck(i0[-1] > ints[-1], "T8d duong cu gop lai => lai/phien cuoi cao hon")

    # T9 — FIFO vs LIFO: co giao dich (cash ra) thi LIFO tra NHIEU hon FIFO (giu lo gia)
    navF, logF = _run(MIN_AGE, "fifo", n_sessions=60, sig_session=30)
    navL, logL = _run(MIN_AGE, "lifo", n_sessions=60, sig_session=30)
    ck(len(logF) == 60 and len(logL) == 60, "T9a idle_age_log day du 60 phien ca hai chan")
    ck(navF["cash"].iloc[-1] < NAV0 * 0.9, "T9b da co mua that (cash tut xuong)")
    eF, eL = logF["eligible"].to_numpy(), logL["eligible"].to_numpy()
    ck((eL >= eF - 1e-6).all(), "T9c LIFO giu lo gia => eligible >= FIFO o MOI phien")
    ck(eL[-1] > eF[-1] + 1.0, f"T9d sau khi mua, LIFO eligible > FIFO ({eL[-1]:.0f} vs {eF[-1]:.0f})")
    ck(navL["nav"].iloc[-1] > navF["nav"].iloc[-1], "T9e => NAV LIFO > NAV FIFO (FIFO la chan THAN TRONG)")
    # eligible khong bao gio vuot qua cash cung phien
    ck((logF["eligible"] <= logF["cash_pre_int"] + 1e-6).all(), "T9f eligible <= cash (khong the tra qua so tien co)")
    ck((logL["eligible"] <= logL["cash_pre_int"] + 1e-6).all(), "T9g eligible <= cash (chan lifo)")

    # T10 — lai moi phien PHAI dung bang rate * eligible / 252 (khong phai * tong cash)
    for lbl, nv, lg in (("fifo", navF, logF), ("lifo", navL, logL)):
        exp = lg["eligible"].to_numpy() * PER
        got = nv["interest"].to_numpy()
        ck(np.abs(got - exp).max() < 1e-6,
           f"T10 {lbl}: interest == eligible*r/252 tung phien (lech max {np.abs(got-exp).max():.3e})")
        ck(np.abs(got - lg["cash_pre_int"].to_numpy() * PER).max() > 1.0,
           f"T10b {lbl}: interest KHAC cash_total*r/252 (chung minh age-gate co tac dung)")


def _run_straddle(order="fifo", n_sessions=60):
    """Panel 2 ma dung de bat dong tien RA/VE *bac qua* moc step-4 (xem T11).

    BBB mua o phien 6, hold 25 phien -> ban va tien VE dau phien 32 (step 0).
    AAA mua o phien 31 (tin hieu phien 30) -> tien RA cuoi phien 31 (step 5).
    => tai step 4 cua phien 32, cash gan y NGUYEN so truoc phien 31. Mot engine chi doi chieu so
    lo MOT lan moi phien (o step 4) se khong thay 250M da roi khoi tay; chi reconcile cuoi phien
    (6z) moi ghi nhan duoc.
    """
    dates = list(pd.bdate_range("2020-01-01", periods=n_sessions))
    px = {t: {d: 10_000.0 for d in dates} for t in ("AAA", "BBB")}
    sig = pd.DataFrame([
        {"time": dates[5], "ticker": "BBB", "play_type": "T_SHORT", "ta": 2.0, "Close": 10_000.0},
        {"time": dates[30], "ticker": "AAA", "play_type": "T_LONG", "ta": 1.0, "Close": 10_000.0},
    ])
    log = []
    nav, _tr = S.simulate(
        sig, px, dates, allowed_tiers=["T_LONG", "T_SHORT"], max_positions=4,
        hold_days=999, hold_days_by_tier={"T_LONG": 999, "T_SHORT": 25},
        stop_loss=-0.99, min_hold=2, slippage=0.0, init_nav=NAV0,
        deposit_annual=RATE, borrow_annual=0.0, deposit_min_age_sessions=MIN_AGE,
        deposit_age_order=order, idle_age_log=log, reentry_blacklist_days=0,
        force_close_eod=False, name="agecheck_straddle",
    )
    return nav.reset_index(drop=True), pd.DataFrame(log)


def round_trip_tests():
    """T11 — tien RA roi VE phai an vao lo gia THAT SU, khong duoc NET mat.

    Dung panel straddle (_run_straddle): 250M roi khoi tay cuoi phien 31, 250M khac ve dau phien
    32, nen o step 4 cua phien 32 tong cash gan nhu khong doi. Hai dau phai dung DONG THOI:
      (a) tu phien 32, cash ~750M nhung eligible chi ~500M — 250M da tieu bi day ve tuoi 0;
      (b) dung phien 32+21 = 53 tien ve moi DU TUOI tro lai, va khi do KHONG co cuc truy linh.
    """
    nav, log = _run_straddle("fifo")
    cash = nav["cash"].to_numpy()
    elig = log["eligible"].to_numpy()
    gap = cash - elig
    ck(gap[32:40].min() > 2.4e8,
       f"T11a FIFO an vao lo gia THAT du dong RA/VE bac qua moc step-4 "
       f"(gap min phien 32-39 = {gap[32:40].min():.0f}, phai > 240M)")
    ck(elig[35] > 4.5e8 and elig[35] < 5.5e8, f"T11b eligible ~500M (do {elig[35]:.0f})")
    ck(gap[31 + MIN_AGE] > 2.4e8, "T11c truoc phien 53 tien ve VAN chua du tuoi")
    ck(gap[32 + MIN_AGE] < 1.0e7, "T11d dung phien 32+21=53 tien ve du tuoi (dong ho chinh xac)")
    ints = nav["interest"].to_numpy()
    ck(near(ints[32 + MIN_AGE], elig[32 + MIN_AGE] * PER),
       "T11e phien du tuoi tra dung r/252 x eligible, KHONG co cuc truy linh 21 phien")
    ck((elig <= log["cash_pre_int"].to_numpy() + 1e-6).all(), "T11f eligible <= cash moi phien")
    # LIFO tren cung panel: giu lo gia => eligible khong bao gio thap hon FIFO
    _navL, logL = _run_straddle("lifo")
    ck((logL["eligible"].to_numpy() >= elig - 1e-6).all(), "T11g LIFO eligible >= FIFO moi phien")


def tests():
    unit_tests()
    e2e_tests()
    round_trip_tests()
    print(f"  assertion: {N} PASS")


# ------------------------------------------------------------------- MUTATIONS
MUTATIONS = [
    ("M1 bo nguong tuoi (tra cho MOI dong tien, ke ca vua ve)",
     "def idle_lots_eligible(lots, min_age):\n"
     '    """Total amount that has ALREADY been idle >= `min_age` sessions (so: earns carry today)."""\n'
     "    return sum(a for g, a in lots if g >= min_age)",
     "def idle_lots_eligible(lots, min_age):\n"
     '    """Total amount that has ALREADY been idle >= `min_age` sessions (so: earns carry today)."""\n'
     "    return sum(a for g, a in lots)"),
    ("M2 TRUY LINH: lo du tuoi duoc tra bu cho ca min_age phien dau (nhin truoc)",
     "                cash += _age_elig * _dep_today / 252",
     "                cash += _age_elig * _dep_today / 252 * (1 + _age_min if _age_elig > 0 else 1)"),
    ("M3 dao FIFO/LIFO (chan PIN thanh chan KHONG than trong)",
     '        idx = 0 if order == "fifo" else len(lots) - 1',
     '        idx = len(lots) - 1 if order == "fifo" else 0'),
    ("M4 off-by-one: du tuoi som 1 phien (phien 21 thay vi 22)",
     "    return sum(a for g, a in lots if g >= min_age)",
     "    return sum(a for g, a in lots if g >= min_age - 1)"),
    ("M5 off-by-one: du tuoi muon 1 phien (phien 23)",
     "    return sum(a for g, a in lots if g >= min_age)",
     "    return sum(a for g, a in lots if g > min_age)"),
    ("M6 tien ve roi di trong 1 phien bi NET mat (bo reconcile cuoi phien 6z)",
     "        if _age_on:\n            _lots_reconcile(cash)\n\n        # 7) Record NAV",
     "        if False:\n            _lots_reconcile(cash)\n\n        # 7) Record NAV"),
    ("M7 khong tang tuoi dau phien (khong lo nao gia di => khong bao gio du tuoi)",
     "        if _age_on:\n            for _lot in _cash_lots:\n                _lot[0] += 1",
     "        if _age_on:\n            for _lot in _cash_lots:\n                _lot[0] += 0"),
    ("M8 lo tao ra bat dau tu tuoi 1 (an gian 1 phien cho MOI lo)",
     "    if d > 1e-9:\n        lots.append([0, d])",
     "    if d > 1e-9:\n        lots.append([1, d])"),
    ("M9 lo MOI chen vao DAU so (pha thu tu tuoi => fifo/lifo an sai lo)",
     "    if d > 1e-9:\n        lots.append([0, d])",
     "    if d > 1e-9:\n        lots.insert(0, [0, d])"),
    ("M11 lai duoc GOP vao lo da du tuoi (lai thua huong tuoi cua goc => gop lai ngay)",
     "                cash += _age_elig * _dep_today / 252\n",
     "                _int_amt = _age_elig * _dep_today / 252\n"
     "                cash += _int_amt\n"
     "                for _l in _cash_lots:\n"
     "                    if _l[0] >= _age_min:\n"
     "                        _l[1] += _int_amt\n"
     "                        break\n"),
    ("M10 tra lai tren TONG cash thay vi phan du tuoi (chinh la bug can chan)",
     "            if cash > 0 and _dep_today > 0 and _age_elig > 0:\n"
     "                cash += _age_elig * _dep_today / 252",
     "            if cash > 0 and _dep_today > 0 and _age_elig > 0:\n"
     "                cash += cash * _dep_today / 252"),
]


# Mutation UNG VIEN bi loai vi CHUNG MINH DUOC LA TUONG DUONG (ghi ra, khong im lang bo) —
# cung ky luat nhu `idle_rate_proxy_selfcheck.py`:
#   (E1) `tgt = max(float(target_cash), 0.0)` -> `tgt = float(target_cash)`.
#        Voi target am, d = tgt - sum(lots) < 0 nen vao nhanh tieu; vong lap chay den khi `lots`
#        rong roi dung (need con du nhung khong con lo). Ket qua: sum(lots) == 0 == max(tgt, 0)
#        trong CA HAI ban => khong mot dau vao nao phan biet duoc. `max(...,0)` giu lai vi no KHAI
#        Y DINH, khong vi no doi hanh vi. (T5 van test hanh vi margin — chi la khong dung lam
#        mutation duoc.)
#   (E2) Dao thu tu 2 dong o step 4: `_lots_reconcile(cash)` roi `idle_lots_eligible(...)` <->
#        nguoc lai. Tuong duong CO DIEU KIEN, va dieu kien do chinh la reconcile 6z: sau 6z(s-1) so
#        lo dung bang cash cuoi phien s-1; giua do va step 4 cua phien s CHI co dong VAO (step 0
#        T+1-open exec cua exit, va force-delever ban chung khoan) — khong mot dong RA nao. Nen o
#        step 4 luon co cash >= tong so lo, phan chenh la tien MOI (tuoi 0, khong eligible) => tap
#        lo du tuoi y nhau bat ke thu tu. Giu thu tu reconcile-truoc vi no dung theo thoi gian; neu
#        ai do bo 6z thi E2 KHONG con tuong duong nua (va M6 da chan viec bo 6z).
EQUIVALENT_MUTATIONS = 2


def run_mutations():
    src = open(SRC, encoding="utf-8").read()
    self_src = open(os.path.abspath(__file__), encoding="utf-8").read()
    here = os.path.dirname(os.path.abspath(__file__))
    killed = 0
    for label, old, new in MUTATIONS:
        assert src.count(old) == 1, f"pattern khong duy nhat ({src.count(old)}x): {label}"
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "simulate_holistic_nav.py"), "w", encoding="utf-8").write(
                src.replace(old, new))
            open(os.path.join(td, "idle_cash_age_selfcheck.py"), "w", encoding="utf-8").write(self_src)
            # td FIRST on the path so the MUTATED copy wins; `here` after it for sibling imports.
            r = subprocess.run([sys.executable, "idle_cash_age_selfcheck.py"], cwd=td,
                               capture_output=True, text=True,
                               env={**os.environ, "PYTHONPATH": td + os.pathsep + here})
            ok = r.returncode != 0
            killed += ok
            first = next((l for l in (r.stderr or "").splitlines()[::-1] if l.strip()), "")
            print(f"  [{'KILLED' if ok else 'SURVIVED'}] {label}"
                  + ("" if ok else "   <-- LO HONG TEST") + (f"\n      {first[:120]}" if ok else ""))
    print(f"  mutation: {killed}/{len(MUTATIONS)} bi giet")
    return killed == len(MUTATIONS)


def run_all_tz():
    """§16: chung minh khong phu thuoc dong ho he thong — chay lai duoi 4 TZ + env -u TZ."""
    me = os.path.abspath(__file__)
    ok = True
    for tz in ("Asia/Ho_Chi_Minh", "UTC", "America/New_York", "Pacific/Kiritimati"):
        r = subprocess.run([sys.executable, me], capture_output=True, text=True,
                           env={**os.environ, "TZ": tz}, cwd=os.path.dirname(me))
        print(f"  [{'PASS' if r.returncode == 0 else 'FAIL'}] TZ={tz}")
        ok &= r.returncode == 0
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    r = subprocess.run([sys.executable, me], capture_output=True, text=True, env=env,
                       cwd=os.path.dirname(me))
    print(f"  [{'PASS' if r.returncode == 0 else 'FAIL'}] env -u TZ")
    ok &= r.returncode == 0
    return ok


if __name__ == "__main__":
    if "--all-tz" in sys.argv:
        print("== assertion duoi nhieu TZ ==")
        raise SystemExit(0 if run_all_tz() else 1)
    print("== assertion ==")
    tests()
    if "--mutations" in sys.argv:
        print("== mutation ==")
        if not run_mutations():
            raise SystemExit(1)
    print("OK")
