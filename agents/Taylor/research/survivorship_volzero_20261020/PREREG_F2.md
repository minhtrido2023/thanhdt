# PREREG F2 — TÁCH TÁI PHÂN BỔ khỏi FILL-ARTIFACT — job Taylor_20261021_012028, EXPLORATORY
Không sửa pin/registry/pin_ledger/engine thật; chỉ bản sao `eng/`. Không đề xuất đổi luật. md5 + commit TRƯỚC khi chạy.

## 1. Câu hỏi
V1D tăng CAGR vì (a) vốn giải phóng quay sang sự kiện LAG khác hay (b) chặn ngày không giao dịch tự tạo lợi nhuận?
## 2. Cơ chế (đơn giản nhất của engine bản sao)
**Whitelist sự kiện của PIN**: chỉ cho phép book LAG xếp lệnh mua cho các sự kiện mà PIN đã thực sự bắt đầu khớp.
- Bước dump: chạy cấu hình PIN (mọi knob off) + `F2_DUMP=<file>` ⇒ ghi khoá `(tên simulate, ticker, exec_start_date)` của mọi lệnh LAG
  có `filled_shares>0` (cả lượt base lẫn chính). Ghi file phụ, KHÔNG đổi CSV ⇒ 4 run này cũng là control (md5 phải = 4 pin).
- `F2_WL=<file>`: ở bước 6 (xếp tín hiệu T+1) của simulate() tên `v23audit_LAG*`, tín hiệu có khoá KHÔNG thuộc whitelist ⇒ bỏ (không xếp).
  ⇒ vốn mà V1D giải phóng (lệnh không mua được ở ngày Volume=0/ADV3M<=0) KHÔNG thể sang sự kiện LAG ngoài tập pin; nó ở lại tiền
  mặt của book LAG và đi theo luật gửi/đỗ của engine (sweep 6b: p30 đỗ 30% tiền nhàn rỗi vào rổ ở NEUTRAL; p0 không đỗ; pin1M có lãi
  tiền nhàn rỗi). Slot trống cũng không bị sự kiện ngoài pin lấp.
- Biến thể: **F2** = V1D (`ZVF_MODE=block LIQ_ZERO_BLOCK=lag V1D_SELL=1`) + `F2_WL`. **F2C** (đối chứng cơ chế) = chỉ `F2_WL`, knob khác off:
  phải tái lập pin (kỳ vọng ≈ byte-identical; lệch ⇒ báo Δ F2C−pin là sai số cơ chế whitelist, trừ khỏi diễn giải).
- Kết hợp: phần đóng góp tái phân bổ ≈ Δ(V1D − F2); phần "chặn tự tạo lợi nhuận" ≈ Δ(F2 − F2C).
## 3. Đo
4 chân × {F2, F2C}: ΔCAGR/ΔSharpe/ΔMaxDD/ΔIS/ΔOOS so pin và so V1D, nhãn sàn 0,46pp, số lô LAG, lô whitelisted bị chặn (không khớp),
book ref BAL/LAG. Quy tắc đọc (khai trước): ΔCAGR(F2−pin) trong [−0,46; +0,46] hoặc âm ⇒ "chặn ngày không giao dịch không tự tạo lợi
nhuận"; dương >0,46 ⇒ phân rã phần dương (lô nào/năm nào, so lô pin cùng khoá).
## 4. Control + self-check: như PREREG_V1D §4.
## 5. Giới hạn
Lệnh trong whitelist có thể không xếp được nếu cùng mã đang bị giữ/hoãn bán (ngày tín hiệu khác) ⇒ thêm vốn ở tiền mặt (bảo thủ).
Khoá theo exec_start_date: tín hiệu lặp ngày khác của cùng sự kiện bị coi là ngoài tập.
