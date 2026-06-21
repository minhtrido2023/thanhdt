---
name: deposit_hurdle_neutral_only_2026
description: "Deposit-rate Fed-model hurdle for 8L value v3 — works in NEUTRAL only, NOT bear/crisis"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb305f6-9ad2-4e2f-9dfd-b054819e2145
---

8L valuation v3 (L1), deposit-rate lens. User idea: 1/PE must clear deposit + risk-premium to deserve a BUY; apply state-conditionally, hoped "most effective in BEAR/CRISIS." **Validated [REDACTED]19 on `data/value_panel_2014.csv` + real DT5G states → INTUITION INVERTED.**

**Data:** `deposit_rate_vn.py` = Big-4 12M deposit monthly proxy (DEPOSIT_EVENTS step series). SHAPE from TradingEconomics avg-lending chart 1999-2023 (user-provided: 2011 peak ~17%, 2014 8.7, 2015-17 ~7, 2022-23 spike, 2023 9.2); LEVELS pinned to Big-4 web anchors (spread lending−deposit ≈2% for Big-4, narrower than the 3-3.5% SME rule, widens in tight years). Annual: 2014 6.7 / 2015-16 5.5 / 2022-23 ~5.9-6.4 (intra-yr hits 7.5) / 2024 4.8 / 2026-06 6.8 (BIDV current). ⚠️PROXY — refine 2022-H2 spike if clean series found.

**Finding (`deposit_hurdle_validate.py`):** per-stock hurdle = `100/PE − deposit ≥ X`. Forward-2M edge (PASS−FAIL) of cheapest-EY-tercile candidates by state:
- **CRISIS/BEAR: near-INACTIVE** — pass% 96-98%, almost nothing to demote. In a crash PEs collapse → 1/PE huge → cheap names trivially clear any hurdle. So the cash-yield bar CANNOT be the crisis protector (capit sleeve + quality/timing do that). BEAR FAIL-bucket n=10-19 = noise.
- **NEUTRAL: clean +1.2 to +1.5pp edge** (X=2..4) — the Fed-model discipline works in normal markets.
- BULL/EXBULL: big edge but confounded with momentum; user says OFF there anyway.
- **Over-filter risk REAL** (user's caution confirmed): X=4 demotes 19% (2025)/25% (2026) of candidates in high-deposit years; X=3 tame (2-12%).

**DECISION (user, [REDACTED]19): GENTLE NEUTRAL-ONLY TILT** — fold 1/PE-vs-deposit as a SMALL secondary tilt active ONLY in DT5G NEUTRAL (state 3), off all other states, soft demote-not-kill, low weight. NOT a hard gate, NOT bear/crisis. Composite v3 carried by cross-sectional lenses ([[dcf_valuation_ic_test_2026]]: 1/PCF strongest+orthogonal, 1/PE solid, PS for consumer, pb_z linear-dead/golden-only). Lesson: a per-stock absolute hurdle can't bind in crisis (crashed stocks clear it trivially); the market-level Fed-model is a TIMING signal already covered by DT5G + Pillar-A rate momentum [[rate_signal_ic_validation_2026]].
