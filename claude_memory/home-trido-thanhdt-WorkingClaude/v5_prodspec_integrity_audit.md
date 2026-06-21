---
name: v5-prodspec-integrity-audit
description: "Is V5/V121_ENS 2014-now 'số ảo'? VERDICT: no look-ahead (point-in-time signal, fills within real BQ range, NAV identity=0). Gap backtest-40% vs live-engine-23% is NOT signal (v10≈v11, capacity-bound) and NOT look-ahead — it's ETF-proxy (~3pp) + idealized backtest construction (~12pp). Trustworthy V5 2024-now = 23% (transparent engine), backtest 37-40% is idealized."
metadata:
  node_type: memory
  type: project
  originSessionId: 08a5052c-9cbc-4e6a-a377-48ffb1d4f142
---

# V5 / prod-spec integrity audit — is the 2014-now performance 'số ảo'? (2026-05-28)

User asked to trace the 23%-vs-36% V5 discrepancy and confirm 2014-now isn't illusory.

## VERDICT: NOT số ảo (no look-ahead), BUT the headline is OPTIMISTIC on 3 counts.

### Confirmed CLEAN (no fakery)
1. **Execution no-look-ahead**: `t1_open_exec=True` (signal T-close → fill T+1 open). Audit Gate C: **99.8% (429/430) of stock fills lie within that day's actual BQ [Low,High]** (1 outlier = HPG 2025-07-09, adjustment-factor edge). Trades are real & executable.
2. **Books reconcile**: Gate A — daily NAV identity `nav == cash + cash_etf + stocks_mv` residual = **0.00 VND** over 593 days.
3. **SIGNAL_V11 is point-in-time** (audited `sim_v11_for_analyzer.py:SIGNAL_V11_UNIFIED`): `fa_dated`/`fin_dated`/`state5`/`days_since_release` all as-of joins (`t.time >= f_time AND < next_f_time`); `vni_max3m` = trailing 60-session rolling MAX; classification uses only contemporaneous TA + as-of FA tier + valuation z. **NO forward `profit_*` columns.** v11's edge is a genuinely better model, not look-ahead.

### Three sources of OPTIMISM in the headline (quantified)
**Decomposition of fresh-2024 V5: backtest 40.87% → live-faithful ~22.6%, gap 17.8pp:**
- **ETF proxy** (run_5systems_prodspec uses VNINDEX as the ETF-parking underlying, not real E1VFVN30): V5 full-period inflation **+1.77pp** (real-ETF 24.05% vs proxy 25.82%); V4 +0.23pp; 2024-slice only +0.55pp. `run_prodspec_etf_audit.py`. NB: 2024+ E1VFVN30 actually BEAT VNINDEX (+87% vs +70%, total-return), so proxy isn't a free lunch — the inflation is regime-specific.
- **Fill model**: HYBRID(ATC/11:15) vs t1_open ≈ **0.5pp** only (`pt_v5_audit_t1.py` 22.57% vs HYBRID 23.07%). NOT a driver.
- **SIGNAL VERSION — DISPROVEN as the driver (corrected 2026-05-28)**: I hypothesized the ~15pp residual was SIGNAL_V10 (live) vs SIGNAL_V11 (backtest pkl). **WRONG.** Direct diff: `signal_v10_sql.py` SIGNAL_V10 and `signal_v11_sql.py` SIGNAL_V11 produce **near-identical output** for 2024+ (same 175,166 rows, identical play_type distribution, TIER_BAL 3579 vs 3556 = 23-row diff). The current SIGNAL_V10 is ALREADY FA-tier-integrated (has COMPOUNDER_BUY/DEEP_VALUE_RECOVERY/MOMENTUM_QUALITY). v11 only adds a `ticker_1m` UNION fallback (rarely fires on prune universe). **Swapping pt_v5_audit to SIGNAL_V11 gave byte-identical 82.2174B / 23.07%** → BAL/VN30 books are capacity-bound (top-12 picks identical), exactly like the SVT-inert finding. **So the 23-vs-40 gap is NOT the stock signal.**
  - **Real driver of the residual ~12pp = backtest CONSTRUCTION optimism**, not signal/look-ahead: the prod-spec `switched_nav` recombines independently-run full-25B legs (proxy-ETF parked) + cached-M1 ensemble, vs the transparent engine's realistically-constructed books + live-recomputed M1. Not yet fully isolated leg-by-leg (ensemble-M1 allocation timing is prime suspect). The BAL book reality: BA v11 stock picks returned only ~+41% over 2024-now while VNINDEX +70%/E1VFVN30 +87% (BA misses VIC/VHM mega-cap rally) — so the transparent ~23% is plausibly the REAL number and the backtest 37-40% is idealized.

