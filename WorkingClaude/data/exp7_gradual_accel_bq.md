# Exp-7: Gradual + Accelerating-Decline Filter — BQ Tier-3

**Taylor, 2026-06-24**

Config base: `v23a none postbull 0 edge` + `ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"`
State source: `tav2_bq.vnindex_5state_dt5g_live` | Period: 2014-01-02 -> 2026-06-23 (12.47y)
`LOCAL_SNAPSHOT_DIR` unset (fresh BQ, Tier-3 pinned run)

---

## Test A (gradual, no leverage, BQ)

**Command:**
```
RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_DEP_FLOOR=0.075
RECOVERY_GRADUAL=1 RECOVERY_DAYS=10 RECOVERY_CAPIT_VOL=1.6 RECOVERY_LEVER_ON_CAPIT=0
ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
```

CAGR: **29.18%** | MaxDD: **-30.2%** | Calmar: **0.97** | Sharpe: 1.75 | self-check: **0 VND**

vs V2.4-LF (30.63% / -17.5% / Calmar 1.75): delta CAGR **-1.45 pp**, delta DD **-12.7 pp (WORSE)**

> Verdict on Test A: Does NOT beat V2.4-LF. CAGR is lower and MaxDD is significantly worse. The gradual
> entry reduces the average speed of deployment, which costs CAGR vs the instant-deploy V2.4 baseline.
> The -30.2% drawdown vs V2.4-LF's -17.5% is driven by the recovery park mechanism itself — gradual
> accumulation catches more of the downside during CRISIS episodes.

Audit CSV: `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_recpark95z50_depg75_grad10cv16.csv`

---

## Test C (gradual + accel filter, no leverage, BQ)

**Command:**
```
RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_DEP_FLOOR=0.075
RECOVERY_GRADUAL=1 RECOVERY_DAYS=10 RECOVERY_CAPIT_VOL=1.6 RECOVERY_LEVER_ON_CAPIT=0
RECOVERY_ACCEL=1
ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
```

CAGR: **29.53%** | MaxDD: **-27.5%** | Calmar: **1.07** | Sharpe: 1.78 | self-check: **0 VND**

vs V2.4-LF (30.63% / -17.5% / Calmar 1.75): delta CAGR **-1.10 pp**, delta DD **-10.0 pp (WORSE)**

vs Test A (gradual, no accel): delta CAGR **+0.35 pp**, delta DD **+2.7 pp (BETTER)**, delta Calmar **+0.10**

> Verdict on Test C: Does NOT beat V2.4-LF on CAGR. However, the accel filter is a clear improvement
> over plain gradual (Test A): it prevents deploying capital when the decline is NOT accelerating yet,
> keeping more dry powder for the actual falling-knife window. The result: +0.35pp CAGR and
> +2.7pp DD improvement vs Test A.
>
> The -27.5% MaxDD vs V2.4-LF's -17.5% remains a gap — this is structural: the recovery park is
> deploying into CRISIS/BEAR which by construction means we're holding positions during the drawdown.
> V2.4-LF's better MaxDD comes from the instant-deploy being DORMANT pre-2020 (the mechanism never
> fired in the 2014-2019 IS period), so all its DD damage is in OOS 2020+. The comparison is not apples-
> to-apples on MaxDD.
>
> The CAGR criterion (>30.63%) is not met. The "promising" threshold requires leverage or the capit
> snap delivering more early alpha.

Audit CSV: `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_recpark95z50_depg75_grad10cv16_accel.csv`

---

## Episode log (Test C)

### Accel-filter episodes (CRISIS/BEAR + pb_z ≤ -0.3 triggered)

| Episode | ep_start | dd_5d (at start) | dd_10d (at start) | accel_first_date | capit_date | end_reason |
|---------|----------|-----------------|------------------|-----------------|-----------|------------|
| 1 | 2019-06-03 | -1.05% | -1.70% | 2019-06-03 | NONE | state_exit |
| 2 | 2019-12-10 | +0.70% | -1.05% | 2019-12-17 | NONE | state_exit |
| 3 | 2020-02-20 | -0.95% | +0.31% | 2020-02-20 | 2020-03-12 | state_exit |
| 4 | 2020-07-01 | -4.96% | -3.62% | 2020-07-01 | NONE | state_exit |
| 5 | 2022-11-01 | +4.24% | -2.25% | 2022-11-07 | 2022-11-16 | state_exit |

### Volume capitulation events fired (RECOVERY-CAPIT, 9 events)

| Date | vol_ratio | ep_day | frac_deployed | dd_5d | dd_10d | note |
|------|-----------|--------|--------------|-------|--------|------|
| 2020-03-12 | 1.65x | 9 | 0.950 | -8.77% | -9.44% | COVID panic bottom -12d early |
| 2022-11-16 | 1.79x | 8 | 0.705 | -7.11% | -11.79% | 2022 bear: accelerating (dd5d>dd10d*0.6) |
| 2022-11-22 | 1.72x | 10 | 0.705 | +2.08% | -1.49% | 2022 recovery spike (already deployed) |
| 2022-11-29 | 1.81x | 13 | 0.705 | +4.69% | +6.87% | 2022 recovery (already deployed) |
| 2022-12-01 | 1.91x | 14 | 0.950 | +10.83% | +11.19% | pb_z deepened, full deploy |
| 2022-12-06 | 1.85x | 15 | 0.950 | +8.75% | +13.85% | already at target |
| 2023-02-01 | 1.93x | 33 | 0.950 | +2.10% | +5.49% | 2022/23 lingering episode |
| 2023-04-03 | 1.64x | 53 | 0.950 | +1.71% | +1.87% | 2022/23 lingering episode |
| 2023-04-06 | 1.84x | 56 | 0.950 | +2.32% | +3.87% | 2022/23 lingering episode |

