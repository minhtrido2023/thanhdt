---
name: T+1 Intraday Buy-Point Research Plan
description: Future research direction — optimize buy POINT within T+1 day (open vs midday low vs VWAP vs ATC) without violating T+1 constraint. Per user direction 2026-05-17.
type: project
originSessionId: df3c1340-40c2-46c7-b6dc-247737308843
---
# T+1 Intraday Buy-Point Optimization (research plan)

**Context (2026-05-17)**: After adopting realistic T+1 Open execution as canonical
(simulate_holistic_nav.py default `t1_open_exec=True`), the 12y v11 stack delivers
**18.18% CAGR** (vs 20.10% under the legacy look-ahead T-close exit).

User direction:
> phải apply cái realistic assumption, không phải cái không thực tế để tạo
> kết quả cao. quan trọng là việc mua với giá khởi điểm, hay giá nào trong
> phiên sẽ mang đến kết quả tốt hơn. Tôi nghĩ là dựa trên kết quả nghiên cứu
> intraday có thể cải thiện thời điểm mua vào trong ngày. nhưng cơ bản vẫn
> phải là ngày T+1

→ T+1 day constraint is HARD. Question: which time/price within T+1 day gives
the best fill?

## Reference baseline

T+1 Open execution. Sim uses `open_prices[ticker][T+1]` as buy fill price.
Already realistic-aligned with `recommend_holistic.py` (signals run pre-market,
orders placed at open).

## Candidate intraday entry points

1. **T+1 Open (current canonical)** — simplest, no intraday data needed for prod
2. **T+1 11:15 LIMIT** — Layer 3 finding (`layer3_rules_backtest.md`): TOP30
   +0.90pp / MIDCAP +1.18pp / PENNY +1.73pp lift per trade vs ATC; miss-rate <2%
3. **T+1 midday Low** — buy at session low (impossible in live without limit
   order placed pre-market at unknown level); use as oracle upper-bound
4. **T+1 VWAP** — algorithmic TWAP/VWAP fill; benchmark for institutional flows
5. **T+1 ATC (close)** — wait-and-see, may miss runners but avoids opening gaps

## Existing evidence

- **`layer3_rules_backtest.md`** — 159,712 combo events: E1_T1115_LIM (entry
  11:15 limit) + X1_T0945_LIM (exit 09:45 limit) wins ALL segments. **Expected
  +0.8-1.5pp CAGR alpha for BA-system 50B**. Real BA BUYs (n=22): DEEP_VALUE
  plays prefer ATC entry.
- **`layer3_timing_findings.md`** — BUY U-shape: rẻ nhất 11:15-13:00. NET @
  slippage: TOP30 @ T1115 +0.14%/trade, MIDCAP @ ATC +0.08%.
- **`layer3_full_findings_consolidated.md`** — SELL intraday STOP saves +8.5pp/event
  (synthetic) **but FAILS on real BA flow** (`layer3_backfill_reality_check.md`
  & `intraday_stop_full_backtest.md` — full 12y showed -4.31pp CAGR). Lesson:
  intraday-stop synthetic ≠ real. Apply same skepticism to intraday BUY claims.

## Research design

1. Extend `simulate_holistic_nav.py` with `entry_fill_mode` parameter:
   - `"open"` (current default, realistic, no extra data needed)
   - `"vwap_30m"` — average of 09:15-09:45 prices (requires intraday bars)
   - `"limit_1115"` — fill at 11:15 close price; if max(11:15, low_pre_1115) >
     limit_price then skip (miss event)
   - `"atc"` — fill at T+1 Close
2. Pull intraday bars from `vnstock` for full 12y or available history
   (likely 2-3y only — Vietnam intraday history limited)
3. Run baseline + each mode on V11 stack 50B 2014-2026 (or available subset)
4. Report: CAGR, Sharpe, MaxDD, miss-rate (limit modes only), per-segment lift
5. **CRITICAL**: Validate on real BA journal flow (not synthetic universe).
   Layer 3 backfill check showed synthetic results misleading when applied
   to production flow distribution.

## Decision rule

Adopt intraday mode ONLY IF:
- ≥ +0.5pp CAGR on full 12y realistic stack
- Sharpe equal or higher
- Miss-rate < 5% (for limit modes)
- Per-segment lift positive in TOP30 AND MIDCAP (not just averaged)
- Validates on real journal forward-flow (≥ +0.3pp per trade alpha)

If 11:15 limit holds up: integrate as default `entry_fill_mode` in
`simulate_holistic_nav.py` + emit limit-order recommendations in
`recommend_holistic.py` daily output (instead of "buy at open").

## Reference scripts (existing)

- `layer3_rules_backtest.md` — combo grid results
- `layer3_intraday_timing.py` — daily intraday scoring script
- `layer3_paper_trade.py` — paper-trade tracker

## Status

📅 **NOT STARTED** as of 2026-05-17. Captured per user direction; pick up after
v11 realistic baseline accepted by user and any planned holdout verification
completes.
