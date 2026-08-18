# VIC-family: (A) Tầng 1 mở rộng đã triển khai, (B) proxy lãi vay thị trường, (C) test giả thuyết "neo giá giữ tài sản thế chấp" — 2026-08-18

Job Taylor_20260818_032509 (dispatch từ Mike sau khi user duyệt plan từ báo cáo
`vic_family_credit_concentration_20260818.md`). 3 phần theo đúng thứ tự dispatch.

---

## Phần A — Tầng 1 đã triển khai (code change thật)

Thêm nhóm từ khoá `c) NHÓM BĐS ĐẦU NGÀNH/HẠ TẦNG CÔNG` vào `mike/bin/fearbuy_weekly_scan.sh`
(song song nhóm ngân hàng đã có, ngay sau nó), nguyên văn danh sách từ khoá lấy từ §6 báo cáo
08-18 + bổ sung 3 cụm giải chấp/margin theo yêu cầu Phần C mục 3 của dispatch này (`giải chấp cổ
phiếu · call margin cổ đông lớn · cầm cố cổ phiếu Vingroup`). Nhóm ngoài-ngân-hàng cũ được đổi
nhãn từ `c)` sang `d)` — nội dung KHÔNG đổi.

**Diff** (commit `38b8c835`, thuần chèn, không sửa dòng nào của nhóm a/b hiện có):
```diff
-   c) NHÓM NGOÀI NGÂN HÀNG — BỔ SUNG:
+   c) NHÓM BĐS ĐẦU NGÀNH/HẠ TẦNG CÔNG — BỔ SUNG (research/vic_family_credit_concentration_20260818.md
+      §6, cùng khung Tầng 1 đã duyệt 08-14, không dựng cơ chế mới):
+      chậm/vỡ nợ trái phiếu doanh nghiệp · không thanh toán được lãi/gốc trái phiếu đến hạn ·
+      tổ chức xếp hạng tín nhiệm hạ bậc · ngân hàng siết nợ/thu hồi tài sản đảm bảo · dự án hạ tầng
+      chậm tiến độ/đội vốn bị thanh tra · SBV/NHNN thay đổi chính sách loại trừ room tín dụng ·
+      Vingroup/VinFast dòng tiền · huỷ/hoãn niêm yết trái phiếu · kiện tụng nhà thầu/nợ đọng xây dựng ·
+      giải chấp cổ phiếu · call margin cổ đông lớn · cầm cố cổ phiếu Vingroup
+
+   d) NHÓM NGOÀI NGÂN HÀNG — BỔ SUNG:
       tai nạn/sự cố nhà máy · thu hồi sản phẩm · mất giấy phép/mỏ · kê biên tài sản · tranh chấp
       lãnh đạo
```
Test: `bash -n bin/fearbuy_weekly_scan.sh` → OK. Không chạy full dispatch LLM thật (chi phí, và
nội dung prompt không thay đổi cấu trúc điều khiển — chỉ thêm text vào một khối heredoc tĩnh).
Không cần chạy hàng tuần thật để verify vì group c)/d) chỉ là văn bản trong prompt, không phải
logic rẽ nhánh.

---

## Phần B — Proxy lãi vay thị trường VIC-group (WebSearch, có trong phiên headless)

**Trái phiếu VND phát hành mới, 2026 (giá thực tế, không phải suy diễn):**

