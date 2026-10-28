# PREREG V3A' — V3A với state(t-1) nhân quả lúc Open — job Taylor_20261020_162558, EXPLORATORY
Không sửa pin/registry/pin_ledger/engine thật; bản sao `eng/`. KHÔNG kết luận đổi luật. md5 + commit TRƯỚC khi chạy.

## 1. Lý do
V3A huỷ lệnh LAG chưa khớp nếu `state_by_date[today]==2` — state cuối ngày, chưa biết lúc khớp T+1 Open (skeptic: ~18 lệnh ngày đầu
sau BEAR bị huỷ oan; 0 lệnh ngày đầu BEAR được lợi).
## 2. Biến thể `V3_MODE=noentry_bear_t1`
Như V3A nhưng dùng state của phiên VNINDEX liền trước (`vni_dates[i-1]`); phiên đầu tiên (i=0) không huỷ. Phạm vi: chỉ `simulate()`
name bắt đầu `v23audit_LAG` (base + chính), như V3A.
## 3. Đo
4 chân: ΔCAGR/ΔSharpe/ΔMaxDD/ΔIS/ΔOOS so pin; `[V3]` entry_dropped; so ΔCAGR từng chân với V3A (+0,32/+0,41/+0,48/+0,52).
Nhãn sàn 0,46pp; nêu rõ nhãn có đổi so V3A ("vượt sàn ở 2/4 chân") không.
## 4. Control + self-check: như PREREG_V1D §4.
## 5. Giới hạn: như PREREG_V3 §5 (≈1 giai đoạn BEAR, mô tả, không edge).
