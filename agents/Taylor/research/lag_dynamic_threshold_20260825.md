# Sàn thanh khoản LAG — ĐỘNG vs TĨNH: **NO-GO cho cả 3 biến thể, giữ nguyên 2 tỷ cứng**

- **Job:** `Taylor_20260825_094721` · 2026-08-25 · Taylor
- **Prereg:** `lag_dynamic_threshold_prereg_20260825.md` (ghi TRƯỚC mọi chân backtest)
- **Trạng thái:** research paper-only. **KHÔNG wire.** `git status` trên `pt_v23_audit_2014.py`,
  `lag_liquidity_filter.py`, `signal_v11_sql.py`, `simulate_holistic_nav.py` **SẠCH** — engine dùng
  là **bản sao nghiên cứu** `exp_lag_advdyn_20260825/pt_v23_advdyn.py`.

> **KẾT LUẬN 1 DÒNG.** Không biến thể động nào đạt nổi **1/3 điều kiện** của quy tắc quyết định đã
> khoá trước (|ΔCAGR OOS| lớn nhất = **0,29pp** so với ngưỡng cần ≥1,0pp; p nhỏ nhất trong cả rổ 9
> test = **0,421** so với ngưỡng BH 0,0056; **mọi** biến thể lật dấu dưới LOO). **Nhưng câu hỏi
> "sàn danh nghĩa có bị xói mòn không" thì có câu trả lời thật, và nó KHÔNG đến từ backtest:**
> sàn 2 tỷ chặn **70,6% ứng viên LAG năm 2014 → 65,0% năm 2026** (Spearman ρ=−0,764, **p=0,002**)
> — xói mòn **có thật nhưng nhỏ (~0,47pp/năm)**, và **đã dừng**: trong riêng OOS 2020–2026,
> ρ=**0,000**, p=**1,000**.
>
> **Phát hiện đáng giá nhất của cả job lại nằm ở biến thể C:** sàn 2 tỷ **không phải ràng buộc
> capacity ở bất kỳ thang NAV nào** — nó **sai cả hai chiều**. Tại NAV THẬT đang chạy (SpaceX
> **980,2tr**, ZaloPay **958,3tr**, 2026-08-24), capacity chỉ đòi **ADV ≳ 0,33 tỷ** ⇒ 2 tỷ **chặt
> hơn ~6,1×** nhu cầu thật. Tại NAV 50B, capacity đòi **16,84 tỷ** ⇒ 2 tỷ **lỏng hơn ~8,4×**.

---

## §0 — Trả lời trực tiếp câu hỏi của dispatch

| Câu hỏi | Trả lời |
|---|---|
| Sàn 2B danh nghĩa cứng có bị xói mòn khi thanh khoản thị trường tăng không? | **CÓ, nhưng nhỏ và đã dừng.** 70,6%→65,0% tỷ lệ chặn trong 12 năm (ρ=−0,764 p=0,002); trong OOS 2020+ **không còn xu hướng nào** (ρ=0,000 p=1,000). Đây là **bước nhảy mức** giữa thời kỳ 2014-19 và 2020+, không phải trôi liên tục đang tiếp diễn |
| Thang liều tĩnh [1B…4B] có điểm gãy không? | **KHÔNG.** Biên độ CAGR toàn dải = **0,34pp**, OOS = **0,37pp**. Xác nhận lại kết luận 08-04 |
| Biến thể động nào đáng thay 2B? | **KHÔNG có biến thể nào.** Cả 9 test đều trượt cả 3 điều kiện |
| Sàn "đúng bản chất" theo capacity là bao nhiêu? | **0,33 tỷ** ở NAV thật · **16,84 tỷ** ở NAV 50B · **67,36 tỷ** ở NAV 200B (X=3,86%). Tức nó **giãn tuyến tính theo NAV** trong khi 2B đứng yên |
| BAL có cùng vấn đề không? | **Không đo được xói mòn có ý nghĩa** (ρ=−0,24 p=0,43 ở sàn 1B; ρ=−0,41 p=0,17 ở 2B) |
| Công thức ADV cho BAL có cần khác vì hold 45 phiên vs 25 phiên? | **KHÔNG** — và lý do khác trực giác của dispatch: **cả hai book dùng `max_fill_days=5` y hệt nhau**. `hold_days` quyết định khi nào THOÁT, không quyết định cửa sổ VÀO |

