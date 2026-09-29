# Rủi ro tập trung tín dụng vào nhóm BĐS đầu ngành (VIC-family) — đánh giá & thiết kế cảnh báo sớm

> Taylor (Quant/Algo), job `Taylor_20260818_030812`, 2026-08-18. **Research-only — không wire gì.**
> Câu hỏi gốc từ user (qua Mike): lo ngại tín dụng ngân hàng dồn vào vài DN BĐS đầu ngành
> (Vingroup/VIC), (1) crowding-out lãi suất, (2) đặt cược một chiều giá BĐS, (3) lãi vay BĐS
> 12-16%/năm + thanh khoản BĐS chững/giá giảm, (4) contagion nếu VIC gặp vấn đề dòng tiền.

---

## 0. Trả lời thẳng — có nên hành động gì NGAY BÂY GIỜ không

**Không có hành động bán/giảm tỷ trọng nào được đề xuất ngay.** Ba lý do, mỗi lý do độc lập:

1. **Claim định lượng cụ thể nhất mà user có thể đang cầm ("VIC ~10% tổng tín dụng quốc gia") bị
   SỐ LIỆU BÁC BỎ** — thực tế đo được là **~1,8%** (§1). Không phủ nhận rủi ro tập trung có thật,
   chỉ phủ nhận ĐỘ LỚN đang được hình dung.
2. **Exposure thật của portfolio đi qua SỔ NGÂN HÀNG (17–36% NAV), không phải cầm trực tiếp
   VIC/VHM** (2,6–8,1% NAV, đến từ custom30V screen định kỳ — không phải cược chủ đích). Nếu muốn
   giảm rủi ro, đòn bẩy hiệu quả nhất là **tỷ trọng ngân hàng**, không phải bán VHM/VRE.
3. **Test lịch sử (§3) cho thấy đúng loại tín hiệu user đang nghĩ tới — đòn bẩy tăng, tín dụng
   BĐS đắt/chững — CHƯA TỪNG có giá trị định thời cho VIC/VHM trong dữ liệu quan sát được.**
   Ngược lại: giai đoạn đòn bẩy tăng mạnh nhất (2024-2025) trùng với đợt tăng giá lớn nhất lịch sử
   hai mã này (VIC +709% 12 tháng từ đáy 2024Q4). Một cổng "Debt_Eq vượt ngưỡng lịch sử → cảnh báo
   bán" sẽ bắn liên tục từ 2022Q2 và bỏ lỡ toàn bộ đợt tăng đó — đúng sai lầm mà bank tail-risk
   report (2026-08-14) đã cảnh báo cho nhóm ngân hàng, tái hiện y hệt ở nhóm này.

**Việc ĐÁNG làm ngay — rẻ, không phải bán gì**: mở rộng bộ từ khoá `fearbuy_weekly_scan.sh` cho
nhóm BĐS/Vingroup theo đúng khung Tầng 1 đã duyệt 08-14 (§6). Đây là khuyến nghị hành động DUY NHẤT
trong báo cáo này.

---

## 1. Xác minh claim "VIC ~10% tổng tín dụng quốc gia" — REFUTED, ~1,8%

**VERIFIED bằng 2 nguồn độc lập khớp nhau:**

- BQ `tav2_bq.ticker_financial` (2026Q2, VIC): `StDebt_P0` = 137,278 tỷ + `LtDebt_P0` = 218,477 tỷ
  = **355.755 tỷ đồng tổng vay ngân hàng + thuê tài chính** (consolidated, bao gồm VHM/VRE/VPL vì
  đây là BCTC hợp nhất tập đoàn — không cộng dồn thêm nợ riêng của VHM/VRE kẻo đếm trùng).
- WebSearch độc lập (báo chí trích BCTC VIC): **355,756 tỷ đồng** — khớp gần như tuyệt đối với số
  BQ ở trên. Cross-check qua 2 đường dữ liệu khác nhau, cùng một con số → độ tin cậy cao.
- Tổng dư nợ tín dụng toàn nền kinh tế VN, NHNN công bố, 29/07/2026: **20,15 triệu tỷ đồng**
  (tăng 8,38% so cuối 2025).

