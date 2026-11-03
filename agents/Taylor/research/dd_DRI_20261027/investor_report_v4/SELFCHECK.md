# SELFCHECK — DRI_DD_investor_report_20261103 (03/11/2026)
- Số định giá đọc từ r4/calc/*.json đã khoá md5 (LOCK_md5_r4.txt 22:36:11 ICT) — build_report_v4.py không hard-code số định giá (trừ giá đóng 13.400 DNSE và T1 @mid thấp 10.928 từ dri_model_r4_out.txt mục 4).
- Bảng độ nhạy lãi huy động/thanh khoản/kịch bản đối chiếu bằng python (dri_model_r4_out.json × (1−0,020019)): 17.128/16.865/16.610/16.364/16.126; 16.798/16.610/16.470; kịch bản 18.837–22.711 / 15.540–18.837 / 10.709–11.732; bình quân 16.712.
- grep luật 1/11/12/18 (SpaceX|ZaloPay|NAV|Taylor|Bobby|Mike|skeptic|QUALIFY|fear|đính chính|trước đây|vòng N|...) trên md + subject: chỉ còn "giá vốn" (nghĩa: theo chi phí) và mã rủi ro R1–R5.
- PDF 10 trang; đầu trang "dữ liệu đến 03/11/2026"; đã render trang 1 + 7 kiểm bằng mắt.
- Email: `send_dd_report_email.py --dry-run --html-out` → to=địa chỉ user, 18 ảnh, 8,7MB, 18/18 <img có alt. KHÔNG gửi thật.
- Luật 15: bản đồ fig_23 (make_map, ranh giới VN, phía Lào không vẽ; toạ độ Wikipedia gần đúng) + ảnh sản phẩm fig_24 (BCTN 2025 tr.5, 8).
- Thân ~1.850 từ (tính cả ô bảng, không tính phụ lục) — sát trần ~1.800.
