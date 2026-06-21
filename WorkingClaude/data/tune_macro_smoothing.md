# Macro Overlay — transition smoothing (cap confirmation dwell)

*Pure-index recommended config. DEFENSIVE cap now needs K sessions to commit (causal, debounces tighten+release). Target: transitions ~ DT4-only (smooth) while keeping crisis alpha.*

| Variant | Trans (full) | Apr-2025 | Full CAGR | Modern | 2008 | 2011 (DD) | 2020 | 2022 |
|---|---|---|---|---|---|---|---|---|
| DT4-only (ref) | 93 | 0 | +19.17% | +14.49% | +30.18% | +1.44% (-23%) | +16.39% | -4.15% |
| macro cap_K=0 | 192 | 7 | +19.66% | +14.54% | +29.72% | +11.44% (-10%) | +20.71% | -2.15% |
| macro cap_K=3 | 124 | 1 | +19.90% | +15.27% | +29.72% | +11.16% (-10%) | +19.29% | -1.90% |
| macro cap_K=5 | 116 | 1 | +19.79% | +15.15% | +29.72% | +11.97% (-11%) | +17.31% | -1.23% |
| macro cap_K=7 | 112 | 0 | +19.90% | +15.03% | +29.72% | +12.39% (-12%) | +17.76% | -4.15% |
| macro cap_K=10 | 112 | 0 | +19.65% | +14.89% | +29.72% | +13.81% (-12%) | +15.09% | -4.15% |

*DT4-only is the smoothness reference. Pick the smallest K that brings Apr-2025 flicker to ~0-1 and total transitions near DT4 while preserving 2011/2022 crisis protection.*
