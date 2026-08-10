# Nới trần entry LAG `anchor → anchor × 1,03` — BACKTEST NAV THẬT (cổng GO #2 + #3)

**Job** `Taylor_20260810_101717` · 2026-08-10 · Taylor
**Trạng thái**: **0 dòng code production bị sửa.** Patch nằm ở `pending_lag_anchor_widen_20260810/`, **CHƯA ÁP**.
**Tiền đề**: `research/lag_entry_window_execution_20260810.md` §5.4 (event-study nói +0,84pp/sự kiện).

---

## 0. Kết luận cho người quyết định — 3 câu

1. **Cổng GO #2 (backtest NAV) KHÔNG ĐẠT như một luận cứ LỢI NHUẬN.** Ở mức NAV, nới trần lên
   `anchor×1,03` cho **+0,08pp CAGR** (29,01% → 29,09%), **block-bootstrap 95% CI [−0,56; +0,67]pp**,
   `P(Δ>0)=0,55`. Đúng như §5.4 báo cáo gốc đã tự cảnh báo: **+0,84pp/sự kiện co lại ~10 lần và
   biến mất vào nhiễu** khi gặp ràng buộc vốn thật.
2. **Bằng chứng mạnh nhất chống lại là hình dạng, không phải mức**: cơ chế đơn điệu (số phiên bị
   chặn 3.769 → 3.110 → 2.481 → 1.970 → 1.285 khi cap đi 0→1→2→3→5%) nhưng **CAGR thì KHÔNG đơn
   điệu** (29,01 → 29,02 → 28,98 → **29,09** → 28,78). Một tham số có nội dung kinh tế thật không
   nhảy như vậy. **PBO (CSCV) = 0,775** — cao, đúng ngưỡng KB gọi là reshuffle-luck.
3. **Phát hiện phụ NGHIÊM TRỌNG HƠN việc chính** (§6): commit HYBRID fill-timing hôm nay
   (`0f54cb7` + flip `717307f`) **làm hỏng 4 selfcheck / 7 dòng FAIL**, trong đó có **chính
   `hard_no_chase_ceiling_selfcheck.py` E4** — event kiểm toán `HARD_CEILING_BLOCK` **không còn
   được ghi**. Đã chứng minh bằng bisect. LIVE chưa bị (paper-gate), PAPER thì bị.

**Đề nghị**: **KHÔNG wire vì lợi nhuận.** Nếu user vẫn muốn đổi, phải đổi trên **luận cứ vận hành**
(tỉ lệ khớp / rủi ro mất trọn cửa sổ entry), có patch sẵn sàng ở §5 — nhưng đó là quyết định
CHÍNH SÁCH, không được trích con số backtest nào làm chỗ dựa.

---

## 1. Vì sao phải dựng harness — engine KHÔNG có khái niệm trần anchor

Đây là điều phải hiểu trước khi đọc mọi con số bên dưới.

`pt_v23_audit_2014.py` / `simulate_holistic_nav.py` **không mô hình hoá** cửa sổ entry 3 phiên và
**không có** trần giá nào cho book LAG. Nó fill nhiều ngày (`max_fill_days=5`, mỗi ngày ở `Open`,
trần 20% ADV/ngày, `min_fill_pct=0.30`) **không kèm ràng buộc giá**. ⇒ **Số pin R3 hiện tại
(28,86%) là chân "KHÔNG CÓ TRẦN"** — nó KHÔNG phải chân "trần = anchor" đang chạy LIVE. Muốn A/B
được `anchor` vs `anchor×1,03` thì buộc phải **tiêm** cơ chế trần vào engine.

**Cách tiêm** (`exp_lag_anchor_nav_20260810/run_leg.py`): chèn text vào source `simulate_holistic_nav.py`
**lúc chạy**, nạp module đã vá vào `sys.modules` trước khi `pt_v23_audit_2014.py` import nó.
Không sửa file production, **không để lại bản sao tĩnh nào** trong repo (bản sao sẽ mốc khi engine
đổi). Chuỗi neo không còn khớp ⇒ **RAISE**, không im lặng chạy sai.

