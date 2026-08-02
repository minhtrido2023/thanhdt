# Hai bản sửa fidelity thanh khoản LAG — `liq<=0` fail-closed + cơ sở giá ADV
**Job:** `Taylor_20260802_163657` · **Ngày:** 2026-08-02 → 08-03 · **Tác giả:** Taylor

> # 🔴 ĐÍNH CHÍNH (2026-08-03, job `Taylor_20260802_175754`) — ĐỌC TRƯỚC PHẦN CÒN LẠI
> Báo cáo này soạn **TRƯỚC** khi có verdict. quant-skeptic sau đó chấm **INCONCLUSIVE**
> (`mike/logs/verify_20260802_173456.log`). **Mọi kết luận dạng "chân trung thực = 32,71%" trong
> file này (TL;DR và §mục 2/4 phần kết luận) đã BỊ GỠ BỎ** — không phải vì tính sai (mọi số cơ học
> đều tái lập độc lập được), mà vì chúng trả lời nhầm câu hỏi: Δ +4,08pp của **Việc 1** chưa tách
> được *edge thật* khỏi *hiện vật mô hình fill* ở quy mô sổ LAG 25B (lần thứ BA câu hỏi này không
> được trả lời). **Pin R3 chính thức vẫn là 27,24%. Không trích 31,32%/32,71% làm kỳ vọng.**
> Kết luận có hiệu lực: `data/results_registry.md` mục 2026-08-02/03 ·
> `mike/kb/incidents/2026-08/2026-08-02-lag-liquidity-fidelity-two-fixes.md` §3bis.
> Quyết định code: **Việc 2 giữ mặc định `price`** (căn cứ riêng: look-ahead + parity live),
> **Việc 1 hoàn nguyên về opt-in** (`LIQ_ZERO_BLOCK=""`).

> **TL;DR** — Hai lỗi fidelity ĐỘC LẬP trong nhánh thanh khoản sổ LAG, đo tách bạch bằng A/B 4
> chân trên snapshot đóng cứng. Chân đối chứng **tái lập CHÍNH XÁC** số pin hiện hành
> (27,24% / 1,81 / −18,4% / 1,48 / 1.006,33B). Sửa cả hai ⇒ **32,71% / 1,95 / −19,1% / 1,71**.
> Cả hai đều là **sửa lỗi mô tả sai đường đi (fidelity), N=1**, KHÔNG phải config chọn từ họ tối ưu.
> **Tác động LIVE hôm nay = 0 lệnh.**

---

## 1. Bối cảnh — vì sao 2 việc này tách khỏi saga Price/Close

Saga `2026-08-02-pe-price-close-adjustment-saga.md` xử lý cơ sở giá ở **tầng chọn rổ/trọng số**
(`custom_basket.py`, `rating_8l.py`). Hai việc dưới đây cùng **họ cơ chế** (Close đã điều chỉnh hồi
tố bị dùng sai chỗ) nhưng khác **file, khác tầng, khác hệ quả** — nên đo và commit riêng.

| | Việc 1 | Việc 2 |
|---|---|---|
| Lỗi | `liq<=0` ⇒ engine BỎ QUA trần ⇒ mua trọn size | ADV = `Volume_3M_P50 × Close` (giá đã điều chỉnh) |
| Tầng | engine mô phỏng (`simulate_holistic_nav`) | **dùng chung** live + engine |
| Biết từ | 2026-07-21 (đã có root cause, fix default OFF) | phát hiện trong saga hôm nay |

---

## 2. Việc 1 — `liq<=0` = KHÔNG MUA ĐƯỢC (fail-closed)

### Root cause (đã có sẵn, chỉ XÁC NHẬN lại — không điều tra lại từ đầu)
`simulate_holistic_nav.py` viết `if liq and liq > 0:` trước khi áp trần %ADV. Mã có
`Volume_3M_P50<=0`/không đo được ADV rơi vào nhánh `else` ⇒ **không bị trần** ⇒ mua **trọn size
trong 1 phiên**. Đường live thì ngược lại: chặn nhóm này ở **CẢ HAI tầng** — tín hiệu
(`lag_liquidity_filter.lag_filter_illiquid`, từ 07-21) và executor (`plan.cap_lag_orders`,
hard-gate fail-closed từ 07-22). Nên engine đang mô phỏng một đường **live không đi được**.

### Sửa
Kwarg `liquidity_require_positive` (đã có từ 07-21) — **đổi MẶC ĐỊNH `""` → `"lag"`**
(`pt_v23_audit_2014.py:257`). `liq` thiếu hoặc `<=0` ⇒ `daily_max=0`. Phạm vi `lag` = đúng phạm vi
gate live (live KHÔNG gate BAL). `LIQ_ZERO_BLOCK=off` giữ lại để tái lập pin lịch sử.

