---
name: Layer 3 v4 Paper-Trade Shadow Tracker
description: Daily tracker for the Layer 3 v4 asymmetric BUY-ATC / SELL-OPEN rule. Detects rule breakage via rolling 30-entry alpha statistical alarms.
type: project
originSessionId: df3c1340-40c2-46c7-b6dc-247737308843
---

# Layer 3 v4 Shadow Tracker

**Purpose**: Verify that the deployed asymmetric BUY-ATC + SELL-OPEN rule
(Layer 3 v4, 2026-05-17) continues to deliver alpha in live BA-system flow.
Raise alarm if/when the rule stops working.

## Architecture

Script: `layer3_v4_shadow.py`
Bat wrapper: `layer3_v4_shadow_run.bat`
Scheduled task: `Layer3v4Shadow` (daily 15:30, Windows Task Scheduler)
Log CSV: `data/layer3_v4_shadow_log.csv`
Report: `data/layer3_v4_shadow_report.md`
Cron output: `data/layer3_v4_shadow_cron.log`

## Rule under test

For each new BA-system pick:
1. **T1_TOP tickers** (avg session VND traded ≥ 50B over 2.5y): place **MOC market BUY at T+1 14:45 ATC**
   - If ATC bar volume × 20% ≥ position size: fill at p_atc
   - Else: fallback to T+1 09:15 Open price
2. **Non-T1_TOP** (T2_MID / T3_LIQUID / T4_THIN): place **market BUY at T+1 11:15**
   - If 11:15 bar exists: fill at p_t1115
   - Else fallback to T+1 Open
3. **Sell side**: [REDACTED] T+1 09:00 OPEN/ATO (canonical, not paper-traded — already validated in Phase 5)

Baseline for alpha computation = **T+1 BQ.Open** (the old canonical rule).

`alpha_vs_open_pp = (p_open - p_applied) / p_open × 100`

Positive alpha = we paid LESS than baseline (good).
Negative alpha = we paid MORE than baseline (bad).

## Daily workflow

1. **15:30 each weekday**: `Layer3v4Shadow` scheduled task runs `layer3_v4_shadow_run.bat`:
   - `python layer3_v4_shadow.py update` → ingest new picks from `ba_book_*.csv`, compute alpha, append to log
   - `python layer3_v4_shadow.py alert` → write one-line traffic light to cron log
2. **Weekly** (optional Telegram): run `python layer3_v4_shadow.py report` and copy markdown to chat

## CLI modes

```bash
# Daily auto-run
python layer3_v4_shadow.py update                # process new picks (default from today)
python layer3_v4_shadow.py update --from-date 2026-05-01

# Bulk backfill
python layer3_v4_shadow.py backfill              # default from 2025-06-01
python layer3_v4_shadow.py backfill --fetch-missing  # use vnstock for missing intraday (slow)

# Reports
python layer3_v4_shadow.py report                # full markdown report
python layer3_v4_shadow.py alert                 # one-line traffic light (Telegram-ready)
```

## Decision rule (statistical alarms)

Computed over rolling 30 most recent entries:

| Status | Trigger | Interpretation |
|---|---|---|
| 🟢 **GREEN** | mean alpha ≥ +0.50pp/trade AND p_one_tail < 0.10 | Rule healthy, continue |
| 🟡 **YELLOW** | 0 < alpha < +0.50pp OR n < 20 OR CI crosses zero | Monitor, no action |
| 🔴 **RED** | mean alpha < 0 AND p_one_tail < 0.10 (negative significant) | **RULE BREAKAGE** — revert `recommend_holistic.py` to T+1 Open canonical BUY |
| ⚪ NO_DATA | no entries | First-run state |

`p_one_tail` is a z-test approximation: `p = 0.5 × (1 − erf(z / √2))` with
`z = mean / (sd / √n)`. Conservative — assumes normal-ish distribution.

## Initial backfill (2026-05-17)

Bootstrapped log with 68 entries from:
1. Live `ba_book_*.csv` (3 dates, 12 picks)
2. Historical `v11_realistic_transactions.csv` sim trades (56 buys Jun 2025 - May 2026, treated as virtual picks)

**Initial snapshot:**

| Window | n | Alpha | Status | Note |
|---|---|---|---|---|
| Overall | 68 | -0.04pp | 🟡 YELLOW | T2_MID drag |
| Rolling 30 (recent) | 30 | **+0.59pp p=0.04** | **🟢 GREEN** | rule currently working |
| T1_TOP only | 39 | **+0.40pp** | healthy | ATC works for liquid names |
| T2_MID | 17 | **-1.23pp** | ⚠ | T1115 morning vol noisy |
| T3_LIQUID | 12 | +0.22pp | OK | smaller positions absorb |

**Key insight from initial backfill**: T2_MID tickers suffer from T1115 morning-bar volatility (worst: OIL 2026-02-03 -7.65pp alpha — 11:15 was 7.65% above open after sharp morning rally). The Phase 4b NAV sim aggregate of +1.75pp washed out this tier-specific tail risk over a 2.5y window. The shadow tracker exposes it on the actual 11-month subset.

**Open question for future refinement**: should the non-TOP rule switch from "T1115 market" to "stagger across morning bars" or "wait until VWAP"? Decision deferred — current rolling 30 is GREEN, no immediate action.

## What "rule breakage" would look like

The tracker will flag RED if:
- Mean of last 30 entries' alpha drops below 0
- AND the negative direction has statistical significance (p < 0.10 one-tail)

Example breakage scenarios:
- Vietnamese market microstructure changes (e.g., HOSE introduces continuous-call auction, killing ATO premium)
- Regime shift to deep bear: per Phase 3, morning slots failed in 2026 BEAR; if non-TOP T1115 rule starts losing AND it's a regime issue, expect T2_MID to go more negative first
- Broker behavior change (more retail MOO orders → more spike → MORE alpha; or vice versa)

**Response to RED**: revert the BUY-side rule in `recommend_holistic.py` to "buy at T+1 OPEN" (the legacy canonical). Sell rule unchanged.

## Files touched

- `layer3_v4_shadow.py` — main script (524 lines)
- `layer3_v4_shadow_run.bat` — Task Scheduler wrapper
- `data/layer3_v4_shadow_log.csv` — accumulating entry log
- `data/layer3_v4_shadow_report.md` — latest report snapshot
- `data/layer3_v4_shadow_cron.log` — append-only run history
- `MEMORY.md` — index entry

## Maintenance

- Daily 15:30 task runs automatically
- Review report weekly (manual) or set up Telegram integration
- If RED fires: investigate via `report` output to see which tier/period drives the breakage
- Re-backfill (`backfill --fetch-missing`) if intraday cache becomes stale; vnstock provides ~3-year window
- Update `intraday_full.pkl` periodically with `layer3_fetch_intraday_expand.py` to maintain coverage
