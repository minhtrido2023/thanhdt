# Session Synthesis — Book C (Value) + Capitulation Optimization + V2.2 Verification
**Date: 2026-06-12**

## 0. Câu hỏi gốc → hành trình
Bắt đầu: "Tận dụng VN30F khi thị trường quá hưng phấn (EX-BULL) như đã mua khi sợ hãi (CRISIS)?"
→ Short bị bác bỏ → pivot sang VALUE book → thiết kế đầy đủ Book C → tối ưu capitulation → verify V2.2.

---

## 1. EX-BULL / Euphoria short — BÁC BỎ
`euphoria_short_analysis.py`
- EX-BULL = tín hiệu **tiếp diễn (procyclical)**, không đảo chiều: fwd60 +4.9%/76% win.
- SHORT VN30F: corr VNI-VN30F = 0.948 trong EX-BULL → −0.23pp CAGR, **không giảm MaxDD**.
- **Thay vì short → nghiêng VALUE**: trong EX-BULL value +9.7%/tháng vs momentum +3.4%.

## 2. Book C (VALUE) — THIẾT KẾ HOÀN CHỈNH
**Capital (Option A)**: 50B = BAL 17.5B + LAG 17.5B + **VALUE 15B** (thay 30% vốn, quản lý 1 danh mục).

**Signal** (`book_c_signal.py`, `book_c_live_signal.sql`):
- vscore = PB.rank(pct) + PE.rank(pct), top quintile 20%
- Quality gate V4: ROIC5Y≥8% AND FSCORE≥5, PE<100, liq≥10B
- Liq-weighted. Live picks hôm nay: PVP, NT2, VHC, PVT, IJC.

**BQ-validated (ticker_prune 2016-26, profit_1M)**:
- Standalone gated: 18.4%/Sh0.84/DD−33.9 (trung bình)
- **BLEND 70%V2.2+30%C: 24.4%/Sh1.59/DD−17.0/Cal1.44** vs pure V2.2 25.4%/1.29/−19.8
- Giá trị = **diversification (+0.30 Sharpe, −2.8pp DD, đổi −1pp CAGR)**
- Grind 2025-09..2026-03: value −8.8% vs momentum −19.8% (bảo vệ +11pp)
- Anti-phase: 2021 value +122% vs +61%; corr value-vs-momentum = −0.03 (trực giao)

**3 nhịp vận hành**:
1. Rotate mã trong book → **tháng, anchor ngày 10** (`book_c_rebal_timing.py`)
2. Exposure → theo DT5G, đổi NGAY khi state đổi (CRISIS 0/BEAR 20/NEUTRAL 70/BULL 100/EX-BULL 130% của 15B)
3. Cross-book weight reset → **Band ±10pp** (`book_rebal_policy.py`)

**Rebalance timing ngày 10 — phát hiện**: day10-15 plateau CAGR 34-35% vs EOM 27%. Cơ chế: KHÔNG rotate đầu tháng earnings (data cũ, ôm qua mùa BCTC); value drift hậu-BCTC chạy ~6 tuần → rotate sớm tháng-2-quý bắt trọn drift. BCTC rải: ngày 20 mới 32%, ngày 25 = 69%.

**Cross-book ±10pp — phát hiện**: chỉ reset khi 1 book lệch >10pp (4 lần/10 năm). Monthly bơm vốn lại momentum đúng lúc drawdown (hại DD, tốn TC). Never để LAG phình 49% (rủi ro tập trung). Cash do DT5G gate xuống = reserve của book, KHÔNG chuyển sang book khác (chỉ capit sleeve nhận).

## 3. Capitulation stock selection — TỐI ƯU
`capit_stock_optimizer.py`, `capit_before_after.py`, `capit_liquidity_audit.py`

**Feature IC (CRISIS washout)**: pb_z +0.398 ≈ D_RSI +0.382 (mạnh nhất); ID_LO_3Y +0.20; PC_6M +0.22.
**Pattern_Median_Profit_3Y IC = −0.298 (ÂM — tránh "mã hay bounce")**. ROIC5Y ≈ 0 (= risk filter, không phải bounce predictor).