### Điều kiện #1 của pin 07-21 nay ĐÃ ĐÓNG
Pin 07-21 là **PIN TẠM** vì phải chạy trên live BQ (cache hỏng) ⇒ mức tuyệt đối lệch vintage.
Lần này chạy trên snapshot đóng cứng `bq_cache_asof20260729_postrestate` = **đúng vintage của số
pin hiện hành**, và chân đối chứng tái lập số pin chính xác đến từng chữ số ⇒ điều kiện vintage
đã thoả.

---

## 3. Việc 2 — cơ sở giá ADV: `Close` → `Price` (thô)

### CÂU HỎI CHẶN của dispatch: hàm này có được engine backtest gọi không?
**Trả lời: KHÔNG gọi trực tiếp — nhưng CÔNG THỨC là bất biến parity dùng chung.** Đọc code caller
thật, ADV `Volume_3M_P50 × <giá>` xuất hiện ở **3 điểm độc lập**, cố ý giữ giống hệt nhau:

| # | Vị trí | Vai | Ai gọi |
|---|---|---|---|
| 1 | `lag_liquidity_filter.py:~102` (SQL) | LIVE — lọc tầng tín hiệu (chỉ phép thử `>0`) | `golive_recommend_v23.py` |
| 2 | `trading_bot/due_diligence.py:adv_vnd` | LIVE — **độ lớn trần** hard-gate | `plan.cap_lag_orders` |
| 3 | `pt_v23_audit_2014.py:~1317` (`liq_lag`) | MÔ PHỎNG — tốc độ fill | engine backtest |

⇒ Đây **KHÔNG phải** "chỉ live, rẻ và an toàn" như đánh giá ban đầu. Sửa 1 điểm mà bỏ 2 điểm kia
sẽ **phá bất biến "trần live == trần đã mô phỏng"** — chính bất biến mà `cap_lag_orders` tồn tại để
giữ. Nên **sửa ĐỒNG THỜI cả 3**.

### Bằng chứng cơ sở giá đúng là `Price`, không phải `Close`
`Volume_3M_P50` là **số lượng CP THÔ**. Đo trên dữ liệu thật: `Trading_Value == Volume × Price`
khớp **100% số dòng** (r = 1,000000); `Volume × Close` thì không. ⇒ ADV tiền đồng đúng phải nhân
giá **THÔ**. Nhân `Close` (đã điều chỉnh hồi tố) sai **hai lần**:
1. **Sai độ lớn** — ADV bị hạ thấp ⇒ trần live chặt hơn thực tế, engine fill chậm hơn thực tế.
2. **Look-ahead** — hệ số `Close/Price` tại ngày *t* phụ thuộc sự kiện quyền **SAU** *t*.

### Dose-response — kiểm chứng falsifiable, KHÔNG phải kể chuyện
Nếu chẩn đoán đúng, sai số phải **lớn dần khi lùi về quá khứ** (càng nhiều sự kiện quyền tích luỹ
sau đó), và **triệt tiêu ở cuối chuỗi** (không còn sự kiện tương lai). Đo median `Close/Price`
theo năm (n = 156k–316k dòng/năm):

| 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0,443 | 0,487 | 0,530 | 0,586 | 0,643 | 0,686 | 0,731 | 0,784 | 0,833 | 0,887 | 0,934 | 0,979 | **1,000** |

**Đơn điệu hoàn hảo 13/13 năm, hội tụ đúng 1,000 ở 2026.** Năm 2014 ADV bị hạ **2,26 lần**.

Đây cũng là lời giải cho bất đối xứng IS/OOS của Việc 2 (§4): phần hơn tập trung ở IS **không phải
overfit** — nó **tỉ lệ thuận với độ lớn của chính lỗi đang sửa**, và bằng ~0 ở OOS đúng nơi lỗi
bằng ~0. Chữ ký này ngược hẳn với reshuffle-luck (bài học MOM/Wave1).

---

## 4. A/B 4 chân — thiết kế và kết quả

Snapshot đóng cứng `bq_cache_asof20260729_postrestate` (đúng vintage số pin), `threads=1`,
`$DNA_PYEXE`. Harness: `data/liqadv_ab_20260802/run_leg.sh`. Mỗi chân tự gắn hậu tố filename
(`_liqzblag`, `_advprice`) theo §8 — **canonical CSV KHÔNG bị đụng**.

