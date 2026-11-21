# README — fill_timing HYBRID OOS THẬT (06-15→11-18/2026) — job Taylor_20261119_051519 — CHƯA qua quant-skeptic

## 1. Kết luận: **KHÔNG ROLLBACK; edge BUY CHƯA XÁC NHẬN ở OOS (không đạt PASS, CHƯA ĐỦ N) → giữ lịch live, tiếp tục monitor**
- BUY block (11:00–13:30) vs open: **−12,0 bps, CI95 [−27,4; +2,8]** (110 phiên, 23 tuần, 16 mã). Cùng dấu và cùng bậc với recheck (−18,0), **xa ngưỡng rollback +22** ⇒ không rollback. Nhưng CI trên >0 ⇒ **không đạt PASS BUY** theo tiêu chí đã khoá (cần CI trên <0). Hạng mục: INCONCLUSIVE/CHƯA ĐỦ N (CI rộng gấp ~2,5 lần mẫu cũ vì chỉ 23 tuần).
- SELL block (09:15–10:00) vs open: **+1,2 bps [−4,2; +7,1]** — không đạt ≥+5 (như recheck: không chứng minh được "bán trong block tốt hơn bán ở open").
- Kỳ OOS thật là thị trường giảm: median 16 mã cộng dồn **−14,1%** (equal-weight median daily, proxy); 50,0% phiên là ngày giảm (recheck: 45%).
- Cảnh báo ex-post: "ngày giảm" xác định sau cuộc (median lợi suất ngày <0) ⇒ BUY −52,9 ở đó chủ yếu cơ học; ngày TĂNG BUY block **ĐẮT hơn open +28,9** [+8,8; +49,7]. Không dùng làm bộ lọc live. Trung bình BUY là đánh đổi phụ thuộc tỉ lệ ngày giảm.

## 2. Bảng (bps so với open ngày; BUY âm = tốt, SELL dương = tốt) — results_oos.csv
| Subset | BUY mean [CI95 tuần] | SELL mean [CI95] |
|---|---|---|
| Tất cả (n=110) | −12,0 [−27,4; +2,8] | +1,2 [−4,2; +7,1] |
| Ngày giảm (55) | −52,9 [−71,9; −35,7] | −14,6 [−20,3; −8,5] |
| Ngày tăng (55) | +28,9 [+8,8; +49,7] | +17,1 [+10,2; +24,6] |
| 5 mã thanh khoản thấp (D2D,NNC,DHA,HT1,VEA) | −10,1 [−23,9; +3,7] | +4,6 [−3,9; +13,2] |
| Nửa đầu 06-15→(55 phiên) | −13,3 [−40,1; +9,9] | +2,8 [−3,9; +9,3] |
| Nửa sau (55 phiên) | −10,7 [−25,9; +8,0] | −0,3 [−8,9; +9,2] |
Theo block (tất cả ngày): BUY 11:00 −9,4 [−23,6;+4,8] · 11:15 −13,2 [−29,2;+2,2] · **13:00 −16,8 [−34,5;−0,8]** · 13:15 −11,0 [−25,8;+4,1] · 13:30 −9,7 [−26,5;+6,2]. SELL 09:15 +0,6 [−0,2;+1,4] (≈ open) · 09:30 +6,3 [+0,3;+12,9] · 09:45 +1,3 [−6,5;+9,8] · 10:00 −3,3 [−12,6;+6,3]. Block 09:30 là block duy nhất SELL có CI dưới >0 — **1 trong 8 block, không hiệu chỉnh đa trị ⇒ không kết luận** (vì ngày tăng +19,7 / ngày giảm −7,1: cùng cơ học ex-post).

