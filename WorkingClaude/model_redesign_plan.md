# Hyperopt Model Redesign — Kế hoạch Toàn diện

> Document tổng hợp các vấn đề phát hiện được trong hệ thống hyperopt hiện tại và đề xuất kiến trúc mới với roadmap implementation chi tiết.

---

## Tóm tắt Executive

### Tình trạng hiện tại
Hệ thống đang dùng kiến trúc:
1. **Pattern-based hyperopt**: Mỗi pattern hyperopt độc lập trên dữ liệu 2014–2024
2. **Loss function**: `loss = si_return * 1.5 + win_deal * 0.5` (mua), `loss = số_deal * median_profit_2M` (bán)
3. **Ranking**: `ranking_point = 0.3*si_return + 0.3*win_deal*100 + 0.15*win_quarter*100 + 0.1*win_quarter_5Y*100 + 0.05*win_month_24M*100 + 0.1*deal_count`
4. **Order_point**: tầng combine patterns, train trên cùng dữ liệu 2014–2024
5. **Market overlay**: 5-state VNINDEX system (đã fix look-ahead)

### Vấn đề lớn được phát hiện
| # | Vấn đề | Mức độ |
|---|--------|--------|
| 1 | Multi-layer overfitting (3 tầng cùng train trên 1 tập data) | Nghiêm trọng |
| 2 | Loss function path-dependent, không có risk adjustment | Cao |
| 3 | Metric count-based bị inflate do deal overlap | Cao |
| 4 | Không phân biệt được deal đi nhiều tiền vs deal đi ít tiền | Cao |
| 5 | Regime concentration bias khi single train/test split | Cao |
| 6 | Buy/sell chicken-and-egg: không biết tối ưu cái nào trước | Trung bình |
| 7 | Per-pattern hyperopt → portfolio không diversified | Trung bình |
| 8 | Indicators trong pattern coi equal weight (không tận dụng được conviction) | Trung bình |

### Kiến trúc đề xuất
**Hybrid 3-Layer Architecture**:
- **Layer 1 — Pattern Filter (Boolean)**: Patterns đóng vai trò candidacy gate, giữ interpretability
- **Layer 2 — Factor Score (Continuous)**: 8 factor families với weights được hyperopt nhẹ, quyết định position size
- **Layer 3 — Portfolio Construction**: Liquidity constraints, diversification, regime-aware allocation

### Validation Framework
- **CPCV (Combinatorial Purged Cross-Validation)** với 5-fold walk-forward (cấp độ thực tế) hoặc 165-fold (cấp độ chuyên nghiệp)
- **Regime-stratified** validation dùng 5-state system làm labeler
- **Selection by robustness**, không theo mean performance

---

## Phần 1 — Diagnosis: Điểm yếu của Hệ thống Hiện tại

### 1.1 Multi-layer Overfitting

**Vấn đề**: Hiện có 3 tầng tối ưu hóa cùng dùng dữ liệu 2014–2024:
1. Hyperopt từng buy pattern
2. Hyperopt từng sell pattern  
3. Order_point scoring

Mỗi tầng cộng dồn rủi ro overfitting. Tầng 3 đặc biệt nguy hiểm vì nó "học cách bù trừ" cho noise của các patterns đã overfit ở tầng 1+2.

**Hệ quả**: Performance in-sample đẹp, nhưng OOS sụp đáng kể (gap > 30%).

**Nguyên tắc**: Mỗi tầng optimization phải dùng tập data **độc lập** với các tầng khác.

---

### 1.2 Loss Function Path-Dependent

**Loss hiện tại**:
```
loss_buy = si_return * 1.5 + win_deal * 0.5
loss_sell = số_deal * median_profit_2M
```

**3 vấn đề cụ thể**:

#### (a) `si_return` là compound return của portfolio 2014–2024
- Path-dependent: phụ thuộc thứ tự xảy ra của events
- Hyperopt sẽ tìm ngưỡng "tình cờ" miss được crash 2018, 2022 — không vì lý do kinh tế học
- 1 con số duy nhất cho 11 năm → mất sạch thông tin về từng giai đoạn

#### (b) Không có risk adjustment
- CAGR 20% với MaxDD -50% được đánh giá ngang CAGR 15% với MaxDD -10%
- Pattern volatile được chọn vì lucky path

#### (c) Win_rate không có sample size requirement
- Pattern 5 deals thắng 4 (win_rate 80%) được chọn trên pattern 500 deals thắng 350 (win_rate 70%)
- Pattern đầu là noise, pattern sau là signal — nhưng metric không phân biệt

---

### 1.3 Ranking Point — Multiple Metrics, All In-Sample

```
ranking_point = 0.3*si_return + 0.3*win_deal*100 + 0.15*win_quarter*100 
              + 0.1*win_quarter_5Y*100 + 0.05*win_month_24M*100 + 0.1*deal_count
```

**Vấn đề**:
- 5 metric khác nhau nhưng cùng đo trên 1 giai đoạn 2014–2024 → không tăng robustness, chỉ tăng cơ hội tìm ra ngẫu nhiên pattern phù hợp
- `deal_count` ở metric khuyến khích hyperopt tạo patterns "nhạy" → nhiều false positives
- Trọng số (0.3, 0.3, 0.15, 0.1, 0.05, 0.1) là arbitrary, không có cơ sở

---

### 1.4 Deal Overlap Inflate Metrics

Quan sát từ `profile_hit.csv`: cùng AAA, cùng ngày 2014-08-05, **4 patterns khác nhau** (SuperGrowth, BullDvg, BuySupport, SurpriseEarning) đều ra tín hiệu mua.

**Hệ quả**:
- Deal count bị overcount × số patterns trùng
- Win/loss statistics correlated, không independent
- Portfolio simulation: nếu tất cả mua → concentrated 1 cổ phiếu; nếu chọn 1 → bias

---

### 1.5 Capital Deployment Blind Spot

**Pattern A**: 100 deals, mỗi deal chỉ deploy được 50M VND (small-cap illiquid), profit 30%
- Tổng profit thực: 100 × 50M × 30% = **1.5B**

**Pattern B**: 30 deals, mỗi deal deploy được 2B VND (large/mid-cap), profit 20%
- Tổng profit thực: 30 × 2B × 20% = **12B**

`win_rate` và `median_profit` của Pattern A đẹp hơn → ranking_point chọn A.
**Thực tế**: Pattern B mang lại 8× lợi nhuận thực.

**Nguyên nhân**: Mọi metric hiện tại đo theo **count of deals**, không theo **VND deployed**.

---

### 1.6 Regime Concentration Bias

**Vấn đề khi single train/test split (vd train 2014–2019)**:
- Thiếu CRISIS (COVID 2020)
- Thiếu EX-BULL (2021)
- Thiếu BEAR sâu (banking crisis 2022)

→ Patterns optimize cho regime calm → sụp khi gặp regime extreme.

---

### 1.7 Equal-Weight Indicators trong Pattern

Pattern hiện tại định nghĩa boolean: `(RSI < 0.3) & (Volume > X) & (PE < Y)` — mỗi indicator coi như có trọng số bằng nhau, chỉ quan tâm pass/fail ngưỡng.

