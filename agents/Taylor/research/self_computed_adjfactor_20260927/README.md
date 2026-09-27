# Self-computed corp-action adjustment factor — feasibility PROTOTYPE

**Job** `Taylor_20260927_034929` · 2026-09-27 · Taylor (Quant) · **R&D ONLY, NOTHING WIRED**
Bus question addressed: `Mike/retro-pattern-recurring-fpt-vendor-backfill-2days` (day 4).

Artifacts here: `selfcomp_adjfactor.py` (prototype), `audit_week.py` (cohort audit),
`out_fpt.txt`, `out_control.txt`, `out_coverage.txt`, `out_week_audit.txt`, `out_negcontrol.txt`
(raw runs, 2026-09-27, BQ data through 2026-09-25).

## TL;DR — 5 findings, in order of how much they change what we do

1. **It is NOT an FPT problem. Every computable ticker with a price-adjusting ex-date in
   2026-09-19..09-25 is broken: 15 BROKEN / 0 OK.** Deviations −2,82% to **−20,66%**.
2. **VPB (−20,66%) is HELD IN BOTH LIVE ACCOUNTS** (SpaceX + ZaloPay). FPT is not.
3. **Self-computing the factor from `tav2_bq.corporate_action` WORKS**: on the immediately
   preceding cohort (ex-dates 09-01..09-18) it reproduces the vendor's own cumulative factor on
   **46 tickers to within ±0,08%**, over factor magnitudes 1,01 → **4,16**.
4. **Independent third source confirms the repair**: `ticker_1m` already carries the correct FPT
   factor back to 09-08, and its `Close` matches our self-computed `Close` to **≤0,006%** on all
   5 sessions where `ticker`/`ticker_prune` are still wrong.
5. **Rights issues are unrepairable from our data** (subscription price is not a column;
   `ref_price` is **NULL for all 2.418** events since 2025-01-01). 9/24 tickers in the suspect
   week fall in this hole → any fallback must fail-closed there, not guess.

## 1. The FPT defect, measured (`out_fpt.txt`)

Event: `ISS` "Cổ phiếu thưởng" ratio **0,1**, `exright_date=2026-09-21`, `event_status=executed`,
`ingested_at=2026-09-22 15:44:43`. Correct back-adjustment factor for every session before
09-21 is therefore **1,1** (`r = Price/Close = 1,1`).

| window | n | `r_obs` (vendor) | `r_pred` (self) | dev |
|---|---:|---:|---:|---:|
| 2025-01-02 … 2026-09-14 | 419 | 1,0000 → 1,1877 | ×1,1 higher | **−9,09%** every segment |
| 2026-09-15 … 2026-09-18 | **4** | 1,099978 | 1,100000 | −0,0020% ✅ |
| 2026-09-21 … 2026-09-25 | 5 | 1,000000 | 1,000000 | 0,0000% ✅ |

**Shape ≠ the VHM case** in `kb/data_registry/price-volume/ticker_price_stale_on_exdate.md`. VHM
was ONE row of the **`Price`** column forward-filled on its ex-date. Here `Price` is fine; it is
**`Close`** whose back-adjustment reached only the **4 last cum sessions** and no further —
419/428 sessions of history sit in the pre-event frame. The deviation is a flat −9,0909%
(= 1 − 1/1,1) across 20 months, i.e. exactly one missing factor, not drift.

The same "**exactly 4 cum sessions correct**" signature repeats on FPT (ex 09-21 → 09-15..09-18),
GAS (ex 09-22 → 09-16..09-21) and VPB (ex 09-24 → 09-18..09-23). That is the `SETTLE_RUN=4`
constant bq_admin described, i.e. the ETL's narrow fallback path ran and the full-window rewrite
(gated by `need_cafef`, registry §H2) did not.

