# README — fill_timing HYBRID: lệnh thật thuộc lịch nào + fill-vs-open thật — job Taylor_20261119_052911 — CHƯA qua quant-skeptic

## 1. Kết luận
- **HYBRID KHÔNG điều khiển phần lớn lệnh BUY trong journal 07-01→11-16.** BUY 285 lệnh: **207 (72,6%) đặt trong 07-01→08-17 (trước ngày bật cờ 08-26), khi cả hai cổng `fill_timing_live_gate` và `fill_timing_hybrid_live_gate` còn True ở mode live ⇒ layer fill-timing TẮT, lệnh đặt đồng đều từ mở cửa** (config.py:153,157; executor.py:1763-1769; commit 9be375a44 đổi cờ 2026-08-26). **100% BUY đặt <11:00 (160 lệnh = 56,1% BUY) nằm ở giai đoạn này**; từ khi HYBRID live (fill đầu 09-14) **không có BUY nào đặt <11:00**. Số "hơn 60%" trong README OOS đo lại = 56,1% (160/285).
- Sau HYBRID live: BUY chỉ **78 lệnh / 10 ngày** (70 trong block, 8 ngoài block sau 13:45). Quá ít để kết luận.
- **Monitor "fill-vs-open >+22 bps rollback" đo gì?** Nếu quét toàn bộ fill BUY thì ~73% mẫu là hành vi UNIFORM trước HYBRID ⇒ nó đo một hỗn hợp, không đo HYBRID. Chỉ nhóm "BUY thuộc HYBRID" (78 lệnh, 29 mã-ngày) mới liên quan, và nhóm đó **không đủ N**. (Tôi không đọc code monitor; kết luận này chỉ theo phân bổ dữ liệu.)
- fill-vs-open thật (bps, BUY âm tốt / SELL dương tốt): **chỉ có 1 nhóm đủ N: SELL trong block, −6,1 bps [−17,9; +21,6]** (115 mã-ngày, 8 tuần) ⇒ không phân biệt được với 0. Nhóm BUY HYBRID **không đủ N** (22 mã-ngày/4 tuần): mean −56,1 bps — **chủ yếu do 18/22 mã-ngày là ngày giảm** (−110,6 vs ngày tăng +189,3, n=4). Không so được với ngưỡng +22: mean −56 dưới ngưỡng, nhưng không có CI ⇒ **không kết luận rollback hay PASS**.

## 2. Phân loại (orders_classification.csv; 674 lệnh, lọc account_no, dedupe (account,id), join journal PLACE theo child_oid, 669/674 khớp)
| Nhóm | BUY | SELL | Lý do + code |
|---|---|---|---|
| PRE_HYBRID_UNIFORM (07-01→08-17) | 207 | 95 | gate True ⇒ layer tắt; note "ft:in-window" chỉ là nhãn mặc định `executor.py:2208`; cờ `config.py:153,157` (trước 9be375a44) |
| HYB_IN_BLOCK (09-14→11-16) | 70 | 250 | HYBRID live, đặt trong block `executor.py:1640-1646,1692-1714,2203-2206` |
| HYB_OUT_OF_BLOCK | 8 (13:52–14:24) | 39 (10:21–14:28) | blocks_left=0 ⇒ `_hybrid_defer` không hoãn, phần dư chạy nhịp thường `executor.py:1716-1735,1737-1762` |
| NO_JOURNAL (không có PLACE) | 0 | 5 | 4 ATC 14:30 + 1 LO 14:43 (quét cuối phiên) |
Giờ đặt (BUY): <09:30 80, 09:30–10:59 80 — tất cả PRE_HYBRID. Không có fill nào trong 08-18→09-13 (journal không có PLACE khớp trong khoảng này, mô tả; không điều tra thêm). Không thấy bằng chứng bypass urgency/gap/EXTREME trong journal (chỉ 0 note GAP_OVERRIDE); không suy thêm.

## 3. Bảng bps so với OPEN CHƯA ĐIỀU CHỈNH (results_bps.csv)
Open chưa điều chỉnh = `ticker.Open × Price/Close` (BQ, Open/Close điều chỉnh, Price chưa; 0 thiếu). Đơn vị = mã-ngày-chiều (qty-weighted); CI = bootstrap khối tuần, chỉ khi ≥30 đơn vị và ≥8 tuần.
| Chiều/nhóm | lệnh | mã-ngày | ngày | tuần | mean bps | median | CI95 |
|---|---|---|---|---|---|---|---|
| BUY HYB_IN_BLOCK | 70 | 22 | 10 | 4 | −56,1 | −86,9 | không đủ N |
| BUY HYB_OUT | 8 | 7 | 5 | 4 | −68,5 | −31,9 | không đủ N |
| BUY PRE_HYBRID (uniform) | 207 | 89 | 23 | 7 | +16,5 | +9,2 | không đủ N (7 tuần <8) |
| SELL HYB_IN_BLOCK | 250 | 115 | 20 | 8 | −6,1 | −1,5 | [−17,9; +21,6] |
| SELL HYB_OUT | 39 | 23 | 11 | 5 | +23,3 | +14,0 | không đủ N |
| SELL PRE_HYBRID | 95 | 71 | 16 | 6 | −4,8 | −13,7 | không đủ N |
Ex-post (ngày giảm/tăng xác định sau cuộc bằng Price/open−1): BUY HYB_IN −110,6 (18) / +189,3 (4); BUY PRE_HYBRID +7,0 (56) / +32,6 (33); SELL HYB_IN −22,5 (60) / +11,9 (55). Chênh lớn theo hướng ngày ⇒ mean bị chi phối bởi tỉ lệ ngày giảm trong mẫu, **không dùng làm bộ lọc live, không đọc là edge**. Hai account cùng dấu (BUY HYB: SpaceX −54,9 / ZaloPay −57,2 — nhưng cùng mã cùng ngày nên không độc lập).

## 4. Caveat
- BUY HYBRID 10 ngày/4 tuần: thống kê vô nghĩa; mean âm sâu một phần vì thị trường giảm trong 10 ngày đó. SELL "ngoài block" cao (+23,3) là phần dư bán muộn trong ngày giảm/tăng, không so được.
- Fill ở đây = giá khớp từng lệnh LO (không phải VWAP phiên); open = giá mở cửa ATO, không có hình thức lệnh ta có thể khớp tại open thực tế. Chưa có phí/impact. Không nhìn vào code monitor.
- Không đo nguyên nhân khoảng trống 08-18→09-13. Chưa qua quant-skeptic. Tái lập: `python3 build.py` (rồi `analyze.py`), MD5SUMS; PREREG md5 830788d51795e191239e6199df28a9c0 khoá trước khi tính bps.
