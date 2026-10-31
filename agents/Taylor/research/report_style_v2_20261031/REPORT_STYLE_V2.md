# Chuẩn báo cáo tài khoản v2 — ngày / tuần / tháng / quý (bản đề xuất, chờ duyệt)

Mẫu tham chiếu: `out/SpaceX_weekly_26-30_10_v2.pdf`, `out/SpaceX_daily_2026-10-30_v2.pdf`, `out/SpaceX_quarterly_Q3_2026_v2.pdf`.
Mã dựng: `build_report_v2.py` (trình bày) + `data_sources.py` (chỉ đọc pipeline có sẵn).

## Nguyên tắc
1. **Trang 1 là tear sheet.** Banner có tiêu đề là một câu kết luận có số (vd "Tuần −0,60% so với VN-Index −1,83%: hơn chỉ số 1,23 điểm %…"). Dưới banner: dải KPI, một chart NAV đã loại dòng tiền so với VN-Index (cơ sở 100), và "3 điều cần biết".
2. **Mỗi mục có một câu tiêu đề kết luận, một chart hoặc bảng, và tối đa 3 gạch đầu dòng.** Mỗi gạch ≤ 25 từ; `bullets()` báo lỗi khi vượt số gạch hoặc số từ. Không có đoạn văn quá 3 câu.
3. **Phương pháp, đối soát và chú thích dài đưa xuống Phụ lục (≤ 1 trang).** Trong thân chỉ giữ footnote 1 dòng.
4. **Bảng trong thân không quá 10 hàng** (`table()` báo lỗi khi vượt; phụ lục dùng `max_rows=None`). Số căn phải; ô +/− có màu nhưng luôn kèm dấu; hàng tổng in đậm.
5. **Mỗi chart có:** tiêu đề là kết luận, đơn vị, dòng nguồn ở chân hình, CSV dữ liệu kèm theo. Chỉ dùng một trục y; hai đại lượng khác thang đo thì chia hai panel. Danh mục màu xanh `#2a78d6`, VN-Index màu xám. Phân bổ theo thứ tự cố định: xanh, cam, aqua (đã chạy validator của dataviz; aqua dưới 3:1 nên bắt buộc có nhãn số trực tiếp).
6. **Font Be Vietnam Pro, nhúng trong PDF.** Văn bản được NFC; ký tự font không có glyph (→ √ ≥ ≤) được `glyph_safe()` thay bằng chữ. Banner dựng bằng `make_title_banner.py`. Xuất PDF A4 và HTML email có ảnh nhúng `cid:`. Discord nhận kèm PDF, bỏ hẳn câu "xem biểu đồ trong email".
7. **Không lộ nội bộ:** không tên agent (Livermore/Taylor…), không tên script, không nhãn nội bộ (LAG/PARK/DT5G/PEAD). Dùng tên cho nhà đầu tư: "sau công bố lợi nhuận", "tạm giữ (rổ giá trị)", "chọn lọc cơ bản", "mô hình trạng thái thị trường".
8. **Không tạo số mới.** Mọi số lấy từ pipeline đã có (bảng dưới). Thiếu số thì ghi "không có", không tự tính. Mọi tiêu đề/khẳng định suy từ số phải có `assert` trong mã dựng (ví dụ mock tuần từng có tiêu đề "thấp nhất từ 07/2026"; assert bắt được là sai nên đã bỏ).
9. **Giữ các luật trung thực hiện hành, chỉ rút gọn câu chữ.** Dự báo kỹ thuật: 1 dòng và câu "đã chấm 0, chưa tốt hơn giả định thị trường tăng". Định giá: "tham khảo, 0/17 qua kiểm định". Xác suất kịch bản: "ước lượng chủ quan".
9b. **Hiệu suất = trên vốn đang quản lý, KHÔNG phải thay đổi NAV tuyệt đối (user chốt 2026-10-31).** Mọi tỷ suất ở tiêu đề, KPI, chart so VN-Index, bảng kỳ đều là TWR theo giá đơn vị (`nav_period_returns`, đã loại nạp/rút). Thay đổi NAV theo sổ chỉ xuất hiện trong "cầu NAV" (đầu kỳ → lãi/lỗ đầu tư → nạp/rút → cuối kỳ) để người đọc thấy rút vốn không phải lỗ đầu tư. Không có tỷ suất nào lấy từ NAV cuối/NAV đầu. Cầu NAV có ở mọi cadence (ngày/tuần/tháng/quý); nạp/rút luôn ghi bằng chứng + thời điểm (đầu/cuối ngày) theo sổ dòng tiền.