**⇒ VIC-family / tổng tín dụng quốc gia ≈ 355.756 / 20.150.000 ≈ 1,77%.** Không phải ~10%.

**Điều chỉnh có ý nghĩa hơn con số tĩnh này — cơ chế FLOW, không phải STOCK:** SBV vừa ban hành
**Công văn 5368/NHNN-TD (22/06/2026)** — dư nợ tín dụng cho **18 dự án hạ tầng của Vingroup,
Sun Group, Masterise** (tổng giá trị khoản vay ước **>752.000 tỷ đồng** cho cả 3 tập đoàn) **được
LOẠI TRỪ khỏi cách tính tăng trưởng tín dụng của ngân hàng** khi cấp cho các dự án này.

Đây mới là cơ chế crowding-out ĐÚNG hình dạng mà user lo ngại, nhưng khác cơ chế user mô tả:
- **Không phải** "VIC chiếm room khiến DN khác hết room" (room dành cho VIC/Sun/Masterise được
  NHNN cấp NGOÀI trần tăng trưởng tín dụng thông thường của ngân hàng).
- **Là**: bảng cân đối vốn/thanh khoản thật của ngân hàng (vốn chủ sở hữu, tiền gửi huy động được)
  vẫn là nguồn lực hữu hạn — tín dụng cho 3 tập đoàn này KHÔNG bị đếm vào trần tăng trưởng (~15%/
  năm cho toàn hệ thống 2026), nhưng vẫn RÚT vốn thật khỏi cùng một bể vốn khả dụng đó. **752.000
  tỷ giải ngân dần cho 3 tập đoàn qua vài năm** so với **~3.000 tỷ đồng tăng trưởng tín dụng toàn
  hệ thống mỗi năm** (15% × 20,15 triệu tỷ) — không nhỏ ở góc độ dòng chảy biên, dù nhỏ ở góc độ
  tỷ trọng tồn kho.

**KHÔNG XÁC MINH ĐƯỢC** (giới hạn của WebSearch, không suy diễn): tỷ trọng cụ thể của riêng VIC
(tách khỏi Sun Group/Masterise) trong 752.000 tỷ đó; cũng không xác minh được lãi suất áp dụng cho
gói tín dụng loại trừ này có ưu đãi hơn thị trường hay không.

---

## 2. Xu hướng đòn bẩy VIC-family — TĂNG MẠNH, đo được, không tranh cãi

Nguồn: `tav2_bq.ticker_financial`, `Debt_Eq_P0` theo quý, 2017Q4→2026Q2 (self-check: dữ liệu BQ
2026Q2 StDebt+LtDebt khớp khít với số báo chí trích BCTC, xem §1 — coi như đã đối soát).

| Mã | Debt_Eq đáy gần đây | Debt_Eq hiện tại (2026Q2) | Bội số | Ghi chú |
|---|---:|---:|---:|---|
| **VIC** | 1,64 (2021Q3-Q4) | **6,24** | **3,8×** trong <5 năm | đỉnh lịch sử 6,67 (2026Q1) |
| **VHM** | 0,75 (2022Q1) | **3,05** | **4,1×** trong 4,5 năm | nhảy vọt riêng 2026Q1→Q2 (2,19→3,05) |
| **VPL** | 0,34 (2025Q1, mới niêm yết) | 1,63 | 4,8× trong 5 quý | mẫu quá ngắn, không kết luận xu hướng |
| **VRE** | — | dữ liệu BQ dừng ở 2023Q4 | — | **GIỚI HẠN**: không xác minh được lý do dừng cập nhật (khả năng: đổi cấu trúc sở hữu/không còn báo cáo riêng trong nguồn dữ liệu) — không suy diễn, cần Winston xác minh nếu cần dùng VRE cho quyết định |

**CF_Invest_3Y của VIC**: −179,3 nghìn tỷ (2026Q2), tăng đều từ −139,5 nghìn tỷ (2022Q4) — dòng
tiền đầu tư/capex ra liên tục và ngày càng lớn, nhất quán với việc xây hạ tầng quy mô lớn (khớp
với claim "gánh vốn xây hạ tầng công" của user). `ROE_Trailing` VIC rất thấp trong 2022-2024
(1,4–3,3%), chỉ bắt đầu cải thiện rõ từ 2025Q4 (7,1%) → 2026Q2 (16,0%) — tức lợi nhuận trên vốn
đã cải thiện GẦN ĐÂY, không phải toàn bộ giai đoạn đòn bẩy tăng đều "đốt tiền không hiệu quả".

