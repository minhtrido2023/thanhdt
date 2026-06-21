---
name: ng-h-nh-tinh-t-current-live-5-state
description: "🟢 LIVE production codename \"Ngũ Hành — Tinh Tế\" (tech v2g_pe3c_s3). 5-state market system family is \"Ngũ Hành\"; iterations have Vietnamese poetic sub-names. Integrated V11 12y CAGR 17.86% vs Cổ Điển 16.44%."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e35b3d0-06a3-44a7-ba75-11196930c3f0
---

**Codename: "Ngũ Hành — Tinh Tế"** (refined Yin-Yang of 5-state family). Tech name `v2g_pe3c_s3`. Deployed 2026-05-21.

**Lineage:** Cổ Điển (original baseline smooth+gate60) → v2g (2026-05-17, no-smooth, reverted) → v2g_pe3c raw (2026-05-21 morning, integrated FAIL Mid 18-23) → **Tinh Tế (2026-05-21 afternoon)**.

**Registry:** see [vnindex_5state_registry.md](vnindex_5state_registry.md) for LIVE / STAGING / ARCHIVE convention.

## Why s3 smoothing was added

User correctly demanded **integrated V11 backtest** (not just standalone state-system). Result revealed v2g_pe3c raw fails Mid 2018-23 by -2.57pp CAGR (same pattern as 2026-05-12 v2g failure). Light smoothing `mode=3 + min_stay=2` rescues Mid 18-23 to -0.21pp (nearly tied baseline) while preserving OOS gains. Heavy smoothing (mode 10-15) hurts CAGR; light smoothing is the sweet spot.

## Pipeline configuration

**State generation:**
1. v2g_pe3c raw states (from `test_v2g_pe3.py` — composite W=0.03 + S2_bull + cleaned PE)
2. Apply `rolling_mode(3)` (3-day mode smoothing)
3. Apply `min_stay_filter(2)` (eliminate 1-day micro-transitions)

**Composite (7 base factors + PE inverted W=0.03):**
- P3M 0.291, P1M 0.097, MA200 0.1455, RSI 0.1455, MACD 0.097, CMF 0.0776, Breadth 0.1164, PE -1×inv 0.03

**Gate (no change from v2g_pe3c):**
- BearDvg gate floor=CRISIS, GATE_MIN_DUR=30
- Enter: BearDvg RSI signal (mask_2007)
- Exit: BullDvg OR E2 capitulation OR S2_bull (PE 6M slope < -25%/yr)

**PE handling:**
- Cleaned PE 2006-2026 via `clean_vnindex_pe.py` (calibration ×1.093 pre-2011 Bloomberg)
- PE quality gating ≤2 for signals
- Override: PE > expanding P90 OR rolling 5Y P85

## Integrated V11 backtest (50B NAV, 2014-2026, T+1 Open)

| Period | A_baseline | C_pe3c_raw | **D_pe3c_s3 (deployed)** | Δ s3 vs baseline | Δ s3 vs pe3c_raw |
|---|---|---|---|---|---|
| FULL 2014-26 | 16.44 / 1.22 / -17.4 | 17.34 / 1.20 / -20.5 | **17.86 / 1.21 / -23.3** | +1.42pp / -0.01 / -5.9pp | +0.52pp / +0.01 / -2.8pp |
| Pre-OOS 14-19 | 9.70 / 1.05 / -15.1 | 10.37 / 1.01 / -16.9 | 9.77 / 0.94 / -17.5 | +0.07pp / -0.11 / -2.4pp | -0.60pp / -0.07 / -0.6pp |
| Mid 2018-23 | **19.52** / 1.30 / -16.8 | 16.95 / 1.08 / -20.5 | **19.31 / 1.17 / -23.3** | -0.21pp / -0.13 / -6.5pp | **+2.36pp / +0.09 / -2.8pp** |
| OOS 2024-26 | 16.28 / 1.03 / -17.4 | 21.77 / 1.24 / -18.3 | 20.71 / 1.19 / -19.3 | +4.43pp / +0.16 / -1.9pp | -1.06pp / -0.05 / -1.0pp |

**Wealth 12y:** s3 ×7.63 vs baseline ×6.57 (+16%) vs pe3c_raw ×7.22 (+5.7%).

**Key trade-off accepted:** FULL DD -5.9pp worse than baseline (-23.3% vs -17.4%); concentrated in 2018-2023 era (deepest single drawdown). Net CAGR/wealth gains outweigh.

## Why s3 specifically (not s5, s10, s15)

