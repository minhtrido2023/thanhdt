# L2 JIT-unpark — áp phương án (C): làm tròn LÊN đúng 1 lô (job `Taylor_20260806_033014`)

**Trạng thái: ĐÃ SỬA + selfcheck 67/67 + replay 20/20 + đo lại 6/6 ca, CHƯA WIRE.** Không đụng
`bot_execute.py`, `golive_recommend_v23.py`, `trading_rules.json`, `context_planning_mini.md`.
Chờ Mike dispatch quant-skeptic verify.

> ✅ **Lần này mục tiêu ĐẠT.** Phương án (B) sáng nay khử phần hụt do PHÍ nhưng **0/6 ca** hết hụt;
> (C) khử nốt phần hụt do RỜI RẠC LÔ BÁN ⇒ **6/6 ca hụt về 0, 6/6 ca lệnh mua giữ nguyên vẹn**.
> Chi phí thật đo được: bán dư **0,50–2,08tr/ca** (Σ 6,52tr) để cứu **Σ 31,40tr** lệnh mua.

## 1. Đã sửa gì — `allocate()`, 6 dòng logic + 1 tham số trần

`mike/bin/compute_jit_unpark.py`

```python
def allocate(needed, pool, ceiling=None):     # ← THÊM `ceiling` = trần CỨNG tổng giá trị bán
    ...                                        # (pro-rata → làm tròn XUỐNG → largest-remainder: GIỮ NGUYÊN)
    if spent < needed - 1e-6:                                      # ← MỚI: (C)
        cands = [tk for tk in pool
                 if alloc[tk] + LOT <= headroom_qty(tk)
                 and (ceiling is None or spent + LOT * pool[tk]["px"] <= ceiling + 1e-6)]
        if cands:
            alloc[min(cands, key=lambda t: (LOT * pool[t]["px"], t))] += LOT
```

và tại chỗ gọi (dòng ~400):

```python
alloc = allocate(needed, pool, ceiling=day_cap_remaining) if needed > 0 else {}
```

**Vì sao 1 lô là ĐỦ, không cần vòng lặp**: vòng largest-remainder ở trên dừng đúng khi *mọi* lô còn
dư địa đều ĐẮT HƠN phần dư `needed − spent`. Nên thêm bất kỳ 1 lô nào trong số đó **chắc chắn** đưa
`Σ bán` vượt `needed` ⇒ thu ròng ≥ phần thiếu ⇒ sức mua ≥ target. Chọn lô **RẺ NHẤT** để chi phí
nhỏ nhất, tie-break theo ticker ⇒ xác định.

**Bất biến ĐẢO — cận trên MỚI phải giữ** (đúng yêu cầu "không phải bán tuỳ ý"):

| | CŨ | MỚI |
|---|---|---|
| | `Σ bán ≤ needed` | `needed ≤ Σ bán < needed + (1 lô rẻ nhất còn dư địa)` |

`ceiling` là chỗ giữ **trần TỔNG/phiên** làm trần CỨNG: khi trần đang bó (`needed == day_cap_remaining`)
thì không lô nào lọt ⇒ **(C) tự tắt**, hành vi y hệt trước. Trần per-name (`cap_remaining_vnd`) và
`sellable` T+2 đã nằm sẵn trong `headroom_qty()` nên lô thêm vào vẫn phải lọt cả hai.

Ngoài ra: docstring module (khối "chia lệnh bán theo mã") + chú thích tại chỗ. **Không hằng số mới,
không tham số chính sách mới.**

## 2. Selfcheck — 67/67 PASS, digest đồng nhất 4 múi giờ (+ 2 biến thể môi trường trần)

`python3 mike/bin/compute_jit_unpark_selfcheck.py` — digest `5f23cdeec1dd9897` → **`3726faae293c5185`**
(đổi là ĐÚNG: hành vi đổi thật).

