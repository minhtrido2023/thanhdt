#!/usr/bin/env python3
"""
rubber_trend_break.py — TREND_BREAK / TREND_OK: long-horizon REGIME CONFIRMATION
===============================================================================
An INDEPENDENT tier next to rubber_weekly.py's WATCH/ALERT. It answers a different
question on a different cadence, so it must never be folded into that ladder:

    WATCH/ALERT (rubber_weekly.py) : "did anything odd happen THIS WEEK?"  (daily feed,
                                      %-move thresholds, fires weekly-ish)
    TREND_BREAK / TREND_OK (here)  : "has the LONG-TERM trend structure broken?"
                                      (WB monthly series, fires ~1x / 18.7 months)

Design + backtest: mike/agents/Taylor/research/rubber_trend_break_design_20260806.md
(job Taylor_20260806_131319, user-approved 2026-08-06). Parameters below are the
approved ones; do NOT re-derive them here.

  * line   = MA10 on the WB MONTHLY series (= MA200-daily equivalent).
             NOT an OLS trendline: an OLS line rotates with slope, so a flat price in
             a strong up-leg "breaks" it — measured precision 49-53% and whipsaw 60-77%
             vs 73-85% / 8-20% for the MA family (design §2).
             NOT the daily feed: on assets that DO have a long daily history (the rubber
             stocks themselves), a MA200-daily crosses 5.2x more often than the monthly
             equivalent — a different object, and one this backtest does not cover
             (design §4). The daily RSS3 series is also far too short (34 real prints,
             MA200-daily ETA 2027-03).
  * event  = monthly price closes BELOW the line, CONFIRMED on 2 consecutive months
             (whipsaw 20% -> 8%, precision 73% -> 85%; design §5.2).
  * state  = DOWNTREND / UPTREND. This is a STATE with an open and a close, not a
             one-shot event; the cross back above (also confirmed 2 months) closes it.
  * the current, still-running month is estimated from the daily feed's REAL prints and
             any state that DEPENDS on that estimate is flagged PROVISIONAL until the
             World Bank publishes the month.

*** HOW THIS SIGNAL MUST BE READ — this is not a caveat, it is the finding ***
TREND_BREAK is a REGIME CONFIRMATION, not a forecast and NOT a sell signal.
  - It confirms a regime that has ALREADY started: median lag 4 months after the peak,
    median -24% of the decline already gone by the time it fires.
  - It does NOT predict further decline: P(price falls another >=15% within 6 months
    | signal) = 31%, versus a 32% base rate over all months. Zero information.
  - It is NOT a reason to sell the rubber names: historically GVR/PHR/DPR/DRI/TRC/HRC
    averaged +26.5% over the 12 months AFTER the signal, versus a +12.5% base rate
    (CI95 [+6.5,+50.4], does not contain 0) — the evidence points the OTHER way.
Every message this module emits carries those three lines. A red tier named
"TREND_BREAK" firing once every 1.5 years is read as "sell" unless it says otherwise.

Limits worth keeping in view: N = 5 down-cycles / 13 events over 20.2 years — the whole
population of the data, but a small one; N_trials ~= 63 comparisons behind the design, so
no single CI is treated as evidence (design §6).
"""
import os
import pandas as pd

# --- approved parameters (design §5.1) ------------------------------------------
MA_WIN = 10        # months; MA10 monthly == MA200 daily equivalent
CONFIRM = 2        # consecutive months on the new side before the state flips

DOWN, UP, UNKNOWN = "DOWNTREND", "UPTREND", "UNKNOWN"
SIGNAL_OF = {DOWN: "TREND_BREAK", UP: "TREND_OK"}

# Backtest figures quoted in every outgoing message (design §3a/§3c/§3d). Kept as
# constants so the alert text and the docs can never drift apart silently.
BT = {"recall": "5/5", "precision": "11/13 = 85%", "freq_months": 18.7,
      "p_further_drop": 31, "p_further_drop_base": 32,
      "stock_fwd12m": 26.5, "stock_fwd12m_base": 12.5}


def monthly_with_current(monthly_csv, daily_csv=None):
    """WB monthly series (mid-month anchor, same convention as rubber_weekly.py) plus a
    PROVISIONAL point for any month newer than the last WB print, estimated as the mean
    of that month's REAL daily prints (src != wb_seed — a seed is a copy of a WB monthly
    point, folding it back in would be circular).
    Returns (series, provisional_month | None)."""
    m = pd.read_csv(monthly_csv)
    s = pd.Series(m["price"].astype(float).values,
                  index=pd.to_datetime(m["month"].astype(str) + "-15"))
    s = s[s.notna()].sort_index()
    prov = None
    if daily_csv and os.path.exists(daily_csv):
        d = pd.read_csv(daily_csv)
        d["date"] = pd.to_datetime(d["date"])
        real = d[(d["src"] != "wb_seed") & d["rss3_usdkg"].notna()]
        if len(real) and len(s):
            last_wb = s.index[-1].to_period("M")
            newer = real[real["date"].dt.to_period("M") > last_wb]
            for per, g in newer.groupby(newer["date"].dt.to_period("M")):
                s.loc[pd.Timestamp(f"{per}-15")] = float(g["rss3_usdkg"].mean())
                prov = str(per)
            s = s.sort_index()
    return s, prov