## §1 — Điều kiện hợp lệ đăng ký trước: **ĐẠT toàn bộ**

| Kiểm | Kỳ vọng | Thực đo | |
|---|---|---|---|
| Chân control (`mode=static`, min=0) | pin R3 **28,86 / 1,90 / −17,8 / 1,62 / 1.178,01B** | **28,86 / 1,90 / −17,8 / 1,62 / 1.178,01B** | ✅ từng chữ số |
| `[selfcheck BAL]` + `[selfcheck LAG]` | 0 VND | 0 VND trên **cả 11 chân**, `EXIT=0` cả 11 | ✅ |
| Tái lập độc lập job `Taylor_20260804_080547` | static 1,0B = 32,41 (IS 27,58 / OOS 37,02); static 2,0B = 32,44 (IS 27,52 / OOS 37,12) | **trùng từng chữ số cả 6 con số** | ✅ |

⇒ Đây là **lần tái lập độc lập thứ 3** của harness ADV-gate. Mọi Δ dưới đây là chênh lệch thật do
đúng biến can thiệp.

**Môi trường pin:** snapshot `data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`,
`$DNA_PYEXE`, lệnh pin R3 nguyên văn (`NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap
BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19 … v23a none postbull 0 edge`),
`LAG_ADV_BASIS=price`, `EXP_TAG` mọi chân ⇒ **không đụng CSV canonical** (§8 coding_guidelines).

**Engine khác production đúng 3 khối** (khai báo knob `LAG_ADV_MIN_MODE` / điểm chèn gate / dump
danh sách bị loại+giữ lại), **no-op hoàn toàn** khi `mode=static, LAG_ADV_MIN_VND=0` — chứng minh
bằng chính chân control tái lập pin từng chữ số.

## §2 — BƯỚC 1: sweep ngưỡng TĨNH (H1)

| Ngưỡng | CAGR Full | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | ΔOOS vs 2B | n chặn |
|---|---|---|---|---|---|---|---|---|---|
| control ADV=0 | 28,86% | 1,90 | −17,8% | 1,62 | 1.178,01B | 27,09% | 30,48% | −6,64pp | 0 |
| 1,0 tỷ | 32,41% | 1,92 | −18,3% | 1,77 | 1.652,88B | 27,58% | 37,02% | −0,11pp | 2.905 |
| 1,5 tỷ | 32,40% | 1,93 | −18,3% | 1,77 | 1.650,54B | 27,66% | 36,90% | −0,22pp | 3.108 |
| **2,0 tỷ (baseline)** | **32,44%** | **1,93** | **−18,2%** | **1,78** | **1.656,39B** | **27,52%** | **37,12%** | **—** | **3.234** |
| 3,0 tỷ | 32,10% | 1,90 | −18,2% | 1,76 | 1.604,90B | 27,00% | 36,97% | −0,15pp | 3.470 |
| 4,0 tỷ | 32,38% | 1,92 | −18,3% | 1,77 | 1.648,14B | 27,26% | 37,27% | +0,15pp | 3.646 |

**H1₀ KHÔNG bác được.** Toàn dải 1,0→4,0 tỷ nằm gọn trong **0,34pp CAGR**. Bước 0 → 1,0 tỷ vẫn ăn
**3,55pp/3,58pp ≈ 99%** toàn bộ hiệu ứng (đuôi ADV≈0), đúng như 08-04.

**LOO theo năm** (bỏ từng năm 2014…2026, Δ CAGR vs 2B): dấu **LẬT** ở 1,0B (−0,12…+0,17),
1,5B (−0,09…+0,10), 4,0B (−0,16…+0,27). Ngoại lệ duy nhất có dấu ổn định là **3,0 tỷ — và nó ÂM
mọi năm** (−0,23…−0,50pp), tức ngưỡng duy nhất "nhất quán" trong dải lại là ngưỡng **xấu hơn** 2B.
Chi tiết: `exp_lag_advdyn_20260825/loo_delta.csv`.

