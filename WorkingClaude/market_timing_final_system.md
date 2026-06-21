# Hệ thống Xác định Tình trạng Thị trường – Kết quả Backtest 2000-2026

## 1. Tóm tắt Kết quả Backtest

### Toàn bộ giai đoạn 2000-2026 (6,262 ngày)

| Hệ thống | CAGR | Max DD | Sharpe | Calmar | % Thời gian trong TT | Giao dịch |
|---|---|---|---|---|---|---|
| Buy & Hold | 11.9% | -79.9% | 0.46 | 0.15 | 100% | 0 |
| MA200 Cross | 13.7% | -79.2% | 0.72 | 0.17 | 60.5% | 144 |
| RSI Momentum | -2.3% | -86.3% | 0.05 | -0.03 | 56.8% | 60 |
| MA200 + RSI Combo | 0.2% | -73.7% | 0.12 | 0.00 | 43.9% | 204 |
| **MACD Trend** | **24.1%** | **-48.8%** | **1.04** | **0.49** | **53.5%** | **372** |
| Old PE Rule (market_rule.md) | 5.9% | -79.2% | 0.43 | 0.07 | 29.4% | 92 |
| New Multi-factor Rule | 1.4% | -63.1% | 0.17 | 0.02 | 51.0% | 189 |
| **5-State Machine** | 11.9% | -60.0% | 0.51 | **0.20** | 52.9% | 264 |

### Giai đoạn có PE (2016-2026)

| Hệ thống | CAGR | Max DD | Sharpe | Calmar |
|---|---|---|---|---|
| Buy & Hold | 12.5% | -45.3% | 0.73 | 0.28 |
| **MACD Trend** | 14.6% | -14.5% | **1.28** | **1.01** |
| **MA200 Cross** | 14.8% | -21.8% | 1.08 | 0.68 |
| MA200 + RSI Combo | 11.7% | -22.0% | 0.96 | 0.53 |
| 5-State Machine | 13.1% | -26.2% | 1.02 | 0.50 |
| Old PE Rule | ~0% | 0% | N/A | N/A | ← **STUCK IN CASH** |

---

## 2. Phát hiện Quan trọng

### 2.1 Old PE Rule (market_rule.md) – BỊ BROKEN từ 2018

**Nguyên nhân thất bại:**
- Năm 2018, VNI đỉnh 1200 pts với PE = 22.6x (vượt P95 = 19.1x)
- Rule bán ra, block window **545 ngày**, kèm điều kiện cực khắt: cần PE <= P20 = 13.3x mới mở lại
- PE chưa bao giờ rớt xuống 13.3x sau 2018 → **hệ thống bị khóa vĩnh viễn trong cash**
- Toàn bộ đợt tăng 2019-2021 (+170%) bị bỏ lỡ hoàn toàn

**Kết luận: Old PE Rule không hoạt động trong điều kiện thị trường hiện tại.**

### 2.2 RSI Momentum – Tệ nhất

- CAGR -2.3% trên toàn giai đoạn, thua cả tiền gửi ngân hàng
- Lý do: VNINDEX xu hướng đi lên dài hạn, RSI oversold thường xuất hiện trong đáy ngắn hạn của bull market, không phải đỉnh bán

### 2.3 MACD Trend – Hiệu quả Nhất (nhưng nhiều giao dịch)

- CAGR 24.1%, Sharpe 1.04, MaxDD chỉ -48.8%
- 372 lần đổi trạng thái trong 26 năm ≈ 14 lần/năm → **không phù hợp cho investor thông thường**
- Phù hợp nếu dùng làm **bộ lọc phụ** thay vì hệ thống chính

### 2.4 MA200 Cross – Đơn giản, Bền vững

- CAGR 13.7%, chỉ 144 giao dịch (≈ 5.5 lần/năm)
- Mạnh nhất trong giai đoạn volatile 2021-2026 (Calmar 0.90)
- **Nền tảng tốt nhất** cho hệ thống tổng hợp

