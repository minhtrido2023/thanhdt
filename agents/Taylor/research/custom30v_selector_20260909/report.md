# VÒNG 4 — custom30V selector: kết quả 4 chân
job `Taylor_20260909_153631` · 2026-09-09 · **PAPER-ONLY** · **VERDICT: NO-GO cả 4 chân**

Tiền đăng ký: `PREREG.md` (md5 `454f40c0a6846c260e34439f98a58d71`), viết **trước** khi chạy chân
treatment nào — 7 tiêu chí GO, N_trials=4, hằng số lấy từ production/tài liệu đã validate, không
grid-search. Mô tả nền: `PHASE0.md`. Không có chân nào ngoài 4 chân đã khai.

---

## 0. Kết quả một dòng

| chân | luật | ΔCAGR | MaxDD | Calmar | Sharpe | verdict |
|---|---|---|---|---|---|---|
| **L1a** | pool 60 → **90** | **+1,07pp** | −16,33% | 1,833 | 1,95 | **NO-GO** (C5a, C6) |
| **L1b** | pool 60 → **120** | **+2,62pp** | **−14,95%** | **2,105** | **2,05** | **NO-GO** (C5a, C6) |
| L2 | thay `1/PCF` → lợi suất dòng tiền 3 năm (`eycfq`) | +0,09pp | −18,00% | 1,608 | 1,87 | **NO-GO** (C1,C2,C3,C4,C5a,C6) |
| L3 | ghim số ngân hàng, đổi *tên* ngân hàng theo lens Gordon | +0,31pp | −18,34% | 1,591 | 1,85 | **NO-GO** (C1,C2,C4,C5a,C6) |
| ctrl | pin R3 | — | −17,785% | 1,6229 | 1,83 | — |

**Không chân nào qua đủ 7 tiêu chí.** L2 và L3 trượt sạch và **đóng trục**. L1a/L1b qua **6/8** mục
con (C1, C2, C3, C4a, C4b, C5b) và **trượt C5a (DSR) + C6 (bootstrap)** — đó là *chưa chứng minh
được*, không phải *đã bác bỏ*; §5 nói rõ phải đọc thế nào.

## 1. Chân control — harness sạch (C7)

CSV md5 **`7d053e6201c9d107685ff4d1dd9d2d2a`** = **TRÙNG BYTE** pin R3.
CAGR 28,8627% · Final NAV 1.178,0099B · MaxDD −17,785% · Calmar 1,6229 — trùng pin từng chữ số.
`self-check 0 VND` (cash-flow identity **và** final-NAV identity, cả BAL lẫn LAG) trên **cả 5 chân**.
Bẫy `sys.path` vòng 2 xử lý tường minh (`sel_engine.py` re-insert thư mục nghiên cứu ngay sau
`sys.path.insert(0, WORKDIR)`); control chạy qua **chính đường đó** nên md5 trùng là bằng chứng bản
copy `custom_basket.py` trung thực.

---

# L2 — chân dòng tiền bền: NO-GO, và nó nói rõ VÌ SAO

`eycfq` = thay `rank_pct(1/PCF)` bằng `rank_pct(cfy3)`, `cfy3 = (CF_OA_3Y/3)/vốn hoá thô`; tài chính
giữ khuôn `2·ey` của `eyfin`. Độ phủ đã đo trước: **100,0%** trên tên phi-tài-chính, 0/48 kỳ dưới 80%.
Thước đo THẬT SỰ khác: Spearman(1/PCF, cfy3) = **0,319**.

| tiêu chí | L2 |
|---|---|
| C1 ΔCAGR > +0,385 | **+0,087** ❌ |
| C2 Calmar ≥ 1,6229 | 1,6082 ❌ |
| C3 IS & OOS cùng dương | +0,80 / **−0,60** ❌ |
| C4a / C4b | 1,82 / 4,19 ❌ |
| C5a DSR | 0,555 ❌ |
| C6 CI95 | [−1,10; +1,31] ôm 0 ❌ |

**Ý nghĩa:** đây là lần thứ **tư** trục chất-lượng-dòng-tiền bị bác trong custom30V, và lần này ở
dạng mạnh nhất còn lại — không phải cổng, không phải sàn, mà **thay hẳn một chân định giá bằng
thước đo 3 năm**, trên dữ liệu phủ 100%. Kết quả: nhiễu (+0,09pp) với OOS âm.

