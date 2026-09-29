# Dùng phần vốn giải phóng khi park 0.80 → 0.30 như thế nào
Job `Taylor_20260927_085628` · 2026-09-27 · **PAPER-ONLY, không wire, không đổi config, không đặt lệnh**
PREREG: `PREREG.md` (viết trước khi đọc số mới). Artifact: `carry_paired.py`/`carry_paired_results.json`,
`conc_tail.py`/`conc_tail_results.json`/`conc_tail.log`, `breakeven.py`.

## KẾT LUẬN MỘT DÒNG
**Phần vốn giải phóng nên NẰM YÊN Ở TIỀN — trong Trứng vàng.** Carry thực nhận đo được
**8,55%/năm** làm cho park=0,30 **trội park=0,80 trên CẢ HAI trục** (CAGR +0,35pp *và* đuôi DD
tốt hơn 7,6pp); break-even ở **7,00%/năm**. Ngược lại, **mọi** sleeve equity 10% NAV — dù tập
trung (k=4-6) hay diện rộng (k=30) — đều **FAIL đúng cái cổng DD đã dùng để hạ park về 0,30**.
AlphaLens có track đẹp nhưng N cho phép kết luận là **1 cửa sổ**; theo chuẩn của chính fleet cần
**52,5 năm** — không đủ để quyết sizing, dù có gia hạn.

---

## (1) CARRY THẬT CỦA TIỀN NHÀN RỖI — 8,55%/năm, ĐO KHÔNG SUY

Nguồn: `data/execution_logs/dnse_raw_*.jsonl`, record `kind=balances`, `payload.egg.totalValue`,
86 file, 2 TK, 2026-07-06 → 2026-09-27 (egg xuất hiện từ 2026-08-04, khác 0 từ **2026-08-18**).
Tách kỳ bằng chính dữ liệu: nạp/rút = |Δ/ngày| / gốc > 1e-3; 6 kỳ "sạch" còn lại chỉ có lãi.

| TK | Kỳ | Ngày | Gốc (VND) | Lãi nhận | Lãi suất (365d) |
|---|---|---|---|---|---|
| SpaceX | 08-18→09-16 | 29 | 100.200.428 | 680.675 | **8,5500%** |
| SpaceX | 09-17→09-24 | 7 | 50.956.016 | 82.971 | 8,4904% |
| SpaceX | 09-25→09-27 | 2 | 85.449.493 | 39.819 | 8,5044% |
| ZaloPay | 08-18→09-16 | 29 | 38.759.519 | 263.299 | **8,5500%** |
| ZaloPay | 09-17→09-24 | 7 | 7.814.048 | 12.723 | 8,4900% |
| ZaloPay | 09-25→09-27 | 2 | 102.121.977 | 47.811 | 8,5442% |

**Bình quân theo gốc-ngày = 8,543%/năm, biên 8,490–8,550%.** Lãi cộng dồn MỖI NGÀY DƯƠNG LỊCH (kể
cả T7/CN — kiểm chứng 08-22, 08-23 đều +23.471đ), đơn lãi trên gốc (Δ/ngày hằng số trong kỳ), tỉ lệ
**tuyến tính theo gốc** (Δ 11.853/19.909 = 0,5954 vs gốc 50,96tr/85,45tr = 0,5963 ⇒ khớp). Không
thấy phí ở chân NẠP: 09-25 SpaceX cash −34.398.652 ⇒ egg +34.410.506 = đúng nạp + đúng 1 ngày lãi
(11.854). Chân RÚT không tách được khỏi giao dịch cùng ngày ⇒ **không kết luận phí rút = 0**, chỉ
"không quan sát được phí".

**Tiền để TRONG tài khoản chứng khoán (không vào egg) ≈ 0%, có thể ÂM**: `stock.depositInterest`
SpaceX tháng 9 = 1.832đ trên số dư 22–41tr (≈0,12%/năm) trong khi `depositFeeAmount` = 7.129đ —
phí > lãi. Giả định 0%/năm của backtest (CLAUDE.md §Backtest) **đúng cho cash, sai cho egg**.

### Hàm ý pp CAGR — đo CHUNG với mức park, không tuần tự
Đo trực tiếp trên 12 leg đã pin (`*_parkgrid_*_univpit.csv`), credit carry lên
`max(bal_cash_ref+lag_cash_ref, 0)` theo số ngày dương lịch (cash âm = nợ margin, engine đã tính
10%/năm — cộng nữa là tính hai lần). Bootstrap **paired** giữ nguyên L=21, B=4000, seed=12345 của
`park_fraction_grid_20260927/paired_v2.py`.

