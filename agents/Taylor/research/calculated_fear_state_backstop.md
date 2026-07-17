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