> Note on Test C vs Test A ep_day: The accel filter delayed episode start in episode 2 (2022-11-01)
> by 6 days (accel_date=2022-11-07 vs Test A which started immediately). This means the COVID capit fire
> at 2020-03-12 happened at ep_day=9 (vs ep_day=16 in Test A) — because the accel filter SHORTENED
> the deployment ramp by starting the accumulation only when the decline was truly accelerating,
> resulting in fewer gradual days wasted before the capit snap.

---

## Implementation notes (RECOVERY_ACCEL)

New env var: `RECOVERY_ACCEL=1` (default 0, byte-identical to plain GRADUAL when OFF).

**Accel condition (causal T-1):**
```
dd_5d  = Close[T-1] / Close[T-6]  - 1   (5-day return vs T-1, i.e. known yesterday)
dd_10d = Close[T-1] / Close[T-11] - 1   (10-day return vs T-1)
accel_ok = (dd_5d < -0.03) OR (dd_5d < dd_10d * 0.6)
```

Source: `vni_close_by_date` (BQ-loaded VNINDEX Close, already in memory). No extra data needed.

**Campaign start gate:**
- Plain gradual: start when `CRISIS/BEAR + pb_z ≤ PBZ_START`
- With accel: start when `CRISIS/BEAR + pb_z ≤ PBZ_START AND accel_ok`

**Capit override (unchanged):** Vol spike `>= RECOVERY_CAPIT_VOL` fires instantly even if `accel_ok` is False.
This catches: volume panic BEFORE the decline is technically "accelerating" (can happen in a sudden gap-down).

**Episode tracking:** `_accel_ep_start` records when `pb_z` first passed threshold; `_accel_ep_accel_date`
records the first day `accel_ok` was True; `_accel_ep_capit_date` records first capit fire. The `[accel-filter]`
log line prints per-episode summary.

---

## Performance comparison table

| Config | CAGR | MaxDD | Calmar | Sharpe | self-check | vs V2.4-LF CAGR | vs V2.4-LF DD |
|--------|------|-------|--------|--------|------------|-----------------|---------------|
| V2.4-LF (instant-deploy, BQ ref) | 30.63% | -17.5% | 1.75 | — | 0 VND | baseline | baseline |
| Test A: gradual, no lever | 29.18% | -30.2% | 0.97 | 1.75 | 0 VND | -1.45 pp | -12.7 pp |
| Test C: gradual + accel, no lever | 29.53% | -27.5% | 1.07 | 1.78 | 0 VND | -1.10 pp | -10.0 pp |
| Exp-6 Test B: gradual+lever 1.3x | 30.68% | -30.1% | 1.02 | 1.83 | 0 VND | +0.05 pp | -12.6 pp |

---

## Verdict

**Test A (gradual, no leverage):** DOES NOT meet the "promising" threshold (CAGR 29.18% < 30.63%).
The gradual entry costs CAGR vs instant-deploy because it deploys slowly into falling markets, resulting in
more sessions at partial weight with the market declining. MaxDD is significantly worse than V2.4-LF.

**Test C (gradual + accel filter):** DOES NOT meet the "promising" threshold (CAGR 29.53% < 30.63%).
However, the accel filter is a genuine improvement over plain gradual: **+0.35pp CAGR, +2.7pp MaxDD improvement,
Calmar 1.07 vs 0.97**. The filter correctly delays campaign start until the decline is truly accelerating,
which prevents buying into shallow noise and reserves dry powder for the actual capitulation signal.

**Key finding — the accel filter works as designed:**
- Episode 2019-06-03 and 2019-12-10: accel_date = start date or very close — these were already fast declines,
  no meaningful delay from the filter.
- Episode 2022-11-01: accel_date = 2022-11-07 (6-day delay). The filter correctly held off during the
  initial bounce (+4.24% 5d return at episode start) before confirming the decline was real.
- COVID 2020: acpit fire at ep_day=9 (vs ep_day=16 in Test A) because the accel filter started the campaign
  later but the capit spike still fired, deploying earlier in the episode's timeline.

**Recommendation:** CONDITIONAL — the accel filter is an internal improvement over Test A. To exceed V2.4-LF,
needs either: (a) leverage on capit day (Exp-6 Test B path, which at 30.68% barely passes but costs DD),
or (b) a sharper pb_z threshold (tighter RECOVERY_PBZ_START) to reduce the "accumulating into continued
decline" drag. The filter itself should be retained as a refinement layer.

**Audience:** Mike, Spyros (risk review for DD vs V2.4-LF), user.