**Hạn chế**:
- Mất thông tin về độ mạnh tín hiệu (RSI = 0.05 vs 0.29 đều pass nhưng độ tin cậy khác)
- Không có conviction sizing: deal nào cũng cùng position size
- Cliff effect tại ngưỡng filter

---

## Phần 2 — Nền tảng: Data Split & Validation Framework

### 2.1 Tại sao standard train/test fails

Phương pháp truyền thống (train 80%, test 20% cuối) có 3 vấn đề:
1. **Regime concentration**: Test chỉ cover 1 giai đoạn (2023–2024 = recovery)
2. **Single point estimate**: 1 con số performance, không có uncertainty
3. **Inability to detect overfit**: Pattern lucky vs robust trông giống nhau

### 2.2 Combinatorial Purged Cross-Validation (CPCV)

**Cấp độ 1 — Practical (5-fold walk-forward)**:
```
Fold | Train          | Validate (regime quan trọng)
-----|----------------|------------------------------
  1  | 2014→2018      | 2019-2020  [COVID CRISIS + recovery]
  2  | 2014→2019(-6M) | 2020-2021  [CRISIS + EX-BULL]
  3  | 2014→2020(-6M) | 2021-2022  [EX-BULL + banking BEAR]
  4  | 2014→2021(-6M) | 2022-2023  [BEAR sâu + recovery]
  5  | 2014→2022(-6M) | 2023-2024  [NEUTRAL + BULL]

TEST cuối: 2025-nay (KHÓA tuyệt đối)
```

`(-6M)` = purged gap: bỏ 6 tháng cuối train để tránh deals overlap sang validate (vì holding period có thể đến 1Y).

**Cấp độ 2 — Professional (CPCV với 165 folds)**:
- Chia 2014–2024 thành 11 blocks (1 năm/block)
- Chọn k=3 blocks làm test → C(11,3) = 165 fold
- Mỗi fold purge 6 tháng quanh test blocks
- Aggregate metrics → có **distribution** thay vì 1 con số

### 2.3 Regime Stratification (bắt buộc)

Dùng **5-state system** làm regime labeler. Validate mỗi fold:

```python
for fold in folds:
    train_regime = count_states(fold.train)
    test_regime = count_states(fold.test)
    
    # Yêu cầu: mỗi regime ≥10% trong train
    assert all(pct >= 0.10 for pct in train_regime.values())
    
    # Yêu cầu: test có ≥2 regime khác nhau
    assert len([r for r in test_regime if r > 0.05]) >= 2
```

Loại bỏ folds không đạt → tránh evaluate trên degenerate cases.

### 2.4 Selection Criterion mới

**Sai (cách hiện tại)**:
```python
best_version = argmax(mean(ranking_point across folds))
```

**Đúng (robust selection)**:
```python
score = (
    0.4 * median(Calmar)              # robust hơn mean
  + 0.3 * percentile_5(Calmar)        # worst-case fold
  - 0.2 * std(Calmar) / mean(Calmar)  # consistency penalty (CV)
  + 0.1 * regime_coverage             # số regime mà version có Sharpe>0
)
```

**Diễn giải**: Pattern tốt phải vừa có Calmar median cao, vừa không tệ ở fold xấu nhất, vừa ổn định, vừa work trong nhiều regime.

### 2.5 Tại sao việc này quan trọng

Sau khi áp dụng CPCV + regime stratification + robust selection:
- Patterns "may mắn" trên IS sẽ lộ ngay (variance cao across folds)
- Confidence interval cho performance → biết được realistic expectation
- Mỗi quyết định design có **statistical evidence**, không phải gut feeling

---

## Phần 3 — Loss Function Design

### 3.1 Redesign Loss Mua

Thay vì:
```
loss = si_return * 1.5 + win_deal * 0.5
```

Dùng:
```python
loss = -median(Calmar_3Y_rolling) 
     + λ₁ * (1 - win_rate_shrunk) 
     + λ₂ * deal_correlation_penalty
     + λ₃ * max(0, turnover - 100%)
```

**Components**:

#### (a) `Calmar_3Y_rolling`
- Tính Calmar trên các cửa sổ rolling 3 năm (2014-2017, 2015-2018, ...)
- Lấy **median** thay vì mean → robust với 1-2 năm bất thường
- Risk-adjusted: phạt MaxDD → pattern stable hơn

#### (b) `win_rate_shrunk` (Bayesian shrinkage)
```python
win_rate_shrunk = (wins + 5) / (deals + 10)
```
- Pattern 5 deals thắng 4: shrunk = 9/15 = 60% (không phải 80%)
- Pattern 500 deals thắng 350: shrunk = 355/510 = 69.6% (~70%)
- Loại bỏ noise patterns nhỏ

#### (c) `deal_correlation_penalty`
- Phạt khi pattern ra nhiều signals cùng ticker trong 1 tháng
- Tránh inflate deal count

#### (d) `turnover` constraint
- Phạt nếu turnover > 100%/năm
- Tránh patterns "twitchy" tạo nhiều giao dịch không cần thiết

### 3.2 Buy/Sell Chicken-and-Egg Problem

**Vấn đề**: Để tính Calmar cho buy pattern cần có exit. Nhưng sell pattern phải hyperopt sau buy.

**Giải pháp: Two-Stage Evaluation**

#### Stage 1 — Pattern Quality Filter (không cần exit)
Dùng forward returns có sẵn trong `profile_hit.csv` (P1W, P1M, P2M, P3M, P6M):

```python
quality = (
    0.30 * median(P2M)                          # central tendency
  + 0.25 * mean(P2M) / std(P2M)                 # Sharpe-like
  + 0.20 * hit_rate_VND_weighted(P2M > 0)       # consistency
  + 0.15 * mean(P2M | regime in [BEAR,CRISIS])  # tail robustness
  + 0.10 * percentile_25(P2M)                   # downside
)
```

Patterns không pass minimum quality threshold (vd `median(P2M) < 5%` hoặc `hit_rate < 50%`) → loại bỏ ngay.

#### Stage 2 — Strategy Quality (dùng baseline exit)
Trên patterns pass Stage 1, dùng **baseline exit cố định**:

```python
exit_at = min(
    T + 60,                    # max holding 3 tháng
    trigger_trailing_stop_15%, # protect gains
    trigger_cutloss_20%        # hard stop
)
```

Run portfolio simulation → tính loss ở section 3.1.

#### Stage 3 — Sell Pattern Hyperopt (sau khi xong Stage 2)
Trên deals tạo bởi top buy patterns, hyperopt sell với loss:
```python
loss_sell = -(Calmar_smart_sell - Calmar_baseline_sell)
          + λ * std(improvement_per_regime)  # consistency across regimes
```

**Sell pattern được đánh giá là improvement vs baseline**, không phải absolute performance.

#### Stage 4 — Iterative Refinement (optional)
- Round 2: dùng v1_sell làm baseline mới, re-hyperopt buy
- Thường converge sau 2-3 rounds

### 3.3 Tại sao baseline exit hợp lý

