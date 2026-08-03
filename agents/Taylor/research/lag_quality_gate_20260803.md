# LAG book — có nên nâng "sàn chất lượng" của gate PEAD không?

**Job** `Taylor_20260803_015850` · 2026-08-03 · Taylor (quant)
**Câu hỏi gốc (user)**: plan ZaloPay 08-03 có lệnh mua DHD — thanh khoản quá mỏng (ADV ~55tr/phiên),
hệ số tài chính bình thường, ngoài `universe_pit`, chỉ lọt vì tín hiệu PEAD. Chiến lược LAG có nên
nâng chất lượng gate (chấp nhận ÍT DEAL hơn để đổi CHẤT LƯỢNG MUA cao hơn) không?

**TL;DR — 3 kết luận, xếp theo mức quan trọng:**

1. **KHÔNG nên thêm sàn thanh khoản 2 tỷ.** Đo ở tầng full-engine: sàn 2B cho **+3,59pp CAGR**, nhưng
   bộ lọc `ADV>0` **đã chạy live từ 07-21** cho **+3,85pp** — tức **nâng từ ">0" lên "≥2B" LỖ
   −0,26pp**. Bật cả hai cùng lúc ra **đúng bằng** bật riêng sàn 2B (1.658,89B vs 1.658,57B) ⇒ hai
   thứ là **CÙNG MỘT cơ chế**, không cộng dồn. Thêm nữa toàn bộ +3,85pp đó chính là đại lượng đã bị
   quant-skeptic chấm **INCONCLUSIVE 3 lần** (chưa tách được "edge thật" khỏi "hiện vật mô hình fill").
2. **Phát hiện quan trọng hơn câu hỏi gốc: `VVS` — mã BANNED VĨNH VIỄN + cờ forensic `exclude` — lọt
   qua TOÀN BỘ gate LAG tự động của đường live** và đang là ứng viên **LAG_HI** (release 2026-07-23,
   NP_R +342%). Lần 07-30 nó bị chặn **bằng tay** (DollarBill ghi "VVS=BANNED" trong plan note), không
   phải bằng cơ chế. Engine backtest CÓ `LAG_FORENSIC_GATE` (mặc định ON), đường live **không có gì**.
3. **Số pin R3 27,24% trong `results_registry.md` KHÔNG còn tái lập được trên code production hôm
   nay** — production hiện cho **28,86%**. Nguyên nhân đã truy ra chính xác: mặc định `LAG_ADV_BASIS`
   đổi `close` → `price` (08-02) mà registry chưa cập nhật. Chạy lại với `LAG_ADV_BASIS=close` tái lập
   pin **tuyệt đối cả 5 chỉ tiêu**.

---

## 0. Đính chính 3 tiền đề trong prompt dispatch (đọc code thật, skill §1)

| # | Mike nói | Thực tế | Ảnh hưởng |
|---|---|---|---|
| 1 | Gate LAG ở `deploy_golive_dt5g_v4/golive_recommend.py:159-169` | **SAI FILE.** Money-path là `golive_recommend_v23.py`, nó `import live_lag_candidates` từ **`lag_live_schedule.py:57`**. `golive_recommend.py` (Jun-21) là bản v4 cũ, không ai gọi. *Nội dung* gate thì Mike đúng: `NP_R≥15 & prior_n_good≥4 & pa_HL3≥5`. | Trung bình — kết luận không đổi |
| 2 | Universe LAG lấy từ `ticker_prune`; KHÔNG lọc thanh khoản ở tầng tín hiệu | **SAI cả hai vế.** Ứng viên LAG lấy từ `data/earnings_surprise_data.pkl` + `earnings_events_classified.csv`, **không đụng `ticker_prune`**. Và **CÓ** lọc thanh khoản tầng tín hiệu: `lag_filter_illiquid()` (`golive_recommend_v23.py:627`, live từ 2026-07-21). | **Lớn** — vế "sai tầng" không đúng |
| 3 | Backtest PEAD giả định sàn 2 tỷ/ngày | **SAI.** Không có sàn thanh khoản nào cho LAG trong backtest. Số `>= 2` ở `pt_v23_audit_2014.py:1198` là **pool CAPIT**, không phải LAG. (BAL có `liq >= 1e9` ở `signal_v11_sql.py:143`.) | **Lớn** — xem §5 |
| 4 | 2 tinh chỉnh trong harness có thể chưa lên live | **Đúng là chưa live** — nhưng lý do KHÔNG phải "quên": cả hai **đã đo ở full-engine rồi bị loại có chủ ý** (xem §3). | Đảo hướng kết luận |

