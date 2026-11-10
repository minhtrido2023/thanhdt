# SCL — cập nhật sau GDKHQ r4 (10/11/2026, job Taylor_20261110_034232)

Nền: `dd_redo_20261105/SCL/REPORT_r3.md`. Định giá doanh nghiệp **không làm lại** (mù giá). r3 đã dựng sẵn lưới sau quyền (`calc_r3/model_scl_r3_out.json → post_rights`). Bản này chỉ thay giá cum bằng giá giao dịch thực tế sau GDKHQ, rồi kiểm số cp, ESOP và kịch bản bao phủ.
Calc: `calc/dilution_calc.py` (output trùng byte 2 lần, `calc/dilution_out.json`).

## 0. Kết luận — **TRÊN vùng, không đổi; khoảng cách so với P90 nới rộng**

| Cơ sở (sau quyền, phát hành đủ, 44.836.815 cp) | Tâm | P10 | P50 | P90 | Giá EX | Giá / P90 | Giá / tâm | Nhãn | Luật 4 |
|---|---|---|---|---|---|---|---|---|---|
| **CK 5 tỷ (cỡ ghi sổ)** | **21.339** | 17.445 | 20.964 | **25.681** | **28.000** (BQ đóng cửa 09/11) | **+9,0%** | +31,2% | **TRÊN** | KHÔNG (ngưỡng 18.138) |
| CK sleeve 40 tr | 22.146 | 18.104 | 21.756 | 26.651 | 28.000 | +5,1% | +26,4% | TRÊN | KHÔNG (18.824) |
| Giá DNSE 10/11 10:18 ICT | | | | | 28.300 (khớp 690 cp — chưa có KL cả phiên, thanh khoản mỏng) | +10,2% / +6,2% | | TRÊN | |

- **So cùng cỡ:** cum 5 tỷ: giá 29.400 / P90 27.803 = **+5,7%**; ex 5 tỷ: 28.000 / 25.681 = **+9,0%**. Cum 40 tr: +1,9% (r3); ex 40 tr: +5,1%. Sau GDKHQ, giá 28.000 cao hơn P90 sau quyền **+5,1%** (40 tr) và **+9,0%** (5 tỷ).
- Nguyên nhân: giá ex **cao hơn TERP 27.139 là +3,2%** (09/11), tức cổ phiếu tăng giá thực khi đã điều chỉnh quyền. Giá trị định giá không đổi.
- Quy đổi về cum, giá 09/11 tương đương **30.394** (+3,4% so với 29.400 ngày 06/11).
- Kết luận "TRÊN vùng" **không đổi** ở mọi biến thể r3, cả hai cỡ CK, và các kịch bản bao phủ 50–100% (§3).

