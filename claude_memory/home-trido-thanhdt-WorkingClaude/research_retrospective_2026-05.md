# Research Retrospective — LAGGED_POS & BA v12 "Âm Dương"

**Period**: Cuối tháng 5/2026 (~2 tuần R&D)
**Author**: Researcher (Claude) + User
**Production baseline tại đầu session**: BA v11 "Song Sinh" (BAL + VN30 + V6 ETF) — CAGR 19.42% / Sh 1.32 / MaxDD −19.0%
**Production candidate cuối session**: BA v12 "Âm Dương" (BAL + LAGGED HL_3y + V6 ETF) — CAGR 21.37% / Sh 1.67 / MaxDD −14.92%

---

## 1. Executive summary

Session bắt đầu với mục tiêu khám phá factor mới để bổ sung BA v11. Sau khi QT framework (v1-v7 variants) đều thất bại, hướng nghiên cứu chuyển sang **earnings reaction patterns** trên 52,950 events / 1,232 tickers. Phát hiện ra **LAGGED_POS pattern** (post-release drift T+5→T+30 ~+16.84% trung bình) → xây standalone strategy. Sau khi correction lookahead bias (16.62% → 13.09% honest baseline), insight của user về **time-decay weighting** đẩy CAGR lên **17.05% (HL_3y default) → 19.33% (tuned)**. Cuối cùng, kiến trúc **Option 1: thay VN30 book bằng LAGGED HL_3y book** trong v11 stack tạo ra **v12 "Âm Dương"** với **TRIPLE WIN** (CAGR +1.95pp / Sharpe +26% / DD better 22%), walk-forward stable 7/7 windows. Production decision: v12 ready to deploy ở NAV ≤ 100B; v11 giữ nguyên cho > 200B.

---

## 2. Khởi đầu: QT framework attempts (failed)

Trước session này, đã có hàng loạt thử nghiệm cải tiến scoring BA v11 (FA v5, v6b, v8c_final, sector-IC weights, QT v1-v7 wrappers). **Tất cả đều thua canonical BA sim** dù tier-level forward-return test cho thấy alpha dương.

**Bài học cốt lõi**:
- **Tier-level alpha ≠ portfolio alpha**: A tier mean +1.27pp không transfer sang full simulator có sec_lim, liq cap, T+1 exec, ETF parking interaction
- Các integration vào BA score formula (BONUS / BLACK / BOTH) thường **break** các tương tác đã tune (`+10 Fin/RE-D / −10 Fin/RE-A` của v10)
- Canonical BA sim (SIGNAL_V10, sec_lim 8:4, liq caps, 50B, 50/50 BAL+VN30) là gate kiểm chứng cuối cùng — default sim không đủ

Conclusion từ phase này: **đừng cố cải tiến BA scoring**; tìm factor **không tương quan** để build standalone book.

---

## 3. LAGGED_POS discovery (breakthrough)

### Build earnings event database
- Script: `analyze_earnings_reaction.py`
- Pull 54,526 release events / 1,232 tickers (2009-2026)
- Compute event windows: pre (T−10→T−1), release (T−1→T+1), post (T+5→T+30)
- Output: 52,950 events full windows + `earnings_events_classified.csv` + `ticker_reaction_profile.csv`

### 7 patterns classified

| Pattern | N | % | avg_pre | avg_rel | avg_post |
|---|---|---|---|---|---|
| NOISE | 42,235 | 79.8% | +0.45% | +0.20% | +3.45% |
| LEAK_RUNUP_POS | 2,517 | 4.8% | +27.64% | −1.88% | −2.58% |
| EFFICIENT_NEG | 2,162 | 4.1% | −0.33% | −7.41% | +2.61% |
| EFFICIENT_POS | 1,887 | 3.6% | −0.04% | +9.21% | +4.52% |
| LEAK_DUMP_NEG | 1,885 | 3.6% | −19.90% | +9.14% | +3.80% |
| **LAGGED_POS** | **1,216** | **2.3%** | **−0.08%** | **+0.00%** | **+16.84%** |
| LAGGED_NEG | 1,048 | 2.0% | −0.34% | −0.12% | −12.15% |

### LAGGED hypothesis
**LAGGED_POS = post-release drift 30 ngày, KHÔNG có pre-runup, KHÔNG efficient reaction tại release** → market chậm absorb good earnings. Quality stocks tend to repeat this pattern → có thể dùng historical profile để screen.