| x (park) | cash share NAV | park share NAV | carry (pp/năm) | CAGR @0% | CAGR @8,55% | DD5th @0% | DD5th @8,55% |
|---|---|---|---|---|---|---|---|
| 0,00 | 56,97% | 0,00% | +4,96 | 22,37% | 28,44% | −24,0% | −21,2% |
| **0,30** | **46,35%** | **10,48%** | **+4,02** | 23,43% | **28,40%** | −25,1% | **−22,4%** |
| **0,80** | **28,64%** | **28,06%** | **+2,48** | 24,95% | **28,05%** | −32,0% | **−30,0%** |
| 1,00 | 21,74% | 36,72% | +1,89 | 24,93% | 27,29% | −36,1% | −34,6% |

- Chênh carry 0,30 vs 0,80 = **+1,54pp/năm** — xấp xỉ TRỌN VẸN toàn bộ +1,52pp CAGR mà lưới nói
  park=0,80 "mua được" (CAGRnet +1,48pp). Đây chính là con số user gợi ý: 17,58pp NAV × 8,55% = 1,50pp.
- **Break-even carry = 7,00%/năm** (`breakeven.py`, sweep 0,05% một bước). Trên 7,00% thì park=0,30
  CAGR cao hơn park=0,80; measured 8,55% ⇒ **+0,346pp**.
- Bền với giả định carry: ở **6,0%** park=0,80 chỉ còn hơn 0,22pp CAGR (DD5th −30,5% vs −23,2%);
  ở **4,5%** hơn 0,55pp (−30,9% vs −23,6%). **Cổng DD không đổi ở CẢ BA mức**: pass = {0; 0,1; 0,2; 0,3},
  0,80 FAIL. Carry làm quyết định 0,80→0,30 MẠNH HƠN, không hề lung lay nó.
- ⚠️ **Áp 8,55% (rate spot 09/2026) cho cả 2014–2026 là NGƯỢC THỜI GIAN** — lãi suất VN giai đoạn
  đó dao động ~3–10%. Cột "@8,55%" là **minh hoạ**, không phải restatement của CAGR lịch sử. Phát
  biểu bảo vệ được là phát biểu TIẾN: *ở carry hôm nay, break-even 7,00% đã bị vượt.*

### Trần / T+1 — cái CHẶN thật, và nó CHƯA được xác minh
- Lãi suất **phẳng 8,49–8,55% trên biên gốc 7,8tr → 102,1tr**: không thấy bậc thang trong biên đó.
- NAV 09-25: SpaceX **983,0tr**, ZaloPay **957,3tr** (`data/execution_logs/nav_history_*.csv`).
  Ở NEUTRAL (pool nhàn rỗi ~30% NAV), hạ 0,80→0,30 nhả **0,5 × 30% = ~15pp NAV ≈ 147tr/TK**; cộng
  6pp cash đang có ⇒ egg phải giữ **~21% NAV ≈ 205tr/TK**, tức **~2× mức cao nhất từng quan sát
  (102,1tr)**. **Capacity trên 102tr/TK = CHƯA XÁC MINH** — cần Mafee đọc điều khoản sản phẩm
  (trần số dư, trần nạp/rút ngày, bậc lãi suất, phí rút, thuế TNCN trên lãi nếu egg là quỹ chứ
  không phải tiền gửi). **Không suy từ biểu lãi công bố** (đúng yêu cầu dispatch) và tôi không suy
  capacity từ 3 điểm dữ liệu.
- T+1: cơ chế đã CÓ, không phải xây mới — `compute_jit_unpark.py` (L2) là **ngoại lệ duy nhất được
  user duyệt 2026-08-19** cho cộng egg vào pool, sinh `funded_via="cash+egg"` + `egg_relied_vnd` và
  in cảnh báo "CẦN RÚT Trứng vàng TRƯỚC khi đặt lệnh"; gate cứng `check_plan_funding()` (P0) **vẫn
  không** cộng egg ⇒ rút không kịp thì HOLD, đúng thiết kế (coding_guidelines_ext §25).
  Rủi ro vận hành TĂNG theo tỉ lệ: egg từ 6%→21% NAV ⇒ mỗi ngày mua cần lệnh rút lớn hơn từ hôm
  trước; quên rút = HOLD nhiều hơn. Đây là chi phí thật của phương án (a), phải nói ra.
- LIVE hiện đã dùng egg cho gần như toàn bộ cash nhàn rỗi (08-18: SpaceX cash 110tr → 9,8tr,
  egg 0 → 100,2tr) ⇒ cơ chế chạy được ở mức ~100tr, chỉ chưa biết trần.

---