## What's actually live vs backtested
- Backtest headline **V5 25.82% (full) / 40.87% (fresh-2024)** = v11 signal + VNINDEX-proxy ETF.
- Live-faithful (v10 + real E1VFVN30 + realistic fills, fresh-2024) = **~22.6-23.1%**.
- **DONE (2026-05-28): all 6 live pt_ scripts upgraded to SIGNAL_V11** (pt_v11_tq34b, pt_v12_tq34b, pt_v12_live, pt_v12_dt4, pt_v121_ensemble, pt_v121_ens_q2) via new reusable `signal_v11_sql.py`. Verified byte-identical result (v10≈v11) so it's a cosmetic/consistency rename, NOT a performance change. To make the NUMBERS match, the real fix is the BACKTEST (swap VNINDEX-proxy ETF → real E1VFVN30, brings backtest DOWN to ~24% reality), not the live up.

## CORRECTED canonical table — run_5systems_prodspec.py now uses REAL E1VFVN30 (2026-05-28)
Fix applied (line ~68: VNINDEX proxy → real E1VFVN30 w/ pre-2016 rescaled-proxy fallback) + re-run full 2014-now:

| System | CAGR | Sharpe | MaxDD | Calmar | vs old-proxy |
|--------|------|--------|-------|--------|--------------|
| V1 V11+TQ34b | 20.16% | 1.37 | -18.94% | 1.06 | -0.40 |
| V2 V12+TQ34b | 21.16% | 1.64 | -14.43% | 1.47 | -0.05 |
| V3 V12+LIVE | 21.15% | 1.64 | -14.43% | 1.47 | -0.07 |
| **V4 V121_ENS** ⭐ | **24.01%** | **1.67** | **-16.03%** | **1.50** | -0.23 |
| V5 V4+KellyQ2 | 24.05% | 1.55 | -18.41% | 1.31 | **-1.77** |

**MAJOR FINDING: with real ETF, V5 (KELLY) LOSES its edge over V4 (BASE).** V5 24.05% ≈ V4 24.01% on return, but V4 wins Sharpe (1.67 vs 1.55), Calmar (1.50 vs 1.31), DD (-16.0 vs -18.4). V5's old "+1.6pp KELLY premium" was mostly **proxy illusion** (VNINDEX-proxy inflated the 100%-parked KELLY leg). **→ V4 (V121_ENS, BASE) is now the recommended system; KELLY/V5 no longer justified.** Full-2014 V5-real 24.05% matches etf_audit V5 KELLY REAL exactly → backtest now consistent with live-faithful engine on full period (the fresh-2024 gap that remains is construction/path, separate from proxy).

