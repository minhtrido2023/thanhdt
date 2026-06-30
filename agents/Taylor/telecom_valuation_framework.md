# Telecom — valuation & entry framework (VN)

**Author:** Taylor (Quant) · **Job:** Taylor_20260630_060226 · **For:** DollarBill, user (via Mike)
**Scope:** VN listed telecom is a **structurally thin** sector — the Big-3 operators (Viettel, VNPT,
MobiFone) are state-owned/unlisted. The investable listed names are infrastructure/service plays that
only matured into the **liquid quality universe (`ticker_prune`) in June 2026**. This doc maps telecom
economics to BQ, runs a point-in-time **backlook** (full `ticker`, 2017-2026), and concludes with an
honest verdict: a real & strong valuation lens, but a universe too thin to backtest as a standalone book.

---

## 0. Universe (BQ, ICB-coded — verified)

| ICB | meaning | names | full-`ticker` history | in `ticker_prune`? |
|-----|---------|-------|----------------------|--------------------|
| **6535** | Fixed-line telecom | **FOX** (FPT Telecom), TTN (Tien Thanh, micro) | FOX 2017-01→, TTN 2017-04→ | **only since 2026-06-19** |
| **6575** | Mobile telecom | **VGI** (Viettel Global) | 2018-09→ | **only since 2026-06-19** |
| **2357** (construction) | tower / telecom-infra | **CTR** (Viettel Construction) | 2017-10→ | yes (2018+) |

**Adjacent (IT/tech, NOT pure telecom — classified 95xx):** FPT (9537, the parent — IT+telecom mix),
CMG (9533, CMC), ELC (9578, Elcom equipment), SGT/ITD/ICT. These are technology names; FPT's telecom
exposure is via its FOX stake, so **read FOX directly** rather than diluting through FPT.

> **The core liquidity fact:** FOX and VGI traded on **UPCOM since 2017-2018** but were too illiquid for
> `ticker_prune` (the quality/liquid universe) until **June 2026**. So a backtest on the *tradeable*
> quality universe has ~1 month of history → impossible. The backlook below runs on full `ticker`
> (includes the illiquid UPCOM tail) and is a **valuation lens**, not a tradeable backtest.

---

## 1. Telecom economics → valuation primary

Telecom is infrastructure-heavy and mature — D&A from network assets (spectrum, towers, fiber, last-mile)
distorts P/E. Standard global practice, mapped to BQ:

- **Primary: EV/EBITDA (`EVEB`)** — neutralises the heavy D&A. Global benchmark: mature telecom **4-8x**,
  growth telecom 8-12x. **This is the single best entry signal for VN telecom (see §3).**
- **FCF over earnings:** `FCF = CF_OA_P0 + CF_Invest_P0` (CF_Invest signed negative = capex). Telecom has
  high EBITDA margin but heavy capex → FCF much thinner than EBITDA. Positive FCF = harvesting phase;
  negative = network build-out (data-center / tower capex).
- **Margin trajectory (`NPM_P0`, GPM from `ticker_financial`):** scaling a network → margin **expands**
  over time. A rising NPM is the moat showing up in the P&L.
- **Moat proxy: `ROIC5Y`** (spectrum/last-mile/tower value not on balance sheet). Rising ROIC5Y = real
  infrastructure moat compounding.
- **Dividend Yield (`DY`):** mature fixed-line can be a yield play (DY>4% attractive). VN reality: FOX
  pays modest 0.5-2%; VGI/CTR pay ~0 (growth/reinvest). VN telecom is **not** a yield sector yet.
- **Leverage (`Debt_Eq_P0` + `IntCov_P0`):** Net Debt/EBITDA 1.5-3x OK, >4x dangerous. BQ proxy: De<3
  with IntCov>1.5. (ARPU / subscriber / Net-Debt-EBITDA not directly in BQ → proxy with Revenue_YoY +
  Debt_Eq/IntCov.)

---

## 2. The three listed economics (one size does NOT fit)