## §3 — BƯỚC 2A: deflate lạm phát 7%/năm

`sàn(t) = 2e9 × 1,07^((t − 2026-08-10).days / 365)`

| Năm | 2008 | 2012 | 2016 | 2020 | 2026 |
|---|---|---|---|---|---|
| Sàn | 0,587B | 0,769B | 1,009B | 1,322B | 1,985B |

| | CAGR | Sharpe | MaxDD | Calmar | NAV | IS | OOS | ΔOOS | p (BH) |
|---|---|---|---|---|---|---|---|---|---|
| A inflate 7% | 32,47% | 1,93 | −18,3% | 1,77 | 1.661,24B | 27,54% | 37,16% | **+0,04pp** | **0,699** |

**NO-GO.** +0,03pp CAGR / +0,04pp OOS = nhiễu; p=0,699; dấu lật dưới LOO. Chỉ **thả ra 173** ứng
viên trong 12,5 năm và **chỉ ở quá khứ** (không chặn thêm ai) — đúng theo cấu tạo của hàm mũ.

⚠️ **Đúng như prereg §5 R3 đã cảnh báo:** A sinh xu hướng đơn điệu **theo cấu tạo**. Mọi "phát hiện
xói mòn" ở A là **tautology**. A ở đây chỉ có giá trị như một **phép quy đơn vị**.

## §4 — BƯỚC 2B: percentile thị trường (`tav2_mike.universe_pit`)

**Phương pháp.** Mỗi phiên t: phân phối **chéo** của `ADV3T = Volume_3M_P50 × COALESCE(Price, Close)`
trên các mã `in_universe=True`; lấy percentile k; làm mượt **rolling-252-phiên median, backward-only**
(point-in-time). Chuỗi 2007-04-03 → 2026-08-24, **4.839 phiên**. Chưa đủ lịch sử ⇒ **fail-closed**.

### 4a. Calibration lộ ra một sai lệch trong chính đề bài

Dispatch đề xuất k = 20/25/30. **Cả ba đều cho sàn thấp hơn hẳn 2B ở MỌI năm.** Đo thật: tại
**2026-08-10, sàn 2 tỷ tương ứng percentile 43,1** của `universe_pit` — không phải 20-30.

| Sàn (tỷ VND) | 2008 | 2012 | 2016 | 2020 | 2024 | 2026 |
|---|---|---|---|---|---|---|
| k=20 | 0,25 | 0,20 | 0,41 | 0,98 | 0,83 | 0,70 |
| k=25 | 0,30 | 0,25 | 0,52 | 1,25 | 1,04 | 0,92 |
| k=30 | 0,35 | 0,31 | 0,68 | 1,55 | 1,33 | 1,18 |
| **k=43 (calib)** | 0,52 | 0,50 | 1,41 | 2,91 | 2,71 | 2,18 |

⇒ Đã **thêm chân k=43** để so apple-to-apple. Hệ quả bắt buộc khai báo: **m của BH tăng 8 → 9**
(prereg §4 yêu cầu đúng điều này — không được giữ m=8 rồi thêm test).

⚠️ Theo prereg §5 R4: calibrate là thao tác **quy đơn vị bắt buộc**, và **không** được trích
"k=43 khớp 2B hôm nay" như bằng chứng ủng hộ B — đó là lập luận vòng.

### 4b. Kết quả

| Chân | CAGR | Sharpe | MaxDD | NAV | IS | OOS | ΔOOS | p | n khác biệt vs 2B |
|---|---|---|---|---|---|---|---|---|---|
| B k=20 | 32,48% | 1,93 | −18,3% | 1.663,25B | 27,32% | 37,41% | +0,29pp | 0,487 | 512 |
| B k=25 | 32,43% | 1,92 | −18,3% | 1.654,74B | 27,35% | 37,27% | +0,15pp | 0,445 | 407 |
| B k=30 | 32,40% | 1,92 | −18,3% | 1.650,36B | 27,60% | 36,96% | −0,16pp | 0,590 | 292 |
| B k=43 | 32,40% | 1,93 | −18,3% | 1.651,51B | 27,50% | 37,08% | −0,04pp | 0,788 | 223 |