**Kết luận phần này**: claim "đòn bẩy tăng" của user — **VERIFIED, mạnh, đo được**. Đây là phần
đúng nhất trong toàn bộ mối lo của user. Nhưng đòn bẩy tăng không tự nó là tín hiệu bán (§3).

---

## 3. Đòn bẩy có định thời được giá không? — TEST, và câu trả lời là KHÔNG (giống bank tail-risk)

Phương pháp: với mỗi quý, lấy `Debt_Eq_P0` tại ngày công bố BCTC + 45 ngày trễ công bố (giống cách
xử lý CASA/LDR ở bank report), đo lợi suất giá 6 tháng và 12 tháng sau đó. N = 34 quý (VIC) + 34
quý (VHM), 2018–2025 (2026 chưa đủ dữ liệu tương lai để đo).

| Giai đoạn | Debt_Eq (VIC) | r12m sau đó (VIC) | Debt_Eq (VHM) | r12m sau đó (VHM) |
|---|---:|---:|---:|---:|
| 2021Q3 (đáy đòn bẩy) | 1,64 | **−40,0%** | 0,84 | **−46,8%** |
| 2022Q4 (đòn bẩy bắt đầu tăng vọt) | 3,26 | −19,5% | 1,44 | −1,3% |
| 2023Q2 (đòn bẩy cao, giá đã giảm sẵn) | 3,35 | −42,3% | 1,30 | −39,7% |
| **2024Q3 (đòn bẩy 3,82 — cao hơn hẳn lịch sử)** | 3,82 | **+435,3%** | 1,43 | **+136,0%** |
| **2024Q4 (đòn bẩy 4,44 — đỉnh mới)** | 4,44 | **+709,5%** | 1,56 | **+185,3%** |
| 2025Q2 (đòn bẩy 5,04, tiếp tục leo) | 5,04 | +235,0% | 1,84 | +50,7% |

**Không có quan hệ đơn điệu nào giữa mức đòn bẩy và lợi suất tương lai** — thời điểm đòn bẩy CAO
NHẤT lịch sử (2024Q4) lại là thời điểm SAU ĐÓ giá tăng MẠNH NHẤT lịch sử (+709% cho VIC, +185% cho
VHM trong 12 tháng). Ngược lại, thời điểm đòn bẩy THẤP nhất (2021Q3-Q4) lại dẫn tới mức giảm giá
sâu nhất (−40% đến −47%).

**Diễn giải đúng, không phải "đòn bẩy cao là tốt"**: đây là chuỗi thời gian ngắn (N thực chất là
2 công ty × ~8 năm = ~16 "năm-công-ty" độc lập, không phải 68 quan sát độc lập — kỷ luật khai N
theo `quant-research` skill), giai đoạn 2024-2025 là một đợt tái định giá lớn của toàn bộ nhóm
BĐS/hạ tầng VN (không riêng VIC), rất có thể trùng với chu kỳ định giá macro khác (lãi suất, DT5G
regime) chứ không phải đòn bẩy GÂY RA tăng giá. Điều duy nhất có thể kết luận chắc chắn:
**`Debt_Eq` KHÔNG có giá trị định thời (timing) cho quyết định mua/bán** — giống hệt kết luận đã
rút ra cho CASA/LDR ngân hàng ở report 08-14 (trễ 45 ngày, N nhỏ, không đơn điệu).

**⇒ Một cổng tự động kiểu "Debt_Eq vượt ngưỡng X → cảnh báo/giảm tỷ trọng" sẽ có false-positive
gần như chắc chắn nếu áp cho giai đoạn 2022-2025** — nó sẽ bắn liên tục từ 2022Q2 (khi Debt_Eq VIC
vượt hẳn range 2017-2021) và bỏ lỡ đợt tăng giá lớn nhất lịch sử ngay sau đó. **Không đề xuất cổng
loại này**, đúng nguyên tắc đã chốt cho nhóm ngân hàng.

---