**Mô hình trần** — khớp luật V2.4 rule 2 tới đâu, lệch ở đâu:

| | Live (V2.4) | Trong harness |
|---|---|---|
| Anchor | `tav2_bq.ticker.Price` (thô) của **phiên chuẩn**, ≈ giá đóng cửa | `Open` của **ngày xử lý đầu tiên** |
| Điều kiện | giá live ≤ anchor×(1+cap) | `px_Open(ngày k≥2) ≤ anchor×(1+cap)` |
| Vượt trần | không khớp | bỏ phiên đó, **giữ pending** (không huỷ lệnh) |
| Cửa sổ | 3 phiên rồi `WINDOW_PASSED` | 5 phiên (mặc định engine) — **có chân kiểm 3 phiên riêng, §4** |
| Phạm vi | LAG phiên 2/3 | chỉ tier `LAG_HI/LAG_LO/LAG_TOP`; BAL/CAPIT/ETF **không đụng** |

Hai lệch (anchor Open-vs-Close; 5-vs-3 phiên) **tác động NHƯ NHAU lên mọi chân**, nên Δ vẫn cô lập
đúng một tham số — nhưng chúng làm **mọi chân có trần rộng rãi hơn live**. Ghi ra để không ai
trích số này như "mô phỏng đúng live".

### 1.1 Chân đối chứng — bằng chứng mạnh nhất có thể có

Chạy harness với `cap=None` (không tiêm gì) bằng **lệnh pin R3 nguyên văn** + snapshot
`bq_cache_asof20260729_postrestate` + `threads=1` + `$DNA_PYEXE`:

```
Final NAV 1,178.01B  CAGR 28.86%  Sharpe 1.90  MaxDD -17.8%  Calmar 1.62
[selfcheck BAL] 0 VND · [selfcheck LAG] 0 VND
CSV md5 = 7d053e6201c9d107685ff4d1dd9d2d2a
```

CSV **BYTE-IDENTICAL** (cùng md5 `7d053e62…`) với CSV pin registry 2026-08-03
(`..._exp_repin0803_price_univpit.csv`). Không chỉ khớp 5 chỉ tiêu — **khớp từng byte**. ⇒ harness
hợp lệ tuyệt đối, mọi Δ bên dưới là do đúng 1 tham số.

---

## 2. Bảng chính — họ 6 cấu hình (cửa sổ 5 phiên, mặc định engine)

NAV 50B · `AUDIT_END=2026-06-19` · `universe_pit` · `LAG_ADV_BASIS=price` · **self-check 0 VND cả 9 chân**

| Chân | trần | CAGR | Sharpe | MaxDD | Calmar | Final B | IS 14-19 | OOS 20+ | Δ vs LA |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **L0** | *không trần* (= pin R3) | 28,86% | 1,90 | −17,8% | **1,62** | 1.178,01 | 27,09% | 30,48% | −0,15 |
| **LA** | `= anchor` **(luật LIVE)** | **29,01%** | 1,91 | −18,1% | 1,60 | 1.195,16 | 27,37% | 30,51% | — |
| LB | `× 1,01` | 29,02% | 1,91 | −18,2% | 1,60 | 1.196,21 | 27,25% | 30,64% | +0,01 |
| LC | `× 1,02` | 28,98% | 1,91 | −18,1% | 1,60 | 1.191,04 | 27,19% | 30,61% | −0,04 |
| **LD** | `× 1,03` **(đề xuất)** | **29,09%** | 1,91 | −18,3% | 1,59 | 1.204,27 | 27,01% | 31,01% | **+0,08** |
| LE | `× 1,05` | 28,78% | 1,90 | −18,3% | 1,58 | 1.168,75 | 26,84% | 30,56% | −0,23 |

**Ba điều đọc được ngay:**

1. **Δ(LD−LA) = +0,08pp CAGR.** Event-study nói +0,84pp/sự kiện ⇒ **co lại ~10 lần**. §5.4 báo cáo
   gốc dự báo đúng chiều và đúng cả bậc độ lớn.
