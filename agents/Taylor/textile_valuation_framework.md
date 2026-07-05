# Textile / Garment EXPORT — Valuation Framework (Sector #16)

> Author: Taylor (Quant) · job Taylor_20260705_154537 · 2026-07-05
> Companion screen: `textile_screen.py` → `data/textile_{qualityvalue,basket}_monthly.csv` + `data/textile_verdict.json`
> First sector NOT in the 2026-06-30 15-sector sweep. Distinct economics: **USD revenue (export) / VND cost
> (labor) + order-book-driven demand** → trailing P/E distorted by the cotton-yarn input cycle.

---

## Part 1 — International framework (the economics)

Vietnamese textile/garment is an **export labor-arbitrage cyclical**, split by position in the value chain:

- **Vertically integrated (TCM: yarn→fabric→garment)** — capital-intensive (spinning/weaving D&A) → global
  comps (Shenzhou, Eclat) trade on **EV/EBITDA**, premium for margin stability. Earns a real through-cycle
  margin (GPM ~16-20% stable). *BQ caveat:* TCM's quarterly `EVEB` is **noisy** (spikes to 40-70 on lumpy
  quarterly EBITDA) → PE-vs-own-history is the cleaner cycle-normaliser here.
- **FOB high-margin (MSH: Song Hong)** — owns design/sourcing, not just cut-make-trim → **elite ROE
  (5Y 25-34%), ROIC 15-20%, IntCov 8-60×, low leverage**. The one genuine quality compounder. Trades on P/E,
  but is only ever *cheap* in a crash (2020 COVID) — the classic quality-never-on-sale problem.
- **Pure CMT scale (TNG, and the thin tail)** — cut-make-trim = commodity labor arbitrage: **razor-thin net
  margin (NPM~0-4%), high working-capital leverage (Debt_Eq 2-4×), negative IntCov**. Return comes from
  *volume growth* (TNG 5-6× 2016-18 on RevYoY +40-50%), not margin — a growth bet, not a value entry.

**Primary metric = P/E vs PE_MA1Y (cheap-vs-own-history)**, cycle-normalised, because (a) the order book that
drives next-year earnings is forward and not in BQ, and (b) trailing P/E swings violently with the input
cycle. EV/EBITDA is the textbook choice for the integrated names but the BQ `EVEB` series is too noisy to
gate on. Secondary: EV/EBITDA (context), P/B (crash-trough floor for the quality names).

**International reality that carries over:** the value chain, not the ICB code, sets the lens. FOB/integrated
(margin-stable) ≠ CMT (margin-commodity). The margin-stability gate is the whole game.

---

## Part 2 — Map to BQ columns
| Concept | BQ column | Role |
|---|---|---|
| Cycle-normalised valuation (primary) | `PE`, `PE_MA1Y` | entry when `PE < PE_MA1Y` |
| Integrated-name valuation (context, noisy) | `EVEB` | secondary rank only |
| **Margin stability (the quality gate)** | CV of `GPM_P0..GPM_P7` < 0.15 & mean > 0.12 | ejects CMT / messy pivots |
| Survival / not-a-leverage-trap | `IntCov_P0 > 1.5` | ejects TNG (IntCov<0), pre-2018 TCM |
| Real profitability | `ROE5Y > 0.15`, `NPM_P0 > 0.04` | ejects VGT (ROE 0.07), EVE (0.04) |
| Survived a cycle (cash) | `CF_OA_3Y > 0` | ejects GIL (neg 3Y CF) |
| FX sensitivity (test only) | `data/macro_usdvnd.csv` vs `profit_1M/2M/3M` | evaluation, never a live filter |
| Liquidity | `Trading_Value_1M_P50 ≥ 5B` | thin tail is untradeable |

**Universe (hand-curated).** LIQUID export core (ADV>5B, full history): **TCM, TNG, MSH, GIL, VGT**.
Thin tail (in universe, liquidity-gated out most months): STK, EVE, ADS, HTG, GMC, VGG. STK (recycled yarn)
is loss-making 2024-26; EVE is bedding (not pure export, ROE 0.04); GIL pivoted to industrial parks + lost
its Amazon contract 2022 (GPM CV 0.38).

