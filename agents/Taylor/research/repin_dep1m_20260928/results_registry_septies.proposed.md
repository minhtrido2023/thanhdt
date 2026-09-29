<!-- ĐỀ XUẤT — CHƯA GHI VÀO data/results_registry.md. Chờ Mike/user duyệt (§13 + ranh giới dispatch
     job Taylor_20260928_010454: "KHÔNG tự ghi results_registry.md canonical").

     BẢN NÀY THAY BẢN 1-SỐ ngày 2026-09-28 (job Taylor_20260927_170645) — user chốt 08:02 ICT
     2026-09-28 (Discord): "Nên áp dụng bản pin 2 con số cho dễ hình dung. Cần note rõ pin0%, và
     pin1M để có ngưỡng sàn và trần." Bản 1-số giữ ở `results_registry_septies.proposed.v1-1so.md.bak`
     + trong git (commit 4cd4c3ea) để tra được, KHÔNG dùng nữa.

     Cách áp: (A) append NGUYÊN KHỐI "## 2026-09-28 (septies) — ..." dưới đây vào CUỐI file registry;
              (B) áp PATCH §0 ở mục cuối file này vào khối "## ⭐ CONFIG TỐT NHẤT = V2.4".
     Tiêu đề dùng số (septies) — đã `grep -c "septies" data/results_registry.md` = 0. -->

## 2026-09-28 (septies) — ⭐ **R3 CÔNG BỐ THEO DẢI 2 SỐ: SÀN `pin0%` 23,37% … TRẦN `pin1M` 25,71%**, điểm thực tế `dep1m_21s` **25,24%** — job `Taylor_20260927_170645` + `Taylor_20260928_010454` ⚠️ **PAPER + REGISTRY, `trading_rules.json` KHÔNG ĐỔI, rail KHÔNG ĐỔI**

> **ĐÂY LÀ ĐỔI QUY ƯỚC ĐO, KHÔNG ĐỔI MÔ HÌNH.** Park giữ **0,30** y nguyên, universe/engine/lệnh y
> nguyên anchor R3. Thay đổi duy nhất: giả định **lãi tiền gửi trên tiền nhàn rỗi**.
> User chốt 2 mốc, cả hai đều là chỉ đạo còn hiệu lực:
> - 23:58 ICT 2026-09-27: *"Tiền mặt thì neo theo lãi suất huy động 1 tháng. Lấy căn cứ này làm số pin"*.
> - 08:02 ICT 2026-09-28: *"…chỉ trả carry cho phần tiền nằm im 21 phiên trở lên. Nhưng cũng chưa
>   chính xác thận trọng. Thực tế nếu rút trước hạn coi như hưởng lãi 0%. Nên áp dụng bản pin 2 con
>   số cho dễ hình dung. Cần note rõ pin0%, và pin1M để có ngưỡng sàn và trần."*
>
> Code: worktree `mike/agents/Taylor/wt-repin-dep1m-2809`, branch `research/repin-dep1m-2709`.
> Báo cáo đầy đủ: `mike/agents/Taylor/research/repin_dep1m_20260928/REPORT.md` (§1–10 = dải/pin1M,
> **§11 = chân `_21s`**).

### 0. 🚩 LUẬT TRÍCH SỐ (đọc trước mọi thứ khác)

**CẤM trích một con số mà không kèm quy ước tiền nhàn rỗi.** Ba quy ước dưới đây đo **cùng một chiến
lược**, chênh nhau tới **2,34pp CAGR** chỉ vì giả định lãi tiền mặt. **CẢ BA đều là số pin chính
thức; KHÔNG cái nào superseded cái nào** — chúng trả lời ba câu hỏi khác nhau:

| Nhãn | Quy ước | Vai trò | CAGR |
|---|---|---|---|
| **`pin0%`** | tiền nhàn rỗi hưởng **0%/năm** | **NGƯỠNG SÀN** — giả định tiền không sinh lời đồng nào | **23,37%** |
| **`dep1m_21s`** | lãi huy động 1M Big-4, **chỉ trả cho tiền đã nằm im ≥21 phiên** (rút trước hạn = 0%) | **ĐIỂM THỰC TẾ** trong dải | **25,24%** |
| **`pin1M`** | lãi huy động 1M Big-4 trả cho **MỌI** đồng nhàn rỗi | **NGƯỠNG TRẦN** — giả định mọi đồng nhàn rỗi hưởng đủ lãi kỳ hạn | **25,71%** |

