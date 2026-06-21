---
name: F-system definition
description: F-system cho giao dịch phái sinh VN30F ngắn hạn 3-5 ngày. SIG-B chính (r_score valley, score≥4). SIG-A tạm suspend (VN30 data chỉ 6 signals). Script daily: f_system_daily.py
type: project
originSessionId: 637d3857-e32a-46ff-8dc2-9739c4574bd9
---
## F-system — Short-term Derivatives (VN30F, 3-5 ngày)

**Nguyên tắc:** Dùng H-system state + r_score để phát tín hiệu LONG VN30F.
**Chỉ LONG** — short side không có edge trên VNINDEX/VN30.
**Holding period:** T+5 phiên (entry T+1 sau tín hiệu)
**TC phái sinh:** 0.1% round-trip
**Return measurement:** VN30 index (không phải VNINDEX) vì trade VN30F futures.
**State machine:** Vẫn dùng VNINDEX H-system làm timing signal.

---

### SIG-A: BEAR → NEUTRAL Transition — ⚠️ SUSPEND

**Lý do suspend:** VN30 chỉ có từ 2012-02-06, chỉ có 6 BEAR→NEUTRAL signals.
Sample quá nhỏ (n=6), scoring rules cũ không valid trên VN30 returns.
Khi có thêm data (≥15 signals) sẽ recalibrate.

**Điều kiện:** State hôm qua = BEAR, state hôm nay = NEUTRAL (sau smoothing)

---

### SIG-B: r_score Valley (Turn Up) — CHÍNH

**Điều kiện:** Hôm qua là đáy r_score được xác nhận:
  - r_score[hôm qua] < r_score[hôm kia]  ← đang giảm
  - r_score[hôm qua] < r_score[hôm nay]  ← bắt đầu tăng (xác nhận)
  - delta_up = r_score[hôm nay] - r_score[hôm qua] >= 0.010

**Timing:** Xác nhận cuối ngày hôm nay, entry mở cửa phiên sau (T+2 từ đáy = 1 ngày delay so với backtest)

**Scoring (0–6 điểm, cần ≥4 để giao dịch):**

| Rule | Điều kiện | Điểm |
|------|-----------|------|
| Valley thấp | r_score_valley < 0.40 | +1 |
| Turn mạnh | delta_up > 0.015 | +1 |
| Giảm sâu | valley_depth > 0.05 (từ đỉnh gần nhất) | +1 |
| State tốt | State trong NEUTRAL/BULL/EX-BULL | +1 |
| 1M yếu | p1m_vn30 < -3% | +1 |
| Vol ổn | vol20_vn30 < median (~14.5%) | +1 |

**Kết quả backtest (VN30, 2012–2026, n=194 total, ~13.7/năm):**

| Score | n | WR T+5 | Net T+5 | Leverage Kelly 30% |
|-------|---|--------|---------|-------------------|
| <4 | 90 | ~56% | ~+0.2% | **Bỏ qua** (score 3 net âm) |
| 4 | 49 | 61% | +0.50% | **0.83x** |
| 5 | 45 | 60% | +0.60% | **1.11x** |
| 6 | 10 | 70% | +0.53% | **1.20x** |

**Combined (score ≥4, 2012+):**
- ~7 trades/năm | WR = 62% | AvgWin = +1.84% | AvgLoss = -1.78% | PF = 1.42

---

### Daily signal script

**File:** `f_system_daily.py`
**Chạy:** `python f_system_daily.py` sau khi có data cuối ngày
**Output:**
```
=== F-SYSTEM SIGNAL — 2026-05-06 ===
SIG-B: CÓ — Score 5/6 → Leverage 1.11x
  Entry: mở cửa ngày mai
  Hold:  5 phiên (đến 2026-05-13)
  P(win): 60%
```

---

### Lưu ý quan trọng

1. **Return measurement = VN30:** Script tính vol, p1m dùng VN30 (không phải VNINDEX). Median vol VN30 ~14.5% (thấp hơn VNINDEX ~18%).
2. **SIG-B có 1 ngày lag:** Valley xác nhận hôm nay → entry ngày mai (T+2 từ đáy).
3. **Ngưỡng score ≥4 (không phải ≥3):** Score 3 trên VN30 cho net return âm (-0.09%).
4. **SIG-A suspend:** Chỉ có 6 VN30 signals từ 2012, không đủ để hiệu chỉnh.
5. **Chỉ LONG:** Không short trong mọi trường hợp.
6. **Không overlap:** Nếu đang có lệnh T+5 chưa thoát, không vào lệnh mới.
