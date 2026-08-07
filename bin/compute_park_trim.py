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

CÔNG THỨC (§D1 `park_membership_sync_L0_design_20260806.md` — user John duyệt 2026-08-07,
job Taylor_20260807_020402. Mọi hằng số vẫn PORT từ engine/gate đã chạy, KHÔNG tham số mới):

    pool        = availableCash (DNSE) + park_mv (sổ book, §park_holdings)
    target_park = pool × PARK_TARGET
    delta       = target_park − park_mv
    if delta < −pool × 0.005:                          # ngưỡng 0,005 = engine dòng 918 (GIỮ NGUYÊN)
        w_i        = trọng số rổ custom30V đang hiệu lực tại asof (PIT: rebal_date ≤ asof)
        khả thi    = {i ∈ rổ : i ∉ BANNED ∧ i ∉ excluded_tickers ∧ có giá ∧ w_i×target_park ≥ 1 lô}
        w'_i       = w_i / Σ_{khả thi} w_j             # CHUẨN HOÁ LẠI, in rõ mã bị loại
        tgt_i      = target_park × w'_i                # mã NGOÀI rổ khả thi ⇒ tgt_i = 0
        want_i     = max(0, mv_i − tgt_i)              # ← chỉ chiều BÁN (P1); chiều MUA là P2
        scale      = min(1, _etf_day_cap_live / Σ want) # tầng 1: trần TỔNG (engine dòng 921)
        cap_i      = LAG_ADV_PCT × adv_vnd(i) × share  # tầng 2: trần RIÊNG = gate LAG live
        sell_i     = min(want_i × scale, cap_i)        # phần bị cắt CARRY-OVER sang phiên sau,
                                                       # KHÔNG phân bổ lại sang mã khác (§D2)

VÌ SAO ĐỔI (công thức cũ `sell_i = w_live_i × trim_total` = pro-rata theo trọng số ĐANG CÓ):
nó giữ nguyên CẤU TRÚC sai và KHÔNG BAO GIỜ tiêu diệt được một vị thế nhỏ đã rớt rổ — SHS
(0,5% PARK SpaceX) chỉ được phân 609k đ/phiên, luôn < 1 lô ⇒ mắc kẹt vĩnh viễn. Engine mô phỏng
giữ PARK như MỘT chứng khoán tổng hợp (`vn30_underlying = _lvl_d`), nên bán "đơn vị rổ" = bán
pro-rata theo trọng số **MỤC TIÊU**, và việc đổi thành viên xảy ra TỨC THÌ ngay phiên rebal
(`custom_basket.py active_q`). `tgt_i − mv_i` là port ĐÚNG của cùng cơ chế đó; mã rớt rổ có
tgt_i = 0 ⇒ tự động bán sạch, KHÔNG cần luật riêng.

Trong từng mã: FIFO theo lô (`entry_date`) — đúng như engine.

⚠️ HỆ QUẢ PHẢI ĐỌC — P1 là SELL-ONLY: Σ bán ở đây LỚN HƠN mức vượt trần (−delta), vì nó gồm cả
phần của các mã ta CHƯA MUA (tgt của chúng không thuộc về mã ta đang giữ). Sau khi bán, PARK sẽ
nằm DƯỚI target cho tới khi đường MUA (P2 / hàng `PARK_ADVISORY` của golive) bù lại. Con số cụ
thể được ghi ra `underpark_after_vnd` + `notes` mỗi lần chạy — CHÉP vào notes plan để user thấy.

RANH GIỚI CỨNG (§B5 + §D4):
  · `excluded_tickers` (vd DGC ở ZaloPay) — KHÔNG BAO GIỜ trim, VÀ tgt = 0 (không mua) ⇒ trọng
    số của nó chuẩn hoá sang các mã còn lại. (Quyết định 4b, Mike chốt 2026-08-07.)
  · Mã `BANNED` vĩnh viễn (`lag_forensic_filter.BANNED` — PC1/HVN/HSG… ĐÃ từng là thành viên
    custom30V các kỳ trước) — LỌC KHỎI rổ mục tiêu, tgt = 0. Đây là **lệch có chủ đích so với
    backtest** (backtest không có khái niệm BANNED-vĩnh-viễn): Mike chốt 2026-08-07 theo hướng
    an toàn hơn, nhất quán với chính sách BANNED toàn hệ. User đảo lại được nếu muốn.
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
# Danh sách BANNED vĩnh viễn — DÙNG LẠI hằng số chuẩn tắc, KHÔNG chép tay lần thứ ba
# (bản 1: lag_forensic_filter.py:90, bản 2: mike/bin/build_universe_pit_quality.py:71).
from lag_forensic_filter import BANNED                      # noqa: E402

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