Mọi số pin của V2.4 **trước 2026-09-28** (kể cả R3 28,86% mục (bis)/(ter) và 23,37% mục (sexies))
đo ở quy ước **`pin0%`** — đó là số ĐÚNG dưới quy ước cũ, **không phải số sai**, nên không gạch ngang.
So một số trước 09-28 với một số sau 09-28 mà không quy về cùng quy ước là **so sai**.

### 1. Bảng số đầy đủ — cả dải

| Đại lượng | **`pin0%` (SÀN)** | **`dep1m_21s` (ĐIỂM)** | `21s` LIFO *(độ nhạy)* | **`pin1M` (TRẦN)** |
|---|---|---|---|---|
| CAGR | **23,37%** | **25,24%** | 24,95% | **25,71%** |
| Sharpe(252) | 1,88 | 2,03 | 2,00 | 2,06 |
| MaxDD | −14,6% | −14,4% | −14,4% | −14,0% |
| Calmar | 1,60 | 1,75 | 1,73 | 1,83 |
| Final NAV | 684,52B | 825,92B | 802,45B | 864,86B |
| IS 2014-2019 | 20,00% | 21,39% | 21,53% | 22,47% |
| OOS 2020+ | 26,50% | 28,85% | 28,14% | 28,71% |
| **Bootstrap DD 5th-pct** | **−25,2%** ⬅ **NEO SIZING** | −23,9% | −24,2% | −23,6% |
| Bootstrap CAGR 5th-pct | 15,5% | 17,3% | 17,0% | 17,8% |
| Bootstrap Sharpe 5th | 1,26 | 1,42 | 1,39 | 1,45 |
| P(DD < −30%) | 1,1% | 0,4% | 0,7% | 0,5% |
| ledger md5 | `4707bcbeb7e801d49a4a851ffd91d5e7` | `d73f983d7d6a4b7028343be65c9ed7cf` | `62baf89e2f6bad3887e5c969957676ce` | `bcd0469f42c2f76937a6ebb10aae9b40` |
| self-check | 0 VND | 0 VND | 0 VND | 0 VND |
| carry mean thực áp | 0% | 3,501%/năm trên **24,57% NAV** | 3,501% trên 26,29% NAV | 3,501% trên **46,16% NAV** |

Cửa sổ 2014-01-02 → 2026-06-19 (12,46y), NAV 50B, park 0,30, `ETF_LIQ=custompitg`, universe
`universe_pit`. **OOS > IS ở mọi chiều trên cả 4 chân** ⇒ edge không rớt OOS ở bất kỳ quy ước nào.
Bootstrap: `bootstrap_nav.py` circular block **L=21, B=4000, seed=12345**.
**Sharpe(252) là cột ENGINE in ra** — 3 quy ước Sharpe cùng tồn tại (engine `sqrt(252)` · `leg_metrics`
theo thời gian lịch 249,28 obs/năm · bootstrap log-return); số của record là cột engine, vì đó đúng quy
ước sinh ra 1,88 của anchor. Đừng trộn.

### 2. 🔴 NEO SIZING DD = **−25,2%** (đầu THẬN TRỌNG = của `pin0%`), **KHÔNG** dùng −23,6%

**Lý do: sizing phải đứng ở cận xấu.** Ba lớp lập luận, không phải một:
1. **Nguyên tắc**: neo rủi ro lấy từ giả định BẤT LỢI nhất trong dải đang mở, không lấy trung điểm và
   tuyệt đối không lấy đầu tốt. Đầu tốt (−23,6%) đòi hỏi **mọi** đồng nhàn rỗi luôn hưởng đủ lãi kỳ
   hạn 1 tháng — điều không ai cam kết.
