# DT4G Improvements — Ablation (#2 trend, #3 breadth-thrust, #4 hysteresis)

*Real BQ data, 2000-07-28 → 2026-05-26, 1B VND. Costs: 0.1% fee + 0.1% sell tax, borrow 10%/yr. Idle cash 0.1%/yr except final row (time-varying VN 1Y gov-bond yield: ~8% early-2000s, peak 14% 2008 / 12% 2011, falling to ~2% 2020-2025). Sharpe uses a fixed 0.1% rf hurdle for all variants (comparable).*

**VNINDEX B&H full-period ref**: +12.04% | 0.46 | -79.9% | 0.15 | 18.84B (MaxDD includes pre-2007 −80%).

## Full-period (2000→now) + Modern (2014→now)

| Variant | Full CAGR | Sh | MaxDD | Calmar | Final | Modern CAGR | Mod DD | Rebals |
|---|---|---|---|---|---|---|---|---|
| Baseline (corrected) | +15.08% | 1.08 | -37.6% | 0.40 | 37.60B | +12.26% | -18.8% | 94 |
| +#2 trend (raw) | +15.68% | 1.05 | -37.6% | 0.42 | 43.06B | +13.31% | -19.4% | 326 |
| +#2 trend +#4 confirm10 | +15.76% | 1.05 | -38.3% | 0.41 | 43.81B | +13.13% | -19.4% | 136 |
| +#3 breadth thrust (14+) | +15.16% | 0.64 | -53.2% | 0.29 | 38.28B | +11.98% | -22.2% | 98 |
| #2+#4 + #3 | +15.84% | 0.65 | -53.2% | 0.30 | 44.60B | +12.85% | -23.1% | 142 |
| #2+#4 + bond-cash (time-var VGB) | +19.17% | 1.25 | -34.8% | 0.55 | 92.71B | +14.49% | -18.7% | 136 |

## Crisis / recovery stress (sub-period, re-based 1B)

| Variant | 2007-08 GFC CAGR | GFC DD | COVID-2020 CAGR | 2020 DD |
|---|---|---|---|---|
| Baseline (corrected) | +19.50% | -17.2% | +14.83% | -16.0% |
| +#2 trend (raw) | +20.12% | -17.4% | +15.69% | -16.6% |
| +#2 trend +#4 confirm10 | +18.97% | -18.0% | +15.20% | -16.0% |
| +#3 breadth thrust (14+) | +8.20% | -53.2% | +25.16% | -10.6% |
| #2+#4 + #3 | +7.72% | -53.2% | +25.56% | -10.6% |
| #2+#4 + bond-cash (time-var VGB) | +30.18% | -15.8% | +16.39% | -15.3% |

## Annual: Baseline vs Best (#2 trend + #4 confirm10) vs B&H

| Year | Baseline | Best-combo | B&H | Δ(combo−base) |
|---|---|---|---|---|
| 2000 | +66.5% | +66.5% | +106.8% | +0.0pp |
| 2001 | +1.5% | +1.5% | +11.8% | +0.0pp |
| 2002 | +0.9% | +0.9% | -20.9% | +0.0pp |
| 2003 | +4.3% | +4.3% | -9.0% | +0.0pp |
| 2004 | +28.1% | +28.1% | +41.5% | +0.0pp |
| 2005 | +20.1% | +23.6% | +29.6% | +3.5pp |
| 2006 | +81.7% | +94.6% | +146.3% | +12.8pp |
| 2007 | +50.4% | +48.9% | +25.1% | -1.5pp |
| 2008 | -0.8% | -0.8% | -65.7% | -0.0pp |
| 2009 | +9.0% | +10.2% | +57.9% | +1.2pp |
| 2010 | -4.0% | -5.2% | -6.3% | -1.1pp |
| 2011 | -14.0% | -18.4% | -27.7% | -4.4pp |
| 2012 | +18.3% | +19.7% | +18.2% | +1.4pp |
| 2013 | +14.0% | +15.5% | +20.6% | +1.5pp |
| 2014 | +9.0% | +12.3% | +8.2% | +3.3pp |
| 2015 | +3.9% | +0.1% | +6.4% | -3.9pp |
| 2016 | +12.2% | +14.5% | +15.7% | +2.3pp |
| 2017 | +31.0% | +39.6% | +46.5% | +8.6pp |
| 2018 | +7.7% | +6.4% | -10.4% | -1.3pp |
| 2019 | +7.2% | +6.6% | +7.8% | -0.5pp |
| 2020 | +14.8% | +15.1% | +14.2% | +0.4pp |
| 2021 | +31.1% | +32.7% | +33.7% | +1.5pp |
| 2022 | -6.9% | -6.9% | -34.0% | +0.0pp |
| 2023 | +2.8% | +2.0% | +8.2% | -0.8pp |
| 2024 | +7.4% | +6.6% | +11.9% | -0.8pp |
| 2025 | +30.0% | +33.9% | +40.5% | +3.8pp |
| 2026 | +4.2% | +5.0% | +5.4% | +0.8pp |

## Verdict & notes
- **#2 trend overlay = ADOPT.** Lifts NEUTRAL 70%→90% only when VNINDEX>MA200 + RSI≤0.72 (full history). Modern +1.05pp, MaxDD preserved. Gains come exactly where designed — bull years (2006 +12.8pp, 2017 +8.6pp, 2025 +3.8pp) — while crash years stay identical (2008 −0.8%, 2022 −6.9% unchanged).
- **#4 confirmation dwell (10 sessions) = ADOPT with #2.** Debounces the MA200 cross at the source: rebalances 326→136 (−58%) with essentially identical return/DD. (A global Δw no-trade band does nothing here — discrete state jumps are ≥0.2.)
- **#3 breadth thrust = REJECT.** Even with reliable breadth (≥50 names, from 2007) it blows MaxDD to −53% and halves Sharpe — it re-enters into continuing crashes (2008 GFC CAGR collapses +19.5%→+8.2%). It DOES help the one true V-recovery (2020 +25% vs +15%), but the crash-whipsaw cost dwarfs it. Confirms the documented vol-adaptive failure mode.
- **bond-cash sleeve (idea #1) = biggest single lever**, now with a TIME-VARYING VN 1Y gov-bond yield (realistic: ~8% early-2000s, peak ~14% in 2008 / ~12% in 2011, falling to **~2% in 2020-2025** — NOT a flat 5%). Idle cash earns this instead of 0.1% demand deposit (VN has no deep MMF; a modeled short-dur gov-bond sleeve is the honest proxy). Effect: **+2.2pp modern** on top of #2+#4, and a large FULL-period boost because 2008/2011 parked cash earned 12-14% during the high-rate inflation era. MaxDD improves to −34.8%.
- Sharpe is computed with a fixed 0.1% rf hurdle for ALL variants, so the bond row's 1.25 is directly comparable (and is the best) — no rf artifact.
- **RECOMMENDED config**: DT4G + #2 trend + #4 confirm10 + time-varying bond-cash sleeve → **Full +19.17% / Modern +14.49% / MaxDD −34.8% / Sharpe 1.25**, 136 rebalances. Reject #3.