1. **Reproducible**: Ai cũng verify được, không phụ thuộc tầng sell
2. **Không thiên vị**: Không favor buy patterns "phù hợp" với sell pattern cụ thể
3. **Đo alpha thật của entry**: Calmar phản ánh chất lượng tín hiệu mua
4. **Decoupling**: Cho phép thay sell pattern sau mà không phải làm lại buy

### 3.4 Sell Loss Function

Sell loss hiện tại `số_deal * median_profit_2M` có 2 lỗi:
1. `profit_2M` cố định không phản ánh thực tế (sell có thể trigger trước/sau 2M)
2. Sell pattern hyperopt trên universe ngẫu nhiên ≠ trên deals do buy pattern tạo ra

**Fix**:
```python
# Trên deals từ buy pattern đã chọn
loss_sell = -median(actual_profit_per_deal) 
          + λ₁ * MaxDD_per_deal
          + λ₂ * holding_period_penalty
          + λ₃ * std(profit_per_regime)
```

`actual_profit` = profit thực tế từ buy đến sell (`Sell_profit` trong profile_hit.csv), không phải profit tại horizon cố định.

---

## Phần 4 — Capital Efficiency & VND-Weighted Metrics

### 4.1 Tại sao count-based metrics fails

Đã giải thích ở Phần 1.5. Tóm tắt: với fund 50B VND, không thể deploy đầy capital vào small-caps illiquid → patterns đẹp về count nhưng portfolio impact thực tế thấp.

### 4.2 Liquidity-Constrained Position Sizing

**Trong portfolio simulation, dùng**:
```python
target_position = NAV * 0.05  # ví dụ 5% NAV mỗi deal

# Liquidity ceiling
max_by_liquidity = Trading_Value_1M_P50 * 0.10  # 10% ADV

actual_position = min(target_position, max_by_liquidity)

# Skip deal nếu deploy quá ít
if actual_position < NAV * 0.005:  # < 0.5% NAV
    skip_deal()
```

**Hệ quả tự nhiên**:
- Pattern bắt VNM, HPG, FPT (high liquidity) → deploy đầy
- Pattern bắt small-caps illiquid → bị skip hoặc undersize
- **Không cần penalty thủ công** — simulation phản ánh đúng thực tế

### 4.3 VND-Weighted Metrics

Đổi tất cả metric từ count-based sang VND-based:

| Metric cũ (sai) | Metric mới (đúng) |
|---|---|
| `win_rate = wins/deals` | `win_rate_VND = sum($_won) / sum($_invested)` |
| `median(profit_pct)` | `weighted_avg_return = sum(profit_pct × position) / sum(position)` |
| `deal_count` | `total_VND_invested` |
| `quarterly win rate` | `quarterly $-weighted return` |

### 4.4 Capital Efficiency Metric (mới)

```python
deployed_pct[t] = capital_in_positions[t] / NAV[t]

capital_efficiency = (
    0.5 * avg(deployed_pct) 
  + 0.3 * median(deployed_pct)
  + 0.2 * (1 - pct_time(deployed < 30%))
)
```

Pattern giữ NAV idle 60% thời gian sẽ bị penalty mạnh.

### 4.5 Ranking Point Redesign

Thay vì:
```
ranking_point = 0.3*si_return + 0.3*win_deal*100 + 0.15*win_quarter*100 
              + 0.1*win_quarter_5Y*100 + 0.05*win_month_24M*100 + 0.1*deal_count
```

Dùng:
```python
ranking_VND = (
    0.30 * Calmar_VND            # risk-adj return on actual deployed capital
  + 0.20 * return_VND_total      # absolute VND return
  + 0.20 * capital_efficiency    # deployment ratio
  + 0.15 * win_rate_VND          # $-weighted hit rate
  + 0.10 * worst_regime_return   # robustness across market regimes
  + 0.05 * deal_count_capped     # min sample size, capped tại N=50
)
```

`deal_count_capped = min(deal_count, 50)` — đủ statistical significance mà không reward over-trading.

### 4.6 Multi-Capital Robustness Test

Run simulation với 3 NAV size:
```python
for nav_size in [10_000_000_000, 50_000_000_000, 200_000_000_000]:
    metric[nav_size] = run_simulation(pattern, nav_size)

# Pattern phải work cả 3
loss = -(
    0.4 * metric[10B] +    # small fund
    0.4 * metric[50B] +    # medium (your size)
    0.2 * metric[200B]     # large fund test
)
```

**Insight**: Pattern bắt small-caps tốt với 10B nhưng tệ với 200B. Pattern scalable stable across sizes → ưu tiên.

### 4.7 Pattern-Level Hard Filter

Add trong pattern definition:
```python
'(Trading_Value_1M_P50 >= 1_000_000_000) & (Close >= 5000)'
```

Loại stocks penny + illiquid khỏi universe ngay từ đầu. Hyperopt không waste compute.

### 4.8 Slippage Model (production-ready)

```python
slippage_bps = 10 + 50 * (position / Trading_Value_1M_P50)
# 10% ADV → slippage = 15 bps
# 50% ADV → slippage = 35 bps
# >100% ADV → slippage > 60 bps (impractical)

actual_entry_price = signal_price * (1 + slippage_bps/10000)
actual_exit_price = signal_price * (1 - slippage_bps/10000)
```

---

## Phần 5 — Architecture: Hybrid Pattern + Score

### 5.1 Pure Pattern Architecture (hiện tại)

**Ưu**: Interpretable, low overfit per pattern
**Nhược**: Equal-weight indicators, cliff effect, mất thông tin conviction

### 5.2 Pure Score Architecture

**Ưu**: Continuous, position sizing tự nhiên, single optimization target
**Nhược**: Search space khổng lồ, multicollinearity, mất interpretability, **overfit risk cao**

### 5.3 Hybrid Architecture (đề xuất chính)

```
LAYER 1 — Pattern Filter (Boolean):
    Patterns đóng vai trò "candidacy gate"
    - Chỉ tickers pass ≥1 pattern mới được consider
    - Loại bỏ universe không liên quan
    - Giữ interpretability ("tại sao consider HPG?")

LAYER 2 — Factor Score (Continuous):
    Trên candidates, tính total_score từ 8 factor families
    - Score quyết định position size
    - Conviction-based sizing

LAYER 3 — Portfolio Construction:
    - Liquidity constraint
    - Sector/regime diversification
    - Max position = f(score, ADV, NAV)
```

**Tại sao hybrid tốt hơn cả 2 cực**:

| Aspect | Pure Pattern | Pure Score | Hybrid |
|--------|--------------|-----------|--------|
| Interpretability | Cao | Thấp | **Cao (qua Layer 1)** |
| Overfit risk | Trung bình | Cao | **Thấp (Layer 2 constrained)** |
| Position sizing | Thô | Tốt | **Tốt** |
| Universe filtering | Tốt | Phải tự xử | **Tốt (Layer 1)** |
| Search space | Lớn (per pattern) | Rất lớn | **Nhỏ (8 family weights)** |

### 5.4 Factor Families Definition

