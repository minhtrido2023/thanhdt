# Gate ĐỘNG theo năng lực fill thật (executability) cho book LAG — A/B 12 chân, 2 thang NAV

**Job:** `Taylor_20260804_085248` · 2026-08-04 · Taylor
**Câu hỏi (user John, thread 1521735922066919515):** thay vì gate ADV bằng một số VND **cố định**
(2 tỷ — đã NO-GO ở job `Taylor_20260804_080547`), thiết kế gate **scale theo slot thật của từng
lệnh**: ứng viên LAG chỉ được vào lệnh nếu ADV đủ để fill trọn slot trong `N` phiên ở mức
`%ADV/phiên` **đã xác nhận LIVE** (3,86%), tức
`required_ADV = slot_size_vnd / (fill_pct_live × N_sessions)`.

> **KẾT LUẬN 1 DÒNG — luật executability ĐÚNG VỀ CƠ CHẾ và làm được đúng việc nó hứa (vị thế
> kẹt-không-fill-nổi **35,0% → 0,0%**, bằng số học chứ không bằng may rủi), nhưng KHÔNG được bán
> như một cải thiện lợi nhuận: phần gia tăng +1,53pp CAGR ở thang NAV thật **đổi dấu** khi bỏ
> 2020+2021 (−0,22pp), sign test 8/13 năm (p=0,291).**
>
> **Con số vận hành đáng giá nhất của cả job:** ở NAV thật đang chạy (~950 triệu), executability
> chỉ đòi **ADV ≳ 0,32 tỷ/phiên** — tức đề xuất gate tĩnh **2 tỷ CHẶT HƠN ~6,3 lần** so với nhu
> cầu thật, và con số **17 tỷ** ở báo cáo trước (neo ở NAV 50B) **chặt hơn ~53 lần**. Ai định lấy
> "17 tỷ" áp vào tài khoản đang chạy thì đó là một sai số hai bậc độ lớn.

> 🔴 **CẢNH BÁO BẮT BUỘC ĐỌC TRƯỚC MỌI BẢNG SỐ DƯỚI ĐÂY** (bổ sung sau review quant-skeptic
> 2026-08-04, đúng một khiếm khuyết thật của bản đầu): **chân so sánh chính của báo cáo này là
> L1 (`LIQ_ZERO_BLOCK=lag`) = 32,71% @50B / 32,13% @1B, và bản thân con số đó ĐANG BỊ TREO.**
> `data/results_registry.md` (mục "PHÂN RÃ CƠ CHẾ của Δ", verdict quant-skeptic **INCONCLUSIVE**,
> `mike/logs/verify_20260802_173456.log`) ghi thẳng: ***"KHÔNG được trích 31,32%/32,71% làm cơ sở
> kỳ vọng ở bất kỳ đâu"*** — câu hỏi "Δ này là alpha thật hay hiện vật mô hình fill" đã **3 lần**
> không tách được. Báo cáo này dùng L1 làm **mốc đối chiếu nội bộ** (để đo phần GIA TĂNG của luật
> mới), **không** dùng nó làm cơ sở kỳ vọng. Chiều sai số theo hướng bảo thủ: nếu L1 bị thổi phồng
> bởi hiện vật, thì kết luận "không có edge gia tăng trên nền L1" chỉ càng **chắc hơn**, không
> lỏng hơn. **Đừng trích 32,71% / 32,13% ra khỏi báo cáo này.** Xem thêm §6.5 — job này có bằng
> chứng MỚI cho chính câu hỏi treo đó.

---

## 0. Công thức lấy từ code thật, không đoán (skill §1)

| Thành phần | Nguồn code | Giá trị |
|---|---|---|
| slot LAG trong engine | `simulate_holistic_nav.py:1144-1147` — `target_value = cur_nav × tier_weights[play_type]`, tính tại **first fill** | **path-dependent**, không phải hằng số |
| trọng số tầng | `pt_v23_audit_2014.py:1362-1363` `LAG_TW` | `LAG_HI 0,10` / `LAG_LO 0,08` |
| NAV sổ LAG | `pt_v23_audit_2014.py:57` `LAG_NAV = TOTAL_NAV/2` | 25B khi `NAV_TOTAL_B=50` |
| mô hình fill engine | `pt_v23_audit_2014.py:1333` `LIQ_LAG` | `liquidity_volume_pct=0,20`, `max_fill_days=5`, `min_fill_pct=0,30` |
| trần %ADV live | `trading_bot/plan.py:376,501` `cap_lag_orders` | `LAG_ADV_PCT=0,20 × ADV × share` — **TRIM**, không loại mã |
| lọc live tầng tín hiệu | `lag_liquidity_filter.py:179` | chỉ `adv_vnd > 0` — **nhị phân**, không có ngưỡng độ lớn |