2. **Sharpe đứng yên 1,91 ở cả 4 chân có trần**; **Calmar ĐI XUỐNG đơn điệu** theo độ rộng trần
   (1,60 → 1,60 → 1,59 → 1,58) và **MaxDD xấu đi** (−18,1% → −18,3%). Nới trần = mua ở giá cao hơn
   ⇒ vào nhiều hơn ở đúng lúc giá đã chạy ⇒ trả giá bằng rủi ro. **Không có cải thiện risk-adjusted.**
3. **Chính cái trần (LA vs L0) có lợi +0,15pp — NHƯNG CHỈ Ở CỬA SỔ 5 PHIÊN.**
   ⚠️ **Dấu ĐẢO NGƯỢC ở cửa sổ 3 phiên** (sát live hơn): W0 không trần 29,07% vs WA trần=anchor
   28,81% ⇒ trần **TỐN −0,26pp**. **Không được trích "+0,15pp: trần có lợi" mà bỏ mất điều kiện
   cửa sổ** — xem §4. (quant-skeptic bắt đúng điểm này, đã sửa.)

### 2.1 Cơ chế đơn điệu, kết quả KHÔNG đơn điệu — đây mới là bằng chứng quyết định

| cap | 0% | 1% | 2% | 3% | 5% |
|---|---:|---:|---:|---:|---:|
| số **phiên-fill bị chặn** | 3.769 | 3.110 | 2.481 | 1.970 | 1.285 |
| số **event fill LAG** *(đã sửa, xem dưới)* | 3.479 | 3.688 | 3.882 | 4.027 | 4.280 |
| **CAGR** | 29,01 | 29,02 | 28,98 | **29,09** | 28,78 |

> ⚠️ **ĐÍNH CHÍNH (vòng quant-skeptic).** Dòng "event fill LAG" ở bản đầu ghi 4.648→5.438 —
> **KHÔNG tái lập được từ CSV theo bất kỳ định nghĩa nào** (người kiểm độc lập ra bộ số khác, lệch
> gần như một hằng số ~1.169). Bộ số đúng ở trên, **định nghĩa tường minh để khỏi mơ hồ lần nữa**:
> `record_type=="TX" & book=="LAG" & action=="buy"` đọc thẳng CSV audit từng chân. Định nghĩa hẹp
> hơn (`play_type ∈ {LAG_HI, LAG_LO, LAG_TOP}`) cho 3.032→3.801 — **cùng chiều, cùng bậc**.
> `blocked_days` lấy từ dòng `[EXPA] stats:` của log từng chân (1 dòng/chân, đã đối chiếu từng
> file, không dùng `grep` gộp). **Số đính chính KHÔNG đổi kết luận** — mức tăng vẫn +23% event
> fill trong khi CAGR không đơn điệu; đó mới là lập luận.

Cơ chế phản ứng **hoàn toàn đơn điệu** với tham số. CAGR thì nhảy loạn, và **cap=5% (nới nhất) lại
TỆ NHẤT, thấp hơn cả cap=0%**. Nếu "trần chặn nhầm nhóm tốt" là một edge thật ở mức NAV thì đường
liều-đáp phải đi lên; nó không. **+0,08pp ở đúng cap=3% là một điểm nhô của nhiễu.** Đây là cùng
chữ ký mà `KNOWLEDGE.md` §8 gọi là reshuffle-luck, và cùng dạng đã dùng để NO-GO gate ADV 2 tỷ
(registry 2026-08-04, "thang liều PHẲNG").

### 2.2 Kiểm định — không có cái nào bác được H0