> ⚠️ Tiền đề #3 đã lọt vào `orders_note` của plan ZaloPay 08-03 ("NGOÀI mô hình backtest (sàn 2B)").
> Quyết định SKIP DHD vẫn hợp lý vì lý do khác (xem §6), nhưng **lý do "sàn 2B của backtest" là sai**
> và nên sửa để không lan tiếp.

### Đường live LAG thực tế (đã verify từng dòng)
```
live_lag_candidates()  NP_R≥15 & prior_n_good≥4 & pa_HL3≥5     lag_live_schedule.py:57
  → lag_filter_illiquid()   loại ADV≤0 / dòng giá cũ >30 ngày   golive_recommend_v23.py:627
  → lag_filter_low_rating() loại 8L rating ≥4                   golive_recommend_v23.py:637
  → (tầng lệnh) cap_lag_orders()  trần 20%ADV × 1/N_account     trading_bot/plan.py:484
  → (tầng lệnh) filter_lag_rating_orders()  lưới an toàn P1
```
Hôm nay: 170 mã qualify → 21 bị loại vì thanh khoản → 65 bị loại vì rating → **84 sống sót**.

---

## 1. Môi trường & tính hợp lệ (skill §3, §7, §14)

- Snapshot đóng cứng `data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`.
- Lệnh pin R3 nguyên văn: `NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 … v23a none postbull 0 edge`.
- Engine dùng cho leg = **`pt_v23_lagqual_research.py`**, bản sao nghiên cứu (+27 dòng, **0 dòng bị xoá**)
  của `pt_v23_audit_2014.py` với 2 knob opt-in mặc định TẮT. **Production KHÔNG bị sửa** —
  `git status` sạch trên `pt_v23_audit_2014.py`, `golive_recommend_v23.py`, `lag_live_schedule.py`,
  `lag_liquidity_filter.py`. Mọi output có `EXP_TAG` nên không đè CSV pin nào (§8).
- **7/7 leg: `cash-flow identity max err = 0 VND` và `final NAV identity err = 0 VND`, cả 2 book.**
- **Kiểm chứng harness (2 chiều):**
  - `L0b` = chạy **file production** với đúng lệnh pin → **1.178,01B / 28,86%**, trùng `L0` (bản sao
    nghiên cứu, knob tắt) **tới từng đồng** ⇒ bản sao byte-tương đương production.
  - `L0c` = `LAG_ADV_BASIS=close` → **27,24% / 1,81 / −18,4% / 1,48 / 1.006,33B**, và IS 23,81% /
    OOS 30,46% — **khớp tuyệt đối** số pin registry (kể cả 2 số IS/OOS ghi trong mục re-pin 08-02).

### ⚠️ Registry drift phải xử lý riêng
Chân đối chứng đúng của **code production hôm nay** là **28,86%**, không phải 27,24%. Chênh
**+1,62pp** đến từ mặc định `LAG_ADV_BASIS` `close`→`price` (job `Taylor_20260802_163657`, giữ lại bởi
commit `0062aa0` hôm nay). Bằng chứng cơ học: tên file output của lần chạy pin **không có** tag
`_advprice`, của lần chạy hôm nay **có**. Mọi A/B dưới đây đo **so với 28,86%** (1 biến, cùng vintage,
nội bộ hợp lệ). **Khuyến nghị: re-pin registry hoặc ghi rõ số pin gắn với `LAG_ADV_BASIS=close`** —
việc này ngoài phạm vi job, không tự làm.

---

## 2. N thật của book LAG (skill §4)

- **5.319 event** đã qua gate LAG (2013-12 → 2026-06), **790 mã**.
- ⚠️ Nhưng chúng **cụm vào 50 quý công bố** — với bất cứ hiệu ứng nào tương quan trong mùa BCTC,
  **đơn vị độc lập thực tế ≈ 50, không phải 5.319**. Mọi t-stat dưới đây đều **cluster theo quý**.