⚠️ **Đính chính một con số của báo cáo trước.** Báo cáo `lag_hard_adv_gate_2ty_20260804.md` §6 viết
"ở NAV 50B, LAG_HI ≈ 3,25B (10% × 65% × 50B)". Con số đó dùng **trọng số allocator** `w_LAG=0,65`.
Nhưng engine mô phỏng sổ LAG trên **sổ cái tham chiếu riêng** `LAG_NAV = TOTAL_NAV/2 = 25B`
(`pt_v23_audit_2014.py:57`), rồi allocator mới phủ lên sau. Slot **engine** tại t=0 là
**2,5B**, không phải 3,25B. Sai số này không đổi kết luận nào của báo cáo trước (nó không dùng số
đó để chạy gì), nhưng mọi phép tính executability phải dùng đúng cơ sở.

**Tham số hoá gọn lại thành MỘT hệ số** — dễ đọc dose-response và tránh nhầm hai trục:

```
required_ADV = K × slot_size_vnd ,   K = 1 / (fill_pct_per_session × N_sessions)
```

| K | = f × N | Ý nghĩa |
|---|---|---|
| **1,00** | 20% × 5 | **chính mô hình engine tự nói là fill được** (`LIQ_LAG` nguyên văn) |
| 2,59 | 3,86% × 10 | neo fill LIVE, cửa sổ rộng 10 phiên |
| **5,18** | 3,86% × 5 | **neo fill LIVE, đúng `max_fill_days=5` của engine** ← chân chính |
| 12,95 | 3,86% × 2 | neo LIVE, cửa sổ ngắn 2 phiên |
| 44,4 | 0,45% × 5 | neo **chỉ-sổ-LAG** (T4: sổ LAG thật chỉ xác nhận tới 0,45%ADV) |

**Neo 3,86% phải gắn nhãn xuất xứ** (`research/lag_fidelity_decomp_20260803/T4_RESULTS.md` §2):
nó đến từ **sổ CAPIT** (NCT 07-21), **không** phải sổ LAG. Sổ LAG thật chỉ có **N=2 sự kiện**, lớn
nhất **0,45%ADV**. Dùng 3,86% cho LAG hợp lệ về cơ chế (engine áp **cùng** trần 20%ADV cho mọi sổ)
nhưng là **suy rộng liên-sổ** — đó chính là lý do chân K=44,4 tồn tại trong thang liều.

## 1. Thiết kế phép thử

**Điểm chèn = `simulate_holistic_nav.py:1148`**, NGAY SAU khi engine tính `target_value` và **TRƯỚC**
khối JIT-bán-parking. Lý do đặt trước khối JIT: nếu không định vào lệnh thì cũng không được bán
parking để lấy tiền cho nó (nếu đặt sau, engine đã bán ETF cho một lệnh rồi mới bỏ → tự tạo churn).
Ngữ nghĩa `continue` tại first-fill = **loại hẳn ứng viên**, giống hệt cách engine đang xử lý ca
vượt trần tầng/ngành (`:1035`, `:1070`) — không tự chế cơ chế mới.

- **Phạm vi**: chỉ `play_type` bắt đầu bằng `LAG_`. **KHÔNG** đụng CAPIT trong cùng sổ, **KHÔNG**
  đụng book BAL. Đúng phạm vi câu hỏi.
- **FAIL-CLOSED**: thiếu key ADV hoặc ADV≤0 ⇒ loại (mirror ngữ nghĩa `cap_lag_orders`). ⚠️ Hệ quả
  **bắt buộc phải đọc kỹ**: gate này **bao hàm** `LIQ_ZERO_BLOCK` ⇒ mọi so sánh với chân
  `production` sẽ **thừa hưởng nguyên vẹn** hiệu ứng ADV>0 đã biết (+3,85pp, đã dán nhãn KHÔNG
  được trích như edge). **Phép so quyết định là vs chân L1**, không phải vs pin.
