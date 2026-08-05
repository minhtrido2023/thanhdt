---
name: stock-valuation-report
description: Use whenever the user asks about a specific VN stock ticker for informational/research purposes — "mã X ổn không", "làm due diligence cho X", typing a bare 3-letter ticker code, or asking for valuation/DCF/fair-value on a name. Produces a 4-part report (valuation vs history, quarterly result/forecast, DCF with router-selected method, assessment). This is RESEARCH/DISCUSSION due diligence, not `trade-due-diligence` (that skill is the mechanical red-flag override checklist for live BUY orders in V2.4 — different mechanism, different audience, do not conflate). Built from a real multi-week thread of single-ticker reports (TTN, HPG, PNJ, DRI, GMD, FPT, TV1, DGC, PVT, DHC) where the same mistakes recurred until this checklist existed.
---

# Single-Ticker Valuation Report — Due-Diligence Checklist

A fixed workflow for answering "is ticker X okay / what's it worth" with real BQ data + real
DCF, not narrative impression. Every step below exists because skipping it produced a wrong
number or a wrong conclusion in a real report in this thread — see the incident cited.

## When NOT this skill
- Deciding whether to override a red flag on an actual `PlannedOrder` in V2.4 → `trade-due-diligence`.
- Designing/backtesting a new signal or production rule → `quant-research`.
- This skill is for: "what does the market data say about this specific company right now."

## The report has 4 parts, in this order

1. **Định giá hiện tại** — PE/PB/PCF/EV-EBITDA/DY vs own 5-year history (PE_MA5Y/PB_MA5Y ± SD),
   ROE/ROIC, leverage, technicals (MA50/MA200/RSI/CMF).
2. **KQKD quý gần nhất / dự báo quý tới** — real reported numbers first; only forecast if the
   quarter hasn't landed yet, and say so explicitly.
3. **DCF** — method chosen per the router (below), 3 scenarios (bear/base/bull) with WACC and
   growth stated, never a single point estimate.
4. **Nhận định** — synthesis: what's genuinely good, what's a real risk, a stance (not a hedge).

## Step 0 — read the router first, every time, before touching numbers

`mike/agents/Taylor/valuation_methodology_router.md` is the accumulated, measured methodology —
don't re-derive WACC/beta/method choice from scratch. Its 4-step sequence:

```
B1. Tier (mcap + ADV) → beta range → WACC range   [router §1]
B2. CF_OA vs NP, TTM, vs industry base rate → can this ticker's DCF be trusted?   [router §2]
B3. ICB → which valuation method (this ticker's industry may forbid raw FCF-DCF)   [router §3]
B4. WACC checklist, esp. the double-count check   [router §4]
```

If B2 fails (or "just barely passes," e.g. CF_OA/NP ≈ 1.0x with recent quarters below 1.0x —
DHC, 2026-08-05), don't present DCF as the headline number without flagging why.

## Step 1 — pull the real beta and industry method, don't recompute by hand

- Beta: `grep "^TICKER," mike/agents/Taylor/data_beta_universe.csv` — real regression beta (5y
  and 3y, with t-stat/R²), not `risk_rating.Beta` (that's a 1-5 bin, router §1.1 — plugging it
  into CAPM understates fair value by ~2x, caught on FPT 2026-07-21).
- Size/liquidity premium: keyed to **ADV** (`Volume_3M_P50 × Price`), not market cap — a "size
  premium" measured against market cap turned out to be entirely an illiquidity effect once
  properly controlled (router §1.2b, job `Taylor_20260721_112050`, corrected same-day after an
  initial wrong finding). Don't resurrect a size-based premium table.

## Step 2 — pull BQ data with the query templates below, verify units before trusting them

