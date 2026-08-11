---
name: dnse-fill-reconciliation
description: Use before claiming any order/plan "executed", "filled", "đã đạt X% NAV", or "đã mua đủ" for SpaceX/ZaloPay — planned quantity is not filled quantity. Also use before finalizing any daily/EOD/plan-followup report that states position sizes or execution results. Encodes the real 2026-08-11 incident — Mike reported TV1 "already at ~5% NAV" from the PLAN's order quantity, then discovered via DNSE's own broker confirmation that only 100/2,000cp (SpaceX) and 0/1,300cp (ZaloPay) actually filled, because TV1's ADV is too thin to absorb the full clip in one session.
---

# DNSE Fill Reconciliation

**The gap this closes: "lệnh đã ĐẶT" ≠ "lệnh đã KHỚP".** A plan's `orders[]` records intent
(quantity requested, limit price). It says nothing about how much of that actually traded. For
liquid names this gap is usually zero. For thin names (UPCOM, ADV under a few tỷ/ngày — TV1, DRI,
and similar discretionary/LAG picks are exactly this shape) it can be the entire order.

## When this bites

Any claim of the form "vị thế X đã đạt Y% NAV" or "đã mua đủ Z cổ" derived by reading `orders[]`
quantities and multiplying by price — without checking what actually cleared — is a guess dressed
as a fact. The 2026-08-11 case: DRI (thicker liquidity) filled exactly as planned both accounts;
TV1 (ADV ~0.6 tỷ/ngày) filled 5% of the SpaceX clip and 0% of the ZaloPay clip, on the same plan,
same day, same due-diligence sign-off. Nothing was broken — the order was placed correctly, priced
correctly, inside the approved band. The market simply didn't have a counterparty for the rest.

## The two sources, and when each is live

1. **`data/execution_logs/dnse_raw_<date>.jsonl`, `kind: positions`** — live, updates through the
   session. Read the LATEST record per account, compare `openQuantity`/`accumulateQuantity` for
   the ticker against the pre-order baseline. Available any time during/after the session.
2. **DNSE's own "Báo cáo giao dịch khớp lệnh" email** — broker-issued, arrives ~16:30 ICT,
   itemizes every matched fill line (qty, price, exchange fee, broker fee, tax) for BOTH accounts
   in one file. This is the authoritative source per coding_guidelines §6 ("trace to the broker's
   confirmation, never a downstream summary"). Only exists after ~16:30 ICT — don't expect it
   for same-session/intraday reporting.

Fetch + parse the email with **`fetch_dnse_khoplenh_email.py`** (WorkingClaude root, reuses the
Gmail OAuth readonly credential already set up for auto-OTP — no new credential needed):

```bash
python3 fetch_dnse_khoplenh_email.py --date 11/08/2026
```

Registry entry (bẫy, layout, ownership): `mike/kb/data_registry/trading-bot/dnse_khoplenh_broker_email.md`.

## The check, every time

1. Before writing "đã mua đủ" / "đạt X% NAV" / any executed-quantity claim: pull today's actual
   fills (source 1 if same-day before 16:30 ICT, source 2 if after) — never the plan's `orders[]`
   quantity alone.
2. `groupby(tieu_khoan/account, ma/ticker)` before comparing — the broker email bundles BOTH
   accounts in one file (same §12 discipline as `dnse_raw_*.jsonl`).
3. Diff planned qty vs filled qty per (account, ticker). Non-zero gap → state it explicitly, don't
   round up to "target achieved". Thin-liquidity names (check ADV in the due-diligence note) are
   the ones to expect a gap on; liquid names filling short is a separate, more interesting problem
   (check for a price/ceiling bug per §24 before assuming it's just liquidity).
4. A real gap → feed the shortfall into the NEXT plan as a continuation order (same ticker, same
   target), not a one-off manual top-up — this is what already happens automatically today
   (DollarBill's 2026-08-12 plan independently proposed the exact TV1 shortfall for both accounts
   without being told the gap existed — same underlying data, `dnse_raw` positions, read directly).

## What this doesn't replace

This is a same-day reconciliation habit, not a new canonical source. `dnse_raw_*.jsonl` stays
CANONICAL for cost-basis (coding_guidelines §6's standing pipeline: `verify_account_snapshot.py` →
`daily_nav_snapshot.py` → `reconcile_equity.py`). The broker email is an **independent cross-check**
— useful precisely because it's a different pipeline (DNSE's own backend, not our API client), so
it can catch a bug in either side. Folding it into the automated report-generation pipeline itself
(not just an ad-hoc check) is a bigger change — that goes through Taylor + quant-skeptic review
before being trusted as a report input, same as any other change to the §6 pipeline.