| Kiểm định | Kết quả | Đọc |
|---|---|---|
| Block-bootstrap (block 21 phiên, 4.000 lần) Δ log-CAGR năm | **+0,062pp, CI95 [−0,563; +0,667]** | **CI CHỨA 0, rộng gấp 10 lần điểm ước lượng** |
| ↳ *artifact chạy được* `block_bootstrap.py` (Δ CAGR trực tiếp, seed 20260810) | **+0,080pp, CI95 [−0,707; +0,895], P=0,547** | cùng kết luận; xem ghi chú 2 thống kê dưới |
| `P(Δ>0)` bootstrap | **0,546** | gần như tung đồng xu |
| Sign test theo năm (LD>LA) | 8/13, **p=0,581** | không phân biệt được với 50/50 |
| LOO-1-năm (Δ CAGR) | +0,29 / +0,03 / +0,17 / +0,07 / −0,03 / +0,12 / −0,01 / −0,02 / +0,01 / +0,17 / +0,03 / −0,01 / +0,13 | **4/13 năm ĐỔI DẤU**; toàn bộ dải nằm gọn trong CI nhiễu |
| **PBO (CSCV, S=16, 12.870 tổ hợp)** | **0,775** | **≥0,5 ⇒ KB bắt ưu tiên cấu hình robust-trung vị, không phải IS-best** |
| DSR (mọi chân, `N_trials=6`) | 1,0000 | **KHÔNG phân biệt được gì** — xem ghi chú dưới |

> ℹ️ **Hai thống kê bootstrap, cùng một kết luận — đừng nhầm là mâu thuẫn.** Bản đầu báo
> **Δ log-CAGR** (+0,062pp); artifact `block_bootstrap.py` (thêm sau vòng quant-skeptic, vì bootstrap
> là thống kê quyết định DUY NHẤT trước đó không có script tái lập) báo **Δ CAGR trực tiếp**
> (+0,080pp) — đúng bằng hiệu trong bảng §2 (29,09−29,01). Log-transform làm co điểm ước lượng và
> co CI; **cả hai đều có CI chứa 0 và P(Δ>0)≈0,55**. Người kiểm độc lập tự viết bootstrap riêng
> (seed 7) ra +0,062pp, CI[−0,560;+0,676], P=0,542 — **tái lập được bản đầu**. Chọn trích con nào
> cũng được, miễn nói rõ là con nào; **không con nào bác được H0**.

> ⚠️ **Đừng trích "DSR = 1,0 ⇒ đạt chuẩn".** DSR đo *chiến lược có Sharpe thật hay không* so với
> ngưỡng multiple-testing (`SR0` ann = 0,01 ở đây). Cả 6 chân đều là **cùng một chiến lược V2.4**
> với Sharpe ~1,90 nên chân nào cũng ra 1,0. **DSR không phải công cụ để trả lời "phần GIA TĂNG
> +0,08pp có thật không"** — công cụ đúng cho câu đó là bootstrap CI + PBO ở trên, và cả hai đều nói KHÔNG.

**LOO theo năm đối chiếu với event-study:** event-study cho +0,61…+0,99pp qua **toàn bộ** 13 LOO,
không năm nào âm. Ở mức NAV: 4/13 âm và dải chỉ ±0,3pp. **Cùng một tham số, hai kết luận trái
ngược về độ bền** — đó chính là dấu hiệu ràng buộc vốn đã nuốt hết hiệu ứng.

---

## 3. Vì sao NAV nuốt mất hiệu ứng — cơ chế, không phải phỏng đoán

Sổ LAG **oversubscribe ~6×** (registry audit H8, bind 92% entry). Ở mức sự kiện, "được fill thêm"
là lợi nhuận thuần cộng vào. Ở mức NAV, **fill thêm một mã KHÔNG tạo thêm vốn** — nó chỉ đổi *mã
nào* được cấp vốn, và tiền đó bị rút khỏi mã khác đang xếp hàng. Số liệu khớp đúng cơ chế đó: nới
trần từ 0%→5% làm số event fill LAG tăng **3.479 → 4.280 (+23%)** mà NAV cuối book LAG lại **giảm**
**606,3B → 585,9B**. Nhiều lệnh hơn, không nhiều tiền hơn, và chất lượng trung bình mỗi đồng vốn kém đi.

*(Bộ số fill-event ở bản đầu — 4.648→5.438 — đã được ĐÍNH CHÍNH theo vòng quant-skeptic; định
nghĩa filter tường minh ở ô cảnh báo §2.1. Cặp NAV book LAG 606,3B→585,9B đã được người kiểm
recompute độc lập và **khớp chính xác**.)*

---

## 4. Chân kiểm sát live hơn — cửa sổ đúng 3 phiên

