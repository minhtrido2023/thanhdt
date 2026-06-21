---
name: fitness_matrix_amh3_2026
description: Fitness Matrix (AMH
metadata: 
  node_type: memory
  type: project
  originSessionId: c20741c2-d11c-4052-813a-f3c503120558
---

**AMH proposal #3 — Fitness Matrix** (`fitness_matrix.py`, [REDACTED]09). Turns scattered regime-dependent findings into ONE grid [signal × DT5G market-state] for regime-conditional allocation. Each month → modal DT5G state at formation; per (signal×state) compute mean fwd-3M IC + long/short quintile spread (oriented + = profitable) + t-stat + hit. Panel 2014-26 (147 months) from `data/edge_panel.csv` + `data/dt5g_vnindex.csv`. Outputs `data/fitness_matrix_{ic,spread}.csv`, `fitness_matrix.png`. Months/state: CRISIS 24, BEAR 12, NEUTRAL 88, BULL 19, EXBULL 4 (dropped, <6).

**Four environment laws (L/S spread %, validates memory):**
- **VALUE (PB/PE) = all-weather, strongest at extremes**: PB CRISIS +6.5 / BEAR +8.3 / NEUTRAL +5.0 / **BULL +14.2**; PE CRISIS +7.2 / BULL +8.7. The backbone edge every state.
- **QUALITY (ROIC5Y/ROE_Min5Y) = CRISIS-ONLY**: ROIC +0.108\* CRISIS but ~0 elsewhere; ROE +0.118\* CRISIS, **NEGATIVE in BULL** (ROIC −4.4, ROE −3.3). Exactly validates "CRISIS = only regime quality beats junk" + "FA edge ZERO in BULL" ([[fa_layer_ic_audit_2026]]). Quality = flight-to-quality insurance, only pays when it matters.
- **MOMENTUM (mom_200/D_RSI) = good-times only, INVERTS in CRISIS**: NEUTRAL +5.8/+6.0, BULL +5.0/+6.9, but CRISIS −2.8/0 (mean-reversion). The CRISIS inversion IS the capitulation-buy edge ([[dt5g_8l_crisis_capitulation_2026]], buy oversold = anti-momentum).
- **Flow/Position** track momentum (+ in NEUTRAL/BULL, − in CRISIS/BEAR).

**HEADLINE — the #1×#3 synthesis (this is where AMH changes allocation):**
Fitness Matrix = the THROUGH-CYCLE PRIOR ("what usually fits this state"). Edge Health Monitor (#1) = the LIVE OVERRIDE ("what's actually working now"). They are two layers, not rivals. Current state = NEUTRAL → Matrix ranks momentum top (mom_200 t4.4, D_RSI t5.3) + value; BUT #1 shows momentum FLIPPED last-12M → **down-weight momentum NOW, lean value (still healthy per #1)**. Without #1 you'd trust the Matrix and get hit; without #3 you wouldn't know NEUTRAL should normally carry momentum. = Lo's adaptive mechanism: cyclical map as base, live signal adjusts.

**Allocation playbook per state**: CRISIS→quality+value+capitulation-meanrev, momentum OFF. BEAR→pure value, avoid flow/mom. NEUTRAL→momentum+value (when #1 confirms mom alive), quality dormant. BULL→value(huge)+momentum, cut quality.

**Caveat**: in-sample full-history PRIOR, NOT walk-forward — use as a conditioning MAP combined with live #1, not a standalone alpha (memory: "state in-sample optimistic"). BEAR thin (12mo), EXBULL dropped. Decision metrics note (user Q): Sharpe+Calmar = primary deciding pair (least redundant: everyday-vol vs worst-case); Sortino = reported + asymmetry flag (high Sortino/Sharpe ratio = favorable skew) but noisy in small samples, never override. Fitness cells use IC/spread/hit (cross-sectional), not NAV-path ratios.

AMH roadmap: #1 Edge Health ✅ → #2 Vol-target ✅(rejected) → **#3 Fitness Matrix ✅** → #4 Ecology Dashboard → #5 Biodiversity test.
