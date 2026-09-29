# VIC-family — Khung GIÁM SÁT nền (background monitoring), 2026-08-22

> Taylor (Quant/Algo), job `Taylor_20260822_022947`, dispatch từ Mike. **Research-only — KHÔNG wire
> production, KHÔNG có tín hiệu mua/bán nào phát sinh từ file này.**

## 0. Mục đích — đọc trước, đừng dùng sai

User coi VIC/Vingroup là case **"too big to fall"**: quá lớn để sụp một cách âm thầm, nhưng cũng quá
lớn để bỏ qua nếu thật sự có chuyện. Nhu cầu vì vậy là **GIÁM SÁT LIÊN TỤC**, không phải nghiên cứu
đầu tư. Ba ranh giới cứng, vi phạm bất kỳ cái nào là dùng sai file này:

1. **KHÔNG phải tín hiệu mua/bán.** Không có ngưỡng nào ở đây được phép nối thẳng vào sizing, filter,
   hay `trading_rules.json`. Đầu ra duy nhất của mọi alert = **một dòng báo cho user đọc**.
2. **KHÔNG dựng cò súng trên tỷ số tài chính.** Đã TEST và BÁC BỎ:
   `vic_family_credit_concentration_20260818.md` §3 cho thấy `Debt_Eq` không có giá trị định thời —
   quý đòn bẩy CAO NHẤT lịch sử (2024Q4, Debt_Eq 4,44) là quý mà 12 tháng sau giá VIC **+709,5%**.
   Một cổng "Debt_Eq vượt ngưỡng → cảnh báo bán" sẽ bắn liên tục từ 2022Q2 và bỏ lỡ toàn bộ đợt tăng
   đó. Tỷ số tài chính ở đây dùng để **đọc mức độ nghiêm trọng khi tin xấu THẬT đã đến**, không phải
   để dự đoán tin xấu.
3. **Kênh lan truyền chính tới portfolio là GIÁN TIẾP** — qua sổ ngân hàng (17–36% NAV), không phải
   qua việc cầm VHM/VRE trực tiếp (2,6–8,1% NAV, đến từ screen custom30V định kỳ chứ không phải cược
   chủ đích). Nếu một ngày Tầng 2 mở thật, câu hỏi hành động đúng có thể là "tỷ trọng ngân hàng",
   không phải "bán VHM/VRE" — nhưng hiện **KHÔNG có dữ liệu** để biết ngân hàng nào exposure cao hơn
   (`vic_family_credit_concentration_20260818.md` §5).

**Quan hệ với hạ tầng đã có:** khung này KHÔNG dựng cơ chế mới. Nó là **bản đồ diễn giải** đặt lên
trên `fearbuy_weekly_scan.sh` (đã chạy 2 lần/tuần: Thứ Hai 08:00 + Thứ Sáu 08:10 ICT, nhóm từ khoá
`c) NHÓM BĐS ĐẦU NGÀNH/HẠ TẦNG CÔNG` thêm 2026-08-18, commit `38b8c835` + `68ff3998`) và
`anomaly_scan.py` (IDIOCRASH/FLOOR2, chạy trong cùng script). Khung 3 tầng (Tầng 0 xếp hạng tổn
thương / Tầng 1 phát hiện / Tầng 2 cân nhắc hành động — cần user duyệt) giữ nguyên như đã chốt
2026-08-14 cho nhóm ngân hàng.

---

## 1. Taxonomy 5 loại tín hiệu cảnh báo sớm

Sắp theo **thứ tự thời gian nhân quả**, không phải theo mức nghiêm trọng: (e) chính sách đi trước,
(a)/(b) là giá của vốn phản ứng, (c) là hệ quả của áp lực thanh khoản, (d) là con số kế toán xác nhận
sau cùng. Cột "Độ trễ" = khoảng cách giữa lúc vấn đề tồn tại thật và lúc mình nhìn thấy được.

