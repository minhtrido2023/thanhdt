---
name: trade-due-diligence
description: Use whenever a BUY order is being proposed, reviewed, or approved for the VN trading fleet — building a trade plan (DollarBill), reviewing a plan before approving it (Mike/user), or writing a `dd_override_reason` for an order the automated due-diligence layer flagged 🔴. Also use when deciding whether a flagged candidate should be dropped instead of overridden. Encodes what each mechanical red flag actually means, what evidence resolves it, and what a defensible override reason looks like — built from the DHD case (2026-08-03), where two 🔴 lines were printed at every stage and nobody was required to read them.
---

# Due-Diligence Review — Checklist for Writing `dd_override_reason`

This is a **review checklist for a human/agent deciding on a BUY order**, not a backtest
checklist (that's `quant-research`). It answers one question: *this candidate has a mechanical
red flag — do we buy anyway, and on what stated basis?*

## What the mechanism is (and deliberately is not)

`trading_bot/due_diligence.py` runs on **every** buy candidate at four choke-points
(`golive_recommend_v23.py`, `send_plan_report.sh`, `eod_trading_report.sh`,
`dc_book_waterfall_paper.py`). It is **THUẦN THÔNG TIN** — mandate 2026-07-21, unchanged:
it does **not** block orders, does not change sizing, is not a hard gate.

What was added 2026-08-03 (after DHD) is a **confirmation step**, mirroring the DCF
`dcf_override_reason` pattern exactly:

- `run_due_diligence()` emits mechanical flag codes (`red_flags` list, `has_red_flag` bool) —
  generated at the point of computation, **not** by grepping the 🔴 emoji out of display text.
- `PlannedOrder.dd_check` (dict) + `PlannedOrder.dd_override_reason` (str) in
  `trading_bot/plan.py`.
- Red flag + `side=buy` + empty `dd_override_reason` → **⚠ WARN** in the plan-build notes
  (`strategies.py`) and in the plan-approval report (`send_plan_report.sh`), plus a
  `dd-redflag-fill` bus event when the order actually fills (`executor.py`).
- **The order still executes.** Missing reason = a visible gap in the record, not a blocked
  trade. If you think a flag *should* block, that is a separate proposal to the user — do not
  turn this WARN into a gate on your own.

Precedence: the hard gates that already exist (forensic/legal list, >7% NAV, first-time-buy,
DCF RICH-robust, `cap_lag_orders` %ADV ceiling, LAG 8L rating ≤3, `excluded_tickers`) are
untouched and still bind. A due-diligence override **cannot** unblock any of them.

## The red flags — what each one means and what resolves it

Codes come from `RED_FLAG_CODES` in `trading_bot/due_diligence.py`; keep this table in sync
with that dict (a selfcheck asserts every emitted code is documented there).

| Code | Fires when | What it actually means | What a valid override needs |
|---|---|---|---|
| `THANH_KHOAN_CHET` | ADV3T ≤ 100tr VND/phiên (`Volume_3M_P50 × Price`) | The name trades below the floor the backtested model assumes — the pinned edge was never measured on names like this, and you likely cannot exit at the modelled price | An explicit statement that the position is (a) small enough that exit is trivial vs real daily volume, and (b) accepted as **outside** the model's evidence base — not "backtest says LAG works" |
| `NGOAI_UNIVERSE` | not in `universe_pit` (point-in-time) on `asof` | The name is not in the tradable universe the strategy was fit/simulated on; V2.4's R3 numbers do **not** cover it | Why this specific name is being traded outside the universe, and who accepted that (a person, in the plan record) |
| `LENH_QUA_LON_VS_ADV` | order value > 25% of ADV3T | Market impact/partial-fill risk: the ref price in the plan is not the price you'll get | Either resize (preferred — remove the flag instead of overriding it), or state the fill strategy (multi-session accumulation, limit discipline) |
| `SURPRISE_PHONG_CO_HOC` | `NP_P4 ≤ 0` (LAG/PEAD only) | The %YoY earnings surprise driving the PEAD signal is arithmetically meaningless — a negative base inflates the percentage; the signal is measuring the base, not the improvement | An earnings-quality read that does not depend on %YoY (absolute VND profit, revenue, margin trend, cash flow) showing a real improvement |
| `DD_KHONG_CHAY_DUOC` | DD couldn't run (missing row in `bq_cache/ticker`, read error) | You are buying with **zero** automated verification — not a data nuisance, a blind spot | Say what was checked manually instead (DNSE live quote/volume, broker data), or wait for the data |

**Not red flags on purpose** (they show as ⚠, meaning *consider*, not *justify in writing*):
thin liquidity (ADV < 2 tỷ but > 100tr), Q-C quality flag, a loss quarter inside the YoY base,
an anomaly-scan tier echo, and universe read failure (`n/a` ≠ outside — never treat unknown as
excluded, §4.3). **DCF RICH+robust and DCF NOT_COMPUTED / negative FCFE are NOT dd red flags** —
DCF has its own `dcf_override_reason` field; the same decision is never asked twice. Weak
fundamentals (high `Debt_Eq_P0`, low `ROE5Y`/`FSCORE`) print in the DD FA line for context but
do not raise a flag — the 8L rating gate and the golden floor already own that axis.

## Writing a defensible `dd_override_reason`

Put it on the order in the plan JSON:

```json
{"id": "BUY-DHD-01", "ticker": "DHD", "side": "buy", "quantity": 200,
 "ref_price": 26700, "book": "LAG",
 "dd_override_reason": "User chốt 08-03: chấp nhận mua ngoài universe/dưới sàn thanh khoản..."}
```

A reason is defensible when it:

1. **Names the flag(s) it is answering.** A generic "signal is strong" answers nothing.
2. **Says who decided.** If the user confirmed in real time, say so (same provenance
   discipline as `decided_by: "user"`, coding_guidelines §20). If it's an agent's judgment,
   say that instead — don't imply user approval that didn't happen.
3. **Cites evidence outside the flagged axis.** Answering `THANH_KHOAN_CHET` with a backtest
   CAGR is circular: that backtest excluded such names.
4. **States the bound.** Position size cap, no scaling up, exit intent — an override is for
   *this order*, not a standing exemption for the ticker.

Not defensible: "rating 8L pass", "model says buy", "small position" alone, "we did this
before", or silence. If you cannot write points 1–4, that is the answer: **drop the
candidate** — overriding is not the default resolution, it is the exception you must argue for.

## Worked example — DHD, 2026-08-03 (the case that created this skill)

Automated output at 08-03, LAG_LO window, 200cp @ 26,700đ (~5.34tr):

```
DD DHD [LAG] (data 2026-07-31): 🔴 thanh khoản ~0 (ADV3T 59 tr/phiên) — NGOÀI mô hình backtest
    · 🔴 NGOÀI universe_pit · lệnh dự kiến 5 tr = 9% ADV · nền YoY dương
    FA: ROE5Y 8.9% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.94 · PE 20.53
    🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
```

Both 🔴 lines were already printed on 08-03 at every stage — and the candidate still travelled
through the pipeline into plans on 07-31, 07-30 and 08-03 before a human caught it. That is the
exact gap the confirmation step closes: the information was never missing, the *obligation to
answer it* was.

What the review found on the merits (job `Taylor_20260803_015850`): DHD passes every other gate
(8L rating 3, FSCORE 5, D/E 0.94, `d_NPR` and non-op checks pass) — **only** the liquidity axis
catches it. And the decisive argument for skipping was not the red flag itself but a sizing
fact: 200cp = 27.2% of the slot target, below the engine's `min_fill_pct=0.30`, i.e. a position
the pinned model would never hold. Both accounts skipped it (`USER SKIP 2026-08-03`).

Note the honest counter-evidence: DHD's 3 historical LAG events returned +11.9% / +10.3% /
−3.4% (avg +6.2% vs pool +4.23%), so a 2 tỷ liquidity floor would have blocked all three
profitable entries. This is why the flag is a **WARN requiring an answer**, not a gate: the
liquidity axis is real, and the cost of enforcing it mechanically is also real. See
`mike/agents/Taylor/research/lag_quality_gate_20260803.md`.

## Reviewer checklist (plan approval)

1. Every buy line in the report — does it show a 🔴 DD cờ đỏ line? If yes, is there a
   `lý do override DD:` line right under it?
2. Is the reason answering *these* flags, with evidence off the flagged axis, and does it name
   who decided?
3. Would resizing remove the flag (`LENH_QUA_LON_VS_ADV` especially)? Prefer resizing.
4. Does the position matter at the size that survives the constraint? A position too small to
   move NAV (DHD: 27.2% of slot) is a reason to skip, independent of the flag.
5. After the fill, a `dd-redflag-fill` bus event exists — spot-check periodically that the
   override reasons recorded there hold up, the same way `dcf_lens_history` is reviewed.

## Files

- `trading_bot/due_diligence.py` — flags + `RED_FLAG_CODES` + `format_dd_check()` +
  `dd_check_for_order()`
- `trading_bot/plan.py` — `PlannedOrder.dd_check` / `.dd_override_reason`
- `trading_bot/strategies.py` — plan-build WARN note; `trading_bot/executor.py` — fill audit event
- `mike/bin/send_plan_report.sh` — plan-approval display
- `due_diligence_selfcheck.py` — 35 checks, incl. the DHD case and a `NotAGate` class that
  fails if anyone turns this WARN into a blocking gate
