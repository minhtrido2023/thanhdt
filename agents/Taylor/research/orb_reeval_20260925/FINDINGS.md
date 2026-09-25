# ORB intraday VN30F paper-trial re-eval — 2026-09-25 (job Taylor_20260925_052050)

## 1. Independent session count (data/orb_pt_log.csv)
- 74 rows, 74 unique dates, 0 dupes, 0 NaN, 0 sig==0. Window 2026-06-09 -> 2026-09-24.
- Report 09-24 said "73 phien" = it counted through 09-23. Recomputed: NAV +6.59% (not +6.18%),
  WR 55.4% (not 54.8%), Sharpe_ann 1.536 (not 1.46). Deltas are just the extra 09-24 session.
- >=60 sessions: MET (74).

## 2. Regime condition — NOT MET
tav2_bq.vnindex_5state_dt5g_live, 2026-06-09..2026-09-24: state=3 (NEUTRAL) for ALL 75 rows.
state_raw also 3 (no macro cap ever engaged). ZERO transitions. No BEAR(2), no CRISIS(1).
Encoding confirmed macro_state_live.py:42 -> NEUTRAL,CRISIS,BEAR = 3,1,2.

Underlying tape WAS choppy: VN30F 14:30 proxy start 1950.1 -> end 1936.8 (-0.68%),
range 11.1%, efficiency ratio 0.011 (0=chop). Aug 2026 was a losing month (-2.94%).
So "chop" is arguably present at the tape level, but "bear" is absent at the regime level.

## 3. WHY the regime gap is fatal, not bureaucratic — ORB edge is regime-CONDITIONAL
Deployed config (exit 14:30, no stop, fixed size, slip 1 tick, NO |OR| filter) run over
data/vn30f1m_1min.csv (670 sessions 2023-09-11..2026-06-08) + live log (74) = 744 sessions,
joined to DT5G state:

  CRISIS   n=105  WR 51.4%  mean  +2.21bps  Sh 0.40  t +0.26  cum  +1.9%
  NEUTRAL  n=475  WR 54.3%  mean +12.55bps  Sh 2.24  t +3.08  cum +78.1%
  BULL     n=138  WR 47.8%  mean  +1.02bps  Sh 0.16  t +0.12  cum  +0.7%
  EXBULL   n= 26  WR 57.7%  mean +22.91bps  Sh 2.75  t +0.88  cum  +5.9%
  ALL      n=744  WR 52.8%  mean  +9.31bps  Sh 1.59  t +2.73  cum +93.6%

83% of cumulative edge comes from NEUTRAL. In CRISIS+BULL (243 sessions = 33% of sample) the
strategy earns ~0 (+2.6% combined). The paper trial ran 74/74 sessions in NEUTRAL — i.e. it
re-sampled ONLY the regime where the edge already lives. It added no information about the
regimes where the edge is absent. This is exactly the sampling bias the criterion guards against.

## 4. Live window is a MEDIAN window, not an adverse one
597 rolling 74-session windows in history: cum-sum min -3.28% / p10 +0.61% / median +6.60% /
p90 +14.50% / max +18.68%. Live window cum +6.70% = 51st percentile; Sharpe 1.54 = 44th pct.
Only 6.5% of historical 74-session windows are negative. The trial did not sample the tail.

## 5. Live window alone has no statistical power
N=74, mean +9.06bps/day, sd 93.6bps. t=0.832, p=0.41 (two-sided).
Bootstrap (20k) mean 95% CI [-12.98, +29.88] bps/day; P(mean<=0)=0.198.
Bootstrap Sharpe 95% CI [-1.96, +5.87]; P(Sharpe<=0)=0.199; P(Sharpe<1)=0.381.
PSR vs 0 (NO deflation, N_trials=1) = 0.784 -> already below the fleet's 0.95 RED-FLAG line.
Sessions needed for t=2.0 at the observed effect size: 428 (~1.7 yr). For t=1.64: 288 (~1.1 yr).
skew -0.955, excess kurt 2.386, MaxDD -6.15%.

## 6. Config WAS selected from a sweep; DSR/PBO never computed
- vn30f_orb_strategy.py grid A: exit_hm {13:30,14:00,14:30} x stop {None,0.5%,0.7%,1.0%} = 12
  configs; + TC sensitivity {1.5,2.5,3.5}bps; declares "best config exit 14:00, stop 0.7%".
- vn30f_orb_final.py: sizing {fixed-1, vol-target} x slip {0,1,2,3} = 8 configs; declares
  "config cuoi (vol-target + slip 2tick + fee, |OR|>=0.2%)".
