# DRI định giá vòng 4 — đường sản lượng từ dữ liệu công bố (PREREG, job `Taylor_20261027_123420`)

> READ-ONLY, paper. Commit file này TRƯỚC khi chạy `model.py`. Gốc: r3 (`../dri_val_supply_adj_r3_20261027/`, commit ad45d904e).
> Việc r4: THAY đường sản lượng của r3 (14.000 t tới 2029, −2%/năm từ 2030, tới 2054) bằng đường dựng từ diện tích/năng suất
> công bố + lịch thanh lý/tái canh. GIỮ NGUYÊN mọi trục khác của tâm r3: mid RSS3 {1,865; 1,97; 2,075; 2,18}, C_ref = C_cal
> (thuế 9T), k chọn bằng backcast, f 0,5, thuế 19,58%, KTPL 10,6%, w 10%, quỹ Lào giữ tới 2054, h 15%, TDND 0, X 1.717, Q4 Base,
> khung thực r_dn 12%, trọng số PEAK/MID 60/40, FCF = 0,9 × LN lõi.
> Nhãn: [BCTN25] BCTN 2025 (số trang = trang PDF; md5 15e594db…) · [BCTN24] BCTN 2024 (NQ HĐQT trích trong BCTN) · [BCTC3] BCTC HN Q3/26
> · [SXKD] · [UL] giả định chưa có nguồn · [NỀN] hiểu biết ngành · [SL] suy luận từ số công bố.

## 1. Dữ liệu dùng (đã đọc trước khi khai lưới — khai thật để skeptic biết)
| Dữ liệu | Số | Nguồn |
|---|---|---|
| KH 2026 khai thác / năng suất | 13.800 t / 1,69 t/ha ⇒ diện tích cạo 8.165,7 ha [SL] | [BCTN25 tr.46] |
| KH 2026 GVHB / giá vốn BQ / tiêu thụ | 1.430 USD/t (trước thuế) / 1.759 USD/t / 16.900 t | [BCTN25 tr.46] |
| 2025 khai thác / năng suất | 15.152,83 t / 1,81 t/ha ⇒ 8.371,7 ha [SL] | [BCTN25 tr.20, tr.40] |
| 2024 khai thác / năng suất; 2023 năng suất | 11.116 t / 1,34 t/ha; 1,63 t/ha | [BCTN24] |
| Diện tích cao su quản lý | 8.592,3 ha (tổng 9.276,07 ha) | [BCTN25 tr.20] |
| Diện tích kinh doanh | 8.299,83 ha (EUDR); FSC 6.148,03 = 74,07% | [BCTN24]; [BCTN25 tr.6,10] |
| KH 2025 (NQ 12/NQ-HĐQT 31/12/2024): cao su 8.588,69 ha = KTCB 387,03 + khai thác 8.201,66 | | [BCTN24 tr.56] |
| Chi phí KTCB cao su KH 2025 | 9.542,65 tr / 387,04 ha = **24,655 tr/ha/năm** | [BCTN24 tr.57] |
| Vườn ươm 80.000 stump cho tái canh 2025 | 1.225,14 tr LAK | [BCTN24 tr.55] |
| Tái canh: 2025 thanh lý 94,56 ha để tái canh cao su; 2026 tái canh 37,77 ha; dự án tái canh 4.081,64 ha (NQ 01/2025) | | [BCTN24 tr.55; BCTN25 tr.46, 49, 57] |
| Thanh lý hàng loạt chờ liên doanh nhà máy gỗ/viên nén; giá sàn gỗ NQ 12/2025 (không công bố số) | | [BCTN25 tr.39, 49, 59] |
| 2015: 80% diện tích đã vào khai thác | | [BCTN25 tr.6] |
| Tầm nhìn 2054; lộ trình "phù hợp thời hạn tô nhượng"; thoả thuận 19/11/2004 | thời hạn văn bản CHƯA thấy | [BCTN25 tr.26, 49] |
| Cam kết khoanh nuôi tái sinh rừng phần đất quy hoạch Rừng bảo tồn Đông Huê Sáo khi hết chu kỳ 1 | diện tích không công bố | [BCTN25 tr.35] |
| Mua ngoài 2.000 t/2026 "bù thiếu hụt khi vườn đi vào lộ trình thanh lý" | | [BCTN25 tr.47, 50] |
| Khấu hao vườn tiếp tục để GTCL khi thanh lý ~0 (xin Lào cho trích hợp lý) | | [BCTN25 tr.58] |
| Dừng mua bảo hiểm vườn từ 2026 | | [BCTN25 tr.59] |
| Vườn cây lâu năm 30/09/26: NG 567,43 tỷ; HMLK 316,69 tỷ; GTCL 250,74 tỷ; KH 9T 26,20 tỷ | | [BCTC3 tr.21 bảng 5.8] |
| Quỹ đầu tư phát triển 30/09/26 (BCTN: trích quỹ ĐTPT "nhằm đảm bảo kế hoạch tái canh") | 96,97 tỷ (01/01: 61,94) | [BCTC3 mã 418; BCTN25 tr.51] |
| Sầu riêng Lào 238,12 ha tới 2030 (30,48 ha 2025, 60,66 ha 2026); suất ĐT trồng mới 178,52 tr/ha | | [BCTN25 tr.6, 26, 46, 49; BCTN24 tr.54, 57] |
| Sầu riêng CNC 2026 KH: 760 t, 40.000 đ/kg, giá vốn 31.419 đ/kg; diện tích 142,17 ha | | [BCTN25 tr.46; BCTN24 tr.56] |

