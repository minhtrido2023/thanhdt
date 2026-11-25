# Tổng quan học thuật có chọn lọc — hành vi nhà đầu tư và giá cổ phiếu (ngắn)

**Cách đọc:** trích dẫn dưới đây viết từ trí nhớ của Taylor, **chưa đối chiếu lại bản gốc trong phiên này**. Mức chắc:
**[A]** = bài kinh điển, tác giả/năm/tạp chí chắc chắn; **[B]** = chắc về tác giả + ý chính, chi tiết xuất bản cần kiểm;
**[C]** = chỉ nhớ ý, KHÔNG dùng làm trích dẫn trước khi kiểm. Không có nghiên cứu riêng về Việt Nam nào được trích ở đây vì
tôi không kiểm chứng được trích dẫn nào đủ chắc — đây là khoảng trống, không phải kết luận "không tồn tại". Cột "dấu ở pilot"
là số đo trong kho (`out/pilot_results.json`), không phải từ tài liệu.

| # | Hiệu ứng | Nguồn | Cơ chế | Đặc trưng đo được ở VN (nguồn: DATA_INVENTORY) | Dấu dự đoán (lợi suất tương đối 12–24 tháng) | Rủi ro nhiễu |
|---|---|---|---|---|---|---|
| 1 | Neo giá vào đỉnh 52 tuần | George & Hwang (2004), *J. Finance* — "The 52-Week High and Momentum Investing" **[A]**; neo: Tversky & Kahneman (1974), *Science* **[A]** | Giá gần đỉnh cũ: người mua ngại trả cao hơn mốc neo ⇒ tin tốt ngấm chậm ⇒ tiếp diễn | `hi52` = log(giá / đỉnh 252 phiên) — CÓ | **+** (gần đỉnh ⇒ tiếp tục vượt trội) | Trùng với đà (tương quan hạng 0,45) và với quy mô/chất lượng; biên độ ±7% làm đỉnh "dính" |
| 2 | Hiệu ứng ngại chốt lỗ, giá vốn đám đông | Shefrin & Statman (1985), *J. Finance* **[A]**; Odean (1998), *J. Finance* **[A]**; Grinblatt & Han (2005), *J. Financial Economics* **[A]**; Frazzini (2006), *J. Finance* **[A]** | Lãi chưa thực hiện lớn ⇒ bán chốt lời ghìm giá ⇒ phản ứng chậm với tin tốt (và ngược lại với lỗ) | `cgo` = log(giá / giá vốn bình quân theo vòng quay) — CÓ, xấp xỉ (không có free-float) | **+** | Trùng `hi52` (0,67); mẫu số tổng CP làm giá vốn ì; Frazzini dùng sổ nắm giữ quỹ — VN không có |
| 3 | Ngoại suy quá mức / hiệu ứng gần đây | Barberis, Shleifer & Vishny (1998), *JFE* **[A]**; De Bondt & Thaler (1985), *J. Finance* **[A]**; Greenwood & Shleifer (2014), *Rev. Financial Studies* **[A]**; Barberis, Greenwood, Jin & Shleifer (2015), *JFE* (X-CAPM) **[A]** | Kỳ vọng bám lợi suất gần đây ⇒ quá đà ⇒ đảo chiều 3–5 năm | Lợi suất 36–60 tháng, tăng trưởng LN gần đây (`npg`, `revg`), lớp 2 (`lv_L2_*`) | **−** ở 3–5 năm; **+** ở 3–12 tháng (đà: Jegadeesh & Titman 1993, *J. Finance* **[A]**) | Hai chiều ngược nhau theo kỳ hạn ⇒ sai kỳ hạn là sai dấu; IC của tăng trưởng LN ở V3 ≈ 0 |
| 4 | Giá trị + đà bổ sung nhau | Asness, Moskowitz & Pedersen (2013), *J. Finance* — "Value and Momentum Everywhere" **[A]** | Hai nhân tố tương quan âm; kết hợp tốt hơn từng cái | `lv_ENS2`/E/P × `hi52`/đà | tương tác **+** | Đây là kiến thức phổ biến ⇒ "lực kéo" có thể chỉ là tái phát hiện nó |
| 5 | Chú ý | Barber & Odean (2008), *Rev. Financial Studies* — "All That Glitters" **[A]** | Cá nhân MUA ròng mã gây chú ý (khối lượng bất thường, lợi suất cực trị, tin) ⇒ giá bị đẩy rồi nguội | `to60` bất thường, `n_up60`, `max21` | **−** | Chú ý cũng đi cùng tin thật; cần tách khỏi PEAD |
| 6 | Ưa xổ số / MAX | Bali, Cakici & Whitelaw (2011), *JFE* — "Maxing Out" **[A]**; Kumar (2009), *J. Finance* **[A]** | Trả giá cao cho phân phối lệch phải | `max21`; giá thấp tuyệt đối; biến động | **−** | Biên độ chặn MAX ⇒ ở VN ≈ đếm phiên trần |
| 7 | Bầy đàn cá nhân | Lakonishok, Shleifer & Vishny (1992), *JFE* (thước đo bầy đàn) **[A]**; Barber, Odean & Zhu (2009), *Rev. Financial Studies* **[B]**; Barber, Lee, Liu & Odean (2009), *Rev. Financial Studies* (Đài Loan) **[A]** | Lệnh cá nhân cùng chiều, dai dẳng ⇒ đẩy giá ngắn hạn, đảo chiều sau | Không có lệnh cá nhân theo mã ⇒ **không đo trực tiếp**; proxy: vòng quay + phiên trần | **−** sau đợt mua dồn | Proxy yếu |
| 8 | Dồn giá ở số tròn | Harris (1991), *Rev. Financial Studies* **[A]**; Bhattacharya, Holden & Jacobsen (2012), *Management Science* **[B]** | Lệnh tập trung ở mốc tròn ⇒ kháng cự/hỗ trợ ngắn hạn | Khoảng cách tới mốc tròn của `Price` thô | hiệu ứng vài phiên – vài tuần | **Kỳ hạn không khớp** với mục tiêu 12–24 tháng ⇒ không đưa vào |
| 9 | Biên độ giá | Kim & Rhee (1997), *J. Finance* (Tokyo) **[A]**; Chen, Gao, He, Jiang & Xiong (2019), *J. Econometrics* (Trung Quốc) **[B]**; "hiệu ứng nam châm": Cho, Russell, Tiao & Tsay (2003), *J. Empirical Finance* **[B]** | Chạm biên trì hoãn khám phá giá, biến động lan sang phiên sau; chuỗi trần thu hút mua đuổi | `n_up60`, `n_dn60`, chuỗi phiên trần/sàn liên tiếp | chuỗi trần: **−** trung hạn; chuỗi sàn: tiếp diễn ngắn hạn | Kho thiếu sàn niêm yết PIT ⇒ ngưỡng 6,5% gộp nhầm HNX/UPCOM |
| 10 | Chuỗi giải chấp margin | Brunnermeier & Pedersen (2009), *Rev. Financial Studies* **[A]**; Bian, He, Shue & Zhou — bán tháo do đòn bẩy ở Trung Quốc 2015 **[C]** | Giá giảm ⇒ gọi ký quỹ ⇒ bán ép ⇒ giảm quá mức rồi hồi | **Không có dữ liệu margin**; proxy: chuỗi phiên sàn + khối lượng | **+** sau bán ép (hồi) | Không tách được bán ép khỏi tin xấu thật |
| 11 | Trôi giá sau công bố KQKD | Bernard & Thomas (1989), *J. Accounting Research* **[A]** | Phản ứng chậm với bất ngờ lợi nhuận | Đã là sổ LAG của production | **+** 1–3 tháng | Đã khai thác ở LAG ⇒ không lặp |
| 12 | Dòng vốn ngoại | Froot, O'Connell & Seasholes (2001), *JFE* **[A]**; Choe, Kho & Stulz (1999), *JFE* (Hàn Quốc) **[A]** | Dòng ngoại dai dẳng, đuổi lợi suất; tác động giá tạm thời hay lâu dài còn tranh cãi | `netVal` theo mã, `currentRoom` (từ 2018-08) | chưa rõ dấu | Không phủ IS; hết room làm méo giá (premium) |
| 13 | Kỳ hạn thanh toán | — (đặc thù quy định, không trích bài) | Hàng về chậm ⇒ không bán được ngay ⇒ rủi ro qua đêm dồn | Không có đặc trưng cắt ngang | — | Thay đổi theo thời kỳ (chu kỳ thanh toán và giờ hàng về đã đổi; **ngày hiệu lực cần Wendy/Winston xác nhận**) ⇒ chỉ là biến chế độ, N ≈ 1–2 |

## Ba điều rút ra cho thiết kế
1. Các hiệu ứng có bằng chứng mạnh nhất và đo được sạch ở VN (#1, #2, #4) đều nói về **thứ hạng lợi suất tương đối**, không nói
   về **mức giá** tương lai. Tài liệu không hỗ trợ ý "tâm giá hành vi dự báo mức giá 1–2 năm tốt hơn giá hôm nay".
2. #1 và #2 và đà là một cụm (tương quan 0,45–0,67) ⇒ thêm cả ba không phải ba bằng chứng độc lập.
3. Các hiệu ứng đặc thù VN đáng kỳ vọng nhất (#9 biên độ, #10 margin, #7 bầy đàn, #12 room) lại đúng là chỗ kho **thiếu dữ liệu**
   (sàn PIT, margin, lệnh cá nhân theo mã, khối ngoại trước 2018).

**Nhận định "cá nhân chiếm > 90% thị trường VN":** là tiền đề user nêu; kho không có tỉ trọng giao dịch theo nhóm nhà đầu tư
(chỉ có giá trị ròng cấp chỉ số) ⇒ **chưa đo**, không dùng làm số trong báo cáo.