def park_target_basket(asof, path=BASKET_CSV):
    """Rổ MỤC TIÊU custom30V đang hiệu lực tại `asof` — {ticker: weight}, + rebal_date.

    Nguồn = `data/custom30v_8l_publish.csv`. Đây ĐÚNG là thứ production đọc: `custom30_history.py`
    ghi CSV này rồi `bq load --replace` CHÍNH FILE ĐÓ lên `tav2_bq.custom30v_8l` (bảng mà
    `golive_recommend_v23.py` query) ⇒ CSV là nguồn, bảng BQ là bản sao. Đối chiếu 2026-08-07:
    `data/bq_cache/custom30v_8l.parquet` khớp CSV TUYỆT ĐỐI ở kỳ 2026-08-05 (30/30 mã, max|Δw|=0).

    PIT: chỉ lấy `rebal_date ≤ asof` (engine `custom_basket.active_q` = bisect_right(reb, d)-1,
    tức kỳ đang hiệu lực, không bao giờ là kỳ tương lai). Trước đây `etf_day_cap_live` dùng
    `.max()` trần — trùng kết quả hôm nay nhưng sẽ nhìn trước nếu CSV publish kỳ tương lai.
    """
    import pandas as pd
    if not os.path.exists(path):
        return None, None, f"không có {path}"
    bk = pd.read_csv(path)
    bk = bk[bk.rebal_date.astype(str) <= str(asof)]
    if bk.empty:
        return None, None, f"không có kỳ rebal nào ≤ {asof} trong {os.path.basename(path)}"
    rd = str(bk.rebal_date.astype(str).max())
    cur = bk[bk.rebal_date.astype(str) == rd]
    # KHÔNG kiểm Σ trọng số ở đây — phép kiểm đó nằm trong `compute_trim` để áp cho MỌI nguồn
    # rổ (kể cả `basket_override` của selfcheck), một chỗ duy nhất.
    return {str(r.ticker): float(r.weight) for r in cur.itertuples()}, rd, None


def etf_day_cap_live(asof, names=None):
    """Trần TỔNG mỗi phiên = ETF_LIQ_PCT × ADV_rổ, với ADV_rổ = trung bình 60 phiên của
    Σ(Price×Volume) trên rổ custom30V — ĐÚNG định nghĩa `_etf_day_cap` của engine.

    `names=None` ⇒ tự đọc rổ đang hiệu lực (chữ ký + shape trả về GIỮ NGUYÊN cho consumer sẵn
    có: `compute_jit_unpark.py:351` gọi `etf_day_cap_live(asof)` và nhận 3-tuple).

    ⚠️ §D3: đây là ADV **rổ**, KHÁC hẳn ADV **mã** (Volume_3M_P50 × Price) dùng cho trần
    per-name bên dưới. Hai số không cùng đơn vị khái niệm (đo 08-03 lệch 24%) — KHÔNG BAO GIỜ
    chia số này cho số kia.
    """
    import pandas as pd
    if names is None:
        bk, _rd, err = park_target_basket(asof)
        if err or not bk:
            return None, [], err or "không đọc được rổ"
        names = sorted(bk)
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


def live_price_fn(asof):
    """Trả hàm `f(ticker) -> (price|None, err|None)` cho mã KHÔNG nằm trong vị thế broker.

    CẦN giá của mã ta CHƯA MUA vì phép "trọng số mục tiêu ≥ 1 lô" (§D3) quyết định mã nào bị
    loại khỏi rổ khả thi, và việc loại đó làm ĐỔI trọng số chuẩn hoá của các mã ta ĐANG giữ.

    §6 (bright-line user 2026-07-09): số liệu same-day lấy từ DNSE, KHÔNG BAO GIỜ từ BQ ⇒ dùng
    quote LIVE (`DNSEBroker(quote_only=True)`, không cần tiểu khoản/OTP). `asof` quá khứ ⇒ trả
    lỗi cho mọi mã (không có nguồn giá quá khứ cho mã KHÔNG giữ mà không đụng BQ) — mã đó rơi
    vào nhánh fail-closed "coi như không khả thi", tức bán ÍT đi, không bán nhiều hơn.
    """
    if asof != today_ict():
        return lambda tk: (None, f"asof {asof} ≠ hôm nay — không có quote live")
    state = {"b": None}

    def _f(tk):
        if state["b"] is None:
            from trading_bot.brokers import DNSEBroker
            b = DNSEBroker(account_id=None, credentials_file=None, label="park_trim_quote",
                           quote_only=True)
            b.connect()
            state["b"] = b
        try:
            q = state["b"].get_quote(tk)
        except Exception as e:                       # noqa: BLE001 — mọi lỗi ⇒ fail-closed per-name
            return None, f"quote lỗi: {e}"
        if q is None or not q.ok():
            return None, "quote rỗng/không map được field"
        px = q.last or q.ref
        return (float(px), None) if px and px > 0 else (None, "quote không có last/ref")

    return _f


