# CAPIT 07-21 — có nên bù 93,2tr thiếu cho SpaceX không?

Job `Taylor_20260731_155814` (Việc 2) · 2026-07-31 · **đề xuất, KHÔNG tự thực thi lệnh**

Bối cảnh: finding `Taylor_20260731_154624` — plan CAPIT SpaceX 07-21 nhân `capit_size` hai lần,
deploy 255,2tr thay vì mục tiêu 348,4tr. Việc 1 (fix gốc, producer + gate đối chiếu 21:00) đã xong
và commit (`53cb117` outer / `d3aa3f05` mike, self-check 24/24 PASS). Việc 2 hỏi: **bù hay không?**

**Khuyến nghị: KHÔNG BÙ (phương án C — để nguyên).** Không phải vì "thiệt hại chìm" (nguyên tắc
trừu tượng), mà vì cả 4 trục đo được đều nói không, và 2 trong 4 nói *ngược lại* với trực giác
"đang thiếu tiền thì bơm cho đủ".

---

## 1. Vị thế CAPIT SpaceX hiện tại — đo thật, không giả định

Khối lượng CAPIT = fill THẬT ngày 07-21 (`data/execution_logs/dnse_raw_2026-07-21.jsonl`, lọc
`accountNo=0002023347`, dedupe theo `orderId`, lấy bản ghi fill cuối mỗi lệnh). Giá hôm nay =
**DNSE API live** 2026-07-31 (`mike/bin/compute_active_nav.py --account SpaceX`), không dùng BQ.

| Mã | KL | Giá vào | Giá 07-31 | % | P&L |
|---|---:|---:|---:|---:|---:|
| NCT | 500 | 94 360 | 83 400 | **−11,6%** | −5,5tr |
| PVT | 3 000 | 17 100 | 18 300 | +7,0% | +3,6tr |
| SAB | 1 100 | 47 368 | 43 550 | **−8,1%** | −4,2tr |
| SIP | 1 100 | 47 123 | 48 100 | +2,1% | +1,1tr |
| VNM | 900 | 58 600 | 60 900 | +3,9% | +2,1tr |
| **Tổng** | | **255 159 968** | **252 225 000** | **−1,15%** | **−2,93tr** |

Còn giữ đủ 5/5 mã, chưa bán gì. Episode `CAPIT-2026-07-20` **đang mở**, đã giữ **9/60 phiên**
(`data/golive_v23_status.json`, sổ episode wire 07-31). Vị thế broker của PVT (3 500) và SIP
(1 700) lớn hơn KL CAPIT vì có phần chồng lấn custom30V parking — phần CAPIT đúng bằng KL bảng trên.

VNINDEX cùng kỳ: 1 730,56 (07-21) → 1 735,78 (07-31) = **+0,30%**. Rổ CAPIT thua chỉ số ~1,45pp
sau 9 phiên.

**Hệ quả trực tiếp: phần thiếu 93,2tr tới giờ KHÔNG gây thiệt hại — nó tránh được lỗ.** Nếu 93,2tr
đó đã được giải ngân 07-21 theo cùng tỷ trọng, P&L hôm nay là **−4,01tr thay vì −2,93tr** (tệ hơn
1,07tr). Không có khoản lỗ thực nào để "bù cho hoà".

## 2. Điều kiện CAPIT hôm nay: KHÔNG cho phép mua

| Chỉ báo (07-31) | Giá trị |
|---|---|
| `capit_signal_today` | **false** |
| breadth oversold | 10,0% (07-30) vs gate **31%** |
| `capit_size` hôm nay | **0,0** |
| `n_capit_basket` | **0** |

Công thức sống hôm nay cho ra mục tiêu CAPIT = `NAV_book_LAG × capit_size` = **0 VND**. Con số
348,4tr chỉ tồn tại ở ngày 07-20/07-21 khi gate fire. Mua thêm bây giờ **không phải "khôi phục vị
thế đúng thiết kế"** — đó là một lệnh discretionary MỚI mà không rule production nào cho phép
(đúng ranh giới đã chốt sau vụ VIX stop-loss bịa 07-20: không viện dẫn rule để hợp thức hoá hành
động chưa verify trong code).

