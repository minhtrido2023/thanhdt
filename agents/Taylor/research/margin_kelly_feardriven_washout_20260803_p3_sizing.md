# Tách biến cơ chế SIZING — "dịch vốn parking sang CAPIT lúc washout sâu" — PHẦN 3

**Job** `Taylor_20260803_082141` · **Ngày** 2026-08-03 · **RESEARCH-ONLY** (production `git status` sạch)
**Nối tiếp** `margin_kelly_feardriven_washout_20260803_p2.md` §1.5 + §4 mục 1 (job `Taylor_20260803_073714`) —
dùng lại nguyên bộ sự kiện / rổ `universe_pit` / harness của p2, không định nghĩa lại gì.

> ## VERDICT NGẮN
> **`parkdd:f` (dịch parking CHỈ ở washout sâu `dd52<=−20%`) — 🔴 NO-GO.** Kém hơn bản KHÔNG điều kiện
> ở **mọi** mức `f`, dose-response zig-zag không đơn điệu. Trả lời thẳng câu hỏi của dispatch:
> **+0,61pp của chân L1b KHÔNG phải là hiệu ứng "dịch vốn ở washout SÂU"** — điều kiện hoá theo độ sâu
> chỉ làm giảm giá trị. Đây là **lần tái lập thứ ba** của kết luận p2 §1.3(3).
>
> **`park:f` (dịch parking ở MỌI sự kiện) — 🔴 NO-GO cho wire (hạ cấp từ CONDITIONAL sau kiểm tra cuối).**
> Về bề mặt rất đẹp: +0,82…+1,10pp CAGR, **MaxDD không đổi một chữ số** (−17,79% vs −17,78%, cùng ngày
> đáy 2018-07-05), OOS > IS, LOO theo năm **0/13** năm âm, **0 VND vay** (đúng thứ p2 không đo được).
> Nhưng **leave-one-EVENT-out** (chạy thêm sau khi quant-skeptic nêu đúng lỗ hổng này) cho thấy:
> **1 sự kiện duy nhất — 2020-07-27 — gánh 67% edge toàn kỳ và 74% edge OOS**; thêm 2025-10-20 nữa là
> **~95%**. 5/7 sự kiện còn lại đóng góp ~0. Cộng với **PBO ≥ 0,5 ở 4/6 đặc tả** và **phán quyết
> DỪNG-KHÔNG-WIRE 2026-07-31** vẫn đang treo trên chính họ tham số này ⇒ không đủ điều kiện wire.
>
> **Điểm dương thực chất giữ lại:** cơ chế này **vô hại về rủi ro** (MaxDD y hệt ở **cả 18 chân**) và
> **không cần vay một đồng nào** — nên nếu sau này có thêm sự kiện OOS làm phân bố bớt lệch, đây vẫn là
> ứng viên đáng đo lại. Không phải "bác bỏ vĩnh viễn", là "chưa đủ bằng chứng, và bằng chứng hiện có
> tập trung vào 1-2 đợt".

---

## 1. Thiết kế — tách biến thế nào cho đúng

### 1.1 Vấn đề p2 để lại

p2 đo được +0,61pp cho chân L1b (`MGE=1,3` + cổng `dd52<=−20%`) nhưng **không đọc được nó**: `MGE` trộn
lẫn hai cơ chế (nhân hệ số sizing + mở room vay thật), và đo ra chỉ **5-9%** phần tăng là tiền vay thật.
Muốn biết phần sizing đáng giá bao nhiêu thì phải có một tham số **chỉ** đụng sizing, **không** đụng vay.

### 1.2 Tham số dùng — và một đính chính đáng ghi

`CAPIT_SIZE_BASE=park:f` mà p2 đề xuất **đã tồn tại sẵn trong production** `pt_v23_audit_2014.py`
(dòng ~1422, thêm 2026-07-31 job `Taylor_20260731_085810`), mặc định `cash` nên inert. Nghĩa là trục
"không điều kiện" **không cần code mới** — và quan trọng hơn, **đã từng được chạy** (§4.1, phải đối chiếu).

Thứ **thật sự mới** là điều kiện hoá theo độ sâu. Bản sao nghiên cứu `p3/engine_park.py` thêm:

