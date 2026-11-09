# DD CSV (Hoá chất Cơ bản Miền Nam) · ứng viên LAG_LO · 09/11/2026 · job `Taylor_20261109_073602`

> Chỉ nghiên cứu, không đặt lệnh hay wire. Định giá được dựng MÙ giá thị trường: giá chỉ được đưa vào ở bước dán nhãn.
> Nguồn chính là **BCTC hợp nhất Q3/2026 gốc** (scan có chữ ký số, CBTT ngày 22/10/2026), lấy từ kho IR chính thức mà `sochemvn.com/quan-he-co-dong` nhúng (`ezir.fpts.com.vn`, gateway FPTS), lưu ở `src/`. Các file khác trong `src/`: giải trình LNST Q2 và Q3, QĐ cưỡng chế BH1, QĐ dừng nhà máy TB2, thông báo thu hồi đất HCM, BCTC soát xét 6T và BCTC kiểm toán 2025 (hai file cuối đã tải nhưng chưa đọc trang ý kiến kiểm toán, xem §9).
> Tái lập: `cd calc && /home/trido/thanhdt/wc_venv/bin/python -I model.py`. Chạy 2 lần cho `run1.txt` = `run2.txt` (md5 38878033…). Khoá giả định ghi **trước** lần chạy đầu ở `calc/LOCK_prerun.txt` (14:45:09 ICT). Minh bạch: giá 22.600 đã biết từ brief trước khi khoá, nhưng không có tham số nào được chỉnh sau khi xem kết quả.

## 1. Kết luận
| | Tâm | P10 | P50 | P90 | Giá 06/11 | Nhãn | % trọng số dưới giá |
|---|---|---|---|---|---|---|---|
| **Trước CK thanh khoản** | 17.569 | 12.957 | 17.455 | 22.261 | 22.600 | TRÊN vùng | — |
| **Sau CK, cỡ 5 tỷ (headline)** | **17.273** | **12.739** | 17.160 | **21.885** | 22.600 | **TRÊN vùng** | 92,8% |
| Sau CK, cỡ sleeve 40 tr | 17.543 | 12.938 | 17.429 | 22.227 | 22.600 | TRÊN vùng | — |

- Giá cao hơn tâm 30,8% và cao hơn P90 3,3%. **Luật 4 không đạt**: ngưỡng là 14.682 ở cỡ 5 tỷ và 14.912 ở cỡ 40 tr.
- **Giá 22.600 ngầm định điều gì.** Có hai cách đọc. (a) LN công ty mẹ ≈ **305,6 tỷ/năm vĩnh viễn**, cao hơn cả TTM 294,5 tỷ (đỉnh 10 năm), tức thị trường coi lãi bất thường từ axit/phốt pho 2026 là mức bền. (b) Hoặc r ≈ **9,66%**, ứng với lãi huy động 12T khoảng 3,6%, so với 7,40% hiện nay.
- **Trả lời câu (1).** LAG bắt đúng một cú surprise thật, trên nền YoY dương: LN mẹ Q3 +47,9%, Q2 +107,6%, 9T +49,5%. Nhưng phần vượt đến từ **giá H2SO4 +249%/+289%** (cú sốc lưu huỳnh) và **phốt pho vàng**. Bobby xếp cú sốc lưu huỳnh là **TẠM THỜI, đang đảo chiều** (độ tin 0,85; lưu huỳnh đã −52% từ đỉnh). Mảng lõi xút–clo ở **đáy 3 năm** giá.
- **Điểm yếu lớn nhất:** gần như toàn bộ lợi nhuận vượt là giá chu kỳ. Thêm vào đó, công ty đang **di dời bắt buộc** toàn bộ sản xuất sang Nhơn Trạch (khoảng 1.840 tỷ, gần bằng vốn CSH mẹ 1.819 tỷ) đúng lúc công suất xút nội địa có thể gần gấp đôi.