| Tổ chức | Lô | Ngày | Kỳ hạn | Lãi suất | Nguồn |
|---|---|---|---|---|---|
| Vinhomes (VHM) | VHM12607–12610, 6.000 tỷ | 20/06/2026 | 36–38 tháng | **12,5%/năm** | [Vinhomes muốn huy động 15.000 tỷ](https://cafef.vn/vinhomes-muon-huy-dong-15000-ty-dong-trai-phieu-sau-khi-da-phat-hanh-21000-ty-tu-dau-nam-188260625082638443.chn) |
| Vinhomes (VHM) | VHM12613–12614, 3.000 tỷ | 10/07/2026 | 36 tháng | **12,5%/năm** | cùng nguồn |
| Vinhomes (VHM) | VHM12615, 2.000 tỷ | 06/08/2026 | 36 tháng (3 năm) | **12,5%/năm** | [VHM huy động thêm 2.000 tỷ](https://stockbiz.vn/tin-tuc/vhm-vinhomes-huy-dong-them-2000-ty-dong-tu-trai-phieu/41390774) |
| Vinpearl (VPL) | VPL12601, 4.907 tỷ | đầu 06/2026 | 5 năm | **12%/năm** 4 kỳ đầu, sau đó tham chiếu lãi suất MB + biên độ 2,45đ%, sàn 12%/năm | [Vinhomes muốn huy động 15.000 tỷ](https://cafef.vn/vinhomes-muon-huy-dong-15000-ty-dong-trai-phieu-sau-khi-da-phat-hanh-21000-ty-tu-dau-nam-188260625082638443.chn) |
| Vingroup (VIC) | VICGIFB1626002 (thanh toán) | 23/02/2026 | — | **8,5%/năm** (lô cũ, không phải phát hành mới — không dùng làm proxy lãi suất HIỆN TẠI) | [Vingroup thanh toán gần 1.100 tỷ](https://cafef.vn/vingroup-thanh-toan-gan-1100-ty-dong-goc-lai-trai-phieu-188260225110419967.chn) |
| Vingroup (VIC) | Trái phiếu quốc tế, tối đa 350 triệu USD | kế hoạch Q2/2026 | 5 năm | **≤5,75%/năm** (USD, KHÔNG so được trực tiếp với lãi VND — chênh lệch phần lớn là basis tiền tệ, không phải rủi ro tín dụng thuần) | [Vingroup chuẩn bị phát hành trái phiếu quốc tế](https://vietstock.vn/2026/02/vingroup-chuan-bi-phat-hanh-lo-trai-phieu-quoc-te-toi-da-350-trieu-usd-trong-quy-2-3118-1406171.htm) |

**⇒ Proxy tốt nhất cho lãi vay thị trường VIC-group hiện tại: ~12–12,5%/năm** (trái phiếu VND kỳ
hạn 3 năm, phát hành 06–08/2026, đây là lô MỚI PHÁT HÀNH nên phản ánh giá thị trường tại thời điểm
đó — khác với lô VIC 8,5% nói trên là NGHĨA VỤ THANH TOÁN của lô cũ phát hành trước, không phải giá
mới). Con số này **khớp chiều hướng** với ước lượng "lãi suất BĐS phổ biến 9-11%, dự báo tăng thêm
3-4đ%" đã VERIFIED ở báo cáo 08-18 trước — Vinhomes đang trả cao hơn cả biên trên của phổ biến thị
trường BĐS nói chung, phù hợp với vị thế đòn bẩy cao (Debt_Eq VHM 4,1× trong 12 tháng qua, đã đo
BQ trong báo cáo trước).

**Xếp hạng tín nhiệm nội địa** — VERIFIED, có thật, không suy diễn:
- **Saigon Ratings** xếp hạng khởi đầu **Vinhomes ở mức "vnAA", triển vọng "Ổn định"**.
- **S&I Ratings** đánh giá Vinhomes rủi ro **"thấp"** nhờ chính sách đòn bẩy "tương đối thận
  trọng", khả năng thanh khoản và trả lãi ở mức an toàn.
- **FiinRatings** có Vingroup trong danh mục khách hàng lớn xếp hạng nội địa (cùng nhóm
  Techcombank, Coteccons, Hà Đô, F88) — KHÔNG tìm được mức xếp hạng cụ thể công khai của Vingroup
  (khác Vinhomes đã có "vnAA" nêu trên).

**Spread ước tính**: lãi suất huy động tiết kiệm kỳ hạn 12-36 tháng của NHTM lớn hiện phổ biến
~5-6%/năm (không tra lại trong job này — số tham chiếu chung, không phải verified riêng cho
08-2026). Nếu đúng, **spread trái phiếu VHM 12,5% so với lãi huy động ngân hàng ~6-7 điểm phần
trăm** — mức spread cao, phù hợp với rating "vnAA" (đầu tư được nhưng không phải hạng cao nhất)
và đòn bẩy đang tăng nhanh đã đo ở báo cáo trước. **KHÔNG XÁC MINH ĐƯỢC** giá trị lãi suất huy
động ngân hàng cùng kỳ hạn TẠI ĐÚNG THỜI ĐIỂM 08/2026 trong job này — nếu cần spread chính xác,
cần 1 lượt WebSearch riêng.

**KHÔNG XÁC MINH ĐƯỢC**: lãi suất áp dụng cho gói 752.000 tỷ được loại trừ trần tăng trưởng theo
Công văn 5368/NHNN-TD (đã nêu ở báo cáo trước) — WebSearch không tìm ra con số cụ thể cho phần vay
ngân hàng trực tiếp (chỉ có dữ liệu trái phiếu công khai ở trên, đây là 2 kênh vốn khác nhau).

---

## Phần C — Giả thuyết "neo giá giữ tài sản thế chấp"

### (a) Bằng chứng QUAN SÁT ĐƯỢC

**C.1 — Test tail-asymmetry được kiểm soát theo momentum, N=225 mã thanh khoản cao (mở rộng so
với 4-5 mã Mike so tay ban đầu):**

- Nguồn: `tav2_bq.ticker_prune`, 365 phiên gần nhất kết thúc 2026-08-17 (khớp đúng cửa sổ
  Mike đã dùng). N khai rõ = **225 mã** (sau lọc `n_days >= 200` để loại mã mới niêm yết/thiếu dữ
  liệu; loại VNINDEX khỏi hồi quy vì không có biên độ ±7%).
- Biến: `n_ceil` = số phiên lợi suất ngày ≥+6,5%, `n_floor` = số phiên ≤−6,5% (đúng ngưỡng Mike
  dùng, gần sát biên HOSE ±7%), `total_ret` = Close cuối/Close đầu − 1 (momentum 12 tháng).
- **Self-check độc lập**: VIC total_ret tính lại tay từ 2 điểm giá thô (`Close` 2025-08-18 =
  59.100, 2026-08-17 = 198.000) → 198.000/59.100 − 1 = **2,350** — khớp tuyệt đối với số trong
  pipeline (2,350253...). Recompute PASS.
- **Phương pháp**: hồi quy tuyến tính đơn giản `(n_ceil − n_floor)/n_days ~ total_ret` trên toàn
  bộ 225 mã (kiểm soát cho việc "mã tăng giá mạnh tự nhiên có nhiều phiên trần hơn phiên sàn" —
  đúng cơ chế Mike đã nêu là khó phân biệt). Sau đó xem **phần dư (residual)** của VIC/VHM/VRE so
  với đường xu hướng chung — mã nào có phần dư cao bất thường (z lớn) tức là có NHIỀU phiên trần
  hơn mức "bình thường" của một mã tăng cùng mức momentum.

**Kết quả (KHÔNG ủng hộ giả thuyết neo giá theo hướng mạnh):**

| Mã | total_ret 12T | (ceil−floor)/n thực tế | Dự đoán theo xu hướng chung | Phần dư (residual) | z-score | Percentile trong 225 mã |
|---|---:|---:|---:|---:|---:|---:|
| **VIC** | +235,0% | 0,0201 | 0,0432 | **−0,0231** | **−1,85** | **0,9%** (gần thấp nhất) |
| **VHM** | +50,9% | 0,0321 | 0,0152 | +0,0170 | +1,36 | 92,0% |
| **VRE** | −15,7% | 0,0120 | 0,0051 | +0,0070 | +0,56 | 76,9% |

- **VIC**: phần dư ÂM, nằm ở percentile 0,9% (gần đáy) trong 225 mã — nghĩa là so với một mã có
  momentum +235% trong 12 tháng, VIC có **ÍT phiên trần dư ra so với phiên sàn hơn** mức "bình
  thường" của nhóm tăng mạnh, không phải nhiều hơn. Đây là bằng chứng đi **NGƯỢC** hướng giả
  thuyết "trần được bảo vệ nhân tạo" — nếu có neo giá kiểu ngăn giảm/đẩy trần, kỳ vọng sẽ thấy
  phần dư DƯƠNG mạnh, không phải âm.
- **VHM**: phần dư dương, z=1,36 — **chưa vượt ngưỡng thường dùng để gọi là bất thường** (thường
  cần z≥2). Nằm ở top ~8% cao nhất nhưng không phải outlier cực đoan.
- **VRE**: phần dư dương nhẹ, z=0,56 — hoàn toàn trong biên độ bình thường, không đáng chú ý
  (đúng như Mike đã ghi nhận ban đầu).

**Giới hạn phương pháp — khai rõ, không giấu:** đây là hồi quy tuyến tính đơn biến trên dữ liệu
lệch mạnh (total_ret có đuôi dài do momentum extreme), KHÔNG kiểm soát heteroskedasticity, KHÔNG
cluster theo ngành/beta thị trường, KHÔNG bootstrap CI cho residual, và N=225 là **225 mã, không
phải 225 sự kiện độc lập** (giá các mã tương quan qua thị trường chung — test này là MÔ TẢ/dò
tìm outlier, không phải kiểm định giả thuyết thống kê chặt theo chuẩn §18 quant-research). Kết
luận đúng mức: **KHÔNG tìm thấy bằng chứng bất thường mạnh** ở cấp độ này, không phải "đã bác bỏ
hoàn toàn khả năng có can thiệp".

**C.2 — Share pledge (cầm cố cổ phiếu) — CÓ THẬT, công khai, VERIFIED qua WebSearch:**

- **Vinhomes dùng 40 triệu cổ phiếu VIC làm tài sản đảm bảo cho 2 lô trái phiếu VHM12605 (3.000
  tỷ) + VHM12606 (1.000 tỷ) = 4.000 tỷ đồng**, tỷ lệ tài sản đảm bảo/dư nợ gần 200% theo đánh giá
  của tổ chức xếp hạng. ([nguồn](https://nguoiquansat.vn/40-trieu-co-phieu-vingroup-bao-dam-cho-2-khoan-vay-nghin-ty-to-chuc-xep-hang-tin-nhiem-noi-gi-293995.html))
- **Vingroup chuyển nhượng ~15,2 triệu cổ phiếu VHM trong tháng 6/2026** (gồm 5,6 triệu cổ phiếu
  cho BNP Paribas Financial Markets ngày 22/06) và **thêm gần 5 triệu cổ phiếu VHM ngày 04-05/08/
  2026 (giá trị >700 tỷ đồng)** — công ty công bố lý do là **"đảm bảo nghĩa vụ thanh toán trái
  phiếu"**. ([nguồn 1](https://nguoiquansat.vn/vingroup-chuyen-nhuong-gan-5-trieu-co-phieu-vhm-309619.html), [nguồn 2](https://vietstock.vn/2026/06/vhm-thong-bao-giao-dich-co-phieu-cua-to-chuc-co-lien-quan-cua-nguoi-noi-bo-tap-doan-vingroup-cong-ty-co-phan-739-1451737.htm))

⇒ **Cơ chế "cổ phiếu làm tài sản thế chấp cho nợ vay/trái phiếu" là THẬT và đang hoạt động ở quy
mô đáng kể** (ít nhất 4.000 tỷ qua cầm cố cổ phiếu VIC + hàng chục triệu cổ phiếu VHM chuyển
nhượng liên quan nghĩa vụ trái phiếu trong năm 2026). Đây LÀ đúng cơ chế tạo động cơ tránh giá
giảm mạnh mà user nêu — không cần chứng minh "thao túng" mới có giá trị: **giá trị tài sản đảm
bảo giảm mạnh → tỷ lệ tài sản đảm bảo/dư nợ tụt dưới ngưỡng hợp đồng → có thể kích hoạt yêu cầu bổ
sung tài sản đảm bảo hoặc giải chấp**, là RỦI RO LAN TRUYỀN có thật, không phải suy diễn.

**KHÔNG XÁC MINH ĐƯỢC** (giới hạn WebSearch trong job này, không suy diễn thay):
- **Tổng khối lượng cầm cố cổ phiếu VIC-family / free float** — free float đo được (VIC 27,32%,
  VHM 33,81%, tra `cafef`/`vietstock`), nhưng KHÔNG tìm được tổng khối lượng cầm cố toàn hệ thống
  (chỉ có 2 case cụ thể: 40 triệu CP VIC cho 2 lô trái phiếu, và các đợt chuyển nhượng VHM nêu
  trên — đây là các sự kiện RỜI RẠC được công bố, không phải một con số tổng hợp một lần).
- **Có sự kiện margin-call/giải chấp thực tế nào gần đây với cổ phiếu VIC-family không** —
  WebSearch chỉ trả về nội dung giáo dục chung về khái niệm "call margin"/"bán giải chấp", KHÔNG
  tìm được tin tức cụ thể nào về việc VIC/VHM/VRE bị giải chấp trong 2026. **Không suy diễn "chưa
  từng xảy ra"** — chỉ là không tìm thấy qua WebSearch trong phạm vi job này.

### (b) Diễn giải CÓ THỂ — không phân biệt được từ dữ liệu giá đơn thuần

Hai khả năng vẫn cùng khớp với dữ liệu quan sát được, và test C.1 (kiểm soát momentum, N=225) **không
nghiêng rõ về phía nào**:
1. **Momentum thật/lực mua chủ động mạnh** — khớp với +709% VIC 12 tháng đã đo trước, dòng vốn
   FOL/margin đổ vào nhóm vốn hoá lớn, kỳ vọng thị trường về hạ tầng/VinFast. Test C.1 cho thấy
   VIC còn có phần dư ÂM (ít trần-dư hơn mã cùng momentum), phù hợp với khả năng này hơn.
2. **Phòng thủ giá có chủ đích ở vùng nhạy cảm với tài sản thế chấp** — cơ chế C.2 (cầm cố cổ
   phiếu thật, quy mô nghìn tỷ) tạo ĐỘNG CƠ kinh tế thật để tránh giá giảm mạnh, nhưng test C.1
   không tìm thấy dấu vết thống kê ủng hộ ở cấp độ tail-asymmetry đã đo.

**Không thể kết luận đúng/sai giữa 2 khả năng này từ bộ dữ liệu và phương pháp trong job hôm nay.**
Test C.1 mạnh hơn phép so tay 4-5 mã ban đầu (N=225, có kiểm soát momentum) nhưng vẫn là hồi quy
thô, không phải kiểm định nhân quả.

### (c) Hàm ý rủi ro thực tế — đo được một phần, không cần chứng minh thao túng

- **Rủi ro giải chấp dây chuyền (margin/pledge call cascade) là kênh lan truyền CÓ THẬT**, độc lập
  với câu hỏi có "thao túng" hay không: C.2 xác nhận ít nhất 4.000 tỷ đồng nợ có cổ phiếu VIC làm
  tài sản đảm bảo trực tiếp + nhiều đợt chuyển nhượng VHM gắn với nghĩa vụ trái phiếu trong năm.
  Nếu giá giảm mạnh, tỷ lệ tài sản đảm bảo/dư nợ (hiện ~200% theo rating agency, còn dư địa) có
  thể tụt xuống ngưỡng kích hoạt bổ sung tài sản/giải chấp — tạo áp lực bán TỰ CỦNG CỐ
  (self-reinforcing), đúng cơ chế crowding-out/contagion đã nêu ở báo cáo trước nhưng ở TẦNG CỔ
  PHIẾU thay vì tầng tín dụng ngân hàng.
- **Từ khoá cảnh báo sớm cho rủi ro này ĐÃ được thêm vào Tầng 1** (Phần A: "giải chấp cổ phiếu",
  "call margin cổ đông lớn", "cầm cố cổ phiếu Vingroup") — đúng khuyến nghị dispatch mục 3.
- Biên an toàn hiện tại (~200% tài sản đảm bảo/dư nợ cho lô 4.000 tỷ, rating "vnAA"/"rủi ro thấp"
  từ 2 tổ chức độc lập) là **dữ liệu TRẤN AN**, không phải báo động — nhưng đây là ảnh chụp tại
  1 thời điểm công bố, không phải giám sát liên tục.

---

## (d) Cần user quyết thêm gì

1. **Có muốn mở job riêng đo tổng khối lượng cầm cố cổ phiếu VIC-family / free float** (thay vì 2
   case rời rạc đã tìm được) không? Cần nguồn khác WebSearch phổ thông — có thể phải tra cứu công
   bố thông tin định kỳ trên HOSE/UBCKNN trực tiếp theo từng mã, ngoài khả năng 1 lượt WebSearch.
2. **Có muốn thiết lập theo dõi định kỳ (không phải một lần)** cho tin tức "chuyển nhượng cổ phiếu
   đảm bảo nghĩa vụ trái phiếu" của nhóm Vingroup không? Đây là tín hiệu sớm hơn cả "vỡ nợ trái
   phiếu" — nếu tần suất/khối lượng các đợt chuyển nhượng này tăng đột biến, có thể là dấu hiệu áp
   lực tài sản đảm bảo tăng trước khi có tin xấu công khai khác.
3. Test C.1 dùng ngưỡng ±6,5% và cửa sổ 365 phiên theo đúng cách Mike đã làm ban đầu để so sánh
   được — nếu muốn kiểm định chặt hơn (bootstrap CI, cluster theo ngành, N tính theo sự kiện độc
   lập đúng chuẩn §18) thì đây là job riêng, không nằm trong phạm vi hôm nay.
