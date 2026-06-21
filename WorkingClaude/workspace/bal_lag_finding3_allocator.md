# Finding #3 — State-conditional LAG/BAL capital allocator (validated, two-book)
**2026-06-11. Follow-up to user Q: "LAG hiệu quả hơn momentum — tăng tỉ trọng LAG theo state?"**

## Premise checks (all confirmed)
- **LAG >> BAL standalone** (each 25B): FULL BAL 19.0%/Sh1.20 vs LAG 29.9%/Sh1.57; 2025+ BAL 2.6% vs LAG 25.0%.
- **LAG alpha is REAL, not ETF-beta**: on PEAD-live days LAG earns +42%/yr (full)/+28% (2025); ETF-park-only days −5.8%/yr. So it didn't ride the VIC index rally.
- **LAG scales well (mild capacity decay)**: 25B FULL 28.1% → 40B 25.7% → 60B 25.3% → 120B 22.6% (deployed 39.5%→33%). Far better than capit (which collapsed). LAG can absorb more capital.

## The decisive nuance — LAG by DT5G state (annualized / Sharpe, full history)
| State | BAL | LAG | |
|---|---|---|---|
| CRISIS(1) | 8.1% / 0.92 | 21.2% / 0.79 | ~tie |
| **BEAR(2)** | **6.0% / 1.59** | **−14.4% / −0.97** | **BAL — LAG LOSES money** |
| NEUTRAL(3) | 22.3% / 1.39 | 31.2% / 1.69 | LAG |
| BULL(4) | 48% / 1.55 | 87% / 4.01 | LAG |
| EXBULL(5) | −12% / −0.39 | 114% / 3.22 | LAG |
Corr BAL/LAG daily = 0.48 (diversifying, not redundant). PEAD fails in BEAR (good earnings sold) → must drop LAG there.

## Faithful one-wallet test (per-name weight tilt; 50B; mom+LAG+capit+park)
- A base (flat LAG .05): FULL 21.85%/−24.1/Sh1.29; 2025+ 13.67%/Sh0.76. (Base's worst DD = the 2025 grind itself.)
- B aggressive (good=.08, BEAR=0): 2025+ +5.7pp but FULL MaxDD −24.1→−26.6 (amplified the **2020 COVID crash** −12.6→−20.0; LAG has no stop, big longs rode it down).
- **F gentle (good=.065, BEAR=0): STRICTLY DOMINATES — FULL 22.94% (+1.1pp), DD −23.5 (better), Sh 1.35; 2025+ 19.65% (+6pp), DD −20.7, Sh 0.99.** Magnitude matters more than which good-state. Aggressive overshoots into crash tail-risk; gentle stays under that threshold.

## Two-book (PRODUCTION architecture) capital allocator — book weights by state, rebalance at state transition, ~6% LAG capacity haircut applied
| Scheme (BEAR always LAG 0) | FULL | DD | Sh | Cal | 2025+ |
|---|---|---|---|---|---|
| base 50/50 | 24.81% | −20.5 | 1.62 | 1.21 | 13.68% |
| USER (NEU 65, others 50) | 25.28% | −19.1 | 1.70 | 1.32 | 13.45% |
| **LAG 65 ALL good-states** | **26.12%** | **−18.6** | **1.79** | **1.40** | **16.11%** |
| moderate (NEU 60) | 25.39% | −19.2 | 1.73 | 1.32 | 14.17% |

**Recommended scheme** (w_LAG by state): CRISIS 0.50 · **BEAR 0.00** · NEUTRAL 0.65 · BULL 0.65 · EXBULL 0.65.
→ FULL 24.8→26.1% (+1.3pp), MaxDD −20.5→−18.6, Sharpe 1.62→1.79, Calmar 1.21→1.40; 2025+ 13.7→16.1%. Apply 65/35 across ALL good states (not NEUTRAL-only — captures LAG's BULL/EXBULL edge); user's NEUTRAL-only version barely moved 2025+.

## Caveats (deploy moderately)
1. **Edge-cycle**: in LAG's weak patch (2022-2024) the tilt LAGS base on return (12.9 vs 13.5%, better DD only). LAG is at **percentile-3 NOW** ([[edge-health-monitor-amh1-2026]]) → the tilt's gains concentrate in strong-LAG years (2020-21, 2024-25). **Start moderate (LAG 58-60% good-states) and ramp to 65% as `lag_edge_health.csv` recovers (12M-mean > +4-5%).**
2. Two-book numbers carry ~6% LAG capacity haircut (conservative); one-wallet base spec (21.85%) < two-book champion (25.77%) — use the DELTAS, not absolutes, across architectures.
3. This is the [[sleeve-budget-allocator-2026]] concept made concrete for the BAL/LAG split.
4. Tilting hard amplifies fast-crash tail-risk (LAG no-stop); BEAR=0 + gentle sizing is the guardrail.

Scripts: `workspace/pt_onewallet_allocator.py` (one-wallet arms A/B/E/F), two-book allocator inline (book-weight rebalance over `data/pt_v22_{bal,lag}_v21_cap.csv`).