Group indicators thành 8 families. **Trong mỗi family**: dùng rank percentile cross-sectional rồi average. **KHÔNG hyperopt indicators riêng lẻ**.

```
Factor Family            | Indicators (equal-weighted within family)
-------------------------|------------------------------------------
F1. Momentum             | D_RSI, D_MACDdiff, D_MFI, C_L1M
F2. Trend                | MA20/MA50, MA50/MA200, D_CMB
F3. Volume               | Volume_1M/Volume_3M_P50, Trading_Value_*
F4. Mean-Reversion       | D_RSI_MinT3, C_L1W, distance from VAP
F5. Quality              | ROE5Y, ROIC5Y, FSCORE, IntCov_P0
F6. Value                | PE vs PE_MA5Y, PB vs PB_MA5Y, EVEB
F7. Growth               | NP_R, Revenue_YoY_P0, GPM_P0 vs P4
F8. Risk                 | Risk_Rating, Beta, Debt_Eq_P0
```

```python
def family_score(ticker, date, family_indicators):
    ranks = []
    for ind in family_indicators:
        # Cross-sectional rank: ticker đứng thứ mấy trong universe hôm nay
        rank = percentile_rank(ind[ticker, date], among=all_tickers[date])
        ranks.append(rank)
    return mean(ranks)  # 0 to 1
```

**Lợi ích then chốt**:
- Trong mỗi family chỉ 3-5 indicators → equal weight đủ tốt
- Indicators correlated trong cùng family → average robust hơn weighted sum

### 5.5 Total Score with Family Weights

```python
total_score = (
    w1 * F1_momentum  + w2 * F2_trend     + w3 * F3_volume  +
    w4 * F4_meanrev   + w5 * F5_quality   + w6 * F6_value   +
    w7 * F7_growth    + w8 * F8_risk
)

# Constraints:
sum(w_i) = 1                # weights normalize
w_i ∈ [0.05, 0.30]          # không family nào dominate (>30%) hoặc bị loại (<5%)
```

**Search space**: 8 weights with constraints → rất nhỏ. Khó overfit.

### 5.6 Regime-Conditional Weights (chống overfit qua regime)

Dùng **shrinkage** thay vì 5 vector độc lập:

```python
w_regime = α * w_global + (1-α) * w_regime_specific
α = 0.7  # 70% global, 30% regime-specific
```

**Ví dụ**:
```python
w_global       = [0.15, 0.15, 0.15, 0.10, 0.15, 0.10, 0.10, 0.10]
                # Mom  Trend Vol  MR   Qual Val  Grow Risk

w_BULL         = [0.25, 0.20, 0.15, 0.05, 0.10, 0.05, 0.15, 0.05]
                # Momentum/Trend/Growth ↑

w_CRISIS       = [0.05, 0.05, 0.05, 0.20, 0.25, 0.20, 0.05, 0.15]
                # Quality/Value/MR/Risk ↑
```

### 5.7 Score → Action Mapping

```python
if total_score >= 0.85:        # top 15% → strong buy
    target_position = 8% NAV
elif total_score >= 0.75:      # top 25% → buy
    target_position = 5% NAV
elif total_score >= 0.65:      # top 35% → small buy
    target_position = 3% NAV
elif total_score <= 0.30:      # bottom 30% → sell signal
    target_position = 0
else:
    target_position = current  # hold

# Final position sau liquidity constraint
final_position = min(target_position, 10% × ADV)
```

### 5.8 Regularization để Chống Overfit

#### Lasso/Ridge
```python
loss = -portfolio_calmar + λ * sum(w_i^2)  # Ridge
# hoặc
loss = -portfolio_calmar + λ * sum(|w_i|)  # Lasso (sparsity)
```

`λ` đủ lớn để buộc weights gần `1/8` (equal). Chỉ cho phép deviation nếu data **rất** mạnh.

#### Equal-Weight Baseline (bắt buộc)
Compare hyperopt'd model vs equal-weight (`w_i = 1/8`). Nếu không vượt baseline rõ rệt OOS → **dùng equal-weight**. Equal-weight thường khó beat trong factor investing.

---

## Phần 6 — Portfolio-Level Selection

### 6.1 Why Per-Pattern Hyperopt Independent Fails

Ngay cả khi từng pattern hyperopt'd tốt, portfolio aggregate có thể tệ vì:

1. **Correlation explosion**: Patterns convere về cùng "công thức thắng" → 15 patterns thực chất 1 pattern lặp 15 lần
2. **Regime concentration**: Mọi pattern ưu tiên BULL → portfolio không có pattern cho BEAR/CRISIS
3. **Local vs global optimum**: A có Calmar 1.5, B có 1.4 độc lập, nhưng (A+B) chỉ 1.2 trong khi (A+C) cho 1.8
4. **Mất "vai trò"**: Defensive pattern Sharpe thấp nhưng anti-correlated với bull patterns → bị loại bỏ vì metric thấp

### 6.2 Forward Stagewise Selection

```python
selected = []
candidates = top_50_from_hyperopt

# Pattern đầu tiên: best individual
selected.append(best_individual(candidates))

# Patterns 2-15: best ADDITION to existing portfolio
for i in range(2, 16):
    best_addition = None
    best_improvement = 0
    
    for candidate in candidates:
        if candidate in selected: continue
        
        new_portfolio = selected + [candidate]
        new_calmar = simulate_portfolio(new_portfolio)
        improvement = new_calmar - current_portfolio_calmar
        
        if improvement > best_improvement:
            best_improvement = improvement
            best_addition = candidate
    
    if best_addition is None or best_improvement < threshold:
        break  # thêm pattern không cải thiện → stop
    
    selected.append(best_addition)
```

**Insight**: Pattern thứ 8 không phải pattern Calmar độc lập cao thứ 8, mà là pattern **bổ sung tốt nhất** cho 7 patterns đã chọn.

### 6.3 Diversification Constraints (bắt buộc)

```python
# Correlation constraint
for i, j in combinations(selected, 2):
    deal_overlap[i,j] = (deals_i ∩ deals_j) / (deals_i ∪ deals_j)
    assert deal_overlap[i,j] < 0.4

# Regime coverage
for regime in [CRISIS, BEAR, NEUTRAL, BULL, EX-BULL]:
    n_active = sum(p.has_signals_in(regime) for p in selected)
    assert n_active >= 2

# Sector diversity
sector_concentration = max(deals_per_sector) / total_deals
assert sector_concentration < 0.35
```

### 6.4 Pattern Archetypes (định nghĩa từ đầu)

Trước khi hyperopt, định nghĩa 6-8 archetypes. Hyperopt 2-3 patterns/archetype:

| Archetype | Triết lý | Indicators chính |
|-----------|----------|-----------------|
| Momentum-Strong | Momentum mạnh, volume tăng | RSI, MACD, Volume_Max |
| Breakout | Phá kháng cự với volume | Res_1Y, Volume_3M_P90 |
| Mean-Reversion | Quá bán trong uptrend | RSI_MinT3, MA200 |
| Value-Quality | Định giá rẻ + chất lượng cao | PE, ROE5Y, FSCORE |
| Earnings-Surprise | NP tăng vọt YoY | NP_R, Revenue_YoY |
| Defensive | Low beta, dividend stable | Risk_Rating, Dividend_3Y |
| Recovery | Bounce từ đáy | C_L1M, D_CMB |
| Bottom-Fishing | Crisis recovery play | regime=CRISIS, fundamental |