```sql
-- valuation + technicals, last 5 sessions
SELECT t.ticker, t.time, t.Close, t.Volume, t.Volume_3M_P50, t.PE, t.PB, t.PCF, t.EVEB, t.DY,
       t.ROE5Y, t.ROIC5Y, t.FSCORE, t.Risk_Rating, t.ICB_Code, t.Debt_Eq_P0, t.NPM_P0, t.OShares,
       t.PE_MA5Y, t.PE_SD5Y, t.PB_MA5Y, t.PB_SD5Y, t.MA50, t.MA200, t.D_RSI, t.D_CMF
FROM tav2_bq.ticker AS t WHERE t.ticker = "TICKER" ORDER BY t.time DESC LIMIT 5;

-- quarterly history, 8 quarters
SELECT f.ticker, f.quarter, f.time, f.Release_Date, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_P4,
       f.Revenue_YoY_P0, f.GPM_P0, f.NPM_P0, f.ROE_Trailing, f.Debt_Eq_P0, f.CF_OA_P0,
       f.CF_Invest_P0, f.FSCORE, f.PE, f.PB
FROM tav2_bq.ticker_financial AS f WHERE f.ticker = "TICKER" ORDER BY f.time DESC LIMIT 8;

-- DCF inputs, latest quarter
SELECT f.ticker, f.quarter, f.time, f.OShares, f.EPS_P0, f.BVPS, f.Cash_P0, f.StDebt_P0,
       f.LtDebt_P0, f.totalAsset_P0, f.CF_OA_P0, f.CF_OA_3Y, f.CF_OA_5Y, f.CF_Invest_P0,
       f.CF_Invest_3Y, f.CF_Invest_5Y, f.EBITDA_P0, f.NP_P0
FROM tav2_bq.ticker_financial AS f WHERE f.ticker = "TICKER" ORDER BY f.time DESC LIMIT 1;
```

Three unit/staleness traps, each one a real wrong number in this thread before the fix:

- **Market cap = `Price × OShares`, never `Close × OShares`.** `Close` is dividend/split-adjusted;
  multiplying it by *current* share count silently shrinks historical market cap for high-dividend
  names (router §1.2, discovered while re-deriving a "size premium" that turned out to be a
  dividend-adjustment artifact).
- **`OShares` in `ticker_financial` only updates on the next quarterly filing** — if the company
  did a stock dividend/private placement between filings, that field is stale until the next
  release. Use `ticker.OShares` (or `ticker_1m`, same schema) which updates daily and already
  reflects the change. Real case: PVT issued a 10% stock dividend 2026-06-08 (469.9M→516.9M
  shares); `ticker_financial.OShares` still said 469.9M weeks later, producing a market cap ~10%
  too low and a DCF-per-share ~10% too high, until caught by the user (2026-07-26).
- **A "2026Q2" row in `ticker_financial` can be a stale carry-forward, not a real new filing.**
  Check `Release_Date` — if it's identical to the prior quarter's release date and every financial
  field is byte-identical, no new report has landed yet (TV1, checked 2026-08-04: the "Q2" row
  was Q1 data re-labeled by the table's own rolling-quarter logic). Cross-check against a web
  search for the actual filing before reporting a quarter as "released."

## Step 3 — CF_OA ≥ NP test, TTM not one quarter, vs industry base rate

Sum CF_OA and NP over the last 4 quarters (not one quarter — ~49% of VN companies post negative
CF_OA in Q1 alone from post-Tết working-capital timing; a one-quarter read flags clean companies
as dirty, router §2.2, caught on FPT). Compare the ratio against the industry base rate, not a
flat 50% (utilities ~0.65, financial services ~0.31 — router §2.3).

**Don't stop at "does it pass" — read *why* it's high or low:**
- TTM CF_OA ≫ NP (PVT: 2.9x, TV1: consistently ≥1x every quarter) → mature/low-capex asset,
  D&A add-back dominates, FCF-DCF is trustworthy as the primary anchor.
- TTM CF_OA ≈ NP with recent quarters *below* 1.0x, alongside a visible capex ramp in
  `CF_Invest_P0` (DHC 2026Q2: capex ~10x the 3-year average) → **not automatically bad** — read
  it as active capacity expansion, then apply Step 4's method choice, don't just flag it dirty.
- TTM CF_OA ≪ NP with no clear one-off explanation (DGC 2026Q1) → investigate before trusting
  any DCF off this name; could be one-time (verify against next quarter) or structural.

## Step 4 — pick the valuation method BEFORE running one DCF and believing it

Capex-heavy, growth-phase businesses (ports/infra mid-expansion like GMD's Gemalink Phase 2,
shipping lines actively buying vessels like PVT, manufacturers ramping capacity like DHC) will
show a **naive FCF-DCF that's wildly more bearish than an earnings-power (NP-based, discounted at
cost of equity) DCF** — sometimes the FCF-DCF goes negative-fair-value while the market and
earnings-power model both say the stock is cheap. This is not a contradiction to average away;
it means growth capex is being double-counted as a permanent recurring drag. When TTM FCF is
persistently negative/small alongside heavy `CF_Invest_P0` relative to the 3-5y average, run
**both**, show the gap explicitly, and default to earnings-power as the primary read (GMD
2026-07-16, PVT 2026-07-26, DHC 2026-08-05 all hit this; router §3 has the fuller framework by
ICB code, including banks — never FCF-DCF, use P/B or residual income instead).

