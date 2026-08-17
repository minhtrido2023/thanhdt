# `corporate_action.listing_date` — semantic gate for an exchange-notification study

Job `Taylor_20260817_112844`, 2026-08-17. Step 1 of the dispatch (semantic gate). Rebuild:
`python3 gate_build.py`. Selfcheck **33/33 PASS** (`selfcheck_gate.py`, offline, recomputes every
number below from `out/*.csv`).

---

## Answer first

| Question | Answer |
|---|---|
| Is `listing_date` 100% NULL, as `DATA_DICTIONARY.md` line 47 claims? | **No.** It is NULL on every event family *except* `ISS`, where **9.594 / 11.722 (81,8%)** rows carry it. The Sprint-1 line is wrong. |
| Is `listing_date` the date the issuer notified the exchange? | **No.** It is the date the **newly issued shares are listed for trading** (niêm yết bổ sung) — a *post*-event date. |
| **GATE verdict** | **FAIL.** Both criteria fail, and not marginally: required median gap ∈ [5, 20] days, actual **−91**; required ≥70% of events with gap ∈ [3, 30], actual **1 event out of 1.542 (0,06%)**. |
| Consequence | **Step 2 not run**, per the dispatch's own stop rule. No PREREG, no event study. |

The hypothesis was reasonable — HOSE/HNX rules do require notice ≥5 working days before the record
date, so *some* column ought to carry that date. This one does not, and the fallback is not "use it
anyway with caveats": see §4, the field is unusable as an anchor for a different and more serious
reason than being the wrong date.

---

## 1. Sign convention

Throughout, **`gap = exright_date − listing_date`**, in calendar days — the dispatch's convention.

- `gap > 0` ⇒ `listing_date` **precedes** the ex-date. This is what the notification hypothesis
  predicts (+7 to +15 days).
- `gap < 0` ⇒ `listing_date` **follows** the ex-date.

## 2. Fill rate — the DATA_DICTIONARY correction (`out/m1_fill_by_event_code.csv`)

| `event_code` | n | with `listing_date` | % |
|---|---:|---:|---:|
| `ISS` | 11.722 | 9.594 | **81,8%** |
| `DIV` | 17.072 | 0 | 0,0% |
| `AIS` | 4.884 | 0 | 0,0% |
| `NLIS` · `SUSP` · `MOVE` · `MA` | 2.498 | 0 | 0,0% |

The Sprint-1 claim was presumably measured across the whole table, where `ISS` is a minority and
`DIV` alone is 47% of rows. It is a **false negative about data that exists**, which is the
expensive direction — it kept a populated field out of consideration for two days.

## 3. Gap distribution — the gate (`out/m2_gap_by_subtype.csv`)

Deduplicated events (survivor rule identical to `sprint4_build.py`), `event_status='executed'`.
**N is declared as independent issuers**, not rows.

| subtype | events | issuers | gap>0 | gap=0 | gap<0 | gap ∈ [3,30] | p25 | **median** | p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **RIGHTS** | 1.569 | **794** | 11 | 448 | **1.083** | **1 (0,06%)** | −125 | **−91** | 0 |
| PRIVATE_PLACEMENT | 2.280 | 884 | 14 | 1.552 | 680 | 3 (0,1%) | −52 | 0 | 0 |
| STOCK_DIVIDEND | 2.338 | 746 | 11 | 313 | 1.972 | 5 (0,2%) | −66 | −50 | −37 |
| BONUS | 1.378 | 650 | 12 | 286 | 1.058 | 3 (0,2%) | −65 | −49 | −30 |
| ESOP | 1.220 | 517 | 10 | 317 | 871 | 1 (0,1%) | −371 | −96 | 0 |

**Gate arithmetic (RIGHTS):** median −91 ∉ [5, 20] ⇒ FAIL. 0,06% < 70% ⇒ FAIL. Locked by
selfcheck T4–T8; T7 recomputes the verdict from the thresholds rather than trusting this prose.

Two readings to head off:

- **PP's median of 0 is not "same-day listing."** 1.552 of 2.246 PP events (69%) carry the
  degenerate value `listing_date == exright_date` — see §5. Selfcheck T10.
- The 20-event manual sample (`out/m4_sample20.csv`, deterministic `FARM_FINGERPRINT` pick, not
  `RAND()`) was drawn on **|gap|** in [5,15] and >30 so both strata could be inspected by hand.
  **All 20 came back negative** — the smallest listing lag in the whole sample is GGG at 5 days
  after the ex-date, the largest TTB/QBS/BGM at ~368 days. Selfcheck T15.

## 4. What `listing_date` actually is (`out/m3_ais_match.csv`, `out/m7_ais_match_scoped.csv`)

`AIS` = "Niêm yết bổ sung" (additional listing), whose `effective_date` the data registry already
documents as *"ngày CP mới CHÍNH THỨC vào lưu hành"*. Hypothesis: `ISS.listing_date` is that same
quantity, carried on the issuance row.