- **Engine = BẢN SAO nghiên cứu** `exp_lag_dyngate_20260804/simulate_holistic_nav.py`, khác
  production **đúng 2 khối** (khai báo knob + gate), **no-op khi `LAG_EXEC_GATE_K=0`**.
  `pt_v23_audit_2014.py` **KHÔNG bị sửa** — nạp qua `run_leg.py` pre-seed `sys.modules`
  (bài học `run_jit.sh` 2026-08-03: `PYTHONPATH` thua `sys.path.insert(0, WORKDIR)` ⇒ ablation im
  lặng thành no-op; launcher có `assert` cứng, in ra đường dẫn module thật + K thật mỗi lần chạy).
- **Môi trường pin** (skill §3): snapshot `data/bq_cache_asof20260729_postrestate`,
  `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`, lệnh pin R3 nguyên văn, `EXP_TAG` mọi chân ⇒ **không đụng CSV
  canonical** (§8). `LAG_ADV_BASIS=price` = mặc định production.
- **Self-check 0 VND**: `[selfcheck BAL]` và `[selfcheck LAG]` = 0 VND trên **cả 12 chân**, `EXIT=0`.

**Điều kiện hợp lệ đăng ký trước — ĐẠT:**

| Chân đối chứng | Kỳ vọng | Thực đo | Khớp |
|---|---|---|---|
| `K=0`, `LIQ_ZERO_BLOCK=""` @50B | pin R3 **28,86 / 1,90 / −17,8 / 1,62 / 1.178,01B** | **y hệt** | ✅ từng chữ số |
| `K=0`, `LIQ_ZERO_BLOCK=lag` @50B | **32,71 / 1,95 / −19,1 / 1,71 / 1.699,09B** | **y hệt** | ✅ từng chữ số |

⇒ Đây là lần tái lập độc lập **thứ 4** của chân L1 32,71%, và harness tái lập pin chính thức bằng
một **đường nạp module khác hẳn** job trước (bản sao `shn` thay vì bản sao `pt_v23`) ⇒ mọi Δ dưới
đây là chênh lệch thật do đúng biến can thiệp.

## 2. Kết quả — 12 chân

### 2a. Thang NAV = 50 tỷ (so apple-to-apple với job trước)

| Chân | CAGR | Sharpe | MaxDD | Calmar | NAV cuối | vị thế mở | **bỏ dở** | **%bỏ** | deal xong | mã | vốn kẹt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ctrl = pin R3 | 28,86% | 1,90 | −17,8% | 1,62 | 1.178,0B | 1.498 | 848 | **56,6%** | 650 | 506 | 773,7B |
| **L1** (`LIQ_ZERO_BLOCK=lag`) | **32,71%** | 1,95 | −19,1% | 1,71 | 1.699,1B | 2.004 | 1.395 | **69,6%** | 609 | 557 | 2.305,9B |
| K=1,00 | 31,88% | 1,89 | −18,6% | 1,71 | 1.571,3B | 516 | 15 | **2,9%** | 501 | 136 | 116,5B |
| K=2,59 | 29,93% | 1,85 | −19,1% | 1,57 | 1.305,2B | 328 | **0** | **0,0%** | 328 | 83 | 0 |
| **K=5,18** | 27,52% | 1,77 | −18,8% | 1,46 | 1.033,8B | 233 | **0** | **0,0%** | 233 | 63 | 0 |
| K=12,95 | 24,86% | 1,69 | −17,2% | 1,44 | 794,9B | 126 | **0** | 0,0% | 126 | 36 | 0 |
| K=44,4 | 21,97% | 1,62 | −16,5% | 1,33 | 593,6B | 28 | **0** | 0,0% | 28 | 10 | 0 |

### 2b. Thang NAV = 1 tỷ (≈ `active_nav` THẬT: SpaceX ~950tr, ZaloPay cỡ tương tự)

