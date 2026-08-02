# 2026-08-02 — Hai lỗi fidelity thanh khoản sổ LAG: engine mô phỏng một đường live không đi được

**Job:** `Taylor_20260802_163657` → kết luận lại ở `Taylor_20260802_175754`
**Trạng thái:** ⏸️ **MỘT PHẦN CÒN TREO** — Việc 2 đóng, **Việc 1 KHÔNG đóng** (xem §3bis)
**Báo cáo đầy đủ:** `mike/agents/Taylor/research/liq_fidelity_and_adv_basis_20260802.md`
**Liên quan (KHÁC tầng, cùng họ cơ chế ở Việc 2):** `2026-08-02-pe-price-close-adjustment-saga.md`

> ⚠️ **quant-skeptic chấm INCONCLUSIVE** (`mike/logs/verify_20260802_173456.log`). Bản đầu của
> incident này viết TRƯỚC verdict và kết luận nhầm rằng mọi điều kiện treo đã đóng. **KHÔNG được
> trích 31,32% / 32,71% làm cơ sở kỳ vọng.** Pin R3 chính thức vẫn là **27,24%**.

---

## 0. Vì sao đây là incident RIÊNG, không phải "Phần 5" của saga Price/Close

Saga Price/Close (4 phần) xử lý cơ sở giá ở tầng **chọn rổ / định giá / trọng số**
(`custom_basket.py`, `rating_8l.py`). Incident này ở tầng **thanh khoản & khả năng khớp lệnh**:

- **Việc 1 KHÔNG liên quan gì tới Price/Close** — nó là lỗi fail-**open** trong nhánh trần %ADV.
- **Việc 2 cùng họ cơ chế** (Close đã điều chỉnh hồi tố bị dùng làm cơ sở tiền đồng) nhưng khác
  file, khác tầng, khác hệ quả (độ lớn trần + tốc độ fill, không phải chọn mã nào).

Gộp vào saga sẽ làm cả hai khó đọc. Cross-link hai chiều thay vì gộp.

---

## 1. Việc 1 — `liq<=0` được đối xử như "KHÔNG CÓ TRẦN" thay vì "KHÔNG MUA ĐƯỢC"

`simulate_holistic_nav.py` kiểm `if liq and liq > 0:` trước khi áp trần %ADV. Mã có
`Volume_3M_P50<=0` hoặc không đo được ADV rơi vào nhánh `else` ⇒ **không bị trần** ⇒ engine cho
**mua trọn size trong 1 phiên**. Đường live thì chặn nhóm này ở **CẢ HAI tầng**: tín hiệu
(`lag_filter_illiquid`, từ 07-21) và executor (`cap_lag_orders`, hard-gate fail-closed từ 07-22).

**Hình dạng lỗi:** một điều kiện phòng thủ viết theo hướng fail-**OPEN**. `liq` vắng mặt là dấu
hiệu *xấu nhất* (mã không có thanh khoản thật), nhưng code đọc nó thành *dễ dãi nhất* (miễn trần).

Root cause này **đã được phát hiện và ghi từ 2026-07-21** (`results_registry.md`, job
`Taylor_20260721_162243`) cùng bản vá `liquidity_require_positive`, nhưng để **mặc định TẮT** vì
2 điều kiện chưa thoả (vintage + giả định substitution). Job này đóng cả hai (§3) rồi bật mặc định.

---

## 2. Việc 2 — ADV tiền đồng nhân giá ĐÃ ĐIỀU CHỈNH

`ADV = Volume_3M_P50 × Close`. Nhưng `Volume_3M_P50` là **số lượng CP THÔ** — đo được
`Trading_Value == Volume × Price` khớp **100% số dòng**, `Volume × Close` thì không. Nhân `Close`
(đã điều chỉnh hồi tố) sai hai lần: **sai độ lớn** (ADV bị hạ ⇒ trần chặt oan, fill chậm oan) và
**look-ahead** (hệ số `Close/Price` tại ngày *t* phụ thuộc sự kiện quyền SAU *t*).

