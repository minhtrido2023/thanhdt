# KẾT QUẢ — CAPIT: cơ chế thoát / sizing-timing / thanh khoản
Job `Taylor_20260720_164006` · pre-registration: [PREREG.md](PREREG.md) · 2026-07-20
Scripts: `build_panel.py` → `analyze.py` → `diag_and_axes23.py` → `axis3_liquidity.py`
Dữ liệu: `data/bq_cache/ticker_prune` (PIT), 14 washout event 2014-2026, 66 vị thế.
**KHÔNG sửa gì trong production.**

---
## 0. ĐÍNH CHÍNH TIỀN ĐỀ DISPATCH — "K=5 slot" là SAI
Production cap rổ ở **15 tên**, không phải 5 (`nsmallest(15,"pbz")` ở CẢ
`pt_v23_audit_2014.py::capit_basket` lẫn `deploy_golive_dt5g_v4/golive_recommend_v23.py`;
`tier_position_limit={t:15}`). Size mỗi tên = `capit_size / len(basket)` — chia cho kích thước
rổ THỰC TẾ, không phải hằng số.

Đo thực tế 14 event: rổ **min 3 / median 5 / max 7 tên**. Trần 15 **ràng buộc 0/14 event**.
Và 6/14 event có rổ < 5 → dù K=5 có tồn tại thật thì nó cũng không ràng buộc.
**→ "chọn K" KHÔNG phải tham số sống. Câu hỏi trục 2 gốc không có nội dung để tối ưu.**

---
## 1. TRỤC 1 — CƠ CHẾ THOÁT: **NO-GO 6/6, và là NO-GO MẠNH**
Không phải "thiếu bằng chứng" — mọi biến thể đều **kém baseline một cách nhất quán**.
Sleeve return trung bình 14 event (vốn thoát sớm nằm im 0%, đo bảo thủ):

| biến thể | mean | median | worst event | p5 vị thế | t (cluster 14 event) | n_fire | LOO |
|---|---|---|---|---|---|---|---|
| **E0 baseline (hold 60)** | **+14,36%** | **+14,49%** | −16,74% | −24,86% | — | — | — |
| E1 pb_z ≥ −0,5 | +9,77% | +10,80% | −6,93% | −13,68% | −1,46 | 30 | STABLE |
| E2 pb_z ≥ 0 | +11,20% | +11,78% | −12,37% | −20,08% | −1,48 | 16 | STABLE |
| E3 vỡ cổng chất lượng | +11,08% | +10,96% | −11,00% | −20,08% | −1,79 | 29 | STABLE |
| E4 vỡ cổng nặng | +13,62% | +13,41% | −16,99% | −26,97% | −2,24 | 6 | STABLE |
| E5 time-decay (ret<0 @30) | +13,30% | +13,10% | −16,25% | −26,40% | −1,38 | 18 | STABLE |
| E6 time-decay (pb_z @30) | +12,72% | +12,86% | −15,92% | −26,40% | −1,94 | 27 | STABLE |

**Cả 6 trượt tiêu chí (i)** (không cải thiện — đều XẤU đi). LOO **STABLE theo hướng ÂM** ở cả 6:
bỏ bất kỳ event nào cũng không cứu được. Bản robustness (vốn thoát ăn return VNINDEX) cùng dấu,
cùng thứ hạng. **→ NO-GO, và mạnh hơn NO-GO thông thường: đây là bằng chứng ủng hộ thiết kế hiện tại.**

### Vì sao — cơ chế đã đo được
| biến thể | phiên thoát (median) | ret tại lúc thoát | ret nếu giữ tới 60 | **bỏ lỡ** |
|---|---|---|---|---|
| E1 | 2 | +6,78% | +13,20% | **−6,43%** |
| E2 | 4 | +10,98% | +19,56% | **−8,58%** |
| E3 | 23 | +0,16% | +8,64% | **−8,48%** |
| E4 | 20 | −6,46% | +2,55% | **−9,01%** |
| E6 | 31 | −7,83% | +0,60% | **−8,43%** |

Mọi cơ chế thoát — dù dựa trên tín hiệu, chất lượng hay thời gian — đều **bán trước đúng đợt hồi
phục mà CAPIT đang chờ**. E1/E2 tệ nhất vì pb_z hồi phục CHÍNH LÀ tín hiệu luận điểm đang đúng:
thoát khi pb_z hồi = cắt lãi ở phiên thứ 2-4. E3/E4 (chất lượng) cũng thua vì báo cáo tài chính
xấu đi trong khủng hoảng là **trễ và đồng chu kỳ** — đến lúc số liệu xác nhận thì giá đã hồi.

