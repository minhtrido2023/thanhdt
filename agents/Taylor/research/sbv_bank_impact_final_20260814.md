# Tài liệu định hướng NHNN 2026-08-13 → tác động lên rổ ngân hàng đang nắm giữ — BẢN TỔNG HỢP CUỐI

job `Taylor_20260814_021603` · 2026-08-14 · Taylor (Quant)
Gộp 3 vòng: `Taylor_20260813_164933` (tác động) → `Taylor_20260813_172358` (ngày tài liệu + LDR)
→ `Taylor_20260814_002041` (CASA nguồn sơ cấp). **Không sửa đè 3 báo cáo cũ** — chúng vẫn là audit
trail từng vòng (`sbv_meeting_note_impact_20260813.md` + addendum,
`kb/data_registry/fundamentals/bank_casa_ldr.md`).

Đọc file này là đủ; không cần lật lại 3 report cũ.

| Nhãn | Nghĩa |
|---|---|
| **[VERIFIED]** | Đo được từ BQ / BCTC gốc / artifact live, tái lập được |
| **[HYPOTHESIS]** | Suy luận định tính từ văn bản họp — **chưa kiểm chứng, không trích như finding** |

---

## ⚠️ ĐÍNH CHÍNH QUAN TRỌNG — trọng số rổ ngân hàng ở vòng 1 SAI, đã tính lại

Vòng 1 báo **SpaceX 66,8% · ZaloPay 58,6%** active MV là ngân hàng. **Con số đó sai.** Nó tính
market value bằng `accumulateQuantity` — trường cộng dồn TOÀN BỘ khối lượng đã mua trong đời mỗi
deal, gồm cả phần **đã bán xong**. Trường đúng là `openQuantity` (khối lượng còn đang mở), đúng
như `DNSEBroker.get_positions()` (`trading_bot/brokers.py:474`) dùng cho production.

Số đúng, đo lại từ cùng bản ghi `positions` 20:30 ICT 2026-08-13 [VERIFIED]:

| Account | Active stock MV | **Rổ ngân hàng (13 mã)** | (vòng 1 báo nhầm) |
|---|---:|---:|---:|
| SpaceX | **832,5tr** | **311,5tr = 37,4%** | ~~1.638,0tr / 66,8%~~ |
| ZaloPay (đã trừ DGC legacy 439,0tr) | **454,7tr** | **153,8tr = 33,8%** | ~~777,9tr / 58,6%~~ |

**Đối soát độc lập (đường dữ liệu khác):** `data/execution_logs/nav_history_*.csv` cột `mtm_stock`
ngày 2026-08-13 — SpaceX **831,76tr**, ZaloPay **893,23tr** (gồm DGC). Khớp với số `openQuantity`
(832,5 / 893,7tr; chênh <0,1% do `marketPrice` vs giá đóng cửa), **không** khớp với số
`accumulateQuantity`. ⇒ sai lệch đã được xác nhận, không phải khác quy ước.

**Vì sao lệch không đều giữa các mã:** `accumulate` phồng lên tỉ lệ với mức độ **quay vòng** của
mã. Rổ ngân hàng là phần bị giao dịch nhiều nhất của book ⇒ phồng mạnh nhất ⇒ tạo ảo giác tập
trung. Ca nặng nhất là **VPB ở ZaloPay: 26,72% (sai) → 7,25% (đúng)**, tức toàn bộ mệnh đề "VPB
nặng ký nhất ZaloPay" của 2 vòng trước **không còn đúng** (xem §4).

**Điều KHÔNG đổi:** ngân hàng vẫn là **nhóm ngành lớn nhất** trong cả 2 book (~1/3 active MV),
nên toàn bộ phân tích dưới đây vẫn đáng làm — chỉ là biên độ tác động nhỏ hơn ~45% so với con số
vòng 1. Mọi số "% NAV" trong file này đã dùng trọng số đúng.

---

## §1. Tài liệu SBV 2026-08-13 nói gì — 1 đoạn