| # | Loại tín hiệu | Cơ chế | Độ trễ | Đã quan sát được gì (2026-08) |
|---|---|---|---|---|
| **(a)** | **Chi phí vốn bất thường** — spread lãi vay USD/VND, hạ bậc tín nhiệm | Thị trường trái phiếu định giá lại rủi ro tín dụng TRƯỚC khi có sự kiện vỡ nợ | **Tuần–tháng** (nhanh nhất trong 5 loại) | Trái phiếu VND 3 năm VHM 06→08/2026 **12,5%/năm ổn định** ở 3 lô liên tiếp; VPL 12% sàn. Rating nội địa Vinhomes **vnAA "Ổn định"** (Saigon Ratings), S&I "rủi ro thấp" |
| **(b)** | **Dấu hiệu hết hạn mức tín dụng** — rollover khó, covenant, huỷ/hoãn phát hành | Khi kênh vốn tắc, DN buộc lộ ra qua hành vi phát hành | Tuần–tháng | Không có dấu hiệu tắc: VHM phát hành liên tục 06/2026 (6.000 tỷ), 07 (3.000 tỷ), 08 (2.000 tỷ) — đều thành công |
| **(c)** | **Pledge ratio leo thang** — cầm cố cổ phiếu, chuyển nhượng "đảm bảo nghĩa vụ trái phiếu", giải chấp | Cổ phiếu làm TSĐB → giá giảm làm tỷ lệ TSĐB/dư nợ tụt → bổ sung TSĐB hoặc giải chấp → áp lực bán TỰ CỦNG CỐ | **Ngày–tuần** khi đã kích hoạt, nhưng **tích tụ âm thầm hàng tháng** | Cận dưới đo được: 40tr CP VIC (0,52% lưu hành / **1,89% free float**) + 20,2tr CP VHM (0,49% / **1,45%**). TSĐB/dư nợ ~200% theo rating agency (còn dư địa). **2 đợt chuyển nhượng VHM cách nhau ~6 tuần** (06/2026, 04-05/08/2026) |
| **(d)** | **Cash-flow coverage suy giảm** | Khả năng trả lãi bằng dòng tiền hoạt động, thay vì bằng vốn vay mới | **Quý + 45 ngày** (chậm nhất — nhưng là kênh KHÓ NGUỴ TRANG NHẤT) | `ROE_Trailing` VIC cải thiện rõ: 1,4–3,3% (2022-24) → 7,1% (2025Q4) → **16,0% (2026Q2)**. `CF_Invest_3Y` = **−179,3 nghìn tỷ**, capex ra liên tục và tăng đều |
| **(e)** | **Chính sách / regulatory** | Cơ chế ưu đãi tín dụng riêng cho nhóm này là **do chính sách tạo ra** ⇒ đảo chính sách là rủi ro hệ thống, không phải rủi ro DN | Ngày (công bố) nhưng **báo hiệu trước hàng quý** | Công văn **5368/NHNN-TD (22/06/2026)**: loại trừ dư nợ 18 dự án hạ tầng của Vingroup/Sun Group/Masterise (**>752.000 tỷ** cho cả 3) khỏi cách tính tăng trưởng tín dụng |

**Vì sao 5 loại này mà không phải loại khác:** cả 5 đều là **bằng chứng rời rạc, công khai, kiểm chứng
được** — đúng dạng tín hiệu mà `bank_tailrisk_insurance_design_20260814.md` kết luận là kênh duy nhất
hoạt động ở VN cho rủi ro đuôi. Ba thứ **CỐ Ý không nằm trong danh sách**: giá cổ phiếu (đã test, không
định thời được), `Debt_Eq`/tỷ số đòn bẩy (§0 mục 2), và tail-asymmetry trần/sàn (đã test N=225 ở
`vic_pinning_hypothesis_and_creditrate_proxy_20260818.md` §C.1 — VIC nằm ở **percentile 0,9%**, phần dư
ÂM, tức đi NGƯỢC giả thuyết neo giá; VHM z=1,36 chưa vượt ngưỡng z≥2).

---

## 2. Nguồn dữ liệu — cái gì lấy được, cái gì KHÔNG

