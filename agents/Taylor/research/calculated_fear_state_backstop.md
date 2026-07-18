# "Mua khi sợ hãi có tính toán" — State-Backstop Special-Situation Playbook

> Taylor (Quant/Algo), job `Taylor_20260717_122129`, 2026-07-17. **RESEARCH-ONLY — không wire production.**
> Case mẫu: **TV1 (PECC1)**. Đây là một *playbook special-situations có kỷ luật*, KHÔNG phải một book
> hệ thống hoá (N quá nhỏ). Mọi vị thế theo pattern này = manually-curated, cần user duyệt từng tên.

---

## 0. Luận điểm một câu
Khi **scandal CÁ NHÂN lãnh đạo** (không phải scandal chạm vào chính tài sản lõi) đánh sập giá một
doanh nghiệp **có cổ đông nhà nước/chiến lược chi phối (>50%)** đang sở hữu **tài sản sinh tiền đã
hết/gần hết nợ**, thị trường bán tháo *pháp nhân* vì sợ *con người* — tạo khoảng lệch giá có thể khai
thác. Điều KIỆN QUYẾT không phải "mua sau khi bắt", mà là **bộ tiêu chí phân biệt** (§2): pattern
thắng đúng khi tài sản lõi tách biệt khỏi người bị điều tra và vẫn tạo tiền.

---

## 1. Bằng chứng lịch sử (đo trên BQ cache `ticker`, adjusted Close, trough→forward return)

| Ticker | Sự kiện | Loại | DD đáy | +6m | +12m | +18m | Kết luận |
|---|---|---|---|---|---|---|---|
| **PNJ** | 8/2015 DongABank bị kiểm soát đặc biệt (chồng CT Cao Thị Ngọc Dung = Trần Phương Bình) | ✅ QUALIFY (contagion cá nhân/liên quan, lõi bán lẻ trang sức intact) | −27% | **+50%** | **+148%** | **+160%** | Textbook — hồi phục khổng lồ |
| **VEA** | 3/8/2019 bắt cựu CT/TGĐ Trần Ngọc Hà (vi phạm quản lý tài sản NN) | ✅ QUALIFY (NN sở hữu 88%, cash-cow cổ tức từ JV Honda/Toyota/Ford) | −28% | +4% | **+21%** | +19% | **Twin cấu trúc của TV1**; giá-only khiêm tốn nhưng VEA trả cổ tức ~50%+/năm → total return cao hơn nhiều |
| TIS | 4/2019 đại án TISCO-2, nhiều sếp bị khởi tố | ⚠️ AMBIGUOUS (NN, nhưng lõi thép *đang* có vấn đề) | −62% | +69% | +98% | +152% | Hồi phục THẬT nhưng do **chu kỳ thép 2020-21** (beta ngành), không phải resolve scandal — bài học: đừng nhầm beta ngành với edge của pattern |
| OCH | 10/2014 Hà Văn Thắm (parent OceanBank) | ⚠️ sub giàu tài sản bị parent kéo | −82% | +42% | +2% | +36% | Choppy; multi-bagger thật đến sau 18m (ngoài cửa sổ) |
| **OGC** | 10/2014 Hà Văn Thắm | ❌ NON (lõi = gian lận ngân hàng) | −69% | −43% | **−26%** | −70% | Không hồi phục — scandal LÀ tài sản lõi |
| **PVX** | 2017 mất khả năng thanh toán PVC/PVX (Trịnh Xuân Thanh) | ❌ NON (lõi = phá sản vận hành) | −57% | −17% | **0%** | −8% | Không hồi phục |
| **FLC** | 3/2022 Trịnh Văn Quyết thao túng | ❌ NON (gian lận/thao túng = lõi) | — | — | — | — | **Huỷ niêm yết → mất trắng** |
| **HVN** | 2021 (COVID) | ❌ NON (suy giảm vận hành lõi, không phải scandal cá nhân) | −16% | +28% | **−14%** | −24% | NN sở hữu không cứu được khi lõi hỏng |
| PVD/PVS/GAS | 12/2017 bắt Đinh La Thăng | ↔️ tác động mỏng | −6..−10% | +13..+16% | +6..+19% | +7..+48% | Scandal nhắm parent PVN, các cty khai thác niêm yết gần như không bị hề hấn → DD do scandal quá nhỏ để là "case" |

**Cụm điện hiện tại (2026, đang diễn ra — chỉ đo được DD, recovery CHƯA quan sát được):**

| Ticker | Công bố | preHi(120d) | Đáy tạm | DD | Bounce từ đáy (đến 13/07) |
|---|---|---|---|---|---|
| **TV1** | 22/05 (bắt 07/05) | 39.400 | 22.000 (còn dò) | **−44%** | 0% (chưa lập đáy chắc) |
| **PC1** | 15/05 | 31.350 | 17.650 | **−44%** | **+20%** |
| **TV2** | 21/05 | 43.050 | 26.600 (còn dò) | **−38%** | 0% |
| TV3 | 09/06 | 18.000 | 14.500 | −19% | +7% |
| TV4 | 12/06 | 16.700 | 12.600 | −25% | +3% |
| DGC | 17/03 (KB special case) | 95.810 | 44.850 | **−53%** | (đang dò, quá sớm) |

