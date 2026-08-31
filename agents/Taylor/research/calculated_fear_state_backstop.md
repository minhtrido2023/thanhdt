# "Mua khi sợ hãi có tính toán" — State-Backstop Special-Situation Playbook

> Taylor (Quant/Algo), job `Taylor_20260717_122129`, 2026-07-17. **RESEARCH-ONLY — không wire production.**
> Case mẫu: **TV1 (PECC1)**. Đây là một *playbook special-situations có kỷ luật*, KHÔNG phải một book
> hệ thống hoá (N quá nhỏ). Mọi vị thế theo pattern này = manually-curated, cần user duyệt từng tên.

---

## 0. Luận điểm một câu

> **⚠️ ĐÍNH CHÍNH PHẠM VI 2026-07-23 (user, job `Taylor_20260723_121602`) — ĐỌC TRƯỚC TIÊN.**
> Khung này TRƯỚC ĐÂY bị scope HẸP SAI vào **scandal pháp lý cá nhân lãnh đạo** (mọi case §1/§6/§7 đều
> vậy). User đính chính nguyên văn: *"Chú ý vấn đề không phải là bị pháp lý. Vấn đề là bị đánh giá quá
> thấp so với giá trị thực. Nên pool sẽ có rất nhiều đặc biệt trong giai đoạn khủng hoảng. Ví dụ HPG
> 2022 tháng 11, giá về bằng book value. 1 năm sau tăng 90%. Kiểu như vậy bạn sẽ có nhiều case hơn hẳn
> thay vì bám vào pháp lý để tìm."* → **Scandal pháp lý chỉ là MỘT trong nhiều loại TRIGGER**, không
> phải điều kiện. Tiêu chí THẬT SỰ = §0.5 dưới đây. Đừng loại nhầm case như HPG chỉ vì "không có scandal".

**Tiêu chí cốt lõi (một câu):** khi một **giai đoạn khủng hoảng** (bất kể nguồn cơn) đẩy giá một doanh
nghiệp xuống **THẤP HƠN NHIỀU giá trị thực** của nó — trong khi khủng hoảng đó **sẽ QUA** (mang tính
chu kỳ/tạm thời/tâm lý) chứ không **PHÁ HỦY CẤU TRÚC** giá trị lõi — thì khoảng lệch giá đó có thể khai
thác. Điều KIỆN QUYẾT không phải "đã giảm sâu bao nhiêu" mà là **bộ tiêu chí phân biệt "khủng hoảng sẽ
qua" vs "giá trị đã hỏng vĩnh viễn"** (§0.5 + §2). Trường hợp scandal cá nhân (§2) là một *đặc tả* của
tiêu chí này cho nhóm trigger (a); các nhóm (b)/(c)/(d) có đặc tả tương đương ở §2.5.

---

## 0.5. Taxonomy trigger — 4 loại khủng hoảng có thể tạo case (mở rộng 2026-07-23)

Cùng MỘT tiêu chí cốt lõi ("giá << giá trị thực, khủng hoảng sẽ qua"), nhưng **nguồn cơn khủng hoảng**
đa dạng. Mỗi nhóm có một **câu hỏi phân biệt trung tâm khác nhau** (bản chất giống nhau: khủng hoảng
này là CHU KỲ/TẠM THỜI hay CẤU TRÚC/VĨNH VIỄN):

| Nhóm | Trigger | Câu hỏi phân biệt trung tâm | Case đã có |
|---|---|---|---|
| **(a)** | **Scandal/pháp lý cá nhân lãnh đạo** | Tài sản/hoạt động lõi có **TÁCH BIỆT** khỏi người bị điều tra & vẫn tạo tiền? (test CF_OA≥NP — §2) | PNJ✅ · VEA✅ · TV1✅ · DGC⚠️ · OGC❌ · FLC❌ |
| **(b)** | **Khủng hoảng ngành / chu kỳ hàng hoá** (giá đầu ra sập, tồn kho ứ, cầu đóng băng tạm thời) | Chu kỳ **SẼ QUAY LẠI** (cầu tạm giảm, không mất vĩnh viễn)? DN có **sống sót qua đáy** không (bảng cân đối) + có phải **DN dẫn đầu chi phí thấp**? (§2.5) | **HPG 2022** ✅ (case mới) |
| **(c)** | **Khủng hoảng vĩ mô / thị trường chung** kéo cả nhóm ngành xuống dưới giá trị (bán tháo hệ thống, margin call, thanh khoản) | Giá sập vì **KỸ THUẬT/tâm lý** (deleveraging, panic) hay vì **lõi kinh doanh xấu đi thật**? DN có bị **buộc bán tài sản/pha loãng** ở đáy không? | *(chưa có case verify)* |
| **(d)** | **Gián đoạn vận hành TẠM THỜI** không liên quan pháp lý (đứt gãy chuỗi cung, sự cố nhà máy, mất 1 hợp đồng lớn, thiên tai) | Gián đoạn có **thời hạn/khắc phục được** hay là **mất cấu trúc** (mất khách hàng vĩnh viễn, tài sản hỏng không sửa)? | *(chưa có case verify)* |

**Điểm chung tất cả 4 nhóm — cùng 1 discriminator gốc:** *"Cái gì đang bị định giá — nỗi sợ tạm thời,
hay sự phá hủy giá trị thật?"* Nhóm (a) hỏi qua lăng kính "scandal chạm lõi chưa"; nhóm (b)/(c)/(d) hỏi
qua lăng kính "chu kỳ vs cấu trúc". **Đây là cùng một câu hỏi mặc hai bộ áo khác nhau** — không phải hai
khung khác nhau.

**Hệ quả quan trọng cho việc TÌM case (user nhấn mạnh):** bám vào "scandal pháp lý" để tìm case là
scope quá hẹp → bỏ lỡ phần lớn cơ hội. Pool THẬT SỰ rộng hơn nhiều — mọi điểm cực trị định giá (giá ≈
book / PE nén sâu vs lịch sử) trùng với một khủng hoảng-sẽ-qua đều là ứng viên. **Cách tìm nhóm
(b)/(c)/(d): user tự phát hiện + đưa case tới** (xem §4-note: KHÔNG mở rộng scanner tự động — phạm vi
quá rộng, trùng public value screen). Nhiệm vụ của khung = **due-diligence ĐÚNG khi case tới**, không
phải quét tự động.

---

## 1. Bằng chứng lịch sử (đo trên BQ cache `ticker`, adjusted Close, trough→forward return)

> **Ghi chú phạm vi (2026-07-23):** bảng dưới toàn nhóm trigger **(a) scandal cá nhân** — vì khung ban
> đầu bị scope hẹp vào đó. Nhóm **(b) chu kỳ ngành** có case chuẩn **HPG 2022** với số liệu đầy đủ ở
> **§8** (tách riêng vì discriminator khác — chu kỳ vs cấu trúc, không phải scandal-chạm-lõi).

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

## 2. Bộ tiêu chí sàng lọc — nhóm (a) SCANDAL CÁ NHÂN — QUALIFY vs KHÔNG

> Đây là đặc tả cho **nhóm trigger (a)** (scandal/pháp lý cá nhân lãnh đạo). Nhóm (b)/(c)/(d) dùng **§2.5**.

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

## 2.5. Bộ tiêu chí sàng lọc — nhóm (b) CHU KỲ NGÀNH / (c) VĨ MÔ / (d) GIÁN ĐOẠN TẠM THỜI (thêm 2026-07-23)

Cho các trigger KHÔNG có scandal cá nhân. Test cốt lõi đổi từ *"scandal có tách khỏi lõi không"* sang
**"khủng hoảng này CHU KỲ (sẽ qua) hay CẤU TRÚC (không qua)"** — tương đương về mặt logic, khác về công cụ đo.

### ✅ ĐỦ ĐIỀU KIỆN (tất cả phải đúng)
1. **Khủng hoảng có tính CHU KỲ/TẠM THỜI, không CẤU TRÚC**: cầu *tạm* giảm (chu kỳ hàng hoá, siết tín
   dụng, panic vĩ mô, gián đoạn có thời hạn) — KHÔNG phải mất cầu vĩnh viễn / công nghệ lỗi thời / sản
   phẩm bị thay thế / mất giấy phép hoạt động. **Bằng chứng chu kỳ**: ngành từng có nhiều chu kỳ lên-
   xuống trong lịch sử và đã hồi phục; động lực cầu dài hạn còn nguyên (HPG: thép ↔ đầu tư công/BĐS,
   chu kỳ kinh điển; giá thép/HRC có đáy chu kỳ rõ).
2. **Sống sót qua đáy — bảng cân đối chịu được** (thay trụ "NN backstop" của nhóm a): net debt **quản
   lý được**, không bị **buộc bán tài sản / pha loãng cổ phiếu ở đáy** để tồn tại. Đây là điều kiện
   sinh-tử: chu kỳ sẽ qua CHỈ CÓ Ý NGHĨA nếu DN còn sống tới lúc đó. (HPG: nợ vay cao lúc đỉnh nhưng
   không mất khả năng thanh toán, không pha loãng — vượt qua đáy 2022 nguyên vẹn.)
3. **DN DẪN ĐẦU chi phí thấp trong ngành** (đòn bẩy vận hành đúng chiều khi chu kỳ quay lại): kẻ sống
   sót trong đợt thanh lọc, giành thị phần từ đối thủ yếu chết đi, và **bật mạnh nhất** khi biên hồi.
   (HPG: nhà sản xuất thép chi phí thấp nhất VN, lò cao tích hợp — khác hẳn tôn/thép thương mại biên mỏng.)
4. **Sàn định giá bằng TÀI SẢN THỰC (không phải lợi nhuận)**: đây là điểm mấu chốt khác nhóm (a). Ở đáy
   chu kỳ, **lợi nhuận SẬP/âm là BÌNH THƯỜNG** (đó chính là lý do giá rẻ) → **PE ở đáy chu kỳ vô dụng/
   gây hiểu lầm** (xem HPG §8: PE 3,9x lúc đáy rồi vọt lên 190x khi EPS sập — cùng lúc giá TĂNG gấp đôi).
   Sàn đúng = **PB ≲ 1 trên tài sản HỮU HÌNH thật** (nhà máy/thiết bị, không phải goodwill). Mua dưới
   giá trị thanh lý của tài sản vật chất mà chu kỳ không phá huỷ được. (HPG đáy: **PB 0,72** — dưới book 28%.)

### ❌ KHÔNG ĐỦ (bất kỳ điều nào → loại)
- **Khủng hoảng CẤU TRÚC, không phải chu kỳ**: cầu mất vĩnh viễn (công nghệ thay thế, đổi hành vi tiêu
  dùng không đảo ngược), sản phẩm/mô hình lỗi thời. Chu kỳ sẽ KHÔNG quay lại → không phải case này.
- **Bảng cân đối KHÔNG sống nổi qua đáy**: đòn bẩy quá cao, phải pha loãng/bán tài sản lõi để trả nợ ở
  đáy → dù chu kỳ hồi thì cổ đông cũ đã bị nghiền (equity wipeout / dilution). Book value "rẻ" trên
  giấy nhưng sẽ bị nợ ăn hết trước khi chu kỳ quay lại.
- **DN chi phí cao / biên mỏng / theo sau**: chết trong đợt thanh lọc hoặc không bật được khi chu kỳ hồi.
- **"Rẻ" chỉ vì tài sản ảo/goodwill/định giá lại đất chưa thực**: PB<1 trên tài sản không có giá trị
  thanh lý thật = bẫy giá trị, không phải sàn.
- **Đáy chu kỳ CHƯA tới / không xác định được** — bắt dao rơi giữa chu kỳ đi xuống mà chưa có dấu hiệu
  tạo đáy giá/đáy hàng hoá → rủi ro timing lớn. Ưu tiên bằng chứng đáy (§3: higher-low + volume cạn +
  giá đầu vào/đầu ra ngành chạm đáy) hơn là "đã rẻ so book".

**Ghi chú áp dụng chéo**: một case có thể thuộc NHIỀU nhóm cùng lúc (vd DGC — §6 — vừa có (a) scandal
cá nhân, vừa có yếu tố (b) đáy chu kỳ hoá chất/phốt pho + (d) gián đoạn mỏ 25). Khi đó chạy **cả** bộ
tiêu chí liên quan; case QUALIFY khi vượt discriminator của TỪNG nhóm mà nó thuộc về.

---

## 3. Khung entry/exit kỷ luật tổng quát (không riêng TV1)

**Sleeve riêng "special-situation", KHÔNG phải core book. Cap cứng mỗi tên 2–4% NAV** (tail-risk đình
chỉ giao dịch là thật). Không bao giờ size như một vị thế momentum/value thường.

### Entry — 3 tranche (không cố bắt đáy)
- **T1 (1/3)** khi đã QUALIFY §2 **và** DD>35% **và** giá ≤ book hữu hình. Chấp nhận còn dò đáy.
- **T2 (1/3)** khi có *ổn định giá* (higher-low + volume cạn kiệt) **hoặc** 1 catalyst dương đầu tiên.
  ⚠️ **Đây là KỶ LUẬT CHIA TRANCHE để hạ giá vốn trung bình, KHÔNG PHẢI tín hiệu làm tăng xác suất
  thắng.** Kiểm định trực tiếp (`postshock_base_formation_20260823.md`, job `Taylor_20260823_025658`,
  n=45 sự kiện RATING_OK độc lập, entry sau khi "ổn định giá" xác nhận): excess vs VNINDEX **ÂM** cả
  3 horizon (H60 −5,9% / H120 −8,8% / H250 −20,1%, CI dưới 0 cả 3), rủi ro rơi tiếp ≥−30% KHÔNG giảm
  so với vào ngay lúc sập (51,2% vs 48,8%, không có ý nghĩa thống kê). Cái quyết định thắng-thua vẫn
  là discriminator ĐỊNH TÍNH §2/§2.5 (khủng hoảng có chạm lõi kinh doanh hay không), không phải hình
  dạng giá/volume — đợi "ổn định giá" không mua được xác suất thắng cao hơn, chỉ mua được giá vốn
  bình quân thấp hơn nếu giá tiếp tục đi ngang/xuống.
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

### ⚠️ CẬP NHẬT 2026-07-23 (Mike) — Q2/2026 đã công bố (22/07), CỔNG XÁC NHẬN CHO KẾT QUẢ XẤU: DOWNGRADE khỏi AMBIGUOUS, gần nhóm NON

BQ (`ticker_financial`) tại 23/07 vẫn chỉ có tới 2026Q1 (chưa sync), nhưng DGC đã công bố công khai
KQKD Q2/2026 ngày 22/07 (báo chí, chưa xác nhận qua BQ):

| | Q2/2026 | So Q2/2025 |
|---|---|---|
| Doanh thu | 2.416,2 tỷ | **−16,55% YoY** |
| LN sau thuế | 440,77 tỷ | **−50,52% YoY** |
| GPM | 18,9% | Sụt từ 33,9% (gần một nửa) |

**Nguyên nhân công ty tự công bố — đây là bằng chứng quyết định**: **Mỏ 25 tạm ngừng khai thác để
phục vụ công tác điều tra** (đúng vụ án "khai thác Apatit trái phép" đang bị điều tra) → công ty phải
dùng hoàn toàn quặng nhập khẩu/mua ngoài, chi phí sản xuất phốt pho vàng tăng vọt. Cộng thêm giá đầu
vào (lưu huỳnh, điện, than cốc, amoniac) tăng.

**Áp đúng cổng đã đặt ra ở trên**: "CF_OA tiếp tục âm/doanh thu tiếp tục giảm → chuyển sang nhóm NON"
— **2 quý liên tiếp doanh thu giảm YoY** (Q1 −24,4%, Q2 −16,55%), không phải cú sốc 1 quý rồi qua như
kịch bản Bull kỳ vọng.

**Khác biệt về CHẤT so với đánh giá 17/07**: đây không còn là "thị trường sợ hãi trong khi hoạt động
vẫn bình thường" (điều kiện cốt lõi của QUALIFY §2 tiêu chí #3) — **chính tài sản lõi vật lý (mỏ khai
thác) bị dừng hoạt động vì phục vụ điều tra**, tức vụ án đang **trực tiếp phá vỡ vận hành sản xuất**,
không chỉ ảnh hưởng tâm lý/định giá. Đây là khác biệt nền tảng với TV1 (thủy điện Sông Bung 5 chưa một
ngày ngừng phát điện suốt vụ án) — DGC giờ gần với case NON (lõi bị chạm trực tiếp) hơn là QUALIFY.

**Kết luận cập nhật: hạ mức ưu tiên DGC trong watchlist "mua khi sợ hãi có tính toán".** Không loại
hẳn (biên lợi nhuận có thể phục hồi khi mỏ hoạt động trở lại + điều tra kết thúc), nhưng KHÔNG còn là
ứng viên tốt cho pattern này ở thời điểm hiện tại — cần chờ: (a) mỏ 25 hoạt động trở lại, (b) biên lợi
nhuận GPM hồi phục về vùng 30%+, (c) CF_OA chính thức qua BQ xác nhận xu hướng. Kịch bản Bull (+68%,
PE về PE_MA5Y) trong ước tính 17/07 coi như đã bị bác bỏ bởi dữ liệu thật; kịch bản Bear (đi ngang/
giảm thêm) đang là kịch bản có xác suất cao hơn.

### ⚠️⚠️ RE-DO 2026-07-23 (job `Taylor_20260723_112707`) — user phản biện MẠNH → ĐẢO NGƯỢC downgrade: DGC **KHÔNG phải gần-NON**, đúng hơn là **AMBIGUOUS-nghiêng-constructive** (asset-backed deep value, downside được bảo vệ mạnh)

User phản biện: *"DGC book value 4x, LN kế hoạch 1.600 tỷ, giá 37,9k vốn hoá 14.400 tỷ gần bằng tiền
mặt 13.000 tỷ. LN giảm 50% nhưng chưa lỗ bao giờ, năm nào dòng tiền cũng > lợi nhuận, 2026 chia 3k
cổ tức. Giá đó hơn gửi tiết kiệm rồi. Sao phải sợ."* — verify TỪNG claim bằng dữ liệu thật:

| Claim user | Verdict | Số thật (nguồn) |
|---|---|---|
| "book value 4x" | ✅ ĐÚNG (nghĩa: BVPS ~4× mệnh giá) | BVPS 41.696đ ≈ 4,17× par 10.000đ; **PB = 0,91x → giá DƯỚI sổ sách** |
| LN kế hoạch 2026 = 1.600 tỷ | ✅ CHÍNH XÁC | ĐHĐCĐ 22/07: DT 10.100 tỷ / **LNST 1.600 tỷ** (−10%/−50% vs 2025). ĐHCĐ 13/8 |
| Giá 37,9k, vốn hoá 14.400 tỷ | ✅ số học khớp (379,78M×37.900=14.394 tỷ) | ⚠️ **close 22/07 = 40.500** (sau KQKD) → ~15.380 tỷ; xác nhận giá LIVE khi thực thi |
| "gần bằng tiền mặt 13.000 tỷ" | ⚠️ MỘT PHẦN | Cash+tiền gửi 30/6 = **~10.922 tỷ** (−17% YTD; **đầu năm ~13.000 tỷ**, đã rút trả cổ tức). **EV thật = 14.394−10.922 = ~3.472 tỷ**, KHÔNG phải ~1.400 tỷ như user gộp — user overstate ~2.000 tỷ |
| "LN giảm 50% nhưng chưa lỗ bao giờ" | ✅ XÁC NHẬN | 48 quý (2014Q2→2026Q1), **min NP quý = +10,6 tỷ, ZERO quý lỗ**. −50% là kế hoạch/thực tế, vẫn lãi đậm |
| "năm nào dòng tiền cũng > lợi nhuận" | ⚠️ ĐA SỐ ĐÚNG (không tuyệt đối) | CF_OA>NP **9/12 năm đủ**; NGƯỢC ở 2017/2023/2025. CF_OA 3Y=7.939 tỷ, 5Y=16.496 tỷ (vẫn lớn) |
| "2026 chia 3k cổ tức" | ✅ + CÒN HƠN | 2026 plan cổ tức 30% = **3.000đ/cp (yield 7,9%)**; CỘNG **50% còn treo từ 2025 = 5.000đ/cp (yield 13,2%)** |
| "hơn gửi tiết kiệm, sao phải sợ" | ✅ ĐÚNG VỀ DOWNSIDE | Lãi tiền gửi ~707 tỷ/năm (6,5%×10.884 tỷ) ~44% LN kế hoạch; cash = **76% vốn hoá**; div yield >> gửi TK |

**★ PHÁT HIỆN MỚI QUYẾT ĐỊNH (§6 downgrade 17/07 KHÔNG có dữ liệu này): CF_OA quý 2/2026 ĐÃ BẬT
DƯƠNG lại ~+1.083 tỷ.** H1/2026 CF_OA = **−10 tỷ** (báo cáo), Q1 = **−1.093 tỷ** (BQ) ⇒ Q2 = −10−(−1.093)
= **+1.083 tỷ dương**. Tức cú CF_OA −1.093 tỷ ở Q1 (từng là lý do #1 hạ DGC gần-NON) phần LỚN là **một
lần** (331 tỷ khắc phục + timing vốn lưu động), KHÔNG phải lõi mất khả năng tạo tiền cấu trúc. Red-flag
lớn nhất của §6 **giảm mạnh** — dù mỏ dừng + LN nửa, lõi vẫn tạo được +1.083 tỷ tiền mặt trong Q2.

**§6 downgrade "gần NON" QUÁ NẶNG — 2 lỗi lập luận:**
1. **Chỉ có Q1 CF_OA khi viết** → coi −1.093 tỷ là dấu hiệu cấu trúc. Q2 dương lại bác điều đó.
2. **Lẫn "cú sốc BIÊN LỢI NHUẬN" với "lõi vô giá trị".** Mỏ 25 dừng = phải mua quặng nhập → GPM
   34%→19% = **vấn đề CHI PHÍ**, KHÔNG phải phá sản/gian lận-là-lõi (OGC/FLC/PVX → lỗ/huỷ niêm yết).
   DGC vẫn SẢN XUẤT, vẫn LÃI, vẫn tạo tiền. Khác CHẤT với nhóm NON.

**Thận trọng CÒN giá trị (không phải lệnh sạch):**
- Mỏ 25 **không có lộ trình mở lại** (mở/đóng theo tiến độ điều tra — vô định); GPM có thể kẹt ~19%
  nhiều quý. 2 quý liên tiếp doanh thu giảm YoY (Q1 −24%, Q2 −16,6%).
- Vụ án THẬT dính đúng tài sản lõi (khai thác Apatit trái phép) — khác TV1 (thuỷ điện chưa 1 ngày dừng).
- Tư nhân, không NN backstop (nhưng PNJ chứng minh không bắt buộc).
- "Rẻ" một phần ảo: ~44% LN kế hoạch chỉ là lãi tiền gửi, mảng hoá chất đang đáy thật.
- Cổ tức rút từ két (cash −17% YTD) → không giả định 10.900 tỷ đứng yên nếu tiếp tục chia ~3.000 tỷ/năm.

**KẾT LUẬN ĐẢO NGƯỢC (trung thực, không giữ lập trường cũ):** user **ĐÚNG phần lớn** trên trục
*bảo toàn vốn / margin-of-safety*. DGC nâng từ "hạ ưu tiên/gần-NON" → **AMBIGUOUS-nghiêng-constructive,
QUALIFIED YES cho vị thế NHỎ, kiên nhẫn, kiểu carry cổ tức + deep-value tài sản** (giống khung TV1
discretionary special-situation, ngoài book V2.4). Luận điểm = *"được trả ~8-13% cổ tức + downside kê
bởi ~10.900 tỷ tiền mặt (76% vốn hoá) + chưa lỗ 12 năm, trong khi optionality mỏ-mở-lại/biên-hồi-phục
là miễn phí"*. **KHÔNG** underwrite kịch bản re-rating +100% kiểu PNJ làm base (mỏ vô định lịch) — có
thể "dead money" vài quý. Size ≤0,5-1,0% NAV, chân trời 1-2 năm. **Cần user quyết định cuối** (Taylor/
Mike không tự đặt lệnh ngoài V2.4). Nguồn số: BQ cache `ticker_financial` (48 quý) + Vietstock/CafeF/
DNSE/TinNhanhCK KQKD Q2 & tài liệu ĐHĐCĐ 22/07/2026.

### ⚠️ CẬP NHẬT 2026-07-23 (quét tuần `Taylor_20260724_011001`) — VỤ ÁN MỞ RỘNG SANG BAN ĐIỀU HÀNH ĐANG TẠI CHỨC → DGC giảm SÀN, giảm nhẹ conviction của RE-DO

Ngày 22-23/07, Bộ Công an khởi tố THÊM **3 lãnh đạo DGC**: **TGĐ (CEO) Lưu Bách Đạt** + Thành viên
HĐQT **Nguyễn Quốc Trung** + Phó TGĐ **Phùng Trọng Tú** (cấm đi khỏi nơi cư trú). Cổ phiếu **giảm
SÀN 07-23** (−6,9%, close 37.700-37.950, thủng đáy 5 năm; vốn hoá ~14.300 tỷ, mất ~2/3 giá trị/1 năm).
anomaly_scan bắt DGC tier-H (VOLSPIKE+IDIOCRASH, idio −8,1% khi VNINDEX +1,8%). Nguồn: Vietstock/
VietnamBiz/CafeBiz/Dân Trí 22-23/07.

**Khác biệt về CHẤT so với vụ 17/03 (chỉ dính họ Đào Hữu Huyền — nhà sáng lập):** lần này chạm **ban
điều hành ĐANG TẠI CHỨC** (CEO + Phó TGĐ) ngay trước ĐHĐCĐ (13/08) → rủi ro **gián đoạn quản trị/vận
hành** + khoảng-trống-lãnh-đạo, đúng loại "vụ án di cư từ cá nhân sáng lập → pháp nhân/ban điều hành"
mà §3 liệt là tín hiệu cần theo dõi sát (chưa tới HARD ABANDON: chưa khởi tố pháp nhân, chưa kê biên).
Cộng dồn với mỏ 25 vẫn dừng (Q2 GPM 19%) → **2 trong 4 rủi ro-thật của RE-DO (mỏ vô định + vụ án chạm
lõi) đang NẶNG THÊM, không nhẹ đi.**

**Điều KHÔNG đổi:** luận điểm asset-backed deep-value của RE-DO (cash ~10.900 tỷ = 76% vốn hoá, chưa
lỗ 12 năm, CF_OA Q2 bật dương +1.083 tỷ, div yield ~8-13%) VẪN đứng — downside vẫn được kê bởi tiền
mặt + tài sản, và giá càng giảm sàn thì margin-of-safety trên trục carry-cổ-tức càng dày. **Điều đổi:**
optionality "re-rating khi vụ án kết thúc" bị đẩy XA hơn và bất định hơn (giờ phải chờ cả ổn định lại
ban điều hành, không chỉ mỏ mở lại). **Ròng: giữ nguyên khung QUALIFIED-YES vị thế NHỎ ≤0,5-1,0% NAV
kiểu carry+deep-value, nhưng KHÔNG vội bắt đáy sàn 07-23** — thêm 1 tín hiệu bất định lớn, ưu tiên chờ
ổn định giá (§3 T2: higher-low + volume cạn) + tín hiệu quản trị được kiện toàn trước khi cân nhắc T1.
**Vẫn cần user quyết định cuối.**

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

---

## 8. Case #4 — HPG 2022 (nhóm trigger (b) CHU KỲ NGÀNH), thêm 2026-07-23 (Taylor, job `Taylor_20260723_121602`)

**Case CHUẨN đầu tiên của nhóm (b)** — do user đưa ra để đính chính scope của khung (§0). KHÔNG có
scandal/pháp lý gì cả: đây thuần là **đáy chu kỳ thép + BĐS đóng băng 2022** đẩy nhà sản xuất thép đầu
ngành xuống DƯỚI giá trị sổ sách. Chứng minh discriminator "chu kỳ vs cấu trúc" (§2.5) hoạt động y hệt
discriminator "scandal-chạm-lõi" (§2).

### Bằng chứng số (BQ `ticker`, adjusted Close, verify job này)

| Mốc | Ngày | Close (adj) | PB | PE | Ghi chú |
|---|---|---|---|---|---|
| Đỉnh 2022H1 | 2022-03-07 | 26.120 | 2,52 | 6,63 | Đỉnh chu kỳ, PE thấp trên EPS đỉnh |
| **ĐÁY** | **2022-11-10** | **8.180** | **0,72** | 3,93 | **PB 0,72 = dưới book 28%**; BVPS 16.867 |
| +6m | 2023-05-10 | 14.660 | 1,31 | **190** | **+79%** từ đáy — EPS đã SẬP (PE vọt 190x) |
| +12m | 2023-11-10 | 17.900 | 1,54 | 82 | **+118,8%** từ đáy |
| +18m | 2024-05-10 | 20.570 | 1,68 | 19 | **+151,5%** từ đáy — EPS hồi (PE về 19x) |

- **DD đỉnh→đáy = −68,7%** (26.120 → 8.180).
- **Đính chính lời user (số thật TỐT HƠN trí nhớ):** user nhớ *"giá về bằng book value, 1 năm sau tăng
  90%"*. Thực tế: (a) giá về **DƯỚI book 28%** (PB 0,72), *rẻ hơn* "bằng book"; (b) +12m = **+118,8%**,
  *cao hơn* "+90%" user nhớ. Trí nhớ user conservative ở cả 2 chiều — luận điểm càng đứng vững hơn.

### ★ Bài học methodology QUAN TRỌNG NHẤT từ case này — tại sao PE vô dụng ở đáy chu kỳ

Nhìn cột PE: **đáy PB 0,72 / PE 3,93 → +6m giá +79% nhưng PE VỌT lên 190x**. Nghịch lý biểu kiến: giá
tăng gấp đôi trong khi PE tăng 48 lần. Giải thích: **EPS SẬP về gần 0** ở giữa chu kỳ (thép lỗ/hoà vốn
Q4/22–Q1/23) → mẫu số PE bốc hơi. Nếu ai dùng "PE thấp = rẻ" làm tín hiệu, họ sẽ **BÁN đúng đáy** (khi
PE nhảy lên 190x trông "đắt") — sai hoàn toàn.

→ **Xác nhận §2.5 tiêu chí #4:** ở nhóm (b), **sàn định giá phải neo vào TÀI SẢN (PB trên tài sản hữu
hình), KHÔNG neo vào lợi nhuận (PE)**. Lợi nhuận sập ở đáy chu kỳ LÀ lý do giá rẻ — không phải cảnh báo.
Recovery đến từ 2 nguồn cộng hưởng: (1) **PB normalize** 0,72→1,68 (thị trường trả lại giá trị tài sản
thực khi hết panic), (2) **EPS hồi** khi chu kỳ quay lại (PE 190→19). Đây là khác biệt CƠ CHẾ nền tảng
so với nhóm (a): case scandal có **PE thấp trên lợi nhuận THẬT còn nguyên** (lõi tạo tiền), recovery =
de-rate phần bù sợ hãi; case chu kỳ có **lợi nhuận đã sập**, recovery = tài sản + chu kỳ.