```
CAPIT_SIZE_BASE=parkdd:f   # y hệt park:f, NHƯNG f chỉ áp cho sự kiện có dd52 <= CAPIT_PARKDD_TH (-20%)
                           # sự kiện nông hơn giữ nguyên cơ sở "cash" (spec production)
CAPIT_PARK_LOO=<i,...>     # leave-one-EVENT-out (thêm sau, theo yêu cầu quant-skeptic — §5)
```

`dd52` lấy từ chính field `e["dd"]` engine đã tính tại **ngày sự kiện** (causal, không nhìn trước).
Diff so với production = **5 hunk thuần THÊM**, tất cả inert khi không bật.
**Không sửa production** (`git status --porcelain` rỗng trên `pt_v23_audit_2014.py`, `macro_state_live.py`,
`rating_8l.py`, `data/trading_rules.json`).

### 1.3 Tại sao trục này CHỈ chạm được ít sự kiện — quan sát cấu trúc, đọc trước mọi bảng số

Parking (custom30V) **chỉ tồn tại ở state NEUTRAL** (`PARK_STATES=3:0.7`). Washout sâu nhất lại thường
rơi vào CRISIS/BEAR. Hai thứ **gần như loại trừ nhau theo thiết kế**. Đo trực tiếp trên 15 sự kiện có
vào lệnh (log `[capit-size]` của chân control):

| nhóm | sự kiện | ghi chú |
|---|---|---|
| có parking để dịch (`idle > cash` ở ít nhất 1 sổ) | **7**: E2, E3, E5, E6, E8, E16, E17 | trục `park:f` chỉ chạm được đúng 7 sự kiện này |
| `idle == cash` (tiền đã nằm trong deal, hoặc rỗng hẳn) | 8: E0, E4, E7, E10, E12, E13, E14, E15 | `park:f` = `cash`, không đổi gì |
| **∩ với `dd52<=−20%`** | **2**: E5 (2018-07-05, −25,3%), E8 (2020-07-27, −23,4%) | **`parkdd:f` chỉ chạm được 2 sự kiện** |

3 sự kiện sâu còn lại (E4 2018-05-28, E7 2020-03-11, E10 2022-06-15) đều `idle == cash` ⇒ cổng `dd52`
mở nhưng **không có gì để dịch**. Tức là **N hiệu dụng của trục dd52-gated = 2** trên 12,5 năm.
Con số này phải nằm trước mọi bảng kết quả, vì nó là trần cứng cho mọi kết luận bên dưới.

---

## 2. Harness + cổng 1 (tái lập control)

Lệnh pin R3 **nguyên văn** (`data/results_registry.md`, mục 2026-08-03): `NAV_TOTAL_B=50`
`ETF_LIQ=custompitg` `BASKET_WT=namecap` `BASKET_SELECT=yieldcombo` `PARK_STATES="3:0.7"`
`AUDIT_END=2026-06-19`, snapshot `data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`,
`$DNA_PYEXE` (pandas 3), `LAG_ADV_BASIS` để mặc định (= `price`). **`MGE` TẮT hoàn toàn ở mọi chân.**

| kiểm tra | kết quả |
|---|---|
| **control `cash`** | **28,86% / MaxDD −17,79% / Calmar 1,62 / Final NAV 1.178,01B / IS 27,09% / OOS 30,48%** — **khớp tuyệt đối** số pin R3 chính thức 2026-08-03 |
| **`park:0` (identity)** | trùng control **từng chữ số** trên cả 6 chỉ tiêu ⇒ nhánh parser đúng |
| self-check cash-flow | **0 VND (BAL+LAG) ở 18/18 chân** |
| **borrow-audit** | **total borrow cost = 0 VND, max gross combined = 1,000 ở 18/18 chân** |

Dòng cuối là **bằng chứng tách biến thành công**: đây là **sizing thuần**, không một đồng vay — đúng
thứ p2 không đo được. ⇒ **Cổng 1 PASS**, mọi số dưới đây so sánh được.

---

## 3. Kết quả — dose-response theo `f`

*(Sharpe ở bảng này tự tính lại từ chuỗi NAV ngày qua `dsr_pbo_annex.load_nav`; registry pin 1,90 từ
bản in engine — khác quy ước gom NAV theo ngày, **không** phải chênh lệch kết quả. Chỉ đọc delta trong
cùng một cột.)*

### 3.1 `park:f` — dịch parking ở MỌI sự kiện washout