**NO-GO cả 4 mức k.** Biên độ CAGR 32,40–32,48 = **0,08pp**.

### 4c. Phát hiện có nội dung thật — **percentile KHÔNG khử được xói mòn**

Đây là phép thử duy nhất trong H2 không phải tautology (prereg §5 R3), và nó **bác luôn giả thiết
làm nền cho biến thể B**:

| | 2014 | 2026 | Spearman 2014-26 | Spearman OOS 2020-26 |
|---|---|---|---|---|
| **2B cứng** (tỷ lệ chặn ứng viên LAG) | 70,6% | 65,0% | ρ=**−0,764**, **p=0,002** | ρ=0,000, p=1,000 |
| **k=43 tự co giãn** | 69,1% | 67,8% | ρ=−0,429, p=0,144 | ρ=+0,107, p=0,819 |
| A inflate 7% | 66,5% | 64,7% | ρ=−0,533, p=0,061 | ρ=0,000, p=1,000 |

Hai điều đọc ra:
1. **Xói mòn của 2B là thật nhưng nhỏ và đã dừng.** −5,6pp tỷ lệ chặn trong 12 năm ≈ 0,47pp/năm.
   Trong OOS 2020-2026 **không còn xu hướng nào** (ρ=0,000). Chu kỳ nuốt trôi xu hướng thế kỷ:
   2021 chỉ chặn **42,5%**, 2022 **48,2%**, 2014 **70,6%** — biến thiên theo chu kỳ (±28pp) lớn
   **gấp 5 lần** toàn bộ độ trôi thế kỷ (5,6pp).
2. **Sàn percentile không phải phiên bản ổn định hơn của 2B.** Nó cũng trôi (69,1→67,8), và chênh
   lệch (k43 − 2B) **tăng theo thời gian** (ρ=**+0,718**, p=**0,006**, biên độ −5,4…+9,4pp). Tức
   đổi sang percentile chỉ là **đổi một cách trôi này lấy một cách trôi khác**, không phải khử trôi.

## §5 — BƯỚC 2C: sàn neo theo NAV và fill thật (capacity)

**Phép tính số học, KHÔNG phải phép thử thống kê** ⇒ không vào rổ BH (khai trước ở prereg §2 H3).

### 5a. Đính chính công thức của dispatch

Dispatch viết `slot = 8% × w_LAG × NAV`. Đúng cho **tầng LIVE** (allocator `STATE_LAG_WEIGHT`
= 0,65 ở NEUTRAL/BULL/EX-BULL, `golive_recommend_v23.py:100`), nhưng **sai cho ENGINE**: engine mô
phỏng sổ LAG trên **sổ cái tham chiếu riêng** `LAG_NAV = TOTAL_NAV/2` (`pt_v23_audit_2014.py:57`)
rồi allocator mới phủ lên. Và tier weight là **`LAG_HI 0,10` / `LAG_LO 0,08`** (`:1362`), không phải
8% cho cả hai. ⇒ Slot **engine** tại NAV 50B = **2,5B**, không phải 2,6B. *(Đính chính này đã được
ghi ở job `Taylor_20260804_085248` §0; tôi tái lập độc lập và xác nhận.)*

### 5b. `required_ADV = slot / (X% × 5 phiên)` — slot LIVE = 10% × 0,65 × NAV

| NAV | slot (tỷ) | X=3,86% (fill LIVE) | X=10% (bảo thủ) | X=20% (chính mô hình engine) |
|---|---|---|---|---|
| **THẬT hôm nay** — SpaceX 0,980B | 0,064 | **0,33** | 0,13 | 0,06 |
| THẬT — ZaloPay 0,958B | 0,062 | 0,32 | 0,12 | 0,06 |
| 50B (thang backtest pin) | 3,250 | **16,84** | 6,50 | 3,25 |
| 100B | 6,500 | 33,68 | 13,00 | 6,50 |
| 150B | 9,750 | 50,52 | 19,50 | 9,75 |
| 200B | 13,000 | 67,36 | 26,00 | 13,00 |

