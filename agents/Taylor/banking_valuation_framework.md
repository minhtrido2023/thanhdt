# Banking Valuation Framework — VN bank compounders (P/B-vs-ROE / Gordon)

Job Taylor_20260630_051434 (sector-by-sector compounder book; banking after retail). Companion to
`retail_valuation_framework.md`. Backtest: `bank_compounder_screen.py` → `data/bank_compounder_{monthly.csv,verdict.json}`.

## Part 1 — Why banks are valued differently (international practice)
A bank's earnings are **leveraged off book equity** — leverage is the *product*, not a risk flag. So the
generic toolkit breaks:
- **P/B is primary** (not P/E, not P/S). P/E is noisy through the credit cycle; P/S is meaningless (no "sales").
- **Gordon justified-P/B**: `justified_PB = (ROE − g) / (COE − g)`. A bank earning sustainable ROE above its
  cost of equity (COE) deserves P/B > 1; it is **cheap when actual P/B < the level its through-cycle ROE
  justifies**. VN bank COE ≈ 12–14% → we use **COE=0.13, g=0.05** → `justified_PB = (ROE5Y − 0.05)/0.08`.
- **ROE > COE** = the value-creation test. Below COE, growth destroys value.
- **DO NOT use**: `Debt_Eq` (every bank is highly levered by design), `CF_OA` (loan issuance distorts operating
  cash flow), `ROIC` (no "invested capital" ex-balance-sheet). Confirmed meaningless for banks.
- **NIM / CASA / NPL / CAR** are the right risk metrics but are **NOT in BQ** (`ticker_financial`). Proxies used:
  through-cycle ROE floor (`ROE_Min3Y`, `ROE5Y`) stands in for asset quality — a bad-debt blow-up crushes ROE,
  so a high *minimum* ROE over 3Y ≈ "never destroyed equity". Real NPL/CAR live only in `bank_lens_v3.py` (vnstock).
- **Loan/credit growth** = revenue-growth proxy → `NP_P0/NP_P4` (profit growth) and `Revenue_YoY_P0` (total income).

## Part 2 — BQ column map (what's usable for a bank screen)
| Role | Column | Note |
|---|---|---|
| Valuation (primary) | `PB`, `PB_MA5Y/SD5Y` | Gordon justified-P/B from ROE |
| Through-cycle ROE | `ROE5Y`, `ROE3Y`, `ROE_Trailing` | franchise quality; trailing is cycle-noisy |
| Asset-quality proxy | `ROE_Min3Y` (also `_Min5Y`) | never-destroyed-equity floor |
| Credit-book growth | `NP_P0..P4`, `Revenue_YoY_P0` | loan/income growth |
| (noisy, dropped) | `NPM_P0/P4`, `FSCORE` | bank NPM swings 0.1↔0.4 q/q; bank-Piotroski distorted (MBB scored **2** at its best entry) |
| AVOID | `Debt_Eq`, `CF_OA*`, `ROIC*` | meaningless for banks |
| Universe id | `ICB_Code = 8355` | = banks (verified in cache) |

## Part 3 — Backlook: MBB & VCB 2017Q1 (the two archetypes)
| | PB | ROE_Trailing | ROE5Y | ROE_Min3Y | NP YoY | Rev YoY | FSCORE | justified_PB | read |
|---|---|---|---|---|---|---|---|---|---|
| **MBB** 2017Q1 | **1.09** | 11.9% | **15.3%** | **12.0%** | +26% | +28% | 2 | **1.29** | PB 1.09 < 1.29 → **CHEAP-for-quality**. Market hadn't re-rated after 2012–14 bad-debt cleanup. The +10x. |
| **VCB** 2017Q1 | **2.54** | 14.7% | 9.9% | 10.6% | +20% | +22% | 2 | **0.61** | PB 2.54 ≫ 0.61 → **already EXPENSIVE** on through-cycle ROE. Worked only on FORWARD ROE → 24%+ (state-bank moat). |