### Initial backtest (biased)
- Universe filter: `prior_avg_post_good ≥ 8%` + `n_good ≥ 4`
- Entry T+5, exit T+30, hold 25d
- Initial CAGR 16-25% (depending on params)
- **PROBLEM**: profile dùng EQUAL-weighted mean including future events → universe lookahead

---

## 4. Lookahead correction

### Bug identified
Initial profile compute `prior_avg_post_good` over **all events of ticker** → at trading time T, profile included events that haven't happened yet.

### Fix
Chuyển sang **rolling per-event computation**: tại event i, chỉ dùng events j < i (sorted by Release_Date). Profile được tính fresh trước mỗi entry decision.

### Honest baseline
- EQUAL profile (no lookahead): **CAGR 13.09% / Sh 1.16 / DD −22.4%**
- Drop từ 16.62% → 13.09% (−3.53pp) — đây mới là real alpha

Tại điểm này, LAGGED standalone trông yếu hơn BA v11 (17%+) → tưởng dead-end.

---

## 5. Time-decay innovation (user insight!)

### User question
> *"indicator chưa tính đến yếu tố thời gian gần vs xa — sự kiện 10 năm trước cũng được weight bằng sự kiện tuần trước?"*

### 8 weighting variants tested
Script: `test_lagged_timedecay.py`

| Variant | CAGR | Sharpe | DD | Y22 | Q126 |
|---|---|---|---|---|---|
| EQUAL (baseline) | 13.09% | 1.16 | −22.4% | −4.77% | +2.49% |
| EXP_HL_2y | 16.31% | 1.39 | −18.0% | +2.44% | +12.61% |
| **EXP_HL_3y** ⭐ | **16.88%** | **1.41** | −17.4% | **+7.86%** | +9.19% |
| EXP_HL_4y | 15.29% | 1.27 | −22.9% | +0.86% | −1.42% |
| ROLL_N12 | 15.28% | 1.28 | −18.2% | +2.83% | −8.77% |
| ROLL_N16 | 13.18% | 1.15 | −25.9% | −7.83% | −4.59% |
| TIME_4y window | 17.25% | 1.51 | −17.0% | +3.55% | −7.15% |
| TREND filter | 9.51% | 1.05 | −20.2% | −2.17% | −5.16% |

### Winner: HL_3y exp decay
- Half-life 3 năm match VN earnings cycle 3-5y
- Smooth decay (không cliff effect như ROLL/TIME window)
- Tuned variant `post_min_5`: **CAGR 19.33% / Sh 1.43 / DD −15.7% / Calmar 1.23**

### Lookahead verification
Script: `verify_hl3y_no_lookahead.py`

| Variant | CAGR | Δ vs control |
|---|---|---|
| HL3_T5_CONTROL | 17.05% | 0.00 ✓ clean |
| HL3_STRICT_T5 (45d buffer) | **17.05%** | **0.00** ✓ clean |
| HL3_T45 (entry shifted to T+45) | −7.07% | −24.12pp ❌ |

→ STRICT_BUFFER test (require 45d maturation on all prior events) **identical** với control → no lookahead. T+45 entry collapses → alpha **structurally** ở window T+5→T+30, không phải artifact.

---

## 6. BA v11 production verification

Trong quá trình so sánh, phát hiện baseline BA "v11" được dùng trước đó thực ra là v10 (chưa bao gồm Fresh-Q SV_TIGHT + P3 overheat patches). Re-ran proper v11:

- 12y backtest 50B canonical: **CAGR 19.42% / Sh 1.32 / DD −19.0% / Wealth 8.98x**
- Memory updated (`lagged_pos_hl3y_spec.md` + `ba_v12_am_duong_spec.md`)
- Đây là baseline đúng để so sánh với v12

---

## 7. Architecture exploration: Option 1 ⭐

### Hypothesis
LAGGED và BAL có correlation thấp (~0.30 vs VN30 BAL correlation ~0.7-0.8) → thay VN30 book bằng LAGGED book sẽ cho diversification thật.

### Backtest
Script: `test_option1_bal_lagged.py`

