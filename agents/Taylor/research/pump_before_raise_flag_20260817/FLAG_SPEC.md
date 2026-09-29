# FLAG_SPEC — `pre_raise_high_momentum` (PRHM)

Specification only. **Nothing in this document is wired.** Job `Taylor_20260817_101337`, evidence in
`FINDINGS.md`, design locked at `4835d3f2`.

---

## 0. Headline for whoever reads only one line

> **NOT RECOMMENDED FOR WIRING AS A RETURN PREDICTOR.** The preregistered 1-year test returned
> **`NO-FLAG`**: at all seven thresholds the flagged and unflagged groups are statistically
> indistinguishable (every CI spans zero, every Holm p = 1.000). What follows specifies the flag as
> an **informational disclosure** — the same non-blocking role `due_diligence.py` already plays —
> because the *inputs* are worth surfacing even though the *prediction* does not hold.

Wiring it as a gate, a sizing input, or a screen would be asserting an edge that this program looked
for and did not find.

---

## 1. What the flag is

For a candidate that has a **cash raise** (`RIGHTS` or `PRIVATE_PLACEMENT`) with an `exright_date`
in the recent past or announced ahead, report three point-in-time facts and one base rate. It does
not block, does not change sizing, does not alter a score.

## 2. Fields

Emitted under `due_diligence` output as a nested object; every field nullable, and a null must
print as "unavailable", never as a passing value.

| Field | Type | Definition | Null when |
|---|---|---|---|
| `prhm.pretrend_250` | float | Ticker's buy-and-hold return over its own last 250 sessions **ending the session before `exright_date`**, minus VNINDEX over the same calendar span | <250 sessions of history |
| `prhm.pretrend_bucket` | enum | `low` <15% · `moderate` 15–40% · `high` 40–100% · `extreme` >100% | pretrend null |
| `prhm.beta_250` | float | OLS beta of daily return on VNINDEX's, same 250-session window, **≥150 overlapping sessions required** | fewer than 150 obs |
| `prhm.beta_bucket` | enum | `low` ≤1.2 · `elevated` >1.2 (the preregistered mid/high bins merged — the >1.8 bin alone holds 31 events and is below the power floor) | beta null |
| `prhm.raise_count_3y` | int | Cash raises with `exright_date` in the trailing 3 years, from `tav2_bq.corporate_action`, `event_code='ISS'`, `event_status='executed'`, `issue_method_code ∈ {Rights, PP}` | — |
| `prhm.sector_raise_intensity` | enum | `elevated` if ICB 8777; else `normal` | ICB unavailable |
| `prhm.message` | string | §4 | — |

**Buckets are presentation, not prediction.** They exist so a human reads a number in context. The
cut points come from the preregistered grid and bins; none of them was validated as a decision
boundary, because none of them cleared the gap test.

## 3. Computation rules that must not be relaxed

1. **Every input ends the session BEFORE `exright_date`** (or before "today" for a forward-looking
   candidate). Asserted in this program: 0/2,953 violations. A window that touches the ex-date is
   a look-ahead bug, not a rounding choice.
2. **Horizons in the ticker's OWN sessions**, via row number — never calendar days. A suspension
   must shorten the count, not silently stretch the window.
3. **Beta needs ≥150 overlapping sessions.** Below that the field is null. Do not substitute a
   short-window beta; do not substitute `risk_rating.Beta` (see §6).
4. **`risk_rating` is never the source of `beta_250`.** It is a 1–5 bin, NULL on 84.4% of rows.
5. **No accusatory vocabulary** — no wording implying intent, wrongdoing or market abuse — in any
   emitted string, log line or report. The condition is a realised return, nothing more. Enforced
   mechanically: `selfcheck_pump_flag.py::g_language` greps this file and `FINDINGS.md` against a
   banned-substring list and fails the run on a hit. (It fired on an earlier draft of this very
   line, which spelled the banned words out in order to forbid them.)

## 4. Message template

```
PRHM: {ticker} raised cash (RIGHTS/PP) on {exright_date}, after a {pretrend:+.0%} 250-session
excess return vs VNINDEX ({pretrend_bucket}); beta {beta:.2f} ({beta_bucket});
{raise_count_3y} cash raise(s) in 3Y{sector_clause}.
Base rates (2010-2026, 590 raises / 312 companies): 1Y abnormal return averages -7% to -9%
REGARDLESS of the pre-raise run-up — the run-up does NOT separate outcomes at 1Y (NO-FLAG).
~29% of high-run-up raisers have healthy ROIC and F-score. Informational only; not a gate.
```

