# PREREG F1 — V1D có TRẦN THỜI GIAN HOÃN BÁN — job Taylor_20261021_012028, EXPLORATORY
Không sửa pin/registry/pin_ledger/engine thật; chỉ bản sao `eng/` (+`eng_dep1m/` symlink). Không đề xuất đổi luật.
Viết + md5 + commit TRƯỚC khi chạy. Lỗ hổng skeptic (logs/verify_20261020_180301_118003.log): V1D hoãn bán VÔ HẠN, lô kẹt giữ giá cũ.
Nguồn dữ liệu: cache pin `data/bq_cache_asof20260729_postrestate/ticker` (registry `price-volume/ticker_ohlcv_tables.md` CANONICAL lịch sử).

## 1. Biến thể (khai báo trước, chạy ĐỦ lưới, không chọn theo kết quả)
Nền = V1D (`ZVF_MODE=block LIQ_ZERO_BLOCK=lag V1D_SELL=1`, như PREREG_V1D). Knob bản sao mới `F1_N`, `F1_H`:
- Mỗi lệnh bán T+1 Open (mục `pending_exits`) mang bộ đếm `_f1d` = số phiên ĐÃ bị hoãn vì ZVF (Volume=0) hoặc V1D (ADV3M<=0/thiếu).
  Hoãn vì THIẾU GIÁ (engine gốc) không đếm, không ép (không có giá để khớp — giữ như pin).
- Khi lệnh bị chặn lần nữa mà `_f1d >= N` ⇒ **ÉP BÁN** ngay phiên đó, toàn bộ lô, giá = `open_px × (1 − H)` (`open_px` = giá engine dùng
  phiên đó, tức giá tham chiếu cũ), phí bán như engine; ghi TX `reason=<lý do>_F1FORCE`. Tức lô bị hoãn N phiên, phiên N+1 bị ép.
- Áp cho MỌI book có lệnh bị hoãn (BAL bị ZVF hoãn, LAG bị ZVF+V1D hoãn) — chặn giá cũ ở cả hai; báo số lô ép bán theo book.
- Lưới: N ∈ {5, 20} × H ∈ {0,10; 0,30} ⇒ `F1_N5H10, F1_N5H30, F1_N20H10, F1_N20H30` × 4 chân = 16 run.
- **Lô còn kẹt cuối kỳ** (lệnh bán đang hoãn `_f1d>0`, tối đa N phiên) — engine vẫn mark theo Close; hạch toán HẬU KỲ 2 cách:
  (a) giá 0, (b) chiết khấu H. combined_nav phiên cuối điều chỉnh = combined − cap_book × (giá trị lô kẹt book ref / nav book ref) × w,
  w=1 (a) hoặc H (b), theo từng book (BAL/LAG). CAGR điều chỉnh từ DAILY (cùng công thức v_metrics). Engine in `[F1] stuck_end`.
## 2. Đo
4 chân × 4 cấu hình: ΔCAGR/ΔSharpe/ΔMaxDD/ΔIS 14-19/ΔOOS 20+ so PIN và so V1D (run V1D cũ `vz_V1D_*`); nhãn |ΔCAGR so pin| vs sàn 0,46pp;
số lô ép bán (BAL/LAG); CAGR điều chỉnh (a)/(b). Book ref BAL/LAG mô tả.
## 3. Control + self-check: như PREREG_V1D §4 (4 md5 4707bcbe/bcd0469f/537e349b/a6ba34d8; mọi run `[selfcheck BAL/LAG] = 0 VND`).
## 4. Giới hạn
Giá ép bán = giá cũ × (1−H) là giả định (thoả thuận/khớp lẻ), không đo được; H chỉ là 2 điểm. Lô ép bán vào ngày Volume=0 vẫn là
"khớp ngày không giao dịch" có chiết khấu — đó là chủ đích (cận phạt). Không slippage.