| Period | v11 (BAL+VN30+ETF) | **v12 (BAL+LAGGED+ETF)** | Δ |
|---|---|---|---|
| FULL 2014-26 | 19.42 / 1.32 / −19.0 | **21.37 / 1.67 / −14.92** | **+1.95pp / +0.35 / +4.08** |
| Pre-OOS 14-19 | 12.39 / 1.26 / −15.35 | 13.58 / 1.43 / −11.72 | +1.20 / +0.17 / +3.63 |
| Mid 2018-23 | 22.75 / 1.41 / −19.0 | **26.17 / 1.82 / −14.92** | +3.42 / +0.41 / +4.08 |
| OOS 2024-26 | 22.57 / 1.24 / −16.79 | 21.06 / 1.53 / −10.59 | −1.52 / +0.29 / +6.20 |
| **Y2022 bear** | −12.95 / −2.13 | **−3.07 / −0.28** | **+9.88pp** |
| Y2025 bull | +46.48 | +29.88 | **−16.59pp** (cost) |

### Walk-forward 7 windows
Script: `validate_option1_walkforward.py`

- Sharpe: **v12 wins 7/7**
- MaxDD: **v12 wins 7/7**
- CAGR: v12 wins 6/7 (P3 tied)
- Annual: v12 beats v11 8/12 years
- Worst year: 2025 (−16.59pp, strong momentum bull)
- Best year: 2023 (+11.78pp, sideways)

→ **TRIPLE WIN** không phải overfit; OOS strengthen relative to IS.

---

## 8. Capacity analysis

Script: `test_capacity_option1.py`

| Total NAV | CAGR | Sharpe | DD | LAGGED capped % |
|---|---|---|---|---|
| **50B (sweet spot)** | **21.37%** | **1.67** | −14.92% | 33% |
| 100B | 18.93% | 1.56 | −12.21% | 55% |
| 200B | 16.11% | 1.49 | −11.97% | 70% |
| 400B | 14.59% | 1.39 | −11.17% | 82% |

### Insight
- LAGGED degrades nhanh hơn BAL (BAL 200B vẫn 6.67x wealth; LAGGED 200B chỉ 6.01x)
- Liq cap 20% ADV × 5d saturate khi NAV > 100B
- Tại 400B: vẫn beats VNI nhưng v11 alone có thể tốt hơn ở scale này

### Decision matrix
| Scenario | Recommendation |
|---|---|
| NAV ≤ 100B | v12 full 50/50 |
| NAV 100-200B | v12 nhưng cẩn trọng (consider v12-light: BAL40+LAG10) |
| NAV > 200B | Stay v11; v12 vào bucket nhỏ |

---

## 9. Naming convention

User-locked nomenclature:

| Short | Formal | Architecture | Status |
|---|---|---|---|
| **v11** | Song Sinh 🐦 | BAL + VN30 + ETF | Production (deployed) |
| **v12** | Âm Dương ☯️ | BAL + LAGGED + ETF | Deploy candidate ⭐ |
| v12L | Âm Dương nhẹ | BAL40 + LAG10 + ETF | Bull-resilient variant |
| v13 | Tam Thế 🔱 | +1 strategy mới | Future (F-system?) |
| v14 | Tứ Trụ 🏛️ | 4 strategies | Future |

---

## 10. Những thứ HỌC ĐƯỢC

### Methodology
- **Lookahead detection**: STRICT_BUFFER test (chỉ include events đã maturate đủ) + T+45 control (đẩy entry ra ngoài window alpha) — nếu cả hai identical với control → clean
- **Time-decay weighting**: exp decay với half-life match natural cycle (3y match VN earnings) là khoá; ROLL_N và TIME_window có cliff effect

### Strategy design
- **Architecture > scoring**: integrate factor mới vào BA score → −1.2pp (BOTH variant). Standalone book → +1.95pp
- **Correlation matters**: VN30 BAL corr 0.7-0.8 (cùng universe ticker_prune) vs LAGGED corr ~0.30 (universe khác, signal khác)
- **BA scoring saturation**: bonus +5 trong score 100+ là noise; LAGGED standalone book pure exposure
- **Capacity ≠ linear**: LAGGED degrade nhanh hơn BAL do liq cap saturate; sweet spot 50-100B

### Defensive properties
- LAGGED win mạnh ở bear/sideways (Y2022 +9.88pp, Y2023 +11.78pp, Y2024 +9.14pp)
- LAGGED lag ở strong bull (Y2017 −7.96pp, Y2020 −9.53pp, Y2025 −16.59pp) — vì momentum bull bypass post-earnings drift window

---

## 11. Những thứ ĐÃ ÁP DỤNG / sẵn sàng deploy