## 3. Rổ đã bị chính bộ lọc chất lượng loại — và loại đúng 2 mã đang rẻ nhất

Rổ tính lại mỗi phiên có fire, co dần: 07-20 `NCT PVT SAB SIP VNM` → 07-22 `PVT SAB SIP VNM` →
07-24 & 07-28 `PVT SIP VNM`.

Lý do (BQ `tav2_bq.ticker`, đúng bộ lọc pool `capit_pool_sql`: ROE_Min5Y≥0,12 ∧ ROIC5Y≥0,10 ∧
**FSCORE≥6** ∧ ADV≥2 tỷ):

| Mã | FSCORE 07-17 | FSCORE 07-21 | FSCORE 07-23 | pbz 07-23 |
|---|---:|---:|---:|---:|
| NCT | 6 | **3** ❌ | **3** ❌ | −2,43 |
| SAB | 6 | 6 | **5** ❌ | −0,70 (hết <−1) |
| PVT | 6 | 6 | 6 ✅ | −1,41 |
| SIP | 7 | 7 | 7 ✅ | −1,71 |
| VNM | 7 | 7 | 7 ✅ | −1,36 |

**NCT rớt sàn Piotroski 6→3 ngay sau ngày mua** (BCTC mới ra), SAB 6→5 và PB-z hết rẻ. Hai mã
này chính là hai mã **giảm sâu nhất** (−11,6% / −8,1%). Nghĩa là bộ lọc chất lượng đã hoạt động
đúng — nó ejected chúng *trước* phần lớn mức giảm.

Bù "theo đúng tỷ trọng 5 mã ban đầu" ⇒ **bơm thêm ~37tr vào 2 mã mà chính hệ thống production
hiện đang từ chối**, chỉ vì chúng rẻ hơn giá vốn. Đây là nghịch lý "mua thêm cái đang hỏng", ngược
hẳn tinh thần CAPIT (mua *chất lượng* bị bán tháo, sàn ROE/ROIC/FSCORE là điều kiện cấu thành, không
phải trang trí).

Về giá thuần tuý: rổ đang **−1,15% so giá vốn** ⇒ bù bây giờ không phải "mua đuổi", nhưng cũng
không phải món hời — giá không cho lý do hành động theo chiều nào. Chỉ chất lượng cho lý do, và nó
nói *không*.

## 4. Tiền lấy ở đâu — không có chỗ trống trong book

Số dư SpaceX thật (DNSE balances 2026-07-31 23:10):

| | VND |
|---|---:|
| `availableCash` | **4 551 848** |
| `totalCash` | 14 326 923 (gồm 9,775tr cổ tức chưa về) |
| `totalDebt` / `totalLoanDebt` | 6 212 / 0 (≈ 0, chỉ phí tích luỹ) |
| Cổ phiếu MTM | 924 115 000 |
| NAV | 928 666 848 |

Gross exposure hiện tại **99,5%**, nợ margin ~0. Bù 93,2tr ⇒ hoặc **vay margin ~89tr**
(~12,5%/năm ≈ 0,93tr/quý, đưa exposure lên ~110%) — V2.4 không có rule nào cho phép dùng margin để
mở rộng CAPIT, đòn bẩy (V2.5 MGE=1,5) đang **DISABLED** — hoặc **bán bớt custom30V parking**.

Bán parking mới là cơ chế đúng thiết kế, nhưng chỗ trống không tồn tại:

- LAG book hôm nay = 928,67tr × w_LAG 0,50 = **464,33tr**; CAPIT đang chiếm **252,2tr = 54,3%**;
  còn **212,1tr**.
- CSV 07-31 có **10 mã LAG UPCOMING trong T+1…T+3** (DHD 08-01; APF/MAC/TV2/TV3; BVB/DCM/DGW/PRE/PVT).
  Ở trọng số LAG_HI 10% = 46,4tr/mã, **chỉ 5 mã đã là 232,2tr > 212,1tr còn lại**. Kể cả sau khi
  lọc thanh khoản loại các mã bị cờ 🔴/⚠ (DHD/MAC/TV3/PRE/APF), phần còn lại (BVB/DCM/DGW/PVT/TV2)
  vẫn **oversubscribe** ngân sách còn lại của book.

