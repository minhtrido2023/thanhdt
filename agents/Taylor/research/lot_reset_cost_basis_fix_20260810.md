# Vá bug kế toán lô — giá vốn bình quân gia quyền không reset khi vị thế về 0 (LPB)

**Job:** `Taylor_20260810_044215` · **Ngày:** 2026-08-10
**File sửa:** `mike/bin/verify_account_snapshot.py` (+ selfcheck mới)
**Loại:** sửa bug kế toán lô. KHÔNG đụng tiền thật, KHÔNG đổi logic giao dịch, KHÔNG đụng công
thức cổ tức (user đã chốt giữ nguyên `total_return = (P_end + D_net − cost)/cost`).

---

## 1. Kết luận một dòng

`verify_account_snapshot.py` tính giá vốn bằng `Σbuy_value / Σbuy_qty` **cộng dồn cả đời**, nên khi
một mã bán sạch rồi mua lại thì lô đã tất toán vẫn bị trộn vào lô mới. Đã thay bằng bình quân gia
quyền **theo lô đang sống** (`CostBook`): bán bớt rút cơ sở giá vốn theo tỉ lệ, vị thế về 0 thì cơ
sở về 0. LPB (SpaceX) ra đúng **51.466,67** khớp `costPrice` broker; **20 mã SpaceX + 15 mã ZaloPay
còn lại không đổi một đồng** (kiểm ở cả hai mốc 07/08 và 10/08).

## 2. Cơ chế hỏng

```
main():  raw_agg[tk] = [net_qty, buy_qty, buy_value]   # cộng dồn qua MỌI ngày
         cost = buy_value / buy_qty                     # chia MỘT LẦN ở cuối
```

Công thức này chỉ đúng khi vị thế **chưa từng về 0 và chưa từng bán bớt rồi mua thêm**. Nó không
có khái niệm "lô", nên không thể biết chuỗi mua–bán–mua đã cắt đôi lịch sử.

Ca thật LPB/SpaceX (đọc thẳng từ `dnse_raw`, `accountNo=0002023347`):

| Ngày | Chiều | KL | Giá |
|---|---|---:|---:|
| 01/07 | mua | 900 | 53.700 |
| 06/07 | bán | 100+200+200+400 = **900** | 51.200–51.500 |
| 15/07 | mua | 100+300+100+200+200 = **900** | 51.300–51.600 |

- Đúng: giá vốn = trung bình lô 15/07 = 46.320.000 / 900 = **51.466,67**
- Cũ: (900×53.700 + 46.320.000) / 1.800 = **52.583,33** — lệch **+1.116,67đ/cp**

## 3. Bản vá

- **`CostBook`** (class mới): `buy()` cộng KL + tiền vốn; `sell()` rút cơ sở giá vốn **theo tỉ lệ**
  tại giá bình quân hiện hành (nên bán bớt không làm đổi giá bình quân — đúng weighted-average), và
  khi KL về 0 thì đặt `qty = basis = 0`, đếm `resets += 1`.
- **`dnse_fill_events()` / `journal_fill_events()`**: trả về từng fill rời **đã sắp theo thời gian**
  thay vì gộp sẵn theo ngày ⇒ nhận diện được vị thế về 0 **cả trong cùng một ngày**, không chỉ giữa
  các ngày. `true_fills_from_dnse_raw()` / `true_fills_from_journal()` giữ nguyên chữ ký (dựng lại
  từ event qua `aggregate_events()`) nên selfcheck corp-action và mọi caller cũ không đổi.
- **`build_cost_books()`**: chạy CostBook theo trình tự, áp `corp_action_multiplier` **từng fill**
  (giữ nguyên quy ước ex_date/asof cũ). Tự `sorted()` theo ngày — truyền `--dates` lộn xộn vẫn đúng.
- `main()`: giá vốn lấy từ `raw_books[tk].avg_cost`; **cross-check dnse_raw vs journal cũng đổi sang
  cùng quy ước** (nếu chỉ đổi một bên sẽ đẻ cảnh báo giả ở đúng những mã đã tất toán rồi mua lại).
- Thêm dòng `INFO <MÃ>: vị thế đã về 0 N lần rồi mua lại …` vào `warnings` + field
  `cost_basis_lot_resets` trong JSON — để người đọc báo cáo thấy được vì sao giá vốn khác kỳ vọng
  ngây thơ, thay vì phải tự phát hiện lại.