Hyperopt **trong từng archetype** → patterns đa dạng tự nhiên, không converge về 1 công thức.

---

## Phần 7 — Validation Framework

### 7.1 Decile Analysis (cho score model)

Chia universe theo score thành 10 deciles. Forward return phải **monotonic**:

```
D1:  forward_2M = -3%   ✓
D2:  forward_2M = -1%   ✓
...
D9:  forward_2M = +12%  ✓
D10: forward_2M = +18%  ✓
```

Nếu không monotonic → model không có discriminative power.

### 7.2 Spread Stability

`spread = mean(D10) - mean(D1)`. Phải positive **trong từng năm**, không chỉ tổng.

### 7.3 Score Persistence Test

Tickers score cao hôm nay phải score cao tuần tới (correlation > 0.7). Score noisy → false signal.

### 7.4 Validation Pass Thresholds

| Tiêu chí | Pass threshold |
|---|---|
| Calmar OOS / Calmar IS | ≥ 60% |
| Win rate OOS - IS | Trong khoảng ±5% |
| MaxDD OOS / MaxDD IS | ≤ 1.3× |
| Số deals/năm OOS | Trong khoảng ±30% |
| Decile monotonicity | All adjacent pairs satisfied |
| Annual spread positive | ≥ 8/11 năm |

**Nếu không pass**: KHÔNG tune để pass. Phải **đơn giản hóa** (giảm patterns, tăng regularization). Pass bằng cách tune validation = đã contaminate validation.

### 7.5 Equal-Weight Baseline Comparison

Bắt buộc cho score model: hyperopt'd weights phải vượt equal-weight (`w_i = 1/8`) trên OOS với:
- Calmar improvement ≥ 15%
- Stability across folds ≥ baseline

Nếu không → dùng equal-weight.

---

## Phần 8 — Implementation Roadmap

### Phase 0: Foundation (1 tuần)
- [ ] Verify look-ahead fix trong `_quantile_pe()` thực sự work
- [ ] Build CPCV framework cơ bản (5-fold walk-forward)
- [ ] Build regime labeler dùng 5-state system
- [ ] Verify regime distribution mỗi fold

### Phase 1: Liquidity & VND-Weighted Metrics (1-2 tuần)
- [ ] Implement liquidity-constrained position sizing trong simulation
- [ ] Convert all metrics sang VND-weighted
- [ ] Add `capital_efficiency` metric
- [ ] Add hard filter `Trading_Value_1M_P50 >= 1B` ở pattern level
- [ ] Re-run existing patterns với metrics mới → so sánh ranking

### Phase 2: Loss Function & Two-Stage Evaluation (2 tuần)
- [ ] Implement Stage 1: Pattern Quality Filter (forward returns)
- [ ] Implement Stage 2: Strategy Quality (baseline exit)
- [ ] Implement Stage 3: Sell pattern hyperopt (improvement vs baseline)
- [ ] New loss function với Calmar_3Y_rolling + shrinkage + correlation penalty

### Phase 3: CPCV Validation (2 tuần)
- [ ] Re-run hyperopt cho 1-2 representative patterns trên 5-fold
- [ ] Build robust selection criterion
- [ ] So sánh: best by old method vs by new method
- [ ] Quan sát: version mới có conservative hơn không, deal count giảm không

### Phase 4: Hybrid Architecture Implementation (3-4 tuần)
- [ ] Define 8 factor families
- [ ] Implement hierarchical scoring (rank within family → mean)
- [ ] Build score → position size mapping
- [ ] Test với equal-weight (`w_i = 1/8`) trước, không hyperopt
- [ ] **Quyết định gate**: Equal-weight có alpha không? Nếu không → score-based không work

### Phase 5: Hyperopt Family Weights (2-3 tuần)
- [ ] Hyperopt 8 weights với strong regularization (Ridge λ cao)
- [ ] CPCV validation
- [ ] Compare vs equal-weight baseline OOS
- [ ] Add regime-conditional với shrinkage α=0.7

### Phase 6: Portfolio-Level Selection (2 tuần)
- [ ] Implement Forward Stagewise Selection
- [ ] Add diversification constraints (correlation, regime, sector)
- [ ] Test với top-15 patterns vs all candidates

### Phase 7: Production Readiness (2-3 tuần)
- [ ] Slippage model
- [ ] Multi-capital robustness test (10B, 50B, 200B)
- [ ] Final validation framework checks
- [ ] Documentation

### Phase 8: Test Final & Go Live (1 tuần)
- [ ] Mở test set 2025 (1 lần duy nhất)
- [ ] Verify performance đạt validation thresholds
- [ ] Nếu đạt → go live; nếu không → simplify, không tune

**Tổng thời gian**: ~16-22 tuần (4-5 tháng) cho implementation đầy đủ.

---

## Phần 9 — Common Pitfalls (Phải tránh)

### 9.1 Optimization Pitfalls

❌ **"Optimal exit" trong buy hyperopt**: Sell tại đỉnh → upper bound không thực tế, buy pattern overfit vào structure của optimal exit.

❌ **Sell pattern phức tạp khi hyperopt buy**: Buy bị "dán" vào sell, đổi sell sau performance buy sụp.

❌ **Không gate Stage 1 → Stage 2**: Waste compute cho patterns không có alpha thật.

❌ **Đánh giá sell trên universe, không trên deals từ buy**: Selection bias.

### 9.2 Validation Pitfalls

❌ **Nhìn vào TEST nhiều lần**: TEST đã thành TRAIN. Chỉ mở 1 lần duy nhất.

❌ **Tune validation để pass thresholds**: Validation đã contaminate. Phải simplify thay vì tune.

❌ **Single-point estimate**: 1 con số không có uncertainty. Dùng distribution across folds.

❌ **Mean across folds**: Robust = median + worst-case + variance, không phải mean.

### 9.3 Architecture Pitfalls

❌ **Hyperopt 100 indicator weights independently**: Search space khổng lồ, overfit chắc chắn.

❌ **Pure score model không có Layer 1**: Mất interpretability + universe filtering.

❌ **Pick top-K patterns by individual ranking**: 15 patterns trùng lặp, không diversify.

❌ **Bỏ equal-weight baseline**: Hyperopt'd model phải prove value vs equal-weight.

### 9.4 Data Pitfalls

❌ **Forward-looking columns dùng làm features**: P1W, P1M, ... chỉ là labels, không phải features.

❌ **Pattern overlap không deduplicate**: Inflated metrics.

❌ **Cross-validation không purge**: Train/test contaminate qua deals overlapping.

---

## Phần 10 — Quy tắc Vàng

1. **Càng đơn giản càng tốt**: 8 weights > 100 weights. Equal-weight thường hard-to-beat.

2. **Regularization là bạn**: Lasso/Ridge, shrinkage, equal-weight defaults — tất cả giúp giảm overfit.