### 2.1 BQ `tav2_bq.ticker_financial` — chỉ phục vụ (d), tần suất quý

| Trường | Dùng cho | Ghi chú |
|---|---|---|
| `StDebt_P0`, `LtDebt_P0` | Tổng nợ vay. VIC 2026Q2 = 137.278 + 218.477 = **355.755 tỷ** | **VERIFIED 2 nguồn độc lập**: số BQ khớp gần tuyệt đối với báo chí trích BCTC (355.756 tỷ) |
| `IntCov_P0`, `IntCov_P4` | Interest coverage — trụ cột chính của (d) | Kênh trực tiếp nhất cho "trả lãi bằng dòng tiền hay bằng nợ mới" |
| `CF_OA_P0..P4`, `CF_OA_3Y` | Dòng tiền hoạt động / tài sản | So với nghĩa vụ lãi để ra coverage thật |
| `CF_Invest_3Y` | Capex ra | VIC −179,3 nghìn tỷ, tăng đều từ −139,5 (2022Q4) |
| `ROE_Trailing` | Hiệu quả vốn 4 quý gần nhất | Đã hồi phục mạnh 2025Q4→2026Q2 |
| `Debt_Eq_P0` | **CHỈ Tầng 0** — đọc mức độ tổn thương, KHÔNG làm cò súng | §0 mục 2 |

**Bẫy dữ liệu phải nhớ:**
- **BCTC hợp nhất tập đoàn** — `ticker_financial` cho VIC đã bao gồm VHM/VRE/VPL. **KHÔNG cộng dồn**
  nợ VIC + VHM + VRE kẻo đếm trùng.
- **VRE: dữ liệu BQ dừng ở 2023Q4**, chưa xác minh được lý do (khả năng: đổi cấu trúc sở hữu / không
  còn báo cáo riêng trong nguồn). **KHÔNG suy diễn** — cần Winston xác minh nếu muốn dùng VRE.
- **VPL mẫu quá ngắn** (niêm yết 2025Q1) — không kết luận xu hướng.
- **Trễ công bố ~45 ngày** — mọi so sánh point-in-time phải trừ độ trễ này (giống cách xử lý CASA/LDR
  ở bank report), nếu không là look-ahead.

### 2.2 Nguồn công khai (WebSearch qua `fearbuy_weekly_scan.sh`) — phục vụ (a)(b)(c)(e)

| Loại | Nguồn thực tế đã dùng được | Ghi chú |
|---|---|---|
| (a) lãi suất trái phiếu mới | cafef / vietstock / stockbiz — bản tin phát hành trái phiếu | Chỉ lô **PHÁT HÀNH MỚI** mới là giá thị trường. Lô cũ đang thanh toán (VD VIC 8,5%) **KHÔNG** dùng làm proxy hiện tại |
| (a) rating | Saigon Ratings, S&I Ratings, FiinRatings | FiinRatings có Vingroup trong danh mục nhưng **không công khai mức hạng cụ thể** |
| (b)(c) công bố thông tin | HOSE/UBCKNN, bản tin "giao dịch cổ phiếu của tổ chức có liên quan của người nội bộ" | Cách công bố THẬT dùng cụm **"chuyển nhượng cổ phiếu … đảm bảo nghĩa vụ thanh toán trái phiếu"** — đã thêm vào từ khoá scan (commit `68ff3998`) vì khác hẳn từ vựng "cầm cố" |
| (e) chính sách | Công văn NHNN, thông tư SBV | Công văn 5368/NHNN-TD là tiền lệ: cơ chế loại trừ room có thể bị đảo |
| (c) giá/khối lượng bất thường | `anomaly_scan.py` IDIOCRASH/FLOOR2 — **đã chạy sẵn** | Kênh phát hiện NHANH HƠN tin tức cho biến động giá; WebSearch chỉ bổ sung NGUYÊN NHÂN |

### 2.3 KHÔNG lấy được — khai rõ, không suy diễn thay