Tài liệu định hướng NHNN họp với các ngân hàng, **ngày 2026-08-13 (user đã xác nhận)**, ba ý:
(a) **hết dư địa nới lỏng CSTT** — tỷ giá là ràng buộc cứng; (b) ép các NHTM "chia sẻ lợi ích",
**giảm lãi suất cho vay trong khi vẫn phải giữ lãi suất huy động cao** (LDR hệ thống 107,7%, chênh
tín dụng−huy động ~2 triệu tỷ, vốn trung-dài hạn chỉ 16% nguồn nhưng tài trợ 48,5% dư nợ TDH);
(c) **room tín dụng 2027 gắn với mức độ tuân thủ** việc giảm lãi vay — tức đòn bẩy tuân thủ.

Hệ quả cấu trúc: ba "van xả" thông thường của ngân hàng bị bịt cùng lúc — không hạ được lãi huy
động (mất vốn), không bù được bằng tăng dư nợ (room bị nắm), không chuyển được sang cho vay lợi
suất cao (kiểm soát lĩnh vực rủi ro + thanh tra BĐS/related-party). **[HYPOTHESIS]** — đây là đọc
hiểu văn bản, không phải số đo.

---

## §2. Rổ thật đang chịu tác động — 13 mã [VERIFIED]

ACB · BID · CTG · HDB · LPB · MBB · MSB · SHB · TCB · TPB · VCB · VIB · VPB.
Đây là **vị thế THẬT** (SpaceX ∪ ZaloPay), không phải universe ngân hàng VN.

Tỷ trọng: **SpaceX 37,4% · ZaloPay 33,8%** active MV (bảng §0). Để so sánh — top-weight thật của
SpaceX hôm nay là SIP 10,4% · PVT 8,4% · VHM 7,8%, mã ngân hàng lớn nhất chỉ là BID 5,13%. Không
mã ngân hàng đơn lẻ nào vượt 5,2% ở SpaceX, hay 7,3% ở ZaloPay.

---

## §3. BẢNG TỔNG HỢP PER-MÃ — dữ liệu quan trọng nhất của cả chuỗi

Ba cột dữ liệu + hai cột trọng số thật. **Mỗi cột là một loại rủi ro KHÁC nhau, không cộng dồn.**

| Mã | Đệm LN/dư nợ (proxy NIM)¹ | LDR Q2/2026² | CASA Q2/2026³ | w SpaceX | w ZaloPay |
|---|---:|---:|---:|---:|---:|
| **VPB** | 3,53% | **158,5** | 11,48 | 3,65% | **7,25%** |
| **ACB** | 4,77% | 129,3 | 21,41 | 2,40% | 1,46% |
| **TCB** | 3,29% | 127,9 | **33,81** | 3,81% | 2,48% |
| **MBB** | 4,03% | 127,4 | **33,62** | 3,79% | 2,80% |
| **VIB** | n/a | 125,1 | 11,76 | 0,87% | 0,64% |
| **LPB** | 3,82% | 121,5 | **6,31** | 2,58% | 4,17% |
| **TPB** | 4,98% | 117,2 | 18,32 | 0,87% | 0,32% |
| **MSB** | n/a | 112,6 | 21,91 | 0,97% | 0,71% |
| **CTG** | 5,16% | 110,7 | 22,72 | 4,63% | 3,18% |
| **BID** | **7,47%** | 110,6 | 20,13 | 5,13% | 3,42% |
| **SHB** | 5,57% | 105,7 | 7,77 | 1,13% | 0,78% |
| **VCB** | 4,47% | 101,7 | 32,34 | 5,00% | 3,93% |
| **HDB** | 3,83% | **97,8** | 10,81 | 2,57% | 2,70% |

*(sắp theo LDR giảm dần)*

**¹ Đệm LN/dư nợ** = mức sụt **% lợi nhuận ròng TTM** cho **mỗi 10bp** cắt lãi vay không bù trừ,
tại `L = dư nợ/tổng tài sản = 0,70`. Nguồn: `ticker_financial` 2025Q3→2026Q2. **Là CẬN TRÊN có
chủ đích**: giả định toàn bộ dư nợ tái định giá ngay, không bù bằng lãi huy động/khối lượng/phí,
bỏ qua thuế (nên còn *đánh giá thấp* ~×1,25 nếu quy sau thuế). **Không phải dự báo.** Bản chất
công thức là `1/ROA` ⇒ nó đo **đệm lợi nhuận trên quy mô tài sản**, KHÔNG đo cơ cấu vốn — hai mã
cùng ROA nhưng CASA lệch hẳn sẽ cùng điểm ở cột này, và đó là lý do cột 2/3 tồn tại.
⚠️ **MSB và VIB không có số** — vòng 1 chỉ chạy 11/13 mã. Chưa đo, không phải bằng 0.

