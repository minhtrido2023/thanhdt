# Trần giá "slide theo phiên trước" (A) vs "mean-5" (B) — tái lập độc lập + nút thắt thật

Job `Taylor_20260814_170351` · Taylor (Quant/Algo) · 2026-08-14
Chỉ đạo: John (user) qua Mike, topic Discord 1521183164364754974.

> **TRẠNG THÁI: R&D THUẦN. KHÔNG sửa một dòng production nào**, không đụng
> `trading_rules.json`, không đụng `trading_bot/`. Toàn bộ code là `exp_*` (§8
> coding_guidelines). Chưa qua quant-skeptic ⇒ chưa mục nào đủ điều kiện wire.

---

## 0. TL;DR — 4 câu

1. **Số Mike tường thuật qua Discord là ĐÚNG, tái lập được.** Tôi viết lại mô phỏng từ đầu
   (không đọc, không import code cũ), chạy trên dữ liệu thật: Rule A thắng Rule B về fill ở
   **30/30 mã**, +1,93pp trung bình (Mike: 23/23, +1,721pp); TV1 fill **89,72% vs 87,00%**
   (Mike: 89,354% vs 86,309%). Trùng gần như tuyệt đối.
2. **Nhưng kết luận "A thắng" chỉ đúng trên MỘT chiều đo.** Mike chỉ đo *fill*. A mua được
   nhiều hơn vì nó **trả giá cao hơn** (+16,5 bps so VWAP; giá **biên** của phần mua thêm
   **+85 bps**). Trên **implementation shortfall** — thước đo gộp cả giá lẫn phần chưa mua được
   — chênh lệch A−B là **+4,89 bps nghiêng về B**, và **KHÔNG có ý nghĩa thống kê** khi khai
   N trung thực (t = +0,20 gộp theo ngày; **đổi dấu** khi đổi giả định mua bù).
3. **Và trong 65,1% số campaign, A với B cho kết quả Y HỆT NHAU** — chỉ **7,5%** khác nhau về
   khối lượng khớp. Đây không phải một cái cần "chọn đúng"; nó là một tham số hạng hai.
4. **Nút thắt TV1 KHÔNG nằm ở luật giá — đúng như Mike nhận định.** Nó nằm ở **KÍCH THƯỚC
   BLOCK so với ADV** và ở **`max_participation` = 10% ADV20/phiên**. Đòn bẩy lớn nhất, rẻ
   nhất, không tăng rủi ro impact: **kéo dài cửa sổ gom 5 → 10 phiên** — khớp-đủ ở block 60%
   ADV20 đi từ **4,0% → 81,6%** trong khi %tape chiếm được **không đổi** (9,7% → 8,4%).

---

## 1. Dữ liệu — kiểm tra trước, không giả định

| Nguồn | Có gì | Dùng làm gì ở đây |
|---|---|---|
| BQ `ticker`/`ticker_1m`/`ticker_prune` | OHLCV theo **NGÀY** — **KHÔNG có nội phiên** | không dùng được (đã kiểm lại, khớp kết luận job 08-04) |
| `vnstock` 3.4.2 / VCI, `interval='1m'` | Bar **1 phút**, 2023-09-11 → 2026-08-12 | **nguồn chính** |
| `Quote.price_depth()` | `NotImplementedError` | **không tồn tại order-book lịch sử** |
| `data/execution_logs/dnse_khoplenh_broker_confirm_*.csv` | Khớp lệnh THẬT do DNSE phát hành | **neo thực tế** cho §3 (κ) |

**Rổ = 30 mã** (nhiều hơn 23 mã Mike dùng — dispatch yêu cầu đa dạng thanh khoản):

- **23 mã mỏng** (ADV20 ≈ 300–1.000tr/phiên): cache sẵn từ job `Taylor_20260812_091343`,
  chọn ĐỀU theo hạng ADV (không chọn tay), **có TV1** (672tr) và **có DRI** — đúng 2 mã của ca thật.
- **7 mã thanh khoản cao** tôi kéo mới cho job này: **FPT, MBB, ACB, HDB, DCM, VGC, PVT**
  (`data/bars1m_liquid/`). Đây là nhóm LAG/BAL ta thật sự giao dịch — không có nhóm này thì
  không thể nói câu nào về việc kết luận có riêng cho mã mỏng hay không.