2. **Cơ chế**: DD hẹp hơn ở các chân có carry là **hệ quả số học** của việc cộng thêm một dòng lãi
   dương không rủi ro vào NAV — nó làm phân mẫu DD lớn hơn chứ **không** làm chiến lược bớt rủi ro
   một đồng nào. Lấy nó làm neo = tự nới hạn mức bằng một giả định kế toán.
3. **Đối chứng**: `pin0%` là quy ước mà **toàn bộ** lịch sử pin của V2.4 dùng, nên −25,2% là neo
   **liên tục so sánh được** với mọi mốc rủi ro đã đặt trước đó. Đổi neo sang −23,6% là âm thầm nới
   toàn bộ hệ hạn mức.

Anchor DD dài hạn của V2.4 vẫn là **~−29%** (bootstrap 5th-pct của R3 @50B, `context_taylor_mini`),
KHÔNG phải −18%/−14%. Mục này **không** thay con số đó.

### 3. Quy ước `dep1m` là gì (đọc trước khi trích `dep1m_21s` hoặc `pin1M`)

Lãi suất **huy động kỳ hạn 1 tháng, khách CÁ NHÂN, bình quân nhóm Big 4** (FiinPro-X, snapshot
2026-09-27). **HAI ĐOẠN, KHÁC BẢN CHẤT:**
- **2019-02 → 2026-09: SỐ THẬT** FiinPro công bố (92 tháng, chụp ngày 15). Trong cửa sổ: **89 tháng**.
- **trước 2019-02: DỰNG LẠI** = `SBV 12M-thấp + median(dep1m − SBV 12M-thấp)` = `sbv_low − 2,525pp`.
  Trong cửa sổ: **53 tháng** (+8 tháng khuyết `sbv_low` được forward-fill) — **53/150 tháng**.
  Route FiinPro trả **HTTP 500 cho mọi ngày ≤ 2018-12**; trial hết hạn 28/09/2026 ⇒ **không thể kéo
  thêm, vĩnh viễn.**

Chọn cầu bằng đo (n=90 overlap, đo lại độc lập): `dep1m − sbv_low` median **−2,525** / sd **0,883** /
corr **+0,619** ⇒ dùng được. `dep1m − liên NH 1M` median −0,240 / sd **2,472** / corr **−0,141** ⇒
**KHÔNG** bắc cầu được. PIT: mốc tháng T dùng từ đầu tháng T+1, không back-fill, **0 phiên bị trả 0%
vì thiếu chuỗi**. Băng bất định của cầu: p25/median/p75 cho CAGR 25,89 / 25,71 / 25,80 ⇒ dải
**0,181pp**, **dưới** sàn nhiễu W2b 0,46pp ⇒ số pin không nhạy với offset.

### 4. Ngữ nghĩa `_21s` — "rút trước hạn thì hưởng 0%"

Knob **ENGINE** (`simulate_holistic_nav.py`), không phải tier mới trong `idle_rate_proxy.py`: tuổi
tiền là **trạng thái của simulator**, còn module rate chỉ biết NGÀY. Hai trục mới, **cả hai vào tên
file** (§8): `IDLE_CARRY_MIN_AGE=21` + `IDLE_CARRY_AGE_ORDER=fifo|lifo` ⇒ tag `_idledep1m_21sfifo`.

- Chỉ trả lãi cho phần tiền **ĐÃ nằm im ≥21 phiên tính đến ngày đó**. Phiên 1–21 của một lô: **0 VND**;
  từ **phiên 22** mới cộng `r/252` cho lô đó.
- **KHÔNG TRUY LĨNH, bằng thiết kế.** Lô nằm 100 phiên không bao giờ được trả bù 21 phiên đầu — truy
  lĩnh đòi biết lô đó có bị tiêu không ⇒ **nhìn trước**. Lãi trả ra **không nhập vào gốc lô**, nó tự
  đếm tuổi từ 0.
- Tiền bị tiêu trước phiên 22 hưởng 0% **tự động**, không cần cơ chế thu hồi. `cash<0` ⇒ sổ lô rỗng.
- **FIFO** (tiêu lô CŨ trước ⇒ giết lô già ⇒ ÍT lãi) = chân **PIN** (luật định trước).
  **LIFO** = chân độ nhạy. Đo được: tiền đủ tuổi/tiền nhàn rỗi **51,3%** (FIFO) vs **57,0%** (LIFO).