**Hệ quả phụ đã lường:** quy ước mới cũng sửa ca "bán bớt rồi mua thêm" (cũ: `(q₁p₁+q₂p₂)/(q₁+q₂)`;
đúng: bình quân chạy trên phần còn lại). Trong toàn bộ lịch sử hiện có **không mã nào rơi vào ca
này**, nên bản vá không đổi số nào ngoài LPB — nhưng logic đã đúng cho tương lai.

## 4. Kiểm chứng

### 4.1 Toàn bộ danh mục, 2 mốc, đối chiếu `costPrice` broker

Script: `mike/agents/Taylor/exp_lot_reset_20260810/compare_cost.py` (tính OLD và NEW song song trên
cùng dữ liệu, so với `costPrice` trong bản ghi `positions` của broker).

| Mốc | Tài khoản | Số mã | Mã đổi số | Kết quả |
|---|---|---:|---|---|
| 07/08 | SpaceX | 20 | **LPB** 52.583,33 → 51.466,67 | khớp `costPrice` broker tuyệt đối |
| 07/08 | ZaloPay | 14 | không mã nào | — |
| 10/08 | SpaceX | 21 | **LPB** (giữ 200cp sau khi bán 300 sáng 10/08) | khớp `costPrice` broker |
| 10/08 | ZaloPay | 15 | không mã nào | — |

Mọi mã còn lại: `NEW − costPrice` **= 0**, hoặc **= đúng cổ tức GỘP** ở 6 mã có cổ tức (BID/CTG/VCB
450, MBB 1.000, SAB 3.000, NCT 8.000) — đó là quy ước DNSE tự trừ cổ tức khỏi giá vốn, đã biết từ
báo cáo trước, **không** phải sai lệch mới.

### 4.2 Selfcheck mới — `verify_account_snapshot_lot_reset_selfcheck.py`

**25/25 PASS**, PASS y hệt dưới `env -u TZ`, `TZ=America/New_York` và cwd khác (§16).
Mọi ca "chặn được" đều kèm **ca chứng minh ngược** — tính lại bằng công thức CŨ trên cùng dữ liệu
và xác nhận nó **thật sự** ra số sai:

| Ca | Nội dung |
|---|---|
| 1 | mua → bán sạch → mua lại ⇒ chỉ lô mới; chứng minh ngược: công thức cũ ra 52.583,33 |
| 2 | bán bớt **không** làm đổi giá bình quân; cơ sở rút theo tỉ lệ |
| 3 | bán bớt rồi mua thêm ⇒ 16.666,67; chứng minh ngược: công thức cũ ra 15.000 |
| 4 | về 0 rồi mua lại **3 lần** ⇒ mỗi lần reset |
| 5 | bán quá KL trace được (vị thế legacy) ⇒ KL âm giữ nguyên dấu (cảnh báo lệch KL vẫn nổ), avg = 0 |
| 6 | bán sạch bằng **4 lệnh lẻ** (đúng chuỗi LPB 06/07) ⇒ vẫn nhận diện về 0, không dư float |
| 7 | end-to-end trên `dnse_raw` **THẬT** ⇒ 51.466,67; chứng minh ngược ⇒ 52.583,33 |
| 8 | truyền ngày **lộn xộn** vẫn ra cùng kết quả |
| 9 | 20 mã không-reset giữ **nguyên** giá vốn; đúng 1 mã ĐANG GIỮ bị đổi số và đó là LPB |

Fixture đóng băng (3 ngày lịch sử 01/07 · 06/07 · 15/07), không đọc trạng thái sống ⇒ không tự mốc
theo thời gian (§23 hệ luận 1).

> **Selfcheck đã bắt lỗi của chính tôi ngay lần chạy đầu:** ca 9 bản đầu khẳng định "đúng 1 mã có
> reset = LPB" và **FAIL** — thực tế có **9** mã từng về 0 (HPG, HAH, VHC, MSB, VIB, DCM, MBS, VGC,
> LPB), nhưng 8 mã kia đã **thoát hẳn** (KL = 0) nên không vào báo cáo vị thế và không đổi số nào.
> Ranh giới đúng là "vừa còn giữ vừa từng về 0" — đã sửa assertion, và đây chính là loại lỗi mà một
> test chỉ khẳng định suông sẽ bỏ qua.