*Tái lập số của dispatch:* dùng đúng công thức dispatch (8% × 0,65 × 50B = 2,6B) cho **13,47 tỷ**
tại X=3,86% và **5,20 tỷ** tại X=10% — khớp "~13,5B / ~5,2B" trong đề bài. Bảng trên dùng
`LAG_HI 10%` nên cao hơn tương ứng.

### 5c. Kết luận C — **H3₀ BỊ BÁC**

**Sàn 2 tỷ sai CẢ HAI CHIỀU, tuỳ thang NAV:**

| | required_ADV | 2B là… |
|---|---|---|
| NAV THẬT đang chạy (~0,98B) | 0,33 tỷ | **chặt hơn 6,1×** nhu cầu thật |
| NAV 50B (thang backtest) | 16,84 tỷ | **lỏng hơn 8,4×** nhu cầu thật |

Số mã `universe_pit` qua được từng sàn (TB phiên tháng 8/2026, universe 358 mã):

| Sàn | ≥0,33B | ≥2B | ≥6,5B | ≥16,84B | ≥33,68B | ≥67,36B |
|---|---|---|---|---|---|---|
| Số mã | 325 | **204** | 141 | **101** | 69 | 47 |

⇒ Nếu deploy lên 50B, ràng buộc **thật sự binding** là capacity 16,84 tỷ → chỉ còn **101/358 mã
(28%)**. Nó đến **trước rất lâu** so với lúc sàn danh nghĩa 2B trở nên quan trọng.

⚠️ **Xuất xứ neo 3,86% phải mang theo:** con số đến từ **sổ CAPIT** (NCT 2026-07-21), **không phải
sổ LAG**. Sổ LAG thật chỉ có **N=2 sự kiện**, lớn nhất **0,45% ADV**
(`research/lag_fidelity_decomp_20260803/T4_RESULTS.md` §2). Dùng 3,86% cho LAG hợp lệ về cơ chế
(engine áp cùng trần 20%ADV cho mọi sổ) nhưng là **suy rộng liên-sổ**.

## §6 — BƯỚC 3: đối chiếu BAL

**Hai tầng sàn BAL:** (1) `signal_v11_sql.py:143` `WHERE liq >= 1e9` **cứng trong SQL** — file này
**dùng chung** với engine backtest đã pin (`pt_v23_audit_2014.py:48` import thẳng `SIGNAL_V11`), sửa
là lặng lẽ đổi nền R3; (2) tầng **LIVE 2e9** áp qua `lag_liquidity_filter.bal_filter_thin()`.

| Năm | ứng viên mua | ≥1B | ≥2B | % cắt @1B | % cắt @2B | 2B thêm vs 1B |
|---|---|---|---|---|---|---|
| 2014 | 805 | 350 | 269 | 56,5% | 66,6% | +10,1pp |
| 2016 | 393 | 338 | 279 | 14,0% | 29,0% | +15,0pp |
| 2019 | 2.763 | 1.568 | 1.315 | 43,3% | 52,4% | +9,2pp |
| 2021 | 10.999 | 8.968 | 8.140 | 18,5% | 26,0% | +7,5pp |
| 2022 | 384 | 235 | 211 | 38,8% | 45,1% | +6,2pp |
| 2025 | 7.079 | 5.353 | 4.658 | 24,4% | 34,2% | +9,8pp |
| 2026 | 2.353 | 1.514 | 1.403 | 35,7% | 40,4% | +4,7pp |

Đầy đủ 13 năm: `exp_lag_advdyn_20260825/bal_candidates_per_year.csv`.

**Câu hỏi 1 — cùng vấn đề danh nghĩa cứng?** Về nguyên tắc CÓ, nhưng **không đo được xói mòn có ý
nghĩa**: ρ=−0,242 (p=0,426) ở sàn 1B; ρ=−0,407 (p=0,168) ở 2B. Đối lập rõ với LAG (ρ=−0,764,
p=0,002). Lý do cơ chế: BAL chỉ bắn tín hiệu ở `state5 ∈ {3,4,5}` ⇒ số ứng viên biến thiên **384
(2022) → 10.999 (2021)** theo **chu kỳ thị trường**; chu kỳ nuốt trôi xu hướng thế kỷ. LAG là
event-driven theo lịch công bố BCTC nên mẫu đều hơn qua các năm.