**N khai theo kỷ luật §18**: campaign = **5 phiên liên tiếp KHÔNG CHỒNG LẤN** (chồng lấn thì
các quan sát không độc lập), sau warm-up 20 phiên để có ADV20 causal ⇒ **N = 4.178 campaign**
cho mỗi cấu hình. Nhưng 30 mã cùng một cửa sổ ngày thì **tương quan chéo rất cao** — nên mọi
kiểm định quan trọng ở §2.3 tôi **gộp theo NGÀY bắt đầu campaign trước** (N thật = **475 ngày**),
và báo cả hai con số t.

### Vì sao viết lại code thay vì chạy lại code cũ

Job 08-12 đã có `exp_ceiling_tolerance.py` làm việc gần giống. Tôi **cố ý không import và không
đọc để chép** — dùng chung DỮ LIỆU thô nhưng **hai bản mô phỏng độc lập nhau về code**, để lỗi
của bản này không tự tái lập vào bản kia. Tham số cơ chế đọc thẳng từ `trading_bot/config.py`
(2026-08-14): `max_participation=0,10`, `capit_realized_participation_ceiling=0,30`,
`slice_interval_min=8`, `max_child_value=200tr`, `expected_volume_curve`, `tape_clamp=0,50`.

### Mô hình fill (khai rõ để phản biện được)

Mỗi phút: `elig = KL bar × phần khớp ở giá ≤ trần` (nội suy tuyến tính trong [low, high]);
`fill = min(KL đang hiển thị, κ × elig)`, làm tròn lô. KL hiển thị tính đúng công thức
`_child_qty` của executor, refresh mỗi 8 phút. Giá trả = `min(close bar, trần)`.
**Đơn vị**: VCI trả giá theo **nghìn đồng** — đã quy đổi ở mọi chỗ chia giá trị (bẫy này đã cắn
job 08-12; tôi kiểm lại bằng cách xác nhận `max_child_value` có ràng buộc thật).

---

## 2. PHẦN 1+2 — Rule A vs Rule B

Rule A: trần = `close[t−1] × 1,03`, tái lập MỖI phiên · Rule B: trần = `mean5(close) × 1,03`,
cũng tái lập mỗi phiên. Cùng τ = 3% — câu hỏi thuần tuý là **ANCHOR**.

### 2.1 Chiều FILL — Mike đúng, tái lập được

| size lệnh | κ | fill A | fill B | Δ | khớp-đủ A | khớp-đủ B | Δ |
|---|---|---|---|---|---|---|---|
| 10% ADV20 | 0,34 | 99,32% | 98,97% | **+0,35pp** | 98,71% | 97,85% | +0,86pp |
| **30% ADV20** | **0,34** | **95,46%** | **93,52%** | **+1,94pp** | 86,91% | 81,92% | **+4,99pp** |
| 60% ADV20 | 0,34 | 71,64% | 67,85% | **+3,80pp** | 2,58% | 1,79% | +0,79pp |

**A > B ở 9/9 ô** (3 size × 3 κ ∈ {0,20; 0,34; 0,50}) — hướng bền tuyệt đối.
Ở size 30%: **A thắng 30/30 mã**, Δ từ +0,14pp (PGB) đến +5,53pp (FPT).
**TV1**: fill A **89,72%** vs B **87,00%**.

> **So với Mike**: 23/23 mã, +1,721pp TB, dải +0,22..+4,11pp, TV1 89,354 vs 86,309.
> ⇒ **Tái lập THÀNH CÔNG** ở cấu hình size ≈ 30% ADV20, κ = 0,34. Số Discord không bị trôi.
> **Một chỗ KHÔNG tái lập được: "khớp đủ 100%" của TV1** — Mike báo 15,71% vs 15,00%, tôi đo
> **74,3% vs 68,6%**. Hướng giống, **mức lệch 5×**. Chỉ tiêu "khớp đủ" cực nhạy với định nghĩa
> mục tiêu Q; đừng trích con số tuyệt đối của nó từ bất kỳ bản nào trong hai bản.

