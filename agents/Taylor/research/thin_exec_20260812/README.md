# Chiến lược thực thi cho mã THANH KHOẢN MỎNG — case TV1

Job `Taylor_20260812_091343` · Taylor (Quant/Algo) · 2026-08-12
Chỉ đạo user (John) qua Mike, thread 1521735922066919515.

> **TRẠNG THÁI: R&D. KHÔNG có dòng production nào bị sửa.** Toàn bộ code trong thư mục
> này là `exp_*`/`probe_*` (§8 coding_guidelines), không import và không chạy
> `trading_bot/`. Không có patch nào được áp. `hard_no_chase_ceiling_vnd` (§24) được
> giữ nguyên là ràng buộc cứng trong MỌI kịch bản mô phỏng — không kịch bản nào mua
> trên trần.

---

## 0. TL;DR

Lệnh TV1 không khớp vì **HAI nguyên nhân KHÁC NHAU**, và gộp chúng lại là cách chắc
chắn sửa sai chỗ:

| | Nguyên nhân | Bằng chứng | Sửa được bằng thuật toán? |
|---|---|---|---|
| **A** | **Trần giá nằm DƯỚI thị trường.** Trần 20.000đ chốt 2026-07-23, giá lên 20.200–20.500 từ 08-11 | 08-12: **0cp** khớp ở giá ≤20.000đ trên tổng 39.500cp | **KHÔNG.** Mọi cơ chế, mọi κ đều cho fill = 0. Đây là câu hỏi CHÍNH SÁCH → user |
| **B** | **Executor tự bóp KL hiển thị.** `ceil_allow = 30% × KL ĐÃ khớp trong ngày` ⇒ đầu phiên allowance ≈ 0 | 08-11: 12.400cp có sẵn ở ≤20.000đ, bot khớp **100cp**. Mô phỏng cơ chế hiện tại cho **0cp** (thật: 100cp) | **CÓ.** Bỏ riêng ràng buộc này: mô phỏng cho 1.860–3.300cp |

**Khuyến nghị**: P1 (trần thành LUẬT có dung sai) — **GO, cần user duyệt** (chính sách).
P2 (đổi mẫu số pacing sang KL kỳ vọng + clamp đuôi) — **GO có điều kiện**, cần paper
trial + quant-skeptic. P3/P4 (rải nhiều phiên / chọn khung giờ) — **NO-GO như một thay
đổi**, hệ đã đúng sẵn / lợi ích hạng hai. P5 (depth-aware từ L2) — **CHƯA KẾT LUẬN
ĐƯỢC**, thiếu dữ liệu, phải log sống trước.

---

## 1. Dữ liệu — có gì và KHÔNG có gì

Đo thật, không suy diễn (§9, mục 5 của dispatch):

| Nguồn | Có | Không có |
|---|---|---|
| `vnstock` 3.4.2 / VCI | Bar **1 phút** OHLCV, 2023-09 → 2026-08-12, mọi mã | — |
| `Quote.price_depth()` | — | **`NotImplementedError`** — không có sổ lệnh |
| `Quote.intraday()` | tick + phía chủ động (Buy/Sell) | **CHỈ PHIÊN HÔM NAY**, không có lịch sử |
| DNSE G1 (live) | 10 mức giá + KL mỗi mức | không lưu lịch sử; `brokers.py:Quote` **vứt bỏ** mảng này (chỉ giữ `bidPrice1`/`offerPrice1`) |

**Hệ quả bắt buộc phải mang theo mọi con số dưới đây:** không tồn tại order-book lịch sử
cho mã VN ở nguồn ta có. Mọi chữ "depth" trong báo cáo này = **KL ĐÃ KHỚP**, không phải
KL chờ. KL đã khớp là **cận dưới** của thanh khoản khả dụng (hàng chờ không ai lấy thì
không thành khớp). Vì vậy **câu hỏi 1 của dispatch — "đo depth thật theo khung giờ" —
CHỈ trả lời được ở dạng KL khớp theo khung giờ, không phải depth sổ lệnh.**

Rổ: **23 mã**, ADV20 200–2.500tr/phiên (TV1 = 672tr), chọn **đều theo hạng ADV**
(`probe_pull_1m.py:pick_cohort`) — không chọn tay. N = **1.840 phiên-mã**.

