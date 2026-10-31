# So sánh bản cũ và mock v2, cùng nguồn gốc các lỗi

Cách đo: dùng `measure_old.py` (dựng bản md cũ ra A4 cùng font, cỡ chữ và lề, kết quả ở `recon/old_metrics.json`) và `recon/*_meta.json`. "Văn xuôi" là phần chữ không nằm trong bảng, KPI hay hình.

| Báo cáo | Trang A4 | Từ (toàn bộ) | Từ văn xuôi thân | Đoạn dài nhất | Chart | Bảng |
|---|---|---|---|---|---|---|
| Tuần, cũ | 6 (quy đổi) | 3.852 | ≈3.150 | 235 từ ("Nhận định tuần"); khối kỹ thuật 536 từ; phụ lục 371 từ | 3 | 6 (+1 bảng vỡ thành tuple) |
| **Tuần, v2** | **5 (4 thân + 1 phụ lục)** | 1.464 | **517** | gạch ≤ 25 từ | **7** | 8 + dải KPI |
| Ngày, cũ | 1 (văn bản Discord) | 775 | 545 | 117 từ | 0 | 3 |
| **Ngày, v2** | **1** | 329 | **136** | gạch ≤ 25 từ | **2** | 2 + KPI |
| Quý, cũ | không có (quý 3 chỉ là 1 bảng trong báo cáo tháng 9: 8 trang, 3.725 từ) | — | — | — | — | — |
| **Quý 3, v2** | **3** | 546 | **151** | gạch ≤ 25 từ | **4** | 3 + KPI |

Ảnh từng trang nằm ở `pages/*.png`. Mock quý chỉ có 3 trang vì 4 mục chưa có nguồn pipeline (đóng góp, vị thế cuối quý, chi phí, triển vọng). Các mục này được ghi rõ "không có" chứ không tự tính.

## Đối chiếu số: mock và báo cáo gốc — 98/98 dòng sai lệch 0
| File | Số dòng | Lệch | Ghi chú |
|---|---|---|---|
| `recon/weekly_recon.csv` | 62 | 0 | Gồm NAV 945.141.046; tuần −0,60% / VNI −1,83%; MTD −1,89%; từ đầu −3,69%; attribution tổng −5.770.257; 9 lệnh; 8 vị thế; 6 NAV ngày |
| `recon/daily_recon.csv` | 21 | 0 | NAV, −700.678 (−0,07%), −36.835.465 (−3,69%), 9 vị thế và 3 nhóm |
| `recon/quarterly_recon.csv` | 15 | 0 | So với báo cáo tháng 9 §2.2 + §4: 3 tháng, quý −1,84% / −4,91% / +3,07; độ lệch chuẩn ngày tháng 9 = 0,616% (xác nhận cùng phương pháp) |

Mỗi dòng đối chiếu kiểm hai điều: mock in đúng chuỗi số, và chuỗi đó có thật trong file gốc.

## Nguồn gốc lỗi
**(a) Bảng attribution §3.3 in ra repr tuple** (`['| Nguồn | Đóng góp |\n…', 515443.0]`), lỗi có ở cả SpaceX và ZaloPay.
- Lỗi không nằm trong `bin/`. Nó nằm ở script tay của job tuần: `agents/Taylor/research/weekly_20261026_20261030/gen.py`. Hàm `attr(a)` trả `(bảng, ex)`, nhưng dòng `D[a]=dict(attr=attr(a), …)` lưu nguyên tuple. Sau `json.dumps`, tuple thành list, và `write_spacex.py:76` / `write_zalopay.py:80` chèn `{D['attr']}` nên in ra repr.
- Vá tối thiểu: `attr=attr(a)[0]`.
- Vá gốc:
  1. Bỏ kiểu "mỗi tuần một bộ `gen.py`/`write_*.py` tay". Báo cáo dựng bằng module chung (`build_report_v2.py`); bảng là đối tượng có kiểu, nên không thể chèn một tuple vào văn bản.
  2. `report_delivery_gate.py` đã cho báo cáo này COMPLETE dù có repr. Cần thêm lint cơ học (`lint_pdf` + regex `\['\|`, `\\n\|`, `\*\*`) để chặn.

**(b) Văn xuôi dài.**
- Nguồn gốc: prompt cadence yêu cầu agent "viết nhận định". Không có trần từ, không có khung mục, nên agent dồn mọi dữ kiện vào một đoạn (235 từ).
- Khối kỹ thuật dài 536 từ vì in nguyên 6 gạch văn xuôi của khối kỹ thuật độc lập. Khối này còn lộ tên nội bộ "Livermore" ra báo cáo nhà đầu tư.
- v2 xử lý: `bullets()` chặn gạch > 25 từ; `table()` chặn bảng > 10 hàng; khối kỹ thuật thành bảng 5 dòng; dự báo còn 1 dòng.

**(c) Discord chỉ có chữ ("biểu đồ xem trong email").**
- Nguồn gốc: báo cáo là `.md` và ảnh rời. Discord chỉ nhận văn bản.
- v2 xử lý: có PDF A4 tự chứa để đính kèm Discord giống báo cáo DD, và HTML email cùng nội dung (ảnh nhúng `cid:`).

**(d) Báo cáo ngày lặp cảnh báo "NAV hôm nay CHƯA có".**
- Nguồn gốc: `bin/portfolio_status.py:849-854` in cảnh báo khi `nav_history` chưa có dòng hôm nay. `eod_trading_report.sh` dựng khối danh mục (gọi `portfolio_status`, khoảng dòng 743) TRƯỚC khi `_nav_section` (dòng 857) chạy `daily_nav_snapshot.py`. Vì vậy cùng một báo cáo vừa có NAV hôm qua kèm cảnh báo, vừa có NAV hôm nay ở cuối.
- Đề xuất: gọi `_nav_section` trước khối danh mục, hoặc bản cho nhà đầu tư chỉ lấy NAV từ snapshot. v2 chỉ dùng NAV đã chốt.

## Phát hiện phụ khi đối chiếu (cần Mike/user quyết, mock CHƯA đổi)
1. **Dòng NAV ngày 29/10 trong báo cáo tuần gốc là −0,29%, pipeline chuẩn cho −0,30% (−0,2972%).**
   - Bản gốc tự tính trong `tables.py` và giả định khoản rút 18,02 triệu xảy ra cuối ngày. `nav_period_returns` ghi khoản này là `bod` (rút 09:04, đầu ngày).
   - Báo cáo ngày 29/10 cũng in −0,30%, tức hai báo cáo đang lệch nhau.
   - Tổng tuần (−0,60%), MDD (−10,29%) và độ biến động (0,77%) trùng nhau ở độ chính xác đang in.
   - Mock giữ số gốc để bảo đảm sai lệch 0. Khi gắn pipeline thì phải lấy số chuẩn.
2. Bảng nhóm của báo cáo ngày định giá cổ phiếu theo giá CTCK cuối ngày (tổng 166,4 triệu), còn NAV dùng giá đóng cửa (165,67 triệu). Bản gốc đã có chú thích. v2 tách bạch: KPI và phân bổ dùng NAV đã chốt, bảng nhóm có footnote nêu nguồn giá.
3. Tỷ suất từng vị thế trong báo cáo tuần gốc tính trong `tables.py` (cổ tức/cp gõ tay), không gọi công cụ §21. Số khớp với báo cáo ngày (đi qua §21), nhưng đường đi chưa đúng luật. v2 đặt nguồn bắt buộc là `report_return_gate`.