### Nhượng bộ trung thực — cái giá là ĐUÔI TRÁI, không phải trung bình
E1 **cải thiện đuôi trái rõ**: worst event −6,93% (vs −16,74%), p5 vị thế −13,68% (vs −24,86%).
Tức thoát sớm KHÔNG vô dụng — nó mua bảo hiểm downside với giá **−4,6pp mean**. Nếu về sau user
muốn giới hạn drawdown của sleeve hơn là tối đa hoá return, E1 là công cụ đúng đắn để bàn.
Nhưng theo tiêu chí pre-register (tối ưu risk-adjusted return), **NO-GO**.

### Về power — đính chính kỳ vọng dispatch
Dispatch kỳ vọng "~70 position-event granular hơn N=14". **Không đúng về mặt thống kê**: độ phân
tán TRONG event = 13,40%, GIỮA event = 16,62% → các vị thế trong cùng một washout chia sẻ đúng
một cú sốc thị trường. **N hiệu dụng vẫn là 14 event, không phải 66 vị thế.** Mọi t-stat báo trên
đã cluster theo event (đúng); nếu tính t theo 66 vị thế độc lập sẽ phóng đại power ~2x một cách sai.

**DSR: KHÔNG báo** — không có biến thể nào qua (i)-(v), nên không có config nào để deploy.
Điều kiện tiên quyết không đạt (giống 3 job trước).

---
## 2. TRỤC 2 — SIZING / TIMING: **NO-GO (weighting) + KHÔNG KIỂM ĐỊNH ĐƯỢC (timing)**

### 2a. K / trần rổ — không có gì để tối ưu (xem §0)

### 2b. Depth-weight vs equal-weight — **NO-GO (nhiễu)**
| cách weight | mean | median | worst | vs equal | t | LOO |
|---|---|---|---|---|---|---|
| equal (production) | +14,36% | +14,49% | −16,74% | — | — | — |
| depth (∝ độ sâu pb_z) | +15,27% | +14,57% | −10,67% | +0,91pp | 0,64 | STABLE |
| rank-weight | +14,98% | +14,12% | −12,22% | +0,62pp | 0,55 | **FLIP** |

t = 0,55-0,64 → **nhiễu thuần**, xa ngưỡng. Nhất quán với IC(pb_z_entry, ret60) = **+0,038**
(median +0,043) — dấu này còn **NGƯỢC** kỳ vọng (dương = pb_z sâu hơn cho return THẤP hơn), nhưng
độ lớn ~0 nên đọc đúng là: **trong rổ đã lọc, độ sâu pb_z không phân biệt được tên nào tốt hơn.**
Kết quả này khớp hoàn toàn với 3 job selection trước (pb_z/DCF/gate đều NO-GO) — cùng một sự thật:
**edge của CAPIT nằm ở TIMING VÀO (mua khi washout), không nằm ở việc chọn/xếp hạng trong rổ.**
Equal-weight giữ nguyên.

### 2c. Entry timing 11:15 — **KHÔNG KIỂM ĐỊNH ĐƯỢC (không đủ dữ liệu)**
Dữ liệu intraday (`data/intraday_full.pkl`) chỉ phủ **2025-06-16 → 2026-05-12** → chỉ **2/14
washout event** (2025-10-20, 2026-03-09), 8 vị thế. Không thể kết luận, và tôi **không** kết luận.

Chỉ mô tả (N=8, KHÔNG phải bằng chứng): trên ngày vào lệnh, giá 11:15 **đắt hơn** open +0,36%,
close đắt hơn open +1,43%. **Dấu NGƯỢC với edge BUY@11:15 của lệnh thường** (job
`Taylor_20260702_031608`: 11:15 rẻ hơn open −17,6bps). Hợp lý về mặt cơ chế — ngày sau washout
có xu hướng hồi trong phiên, nên mua sớm rẻ hơn.
**Khuyến nghị: KHÔNG giả định edge 11:15 generalize cho CAPIT.** Cần tích thêm event có intraday
mới trả lời được (~1-2 event/năm → còn rất lâu). Trong lúc đó giữ nguyên hành vi hiện tại là lựa
chọn đúng (không có bằng chứng để đổi).

---
## 3. TRỤC 3 — THANH KHOẢN: **GO có điều kiện (safeguard, không phải alpha)**
Đây là trục duy nhất tìm thấy vấn đề thiết kế thật.