**On the stated root cause (VCI rate-limit that day):** consistent with what we measure, and the
cohort evidence sharpens it — every event of that ONE week is affected while the preceding week's
events are clean, which is the signature of a dated outage rather than of a per-ticker glitch. But
the corollary "it will heal when VCI is reachable again" is **not** supported: four trading days
after the ex-date, `ticker` still covers only 09-15..09-18 while `ticker_1m` — same ETL, different
window — already reaches 09-08, and everything older than 15 sessions is frozen by design
(registry §3). We hold no earlier snapshot of `ticker`, so we cannot say whether its window crept
at all; what the latest data does say is that the bulk of history is still wrong, and that the
mechanism which would repair it is the one bq_admin confirmed never fires for this defect class.

## 2. Blast radius — cohort audit (`out_week_audit.txt` vs `out_negcontrol.txt`)

`audit_week.py` takes every ticker with a price-adjusting ex-date in a window and asks whether the
factor reached the OLDEST session of a 4-month price window.

| cohort (ex-date range) | BROKEN | OK | UNCOMPUTABLE |
|---|---:|---:|---:|
| **2026-09-19 … 09-25 (suspect week)** | **15** | **0** | 9 |
| 2026-09-01 … 09-18 (negative control) | 11 | **46** | 26 |

BROKEN in the suspect week: AMS, BTD, DRI, E29, **FPT**, **GAS**, HTL, PGD, PHC, TVN, V12, VCC,
VFR, **VPB**, VTB. The 11 BROKEN in the control window are all thin names (BAL, DP1, DVN, HES,
NJC, OIL, PAT, PBP, PLE, PMT, SHC) — the ~19% background defect rate on illiquid tickers the
registry already documents, unrelated to this incident.

**The negative control is what makes the method credible.** A detector that flags every window it
is pointed at is measuring itself. 46/57 clean in one week and 0/15 clean in the next is a
discontinuity in the DATA, not in the tool.

## 3. The method

```
r(t)  = Price(t) / Close(t)                    # cumulative back-adjustment factor, vendor-implied
r_pred(t) = PROD over ex-dates E > t of f_E     # self-computed, from corporate_action
Close_self(t) = Price(t) / r_pred(t)            # the repaired series
```

Per ex-date, **all events sharing that date combine inside the exchange's reference-price
formula**:

```
P_ref = (P_cum − D_total) / (1 + q_total)   ⇒   f_E = (1 + q_total) · P_cum / (P_cum − D_total)
```

`q_total` = Σ stock ratios (bonus + stock dividend), `D_total` = Σ cash dividends per share,
`P_cum` = **raw** (`Price`) close of the last cum session. Event taxonomy is **reused** from
`corp_action_lib.is_price_adjusting` (ESOP / private placement do not move price) — not
re-derived. `daily_nav_snapshot.confirmed_qty_multiplier_after` /
`confirmed_share_event_multiplier` were deliberately **not** reused: they are QUANTITY multipliers
and return 1,0 for `DIV` by design, correct for share counts and silently wrong as a price factor.

### Two formula bugs the measurement caught (both would have produced FALSE ACCUSATIONS)

- **Multiplying same-day events instead of combining them.** GEX 2026-05-05 (bonus 20% + stock
  dividend 25%): the exchange uses `1 + 0,45 = 1,450`, matching the vendor's 1,450191; the product
  `1,20 × 1,25 = 1,500` is off by −3,32%. DGC 2026-09-14 (cash 3.000 + 5.000 on raw 46.750):
  `46750/38750 = 1,206452` matches the vendor to 6 decimals; the product of the two single-dividend
  factors gives 1,196544, off by +0,83%. The naive version reported both as vendor defects.
- **Comparing raw `Price` against the adjusted `High`/`Low` band.** `High`/`Low` live in the
  back-adjusted frame, so the VHM ffill guard flagged every healthy pre-event row (FPT 2025-06-11:
  `Price=117.900` vs band `[97.750, 99.520]`). The band must be lifted into the raw frame with a
  ratio from a NEIGHBOUR row — never from the suspect row, where `Price/Close` is the quantity
  that broke. Before the fix, 44/51 control tickers fail-closed as UNCOMPUTABLE.