- ⚠️ Và book LAG **quá tải ~6×**: engine chỉ vào ~1.652 lệnh / hoàn tất ~674 vị thế trên 5.319 ứng
  viên. Nghĩa là **hiệu ứng "chọn lọc" đo trên toàn bộ 5.319 ứng viên PHÓNG ĐẠI** cái thực sự tới
  được NAV — đây chính là lý do bắt buộc phải chạy tầng full-engine (§4), và là chỗ 2 tầng lệch nhau.

Baseline pool: mean `post_ret` (T+5 → T+30, đúng cửa sổ nắm giữ LAG) = **+4,23%**, median +1,37%,
hit 54,2%.

---

## 3. Hai tinh chỉnh trong harness: KHÔNG phải "có sẵn mà quên dùng"

Trả lời câu Mike coi là quan trọng nhất — **cả hai đã được đo ở full-engine và bị loại có chủ ý**,
comment ngay trong code production ghi rõ:

| Bộ lọc | Trạng thái | Bằng chứng (comment tại chỗ) |
|---|---|---|
| `d_NPR ≥ 0` (gia tốc lợi nhuận) | **Đã thử dạng HARD FILTER → bác** | `pt_v23_audit_2014.py:270`: *"contrast the rejected d_NPR HARD FILTER, job …121416, **−1,44pp FULL**"*. Chỉ bản **REORDER** (`LAG_FUND_DNPR`, ưu tiên cấp vốn trong cùng tier, không loại event nào) được giữ, vẫn OFF-default. |
| non-op (`NPM > 1,2×EBITM`) | **Đã đo → OFF** | `pt_v23_audit_2014.py:265`: *"OFF: audit showed **+0,44pp CAGR nhưng −2,2pp MaxDD** (concentration); not robust"*. |

Con số "+0,81pp OOS / Sharpe 1,34 vs 1,06" mà Mike trích là kết quả **tầng event-study**, không phải
tầng NAV — và đây đúng là ca sách giáo khoa của skill §6 ("2 tầng có thể mâu thuẫn"): tầng vị thế
+0,81pp, tầng full-engine **−1,44pp**.

**Tôi đo lại tầng vị thế trên pool hiện hành và cũng không tái lập được +0,81pp:**

| Bộ lọc | % rổ bị loại | Δ (giữ − loại) | IS 2014-19 | OOS 2020+ |
|---|---|---|---|---|
| `d_NPR≥0` (định nghĩa engine) | 26,5% | **+0,26pp** | −0,16 | +0,45 |
| `d_NPR≥0` (định nghĩa pkl) | 39,3% | **+0,40pp** | +0,60 | +0,35 |
| non-op | 24,9% | **+1,13pp** | +0,43 | +1,60 |

⇒ `d_NPR` ≈ nhiễu. non-op có thật nhưng nhỏ, và đã bị loại vì MaxDD.

---

## 4. Kết quả tầng FULL-ENGINE (phần quyết định)

Tất cả trên cùng vintage + cùng `LAG_ADV_BASIS=price` (= production hôm nay). Chân đối chứng = L0.
Số CAGR/Sharpe/MaxDD/Calmar đã **tự tính lại độc lập từ CSV thô** (`combined_nav`), khớp bản in.

| Leg | Cấu hình | CAGR | Sharpe | MaxDD | Calmar | **Δ CAGR** | IS 14-19 | OOS 20+ |
|---|---|---|---|---|---|---|---|---|
| **L0** | đối chứng (= production) | 28,86% | 1,90 | −17,8% | **1,62** | — | 27,09% | 30,48% |
| **L1** | + sàn ADV ≥ **2 tỷ**/phiên | 32,45% | 1,93 | −18,2% | 1,78 | **+3,59** | 27,38% | 37,29% |
| **L2** | + **FSCORE ≥ 5** | 29,59% | 1,94 | **−19,7%** | **1,50** | +0,73 | **26,12%** | 32,83% |
| **L3** | + `LIQ_ZERO_BLOCK=lag` (**ADV>0 — ĐÃ LIVE**) | 32,71% | 1,95 | −19,1% | 1,71 | **+3,85** | 27,22% | 37,96% |
| **L4** | **L3 + sàn 2 tỷ** (cả hai) | 32,45% | 1,93 | −18,2% | 1,78 | +3,59 | 27,46% | 37,21% |
| L0b | production repro (kiểm chứng) | 28,86% | 1,90 | −17,8% | 1,62 | 0,00 | 27,09% | 30,48% |
| L0c | `LAG_ADV_BASIS=close` (= số pin) | 27,24% | 1,81 | −18,4% | 1,48 | — | 23,81% | 30,46% |

