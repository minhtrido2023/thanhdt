# T4 — NEO NGOÀI MÔ PHỎNG: đối chiếu mô hình fill của engine với FILL THẬT (DNSE)

**Job:** `Taylor_20260803_045138` (tiếp `Taylor_20260803_021414`) · 2026-08-03
**Script:** `t4_fill_anchor.py` · **Dữ liệu thô:** `t4_fills.json`
**Nguồn:** `data/execution_logs/dnse_raw_*.jsonl` (2026-07-01 → 2026-08-02) **đã lọc `accountNo`**
theo coding_guidelines §12 — lọc **hai lần**: ở tầng record (`account_no`) và ở tầng snapshot lệnh
(`payload.orders[].accountNo`), vì file là **dùng chung** giữa SpaceX (0002023347) và ZaloPay
(0001743768). Book của mỗi lệnh lấy từ `data/trade_plans/plan_*.json` (`mode=="live"` only).

## 1. Đại lượng đo — và vì sao phải đo ba cái, không phải một

Mô hình fill của engine (`pt_v23_audit_2014.py:1329-1335`):

```
daily_max = (Volume_3M_P50 × Px) × 0.20      # trần mua MỖI PHIÊN cho MỘT vị thế
```

| | Công thức | Đo cái gì |
|---|---|---|
| **size_ratio** | `ý_định_mua / (ADV×0,20)` | lệnh thật **lớn cỡ nào** so với trần engine |
| **fill_rate** | `đã_khớp / ý_định_mua` | lệnh đó **có khớp không** |
| **ratio_prereg** | `đã_khớp / (ADV×0,20)` | **chỉ số đã đăng ký trước** ở README §4 |

`ratio_prereg = size_ratio × fill_rate`. Đây chính là vấn đề — xem §4.

**N = số SỰ KIỆN độc lập** (skill §4), tức mỗi `(account, ngày, mã)`, **không** phải số dòng JSONL
và **không** phải số `order id`: executor cắt một ý định mua thành nhiều slice (huỷ-đặt-lại giá, lô
lẻ). 135 order id thật → **30 sự kiện độc lập**.

## 2. Kết quả

| Nhóm | N sự kiện | trung vị `size_ratio` | max `size_ratio` | fill ≥99% | trung vị `ratio_prereg` |
|---|---|---|---|---|---|
| **A. Sổ LAG** (phạm vi **đăng ký trước**) | **2** | 0,0115 | 0,0227 | **2/2** | **0,0115** |
| B. Mọi lệnh mua live (engine áp **cùng** trần 20%ADV) | 30 | 0,0011 | **0,1929** | **29/30** | 0,0011 |
| C. CAPIT (size lớn nhất trong kỳ) | 12 | 0,0083 | 0,1929 | **12/12** | 0,0083 |
| D. custom30V parking | 13 | 0,0003 | 0,0012 | 13/13 | 0,0003 |
| E. DISCRETIONARY (TV1) | 2 | 0,0392 | 0,0452 | 1/2 | 0,0222 |

**Sự kiện lớn nhất từng khớp trọn:** NCT 07-21 (SpaceX) — 47,2tr VND = **19,3% trần engine** =
**3,86% ADV trong một phiên**, khớp **100%**. Kế đó: SIP 07-21 = 3,66% trần = **0,73% ADV**;
CSV 07-28 (LAG) = 2,27% trần = **0,45% ADV**… tất cả khớp trọn.
⚠️ **Đơn vị — sửa 2026-08-03 sau review quant-skeptic:** `size_ratio` là **tỷ lệ trên TRẦN**
(=`ý_định/(ADV×0,20)`); muốn ra **%ADV** phải nhân **0,20**, không phải 100. Bản đầu của mục này ghi
nhầm SIP/CSV theo %trần mà gắn nhãn %ADV (sai hệ số 5×). Neo chịu lực **NCT 3,86% ADV** tính đúng
ngay từ đầu (0,1929 × 0,20) và **không** bị ảnh hưởng.
⚠️ **Neo 3,86% đến từ sổ CAPIT, KHÔNG phải sổ LAG.** Sổ LAG thật chỉ có N=2 sự kiện, lớn nhất
**0,45% ADV**. Dùng neo CAPIT cho LAG hợp lệ về **cơ chế** (engine áp **cùng** trần 20%ADV cho mọi
sổ) nhưng đây là **suy rộng liên-sổ**, phải gắn nhãn — cận dưới riêng cho sổ LAG chỉ là **0,45%**.

**Trường hợp DUY NHẤT không khớp đủ — và nó KHÔNG phải chuyện thanh khoản.** TV1 07-28: 100/400
cp. Truy về từng slice: `status` của 2 slice hụt là **`Rejected`** (broker từ chối), không phải
`Canceled`/hết phiên. Toàn bộ 135 slice: 67 `Filled`, 64 `Canceled` với 0 khớp (= hành vi
huỷ-đặt-lại-giá bình thường của executor, ở tầng sự kiện vẫn mua đủ), **2 `Rejected`**. ⇒ **0/30
sự kiện thất bại vì lý do thanh khoản.**

**Cơ sở giá ADV không ảnh hưởng kết luận:** `Price/Close` trên đúng bộ (mã, ngày) này có trung vị
**1,0000** (max 1,0943) ⇒ chọn `LAG_ADV_BASIS=close` hay `price` cho ra cùng một bảng. (Nhất quán
với ghi nhận ở `context_pack`: hệ số hội tụ về 1,00 những năm gần đây.)