3. **Pattern tốt = bổ sung cho portfolio, không phải Sharpe cao nhất**: Always think portfolio-level.

4. **Mọi metric phải VND-weighted**: Count-based metrics thiếu thực tế cho fund 50B+.

5. **Mỗi tầng optimization phải dùng data độc lập**: Không cho phép contamination.

6. **Validation by distribution, không single point**: CPCV → distribution → robust selection.

7. **Selection by worst-case, không best-case**: Robust = không bị crash trong scenario tệ nhất.

8. **Pass thresholds thay vì optimize thresholds**: Validation phải có pass/fail clear, không tune.

9. **Interpretability matters**: Hybrid architecture giữ interpretability qua Layer 1.

10. **Regime awareness everywhere**: Loss, validation, selection — đều phải condition on 5-state regime.

---

## Phần 11 — Câu hỏi đã được trả lời

### Q1: "Làm sao đánh giá performance của pattern mua khi chưa có pattern bán?"
**A**: Dùng baseline exit cố định (`min(T+60, trailing_15%, cutloss_20%)`) trong Stage 2. Sell pattern optimize sau như improvement vs baseline.

### Q2: "Làm sao tránh regime concentration khi train chỉ 2014-2019?"
**A**: CPCV với 5-fold (cấp 1) hoặc 165-fold (cấp 2). Mỗi fold cover regime khác nhau. Selection by robustness across folds.

### Q3: "Làm sao phân biệt deal đi nhiều tiền vs deal đi ít tiền?"
**A**: 
- Liquidity-constrained position sizing trong simulation
- Tất cả metric VND-weighted
- Add `capital_efficiency` metric
- Multi-capital test (10B, 50B, 200B)

### Q4: "Hyperopt từng pattern riêng lẻ có hiệu quả không?"
**A**: Có, NHƯNG phải có:
- Tầng 1 dùng pattern quality metric (forward returns), không portfolio metric
- Tầng 2 Forward Stagewise Selection chọn 15 từ 30-50 candidates
- Diversification constraints + Pattern Archetypes

### Q5: "Có nên chuyển từ pattern sang score model không?"
**A**: Hybrid tốt hơn cả 2. Layer 1 patterns (interpretability + filter), Layer 2 score (sizing). 8 factor families với equal-weight trong family + hyperopt nhẹ giữa families. Strong regularization. Equal-weight baseline bắt buộc.

---

## Phụ lục A: Mapping với Existing Codebase

### Files cần modify
- `filter.json` — Pattern definitions (Layer 1 boolean filters)
- `gen_sql.py` — Add liquidity hard filter ở SQL level
- `webui/utils.py` — `MarketEvaluation`, `BaseEval`, `AllEvaluation`, `Simulation_*` classes

### Files cần tạo mới
- `factor_families.py` — Define 8 factor families, family scoring functions
- `cpcv_framework.py` — Combinatorial Purged Cross-Validation
- `regime_labeler.py` — Wrapper around 5-state system làm labeler
- `forward_stagewise.py` — Portfolio-level pattern selection
- `validation_framework.py` — Decile analysis, spread stability, all checks
- `loss_functions_v2.py` — New loss với Calmar_3Y_rolling, VND-weighted, shrinkage

### Existing systems leverage được
- `vnindex_5state_system.py` — Regime labeling đã ready
- `state_transition_logic.py` — Explainability cho regime conditioning
- `backtest_workflow.py` — Backtest methodology đã có sẵn

---

## Phụ lục B: Metrics Reference

### Old metrics (deprecated)
```python
loss_buy = si_return * 1.5 + win_deal * 0.5
loss_sell = số_deal * median_profit_2M
ranking_point = 0.3*si_return + 0.3*win_deal*100 + 0.15*win_quarter*100 
              + 0.1*win_quarter_5Y*100 + 0.05*win_month_24M*100 + 0.1*deal_count
```

### New metrics
```python
# Stage 1 — Pattern Quality (no exit needed)
quality = (
    0.30 * median(P2M)
  + 0.25 * mean(P2M) / std(P2M)
  + 0.20 * hit_rate_VND_weighted(P2M > 0)
  + 0.15 * mean(P2M | regime in [BEAR,CRISIS])
  + 0.10 * percentile_25(P2M)
)

# Stage 2 — Buy Loss (with baseline exit)
loss_buy = (
    -median(Calmar_3Y_rolling)
  + λ₁ * (1 - win_rate_shrunk)
  + λ₂ * deal_correlation_penalty
  + λ₃ * max(0, turnover - 100%)
)

# Stage 3 — Sell Loss (improvement vs baseline)
loss_sell = (
    -(Calmar_smart_sell - Calmar_baseline_sell)
  + λ * std(improvement_per_regime)
)

# Final Ranking
ranking_VND = (
    0.30 * Calmar_VND
  + 0.20 * return_VND_total
  + 0.20 * capital_efficiency
  + 0.15 * win_rate_VND
  + 0.10 * worst_regime_return
  + 0.05 * deal_count_capped
)

# Robust Selection across CPCV folds
final_score = (
    0.4 * median(Calmar across folds)
  + 0.3 * percentile_5(Calmar)
  - 0.2 * std(Calmar) / mean(Calmar)
  + 0.1 * regime_coverage
)
```

---

## Kết luận

Hệ thống hiện tại có nền tảng tốt (data đầy đủ, indicators phong phú, market overlay 5-state đã fix look-ahead). Vấn đề chính là **kiến trúc validation và metric**. Với roadmap 4-5 tháng, có thể chuyển sang hệ thống:

- **Robust** qua CPCV thay vì single split
- **VND-aware** qua liquidity constraints + VND-weighted metrics
- **Diversified** qua hybrid architecture + Forward Stagewise Selection  
- **Generalizable** qua regime conditioning với shrinkage
- **Interpretable** qua Layer 1 patterns
- **Right-sized** qua position sizing dựa trên conviction + liquidity

**Đề xuất ưu tiên ngắn hạn (1 tháng)**:
1. CPCV 5-fold framework (Phase 0)
2. Liquidity constraints + VND-weighted metrics (Phase 1)
3. Re-run 2-3 patterns hiện tại với framework mới → đo gap IS vs OOS

Gap IS-OOS hiện tại sẽ cho biết overfitting bao nhiêu. Đây là baseline để measure improvements các phase sau.

**Quy tắc cuối cùng**: Nếu chỉ có thời gian làm 1 thứ → làm CPCV + robust selection. Mọi cải tiến khác chỉ có ý nghĩa khi có framework validation đúng.

---

# Phần 12 — Phân tích Codebase Hiện tại & Khuyến nghị Bổ sung

## 12.1 Strengths của Codebase Hiện tại

### Infrastructure tốt sẵn có (cần preserve)
- **Distributed hyperopt qua MongoDB**: `MongoTrials` với `exp_key` — scale được dễ dàng across machines
- **2-tier caching**: Redis cache cho Phase2 base buy signals + joblib memory cho deals → khi test variant filters chỉ cần re-evaluate technical extends
- **Process pool parallelism** với pathos
- **Reproducible seed** (`rstate=np.random.default_rng(42)`)
- **Cleanup hygiene**: `cleanup_stuck_jobs()` trong MongoDB