Cửa sổ 5 phiên của engine rộng hơn luật live (3 phiên rồi `WINDOW_PASSED`). Chạy thêm 3 chân với
`max_fill_days=3` **chỉ cho book LAG** (BAL/CAPIT giữ 5):

| Chân | trần | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---:|---:|---:|---:|
| **W0** | không trần | **29,07%** | 1,91 | **−17,7%** | **1,64** |
| **WA** | `= anchor` (LIVE) | 28,81% | 1,90 | −18,2% | 1,58 |
| **WD** | `× 1,03` | 28,90% | 1,90 | −18,4% | 1,57 |

- **Δ(WD−WA) = +0,09pp** — y hệt bậc độ lớn với họ 5 phiên. Bootstrap: **+0,072pp, CI95
  [−0,808; +1,039], P(Δ>0)=0,508**. Sign test 8/13, p=0,581. **Cùng kết luận.**
- Ở cửa sổ 3 phiên, **không trần lại tốt nhất trên MỌI chỉ tiêu** (Calmar 1,64 vs 1,57–1,58).
- **Giới hạn phải đọc**: kể cả ở cửa sổ 3 phiên, chỉ **14/7.283** lệnh (0,19%) bị trần làm **không
  fill nổi một cổ nào**. Trong khi LIVE ngày 08-10, **3/4 mã** khớp 0. **Backtest KHÔNG tái lập
  được chế độ hỏng của live** — vì trong backtest anchor = `Open` của chính ngày đầu và fill cũng ở
  `Open`, nên ngày 1 gần như luôn fill được; live thì anchor là giá đóng phiên trước và thị trường
  mở gap lên trên nó. ⇒ **Backtest là bằng chứng YẾU cho vấn đề vận hành của live, theo CẢ HAI
  chiều** — nó không xác nhận mà cũng không bác được luận cứ vận hành.

---

## 5. Patch chờ duyệt — có sẵn, nhưng KHÔNG được biện minh bằng backtest

`pending_lag_anchor_widen_20260810/lag_anchor_widen.patch` — `git apply --check` **sạch**.