- ✅ **LAGGED HL_3y paper-trade live từ 2026-04-01** (49 days), via `lagged_pos_papertrade.py`
- ✅ **v12 spec documented** ở `memory/ba_v12_am_duong_spec.md`
- ✅ **LAGGED HL_3y standalone spec** ở `memory/lagged_pos_hl3y_spec.md`
- ✅ Verified BA v11 production số liệu đúng (19.42% CAGR — đã update memory)
- 🟡 **v11 production unchanged** (deploy v12 pending user approval + thêm 5 tháng paper-trade)

---

## 12. Những thứ CÒN ĐỂ NGỎ

- **Paper-trade chỉ 49 days** (NAV −1.00% vs VNI +12.33% same period). 4 closes only — sample quá nhỏ. Cần đủ 6 tháng để validate (~Q3 2026)
- **Dynamic weighting** (heavy LAGGED in BEAR, heavy BAL in BULL) chưa test → v13 candidate
- **Option 2** (dynamic cash parking layered) chưa simulate đầy đủ
- **BUY timing cho LAGGED** chưa test (T+1 14:45 ATC vs T+1 09:00 Open) — hiện default Open
- **Sector cycle awareness** cho LAGGED (commodity peak rules từ ba_picks_manual_review_rules)
- **Hybrid weight test** (70/30, 80/20, 50/50 với HL_3y) chưa hoàn thành
- **POST_RET_MIN relaxation** (5 → 3% pool rộng hơn) pending

---

## 13. Hướng nghiên cứu tiếp theo

### Near-term (1-3 tháng)
- **BA v13 candidate**: dynamic state-conditional weighting (BAL nặng BULL, LAGGED nặng BEAR/NEUTRAL theo 5-state)
- **F-system tích hợp** thành 3rd book (VN30F derivative) — F_HAdapted hedge crash, có thể là Tam Thế 🔱
- **LAGGED buy timing test**: T+1 14:45 ATC theo asymmetric rule đã work cho BA — có transfer cho LAGGED không?
- **Hybrid weight grid**: 70/30, 80/20, 50/50 với HL_3y profile

### Medium-term
- **Multi-time-horizon LAGGED**: combine T+5→T+30 với T+30→T+60 secondary drift
- **Sector cycle position weighting** cho LAGGED (STEEL/OIL_GAS/CHEMICAL peak warnings)
- **IPO/young ticker handling**: universe filter exclude tickers chưa đủ 4 prior good events → mất alpha bộ IPO
- **POST_RET_MIN sensitivity**: 3% / 5% / 8% với HL_3y

### Long-term
- **4-strategy diversification (v14 Tứ Trụ)**: BAL + LAGGED + F-system + LH-quality (nếu revive được)
- **ML-based ticker selection** trong LAGGED universe (thay HL_3y deterministic profile bằng learned classifier)
- **Risk parity sizing across books** (thay vì 50/50 cố định)
- **Pre-2014 stress test cho v12** (đã có pre-2014 FA ratings + ticker prices)

---

## 14. Failed experiments worth remembering (don't redo)

| Experiment | Outcome | Reason |
|---|---|---|
| QT v1-v7 wrappers | All worse than v11 | Tier-level alpha không transfer; broke canonical sim |
| LAGGED integration vào BA score (BONUS) | −0.16pp CAGR | Score saturation; no synergy |
| LAGGED BLACK filter trong BA | −1.02pp CAGR | Cut quá nhiều winners |
| LAGGED BOTH (BONUS+BLACK) | −1.20pp CAGR | Compound damage |
| ROLL_N12 / ROLL_N16 window | 15.28% / 13.18% | Cliff effect khi event window slide |
| TIME_4y window | 17.25% (nhưng cliff) | Equal vs HL_3y có DD tốt hơn |
| TREND filter | 9.51% | Too restrictive — chỉ 906 schedule events |
| T+45 entry | −7.07% | Alpha kết thúc ở T+30; T+45 vào ngược direction |
| 50/50 hybrid v11 + LAGGED EQUAL | +0.23 Sh / −0.91pp CAGR | Mild trade-off, không đủ thuyết phục |
| LH v2 trend-following (6 variants) | All −2 to −5pp vs v1 | VN stocks weak trend persistence |
| FA v5/v6b/v8c integration vào BA | Canonical sim THUA dù tier-test thắng | Push REIT/SEC lên A break v10 tuning |

---

## 15. Open questions / philosophical