### 4.1 Sàn thanh khoản: KHÔNG cộng thêm gì — L4 ≡ L1

**L4 (cả hai bộ lọc) = 1.658,89B; L1 (chỉ sàn 2B) = 1.658,57B — lệch 0,02%.**
Cộng thêm `ADV>0` vào sàn 2B ra **đúng cùng một danh mục**, vì mọi mã ADV≤0 đã nằm trong nhóm <2B.
⇒ Đây là **một cơ chế duy nhất**, không phải hai lớp bảo vệ.

Và so trực tiếp **L3 (+3,85pp) vs L1 (+3,59pp)**: bộ lọc `ADV>0` **đang chạy live rồi** đã lấy hết
phần lợi; siết tiếp lên 2 tỷ **trả lại −0,26pp** trong khi cắt thêm ~1.200 event nữa.

> **Trả lời trực tiếp câu user hỏi**: đánh đổi "ít deal hơn để mua chất lượng hơn" ở trục thanh khoản
> **đã được thực hiện xong rồi** (07-21, ở đúng tầng tín hiệu). Siết thêm chỉ mất đa dạng hoá, không
> được gì.

### 4.2 ⚠️ Và ngay cả +3,85pp đó cũng KHÔNG được coi là edge (skill §12 — đối chiếu phát hiện cũ)

Đây là **cùng một đại lượng** đã bị quant-skeptic chấm **INCONCLUSIVE**, lần thứ ba, ngày hôm qua
(`mike/logs/verify_20260802_173456.log`, job `Taylor_20260802_175754`). Chưa tách được:
- **(A) edge thật** — vốn không kẹt ở mã không mua được nên chảy sang event LAG kế tiếp; hay
- **(B) hiện vật mô hình fill** — sổ 25B đơn giản **không fill nổi** mã LAG mỏng ở quy mô này.

Dấu vân tay của (B) hiện rõ ngay trong leg của tôi: **toàn bộ lợi ích nằm ở OOS** (L1: IS +0,29pp /
OOS **+6,81pp**). Pool ứng viên OOS lớn gần gấp đôi IS (3.439 vs 1.880 event) ⇒ mức quá tải vốn OOS
nặng hơn hẳn ⇒ **hiệu ứng vận tốc-vốn phải mạnh hơn ở OOS đúng như quan sát**. Nói cách khác dữ liệu
của tôi **phù hợp với giả thuyết (B)** ít nhất ngang với (A). Vì `LIQ_ZERO_BLOCK` mặc định vẫn để
opt-in (`""`) đúng theo kỷ luật INCONCLUSIVE, **không được trích +3,85pp làm cơ sở kỳ vọng.**

### 4.3 Sàn FSCORE ≥ 5: BÁC
Tầng vị thế trông tốt nhất trong nhóm cơ bản (+1,21pp, 11/13 năm dương, dương cả 2 nửa). Nhưng tầng
full-engine: **CAGR +0,73pp nhưng MaxDD xấu đi −1,9pp (−17,8→−19,7%) và Calmar TỤT 1,62→1,50**, **IS
âm −0,97pp**. Ladder ngưỡng cũng không đơn điệu (§10) — đỉnh đúng ở ≥5 rồi tụt (≥4: +0,80 / ≥5:
+1,21 / ≥6: +0,92 / ≥7: +0,65), dấu hiệu chọn ngưỡng theo dữ liệu. **Không đề xuất.**

---

## 5. Các sàn chất lượng cơ bản khác — tầng vị thế (đều BÁC)

Cluster theo quý công bố (n≈50), LOO theo năm:

