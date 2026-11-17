# SELFCHECK — QTP investor report 17/11/2026 (nội bộ)

- Nguồn số: ../REPORT.md (bản đã phản biện) + ../model/qtp_model_out.txt + sector read nhiet_dien_than_20261117. Phụ lục E nội bộ KHÔNG đưa vào; Phụ lục E bản NĐT chỉ mô tả quy trình trung tính. Mục HARD-ABANDON không đưa vào.
- Giá: DNSE latest_trade 17/11/2026 11:24:15 = 10.300 (basicPrice 10.300 = đóng cửa 16/11; sàn UPX/UPCOM theo secdef). Kết luận không đổi ở cả hai mức.
- Số đã đối chiếu lại: tâm 13.139≈13.140, vùng 10.390–16.490 (=0,9×11.546/18.324), kịch bản 11.546/15.200/18.324 trọng số 0,25/0,65/0,10, vòng đời 2030/35/40/47 = 11.507/12.437/12.847/13.139, lãi huy động ±50/100bp, CK thanh khoản 5/10/15%, PE A/B — khớp qtp_model_out.txt. ADV 1,22 tỷ tái lập từ figs/price_raw.csv (63 phiên).
- Số mới chỉ trình bày (đo trong phiên này, không vào định giá): lợi nhuận gộp quý từ BCTC gốc (Q1/26 252,4; Q1/25 239,7; Q4/25 954,8; Q4/24 214,2; Q2 suy từ lũy kế); tiền gửi đáo hạn mã 123 các kỳ (520/1.030/1.460/1.025/1.220/1.774,1); giá điều chỉnh quanh GDKHQ 10.400–10.500.
- Bản đồ: nhà máy ở Hà Khánh (TP Hạ Long cũ, nay phường Cao Xanh) theo địa chỉ website + OSM 21.0113,107.1279 — KHÔNG phải Cẩm Phả như brief gợi ý; Cẩm Phả vẽ như vùng than TKV. Chỉ bản đồ khu vực.
- Ảnh: logo + ảnh nhà máy (banner1.jpg) từ tpcquangninh.com.vn.
- Lãi suất (luật 17): dcf_rate_display 2026-11-17 → r* 15,1% p75; TPCP 10Y 4,57% +0,57pp (ghi "nguồn chưa đối chiếu độc lập").
- Grep cấm (md + html bỏ base64): RỖNG. Grep r[0-9]: rỗng. HTML: 11 <img>, alt đóng đúng, banner không trùng.
- Thân ~1.110 từ (không tính bảng/hình/phụ lục); PDF 10 trang (thân 8 + phụ lục 2). Đã render trang 1, 6, 9 + contact sheet và xem bằng mắt.
- Email: send_dd_report_email.py --dry-run --html-out (to=địa chỉ trong secrets, 11 ảnh, 5,8MB). CHƯA GỬI THẬT.
- PDF md5: 5facf0a700b689d234322b4e5a3368ac
- Chưa ghi dd_price_zones.json (việc của Mike sau khi chốt).