### 3a. Cổng thanh khoản ≥2 tỷ chỉ kiểm tra ĐÚNG NGÀY VÀO
Ngày washout là ngày **volume spike theo định nghĩa** → ADV ngày vào **hệ thống hoá phóng đại**
thanh khoản có thật trong 60 phiên nắm giữ:
- median ADV20 sau khi vào / ADV ngày vào = **0,54** (p10 = 0,32) — hụt gần một nửa.
- **8/66 vị thế (12%) rơi xuống DƯỚI chính cổng 2 tỷ** sau khi vào: NNC 0,43 tỷ · **NCT 0,87 tỷ**
  · NTC 1,00 · THG 1,24 · RAL 1,46 · VCS 1,85 · TLG 1,92 · MCH 1,98.
- NCT (tên đang trong rổ 07-20) nằm trong nhóm này — đợt 2026-03-09 nó tụt về 0,87 tỷ/ngày.

### 3b. Equal-weight khiến capacity của CẢ sleeve bị TÊN MỎNG NHẤT quyết định
Capacity = deploy được bao nhiêu mà vẫn thoát được trong 2 phiên ở ≤10% ADV:

| | capacity sleeve |
|---|---|
| median 14 event | **2,2 tỷ** |
| event chặt nhất (2016-01-18) | **0,4 tỷ** |
| 2026-03-09 (gần nhất) | **1,0 tỷ** |

Sensitivity — số event đủ capacity theo quy mô sleeve (`NAV_book_LAG × capit_size`):

| sleeve cần | equal-weight |
|---|---|
| 0,38 tỷ | 14/14 ✅ |
| 0,75 tỷ | 13/14 |
| 1,50 tỷ | 10/14 ⚠️ |
| 3,75 tỷ | **4/14** ❌ |
| 7,50 tỷ | **1/14** ❌ |

**→ Xác nhận nhận định của user: đợt 07-20 sức mua nhỏ nên NCT chưa thành vấn đề.** Nhưng ràng
buộc bắt đầu cắn từ **sleeve ~1,5 tỷ** và trở nên nghiêm trọng từ **~3,75 tỷ** — tức hoàn toàn
nằm trong tầm với khi NAV lớn lên. Đây là vấn đề thật của tương lai gần, không phải giả định xa.

### 3c. Đề xuất — CAP, KHÔNG PHẢI TILT (đã kiểm tra và bác bỏ tilt)
Tôi đã test cách "weight ∝ ADV" (nghiêng về tên thanh khoản): capacity median tăng 2,2 → 21,8 tỷ
(9,3x), return **trung tính** (diff +0,20pp, t=0,15, LOO FLIP = nhiễu) — NHƯNG **worst event xấu
đi rõ: −16,74% → −26,91%**, vì nó dồn tiền vào ít tên. **KHÔNG khuyến nghị tilt.**

Khuyến nghị dạng **CAP thuần** (đúng dạng user gợi ý), giữ nguyên equal-weight và selection:
```
w_i = min( capit_size / len(basket),  X% × ADV20_i × D / NAV_book_LAG )
phần dư KHÔNG dồn sang tên khác → để lại tiền mặt (sleeve under-deploy)
X = 10% (thông lệ chống market impact), D = 2 phiên (thoát trong 2 ngày)
ADV20 = median 20 phiên TRƯỚC ngày vào, KHÔNG dùng ADV ngày washout (§3a)
```
Tính chất: **thuần phòng thủ** — không tạo capacity, không hứa alpha, chỉ chặn việc ôm một vị thế
không thoát nổi.

> ⚠️ **ĐÍNH CHÍNH (job Taylor_20260720_170223, xác nhận lại Taylor_20260720_172614).** Câu gốc ở
> đây ghi "ở quy mô sleeve hiện tại nó KHÔNG kích hoạt (14/14 event đủ capacity ở 0,38 tỷ) → wire
> bây giờ = zero thay đổi" — **SAI**. Bảng capacity §3b phía trên tính bằng ADV20 **SAU** khi vào
> (`axis3_liquidity.py`, k∈[1,20]), trong khi công thức chốt dùng ADV20 **TRƯỚC** ngày washout
> (cửa sổ nhân quả duy nhất live dùng được). Chạy đúng cửa sổ PRE: **cap kích hoạt 1/14 event** —
> **NNC ngày 2016-01-18** (ADV20_pre 0,335 tỷ → cap 0,067 tỷ/tên, equal-weight đòi 0,076 tỷ),
> lệch **8.975.500đ** ở 1 vị thế. 13/14 event còn lại không kích hoạt. Bảng §3b giữ nguyên vì nó
> mô tả đúng biến thể POST, chỉ **không phải** biến thể được wire.
> Tác động **live hiện tại vẫn = 0**: rổ 2026-07-20 (NCT/PVT/SAB/VNM) không chạm cap tới tận
> sleeve 0,75 tỷ. Bằng chứng: `exp_capitadvcap/selfcheck_capit_adv_cap.py`.