| Sàn | % loại | Δ | IS | OOS | Năm dương | t (cluster quý) | Kết luận |
|---|---|---|---|---|---|---|---|
| ADV ≥ 2 tỷ | 61,2% | +1,86 | **−0,18** | +2,52 | 8/13 | +2,30 | Xem §4.1 — **không thêm gì so với live** |
| **Debt_Eq ≤ 1,0** | 50,6% | **−0,65** | −0,94 | −0,65 | **6/13** | −1,63 | **BÁC — trần đòn bẩy GÂY HẠI**, âm cả 2 nửa, mọi ngưỡng (1,5/1,0/0,6) |
| ROE5Y ≥ 10% | 47,1% | +0,65 | **+1,45** | **+0,35** | — | — | **BÁC — hình IS-overfit** (≥5%: IS +1,97 / OOS **−0,56**; ≥15%: IS +1,41 / OOS **−0,31**) |
| Golden floor (ROE_Min3Y≥0 ∧ CF_OA_3Y>0) | 36,4% | +0,03 | +0,88 | −0,27 | — | — | BÁC — bằng 0 |
| FSCORE ≥ 5 | 26,5% | +1,21 | +1,94 | +0,90 | 11/13 | +1,92 | Tốt nhất ở tầng này nhưng **chết ở tầng engine** (§4.3) |
| non-op | 24,9% | +1,13 | +0,43 | +1,60 | 11/13 | +1,98 | Đã bị loại vì MaxDD (§3) |

**Điểm đáng chú ý nhất cho user**: đề xuất (d) trong prompt — trần D/E — là bộ lọc **duy nhất có dấu
ÂM ổn định**: âm ở IS, âm ở OOS, âm ở mọi ngưỡng, chỉ 6/13 năm dương. Trực giác "công ty ít nợ thì
PEAD đáng tin hơn" **không đúng với dữ liệu VN**. D/E của DHD = 0,94 dù sao cũng đã lọt trần 1,0.

Sàn thanh khoản còn có **rủi ro chế độ** ít ai để ý: Δ âm 2014-2016 (−1,8/−2,2/−2,2pp), dương
2017-2024, rồi **âm trở lại 2025 (−2,18pp) và 2026 (−3,51pp)** — tức **2 năm gần nhất, mã mỏng lại
chạy TỐT HƠN**.

---

## 6. Ca DHD cụ thể (§4 của prompt) — xác nhận trực tiếp, không suy đoán

Số thật, `tav2_bq` (2026-07-31): `Volume_3M_P50` = **2.200 CP**, `Price` = 26.700đ →
**ADV = 58,7 triệu/phiên** (Mike ước 55tr — khớp).

| Bộ lọc | DHD có bị loại? |
|---|---|
| (a) sàn thanh khoản ≥ 2 tỷ | ✅ **CÓ** — 58,7tr = 2,9% ngưỡng (loại ở mọi ngưỡng ≥0,2 tỷ) |
| (b) `d_NPR ≥ 0` | ❌ **KHÔNG** — d_NPR = +0,060 (tăng tốc: YoY 32,9% quý này vs 26,9% quý trước) |
| (c) non-op | ❌ **KHÔNG** — NPM 8,29% < 1,2×EBITM (13,0%); lợi nhuận là **hoạt động cốt lõi**, không one-off |
| (d) trần D/E ≤1,0 | ❌ KHÔNG (0,94) · ROE5Y ≥10% → CÓ (8,94%) · golden floor → KHÔNG (ROE_Min3Y 7,7%>0, CF_OA_3Y +109 tỷ>0) · **FSCORE≥5 → KHÔNG** (DHD FSCORE = 5) |
| gate 8L rating ≤3 (đang live) | ❌ KHÔNG — rating 3/5, pass |

⇒ **Chỉ sàn thanh khoản bắt được DHD.** Mọi sàn "chất lượng cơ bản" đều cho DHD qua — vì xét thuần
cơ bản DHD **không hề tệ**: lợi nhuận cốt lõi, đang tăng tốc, dòng tiền dương, ROE ổn định 7,7-8,9%.
Vấn đề của DHD **thuần tuý là thanh khoản**, không phải chất lượng.

**Phản chứng phải nói thẳng (§12):** DHD đã có **3 event LAG trong lịch sử pool**, lợi nhuận
**+11,88% / +10,28% / −3,45%** (trung bình **+6,2%**, cao hơn trung bình pool +4,23%). Một sàn 2 tỷ
áp hồi tố **sẽ đã chặn cả ba và làm mất tiền trên chính mã này**. Đây không phải lý do bỏ sàn — nhưng
là bằng chứng cụ thể rằng "mỏng" ≠ "kém".

**Vì sao SKIP DHD hôm 08-03 vẫn ĐÚNG (bằng lập luận khác):** trần 20%ADV bóp lệnh xuống **200 CP =
27,2% slot target**. Engine mô phỏng dùng **`min_fill_pct = 0.30`** (`simulate_holistic_nav.py:354`) —
lệnh fill dưới 30% sau `max_fill_days` bị **ABANDON**. Tức **27,2% nằm DƯỚI ngưỡng chính backtest đã
giả định**: đây là một vị thế mà mô hình pin **không bao giờ giữ**. Lý do đúng để bỏ là *"không đạt
ngưỡng fill tối thiểu của mô hình"*, **không phải** *"ngoài sàn 2B của backtest"* (không tồn tại).

