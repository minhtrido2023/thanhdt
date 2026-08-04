"""Capacity check v2 — ĐO TRỰC TIẾP ở mức park_mv THẬT của F1 (0,80) và F2 (0,85).

Vì sao cần: quant-skeptic (2026-08-04T02:16) ghi rõ `capacity_check.py` bản 1 chỉ đo ở
target 0,70 và mọi phát biểu về F2 là EXTRAPOLATION chưa verify trực tiếp.

Bản này parametrize 2 trục ĐỘC LẬP nhau:
  (a) TARGET — ảnh hưởng NHU CẦU trim hôm nay (target cao ⇒ trim ÍT hơn);
  (b) QUY MÔ SỔ PARK — ảnh hưởng nhu cầu trim khi phải THOÁT (regime rời NEUTRAL).
      Đây mới là trục quant-skeptic lo: F2 giữ park lớn hơn hẳn (30,4% NAV TB / 78,4% p95)
      so với Conservative (24,8% / 64,2%), đo trực tiếp từ sổ mô phỏng, không suy diễn.

Ràng buộc per-name T_bind = min_i(cap_i / w_i) KHÔNG phụ thuộc quy mô sổ (chỉ phụ thuộc
phân bố trọng số + ADV) — nên phần phải đo lại là NHU CẦU, và số PHIÊN cần để thoát.

KHÔNG sửa file production. Chỉ đọc. Cùng nguồn/định nghĩa ADV với capacity_check.py.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
ASOF = os.environ.get("ASOF", "2026-08-03")

LAG_ADV_PCT = 0.20
ETF_LIQ_PCT = 0.20
SHARE = 0.5                      # 2 account live

# park% NAV đo TRỰC TIẾP từ CSV mô phỏng (exposure_check.py, cùng vòng quét)
PARK_PCT = {                     # (trung bình, p95, max)
    "Conservative 0.70": (0.248, 0.642, 0.668),
    "F1  0.80":          (0.286, 0.735, 0.765),
    "F2  0.85":          (0.304, 0.784, 0.810),
}
TARGETS = {"Conservative 0.70": 0.70, "F1  0.80": 0.80, "F2  0.85": 0.85}

# ── 1. Rổ + ADV per-name (y hệt capacity_check.py) ───────────────────────────
bk = pd.read_csv(os.path.join(WORKDIR, "data", "custom30v_8l_publish.csv"))
bk = bk[bk.rebal_date == bk.rebal_date.max()].copy()
NAMES = list(bk.ticker)
print(f"[rổ] custom30V rebal={bk.rebal_date.iloc[0]}  n={len(NAMES)}")

tk = pd.read_parquet(os.path.join(WORKDIR, "data", "bq_cache", "ticker",
                                  f"{int(ASOF[:4])}.parquet"))
tk["time"] = pd.to_datetime(tk["time"])
tk = tk[(tk.ticker.isin(NAMES)) & (tk.time <= pd.Timestamp(ASOF))]

adv_live, px_last = {}, {}
for t in NAMES:
    d = tk[tk.ticker == t].sort_values("time")
    if not len(d):
        continue
    r = d.iloc[-1]
    px = r["Price"] if pd.notna(r["Price"]) else r["Close"]
    adv_live[t] = float(r["Volume_3M_P50"]) * float(px)
    px_last[t] = float(px)

tv = tk.copy()
tv["px"] = tv["Price"].fillna(tv["Close"])
tv["tv"] = tv["px"] * tv["Volume"]
adv_basket_engine = float(tv.groupby("time")["tv"].sum().sort_index().tail(60).mean())
day_cap_engine = ETF_LIQ_PCT * adv_basket_engine
print(f"[engine] ADV rổ 60 phiên = {adv_basket_engine/1e9:,.1f} tỷ/phiên"
      f"  →  _etf_day_cap = {day_cap_engine/1e9:,.1f} tỷ/phiên")

# ── 2. Sổ live: park_mv, cash, NAV (§12 — lọc account trước mọi phép tính) ────
CAPIT = {"NCT", "PVT", "SAB", "SIP", "VNM"}
EXCLUDED = {"ZaloPay": {"DGC"}, "SpaceX": set()}
pos_by_acct, cash_by_acct, tcash_by_acct = {}, {}, {}
for line in open(os.path.join(WORKDIR, "data", "execution_logs",
                              f"dnse_raw_{ASOF}.jsonl"), encoding="utf-8"):
    try:
        rec = json.loads(line)
    except Exception:
        continue
    lab = rec.get("account_label")
    if rec.get("kind") == "positions":
        p = {}
        for q in rec["payload"]["positions"]:
            qty = float(q.get("openQuantity") or 0)
            if qty <= 0:
                continue
            s = q["symbol"]
            prev = p.get(s, (0.0, 0.0))
            p[s] = (prev[0] + qty, float(q.get("marketPrice") or 0) or prev[1])
        pos_by_acct[lab] = p
    elif rec.get("kind") == "balances":
        st = rec["payload"].get("stock", {})
        cash_by_acct[lab] = float(st.get("availableCash") or 0)
        tcash_by_acct[lab] = float(st.get("totalCash") or 0) - float(st.get("totalDebt") or 0)


def park_book(acct):
    pos = pos_by_acct.get(acct, {})
    mv = {t: q * (mpx if mpx > 0 else px_last.get(t, 0.0))
          for t, (q, mpx) in pos.items()
          if t in NAMES and t not in CAPIT and t not in EXCLUDED[acct]}
    return {t: v for t, v in mv.items() if v > 0}


def nav(acct):
    pos = pos_by_acct.get(acct, {})
    mv = sum(q * (mpx if mpx > 0 else px_last.get(t, 0.0)) for t, (q, mpx) in pos.items())
    return mv + tcash_by_acct.get(acct, 0.0)


def t_bind(mv):
    """Trim TỔNG lớn nhất còn an toàn cho MỌI mã (pro-rata theo trọng số hiện tại)."""
    tot = sum(mv.values())
    c = [(t, (LAG_ADV_PCT * adv_live[t] * SHARE) / (v / tot))
         for t, v in mv.items() if adv_live.get(t, 0) > 0]
    return min(c, key=lambda kv: kv[1])


ACCTS = ("SpaceX", "ZaloPay")
print("\n" + "=" * 100)
print("A. NHU CẦU TRIM HÔM NAY, ĐO TRỰC TIẾP ở TỪNG target (không ngoại suy)")
print("=" * 100)
print(f"{'Cấu hình':20s} {'acct':8s} {'park_mv(tr)':>12s} {'cash(tr)':>10s} {'target(tr)':>11s} "
      f"{'cần trim(tr)':>13s} {'max %ADV':>10s} {'dư địa':>10s}")
rows = []
for lab, tgt in TARGETS.items():
    for acct in ACCTS:
        mv = park_book(acct)
        pm, cash = sum(mv.values()), cash_by_acct.get(acct, 0.0)
        pool = pm + cash
        trim = min(max(pm - pool * tgt, 0.0), day_cap_engine)
        tb_t, tb_v = t_bind(mv)
        if trim <= 0:
            print(f"{lab:20s} {acct:8s} {pm/1e6:>12,.1f} {cash/1e6:>10,.1f} "
                  f"{pool*tgt/1e6:>11,.1f} {'0 (không trim)':>13s} {'—':>10s} {'—':>10s}")
            continue
        mx = max((w / pm * trim) / adv_live[t] for t, w in mv.items() if adv_live.get(t, 0) > 0)
        print(f"{lab:20s} {acct:8s} {pm/1e6:>12,.1f} {cash/1e6:>10,.1f} "
              f"{pool*tgt/1e6:>11,.1f} {trim/1e6:>13,.1f} {mx*100:>9.3f}% "
              f"{tb_v/max(trim,1):>9,.0f}×")
        rows.append({"cfg": lab, "acct": acct, "trim_tr": trim / 1e6,
                     "max_pct_adv": mx * 100, "headroom_x": tb_v / max(trim, 1),
                     "bind_ticker": tb_t, "t_bind_ty": tb_v / 1e9})

print("\n" + "=" * 100)
print("B. STRESS — THOÁT SỔ PARK Ở QUY MÔ RIÊNG CỦA TỪNG CẤU HÌNH")
print("   (regime rời NEUTRAL ⇒ target→0; park_mv = park%NAV của CHÍNH cấu hình đó × NAV live)")
print("=" * 100)
for acct in ACCTS:
    mv = park_book(acct)
    N = nav(acct)
    tb_t, tb_v = t_bind(mv)
    rate = min(day_cap_engine, tb_v)          # tốc độ thoát an toàn/phiên
    print(f"\n--- {acct} — NAV={N/1e6:,.1f}tr · park hiện tại={sum(mv.values())/1e6:,.1f}tr "
          f"({sum(mv.values())/N*100:.1f}% NAV) · T_bind={tb_v/1e9:,.1f} tỷ ({tb_t}) "
          f"· engine cap={day_cap_engine/1e9:,.1f} tỷ ⇒ tốc độ ràng buộc={rate/1e9:,.1f} tỷ/phiên")
    print(f"    {'cấu hình':20s} {'park%NAV':>9s} {'park_mv(tr)':>12s} {'phiên để thoát':>15s} "
          f"{'max %ADV/phiên':>15s}")
    for lab, (tb_, p95, mx_) in PARK_PCT.items():
        for tag, pct in (("TB", tb_), ("p95", p95), ("max", mx_)):
            pm = pct * N
            sess = pm / rate
            one = min(pm, rate)
            wmax = max((w / sum(mv.values())) for w in mv.values())
            # mã nặng nhất theo %ADV khi bán ở tốc độ `rate`
            madv = max((w / sum(mv.values()) * one) / adv_live[t]
                       for t, w in mv.items() if adv_live.get(t, 0) > 0)
            print(f"    {lab + ' [' + tag + ']':20s} {pct*100:>8.1f}% {pm/1e6:>12,.1f} "
                  f"{sess:>14.2f}  {madv*100:>14.3f}%")

print("\n" + "=" * 100)
print("C. NGƯỠNG THẬT SỰ BINDING — park_mv phải LỚN CỠ NÀO thì mới cần >1 phiên để thoát?")
print("=" * 100)
for acct in ACCTS:
    mv = park_book(acct)
    N = nav(acct)
    tb_t, tb_v = t_bind(mv)
    rate = min(day_cap_engine, tb_v)
    print(f"  {acct}: thoát trong 1 phiên an toàn tới park_mv = {rate/1e9:,.1f} tỷ "
          f"= {rate/N*100:,.0f}% NAV hiện tại ⇒ NAV phải gấp "
          f"{rate/(0.784*N):,.0f}× hiện tại thì mức p95 của F2 mới chạm ngưỡng")