**KHÔNG có trong tài liệu đã đọc:** bảng diện tích theo năm trồng; phương pháp/thời gian khấu hao vườn; văn bản thời hạn tô nhượng;
dự toán vốn dự án 4.081,64 ha; lịch thanh lý theo năm; giá sàn gỗ.

## 2. Phân bố tuổi vườn [SL, khoảng bất định]
- Năm BẮT ĐẦU CẠO của diện tích chu kỳ 1: 80% đều trên 2011–2015, 20% đều trên 2016–2018 (từ "2015: 80% đã khai thác"; trồng
  ~2004–2011 nếu KTCB 7 năm). Bất định ±2 năm — không đưa vào lưới, chỉ ảnh hưởng qua trục L_tap (cùng chiều).
- Kiểm chéo (in ra, không chỉnh tham số): HMLK/NG vườn 55,8% và tốc độ KH 9T ⇒ số năm còn lại tới GTCL 0.

## 3. Đường sản lượng (tự khai thác, tấn khô)
- 2026 = 13.800 (KH). Diện tích cạo gốc A0 = 13.800/1,69 = 8.165,7 ha; năng suất gốc Y0 = 1,69.
- Chia A0 thành 2 khối: **khối tái canh** R = 4.081,64 − 94,56 − 37,77 = 3.949,31 ha (giả định [UL]: 132,33 ha 2025–26 thuộc dự án)
  và **khối còn lại** A0 − R.
- Khối tái canh: thanh lý đều 8 năm bắt đầu từ năm s; năm thanh lý không cho mủ cũ; cây mới cho mủ từ L+7 (KTCB 6 năm sau năm trồng
  L), năng suất mở cạo năm 1/2/3 = 0,9/1,2/1,5 rồi 1,69 phẳng [UL/NỀN]. 94,56 ha (2025) và 37,77 ha (2026) mở cạo 2032 / 2033.