→ wire bây giờ = zero thay đổi hành vi live **hiện tại** (không phải zero thay đổi lịch sử), và
có sẵn khi NAV lớn lên.
Điểm quan trọng: dùng ADV20 **trước** washout thay vì ADV ngày washout đã tự sửa lỗi phóng đại
ở §3a — đây mới là phần có giá trị nhất, độc lập với việc có cap hay không.

**Giới hạn cần nói rõ**: X=10%/D=2 là **thông lệ ngành, KHÔNG phải tham số backtest ra**. Không
có dữ liệu market-impact thật để hiệu chỉnh. Đừng trích dẫn như đã kiểm chứng bằng số.

---
## 4. TỔNG KẾT VERDICT
| trục | verdict | ghi chú |
|---|---|---|
| **1. Cơ chế thoát** | **NO-GO 6/6 (mạnh)** | Hold-60 cố định là ĐÚNG. Thoát sớm bỏ lỡ −6,4→−9,0pp. LOO stable âm. Không báo DSR (không có config để deploy). |
| **2a. K / trần rổ** | **KHÔNG CÓ NỘI DUNG** | Trần 15 ràng buộc 0/14 event; tiền đề "K=5" của dispatch sai. |
| **2b. Depth-weight** | **NO-GO** | t=0,55-0,64 nhiễu; IC(pb_z, ret60)≈0. Giữ equal-weight. |
| **2c. Entry timing** | **KHÔNG KIỂM ĐỊNH ĐƯỢC** | Intraday chỉ phủ 2/14 event. N=8 gợi ý dấu NGƯỢC edge 11:15 → đừng giả định generalize. |
| **3. Thanh khoản** | **GO có điều kiện (safeguard)** | Cổng 2 tỷ chỉ kiểm tra ngày vào; 12% vị thế rơi dưới cổng sau đó. Đề xuất cap %ADV + dùng ADV20 trước washout. |

## 5. Về câu hỏi "biến thể nào đáng paper-first?"
Dispatch nêu giả thuyết exit-mechanism dễ paper hơn selection (áp dụng ngay cho vị thế đang hold).
**Lập luận đó đúng về mặt cơ chế, nhưng không còn liên quan** — không có biến thể exit nào đáng
paper, vì cả 6 đều kém baseline.

Thứ đáng đưa lên là **cap %ADV (trục 3)**, và nó *không cần* paper-trading: ở quy mô sleeve hiện
tại cap không kích hoạt trên rổ live (xem ĐÍNH CHÍNH §3c — lịch sử có 1/14 event kích hoạt, nhưng
rổ hôm nay còn cách cap khá xa), nên paper sẽ quan sát được đúng **0 sự kiện** — paper ở đây là
nghi thức rỗng, không phải bằng chứng. Đường đi đúng: **selfcheck xác minh công thức +
quant-skeptic + user sign-off**.
**Đã wire (phương án B, job Taylor_20260720_172614) — nhánh `capit-adv-cap-20260721`, chưa merge.**

## 6. Kết luận rộng hơn — 4 job liên tiếp đang chỉ về cùng một chỗ
`pb_z rank` (NO-GO) → `DCF filter/tiebreaker` (NO-GO) → `DCF rank chính` (NO-GO) → `nới quality
gate` (NO-GO) → giờ `exit / weighting` (NO-GO). Năm hướng, năm lần cùng một kết quả, cộng thêm
IC(pb_z, ret60) ≈ 0 đo trực tiếp ở job này.

Đọc thẳng: **toàn bộ edge của CAPIT nằm ở QUYẾT ĐỊNH VÀO — mua rổ chất lượng khi breadth washout
kích hoạt. Mọi thứ sau đó (chọn tên nào, weight bao nhiêu, thoát khi nào) đều là nhiễu.**
Đề nghị **dừng tối ưu vi mô CAPIT**. Ngân sách R&D còn lại nên chuyển sang trục có nhiều dư địa
hơn (vd điều kiện kích hoạt washout, hoặc sizing theo state) — hoặc chuyển hẳn khỏi CAPIT.
