# MGE=1.3 fedborrow — Per-year breakdown
> Config: RECOVERY_PARK=1 wmax=0.95 pbz=-0.5 dep=0.075 MGE=1.3 CAPIT_ONLY fedborrow gate
> Run: 2026-06-24, Tier-1 local snapshot (signal parquet) + BQ for vni/state/D1
> Script: pt_v23_audit_2014.py v23a none postbull 0 edge

## Key finding: fedborrow gate = fully closed, no leverage ever deployed

At every CAPIT washout event (2014–2026), VNINDEX earnings yield (1/PE) ranged **5.7%–9.1%** —
ALL below the 10% borrow rate. fedborrow gate fires `m=0` at each event →
MGE=1.3 CAPIT_ONLY fedborrow is **de facto unleveraged** (identical to MGE=0).

| CAPIT event | PE | eyield | borrow | gate m |
|---|---|---|---|---|
| 2014-05-08 | 13.3 | 7.5% | 10% | 0.0 |
| 2015-05-18 | 12.2 | 8.2% | 10% | 0.0 |
| 2015-08-24 | 11.0 | 9.1% | 10% | 0.0 |
| 2016-01-18 | 11.2 | 9.0% | 10% | 0.0 |
| 2018-05-28 | 17.4 | 5.7% | 10% | 0.0 |
| 2018-07-05 | 17.6 | 5.7% | 10% | 0.0 |
| 2020-02-03 | 14.4 | 7.0% | 10% | 0.0 |
| 2020-03-11 | 12.4 | 8.1% | 10% | 0.0 |
| 2020-07-27 | 12.7 | 7.9% | 10% | 0.0 |
| 2022-06-15 | 13.0 | 7.7% | 10% | 0.0 |
| 2023-10-30 | 12.6 | 7.9% | 10% | 0.0 |
| 2024-04-17 | 13.9 | 7.2% | 10% | 0.0 |
| 2024-08-05 | 12.9 | 7.8% | 10% | 0.0 |
| 2025-04-03 | 12.2 | 8.2% | 10% | 0.0 |
| 2025-10-20 | 14.9 | 6.7% | 10% | 0.0 |
| 2026-03-09 | 13.6 | 7.3% | 10% | 0.0 |

Max gross exposure any day: **1.000** (never above 1.0 = no margin ever used).

---

## Full-period (2014-01-02 → 2026-06-23, 12.47y)

| Metric | System | VNINDEX B&H |
|--------|--------|-------------|
| CAGR | **31.0%** | 11.1% |
| Sharpe (252) | **1.84** | 0.67 |
| Sortino (252) | **1.75** | 0.59 |
| MaxDD | **-31.5%** | -45.3% |
| Calmar | **0.99** | 0.24 |
| DD duration | 163 sessions | 882 sessions |
| Final NAV | 1,449.2B | — |
| Self-check err | **0 VND** (both books) | — |

---

## IS (2014–2019) vs OOS (2020–2026)

| | IS (2014-2019) | OOS (2020-2026) |
|--|--|--|
| CAGR | 26.0% | 35.6% |
| MaxDD | -12.8% | -31.5% |
| Calmar | 2.04 | 1.13 |

OOS > IS on CAGR (2021 bull + 2023 recovery), IS better Calmar (no COVID drawdown in IS).

---

## Annual returns

| Year | System | VNI B&H | Delta | Per-year MaxDD | Comment |
|------|--------|---------|-------|----------------|---------|
| 2014 | +38.7% | +8.2% | +30.6pp | -8.7% | IS |
| 2015 | +21.7% | +6.4% | +15.3pp | -9.8% | IS |
| 2016 | +14.5% | +15.8% | -1.2pp | -7.5% | IS; VNI catches up |
| 2017 | +40.1% | +46.5% | -6.3pp | -8.5% | IS; strong bull year |
| 2018 | +25.9% | -10.4% | +36.2pp | -12.8% | IS; defensive in bear |
| 2019 | +17.0% | +7.8% | +9.2pp | -5.3% | IS |
| 2020 | +30.1% | +14.2% | +15.9pp | -31.5% | OOS; COVID washout survived |
| 2021 | +125.6% | +33.7% | +91.9pp | -6.3% | OOS; post-crisis bull explosion |
| 2022 | -4.3% | -34.0% | +29.7pp | -17.1% | OOS; postbull guard size=0 on 2022-04-19 & 2022-09-28 |
| 2023 | +38.4% | +8.2% | +30.2pp | -14.6% | OOS; recovery |
| 2024 | +19.3% | +11.9% | +7.4pp | -8.7% | OOS |
| 2025 | +42.6% | +40.5% | +2.0pp | -14.1% | OOS; bull year; system lags slightly |
| 2026* | +1.3% | +4.5% | -3.3pp | -11.1% | OOS; partial (thru 2026-06-23) |

*2026 partial year through 2026-06-23.

**Worst year**: 2022 at -4.3% (VNI: -34.0%). Only losing year in 13 years.
**Best year**: 2021 at +125.6%.

---

## CAPIT leverage events
MGE=1.3 CAPIT_ONLY fedborrow: **0 leverage events fired**.
All 18 washout detections had fedborrow gate m=0 (eyield < 10% borrow rate).

CAPIT did deploy cash-based positions across 16 events (2 of 18 sized to 0 by postbull guard):

| Date | State | Size | Postbull note |
|------|-------|------|---------------|
| 2014-05-08 | CRISIS(1) | 1.00 | normal |
| 2015-05-18 | NEUTRAL(3) | 0.75 | normal |
| 2015-08-24 | NEUTRAL(3) | 0.375 | grind halved |
| 2016-01-18 | NEUTRAL(3) | 0.75 | normal |
| 2018-05-28 | CRISIS(1) | 1.00 | normal |
| 2018-07-05 | NEUTRAL(3) | 0.375 | grind halved |
| 2020-02-03 | NEUTRAL(3) | 0.75 | normal |
| 2020-03-11 | BEAR(2) | 0.25 | grind halved |
| 2020-07-27 | NEUTRAL(3) | 0.375 | grind halved |
| 2022-04-19 | CRISIS(1) | **0.00** | postbull: ret2y=+83%, dd1y=-8% → size zeroed |
| 2022-06-15 | BEAR(2) | 0.25 | grind halved |
| 2022-09-28 | BEAR(2) | **0.00** | postbull zeroed again |
| 2023-10-30 | CRISIS(1) | 1.00 | normal |
| 2024-04-17 | BULL(4) | 0.50 | mild washout |
| 2024-08-05 | CRISIS(1) | 0.50 | grind halved |
| 2025-04-03 | BULL(4) | 0.50 | mild washout |
| 2025-10-20 | NEUTRAL(3) | 0.75 | normal |
| 2026-03-09 | NEUTRAL(3) | 0.75 | normal |

---

## Implication for Spyros review

The `fedborrow` gate is a structural veto for the Vietnamese market:
- VN market PE has traded 10–17x across all washout windows → eyield 5.7–9.1%
- Borrow cost = 10% → carry spread always negative → gate never opens
- **MGE=1.3 fedborrow ≡ MGE=0 (unleveraged)** for all practical purposes

To actually deploy leverage via CAPIT in VN, either:
1. Use `MGE_GATE=deposit_eyield` (eyield vs deposit rate ~4-5% → spread positive → gate opens at most washouts)
2. Use `MGE_GATE=none` (no carry gate, leverage at conviction only)
3. Lower `BORROW_ANNUAL` to reflect real margin rates (VN margin rates ~9-14%, but 10% is conservative; the issue is PE-based eyield is structurally below 10%)