**Tiền đủ tuổi thực tế** (ledger thật, đã đối soát độc lập bằng đồng nhất thức tiền của chính ledger,
khớp engine tới 0,01pp):

| Chân | Sổ | đủ tuổi / NAV_ref | median | **phiên trả 0% vì CHƯA ĐỦ TUỔI** |
|---|---|---|---|---|
| FIFO | BAL | 41,69% | 45,55% | **606 / 2.979 = 20,3%** |
| FIFO | LAG | 18,03% | **0,00%** | **1.676 / 2.919 = 57,4%** |
| LIFO | BAL | 44,41% | 51,33% | 390 / 3.015 = 12,9% |
| LIFO | LAG | 19,74% | 0,51% | 882 / 2.924 = 30,2% |

**Sổ LAG có median = 0,00%**: LAG quay vòng 25 phiên nên tiền của nó gần như không bao giờ nằm im nổi
21 phiên. Đó chính xác là phần over-pay mà quy ước `pin1M` đang trả và `_21s` cắt đi.
Tổng lãi đã trả: `pin1M` **51,58B** vs `21s FIFO` **28,07B** = **54,4%**.

### 5. Cổng bắt buộc đã QUA

| Cổng | Kết quả |
|---|---|
| `rp_ctrl` / `rp_ctrl2` (`IDLE_CARRY_TIER=off`) | md5 **`4707bcbe…`** = anchor R3, `cmp` **sạch, byte-identical** ✅ |
| `rp_pin2` — chân `pin1M` chạy lại trên code có sổ lô tuổi | md5 **`bcd0469f…`** = đúng số pin 27/09 ✅ |
| self-check mọi chân | BAL + LAG: cash-flow identity **0 VND**, final-NAV identity **0 VND** ✅ |
| borrow cost 2 chân `_21s` | **0 VND**, max gross 1,000 |
| selfcheck `idle_rate_proxy_selfcheck.py` | 102 assertion PASS, 15/15 mutation bị giết, 4 TZ + `env -u TZ` |
| selfcheck `idle_cash_age_selfcheck.py` (MỚI) | **50 assertion PASS, 11/11 mutation bị giết**, 4 TZ + `env -u TZ`; mutation 11/11 cũng bị giết dưới `TZ=UTC` |

`rp_pin2` là cổng **mạnh hơn** mức dispatch đòi: nó chứng minh thêm sổ lô tuổi không làm lệch chân
`pin1M` đã pin hôm trước, chứ không chỉ chân tắt.

Mutation của `_21s` (mỗi cái BỊ GIẾT): bỏ ngưỡng tuổi · **truy lĩnh** · đảo FIFO/LIFO · off-by-one
sớm/muộn 1 phiên · bỏ reconcile cuối phiên (tiền ra/vào bị net mất) · không tăng tuổi đầu phiên · lô
sinh ở tuổi 1 · lô mới chèn đầu sổ · trả lãi trên TỔNG cash · lãi gộp vào lô đã đủ tuổi.
**2 mutation ứng viên bị loại vì CHỨNG MINH ĐƯỢC LÀ TƯƠNG ĐƯƠNG** (ghi rõ trong file, không im lặng
bỏ) — xem REPORT §11.5.

### 6. ⚠️ Δ của `_21s` KHÔNG phải "hệ tốt lên" — và phần đường đi VƯỢT sàn nhiễu

| Chân | Δ TỔNG vs `pin0%` | Δ SỐ HỌC | **Δ ĐƯỜNG ĐI** | % số học |
|---|---|---|---|---|
| `pin1M` | +2,337pp | +2,042pp | +0,295pp *(dưới sàn 0,46)* | 87,4% |
| **`dep1m_21s` FIFO** | **+1,873pp** | **+1,116pp** | **+0,758pp** ⚠️ *(1,6× sàn 0,46)* | 59,6% |
| `21s` LIFO | +1,584pp | +1,191pp | +0,393pp *(dưới sàn)* | 75,2% |

