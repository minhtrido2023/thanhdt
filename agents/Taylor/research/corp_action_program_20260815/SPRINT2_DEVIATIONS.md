# SPRINT 2 — DEVIATIONS từ pre-registration

> Prereg đã commit **`2a9b951a`** TRƯỚC khi tính bất kỳ outcome nào. File này ghi mọi thứ tôi làm
> **khác** với nó, kèm lý do và cái giá phải trả. Prereg không bị sửa một chữ nào sau khi chạy.
> Job `Taylor_20260815_121850`, 2026-08-15.

**Tóm tắt:** 5 deviation. Không cái nào đổi outcome primary hay tiêu chí thành công/thất bại.
D3 là cái quan trọng nhất — nó SINH RA từ một robustness check của chính prereg trả về kết quả
mà prereg không lường trước.

---

## D1 — Benchmark EW: loại 2 quan sát lợi suất bất khả thi

**Prereg nói gì:** §4.3 định nghĩa `EW_ret(d)` là trung bình lợi suất ngày của thành viên
`universe_pit`. Không nói xử lý dữ liệu lỗi thế nào.

**Làm gì khác:** dùng cột `ew_ret` (đã loại `|ret| > 50%`) thay vì `ew_ret_raw`.

**Vì sao:** trên chuỗi `Close` **đã hồi tố**, một lợi suất ngày > 50% không phải biến động thị
trường mà là lỗi dữ liệu (biên độ sàn VN cao nhất là UPCOM ±15%). Đo được: **2 quan sát trên
3.396 phiên**, tức 0,06‰.

**Giá phải trả:** gần bằng 0. Cả hai chuỗi được giữ trong `out2/ew_universe.csv`
(`ew_ret` và `ew_ret_raw`) để ai cũng dựng lại được bản không lọc. Đây là **vệ sinh dữ liệu**,
không phải nút vặn — không có tham số nào để chọn.

---

## D2 — Hồi quy: winsorise BIẾN KIỂM SOÁT ở 1/99 phân vị

**Prereg nói gì:** §6.3 liệt kê biến kiểm soát, không nói winsorise.

**Làm gì khác:** cắt đuôi 1%/99% cho 7 biến kiểm soát (`y_gross`, `log_adv`, `mom_6m`,
`rvol_60`, `log_mcap`, `ey`, `pb_m1`).

**Vì sao:** vài giá trị `PE`/`PB` cực đoan chi phối leverage của OLS.

**Giá phải trả + ranh giới đã giữ:** **KHÔNG winsorise biến kết quả** `BHAR_20` — làm thế sẽ trực
tiếp bóp hiệu ứng đang đo. Hiệu ứng đuôi của biến kết quả được xử lý minh bạch ở R3 (winsorised
−1,056% · trimmed −1,136% · thô −1,065% ⇒ kết luận không do ngoại lai). Hồi quy là **kiểm chứng
chéo**, không phải nguồn của kết luận primary.

---

## D3 — ⭐ Thêm baseline XA (R7) + estimator GHÉP CẶP + chẩn đoán một phiên

**Đây là deviation quan trọng nhất. Nó không phải tùy hứng — nó là phản ứng bắt buộc với một
robustness check của chính prereg trả về kết quả bác bỏ giả định ngầm của prereg.**

**Prereg nói gì:** §7 R5 đặt placebo ở `ex − 40` phiên; §9(f) coi placebo là cổng: "placebo
KHÔNG cho hiệu ứng cùng cỡ". Ngầm định: **null của pipeline là 0**.

**Cái gì xảy ra:** R5 trả về **+1,180%** [+0,684; +1,693], p < 0,0001. **Null của pipeline KHÔNG
phải 0** cho population này. Nhưng cửa sổ R5 (−40..−20 phiên) nằm NGAY TRONG giai đoạn chạy giá
trước ex-date, nên nó **không tách được** hai cách giải thích:
- (a) "mã trả cổ tức đơn giản là mã tốt hơn trung bình universe" — một phần bù chất lượng; hay
- (b) "có lực mua chạy trước ngày GDKHQ".

**Làm gì thêm (4 thứ, tất cả đều là trial mới):**