### Đọc HPG qua bộ tiêu chí §2.5 — QUALIFY sạch (hồi tố)

| Tiêu chí §2.5 | Phán quyết | Bằng chứng |
|---|---|---|
| #1 chu kỳ (không cấu trúc) | ✅ | Thép ↔ đầu tư công/BĐS, chu kỳ kinh điển; 2022 = giá HRC sập + BĐS đóng băng *tạm thời* (chính sách siết trái phiếu), cầu thép dài hạn nguyên |
| #2 sống sót qua đáy | ✅ | Nợ vay cao lúc đỉnh nhưng KHÔNG mất thanh khoản, KHÔNG pha loãng; qua đáy 2022 nguyên vẹn |
| #3 dẫn đầu chi phí thấp | ✅ | Nhà SX thép chi phí thấp nhất VN (lò cao tích hợp Dung Quất) — khác tôn/thép thương mại biên mỏng (HSG/NKG đã BANNED) |
| #4 sàn tài sản thực | ✅ | PB 0,72 trên nhà máy/thiết bị thật (không goodwill) — mua dưới giá trị thanh lý tài sản vật chất |

**Cảnh báo tự nhất quán:** HSG/NKG (tôn/thép thương mại) đang nằm trong **BANNED list** của đội (KB
"Cổ phiếu — quy tắc nhanh") — đúng logic §2.5 #3: chúng là DN biên mỏng/theo sau, KHÔNG phải kẻ dẫn đầu
chi phí thấp, nên **cùng đáy chu kỳ 2022 nhưng KHÔNG qualify** (chết/bật yếu hơn nhiều trong đợt thanh
lọc). HPG qualify không phải vì "thép rẻ" mà vì "kẻ DẪN ĐẦU chi phí thấp mua dưới book giữa đáy chu kỳ".
Đây là bằng chứng discriminator §2.5 phân biệt được trong CÙNG một ngành cùng một đáy.

### Hàm ý cho khung
- Case (b) **KHÔNG cần** test CF_OA≥NP kiểu (a) — ở đáy chu kỳ CF_OA/NP âm là bình thường. Thay bằng
  **survivability (bảng cân đối) + leader (chi phí thấp) + PB tài sản thực**.
- Recovery của (b) thường **CHẬM hơn cú nảy đầu của (a)** nhưng **BỀN và lớn** (+79/+119/+152% qua
  6/12/18m — leo đều theo chu kỳ, khác cú nảy giật của scandal). → Exit §3 nên **giữ runner lâu hơn**
  cho (b) (chốt theo PB normalize về ~1,5–2,0x + dấu hiệu đỉnh chu kỳ hàng hoá), không chốt sớm ở +30–40%.
- **N vẫn nhỏ** (1 case (b) verify đầy đủ) → vẫn là playbook, không phải edge thống kê. Giá trị = bộ lọc §2.5.

---

## 9. Ranh giới với BAL book / custom30V (value tilt hệ thống) — tránh trùng lặp vô nghĩa

Câu hỏi user (§3 của dispatch): sleeve "mua khi sợ hãi" khác gì cơ chế value đã có sẵn trong V2.4?

**Trả lời: khác về CONCENTRATION + TIMING + tính DISCRETIONARY, KHÔNG khác về triết lý.** Cả hai đều
là "mua rẻ so giá trị" — nhưng ở hai chế độ vận hành khác nhau, KHÔNG chồng lấn:

| Chiều | BAL / custom30V (value tilt hệ thống, LIVE V2.4) | Sleeve "mua khi sợ hãi có tính toán" (playbook này) |
|---|---|---|
| **Cơ chế** | Quy tắc CỨNG, tự động: rank 1/PE+1/PCF (BAL) / ey (custom30V), rebalance định kỳ | DISCRETIONARY, thủ công: due-diligence từng case §2/§2.5, user duyệt từng tên |
| **Diện** | Rải rộng, LIÊN TỤC trên toàn universe (30 tên custom30V, cap 0,10) | CHỌN LỌC, thưa, chỉ tại **điểm cực trị định giá + khủng hoảng cụ thể** |
| **Sizing** | Tỷ trọng nhỏ đều tay (~3,3%/tên custom30V, theo rank) | **Tập trung lớn hơn CÓ CHỦ ĐÍCH: 2–4%/tên** (cap cứng §3), vào 3 tranche |
| **Timing** | Luôn-bật (always-on), không định thời khủng hoảng | **Định thời**: chỉ khi DD sâu + tạo đáy + qua cổng discriminator |
| **Universe** | Chỉ mã LỌT rating gate ≤3 + golden floor (ROE_Min3Y≥0, CF_OA_3Y>0) | **CÓ THỂ gồm mã golden-floor loại tạm** (đáy chu kỳ EPS/CF âm → HPG/DGC sẽ RỚT custom30V) — đây chính là lý do cần sleeve riêng |

**Điểm mấu chốt — tại sao KHÔNG trùng lặp:** cơ chế value hệ thống (custom30V/BAL) **theo định nghĩa sẽ
LOẠI** đúng các case này ở đáy khủng hoảng — vì golden floor (CF_OA_3Y>0, ROE_Min3Y≥0) và rank ey/PE
đều bị bóp méo khi lợi nhuận/dòng tiền sập tạm thời (HPG đáy 2022: EPS gần 0, CF_OA âm → rớt mọi filter
hệ thống). Sleeve "mua khi sợ hãi" **bắt đúng cái mà hệ thống buộc phải bỏ**: mã tốt-về-tài-sản-lõi
nhưng xấu-tạm-thời-về-số-hiện-tại. → Bổ sung, không chồng lấn: hệ thống bắt "rẻ + số đẹp bền", sleeve
bắt "rẻ + số xấu TẠM THỜI có lý do sẽ qua". Đây là lý do sleeve phải **NGOÀI book V2.4, discretionary,
cap riêng** (như TV1/DGC đã làm) — nhét vào custom30V sẽ vừa vi phạm golden floor vừa mất tính chọn-lọc.

**Kết luận ranh giới:** giữ 2 cơ chế TÁCH BIỆT. custom30V = value-tilt always-on trong book. Sleeve fear-
buy = special-situation discretionary ngoài book, kích hoạt tại giao điểm (định-giá-cực-trị × khủng-hoảng-
sẽ-qua), user duyệt từng tên. Không systematize sleeve vào V2.4 (N nhỏ + discretionary theo bản chất).

---

## 9. Case #5 — DGC 3/2020 (nhóm (b) chu kỳ, COVID) + SYSTEMATIC SCREEN N-lớn (Taylor, job `Taylor_20260723_123927`, 2026-07-23)

**Bước ngoặt phương pháp:** thay vì thêm 1 case tay nữa (bẫy chọn-case-đã-biết-kết-quả), quét CÓ HỆ
THỐNG toàn lịch sử VN 2008–2026 → N=237 episode độc lập thay N=2. Chi tiết đầy đủ + script tái lập:
**`fearbuy_systematic_screen_20260723.md`**. Tóm tắt:

**DGC 3/2020 verify:** đáy 2020-03-31 PB **0.73** (dưới book 27%), PE 4.4, LN quý +168 tỷ, CF_OA +197
tỷ (lõi tạo tiền nguyên). 24m sau = **+16,3× adjusted** (user nhớ "10×" là conservative). ★ Tách cơ chế:
16,3× = PE 3,7× (**de-rate = value thật, lặp lại được**) × EPS 4,4× (**siêu chu kỳ photpho 2021-22 =
trúng chu kỳ, KHÔNG đếm ex-ante**). → entry PB 0.73 đủ đảm bảo de-rate 3–5×; đuôi 16× là may super-cycle.

**FEARBUY v1 — bộ tiêu chí định lượng rút ra:** (mkt_dd VNINDEX<−30% so đỉnh 1y) ∧ (PB<0.7) ∧ (NP_P0>0
∧ CF_OA_P0>0) ∧ (ROE_Min3Y≥0), trong `universe_pit` point-in-time.
- **Median excess 12m vs VNINDEX = +37.8%, winrate 77%; excess 24m +45.3%.** Tail sạch: 0.8% mất >50%/24m.
- **8/8 năm-khủng-hoảng median DƯƠNG, sign-test p=0.0039** (N_eff thật = 8 regime, KHÔNG phải 237 —
  độ tin nằm ở "dương mọi crisis", không ở con số điểm).

**3 phát hiện đính chính trực giác:**
1. **Value-trap ở TẦNG THỊ TRƯỜNG (2010):** gate −20% dd bắn suốt bear cấu-trúc 2010–12 → mua rẻ nhưng
   giá tiếp tục rơi (median −27%, wr 15%). Fix = yêu cầu panic **SÂU −30%** (phân biệt crash cấp tính
   mean-revert vs grind cấu trúc) → xoá sạch bẫy 2010. **Discriminator "khủng hoảng sẽ qua" cần cả
   chiều THỊ TRƯỜNG, không chỉ chiều doanh nghiệp.**
2. **Golden floor ROE_Min3Y≥0 KHÔNG tăng mean, nhưng cắt blow-up từ 6.5% → 1%** — đúng vai trò tail-guard.
3. **Commodity KHÔNG phải động lực:** non-commodity median +47.5% > commodity +12.5%. DGC/HPG là đuôi nổi
   bật nhưng subset median-thấp + phụ thuộc chu kỳ. **Edge lõi = deep-value-trong-panic DIỆN RỘNG, không
   cần siêu chu kỳ hàng hoá** (salience bias: user nhớ commodity 10-bagger, screen cho thấy value phi-HH
   đáng tin hơn).

**Ranh giới không đổi:** screen = CANDIDATE GENERATOR; PVX 2011 qua rule vẫn mất 57% → discriminator
§2/§2.5 vẫn là HARD GATE thủ công + user duyệt từng tên. Sleeve special-situation ≤0.5–1.0% NAV/tên,
NGOÀI book V2.4. Đề xuất nâng cấp `fearbuy_weekly_scan.sh` chạy FEARBUY v1 định lượng (gate −30% tự
bật/tắt: 2026 hiện chưa −30% → screen "ngủ", crash sâu tự kích hoạt) — **chờ user duyệt, chưa wire.**

---

## 9.5. Mở rộng mẫu nhóm (b) — 14 case, 6 ngành: **discriminator KHÔNG phân biệt được ở 12M** (Taylor, job `Taylor_20260822_022947`, 2026-08-22)

**Kết quả đầy đủ + số liệu: `cycle_fear_backtest_20260822.md`. PREREG commit `4e36d170` TRƯỚC mọi truy
vấn outcome (`cycle_fear_prereg_20260822.md`). Verdict: NO-GO. KHÔNG wire, KHÔNG đổi §2.5.**

Mục đích: §8 chỉ có **1** case (b) verify (HPG 2022). Job này mở ra **14 case × 6 ngành** (thép, chứng
khoán, BĐS, chăn nuôi, phân bón, hoá chất), có **3 negative control chỉ định trước** (HSG/NKG = không
phải leader chi phí thấp; NVL = nghi cấu trúc).

| Giả thuyết | Ngưỡng | Đo được | |
|---|---|---|---|
| H1 median BHAR_12M > 0, N ≥ 5 | >0, N≥5 | **+108,3pp**, N=14 | ✅ đạt |
| H2 median(PASS) − median(FAIL) ≥ +20pp @12M | ≥+20pp | **−17,0pp** | ❌ **bác bỏ** |

### ★ Ba bài học ghi vào khung (KHÔNG đổi tiêu chí §2.5 — N_eff ≈ 2 cú sốc độc lập, sửa là overfit)

1. **Chân trời đánh giá nhóm (b) phải là 24M, KHÔNG phải 12M.** Ở 12M **mọi thứ rơi sâu đều nảy** —
   tiêu chí #2 (sống sót) có gap ≈ 0 (+104,9 vs +108,3pp). Ở 24M gap bung ra **−82,8pp** (nhóm nghi
   ngờ +34,5 vs nhóm ổn +117,3). **12M quá ngắn để thiệt hại cấu trúc kịp cắn.** Bổ sung, không mâu
   thuẫn, với ghi chú §8 ("recovery của (b) chậm hơn nhưng bền").
2. **Tiêu chí #3 (leader chi phí thấp) ANTI-phân biệt ở 12M.** Cùng ngành cùng đáy: HSG **+178,1pp**
   và NKG **+166,8pp** (biên mỏng, DD −80%/−82%) **ĐÁNH BẠI HPG +102,5pp** (leader, DD −71%). §8 viết
   "HSG/NKG cùng đáy nhưng bật yếu hơn nhiều" — **số liệu bác bỏ câu đó ở chân trời 12M**. Cơ chế:
   **độ nảy đi theo độ RƠI, không theo CHẤT LƯỢNG**. Đừng dùng #3 để kỳ vọng "leader nảy mạnh hơn";
   giữ nó như bộ lọc rủi ro dài hạn thì được.
3. **#2 (sống sót qua đáy) là tiêu chí duy nhất làm việc — và làm việc theo kiểu PHÒNG THỦ.** NVL,
   case chỉ định trước là structural, là mã **DUY NHẤT âm ở 24M** (−22,0pp; neo thực tế T20 **−43,1pp**).
   Giá trị của discriminator = **tránh thảm hoạ**, không phải chọn người thắng — đúng vai trò
   "golden floor cắt blow-up" ở §9 phát hiện #2.

**Cảnh báo đọc số:** median +108,3pp là **neo tại đáy ex-post**; neo thực tế trough+20 phiên còn
**+52,6pp**. VNINDEX từ chính đáy đó đã +23,1%/12M. Và kết quả này **đá với screen N-lớn §9**
(non-commodity +47,5% > commodity +12,5%, N=237 episode, 8 regime) ⟹ **khi hai bên đá nhau, tin §9**;
đọc job này là bằng chứng cho "2022Q4 là một đáy tốt", KHÔNG phải "nhóm chu kỳ có edge".

### Nhóm (c) vĩ mô — 1 case phản chứng đáng giá hơn cả 3 case thuận

Mua **chỉ số** trong panic vĩ mô hiệu quả (VNINDEX từ đáy COVID 2020-03-24: **+76,2%**/12M; từ đáy
2022-11-15: **+23,1%**). Nhưng **chọn mã vẫn cần discriminator**: cùng đáy COVID, FPT **+49,1pp** và
MWG **+43,5pp** BHAR_12M, còn **VNM −28,3pp @12M và −106,7pp @24M** — large-cap "rẻ", cùng panic,
nhưng **lõi đang xấu đi thật**. Đây là minh hoạ sạch nhất cho câu hỏi trung tâm của nhóm (c): *giá sập
vì KỸ THUẬT hay vì lõi xấu đi thật*.
⚠️ **Đính chính mô tả thường gặp**: đáy 2022 rơi vào **Q4/2022** (siết trái phiếu + margin call),
KHÔNG phải Q1/2022 (Nga-Ukraine) — Q1/2022 là vùng **ĐỈNH** của VN-Index.

### Nhóm (d) gián đoạn vận hành — vẫn CHƯA có case

5 ứng viên tìm được (RAL cháy nhà máy 08/2019; MSH/TNG/VHC/FMC đóng cửa "3 tại chỗ" Q3/2021) đều có
DD chỉ **−14,6% đến −28,9%**, trong khi nhóm (b) có DD **−43% đến −90%**. **Thị trường chưa bao giờ
định giá đây là khủng hoảng** ⟹ không có nỗi sợ nào để mua. BHAR dương của chúng là lợi suất của DN
tốt trong thị trường tăng, **không phải bằng chứng cho khung này**. Ô "case đã có" của nhóm (d) trong
bảng §0.5 **giữ nguyên trống**.

---

## 10. Checklist phân tích SÂU cho case KHÔNG có gate thị trường — khi không có −30% VNINDEX làm bộ lọc thô, phân tích phải GÁNH HẾT việc phân biệt hàng tốt vs hàng lởm
> Thêm 2026-07-23 (job `Taylor_20260723_130951`, user chỉ đạo). Trích xuất TRỰC TIẾP từ due-diligence
> đã làm rất kỹ với TV1 (SOTP) và DGC (CF one-time vs cấu trúc). Đây là **công cụ ĐỊNH TÍNH, SÂU,
> per-case** — khác hẳn FEARBUY v1 (định lượng, auto-weekly). Ranh giới 2 công cụ ở §10.9.

**Bối cảnh kích hoạt:** nhóm trigger **(a) scandal cá nhân** và **(d) gián đoạn tạm thời** — TV1/DGC/PNJ
đều rẻ (PB≈book, PE nén) NHƯNG **VNINDEX KHÔNG sập −30%** đi kèm. FEARBUY v1 (gate thị trường −30%)
CHỦ ĐÍCH không bắt nhóm này → khi user/Mike tự đưa 1 case loại "rẻ mà thị trường không sập", chạy
checklist dưới. **Mỗi bước BẮT BUỘC, ghi rõ PASS/FAIL/AMBIGUOUS + số liệu**, không mô tả chung chung.

### 10.1. Phân tầng rủi ro: PHÁP NHÂN vs CÁ NHÂN (bước phân biệt #1, quyết định nhất)
- Người/sự kiện bị điều tra có **tách rời khỏi tài sản tạo tiền** không? Hỏi cụ thể: hợp đồng/giấy
  phép/nhà máy có **tiếp tục vận hành** trong lúc điều tra không (đo bằng sản lượng/doanh thu mảng lõi
  theo quý, KHÔNG bằng lời trấn an)?
- **TEST PHÂN BIỆT THẬT (bài học TV1 vs DGC):** vụ án dính vào **hoạt động ngoại vi/cá nhân** (TV1: tư
  vấn đấu thầu EVNNPT — thuỷ điện Sông Bung 5 **chưa 1 ngày dừng phát điện**) = QUALIFY-được; vụ án dính
  **chính tài sản lõi vật lý** (DGC: mỏ apatit 25 bị dừng — nguồn nguyên liệu lõi) = gần NON. Viết ra
  1 câu: "tài sản tạo ≥X% lợi nhuận có bị chạm trực tiếp không?"
- FAIL ngay nếu: lõi kinh doanh CHÍNH là cái bị điều tra (OGC/FLC — "lõi giả tưởng").

### 10.2. SOTP — tách & định giá ĐỘC LẬP tài sản lõi (bài học TV1, bước bỏ sót ở DD lần 1)
- **Liệt kê tài sản theo mảng**, định giá TỪNG mảng độc lập, gán **tư vấn/mảng-dính-án = 0** (thận
  trọng): TV1 = hydro Sông Bung 5 (57MW) đáy-DCF + tư vấn=0 → equity ~883 tỷ = 33.100đ/cp (+66%).
- **Kiểm tra NỢ của tài sản lõi** (đừng định giá gộp): SB5 nợ dự án đã trả gần hết (257 tỷ→0,4 tỷ) →
  equity value ≈ enterprise value. Bỏ sót nợ = sai to theo cả 2 chiều.
- **NEO bằng comp M&A THẬT, không bằng multiple sách vở**: thuỷ điện Nậm Nơn 32 tỷ/MW → SB5 ~1.824 tỷ;
  đấu giá SB5 2018 1.390–1.688 tỷ (gồm nợ, nay hết nợ). Comp giao dịch thật > multiple lý thuyết.

### 10.3. Chất lượng lợi nhuận: CF_OA vs NP — one-time hay CẤU TRÚC (bài học DGC)
- CF_OA quý-scandal âm trong khi NP dương = **cờ đỏ accrual/lõi**. NHƯNG **phân tách one-time vs cấu
  trúc TRƯỚC khi kết luận**: DGC Q1 CF_OA −1.093 tỷ **phần lớn one-time** (331 tỷ khắc phục + timing vốn
  lưu động) → Q2 bật dương +1.083 tỷ. 1 quý CF âm ≠ mất khả năng tạo tiền.
- **Đọc TTM/nhiều-năm, KHÔNG 1 điểm** (bài học PVX §10.10): dùng cumulative 3Y CF_OA/NP + đếm % quý
  CF_OA>0, so **base-rate NGÀNH** (đừng so 50% chung — Q1 mùa vụ ~49% DN CF_OA âm là bình thường).
- **Ngoại lệ cần biết (nếu KHÔNG sẽ false-negative):** equity-method (VEA: LN là cổ tức JV, CF_OA cấu
  trúc < NP — tiền ở dòng đầu tư) và ôm-tồn-kho (PNJ: vốn kẹt tồn kho vàng) → CF_OA<NP KHÔNG phải red-
  flag. → nhóm (a) cash-cow/holding: đọc thêm **cổ tức nhận + CF gồm đầu tư**, đừng chỉ CF_OA.

### 10.4. Bất thường bảng cân đối theo MẢNG: AR/DSO, tồn kho, phải-thu-dở-dang
- **DSO/khoản phải thu tăng đột biến** so lịch sử & so peer = LN đang được "ghi nhận" chứ chưa thu tiền
  (đặc biệt POC/xây lắp — WIP receivable phình). Đo DSO_P0 vs DSO_P4 và vs trung vị ngành.
- Tồn kho/dở dang phình nhanh hơn doanh thu = ứ đọng/ghi nhận sớm. Chia theo mảng nếu DN đa ngành.
- Nợ vay ngắn hạn tăng để đắp vốn lưu động (không phải đầu tư) = dấu hiệu căng thanh khoản.

### 10.5. Solvency — SỐNG SÓT qua khủng hoảng (điều kiện tiên quyết, không có = vô nghĩa mọi định giá)
- **Đòn bẩy phải đọc THEO NGÀNH bằng khung 8L, KHÔNG dùng sàn Debt_Eq chung** (sửa 2026-07-23, job
  `Taylor_20260723_134350` — xem §10.11). `Debt_Eq_P0` là **tổng-nợ-phải-trả/vốn** (gồm tiền khách trả
  trước, phải trả người bán, tiền gửi ngân hàng) → phồng giả cho ngân hàng/BĐS/xây lắp. Dùng **`real_lev`
  = STLTDebt_Eq_P0 (nợ VAY có lãi/vốn)** và ngưỡng theo route: NH/CK/BH bỏ qua (đòn bẩy = vận hành); BĐS
  nới (real_lev≤2,5); hàng hoá/xi măng chu kỳ chặt (≤1,5); xây lắp/CN thường (COMPOUNDER, ≤3). Xu hướng
  vẫn quan trọng (PVX tổng-nợ 3,7→9,1 = đi tới vỡ nợ). CR/QuickR, lịch đáo hạn nợ vs tiền mặt.
- Câu hỏi sinh tử: "DN có bị BUỘC bán tài sản / pha loãng cổ đông ở đáy không?" Nếu có → không phải
  value opportunity, là bẫy giá trị.

### 10.6. Sàn định giá & downside (không chỉ upside)
- PB neo **tài sản THỰC** (đất/nhà máy/thuỷ điện định giá lại), không neo PE (EPS đáy vô nghĩa).
- **Cổ tức làm sàn carry** (bài học DGC/VEA): DGC yield tổng ~21% (30% tiền mặt 2026 + 50% treo 2025),
  VEA ~50%+/năm → trả tiền để CHỜ re-rating, hạ downside. Kiểm tra lịch sử chi trả (Dividend_Min3Y).
- Book value vs giá: PB<1 dưới sổ = biên an toàn; nhưng phải qua §10.4 (book có thật không, AR ảo?).

