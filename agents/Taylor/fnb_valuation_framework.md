# F&B (Food & Beverage) valuation framework (Taylor, job Taylor_20260630_071901)

**Sector #10 of the sector-by-sector valuation sweep.** ICB lumps "Food & Beverage" but the sector
splits into two sub-sectors with **opposite economics**, so the screen is a DUAL hand-curated universe.
Script: `fnb_screen.py`. Outputs: `data/fnb_{fmcg,seafood}_monthly.csv`, `data/fnb_verdict.json`.

## Verdict (one line)
**Both sub-screens are REAL-but-thin lens-not-book — F&B sits in the weak tier alongside steel/energy.**
FMCG-defensive is **IS-driven with NO OOS edge** (strong +11pp IS → −2.4pp OOS, the textbook
megacap-rerating-then-derating shape, like retail). Seafood-cyclical has a **single-event OOS edge**
(+7pp OOS but it is ENTIRELY the 2022 ASP super-cycle; fails IS −8pp, flat Sharpe, −36% DD). Two
durable exports: the **GPM-stability moat gate** (cleanly rejects KDC the serial restructurer) and the
**seafood duty-cycle value-trap filter** + the structural finding that **VHC is un-capturable as a
trough buy** (quality never gets cheap).

## Part 1 — International framework → VN reality
| Sub-sector | Textbook method | VN reality (what actually works in BQ) |
|---|---|---|
| **FMCG / staples** (VNM/SAB/MSN/MCH/QNS/KDC) | P/E primary (Nestlé/Unilever/AB-InBev); brand moat = stable high GPM; DY>4% when mature; ROE>20% sustained | **PE<PE_MA1Y** (cheap vs OWN history — these rarely get absolutely cheap) + **ROE5Y>18%** + **GPM moat** (avg8q≥22% AND CV<25%). **DY is a TRAP** (see below). Real lens, but **no OOS return edge** — defensive names lag in bull years (2021 −58pp). |
| **Seafood export** (VHC/FMC/MPC/ANV/IDI/CMX) | Cyclical, NOT FMCG: tied to global shrimp/catfish ASP + US/EU anti-dumping duties. P/B trough-buy; GPM = ASP proxy | **PB<1.2** trough + **GPM_P0>GPM_P4** (ASP turning up) + **CF_OA_3Y>0** (survives duty cycle) + **Debt_Eq<1.5**. Mechanically sound but **thin** (median 1 name, holds 38/148 mo) and the OOS edge is one event (2022). |

## Part 2 — The durable findings

### (a) DY is uncapturable in VN FMCG → no "staples yield screen" in BQ
DY is only populated in **dividend-declaration quarters**, not continuously: VNM 36/83, SAB 22/39,
**MSN 7/67**, MCH 15/39. Across the FMCG universe only **359/754** ASOF rows have DY>0. A hard
`DY>3%` gate fires sporadically and *ejects a known payer* in the ~60-90% of quarters DY isn't
recorded. → **DY used as a SCORING bonus, never a gate.** Same data gap found in energy + cement;
it generalizes to every VN dividend-yield screen.

### (b) GPM-stability = the FMCG moat gate (the real discriminator)
Brand moat = a **high AND stable** gross margin. Gate: `gpm_avg8q ≥ 22% AND gpm_CV < 25%`. It KEEPS
the genuine brands (MCH CV 0.05 / SAB 0.12 / QNS 0.11 / VNM 0.18) and cleanly **REJECTS KDC**
(CV 0.38 — a serial restructurer whose margin swings 15%→58%; no stable margin = no moat). Of 300
PE-cheap + ROE>18% FMCG rows, the GPM-moat gate rejects 27 — *all KDC*.

### (c) Seafood duty-cycle value-trap filter + VHC is structurally un-capturable
The discipline `CF_OA_3Y>0 AND Debt_Eq<1.5` rejects **90 of 133** cheap-PB + margin-up seafood rows —
the names that are cheap *because* a duty cycle damaged their 3-year cash generation or balance sheet
(ANV/FMC/IDI in bad quarters; CMX fully excluded, median Debt 3.5). The screen then captures only the
*survivable* troughs (ANV 6mo, MPC 4mo). **VHC = 0 trough entries**: its PB floor is 0.91 and median
1.63 — the quality catfish name essentially never trades below book, so a PB<1.2 trough screen *correctly*
says VHC is seldom a value entry. VHC's return is a quality-compounding story, **not** a trough-buy signal.

## Part 3 — Backlook anchors (ticker_financial cache)
- **MCH** GPM avg0.44 CV0.05 ROE5Y0.36 → highest & most stable margin in VN FMCG (Masan Consumer moat)
- **VNM** GPM avg0.39 CV0.18 ROE5Y0.29 → dairy moat; qualifies on the PE mean-reversion legs (89 mo)
- **SAB** GPM avg0.28 CV0.12 → beer moat (only in liquid prune from 2017 → thin IS)
- **QNS** GPM avg0.32 CV0.11 → Vinasoy soymilk + sugar (from 2017)
- **KDC** GPM avg0.28 **CV0.38** → unstable margin → GPM-moat gate REJECTS (no moat) ✓
- **MSN** GPM avg0.33 CV0.20, low ROE5Y → conglomerate (resources+consumer+retail), not a pure staple
- **VHC** PB min0.91 med1.63, CF_OA_3Y+ 66/74 → quality, rarely <1.2 → 0 trough entries (correct)
- **ANV** PB min0.22, CF_OA_3Y+ 58/75 → deep but survivable duty-cycle troughs → trough-buy candidate
- **MPC** PB min0.78 GPM avg0.13 → shrimp, levered; trough entries only when CF+ and Debt<1.5
- **CMX** Debt med3.5 → over-levered → trap-gate fully excludes (0 entries)

## Part 4 — Caveat: sub-universe maturity
SAB/MCH/QNS only enter the liquid `ticker_prune` universe from 2017, so the FMCG IS window (2014-19)
is dominated by VNM/MSN/KDC — the strong IS edge (+11pp) leans on the 2015-16 VNM/MSN megacap re-rating
(+43pp/+34pp years) that does not repeat OOS. Same "sector just became investable" caveat as telecom,
weaker form.

## Where it lands for the book
Neither sub-screen is a standalone sleeve. **FMCG** = a quality/defensive **watchlist lens** (orthogonal:
15% custom30V, 0% 8L top-25) for parking in risk-off, NOT an alpha picker — no OOS edge, worse-than-market
DD. **Seafood** = a **cyclical trough lens** (the duty-trap filter is the reusable export) to flag ASP-cycle
entries (ANV/MPC), but un-backtestable as a standalone book (one-event OOS, fails IS, ADV only 3.6B).
Mirrors the retail (IS-driven) and shipping (cyclical-trough) findings of the sweep.
