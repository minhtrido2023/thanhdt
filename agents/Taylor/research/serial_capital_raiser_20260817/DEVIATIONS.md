# DEVIATIONS from PREREG.md

Job `Taylor_20260817_075412`. Prereg committed at `eccab390` before any outcome was computed.
Everything below either departs from that document or was added after seeing results. Nothing here
replaces a preregistered primary — the primaries all ran as written and are reported in FINDINGS §2–4.

---

## D1 — control variables substituted (before outcomes)

**Prereg said:** controls = `ln(ADV60)`, `ROE_Trailing`, `Debt_Eq_P0`, `Revenue_YoY_P0`.

**Actual:** `ln(ADV60)`, `ROIC_Trailing`, `NPM_P0`, `FSCORE`, `Debt_Eq_P0`.

**Why:** `ROE_Trailing` and `Revenue_YoY_P0` **do not exist in `tav2_bq.ticker`** — they live in
`ticker_financial`. Caught by a `--dry_run` before any data was pulled, so this deviation is
pre-outcome. The alternative was joining `ticker_financial` on a second key, whose PIT semantics I
have not audited for this use; adding an unaudited join to fix a control variable is a worse trade
than substituting same-table columns whose basis is already verified. `ROIC_Trailing` is the nearest
trailing-4Q profitability measure available in the same table; `NPM_P0` and `FSCORE` cover margin and
the quality/growth axis `Revenue_YoY_P0` was there for.

**Impact:** none on the primary sign or significance — §3.1 shows the raw medians move the same way
as the regression, so the result is not resting on a particular control set.

## D2 — winsorised variant added (post-outcome, additive)

Prereg specified raw yields. Because `ey = 1/PE` is unbounded below a small positive PE, a 1/99
per-month winsorised variant was added. **The raw specification remains the primary as written.** Both
agree in sign and significance; reported in `out/results.json` under `q2a_winsor_primary`.

## D3 — R1: pre-trend conditioning (post-outcome)

**Trigger:** the preregistered far placebo came back **+30.21%, CI [+20.71%, +40.78%]** — significant.
PREREG §3 committed that this forces a downgrade, and it did: Q1's verdict is RISK/DESCRIPTIVE, not a
causal issuance effect. But "downgrade" alone would leave unanswered *how much* of the effect is
reversal, which is the first thing any reader will ask.

**Added:** (a) BHAR by pre-trend quartile; (b) a pooled regression of `BHAR_250` on a cash-raise
dummy alongside the pre-trend, `ln(ADV)`, realised vol and year FE, SE two-way clustered.

**Explicitly post-hoc.** The `is_raise = −5.49% (t=−2.17)` coefficient is a descriptive
decomposition, not a preregistered test, and is labelled as such in FINDINGS §2.1. A properly
prior-return-matched control design was **not** attempted — that is a different study, not a
robustness check, and inventing it after seeing the placebo would be exactly the drift this program's
discipline exists to prevent.

## D4 — R2/R3/R4: size matching, ADV floor, unmatched levels (post-outcome)

**Trigger:** the preregistered Q2b spread came in at ~−10%/yr. A number that large has to be checked
against the possibility that it lives entirely in names this book cannot trade, and against the
possibility that "value-matched" is doing nothing.

**Added:** (R2) 16 specifications crossing sort variable × size-tercile matching × the production
`ADV ≥ 2bn` gate from `lag_liquidity_filter.py`; (R3) unmatched leg levels and median multiples;
(R4) the Q2a regression re-run on the ADV ≥ 2bn slice.

**This deviation cut against the finding, which is the point of running it.** The most demanding
cells (size-matched + liquidity floor) are directionally consistent but lose significance, and the
`by`-sorted version dies outright (t=−1.04, p=.273). Reported in FINDINGS §4.1 rather than buried.

## D5 — IS/OOS at all three horizons (post-outcome, additive)

Prereg specified IS/OOS splits **on the primary horizon only**. Added for 500 and 750 after the
primary's OOS came back insignificant, because reporting only the split that fails would misstate the
picture in the opposite direction — the 3-year horizon holds in both halves (OOS −23.89%, p<.0001)
while the 1-year does not. Both facts are in FINDINGS §2.2.

## D6 — `listing_date` is not 100% NULL (documentation correction, no impact)

`corp_action_program_20260815/DATA_DICTIONARY.md` records `listing_date` as "100% NULL toàn bảng".
Measured 2026-08-17 on executed ISS rows it is populated on the large majority (e.g. RIGHTS
1,543/1,570; PRIVATE_PLACEMENT 2,249/2,280). The dictionary line is either stale or was scoped to a
different slice. **No impact here** — this program anchors exclusively on `exright_date` — but the
predecessor's dictionary should be corrected, since Sprint 4's AIS panel did anchor on `listing_date`
and a reader comparing the two documents would conclude one of them is impossible.

---

## Two selfcheck tests were wrong and were fixed — with the reason recorded

Both failed on the first run. In both cases the analysis was correct and **the test was the defect**
(corp-action ledger E1: the first hypothesis on a selfcheck FAIL is "I wrote the test wrong").

### T1c — flagged the rule being documented as a violation of the rule

`T1c` scans the source for a `Price/Close` expression (registry bẫy (4): building that ratio injects
look-ahead). It failed on `analyze.py:85`, which is the **comment** `# ... never rescaled by
Price/Close`. Fixed by scanning with comment tails stripped.

Deliberately **not** fixed by stripping string literals: the BigQuery SQL lives inside triple-quoted
f-strings and that SQL is precisely where a mixed-basis expression would hide. A helper that blanked
strings would have made T1c and T1d pass by going blind — a worse outcome than the false positive it
was fixing. The helper's docstring says so, so nobody "simplifies" it later.

### T5a — asserted something false about a quality universe

`T5a` distinguishes a per-day universe gate from a static list. It originally asserted that **no**
ticker is present in all 197 months, and failed on 41. Those 41 are the VN long-listed large caps —
ACB, CTG, FPT, MSN, PVD, REE, SSI, STB, VCB, VIC, VNM and similar — 4.6% of the 895 tickers. A
quality screen that dropped every one of them at some point would be the broken thing. The assertion
was simply wrong.

Fixed to test what actually separates the two cases: membership **varies** (<20% of tickers present
in every month; median ticker present 57 of 197 months; the per-month name count moves). The
independent `[BQ]` test T5b — 660 real tickers flip `in_universe` between 2015 and 2025 — was already
proving the gate is per-day and passed throughout.

Final state: **28/28 PASS**, identical under `env -u TZ` and `TZ=America/Chicago`.

---

## Preregistered items NOT executed, and why

| Item | Status |
|---|---|
| `self-check 0 VND` | **Not applicable, declared in advance** (PREREG §6). No NAV path and no execution exists in this program — Q2b is a return-spread series, not a capital path. The substituted discipline (independent recompute by a separate code path, T7a/T7b, both matching to <1e-9) was executed. |
| DSR / PBO | **Not computed, declared in advance** (PREREG §5). Gate for selecting a config to deploy; nothing here is proposed for deployment. Becomes mandatory if anyone revives the `ey` spread as a screen. |
| Regime subsample split | **Not attempted, declared in advance** (PREREG §4 falsification 4). Month FE is the regime control; DT5G-era tables cover a shorter span and would confound the test. |