## 2. Vì sao LAG chọn (câu 1): surprise, độ bền, nền so sánh
| Kỳ | DT thuần (tỷ) | LN gộp / biên | LNST HN | LN mẹ | YoY LN mẹ | Nguồn |
|---|---|---|---|---|---|---|
| Q3/26 | 814,1 (+59,6%) | 187,7 / **23,1%** (Q3/25: 26,0%) | 96,35 (+60,4%) | **85,40** | **+47,9%** (Q3/25 57,75) | BCTC p3; GT 1591/GT-HCCB |
| Q2/26 | 687,3 (+31,3%) | 230,6 / **33,6%** (Q2/25: 27,4%) | 134,07 (+86,7%) | **130,03** | **+107,6%** (Q2/25 62,64) | GT 1020/GT-HCCB; BQ |
| 9T/26 | 2.129,7 (+40,5%) | 544,1 / 25,5% | 275,76 | **258,32** | **+49,5%** (172,78) | BCTC p3 mã 61 |

**Nguồn gốc phần vượt (theo giải trình của chính công ty):**
- Q2: DT công ty mẹ +187,4 tỷ, do sản lượng NaOH +22%, H2SO4 +27%, **giá H2SO4 +249%**. Công ty con phốt pho thì DT −17%.
- Q3: DT công ty mẹ +188,9 tỷ, chủ yếu **giá H2SO4 +289%** và HCl +72%, các sản phẩm khác chỉ +1–7%. Công ty con phốt pho vàng DT +83,9% (sản lượng +56%, giá +22%).
- Lợi nhuận khác không đáng kể (Q3 0,92 tỷ; 9T 4,10 tỷ). Như vậy surprise là **lợi nhuận kinh doanh thật**, không có khoản một lần kế toán, nhưng **phụ thuộc giá chu kỳ**.
- **Kiểm chéo theo nhóm doanh thu 9T** (thuyết minh VI.1 và VI.3):
  - Thành phẩm: DT 1.772,8 tỷ (+24,5%), LN gộp 483,6 tỷ, biên **27,3%**, gần như không đổi so với 27,5% của 9T/25.
  - **Hàng hoá thương mại: DT 350,3 tỷ, gấp 4 lần (87,0 tỷ cùng kỳ); LN gộp 73,4 tỷ so với 15,4 tỷ.** Đây là mảng nhỏ trước đây, nay đóng góp khoảng 58 tỷ LN gộp tăng thêm. Mặt hàng cụ thể **cần kiểm** (câu hỏi IR, §9).
- **Nền so sánh:** LN mẹ năm 2019–2025 lần lượt là 244,0 / 179,7 / 208,9 / 353,2 / 209,2 / 240,8 / 209,0 tỷ, trung bình **235,0**. TTM 294,5 tỷ là cao thứ hai sau 2022, năm đỉnh xút. Q4/25 chỉ 36,2 tỷ, nên Q4/26 còn có nền thấp.
- **Kết luận câu (1):** surprise thật. Phần **một lần ước khoảng 60–85 tỷ/năm** [ước lượng: 9T vượt cùng kỳ 85,5 tỷ, chủ yếu do giá axit và hàng thương mại]. Bobby (DK) cho giá lưu huỳnh TQ −52% từ đỉnh và axit TQ giảm đều từ T9, nên **không coi là mức bền**. Mô hình chỉ cho TTM vào kịch bản TỐT.

## 3. Bảng cân đối và dòng tiền (30/09/2026, BCTC p1–p4)
- **Tiền và tiền gửi:**
  - Tiền 154,6 tỷ, tiền gửi kỳ hạn trên 3 tháng 630,6 tỷ, vay ngắn hạn 259,6 tỷ (vay ngân hàng tại công ty mẹ), vay dài hạn 0.
  - ⇒ **Tiền ròng 525,6 tỷ ≈ 4.757 đ/cp.**
  - Lợi ích CĐKKS 49,96 tỷ, trừ theo sổ.