```
TZ=<unset>          exit=0 digest=3726faae293c5185 [67 PASS / 0 FAIL]
TZ=Asia/Ho_Chi_Minh exit=0 digest=3726faae293c5185 [67 PASS / 0 FAIL]
TZ=UTC              exit=0 digest=3726faae293c5185 [67 PASS / 0 FAIL]
TZ=America/New_York exit=0 digest=3726faae293c5185 [67 PASS / 0 FAIL]
✅ MA TRẬN TZ: mọi môi trường PASS và digest ĐỒNG NHẤT
```

Theo skill `verify-before-done` bước 2–3, chạy thêm 2 biến thể khắc nghiệt — **digest y hệt**:
`cwd=/tmp` và `cd / && env -i PATH=/usr/bin:/bin` (bỏ sạch biến môi trường, kể cả `TZ`).

**Trước khi sửa test, chạy để xem test nào GÃY** — đúng 10 assert, **toàn bộ đều là test ghim bất
biến CŨ**, không có test nào gãy vì lý do khác (bằng chứng thay đổi khu trú đúng chỗ):

| Test | Trước | Sau |
|---|---|---|
| `T01b2`/`T01b3` | `NO_SELL_POSSIBLE`, mua 900cp | `JIT`, mua ĐỦ 1000cp (bán dư 1,50tr) |
| `T02`/`T02a1` | `SHRINK` 1000→900cp | `FUNDED_BY_JIT`, mua đủ 1000cp |
| `T14c` ×5 | `Σ ≤ needed` | `needed ≤ Σ < needed + 1 lô` (hoặc hết dư địa) |
| `T18e` | mô phỏng "(C) sẽ đúng" | kiểm (C) ĐÃ chạy thật |

**Test MỚI / đổi chiều:**
- **`T14c`** — bất biến hai vế: cận dưới `Σ ≥ needed` (trừ khi hết dư địa) **và** cận trên
  `Σ < needed + 1 lô rẻ nhất`, quét 7 mức `needed` từ 0 → 999.999.999.
- **`T14c2`** — `ceiling` là trần CỨNG: `allocate(x, pool, ceiling=x)` **không bao giờ** làm tròn LÊN.
- **`T14e`** — (C) chọn đúng lô **RẺ NHẤT** (BBB @25k), không phải lô đầu bảng chữ cái (AAA @50k).
- **`T18a-d`** ×3 mức giá — **A/B/C ba chân trên cùng rổ**: hụt chỉ GIẢM qua từng phương án
  (`C ≤ B ≤ A`), và **chỉ (C)** đưa hụt về 0 trong khi bán dư vẫn < 1 lô rẻ nhất.
- **`T18e`/`T18e2`** — ca mẫu báo cáo cũ: hết hụt thật + ghim cận trên chi phí.
- **`T19a-d`** — mỗi trần CỨNG một ca riêng: **(a)** trần TỔNG/phiên bó ⇒ (C) tự tắt, `Σ ≤ trần`,
  lệnh vẫn CO; **(b)** trần per-name ADV; **(c)** `sellable` T+2 (chỉ 100cp/mã); **(d)** hết dư địa
  (bán sạch rổ vẫn thiếu) ⇒ (C) tự tắt, không lỗi, không bán quá số đang giữ.

**Sửa một nhãn SAI phát hiện khi rà lại** (không phải yêu cầu của dispatch nhưng phải sửa): chân
"công thức CŨ" của `T18c` gọi `allocate(...)` — mà `allocate()` nay làm tròn LÊN, nên chân "cũ"
cũng bị làm tròn LÊN ⇒ nó **so B-với-B** và in "KHÔNG ĐỔI" cho mọi ca. Cách tái lập chân làm tròn
XUỐNG mà **không** cần cờ riêng: `allocate(x, pool, ceiling=x)`. Cùng lý do, script cũ
`jit_unpark_grossup_ab_20260806.py` (dòng 55) nay in số sai nhãn ⇒ đã gắn banner **HẾT HIỆU LỰC**
trỏ sang script mới, giữ lại làm bằng chứng phiên đo (B).