def compute_trim(account_label, asof=None, target=PARK_TARGET_F1, holdings=None,
                 share_override=None, adv_fn=None, day_cap_override=None,
                 basket_override=None, price_fn=None):
    """Trả dict mô tả đầy đủ quyết định. `*_override`/`*_fn` chỉ để selfcheck bơm dữ liệu."""
    asof = asof or today_ict()
    h = holdings if holdings is not None else park_holdings(account_label, asof)
    adv_fn = adv_fn or _adv_for_gate

    out = {"account_label": account_label, "asof": asof, "target_park": target,
           "trim_band": TRIM_BAND, "orders": [], "blocked": [], "notes": [],
           "at_or_below_target": [],
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

    # ── Rổ MỤC TIÊU custom30V (PIT theo asof) — nguồn của tgt_i ──────────────
    if basket_override is not None:
        basket_w, rebal_date, b_err = basket_override, "override", None
    else:
        basket_w, rebal_date, b_err = park_target_basket(asof)
    if not b_err and basket_w and not (0.99 <= sum(basket_w.values()) <= 1.01):
        b_err = f"Σ trọng số kỳ {rebal_date} = {sum(basket_w.values()):.4f} ≠ 1 (rổ hỏng)"
    if b_err or not basket_w:
        out["decision"] = "BLOCKED_BASKET"
        out["notes"].append(f"không đọc được rổ mục tiêu custom30V ({b_err}) ⇒ fail-closed, "
                            f"không trim")
        return out
    out["basket_rebal_date"] = rebal_date
    out["basket_n"] = len(basket_w)

    # ── Tầng 1: trần TỔNG mỗi phiên (engine `_etf_day_cap`) ──────────────────
    if day_cap_override is not None:
        day_cap, cap_err = day_cap_override, None
    else:
        day_cap, _names, cap_err = etf_day_cap_live(asof, sorted(basket_w))
    if cap_err or day_cap is None or day_cap <= 0:
        out["decision"] = "BLOCKED_DAYCAP"
        out["notes"].append(f"không đo được trần thanh khoản rổ ({cap_err}) ⇒ fail-closed, "
                            f"không trim")
        return out
    out["etf_day_cap_vnd"] = day_cap

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
    if not tradable:
        out["decision"] = "BLOCKED_NO_TRADABLE"
        out["notes"].append("không mã PARK nào đủ điều kiện sinh lệnh")
        return out

    # ── Rổ KHẢ THI + trọng số MỤC TIÊU chuẩn hoá (§D1/§D3) ───────────────────
    # Thứ tự loại: BANNED → excluded_tickers → không có giá → target < 1 lô. Mọi mã bị loại đều
    # được LIỆT KÊ (yêu cầu "no silent caps"), kèm Σ trọng số đã bỏ.
    price_fn = price_fn or live_price_fn(asof)
    bpos = h.get("broker_positions", {})
    dropped, feasible = [], {}
    for tk in sorted(basket_w):
        w_raw = basket_w[tk]
        if tk in BANNED:
            dropped.append({"ticker": tk, "weight": w_raw,
                            "reason": "BANNED vĩnh viễn (Mike chốt 2026-08-07: lọc khỏi rổ mục "
                                      "tiêu — lệch backtest CÓ CHỦ ĐÍCH)"})
            continue
        if tk in excluded:
            dropped.append({"ticker": tk, "weight": w_raw,
                            "reason": "excluded_tickers — không mua, không bán (vị thế legacy)"})
            continue
        px_i = per_tk[tk]["px"] if tk in per_tk and per_tk[tk]["px"] > 0 else None
        px_err = None
        if px_i is None:
            px_i, px_err = price_fn(tk)
        if not px_i or px_i <= 0:
            dropped.append({"ticker": tk, "weight": w_raw,
                            "reason": f"không lấy được giá ({px_err}) ⇒ fail-closed, coi như "
                                      f"không khả thi"})
            continue
        if target_value * w_raw < LOT * px_i:
            dropped.append({"ticker": tk, "weight": w_raw,
                            "reason": f"target {target_value*w_raw:,.0f}đ < 1 lô "
                                      f"({LOT}cp × {px_i:,.0f}đ)"})
            continue
        feasible[tk] = w_raw
    w_sum = sum(feasible.values())
    if w_sum <= 0:
        out["decision"] = "BLOCKED_NO_FEASIBLE_BASKET"
        out["notes"].append("không mã nào trong rổ mục tiêu khả thi ⇒ không suy được tgt, "
                            "fail-closed")
        out["basket_dropped"] = dropped
        return out
    tgt = {tk: target_value * (w / w_sum) for tk, w in feasible.items()}
    out["basket_dropped"] = dropped
    out["basket_dropped_weight"] = sum(d["weight"] for d in dropped)
    out["basket_feasible_n"] = len(feasible)
    out["target_weights"] = {tk: feasible[tk] / w_sum for tk in sorted(feasible)}
    out["target_value_vnd"] = {tk: tgt[tk] for tk in sorted(tgt)}
    if dropped:
        out["notes"].append(
            f"rổ mục tiêu kỳ {rebal_date}: {len(feasible)}/{len(basket_w)} mã khả thi, bỏ "
            f"{len(dropped)} mã (Σ {out['basket_dropped_weight']*100:.2f}% trọng số) — trọng số "
            f"đã CHUẨN HOÁ LẠI trên tập khả thi: "
            + "; ".join(f"{d['ticker']} {d['weight']*100:.2f}% ({d['reason']})" for d in dropped))

    # ── want_i = mv_i − tgt_i, trần TỔNG, rồi tầng 2 (trần per-name = gate LAG live) ──
    want_raw = {tk: max(0.0, d["mv"] - tgt.get(tk, 0.0)) for tk, d in tradable.items()}
    want_total = sum(want_raw.values())
    if want_total <= 0:
        out["decision"] = "NO_TRIM_STRUCTURE"
        out["notes"].append("mọi mã PARK đang giữ đều ở/dưới trọng số mục tiêu — không sinh lệnh "
                            "bán (phần vượt trần nằm ở các mã CHƯA MUA, cần đường MUA P2)")
        return out
    scale = min(1.0, day_cap / want_total)
    trim_total = want_total * scale
    out.update({"structural_excess_vnd": want_total, "trim_total_vnd": trim_total,
                "day_cap_binding": scale < 1.0, "day_cap_scale": scale})

    for tk in sorted(tradable):
        d = tradable[tk]
        want_vnd = want_raw[tk] * scale
        px = d["px"]
        if want_vnd <= 0:
            # KHÔNG phải "blocked" (đó là nhánh muốn làm mà không làm được) — đây là mã đang ở
            # hoặc DƯỚI trọng số mục tiêu, không có gì để bán. Phần thiếu là việc của đường MUA.
            out["at_or_below_target"].append(
                {"ticker": tk, "mv_vnd": d["mv"], "target_vnd": tgt.get(tk, 0.0),
                 "gap_vnd": tgt.get(tk, 0.0) - d["mv"]})
            continue
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
        w_t = out["target_weights"].get(tk, 0.0)
        out["orders"].append({
            "ticker": tk, "side": "sell", "qty": int(qty), "ref_price": px,
            "value_vnd": qty * px, "book": "PARK", "play_type": "PARK_TRIM",
            "weight_target": w_t, "weight_in_park": d["mv"] / park_mv if park_mv else 0.0,
            "mv_vnd": d["mv"], "target_vnd": tgt.get(tk, 0.0),
            "in_basket": tk in feasible, "want_vnd": want_vnd, "adv_cap_vnd": cap_i,
            "adv_capped": cap_i < want_vnd, "adv_vnd": adv, "adv_data_date": data_date,
            "sellable": sellable, "fifo_lots": fifo,
            "reason": (f"L1 park-sync (rổ {rebal_date}): đang {d['mv']/1e6:,.1f}tr vs target "
                       f"{tgt.get(tk, 0.0)/1e6:,.1f}tr "
                       + (f"(w' {w_t:.2%} × park-target {target_value/1e6:,.1f}tr)"
                          if tk in feasible else "(NGOÀI rổ khả thi ⇒ target 0, bán sạch)")
                       + (f"; bị co theo trần TỔNG/phiên ×{scale:.3f}" if scale < 1 else "")
                       + (f"; BỊ CẮT bởi trần {LAG_ADV_PCT:.0%}ADV×{share:.2f}"
                          f"={cap_i/1e6:,.1f}tr, phần dư sang phiên sau" if cap_i < want_vnd else "")),
        })
    out["decision"] = "TRIM" if out["orders"] else "BLOCKED_ALL_NAMES"
    out["trim_proposed_vnd"] = sum(o["value_vnd"] for o in out["orders"])
    out["trim_shortfall_vnd"] = trim_total - out["trim_proposed_vnd"]

    # ⚠️ P1 SELL-ONLY: bán theo cấu trúc kéo PARK xuống DƯỚI target vì phần trọng số của các mã
    # ta CHƯA MUA không thuộc về mã nào đang giữ. Ghi số ra để user thấy TRƯỚC khi duyệt —
    # đây là lệch MỚI do P1 tạo ra, chỉ đóng lại khi đường MUA (P2/PARK_ADVISORY) chạy.
    park_after = park_mv - out["trim_proposed_vnd"]
    out["park_mv_after_vnd"] = park_after
    out["park_pct_after"] = park_after / pool if pool else None
    out["underpark_after_vnd"] = max(0.0, target_value - park_after)
    if out["underpark_after_vnd"] > pool * TRIM_BAND:
        out["notes"].append(
            f"⚠️ SAU KHI BÁN, PARK = {park_after/1e6:,.1f}tr = {park_after/pool:.1%} pool, DƯỚI "
            f"target {target:.0%} ({target_value/1e6:,.1f}tr) {out['underpark_after_vnd']/1e6:,.1f}tr. "
            f"Đúng thiết kế P1 (sell-only): phần thiếu là trọng số của các mã trong rổ mà ta CHƯA "
            f"MUA — nó chỉ đóng lại khi đường MUA chạy (P2 chưa có code; hiện là hàng "
            f"PARK_ADVISORY do người quyết định). CHÉP dòng này vào notes plan.")
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
    if "basket_rebal_date" in r:
        print(f"  rổ mục tiêu custom30V kỳ {r['basket_rebal_date']}: "
              f"{r.get('basket_feasible_n', '?')}/{r.get('basket_n')} mã khả thi"
              + (f", bỏ {len(r.get('basket_dropped') or [])} mã "
                 f"(Σ {r.get('basket_dropped_weight', 0)*100:.2f}% trọng số)"
                 if r.get("basket_dropped") else ""))
    if "etf_day_cap_vnd" in r and "trim_total_vnd" in r:
        print(f"  trần TỔNG/phiên (ADV rổ × {ETF_LIQ_PCT:.0%}) = {r['etf_day_cap_vnd']/1e9:,.2f} tỷ"
              f"  → lệch cấu trúc {r['structural_excess_vnd']/1e6:,.2f}tr, bán mục tiêu "
              f"{r['trim_total_vnd']/1e6:,.2f}tr"
              f"{'  [trần TỔNG binding]' if r.get('day_cap_binding') else ''}")
    for o in r["orders"]:
        print(f"   BÁN {o['ticker']:<5} {o['qty']:>7,}cp @ {o['ref_price']:>9,.0f} = "
              f"{o['value_vnd']/1e6:>8,.2f}tr  mv {o['mv_vnd']/1e6:>7,.2f}tr → tgt "
              f"{o['target_vnd']/1e6:>7,.2f}tr (w' {o['weight_target']:.2%})"
              f"{'  [NGOÀI RỔ → bán sạch]' if not o['in_basket'] else ''}"
              f"{'  [trần ADV cắt]' if o['adv_capped'] else ''}")
    if r["orders"]:
        print(f"  Σ đề xuất = {r['trim_proposed_vnd']/1e6:,.2f}tr "
              f"(còn thiếu {r['trim_shortfall_vnd']/1e6:,.2f}tr → phiên sau)")
        print(f"  PARK sau khi bán = {r['park_mv_after_vnd']/1e6:,.2f}tr = "
              f"{r['park_pct_after']:.1%} pool"
              + (f"  ⚠ DƯỚI target {r['underpark_after_vnd']/1e6:,.2f}tr — chờ đường MUA"
                 if r.get("underpark_after_vnd", 0) > 0 else ""))
    for b in r["blocked"]:
        print(f"   – bỏ qua {b['ticker']}: {b['reason']}")
    for a in r.get("at_or_below_target") or []:
        print(f"   · {a['ticker']} đang {a['mv_vnd']/1e6:,.2f}tr ≤ target "
              f"{a['target_vnd']/1e6:,.2f}tr (thiếu {a['gap_vnd']/1e6:,.2f}tr — việc của đường MUA)")
    for n in r["notes"]:
        print(f"   ⚠ {n}")
    print("  (script CHỈ ĐỌC — không đặt lệnh, không ghi plan; đề xuất vẫn phải qua duyệt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