- **TSCĐ đã gần hết khấu hao:** nguyên giá hữu hình 1.144,9 tỷ, còn lại **37,1 tỷ**; khấu hao 9T chỉ 16,4 tỷ. ⇒ Biên lợi nhuận hiện nay **chưa gánh khấu hao** của nhà máy mới.
- **Nhơn Trạch đã bắt đầu tiêu tiền:**
  - Capex 9T 265,7 tỷ.
  - XDCB dở dang 77,5 tỷ (trong đó dự án Nhơn Trạch 52,0 tỷ).
  - **Trả trước người bán 242,4 tỷ, tăng từ 29,1 tỷ**: nhiều khả năng là ứng trước thiết bị cho dự án, **cần kiểm**.
  - Chi phí trả trước dài hạn có 294,5 tỷ **tiền thuê đất và phí hạ tầng KCN Nhơn Trạch**, đã trả trước.
- **CFO 9T: +197,8 tỷ** (9T/25: −13,4 tỷ). Hàng tồn kho 529,3 tỷ, dự phòng chỉ 0,34 tỷ.
- **Cổ tức:** toàn bộ LN 2025 (172,8 tỷ) đã trích vào quỹ đầu tư phát triển (thuyết minh 17a). Năm 2025 **không chia cổ tức tiền** cho cổ đông công ty mẹ, khớp với `trailing_yield = NO_DATA` của hệ. Tiền được giữ lại cho Nhơn Trạch.
- **Sở hữu:** Nhà nước (Vinachem) nắm **718,3/1.105,0 tỷ = 65,0%** vốn ⇒ free float ≤ 35%.
- **Khách hàng lớn** (phải thu, thuyết minh V.3):
  - Leoch (ắc quy): 46,9 tỷ.
  - TKV Nhôm Lâm Đồng (alumina): 31,6 tỷ.
  - Lavita: 28,0 tỷ.

## 4. Dự án Nhơn Trạch và di dời BH1 (luật NPV = 0)
**Dữ kiện:**
- **Quy mô và vốn:**
  - Tổng vốn khoảng **1.840 tỷ** (ĐHĐCĐ bất thường 21/07/2025), gồm 632 tỷ vốn tự có và khoảng 1.208 tỷ vay 10 năm (baodauthau 03/07/2025).
  - Công suất thiết kế **307.900 t/năm** quy 100% (danchuphapluat 18/08/2026), gộp 3 nhà máy BH1.
  - Khởi công 24/09/2025. Một số dây chuyền chạy "từ cuối năm 2026", **chưa có ngày vận hành đồng bộ**.
- **Lực ép di dời:**
  - QĐ 2408/QĐ-UBND ngày 07/07/2026 **cưỡng chế tháo dỡ** tài sản trên các thửa đất BH1 (CBTT 13/07).
  - QĐ 1122/QĐ-HĐQT ngày 31/07/2026 **dừng toàn bộ NM Tân Bình 2** trước 15/08/2026.
  - Công ty mô tả cách di dời là "cuốn chiếu, hạn chế tối đa ảnh hưởng", **không cam kết không gián đoạn**.
- **Bồi thường:** đất BH1 là đất thuê lại của Sonadezi. **Không có số bồi thường** công bố.

**Xử lý trong mô hình:**
- **Base:** dự án có NPV = 0. Phần đã chi là tài sản theo giá vốn, nên tiền ròng vẫn cộng đủ 100%. Phần còn phải chi được đối ứng bằng giá trị tương đương.
- **Trục NPV dự án:** −20% / 0 / +20% × 1.840 tỷ, trọng số 0,2/0,6/0,2, **đối xứng, kỳ vọng 0**.
  - Phía (−) có cơ sở DK từ Bobby: công suất xút nội địa có thể từ khoảng 230 lên 430–500 nghìn t vào 2028–30, có ràng buộc clo, xút TQ ở đáy 3 năm.
  - Phía (+): công suất mới lớn hơn nhà máy cũ, cầu alumina dài hạn tăng.
  - Độ lớn 20% là [UL].
- **Trục gián đoạn chuyển tiếp:** 0 / −25% / −50% của một năm LN lõi, trọng số 0,4/0,4/0,2.
  - Cơ sở là QĐ dừng TB2 và QĐ cưỡng chế BH1 (DK). Độ lớn là [UL].
  - Bỏ trục này thì tâm 17.634, +361 đ/cp.
- **Bồi thường BH1** = 0 ở base. Độ nhạy: mỗi +100 tỷ ⇒ tâm 18.162 (+889 đ/cp).

