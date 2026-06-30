# Insurance (Bảo hiểm) — Valuation Framework & Quick Screen Verdict

Sector #15. Author: Taylor. Date: 2026-06-30. Job: Taylor_20260630_080041.
**QUICK CHECK only** (no full backtest — universe + walk-forward both kill it early).

## 1. Universe (ticker_prune, ADV)
| Ticker | Type | First | ADV all-time | ADV 2023+ | Verdict |
|---|---|---|---|---|---|
| BVH | Life + non-life + invest | 2009 | 26.6B | **32.8B** | only genuinely liquid name |
| MIG | Non-life (military) | 2019 | 12.2B | 6.3B | moderate, young (2019+) |
| BMI | Non-life (Bảo Minh) | 2007 | 5.8B | 5.8B | moderate |
| PVI | Non-life + reinsurance | 2007 | 6.1B | 5.3B | moderate |
| BIC | Non-life (BIDV) | 2012 | 2.7B | 3.7B | thin |
| PTI | Non-life | 2011 | 1.0B | **delisted from prune 2022** | drop |

→ One liquid name (BVH), 3-4 moderate, 1 thin, 1 dropped. Slightly deeper than aviation but still a **5-name pond, single liquid name**.

## 2. International framework vs BQ reality
- **P/B primary** (like banks — capital deployed): ✅ available.
- **ROE vs COE**: ✅ ROE5Y available. VN COE ≈ 14-16%. **Every VN insurer sits BELOW COE** (ROE5Y 4-12%, see §3) → structurally value-neutral-to-destructive on book; they trade near/below book *for a reason*.
- **Combined Ratio (loss+expense ratio)** — the actual underwriting-quality metric — **NOT in BQ**. Cannot build the real insurance framework; P/B+ROE is a crude proxy only.
- **Embedded Value (EV)** for life (BVH) — **not capturable** (not in BQ, and BVH's P/B premium is an EV bet we can't model).
- **ROIC is meaningless** for insurers (investment float leverage) — BQ ROIC5Y prints negative/garbage for all names; ignore.
- **Investment return on float**: not isolable in BQ.

## 3. BQ backlook (2014→2026, annual avg)
- **BVH**: P/B 1.4–4.1 (premium, EV story), ROE5Y only 4–9% (worst quality), PE 17–54. P/B<1.5 only since 2023. **Never passes a 12% ROE floor.** Liquid but a low-ROE life insurer at a premium = uncapturable EV bet.
- **PVI**: cheapest book (0.66–2.2), ROE 2.4%→12% (rising), had real DY 3–5% in 2014–17 then dried to ~0. Best "value+improving" story but DY now uncapturable.
- **BMI**: cheap (0.5–1.5), ROE 3–11%, crossed ~10% only 2024+. DY ≈ 0.
- **MIG/BIC**: ROE rose into 12–15% by 2024–26 (the only names to clear the floor), but thinnest/youngest.
- **DY uncapturable** across the board (≈0 for the modern era; only PVI/BVH/BIC had small early payouts) — same DY-uncapturable rule as steel/energy/F&B.
- **No clear standalone entry window**: P/B compresses near book in drawdowns but ROE-below-COE means no book-compounding reward for waiting.

## 4. Quick screen test — P/B<1.5 + ROE5Y>12% + PE>0
| Bucket | obs | names | avg fwd-3M | winrate |
|---|---|---|---|---|
| QUALIFY | 820 | 2 | **+10.85%** | 0.74 |
| rest | 10,981 | 5 | +3.96% | 0.55 |

Looks like a strong edge — **but it is an artifact**:
- **100% OOS**: IS(2014–19) qualifying obs = **0**. The ROE5Y>12% floor *never fires* before 2024 (all insurers sub-12% ROE in-sample) → **un-walk-forward-able by construction**.
- All 820 qualifying obs are **2024–2026, only BIC + MIG** (the two thinner names), exactly when small non-life re-rated in the 2024–25 rally. The +10.85% is that single re-rate window, not a repeatable screen.
- **BVH (the only liquid name) never qualifies** → the apparent edge is uninvestable at size anyway.

## 5. Honest verdict
**Insurance = thin + structurally low-ROE; no capturable, walk-forward-valid edge.** Weak tier alongside aviation / steel / energy / pharma.
- Universe: one liquid name (BVH), and BVH is a low-ROE life insurer trading on an EV premium we can't capture / never passes a quality floor.
- The screen's headline +10.85% fwd-3M is a **2024–26 BIC/MIG re-rate artifact with ZERO in-sample support** → not deployable.
- The actual insurance quality metric (Combined Ratio) and the life-insurance value metric (EV) are both **absent from BQ** → we cannot even build the correct framework.
- Durable exports: (a) **ROIC meaningless for insurers** (float leverage) — never screen insurers on ROIC; (b) **DY-uncapturable** reconfirmed; (c) **EV/Combined-Ratio gap** = BQ structurally can't value insurers properly; (d) VN insurers sit **below COE** → near/below book is fair, not opportunity.
- **No book, no timed screen.** If anything, BVH is a buy-and-hold liquidity proxy, not an alpha source.