**Vì sao A thắng, và vì sao đó gần như là một hệ quả toán học chứ không phải phát hiện thị
trường**: khi giá TĂNG, `mean5` tụt lại sau ⇒ trần B nằm dưới thị trường ⇒ fill 0. Khi giá
GIẢM, cả hai trần đều ở trên thị trường ⇒ cả hai fill đủ. Bất đối xứng đó cho A ≥ B gần như
mọi lúc **theo cấu tạo**. Nó không nói Rule A "tốt hơn" — nó nói Rule A **đuổi giá nhiều hơn**.

### 2.2 Chiều GIÁ — Mike KHÔNG đo, và nó ngược chiều

| size | κ | giá A vs VWAP campaign | giá B vs VWAP | Δ(A−B) | giá **biên** của phần mua thêm |
|---|---|---|---|---|---|
| 10% | 0,34 | −12,85 bps | −19,44 bps | **+6,58 bps** | (chỉ 45/4.178 campaign khác nhau — nhiễu) |
| 30% | 0,34 | −11,78 bps | −28,29 bps | **+16,51 bps** | **+85,4 bps** |
| 60% | 0,34 | −17,86 bps | −42,50 bps | **+24,64 bps** | **+126,7 bps** |

Ghép cặp (cùng mã, cùng campaign, n=4.163): Δgiá **+16,70 bps, t = 12,76**; Δfill **+1,82pp,
t = 12,07**. Cả hai đều "có ý nghĩa" — **và chúng ngược dấu về lợi ích**.

⚠️ Giá ÂM ở cả hai rule là **chọn lọc sống sót**, không phải edge: ta chỉ khớp khi giá ở dưới
trần. Đọc **mức chênh**, đừng đọc dấu.

### 2.3 Thước đo gộp — implementation shortfall (chỗ kết luận đảo chiều)

`IS = fill × (giá trả − giá quyết định) + (1 − fill) × (giá mua bù − giá quyết định)`,
giá quyết định = close phiên trước campaign; giá mua bù = close **5 phiên sau khi campaign kết
thúc** (chương trình gom 5% NAV thì **vẫn phải mua nốt ở đâu đó**). Đơn vị bps. Âm = tốt.

| size | κ | IS(A) | IS(B) | Δ(A−B) | t "ngây thơ" (N=4.156) | **t gộp theo ngày (N=475)** |
|---|---|---|---|---|---|---|
| 10% | 0,34 | −10,75 | −14,67 | +3,93 | 2,29 | — |
| **30%** | **0,34** | **−5,09** | **−9,98** | **+4,89** | 2,51 | **+0,20** |
| 60% | 0,34 | +0,34 | −4,34 | +4,68 | 3,10 | — |

**Nhạy với giả định mua bù** (size 30%, κ 0,34): độ trễ 0 / 5 / 20 phiên ⇒ t gộp-theo-ngày
= **+1,34 / +0,20 / −0,83** (N ngày = 478 / **475** / 463). **Đổi dấu.** Không có kết luận
thống kê nào sống sót ở đây.

> **Artifact kiểm chứng** (bổ sung 2026-08-15, job `Taylor_20260815_002825` — đóng lỗ hổng
> auditability quant-skeptic chỉ ra; KHÔNG chạy lại verify, KHÔNG đổi kết luận):
> `exp_shortfall_sweep.py` → `out/shortfall_sweep.csv`, 27 ô (3 lag × 3 size × 3 κ), mỗi ô có
> **cả hai** t và **cả hai** N. Cột `t_naive_DO_NOT_CITE` cố ý đặt tên như vậy: nó đếm mỗi ngày
> tới 30 lần (30 mã cùng lưới ngày) nên phóng đại |t| ~√30 ≈ 5,5×. Con số phải trích là
> `t_day_clustered` với `n_day`.

### 2.4 Hình dạng phân bố — cái quan trọng nhất của mục này

- **65,1% campaign: A và B ra kết quả Y HỆT.** Chỉ **7,5%** khác nhau về khối lượng khớp.
- Trong 34,9% có khác biệt: **B tốt hơn ở 66% số ca**, median nghiêng về B **+5,75 bps**…
- …nhưng A có **đuôi trái khổng lồ**: min **−3.195 bps** (ca giá chạy mất, B không mua được gì),
  p95 **+212 bps**.

⇒ **Đây là hình dạng BẢO HIỂM, không phải edge**: B thắng nhỏ và thường xuyên; A thắng hiếm
nhưng rất lớn. Chọn A = **mua bảo hiểm chống hụt hàng khi giá chạy**, trả bằng vài bps mỗi lần.
Đó là một quyết định **CHÍNH SÁCH** (chấp nhận trả thêm để chắc có hàng), **không phải** một
edge định lượng đã kiểm chứng.

