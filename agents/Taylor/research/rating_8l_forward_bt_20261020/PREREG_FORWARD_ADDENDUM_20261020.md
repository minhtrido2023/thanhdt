# PREREG_FORWARD — ADDENDUM 2026-10-20 (không sửa PREREG gốc)

PREREG_FORWARD.md (md5 `4ad20803a74b046af74a9b128085019c`) và `event_study_v2_frozen.py`
(md5 `a857d81bfc95be8b7dac507f6cf9dbad`) KHÔNG đổi. Addendum này viết và commit TRƯỚC khi có bất kỳ CAR nào
được tính (lúc viết: `data/rating_8l_forward_car.csv` chưa tồn tại). Tracker kiểm md5 addendum lúc khởi động
như hai file trên (lệch ⇒ dừng, không ghi ledger).

## (i) Lô bootstrap 295 sự kiện
Lần chạy đầu (`first_seen` 2026-10-20T13:01:02+0700) ghi 295 sự kiện eff > 2026-07-31 đã tồn tại sẵn, trong đó
**11 G1** (đo từ `data/rating_8l_forward_events.csv`: G0 258 · G1 11 · G2 11 · G3 15). Lô này không phải
"quan sát đi tới" thuần: rating đã được biết trước khi PREREG forward có hiệu lực. Khai trước:
- Mọi kết luận báo cáo **CẢ HAI** bản: (A) tính cả lô bootstrap, (B) loại lô bootstrap
  (`first_seen` == 2026-10-20T13:01:02+0700).
- **Kết luận chính dùng bản (B)** nếu (A) và (B) khác dấu hoặc khác phía ngưỡng PREREG §3; nếu cùng dấu
  và cùng phía ngưỡng thì nêu rõ hai bản nhất quán.

## (ii) Vendor sửa lùi Release_Date sau lần thấy đầu
Ledger giữ `eff_date` ghi lúc thấy đầu (append-only, không sửa). Khi review, dựng lại eff từ `ticker_financial`
hiện hành; sự kiện nào eff dựng lại ≠ eff trong ledger bị **rớt khỏi kết luận** và **số rớt được ĐẾM và báo kèm**
(theo nhóm G0–G3), không âm thầm bỏ.

## (iii) Vai trò của CAR trong ledger
`data/rating_8l_forward_car.csv` là số **mô tả** (lịch = phiên có ≥100 mã có giá, benchmark B3 như event study
v2). Kết luận chính luôn **chạy lại bằng code frozen** (`event_study_v2_frozen.py`), không đọc thẳng từ ledger.
