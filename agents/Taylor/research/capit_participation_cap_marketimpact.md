# CAPIT ADV20-basis switch — market-impact / self-competition risk test

**Job:** Taylor_20260721_050720 (follow-up to Taylor_20260721_043923, quant-skeptic CONFIRMED
`verify_20260721_050105.log`) · **Date:** 2026-07-21 · **Author:** Taylor (Quant)

**Question (narrowed by user):** Chase-price risk is OUT of scope — `max_chase_pct_buy=0.015`
(config.py:47) is an independent, unchanged guard. The one thing quant-skeptic still doubted:
if we drop the real-time `q.day_volume` participation guard and use **ADV20** for CAPIT buys,
does the bot consume **too much % of the ACTUAL day's traded volume** on genuinely thin
sessions (market-impact / being-an-outsized-participant), i.e. is the realtime guard silently
protecting us in the past where ADV20 wouldn't?

---

## Mechanism recap (the exact thing being changed)

Executor `_child_qty` (executor.py:375-380): `allowance = int(0.10 × q.day_volume) − fleet_filled`;
`if allowance < LOT → return 0`. `max_participation=0.10`. This is the **per-round pacing** guard.
Proposal: for `book==CAPIT` only, change the **basis** from real-time `day_volume` to **ADV20**
(keep 10%). Order size is ALREADY capped upstream at `0.20×ADV20` shares by `plan.cap_capit_orders`
(= `capit_adv_caps`, X·D·ADV20 = 0.10·2·ADV20).

**Structural identity used throughout:** let `f = Volume_today / ADV20`.
- **Realtime basis (current):** fleet fill ≤ 10% of realized day tape **by construction, always ≤10%.**
- **ADV20 basis (proposed):** guard permits `0.10×ADV20` shares → as % of the actual day tape =
  `0.10/f`. Thinner than average (f<1) ⇒ >10%; f<0.5 ⇒ >20%. Realized fill also bounded by order
  size and by seller availability at ≤+1.5%.

## Data
Full daily `tav2_bq.ticker.Volume` for the 5 current basket names (NCT/PVT/SAB/SIP/VNM), 2013→2026-07-20
(13,735 name-days after causal ADV20 warm-up). ADV20 = median of 20 **prior** trading days (causal, no
look-ahead). 12 recorded washout events (`data/_washout_baskets.csv`, 2014→2026).

---

## Result 1 — MI distribution across order-size regimes (all name-days pooled)

| order size (frac of ADV20) | realtime MI (median / p95 / max) | ADV20 MI (median / p95 / max) | ADV20 days >20% | >50% |
|---|---|---|---|---|
| **~2.2% ADV20** (NCT-real 2026-07-21) | 2.18 / 6.39 / **10.0%** (capped) | 2.18 / 6.42 / ∞* | 0.61% (84 d) | 0.20% (27 d) |
| 10% ADV20 (= the exec guard itself) | 10 / 10 / **10.0%** | 10.1 / 29.7 / ∞* | 13.1% | 1.74% |
| **20% ADV20** (= plan-cap MAX) | 10 / 10 / **10.0%** | 10.1 / 29.7 / ∞* | 13.1% | 1.74% |

*∞ = the 14/13,735 (0.1%) genuine halt days (Volume=0); guard "permits" unbounded relative
participation but in reality the order sits **unfilled** (no sellers) — none fall in a real event window.

**Read:** realtime caps at ≤10% of realized tape by design. ADV20 diverges only on the thin tail. At the
**realistic** order size CAPIT actually generates (~2% ADV20), even ADV20 keeps MI ≤10% on 98% of days.
At the **maximum legal** order (plan-cap 0.20×ADV20, guard-bound to 0.10×ADV20/session), ADV20 would let
the fleet be **>20% of the tape on 13% of days, >50% on 1.7%.**

## Result 2 (DECISIVE) — f on the 12 REAL washout events + the T+0..T+2 execution window

Washout **day itself** spikes (f_D0 median **1.77**) — but the bot executes on **T+1/T+2**, and those
frequently revert thin:

| stat (n=52 name×event obs) | value |
|---|---|
| f_D0 (event day) median | 1.77 (p10 0.56, min 0.32) |
| **f_min over exec window D0..D2** median | **0.84** (p25 0.48, p10 0.34, **min 0.09**) |
| obs with a thin exec day f<0.5 | **26.9%** |
| obs with f<0.3 | 5.8% |

Concrete thin exec-window cases: NCT 2016-01-18 f_min 0.18, NCT 2022-06-20 f_min 0.09, SIP 2022-06-20
f_min 0.14, SIP 2026-03-09 f_min 0.34. **ADV20-basis MI on the thinnest exec day:**
- order ~2.2% ADV20 (realistic): median **2.6%**, p90 6.3%, **max 24.0%**
- order 10% ADV20 (max, guard-bound): median 11.9%, p90 29.3%, **max 111%** (=unfilled)

**This is the key finding and it corrects the naive "washout = volume spike ⇒ ADV20 always safe"
reassurance from the prior memo.** The spike is on D0; CAPIT buys over the following ~2 sessions, and a
genuinely thin day lands inside the real execution window **~1 in 4 times**. So the realtime guard is
**NOT purely redundant** — on that ~27% it provides real outsized-participation protection that pure
ADV20 discards.

## Result 3 — absolute scale (why the tail hasn't bitten yet)
Recent `0.10×ADV20` guard notional: NCT **116M VND**, PVT 5.3B, SAB 3.8B, SIP 2.5B, VNM 22B. The actual
NCT order 2026-07-21 was **47M (500sh)** ≪ the 116M guard → for NCT the binding constraint is the *order
size* (NAV-target-driven), not the participation guard at all. Big names have enormous headroom.

---

## Honest limitation
Daily bars cannot see the **intraday-morning** thinness that actually triggered the 2026-07-21 NCT block
(that was <1000cp realized by 11:29 on a name whose full day likely normalized). BUT — for the
**market-impact** question (fill ÷ *whole day's* tape) the full-day volume is the **correct**
denominator, so this daily test is *more* valid for THIS question than a daily test would be for the
*block-cost* question the prior memo rightly declined. The residual gap: intraday, realtime is even more
protective than the daily f implies (it paces against cumulative-so-far, always < full day), so pure
ADV20 removes *more* protection intraday than the daily numbers show — the daily test **understates**,
not overstates, the divergence.

## Conclusion — wire now vs. need more?

**The risk is now QUANTIFIED and BOUNDED — this does NOT block wiring; no further data-gathering is
needed** (this test answered the exact market-impact question quant-skeptic flagged). The remaining
choice is a **design** decision, not an evidence gap:

1. **Pure ADV20 basis** is *acceptable at current realistic sizes* (worst historical MI 24% of a thin
   exec-day tape, median 2.6%) given CAPIT's stated impact appetite + 3 intact guards (chase-cap 1.5%,
   plan-cap 0.20×ADV20, max_child_value 200M) + seller-scarcity self-limiting (a truly dead day → order
   unfilled, not a price push). **BUT this safety margin is a coincidence of today's small sizing (NCT
   2.2% ADV20), not structural** — it erodes toward the >20-100% tail if a future CAPIT order approaches
   the plan cap on a thin-exec-window name.

2. **RECOMMENDED — ADV20 floor + realized-volume ceiling (hybrid):** wire the ADV20 basis (fixes the
   real 2026-07-21 over-block false-negative) but layer a co-active **realized-volume ceiling (~25-30% of
   cumulative day_volume)** so the fleet can never become a *majority* of a thin day's tape even at max
   sizing. Note the two goals genuinely tension (a low realized-ceiling would re-introduce the
   thin-morning zero-block; the ADV20 floor is what must unblock the morning), so the exact guard shape
   is an **implementation decision for the wiring PR** — with its own selfcheck + quant-skeptic — not
   finalized here. Set the ceiling loose enough (≥25%) that it never reproduces the 2026-07-21 pathology
   (which needed the guard <10% of realized) yet still catches the >30% tail.

**Bottom line:** wireable now; recommend the **hybrid (ADV20 floor + ~25-30% realized ceiling)** over
pure ADV20 for robustness against future larger sizing. If the team prefers pure ADV20 for simplicity,
that is defensible *today* but must ship with an explicit documented caveat that the margin depends on
CAPIT orders staying small (≲5% ADV20) relative to the plan cap.