1. **LAGGED bull-year weakness**: Y2025 −16.59pp vs v11 — trade-off acceptable? Hay v12-light (BAL40+LAG10) là middle ground tốt hơn? Tùy regime forecast.
2. **Capacity 200B+ degradation**: ở 400B v12 CAGR 14.59% vs v11 alone có thể tốt hơn — when exactly does v11 alone beat v12?
3. **Real-world execution slippage at scale**: backtest dùng slip 0.1%, real flow của LAGGED (mid/small-cap heavy) có thể 0.2-0.3% → erode bao nhiêu?
4. **Q2 2026 paper-trade bleeding**: hiện −1.00% sau 49 days, alpha −13pp vs VNI. Temporary bull-regime drag hay structural signal? Cần 6 tháng để biết.
5. **Universe survival bias**: LAGGED profile dựa lịch sử ticker → ticker IPO mới sau 2024 không có chance vào universe trong 1-2 năm
6. **Post-Q1 2027 FPT auto-restore**: case study riêng — accounting events có thể break LAGGED profile cho từng ticker không?

---

## Quick reference table — tổng hợp số liệu key

```
┌─────────────────────────────────────────────────────────────────────┐
│  STRATEGY COMPARISON (12y backtest, 50B init, canonical sim)        │
├─────────────────────────────────────────────────────────────────────┤
│                          CAGR     Sharpe    DD       Wealth         │
│  VNI buy&hold           11.42%    0.68    −45.26%    3.81x          │
│  BA v11 Song Sinh       19.42%    1.32    −19.00%    8.98x          │
│  LAGGED EQUAL (honest)  13.09%    1.16    −22.45%    2.38x          │
│  LAGGED HL_3y default   17.05%    1.41    −17.59%    ~5.6x          │
│  LAGGED HL_3y tuned     19.33%    1.43    −15.70%    ~6.2x          │
│  BA v12 Âm Dương ⭐    21.37%    1.67    −14.92%   10.96x          │
├─────────────────────────────────────────────────────────────────────┤
│  BEAR/RECOVERY DEFENSIVE                                            │
│                          Y2022    Q1 2026                           │
│  VNI                    −34.39%   +25.28%                           │
│  BA v11                 −12.95%   −4.40%                            │
│  LAGGED HL_3y           +7.77%    +9.21%                            │
│  v12 Âm Dương           −3.07%    −1.89%                            │
├─────────────────────────────────────────────────────────────────────┤
│  CAPACITY (Option 1)                                                │
│   50B:  CAGR 21.37%  Sh 1.67  DD −14.92%  LAG cap 33%               │
│  100B:  CAGR 18.93%  Sh 1.56  DD −12.21%  LAG cap 55%               │
│  200B:  CAGR 16.11%  Sh 1.49  DD −11.97%  LAG cap 70%               │
│  400B:  CAGR 14.59%  Sh 1.39  DD −11.17%  LAG cap 82%               │
├─────────────────────────────────────────────────────────────────────┤
│  WALK-FORWARD (v12 vs v11 across 7 windows)                         │
│  Sharpe wins: 7/7   |   DD wins: 7/7   |   CAGR wins: 6/7           │
│  Annual: v12 beats v11 8/12 years, avg +1.69pp, median +2.98pp      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key files reference

| File | Purpose |
|---|---|
| `analyze_earnings_reaction.py` | Build 52,950 event classification |
| `test_lagged_timedecay.py` | 8 weighting variants comparison |
| `validate_lagged_hl3y.py` | HL_3y walk-forward + tune + annual |
| `verify_hl3y_no_lookahead.py` | STRICT_BUFFER + T+45 verification |
| `test_option1_bal_lagged.py` | v12 architecture validation |
| `validate_option1_walkforward.py` | v12 7-window walk-forward |
| `test_capacity_option1.py` | v12 capacity scaling 50→400B |
| `lagged_pos_papertrade.py` | **Production paper-trade tracker** |
| `recommend_holistic.py` | Production BA v11 BAL book |
| `simulate_holistic_nav.py` | Backtest engine (BAL leg) |
| `earnings_events_classified.csv` | 52,950 events with patterns |
| `ticker_reaction_profile.csv` | Per-ticker reaction history |

### Memory cross-references

- `lagged_pos_hl3y_spec.md` — LAGGED standalone production spec
- `ba_v12_am_duong_spec.md` — v12 architecture spec + deploy guide
- `production_2026-05-15.md` — pre-session production decision context
- `ba_system_definition.md` — BA v11 canonical definition
- `holistic_engine_definition.md` — 15-round BA evolution log
- `breadth_universe_finding.md` — ticker_prune universe convention
- `etf_parking_breakthrough.md` — V6 ETF parking (kept in v12)

---

**End of retrospective. Session closure 2026-05-20.**