## ROOT CAUSE of the residual ~14pp construction gap — STALE state5 in the pkl (2026-05-28, closed)
Traced fully (leg-by-leg + arg A/B + data diff). Backtest fresh-2024 V5 (37.7% real) vs live engine (23%): ALL legs higher (BAL +111% vs +41%, VN30 +87 vs +73, LAGGED +87 vs +65). Ruled out: prices (pkl Close == live SQL Close 100%, same 392 tickers), state-for-parking (CSV vs BQ v34b 4/3082 diffs), args (`run_bal_argdiff.py`: pkl-data BAL = +117% under prod-spec AND pt-style args; HYBRID +6pp, force_close_eod 0pp — args don't matter).
**Real cause = the backtest signal pkl `ba_v11_unified_12y_sig.pkl` (built 2026-05-20) carries a STALE `state5` column**: 69,611 AVOID_bear rows vs live SQL 48,153 (~21.5k more bear-state rows); buy-tier rows 3436 vs 3556 (mostly shared, 3212 common). Prices/universe identical, only the embedded state5 differs (vnindex_5state was recomputed since May 20).
**Why it inflates KELLY V5**: the pkl's stale-bearish state5 sets AVOID_bear → blocks stocks on days the (current) PARKING state treats as NEUTRAL(3) → under KELLY {3:1.0} that idle cash is dumped into E1VFVN30 (+87% in 2024-25). So *signal-state* and *parking-state* DISAGREE in the backtest, accidentally over-parking into the winning ETF (+70pp on BAL). The live engine uses ONE consistent current state → no windfall → +41% BAL → ~23% V5. **This is an internal-inconsistency artifact, NOT replicable live, NOT real alpha.**
**FIX**: rebuild `ba_v11_unified_12y_sig.pkl` from CURRENT `vnindex_5state` (so backtest state5 == live state5 == parking state). Expected to bring the backtest down to ~live (~23-24%). Until then, **trust the live engine (~23%) over the prod-spec backtest (37-40%)**. Files: `run_bal_argdiff.py`.

## ✅ FIX APPLIED — pkl rebuilt from current state, FINAL honest table (2026-05-28)
`build_pkl_v11_current.py`: backed up old pkl (`ba_v11_unified_12y_sig.pkl.bak_stale_20260520`), rebuilt from SIGNAL_V11 with CURRENT vnindex_5state. Verified 2024+ AVOID_bear 69,611→**48,153** (== live SQL), TIER_BAL 3,436→3,556 (== live). Re-ran run_5systems_prodspec.py (now real E1VFVN30 + current-state pkl):

| System | CAGR | Sharpe | MaxDD | Calmar | vs old "canonical" (proxy+stale) |
|--------|------|--------|-------|--------|------|
| V1 V11+TQ34b | 16.97% | 1.19 | -19.9% | 0.85 | -3.6pp |
| V2 V12+TQ34b | 18.53% | 1.47 | -16.4% | 1.13 | -3.1pp |
| V3 V12+LIVE | 18.53% | 1.47 | -16.4% | 1.13 | -3.1pp |
| V4 V121_ENS | 20.93% | 1.48 | -19.2% | 1.09 | -3.3pp |
| **V5 V4+KellyQ2** | **22.08%** | 1.44 | -18.4% | 1.20 | -3.7pp |
| VNI B&H | 11.42% | 0.68 | -45.3% | 0.25 | — |

**The stale-state5 artifact inflated the ENTIRE history ~3-4pp (all systems), not just 2024.** Old "canonical" V5 25.82/26.09% and V4 24.24/24.64% were inflated by proxy-ETF (~0.2-1.8pp) + stale-state5 (~3pp). **TRUE honest full-period: V5 ~22%, V4 ~21%, V1 ~17%.** Backtest now CONSISTENT with live engine (2024-now ~23%). V5(22.08) regains modest edge over V4(20.93) +1.15pp once state is consistent (Calmar 1.20 vs 1.09). Realistic forward (−1.5pp haircut): V5 ~20%, still ~2x VNI B&H.
**Going forward backtest↔live aligned**: backtest uses rebuilt current-state pkl; live pt_* use SIGNAL_V11 SQL ([REDACTED] current). Both self-consistent. NOTE: for a true point-in-time backtest one would need VINTAGE state per date (state machine gets recomputed); current rebuild removes the internal inconsistency but uses today's state for all history.

## VINTAGE state reference — built for reproducible re-tests (2026-05-28)
To stop state-restatement drift from silently changing backtest results, built a point-in-time vintage system:
- **`snapshot_state_vintage.py`** — `--init` seeds `state_vintage/`; default (daily) appends today's `vnindex_5state` as `vnindex_5state_VINTAGE_YYYYMMDD.csv` + MANIFEST. **Wired into `papertrade_daily.bat` step [0b]** → true vintage accumulates going forward.
- **`state_vintage_loader.py`** — `load_vintage(asof=None)` returns the state series as KNOWN on `asof` (latest snapshot ≤ asof). Future "as of date D" backtests should call this for reproducibility / no-restatement.
- Seeded with 2 historical points: **VINTAGE_20260520** (the STALE state from the May-20 pkl, 2014+, the one that inflated backtests) + **VINTAGE_20260528** (current corrected). MANIFEST + README in `state_vintage/`.
- **WALK-FORWARD VINTAGE = WRONG TOOL (decided 2026-05-28, do NOT build it).** Tested whether the May20→May28 restatement is causal-tail (min_stay, walk-forward-fixable) or methodology-rebuild (not fixable): diff = **1050/3082 (34.1%) states changed, SPREAD ACROSS ALL 12 YEARS** (2014:99 … 2025:122), only 4 diffs in the last 30 sessions. → It's a **methodology/data-rebuild change**, NOT min_stay tail. A walk-forward replays a FIXED methodology point-in-time → it CANNOT reproduce methodology changes → would give FALSE confidence. Also: v3.4b `state_raw→state` is the full Tam Quan chain (US override+BTC+concentration+risk+smoothing; mode+min_stay on state_raw reproduces `state` only 51%), CSV lacks `state_dvg`, so a real walk-forward needs replaying the 6-step chain per cutoff (multi-hour, scripts not import-safe). **CONCLUSION: forward-snapshot freezing (already built) is the CORRECT + sufficient solution** — it pins each backtest to an immutable state version, immune to BOTH methodology change and min_stay tail. State is unstable across rebuilds (34%/8days) so backtests MUST pin to a frozen vintage snapshot.
- LIMITATION: true per-date vintage only accumulates from 2026-05-28 forward (can't recover what the state table said on arbitrary past dates — only the 2 pkl-snapshot points exist historically). For absolute point-in-time pre-2026-05, would need walk-forward replay of the v3.4b chain (heavier, not done). The 2-point seed already lets us reproduce the stale-vs-corrected difference.

## V1-V5 on DT4 foundation — live-faithful (2026-05-28, `run_5systems_dt4.py`)
FULL DT4 foundation (NOT decoupled): fresh SIGNAL_V11 with state5 from `vnindex_5state_dt_4gate` (so AVOID_bear/SVT/tiers all DT4) + DT4 parking/overheat + real E1VFVN30 + t1_open. Full 2014-now:

| Sys | DT4 CAGR | Sharpe | MaxDD | Calmar | vs corrected TQ34b |
|-----|----------|--------|-------|--------|--------------------|
| V1 V11 | 19.34% | 1.29 | -21.6% | 0.89 | **+2.37pp** (TQ 16.97) |
| V2 V12 | 20.12% | 1.54 | -14.3% | 1.40 | +1.59 (TQ 18.53) |
| V3 V12.1 | 21.09% | 1.55 | -15.2% | 1.39 | (TQ V3=V12+LIVE 18.53) |
| V4 V121_ENS | 22.47% | 1.56 | -18.1% | 1.24 | +1.54 (TQ 20.93) |
| V5 +Kelly | 23.43% | 1.46 | -20.8% | 1.12 | +1.35 (TQ 22.08) |

OOS24: V5 34.07%, V4 28.37%, V1 25.44%. **DT4 beats TQ34b on CAGR across ALL systems (+1.3 to +2.4pp).**
**Mechanism (differs from earlier ensemble DT tests which were null/negative)**: here DT4 is the FULL foundation (state5 in the signal → drives AVOID_bear gate), not decouple-parking-only. DT4 less defensive than v3.4b (2024+: 78 AVOID_bear days vs 161) → blocks fewer stocks → captures more 2024-25 bull. Earlier ensemble-DT tests only swapped parking (capacity-bound, null); changing the AVOID_bear GATE is what moves returns.
**Trade-off**: DT4 buys return with LESS defense → higher DD on V1 (-21.6 vs -19.9) and V5 (-20.8 vs -18.4); V2/V3 DD fine. Best risk-adj = V3/V4 DT4 (Sharpe 1.55-1.56). Realistic forward (-1.5pp): V5 ~22% / V4 ~21% / V1 ~18%, still ~2x VNI.
**Caveats**: backtest (not live fills); 2014+ only (DT V-recovery lag + pre-2014 risk); DT4 higher beta in bull. NAV: `data/5sys_dt4_nav.csv`.

## Paper-trade A/B: DT4-foundation vs TQ34b, V1-V5 (2026-01-01 → [REDACTED]30 GO-LIVE decision)
`pt_dt4_vs_tq34b_ab.py` — V1-V5 under each state foundation, live-faithful (fresh SIGNAL_V11 with state5 per foundation, real E1VFVN30, t1_open, prod-spec). Sim runs contiguous from 2025-01-01 (warmup) then NAV sliced+rebased to 2026-01-01 (YTD of a running book). Decision = which foundation goes LIVE.
- **Wired into `papertrade_daily.bat` step [7]** (daily). **Scheduled task `DT4FoundationDecision`** fires [REDACTED]30 09:00 → runs `dt4_foundation_decision.bat` → writes `data/DT4_FOUNDATION_DECISION.md` + popup. Report auto-shows 🟢/🔴 verdict on/after 06-30 (🟡 before).
- **Initial reading (2026 YTD → 05-26): DT4 wins ALL 5 systems** (vote 5-0). V5 DT4 -0.41% vs TQ34b -10.81% (Δ+10.4pp, DD -13.9 vs -17.3); V4 -2.24 vs -9.28 (+7.0pp); V1 +6.9pp. 2026 is a hard/choppy period (both negative) but DT4 less defensive (fewer AVOID_bear) → loses far less + better DD. Decision pending end-June.
- ⚠️ **BUG FIXED during build (reusable lesson)**: E1VFVN30 data lags (~stops 05-18 while VNI/state go to 05-26). The ETF-parking `vn30_underlying` fallback MUST rescale the VNINDEX proxy to ETF scale (~25 vs ~1400) — raw proxy = 56x price jump → KELLY-parked NAV explodes → bogus -50/-79%. Also: never start `simulate` on a date-sliced list mid-history; run contiguous from a warmup start then slice+rebase the NAV. Both bugs gave catastrophic numbers before the fix.

## Honest number to quote
For V5 forward expectation: **~22-24% real** (live-faithful), NOT 25.82% (proxy-inflated v11) and NOT 40% (in-sample fresh-2024). Subtract the usual ~1.5pp real-world haircut on top. V4 BASE is barely proxy-affected (24.01% real) and remains the cleaner risk-adjusted pick.

## Files
- `run_prodspec_etf_audit.py` (proxy vs real E1VFVN30, V4/V5, full/2016+/2024+)
- `pt_v5_audit_2024.py` (transparent V5 = KELLY ensemble, 2024-now, SIGNAL_V10+HYBRID+real-ETF; trade log + reconciliation) → `data/pt_v5_2024_*`
- `pt_v5_audit_t1.py` (same, t1_open fills — isolates fill model)
- Gate verification: inline (NAV identity, per-lot P&L, fills-within-BQ-range)

## Cross-refs
- [[dt4-ensemble-smart-integration]] — same harness lesson (reduced/proxy harness inflates vs prod/real)
- [[backtest-canonical-prodspec]] — the prod-spec table being audited (uses proxy ETF + v11 pkl)
