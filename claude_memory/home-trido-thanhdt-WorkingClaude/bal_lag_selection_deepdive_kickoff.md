---
name: bal-lag-selection-deepdive-kickoff
description: "Kickoff brief for the BAL/LAG stock-selection deep-dive (new session [REDACTED]12) — improve V2.3 selection from within the signal, not via overlays"
metadata: 
  node_type: memory
  type: project
  originSessionId: 169175c2-e4bb-43b4-990e-5ab581fd0038
---

User opened a NEW session ([REDACTED]12) to deep-dive **stock-selection criteria of BAL & LAG** (V2.3's two books), after concluding V2.3's grind weakness can't be fixed by defensive overlays.

**START HERE**: full brief at `workspace/bal_lag_selection_kickoff.md` (current selection logic + research angles + entry points + method discipline).

**One-line state**: V2.3 = production champion (26.2%/Sh1.66/DD−20.1). Weakness = 2025-08 style-rotation grind (−11.8%/294d, breadth 0.55 = selection issue not breadth). Book C / participation tilt / book-stops ALL tested & REJECTED → only lever left = the selection signal itself.

**BAL** = `signal_v11_sql.py` 100-pt momentum composite `ta` (RSI/MA-stack/volume/near-highs/MACD + minor PE/FSCORE/NP terms) → play_type by ta×state×fa_tier; buys only state 3/4/5; fa_tier used INVERTED. **LAG** = PEAD (NP_R≥15 & prior_n_good≥4 & pa_HL3≥5, T+5/25d, no stop); ⚠️ edge at 3rd percentile [[edge-health-monitor-amh1-2026]].

**First obvious analysis**: per-term IC attribution on BAL's 22-term `ta` by DT5G state (clean LEAD fwd-ret, not profit_*). Then style-rotation conditioning, LAG threshold re-fit. Validate on FAITHFUL 2-ledger engine (signal-level wins die at integration); momentum book RESISTS FA overlays ([[fa-layer-ic-audit-2026]]). See [[v4-faithful-reproduction-2026]] for V2.3 architecture, [[book-c-value-design-2026]] for the dropped value work.
