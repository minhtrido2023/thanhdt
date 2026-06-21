---
name: TA-system definition (Layer 2)
description: Hệ thống chấm điểm kỹ thuật momentum-based làm lớp 2 bổ sung cho FA-system; validated trên ticker_prune 2014-2026
type: project
originSessionId: cc0496d6-7fd6-4cd3-8964-4af6fe223c99
---
**Mục đích:** Chọn thời điểm mua hợp lý sau khi FA-system đã chọn cổ phiếu tốt. Lớp 2 trong kiến trúc FA→TA→Intraday.

**Script:** `ta_score_daily.py` | **SQL:** `sql_queries/ta_daily_score.sql`

**Công thức điểm v6 (max ~184):**

Technical (max 113):
- +25 s_rsi_strong: D_RSI > 0.50
- +25 s_uptrend: Close > MA50 AND MA50 > MA200
- +20 s_volume: Volume ≥ Volume_3M_P50 × 1.3 AND Close > Close_T1
- +15 s_macd_pos: D_MACDdiff > 0
- +15 s_above_ma20: Close > MA20
- +10 s_vni_max3m: VNINDEX_RSI_Max3M > 0.65
- +8  s_fresh_high: ID_HI_3Y ≤ 5
- +5  s_rsi_max1w: D_RSI_Max1W > 0.65
- +5  s_bonus_extreme: D_RSI > 0.75
- -10 s_penalty_weak: D_RSI < 0.30

Valuation:
- +15 s_cheap_pe: PE < PE_MA5Y - 0.5×PE_SD5Y
- -15 s_expensive_pe: PE > PE_MA5Y + 1.0×PE_SD5Y

FA quality:
- +10 s_fscore_top: FSCORE ≥ 8
- +8  s_np_growth: NP_P0 > 1.5×NP_P4 AND NP_P4 > 0 (YoY growth)
- -8  s_np_decline: NP_P0 < 0.7×NP_P4 AND NP_P4 > 0 (YoY decline)

Sector tilt:
- +5  s_sector_strong: ICB sector ∈ {8 Financials/RE, 9 Tech/Telecom}
- -5  s_sector_weak: ICB sector ∈ {4 Health, 7 Utilities}

Trend confirmation [v6 add]:
- +5  s_ma50_rising: MA50 > MA50_T1
- +5  s_ma50_strong: MA50 > MA50_T1 × 1.005 (cumulative với rising)
- -5  s_ma50_falling: MA50 < MA50_T1
- -10 s_dd_deep: Close/HI_3M_T1 < 0.85 (relief rally pattern)

Earnings momentum [v6 add]:
- +8  s_np_qoq: NP_P0 > NP_P1 × 1.2 AND NP_P1 > 0 (QoQ acceleration)

**Regime gate (BẮT BUỘC):**
- BULL: VNINDEX_RSI > 0.45 AND VNINDEX_MACDdiff > 0
- NEUTRAL: VNINDEX_RSI > 0.40
- BEAR: còn lại — **bỏ qua, không có edge**

**Tier v9 (5-state regime + FA tier integration):**

State map (vnindex_5state_system.py):
- state=1 CRISIS, state=2 BEAR → skip entirely
- state=3 NEUTRAL → S/A allowed (with `_N` tag), no top tier
- state=4 BULL → all tiers including MEGA
- state=5 EX-BULL → top tiers allowed but lose10 high (be cautious)

| Tier | Condition | n | P3M | hit20 | lose10 |
|---|---|---|---|---|---|
| **MEGA** | score≥160 + state(4,5) + FA C/D | 148 | **32.8%** | **59.5%** | **4.1%** |
| S_PRO | score≥160 + state(4,5) | 477 | 21.4% | 39.4% | 13.6% |
| S_HIGH | score≥145 + state(4,5) | 2300 | 18.5% | 39.0% | 17.3% |
| S_HIGH_AB | score≥145 + state(4,5) + FA A/B | — | 8.4% | 22.6% | 19.4% (low edge!) |
| S_HIGH_N | score≥145 + state=3 NEUTRAL | 3305 | 15.3% | 32.3% | 17.7% |
| S | score≥130 + state(3,4,5) | — | 12.3% | — | — |
| A | score≥115 + state(3,4,5) | — | 10.3% | — | — |
| BEAR_skip | state(1,2) | — | 6.7% | 20.2% | 25.4% |