| Chân | CAGR | Sharpe | MaxDD | Calmar | NAV cuối | vị thế mở | **bỏ dở** | **%bỏ** | deal xong | mã |
|---|---|---|---|---|---|---|---|---|---|---|
| ctrl (production) | 25,90% | 1,67 | −17,7% | 1,46 | 17,64B | 795 | 200 | **25,2%** | 595 | 357 |
| **L1** (`LIQ_ZERO_BLOCK=lag`) | **32,13%** | 1,87 | −19,3% | 1,66 | 32,20B | 932 | 326 | **35,0%** | 606 | 374 |
| K=1,00 | 32,62% | 1,88 | −19,6% | 1,66 | 33,72B | 591 | 16 | **2,7%** | 575 | 223 |
| **K=5,18** | **33,75%** | **1,90** | −19,3% | **1,75** | 37,45B | 541 | **0** | **0,0%** | 541 | 181 |
| K=44,4 | 31,03% | 1,81 | −17,8% | 1,75 | 29,00B | 458 | **0** | 0,0% | 458 | 130 |

### 2c. Ba điều bảng trên nói — theo thứ tự quan trọng

**(1) Trọng tâm dispatch: vị thế kẹt bị xoá SẠCH, và đó là SỐ HỌC chứ không phải may rủi.**
Gate đòi `ADV_entry ≥ K × slot`; engine fill `0,20 × ADV` mỗi phiên trong tối đa 5 phiên và coi là
xong khi đạt 95%. Với K=5,18: khả năng fill ngay **phiên đầu** = `0,20 × 5,18 × slot = 1,04 × slot
> 0,95` ⇒ **không thể bỏ dở** trừ khi ADV sụp sau ngày vào lệnh. Đó chính là vì sao K≥2,59 cho
**đúng 0** vị thế bỏ dở, còn K=1,00 vẫn còn **15-16 ca** (K=1 nghĩa là phải dùng trọn 5 phiên,
biên bằng 0, nên chỉ cần ADV tụt một phiên là hụt). Cơ chế khớp số liệu ở **cả hai thang NAV** —
đây là quan hệ định danh, không phải kết quả thống kê cần p-value.

> Ghi chú đọc đúng đơn vị: "fill trong 1 phiên" ở trên là theo **mô hình engine 20%ADV**. Ở
> **live 3,86%ADV/phiên** thì cùng một mã K=5,18 fill trong **5 phiên**. Luật vẫn nhất quán — đó
> đúng là điều nó được thiết kế để bảo đảm.

**(2) `LIQ_ZERO_BLOCK` LÀM TỆ ĐI vấn đề kẹt vốn — chi tiết chưa từng đo trước đây.**
Chân L1 có **nhiều** vị thế bỏ dở hơn chân production (69,6% vs 56,6% @50B; 35,0% vs 25,2% @1B) và
vốn kẹt tăng **3×** (773,7B → 2.305,9B). Lý do cơ học: chặn nhóm ADV≤0 (vốn fill TRỌN trong 1 phiên
vì không bị trần) làm vốn dồn sang nhóm **đo được ADV nhưng mỏng**, và chính nhóm này mới bị bóp
20%/phiên rồi bỏ dở. ⇒ L1 mua **CAGR bằng cách đổi lấy một hồ sơ thi hành tệ hơn** — thêm một lý
do độc lập để không đọc +3,85pp của L1 như một "cải thiện".

**(3) Ở NAV 50B gate PHÁ giá trị, ở NAV 1B gate CẢI THIỆN. Không mâu thuẫn — đó là capacity.**
Số quyết định là bảng `required_ADV` trung vị theo năm (đo trên chính các ứng viên bị loại):

| | 2014 | 2017 | 2020 | 2023 | 2026 |
|---|---|---|---|---|---|
| **@NAV 50B**, K=5,18 | 14,0 tỷ | 23,4 tỷ | 33,7 tỷ | 94,9 tỷ | **209,3 tỷ** |
| **@NAV 1B**, K=5,18 | 0,34 tỷ | 0,69 tỷ | 1,04 tỷ | 4,67 tỷ | 12,98 tỷ |

Sổ cái tham chiếu LAG **compound 25B → 590B (23,6×)** trong mẫu. Gate tỉ-lệ-NAV vì thế **tự siết
23,6 lần** dọc mẫu, trong khi ADV của cổ phiếu VN thì không. Đến 2026 nó đòi **209 tỷ/phiên** — gần
như không mã nào đạt ⇒ K=44,4 chỉ còn **10 mã / 28 vị thế** trong 12,5 năm (chân suy biến, giữ lại
làm mốc, không đọc như một cấu hình).