### A. FOX — FPT Telecom (fixed-line broadband + data center). **The one genuine quality telecom.**
- Last-mile fiber moat; broadband subscriber base + emerging DC business.
- **Margin expansion is the story:** NPM ~10% (2017-2020) → **~20% (2022-2026)** as broadband scaled.
- **ROIC5Y 13.5% → 18.8%** (steady rise = durable moat).
- FCF positive most years (CF_OA 560-940B vs capex 170-570B) — but **2026 capex spike (DC build) flips FCF negative**.
- Leverage healthy: De 1.3-2.1, IntCov 8-14.
- DY modest 0.5-2.1%.

### B. CTR — Viettel Construction (tower-co / telecom-infra). **Tower compounder.**
- Towers + B2B construction; the closest VN analog to a global tower REIT.
- **ROIC5Y 10% → 24%** (towers compound beautifully); PE 10→27 over the decade = multi-bagger.
- Heavy growth capex (CF_Invest large negative) → FCF often negative (building towers).
- De rising 1.5→2.9, IntCov compressing 81→6 (watch leverage as it builds).

### C. VGI — Viettel Global (international mobile, Africa/SE-Asia). **Speculative turnaround, NOT value.**
- Loss-making / FX-volatile early (negative PE 2018/2021/2022 from overseas FX).
- **EVEB never cheap** (17-55x) — market prices turnaround optionality, not current EBITDA.
- ROIC5Y low (1-4%) until **2025-2026 finally turning (7.6→11.6)**; NPM −0.1→+0.3.
- Huge CF_OA but heavy capex. **Do not value VGI on EVEB** — it is a momentum/turnaround book, screen it elsewhere.

---

## 3. Backlook — EVEB entry discipline works powerfully (full `ticker`, 2017-2026)

Forward **12-month** total return from semi-annual (Jan/Jul) snapshots, tagged by entry `EVEB`:

| name | cheap entries (EVEB ≤ ~8) → fwd-12M | expensive entries (EVEB ≥ ~9) → fwd-12M |
|------|--------------------------------------|------------------------------------------|
| **FOX** | 2019-07 (5.3)→**+44%**, 2020-01 (5.6)→**+57%**, 2020-07 (6.2)→**+101%**, 2021-01 (6.5)→**+56%**, 2023-01 (7.3)→**+56%**, 2023-07 (6.4)→**+155%**, 2024-01 (9.0)→**+95%** | 2021-07 (10.3)→−9%, 2022-01 (9.1)→−27%, 2022-07 (10.1)→−10%, 2024-07 (13.6)→+1%, 2025-01 (11.8)→+3% |
| **CTR** | 2019-01 (3.5)→**+132%**, 2019-07 (6.0)→**+94%**, 2020-01 (7.7)→**+113%**, 2020-07 (8.4)→**+141%**, 2023-01 (8.1)→**+75%**, 2023-07 (11.6)→**+108%** | 2022-01 (13.7)→−25%, 2024-07 (19.2)→−28%, 2025-01 (15.3)→−32% |

**Read:**
1. **EVEB < 8 entry → large forward returns; EVEB > 9 → flat/negative.** A clean, monotone, repeatable
   signal across both names and across the IS/OOS divide.
2. **EVEB-cheap alone is NOT sufficient — needs the margin/ROIC expansion confirming.** FOX's 2017-2018
   entries were EVEB ~6 (cheap) but went FLAT (+13/+1/+5/−5%) because broadband margin expansion hadn't
   started yet (NPM still ~10%, flat). The signal turned ON from **2019** once NPM began climbing and
   ROIC5Y rose. So the screen pairs **cheap EVEB AND rising NPM/ROIC**.
3. **CTR shows the same monotonicity** even as a growth-capex tower-co — buy cheap EVEB, towers compound.

---

## 4. Telecom screen criteria

Entry = a quality telecom-infra name trading cheap on EBITDA with the moat confirming in margins:

