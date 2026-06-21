# ZIP 3 — V2.3 + DT5G Recommender (`v23_dt5g_recommender.zip`)

**REPLACES** ZIP 2 (`v4_dt5g_recommender.zip`, handed off 2026-05-29). Layer 1
(`dt5g_state_engine.zip`, the DT5G state engine) is **unchanged and still required** —
deploy/keep it in the SAME working folder and run it first each day.

> ⚠️ **One Layer-1 file IS updated in this zip**: `simulate_holistic_nav.py`. Unzip this package
> AFTER ZIP 1 so it overwrites ZIP 1's copy (carries a critical `bq()` zero-row fix — see §Bug fixes).

## Why V4 → V2.3 (one paragraph)

The V4 ensemble-switch architecture did not survive a faithful single-ledger backtest
(real fills, one wallet): **V4 faithful = 14.20% CAGR / Sharpe 1.10** vs
**V2.3 = 25.77% / 1.65** (plain-sum champion) and **26.29% / 1.80 / MaxDD −18.3% / Calmar 1.43**
with the live allocator shipped here (full period 2014→2026-06, 50B, ~−1.5pp/yr real-world
haircut applies). V2.3 drops the ensemble switch entirely: both books run **always-on**, capital
is steered by a slow state-conditional allocator instead of signal-switching. V4 keeps running
on our side as the paper-trade **control arm** of a forward OOS showdown — it is no longer the
production recommendation source.

## What V2.3 is

| Component | Spec |
|---|---|
| **BOOK A — BAL** (momentum) | SIGNAL_V11 stack + D1 RE_BACKLOG + SV_TIGHT Fresh-Q + overheat guard + **AVOID_exbull** (momentum tiers blocked in EX-BULL — IC inverts there) + **regime_size** (8L rating≥4 half-size, BEAR/CRISIS only). 10%/slot of book, max 12, hold 45d, stop −20%, Fin/RE cap 4. |
| **BOOK B — LAG** (PEAD) | Earnings-surprise drift: NP_R≥15 & prior_n_good≥4 & pa_HL3≥5, entry T+5 after release, hold 25td, **NO stop**, LAG_HI 10% / LAG_LO 8% per slot. **Always on — no ensemble switch.** |
| **Allocator** | w_LAG target by DT5G state: **CRISIS 50% / BEAR 0% / NEUTRAL·BULL·EX-BULL 65%**. Rebalance ONLY when |current − target| > **±10pp** (band trigger: let the winner run; BEAR/CRISIS entries always breach the band → protection fires). BEAR=0 because PEAD loses money in bear (good earnings get sold). |
| **ETF parking** | `{NEUTRAL: 0.7}` of idle cash → E1VFVN30, on **both** books. |
| **CAPIT v2** | Capitulation-buy sleeves: gate = oversold breadth (D_RSI<0.3 share of ticker_prune) ≥ **30%**; size routed by state (CRISIS 1.0 / NEUTRAL 0.75 / BULL·EX-BULL 0.5 / BEAR 0.5 only if dd52w>−25% or domestic rv10-cooling, else 0) × 0.5 if grind (washout repeat within 20–90 sessions); basket = quality-golden (ROE_Min5Y≥12% & ROIC5Y≥10% & FSCORE≥6, pb_z<−1 preferred); committed = size × the book's free cash, hold 60td, stop/slot-exempt. Margin valve stays a MANUAL desk decision. |

Behavioral difference the desk must know: **V2.3 does NOT go full-cash in BEAR/CRISIS** (unlike
V4). BAL stays on behind the Fresh-Q gate (≤60d BEAR / ≤30d CRISIS) with weak names half-sized;
LAG is defunded by the allocator in BEAR; CRISIS washouts are a *buy* signal for the CAPIT sleeve.

## Contents

```
deploy_golive_dt5g_v4/golive_recommend_v23.py   ENTRY — daily picks -> out/golive_v23_recommendations_<DATE>.{md,csv}
                                                + data/golive_v23_status.json (allocator/capit status)
deploy_golive_dt5g_v4/golive_daily.bat          daily orchestrator (Layer-1 steps then [5] = v23)
deploy_golive_dt5g_v4/README.md                 full architecture / fail-safe / config reference (updated to V2.3)
deploy_golive_dt5g_v4/requirements.txt
signal_v11_sql.py                               live BA SIGNAL_V11 (point-in-time)
simulate_holistic_nav.py                        bq() helper — UPDATED, overwrites ZIP-1 copy (0-row fix)
earnings_events_classified.csv                  LAG/PEAD schedule input
earnings_surprise_data.pkl                      LAG_HI/LAG_LO surprise split input (NEW vs ZIP 2)
telegram_recommend.py                           OPTIONAL 18:00 Telegram report (V2.3 layout) — overwrites ZIP-1 copy
telegram_config.template.json                   copy -> telegram_config.json + fill bot_token/chat_id
recommend_holistic.py                           report dependency (TA scoring / book display)
fundamental_rating_all.csv                      report dependency (FA display columns)
data/rating_8l.csv                              report dependency (8L "R" column display; optional)
```

