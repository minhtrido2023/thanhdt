#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2b — park_holdings / compute_park_trim (L1) / compute_jit_unpark (L2) qua vòng đời quyền mua
SCL (LAG 14.000cp, quyền 14:5 @12.500). Sandbox tạm, account giả. Chạy:
  $DNA_PYEXE b3_b2_park_unpark.py   (hoặc python3)"""
import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b3_common as C  # noqa: E402  (đặt MIKE_BOT_TEST_MODE trước mọi import trading_bot)
import compute_park_trim as cpt  # noqa: E402
import compute_jit_unpark as cju  # noqa: E402

E = dt.date(2026, 10, 26)
T0 = C.nth_session_after(E, 10)          # GDKHQ quyền mua
PAY = C.nth_session_after(T0, 5)         # user nộp tiền quyền
CREDIT = C.nth_session_after(T0, 18)     # dạng A: CP mới vào openQuantity (chưa niêm yết)
LIST = C.nth_session_after(T0, 60)       # niêm yết bổ sung
TARGET = cpt.park_target_from_rules(cpt.PARK_TARGET_RULES)   # R3 thật — CHỈ ĐỌC
CASH0, EGG = 150e6, 300e6

td, EX, PL = C.sandbox()
C.write_journal(EX, E.isoformat(), [(C.LAG_TK, "buy", C.QTY_OLD, C.PX_CUM, "LAG")])

# (nhãn, asof, open, trade, giá SCL, totalCash, availableCash)
STAGES = [
    ("S0 trước GDKHQ", C.nth_session_after(E, 9), 14_000, 14_000, C.PX_CUM, CASH0, CASH0),
    ("S1 ngày GDKHQ (KL không đổi, giá tham chiếu giảm)", T0, 14_000, 14_000, C.PX_EX, CASH0, CASH0),
    ("S2 sau khi user nộp 62,5tr (CP chưa về)", PAY, 14_000, 14_000, C.PX_EX,
     CASH0 - C.PAYMENT, CASH0 - C.PAYMENT),
    ("S3A CP mới vào openQuantity, chưa niêm yết (dạng A)", CREDIT, 19_000, 14_000, C.PX_EX,
     CASH0 - C.PAYMENT, CASH0 - C.PAYMENT),
    ("S3B dạng B — chưa niêm yết thì broker chưa hiện", CREDIT, 14_000, 14_000, C.PX_EX,
     CASH0 - C.PAYMENT, CASH0 - C.PAYMENT),
    ("S4 sau niêm yết (19.000/19.000)", LIST, 19_000, 19_000, C.PX_EX,
     CASH0 - C.PAYMENT, CASH0 - C.PAYMENT),
]


def run_l1(h, asof):
    fd, path = tempfile.mkstemp(suffix=".json", dir=td)
    os.close(fd)
    json.dump({"state": 3, "state_name": "NEUTRAL", "date": asof, "etf_park_frac": TARGET},
              open(path, "w"))
    old = cpt.STATE_FILE
    cpt.STATE_FILE = path
    try:
        return cpt.compute_trim(C.ACCOUNT, asof, TARGET, holdings=h, share_override=1.0,
                                adv_fn=lambda tk, a: (1e12, a, None), day_cap_override=10e9,
                                basket_override={"FPT": 0.5, "MBB": 0.5},
                                price_fn=C.price_fn_for(C.PX_EX),
                                excluded_dividend_config_override=[])
    finally:
        cpt.STATE_FILE = old


def run_l2(h, asof):
    buy = {"id": "BUY-HPG", "ticker": "HPG", "side": "buy", "qty": 4_000, "ref_price": 30_000,
           "book": "LAG", "play_type": "LAG_HI", "priority": 1}     # 120tr > cash ⇒ cần unpark
    return cju.compute_jit_unpark(C.ACCOUNT, asof=asof, orders=[buy], holdings=h,
                                  share_override=0.5,
                                  adv_fn=lambda tk, a: (50e9, a, None), day_cap_override=5e9)


print(f"E={E} T0(GDKHQ)={T0} PAY={PAY} CREDIT={CREDIT} LIST={LIST} target R3={TARGET}")
for label, d, op, tr, px, tc, av in STAGES:
    asof = d.isoformat()
    C.write_raw(EX, asof, op, tr, px, cash_total=tc, cash_avail=av, egg=EGG)
    h = C.holdings(asof, PL, EX, px)
    l1 = run_l1(h, asof)
    l2 = run_l2(h, asof)
    lag = sum(l["qty"] for l in h["lots"] if l["book"] == "LAG")
    print(f"\n== {label} asof={asof}")
    print(f"  park_holdings: reconcile_ok={h['reconcile']['ok']} mismatches="
          f"{h['reconcile']['mismatches']} unverified={h['unverified_tickers']} sổ LAG={lag} "
          f"broker SCL={h['broker_positions'].get('SCL')}")
    print(f"  L1 decision={l1.get('decision')} pool={l1.get('pool_vnd', 0)/1e6:,.1f}tr "
          f"delta={l1.get('delta_vnd', 0)/1e6:,.1f}tr orders="
          f"{[(o['ticker'], o.get('qty')) for o in l1.get('orders', [])]}")
    print(f"  L2 decision={l2.get('decision')} cash_start={l2.get('cash_start_vnd', 0)/1e6:,.1f}tr "
          f"orders={[(o['ticker'], o.get('qty')) for o in l2.get('orders', [])]}")
    if not h["reconcile"]["ok"]:
        print(f"  L1 note: {l1['notes'][0][:160]}")

# ── Thử "lối thoát" sẵn có: ghi corp_actions loại RIGHTS ⇒ validate() có nhận không? ──
print("\n== corp_actions: record event_type=RIGHTS (kể cả PROPOSED, chưa ký)")
import corp_actions as ca  # noqa: E402
reg = os.path.join(td, "corp_actions.json")
json.dump({"actions": [{"id": "SCL-RIGHTS", "ticker": "SCL", "event_type": "RIGHTS",
                        "qty_multiplier": 19 / 14, "ex_date": T0.isoformat(),
                        "record_date": T0.isoformat(),
                        "broker_effective_ts": f"{CREDIT}T19:00:00", "_status": "PROPOSED"}]},
          open(reg, "w"))
for fn in ("load_all", "load_corp_actions"):
    try:
        r = getattr(ca, fn)(reg)
        print(f"  {fn}: OK {r}")
    except Exception as e:
        print(f"  {fn}: {type(e).__name__}: {str(e)[:200]}")

# ── Lối thoát giả-dạng: BONUS_ISSUE ×19/14 CONFIRMED (KHÔNG khuyến nghị — đo hệ quả giá vốn) ──
print("\n== workaround BONUS_ISSUE ×19/14 tại S3A")
act = {"id": "SCL-RIGHTS-AS-BONUS", "ticker": "SCL", "event_type": "BONUS_ISSUE",
       "qty_multiplier": 19 / 14, "ex_date": T0.isoformat(), "record_date": T0.isoformat(),
       "broker_effective_ts": f"{CREDIT}T19:00:00", "_status": "CONFIRMED test",
       "evidence": ["a", "b"]}
C.write_raw(EX, CREDIT.isoformat(), 19_000, 14_000, C.PX_EX, cash_total=CASH0 - C.PAYMENT,
            cash_avail=CASH0 - C.PAYMENT, egg=EGG)
h = C.holdings(CREDIT.isoformat(), PL, EX, C.PX_EX, corp_actions=[act])
lots = [(l["book"], l["qty"], round(l["price"]), l["entry_date"]) for l in h["lots"]
        if l["ticker"] == "SCL"]
print(f"  reconcile_ok={h['reconcile']['ok']} lô SCL={lots} (giá vốn thật = "
      f"{(C.QTY_OLD*C.PX_CUM + C.PAYMENT)/19_000:,.0f}đ/cp)")
print(f"  L1={run_l1(h, CREDIT.isoformat()).get('decision')}  "
      f"L2={run_l2(h, CREDIT.isoformat()).get('decision')}")
# ── Độ nhạy L1 với khoản nộp 62,5tr nếu PARK bật lại (R3 hiện = 0.0 ⇒ delta = −park_mv, KHÔNG nhạy) ──
print("\n== Độ nhạy L1 với khoản nộp tiền quyền, target giả định 0.30 (mức trước 2026-10-01)")
for label, d, tc in (("S1 trước nộp", T0, CASH0), ("S2 sau nộp", PAY, CASH0 - C.PAYMENT)):
    C.write_raw(EX, d.isoformat(), 14_000, 14_000, C.PX_EX, cash_total=tc, cash_avail=tc, egg=EGG)
    hh = C.holdings(d.isoformat(), PL, EX, C.PX_EX)
    old_t = TARGET
    TARGET = 0.30
    r = run_l1(hh, d.isoformat())
    TARGET = old_t
    print(f"  {label}: decision={r.get('decision')} pool={r['pool_vnd']/1e6:,.1f}tr "
          f"target_value={r['target_park_vnd']/1e6:,.2f}tr delta={r['delta_vnd']/1e6:,.2f}tr "
          f"orders={[(o['ticker'], o.get('qty')) for o in r.get('orders', [])]}")
print(f"\nsandbox={td}")
