# PHẦN 3 — Backtest hướng sửa BAL: nghiêng bộ chọn về earnings yield (H-EY)
job `Taylor_20260909_100425` · 2026-09-09 · **PAPER-ONLY, VERDICT = NO-GO**

Tiền đăng ký viết TRƯỚC khi nhìn số treatment: `p3/PREREG.md` (N_trials=3, λ ∈ {0,25; 0,50; 1,00},
7 tiêu chí GO chốt trước). Không có trial nào khác trên trục này trong job.

## 1. Vì sao chỉ chạy H-EY

Phần 2 loại toàn bộ họ kỹ thuật ở cổng OOS sau BH (`prox52` p_BH 0,638; mọi indicator momentum/trend
t ∈ [−1,0; +0,3] OOS). `ey` là indicator DUY NHẤT sống OOS (IC +0,0747, t 4,81, p_BH < 0,0001), dương
ở cả BULL lẫn NEUTRAL, và mạnh lên 2025-2026. Cơ chế Phần 1 (gate `state ∈ {4,5}` + hold cứng 45 phiên)
là hướng đúng hơn về nhân quả **nhưng N thật = 10 cửa sổ regime** ⇒ mọi tham số mới sẽ được chọn trên
chính 10 sự kiện đó; ghi làm khuyến nghị thiết kế vòng sau, KHÔNG chạy ở đây.

Knob dùng: `BAL_CFO_BLEND=λ` + `BAL_YIELD_METRIC=pe` — **đã có sẵn trong production**, mặc định 0 = tắt.
Cộng `λ·40·(rank_pct(ey) − 0,5)` vào `ta` (khoá SẮP XẾP trong-tier). Không đổi ngưỡng tier, DT5G,
allocator, CAPIT, custom30V.

## 2. Chân control — tái lập pin R3 BYTE-IDENTICAL

CAGR **28,8627%** / Sharpe 1,8316 / MaxDD −17,785% / Calmar 1,6229 / Final NAV **1.178,0099B**
= trùng pin R3 2026-08-03. CSV md5 **`7d053e6201c9d107685ff4d1dd9d2d2a`** = trùng byte artifact pin.
Self-check **0 VND** (cash-flow identity + final-NAV identity, cả sổ BAL lẫn LAG) trên **cả 4 chân**.

## 3. Kết quả A/B (`p3/p3_ab_metrics.csv`)

| leg | λ | CAGR % | ΔCAGR pp | ΔCAGR IS(14-19) | ΔCAGR OOS(20+) | Calmar | MaxDD % |
|---|---|---|---|---|---|---|---|
| ctrl2 | 0 | 28,863 | — | — | — | 1,6229 | −17,785 |
| ey025 | 0,25 | 29,540 | +0,677 | **−0,015** | +1,331 | 1,6869 | −17,512 |
| ey050 | 0,50 | 29,145 | +0,283 | **−0,015** | +0,557 | 1,6643 | −17,512 |
| ey100 | 1,00 | **29,643** | **+0,781** | +0,028 | +1,502 | 1,6894 | −17,546 |

## 4. Chấm theo 7 tiêu chí tiền đăng ký

| # | Tiêu chí | Ngưỡng | Kết quả (chân tốt nhất ey100) | |
|---|---|---|---|---|
| C1 | ΔCAGR full | > +0,385pp | +0,781pp | ✅ |
| C2 | Calmar không xấu đi | ≥ 1,6229 | 1,6894 | ✅ |
| C3 | IS và OOS cùng dấu dương | — | IS **+0,028pp** / OOS +1,502pp | ⚠️ sát 0 (ey025/ey050 IS ÂM) |
| C4 | LOYO: không năm nào > 50% delta | — | **2021 = +12,93pp**, full-period delta chỉ +0,78pp | ❌ |
| C5a | DSR (N_trials=3) | > 0,95 | **0,570** (null = Sharpe của control) | ❌ |
| C5b | PBO (CSCV S=16) | < 0,5 | **0,6845** | ❌ |
| C6 | Dose-response đơn điệu theo λ | — | +0,677 → **+0,283** → +0,781 (răng cưa) | ❌ |
| C7 | Self-check 0 VND | — | 0 VND, 2 sổ × 4 chân | ✅ |

**4 tiêu chí fail ⇒ NO-GO.** Prereg quy định thiếu 1 là NO-GO.

⚠️ **Cách đọc DSR cho đúng.** `DSR vs 0 = 1,000000` là con số VÔ NGHĨA ở đây — nó chỉ nói "Sharpe
dương sau 12,5 năm", đúng với cả chân control. Null trung thực là **"có đánh bại được chính cấu hình
pin không"** ⇒ `DSR vs SR_ctrl = 0,570`. Ai trích `DSR = 1,0` từ log này là trích sai null.

## 5. Vì sao fail — cơ chế, không phải xui

**(a) Delta là NHIỄU ĐƯỜNG ĐI, không phải edge.** Per-year (`p3/p3_peryear.csv`):