## 3. ✅ Đo lại trên SỔ THẬT — đúng 6 ca cũ (SpaceX/ZaloPay × 100k/30k/12k)

`mike/agents/Taylor/jit_unpark_roundup_c_abc_20260806.py` — asof 2026-08-05, mọi thứ THẬT (sổ lô
theo book, vị thế/giá/`availableCash` từ bản ghi DNSE, ADV thật, trần rổ thật, share thật); chỉ
lệnh mua LAG ~80tr là tiêm vào để kích hoạt đường JIT. Chân A/B tái lập độc lập bằng chính
`allocate()` với `ceiling` ép làm tròn XUỐNG.

| acct | px | hụt A (cũ) | hụt B (sáng nay) | **hụt C** | qty A/B | **qty C** | mất A/B | **bán dư C** | 1 lô rẻ nhất |
|---|---|---|---|---|---|---|---|---|---|
| SpaceX | 100.000 | 296.350đ | 1.792đ | **−1.176.438đ** | 700 | **800** | 10,00tr | **1,18tr** | 1,18tr |
| SpaceX | 30.000 | 547.967đ | 547.967đ | **−630.263đ** | 2.500 | **2.600** | 3,00tr | **0,63tr** | 1,18tr |
| SpaceX | 12.000 | 674.580đ | 674.580đ | **−503.650đ** | 6.500 | **6.600** | 1,20tr | **0,50tr** | 1,18tr |
| ZaloPay | 100.000 | 1.150.856đ | 1.150.856đ | **−1.275.499đ** | 700 | **800** | 10,00tr | **1,28tr** | 2,43tr |
| ZaloPay | 30.000 | 1.577.211đ | 1.577.211đ | **−849.144đ** | 2.400 | **2.600** | 6,00tr | **0,85tr** | 2,43tr |
| ZaloPay | 12.000 | 350.856đ | 350.856đ | **−2.075.499đ** | 6.500 | **6.600** | 1,20tr | **2,08tr** | 2,43tr |

*(hụt âm = DƯ tiền so với target)*

**6/6 ca hụt về 0 · 6/6 ca mua ĐỦ nguyên lệnh · 6/6 ca bán dư nằm trong cận trên.**
Σ lệnh mua không còn bị mất **31,40tr**, Σ bán dư phải trả **6,52tr** ⇒ **1đ bán dư cứu 4,8đ lệnh mua**.

### ⚠️ Đính chính con số "~2,70 triệu" của báo cáo trước

Dispatch yêu cầu xác nhận chi phí khớp ước lượng ~2,70tr. **Không khớp — và ước lượng cũ mới là số
sai bối cảnh, không phải phép đo mới.** 2,70tr là 1 lô của mã CCC @27.000 trong **rổ 3 mã tổng
hợp** của test `T18e`, không phải rổ thật. Trên sổ thật, lô rẻ nhất **đủ điều kiện bán** là
**1,18tr** (SpaceX — SHB @11.800) và **2,43tr** (ZaloPay — MBB @24.300), nên chi phí thật đo được
là **0,50–2,08tr/ca**, **thấp hơn** ước lượng cũ ở mọi ca. 2,70tr vẫn đúng với vai trò *cận trên
của ca mẫu tổng hợp*; **cận trên đúng cho live là "1 lô rẻ nhất của rổ PARK đủ điều kiện bán phiên
đó"**, và nó thay đổi theo rổ/phiên — nên đừng ghim thành hằng số.

## 4. Replay — 20/20 bất biến trên dữ liệu thật, 2 account

`jit_unpark_replay_20260806.py` (sửa đúng 1 bất biến theo (C), thêm hàm `cheapest_lot_vnd()` tính
cận trên bằng chính `build_pool()` để cận là cận THẬT — mã bị chặn không được tính dù rẻ hơn):