## 4. VIC-family có phải "serial capital raiser" theo đúng định nghĩa 08-17 không?

`FINDINGS.md` (08-17) định nghĩa: **RAISE_SET = RIGHTS ∪ PRIVATE_PLACEMENT ∪ AUCTION**, ngưỡng
serial = **≥2 lần trong 3 năm liền trước**. Base rate đo được: BHAR_250 (1 năm) −7,74% [CI −13,18%,
−1,77%], BHAR_750 (3 năm) −22,03% — nhưng báo cáo đó tự nêu confound pre-trend chưa loại hết.

Tra `tav2_bq.corporate_action` (event_code='ISS', executed) cho VIC/VHM/VRE/VPL, cửa sổ 3 năm liền
trước hôm nay (2023-08-18 → 2026-08-18):

| Mã | Sự kiện RAISE_SET (rights/PP/auction) trong 3Y gần nhất | Serial raiser? |
|---|---|---|
| **VIC** | PP 2025-08-21 (×2 dòng cùng ngày), PP 2026-07-10 (×2 dòng cùng ngày) → **2 đợt phát hành riêng lẻ phân biệt trong 3 năm** | **CÓ — đạt ngưỡng ≥2/3Y** |
| VHM | Không có sự kiện RAISE_SET nào trong 3Y gần nhất (lần gần nhất là PP 2018) | Không |
| VRE | Không có sự kiện RAISE_SET nào trong lịch sử được ghi nhận | Không |
| VPL | Không có sự kiện RAISE_SET nào (chỉ MERGER/PP cũ 2015-2017, ngoài cửa sổ) | Không |

**⇒ VIC (riêng công ty mẹ) đạt ngưỡng "serial raiser" — CÓ THỂ áp base rate 08-17, nhưng với
cảnh báo n=1 nghiêm ngặt như dispatch đã yêu cầu.** BHAR_250 trung bình của population 712 sự kiện
là −7,74% — nhưng **đặt số này lên VIC cụ thể là ngoại suy từ 1 quan sát ra 1 công ty cụ thể**,
đúng loại suy diễn mà `FINDINGS.md` §6 tự cảnh báo không nên dùng để định thời cho 1 mã. Thêm nữa,
2 đợt phát hành gần nhất của VIC (2025-08, 2026-07) đều **nhỏ và có dòng "âm"** (`issue_volumn`
âm cùng ngày — dấu hiệu là **swap/hoán đổi cổ phiếu ESOP hoặc tái cơ cấu sở hữu nội bộ**, KHÔNG
phải huy động tiền mặt mới từ nhà đầu tư bên ngoài như rights/PP thông thường mà FINDINGS.md mô
tả) — `total_value` = 0 cho cả 2 đợt 2025-08 và 2026-07, khác hẳn các đợt PP có tiền thật đổ vào
(2018: 9,3–17,4 nghìn tỷ, 2022: 823 tỷ). **Đây là khác biệt về CHẤT so với population dùng để đo
base rate 08-17** (`total_value > 0` là điều kiện lọc của RAISE_SET gốc — cần kiểm tra lại nếu
2 đợt 2025/2026 của VIC có nằm trong tập 758 events gốc hay bị code phân loại khác).

**KHÔNG XÁC MINH ĐƯỢC** trong phạm vi báo cáo này liệu 2 sự kiện 2025-08/2026-07 của VIC có thực
sự nằm trong tập RAISE_SET đã dùng để tính BHAR_250/750 hay không (cần chạy lại `scr_lib.py` filter
trên đúng 2 sự kiện này để xác nhận, không có trong phạm vi job hôm nay). **Không áp base rate
−7,74%/−22,03% cho VIC như một kết luận chắc chắn** — chỉ nêu như một giả thuyết cần thêm dữ liệu.

---

## 5. Exposure ngân hàng của bot tới nhóm BĐS lớn — GIỚI HẠN DỮ LIỆU

`bigquery_dictionary.json` **không có cột nào** cho biết cơ cấu dư nợ cho vay bất động sản theo
từng ngân hàng (vd "% dư nợ cho vay BĐS/tổng dư nợ" hay "dư nợ cho vay Vingroup" ở cấp ngân hàng
niêm yết). Đây là dữ liệu **KHÔNG có trong BQ hiện tại** — không suy diễn thay.