## 5. Vị thế và lợi thế cạnh tranh (5F tầng b): TÁI DÙNG, kiểm nhanh
- **Nguồn tái dùng:** `data/moat_tags.csv`, dòng CSV, asof **2026-06-05** (5 tháng, dưới 12 tháng). Nội dung: **NARROW · COST/SCALE**, ghi là "nhà sản xuất xút–clo chiếm ưu thế phía Nam, nhưng là commodity price-taker", ROIC_Min5Y 14,3%.
- **Kiểm nhanh, có gì đổi hào:**
  1. Lực thứ 6, **hành chính**: di dời bắt buộc toàn bộ cơ sở sản xuất, cùng capex ≈ 1,0× vốn CSH mẹ.
  2. Lực đối thủ: Bobby ghi nhận các dự án Thanh Hoá 50–100 nghìn t, Bảo Lâm 20 → 45 nghìn t, Phú Vinh. Thiếu hụt nội địa thu hẹp, nên bán hàng sẽ chuyển từ "bán phần thiếu" sang cạnh tranh giành khách lớn.
  3. Bằng chứng định lượng, BQ 30/09: ROE_Min5Y **13,66%**, ROIC_Min5Y **14,26%**, xấp xỉ Ke 13,5%. Lợi nhuận siêu ngạch qua chu kỳ **rất mỏng**, nên không đạt điều kiện (i).
  ⇒ **Giữ NARROW, không thưởng tham số moat.** RONIC = Ke; vì ROE_Min5Y ≈ Ke nên giả định này gần như trung tính.
  - Hào thật nhưng hẹp: lợi thế logistics xút lỏng (Bobby ước 30–60 USD/t, chưa kiểm), khách công nghiệp gần nhà máy, và dải sản phẩm gốc clo tiêu thụ được clo (HCl, PAC, javen, clo lỏng), giúp giải ràng buộc clo tốt hơn nhà máy mới.
- **Độ nhạy theo moat:**
  - Nếu thưởng moat (RONIC = ROE5Y 18,3%, g 4%): tâm **18.760** (+1.487), vẫn thấp hơn giá 17,0%. P10/P90 của bản này chưa chạy.
  - Nếu NONE: dùng lại mô hình cơ sở, không trừ (luật 08/11).
- **Đề xuất dòng moat_tags** (không sửa file, human-curated): giữ `NARROW,COST/SCALE`. Đổi `risk1` thành "di dời bắt buộc BH1 → Nhơn Trạch 1.840 tỷ ≈ vốn CSH + công suất xút nội địa ~×2 2027–30; lãi 2026 là cú sốc axit/phốt pho tạm thời".

## 6. Định giá (câu 2)
**Phương pháp:**
- **Công thức:** Giá trị = LN lõi chuẩn hoá / Ke + tiền ròng − CĐKKS + NPV Nhơn Trạch + gián đoạn chuyển tiếp.
- **LN lõi** = LN mẹ chuẩn hoá − lãi tiền gửi sau thuế. Lãi tiền gửi sau thuế lấy 32,65 tỷ/năm (lãi 9T 30,61 tỷ × 4/3 × 0,8) và được trừ ra để không đếm hai lần với tiền ròng.
- **Ke:** r = 13,5% + 1,0 × (lãi huy động 12T − 7,40%). Lãi huy động 12T (06/11) = `cctg_12m(2026-11-02)` **7,40%**, nên **r = 13,50%**.
- **Tăng trưởng:** RONIC = Ke, nên g không tạo giá trị.

**Ba kịch bản**, trọng số **0,25/0,5/0,25** (đối xứng [UL], tiền lệ FPT r3):

| Kịch bản | LN mẹ chuẩn hoá | Cơ sở | Giá trị/cp (trước CK, tại tham số trung tâm) |
|---|---|---|---|
| XẤU | 179,7 tỷ | Năm thấp nhất 2019–25 (2020). Phù hợp với đáy xút và khấu hao Nhơn Trạch | 14.159 |
| CƠ SỞ | 235,0 tỷ | Trung bình 2019–25, gồm cả đỉnh 2022 | **17.866** |
| TỐT | 294,5 tỷ | TTM, giả định lãi axit/phốt pho được duy trì | 21.857 |