### Data infrastructure đã có (chỉ cần leverage)
- **`trading_val_median/mean`**: đã collect trong buy hyperopt (line 253-254) nhưng **không vào loss/ranking** → chỉ cần thêm vào ranking_VND
- **`utilize_percent`**: scaling parameter đã có → multi-capital test gần như free
- **`weighted_profit`** trong sell pattern (line 192): `p_trading_val_clip / trading_val_clip * 100` — đây là **VND-weighted metric đã tồn tại**, chỉ cần áp tương tự cho buy
- **`unique_ticker`**: diversity metric đã collect (line 255), chưa dùng

## 12.2 Critical Issues mới phát hiện

### Issue 1: Suboptimal use of O2W trong loss function (KHÔNG phải look-ahead)

**Correction**: Ban đầu tôi gọi đây là "look-ahead bias" — sai. Dùng O2W làm **label/target** trong loss function = supervised learning chuẩn (không phải feature input). Pattern definition không dùng O2W → không có leak ở decision logic.

**Vấn đề thực với cách implement hiện tại**:

`tuning/buy_pattern/run_tuning.py` line 334:
```python
penalty *= deal_result['O2W_deal'] * deal_result['O2W_hit']
```

1. **Multiplicative form gây instability**: O2W ratio ~1.0, swing nhỏ compound mạnh khi nhân với các penalty khác
2. **Horizon mismatch**: O2W chỉ 2 tuần, nhưng holding period thực 2-12 tháng → bias toward fast-momentum patterns, miss value/contrarian patterns có drawdown ban đầu
3. **Redundant với si_return**: si_return đã capture forward returns qua portfolio simulation → double-counting
4. **Median không robust**: Outliers + regime shifts làm median nhảy

**Fix recommended**: Chuyển từ multiplicative penalty sang **Stage 1 Quality Gate**:
```python
# Hard pass/fail filter trước khi tính main loss
def stage1_quality_gate(result):
    horizons_pass = sum([
        result['O2W_deal'] > 0.98,
        result['O1M_deal'] > 1.00,
        result['O2M_deal'] > 1.05,
    ])
    return horizons_pass >= 2

if not stage1_quality_gate(result):
    return {'loss': np.inf}

# Main loss KHÔNG còn O2W (tránh redundancy với si_return)
loss = -(si_return * 1.5 + win_deal * 0.5)
```

**Ưu**: Decoupled, dùng nhiều horizons không chỉ 2W, save compute (skip simulation cho bad patterns).

### 🚨 Issue 2: Validation đã bị disable

`tuning/buy_pattern/run_tuning.py` line 537: `if False:` → block validation hoàn toàn không chạy. Tất cả selection chỉ dựa IS performance.

**Fix**: Remove `if False:`, build CPCV framework theo Phần 2.

### 🚨 Issue 3: Sell pattern hyperopt độc lập với buy

Sell pattern dùng `ShortEvaluation` chạy trên **toàn universe**, không phải trên deals do buy pattern tạo ra → selection bias.

**Fix**: Theo Stage 3 trong Phần 3.2 — sell pattern hyperopt CHỈ trên deals từ top buy patterns.

### 🚨 Issue 4: Sell pattern không có portfolio simulation

Sell hyperopt chỉ deal-level metrics (median_profit, win_rate per deal). Không có Calmar, MaxDD, capital efficiency.

**Fix**: Add `Simulation` class vào sell pattern flow, đo improvement vs baseline exit.

### 🚨 Issue 5: Hard cutoff `NUM_DEAL_THRESHOLD = 200/150`

Pattern 199 deals → loss = inf. Pattern 201 deals → loss bình thường. Discontinuity.

**Fix**: Bayesian shrinkage thay vì hard cutoff:
```python
# Thay vì: if deal_count < 200: return inf
# Dùng: 
shrunk_metric = (metric * deal_count + prior * 100) / (deal_count + 100)
```

### 🚨 Issue 6: Buy pattern Init thiếu liquidity filter

Buy: `Init = "(time>='2014-01-01') & (time<='2025-01-01')"` — KHÔNG có liquidity filter.
Sell: `Init = "((Volume_3M_P50*Price/Inflation_7)>700_000_000) & (Volume > 2e+4)"` — có.

Buy hyperopt đang search trên universe rộng hơn sell → inconsistent + bias.

**Fix**: Thống nhất Init filter giữa buy và sell với liquidity floor.

### 🚨 Issue 7: Penalty multiplicative ad-hoc

```python
if (win_quarter < 0.5) or ...:
    penalty *= np.min([...]) / 0.5
```

Chia 0.5 không có lý thuyết. Multiplicative compound — pattern tệ ở 4 metrics bị penalty^4.

**Fix**: Additive penalty với explicit weights, hoặc dùng soft-thresholds:
```python
penalty = sum(max(0, threshold - metric) * weight for metric, threshold, weight in checks)
```

### 🚨 Issue 8: `clear_all_cache()` mỗi run

Line 622: clear cả Redis lẫn joblib trước mỗi tuning. Mất value của caching đã build.

**Fix**: Chỉ clear cache khi:
- Filter template thay đổi
- Indicator definitions thay đổi
- Time range thay đổi

Cache key có thể include hash của filter template để auto-invalidate khi cần.

### 🚨 Issue 9: Single train/test split

Buy: train `2014-2025`, validate `2025-2026` → chỉ 1 năm validate, regime concentration cao.

**Fix**: CPCV theo Phần 2.2 — 5-fold walk-forward minimum.

### 🚨 Issue 10: Fixed `INIT_SLOTS = 10`

Mỗi deal cùng size (10% NAV). Không có conviction sizing.

**Fix**: Score-based position sizing theo Layer 2 trong Phần 5.7.

## 12.3 Updated Implementation Plan (codebase-aware)

### Phase 0+: Quick Wins (1 tuần — làm trước mọi thứ khác)

Các fix có thể làm ngay với codebase hiện tại, immediate impact:

```python
# Fix 1: Refactor O2W từ multiplicative penalty thành Stage 1 quality gate
# tuning/buy_pattern/run_tuning.py line 334
# REMOVE: penalty *= deal_result['O2W_deal'] * deal_result['O2W_hit']
# ADD: stage1_quality_gate() check trước khi compute loss chính (xem Issue 1)

# Fix 2: Add liquidity filter to buy Init
Init = "(time>='2014-01-01') & (time<='2025-01-01') & ((Volume_3M_P50*Price/Inflation_7)>1_000_000_000)"

# Fix 3: Add trading_val to ranking
ranking_point = (
    0.25 * si_result['BuyPattern']['return']
  + 0.20 * deal_result['win_deal'] * 100
  + 0.15 * deal_result['win_quarter'] * 100
  + 0.10 * deal_result['winblock_20quarters'] * 100
  + 0.10 * deal_result['unique_ticker']  # MỚI: diversity
  + 0.10 * np.log10(deal_result['trading_val_median'] + 1)  # MỚI: liquidity
  + 0.10 * deal_result['profit_expected'] * 100
)

# Fix 4: Bayesian shrinkage thay hard cutoff
def shrunk_win_rate(wins, deals, prior_rate=0.5, prior_strength=20):
    return (wins + prior_rate * prior_strength) / (deals + prior_strength)

# Fix 5: Re-enable validation
# Replace `if False:` with `if loss > RECORD:`
```