---

## Part 3 — FX sensitivity test (the sector-specific question) — hypothesis REFUTED

Dispatch hypothesis: *VND depreciation (USD/VND ↑) lifts the VND-translated revenue of exporters → forward-
return tailwind.* Tested causally: USD/VND 3M/6M momentum at time *t* vs forward T+20/40/60 return
(`profit_1M/2M/3M`, evaluation-only). Pooled over 17.8k name-days, 2014-2026.

| FX momentum | vs profit_1M | vs profit_2M | vs profit_3M |
|---|---|---|---|
| USD/VND 3M | −0.067 | −0.103 | −0.110 |
| USD/VND 6M | −0.098 | −0.148 | **−0.177** |

Mean forward return by FX(6m) regime — the direction is the **opposite** of the thesis:
| Regime | fwd 1M | fwd 2M | fwd 3M | n |
|---|---|---|---|---|
| VND_weak (fx6m>+1%) | +0.4% | −0.3% | **−0.8%** | 6527 |
| flat | +1.4% | +3.8% | +6.1% | 8063 |
| VND_strong (fx6m<−0.5%) | +3.2% | +5.3% | **+8.0%** | 3225 |

**Interpretation (auditable):** the "weak-VND-helps-exporters" thesis is **dominated by the risk-off
confound**. In VN, USD/VND spikes are a global-tightening / Fed-hike / risk-off proxy (2018, 2022, 2024),
which crushes *all* VN equity — and textile, a high-beta cyclical exporter, gets hit **harder** than the
market (textile fx6m→profit_3M **−0.177** vs whole-market **−0.118**). Any real earnings tailwind from a
weaker VND is swamped by the beta/macro effect. **FX depreciation is NOT a tradeable long signal for this
group — if anything it flags "size down, macro stress incoming."** (Parallel to fertilizer, where the return
was one un-forecastable global catalyst, not the metric.)

*The fresh `data/vcb_fx_rate.csv` live feed (Winston, 2026-07-05) is for forward monitoring only — 3 days of
history, not backtestable.*

---

## Part 4 — Screens & backtest (point-in-time monthly, ASOF ≤120d, T+1, TC 0.1%, threads=1, hold cash when empty)

**Screen A — Quality-value exporter:** `GPM_CV(P0..P7)<0.15` & `GPM_mean>0.12` & `IntCov_P0>1.5` &
`CF_OA_3Y>0` & `ROE5Y>0.15` & `NPM_P0>0.04` & `PE<PE_MA1Y` & `PE>0` & `ADV≥5B`. Rank z(−PE)+z(ROE5Y)+z(−EVEB).

**Screen B — Sector basket (EW beta reference):** always-in the liquid export core (ADV≥5B).

| screen | window | net CAGR | Sharpe | MaxDD | Calmar | B&H CAGR | edge |
|---|---|---|---|---|---|---|---|
| **A quality-value** | FULL 14-26 | **−0.78%** | 0.09 | −59.1% | −0.01 | 10.23% | **−11.01pp** |
| A quality-value | IS 14-19 | 2.00% | 0.19 | −29.4% | 0.07 | 8.96% | −6.96pp |
| A quality-value | OOS 20-26 | −3.34% | 0.03 | −44.3% | −0.08 | 11.45% | −14.80pp |
| **B basket EW** | FULL 14-26 | 10.04% | 0.44 | −56.8% | 0.18 | 10.23% | −0.19pp |
| B basket EW | IS 14-19 | 4.32% | 0.28 | −32.5% | 0.13 | 8.96% | −4.64pp |
| B basket EW | OOS 20-26 | 15.76% | 0.56 | −56.6% | 0.28 | 11.45% | +4.30pp |

**Self-check 0 VND: PASS** (qualityvalue 1e-6, basket 2e-6).