| f | CAGR | ΔCAGR | Sharpe | MaxDD | Calmar | IS 14-19 | OOS 20+ | ΔOOS |
|---|---|---|---|---|---|---|---|---|
| 0,00 *(≡ control)* | 28,86% | — | 1,832 | **−17,79%** | 1,623 | 27,09% | 30,48% | — |
| 0,25 | 29,68% | **+0,82pp** | 1,888 | −17,79% | 1,669 | 27,25% | 31,93% | +1,45pp |
| 0,50 | 29,73% | +0,87pp | 1,887 | −17,79% | 1,672 | 27,26% | 32,03% | +1,55pp |
| **0,75** | **29,97%** | **+1,10pp** | **1,896** | −17,78% | **1,685** | 27,36% | **32,38%** | **+1,90pp** |
| 1,00 *(≡ `idle`)* | 29,76% | +0,89pp | 1,876 | −17,78% | 1,673 | 27,43% | 31,90% | +1,42pp |

### 3.2 `parkdd:f` — dịch parking CHỈ ở washout sâu `dd52<=−20%`

| f | CAGR | ΔCAGR | Sharpe | MaxDD | Calmar | ΔOOS |
|---|---|---|---|---|---|---|
| 0,25 | 29,42% | +0,56pp | 1,876 | −17,79% | 1,654 | +0,97pp |
| 0,50 | 29,22% | +0,36pp | 1,858 | −17,79% | 1,643 | +0,53pp |
| 0,75 | 29,55% | +0,69pp | 1,881 | −17,79% | 1,662 | +1,12pp |
| 1,00 | 29,30% | +0,44pp | 1,866 | −17,79% | 1,648 | +0,56pp |

### 3.3 Đọc bảng — trả lời đúng 3 câu hỏi cổng 2 của dispatch

**(a) Có đơn điệu không? — KHÔNG, ở cả hai họ.**
`park:f` nhảy bậc ngay tại `f=0,25` (+0,82pp = **75% của mức tối đa**), rồi gần như phẳng, đỉnh ở 0,75,
**tụt** ở 1,0. `parkdd:f` dao động **0,56 → 0,36 → 0,69 → 0,44** — thứ tự đảo hai lần. Hình dạng đúng
của "một bậc + nhiễu", **không** phải đường liều-đáp ứng. Đối chiếu: chính dose-response đơn điệu là thứ
đã làm `dd52` thành ứng viên duy nhất ở **tầng vị thế** (p2 §2.2). Ở tầng danh mục nó **không có**.

**(b) Mức `f` nào tối ưu mà không làm xấu MaxDD?** — trên lưới, `f=0,75` tối ưu cả CAGR/Sharpe/Calmar;
và **MaxDD không xấu đi ở BẤT KỲ mức nào** (−17,79% → −17,78%, **cùng ngày đáy 2018-07-05** ở cả 18 chân).
Nhưng "tối ưu trên lưới" chính xác là thứ **PBO cấm** dùng làm căn cứ chọn (§4.2).

**(c) LOO per-year:** **0/13 năm âm ở mọi mức `f`**, cả hai họ (min +0,50pp khi bỏ 2022 với `park:0,50`).
⚠️ **Con số này về sau hoá ra gây hiểu nhầm** — xem §5, đây là đúng chỗ quant-skeptic bắt được.

**(d) `parkdd` thua `park` ở MỌI mức `f`** (+0,56/+0,36/+0,69/+0,44 vs +0,82/+0,87/+1,10/+0,89).
Điều kiện hoá theo độ sâu **lấy đi** giá trị chứ không thêm. Đây là lần **thứ ba** cùng một kết luận:
ở tầng danh mục, thứ làm ra số là **TỔNG LƯỢNG vốn đưa vào CAPIT**, **không** phải chất lượng cổng độ sâu
(p2 §1.3(3): chân không cổng +0,80/+1,07pp > chân có cổng +0,61/+0,64pp — cùng chiều, cùng cỡ).

---

## 4. Kỷ luật thống kê

### 4.1 Đối chiếu nghiên cứu cũ — bắt buộc, và đây là phần khó chịu nhất

**Chính họ `park:f` đã chạy ngày 2026-07-31** (job `Taylor_20260731_094324`,
`research/capit_sizing_backtest_20260731.md` §3.3). Kết quả khi đó vs hôm nay:

| f | 07-31 (control 27,60%) | **hôm nay (control 28,86%)** |
|---|---|---|
| 0,25 | **+0,09pp** | **+0,82pp** |
| 0,50 | +0,39pp | +0,87pp |
| 1,00 | +0,32pp | +0,89pp |

Cùng cơ chế, **cùng snapshot BQ** (`asof20260729_postrestate`), cùng bộ sự kiện. Chênh **2-9 lần**.
Nguyên nhân đã truy được, **không phải bug**: giữa hai lần đo có 2 thay đổi cơ sở giá ở production —
(i) vá look-ahead cơ sở giá dựng rổ (control 27,60% → 27,24%, `results_registry.md` mục 2026-08-02), và
(ii) đổi mặc định `LAG_ADV_BASIS` `close`→`price` ngày 08-02 (commit `0062aa0`) (27,24% → 28,86%).

Đọc đúng, hai vế:
- **Số hôm nay đáng tin hơn** — đây là lần đo **đầu tiên** của họ này trên mặc định production đã vá
  look-ahead. Số 07-31 đo trên vintage nay đã biết là có look-ahead.
- **Nhưng** một ước lượng dịch 2-9 lần dưới một thay đổi **cơ sở dữ liệu không liên quan gì đến cơ chế**
  thì không phải thứ để đặt quyết định wire lên. Nó nói rằng phần lớn "+0,8…+1,1pp" là **tương tác với
  chi tiết cơ sở giá**, không phải một hằng số của cơ chế.

**Và phán quyết cũ vẫn treo:** `capit_sizing_pbo_robustness_20260731.md` kết luận **"DỪNG, KHÔNG
IMPLEMENT"** cho toàn họ sizing CAPIT, vì PBO không ổn định theo đặc tả (**0,073 → 0,814**). Job này
**không** đảo ngược được phán quyết đó — nó tái lập chính hiện tượng bất ổn ấy (§4.2).

### 4.2 PBO (CSCV, Bailey et al 2017) — cổng quyết định thật của job này

| họ | S=8 | S=12 | S=16 |
|---|---|---|---|
| **đầy đủ 9 cấu hình** (control + park×4 + parkdd×4) | **0,671** | 0,464 | **0,611** |
| chỉ `park:f` (control + 4) | **0,614** | 0,478 | **0,574** |
| chỉ `parkdd:f` (control + 4) | 0,400 | 0,179 | 0,370 |

**PBO ≥ 0,5 ở 4/6 đặc tả** cho các họ chứa ứng viên ⇒ theo đúng KB §Quy chuẩn 5, **cấm chọn cấu hình
theo thứ hạng backtest**; ưu tiên cấu hình robust-trung vị, không phải IS-best. Nói cách khác: **`f=0,75`
không được phép là đề xuất**, dù nó tốt nhất trên lưới.
Họ `parkdd` riêng có PBO thấp (0,18-0,40) — **không** đọc là ủng hộ: mọi thành viên của nó đều **kém hơn**
chân ungated, một họ toàn cấu hình xoàng thì PBO thấp một cách tầm thường (đúng cơ chế đã ghi ở
`capit_sizing_pbo_robustness_20260731.md` §3).

### 4.3 DSR — chạy đủ, nhưng KHÔNG phải bằng chứng ủng hộ

DSR = **1,0000** cho **mọi** chân, **kể cả control**, ở cả N=9 / 24 / 38. Lý do (giống p2 §3): DSR chạy
trên chuỗi NAV của **cả hệ V2.4** (SR/obs 0,115-0,119, Sharpe ~1,83+), nên nó chỉ nói "chuỗi tổng thể
không phải sản phẩm của dò tham số". Nó **không** tách được đóng góp của lớp sizing. Báo cáo đúng phải là:
**DSR ở đây vô thông tin**, không được trích như một cổng đã qua.

### 4.4 N_trials khai báo

- **Job này: 9 cấu hình** (control + `park`×4 + `parkdd`×4) + **8 chân leave-one-event-out** (§5).
- **Cộng dồn họ sizing CAPIT**: 10 leg (07-31) + 5 đặc tả PBO (07-31) + 9 (job này) = **24**.
- **Cộng dồn cả chuỗi margin/Kelly/sizing washout**: p1 (17) + p2 (27+4) + job này (9) = **57** phép thử
  trên cùng chủ đề. Khai báo đủ, không chọn-lọc-sau: **mọi** chân đã chạy đều nằm trong báo cáo này.