### 2.5 5-State Machine – Tốt nhất về Điều chỉnh Rủi ro

- MaxDD chỉ -60% vs Buy & Hold -79.9% (cải thiện 20pp)
- CAGR bằng Buy & Hold nhưng **Calmar = 0.20 vs 0.15**
- Xác định đúng các sự kiện lịch sử quan trọng

---

## 3. Kiểm tra tại các Sự kiện Lịch sử

| Sự kiện | VNINDEX | RSI | PE | State 5SM | Nhận định |
|---|---|---|---|---|---|
| 2007-03 Đỉnh 1170 | 1171 | 0.68 | N/A | **CAUTION** ✓ | Đúng – thoát ra |
| 2008-03 Bear bắt đầu | 635 | 0.23 | N/A | **PANIC** ← | RSI cực thấp nhưng còn đang rơi |
| 2009-02 Đáy 235 | 236 | 0.15 | N/A | **PANIC** ✓ | Đúng – mua đáy |
| 2012-01 Đáy 350 | 339 | 0.24 | N/A | **PANIC** ✓ | Đúng – mua đáy |
| 2018-04 Đỉnh 1200 | 1204 | 0.71 | 22.6x | **CAUTION** ✓ | Đúng – PE cực cao, RSI > 0.70 |
| 2020-03 COVID crash | 667 | 0.08 | 10.3x | **PANIC** ✓ | Đúng – cơ hội mua thế kỷ |
| 2021-11 Đỉnh 1500 | 1489 | 0.68 | 17.5x | **CAUTION** ✓ | Đúng – bắt đầu giảm |
| 2022-11 Đáy 900 | 943 | 0.35 | 9.8x | **BEAR** ← | Gần đúng (RSI vừa chạm ngưỡng) |
| **2026-04 Hiện tại** | **1817** | **0.648** | **15.45x** | **BULL** ✓ | PE hợp lý, xu hướng tốt |

---

## 4. Optimal Parameters (Grid Search)

Từ tìm kiếm tham số tối ưu trên giai đoạn PE 2016-2026:

```
PE Sell threshold : P80 = 17.04x  (vs P60 = 16.33x cũ)
RSI Sell threshold: 0.70           (vs 0.65 đề xuất trước)
RSI Bear threshold: 0.40           (vs 0.45 đề xuất trước)
RSI Panic threshold: 0.32          (vs 0.30 đề xuất trước)

Kết quả: CAGR 15.3%, MaxDD -25.2%, Sharpe 1.12, Calmar 0.61
So với 5-State Machine ban đầu: Calmar 0.50 → cải thiện +22%
```

---

## 5. Hệ thống Đề xuất Cuối cùng

### VNINDEX Market Timing System v2.0

**Kiến trúc: 3 lớp**

```
Layer 1: TREND FILTER (MA200)          → Xác định bull/bear
Layer 2: MOMENTUM FILTER (MACD + RSI)  → Xác định mạnh/yếu trong trend
Layer 3: VALUATION OVERLAY (PE)        → Giới hạn tham gia khi quá đắt
```

### Các trạng thái và vị thế

| State | Điều kiện | Vị thế Cổ phiếu | Ghi chú |
|---|---|---|---|
| **PANIC** | RSI < 0.32 AND dưới MA200 AND C3M < -15% | **100%** + xem xét margin | Mua mạnh đáy |
| **BULL** | Trên MA200 AND MACD > 0 AND RSI < 0.70 AND PE < P80 | **90-100%** | Tình trạng bình thường tốt |
| **NEUTRAL** | Trên MA200 AND (MACD > 0 hoặc RSI > 0.40) | **70-80%** | Duy trì, không mở thêm |
| **CAUTION** | PE >= P80 (17.0x) AND RSI > 0.70 AND trên MA200 | **30-50%** | Cắt giảm dần |
| **BEAR** | Dưới MA200 AND RSI < 0.40 AND MACD < 0 | **0-20%** | Phòng thủ, giữ tiền mặt |

### Quy tắc chuyển trạng thái (với Hysteresis)

