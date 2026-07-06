# Holding Company / Conglomerate — Sum-of-the-Parts (SOTP) Archetype — Sector #20 Framework

> **Author:** Taylor (Quant) · **Job:** Taylor_20260706_042831 (dispatch from Mike) · **For:** DollarBill, user (via Mike)
> **Scope:** RESEARCH-ONLY, new files only (`holdco_sotp_screen.py` + this doc + `data/holdco_*`). Production (custom30V/BAL/LAG/DT5G/rating_8l.py) untouched.
> **This is NOT a sector — it is a VALUATION METHOD**, a cross-cutting lens like the 5F moat overlay (#0) and the SOE governance note (#19). The deliverable is a SOTP *diagnostic*, not a book and not a new gate.
> Backtest self-check 0 VND PASS (all 0e0, discount 0e0), threads=1, walk-forward IS(2016–19)/OOS(2020–26). Point-in-time on `ticker_prune` + `ticker_financial` cache. `profit_*` eval-only, never a live filter.

---

## 0. What this archetype IS

A **holding company / conglomerate** is a listed group whose value is the sum of several segments with
*different economics*. A single P/E or P/B for the whole group is **meaningless** — you would be averaging a
high-margin property developer, a cash-burning EV startup, and a bank stake into one number that describes
none of them. The international convention is **Sum-of-the-Parts (SOTP)**: value each segment on its *own*
sector multiple (property on P/B–NAV, manufacturing on EV/EBITDA, a listed financial stake at its real market
value), add them up, then subtract a **holdco discount** (10–30% in emerging markets, for opacity of the
cash-flow up to the parent, double taxation, and governance).

**The VN advantage this framework exploits:** several segments are *themselves listed*, so that slice is
**measured directly from BQ** (parent's stake × subsidiary market cap), not estimated. This collapses most of
the SOTP estimation error. We build a **listed-stake coverage ratio** through time:

```
coverage(t) = ParentMarketCap(t) / Σ_s [ stake_s × SubsidiaryMarketCap_s(t) ]      MarketCap = Price × OShares
```

| reading | meaning |
|---|---|
| **coverage < 1** | Parent trades **below the market value of just its listed stakes** → the market assigns **≤ 0** to every unlisted business + net cash. A **holdco discount**. |
| **coverage > 1** | Parent trades **above** its listed stakes → the market **pays up** for unlisted optionality (VinFast at VIC; the plantation→industrial-park landbank at GVR) — or it is simply a premium. |

> **The caveat that IS the point:** coverage ignores (a) unlisted operating businesses and (b) holdco net debt.
> So coverage<1 is **not automatically "cheap"** (it can be *justified* by real holdco leverage), and coverage>1
> is **not automatically "expensive"** (unlisted ops have real value). **coverage is a RELATIVE gauge vs the
> name's OWN history, never an absolute NAV.** Anyone who reads it as "buy below 1.0, sell above 1.0" will be
> run over — see §3.

**Universe (listed parent → listed subs measurable in BQ; unlisted parts noted):**

| Parent | Listed subs in BQ (stake) | Unlisted / qualitative |
|---|---|---|
| **VIC** (Vingroup) | **VHM** (64.9%) | VinFast (cash-burn), Vinpearl, VEF |
| **MSN** (Masan) | **MCH** (68.1%), **TCB** stake (15%) | MSR/MML thin in prune; **WinCommerce** (unlisted retail) |
| **GEX** (Gelex) | **VGC** (50.2%), **GEE** Gelex Electric (78.6%, listed 2022) | — |
| **GVR** (VN Rubber) | **PHR** (66.6%) + **DPR** (55.8%) + **TRC** (60%) | **huge** unlisted plantation + industrial-park landbank |

**Stakes are approximate public economic stakes, HELD CONSTANT through time** (real stakes drifted — VIC
divested VRE 2024, HAG dumped HNG to Thaco 2021, Masan trimmed TCB). Same accepted data limit as SOE state%
(#19) and construction backlog (#18): **BQ has no ownership field.** The absolute premium/discount *level* is
sensitive to this; the *trend / no-mean-reversion / momentum-sign* conclusions (§2–§3) are **invariant** to a
constant stake error (they read the time-shape, which a constant stake preserves exactly).

---

## 1. The snapshot — a clean PREMIUM/DISCOUNT split (PART 0)

Listed-stake coverage, current (2026-06-26):

| Parent | Parent MC | Listed-stake value | **coverage** | reading |
|---|---|---|---|---|
| **VIC** | 1,757 tn | 432 tn (VHM 64.9%) | **4.07×** | **+307% PREMIUM** |
| **GVR** | 128 tn | 8.7 tn (PHR+DPR+TRC) | **14.8×** | **+1376% PREMIUM** |
| **MSN** | 104 tn | 149 tn (MCH 68% + TCB 15%) | **0.70×** | **−30% DISCOUNT** |
| **GEX** | 27 tn | 35 tn (VGC 50% + GEE 79%) | **0.77×** | **−23% DISCOUNT** |

**The split is the finding.** It is *not* random — it maps exactly onto **what the unlisted part carries**:
- **PREMIUM names (VIC, GVR)** — the market pays a large premium over the listed NAV because the *unlisted*
  business carries the story: **VinFast** (an unlisted-domestically EV bet) at VIC, and the **landbank**
  (rubber acreage being converted to industrial parks) at GVR, whose *listed* rubber subs are a trivial **~7%**
  of its cap. You are buying an unlisted call option, not the listed subs.
- **DISCOUNT names (MSN, GEX)** — the market pays *less* than the listed stakes are worth, because the parent
  carries **real holdco leverage and conglomerate complexity**: MSN Debt_Eq ~1.8–2.9, VIC 6.7 (below), the
  cash sitting one level down behind minority interests. The discount is **partly deserved**, not pure
  mispricing — which is exactly why it does not automatically close (§3).

---

## 2. Why a blended parent multiple is a lie — the cash-burn / leverage drag (PART 1)

Consolidation folds a money-loser or a levered arm into the parent's headline ratios and destroys them:

| ticker | 2022Q2 NPM | 2024Q2 NPM | 2026Q1 NPM | 2026Q1 Debt_Eq | 2026Q1 PB |
|---|---|---|---|---|---|
| **VIC** | **−0.082** | 0.022 | 0.041 | **6.67** | **11.3** |
| **VHM** (its property arm) | 0.498 | 0.298 | 0.327 | 2.19 | 2.27 |
| **MSN** | 0.142 | 0.030 | 0.089 | 1.83 | 2.44 |
| **MCH** (its consumer arm) | 0.202 | 0.256 | 0.220 | 0.84 | **10.2** |

**VIC's net margin went NEGATIVE in 2022** (VinFast losses) while its property arm VHM ran +30–50% margins;
VIC's Debt_Eq climbed **3.0 → 6.7** funding VinFast; its PB is **11.3** — a number that reflects *option value
on an unlisted startup*, not the property business. **You cannot value VIC on a consolidated P/E, P/B, ROE or
Debt_Eq** — every one is a blend of incompatible parts. This is Rule 1 ("split by economics, not by ICB code")
applied *inside a single ticker*, and it is the entire reason SOTP exists.

---

## 3. The discount does NOT mean-revert — it is a TRAP, not a signal (PART 2 + PART 4)

The intuitive thesis — *"buy the conglomerate when its holdco discount is unusually deep, ride the re-rating
as it closes"* — is **REFUTED**.

**Stability (PART 2).** Coverage is a **trending / slowly-drifting** series, not one that oscillates around a
stable mean:

| Parent | n | mean | range | AR(1) half-life | **trend vs time** |
|---|---|---|---|---|---|
| VIC | 1967 | 1.86 | [1.17, 5.01] | 153 d | −0.28 |
| MSN | 1563 | 1.46 | [0.56, 2.98] | 259 d | **−0.68** (secular de-rating) |
| GEX | 464 | 0.81 | [0.47, 1.15] | 62 d | **−0.62** (secular de-rating) |
| GVR | 540 | 13.1 | [6.79, 18.4] | 51 d | **+0.55** (premium re-rating) |

Half-lives of **2–9 months** and strong non-zero trend-vs-time correlations (MSN −0.68, GEX −0.62, GVR +0.55)
say the discount/premium **drifts structurally** (MSN and GEX have been *de-rating* for years; GVR *re-rating*
up) rather than mean-reverting. This is the textbook **emerging-market conglomerate discount that never closes.**

**Signal test (PART 4, eval-only).** Pooled Spearman of each parent's **own-history coverage z-score** vs
forward return (`profit_1M/2M/3M`, 3,759 name-days):

| horizon | IC | reading |
|---|---|---|
| profit_1M | **+0.073** | **wrong-signed for the thesis** |
| profit_2M | +0.054 | |
| profit_3M | +0.036 | |

coverage-z **LOW** = deep discount vs own norm. A *positive* IC means **HIGH** coverage-z (premium expanding)
predicts higher forward return — i.e. **premium-MOMENTUM, not discount-reversion.** Buying the deep discount
predicts *worse* returns. The direct basket confirms it:

| Basket (monthly, TC 0.1%) | Full CAGR | Sharpe | MaxDD | Full edge vs B&H | IS 2016-19 | OOS 2020-26 |
|---|---|---|---|---|---|---|
| **ALL 4 parents EW** (naive) | 14.0% | 0.61 | −51.3% | +1.4pp | **−19.1pp** | **+16.2pp** |
| **DISCOUNT-TILT** (hold deepest-own-discount half) | **4.5%** | 0.29 | **−57.6%** | **−8.1pp** | −19.4pp | −0.5pp |

- The **discount-tilt LOSES** — Full 4.5% vs 14.0% for naive EW-all, with a *worse* drawdown. Trading the
  discount is negative-edge.
- Even the naive EW-all "+1.4pp" is **reshuffle luck, not signal**: it is **100% OOS-concentrated**
  (IS −19.1pp / OOS +16.2pp) — the 2020+ VIC+GVR run-up carries the entire edge. Fails the per-year-LOO /
  multiple-testing discipline (Rule: 1–2 years carrying all the edge = luck, not a bearable signal).

---

## 4. Regime — the premium is optionality that deflates violently in stress (PART 3)

Mean coverage by DT5G state:

| Parent | CRISIS | BEAR | NEUTRAL | BULL | EXBULL |
|---|---|---|---|---|---|
| VIC | 1.64 | 1.73 | 1.98 | 1.79 | 1.80 |
| MSN | 1.46 | 1.98 | 1.42 | 1.42 | 1.33 |
| GEX | 1.00 | 0.92 | 0.77 | 0.77 | 1.04 |
| **GVR** | **7.18** | — | 12.91 | **14.73** | 14.36 |

No clean "discount always widens in stress" law — it is **name-specific**, driven by the *subs'* own beta
(MSN's coverage actually *rises* in BEAR because defensive consumer MCH holds up better than the group). The
one sharp, actionable pattern: **GVR's premium collapses 14.7× (BULL) → 7.2× (CRISIS)** — the unlisted-story
premium has **higher downside beta than its listed-stake NAV.** General rule: **a premium holdco is a long
unlisted call option; that option gets marked down hardest exactly in CRISIS.** Size it as optionality.

---

## 5. VinFast / cash-burn risk — it shows up in consolidated CF, confirming SOTP logic

The dispatch asked whether a money-burning subsidiary (VinFast) drags the parent faster than the other segments'
NAV grows. It does, and the drag is *visible in consolidated financials* (§2): VIC's consolidated NPM went
negative and Debt_Eq doubled to 6.7 — the burn is funded by holdco leverage. **This is precisely why you must
value the profitable parts (VHM) *separately* rather than on a blended parent metric** that the burn has
poisoned. The consolidated CF_OA is lumpy and negative in many quarters at both VIC and MSN — a blended
cash-flow yield on the parent is therefore uninterpretable; SOTP (value VHM on its own, treat VinFast as a
separately-sized option) is the only coherent read.

---

## 6. Verdict + rules this archetype adds (for `sector_watchlist_framework.md`)

**VERDICT: a valuation-DIAGNOSTIC LENS (like 5F moat / SOE governance), NOT a book and NOT a gate.** SOTP tells
you *what you are paying for* (listed NAV vs unlisted burn/landbank) and lets you size the optionality/leverage
risk — it does **not** generate a tradeable signal. Do not wire: N=4, the discount is a trap (does not
mean-revert; momentum dominates; IC wrong-signed), and any basket edge is OOS reshuffle-luck. Consistent with
every prior sector: **lens, not book (Rule 3).**

The five SOTP rules to carry forward:
1. **A blended P/E/P/B on a conglomerate is a lie — value the parts.** VIC PB 11.3 with once-negative NPM is
   VinFast option value, not the property business. Split the parent by economics (Rule 1, applied to one ticker).
2. **`coverage = ParentMC / Σ(stake × listed-sub MC)`.** <1 = leverage/complexity discount (MSN 0.70, GEX 0.77);
   >1 = the market pays up for unlisted optionality (VIC 4.07 = VinFast, GVR 14.8 = landbank). Read it *relative
   to the name's own history*, never as an absolute buy/sell line.
3. **The discount does NOT mean-revert — deep discount is a TRAP.** Pooled coverage-z IC is *positive*
   (premium-momentum), the discount-tilt basket LOSES (−8.1pp), the series trend/de-rate. Never trade the discount.
4. **Any conglomerate-basket edge is reshuffle-luck** — 100% OOS-concentrated (IS −19pp / OOS +16pp). Fails LOO.
5. **A premium holdco is a long unlisted call option; it deflates violently in CRISIS** (GVR 14.7×→7.2×). Size
   the premium as optionality, not as NAV.

**No name added to the buy watchlist and none to the permanent-exclude list** — the underlying operating names
(VHM, MCH, VGC…) are handled by their own sector frameworks (RE, F&B, building-materials). This archetype adds a
**valuation-method annotation** to apply whenever a listed group spans incompatible segments.

---

### Auditability
Screen `holdco_sotp_screen.py` → `data/holdco_{all,discount}_monthly.csv` + `data/holdco_sotp_verdict.json`.
Self-check 0 VND PASS (all 0e0, discount 0e0), threads=1, walk-forward IS/OOS. Prices/forward returns from
`ticker_prune` cache; OShares ASOF-forward-filled from `ticker_financial`; MarketCap = unadjusted Price × OShares;
DT5G regime from `vnindex_5state_dt5g_live`. Ownership stakes hand-curated from public structure, held constant
(no BQ field) — absolute level sensitive, trend/signal conclusions invariant. Results pinned in
`data/results_registry.md`. No production code touched.