- **Screen A FAILS decisively** — worse than B&H both IS (−6.96pp) and OOS (−14.80pp), Sharpe 0.09, MaxDD
  −59%. It holds cash 90/140 months (the margin-stable quality names are rarely *also* cheap-vs-history), so
  it fires as concentrated 1-name bets that whipsaw (2020 caught MSH/TCM but they *lagged* the broad +11%
  rally −8.4%; 2022 the garment order-collapse −37.7%). **Not a book.**
- **Screen B basket** ≈ B&H on CAGR but with a **−57% MaxDD** (vs −43%) and lower Sharpe. Its OOS "+4.30pp"
  is **entirely** the 2020 (+124%) and 2021 (+75%) COVID reopening/PPE order-surge — an un-repeatable event;
  2022 −44.7%, 2025 +1.6% vs market +44%. **A high-beta cyclical, not a durable book** (the fertilizer-2021
  pattern again).

**Verify (Screen A picks behaved as designed):** MSH CAUGHT (18mo, incl 2020 COVID cheap-quality) · TCM
CAUGHT (33mo, incl the 2018Q1-2019 IntCov-just-turned-positive window before the 2020-21 PE 3.9→31 surge) ·
TNG REJECTED (thin-CMT: NPM~0, Debt_Eq 2-4, IntCov<0) · STK/VGT REJECTED · GIL leaked 11mo in 2021-22
(margin was transiently stable *before* the Amazon-contract loss blew GPM CV to 0.38 — an honest, documented
minor leak). **Orthogonality:** 34% vs custom30V, 2% vs 8L top-25. **Median selected ADV 15.8B.**

---

## Part 5 — Macro context (qualitative, NOT a quant variable)

Order-flow diversion out of China (nearshoring / "China+1" / trade-war tariff routing) is the real
multi-year tailwind for VN garment capacity, but there is **no BQ series that measures it directly** →
recorded as qualitative context only, never a screen variable (same discipline as the fertilizer supercycle:
don't quantify what you can't measure). It shows up, if at all, as revenue growth in the names that *win*
share (TNG capacity build; MSH FOB up-mix) — already captured by RevYoY, not a separate signal.

---

## Part 6 — Verdict: LENS, not a BOOK (sweep Rule 3 holds)

Textile/garment export is **not a sector to add as an automated V2.4 sleeve.** Neither the quality-value
screen (fails IS+OOS) nor the sector basket (one-off 2020-21 boom, −57% DD otherwise) is a tradeable book.
The durable, transferable artifacts:

1. **FX: the "weak-VND-helps-exporters" thesis is quantitatively FALSE for forward returns** — USD/VND
   depreciation is a risk-off proxy (Spearman −0.18, worse than market), not an earnings tailwind. **Do not
   size textile up on VND weakness; it flags macro stress.** (The single most useful output of this job.)
2. **The GPM-CV<0.15 + IntCov>1.5 + ROE5Y>0.15 gate is a valid single-name LENS** — it correctly ranks
   **MSH (elite) > TCM (margin-stable, faded ROE now) >> TNG (thin-CMT leverage trap)** and ejects the messy
   pivots/losses (GIL, STK, VGT, EVE). Use it to *evaluate* a textile name, not to rotate a book.
3. **MSH is the one genuine quality compounder** (ROE5Y 25-34%, ROIC 15-20%, IntCov 8-60) — a buy-and-hold-
   on-weakness watchlist name (like DHG in pharma; **timing destroys it**). It is only ever cheap in a crash
   (2020), and — usefully — **it is cheap-vs-own-history again right now** (2026Q1: PE 6.5 < PE_MA1Y 7.6, PB
   1.78, ROE5Y 24.9%, IntCov 7.7). Accumulate-on-weakness candidate, NOT a timed trade.

No HPG/DGC/MWG-style catchable *compounding* book exists here: MSH is quality-but-rarely-cheap (buy-the-crash,
not a screen), TCM's ROE5Y has faded below 0.15, and TNG's multibagger was a thin-margin/high-leverage
*growth* bet a quality-value screen correctly declines. Watchlist single-name (MSH) only.