| thêm | định nghĩa | trả lời câu gì |
|---|---|---|
| **R7** baseline xa | cùng thống kê 20 phiên, neo ở `ex − 250` → `ex − 230` (≈ 1 NĂM trước, ngoài mọi cửa sổ sự kiện) | tách (a) khỏi (b) |
| **paired** | `BHAR_20 − FARBASE_20`, **ghép cặp cùng một mã, cùng pipeline** | ước lượng hiệu ứng sự kiện sau khi trừ phần bù chất lượng |
| **AAR_0_1** | lợi suất bất thường của ĐÚNG một phiên đầu sau ex-date | **máy dò hiện vật**: nếu vendor đặt bước điều chỉnh nhầm sang k=+1 thì toàn bộ cổ tức sẽ nằm gọn ở đúng lợi suất này |
| **phân rã đoạn** | lợi suất thô 0→1, 1→2, 2→3, 3→5, 5→10, 10→20 | phân biệt "cú nhảy một phiên" (hiện vật) với "suy giảm dần" (kinh tế) |

**Kết quả:** R7 = **+0,637%** [+0,132; +1,136] ⇒ phần bù chất lượng CÓ THẬT nhưng chỉ bằng ~½
mức R5 ⇒ R5 = phần bù chất lượng **cộng** một phần chạy giá trước ex. AAR_0_1 = **−0,446%**,
trong khi tỉ suất gộp trung bình của P-CORE là **4,325%** — nếu là hiện vật đặt nhầm bước điều
chỉnh thì con số này phải ≈ −4,3%. **Giả thuyết hiện vật BỊ BÁC BỎ bằng số, không bằng lập luận.**

**Giá phải trả — nói thẳng:**
1. **+5 trial** ngoài 20 đã khai. Tổng thực thi **27**. Holm được tính trên **toàn bộ 27**, nên
   phần thêm tự trả chi phí bội kiểm của nó.
2. **R7 tự nó KHÔNG sống sót Holm** (p thô 0,0168 → Holm **0,118**). ⇒ phép hiệu chỉnh baseline
   là **bất định**. Vì vậy báo cáo trình **CẢ HAI** con số (thô −1,065% và ghép cặp −1,609%) và
   **primary vẫn là bản THÔ theo prereg**, không phải bản ghép cặp đẹp hơn.
3. Estimator ghép cặp nhiễu hơn ở lát mỏng: bin Y1 ra −2,839% chỉ vì baseline xa của riêng Y1 cao
   bất thường (+2,26%), trong khi Y1 **thô** không có ý nghĩa thống kê (p = 0,182). Đã ghi rõ
   trong báo cáo và trên chính hình 3.

**Vì sao vẫn làm:** bỏ qua một placebo dương có ý nghĩa rồi vẫn báo cáo con số thô như thể null
là 0 thì mới là sai. Prereg đặt R5 vào đúng để bắt chuyện này — làm ngơ kết quả của nó là vô
hiệu hoá chính prereg.

---

## D4 — Module A chạy thêm lát P-CORE

**Prereg nói gì:** §4.2 chạy Module A trên P-WIDE.

**Làm gì khác:** thêm đúng bộ thống kê đó trên P-CORE (thành viên `universe_pit`). **+1 trial.**

**Vì sao:** đường CAAR cho thấy hiệu ứng ex-day trên tập ĐẦU TƯ ĐƯỢC nhỏ hơn hẳn P-WIDE
(AR_ex +0,348% vs +1,008%; drop ratio trung vị 0,898 vs 0,833). Trích con số P-WIDE mà không kèm
điều kiện đó sẽ khiến người đọc tưởng mức under-adjustment áp dụng cho mã họ thật sự mua được.
Một con số mô tả gây hiểu nhầm về thứ có thể mua được là **lỗi**, không phải sự thận trọng.

---

## D5 — Selfcheck T27 viết SAI, đã sửa TEST chứ không sửa estimator

**Chuyện gì:** T27 bản đầu assert "CI block-bootstrap rộng hơn CI theo sự kiện", chạy trên dữ liệu
tổng hợp **không có tương quan trong block**. **Nó FAIL.**

**Chẩn đoán:** *test sai*, không phải estimator sai. Khi không có cú sốc chung theo block thì
cluster bootstrap **không có lý do gì** phải rộng hơn.

**Sửa:** T27 giờ tạo cú sốc chung theo block rồi mới assert (đo được **7,07×**). Thêm **T27b**
assert trên **dữ liệu thật**: CI block/CI sự kiện = **1,46×** ⇒ cụm theo tháng là CÓ THẬT và
CI báo cáo là bản **thận trọng**.