Cộng với `eyonly` (bỏ hẳn chân 2 = −0,05pp) đã đo 07-14, ta có kết luận cơ học đáng ghi:
**chân thứ hai của yieldcombo không mang thông tin — bỏ nó, giữ nó, hay thay nó bằng một thước đo
tương quan chỉ 0,32 đều ra cùng một chỗ.** Rổ được quyết định gần như hoàn toàn bởi `rank(1/PE)`.
⇒ **Đóng trục (1). Không đề xuất biến thể dòng tiền nào nữa.**

# L3 — ghim số lượng ngân hàng, đổi *tên* ngân hàng: NO-GO đúng như prior

Cơ chế chạy **đúng như thiết kế**: `d_fin_name_share = 0,00pp` và `d_bank_name_share = 0,00pp` —
số lượng ngân hàng bất biến tuyệt đối, chỉ danh tính đổi. Lens dùng nguyên văn
`banking_valuation_framework.md` (`ROE_Min3Y ≥ 0,08`, Gordon `(ROE5Y−0,05)/0,08`,
`z(discount)+z(ROE5Y)+z(NP_YoY)`), không hằng số mới.

ΔCAGR **+0,31pp** — dưới sàn nhiễu 0,385 — với **Calmar TỆ ĐI** (1,591 < 1,623) và MaxDD sâu hơn
(−18,34% vs −17,79%). C4a 1,16 / C4b 1,44 (một rổ đơn lẻ lớn hơn cả tổng delta = chữ ký nhiễu).

**Ý nghĩa:** prior khai trước ("largely already owned … pb_z trong route bank IC +0,065 t=1,17")
được xác nhận. Chọn *ngân hàng nào* trong nhóm ngân hàng **không có gì để thu hoạch** — 1/PE đã làm
hết việc, đúng như registry 07-14 dự đoán. ⇒ **Đóng nốt hướng route-aware cuối cùng.** Sau L3,
trục (2)+(3) không còn dạng nào chưa đo.

---

# L1 — ĐỘ RỘNG POOL: chân duy nhất còn sống, nhưng KHÔNG PHẢI điều nó trông giống

## 2. Phản ứng ĐƠN ĐIỆU — điều kiện tiền đăng ký đã đạt

| pool | CAGR | ΔCAGR | Sharpe | MaxDD | Calmar | IS | OOS |
|---|---|---|---|---|---|---|---|
| 60 (ctrl) | 28,86 | — | 1,83 | −17,79 | 1,623 | 27,09 | 30,48 |
| **90** | 29,93 | **+1,07** | 1,95 | −16,33 | 1,833 | +0,20 | +1,90 |
| **120** | 31,48 | **+2,62** | 2,05 | **−14,95** | **2,105** | +1,44 | +3,75 |

Đơn điệu trên **mọi** chiều (CAGR, Sharpe, MaxDD, Calmar, IS, OOS) — chính điều kiện đọc kết quả
đã chốt trước ở PREREG §3. C4a 0,42/0,24 và C4b 0,45/0,37 (không rổ nào chiếm quá nửa delta).
PBO toàn họ **0,0216**. Cả hai chân **IS và OOS cùng dương**, và OOS mạnh hơn IS — ngược với chữ ký
IS-overfit đã giết `v3latest`.

## 3. Nhưng nó trượt C5a và C6 — và đó là kết luận, không phải chi tiết

| | L1a | L1b |
|---|---|---|
| **C5a DSR vs SR_ctrl** (ngưỡng 0,95) | 0,656 ❌ | 0,778 ❌ |
| **C6 bootstrap CI95** (block 63 phiên) | [−1,20; +2,75] ❌ | **[−0,116; +3,98]** ❌ |
| C6 P(Δ > 0) | 0,795 | **0,969** |

L1b **sát mép** — cận dưới CI95 là −0,116pp, P(Δ>0) = 96,9%, DSR 0,778. Nhưng ngưỡng chốt trước là
0,95 và "loại trừ 0", và **sát mép vẫn là trượt**. Không có "gần đạt" (PREREG §5).

Đọc đúng: **12,5 năm không đủ mẫu để phân biệt +2,6pp/năm với nhiễu quỹ đạo** ở mức tin cậy 95%.
Đây là *chưa chứng minh được*, khác hẳn L2/L3 (*đã bác bỏ*).

## 4. ĐỐI CHỨNG BẮT BUỘC (§6) — và đây mới là phát hiện thật của L1