### Phase 1+: CPCV Framework (2 tuần — leverage MongoDB infrastructure)

Existing MongoDB distributed framework hỗ trợ CPCV rất tốt:

```python
# Tạo 5 separate exp_keys cho 5 folds
for fold_idx in range(5):
    train_filter, val_filter = build_cpcv_fold(fold_idx)
    
    trials_name = f"trials_buy_{pattern}_{TRACK_VERSION}_fold{fold_idx}"
    trials = MongoTrials(f'mongo://...', exp_key=trials_name)
    
    # Override Init để chỉ dùng train data của fold này
    # ...
```

Mỗi fold chạy independent hyperopt → có 5 sets of best params. Robust selection chọn version tốt nhất across folds.

### Phase 2+: Refactor Sell Pattern Pipeline (2 tuần)

Sell pattern hiện tại chạy trên universe → chuyển sang chạy trên deals từ buy:

```python
# tuning/sell_pattern/hyo_tuning_manager.py
# Thay vì:
def eval(ticker):
    eval_ticker = ShortEvaluation(ticker, pdxx, dictFilter, ...)
    res_s = eval_ticker.get_shortsell(**params)

# Dùng:
def eval(ticker):
    # Load deals from selected buy pattern (cached)
    buy_deals = load_buy_deals(ticker, buy_pattern_version)
    
    # Apply sell pattern to these deals only
    eval_ticker = ShortEvaluationOnDeals(ticker, pdxx, dictFilter, buy_deals=buy_deals)
    res_s = eval_ticker.evaluate_with_baseline_exit(baseline_exit, **params)
    
    return res_s  # includes (calmar_smart - calmar_baseline)
```

### Phase 3+: Multi-Capital Robustness (1 tuần — leverage utilize_percent)

`utilize_percent` đã có sẵn → loop qua 3 sizes:

```python
# tuning/buy_pattern/run_tuning.py
def objective_multi_capital(params):
    losses = []
    for utilize_pct, weight in [(0.2, 0.4), (1.0, 0.4), (4.0, 0.2)]:
        # 0.2 = 4B (vs INIT_ASSETS = 20B), 1.0 = 20B, 4.0 = 80B
        result = eval_filter_all_v2(filter_dict, utilize_percent=utilize_pct)
        losses.append(weight * compute_loss(result))
    return sum(losses)
```

### Phase 4+: Pattern Quality Filter — Forward Returns Stage (1 tuần)

Existing code đã collect `O2W_deal`, `O1M_deal`, `O2M_deal` (line 232-234). Dùng làm Stage 1 quality filter:

```python
def stage1_quality_filter(result):
    """Pre-filter before expensive portfolio simulation"""
    quality = (
        0.30 * result['O2M_deal']                          # forward 2M return
      + 0.25 * result['O1M_deal']                          # forward 1M return  
      + 0.20 * result['win_deal'] * 100                    # hit rate
      + 0.15 * result['profit_median']                     # robust central
      + 0.10 * np.log10(result['trading_val_median'] + 1)  # liquidity
    )
    return quality

# Trong objective:
quality = stage1_quality_filter(deal_result)
if quality < QUALITY_THRESHOLD:
    return {'loss': np.inf}  # skip portfolio simulation
```

Tiết kiệm compute massive — bad patterns reject sớm trước khi simulate portfolio.

## 12.4 Quick Reference: File-Level Changes

| File | Changes |
|------|---------|
| `tuning/buy_pattern/run_tuning.py` | Bỏ O2W penalty (line 334), enable validation (line 537), add CPCV loop, add multi-capital, add liquidity Init filter |
| `tuning/buy_pattern/hyo_tuning_manager.py` | Pattern templates không đổi (Layer 1 patterns vẫn dùng) |
| `tuning/sell_pattern/hyo_tuning_manager.py` | Refactor để chạy trên buy_deals thay vì universe, add baseline exit comparison, add Simulation |
| `tuning/sell_pattern/run_tuning.py` | Loop qua buy patterns đã chọn, hyperopt sell trên từng cụm deals |
| `tuning/buy_pattern/parse_hyperopt_results.py` | Add CPCV aggregation: combine results from 5 folds, robust selection |
| **NEW** `tuning/cpcv_framework.py` | 5-fold walk-forward setup, regime stratification check |
| **NEW** `tuning/portfolio_selection.py` | Forward Stagewise Selection từ top patterns |
| **NEW** `tuning/factor_families.py` | Layer 2 factor scoring (8 families) |
| **NEW** `core_utils/shrinkage.py` | Bayesian shrinkage helpers |

## 12.5 Migration Path (không đập đi xây lại)

Mục tiêu: cải tiến **incrementally**, không break production:

1. **Week 1**: Apply Quick Wins (Phase 0+) — chỉ là bug fixes, hệ thống hiện tại vẫn chạy
2. **Week 2-3**: Build CPCV framework parallel với pipeline hiện tại — chạy cả 2 để compare
3. **Week 4-5**: Refactor sell pipeline — keep old version available cho rollback
4. **Week 6-7**: Add multi-capital + Stage 1 filter
5. **Week 8+**: Build Layer 2 factor scoring (new component, không thay thế)
6. **Week 12+**: Compare new full pipeline vs old, decide cutover

**Quan trọng**: Mỗi bước phải có A/B test (old vs new) trên cùng pattern set. Document gap IS-OOS sau mỗi fix → quantify improvement.

## 12.6 Tóm tắt Critical Issues Theo Mức độ

| # | Issue | Mức độ | Effort fix | Impact |
|---|-------|--------|-----------|--------|
| 1 | O2W multiplicative penalty (refactor sang Stage 1 gate) | High | 2-3h | Trung bình-Cao |
| 2 | Validation disabled (`if False:`) | 🚨 Critical | < 1h | Cao |
| 3 | Buy Init thiếu liquidity filter | High | 1h | Cao |
| 4 | Sell hyperopt độc lập với buy | High | 1 tuần | Cao |
| 5 | Sell không có portfolio simulation | High | 3-4 ngày | Cao |
| 6 | Hard cutoff NUM_DEAL_THRESHOLD | Medium | 1 ngày | Trung bình |
| 7 | Penalty multiplicative ad-hoc | Medium | 1 ngày | Trung bình |
| 8 | clear_all_cache mỗi run | Low | 1 ngày | Hiệu suất |
| 9 | Single train/test split | High | 2 tuần | Cao |
| 10 | Fixed INIT_SLOTS không conviction | Medium | 1 tuần | Trung bình |

**Action gợi ý**: Làm Issues #1, #2, #3 ngay trong tuần này (< 4 giờ work, immediate impact). Sau đó plan các fix còn lại theo roadmap Phase 0+ → Phase 4+.