**Lưới và kết quả:**
- Lưới **81 kết cục** = kịch bản (3) × dE ±10% (3) × NPV Nhơn Trạch (3) × gián đoạn (3). Phân vị lấy theo trọng số (mid-block).
- Kết quả: tâm/P10/P90 ở §1; min 8.888, max 26.703 (sau CK 5 tỷ).
- **Độ nhạy r (tâm sau CK 5 tỷ):** −100bp 18.345 · −50bp 17.788 · +50bp 16.794 · +100bp 16.348. Muốn tâm chạm giá thì cần r khoảng 9,7%.
- **Đối chiếu nhanh:**
  - P/E giá / LN chuẩn hoá = **10,6x**; P/E TTM = 8,5x; P/B mẹ = 1,37x (BVPS mẹ khoảng 16.461).
  - Nếu tính lãi tiền gửi trong E mà không cộng tiền ròng: 15.299.
- **Cờ DCF tự động "CHEAP ~29.479" (câu 4) là NHIỄU về kết luận.** Lý do: nó dùng thu nhập gần TTM (đỉnh có cú sốc axit) cộng tăng trưởng; P/E TTM 8,5x trông rẻ chính vì mẫu số ở đỉnh. Trên LN chuẩn hoá chu kỳ thì giá không rẻ. Cả bản moat-thưởng 18.760 lẫn bản không gián đoạn và có bồi thường (khoảng 18,5k [ước lượng: 17.634 + 889, chưa chạy cộng gộp]) đều dưới giá.

## 7. Thanh khoản và sizing (câu 5)
- **Số liệu thanh khoản:** σ ngày 2,29%. **ADV250 (trung vị giá trị) 9,22 tỷ**, ADV60 5,75 tỷ; ADV3T của hệ là 6,10 tỷ.
- **Chiết khấu thanh khoản (CK = σ × √(Q/ADV250)):**
  - 5 tỷ: **1,69%**. Q/ADV = 54%, **ngoài vùng hiệu chỉnh** của luật căn bậc hai, nên số này chỉ là chỉ dấu.
  - 40 tr: 0,15%; 10 tr: 0,08%.
- **Thời gian thoát lệnh:**
  - 1 tỷ: 1,1 phiên ở tỷ lệ tham gia 10%.
  - 5 tỷ: 5,4 phiên ở 10%, 2,7 phiên ở 20%.
- **Khẩu phần plan thực tế:**
  - ≤ 1 tỷ một lần vào (≈ 11% ADV250, ≈ 17% ADV60) là mức thực thi được.
  - Trên 1 tỷ phải chia tối thiểu 2–3 phiên.
  - Free float ≤ 35% (Nhà nước 65%), nên thanh khoản khó cải thiện mang tính cấu trúc.
- **Nhãn không đổi theo cỡ:** TRÊN vùng ở cả 10 tr, 40 tr và 5 tỷ.

## 8. Rủi ro và điều làm nhận định đổi theo CẢ HAI chiều (câu 3)
**Lớn nhất:** LN 2026 được nâng bởi giá axit/phốt pho (tạm thời theo Bobby) trong khi mảng lõi xút ở đáy. Năm 2027–28 có thêm khấu hao và lãi vay của khoản đầu tư 1.840 tỷ, cùng rủi ro gián đoạn khi di dời và cạnh tranh công suất nội địa.

**Mốc làm nhận định đổi:**

