# Livestock / Animal-Feed (Hog Cycle) — Valuation Framework (Sector #17)

> Author: Taylor (Quant) · job Taylor_20260705_160724 · 2026-07-05
> Companion screen: `livestock_screen.py` → `data/livestock_{troughbuy,basket}_monthly.csv` + `data/livestock_verdict.json`
> Second sector NOT in the 2026-06-30 15-sector sweep (after textile #16). Distinct economics: a genuine
> **protein / hog commodity cycle** — margins swing violently on hog price (supply, ASF disease) vs imported
> feed cost (corn/soybean). **Trailing P/E goes NEGATIVE at the cycle trough** → the international protein-cycle
> playbook says value on P/B-trough + a margin-inflection trigger, not on P/E. This is the OPPOSITE animal from
> the defensive F&B/FMCG of sector #10.

---

## Part 1 — International framework (the economics)

Global protein-cycle players (Tyson Foods, WH Group/Smithfield, BRF, Muyuan, Charoen Pokphand) are
**capital-intensive commodity cyclicals**, valued on:

- **P/B trough-buy** — at the cycle bottom hog price < cost of production → the pure farmers post **losses**,
  so **trailing P/E is negative or absurd** and useless. P/B is the only stable through-cycle anchor: buy near
  replacement-cost trough, sell into the margin peak.
- **EV/EBITDA** on the way up (mid-cycle 4–8×), because leverage (herd/farm expansion capex) distorts P/E.
- **The margin cycle IS the signal.** GPM/NPM mean-revert around the hog-vs-feed spread. The best entry is the
  **margin-inflection** point — GPM turning up off a trough — not the low multiple alone.
- **Integrated ("3F": Feed → Farm → Food, e.g. CP)** earns a real through-cycle ROIC and *survives* the
  downcycle → the market never lets it get truly cheap except at a crash. **Pure-play farmers** (thin margin,
  levered expansion) are the high-beta bet: they multibag on the up-cycle and wipe out on the down.

**Primary metric = P/B-vs-own-history (`PB < PB_MA1Y`) + a margin-turn trigger (`GPM_P0 > GPM_P4`)**, because
(a) P/E is negative/distorted precisely when you want to buy (the trough), and (b) there is no direct hog-price
series → GPM is the cycle proxy. Secondary: EV/EBITDA (mid-cycle rank), leverage/solvency gate (`IntCov`,
`CF_OA_3Y`) because these names carry heavy expansion debt.

**International reality that carries over:** integrated survivor (DBC) ≠ levered pure-play (BAF). The
survival/margin-stability gate is the whole game — same structure as steel (HPG-survivor vs HSG/NKG
leverage-trap) and textile (FOB-quality vs thin-CMT).

---

## Part 2 — Map to BQ columns
| Concept | BQ column | Role |
|---|---|---|
| Cycle-trough valuation (primary) | `PB`, `PB_MA1Y` | entry when `PB < PB_MA1Y` (cheap vs own history) |
| **Margin inflection (the real signal)** | `GPM_P0 > GPM_P4` (YoY margin turning up) | the trigger that carries the forward return |
| Mid-cycle valuation rank | `EVEB` | secondary rank |
| Survived the downcycle (cash) | `CF_OA_3Y > 0` | ejects BAF (CF_OA_3Y went −981B → −2091B on capex) |
| Not a solvency wreck | `IntCov_P0 > 1.0` (loose — names carry expansion debt) | ejects the deep-loss quarters |
| Through-cycle quality (context) | `ROE5Y`, `ROIC5Y` | DBC ~0.11–0.19 (cyclical, NOT elite-stable) |
| Cycle proxy for the signal test | quarterly `GPM_P0` (no hog-price field exists in BQ) | evaluation of the cycle, not a live filter |
| Liquidity | rolling-21d ADV (`Volume×Price`) ≥ 5B | thin tail (MML/VLC/VSN/APF/HKB/AGM, all <3B) is untradeable |

**Universe (hand-curated).** Prices pulled from the **full `ticker` table** (`data/livestock_prices.csv`), not
the prune cache — the prune cache is stale for the recently-added BAF/HNG (only 2 rows). Liquid core (rolling
ADV>5B): **DBC, BAF, HAG, HNG**. Thin tail (in universe, liquidity-gated out most months): MML (Masan
MEATLife), VLC (Vilico), VSN (Vissan, ADV 0.1B), APF, HKB, AGM.
- **DBC (Dabaco)** — integrated feed→3F, the flagship. The one genuine survivor-cyclical (the HPG-analog).
- **BAF (BaF, IPO 2021)** — pure-play hog-farm expansion; PE 18–177 (**never cheap on P/E**), GPM 0–20% thin,
  ROE5Y ~0.10–0.15, Debt_Eq 2–2.5, IntCov collapsed 25→2. A **levered growth bet** (the TNG-analog).
- **HAG (HAGL)** — diversified agri conglomerate (pork + banana, ex-rubber/sugar/RE turnaround); near-default
  2015–2019. Not a clean hog play.
- **HNG (HAGL Agrico)** — crop/banana plantation (trồng-trọt), chronic-loss restructuring. A different
  sub-group, as the dispatch flagged.

**Aquaculture protein (VHC/ANV/MPC pangasius/shrimp) DELIBERATELY EXCLUDED** — it is an **export-FX** protein
cycle (USD revenue), a different animal from the domestic hog cycle. That is the textile-#16 FX story, and the
FX thesis there was refuted.

---

## Part 3 — The hog-cycle signal test (the sector-specific question) — SIGNAL CONFIRMED

No direct hog-price field in BQ → proxy the cycle with quarterly GPM. Test causally: at each name-day, does
**P/B-vs-own-history** (`PB/PB_MA1Y`, "trough") and **margin turn** (`GPM_P0 − GPM_P4`) predict forward
T+20/40/60 return (`profit_1M/2M/3M`, evaluation-only, never a live filter)? Pooled 22.4k name-days, 2014–2026.

| Signal | vs profit_1M | vs profit_2M | vs profit_3M |
|---|---|---|---|
| PB/PB_MA1Y (trough, lower=cheaper) | +0.013 | +0.006 | +0.002 |
| **GPM turn (GPM_P0−GPM_P4)** | +0.072 | +0.100 | **+0.117** |

Mean forward return by cycle regime — the **combined trough+margin-turn regime dominates**:
| Regime | fwd 1M | fwd 2M | fwd 3M | n |
|---|---|---|---|---|
| **trough_up** (PB<MA1Y **AND** GPM turning up) | +3.3% | +6.0% | **+8.3%** | 5925 |
| mixed | +0.2% | +0.3% | +0.4% | 11912 |
| rich_down (PB≥MA1Y AND margin falling) | +0.4% | +0.8% | +1.1% | 4538 |

**Interpretation (auditable):** unlike textile (FX refuted), the hog-cycle entry signal **is real** —
`trough_up` earns +8.3% forward 3M vs +1.1% `rich_down`. BUT the work is done by the **margin inflection**, not
the P/B-trough: `pb_rel` alone (IC +0.002) is no better than the whole market (−0.003) — **P/B-trough alone is
a value trap** (identical to steel's finding). It is the **GPM-turn (IC +0.117)** that carries the return, and
the combination that fires. **The transferable rule: buy the hog names when margin is inflecting up off a
trough (GPM_P0 > GPM_P4) AND the multiple is cheap-vs-history — never on the cheap multiple alone.**

---

## Part 4 — Screens & backtest (point-in-time monthly, ASOF ≤120d, T+1, TC 0.1%, threads=1, hold cash when empty)

**Screen A — Hog-cycle trough-buy:** `PB<PB_MA1Y` & `GPM_P0>GPM_P4` & `CF_OA_3Y>0` & `IntCov_P0>1.0` & ADV≥5B.
Rank z(−PB/PB_MA1Y)+z(GPM_turn)+z(−EVEB).
**Screen B — Sector basket (EW beta reference):** always-in the liquid core (ADV≥5B).

| screen | window | net CAGR | Sharpe | MaxDD | Calmar | B&H CAGR | edge |
|---|---|---|---|---|---|---|---|
| **A trough-buy** | FULL 14-26 | **10.07%** | 0.46 | **−27.0%** | 0.37 | 10.27% | −0.19pp |
| A trough-buy | IS 14-19 | 10.41% | 0.53 | −7.2% | **1.45** | 8.96% | **+1.45pp** |
| A trough-buy | OOS 20-26 | 9.76% | 0.43 | −27.0% | 0.36 | 11.51% | −1.75pp |
| **B basket EW** | FULL 14-26 | **−1.30%** | 0.17 | **−82.9%** | −0.02 | 10.27% | −11.57pp |
| B basket EW | IS 14-19 | −20.61% | −0.37 | −80.9% | −0.25 | 8.96% | −29.57pp |
| B basket EW | OOS 20-26 | 20.99% | 0.63 | −54.3% | 0.39 | 11.51% | +9.48pp |

**Self-check 0 VND: PASS** (trough-buy 0.0, basket 0.0).

- **Screen A trough-buy ≈ B&H on CAGR (−0.19pp) but at HALF the drawdown (−27% vs −43%)** → Calmar 0.37 > 0.24,
  and **IS +1.45pp with a superb Calmar 1.45 / −7.2% DD**. It holds **cash 121/151 months** (the margin-turn
  rarely fires — only 30 months in market, median **1 name**). The edge is **extremely lumpy**: driven by DBC's
  2018 (+98.7pp), the 2020 ASF explosion (+50.8pp), and the 2023 recovery (+18.7pp) — but it sits in cash
  through the 2016/2017/2021 bulls and gives back −22.6pp in 2026. **A valid single-name timing LENS, not a
  book** (too few names, too much cash, OOS −1.75pp — the boom-year lumpiness is the Wave1/H8a lesson again).
- **Screen B basket is un-investable** — **−82.9% MaxDD**, −1.30% FULL CAGR, IS −20.61%. The 2015–2019 collapse
  (HAG near-default, HNG chronic losses) destroys it; the OOS "+9.48pp" is entirely the 2020-21-23-24 hog
  up-cycles. A high-beta wreck, not a durable book.

**Verify (Screen A picks behaved as designed):** DBC CAUGHT 14mo incl the **2019Q4→2020 pre/into-ASF window**
(PB 0.68<MA1Y 0.75, GPM about to turn) → the ASF explosion · BAF **leaked 9mo in 2023** (post-IPO multiple
deflating PB 5.4→1.5 read as "cheap-vs-history" + a tiny GPM uptick — an honest documented leak, like GIL in
textile; later correctly **ejected by CF_OA_3Y<0** as expansion capex ballooned) · HAG 6mo / HNG 3mo (the messy
conglomerate/plantation leak in). **Orthogonality:** 33% vs custom30V, 12% vs 8L top-25. **Median selected ADV
56.9B** (highly liquid — DBC/BAF/HAG are large-caps).

---

## Part 5 — Macro / disease context (qualitative, NOT a quant variable)

**African Swine Fever (ASF)** is the dominant supply shock — the 2019–2020 ASF epidemic culled herds, spiked
hog prices, and drove DBC's record 2020 (GPM 10%→30%, NP ×4). **Disease risk is not measurable in financial
data** → recorded as qualitative context only (same discipline as the fertilizer supercycle and textile
nearshoring: don't quantify what you can't measure). It surfaces, if at all, as the GPM inflection already in
the signal. State feed-import policy and live-hog price controls similarly can't be gated on. **Fresh commodity
feeds (corn/soybean, live-hog price) are Winston's Data/Regime Ops remit** if a live overlay is ever wanted —
but there is no backtestable BQ series today.

---

## Part 6 — Verdict: LENS, not a BOOK (sweep Rule 3 holds) — but the signal is REAL

Livestock/animal-feed is **not a sector to add as an automated V2.4 sleeve.** The basket is un-investable
(−83% DD) and the trough-buy screen is too few names / too much cash to carry a book (OOS −1.75pp, lumpy). The
durable, transferable artifacts:

1. **The hog-cycle entry signal is GENUINE** (unlike textile's FX) — but it is the **margin inflection
   (`GPM_P0 > GPM_P4`, IC +0.117), not the cheap P/B, that carries it.** `trough_up` earns +8.3% fwd-3M vs
   +1.1% `rich_down`. **P/B-trough alone is a value trap** (IC +0.002 ≈ market — the steel lesson). **Rule:
   buy the hog names only when margin is turning up off a trough AND the multiple is cheap-vs-history.**
2. **DBC is the one genuine catchable name** — the HPG-analog of this sector: integrated 3F, *survives* the
   cycle (positive CF_OA_3Y, IntCov turned strongly positive post-2018), P/B-trough+GPM-turn entry demonstrably
   works (2018, 2020 ASF, 2023). But it is a **cyclical, not a secular compounder** — ROE5Y swings 0.11–0.19
   and IntCov was **negative 2012–2017**. So it is cyclical-trough-*timing*, **not** an MWG/DGC/HPG-style
   buy-and-hold compounder. **No steady-compounder book exists here** — the dispatch's HPG-2014/DGC-2016 pattern
   is present only as *DBC's own ASF up-cycle*, a timed cyclical trade, not a hold.
3. **BAF is the levered-growth bet** a value screen correctly declines (never cheap on P/E, thin margin,
   CF_OA_3Y negative on capex) — the TNG-analog. Not a value entry.

**Current read (2026Q1, watchlist):** **DBC is cheap-vs-own-history (PB 1.03 < PB_MA1Y 1.34, PE 6.3, IntCov
7.5)** BUT the **GPM-turn trigger is NOT firing** (GPM_P0 0.17 = GPM_P4 0.17, margin flat) and **ROE5Y has faded
to 0.11**. So it is a *watch* — the value half of the setup is present, but the margin-inflection half (the part
that actually pays) has not fired. **Buy DBC on the next confirmed GPM turn-up, not on the cheap multiple
alone.** (Sizing small, high-beta tactical — DT5G state caps gross.)
