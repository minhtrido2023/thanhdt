# disc_c4/c5 (LAG half-size in low DT5G) — re-run in BLENDED V2.4
Job Taylor_20260723_162813 · 2026-07-23 · Taylor (quant) · **R&D only, wires nothing.**

Follow-up to the LAG-only study (Taylor_20260723_131958, verify log verify_20260723_142043.log,
quant-skeptic CONFIRMED). That study found disc_c4/c5 improved the **isolated LAG sleeve**
(Sharpe 1.16→1.30, MaxDD −18.3→−15.1%, Calmar 0.88→1.05, DSR 0.999) but ran on a LAG-only NAV
path. This job re-runs it inside the **full production V2.4 system** (BAL + LAG + CAPIT +
custom30V parking + allocator), the way production actually operates.

## Mechanism (as wired for this test)
New env knob `LAG_DISC_STATE` in `pt_v23_audit_2014.py` (default OFF = byte-identical). Uses the
engine's existing `tier_weights_by_state` hook to **halve the LAG_* tier weights** (LAG_HI 0.10→
0.05, LAG_LO 0.08→0.04) on the LAG book's entry sizing when the DT5G state is low:
- **c4** = halve in states {1,2} = CRISIS + BEAR   (LAG-only winner)
- **c5** = halve in state {1} = CRISIS only
Applied to BOTH LAG passes (base + CAPIT-arm), so freed LAG cash is visible to the CAPIT arm
(which sizes on book free-cash) — the faithful full-system behaviour. §8-compliant: experiment
CSVs carry `_lagdisc{c4,c5}_exp_*` tags, canonical R3 CSV untouched.

## Runs (frozen cache `data/bq_cache` verified:true 14/14, threads=1, self-check 0 VND all 3)
Pin command + `EXP_TAG`, `AUDIT_END=2026-06-19`, `$DNA_PYEXE`. **Control reproduces the pinned R3
byte-for-byte: 27.16% / 1.81 / −18.1% / 1.50.**

## Q1 — does the effect survive, or dilute? → **SURVIVES DIRECTIONALLY, HEAVILY DILUTED**

| metric | LAG-only c4 Δ | **blended c4 Δ** | dilution |
|---|---|---|---|
| CAGR   | −0.17pp | **−0.18pp** | (neutral, unchanged) |
| Sharpe | **+0.14** | **+0.01** (raw +0.002) | ~93% — effectively gone |
| MaxDD  | **+3.2pp** better | **+0.9pp** better | ~72% |
| Calmar | **+0.17** | **+0.07** | ~59% |

**The compelling LAG-only case does NOT survive into the full system.** The Sharpe win vanishes
(1.815→1.817 annualized = noise); only a marginal DD-shave and Calmar bump remain, and even those
are within R3 bootstrap DD noise (5th-pct ~−30%). **Not counterproductive** (it never hurts
risk-adjusted metrics) — just largely **redundant**.

Why (exactly the pre-registered dilution hypothesis, confirmed):
1. **The allocator already sets `w_LAG = 0` in BEAR(2)** (`STATE_LAG_WEIGHT={1:.50,2:0,3/4/5:.65}`).
   So disc_c4's entire BEAR half-sizing — ~half the LAG-only benefit — is **already done at book
   level**. disc_c4 and disc_c5 differ only through the CAPIT-cash + LAG-book-path second-order
   effects (c4≠c5 in 2015/2020/2022), not through book weight.
2. **LAG is only ~half the total book** (BAL is the other half + CAPIT + parking). Halving LAG risk
   in CRISIS moves only ~¼ of the portfolio.
3. **custom30V parking + CAPIT already de-risk in risk-off** independently.
4. The live bite window is tiny: state≤2 = 24.4% of days but BEAR(2, 7.8%) is moot → **effective
   bite ≈ CRISIS(1) = 16.6% of days, and only on the LAG half.**

## Q2 — full comparison (engine metrics, 252-Sharpe; = pin convention)

| variant | CAGR | Sharpe | MaxDD | Calmar | | IS CAGR/Shrp | OOS CAGR/Shrp/DD/Calm |
|---|---|---|---|---|---|---|---|
| **control (=pin R3)** | 27.16% | 1.81 | −18.1% | 1.50 | | 23.17 / 1.59 | 30.91 / 1.99 / −18.1 / 1.71 |
| **c4** | 26.98% | 1.82 | −17.2% | 1.57 | | 23.79 / 1.64 | 29.96 / 1.95 / −16.7 / 1.79 |
| c5 | 26.84% | 1.81 | −17.2% | 1.56 | | 23.64 / 1.63 | 29.82 / 1.95 / −16.9 / 1.76 |

- **Walk-forward asymmetric**: c4 *improves* IS CAGR (+0.62pp) & Sharpe (+0.05) but *costs* OOS CAGR
  (−0.95pp); DD/Calmar improve in BOTH windows. So the only sign-consistent benefit is DD/Calmar,
  never CAGR (CAGR is a wash IS-plus / OOS-minus).
- **LOO-by-year (NAV-level, drop each year's daily returns)**: c4 full-period CAGR edge −0.18pp,
  stays small-negative in 12/13 drops (positive only when 2024 is removed → 2024 is where c4 hurts
  CAGR most). **Not carried by any single year** — it is a flat, tiny, slightly-negative CAGR
  trade for a small DD reduction, every year.
- Per-year c4−control swings are larger than the net (+4.5pp in 2014, **−5.7pp in 2024**) but
  net to ≈0 — no year makes it a win.

## Q3 — DSR / statistical significance → **NOT SIGNIFICANT at blended level**
All three configs DSR=1.0000 (they are all strong strategies — DSR of the *level*, not the diff).
The relevant test is the **c4−control difference**: annualized Sharpe +0.002, MaxDD +0.9pp on an
18% base — **statistically indistinguishable from zero**, inside the R3 bootstrap DD band. There is
no multiple-testing case to make because there is no significant edge to deflate. **Precondition
for reporting a meaningful DSR-on-the-improvement is NOT met.**

## Verdict → **NO-GO for wiring as a Sharpe/return improver; marginal DD-insurance at best**
The premise of the candidate — "half-size LAG in fear buys a real risk-adjusted improvement" — is
**true on the isolated sleeve but fails at the portfolio level**, because production's allocator
(w_LAG=0 in BEAR) already captures most of the intended protection. What remains in blended V2.4 is
a CAGR-neutral (−0.18pp), Sharpe-flat, ~+0.9pp DD / +0.07 Calmar shave that is within noise.

- **Do NOT propose wiring as a return/Sharpe win** (it isn't one) → therefore **no second
  quant-skeptic pass is triggered** (that gate was conditional on a wire-worthy result).
- If the user specifically wants *pure CRISIS-LAG de-risking insurance*, c4 is a mild, near-free
  option (−0.18pp CAGR for −0.9pp DD) — but honestly frame it as marginal and largely redundant
  with the existing allocator, not as the LAG-only headline.
- c4 ≥ c5 (higher CAGR, same DD) if either is ever chosen.
- Reconciles the two studies cleanly: the LAG-only result was real **for the sleeve**; the
  portfolio just already does most of it. Consistent with the standing house view that DT5G-style
  regime gates are **insurance, not return-enhancers** — and here the insurance is already priced
  into the allocator.

Artifacts: `pt_v23_audit_2014.py` (knob `LAG_DISC_STATE`, OFF-default), run logs + CSVs +
`analyze.py` + `analysis_output.txt` in this dir.
