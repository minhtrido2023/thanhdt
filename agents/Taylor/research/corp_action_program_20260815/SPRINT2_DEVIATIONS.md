# SPRINT 2 — DEVIATIONS từ pre-registration

> Prereg đã commit **`2a9b951a`** TRƯỚC khi tính bất kỳ outcome nào. File này ghi mọi thứ tôi làm
> **khác** với nó, kèm lý do và cái giá phải trả. Prereg không bị sửa một chữ nào sau khi chạy.
> Job `Taylor_20260815_121850`, 2026-08-15.

**Tóm tắt:** 5 deviation. Không cái nào đổi outcome primary hay tiêu chí thành công/thất bại.
D3 là cái quan trọng nhất — nó SINH RA từ một robustness check của chính prereg trả về kết quả
mà prereg không lường trước.

---

## D1 — Benchmark EW: loại 2 quan sát lợi suất bất khả thi

**Prereg nói gì:** §4.3 định nghĩa `EW_ret(d)` là trung bình lợi suất ngày của thành viên
`universe_pit`. Không nói xử lý dữ liệu lỗi thế nào.

**Làm gì khác:** dùng cột `ew_ret` (đã loại `|ret| > 50%`) thay vì `ew_ret_raw`.

**Vì sao:** trên chuỗi `Close` **đã hồi tố**, một lợi suất ngày > 50% không phải biến động thị
trường mà là lỗi dữ liệu (biên độ sàn VN cao nhất là UPCOM ±15%). Đo được: **2 quan sát trên
3.396 phiên**, tức 0,06‰.

**Giá phải trả:** gần bằng 0. Cả hai chuỗi được giữ trong `out2/ew_universe.csv`
(`ew_ret` và `ew_ret_raw`) để ai cũng dựng lại được bản không lọc. Đây là **vệ sinh dữ liệu**,
không phải nút vặn — không có tham số nào để chọn.

---

## D2 — Hồi quy: winsorise BIẾN KIỂM SOÁT ở 1/99 phân vị

**Prereg nói gì:** §6.3 liệt kê biến kiểm soát, không nói winsorise.

**Làm gì khác:** cắt đuôi 1%/99% cho 7 biến kiểm soát (`y_gross`, `log_adv`, `mom_6m`,
`rvol_60`, `log_mcap`, `ey`, `pb_m1`).

**Vì sao:** vài giá trị `PE`/`PB` cực đoan chi phối leverage của OLS.

**Giá phải trả + ranh giới đã giữ:** **KHÔNG winsorise biến kết quả** `BHAR_20` — làm thế sẽ trực
tiếp bóp hiệu ứng đang đo. Hiệu ứng đuôi của biến kết quả được xử lý minh bạch ở R3 (winsorised
−1,056% · trimmed −1,136% · thô −1,065% ⇒ kết luận không do ngoại lai). Hồi quy là **kiểm chứng
chéo**, không phải nguồn của kết luận primary.

---

## D3 — ⭐ Thêm baseline XA (R7) + estimator GHÉP CẶP + chẩn đoán một phiên

**Đây là deviation quan trọng nhất. Nó không phải tùy hứng — nó là phản ứng bắt buộc với một
robustness check của chính prereg trả về kết quả bác bỏ giả định ngầm của prereg.**

**Prereg nói gì:** §7 R5 đặt placebo ở `ex − 40` phiên; §9(f) coi placebo là cổng: "placebo
KHÔNG cho hiệu ứng cùng cỡ". Ngầm định: **null của pipeline là 0**.

**Cái gì xảy ra:** R5 trả về **+1,180%** [+0,684; +1,693], p < 0,0001. **Null của pipeline KHÔNG
phải 0** cho population này. Nhưng cửa sổ R5 (−40..−20 phiên) nằm NGAY TRONG giai đoạn chạy giá
trước ex-date, nên nó **không tách được** hai cách giải thích:
- (a) "mã trả cổ tức đơn giản là mã tốt hơn trung bình universe" — một phần bù chất lượng; hay
- (b) "có lực mua chạy trước ngày GDKHQ".

**Làm gì thêm (4 thứ, tất cả đều là trial mới):**

| thêm | định nghĩa | trả lời câu gì |
|---|---|---|
| **R7** baseline xa | cùng thống kê 20 phiên, neo ở `ex − 250` → `ex − 230` (≈ 1 NĂM trước, ngoài mọi cửa sổ sự kiện) | tách (a) khỏi (b) |
| **paired** | `BHAR_20 − FARBASE_20`, **ghép cặp cùng một mã, cùng pipeline** | ước lượng hiệu ứng sự kiện sau khi trừ phần bù chất lượng |
| **AAR_0_1** | lợi suất bất thường của ĐÚNG một phiên đầu sau ex-date | **máy dò hiện vật**: nếu vendor đặt bước điều chỉnh nhầm sang k=+1 thì toàn bộ cổ tức sẽ nằm gọn ở đúng lợi suất này |
| **phân rã đoạn** | lợi suất thô 0→1, 1→2, 2→3, 3→5, 5→10, 10→20 | phân biệt "cú nhảy một phiên" (hiện vật) với "suy giảm dần" (kinh tế) |

