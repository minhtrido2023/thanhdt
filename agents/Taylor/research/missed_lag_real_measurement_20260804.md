# Đo THẬT: ứng viên LAG bị bỏ lỡ vì thiếu tiền — SpaceX/ZaloPay, go-live → 2026-08-04

**Job**: `Taylor_20260804_071841` · **Ngày**: 2026-08-04
**Loại**: phép đo trên dữ liệu THẬT (không backtest, không NAV giả lập)
**Kết luận 1 dòng**: **KHÔNG có bằng chứng thật nào cho thấy thiếu vốn đã làm mất giá trị.**
Nhóm bỏ lỡ và nhóm mua thật không phân biệt được nhau (CI chứa 0, p=0.58, N=9 vs N=2), và —
điểm quyết định — **nguồn vốn thật để mua LAG là bán PARK, mà PARK lại CHẠY TỐT HƠN nhóm LAG bỏ
lỡ ở cả hai ngày**. Việc F1/PARK-trim wire hôm nay là đủ; **không cần thêm cơ chế chọn lọc/ưu
tiên nào**.

---

## 1. Phương pháp

- **Nguồn 1 — kế hoạch thật**: quét toàn bộ 49 file `data/trade_plans/plan_{SpaceX,ZaloPay}_2026-*.json`
  từ go-live 2026-07-01 → 2026-08-04 (bỏ các bản `superseded`/`wrongdate`).
  Script: `mike/agents/Taylor/exp_missed_lag_20260804/extract_deferred.py`.
- **Nguồn 2 — fill thật**: `data/execution_logs/dnse_raw_*.jsonl`, đọc `averagePrice`/`fillQuantity`
  do broker trả về, **lọc theo `accountNo`** (kỷ luật `coding_guidelines` §12).
- **Nguồn 3 — giá lịch sử**: `tav2_bq.ticker`, cột **`Close` (đã điều chỉnh)** cho CẢ hai đầu mút
  ⇒ tỉ suất là **total return đã bao gồm cổ tức** (kỷ luật §21 — không dùng `Price` thô, không suy
  cổ tức bằng hiệu `Close − Price`).
- **Điểm cuối đo** = **2026-08-03** (phiên gần nhất có close; 08-04 đang giao dịch).
- Phân biệt **DEFER vì THIẾU TIỀN** với **SKIP vì chất lượng/thanh khoản/DCF/rating** — chỉ đếm
  loại thứ nhất, đúng như yêu cầu. Các plan ghi rõ hai nhóm này ở hai field khác nhau
  (`deferred_insufficient_cash` vs `excluded_*`), nên phân loại là đọc-được, không phải suy đoán.

## 2. Đếm thật — có bao nhiêu ứng viên LAG bị bỏ lỡ vì thiếu tiền?

### 2a. BỎ LỠ HẲN (cửa sổ entry đã hết, không bao giờ được mua): **9 mã**

| Ngày entry | Account | Mã | Nguồn trong plan |
|---|---|---|---|
| 2026-07-27 | ZaloPay | AGR, BSI, FTS, HCM, VND | `lag_status.lag_entries_due_today_t1_from_20260724.deferred_insufficient_cash` |
| 2026-07-28 | SpaceX | CSV, EVF, PSI, VCI | `deferred_orders[]` (`book:"LAG"`, `defer_reason` = "DEFERRED — thiếu tiền") |

Đã kiểm chéo toàn bộ `orders[]` của mọi plan sau đó: **không mã nào trong 9 mã này từng được mua**
ở account tương ứng.

### 2b. ĐANG TREO hôm nay (cửa sổ mở ĐÚNG 08-04 — chưa đo được): **6 bản ghi**

SpaceX `TV2`, `APF` (171,10tr) · ZaloPay `DCM`, `DRI`, `POW`, `TV2`. Chưa có giá sau entry ⇒
không đưa vào phép đo, chỉ ghi nhận.

### 2c. Nhóm đối chứng — LAG **thật sự đã mua** từ go-live: chỉ **2 lệnh**, cả hai ở ZaloPay

