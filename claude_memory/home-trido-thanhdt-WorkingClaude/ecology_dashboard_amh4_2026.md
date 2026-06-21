---
name: ecology_dashboard_amh4_2026
description: Ecology Dashboard (AMH
metadata: 
  node_type: memory
  type: project
  originSessionId: c20741c2-d11c-4052-813a-f3c503120558
---

**AMH proposal #4 — Ecology Dashboard** (`ecology_dashboard.py`, [REDACTED]09). Gauges market ecology (Lo: crowds wise when diverse, mad when uniform) on 3 daily causal axes over liquid `ticker_prune`: **A Opportunity** = cross-sectional return dispersion pctile (wide=stock-picker's market, narrow=crowded/macro); **B Uniformity** = breadth extremity |breadth−0.5|×2 + low-dispersion; **C Mood** = +euphoria/−panic from z(breadth)+z(overbought−oversold)+z(pb_z_median); + **Divergence** flag (index up 60d while breadth<50%). Inputs `data/ecology_panel.csv` (BQ daily aggregate) + `data/dt5g_vnindex.csv`. Outputs `data/ecology_dashboard.csv`, `ecology_dashboard.png`, `data/ecology_now.md`.

**KEY FINDING — refutes the naive "fade the mad crowd" reading.** Forward-VNINDEX-by-mood-decile is **PROCYCLICAL (momentum), NOT contrarian** at the market/60d level: euphoria decile-9 fwd60 **+8.2%/82% win** >> panic decile-0 +3.9%/64%; spread (panic−euphoria) = **−4.3pp**. Fading the crowd is WRONG (you'd short the whole bull). The contrarian/capitulation kick lives ONLY in the extreme-tail decile-0 (+3.9% > mild-pessimism deciles 1-3 ~0-2%) AND needs the DT5G-CRISIS+washout conditioning from [[dt5g_8l_crisis_capitulation_2026]] / [[fitness_matrix_amh3_2026]]. → **Ecology Dashboard's role = a FRAGILITY gauge, not a timing/fade trigger**: high madness + divergence = market extended/fragile → tighten risk discipline, trust the DT5G de-risk gate, cut leverage, demand quality — NOT "sell now". Read THROUGH #3: same mood means different things per state (panic in CRISIS = capitulation opportunity; panic in NEUTRAL = just persistent weakness).

**Current ([REDACTED]08) = textbook late-cycle narrow-breadth divergence**: VNINDEX near highs (+60d) but breadth only **29% >MA200** / 24% >MA50; Opportunity 26th pctile (CROWDED/macro, narrow VIC-led leadership); Mood −1.50 (8th pctile, broad-market panic) while index pb_z +0.11 (slightly expensive). Divergence flag FIRES — fragile megacap-supported rally; broad market already in a bear. Consistent with V4/V5 momentum-bleed (#1 momentum FLIP) and the 8L-vs-VN30 grind. Forward: either breadth catches up (healthy) or index converges down (top).

AMH roadmap: #1 Edge Health ✅ → #2 Vol-target ✅(rejected) → #3 Fitness Matrix ✅ → **#4 Ecology Dashboard ✅** → #5 Biodiversity test (orthogonality screen for new strategies).