Hai lỗi đơn vị của chính tôi đã phát hiện và sửa trước khi kết luận: (a) VCI trả giá
theo **nghìn đồng** (19.8 = 19.800đ) ⇒ `max_child_value` không bao giờ ràng buộc;
(b) bucket khung giờ lệch 30 phút ⇒ "nghỉ trưa" ăn nhầm 13:00–13:30. Cả hai đã sửa,
mọi số dưới đây chạy sau khi sửa.

---

## 2. Cơ chế đang chạy — đọc từ code, không từ mô tả

`trading_bot/executor.py::_child_qty` (đọc 2026-08-12). TV1 là
`book="DISCRETIONARY_SPECIAL"`, side buy ⇒ đi vào nhánh **ADV20-paced**:

```
floor_allow = 10% × ADV20_vnd / giá        − đã_khớp     # max_participation
ceil_allow  = 30% × KL_luỹ_kế_trong_ngày   − đã_khớp     # capit_realized_participation_ceiling
allowance   = min(floor_allow, ceil_allow)               # <1 lô ⇒ trả 0 (WAIT_QUOTA)
```

Với TV1 (ADV20 695tr, giá 20.000đ): `floor_allow` ≈ **3.475cp** — KHÔNG ràng buộc,
lệnh 2 account gộp chỉ 3.300cp. Ràng buộc thật là `ceil_allow`.

**`ceil_allow` là một cái bẫy quả trứng-con gà**: mẫu số là KL đã khớp **không có ta**.
Lúc 09:15 nó bằng 0 ⇒ ta được hiện 0. Người bán duy nhất của phiên xuất hiện lúc 09:40
chỉ nhìn thấy vài lô của ta. Ghi chép thật trong plan 08-12 mô tả đúng chữ ký này:
lệnh con **100cp → 200cp → 300cp** — bám theo 30% KL luỹ kế.

Và trên TV1 08-11 nó hỏng theo cách tệ nhất có thể: **KL ở giá ≤20.000đ tập trung ĐẦU
phiên** (giá chạy từ 19.800 lên 20.500 trong ngày), tức đúng lúc allowance nhỏ nhất.
Tới lúc allowance đủ lớn thì không còn hàng dưới trần nữa.

---

## 3. Mô phỏng — thiết kế và ĐỐI CHIẾU VỚI THỰC TẾ

`exp_fill_sim.py` replay từng phút: allowance tính đúng công thức trên (chỉ dùng tape đã
xảy ra — không nhìn trước), refresh mỗi `slice_interval_min=8`, fill mỗi phút
`= min(KL đang hiện, κ × KL khớp ở giá ≤ trần)`.

**κ = phần của tape ở dưới trần mà lệnh nằm chờ giành được.** KHÔNG quan sát được từ dữ
liệu này ⇒ chạy 3 mức và xem kết luận có đổi dấu không (không).

### 3.1 Đối chiếu với kết quả THẬT (`exp_tv1_reality_check.py`)

Đây là điểm kiểm chứng ngoài mẫu duy nhất tồn tại — kết quả khớp lệnh thật TV1 08-11
(email khớp lệnh DNSE, skill `dnse-fill-reconciliation`): **100cp / 3.300cp**.

| Ngày | Cơ chế | Mô phỏng | Thật |
|---|---|---|---|
| 08-11 | hiện tại (mọi κ 0,15→1,00) | **0cp** | **100cp** |
| 08-11 | bỏ trần 30% | 1.860cp (κ=0,15) → 3.300cp (κ≥0,34) | — |
| 08-12 | **mọi** cơ chế, **mọi** κ | **0cp** | 0cp (vị thế không đổi) |

Mô phỏng tái lập thất bại thật **sai lệch đúng 1 lô**. Đây là **n=1 điểm kiểm chứng** —
là sự chứng thực, KHÔNG phải bằng chứng hiệu lực thống kê. Nhưng nó đủ để loại bỏ khả
năng mô hình fill của tôi lạc quan quá đà theo hướng làm hỏng kết luận.

### 3.2 Phân rã tầng ràng buộc (κ-free, N=1.840)

Lệnh = 10% ADV20, trần = giá đóng cửa phiên trước:

```
L1 GIÁ    %phiên KL thật ở ≤trần = 0                    6,3%
L1 GIÁ    %phiên KL ở ≤trần < KL cần                   16,4%
L2 PACING %phiên executor chỉ cho hiện < KL cần        86,0%
```

Trong **1.538 phiên mà THỊ TRƯỜNG CÓ ĐỦ HÀNG dưới trần**: cơ chế hiện tại khớp
**0,804**, bỏ trần 30% khớp **0,910**. Chênh **+10,6pp là do chính ta tự bóp**, không
do thị trường.

### 3.3 Bền theo κ (không đổi dấu)

| κ | hiện tại | bỏ trần 30% | chênh |
|---|---|---|---|
| 0,15 | 0,547 | 0,615 | +6,8pp |
| 0,34 | 0,681 | 0,776 | +9,5pp |
| 0,60 | 0,727 | 0,841 | +11,4pp |

---

## 4. Bốn hướng thay thế — định lượng

### P1 — Trần no-chase phải là LUẬT có dung sai, không phải một SỐ đông cứng

`exp_ceiling_tolerance.py`. Trần = `anchor × (1+τ)`, anchor = giá đóng cửa **L phiên
trước** (mô phỏng đúng bệnh: trần chốt lúc duyệt chương trình rồi không xem lại).
Lệnh 10% ADV20, κ=0,34, N=1.840:

| anchor cũ | τ | fill TB | %phiên fill=0 | giá TB trả / anchor |
|---|---|---|---|---|
| 5 phiên | **0%** | 0,627 | **22,4%** | −2,24% |
| 5 phiên | 1% | 0,708 | 14,1% | −1,89% |
| 5 phiên | 2% | 0,750 | 9,6% | −1,68% |
| 5 phiên | **3%** | **0,783** | **6,1%** | **−1,47%** |
| 5 phiên | 5% | 0,797 | 4,0% | −1,29% |
| 10 phiên | 0% | 0,634 | 22,8% | −3,63% |
| 10 phiên | 3% | 0,756 | 9,3% | −2,74% |
| 20 phiên | 0% | 0,663 | 21,8% | −5,84% |
| 20 phiên | 3% | 0,748 | 11,0% | −4,86% |

**Đọc bảng này cho đúng — "giá trả" ÂM ở mọi τ vì có chọn lọc sống sót**: ta chỉ khớp
khi giá ở dưới trần, nên có điều kiện đã khớp thì luôn trả dưới anchor. Cái phải đọc là
**mức tăng** khi nới τ: từ τ=0 lên τ=3% trả thêm **+0,77pp** giá, đổi lấy **+15,6pp
fill** và tỷ lệ phiên trắng tay **22,4% → 6,1%**. Tỷ lệ đổi chác ~20:1 nghiêng về nới.

**Anchor càng cũ càng đắt** (−2,24% → −5,84% khi đi từ 5 lên 20 phiên) mà fill gần như
không hơn — tức là **giữ trần cũ không "mua rẻ", nó chỉ mua ÍT**.

**Ca TV1 cụ thể** (`out/tv1_ceiling_case.csv`, 40 phiên):

| Giai đoạn | KL khớp ở ≤20.000đ |
|---|---|
| 06-18 → 07-17 (17 phiên) | **0** mỗi phiên — giá ở 20.600–23.300 |
| 07-20 → 08-10 (15 phiên) | 4.300 → 96.600cp/phiên, **100% KL phiên** ở 10/15 phiên |
| 08-11 | 12.400 / 42.700cp (**29%**), tập trung đầu phiên |
| 08-12 | **0** / 39.500cp |

Trần 20.000đ được duyệt 2026-07-23 — đúng lúc TV1 ở 19.900. Nó **đúng trong 3 tuần rồi
hết đúng**, và không có cơ chế nào phát hiện việc đó. Chương trình gom size 5% NAV chỉ
bắt đầu 08-11 (chỉ đạo user 08-10 tối), tức **bắt đầu đúng phiên giá vượt trần**. Trong
15 phiên trước đó thị trường có tổng cộng >300.000cp ở dưới trần cho một nhu cầu
3.300cp — thanh khoản chưa bao giờ là ràng buộc trong cửa sổ đó.