Both bugs were found only because the control set exists. Neither is visible from the FPT case
alone, where the naive and correct versions agree.

## 4. Repair verified against an independent third source

| date | `ticker.Close` | `ticker_1m.Close` | `Close_self` = Price/1,1 | self vs `ticker_1m` |
|---|---:|---:|---:|---:|
| 2026-09-08 | 72.200 ❌ | 65.640 | 65.636,4 | −0,006% |
| 2026-09-09 | 72.400 ❌ | 65.820 | 65.818,2 | −0,003% |
| 2026-09-10 | 74.500 ❌ | 67.730 | 67.727,3 | −0,004% |
| 2026-09-11 | 72.700 ❌ | 66.090 | 66.090,9 | +0,001% |
| 2026-09-14 | 72.400 ❌ | 65.820 | 65.818,2 | −0,003% |

`ticker_1m` is a **different table written by the same ETL** on a different window, so this is a
genuine second witness, not a restatement. Residuals are the vendor rounding to the 10-VND tick.
Older than ~1 month `ticker_1m` runs out, so this cross-check cannot be extended backwards — the
46-ticker control cohort (§2) is what covers the long history.

## 5. Honest risk assessment — does "our corp-action DB beats the vendor" hold up?

**Measured, not assumed** (`out_coverage.txt`): over 60 liquid tickers × 9 months, every SUSTAINED
drop in the vendor factor was matched by a price-adjusting row in `corporate_action` —
**55 matched, 10 "orphan", and all 10 traced to `Price`-column artifacts, 0 genuinely missing
events**:

- 6 orphans on 2026-02-02 are the tail of a **market-wide `Price` forward-fill on 2026-01-30**
  (662/1.252 tickers have `Price` outside `[Low,High]` that day; GAS `Price=116.800` is exactly
  its 01-29 close while `Close=117.000`). New observation, not in the registry, which documents
  this ffill only as ~2% of ex-date rows.
- VHM 2026-08-07 is the known 08-06 ex-date ffill shifting the apparent step by one day.
- VNM (ex 06-26) and DCM (ex 07-09) are off-by-one for the same reason — a stale `Price` on the
  last cum session. Our table has both events, correctly dated.
- 40 further one-day ratio spikes were excluded before counting, by requiring the step to persist
  3 sessions. Counting them would have overstated our blind spots ~4×.

**Where the premise does NOT hold — state these before anyone wires this:**

1. **Rights issues are unrepairable.** `Quyền mua CP cho Cổ đông hiện hữu` needs the subscription
   price, which is not in `corporate_action`; the `ref_price` column that would have solved it is
   **NULL on all 2.418 rows since 2025-01-01** (verified). 9/24 of the suspect week and 26/83 of
   the control cohort land here. The prototype returns `None` → the caller must fail-closed. A
   fallback that silently used 1,0 here would invent a defect-free answer out of a data gap.
2. **`corporate_action` is `TRAP` status with an external writer** (registry:
   `price-volume/corporate_action_bq.md`) — upserted in place, no repo-side cron, `public_date`
   of historical rows overwritten. Feed is currently fresh (`MAX(ingested_at)=2026-09-26`,
   `MAX(public_date)=2026-09-25`) and the FPT event landed 09-22, one day after ex-date — which is
   exactly why this idea works today. But it is one external feed replacing another, not a move to
   first-party data.
3. **Multiple overlapping ex-dates**: same-day events are handled correctly (§3, verified on GEX
   and DGC). **Consecutive** ex-dates compound correctly — the negative control includes tickers
   with 2–5 events in the window, including TRC at a cumulative 4,16 and SZL at 1,79, both matched
   to <0,08%. The remaining exposure is a **missing** event inside a chain: one absent factor
   contaminates every date before it, and the error is indistinguishable from a vendor defect.
   The detector cannot tell "vendor wrong" from "our table incomplete" by itself — only the
   direction differs (ours missing ⇒ `r_obs > r_pred`; vendor missing ⇒ `r_obs < r_pred`), and
   that sign IS usable as a triage hint, not as proof.
