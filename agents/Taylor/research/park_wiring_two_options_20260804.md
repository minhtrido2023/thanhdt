# Các phương án wiring L1/L2 để user chọn — Conservative · Aggressive-lite · Aggressive

Job `Taylor_20260804_012953`, **bổ sung/sửa vòng 2 sau quant-skeptic** (job `Taylor_20260804_022423`)
· 2026-08-04 · Taylor
Tiếp nối `research/park_unpark_live_wiring_20260803.md` (§E, bảng 2×2).
**Không sửa file production nào** — `git status` trên `golive_recommend_v23.py`,
`simulate_holistic_nav.py`, `pt_v23_audit_2014.py`, `trading_bot/`, `data/trading_rules.json` = rỗng.
Mọi thay đổi nằm trong `mike/agents/Taylor/exp_park_jit_20260803/`.

> ### ⚠️ Bản này SỬA bản đầu tiên — quant-skeptic bắt đúng 2 lỗi (CONFIRMED, confidence medium, 02:16)
>
> 1. **Menu thiếu một hàng đáng lẽ phải có.** Bản đầu chỉ trình 3 hàng (Conservative / F2 / Live)
>    và đẩy **F1 (target 0,80)** xuống một dòng trong bảng dose-response. Nhưng F1 **thắng F2 trên
>    Sharpe, MaxDD, Calmar VÀ rủi ro đuôi** — F2 chỉ hơn ở CAGR thô (+0,66pp). Giấu F1 khỏi bảng
>    quyết định là **thu hẹp lựa chọn của user một cách không chính đáng**. → §0 giờ có **4 hàng**.
> 2. **Câu chữ "đỉnh của plateau (0,85)" ở §3.3 KHÔNG khớp chính số liệu trong báo cáo.**
>    Theo Calmar, đỉnh thật là **F1 = 1,63**, không phải F2 = 1,62. → §3.3 đã viết lại: lý do chọn
>    F2 làm "Aggressive" được nói **tường minh** (xếp hạng theo CAGR, biện minh bằng PBO), không
>    còn núp sau chữ "đỉnh plateau" sai.
>
> Việc thứ 3: **capacity đã được ĐO LẠI trực tiếp ở mức `park_mv` thật của F1/F2** (§3.7), thay cho
> phép ngoại suy từ mức 0,70 mà quant-skeptic ghi là chưa verify.

---

## 0. BẢNG QUYẾT ĐỊNH — 4 hàng user chọn

Cùng một harness, cùng một cửa sổ, cùng một nguồn dữ liệu (chi tiết §1).

| | **Conservative** | **Aggressive-lite** | **Aggressive** | **Live hôm nay** |
|---|---|---|---|---|
| Chân ablation | **A** (= số pin R3) | **F1** (mới) | **F2** (mới) | **E** |
| Wire gì | L1 + L2 đầy đủ | L1 + L2 đầy đủ | L1 + L2 đầy đủ | không có đường bán PARK |
| Target park NEUTRAL | **0,70** (đã pin) | **0,80** (mới) | **0,85** (mới) | — (không có trần) |
| Ngưỡng kích hoạt trim | 0,005 × pool | 0,005 (không đổi) | 0,005 (không đổi) | — |
| **CAGR** | 28,86% | 29,85% | **30,51%** | **33,16%** |
| **Sharpe(252)** | **1,90** | 1,87 | 1,86 | 1,48 |
| **MaxDD** | **−17,8%** | −18,3% | −18,9% | **−33,7%** |
| **Calmar** | 1,62 | **1,63** ← cao nhất | 1,62 | 0,98 |
| Final NAV (50B start) | 1.178,0B | 1.295,7B | 1.380,2B | 1.773,3B |
| IS 2014-19 / OOS 2020+ | 27,09 / 30,48 | 27,97 / 31,57 | 28,37 / 32,48 | 26,28 / 39,63 |
| **DSR** (N=7 hẹp → N=200 rộng) | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| **PBO (họ 7 cấu hình)** | 0,080 (metric CAGR) · 0,411 (metric Sharpe) — **thống kê CỦA CẢ HỌ, không xếp hạng từng cấu hình** |||
| **LOO Δ vs Conservative** | — | +1,01pp (dải **+0,71…+1,25**, 0 ô âm) | +1,63pp (dải +1,29…+1,94, 0 ô âm) | — |
| **Tham số mới** | **0** | **1** (0,70 → 0,80) | **1** (0,70 → 0,85) | — (đang chạy ngoài spec) |
| **Audit trail** | ✅ đầy đủ, quant-skeptic CONFIRMED vòng 2×2 | ⚠️ cấu hình MỚI | ⚠️ cấu hình MỚI | — |
| **Cổng phải mở** | không (đưa live về đúng spec đã duyệt) | **`risk_dial_override`** | **`risk_dial_override`** | — |

**Số đáng chú ý nhất không nằm trong bảng trên** — tỷ trọng cổ phiếu TRUNG BÌNH thực tế
(đo trực tiếp từ sổ mô phỏng, `exposure_check.py`), tức thứ user thật sự đang chọn:

| | Conservative | Aggressive-lite (F1) | Aggressive (F2) | Live (E) |
|---|---|---|---|---|
| Cổ phiếu TB / NAV | **60,4%** | 63,1% (**+2,7pp**) | 64,7% (**+4,3pp**) | **82,7% (+22,3pp)** |
| Trong đó PARK | 24,8% | 28,6% | 30,4% | 75,1% |
| PARK p95 (đỉnh thực tế) | 64,2% | 73,5% | 78,4% | — |
| Tiền mặt TB | 32,2% | 29,0% | 27,2% | **11,7%** |
| Cổ phiếu TB **năm 2022** (năm sập) | 28,0% | 24,4% | 25,5% | **84,0%** |
| Lợi nhuận 2022 | −8,0% | **−4,3%** ← ít lỗ nhất | −5,4% | **−21,4%** |

> Aggressive-lite nâng beta cổ phiếu **+2,7pp**, Aggressive **+4,3pp** so với Conservative.
> Live đang chạy **+22,3pp** — gấp 5–8 lần khoảng cách giữa các phương án user đang được mời chọn.

**Rủi ro đuôi (stationary bootstrap Politis-Romano, mean L=21, B=4000, seed=12345):**

| | CAGR p5 | CAGR p50 | MaxDD p5 | **P(MaxDD < −30%)** |
|---|---|---|---|---|
| Conservative (0,70) | 19,6% | 29,1% | **−27,3%** | **2,2%** |
| **Aggressive-lite (F1, 0,80)** | 20,5% | 30,1% | −28,2% | **2,8%** |
| Aggressive (F2, 0,85) | 20,8% | 30,8% | −28,7% | **3,4%** |
| Live (E) | 19,8% | 33,6% | −47,5% | **63,7%** |

### 0.1 Đọc bảng này thế nào — F1 là hàng "cân bằng"

Nếu chỉ nhìn CAGR thì thứ tự là hiển nhiên (0,70 < 0,80 < 0,85 < live). Nhưng ngoài CAGR ra,
**F1 thắng F2 ở 6/7 chỉ tiêu còn lại** — F2 chỉ giữ được đúng một (sàn LOO):

| So sánh trực tiếp F1 (0,80) vs F2 (0,85) | F1 | F2 | Ai thắng |
|---|---|---|---|
| CAGR | 29,85% | 30,51% | **F2** (+0,66pp) |
| Sharpe | 1,87 | 1,86 | F1 |
| MaxDD | −18,3% | −18,9% | F1 |
| Calmar | **1,63** | 1,62 | F1 (và là **đỉnh của cả dải quét**) |
| P(MaxDD < −30%) bootstrap | 2,8% | 3,4% | F1 (**+21% rủi ro tương đối** khi lên F2) |
| MaxDD p5 bootstrap | −28,2% | −28,7% | F1 |
| Lỗ năm 2022 | −4,3% | −5,4% | F1 |
| Sàn LOO (ô yếu nhất) | +0,71pp | +1,29pp | **F2** |

⇒ Tính trên chênh so với Conservative: **F1 lấy được 60% phần CAGR tăng thêm của F2**
(+0,99pp trên +1,65pp) **trong khi chỉ chịu 50% phần rủi ro đuôi tăng thêm**
(P(DD<−30%): +0,6pp trên +1,2pp) **và 45% phần MaxDD xấu đi** (+0,5pp trên +1,1pp).
Đây là hàng dành cho khẩu vị **"muốn hơn Conservative nhưng không muốn đánh đổi rủi ro nhiều"**.

**KHÔNG khuyến nghị chọn cái nào** — đây là quyết định khẩu vị rủi ro của user, không phải câu
hỏi kỹ thuật (đúng như §G mục 5 của báo cáo 08-03 đã nêu). Việc của báo cáo này là **trình đủ 4
hàng với cùng một bộ chỉ tiêu**, không phải chọn hộ.

---

## 1. Cấu hình chung & các cổng tự kiểm