`{sector_clause}` = `"; securities firms raise ~1.5x as often as other sectors"` when
`sector_raise_intensity == elevated`, else empty.

Worked example (synthetic, illustrative field values):

```
PRHM: XYZ raised cash (RIGHTS/PP) on 2026-07-15, after a +94% 250-session excess return vs
VNINDEX (high); beta 1.43 (elevated); 2 cash raise(s) in 3Y; securities firms raise ~1.5x as
often as other sectors.
Base rates (2010-2026, 590 raises / 312 companies): 1Y abnormal return averages -7% to -9%
REGARDLESS of the pre-raise run-up — the run-up does NOT separate outcomes at 1Y (NO-FLAG).
~29% of high-run-up raisers have healthy ROIC and F-score. Informational only; not a gate.
```

**The base-rate sentence is mandatory and may not be trimmed for brevity.** Without it a reader sees
"+94%, high" next to a raise and supplies the conclusion the data refused to support. The disclosure
of the flag's own weakness is the most load-bearing line in the message.

## 5. False positives — the number to quote

**≈29% at every threshold tested** (26.7–28.3% using within-year medians), where "false positive" is
the dispatch's definition: flagged, yet trailing ROIC above the sample median **and** Piotroski
F-score above 4. Stable across T = 15% … 60%, so raising the bar buys nothing — it shrinks the
flagged group without improving its purity.

Two further error modes not in that number:

- **Discrimination failure.** The dominant error is not that ~29% look healthy; it is that the other
  ~71% *also* return about the same as unflagged raises at 1Y. The flag's precision problem is
  secondary to its having no measured 1Y signal at all.
- **Sector base rate.** For a brokerage, `pretrend` averages +83% versus +42% elsewhere, so a fixed
  threshold flags brokerages far more often without evidence they do worse (−6.1% vs −7.7%, CI spans
  zero). Any future threshold applied to ICB 8777 should be sector-relative, or the flag is mostly a
  sector detector.

## 6. Deliberately excluded from this spec

| Excluded | Why |
|---|---|
| A 1Y return prediction or any implied direction | `NO-FLAG`; every CI spans zero |
| A hard block, sizing haircut, or score adjustment | Would assert an edge that was tested for and not found |
| `risk_rating.Beta` as the beta source | Integer 1–5 bin, NULL on 84.4% of rows (deviation D-B1) |
| The `pretrend > T AND beta > 1.8` combined cut | n = 8 events / 7 tickers; declared underpowered before it was computed |
| A securities-sector penalty | 26 companies, below the preregistered verdict floor; outcome gap is +1.6pp with a CI spanning zero |
| The 2Y/3Y result (−23.5pp / −33.1pp at T=60%) | Real, monotone, IS/OOS-robust — but 3Y was preregistered as *context*, not the decision horizon. Needs its own prereg, and a holding period this book does not have |

## 7. If someone later wants to wire the long-horizon version

Required before it is even a candidate, per this fleet's standing rules — not optional steps:

1. A **fresh preregistration** with 3Y as the primary horizon, written before re-running anything.
2. **DSR and PBO** on the NAV of the configuration proposed for deployment; DSR < 0.95 is a red
   flag. Declare N trials including the 11 already spent here.
3. **quant-skeptic gate.** `REFUTED` / `INCONCLUSIVE` = do not wire.
4. An answer to the holding-period question: a 3-year abnormal return is not tradable by a book that
   rebalances monthly. If the answer is "avoid these names for 3 years", that is an **exclusion
   list** design, not a signal — and it needs its own cost accounting.
5. Resolution of the reversal confound (prior program §2.1) — pre-trend +45.5%, far placebo +30.2%
   mean the underperformance still cannot be separated from reversal of the run-up.

## 8. Provenance

Evidence `FINDINGS.md` · design `PREREG.md` (locked `4835d3f2`) · deviations `DEVIATIONS.md` ·
numbers `out/results.json` · 55/55 selfcheck under three timezones (`out/selfcheck.json`) ·
built on `serial_capital_raiser_20260817` (`ec3fd8d2`), whose three published headline numbers this
program reproduces to 5 decimal places before computing anything of its own.