**Câu hỏi 2 — công thức ADV có cần khác vì hold 45 vs 25 phiên?** **KHÔNG**, và lý do khác trực
giác của đề bài. Đọc code thật: **cả hai book dùng `max_fill_days=5` y hệt nhau**
(`LIQ_FULL` `:990`, `LIQ_LAG` `:1333`). `hold_days` (BAL 45 `:1940` / LAG 25 `:1992`) quyết định
khi nào **THOÁT**, không quyết định cửa sổ **VÀO**. Ràng buộc fill giống hệt ⇒ công thức không cần khác.

**Trục thật sự khác giữa hai book là tính CO GIÃN của cửa sổ vào lệnh, không phải độ dài nắm giữ.**
LAG bị trói vào T+5 sau release — lỡ cửa sổ là mất alpha (PEAD phân rã). BAL là tín hiệu
momentum/state tồn tại nhiều phiên liên tiếp và có thể tái phát ⇒ **có thể đợi thanh khoản**. Về
nguyên tắc điều này biện hộ cho **sàn LAG ≥ sàn BAL** — đúng chiều cấu hình hiện tại.

📌 *Quan sát ngoài phạm vi, ghi lại để người đọc sau không hiểu nhầm:* `signal_v11_sql.py:112` join
`tav2_bq.vnindex_5state` — đó là bảng **v3.4b BASE, KHÔNG phải DT5G** (bẫy đã ghi trong `CLAUDE.md`).
Đây là SQL backtest **đã pin**, đổi là đổi nền R3. **Không đề xuất sửa trong job này.**

## §7 — Hiệu chỉnh đa phép thử (BH FDR)

Block bootstrap trên chuỗi lợi suất **ngày OOS 2020+**, khối **21 phiên**, **10.000** lần, hai đuôi,
seed 20260825. **m = 9** (prereg đăng ký 8; +1 vì chân k=43 phát sinh từ calibration — khai báo theo
đúng prereg §4).

| Chân | ΔOOS (pp/năm) | p | rank | ngưỡng BH | qua? |
|---|---|---|---|---|---|
| static 1,5B | −0,162 | 0,421 | 1 | 0,0056 | ❌ |
| B k=25 | +0,109 | 0,445 | 2 | 0,0111 | ❌ |
| B k=20 | +0,211 | 0,487 | 3 | 0,0167 | ❌ |
| static 4,0B | +0,108 | 0,545 | 4 | 0,0222 | ❌ |
| B k=30 | −0,119 | 0,590 | 5 | 0,0278 | ❌ |
| static 3,0B | −0,112 | 0,633 | 6 | 0,0333 | ❌ |
| A inflate 7% | +0,031 | 0,699 | 7 | 0,0389 | ❌ |
| B k=43 | −0,033 | 0,788 | 8 | 0,0444 | ❌ |
| static 1,0B | −0,078 | 0,801 | 9 | 0,0500 | ❌ |

**0/9 qua.** p nhỏ nhất = 0,421 — không chỉ trượt BH mà còn **trượt cả α=0,05 thô**.

## §8 — Đối chiếu quy tắc quyết định đã khoá trước (prereg §3)

| Điều kiện | Ngưỡng | Kết quả tốt nhất đo được | Đạt? |
|---|---|---|---|
| 1. ΔCAGR OOS vs 2B | ≥ **+1,0pp** | **+0,29pp** (B k=20) | ❌ |
| 2. p sau BH | < 0,05 (thực tế 0,0056) | **0,421** | ❌ |
| 3. dấu Δ không lật dưới LOO | — | **lật ở mọi biến thể** (trừ 3,0B, mà nó âm) | ❌ |

⇒ **Cam kết công bố âm tính (prereg §7) được thực hiện: GIỮ NGUYÊN sàn 2 tỷ cứng.**