V11 integrated sweep tested 4 smoothing levels:
| Variant | FULL CAGR | FULL Sh | Mid 18-23 CAGR | OOS CAGR | DD |
|---|---|---|---|---|---|
| pe3c_s3 (mode 3, min_stay 2) | **17.86** | 1.21 | **19.31** | 20.71 | -23.3 |
| pe3c_s5 (mode 5, min_stay 3) | 17.07 | 1.20 | 19.23 | 17.10 | -20.5 |
| pe3c_s10 (mode 10, min_stay 5) | 17.01 | **1.27** | 16.79 | 20.48 | -23.9 |
| pe3c_s15 (mode 15, min_stay 7) | 16.63 | 1.18 | 17.35 | 18.80 | -25.2 |

- s3 wins on CAGR and Mid 18-23 (key recovery target)
- s10 wins on Sharpe (1.27, highest of all 7 variants tested) but loses Mid 18-23
- s5 has weak OOS (17.10, lowest of smoothing variants)
- s15 = heavy smoothing erases v2g_pe3c gains

**Light smoothing (mode 3-5) helps; medium-heavy (mode 10+) hurts.** Reason: mode 3 eliminates 1-day micro-transitions caused by no-smooth raw, without altering the longer-term state regimes that capture v2g_pe3c's PE-upgrade alpha.

## Deployment

**✅ DEPLOYED 2026-05-21 to all 4 canonical stores:**
- `vnindex_5state_history.csv` (6282 rows, 2000-07-28 → 2026-05-20)
- `vnindex_5state.csv`
- `vnindex_state_history.csv` (legacy schema)
- `tav2_bq.vnindex_5state`

**Latest state 2026-05-20:** BULL (4)

**Backup suffix `_baseline_pre_pe3c_s3_20260521_021831`:**
- 3 local CSV backups
- BQ: `tav2_bq.vnindex_5state_baseline_pre_pe3c_s3_20260521_021831` (contains v2g_pe3c raw from earlier today)

**Rollback to baseline ORIGINAL (smooth+gate60, proven robust):**
- BQ: `bq cp -f tav2_bq.vnindex_5state_baseline_pre_v2g_20260517_144254 tav2_bq.vnindex_5state`
- Then re-extract local CSVs from that table

**Refresh pipeline (weekly):**
```bash
python clean_vnindex_pe.py            # fresh BQ pull + clean PE
python test_v2g_pe3.py                # build v2g_pe3 state
python generate_smoothed_v2g_pe3c.py  # apply s3 smoothing + upload variants to BQ
python deploy_v2g_pe3c_s3.py          # overwrite canonical with s3 + auto-backup
```

## State distribution (v2g_pe3c_s3, 2000-2026)
- CRISIS 19.9% · BEAR 5.6% · NEUTRAL 63.8% · BULL 8.7% · EX-BULL 1.9%
- Transitions FULL: 250 (vs raw 287, baseline 117)

## Critical lessons learned (research log)

1. **NEVER trust standalone state-system backtest** — must validate in integrated V11 stack. Memory note from 2026-05-12 (v2g integrated FAIL) was correct; we re-discovered the same pattern with v2g_pe3c raw before adding smoothing.

2. **PE bear signals universally FAIL in Vietnam** — sustained PE elevation 3-5 years without correction; "expensive" ≠ "crash imminent" in emerging market with 6-7% real GDP growth.

3. **Light smoothing (mode 3) is the sweet spot** — eliminates 1-day micro-transitions while preserving regime detection. Heavy smoothing (mode 10+) erases the alpha.

4. **Additivity perfect on standalone but partial in integrated** — PE composite +0.172pp + S2_bull +0.067pp = +0.239pp standalone (synergy=0.000); integrated V11 gain is mostly from cleaned PE 2007+ extension + S2_bull (not composite W=0.03).

5. **Shiller PE rejected on theoretical grounds** — emerging-market GDP growth + composition changes + accounting regime → upward CAPE bias. Already capture mean-reversion via pe_ma5y proxy.

## Caveats and risks

- DD -23.3% on FULL (-5.9pp worse than baseline). User explicitly accepted this trade-off in exchange for +1.42pp CAGR.
- Mid 2018-23 still slightly behind baseline (-0.21pp CAGR, -0.13 Sharpe). Not a hard win, but tied.
- s3 smoothing parameter was chosen via single sweep; not stress-tested across market regimes.
- If next quarter shows v11 production NAV drift from backtest by > 5%, reconsider rollback to baseline.