⇒ **Hệ quả phải nói thẳng: chuỗi @50B KHÔNG đo "luật này tốt hay xấu", nó đo "chiến lược LAG đã
vượt sức chứa của chính rổ tên nó mua".** Đó là một phát hiện về **capacity**, và nó củng cố (không
mâu thuẫn) cảnh báo đang có trong `lag_liquidity_filter.py` + `kb/projects/lag-adv-filter-tracking.md`.
Nói cách khác: pin R3 28,86% @50B đạt được **nhờ mua những mã mà một tài khoản 50B không bao giờ
fill nổi** — 56,6% vị thế của chính chân pin bị bỏ dở.

## 3. Δ CAGR có bền không? — KHÔNG (giống hệt kết luận job trước, dù cơ chế khác hẳn)

Phép so **quyết định** = `K=5,18` vs **L1** ở thang NAV THẬT (1B). N khai đúng (skill §4): đơn vị
độc lập cho một Δ **mức danh mục** là **13 năm dương lịch**, không phải 3.522 lần loại ứng viên,
không phải 3.106 phiên NAV.

| | CAGR | Sharpe | MaxDD | Calmar | deal xong | vị thế bỏ dở |
|---|---|---|---|---|---|---|
| L1 @1B | 32,13% | 1,87 | −19,3% | 1,66 | 606 | 326 |
| K=5,18 @1B | **33,75%** | **1,90** | −19,3% | **1,75** | 541 (**−10,7%**) | **0** |
| **Δ** | **+1,62pp** | +0,03 | 0,0pp | +0,09 | −65 deal / 12,5 năm | −326 |

(Phần LOO dưới đây ghép CAGR từ tỷ suất **năm** nên chân "không bỏ" ra +1,53pp thay vì +1,62pp —
sai số làm tròn của phép ghép, không phải hai phép đo khác nhau. Mọi so sánh trong bảng LOO là
nội bộ nhất quán.)

- **Sign test: thắng 8/13 năm, P(X≥8 | p=0,5) = 0,291** ⇒ không có ý nghĩa trên tần suất.
- **LOO / bỏ-nhóm (ghép từ tỷ suất năm):** bỏ 2021 → +0,56pp; bỏ 2020 → +0,85pp; **bỏ 2020+2021 →
  −0,22pp (ĐỔI DẤU)**; bỏ 2014+2020+2021 → **−0,72pp**.
- 2 năm (2020 +10,77pp, 2021 +22,23pp) gánh gần trọn Δ — đúng chữ ký "reshuffle-luck" mà
  `kb/KNOWLEDGE.md` §8 cảnh báo, **y hệt** kết luận của gate tĩnh 2 tỷ.

**Nhưng có MỘT khác biệt thật so với gate tĩnh, phải ghi nhận:** thang liều ở đây **có dose-response
đơn điệu** (@50B: 31,88 → 29,93 → 27,52 → 24,86 → 21,97 khi K tăng; @1B có cực đại nội tại tại
K=5,18), trong khi gate tĩnh 2 tỷ có thang **phẳng** (biên độ 0,21pp từ 0,5→5 tỷ). Tức luật này
**có nội dung kinh tế riêng**; nó chỉ không có **edge lợi nhuận bền**.

## 4. Multiple-testing (skill §13)

**N_trials khai đầy đủ = 12 lần chạy engine**: @50B `{K=0, 1,00, 2,59, 5,18, 12,95, 44,4}` + chân
L1; @1B `{K=0, 1,00, 5,18, 44,4}` + chân L1. Họ dùng cho CSCV: 6 cấu hình @50B, 4 @1B.

| Họ | DSR (mọi chân) | PBO (CSCV, S=16, 12.870 tổ hợp) | median logit | khối suy biến |
|---|---|---|---|---|
| @50B, Ncfg=6, T=3.104 | 1,0000 | **0,301** | +0,288 | **0/16** |
| @1B, Ncfg=4, T=3.104 | 1,0000 | **0,299** | +0,405 | **0/16** |

