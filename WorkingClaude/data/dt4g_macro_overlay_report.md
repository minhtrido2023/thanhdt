# DT4G + Consolidated Macro Overlay — one layer (SBV money + US panic)

*Real BQ prices, 2000→2026, 1B VND. Base = recommended config (DT4G + #2 trend + #4 confirm10 + time-var bond-cash). Macro = SBV refi 6m-momentum + US VIX/SPX, fused into one cap/floor signal. Causal (US T-1, refi +5d).*

## Baseline vs +Macro (raw easing) vs +Macro (confirmed easing = refined (a))

| Period | Base CAGR\|Sh\|DD\|Cal\|NAV | +Macro raw | +Macro confirmed |
|---|---|---|---|
| FULL 2000-now | +19.17% | 1.25 | -34.8% | 0.55 | 92.71B | +19.78% | 1.33 | -34.7% | 0.57 | 105.69B | +20.13% | 1.37 | -34.7% | 0.58 | 113.99B |
| Pre-2014 | +23.67% | 1.42 | -34.8% | 0.68 | 17.33B | +24.67% | 1.58 | -34.7% | 0.71 | 19.30B | +25.11% | 1.61 | -34.7% | 0.72 | 20.23B |
| Modern 2014-now | +14.49% | 1.05 | -18.7% | 0.78 | 5.35B | +14.70% | 1.05 | -18.7% | 0.79 | 5.48B | +14.97% | 1.09 | -18.7% | 0.80 | 5.63B |
| 2007-08 GFC | +30.18% | 1.39 | -15.8% | 1.91 | 1.81B | +29.72% | 1.80 | -15.8% | 1.88 | 1.79B | +29.72% | 1.80 | -15.8% | 1.88 | 1.79B |
| 2011 inflation | +1.44% | 0.18 | -23.3% | 0.06 | 1.02B | +12.79% | 1.45 | -9.4% | 1.37 | 1.20B | +14.35% | 1.65 | -9.4% | 1.53 | 1.22B |
| COVID 2020 | +16.39% | 1.30 | -15.3% | 1.07 | 1.16B | +17.76% | 1.43 | -14.4% | 1.24 | 1.18B | +17.76% | 1.43 | -14.4% | 1.24 | 1.18B |
| 2022 hikes | -4.15% | -0.99 | -8.0% | -0.52 | 0.96B | -4.15% | -0.99 | -8.0% | -0.52 | 0.96B | -4.15% | -0.99 | -8.0% | -0.52 | 0.96B |

## Annual return: base vs +macro
| Year | Base | +Macro | Δ |
|---|---|---|---|
| 2000 | +67.5% | +67.5% | +0.0pp |
| 2001 | +4.2% | +2.3% | -1.9pp |
| 2002 | +6.1% | +7.5% | +1.3pp |
| 2003 | +8.7% | +9.9% | +1.1pp |
| 2004 | +31.5% | +31.5% | +0.0pp |
| 2005 | +25.5% | +25.5% | -0.0pp |
| 2006 | +97.1% | +97.1% | -0.0pp |
| 2007 | +56.5% | +56.5% | +0.0pp |
| 2008 | +13.1% | +12.2% | -0.9pp |
| 2009 | +15.7% | +15.7% | -0.0pp |
| 2010 | -1.6% | +0.2% | +1.9pp |
| 2011 | -13.3% | +5.2% | +18.5pp |
| 2012 | +27.5% | +20.3% | -7.2pp |
| 2013 | +19.1% | +19.6% | +0.5pp |
| 2014 | +14.3% | +16.9% | +2.7pp |
| 2015 | +1.4% | +1.4% | +0.0pp |
| 2016 | +17.3% | +17.3% | -0.0pp |
| 2017 | +40.4% | +40.4% | -0.0pp |
| 2018 | +8.2% | +8.2% | +0.0pp |
| 2019 | +7.7% | +7.7% | -0.0pp |
| 2020 | +16.3% | +17.7% | +1.4pp |
| 2021 | +32.7% | +32.7% | +0.0pp |
| 2022 | -4.1% | -4.1% | -0.0pp |
| 2023 | +3.0% | +4.8% | +1.8pp |
| 2024 | +7.4% | +7.4% | -0.0pp |
| 2025 | +34.2% | +34.2% | +0.0pp |
| 2026 | +5.1% | +5.1% | +0.0pp |

## Macro signal attribution (days fired by pillar)
| Trigger | Days |
|---|---|
| SBV-cut+US-calm | 679 |
| US-mild | 374 |
| US-crisis | 360 |
| SBV-tighten-mild | 305 |
| US-bear | 267 |
| SBV-tighten-extreme | 213 |
| SBV-tighten-strong | 99 |

## Design notes
- **One module, not three overlays.** SBV-policy and the domestic rate-momentum finding are the SAME driver (policy rate) → fused into Pillar A (no double-counting). US panic = Pillar B. DXY/FX deliberately omitted to avoid over-stacking (weakest, overlaps US).
- **Asymmetric**: stress → cap state ceiling (de-risk early); SBV-cut + US-calm → floor NEUTRAL (re-enter early). Recovery leg is the rate-driven fix for the V-recovery lag that breadth-thrust failed.
- Caps use the validated US 3-tier (VIX/SPX-DD) OR'd with SBV refi 6m-change tiers (mild 0.5/strong 1.5/extreme 3.0 pp).
