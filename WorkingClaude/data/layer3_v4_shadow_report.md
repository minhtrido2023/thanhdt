# Layer 3 v4 Shadow Tracker Report

*Generated: 2026-05-17 23:38*

## Status

| Window | Status | Detail |
|---|---|---|
| Overall (n=68) | **YELLOW** | mean=-0.038pp, p(neg)=0.441 |
| Rolling 30 (n=30) | **GREEN** | mean=+0.587pp, p=0.043, n=30 |

## Summary
- Total entries logged: **68**
- Date range: 2025-06-09 → 2026-05-08
- Mean alpha vs T+1 Open: **-0.038pp** (sd 2.109)
- ATC fill feasible: **58.8%** | T1115 fill feasible: **58.8%**
- Win rate (alpha > 0): **54.4%**

## By Liquidity Tier

| Tier | n | mean alpha pp | std |
|---|---|---|---|
| T1_TOP | 39 | +0.402 | 1.642 |
| T2_MID | 17 | -1.228 | 2.753 |
| T3_LIQUID | 12 | +0.219 | 1.956 |

## By Book

| Book | n | mean alpha pp | std |
|---|---|---|---|
| BAL | 11 | +0.007 | 2.728 |
| SIM | 56 | -0.074 | 2.006 |
| VN30 | 1 | +1.493 | nan |

## By Play Type

| Play Type | n | mean alpha pp | std |
|---|---|---|---|
| DEEP_VALUE_RECOVERY | 11 | -0.064 | 2.672 |
| RE_BACKLOG_BUY | 1 | +2.279 | nan |
| v11_sim | 56 | -0.074 | 2.006 |

## Recent 10 entries

| T+1 date | Ticker | Book | Tier | Rule | Alpha (pp) |
|---|---|---|---|---|---|
| 2026-02-03 | OIL | BAL | T2_MID | T1115_MKT_thin_liquidity | -7.647 |
| 2026-02-03 | NAF | BAL | T2_MID | T1115_MKT_thin_liquidity | +1.449 |
| 2026-02-03 | IDI | BAL | T3_LIQUID | T1115_MKT_thin_liquidity | +0.289 |
| 2026-02-03 | HHP | BAL | T3_LIQUID | T1115_MKT_thin_liquidity | +0.000 |
| 2026-02-03 | DXP | BAL | T3_LIQUID | T1115_MKT_thin_liquidity | +0.000 |
| 2026-02-03 | DVN | BAL | T3_LIQUID | T1115_MKT_thin_liquidity | -1.304 |
| 2026-02-03 | BID | BAL | T1_TOP | ATC_full | +1.097 |
| 2026-02-03 | MML | BAL | T3_LIQUID | T1115_MKT_thin_liquidity | +1.711 |
| 2026-04-10 | PAN | SIM | T2_MID | T1115_MKT_thin_liquidity | +1.534 |
| 2026-05-11 | VIC | BAL | T1_TOP | ATC_full | +2.279 |

## Decision rule
- **GREEN**: rolling 30 alpha >= +0.5pp AND p<0.10 → rule healthy, continue
- **YELLOW**: alpha 0 to +0.5pp or sample too small (n<20) → monitor
- **RED**: alpha < 0 with p<0.10 → **RULE BREAKAGE**, revert to T+1 Open canonical