**Before/after (9 events)**: OLD strict quality+golden = **91% win** > composite mới 55%. → strict quality gate là yếu tố then chốt, KHÔNG nới lỏng.

**Update `crisis_capitulation_signal.py`** (bảo thủ):
- Tier 0 mới = quality_strict + golden + RSI≤0.35 (triple confirm)
- RSI làm secondary sort; sector exclusion BDS(86)/ck(87)/mining(33) — đều IC âm
- Giữ nguyên strict quality + golden

**Capacity constraint (QUAN TRỌNG)**: universe **cấu trúc mỏng** — avg 2 mã/event, fill 50% ở 10B. Chỉ 6 mã unique trong 9 events (SAB/VSC/SCS/BMP/VCS/SIP). Thêm Tier 2+ để fill → delta fwd60d ÂM (−4..−12pp 2022). → **size capit 8-10B max, giữ cash phần dư, KHÔNG force-fill**. Script giờ in capacity table + Tier 2 fallback chỉ khi T0+1=0.

## 4. V2.2 RE-VERIFICATION (2014 → 2026-05) — XÁC NHẬN
`v22_reverify_2014.py` — tái dựng độc lập từ leg NAV thật (pt_v22_bal/lag_v21):

| Strategy | CAGR | Sharpe | Sortino | MaxDD | Calmar |
|----------|------|--------|---------|-------|--------|
| BAL leg (25B) | 18.2% | 1.20 | 1.14 | −24.7% | 0.74 |
| LAG leg (25B) | 28.5% | 1.49 | 1.62 | −31.5% | 0.90 |
| **V2.2 base (sum)** | **24.5%** | **1.61** | 1.87 | −21.6% | 1.13 |
| **V2.2 +capit** | **26.2%** | **1.66** | 1.98 | **−20.1%** | 1.31 |
| VNINDEX B&H | 11.4% | 0.68 | 0.80 | −45.3% | 0.25 |

**Khớp champion**: base 24.49% vs claimed 24.08% (+0.41pp, do period kết thúc 2026-05-15 chưa gồm 2026 âm); +capit 26.20% vs 25.77%, **MaxDD −20.1 khớp tuyệt đối, Sharpe 1.66 vs 1.65**. ✅ V2.2 LÀ THẬT.

**IS/OOS (không overfit)**: base IS 19.6%/OOS 29.3%; +capit IS 23.6%/OOS 28.7%. OOS ≥ IS.
**Phòng thủ**: 2022 VNINDEX −34% → V2.2 +1.8%. Beats VNINDEX 9/13 năm.
**Diversification > combination**: ghép BAL+LAG nâng Sharpe 1.20/1.49 → 1.61. Band±10pp cho Sharpe/Calmar tốt nhất (1.63/1.14) ngay cả 2-leg.
**2026 YTD: base −1.6%, capit −0.1%** = grind hiện tại → đây chính là chỗ Book C (value) bù đắp.

---

## TỔNG KẾT — Kiến trúc đề xuất
```
V2.2 EXTENDED — 50B, quản lý 1 danh mục
├─ BOOK A: BAL (V11 momentum)    17.5B  35%  ─┐ momentum bucket
├─ BOOK B: LAG (PEAD)            17.5B  35%  ─┘ (BAL/LAG corr 0.53)
└─ BOOK C: VALUE (PB+PE, V4)     15.0B  30%     (trực giao, corr −0.03)
+ CAPIT sleeve overlay (8-10B, CRISIS-only, capacity-bound, đã verify)

Rebalance: holdings tháng (C: ngày 10) | exposure theo DT5G | cross-book Band ±10pp
DT5G gating Book C: CRISIS 0 / BEAR 20 / NEUTRAL 70 / BULL 100 / EX-BULL 130%
```
**Trạng thái**: V2.2 LIVE từ 2026-06-11. Book C đã đủ spec, validated, chờ paper-trade forward.
**Tại sao thêm Book C**: V2.2 = độc canh momentum, 2026 grind −1.6% là điểm yếu cấu trúc; value trực giao bù đúng pha (+0.30 Sharpe, −2.8pp DD).
