# Margin Engine Rebuild — Scenario Spec

> Author: Taylor (quant). Started 2026-06-25. Driver: `pt_v23_audit_2014.py` → engine `simulate_holistic_nav.py:simulate()`.
> Principle (user, 2026-06-25): *"1 engine hoàn chỉnh phải có đầy đủ các kịch bản. Margin là nền tảng của giao dịch khi thị trường sợ hãi. Engine không kiểm soát được = rủi ro production."*
>
> **Discipline (binding):** every feature env-gated **OFF** → production run byte-identical until validated. Each piece must pass **self-check 0 VND** (per-session cash-flow identity) + **walk-forward IS(2014-19)/OOS(2020+)** before any LIVE change. LIVE change needs **user approval**.

## A. Control-audit — what the engine could NOT do (2026-06-25, code-grounded)

| # | Scenario | Before | Evidence |
|---|----------|--------|----------|
| 1 | Margin-call / force-deleverage on gross breach | **ABSENT** | `max_gross_exposure` used only at entry (buying-power cap, `simulate_holistic_nav.py:1016-1039`). No sell trigger references gross-cap. Sells fire on signal/stop/trail/state/evict/EOD only. |
| 2 | Live gross tracking during hold | **ABSENT** | gross never computed in session loop; no `gross` field in `nav_history` (record dict ~line 1221). |
| 3 | Fast-deploy levered vehicle (parking on margin) | **DISABLED by design** | line 314: "ETF parking never uses margin"; `target_etf = total_cash_pool×etf_frac` is cash-bounded. |
| 4 | Parking-on-margin cash accounting | **NON-RECONCILING** (≤241M/session) | self-documented `pt_v23_audit_2014.py:379` "parking-margin path double-charges interest on cash_etf"; routed around, not fixed. |
| 5 | Regime-driven deleverage | **ABSENT** | regime gates entry; no rule cuts gross when DT5G downgrades while levered. |

## B. Complete scenario matrix the rebuilt engine MUST handle

Gross exposure `G = (positions_mv + etf_mv) / NAV`. Cap params: `MGE` (soft target ceiling), `MGE_HARD` (force-sell trigger), `MGE_FLOOR` (deleverage target after a call).

| Scenario | Trigger | Engine action | Reconcile |
|----------|---------|---------------|-----------|
| **S0 Normal (G≤1)** | always | cash-bounded buys; idle cash earns deposit | already 0-VND ✓ |
| **S1 Levered entry** | bottom signal + `play_type∈margin_tiers` | buy beyond cash up to `(MGE-1)×NAV` borrow room; cash<0 charged borrow/252 | clean stock path 0-VND ✓ (existing) |
| **S2 Levered parking entry** | fear-gate on parking sleeve | parking sleeve allowed to deploy on borrow (fast vehicle) | **FIX #4** — make parking-margin reconcile to 0 |
| **S3 Hold while levered** | each session | mark G; accrue borrow interest on cash<0 | add `gross` field (FIX #2) |
| **S4 Margin-call** | `G > MGE_HARD` mid-hold (price drop) | force-sell to bring `G → MGE_FLOOR`; pro-rata across positions (default), intraday at today's px; log `MARGIN_CALL` tx | **FIX #1** — 0-VND |
| **S5 Regime-deleverage** | DT5G downgrade (→CRISIS/BEAR) while `G>1` | lower target G (e.g. force `G≤1`); sell excess | **FIX #5** — 0-VND |
| **S6 Rebalance while levered** | quarterly basket rebal | preserve G (don't silently delever) | gross-aware sizing |
| **S7 Unwind** | close levered book / hold-expiry | sell, repay borrow, realize P&L | existing sell path ✓ |
| **S8 Carry asymmetry** | each session | idle cash → deposit; borrowed cash → borrow (10%/yr) | existing interest block ✓ |

## C. Design decisions (defaults — user can override)

1. **Margin-call execution timing.** Default = **intraday at today's price** (VN brokers force-sell intraday on a margin breach; conservative — assumes no escape). Alternative = T+1 open (consistent with other exits but lets one more day of loss accrue). → default intraday.
2. **Margin-call liquidation order.** Default = **pro-rata trim** across all open positions (neutral, preserves diversification). Alternatives: cheapest-to-exit first (liquidity-aware), or lowest-conviction first (mirror EVICT). → default pro-rata; revisit if it sells the wrong names.
3. **`MGE_HARD` buffer.** Default = `MGE + 0.15` (e.g. MGE 1.30 → call at 1.45). Gives price noise room before a forced sale; the bigger the buffer, the deeper the tail you tolerate.
4. **`MGE_FLOOR` (post-call target).** Default = `MGE` (deleverage back to the soft cap, not all the way to 1.0 — avoid over-selling on a transient spike).
5. **Regime-deleverage target.** Default = **force `G≤1.0` on CRISIS** (kill leverage in the worst regime; keep cash-funded positions). BEAR = `G≤MGE` (no extra room, no forced cut).
6. **Parking-on-margin (S2) gate.** Reuse the lever-at-bottom gate (deposit-gate `m≥0.5` + deep-pb_z + CRISIS/BEAR + A&C-confirm) so leverage lands only at confirmed bottoms.

## D. Build order (each: implement → self-check 0 → walk-forward → pin)

1. **FIX #2** live gross tracking — add `gross` to nav_history; no behavior change (production byte-identical).
2. **FIX #1** margin-call — the missing risk primitive; validate it fires in a crash, reconciles 0.
3. **FIX #4** parking-on-margin reconciliation — unlock the fast vehicle for lever-at-bottom.
4. **FIX #5** regime-deleverage.
5. Integration: lever-at-bottom (S1+S2) WITH S4/S5 active → re-measure the edge under *realistic* forced-unwind, walk-forward. This is the honest re-test of the thread I wrongly closed.

## E. Open questions for user (non-blocking; defaults chosen above)

- Margin-call order: pro-rata (default) vs liquidity-aware vs conviction-aware?
- Should regime-deleverage be hard (`G≤1` on CRISIS) or graded?
- Real VN broker margin mechanics (maintenance margin %, call grace period, force-sell rules) — verify with the desk (DollarBill/Mafee) before calibrating `MGE_HARD`/timing to reality rather than my assumption.
