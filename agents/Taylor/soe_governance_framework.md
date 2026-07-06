# State-Owned-Enterprise (SOE) GOVERNANCE Archetype — Sector #19 Framework

> **Author:** Taylor (Quant) · **Job:** Taylor_20260706_040038 (dispatch from Mike) · **For:** DollarBill, user (via Mike)
> **Scope:** RESEARCH-ONLY, new files only (`soe_governance_screen.py` + this doc + `data/soe_*`). Production (custom30V/BAL/LAG/DT5G/rating_8l.py) untouched.
> **This is NOT a sector — it is a cross-cutting GOVERNANCE NOTE**, analogous to the 5F moat overlay. The deliverable is a governance *lens*, not a book and not a new gate.
> Backtest self-check 0 VND PASS (soe_broad 4e-6, privpeer 7e-6, cashcow 2e-6), threads=1, walk-forward IS(2014–19)/OOS(2020–26). Point-in-time on 2014→2026-04 `ticker_prune` + `ticker_financial` cache. `profit_*` eval-only, never a live filter.

---

## 0. What this archetype IS

State-controlled listed companies (**State holds >50%, or de-facto control**). They are already scattered
across sectors screened earlier — GAS/PLX in energy #9, POW/NT2 in power, VCB/CTG/BID in banking, BVH in
insurance — so this is **not a new industry**. It is a *governance archetype* that cuts across all of them,
defined by four features a purely private capital-allocator does not share:

| Feature | Why it changes the analysis |
|---|---|
| **(a) Dividend = partly a state-budget decision** | The State shareholder (SCIC / a line ministry / PVN / SBV) can pull cash UP for the budget (cash-cows: GAS, VEA, PLX) **or force RETENTION** for policy (state banks VCB/CTG/BID pushed to pay STOCK dividends + retain to build CAR under Basel II). "SOE ⇒ high stable DY" is only **half true** — the policy runs both directions. |
| **(b) Thin free-float** | 65–96% of shares locked in State hands, non-trading. Small tradeable float → **structurally low turnover**, hard execution — even for a "large-cap." *The cleanest measurable SOE signature.* |
| **(c) Policy price control caps upside asymmetrically** | Fuel retail (PLX), electricity (POW/NT2 sell to the EVN single-buyer at administered PPA prices), gas — selling prices are set for public-policy goals, not profit-max. The State caps your margin in the good times. |
| **(d) State action = discrete event risk/opportunity** | Divestment (SAB 2017 → ThaiBev at a huge premium; the SCIC/VNM overhang), forced capital raises, restructuring. Un-modellable in BQ → noted qualitatively. |

**Universe + approx state % (public knowledge, controlling holder):** GAS 95.8 (PVN) · PLX 75.9 (CMSC) · POW 79.9 (PVN) · ACV 95.4 (CMSC) · BSR 92.1 (PVN) · VEA 88.5 (MoIT) · NT2 59.4 (PV Power) · VCB 74.8 (SBV) · CTG 64.5 (SBV) · BID 81.0 (SBV) · BVH 65.0 (MoF) · SAB 36.0 (post-ThaiBev divest) · VNM 36.0 (SCIC, no longer controlling). Private control group (matched sub-sector): REE/HDG/GEG/PPC, ACB/MBB/TCB/VPB/HDB, BMI/PVI, QNS.
**BQ has no state-ownership field** — tags are hand-curated from public ownership structure. This is the same accepted data limit as backlog (construction) and DY (Rule 2).

---

## 1. The float signature — the one thing that is cleanly measurable (PART 0)

Annual **share turnover = Σ Volume / shares-outstanding** (unit-free), 2024–25:

| | median turnover | reading |
|---|---|---|
| **SOE** | **0.181** | ~2.4× thinner |
| **Private peer** | **0.443** | |

**Spearman(state %, turnover) = −0.51** across all 25 names — a strong monotone relationship: *more state
ownership → thinner float → lower turnover.* The most locked-up flagships are the most float-starved:
**ACV 0.040 · VCB 0.105 · GAS 0.115 · VEA 0.117 · BID 0.124.**

> **Exceptions matter:** POW 0.691, NT2 0.650, VNM 0.428, PLX 0.406 trade freely *despite* state control —
> their ~20–40% public float is deep enough and they are retail momentum favorites. **So "SOE = illiquid" is
> true for the high-lock flagships (ACV/GAS/VCB/VEA/BID), NOT universal.** Read the turnover, don't assume.