**² LDR** = `cho vay khách hàng (GỘP, trước dự phòng) / tiền gửi khách hàng`, tự tính từ bảng cân
đối VCI (vnstock). **KHÔNG phải LDR quy định** (TT 22/2019, trần 85% — mẫu số rộng hơn): mọi giá
trị >100% ở đây là **bình thường**, không đọc là vi phạm trần. Verify: bất biến kế toán
`gộp = ròng + dự phòng` **52/52 kỳ**; đối soát chéo nguồn không-qua-VCI **5/5, lệch ≤0,13%**.

**³ CASA** = cột `casa_strict_pct` (không kỳ hạn + tiết kiệm không kỳ hạn) / tổng tiền gửi KH,
đọc thẳng từ **thuyết minh BCTC hợp nhất Q2/2026 GỐC** (OCR/text), 13/13 mã, nguồn
`data/bank_casa_primary_20260814.csv`. **Đây là số ĐÃ THAY THẾ số báo chí ở vòng 2** (xem §6a).
Ba chân verify độc lập: bất biến số học nội bộ 13/13 · mẫu số khớp TUYỆT ĐỐI (0,0000%) với
vnstock/VCI 13/13 · tỉ lệ khớp báo chí 10/10 trong ±0,03pp dưới định nghĩa đã chốt.

**Tổng hợp gia quyền theo trọng số THẬT** [VERIFIED]:

| | SpaceX | ZaloPay |
|---|---:|---:|
| Đệm LN gia quyền (10bp cắt) | **−4,70%** LN rổ NH | **−4,42%** |
| …quy về toàn book (PE không đổi) | **−1,76%** NAV | **−1,50%** NAV |
| LDR gia quyền | 119,0 | 123,9 |
| CASA gia quyền | 21,9% | 19,2% |

*(phủ 95%/96% rổ — thiếu MSB+VIB ở cột đệm LN)*
Kịch bản 50bp: SpaceX ≈ **−8,8% NAV**, ZaloPay ≈ **−7,5% NAV** — **stress test, KHÔNG phải base
case**; chỉ thị thực tế thường chỉ chạm lãi suất mới/lĩnh vực ưu tiên, dải nhiều khả năng 10–25bp
(⇒ −1,8% … −4,4% NAV).

---

## §4. Xếp hạng rủi ro funding — LDR cao + CASA thấp, đối chiếu trọng số thật

Điểm = hạng LDR (cao→1) + hạng CASA (thấp→1); điểm càng thấp càng căng. Hai trục ngang quyền,
cố ý không đánh trọng số (không có cơ sở thực nghiệm để cân).