```
BEAR → NEUTRAL: Cần trên MA200 AND RSI > 0.45 AND MACD > 0
CAUTION → NEUTRAL: Cần PE < P70 HOẶC RSI < 0.55
NEUTRAL → BULL: Trên MA200 AND MACD > 0 AND RSI < 0.65 AND PE < P80
BULL → CAUTION: PE >= P80 AND RSI > 0.70 AND trên MA200
```

### Tích hợp với chiến lược cổ phiếu

**Thay thế `_create_schedule_market` trong MarketEvaluation:**

```python
# SELL trigger (thay vì PE >= P60 cũ)
sell_trigger = (pe >= P80) and (rsi > 0.70) and (close > ma200)

# Block window (rút ngắn)
if pe >= P95:  window = 180  # days (vs 545 cũ)
elif pe >= P90: window = 120  # days (vs 365 cũ)
elif pe >= P80: window = 60   # days (vs 90 cũ)

# Reopen condition (nới lỏng)
if sell_pe >= P90:
    reopen = (pe <= P40) or (rsi < 0.35)  # vs PE <= P20 cũ
else:
    reopen = (pe <= P70) or (rsi < 0.40)

# PANIC override (thêm mới)
if rsi < 0.32 and not above_ma200 and c3m < -0.15:
    force_buy = True  # Bỏ qua mọi block window
```

---

## 6. Kết luận về Hiệu quả từng Hệ thống

### Xếp hạng tổng hợp (cân bằng giữa return, risk, thực tế)

| Rank | Hệ thống | Điểm mạnh | Điểm yếu | Phù hợp |
|---|---|---|---|---|
| 🥇 | **MACD Trend** | Return cao nhất, MaxDD thấp | 372 giao dịch/26 năm | Quant/algo |
| 🥈 | **MA200 Cross** | Đơn giản, robust, ít giao dịch | Lag khi trend đảo | Tất cả |
| 🥉 | **5-State Machine** | Risk-adjusted tốt, đúng ở sự kiện lớn | Phức tạp hơn | Sophisticated investor |
| 4 | MA200 + RSI Combo | Ít giao dịch, stable | Return thấp hơn MA200 | Conservative |
| 5 | Old PE Rule | N/A | **Broken – bỏ ngay** | Không |

### Khuyến nghị thực tế

**Cho investor thông thường:**
→ Dùng **MA200 Cross** làm nền, thêm **MACD xác nhận** tránh false cross

**Cho hệ thống algo (webui/utils.py):**
→ Implement **5-State Machine** với optimal params:
  - PE P80 = 17.04x làm ngưỡng CAUTION
  - RSI 0.70 sell, 0.40 bear, 0.32 panic
  - PANIC override để mua đáy

**Điều chỉnh MarketEvaluation:**
1. ❌ Loại bỏ: rule P60 sell + block window dài + P90→P20 reopen
2. ✅ Thêm: 5-State Machine với optimal params
3. ✅ Thêm: PANIC override (mua bất chấp block khi RSI < 0.32 + dưới MA200)
4. ✅ Rút ngắn: block windows x3 lần (180/120/60 thay vì 545/365/90)

---

## 7. Tình trạng Hiện tại (2026-04-17)

```
VNINDEX   : 1817  (+above MA200=1685, +7.8%)
RSI       : 0.648  (neutral-high, chưa overbought)
MACDdiff  : +18.48 (dương – bullish momentum)
CMF       : +0.052 (nhẹ bullish)
PE        : 15.45x  (P50, moderate – không đắt)
C3M       : -4.2%   (đã pullback 3 tháng)

STATE     : BULL ✅
SIGNAL    : IN – 90-100% cổ phiếu
```

**Nhận định:** Thị trường đang ở vùng hợp lý. PE ở mức trung bình lịch sử (P50), đang trên MA200, MACD dương. Không có dấu hiệu CAUTION. Có thể duy trì/mở vị thế. Cần theo dõi nếu RSI chạm 0.70+ kết hợp PE tăng lên 17x+.