**Deploy:** for a high-lock flagship, size for the thin float (execution/impact constraint) — this is a
liquidity fact `Trading_Value` alone under-states, because a large notional ADV can still be a tiny fraction
of the (mostly locked) cap.

---

## 2. Governance is a mild return DRAG, not an alpha factor (PART 1 signal test)

Spearman IC vs forward T+20/40/60 return (`profit_1M/2M/3M`, **eval-only**), 63,679 name-days, 25 names, 2014→2026:

| Factor | IC(3M) | Read |
|---|---|---|
| **`state_pct`** | **−0.034** | **Mildly NEGATIVE. State control is a small forward-return drag, not a factor to harvest.** |
| `turnover` (liquidity) | +0.019 | ~zero — thin float doesn't *predict* return, it's an execution constraint. |
| `DY` (when present) | +0.027 | ~zero — the yield does not rescue it (see §4 income trap). |
| `PB` (absolute) | −0.174 | The generic value factor (cheap → better) — **not SOE-specific**; present market-wide. |
| `pb_rel` = PB/PB_MA1Y | −0.052 | Weak trough proxy. |

**Mean forward return, SOE vs PRIV:** T+60 **3.16% (SOE) vs 4.25% (PRIV)** — a realized ~1pp/quarter drag,
consistent at every horizon (T+20 1.13 vs 1.43, T+40 2.20 vs 2.81). **Governance is a risk/return LENS, never
a selection factor.**

---

## 3. There is NO governance discount to harvest — flagships trade a PREMIUM (PART 2)

The intuitive thesis ("SOEs are cheap because of governance/float/policy risk → buy the discount") is **REFUTED.**
Within every sub-sector that has both state and private names, the State flagship trades a **premium**:

| Sub-sector | SOE avg PB / PE | Private avg PB / PE | SOE/PRIV PB | verdict |
|---|---|---|---|---|
| **Power** | 1.27 / 18.1 | 1.25 / 12.5 | **1.02×** | ~flat |
| **Banks** | 2.01 / 13.6 | 1.51 / 9.4 | **1.33×** | **PREMIUM** |
| **Insurance** | 2.33 / 28.3 | 1.10 / 12.4 | **2.12×** | **PREMIUM** |

The index-heavyweight state flagships (VCB, BVH, GAS PB 3.4, SAB PB 5.8, VNM PB 6.2) earn a **scarcity /
blue-chip / foreign-favorite premium** that *outweighs* the governance-and-thin-float discount. There is no
"buy the cheap SOE" edge: a state name trading cheap-PB is cheap for a policy/quality reason (BSR refinery
cyclicality, PLX price-control losses), not a mispricing. **Do not overweight a name FOR being a state blue-chip
— you pay up and earn less (§2).**

---

## 4. The high-DY "yield play" is a documented INCOME TRAP (PART 3 backtests)

Three EW monthly baskets, TC 0.1%, liquidity-gated (ADV≥10B), hold-cash-when-empty. NAV is **price-only**
(dividends not reinvested — the caveat is handled explicitly below).

| Basket | Full CAGR | Full Sharpe | Full MaxDD | OOS 2020-26 edge | Read |
|---|---|---|---|---|---|
| **A — SOE-controlled broad** (GAS/PLX/POW/NT2/BSR/VCB/CTG/BID/BVH/VNM) | 9.45% | 0.48 | **−48.1%** | +0.06pp (≈flat) | **Lags B&H (−0.78pp), worse Sharpe & DD.** State-blue-chip beta with no edge. |
| **B — Private-peer matched** (REE/HDG/GEG/ACB/MBB/TCB/VPB/HDB/BMI/QNS) | **14.50%** | **0.69** | −49.4% | **+9.79pp** | The **control group clobbers it** — same industries, private governance compounds far better. |
| **C — SOE high-DY cash-cow** (GAS/PLX/POW/NT2/BSR/PPC) | **4.53%** | 0.30 | **−58.2%** | +0.44pp | **The pure yield play. IS −11.67pp, Calmar 0.08.** |

**The income-trap proof (Basket C):** price-only CAGR 4.53% **+ ~4.5pp/yr gross dividend ≈ 9.0% total-return,
still LAGS B&H 10.23%** — with a −58% drawdown. The high, "stable" dividend does **not** compensate for price
stagnation; you collect the coupon and lose it (and more) in the drawdown. This is the textbook income trap.