### Đọc bằng chứng
- **Discriminator HOẠT ĐỘNG**: 2/2 case QUALIFY (lõi intact, scandal cá nhân) hồi phục có ý nghĩa;
  0/4 case NON (OGC/PVX/FLC/HVN — scandal chạm lõi hoặc lõi tự hỏng) hồi phục. Cái quyết định thắng-thua
  là **bản chất scandal + tính tách biệt của tài sản lõi**, KHÔNG phải "đã giảm sâu bao nhiêu".
- **N nhỏ → đây là playbook, không phải edge thống kê**. "Win rate" 2/2 không có ý nghĩa thống kê.
  Giá trị nằm ở BỘ LỌC (§2) + kỷ luật sizing/exit (§3), áp từng case, KHÔNG systematize vào V2.4.
- **Cảnh báo beta ngành (TIS)**: một số "hồi phục" đến từ chu kỳ ngành trùng thời điểm (thép 2020-21),
  không phải từ resolve scandal. Khi quy kết edge cho pattern, phải trừ beta ngành/thị trường cùng kỳ.
- **Total-return > price-return với SOE cổ tức cao (VEA)**: đo giá-only *hiểu thấp* các cash-cow trả
  cổ tức lớn. Với TV1, cổ tức là một phần catalyst (§4), không chỉ là re-rating giá.

---

## 2. Bộ tiêu chí sàng lọc — QUALIFY vs KHÔNG

### ✅ ĐỦ ĐIỀU KIỆN (tất cả phải đúng)
1. **Scandal là CÁ NHÂN**: khởi tố lãnh đạo vì hành vi cá nhân (tham ô/vi phạm kế toán/quản lý tài sản)
   — KHÔNG phải cáo buộc làm sản phẩm/dịch vụ/tài sản lõi vô giá trị hay bất hợp pháp.
2. **Cổ đông NN/chiến lược chi phối >50%** với năng lực & động cơ backstop (EVN/SCIC/PVN/Viettel/TKV/Bộ
   ngành). Động cơ cổ tức của NN là dấu hiệu tốt (SOE không thích ôm tiền mặt vô mục đích → ép chia).
3. **Tài sản lõi sinh tiền TÁCH BIỆT khỏi người bị điều tra**: thuỷ điện/cảng/hạ tầng viễn thông/BĐS KCN
   đã vận hành, hợp đồng/giấy phép không phụ thuộc cá nhân đó. Kiểm tra bằng **CF_OA thực dương và ≥ NP**
   (tiền khó nguỵ tạo hơn accrual đang bị điều tra — TV1: CF_OA_P0 ≥ NP_P0 nhiều quý liền).
4. **Bảng cân đối solvent**: net cash hoặc nợ thấp/đã trả hết nợ dự án, nợ được dòng tiền tài sản phủ.
   (TV1: Debt/Eq 1,64→0,91, nợ Sông Bung 5 đã trả hết từ 2026.)
5. **Sàn định giá**: giá ≈ hoặc dưới book hữu hình (PB≲1,2) HOẶC <5x lợi nhuận thực đã bị nén, với
   PE_MA5Y cao hơn nhiều (TV1: PE 3,9x vs PE_MA5Y 11,65 · PB 1,08).

### ❌ KHÔNG ĐỦ (bất kỳ điều nào → loại)
- Scandal lan vào **pháp nhân/tài sản lõi**: giấy phép bị rút, tài sản bị kê biên, hợp đồng bị vô hiệu,
  cáo buộc thao túng/gian lận BCTC làm *toàn bộ* con số vô giá trị (FLC, OGC — gian lận ngân hàng LÀ lõi).
- **Lõi tự hỏng độc lập với scandal**: mất khả năng thanh toán, ngành sụp, sản phẩm ế (PVX phá sản; HVN
  đội bay nằm đất vì COVID — NN sở hữu không cứu nổi lõi hỏng).
- **DN tư nhân không có backstop/áp lực cổ tức từ NN** → thiếu trụ #2, không có bên nâng đỡ giá trị.
- ⚠️ **Rủi ro RIÊNG của TV1 (khác rủi ro pháp lý cá nhân)**: **cả 4 Big4 từ chối kiểm toán** → nguy cơ
  thiếu BCTC kiểm toán → **bị hạn chế/đình chỉ giao dịch**. Đây là tail-risk kiểu-OGC/PVX/FLC (về gần 0
  / huỷ niêm yết). Không tự động loại TV1, nhưng **hạ sizing** và biến việc *chọn được kiểm toán* thành
  **cổng nhị phân** (xem §4). Đây là lý do TV1 xứng đáng size NHỎ HƠN PNJ/VEA ngày đó.

---

## 3. Khung entry/exit kỷ luật tổng quát (không riêng TV1)

**Sleeve riêng "special-situation", KHÔNG phải core book. Cap cứng mỗi tên 2–4% NAV** (tail-risk đình
chỉ giao dịch là thật). Không bao giờ size như một vị thế momentum/value thường.

### Entry — 3 tranche (không cố bắt đáy)
- **T1 (1/3)** khi đã QUALIFY §2 **và** DD>35% **và** giá ≤ book hữu hình. Chấp nhận còn dò đáy.
- **T2 (1/3)** khi có *ổn định giá* (higher-low + volume cạn kiệt) **hoặc** 1 catalyst dương đầu tiên.
- **T3 (1/3)** khi **catalyst xác nhận** (chọn được kiểm toán / công bố BCTC kiểm toán sạch / cổ tức
  thực trả / gỡ hạn chế giao dịch). Đây là tranche "thêm khi luận điểm được chứng minh", không phải đoán.