---

## 7. ⚠️ Phát hiện ngoài phạm vi câu hỏi — nhưng khẩn hơn: lỗ hổng BANNED/forensic ở đường live

Rà rổ ứng viên LAG **sống** hôm nay (84 mã qua hết mọi gate tự động):

| Mã | Trạng thái | Qua được gate live? |
|---|---|---|
| **VVS** | **BANNED vĩnh viễn** (`kb/KNOWLEDGE.md`) **VÀ** `forensic_flags.csv` severity=`exclude` (pump_no_moat, +6,5× trong 15 tháng, bẫy cheap-yield-on-peak-earnings) | ✅ **QUA HẾT** — LAG_HI, release 2026-07-23, NP_R +342% |
| **BFC** | `forensic_flags.csv` severity=`exclude` (no-moat NPK, peak earnings đang lăn xuống) | ✅ **QUA HẾT** |
| KLB, L40 | forensic `exclude` | ❌ bị gate 8L rating chặn (may, không phải thiết kế) |
| HSG | BANNED | ❌ bị gate 8L rating chặn (may) |

**Cơ chế:** `forensic_flags.csv` chỉ được đọc bởi **backtest** (`LAG_FORENSIC_GATE=1`, mặc định ON).
Đường live: grep `forensic|BANNED|banned` trong `golive_recommend_v23.py` + `lag_live_schedule.py` →
**0 kết quả**. `anomaly_excluded()` **chỉ áp cho pool CAPIT** (`golive_recommend_v23.py:702`, nằm trong
nhánh `if capit_size > 0.005`). `due_diligence.py` **cố ý thuần thông tin, không chặn**.

**Đã xảy ra chưa?** Chưa mất tiền: plan 07-30 ghi *"LAG T+1: PCT/VVS/XPH đều bị loại (**VVS=BANNED**,
PCT/XPH ADV~0)"* — **DollarBill chặn bằng tay**. Tức lớp phòng thủ hiện tại là **trí nhớ của người/
LLM lập plan**, không phải cơ chế. Đúng y hệt loại lỗ hổng mà P1 `filter_lag_rating_orders` đã được
xây để vá ("gate cũ chỉ sống ở tầng sinh tín hiệu").

**Sắc thái phải nói cho đúng:** trong cửa sổ backtest (`AUDIT_END=2026-06-19`) gate forensic drop **0
event** (cờ ghi ngày 2026-06-20, sau đó) — nên **số pin R3 không hề phụ thuộc gate này**. Lỗ hổng là
**thuần hướng tới tương lai**, và VVS là ca đầu tiên nó cắn.

**Đề xuất (KHÔNG tự sửa — cần user duyệt):** thêm `lag_filter_forensic_banned()` song song với
`lag_filter_low_rating()` đã có, đọc `data/forensic_flags.csv` (severity=`exclude`, date-aware) + danh
sách BANNED. Đây là **cổng an toàn/quản trị, không phải tham số tối ưu lợi nhuận** — nên DSR/PBO không
áp dụng, và nó **không đổi một chữ số nào** của số pin (0 event trong cửa sổ).

---

## 8. Ảnh hưởng LIVE nếu vẫn muốn áp sàn thanh khoản (để user cân)

Trên đúng 84 ứng viên LAG sống hôm nay:

| Ngưỡng | Số mã bị loại thêm |
|---|---|
| ADV < 0,5 tỷ | 39/84 = 46,4% |
| ADV < 1 tỷ | 42/84 = 50,0% |
| **ADV < 2 tỷ** | **50/84 = 59,5%** |
| ADV < 5 tỷ | 56/84 = 66,7% |

Median ADV của rổ = **0,98 tỷ/phiên**. Mỏng nhất: **AMC 502 nghìn đồng/phiên**, SD2 615 nghìn, PCT
1,03 triệu. **Tất cả đều qua bài kiểm tra `ADV>0` hiện hành** — cho thấy `>0` gần như không phải bộ
lọc, dù §4.1 nói nó đã lấy hết phần lợi ở tầng NAV.

