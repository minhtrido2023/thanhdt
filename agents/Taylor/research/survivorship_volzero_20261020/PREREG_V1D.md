# PREREG V1D — Chặn khớp khi ADV3M<=0 (LIQ_ZERO_BLOCK, nhân quả) — job Taylor_20261020_162558, EXPLORATORY
Không sửa pin/registry/pin_ledger/engine thật; chỉ bản sao `eng/` (+ `eng_dep1m/` giống hệt). Không đề xuất đổi luật.
Viết + md5 + commit TRƯỚC khi chạy. Khuyến nghị gốc: quant-skeptic `logs/verify_20261020_160452_37110.log` (recommended_reruns[0]).

## 1. Câu hỏi
Pin LAG có thực thi được ở NAV 50 tỷ không khi KHÔNG cho khớp ở mã ADV3M<=0 (engine gốc bỏ qua trần ⇒ mua trọn size)?
ΔCAGR nhân quả (không dùng KL cùng phiên để định cỡ).

## 2. Biến thể (bản sao engine; chỉ lệnh gọi `simulate()` có `liquidity_require_positive=True` = book LAG, cả lượt base lẫn chính)
ADV3M = `liquidity_lookup[(tk, ngày)]` = `Volume_3M_P50 × COALESCE(Price, Close)` (đúng nguồn trần 20% của pin; giá trị đã có
lúc mở cửa vì Volume_3M_P50 là thống kê 3 tháng — dùng nguyên như pin, không đổi định nghĩa). "ADV3M<=0" = key thiếu HOẶC <=0.
- **MUA**: knob CÓ SẴN của engine `LIQ_ZERO_BLOCK=lag` ⇒ `daily_max=0` khi ADV3M<=0 (phiên đó tính vào cửa sổ `max_fill_days=5`;
  hết cửa sổ <`min_fill_pct` ⇒ bỏ, như engine). Mã ADV3M>0: trần 20%×ADV3M giữ nguyên.
- **BÁN** (knob mới bản sao `V1D_SELL=1`): lệnh bán T+1 Open của lô LAG bị hoãn (`still_pending`, thử lại mỗi phiên) khi ADV3M
  của phiên đó <=0. Không có trần bán cho ADV3M>0 (giữ như pin). Lô kẹt tới cuối kỳ vẫn mark theo Close như engine.
- Hai chân đo:
  - **V1D (CHÍNH)** = `ZVF_MODE=block` (V1A: Volume=0 ⇒ không khớp, ngữ nghĩa user xác nhận) + `LIQ_ZERO_BLOCK=lag` + `V1D_SELL=1`.
    Câu "pin LAG có thực thi được": cả 2 điều kiện khả thi (có khớp + có thanh khoản đo được trước phiên).
  - **V1D0 (phân rã)** = `LIQ_ZERO_BLOCK=lag` + `V1D_SELL=1`, không ZVF. Δ(V1D0−pin) = đóng góp riêng của chặn ADV3M<=0;
    Δ(V1D−V1A) = gia số của chặn ADV3M<=0 khi đã chặn Volume=0.
- BAL không đụng (BAL không có lệnh mua ngày Volume=0; trần BAL như pin).

## 3. Đo
4 chân pin (p30_pin0/p30_pin1M/p0_pin0/p0_pin1M) × {V1D, V1D0}: `METRIC cagr/sharpe_252/max_dd`, IS 2014-19 / OOS 2020+ CAGR từ
DAILY combined_nav (`v_metrics.py`). ΔCAGR/ΔSharpe/ΔMaxDD/ΔIS/ΔOOS so pin. Nhãn |ΔCAGR| vs sàn nhiễu **0,46pp** ở 4 chân (như
PREREG_V1 §3). Tách BAL/LAG: METRIC `final_nav_bal_ref_vnd` / `final_nav_lag_ref_vnd` (book ref) — mô tả, không cộng ra combined.
Đếm: lô LAG (holding_id), tổng giá trị mua LAG, `ABANDONED_REFUND`, `[V1D]` sell_deferred (phiên-lệnh) + số lô bị hoãn bán >5 và
>20 phiên, số lô còn kẹt cuối kỳ; % giá trị mua LAG còn lại ở ngày Volume=0 / vượt 20% giá trị khớp cùng ngày (chỉ đo mô tả,
dùng KL cùng phiên SAU KHI chạy — không đưa vào luật khớp).

## 4. Control + self-check
Cuối job: bản sao, mọi knob off ⇒ 4 md5 = 4707bcbe/bcd0469f/537e349b/a6ba34d8. Mọi run: `[selfcheck BAL/LAG] ... = 0 VND`.

## 5. Giới hạn
Volume_3M_P50 là trung vị 3 tháng tính cả ngày KL=0 — mã giao dịch <50% số phiên có ADV3M=0 dù có phiên khớp lớn ⇒ V1D là cận
BẢO THỦ (chặn cả lệnh có thể khớp được). Cận lạc quan nhân quả = V1E. Hoãn bán vô hạn có thể giữ lô quá hạn 25 phiên (khác live:
live có thể bán thoả thuận/khớp lẻ). Không mô hình slippage.