**Đánh nhãn `UNDERPOWERED` theo prereg §5 R1** — bắt buộc đọc kèm mọi Δ ở trên: vùng bị tác động là
băng ADV 0,1–2 tỷ = **1,6% vốn lịch sử**, **23 deal khớp** trong 12,5 năm, **n=8** ở OOS. Số ứng
viên **đổi kết cục gate** giữa các biến thể là 173–512, nhưng **~93% trong số đó không fill nổi**
(băng D, đo 08-10) ⇒ **n-event thực sự chạm NAV chỉ vài chục**. Mọi con số ΔCAGR trong báo cáo này
đều nằm **dưới nhiễu của chính engine**, và không được diễn giải theo hướng ủng hộ bất kỳ biến thể nào.

## §9 — Khuyến nghị

### 9.1 Khuyến nghị chính: **KHÔNG thay 2 tỷ cứng bằng bất kỳ biến thể động nào**

Ba lý do độc lập, không lý do nào dựa vào lý do kia:
1. **Không có tín hiệu** — 0/9 test qua BH, p nhỏ nhất 0,421, biên độ toàn bộ 11 chân = 0,38pp CAGR.
2. **Vấn đề mà sàn động hứa giải quyết thì gần như không tồn tại** — xói mòn 0,47pp/năm, và **đã
   dừng** trong OOS (ρ=0,000 p=1,000). Chu kỳ thị trường gây biến thiên gấp ~5× độ trôi thế kỷ.
3. **Sàn động không khử được trôi, chỉ đổi cách trôi** — k=43 tự co giãn vẫn trôi 69,1→67,8, và
   chênh lệch với 2B còn **tăng** theo thời gian (ρ=+0,718 p=0,006).

Thêm: PBO của chính họ tham số này = **0,916** (08-04). Mọi "điểm tối ưu" tìm được trên lịch sử ở
đây phải mặc định coi là nhiễu — và đúng thế, **3,0 tỷ là ngưỡng duy nhất có dấu ổn định dưới LOO,
và nó XẤU hơn 2B**.

### 9.2 Điều đáng theo dõi thật sự — **capacity, không phải xói mòn danh nghĩa**

Biến thể C không đủ điều kiện để wire (và job `Taylor_20260804_085248` đã A/B chính luật đó: nó làm
vị thế kẹt-không-fill-nổi **35,0% → 0,0%** nhưng phần gia tăng +1,53pp **đổi dấu** khi bỏ
2020+2021). **Nhưng nó là ràng buộc duy nhất trong cả job có bậc độ lớn thay đổi theo trạng thái
thật của book.** Ba mốc cụ thể để user quyết:

| NAV/tài khoản | required_ADV (X=3,86%) | Sàn 2B đang là | Hàm ý |
|---|---|---|---|
| ~1B (hôm nay) | 0,33 tỷ | chặt hơn 6,1× | Sàn 2B đang **cắt oan** vùng 0,33–2 tỷ. Đó chính là ca TRC (ADV ~1–1,4 tỷ) |
| **~5,9B (điểm giao)** | **2,0 tỷ** | vừa đúng | Từ đây trở lên sàn 2B **không còn đủ chặt** |
| ~12B | 4,0 tỷ | lỏng hơn 2,0× | |
| 50B | 16,84 tỷ | lỏng hơn 8,4× | Chỉ 101/358 mã khả thi; 2B trở nên vô nghĩa |

⇒ Sàn 2B đang **đúng vì lý do khác** với lý do người ta hay gán cho nó. Nó không phải ràng buộc
thanh khoản đúng bậc; nó là **quyết định hiệu quả vốn** (user chốt 08-10) — và tài liệu hiện tại
(`lag_liquidity_filter.py:16-28`) đã ghi đúng như vậy. Báo cáo này **củng cố** cách ghi đó.

### 9.3 Điều kiện CẦN THÊM để mở lại câu hỏi này

Không phải "chạy lại backtest lần thứ tư" — cả 3 biến thể đều là mệnh đề **về mô hình fill**, mà
backtest dùng chính mô hình đó (prereg §5 R2: engine giả định 20%/phiên, fill THẬT đo được 3,86%,
lệch **~5,2×**). Ba điều kiện, theo thứ tự giá trị:

1. **Fill THẬT của sổ LAG live, N ≥ 30 sự kiện.** Hiện chỉ có **N=2**, lớn nhất 0,45%ADV. Đây là
   thứ có thẩm quyền phân xử duy nhất. Nguồn đang tích luỹ: `data/lag_liq_ledger.csv` +
   `dnse_raw_*.jsonl`. **Mốc: checkpoint 2026-12-15, rà soát đầy đủ 2027-03-31**
   (`kb/projects/lag-adv-filter-tracking.md`) — **không rút ngắn**.
2. **NAV vượt ~5,9 tỷ** (điểm giao ở bảng §9.2 — nơi `required_ADV = 0,3368 × NAV` cắt mốc 2 tỷ;
   với công thức 8% của dispatch thì điểm giao là ~7,4 tỷ). Dưới mốc đó, capacity chưa binding và mọi tranh luận
   về sàn là tranh luận về 1,6% vốn. Trên mốc đó, câu hỏi đúng **không còn là "2B hay động"** mà là
   **"sàn capacity theo NAV"** — một luật khác hẳn, và nó nên được đo lại từ đầu ở thang NAV thật.
3. **Nếu vẫn muốn một sàn động dù không có tín hiệu** (lý do vận hành, không phải lợi nhuận):
   biến thể **A (inflate 7%)** là lựa chọn ít tệ nhất — nó đơn giản nhất, không phụ thuộc nguồn dữ
   liệu ngoài (`universe_pit`), không cần calibrate, Δ≈0 nên **không phá gì**, và tại 2026 nó cho
   1,985 tỷ ≈ đúng sàn hiện hành. Nhưng phải nói thẳng: đó là quyết định **thẩm mỹ/vận hành**,
   backtest **không** ủng hộ nó.

## §10 — Artifact

| File | Nội dung |
|---|---|
| `exp_lag_advdyn_20260825/pt_v23_advdyn.py` | engine bản sao NC (khác production đúng 3 khối) |
| `exp_lag_advdyn_20260825/run_leg.sh` | lệnh chạy pin R3 nguyên văn |
| `exp_lag_advdyn_20260825/{dyn_ctrl,s1000m,s1500m,s2000m,s3000m,s4000m,dynA,dynB20,dynB25,dynB30,dynB43}.log` | 11 log đầy đủ, `EXIT=0`, self-check 0 VND |
| `…/legs_summary.csv`, `is_oos.csv` | metric tổng hợp + IS/OOS |
| `…/bootstrap_bh.csv` | p-value bootstrap + bảng BH |
| `…/loo_delta.csv` | LOO theo năm |
| `…/dropped_per_year.csv`, `dropped_rate_per_year.csv`, `diff_events.csv` | số/tỷ lệ ứng viên bị chặn, n-event khác biệt |
| `…/dropped_*.json`, `kept_*.json` | danh sách ứng viên bị loại/giữ từng chân (có `floor_vnd` tại ngày tín hiệu) |
| `…/universe_adv_pctiles.csv`, `universe_frac_below.csv`, `universe_pctile_k.csv`, `floor_pctile_k{20,25,30,43}.csv` | phân phối ADV `universe_pit` + chuỗi sàn động |
| `…/bal_candidates_per_year.csv` | Bước 3 — ứng viên BAL bị lọc per year |

## §11 — Liên quan

- `lag_dynamic_threshold_prereg_20260825.md` (prereg của chính job này)
- `lag_hard_adv_gate_2ty_20260804.md` — job `Taylor_20260804_080547`, thang liều phẳng + PBO 0,916
- `lag_dynamic_adv_gate_executability_20260804.md` — job `Taylor_20260804_085248`, A/B luật capacity
- `adv_hard_gate_impact_20260810.md` — job `Taylor_20260810_073541`, băng ADV 1,6% vốn
- `kb/projects/lag-adv-filter-tracking.md` — **kết luận bị khoá**, mốc 2026-12-15 / 2027-03-31
- `lag_liquidity_filter.py` docstring — nguồn chuẩn tắc về lý do wire sàn 2 tỷ