| Hạng | Mã | LDR (#) | CASA (#) | Điểm | w SpaceX | w ZaloPay |
|---|---|---:|---:|---:|---:|---:|
| 🔴 1 | **VPB** | 158,5 (#1) | 11,48 (#4) | **5** | 3,65% | **7,25%** |
| 🔴 2 | **LPB** | 121,5 (#6) | 6,31 (#1) | **7** | 2,58% | **4,17%** |
| 🟠 3= | ACB | 129,3 (#2) | 21,41 (#8) | 10 | 2,40% | 1,46% |
| 🟠 3= | VIB | 125,1 (#5) | 11,76 (#5) | 10 | 0,87% | 0,64% |
| 🟡 5= | SHB | 105,7 (#11) | 7,77 (#2) | 13 | 1,13% | 0,78% |
| 🟡 5= | TPB | 117,2 (#7) | 18,32 (#6) | 13 | 0,87% | 0,32% |
| 🟢 7= | HDB | 97,8 (#13) | 10,81 (#3) | 16 | 2,57% | 2,70% |
| 🟢 7= | MBB | 127,4 (#4) | 33,62 (#12) | 16 | 3,79% | 2,80% |
| 🟢 7= | TCB | 127,9 (#3) | 33,81 (#13) | 16 | 3,81% | 2,48% |
| 🟢 10= | BID | 110,6 (#10) | 20,13 (#7) | 17 | 5,13% | 3,42% |
| 🟢 10= | MSB | 112,6 (#8) | 21,91 (#9) | 17 | 0,97% | 0,71% |
| 🟢 12 | CTG | 110,7 (#9) | 22,72 (#10) | 19 | 4,63% | 3,18% |
| 🟢 13 | VCB | 101,7 (#12) | 32,34 (#11) | 23 | 5,00% | 3,93% |

**Ba điều đọc ra được, đều là số:**

1. **VPB vẫn đứng #1 rủi ro funding — nhưng vì LDR, không vì "nặng ký".** LDR 158,5% cao nhất rổ
   một cách cách biệt (#2 là ACB 129,3), CASA 11,48% thấp thứ 4. Sau đính chính §0, VPB **không
   còn** là mã nặng nhất ZaloPay (7,25%, đứng thứ 5 sau PVT/SIP/VNM/SAB), và ở SpaceX chỉ 3,65%.
   ⇒ **Kết luận "VPB vừa nặng ký nhất vừa rủi ro cao nhất" của 2 vòng trước KHÔNG còn đúng.** Nó
   vẫn là mã rủi ro funding cao nhất, ở mức phơi nhiễm bình thường.
2. **LPB là ca đáng chú ý thứ hai và bị bỏ sót ở vòng 1.** CASA 6,31% — thấp nhất rổ một cách bất
   thường (mã kế tiếp SHB 7,77%, trung vị rổ ~20%) — cộng LDR 121,5%. Trọng số ZaloPay **4,17%**,
   cao thứ 2 trong rổ ngân hàng của account đó.
3. **Hai trục thật sự trực giao, và điều đó là phát hiện.** TCB/MBB có LDR gần bằng VPB (127,9 /
   127,4) nhưng CASA **33,8% / 33,6%** — cùng nhu cầu huy động, **chi phí vốn biên khác hẳn**.
   Ngược lại HDB LDR thấp nhất rổ (97,8) nhưng CASA chỉ 10,81%. Xếp hạng bằng một trục duy nhất —
   như bảng đệm-LN của vòng 1, bản chất `1/ROA` — **không** phân biệt được các ca này.

**Phơi nhiễm gộp nhóm 🔴🟠 (VPB+LPB+ACB+VIB):** SpaceX **9,50%** active NAV · ZaloPay **13,52%**.
ZaloPay nghiêng về nhóm căng hơn rõ rệt, chủ yếu do VPB+LPB.

Toàn bộ §4 là **[HYPOTHESIS]** ở tầng *diễn giải*: hai cột đầu vào là [VERIFIED], nhưng "LDR cao +
CASA thấp ⇒ chịu thiệt nhiều hơn khi lãi huy động lên" **chưa hề được backtest**, N = 0 sự kiện
lịch sử của cơ chế này. Đây là bản đồ giám sát, không phải tín hiệu.

---

## §5. CÓ NÊN HÀNH ĐỘNG GÌ KHÔNG? — trả lời thẳng

**KHÔNG. Không đổi sizing, không đổi rating, không đổi gate, không đổi filter live.** Giữ nguyên
khuyến nghị từ vòng 1.

**Nhưng độ tin cậy của chính khuyến nghị "không đổi" đã TĂNG, và đó là thay đổi thật.** Vòng 1
nói "không đổi" một phần vì **không đo được** cơ cấu vốn (BQ không có CASA/LDR/NIM) — tức là "không
đổi vì mù". Bây giờ đã có số thật cho cả 13 mã, và số đó **không hiện ra ca nào đủ cực đoan để
biện minh cho một thay đổi cấu trúc**: mã căng nhất (VPB) chiếm 3,65%/7,25% active NAV; nhóm căng
nhất gộp lại 9,5%/13,5%; và ngay cả kịch bản 50bp — vốn là stress test không phải base case — cũng
chỉ ra −8,8%/−7,5% NAV. ⇒ "Không đổi" giờ là **kết luận có bằng chứng**, không còn là mặc định khi
thiếu dữ liệu. Đây là lý do đáng để chạy cả 3 vòng.

Bốn lý do cụ thể cho từng đề xuất đã bị loại:

| Đề xuất khả dĩ | Vì sao KHÔNG |
|---|---|
| Cắt/giảm sizing nhóm 🔴 (VPB/LPB) | Cơ chế chưa backtest, N=0 sự kiện lịch sử. Sizing hiện do V2.4 allocator + rating 8L quyết định; can thiệp tay = discretionary override lên hệ đã kiểm chứng, đúng thứ [[feedback-plan-must-follow-production-rule-not-opinion]] cấm. Mức phơi nhiễm cũng không đòi hỏi hành động khẩn. |
| Thêm CASA/LDR vào rating 8L | Đề xuất wire ⇒ bắt buộc backtest + walk-forward IS/OOS + DSR/PBO + quant-skeptic. **1 kỳ dữ liệu (Q2/2026) thì không backtest được gì cả** — xem §6b. Chặn bởi dữ liệu, không phải khẩu vị. |
| Mở rộng `deposit-rate-autocheck` để theo dõi room 2027 | Kiến trúc phòng thủ của nó (delta-guard 1,0pp, gate ≥2 owner-group, consumer live) xây quanh bất biến "output là 1 số kiểm được cơ học". "NH X có bị cắt room không" không phải một con số, không có nguồn công bố định kỳ đáng tin. Nhét vào sẽ phá đúng bất biến khiến nó an toàn. |
| Sửa DT5G / thêm Pillar A′ theo lãi suất huy động | Tham số DT5G đang ở vùng bình ổn, CLAUDE.md cấm re-tune theo lịch sử. Pillar A′ đã pre-register (`Taylor_20260713_124803`) và **chặn dữ liệu**: chuỗi point-in-time thật của `deposit_rate_vn` mới có **1 mốc** (2026-07-20); 26 mốc lịch sử neo hồi tố cùng ngày ⇒ mọi backtest trên đó mang bias hindsight. **Chưa đủ dữ liệu để nghiên cứu, chứ không phải đã bác bỏ.** |

**Hai quan sát cơ chế vẫn để mở (không phải đề xuất, đã verify — cần biết, chưa cần làm):**

- **§3b vòng 1 — điểm mù Pillar A.** Pillar A của DT5G chỉ nhìn lãi suất **tái cấp vốn** (giá hành
  chính), và là **máy dò THẮT CHẶT** (`refi_chg6m ≥ +0,5pp → cap NEUTRAL`). Mốc refi cuối cùng
  2023-06-19 @4,5%, phẳng 1.151 ngày ⇒ `cap = 9` (không cap). Sự thắt chặt mà tài liệu mô tả là
  thắt **lượng và giá thị trường** — có thể đẩy lãi suất thực tế lên mà **không bao giờ chạm mốc
  refi**, và DT5G mù hoàn toàn ở lớp cảnh báo sớm. Không phải lỗi thiết kế (DT5G là bảo hiểm dựa
  trên GIÁ, base v3.4b sẽ bắt được qua VNINDEX), nhưng lớp *cảnh báo sớm* không hoạt động ở kịch
  bản này. [VERIFIED về cơ chế, [HYPOTHESIS] về kịch bản]
- **§4b vòng 1 — rổ ngân hàng không có kênh phản ứng lãi suất ở tầng rating.** Deposit tilt trong
  `rating_8l.py:858-870` (±0.03 lên `value_score_v3`, hurdle `1/PE − deposit ≥ 3pp`) chỉ áp cho
  `val_route ∈ {COMPOUNDER, CYCLICAL, RETAIL}`. Đối chiếu `data/rating_8l_screener.csv`: **cả 8 mã
  ngân hàng kiểm tra đều mang `val_route = "BANK"`** ⇒ không nằm trong danh sách áp tilt. Việc
  banks dùng v2 (không PS) là **quyết định đúng và có chủ đích** (PS vô nghĩa với ngân hàng); vấn
  đề là hệ quả *phụ*: nếu lãi huy động tăng, kênh truyền dẫn duy nhất đang wire siết vào ~2/3 danh
  mục phi ngân hàng và **không chạm 1/3 rổ ngân hàng**. Có nên có kênh riêng hay không là câu hỏi
  R&D riêng, cần backtest + quant-skeptic. [VERIFIED]

**Việc DUY NHẤT đáng làm, rẻ, không chạm production:** thêm **một dòng** vào recon hàng quý — tăng
trưởng tổng tài sản YoY của rổ ngân hàng, đã có sẵn trong `ticker_financial`. Nếu cơ chế room-2027
là thật, nó sẽ **lộ ra trong số liệu** dưới dạng tăng trưởng tài sản chậm đột ngột, không cần theo
dõi tin tức (mốc hiện tại: MBB +34,4% · HDB +33,3% · ACB +14,4% YoY; MBB rơi về ~+15% là tín hiệu
mạnh hơn bất kỳ bản tin nào). Cadence **quý** (khớp BCTC), chỉ báo giám sát, **không wire vào
filter**. Vẫn chờ user duyệt cadence.

---

## §6. Độ tin cậy toàn chuỗi — cái gì VERIFIED, cái gì vẫn là HYPOTHESIS

### VERIFIED — trích dẫn được

| # | Nội dung | Bằng chứng |
|---|---|---|
| 1 | Trọng số rổ ngân hàng 37,4% / 33,8%; toàn bộ bảng w SpaceX/ZaloPay | `dnse_raw_2026-08-13.jsonl` `positions` 20:30, `openQuantity`; đối soát `nav_history_*.csv` `mtm_stock` |
| 2 | **LDR 13/13 mã Q2/2026** | Bất biến `gộp=ròng+dự phòng` 52/52 kỳ; đối soát chéo nguồn không-qua-VCI 5/5, lệch ≤0,13% |
| 3 | **CASA 13/13 mã Q2/2026** | BCTC gốc; 3 chân verify độc lập (bất biến số học 13/13 · mẫu số khớp 0,0000% với VCI 13/13 · tỉ lệ khớp báo chí 10/10 ±0,03pp) |
| 4 | Đệm LN/dư nợ 11/13 mã (cận trên) | `ticker_financial` TTM 2025Q3→2026Q2 |
| 5 | Cơ chế Pillar A (ngưỡng, `EASING_FLOOR_ENABLED=False`, refi phẳng 1.151 ngày, `cap=9`) | `macro_state_live.py:174-215` + `sbv_macro_overlay.SBV_REFI_EVENTS` |
| 6 | Deposit tilt không chạm `val_route="BANK"` | `rating_8l.py:858-870` + `data/rating_8l_screener.csv` |
| 7 | Ngày tài liệu = 2026-08-13 | user xác nhận |

### HYPOTHESIS — **không** trích như finding

| # | Nội dung | Vì sao chưa verify được |
|---|---|---|
| 1 | **Room tín dụng 2027 thực sự bị dùng làm đòn bẩy tuân thủ** | **Không có một dòng dữ liệu nào trong cả 3 vòng chạm được việc này.** Suy luận định tính thuần từ văn bản họp. N=0 sự kiện lịch sử. Chỉ kiểm được gián tiếp, sau nhiều quý, qua tăng trưởng tài sản |
| 2 | **Funding gap thực sự đẩy lãi suất huy động LÊN** | Tương tự — **không dữ liệu nào trong chuỗi verify được**. Chuỗi lãi suất huy động point-in-time thật có **n=1** (2026-07-20, 6,8%); 26 mốc lịch sử neo hồi tố cùng một ngày ⇒ vô dụng cho kiểm chứng |
| 3 | Cơ chế "bịt cả 3 van xả cùng lúc" (§1) | Đọc hiểu văn bản. Kiểm được bằng NIM công bố BCTC Q3/2026 (~cuối 10/2026) so với dải §3 |
| 4 | Xếp hạng funding §4 dự báo được thiệt hại tương đối | Chưa backtest, chưa quant-skeptic, N=0. Là bản đồ giám sát |
| 5 | Kịch bản DT5G mù trước thắt chặt *lượng* (§5) | Cơ chế đã verify; việc kịch bản đó xảy ra thì chưa |

**Ranh giới cần giữ khi trích dẫn:** cột "đệm LN" là **cận trên có chủ đích**, không phải dự báo,
và bản chất là `1/ROA` nên **không** đọc là NIM. `Revenue_P0` với ngân hàng là **TOI** (gồm phí +
ngoại hối/chứng khoán), không phải thu nhập lãi thuần. LDR ở đây là LDR **thuần**, không phải LDR
quy định TT 22/2019.

---

## §7. Hai việc còn treo — chưa cần làm ngay, nhưng phải biết

**(a) `data/bank_casa_ldr_20260814.csv` còn cột `casa` mang SỐ BÁO CHÍ SAI — dễ trích nhầm.**
File đó (chân LDR) vẫn giữ cột `casa`/`casa_source = PRESS_UNVERIFIED_2026Q2`, chỉ có 10/13 mã, vì
`build_bank_casa_ldr.py` chưa được sửa. **CASA chỉ được lấy từ `bank_casa_primary_20260814.csv`.**
Hai file **dùng chung tiền tố tên** ⇒ đây là chỗ dễ trích nhầm nhất của cả chuỗi. Ba cái bẫy kèm
theo: (i) chọn đúng cột — `casa_strict_pct` là mặc định, `casa_pressdef_pct` **chỉ** để đối chiếu
báo chí (TPB lệch **+2,65pp** giữa hai cột, sai thật chứ không phải làm tròn); (ii) đơn vị
`*_mn` = **triệu VND** ở file primary nhưng **đồng VND** ở file LDR; (iii) `vnstock finance.ratio()`
có sẵn 2 chỉ tiêu `Tỷ lệ CASA`/`LDR (%)` nhưng dưới community edition **trả số của năm 2018** với
nhãn cột hỏng, không báo lỗi gì — `bank_lens_v2.py`/`v3.py` đọc đúng cột đó (hiện đang crash sớm
nên chưa in ra số 2018; "sửa" chúng một cách ngây thơ sẽ TẠO RA đúng bug đó).
*Sửa đúng cách:* cập nhật `build_bank_casa_ldr.py` để nó join CASA từ file primary, hoặc bỏ hẳn
cột `casa` khỏi file LDR. Chưa làm vì chưa có consumer nào đọc — nhưng đó chính là rủi ro.

**(b) Chỉ có 1 kỳ dữ liệu CASA/LDR (Q2/2026) — không trả lời được XU HƯỚNG.**
LDR có chuỗi 4 quý (2025Q3→2026Q2) trong CSV; **CASA chỉ có 30/6/2026**. Nghĩa là mọi câu hỏi
dạng "LPB CASA 6,31% là đang xấu đi hay đã luôn thấp?", "VPB LDR 158,5% là mới căng hay cấu trúc
sẵn?" — **không trả lời được**, và **không được kéo ngang** số Q2 sang kỳ khác. Đây cũng là lý do
kỹ thuật khiến §5 không thể đề xuất wire gì: 1 kỳ thì không backtest được. Muốn có chuỗi phải OCR
thêm BCTC từng quý theo quy trình ở `kb/data_registry/fundamentals/bank_casa_ldr.md` (Bẫy 3) —
đáng làm khi BCTC Q3/2026 ra (~cuối 10/2026), lúc đó có 2 điểm và mới bắt đầu nói được về xu hướng.

---

## §8. Tuyên bố phạm vi

R&D thuần. **KHÔNG chạm production, KHÔNG đề xuất đổi config live, không cần quant-skeptic** (đúng
ranh giới dispatch). Bước tổng hợp — không query BQ/OCR mới; nguồn duy nhất phát sinh trong job này
là việc **tính lại trọng số** từ `dnse_raw_2026-08-13.jsonl` để đính chính §0, đã đối soát độc lập
bằng `nav_history_*.csv`. Nếu bất kỳ mục nào tiến tới đề xuất wire, khi đó mới bắt buộc qua gate
đầy đủ (backtest + walk-forward IS/OOS + DSR/PBO + quant-skeptic).
