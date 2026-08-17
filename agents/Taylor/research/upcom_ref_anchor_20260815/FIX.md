# PHẦN 2 — Bản vá

Job `Taylor_20260815_034407` · commit **`WorkingClaude@38b6c04`** + **`mike@1533b596`**

> **SỬA LỖI (bug fix), không phải cải tiến.** Anchor luật A trước đây không phải đại lượng mà
> user chỉ định ("giá tham chiếu"), và sai đó ĐO ĐƯỢC bằng số — xem `REGRESSION.md`.

---

## 1. Nguyên tắc chọn nguồn — nêu tường minh, không chọn ngầm

Chỉ đạo yêu cầu **ghi rõ chọn phương án nào và vì sao**. Ba phương án đã cân nhắc:

| # | Phương án | Kết luận |
|---|---|---|
| A | **Đọc thẳng `q.ref` từ DNSE live** | ✅ **CHỌN** |
| B | Tự tính bình quân gia quyền từ dữ liệu khớp lệnh | ❌ loại |
| C | Tìm cột thay thế trong BigQuery | ❌ **không tồn tại** — đã kiểm, không suy đoán |

**Vì sao A**: `q.ref` là số do **chính sở giao dịch công bố** ⇒ đã đúng công thức RIÊNG của từng
sàn VÀ đã điều chỉnh theo giá trị quyền, không phải tự tính lại rồi hy vọng trùng. Đã đối soát
cơ chế (README §1.4): dựng lại bình quân gia quyền từ bar 1 phút nguồn VCI — đường dữ liệu độc
lập hoàn toàn với DNSE — trùng `q.ref` **6/7 mã UPCOM tới TỪNG TICK**.

**Vì sao KHÔNG B**: tự tính lại là tái tạo một đại lượng pháp quy từ dữ liệu thứ cấp — mọi sai
lệch định nghĩa (lô chẵn? chỉ khớp lệnh liên tục? bỏ thoả thuận?) thành sai số im lặng của
chính cái trần. Đã dùng B làm **vật đối soát** cho A, đó là đúng vai của nó.

**Vì sao KHÔNG C — đã kiểm chứ không đoán** (README §1.7):
- `INFORMATION_SCHEMA` bảng `ticker`: không cột nào mang giá tham chiếu / sàn / trần-sàn.
- `Trading_Value` **không dùng được**: `Trading_Value / Volume == Close` **tuyệt đối 24/24 dòng**
  ⇒ cột PHÁI SINH (`Volume × Close`), không phải giá trị khớp thật.
- `Price` là giá thô chưa điều chỉnh ⇒ sai ở mọi ngày GDKHQ.

### Hệ quả BẮT BUỘC phải công bố của việc chọn A
`q.ref` **chỉ đọc được SỐNG** — DNSE không có endpoint lịch sử. Vì vậy:
1. `lag_rule_a_ceiling.py` **chỉ chạy được cho phiên giao dịch KẾ TIẾP** (đã thêm cổng cứng ở
   `main()`). Chạy cho `plan_date` quá khứ sẽ gắn tham chiếu HÔM NAY vào một phiên đã qua —
   đúng loại lỗi im lặng đang sửa.
2. Hồi quy quá khứ trên chính `q.ref` là **bất khả**. `REGRESSION.md` nói rõ nó đo cái gì thay thế
   và vì sao vật thay thế đó hợp lệ.

---

## 2. Những gì đã đổi

### 2.1 `trading_bot/no_chase_ceiling.py` — nguồn luật
- **`ANCHOR_BASIS_OFFICIAL_REF`** = `"official_reference_price"`. Plan sinh bởi bản CŨ không mang
  field này ⇒ `_verify_rule_a` **fail-closed về luật cũ**. Bản vá **tự vô hiệu hoá vintage lỗi**
  thay vì trông chờ "chắc không còn plan cũ nào" — §22 coding_guidelines.