## 3. Dữ liệu & self-check
- Kéo: vnstock VCI 1m (`Quote().history`, 2026-06-12→11-18), 16 mã × 111 phiên, 0 lỗi/retry; `fetch_failures.json` rỗng; MD5SUMS_data.txt, thư mục `data/intraday_1m_ext_20261119/` (không đụng thư mục cũ). 1m cũ chỉ tới 06-12 nên không có trường hợp chồng >1 ngày. Không thử 15m (1m có đủ).
- **Kiểm khớp 06-12: timestamp + volume khớp 100% ở 16 mã; giá open/close: 5 mã khớp tuyệt đối, 11 mã lệch bởi HỆ SỐ NHÂN HẰNG (điều chỉnh corp-action sau 06-12 của VCI, vd PHR ×0,543, PVD ×0,599, SSI ×0,799, D2D ×0,831)** — không phải lệch dữ liệu; metric là tỷ số trong ngày nên bất biến. Tôi diễn giải "lệch thì dừng" theo đúng ý này (đã khai ở PREREG_OOS); nếu Mike muốn dừng cứng theo chữ thì báo lại.
- Control: metric 06-12 trên bản cũ vs bản mới, 13 mã (D2D/DHA/NNC <50 bar bị loại như engine): |Δ| buy/sell tối đa 1,7 bps, trung bình toàn cột 0,43 (max 5,46 ở 1 cột block lẻ) — selfcheck_0612_old_vs_new.csv. Nhiễu tick trên giá đã điều chỉnh thấp (PVD ~18, PHR ~35) ≲ ~3 bps/bar, không thiên lệch có hệ thống.
- Engine NGUYÊN `../fill_timing_recheck_20261119/engine.py` (import, không sửa), tiêu chí PREREG gốc; PREREG_OOS.md md5 acffe4d82adb6c8f91378fd035d37072 khoá TRƯỚC khi tính. Số phiên mong đợi 110 = thực tế 110. 1475 ticker-ngày (12–16 mã/ngày; mã thưa D2D/DHA/NNC rụng ngày <50 bar).

## 4. Journal fill thật (mô tả, KHÔNG suy edge) — real_fills_postjun12.csv, fills_table.py
Lọc account_no (0002023347 SpaceX / 0001743768 ZaloPay), dedupe theo order id, lệnh có fillQuantity>0, 07-01→11-16, 54 phiên, 674 lệnh. Phân bố theo GIỜ ĐẶT lệnh (không phải giờ khớp; journal chỉ có modifiedDate):
| | <09:30 | 09:30–10:59 | 11:00–11:59 | 13:00–13:29 | 13:30–14:29 | ≥14:30 |
|---|---|---|---|---|---|---|
| SpaceX BUY (176) | 55 | 55 | 27 | 21 | 18 | 0 |
| SpaceX SELL (221) | 86 | 95 | 3 | 17 | 17 | 3 |
| ZaloPay BUY (109) | 25 | 25 | 27 | 19 | 13 | 0 |
| ZaloPay SELL (168) | 71 | 75 | 2 | 6 | 12 | 2 |
Nhận xét mô tả: >60% BUY đặt trước 11:00 (không phải 5 block lịch HYBRID) ⇒ lịch live không phải toàn bộ hành vi thực; chỗ này cần Mafee xác nhận lệnh nào thuộc lịch HYBRID. Chưa tính fill-vs-open: giá ext đã điều chỉnh corp-action, giá khớp thật chưa điều chỉnh ⇒ cần bảng open chưa điều chỉnh (BQ `ticker.Price`) — chưa làm; N theo mã nhỏ.

## 5. Caveat
- 23 tuần ⇒ CI tuần thô; 16 mã thanh khoản tương đối cao; ước lượng fill = open bar phút (không mô hình hàng đợi/khối lượng, không phí 0,097%/chiều — triệt tiêu giữa lịch). Panel 15m 335 mã không mở rộng. Chưa qua quant-skeptic.
- Đề xuất: giữ lịch live; chạy lại PREREG này khi đủ ≥ ~12 tháng OOS hoặc dùng fill thực (Mafee) để đối chiếu.