---

## 5. Leave-one-EVENT-out — quant-skeptic bắt đúng chỗ, và nó đổi kết luận

`bin/verify_finding.sh` → **quant-skeptic: CONFIRMED (confidence high)**, 7/7 check pass, có recompute
độc lập (CAGR/MaxDD/FinalNAV của chân PK025 từ CSV thô, khớp đến chữ số đã trích) và tự đối chiếu
được số 07-31. Log: `mike/logs/verify_20260803_084642.log`.

**Killer objection của reviewer** (nguyên văn ý): *LOO chỉ làm theo NĂM, không theo SỰ KIỆN; với ~9-10
sự kiện washout trong cửa sổ OOS, một đợt lớn (vd COVID 2020) có thể gánh phần lớn delta OOS mà LOO
theo năm vẫn che được.*

**Đã chạy để đóng lỗ hổng** — thêm knob `CAPIT_PARK_LOO`, chạy `park:0,25` (ứng viên) bỏ boost parking
ở **từng** sự kiện một, 7 sự kiện + 1 chân hồi quy:

*(Kiểm hồi quy trước: chân `CAPIT_PARK_LOO` rỗng tái lập `park:0,25` **CAGR 29,6811% — trùng từng chữ
số**, knob inert khi không dùng.)*

| bỏ sự kiện | CAGR | ΔCAGR vs control | **còn lại % edge** | ΔOOS | **còn lại % edge OOS** | MaxDD |
|---|---|---|---|---|---|---|
| — (đầy đủ) | 29,68% | +0,82pp | 100% | +1,45pp | 100% | −17,79% |
| E2 2015-08-24 (IS) | 29,67% | +0,81pp | 99% | +1,45pp | 100% | −17,79% |
| E3 2016-01-18 (IS) | 29,68% | +0,81pp | 99% | +1,45pp | 100% | −17,79% |
| E5 2018-07-05 (IS) | 29,63% | +0,76pp | 93% | +1,46pp | 101% | −17,79% |
| E6 2020-02-03 (OOS) | 29,66% | +0,80pp | 98% | +1,41pp | 97% | −17,79% |
| **E8 2020-07-27 (OOS)** | **29,13%** | **+0,27pp** | **33%** | **+0,38pp** | **26%** | −17,79% |
| **E16 2025-10-20 (OOS)** | 29,45% | +0,59pp | **72%** | +0,99pp | **69%** | −17,79% |
| E17 2026-03-09 (OOS) | 29,68% | +0,82pp | 100% | +1,45pp | 100% | −17,79% |

**Kết luận thẳng:**
- **Một sự kiện duy nhất (2020-07-27) gánh 67% edge toàn kỳ và 74% edge OOS.** Cộng thêm 2025-10-20 là
  **~95%**. **5/7 sự kiện còn lại đóng góp ~0** (99-101% edge còn lại khi bỏ chúng).
- **LOO theo NĂM "0/13 âm" là một ảo ảnh của phép compounding**: lợi ích của E8 (tháng 7/2020) được
  nhân vào NAV suốt mọi năm sau, nên bỏ **bất kỳ năm nào** vẫn thấy delta dương. Reviewer đúng, và
  đây là loại lỗi rất dễ tin — bảng LOO-năm trông y hệt một edge bền.
- **MaxDD không đổi ở cả 8 chân LOO** (−17,79%) ⇒ mệnh đề "cơ chế này vô hại về rủi ro" **vẫn đứng**;
  chỉ mệnh đề "edge phân bố rộng" là sụp.

Đây đúng mẫu hình mà KB §Quy chuẩn 5 gọi là **reshuffle-luck** (ca Wave1/H8a 2026-07-05): 1-2 sự kiện
gánh hết edge ⇒ **không wire**.

---

## 6. Verdict

| trục | verdict | lý do quyết định |
|---|---|---|
| **`parkdd:f`** (dịch parking CHỈ ở washout sâu) | **🔴 NO-GO** | Kém hơn ungated ở **mọi** `f`; dose-response zig-zag; **N hiệu dụng = 2 sự kiện**/12,5 năm; thêm 1 tham số mà không đổi lại gì |
| **`park:f`** (dịch parking mọi sự kiện) | **🔴 NO-GO cho wire** *(hạ từ CONDITIONAL)* | 1 sự kiện gánh 67% edge / 2 sự kiện gánh 95%; PBO ≥0,5 ở 4/6 đặc tả ⇒ cấm chọn `f` theo hạng; ước lượng dịch 2-9× theo vintage; họ này đang mang phán quyết **DỪNG-KHÔNG-WIRE 2026-07-31** chưa được đảo |