| Cái gì | Vì sao | Muốn có thì cần gì |
|---|---|---|
| **Tổng khối lượng cầm cố VIC-family / free float** | Không tồn tại nguồn tổng hợp công khai. 6 lượt WebSearch (2026-08-18) không tìm ra cổng tra cứu nào của HOSE/SSC | Tra công bố định kỳ từng đợt theo mã trên HOSE/UBCKNN — **job riêng**, tốn nhiều lượt |
| **Exposure của từng ngân hàng niêm yết tới nhóm BĐS lớn** | `bigquery_dictionary.json` **không có cột nào** cho cơ cấu dư nợ theo ngành ở cấp ngân hàng | Thuyết minh BCTC ngân hàng (OCR/nhập tay như CASA/LDR) hoặc report ngành CTCK — **job riêng** |
| **Lãi suất áp dụng cho gói 752.000 tỷ loại trừ room** | Không công bố | — |
| **Đã từng có margin-call/giải chấp thật với VIC-family chưa** | WebSearch chỉ trả nội dung giáo dục chung về "call margin" | **KHÔNG kết luận "chưa từng xảy ra"** — chỉ là không tìm thấy |
| **Tỷ trọng riêng VIC (tách khỏi Sun/Masterise) trong 752.000 tỷ** | Không công bố tách | — |

---

## 3. Ngưỡng alert đề xuất — khi nào báo tay cho user

**Nguyên tắc chi phối:** mỗi ngưỡng dưới đây kích hoạt **MỘT DÒNG BÁO CHO USER ĐỌC**, không kích hoạt
hành động nào. Điều kiện Tầng 2 (cân nhắc hành động) giữ nguyên như đã chốt 2026-08-14 và **không đổi
trong file này**: cần **≥2 tín hiệu độc lập, bắt buộc có ≥1 tín hiệu solvency thật** (vỡ nợ trái phiếu,
hạ bậc tín nhiệm, siết nợ thật) — **giá hay Debt_Eq KHÔNG tính là tín hiệu solvency**.