## 3. Đối chiếu với tiêu chí ĐĂNG KÝ TRƯỚC — và tại sao phải tuyên bố VÔ HIỆU

Tiêu chí README §4: *trung vị `filled_value/(ADV×0,20)` ≥ 1,0 ⇒ PASS; < 0,5 ⇒ FAIL.*

Đo được: **0,0115** (LAG) / **0,0011** (mở rộng). Đọc thô thì rơi vào vùng "FAIL".

**Không được đọc như vậy. Tiêu chí này bị đặc tả SAI, và phải nói thẳng.**

Chỉ số `ratio_prereg` = `size_ratio × fill_rate` — nó **trộn** hai thứ khác hẳn nhau: lệnh
**lớn cỡ nào** và lệnh **có khớp không**. Với tài khoản thật ~1B NAV, một slot LAG cỡ 17–20tr VND
trên một mã ADV hàng chục tỷ thì `size_ratio ~ 0,001–0,02` là **số học thuần tuý**, độc lập hoàn
toàn với việc mô hình fill đúng hay sai. Nói cách khác: **với NAV 1B, chỉ số này KHÔNG THỂ ≥1 dù
mô hình fill có hoàn hảo đến đâu** — nó chỉ ≥1 nếu ta đặt lệnh ≥20% ADV, điều mà `cap_lag_orders`
(gate live, fail-closed từ 07-22) **cố tình cấm**.

⇒ Đây là **khiếm khuyết D4 lặp lại ở chính T4** (một can thiệp/phép đo không tác động được vào cơ
chế định nhắm). Theo đúng kỷ luật đã đăng ký cho T1 ("manipulation không ăn ⇒ phép thử VÔ HIỆU,
cấm kết luận từ số"), **verdict PASS/FAIL đã đăng ký của T4 tuyên bố VÔ HIỆU**, không phải FAIL.
Ghi nhận điều này là một **thất bại thiết kế của kế hoạch, không phải một kết quả**.

## 4. Cái T4 THỰC SỰ xác lập được (đọc lại theo `fill_rate`)

Câu hỏi trả lời được với dữ liệu này không phải "mô hình fill có đúng ở 20% ADV không" mà là
**"mô hình fill đã được xác nhận an toàn tới ngưỡng nào"**:

- **Cận dưới đã xác nhận: 3,86% ADV/phiên** (= 0,193× trần engine). Ở mọi size ≤ ngưỡng này,
  **29/30 sự kiện khớp trọn trong một phiên**, ca hụt duy nhất là lỗi `Rejected` của broker.
- **Không có bằng chứng nào cho thấy engine lạc quan trong dải đã quan sát.** Thực tế khớp
  **ít nhất bằng** giả định engine ở mọi size từng thử.
- **Nhưng dải 3,86% → 20% ADV (5,2 lần) hoàn toàn CHƯA được kiểm chứng bằng dữ liệu thật.** Đúng
  cái dải mà T1 vừa chứng minh Δ **rất nhạy** với nó (Δ = +2,51 → +5,20pp khi quét `%ADV` 20×).

**Giới hạn phải nói thẳng (đã đăng ký trước ở README §4):**
- N=2 cho sổ LAG là **quá nhỏ để làm phép thử**; nhóm B/C là **mở rộng KHÔNG đăng ký trước** (engine
  áp cùng trần 20%ADV cho mọi sổ nên về cơ chế là hợp lệ, nhưng phải gắn nhãn hậu-kiểm).
- Mẫu **chệch về phía dễ fill** một cách có hệ thống: `cap_lag_orders` giới hạn size **trước khi**
  lệnh ra thị trường ⇒ ta chỉ quan sát được đúng vùng mà chính ta đã chọn là an toàn.
- 1 tháng, thị trường không có phiên nào căng thanh khoản bất thường.
- Đây là **kiểm tra bậc độ lớn**, **không** phải hiệu chuẩn tham số.

## 5. Hệ quả cho câu hỏi gốc

1. **T4 KHÔNG bác được T1.** Không có dấu hiệu nào cho thấy mô hình fill lạc quan trong dải đo được
   ⇒ không có căn cứ để nói "cả hai chân đều lạc quan" (nhánh FAIL của README §4 **không** kích hoạt).
2. **T4 cũng KHÔNG cấp phép neo mức.** Tham số 20%ADV/phiên vẫn **chưa được neo** — chỉ được xác
   nhận an toàn tới 3,86%. Vì Δ nhạy mạnh với chính tham số này (T1 §5.2), **không có cơ sở dữ
   liệu thật nào để pin bất kỳ con số nào ở rung 20%** — kể cả 27,24%, kể cả 31,32%.
3. **Đường duy nhất để khép câu hỏi này bằng dữ liệu thật** là tích luỹ fill ở size lớn dần —
   tức đúng sổ theo dõi `lag_liq_ledger.py` đã mở, với mốc cứng 2026-12-15 / 2027-03-31
   (`kb/projects/lag-adv-filter-tracking.md`). T4 **định lượng được** cái mà sổ đó cần bắt:
   **`size_ratio` của mỗi lần fill thật**, và cột mốc cần vượt là **3,86% ADV**.