| Chân | `LIQ_ZERO_BLOCK` | `LAG_ADV_BASIS` | CAGR | Sharpe | MaxDD | Calmar | NAV cuối | IS 14–19 | OOS 20+ |
|---|---|---|---|---|---|---|---|---|---|
| **L0** đối chứng | off | close | **27,24%** | **1,81** | **−18,4%** | **1,48** | **1.006,33B** | 23,81% | 30,46% |
| **L1** chỉ Việc 1 | lag | close | 31,32% | 1,88 | −18,8% | 1,67 | 1.490,21B | 24,67% | 37,75% |
| **L2** chỉ Việc 2 | off | price | 28,86% | 1,90 | −17,8% | 1,62 | 1.178,01B | 27,09% | 30,48% |
| **L3** cả hai | lag | price | **32,71%** | **1,95** | −19,1% | **1,71** | 1.699,09B | 27,22% | 37,96% |

**L0 tái lập số pin hiện hành CHÍNH XÁC** (27,24 / 1,81 / −18,4 / 1,48 / 1.006,33B) ⇒ A/B hợp lệ.
Không tái lập được thì mọi kết luận L1/L2/L3 vô hiệu — đây là điều kiện tiên quyết, đã thoả.

- Self-check **0 VND** cả BAL+LAG ở **CẢ 4 chân** (cash-flow identity + final NAV identity).
- Coverage gate `universe_pit` OK 3107/3107 phiên ở cả 4 chân.
- Recompute độc lập `extract_peryear.py` từ CSV **khớp chính xác** bản in engine cả 4 chân.
- Δ **không cộng tuyến tính** (+4,08 + 1,62 = 5,70 > 5,47 thực đo): hai bản sửa **giao thoa** —
  đều tác động lên cùng một cơ chế (tốc độ/khả năng fill sổ LAG), nên không quy kết riêng lẻ được
  quá chặt. Đây là lý do phải chạy L3 thật chứ không cộng L1+L2.

### Per-year leave-one-out trên Δ (bài học MOM/Wave1)

| Δ | Dương | Biên độ | Đọc |
|---|---|---|---|
| Việc 1 (L0→L1) | **13/13** | +2,59 … +5,54pp | tái lập 07-21 (+4,12 vs +4,11) |
| Việc 2 (L0→L2) | **13/13** | +0,86 … +1,98pp | **rất ổn định**, không năm nào carry |
| Cả hai (L0→L3) | **13/13** | +4,01 … +6,76pp | — |

Không có phép LOO nào đảo dấu ⇒ lợi ích **không do 1–2 năm carry**. (Riêng *mức tuyệt đối* vẫn phụ
thuộc 2021 nặng ở **mọi** chân — đặc tính sẵn có của R3, không phải của hai bản sửa này.)

### DSR / PBO / bootstrap trên chân L3 (ứng viên production)
`data/liqadv_ab_20260802/annex_L3.py` (wrapper §8, trỏ `dsr_pbo_annex` sang CSV L3):
- ann-SR **1,871**; **DSR = 1,0000** ở mọi N (232 CSV / N_reg=120 / N_reg=200 bảo thủ).
- PBO family-level **0,4430** — chỉ số này nói về **CẢ HỌ tìm kiếm 232 CSV**, KHÔNG phải về hai
  bản sửa fidelity N=1 này (không có multiple-testing để deflate: đây là sửa lỗi, không phải chọn
  config thắng từ một họ).
- Bootstrap circular-block L=21: CAGR 5th-pct **22,2%** (med 33,0%); MaxDD 5th-pct **−30,2%**;
  **P(DD<−30%) = 5,2%**.

⇒ **Anchor DD giữ nguyên ~−30%**, KHÔNG phải −19,1%. Điểm ước lượng MaxDD xấu đi nhẹ
(−18,4% → −19,1%) đúng như kỳ vọng: sổ LAG chạy nhiều vốn hơn trong nhóm **mua được thật** thì
cũng ăn drawdown thật hơn — đây là fidelity, không phải hồi quy chất lượng.

---

## 5. Tác động LIVE (đo, không suy đoán)

Việc 2 chạm đường LIVE thật (`due_diligence.adv_vnd` → `cap_lag_orders`, hard-gate chặn lệnh).
Đổi cơ sở `Close`→`Price` làm trần **NỚI** theo hệ số `1/(Close/Price)`. Đo trên rổ ứng viên LAG
thật hôm nay (asof 2026-07-31, 152 mã, đọc được 152):