| Loại | Ngưỡng đề xuất | Cơ sở đặt ngưỡng | Mức |
|---|---|---|---|
| **(a)** | Lô trái phiếu VND **phát hành mới** kỳ hạn ~3 năm của VIC/VHM/VPL có lãi suất **≥14,0%/năm** (tăng ≥1,5đ% so mốc 12,5% hiện tại) | 3 lô liên tiếp 06→08/2026 đều đúng **12,5%** ⇒ mốc rất ổn định, lệch 1,5đ% là đổi chế độ thật chứ không phải nhiễu | ⚠️ ALERT |
| **(a)** | **Bất kỳ** hạ bậc tín nhiệm nào (Saigon Ratings / S&I / FiinRatings / tổ chức quốc tế) đối với bất kỳ pháp nhân nào trong nhóm | Hiện vnAA "Ổn định"; hạ bậc = tổ chức chuyên môn độc lập đổi ý ⇒ tín hiệu solvency đủ tư cách cho Tầng 2 | 🔴 SOLVENCY |
| **(a)** | Trái phiếu **USD** phát hành mới có coupon **≥8,0%/năm** (mốc kế hoạch Q2/2026: ≤5,75%) | Cùng logic spread, nhưng **cẩn thận**: chênh USD–VND phần lớn là **basis tiền tệ**, không phải rủi ro tín dụng thuần ⇒ chỉ đọc theo chuỗi USD-vs-USD | ⚠️ ALERT |
| **(b)** | Một đợt phát hành trái phiếu đã công bố kế hoạch bị **huỷ/hoãn/giảm quy mô >30%**, hoặc phát hành thành công **<70%** khối lượng chào bán | VHM 06→08/2026 phát hành trót lọt 3 lô liên tiếp ⇒ hụt là đứt mạch rõ ràng | ⚠️ ALERT |
| **(b)** | Bất kỳ tin **chậm/không thanh toán lãi hoặc gốc trái phiếu đến hạn**, kể cả 1 ngày | Không có ngưỡng nào dưới mức này có ý nghĩa | 🔴 SOLVENCY |
| **(b)** | **Ngân hàng siết nợ / thu hồi tài sản đảm bảo** — bất kỳ quy mô | Sự kiện rời rạc, tự nó là bằng chứng | 🔴 SOLVENCY |
| **(c)** | **≥3 đợt** công bố "chuyển nhượng cổ phiếu đảm bảo nghĩa vụ trái phiếu" trong **90 ngày** | Nhịp tự nhiên quan sát được là ~6 tuần/đợt ⇒ 3 đợt/90 ngày là **tăng gấp đôi nhịp** | ⚠️ ALERT |
| **(c)** | Khối lượng cầm cố/chuyển nhượng-TSĐB **tích luỹ vượt 5% free float** của một mã (hiện: VIC 1,89%, VHM 1,45%) | ~2,6× mức hiện tại. Nhớ: đây là **cận dưới của cận dưới** ⇒ chạm 5% trên số ĐO ĐƯỢC nghĩa là thực tế cao hơn nhiều | ⚠️ ALERT |
| **(c)** | Tỷ lệ **TSĐB/dư nợ công bố tụt xuống <150%** (hiện ~200%) | Rating agency công bố ~200% cho lô 4.000 tỷ; 150% là mức thường thấy làm ngưỡng bổ sung TSĐB trong hợp đồng VN — **GIẢ ĐỊNH, chưa verify hợp đồng cụ thể** | ⚠️ ALERT |
| **(c)** | Bất kỳ tin **giải chấp/bán giải chấp thật** với cổ phiếu VIC-family | Kênh tự củng cố ⇒ tự nó là solvency-adjacent | 🔴 SOLVENCY |
| **(d)** | `IntCov_P0` **<1,0** hai quý liên tiếp (không trả nổi lãi bằng lợi nhuận hoạt động) | 2 quý để loại nhiễu một-quý; đây là kênh khó nguỵ trang nhất | ⚠️ ALERT |
| **(d)** | `CF_OA_P0` **âm** hai quý liên tiếp **ĐỒNG THỜI** tổng nợ vay tăng >10% cùng kỳ | Chữ ký của "trả lãi bằng vốn vay mới". Một mình CF_OA âm KHÔNG đủ — DN đang capex nặng có thể âm hợp lý | ⚠️ ALERT |
| **(d)** | Tổng nợ vay (`StDebt_P0`+`LtDebt_P0`) tăng **>25% trong 1 quý** | VIC 2026Q1→Q2 tăng vọt đã quan sát ⇒ mốc phải cao hơn biến động bình thường của chính nó | ℹ️ GHI NHẬN |
| **(e)** | Công văn 5368/NHNN-TD (hoặc cơ chế loại trừ room tương đương) **bị thu hồi/sửa/hết hiệu lực không gia hạn** | Cơ chế ưu đãi do chính sách tạo ra ⇒ đảo chính sách là thay đổi rời rạc, lớn, quan sát được | 🔴 CHÍNH SÁCH |
| **(e)** | Thanh tra/kiểm tra chính thức với các dự án hạ tầng trong danh sách 18 dự án | Có thể là tiền đề của (e) trên | ⚠️ ALERT |

**Ba loại nhãn:** `ℹ️ GHI NHẬN` = ghi vào nhật ký, không báo riêng. `⚠️ ALERT` = một dòng báo cho user
trong chu kỳ scan gần nhất. `🔴 SOLVENCY/CHÍNH SÁCH` = báo NGAY, và **đủ tư cách làm 1 trong 2 tín
hiệu độc lập của điều kiện Tầng 2**.

**Tự phê bình về các ngưỡng số:** ngưỡng của (a)(c)(d) được đặt bằng cách **neo vào mốc quan sát hiện
tại + một biên đủ rộng để không bắn vì nhiễu** — chúng KHÔNG được calibrate trên base rate lịch sử
(không có mẫu: nhóm này chưa từng có sự kiện tín dụng nào trong dữ liệu quan sát được). Nghĩa là false
negative rate **không biết**. Đây là giới hạn thật, và cũng chính là lý do khung này **chỉ báo tay,
không tự hành động** — một ngưỡng chưa calibrate mà nối vào lệnh là đúng loại sai lầm §0 mục 2 cấm.

