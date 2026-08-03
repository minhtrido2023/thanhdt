# T5 — KHUNG QUYẾT ĐỊNH CUỐI: tổng hợp T1–T4

**Job:** `Taylor_20260803_045138` (tiếp `Taylor_20260803_021414`) · 2026-08-03 · Taylor
**Trạng thái:** RESEARCH. **Không đụng production.** Không tự tuyên bố CONFIRMED — gửi
quant-skeptic sau báo cáo này.

---

## 0. Ba câu trả lời, ngay đầu

| Câu hỏi | Trả lời |
|---|---|
| **Có tách được "edge thật" khỏi "hiện vật mô hình fill" chưa?** | **TÁCH ĐƯỢC MỘT NỬA.** Giả thuyết H_B ("Δ là hiện vật khả năng hấp thụ vốn của sổ") **BỊ BÁC BỎ hai lần bằng hai knob trực giao, cả hai lần bằng sai DẤU của đạo hàm** — không phải "chưa loại trừ được". Nhưng vế còn lại — **mức** — thì **KHÔNG**: cả hai chân đều đứng trên một tham số mô hình chưa bao giờ được neo, và T4 vừa đo được **sim vận hành xa ngoài vùng đã kiểm chứng bằng dữ liệu thật**. |
| **Số nào nên trích dẫn?** | **Giữ nguyên pin hiện hành.** Không re-pin lên. **Không trích +4,11pp (hay +4,08pp) như edge** — nó không sống sót khi hiệu chỉnh tham số fill về mức duy nhất có bằng chứng thật (§3). |
| **Còn gắn nhãn "cận dưới có thiên lệch đã biết" không?** | **KHÔNG — phải BỎ nhãn đó.** Xem §4. Đó là kết quả có hành động rõ ràng nhất của cả vòng này. |

---

## 1. Cái đã đóng được — và đóng chắc

| Phép thử | Knob | H_B đòi hỏi | Thực đo | Kết quả |
|---|---|---|---|---|
| **T3** phân rã sổ lệnh | — | (không áp dụng) | 81% Δ = **không rót 1.690B vào rổ sinh −1,77%/chu kỳ**; compounding khớp 1,51x vs 1,48x | diễn giải "capital velocity" BỊ BÁC; vòng quay vốn **giảm** 6,28→5,62x/năm |
| **T1** thang `%ADV/ngày` (×20) | trần mô hình | Δ → ~0 khi nới | Δ = **+2,51 → +4,08 → +5,20pp** (TĂNG) | **sai dấu đạo hàm** ⇒ H_B bác |
| **T2** thang NAV (×20) | kích cỡ sổ | Δ → ~0 khi nới | Δ = **+5,48 → … → +3,65pp** (cực đại ở đầu LỎNG) | **sai dấu đạo hàm** ⇒ H_B bác **lần 2, knob trực giao** |

Manipulation check **ăn** ở cả T1 và T2 (abandoned% đơn điệu đúng chiều, T2 đơn điệu hoàn hảo cả 5
rung × 2 chân). Chỉ đạt **một phần** ở cả hai (đầu lỏng vẫn 30–35% abandoned, chưa <20%) ⇒ chỉ dùng
**chiều đạo hàm**, không dùng mức tuyệt đối. Điều đó **đủ** cho một kết luận về **dấu**.

**Khung khái niệm đúng (từ code, §2 README):** `liquidity_require_positive` **chỉ** biến một
`daily_max` **vô hạn** thành **0** — nó không nới bất kỳ ràng buộc nào. L1 là siết chặt **nghiêm
ngặt** của L0. Một hiện vật kiểu "mô hình fill dễ dãi hơn thực tế" **không thể** sinh ra từ chân bị
siết chặt hơn. ⇒ Δ là **hiệu chỉnh sai số đo**, không phải alpha.

⇒ **Câu hỏi treo 3 vòng INCONCLUSIVE, ở vế "Δ có phải hiện vật capacity không", nay ĐÃ ĐÓNG: KHÔNG.**

---

## 2. Cái KHÔNG đóng được — và vì sao nó lớn hơn cái đã đóng