```
EVEB > 0 AND EVEB < 8            # cheap vs global mature-telecom 4-8x benchmark
AND NPM_P0 rising OR ROIC5Y > 12 # margin/moat expansion confirming (NOT cheap-EVEB alone)
AND CF_OA_P0 > 0                 # operating cash generative
AND Debt_Eq_P0 < 3.0 AND (IntCov_P0 > 1.5 OR IntCov_P0 IS NULL)   # leverage sane (NaN IntCov = net-cash = pass)
AND Revenue_YoY_P0 > 0           # subscribers/ARPU growing (proxy)
# DY > 3% OR ROIC5Y > 10% as a tilt, not a hard gate (VN telecom pays little)
# EXCLUDE VGI-type: EVEB never cheap + ROIC5Y < 5 = turnaround, screen elsewhere
```

Script: `telecom_screen.py` (point-in-time, monthly snapshots on full `ticker`; NPM-rising via 6m-lag).

**Screen result (100 monthly snapshots, 2017-2026, universe FOX/VGI/CTR/TTN):**
- **FLAGGED** (cheap EVEB + margin/moat confirm): n=**10**, avg fwd-12M **+142.7%**, winrate **100%**
- **UNFLAGGED** (expensive / not confirming): n=90, avg fwd-12M +34.2%, winrate 64%
- **SPREAD = +108.5pp.** Clean, monotone — but **n=10 is thin** and the +34% unflagged baseline shows
  these high-beta UPCOM names ran hot generally in the 2020-2021 / 2023 bull windows. The lens adds real
  timing edge (+108pp by waiting for cheap EVEB), but the small-n + structural illiquidity is why this is
  a lens, not a book. Output: `data/telecom_screen_entries.csv`.

---

## 5. Verdict — REAL & strong lens, but un-backtestable as a sector (universe just became investable)

- **The signal is real and strong** — EVEB<8 + margin-confirm entry on FOX/CTR delivered +44% to +155%
  forward-12M repeatedly, IS and OOS, with the expensive entries flat/negative. This is the cleanest
  single-metric entry discipline of any sector screened so far.
- **But it is NOT a backtestable standalone book.** The investable pure-telecom universe is effectively
  **one name (FOX)** plus a tower-co (CTR) and a turnaround (VGI). FOX/VGI only entered the liquid quality
  universe (`ticker_prune`) in **June 2026** — historical tradeability was UPCOM/illiquid, conflicting with
  the fleet's established finding that the VN illiquidity premium is not realistically capturable. A
  monthly-rebalance backtest on the quality universe has ~1 month of data.
- **Actionable conclusion: telecom is a WATCHLIST / valuation-LENS, not a book — but the sector just became
  investable for the first time.** With FOX/VGI/CTR liquidity maturing (entered `ticker_prune` 2026-06), a
  forward watchlist is now warranted:
  - **FOX** = the genuine quality compounder. **Entry discipline: EVEB < 8 with NPM/ROIC still rising.**
    As of 2026 it sits at EVEB ~12-13 (NPM 20%, ROIC 18.8%) — quality intact but **NOT a cheap entry**; wait
    for an EVEB pullback toward <8 (last seen 2023).
  - **CTR** = tower compounder; same EVEB<8 entry discipline, watch the rising leverage (IntCov compressing).
  - **VGI** = do not value on EVEB; it's a momentum/turnaround name — route to the momentum book, not here.
- **Orthogonality:** the EVEB-primary telecom lens is orthogonal to the 8L composite (8L value =
  ey+cfy+ps, has no EV/EBITDA term) and to the prior sector compounder screens (different names entirely;
  no overlap with custom30V). It adds a sector-entry lens, not a new alpha source.

**Self-check:** no NAV simulation (no tradeable history) → no 0-VND check applicable; the backlook
forward-return table (§3) is the auditable artifact, recomputed directly from full `tav2_bq.ticker`
adjusted Close. AUDIT_END 2026-06-29.
