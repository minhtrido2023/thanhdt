# CAPIT vs `max_participation` (realtime day_volume) — research memo

**Job:** Taylor_20260721_043923 · **Date:** 2026-07-21 · **Author:** Taylor (Quant)
**Question (Mike/user):** Should the executor's `max_participation=10%` rule — which throttles
per-round buy qty against **real-time cumulative matched volume** (`q.day_volume`), NOT long-run
ADV — be applied differently for CAPIT (bear-washout basket)? Trigger: NCT total-blocked all
morning 2026-07-21.

> ⚠️ Scope: this is about **mechanism (2)** `max_participation` in
> `trading_bot/executor.py._child_qty()`. It is NOT `capit_adv_caps()` in
> `golive_recommend_v23.py` (mechanism (1), the ADV20 total-day cap). The two are easy to
> confuse — they share the `0.10` number but have different bases and live in different layers.

---

## 1. The two caps, precisely (this is the whole answer in one table)

| | (1) `capit_adv_caps` — TOTAL-day | (2) `max_participation` — PER-ROUND pace |
|---|---|---|
| Where | `golive_recommend_v23.py`, enforced in `plan.filter_capit_adv_caps()` at **plan-load** | `executor._child_qty()` at **each execution round** |
| Basis | **ADV20** (20-day median trading value, causal, washout day excluded) | **`q.day_volume`** = shares matched *so far today*, live from quote API |
| Formula | `cap_vnd = 0.10 × ADV20 × 2.0` → caps `o.qty` to `round_lot(cap/ref)` | `allowance = int(0.10 × day_volume) − fleet_filled`; **if `< LOT` → return 0** |
| CAPIT-specific? | YES (only `book==CAPIT` buys) | NO — global rule for every order |
| Role | bounds **how much total** per name per day | bounds **how fast** within the day |

**Key structural fact:** for a CAPIT buy, `o.qty` reaching the executor is **already ADV20-total-
capped** by (1). So on the *total-quantity* dimension the realtime cap (2) is **redundant** for
CAPIT. Its only distinct job is intraday pacing — and that is exactly where it malfunctions on
thin names.

**The binding boundary of (2):** `allowance < LOT` ⟺ `0.10 × day_volume < 100` ⟺
**`day_volume < 1000 shares`** → returns 0 → *no order placed at all*, regardless of book depth.

---

## 2. Live evidence — NCT, 2026-07-21 (n=1, decisive)

Plan (`plan_SpaceX_2026-07-21.json`): `BUY-NCT-01`, **500 shares** (5 lots) @ ref 94,200,
target 52.3M, `book=CAPIT`, `play_type=CAPIT_GOLDEN`, `capit_status=WASHOUT`.

Journal (`exec_SpaceX_2026-07-21_journal.csv`): **357× `WAIT_QUOTA` ("hết quota
participation/đợi KL") from 09:30 to 11:29, ZERO fills.** ZaloPay: 233 identical events, also 0
fills. **NCT completely blocked all morning on both accounts.**

Because `WAIT_QUOTA` (allowance<LOT) fired on *every* round while `fleet_filled` stayed 0, the
journal itself **proves `day_volume < 1000 shares` continuously for ~2 hours**. NCT ADV20 ≈
2.178B VND ≈ ~23,100 sh/day → the whole morning traded **< 4.3% of a normal day's volume**.

Meanwhile the order book had **firm two-sided quotes (94,300 bid / 94,400 ask)**. The 500 shares
SpaceX wanted = **~2.2% of ADV20** — trivially fillable by lifting the ask with negligible
impact. And it was **already bounded** by every other guard:
- `capit_adv_caps` total-day cap NCT/SpaceX = 218.9M ≈ **2,323 shares** → 500 ≪ 2,323, *not
  binding*.
- chase-cap: buy limit = ref×(1+1.5%), min with ceiling → bot physically **cannot pay >
  +1.5%**.
- `max_child_value` 200M/round → not binding for a 47M order.

→ The **only** thing that blocked NCT was cap (2) mistaking "few sellers have crossed *yet*"
for "no liquidity." The user's hypothesis is correct: low *realized* volume ≠ absent liquidity,
especially early on a panic day when sellers are hesitant — **the exact condition CAPIT is
designed to buy into.** So the cost of the current rule is **structurally concentrated on
CAPIT's highest-conviction, thinnest, biggest-discount names** (you fill the liquid recoverers
PVT/SAB/VNM, miss the illiquid NCT with the sharpest washout).