```
SpaceX  : FUNDED_BY_JIT 800→800cp | needed 75,29tr | bán PARK 76,47tr trên 12 mã
ZaloPay : FUNDED_BY_JIT 800→800cp | needed 74,29tr | bán PARK 75,57tr trên 9 mã
✅ REPLAY: mọi bất biến GIỮ trên dữ liệu thật
```

Cả 2 account đổi từ `SHRINK 800→700cp` sang `FUNDED_BY_JIT 800→800cp`. Mười bất biến mỗi account
đều GIỮ: chỉ bán sổ PARK · không đụng CAPIT/LAG/BAL/DISCRETIONARY · không đụng `excluded_tickers`
(**DGC ở ZaloPay vẫn không bị chạm**) · không đụng UNVERIFIED · không quá số giữ · không quá
`sellable` T+2 · ≤ trần TỔNG/phiên · **Σ bán < needed + 1 lô rẻ nhất** (bất biến mới) · bội số lô ·
không bán sạch mã nào.

## 5. Rủi ro còn lại / điều người duyệt cần biết

1. **Đây là bán THỪA có chủ ý** — L2 nay bán PARK nhiều hơn phần lệnh mua cần, tối đa 1 lô. Tiền
   thừa nằm lại ở cash (không mất), chi phí thật = friction 0,15% trên phần thừa + lệch trọng số
   parking một lượng nhỏ trong phiên. Đo được: ≤2,08tr/ca trên rổ hiện tại.
2. **(C) kích hoạt cả khi phần thiếu rất nhỏ.** `T01b3`: thiếu **1 đồng** vẫn bán 1 lô 2,5tr. Đúng
   theo thiết kế user duyệt (thiếu 1đ = mất trọn 1 lô mua), nhưng là hành vi cần biết trước.
3. **Không có "trần số lô thừa" riêng** — cận trên là 1 lô/lệnh mua, nên plan nhiều lệnh mua BAL/LAG
   thì tối đa 1 lô thừa **mỗi lệnh**. Chưa có ca thật để đo (plan thật đang 0 lệnh BAL/LAG); test
   `T12` phủ chuỗi nhiều lệnh về mặt số học.
4. **Chưa wire** — mọi số ở đây là ĐỀ XUẤT của một script CHỈ ĐỌC, chưa vào plan nào.

## 6. Đã đụng file nào

| File | Thay đổi |
|---|---|
| `mike/bin/compute_jit_unpark.py` | `allocate()`: thêm tham số `ceiling` + khối làm tròn LÊN (6 dòng logic); chỗ gọi truyền `ceiling=day_cap_remaining`; docstring + chú thích |
| `mike/bin/compute_jit_unpark_selfcheck.py` | sửa 4 test ghim bất biến cũ (T01b2/b3, T02/T02a1, T14c, T18e); sửa nhãn sai chân A/B của T18; thêm T14c2/T14e/T18d/T18e2/T19a-d (57→67 case) |
| `mike/agents/Taylor/jit_unpark_replay_20260806.py` | đổi 1 bất biến sang cận trên mới + hàm `cheapest_lot_vnd()` |
| `mike/agents/Taylor/jit_unpark_roundup_c_abc_20260806.py` | **mới** — A/B/C trên sổ thật, 6 ca |
| `mike/agents/Taylor/jit_unpark_grossup_ab_20260806.py` | banner **HẾT HIỆU LỰC** (chân A của nó nay bị (C) làm tròn LÊN ⇒ số sai nhãn) |
| `mike/agents/Taylor/jit_unpark_replay_*.json` | chạy lại (artifact) |

Production **không bị đụng**: `git status` chỉ có các file trên (đều chưa từng commit) +
`kb/fleet_status.md` của consolidator. `bot_execute.py`, `golive_recommend_v23.py`,
`trading_rules.json` sạch. `grep` xác nhận **không consumer nào khác** gọi `allocate()` ngoài
module L2 + test + 2 script nghiên cứu này.