### Exit — chốt lời theo tầng + stop cứng
- **Tầng 1**: trim 1/3 tại **+30–40%** (khớp median cú nảy đầu — PC1 đã +20%, các nảy nhanh 30–50%).
- **Tầng 2**: trim 1/3 tại **sàn fair-value thận trọng** (giá trị theo DDM/tài sản — vùng downside gặp
  giá) HOẶC khi PE hồi ~0,6× PE_MA5Y.
- **Runner (1/3 cuối)**: giữ chạy tới re-rating về PE chuẩn hoá (PE_MA5Y) — **CHỈ KHI** các catalyst
  xác nhận đã lần lượt về (audit sạch, cổ tức trả, thay CT, gỡ hạn chế). Runner này chính là phần bắt
  trọn PNJ +148% / TIS +98%. Không có catalyst xác nhận → không giữ runner, chốt hết ở tầng 2.
- **HARD ABANDON (cắt bất kể giá)** — bất kỳ điều nào:
  1. Scandal **di cư từ cá nhân → pháp nhân/tài sản lõi** (rút phép, kê biên tài sản, vô hiệu hợp đồng).
  2. BCTC kiểm toán (khi có) **lộ ra tiền/tài sản đã bị thổi phồng** → luận điểm "lõi còn tiền" sai.
  3. **Đình chỉ/huỷ niêm yết thành hiện thực** (không chỉ cảnh báo) — thoát trước khi mất thanh khoản.
  4. **Backstop gãy**: parent NN ép rút giá trị chống cổ đông nhỏ, hoặc cổ tức đã hứa bị huỷ.
- **Time stop**: không ổn định/không catalyst trong ~12–18 tháng và giá liên tục lập đáy thấp hơn →
  luận điểm hỏng (mọi recovery quan sát được đều gom trong 6–18m).

---

## 4. TV1 — bảng theo dõi catalyst (Part 4)

Trạng thái tại 2026-07-17 (giá 22.000, PE 3,87x, PB 1,08x, MA200 25.878 → dưới MA200; DD từ ~63k về
20,4k ≈ −68% đỉnh-dài, −44% đỉnh-120d):

| Catalyst | Trạng thái 17/07 | Ý nghĩa | Mốc theo dõi |
|---|---|---|---|
| **Chọn được đơn vị kiểm toán** | ❌ CHƯA. Cả 4 Big4 (Deloitte/EY/KPMG/PwC) từ chối. Chốt DS cổ đông 20/07, **lấy ý kiến bằng văn bản 10/08** để chọn đơn vị kiểm toán khác | **Cổng nhị phân quan trọng nhất.** Không có kiểm toán → nguy cơ hạn chế/đình chỉ GD (tail-risk). Chọn được (dù ngoài Big4) = gỡ được rủi ro pháp-nhân lớn nhất | **10/08/2026** (kết quả lấy ý kiến) |
| **Cổ tức 2025 tỷ lệ 15% thực trả** | ⏳ ĐHCĐ đã duyệt nâng 6%→15% (LN kỷ lục 150,2 tỷ). Guide 2026 ≥10%. **Chưa có ngày ĐKCC/ngày thanh toán** | Cổ tức THỰC TRẢ = xác nhận (a) tiền thật, (b) NN backstop qua chính sách chia, (c) thu hẹp khoảng cách full-FCF DCF vs DDM (câu hỏi phân bổ vốn trung thực) | Chờ nghị quyết HĐQT về ngày ĐKCC |
| Thay Chủ tịch / kiện toàn HĐQT | (theo dõi) | Bình thường hoá quản trị | — |
| Trạng thái hạn chế GD trên HNX | Chưa bị (còn thời hạn nộp BCTC) | Nếu bị đưa vào diện cảnh báo/kiểm soát → tín hiệu tail-risk kích hoạt | Theo hạn nộp BCTC bán niên/soát xét |

**Đọc TV1 theo khung**: TV1 QUALIFY §2 (scandal cá nhân · EVN 54,34% · Sông Bung 5 hết nợ, biên >50% ·
CF_OA≥NP · PB~1). NHƯNG mang **tail-risk kiểm toán/đình chỉ** mà PNJ/VEA không có → **size nhỏ hơn** và
coi **10/08 (kiểm toán)** là cổng T3. Khoảng full-FCF DCF (40k–140k) vs DDM (12k–19k) chính là "công ty
có phân bổ vốn trung thực không" — mà cổ tức 15% thực trả sẽ trả lời một phần.

---

## 5. Khuyến nghị cho đội
- **KHÔNG** wire vào V2.4/hệ thống sống. Đây là **sleeve special-sit thủ công**, cap 2–4%/tên, user
  duyệt từng tên (đúng human-in-the-loop).
- Nếu đội muốn theo đuổi: dựng **watchlist "state-backstop special-sit"** — quét các DN NN-chi-phối có
  lãnh đạo bị khởi tố, chạy bộ lọc §2, xếp theo (PB, CF_OA/NP, mức backstop). TV1 là case sống đầu tiên.
- Theo dõi 2 catalyst TV1 (kiểm toán 10/08 · ngày trả cổ tức 15%) như tín hiệu falsify/confirm luận điểm.

---

## 6. Case #2 — DGC (Hoá chất Đức Giang), thêm 2026-07-17 (Mike, dispatch từ user)