**Aggravating factor:** cap (2) is **fleet-shared** (`self.shared[ticker]`) — both accounts draw
from the *same* `0.10 × day_volume` pool, so on a thin name the two accounts compete for one tiny
quota, roughly halving each's effective pace.

---

## 3. Answering the four research questions

**Q1 — switch CAPIT basis to ADV20? → YES. This is the recommended fix.**
CAPIT is explicitly designed to buy into abnormally low realized volume; a realtime-volume gate
misreads that as illiquidity. Basing the per-round allowance on ADV20 (already computed for
cap (1)) instead of `day_volume` eliminates the pathology while keeping a liquidity-proportional
pace. Since `o.qty` is *already* ADV20-total-capped upstream, this is low-risk (see Q4).

**Q2 — keep realtime basis but raise % to 15–20%? → NO (insufficient + wrong lever).**
Raising to 20% only moves the block boundary from `day_volume<1000` to `day_volume<500` shares.
NCT was under 1000 (and for stretches under 500) all morning → 20% would **not reliably** have
unblocked it. It treats the symptom (level), not the cause (wrong basis), and — because
`max_participation` is **global** — it would weaken impact protection for *every* non-CAPIT order
too. Reject.

**Q3 — quantify cost of the current approach.**
- Live: n=1 but decisive (§2) — a total miss on the thinnest, highest-conviction washout name.
- Historical: **cannot be honestly backtested.** The failure is **intraday** (early-session
  realized volume << ADV). BQ holds only **daily** bars; the bot's **quote stream is not
  persisted** (`dnse_raw_*.jsonl` logs only orders/positions/balances — verified, 0 NCT quote
  records). Worse, washout days are *volume-spike* days by definition, so *daily* volume would
  **understate** the problem and could falsely reassure. Fabricating a daily-volume "backtest"
  here would be methodologically wrong — I explicitly decline it. The robust claim stands on
  mechanism + the live event: the cost is real and concentrated on exactly CAPIT's best targets.

**Q4 — quantify risk of loosening (ADV20 basis for CAPIT).**
Bounded, because switching cap (2)'s basis leaves **three** independent guards intact:
1. cap (1) `capit_adv_caps` total-day ceiling (ADV20-based) still caps `o.qty` (NCT: 2,323
   sh/acct).
2. chase-cap 1.5% + ceiling caps price per lot — bot **cannot push price beyond +1.5%** by
   construction.
3. `max_child_value` 200M/round caps per-round notional.
Worst case under ADV20 basis on a genuinely dead book = the order **sits unfilled** at the
chase-capped limit (no impact) — never "pushes price." For NCT even a full 500-share single-round
post = ~2.2% ADV20 @ ≤+1.5% = negligible. This is within CAPIT's stated risk appetite (accept
higher impact for a rare cheap entry).

---

## 4. Recommendation

**Change the BASIS, not the level.** For `book==CAPIT` buys only, replace the realtime
`day_volume` participation basis in `_child_qty()` with an **ADV20 basis** (reuse the ADV20
already implied by `capit_adv_caps`), or equivalently **exempt CAPIT buys from cap (2)** since
`o.qty` is already ADV20-total-capped upstream and price/notional are independently bounded.
**Keep the global realtime 10% rule unchanged for all non-CAPIT orders. Do NOT raise the global
%.**

Feasibility: the executor order object already carries `o.book` (`plan.py:23`), and
`plan.py:184` already has an `is_capit` helper — a CAPIT-aware branch in `_child_qty` is a
minimal, surgical change.

**NOT wired.** This memo is research only. Any change to `executor.py`/`max_participation` is a
live money-risk parameter → requires **quant-skeptic CONFIRMED** + **separate user approval**
before wiring. Suggested skeptic angle: does exempting/rebasing cap (2) for CAPIT create any
path where the bot becomes an outsized fraction of a *truly* thin round given guards (1)+(3)
are intact? (Expected: no, but adversarial-verify.)

---

## 5. Caveats / honesty notes
- n=1 live event; no intraday historical backtest is possible (data does not exist) — argument
  rests on mechanism + the single decisive live case, not a distribution.
- Fix reduces one failure mode (total-block on thin washout) at the cost of slightly higher
  potential intraday footprint on CAPIT names — judged acceptable given guards (1)/(2-price)/(3)
  and CAPIT's explicit risk appetite, but this is a **judgment**, not a measured Sharpe gain.
- DSR/PBO/walk-forward are **not applicable**: `max_participation` is an execution-microstructure
  parameter invisible to the daily-bar strategy backtest (no NAV series depends on it).