**T4 (`T4_RESULTS.md`) không bác được T1/T2, nhưng nó phát hiện chỗ khác hẳn.**

Tiêu chí PASS/FAIL đăng ký trước của T4 phải **tuyên bố VÔ HIỆU** (đặc tả sai — chỉ số trộn "lệnh
lớn cỡ nào" với "lệnh có khớp không"; với NAV thật ~1B nó không thể ≥1 dù mô hình fill hoàn hảo).
Đọc lại theo `fill_rate`, cái T4 **thực sự** xác lập:

- **29/30 sự kiện mua thật khớp ≥99% trong một phiên**; ca hụt duy nhất là `Rejected` của broker,
  **0/30 thất bại vì thanh khoản**.
- **Cận dưới đã xác nhận bằng dữ liệu thật: 3,86% ADV/phiên** (NCT 07-21, khớp 100%).
- **Trần engine là 20% ADV/phiên — gấp 5,2 lần cận dưới đó, hoàn toàn chưa có dữ liệu thật.**

**Đo tiếp (`bridge_sim_vs_verified.py`) — sim đứng ở đâu trên chính trục đó:**

| Chân | trung vị %ADV/phiên của 1 vị thế LAG | % phiên-fill **chạm trần** (≥19,5%) | **% VỐN** triển khai ở size > 3,86% ADV |
|---|---|---|---|
| **L0@50B (= chân pin R3)** | **19,95%** | 89,5% | **99,1%** |
| L1@50B (`LIQ_ZERO_BLOCK`) | 19,95% | 95,8% | **99,2%** |
| L0@5B (NAV nhỏ nhất) | 19,95% | 76,2% | 83,3% |

**Đây là phát hiện quan trọng nhất của cả vòng 4.** Sổ LAG của mô phỏng **không** chỉ thỉnh thoảng
chạm trần fill — nó **sống ở trần**: ~90–96% số phiên-fill nằm đúng mức trần, và **99% vốn triển
khai** được mua ở size **ngoài** vùng dữ liệu thật đã xác nhận. Trần `%ADV/ngày` **chính là ràng
buộc quyết định** của toàn bộ sổ LAG, chứ không phải một tham số phụ — và nó **chưa từng được neo**
ở điểm vận hành của chính nó.

Điều này giải thích luôn vì sao T1 nhạy đến vậy: quét một tham số đang **bind** ~90% thời gian thì
đương nhiên nó dịch chuyển mọi thứ.

---

## 3. Ghép lại thành MỘT con số: hai thiên lệch NGƯỢC CHIỀU, và chúng gần triệt tiêu nhau

Đến đây có đúng hai hiệu chỉnh đã biết, đi **ngược chiều nhau**:

| Hiệu chỉnh | Hướng | Độ lớn (đo được) |
|---|---|---|
| **(A)** L0 rót vốn vào nhóm mã live **không mua được** (T3: −1,77%/chu kỳ trên 1.690B) → chặn đi | **LÊN** | L0@0,20 → L1@0,20 = **+4,08pp** |
| **(B)** Cả hai chân giả định fill 20% ADV/phiên, trong khi dữ liệu thật chỉ xác nhận tới 3,86% | **XUỐNG** | L1@0,20 → L1@0,05 = **−4,50pp**  ·  L0@0,20 → L0@0,05 = **−2,93pp** |

Rung `LAG_LIQ_PCT=0,05` = **5% ADV/phiên** — rung gần nhất với **3,86%**, tức mức duy nhất có bằng
chứng ngoài mô phỏng. Áp **cả hai** hiệu chỉnh cùng lúc:

> **L1 @ 0,05 = 26,82%**  ·  so với **chân pin L0 @ 0,20 = 27,24%**  ⇒ **−0,42pp.**

**Hai thiên lệch gần như triệt tiêu nhau.** Con số pin hiện hành — thứ được sinh ra từ *một chân có
lỗi đo* nhân *một giả định fill lạc quan* — tình cờ nằm rất sát con số của *chân đã sửa lỗi đo*
nhân *giả định fill đã neo vào dữ liệu thật*.

⇒ **Không có cơ sở nào để re-pin LÊN.** Và cũng không có cơ sở để re-pin XUỐNG: 3,86% là **cận
dưới đã xác nhận**, không phải ước lượng khả năng fill thật — mẫu chệch có hệ thống vì
`cap_lag_orders` (fail-closed từ 07-22) **cấm** đặt lệnh lớn hơn, nên ta chỉ quan sát được đúng
vùng ta đã tự chọn là an toàn. **Vắng bằng chứng ở 20% ≠ bằng chứng vắng mặt.**

> ⚠️ **26,82% KHÔNG phải một ước lượng đã hiệu chuẩn — đọc kỹ trước khi trích** (bổ sung sau review
> quant-skeptic, đây là phản bác mạnh nhất reviewer đưa ra và nó **đúng**). Rung `0,05` được dùng
> **chỉ vì nó là điểm lưới gần nhất** với neo 3,86%; **bản thân mức 5% ADV chưa hề được xác nhận
> bằng một fill thật nào**. Nặng hơn: neo 3,86% đến từ một sự kiện **sổ CAPIT**, còn sổ **LAG** thật
> chỉ có N=2 sự kiện, lớn nhất **0,45% ADV** — không chạm tới 5% lẫn 20%. Vậy nên §3 là **phép so
> bậc độ lớn**, **không** phải hiệu chuẩn; kết luận rút ra từ nó chỉ là *"hai hiệu chỉnh cùng bậc và
> ngược chiều"*, **không** phải *"số đúng là 26,82%"*. Không re-pin ở 26,82%.

### 3b. Walk-forward IS/OOS trên CẢ 10 chân (bổ sung sau review — báo cáo gốc THIẾU mục này)

Reviewer chỉ ra T1/T2 không có bảng IS/OOS. Đã tự tính lại từ chuỗi NAV daily của từng chân
(IS 2014-01→2019-12, OOS 2020-01→2026-06-19):

| Rung | IS Δ | OOS Δ | FULL Δ |
|---|---|---|---|
| `%ADV`=0,05 | +1,49pp | +3,52pp | +2,51pp |
| `%ADV`=0,20 (gốc) | **+0,86pp** | **+7,28pp** | +4,07pp |
| `%ADV`=1,00 | +1,80pp | +8,55pp | +5,20pp |
| NAV 5B | +1,26pp | +9,59pp | +5,47pp |
| NAV 100B | +1,69pp | +5,62pp | +3,65pp |

**Hai điều rút ra, một tốt một xấu — nói cả hai:**
- ✅ **Δ dương ở CẢ HAI nửa, trên CẢ 10 chân.** Loại trừ phản bác "đây chỉ là biến động in-sample".
  Δ **lớn hơn** ngoài mẫu, không nhỏ hơn.
- ⚠️ **Nhưng độ lớn thì gần như hoàn toàn nằm ở OOS.** Ở rung gốc, IS chỉ **+0,86pp** so với OOS
  **+7,28pp** (8,5×). Cơ chế thì bền, **mức thì tập trung vào một nửa mẫu** — thêm một lý do nữa để
  **không** trích +4,08pp như một hằng số. (Nhất quán với T3: nhóm mã bị chặn là các small-cap kém
  thanh khoản, và giai đoạn 2020+ là lúc sổ LAG lớn lên đủ để đụng nhóm đó thường xuyên.)

---

## 4. Nhãn của con số pin — ĐỀ XUẤT ĐỔI (đây là hành động cụ thể của T5)

**Nhãn hiện hành trong KB:** *"đọc như một **CẬN DƯỚI**, đừng tự gắn cận trên"*.

Nhãn đó dựa trên **duy nhất** lập luận (A): "L0 mô phỏng việc mua nhóm mã live không mua được, nhóm
đó lỗ ⇒ số thật phải cao hơn". Lập luận (A) **vẫn đúng** (T3 + T1 + T2 củng cố nó). Nhưng nó **chỉ
đúng bên trong giả định fill 20% ADV**. §2 vừa chứng minh giả định đó **bind 90% thời gian và chưa
từng được kiểm chứng ở điểm vận hành** ⇒ tồn tại thiên lệch (B) đi **ngược chiều**, **cùng bậc độ
lớn** (thậm chí lớn hơn: −4,50pp vs +4,08pp trên chân L1).

Một con số có hai thiên lệch đã biết, ngược chiều, chưa net-out được **không phải là một cận dưới**.
Gọi nó là cận dưới là **tuyên bố một chiều mà bằng chứng không cấp phép** — và trong thực tế nó
đang được đọc như "giấy phép để trích một khoảng đi lên".

**Đề xuất nhãn mới (thay cho "cận dưới có thiên lệch đã biết"):**

> **ƯỚC LƯỢNG ĐIỂM, có ĐIỀU KIỆN vào một tham số mô hình chưa được neo.** Hai thiên lệch đã biết đi
> ngược chiều và ở cùng bậc độ lớn: (A) chân đo mô phỏng mua nhóm mã live không mua được — kéo số
> **xuống** ~4pp so với hệ thật; (B) mô hình fill giả định 20% ADV/phiên trong khi dữ liệu thật chỉ
> xác nhận tới 3,86%, và sim tiêu 99% vốn LAG ở size ngoài vùng đó — kéo số **lên** ~3–4,5pp. Áp cả
> hai cùng lúc cho **26,82%**, tức **sát dưới** con số pin. ⇒ **Không đọc theo chiều nào cả**: không
> phải cận dưới, không phải cận trên. **Không trích +4,08/+4,11pp như edge.**

*(Ghi chú vintage: toàn bộ T1/T2/T3 chạy trên `LAG_ADV_BASIS=close` nên chân đối chứng là **27,24%**.
Pin chính thức từ 2026-08-03 là **28,86%** ở cơ sở `price`. Kết luận trên **không phụ thuộc cơ sở
giá**: tham số chưa neo là **trần 20% ADV/phiên**, chung cho cả hai cơ sở. Muốn ghép số tuyệt đối
cho pin `price` thì phải chạy lại thang T1 với `LAG_ADV_BASIS=price` — **chưa làm trong job này**,
không được tự nội suy.)*

---

## 5. Hai câu hỏi kinh doanh tách rời (đã đăng ký trước ở README §4, nay trả lời)

### 5.1 Có giữ bộ lọc thanh khoản LAG không? — **CÓ, VÔ ĐIỀU KIỆN**
Không phụ thuộc T1–T4, và **kết quả T4 còn củng cố thêm**: live đã chặn nhóm này ở hai tầng từ
07-21/07-22 vì lý do độc lập ("không đo được thanh khoản thì đừng đặt mục tiêu mua"). T4 cho thấy
lệnh thật **không bao giờ** vượt 3,86% ADV — tức chính sách live đang tự giới hạn ở vùng an toàn.
**Không đề xuất thay đổi gì ở tầng live.**

### 5.2 Pin số nào? — **GIỮ NGUYÊN pin hiện hành, ĐỔI NHÃN**
- **KHÔNG** re-pin lên 31,32% / 33,98% / 28,86%+Δ — §3 cho thấy Δ không sống sót hiệu chỉnh (B).
- **KHÔNG** re-pin xuống 26,82% — đó là kịch bản "fill chặt" chưa được chứng minh là đúng, chỉ là
  kịch bản **duy nhất có neo ngoài**.
- **ĐỔI NHÃN** theo §4.
- **KHÔNG** bật `LIQ_ZERO_BLOCK` mặc định trong backtest production. Giữ opt-in.

---

## 6. Điều duy nhất còn có thể đóng câu hỏi này — và nó đã có sổ

Cả T1, T2, T3 đều là **mô phỏng-với-mô phỏng** (khiếm khuyết D3). T4 là neo ngoài duy nhất, và nó
mới phủ được **19% của trục** (3,86% / 20%). **Không có phép thử mô phỏng nào có thể đóng phần còn
lại** — thêm rung, thêm knob, thêm bootstrap đều sẽ cho INCONCLUSIVE lần thứ năm ở vế **mức**.

Đóng được chỉ bằng **tích luỹ fill thật ở size lớn dần**, tức đúng sổ `lag_liq_ledger.py` đã mở
(`kb/projects/lag-adv-filter-tracking.md`, mốc cứng **2026-12-15** / **2027-03-31**). T5 đóng góp
cho sổ đó **một cột mốc định lượng cụ thể** mà trước đây chưa có:

> **Chỉ số sổ cần bắt: `size_ratio = giá_trị_lệnh / (Volume_3M_P50 × Px)` của MỖI lần fill thật.**
> Mốc hiện tại: **3,86% ADV** (khớp 100%). Trần engine cần chạm để câu hỏi mức được đóng: **20%**.
> Mỗi lần fill thật vượt mốc cũ mà vẫn khớp trọn ⇒ đẩy cận dưới lên, thu hẹp thiên lệch (B).

**Trước 2026-12-15: không trích +4,11pp như edge; không đọc pin theo chiều nào.**

---

## 7. Kỷ luật đã tuân thủ / phải nói thẳng

- **Production KHÔNG bị đụng** (skill §14). Engine dùng là bản sao `pt_v23_lagcap_research.py`
  (khác production **đúng 1 dòng đã ghi chú**); chân đối chứng L0@0,20@50B tái lập pin **27,24 /
  1,81 / −18,4 / 1,48 / 1.006,33B** đến từng chữ số ⇒ A/B hợp lệ.
- **§8 tên file:** mọi chân T2 gắn `EXP_TAG=navXXX_LY` ⇒ không ghi đè CSV canonical nào.
- **Vintage:** T1/T2/T3 + bridge đều trên `bq_cache_asof20260729_postrestate` (**cùng** vintage số
  pin). T4 dùng BQ live cho ADV tháng 7-8/2026 (dữ liệu chưa có trong snapshot 07-29) — khác
  vintage **có chủ đích** và chỉ dùng cho phép so bậc độ lớn, không ghép vào bảng backtest nào.
- **§12 (cross-account):** `dnse_raw_*.jsonl` lọc `accountNo` **hai tầng** (record + snapshot lệnh).
- **N thật (skill §4):** T4 = **30 sự kiện độc lập** `(account, ngày, mã)`, **không** phải 135 order
  id và **không** phải số dòng JSONL. Sổ LAG riêng chỉ **N=2** — quá nhỏ, nhóm mở rộng là **hậu
  kiểm không đăng ký trước**, đã gắn nhãn.
- **Thất bại thiết kế đã tự khai:** tiêu chí PASS/FAIL của T4 **đặc tả sai** và phải tuyên bố VÔ
  HIỆU. Đây là khiếm khuyết D4 lặp lại ở chính phép thử được thiết kế để sửa D3.
- **Không đơn điệu ở T2 vùng 25–100B** ⇒ đã tự hạ độ tin cậy một bậc cho vùng đó (skill §10).
- **KHÔNG tự tuyên bố CONFIRMED.** Báo cáo này đi qua `bin/verify_finding.sh` (quant-skeptic) trước
  khi bất kỳ ai dùng làm căn cứ — đây là câu hỏi đã INCONCLUSIVE 3 vòng.
- **Việc còn treo, không tự làm:** (i) docstring `lag_liquidity_filter.py:23-24` vẫn ghi diễn giải
  "capital velocity" đã bị T3 bác — **file production, cần duyệt**; (ii) thang T1 ở
  `LAG_ADV_BASIS=price` để ghép số tuyệt đối cho pin 28,86% — chưa chạy.

---

## 8. BỔ SUNG 2026-08-03 (job `Taylor_20260803_052705`) — thang T1 ở `LAG_ADV_BASIS=price`: ghép số cho pin 28,86%

Đây là việc "còn treo (ii)" ở §7 của chính báo cáo này. Chi tiết đầy đủ + manipulation check:
**`T1_PRICE_RESULTS.md`** cùng thư mục. Tóm tắt những gì nó đổi và những gì nó KHÔNG đổi:

**Điều kiện hợp lệ — ĐẠT, chặt hơn T1 gốc:** bản sao nghiên cứu tái lập **cả hai** chân của A/B
production 08-02 đến từng chữ số — L0@0,20 = **28,86% / 1,90 / −17,8% / 1,62 / 1.178,01B** (= pin
chính thức) và L1@0,20 = **32,71% / 1,95 / −19,1% / 1,71 / 1.699,09B** (= `L3_both`).
Self-check **0 VND** cả 6 chân, `EXIT=0` cả 6.

| `%ADV/ngày` | L0 | L1 | **Δ (`price`)** | Δ (`close`, T1 gốc) |
|---|---|---|---|---|
| 0,05 | 26,51% | 29,18% | **+2,67pp** | +2,51pp |
| 0,20 | **28,86%** (pin) | 32,71% | **+3,85pp** | +4,08pp |
| 1,00 | 28,68% | 34,24% | **+5,56pp** | +5,20pp |

**Ba điều rút ra:**

1. **Kết luận cơ chế KHÔNG phụ thuộc cơ sở giá — đúng như §7 dự báo trước khi chạy.** Δ vẫn **tăng
   đơn điệu** khi nới capacity trên cả ba rung ⇒ H_B (hiện vật capacity) vẫn bị bác bằng **sai dấu
   đạo hàm**, y hệt cơ sở `close`. Manipulation check cũng đơn điệu đúng chiều ở cả hai chân
   (L0 54,9→31,0%; L1 71,4→42,8%) và cũng **không** đạt ngưỡng <20% ⇒ vẫn chỉ dùng chiều đạo hàm.
2. **Phép ghép hai thiên lệch ngược chiều (§3) TÁI LẬP ở cơ sở của pin** — và mạnh thêm một ý:

   | | `close` (§3) | `price` (mới) |
   |---|---|---|
   | (A) LÊN L0@0,20 → L1@0,20 | +4,08pp | **+3,85pp** |
   | (B) XUỐNG L1@0,20 → L1@0,05 | −4,50pp | **−3,53pp** |
   | Áp CẢ HAI: L1@0,05 vs chân pin L0@0,20 | 26,82% vs 27,24% = **−0,42pp** | 29,18% vs 28,86% = **+0,32pp** |

   Ở **cả hai** cơ sở, áp đồng thời hai thiên lệch cho một số **cách chân pin < 0,5pp** ⇒ "hai
   thiên lệch gần triệt tiêu nhau" là kết luận **bền theo cơ sở giá**. Hơn nữa **dấu của phần dư
   ĐỔI CHIỀU** (−0,42 → +0,32) ⇒ phần dư nằm trong nhiễu, không phải hiệu ứng có hướng ⇒ **củng cố
   nhãn mới ở §4**: đọc pin **không theo chiều nào**, không cận dưới cũng không cận trên.
3. **Một nghịch đảo MỚI phải nói thẳng:** chân **L0** ở cơ sở `price` **không đơn điệu** (rung 1,00
   = 28,68% **thấp hơn** rung gốc 28,86%, −0,18pp); ở cơ sở `close` thì đơn điệu. Không đổi kết
   luận về dấu (Δ vẫn đơn điệu, và nghịch đảo này còn *làm Δ tăng*), nhưng theo kỷ luật đăng ký
   trước ⇒ **hạ một bậc độ tin cậy cho giá trị tuyệt đối ở rung 1,00**. MaxDD của L1 lại **xấu
   hơn** L0 ở rung 0,20 và 1,00 (−19,1/−20,0 vs −17,8/−18,0) — lặp lại cảnh báo vận hành của T2.

**KHÔNG đổi gì ở §4/§5:** pin giữ **28,86%**, nhãn giữ "ước lượng điểm có điều kiện", bộ lọc giữ vô
điều kiện, `LIQ_ZERO_BLOCK` giữ opt-in, **không** tuyên bố CONFIRMED mới (đây là bước ghép số, không
phải phép thử mới), câu hỏi **MỨC** vẫn chỉ đóng được bằng sổ `lag_liq_ledger.py` ở mốc
**2026-12-15 / 2027-03-31**.

**Việc treo (i) ở §7 — docstring `lag_liquidity_filter.py` — ĐÃ XONG** trong cùng job này
(docstring-only, chứng minh cơ học bằng AST-identity sau khi gỡ docstring: IDENTICAL; selfcheck
13/13 offline + 22/22 `--live`). Diff lưu ở `docstring_fix_20260803.diff`.
