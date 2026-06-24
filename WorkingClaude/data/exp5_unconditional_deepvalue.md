# Exp-5: Unconditional lever + deep-value postbull override

**Run date**: 2026-06-24  
**Base config**: RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_DEP_FLOOR=0.075 MGE=1.3 MGE_CAPIT_ONLY=1 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7  
**Maturity mode**: postbull (argv[3]=postbull, argv[4]=0 → EW2D_SHRINK=0.0 = hard-block postbull events)  
**Reference (V2.4-LF no leverage)**: CAGR ~30.99% (Tier-1 baseline)

---

## Exp-5a: MGE_GATE=none (unconditional lever at all CAPIT events with size > 0)

**Command**: `MGE_GATE=none` (default, already the baseline for the MGE=1.3 config)

| Metric | Value |
|--------|-------|
| CAGR | 29.73% |
| Sharpe | 1.77 |
| MaxDD | -31.4% |
| Calmar | 0.95 |
| Self-check | 0 VND |
| Final NAV | 1,284.41B |

**Events levered** (size > 0, unconditional MGE_GATE=none → head = size × 0.3 added):
- 2014-05-08: size=1.00
- 2015-05-18: size=0.75
- 2015-08-24: size=0.38
- 2016-01-18: size=0.75
- 2018-05-28: size=1.00
- 2018-07-05: size=0.38
- 2020-02-03: size=0.75
- 2020-03-11: size=0.25
- 2020-07-27: size=0.38
- 2022-06-15: size=0.25
- 2023-10-30: size=1.00
- 2024-04-17: size=0.50
- 2024-08-05: size=0.50
- 2025-04-03: size=0.50
- 2025-10-20: size=0.75
- 2026-03-09: size=0.75

**Events still zero (postbull/base zeroed → lever=0)**:
- 2022-04-19: state=1 (CRISIS), **postbull guard zeroed** (ret2y=+83% > 60%, dd1y=-8% > -15%) → size=0.00, head=0.00
- 2022-09-28: state=2 (BEAR), **base=0** (capit_base: dd52=-25.2% ≤ -25 AND cool=False → returns 0.0 for BEAR state) → size=0.00, head=0.00

**Diagnosis**: MGE_GATE=none has no effect on zero-size events. Lever headroom = `size × (MGE-1)`, so when size=0 the borrow is also 0. The unconditional gate does not help recover 2022.

---

## Exp-5b: Deep-value postbull override

**Implementation**: Post-pass after RECOVERY_PARK block loads `_pbz_asof()`. For any capit event zeroed by postbull guard (mat < 1.0, size_premat > 0, final size ≈ 0), if universe median pb_z (prior completed month, causal) < DEEP_VALUE_PBZ threshold → restore size to pre-maturity value.

**Key finding — 2022 universe pb_z by month** (prior-month causal, from BQ):
| Month | Median pb_z (prior of event) |
|-------|------------------------------|
| 2022-03 (prior for Apr event) | **+1.72** |
| 2022-04 | +1.25 |
| 2022-05 | +0.45 |
| 2022-06 | +0.22 |
| 2022-07 | +0.09 |
| 2022-08 (prior for Sep event) | **+0.27** |
| 2022-09 | +0.16 |
| 2022-10 | -0.45 |
| 2022-11 | -0.88 |

### pb_z threshold -1.0

| Metric | Value |
|--------|-------|
| CAGR | 29.73% |
| Sharpe | 1.77 |
| MaxDD | -31.4% |
| Calmar | 0.95 |
| Self-check | 0 VND |

**Events override fired**: **NONE** (0 events restored)
- 2022-04-19: pb_z = **+1.72** (prior month = Mar 2022) — not below -1.0 → still blocked
- 2022-09-28: not examined (zeroed by base=0 for BEAR state, not by postbull mat; _size_premat=0)

### pb_z threshold -0.8

| Metric | Value |
|--------|-------|
| CAGR | 29.73% |
| Sharpe | 1.77 |
| MaxDD | -31.4% |
| Calmar | 0.95 |
| Self-check | 0 VND |

**Events override fired**: **NONE** (0 events restored)
- 2022-04-19: pb_z = **+1.72** — not below -0.8 → still blocked

---

## Verdict

### 2022 NOT captured by either mechanism

The core hypothesis — "postbull guard blocked 2022 when market was cheap (pb_z sâu)" — is **factually incorrect**.

- **2022-04-19 (CRISIS, postbull-zeroed)**: Universe median pb_z = **+1.72** (prior month March). The market was EXPENSIVE vs 5Y history, not cheap. Postbull guard fired CORRECTLY.
- **2022-09-28 (BEAR, zeroed)**: NOT zeroed by postbull — zeroed by capit_base returning 0 for BEAR state when dd52=-25.2% ≤ -25% and cooling=False. A separate mechanism.

The market didn't get genuinely cheap (pb_z < -0.8 or -1.0) until late 2022 (Oct-Dec), by which time there were no new washout events to trigger CAPIT entries.

### Why Exp-5a is identical to baseline

MGE_GATE=none was already the default setting. Lever headroom = `size × (MGE-1)` → zero when size=0. No unconditional gate can add leverage on top of a zeroed position. The 2022 miss is structural: the market wasn't ripe (cheap enough + mature enough decline) for the CAPIT system at the April event.

### Recommendation

Do NOT implement the deep-value postbull override as a production change — it solves a non-existent problem for 2022. The postbull guard performed correctly by blocking an expensive post-bull washout that subsequently fell further (-16% to -39%). The 2022 loss (-3.88% sys) stems from the June washout (size=0.25, short hold into continued decline) and portfolio holdings, not from the April miss.

If addressing 2022 is a priority, the angle to examine is the BEAR state capit_base logic (state=2, dd52 exactly at the -25% boundary) — but this is a data-driven edge case, not a pb_z story.
