# CAPIT sizing — 4 việc cổng wire (follow-up verdict quant-skeptic CONFIRMED)

> ⚠️ **SUPERSEDED một phần (2026-07-31, job `Taylor_20260731_151958`) — ĐỌC TRƯỚC KHI TRÍCH.**
> §Việc 1.2 (**PBO = 0,732**) và mọi kết luận dựa vào nó (§5 bảng cổng, §5.2 trụ (c), việc "bác
> `idle`"/"bác `navsize:0.40`") **KHÔNG còn đứng vững**: PBO không ổn định theo đặc tả, chạy từ
> **0,073** (neo 15 sự kiện CAPIT thật — đúng đặc tả reviewer yêu cầu) tới **0,814** (calendar S=8).
> ⇒ Đề xuất wire ở §5.1 **ĐÃ DỪNG, KHÔNG implement**. Chi tiết + 3 phương án trả user:
> `research/capit_sizing_pbo_robustness_20260731.md`.
> §Việc 2 (trần %ADV), §Việc 3 (lưới navsize), §Việc 4 (stress washout sâu) **KHÔNG bị ảnh hưởng** —
> chúng không dùng PBO và vẫn là bằng chứng hiện hành.

Job `Taylor_20260731_111654`. Nối tiếp `Taylor_20260731_094324`
(`research/capit_sizing_backtest_20260731.md`) + verdict CONFIRMED
`logs/verify_20260731_105431.log`.

**Killer objection của reviewer (lý do 4 việc này tồn tại):** N=15 sự kiện CAPIT lịch sử KHÔNG
chứa một lần washout thất bại sâu nào (lỗ tệ nhất quan sát −4,7%) ⇒ kết luận "cơ sở sizing gần như
không quan trọng" chỉ được kiểm chứng ở đúng vùng mà sizing ít quan trọng nhất.

Điều kiện chạy giữ nguyên job trước: `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`,
`NAV_TOTAL_B=50`, `ETF_LIQ=custompitg`, `BASKET_WT=namecap`, `BASKET_SELECT=yieldcombo`,
`PARK_STATES=3:0.7`, `AUDIT_END=2026-06-19`, threads=1, `$DNA_PYEXE`, runner
`data/capit_sizing_20260731/run_leg.sh`. 3 leg mới **EXIT=0, self-check cash-flow identity = 0 VND
cả BAL lẫn LAG**.

Script tái lập: `mike/agents/Taylor/job_20260731_111654_{dsr_pbo,adv,adv2,stress}.py`.
Artefact: `research/capit_adv_check_20260731.csv`, `research/capit_stress_deep_20260731.csv`.

---

## VIỆC 1 — DSR / PBO trên họ N=13 trial

`N_trials` khai lại = **13** (10 leg job trước + 3 leg navsize job này, §Việc 3 — cộng vào, không giấu).
Tính trên chuỗi `combined_nav` daily (T=3106 phiên) đọc thẳng từ 13 audit CSV, không chạy lại backtest.

### 1.1 DSR = 1,0000 cho CẢ 13 leg — và con số này KHÔNG trả lời câu hỏi đang hỏi

| | |
|---|---|
| Var(SR) giữa 13 trial (daily) | 1,64e−06 |
| SR0 (kỳ vọng max-Sharpe dưới null, N=13) | 0,00202/ngày = **0,032 annualized** |
| SR quan sát mỗi leg | 1,79 – 1,86 annualized |
| z | 6,12 – 6,40 ⇒ **DSR = 1,0000 mọi leg** |

**Đọc đúng:** tương quan lợi suất ngày giữa các leg là **0,982 – 0,998 (median 0,993)** — cả 13 leg
là CÙNG một chiến lược V2.3A, chỉ khác nhau ở kích cỡ của một arm bắn 15 lần trong 12 năm. Vì thế
DSR ở đây trả lời "Sharpe 1,84 của V2.3A có thật sau khi trừ 13 lần thử không?" (→ có, áp đảo),
**chứ không phải** "lựa chọn cơ sở sizing có edge không?". Trích DSR=1,0 như bằng chứng ủng hộ
`navsize:0.25` sẽ là trích sai — đây là chỉ tiêu đi qua cổng §Quy chuẩn 5 một cách hình thức, không
phải bằng chứng cho quyết định này.

### 1.2 PBO (CSCV, S=16, 12.870 tổ hợp) = **0,732** — CAO, và đây MỚI là con số có ý nghĩa

- Median OOS-rank của config thắng IS = **5/13** (dưới trung vị).
- Tần suất thắng IS: `navsize:0.40` 38,2% · `park:0.50` 22,3% · `idle` 21,7% · `navsize:0.35` 6,0%
  · `booknav` 4,1% · `cash` 3,7% — tức các leg **hung hăng nhất** hay thắng IS nhất, rồi tụt hạng OOS.

**Hệ quả cho quyết định wire (quan trọng nhất của Việc 1):** PBO ≥ 0,5 ⇒ theo đúng §Quy chuẩn 5,
**cấm chọn config theo thứ hạng backtest**; phải chọn config robust/trung vị. Điều này:
1. **Bác `idle`** — leg duy nhất qua cổng pre-registered của job trước (Calmar 1,60 vs 1,58) chính là
   một trong 3 leg hay thắng IS nhất. Biên +0,02 Calmar của nó là đúng thứ PBO nói là ảo.
2. **Bác `navsize:0.40`** (thắng IS 38,2%, CAGR cao nhất họ navsize).
3. **Ủng hộ lập luận gốc của đề xuất** — đề xuất `navsize:0.25` chưa bao giờ dựa trên hiệu năng
   (nó THẤP hơn baseline −0,30pp CAGR); nó dựa trên tính xác định. PBO 0,73 nói rằng đó là loại
   lập luận DUY NHẤT còn đứng vững ở họ này.

---

## VIỆC 2 — đối chiếu navsize:0,25 với trần %ADV THẬT

Tái lập đúng công thức production `golive_recommend_v23.capit_adv_caps()`:
`cap_vnd_i = ADV_X · ADV20_i · ADV_D` với `ADV_X=0,10`, `ADV_D=2,0`; `ADV20_i` = **median
(Price×Volume) của 20 phiên NGAY TRƯỚC ngày fire** (ngày fire không tính), cửa sổ 90 ngày lịch,
nguồn `ticker_prune` (= `CAPIT_POOL_SOURCE='prune'` đang ghim live). Rổ mỗi sự kiện đọc từ chính
audit CSV leg `navsize:0.25` (`play_type` `CAPITB_E*`/`CAPITL_E*`).

### 2.1 Ở NAV FLEET THẬT (1,823 tỷ — SpaceX 0,937 + ZaloPay 0,886, `nav_history_*` 2026-07-30)

| E | ngày | size | n mã | target 25%·size (tỷ) | Σ cap ADV rổ (tỷ) | util |
|---|---|---|---|---|---|---|
| 0 | 2014-05-08 | 1,00 | 3 | 0,456 | 24,44 | 1,9% |
| 2 | 2015-08-24 | 0,375 | 3 | 0,171 | 22,95 | 0,7% |
| 3 | 2016-01-18 | 0,75 | 5 | 0,342 | 13,96 | 2,5% |
| **4** | **2018-05-28** | 1,00 | 3 | 0,456 | **2,16** | **21,1%** ← chặt nhất |
| 5 | 2018-07-05 | 0,375 | 1 | 0,171 | 11,04 | 1,6% |
| 6 | 2020-02-03 | 0,75 | 5 | 0,342 | 3,01 | 11,4% |
| 7 | 2020-03-11 | 0,25 | 4 | 0,114 | 2,98 | 3,8% |
| 8 | 2020-07-27 | 0,375 | 8 | 0,171 | 16,50 | 1,0% |
| 10 | 2022-06-15 | 0,25 | 4 | 0,114 | 134,10 | 0,1% |
| 12 | 2023-10-30 | 1,00 | 4 | 0,456 | 8,76 | 5,2% |
| 13 | 2024-04-17 | 0,50 | 6 | 0,228 | 81,00 | 0,3% |
| 14 | 2024-08-05 | 0,50 | 5 | 0,228 | 61,71 | 0,4% |
| 15 | 2025-04-03 | 0,50 | 5 | 0,228 | 28,66 | 0,8% |
| 16 | 2025-10-20 | 0,75 | 3 | 0,342 | 18,32 | 1,9% |
| 17 | 2026-03-09 | 0,75 | 6 | 0,342 | 135,76 | 0,3% |

**Trả lời thẳng: KHÔNG. Ở quy mô hiện tại, 25% NAV KHÔNG vượt sức hấp thụ thanh khoản của rổ ở bất
kỳ sự kiện nào trong 15** — util median **1,6%**, max **21,1%** (E4 2018-05-28, rổ FMC/TCM/VSC —
rổ mỏng nhất lịch sử). 0/15 sự kiện vượt. Hệ số navsize tối đa còn vừa cap tổng tại NAV thật: min
**1,18** (E4), p10 3,24, median 16,2 ⇒ dư địa ≥4,7× so với 0,25 ngay cả ở sự kiện chặt nhất.

### 2.2 Trần THỰC TẾ — ngưỡng NAV mà 25% bắt đầu chạm cap

| tiêu chí | NAV fleet tối đa để `navsize:0.25` không chạm cap tổng |
|---|---|
| sự kiện chặt nhất (E4 2018) | **~8,6 tỷ VND** |
| p10 sự kiện | ~23,6 tỷ VND |
| sự kiện trung vị | ~117,8 tỷ VND |

⇒ **`navsize:0.25` khả thi thực tế tới NAV fleet ~8,6 tỷ** (gấp 4,7× hiện tại) mà không sự kiện nào
bị cắt; từ ~8,6 → ~24 tỷ sẽ có lác đác sự kiện rổ-mỏng bị ADV cap ép xuống (cơ chế `cap_capit_orders`
đã fail-closed sẵn, không cần rule mới); trên ~24 tỷ thì cap bắt đầu là ràng buộc thường trực và
25% trở thành "trần mong muốn" chứ không phải trần thực thi.

### 2.3 Phát hiện phụ (giới hạn của CHÍNH backtest, áp cho mọi leg — không riêng navsize)

Ở mức sổ 50 tỷ của backtest, target 25%·size **vượt** Σ cap ADV ở **4/15** sự kiện (E4 util 5,80×,
E6 3,12×, E12 1,43×, E7 1,05×) và có ≥1 tên binding ở 12/15. Backtest **không mô hình hoá ràng buộc
này** (đã ghi ở §5 job trước) ⇒ ở quy mô 50 tỷ, phần triển khai CAPIT của **mọi leg kể cả baseline
`cash`** là không khả thi về thanh khoản ở vài sự kiện. Đây là **hiện tượng quy mô**, không phải lỗi
riêng của `navsize:0.25`, và nó không đảo bất kỳ so sánh tương đối nào giữa các leg.

---

## VIỆC 3 — lưới navsize thành mặt phẳng thật (thêm 0,15 / 0,30 / 0,35)

3 leg mới: `EXIT=0`, `[selfcheck BAL]`/`[selfcheck LAG]` cash-flow identity max err = **0 VND**, borrow cost 0 VND.

| base | CAGR | Sharpe | MaxDD | Calmar | IS 14-19 | OOS 20-26 |
|---|---|---|---|---|---|---|
| `cash` **(baseline pin R3)** | 27,60% | 1,84 | −17,5% | **1,58** | 23,38% | 28,49% |
| `navsize:0.15` | 26,66% | 1,79 | **−17,3%** | 1,54 | 22,74% | 27,35% |
| **`navsize:0.25`** | 27,30% | 1,83 | −17,5% | 1,56 | 22,90% | 28,23% |
| `navsize:0.30` | 27,54% | 1,84 | −17,6% | 1,56 | 23,00% | 28,61% |
| `navsize:0.35` | 27,74% | 1,85 | −17,6% | **1,57** | 23,11% | 28,85% |
| `navsize:0.40` | 27,90% | 1,86 | −18,0% | 1,55 | 23,22% | 29,00% |
| `booknav` **(ĐANG CHẠY LIVE)** | 27,34% | 1,82 | −18,0% | **1,52** | 22,37% | 28,76% |
| `idle` | 27,92% | 1,85 | −17,4% | 1,60 | 23,68% | 28,59% |

**Đây là một MẶT PHẲNG thật, không phải điểm nhọn** — 5 điểm lưới:
- CAGR **đơn điệu tăng** 26,66 → 27,90% (không có bướu, không có đảo dấu);
- MaxDD **đơn điệu xấu đi** −17,3 → −18,0%;
- Calmar 1,54 / 1,56 / 1,56 / 1,57 / 1,55 — **biên độ toàn lưới chỉ 0,03**, đỉnh phẳng ở 0,30–0,35;
- IS và OOS **cùng dấu, cùng thứ tự** ở cả 5 điểm (không có điểm nào IS tốt/OOS xấu).

Đọc: **0,25 nằm ở nửa THẬN TRỌNG của một cao nguyên phẳng, không phải đỉnh được chọn** — đúng loại
điểm mà PBO=0,73 yêu cầu (chọn robust, không chọn IS-best). Nếu tối ưu Calmar trên lưới thì phải
chọn 0,35 (1,57) — Việc 4 dưới đây là lý do KHÔNG làm thế.

⚠️ Chênh 0,25 → 0,35 chỉ là +0,44pp CAGR / +0,01 Calmar, nhỏ hơn cả sai số vintage dữ liệu đã đo
(+0,47pp CAGR do trôi dữ liệu ở lần re-pin 07-29). Toàn bộ lưới nằm trong nhiễu về hiệu năng.

---

## VIỆC 4 — kịch bản stress washout SÂU (đúng thứ đang thiếu trong mẫu)

**Cách làm (auditable):** phần **phơi nhiễm** là DỮ LIỆU THẬT — %NAV danh mục thực sự triển khai ở
mỗi sự kiện, đọc từ TX của chính leg đó (peak net cumulative buy−sell mỗi sổ ÷ `nav_*_ref`, rồi
quy về NAV danh mục bằng `cap_book / combined_nav` theo META `combination_note`). Chỉ **đường giá
sau khi mua** là giả lập — đây chính là biến còn thiếu trong mẫu lịch sử.

### 4.1 Phơi nhiễm thật (15 sự kiện, % NAV TỔNG danh mục)

| công thức | min | median | **max (đuôi)** |
|---|---|---|---|
| `cash` (spec pin) | 0,69% | 9,46% | **35,05%** |
| `idle` | 1,80% | 17,65% | **35,52%** |
| `booknav` (LIVE) | 0,00% | 5,80% | 25,48% |
| `navsize:0.15` | 1,87% | 7,54% | 22,66% |
| **`navsize:0.25`** | 2,18% | 10,17% | **23,87%** |
| `navsize:0.30` | 2,18% | 11,13% | 25,17% |
| `navsize:0.35` | 2,18% | 12,04% | 26,83% |
| `navsize:0.40` | 2,18% | 12,09% | 28,49% |

### 4.2 Cú đánh vào NAV danh mục ở sự kiện tệ nhất

| công thức | S0 lịch sử (quan sát) | S2 −30% hồi nửa đường | **S3 −30% cắt lỗ tại đáy** | S4 −45% hồi nửa đường |
|---|---|---|---|---|
| `cash` | −0,35% | −5,26% | **−10,51%** | −7,89% |
| `idle` | −0,44% | −5,33% | **−10,65%** | −7,99% |
| `booknav` (LIVE) | −0,00% | −3,82% | **−7,64%** | −5,73% |
| `navsize:0.15` | −0,29% | −3,40% | −6,80% | −5,10% |
| **`navsize:0.25`** | −0,41% | −3,58% | **−7,16%** | −5,37% |
| `navsize:0.30` | −0,46% | −3,78% | −7,55% | −5,66% |
| `navsize:0.35` | −0,40% | −4,02% | −8,05% | −6,04% |
| `navsize:0.40` | −0,44% | −4,27% | −8,55% | −6,41% |

(Đáy drawdown tạm thời trước hồi phục, S4: `idle` −15,98% · `cash` −15,77% · `booknav` −11,47% ·
`navsize:0.25` −10,74% · `navsize:0.15` −10,20%.)

### 4.3 CÓ phân hoá rõ — và nó ĐẢO kết luận đọc từ lịch sử

| kịch bản | độ rộng giữa các công thức |
|---|---|
| **S0 lịch sử (mẫu thật)** | **0,46pp** ← đúng như reviewer nói: gần như vô hình |
| S2 −30% hồi nửa đường | 1,93pp |
| **S3 −30% cắt lỗ tại đáy** | **3,86pp (×8,4 so với S0)** |
| S4 −45% hồi nửa đường | 2,90pp |

**Ba kết luận:**
1. **Reviewer đúng.** Trong mẫu lịch sử độ rộng chỉ 0,46pp — mẫu KHÔNG có khả năng phân biệt các
   công thức. Câu "cơ sở sizing không quan trọng" của job trước chỉ đúng có điều kiện: *ở đường đi
   nhẹ-vừa*. Dưới washout sâu, độ rộng nở gấp ~8 lần và trở thành khoản tiền thật.
2. **Xếp hạng dưới stress ĐẢO NGƯỢC xếp hạng lịch sử.** `idle` — leg DUY NHẤT qua cổng pre-registered
   của job trước (Calmar 1,60) — là leg **TỆ NHẤT** trong cả 3 kịch bản stress (−10,65% S3). `cash`
   (spec pin R3) đứng áp chót (−10,51%). Cả hai đều vì cùng một lý do: cơ sở "tiền mặt tình cờ có"
   không có trần, nên đúng lúc sổ đầy tiền (= thường là sau một đợt bán tháo, tức đúng lúc rủi ro đuôi
   cao nhất) nó đặt 35% NAV vào một rổ deep-value.
3. **`navsize:0.25` cắt được đuôi**: −7,16% S3, tức **tốt hơn `cash` 3,35pp và tốt hơn công thức
   ĐANG CHẠY LIVE (`booknav`) 0,48pp**; ở S4 tốt hơn `cash` 2,52pp / live 0,36pp. Chi phí đổi lấy:
   −0,30pp CAGR lịch sử (nằm trong nhiễu, §Việc 3).

### 4.4 Giới hạn thật của Việc 4 (không được bỏ qua khi trích)

- **Backtest KHÔNG thi hành được trần một cách chính xác.** Đo trực tiếp: ở 5/15 sự kiện (E0-BAL,
  E4, E10-BAL, E12, E14) phần triển khai thực tế của MỌI leg **hội tụ như nhau** dù `wt` mục tiêu
  lệch tới 6,7× (vd E10: `cash` wt=0,25 và `navsize:0.15` wt=0,0375 đều ra ~21,6% sổ BAL) — vì ở
  các sự kiện đó CAPIT gần như là tier duy nhất tranh vốn của sổ, nên sàn sizing của engine chi phối
  chứ không phải `wt`. Live thì ngược lại: công thức được áp THẲNG để tính khối lượng lệnh
  (`golive_recommend_v23` → plan → `cap_capit_orders`), nên trần 25% là **cưỡng chế chính xác**.
  ⇒ Con số §4.2 **ƯỚC LƯỢNG THẤP** lợi ích cắt đuôi thật của `navsize:0.25` khi chạy live, chứ không
  thổi phồng. (Cùng lý do này giải thích vì sao cả 13 leg dồn cục trong 1,3pp CAGR.)
- Kịch bản S1-S4 là **giả lập có chủ đích**, không phải xác suất đã ước lượng — chúng trả lời "nếu
  xảy ra thì phân hoá bao nhiêu", KHÔNG trả lời "khả năng xảy ra bao nhiêu". n=15 vẫn là n=15.
- Bảng §4.1 (%NAV thực tế, max `cash` 35,05%) **đính chính** cột "%NAV `cash`" của §2 job trước
  (max 87,4%) — số cũ là **mục tiêu `wt`**, số này là **phần thực sự khớp lệnh**. Kết luận định
  tính không đổi (spec `cash` dao động ~0,7% → ~35% NAV giữa các sự kiện cùng mức tin cậy), nhưng
  biên độ đuôi thật nhỏ hơn con số đã trích trước đó.

---

## 5. TỔNG HỢP — `navsize:0.25` có đủ điều kiện wire không?

**CÓ — đủ điều kiện đề xuất wire**, với lập luận phải trình đúng như dưới đây (không trình như một
cải thiện hiệu năng).

| cổng | kết quả |
|---|---|
| DSR (N=13) | 1,0000 — **qua nhưng không thông tin** (đo V2.3A, không đo lựa chọn sizing), §1.1 |
| PBO/CSCV (N=13) | **0,732 CAO** ⇒ cấm chọn theo thứ hạng backtest; `navsize:0.25` là điểm robust, không phải IS-best. Bác `idle` và `navsize:0.40` |
| Mặt phẳng lưới | 5 điểm đơn điệu, Calmar biên độ 0,03, IS/OOS cùng dấu — không phải điểm nhọn |
| Trần %ADV thật | **KHÔNG binding** ở NAV hiện tại (util max 21%, 0/15 vượt); khả thi tới NAV fleet ~8,6 tỷ |
| Stress washout sâu | phân hoá rõ (3,86pp ở S3); `navsize:0.25` tốt hơn LIVE `booknav` 0,48pp và spec `cash` 3,35pp |
| Walk-forward IS/OOS | cùng dấu, không có leg nào IS-tốt/OOS-xấu |
| self-check | 13/13 leg EXIT=0, cash-flow identity 0 VND cả 2 sổ |

### 5.1 Công thức cuối đề xuất

> **CAPIT target = `state_size × 25% NAV TỔNG`** (fleet-level), rồi **chia theo account** đúng cơ chế
> `capit_account_shares()` hiện có; trần %ADV `cap_capit_orders()` giữ nguyên là **ràng buộc cứng
> cuối cùng, fail-closed** (không đổi 1 dòng).
>
> Theo `state_size` hiện hành: 1,0 → **25%** NAV · 0,75 (grind) → **18,75%** · 0,5 → **12,5%** ·
> 0,375 → **9,4%** · 0,25 → **6,25%**.

**Không có giới hạn thực tế nào buộc phải hạ xuống dưới 25% ở quy mô hiện tại** (Việc 2) — nhưng
kèm 1 điều kiện tái xét:

> **Gate quy mô**: khi NAV fleet vượt **~8,6 tỷ VND**, chạy lại Việc 2 trước khi giữ nguyên 25%.
> Không cần rule mới ở tầng code — `cap_capit_orders()` đã fail-closed nên vượt cap là bị CHẶN
> (không phải mua tràn); gate này chỉ để biết trước rằng 25% khi đó là "trần mong muốn", và
> con số hiệu năng backtest tương ứng không còn khả thi.

### 5.2 Lập luận phải trình đúng (chống trích sai)

- **KHÔNG** phải "cao hơn baseline": `navsize:0.25` **thấp hơn** spec pin `cash` −0,30pp CAGR / −0,02
  Calmar. Toàn bộ lưới nằm trong nhiễu hiệu năng (§3).
- Lý do wire = **(a) tính xác định** (chặn cả hai đuôi: sàn 6,25% chống ca E17 gần như bỏ lỡ tín hiệu,
  trần 25% chống ca 35% NAV vào rổ deep-value) + **(b) tốt hơn thứ ĐANG CHẠY LIVE** (`booknav`: Calmar
  1,52→1,56, MaxDD −18,0→−17,5%, IS 22,37→22,90%, stress S3 −7,64→−7,16%) + **(c) PBO 0,73 loại bỏ
  mọi lập luận dựa trên thứ hạng hiệu năng**, để lại (a)+(b) là căn cứ duy nhất còn đứng vững.
- Không chọn 0,30/0,35 dù Calmar nhỉnh hơn 0,01 — chênh đó nhỏ hơn sai số vintage, còn ở stress S3
  chúng xấu hơn 0,39–0,89pp. Đây là đánh đổi đúng chiều pre-reg (ưu tiên Calmar/MaxDD, và ở đây là
  rủi ro đuôi chưa quan sát được).

### 5.3 Còn treo (KHÔNG tự làm trong job này)

- **Không implement, không commit** — đây là cơ chế CAPIT **đang sống** (5 mã SAB/SIP/VNM/PVT/NCT
  giữ thật, verify DNSE 07-31). Bước cuối do user/Mike quyết.
- Khi wire: `capit_size` trong `trading_rules.json` + đường tính target trong `golive_recommend_v23.py`
  là 2 chỗ chạm; **thay đổi áp vào LIVE cần user duyệt** (CLAUDE.md Taylor).
- Nên chạy lại `bin/verify_finding.sh` cho chính 4 kết quả này trước khi user chốt (verdict CONFIRMED
  ngày 07-31 là cho job trước, chưa bao gồm PBO/ADV/stress ở đây).
