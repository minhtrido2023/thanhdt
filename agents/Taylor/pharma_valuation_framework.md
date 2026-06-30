# Pharmaceuticals (VN) — Valuation Framework + Screen Design

Job: Taylor_20260630_072007 (Sector #12). Script: `pharma_screen.py`.
Universe: **DHG, DMC, IMP, TRA, DBD, MKP** (generic + distribution; **no innovative R&D pipeline** in VN).

## What VN pharma actually is
Not innovative pharma — there is no drug-discovery pipeline to value on `P/pipeline` or `EV/R&D`.
VN pharma = **generics manufacturing + distribution**, defensive recurring demand (aging population +
rising health-spend/GDP). The moat is **brand at the point of dispensing** (doctors/pharmacists) plus a
**foreign strategic partner** (Taisho→DHG, Abbott→DMC, Daewoong→TRA) signalling quality + tech transfer.
So the valuation lens is the **defensive-compounder / P-E mean-reversion** lens, not a cyclical one.

- **P/E primary** — recurring prescription/OTC demand, low cyclicality.
- **ROIC > 15%** = distribution-moat signal (pricing power with the channel).
- **GPM/NPM durability** — generic margins are thinner than branded but should be *stable*.
- **DY > 3%** for mature payers (DHG/DMC) — but see DY-uncapturable note below.
- **Clean balance sheet** (Debt/Eq < 0.5) — manufacturing pharma should self-fund.
- **ETC vs OTC**: ETC (hospital/prescription, won by tender) = higher margin + higher barrier but
  capex-heavy (EU-GMP / WHO-GMP lines); OTC = distribution-network moat.

## Backlook (ticker_financial cache) — what the data says
| ticker | 2015Q4 | 2018Q4 | 2020Q4 | read |
|---|---|---|---|---|
| DHG | PE9.2<MA12.1, ROE5Y29%, ROIC5Y21%, GPM38% | PE16.9<MA20.3, ROE24%, ROIC18% | PE18.6, ROE22%, GPM48% | quality leader, Taisho moat; PE-MA dip = the entry |
| DMC | PE8.1, ROE18%, GPM34% | PE11.0<MA14.4, ROE21% | PE11.5, ROE20% | Abbott; clean, mid-quality; **goes illiquid 2023** |
| IMP | PE11.8, **ROE5Y10.6%, ROIC5Y8.6%** | ROE10.5%, ROIC9.2% | ROE10.8%, ROIC11% | ETC champion but **structurally sub-15% returns** |
| TRA | PE11.4<MA12.4, ROE23% | PE18.6, ROE20%, GPM52% | PE14.1<MA14.7, ROE19% | herbal/OTC, Daewoong; **goes illiquid 2022** |

Three structural facts that shape the verdict **before** any backtest:
1. **IMP is excluded by the quality floor.** Its ROE5Y/ROIC5Y sit ~10–11% — the ETC build-out (EU-GMP
   plants, hospital-tender working capital) structurally depresses returns. A `ROE5Y>15% AND ROIC5Y>15%`
   gate ejects the *single best secular growth story* in VN pharma. Documented **capture failure** —
   the ETC-growth archetype is un-screenable on a backward quality floor.
2. **ROIC5Y has a scale artifact pre-2017** (DMC 1.87, TRA 2.71 in 2015–16 = garbage denominators on a
   tiny equity base; normalise to ~0.17–0.20 by 2018). A `>0.15` gate *passes* them anyway, so it doesn't
   corrupt picks, but the ROIC number itself is untrustworthy in the early window — don't read it as moat.
3. **The liquid window is short and shrinking.** In `ticker_prune`: DHG to 2026 (ADV ~5.1B), IMP to 2026
   (2.5B), DBD from 2017 (3.7B), **DMC stops 2023-09 (2.7B), TRA stops 2022-07 (1.0B)**, MKP not in prune.
   So the tradeable universe collapses to ~2–3 liquid names after 2023.

## Screen (as dispatched)
`PE>0 AND PE < PE_MA1Y×0.9` (cheap relative to own 1Y mean = defensive mean-reversion entry)
`AND ROIC5Y>0.15 AND ROE5Y>0.15` (distribution-moat / quality floor)
`AND GPM_P0 ≥ GPM_P4−0.02` (gross-margin stable YoY)
`AND CF_OA_3Y>0` (cash-generative) `AND Debt_Eq_P0<0.5` (clean balance sheet).
Hold **top-8** (score = cheapness −z(PE/MA) + DY bonus + z(GPM)); monthly rebal, EW, T+1, TC 0.1%,
**hold cash when nothing qualifies** (correct for a wait-for-cheapness defensive screen). IS 2014-19 /
OOS 2020-26. Self-check 0 VND, orthogonality vs custom30V & 8L top-25.

## A-priori expectation
Defensive, thin, partly-illiquid universe with one structural exclusion (IMP). Expect a **low-DD,
low-turnover lens** that under-returns VNINDEX in bull years and protects in drawdowns — a
**watchlist/risk lens, not a standalone book**. The interesting questions are (a) does the PE-MA
mean-reversion entry add anything over buy-and-hold the same names, and (b) does it hold OOS once the
universe thins to DHG+IMP.