**Bài học giữ lại trong code** (comment tại chỗ): giả thuyết đầu tiên khi một selfcheck fail là
"tôi viết sai test", không phải "code sai" — và cách phân biệt là hỏi *bất biến này có thật sự
đúng dưới giả định tôi vừa dựng trong test không*.

---

## D6 — ⭐ **SỬA LỖI ENTITLEMENT** trong cost screen + outcome hold-through mới (post-hoc)

> Job `Taylor_20260815_125247`, sau khi bản đầu tiên đã commit (`7ae396c9`). Đây là **sửa lỗi**,
> không phải mở rộng nghiên cứu. Prereg `SPRINT2_PREREG.md` **KHÔNG bị sửa** — nó đã khoá và lỗi
> này nằm ngay trong chính prereg (§8).

### Lỗi

Outcome primary `BHAR_20` được dựng là `raw_h = c_h/c_0 − 1`, tức **vào lệnh ở giá đóng cửa T0 =
chính ngày GDKHQ**. Người mua ở giá đó mua cổ phiếu **đã ex** ⇒ **không nhận cổ tức của sự kiện
đó** ⇒ **không nợ thuế TNCN 5%** trên nó.

Nhưng prereg §8 và code lại tính:

```
BHAR_net = BHAR_20 − 0,05·y_gross − 0,002 − 0,003        ← SAI entitlement
```

Nó trừ thuế của một khoản tiền mà người nắm giữ không được nhận. Kéo theo hai lỗi nữa trong báo cáo:

1. Câu "mua ngay trước GDKHQ có chi phí ≈ 0,50 × tỉ suất, **cộng** thuế 5%, **cộng** cú rơi cơ
   học" — `BHAR_20` **không đo** giao dịch mua-trước-ex. Cộng thêm số hạng vào nó là **số học trên
   một outcome khác**, không phải kết quả đo.
2. Selfcheck **T36** khẳng định cost screen *phải* trừ `0,05·y_gross` ⇒ test đang **bảo vệ chính
   lỗi đó**. Xanh 38/38 vì vậy không có giá trị chứng minh ở điểm này.

### Sửa — C1: cost screen post-ex (số ĐỔI)

```
BHAR_net = BHAR_20 − 0,002 (TC 2 chiều) − 0,003 (spread/slippage)
```

| | cũ (SAI) | mới | chênh |
|---|---:|---:|---:|
| mean | −1,781% | **−1,565%** | **+0,216pp** |
| CI95 lo | −2,317% | −2,099% | +0,218 |
| CI95 hi | −1,250% | −1,033% | +0,217 |
| trung vị | −2,543% | −2,342% | +0,201 |
| tỉ lệ dương | 37,5% | 38,7% | +1,2pp |

Chênh = `0,05 × tỉ suất gộp trung bình` = 0,05 × 4,325% = 0,216pp. Khớp chính xác.

### Sửa — C2: hold-through T−1 → T+20 thành **outcome MỚI đo riêng**, không phải suy diễn

Nếu vẫn muốn phát biểu về việc mua trước ex thì phải đo nó, trên **total return đúng
entitlement**: mua giá thô `P₋₁`, **nhận** cổ tức ròng thuế 5%, bán giá thô `P₊₂₀`.
Trong hệ giá điều chỉnh, với `f = 1 − y` và không có sự kiện nhiễm trong cửa sổ (đảm bảo bởi
`clean(·, 21)`): `P₊₂₀/P₋₁ = (C₊₂₀/C₋₁)·f` và `D/P₋₁ = y`.

```
HOLDTHRU_20 = (C₊₂₀/C₋₁)·(1−y) + 0,95·y − 1 − EW(d₋₁, d₊₂₀)
```

| | mean | trung vị | CI95 | p thô | Holm (họ 33) |
|---|---:|---:|---|---:|---:|
| gộp | **−0,907%** | −1,576% | [−1,464; −0,356] | 0,0012 | **0,017** |
| sau phí (−50bps) | **−1,407%** | −2,076% | [−1,964; −0,856] | 0,0000 | **0,000** |

**Kết quả này bác bỏ narrative cũ, không xác nhận nó.** Số học sai cũ cho ra âm hơn nhiều
(−1,281% nếu chỉ cộng thuế; còn âm hơn nếu cộng cả cú rơi cơ học). Đo thật: **−0,907%**, tức
**ít âm hơn cả `BHAR_20` (−1,065%)**. Cơ chế đã có sẵn trong chính §3: giá rơi **ít hơn** cổ tức
(drop ratio trung vị 0,90 P-CORE) ⇒ người giữ xuyên ex **được hưởng** phần dưới-điều-chỉnh, người
mua sau ex thì không. Ghi rõ: **post-hoc, KHÔNG pre-register**, +2 trial, chịu Holm riêng.