1. **Chiều SỐ HỌC đúng và đơn điệu**: LIFO trả nhiều lãi hơn FIFO (+1,191 vs +1,116pp), khớp tiền đủ
   tuổi 57,0% vs 51,3%. Quy ước chạy đúng thiết kế.
2. **Thứ tự CAGR engine thì ĐẢO** (FIFO 25,24 > LIFO 24,95), hoàn toàn do phần đường đi. Khoảng cách
   FIFO/LIFO = **0,289pp < sàn nhiễu W2b 0,46pp** ⇒ **BẤT ĐỊNH QUY ƯỚC, không phải kết quả** — engine
   **không xếp hạng được** fifo vs lifo. Pin FIFO vì đó là **luật định trước** và là quy ước thận
   trọng về CARRY, **không** vì nó cho số cao hơn.
3. **Phần đường đi của chính chân PIN (0,758pp) VƯỢT sàn 0,46pp** — điều KHÔNG xảy ra ở `pin1M`
   (0,295pp). Ở 1,6σ thì **chưa có ý nghĩa thống kê**, nhưng nó không còn nằm gọn trong sàn ⇒
   **25,24% "bẩn" hơn 25,71%.** Hai cách đọc, phải công bố cả hai:

   | Cách đọc | CAGR | Vị trí trong dải [23,37 ; 25,71] |
   |---|---|---|
   | **SỐ HỌC** (chỉ hiệu ứng quy ước) | **24,49%** | **47,8%** |
   | ENGINE (số của record, tái lập từ ledger) | **25,24%** | 80,1% |

   Vị trí **47,8%** khớp gần khít **51,3%** tiền đủ tuổi/tiền nhàn rỗi (lệch 3,5pp) ⇒ cách đọc số học
   **nhất quán nội tại** với quy ước; 32,3pp còn lại của cách đọc engine là **đường đi**.

🚩 **Cảnh báo kế thừa (bắt buộc mang theo):** mọi so sánh **PHƯƠNG TIỆN** (park vs không park,
custom30V vs custom30 vs C6/C10) **VẪN** ở trạng thái W2b — engine không có sức phân giải. Mục này
**KHÔNG mở lại** câu hỏi đó, và chân `_21s` làm phần đường đi **TO HƠN** chứ không nhỏ hơn.

### 7. DSR / PBO
`pin1M`: DSR **1,0000** (N=4 / N_reg=120 / N_reg=200). PBO **0,5000** trên họ N=4 — **chạm** cờ đỏ
nhưng là giá trị **THOÁI HOÁ** (4 chân gần cộng tuyến, corr log-return ngày 0,98771–0,99998; logit λ
median 0,00, P(λ<0)=0,5 = tung xu); trên họ N=14 PBO = **0,1258**. Remedy của luật đã làm TRƯỚC khi
đo: offset **median** là luật định trước và chân median cho **CAGR THẤP NHẤT** trong 3 chân
(25,71 < 25,80 < 25,89) ⇒ không thể là IS-best-picking. Manifest ghim tường minh (không glob động):
`data/dsr_family_manifest_repin_dep1m_2026-09-28.json` (N=4) + `…_ext.json` (N=14).
⚠️ **Hai chân `_21s` CHƯA được đưa vào manifest DSR/PBO** — thêm chân là **tăng N**, nên việc nạp
chúng vào họ phải là một bước có ý thức, không làm lặng lẽ. Đề xuất: khi user chốt dải 2 số là công
bố chính thức thì mở rộng manifest lên N=6 và đo lại DSR/PBO.

### 8. Chân đối chứng KHÔNG CẦN BẮC CẦU (88 tháng SỐ THẬT, 0 dựng lại)
Cửa sổ **2019-03-01 → 2026-06-19** (7,30y): carry 0% → CAGR 22,86% (md5 `2988c7a3…`), `dep1m` →
**24,86%** (md5 `13d8e1de…`) ⇒ hiệu ứng carry trên **DỮ LIỆU THẬT một mình = +2,00pp** vs +2,34pp toàn
cửa sổ. Đoạn dựng lại **không bịa ra hiệu ứng**; chênh 0,34pp do 2014-2019 lãi suất cao hơn.
*(Chưa chạy chân `_21s` trên cửa sổ này — nếu cần thì là 2 chân nữa.)*