Gone vs ZIP 2 (no longer needed): `compare_v11_v12_concentration_switch.csv` (cached M1 ensemble
signal — V2.3 has no ensemble mode). `golive_recommend.py` (V4) is NOT shipped; do not run it.

## Setup

1. Unzip **ZIP 1 first**, then this zip, into the same WORKDIR (this zip intentionally
   overwrites `simulate_holistic_nav.py` and `telegram_recommend.py`).
2. Edit hardcoded paths to your environment: `WORKDIR` in `golive_recommend_v23.py`,
   `simulate_holistic_nav.py`, `telegram_recommend.py`, `recommend_holistic.py`;
   `ROOT`/`PKG` in `golive_daily.bat`.
3. Same BigQuery + Python prerequisites as ZIP 1. Additional BQ tables read:
   `tav2_bq.fa_ratings_8l` (weak-size flag) — stale/missing degrades gracefully (no weak flag),
   never blocks the run.
4. Keep `earnings_events_classified.csv` / `earnings_surprise_data.pkl` refreshed each session
   (our side refreshes via `refresh_lagged_caches.py`; shipped copies are current as of the
   build date — LAG entries will silently dry up if these go stale through an earnings season).
5. **Allocator current-weight**: the recommender reads the live book split from
   `data/pt_v22_dt5g_logs.csv` if present. At your site, either (a) maintain that CSV from your
   own ledger (columns `ymd,nav,SECOND_cash,SECOND_stocks,SECOND_etf`; SECOND = LAG book), or
   (b) ignore the printed current/REBALANCE line and compare the **target w_LAG** against your
   actual book weight yourself — the band rule is: rebalance only when off by more than 10pp.

## Run

```
golive_daily.bat                                  # one scheduled task ~15:30 ICT after close
# or just Layer 2 (after ZIP-1 published today's gated state):
python deploy_golive_dt5g_v4\golive_recommend_v23.py
# optional Telegram desk report (after the recommender):
python telegram_recommend.py --dry-run            # verify, then drop --dry-run
```

## Bug fixes carried in this zip (important)

- **`bq()` zero-row crash** (`simulate_holistic_nav.py`): `bq --format=csv` prints NOTHING (not
  even a header) for a zero-row result; `pd.read_csv` then raised `EmptyDataError`. Any caller
  with a legitimately-empty query window crashed. Now returns an empty DataFrame.
- **Release-date lookback**: scripts that compute `days_since_release` from a window-limited
  release list must look back `DATE_SUB(START, INTERVAL 120 DAY)` — a window starting mid-quarter
  otherwise sees zero releases (crash, and worse: SV_TIGHT silently blocks ALL buys until the
  next earnings season). The V4 paper-trade died daily from 06-01 to 06-11 on exactly this; the
  recommender in this zip uses a 120-day signal window and is not affected, but if you port the
  pattern into your own ledger sim, keep the lookback.

## Validation summary (label per memory convention: baseline = V2.3C plain-sum champion)

| System | Full 2014→2026-06 (faithful, 50B) | Notes |
|---|---|---|
| **V2.3A (this package: allocator + band ±10pp)** | **26.29% / Sharpe 1.80 / MaxDD −18.3% / Calmar 1.43** | 32 rebalances/12y |
| V2.3C (plain-sum 50/50 static, baseline) | 25.77% / 1.65 / −20.1% | champion before allocator |
| V4 (replaced, faithful) | 14.20% / 1.10 | ensemble switch fails a real ledger |

Forward OOS: V2.3 paper-trade started fresh 2026-06-11 (50B, `pt_v22_dt5g.py` on our side);
V4 keeps running as the control arm. Note the LAG/PEAD edge is currently at its historical
trough (3rd percentile rolling-12M) — the allocator weights (BEAR=0, good-states 65%) were
chosen with that known and must NOT be retuned to recent history.