| Ngày | Account | Mã | KL | Giá fill (broker) |
|---|---|---|---|---|
| 2026-07-27 | ZaloPay | VPB | 700 | **24.950** |
| 2026-07-28 | ZaloPay | CSV | 1.000 | **19.750** |

> **SpaceX chưa từng mua một vị thế LAG nào kể từ go-live.** Toàn bộ 306,7tr LAG mà SpaceX lập kế
> hoạch (07-28) đều rơi vào `deferred_orders[]`.

## 3. Kết quả — nhóm bỏ lỡ diễn biến ra sao?

### 3a. Tỉ suất thô (entry close → 2026-08-03 close)

| Mã | Nhóm | Entry | Ret | Phiên |
|---|---|---|---|---|
| AGR | BỎ LỠ | 07-27 | **+7,76%** | 5 |
| BSI | BỎ LỠ | 07-27 | **+7,43%** | 5 |
| FTS | BỎ LỠ | 07-27 | **+9,95%** | 5 |
| HCM | BỎ LỠ | 07-27 | **+0,60%** | 5 |
| VND | BỎ LỠ | 07-27 | **+9,77%** | 5 |
| CSV | BỎ LỠ | 07-28 | **+4,58%** | 4 |
| EVF | BỎ LỠ | 07-28 | **+5,08%** | 4 |
| PSI | BỎ LỠ | 07-28 | **−1,00%** | 4 |
| VCI | BỎ LỠ | 07-28 | **+10,41%** | 4 |
| VPB | ĐÃ MUA | 07-27 | +3,87% (fill-basis **+2,20%**) | 5 |
| CSV | ĐÃ MUA | 07-28 | +4,58% (fill-basis **+9,87%**) | 4 |

- **BỎ LỠ**: N=9, mean **+6,06%**, median +7,43%, sd 4,11
- **ĐÃ MUA**: N=2, mean **+4,22%** (cơ sở close) / **+6,04%** (cơ sở giá fill thật)
- **Chênh lệch**: **+1,84 pp** trên cơ sở close, **−0,02 pp** trên cơ sở fill thật

### 3b. Có đáng kể không? **KHÔNG.**

- **Bootstrap 95% CI cho chênh lệch: [−0,87; +4,28] pp** (20.000 resample) — **chứa 0**, rộng 5,2pp.
- **Permutation test chính xác** (55 hoán vị, đếm hết): **p = 0,582**.
- Với N=2 ở nhóm đối chứng, không có công cụ thống kê nào cho ra kết luận. Đây là **thống kê mô tả**,
  không phải kiểm định. Con số điểm +1,84pp **không được đọc như một hiệu ứng**.
- Riêng việc đổi cơ sở giá (close → giá fill thật) đã lật dấu chênh lệch từ +1,84pp thành −0,02pp —
  cho thấy tín hiệu mỏng hơn nhiễu đo lường.

### 3c. Chuẩn hoá theo thị trường: **không nhóm nào có alpha**

Cửa sổ này là một nhịp tăng mạnh: **VNINDEX +5,62% (từ 07-27) / +4,89% (từ 07-28)** trong 4–5 phiên.

- Excess vs VNINDEX: **BỎ LỠ +0,77pp** (N=9) · **ĐÃ MUA −1,03pp** (N=2).
- Cả hai nhóm về cơ bản **chỉ đi theo beta thị trường**. Toàn bộ "lãi" +6% của nhóm bỏ lỡ là beta,
  không phải edge PEAD.

## 4. Điểm quyết định — nguồn vốn thật KHÔNG phải tiền nhàn rỗi

Đây là phần đảo ngược cách đọc trực giác, và là phát hiện quan trọng nhất của phép đo này.

Cash thật của SpaceX ngày 07-28 chỉ **4,4tr** (ZaloPay 07-27 tương tự). Tài khoản gần như
full-invested. Nên **phản thực (counterfactual) đúng của "mua LAG" KHÔNG phải "để tiền nằm im" —
mà là "BÁN PARK để lấy tiền"**. Đo trực tiếp rổ PARK thật (14 mã, trọng số theo giá trị vị thế
thật ngày 08-03):