> **Đây là quyết định CHÍNH SÁCH, không phải kỹ thuật (§22) ⇒ user quyết.** Tôi không
> tự nới trần và không đề xuất nới riêng lẻ cho TV1 như một ngoại lệ. Đề xuất là đổi
> *dạng* của tham số: `hard_no_chase_ceiling_vnd` (số tuyệt đối) → sinh ra từ luật
> `anchor × (1+τ)` tại lúc lập plan, với anchor được refresh và τ do user chốt một lần
> cho cả lớp lệnh discretionary. Trần vẫn là **ràng buộc cứng ở tầng executor** đúng
> như §24 — không đụng gì tới `_limit_price`/guard cuối.

### P2 — Đổi mẫu số pacing: KL **kỳ vọng** tới giờ này thay cho KL **đã khớp**

`exp_expected_floor.py`. Thay
`ceil_allow = 30% × cum_vol` bằng
`ceil_allow = 30% × max(cum_vol, ADV20_cp × f(t))`, với `f(t)` = tỷ trọng KL luỹ kế
trung vị tới phút t, **đo trên chính rổ mã mỏng** (120 phiên):

```
f(09:15)=4,5%   f(10:00)=19,8%   f(11:00)=41,1%   f(13:30)=63,7%   f(14:30)=95,8%
```

…**cộng clamp đuôi**: fill luỹ kế không bao giờ vượt **50% KL THẬT** đã khớp. Đây mới
là chỗ đúng để đặt bất biến "fleet không thành đa số một phiên mỏng" — nó phải neo vào
tape THẬT. Còn **KL HIỂN THỊ thì không cần bị neo vào tape đã xảy ra: hiện lệnh không
tiêu thụ thanh khoản của ai.** Đó chính là lỗi thiết kế của cơ chế hiện tại.

Kết quả (κ=0,34, lệnh 10% ADV20, anchor cũ 5 phiên, N=1.840):

| Cơ chế | fill TB (τ=0) | fill TB (τ=3%) | %fill=0 (τ=3%) | giá/anchor | %tape TB | p95 | %phiên >50% tape |
|---|---|---|---|---|---|---|---|
| hiện tại | 0,627 | 0,783 | 6,1% | −1,47% | 11,7% | 23,9% | 0,0% |
| **P2 kỳ vọng** | **0,697** | **0,860** | **4,3%** | −1,42% | 14,6% | 34,0% | **0,0%** |
| bỏ hẳn trần | 0,705 | 0,868 | 4,3% | −1,41% | 14,7% | 34,0% | 0,0% |

**P2 lấy được ~97% lợi ích của việc bỏ hẳn trần, giá trả gần y hệt (−1,42 vs −1,47%),
mà vẫn giữ được bảo vệ đuôi.**

**Vì sao KHÔNG đề xuất bỏ hẳn trần** (`exp_participation_bound.py`, cận trên κ-free —
tức nếu ta là người mua duy nhất): bỏ hẳn trần cho phép ta chiếm **>50% tape ở 6,9% số
phiên và >80% ở 3,5%**, vì `floor_allow` neo vào ADV20 chứ không vào KL thật của phiên
hôm đó, mà **12,7% số phiên có KL <30% ADV20**. Trần 30% đang bảo vệ đúng nhóm này.
Con số "%tape" trong bảng trên bị chính κ chặn ở 34% nên **KHÔNG đọc nó như thước đo
rủi ro đuôi** — thước đo đuôi là cận trên κ-free vừa nêu.

### P3 — Rải nhiều phiên: **hệ đã đúng sẵn, NO-GO cho việc thay đổi**

`exp_intraday_profile.py::multi_session` — số phiên cần để gom, trần 10% ADV20/phiên,
κ=0,34, N=1.150 lần thử:

| Kích thước lệnh | trung vị | p90 | max |
|---|---|---|---|
| 10% ADV | 1 phiên | 2 | 4 |
| 30% ADV | 4 phiên | 4 | 7 |
| 60% ADV | 7 phiên | 8 | 15 |

Lệnh TV1 gộp 2 account = **~10% ADV** ⇒ **1–2 phiên là bình thường**, và quy trình lập
plan hằng ngày đã tự làm việc rải này. Không có gì để sửa ở đây.