Giữ **y hệt** vòng 2×2 để mọi con số so sánh được với nhau:
`AUDIT_END=2026-06-19` · `NAV_TOTAL_B=50` · `universe_pit` ·
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate` · `BQ_CACHE_THREADS=1` ·
`ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo` · `LAG_ADV_BASIS=price` (mặc định
production hiện hành) · argv `v23a none postbull 0 edge` · `$DNA_PYEXE` (pandas 3).

| Cổng | Kết quả |
|---|---|
| **No-op gate** — chân `agg_A0_gate` (target 0,70 + band 0,005 = hằng số gốc) chạy **qua code đã thêm 2 switch mới** | CSV md5 **`7d053e62…`** — **trùng khít** chân A vòng trước ⇒ hai switch `PARK_BAND`/`PARK_STATES` là **no-op tuyệt đối** ở giá trị mặc định. **PASS** |
| **selfcheck cash-flow + NAV identity** | **0 VND** cả 2 sổ (BAL + LAG), ở **cả 7** chân |
| **MD5 phân biệt** | 7 chân → 7 file khác nhau (target khác ⇒ `_park3-XX` vào tên file, `EXP_TAG` vào tên file) ⇒ không tái diễn lỗi no-op của §0 báo cáo trước |
| **Production untouched** | `git status` sạch trên 5 đường dẫn production |

Đây là lý do chân A0 được chạy lại dù đã có số: §0 của báo cáo 08-03 chính là một ablation
**no-op** mà không ai phát hiện cho tới khi so md5. Không lặp lại lỗi đó.

---

## 2. Conservative — trình bày lại chân A thành một phương án độc lập

**Định nghĩa:** wire cả L1 (`PREFILL_STATE_REBAL` — park-target compliance hằng ngày) và L2
(`JIT_FOR_BA_BUY` — unpark khi thiếu tiền mua), **dùng đúng tham số đã backtest**:
target park NEUTRAL `0,70`, ngưỡng kích hoạt `0,005 × pool`, FIFO theo lô, trần `_etf_day_cap`
(20% ADV). **Không một tham số nào là mới.** Thiết kế chi tiết: §B2/B3/B4/B5 báo cáo 08-03.

| CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS | OOS |
|---|---|---|---|---|---|---|
| 28,86% | 1,90 | −17,8% | 1,62 | 1.178,0B | 27,09% | 30,48% |

**Vì sao đây là phương án "0 rủi ro mô hình":**
- Đúng bằng số pin R3 trong `data/results_registry.md` — không phải một cấu hình mới, mà là
  **đưa live về đúng cuốn sổ đã được duyệt và đã đo**.
- Toàn bộ audit trail đã có: 2×2 ablation, quant-skeptic CONFIRMED (2026-08-03T18:00), self-check 0 VND.
- N_trials = **0** (không chọn gì từ họ nào) ⇒ DSR/PBO về nguyên tắc không áp dụng; con số ở
  bảng §0 chỉ để so ngang hàng với Aggressive.

**Giá phải trả, nói thẳng:** so với live hôm nay, CAGR mô phỏng **33,16% → 28,86% (−4,30pp)**.
Đổi lại MaxDD **−33,7% → −17,8%** và P(DD<−30%) **63,7% → 2,2%**.

---

## 3. Aggressive — việc thật của vòng này

### 3.1 Vì sao "L1 only" (chân C) KHÔNG phải phương án aggressive

Dispatch đã nêu đúng và tôi xác nhận bằng số: chân C có CAGR **28,08% < 28,86%** của Conservative,
Sharpe 1,88 < 1,90, Calmar 1,57 < 1,62. **C thua Conservative trên MỌI chỉ tiêu.** Nó không cho
user thêm bất cứ thứ gì để đánh đổi ⇒ loại khỏi menu, không trình bày như một lựa chọn.

### 3.2 Hai trục nới biên đã thử — và một trục bị LOẠI

Aggressive đúng nghĩa phải **giữ nhiều beta cổ phiếu hơn Conservative** nhưng **kiểm soát tốt hơn
hẳn live**. Hai trục nới biên khả dĩ, cả hai đều đã chạy đủ:

**Trục 1 — target park NEUTRAL** (`PARK_STATES="3:X"`, không cần sửa code):

*(bold = tốt nhất cột)*

| target | CAGR | Sharpe | MaxDD | Calmar | Final NAV | eq% TB |
|---|---|---|---|---|---|---|
| 0,70 (= Conservative) | 28,86% | **1,90** | **−17,8%** | 1,62 | 1.178,0B | 60,4% |
| **0,80 (F1 = Aggressive-lite)** | 29,85% | 1,87 | −18,3% | **1,63** | 1.295,7B | 63,1% |
| **0,85 (F2 = Aggressive)** | 30,51% | 1,86 | −18,9% | 1,62 | 1.380,2B | 64,7% |
| 0,90 (F3 — **bị loại**, §3.3) | **31,01%** | 1,84 | −19,5% | 1,59 | 1.447,4B | 66,8% |

**Dose-response ĐƠN ĐIỆU và trơn trên cả 4 chỉ tiêu** — dấu hiệu của một cơ chế thật, không phải
một điểm may mắn: CAGR ↑, Sharpe ↓, MaxDD ↓, đều đặn từng nấc.
**Calmar KHÔNG đơn điệu**: 1,62 → **1,63** (đỉnh, ở 0,80) → 1,62 → 1,59 (gãy ở 0,90). Chênh lệch
0,01 trong dải 0,70–0,85 nằm trong nhiễu ⇒ đọc dải đó là **plateau**, và **đỉnh danh nghĩa của
plateau là F1 (0,80), không phải F2** — xem đính chính §3.3.

**Trục 2 — nới ngưỡng kích hoạt (deadband)** (`PARK_BAND`, switch mới trong bản sao research):

| band | CAGR | Sharpe | MaxDD | Calmar | số lệnh ETF (BAL / LAG) |
|---|---|---|---|---|---|
| 0,005 (= Conservative) | 28,86% | 1,90 | −17,8% | 1,62 | 664 / 1.230 |
| 0,030 (G1) | 28,92% | 1,90 | −17,8% | 1,62 | — |
| 0,060 (G2) | 29,17% | **1,91** | −17,8% | **1,64** | **334 / 1.035** |

> 🔴 **Trục 2 BỊ LOẠI làm nút aggression.** Nới band gấp **12 lần** (0,005 → 0,06) chỉ đổi được
> **+0,31pp CAGR** và **MaxDD KHÔNG đổi một chữ số nào** (−17,8% cả ba). Nó không phải nút rủi ro —
> nó là **nút ma sát**: cắt gần **một nửa** số lệnh parking của sổ BAL (664 → 334). Phần lợi
> nhuận nhỏ nó tạo ra chủ yếu là **phí giao dịch tiết kiệm được**, không phải beta thêm.
>
> Kiểm chứng chéo: chân **H1** (target 0,85 **+** band 0,03) cho **30,53% / 1,85 / −18,9% / 1,62** —
> gần như **trùng khít** F2 (30,51% / 1,86 / −18,9% / 1,62). Cộng thêm trục band vào trục target
> **không đổi gì cả** ⇒ xác nhận band là trục trơ. **Chọn F2 (1 tham số đổi) thay vì H1 (2 tham số đổi)** —
> cùng kết quả thì lấy cấu hình đơn giản hơn.

### 3.3 Chọn mức nào — và tại sao trình BA mức chứ không một

> 🔴 **ĐÍNH CHÍNH (vòng 2, sau quant-skeptic).** Bản đầu của mục này viết *"lấy đỉnh của plateau
> (0,85)"*. **Câu đó sai so với chính bảng ở §3.2**: theo Calmar, đỉnh của dải là **F1 = 1,63**
> (0,70 → 1,62 · **0,80 → 1,63** · 0,85 → 1,62 · 0,90 → 1,59). Chữ "đỉnh plateau" đã khiến việc
> chọn F2 trông như một kết luận rút ra từ số liệu, trong khi thực chất nó là một **lựa chọn xếp
> hạng theo CAGR**. Mục này viết lại để nói thẳng điều đó.

**Bước 1 — loại F3 (0,90). Đây mới là kết luận thật sự rút ra từ số liệu**, bốn căn cứ:

1. **F3 nằm ở BIÊN của dải quét, không phải điểm trong.** Trên trục này, 1,00 = park toàn bộ pool
   = *không bao giờ trim* = quay về đúng bệnh của live (chân E). Chọn nghiệm sát biên của một dải
   mà đầu kia là chế độ hỏng là chữ ký kinh điển của overfit.
2. **Calmar gãy đúng ở F3.** Dải 0,70–0,85 nằm trong **1,62–1,63** (chênh 0,01 = nhiễu, không phân
   biệt được); 0,90 rơi xuống **1,59** — bước gãy đầu tiên vượt hẳn mức nhiễu đó.
3. **Đánh đổi đuôi xấu đi nhanh hơn lợi nhuận.** F2 → F3: CAGR p50 bootstrap chỉ +0,4pp,
   nhưng **P(DD<−30%) tăng 3,4% → 4,8% (+41% tương đối)** và MaxDD p5 chạm **−29,9%**, tức gần
   như đâm thẳng vào ngưỡng neo rủi ro −30% mà `kb/current_ops.md` đang dặn.
4. **Nhất quán với bằng chứng CŨ trên cùng trục** (§3.5) — mức 0,94 đã từng được đo là mức bắt
   đầu mất Calmar rõ rệt; 0,90 là hàng xóm của nó.

**Bước 2 — trong dải còn lại 0,70 / 0,80 / 0,85, SỐ LIỆU KHÔNG CHỌN HỘ ĐƯỢC.** Cả ba nằm trên
cùng một plateau Calmar (1,62 / 1,63 / 1,62) và cùng một dải Sharpe (1,90 / 1,87 / 1,86). Sự khác
biệt giữa chúng **không phải chất lượng mô hình mà là mức beta cổ phiếu** — tức đúng thứ thuộc về
khẩu vị rủi ro của user. Vì vậy **cả ba đều lên bảng quyết định §0**, không mức nào bị giấu.

**Bước 3 — vì sao nhãn "Aggressive" được gắn cho F2 (0,85), nói tường minh chứ không để suy ngầm:**

- Nhãn "Aggressive" theo định nghĩa là **cực CAGR cao nhất còn an toàn** trong dải đã lọc ở Bước 1.
  Xếp hạng theo CAGR ⇒ F2. **Đây là một lựa chọn định nghĩa, không phải một phát hiện thống kê.**
- **Biện minh cho việc xếp hạng bằng CAGR (chứ không bằng Sharpe/Calmar): `PBO(CAGR) = 0,080` vs
  `PBO(Sharpe) = 0,411`** (§3.4). Nghĩa cơ học: thứ hạng theo **CAGR** giữ được từ nửa mẫu này sang
  nửa mẫu kia (robust, PBO thấp), còn thứ hạng theo **Sharpe** gần như ngẫu nhiên (7 chân nằm trong
  1,84–1,91 = dải nhiễu, PBO 0,41 ≈ tung đồng xu). ⇒ Nếu phải xếp hạng trong họ này, **CAGR là
  metric duy nhất trong tay có bằng chứng là xếp hạng được**. Trên metric đó F2 > F1 > A0.
- **Hệ quả PHẢI nói cùng lúc, không được tách rời:** chính vì Sharpe/Calmar không xếp hạng được
  trong dải này, **không có căn cứ thống kê nào để nói F2 "tốt hơn" F1**. F2 chỉ đơn giản là mức
  **nhiều beta hơn**. Ai muốn ưu tiên Calmar/MaxDD/đuôi thì **F1 mới là hàng khớp** — và F1 tình cờ
  cũng là đỉnh Calmar của dải.

⇒ **Aggressive = F2 (target 0,85)** và **Aggressive-lite = F1 (target 0,80)**, cả hai giữ nguyên
mọi tham số khác (band 0,005, FIFO, `_etf_day_cap`). Mỗi phương án đúng **một** tham số đổi.

### 3.4 Multiple-testing: khai báo N_trials, DSR, PBO, LOO

**N_trials — khai đủ, không giấu:**

| Nguồn | Số cấu hình | Ghi chú |
|---|---|---|
| **Vòng này** (target × band, engine 2 sổ đầy đủ) | **7** | 0,70/0,80/0,85/0,90 × band 0,005; + band 0,03/0,06 @0,70; + 0,85×0,03 |
| Trước đây, cùng trục (job `Taylor_20260703_130720`, NAV 2 sổ đầy đủ) | 3 | 0,70 / 0,94 / 1,00 |
| Trước đây, cùng trục (job `Taylor_20260703_120555`, sleeve cô lập) | 6 | 0,70/0,80/0,85/0,90/0,94/1,00 |
| **Cộng dồn trên trục "target park NEUTRAL"** | **≈ 16** | 6 mức target khác nhau, 3 harness |

**DSR** (Bailey & López de Prado 2014, hàm copy nguyên từ `dsr_pbo_annex.py`):

| Cấu hình | DSR @N=7 (Var hẹp) | DSR @N=7 (Var rộng) | DSR @N=120 | DSR @N=200 |
|---|---|---|---|---|
| Conservative (0,70) | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| F1 (0,80) | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| **F2 (0,85)** | **1,0000** | **1,0000** | **1,0000** | **1,0000** |
| F3 (0,90) | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| G1/G2/H1 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |

> ⚠️ **Đọc DSR ở đây cho đúng — nó KHÔNG phân biệt được các cấu hình này.** DSR = 1,0000 cho
> **tất cả 7** chân, kể cả ở giả định thù địch nhất (N=200 trials, Var(SR) lấy từ **cả 311 CSV**
> của họ tìm kiếm V2.3A/V2.4 chứ không phải 7 chân gần-giống-nhau — sd ann-SR 0,132 thay vì 0,028).
> Ý nghĩa đúng: **không chân nào là một cú may thống kê** (12,5 năm dữ liệu, Sharpe ~1,85, T=3.106
> phiên). Ý nghĩa KHÔNG được suy ra: DSR **không** nói F2 tốt hơn hay xấu hơn Conservative —
> nó bão hoà ở 1,0 nên vô dụng cho việc **xếp hạng trong họ**. Ai trích "DSR=1,0 nên Aggressive an
> toàn" là đọc sai công cụ.

**PBO** (CSCV, Bailey-Borwein-LdP-Zhu 2017; S=16 block, 12.870 tổ hợp IS/OOS, ma trận 3.106 ngày × 7 cấu hình):

| metric xếp hạng | PBO | logit trung vị |
|---|---|---|
| **CAGR** (đúng mục tiêu mà nút này nhắm tới) | **0,0803** | +0,51 |
| Sharpe | 0,4105 | +0,00 |

> **PBO theo CAGR = 0,080 — thấp, tốt** (ngưỡng cảnh báo 0,5). Nghĩa là: chọn cấu hình tốt nhất
> trong nửa mẫu này thì ở nửa mẫu kia nó gần như luôn vẫn nằm trên trung vị — đúng như kỳ vọng của
> một dose-response đơn điệu.
> ⚠️ **PBO theo Sharpe = 0,411 — cao, và tôi báo cáo nó chứ không giấu.** Lý do cơ học chứ không
> phải bệnh: Sharpe của cả 7 chân nằm trong dải **1,84–1,91**, chênh lệch ở mức nhiễu, nên "chân
> Sharpe-tốt-nhất trong nửa mẫu" gần như là ngẫu nhiên. Đây là bằng chứng rằng **trục này không
> mua được Sharpe** — trùng khớp với chính bảng dose-response (Sharpe giảm đều khi target tăng).
> Cả hai con số PBO đều là thống kê **của cả họ**, không xếp hạng được từng cấu hình.

**Per-year leave-one-out** — bỏ từng năm rồi tính lại CAGR chain-link, chênh so với Conservative:

| Cấu hình | Δfull | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | **2022** | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 (0,80) | +1,01 | +1,11 | +0,98 | +1,04 | +0,85 | +1,20 | +0,96 | +1,04 | +1,25 | +0,71 | +0,99 | +1,08 | +1,03 | +0,94 |
| **F2 (0,85)** | **+1,63** | +1,79 | +1,58 | +1,69 | +1,38 | +1,94 | +1,55 | +1,71 | +1,81 | **+1,52** | +1,61 | +1,69 | +1,29 | +1,64 |
| F3 (0,90) | +2,13 | +2,34 | +2,05 | +2,12 | +1,80 | +2,57 | +2,08 | +2,08 | +1,89 | +2,09 | +2,10 | +2,38 | +1,92 | +2,27 |
| G2 (band 6%) | +0,35 | +0,38 | +0,37 | +0,36 | +0,35 | +0,36 | +0,37 | +0,41 | +0,61 | **−0,13** | +0,36 | +0,43 | +0,36 | +0,28 |

> **Cả F1 và F2 đều vượt kiểm định LOO một cách sạch sẽ:** bỏ BẤT KỲ năm nào, edge vẫn dương —
> F2 trong dải **+1,29 … +1,94pp**, F1 trong dải **+0,71 … +1,25pp**. Không ô nào âm, không ô nào
> gánh phần lớn ở cả hai. Đây đúng là điều mà ca Wave1/H8a-tiebreaker (2026-07-05) đã dạy phải
> kiểm — và **không** chân nào mắc lỗi đó.
> Chỗ DUY NHẤT F2 hơn F1 ngoài CAGR nằm ở đây: **sàn LOO của F2 (+1,29pp) cao hơn sàn của F1
> (+0,71pp)** — edge của F2 ít phụ thuộc một năm cụ thể hơn về mặt tương đối. Ô yếu nhất của F1 là
> **2022 (+0,71pp)**, tức năm sập là năm F1 hưởng lợi ít nhất so với Conservative — nhưng vẫn dương,
> và về lợi nhuận tuyệt đối năm 2022 thì F1 lại là chân **ÍT LỖ NHẤT** (−4,3% vs −5,4% F2 vs −8,0% A0).
> Ngược lại, **G2 lộ nguyên hình**: ô 2022 là **−0,13** (ô âm DUY NHẤT của cả bảng), tức phần
> "lợi" nhỏ nhoi của nó đến từ việc giữ thêm cổ phiếu qua năm sập — thêm một lý do loại trục band.
> Còn IS/OOS thì dose-response giữ nguyên **ở CẢ HAI NỬA riêng biệt** (F2: IS 28,37 / OOS 32,48,
> đều cao hơn Conservative 27,09 / 30,48) — không phải hiện tượng chỉ sống ở một nửa mẫu.

**Thống kê tôi đã tính nhưng KHÔNG dùng để chọn** (nêu ra vì đã chạy): "độ tụt hạng IS→OOS" từng
cấu hình. Trung bình Δrank = +0,000 cho cả 7 chân — **suy biến về mặt cấu trúc** (tập tổ hợp CSCV
đối xứng: mỗi split đều có split bù hoán đổi IS/OOS), nên chỉ còn tần suất tụt hạng đọc được
(F1 24,8% … H1 41,0%), mà con số đó lại nhiễu vì thứ hạng CAGR gần như tất định theo target.
**Không cho nó tham gia quyết định** — ghi lại để ai đọc log không tưởng là bằng chứng.

### 3.5 Đối chiếu với bằng chứng CŨ trên cùng trục — có một chỗ phải nói rõ

`data/trading_rules.json` → `neutral_parking` đã có sẵn bằng chứng cho trục này (job
`Taylor_20260703_130720`, NAV 2 sổ đầy đủ):

| target | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| 0,70 | 26,83% | 1,78 | −16,5% | 1,63 |
| 0,94 | 28,01% | 1,66 | −18,8% | 1,49 |
| 1,00 | 29,30% | 1,65 | −19,3% | 1,52 |

⚠️ **KHÁC VINTAGE — cấm so trực tiếp với số vòng này.** Vintage 07-03 chạy trên `ticker_prune` và
trước khi `LAG_ADV_BASIS` đổi `close`→`price` (08-02), nên 0,70 ở đó là 26,83% còn ở đây là 28,86%.
So được là **chiều và hình dạng**, không phải mức:
- ✅ **Cùng chiều, xác nhận lẫn nhau**: target ↑ ⇒ CAGR ↑, Sharpe ↓, MaxDD sâu hơn.
- ✅ **Bổ sung chỗ trống**: vintage cũ **không có** điểm 0,80/0,85 trên harness NAV đầy đủ — nó
  nhảy thẳng 0,70 → 0,94. Vòng này lấp đúng khoảng trống đó và cho thấy **Calmar còn giữ plateau
  tới 0,85** rồi mới gãy. Không mâu thuẫn: 0,94 (Calmar 1,49) nằm **ngoài** plateau, đúng như 0,90
  (1,59) đã bắt đầu gãy ở vòng này.
- ⚠️ **Một chỗ PHẢI đính chính cách đọc**: job `Taylor_20260703_120555` (sleeve cô lập) kết luận
  *"Sharpe BẤT BIẾN 70→100, Calmar TĂNG theo exposure, không có knee"*. **Kết luận đó đúng với phép
  đo đó nhưng KHÔNG áp được cho hệ production** — vì sleeve cô lập tính `port = e·rb`, hệ số `e`
  triệt tiêu trong tỷ số Sharpe **theo đại số**, nên Sharpe *buộc phải* bất biến, đó là hằng đẳng
  thức chứ không phải phát hiện thực nghiệm. Trong engine 2 sổ đầy đủ, target cao còn **tương tác**
  với việc cấp vốn cho BAL/LAG (§E báo cáo 08-03 đã đo tương tác này rất mạnh), và ở đó
  **Sharpe GIẢM thật: 1,90 → 1,84**. ⇒ Khi trích dẫn cho quyết định production, dùng bảng của vòng
  này, **không** dùng "Calmar tăng theo exposure" của bản sleeve.

### 3.6 Cổng phải mở trước khi Aggressive / Aggressive-lite được phép vào plan

Cả hai **không phải một rule mới** — chúng chính là cái nút mà `trading_rules.json` đã dựng sẵn
và đang để TẮT: `neutral_parking.risk_dial_override`, trạng thái `PROPOSED/DISABLED`. Muốn dùng
F1 **hoặc** F2 (yêu cầu giống hệt nhau, chỉ khác giá trị target ghi vào):

1. `risk_dial_confirmed_by_user: true` — user xác nhận tường minh (Mafee **hard-block** nếu thiếu).
2. `risk_dial_warning_acknowledged` — phải **trích số thật** về cái giá risk-adjusted. Lưu ý:
   bảng đang nằm trong `trading_rules.json` (`measured_tradeoff_job_130720`) **chưa có mức 0,80 lẫn
   0,85** và là vintage cũ ⇒ nếu user chọn F1 hoặc F2, **phải bổ sung bảng vòng này vào `evidence`**
   trước, nếu không nội dung acknowledge sẽ dẫn số sai cơ sở.
3. Ghi chú của chính rule đó: *"Changing the engine DEFAULT away from 0.70 requires user approval
   applied to LIVE"* — tức đây là quyết định của user, đúng như dispatch đặt vấn đề.

### 3.7 Capacity ĐO LẠI TRỰC TIẾP ở mức `park_mv` thật của F1 và F2 (không còn ngoại suy)

quant-skeptic ghi rõ: §D báo cáo 08-03 chỉ đo capacity ở **target 0,70**, mọi phát biểu về F2 là
**extrapolation chưa verify**. Vòng này chạy lại bằng `capacity_check_v2.py` — cùng nguồn, cùng
định nghĩa ADV, chỉ ĐỌC, không sửa production. Đầu vào quy mô sổ park **lấy trực tiếp từ CSV mô
phỏng của chính từng cấu hình** (`exposure_check.py`), không suy diễn:

| | Conservative | F1 (0,80) | F2 (0,85) |
|---|---|---|---|
| park% NAV trung bình | 24,8% | 28,6% | **30,4%** |
| park% NAV **p95** (đỉnh thực tế) | 64,2% | 73,5% | **78,4%** |
| park% NAV **max** | 66,8% | 76,5% | **81,0%** |

**A. Nhu cầu trim HÔM NAY, đo ở từng target** (sổ live 2026-08-03, `_etf_day_cap` = 1.337,0 tỷ/phiên;
trần per-name live = `LAG_ADV_PCT 20% × ADV × share 0,5`):

| Cấu hình | acct | park_mv | cần trim | **max %ADV per-name** | dư địa tới trần |
|---|---|---|---|---|---|
| Conservative 0,70 | SpaceX | 642,5tr | 189,4tr | 0,016% | 638× |
| | ZaloPay | 297,6tr | 85,2tr | 0,006% | 1.585× |
| **F1 0,80** | SpaceX | 642,5tr | **124,6tr** | **0,010%** | **969×** |
| | ZaloPay | 297,6tr | 54,9tr | 0,004% | 2.461× |
| **F2 0,85** | SpaceX | 642,5tr | **92,3tr** | **0,008%** | **1.309×** |
| | ZaloPay | 297,6tr | 39,7tr | 0,003% | 3.401× |

> **Kết quả ngược chiều trực giác nhưng đúng cơ học: target CAO ⇒ trim ÍT hơn ⇒ áp lực %ADV NHỎ
> hơn.** L1 chỉ bán phần *vượt* target; nâng trần từ 0,70 lên 0,85 làm phần vượt co lại. Trên trục
> "nhu cầu bán hằng ngày", F1/F2 **an toàn hơn** Conservative, không phải rủi ro hơn.

**B. Stress — thoát sổ park ở quy mô RIÊNG của từng cấu hình** (regime rời NEUTRAL ⇒ target→0,
`park_mv = park%NAV của chính cấu hình đó × NAV live`; NAV SpaceX 959,6tr / ZaloPay 902,0tr):

| Kịch bản (SpaceX) | park_mv | phiên để thoát | max %ADV/phiên |
|---|---|---|---|
| Conservative @p95 (64,2% NAV) | 616,1tr | < 0,01 | 0,051% |
| F1 @p95 (73,5% NAV) | 705,3tr | < 0,01 | 0,058% |
| **F2 @p95 (78,4% NAV)** | **752,3tr** | **< 0,01** | **0,062%** |
| **F2 @max (81,0% NAV)** | **777,3tr** | **< 0,01** | **0,064%** |

Tốc độ thoát an toàn bị ràng buộc bởi **per-name**, không phải trần rổ: SpaceX **120,8 tỷ/phiên**
(mã ràng buộc **LPB**), ZaloPay **135,0 tỷ/phiên** (**BID**) — trong khi `_etf_day_cap` của engine
là 1.337,0 tỷ, tức **lỏng hơn 9,9–11,1×** (đúng như §D 08-03; T_bind chỉ phụ thuộc phân bố trọng số
+ ADV nên KHÔNG đổi theo target — đây là lý do cấu trúc khiến kết luận giữ nguyên qua mọi mức).

**C. Ngưỡng thật sự binding.** Ngay cả kịch bản xấu nhất của F2 (bán sạch sổ park ở mức max 81,0%
NAV trong MỘT phiên) chỉ chạm **0,064% ADV** của mã nặng nhất — cách trần live 20% **hơn 300×**.
Để mức p95 của F2 chạm ngưỡng per-name, **NAV phải gấp ~161× hiện tại (SpaceX) / ~191× (ZaloPay)**.

> ✅ **KẾT LUẬN capacity (đo trực tiếp, không ngoại suy): không mức nào trong 0,70 / 0,80 / 0,85 bị
> ràng buộc thanh khoản ở quy mô NAV hiện tại — cách ngưỡng 2–3 bậc độ lớn.** Capacity **không phải**
> một tiêu chí phân biệt giữa 4 hàng ở §0; quyết định vẫn thuần khẩu vị rủi ro.
> ⚠️ **Giới hạn của phép đo này, ghi rõ:** `park_mv` live vẫn **suy luận theo tên mã** (hạn chế A7 —
> chưa có tag `book`/`play_type` per-lot). Rổ custom30V dùng bản rebal **2026-05-05**; đổi rổ ⇒ phải
> chạy lại. Dư địa 300–3.400× lớn tới mức không một sai số hợp lý nào của hai giả định trên đảo
> được kết luận, nhưng con số chính xác thì phụ thuộc chúng.

---

## 4. Điều KHÔNG được suy ra từ báo cáo này

- **F1 VÀ F2 đều CHƯA qua quant-skeptic.** Cả hai là cấu hình mới, mỗi cái 1 tham số mới, N_trials
  khai ở §3.4. Chúng **không** ngang hàng Conservative về độ tin cậy cho tới khi có một vòng
  quant-skeptic riêng. Conservative thì đã có (CONFIRMED 2026-08-03T18:00 cho vòng 2×2).
  ⚠️ Vòng quant-skeptic 2026-08-04T02:16 **chỉ verify báo cáo, không verify cấu hình** — verdict
  CONFIRMED (medium) đi kèm đúng 2 objection mà bản này đang sửa; nó **không** là sign-off cho F1/F2.
- **Không suy ra "F1/F2 an toàn vì DSR=1,0"** — §3.4 đã nói rõ DSR bão hoà, không phân biệt.
- **Không suy ra "F1 tốt hơn F2" (hay ngược lại) từ Sharpe/Calmar.** §3.3 Bước 2: chênh lệch
  Calmar 1,63 vs 1,62 và Sharpe 1,87 vs 1,86 **nằm trong nhiễu** — chính `PBO(Sharpe)=0,411` là
  bằng chứng rằng thứ hạng theo các metric đó không giữ được ra ngoài mẫu. F1 được trình như "cân
  bằng hơn" vì **tỷ lệ đánh đổi** (60% return uplift / 50% tail risk, §0.1), **không** vì nó thắng
  một phép kiểm định thống kê nào.
- **Cả 4 phương án đều phụ thuộc P0 chưa làm.** L1/L2 **không thi công chính xác được** khi live
  chưa tag `book`/`play_type` per-lot (§A7/§F báo cáo 08-03) — thiếu nó, L1 sẽ im lặng không trim
  gì. Bootstrap snapshot book-tag cho SpaceX/ZaloPay vẫn **CHƯA có** và không tự sinh được.
- **Neo MaxDD:** lỗi fidelity `liq<=0` vẫn mở ⇒ theo `kb/current_ops.md`, đọc mọi con số MaxDD ở
  đây như **cận dưới**, và giữ neo DD thực tế ~−30%. Điều này áp cho **cả bốn** hàng, không riêng hàng nào.
- **Chạy ở NAV 50B, `universe_pit`, không margin.** SpaceX có margin, ZaloPay cash-only ⇒ mức phóng
  đại rủi ro ở tài khoản có margin có thể **cao hơn** con số ở đây, không thấp hơn.
- **Không suy ra F1/F2 "mua thêm alpha"** — chúng mua thêm **beta cổ phiếu** (+2,7pp / +4,3pp tỷ
  trọng TB). Sharpe giảm đều (1,90 → 1,87 → 1,86) chính là cách hệ nói điều đó.
- **Capacity KHÔNG binding ≠ capacity vô hạn.** §3.7 đo ở NAV hiện tại (~0,96B/0,90B mỗi tài khoản)
  và rổ custom30V bản 2026-05-05. Kết luận là *"cách ngưỡng 2–3 bậc"*, không phải *"không bao giờ
  chạm"* — phải chạy lại `capacity_check_v2.py` khi NAV tăng bậc hoặc khi rổ đổi.

---

## 5. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
OUT=mike/agents/Taylor/exp_park_jit_20260803
$OUT/run_agg.sh agg_A0_gate   "3:0.7"  0.005    # GATE: phải ra md5 7d053e62…
$OUT/run_agg.sh agg_F1_t80    "3:0.8"  0.005    # = Aggressive-lite
$OUT/run_agg.sh agg_F2_t85    "3:0.85" 0.005    # = Aggressive
$OUT/run_agg.sh agg_F3_t90    "3:0.9"  0.005
$OUT/run_agg.sh agg_G1_b03    "3:0.7"  0.03
$OUT/run_agg.sh agg_G2_b06    "3:0.7"  0.06
$OUT/run_agg.sh agg_H1_t85b03 "3:0.85" 0.03
$DNA_PYEXE $OUT/agg_metrics.py       # bảng + DSR + PBO + LOO + bootstrap -> agg_metrics_out.txt
$DNA_PYEXE $OUT/exposure_check.py    # tỷ trọng cổ phiếu + park% (TB/p95/max)
$DNA_PYEXE $OUT/capacity_check_v2.py # capacity ở park_mv THẬT của F1/F2 -> capacity_check_v2_out.txt
```

Hiện vật: `agg_*.log` (7 log engine), `agg_metrics_out.txt`, `agg_metrics.py`,
`exposure_check.py`, `capacity_check_v2.py` + `capacity_check_v2_out.txt` (mới, vòng 2),
`run_agg.sh`, `run_leg2.py`; CSV NAV trong `data/` với hậu tố
`_exp_agg_*_univpit.csv`. Switch `PARK_BAND` chỉ tồn tại trong **bản sao research** của
`simulate_holistic_nav.py`; bản production không bị đụng.

**Vòng 2 (job `Taylor_20260804_022423`) KHÔNG chạy lại engine** — F1 đã có sẵn từ vòng quét trước
(`agg_F1_t80.log`, CSV `..._park3-80_..._exp_agg_F1_t80_univpit.csv`), chỉ trích xuất + trình bày
lại. Việc chạy mới duy nhất là `capacity_check_v2.py` (script chỉ ĐỌC: parquet cache BQ +
`dnse_raw_2026-08-03.jsonl` + `custom30v_8l_publish.csv`). `git status` trên 5 đường dẫn production
vẫn rỗng sau vòng 2.