**Trả lời trực tiếp câu hỏi mà job này được giao** (tách +0,61pp của L1b ra thành phần sizing riêng):
+0,61pp đó **không** phải là phần thưởng của "dịch vốn ở washout sâu". Khi tách sạch (0 đồng vay):
- điều kiện hoá theo **độ sâu** làm **giảm** giá trị ⇒ không phải nguồn của +0,61pp;
- phần "dịch vốn" **không điều kiện** thì lớn hơn, nhưng khi soi tới cấp sự kiện thì **~95% nằm ở 2 đợt**
  — nghĩa là ngay cả nó cũng không phải một cơ chế đã được chứng minh, mà là **2 lần gặp may đã được
  compounding phóng đại**.

**Nếu về sau vẫn muốn theo hướng này**, giá trị duy nhất được phép nêu là **`f = 0,25`** — không phải
vì tốt nhất (0,75 mới tốt nhất trên lưới), mà vì nó bắt ~75% lợi ích tối đa với độ lệch nhỏ nhất khỏi
spec đã pin, và chọn 0,75 chính là phép chọn-theo-hạng mà PBO cấm. **Nhưng ở trạng thái bằng chứng hiện
tại thì ngay cả `f=0,25` cũng chưa đủ điều kiện wire.**

---

## 7. Việc còn treo / bước tiếp theo (không tự làm)

1. **[Đo lại có mốc, không gấp]** Chờ thêm sự kiện washout OOS sau `AUDIT_END=2026-06-19` rồi chạy lại
   đúng bộ chân này. Điều kiện đảo verdict phải nêu **trước**: edge còn ≥50% khi bỏ sự kiện gánh nhiều
   nhất, **và** PBO < 0,5 ở đa số đặc tả. (Đề xuất thứ hai của quant-skeptic, giữ nguyên.)
2. **[Ghi sổ]** Trục `park:f`/`parkdd:f` nên được ghi vào `kb/projects/` chung với sổ theo dõi họ sizing
   CAPIT 07-31 để lần sau không ai chạy lại vòng thứ ba mà không đọc §4.1.
3. **[Vẫn treo từ p1/p2, không đổi]** `pp0Buy` thật của SpaceX + P0 shadow log ≥10 phiên — điều kiện bắt
   buộc nếu còn muốn theo hướng **margin** (job này vẫn **không** chạm tới hướng đó: 0 đồng vay).
4. **[Vệ sinh, từ p2 §4 mục 4]** Bẫy `MGE_GATE` vô hiệu im lặng khi `RECOVERY_PARK=0` — vẫn chưa ghi vào
   nơi ai đó sẽ đọc trước khi dùng lại `MGE_GATE`.

---

## 8. Minh bạch / tái lập

- **Artifact:** `mike/agents/Taylor/exp_margin_kelly/p3/` — `engine_park.py` (bản sao nghiên cứu,
  diff vs production = 5 hunk thuần thêm), `run_p3.sh`, `metrics_p3.py` + `metrics_p3.log`,
  `loo_event.py` + `loo_event.log`, **18 log chạy** `p3_*.log`.
- **18/18 chân**: `EXIT=0`, self-check cash-flow identity **0 VND** cả BAL+LAG, borrow cost **0 VND**,
  max gross combined **1,000**.
- **Mọi CSV kết quả có `EXP_TAG` `p3_*`** (coding_guidelines §8) — canonical `..._wtnamecap.csv` không bị
  đụng tới.
- **quant-skeptic:** CONFIRMED (high) trên bản kết luận **CONDITIONAL**; §5 chạy sau đó làm kết luận
  **thận trọng hơn** (CONDITIONAL → NO-GO), tức là bằng chứng mới đi cùng chiều với reviewer, không
  ngược. Không có kết luận GO nào được đưa ra.
- **RESEARCH-ONLY:** không sửa `data/trading_rules.json`, không sửa production. Không có đề xuất wire.