Con đường khả thi nếu muốn đo (ngoài phạm vi job hôm nay, cần dữ liệu mới):
- Thuyết minh BCTC ngân hàng (phần "dư nợ theo ngành") — cần OCR/nhập tay như CASA/LDR đã làm
  cho bank tail-risk report, KHÔNG tự động hoá được từ BQ hiện có.
- Báo cáo phân tích ngành ngân hàng của công ty chứng khoán (SSI/VCBS/…) — cần WebSearch định kỳ,
  không phải BQ.

Đề xuất: nếu user muốn con số này, đây là một job riêng (giống cách CASA/LDR đã tách ra job riêng
08-14) — không nên vội làm trong job hôm nay để tránh dữ liệu nửa vời.

---

## 6. Thiết kế cảnh báo sớm — TÁI DÙNG khung 3 tầng 08-14, mở rộng đúng loại rủi ro

**Không dựng cơ chế mới.** `bank_tailrisk_insurance_design_20260814.md` đã kết luận (và user đã
duyệt Tầng 1): rủi ro đuôi ở VN đi qua **bằng chứng mất khả năng thanh toán công khai rời rạc**
(tin tức), không đi qua giá hay tỷ số tài chính trễ. §3-4 ở trên xác nhận **kết luận đó ĐÚNG Y HỆT
cho VIC-family** — đòn bẩy không định thời được (§3), giá cũng không định thời được (bank report
§3, chưa test riêng cho VIC nhưng cùng cơ chế).

### Tầng 0 — Xếp hạng tổn thương thường trực (đã có dữ liệu, cập nhật mỗi quý)
`Debt_Eq_P0` VIC/VHM/VPL từ `ticker_financial`, không cò súng — chỉ dùng để đọc tin xấu nghiêm
trọng đến đâu khi nó đến, và làm đầu vào sizing (đòn bẩy càng cao, khi CÓ tin xấu thật thì mức độ
nghiêm trọng kỳ vọng càng lớn — đây là ĐÚNG cách dùng dữ liệu trễ, không phải làm cò súng).

### Tầng 1 — Phát hiện & escalate, mở rộng `fearbuy_weekly_scan.sh` — **đề xuất làm ngay**
Bổ sung **nhóm từ khoá RIÊNG cho BĐS đầu ngành/hạ tầng công**, song song nhóm ngân hàng đã có
(dòng 113-119 của script):

> **NHÓM BĐS ĐẦU NGÀNH/HẠ TẦNG CÔNG — BỔ SUNG:**
> chậm/vỡ nợ trái phiếu doanh nghiệp · không thanh toán được lãi/gốc trái phiếu đến hạn ·
> tổ chức xếp hạng tín nhiệm hạ bậc · ngân hàng siết nợ/thu hồi tài sản đảm bảo · dự án hạ tầng
> chậm tiến độ/đội vốn bị thanh tra · SBV/NHNN thay đổi chính sách loại trừ room tín dụng ·
> Vingroup/VinFast dòng tiền · huỷ/hoãn niêm yết trái phiếu · kiện tụng nhà thầu/nợ đọng xây dựng

Chi phí biên ~0 — bám đúng cron thứ Sáu đã chạy, chỉ thêm từ khoá vào đúng vị trí Tầng 1 hiện có.

### Tầng 2 — Cân nhắc hành động (KHÔNG tự động, cần user duyệt)
Giữ nguyên điều kiện đã chốt 08-14: **≥2 tín hiệu độc lập, bắt buộc có ≥1 tín hiệu solvency**
(vỡ nợ trái phiếu thật, hạ bậc tín nhiệm thật, hoặc siết nợ thật — KHÔNG phải giá hay Debt_Eq).
Không cần chốt lại chính sách này — user đã quyết 08-14 cho nhóm ngân hàng, áp dụng nguyên văn.