### 9. Lệnh tái lập
```bash
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/repin_dep1m_20260928/run_leg.sh
$R rp_ctrl2   … PARK_STATES=3:0.3 IDLE_CARRY_TIER=off                        # pin0%  (SÀN)
$R rp_pin2    … PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m                      # pin1M  (TRẦN)
$R rp_21sfifo … IDLE_CARRY_TIER=dep1m IDLE_CARRY_MIN_AGE=21 IDLE_CARRY_AGE_ORDER=fifo   # ĐIỂM (PIN)
$R rp_21slifo … IDLE_CARRY_TIER=dep1m IDLE_CARRY_MIN_AGE=21 IDLE_CARRY_AGE_ORDER=lifo   # độ nhạy
```
Đầy đủ env + selfcheck + bootstrap + overlay: REPORT §11.8. Runner `run_leg.sh` (phần thực thi
**byte-identical** với `run_leg.sh` của W2/Q2).

### 10. Giới hạn — phải mang theo khi trích bất kỳ số nào ở trên
1. **53/150 tháng của chuỗi lãi suất là SỐ DỰNG LẠI**, không phải số công bố (§3 và §8 giới hạn tác
   động, không xoá nó). Ảnh hưởng `pin1M` và `dep1m_21s`; **không** ảnh hưởng `pin0%`.
2. **Upstream ĐÃ CHẾT** 28/09/2026 (FiinPro-X trial). Mốc sau 2026-09 phải lấy NHNN trực tiếp.
3. Đoạn 2011-01→2025-10 của `sbv_low` (xương sống của cầu) **chưa có nguồn thứ hai xác minh** — di
   sản registry W1, và giờ NẶNG hơn vì nó chạy vào số pin.
4. **Δ đường đi 0,758pp của chân PIN vượt sàn nhiễu 0,46pp** (§6 điểm 3) — giới hạn NẶNG NHẤT của
   `dep1m_21s`, và là lý do phải công bố kèm cách đọc số học 24,49%.
5. **Ngưỡng 21 phiên là quy ước, không phải phép đo** (xấp xỉ "1 tháng giao dịch"; ngân hàng tính kỳ
   hạn theo ngày dương lịch, 30 ngày ≈ 20–22 phiên). Chưa đo độ nhạy theo ngưỡng 14/21/30.
6. **FIFO/LIFO không xếp hạng được** (0,289pp < 0,46pp); hai chân là hai **cận**, không phải hai ứng
   viên. Quy ước tiêu tiền thật không phải FIFO cũng chẳng phải LIFO.
7. Đây là **lãi tiền gửi THỊ TRƯỜNG**, KHÔNG phải carry egg DNSE thật (8,543%/năm spot 09/2026 — cao
   hơn cả đầu mút cao NHNN ~1pp, là spread SẢN PHẨM, DNSE không cam kết) ⇒ cả dải cố ý đứng ở đầu
   **THẬN TRỌNG**.
8. **KHÔNG kết luận gì về xếp hạng PHƯƠNG TIỆN park** (§6 cảnh báo kế thừa).
9. Quy đổi thực tế theo CLAUDE.md (CAGR thật ≈ backtest − 1,5%): `pin0%` → ~**21,9%** ·
   `dep1m_21s` → ~**23,7%** (đọc số học ~23,0%) · `pin1M` → ~**24,2%**.

### 11. ⚠️ HỆ QUẢ PHẢI XỬ — `CLAUDE.md` đang nói NGƯỢC (cần user/Mike quyết, Taylor KHÔNG tự sửa)
`WorkingClaude/CLAUDE.md` § Backtest ghi quy ước chung: *"lãi tiền gửi nhàn rỗi **0%/năm**"*, và
`backtest_fundamental_rating.py` / `simulate_holistic_nav.py` **trích thẳng "per CLAUDE.md"**.
Định dạng DẢI 2 SỐ **làm nhẹ** xung đột này (vì `pin0%` = quy ước CLAUDE.md hiện hành vẫn là một đầu
chính thức của dải) nhưng **không xoá** nó. Hai lựa chọn:
- **(A)** cập nhật CLAUDE.md § Backtest: khai rõ **ba** quy ước + **quy tắc §0 "cấm trích số không
  kèm quy ước"** + nói rõ mặc định của engine vẫn là 0%/năm (`IDLE_CARRY_TIER=off`, byte-identical).
  Đây là lựa chọn Taylor **khuyến nghị**: dải 2 số chỉ hữu dụng nếu luật trích số nằm ở file
  auto-load, không nằm trong registry mà ít ai mở.