| Chiều | Mốc khoá trước (kiểm bằng BCTC/CBTT) | Tác động |
|---|---|---|
| **NÂNG** | LN mẹ Q4/26 ≥ 70 tỷ (gấp khoảng 2 lần nền 36,2) **và** Q1/27 ≥ 60 tỷ, sau khi lưu huỳnh đã giảm | Bằng chứng mức LN mới khoảng 270–300 tỷ bền ⇒ dời trọng số sang TỐT. Tâm có thể lên khoảng 20–21k [ước lượng], vẫn phải so lại với giá |
| NÂNG | Nhơn Trạch vận hành đồng bộ, đúng hạn và đúng dự toán, kèm hợp đồng khách lớn (alumina/lọc dầu) có giá | Trục NPV nghiêng (+) |
| NÂNG | Công bố bồi thường di dời BH1 | +889 đ/cp mỗi 100 tỷ |
| NÂNG | Lãi huy động 12T −100bp | +1.072 đ/cp |
| **HẠ** | Biên gộp quý về dưới 20% hoặc LN mẹ quý dưới 40 tỷ trong giai đoạn di dời | Dời trọng số sang XẤU / gián đoạn −50% |
| HẠ | Vượt dự toán Nhơn Trạch hoặc trễ trên 6 tháng, có tín hiệu cụ thể | Trục NPV (−) |
| HẠ | Lưu huỳnh/axit tiếp tục giảm theo forecast Bobby (`sulfur` TB5 < 5.271,75 vào 08/01/2027, P = 0,62) | Xác nhận mức TTM không bền |

**HARD ABANDON** (với tư cách ứng viên giữ dài): kiểm toán ngoại trừ BCTC 2026; dừng sản xuất trên 1 quý mà không có công suất thay thế; vay để chia cổ tức.

## 9. Pháp lý và quản trị (chỉ WARNING, không đưa vào tâm)
- **Cưỡng chế tháo dỡ BH1** (QĐ 2408, 07/07/2026) là thi hành đề án chuyển đổi KCN Biên Hoà 1, không phải xử phạt. Rủi ro là vận hành, không phải hình sự.
- **UBND TP.HCM thu hồi khu đất** do CSV "không còn nhu cầu, tự nguyện trả lại" (CBTT 19/10/2026): **chưa đọc nội dung, không có số bồi thường**.
- **Giao dịch bên liên quan 9T:** chủ yếu với các công ty cùng Vinachem (LIX, NET, Pin Ắc quy MN, Phân bón MN, Thiết kế CN Hoá chất 17,6 tỷ dịch vụ), giá trị nhỏ. HĐQT đã ra nhiều NQ chấp thuận giao dịch NCLQ trong năm 2026 (02, 04, 07, 08); **chưa đọc nội dung các NQ này**.
- **Nhân sự:** đổi Chủ tịch ngày 25/04/2026 (Khúc Ngọc Giảng thay bà Nguyễn Thị Mai) và đổi người phụ trách KTNB ngày 06/07/2026.
- **Kiểm toán:** đã tải BCTC soát xét 6T/2026 và kiểm toán 2025 nhưng **chưa đọc trang ý kiến** ⇒ mục cần kiểm (G1).
- **Câu hỏi IR / GAPS:**
  - G1: ý kiến soát xét 6T và kiểm toán 2025.
  - G2: khoản trả trước người bán 242,4 tỷ là gì.
  - G3: hàng hoá thương mại 350 tỷ là mặt hàng nào, biên có bền không.
  - G4: lịch dừng từng dây chuyền BH1 và lịch chạy Nhơn Trạch.
  - G5: bồi thường BH1 và đất HCM.
  - G6: H2SO4 sản xuất từ đốt lưu huỳnh hay mua thương mại (nhà cung cấp Deltacorp, Kompass, Marubeni, Tricon nằm trong phải trả).

## 10. Cờ tự động của hệ (câu 4)
| Cờ | Đánh giá | Bằng chứng |
|---|---|---|
| **W IDIOCRASH 2026-07-27** | **NHIỄU** | Ngày 27/07 CSV −6,98% (21.500 → 20.000) trong khi VNINDEX −1,0% (1.686,11 → 1.669,01). Khối lượng 546k, vol_x 1,46, không phải bán tháo. Cùng ngày còn MBS và VND bị cờ (`anomaly_flags.json`). Không có CBTT ngày 27/07: tin cưỡng chế ra 13/07, KQ Q2 tốt ra 21/07. Phiên sau giá hồi +3,75%, và Q3 ra sau đó vẫn tốt. Có thể là bán do tin cưỡng chế ngấm chậm [ước lượng], nhưng không có dữ kiện cơ bản xấu mới |
| ROE5Y 18,3% | Thật nhưng **dễ hiểu sai** | Trung bình 5 năm gồm đỉnh 2022 (353 tỷ). ROE_Min5Y 13,66% ≈ Ke |
| **DCF auto CHEAP ~29.479** | **Nhiễu về kết luận** | Thu nhập gần đỉnh chu kỳ (axit), xem §6. Trên LN chuẩn hoá thì TRÊN vùng |
| moat NARROW COST/SCALE (06/2026) | Thật, tái dùng | §5 |
| ADV3T 6 tỷ | Thật | §7. ADV60 5,75 tỷ, giới hạn khẩu phần ≤ 1 tỷ/lần |
| Không cổ tức tiền 2025 | Thật | LN 2025 trích hết vào quỹ ĐTPT cho Nhơn Trạch (thuyết minh 17a) |