- >=20 configs explored, all on the SAME 670-session history. No DSR, no PBO anywhere in repo.
DSR on the live window deflated for the sweep: N=12 -> 0.212; N=20 -> 0.153; N=40 -> 0.097.
All far below 0.95.

## 7. PROVENANCE DEFECT — docstring claim is not traceable
orb_pt.py docstring: "Config CHOT (validated): tat ca ngay (khong loc |OR|), size co dinh,
net slip 1tick + fee". This differs from vn30f_orb_final.py's declared "config cuoi" on THREE
axes simultaneously: sizing (fixed vs vol-target), slippage (1 tick vs 2 tick), and the |OR|
filter (none vs >=0.2%). No artifact in the repo validates the deployed combination. The word
"validated" is unsupported. Note the |OR|>=0.2% variant has HIGHER Sharpe (2.22 vs 1.59) on
full history -- the all-days choice maximizes cumulative return, not Sharpe, and that choice
is undocumented.

## 8. Auditability defect
orb_pt.py re-fetches ALL history from vnstock on every run and rewrites data/orb_pt_log.csv.
It is not an append-only paper record: a vendor data revision silently rewrites trial history,
and no prior state is retained to detect it. Fails the fleet's auditable-backtest standard.

## 9. What DOES hold up (fair statement of the positive side)
- Live OOS mean +9.06bps/day is essentially identical to the 670-session historical mean
  +9.34bps/day. No OOS degradation in the regime it was sampled in.
- Edge is not knife-edge on exit time: 13:30 Sh 1.24 (t 2.03), 14:00 Sh 1.12 (t 1.83),
  14:30 Sh 1.59 (t 2.60) -- all positive on full history.
- Slip sensitivity monotone and survives to 3 ticks (Sharpe 1.19, +7.00bps/day).
- Every calendar year positive; both halves positive (2023-09..2024-12 Sh 1.17;
  2025-01..2026-06 Sh 1.94).
- Full-history t=+2.73 over 744 sessions -- but 670 of those were the selection sample.

---
# CORRECTION after quant-skeptic adversarial review (agent a86fc2125b8011808, 2026-09-25)

VERDICT on my headline claim as stated: **REFUTED**. Verdict on the ACTION: unchanged
(CONTINUE PAPER), but it must be re-argued on different grounds. Corrections I accept:

## C1. §3 "the ORB edge is regime-CONDITIONAL" — WITHDRAWN
I ran four one-sample t-tests and read the spread between them as a regime effect. That is a
DIFFERENCE claim and I never tested a difference. It fails at every defensible framing:
  ANOVA across 4 regimes        F=0.939  p=0.42
  Kruskal-Wallis                H=2.977  p=0.40
  Welch NEUTRAL vs rest         t=1.21   p=0.23
  Episode-level (N=13 regime runs = the honest independent-event count):
      Mann-Whitney p=0.18, Welch p=0.20
Correct statement: the ORB edge is NOT demonstrably regime-conditional.

## C2. §3 "CRISIS/BULL earn ~0" — WRONG, it is UNTESTED
  CRISIS n=105 mean +2.21bps  95% CI [-14.80,+19.22]  power@9.31bps = 0.19
  BULL   n=137 mean +1.05bps  95% CI [-16.30,+18.39]  power@9.31bps = 0.18
Both CIs contain the full-sample +9.31 AND NEUTRAL's +12.55. Detecting +9.31bps at 80% power
needs ~700 CRISIS / ~955 BULL sessions. Two further noise signatures: ordering is non-monotone
(EXBULL +22.91 sits next to BULL +1.02), and BULL's near-zero mean rests on ONE 10-session
episode at -42.7bps (excluding it, BULL = +4.49bps).
=> "untested in CRISIS/BULL", not "no edge in CRISIS/BULL".

## C3. §4 rolling-window framing overstated
596 overlapping windows come from only ~9 non-overlapping blocks. Live window ranks 5th of 10
non-overlapping blocks — the "median, not adverse" conclusion HOLDS, the "597 windows" framing
was decorative. My tail percentiles also drifted slightly vs skeptic's recompute
(min -3.28 vs -3.53, negative-window share 6.5% vs 7.9%).

## C4. Session count 744 -> 743; §4 unit inconsistency
My §3 table used the research scripts' `len(g)>=150` completeness rule, not orb_pt.py's own
`last bar >= 14:25`. Deployed-code count is 669 hist + 74 live = 743 (BULL 137, not 138).
Also §4 quoted +6.70% (arithmetic sum) while §1 quoted +6.59% (compound) for the same window.