CAPIT và LAG rút từ **cùng một book**. 93,2tr "thiếu" không phải tiền nhàn rỗi — nó là đúng phần
ngân sách mà pipeline PEAD sẽ đòi trong 1-3 phiên tới.

## 5. Kết luận & 3 phương án

**Khuyến nghị: C — để nguyên, không bù.** Bốn căn cứ độc lập, mỗi cái tự nó đã đủ:
điều kiện entry đang TẮT (§2) · bộ lọc chất lượng đã loại 2/5 mã, đúng 2 mã sẽ được bù nhiều nhất
(§3) · không có ngân sách trong LAG book, cash thật 4,55tr, bù = vay margin ngoài rule hoặc cướp
chỗ của PEAD (§4) · và thiệt hại tới giờ = 0, thực tế phần thiếu đang *có lợi* 1,07tr (§1).

| PA | Nội dung | Đánh giá |
|---|---|---|
| **A** | Bù đủ 93,2tr theo 5 mã gốc | **Không nên** — vi phạm cả 4 trục §1-§4 |
| **B** | Bù một phần, chỉ 3 mã còn qua sàn (PVT/SIP/VNM) | Đỡ tệ hơn A về chất lượng, nhưng vẫn là entry mới không rule nào cho phép, vẫn phải lấy tiền từ chỗ LAG sắp cần. Nếu user vẫn muốn: 55,9tr (=3/5 phần thiếu), phải ghi rõ là **quyết định discretionary của user**, không phải CAPIT rule |
| **C** | **Để nguyên** (khuyến nghị) | Vị thế vẫn đúng thiết kế về *chất* (5 mã, hold 60 phiên, exit chung), chỉ nhỏ hơn ý định về *lượng*. Lần fire tiếp theo sẽ đúng size nhờ fix Việc 1 |

**Điều đáng làm thay vì bù**: fix Việc 1 đã đóng lỗ hổng cho lần fire SAU (`capit_slot_targets`
publish sẵn VND/slot + đối chiếu Σ lệnh vs mục tiêu ở bước duyệt 21:00, WARN khi lệch >10%). Đó là
nơi 93,2tr thật sự được "bù" — bằng cách lần tới không thiếu nữa, đúng lúc gate cho phép mua.

**Điểm cần theo dõi (không phải hành động ngay)**: NCT FSCORE 3 và SAB FSCORE 5 hiện **dưới sàn
chất lượng của chính pool CAPIT**. Rule CAPIT hiện tại không có exit theo chất lượng (chỉ hold 60
phiên rồi thoát) — nên đây không phải tín hiệu bán theo rule. Nhưng nếu user muốn đặt câu hỏi
"CAPIT có nên có quality-exit không", đây là ca thật đầu tiên để khảo sát; cần backtest riêng,
không sửa nóng giữa episode đang mở.

---

### Nguồn số (đều tái lập được)
- Fill 07-21: `data/execution_logs/dnse_raw_2026-07-21.jsonl` (lọc `accountNo`, dedupe `orderId`)
- Giá + cash live 07-31: DNSE API qua `mike/bin/compute_active_nav.py --account SpaceX`;
  balances `data/execution_logs/dnse_raw_2026-07-31.jsonl` kind=`balances`
- Trạng thái CAPIT: `data/golive_v23_status.json` (07-31)
- Rổ theo ngày: `deploy_golive_dt5g_v4/out/golive_v23_recommendations_2026-07-{20,22,24,28,31}.csv`
- Pool screen: `deploy_golive_dt5g_v4/golive_recommend_v23.py:237` `capit_pool_sql`
- FSCORE/pbz: BQ `tav2_bq.ticker` (dữ liệu lịch sử, sau sync — hợp lệ theo §6 coding_guidelines)
- VNINDEX: BQ `tav2_bq.ticker` ticker=VNINDEX
