# Paper-trade roster review — PRELIMINARY (decision date 2026-06-30)  (as of 2026-06-05)

## Time-boxed sleeves (decision 2026-06-30)
- #6 vol-hedge: insufficient data.
- #7 F-sleeve: insufficient data.
- #10 DT4-vs-TQ34b A/B: report says →
      # A/B DT4 vs TQ34b foundation — window 2026-01-01 -> 2026-06-08  (DECISION 2026-05-29)
      
      *Live-faithful: fresh SIGNAL_V11 (state5 per foundation), real E1VFVN30, t1_open, prod-spec. 50B/system.*
      
      | System | DT4 TotRet | TQ34b TotRet | ΔTot | DT4 Sh | TQ Sh | DT4 DD | TQ DD | lead |
      |---|---:|---:|---:|---:|---:|---:|---:|:--:|
      VERDICT: production foundation is already DT5G (= DT4-gate + macro) per CLAUDE.md → A/B can RESOLVE/RETIRE.

## V6-v2 absorption check
- merge: V6-v2 forward 46 sessions, states seen [np.int64(3)] (SINGLE regime ✗ (need a drawdown window)), V6−V5 spread -1.57pp.
      → NOT ready — keep capit-shadow standalone (still feeds capit-edge); re-check after a non-NEUTRAL window.

## Proposed bat cleanup (apply manually after review)
- If #6 DROP → comment papertrade_daily.bat step [5b] vol_spike_hedge_pt.py
- If #7 DROP → comment step [5c] f_sleeve_pt.py
- If #10 RESOLVED → comment step [7] pt_dt4_vs_tq34b_ab.py (decision logged)
- If V6-v2 MULTI-regime+ahead → fold step [9] pt_capitulation_shadow into V6-v2; keep [14] pt_sleeve_allocator as the unified successor
- Always KEEP core books [1-4b], monitors [11-13], ORB [5d] (orthogonal edge).