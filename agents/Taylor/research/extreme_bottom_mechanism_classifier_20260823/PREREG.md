# PREREG — phân loại cơ chế "cú sốc THANH KHOẢN/CHÍNH SÁCH" vs "cú sốc CƠ BẢN THẬT"

Job `Taylor_20260823_110750`. Viết & **commit TRƯỚC** khi chạy bất kỳ truy vấn ROE/NP nào và
trước khi gán nhãn bất kỳ episode nào. Đối tượng: **7 episode `dd52<=-20%`** đã liệt kê ở
`research/extreme_bottom_recognition_20260823/episodes_dd52.csv` (job `Taylor_20260823_083709`).

## 0. KHAI BÁO XUNG ĐỘT — prereg này KHÔNG mù với outcome

Phải nói thẳng trước mọi thứ khác: **forward return 12/24 tháng của cả 7 episode ĐÃ ĐƯỢC BIẾT**
từ job trước (`trough_stock_forward.csv`, README §Q2), và người viết prereg này chính là người
đã chạy job đó. Đây **không** phải prereg mù. Không thể giả vờ ngược lại.

Vậy prereg này còn giá trị ở đâu:
1. Nó khoá **LUẬT PHÂN LOẠI + NGƯỠNG SỐ** trước khi chạy truy vấn ROE/NP — dữ liệu lợi nhuận rổ
   theo quý ở các episode 2007/2009/2011/2012/2018 **CHƯA từng được nhìn**, nên phần bằng chứng
   số này thực sự out-of-sample với người phân loại.
2. Nó khoá **tiêu chí bác bỏ** (§5) trước, nên không thể nới ngưỡng sau khi thấy kết quả.
3. Nó ghi lại trước những gì **đã biết** (§0b) để người đọc sau tự trừ hao đúng phần thiên lệch.

### 0b. Những gì người viết ĐÃ BIẾT trước khi phân loại (liệt kê đầy đủ, không giấu)
- Median **cổ phiếu** fwd-12m tính từ ĐÁY của từng episode: 2009-02-24 **+130,0%** · 2010-08-25
  **−46,8%** · 2012-01-06 +21,2% · 2012-11-02 +26,3% · 2019-01-03 +0,8% · 2020-03-24 **+96,7%** ·
  2022-11-15 +42,4%.
- VNINDEX fwd-12m tính từ ARM: 2007-04 −44,2% · 2009-11 −8,9% · 2011-05 +7,2% · 2012-08 +22,6% ·
  2018-05 +4,3% · 2020-03 +44,2% · 2022-05 −9,9%.
- Giả thuyết của user (John) nêu tường minh trong dispatch: nhóm THANH KHOẢN/CHÍNH SÁCH
  mean-revert mạnh hơn nhóm CƠ BẢN THẬT; user đoán trước 2010-08-25 và GFC 2008 thuộc nhóm CƠ
  BẢN THẬT. **Người phân loại biết cả kỳ vọng lẫn đáp án** ⇒ mọi nhãn khớp kỳ vọng phải bị đọc
  với chiết khấu tương ứng.

## 1. Định nghĩa hai loại (khoá trước, không sửa sau)

| Nhãn | Định nghĩa CƠ CHẾ |
|---|---|
| **LIQUIDITY_POLICY** | Cú sốc sinh ra **NGOÀI** bảng kết quả kinh doanh của doanh nghiệp niêm yết: khủng hoảng ngân hàng/bank-run, siết thanh khoản đột ngột, cú sốc lãi suất/chính sách tiền tệ, cú sốc tỷ giá, margin-call/bán giải chấp cưỡng bức, đại dịch/thiên tai gây đóng cửa tạm thời. Giá bị ép xuống bởi **người bán buộc phải bán**, không phải bởi thu nhập suy giảm. |
| **FUNDAMENTAL_REAL** | Cú sốc **ĐÃ vào** thu nhập doanh nghiệp: suy thoái kinh tế thực, đơn hàng/doanh thu giảm, biên lợi nhuận co, nợ xấu tăng do hoạt động kinh doanh yếu (không phải do thanh khoản), thừa cung/đóng băng một ngành trụ cột kéo dài nhiều quý. |
| **AMBIGUOUS** | Hai nguồn bằng chứng (§2 tin tức vĩ mô vs §3 số lợi nhuận) **mâu thuẫn**, hoặc dữ liệu tài chính không đủ để kết luận. **Bắt buộc dùng nhãn này khi mâu thuẫn — cấm ép về một phía.** |

Lưu ý cơ chế: hai loại **không loại trừ nhau về thời gian**. Một cú sốc thanh khoản kéo dài đủ
lâu CÓ THỂ biến thành suy thoái thu nhập thật (kênh tín dụng). Luật gán nhãn ở §4 quyết định
theo **bằng chứng trong cửa sổ đo**, không theo diễn giải tự do.

## 2. Nguồn bằng chứng A — nguyên nhân vĩ mô (định tính, có nguồn)
Tra tin tức/lịch sử thật bằng WebSearch cho MỖI episode; ghi ≥1 nguồn dẫn được cho mỗi episode.
**Cấm suy đoán từ hình dạng đồ thị giá.** Ghi rõ: sự kiện khởi phát, kênh lan truyền, và câu trả
lời nhị phân "cú sốc này có đi qua bảng kết quả kinh doanh trong 4 quý kế tiếp không?".

## 3. Nguồn bằng chứng B — số lợi nhuận rổ (định lượng, PIT về mặt cấu trúc rổ)