- **DSR = 1,0 vô nghĩa để phân biệt ở đây** (đọc y như job trước): SR/quan sát của cả họ nằm trong
  0,098–0,115, DSR chỉ đang nói "chiến lược nền có Sharpe dương chắc chắn", **không** nói chân nào
  hơn chân nào.
- **PBO ≈ 0,30 < 0,5** ⇒ khác hẳn gate tĩnh (**PBO 0,916**). Đọc đúng: PBO thấp nói **thứ hạng cấu
  hình ổn định IS→OOS** — hệ quả trực tiếp của dose-response đơn điệu, **không** nói "edge có thật".
  Cấu hình xếp hạng ổn định vẫn có thể có Δ không bền theo năm, và §3 cho thấy đúng là như vậy.
- **Kiểm khối suy biến trước khi chạy** (bài học CAPIT navsize 07-31): 0/16 khối có sd≈0 hoặc NaN
  ở cả hai họ ⇒ CSCV hợp lệ.

## 5. Câu hỏi vận hành: ngưỡng THẬT hôm nay là bao nhiêu, và nó chặn ai?

Số học trực tiếp, không qua backtest (NEUTRAL, `w_LAG=0,65`, `LAG_HI=0,10`):

```
slot_live  = 0,95 tỷ (active_nav) × 0,65 × 0,10 = 61,7 triệu
required_ADV = 5,18 × 61,7tr = 0,32 tỷ/phiên      (f=3,86%, N=5)
```

Đối chiếu trên **chính rổ ứng viên LAG thật** (5.317 sự kiện tín hiệu 2014→nay, phân bố ADV lấy từ
`exp_lag_advgate_20260804/dropped_gate5000m.json`):

| Ngưỡng | Nguồn gốc con số | Ứng viên bị loại | % rổ |
|---|---|---|---|
| **0,32 tỷ** | **executability tại NAV THẬT hôm nay** | 2.401 | **45,2%** |
| 0,62 tỷ | như trên, biên an toàn 2× (K=10) | 2.673 | 50,3% |
| 1 tỷ | — | 2.904 | 54,6% |
| **2 tỷ** | đề xuất gate tĩnh (**đã NO-GO**) | 3.232 | 60,8% |
| **17 tỷ** | con số báo cáo trước, neo ở **NAV 50B** | >3.751 | **>70,5%** |

**Ba điều đọc ra:**
1. **Ngưỡng vận hành đúng hôm nay là ~0,32 tỷ, không phải 2 tỷ và tuyệt đối không phải 17 tỷ.**
   Gate tĩnh 2 tỷ **chặt hơn 6,3×** nhu cầu thật; 17 tỷ chặt hơn **53×**. Câu "2 tỷ vẫn lỏng hơn
   ~8 lần yêu cầu vận hành" ở báo cáo trước **chỉ đúng cho một tài khoản 50 tỷ** — áp vào tài khoản
   đang chạy thì **ngược dấu hoàn toàn**.
2. **Nhưng ngay cả ngưỡng "lỏng" 0,32 tỷ vẫn cắt 45,2% rổ** — vì đuôi ứng viên LAG cực mỏng
   (trong nhóm ADV<5 tỷ: phân vị 25 = **0,002 tỷ**, trung vị = 0,088 tỷ). Khoảng cách 0,32 → 2 tỷ
   chỉ thêm 15,6pp rổ, và job trước đã chứng minh **98% hiệu ứng CAGR nằm ở bước 0 → 0,5 tỷ**.
   ⇒ Về mặt tác động, gate động tại NAV thật và gate tĩnh 0,5 tỷ **gần như cùng một luật**.
3. **Gate động tự siết khi tài khoản lớn lên** — đó là ưu điểm thật so với số tĩnh: ở NAV 5 tỷ
   ngưỡng thành 1,7 tỷ, ở NAV 20 tỷ thành 6,7 tỷ, không cần ai nhớ chỉnh tay.

## 6. Đối chiếu với các finding liền kề (skill §12)

1. **Job `Taylor_20260804_080547` (gate tĩnh 2 tỷ, NO-GO)** — kết luận **không đổi**, và job này
   **đính chính một số của nó** (slot engine 2,5B chứ không 3,25B; "17 tỷ" chỉ đúng ở NAV 50B).
   Hai job hội tụ: cả hai đều KHÔNG có edge lợi nhuận bền; khác nhau ở chỗ luật động **có**
   dose-response và **có** một tác dụng cơ học đo được (xoá vị thế kẹt) mà luật tĩnh không có.