- **1/152 mã (0,7%)** có `Close != Price`: **DNN** (r = 0,4514 ⇒ trần × 2,215).
- DNN **đã bị loại ở tầng tín hiệu** (`lag_filter_illiquid`, nằm trong danh sách loại 19 mã) ⇒
  **không bao giờ tới executor**.

⇒ **Tác động lên lệnh thật hôm nay = 0.** Đúng như dose-response dự báo (2026 ratio = 1,000).
Thay đổi này quan trọng cho **replay lịch sử** và cho **tương lai** (mã trả cổ tức sẽ được trần
ĐÚNG thay vì chặt oan), không phải cho phiên kế tiếp.

> ⚠️ **Vẫn là thay đổi chạm LIVE** (nới một hard-gate), dù hôm nay đo được 0 lệnh đổi. Theo mandate
> Taylor ("thay đổi áp vào LIVE cần user duyệt") — báo cáo tường minh, để user/Mike quyết, KHÔNG tự
> coi là dọn dẹp nội bộ.

### Self-check tầng live
`lag_liq_signal_filter_selfcheck.py --live`: **22 PASS / 0 FAIL**, gồm **positive control 2 chiều**
mới thêm cho cơ sở giá:
- `ADV(CLL) == Volume_3M_P50 × Price` ✓
- `ADV(CLL) != Volume_3M_P50 × Close` (chiều ngược — bắt lỗi im lặng nếu ai đó revert) ✓
- Kèm check "tìm được mã `Close≠Price` để kiểm" — nếu không có mã nào tách được hai chân thì check
  vô nghĩa và **phải nói ra**, không im lặng PASS.

Chạy không `--live` chỉ ra 13 UNIT PASS — phần cơ sở giá **nằm sau cờ `--live`**. Ghi rõ ở đây vì
đúng bài học `verify-before-done`: "selfcheck PASS" mà không nói chạy ở chế độ nào là báo cáo thiếu.

---

## 6. Kết luận & đề xuất

1. **Cả hai bản sửa là fidelity thật, có căn cứ cơ học độc lập với kết quả backtest** — Việc 1 từ
   parity với gate live 2 tầng; Việc 2 từ đẳng thức đo được `Trading_Value == Volume × Price`.
   Không phải "tinh chỉnh cho số đẹp".
2. **Số pin R3 hiện hành 27,24% là chân fill-lạc-quan** và nay đo được đầy đủ: chân trung thực
   (cả 2 fix) = **32,71%**.
3. **Anchor DD ~−30%** giữ nguyên (bootstrap 5th-pct −30,2%) — KHÔNG dùng −19,1% làm kỳ vọng.
4. Khoảng `[~27,2%; ~31,3%]` ghi trong registry **hết hiệu lực** — nó là khoảng *chưa đo được*
   dựng từ pin 07-21. Nay đo trực tiếp trên đúng vintage ⇒ thay bằng số thật.
5. **Giả định thay thế (substitution) — điều kiện #2 của pin 07-21 nay ĐÃ ĐÓNG.** 07-21 lo rằng
   engine cho vốn chảy ngay sang ứng viên kế tiếp còn live để tiền nằm im (vì chỉ chặn ở
   executor). Từ 07-21 live đã có lọc **tầng tín hiệu** (`lag_filter_illiquid`) ⇒ sổ live tự chọn
   ứng viên kế tiếp, **đúng như engine mô phỏng**. Đây chính là "việc cần quyết #3" của 07-21, và
   nó đã được làm rồi ⇒ 32,71% là ước lượng có thay thế **hợp lệ**, không còn là cận trên treo.

**Đề xuất:** nhận L3 làm hành vi mặc định của engine (đã là default trong code) + giữ nguyên bản
sửa live 3 điểm, và **re-pin R3**. Chờ quant-skeptic + user duyệt phần chạm LIVE.

---

## 7. Files

- Harness: `data/liqadv_ab_20260802/run_leg.sh` · LOO: `.../loo_delta.py` · annex: `.../annex_L3.py`
- Log 4 chân: `data/liqadv_ab_20260802/{L0_legacy,L1_liqzb,L2_advprice,L3_both}.log`
- CSV: `data/v23_..._wtnamecap[_liqzblag][_advprice]_exp_L{0..3}_*_univpit.csv` (canonical KHÔNG đụng)
- Code: `pt_v23_audit_2014.py` (`LIQ_ZERO_BLOCK` default, `LAG_ADV_BASIS` mới),
  `lag_liquidity_filter.py`, `trading_bot/due_diligence.py`, `trading_bot/plan.py`,
  `lag_liq_signal_filter_selfcheck.py`
