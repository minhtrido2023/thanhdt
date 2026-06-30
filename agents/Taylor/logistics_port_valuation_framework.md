# Logistics / Port / Shipping — valuation & compounder framework (VN)

**Author:** Taylor (Quant) · **Job:** Taylor_20260630_054646 · **For:** DollarBill, user (via Mike)
**Scope:** the maritime/transport-infrastructure complex needs its own valuation lens — it is NOT one
business. Under two ICB codes sit three structurally different economics. Treating them with one P/E
or one P/B screen is the mistake; this doc splits them and maps each to BQ columns, then defines two
screens. Backed by a point-in-time backlook (`ticker_financial` cache, 2014-2024).

---

## 0. Universe (BQ, ICB-coded — verified)

| ICB | meaning | names in `ticker_prune` |
|-----|---------|--------------------------|
| **2777** | Transport infrastructure & services (ports, airports, cargo terminals, logistics) | GMD, VSC, HAH, ACV, DVP, PHP, SGP, DXP, NCT, SGN, DL1, TMS, STG, ILB, DS3, TCW (16) |
| **2773** | Marine transportation (tankers, dry-bulk, container shipping lines) | PVT, VOS, VIP, VTO, SWC, GSP, SFI (7) |

> Note: ICB 2777 also holds **airport** concessions (ACV monopoly, SGN/NCT cargo terminals) — these
> are infrastructure/concession plays and belong in the Port screen by economics, not just by code.
> **HAH** (container shipping line) sits in 2777 by code but behaves like a cyclical shipper; **GMD**
> is the hybrid (deepwater port Gemalink + logistics/shipping). Both are kept in the Port screen per
> their ICB but flagged as cycle-sensitive.

---

## 1. Three economics, three valuation primaries

### A. Ports / transport infrastructure (REIT-/concession-like)
- Deepwater quay walls + port concessions are **non-reproducible** → durable moat when utilised.
- Heavy front-loaded capex, large D&A → **P/E is distorted; EV/EBITDA is primary** (`EVEB`).
- Secondary: **PCF** (price/cash-flow, D&A-neutral), **P/B**, **DY** for mature cash-cow ports.
- Moat = **ROIC** ≥ concession-economics threshold. **CAVEAT (backlook):** a 5-yr-average ROIC
  (`ROIC5Y`) is *suppressed during the build phase* — GMD ran ROIC5Y 1.5%→7.7% the whole decade
  because Gemalink capex sat on the balance sheet before it earned. Use **ROIC5Y≥5%** (not 8%) and
  read **ROIC_Trailing** (current earnings power, post-ramp) as the real moat signal.
- **CF_Invest** separates phase: large negative = build-out (capex), small = maintenance/cash-cow.
  FCF = `CF_OA_P0 + CF_Invest_P0` (CF_Invest is signed negative). FCF>0 = harvesting; <0 = investing.
- Throughput (TEU) not in BQ → proxy with sustained **Revenue_YoY**.
- Leverage: prefer Debt/EBITDA; BQ proxy = `Debt_Eq_P0` + `IntCov_P0`. **Net-cash ports
  (DVP, VSC) have IntCov = NaN** — that is the *best* case, not a fail → treat NaN as pass.

### B. Shipping / marine transport (deep cyclical — opposite playbook)
- No moat; earnings ride freight rates (Baltic Dry / tanker rates — **not in BQ**).
- **Trough = P/B < ~0.9** (market cap below fleet replacement value); boom = low EV/EBITDA.
- Classic entry: **P/B<0.9 in the bust + CF_OA turning positive + NP improving**, with leverage
  *survivable*. The danger is identical-looking cheap-but-dying: cheap P/B + over-leverage +
  cash burn (the VOS pattern). The screen's job is to tell them apart.
- Freight-rate spikes → proxy with **Revenue_YoY** jump and **NP_P0 > NP_P4** turn.
- Fleet age / fuel efficiency not in BQ.

### C. GMD — the hybrid
- Port piece (Gemalink Cai Mep, Nam Hai Dinh Vu) → value as infrastructure (EVEB + ROIC + Rev growth).
- Logistics/shipping piece → service-business margins.
- Blend: it screens in the **Port screen** (its ICB), valued on EVEB + ROIC_Trailing + stable Rev.

---

## 2. BQ column map

| concept | column(s) |
|---|---|
| port cheapness (primary) | `EVEB` (EV/EBITDA) |
| cash-flow valuation | `PCF` |
| FCF (harvest vs build) | `CF_OA_P0 + CF_Invest_P0` |
| cash quality gate | `CF_OA_3Y > 0` |
| concession moat | `ROIC5Y` (≥5% build-tolerant), `ROIC_Trailing` (real earnings power) |
| mature-port yield | `DY` |
| leverage health | `Debt_Eq_P0`, `IntCov_P0` (NaN = net cash = pass) |
| throughput proxy | `Revenue_YoY_P0`, `Revenue_YoY_P4` |
| shipping trough | `PB` (<0.9) |
| cyclical turn | `NP_P0 > NP_P4`, `CF_OA_P0 > 0`, `Revenue_YoY_P0` spike |
| margin trajectory | `GPM_P0`/`GPM_P4`, `NPM_P0` |