### 2.5 Đánh giá phương pháp — κ = 34% từ đâu?

**KHÔNG neo vào fill thật.** Truy nguồn: κ=0,34 xuất hiện trong `exp_tv1_reality_check.py` (job
`Taylor_20260812_091343`) là **ngưỡng BÃO HOÀ** — mức κ nhỏ nhất mà mô phỏng "bỏ trần 30%" tái
lập đủ 3.300cp của TV1 ngày 08-11. Đó là **n = 1**, và là một **ngưỡng**, không phải một **ước
lượng**. Dùng nó làm tham số trung tâm là hợp lý cho *xếp hạng*, **sai** nếu đọc như dự báo.

**Neo thực tế duy nhất tồn tại** — email khớp lệnh DNSE phát hành (§27, skill
`dnse-fill-reconciliation`), %tape ta thật sự chiếm:

| Ngày | Mã | KL khớp thật | KL phiên | %tape |
|---|---|---|---|---|
| 08-11 | TV1 | 100 | 42.700 | **0,23%** |
| 08-13 | TV1 | 1.200 | 23.200 | **5,17%** |
| 08-14 | TV1 | 1.300 | 27.600 | **4,71%** |
| 08-11 | DRI | 5.600 | 470.100 | 1,19% |
| 08-10 | SCL | 2.500 | 231.300 | 1,08% |

Mô hình ở κ=0,34 hàm ý **~9% tape trung bình** (p95 ~18%) — tức **lạc quan ~2× so với quan sát
thật cao nhất**. Và ca TV1 thật: mục tiêu 3.300cp, khớp 100+1.200+1.300 = **2.600cp trong 3
phiên (78,8%)**, trong khi mô phỏng của tôi cho TV1 ở size 10% ADV20 ra **fill 97,5%,
khớp-đủ 94,3%**.

**Kết luận phương pháp — tách bạch dứt khoát:**

| | Có tin được không? | Vì sao |
|---|---|---|
| **HƯỚNG (A > B về fill)** | **CÓ** | bền ở 9/9 ô (3 size × 3 κ), 30/30 mã, và có giải thích cấu tạo (§2.1) — không phải hiện vật của κ |
| **HƯỚNG (A đắt hơn B)** | **CÓ** | cùng lý do, cùng cấu tạo |
| **HƯỚNG (A tốt/tệ hơn về IS)** | **KHÔNG** | đổi dấu theo giả định mua bù; t gộp-theo-ngày = 0,20 |
| **MỨC (mọi con số % tuyệt đối)** | **KHÔNG** | κ không quan sát được; "hàng dưới trần" = KL đã khớp = **cận dưới**; mô hình over-predict 97,5% ở đúng ca mà thực tế cho 78,8% |

---

## 3. PHẦN 3 — Nút thắt thật: kích thước block, không phải luật giá

Chạy trên **rổ mã MỎNG** (ADV20 < 2 tỷ, n=23 mã), Rule A, κ=0,34, campaign 5 phiên.
`prod` = cơ chế LIVE hôm nay · `p2` = mẫu số kỳ vọng đã wire PAPER (08-17) · `pr50/pr100` =
participation-rate thuần p×ADV20×f(t) · `nocap` = bỏ hẳn trần phụ (tham chiếu cận trên).

### 3.1 Đổi cơ chế pacing — lợi ích có thật nhưng nhỏ, và **BÃO HOÀ**

**Tỷ lệ khớp ĐỦ 100% (%)**

| size lệnh | prod (LIVE) | p2 (paper) | pr50 | pr100 | nocap |
|---|---|---|---|---|---|
| 5% ADV20 | 99,1 | 99,5 | 99,5 | 99,5 | 99,9 |
| 10% ADV20 | 97,1 | 98,7 | 98,6 | 98,7 | 99,6 |
| 20% ADV20 | 90,8 | 93,6 | 93,1 | 93,3 | 97,1 |
| **30% ADV20** | **78,7** | **82,9** | 82,7 | 83,0 | 90,0 |
| **60% ADV20** | **3,7** | **4,0** | 3,8 | 3,9 | 4,4 |