Điều CẦN sửa là **kỳ vọng và cách đọc**: một lệnh 10% ADV trên mã mỏng khớp một phần
là **hành vi đúng**, không phải sự cố. Đề xuất (rẻ, không đụng logic): plan sinh ra cho
mã có `KL_lệnh / ADV20 > 5%` ghi thẳng vào `note` số phiên kỳ vọng theo bảng trên, để
báo cáo EOD không đọc partial fill là lỗi.

### P4 — Chọn khung giờ: **NO-GO như một thay đổi độc lập**

`out/intraday_profile.csv`, 120 phiên × 23 mã, tỷ trọng KL khớp:

| khung giờ | trung vị | trung bình |
|---|---|---|
| mở cửa <09:30 | 9,1% | 8,9% |
| 09:30–10:00 | 11,9% | 11,3% |
| **10:00–11:00** | **19,9%** | **20,9%** |
| 11:00–11:30 | 8,6% | 9,1% |
| 13:00–13:30 | 14,7% | 14,9% |
| 13:30–14:00 | 13,3% | 12,9% |
| 14:00–14:30 | 15,4% | 15,7% |
| 14:30–14:45 | 0,0% | 0,8% |
| 14:45+ (ATC) | 5,0% | 5,6% |

10:00–11:00 đặc thật nhưng chỉ **~1,5× mức đều** — hạng hai so với P1/P2 (+15,6pp và
+7,7pp). Và quan trọng hơn: **với lệnh NẰM CHỜ, chọn giờ gần như vô nghĩa** — nằm chờ
cả phiên không tốn gì, cứ ở đó là bắt được mọi nhịp. Profile giờ chỉ đáng dùng khi
**buộc phải cắn giá chủ động**, hoặc như đầu vào `f(t)` của P2 — và đó chính là chỗ
tôi đã dùng nó.

Một quan sát phụ đáng ghi: **14:45+ (ATC) chỉ 5,0% KL trung vị**, cá biệt có mã 0,2%.
Câu trả lời phản xạ "dồn vào phiên ATC cho chắc khớp" **không đúng với nhóm mã này**.

### P5 — Depth-aware sizing từ L2: **CHƯA KẾT LUẬN ĐƯỢC — thiếu dữ liệu**

Đây là hướng dispatch nêu (2b) và tôi **không kiểm chứng được**, nói thẳng thay vì suy
diễn:

- DNSE G1 **có** trả 10 mức giá + KL (`client.latest_quote` → `quotes[].bid/offer` là
  list `{price, quantity}`).
- `brokers.py::DNSEBroker.get_quote` **chủ động vứt bỏ** các mảng này: nó chỉ lấy
  `arr[0]["price"]` thành `bidPrice1`/`offerPrice1`, còn dòng
  `raw.update({k:v for k,v in qt.items() if not isinstance(v,(list,dict))...})` loại mọi
  field dạng list. `Quote` do đó **không có KL ở bất kỳ mức giá nào**.
- Không có lịch sử order-book ⇒ **không backtest được** hướng này. Bất kỳ con số
  fill-rate nào tôi đưa ra cho P5 sẽ là bịa.

**Bước đúng tiếp theo cho P5 là LOG TRƯỚC, KẾT LUẬN SAU**: ghi mảng L2 10 mức vào
`dnse_raw_<date>.jsonl` mỗi lần `get_quote` (chỉ ghi, không đổi hành vi đặt lệnh),
tích luỹ 4–6 tuần trên đúng nhóm mã mỏng, rồi mới đo được "KL chờ thật ở dưới trần" —
đại lượng mà toàn bộ báo cáo này đang phải thay bằng cận dưới (KL đã khớp).

---

## 5. Khuyến nghị GO/NO-GO