## C5. TWO GATE CRITERIA I MISSED — both cut harder than my own argument
I evaluated only registry criterion #1. All four are still `pending`:

**[2] "Walk-forward 2024 full-year loss được giải thích/không lặp lại trong forward window."**
This is the sharpest defect. Verified by direct recompute:
  ORIGINAL validated config (exit 14:00, stop 0.7%, |OR|>=0.2%, TC 2.5bps):
      2024 n=76  mean -5.93bps  Sharpe -1.84  cum  -4.50%   <- the loss the criterion is about
  DEPLOYED config (exit 14:30, no stop, all days, slip 1 tick):
      2024 n=250 mean +5.69bps  Sharpe +1.18  cum +14.43%   <- it disappears
The 2024 loss was not EXPLAINED; it was dissolved by a config change. And the forward window
has never tested the config the criterion was written about. Consequence: my §9 line
"Every calendar year positive", filed under "What DOES hold up", is true ONLY for the
un-validated config — the single most misleading line in this document.

**[3] "Hạ tầng phái sinh ... bot hiện CASH-EQUITY ONLY — chưa thể live dù edge có thật"** —
an independent hard blocker on graduation, regardless of any statistic. (Out of scope for this
job per the dispatch; noted only because it is a registry gate criterion.)
**[4]** sleeve <=5% NAV + quant-skeptic + user sign-off — not addressed.

## C6. Capacity premise in the tasking was wrong by 100x — non-issue either way
`reco_contracts` = 5, not 515 (MULT = 100,000 VND/point => 1 contract ~194M VND notional).
Median 09:30-bar volume since 2025-06 = 1,078 contracts; 5 contracts = 0.46% of ONE bar.
Fully absorbable. Undeclared conventions worth fixing: 1 contract = 19.4% of the sleeve so
rounding 5.16->5 is a -3% size error, and "1B sleeve" is full NOTIONAL while VN30F initial
margin is ~17%.

## C7. Things that SURVIVED the attack (my claims the skeptic could not break)
- All headline numbers reproduced to quoted precision on an independent rebuild (NAV +6.5881%,
  WR 0.5541, Sharpe 1.5362, bootstrap CIs exact, PSR 0.784, NEUTRAL t=+3.08, DSR 0.216/0.156/0.100).
- NO look-ahead: lagging DT5G 1d/2d keeps NEUTRAL t=+3.13/+3.00; delaying ORB entry +1/+2/+3/+5
  bars past the 09:30 close gives +9.52/+9.42/+8.91/+8.68bps vs deployed +9.36. Exit correctly
  excludes the 14:45 ATC bar (which holds the file's largest 1-min move, -3.56% on 2025-12-25).
- §2 regime fact stands: 75/75 days NEUTRAL, state_raw identical, zero transitions.
- §5 (no statistical power), §6 (>=20-config sweep, DSR 0.10-0.22), §7 (config provenance
  defect), §8 (non-append-only log) all CONFIRMED. §8 is worse than I stated: vnstock returned
  bars from 2026-08-24 14:02 for a start=end=2026-08-26 request, so silent history rewrite is a
  live risk, not theoretical.
- VN30F1M splices contracts unadjusted (day-after-expiry mean |overnight gap| 0.639% vs 0.334%)
  but ORB is strictly intraday, so no splice gap enters a return. Clean.
- New caveat from the skeptic: `asof_date` shows 3131/3244 DT5G rows written in ONE batch on
  2026-07-30 — historical DT5G labels are a full-sample backfill, not a point-in-time series.

## C8. CORRECTED VERDICT — (B) CONTINUE PAPER
Grounds, in order of weight:
1. N=74 has no power: t=0.83, p=0.41; bootstrap mean CI [-12.98,+29.88]bps; P(mean<=0)=0.198.
   PSR (undeflated) 0.784 is already under the fleet's 0.95 red-flag line; DSR deflated for the
   >=20-config sweep = 0.10-0.22. Need ~428 sessions (~1.7yr) for t=2.0.
2. The window was a 51st-percentile window (5th of 10 non-overlapping blocks) — it did not
   sample the adverse tail the criterion exists to reach.
3. Criterion #1 regime condition literally unmet: 75/75 days NEUTRAL, zero transitions.
4. Criterion #2 is not met and is currently being masked: the 2024 loss was erased by an
   un-validated config swap rather than explained.
5. Criterion #3 (no VN30F execution path) is an independent hard blocker; #4 untouched.
NOT grounds (withdrawn): "the edge is regime-conditional / absent outside NEUTRAL."