### 4.1 KHÔNG phải đổi mức rủi ro ✅
| chân | w_stock | w_park | **w_equity** | Δw_equity |
|---|---|---|---|---|
| ctrl | 21,65 | 51,35 | 72,995 | — |
| L1a | 21,13 | 51,71 | 72,843 | **−0,15pp** |
| L1b | 21,09 | 51,72 | 72,806 | **−0,19pp** |

Ngưỡng ±2pp; thực đo **−0,2pp**. Tỷ trọng cổ phần **không đổi** ⇒ delta đến từ **chọn mã**, không
phải từ nâng beta. (Ngược hẳn trục A vòng 3, nơi Δw_equity là +6,8…+15,1pp.)

### 4.2 NHƯNG nó LÀ một cú cược ngành — cổng §6.2 KÊU ❌
| chân | % tên tài chính | Δ | % tên ngân hàng | Δ |
|---|---|---|---|---|
| ctrl | 33,19 | — | 25,28 | — |
| L1a | 26,88 | **−6,32pp** | 21,67 | −3,61pp |
| L1b | **20,76** | **−12,43pp** | **17,22** | **−8,06pp** |

Ngưỡng khai trước là 5pp; L1b vượt **gấp 2,5 lần**. Theo đúng luật đã chốt: **phải báo cáo L1 như
một cú CƯỢC NGÀNH, không phải như "selector tốt hơn".**

**Cơ chế rõ ràng và không tranh cãi:** ngân hàng là nhóm **thanh khoản nhất** thị trường VN, nên một
pool định nghĩa bằng *top-60 thanh khoản* **cấu trúc-hoá** việc quá tải ngân hàng. Nới pool lên 120
không "chọn giỏi hơn" — nó **pha loãng** một vị thế ngành mà Phần 0 đã đo là **49,1% trọng số toàn
kỳ / 67,5% OOS, và đang tăng**.

**Điều này đặt cạnh `fincap` mới thú vị.** Cả hai đều giảm tỷ trọng tài chính, nhưng ngược dấu:

| cách giảm ngân hàng | cơ chế | ΔCAGR |
|---|---|---|
| `fincap` 0,30 / 0,45 / 0,50 / 0,55 (07-14) | **cắt trọng số** cùng tập tên | −0,64 / −0,84 / −0,74 / −0,32 |
| **L1b pool 120** (vòng này) | **đổi tập tên được cạnh tranh** | **+2,62** |

Cùng một mục tiêu ngành, hai cơ chế, kết quả trái dấu ~3pp. `fincap` bắt rổ giữ đúng những tên đó
với trọng số nhỏ hơn; nới pool cho **132 tên đã qua cổng chất lượng nhưng chưa bao giờ được chấm
điểm** vào thay. Nếu có gì đáng nghiên cứu tiếp sau vòng này, đó là chỗ này — **không phải** vì
+2,62pp (chưa chứng minh được), mà vì **hai cơ chế cùng đích lại cho kết quả trái dấu**.

### 4.3 Cái giá: thanh khoản xe giảm 71% ⚠️
| chân | ADV rổ trung vị | sức park 20%/ngày |
|---|---|---|
| ctrl | **1.743,7B/ngày** | 348,7B/ngày |
| L1a | 1.172,3B/ngày (−33%) | 234,5B/ngày |
| L1b | **510,3B/ngày (−71%)** | **102,1B/ngày** |

Cap 20%-ADV là **trần dòng chảy mỗi ngày, được engine cưỡng chế thật** cho cả mua lẫn bán
(`simulate_holistic_nav.py:440-446`) ⇒ số của L1b **đã** tính cả ràng buộc chặt hơn 3,4 lần này,
không phải con số vô ràng buộc. Nhưng hệ quả vận hành là thật: xe mỏng đi 3,4 lần thì **trần dung
lượng của cả V2.4 dịch xuống tương ứng**. Ở NAV live hiện tại (1-5B) không ràng buộc; ở vùng
≥100-150B thì đây là ràng buộc chính, đúng lớp vấn đề registry #10/#19 đã gặp.

### 4.4 Turnover — trong ngưỡng ✅
ctrl 32,3%/quý · L1a 35,5% (×1,10) · L1b 38,7% (×1,20) — dưới trần 1,5× nên **không** phải trừ thêm
chi phí trước khi so C1.

---

## 5. Chấm điểm đầy đủ 7 tiêu chí