## 11. Giả định [UL] / tự đặt (đầy đủ ở `calc/assumptions.json`, mỗi mục có cơ sở và nguồn)
- Trọng số kịch bản 0,25/0,5/0,25 [UL].
- dE ±10% [UL].
- NPV Nhơn Trạch ±20% (0,2/0,6/0,2) [UL, kỳ vọng 0].
- Gián đoạn 0/−25/−50% một năm LN lõi (0,4/0,4/0,2) [UL].
- Lãi tiền gửi sau thuế 32,65 tỷ/năm [ước lượng từ 9T].
- RONIC = Ke.
- Bồi thường = 0.
- CĐKKS trừ theo sổ.
- Mức "phần một lần 60–85 tỷ" [ước lượng].

## 12. File
- `REPORT.md`, `SUMMARY.json`.
- `calc/`: `model.py`, `assumptions.json`, `LOCK_prerun.txt`, `LOCK_post_md5.txt`, `run1/run2.txt`, `model_out.json`, `fin_csv_bq.csv` (+ `.sql`), `px_csv.csv` (+ `.sql`).
- `src/`: PDF gốc và `png/` các trang đã đọc.
- Không sửa `kb/dd_price_zones.json` (Mike ghi sau skeptic). Không email, không PDF.
- ⚠ Hai file `.sql` được viết lại sau khi chạy (bản đầu bị `wc_env.sh` đổi cwd nên ghi lạc ra thư mục gốc rồi bị xoá). Nội dung SQL trùng với truy vấn đã chạy; md5 được ghi ở `LOCK_post_md5.txt`, không có trong `LOCK_prerun.txt`.

Nguồn web: [Báo Pháp luật 27/10/2026 KQ Q3](https://doanhnhan.baophapluat.vn/hoa-chat-co-ban-mien-nam-csv-bao-lai-quy-3-tang-48-huong-loi-tu-da-tang-gia-axit-va-phot-pho-vang.html) · [danchuphapluat 18/08/2026](https://danchuphapluat.vn/hoa-chat-co-ban-mien-nam-loi-nhuan-6-thang-but-pha-nha-may-hoa-chat-nhon-trach-tang-toc-ve-dich-10156.html) · [baodauthau 03/07/2025, 1.840 tỷ](https://baodauthau.vn/cong-ty-cp-hoa-chat-co-ban-mien-nam-du-kien-dau-tu-1840-ty-dong-xay-nha-may-tai-nhon-trach-post181151.html) · [baodauthau 28/03/2026 gói thầu](https://baodauthau.vn/3-nha-thau-canh-tranh-xay-nha-may-hoa-chat-nhon-trach-post196043.html) · [Tạp chí Công Thương 22/07/2026](https://tapchicongthuong.vn/tong-giam-doc-vinachem-nguyen-huu-tu-kiem-tra-tien-do-du-an-nha-may-hoa-chat-nhon-trach-535908.htm) · [Đại biểu Nhân dân 26/09/2025](https://daibieunhandan.vn/khoi-cong-nha-may-hoa-chat-nhon-trach-buoc-ngoat-phat-trien-cua-hoa-chat-co-ban-mien-nam-10388014.html) · [DSC cập nhật Q2/2026](https://extgw.dsc.com.vn/eback/uploads/BCCN_CSV_Q2_2026_acbfc95985.pdf) (chỉ đọc tóm tắt tìm kiếm).