| | 2014-17 | 2018 | 2020 | 2021 | 2022 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| Δ ey100 | **0,00** | +0,16 | −1,15 | **+12,93** | +3,13 | −1,39 | −1,64 | +1,24 |
| Δ ey050 | **0,00** | −0,29 | +0,66 | **−13,22** | +4,02 | −0,06 | **+7,20** | −0,16 |

Cùng một hướng nghiêng, λ = 0,5 làm 2021 **−13,2pp** còn λ = 1,0 làm 2021 **+12,9pp**. Một tham số
đơn điệu không thể tạo ra đảo dấu 26pp trên cùng một năm nếu nó đang khai thác một edge thật — đó là
chữ ký của **hoán vị thứ tự chọn mã làm rẽ nhánh cả quỹ đạo danh mục** (chọn khác mã ⇒ vốn khác ⇒
lệnh sau khác). C6 (răng cưa) và C4 (một năm nuốt toàn bộ delta) là **cùng một sự thật** nhìn từ 2 phía.

**(b) 4/13 năm delta = 0,00 chính xác.** 2014-2017 knob KHÔNG hề đổi kết quả ⇒ N hiệu dụng còn nhỏ
hơn 10 cửa sổ của Phần 1. ΔCAGR full-period +0,78pp đang được ước lượng trên ~6 sự kiện độc lập.

**(c) Block bootstrap xác nhận:** delta = **+0,604pp/năm, CI95 [−0,242; +1,666]**, P(Δ>0) = 0,901.
CI ôm 0 ⇒ không phân biệt được với 0 ở mức 5%.

**(d) PBO 0,68 nói thẳng:** chọn chân tốt nhất theo IS thì 68% số lần nó rơi xuống dưới trung vị OOS.
Đúng dạng "chọn được λ tốt trong quá khứ ≠ λ đó tốt trong tương lai".

## 6. Nghịch lý phải nói rõ

`ey` **có IC OOS thật** (t 4,81, p_BH<1e-4 — Phần 2 §3.2) nhưng nghiêng BAL theo nó **không** cho edge
danh mục. Không mâu thuẫn: IC đo trên **51.650 dòng × 150 tháng toàn universe**, còn BAL chỉ mở lệnh
trong **10 cửa sổ BULL/EX-BULL**, mỗi cửa sổ tối đa 12 vị thế. Một tín hiệu cắt-ngang yếu-nhưng-thật
cần hàng trăm lượt độc lập để hiện ra; BAL không có chỗ cho nó chạy. **Nút cổ chai của BAL là CẤU TRÚC
CƠ HỘI (gate regime + hold cứng), không phải chất lượng xếp hạng.**

Đây cũng là lý do khuyến nghị vòng sau nhắm vào cơ chế chứ không nhắm vào feature — xem §7.

## 7. Khuyến nghị (KHÔNG wire, cần tiền đăng ký riêng)

1. **Không wire H-EY.** `BAL_CFO_BLEND` giữ mặc định 0. Đây là lần NO-GO độc lập cho hướng "thêm/đổi
   tín hiệu xếp hạng cho BAL".
2. **Hướng có cơ sở nhân quả duy nhất còn lại = cơ chế thoát/tái nhập** (Phần 1 §5: hold cứng 45 phiên
   buộc bán 10-21/04/2026 đúng đáy, rồi gate `state ∈ {4,5}` khoá BAL ngoài nhịp +10,73%). Nhưng N=10
   ⇒ **không được tune trên chính 10 cửa sổ đó**. Thiết kế đúng phải là tiền đăng ký một luật đơn giản
   (vd exit theo trailing thay vì đếm phiên), khai N_trials thật, và chấp nhận power thấp.
3. **Theo dõi, chưa hành động:** `ey` lúc BAL vào lệnh trôi 0,15 (2019) → 0,059 (2026) — BAL đang mua
   ngày càng đắt. Nếu xu hướng này tiếp tục 2027 thì đó mới là bằng chứng alpha decay; hiện Spearman
   (năm, ret) p=0,960.
4. **Nợ kỹ thuật đã khai trong PREREG (giờ thành moot vì NO-GO):** `data/bal_open_pcf.csv` vintage
   2026-06-16 lệch snapshot pin, dừng 2026-06-15. Nếu ai chạy lại trục này phải sửa vintage TRƯỚC.

## 8. Vật chứng

`p3/PREREG.md` · `p3/run_leg.sh` · `p3/bal_ey_engine.py` · `p3/run_{ctrl2,ey025,ey050,ey100}.log` ·
`p3/analyze_p3.py` · `p3/p3_ab_metrics.csv` · `p3/p3_peryear.csv`.
NAV CSV: `data/v23_golive_audit_..._exp_baley{ctrl2,ey025,ey050,ey100}.csv` (`AUDIT_EXP_TAG` giữ mọi
output khỏi đường dẫn canonical — §8 coding_guidelines).