| # | ngưỡng | L1a | L1b | L2 | L3 |
|---|---|---|---|---|---|
| C1 ΔCAGR | > +0,385pp | +1,07 ✅ | +2,62 ✅ | +0,09 ❌ | +0,31 ❌ |
| C2 Calmar | ≥ 1,6229 | 1,833 ✅ | 2,105 ✅ | 1,608 ❌ | 1,591 ❌ |
| C3 IS & OOS | cùng dương | +0,20/+1,90 ✅ | +1,44/+3,75 ✅ | +0,80/−0,60 ❌ | +0,23/+0,38 ✅ |
| C4a LOYO năm | < 0,50 | 0,42 ✅ | 0,24 ✅ | 1,82 ❌ | 1,16 ❌ |
| C4b per-window | < 0,50 | 0,45 ✅ | 0,37 ✅ | 4,19 ❌ | 1,44 ❌ |
| **C5a DSR** | **> 0,95** | **0,656 ❌** | **0,778 ❌** | 0,555 ❌ | 0,523 ❌ |
| C5b PBO | < 0,50 | **0,0216 ✅** (chung cả họ 5 config) | | | |
| **C6 bootstrap CI95** | **loại trừ 0** | **[−1,20;+2,75] ❌** | **[−0,12;+3,98] ❌** | [−1,10;+1,31] ❌ | [−0,37;+0,84] ❌ |
| C7 self-check | 0 VND + md5 pin | ✅ | ✅ | ✅ | ✅ |

---

## 6. Kết luận

1. **NO-GO cả 4 chân. Không wire gì.** Vòng NO-GO thứ tư liên tiếp; L2/L3 **đóng trục (1), (2), (3)**
   của roadmap selector — sau vòng này cả ba hạt giống user nêu đều đã có câu trả lời đo được, ở
   mọi dạng khả dĩ.
2. **L1 (độ rộng pool) là lead duy nhất còn sống**, và giá trị của nó KHÔNG nằm ở +2,62pp (chưa
   chứng minh được, DSR 0,778 / CI ôm 0) mà ở chỗ nó **cho thấy pool định-nghĩa-bằng-thanh-khoản
   chính là cơ chế sinh ra vị thế overweight ngân hàng** mà 07-14 đã cảnh báo là "không ai chủ ý
   đặt và không ai quản" — và là cách duy nhất đo được để giảm nó mà **không** mất tiền như `fincap`.
3. **Câu hỏi tiếp theo là câu hỏi cho USER/Mike, không phải câu hỏi backtest** (giống hệt kết luận
   07-14, giờ có thêm bằng chứng): rổ đỗ tiền đang có **49% trọng số ở ngân hàng, 67,5% giai đoạn
   OOS, đỉnh 93,3%**. Đó có phải vị thế muốn giữ có chủ ý không? Nếu KHÔNG — nới pool là đòn bẩy
   rẻ nhất đã biết, đổi lại **thanh khoản xe giảm 71%**. Nếu CÓ — khai báo tường minh thành rule
   ngành kiểm soát được, thay vì để nó phát sinh như tác dụng phụ của định nghĩa pool.
4. **Nếu Mike/user muốn đi tiếp trục L1**, việc cần làm KHÔNG phải quét thêm điểm pool (đó là tuning
   và sẽ chết ở DSR y hệt). Việc cần làm là **tiền đăng ký lại một câu hỏi khác**: *"tách riêng
   hiệu ứng pha-loãng-ngành khỏi hiệu ứng thêm-tên-rẻ"* — placebo đếm-khớp (giữ pool 60 nhưng ép
   đúng số tên tài chính mà pool-120 chọn) sẽ trả lời được, và `BASKET_PLACEBO_FIN` đã có sẵn trong
   `custom_basket.py`. Chưa làm trong vòng này vì nó **không nằm trong 4 chân đã tiền đăng ký**.

**Artifacts:** `PREREG.md` · `PHASE0.md` · `sel_engine.py` · `custom_basket.py` (bản copy nghiên cứu,
`eycfq` + `BASKET_BANKSWAP` mặc định OFF) · `run_leg.sh` · `analyze.py` · `analyze_out.txt` ·
`ab_metrics.csv` · `peryear.csv` · `perwindow.csv` · `exposure_decomp.csv` · `members_decomp.csv` ·
`run_{ctrl,L1a,L1b,L2,L3}.log`.