**FA tier × momentum is INVERSE:**
- FA A/B (compounders) underperform momentum trades — already priced in
- FA C/D (recovery/junk-rally) outperform — best edge in S145+ pool

**Liquidity floor:** Volume_3M_P50 × Close ≥ 1B VND

**Validation results v6 (ticker prune universe, 2014-2026-01-16, BULL only):**

| Tier | n | avg P3M | hit P3M>10% | hit P3M>20% | lose <-10% |
|---|---|---|---|---|---|
| **S_PRO ≥160** | **526** | **20.34%** | **48.7%** | **37.5%** | **13.5%** |
| **S_HIGH ≥145** | 4.5k | 15.51% | 46.3% | 32.6% | 18.0% |
| S ≥130 | 21k | 12.28% | 42.5% | 28.6% | 19.5% |
| A ≥115 | 59k | 10.34% | 39.8% | 25.9% | 19.5% |
| Baseline | 1.39M | 4.5% | 29.5% | 17.0% | 22.0% |

v6 vs v5 (BULL, comparable tiers):
- S_PRO mới 160+: P3M 20.34% vs v5 S_PRO 16.24% (+4.1pp), hit20 37.5% vs 33% (+4.5pp), lose10 13.5% vs 15% (-1.5pp)
- S_HIGH 145+: P3M 15.51% vs v5 S_HIGH 12.64% (+2.9pp), hit20 32.6% vs 28.1% (+4.5pp)
- v6 amplifies further in bull years (2020 +25pp edge tại S160+, 2016 +19pp, 2025 +13pp)
- v6 still fails 2022/2023 (-11pp, -1pp) — same regime issue.

**Why momentum-based not mean-reversion:**
Per-factor decomp ban đầu cho thấy *các nhân tố phải lý "mua đáy" đều có edge âm hoặc 0*:
- Position (Close/C_L1M ∈ [1.00, 1.06] near 1M low): edge **-1.1% / -4.6pp** ❌
- Reversal (RSI bounce from oversold): edge ~0
- Bonus_bottom (CMB peak < -0.3): edge -1.7%
Trong khi các nhân tố momentum/strength đều có edge dương:
- Overbought RSI>0.75: edge **+4.0% / +8.1pp** ⭐⭐⭐
- Uptrend MA50>MA200: edge +2.1% / +3.5pp ⭐⭐
- Volume green confirm: edge +1.0% / +2.8pp ⭐
- Strong RSI 0.5-0.75: edge +1.0% / +2.2pp ⭐

→ TTCK Việt Nam là momentum market trong giai đoạn này — mua mạnh thắng, mua đáy thua.

**Year stability v3 (S_110+ BULL vs baseline edge):**
- 2015-2020, 2024-2025: edge +1.95 đến +9.92 (10/12 năm dương)
- 2014: edge -2.09 (mild)
- **2022 (-9.10), 2023 (-6.02): edge âm mạnh — không thể fix bằng signal-level**
- Đây là regime-shift năm, momentum signals luôn fire TRƯỚC khi trend đảo chiều
- **Production fix:** layer với `vnindex_5state_system.py` — chỉ trade khi state ∈ {NEUTRAL, BULL, EX-BULL}, skip CRISIS/BEAR

**Marginal factor analysis (within A_90+, V2 → v3):**
- ⭐ Cheap_PE (PE < MA5Y - 0.5SD): +2.89% edge → +15 pts
- ⭐ FreshHigh_3Y (ID_HI_3Y ≤ 5): +4.58% edge nhưng n nhỏ (596) → +8 pts
- ⭐ VNI_max3M_high (RSI_Max3M > 0.65): +2.70% edge → +10 pts
- ⭐ RSI_max1W_high (> 0.65): +1.78% edge → +5 pts
- ❌ Expensive_PE (PE > MA5Y + 1SD): -5.50% edge → -15 pts
- ❌ Liquidity floor TUY có edge âm trong backtest (large-cap underperforms small-cap) NHƯNG cần để trade live (slippage); chỉ dùng làm filter, không trừ score

