#!/usr/bin/env python3
"""P2 park-ADD — đường MUA của sổ PARK. ĐỐI XỨNG ĐẠI SỐ của L1 `compute_park_trim.py`.

VÌ SAO TỒN TẠI: `compute_park_trim.py` (L1, LIVE 2026-08-04, quant-skeptic CONFIRMED cao) là
đường BÁN. Chính nó in ra dòng:

    "phần thiếu là trọng số của các mã trong rổ mà ta CHƯA MUA — nó chỉ đóng lại khi đường MUA
     chạy (P2 chưa có code; hiện là hàng PARK_ADVISORY do người quyết định)"

File này là "P2" đó, ở dạng CÔNG CỤ TÍNH cho DollarBill (KHÔNG phải script production trong
`mike/bin/`, KHÔNG cron, KHÔNG side-effect) — chỉ đọc, in đề xuất lệnh MUA để đưa vào plan chờ
user duyệt. Mọi hằng số/hàm dùng lại NGUYÊN VẸN từ L1 bằng import, không chép tay:
`park_holdings`, `park_target_basket`, `etf_day_cap_live`, `live_share`, `live_price_fn`,
`PARK_TARGET_F1`, `TRIM_BAND`, `LAG_ADV_PCT`, `LAG_ADV_MAX_STALE_DAYS`, `_adv_for_gate`,
`BANNED`, `LOT`, `round_lot`.

CÔNG THỨC (đối xứng từng dòng với L1, chỉ đảo dấu):
    pool        = (totalCash − totalDebt − reserve) + park_mv        # §pool của L1, §25 CLAUDE.md
    target_park = pool × PARK_TARGET_F1                              # 0,80 = mặc định v2.3
    delta       = target_park − park_mv
    if delta <= pool × TRIM_BAND:  NO_ADD                            # cùng băng 0,005 với L1
    tgt_i       = target_park × w_i / Σw_feasible                    # cùng phép chuẩn hoá L1
    want_i      = max(0, tgt_i − mv_i)                               # L1: max(0, mv_i − tgt_i)
    scale       = min(1, etf_day_cap / Σwant)                        # cùng trần TỔNG/phiên
    cap_i       = LAG_ADV_PCT × adv_i × share                        # cùng trần per-name
    qty_i       = round_lot(min(want_i×scale, cap_i, name_cap_room_i, cash_room_i) / px_i)

BA RÀNG BUỘC CHỈ CÓ Ở CHIỀU MUA (chiều bán không cần):
  1. `--max-spend-vnd` — TIỀN THẬT. L1 bán thì bị chặn bởi "không bán quá số đang giữ/sellable";
     chiều mua bị chặn bởi "không tiêu quá tiền đang có". Fail-closed: không truyền ⇒ lấy
     (totalCash − totalDebt − cash_dividend_receiving − reserve) làm trần TIỀN MẶT THUẦN, tức
     KHÔNG BAO GIỜ tự cấp margin cho mình (SpaceX có margin: pp0Buy 565tr > tiền mặt 305tr).
  2. `name_cap` 0,10 NAV/mã (`trading_rules.json sizing.name_cap_pct`) — tính trên vị thế TỔNG
     mọi book (PARK + CAPIT + LAG + …), không phải riêng phần PARK, vì trần này là trần TẬP TRUNG.
  3. Rổ mục tiêu = MỌI mã khả thi trong rổ, kể cả mã ĐANG CHƯA GIỮ. Đó chính là chỗ trọng số
     bị thiếu mà L1 không với tới được (L1 chỉ bán mã đang giữ).

KHÔNG làm: không đụng CAPIT/LAG/BAL/DISCRETIONARY/excluded_tickers; không đề xuất bán; không
tự đặt lệnh; không sửa plan. Đề xuất vẫn phải qua user duyệt → Mafee plan-bound như mọi lệnh.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(WC_ROOT, "mike", "bin"))
sys.path.insert(0, WC_ROOT)

from park_holdings import park_holdings, today_ict                      # noqa: E402
from compute_park_trim import (PARK_TARGET_F1, TRIM_BAND, STATE_FILE,   # noqa: E402
                               park_target_basket, etf_day_cap_live,
                               live_share, live_price_fn)
from trading_bot.plan import (LAG_ADV_PCT, LAG_ADV_MAX_STALE_DAYS,      # noqa: E402
                              _adv_for_gate)
from trading_bot.vn_market import LOT, round_lot                        # noqa: E402
from lag_forensic_filter import BANNED                                  # noqa: E402

FEE_RATE = 0.00075          # phí mua thật, = coding_guidelines §6 (0,075%)


def compute_add(account_label, asof=None, target=PARK_TARGET_F1, reserve_vnd=0.0,
                max_spend_vnd=None, active_nav_vnd=None, name_cap_pct=0.10,
                pp0buy_vnd=None, holdings=None, basket_override=None, share_override=None,
                adv_fn=None, day_cap_override=None, price_fn=None):
    asof = asof or today_ict()
    adv_fn = adv_fn or _adv_for_gate
    # name_cap là trần TẬP TRUNG bắt buộc (trading_rules.sizing.name_cap_pct) — không có NAV thì
    # không áp được ⇒ fail-closed thay vì âm thầm bỏ trần (quant-skeptic 2026-08-11).
    if not active_nav_vnd:
        raise ValueError("active_nav_vnd BẮT BUỘC — không có NAV thì không áp được name_cap 0,10")
    out = {"script": "mike/agents/DollarBill/tools/compute_park_add.py",
           "account": account_label, "asof": asof, "target_park": target,
           "reserve_vnd": float(reserve_vnd), "orders": [], "blocked": [], "notes": [],
           "at_or_above_target": []}

    h = holdings or park_holdings(account_label, asof=asof)
    rec = h.get("reconcile") or {}
    if not rec.get("ok", False):
        out["decision"] = "BLOCKED_RECONCILE"
        out["notes"].append("sổ lô LỆCH so với broker ⇒ không sinh đề xuất nào (cùng luật L1). "
                            f"mismatches={rec.get('mismatches')}")
        return out

    # ── Cổng DT5G — PORT NGUYÊN từ L1:275. Rổ parking chỉ được ĐO ở NEUTRAL (PARK_STATES={3}).
    # Ở chiều BÁN, thiếu cổng này chỉ làm "không bán" (vô hại). Ở chiều MUA, thiếu nó nghĩa là
    # tool sẽ size một lệnh mua 80% pool giữa BEAR/CRISIS — ngược hẳn allocator (w_LAG=0 ở BEAR).
    # quant-skeptic 2026-08-11 killer_objection: đây là chỗ "đối xứng CODE ≠ đối xứng RỦI RO".
    state = {}
    if os.path.exists(STATE_FILE):
        state = json.load(open(STATE_FILE, encoding="utf-8"))
    out["state"] = {"state": state.get("state"), "state_name": state.get("state_name"),
                    "date": state.get("date"), "etf_park_frac_live": state.get("etf_park_frac")}
    live_frac = state.get("etf_park_frac")
    if live_frac is not None and abs(float(live_frac) - target) > 1e-9:
        out["notes"].append(
            f"⚠️ ENGINE CHƯA ĐỒNG BỘ: target ở đây = {target:.2f} nhưng `etf_park_frac` LIVE = "
            f"{live_frac}. Chép dòng này vào notes plan.")
    if state.get("state") is None:
        out["decision"] = "BLOCKED_STATE"
        out["notes"].append(f"không đọc được DT5G state từ {STATE_FILE} ⇒ fail-closed, không mua")
        return out
    if int(state["state"]) != 3:
        out["decision"] = "SKIP_STATE"
        out["notes"].append(f"state={state.get('state')} ({state.get('state_name')}) ≠ NEUTRAL — "
                            "rổ parking chỉ được đo ở NEUTRAL, không tự suy target cho state khác")
        return out

    cash_total = h.get("cash_total_vnd")
    debt = h.get("cash_debt_vnd")
    div_recv = h.get("cash_dividend_receiving_vnd") or 0.0
    avail = h.get("cash_available_vnd")
    # ── 3 guard tiền của L1 — PORT NGUYÊN, không viết lại (CLAUDE.md §25 mục 2: bỏ bất kỳ cái
    # nào là để hở đúng một lối). Đặc biệt `debt is None` KHÔNG được ép về 0: ép = thổi phồng
    # trần "không margin" lên đúng bằng số nợ vay.
    if cash_total is None or debt is None:
        out["decision"] = "BLOCKED_CASH_BASIS"
        out["notes"].append("không đọc được totalCash/totalDebt ⇒ fail-closed (KHÔNG rơi về "
                            "availableCash, KHÔNG coi totalDebt thiếu là 0 — §25 CLAUDE.md)")
        return out
    park_mv = float(h["park_mv_vnd"])
    if (park_mv > 0 and float(cash_total) == 0 and float(debt) == 0
            and float(avail or 0) == 0):
        out["decision"] = "BLOCKED_CASH_BASIS"
        out["notes"].append("mọi field tiền = 0 trong khi sổ PARK > 0 ⇒ chữ ký lỗi feed DNSE "
                            "toàn-0 (sự cố 2026-07-27) ⇒ fail-closed")
        return out
    if float(cash_total) < float(avail or 0):
        out["decision"] = "BLOCKED_CASH_BASIS"
        out["notes"].append(
            f"totalCash {float(cash_total):,.0f}đ < availableCash {float(avail or 0):,.0f}đ — vi "
            "phạm bất biến kế toán ⇒ block tiền không đáng tin ⇒ fail-closed")
        return out
    cash = float(cash_total) - float(debt) - float(reserve_vnd)
    pool = cash + park_mv
    target_value = pool * target
    delta = target_value - park_mv
    out.update({"park_mv_vnd": park_mv, "cash_after_reserve_vnd": cash, "pool_vnd": pool,
                "target_park_vnd": target_value, "delta_vnd": delta,
                "threshold_vnd": pool * TRIM_BAND})

    # Trần TIỀN: mặc định = tiền mặt THUẦN còn lại (đã trừ reserve + cổ tức phải thu).
    # KHÔNG BAO GIỜ mặc định theo pp0Buy — pp0Buy của account có margin bao gồm cả hạn mức vay.
    # Nhưng pp0Buy VẪN là một trần độc lập phải tôn trọng (nó có thể THẤP HƠN tiền mặt sổ sách:
    # ZaloPay 2026-08-11 trần tiền mặt 146.046.482 > pp0Buy 145.946.201) — quant-skeptic 08-11.
    cash_ceiling = float(cash_total) - float(debt) - float(div_recv) - float(reserve_vnd)
    caps = [cash_ceiling]
    if pp0buy_vnd is not None:
        caps.append(float(pp0buy_vnd) - float(reserve_vnd))
    if max_spend_vnd is not None:
        caps.append(float(max_spend_vnd))
    budget = max(0.0, min(caps))
    out["cash_ceiling_no_margin_vnd"] = cash_ceiling
    out["pp0buy_ceiling_vnd"] = (float(pp0buy_vnd) - float(reserve_vnd)) if pp0buy_vnd is not None else None
    out["budget_vnd"] = budget

    if delta <= pool * TRIM_BAND:
        out["decision"] = "NO_ADD"
        out["notes"].append(f"PARK {park_mv/1e6:,.1f}tr vs target {target_value/1e6:,.1f}tr "
                            f"(pool {pool/1e6:,.1f}tr) — thiếu {max(0, delta)/1e6:,.1f}tr, "
                            f"chưa quá ngưỡng {pool*TRIM_BAND/1e6:,.1f}tr")
        return out
    if budget <= 0:
        out["decision"] = "NO_CASH"
        out["notes"].append(f"thiếu {delta/1e6:,.1f}tr so với target nhưng ngân sách tiền mặt "
                            f"thuần = {budget:,.0f}đ ⇒ không đề xuất lệnh nào")
        return out

    # ── Rổ MỤC TIÊU custom30V (PIT theo asof) — DÙNG LẠI hàm của L1 ──────────
    if basket_override is not None:
        basket_w, rebal_date, b_err = basket_override, "override", None
    else:
        basket_w, rebal_date, b_err = park_target_basket(asof)
    if not b_err and basket_w and not (0.99 <= sum(basket_w.values()) <= 1.01):
        b_err = f"Σ trọng số kỳ {rebal_date} = {sum(basket_w.values()):.4f} ≠ 1 (rổ hỏng)"
    if b_err or not basket_w:
        out["decision"] = "BLOCKED_BASKET"
        out["notes"].append(f"không đọc được rổ mục tiêu custom30V ({b_err}) ⇒ fail-closed")
        return out
    out["basket_rebal_date"] = rebal_date
    out["basket_n"] = len(basket_w)

    if day_cap_override is not None:
        day_cap, cap_err = day_cap_override, None
    else:
        day_cap, _n, cap_err = etf_day_cap_live(asof, sorted(basket_w))
    if cap_err or day_cap is None or day_cap <= 0:
        out["decision"] = "BLOCKED_DAYCAP"
        out["notes"].append(f"không đo được trần thanh khoản rổ ({cap_err}) ⇒ fail-closed")
        return out
    out["etf_day_cap_vnd"] = day_cap

    share, live_labels, share_err = (share_override, None, None) if share_override is not None \
        else live_share()
    if share_err or not share:
        out["decision"] = "BLOCKED_SHARE"
        out["notes"].append(f"{share_err} ⇒ fail-closed")
        return out
    out["adv_share"] = share
    out["live_labels"] = live_labels

    excluded = set(h["excluded_tickers"])
    unver = set(h["unverified_tickers"])
    if unver:
        out["decision"] = "BLOCKED_UNVERIFIED"
        out["notes"].append(f"có mã UNVERIFIED trong sổ ({sorted(unver)}) ⇒ fail-closed (§21)")
        return out

    # mv PARK hiện tại theo mã (chỉ lô PARK) + vị thế TỔNG mọi book (cho name_cap)
    per_tk = {}
    for l in h["park_lots"]:
        d = per_tk.setdefault(l["ticker"], {"qty": 0, "mv": 0.0, "px": l["market_price"]})
        d["qty"] += l["qty"]
        d["mv"] += l["mv_vnd"]
    bpos = h.get("broker_positions", {}) or {}

    # ── Rổ KHẢ THI + trọng số chuẩn hoá — SAO CHÉP ĐÚNG thứ tự loại của L1 ───
    price_fn = price_fn or live_price_fn(asof)
    dropped, feasible, px_of = [], {}, {}
    for tk in sorted(basket_w):
        w_raw = basket_w[tk]
        if tk in BANNED:
            dropped.append({"ticker": tk, "weight": w_raw, "reason": "BANNED vĩnh viễn"})
            continue
        if tk in excluded:
            dropped.append({"ticker": tk, "weight": w_raw,
                            "reason": "excluded_tickers — không mua, không bán"})
            continue
        px_i = per_tk[tk]["px"] if tk in per_tk and per_tk[tk]["px"] > 0 else None
        if px_i is None and tk in bpos and (bpos[tk].get("market_price") or 0) > 0:
            px_i = float(bpos[tk]["market_price"])
        px_err = None
        if px_i is None:
            px_i, px_err = price_fn(tk)
        if not px_i or px_i <= 0:
            dropped.append({"ticker": tk, "weight": w_raw,
                            "reason": f"không lấy được giá ({px_err}) ⇒ fail-closed"})
            continue
        if target_value * w_raw < LOT * px_i:
            dropped.append({"ticker": tk, "weight": w_raw,
                            "reason": f"target {target_value*w_raw:,.0f}đ < 1 lô "
                                      f"({LOT}cp × {px_i:,.0f}đ)"})
            continue
        feasible[tk] = w_raw
        px_of[tk] = float(px_i)
    w_sum = sum(feasible.values())
    if w_sum <= 0:
        out["decision"] = "BLOCKED_NO_FEASIBLE_BASKET"
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
            "đã CHUẨN HOÁ LẠI trên tập khả thi: "
            + "; ".join(f"{d['ticker']} {d['weight']*100:.2f}% ({d['reason']})" for d in dropped))

    want_raw = {tk: max(0.0, tgt[tk] - per_tk.get(tk, {}).get("mv", 0.0)) for tk in feasible}
    want_total = sum(want_raw.values())
    if want_total <= 0:
        out["decision"] = "NO_ADD_STRUCTURE"
        out["notes"].append("mọi mã trong rổ khả thi đều ở/trên trọng số mục tiêu")
        return out

    # ── BA trần, lấy cái CHẶT NHẤT ───────────────────────────────────────────
    # scale_delta là trần KHÔNG có ở L1 và BẮT BUỘC phải có ở đây (quant-skeptic 2026-08-11):
    # Σwant_i (thiếu hụt của các mã DƯỚI trọng số) LỚN HƠN delta (thiếu hụt của CẢ SỔ) đúng bằng
    # phần THỪA của các mã đang VƯỢT trọng số — mà đường MUA không chạm tới được. Mua trọn Σwant
    # ⇒ sổ PARK vọt LÊN TRÊN target 80% (đo 2026-08-11: 84,04% SpaceX / 87,38% ZaloPay), tức phá
    # đúng cái trần mà L1 sinh ra để giữ, rồi phiên sau L1 lại bán ngược = churn + 2 lần phí.
    # L1 ở chiều bán có tính chất đối xứng (Σsell > |delta| ⇒ về DƯỚI target) nhưng chiều đó là
    # THẬN TRỌNG nên chỉ cần CÔNG BỐ (underpark_after_vnd); chiều mua thì phải CHẶN.
    scale_delta = min(1.0, delta / want_total)
    scale_liq = min(1.0, day_cap / want_total)
    scale_cash = min(1.0, budget / (want_total * (1.0 + FEE_RATE)))
    scale = min(scale_delta, scale_liq, scale_cash)
    add_total = want_total * scale
    out.update({"structural_deficit_vnd": want_total, "add_total_vnd": add_total,
                "overshoot_if_unclamped_vnd": max(0.0, want_total - delta),
                "park_pct_if_unclamped": (park_mv + want_total) / pool if pool else None,
                "delta_binding": scale_delta <= min(scale_liq, scale_cash),
                "day_cap_binding": scale_liq <= min(scale_delta, scale_cash),
                "cash_binding": scale_cash < min(scale_delta, scale_liq),
                "scale": scale, "scale_delta": scale_delta, "scale_liq": scale_liq,
                "scale_cash": scale_cash})

    # ── Pass 1: trần từng mã (VND) sau MỌI trần, chưa làm tròn lô ────────────
    alloc, ceil_i = {}, {}
    for tk in sorted(feasible):
        want_vnd = want_raw[tk] * scale
        px = px_of[tk]
        if want_vnd <= 0:
            out["at_or_above_target"].append({"ticker": tk, "mv_vnd": per_tk.get(tk, {}).get("mv", 0.0),
                                              "target_vnd": tgt[tk]})
            continue
        adv, data_date, err = adv_fn(tk, asof)
        if err:
            out["blocked"].append({"ticker": tk, "reason": f"không đo được ADV: {err}"})
            continue
        if data_date:
            try:
                import datetime as _dt
                lag_days = (_dt.date.fromisoformat(asof) - _dt.date.fromisoformat(data_date)).days
            except Exception:
                lag_days = None
            if lag_days is not None and lag_days > LAG_ADV_MAX_STALE_DAYS:
                out["blocked"].append({"ticker": tk, "reason":
                                       f"ADV data {data_date} cũ {lag_days} ngày"})
                continue
        if adv <= 0:
            out["blocked"].append({"ticker": tk, "reason": f"ADV ≤ 0 (data {data_date})"})
            continue
        cap_i = LAG_ADV_PCT * adv * share
        # name_cap 0,10 NAV — trên vị thế TỔNG mọi book, không riêng PARK.
        held_all = float(bpos.get(tk, {}).get("qty", 0) or 0) * px
        name_room = max(0.0, name_cap_pct * float(active_nav_vnd) - held_all)
        # TRẦN CỨNG per-name (không bị scale): mua tới đây thì mã đó CHẠM đúng trọng số mục
        # tiêu tgt_i — pass 2 chỉ được thêm lô trong khoảng [alloc_i, ceil_i], không bao giờ
        # đẩy MỘT mã nào lên TRÊN trọng số mục tiêu của nó.
        ceil_i[tk] = min(want_raw[tk], cap_i, name_room)
        alloc[tk] = min(want_vnd, cap_i, name_room)
        out.setdefault("_meta_per_name", {})[tk] = {
            "px": px, "adv": adv, "adv_data_date": data_date, "cap_i": cap_i,
            "name_room": name_room, "want_vnd": want_vnd}

    # ── Pass 2: LÀM TRÒN LÔ theo phép "phần dư lớn nhất" (largest remainder) ─
    # VÌ SAO KHÔNG chỉ floor như L1: floor đơn thuần ném đi 22% ngân sách (đo thật 08-11:
    # 110,0tr mục tiêu → chỉ đặt được 85,5tr). L1 chấp nhận mất ~32% vì ở chiều BÁN, bán ÍT
    # hơn là hướng sai AN TOÀN. Ở chiều MUA, mua ít hơn nghĩa là giữ tiền mặt cao hơn thiết
    # kế — đúng cái vấn đề plan này sinh ra để sửa. Largest-remainder KHÔNG phải tham số rủi
    # ro mới: nó là phép phân bổ số nguyên tiêu chuẩn, mọi trần (tgt_i, %ADV, name_cap, ngân
    # sách, delta) vẫn nguyên vẹn và vẫn là ràng buộc CỨNG.
    # `hard_budget` là trần DUY NHẤT mà vòng largest-remainder dưới đây tôn trọng ở cấp TỔNG
    # (các trần per-name đi qua `ceil_i`). Nên MỌI trần cấp tổng phải có mặt ở đây, nếu không
    # pass 2 sẽ mở lại đúng cái pass 1 vừa siết: `ceil_i = min(want_raw, cap_i, name_room)` KHÔNG
    # mang `scale`, nên vòng phát-thêm-lô được phép leo từ `alloc_i` (đã scale) lên tới `want_raw`.
    # `day_cap` thiếu ở đây ⇒ trần thanh khoản TỔNG/phiên BỊ VƯỢT — bug thật do
    # `compute_park_add_selfcheck.py` T61 bắt ngay lần chạy đầu (2026-08-11): day_cap 50tr, tool
    # đề xuất 52tr (+4%). KHÔNG bit ngày 08-11 (day cap 1.352 tỷ vs lệnh ~110tr, chênh 4 bậc độ
    # lớn) nên output production KHÔNG đổi sau khi vá — đã verify lại từng đồng.
    # ×(1+FEE_RATE) vì `spent` tính GỒM phí, còn `delta`/`day_cap` là notional (cùng phép quy đổi
    # đang dùng cho `delta`), để so sánh cùng đơn vị.
    hard_budget = min(budget, delta * (1.0 + FEE_RATE), day_cap * (1.0 + FEE_RATE))
    qty_of, spent = {}, 0.0
    for tk in sorted(alloc, key=lambda t: -alloc[t]):
        px = out["_meta_per_name"][tk]["px"]
        room = max(0.0, hard_budget - spent) / (1.0 + FEE_RATE)
        q = round_lot(min(alloc[tk], room) / px)
        if q > 0:
            qty_of[tk] = q
            spent += q * px * (1.0 + FEE_RATE)
    # phát thêm từng LÔ cho mã có phần dư (alloc_i − đã cấp) lớn nhất, tới khi hết ngân sách
    while True:
        best, best_rem = None, 0.0
        for tk in alloc:
            px = out["_meta_per_name"][tk]["px"]
            cur = qty_of.get(tk, 0) * px
            if cur + LOT * px > ceil_i[tk] + 1e-6:
                continue                       # thêm 1 lô sẽ vượt trọng số mục tiêu của mã đó
            if spent + LOT * px * (1.0 + FEE_RATE) > hard_budget + 1e-6:
                continue                       # thêm 1 lô sẽ vượt ngân sách/delta
            rem = alloc[tk] - cur
            if rem > best_rem:
                best, best_rem = tk, rem
        if best is None:
            break
        px = out["_meta_per_name"][best]["px"]
        qty_of[best] = qty_of.get(best, 0) + LOT
        spent += LOT * px * (1.0 + FEE_RATE)
    out["hard_budget_vnd"] = hard_budget

    for tk in sorted(alloc):
        m = out["_meta_per_name"][tk]
        px, cap_i, name_room = m["px"], m["cap_i"], m["name_room"]
        qty = qty_of.get(tk, 0)
        if qty < LOT:
            out["blocked"].append({"ticker": tk, "reason":
                                   f"trần < 1 lô (muốn {m['want_vnd']:,.0f}đ, trần ADV "
                                   f"{cap_i:,.0f}đ, room name_cap {name_room:,.0f}đ, "
                                   f"ngân sách {hard_budget:,.0f}đ)"})
            continue
        val = qty * px
        w_t = out["target_weights"].get(tk, 0.0)
        held_qty = int(bpos.get(tk, {}).get("qty", 0) or 0)
        out["orders"].append({
            "ticker": tk, "side": "buy", "qty": int(qty), "ref_price": px,
            "value_vnd": val, "book": "PARK", "play_type": "PARK_ADD",
            "weight_target": w_t, "mv_vnd": per_tk.get(tk, {}).get("mv", 0.0),
            "target_vnd": tgt[tk], "want_vnd": m["want_vnd"], "alloc_vnd": alloc[tk],
            "per_name_ceiling_vnd": ceil_i[tk], "adv_cap_vnd": cap_i,
            "adv_capped": cap_i < m["want_vnd"], "adv_vnd": m["adv"],
            "adv_data_date": m["adv_data_date"],
            "name_cap_room_vnd": name_room, "held_qty_all_books": held_qty,
            "is_new_name": tk not in per_tk,
            "reason": (f"P2 park-sync (rổ {rebal_date}): đang "
                       f"{per_tk.get(tk, {}).get('mv', 0.0)/1e6:,.1f}tr vs target "
                       f"{tgt[tk]/1e6:,.1f}tr (w' {w_t:.2%} × park-target "
                       f"{target_value/1e6:,.1f}tr)"
                       + (f"; co theo trần Σ=delta/tiền/thanh khoản ×{scale:.3f}" if scale < 1 else "")
                       + (f"; BỊ CẮT bởi trần {LAG_ADV_PCT:.0%}ADV×{share:.2f}"
                          f"={cap_i/1e6:,.1f}tr" if cap_i < m["want_vnd"] else "")),
        })
    out.pop("_meta_per_name", None)

    out["decision"] = "ADD" if out["orders"] else "BLOCKED_ALL_NAMES"
    out["add_proposed_vnd"] = sum(o["value_vnd"] for o in out["orders"])
    out["add_proposed_with_fee_vnd"] = spent
    out["add_shortfall_vnd"] = add_total - out["add_proposed_vnd"]
    park_after = park_mv + out["add_proposed_vnd"]
    out["park_mv_after_vnd"] = park_after
    out["park_pct_after"] = park_after / pool if pool else None
    out["cash_after_vnd"] = cash - spent                     # cơ sở POOL (gồm cổ tức phải thu)
    out["cash_after_spendable_vnd"] = cash - float(div_recv) - spent   # cơ sở TIÊU ĐƯỢC (§25)
    out["underpark_after_vnd"] = max(0.0, target_value - park_after)
    out["overpark_after_vnd"] = max(0.0, park_after - target_value)
    if out["overpark_after_vnd"] > 0:
        out["notes"].append(
            f"⚠️ SAU KHI MUA, PARK = {park_after/1e6:,.1f}tr = {park_after/pool:.2%} pool, TRÊN "
            f"target {target:.0%} ({target_value/1e6:,.1f}tr) {out['overpark_after_vnd']/1e6:,.2f}tr "
            f"— nếu vượt quá băng {TRIM_BAND:.1%} thì L1 sẽ bán ngược lại phiên sau (churn). "
            "CHÉP dòng này vào notes plan.")
    if out["underpark_after_vnd"] > pool * TRIM_BAND:
        out["notes"].append(
            f"⚠️ SAU KHI MUA, PARK = {park_after/1e6:,.1f}tr = {park_after/pool:.1%} pool, VẪN "
            f"DƯỚI target {target:.0%} ({target_value/1e6:,.1f}tr) "
            f"{out['underpark_after_vnd']/1e6:,.1f}tr — nguyên nhân: "
            + ("NGÂN SÁCH TIỀN MẶT (không dùng margin)" if out.get("cash_binding") else "")
            + (" / trần thanh khoản rổ" if out.get("day_cap_binding") else "")
            + " / làm tròn lô + trần %ADV per-name. CHÉP dòng này vào notes plan.")
    return out


def main():
    ap = argparse.ArgumentParser(description="P2 park-add — CHỈ ĐỌC, đề xuất lệnh MUA sổ PARK")
    ap.add_argument("--account", required=True)
    ap.add_argument("--asof", default=None)
    ap.add_argument("--target", type=float, default=PARK_TARGET_F1)
    ap.add_argument("--reserve-vnd", type=float, default=0.0,
                    help="tiền plan đã cam kết cho lệnh khác (discretionary/LAG/BAL), gồm phí")
    ap.add_argument("--max-spend-vnd", type=float, default=None,
                    help="trần tiền cho riêng phần PARK (mặc định = tiền mặt thuần còn lại)")
    ap.add_argument("--active-nav-vnd", type=float, required=True,
                    help="active_nav để áp name_cap 0,10/mã — BẮT BUỘC (fail-closed)")
    ap.add_argument("--pp0buy-vnd", type=float, default=None,
                    help="pp0Buy đo sống — dùng làm trần THỨ HAI (không thay trần tiền mặt)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    r = compute_add(a.account, asof=a.asof, target=a.target, reserve_vnd=a.reserve_vnd,
                    max_spend_vnd=a.max_spend_vnd, active_nav_vnd=a.active_nav_vnd,
                    pp0buy_vnd=a.pp0buy_vnd)
    if a.out:
        tmp = a.out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        os.replace(tmp, a.out)
    print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
