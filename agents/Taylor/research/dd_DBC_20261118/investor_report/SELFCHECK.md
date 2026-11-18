# SELFCHECK — DBC investor report 18/11/2026 (nội bộ)

- Nguồn số: ../REPORT.md (bản cuối, assumptions_md5 207da8c9f22224141b64771a34fc2e20) + ../model/calc_output.txt + sector read chan_nuoi_heo_tacn_20261118. Phụ lục E/E2 nội bộ KHÔNG đưa vào; Phụ lục E bản NĐT chỉ mô tả quy trình trung tính. BAF (banned nội bộ) bỏ khỏi bảng peer.
- Giá: neo đóng cửa 17/11/2026 = 16.950 (BQ ticker). DNSE latest_trade 18/11/2026 11:29:40 = 16.950 (basicPrice 16.950; marketId STO = HOSE). Kết luận không đổi ở cả hai mức (giá/tâm 0,87).
- Đối chiếu số tự động: mọi số ≥3 chữ số trong md (trừ Phụ lục F) có trong REPORT/calc_output/sector read/website, trừ 3.657 (làm tròn 3.656,6) và 49.000 (dải 46–49k sector read). build_report.py tái lập ROE trung bình 15 quý = 11,425% từ assumptions (khớp 11,42%), assert NP BQ = assumptions; ADV trung vị 63 phiên = 20,08 tỷ từ figs/price_raw.csv.
- Số mới chỉ trình bày (không vào định giá): vùng giá 12 tháng 15.000–25.560 (BQ Close 18/11/2025–17/11/2026).
- Kết luận khớp REPORT §0/§6f: tâm 19.491 (trước CK 19.888), vùng 11.314–27.270, base sau CK 19.689, toàn vốn 15.291, ma trận 0,83–1,10, 6 cách chuẩn hoá 0,78–1,27, lãi huy động ±50/100bp, CK 0/5%, §9 mốc hai chiều, TSSH 94–188, Q4 −50…+120, phải thu NLĐ 237,1 (27%).
- Lãi suất (luật 17): dcf_rate_display 2026-11-18 → r* 15,1% p75 (đỉnh 15,9% 2022, đáy 12,1%); TPCP 10Y 4,57% +0,57pp ("nguồn chưa đối chiếu độc lập"). Nhãn DISPLAY-ONLY/UNVERIFIED đã chuyển sang lời thường.
- Ảnh/logo: logo-dabaco-new.svg (dabaco.vn, render PNG bằng pymupdf); ảnh trại gà, phòng thí nghiệm, nhà máy ép dầu, giống vật nuôi, trứng, dầu ăn từ dabaco.vn (tải 18/11/2026). Không có ảnh TACN trên website -> ghi rõ dưới khung ảnh.
- Bản đồ: chỉ khu vực miền Bắc (bbox 103,4–108,4 / 19,3–22,9), toạ độ OSM Nominatim 18/11 theo xã/huyện có trong website/BCTC; tỉnh chưa rõ huyện chỉ tô đậm. tools/make_map_dbc.py = bản sao make_map.py đổi nhãn chú giải + wrap chú thích nguồn.
- Grep (md + html bỏ base64): nội bộ RỖNG; fear-buy/nhãn nội bộ (gồm V_dài/V_ngắn/phân kỳ/NARROW/DISPLAY-ONLY/UNVERIFIED) RỖNG; luật 18 RỖNG trừ "R1–R6" (mã rủi ro, không phải số bản). HTML: 12 <img>, alt banner đóng đúng (tiêu đề không có nháy kép).
- Thân 1.018 từ (không tính bảng/hình/phụ lục); PDF 10 trang (thân 8 + phụ lục 2). Đã render toàn bộ trang ra PNG, xem trang 1 độ phân giải đầy đủ + contact sheet trang 1–10: dấu Việt đúng, bảng không tràn.
- Email: send_dd_report_email.py --dry-run --html-out (DRY-RUN: không gửi). CHƯA GỬI THẬT. Chưa ghi dd_price_zones.json (việc của Mike).
- PDF md5: d5a8515f88c3d593a9c290cbd4f4972c
