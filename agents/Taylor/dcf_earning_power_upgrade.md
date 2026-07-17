# DCF upgrade study — earning-power basis · GDP terminal growth · conditional refresh gate

> Author: Taylor (quant). Job `Taylor_20260717_063638` (user-approved direction, via Mike).
> Status: **RESEARCH — nothing wired to production.** Canonical `dcf_valuation.py` UNTOUCHED.
> quant-skeptic: **CONFIRMED (high confidence)**, independent recompute matched all figures
> (`mike/logs/verify_20260717_070358.log`).
> Code: `dcf_earning_power.py` (variant valuation), `dcf_earning_power_test.py` (Study B IC +
> orthogonality harness), `gdp_growth_vn.py` + `refresh_gdp_growth_vn.py` (new GDP data source),
> `dcf_refresh_gate.py` + `dcf_refresh_gate_selfcheck.py` (Việc 2).

Reuses the existing DCF test methodology verbatim (Study B walk-forward IC of margin-of-safety vs
forward return + orthogonality vs 1/PE — see `dcf_valuation_framework.md` §7). Same panel
construction: non-financial rating≤3 universe, FV once per financial release (point-in-time,
`fin.time ≤ asof`), as-of merged (`merge_asof` backward) to a monthly price panel, 15-month FV
freshness, cross-sectional Spearman IC per month averaged, **t on the MONTHLY IC series (n≈144)**,
walk-forward IS(2014-19)/OOS(2020-26). Panel here: 1006 tickers · 58,354 rows · 144 months.

---

## Việc 1 — Earning-power DCF vs FCFE  →  **NO-GO (as a replacement)**

**Direction chosen: option (b)** — keep the 2-stage framework, change ONLY the base input. Rejected
option (a) pure Greenwald EPV on a decisive theoretical ground: no-growth EPV on *trailing* earnings
collapses to `MoS = 1 − r·PE`, which cross-sectionally is **rank-identical to 1/PE** (r is date-only)
— it would fail orthogonality by construction. Option (b) (normalized earning-power base, keep the
growth/terminal machinery) is the only variant that could plausibly be a *distinct* axis, so it is
the honest test of the user's hypothesis.

**Earning-power base** = normalized 3Y-avg TTM **net income to equity** (cycle-smoothed; capex NOT
deducted → EPV/Greenwald steady-state assumption maintenance-capex ≈ D&A). Net income (not
NOPAT/EBIT) is correct because the DCF discounts at **cost of equity** — NOPAT is unlevered and would
need WACC. Same golden-floor cash gate kept (`CF_OA_3Y > 0`): positive earnings + negative operating
cash is an accrual red flag we still exclude.

**Result — the user's intuition is *partly* right but the gain is redundant:**

| variant | 3M IC ALL | 3M IC OOS | coverage rows | rank-corr(MoS, 1/PE) |
|---|---|---|---|---|
| **FCFE + CPI (canonical V0)** | +0.0754 | +0.0747 | 48,296 | **+0.29** |
| **earning-power + CPI (V1)** | **+0.0976** | **+0.1188** | 57,134 (+9k) | **+0.756** |

Earning-power raises raw IC substantially (OOS 3M 0.073 → 0.119) **and** expands coverage — it values
the FCFE-negative build-outs (MSH/PVT/HAH) the canonical DCF correctly abstains on, and those reads
(CHEAP +58%/+50%/+38% as-of 2026-06) agree with the sector_lens BUY/ACCUM calls. **But** the
orthogonality test (the gate every 8L lens must pass) exposes the catch:

| residual after ⟂ 1/PE (COMMON subset) | IS 2M | IS 3M | OOS 2M | OOS 3M |
|---|---|---|---|---|
| **FCFE (V0)** | +0.0306 (t+3.2) | +0.0445 (t+4.3) | +0.0401 (t+4.9) | +0.0413 (t+5.3) |
| **earning-power (V1)** | **−0.0061 (t−0.7)** | **−0.0058 (t−0.7)** | +0.0398 (t+4.4) | +0.0530 (t+6.2) |

Earning-power MoS is **highly collinear with 1/PE (0.756)** and after neutralizing 1/PE its **in-sample
residual collapses to ~0 (t=−0.7)** — in-sample it adds *nothing* beyond the 1/PE factor already
deployed. The canonical FCFE model, despite lower raw IC and reading "too RICH", keeps a **significant
residual in BOTH windows** (the whole point of an *absolute* lens orthogonal to the relative ones).

This is exactly the **KNOWLEDGE.md composite-as-selector trap** (1/PE dominant factor absorbs
everything) reappearing. The higher raw IC is 1/PE relabeled with more steps.

**Nuance (quant-skeptic):** earning-power's residual *survives OOS* (+0.053, t+6.2) while collapsing
IS — a **window-inconsistent** signal. A bull could call this genuine deployment-era orthogonal alpha;
but window-inconsistency is precisely what argues for the **window-consistent FCFE** choice. So the
nuance strengthens, not weakens, the NO-GO. "Largely redundant," not "fully redundant."

**Verdict:** **NO-GO to replace FCFE with earning-power as the primary DCF.** Keep earning-power ONLY
as an optional, clearly-labelled **coverage extension for FCFE-negative names** (a normalized
earnings-yield proxy, NOT an independent DCF axis) — never sold as new alpha.

---

## Việc 3 — GDP terminal growth vs CPI-only  →  **LEVEL/display fix, NOT alpha**

Current terminal g = 5Y-avg CPI (≈3.4%) ⇒ implicit **real growth = 0 forever** (very conservative).
New GDP data source `gdp_growth_vn.py` (World Bank `NY.GDP.MKTP.KD.ZG`, real GDP growth, 26y 2000-2025,
`lastupdated` 2026-07-13): **long-run 15y avg real GDP = 6.22%**. Four terminal-g modes tested:

| mode | terminal g @2026-06 | Gordon-clamp (r≤g_term) | 3M IC ALL | %cheap |
|---|---|---|---|---|
| `cpi` (baseline) | 3.38% | 0.0% | +0.0754 | 57% |
| `cpi_gdp_full` (naive) | **9.60%** | **23.0%** ⚠ | +0.0740 (marginally worse) | 85% (overcooked) |
| `cpi_gdp_half` (faded ×0.5) | 6.49% | 15.4% | +0.0751 | 71% |
| `cap_rf` (Damodaran, min(full, r_f)) | 6.80% | **0.0%** | +0.0760 | 66% |

**Two findings:**
1. **Terminal g does NOT change the cross-sectional edge.** All modes' IC are within ~0.002 of
   baseline at every horizon/window (the fragile full-GDP reaches −0.0027 at IS-3M). This is the
   **date-only argument (framework §7.1)**: terminal g is identical across all tickers on a date, so it
   shifts every name's FV level by ~the same factor, and the within-month rank IC differences it out.
   Confirmed numerically.
2. **The naive full-GDP proposal is numerically fragile** — 23% of releases hit the Gordon guard
   (`r ≤ g_term` → terminal value explosive-clamped) — the exact **convergence caveat** Mike flagged,
   empirically demonstrated. Using current ~7-8% real growth forever is untenable at VN discount rates.

**Verdict:** GDP terminal g is a **LEVEL/display improvement, not an edge improvement.** It DOES address
the user's real complaint (FCFE DCF "reads everything RICH": %cheap 57%). If a more usable absolute line
is wanted, adopt **`cap_rf` (Damodaran risk-free cap)**: cleanest theory (g_term ≤ nominal risk-free),
**0% Gordon-clamp**, IC unchanged (marginally best at 3M-IS 0.0776), %cheap a sensible 66% — reject the
naive full-GDP (fragile + marginally worse IC). **Must be sold as display realism, never as alpha.**
Consistent with framework §6.3 "use ranks, not the line."

---

## Việc 2 — Conditional refresh gate (deposit-rate 1pp band)  →  **DONE, selfcheck 24/24 PASS**

`dcf_refresh_gate.py`: recompute DCF only when the Big-4 12M deposit rate has moved **≥ 1.0pp** from the
rate last used; else keep existing numbers. State `data/dcf_refresh_state.json` (atomic write:
`last_used_rate`, `last_used_date`, `last_check_date`); append-only audit `data/dcf_refresh_gate.log`.
Pure `decide()` separated from I/O `run_gate()`. **Fail-safe:** any error → `refresh=True` (recompute
rather than serve stale on a broken gate).

**Boundary =exactly 1.0pp → INCLUSIVE (refresh).** User said ">1pp"; chose inclusive deliberately —
(a) DCF recompute is cheap, staleness is the real risk; (b) float equality (6.8−5.8) is fragile under
strict `>`. One-flag switch `THRESHOLD_INCLUSIVE=False` restores strict `>`. **This is the single
judgment call — flag for user.** `dcf_refresh_gate_selfcheck.py`: 24/24 PASS (band, boundary both
modes, first-run init, persistence, idempotency, downward move, fail-safe, dry-run isolation).

**Proposed cron cadence (PROPOSAL ONLY — not installed; read `cron_registry.md` §11 first):**
monthly, **day 11, 08:10 ICT** — after the WB commodity 2nd-attempt (day 10) and, critically, **after
`deposit_rate_vn.py` reflects any new rate**. **Hard dependency:** the gate only sees rate changes
*already entered into* `deposit_rate_vn.py`, which is still **manual** (the Winston monthly
deposit-refresh routine `proposal_deposit_rate_monthly_refresh_20260713.md` is proposed, not
installed). So this gate should be sequenced *after* that routine when adopted — installing it before
the deposit series auto-updates gains little. Registry answers (§11 4 questions): reads
`deposit_rate_vn.current_deposit_rate()` (as-of, T-anchor step series) + prior JSON state; writes the
state JSON + log; consumer = whoever regenerates DCF numbers for a report/dashboard (calls `run_gate()`,
recomputes only if `refresh=True`); no downstream deadline (reference tool, not a daily pipeline).

---

## GO/NO-GO summary + what's owed

| Việc | Verdict | Wire? |
|---|---|---|
| 1 earning-power basis | **NO-GO** as replacement (redundant w/ 1/PE, IS residual ~0) | keep FCFE canonical; earning-power = optional labelled coverage-extension only |
| 3 GDP terminal g | **level/display fix, NOT alpha** (IC flat; full-GDP fragile) | `cap_rf` optional display-realism; propose to user, NOT auto-default |
| 2 refresh gate | **DONE** (24/24 selfcheck) | operational; propose monthly cron, gated behind deposit-refresh routine |

- Nothing auto-defaulted. Both Việc 1 (NO-GO) and Việc 3 (display-only) conclusions **quant-skeptic
  CONFIRMED high-confidence**; a Việc-3 `cap_rf` *display* default (if user wants it) is a UI change on
  the canonical `dcf_valuation.py` that would still route through user sign-off before wiring.
- `gdp_growth_vn.py` added to `mike/kb/data_registry.md` (CANONICAL-single-tier, WB API, annual refresh).
- Caches in experiment namespace `dcf_exp/fv_releases_epvariants.parquet` (§8 — never the pinned cache).
- Reproduce: `DCF_REFRESH=1 $DNA_PYEXE dcf_earning_power_test.py`.
