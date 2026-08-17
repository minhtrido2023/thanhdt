# Deviations from `PREREG.md` (locked `4835d3f2`)

Every departure from the locked design, with what it changed. None of them alters the Mục 1 verdict,
which is `NO-FLAG` under the rule exactly as written.

---

## D-B1 — beta source: `risk_rating.Beta` demoted to a cross-check

**Declared IN the prereg, before any outcome** — recorded here too so the list is complete.

The dispatch asked for beta cuts at 1.2 / 1.8 from `tav2_bq.risk_rating`. That column cannot carry
them: it is an integer **1–5 bin** (`SSI` = 5.0 in every quarter since 2025Q2), not a coefficient,
and is NULL on **99,047 of 117,390 rows (84.4%)**. "≤1.2" applied to it would have silently meant
"bin 1 only".

**Instead:** primary beta is a self-computed 250-session OLS coefficient vs VNINDEX over
`[t0−250, t0−1]`, requiring ≥150 overlapping sessions (coverage 93.8% of events). `risk_rating.Beta`
is reported as a secondary cross-check on its own 1–2 / 3 / 4–5 scale (coverage 67.3% of events).

**Effect:** the dispatched cut points became applicable at all. The two measures agree — correlation
+0.55, and both produce the same monotone ordering — so the cross-check is corroboration rather than
a substitute.

---

## D-1 — AUCTION reported as a sensitivity, not folded into the primary

The dispatch named "RIGHTS + PRIVATE_PLACEMENT (RAISE_SET từ scr_lib.py)", but the prior program's
`RAISE_SET` also contains `AUCTION` (n=23, below that program's own N=200 reporting floor).

**Resolution:** primary population = the two subtypes named literally (590 events / 312 tickers);
`RAISE_SET` including AUCTION reported as a declared sensitivity (608 / 321).

**Effect:** none on the verdict. Both return `NO-FLAG`; the sensitivity's gaps are −0.3pp to −3.6pp,
all Holm p = 1.000.

---

## D-2 — CIs and p-values added to the preregistered 2Y/3Y "context" gaps

PREREG §2 committed to *reporting* the 500/750-session gaps "for context" but specified only the
point estimate.

**Change:** the block-bootstrap CI and p are computed for them as well, Holm-adjusted **within each
horizon's own family of 7** and never pooled with the h=250 family. The IS/OOS split and sample
attrition for those horizons are reported alongside.

**Why:** a bare point estimate with no CI invites exactly the over-reading this program exists to
prevent — and in this case the omission would have cut the other way, hiding that the long-horizon
gaps are large, monotone in T and IS/OOS-robust while the preregistered 1Y gaps are nothing.

**Effect on the verdict: none.** The selection rule keys on h=250 exactly as preregistered, and
`FINDINGS.md` §2.1 labels the long-horizon result a hypothesis requiring its own preregistration —
not a validated flag. It is excluded from `FLAG_SPEC.md`'s recommendation for that reason.

---

## D-3 — stability tests added to Mục 3, and the two upper beta bins merged

PREREG §4 fixed the three beta bins but specified no stability test for them, while the fleet's
standing bar is `Edge rớt OOS = loại`.

**Change (a):** IS/OOS split and leave-one-year-out run on the beta result. It can only weaken a
claim, never create one — and it did weaken it: OOS −8.4pp p=.20 (insignificant), 2010 carrying
50.1% of the high-beta leg. That is why `FLAG_SPEC.md` says risk marker, not return predictor.

**Change (b):** the dispatched `high` bin (β>1.8) holds 31 events / 24 tickers and is below the
declared power floor, so the powered version of the same ordering merges the two **preregistered
adjacent** bins into `β > 1.2` (236 / 146). This is a regrouping of preregistered bins, not a new
cut point searched for after the fact; the original three-bin table is reported in full alongside.

**Change (c):** descriptive covariates per bin (ADV, realised vol, ROIC, PE, sector mix) added so
the confounds are stated rather than left implicit. Descriptive only, no test attached.

---

## D-4 — Mục 3 runs on a wider population than Mục 1 (646 vs 590)

Not a design change, but it was not written down in advance and is worth stating: Mục 1 requires
both a pre-trend and a 1Y outcome (590 events); Mục 3 tests beta against the outcome and does not
need a pre-trend, so it keeps the 56 events whose pre-trend is missing (646). The combined cut still
excludes them, because `NaN > T` is False.

Both counts are now recorded in `out/results.json` (`muc3.n_population`, `muc3.n_population_muc1`)
and a selfcheck asserts the difference is *exactly* the missing-pre-trend events, so a future edit
cannot widen the gap unnoticed.

---

## Non-deviations worth recording

- **`build_extras.py` keys on `(ticker, t0)`, not `(ticker, t0, subtype)`.** The first attempt
  returned 3,246 rows against the prior panel's 2,953. Cause: that panel's final `GROUP BY ticker,
  t0` collapses a ticker with two different ISS subtypes on one ex-date into one row. Keying on
  subtype fanned the joins out. Corrected before any outcome was computed; CC5 now asserts the key
  sets are identical, and `subtype` is taken from the prior panel at merge time, never from the new
  pull.
- **`selfcheck_pump_flag.py` loads `analyze.py` by absolute path.** Both this program and the prior
  one have a module named `analyze`, and `sys.path` order decided which one `import analyze`
  resolved to — the selfcheck was briefly testing the wrong module. Now loaded via
  `importlib.util.spec_from_file_location`, so the name cannot resolve elsewhere.
- **No wiring, no `trading_rules.json` change, no cron, no announcement study** — all four were out
  of scope in the dispatch and remain untouched.
