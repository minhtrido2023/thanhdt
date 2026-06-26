# Intraday Fill-Timing Rule (Layer-3) — spec for execution

> Author: Taylor, 2026-06-26. Backtest: `intraday_fill_timing.py` (data/intraday_1m, 16 names, 9670 ticker-days). Finding on bus 2026-06-26. **This is the WHEN-to-fill layer; it composes ON TOP of the adaptive cross_mode (HOW-to-fill, already live).**

## The edge (vs prior-day close, BUY: lower=better)
| time | BUY cost | vs day-VWAP |
|---|---|---|
| Open | +18.7 bps (worst) | +13.8 (above avg) |
| **11:15** | **+1.1 bps (best)** | **−5.4 (intraday trough)** |
| ATC | +6.9 bps | −0.3 |

SELL: **Open is the best exit ~50% of days** (+18.7 vs prior close). Same VN morning-premium: worst to buy, best to sell.

## RULE
- **BUY → concentrate fills in the late-morning window ≈ 10:45–11:15** (the intraday trough). Do NOT front-load at the open. Saves ~17.6 bps vs Open; ~5–6 bps beyond uniform/VWAP slicing.
- **SELL → concentrate at the T+1 Open** (sell into the morning premium).
- **TOP / high-conviction BUY → ATC is an accepted alternative** (≈12 bps better than Open + the close auction guarantees the fill) — use when fill-certainty matters more than the last few bps.
- Within the chosen window, keep the existing **adaptive cross_mode** (DIP < 1% ADV, TWAP ≥).

## Ownership / handoff
- **Mafee (executor, primary):** make the slice schedule **side-aware** — BUY: weight slices toward 10:45–11:15 (light at the open, heavy late-morning); SELL: weight toward the open. Configurable window + on/off. This is the core edge; needs no per-order plan tag.
- **DollarBill (plan, optional refinement):** to enable TOP→ATC, tag high-conviction buys in the plan so the executor routes them to the ATC auction instead of 11:15.
- **Taylor:** validated the edge; will re-check on the illiquid tail and monitor the morning-premium persistence.

## Caveats
- 16 liquid names; illiquid tail not yet tested.
- Edge is modest (5–17 bps) with high day-to-day variance (std 100–220 bps) — it's an AVERAGE edge over many trades, not per-trade certainty.
- Morning-premium is a 2023–26 microstructure feature — persistent but monitor; rule should be configurable/disable-able.
- Audited backtest assumes T+1 Open (pessimistic) → live with this rule should fill BETTER than the audit, not worse.
- **LIVE activation needs user approval** (go-live config, real money) — implement gated/paper first.