---

## 4. Tần suất

| Loại | Tần suất | Cơ chế | Vì sao đúng nhịp này |
|---|---|---|---|
| (a)(b)(c)(e) | **2 lần/tuần** (Thứ Hai 08:00 + Thứ Sáu 08:10 ICT) | `fearbuy_weekly_scan.sh` — **đã chạy sẵn, không cần cron mới** | Loại tin này có nhịp tự nhiên TUẦN–THÁNG (2 đợt chuyển nhượng VHM cách nhau ~6 tuần) ⇒ độ trễ tối đa 3–4 ngày là đủ |
| (c) biến động giá | **Hàng ngày** | `anomaly_scan.py` IDIOCRASH/FLOOR2 — đã có | Margin-call diễn ra trong vài giờ–vài ngày, **nhanh hơn tin báo**. Kênh giá bắt trước, WebSearch bổ sung nguyên nhân sau |
| (d) | **Hàng quý, sau BCTC + trễ 45 ngày** | Thủ công qua BQ khi review | Dữ liệu chỉ đổi mỗi quý — chạy dày hơn là lãng phí |
| (e) event-driven | **Ngay khi có tin** | Cùng kênh WebSearch | — |

**KHÔNG đề xuất cron mới.** Tăng tần suất WebSearch tốn chi phí và không cải thiện gì: tin margin-call
cấp tốc thường không kịp lên báo trước khi giá đã phản ánh — kênh giá (`anomaly_scan.py`) đã phủ phần
nhanh đó.

**Review định kỳ khung này:** mỗi quý, cùng lúc với chu kỳ (d). Việc cần làm: cập nhật lại các mốc neo
(lãi suất trái phiếu mới nhất, rating, pledge tích luỹ, TSĐB/dư nợ) vì **mọi ngưỡng ở §3 đều neo vào
mốc quan sát, không phải hằng số phổ quát** — mốc trôi thì ngưỡng phải trôi theo.

---

## 5. Khoảng trống đã biết (không giấu)

1. **Không có base rate** ⇒ không biết false negative rate của bộ ngưỡng §3 (đã nêu ở §3).
2. **Không đo được exposure ngân hàng** (§2.3) — trong khi đây là kênh lan truyền CHÍNH tới portfolio.
   Đây là khoảng trống lớn nhất, không phải chi tiết vặt.
3. **Không đo được tổng pledge** (§2.3) — mọi con số (c) là cận dưới của cận dưới.
4. **VRE mù dữ liệu từ 2023Q4** — nếu VRE thành trọng yếu, phải xác minh trước.
5. **Ngưỡng TSĐB/dư nợ <150% là GIẢ ĐỊNH**, chưa verify điều khoản hợp đồng thật của lô nào.
6. **Chưa đóng**: 2 sự kiện phát hành VIC 2025-08/2026-07 (`total_value=0`, dấu hiệu swap/ESOP nội bộ)
   có nằm trong tập RAISE_SET gốc của `FINDINGS.md` 08-17 hay không — ảnh hưởng tới việc có được áp
   base rate BHAR_250 −7,74% cho VIC hay không. Hiện **KHÔNG áp** (ngoại suy population→1 công ty).

## 6. Nguồn

- `vic_family_credit_concentration_20260818.md` — tín dụng tập trung, đòn bẩy, test §3 bác bỏ cò súng
  đòn bẩy, khung 3 tầng §6
- `vic_family_pledge_volume_and_monitoring_20260818.md` — khối lượng cầm cố (cận dưới), tần suất scan
- `vic_pinning_hypothesis_and_creditrate_proxy_20260818.md` — proxy lãi vay 12–12,5%, rating, test
  tail-asymmetry N=225, cơ chế pledge
- `bank_tailrisk_insurance_design_20260814.md` — khung 3 tầng gốc, điều kiện Tầng 2 (user duyệt 08-14)
