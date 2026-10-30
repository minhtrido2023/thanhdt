# SELFCHECK — DGC DD bản 2.2 (job Taylor_20261030_094438, 30/10/2026)

## 1. Grep khách quan — RỖNG
`grep -n -E "QUALIFY|AMBIGUOUS|NON|fear|§2\.5|SpaceX|ZaloPay|Taylor|Bobby|skeptic" <md> <html> figs/*.csv` → 0 hit.
Bản không phân biệt hoa/thường + `\bMike\b|Wendy|Spyros|Winston|Mafee|DollarBill|sợ hãi|đang nắm giữ` → 0 hit.
Ke 14,9 chỉ còn ở ngữ cảnh đối chứng/lịch sử (mục 8b dòng "Bản 2.1 dùng…", Phụ lục E); 15,8% chỉ kèm "góc nhìn nước ngoài".

## 2. Tái lập số ở 2 múi giờ (`env -u TZ TZ=Asia/Ho_Chi_Minh` và `TZ=UTC`, $DNA_PYEXE)
Trong `../../dgc_ke_domestic_20261030/`:
- `ke_sens.py`, `grid_ke.py`, `margin_ke.py`: rc 0 ở cả 2 TZ; `out_ke_sens.csv`, `out_grid_ke.csv`, `out_margin_ke.csv` trùng byte bản đã dùng (cmp); mọi CSV trong `r10_at_ke*/` trùng md5.
  Các script tự assert đối chứng Ke 14,9: A7/B7 = 32.182/37.060, biên ±2pp 29.345/35.017.
- `rerun_r12.py` (TZ=UTC): Ke 12,5/13,0/13,5/14,9 rc 0; "đối chứng Ke 14,9: 18 file, lệch: []" (18/18 out_r10_/r11_/r12_*.csv trùng byte r12).
- `build_report.py` chạy lại trong bản sao tạm (đường dẫn tương đối qua symlink) ở cả 2 TZ: md trùng byte, mọi `figs/*.csv` trùng; PDF 24 trang.

## 3. Số then chốt (mốc 13,0; khoảng 12,5–13,5) — từ `out_ke_sens.csv`
A7 33.514 (33.118–33.951); B7 38.832 (38.305–39.414); kịch bản A7 46.197/35.159/22.316; ô thấp nhất lưới A7 27.003 (26.739–27.293);
tỉ trọng terminal/giá trị hoạt động 0,592 (0,578–0,607), /DCF 0,34; RONIC = Ke: A7 +74/+135/+185. Đối chứng 14,9 = 32.182/37.060.

## 4. Pháp lý — nguồn đã mở 30/10
Xem CHANGELOG #5–#8. Chưa xác minh: thông cáo gốc Bộ Công an (tách 25/12/2025 vs 14/03/2026), trang thông báo HOSE sau 06/10, ý nghĩa mã `RES` theo bảng mã sàn.

## Giới hạn
Phần sửa 2.2 chưa được người phản biện rà (rev2: chưa rà lại). Không gửi email; subject gợi ý `EMAIL_SUBJECT_v22.txt`.

## rev2 sau fundamental-skeptic 30/10 (job Taylor_20261030_102330)
- Grep khách quan sau sửa (md, html, figs/*.csv, EMAIL_SUBJECT_v22.txt): `QUALIFY|AMBIGUOUS|\bNON\b|fear|§2\.5|SpaceX|ZaloPay|Taylor|Bobby|skeptic|Mike|Wendy|Spyros` → 0 hit; `Winston|Mafee|DollarBill|sợ hãi|đang nắm giữ` → 0 hit (md).
- Số tính lại bằng lệnh (python -I, từ `out_*.csv`), không đổi số mô hình: 33.300/33.951−1 = −1,92%; /33.514−1 = −0,64%; /33.118−1 = +0,55%; 32.900/A7 = −3,1% … −0,7%.
  B7 dịch so bản 2.1 (37.060): 38.305−37.060 = +1.245; 39.414−37.060 = +2.354; A7: +936 … +1.769.
  Ngưỡng biên: (A7−32.900)/(A7−A7[−1pp]) = 0,675pp (12,5%: 33.951, 32.393) và 0,146pp (13,5%: 33.118, 31.626) — `out_margin_ke.csv`.
  Dự phòng 100 tỷ × 4 quý, A7 (`r10_at_ke*/out_r10_finite_N.csv`, N=4, x=100): Ke 12,5% q4ex 33.194 / sau lá chắn 33.389, "old" 32.977 / 33.172; Ke 13,5% q4ex 32.368 / 32.561, "old" 32.150 / 32.343.
  3.019 − (−228) = 3.247; 33.514 − 32.760 = 754; 33.731 − 32.760 = 971; 33.731 − 32.954 = 777; 0,34/3 = 0,113; 3.188,97 − 3.025 = 163,97.
  Justify: `erp_domestic_20261030/out_justify_grid.csv`, non_bank, g 5,5: pct_rich 78,2 (Ke 15) / 69,7 (Ke 13).
- Dựng lại: `build_report.py all` rc 0; md → html/pdf 25 trang; `figs/*.csv` hero/football tái sinh; banner dựng bằng `make_title_banner.py`. Chưa chạy lại ở 2 múi giờ (rev2 không chạm mô hình; script chỉ đổi chú thích/tiêu đề).
- Lưu ý đọc: các cột "q4ex" và "old" của dự phòng 4 quý khác nền (q4ex = tách ~100 tỷ ngầm Q4, nền của bảng §9; "old" = giữ ngầm, nền A7 chính); cả hai đều trên 32.900 ở Ke 12,5%.