| Ngày | LAG bỏ lỡ (mean) | PARK — nguồn vốn (value-weighted) | Đổi PARK → LAG |
|---|---|---|---|
| 2026-07-27 (ZaloPay) | +7,10% | **+7,66%** | **−0,56 pp** |
| 2026-07-28 (SpaceX) | +4,77% | **+6,96%** | **−2,20 pp** |

> **Ở CẢ HAI ngày, bán PARK để mua LAG sẽ làm KẾT QUẢ XẤU ĐI.** PARK (rổ ngân hàng/bluechip:
> VCB +12,4%, VHM +12,2%, CTG +9,7%, BID +9,0%, MBB +8,4%) chạy tốt hơn rổ LAG bị bỏ lỡ.
> Nói cách khác: trong cửa sổ này, "thiếu tiền" **không phải chi phí — mà là may mắn**.

## 5. Thí nghiệm tự nhiên sạch nhất: CSV, cùng mã, cùng ngày, hai account

Ngày 2026-07-28, cùng tín hiệu CSV (LAG_HI):
- **ZaloPay MUA THẬT** 1.000cp @ 19.750 → 08-03 giá 21.700 = **+9,87%**
- **SpaceX DEFER** 4.500cp (90,07tr) vì cash 12,37tr < lệnh 90tr → **+4,58%** (cơ sở close)

Chênh lệch giữa hai account **không đến từ chất lượng tín hiệu** (cùng một tín hiệu), mà từ
(a) có tiền hay không và (b) ZaloPay khớp được giá tốt hơn close 1.000đ (19.750 vs 20.750).
Giá trị SpaceX bỏ lỡ trên riêng CSV: **+4,12tr VND**. Đây là **N=1**, không suy rộng được.

## 6. Quy ra tiền (chỉ 4 lệnh SpaceX 07-28 có size tường minh trong plan)

| Mã | Size dự kiến | Ret | P&L giả định |
|---|---|---|---|
| CSV | 90,1tr | +4,58% | +4,12tr |
| EVF | 72,1tr | +5,08% | +3,66tr |
| PSI | 72,6tr | −1,00% | −0,73tr |
| VCI | 72,0tr | +10,41% | +7,49tr |
| **TỔNG** | **306,7tr** | | **+14,55tr (+4,75%)** |

⚠️ Con số +14,55tr này **KHÔNG phải "tiền đã mất"**. Để triển khai 306,7tr đó, SpaceX phải bán
306,7tr PARK — mà PARK cùng kỳ +6,96% (≈ **+21,3tr**). **Net thật: −6,8tr**, tức việc bỏ lỡ đã
*giúp* tài khoản, không hại. (5 mã ZaloPay 07-27 không có size tường minh trong plan ⇒ không quy
ra tiền được.)

## 7. Trả lời trực tiếp 4 câu hỏi của dispatch

1. **Bao nhiêu ứng viên LAG bị bỏ lỡ hoàn toàn vì thiếu tiền?**
   → **9 mã** đã hết cửa sổ và không bao giờ được mua (5 ZaloPay 07-27 + 4 SpaceX 07-28).
   Thêm **6 bản ghi đang treo hôm nay 08-04** (chưa đo được). Đối chứng chỉ có **2 lệnh LAG thật**
   trong toàn bộ 1 tháng go-live.

2. **Nhóm bỏ lỡ tốt hơn / xấu hơn / tương đương nhóm đã mua? Chênh bao nhiêu?**
   → **Tương đương — không phân biệt được.** +1,84pp trên cơ sở close, **−0,02pp** trên cơ sở giá
   fill thật. Bootstrap 95% CI **[−0,87; +4,28] pp chứa 0**; permutation p=0,582. Với N=9 vs N=2
   không thể tuyên bố khác biệt. Sau khi trừ beta VNINDEX, cả hai nhóm đều ≈ thị trường.

