# GAPS — DD HHS 01/11/2026 (job Taylor_20261101_033221)

Các mục dưới đây là những gì DD chưa kiểm được. Mỗi mục ghi tác động nếu kết quả khác với giả định đang dùng.

## Thiếu nguồn
| # | Thiếu | Đã thử | Tác động |
|---|---|---|---|
| G1 | CV giải trình biến động LNST Q3/2026 (và 6T, Q2) | Thử khoảng 60 tên file trên hoanghuyhhs.vn: đều 404. Chưa thử HOSE CBTT, cafef, vietstock | Thấp, vì BCTC đã đủ để tách lợi nhuận |
| G2 | BCTN 2025 (cơ cấu xe theo hãng/phân khúc, số xe bán, hợp đồng phân phối Dongfeng) | Dò tên file 03–06/2026 không trúng | **Trung bình.** Chưa biết HHS có độc quyền Dongfeng hay không, thời hạn hợp đồng, có còn International/Navistar không (Bobby §7.3) |
| G3 | BCTC Q1/2026 và Q3/2025 bản gốc | Dò tên file không trúng | Chưa đối chiếu được số báo chí Q2/2026 "DT 233,8, LNST 31,6" |
| G4 | NQ ĐHĐCĐ 24/04/2025 và CBTT về mua HHS Capital: **người bán là ai**, có định giá độc lập không | Chưa tìm | **Cao cho WARNING.** Nếu người bán là người liên quan ⇒ CK quản trị +5 điểm % (≈ −670 đ) |
| G5 | Danh tính nhóm uỷ quyền 7,37–7,53% biểu quyết CRV và thời hạn uỷ quyền | [TCH-DD] cũng chưa tìm được | Trung bình. Hiện không cần uỷ quyền vẫn >50% (biên 1,15 điểm %) |
| G6 | Cổ đông ngoài TCH (41,69%), sở hữu nước ngoài, room, free float thực | BQ không có dữ liệu khối ngoại | Thấp–trung bình (thanh khoản 10,8 tỷ/phiên) |
| G7 | Thuyết minh **bảo lãnh/cam kết mua lại xe** cho ngân hàng (Bobby §7.12) | BCTC Q3 HN chỉ có thuê hoạt động ở mục ngoài bảng | **Trung bình.** "Không thuyết minh" ≠ "không có". Kiểm ở BCTC năm 2025 (TM nợ tiềm tàng; chưa đọc hết 107 trang) |
| G8 | Thuyết minh PPA chi tiết: phân bổ phần đánh giá lại theo dự án (NC-II / H1 / BĐSĐT / I.14), giả định giá bán | Mới đọc [KT25 TM3.1] tổng | **Cao cho định giá.** Haircut 25–60% là ước lượng; nếu PPA dựa trên giá bán đã thấp hơn thị trường ⇒ lệch về phía tốt |
| G9 | Mục đích ký quỹ 28,4 tỷ cho cá nhân Phạm Văn Xuân | Không có trong thuyết minh | Thấp về số, nhưng là cờ quản trị |
| G10 | Dự toán chi phí còn lại để hoàn thành các căn NC-II đã nhận tiền (3.099) | BCTC không có | Trung bình cho net cash thật |
| G11 | QĐ xử phạt riêng của HHS (thuế, UBCKNN) | Chưa tra ssc.gov.vn và CBTT HHS | Trung bình |
| G12 | Số cổ phiếu CRV sau đợt phát hành 2026 (166 tỷ TCH mua) | Ước 672,5 tr cp từ [KT25] | Thấp (chỉ ảnh hưởng phép suy giá/cp CRV) |

## Ước lượng tự đặt (đều gắn nhãn trong REPORT)
- Thuế suất 20% để quy thuế hoãn lại ra phần đánh giá lại (Pruksa VN 10%, nhỏ).
- CRV trên cơ sở giá trị hợp lý ≈ NCI / 48,85% (bỏ qua NCI Pruksa VN 9,83%).
- LNST lõi mảng xe 25/40/55, P/E 6/8/10, haircut 60/40/25%, CK holding 35/25/15%, CK quản trị 15/10/5%, P 0,30/0,50/0,20.
- Q2/2026 DT ô tô ≈ 203 (suy từ [TCH-DD] 6T FY26 trừ Q3 HHS).

## Bước tiếp theo đề xuất (nếu user cân nhắc discretionary)
1. Tìm G4/G8 (CBTT HOSE 04–06/2025, BCTC năm 2025 TM PPA) trước khi chạy fundamental-skeptic.
2. Theo dõi M2 (HTK xe Q4) và M3 (cổ tức CRV).

## Cập nhật v2 (01/11/2026, job Taylor_20261101_041414) — sau GAPS_FILL + phản biện
| # | Trạng thái | Ghi chú |
|---|---|---|
| G1 | một phần | Báo chí dẫn giải trình Q2 (Mekong ASEAN 30/07). Chưa có CV Q3 |
| G2 | **đóng một phần** | BCTN25: HHS = đại lý Dongfeng; Navistar ở TCH. Còn thiếu số xe/hợp đồng |
| G3 | **đóng Q2** | Q2HN có trong `src/` (DTT 233,81; LNST 31,60) — v1 ghi sai "chưa kiểm". Q1/2026, Q3/2025 riêng lẻ vẫn thiếu |
| G4 | mở (một phần) | NQ25: không tên người bán, không định giá độc lập, TCH được biểu quyết. Còn: danh sách cổ đông HHS Capital (Sở KH&ĐT HP) |
| G5 | mở | Nhóm uỷ quyền 7,53% không tên |
| G6 | đóng | TCH 58,31%; NN 0,59%; nhóm Đinh Quang Chiến 5,12% |
| G7 | **đóng** | KT25 không có thuyết minh bảo lãnh/mua lại xe; vay 390 do CRV vay, thế chấp NC-II |
| G8 | mở | PPA chỉ thuyết minh tổng. **v2 không còn phụ thuộc haircut PPA** — cơ sở chính dùng tham số DD TCH |
| G9 | một phần | Ký quỹ 28,4 phát sinh 2026; mục đích chưa rõ |
| G10 | mở | |
| G11 | một phần | Không thấy QĐ phạt HHS; MỚI: KL 08/KL-TTTP (Pruksa NƠXH), TB 2124/TB-TTCP (N01 CRV, 7,87 tạm trích). Chưa tra ssc.gov.vn |
| G13 (mới) | mở | Q3/2026 chưa soát xét; 6T soát xét hạ LNST mẹ −34% ⇒ chờ BCTC năm 2026 kiểm toán (M1) |
| G14 (mới) | mở | Thặng dư BĐSĐT CRV chính xác (cận dưới ~1.021 trước thuế từ chênh sổ HHS–TCH) — cần BCTC CRV 2025 kiểm toán |
| G15 (mới) | mở | Ngày lập HHS Capital: báo cáo sở hữu CRV 18/06/2025 → 31/03/2025; BCTN 2025 → 31/05/2025. Investor report không nêu ngày lập |