2. **`kb/projects/lag-adv-filter-tracking.md`** — mọi con số CAGR ở đây **thừa hưởng nguyên vẹn**
   2 mốc cứng **2026-12-15 / 2027-03-31**; **không trích như edge trước mốc**. Job này **bổ sung
   dữ liệu cho sổ đó**: mức fill cần theo dõi không phải một con số mà là **`size_ratio` so với
   slot đương thời**, và nó phải được ghi kèm NAV của phiên đó.
3. **`T4_RESULTS.md`** — neo 3,86% là **suy rộng liên-sổ từ CAPIT**; cận dưới riêng cho sổ LAG là
   **0,45%** (chân K=44,4). Nếu user muốn giữ kỷ luật "chỉ dùng bằng chứng của chính sổ LAG" thì
   ngưỡng hôm nay là **2,7 tỷ** chứ không phải 0,32 tỷ — **và khi đó gate tĩnh 2 tỷ lại gần đúng**.
   Đây là điểm cần user chọn, không phải điểm backtest quyết được.
4. **Docstring `lag_liquidity_filter.py`** — báo cáo này **không** tạo khoảng thay thế cho
   `[~27,2%; 31,3%]` (đã hết hiệu lực) và **không** đề xuất re-pin.

## 6.5. Bằng chứng MỚI cho câu hỏi treo 3 vòng "L1 là edge thật hay hiện vật fill?"