3. **Nếu nhóm bỏ lỡ TỐT HƠN đáng kể → bằng chứng thật rằng thiếu vốn đang làm mất giá trị?**
   → **Điều kiện này KHÔNG thoả.** Không có khác biệt đáng kể. Và ngay cả con số điểm dương +1,84pp
   cũng bị **triệt tiêu và đảo dấu** khi so với nguồn vốn thật: đổi PARK→LAG cho **−0,56pp
   (ZaloPay) / −2,20pp (SpaceX)**. **Không có cơ sở để nâng ưu tiên cho L2 JIT-unpark hay nâng
   trần w_LAG book** dựa trên dữ liệu thật này.

4. **Nếu KHÔNG khác biệt đáng kể → xác nhận F1/PARK vừa wire là đủ?**
   → **XÁC NHẬN CÔNG KHAI: đủ.** Dữ liệu thật của chính hai tài khoản **không mâu thuẫn** với hai
   kết luận NO-GO backtest hôm nay (`Taylor_20260804_051145`, `Taylor_20260804_061252`) — nó
   **củng cố** chúng bằng một cơ chế khác (đo trực tiếp, không qua NAV giả lập).
   **Không đề xuất thêm cơ chế chọn lọc/ưu tiên vốn LAG nào.**

## 8. Giới hạn — đọc kỹ trước khi trích dẫn

1. **N cực nhỏ**: 9 vs **2**. Nhóm đối chứng có ĐÚNG 2 quan sát. Mọi so sánh ở đây là **mô tả**,
   không phải kiểm định. Đừng trích một con số điểm nào như "hiệu ứng".
2. **Chưa hết chu kỳ**: hold LAG = **25 phiên**; mới đo được **4–5 phiên (16–20%)**. Kết quả có thể
   đảo hoàn toàn. Cửa sổ đầy đủ kết thúc ~2026-09-01/09-02.
3. **Một nhịp thị trường duy nhất, tăng mạnh** (VNINDEX +4,9~5,6% trong 4–5 phiên). Kết luận
   "PARK thắng LAG" gắn chặt với việc nhịp này do ngân hàng/bluechip dẫn dắt — **không suy rộng
   sang nhịp giảm**.
4. **Rổ PARK dùng vị thế SpaceX ngày 08-03** làm đại diện cho "nguồn vốn" ở cả hai ngày; ZaloPay
   có rổ PARK khác (đã kiểm là cùng họ ngân hàng/bluechip nên hướng kết luận không đổi, nhưng con
   số −0,56pp cho ZaloPay là xấp xỉ).
5. **5 mã ZaloPay 07-27 không có size tường minh** trong plan ⇒ chỉ có tỉ suất, không có VND.
6. **Bất nhất gate giữa 2 account (đáng chú ý, ngoài phạm vi job này)**: cùng ngày 07-28, ZaloPay
   **SKIP** EVF/PSI/VCI vì `FLOOR_FAIL`, trong khi SpaceX xếp chúng là **"đủ điều kiện, chỉ thiếu
   tiền"** (dùng P/B+ROE screen ngành chứng khoán để vượt floor). Cùng tín hiệu, hai account phân
   loại khác nhau. Nếu áp gate của ZaloPay thì nhóm "bỏ lỡ vì thiếu tiền" của SpaceX chỉ còn **1 mã
   (CSV)**, và toàn bộ phép so sánh mất nốt ý nghĩa. **Nên thống nhất gate — đề xuất mở việc riêng.**

## 9. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
python3 mike/agents/Taylor/exp_missed_lag_20260804/extract_deferred.py   # liệt kê defer/skip
python3 mike/agents/Taylor/exp_missed_lag_20260804/analyze.py            # số liệu mục 3–6
```
Dữ liệu kèm theo: `prices_full.csv`, `park_prices.csv` (BQ live 2026-08-04),
`deferred_raw.json`, `analyze_out.txt`.

**Production KHÔNG bị đụng** — job này chỉ đọc file plan + giá lịch sử, không sửa code nào.