For a mature, low-capex, cash-generative asset (a paid-off hydro plant, a stable service
business), the reverse caution applies: don't automatically credit 100% of retained earnings as
shareholder value — TV1's full-FCF DCF (40k-140k) vs dividend-only DDM (12k-19k) gap *is* the
capital-stewardship question the market is actually pricing; state both and say which one you
trust and why (governance track record, actual payout history), don't just average them.

## Step 5 — WACC checklist (router §4), the double-count check specifically

State Rf, beta (from Step 1, not a guessed number), ERP, and any illiquidity/size premium
separately. Then ask explicitly: **did a qualitative risk (e.g. "AI could disrupt this
business") get built into the growth path AND into WACC?** Doing both is double-counting the
same risk twice, and it was the single largest source of an over-conservative fair value in
this thread (FPT, 2026-07-21: base-case fair value moved from 48,700 to ~85,000-100,000 — closer
to sell-side consensus — purely by fixing a beta assumption that had baked the same AI-risk
narrative into both the discount rate and the growth rate simultaneously). Show a WACC
sensitivity table (±1-2pp) in the report; don't hide how much the "fair value" number is riding
on one assumption.

## Step 6 — for scandal/event-driven names, don't stop at market data — verify the actual claim

When the trigger is a legal/governance event (chairman arrested, audit refused, environmental
violation), the market-data steps above are necessary but not sufficient — the report has been
wrong in both directions in this thread from skipping this:
- **Verify quantified damage vs. remediation amount from primary reporting**, don't take a
  Discord/user paraphrase at face value in either direction — TV1's actual state damage ("hàng
  chục tỷ") vs voluntary repayment (331.3 tỷ) was a real, checkable fact that meaningfully
  changed the read once verified (2026-07-17), and separately the "all 4 Big4 refused audit"
  framing turned out to conflate an *already-audited* FY2025 with a *forward* FY2026 vote — two
  different fiscal years, verify which one any given audit-refusal headline is about (router-
  adjacent lesson, `calculated_fear_state_backstop.md` §10.8).
- **Ask whether the event touched the core operating asset or only individuals separate from
  it** — this is the single most decisive discriminator measured in this thread (§10.1 of
  `calculated_fear_state_backstop.md`): TV1's hydro plant never stopped generating power through
  its chairman's arrest (QUALIFY); DGC's actual apatite mine was suspended "to support the
  investigation," directly raising production costs the following quarter (downgrade toward
  NON) — confirmed only by reading the Q2 earnings release, not by re-reading the original
  indictment. Always run this test again once a new quarter's real numbers land; don't let an
  early verdict fossilize.
- **Cite every web-search claim with its source URL** in the final report — a claim about legal
  proceedings, remediation amounts, or ownership structure is exactly the kind of fact that gets
  corrected later; sourcing lets the next read verify or update it.
- For anything genuinely novel/deep on this axis (SOTP asset-by-asset valuation, quality-of-
  earnings one-time-vs-structural split, solvency-through-crisis check), open
  `mike/agents/Taylor/research/calculated_fear_state_backstop.md` §10 — it's the fuller
  qualitative checklist this skill's Step 6 summarizes; don't re-derive it inline in a report.

## Step 7 — same-day data discipline

BQ syncs overnight (`sync_bq_cache_daily.sh`, ~23:45 ICT) — a same-day price move or an
after-hours earnings release will not be in BQ yet. State the as-of date of every BQ number
explicitly, and when the user references "today," check whether BQ's latest row is actually
today or the prior session before treating it as current (caught mid-report, LPB 2026-07-31:
BQ's newest row was one day stale, and separately the web-searched news for "today" itself
disagreed across sources — when that happens, say so plainly rather than picking whichever
story fits the user's premise; CLAUDE.md's DNSE-vs-BQ same-day rule is the general form of this).

## Output discipline

- Every DCF scenario needs an explicit WACC and growth path in the report, not just a number.
- State what changed since the last report on this ticker if there is one (price move, new
  quarter, resolved/new catalyst) — don't re-derive from zero and silently contradict an earlier
  conclusion without flagging the update.
- If a prior finding in this thread or in the research doc turns out wrong on re-check, say so
  explicitly and correct the record (both the live report and, if it exists,
  `calculated_fear_state_backstop.md` / `valuation_methodology_router.md`) — several corrections
  in this thread only stayed useful because the wrong number was replaced in place, not left
  standing next to the right one.