## 1. Sự kiện (đã xảy ra)
- **NQ 1363/NQ-HĐQT ngày 26/10/2026** (PDF gốc `dd_SCL_20261029/src/nq_1363_chotquyen_27102026.pdf`, đã kiểm ở r3 §1 #4) quy định:
  - tỷ lệ 100:15,4453;
  - giá **12.500**;
  - ĐKCC 10/11; **GDKHQ 09/11**;
  - chuyển nhượng quyền 17/11–03/12;
  - đăng ký và nộp tiền 17/11–08/12.
- BQ `corporate_action` có dòng ISS `announced` với exright 2026-11-09 và record 2026-11-10, khớp với NQ.
- Số cp trước quyền là **38.836.815**:
  - BQ `ticker.OShares` = 38.836.815;
  - AIS 17/09/2026 (+920.000 ESOP, tổng 38.836.815);
  - vốn góp 388,4 tỷ trong BCTC Q3, theo r3.
- Phát hành mới: 38.836.815 × 15,4453% = **5.998.463 cp**. Tiền thu ≈ **74,98 tỷ**, chưa trừ chi phí. Số cp chào bán theo TB 1368/TB-SCL: **6.000.000 cp mới = 75 tỷ**; 5.998.463 chỉ là phần theo tỷ lệ quyền (calc dùng 5.998.463, chênh 1.537 cp = 0,003% ⇒ không đổi số làm tròn). Sau quyền: **44.836.815 cp**, khớp "44,84 tr" ở r3.
- **ESOP 0,92 tr** (ISS executed 03/08/2026, ratio 2,43%, @10.000 theo REPORT gốc) **đã nằm trong 38,84 tr**. Không cộng thêm lần nữa.

## 2. ESOP "đợt 2" 2,1% (announced 07/05/2026) — **KHÔNG XÁC ĐỊNH ĐƯỢC nguồn gốc**
- Dữ liệu trong BQ:
  - Dòng ISS public 07/05/2026: ratio 0,021, issue_volumn 0, không có ngày nào, source_news 11998383 (fiinpro, không truy cập được).
  - Đợt ESOP đã thực hiện có first_disclosure 28/05/2026 (cùng lúc cổ tức CP 17%) và ra 920.000 cp.
  - Không có AIS ESOP thứ hai.
- Website công ty (songdacaocuong.com.vn, mục ĐHĐCĐ) chỉ cập nhật tới 2016. WebSearch 10/11 không ra văn bản nào về ESOP 2026 thứ hai.
- **Nhận định, chưa kiểm:** dòng 2,1% nhiều khả năng là bản công bố ở ĐHĐCĐ cho **chính đợt ESOP 920.000 cp** đã thực hiện, và vendor không đóng trạng thái. Không có văn bản để khẳng định.
- **Phép tính 2,1%:** 920.000 / (37.916.815 + 6.000.000) = **2,095%** — đúng 2,1% ở **cả hai cách đọc**: (a) dòng 2,1% là **bản trùng** của chính 920.000 cp đã thực hiện (đã nằm trong 38,84 tr); (b) là **ESOP riêng** phát hành sau quyền (≈ 0,92 tr cp thêm trên 43,92 tr; độ nhạy bên dưới dùng 2,1% × 44,84 tr ≈ 0,94 tr, cận trên). Hai cách đọc cùng cho 2,095% ⇒ phép chia KHÔNG phân biệt được.
- **CHƯA đóng.** Chưa nên nhờ Winston đóng dòng vendor trước khi đọc **NQ 486/NQ-ĐHĐCĐ 24/04/2026** (hoặc bản cáo bạch) để xác định ESOP 2026 có 1 hay 2 đợt. Tôi chưa đọc 2 văn bản này.
- **Độ nhạy nếu là ESOP riêng** (thêm ≈ 0,94 tr cp @10.000 sau quyền):
  - 5 tỷ: tâm 21.106, P90 25.358 (−233 / −323);
  - 40 tr: tâm 21.896, P90 26.309.
  - Nhãn TRÊN không đổi.

## 3. Kịch bản bao phủ
- Tính lại từ phân phối cum r3: V = (V_cum × 38,84tr + (1 − CK) × c × 74,98 tỷ (75 tỷ theo TB)) / (38,84tr + c × 6,0tr).

| c | Tâm 5 tỷ | P90 5 tỷ | Tâm 40 tr | P90 40 tr | Nhãn @28.000 |
|---|---|---|---|---|---|
| 1,0 (đủ) | 21.340 | 25.681 | 22.146 | 26.652 | TRÊN |
| 0,5 | 22.013 | 26.666 | 22.845 | 27.674 | TRÊN |
| 0 (huỷ) | 22.791 | 27.803 | 23.652 | **28.854** | 5 tỷ TRÊN; **40 tr TRONG** (28.000 < 28.854) |

- Đã sửa kịch bản 40 tr: áp CK 40 tr (disc_40tr = 0,843%) lên tiền thu như r3. Tại c = 1 tâm **22.146 / P10 18.104** khớp r3 đúng; P90 26.652 vs 26.651 (làm tròn). (Bản vòng 1 dùng nhầm CK 0 ⇒ 22.160, đã sửa.)
- **Bao phủ đủ rất có khả năng:**
  - Quyền đang có giá trị nội tại theo thị trường **15.500 đ/cp mới** (28.000 − 12.500), tức **2.394 đ/cp cũ**.
  - Đợt trước bán được 97,5%, lãnh đạo mua nốt phần dư (tin [baophapluat](https://doanhnhan.baophapluat.vn/song-da-cao-cuong-scl-ban-thanh-cong-975-luong-co-phieu-chao-ban-lanh-dao-gom-not-hang-du-de-tra-no-bidv-89369.html)). Bài báo không ghi năm. Tôi gán nó cho đợt 10/2025 vì tỷ lệ 28:10 = 35,7% khớp dòng BQ ISS 10/2025 (executed, 8.000.000 cp, AIS 19/01/2026).
  - Kịch bản huỷ tương đương "HARD ABANDON: quyền mua bị huỷ hoặc đổi điều khoản" của r3.

## 4. Kiểm điều chỉnh ex trong dữ liệu
- **Giá tham chiếu 09/11:** theo lý thuyết, TERP trên giá đóng cửa 06/11 là 27.139. SCL niêm yết **UPCOM** (DNSE secdef `marketId=UPX`), nên tham chiếu tính từ giá bình quân phiên trước. Vì vậy không so trực tiếp được với 27.139; phiên này không đọc được secdef ngày 09/11. Biên độ phiên 09/11 là 27.700–29.000, nhất quán với tham chiếu khoảng 27.1xx.
- **Tham chiếu 10/11** = 28.100 (DNSE secdef 08:01, = bình quân 09/11). Trần 32.300, sàn 23.900.
- ⚠ **BQ `tav2_bq.ticker` chưa điều chỉnh lùi chuỗi `Close` cho quyền** (đọc sau sync 09/11): ngày 06/11, Close = Price = 29.400. Hệ số kỳ vọng 27.139 / 29.400 = 0,9231. Mọi phép tính lợi suất hoặc chỉ báo SCL qua mốc 09/11 trên BQ sẽ thấy cú giảm giả −4,8% (28.000 / 29.400 − 1). Cần báo Winston (data-ops) theo dõi lần sync kế.
- Phiên 09/11 khớp 45.100 cp, mỏng hơn trung bình r3 (ADV120 ≈ 2,35 tỷ).

## 5. Hệ quả vận hành
- Không có vị thế: SCL đã thoái hết khỏi LAG ngày 30/10 (luật user 29/10). Bản này **không** tạo hành động mua.
- Luật 5 (mua LAG cần DD + giá ≤ tâm): giá 28.000 cao hơn tâm 21.339 tới +31%, nên không đạt.
- WARNING tăng vốn (luật 29/10): đã kích hoạt ở r3, giữ nguyên.
- Mốc lên/xuống và HARD ABANDON giữ như r3 §8. Ngưỡng nhãn mới, tính trên **giá EX**:
  - về TRONG khi giá ≤ **25.681** (5 tỷ) hoặc ≤ 26.651 (40 tr);
  - luật 4 đạt khi ≤ **18.138** (5 tỷ).