### 4.3 Các cổng/selfcheck liên quan (§23 — quét theo phạm vi cái vừa sửa)

| Kiểm | Kết quả |
|---|---|
| `report_return_gate.py --selfcheck` (cổng chặn cứng dựng hôm nay) | **PASS** |
| `report_return_gate.py --report <báo cáo tuần 03–07/08>` (chạy thật, không phải selfcheck) | **PASS, exit 0** — 19/19 dòng bảng + 8 tỉ suất văn xuôi khớp kỳ vọng dựng từ `costPrice` broker |
| `verify_account_snapshot_corp_action_selfcheck.py` | **12/12 PASS** (không hồi quy) |
| `nav_scripts_2account_selfcheck.py` (§12 chống lẫn account) | **PASS** |
| A/B pre-patch vs post-patch trên `nav_scripts_2account_selfcheck` | rc của `reconcile_equity` (1) và `daily_nav_snapshot` (2) **giống hệt hai bên** ⇒ là tình trạng có sẵn, không do bản vá; `mtm` hai bên trùng khít |

`bin/selfcheck_scope_map.sh mike/bin/verify_account_snapshot.py` báo không selfcheck nào **import**
module này — nên phải quét bằng tay theo caller thật (`daily_nav_snapshot.py` gọi subprocess,
`nav_scripts_2account_selfcheck.py` chạy nó, corp-action selfcheck import nó).

## 5. Hiện vật đã cập nhật

- **6 file `verified_snapshot_{SpaceX,ZaloPay}_2026-08-{07,08,09}.json`** đã tính lại và ghi đè
  (bản gốc lưu ở `exp_lot_reset_20260810/backup_pre_fix/`). Diff xác nhận **chỉ**
  `LPB.true_avg_cost` (52.583,3 → 51.466,7), `LPB.unrealized_pnl` (+158.333 → +716.667) và
  `total_cost_value` SpaceX (783.378.600 → 782.820.267) thay đổi; ZaloPay **không đổi gì**; `mtm`
  mọi mã không đổi. Lý do phải ghi đè: các file này là thứ người soạn báo cáo sau đọc — để nguyên
  số cũ là để sẵn cái bẫy vừa xảy ra.
- **`verified_snapshot_*_2026-08-10.json` KHÔNG ghi đè** — hôm nay `asof = today` nên script dùng
  giá ATC sống của DNSE; `daily_nav_snapshot.py` cuối phiên sẽ tự sinh lại bằng bản đã vá.
- **Báo cáo tuần 03–07/08**: các con số LPB trong báo cáo **đã đúng sẵn** (51.466,67 — bản đính
  chính trước đã sửa tay). Chỉ cập nhật một câu trong Mục 11.3 từ "*việc cần làm, chưa chốt hạn*"
  thành đã vá tận gốc + phạm vi đã kiểm — **gộp vào mục ĐÍNH CHÍNH có sẵn**, không tạo mục mới.

## 6. Không đụng tới (theo chỉ đạo user)

Công thức tỉ suất giữ nguyên: `total_return = (P_end + D_net − cost) / cost` — cổ tức RÒNG cộng vào
**tử số**, giá vốn gốc giữ nguyên ở **mẫu số**. `dividend_adjusted_return.py` và phần tử/mẫu của
`report_return_gate.py`: **không sửa một dòng nào**.

Bản vá này trực giao với công thức cổ tức: nó sửa `cost` (giá vốn của lô đang sống), không sửa cách
cổ tức đi vào công thức.

## 7. Nguồn

- Code: `mike/bin/verify_account_snapshot.py` (`CostBook`, `build_cost_books`, `dnse_fill_events`,
  `journal_fill_events`, `aggregate_events`)
- Selfcheck: `mike/bin/verify_account_snapshot_lot_reset_selfcheck.py`
- Script so sánh OLD/NEW/broker: `mike/agents/Taylor/exp_lot_reset_20260810/compare_cost.py`
- Sao lưu hiện vật trước khi sửa: `mike/agents/Taylor/exp_lot_reset_20260810/backup_pre_fix/`
- Bối cảnh: `mike/agents/Taylor/research/dividend_scope_gap_20260810.md` §5 (nơi lỗi này được phát
  hiện nhưng để mở), job `Taylor_20260810_030558`