**Kết quả:** R7 = **+0,637%** [+0,132; +1,136] ⇒ phần bù chất lượng CÓ THẬT nhưng chỉ bằng ~½
mức R5 ⇒ R5 = phần bù chất lượng **cộng** một phần chạy giá trước ex. AAR_0_1 = **−0,446%**,
trong khi tỉ suất gộp trung bình của P-CORE là **4,325%** — nếu là hiện vật đặt nhầm bước điều
chỉnh thì con số này phải ≈ −4,3%. **Giả thuyết hiện vật BỊ BÁC BỎ bằng số, không bằng lập luận.**

**Giá phải trả — nói thẳng:**
1. **+5 trial** ngoài 20 đã khai. Tổng thực thi **27**. Holm được tính trên **toàn bộ 27**, nên
   phần thêm tự trả chi phí bội kiểm của nó.
2. **R7 tự nó KHÔNG sống sót Holm** (p thô 0,0168 → Holm **0,118**). ⇒ phép hiệu chỉnh baseline
   là **bất định**. Vì vậy báo cáo trình **CẢ HAI** con số (thô −1,065% và ghép cặp −1,609%) và
   **primary vẫn là bản THÔ theo prereg**, không phải bản ghép cặp đẹp hơn.
3. Estimator ghép cặp nhiễu hơn ở lát mỏng: bin Y1 ra −2,839% chỉ vì baseline xa của riêng Y1 cao
   bất thường (+2,26%), trong khi Y1 **thô** không có ý nghĩa thống kê (p = 0,182). Đã ghi rõ
   trong báo cáo và trên chính hình 3.

**Vì sao vẫn làm:** bỏ qua một placebo dương có ý nghĩa rồi vẫn báo cáo con số thô như thể null
là 0 thì mới là sai. Prereg đặt R5 vào đúng để bắt chuyện này — làm ngơ kết quả của nó là vô
hiệu hoá chính prereg.

---

## D4 — Module A chạy thêm lát P-CORE

**Prereg nói gì:** §4.2 chạy Module A trên P-WIDE.

**Làm gì khác:** thêm đúng bộ thống kê đó trên P-CORE (thành viên `universe_pit`). **+1 trial.**

**Vì sao:** đường CAAR cho thấy hiệu ứng ex-day trên tập ĐẦU TƯ ĐƯỢC nhỏ hơn hẳn P-WIDE
(AR_ex +0,348% vs +1,008%; drop ratio trung vị 0,898 vs 0,833). Trích con số P-WIDE mà không kèm
điều kiện đó sẽ khiến người đọc tưởng mức under-adjustment áp dụng cho mã họ thật sự mua được.
Một con số mô tả gây hiểu nhầm về thứ có thể mua được là **lỗi**, không phải sự thận trọng.

---

## D5 — Selfcheck T27 viết SAI, đã sửa TEST chứ không sửa estimator

**Chuyện gì:** T27 bản đầu assert "CI block-bootstrap rộng hơn CI theo sự kiện", chạy trên dữ liệu
tổng hợp **không có tương quan trong block**. **Nó FAIL.**

**Chẩn đoán:** *test sai*, không phải estimator sai. Khi không có cú sốc chung theo block thì
cluster bootstrap **không có lý do gì** phải rộng hơn.

**Sửa:** T27 giờ tạo cú sốc chung theo block rồi mới assert (đo được **7,07×**). Thêm **T27b**
assert trên **dữ liệu thật**: CI block/CI sự kiện = **1,46×** ⇒ cụm theo tháng là CÓ THẬT và
CI báo cáo là bản **thận trọng**.

**Bài học giữ lại trong code** (comment tại chỗ): giả thuyết đầu tiên khi một selfcheck fail là
"tôi viết sai test", không phải "code sai" — và cách phân biệt là hỏi *bất biến này có thật sự
đúng dưới giả định tôi vừa dựng trong test không*.

---

## Điều kiện của prereg đã được GIẢI QUYẾT (không phải deviation, ghi để truy được)

| prereg | điều kiện | kết quả đo | hành động |
|---|---|---|---|
| §6.3 | "coverage `OShares` PIT < 80% ⇒ bỏ biến size" | **96,05%** | **GIỮ** `log_mcap` trong hồi quy |
| §4.1 | "(i) < 80% khớp ±1% ⇒ fail closed, Module A hạ descriptive-only" | **97,46%** khớp ±1% (92,04% trong ±0,2%) | Module A **chạy đầy đủ** — nhưng vẫn tuyên bố DESCRIPTIVE ONLY vì lý do KINH TẾ (giá tham chiếu do sở ấn định), không phải vì dữ liệu |
| §2.3 | "đo và công bố tỉ lệ `universe_pit.backfilled`" | **99,99%** | công bố ở §6 báo cáo như một hạn chế thật |
| §3 X3 | "báo riêng số bị loại vì tỉ suất > 50%" | **1** sự kiện | đã ghi trong funnel |

---

## Bảng trial cuối cùng

| | |
|---|---:|
| Khai báo trước trong prereg | 20 |
| Thực thi thật | **27** |
| Thêm do D3 | 5 (`R7`, `paired`, `paired_IS`, `paired_OOS`, `aar01`) |
| Thêm do D4 | 1 (Module A P-CORE) |
| Chênh còn lại | 1 (`R3_trim` — prereg gộp R3 thành 1 lát, thực thi tách phần trimmed thành test riêng) |

Holm tính trên **cả 27**. Kết luận primary (`BHAR_20`) có Holm-adjusted p = **0,000** nên không
phụ thuộc vào việc đếm 20 hay 27.