**KHÔNG phải NN chi phối** (tư nhân, họ Đào Hữu Huyền kiểm soát) — khác TV1/VEA, giống PNJ (cũng tư
nhân). Xác nhận qua case này: tiêu chí "NN>50%" trong §2 KHÔNG phải điều kiện bắt buộc cứng — PNJ đã
hồi phục +148%/12m dù không có NN backstop. Discriminator thật sự quan trọng hơn là **tài sản/hoạt
động lõi có tách biệt khỏi hành vi bị điều tra hay không** (§2 tiêu chí #1+#3), không phải cơ cấu sở
hữu.

**Bối cảnh**: 17/03/2026 khởi tố Chủ tịch Đào Hữu Huyền + con trai + nhiều lãnh đạo (14 bị can) về
3 nhóm hành vi: (a) vi phạm kế toán, (b) khai thác Apatit trái phép, (c) xả thải ô nhiễm tại KCN Tằng
Loỏng. Thiệt hại thuế cho NN được nêu ~"hàng chục tỷ" — NHỎ hơn nhiều so với **331,3 tỷ đã tự nguyện
khắc phục** (dấu hiệu thiện chí/dư dả tài chính, không phải vá lỗ hổng lớn). DGC là DN đầu ngành thật
(chi phối ~1/3 xuất khẩu phốt pho vàng toàn cầu, công nghệ độc quyền) — khác về CHẤT so với case
"lõi giả tưởng" (OGC/FLC).

**⚠️ PHÁT HIỆN QUAN TRỌNG — DGC KHÔNG qua được bài test CF_OA≥NP mà chính §2 đề ra:**

| | 2026Q1 (quý xảy ra scandal) | 5 quý trước |
|---|---|---|
| Revenue YoY | **-24,4%** | +1,3% đến +17,8% |
| NP YoY | **-49,5%** | dương ổn định |
| GPM | 28,66% (thấp nhất) | 31-36% |
| **CF_OA** | **-1.093 tỷ** (âm mạnh) | +281 đến +786 tỷ (luôn dương) |
| FSCORE | 2/9 (thấp nhất) | 2-7 |

→ Khác hẳn TV1 (CF_OA≥NP mọi quý suốt vụ án — lõi sạch xác nhận bằng dữ liệu), ở DGC quý xảy ra
scandal có **CF_OA âm sâu trong khi NP vẫn dương** — đúng loại tín hiệu "accrual/lõi có vấn đề" mà
chính tiêu chí #3 của khung này được thiết kế để bắt. Chưa rõ đây là (a) tác động thật từ scandal
(khách hàng/đối tác thận trọng, gián đoạn giao dịch), (b) chu kỳ ngành hóa chất/phốt pho đang yếu
riêng biệt, hay (c) chi phí một lần (khắc phục 331 tỷ + phí pháp lý) — **Q1 chỉ có ~2 tuần sau ngày
khởi tố (17/03) nên không thể quy hết cho scandal.**

**Giá**: đỉnh trước scandal 95.810 → đáy 44.850 → hiện tại (17/07) 44.800 — **CHƯA có tín hiệu tạo đáy
ổn định** (dưới MA50/MA200, RSI yếu, CMF âm), khác PNJ đã bật +50%/6m ngay từ đầu.

**Kết luận: DGC = case AMBIGUOUS (giống TIS/OCH), CHƯA đủ điều kiện QUALIFY §2 để vào T1/T2** — mặc dù
định giá hấp dẫn (PB 1,07x gần book, PE 6,48x vs PE_MA5Y 10,89x) và câu chuyện thiệt hại-nhỏ-hơn-khắc-
phục ủng hộ luận điểm giá trị, phát hiện CF_OA<<NP là lý do đủ mạnh để **CHỜ KQKD Q2/2026** (dự kiến
công bố cuối tháng 7 theo lịch sử — Q2/2025 công bố 22/07) làm cổng xác nhận:
- CF_OA dương trở lại + doanh thu hồi phục → nâng cấp QUALIFY, vào T1
- CF_OA tiếp tục âm/doanh thu tiếp tục giảm → chuyển sang nhóm NON, không vào

**Ước tính lợi nhuận kỳ vọng 12 tháng tại giá 44.800** (dùng làm ví dụ minh hoạ cách lượng hoá case
AMBIGUOUS, không phải khuyến nghị vào ngay):
- Bull (giống PNJ, Q2 xác nhận Q1 chỉ là sốc 1 quý): PE về PE_MA5Y 10,89x → ~75.250 (**+68%**)
- Base (tái định giá một phần, PE→8,5-9x): ~59.000-63.400 (**+32-41%**)
- Bear (Q2 xác nhận suy giảm thật, không chỉ do scandal): 40.000-45.000 (**-11% đến 0%**)
- Kỳ vọng trung tâm nếu phải chọn 1 số: **~+25-35%/12m** — thấp hơn nhiều PNJ (+148%) đúng vì thiếu
  xác nhận "lõi sạch" mà PNJ/TV1 có tại thời điểm entry.

**Việc cần làm tiếp**: theo dõi ngày công bố BCTC Q2/2026 DGC (ước cuối tháng 7/đầu tháng 8 theo lịch
sử công bố các năm trước), đọc lại đúng 2 chỉ số CF_OA và Revenue YoY làm cổng quyết định.

---

## 7. Case #3 — PNJ (P-Lab 2026), thêm 2026-07-18 (Taylor, dispatch từ Mike, job `Taylor_20260718_044400`)

**KHÔNG phải NN chi phối** (tư nhân, gia đình sáng lập Cao Thị Ngọc Dung) — giống DGC. Theo kết luận
đã chốt ở §6, tiêu chí "NN>50%" KHÔNG phải điều kiện cứng → không tự động loại (tiêu chí #2 pass mềm).

**⚠️ ĐÂY LÀ CASE KHÓ NHẤT của khung cho tới nay** vì nó rơi ĐÚNG vào cái bẫy mà framework được thiết
kế để tránh: **PNJ đã có 1 case QUALIFY textbook trong chính §1 (2015, DD−27%→+148%/12m)** — nhưng bản
chất scandal lần này KHÁC HẲN, và mặc định "PNJ từng qua 2015 thì lần này cũng qua" chính xác là loại
sai lầm "nhầm case cũ với case mới" mà §0/§2 cảnh báo.

### Bối cảnh (đã verify qua tin tức thật — Mike tra, không query lại)
Cựu giám đốc **P-Lab** (công ty con giám định kim cương của PNJ) bị bắt liên quan đường dây buôn lậu
kim cương xuyên quốc gia (141 lô, ~28.000 viên từ 2024) — dùng chuyên môn **xóa mã laser GIA gốc** và
**cấp chứng chỉ P-Lab giả**. Công bố 02/07/2026. Giá sàn 3 phiên liên tiếp (03–07/07): 63.100→50.800
(**−19,5% trong 3 phiên**). Khuếch đại bởi **FPTS cắt margin PNJ 50%→30% hiệu lực 08/07** (bán cưỡng
bức — volume 08/07 nhảy vọt 25,6 triệu cp). PNJ tuyên bố cáo buộc liên quan cá nhân cựu GĐ, không có
kim cương lậu vào hệ thống bán lẻ, đang hợp tác điều tra + công bố **ý định** mua cổ phiếu quỹ (08/07).

**Cập nhật 18/07/2026 (Winston, job `Winston_20260718_051002`, verified qua Tuổi Trẻ/VnExpress/
Vietstock/CafeF/Dân Trí/Người Quan Sát):**
- **16/07**: NQ HĐQT (CT Cao Thị Ngọc Dung ký) — CHỦ TRƯƠNG thuê 3 tổ chức quốc tế độc lập: (a) kiểm
  định chất lượng sản phẩm, (b) kiểm toán TOÀN BỘ chuỗi nhập khẩu→sản xuất→bán kim cương (kèm kiểm
  toán thuế 2025), (c) tư vấn đánh giá hệ thống quản trị rủi ro. TGĐ Phan Quốc Công được giao tìm/
  đàm phán/ký HĐ, Ủy ban Kiểm toán giám sát. **CHƯA có tên đơn vị cụ thể, CHƯA có timeline, CHƯA cam
  kết công bố công khai kết quả** — về nguyên tắc đây là catalyst T2/T3 mạnh (đúng khung §3), nhưng
  còn quá non để coi là cổng xác nhận (xem khuyến nghị timing cuối §7.5).
- **Cổ phiếu quỹ — ĐÍNH CHÍNH quan trọng**: con số "169.559 cp, giá ≥50.000đ" lan truyền là bước
  **BÁN** cổ phiếu quỹ CŨ đang có (bắt buộc theo NĐ 245/2025 trước khi mua lại đợt mới) — **KHÔNG
  phải quy mô đợt MUA LẠI**. Quy mô/giá trần đợt mua lại thật **CHƯA công bố**; mới ở giai đoạn lấy ý
  kiến cổ đông bằng văn bản, ĐKCC 17/08/2026.
- **Vụ án mở rộng (Chuyên án 268V)**: tới 12–14/07 đã 31 bị can (thêm 4 chủ tiệm vàng TP.HCM + **1
  nhân viên P-Lab khởi tố 14/07, được truyền thông nêu là EM TRAI một thành viên HĐQT PNJ**), tổng
  giá trị buôn lậu >1.500 tỷ, thu lợi bất chính >300 tỷ. Governance-link này thu hẹp nhẹ khoảng cách
  "cá nhân bên ngoài" nhưng **cáo buộc vẫn nhắm cá nhân**, CHƯA khởi tố pháp nhân PNJ, chưa kê biên
  → chưa chạm HARD ABANDON §3.

### Tiêu chí #1 (scandal cá nhân vs chạm lõi) — ĐIỂM QUYẾT ĐỊNH, và là điểm KHÁC 2015

| | PNJ 2015 (QUALIFY textbook) | PNJ 2026 (case này) |
|---|---|---|
| Vị trí scandal | Ngân hàng của **CHỒNG** chủ tịch (DongABank) — **ngoài ngành, ngoài công ty** | **Công ty con của chính PNJ** (P-Lab) |
| Sản phẩm bị làm giả | Không có — thuần contagion cá nhân/liên quan | **Chứng chỉ giám định kim cương** — một mắt xích trong chuỗi giá trị kim cương PNJ bán trực tiếp cho khách |
| Khoảng cách tới lõi | Rất xa (0 chạm lõi bán lẻ) | **Gần lõi hơn nhiều** — nội bộ + chạm product-integrity |

→ **Phép loại suy 2015 YẾU hơn vẻ ngoài.** 2015 = pure external contagion; 2026 = scandal nội bộ về
tính toàn vẹn sản phẩm. KHÔNG được coi 2015 là bằng chứng "PNJ luôn hồi phục". Đánh giá độc lập 3 lớp:

- **(a) Quy mô P-Lab trong PNJ**: BQ chỉ có số hợp nhất, **không có segment breakdown** cho P-Lab
  (giới hạn dữ liệu — nêu rõ). Nhưng cơ cấu doanh thu PNJ bị **bán lẻ vàng/trang sức truyền thống chi
  phối áp đảo** (riêng Q1/2026 doanh thu hợp nhất 17,37 nghìn tỷ). P-Lab là **mảng giám định/chứng
  nhận** (dịch vụ), không phải trung tâm doanh thu bán lẻ → gần như chắc chắn là **tỷ trọng nhỏ** trong
  doanh thu/LN hợp nhất. Điểm này **kéo về phía criterion #1** (ngoại vi, lõi bán lẻ vàng không bị chạm).
- **(b) Rủi ro lan uy tín (đây là phần "gần lõi" thật)**: khách hàng có thể nghi ngờ **TẤT CẢ chứng
  chỉ P-Lab đã cấp trước đây** (không chỉ 28.000 viên bị điều tra) → tổn hại thương hiệu **rộng hơn phạm
  vi vụ án hình sự**, chạm vào mảng kim cương/kim hoàn cao cấp (biên cao, đang tăng trưởng). Đây là rủi
  ro reputational, không phải rủi ro pháp nhân trực tiếp — nhưng THẬT.
- **(c) Quan hệ GIA (tổ chức quốc tế) — "chiếc đèn báo lõi" quan trọng nhất**: scandal DÍNH TRỰC TIẾP
  GIA (xóa mã laser GIA gốc). Nếu **GIA rút công nhận/hợp tác với P-Lab** → đây là **tổn hại LÕI thật**
  (không còn là tin đồn), vì năng lực chứng nhận quốc tế là tài sản cạnh tranh của mảng kim cương. **Chưa
  có tin GIA phản ứng** — đây là watch-item hạng nhất, không phải điều đã biết.

**Kết luận tiêu chí #1: AMBIGUOUS.** Gần lõi hơn 2015 (nội bộ + product-integrity), nhưng lõi lớn nhất
(bán lẻ vàng) không bị chạm và P-Lab là mảng nhỏ. KHÔNG phải "lõi giả tưởng" kiểu OGC/FLC (loại NON),
cũng KHÔNG phải contagion cá nhân sạch kiểu 2015 (QUALIFY). Nằm CHÍNH GIỮA.

### Tiêu chí #3 (CF_OA≥NP, lõi tách biệt) — mùa vụ ĐÃ VERIFY + khoảng trống dữ liệu DÀI

**Xác nhận giả thuyết mùa vụ (query BQ 5 năm, adjusted):** CF_OA PNJ theo quý (nghìn tỷ VND):

| Quý | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2022 | +1,71 | +0,20 | −0,64 | **−1,18** |
| 2023 | +1,40 | −0,31 | +0,65 | **−0,24** |
| 2024 | +1,89 | +0,23 | −0,46 | **−1,57** |
| 2025 | −0,24 | +0,13 | +1,82 | **−1,70** |
| 2026 | **+3,56** | *(chưa CB)* | — | — |

→ **Q4 âm ĐỀU ĐẶN 5/5 năm** (tích trữ vàng trước Tết → dòng tiền vận hành âm Q4 là BÌNH THƯỜNG, không
phải dấu hiệu xấu). **Hệ quả methodology quan trọng:** với PNJ, tiêu chí #3 **KHÔNG áp được kiểu "1 quý
âm = xấu"** như đã làm với DGC ở §6 — phải so **YoY cùng quý**, không so quý liền kề. Đây là tinh chỉnh
khung mà case DGC không cần (DGC không có mùa vụ CF_OA rõ như PNJ).

**Trên dữ liệu MỚI NHẤT có sẵn (2026Q1, công bố 29/04/2026, hoàn toàn TRƯỚC khủng hoảng): tiêu chí #3
PASS mạnh** — CF_OA_P0 **+3,558 nghìn tỷ >> NP_P0 +1,467 nghìn tỷ**; Revenue YoY **+77,9%**; FSCORE
**7/9**; ROE_Trailing **27,1%**; NPM 8,5%. Lõi bán lẻ vàng đang tạo tiền tốt.

**⚠️ NHƯNG dữ liệu đó ENTIRELY PRE-CRISIS.** Scandal nổ 02/07/2026 = **đầu Q3/2026**. Các cổng:
- **BCTC Q2/2026** (Apr–Jun, ước công bố ~cuối tháng 7 — lịch sử Q2/2025 công bố 29/07) → **hoàn toàn
  trước khủng hoảng, KHÔNG phản ánh tác động thật**. Chỉ có giá trị ở phần thuyết minh/guidance ban lãnh
  đạo về P-Lab (nếu có).
- **BCTC Q3/2026** (Jul–Sep, ước công bố **~cuối tháng 10** — lịch sử Q3/2025 công bố 28/10/2025) =
  **cổng xác nhận tiêu chí #3 THẬT SỰ** — quý đầu tiên bao trọn khủng hoảng. Đọc **CF_OA (so YoY vs
  Q3/2025 +1,82T, KHÔNG so Q2)** + Revenue YoY + thuyết minh mảng kim cương.

→ **Khoảng trống dữ liệu DÀI ~3,5 tháng** — xa hơn NHIỀU so với DGC (DGC đã có Q1 ~2 tuần sau khởi tố +
Q2 cận kề lúc đánh giá). **Không thể kết luận QUALIFY/NON ngay bây giờ** — đây là lý do cấu trúc, không
phải do thiếu phân tích.

### Tiêu chí #4 (bảng cân đối) — PASS
Debt_Eq_P0 = **0,367** (Q1/2026, thấp/solvent; dải lịch sử 0,21–0,77, lành mạnh). Bán lẻ vàng cần vốn
tồn kho nhưng đòn bẩy thấp. ✓

### Tiêu chí #5 (sàn định giá) — PASS trên trục "chiết khấu vs lịch sử của chính nó"
Tại giá **43.000 (17/07)**: **PE 6,08x vs PE_MA5Y 16,09x (SD5Y 3,91 → 2,56 SD DƯỚI trung bình)**; **PB
1,53x vs PB_MA5Y 3,05x (SD5Y 0,56 → 2,70 SD DƯỚI trung bình)**. Lưu ý: PB 1,53 **KHÔNG** ≲1,2 (không ở
book hữu hình) — nhưng khác TV1 (thủy điện nặng tài sản, PB~1 hợp lý), PNJ là **bán lẻ thương hiệu
asset-light, ROE 27%** → book value *hiểu thấp* giá trị; sàn định giá đúng của PNJ là **bội số so lịch
sử chính nó** (ở đó nó rẻ 2,6 SD), không phải book hữu hình. ✓ trên leg này.

### Tín hiệu kỹ thuật + catalyst (§3 T2)
- **Giá**: đỉnh trước scandal 63.100 (02/07) → đáy tạm **40.900 (16/07)** = **−35% peak-to-trough** (từ
  đỉnh 120d ~64.100 ≈ −36%). Bật **+5,1% lên 43.000 (17/07)**. Close 43.000 **<< MA50 61.724 << MA200
  66.017** (rất sâu dưới cả 2 đường).
- **Volume cạn kiệt (đang hình thành)**: panic 25,6 triệu (08/07, ngày FPTS cắt margin) → 14,7 triệu
  (16/07) → **7,5 triệu (17/07)**, tiệm cận Volume_1M 4,7 triệu. Áp lực bán cưỡng bức đang giảm.
- **RSI hồi từ đáy**: D_RSI 0,148 (13/07) → **0,261 (17/07)** (thoát vùng quá bán sâu). **CMF −0,098
  (16/07) → −0,008 (17/07)** (áp lực bán ròng dịu về gần trung tính, chưa dương).
- **Đọc §3**: mới **1 phiên bật**, đáy 40.900 chưa được test lại → **higher-low CHƯA xác lập**. Ổn định
  giá đang CHỚM (volume dry-up + RSI/CMF hồi), **chưa đủ chuẩn "ổn định + higher-low + volume cạn kiệt"
  để chắc chắn T2**. Catalyst dương đầu tiên = **kế hoạch mua cổ phiếu quỹ** (đúng khung §3) — cần verify
  số lượng/giá trần (Winston/corp-action, không có trong BQ).

### Ước tính lợi nhuận kỳ vọng 12 tháng tại giá 43.000 (minh hoạ lượng hoá case AMBIGUOUS, KHÔNG phải khuyến nghị vào ngay)
Neo vào PE hiện tại 6,08x, giả định lõi bán lẻ vàng (phần lớn LN) không bị chạm:
- **Bull** (khủng hoảng chỉ là sốc uy tín 1–2 quý, Q3 xác nhận lõi intact, P-Lab được ring-fence, GIA
  không rút): re-rate 1 phần về PE ~12x (dưới TB 16x — thị trường giữ 1 phần discount rủi ro vĩnh viễn)
  → **~84.900 (+97%)**. Re-rate đầy đủ về 16x = +164% (dội lại 2015 +148%) nhưng để **thận trọng hơn**
  vì tính "gần lõi" lần này → dùng cận Bull ~+90–100%.
- **Base** (re-rate 1 phần về PE ~9–10x, thị trường áp discount uy tín có kéo dài nhưng hữu hạn):
  ~63.700–71.000 → **+48–65%**, trung tâm ~**+55%**.
- **Bear** (Q3/2026 lộ tổn hại lõi thật — tẩy chay mảng kim cương / GIA rút công nhận / biên co lại):
  PE giữ 6–7x hoặc EPS giảm → 38.000–45.000 → **−12% đến +5%**.
- **Kỳ vọng trung tâm nếu phải chọn 1 số: ~+40%/12m** — **cao hơn DGC (+25–35%)** vì fundamentals mới
  nhất của PNJ *chứng minh được* là mạnh (CF_OA>>NP, rev +78%, FSCORE 7) trong khi DGC quý gần nhất đã
  lộ CF_OA<<NP; nhưng **thấp hơn nhiều 2015 (+148%)** vì (a) scandal lần này GẦN LÕI hơn, (b) khoảng
  trống dữ liệu tới Q3/2026 dài, chưa có xác nhận post-crisis "lõi sạch" như PNJ/TV1 có tại điểm entry.

### Kết luận: PNJ = **AMBIGUOUS** (nghiêng constructive, mạnh hơn DGC nhưng bị chặn bởi wait dài)

| Tiêu chí | Phán quyết | Ghi chú |
|---|---|---|
| #1 cá nhân vs lõi | ⚠️ AMBIGUOUS | Gần lõi hơn 2015 (nội bộ + product-integrity), nhưng lõi vàng bán lẻ không chạm, P-Lab nhỏ. GIA + lan uy tín = ẩn số. |
| #2 NN backstop | pass mềm | Tư nhân — không phải điều kiện cứng (§6). |
| #3 CF_OA≥NP | ⚠️ PASS nhưng PRE-CRISIS | Q1/2026 CF_OA +3,56T >> NP +1,47T, nhưng trước khủng hoảng. Cổng thật = **Q3/2026 (~cuối 10/2026)**, so YoY. |
| #4 solvent | ✓ PASS | Debt_Eq 0,367. |
| #5 sàn định giá | ✓ PASS | 2,56 SD (PE) / 2,70 SD (PB) dưới lịch sử. |
| Kỹ thuật (T2) | chớm, chưa xác nhận | Volume cạn dần + RSI/CMF hồi + bounce +5%, nhưng higher-low chưa lập. |

**Lý do AMBIGUOUS (không QUALIFY, không NON):** không phải "lõi giả tưởng" (nên không NON), nhưng
**thiếu xác nhận post-crisis "lõi sạch"** mà PNJ-2015/TV1 có tại điểm entry — và cổng xác nhận đó (Q3/2026)
**xa ~3,5 tháng**. Định giá + fundamentals-pre-crisis ủng hộ luận điểm giá trị mạnh hơn DGC, nhưng
tiêu chí #1 gần lõi + khoảng trống dữ liệu dài = không đủ để nâng thẳng QUALIFY→T1/T2 full.

**Hàm ý sizing (§3):** nếu đội muốn mở vị thế special-sit, **T1 nhỏ (cận dưới cap 2–4% NAV)** có thể
biện minh (chiết khấu sâu 2,6 SD + fundamentals pre-crisis mạnh + volume cạn dần + catalyst buyback),
nhưng **KHÔNG T2/T3 full** cho tới khi qua cổng. Điểm khác PNJ-2015: đó là vào-được-ngay vì scandal
rõ-ràng-ngoài-lõi; lần này phải chờ chứng minh lõi không bị lây.

### Cổng xác nhận + catalyst trung gian đáng theo dõi (thứ tự thời gian)
1. **BCTC Q2/2026** (~cuối 07/2026) — KHÔNG phản ánh khủng hoảng (Apr–Jun), nhưng đọc **thuyết minh/
   guidance ban lãnh đạo về P-Lab** nếu có.
2. **Phản ứng GIA** (bất kỳ lúc nào) — nếu GIA rút công nhận/hợp tác P-Lab → tín hiệu tổn hại LÕI thật
   (nghiêng về NON). Watch-item hạng nhất.
3. **Tiến độ vụ án hình sự** — nếu mở rộng từ cá nhân cựu GĐ → pháp nhân PNJ / kê biên tài sản → HARD
   ABANDON (§3).
4. **Kết quả mua cổ phiếu quỹ** — thực thi = catalyst dương + đỡ giá (verify số lượng/giá trần: Winston).
5. **★ BCTC Q3/2026 (~cuối 10/2026) = CỔNG QUYẾT ĐỊNH** — quý đầu bao trọn khủng hoảng. **CF_OA so YoY
   vs Q3/2025 (+1,82T)** + Revenue YoY + thuyết minh mảng kim cương:
   - CF_OA giữ dương ~mức YoY + doanh thu lõi vàng không sụt → **nâng QUALIFY**.
   - CF_OA sụt bất thường so YoY / doanh thu kim cương bốc hơi / GIA đã rút → **chuyển NON**.

**Việc cần làm tiếp**: (a) nhờ Winston verify số lượng/giá trần cổ phiếu quỹ + theo dõi phản ứng GIA
(corp-action + tin quốc tế); (b) đặt reminder đọc BCTC Q3/2026 PNJ (~cuối 10/2026) — cổng quyết định.

### 7.5 Khuyến nghị timing — audit độc lập có nên đẩy cổng xác nhận sớm hơn Q3 không? (18/07/2026)
**KHÔNG, giữ nguyên cổng = BCTC Q3/2026.** Việc thuê 3 tổ chức quốc tế đúng là loại catalyst T2/T3
(§3) và VỀ NGUYÊN TẮC có thể ra kết quả trước Q3 (kiểm định sản phẩm thường nhanh hơn 1 quý tài
chính) — nhưng hiện quá non để nâng cổng: chưa chọn đơn vị (uy tín = ẩn số), không timeline, không
cam kết công bố công khai (có thể chỉ nội bộ → thị trường không quan sát được, không phải cổng xác
nhận thật). **Chỉ nâng audit thành cổng-sớm khi đủ CẢ 3 điều kiện**: (1) tên đơn vị uy tín quốc tế
thật (kiểu GIA/Bureau Veritas/SGS, không phải đơn vị vô danh), (2) timeline ra kết quả trước cuối
Q3/2026, (3) cam kết công bố công khai. Tới lúc đó có thể coi là T2 xác nhận sớm hơn BCTC Q3.

**Rủi ro timing cho người muốn vào**: nếu đợi tới đúng lúc BCTC Q3 công bố mới vào, có thể đã bỏ lỡ
phần lớn mức tái định giá — thị trường thường phản ứng trước với tin tức trung gian (chọn được đơn
vị kiểm định uy tín, audit sơ bộ rò rỉ tích cực) hơn là chờ đúng ngày báo cáo tài chính chính thức.
Đây là lý do §3 thiết kế 3 tranche thay vì 1 cổng duy nhất — case PNJ-2015 cho thấy phần lớn mức
tăng (+50%/6m) đến RẤT SỚM, trước khi có xác nhận đầy đủ.