- **`check_reference_snapshot()`** — hàm THUẦN, 3 cổng **trực giao**, mỗi cổng bắt một cách hỏng
  hai cổng kia MÙ:
  - **G1 — sàn phải XÁC ĐỊNH ĐƯỢC.** Không biết sàn thì không biết tham chiếu tính theo công
    thức nào. Hỏi `exchange_known`, **không** hỏi `exchange` (xem 2.2).
  - **G2 — biên độ phải khớp sàn.** `ceiling/ref−1 ≈ +biên`, `floor/ref−1 ≈ −biên`. Tín hiệu
    TRỰC GIAO với `marketId`: chứng minh `ref/ceiling/floor` là MỘT snapshot nhất quán của CÙNG
    một phiên.
  - **G3 — tham chiếu ∈ [Low, High] phiên trước.** Bất biến của chính công thức (giá đóng hiển
    nhiên ∈ biên; bình quân gia quyền cũng ∈ biên theo cấu tạo). **Cổng DUY NHẤT bắt được
    snapshot CŨ** bị phục vụ nhầm cho phiên mới.
- **`apply_rule_a`** nhận bộ 3 `(giá, ngày, SÀN)`; sàn không xác định ⇒ KHÔNG gắn nhãn luật A.
- **`check_ref_vs_live`**: mốc sống đổi giá ĐÓNG → **`q.ref`**.

> ⚠️ **Đổi mốc này làm cổng CHẶT HƠN, không lỏng hơn.** Hai vế của phép so nay là cùng một
> trường, cùng một feed, cùng một phiên ⇒ đúng phiên thì lệch **0,0000%** (43/43 mã). Giữ mốc cũ
> trong khi anchor đã đổi cơ sở sẽ **chặn oan sạch UPCOM** — hai vế đứng trên hai định nghĩa
> khác nhau. Dung sai **GIỮ NGUYÊN 1%**, cố ý KHÔNG re-tune: đổi cơ sở giá và đổi ngưỡng cùng
> lúc thì không còn quy được thay đổi hành vi về nguyên nhân nào.

### 2.2 `trading_bot/brokers.py` — 🐞 bug phụ fail-OPEN, sửa tận gốc
```python
self.exchange = qget(raw, "exchange", "market", "floorcode", default="HOSE")   # CŨ
```
Payload DNSE **không có** key nào trong ba key đó (nó có **`marketId`**) ⇒ luôn rơi về
`default="HOSE"` cho **43/43 mã**, kể cả SHS/MBS (HNX) và DRI/SCL/TV1 (UPCOM).

Đây chính là **root cause đã được ghi nhận từ 2026-07-01** mà lúc đó chỉ chữa ở ngọn: SHS/MBS bị
DNSE từ chối **1.494 lần** ("Invalid price lot") vì `_limit_price` làm tròn theo bước giá HOSE →
vá bằng `_retry_tick_mismatch()` (thử-sai rồi học), với lý do ghi thẳng trong
`tick_retry_selfcheck.py`: *"no guessing the live JSON field name"*. **Nay tên trường đã ĐO được.**

Thêm `market_id` + `exchange_known`. **`exchange` GIỮ mặc định `"HOSE"`** có chủ đích — đường tính
bước giá không đổi hành vi, cơ chế retry vẫn là lưới an toàn; đổi cái đó là một thay đổi khác,
ngoài phạm vi sửa lỗi này. Mọi cổng fail-closed phải hỏi **`exchange_known`**.

### 2.3 `trading_bot/executor.py` — cổng live-check đổi theo cho nhất quán
`_rule_a_ref_guard(o, q)` đọc `q.ref` từ quote **đã có sẵn ở call-site** ⇒ gỡ hẳn
`_live_prev_close` / `_fetch_prev_close` / `_prev_close_cache` (**bớt 1 lời gọi `ohlc`/mã/chu
kỳ**). Ngoại lệ paper/sim giữ nguyên: broker không có client `ohlc` ⇒ bỏ qua cổng.

Toàn bộ thiết kế C1/C2 đã **đánh giá lại**, không vá chắp vá: C1 (anchor còn đúng phiên) và C2
(trần % theo `ref_price` không âm thầm thay trần luật A) giữ nguyên logic, chỉ đổi **đại lượng
được so** — vì lỗi nằm ở đại lượng, không ở cấu trúc cổng.

