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

HAI CHE DO TRA, hai nghia khac nhau (dung lan la ra hai con so khac nhau):
  pay_mode="daily"    = quy uoc THAN TRONG dang pin (25,24%): r/252 moi phien tu phien min_age+1,
                        min_age phien dau KHONG BAO GIO duoc truy linh => lo song n phien duoc tra
                        n-min_age ngay. Tra THIEU so voi mot so tiet kiem 1 thang dao han lien tuc.
  pay_mode="maturity" = luat user chot doc DUNG NGHIA (quant-skeptic 2026-09-28, user duyet 12:05
                        ICT): moi moc min_age phien cua mot lo credit dung min_age phien lai theo
                        rate PIT cua chinh nhung phien do => lo song n phien duoc tra
                        min_age*floor(n/min_age) ngay >= che do daily. Ky han DO DANG khi tien bi
                        tieu van huong 0%. Vi vay `daily` la CHAN DUOI cua `maturity`.

Ba tang test, co y:
  T1..T6 = UNIT tren `idle_lots_reconcile` / `idle_lots_eligible` (ngu nghia so lo).
  T7..T10 = END-TO-END mot lan `simulate()` that tren panel tong hop 60 phien, gia co dinh,
            deposit_annual = 0.0252 (=> r/252 = 1.000e-4 chan) => moi so lai KIEM TAY duoc.
            Tang nay moi la thu chung minh WIRING dung cho: tang tuoi o DAU phien, reconcile
            2 lan/phien, va chi tra cho phan du tuoi.
  T12..T17 = che do maturity: T12..T14 unit tren `idle_lots_mature`/`idle_lots_accrue`, T15 e2e
            rate co dinh (cuc o dung phien 21/42), T16 e2e rate BIEN THIEN (chung minh dung
            rate-SUM PIT chu khong xap xi — mutation M16 chi chet o day), T17 panel straddle
            (tien tieu giua ky han huong 0% that).

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