- Khối còn lại: mỗi cohort (theo năm bắt đầu cạo §2) bị thanh lý KHÔNG tái canh ở năm (bắt đầu cạo + L_tap).
- Năng suất cây cũ (cả 2 khối khi còn cạo): Y0 tới 2029, −2%/năm từ 2030 — GIỮ ĐÚNG lão hoá tâm r3 (d 2%, d0 2030).
- **3 đường đối xứng theo tốc độ thanh lý/tái canh** (L_tap = 27 ở cả 3):
  - NHANH: s = 2027 (thanh lý/tái canh 2027–2034)
  - TRUNG BÌNH: s = 2029 (2029–2036)
  - CHẬM: s = 2031 (kẹt đối tác gỗ tới 2030; 2031–2038)
- Trục phụ L_tap ∈ {22; 27; 32} năm cạo (tâm 27) [NỀN: đời kinh tế cao su ~25–30 năm cạo; UL].
- Chi phí cố định: GIỮ hàm r3 cost(P,V) = (C_ref + k(P−P25)) × ((1−f) + f×V0/V), V0 = 14.000 (tâm). Biến thể báo riêng: phần cố
  định co theo diện tích cạo (f áp lên V0/V × A(y)/A0).

## 4. Tái canh, quỹ ĐTPT, mua ngoài, sầu riêng
- Capex tái canh/ha = m × 24,655 tr (năm-chăm-sóc KTCB tương đương), rải đều 7 năm L..L+6; m ∈ {4; 7; 10} (tâm 7) [UL đối xứng,
  neo đơn giá công bố]. Tiền 2025 thực. Trừ vào FCF cổ đông × (1 − w) (chi tại Lào làm giảm lợi nhuận chuyển về). Không lá chắn thuế.
  Không tính tiền thu gỗ thanh lý (giá không công bố) — ghi caveat.
- Rủi ro chồng: FCF r3 đã trừ 10% "tái đầu tư" (0,9 × LN lõi). Báo biến thể cận trên: capex tái canh THAY 10% đó (0,9 → 1,0).
- Quỹ ĐTPT 96,97 tỷ: là quỹ trong VCSH, tiền tương ứng đã nằm trong tiền ròng ⇒ tâm KHÔNG trừ (capex đã trừ ở dòng tiền).
  Biến thể theo đề bài: coi quỹ là tiền bị khoá cho tái canh ⇒ trừ 96,97 tỷ khỏi tiền ròng VÀ giảm capex tương ứng (đầu tiên, danh
  nghĩa) — chênh = giá trị thời gian. Biến thể "trừ thẳng không giảm capex" in ra kèm nhãn ĐẾM HAI LẦN.
- Mua ngoài 2.000 t/năm 2027–2054: biên gộp m_b ∈ {0; 1,5; 3,0} tr/t [UL], qua thuế + rò rỉ như LN lõi. BÁO RIÊNG, không vào tâm.
- Sầu riêng 238,12 ha: dòng chỉ báo RIÊNG [UL], không vào tâm, không bù cao su.

## 5. Bảng ra (cam kết)
1. Selfcheck: tái lập 10.878/11.031, 14.301, r2 hàng 60/40, **r3 tâm 10.521/11.863/13.206/14.548** bằng hàm sản lượng r3; in thêm
   đường phẳng 14.000 tới 2054 làm mốc; kiểm 13.800/1,69 = diện tích; in đường sản lượng 3 path theo năm.
2. FV/cp 3 đường × 4 mid (tâm L_tap 27, m 7), 60/40; kèm 14.700/14.400 so FV.
3. Lưới 3 đường × 3 L_tap × 3 m (27 ô) × 4 mid: min/trung vị/max.
4. Cầu nối r3 → r4 từng bước (mỗi mid riêng, KHÔNG ghép mid).
5. Biến thể: quỹ ĐTPT, capex thay 10%, chi phí cố định theo diện tích; dòng riêng mua ngoài và sầu riêng.
6. Ngưỡng giá biên an toàn ≥15% = FV/1,15 cho từng đường × mid.
Không sửa tham số sau khi xem kết quả; mọi thứ thêm sau gắn nhãn POST-HOC.