### 10.7. Catalyst & timing — có LỘ TRÌNH đóng gap không (đừng mua dead-money vô hạn)
- Liệt kê catalyst THẬT có thời hạn: kết quả điều tra, kiểm toán ra BCTC, mở lại tài sản dừng, bán tài
  sản. Phân biệt catalyst **còn giá trị** vs **đã vô hiệu** (TV1 lần 1: cổ tức 15% + bỏ phiếu kiểm toán
  đều mất giá trị thực khi Big4 từ chối FY2026).
- **Không lộ trình rõ = dead-money vài quý → size NHỎ hơn + chân trời DÀI hơn** (DGC mỏ 25 chưa có
  lộ trình mở lại → ≤0,5–1,0% NAV, 1–2 năm).

### 10.8. Đính chính chéo — đừng đánh đồng 2 việc khác nhau (bài học TV1 lần 1)
- FY đã kiểm toán vs FY tương lai: TV1 lần 1 SAI khi đánh đồng "A&C kiểm toán sạch FY2025" với "Big4
  từ chối FY2026" — 2 việc khác nhau. Luôn ghi rõ **năm tài chính** của mỗi rủi ro.
- User overstate/understate số (DGC: cash thật ~10.922 tỷ không phải 13.000; EV ~3.472 tỷ không phải
  ~1.400) — **verify từng con số bằng BQ**, giữ luận điểm nếu vẫn đứng vững sau khi sửa số.