**Two banking-compounder archetypes** (parallel to retail's volume/margin split):
- **A — cheap re-rating (MBB)**: low P/B + high through-cycle ROE + recovering current ROE. **Value-identifiable at entry.**
- **B — quality-premium (VCB)**: already-premium P/B justified only by *forward* ROE expansion. **NOT identifiable without look-ahead** → structurally uncapturable by a value-disciplined screen (exactly like retail's PNJ margin-turnaround miss).

The dispatch's first-draft gates (ROE_Trailing≥15% AND rising; NP/NP≥1.20; FSCORE≥4; fixed PB<X) were **too
strict** — they miss BOTH anchors (MBB ROE_Trailing 11.9<15, FSCORE 2<4; VCB PB 2.54 > any cheap X).
Recalibrated to the data below.

## Part 4 — Banking Compounder Screen (headline = value-disciplined cheap-rerate)
Universe: `ICB_Code=8355`, in `ticker_prune`, `Trading_Value_1M_P50 ≥ 1e9`. Point-in-time ASOF financials
(Release_Date ≤ day, staleness ≤ 120d).
- **Quality floor** (asset-quality proxy): `ROE_Min3Y ≥ 0.08`
- **Franchise** (earns its COE): `ROE5Y ≥ 0.12`
- **Credit-book growth**: `NP_P0/NP_P4 ≥ 1.10` **OR** `Revenue_YoY_P0 ≥ 0.12`
- **Gordon value**: `PB < (ROE5Y−0.05)/0.08` **AND** `0 < PB < 2.0`
- Rank `z(justified_PB−PB) + z(ROE5Y) + z(NP_growth)`, top-K=10, monthly EW, T+1, TC 0.1%.

## Part 5 — Backtest result (auditable, self-check PASS 0 VND)
| window | Bank net CAGR | Sharpe | MaxDD | B&H CAGR | edge |
|---|---|---|---|---|---|
| FULL 2015-2026 | **31.9%** | 1.06 | **−44.5%** | 13.2% | **+18.7pp** |
| IS 2014-2019 | 36.2% | 1.40 | −18.4% | 17.3% | +19.0pp |
| **OOS 2020-2026** | **30.0%** | 0.96 | −44.5% | 11.5% | **+18.6pp** |

Verify: **MBB caught 2016–2017** (12 months) ✓; **VCB correctly absent** (premium, value gate) ✓; weak/bad-debt
tail **BVB/KLB/NVB excluded** ✓ (ROE_Min3Y floor works). Orthogonality: vs 8L top-25 **5%** (orthogonal —
8L value-tilt misses banks), vs retail/industrial 0% (disjoint sector), **vs custom30V 74%** (see caveat).

## Verdict — REAL signal, holds OOS, but a high-beta tilt largely already owned
**Strongest of the three sector compounders**: unlike retail (no OOS edge), banking's +18.6pp edge **holds OOS
and is broad** (2020 +70, 2021 +60, 2023 +20, 2024 +19pp). BUT three honesty caveats:
1. **High-beta, concentrated**: MaxDD −44.5% (worse than B&H); ~79% of cumulative return = two bank-bull
   episodes (2017 = 27%, 2020–21 = 52%); 2022 drew −34.9% (worse than B&H −28%).
2. **Early years = a 1-name book** (2015–19 avg **1.1** names held) — the 2017 +100% is essentially a single
   MBB bet, not a diversified book. Only OOS (avg 6.7 names) is a real book — and it still does 30% CAGR.
3. **~74% redundant with custom30V** — the production parking basket already holds **10–13 banks** (of 30)
   since 2018. The non-redundant slice is precisely the fragile 2017 MBB era (custom30V held 1 bank then).

→ **Deploy as a sector watchlist / tilt + a reusable valuation lens (Gordon justified-P/B), NOT a new standalone
leveraged book.** The framework's lasting value is the *valuation method* (P/B-vs-ROE, archetype split,
asset-quality-via-ROE-floor) for sizing bank exposure inside V2.4 — not a separate book whose beta/return is
already captured by custom30V. Real-NPL/CAR overlay for live sizing → `bank_lens_v3.py` (vnstock).
