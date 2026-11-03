# SELFCHECK — DRI_DD_investor_report_20261103 (r5, 03/11/2026)
- Số định giá đọc từ r5/calc/*.json đã khoá md5 (LOCK_md5_r5.txt 23:12:56 ICT); build_report_v4.py không hard-code số định giá; giá 13.400 đọc từ liquidity_r5_out.json (DNSE ohlc 1D).
- Đối chiếu md ↔ json (× (1−0,020019)): tâm 15.860→15.543; vùng 13.301–16.488; P10/P90 12.893/18.033; lãi huy động 16.000/15.768/15.543/15.325/15.114; thanh khoản 15.718/15.543/15.411; kịch bản 13.301–16.488 / 10.101–12.482; bình quân 14.360; p0/10/30 15.103/14.732/13.989; diễn giải thanh lý 13.184 (11.734–13.764); L22 13.301; đáy 13.013.
- PDF 10 trang; grep PDF không còn 16,6 / 16.610 / 18.840 / 2,34 / 14.130 / 22.710; render trang 1 + 7 kiểm bằng mắt; banner tiêu đề dựng lại (make_title_banner.py).
- grep luật 1/11/12/18 trên md + subject: chỉ khớp "Vòng đời" và mã rủi ro R4/R5 (không phải tên nội bộ/vòng sửa).
- Email: send_dd_report_email.py --dry-run --html-out → to=địa chỉ user, 18 ảnh, 8,8MB, 18/18 <img có alt. KHÔNG gửi thật.
- Thân ~2.100 từ theo cách đếm tách ký hiệu bảng (bản trước cùng cách đếm 2.012) — hơi vượt trần ~1.800.