**Nếu user vẫn muốn siết**, khuyến nghị của tôi **không phải sàn ADV tuyệt đối** (engine nói ~0 lợi
ích) mà là **quy tắc de-minimis mirror đúng hằng số backtest đã giả định**: nếu trần 20%ADV khiến lệnh
không đạt **≥30% slot target** (`min_fill_pct=0.30`) thì **không đặt**, để vốn chảy sang event LAG kế
tiếp. Ưu điểm: (a) không phải tham số mới dò từ dữ liệu — nó **đã nằm trong mô hình pin**; (b) đúng
cơ chế `lag_filter_illiquid` tuyên bố muốn đạt; (c) tự loại DHD (27,2% < 30%) **bằng lý do đúng**;
(d) không cắt mù 59,5% rổ — mã mỏng nhưng slot nhỏ vẫn qua. **Cần backtest riêng trước khi wire** —
job này chưa đo nó.

---

## 9. Kỷ luật thống kê (§13) & việc CHƯA làm

- **N_trials**: 7 leg full-engine + ~20 biến thể ngưỡng ở tầng vị thế. **DSR/PBO KHÔNG áp dụng** vì
  **tôi không đề xuất wire cấu hình nào** — khuyến nghị là *giữ nguyên gate hiện tại* (§13 nói rõ:
  không có config được chọn thì bỏ qua DSR/PBO).
- **quant-skeptic**: chưa dispatch, vì không có đề xuất thay đổi production nào. **Nếu user muốn làm
  §7 (gate BANNED/forensic) hoặc §8 (de-minimis 30%)** thì phải qua quant-skeptic trước.
- **Chưa làm / còn mở**: (a) không đo được quy tắc de-minimis 30% (cần leg engine riêng); (b) confound
  (A) vs (B) ở §4.2 vẫn chưa tách — job này **không** đóng được nó, chỉ cung cấp thêm bằng chứng
  (gradient IS/OOS) nghiêng về (B); (c) registry drift §1 cần một quyết định re-pin riêng.

## 10. Khuyến nghị cuối

| # | Việc | Mức |
|---|---|---|
| 1 | **KHÔNG** thêm sàn thanh khoản 2 tỷ vào gate LAG — `ADV>0` live đã lấy hết phần lợi, siết thêm −0,26pp | Kết luận chắc (full-engine, self-check 0 VND) |
| 2 | **KHÔNG** thêm sàn FSCORE / ROE / trần D/E — D/E gây hại rõ, ROE là IS-overfit, FSCORE làm xấu Calmar | Kết luận chắc |
| 3 | **KHÔNG** bật `d_NPR` / non-op — đã bị loại có chủ ý từ trước, tôi tái lập được lý do | Kết luận chắc |
| 4 | **Vá lỗ hổng BANNED/forensic ở đường live LAG** — cần user duyệt | **Khẩn** (VVS đang sống trong rổ) |
| 5 | Cân nhắc quy tắc de-minimis `min_fill_pct=0.30` thay cho sàn ADV — **cần backtest trước** | Đề xuất, chưa đo |
| 6 | Re-pin registry hoặc chú thích số 27,24% gắn với `LAG_ADV_BASIS=close` | Vệ sinh dữ liệu |

**Về câu hỏi gốc của user — "nâng chất lượng gate, ít deal hơn nhưng mua tốt hơn?"**: hướng đi đúng,
nhưng dữ liệu nói **trục "chất lượng cơ bản" (ROE/đòn bẩy/FSCORE/gia tốc LN) không mang lại gì cho
LAG** — PEAD kiếm tiền từ *bất ngờ lợi nhuận + đà giá*, không từ chất lượng bảng cân đối, và ép chất
lượng vào chỉ cắt N. Trục **thanh khoản** thì có thật, nhưng phần lợi **đã thu xong từ 07-21**. Chỗ
gate LAG thực sự còn hở không phải "chất lượng cơ bản" mà là **quản trị**: một mã BANNED lọt tới sát
lệnh mua và chỉ được cứu bằng trí nhớ của người lập plan.

---
**Artifact**: `mike/agents/Taylor/research/lag_quality_20260803/` (7 log + `run_leg.sh`),
engine nghiên cứu `pt_v23_lagqual_research.py`, CSV audit `data/v23_golive_audit_*exp_lagq_*.csv`.