- **(B)** giữ CLAUDE.md nguyên văn và coi (septies) là số song song — khi đó PATCH §0 dưới đây phải
  bỏ dòng `⭐⭐⭐` và chỉ thêm con trỏ.
**Chưa chọn thì đừng áp PATCH §0.**

---

## PATCH §0 — khối "## ⭐ CONFIG TỐT NHẤT = V2.4" (chỉ áp khi user chọn (A) ở §11)

Chèn NGAY TRÊN dòng `> ⭐⭐ **SỐ R3 HIỆN HÀNH (từ 2026-09-27 mục (sexies))...`:

```markdown
> ⭐⭐⭐ **SỐ R3 HIỆN HÀNH CÔNG BỐ THEO DẢI 2 SỐ (từ 2026-09-28 mục (septies)) — CẤM trích 1 số mà
> không kèm quy ước tiền nhàn rỗi:**
> - **SÀN `pin0%`** (tiền nhàn rỗi 0%/năm — quy ước của MỌI số pin trước 09-28): **CAGR 23,37%** /
>   Sharpe 1,88 / MaxDD −14,6% / Calmar 1,60 / NAV 684,52B / md5 `4707bcbe…`.
> - **ĐIỂM `dep1m_21s`** (lãi huy động 1M Big-4, chỉ trả cho tiền nằm im ≥21 phiên — "rút trước hạn
>   hưởng 0%", FIFO): **CAGR 25,24%** / Sharpe 2,03 / MaxDD −14,4% / Calmar 1,75 / NAV 825,92B /
>   md5 `d73f983d…`. ⚠️ Δ đường đi 0,758pp **vượt** sàn nhiễu 0,46pp ⇒ cách đọc SỐ HỌC = **24,49%**.
> - **TRẦN `pin1M`** (lãi huy động 1M Big-4 trả cho MỌI đồng nhàn rỗi): **CAGR 25,71%** / Sharpe 2,06
>   / MaxDD −14,0% / Calmar 1,83 / NAV 864,86B / md5 `bcd0469f…`.
>
> 🔴 **NEO SIZING DD = −25,2%** (bootstrap 5th-pct của **`pin0%`** = đầu THẬN TRỌNG). **KHÔNG** dùng
> −23,9%/−23,6%: DD hẹp hơn ở chân có carry là hệ quả SỐ HỌC của một dòng lãi không rủi ro, không
> phải chiến lược bớt rủi ro. Anchor DD dài hạn V2.4 vẫn **~−29%**.
>
> **ĐỔI QUY ƯỚC ĐO, KHÔNG ĐỔI MÔ HÌNH** — park vẫn 0,30, rail không đụng, universe/engine y nguyên;
> engine mặc định vẫn 0%/năm (`IDLE_CARRY_TIER=off`, byte-identical). **KHÔNG đọc là "hệ tốt lên",
> KHÔNG dùng để xếp hạng phương tiện park** (vẫn W2b: engine không phân giải). Mục:
> **"2026-09-28 (septies) — ⭐ R3 CÔNG BỐ THEO DẢI 2 SỐ"** cuối file.
```

Và sửa dòng `> ⭐⭐ **SỐ R3 HIỆN HÀNH (từ 2026-09-27 mục (sexies))` thành
`> ⭐ **SỐ R3 mục (sexies) 2026-09-27 — nay là ĐẦU SÀN `pin0%` của dải (septies)**` (giữ toàn bộ nội
dung; đây là số ĐÚNG dưới quy ước `pin0%`, **không gạch ngang**).