| | Hướng | Tác động đo được | Verdict | Bước kế tiếp |
|---|---|---|---|---|
| **P1** | Trần no-chase = `anchor×(1+τ)`, anchor refresh, τ chốt cho cả lớp | fill 0,627→0,783 (τ=3%); phiên trắng tay 22,4%→6,1%; giá +0,77pp | **GO — CHÍNH SÁCH, user quyết** | User chốt τ. Sửa ở **plan generator**, KHÔNG đụng `_limit_price`/guard §24 |
| **P2** | `ceil_allow = 30%×max(cum_vol, ADV20×f(t))` + clamp fill ≤50% tape thật | fill +7,0pp (τ=0) / +7,7pp (τ=3%); giá không đổi; đuôi vẫn chặn | **GO CÓ ĐIỀU KIỆN — kỹ thuật** | Paper trial ≥4 tuần (mẫu HYBRID 08-10) → quant-skeptic → mới wire |
| **P3** | Rải nhiều phiên | hệ đã đúng: 10%ADV = 1–2 phiên | **NO-GO** (không đổi logic) | Chỉ thêm dòng kỳ vọng số phiên vào `note` của plan |
| **P4** | Chọn khung giờ | 10–11h chỉ 1,5× mức đều; vô nghĩa với lệnh nằm chờ | **NO-GO độc lập** | Đã tái sử dụng làm `f(t)` trong P2 |
| **P5** | Depth-aware theo L2 | **không đo được** | **CHƯA KẾT LUẬN** | Log L2 vào `dnse_raw` trước, 4–6 tuần, rồi mới đo |

### Thứ tự ưu tiên
1. **P1 trước, một mình.** Nó lớn hơn P2 gấp đôi, và **nếu trần vẫn dưới thị trường thì
   P2 không cứu được gì** (08-12: mọi cơ chế, mọi κ → 0cp). Sửa P2 trước là sửa đúng cơ
   chế nhưng sai thứ tự.
2. **P2 sau, qua paper trial.** Đây là thay đổi tầng thực thi, chạm `_child_qty` — module
   lõi (`executor.py`: **11 selfcheck phụ thuộc**, §23) ⇒ phải quét rộng khi làm thật.
3. **P5 chỉ bắt đầu bằng logging.**

---

## 6. Giới hạn — đọc kèm mọi con số

1. **Không có order-book lịch sử.** "Depth" = KL đã khớp = **cận dưới**. Fill thật có
   thể cao hơn mô phỏng ở mọi kịch bản (kể cả kịch bản hiện tại).
2. **κ không neo được.** Kết luận **thứ hạng** giữa các cơ chế bền qua κ ∈ {0,15; 0,34;
   0,60} (không đổi dấu lần nào); **mức tuyệt đối** thì không — đừng trích "fill 0,86"
   như một dự báo.
3. **n=1 điểm kiểm chứng ngoài mẫu** (TV1 08-11, lệch 1 lô). Chứng thực, không phải
   validation thống kê.
4. **Chưa có NAV backtest.** Toàn bộ báo cáo đo **fill-rate và giá thực thi**, KHÔNG đo
   lợi nhuận. **Không được trích các con số này như CAGR/edge.** Fill cao hơn chỉ tốt
   khi bản thân quyết định mua là đúng — đó là câu hỏi khác (DCF/DD của TV1, đã PASS
   riêng).
5. **Chưa qua quant-skeptic.** Không mục nào ở đây đủ điều kiện wire.
6. Rổ 23 mã cùng một chế độ thị trường gần đây (80 phiên). Chưa test qua chế độ khác.

## 7. File

```
probe_pull_1m.py            kéo bar 1m (vnstock/VCI) + chọn rổ đều theo hạng ADV
exp_fill_sim.py             mô phỏng chính: phân rã L1 giá / L2 pacing / L3 capture
exp_ceiling_tolerance.py    P1 — đường đổi chác fill ↔ giá theo τ và tuổi anchor
exp_expected_floor.py       P2 — mẫu số KL kỳ vọng + clamp đuôi
exp_participation_check.py  %tape chiếm được (bị κ chặn — KHÔNG dùng đo đuôi)
exp_participation_bound.py  cận trên κ-free của %tape — thước đo rủi ro đuôi
exp_intraday_profile.py     P3/P4 — profile khung giờ + số phiên cần gom + ca TV1
exp_tv1_reality_check.py    đối chiếu mô phỏng vs kết quả khớp lệnh THẬT 08-11
data/bars1m/*.csv           23 mã × bar 1 phút
out/*.csv                   kết quả từng phiên-mã (tái lập được)
```

Chạy: `/home/trido/thanhdt/wc_venv/bin/python <script>` (vnstock chỉ có ở venv này;
guest rate-limit 20 req/phút — `probe_pull_1m.py` có cache, chạy lại không gọi lại API).