- Sửa **1 giá trị** ở tầng nạp plan: `trading_bot/plan.py` thêm hằng `LAG_ANCHOR_CEILING_MULT = 1.03`,
  `load_plan()` suy `hard_no_chase_ceiling_vnd = anchor × MULT` (giữ nguyên "giá trị generator CHẶT
  HƠN thì thắng"; giá trị **rác vẫn chỉ rơi về `anchor×MULT`, không bao giờ vô hiệu hoá trần**).
- **KHÔNG sửa `executor.py`** — cơ chế §24 giữ nguyên tuyệt đối.
- **Phạm vi tự động đúng**: `entry_anchor_price` CHỈ do `filter_lag_entry_window.py::_apply_anchor_gate()`
  gắn cho ứng viên LAG **phiên 2/3** (phiên 1 không có anchor — chính nó đặt ra anchor).
  CAPIT/discretionary ghi thẳng `hard_no_chase_ceiling_vnd` và **không mang** `entry_anchor_price`
  ⇒ khối này bỏ qua chúng hoàn toàn. BAL không có trần cứng.
- Selfcheck cập nhật **trong cùng patch** (không xoá ca): I2/I5b/I5c/I6 assert lên **CÔNG THỨC**
  (import hằng số từ module) chứ không chép cứng 13.390 ⇒ đổi hằng số thì test đi theo, không mốc
  (§23 hệ luận 1). Thêm ca mới **I2b** = chứng minh ngược: `MULT>1` thì trần PHẢI **cao hơn** anchor.

**Đã verify bằng cách CHẠY, không phải đọc** (§22 — `git apply` exit 0 không phải bằng chứng):
áp `patch -p1` vào một **git worktree tạm** rồi chạy thật.

| Kiểm | Kết quả |
|---|---|
| `hard_no_chase_ceiling_selfcheck.py` sau vá | I2 = **13.390,0**, I3 giữ 13.000 (chặt hơn thắng), I5b/I5c = 13.390,0, I6 8/8 lệnh thật PASS ở ngưỡng mới |
| **Quét rộng §23** (`plan.py` = module lõi, `selfcheck_scope_map.sh` liệt kê **23** file) | **23/23 kết quả GIỐNG HỆT chân chưa vá** (cùng rc, cùng số dòng FAIL) ⇒ **patch gây 0 hỏng mới** |
| Repo THẬT sau khi xong | `git status --porcelain trading_bot/` **rỗng** — chưa đụng |

---

## 6. ⚠️ PHÁT HIỆN PHỤ — commit HYBRID hôm nay làm hỏng 4 selfcheck (7 dòng FAIL)

Phát hiện khi chạy quét rộng §23. **Không do patch của tôi** (baseline chưa vá hỏng y hệt).

**Bisect trên worktree — 3 mốc, kết luận không thể chối:**

| Mốc | `extreme_regime` | `paper_main_window` | `t2_settlement` | `hard_no_chase_ceiling` |
|---|---|---|---|---|
| `0f54cb7^` (**trước** commit HYBRID) | ✅ 0 | ✅ 0 | ✅ 0 | ✅ 0 |
| HEAD, cờ `fill_timing_hybrid_enabled=False` | ✅ 0 | ❌ 3 | ❌ 2 | ✅ 0 |
| **HEAD hiện tại** (cờ = `True`, commit `717307f`) | ❌ 1 | ❌ 3 | ❌ 2 | ❌ 1 |

⇒ **2 nguyên nhân tách bạch**: `0f54cb7` (bản thân CODE) làm hỏng `paper_main_window` + `t2_settlement`;
`717307f` (FLIP CỜ) làm hỏng thêm `extreme_regime` + `hard_no_chase_ceiling`.

**Cả 7 dòng FAIL cùng một chữ ký: lệnh MUA lẽ ra phải đặt thì không được đặt.**
```
[FAIL] C1 OFF: buy order placed normally            — placed=0        (extreme_regime)
[FAIL] C1 BUY placed in a 10:46 step                — 0 buy PLACE     (paper_main_window)
[FAIL] E1 BUY order unaffected by (empty) positions — []              (t2_settlement)
[FAIL] E4 có journal HARD_CEILING_BLOCK                               (hard_no_chase_ceiling)
```
Dump journal chỉ đúng thủ phạm:
```
HYBRID_DEFER,BUY-DRI-LAG-01,DRI,buy,...,"lịch HYBRID: ngoài block, còn 5 block phía trước"
```
`_place_slices` gặp `HYBRID_DEFER` là `continue` **TRƯỚC** khi tới `_limit_price` ⇒ nhánh ghi
`HARD_CEILING_BLOCK` không bao giờ chạy.

**Vì sao đáng lo hơn việc chính:**
1. **Mất dấu vết kiểm toán.** `HARD_CEILING_BLOCK` là event DUY NHẤT phân biệt "lỡ phiên vì TRẦN"
   với `NO_QUOTE`/`WAIT_CASH`. Hybrid bật ⇒ event này im. Cơ chế §24 vừa vá 08-09 mất khả năng
   quan sát đúng lúc ta đang tranh luận về nó.
2. **Suy luận §1.1 của báo cáo gốc vẫn ĐÚNG cho LIVE** — vì `fill_timing_live_gate=True` chặn mọi
   account `mode="live"`, SpaceX/ZaloPay không chạy hybrid ⇒ "0 event `HARD_CEILING_BLOCK`" trên
   journal LIVE 08-10 vẫn có nghĩa. **Nhưng từ giờ, bất kỳ ai đọc journal PAPER và kết luận "trần
   không chặn gì" sẽ SAI.**
3. **Pending patch `pending_paper_enable_hybrid_fill_20260810/` ghi "CHƯA ÁP DỤNG, CHỜ DUYỆT"**
   nhưng cờ **đã ở `True` trong `trading_bot/config.py`** và **đã commit** (`717307f`). Hai nguồn
   nói ngược nhau — cần Mike xác nhận đây là đã duyệt hay lọt.

**Đây không phải việc của job này để tự sửa.** Đã ghi bus, đề nghị Mike điều phối chủ sở hữu
(`Taylor_20260810_034544`) xử lý — cùng đường với các sự cố selfcheck khác.

---

## 7. Trả lời từng cổng GO của §5.4 báo cáo gốc

| # | Cổng | Trạng thái sau job này |
|---|---|---|
| 1 | User duyệt tiến hành | ✅ đã có (chính dispatch này) |
| 2 | **Backtest NAV thật, self-check 0 VND, IS/OOS** | ✅ **ĐÃ CHẠY** (9 chân, self-check 0 VND cả 9, chân đối chứng byte-identical pin R3) — nhưng **KẾT QUẢ KHÔNG ỦNG HỘ**: Δ +0,08pp, CI chứa 0, PBO 0,775, liều-đáp không đơn điệu |
| 3 | quant-skeptic CONFIRMED | ✅ **CONFIRMED / confidence cao** (log `logs/verify_20260810_110722_3041901.log`). ⚠️ Bus hiển thị "INCONCLUSIVE" là **hiện vật parser**, không phải verdict — xem §8 |
| 4 | **Paper rehearsal 1 phiên** | ⛔ **chưa chạy — kế hoạch ở §9** |
| 5 | Sửa đường cấp vốn phiên 1 (park_trim) | ⛔ chưa — **vẫn ưu tiên CAO HƠN việc này** (và giờ càng rõ: §2 cho thấy trần không phải chỗ mất tiền, thiếu vốn phiên 1 mới là) |

---

## 8. quant-skeptic — **CONFIRMED, confidence cao**

Log thô: `mike/logs/verify_20260810_110722_3041901.log` (dòng 35-36: `"verdict": "CONFIRMED"`,
`"confidence": "high"`).

> ⚠️ **Bus ghi "INCONCLUSIVE — VERDICT_JSON present but unparseable". ĐÓ LÀ HIỆN VẬT PARSER, KHÔNG
> PHẢI VERDICT.** Nguyên nhân đã biết và đã có memory riêng
> ([[reference-verify-finding-json-trailing-comma-bug]]): agent sinh JSON có **dấu phẩy thừa** trước
> `}` (ở đây: `"...changes the NO-GO.",\n  },`) ⇒ `verify_finding.sh` parse fail ⇒ hạ xuống
> INCONCLUSIVE. **Luôn đọc log thô, đừng đọc mỗi event bus.** Đây là lần tái phát thứ N của cùng
> một bug — đáng để Wags/Mike xử lý dứt điểm (parser nên strip trailing comma trước khi
> `json.loads`), vì nó đang **âm thầm hạ cấp các verdict CONFIRMED thật**.

**Người kiểm đã recompute độc lập** (không tin số tôi in ra): bảng 6 chân đầy đủ, IS/OOS, lưới
per-year 13 năm, chuỗi LOO, sign test 8/13, **PBO 0,775 khớp chính xác**; tự viết bootstrap riêng
ra +0,062pp CI[−0,560;+0,676]; tự md5 chân đối chứng — **byte-identical với pin registry**; tự
recompute NAV book LAG 606,3B→585,9B — khớp.

### 8.1 Hai lỗi thật người kiểm bắt được — đã sửa trong bản này

| # | Lỗi | Xử lý |
|---|---|---|
| 1 | §3 số **event fill LAG** (4.648→5.438) không tái lập được từ CSV | ✅ **ĐÃ SỬA** — bộ số đúng 3.479→4.280 + **định nghĩa filter tường minh** (§2.1, §3). Chiều và mức tăng không đổi (+23%) ⇒ kết luận cơ chế nguyên vẹn |
| 2 | §2 bullet 3 ("bản thân cái trần có lợi +0,15pp") **đổi dấu** ở cửa sổ 3 phiên | ✅ **ĐÃ SỬA** — bullet 3 giờ mang điều kiện cửa sổ; ở 3 phiên trần **TỐN −0,26pp** |
| 3 | Bootstrap — thống kê quyết định **duy nhất không có artifact chạy được** | ✅ **ĐÃ BỔ SUNG** `exp_lag_anchor_nav_20260810/block_bootstrap.py` (đã chạy, output ở §2.2) |

Hai mục còn lại người kiểm nêu, **CÓ CHỦ Ý không làm trong job này**: (a) chạy lại trên universe
mang gate ADV3T≥2 tỷ (`c4ca90f`, LAG pool −67%) — chỉ cần **nếu câu hỏi lợi nhuận được mở lại**,
mà kết luận là KHÔNG mở; (b) sửa `HARD_CEILING_BLOCK` bị hybrid nuốt — **điều kiện tiên quyết của
rehearsal**, đã nằm ở §9 bước 3.

### 8.2 Killer-objection của người kiểm — phải đọc kèm mọi trích dẫn

> Harness **không tái lập được chế độ hỏng của live**: vì anchor = `Open` của chính ngày fill đầu,
> ngày 1 gần như luôn khớp và chỉ **14/7.283 lệnh (0,19%)** bị chặn hoàn toàn ngay cả ở cửa sổ 3
> phiên — trong khi LIVE 08-10 có **3/4 mã khớp 0**. ⇒ backtest **hệ thống ĐÁNH GIÁ THẤP** mức độ
> trần bó live, nên cũng đánh giá thấp giá trị VẬN HÀNH của việc nới.

Điều này **không làm NO-GO sai** (báo cáo đã tự nêu đúng giới hạn đó ở §4 và đã giới hạn kết luận
trong phạm vi "không phải luận cứ lợi nhuận"), **nhưng** nó có nghĩa: **không ai được trích các con
số này làm bằng chứng CHỐNG LẠI luận cứ vận hành.** Backtest yếu theo CẢ HAI chiều.

---

## 9. Kế hoạch rehearsal (cổng #4) — bước kế tiếp nếu user vẫn muốn tiến

Chưa chạy trong job này theo đúng dispatch. Nếu được duyệt tiếp:

1. **Áp patch trên worktree tạm** (không phải repo chính), chạy lại 23 selfcheck §23 + ghi lại
   chân baseline để so — y hệt quy trình §5 ở trên.
2. **Rehearsal PaperBroker 1 phiên** trên plan LAG phiên-2/3 THẬT gần nhất (08-10 có sẵn 4 mã mang
   anchor): xác nhận (a) `load_plan()` cho trần = anchor×1,03 trên đúng 4 lệnh đó và **không lệnh
   nào khác** đổi; (b) `_limit_price` clamp tại trần mới; (c) có ca chứng minh ngược — bỏ trần thì
   giá thật sự vượt.
3. **Sửa `HARD_CEILING_BLOCK` bị hybrid nuốt (§6) TRƯỚC** — nếu không, rehearsal không quan sát
   được chính thứ cần quan sát.
4. Chỉ sau đó mới bàn LIVE, và **chỉ trên luận cứ vận hành**, kèm câu công bố rõ: "backtest NAV
   không ủng hộ; đây là đánh đổi lấy tỉ lệ khớp".

---

## Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
R=mike/agents/Taylor/exp_lag_anchor_nav_20260810/run_all.sh
bash $R none anch_L0control      # chân đối chứng → PHẢI ra md5 7d053e6201c9d107685ff4d1dd9d2d2a
bash $R 0.00 anch_LA_cap000 ; bash $R 0.01 anch_LB_cap001
bash $R 0.02 anch_LC_cap002 ; bash $R 0.03 anch_LD_cap003 ; bash $R 0.05 anch_LE_cap005
EXPA_LAG_FILLDAYS=3 bash $R none anch_W0_w3nocap
EXPA_LAG_FILLDAYS=3 bash $R 0.00 anch_WA_w3cap000
EXPA_LAG_FILLDAYS=3 bash $R 0.03 anch_WD_w3cap003
$DNA_PYEXE mike/agents/Taylor/exp_lag_anchor_nav_20260810/summarize.py
```
Log 9 chân: `exp_lag_anchor_nav_20260810/anch_*.log`. CSV: `data/..._exp_anch_*_univpit.csv`
(tên `exp_*` theo §8 — **không** canonical, **KHÔNG** pin vào `results_registry.md`;
canonical `..._wtnamecap.csv` không bị đụng).
