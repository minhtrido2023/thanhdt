#!/usr/bin/env python3
"""L1 — Park-target compliance: đề xuất lệnh BÁN đưa sổ PARK về đúng trần đã backtest.

⚠️ CHỈ ĐỌC — script này KHÔNG đặt lệnh, KHÔNG ghi vào bất kỳ file plan nào. Đầu ra là một
   DANH SÁCH ĐỀ XUẤT; nó vẫn phải đi qua đúng cơ chế duyệt hiện có (user duyệt plan → Mafee
   plan-bound) như mọi lệnh khác.

VÌ SAO (§A5 `park_unpark_live_wiring_20260803.md`): engine mô phỏng có BA đường vào/ra sổ
PARK, live chỉ có MỘT — và nó là đường MUA. Không có đường bán nào ⇒ tỷ trọng PARK live trôi
lên trên trần mà backtest đã mô phỏng (đo 2026-08-03: SpaceX vượt ~182tr). L1 chỉ đưa tỷ lệ
về đúng thiết kế; nó KHÔNG phụ thuộc bất kỳ tín hiệu mua nào (chạy hằng ngày, vô điều kiện —
đúng như engine sweep theo state).

CÔNG THỨC (§B2 + §D2 — mọi hằng số đều PORT từ engine/gate đã chạy, không có tham số mới):

    pool        = availableCash (DNSE) + park_mv (sổ book, §park_holdings)
    target_park = pool × PARK_TARGET
    delta       = target_park − park_mv
    if delta < −pool × 0.005:                          # ngưỡng 0,005 = engine dòng 918
        trim_total = min(−delta, _etf_day_cap_live)    # tầng 1: trần TỔNG (engine dòng 921)
        sell_i     = w_live_i × trim_total             # PRO RATA theo trọng số hiện tại (§B4)
        cap_i      = LAG_ADV_PCT × adv_vnd(i) × share  # tầng 2: trần RIÊNG = gate LAG live
        sell_i     = min(sell_i, cap_i)                # phần bị cắt CARRY-OVER sang phiên sau,
                                                       # KHÔNG phân bổ lại sang mã khác (§D2)

Trong từng mã: FIFO theo lô (`entry_date`) — đúng như engine. KHÔNG bán sạch vài mã: bán sạch
= đổi cấu trúc rổ = đổi hẳn thứ đã backtest (§B4).

RANH GIỚI CỨNG (§B5):
  · `excluded_tickers` (vd DGC ở ZaloPay) — KHÔNG BAO GIỜ trim.
  · Vị thế CAPIT (stop_exempt/slot_exempt) — KHÔNG phải PARK, KHÔNG trim (exit CAPIT do
    người quyết định). LAG/BAL/DISCRETIONARY_SPECIAL/LEGACY_ORPHAN cũng không đụng tới.
  · Ticker `UNVERIFIED` (sổ chưa đối soát được) — KHÔNG sinh lệnh (§21).
  · Đối soát sổ-vs-broker LỆCH ⇒ KHÔNG đề xuất gì cả (fail-closed, §5).
  · Giá/tiền đọc từ DNSE, không từ BQ (§6). `availableCash` chứ không `totalCash` — totalCash
    gồm cổ tức chưa về (đo 08-03: SpaceX 14,60tr totalCash gồm 9,78tr chưa về).

FAIL-CLOSED per-name (sao chép nguyên `cap_lag_orders._block`): không đo được ADV / ADV cũ
hơn LAG_ADV_MAX_STALE_DAYS / ADV ≤ 0 / không dựng được danh sách account live ⇒ KHÔNG trim mã
đó phiên này.

    python3 mike/bin/compute_park_trim.py --account SpaceX [--asof ...] [--target 0.80] [--json]
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

from park_holdings import park_holdings, today_ict          # noqa: E402
from trading_bot.plan import (LAG_ADV_PCT, LAG_ADV_MAX_STALE_DAYS,  # noqa: E402
                              _adv_for_gate)
from trading_bot.vn_market import LOT, round_lot            # noqa: E402

# ── Tham số — KHÔNG có cái nào tự chế ────────────────────────────────────────
# Target park F1, user CHỐT 2026-08-04 (báo cáo `park_wiring_two_options_20260804.md`:
# F1 = đỉnh Calmar 1,63 của cả dải quét; PBO họ 7 cấu hình = 0,08 trên metric CAGR).
# ⚠️ Đây là DUY NHẤT một tham số đổi so với spec đã pin (0,70 → 0,80).
# Cổng chính sách ĐÃ MỞ 2026-08-04: `data/trading_rules.json` v2.3 đặt
# `neutral_parking.default_park_of_idle_pct = 0.80` (user chốt, job Taylor_20260804_034133).
# CÒN LẠI: engine `golive_recommend_v23.py:96 ETF_PARK={3:0.7}` — đường MUA — vẫn publish 0,70,
# nên `etf_park_frac` live còn lệch target này (xem `neutral_parking.pending_engine_consistency`).
# Cảnh báo dưới đây nói về CHỖ LỆCH ĐÓ, không phải cổng chính sách.
PARK_TARGET_F1 = 0.80
TRIM_BAND = 0.005          # = simulate_holistic_nav.py dòng 918 (PREFILL_STATE_REBAL)
ETF_LIQ_PCT = 0.20         # = pt_v23_audit_2014.py:206 ETF_LIQ_PCT (trần thanh khoản rổ)
STATE_FILE = os.path.join(WC_ROOT, "data", "golive_v23_status.json")
BASKET_CSV = os.path.join(WC_ROOT, "data", "custom30v_8l_publish.csv")


def live_share():
    """Phần %ADV account này được phép chiếm = 1/N account LIVE. Sao chép ĐÚNG cách tính của
    `cap_lag_orders` (không dùng live_dnse_labels() — nó lọc broker=='dnse' và sẽ đếm thiếu)."""
    from trading_bot.config import load_config, load_accounts
    labels = [p["label"] for p in load_accounts(load_config())
              if p["enabled"] and p["cfg"]["mode"] == "live"]
    if not labels:
        return None, None, "không dựng được danh sách account live"
    return 1.0 / len(labels), labels, None


def etf_day_cap_live(asof):
    """Trần TỔNG mỗi phiên = ETF_LIQ_PCT × ADV_rổ, với ADV_rổ = trung bình 60 phiên của
    Σ(Price×Volume) trên rổ custom30V — ĐÚNG định nghĩa `_etf_day_cap` của engine.

    ⚠️ §D3: đây là ADV **rổ**, KHÁC hẳn ADV **mã** (Volume_3M_P50 × Price) dùng cho trần
    per-name bên dưới. Hai số không cùng đơn vị khái niệm (đo 08-03 lệch 24%) — KHÔNG BAO GIỜ
    chia số này cho số kia.
    """
    import pandas as pd
    bk = pd.read_csv(BASKET_CSV)
    bk = bk[bk.rebal_date == bk.rebal_date.max()]
    names = list(bk.ticker)
    pq = os.path.join(WC_ROOT, "data", "bq_cache", "ticker", f"{int(asof[:4])}.parquet")
    if not os.path.exists(pq):
        return None, names, f"không có cache giá {pq}"
    tk = pd.read_parquet(pq)
    tk["time"] = pd.to_datetime(tk["time"])
    tk = tk[(tk.ticker.isin(names)) & (tk.time <= pd.Timestamp(asof))].copy()
    if tk.empty:
        return None, names, "cache giá rỗng trong cửa sổ"
    tk["px"] = tk["Price"].fillna(tk["Close"])
    tk["tv"] = tk["px"] * tk["Volume"]
    adv_basket = float(tk.groupby("time")["tv"].sum().sort_index().tail(60).mean())
    return ETF_LIQ_PCT * adv_basket, names, None


def compute_trim(account_label, asof=None, target=PARK_TARGET_F1, holdings=None,
                 share_override=None, adv_fn=None, day_cap_override=None):
    """Trả dict mô tả đầy đủ quyết định. `*_override`/`adv_fn` chỉ để selfcheck bơm dữ liệu."""
    asof = asof or today_ict()
    h = holdings if holdings is not None else park_holdings(account_label, asof)
    adv_fn = adv_fn or _adv_for_gate

    out = {"account_label": account_label, "asof": asof, "target_park": target,
           "trim_band": TRIM_BAND, "orders": [], "blocked": [], "notes": [],
           "park_mv_vnd": h["park_mv_vnd"], "cash_available_vnd": h["cash_available_vnd"],
           "reconcile_ok": h["reconcile"]["ok"],
           "unverified_tickers": h["unverified_tickers"],
           "excluded_tickers": h["excluded_tickers"]}

    # ── Cổng 0: sổ chưa đối soát được ⇒ KHÔNG đề xuất gì (fail-closed, §5) ────
    if not h["reconcile"]["ok"]:
        out["decision"] = "BLOCKED_RECONCILE"
        out["notes"].append("sổ lô LỆCH so với broker ⇒ không sinh đề xuất nào. "
                            f"Lệch: {h['reconcile']['mismatches']}")
        return out

    state = {}
    if os.path.exists(STATE_FILE):
        state = json.load(open(STATE_FILE, encoding="utf-8"))
    out["state"] = {"state": state.get("state"), "state_name": state.get("state_name"),
                    "date": state.get("date"), "etf_park_frac_live": state.get("etf_park_frac")}
    live_frac = state.get("etf_park_frac")
    if live_frac is not None and abs(float(live_frac) - target) > 1e-9:
        out["notes"].append(
            f"⚠️ ENGINE CHƯA ĐỒNG BỘ: target dùng ở đây = {target:.2f} (F1, mặc định mới trong "
            f"trading_rules.json v2.3) nhưng `etf_park_frac` LIVE trong golive_v23_status.json = "
            f"{live_frac} (đường MUA, hằng số ETF_PARK của golive_recommend_v23.py chưa đổi) ⇒ hệ "
            f"đang ở trạng thái lai: mua tới {float(live_frac):.0%} nhưng chỉ trim khi vượt "
            f"{target:.0%}. Cổng chính sách ĐÃ mở; chỗ lệch này cần user/Mike duyệt đổi 1 dòng "
            f"engine (neutral_parking.pending_engine_consistency). Chép dòng này vào notes plan.")
    # ⚠️ L1 chỉ được thiết kế/đo ở state NEUTRAL (PARK_STATES = {3: ...}). State khác ⇒ báo,
    # không tự suy ra target cho state chưa đo.
    if state.get("state") is not None and int(state["state"]) != 3:
        out["decision"] = "SKIP_STATE"
        out["notes"].append(f"state={state.get('state')} ({state.get('state_name')}) ≠ NEUTRAL — "
                            f"L1 chỉ được đo ở NEUTRAL, không tự suy target cho state khác")
        return out

    park_mv = float(h["park_mv_vnd"])
    cash = float(h["cash_available_vnd"] or 0)
    pool = cash + park_mv
    target_value = pool * target
    delta = target_value - park_mv
    out.update({"pool_vnd": pool, "target_park_vnd": target_value, "delta_vnd": delta,
                "threshold_vnd": pool * TRIM_BAND})
    if delta >= -pool * TRIM_BAND:
        out["decision"] = "NO_TRIM"
        out["notes"].append(f"PARK {park_mv/1e6:,.1f}tr vs target {target_value/1e6:,.1f}tr "
                            f"(pool {pool/1e6:,.1f}tr) — vượt {max(0, -delta)/1e6:,.1f}tr, "
                            f"chưa quá ngưỡng {pool*TRIM_BAND/1e6:,.1f}tr")
        return out

    # ── Tầng 1: trần TỔNG mỗi phiên (engine `_etf_day_cap`) ──────────────────
    if day_cap_override is not None:
        day_cap, basket, cap_err = day_cap_override, [], None
    else:
        day_cap, basket, cap_err = etf_day_cap_live(asof)
    if cap_err or day_cap is None or day_cap <= 0:
        out["decision"] = "BLOCKED_DAYCAP"
        out["notes"].append(f"không đo được trần thanh khoản rổ ({cap_err}) ⇒ fail-closed, "
                            f"không trim")
        return out
    trim_total = min(-delta, day_cap)
    out.update({"etf_day_cap_vnd": day_cap, "trim_total_vnd": trim_total,
                "day_cap_binding": trim_total < -delta - 1})

    share, live_labels, share_err = (share_override, None, None) if share_override is not None \
        else live_share()
    if share_err or not share:
        out["decision"] = "BLOCKED_SHARE"
        out["notes"].append(f"{share_err} ⇒ fail-closed, không trim")
        return out
    out["adv_share"] = share
    out["live_labels"] = live_labels

    # ── Rổ PARK sống: gộp lô theo mã, loại các mã bị cấm trim ────────────────
    excluded = set(h["excluded_tickers"])
    unver = set(h["unverified_tickers"])
    per_tk = {}
    for l in h["park_lots"]:
        d = per_tk.setdefault(l["ticker"], {"qty": 0, "mv": 0.0, "px": l["market_price"],
                                            "lots": []})
        d["qty"] += l["qty"]
        d["mv"] += l["mv_vnd"]
        d["lots"].append(l)
    for tk in sorted(per_tk):
        if tk in excluded:
            out["blocked"].append({"ticker": tk, "reason": "excluded_tickers — CẤM trim"})
        elif tk in unver:
            out["blocked"].append({"ticker": tk, "reason": "sổ UNVERIFIED — cấm sinh lệnh (§21)"})
    tradable = {t: d for t, d in per_tk.items() if t not in excluded and t not in unver}
    mv_base = sum(d["mv"] for d in tradable.values())
    if mv_base <= 0:
        out["decision"] = "BLOCKED_NO_TRADABLE"
        out["notes"].append("không mã PARK nào đủ điều kiện sinh lệnh")
        return out

    # ── Pro-rata + tầng 2 (trần per-name = gate LAG live) ────────────────────
    bpos = h.get("broker_positions", {})
    for tk in sorted(tradable):
        d = tradable[tk]
        w = d["mv"] / mv_base
        want_vnd = w * trim_total
        px = d["px"]
        if px <= 0:
            out["blocked"].append({"ticker": tk, "reason": "không có marketPrice broker"})
            continue
        adv, data_date, err = adv_fn(tk, asof)
        if err:
            out["blocked"].append({"ticker": tk, "reason": f"không đo được ADV: {err}"})
            continue
        if data_date:
            try:
                lag_days = (dt.date.fromisoformat(asof) - dt.date.fromisoformat(data_date)).days
            except Exception:
                lag_days = None
            if lag_days is not None and lag_days > LAG_ADV_MAX_STALE_DAYS:
                out["blocked"].append({"ticker": tk, "reason":
                                       f"ADV data {data_date} cũ {lag_days} ngày (> "
                                       f"{LAG_ADV_MAX_STALE_DAYS})"})
                continue
        if adv <= 0:
            out["blocked"].append({"ticker": tk, "reason": f"ADV ≤ 0 (data {data_date})"})
            continue
        cap_i = LAG_ADV_PCT * adv * share
        sell_vnd = min(want_vnd, cap_i)                 # phần dư CARRY-OVER, không phân bổ lại
        qty = round_lot(sell_vnd / px)
        # Không bán quá số đang giữ, và không bán CP chưa về (T+2) — ràng buộc hiện vật.
        sellable = int(bpos.get(tk, {}).get("sellable", d["qty"]))
        qty = min(qty, d["qty"], sellable)
        qty = round_lot(qty)
        if qty < LOT:
            out["blocked"].append({"ticker": tk, "reason":
                                   f"trần/khả năng bán < 1 lô (muốn {want_vnd:,.0f}đ, "
                                   f"trần ADV {cap_i:,.0f}đ, sellable {sellable:,}cp)"})
            continue
        # FIFO trong mã: liệt kê lô bị tiêu thụ (đúng thứ tự entry_date) để audit được.
        remain, fifo = qty, []
        for lot in sorted(d["lots"], key=lambda x: (x["entry_date"], x["source"])):
            if remain <= 0:
                break
            take = min(lot["qty"], remain)
            fifo.append({"entry_date": lot["entry_date"], "qty": take,
                         "cost_price": lot["price"], "source": lot["source"]})
            remain -= take
        out["orders"].append({
            "ticker": tk, "side": "sell", "qty": int(qty), "ref_price": px,
            "value_vnd": qty * px, "book": "PARK", "play_type": "PARK_TRIM",
            "weight_in_park": w, "want_vnd": want_vnd, "adv_cap_vnd": cap_i,
            "adv_capped": cap_i < want_vnd, "adv_vnd": adv, "adv_data_date": data_date,
            "sellable": sellable, "fifo_lots": fifo,
            "reason": (f"L1 park-target: PARK {park_mv/1e6:,.1f}tr > target "
                       f"{target_value/1e6:,.1f}tr ({target:.0%} × pool {pool/1e6:,.1f}tr); "
                       f"trim tổng {trim_total/1e6:,.1f}tr pro-rata w={w:.1%}"
                       + (f"; BỊ CẮT bởi trần {LAG_ADV_PCT:.0%}ADV×{share:.2f}"
                          f"={cap_i/1e6:,.1f}tr, phần dư sang phiên sau" if cap_i < want_vnd else "")),
        })
    out["decision"] = "TRIM" if out["orders"] else "BLOCKED_ALL_NAMES"
    out["trim_proposed_vnd"] = sum(o["value_vnd"] for o in out["orders"])
    out["trim_shortfall_vnd"] = trim_total - out["trim_proposed_vnd"]
    return out


def main():
    ap = argparse.ArgumentParser(description="L1 park-target compliance — CHỈ ĐỌC, đề xuất lệnh bán")
    ap.add_argument("--account", required=True)
    ap.add_argument("--asof", default=None)
    ap.add_argument("--target", type=float, default=PARK_TARGET_F1)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=None,
                    help="ghi kết quả JSON ra file (khuyến nghị cho consumer máy đọc — stdout "
                         "còn có dòng log kết nối của broker nên không parse thẳng được)")
    a = ap.parse_args()
    r = compute_trim(a.account, a.asof, a.target)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1, default=str)
        print(f"[park_trim] JSON → {a.out}")
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
        return 0
    print(f"=== L1 PARK-TRIM (ĐỀ XUẤT, chưa vào plan nào) — {r['account_label']} "
          f"asof={r['asof']} — {r['decision']} ===")
    if "pool_vnd" in r:
        print(f"  pool = cash {r['cash_available_vnd']/1e6:,.2f}tr + PARK "
              f"{r['park_mv_vnd']/1e6:,.2f}tr = {r['pool_vnd']/1e6:,.2f}tr")
        print(f"  target {r['target_park']:.0%} = {r['target_park_vnd']/1e6:,.2f}tr  →  "
              f"vượt {max(0, -r['delta_vnd'])/1e6:,.2f}tr "
              f"(ngưỡng {r['threshold_vnd']/1e6:,.2f}tr)")
    if "etf_day_cap_vnd" in r:
        print(f"  trần TỔNG/phiên (ADV rổ × {ETF_LIQ_PCT:.0%}) = {r['etf_day_cap_vnd']/1e9:,.2f} tỷ"
              f"  → trim mục tiêu {r['trim_total_vnd']/1e6:,.2f}tr"
              f"{'  [trần TỔNG binding]' if r.get('day_cap_binding') else ''}")
    for o in r["orders"]:
        print(f"   BÁN {o['ticker']:<5} {o['qty']:>7,}cp @ {o['ref_price']:>9,.0f} = "
              f"{o['value_vnd']/1e6:>8,.2f}tr  w={o['weight_in_park']:.1%}"
              f"{'  [trần ADV cắt]' if o['adv_capped'] else ''}")
    if r["orders"]:
        print(f"  Σ đề xuất = {r['trim_proposed_vnd']/1e6:,.2f}tr "
              f"(còn thiếu {r['trim_shortfall_vnd']/1e6:,.2f}tr → phiên sau)")
    for b in r["blocked"]:
        print(f"   – bỏ qua {b['ticker']}: {b['reason']}")
    for n in r["notes"]:
        print(f"   ⚠ {n}")
    print("  (script CHỈ ĐỌC — không đặt lệnh, không ghi plan; đề xuất vẫn phải qua duyệt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
