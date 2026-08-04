# P0 bootstrap snapshot — day-0 book state cho cơ chế journal book-tagging

**Job** `Taylor_20260804_012929` · **Ngày** 2026-08-04 · **Tác giả** Taylor
**Tiền đề**: `research/park_unpark_live_wiring_20260803.md` mục **F3** ("bootstrap snapshot cần người xác
nhận, không tự sinh được; thiếu nó L1 sẽ im lặng không trim gì") và mục **G** dòng 4.

**KHÔNG sửa file production nào.** Đầu ra là 2 file `.json.proposed` (điều 13 coding_guidelines) —
`find data/trade_plans -name 'plan_*.json' -newermt '2026-08-04 01:29'` trả về **rỗng** (không file plan
thật nào bị chạm).

| | |
|---|---|
| Output SpaceX | `data/trade_plans/bootstrap_book_snapshot_SpaceX_20260804.json.proposed` — 24 lô / 21 mã |
| Output ZaloPay | `data/trade_plans/bootstrap_book_snapshot_ZaloPay_20260804.json.proposed` — 22 lô / 16 mã |
| Script tái lập | `mike/agents/Taylor/bootstrap_book_20260804/` (`build_ledger.py` → `reconcile.py` → `emit_proposed.py`) |
| Nguồn broker | `data/execution_logs/dnse_raw_2026-08-03.jsonl`, `kind=positions`, lọc `account_no` ngay dòng đầu (điều 12) |

---

## 0. Kết quả một dòng

**Đối soát khớp TUYỆT ĐỐI cả 2 account** — `diff = 0` trên **mọi mã đang giữ** (SpaceX 21/21,
ZaloPay 16/16). Không có vị thế nào rơi vào `UNRESOLVED`. Thiết kế mục F đã đoán rằng lịch sử sẽ
không truy được (§A7 "live KHÔNG có sổ quy vị thế về book"); thực tế **truy được đầy đủ** — vì
`journal.parent_id == PlannedOrder.id`, và plan JSON **đã** mang sẵn `book`/`play_type` từ ngày
đầu go-live. Đó là bằng chứng **tại thời điểm mua**, không phải suy luận theo tên mã.

## 1. Trạng thái day-0 (2026-08-04, giá DNSE 08-03)

**SpaceX (0002023347)** — tổng MV cổ phiếu 945,01tr VND

| Book | Số cp | MV (VND) | % MV | Mã |
|---|---:|---:|---:|---|
| PARK (custom30V_parking) | 20.100 | 642.455.000 | 68,0% | ACB BID CTG HDB LPB MBB SHB SHS TCB TPB VCB VHM VIX VND VPB |
| CAPIT | 7.700 | 294.755.000 | 31,2% | NCT PVT SAB SIP VNM |
| DISCRETIONARY_SPECIAL | 400 | 7.800.000 | 0,8% | TV1 |
| **LAG** | **0** | **0** | **0%** | — |

**ZaloPay (0001743768)** — tổng MV cổ phiếu 889,71tr VND

| Book | Số cp | MV (VND) | % MV | Mã |
|---|---:|---:|---:|---|
| EXCLUDED | 10.000 | 394.000.000 | 44,3% | DGC |
| PARK | 7.219 | 279.775.200 | 31,4% | BID CTG HDB LPB MBB TCB VCB VHM **VPB(1.100)** |
| CAPIT | 4.538 | 176.388.150 | 19,8% | NCT PVT SAB SIP VNM |
| LAG | 1.700 | 39.550.000 | 4,4% | CSV(1.000) **VPB(700)** |

---

## 2. Ca mơ hồ #1 — VPB ở SpaceX: nhãn `LAG/PARK` của plan **BỊ BÁC BỎ**, 100% là PARK

Dispatch nêu đây là ca không phân định được. Lịch sử fill **phân định dứt khoát**:

| Ngày | Lệnh | Chiều | Qty | VWAP | `book` trong plan |
|---|---|---|---:|---:|---|
| 2026-07-02 | `BUY-VPB-03` | mua | 5.600 | 27.914,3 | `custom30V_parking` / `NEUTRAL_park` (lệnh VPB trong plan 07-01 không khớp, gộp sang 07-02) |
| 2026-07-06 | `SELL-VPB-03` | bán | 3.300 | 27.750,0 | `custom30V_parking` |
| | **còn lại** | | **2.300** | | **PARK** |

**SpaceX CHƯA TỪNG có một lệnh mua VPB nào mang `book=LAG`** — quét toàn bộ 29 plan file + 10 journal
file của account. Nhãn `book_note: "LAG/PARK"` xuất hiện lần đầu ở `plan_SpaceX_2026-07-28.json` và
được chép lại tới `2026-08-04`, kèm `existing_lag_holds: [{ticker: VPB, book: "LAG/PARK",
note: "WINDOW_PASSED 2026-07-27"}]`. Đó **đúng là dạng lỗi §A7 mô tả**: plan generator thấy VPB có
tín hiệu LAG quanh 07-27 rồi gán nhãn cho vị thế ĐANG GIỮ, trong khi vị thế đó đến từ rotation PARK
5 tuần trước và tín hiệu LAG kia **không được thực thi** (không có lệnh nào).

**Ca thứ hai cùng bệnh, dispatch chưa nêu: VND ở SpaceX.** `plan_SpaceX_2026-07-31.json` ghi
`{ticker: VND, qty: 300, book: "LAG", note: "WINDOW_PASSED 2026-07-27, đang giữ theo hold 25td"}`.
Lịch sử fill: mua 400cp 07-01 `book=custom30V_parking`, bán 100cp 07-06 `book=custom30V_parking`
→ 300cp còn lại **100% PARK**. Cũng chưa từng có lệnh mua VND nào `book=LAG`.

> **Hệ quả cho L1**: nếu lấy nhãn từ plan artifact, SpaceX có "2 vị thế LAG" (VPB 2.300 × 25.500 +
> VND 300 × 16.850 = **63,71tr VND**) và `park_mv_live` bị **thiếu 63,71tr** (642,46tr → 578,75tr,
> tức **−9,9%** sổ PARK).
> Đây chính xác là chế độ hỏng "im lặng không trim gì" mà F3 cảnh báo. Snapshot này chặn nó.
> **Cần user xác nhận** vì kết luận này mâu thuẫn với một artifact plan đang sống.

## 3. Ca mơ hồ #2 — VPB ở ZaloPay: tách lô **1.100 PARK + 700 LAG**, số lượng được broker tự xác nhận

| | |
|---|---|
| Lô legacy | 7.500cp, `createdDate` 2025-11-20, `costPrice` 27.886,7 — có trước khi bot quản lý, **không có FILL** trong journal (snapshot broker đầu tiên: `dnse_raw_2026-07-06.jsonl`) |
| Trim | 8 lần × 800cp (07-15, 16, 17, 20, 21, 22, 23, 27) = **6.400cp**, mọi lệnh `book=custom30V_parking` (từ 07-22 thêm `play_type=PARK_TRIM`) |
| Mua mới | 07-27 `BUY-VPB-01` **700cp** @24.950, `book=LAG`, `play_type=LAG_LO` |
| Còn lại | 7.500 − 6.400 = **1.100 PARK** + **700 LAG** = 1.800 = `openQuantity` của broker ✓ |

**Xác nhận độc lập bằng giá vốn của chính broker** (không dùng dữ liệu của tôi):
`(1.100×27.886,7 + 700×24.950)/1.800 = 26.744,65` — DNSE báo `costPrice = 26.744,6297`. Nếu cả
1.800cp đều là lô legacy thì giá vốn phải là 27.886,7. **Vậy phép tách theo SỐ LƯỢNG là chắc chắn.**

Ghi chú thêm: `net_offsetting_orders()` (plan.py:169) **KHÔNG** được áp cho cặp lệnh 07-27 này —
journal có 2 parent order riêng biệt và `accumulateQuantity` của broker là 8.200 (= 7.500 + 700),
`closedQuantity` 6.400. Cả 2 chân đều đi ra broker.

**Cái CẦN NGƯỜI QUYẾT** không phải số lượng mà là **nhãn book của 1.100cp legacy**:
- *PARK* — plan đối xử nó như một slot của rổ custom30V và trim theo tỷ trọng (8 lệnh liên tiếp).
- *LEGACY_ORPHAN* — 5 vị thế legacy khác của cùng account (MSH/TCM/TLG/VHC/VIB) được gắn
  `book=legacy_orphan` khi thanh lý. VPB được đối xử khác **vì nó nằm trong rổ custom30V**.
- Tác động: 1.100 × 25.500 = **28,05tr VND** vào/ra `park_mv_live` của ZaloPay.

## 4. Ca mơ hồ #3 — LPB 900cp ở SpaceX: plan **thiếu** trường `book`

`plan_SpaceX_2026-07-15.json` dùng schema cũ, 2 lệnh (`SELL-HPG-00` 2.200, `BUY-LPB-01` 900) **không
có** trường `book`. Suy ra PARK từ văn bản **trong chính plan đó**, không phải từ tên mã:
`strategy = "v24_custom30v"`; `allocation_strategy.rule = "neutral_parking v2.1 + basket_drift_swap"`;
`buy_note = "Mua LPB 900 cổ để thay thế HPG (basket swap, weight 5.22% trong CUSTOM30V_8L)"`;
`allocator_w_lag.actionable = false` kèm `"BAL/LAG đều có 0 active deals"`. Bằng chứng rất mạnh, vẫn
gắn cờ `needs_user_confirmation` vì nó là **suy luận**, không phải trường dữ liệu.

## 5. Khe hổng thật phát hiện được: **journal bỏ sót fill khớp ở ATC**

Ca VHC/ZaloPay 2026-07-10: plan bán 1.800cp; journal `exec_ZaloPay_2026-07-10_journal.csv` chỉ ghi
**1.200cp** (FILL cuối 14:29:59). Nhưng snapshot broker lúc **15:00:11** trong cùng file
`dnse_raw_2026-07-10.jsonl` cho `openQuantity=0 / closedQuantity=1.800` — **600cp khớp ở phiên ATC
sau khi vòng poll của executor đã kết thúc**.

> **Journal KHÔNG phải bản ghi đầy đủ của fill.** Sổ lô dựng thuần từ journal sẽ SAI mỗi khi lệnh
> khớp ở ATC. Hai hệ quả cho thiết kế mục F:
> 1. Đối soát hằng ngày với `openQuantity` (F4) là **BẮT BUỘC**, không phải tuỳ chọn — nó là thứ
>    duy nhất bắt được lớp fill này.
> 2. Nên bổ sung **một lần đọc broker sau ATC** (~15:05) vào cuối phiên, nếu không mỗi ngày có lệnh
>    khớp ATC sẽ đẻ ra một lệch phải xử lý tay.
>
> **Không ảnh hưởng snapshot này**: VHC đã bán hết (`openQuantity=0`) nên không có mặt; mọi mã
> **đang giữ** đối soát khớp tuyệt đối. Tôi **không** tự bù 600cp cho khớp (điều 5: không đoán-rồi-gộp).

## 6. Chênh giá vốn = **cổ tức tiền mặt**, không phải sai sót

Bootstrap ghi giá **THỰC TRẢ** (VWAP từ journal); DNSE điều chỉnh GIẢM `costPrice` đúng bằng cổ
tức/cp. Chênh đo được (VND/cp): **NCT 8.000 · SAB 3.000 · MBB 1.000 · BID/CTG/VCB 450**. Nhất quán
chéo 2 account theo ngày ex (MBB: lô SpaceX mua 07-02 bị điều chỉnh, lô ZaloPay mua 07-10 thì
không ⇒ ex-date nằm giữa 07-06 và 07-10).

**Số lượng đối soát khớp tuyệt đối ở mọi mã ⇒ không có cổ tức CỔ PHIẾU / chia tách nào trong giai
đoạn này** (khe hổng "sự kiện quyền" ở bảng F4 hiện **chưa** phát sinh). Mọi tỉ suất per-position
vẫn phải đi qua `mike/bin/dividend_adjusted_return.py` — điều 21.

## 7. Bẫy đã né (ghi lại để lần sau không phải khám phá lại)

1. **`qty` trên dòng FILL là TÍCH LUỸ theo `child_oid`** (bẫy số 1, F2) — cộng dồn thô sẽ đếm trùng.
   Đã lấy `delta = qty(dòng này) − qty(dòng trước CÙNG child_oid)`.
2. **`plan_main_*` / `exec_main_*` KHÔNG phải SpaceX** — label `main` là account **PHS paper**
   (`secrets/trading_bot_accounts.json`, `mode: "paper"`). Gộp nhầm sẽ thổi phồng cả 2 sổ.
3. **Lọc `account_no` ngay dòng đầu** khi đọc `dnse_raw_*.jsonl` (điều 12) — 2 account nằm chung file.
4. FIFO chạy **trong cùng book**; ở đây may mắn là bài toán không nhạy thứ tự (SpaceX không mã nào
   mua cả 07-01 lẫn 07-02; cặp mua/bán VPB ZaloPay 07-27 nằm ở 2 book khác nhau).

## 8. Việc còn treo — cần Mike/user quyết trước khi L1 dùng được

| # | Việc | Ai quyết |
|---|---|---|
| 1 | Xác nhận **VPB 2.300 + VND 300 ở SpaceX là PARK**, và sửa/gỡ nhãn `LAG/PARK`·`existing_lag_holds` trong plan generator để không tái sinh nhãn sai | user |
| 2 | Chọn nhãn cho **VPB 1.100cp legacy ở ZaloPay**: `PARK` (đề xuất) hay `LEGACY_ORPHAN` — 28,05tr VND | user |
| 3 | Xác nhận **LPB 900 SpaceX = PARK** (suy từ văn bản plan 07-15) | Mike đủ |
| 4 | Duyệt xong → `mv <file>.proposed <file>.json`, rồi mới bật tag `book`/`play_type` ở `Executor._journal()` (F1) và cho FIFO chạy tiến từ snapshot này | Mike |
| 5 | Thêm 1 lần đọc broker **sau ATC** vào cuối phiên (khe hổng §5) — nếu không, mỗi phiên có lệnh khớp ATC sẽ đẻ một lệch phải xử lý tay | Mike/Winston |

**Snapshot này là dữ liệu người phải xác nhận, không phải Taylor tự quyết.** Trước khi được duyệt,
**cấm** dùng nó làm cơ sở sinh lệnh trim (cùng tinh thần điều 21 và F2 mục 4).