**The A-vs-B gap is the money finding:** 9.45% (SOE) vs 14.50% (private), *same sectors* → **state control is a
~5pp/yr realized return drag** — the governance drag of §2 shows up hard in a portfolio. (Caveat: B is not a
perfectly weight-matched hedge — it carries more high-beta banks/brokers — so read A-vs-B as directional, not a
clean spread; but A and C each lag B&H **independently**, which needs no matching assumption.)

---

## 5. Policy-risk case studies (qualitative — the un-modellable event layer)

1. **PLX (Petrolimex), 2022** — the MoIT/MoF retail fuel **price ceiling lagged the oil spike**; Petrolimex
   booked losses in a *record* oil year. The State caps your margin exactly when a private refiner/retailer
   would earn most. **Policy caps upside (feature c).**
2. **POW / NT2 (power)** — sell to the **EVN single buyer at administered PPA prices**; cannot pass gas-cost
   through. Margin is policy-set, not market-set — why the power SOEs show ~flat valuation and no compounding.
3. **SAB (Sabeco), 2017** — the State **divested 53.59% to ThaiBev (Vietnam Beverage) at ~VND 320k**, a large
   premium — a discrete windfall event, then ThaiBev-era governance. **State action = event (feature d).**
4. **VCB / CTG / BID (state banks)** — the **SBV forced stock dividends + retention to build CAR** under Basel
   II. The "SOE cash-cow high-DY" story is **INVERTED** here: the state shareholder wanted *retention*, not
   budget-payout. Confirms the dividend policy is bifurcated (feature a), not monotone.
5. **GAS / VEA (genuine cash-cows)** — PVN/MoIT pull cash **up** for the budget → high, sticky payout (VEA DY
   printed ~15% in a declaration quarter). The real budget-payout names — but per §4 still an income trap.
6. **VNM (SCIC divestment overhang)** — a repeatedly-signalled structural *seller* (SCIC ~36%) that caps
   re-rating and periodically pressures the tape. State-as-seller is its own overhang.

---

## 6. Verdict + rules this archetype adds (for `sector_watchlist_framework.md`)

**VERDICT: a cross-cutting GOVERNANCE NOTE (like 5F moat), NOT a book and NOT a new gate.** State ownership is a
mild drag + a risk lens; it does not select, it does not discount-harvest, and it must not be wired as a gate
(gating on state-ownership would just eject VCB, which banking already treats as archetype-B; and it is already
partly captured by the value/quality factors). Consistent with every prior sector: **lens, not book (Rule 3).**

The five governance rules to carry forward:
1. **Thin float is the measurable SOE signature** — turnover ∝ −state% (IC −0.51). Size high-lock flagships
   (ACV/GAS/VCB/VEA/BID) for the *locked* float, not the headline ADV. NT2/POW/PLX/VNM are the liquid exceptions.
2. **Governance is a ~1pp/quarter realized DRAG** (state% IC −0.034; SOE basket ~−5pp/yr vs identical-sector
   private peers). **Don't overweight a name for being a state blue-chip** — you pay a premium and earn less.
3. **DY on an SOE is a POLICY variable, not a free-cash-flow signal** — bifurcated (budget-payout cash-cows
   GAS/VEA vs regulator-forced-retention state banks). The high-DY yield-play is an **INCOME TRAP** (total-return
   still lags, −58% DD). Reinforces Rule 2 (DY uncapturable) with a *behavioral* reason, not just a data gap.
4. **No governance discount to buy** — flagships trade a scarcity PREMIUM (banks 1.33×, insurance 2.12× PB). A
   cheap-PB SOE is cheap for a policy/cyclical reason (BSR/PLX), not a mispricing.
5. **Policy price-control caps upside asymmetrically (PLX/POW) + state action (divest/raise/overhang) is discrete
   event risk** — un-modellable in BQ, carry it as a qualitative flag on any state-controlled name.

**No name is added to the buy watchlist and none to the permanent-exclude list** — the state blue-chips
(VCB/GAS/etc.) are already handled by their own sector frameworks (banking archetype-B, energy). This archetype
adds a **governance annotation** to apply on top when a name carries State control.

---

### Auditability
Screen `soe_governance_screen.py` → `data/soe_{broad,privpeer,cashcow}_monthly.csv` + `data/soe_governance_verdict.json`.
Self-check 0 VND PASS (4e-6 / 7e-6 / 2e-6), threads=1, walk-forward IS/OOS. Prices/forward returns from
`ticker_prune` cache; PE/PB/DY/OShares ASOF-joined from `ticker_financial` (STALE≤120d). State-ownership % is
hand-curated from public ownership structure (no BQ field). Results pinned in `data/results_registry.md`. No
production code touched.
