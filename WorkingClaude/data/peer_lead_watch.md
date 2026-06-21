# Peer-lead margin watch — BMP→NTP (PVC pipe duopoly) — baseline 2026-05-31

The peer-lead overlay is INFO-ONLY (GPM-corr test: contemporaneous ΔGPM only +0.09, but
lead-lag BMP→NTP +0.33 at 1-quarter lag). This watch tests whether the 1-quarter-lag
contagion is actually operative — to be revisited each quarter, then update the overlay.

## Baseline (gross margin %, GPM_P0)
| quarter | BMP_GPM | NTP_GPM |
|---------|--------:|--------:|
| 2024Q3 | 43.1 | 28.5 |
| 2024Q4 | 42.9 | 32.8 |
| 2025Q1 | 42.7 | 28.2 |
| 2025Q2 | 46.7 | 32.0 |
| 2025Q3 | 47.9 | 31.0 |
| 2025Q4 | 47.0 | 31.8 |
| **2026Q1** | **47.2** (peak, pctile 0.98, 3rd qtr at peak) | **31.3** (stable, mid-cycle) |

## Hypothesis (falsifiable)
BMP has held PEAK margin (~47%, GPM pctile 0.98) for 3 consecutive quarters. If the shared-PVC-input
contagion is real (the lead-lag +0.33 thesis), NTP's margin should COMPRESS over 2026Q2–Q3 as the
same input-cost cycle (PVC/oil) flows through. As of 2026Q1, NTP is NOT yet rolling over (flat ~31%).

## What to check (next earnings)
- After **2026Q2** (~Aug 2026) and **2026Q3** (~Nov 2026) reports: did NTP GPM fall from ~31%?
- **CONFIRM** (NTP compresses while BMP stays high/rolls) → peer-lead has predictive value → consider
  re-instating a small score penalty for same-product pairs.
- **FALSIFY** (NTP holds ~31% through 2026Q3 despite BMP at peak) → contagion not operative for this
  pair → drop the peer-lead flag entirely (margins are company-specific, as the corr test suggested).
- Re-run: `gpm_corr.py` with fresh data + this table.