def _run(min_age, order, n_sessions=60, sig_session=30, max_positions=4, hold_days=999,
         pay_mode="daily", rate=None):
    sig, px, dates = _panel(n_sessions, sig_session)
    log = []
    nav, _tr = S.simulate(
        sig, px, dates, allowed_tiers=["SIGNAL_V11"], max_positions=max_positions,
        hold_days=hold_days, stop_loss=-0.99, min_hold=2, slippage=0.0,
        init_nav=NAV0, deposit_annual=(RATE if rate is None else rate), borrow_annual=0.0,
        deposit_min_age_sessions=min_age, deposit_age_order=order,
        deposit_pay_mode=pay_mode,
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


def _run_straddle(order="fifo", n_sessions=60, pay_mode="daily"):
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
        deposit_age_order=order, deposit_pay_mode=pay_mode,
        idle_age_log=log, reentry_blacklist_days=0,
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


# ------------------------------------------- T12..T17: che do TRA KHI DAO HAN (pay_mode=maturity)
# Lap luan quant-skeptic 2026-09-28 (Mike + user xac nhan 12:05 ICT): che do `daily` KHONG truy linh
# la mot QUY UOC THAN TRONG, khong phai rang buoc nhan qua — tra mot ky han DA DI HET vao dung phien
# ky vong cua no la nhan qua. Che do `maturity` hien thuc hoa dung luat user chot: moi moc 21 phien
# cua mot lo duoc credit dung 21 phien lai theo rate PIT cua chinh 21 phien do; ky han DO DANG khi
# tien bi tieu => 0%. Vi `daily` tra n-21 ngay con `maturity` tra 21*floor(n/21) ngay, `maturity`
# LUON >= `daily` (T15 do dieu do end-to-end).
def maturity_unit_tests():
    R, M, A = S.idle_lots_reconcile, S.idle_lots_mature, S.idle_lots_accrue
    TAIL = (0.0, 0)

    # T12 — so lo 4 truong + dong ho ky han: mature TRUOC accrue => tra o dung moc thu 21
    lots = []
    R(lots, 100.0, "fifo", TAIL)
    ck(lots == [[0, 100.0, 0.0, 0]], "T12a lo maturity = [age 0, amt, accrued 0, term_days 0]")
    for k in range(MIN_AGE):                      # mo phong 21 phien: mature (0) roi accrue
        ck(near(M(lots, MIN_AGE), 0.0), f"T12b phien {k}: chua du ky han => tra 0")
        A(lots, PER)
    ck(lots[0][3] == MIN_AGE, f"T12c sau 21 phien term_days = 21 (do {lots[0][3]})")
    ck(near(lots[0][2], MIN_AGE * PER), "T12d accrued = TONG 21 phien rate (khong phai binh quan)")
    ck(near(M(lots, MIN_AGE), 100.0 * MIN_AGE * PER),
       "T12e phien thu 22 tra TRON ky han = amt x 21 x r/252")
    ck(lots[0][2] == 0.0 and lots[0][3] == 0, "T12f sau khi tra, ky han reset ve 0 (khong tra 2 lan)")
    ck(near(M(lots, MIN_AGE), 0.0), "T12g goi lai ngay sau do tra 0 (khong tra trung)")

    # T13 — RUT TRUOC HAN = 0%: ky han do dang bi tieu thi khong bao gio duoc tra
    lots = [[30, 100.0, MIN_AGE * PER - PER, MIN_AGE - 1]]      # con 1 phien nua la dao han
    R(lots, 0.0, "fifo", TAIL)
    ck(lots == [], "T13a tieu het o phien cuoi ky han => lo bien mat")
    ck(near(M(lots, MIN_AGE), 0.0), "T13b => khong mot dong lai nao duoc tra (rut truoc han = 0%)")
    # tieu MOT PHAN: rate-SUM di theo GOC CON LAI, khong theo goc ban dau
    lots = [[30, 100.0, 0.0020, MIN_AGE - 1], [0, 50.0, 0.0, 0]]
    R(lots, 100.0, "fifo", TAIL)                                # fifo an 50 cua lo GIA
    ck(near(lots[0][1], 50.0), "T13c FIFO an 50 vao lo gia")
    A(lots, PER)
    ck(near(M(lots, MIN_AGE), 50.0 * (0.0020 + PER)),
       "T13d dao han tra tren GOC CON LAI 50 x rate-sum, KHONG phai 100 (phan da tieu huong 0%)")

    # T14 — lai tra KHONG nhap goc: goc lo khong doi sau khi tra
    lots = [[0, 100.0, MIN_AGE * PER, MIN_AGE]]
    paid = M(lots, MIN_AGE)
    ck(near(lots[0][1], 100.0) and paid > 0,
       "T14 lai tra ra KHONG cong vao goc lo (lai tu de lai tu tuoi 0 qua reconcile)")


def maturity_e2e_tests():
    # T15 — panel KHONG giao dich, rate CO DINH: lai la nhung CUC o dung phien 21 va 42
    nav, log = _run(MIN_AGE, "fifo", n_sessions=60, sig_session=99, pay_mode="maturity")
    ints = nav["interest"].to_numpy()
    LUMP = NAV0 * MIN_AGE * PER
    ck(near(ints[:MIN_AGE].sum(), 0.0, 0), f"T15a phien 0..20 tra 0 VND (do {ints[:MIN_AGE].sum()})")
    ck(near(ints[MIN_AGE], LUMP), f"T15b phien 21 tra TRON 21 phien = {LUMP:.1f} (do {ints[MIN_AGE]:.1f})")
    ck(near(ints[MIN_AGE + 1:2 * MIN_AGE].sum(), 0.0, 0), "T15c giua 2 moc dao han tra 0 VND")
    ck(near(ints[2 * MIN_AGE], LUMP), f"T15d phien 42 tra cuc thu hai = {LUMP:.1f}")
    ck(near(ints[2 * MIN_AGE + 1], LUMP * MIN_AGE * PER),
       "T15e phien 43: cuc cua chinh CUC LAI phien 21 (lo rieng, dong ho ky han rieng)")
    ck(sorted(np.flatnonzero(np.abs(ints) > 1e-9)) == [MIN_AGE, 2 * MIN_AGE, 2 * MIN_AGE + 1],
       f"T15f lai CHI xuat hien o 3 phien 21/42/43 — moi phien khac tra 0 "
       f"(do {list(np.flatnonzero(np.abs(ints) > 1e-9))})")
    # doi chieu voi che do daily tren CUNG panel. Don vi = NAV0*r/252 = 1 "ngay lai tren toan bo NAV":
    # maturity tra 2 cuc x 21 = 42 ngay; daily tra tung phien tu index 21..59 = 39 ngay.
    navD, _ = _run(MIN_AGE, "fifo", n_sessions=60, sig_session=99, pay_mode="daily")
    tot_m, tot_d = ints.sum(), navD["interest"].to_numpy().sum()
    ck(tot_m > tot_d, f"T15f2 maturity ({tot_m:.0f}) > daily ({tot_d:.0f}) — daily la CHAN DUOI")
    ck(near(tot_m / (NAV0 * PER), 42.0, 2e-3),
       f"T15g maturity tra dung 42 ngay (2 cuc x 21); do {tot_m/(NAV0*PER):.4f}")
    ck(near(tot_d / (NAV0 * PER), 39.0, 2e-3),
       f"T15g2 daily tra dung 39 ngay (index 21..59); do {tot_d/(NAV0*PER):.4f}")
    ck(navD["nav"].iloc[-1] < nav["nav"].iloc[-1], "T15h => NAV cuoi daily < NAV cuoi maturity")
    ck((log["pay_mode"] == "maturity").all(), "T15i idle_age_log ghi ro pay_mode cua chan")

    # T16 — rate BIEN THIEN theo phien: cuc phai bang TONG 21 rate PIT cua dung 21 phien do,
    #       khong phai 21 x rate cua phien tra. Day la thu CHUNG MINH tinh CHINH XAC (khong xap xi).
    _sig, _px, dates = _panel(60, 99)
    rser = {d: RATE * (1.0 + i / 20.0) for i, d in enumerate(dates)}   # tang deu, gap 3.9x cuoi ky
    navV, logV = _run(MIN_AGE, "fifo", n_sessions=60, sig_session=99, pay_mode="maturity", rate=rser)
    iv = navV["interest"].to_numpy()
    exp1 = NAV0 * sum(rser[d] for d in dates[:MIN_AGE]) / 252
    exp2 = NAV0 * sum(rser[d] for d in dates[MIN_AGE:2 * MIN_AGE]) / 252
    ck(near(iv[MIN_AGE], exp1), f"T16a cuc 1 = TONG rate phien 0..20 = {exp1:.2f} (do {iv[MIN_AGE]:.2f})")
    ck(near(iv[2 * MIN_AGE], exp2, 1e-4),
       f"T16b cuc 2 = TONG rate phien 21..41 = {exp2:.2f} (do {iv[2*MIN_AGE]:.2f})")
    ck(not near(iv[MIN_AGE], NAV0 * MIN_AGE * rser[dates[MIN_AGE]] / 252, 1e-3),
       "T16c cuc 1 KHAC 21 x rate cua phien tra (chung minh dung rate-SUM PIT, khong phai rate hom tra)")
    ck((logV["eligible"].to_numpy()[[MIN_AGE, 2 * MIN_AGE]] > 0).all()
       and near(logV["eligible"].to_numpy()[MIN_AGE - 1], 0.0, 0),
       "T16d `eligible` cua che do maturity = GOC dao han phien do (0 o phien khong dao han)")

    # T17 — panel straddle: tien RA giua ky han thi huong 0%, tien VE bat dong ho ky han MOI
    navS, logS = _run_straddle("fifo", pay_mode="maturity")
    iS = navS["interest"].to_numpy()
    eS = logS["eligible"].to_numpy()
    # BBB da mua o phien 6 nen o phien 21 chi con ~750M nam im; 250M kia dang la co phieu.
    ck(near(eS[MIN_AGE], 7.5e8, 1e-3) and near(iS[MIN_AGE], eS[MIN_AGE] * MIN_AGE * PER),
       f"T17a cuc phien 21 tra tren ~750M dang nam im (do {eS[MIN_AGE]:.0f})")
    # phien 42: goc dao han chi con ~500M (250M da bi FIFO an cuoi phien 31, 250M ve phien 32 la lo MOI)
    ck(4.5e8 < eS[2 * MIN_AGE] < 5.6e8,
       f"T17b phien 42 goc dao han ~500M, KHONG phai ~750M (do {eS[2*MIN_AGE]:.0f})")
    ck(near(iS[2 * MIN_AGE], eS[2 * MIN_AGE] * MIN_AGE * PER),
       "T17c cuc phien 42 = goc dao han x 21 x r/252 (250M da tieu huong 0%)")
    ck(sorted(np.flatnonzero(np.abs(iS) > 1e-9)) == [MIN_AGE, 2 * MIN_AGE, 2 * MIN_AGE + 1, 32 + MIN_AGE],
       f"T17d lai CHI o 4 phien 21/42/43/53 (43 = cuc cua cuc phien 21) "
       f"(do {list(np.flatnonzero(np.abs(iS) > 1e-9))})")
    ck(2.0e8 < eS[32 + MIN_AGE] < 2.6e8 and near(iS[32 + MIN_AGE], eS[32 + MIN_AGE] * MIN_AGE * PER),
       f"T17e phien 53 = 32+21: lo ~250M ve phien 32 dao han lan dau, tra tron 21 phien "
       f"(do goc {eS[32+MIN_AGE]:.0f})")
    # bat bien chung cho MOI phien duoi rate co dinh: interest == goc dao han x 21 x r/252
    ck(np.abs(iS - eS * MIN_AGE * PER).max() < 1.0,
       f"T17f bat bien moi phien: interest == eligible x 21 x r/252 "
       f"(lech max {np.abs(iS - eS*MIN_AGE*PER).max():.3e})")
    # chan tren cua dai: maturity van THAP hon carry tra hang ngay tu phien dau (min_age=0)
    nav0, _ = _run_straddle("fifo", pay_mode="daily")
    ck(navS["nav"].iloc[-1] > nav0["nav"].iloc[-1],
       "T17g NAV maturity > NAV daily tren cung panel co giao dich")


def tests():
    unit_tests()
    e2e_tests()
    round_trip_tests()
    maturity_unit_tests()
    maturity_e2e_tests()
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
    # --- che do TRA KHI DAO HAN (pay_mode=maturity) ---
    ("M12 maturity: accrue TRUOC mature => dao han som 1 phien (moc 20 thay vi 21)",
     "            cash += idle_lots_mature(_cash_lots, _age_min)\n"
     "            idle_lots_accrue(_cash_lots, max(_dep_today, 0.0) / 252)",
     "            idle_lots_accrue(_cash_lots, max(_dep_today, 0.0) / 252)\n"
     "            cash += idle_lots_mature(_cash_lots, _age_min)"),
    ("M13 maturity: TRA CA KY HAN DO DANG (xoa nghia 'rut truoc han = 0%')",
     "        if lot[IDLE_LOT_TERM_DAYS] >= term_sessions:",
     "        if lot[IDLE_LOT_TERM_DAYS] >= 1:"),
    ("M14 maturity: khong reset rate-sum sau khi tra => tra trung, cong don vo han",
     "            paid += lot[1] * lot[IDLE_LOT_ACCRUED]\n"
     "            lot[IDLE_LOT_ACCRUED] = 0.0\n"
     "            lot[IDLE_LOT_TERM_DAYS] = 0",
     "            paid += lot[1] * lot[IDLE_LOT_ACCRUED]\n"
     "            lot[IDLE_LOT_TERM_DAYS] = 0"),
    ("M15 maturity: lai nhap GOC lo (gop lai trong ky han, lai thua huong tuoi cua goc)",
     "            paid += lot[1] * lot[IDLE_LOT_ACCRUED]\n",
     "            paid += lot[1] * lot[IDLE_LOT_ACCRUED]\n"
     "            lot[1] += lot[1] * lot[IDLE_LOT_ACCRUED]\n"),
    ("M16 maturity: tra 21 x rate cua PHIEN TRA thay vi TONG rate PIT cua 21 phien "
     "(chi T16 rate-bien-thien giet duoc — day la ly do T16 ton tai)",
     "            cash += idle_lots_mature(_cash_lots, _age_min)",
     "            idle_lots_mature(_cash_lots, _age_min)\n"
     "            cash += _age_elig * _age_min * max(_dep_today, 0.0) / 252"),
    ("M17 maturity: dong ho ky han dem theo TUOI lo thay vi so phien DA ACCRUE "
     "(lech 1 phien cho moi lo sinh o 6z, vd chinh cuc lai vua tra)",
     "            _age_elig = sum(lot[1] for lot in _cash_lots\n"
     "                            if lot[IDLE_LOT_TERM_DAYS] >= _age_min)\n"
     "            cash += idle_lots_mature(_cash_lots, _age_min)",
     "            _age_elig = sum(lot[1] for lot in _cash_lots if lot[0] >= _age_min)\n"
     "            cash += sum(lot[1] * lot[IDLE_LOT_ACCRUED] for lot in _cash_lots\n"
     "                        if lot[0] >= _age_min)\n"
     "            for _l in _cash_lots:\n"
     "                if _l[0] >= _age_min:\n"
     "                    _l[IDLE_LOT_ACCRUED] = 0.0\n"
     "                    _l[IDLE_LOT_TERM_DAYS] = 0"),
    ("M18 maturity: lo moi sinh ra da co san 1 phien ky han => MOI lo dao han som 1 phien",
     '    _age_tail = (0.0, 0) if _age_mode == "maturity" else ()',
     '    _age_tail = (0.0, 1) if _age_mode == "maturity" else ()'),
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