### 2.4 `lag_rule_a_ceiling.py` (LAG) — anchor đổi nguồn, BQ hạ vai
- Anchor: `tav2_bq.ticker.Price` → **DNSE live `q.ref`**.
- BQ giữ vai **kiểm chéo, không phải nguồn**: `Low/High` phiên đã đóng (cổng G3) + lịch phiên.
- **Cổng "chỉ phiên KẾ TIẾP"** (mới) — hệ quả bắt buộc của anchor sống.
- **`fetch_exright_on()`** — mã có GDKHQ đúng `plan_date` ⇒ **BỎ QUA luật A** + cảnh báo to.
  Giới hạn phạm vi CÓ CHỦ ĐÍCH, không phải bỏ sót: hôm đó `ref_price` và `qty` của chính lệnh
  cũng dựng trên giá/khối lượng CHƯA điều chỉnh ⇒ **cả lệnh đáng ngờ chứ không riêng cái trần**;
  sửa trần mà để nguyên sizing là vá nửa vời.

### 2.5 `mike/bin/discretionary_accumulation_inject.py` (TV1) — chân injector
`official_reference_price()` thay phần tử CUỐI của `anchors` bằng giá tham chiếu **chỉ khi**
`ceiling_rule == "A"`. `anchor_dates` GIỮ NGUYÊN (ngày vẫn là phiên ĐÃ ĐÓNG sinh ra tham chiếu ⇒
bất biến #4 không đổi nghĩa). **Nhánh mean-N (luật B) không bị chạm một dòng** — nó cố ý là trung
bình 5 phiên GIÁ ĐÓNG, một đại lượng khác hẳn.

---

## 3. FAIL-CLOSED — không đường nào fail-OPEN

| Hỏng gì | Hành vi |
|---|---|
| Không xác định được sàn | KHÔNG gắn luật A (G1) |
| Snapshot không nhất quán (biên độ sai) | KHÔNG gắn luật A (G2) |
| Tham chiếu ngoài biên phiên trước | KHÔNG gắn luật A (G3) |
| DNSE không trả quote | KHÔNG gắn trần / band cố định |
| Plan vintage CŨ (thiếu `ceiling_anchor_basis`) | `load_plan` fail-closed **về luật cũ** |
| GDKHQ đúng `plan_date` | BỎ QUA luật A + cảnh báo |
| `plan_date` không phải phiên kế tiếp | công cụ TỪ CHỐI chạy |

---

## 4. Verify

- **Selfcheck: 25/25 file trong scope map PASS.** `brokers.py` + `executor.py` là **module lõi
  dùng chung** (§23) nên quét rộng là bắt buộc — không phải phản xạ.
- **4 bộ nhạy ngày chạy lại dưới `TZ=UTC` / `America/New_York` / `Pacific/Kiritimati` /
  `env -u TZ`**: PASS đồng nhất (§16/§19).
- **Ca chứng minh ngược có thật, không vacuous**: `F10` — anchor = giá ĐÓNG SCL 23.700 (vintage
  cũ) **BỊ CHẶN** vì lệch 3,49% so tham chiếu thật 22.900. `G'7` — ca SSI ex-right bị G3 chặn đúng.
- **Hồi quy plan LIVE**: 96 plan nạp lại, **0/23 lệnh có trần đổi giá trị**; kho plan hiện tại
  chưa có lệnh luật A nào ⇒ **hành vi LIVE hôm nay KHÔNG đổi**.

---

## 5. Việc CÒN LẠI (công bố, không giấu)

1. **Ngày GDKHQ hiện chỉ BỎ QUA luật A**, chưa xử lý trọn: `ref_price`/`qty` của lệnh hôm đó
   cũng dựng trên giá chưa điều chỉnh. Cần job riêng cho toàn bộ đường sizing ngày GDKHQ.
   **Cắn ngay 2026-08-17 với SSI.**
2. **`Quote.exchange` vẫn mặc định `"HOSE"`** khi feed câm (chủ đích, mục 2.2). Đường tính bước
   giá vẫn dựa vào nó + retry. Sửa triệt để = thay `_retry_tick_mismatch` bằng bước giá suy từ
   `market_id` — thay đổi khác, cần đo riêng.
3. **Chưa xác nhận trên phiên LIVE thật** — mọi số ở đây đo từ feed quote-only + bar lịch sử.