**Điểm quan trọng nhất về phạm vi — và là chỗ dispatch bắt phải kiểm trước khi sửa:** công thức
này nằm ở **3 điểm** phục vụ **cả live lẫn mô phỏng**, cố ý giữ giống hệt nhau:

| # | Vị trí | Vai |
|---|---|---|
| 1 | `lag_liquidity_filter.py` (SQL) | LIVE — lọc tầng tín hiệu (chỉ dùng phép thử `>0`) |
| 2 | `trading_bot/due_diligence.py:adv_vnd` | LIVE — **độ lớn trần** hard-gate `cap_lag_orders` |
| 3 | `pt_v23_audit_2014.py` (`liq_lag`) | MÔ PHỎNG — tốc độ fill sổ LAG |

⇒ Đánh giá ban đầu "chỉ live, dọn dẹp rẻ và an toàn" là **SAI**. Sửa 1 điểm mà bỏ 2 điểm kia sẽ
**phá bất biến "trần live == trần đã mô phỏng"** — chính bất biến mà `cap_lag_orders` tồn tại để
giữ. Đã sửa **đồng thời cả 3**.

---

## 3. Hai điều kiện treo của pin 07-21 — đóng cả hai, NHƯNG có điều kiện thứ BA (xem §3bis)

Pin 07-21 tự đánh dấu **PIN TẠM**. Job này đóng nốt:

| Điều kiện 07-21 | Trạng thái nay |
|---|---|
| **#1 Vintage** — phải chạy lại trên cache `verified:true`, không phải live BQ | **ĐÓNG** — chạy trên snapshot đóng cứng `bq_cache_asof20260729_postrestate` = đúng vintage số pin; chân đối chứng tái lập pin **chính xác** |
| **#2 Substitution** — engine cho vốn chảy ngay sang ứng viên kế tiếp, còn live (chỉ chặn ở executor) thì để tiền nằm im ⇒ 31,33% chỉ là **cận trên** | **ĐÓNG** — từ 07-21 live đã có lọc **tầng tín hiệu** `lag_filter_illiquid`, nên sổ live tự chọn ứng viên kế tiếp **đúng như engine**. Đây chính là "việc cần quyết #3" của 07-21 và nó đã làm rồi |

⇒ Khoảng `[~27,2%; ~31,3%]` ghi trong registry/current_ops **hết hiệu lực**: đó là khoảng *chưa
đo được* dựng từ pin tạm. **NHƯNG không có khoảng mới thay thế** — xem §3bis.

---

## 3bis. ĐIỀU KIỆN THỨ BA — chưa ai liệt kê, và nó mới là điều kiện chặn