### Sửa — C3: selfcheck

| test | trước | sau |
|---|---|---|
| **T36** | khẳng định công thức **CÓ** `0.05*y_gross` (bảo vệ lỗi) | neo `entry_anchor = ex_date_close_T0`, `dividend_entitlement = False`, chỉ TC + slippage |
| **T36b** | — | chống tái phát: công thức post-ex **không chứa** `y_gross` / `0.05` / `tax` |
| **T36c** | — | bất biến số: `net − BHAR_20 == −0,005` đúng bằng phí, không số hạng ẩn |
| **T36d** | — | mọi claim hold-through/pre-ex phải có outcome riêng, `entry_anchor = close_T_minus_1` và `dividend_entitlement = True` |
| **T36e** | — | hold-through **khác** phép số học `BHAR_20 − thuế` (nếu trùng nghĩa là suy diễn chứ không đo) |
| **T36f** | — | outcome post-hoc phải xuất hiện trong bảng trial + Holm |
| **T36g** | — | prohibition ở TẦNG MÃ NGUỒN: dòng dựng `net` không được chứa `y_gross` |
| **T36h** | — | prohibition ở TẦNG BÁO CÁO: không dòng nào còn tính thuế cổ tức cho người mua sau ex |

38 → **45 test, 45 PASS**. (D7 dưới đây nâng tiếp lên **50**.)

### Cái KHÔNG đổi

Mọi outcome thô confirmatory giữ nguyên **từng chữ số**: `BHAR_5/10/20/60`, bin theo tỉ suất, hồi
quy, IS/OOS, LOO, R1-R7, ghép cặp, phân rã đoạn, Module A. Lỗi nằm **chỉ** ở lớp trừ chi phí và ở
lớp diễn giải. Commit prereg `2a9b951a` và commit kết quả `7ae396c9` giữ nguyên trong lịch sử.

---

## Điều kiện của prereg đã được GIẢI QUYẾT (không phải deviation, ghi để truy được)

| prereg | điều kiện | kết quả đo | hành động |
|---|---|---|---|
| §6.3 | "coverage `OShares` PIT < 80% ⇒ bỏ biến size" | **96,05%** | **GIỮ** `log_mcap` trong hồi quy |
| §4.1 | "(i) < 80% khớp ±1% ⇒ fail closed, Module A hạ descriptive-only" | **97,46%** khớp ±1% (92,04% trong ±0,2%) | Module A **chạy đầy đủ** — nhưng vẫn tuyên bố DESCRIPTIVE ONLY vì lý do KINH TẾ (giá tham chiếu do sở ấn định), không phải vì dữ liệu |
| §2.3 | "đo và công bố tỉ lệ `universe_pit.backfilled`" | **99,99%** | công bố ở §6 báo cáo như một hạn chế thật |
| §3 X3 | "báo riêng số bị loại vì tỉ suất > 50%" | **1** sự kiện | đã ghi trong funnel |

---

## Bảng trial cuối cùng

| | |
|---|---:|
| Khai báo trước trong prereg | 20 |
| Thực thi thật | **29** |
| Thêm do D3 | 5 (`R7`, `paired`, `paired_IS`, `paired_OOS`, `aar01`) |
| Thêm do D4 | 1 (Module A P-CORE) |
| Chênh còn lại | 1 (`R3_trim` — prereg gộp R3 thành 1 lát, thực thi tách phần trimmed thành test riêng) |
| Thêm do **D6** | **2** (`holdthru`, `holdthru_net` — outcome hold-through post-hoc) |
| Thêm do **D7** | **4** (`holdthru_IS`, `holdthru_OOS`, `holdthru_net_IS`, `holdthru_net_OOS`) |
| **Tổng thực thi** | **33** |

Holm tính trên **cả 33**. Kết luận primary (`BHAR_20`) có Holm-adjusted p = **0,000** nên không
phụ thuộc vào việc đếm 20, 27, 29 hay 33. Sáu trial của D6+D7 thì **có** phụ thuộc: `holdthru`
gộp có Holm-p = **0,017** (từ 0,013 khi họ còn 29) và `holdthru_IS` có Holm-p = **0,547** — đọc
như outcome post-hoc biên, không phải kết quả đã pre-register.