### 10.9. ⚠️ RANH GIỚI: FEARBUY v1 (định lượng, auto) vs Checklist §10 (định tính, sâu) — 2 CÔNG CỤ KHÁC NHAU
| | **FEARBUY v1** (§9 Case#5 + `fearbuy_systematic_screen`) | **Checklist §10** (mục này) |
|---|---|---|
| **Loại** | Định lượng, quét TỰ ĐỘNG | Định tính, due-diligence per-case |
| **Kích hoạt** | Auto weekly (`fearbuy_weekly_scan.sh`), **gate thị trường −30%** | Khi user/Mike tự đưa 1 case cụ thể |
| **Tình huống** | Thị trường **SẬP SÂU** (crash diện rộng) → dò rộng ứng viên PB<0.7 | **"Rẻ nhưng thị trường KHÔNG sập"** (scandal cá nhân/gián đoạn — TV1/DGC/PNJ) |
| **Đầu ra** | Danh sách ứng viên (candidate generator) | Kết luận QUALIFY/AMBIGUOUS/NON + size + entry/exit |
| **Quan hệ** | Screen ra → mọi tên vẫn PHẢI qua §2/§2.5 + §10 + user duyệt | Là HARD GATE thủ công cho từng tên |

**KHÔNG thay thế nhau.** FEARBUY v1 gate −30% cố tình "ngủ" khi thị trường chưa sập → nhóm (a)/(d)
"rẻ-mà-thị-trường-không-sập" lọt lưới screen tự động là ĐÚNG THIẾT KẾ; §10 gánh đúng nhóm đó. Ngược
lại khi thị trường crash sâu, FEARBUY v1 thu hẹp vũ trụ, rồi §10 (+§2/§2.5) chạy trên từng tên lọt ra.

### 10.10. Red-flag PVX — POC/xây lắp biên mỏng + CF_OA âm đa-kỳ + đòn bẩy tăng = LN sổ sách hư cấu
> Verify job `Taylor_20260723_130951`, chi tiết `research/pvx_2011_ruleverify_20260723.md`.
- **PVX (Xây lắp Dầu khí, ICB 2357)**: NPM 3,1%, kế toán **percentage-of-completion** → TTM CF_OA/NP
  **không bao giờ ≥1** khi NP dương (3Y cumulative −0,31), Debt_Eq 3,7→9,1 → **insolvency**. Lọt FEARBUY
  v1 chỉ vì `CF_OA_P0>0` **1 quý** lumpy (2011Q3) ngay trước sập. r24 −57%→−70%.
- **Red-flag bắt buộc kiểm khi case thuộc ngành POC/xây lắp/EPC (ICB 23xx)**: (biên NPM mỏng <5%) ∧
  (CF_OA âm/lag NP **nhiều năm** — §10.3 TTM) ∧ (Debt_Eq tăng dần) → **LN sổ sách là hư cấu kế toán, DN
  đang đi tới vỡ nợ, LOẠI** dù PB<1. (TV1 ICB **2791** consulting, KHÔNG thuộc 23xx → red-flag này không
  áp; TV1 chết/sống theo §10.1–10.2, không theo red-flag ngành.)
- **⚠️ ĐÃ HỦY đề xuất `Debt_Eq_P0 ≤ 2,5`** (job `Taylor_20260723_134350`, user chỉ đạo): sàn chung dùng
  tổng-nợ-phải-trả, KHÔNG so sánh được giữa ngành → công cụ đúng là **8L rating (route-aware) đã có sẵn**.
  Xem §10.11 để biết vì sao và dùng thế nào.

### 10.11. Đòn bẩy đọc THEO NGÀNH bằng 8L — KHÔNG dựng sàn Debt_Eq chung (verify job `Taylor_20260723_134350`)
> User chỉ đạo (2026-07-23): "vấn đề đòn bẩy đã dùng lens từng nhóm ngành để xử lý, không thể dùng
> chung. Cập nhật lại kiến thức 8L từ đó dễ phân biệt case tốt/xấu hơn thay vì chọn tràn lan."
> Artifact: `research/fearbuy_screen/analyze_8l_rating.py` (+ `analyze_8l_lev.py`).

**8L ĐÃ xử lý đòn bẩy theo ngành ở 2 tầng (đọc code `rating_8l.py`):**
1. **Metric đúng — `real_lev()` = STLTDebt_Eq_P0 (nợ VAY có lãi/vốn), KHÔNG phải Debt_Eq_P0.** Debt_Eq_P0
   là tổng-nợ-phải-trả/vốn → đếm cả tiền khách trả trước + phải trả người bán + tiền gửi (với NH) là "nợ",
   thổi phồng đòn bẩy cho BĐS/khu-CN/NH.
2. **Ngưỡng theo route** (router BANK/POWER/CYCLICAL/COMPOUNDER + INSURANCE/SECURITIES/REALESTATE):
   NH(8355)/BH(853x-857x)/CK(877x) **bỏ qua đòn bẩy** (là vốn vận hành); BĐS(8633) **nới** (real_lev≤0,5→+2,
   ≤1,5→+1); hàng hoá/đường/xi măng **chặt** (real_lev>1,5 → rating 5 "trough-fragile"); xây lắp/CN thường
   (COMPOUNDER) real_lev>3 → red-flag rating 5.

**Bài test user (PVX xấu vs LPB/HDG/SCI tốt), 8L rating point-in-time (universe_pit), tính từ BQ:**

| Mã | Ngày | Route | Debt_Eq (tổng-nợ) | real_lev (nợ vay) | 8L rating | Sàn chung ≤2,5 | 8L ≤3 | Kết cục r24 |
|---|---|---|---|---|---|---|---|---|
| **PVX** | 2011-12 | COMPOUNDER | **3,7** | **1,52** | **4** | ❌ loại | ❌ **LOẠI** ✓ | −57% |
| SCI | 2020-03 | COMPOUNDER | 4,18 | 2,11 | 3 | ❌ loại (SAI) | ✓ giữ | +723% |
| HDG | 2020-03 | REALESTATE | 3,23 | 1,77 | 3 | ❌ loại (SAI) | ✓ giữ | +566% |
| LPB | 2020-03 | BANK | 15,06 | 0,0 | 2 | ❌ loại (SAI) | ✓ giữ | +297% |

**3 kết luận (thay hẳn "đòn bẩy là lever sạch nhất" ở §10.10 cũ):**

1. **Sàn chung `Debt_Eq_P0≤2,5` loại CẢ 4** (PVX + 3 winner). Nó "bắt" được PVX chỉ do **tổng-nợ tình cờ
   đã cao** (3,7) tại đáy, nhưng bắn nhầm luôn NH (LPB 15x = tiền gửi), BĐS (HDG = tiền khách trả trước),
   xây lắp (SCI = phải trả người bán). Đây đúng là "chọn tràn lan" user nói.

2. **Đòn bẩy — làm ĐÚNG (real_lev route-aware) — gần như VÔ DỤNG làm cổng.** Quét toàn panel 276 episode:
   cổng real_lev route-aware chỉ loại **4/276** (không mã nào có r24). Vì đa số mã tổng-nợ cao lại có nợ
   VAY vừa phải. **PVX real_lev 1,52 còn THẤP HƠN SCI 2,11 và HDG 1,77** → không có ngưỡng đòn bẩy nào tách
   được PVX khỏi winner. ⇒ "edge" của sàn chung cũ chỉ là **ảo giác từ dùng sai metric** (tổng-nợ). Đòn
   bẩy KHÔNG phải discriminator.

3. **Công cụ đúng = 8L QUALITY rating (đã có sẵn, route-aware).** Nó loại PVX (rating 4) nhờ **CHẤT LƯỢNG**
   — ROIC3Y 0,051 (yếu, 0 điểm) + FSCORE 3 + chuyển đổi tiền mặt gãy (POC accounting) — KHÔNG phải đòn bẩy;
   và giữ SCI(ROIC 0,113)/HDG(ROIC 0,152, ROE mạnh)/LPB(NH, chấm theo ROE). Đây chính là trục sector-
   comparable. Panel realized-only (n=63): kept-set của **8L≤3 median r24 +22,5%** > no-gate +16,4% > sàn
   chung +17,1%; 8L≤3 loại 8 thảm hoạ (<−30%) vs sàn chung chỉ 2.

**Cách dùng cho FEARBUY v1 (User CHỐT 2026-07-23 — đồng ý đề xuất, dùng chính thức từ đây):**
- **BỎ mọi sàn Debt_Eq chung.** Thay vào: gắn **8L rating point-in-time** (qua máy `custom_basket.rating_asof`
  đã có) vào mỗi ứng viên screen. **rating≥4 = cờ CHẤT-LƯỢNG-CẢNH-BÁO** đẩy vào due-diligence §10 thủ công.
- KHÔNG nên biến 8L≤3 thành cổng auto CỨNG cho sleeve này: fear-buy **cố tình** muốn một số survivor bị
  đánh sập (có thể rating 3-4) — 8L≤3 loại 46% ứng viên (128/276) là bộ lọc chất lượng thật, hợp cho
  BAL/custom30V hơn là cho sleeve deep-value discretionary. Đúng vai: 8L rating là **INPUT sector-aware
  cho §10**, không phải bộ lọc im lặng.
- Caveat trung thực: (a) chỉ 63/276 episode đã có r24 24 tháng (còn lại quá mới) → so sánh realized mỏng;
  (b) 8L rating PIT ở đây là bản **rút gọn** (thiếu moat notch / bank-AQ lens / eq_flag structural / forensic)
  — bản đầy đủ `rating_8l.py` có thể lệch chút nhưng lõi phân biệt (ROIC/FSCORE/route) giữ nguyên.

---

## §11. Blend systematic fear-buy vào V2.4 — nghiên cứu blend (job `Taylor_20260723_163630`, 2026-07-23)

Chi tiết đầy đủ: **`fearbuy_blend_v24_20260723.md`**. Tóm tắt cho backstop:

**User mandate:** blend fear-buy vào V2.4 ưu tiên cao, blue-chip, giữ ≥18m, ngưỡng mua ADAPTIVE theo
market drawdown (càng xấu càng phải rẻ). Đã thiết kế đủ + backtest blend đầy đủ trên NAV ngày.

**Kết quả:**
- **Adaptive threshold** `PB_max(s)=clip(1.0−2.0·(s−0.20),0.40,1.0)`, s=−mkt_dd — CHẠY ĐÚNG ý thiết
  kế; + **blue-chip ADV≥20B → win-rate 77%, median ex24 +41%, sign-test 5/5 crisis p=0.031**. Screen tốt.
- ⚠️ "blue-chip" theo ADV = **cyclical/financial/BĐS high-beta** (SHB/KBC/HSG/HHV/STB…), KHÔNG phải
  compounder phòng thủ — quality defensive hiếm khi về PB<0.7.
- **Blend vào V2.4 KHÔNG "hiệu quả hẳn lên":** swap-model dCAGR **+0.05-0.08pp** (MaxDD xấu đi);
  cash-aware cận-trên **+1.7pp @w10%** nhưng **+2.96pp toàn bộ từ OOS 2020+**, IS chỉ +0.39pp; w≥15%
  MaxDD sập. **Root cause: V2.4 ĐÃ bắt hồi-phục-khủng-hoảng (CAPIT+LAG re-risk+parking); trong cửa sổ
  sleeve active, sleeve +26.9% < V2.4 +29.9% ann → trùng lặp (redundant).**
- **Verdict: KHÔNG blend ưu tiên cao / KHÔNG reserve NAV riêng.** Chỉ overlay cơ hội ≤5-10% NAV rót từ
  tiền-mặt-đáy khi DT5G∈{CRISIS,BEAR}; kỳ vọng trung thực +0.5-1.5pp (kịch bản thuận), Calmar neutral.
- **Phân biệt quan trọng:** market-wide fear (adaptive theo VNINDEX) = trùng V2.4. **Idiosyncratic-
  scandal fear (TV1/DGC/PNJ — thị trường ổn, 1 tên sập) = chỗ V2.4 KHÔNG với tới = giá trị fear-buy
  thật**, giữ nguyên khung discretionary §1-§10 (≤1% NAV/tên, due-diligence, user duyệt).
- Cần `verify_finding.sh` (quant-skeptic) TRƯỚC nếu user chọn overlay nhỏ — chưa làm trong job này.

---

## §12. Holding-period + Sizing RULE cho sleeve idiosyncratic (job `Taylor_20260723_170729`, 2026-07-24)

> Trả lời 2 câu user: **"giữ bao lâu"** + **"đầu tư bao nhiêu"** — thay heuristic tròn số cũ (18m,
> 2-4%/tên) bằng quy tắc CÓ CĂN CỨ DỮ LIỆU. Panel MỚI = **idiosyncratic** (1 mã sập ≥40% từ đỉnh-1-năm
> của CHÍNH NÓ **trong khi VNINDEX vẫn ≥−15% đỉnh** = thị trường ổn), quality-floor (NP_P0>0 ∧
> CF_OA_P0>0 ∧ ROE_Min3Y≥0), in `universe_pit` PIT. **N=1209 episode, 2007–2026.** KHÔNG dùng lại panel
> market-wide (đã chứng minh trùng V2.4 ở §11). Artefacts: `fearbuy_idio/screen_idio.sql` +
> `analyze_*.py` (tái lập). **RESEARCH-ONLY — tài liệu tham khảo khi user duyệt case, KHÔNG wire.**

### ⚠️ Phát hiện #1 (quan trọng nhất, phản trực giác) — screen CƠ HỌC idiosyncratic KHÔNG có edge
Khác hẳn market-wide crash (bán tháo bừa → quality bị vứt rẻ → mua quality thắng, §systematic screen
median ex12 **+38%**), một mã sập 40% **khi thị trường vẫn ổn** thì trung bình là **thị trường định giá
ĐÚNG một vấn đề riêng của doanh nghiệp** → phần lớn là **value-trap**:

| Mốc giữ | N | median return | median **excess** vs VNINDEX | win-rate |
|---|---|---|---|---|
| 3m | 1154 | +2.7% | +2.6% | 55% |
| 6m | 1119 | −3.5% | −4.8% | 44% |
| 12m | 1094 | −1.5% | **−7.2%** | 43% |
| 18m | 1037 | −5.8% | **−11.8%** | 41% |
| 24m | 991 | −3.3% | **−14.4%** | 43% |
| 36m | 934 | +7.3% | −8.9% | 45% |

**Median excess ÂM ở mọi mốc 6–36m, win-rate <50%.** Mean dương (+16–18% ex24m) nhưng chỉ vì **đuôi
phải béo** (vài siêu-winner DGC-2019 +721%, FIT-2019 +192% — trúng chu kỳ về sau). **Bộ lọc CƠ HỌC
(rẻ PB / đòn bẩy thấp / biên cao / thanh khoản) KHÔNG cứu được** — thậm chí combo "QUALIFY-ish"
(PB<1 ∧ DE≤2.5 ∧ NPM≥5% ∧ ADV≥5B) làm median ex24 **TỆ hơn −28%, win 30%**. → **Xác nhận tuyệt đối
luận điểm §10: sleeve idiosyncratic là trò DUE-DILIGENCE ĐỊNH TÍNH, không có screen cơ học thay được.**
(PNJ-2015 & VEA-2019 — 2 winner sạch — thậm chí KHÔNG lọt screen −40% cơ học: cú sập của chúng nông
hơn/UPCoM. Winner sạch không nằm ở đuôi drawdown sâu nhất.)

### ⚡ Phát hiện #2 — Câu trả lời "giữ bao lâu" = CATALYST-CONFIRM, KHÔNG phải lịch cố định
Đây là kết quả mạnh nhất & khả thi vận hành nhất. Test proxy catalyst: **sau khi vào, vị thế có hồi
(r6m>0 hoặc r9m>0) không** = thị trường bắt đầu re-rate khi lõi chứng minh còn nguyên:

| Nhánh | N | median r24 | median **ex24** | **win-rate 24m** | mean r24 |
|---|---|---|---|---|---|
| TẤT CẢ (giữ mù theo lịch) | 991 | −3% | −14% | 43% | +33% |
| **Xác nhận trong 6m (r6m>0) → GIỮ** | 426 | +36% | **+19%** | **62%** | +84% |
| KHÔNG xác nhận 6m → **BỎ** | 565 | −27% | −29% | 28% | −6% |
| Xác nhận trong 9m (r9m>0) | 425 | +45% | **+24%** | **65%** | +94% |

**Tách biệt KHỔNG LỒ (62% vs 28% win-rate) & BỀN: confirmed-6m thắng not-confirmed ở 13/14 năm**
(chỉ 2020 hoà vì mọi thứ hồi, 2024 chưa đủ 24m forward). → **Giữ MÙ theo lịch 18/24m thua trên
median** (nhánh không-xác-nhận là bẫy −29%). **Quy tắc đúng: vào thăm dò → ĐÒI xác nhận trong 6–9m
(giá ổn/hồi + BCTC sau khủng hoảng chứng minh lõi tạo tiền lại) → nếu XÁC NHẬN thì giữ DÀI, nếu
KHÔNG thì THOÁT.** Không phải "giữ đủ 18 tháng rồi xét".
> Caveat trung thực: r6m>0 có phần là **momentum/survivorship** ("thứ đã lên hay lên tiếp"), không phải
> 100% catalyst cơ bản — nhưng nó CAUSAL (chỉ dùng thông tin tới mốc 6m), khả thi, trùng khớp thời điểm
> BCTC-xác-nhận (~2 quý), và tách biệt lớn+bền → bài học vận hành thật: **sleeve phải được QUẢN LÝ có
> cổng tái-đánh-giá 6–9m, không mua-rồi-quên.**

**Một khi ĐÃ xác nhận → giữ bao lâu:** winner nhả lời CHẬM & MUỘN (median winner r = 8%/32%/45%/68%/73%
tại 6/9... 12/18/24/36m). Risk-adjusted (r/|maxDD-trong-kỳ|) chỉ **dương ở 36m** (âm ở 12/24m); maxDD
từ điểm vào **sâu: median −28% @12m, −39% @24m** (bạn SẼ ngồi qua thêm một cú giảm). → **Sau xác nhận,
chân trời tối ưu 24–36m**, chấp nhận dao động sâu; đừng chốt non ở 12m.

### 💰 Phát hiện #3 — "Đầu tư bao nhiêu": Kelly ⇒ size THEO ĐỘ BẢO VỆ DOWNSIDE, không phải số phẳng
1. **Kelly trên panel cơ học = ảo giác đuôi-béo.** f*≈0.44 nhưng do vài siêu-winner kéo mean; N_eff nhỏ
   (số crisis/tên độc lập, không phải 991), median bet LỖ → **loại, Kelly không robust với đuôi phải +
   sai số ước lượng mean.** KHÔNG dùng.
2. **Kelly có-điều-kiện-DD là lưỡi dao quanh break-even.** Với loser NON blended **−70%**:
   break-even p* = 70/(W+70). Winner khiêm tốn VEA-like +22% → cần p>76% (gần như hoàn hảo); blended
   +80% → p>47%; PNJ-tail +249% → chỉ cần p>22%. **Base-rate cơ học win ~43–48% ⇒ bet NGÂY THƠ
   (không DD) ≈ hoà tới âm.** Chỉ DD đẩy p qua break-even mới có EV — mà p **không chứng minh được**
   (N=2 winner sạch).
3. **Point-estimate quarter-Kelly** (p=0.50, W=+100%, L=−70%) ≈ **5% NAV/tên** — NHƯNG sập về **0** ở
   kịch bản bi quan (p=0.45, W=+80%). Vì p bất khả chứng + tồn tại đuôi **−100% (FLC)**, phải hạ **sâu
   dưới** point-Kelly (~1/10-Kelly) → về đúng vùng "**phí bảo hiểm chịu được**".
4. **★ UPGRADE THẬT (thay "2-4%" cũ): size do LOSER-payoff = độ bảo vệ downside chi phối — đúng thứ DD
   đo được:**

   | Loại case | Downside thật (loser) | Kelly cho phép | **SIZE đề xuất/tên** |
   |---|---|---|---|
   | **Fear thuần / cược re-rating** (không sàn tài sản, đuôi −70/−100%) | −70% | ~0 trừ khi p≥0.55–0.65 | **0.5% NAV** |
   | **Asset-backed / SOTP** (sàn tài sản vật lý, downside −20/−30%) | −25% | ≥1.0 dễ dàng | **1.0–1.5% NAV** (ràng buộc = **thanh khoản**, không phải Kelly) |

   → "2-4%/tên" cũ **quá cao** (không phân biệt độ bảo vệ, vượt cả quarter-Kelly cho fear thuần).
   "0.5-1.0%" cũ ĐÚNG cho fear thuần, nới tới **1.5%** CHỈ khi tài sản vật lý chặn đáy (giảm loser
   payoff → Kelly bung ra).

### 🧢 Phát hiện #4 — Trần TỔNG sleeve
- **Tần suất cơ hội THẬT hiếm:** panel cơ học ~64 case/năm nhưng phần lớn là trap/cyclical (median LỖ).
  Case **QUALIFY-grade thật** (scandal tách-lõi, lõi còn tạo tiền — PNJ'15/VEA'19/DGC'20/TV1'26…) ≈
  **0.7–1.5/năm, thường 0**, dồn cụm khi có sóng khởi tố (2026: TV1+DGC+PNJ+JVC cùng lúc).
- **Tương quan giữa case idiosyncratic THẤP** (mỗi case 1 công ty/lý do riêng; độ phân tán ex24 trong
  cùng năm rất lớn, std 50–240%) → giữ **3 tên đồng thời = đa dạng hoá THẬT** (không giả vờ).
- **Worst-case chịu được:** 3 tên × 1% = **3% NAV gross**; toàn bộ hoá NON −70% = **−2.1pp NAV**; thảm
  hoạ toàn bộ FLC −100% = **−3.0pp**. Chấp nhận như phí bảo hiểm đã biết.
- **→ Trần: tổng sleeve ≤ 3% NAV, tối đa 3 tên đồng thời** (khớp con số cũ nhưng nay NEO vào tần suất
  + worst-case, không phải tròn số). Sóng crackdown lớn có thể nới 4 tên NHỎ (0.5–0.75%) vẫn ≤3% tổng.

### ✅ Phát hiện #5 — Áp lên TV1 (đang có)
TV1 nằm trong panel (stock_dd **−49.5%**, mkt_dd **−13.5%** = đúng idiosyncratic, PB 0.98). Size đã
duyệt **0.5–1.0% NAV (do THANH KHOẢN ADV~1 tỷ/ngày)** — vì TV1 là **asset-backed SOTP** (Sông Bung 5
chặn đáy, loser ~−25%), Kelly cho phép **≥1.0–1.5%** → **thanh khoản binding TRƯỚC Kelly, KHÔNG mâu
thuẫn.** Nếu bỏ ràng buộc thanh khoản, "đúng ra" TV1 ~1.0–1.5%; trần 1.0% hiện tại là **hợp lý & thận
trọng**. Cổng catalyst-confirm §12#2 áp cho TV1: theo dõi xác nhận giá/SOTP-catalyst trong 6–9m, không
giữ mù chờ đủ 2 năm.

### 📌 Tóm tắt quy tắc (thay heuristic cũ)
1. **Holding = catalyst-conditional, KHÔNG lịch:** vào thăm dò → đòi xác nhận (giá hồi + BCTC lõi tạo
   tiền lại) trong **6–9m** → xác nhận thì giữ **24–36m** (winner nhả lời muộn), không thì **THOÁT**
   (nhánh không-xác-nhận là bẫy −29%). Giữ mù 18/24m thua trên median.
2. **Sizing theo độ-bảo-vệ-downside:** fear thuần **0.5%**/tên; asset-backed/SOTP **1.0–1.5%**/tên.
   "2-4%" cũ quá cao; số neo vào Kelly có-điều-kiện + đuôi −100% + p bất khả chứng.
3. **Trần sleeve ≤3% NAV, ≤3 tên** đồng thời (tần suất ~1/năm, tương quan thấp, worst-case −2 tới −3pp).
4. **Vẫn CHỈ mua case qua due-diligence §2/§10 + user duyệt.** Screen cơ học idiosyncratic **KHÔNG** có
   edge (median LỖ) → tuyệt đối không auto-buy; DD định tính gánh 100% việc phân biệt.

---

## §13. Nhật ký QUÉT TUẦN (mandate user 2026-07-23) — mỗi tuần 1 mục, kể cả tuần sạch

> Quy tắc quiet-heartbeat: tuần không có case mới VẪN ghi 1 dòng (phân biệt "đã quét, sạch" với
> "pipeline chết"). Chỉ case đủ dữ liệu mới nâng thành mục §6/§7 riêng.

### 2026-07-31 (job `Taylor_20260731_011001`) — 0 QUALIFY mới · 1 case mới AMBIGUOUS (TV4) · 2 read-through cho case cũ

**Phần 1 — anomaly_scan** (`anomaly_scan.py`, phiên 2026-07-30, universe 245 mã = 23 holding + 236
watchlist rating≤2; cache BQ refresh 30/07 23:55).
Cờ MỚI trong 7 phiên (24/07→30/07): **chỉ 1** — VRE `CEIL2` 30/07 (+6,8%, tăng trần 2 phiên) → tín
hiệu TĂNG, không thuộc phạm vi fear-buy.
Cụm 27/07 (**CSV, CTS, MBS, VND, SHS** cùng sàn −6,5…−7,0% trong phiên VNINDEX chỉ −1,0%) = **flush
beta ngành chứng khoán**, KHÔNG phải sự kiện riêng lẻ: không có tin khởi tố/pháp lý nào, cả 5 mã hồi
lại trong 3 phiên (VND 15.350→17.050, CTS 20.000→21.600, MBS 17.400→18.400, SHS 14.300→15.600, CSV
20.000→21.250). Đọc theo §2.5: KHÔNG có sàn tài sản hữu hình (PB 1,12–2,05, không mã nào ≲1), CF_OA
âm là cấu trúc của CTCK (cho vay margin) chứ không phải tín hiệu chất lượng → **NON**.
Riêng **CSV** (Hoá chất Cơ bản Miền Nam) là tên chất lượng nhất cụm — PE 8,8 · PB 1,31 · ROE5Y 18,3% ·
Debt_Eq 0,29 · FSCORE 6 — nhưng nhịp giảm 23.800→20.000 (−16%/8 phiên) là **trôi theo chu kỳ hoá chất
+ lây từ DGC**, không có sự kiện khủng hoảng rời rạc, và PB 1,31 > sàn §2.5 → **WATCH, chưa QUALIFY**.
Ngưỡng falsify: PB về ≲1,0 kèm bằng chứng đáy giá phốt-pho → xét lại theo §2.5.

**Phần 2 — WebSearch tin khởi tố/bắt giữ 7–14 ngày** (bù điểm mù của scan giá/KL). 2 tin mới:

| Mã | Sự kiện | Phản ứng giá | Kết luận |
|---|---|---|---|
| **PAT** (Phốt pho Apatit VN, DGC chi phối) | CT HĐQT **Lưu Bách Đạt** khởi tố 22/07, tội **gây ô nhiễm môi trường** (cùng người, cùng vụ với DGC) | **KHÔNG có** — 21/07: 63.000 → 22/07: 63.000 → 23/07: 62.800; cả tuần −3% | **KHÔNG phải case fear-buy**: (a) thị trường không định giá nỗi sợ nào để mua rẻ; (b) tội danh môi trường/khai thác tài nguyên **chạm lõi** (rủi ro giấy phép mỏ) — sai chiều tiêu chí §2#1; (c) PB 2,13 → không có sàn tài sản. Bổ nhiệm CT mới 28/07 (6 ngày). |
| **TV4** (PECC4) | 11/06 khởi tố+tạm giam **CT Lê Cao Quyền, TGĐ, Phó TGĐ VÀ Kế toán trưởng** (đại án ngành điện: 47 bị can / 5 tội danh gồm **vi phạm kế toán**, tham ô, hối lộ). 24/07 miễn nhiệm toàn bộ 4 người, ĐHĐCĐ bất thường tháng 8 kiện toàn | Sập −25% hồi 06, nay **đi ngang 12.800–13.000 hai tuần** (+3% từ đáy) | **AMBIGUOUS — xem dưới** |

**Phần 3 — TV4: case mới đáng ghi (anh em của TV1, trước nay chỉ là 1 dòng base-rate ở §1)**

Số tại 30/07 (BQ cache, Q2/2026 đã công bố 21/07): giá 13.000 · **PB 0,98** (BVPS 13.269) · PE 5,85 vs
PE_MA5Y 8,37 · **DY 7,8%** · ROE_Trailing 15,8% · ROE_Min3Y 11,7% · **Debt_Eq 0,56 · CR 1,72 · tiền
59,5 tỷ / tổng TS 410 tỷ** · CF_OA_P0 10,75 tỷ vs NP_P0 3,60 tỷ (**≈3× NP** ✓) · CF_OA_3Y lật từ
−24,8 tỷ (2025) sang **+67,3 tỷ**.

Chấm theo §2: #2 backstop *(EVN-family — **⚠️ tỷ lệ sở hữu NN chưa verify, phải xác nhận trước nếu
theo đuổi**)*; #3 CF_OA≥NP ✓ (Q2 3×, nhưng Q4/25 thì 17,2 vs 32,3 ✗ — mùa vụ Q4 nặng, hồ sơ yếu hơn
TV1 rõ); #4 solvent ✓ **mạnh** (nợ thấp nhất họ TV, CR 1,72, tiền 15% tổng TS); #5 sàn định giá ✓
(PB 0,98, PE 5,85 < PE_MA5Y).
**Điểm CHẶN — khác TV1 về CHẤT:** vụ án bắt **cả Kế toán trưởng** với tội danh **vi phạm quy định về
kế toán** → đánh thẳng vào tính toàn vẹn của chính BCTC vừa dùng để định giá. Đây đúng gạch đầu dòng
❌ của §2 ("cáo buộc gian lận BCTC làm *toàn bộ* con số vô giá trị"). TV1 chỉ bị ở tầng Chủ tịch (rủi
ro tương đương của TV1 đến từ đường khác: 4 Big4 từ chối kiểm toán).
Hai chặn phụ: (a) **thanh khoản ~6.260 cp/phiên ≈ 81 triệu VND/ngày** — chỉ bằng ~1/7 TV1, ràng buộc
thanh khoản binding trước Kelly (§12#5) rất sớm; (b) **không còn dislocation để mua** — giá đã đi ngang
2 tuần, nhịp sợ hãi xảy ra từ tháng 6.

→ **TV4 = AMBIGUOUS (không nâng lên QUALIFY).** **Cổng xác nhận nhị phân: ý kiến kiểm toán BCTC bán
niên soát xét 2026 (hạn ~30/08)** — ý kiến chấp nhận toàn phần sau khi Kế toán trưởng bị bắt sẽ gỡ
đúng tiêu chí #1; ý kiến ngoại trừ / từ chối / chậm nộp = **NON**, đóng case. Cổng phụ: kết quả ĐHĐCĐ
bất thường tháng 8 (ban lãnh đạo mới) + verify tỷ lệ sở hữu EVN.

**Phần 4 — read-through cho case đang theo dõi (không làm lại từ đầu)**
- **DGC** (§6, AMBIGUOUS-nghiêng-constructive): dữ liệu Q2 của **PAT** — công ty con phốt-pho — về
  ngày 22/07 và **xác nhận từ phía dưới** luận điểm dòng tiền của RE-DO: FSCORE 2→7, **PCF lật từ
  −27,2 sang +4,0** (CF_OA dương trở lại), Debt_Eq 0,44→0,36, DY 15,8%, ROE5Y 72%, ROIC5Y 52,5%. Giá
  DGC cũng đã hồi 36.000 (27/07) → **39.050 (30/07)**, tức đáy sàn 23-27/07 giữ được. Không đổi khung
  QUALIFIED-YES vị thế NHỎ ≤0,5–1,0% NAV; chưa có tín hiệu §3-T2 đủ (higher-low mới 1 tuần).
- **TV1** (§4): **không có tin mới**. Giá 19.400–20.000 (đi ngang, đáy 19.400 ngày 28/07). Hai cổng
  vẫn nguyên: lấy ý kiến chọn đơn vị kiểm toán **10/08**, ngày ĐKCC cổ tức 15% chưa công bố.
  **Catalyst-confirm gián tiếp mới, có lợi:** **TV2 công bố LNST Q2/2026 ~49 tỷ (+750% YoY) và tăng
  trần 29/07** (23.700→25.350, KL 307k ≈ 2–3× bình thường) — bằng chứng sống rằng một CTCP tư vấn điện
  có lãnh đạo bị khởi tố vẫn công bố được KQKD bình thường và thị trường **re-rate ngay**. ⚠️ Chất
  lượng lợi nhuận có ngoại lệ: phần lớn mức tăng đến từ **doanh thu tài chính (lãi tiền gửi/cho vay:
  2,8 tỷ → 44 tỷ)**, không phải lõi tư vấn → đọc là tín hiệu *thị trường sẵn sàng tha thứ*, KHÔNG phải
  bằng chứng lõi khoẻ.
- **PNJ** (§7, AMBIGUOUS): không có tin mới. Giá ổn định 32.500–32.900 sau đáy 30.750 (24/07) — đã
  ngừng rơi 4 phiên. Cổng xác nhận vẫn là **BCTC Q3/2026 (~cuối 10/2026)**. ⚠️ Nhắc: cờ
  `anomaly_flags.json` của PNJ có **TTL 30 ngày** (last_alert 24/07 → hết hạn ~23/08), tức gate loại
  PNJ khỏi rổ CAPIT sẽ **tự mở** trước cổng xác nhận thật — cần quyết định gia hạn trước 23/08.

**Tổng kết tuần**: 245 mã quét cơ học + 5 truy vấn tin tức · **0 QUALIFY mới** · 1 AMBIGUOUS mới (TV4,
cổng 30/08) · 1 WATCH (CSV) · 5 NON (cụm CTCK 27/07) · 1 loại thẳng (PAT — không có nỗi sợ để mua).

### 2026-08-07 (job `Taylor_20260807_011001`) — 0 QUALIFY mới · 0 case mới đáng nâng · 4 read-through · 1 khuyết tật cơ chế phát hiện được

**Phần 1 — anomaly_scan** (`anomaly_scan.py`, cache BQ refresh 06/08 23:45, phiên cuối **2026-08-06**,
universe 252 mã = 23 holding + 243 watchlist rating≤2; chạy `--backfill-days 9 --no-flags`).
Cờ trong 9 phiên (29/07→06/08): **4**, trong đó **chỉ 1 cờ GIẢM mới**:

| Mã | Ngày | Cờ | ret | idio | Đọc |
|---|---|---|---|---|---|
| **DNA** | 04/08 | FLOOR2 | −14,2% | −15,0% | **MỚI** — xem Phần 1b |
| PNJ | 04/08 + 05/08 | CEIL2 | +6,9% ×2 | +6,1/+7,0% | TĂNG — read-through §7, Phần 4 |
| VRE | 30/07 | CEIL2 | +6,8% | +4,5% | TĂNG — đã ghi tuần trước |

**Phần 1b — DNA (Điện Nước An Giang, POWACO — UPCoM): KHÔNG phải case fear-buy.** Ba lý do độc lập:
(a) **không có sự kiện khủng hoảng** — WebSearch không ra tin pháp lý/khởi tố/sự cố nào; (b) **doanh
nghiệp đang khoẻ**, không có nỗi sợ để mua: Q2/2026 NP 68,6 tỷ (Q1 32,9 · Q2/25 50,0), doanh thu 841
tỷ, **CF_OA_P0 +83,2 tỷ > NP** ✓, CF_OA_3Y +759 tỷ, ROE_Trailing 19,3% · ROE_Min3Y 15,3% · FSCORE 7 ·
Debt_Eq 1,01 · CR 1,18 · DY 8,6% — hồ sơ chất lượng, không phải hàng sập; (c) **thanh khoản không thể
giao dịch**: KL bình thường **100–5.100 cp/phiên** (≈2–100 triệu VND/ngày), riêng phiên 04/08 có 81.000
cp (1,4 tỷ) — chính khối lệnh đó tạo ra cú −14,2% trong sổ mỏng. Giá đã bật lại 17.500 → **20.100
(06/08, chỉ 500 cp)**. Ràng buộc thanh khoản §12#5 binding gấp ~17× so với TV4 (vốn đã bị coi là chặn).
> ⚠️ **Nhiễu biên độ sàn — nguồn dương tính giả mới, đáng ghi**: ngưỡng FLOOR2/IDIOCRASH của
> `anomaly_scan.py` (−6,5% / −6,0%) hiệu chỉnh theo biên độ **HOSE ±7%**. Trên **UPCoM (±15%)** và
> **HNX (±10%)** một phiên biến động bình thường cũng trip cờ. DNA (−14,2%) và TOS (−15,3%, Phần 2b)
> đều là UPCoM. Đọc cờ của mã UPCoM/HNX phải quy về **số lần chạm sàn**, không đọc theo % tuyệt đối.

**Phần 2 — quét RỘNG hơn universe của anomaly_scan (MỚI tuần này, đóng đúng điểm mù mandate nêu).**
`anomaly_scan` chỉ nhìn 252 mã (holding + rating≤2) → mã ngoài watchlist sập vì khủng hoảng là **vô
hình**. Quét cơ học toàn bộ `bq_cache/ticker` 2026: **1.024 mã có dữ liệu, 297 mã đạt sàn thanh khoản
≥1 tỷ/phiên**, tiêu chí IDIOCRASH giống hệt (ret≤−6% ∧ idio≤−5%), cửa sổ 9 phiên → **9 sự kiện / 8 mã**.
Chấm theo §2/§2.5 + red-flag §10.10 — **cả 8 đều NON, 0 QUALIFY, và không mã nào có sự kiện khủng hoảng**:

| Mã | Ngày | ret/idio | Số chặn (bằng chứng BQ, Q2/2026) | Kết luận |
|---|---|---|---|---|
| **TOS** | 29/07 | −15,3% / −16,7% | **BANNED vĩnh viễn** (KB) + PB 2,41 → không có sàn định giá (§2#5). Đã hồi 88.000→96.000 | Loại thẳng, xem 2b |
| **DCL** (Dược Cửu Long) | 06/08 | −6,9% / −6,3% | ROE_Trailing **−0,11%**, ROE_Min3Y 1,3% (lợi nhuận ≈0), **CF_OA_P0 −51,5 tỷ**, PB 1,97 → hỏng cả #3 lẫn #5. Thêm: pharma = buy-and-hold, timing phá alpha (KB) | NON |
| **ASP** (An Pha Petrol) | 04/08 | −6,1% / −6,9% | **CR 0,86 (<1)** + Debt_Eq 2,71 → hỏng #4 solvency. NP 66,6 tỷ nhưng **CF_OA −1,8 tỷ** = đúng chữ ký §10.10 (LN sổ sách không có tiền). ROE_Min3Y −9,7% | NON |
| **ACC** | 31/07 + 03/08 | −6,8/−6,9% | PB **0,32** hấp dẫn NHƯNG **CF_OA_3Y −234,8 tỷ** (âm cấu trúc 3 năm), Q2 CF_OA −230 tỷ, LtDebt 517→857 tỷ. §10.10 | NON dù rẻ |
| **SHN** | 03/08 | −8,0% / −9,5% | PE −134 (lỗ), Debt_Eq 2,99, ROE_Min3Y −0,1% | NON |
| **HID** | 05/08 | −7,0% / −6,9% | PE −4,9 (lỗ), penny 3.480 | NON |
| **DST** | 31/07 | −7,0% / −6,5% | **Doanh thu = 0** (vỏ), PE 78 | NON |
| **SBS** | 31/07 | −6,3% / −5,7% | PB 2,44 → không có sàn định giá | NON |

**Phần 2b — TOS: đã kiểm tra là sập THẬT, không phải hiện vật điều chỉnh giá.** `Close/Price` reset
về 1,0 ngày 23/07 (hành động doanh nghiệp, BVPS Q2 63.866→39.794 = pha loãng), nhưng cú −15,3% ngày
29/07 xảy ra SAU đó trên 449.824 cp (39,6 tỷ ≈ 17× KL thường) — biến động giá thật. Không đào thêm:
**TOS nằm trong danh sách BANNED vĩnh viễn**, và PB 2,41 hỏng §2#5 — hai lý do độc lập cùng loại.

**Phần 3 — WebSearch tin khởi tố/bắt giữ (cửa sổ 24/07→07/08, bù điểm mù của scan giá/KL): 0 case mới.**
5 truy vấn. Mọi tên xuất hiện trong cửa sổ đều **đã có kết luận từ trước**: PAT (khởi tố CT Lưu Bách Đạt
22/07 — đã loại tuần trước), DGC, PNJ, TV4 (11/06), PC1 (**BANNED**), BCG (huỷ niêm yết bắt buộc 15/07
do chậm nộp BCTC >6 tháng — NON kinh điển, tin cũ). Bối cảnh: tuần 03–07/08 thị trường thận trọng,
nhóm ngân hàng mất ~200.000 tỷ vốn hoá trong tháng 7 — **yếu tố vĩ mô/beta, không phải khủng hoảng
riêng lẻ**, ngoài phạm vi sleeve này.

**Phần 4 — read-through case đang theo dõi (có 2 tin MỚI đáng kể, không làm lại từ đầu)**

- **PNJ** (§7, AMBIGUOUS): ⚠️ **hai tin mới ngược chiều nhau.**
  *(xấu, định lượng được)* Vietstock 06/08 công bố cơ chế thiệt hại: **giá trị hàng hoá phải mua lại
  5.900 tỷ trong 20 ngày đầu tháng 7 = 3,7× doanh thu bán hàng** cùng kỳ ("rút tiền hàng loạt" sau vụ
  chứng thư kim cương). **Q2/2026 đã LỖ** (doanh thu 8.484 tỷ, +12% YoY); luỹ kế 6T vẫn lãi 1.185 tỷ
  nhờ Q1. → phần lớn thiệt hại rơi vào **Q3**, đúng như cổng xác nhận đã đặt.
  *(tốt, dòng tiền thật)* Khối ngoại **mua ròng 5 phiên liên tiếp ~335 tỷ** (riêng 03/08: 82 tỷ). Giá
  **30.750 (24/07, đáy ~6 năm) → 37.900 (05/08) → 36.450 (06/08), +18,5% từ đáy**, 2 phiên trần liên tiếp.
  → **Không đổi phân loại AMBIGUOUS. Cổng xác nhận vẫn là BCTC Q3/2026 (~cuối 10/2026)** — nay có SỐ
  cụ thể để kiểm: nghĩa vụ mua lại 5.900 tỷ có phản ánh hết vào Q3 không, và CF_OA Q3 có âm không.
  **Điểm hành động đã hẹp lại**: mức chiết khấu đáy 24/07 không còn (+18,5%), tức nếu trước đây do dự
  thì cửa sổ đó đã đóng phần lớn — nhất quán với bài học "đừng đuổi sau khi đã hồi".
- **DGC** (§6, AMBIGUOUS-nghiêng-constructive): ⚠️ tin mới **chạm lõi**, nhưng **cửa sổ mua đã đóng cơ học**.
  Vietstock 06/08: DGC **bị dừng khai thác mỏ quặng**, phải **nhập toàn bộ nguyên liệu**, biên lợi nhuận
  **34,9% → 23%**, LN 6 tháng **−50%**. Đây là thiệt hại *vận hành cấu trúc*, không phải rủi ro quản trị
  thuần — nghiêng về gạch ❌ §2 ("lõi tự hỏng"), làm yếu luận điểm RE-DO 23/07.
  NHƯNG giá đã **hồi trọn vẹn**: đáy 36.000 (27/07) → **43.350 (06/08), +20,4%**, tức **cao hơn cả mức
  43.000 trước cú sập 20/07**; PB 0,84 → **1,01**. → **Không còn dislocation nào để mua** ⇒ tranh luận
  QUALIFY/NON trở nên vô nghĩa cho mục đích *vào lệnh*. Ghi nhận để lần sau tái xuất hiện thì đọc lại
  từ dữ kiện "mỏ bị dừng", đừng đọc lại từ khung 23/07.
- **TV1** (§4): **không có tin mới**. Giá đi ngang 19.400–20.000 suốt 3 tuần (06/08: 19.500), PB 1,03
  (BVPS đã cập nhật sau Q2). **Cổng gần: lấy ý kiến chọn đơn vị kiểm toán 10/08 — còn 3 ngày**, nên
  đây là mục đáng theo dõi nhất trong watchlist tuần tới. Cổng phụ (ngày ĐKCC cổ tức 15%) chưa công bố.
- **TV4** (§13 tuần trước, AMBIGUOUS): **không có tin mới**. Giá đứng im **12.900** (PB 0,97), KL
  400–7.200 cp/phiên — xác nhận lại ràng buộc thanh khoản. **Cổng xác nhận nhị phân giữ nguyên: ý kiến
  kiểm toán BCTC bán niên soát xét 2026, hạn ~30/08.** (TV2 tiếp tục re-rate: 25.350 → 26.300.)

**Phần 5 — khuyết tật cơ chế phát hiện được trong lúc quét (BÁO CÁO, không tự sửa — chạm production)**

`anomaly_scan.write_flags()` cập nhật `last_alert = max(...)` **không phân biệt `reasons`**, còn
`anomaly_gate.anomaly_excluded()` chỉ đọc `last_alert` **không đọc `reasons`** ⇒ **một cờ CEIL2 (giá
TĂNG trần 2 phiên) gia hạn TTL 30 ngày của cổng loại-trừ y hệt một cờ khủng hoảng.** Hiện trạng
07/08: **10 mã đang bị loại, trong đó 2 mã bị loại vì ĐI LÊN** — `VRE` (CEIL2 30/07, +6,8% → hết hạn
**29/08**) và `PNJ` (CEIL2 04–05/08, +6,9% → hết hạn **04/09**).
Hệ quả hai chiều, cần người quyết định chứ không tự sửa:
- *Tình cờ có lợi*: `current_ops.md` đang lo "cờ PNJ TTL 30 ngày hết hạn ~23/08, gate mở TRƯỚC cổng xác
  nhận thật tháng 10". Thực tế cờ đã tự gia hạn tới **04/09** — nhưng **vì một lý do sai** (giá tăng),
  nên KHÔNG được coi là đã xử lý xong; nhu cầu gia hạn có chủ đích trước cổng Q3 vẫn còn nguyên.
- *Bất lợi*: VRE bị loại khỏi bước chọn mã cơ học 30 ngày chỉ vì tăng trần 2 phiên — hoàn toàn ngoài ý
  đồ "đừng mua đúng lúc doanh nghiệp đang khủng hoảng".
Sửa tối thiểu khả dĩ (chưa đề xuất wire, chưa qua quant-skeptic): `anomaly_excluded` bỏ qua cờ mà
`reasons` chỉ gồm tín hiệu TĂNG (`CEIL2`), hoặc `write_flags` giữ `last_alert` riêng cho cờ giảm.
Chạm 1 sổ production + 3 sổ paper (xem docstring `insider_sell_flagged`) ⇒ cần gate đầy đủ.

**Tổng kết tuần**: **252 mã** (anomaly_scan) **+ 297 mã** (quét rộng, thanh khoản ≥1 tỷ/phiên, mới tuần
này) **+ 5 truy vấn tin tức** · **0 QUALIFY mới** · **0 case mới đáng nâng thành mục riêng** · 9 NON
(DNA + 8 mã quét rộng) · 4 read-through (PNJ, DGC — cả hai có tin mới; TV1, TV4 — không tin mới) ·
1 khuyết tật cơ chế báo lên fleet. **Mốc gần nhất phải theo: TV1 10/08 (3 ngày) → TV4 30/08 → PNJ Q3
cuối 10/2026.**

### 2026-08-14 (job `Taylor_20260814_011001`) — 0 QUALIFY mới · 0 case mới · 4 read-through (2 có tin mới THẬT) · 1 đề xuất lọc nhiễu

**Phần 1 — anomaly_scan** (`anomaly_scan.py --backfill-days 8 --no-flags`, cache BQ refresh 13/08
23:45, phiên cuối **2026-08-13**, universe 252 mã = 29 holding + 241 watchlist rating≤2).
Cờ trong 8 phiên (06/08→13/08): **3, TẤT CẢ đều là cờ TĂNG** — GAS `CEIL2` 10/08 (+7,0%, idio +6,5%,
239,2 tỷ), GVR `CEIL2` 10/08 (+6,9%, idio +6,4%, 194,6 tỷ), PNJ `CEIL2` 05/08 (+6,9%, đã ghi tuần
trước). **0 cờ FLOOR2/IDIOCRASH** trong universe hẹp ⇒ không có mã nào trong watchlist bị sập riêng lẻ.

**Phần 2 — quét RỘNG toàn `bq_cache/ticker` 2026** (bù điểm mù universe hẹp, cùng phương pháp tuần
trước): 1.275 mã có dữ liệu 2026 → **458 mã đạt sàn thanh khoản ≥1 tỷ/phiên**, tiêu chí IDIOCRASH
(ret ≤ −6% ∧ idio ≤ −5% ∧ val ≥ 1 tỷ), cửa sổ 05/08→13/08 → **18 sự kiện / 16 mã**.
*(⚠️ Số 458 KHÔNG so trực tiếp với 297 của tuần trước — tuần này lọc bằng `max(val1m_bn)` cả năm
2026, tuần trước lọc trong cửa sổ. Cùng chiều nới lỏng, tức quét rộng hơn chứ không hụt.)*

**Phần 2b — bước lọc MỚI tuần này: vị trí giá so với đỉnh/đáy 3 tháng.** Tiêu chí ret/idio 1 phiên
KHÔNG phân biệt được "sập xuống đáy mới" (dislocation — cái sleeve này cần) với "chốt lời sau khi
tăng dựng đứng" (không có nỗi sợ nào để mua). Đo cả 16 mã:

| Nhóm | Mã | Đọc |
|---|---|---|
| **PULLBACK từ đỉnh** (còn ≥ +25% trên đáy 3M) — 7 mã | LLM (+112,6% trên đáy), THD (+303,4%), DST (+117,5%), VNZ (+93,9%), DDG (+66,7%), HII (+60,4%), MVN (+26,5%), L14 (+26,0%) | **Không phải case fear-buy** — đang trong xu hướng TĂNG. Ví dụ rõ nhất: **HII** 6.200 (29/07) → **9.390 (11/08), +51% trong 9 phiên**, cờ 12/08 chỉ là nhịp chỉnh −6,3%; **LLM** 19.200 → 40.400 (+110%). |
| **Trung gian** — 6 mã | F88, HHP, TDM, DCL, HID, VNE | Không ở đáy, không có sự kiện — xem Phần 2c/2d |
| **Đáy 3M mới** — 2 mã | **CRC** (−37,5% so đỉnh, +1,9% trên đáy), **ANT** (−30,1% / +6,7%) | Chỉ 2 mã này đáng chấm §2 — xem Phần 2c |

⇒ **13/16 mã bị loại chỉ bằng bước vị-trí-giá**, trước cả khi đọc BCTC. Đề xuất (chưa wire, chỉ ghi
vào playbook): mọi lần quét rộng sau này chạy bước này TRƯỚC khi kéo dữ liệu tài chính — rẻ hơn
nhiều lần và loại đúng nhóm dương tính giả áp đảo của tuần này.

**Phần 2c — chấm §2/§2.5/§10.10 cho 2 mã đáy-mới + các mã trung gian đáng nhắc (BQ Q2/2026):**

| Mã | Số chặn | Kết luận |
|---|---|---|
| **ANT** (Antesco) | **CF_OA_P0 −6,49 tỷ trong khi NP_P0 +30,4 tỷ** = đúng chữ ký §10.10 (lãi sổ sách không có tiền) · Debt_Eq **2,95** · CR 1,06 · FSCORE 3 · PB **1,80** (không có sàn tài sản §2#5) | **NON** |
| **CRC** (Create Capital VN) | PB **0,50** và CF_OA_P0 +118 tỷ / CR 3,02 / Debt_Eq 0,49 — hồ sơ *không* xấu — NHƯNG **không có sự kiện khủng hoảng nào** (WebSearch 0 tin pháp lý/sự cố), giá **trôi chậm** 5.830→5.220 suốt 8 phiên chứ không phải cú sập rời rạc. ROE_Trailing 5,8%, FSCORE 3, DY 0 | **Không phải case** (thiếu trigger §0.5); WATCH yếu |
| **F88** (Đầu tư F88, UPCoM) | Trôi 72.600→65.500 (−10%/8 phiên). Tin thật: **Christopher E. Freund (Mekong Capital) từ nhiệm HĐQT từ 11/08** + đợt chào bán chỉ phân phối 11/22 triệu cp. NHƯNG **Q2/2026 LÃI 303 tỷ, gấp đôi cùng kỳ; 6T 545 tỷ** — doanh nghiệp đang lãi kỷ lục, không có nỗi sợ để mua. Thêm: **không có dòng nào trong `ticker_financial`** ⇒ không chấm được §2#3/#4/#5 | **Không phải case** |
| DCL, HID, DST | Đã kết luận **NON** tuần trước (07/08), không làm lại | NON (cũ) |
| HHP, TDM, VNE, DDG, L14, VNZ, MVN, THD | HHP CF_OA_3Y **−550 tỷ**; TDM PB 2,91 + FSCORE 2; VNE CR 0,96 (<1) + Debt_Eq 3,13 + ROE_Min3Y −30%; DDG ROE_Trailing **−97%**, CR 0,39; L14 CF_OA −41 tỷ, ROE 2,3%; VNZ PB **16,99**, Debt_Eq 12,8; MVN PB **2,99**; THD PB **9,41**, PE 313 | **NON** (8 mã) |

**Phần 3 — WebSearch tin khởi tố/bắt giữ (cửa sổ 07/08→14/08): 0 case NIÊM YẾT mới.** 6 truy vấn.
Vụ khởi tố duy nhất mới trong cửa sổ là **CTCP Đầu tư 706** (08/08 — CT Phan Anh Tuấn + GĐ Đặng Minh
Khoa, tội vi phạm quy định về khai thác tài nguyên, mỏ núi Lệ Thuỷ/Quảng Ngãi) — **không niêm yết,
không có mã** ⇒ ngoài phạm vi. Mọi tên khác xuất hiện đều đã có kết luận: DGC, PAT, PC1 (**BANNED**),
TV4, ACV/Vinaconex (tin quý 1).

**Phần 4 — read-through case đang theo dõi (2 case có tin MỚI thật)**

- **DGC** (§6, AMBIGUOUS-nghiêng-constructive): **ĐHĐCĐ đã họp sáng 13/08 — có 4 dữ kiện mới, ngược
  chiều nhau, và lần đầu là lời của chính ban lãnh đạo chứ không phải suy đoán báo chí.**
  *(xác nhận cái xấu, đúng như tuần trước ghi)* Ban lãnh đạo giải trình: **"Khai trường 25 phải tạm
  dừng hoạt động để phục vụ công tác điều tra"** ⇒ **chuyển sang dùng HOÀN TOÀN quặng apatit mua ngoài
  + nhập khẩu**, giá vốn phốt pho vàng tăng đáng kể. Kế hoạch 2026: **10.100 tỷ doanh thu / 1.600 tỷ
  LNST — thấp nhất kể từ 2020**. Trên 379,78 triệu cp ⇒ EPS mục tiêu ≈ **4.213đ** ⇒ tại giá 43.900
  là **PE forward ≈ 10,4×** và ROE forward ≈ 9,9% (so ROE_Trailing 14,7%).
  *(cái tốt, và là góc mandate dặn không được bỏ sót — dòng tiền/cổ tức)* **CF_OA_P0 Q2 = 1.083 tỷ vs
  NP_P0 389 tỷ = 2,8× NP** ✓ (§2#3 vẫn PASS dù biên bị đánh) · **Debt_Eq 0,19 · CR 5,21** (bảng cân
  đối gần như không nợ) · HĐQT trình **cổ tức 2025 tổng 80% tiền mặt** và **duy trì 30% cho 2026** =
  3.000đ/cp ⇒ **6,8% yield tại 43.900**. Miễn nhiệm TGĐ Lưu Bách Đạt + TV HĐQT Nguyễn Quốc Trung; nhóm
  cổ đông 20,34% đề cử 2 người thay. **Lưu Bách Đạt XUẤT HIỆN TRỰC TIẾP tại đại hội** — nhất quán với
  biện pháp ngăn chặn là *cấm đi khỏi nơi cư trú*, KHÔNG phải tạm giam.
  → **Không đổi phân loại. Nhưng đọc cho đúng: đây KHÔNG còn là scandal cá nhân thuần** — mỏ bị dừng
  là thiệt hại *vận hành cấu trúc* (gạch ❌ §2 "lõi tự hỏng"), chỉ được bù bằng bảng cân đối + dòng
  tiền + cổ tức mạnh bất thường. **Và vẫn không có dislocation để mua**: giá 43.900 (13/08) ≈ đỉnh
  trước cú sập 20/07, PB 1,03. Tranh luận QUALIFY/NON tiếp tục vô nghĩa cho mục đích *vào lệnh*.
- **PNJ** (§7, AMBIGUOUS): **số Q2/2026 nay đã vào BQ và XẤU HƠN những gì báo chí mô tả tuần trước.**
  `NP_P0 = **−282,9 tỷ (LỖ quý)**` · `CF_OA_P0 = **−1.568 tỷ**` (dòng tiền kinh doanh âm nặng — khớp
  cơ chế nghĩa vụ mua lại hàng 5.900 tỷ) · **FSCORE rơi xuống 1** (từ mức lành mạnh trước đó). Giá
  35.300 (13/08), đã lùi từ 37.900 (05/08) nhưng vẫn **+14,8% trên đáy 30.750 (24/07)**.
  → **Không đổi AMBIGUOUS, và luận điểm "chờ cổng Q3" nay mạnh hơn**: thiệt hại đã bắt đầu hiện ra
  trong SỔ chứ không chỉ trong tin. **Không có lý do gì vào trước BCTC Q3/2026 (~cuối 10/2026).**
- **TV1** (§4/§14, QUALIFY): **giá phá lên khỏi biên đi ngang 3 tuần** — 19.400-20.000 → **20.300
  (12-13/08)**, PE 3,51 · PB 1,07. **Hai cổng đều CHƯA đóng được bằng bằng chứng:**
  (a) **kết quả lấy ý kiến bằng văn bản chọn đơn vị kiểm toán (10/08) VẪN CHƯA công bố** — 4 ngày sau
  cuộc lấy ý kiến, tra vietstock/stockbiz/dantri đều chỉ có tin *lịch*, không có tin *kết quả*.
  ⚠️ Giữ nguyên cảnh báo §14: **"chưa thấy tin xấu" ≠ "đã qua cổng"** — kiểm lại tuần tới.
  (b) **ngày thanh toán cổ tức 15% = 14/08 chính là HÔM NAY**, chưa verify được đã trả thật (nguồn
  tổng hợp 1 chiều, chưa có công bố gốc HOSE/HNX). Đây đúng là phép thử DDM mà §14 đặt ra ⇒ **việc
  cụ thể cho lần quét tuần sau: xác nhận tiền cổ tức đã về.**
  ⚠️ **Điểm mới đáng ghi, chưa từng nêu ở §14: `CR_P0 = 0,97` (<1)** và `Debt_Eq 1,18` — thanh khoản
  ngắn hạn của TV1 mỏng hơn hồ sơ TV4 (CR 1,72) rõ rệt. Chưa đủ để hạ QUALIFY (ROE_Trailing 30,6%,
  **CF_OA_3Y +498 tỷ ≈ 92% vốn hoá 542 tỷ**), nhưng phải theo dõi: một công ty tư vấn có CR<1 mà vừa
  chi cổ tức 15% thì đệm thanh khoản còn mỏng hơn con số này.
- **TV4** (§13 tuần trước, AMBIGUOUS): **không có tin mới về kiểm toán.** Giá **12.800** (13/08,
  PB 0,96 · PE 5,76 · DY 7,8%), KL 200-7.200 cp/phiên — ràng buộc thanh khoản không đổi. Xác nhận lại
  ĐHĐCĐ bất thường tháng 8 **vẫn chưa công bố chương trình/địa điểm**. **Cổng nhị phân giữ nguyên: ý
  kiến kiểm toán BCTC bán niên soát xét 2026, hạn ~30/08 (còn 16 ngày).**

**Tổng kết tuần**: **252 mã** (anomaly_scan) **+ 458 mã** (quét rộng) **+ 6 truy vấn tin tức** ·
**0 QUALIFY mới · 0 case mới đáng nâng thành mục riêng** · 10 NON + 3 không-phải-case (CRC, F88, và
nhóm pullback) · 4 read-through (**DGC, PNJ, TV1 đều có dữ kiện mới thật**; TV4 không) · 1 đề xuất
lọc nhiễu (bước vị-trí-giá 3M, loại 13/16 dương tính giả).
**Mốc gần nhất phải theo: TV1 kết quả kiểm toán + cổ tức 14/08 (kiểm tuần sau) → TV4 30/08 → PNJ Q3
cuối 10/2026.**

Nguồn tin tuần này: [nguoiquansat — khởi tố CT/GĐ Đầu tư 706 (08/08)](https://nguoiquansat.vn/khoi-to-chu-tich-hdqt-va-giam-doc-mot-cong-ty-lon-302746.html) ·
[nguoiquansat — DGC ĐHĐCĐ 13/08, Lưu Bách Đạt xuất hiện](https://nguoiquansat.vn/hoa-chat-duc-giang-dgc-sau-bien-co-khoi-to-ong-luu-bach-dat-bat-ngo-xuat-hien-tai-dhdcd-310193.html) ·
[tuoitre — Mekong Capital founder rời HĐQT F88 (11/08)](https://news.tuoitre.vn/mekong-capital-founder-resigns-from-vietnams-pawnshop-chain-f88-board-103260811202442933.htm) ·
[baomoi/TheLEADER — F88 lãi Q2/2026 gấp đôi](https://baomoi.com/f88-bao-lai-quy-ii-2026-gap-doi-cung-ky-c55692596.epi) ·
[baomoi — PECC4 thay toàn bộ ban lãnh đạo](https://baomoi.com/sau-bien-co-phap-ly-pecc4-da-thay-toan-bo-ban-lanh-dao-c55703646.epi)

---

### 2026-08-17 — QUÉT SÁNG THỨ HAI (job `Taylor_20260817_010002`, cadence khác quét tuần: mục đích là BẢO VỆ PHÍA MUA trước 09:00) — 1 case mới (POM → NON) · 0 QUALIFY · 1 mã đang mua có 2 cổng CHƯA đóng

Cửa sổ tin 14/08 (sau phiên) → 16/08. Danh mục đang gác **29 mã** (13 NH + 16 ngoài NH).

**Phần 1 — anomaly_scan** (`--backfill-days 5 --no-flags`): phiên cuối cache **2026-08-14**,
universe 252 mã, **watchlist TƯƠI** (`active_nav` computed_at 2026-08-14) — không có cảnh báo quá hạn.
**0 FLOOR2 · 0 IDIOCRASH.** Chỉ 2 cờ TĂNG (GAS/GVR `CEIL2` 10/08) đã ghi tuần trước.

**Phần 2 — quét rộng** `bq_cache/ticker` 2026 (1.275 mã → **458 mã** đạt ADV ≥1 tỷ), IDIOCRASH
12/08→14/08: **8 sự kiện / 8 mã**. 7/8 đã có kết luận tuần trước (ANT/DDG/HHP/TDM/L14 **NON**;
HII/LLM **pullback từ đỉnh, không phải case**). **1 mã MỚI: POM.**

| Mã | Số chặn | Kết luận |
|---|---|---|
| **POM** (Thép Pomina), 3.200đ, −33,3% so đỉnh 3M, +10,3% trên đáy | **Vốn chủ sở hữu ÂM** (−590 tỷ công ty mẹ / −630 tỷ hợp nhất, BCTC kiểm toán 2025) ⇒ trượt §2#4 + §10.5 solvency, và dưới sàn 30 tỷ để giữ tư cách công ty đại chúng · **ý kiến kiểm toán NGOẠI TRỪ ≥3 năm liên tiếp** = gạch ❌ tường minh của §2 · **hạn chế giao dịch từ 19/06/2026, chỉ khớp phiên thứ Sáu** · đang bị xem xét huỷ niêm yết/huỷ tư cách đại chúng | **NON** |

⚠️ **Lớp dương-tính-giả CƠ HỌC mới phát hiện (đề xuất lọc, chưa wire):** POM chỉ giao dịch **1
phiên/tuần** nên "ret 1 phiên" của nó thực chất là **ret 1 TUẦN** — mọi mã bị hạn chế giao dịch sẽ
sinh cờ IDIOCRASH giả theo cùng cơ chế. Bước lọc rẻ: loại mã có <4 phiên có KL trong 5 phiên gần
nhất, chạy TRƯỚC khi kéo dữ liệu tài chính (cùng tinh thần bước vị-trí-giá 3M thêm tuần trước).

**Phần 3 — bối cảnh thị trường (mới, ảnh hưởng phía mua):** VNINDEX **14/08 đóng 1.729,08, −36,55đ
(−2,07%)**, mất MA200; nhóm Vingroup lấy ~14,5 điểm chỉ số (VIC −3,5% / VRE −3,3% / VHM −2,7%);
BĐS −2,93%, CNTT −2,17%, NH −0,82%. **DT5G vẫn NEUTRAL** (`golive_state_today` as_of 2026-08-14,
published 19:01, base_state_dt4=3 == dt5g=3, không bị macro cap) — trạng thái này đã tính SAU cú
giảm, không phải số cũ.

**Phần 4 — PHÍA MUA phiên 17/08 (câu hỏi chính của lượt quét này): CHỈ CÓ 1 LỆNH MUA trên cả 2
account** — SpaceX `BUY-TV1-DISC-2026-08-17`, 500cp LO ≤20.640 (10,32tr), tranche CUỐI của chương
trình gom 2.300cp (đã khớp 1.800). ZaloPay 0 lệnh.
- **Luận điểm TV1 KHÔNG gãy**: 0 tin mới 14→16/08 (vietstock tin-tức-sự-kiện trống trong cửa sổ);
  nhân sự vẫn nguyên trạng (CT Nguyễn Hữu Chỉnh tạm đình chỉ từ 02/06, TGĐ Nguyễn Kim Cương phụ trách).
- **NHƯNG cả 2 cổng §14 vẫn CHƯA đóng, và cổng (b) nay ĐÃ QUÁ HẠN:**
  (a) **kết quả lấy ý kiến bằng văn bản chọn đơn vị kiểm toán (10/08) vẫn CHƯA công bố** — 7 ngày.
  Nền: cả **4 Big4 (Deloitte/EY/KPMG/PwC) đã TỪ CHỐI** kiểm toán TV1 sau khi CT bị khởi tố.
  (b) **cổ tức tiền mặt 15%, ngày thanh toán công bố 14/08 — KHÔNG có bằng chứng đã về.**
  `cashDividendReceiving` của SpaceX = **9.775.000đ ĐỨNG YÊN** từ 13/08 qua 14/08 tới bản đọc mới
  nhất, `totalCash` không tăng khoản nào ⇒ chưa credit. (Đây đúng là phép thử DDM §14 đặt ra.)
- ⚠️ **Điểm giá đáng lưu ý (không phải vi phạm luật, nhưng nên cân nhắc):** limit **20.640** nằm
  **+2,69% TRÊN giá đóng cửa 14/08 (20.100)**. Nguyên nhân cơ học: trần động neo vào **trung bình 5
  phiên (20.140)**, mà trung bình 5 phiên TRỄ so với cú giảm −2,07% của chỉ số. Trần 20.744 vẫn dưới
  `max_no_chase_ceiling` 25.000 nên hệ không chặn. Đề xuất escalate (KHÔNG tự đổi plan): hạ limit
  tranche cuối về ≤20.100 hoặc hoãn 1 phiên, vì đây là 500cp cuối — không có áp lực thời gian.

**Phần 5 — read-through peer (không phải case mua):** **TV3 (PECC3)** 14/08 bổ nhiệm PTGĐ Hồ Anh
Tùng + tái bổ nhiệm GĐ Trung tâm Nhiệt điện — sau khi 3 lãnh đạo (nguyên CT Nguyễn Như Hoàng Tuấn,
TGĐ Lạc Thái Phước, KTT Phạm Hoàng Vinh) bị khởi tố/tạm giam. Q2/2026 **doanh thu −53,8% YoY nhưng
LNST +30,5% YoY** — chữ ký chất lượng lợi nhuận cần soi, nhưng TV3 quá nhỏ/mỏng thanh khoản, KHÔNG
phải ứng viên. Giá trị duy nhất: xác nhận **cụm khởi tố ngành tư vấn điện (PECC1/3/4) là có thật và
còn đang diễn tiến** — đúng bối cảnh rủi ro của TV1.

**Phần 6 — nhóm ngân hàng (13 mã) + nhóm ngoài NH (16 mã):** 0 sự kiện. Không có tin kiểm soát đặc
biệt / chuyển giao bắt buộc / khởi tố lãnh đạo NH / rút tiền hàng loạt trong cửa sổ. Ghi nhận 2 mục
vận hành (không phải rủi ro): **VIX chốt quyền cổ tức CỔ PHIẾU 5% tuần 17-21/08** (điều chỉnh số
lượng — việc của Winston/Mafee); **DGC vẫn trong danh sách cắt margin HOSE tháng 8** (đã biết).

**Phần 7 — 1 khuyết tật dữ liệu (nhỏ, báo Winston):** trong `bq_cache/ticker/2026.parquet`, cột
mirror `VNINDEX` phiên **2026-08-13** có **1 dòng (mã F88) mang giá trị CŨ 1793,18** thay vì 1765,63
(775 dòng còn lại đúng). `anomaly_scan.compute_signals` dùng `.first()` theo ngày nên KHÔNG bị ảnh
hưởng (F88 không đứng đầu bảng chữ cái và không nằm trong universe 252). Query ad-hoc dùng
`max(VNINDEX)` thì BỊ — chính lượt này đã dính và phải tính lại: dùng **`ticker='VNINDEX'`** làm
chuỗi chỉ số, đừng dùng cột mirror.

**Tổng kết**: **29 mã đang gác** rà qua · 252 mã (anomaly_scan) + 458 mã (quét rộng) + 7 truy vấn tin
· **1 case mới (POM → NON) · 0 QUALIFY mới** · watchlist **KHÔNG** quá hạn · **1 lệnh mua duy nhất
phiên 17/08 (TV1) — luận điểm không gãy nhưng 2 cổng chưa đóng + 1 điểm giá đáng escalate.**
**Mốc phải theo: TV1 kiểm toán + cổ tức (quá hạn, kiểm mỗi phiên) → TV4 30/08 → PNJ Q3 cuối 10/2026.**

**✅ ĐÃ ĐÓNG (2026-08-17, Mike theo quyết định user):** tranche CUỐI TV1 đã khớp ĐỦ — SpaceX 500cp @
**20.100** (PLACE/FILL 09:15 ICT, `exec_SpaceX_2026-08-17_journal.csv`, trong khi plan ref 20.640).
Tracking `fearbuy-monday-buyside-TV1-2-cong-chua-dong` (2 cổng chưa đóng trước phiên 17/08) **CHÍNH
THỨC ĐÓNG** — lệnh đã xong, không còn theo dõi. Chương trình tích luỹ TV1 2.300cp (5% NAV, cả 2
account) vẫn hoạt động; mốc dài hạn giữ nguyên: TV1 kiểm toán + cổ tức (theo dõi chương trình) →
TV4 30/08 → PNJ Q3 cuối 10/2026.

Nguồn: [cafef — "tội đồ" nào khiến VN-Index bay gần 37 điểm phiên 14/8](https://cafef.vn/toi-do-nao-khien-vn-index-bay-gan-37-diem-trong-phien-14-8-188260814153439097.chn) ·
[stockbiz — lý do POM bị duy trì hạn chế giao dịch](https://stockbiz.vn/tin-tuc/pom-ly-do-co-phieu-cua-thep-pomina-bi-duy-tri-han-che-giao-dich/40815374) ·
[24hmoney — Pomina đối mặt án huỷ niêm yết](https://24hmoney.vn/news/pomina-doi-mat-an-huy-niem-yet-c1a2794307.html) ·
[cafef — 4 Big4 từ chối kiểm toán TV1](https://cafef.vn/mot-cong-ty-con-cua-evn-bi-ca-4-cong-ty-big4-tu-choi-kiem-toan-sau-khi-chu-tich-hdqt-bi-khoi-to-188260701114401433.chn) ·
[nguoiquansat — PECC3 (TV3) biến động nhân sự 14/08](https://nguoiquansat.vn/bien-dong-moi-tai-doanh-nghiep-dien-quy-mo-300-ty-dong-sau-khi-dan-lanh-dao-bi-khoi-to-310429.html) ·
[vietstock — lịch chốt quyền cổ tức tuần 17-21/08](https://vietstock.vn/2026/08/tuan-17-2108-noi-bat-khoan-co-tuc-hon-5-ngan-ty-cua-tan-binh-hose-738-1481215.htm)

---

### 2026-08-21 (job `Taylor_20260821_011002`) — 0 QUALIFY mới · 1 NON mới (SGT) · 1 AMBIGUOUS-yếu cần cổng (ICG) · 2 không-phải-case (NTL, TIN) · 4 read-through (3 có tin mới THẬT)

Cửa sổ tin **14/08 → 20/08**. Danh mục đang gác **29 mã** (13 NH + 16 ngoài NH).

**Phần 1 — anomaly_scan** (`--backfill-days 8 --no-flags`): phiên cuối cache **2026-08-20**, universe
**251 mã** (H:29 / W:240), **watchlist TƯƠI** (`active_nav` computed_at 2026-08-20) — KHÔNG có cảnh
báo quá hạn. **0 FLOOR2 · 0 IDIOCRASH.** Cờ duy nhất trong 8 phiên là cờ TĂNG: PTX `CEIL2` 12/08
(+9,5%, idio +8,4%, chỉ 0,3 tỷ giá trị — nhiễu thanh khoản mỏng). ⇒ **không mã nào trong danh mục
đang gác bị sập riêng lẻ.**

**Phần 2 — quét RỘNG** `bq_cache/ticker` 2026: 1.275 mã → **693 mã đạt sàn thanh khoản ≥1 tỷ**,
IDIOCRASH (ret ≤ −6% ∧ idio ≤ −5% ∧ val ≥1 tỷ), cửa sổ 13/08→20/08 → **9 sự kiện / 7 mã**.
*(⚠️ 693 KHÔNG so trực tiếp được với 458 của 2 tuần trước — lượt này lọc bằng `max(Close×Volume)` cả
năm 2026 thay vì `Trading_Value`; cùng chiều NỚI LỎNG nên quét rộng hơn, không hụt.)*
Chuỗi chỉ số lấy từ `ticker='VNINDEX'`, **không** dùng cột mirror (bẫy 08-17 Phần 7).

Áp 2 bước lọc rẻ đã đề xuất các tuần trước, TRƯỚC khi kéo tài chính — **loại 3/7 mã**:

| Bước lọc | Loại | Vì sao |
|---|---|---|
| Vị-trí-giá 3M (thêm 08-14) | **VNZ** (+81,7% trên đáy 3M), **LLM** (+86,8%) | Pullback trong xu hướng TĂNG, không có nỗi sợ để mua |
| Số phiên có KL trong 5 phiên (thêm 08-17, ca POM) | **POM** (1/5 phiên) | Hạn chế giao dịch → "ret 1 phiên" thực chất là ret 1 tuần = cờ giả. Đã kết luận **NON** 08-17 |

⇒ còn **4 mã ở/gần đáy 3M, đều CHƯA từng phân loại** (grep lịch sử case: 0 lần xuất hiện):

| Mã | Giá 20/08 | Vị trí | Số chặn / số đỡ | Kết luận |
|---|---|---|---|---|
| **SGT** (SaigonTel, HOSE) | 8.310 (−46,7% so đỉnh 3M, **đúng đáy 3M**) | PB **0,50** (có sàn tài sản) | **CF_OA_3Y = −1.544 tỷ** (âm nặng 3 năm liền) · Debt_Eq 2,23 · 6T/2026 LNTT 82,4 tỷ **−82,3% YoY**, mới xong ~16% kế hoạch năm · **đang chào bán 148 triệu cp giá 10.000 cho cổ đông hiện hữu để TRẢ NỢ** trong khi thị giá 8.310 (**dưới giá phát hành**) | **NON** — gạch ❌ tường minh §2.5 *"DN bị buộc bán tài sản/pha loãng ở đáy"*; PB rẻ không cứu được khi lõi không sinh tiền 3 năm |
| **ICG** (Xây dựng Sông Hồng, HNX) | 10.800 (−34,1% so đỉnh, +4,9% trên đáy) — **4 phiên SÀN liên tiếp** 14→19/08 (−9,9/−9,5/−9,7/−8,0%), KL 186k/95k/58k/232k vs 4-24k nền | PB **0,61** · PE 7,3 · **CF_OA_3Y +362 tỷ ≈ 1,9× vốn hoá 190 tỷ** · vừa trả cổ tức lớn (DY 23%, BVPS 20.406→17.736 QoQ) | **Debt_Eq 2,91→3,09→4,18 trong 2 quý** · CR 1,09 · ROE_Min3Y −2,7% · NP_P0 chỉ 2,18 tỷ trong khi CF_OA_P0 +109 tỷ (chênh quá lớn — nghi thu hồi công nợ/thoái vốn chứ không phải sinh lời) · ngành xây lắp = đúng chữ ký §10.10 (PVX: biên mỏng + đòn bẩy tăng) · **WebSearch 2 truy vấn KHÔNG tìm được tin nào giải thích 4 phiên sàn** | **AMBIGUOUS-yếu — KHÔNG khuyến nghị, nhưng KHÔNG đóng.** Đây là cú sập THẬT có chữ ký sự kiện (sàn liên tiếp + KL nhân 10×) mà chưa xác minh được trigger. Chặn thực tế mạnh hơn cả phân loại: **vốn hoá 190 tỷ, ADV ≤2,4 tỷ ngay trong phiên sập** — nhỏ hơn cả ràng buộc thanh khoản của TV1. **Cổng xác nhận cụ thể (kiểm tuần sau):** (a) công bố giải trình HNX về chuỗi giảm sàn; (b) **BCTC bán niên soát xét, hạn ~30/08** — cùng mốc TV4 |
| **NTL** (Lideco, HOSE) | 12.500 (−24,5% so đỉnh, +0,4% trên đáy) — 1 phiên −6,7% ngày 19/08 với **3,98 triệu cp = ~20× nền**, rồi ổn định | Bảng cân đối rất khoẻ: Debt_Eq 0,25 · CR 8,42 · tiền 822 tỷ · DY 7,1% · PB 0,93 | **Lõi BĐS 2 năm liền không có doanh thu** (Q2/2026 doanh thu thuần ~4,7 tỷ) · CF_OA_P0 **−186 tỷ**, âm 3 quý liền · ROE_Trailing 1,7% · **lợi nhuận đến từ danh mục chứng khoán** (597 tỷ = 29% tổng tài sản, riêng **TCH chiếm 52%** mà TCH đã −40% từ tháng 5) | **Không phải case** — thiếu trigger §0.5 (không có khủng hoảng nào; giá rớt vì NAV danh mục cổ phiếu giảm THẬT, đúng giá trị, không phải nỗi sợ). Thực chất NTL đang là **proxy có đòn bẩy của TCH**, không phải BĐS giá rẻ |
| **TIN** (ICB 8771 — quản lý tài sản/tài chính, UPCoM) | 106.000 (−19,0% so đỉnh, **+6,0% trên đáy** — chỉ là nhả lại cú tăng 105.000→120.000 trong 2 phiên 12-13/08) | ROE_Trailing 76,4% · PE 5,9 | **PB 3,41** → trượt thẳng §2#5 (không có sàn định giá) · Debt_Eq 7,2 (bình thường với tài chính, nhưng cộng PB 3,4 thì không còn đệm) · `CR_P0`/`Cash_P0` = 0 trong BQ (khoảng trống dữ liệu, không chấm được §2#4) | **Không phải case** — pullback sau spike, không có dislocation |

**Phần 3 — WebSearch tin theo BỘ TỪ KHOÁ NHÓM (12 truy vấn + 2 WebFetch):**
- **Nhóm chung** (khởi tố/thanh tra/đình chỉ/huỷ niêm yết/từ chối kiểm toán, cửa sổ 14→20/08):
  **0 case NIÊM YẾT MỚI.** Mọi tên trả về đều đã có kết luận (ACV, PC1 **BANNED**, DGC, TV1/TV3/TV4).
  Ghi nhận nền: HNX tiếp tục huỷ ĐKGD UPCoM tháng 8 (BCG/BCR/DAN/DVT ~1,4 tỷ cp) — không mã nào
  trong danh mục gác.
- **Nhóm ngân hàng (13 mã)** — bổ sung §4.2 `bank_tailrisk_insurance_design_20260814.md`:
  **0 sự kiện.** Không có kiểm soát đặc biệt / chuyển giao bắt buộc / rút tiền hàng loạt / khởi tố
  lãnh đạo NH mới trong cửa sổ. Kết quả trả về chỉ là nền cũ (4 NH đã chuyển giao xong: GPBank, MBV,
  Vikki, VCBNeo).
- **Nhóm BĐS đầu ngành/hạ tầng (VHM, VRE)** — §6 `vic_family_credit_concentration_20260818.md`:
  **0 sự kiện tín dụng mới** trong cửa sổ. Không có tin chậm/vỡ nợ trái phiếu, hạ bậc tín nhiệm,
  giải chấp/call margin cổ đông lớn, hay siết tài sản đảm bảo. Nền đã biết: Vingroup đã tất toán
  906,5 triệu USD trái phiếu quốc tế chuyển đổi.
- **Nhóm ngoài NH (16 mã)** — tai nạn nhà máy / thu hồi sản phẩm / mất mỏ-giấy phép / kê biên /
  tranh chấp lãnh đạo: **0 sự kiện.**

**Phần 4 — PHÍA MUA (câu hỏi bắt buộc của lượt quét): KHÔNG có rủi ro luận-điểm-gãy.**
`plan_SpaceX_2026-08-21.json` và `plan_ZaloPay_2026-08-21.json` đều **0 orders** (HOLD_ALL cả 2
account). Không mã nào trong rổ ứng viên mua. 4 mã mới quét được (SGT/ICG/NTL/TIN) **không nằm
trong 29 mã đang gác**, nên không có read-through nào chạm danh mục.

**Phần 5 — read-through case đang theo dõi (3/4 có dữ kiện mới THẬT)**

- **TV1** (§4/§14/§13, QUALIFY — SpaceX 2.300cp + ZaloPay 1.200cp): giá **20.000** (20/08), vẫn kẹt
  biên 19.900-20.300, dưới MA50 (21.172) và MA200 (25.417). **Cả 2 cổng VẪN CHƯA đóng, cổng (b) nay
  quá hạn 6 phiên:**
  (a) **kết quả lấy ý kiến bằng văn bản chọn đơn vị kiểm toán (10/08) — vẫn CHƯA công bố sau 11
  ngày.** WebSearch + WebFetch trang tin-tức-sự-kiện vietstock của TV1 đều không có bài kết quả
  (trang chi tiết bị paywall). Nền: cả 4 Big4 đã từ chối; đơn vị kiểm toán 2024 là **VACO**.
  ⚠️ Giữ nguyên cảnh báo §14: *"chưa thấy tin xấu" ≠ "đã qua cổng"*.
  (b) **cổ tức tiền mặt 15% (1.500đ/cp), ngày thanh toán công bố 14/08 — ĐO ĐƯỢC LÀ CHƯA VỀ.**
  Bằng chứng broker: `cashDividendReceiving` SpaceX 9.775.000 (16→19/08) → **8.920.000 (20/08)**,
  giảm **855.000**; ZaloPay 6.453.500 → **6.048.500**, giảm **405.000**. Cùng lúc `availableCash`
  tăng đúng 812.250 / 384.750 = **95% của khoản giảm** (khớp thuế cổ tức 5% tuyệt đối) ⇒ có MỘT
  khoản cổ tức được credit ngày 20/08, **nhưng KHÔNG PHẢI TV1**: TV1 15% trên 2.300cp phải là
  **3.450.000** (SpaceX) và **1.800.000** (ZaloPay), và tỷ lệ 855/2.300 ≠ 405/1.200 nên khoản vừa
  về cũng không cùng một mã theo tỷ lệ/cp. ⇒ **phép thử DDM §14 vẫn CHƯA có kết quả sau 6 phiên
  quá hạn** — đây là khoảng cách đáng chú ý nhất tuần này với case QUALIFY duy nhất đang giữ.
- **TV4** (AMBIGUOUS): **có tin mới THẬT, chiều XẤU, và giá đi ngược tin.** Giá bật **12.800 →
  13.800 (+7,8%) đúng phiên 20/08** (PB 1,04 · PE 6,21 · DY 7,2%). Trong khi đó: **Trưởng ban Kiểm
  soát nội bộ Nguyễn Thị Thanh Hoa từ nhiệm hiệu lực 01/08/2026**, PECC4 **đã thay TOÀN BỘ ban lãnh
  đạo** (miễn nhiệm CT HĐQT + TGĐ + PTGĐ + KTT sau khởi tố), và **ĐHĐCĐ bất thường bị HOÃN**.
  → Người kiểm soát nội bộ rời đi ngay TRƯỚC cổng soát xét bán niên là tín hiệu quản trị xấu, không
  phải trung tính. **Cổng nhị phân giữ nguyên và nay chỉ còn 9 ngày: ý kiến kiểm toán BCTC bán niên
  soát xét 2026, hạn ~30/08.** Không đổi phân loại; **giá tăng KHÔNG phải bằng chứng cổng sẽ mở**.
- **DGC** (§6, AMBIGUOUS-nghiêng-constructive · ZaloPay giữ 10.000cp, `excluded=True`): giá
  **41.400** (20/08), **thủng vùng 43-44 của tuần trước và làm đáy mới kể từ 21/07**; PB 0,97
  (**lần đầu dưới book** trong chuỗi theo dõi), PE 7,24, DY 7,2%, dưới MA50 (44.269) và rất xa MA200
  (61.288). **Không có tin MỚI trong cửa sổ** — mục "cổ phiếu bị kiểm soát" mà tìm kiếm trả về là
  tin **11/05/2026** (HOSE chuyển từ cảnh báo sang kiểm soát từ 13/05 do nộp BCTC kiểm toán 2025
  chậm >30 ngày), **không phải sự kiện tuần này** — ghi ra đây để lần quét sau không đếm nhầm là mới.
  Nền chưa đổi: khai trường 25 dừng vì điều tra, kế hoạch 2026 1.600 tỷ LNST (thấp nhất từ 2020),
  bù bằng Debt_Eq 0,19 · CR 5,21 · CF_OA_P0 2,8× NP · cam kết cổ tức 30% tiền mặt.
- **PNJ** (§7, AMBIGUOUS): **có dữ kiện mới THẬT và là dữ kiện GIẢM rủi ro — cần ghi cho cân bằng.**
  **Kết luận thanh tra Chính phủ về kinh doanh vàng đã ban hành 08/08** và PNJ đã công văn giải
  trình HOSE 09/08: sai phạm là **xác định giá vốn trên tờ khai thuế GTGT**, **PNJ đã TỰ rà soát từ 9/2025 và nộp
  bổ sung 9,999 tỷ đồng thuế GTGT + 973,4 triệu tiền chậm nộp ngay từ 11/11/2025** (trước khi kết
  luận ban hành), cho giai đoạn 1/2023-9/2025 — thời kỳ đã được thanh tra trước 2025. ⇒ **overhang thanh tra nay đã ĐƯỢC LƯỢNG HOÁ và ở mức không trọng
  yếu** (~11 tỷ so vốn hoá) — khác hẳn nỗi sợ "vi phạm chưa rõ quy mô". Giá phản ứng đúng chiều:
  34.850 (14/08) → **37.300 (20/08), +7,0%**, và **+21,3% trên đáy 30.750 (24/07)**.
  → **Không đổi AMBIGUOUS.** Rủi ro thật của PNJ chưa bao giờ là khoản thuế này mà là **Q2/2026 lỗ
  282,9 tỷ + CF_OA −1.568 tỷ + FSCORE 1** (nghĩa vụ mua lại hàng 5.900 tỷ). **Cổng vẫn là BCTC
  Q3/2026 (~cuối 10/2026)**, và giá đã bật 21% khỏi đáy nên biên an toàn để chờ cổng đã mỏng đi.

**Tổng kết tuần**: **29 mã đang gác** rà qua · 251 mã (anomaly_scan) + **693 mã** (quét rộng) + **14
truy vấn tin** · **0 QUALIFY mới** · 1 NON mới (SGT) · **1 AMBIGUOUS-yếu MỚI cần cổng (ICG)** · 2
không-phải-case (NTL, TIN) · 3 loại bằng bước lọc rẻ (VNZ/LLM/POM) · **watchlist KHÔNG quá hạn** ·
**0 lệnh mua trên cả 2 account phiên 21/08 ⇒ không có luận điểm mua nào bị gãy.**
**Mốc phải theo, gần → xa: TV1 kiểm toán + cổ tức (QUÁ HẠN 6 phiên, kiểm mỗi tuần) → ICG giải trình
HNX + soát xét bán niên ~30/08 → TV4 soát xét bán niên ~30/08 (9 ngày, + tín hiệu KSNB từ nhiệm) →
PNJ Q3 cuối 10/2026.**

Nguồn tuần này: [vietstock — SGT chào bán 148 triệu cp trả nợ / LNTT 6T −82,3%](https://finance.vietstock.vn/SGT-ctcp-cong-nghe-vien-thong-sai-gon.htm) ·
[vietstock — Lideco thắng lớn Q2 nhờ đầu tư chứng khoán, danh mục TCH 52%](https://vietstock.vn/2026/07/lideco-tiep-tuc-thang-lon-quy-2-nho-dau-tu-chung-khoan-danh-muc-co-gi-737-1473379.htm) ·
[tuoitre — 2 năm trắng doanh thu BĐS của Lideco](https://tuoitre.vn/2-nam-trang-doanh-thu-bat-dong-san-lideco-lay-gi-de-tra-nguoi-lao-dong-23-trieu-thang-20260406213130528.htm) ·
[vietstock — loạt DN bị huỷ giao dịch UPCoM tháng 8](https://vietstock.vn/2026/08/loat-doanh-nghiep-bi-huy-giao-dich-tren-upcom-trong-thang-8-830-1481382.htm) ·
[baomoi/Tạp chí Điện tử & Ứng dụng — PECC4 thay toàn bộ ban lãnh đạo, KSNB từ nhiệm 01/08](https://baomoi.com/sau-bien-co-phap-ly-pecc4-da-thay-toan-bo-ban-lanh-dao-c55703646.epi) ·
[nguoiquansat — TV4 tiếp tục "có biến"](https://nguoiquansat.vn/doanh-nghiep-quy-mo-400-ty-bi-dieu-tra-trong-vu-an-nganh-dien-tiep-tuc-co-bien-309527.html) ·
[thanhnien — PNJ lên tiếng về kết luận thanh tra (09/08)](https://thanhnien.vn/pnj-len-tieng-ve-ket-luan-thanh-tra-18526080915141617.htm) ·
[tuoitre — PNJ công bố thông tin bất thường sau kết luận Thanh tra Chính phủ](https://tuoitre.vn/pnj-cong-bo-thong-tin-bat-thuong-mi-hong-bao-tin-manh-hai-phat-thong-cao-sau-ket-luan-thanh-tra-10026080913063588.htm) ·
[tapchikinhtetaichinh — DGC chuyển sang diện kiểm soát từ 13/05 (tin CŨ, không phải tuần này)](https://tapchikinhtetaichinh.vn/hoa-chat-duc-giang-doi-mat-ap-luc-kep-tu-hoat-dong-kinh-doanh-va-co-phieu-bi-kiem-soat-155863.html) ·
[dnse — Vingroup tất toán 906,5 triệu USD trái phiếu quốc tế](https://www.dnse.com.vn/senses/tin-tuc/vingroup-tat-toan-9065-trieu-usd-trai-phieu-quoc-te-co-quyen-chuyen-doi-thanh-co-phieu-vic-vhm-vfs-33861216)

---

### 2026-08-24 — QUÉT SÁNG THỨ HAI (job `Taylor_20260824_010002`, mục đích: BẢO VỆ PHÍA MUA trước 09:00) — 0 case mới · 0 QUALIFY · 1 read-through có CATALYST THẬT (DGC gỡ 1 lý do cảnh báo, hiệu lực ĐÚNG hôm nay) · 1 corp-action trên mã đang giữ (EVF pha loãng)

Cửa sổ tin **21/08 → 23/08** (sau phiên thứ Sáu tới hết Chủ Nhật). Danh mục đang gác **29 mã**
(13 NH + 16 ngoài NH).

**Phần 1 — anomaly_scan** (`--backfill-days 3`): phiên cuối cache **2026-08-21**, universe **251 mã**
(H:29 / W:240), **watchlist TƯƠI** (`active_nav` computed_at 2026-08-21 = đúng phiên cuối) — KHÔNG
có cảnh báo quá hạn. **0 FLOOR2 · 0 IDIOCRASH · 0 CEIL2 · 0 VOLSPIKE** — không tín hiệu nào.
Cửa sổ chỉ có **1 phiên giao dịch mới** (21/08) vì lượt quét 08-21 đã phủ tới 20/08.

**Phần 2 — quét RỘNG** `bq_cache/ticker/2026.parquet`: 1.275 mã → **694 mã** đạt sàn thanh khoản
(`max(Close×Volume)` 2026 ≥1 tỷ), IDIOCRASH (ret ≤ −6% ∧ idio ≤ −5% ∧ val ngày ≥1 tỷ), phiên 21/08
→ **0 sự kiện**. Nới xuống ngưỡng mềm (ret ≤ −4% ∧ idio ≤ −3,5%) ra 25 mã nhưng **KHÔNG mã nào có
giá trị khớp ngày ≥1 tỷ** (cao nhất VNE 816tr; TCD −26,7% chỉ 316tr, DFF −20,0% chỉ 60tr) ⇒ toàn
bộ là penny thanh khoản mỏng, không đầu tư được, **0 ứng viên**.
⚠️ Bối cảnh phải đọc kèm: **VNINDEX 21/08 +1,95%** (1.734,24 → 1.768,12) nên `idio = ret − mret` bị
kéo xuống ~2pp cho MỌI mã — tức lượt này ngưỡng idio DỄ trip hơn bình thường mà vẫn 0 hit. Kết luận
"sạch" ở đây là kết luận CHẶT, không phải do gate lỏng.

**Phần 3 — WebSearch tin theo BỘ TỪ KHOÁ NHÓM (10 truy vấn + 1 WebFetch):**
- **Nhóm chung** (khởi tố/thanh tra/đình chỉ/hạn chế giao dịch/từ chối kiểm toán/huỷ niêm yết):
  **0 case NIÊM YẾT MỚI** trong cửa sổ. Mọi tên trả về đều đã có kết luận trước (PAT/DGC vụ Lưu Bách
  Đạt 22-23/07, PC1 **BANNED**, HBS/DVT hạn chế giao dịch từ đầu tháng).
- **Nhóm ngân hàng (13 mã)** — bổ sung §4.2 `bank_tailrisk_insurance_design_20260814.md`:
  **0 sự kiện.** Không kiểm soát đặc biệt / chuyển giao bắt buộc / rút tiền hàng loạt / khởi tố lãnh
  đạo NH niêm yết. Hit duy nhất trong cửa sổ là **cựu Phó GĐ chi nhánh Ngân hàng Hợp tác xã Thanh
  Hoá bị bắt 20/08** — pháp nhân KHÔNG niêm yết, không thuộc 13 mã đang gác, không read-through.
- **Nhóm BĐS đầu ngành/hạ tầng (VHM, VRE)** — §6 `vic_family_credit_concentration_20260818.md`:
  **0 sự kiện tín dụng mới.** Không có chậm/vỡ nợ trái phiếu, hạ bậc tín nhiệm, giải chấp/call
  margin cổ đông lớn, siết tài sản đảm bảo trong cửa sổ.
- **Nhóm ngoài NH (16 mã)** — tai nạn nhà máy / thu hồi sản phẩm / mất mỏ-giấy phép / kê biên /
  tranh chấp lãnh đạo: **0 sự kiện.**

**Phần 4 — PHÍA MUA (câu hỏi bắt buộc của lượt quét): KHÔNG có rủi ro luận-điểm-gãy.**
`plan_SpaceX_2026-08-24.json` và `plan_ZaloPay_2026-08-24.json` đều **0 orders** (HOLD_ALL cả 2
account). Lý do HOLD của SpaceX là **signal_hold chính sách** (BAL paper-track tới 2026-09-16),
KHÔNG phải thiếu tiền. Ứng viên mua duy nhất còn treo là **VPI** (BAL, RE_BACKLOG_BUY, weight 10%,
carry-forward phiên thứ 4 liên tiếp, nay nằm ở `deferred_orders[]` với `deferred_reason=signal_hold`).
→ **VPI KHÔNG có tin xấu nào trong cửa sổ** (giá 65.000 ngày 21/08, +2,36%). Nhưng ghi lại một dữ
kiện NỀN cần theo nếu VPI được kích hoạt mua sau 16/09, vì nó rơi đúng bộ từ khoá nhóm (c) đã duyệt
08-14: **dư nợ trái phiếu >2.584 tỷ so tiền mặt cuối Q1/2026 chỉ ~143 tỷ, ≥8 lô trái phiếu dùng
CHÍNH cổ phiếu VPI của lãnh đạo/bên liên quan làm tài sản đảm bảo** (cấu trúc "cầm cố cổ phiếu đảm
bảo nghĩa vụ trái phiếu" — cùng chữ ký rủi ro mà §6 VIC-family liệt kê). Đây là **nền, không phải
sự kiện tuần này**; và định giá hiện tại (PE 52,0 · PB 3,63) **không phải case fear-buy** — ghi ở
đây để lượt sau không phải tra lại từ đầu, KHÔNG phải khuyến nghị chặn lệnh.

**Phần 5 — read-through case đang theo dõi + mã đang giữ dính tin**

- **DGC** (§6, AMBIGUOUS-nghiêng-constructive · ZaloPay giữ 10.000cp, `excluded=True`): ★ **CÓ
  CATALYST THẬT, HIỆU LỰC ĐÚNG HÔM NAY 24/08.** HOSE **gỡ MỘT lý do cảnh báo** (Quyết định 567 ngày
  02/07 vì chưa họp ĐHĐCĐ thường niên đúng hạn) sau khi DGC **đã tổ chức ĐHĐCĐ 2026 ngày 13/08**.
  Giá phản ứng ngay: **41.400 (20/08) → 43.050 (21/08), +3,99%**, bật khỏi đáy tuần trước và trở lại
  **PB 1,01** (vừa trên book), PE 7,53.
  ⚠️ **Nhưng đây mới là gỡ 1/3, KHÔNG phải mở cổng.** DGC **VẪN**: (a) **hạn chế giao dịch** do chậm
  nộp BCTC kiểm toán 2025 quá 45 ngày; (b) **còn một diện cảnh báo KHÁC do kiểm toán ra Ý KIẾN NGOẠI
  TRỪ trên BCTC 2025** — dữ kiện này chưa từng ghi tường minh trong §6, và nó là gạch ❌ §2 (*"cáo
  buộc/nghi vấn làm con số BCTC mất giá trị"*) ở dạng nhẹ, phải mang theo khi đọc mọi số của DGC.
  ⇒ **Không đổi phân loại.** Cổng xác nhận thật của DGC vẫn là **BCTC kiểm toán 2025 nộp xong +
  ý kiến kiểm toán sạch**, không phải quyết định hành chính hôm nay.
- **TV1** (§4/§14/§13, QUALIFY — SpaceX 2.300cp + ZaloPay 1.200cp): giá **20.000** (21/08, +0,00%,
  KL 24.100), PB 1,06 · PE 3,46, vẫn dưới MA50 (21.118). **Cả 2 cổng VẪN CHƯA đóng; cổng (b) nay
  quá hạn 7 phiên:** (a) kết quả lấy ý kiến bằng văn bản chọn kiểm toán (thực hiện 10/08) — WebSearch
  + WebFetch trang vietstock TV1 đều **không có tin kết quả sau 14 ngày**; (b) cổ tức tiền mặt 15%
  vẫn chưa đo được là đã về. Giữ nguyên cảnh báo §14: *"chưa thấy tin xấu" ≠ "đã qua cổng"*.
- **TV4** (AMBIGUOUS): 14.000 (21/08, +1,45%), PB 1,06 · PE 6,30 — tiếp tục tăng, **+9,4% trong 2
  phiên** kể từ mức 12.800 ngày 19/08. **Không có tin mới trong cửa sổ.** Cổng nhị phân giữ nguyên và
  nay còn **~6 ngày**: **ý kiến kiểm toán BCTC bán niên soát xét 2026, hạn ~30/08**. Nhắc lại nguyên
  văn kết luận tuần trước vì giá đang đi ngược: **giá tăng KHÔNG phải bằng chứng cổng sẽ mở.**
- **PNJ** (§7, AMBIGUOUS): **39.900 (21/08, +6,97%, KL 4,04 triệu cp)** — phiên tăng mạnh nhất trong
  chuỗi theo dõi, **+29,8% trên đáy 30.750 (24/07)**. Không có tin mới trong cửa sổ (dữ kiện giảm
  rủi ro đã ghi tuần trước: kết luận thanh tra 08/08 lượng hoá ~11 tỷ, không trọng yếu). **Không đổi
  AMBIGUOUS**, nhưng ghi rõ hệ quả thực dụng: **biên an toàn để chờ cổng BCTC Q3/2026 (~cuối 10/2026)
  nay đã mỏng gần 30%** so với đáy — case này đang mất dần tính "mua khi sợ hãi" theo đúng nghĩa đen.
- **ICG** (AMBIGUOUS-yếu, mở 08-21): **11.200 (21/08, +3,70%)**, PB 0,63 · PE 7,58 — đã hồi 2 phiên
  liên tiếp sau chuỗi 4 phiên sàn. **KHÔNG tìm được công bố giải trình HNX** (WebSearch 1 truy vấn)
  ⇒ **cổng (a) vẫn treo**, cổng (b) BCTC bán niên soát xét ~30/08 còn ~6 ngày. Không đổi phân loại;
  chặn thanh khoản (vốn hoá ~190 tỷ) vẫn mạnh hơn mọi phân loại.
- **SGT** (NON, đóng 08-21): 8.570 (+3,13%). Không có gì đổi kết luận — PE 39,1 · PB 0,51, vẫn đúng
  hình "PB rẻ nhưng lõi không sinh tiền". Không theo tiếp.

**Phần 6 — 2 corp-action/CBTT trên mã ĐANG GIỮ (không phải case fear-buy, nhưng phải ghi ra):**
- **EVF** (đang giữ, nhóm ngoài NH): **ĐHĐCĐ bất thường 21/08 thông qua 3 nội dung** — (1) chào bán
  **riêng lẻ tối đa 85 triệu cp (+850 tỷ mệnh giá)**, vốn điều lệ 7.605 tỷ → tối đa ~**8.455 tỷ**
  (**pha loãng ~11,2%**), vốn thu về để cấp tín dụng giai đoạn 2027-2028; (2) **nới room ngoại lên
  50%**; (3) bổ sung thành viên độc lập HĐQT. **Đọc theo khung**: đây là tăng vốn TĂNG TRƯỞNG (giá
  21/08 12.550, +2,03%, PB 0,92), **KHÔNG phải "pha loãng ở đáy để sống sót"** — tức KHÔNG chạm gạch
  ❌ §2.5. Nới room 50% là chiều dương cho dòng vốn ngoại. **Không escalate**; theo dõi giá phát hành
  riêng lẻ khi công bố (phát hành dưới book ở PB 0,92 sẽ là pha loãng giá trị sổ sách thật).
  ⚠️ Một dữ kiện nền đáng nhớ cho §6 (khoảng trống "exposure tài chính → BĐS" đã nêu 08-22): báo chí
  cùng đợt ghi EVF **rót >11.369 tỷ vào bất động sản** — nếu sau này dựng thước đo exposure BĐS của
  nhóm NH/tài chính thì EVF là mẫu quan sát được, không phải hộp đen.
- **CTG** (đang giữ, nhóm NH): CBTT **bất thường** về HĐQT thông qua hợp đồng mua bán tài sản **qua
  đấu giá giữa VietinBank và người có liên quan của thành viên nội bộ** (21/08). Là giao dịch bên
  liên quan có cơ chế đấu giá công khai — **không phải sự kiện tail-risk §4.2**, không escalate; ghi
  để lượt sau không đếm nhầm là tin mới.

**Tổng kết**: **29 mã đang gác** rà qua · 251 mã (anomaly_scan) + **694 mã** (quét rộng) + **10 truy
vấn tin + 1 WebFetch** · **0 case mới · 0 QUALIFY mới · 0 NON mới** · **watchlist KHÔNG quá hạn** ·
**0 lệnh mua trên cả 2 account phiên 24/08 ⇒ KHÔNG có luận điểm mua nào bị gãy.**
**Mốc phải theo, gần → xa: TV4 soát xét bán niên ~30/08 (~6 ngày) + ICG soát xét bán niên ~30/08 →
TV1 kiểm toán + cổ tức (QUÁ HẠN 7 phiên, kiểm mỗi tuần) → DGC nộp BCTC kiểm toán 2025 + ý kiến sạch
(gỡ hạn chế giao dịch; hôm nay MỚI gỡ được lý do cảnh báo ĐHĐCĐ) → PNJ Q3 cuối 10/2026.**

Nguồn lượt này: [vietstock — HOSE gỡ một lý do cảnh báo, cổ phiếu DGC vẫn kẹt trong diện hạn chế giao dịch](https://vietstock.vn/2026/08/hose-go-mot-ly-do-canh-bao-co-phieu-dgc-van-ket-trong-dien-han-che-giao-dich-830-1483695.htm) ·
[cafef — Tin vui cho cổ đông Hoá chất Đức Giang (21/08)](https://cafef.vn/tin-vui-cho-co-dong-hoa-chat-duc-giang-188260821150111887.chn) ·
[baodautu — EVF nới room ngoại lên 50%, tăng vốn và kiện toàn bộ máy](https://baodautu.vn/evf-noi-room-ngoai-len-50-tang-von-va-kien-toan-bo-may-d679205.html) ·
[antt — EVF chào bán riêng lẻ 85 triệu cp, tăng vốn thêm 850 tỷ](http://antt.vn/evf-du-kien-chao-ban-rieng-le-85-trieu-co-phieu-tang-von-them-850-ty-dong-404249.htm) ·
[vietstock — Nhịp đập Thị trường 21/08 (VN-Index bứt phá, khối ngoại mua ròng)](https://vietstock.vn/2026/08/nhip-dap-thi-truong-2108-khoi-ngoai-quay-lai-mua-rong-vn-index-but-pha-cung-thanh-khoan-hoi-phuc-1636-1483481.htm) ·
[dantri — TV1 bị cả 4 Big4 từ chối kiểm toán, lấy ý kiến cổ đông 10/08](https://dantri.com.vn/kinh-doanh/chu-tich-vua-bi-bat-cong-ty-dien-bi-ca-4-ben-big-4-tu-choi-kiem-toan-20260701145835409.htm) ·
[docnhanh — bắt cựu Phó GĐ Ngân hàng Hợp tác xã CN Thanh Hoá 20/08 (KHÔNG niêm yết)](https://docnhanh.vn/phap-luat/thanh-hoa-bat-tam-giam-cuu-pho-giam-doc-ngan-hang-bi-cao-buoc-chiem-doat-65-ty-dong-tintuc1049408)

---

### 2026-08-28 (job `Taylor_20260828_011001`) — 0 QUALIFY mới · **2 NON mới (LDP, VTD)** · 1 không-phải-case (PDN) · 5 read-through · ★ **TV1: cổ tức 15% CHƯA TỪNG được broker book làm khoản phải thu** (đo được, không phải suy đoán)

Cửa sổ tin **21/08 → 27/08** (5 phiên). Danh mục đang gác **29 mã** (13 NH + 16 ngoài NH).

**Bối cảnh thị trường phải đọc kèm**: VNINDEX **1.734,24 (20/08) → 1.831,56 (27/08), +5,6%**, vượt
1.750 và 1.800 trong cùng tuần; DT5G `macro_health` **HEALTHY**, state **3 = NEUTRAL**, `market_stress
= false` (VIX không cao, VNI trên MA200). ⇒ Đây là tuần **thị trường tăng mạnh** — pool fear-buy hẹp
lại theo cấu trúc, và vì `idio = ret − mret` bị kéo xuống ~1pp/phiên nên ngưỡng IDIOCRASH **DỄ trip
hơn** bình thường. Kết luận "sạch" ở đây là kết luận CHẶT, không phải do gate lỏng (cùng lập luận
08-24).

**Phần 1 — anomaly_scan** (`--backfill-days 8`): phiên cuối cache **2026-08-27**, universe **253 mã**
(H:29 / W:242), **watchlist TƯƠI** (`active_nav` computed_at 2026-08-27 = đúng phiên cuối) — **KHÔNG
có cảnh báo quá hạn**. **0 IDIOCRASH · 0 FLOOR2.** Cờ duy nhất trong 8 phiên là cờ **TĂNG**: **PNJ
`CEIL2` 24/08** (+6,9%, idio +5,7%, 48,8 tỷ giá trị) — thuộc case đang theo dõi, xem Phần 5.
⇒ **không mã nào trong 29 mã đang gác bị sập riêng lẻ.**

**Phần 2 — quét RỘNG** `bq_cache/ticker/2026.parquet`: 1.276 mã → **696 mã** đạt sàn thanh khoản
(`max(Close×Volume)` 2026 ≥1 tỷ). IDIOCRASH cứng (ret ≤ −6% ∧ idio ≤ −5% ∧ val ngày ≥1 tỷ), 5 phiên
21→27/08 → **2 sự kiện / 2 mã**; nới ngưỡng mềm (ret ≤ −4% ∧ idio ≤ −3,5%) → 13 sự kiện / 11 mã.
Chuỗi chỉ số lấy từ `ticker='VNINDEX'`, **không** dùng cột mirror (bẫy 08-17 Phần 7).

Áp các bước lọc rẻ TRƯỚC khi kéo tài chính:

| Bước lọc | Loại | Vì sao |
|---|---|---|
| Đã có kết luận trước đó | **F88** (không-phải-case 08-14), **TIN**, **NTL** (không-phải-case 08-21) | Xem Phần 5b |
| Vị-trí-giá 3M (thêm 08-14) | **SBB** (+7,5% trên đáy 3M, chỉ −7,0% so đỉnh), **HDA** (+16,9% trên đáy), **SBS** (+4,7%), **NRC** (+6,5%), **BKG** (+1,1% nhưng xem dưới) | Không ở vùng sợ hãi |
| Sàn thanh khoản thực (ADV 3M) | **SBB** 0,47 tỷ · **HDA** 0,23 tỷ · **BKG** 0,59 tỷ · **PDN** 0,66 tỷ | Dưới mọi ràng buộc thanh khoản đã dùng cho TV1 |
| Lõi hỏng hiển nhiên (§10.10) | **TTF** (Debt_Eq **22,0** · BVPS **276đ** · NP_P0 **−209,7 tỷ** · PB 6,17 — vốn chủ gần như bị xoá) · **BKG** (PB 0,18 nhưng PE 23,4, CF_OA_P0 −24,9 tỷ, FSCORE 3 — bẫy giá trị kinh điển) · **SBS** (ROE_Min3Y −22,6%, CF_OA_P0 −50,3 tỷ) · **NRC** (ROE_Min3Y −12,7%, CF_OA_P0 ≈0, Risk_Rating 4) | Trượt §2#3/#4 tường minh |
| Số phiên có KL trong 5 phiên (thêm 08-17, ca POM) | *không loại mã nào lượt này* — **cả LDP và VTD đều 5/5 phiên có KL** ⇒ cú rơi là THẬT, không phải cờ giả do hạn chế giao dịch | |

⇒ còn **3 mã đáng chấm, cả 3 CHƯA từng phân loại** (grep lịch sử case: 0 hit):

| Mã | Giá 27/08 | Vị trí & chữ ký sự kiện | Số chặn / số đỡ | Kết luận |
|---|---|---|---|---|
| **LDP** (Dược Lâm Đồng — Ladophar, HNX, ICB 4577) | **7.100** (−26,8% so đỉnh 3M, **đúng đáy 3M**), phiên 27/08 **−8,97%** với **KL 154.800 = ~48× nền** (3.200→12.000→20.300→154.800) | PB **0,69** (BVPS 10.319) · PE 4,74 · Debt_Eq 0,64 · Cash_P0 16,8 tỷ (~27% vốn hoá) | **BCTC hợp nhất 2024 VÀ 2025 đều bị kiểm toán ra Ý KIẾN NGOẠI TRỪ** (2 năm liên tiếp) ⇒ cổ phiếu đang ở **diện kiểm soát** + **diện cảnh báo** (chưa họp ĐHĐCĐ thường niên quá 6 tháng) · **CF_OA_P0 = −2,86 tỷ trong khi NP_P0 = +0,83 tỷ** ⇒ **trượt thẳng §2#3 (CF_OA ≥ NP)** · FSCORE **2** · ROE_Min3Y −19,6% · PCF 31,7 · DY 0 · **đang có tranh chấp quyền kiểm soát**: công ty ra cảnh báo về nhóm tự nhận sở hữu **54% cổ phần** đi vận động uỷ quyền dự ĐHĐCĐ; chủ tịch liên tục thoái vốn · ADV3M **0,70 tỷ** | **NON** — gạch ❌ §2 tường minh (*"nghi vấn làm con số BCTC mất giá trị"*): **PB 0,69 không phải sàn định giá khi chính book value nằm dưới ý kiến ngoại trừ 2 năm liền**. Đã kiểm góc tài sản/dòng tiền theo bài học TV1/DGC (§3 dispatch): không có tài sản lõi tách rời định giá được, tiền mặt 16,8 tỷ không bù được CF_OA âm + tranh chấp kiểm soát chưa ngã ngũ |
| **VTD** (Vietourist Holdings, UPCoM, ICB 5759 — lữ hành) | **4.500** (−16,7% so đỉnh 3M, **+2,3% trên đáy**), phiên 25/08 **−6,25%** (2,19 tỷ giá trị) | PB **0,40** (BVPS 11.259) · Debt_Eq 0,33 · FSCORE 5 · Risk_Rating 2 | **PE 18,07** (NP_P0 chỉ 5,8 tỷ trên vốn điều lệ 240 tỷ ⇒ sức sinh lời không đáng kể) · **`CF_OA_P0` = NaN trong BQ ⇒ KHÔNG chấm được §2#3**, mà §2#3 là tiêu chí quyết định · ROE_Min3Y −3,7% · **phát hành thêm cổ phiếu để TRẢ NỢ NGÂN HÀNG, nợ tăng gấp 3 trong 3 năm**; đợt phát hành cho cổ đông hiện hữu giá **10.000đ** trong khi thị giá **4.500đ** | **NON** — **đúng chữ ký SGT (đã kết luận NON 08-21)**: gạch ❌ §2.5 *"DN bị buộc bán tài sản/pha loãng ở đáy"*, phát hành **dưới thị giá 2,2×**. PB 0,40 không cứu được khi không chứng minh được lõi sinh tiền |
| **PDN** (Cảng Đồng Nai, HOSE) | **88.700** (−18,6% so đỉnh 3M, **đúng đáy 3M**), phiên 25/08 −4,90% | Lõi **TỐT thật**: ROE_Min3Y **31,0%** · CF_OA_P0 130,5 tỷ ≈ 0,93× NP_P0 140,1 tỷ · Debt_Eq 0,35 · FSCORE 6 · DY 2,3% | **PB 3,32** ⇒ trượt thẳng §2#5 (**không có sàn định giá**) · ADV3M **0,66 tỷ** (không đầu tư được ở quy mô này) | **Không phải case** — doanh nghiệp tốt bị chiết khấu, KHÔNG phải doanh nghiệp tốt bị định giá dưới giá trị. Ghi ra vì nó là mã duy nhất trong nhóm soft có lõi sạch; nếu PB về ≲1,5 thì đáng mở lại |

**Phần 3 — WebSearch tin theo BỘ TỪ KHOÁ NHÓM (12 truy vấn):**
- **Nhóm chung** (khởi tố/bắt tạm giam/thanh tra/đình chỉ/hạn chế giao dịch/từ chối kiểm toán/chậm nộp
  BCTC/cắt margin/huỷ niêm yết): **0 case NIÊM YẾT MỚI** liên quan danh mục gác. Hai ghi nhận nền:
  (a) **HBS** (Chứng khoán Hoà Bình) — HNX ra quyết định **25/08**, **đình chỉ giao dịch ~33 triệu cp
  từ 03/09** do tiếp tục vi phạm CBTT sau khi đã bị hạn chế giao dịch. Là **leo thang thật trong cửa
  sổ** của mã đã ghi nền 08-24; **không thuộc 29 mã gác**, và bản thân vi phạm CBTT liên tục là gạch
  ❌ §2 ⇒ không mở case. (b) Danh sách **59 mã HOSE cắt margin quý III/2026** (công bố 02/07, trong đó
  có **DGC**) là tin CŨ — ghi ra để lượt sau không đếm nhầm là mới; danh sách quý IV sẽ ra đầu 10/2026.
- **Nhóm ngân hàng (13 mã)** — bổ sung §4.2 `bank_tailrisk_insurance_design_20260814.md`:
  **0 sự kiện.** Không kiểm soát đặc biệt / chuyển giao bắt buộc / rút tiền hàng loạt / khởi tố lãnh
  đạo NH niêm yết / cho vay sân sau / thao túng cổ phiếu NH trong cửa sổ. Kết quả trả về chỉ là nền
  2023-2024 (4 NH đã chuyển giao xong) + ca Thanh Hoá 20/08 đã ghi tuần trước (pháp nhân KHÔNG niêm yết).
- **Nhóm BĐS đầu ngành/hạ tầng (VHM, VRE — và VIC/VPI ở phía mua)** — §6
  `vic_family_credit_concentration_20260818.md`: **0 sự kiện tín dụng XẤU mới.** Không chậm/vỡ nợ trái
  phiếu, không hạ bậc tín nhiệm, không siết tài sản đảm bảo, không call margin cổ đông lớn. Chiều
  **ngược lại** trong cửa sổ: **VIC dẫn đầu mua ròng khối ngoại phiên 25/08 với 361,9 tỷ**, và theo
  SSI Research VIC là mã nhận phân bổ thụ động lớn nhất (~689,7 triệu USD) khi dòng vốn FTSE giải ngân.
  Nền đã biết, KHÔNG phải tin mới: 2 lô trái phiếu VHM dùng cổ phiếu VIC làm tài sản đảm bảo (40 triệu cp).
- **Nhóm ngoài NH (16 mã)** — tai nạn/sự cố nhà máy, thu hồi sản phẩm, mất giấy phép/mỏ, kê biên tài
  sản, tranh chấp lãnh đạo: **0 sự kiện.**

**Phần 4 — PHÍA MUA (câu hỏi bắt buộc của lượt quét): KHÔNG có luận điểm mua nào bị gãy.**
`plan_SpaceX_2026-08-28.json` và `plan_ZaloPay_2026-08-28.json` đều **0 orders**. Rổ ứng viên mua
duy nhất = **2 lệnh BAL đang `deferred`** vì `signal_hold` (user quyết định 19/08, giữ tới checkpoint
**2026-09-16**): **VPI** (case gốc) và **VIC** (mới vào diện hold, cùng luật `book=BAL, side=buy`).
- **VIC**: 0 tin xấu trong cửa sổ; dữ kiện duy nhất là chiều DƯƠNG (khối ngoại mua ròng 361,9 tỷ 25/08,
  dòng FTSE sắp giải ngân). **Luận điểm không gãy.**
- **VPI**: 0 tin xấu trong cửa sổ. Giữ nguyên dữ kiện NỀN đã ghi 08-24 (dư nợ trái phiếu >2.584 tỷ vs
  tiền mặt ~143 tỷ cuối Q1/2026, ≥8 lô dùng CHÍNH cổ phiếu VPI của lãnh đạo/bên liên quan làm TSĐB) —
  **nền, không phải sự kiện tuần này**, và không có diễn biến mới làm nó xấu đi.
⇒ Không cần hành động phía mua.

**Phần 5 — read-through case đang theo dõi (1 có dữ kiện MỚI ĐO ĐƯỢC, 4 chỉ có giá)**

- ★ **TV1** (§4/§14, **QUALIFY** — SpaceX 2.300cp + ZaloPay 1.200cp): giá **20.400** (27/08), PE 3,53 ·
  PB 1,08, vẫn dưới MA50 (20.958) và rất xa MA200 (25.348). **Dữ kiện mới quan trọng nhất tuần này —
  và nó MẠNH HƠN kết luận 3 tuần trước, không phải lặp lại:**
  **Cổ tức tiền mặt 15% (1.500đ/cp, ngày thanh toán công bố 14/08) CHƯA TỪNG được DNSE ghi nhận là
  khoản phải thu.** Bằng chứng: phân rã `cashDividendReceiving` khớp TUYỆT ĐỐI, không dư đồng nào —

  | Ngày | SpaceX `divRecv` | ZaloPay `divRecv` | Cấu phần |
  |---|---:|---:|---|
  | 20/08 (số dư đầu cửa sổ) | 8.920.000 | 6.048.500 | = SAB + NCT + (khoản C) |
  | 25/08 (chi trả) | −4.000.000 | −2.984.000 | **NCT 8.000đ/cp** — khớp CHÍNH XÁC 500cp / 373cp |
  | 27/08 (chi trả) | −1.620.000 | −832.500 | khoản C, tỷ lệ **72:37** — **KHÔNG khớp TV1 (23:12)**, gần DRI (3.700:1.900) nhất |
  | **28/08 (còn lại)** | **3.300.000** | **2.232.000** | **SAB 3.000đ/cp** — khớp CHÍNH XÁC 1.100cp / 744cp |

  Cả hai chiều đều đóng: 3.300.000 + 4.000.000 + 1.620.000 = **8.920.000** ✓ và 2.232.000 + 2.984.000
  + 832.500 = **6.048.500** ✓. TV1 15% phải là **3.450.000 (SpaceX) / 1.800.000 (ZaloPay)** — không có
  mặt ở BẤT KỲ ô nào. ⇒ Đây không còn là *"chưa đo được là đã về"* (kết luận 08-21 và 08-24) mà là
  **"broker chưa từng book nó làm khoản phải thu"** — nghĩa là TV1 chưa thực hiện chi trả, đã **quá
  hạn ~9 phiên** kể từ công bố 14/08. Đồng thời cổng (a) **kết quả lấy ý kiến bằng văn bản chọn đơn vị
  kiểm toán (thực hiện 10/08) vẫn CHƯA công bố sau 17 ngày** (WebSearch không có bài kết quả).
  → **Không đổi phân loại QUALIFY** (§14 vẫn đứng: lõi tách biệt, CF_OA≥NP, solvent, PE 3,5).
  Nhưng **phép thử DDM §14 — "SOE có ép chia được tiền ra không" — nay đã có tín hiệu NGƯỢC chiều đầu
  tiên đo được bằng số**, chứ không chỉ là im lặng. Đây là dữ kiện đáng escalate nhất lượt này.
- **PNJ** (§7, AMBIGUOUS): **41.900 (27/08)**, PE 7,40 · PB 1,54 · DY 5,7%; **+36,3% trên đáy 30.750
  (24/07)**, tuần qua +10,2%. Cờ `CEIL2` 24/08 (+6,9%, KL lớn) là cờ TĂNG. **Không có tin mới trong
  cửa sổ** (dữ kiện giảm rủi ro — kết luận thanh tra 08/08 lượng hoá ~11 tỷ, không trọng yếu — đã ghi
  08-21). **Không đổi AMBIGUOUS**, nhưng nhắc lại hệ quả thực dụng đã cảnh báo tuần trước và nay mạnh
  hơn: **biên an toàn để chờ cổng BCTC Q3/2026 (~cuối 10/2026) đã mỏng đi 36%** — case này **đã hết
  tính "mua khi sợ hãi"** theo đúng nghĩa đen; nếu chưa vào thì cửa sổ giá đã đóng, phần còn lại là
  cược vào cổng Q3 ở giá không còn chiết khấu.
- **DGC** (§6, AMBIGUOUS-nghiêng-constructive · ZaloPay giữ 10.000cp, `excluded=True`): **43.200
  (27/08)**, PE 7,56 · PB **1,01** · DY 6,9%; đi ngang quanh MA50 (43.908) sau cú bật 21/08, đỉnh tuần
  44.950 (25/08). **Không có tin mới trong cửa sổ** — mọi kết quả tìm kiếm về "hạn chế giao dịch" đều
  là tin **tháng 5/2026** (hạn chế từ 26/05 do chậm nộp BCTC kiểm toán 2025 >45 ngày), **không phải sự
  kiện tuần này**. Cổng xác nhận thật giữ nguyên: **nộp xong BCTC kiểm toán 2025 + ý kiến SẠCH** (nhắc
  lại dữ kiện 08-24: DGC còn một diện cảnh báo do **ý kiến NGOẠI TRỪ** trên BCTC 2025 — phải mang theo
  khi đọc mọi con số DGC).
- **TV4** (AMBIGUOUS): ⚠️ **KHÔNG có phiên giao dịch nào trong 25→27/08** — dòng cuối trong cache là
  **24/08 với KL 200cp** (13.600, PE 6,12 · PB 1,02). Mã gần như ngừng khớp sau cú bật 19→21/08
  (12.800 → 14.000). Không có tin mới. **Cổng nhị phân nay chỉ còn ~2 ngày: ý kiến kiểm toán BCTC bán
  niên soát xét 2026, hạn ~30/08.** Giữ nguyên cảnh báo 08-21: KSNB từ nhiệm ngay trước cổng + đã thay
  toàn bộ ban lãnh đạo; **giá tăng KHÔNG phải bằng chứng cổng sẽ mở**, và nay thanh khoản cạn càng làm
  giá mất giá trị thông tin.
- **ICG** (AMBIGUOUS-yếu, mở 08-21): **11.000 (27/08)**, PB 0,62 · PE 7,44, +2,8% trên mức 10.700 giữa
  tuần, vốn hoá ~234 tỷ. **Vẫn KHÔNG tìm được công bố giải trình HNX** về chuỗi 4 phiên sàn 14→19/08
  ⇒ **cổng (a) treo sang tuần thứ 2**. Cổng (b) BCTC bán niên soát xét ~30/08 còn ~2 ngày. Không đổi
  phân loại; chặn thanh khoản vẫn mạnh hơn mọi phân loại.

**Phần 5b — 3 mã trong danh sách soft đã có kết luận trước, chỉ echo:**
**F88** (không-phải-case 08-14): 65.800, PB **5,08**, ROE_Min3Y 22,6% — vẫn lãi kỷ lục, không có nỗi
sợ để mua; giá đã −24,8% so đỉnh 3M nhưng PB 5,08 nghĩa là chưa có sàn định giá. **TIN** (không-phải-
case 08-21): 107.900, PB 3,41 — không đổi. **NTL** (không-phải-case 08-21): 12.800 — không đổi, vẫn
là proxy có đòn bẩy của TCH.

**Tổng kết tuần**: **29 mã đang gác** rà qua · 253 mã (anomaly_scan) + **696 mã** (quét rộng) + **12
truy vấn tin** · **0 QUALIFY mới** · **2 NON mới (LDP, VTD)** · 1 không-phải-case (PDN) · 8 loại bằng
bước lọc rẻ · **watchlist KHÔNG quá hạn** (computed_at 2026-08-27 = đúng phiên cuối) · **0 lệnh mua
trên cả 2 account phiên 28/08, 2 ứng viên BAL (VIC, VPI) đang hold tới 16/09 và cả hai đều 0 tin xấu
⇒ KHÔNG có luận điểm mua nào bị gãy.**
**Mốc phải theo, gần → xa: TV4 + ICG soát xét bán niên ~30/08 (~2 ngày) → TV1 cổ tức + kiểm toán
(cổ tức nay CHỨNG MINH ĐƯỢC là chưa được book, quá hạn ~9 phiên; kiểm toán quá hạn 17 ngày) → DGC nộp
BCTC kiểm toán 2025 + ý kiến sạch → HBS đình chỉ giao dịch 03/09 (ngoài danh mục, chỉ ghi nền) →
checkpoint BAL paper-track 16/09 → PNJ Q3 cuối 10/2026.**

Nguồn lượt này: [kinhdoanhnet — LDP duy trì diện cảnh báo, BCTC 2024/2025 ý kiến ngoại trừ](https://kinhdoanhnet.vn/co-phieu-cua-ladophar-ldp-tiep-tuc-bi-duy-tri-dien-canh-bao-quy-i2026-lai-gan-936-trieu-dong-a79900.html) ·
[cafef — Ladophar lên lộ trình khắc phục tình trạng chứng khoán bị cảnh báo](https://cafef.vn/ladophar-len-lo-trinh-khac-phuc-tinh-trang-chung-khoan-bi-canh-bao-188260727111538457.chn) ·
[vietbao — Ladophar cảnh báo nhóm tự nhận sở hữu 54% vận động uỷ quyền dự ĐHĐCĐ](https://vietbao.vn/ladophar-canh-bao-thong-tin-van-dong-uy-quyen-du-hop-dhdcd-tu-nhom-tu-nhan-so-huu-54-co-phan-592856.html) ·
[congluan — Vietourist (VTD) phát hành thêm cổ phiếu để trả nợ ngân hàng, nợ tăng gấp 3 trong 3 năm](https://congluan.vn/vietourist-vtd-phat-hanh-them-co-phieu-de-tra-no-ngan-hang-no-tang-gap-3-trong-3-nam-hoat-dong-post175645.html) ·
[cafef — 33 triệu cp HBS bị đình chỉ giao dịch từ 03/09 (quyết định 25/08)](https://cafef.vn/dung-1-tuan-nua-hang-chuc-trieu-co-phieu-chung-khoan-nay-bi-dinh-chi-giao-dich-188260826134329745.chn) ·
[vietstock — HBS duy trì diện hạn chế giao dịch từ 12/08](https://vietstock.vn/2026/08/tiep-tuc-vi-pham-cong-bo-thong-tin-co-phieu-hbs-duy-tri-dien-han-che-giao-dich-tu-1208-830-1478564.htm) ·
[cafef — 59 mã bị HOSE cắt margin quý III/2026 (tin CŨ 02/07, có DGC)](https://cafef.vn/hose-cong-bo-59-ma-chung-khoan-bi-cat-margin-trong-quy-iii-2026-188260705145437452.chn) ·
[thoibaotaichinhvietnam — khối ngoại gom mạnh VIC trước dòng vốn nâng hạng (mua ròng 361,9 tỷ phiên 25/08)](https://thoibaotaichinhvietnam.vn/khoi-ngoai-gom-manh-co-phieu-vingroup-truoc-them-dong-von-nang-hang-202896.html) ·
[24hmoney — xếp hạng tín nhiệm đánh giá việc Vinhomes dùng 40 triệu cp VIC thế chấp (nền)](https://24hmoney.vn/news/to-chuc-xep-hang-tin-nhiem-danh-gia-ra-sao-khi-vinhomes-dung-40-trieu-co-phieu-vic-the-chap-c4a2787660.html) ·
[vietstock — Vietstock Weekly 24-28/08/2026 (VN-Index +2,26% tuần, vượt 1.750)](https://vn.investing.com/news/stock-market-news/vietstock-weekly-2428082026-tim-lai-dong-luc-2697760) ·
[tuoitre — DGC bị hạn chế giao dịch từ 26/05 (tin CŨ, không phải tuần này)](https://tuoitre.vn/co-phieu-hoa-chat-duc-giang-bi-han-che-giao-dich-tu-26-5-20260520100619702.htm) ·
[vietnambiz — PNJ (nền, tham chiếu giá)](https://vietnambiz.vn/co-phieu-pnj-duoc-giai-cuu-2026727143946827.htm)

---

### 2026-08-31 — QUÉT SÁNG THỨ HAI (job `Taylor_20260831_010002`, mục đích: BẢO VỆ PHÍA MUA) — **0 QUALIFY · 1 NON mới (BNA) · 2 không-phải-case (VIT, DHD)** · ★ **thị trường NGHỈ LỄ 31/08→02/09, phiên kế tiếp 03/09 ⇒ bot KHÔNG đặt lệnh sáng nay** · ★ **0 lệnh mua trên MỌI kênh cho phiên 03/09**

Cửa sổ tin **sau phiên 28/08 → hết CN 30/08**. Danh mục đang gác **29 mã** (13 NH + 16 ngoài NH).

**⚠️ Dữ kiện đổi ý nghĩa cả lượt quét — HÔM NAY KHÔNG CÓ PHIÊN.** `filter_lag_entry_window.py --account
SpaceX --json` trả `plan_date = 2026-09-03` với `calendar_check.ok=true` (signal_date 2026-08-28) ⇒
31/08, 01/09, 02/09 là **nghỉ lễ Quốc khánh 2/9**; phiên kế tiếp **Thứ Năm 03/09**. Mục đích "phủ
khoảng trống tin trước khi bot 09:05 đặt lệnh" vì vậy áp cho **03/09**, không phải hôm nay — và cửa sổ
tin thực tế sẽ còn 3 ngày nữa chưa được phủ (31/08→02/09), cần quét lại tối 02/09 trước khi plan
03/09 được thực thi. Đây là **khoảng trống thật**, không phải đã đóng bằng lượt này.

**Bối cảnh thị trường**: VNINDEX **1.832,12 (28/08)**, **7 phiên tăng liên tiếp**, tuần 24–28/08 khối
ngoại **mua ròng >1.100 tỷ** (tâm điểm **TCB** — mã đang gác). DT5G state **3 = NEUTRAL**, base_dt4 ==
macro_dt5g, không macro cap. ⇒ Vẫn là chế độ **thị trường tăng** ⇒ pool fear-buy hẹp theo cấu trúc và
ngưỡng IDIOCRASH dễ trip hơn (`idio = ret − mret` bị kéo xuống); kết luận "sạch" ở đây là kết luận
CHẶT, không do gate lỏng — cùng lập luận 08-24 và 08-28.

**Phần 1 — anomaly_scan**: phiên **2026-08-28**, universe **253 mã** (H:29 / W:242), **watchlist TƯƠI**
(`active_nav` computed_at **2026-08-28** = đúng phiên cuối) ⇒ **KHÔNG có cảnh báo quá hạn**.
**0 IDIOCRASH · 0 FLOOR2 · 0 CEIL2 · 0 VOLSPIKE** — không mã nào trong 29 mã gác bị sập riêng lẻ.

**Phần 2 — quét RỘNG** `bq_cache/ticker/2026.parquet` (phiên cuối 28/08, đúng 1 phiên MỚI kể từ quét
tuần 08-28): 1.276 mã → **697 mã** đạt sàn thanh khoản (`max(Close×Volume)` 2026 ≥1 tỷ). Chuỗi chỉ số
lấy từ `ticker='VNINDEX'`, **không** dùng cột mirror (bẫy 08-17). IDIOCRASH cứng (ret ≤ −6% ∧ idio ≤
−5% ∧ val ≥1 tỷ) → **3 mã**; nới mềm (ret ≤ −4% ∧ idio ≤ −3,5%) → thêm **1 mã**.

| Mã | Giá 28/08 | Chữ ký sự kiện | Kết luận |
|---|---|---|---|
| **BNA** (Tập đoàn Đầu tư Bảo Ngọc — bánh kẹo, HNX, ICB 3577) | **2.100** (−66,1% so đỉnh 3M, **đúng đáy 3M**), phiên 28/08 **−8,70%**, KL 698.400 (≈4× nền) | ★ **CHỈ GIAO DỊCH PHIÊN THỨ SÁU** — 8 phiên gần nhất đều là Thứ Sáu (10/07, 17/07, 24/07, 31/07, 07/08, 14/08, 21/08, 28/08), 14/30 phiên lịch có KL. **Hạn chế giao dịch từ 20/05/2026** do chậm nộp BCTC kiểm toán 2025 **>45 ngày**; **diện kiểm soát** (chậm >30 ngày); **diện cảnh báo từ 10/07** (chưa họp ĐHĐCĐ quá 6 tháng). Nợ vay + thuê tài chính **731 tỷ** cuối Q1/2026 (ngắn hạn **604 tỷ**), HĐQT thông qua vay + bảo lãnh thêm **261,6 tỷ**; chi phí tài chính **+61% lên ~67 tỷ/quý** trong khi LNST Q1 chỉ ~3 tỷ. Số BQ: **NP_P0 −8,51 tỷ · CF_OA_P0 −49,73 tỷ · Debt_Eq 1,99 · DY 0 · ADV3M 0,57 tỷ** | **NON** — hai gạch ❌ §2 độc lập nhau. (1) **Cờ IDIOCRASH là cờ GIẢ về mặt cơ học** — đúng bài học POM (08-17): mã chỉ khớp 1 phiên/tuần thì một phiên Thứ Sáu gộp cả tuần tin, `ret` không so được với mã giao dịch hằng ngày. (2) **PB 0,115 KHÔNG phải sàn định giá** vì chính book value nằm dưới BCTC kiểm toán 2025 **chưa từng được nộp** — cùng chữ ký LDP (08-28). Đã kiểm góc tài sản/dòng tiền theo bài học TV1/DGC: không có tài sản lõi tách rời định giá được, **CF_OA −49,7 tỷ đối đầu nợ ngắn hạn 604 tỷ** là bài toán thanh khoản, không phải bài toán định giá |
| **VIT** (Viglacera Tiên Sơn, ICB 2353) | **21.600**, phiên 28/08 −8,47% | **+13,9% TRÊN đáy 3M** (−23,4% so đỉnh) · **PB 2,00 · PE 16,80** · ADV3M **0,52 tỷ** · Debt_Eq 2,61. Lõi không xấu (CF_OA_P0 94,9 tỷ = **2,15× NP_P0** 44,2 tỷ, FSCORE 7) | **Không phải case** — trượt thẳng **§2#5 / §2.5#4 (sàn định giá)**: PB 2,00 không có sàn tài sản, và mã không ở vùng sợ hãi (trên đáy 3M gần 14%). Thanh khoản cũng dưới mọi ràng buộc đã dùng cho TV1 |
| **DHD** (ICB 4577 — dược) | **27.000**, phiên 28/08 −5,26% | **chỉ −5,6% so đỉnh 3M** (+3,8% trên đáy) · **PB 2,48 · PE 20,76** · **ADV3M 0,15 tỷ** | **Không phải case** — loại ở bước lọc RẺ NHẤT: không ở vùng sợ hãi + không có sàn định giá + thanh khoản 0,15 tỷ/phiên (không đầu tư được ở quy mô này) |
| **OGC** (Ocean Group) | **2.190**, phiên 28/08 −6,81% | PB 0,34 · **CF_OA_P0 −80,86 tỷ** · Risk_Rating 4 · +6,8% trên đáy 3M | **NON — đã kết luận, chỉ echo.** OGC là ca NON kinh điển ghi thẳng trong §2 (*"gian lận ngân hàng LÀ lõi"*). Không có gì trong cửa sổ đổi kết luận |

**Phần 3 — WebSearch tin theo BỘ TỪ KHOÁ NHÓM (8 truy vấn):**
- **Nhóm chung** (khởi tố/bắt tạm giam/thanh tra/đình chỉ/hạn chế giao dịch/từ chối kiểm toán/chậm nộp
  BCTC/cắt margin/huỷ niêm yết/corp-action bất thường): **0 case NIÊM YẾT MỚI** liên quan danh mục gác
  trong cửa sổ 28/08→30/08. Mọi kết quả trả về đều là tin nền 2023–2026/05 đã ghi ở các lượt trước.
  Nhắc lại mốc đã ghi 08-28, **hiệu lực trong tuần này**: **HBS đình chỉ giao dịch từ 03/09** (ngoài
  29 mã gác, chỉ ghi nền).
- **Nhóm ngân hàng (13 mã)** — §4.2 `bank_tailrisk_insurance_design_20260814.md`: **0 sự kiện.** Không
  kiểm soát đặc biệt / chuyển giao bắt buộc / rút tiền hàng loạt / khởi tố lãnh đạo NH niêm yết / cho
  vay sân sau / thao túng cp NH trong cửa sổ. Kết quả chỉ trả về nền 2024–2025 (4 NH đã chuyển giao
  xong: GPBank, MBV, Vikki, VCBNeo) + ca Thanh Hoá 20/08 (pháp nhân KHÔNG niêm yết) đã ghi 08-28.
  Chiều **ngược lại**: **TCB là tâm điểm mua ròng khối ngoại tuần 24–28/08**.
- **Nhóm BĐS đầu ngành/hạ tầng (VHM, VRE — và VIC/VPI ở phía mua)** — §6
  `vic_family_credit_concentration_20260818.md`: **0 sự kiện tín dụng XẤU mới.** Không chậm/vỡ nợ trái
  phiếu, không hạ bậc tín nhiệm, không siết TSĐB, không call margin cổ đông lớn, không giải chấp. Nền
  đã biết, KHÔNG phải tin mới: FiinRatings xếp VHM **'A'/Stable**; 2 lô VHM12605 (3.000 tỷ) + VHM12606
  (1.000 tỷ) dùng cổ phiếu VIC làm TSĐB. Chiều **dương** trong cửa sổ: bộ đôi **VIC–VHM là động lực
  chính đưa VN-Index phá đỉnh**.
- **Nhóm ngoài NH (16 mã)** — tai nạn/sự cố nhà máy, thu hồi sản phẩm, mất giấy phép/mỏ, kê biên tài
  sản, tranh chấp lãnh đạo: **0 sự kiện.**

**Phần 4 — PHÍA MUA (câu hỏi bắt buộc của lượt quét): 0 LỆNH MUA TRÊN MỌI KÊNH cho phiên 03/09 ⇒
KHÔNG có luận điểm mua nào đang bị gãy.** Đã kiểm **cả ba** kênh mua, không suy đoán từ một kênh:

| Kênh mua | Trạng thái cho phiên kế tiếp (03/09) | Bằng chứng |
|---|---|---|
| **V2.4 BAL** | 2 ứng viên **VIC, VPI** vẫn `deferred` vì `signal_hold` (user chốt 19/08, checkpoint **16/09**) | `deferred_orders` trong `plan_{SpaceX,ZaloPay}_2026-08-28.json`, cưỡng chế bằng `data/signal_holds.json` |
| **V2.4 LAG** | **0 mã đến hạn**, 0 mã upcoming | `filter_lag_entry_window.py` → `due_today: []`, `upcoming_next_plans: []` |
| **TV1 DISCRETIONARY_SPECIAL** (kênh gom TỰ ĐỘNG, cron 20:30) | **SKIP cả 2 account cho `plan_date=2026-09-03`** — SpaceX: deadband (thiếu 100cp = 0,21% active_nav < ngưỡng 0,50%); ZaloPay: đã đạt mục tiêu (filled 1.200 ≥ target 1.200) | `history_noninject` trong `state_TV1_{SpaceX,ZaloPay}.json` |

- **VIC**: 0 tin xấu trong cửa sổ, chỉ dữ kiện DƯƠNG (dẫn dắt VN-Index phá đỉnh). **Luận điểm không gãy.**
- **VPI**: 0 tin xấu trong cửa sổ. Nền 08-24 giữ nguyên (dư nợ trái phiếu >2.584 tỷ vs tiền mặt ~143 tỷ
  cuối Q1/2026, ≥8 lô dùng CHÍNH cổ phiếu VPI của lãnh đạo/bên liên quan làm TSĐB) — **nền, không phải
  sự kiện tuần này**, không có diễn biến mới làm nó xấu đi.
⇒ **Không cần hành động phía mua.**

**Phần 5 — read-through case đang theo dõi**

- ★ **TV1** (§4/§14, **QUALIFY** — SpaceX 2.300cp + ZaloPay 1.200cp): **20.500 (28/08, +0,49%)**, PE 3,55
  · PB 1,08, vẫn dưới MA50 (20.908). **Xác nhận thêm 1 phiên cho phát hiện 08-28, và mốc quá hạn dài
  thêm:**
  - **Cổ tức 15% vẫn CHƯA được broker book làm khoản phải thu.** `cashDividendReceiving` phiên 28/08 =
    **3.300.000 (SpaceX) / 2.232.000 (ZaloPay)** — **không đổi** so với 27/08, và khớp CHÍNH XÁC
    SAB 3.000đ/cp × 1.100cp / × 744cp. TV1 15% phải là **3.450.000 / 1.800.000** — vẫn **không có mặt**.
    Nay **quá hạn ~11 phiên** kể từ công bố ngày thanh toán 14/08.
  - **Kết quả lấy ý kiến bằng văn bản chọn đơn vị kiểm toán (thực hiện 10/08) vẫn CHƯA công bố sau 21
    ngày** (WebSearch lượt này: chỉ trả về tin nền 01/07 về việc cả 4 Big4 từ chối — Deloitte, EY,
    KPMG, PwC — không có bài kết quả).
  → **Không đổi phân loại QUALIFY** (§14 vẫn đứng: lõi tách biệt, CF_OA ≥ NP, solvent, PE 3,55).
  ⚠️ **Nhưng đây là mục ĐÁNG ESCALATE NHẤT lượt này, vì lý do PHÍA MUA chứ không phải phía bán:**
  chương trình gom TV1 là **duy trì TỶ TRỌNG động** (`target_pct_active_nav = 0.05`, `status=active`,
  `hard_expiry.halted = false`) ⇒ **giá TV1 giảm làm số cp mục tiêu TĂNG ⇒ hệ tự mua thêm vào chỗ yếu.**
  Hai điều kiện `hard_expiry` (kiểm toán FY2026 ra ý kiến ngoại trừ/từ chối/trái ngược · TV1 bị đình chỉ
  hoặc hạn chế giao dịch) là **`manual_only: true`** — **không có cơ chế tự động nào bật chúng**; phải
  có người đọc tin rồi set `halted`. Cả hai cổng đang treo quá hạn đúng là **tiền đề** của điều kiện thứ
  nhất. Hôm nay **chưa** đủ để kích hoạt (chưa có ý kiến kiểm toán nào được phát hành ⇒ chưa "ngoại
  trừ/từ chối"), nên **KHÔNG đề xuất halt** — nhưng đề nghị user/Mike biết rằng lá chắn này là thủ công.
- **PNJ** (§7, AMBIGUOUS): **42.100 (28/08, +0,48%)**, PE 7,43 · PB 1,55 · **+36,9% trên đáy 30.750
  (24/07)**, vẫn dưới MA50 (44.014). **0 tin mới trong cửa sổ.** Không đổi AMBIGUOUS; nhắc lại hệ quả
  thực dụng đã ghi 08-28: biên an toàn để chờ cổng BCTC Q3/2026 (~cuối 10/2026) đã mỏng đi ~37% —
  case đã **hết tính "mua khi sợ hãi"** theo nghĩa đen.
- **DGC** (§6, AMBIGUOUS-nghiêng-constructive · ZaloPay giữ 10.000cp, `excluded=True`): **43.000 (28/08,
  −0,46%)**, PE 7,52 · PB **1,01** · vẫn dưới MA50 (43.800). **0 tin mới trong cửa sổ** — mọi kết quả
  tìm kiếm đều là tin 05–06/2026 (hạn chế giao dịch từ 26/05; BCTC kiểm toán 2025 công bố 20/06 bởi UHY
  với **ý kiến NGOẠI TRỪ** do không chứng kiến kiểm kê **950,9 tỷ hàng tồn kho**). ⇒ **Đính chính một
  mốc trong sổ**: cổng "nộp xong BCTC kiểm toán 2025" ghi ở các lượt trước **đã đóng từ 20/06** — cổng
  còn lại đúng là **gỡ được ý kiến ngoại trừ tồn kho** (chỉ có thể qua kỳ kiểm toán sau), không phải
  việc nộp.
- **TV4** (AMBIGUOUS): **13.000 (28/08, −4,41%, KL 12.700cp)** — giao dịch trở lại sau 2 phiên trắng
  (25–27/08), PE 5,85 · PB 0,98, xuyên xuống dưới MA50 (13.046). **Rơi đúng ngay tại cổng.** Cổng nhị
  phân **ý kiến kiểm toán BCTC bán niên soát xét 2026 (hạn ~30/08)** đã tới hạn trong cửa sổ mà
  **WebSearch không tìm được công bố nào** ⇒ cổng **chưa mở, nay đã QUÁ HẠN**. Giữ nguyên cảnh báo
  08-21 (KSNB từ nhiệm ngay trước cổng + đã thay toàn bộ ban lãnh đạo). Thanh khoản 12.700cp/phiên vẫn
  chặn mạnh hơn mọi phân loại.
- **ICG** (AMBIGUOUS-yếu, mở 08-21): **11.000 (28/08, 0,00%, KL 200cp)** — thanh khoản gần như CHẾT,
  PB 0,62 · PE 7,44, giá còn cách MA50 (14.386) 24%. **Vẫn KHÔNG có công bố giải trình HNX** về chuỗi 4
  phiên sàn 14→19/08 ⇒ **cổng (a) treo sang tuần thứ 3**. Cổng (b) soát xét bán niên ~30/08 **cũng quá
  hạn không công bố**. Không đổi phân loại; **hai cổng cùng treo trên một mã KL 200cp/phiên = không có
  đường vào dù phân loại có tốt lên**.

**Tổng kết lượt**: **29 mã đang gác** rà qua · 253 mã (anomaly_scan) + **697 mã** (quét rộng) + **8
truy vấn tin** · **0 QUALIFY mới** · **1 NON mới (BNA)** · 2 không-phải-case (VIT, DHD) · 1 echo NON
(OGC) · **watchlist KHÔNG quá hạn** (computed_at 2026-08-28 = đúng phiên cuối) · **0 lệnh mua trên cả
3 kênh (BAL/LAG/TV1-discretionary) cho phiên 03/09 ⇒ KHÔNG có luận điểm mua nào bị gãy.**
**Mốc phải theo, gần → xa: quét lại tối 02/09 phủ khoảng trống 31/08→02/09 trước plan 03/09 → HBS đình
chỉ giao dịch 03/09 (ngoài danh mục) → TV4 + ICG soát xét bán niên ĐÃ QUÁ HẠN, chờ công bố → TV1 cổ tức
(quá hạn ~11 phiên, chứng minh được là chưa book) + kết quả chọn kiểm toán (quá hạn 21 ngày) → checkpoint
BAL paper-track 16/09 → DGC gỡ ý kiến ngoại trừ tồn kho → PNJ Q3 cuối 10/2026.**

Nguồn lượt này: [stockbiz — BNA bị kiểm soát do chậm nộp BCTC, nợ vay vượt 730 tỷ](https://stockbiz.vn/tin-tuc/bna-co-phieu-dau-tu-bao-ngoc-bi-kiem-soat-do-cham-nop-bao-cao-tai-chinh-no-vay-vuot-730-ty-dong/40086285) ·
[vietstock — BNA bị đưa vào diện kiểm soát](https://vietstock.vn/2026/05/bna-bi-dua-vao-dien-kiem-soat-830-1442879.htm) ·
[vietstock — Cổ phiếu bị đưa vào diện cảnh báo, BNA muốn vay và bảo lãnh hơn 260 tỷ](https://vietstock.vn/2026/07/co-phieu-bi-dua-vao-dien-canh-bao-bna-muon-vay-va-bao-lanh-hon-260-ty-830-1463805.htm) ·
[vnbusiness — Cổ phiếu chủ thương hiệu Bánh Bảo Ngọc bị đưa vào diện kiểm soát](https://vnbusiness.vn/co-phieu-cua-chu-thuong-hieu-banh-bao-ngoc-bi-dua-vao-dien-kiem-soat.html) ·
[dantri — Chủ tịch vừa bị bắt, công ty điện bị cả 4 bên Big4 từ chối kiểm toán (TV1, nền 01/07)](https://dantri.com.vn/kinh-doanh/chu-tich-vua-bi-bat-cong-ty-dien-bi-ca-4-ben-big-4-tu-choi-kiem-toan-20260701145835409.htm) ·
[nguoiquansat — Big4 đồng loạt từ chối kiểm toán TV1, lấy ý kiến cổ đông chọn đơn vị mới ngày 10/08](https://nguoiquansat.vn/big4-dong-loat-tu-choi-kiem-toan-doanh-nghiep-dien-nghin-ty-sau-khi-chu-tich-bi-khoi-to-301231.html) ·
[cafef — DGC công bố BCTC kiểm toán 2025 (20/06), hai vấn đề ngoại trừ](https://cafef.vn/hoa-chat-duc-giang-cong-bo-bctc-kiem-toan-2025-loi-nhuan-giam-hang-chuc-ty-hai-van-de-ngoai-tru-dang-luu-y-188260621122508047.chn) ·
[tinnhanhchungkhoan — DGC bị ngoại trừ khoản hàng tồn kho 950,9 tỷ sau khi đổi đơn vị kiểm toán](https://www.tinnhanhchungkhoan.vn/hoa-chat-duc-giang-dgc-bi-ngoai-tru-khoan-hang-ton-kho-9509-ty-dong-sau-khi-doi-don-vi-kiem-toan-post392759.html) ·
[nguoiquansat — Vinhomes phát hành lô trái phiếu 6.000 tỷ, xếp hạng tín nhiệm FiinRatings 'A'/Stable (nền)](https://nguoiquansat.vn/vinhomes-vhm-sap-phat-hanh-lo-trai-phieu-tri-gia-6-000-ty-dong-to-chuc-xep-hang-tin-nhiem-noi-gi-286189.html) ·
[vietnamplus — VN-Index tăng 7 phiên liên tiếp trước kỳ nghỉ lễ Quốc khánh 2/9 (28/08: 1.832,12)](https://www.vietnamplus.vn/vn-index-tang-7-phien-lien-tiep-truoc-ky-nghi-le-quoc-khanh-29-post1133140.vnp) ·
[dnse — Hành trình phá đỉnh của VN-Index: bộ đôi VIC–VHM áp đảo](https://www.dnse.com.vn/senses/tin-tuc/hanh-trinh-pha-dinh-cua-vn-index-ap-dao-phan-con-lai-dan-hut-hoi-35225059) ·
[24hmoney — Tổ chức xếp hạng tín nhiệm đánh giá việc Vinhomes dùng 40 triệu cp VIC thế chấp (nền)](https://24hmoney.vn/news/to-chuc-xep-hang-tin-nhiem-danh-gia-ra-sao-khi-vinhomes-dung-40-trieu-co-phieu-vic-the-chap-c4a2787660.html)

---

## 14. TV1 — cập nhật 2026-08-10 (Mike, due-diligence trực tiếp theo yêu cầu user, đúng ngày cổng T3)

**Q2/2026 nay là số THẬT, không còn stale carry-forward.** Check 08-04 từng gắn cờ nghi ngờ dòng
"2026Q2" trong `ticker_financial` là Q1 lặp lại. Xác nhận lại hôm nay: `Release_Date`=2026-08-03
(khác Q1's 2026-05-04), NP_P0=31,33 tỷ ≠ NP Q1 32,23 tỷ (không byte-identical) → filing thật.

**KQKD Q2/2026**: NP 31,33 tỷ (+7,96% YoY so NP cùng kỳ 29,02 tỷ), Doanh thu 134,0 tỷ (+4,13% YoY),
NPM 20,66% (~ổn định QoQ), ROE_Trailing 30,58%. Giảm QoQ so Q1 (NP −2,8%, DT −7,4%) khớp mùa vụ
thủy điện đã thấy ở 2025 (Q2/2025 cũng thấp hơn Q1/2025) — không phải tín hiệu xấu. FSCORE giảm
6→5 (đáng ghi nhận, không đáng báo động). CF_OA quý này (24,31 tỷ) < NP quý này lần đầu sau nhiều
quý, NHƯNG **CF_OA/NP TTM (4 quý gần nhất) = 220,13/154,17 = 1,43x** — vẫn đúng mẫu "TV1 luôn
≥1x" trong router, đọc theo TTM chứ không theo 1 quý (đúng luật Step 3) → không đổi kết luận lõi
sạch.

**Cổng T3 (chọn đơn vị kiểm toán) — HÔM NAY 10/08 chính là ngày lấy ý kiến bằng văn bản.**
WebSearch xác nhận lịch (stockbiz/cafef/dantri, đưa tin từ 01/07 và 20/07) nhưng **CHƯA có bài nào
đăng kết quả** — hợp lý vì kết quả lấy ý kiến bằng văn bản thường công bố sau vài ngày, không phải
tức thời trong ngày bỏ phiếu. **Cần tra lại 1-2 ngày tới**, đừng coi "chưa thấy tin xấu" là đã qua
cổng.

**Cổng phụ (cổ tức 15%) — CÓ TIN MỚI, ngày trả đã công bố.** Nguồn dnse.com.vn/baodauthau.vn:
ngày thanh toán cổ tức tiền mặt 15% (1.500đ/cp) = **14/08/2026** (còn 4 ngày). ⚠️ Chỉ 1 nguồn tổng
hợp xác nhận ngày trả, **chưa tìm được ngày ĐKCC (record date) từ thông báo HOSE/HNX gốc** — nêu rõ
độ tin cậy trung bình, verify lại nếu dùng để tính toán chính xác ngày giao dịch không hưởng quyền.

**Giá/kỹ thuật 10/08**: 19.800đ (đi ngang biên 19.400-20.000 hơn 3 tuần, khớp ghi nhận 06/08).
Dưới MA50 (21.598) và MA200 (25.535) — downtrend kỹ thuật dài hạn CHƯA đảo chiều dù đã có 3 tuần
đi ngang. PE 3,43x (PE_MA5Y 11,62±7,81 → −1,05SD), PB 1,05x (PB_MA5Y 1,32±0,29 → −0,92SD).

**DCF cập nhật (router Tier 3, illiquid — beta đo 0,24/R²=1,8% loại bỏ theo đúng cảnh báo router
§1.2b dùng TV1 làm ví dụ, ADV~0,7-0,8 tỷ/ngày < 2 tỷ → premium +4-6pp, CoE 16,3-19,3%, Rf 6,8%
12/06/2026-6.8% xác nhận 20/07, ERP 6,5%)**:
- Full-FCF DCF (perpetuity, FCF TTM 214,45 tỷ, g 1-3%): ~44.300 – 62.200đ/cp
- DDM (chỉ tính cổ tức thực trả, D1 1.000-1.500đ, g 0-4%): ~5.200 – 12.700đ/cp
- Khoảng cách 2 phương pháp = đúng câu hỏi "công ty có thực sự trả lại FCF cho cổ đông không" —
  cổ tức trả 14/08 tới là phép thử thực tế đầu tiên kể từ khi nâng tỷ lệ 6%→15%.
- SOTP trước đó (§10.2, bottom-up từng tài sản Sông Bung 5): ~33.100đ/cp — coi là điểm neo đáng
  tin hơn đầu trên của FCF-DCF top-down (DCF perpetuity dễ overstate giá trị 1 tài sản đơn lẻ).

**Kết luận**: giữ nguyên QUALIFY, lõi vẫn sạch và Q2 thật xác nhận thêm 1 quý không gián đoạn vận
hành. Không đổi sizing đã duyệt (0,5-1,0% NAV, giới hạn bởi thanh khoản). Hai cổng va nhau đúng
tuần này (kết quả kiểm toán ~vài ngày tới + trả cổ tức 14/08) — theo dõi sát, KHÔNG phải tín hiệu
mua thêm chỉ vì tới hạn, cần cổng THẬT xác nhận trước.

Sources: [stockbiz.vn](https://stockbiz.vn/tin-tuc/tv1-mot-cong-ty-con-cua-evn-bi-ca-4-cong-ty-big4-tu-choi-kiem-toan-sau-khi-chu-tich-hdqt-bi-khoi-to/40702174) ·
[dantri.com.vn](https://dantri.com.vn/kinh-doanh/chu-tich-vua-bi-bat-cong-ty-dien-bi-ca-4-ben-big-4-tu-choi-kiem-toan-20260701145835409.htm) ·
[baodauthau.vn](https://baodauthau.vn/dhcd-pecc1-manh-tay-chia-co-tuc-tham-gia-loat-du-an-thuy-dien-mo-rong-luoi-dien-dien-hat-nhan-post198014.html)