4. **Precision floor ≈ 0,3%, not 0,1%.** DXG carries an unexplained −0,17% residual on its 14%
   bonus across 95 sessions (vendor 1,13802 vs exact 1,14). Reason unknown — possibly fractional
   rounding of shares actually issued. So a production threshold should sit near 0,3%; below that
   this method cannot distinguish a defect from vendor convention.
5. **`Price` must be trusted for the repair to work**, and `Price` has its own documented failure
   mode (the whole VHM registry entry). The band guard catches the gross cases but it needs a
   healthy neighbour row; two consecutive ffilled rows would defeat it.

## 6. Proposal — DETECT + fail-closed FALLBACK, not a replacement

Wags previously proposed alerting (option B). This goes one step further but deliberately stops
short of replacing the vendor:

- **Layer 1 — DETECT (cheap, safe, run daily).** For each ticker in any universe we care about,
  compare `r_obs` with `r_pred` over the relevant lookback. Flag `|dev| > 0,3%` persisting ≥3
  sessions. On today's data this fires on 15 names, with VPB the one that matters. Cost is one BQ
  scan; there is no decision riding on it, so a false positive costs an investigation, not money.
- **Layer 2 — REPAIR, only where computable.** Where every ex-date in the window yields a factor,
  publish `Close_self = Price / r_pred` as an explicitly-labelled alternative series. Where any
  ex-date is UNCOMPUTABLE (rights issue, unusable `Price`), **emit nothing** and let the existing
  `report_return_gate` keep blocking. That gate behaved correctly here; the goal is to stop it
  blocking on cases we can actually resolve, not to route around it.
- **Vendor `Close` stays the default.** It is right for ~98% of ex-dates (and 46/57 of the control
  cohort in one week), it is cheaper, and it covers rights issues we cannot compute at all.

**Do not wire any of this yet.** Per `coding_guidelines` §21 this touches investor-facing numbers,
so the gate is a **quant-skeptic CONFIRMED verdict on the repair layer** before it appears in any
consumer — explicitly out of scope for this prototype, which only had to answer "is it feasible".

### Separately, and independent of this design

- **VPB is held live in both accounts and its BQ `Close` history is off by −20,66%.** Anything
  that computes a VPB return across 2026-09-24 from `tav2_bq.ticker`/`ticker_prune` history is
  wrong by that much. Verified NOT affected: the §21 path
  (`dividend_adjusted_return.detect_adjustments`) reads only the LOCAL ratio step at the ex-date,
  which is correct — it returns ex 09-24, last-cum 09-23 @27.800, 5.740đ/cp for VPB, and the right
  values for FPT and GAS. Consumers that compare `Close` ACROSS the ex-date using pre-09-18
  history are the exposed ones; owners should check their own.
- **The 2026-01-30 market-wide `Price` forward-fill** (662/1.252 tickers) deserves its own line in
  `ticker_price_stale_on_exdate.md`: the registry frames this ffill as an ex-date phenomenon on
  thin names, and this is a whole-market, single-date instance on a non-ex-date.

## Reproduce

```bash
cd mike/agents/Taylor/research/self_computed_adjfactor_20260927
python3 selfcomp_adjfactor.py fpt
python3 selfcomp_adjfactor.py control  --since 2026-01-01 --end 2026-09-25 --min-adv 5e10 --limit 60
python3 selfcomp_adjfactor.py coverage --since 2026-01-01 --end 2026-09-25 --min-adv 5e10 --limit 60
python3 audit_week.py --ex0 2026-09-19 --ex1 2026-09-25     # suspect week
python3 audit_week.py --ex0 2026-09-01 --ex1 2026-09-18     # negative control
```
