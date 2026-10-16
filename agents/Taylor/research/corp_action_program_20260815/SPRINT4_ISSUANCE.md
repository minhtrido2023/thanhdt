# Sprint 4 — rights, ESOP and private placement

## Executive verdict

**DESCRIPTIVE ONLY across all three subtypes. No alpha candidate and no supply-arrival risk gate.**

Rights show a short T+5 positive association, but the preregistered T+20 primary is null, the
matched-control estimate is null and the result disappears in the wider population. Pooled
ESOP/private-placement returns around additional listing are null at every horizon. Dilution and
issue discount have no significant dose-response.

## Samples and data gates

- Rights: 548 events with an exact ex-date price session; 201 events / 152 tickers pass valid
  terms, universe, trading and contamination gates. This is only one event above the locked
  minimum N=200.
- AIS: 2,044 Tier-A price anchors before gates; 596 have AIS cross-source conflicts.
- Pooled AIS confirmatory sample: 363 ESOP/private-placement events / 202 tickers.
- Separate ESOP N=199 and private placement N=164 are below the subgroup floor. Rights AIS N=106
  is also below it.
- Valid AIS dilution is available for 310 pooled events; the full term/dose regression retains
  270 events after price validation.

## Rights ex-date and TERP

`issue_price = total_value / issue_volumn`; `TERP=(P_cum + q*issue_price)/(1+q)`. No ex-date raw
`Price` field is read.

| horizon | N | mean BHAR | 95% month-block CI | Holm p |
|---:|---:|---:|---:|---:|
| 5 | 201 | +2.324% | [+0.995%, +3.785%] | .0012 |
| **20 primary** | **201** | **+1.647%** | **[-0.151%, +3.734%]** | **.1588** |
| 60 | 200 | -1.123% | [-4.272%, +2.384%] | .5030 |

The primary distribution is skewed: median T+20 is **-1.605%** and only 47.3% are positive even
though the mean is +1.647%. IS and OOS confidence intervals both contain zero. R-WIDE T+20 is
+0.475%, CI [-1.299%, +2.427%]. The matched-control estimate on 132 events is +0.363%, CI
[-1.840%, +2.695%], also null and below the N floor.

The TERP validation itself passes: 89.1% of 183 stable-ratio events match the theoretical factor
within ±1%. Reconstructed ex prices close **4.083% above TERP** on average, CI
[+3.251%, +4.954%]. This is microstructure around an exchange-set reference, not proof of a
tradable edge; T+20 and control-based results do not sustain it.

Rights placebo, pretrend and one-year far baseline all contain zero. That removes one obvious
selection objection but does not repair the small sample or null primary.

## ESOP and private-placement supply arrival

| horizon | N | pooled mean BHAR | 95% month-block CI | Holm p |
|---:|---:|---:|---:|---:|
| 5 | 363 | -0.321% | [-1.152%, +0.502%] | 1.000 |
| **20 primary** | **363** | **-0.584%** | **[-2.061%, +1.089%]** | **1.000** |
| 60 | 360 | -0.415% | [-2.479%, +1.866%] | 1.000 |

- ESOP T+20: +0.216%, CI [-1.264%, +1.816%], N=199.
- Private placement T+20: -1.554%, CI [-3.876%, +1.056%], N=164.
- Rights AIS T+20: +0.133%, CI [-2.978%, +3.286%], N=106.
- AIS matched-control T+20: -1.490%, CI [-3.571%, +0.487%], N=234.
- Both AIS placebo and pretrend are null. Leave-one-year-out flips sign because 2022/2020 carry
  large opposing contributions; the pooled mean is not temporally stable.

There is no evidence here that the arrival of ESOP/private-placement shares creates a systematic
post-listing loss or gain.

## Dilution and discount

The two-way clustered regression on 270 valid observations is null:

- Dilution coefficient t=0.96.
- Issue discount coefficient t=-0.42.
- Private-placement indicator t=-1.35.

These data do not support a monotonic claim that larger dilution or deeper discount predicts
worse T+20 performance. PIT market cap is unavailable and was not proxied; see deviations.

## Limits and permitted use

- Announcement studies remain forbidden because `public_date` is not proven PIT.
- AIS uses Tier-A listing dates only; 596 cross-source conflicts are excluded.
- ESOP, private placement and rights-AIS subgroup samples do not clear N=200.
- AIS dates are not assumed known early enough for a feasible trade.
- No cost screen, strategy, production gate or wiring is justified.

## Reproducibility

Run `sprint4_build.py`, `sprint4_analyze.py`, `sprint4_plots.py`, then
`selfcheck_sprint4.py`. Machine-readable panels/results are in `out4/`. The design was committed
before outcomes at `03962aaf`.