> Mục này thêm sau review quant-skeptic (khuyến nghị #1 của reviewer). **Đây là bằng chứng
> HẬU-KIỂM, không phải phép thử đăng ký trước** — 2 chân NAV=1B được chạy cho mục đích khác
> (kiểm ngưỡng ở thang tài khoản thật), quan sát dưới đây là sản phẩm phụ. Gắn nhãn đúng như vậy.

Giả thuyết đang treo (`results_registry.md`, quant-skeptic 2026-08-02): Δ của `LIQ_ZERO_BLOCK`
có thể chỉ là **hiện vật sức chứa** — sổ LAG 25B không fill nổi size mục tiêu của chính nó. Ba
vòng review trước không tách được vì 2 giả thuyết **để lại cùng một dấu vết trên CSV**.

Job này vô tình tạo ra **một trục tách mới: thu nhỏ sổ 25 lần** (`LAG_NAV` 25B → 0,5B). Áp lực
sức chứa giảm thấy rõ và **đo được**: tỷ lệ vị thế bỏ dở của chân production rơi **56,6% → 25,2%**.
Nếu Δ của L1 thuần tuý là hiện vật sức chứa thì nó phải **co lại** theo.

| | Δ CAGR của L1 so với production | tỷ lệ bỏ dở của chân production |
|---|---|---|
| Sổ LAG 25B (`NAV_TOTAL_B=50`) | **+3,85pp** (28,86 → 32,71) | 56,6% |
| Sổ LAG 0,5B (`NAV_TOTAL_B=1`) | **+6,23pp** (25,90 → 32,13) | 25,2% |

**Δ KHÔNG co lại — nó LỚN HƠN 1,6 lần ở sổ nhỏ hơn 50 lần, trong khi áp lực sức chứa giảm hơn
một nửa.** Đây là chứng cứ **nghịch chiều** với giả thuyết "thuần hiện vật sức chứa".

**Giới hạn — không được đọc quá:** (a) hậu-kiểm, N=2 điểm thang NAV; (b) cơ chế sinh hiện vật
(mã `liq≤0` **không bị trần** nên fill trọn tức thì) **không tắt** khi thu nhỏ NAV, chỉ giảm
tương đối ⇒ đây là trục **làm nhạt**, không phải trục **tắt hẳn**; (c) một quan sát cùng job lại
**thuận chiều** giả thuyết cũ: L1 làm hồ sơ thi hành **tệ đi** (bỏ dở 56,6%→69,6%, vốn kẹt ×3),
đúng dấu vết mà phe "hiện vật" dự đoán. ⇒ **KHÔNG đóng được câu hỏi treo**, nhưng lần đầu tiên có
một phép đo **phân biệt được** hai giả thuyết thay vì lại xác nhận cả hai.

**Đề xuất phép thử ĐĂNG KÝ TRƯỚC để đóng hẳn** (rẻ, tái dùng đúng harness này): quét `NAV_TOTAL_B`
∈ {1, 5, 10, 25, 50, 100} với/không `LIQ_ZERO_BLOCK` (12 chân). Giả thuyết "hiện vật sức chứa" dự
báo Δ **tăng đơn điệu theo NAV**; giả thuyết "edge thật" dự báo Δ **phẳng hoặc giảm**. Hai đường
cong khác dấu độ dốc ⇒ tách được. Ghi vào `kb/projects/lag-adv-filter-tracking.md` như việc kế.

## 7. Khuyến nghị

**KHÔNG wire vì lợi nhuận** (3 căn cứ độc lập): Δ vs L1 ở thang NAV thật đổi dấu khi bỏ 2020+2021
(−0,22pp); sign test 8/13 (p=0,291); ở thang 50B gate **phá** giá trị đơn điệu theo K.

**CÓ căn cứ để cân nhắc như một LUẬT VẬN HÀNH** — và luật này mạnh hơn đề xuất 2 tỷ ở 3 điểm:
(a) nó **xoá 100% vị thế kẹt-không-fill-nổi** bằng quan hệ định danh, không bằng thống kê;
(b) nó **tự scale theo NAV**, không cần chỉnh tay khi tài khoản lớn lên;
(c) nó **neo vào một đại lượng đo được** (`%ADV/phiên` fill thật) thay vì một con số mượn từ rổ CAPIT.

**Nếu user muốn đi tiếp, đề xuất cụ thể — và đây là đề xuất, CHƯA phải khuyến nghị wire:**
- Ngưỡng: `required_ADV = slot_live / (0,0386 × 5)`, tính lại mỗi phiên từ `active_nav` thật.
- Vị trí: **tầng ORDER** (`trading_bot/plan.py`, cạnh `cap_lag_orders`), **không** ở tầng tín hiệu —
  vì slot chỉ biết được khi đã có NAV live của phiên đó.
- Chế độ: **WARN_ONLY trước**, giống P0 buying-power shadow (`current_ops.md`) — ghi log ≥10 phiên
  thật rồi mới xét ACTIVE. Ở NAV hôm nay ngưỡng chỉ 0,32 tỷ nên số lệnh bị chạm dự kiến **rất ít**;
  đúng điều kiện để chạy shadow rẻ.
- **Việc user phải chốt, backtest không chốt thay được:** dùng neo **3,86%** (suy rộng từ CAPIT →
  ngưỡng 0,32 tỷ) hay **0,45%** (chỉ-sổ-LAG, N=2 → ngưỡng 2,7 tỷ). Chênh nhau **8,4 lần**.

**Chưa đụng production**: không sửa/commit file live nào. `git status` sạch trên
`simulate_holistic_nav.py`, `pt_v23_audit_2014.py`, `trading_bot/plan.py`, `lag_liquidity_filter.py`,
`trading_bot/due_diligence.py`. File duy nhất còn diff là
`deploy_golive_dt5g_v4/golive_recommend_v23.py` (`ETF_PARK {3: 0.7}→{3: 0.8}`) — **việc của job
khác cùng ngày**, không liên quan: backtest không import file này và mọi chân đặt `PARK_STATES="3:0.7"`
tường minh.

**Bước kế: quant-skeptic verify báo cáo này trước khi bất kỳ ai trích số.**

## 8. Hiện vật

`mike/agents/Taylor/exp_lag_dyngate_20260804/`:
`simulate_holistic_nav.py` (bản sao engine, diff **2 khối**) · `run_leg.py` (launcher pre-seed
`sys.modules` + assert cứng) · `run_leg.sh` · `analyze.py` · `dsr_pbo_dyngate.py` · `collect.py` ·
log **12 chân** (`n50_*`, `n1_*`) · `drops_*.json` (mọi lần loại: ticker/ngày/ADV/slot/required).
CSV audit: `data/v23_golive_audit_..._exp_n50_*_univpit.csv` và `..._exp_n1_*_univpit_nav1B.csv`.
CSV canonical `..._wtnamecap.csv` **KHÔNG bị đụng**.
