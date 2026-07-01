# EXTREME-regime execution gate — backtest validation (Step 1)

> Taylor (Quant) · 2026-07-01 · job Taylor_20260701_052919
> Validates the mechanism in `data/exec_extreme_regime_proposal.md` §3 BEFORE any production wire.
> Scripts: `fetch_intraday_cache.py` (data) · `extreme_replay.py` (replay) · raw: `data/extreme_replay.csv`
> Chart: `data/extreme_regime_backtest.png`

## Data
- **Source**: vnstock VCI 15-minute intraday bars (`Quote.history(interval="15m")`), disk-cached, rate-limited.
- **Coverage (HARD LIMIT)**: VCI intraday only reaches back to **2023-10-30**. The 2022 crash (the proposal's
  anchor episode) is **NOT available intraday** — only daily OHLC. So the biggest true multi-day cascade in VN
  history could not be replayed. Validation window = **2024-04 → 2026-03**.
- **Universe**: 18 liquid Tier-1 names (banks, FPT, HPG, brokers, MWG, GAS, VNM, VHM/VRE) — the names actually in
  the production book. (Illiquid air-pocket false-triggers are NOT stress-tested here — handled by the design's
  `day_volume` floor + 2-poll confirm + corp-action |gap|>15% guard; note VNE −54% on 2026-06-08 is a
  corp-action artifact the guard would reject.)
- **Episodes** (market-wide, VNINDEX big-down + breadth-cluster): 2024-04-15, 2024-08-05 (yen-carry),
  **2025-04-03 / -04-08 / -04-09 (US tariff CASCADE, multi-day)**, 2025-07-29, 2025-10-20,
  **2026-03-09 (1-day DIP, bounced next session)**.

## Method (honest, bar-level — no order book, no look-ahead)
- **NORMAL** = current executor: sell limit rests at `ref×0.97` (static −3% cap). Fills the first 15m bar whose
  HIGH ≥ ref×0.97. If price gaps below −3% at open and never revisits → **STRANDED same-day** → modelled fallback
  = carry to next-session close.
- **EXTREME** = proposal §3a/§3c: once `last` ≤ floor×(1+3%) (within 3% of the daily floor), cross down to floor →
  fills at the volume-weighted typical price of bars from trigger-arm onward.
- Reconciliation (replaces the earlier tautological self-check): the two headline sell numbers are recomputed
  a second, independent way straight from the raw cached parquet (not the intermediate CSV) and asserted equal —
  a genuine identity, IDENTITY PASS to 1e-9. threads=1; no `profit_*`/`O*`/`Pattern_*` columns.
- **Fill-model caveats (understated/overstated both ways)**: EXTREME assumes we fill the full remaining qty at
  floor VWAP — on a truly locked floor with a huge sell queue we might only partially fill (EXTREME advantage in
  cascades is thus **optimistic**). NORMAL "carry to next close" ignores a possible better intraday next-day fill
  (NORMAL is thus mildly **pessimistic**). Both are rough proxies; treat magnitudes as indicative, not exact.

## Result — SELL side (the load-bearing claim)

> **Rev 2 (post quant-skeptic verify)**: fixed 3 audit gaps — (1) drop VCI's NaN 23:45 pad bar so the
> down-day filter fires (denominator corrected 144→**126** real <−3%-close sells; strand 15%→**17%**);
> (2) buy leg persisted to `data/extreme_replay_buy.csv`; (3) tautological self-check replaced with a
> genuine independent recompute from raw parquet — **IDENTITY PASS to 1e-9**. Headline sell numbers
> unchanged (the NaN bug was harmless to the 22 gap-lock cases, as the skeptic predicted).

Down-day sells where the static −3% cap is engaged: **126** (real <−3% close, across 18 names × 8 episodes).
Static cap **strands same-day (gap-lock)** on **22 / 126 (17%)** — these are the only cases the two regimes differ.

| Gap-lock sells (n=22) | NORMAL (static → carry) | EXTREME (sell-to-floor) |
|---|---|---|
| Mean exit | −5.55% | **−6.55% (−1.0pp)** |
| p05 | −12.3% | −6.9% |
| **Worst-case** | **−13.4%** | **−6.9%** |
| Dispersion (std) | 3.8pp | **0.3pp** |
| Same-day fill-rate | 0% | 100% |

**Episode split (this is the whole story):**
- **Apr-2025 multi-day CASCADE (n=8): EXTREME +2.63pp.** Carrying into the next −7% day is catastrophic
  (GAS −13.4%, MWG −12.4%); sell-to-floor caps every name at ~−6.7%.
- **Mar-2026 one-day DIP that bounced (n=14): EXTREME −3.08pp.** Selling to floor locks the bottom;
  carry-and-bounce recovers to −3.6%.
- EXTREME beat NORMAL on only **9/22 (41%)** — but its losses are bounded (a dip that recovered) while its wins
  avoid the fat left tail (a cascade that continued).

## Result — BUY-pause side
Crash-day buys: 126. Pausing (buy next session) vs buying into the crash day:
- Mean entry: NORMAL buy-today −6.05% vs EXTREME pause→next −4.98% → **pausing is −1.07pp worse on mean**
  (you systematically skip the cheapest day). Range p05 −6.5pp / p95 +5.6pp.
- Split: Apr-2025 cascade +0.09pp (neutral), Mar-2026 dip −3.16pp (misses the dip).
- Worst-case protection (p95 +5.6pp): pausing saves you when the cascade continues. Mild fail-safe, as the
  proposal claims ("worst case: miss a nhịp, mai mua lại").

## Verdict (Step 1)
**Mechanism VALIDATED as tail-insurance — NOT as a return-enhancer.** Both the sell-to-floor and buy-pause legs
trade **~1pp of mean edge for tail compression**: sell worst-case −13.4% → −6.9%, dispersion 3.8pp → 0.3pp,
same-day fill 0% → 100%. This is **exactly the DT5G verdict pattern** ("fail-safe risk gate / insurance, not a
return-enhancer") and matches the approved design's own §4 framing (default-OFF, insurance).

Causally it **cannot** tell a cascade from a one-day dip in real time — nothing can — so it bounds the outcome at
one floor either way. It is therefore correct **only** as a deliberately-activated risk gate, **never** left on for
alpha. The net-benefit *sign* is regime-dependent (positive in fat-tailed cascades like 2022/Apr-2025, negative in
the more common V-shaped washout) and **cannot be cleanly established** with the available data (no 2022 intraday,
no order book, only ~2 true cascades in-window) — as the proposal §4 predicted.

**Recommendation**: proceed to code **default-OFF** (per approved design); document it as tail-insurance, not
return; require deliberate activation + user sign-off before any LIVE enable. Do NOT re-tune params to this
history (thin, dip-dominated sample).