**Rổ**: các ticker có `in_universe = TRUE` tại **ngày ARM** trong `tav2_mike.universe_pit`
(CANONICAL, đăng ký `price-volume/universe_pit.md`) — đóng băng danh sách tại ARM, không cập
nhật về sau (tránh survivorship trong cấu trúc rổ).

**Nguồn tài chính**: `tav2_bq.ticker_financial` (CANONICAL, `fundamentals/ticker_financial.md`);
cột ROE/NP đã verify KHÔNG hồi tố (job `Winston_20260717_070859`,
`fundamentals/roe_roic_fscore_quality.md` bẫy (1)). **KHÔNG dùng `OShares`** (TRAP: restate).

**Quý neo** `q0` = quý tài chính gần nhất có `time <= arm_date`. Đo tại `q0`, `q0+2`, `q0+4`.

Ba chỉ số, **báo cáo cả ba dù kết quả thế nào**:
- **M1** — median `ROE_Trailing` của rổ tại q0, q0+2, q0+4 (mức, không phải tỷ lệ).
- **M2** — median theo từng mã của `TTM_NP(q0+k) / TTM_NP(q0)`, với `TTM_NP = NP_P0+NP_P1+NP_P2+NP_P3`,
  chỉ tính cho mã có `TTM_NP(q0) > 0` (mẫu số dương). k = 2 và 4.
- **M3** — % số mã trong rổ có `TTM_NP > 0` tại q0, q0+2, q0+4.

**Ngưỡng khoá trước** (chọn ở mức "đủ lớn để không phải nhiễu", không phải tối ưu):

| Bằng chứng số | Điều kiện |
|---|---|
| ủng hộ **FUNDAMENTAL_REAL** | `M2(k=4) <= 0,80` (lợi nhuận rổ giảm ≥20%) **HOẶC** M1 giảm tương đối ≥ 1/3 từ q0 tới q0+4 |
| ủng hộ **LIQUIDITY_POLICY** | `M2(k=4) >= 0,95` **VÀ** M1 giảm tương đối < 1/3 |
| **không kết luận được** | mọi trường hợp còn lại (0,80 < M2 < 0,95), hoặc <30 mã có dữ liệu |

## 4. Luật gán nhãn (khoá trước)
- A và B **cùng chiều** → nhãn đó.
- A và B **ngược chiều** → `AMBIGUOUS`, ghi rõ mâu thuẫn ở đâu.
- B "không kết luận được" → lấy nhãn theo A nhưng **gắn cờ `(chỉ-định-tính)`**, và trong mọi
  bảng kết quả phải hiện cờ đó.

**Thứ tự thao tác bắt buộc**: (i) commit file này; (ii) chạy §2 + §3 và gán nhãn 7 episode;
(iii) commit bảng nhãn; (iv) **chỉ sau đó** mới ghép forward return vào so sánh nhóm.

## 5. Tiêu chí BÁC BỎ — khoá trước, không nới sau

Vì outcome đã biết (§0), mọi ngưỡng "mean-revert mạnh/yếu" chọn bây giờ đều có thể bị bẻ cong.
Nên tiêu chí dùng **thứ hạng, không dùng ngưỡng**:

> **Giả thuyết được ủng hộ CHỈ KHI hai nhóm TÁCH HOÀN TOÀN theo median cổ phiếu fwd-12m tính từ
> đáy**: episode LIQUIDITY_POLICY **kém nhất** vẫn phải cao hơn episode FUNDAMENTAL_REAL **tốt
> nhất**. Chồng lấn dù chỉ 1 cặp = **KHÔNG được ủng hộ**.

Kèm điều kiện dispatch của Mike: **≥2/7 episode đi ngược giả thuyết ⇒ tuyên NO-GO thẳng**, không
giải thích quanh co. Episode `AMBIGUOUS` **không được** dùng để cứu tách nhóm (loại khỏi phép
kiểm tách, vẫn báo cáo số).

## 6. Giới hạn khai báo trước (không phải bào chữa hậu kỳ)
1. **N = 7 episode.** Đây là **bằng chứng cơ chế**, KHÔNG phải kiểm định thống kê. **Không tính
   p-value** — với N=7 và nhãn do chính người biết đáp án gán, p-value là số trang trí.
2. **Bằng chứng B nhìn về TƯƠNG LAI so với ngày ARM** (q0+2, q0+4 chưa công bố tại ARM, còn trễ
   thêm 60–85 ngày theo `MAX_FIN_LAG`). ⇒ Ngay cả khi phân loại đúng 7/7, nó **KHÔNG dùng trực
   tiếp làm cổng live được**. Muốn dùng live phải thay bằng biến quan sát được tại ARM (nguyên
   nhân vĩ mô + lợi nhuận TRAILING) — đó là nghiên cứu KHÁC, chưa làm ở đây.
3. `tav2_bq.ticker` **xoá sạch mã huỷ niêm yết** (0 dòng FLC) ⇒ mọi thống kê lợi nhuận rổ là
   **CẬN TRÊN**; thiên lệch này đánh mạnh nhất vào đúng nhóm FUNDAMENTAL_REAL (nơi doanh nghiệp
   chết nhiều hơn) ⇒ **có xu hướng làm giả thuyết TRÔNG ĐÚNG HƠN thực tế**.
4. Rổ 2007–2012 mỏng (~19–200 mã, `ticker_prune` note) và chuẩn mực kế toán VN thời kỳ đó khác;
   so sánh mức ROE giữa các thập kỷ chỉ là tham chiếu thô.
5. **KHÔNG chạm production, KHÔNG backtest tối ưu tham số, KHÔNG đề xuất wire.** Đây là Phase
   0-tier. Không tính vào `N_trials` của `plan_margin_valuation_spread_20260823.md`.
