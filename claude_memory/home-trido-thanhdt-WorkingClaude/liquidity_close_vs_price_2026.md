# Liquidity: adjusted Close vs unadjusted Price ([REDACTED]01)

## Root cause
`Close` = back-adjusted price (dividends/bonus); `Price` = unadjusted (actual traded).
`Volume` is RAW (proven: BQ `Trading_Value` col == `Price*Volume` to the penny). So any
`Close*Volume` liquidity proxy understates real traded notional by exactly the `Close/Price`
ratio: **~52% low in 2014, ~41% in 2020, ~7% in 2023, ~1% in 2026** (worse the further back,
adjustment factor accumulates). Dictionary: `Trading_Value = Volume * Price` (correct).

Two independent places used `Close*Volume` and were fixed to `COALESCE(Price,Close)*Volume`:

## Fix A — stock-selection book (run_5systems_prodspec & friends)
Liquidity SCREEN (`liq>=1e9`), position fill CAP, universe top30, m3r ranking, LAGGED gate/cap.
DT5G **state engine NOT involved here** (state uses no trading value — see Fix B caveat).
Files: signal_v11_sql.py, sim_v11_for_analyzer.py, run_5systems_prodspec.py,
simulate_holistic_nav.py. Rebuilt `ba_v11_unified_12y_sig.pkl` (623,242→708,053 rows; backup
`.bak_closeliq_20260601`). LAGGED book now uses real notional from BQ (`liq_real_l`), not
`adv*Open_adj`.
**Impact (A/B, prod-spec, TQ34b, real ETF, 50B, 2014→2026-05): every system improves on ALL
metrics.** V1 +16.68→**18.91%** (+2.23pp), V2/V3 20.43→**21.39** (+0.96), V4 20.32→**21.82**
(+1.50), V5 21.37→**22.47** (+1.10). Sharpe up, MaxDD down, Calmar up. Direction = removing a
conservative bias (Close understated liquidity → wrongly excluded names + over-tight caps).
Detail: data/dt5g_liqfix_compare.md.

## Fix B — EW breadth gate (vnindex_5state_ew_v1.py) — AFFECTS THE STATE ITSELF
Correction to earlier wrong claim "DT5G uses no trading value": the macro_state_live pure-index
sim doesn't, BUT the **state CONSTRUCTION** does. `vnindex_5state_ew_v1.py` builds the EW
composite that feeds all 7 factors. Line 127 `tv = Close*Volume`, gate `tv_avg60 >= 5e8 (500M)`
defines the eligible EW universe → breadth (%>MA50), ret_ew, cmf_med → composite EW close →
r_score → **state**. Close-tv shrinks the basket in old years (genuinely-liquid mid-caps with
real tv>500M but Close-tv<500M wrongly excluded). Dev's causal chain CONFIRMED.
Fix: `tv = COALESCE(Price,Close)*Volume`; `log_ret`/`above_ma50` STAY on Close (returns/MA50
must use adjusted). Added `t.Price` to query; MUST `rm _cache_universe_2013_now.pkl` (cache bug).
Backup: vnindex_5state_ew_full.csv.bak_closegate_20260601.
**Impact on state (ew_v1 level, 2014+, 3091 days):** EW universe broadens a LOT in old years
(2014 +26%, 2015 +32%, 2016 +27%, →~0% by 2025-26 — Close wrongly excluded liquid mid-caps).
Breadth mean-abs-diff up to 0.031 (2015)→~0 recent. **State differs on 7.8% of days (240),
concentrated 2021 (103 days!), 2015 (37), 2018 (24).** Direction = MORE bullish: EX-BULL +58,
BULL +35, NEUTRAL −70, CRISIS −20; dominant flips NEUTRAL→EXBULL(59)/→BULL(43). Mechanism: in
broad bull (esp 2021 retail mania) the wider correct universe lifts breadth/ret_ew → higher
r_score → correctly catches BULL/EX-BULL that Close-gate suppressed to NEUTRAL. Transitions 58→61 (no extra whipsaw).
**BUT at the PRODUCTION v3.4b level (after concentration filter + US override + bull-aware +
EMA→mode→min_stay smoothing) the change COLLAPSES to 0.7% (21/3092 days 2014+; FULL 2000+ 21
days; transitions 271→273). The 2021 episode (103 ew-days) shrinks to 2 v3.4b-days.** The
multi-layer chain absorbs almost all the breadth-gate difference → **deployed state is robust to
the fix.** Dev's chain is real at the EW layer but production-immaterial.
Full chain rebuilt (ew_v1→concentration→dual_v3→[reuse us_market]→v3.1→v3.4b), NOT deployed.
**Integrated V4/V5 (Fix-B delta = new state vs old, both on Fix-A real-liq pkl, 2014→2026):**
V1 18.91→18.07 (−0.84pp), V2 21.39→20.85 (−0.54), V3 21.39→21.39 (0, uses LIVE state untouched),
V4 21.82→20.97 (−0.85), V5 22.47→**22.50** (+0.03). Mixed/slightly-NEGATIVE, all within
path-dependency noise (memory std ~2.76pp). 21 differing days cluster 2019(8)/2025(5). Fix B is
theoretically more correct but NOT a backtest win → no urgency to deploy.
**DT5G pure-index NAV (1B, dep 0%, borrow 10%, 2000→now) before vs after Fix B = INDISTINGUISHABLE:**
FULL 15.80→15.79%, since-2011 12.35→12.34%, modern 13.62→13.60%; Sharpe/MaxDD/Calmar identical;
end-NAV 44.19→44.10B (−0.21%); DT5G gated-state differs only 27/6283 days (0.43%, clustered
2019:14/2025:12); transitions 112→110. → Fix B immaterial to DT5G timing; NO adjustment needed.
**STATUS: Fix B REVERTED in code (ew_v1.py tv back to Close) to keep live pipeline/daily-job
unchanged; new-state artifacts stashed as *.PRICEGATE.csv; canonical CSVs restored to close-gate
(= live BQ). To adopt: re-enable the Price tv line, rerun chain, deploy both BQ tables + re-pin
frozen snapshot. Fix A (stock-book liq) stays ADOPTED (pkl rebuilt, code kept).** Backups
*.bak_closegate_20260601.