**Why:** FA-system trả lời "cổ phiếu nào", TA-system trả lời "ngày nào nên mua". Combined với regime gate, hệ thống có edge thống kê đủ lớn (37% hit P3M>10% vs baseline 30%).

**How to apply:**
- Chạy `python ta_score_daily.py` mỗi ngày sau 14:45
- Chỉ trade khi regime ≠ BEAR; production: layer với 5-state system để skip CRISIS/BEAR/2022-style
- Watchlist: tier S_HIGH/S/A (score ≥ 95) + liquidity ≥ 1B VND
- Cross-reference với FA tier A/B trước khi vào lệnh
- Layer 3 (intraday VWAP/volume) dùng để tinh chỉnh thời điểm đặt lệnh trong phiên hôm sau

**Refinement round 2 findings (đã test, không adopt vào score):**
- **Universe:** prune (449 mã) > full (1272 mã) — full diluted P3M -1.9pp; giữ prune
- **Holding period:** edge directional ổn định ~40% hit ở mọi horizon; tốc độ %/ngày cao nhất 2 tuần đầu (0.28%/d), decay xuống 0.17%/d ở 3M
- **Interaction Cheap_PE × FreshHigh:** P3M 17.16% nhưng bull-year bias (mạnh 2017/2020/2021, âm 2018/2019/2023/2025) — KHÔNG add
- **Extension penalty (RSI>0.90, etc):** trade-off đều, **chuyển thành WARN flags** trong watchlist

**Refinement round 3 findings (v5):**
- **Sector tilt (ICB top digit):** Sector 8 (Financials/RE) edge **+7.25pp**, sector 9 (Tech) +6.95; sector 4 (Health) +1.4, sector 7 (Utilities) +0.95 (yếu) → adopt ±5
- **FA fundamentals:**
  - **FSCORE ≥ 8 (Piotroski top):** P3M 13.0% vs 9.82%, lose10 16.3% vs 19.4% — best risk-adjusted, adopt +10
  - **NP_growth (P0 > 1.5×P4):** adopt +8 / **NP_decline (P0 < 0.7×P4):** adopt -8
  - **Counter-intuitive:** ROE5Y > 0.20 (high quality steady) UNDERPERFORMS in S_110+ (P3M 7.2% vs 11.0%) — momentum favors mid-quality stocks. Don't add ROE/ROIC bonuses

**Refinement round 4 findings (v6):**
- **MA50 slope (trend confirmation):** MA50 rising P3M 10.61 vs 8.14 (+2.5pp), MA50 strong rising (>0.5%/d) P3M **11.81%, hit20 30.9%**, MA50 falling P3M 7.66 (xấu) → adopt +5/+5/-5
- **Drawdown filter:** Close/HI_3M_T1 < 0.85 (relief rally pattern) P3M 5.04, lose10 **31%** ❌ → adopt -10
- **Earnings momentum QoQ (NP_P0 > 1.2×NP_P1):** P3M **11.74%, hit10 42.0%** ⭐⭐ → adopt +8 (vs adoption của np_accel_3q nhỏ hơn)
- **RSI multi-timeframe (rising/falling vs T1W):** edge ZERO/negative trong S_110+ pool (RSI rising P3M 10.22 vs 10.56 — counter-intuitive). Stocks trong pool đã RSI > 0.50 rồi, "rising further" không có thêm edge → KHÔNG adopt
- **NPM_high > 15%:** edge zero trong pool (counter-intuitive vẫn) → KHÔNG adopt
- **Revenue_YoY/GPM:** không có trong `ticker` table (chỉ ở `ticker_financial`) — skip

**Round 4 net impact:** v6 S_PRO 160+ đạt P3M **20.34%, hit20 37.5%, lose10 13.5%** — best risk-adjusted tier. v6 S_HIGH 145+ vẫn có 4.5k signals (sample đủ tin cậy).

**Refinement round 5 findings (đã test, ĐA SỐ KHÔNG adopt):**
- **#1 Financial cross-join (Revenue_YoY/GPM/CF):** 
  - cf_oa_neg (5Y < 0): P3M 22.5% (counter-intuitive — junk rally trong S145+ pool)
  - rev_yoy_decline outperforms rev_yoy_strong (cũng counter-intuitive)
  - **Không stable theo năm** — fragile, không adopt