Không kết luận nào ĐỔI VERDICT vì +4 trial: `paired_OOS` 0,0378 → 0,0462 (vẫn qua 0,05), `R7`
0,118 → 0,134 (vẫn trượt), `BHAR_60` 0,283 → 0,330 (vẫn trượt). Danh sách đầy đủ Holm cũ/mới nằm
trong `out2/results.json`.

---

## D7 — hold-through post-hoc: thêm IS/OOS + per-year leave-one-out

**Job `Taylor_20260815_130912`. Đóng đúng một gap của vòng quant-skeptic** (verdict vòng trước:
CONFIRMED/high, gap còn lại: outcome post-hoc `HOLDTHRU_20` chỉ có số **full-sample**, thiếu
IS/OOS và leave-one-out, và §7 báo cáo **không nêu** khoảng trống đó).

**Làm gì:** chạy đúng estimator đang dùng (block bootstrap theo tháng-ex, 5.000 lần), đúng cửa sổ
(T−1 → T+20), đúng entitlement (nhận cổ tức ròng thuế 5%), đúng mốc cắt `IS_END = 2019-12-31` của
`BHAR_20`, trên cả hai bản gộp và sau phí. Thêm per-year leave-one-out cho cả hai.
`_loo()` được tách thành hàm dùng chung và `BHAR_20` LOO cũng chuyển sang gọi nó — cùng một định
nghĩa cho cả hai, thêm ba trường (`largest_carrier_year/_share`,
`sign_flips_when_any_single_year_excluded`).

**Kết quả:**

| | n | mean | CI95 | p thô | Holm (họ 33) |
|---|---:|---:|---|---:|---:|
| gộp · IS 2014–2019 | 1.180 | **−0,414%** | **[−1,096; +0,293]** | 0,2518 | 0,547 ✗ |
| gộp · OOS 2020+ | 1.439 | **−1,312%** | [−2,145; −0,506] | 0,0012 | **0,017** |
| sau phí · IS | 1.180 | −0,914% | [−1,596; −0,207] | 0,0122 | 0,110 ✗ |
| sau phí · OOS | 1.439 | −1,812% | [−2,645; −1,006] | 0,0000 | **0,000** |

LOO gộp: **0/13** năm làm đổi dấu; 4/13 năm dương (2016 +0,33%, 2018 +1,32%, 2022 +0,54%, 2023
−0,05%); bốn năm gánh **99,9%** hiệu ứng — 2020 (31,9%), 2021 (24,1%), 2025 (22,4%), 2017 (21,5%).
Bỏ riêng 2020: −0,907% → **−0,672%**.

**Đọc — và hạ narrative ngay theo yêu cầu:** **DẤU bền, ĐỘ LỚN thì KHÔNG.** Nửa IS gộp không phân
biệt được với 0; toàn bộ ý nghĩa thống kê của bản gộp nằm ở OOS 2020+ (mức âm gấp 3,2×). Dòng
"sau phí · IS" có p = 0,012 nhưng ý nghĩa đó đến từ **hằng số** −0,50pp áp lên mọi sự kiện, không
từ thêm bằng chứng nào — cấm trích nó như xác nhận độc lập. ⇒ báo cáo §6.2/§6.3/§7(13) nay bắt
buộc trích kèm khoảng IS/OOS, không được trích −0,907% như hằng số chi phí.

**Nhãn KHÔNG đổi: POST-HOC.** Độ bền đo được ở đây là *robustness của một outcome hậu nghiệm*,
không nâng nó thành confirmatory, không biến nó thành alpha, và `SPRINT2_PREREG.md` **không sửa**.

### Selfcheck thêm

| test | nội dung |
|---|---|
| **T36i** | tồn tại khối `stability` với đủ 4 test IS/OOS + 2 LOO; `n_IS + n_OOS == n` full-sample |
| **T36j** | 4 tag IS/OOS có mặt trong `raw_p` **và** trong `holm_adjusted_p` (chịu đúng chi phí bội kiểm) |
| **T36k** | LOO có ≥ 10 năm, mỗi năm đủ trường, và `sign_flips…` nhất quán với chính bảng `years` |
| **T36l** | bất biến hằng số phí: `mean(net_IS) − mean(gross_IS) == −0,005` (và OOS cũng vậy) |
| **T36m** | **báo cáo khớp results**: mọi số IS/OOS in trong §6.2 khớp `results.json` tới 0,001pp; §7 phải có mục nêu gap |

45 → **50 test, 50 PASS**.