def trend_state(s, win=MA_WIN, confirm=CONFIRM):
    """Current confirmed regime + the trajectory that produced it.
    Causal by construction: the state at month t uses only months <= t."""
    ma = s.rolling(win).mean()
    below = (s < ma) & ma.notna()
    if ma.isna().all():
        return {"state": UNKNOWN, "note": f"cần >= {win} tháng, mới có {len(s)}",
                "n_months": len(s)}
    state, since, states = UP, s.index[0], []
    for i in range(len(s)):
        if ma.isna().iloc[i]:
            states.append(None); continue
        w = below.iloc[max(0, i - confirm + 1):i + 1]
        if len(w) == confirm and w.all() and state != DOWN:
            state, since = DOWN, s.index[i]
        elif len(w) == confirm and (~w).all() and state != UP:
            state, since = UP, s.index[i]
        states.append(state)
    cur_ma = float(ma.iloc[-1]); cur = float(s.iloc[-1])
    return {"state": state, "since": since, "price": cur, "ma": cur_ma,
            "dist_pct": (cur / cur_ma - 1) * 100,
            "months_below": int(below.iloc[-confirm:].sum()),
            "n_months": len(s), "states": pd.Series(states, index=s.index)}


def evaluate(monthly_csv, daily_csv=None, win=MA_WIN, confirm=CONFIRM):
    """Full tier evaluation.

    `state`      — on the full series, i.e. including the estimated running month.
    `state_firm` — on PUBLISHED months only. This is the one anything durable (a stored
                   state, a Telegram) must be built on: it can never move because an
                   unpublished estimate moved.
    `provisional`— the two disagree, i.e. the reading depends on a figure World Bank has
                   not published yet (design §5.2 layer 3).

    `state_firm`/`since_firm` are ALWAYS present (equal to `state`/`since` when there is
    no running-month estimate) so callers never have to special-case their absence — the
    first version of trend_break_check() read `state` on its baseline path and would have
    baked an unpublished month into production state permanently (found by quant-skeptic,
    2026-08-06; regression test in rubber_weekly_selfcheck.py §8d).

    Note the estimate can only ADD a flip, never cancel one: with confirm=2 a flip needs
    the last two months on the same side, so a single appended month cannot undo a flip
    that the published months already made. Hence the worst case here is a signal arriving
    one month later, never a signal silently lost."""
    s, prov = monthly_with_current(monthly_csv, daily_csv)
    r = trend_state(s, win, confirm)
    r["prov_month"] = prov
    r["provisional"] = False
    r["state_firm"], r["since_firm"] = r["state"], r.get("since")
    if prov and r["state"] != UNKNOWN:
        r_firm = trend_state(s[s.index < pd.Timestamp(f"{prov}-15")], win, confirm)
        r["state_firm"] = r_firm["state"]
        r["since_firm"] = r_firm.get("since")
        r["provisional"] = (r_firm["state"] != r["state"])
    return r