## Nguồn số (không thương lượng)
| Số | Nguồn |
|---|---|
| NAV, cổ phiếu / tiền / Trứng vàng | `nav_history_<acct>.csv` (`daily_nav_snapshot.py`) |
| Tỷ suất ngày/tuần/MTD/từ đầu + VN-Index (giá, có cổ tức) | `nav_period_returns.compute_period_returns` (§31) |
| Chuỗi chart NAV, sụt giảm, biến động | `nav_period_returns.build_ledger` (giá đơn vị, cùng sổ dòng tiền) |
| Chênh điểm % | `data_sources.excess_pp`, tính từ số CHƯA làm tròn (trừ hai số đã làm tròn 3 chữ số có thể lệch 0,01) |
| Tỷ suất từng vị thế | `dividend_adjusted_return.py` qua `portfolio_status` / `report_return_gate` (§21) |
| VN-Index OHLCV, MA, độ rộng %>MA50; khối kỹ thuật | loader của `livermore_report_block.py`; `data/livermore/report_block_<d>_<kind>.json` |

## Khung từng loại
| Loại | Trần | Trang 1 | Các mục (mỗi mục 1 chart/bảng + ≤ 3 gạch) |
|---|---|---|---|
| **Ngày** | 1 trang, ≤ 150 từ văn xuôi | banner + 6 KPI + cặp chart (NAV tháng vs VNI · phân bổ theo nhóm) | lệnh trong ngày (1 dòng tiêu đề) · vị thế theo nhóm (≤ 10 hàng) · sự kiện quyền 7 ngày · cần theo dõi (3 gạch) · 1 dòng đối soát |
| **Tuần** | 4 trang thân + 1 trang phụ lục, ≤ 700 từ văn xuôi | tear sheet + thanh phân bổ đầu/cuối kỳ | Hiệu suất (bảng kỳ + NAV ngày) · Đóng góp (cột ngang) · Danh mục (bảng ≤ 9 hàng + cặp P&L theo mã / sụt giảm) · Giao dịch (bảng + 3 gạch) · Thị trường (cặp VNI+MA+KL / độ rộng; bảng kỹ thuật 5 dòng) · Định giá và trạng thái (bảng 2 dòng) · Tuần tới (bảng kịch bản) · Phụ lục: attribution đầy đủ + phương pháp |
| **Tháng** | ≤ 6 trang | tear sheet (KPI có MTD/QTD/YTD) | khung tuần, cộng thêm: NAV theo ngày trong tháng; heatmap tháng-theo-tháng; so benchmark có cổ tức; bảng rủi ro (độ biến động, MDD, tỷ lệ phiên tăng, beta); đóng góp theo mã/ngành; chi phí; vĩ mô dạng bảng (không viết văn) |
| **Quý** | ≤ 8 trang | tear sheet (quý vs VNI, MDD, độ biến động, tháng tốt/xấu nhất) | heatmap tháng + bảng · sụt giảm vs VNI + bảng rủi ro · tỷ trọng cổ phiếu/NAV theo ngày · danh mục cuối quý · đóng góp · chi phí · triển vọng dạng bảng kịch bản |

Báo cáo tháng chưa có mock trong vòng này. Nó tái dùng toàn bộ thành phần: `chart_month_grid`, `chart_underwater(bench=…)`, `chart_line`, `kpi_tiles`, `table`.

## Điểm gắn đề xuất (CHƯA gắn, chờ duyệt)
1. **`bin/check_report_cadence.sh` (prompt soạn tuần/tháng):** bỏ yêu cầu viết markdown tự do. Thay bằng: "chạy `report_v2/build_<cadence>.py --account A --period …`, đính kèm PDF, rồi qua `report_delivery_gate.py`". Agent chỉ được viết các chuỗi tiêu đề/gạch (có trần từ), không viết số.
2. **`bin/eod_trading_report.sh`:** sau `_nav_section`, gọi `build_daily_v2` để ra PDF 1 trang. Discord nhận tóm tắt 3 dòng kèm PDF; email nhận HTML có ảnh nhúng cid.
3. **`report_delivery_gate.py`:** thêm lint cơ học, chặn khi có `['|`, `\n|`, `**`, dòng `|---` trong PDF/HTML, hoặc font PDF không phải Be Vietnam Pro (dùng `build_report_v2.lint_pdf`).
4. Chuyển module từ thư mục nghiên cứu sang `mike/bin/report_v2/` khi được duyệt (§10: archive các bản `gen.py` / `write_*.py` theo tuần).

## Checklist tự kiểm (`selfcheck.py`, hiện PASS)
- [ ] Chạy mock 2 lần: text PDF và mọi CSV giống hệt (md5).
- [ ] Bảng đối chiếu "mock vs báo cáo gốc": sai lệch 0 ở mọi dòng, và mỗi số gốc phải tìm thấy trong file gốc.
- [ ] Text PDF không còn markdown thô, `['|`, `None` hoặc `nan`. Chỉ font Be Vietnam Pro, có nhúng.
- [ ] Không có tên nội bộ (regex `INTERNAL`). Mọi `<img` trong HTML email có alt đóng đúng, file cid tồn tại.
- [ ] Số trang ≤ trần; văn xuôi thân ≤ trần (`prose_words`).
- [ ] Xem PNG từng trang bằng mắt: nhãn không chồng nhau, dấu tiếng Việt đúng.