## (2) AlphaLens paper — track ĐẸP, N KHÔNG ĐỦ, và không gia hạn nào sửa được

Nguồn thật: `data/alphalens_paper.json` + `mike/reports/paper_programs_daily_report_2026-09-26.md`
(§3) + charter `mike/kb/paper_programs_charter/alphalens.md`. Owner DollarBill, auditor Taylor,
nghiệm thu 2026-09-30.

| | Lợi suất 2026-07-01 → 2026-09-25 |
|---|---|
| AlphaLens EW 4 tên (`terp`, đã áp chặn trên vendor) | **≥ +0,51%** (là **CHẶN DƯỚI**) |
| AlphaLens EW (`accrue_only`, bỏ quyền MBB) | −0,53% |
| **custom30V, trọng số PIT thật** (`custom30v_8l.parquet`, 30 tên, carry-forward rebal 2026-05-05→08-05) | **−7,42%** |
| VNINDEX | **−4,03%** |
| ⇒ excess vs VNINDEX | +3,50 … +4,53pp · **vs custom30V: ~+7,9pp** |

Per-name: FPT +1,38%\* · ACB −5,52% · MBB −1,39% (terp) · HDB **+7,54%**.
\* FPT là **chặn dưới** do lỗi hồi tố hệ số vendor (`Close/Price` 1,000000 tại 06-30 → 0,909066 tại
09-18, đại lượng này KHÔNG được phép giảm); phương án B user duyệt 09-23. Tỉ suất FPT thật nằm đâu
đó trong **−7,83% … +1,38%** ⇒ **±2,3pp trên EW sleeve**. Nghĩa là 1/4 sleeve là KHOẢNG, không phải số.

**N ĐÚNG NGHĨA = 1.** Không phải 63 phiên, không phải 4 quan sát. 4 tên vào CÙNG ngày 2026-07-01,
buy-and-hold, KHÔNG rebalance, thoát CÙNG ngày 09-30 ⇒ chúng chia sẻ trọn một cửa sổ thị trường:
**1 sự kiện độc lập** cho câu hỏi "lens có beat VNINDEX không". Cross-section cũng không cứu được:
3/4 là bank (ACB/MBB/HDB) cùng một lens P/B-Gordon ⇒ thực chất **2 cược** (1 tech + 1 rổ bank), và
HDB một mình đóng góp gần hết excess.

`rnd_preflight_power.py` (skill quant-research Step 0), effect giả định **ngoài mẫu** IR 0,375
(excess ~3%/năm, TE ~8%/năm — mức hợp lý cho value-tilt large-cap), `--n-trials 4`:
- `--n-rule per-episode --obs-per-year 4 --n-available 1` → DSR **0,500**; cần **210 quan sát =
  52,5 năm**; Sharpe năm tối thiểu phát hiện được với N hiện có = **10,0** (×26,7 effect giả định).
- Cách đếm RỘNG NHẤT có thể bào chữa (`per-day`, 63 phiên) → DSR **0,196**; cần **13.038 phiên =
  51,7 năm**.

**Trả lời thẳng câu user hỏi: KHÔNG. Track ~3 tháng × 4 tên (3/4 là bank) KHÔNG đủ để quyết
sizing, và không có phương án gia hạn nào trong tầm với đủ được** — 52 năm là câu trả lời cho cả
"gia hạn 3 tháng" lẫn "gia hạn 1 năm". Đây là **cùng một lớp lỗi với ORB VN30F** (4 tháng R&D rồi
mới biết DSR 0,95 cần 16,2 năm > cả đời hợp đồng).

**Khuyến nghị cho mốc 09-30 (3 ngày nữa):**
1. **ĐÓNG chương trình đúng hạn 2026-09-30** — GO/NO-GO #1 (excess dương vs VNINDEX) là PASS theo
   số, nhưng ghi rõ vào registry: *PASS trên 1 quan sát, KHÔNG phải bằng chứng đủ để sizing.*
   Không gia hạn "để tích luỹ N" — đó chính là sai của ORB.
2. **Đổi THIẾT KẾ nếu muốn tiếp**, không đổi độ dài: cái thiếu là **số sự kiện độc lập**, nên phải
   biến nó thành event study — lens áp ĐỊNH KỲ (mỗi tháng/quý) trên TOÀN universe_pit, mỗi lần
   chọn top-k, đo IC/excess theo từng đợt ⇒ hàng trăm quan sát từ 2014, đo được OOS, DSR/PBO tính
   được. Đó là thứ có thể chấm điểm; 4 cái tên giữ 3 tháng thì không.