**n=1 check, the registry's own worked example.** FPT bonus 15% 2025: `ISS.exright_date =
2025-07-21`, `ISS.listing_date = 2025-09-12`, and the matching `AIS.effective_date = 2025-09-12`.
Exact. The ~7-week lag the registry documents as an `AIS` trap is visible *inside the ISS row*.

**At scale.** `AIS` coverage is thin (4.884 rows vs 9.594 ISS rows carrying a `listing_date`), so a
raw mismatch often just means no `AIS` row exists. Conditioning on the ticker having *some* `AIS`
row within ±365 days of `listing_date`, and running the identical test on `exright_date` as a
placebo:

| subtype | scoped n | `listing_date` matches AIS | `exright_date` matches (placebo) |
|---|---:|---:|---:|
| STOCK_DIVIDEND | 1.788 | **90,9%** | 0,1% |
| BONUS | 917 | **90,7%** | 0,3% |
| PRIVATE_PLACEMENT | 649 | **84,9%** | 5,2% |
| ESOP | 796 | **74,1%** | 8,3% |
| **RIGHTS** | 844 | **65,9%** | **0,1%** |

For RIGHTS the discrimination is ~660×. Exact-match and ±3-day-window rates agree within 1pp on
every subtype (selfcheck T13), so these are the *same field*, not two dates that merely cluster.
Scoping raises the match rate everywhere versus unscoped (T12), confirming the scope filter selects
on data availability rather than on the outcome.

**⚠️ This makes `listing_date` unusable as an event anchor even for post-event windows.** It is not
merely the wrong date — it is a *realised outcome of the raise itself*. How many days after the
ex-date the new shares list depends on how fast the issuer collected subscription money and cleared
the additional-listing filing, which is not knowable on `exright_date`. Anchoring returns on it
conditions the sample on something resolved in the future. Anyone reaching for this column later
should treat that, not the failed gate, as the binding objection.

## 5. The `listing_date == exright_date` mass is a vendor artifact (`out/m5_zero_gap_by_year.csv`)

RIGHTS events where the two dates are identical, by ex-date year:

| era | share |
|---|---:|
| 2002–2008 | 72,3% (avg) |
| 2015–2018 | 24,5% → 27,7% |
| 2021 | 11,4% |
| 2023 · 2025 · 2026 | **0,0%** |

A monotone decay to zero as vendor data quality improves. Under the notification hypothesis a zero
gap is *impossible* (notice must precede the record date by ≥5 working days); under the
additional-listing reading it is an obvious fallback — copy the ex-date when the true listing date
was never captured. Practical consequence: **`listing_date` is least trustworthy the further back
you go**, the opposite of what a long-history study needs. Selfcheck T19.

## 6. The evidence *for* the hypothesis, stated fairly (`out/m6_listing_before_ex.csv`)

Only **11 of 1.542** RIGHTS events have `listing_date` strictly before `exright_date`, and they do
not look like notifications either — gaps of 186, 212, 218, 205, 284, 436 days dominate. Exactly
**one** RIGHTS event falls in a notice-like 3–30 day window (`DTA`, 2011-03-23, gap 9), plus `HAS`
2004 at 2 days. Two events out of 1.542 is noise, not a signal, and both sit in the era where §5
shows the field is least reliable. Selfcheck T17–T18.

## 7. Verdict and what it does *not* say

**GATE: FAIL. Step 2 not run.** Nothing was preregistered and no outcome was examined — the stop
rule fired before any return was computed, which is the point of having it.

This does **not** reopen the announcement study by another route. `public_date` remains banned
(`WEAK_UNVERIFIED_VINTAGE`, Sprint 1 §5) and this job found no substitute: the corp-action table
carries **no column that records when the market first learned of an event**. The three candidates
are now all excluded on measured grounds — `public_date` (overwritten in place, no vintage),
`id_created_date` (89,4% = the 2024-10-11 backfill date), and now `listing_date` (post-event
outcome). The path to an announcement study is unchanged and still slow: accumulate daily vintages
in `tav2_mike.corporate_action_snapshots` (live since 2026-08-17) and re-measure N no earlier than
**2027-08**.

## 8. Follow-up filed

`DATA_DICTIONARY.md` line 47 corrected on branch `session/1538146805207011358` — it now records the
81,8% ISS fill rate and the additional-listing semantic, so the next reader does not re-run this
investigation. This closes the item carried in Taylor working memory since job
`Taylor_20260817_075412`.

---

### Artifacts

| file | contents |
|---|---|
| `gate_build.py` | all 7 measurements, read-only SQL, dumps to `out/` |
| `selfcheck_gate.py` | 33 offline checks recomputing this report from `out/*.csv` |
| `out/m1_fill_by_event_code.csv` | §2 fill rates |
| `out/m2_gap_by_subtype.csv` | §3 gap distribution — the gate |
| `out/m3_ais_match.csv` · `out/m7_ais_match_scoped.csv` | §4 semantic identification + placebo |
| `out/m4_sample20.csv` | §3 the 20 hand-checkable events |
| `out/m5_zero_gap_by_year.csv` | §5 zero-gap decay |
| `out/m6_listing_before_ex.csv` | §6 all 25 RIGHTS/PP events with `listing_date` before ex-date |
| `sql/*.sql` | exact SQL as executed |
