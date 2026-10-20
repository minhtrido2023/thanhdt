# PREREG V1E — Trần mua nhân quả = 20% × trung vị giá trị khớp N phiên trước — job Taylor_20261020_162558, EXPLORATORY
Không sửa pin/registry/pin_ledger/engine thật; bản sao `eng/`. Không đề xuất đổi luật. md5 + commit TRƯỚC khi chạy.

## 1. Câu hỏi
Cận nhân quả (không hindsight) cho V1B: thay trần 20%×ADV3M bằng trần chỉ dùng dữ liệu TRƯỚC phiên khớp, loại ngày KL=0 khỏi trung vị.

## 2. Định nghĩa (khai báo trước; N KHÔNG chọn theo kết quả — chạy CẢ HAI, báo cả hai)
- Giá trị khớp ngày `dv(tk,d) = Volume × COALESCE(Price, Close)` (VND thô, cùng cơ sở ADV của pin), từ
  `data/bq_cache_asof20260729_postrestate/ticker` (đúng cache pin).
- `cap_N(tk,t)` = 20% × trung vị `dv` trên các phiên có `Volume>0` trong **N dòng (phiên giao dịch của mã trong cache) liền TRƯỚC t**
  (không gồm t). Cửa sổ không có phiên Volume>0 nào ⇒ cap=0 (không khớp). Mã/ngày không có dòng nào trước t ⇒ cap=0.
- N ∈ {20, 60}. Biến thể `V1E20`, `V1E60` = `ZVF_MODE=block` (Volume=0 hôm nay ⇒ không khớp, như V1A/V1B) + trần MUA/ngày = `cap_N`
  THAY 20%×ADV3M (như V1B thay bằng KL cùng phiên). Áp mọi lệnh gọi `simulate()` có trần thanh khoản (cùng phạm vi V1B).
  Bán: như V1A (chỉ hoãn ngày Volume=0, không trần) — cặp đối chứng đúng của V1B.
- Knob bản sao: `ZVF_MODE=block_trail ZVF_TRAIL_N=<N>`.

## 3. Đo
Như PREREG_V1D §3 (4 chân, ΔCAGR/ΔSharpe/ΔMaxDD/ΔIS/ΔOOS, nhãn sàn 0,46pp, tách book ref BAL/LAG, đếm lô/refund/`[ZVF]` buy_capped,
% giá trị mua LAG ngày Volume=0 / vượt 20% giá trị khớp cùng ngày). Báo kèm khoảng [V1D … V1E] như dải capacity nhân quả, V1B là
cận hindsight.

## 4. Control + self-check: như PREREG_V1D §4.
## 5. Giới hạn
Trung vị loại ngày KL=0 phóng đại thanh khoản mã giao dịch thưa (đó là chủ đích: cận lạc quan nhân quả). N dòng cache ≠ N phiên
VNINDEX nếu mã thiếu dòng. Giá thô qua chia tách: giá trị khớp gần bất biến, chấp nhận.