**Khác biệt duy nhất so với khung ngân hàng**: kênh lan truyền tới portfolio ở đây là GIÁN TIẾP
qua sổ ngân hàng (17-36% NAV) nhiều hơn là trực tiếp (VHM/VRE 2,6-8,1% NAV) — nên nếu Tầng 2 mở
thật vì tin xấu VIC-family, câu hỏi hành động đúng có thể là **"giảm tỷ trọng ngân hàng có exposure
cao tới BĐS"** chứ không chỉ "bán VHM/VRE" — nhưng §5 cho thấy hiện KHÔNG có dữ liệu để biết ngân
hàng nào exposure cao hơn ngân hàng nào. Đây là khoảng trống thật, không phải chi tiết vặt.

---

## 7. Bảng tổng hợp VERIFIED / HYPOTHESIS (yêu cầu (b) của dispatch)

| # | Claim | Trạng thái | Ghi chú |
|---|---|---|---|
| VIC-family đòn bẩy đang tăng mạnh | **VERIFIED** | Debt_Eq VIC 1,64→6,24 (3,8×), VHM 0,75→3,05 (4,1×), đo trực tiếp BQ |
| VIC "chiếm ~10% tổng tín dụng quốc gia" | **REFUTED** | Đo được ~1,77% (355.756 tỷ / 20,15 triệu tỷ), 2 nguồn khớp nhau |
| SBV có cơ chế ưu đãi tín dụng riêng cho VIC/Sun/Masterise | **VERIFIED** | Công văn 5368/NHNN-TD 22/06/2026, loại trừ 752.000 tỷ khỏi trần tăng trưởng |
| Lãi suất vay BĐS 12-16%/năm, thanh khoản chững, giá giảm | **PHẦN LỚN VERIFIED qua WebSearch** (lãi suất phổ biến 9-11%, dự báo tăng thêm 3-4đ%; tỷ lệ hấp thụ giảm còn 95% 2025; 61% người khảo sát hoãn mua nhà) | Không xác minh trực tiếp mức 12-16% cụ thể user nêu, nhưng chiều hướng khớp |
| Đòn bẩy/tỷ số tài chính có thể dùng làm cò súng bán | **REFUTED bằng test lịch sử** | §3: quan hệ không đơn điệu, giai đoạn đòn bẩy cao nhất trùng đợt tăng giá lớn nhất lịch sử |
| VIC là "serial capital raiser" theo định nghĩa 08-17 | **VERIFIED có điều kiện** | Đạt ngưỡng ≥2/3Y nhưng 2 sự kiện gần nhất `total_value=0` — khác chất với population gốc, chưa xác nhận có nằm trong tập tính BHAR không |
| Áp base rate BHAR_250 −7,74% cho riêng VIC | **HYPOTHESIS, N=1** | Không đủ căn cứ ngoại suy population→1 công ty cụ thể |
| Bank exposure tới nhóm BĐS đo được từ BQ | **KHÔNG CÓ DỮ LIỆU** | Không có cột phù hợp trong `bigquery_dictionary.json`, cần nguồn khác (BCTC/report ngành) |
| VRE Debt_Eq gần đây | **KHÔNG XÁC MINH ĐƯỢC lý do** | Dữ liệu BQ dừng ở 2023Q4, không rõ nguyên nhân |

---

## 8. Câu hỏi cần user quyết (theo mẫu §9 báo cáo 08-14)

1. **Có muốn tôi dựng Tầng 1** (mở rộng từ khoá BĐS/Vingroup cho `fearbuy_weekly_scan.sh`, §6)
   ngay không? Đây là phần rẻ nhất, giá trị nhất, và là khuyến nghị hành động duy nhất của báo
   cáo này.
2. **Có muốn tôi giao Winston điều tra tại sao `ticker_financial` dừng cập nhật VRE ở 2023Q4**
   không (§2) — có thể là gap dữ liệu cần vá, hoặc phản ánh thay đổi cấu trúc thật của VRE.
3. **Có muốn mở job riêng để đo bank exposure tới nhóm BĐS lớn** (§5, cần dữ liệu ngoài BQ — BCTC
   thuyết minh hoặc report ngành, không tự động hoá được từ nguồn hiện có) không?
4. **Có muốn tôi xác minh lại xem 2 sự kiện phát hành 2025-08/2026-07 của VIC có nằm trong tập
   RAISE_SET gốc của FINDINGS.md 08-17 không** (§4, hiện là khoảng trống chưa đóng) — việc này
   dùng lại code có sẵn (`scr_lib.py`), không phải nghiên cứu mới.