**Hai điều đọc ra ngay:**
1. `p2` ≈ `pr50` ≈ `pr100`. **Nới participation vượt quá P2 không cho thêm gì** — vì ràng buộc
   binding phía trên nó không còn là trần 30% nữa mà là **`max_participation` = 10% ADV20/phiên**.
   ⇒ **P2 (đã wire paper) đã lấy gần hết phần dễ; không có "P3 participation" nào để làm thêm.**
2. Ở block **60% ADV20 thì MỌI cơ chế đều chết** (3,7–4,4%). Lý do **cơ học, không phải thị
   trường**: 10% ADV20/phiên × 5 phiên = **trần cứng 50% < 60%**. Không cơ chế pacing nào sửa
   được một bài toán số học.

**Nhóm mã DÀY (ADV20 ≥ 2 tỷ, n=27) hầu như không bị ảnh hưởng**: khớp-đủ 100,0% tới size 10%
ADV20, 98,2–98,7% ở 20%. **Vấn đề này là RIÊNG của mã mỏng** — kết luận này chỉ nói được nhờ
7 mã thanh khoản cao kéo thêm.

### 3.2 Hai đòn bẩy thật — và một cái tốt hơn hẳn cái kia

| Kịch bản (mã mỏng, block **60% ADV20**) | khớp-đủ | %tape TB | %tape p95 |
|---|---|---|---|
| Hiện tại: 5 phiên, `max_participation`=10% | **4,0%** | 9,7% | 19,5% |
| **Kéo dài cửa sổ → 10 phiên** (không đổi gì khác) | **81,6%** | **8,4%** | **17,2%** |
| Giữ 5 phiên, nâng `max_participation` → 20% | 68,4% | 14,2% | 25,3% |
| Giữ 5 phiên, nâng `max_participation` → 30% | 74,8% | 16,2% | 26,7% |

Ở block 30% ADV20: 5 phiên → 82,9% vs **10 phiên → 96,0%**, %tape 9,0% → **8,7%**.

**KÉO DÀI THỜI GIAN THẮNG TUYỆT ĐỐI so với NÂNG PARTICIPATION**: khớp-đủ cao hơn (81,6% vs
68,4%) **và** %tape *thấp hơn* (8,4% vs 14,2%). Nâng participation mua fill bằng cách chiếm
tỷ trọng lớn hơn trong một phiên mỏng — tức **mua bằng đúng thứ rủi ro mà `max_participation`
sinh ra để chặn**, và là thứ mô hình này **không đo được** (tape lịch sử không chứa lệnh của ta,
nên impact của chính ta = 0 theo cấu tạo — mọi con số "nâng participation vẫn ổn" đều lạc quan
có hệ thống).

### 3.3 Trả lời thẳng câu hỏi gốc của John (08-09)

> *"Sao không lên chiến lược mua dựa trên giá tham chiếu, slide theo block bám giá đang khớp?"*

**Trực giác đúng, và phần lớn nó ĐÃ được thực hiện** — nhưng nó không phải là thứ đang chặn TV1.

| Thành phần của ý tưởng | Trạng thái | Bằng chứng |
|---|---|---|
| Trần **bám giá** thay vì số đông cứng | **ĐÚNG và quan trọng** | trần đóng băng 5 phiên: khớp-đủ TV1 66,4% vs 74,3% (A). Ca thật TV1 tệ hơn nhiều vì trần đóng băng **3 tuần** (20.000đ chốt 07-23) |
| **Chọn anchor** (phiên trước vs mean-5) | **Hạng ba** | 65,1% campaign không đổi kết quả; IS không có ý nghĩa |
| **Chia nhỏ theo block** bám KL đang khớp | **ĐÃ CHẠY từ lâu** — chính là `_child_qty` | `prod`: 30% × KL luỹ kế; `p2` đã wire paper 08-17 |
| Nới participation thêm nữa | **BÃO HOÀ, không còn gì** | pr50 ≈ pr100 ≈ p2 (§3.1) |
| **Kích thước block / số phiên gom** | **ĐÂY MỚI LÀ NÚT THẮT** | 4,0% → 81,6% khi 5 → 10 phiên |

