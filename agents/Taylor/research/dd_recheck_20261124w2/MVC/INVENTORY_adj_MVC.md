# INVENTORY_adj_MVC — kiểm kê E17 KHOÁ TRƯỚC khi tính (job Taylor_20261124_131351, 24/11/2026)
Theo PREREG_adj.md (ef5157cb…) + PREREG_adj_v2.md (835dfc1e…). MÙ GIÁ khi dựng. Tâm gốc = 16.241 (r3 sổ rev9, recheck không đổi tâm; = center LEDGER_PROPOSAL_MVC rev10).
Nguồn: S = `skeptic/r1_raw.md`; I = `calc/calc_items_out.json`; NQ = `dd_MVC_20261103/txt/VI_BienBanHopDaiHoiDongCoDongThuongNien2026VaNghiQuyet.txt` (khôi phục /tmp/ddrestore_MVCw2).

## Vào tâm
| # | Hạng mục | Hướng | Bậc | p (nhánh thang) | m |
|---|---|---|---|---|---|
| 1 | Trích quỹ 11% LNST hằng năm (KTPL 7% + HĐQT/BKS 2% + BĐH 2%, NQ:767-785) — flow, khác tồn KTPL 6,52 tỷ đã trừ | xuống | C+ (dấu chắc chắn: NQ đã thông qua 100%; năm 2025 đã trích 10% trên LNST riêng 122,52 tỷ, NQ:725-745) | 0,50 [0,25; 0,75] — thang B, 1 kỳ báo cáo có số (2025) | cận bảo thủ = 11% × LNST riêng 2025 122,52 tỷ, phẳng, trả 2027…2035 (9 lần, trục GP Tân Lập ngắn nhất), chiết khấu r 13,5%, × hệ số sở hữu chéo 1,04755 / tâm trước CK 17.704; cận cao = I.m_cons + I.m_9t26 (−6,10%). KHÔNG dùng −10,13% (cơ sở có lãi LK; quỹ trích trên LNST riêng — S điểm 3) |
| 2 | Truyền dẫn tâm điều chỉnh NNC (`dd_adjcenter_20261124/NNC/adj.json` md5 6beb796c…, bỏ #4 chân MVC) qua stake 44,07% | xuống | kế thừa (p đã nằm trong adj NNC) | 1,0 [1,0; 1,0] | I.nnc_flow: −1,422% [−4,748; +0,091] |

Chống đếm hai lần: #1 cận bảo thủ trên LNST riêng (chỉ cổ tức NNC về) ⇒ không trùng #2 (quỹ của chính NNC nằm trong adj NNC). Tồn KTPL 6,52 tỷ (stock) đã trừ trong NETFIN; #1 là flow. Cổ tức 2025 600 đ (60 tỷ) đã trừ trong NETFIN (cổ tức phải trả V.19) ⇒ cơ học = 0.

## Chỉ độ nhạy (không vào Σ)
- C: Cụm công nghiệp ≤500 tỷ, NPV = 0 theo luật house 03/11 ("DD dự án mới: base = sổ sách/NPV 0", cấm suy "đầu tư mới ⇒ giảm giá trị" khi không có cơ sở độc lập). Không có kế hoạch/giá trong tay ⇒ C hai chiều. Độ nhạy: mỗi 10% hao hụt NPV trên 500 tỷ.
- C: Ký quỹ PHMT/đóng mỏ chưa đọc; tham chiếu NNC 4,50 tỷ (cận trên không chiết khấu).
- C (lên): biên Tân Lập 38% / mỏ mới kịch bản tốt / upside 2034 — không có dữ kiện mới (S symmetry).
- [LUẬT] CK holding 20% (dải 0…+20% user chốt 24/11; base 0%): −7,26% trước CK.
- [LUẬT] r 13,5% vs dải Ke (E15): @12,3% +3,20%; β = 1.
- Hạn GP Tân Lập: đã nằm trong lưới (trục 2035/W/2045) ⇒ không phải hạng mục.