def message(r, prev_state=None, html=False):
    """Human-readable text for a state FLIP. The three read-me-correctly lines are
    mandatory and are not optional formatting — see the module docstring."""
    sig = SIGNAL_OF.get(r["state"], "TREND_?")
    b = lambda t: f"<b>{t}</b>" if html else t
    head = ("🔴 " if r["state"] == DOWN else "🟢 ") + b(f"CAO SU — {sig}")
    what = ("giá tháng ĐÓNG DƯỚI đường xu thế dài hạn"
            if r["state"] == DOWN else "giá tháng cắt LÊN LẠI trên đường xu thế dài hạn")
    L = [f"{head} ({'xác nhận chế độ' if not r['provisional'] else 'TẠM TÍNH'})",
         f"RSS3 {b(f'{r['price']:.2f} USD/kg')} vs MA200-eq (MA{MA_WIN} tháng) "
         f"{r['ma']:.2f} → {r['dist_pct']:+.1f}%",
         f"{what}, xác nhận {CONFIRM} tháng liên tiếp · trạng thái từ {r['since']:%Y-%m}"
         + (f" (trước đó: {prev_state})" if prev_state else "")]
    if r["provisional"]:
        L.append(f"⏳ TẠM TÍNH: dựa vào tháng {r['prov_month']} CHƯA đóng (ước lượng bằng "
                 f"trung bình các phiên thật trong tháng). Chỉ chốt khi World Bank công bố "
                 f"tháng này — chưa gửi Telegram/Bill.")
    L += [f"Tần suất lịch sử ~1 lần/{BT['freq_months']} tháng · bắt chu kỳ "
          f"recall {BT['recall']}, precision {BT['precision']}",
          "",
          b("⚠️ ĐÂY LÀ TÍN HIỆU XÁC NHẬN CHẾ ĐỘ (regime-confirmation), "
            "KHÔNG PHẢI TÍN HIỆU BÁN VÀ KHÔNG PHẢI DỰ BÁO."),
          f"• Không dự báo giảm tiếp: P(giảm thêm ≥15% trong 6 tháng sau tín hiệu) = "
          f"{BT['p_further_drop']}%, gần bằng base rate {BT['p_further_drop_base']}% "
          f"→ không thêm thông tin nào.",
          f"• KHÔNG phải cớ bán cổ phiếu cao su: lịch sử rổ GVR/PHR/DPR/DRI TĂNG trung bình "
          f"+{BT['stock_fwd12m']}% trong 12 tháng SAU tín hiệu (base +{BT['stock_fwd12m_base']}%).",
          "• Tín hiệu bắn TRỄ trung vị 4 tháng sau đỉnh, lúc bắn thì trung vị −24% của cú "
          "giảm đã đi qua. Nó xác nhận chế độ đã bắt đầu, không nhìn thấy trước.",
          "→ Dùng làm BỐI CẢNH chế độ dài hạn cho mô hình/kế hoạch, không phải lệnh hành động."]
    return "\n".join(L)


def note_lines(r):
    """Markdown block for data/rubber_watch.md."""
    if r["state"] == UNKNOWN:
        return ["## Xu thế dài hạn — TREND_BREAK",
                f"- Chưa tính được: {r.get('note', 'thiếu dữ liệu tháng')}", ""]
    sig = SIGNAL_OF[r["state"]]
    badge = "🔴 TREND_BREAK (dưới đường)" if r["state"] == DOWN else "🟢 TREND_OK (trên đường)"
    L = ["## Xu thế dài hạn — TREND_BREAK (tầng ĐỘC LẬP, nhịp THÁNG)",
         f"- **Trạng thái:** {badge} — từ {r['since']:%Y-%m}"
         + (f" · ⏳ TẠM TÍNH (tháng {r['prov_month']} chưa đóng)" if r["provisional"] else ""),
         f"- **Giá tháng:** {r['price']:.2f} USD/kg · **MA200-eq (MA{MA_WIN} tháng):** "
         f"{r['ma']:.2f} → **{r['dist_pct']:+.1f}%** so với đường",
         f"- Tháng dưới đường trong {CONFIRM} kỳ gần nhất: {r['months_below']}/{CONFIRM} "
         f"· chuỗi {r['n_months']} tháng (World Bank Pink Sheet)"]
    if r.get("prov_month"):
        L.append(f"- Tháng {r['prov_month']} là ước lượng từ các phiên ngày thật "
                 + ("(trạng thái KHÔNG phụ thuộc vào nó)" if not r["provisional"]
                    else "và trạng thái ĐANG phụ thuộc vào nó → chưa chốt"))
    L += [f"- Cách đọc: **XÁC NHẬN CHẾ ĐỘ dài hạn, KHÔNG phải tín hiệu bán/dự báo.** "
          f"P(giảm thêm ≥15%/6th sau tín hiệu) = {BT['p_further_drop']}% ≈ base "
          f"{BT['p_further_drop_base']}%; rổ CP cao su fwd-12m sau tín hiệu "
          f"+{BT['stock_fwd12m']}% vs base +{BT['stock_fwd12m_base']}%.",
          f"- Độc lập với WATCH/ALERT ở trên (khác chân trời: 6–24 tháng vs 1 tuần; "
          f"khác nhịp: ~1 lần/{BT['freq_months']} tháng vs hàng tuần).", ""]
    return L


if __name__ == "__main__":
    W = os.path.dirname(os.path.abspath(__file__))
    r = evaluate(os.path.join(W, "data", "rubber_monthly.csv"),
                 os.path.join(W, "data", "rubber_weekly.csv"))
    print("\n".join(note_lines(r)))
    if r["state"] != UNKNOWN:
        print("--- mẫu tin nhắn nếu trạng thái này vừa lật ---")
        print(message(r))