Job này đi kiểm đúng 2 điều kiện đã được liệt kê sẵn từ 07-21, rồi kết luận "đóng hết". Sai ở
chỗ: danh sách 07-21 **không đầy đủ**. Điều kiện thật sự quyết định là **phân rã cơ chế của Δ**,
và nó đã nằm sẵn trong docstring `lag_liquidity_filter.py:28-31` từ trước ("CHƯA PHÂN RÃ
ĐƯỢC… RỦI RO CÒN MỞ"), kèm lời dặn thẳng *"ĐỪNG dùng +4,11pp làm cơ sở kỳ vọng"*.

**Objection quyết định (quant-skeptic, nguyên văn):**
> *"The +4.08/+4.11pp delta this finding certifies as 'reproducible and robust' is the SAME number
> the codebase's own `lag_liquidity_filter.py` docstring already flags as mechanism-undecomposed
> after two prior refuted explanations: TREAT enters 30% more LAG orders but completes 16% fewer
> positions, with abandonment rising 59.2%→73.8%. If that's driven by the 25B LAG book being
> unable to fill its own target sizing (a capacity artifact) rather than genuine capital
> reallocation to better opportunities, the entire delta is a fill-model artifact, not a real edge."*

Hai giả thuyết — *vốn chảy sang event LAG tốt hơn* (edge thật) vs *sổ 25B không fill nổi size mục
tiêu* (hiện vật mô hình fill) — **để lại CÙNG một dấu vết trên CSV**. Đây là **lần thứ BA** câu
hỏi này không được trả lời (2 lần trước: cả hai cách giải thích đều bị REFUTED).

**Điều KHÔNG bị tranh cãi:** 5/7 check PASS, tái tính độc lập — không có look-ahead mới,
self-check 0 VND, L0 tái lập pin bit-for-bit, IS/OOS khớp, LOO 13/13, cờ nhị phân không phải
tham số quét. Toàn bộ chỗ đó trả lời câu *"phép đo có tái lập được không"* (có), **không** trả
lời câu *"Δ này có phải alpha thật không"* (chưa biết). **DSR=1,0000 cũng không cứu được**: nó
chỉ khử multiple-testing, một Δ do capacity-artifact vẫn cho DSR≈1,0 y hệt.

### Quyết định (job `Taylor_20260802_175754`)
| Thành phần | Quyết định | Căn cứ |
|---|---|---|
| **Việc 2** `LAG_ADV_BASIS` (3 điểm) | **GIỮ, mặc định `price`** | Căn cứ RIÊNG, độc lập với mọi số NAV: gỡ look-ahead thật + giữ bất biến parity *live == mô phỏng* (đường live đã dùng `price`; hoàn nguyên riêng engine sẽ **phá** bất biến). quant-skeptic không nêu objection riêng nào cho phần này. Tác động live đo được: **0 lệnh đổi** |
| **Việc 1** code + knob | **GIỮ** | Logic đúng (không mua được thì đừng đặt mục tiêu), cần cho lần phân rã sau |
| **Việc 1 — mặc định** | **HOÀN NGUYÊN `"lag"` → `""` (opt-in)** | Bật cờ = toàn bộ nguồn của Δ đang INCONCLUSIVE. Để mặc định BẬT thì mọi backtest sau này mặc nhiên mang Δ chưa phân rã vào số của nó — "wire" số NAV bằng cửa sau |

⇒ Chấp nhận **có chủ đích** một độ lệch fidelity **đã biết, đã đo** (cận trên +4,08pp) giữa engine
và live, thay vì đóng nó bằng một con số chưa hiểu. Hệ quả: pin R3 **27,24%** nhiều khả năng là
**cận DƯỚI**, còn cận trên **chưa biết**.

⚠️ Lưu ý phân định, đừng đọc rộng hơn thực tế: verdict INCONCLUSIVE là cho **toàn bộ finding**;
hai objection thì truy được về **Việc 1**. Điều đó **không** có nghĩa quant-skeptic đã CONFIRM
riêng Việc 2 hay số 28,86% — nó **không xét riêng** phần đó. Việc 2 merge trên **căn cứ thiết
kế**, không phải trên uy tín một con số NAV.

---

## 4. Số (A/B 4 chân, snapshot đóng cứng, threads=1)

| Chân | `LIQ_ZERO_BLOCK` | `LAG_ADV_BASIS` | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|
| **L0** đối chứng | off | close | **27,24%** | 1,81 | −18,4% | 1,48 |
| L1 chỉ Việc 1 | lag | close | 31,32% | 1,88 | −18,8% | 1,67 |
| L2 chỉ Việc 2 | off | price | 28,86% | 1,90 | −17,8% | 1,62 |
| **L3 cả hai** | lag | price | **32,71%** | 1,95 | −19,1% | 1,71 |

L0 tái lập số pin hiện hành **chính xác** (kể cả NAV cuối 1.006,33B) ⇒ A/B hợp lệ. Self-check
**0 VND** cả 4 chân. LOO trên Δ **dương 13/13** ở cả 3 cặp. DSR(L3) **1,0000**. Bootstrap MaxDD
5th-pct **−30,2%** ⇒ **anchor DD ~−30% GIỮ NGUYÊN**, không dùng −19,1% làm kỳ vọng.

Δ **không cộng tuyến tính** (4,08 + 1,62 = 5,70 > 5,47 thực đo) — hai bản sửa giao thoa vì cùng
tác động lên một cơ chế (khả năng/tốc độ fill sổ LAG). Vì vậy **phải chạy L3 thật**, không được
cộng L1+L2.

🔴 **Mọi số ở bảng trên là ĐO ĐƯỢC và tái lập được — nhưng L1/L3 KHÔNG phải kỳ vọng** (§3bis).
Chân duy nhất được dùng làm số pin vẫn là **L0 = 27,24%**. Chạy engine **mặc định** hôm nay ra
**L2 = 28,86%** (vì Việc 2 bật, Việc 1 tắt) — số này **cũng chưa phải pin**: re-pin R3 sang cơ sở
`price` là món **NỢ CHƯA LÀM**, cần cổng riêng. Muốn tái lập đúng pin 27,24% ⇒ `LAG_ADV_BASIS=close`.

---

## 5. BÀI HỌC

### 5.1. "Tác động = 0 vì Close ≈ Price hôm nay" là suy luận SAI khi hệ thống replay lịch sử
Bài học này đã được nêu ở saga Price/Close (#2) và incident này **định lượng nó**: median
`Close/Price` **đơn điệu** 0,443 (2014) → 1,000 (2026). Ở 2014 ADV bị hạ **2,26 lần**. Một hàm
"chỉ chạy live" vẫn sai nghiêm trọng ngay khi có ai đó replay nó qua lịch sử — và ở đây engine
backtest dùng **đúng công thức đó**.

Hệ quả tích cực: cùng con số này **giải thích** bất đối xứng IS/OOS của Việc 2 (IS +3,28pp, OOS
+0,02pp) — phần hơn **tỉ lệ thuận với độ lớn của chính lỗi đang sửa**, và ~0 đúng nơi lỗi ~0.
Chữ ký này **ngược hẳn** reshuffle-luck (bài học MOM/Wave1). Dose-response là cách rẻ nhất để
phân biệt "sửa lỗi thật" với "tinh chỉnh cho số đẹp".

### 5.2. Điều kiện phòng thủ phải fail-CLOSED; thiếu dữ liệu ≠ được miễn kiểm
`if liq and liq > 0:` đọc "không đo được thanh khoản" thành "miễn trần". Mọi gate mà dữ liệu vắng
mặt đưa tới nhánh **dễ dãi hơn** đều là lỗi chờ nổ, kể cả khi comment nói đúng ý định.

### 5.3. Khi một công thức là BẤT BIẾN PARITY giữa live và mô phỏng — sửa ĐỒNG THỜI mọi điểm
Trước khi sửa "một hàm live", phải trả lời: công thức này còn ai chép không? Ở đây là 3 điểm và
2 trong 3 nằm ngoài file đang mở. Sửa lệch pha sẽ phá đúng cái bất biến mà gate sinh ra để bảo vệ.

### 5.4. "Selfcheck PASS" mà không nói chạy ở chế độ nào là báo cáo THIẾU
`lag_liq_signal_filter_selfcheck.py` cho **13 PASS** khi chạy trần, **22 PASS** với `--live` —
và **toàn bộ positive control cơ sở giá nằm sau cờ `--live`**. Chạy mặc định rồi báo "PASS" sẽ
bỏ sót đúng phần kiểm chứng bản sửa này. Khớp `verify-before-done` §nêu tên phụ thuộc môi trường.

### 5.5. ⚠️ Cron auto-backup CUỐN việc R&D đang dở vào commit — lần này trúng CODE, không phải `kb/`
Attempt 1 hết lượt giữa chừng, để code chưa commit ở working tree. Cron `auto-backup` 17:00 UTC
`git add -A` **blanket** đã gói toàn bộ vào commit `11d28ca "auto-backup 2026-08-02T17:00:01Z"` —
một commit message vô nghĩa cho một thay đổi chạm đường live, và `git status` sạch làm attempt 2
suýt kết luận "attempt 1 không làm được gì" rồi làm lại từ đầu.

Đây là **cùng root cause** với `coding_guidelines.md §13` (viết cho `kb/`) nhưng §13 chỉ nói về
file `kb/`, nên không ai áp nó cho code R&D. Cách phòng đúng vẫn là của §13: việc dở có nguy cơ
bị cắt → **ghi `remember.sh` NGAY** + biết rằng working tree **không phải** nơi an toàn để "giữ
tạm chờ duyệt" trên repo này. Không đề xuất đổi cron (backup blanket là chủ ý, và mất backup
nguy hiểm hơn commit message xấu) — đề xuất là **đừng tin `git status` sạch = chưa ai làm gì**:
luôn `git log` khoảng thời gian của attempt trước.

---

## 6. Tác động LIVE (đo, không suy đoán)

Việc 2 nới trần `cap_lag_orders` theo hệ số `1/(Close/Price)`. Trên rổ ứng viên LAG thật
(asof 2026-07-31, 152 mã): **1 mã duy nhất (DNN, 0,7%)** có `Close≠Price`, và DNN **đã bị loại ở
tầng tín hiệu** ⇒ **0 lệnh thật đổi**. Đúng như dose-response dự báo (2026 ratio = 1,000).

Vẫn là **thay đổi chạm LIVE** (nới một hard-gate) ⇒ báo cáo tường minh cho user/Mike duyệt theo
mandate Taylor, không tự coi là dọn dẹp nội bộ.

---

## 7. Việc còn TREO — đề xuất, CHƯA LÀM (Mike/user quyết có mở sprint riêng)

Mục tiêu duy nhất: **tách capital-velocity thật khỏi capacity/fill-shortfall artifact**. Cả 3 việc
đều **không cần chạy lại backtest** — dữ liệu đã nằm trong 2 CSV audit L0/L1.

1. **Hạ NAV (đề nghị làm TRƯỚC)** — chạy L0/L1 ở quy mô **5–10B**, nơi capacity **không** phải
   ràng buộc. Δ **teo về ~0** ⇒ artifact; Δ **giữ nguyên** ⇒ edge thật. Phép thử falsifiable rẻ
   nhất và cắt trực diện đúng câu hỏi.
2. **Truy vốn trên chuỗi `ENTRY_FILL`/`ABANDONED_REFUND`** — mỗi lệnh bị chặn ở L1, vốn đó đi
   đâu: (a) event LAG khác *hoàn tất*, (b) event khác rồi *cũng bỏ dở*, (c) **nằm im**. (b)+(c)
   chiếm phần lớn ⇒ Δ là hiện vật.
3. **Chất lượng vốn được giải phóng** — vốn ở L1 có rơi vào event LAG *tốt hơn thật* không (phân
   tầng earnings-surprise tercile), hay chỉ parking/idle-cash?
4. (Nếu vẫn muốn tiến) cross-check `ticker_prune` live-BQ cho L1 — quant-skeptic lưu ý 31,32%
   vượt trần auditable ~25,7–27,7% của doctrine ở quy mô NAV này.

**Món nợ riêng, không phụ thuộc mấy việc trên:** re-pin R3 sang cơ sở ADV `price` (L2 = 28,86%)
qua một cổng re-pin đầy đủ — hiện engine mặc định đã chạy `price` nhưng pin vẫn là số `close`.

---

## 8. Tham chiếu

- Verdict quant-skeptic: `mike/logs/verify_20260802_173456.log` (**INCONCLUSIVE**, confidence medium)
- Báo cáo: `mike/agents/Taylor/research/liq_fidelity_and_adv_basis_20260802.md`
- Harness/log/CSV: `data/liqadv_ab_20260802/`
- Nguồn root cause Việc 1: `data/results_registry.md` §"2026-07-21 — RE-PIN R3 (SỬA ENGINE `liq<=0`)"
- Saga cùng họ cơ chế (khác tầng): `2026-08-02-pe-price-close-adjustment-saga.md`
