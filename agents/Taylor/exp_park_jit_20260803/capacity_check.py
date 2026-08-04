"""Việc 1 — vá lỗ hổng capacity của thiết kế L1/L2 (killer_objection quant-skeptic 2026-08-03).

Câu hỏi: nếu L1 trim PARK pro-rata theo trọng số hiện tại để đạt tổng VND cần thiết, MỖI MÃ
trong rổ custom30V bị bán bao nhiêu % ADV RIÊNG của nó, và có mã nào vượt tiền lệ %ADV đang
dùng cho LAG live (`trading_bot.plan.LAG_ADV_PCT` = 20% × share) hay không?

ĐỊNH NGHĨA ADV — dùng ĐÚNG công thức của gate live `cap_lag_orders`:
    adv_i = Volume_3M_P50_i × COALESCE(Price_i, Close_i)      (due_diligence.adv_vnd)
Trần rổ của engine (`_etf_day_cap`) dùng công thức KHÁC (60-phiên rolling mean của
Σ_i Price_i×Volume_i — trading value THẬT, không phải trung vị 3M) nên script tính CẢ HAI để
so được, và KHÔNG trộn hai định nghĩa vào cùng một phép chia.

KHÔNG sửa file production. Chỉ đọc.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
ASOF = os.environ.get("ASOF", "2026-08-03")

LAG_ADV_PCT = 0.20          # trading_bot/plan.py:376 — tiền lệ %ADV đang dùng LIVE cho book LAG
ETF_LIQ_PCT = 0.20          # pt_v23_audit_2014.py:206 — trần %ADV của rổ park trong engine
N_LIVE_ACCOUNTS = 2         # SpaceX + ZaloPay → share = 1/2 trong cap_lag_orders
SHARE = 1.0 / N_LIVE_ACCOUNTS

# ── 1. Rổ custom30V hiện hành + trọng số mục tiêu ─────────────────────────────
bk = pd.read_csv(os.path.join(WORKDIR, "data", "custom30v_8l_publish.csv"))
bk = bk[bk.rebal_date == bk.rebal_date.max()].copy()
REBAL = str(bk.rebal_date.iloc[0])
NAMES = list(bk.ticker)
w_target = dict(zip(bk.ticker, bk.weight))
print(f"[rổ] custom30V rebal={REBAL}  n={len(NAMES)}  Σw={sum(w_target.values()):.4f}")

# ── 2. ADV per-name theo ĐÚNG công thức gate live ─────────────────────────────
yr = int(ASOF[:4])
tk = pd.read_parquet(os.path.join(WORKDIR, "data", "bq_cache", "ticker", f"{yr}.parquet"))
tk["time"] = pd.to_datetime(tk["time"])
tk = tk[(tk.ticker.isin(NAMES)) & (tk.time <= pd.Timestamp(ASOF))]

adv_live, data_date, px_last = {}, {}, {}
for t in NAMES:
    d = tk[tk.ticker == t].sort_values("time")
    if not len(d):
        adv_live[t] = np.nan
        continue
    r = d.iloc[-1]
    px = r["Price"] if pd.notna(r["Price"]) else r["Close"]
    adv_live[t] = float(r["Volume_3M_P50"]) * float(px)
    data_date[t] = str(r["time"])[:10]
    px_last[t] = float(px)

# ── 3. ADV rổ theo ĐÚNG công thức engine (_etf_day_cap) ───────────────────────
tv = tk.copy()
tv["px"] = tv["Price"].fillna(tv["Close"])
tv["tv"] = tv["px"] * tv["Volume"]
daily = tv.groupby("time")["tv"].sum().sort_index()
adv_basket_engine = float(daily.tail(60).mean())
day_cap_engine = ETF_LIQ_PCT * adv_basket_engine
print(f"[engine] ADV rổ (60 phiên, Σ Price×Volume) = {adv_basket_engine/1e9:,.1f} tỷ/phiên"
      f"  →  _etf_day_cap = {day_cap_engine/1e9:,.1f} tỷ/phiên")
print(f"[live]   Σ ADV per-name (Volume_3M_P50×Price) = "
      f"{np.nansum(list(adv_live.values()))/1e9:,.1f} tỷ/phiên")

# ── 4. PARK live per-name (suy luận theo tên — hạn chế A7, ghi rõ) ────────────
CAPIT = {"NCT", "PVT", "SAB", "SIP", "VNM"}       # golive_v23_status.capit_episode_basket
EXCLUDED = {"ZaloPay": {"DGC"}, "SpaceX": set()}   # trading_bot config excluded_tickers

raw = os.path.join(WORKDIR, "data", "execution_logs", f"dnse_raw_{ASOF}.jsonl")
pos_by_acct, cash_by_acct = {}, {}
for line in open(raw, encoding="utf-8"):
    try:
        rec = json.loads(line)
    except Exception:
        continue
    lab = rec.get("account_label")
    if rec.get("kind") == "positions":
        # openQuantity = số CP ĐANG GIỮ. KHÔNG dùng accumulateQuantity (= tổng đã mua tích luỹ,
        # gồm cả phần đã bán: ACB 1800 accumulate vs 1500 open / 300 closed) — dùng nhầm field này
        # thổi PARK SpaceX từ 642tr lên 1.150tr. Giá = marketPrice của broker (§6 DNSE, không BQ).
        p = {}
        for q in rec["payload"]["positions"]:
            qty = float(q.get("openQuantity") or 0)
            if qty <= 0:
                continue
            s = q["symbol"]
            prev = p.get(s, (0.0, 0.0))
            p[s] = (prev[0] + qty, float(q.get("marketPrice") or 0) or prev[1])
        pos_by_acct[lab] = p                       # bản ghi MỚI NHẤT thắng
    elif rec.get("kind") == "balances":
        st = rec["payload"].get("stock", {})
        cash_by_acct[lab] = float(st.get("availableCash") or 0)   # §B5: availableCash, không totalCash

rows = []
for acct in ("SpaceX", "ZaloPay"):
    pos = pos_by_acct.get(acct, {})
    park = {t: v for t, v in pos.items()
            if t in NAMES and t not in CAPIT and t not in EXCLUDED[acct]}
    mv = {t: q * (mpx if mpx > 0 else px_last.get(t, 0.0)) for t, (q, mpx) in park.items()}
    mv = {t: v for t, v in mv.items() if v > 0}
    park_mv = sum(mv.values())
    cash = cash_by_acct.get(acct, 0.0)
    pool = park_mv + cash
    target = pool * 0.70                            # ETF_PARK[NEUTRAL] = 0.70
    excess = park_mv - target
    trim = min(max(excess, 0.0), day_cap_engine)    # trần rổ của engine
    print(f"\n=== {acct} ===  park_mv={park_mv/1e6:,.1f}tr  cash={cash/1e6:,.1f}tr  "
          f"pool={pool/1e6:,.1f}tr  target70%={target/1e6:,.1f}tr  VƯỢT={excess/1e6:,.1f}tr")
    print(f"    trần rổ engine {day_cap_engine/1e9:,.1f} tỷ ⇒ KHÔNG ràng buộc "
          f"({'binding' if trim < excess else 'không binding'}), trim={trim/1e6:,.1f}tr")
    if trim <= 0:
        continue
    for t, v in sorted(mv.items(), key=lambda kv: -kv[1]):
        w_live = v / park_mv
        sell = w_live * trim                        # pro-rata theo trọng số HIỆN TẠI (B4)
        a = adv_live.get(t, np.nan)
        pct = sell / a if a and a > 0 else np.nan
        cap_1acct = LAG_ADV_PCT * a * SHARE if a and a > 0 else np.nan
        rows.append({"account": acct, "ticker": t, "w_live": w_live, "mv_tr": v / 1e6,
                     "sell_tr": sell / 1e6, "adv_ty": a / 1e9 if a else np.nan,
                     "pct_adv": pct, "cap_live_tr": cap_1acct / 1e6 if cap_1acct else np.nan,
                     "vuot_cap_live": (sell > cap_1acct) if cap_1acct == cap_1acct else None,
                     "data_date": data_date.get(t)})

df = pd.DataFrame(rows)
if len(df):
    df["pct_adv_%"] = (df.pct_adv * 100).round(3)
    out = df[["account", "ticker", "w_live", "mv_tr", "sell_tr", "adv_ty", "pct_adv_%",
              "cap_live_tr", "vuot_cap_live", "data_date"]]
    print("\n" + out.to_string(index=False,
                               float_format=lambda x: f"{x:,.3f}"))
    print(f"\n[KẾT LUẬN] max %ADV per-name = {df.pct_adv.max()*100:.3f}% "
          f"({df.loc[df.pct_adv.idxmax(),'ticker']}, {df.loc[df.pct_adv.idxmax(),'account']})")
    print(f"[KẾT LUẬN] số mã vượt trần live (20%ADV×share={SHARE}) = "
          f"{int(df.vuot_cap_live.sum())}/{len(df)}")
    df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "capacity_check_out.csv"), index=False)

# ── 5. Kịch bản áp lực: trim toàn bộ PARK trong 1 phiên (cận trên lý thuyết) ──
print("\n=== KỊCH BẢN ÁP LỰC: trim 100% PARK trong 1 phiên (cận trên) ===")
for acct in ("SpaceX", "ZaloPay"):
    pos = pos_by_acct.get(acct, {})
    park = {t: v for t, v in pos.items()
            if t in NAMES and t not in CAPIT and t not in EXCLUDED[acct]}
    mv = {t: q * (mpx if mpx > 0 else px_last.get(t, 0.0)) for t, (q, mpx) in park.items()}
    worst = max(((t, v / adv_live[t]) for t, v in mv.items()
                 if adv_live.get(t, 0) > 0), key=lambda kv: kv[1], default=(None, 0))
    print(f"  {acct}: bán sạch → mã nặng nhất {worst[0]} = {worst[1]*100:.3f}% ADV riêng")

# ── 6. NGƯỠNG RÀNG BUỘC — trim tổng bao nhiêu thì mã nặng nhất chạm trần live? ─
# Đây mới là câu trả lời đúng cho killer_objection: không phải "hôm nay có vượt không"
# mà "trần TỔNG của engine có đủ chặt để bảo vệ trần PER-NAME của live không".
print("\n=== NGƯỠNG RÀNG BUỘC per-name (trần live = 20%ADV × share) ===")
for acct in ("SpaceX", "ZaloPay"):
    pos = pos_by_acct.get(acct, {})
    park = {t: v for t, v in pos.items()
            if t in NAMES and t not in CAPIT and t not in EXCLUDED[acct]}
    mv = {t: q * (mpx if mpx > 0 else px_last.get(t, 0.0)) for t, (q, mpx) in park.items()}
    mv = {t: v for t, v in mv.items() if v > 0}
    tot = sum(mv.values())
    # T_bind = min over names of (cap_i / w_i): trim tổng lớn nhất còn an toàn cho MỌI mã
    cands = [(t, (LAG_ADV_PCT * adv_live[t] * SHARE) / (v / tot))
             for t, v in mv.items() if adv_live.get(t, 0) > 0]
    t_bind, v_bind = min(cands, key=lambda kv: kv[1])
    print(f"  {acct}: trim tổng an toàn tối đa = {v_bind/1e9:,.1f} tỷ/phiên "
          f"(mã ràng buộc: {t_bind}); trần rổ engine = {day_cap_engine/1e9:,.1f} tỷ "
          f"⇒ engine LỎNG HƠN {day_cap_engine/v_bind:,.1f}×")
    print(f"           nhu cầu trim hôm nay = "
          f"{(tot - (tot + cash_by_acct.get(acct,0.0))*0.70)/1e9:,.3f} tỷ "
          f"⇒ dư địa {v_bind/max(tot - (tot + cash_by_acct.get(acct,0.0))*0.70, 1):,.0f}×")