- **#3 Market cap (liquidity tier):**
  - liq_high (5-10B VND/ngày): P3M 19.81%, hit20 42.5% nhìn hấp dẫn
  - **2020 dominated** (116/475 samples = 24%); 2015/2018/2022 âm
  - liq_top (>10B large caps): P3M chỉ 10.78% trong S145+ — large caps slower momentum
  - Không adopt như score factor; chỉ note: avoid large-cap-only watchlist
- **#4 Seasonality (Dec/Tet):**
  - mo_dec: P3M 30.87%, hit20 47.4%, lose10 7.3% — *trông* siêu mạnh
  - **267/369 (72%) là 2020** — bull bias hoàn toàn. KHÔNG real edge
  - mo_jan_feb_tet: -5.5pp âm trong aggregate, nhưng cũng không stable
- **#2 Industry-relative (RSI vs sector median):**
  - S130+ pool hầu hết đã là sector leader (n=17387 leaders vs 224 laggards)
  - Redundant — score đã capture sector strength
- **#6 5-state BULL_strong regime overlay:** ✓ ADOPT
  - BULL_strong = VNI_RSI > 0.55 + MACDdiff > 0 + RSI_MinT3 > 0.45
  - S_PRO (160+) BULL_strong: P3M **21.36%** vs BULL 20.34% (+1pp), hit20 +1.9pp
  - S_HIGH (145+) BULL_strong: P3M 16.02% vs BULL 15.51% (+0.5pp)
  - Marginal nhưng real, **adopt làm regime-conditional gating**

**Tổng kết Round 5:** Đa số directions thử nghiệm đều thất bại year-stability test. Chỉ BULL_strong regime gate có edge real. v7 = v6 + regime-conditional tiering.

**Refinement round 6 (v8 + v9):**

**v8 — FA tier integration (Hướng C):**
- Upload `fundamental_rating_all.csv` → BQ table `tav2_bq.fa_ratings` (11k rows, 2014-2026)
- **Phát hiện:** FA tier × momentum INVERSE
  - FA A (best fundamentals) trong S145+ BULL: P3M only 8.6%, hit20 22.7% (steady compounders, momentum already priced in)
  - FA D (poor fundamentals) trong S145+ BULL: P3M **21.75%**, hit20 41% (junk rally / recovery)
  - FA C (sweet spot risk-adjusted): P3M 14.99%, lose10 chỉ 15.5%
- ELITE tier: S160+ BULL_strong + FA C/D → P3M **25.0%**, hit20 51.7%, lose10 7.4%

**v9 — 5-state regime overlay (Hướng A):**
- Modified `vnindex_5state_system.py` to dump `vnindex_5state_history.csv`
- Upload to BQ table `tav2_bq.vnindex_5state` (6.3k rows from 2000)
- **Phát hiện:** 5-state state=4 (BULL) > heuristic BULL_strong (+3.9pp P3M)
  - State 4 alone: P3M 19.88%, hit20 41.9%, lose10 14.0% ⭐
  - State 5 EX-BULL: P3M 15.13%, lose10 25.1% (blow-off risk!)
  - State 1,2 (CRISIS/BEAR): P3M 6.68%, lose10 25.4% — skip entirely
- **MEGA-ELITE: S160+ + state(4,5) + FA C/D**: P3M **32.8%, hit20 59.5%, lose10 4.1%** ⭐⭐⭐
- **5-state correctly avoids 2022/2023** — n=0 state=4 BULL during these years (regime detection works!)

**Layer 2 final architecture (v9):**

```
TA Score (max ~184) → Bucket by score
        ↓
JOIN fa_ratings → fa_tier (A/B/C/D/E)
        ↓
JOIN vnindex_5state → state5 (1-5)
        ↓
Tier function: tier(score, state5, fa_tier)
        ↓
MEGA / S_PRO / S_HIGH / S_HIGH_AB / S / A / B / ...
```

**Final result:** v9 MEGA tier đạt P3M 32.8% với lose10 4.1% — risk-adjusted return tăng 8× so với baseline (4.5% / 22%).