**Với TV1 cụ thể**: mục tiêu 5% NAV ≈ 3.300cp ≈ **9,5% ADV20** — theo bảng §3.1 lẽ ra khớp-đủ
~97–99%. Thực tế 08-11 khớp **100cp**. Chênh lệch đó **không giải thích được bằng luật giá hay
pacing**; nó là ca **trần nằm dưới thị trường** (đã kết luận ở job 08-12) — và quả thật khi trần
hết chặn, TV1 khớp 1.200cp (08-13) rồi 1.300cp (08-14) mà **không có thay đổi thuật toán nào**.

---

## 4. PHẦN 4 — Khuyến nghị

### (a) Rule A vs Rule B — **NO-GO như một "cải tiến"; nếu đổi thì phải gọi đúng tên là chính sách**

**Không đề xuất wire Rule A với lý do "backtest cho thấy tốt hơn".** Bằng chứng không đỡ được
câu đó:

- Trên fill: A tốt hơn (30/30 mã) — **nhưng nó tốt hơn vì đuổi giá cao hơn**, không phải vì
  thực thi khéo hơn.
- Trên chi phí thực thi đầy đủ: **không có ý nghĩa thống kê**, và **đổi dấu** theo giả định.
- Trong **65,1%** số ca, **hai luật cho kết quả y hệt**.
- **DSR/PBO không áp dụng được** (§quy chuẩn 5): đây không phải một chiến lược sinh NAV — không
  có chuỗi NAV để tính DSR. **Không được trích bất kỳ số nào ở đây như CAGR/edge.**

**Nếu John vẫn muốn đổi sang A** — đó là lựa chọn hợp lý và tôi ủng hộ **với lý do đúng**:
*"chương trình gom theo target NAV phải chắc có hàng; chấp nhận trả thêm ~16 bps để cắt đuôi
hụt hàng khi giá chạy (đuôi trái tới −3.195 bps)"*. Ghi vào quyết định là **chính sách chấp nhận
đánh đổi**, không phải edge — cùng khuôn mẫu đã dùng cho **sàn ADV3T 2 tỷ** (wire vì hiệu quả
vốn, backtest nói ngược, đã ghi rõ trong comment code).

**Cách wire nếu duyệt** (KHÔNG tự làm — cần user duyệt + quant-skeptic CONFIRMED trước):
1. Sửa ở **plan generator**, sinh `hard_no_chase_ceiling_vnd = anchor × (1+τ)` mỗi lần lập plan,
   anchor = close phiên trước. **KHÔNG đụng `_limit_price`/guard cuối của executor** — trần vẫn
   là field riêng cưỡng chế bằng code (**§24**).
2. τ giữ nguyên giá trị John chốt cho cả lớp discretionary (nghiên cứu 08-12: τ=3% là điểm gãy
   của đường đổi chác).
3. Trần chỉ **tái lập khi lập plan** (1 lần/ngày), **không** trượt trong phiên — trượt trong
   phiên là đuổi giá thật sự, khác hẳn cái đo ở đây.
4. Selfcheck: `plan.py` là **module lõi (21 selfcheck phụ thuộc, §23)** ⇒ quét rộng bắt buộc.

### (b) Participation-rate cho mã mỏng — **NO-GO cho "nới participation", GO cho "kéo dài cửa sổ"**

**NO-GO — nâng `max_participation` (10% → 20/30%)**: mua +64pp khớp-đủ bằng cách nâng %tape
9,7% → 14,2%, tức tăng đúng thứ rủi ro mà mô hình này **không đo được** (impact của chính ta =
0 theo cấu tạo). Không có bằng chứng nào ở đây biện minh được.

**NO-GO — thêm một tầng participation-rate mới**: `pr50`/`pr100` ≈ `p2` (chênh <0,3pp). **P2 đã
wire paper 08-17 lấy gần hết phần dễ.** Thêm cơ chế = thêm bề mặt lỗi, không thêm fill.
Việc đúng bây giờ là **để paper trial P2 chạy hết 08-17 → 09-15** theo charter đã đăng ký.

**GO (có điều kiện) — chuẩn hoá "số phiên gom kỳ vọng" theo tỷ lệ block/ADV20.** Đây là đòn bẩy
lớn nhất (4,0% → 81,6% ở block 60% ADV20), **không tốn gì về impact** (%tape 9,7% → 8,4%), và
**không đụng `executor.py`** — nó là thay đổi ở tầng LẬP KẾ HOẠCH và ở KỲ VỌNG người đọc:

| block / ADV20 | số phiên cần để khớp-đủ ≥90% (mã mỏng) |
|---|---|
| ≤ 10% | 5 (đã đạt 98,7%) |
| 20–30% | 5 (82,9%) → **10 (96,0%)** |
| ≥ 60% | **≥10** (81,6%); 5 phiên là **bất khả thi về số học** |

Bước tiếp theo, đúng khuôn mẫu `expvol_pacing` (charter → paper → quant-skeptic → user):
1. **Không wire code gì bây giờ.** Đăng ký một mục vào `kb/projects/rnd-pipeline-tracker.md`.
2. Với mọi lệnh có `KL_lệnh / ADV20 > 10%`, plan ghi thẳng vào `note` **số phiên gom kỳ vọng**
   (bảng trên) — thuần thông tin, không chặn, không đổi sizing. Việc này một mình đã đóng được
   lỗ hổng "báo cáo EOD đọc partial fill là sự cố".
3. Chỉ sau khi paper trial P2 đóng (09-15) mới bàn tiếp việc *tự động* kéo dài cửa sổ —
   **hai thay đổi cùng chạm pacing chạy song song thì không quy được nhân quả**.
4. Trước bất kỳ đề xuất wire nào: **quant-skeptic CONFIRMED**. Chưa mục nào ở đây qua cổng đó.

---

## 5. Giới hạn — đọc kèm mọi con số

1. **Không có order-book lịch sử.** "Hàng dưới trần" = KL **đã khớp** = **cận dưới**. Mọi fill
   ở đây có thể thấp hơn thực tế — **ở cả hai rule**, nên so sánh vẫn hợp lệ, mức thì không.
2. **κ không neo được** (§2.5). Xếp hạng bền qua κ ∈ {0,20; 0,34; 0,50}; mức tuyệt đối thì không.
3. **Impact của chính lệnh ta = 0 theo cấu tạo.** Mọi kịch bản "nới participation" vì thế lạc
   quan **có hệ thống**. Đây là lý do §4(b) từ chối hướng đó bất kể bảng số.
4. **KHÔNG có backtest NAV.** Đo fill-rate và giá thực thi, **KHÔNG** đo lợi nhuận. Fill cao hơn
   chỉ tốt nếu bản thân quyết định mua là đúng — câu hỏi khác.
5. **N thật nhỏ hơn N thô**: 4.178 campaign nhưng chỉ **475 ngày** độc lập. Mọi t-stat "ngây
   thơ" trong báo cáo này đều được báo kèm bản gộp-theo-ngày; **đừng trích bản ngây thơ**.
6. Mẫu 2023-09 → 2026-08, **một chế độ thị trường**. Chưa test qua chế độ khác.
7. **Chưa qua quant-skeptic.** Không mục nào đủ điều kiện wire.

## 6. File

```
exp_ceiling_ab.py     mô phỏng chính (viết lại từ đầu). ENV: TAG/RULES/SIZES/KAPPAS/MECHS/
                      CAMPAIGN_LEN/MAXPART. Rule C = anchor đóng băng lúc lập plan (đối chứng)
exp_shortfall.py      implementation shortfall A vs B (§2.3), LAG_CATCHUP=5 cố định
exp_shortfall_sweep.py  ARTIFACT §2.3: sweep LAG_CATCHUP 0/5/20 + t GỘP-THEO-NGÀY (N=475)
out/shortfall_sweep.csv   27 ô, cả t ngây thơ lẫn t gộp-theo-ngày + N của cả hai
out/campaigns_main.csv    A vs B × 3 size × 3 κ (75.318 dòng)
out/campaigns_mech.csv    prod/p2/pr50/pr100/nocap × 5 size (104.365 dòng)
out/campaigns_len10.csv   campaign 10 phiên
out/campaigns_mp*.csv     max_participation 0,10/0,20/0,30
out/campaigns_abc.csv     A vs B vs C (anchor đóng băng)
out/shortfall.csv         bảng IS
```

Chạy: `/home/trido/thanhdt/wc_venv/bin/python exp_ceiling_ab.py` (vnstock chỉ có ở venv này).
Dữ liệu bar dùng chung với `../thin_exec_20260812/data/bars1m{,_liquid}/`.