---

## 3. Backlook at known entries (point-in-time `ticker_financial`, no look-ahead)

**Ports (2777):**
| name | quarter | P/B | EVEB | ROIC5Y | ROIC_TTM | IntCov | FCF | read |
|---|---|---|---|---|---|---|---|---|
| GMD | 2014Q4 | **0.67** | 3.9 | 1.5% | 7.7% | neg | +188B | deep value BUT ROIC not yet earned (Gemalink pre-ramp) — **uncapturable by quality gate w/o foresight** |
| GMD | 2020Q1 | 0.80 | 8.2 | 4.3% | 32% | 4.5 | +72B | concession ramping; cheap-ish; **passes once ROIC5Y≥5%** ~2020+ |
| VSC | 2020Q1 | **0.63** | **1.9** | 12% | — | 77 | +51B | high-quality port, net-cash, cheap → clean ENTRY |
| DVP | 2020Q1 | 1.07 | 4.7 | 16% | 94% | **NaN(net-cash)** | +98B | cash-cow pure-play port, NPM 46-60%, DY 2-4% → ENTRY (NaN IntCov must pass) |
| PHP | 2020Q1 | **0.63** | 4.2 | 7.5% | 49% | 16 | +93B | Hai Phong port, near-zero debt, 0% DY (state-owned) → ENTRY |

**Shipping (2773):**
| name | quarter | P/B | EVEB | Debt_Eq | IntCov | CF_OA_P0 | NP turn | read |
|---|---|---|---|---|---|---|---|---|
| PVT | 2020Q1 | **0.47** | 2.9 | 0.93 | 3.4 | **+196B** | improving | textbook trough buy → ENTRY |
| VOS | 2016Q4 | **0.25** | 16 | **5.74** | 2.3 | **−20B** | NP −122B | LEVERAGE TRAP — cheapest P/B, un-survivable → **EXCLUDE** |
| VOS | 2020Q1 | **0.30** | 8.1 | **3.91** | **−1.86** | **−21B** | NP loss | TRAP — can't cover interest → **EXCLUDE** |
| VOS | 2022Q4 | 1.01 | 1.7 | 0.75 | 6.3 | +CF, ROIC+ | recovered | de-levered + freight boom → legit (now passes) |

**Conclusions that shape the screens:**
1. **ROIC5Y≥8% is wrong for VN ports** — kills GMD always, borderline-kills PHP. Relax to **≥5%**;
   read ROIC_Trailing for real moat. GMD's *deep-value* 2014 entry needed Gemalink foresight →
   structurally uncapturable (parallel to banking-VCB / retail-PNJ / RE-NTC premium re-rate misses).
2. **IntCov NaN = net cash = the best ports** (DVP, VSC) → NaN must PASS, never exclude.
3. **DY>4% as a hard gate is wrong for VN** — best ports reinvest / are state-owned (0% DY). Use
   **FCF>0 OR DY>4%** ("return cash, or growing into capex").
4. **Shipping: PB<0.9 alone is a trap detector, not a buy signal.** The Debt_Eq<2.0 + CF_OA>0 +
   NP-improving conjunction is what cleanly separates PVT-2020 (buy) from VOS-2016/2020 (avoid),
   and correctly *admits* VOS only after it de-levered (2022Q4).

---

## 4. The two screens (point-in-time, monthly EW, T+1, TC 0.1%)

**Screen A — Port / Infrastructure** (universe = ICB 2777 ∩ ticker_prune; no hard ADV floor — port
pure-plays are sub-2B ADV, flag illiquidity instead of excluding):
- `EVEB ∈ (0, 10)` — cheap vs earnings power (primary)
- `ROIC5Y ≥ 0.05` — concession economics, build-tolerant
- `CF_OA_3Y > 0` — genuinely cash-generating
- `FCF = CF_OA_P0 + CF_Invest_P0 > 0` **OR** `DY > 0.04` — harvest cash, or grow into capex
- `IntCov_P0 > 2.0` **OR** `IntCov_P0` is NaN (net-cash) — service debt easily
- `Revenue_YoY_P0 ≥ −0.10` — throughput stable, not collapsing
- rank `z(−EVEB) + z(ROIC_Trailing) + z(FCF_yield)`, top-10.

**Screen B — Shipping cyclical (trough buy)** (universe = ICB 2773 ∩ ticker_prune):
- `PB ∈ (0, 0.9)` — buy below fleet value
- `CF_OA_P0 > 0` — still generating cash at the trough
- `Debt_Eq_P0 < 2.0` — survivable leverage (the anti-VOS gate)
- `NP_P0 > NP_P4` — earnings turning up
- rank `z(−PB) + z(CF_OA) + z(NP turn)`, take-all (thin).
- **DEPLOY FLAG: shipping is high-beta — only size in DT5G NEUTRAL/BULL.** Empty months = hold cash
  (the screen is *designed* to be empty outside troughs — that is the discipline, not a defect).

---

## 5. Results — see `data/results_registry.md` (job Taylor_20260630_054646) and bus finding.