3. **Trước khi dùng con số AlphaLens vào bất kỳ quyết định nào: sửa xong lỗi hệ số vendor FPT**
   (hiện headline là chặn dưới, không phải giá trị đo).

---

## (3) BA ỨNG VIÊN, CÙNG MỘT KHUÔN ĐO

Cổng DD giữ nguyên định nghĩa của PREREG v2 park-grid: **DD5th phải ≥ (DD5th tại x=0) − 2,0pp**.
Trong thế giới có carry, DD5th@x=0 = −21,21% ⇒ **floor = −23,21%**.

| Ứng viên | CAGR act | E[Calmar] | **DD5th** | Cổng DD |
|---|---|---|---|---|
| **(a) park 0,30 + carry egg 8,55%** ← baseline ĐÚNG | 28,40% | **1,963** | **−22,4%** | ✅ PASS |
| (b) tăng lại park custom30V về 0,80 (+carry) | 28,05% | 1,439 | −30,0% | ❌ FAIL |
| (b') park 0,50 (+carry) | 28,37% | 1,760 | −24,9% | ❌ FAIL |
| (c1) a + sleeve **k=4** 10% NAV, draw trung vị | 28,70% | 1,713 | −26,2% | ❌ FAIL |
| (c1) a + sleeve **k=4** 10% NAV, draw phân vị 5 đuôi | 28,76% | 1,683 | −27,2% | ❌ FAIL |
| (c1) a + sleeve **k=6** 10% NAV (trung vị / 5th) | 28,46 / 29,05% | 1,668 / 1,742 | −26,7 / −26,0% | ❌ FAIL |
| (c2) a + rổ **k=30** 10% NAV (trung vị / 5th) | 29,13 / 28,87% | 1,761 / 1,722 | −25,8 / −26,3% | ❌ FAIL |

**Đây chính là cái bẫy dispatch cảnh báo, và nó CÓ THẬT bằng số:** nhồi lại 10% NAV vào equity
trả lại **3,4–4,8pp** trong đúng 7,6pp đuôi DD vừa giành được (45–63%), để đổi lấy **+0,3 đến
+0,7pp** CAGR, và hạ E[Calmar] từ 1,963 → 1,67–1,76. Nó **không** xấu hơn park=0,80 (−30,0%) —
nên không đảo ngược quyết định — nhưng nó **FAIL đúng cái cổng đã loại park=0,80**. Không có
ứng viên equity nào qua cổng.

### c1 vs c2: giá của TẬP TRUNG, đo không có hindsight tên
Đo đúng cái đắt nhất: **không** dùng 4 tên AlphaLens đã chọn (đó là hindsight — forward bạn không
biết trước 4 tên nào). Mỗi quý `universe_pit_q`, rút **ngẫu nhiên** k tên từ ĐÚNG pool custom30V
rút (`in_universe ∧ pass_golden_floor ∧ rating_8l≤3 ∧ ¬banned`, pool trung vị 137 tên), EW, giữ
tới quý sau; **300 draw/k**; 2.966 đoạn nắm giữ, 2014-08 → 2026-06.

| k | CAGR trung vị | CAGR 5th | **MaxDD trung vị** | **MaxDD 5th (đuôi)** | SD chéo-draw MaxDD |
|---|---|---|---|---|---|
| **4** | 14,11% | 6,20% | −52,1% | **−63,8%** | **7,54pp** |
| **6** | 14,96% | 7,94% | −51,3% | **−62,5%** | 6,73pp |
| **30** | 15,43% | 12,54% | −48,8% | **−53,7%** | **2,85pp** |

**Tập trung không mua được lợi suất — nó chỉ mua độ phân tán.** CAGR trung vị k=4 (14,11%) THẤP
HƠN k=30 (15,43%), trong khi đuôi DD xấu thêm **10,1pp** và SD chéo-draw gấp **2,6×**. Với cùng
mức exposure, c1 nghiêm ngặt tệ hơn c2 ở mọi trục ngoại trừ "có thể may".
⚠️ Caveat phải mang theo: sleeve mô phỏng **luôn đầu tư, không có state-gate** (AlphaLens cũng
buy-and-hold nên đúng tinh thần), nên đây là **CHẶN TRÊN** của chi phí đuôi. Một sleeve có gate
DT5G sẽ rẻ hơn — mức rẻ hơn bao nhiêu thì **CHƯA ĐO ĐƯỢC bằng ledger hiện có, cần job engine
riêng** (đúng cam kết M4 của PREREG: không ước lượng).

---

## (4) TRẦN CỨNG: ~17,6pp KHÔNG hấp thụ hết được, phần dư ở đâu

`kb/projects/discretionary-margin-policy-20260823.md` (RESYNC 08-30, `decided_by: user`):
per-name **≤5% NAV exposure**, **sleeve tổng ≤10% NAV exposure**, hard-cap f=1,3, ≤10% ADV-3M.
Nới 15% cần TRIGGER ≥3 case marginable đồng thời — hiện chỉ có 2 (TV1, DGC) ⇒ **không tự nâng**.

| Phần | pp NAV | Đi đâu |
|---|---|---|
| Tổng giải phóng (0,80→0,30, bình quân lịch sử) | **17,58** | — |
| Trần tuyệt đối sleeve discretionary | **≤10,0** | và ngay cả 10 này cũng **FAIL cổng DD** ⇒ thực tế **0** |
| **Phần dư bắt buộc phải trả lời** | **≥7,58** (thực tế **17,58**) | **(a) tiền trong Trứng vàng** |

Trả lời tường minh: **toàn bộ 17,58pp nằm ở (a)** — không phải vì hết chỗ, mà vì (a) là ứng viên
DUY NHẤT qua cổng. Ở NEUTRAL hôm nay con số tức thời là ~15pp NAV ≈ 147tr/TK.

---

## (5) THỨ TỰ BƯỚC ĐI — mỗi bước một tiêu chí PASS định lượng

**Bước 1 — LÀM NGAY, không thêm rủi ro nào.** Đảm bảo 100% cash nhàn rỗi sau khi hạ park nằm
trong Trứng vàng (LIVE đã làm ở mức ~100tr, cần mở rộng lên ~205tr/TK).
· PASS: sau 14 ngày dương lịch, `egg.totalValue` tăng ≥ `0,95 × idle_cash × 8,49%/365 × 14` trên
CẢ 2 TK, và `(cash + egg) / NAV` khớp pool nhàn rỗi ±1pp. Đo lại bằng đúng `dnse_raw` như §(1).
· Chặn: **cần Mafee xác minh TRƯỚC** trần số dư/nạp-rút, bậc lãi suất >102tr, phí rút, thuế lãi.
Nếu có trần ~100tr/TK ⇒ phần vượt trần rơi về 0% và **break-even 7,00% không còn được vượt** ⇒
phải quay lại cân park. Đây là một câu hỏi YES/NO, không phải nghiên cứu.

**Bước 2 — LÀM NGAY, rẻ.** Bỏ giả định "cash = 0%" khỏi mọi so sánh park/allocation về sau: ghi
carry đo được vào `data/results_registry.md` như một tham số môi trường, và nếu chấm lại bất kỳ
knob nào phân bổ giữa tiền và equity thì chấm ở carry thật + 2 kịch bản (4,5% / 6,0%).
· PASS: một knob được chấm lại mà kết luận không đổi trên cả 3 mức carry (đã đúng cho park grid).

**Bước 3 — PAPER, KHÔNG sizing.** AlphaLens: đóng đúng hạn 09-30 với ghi chú "PASS trên N=1".
Nếu user muốn đi tiếp hướng lens định giá thì mở chương trình MỚI dạng **event study định kỳ trên
toàn universe_pit**, không phải 4 tên buy-and-hold.
· PASS để được cân nhắc sizing: ≥200 quan sát độc lập (đợt × tên), IC dương OOS (2020+) với
`quant-skeptic` CONFIRMED, DSR ≥0,95, PBO <0,5. Dưới ngưỡng đó ⇒ vẫn là quan sát, không phải sizing.
· Trước đó: sửa hệ số vendor FPT.

**Bước 4 — CẦN JOB ENGINE RIÊNG, chỉ làm nếu user vẫn muốn sleeve.** Câu hỏi duy nhất còn mở mà
tôi KHÔNG đo được bằng ledger: *một sleeve có state-gate (DT5G) thì chi phí đuôi còn lại bao nhiêu?*
Thiết kế: grid 2 CHIỀU **park × w_sleeve** (park ∈ {0; 0,3; 0,5}, w ∈ {0; 5%; 10%}), sleeve gated
theo DT5G, chạy trong engine (không inject hậu kỳ), cùng bootstrap paired L=21/B=4000/seed=12345.
· PASS để được đề xuất wire: DD5th ≥ **−23,21%** (đúng floor đang dùng) VÀ E[Calmar] ≥ **1,963**
(mức của phương án (a)) VÀ `quant-skeptic` CONFIRMED. Không đạt cả ba ⇒ đáp án vẫn là (a).

**KHÔNG kết luận "nên làm sleeve".** Với số đang có, mọi sleeve equity 10% NAV đều FAIL cổng DD;
cái chưa đo được đã nói rõ ở Bước 4 và c1-vs-c2 caveat.
