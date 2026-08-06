# L2 JIT-unpark — áp phương án (B) gross-up phí ma sát (job `Taylor_20260806_025613`)

> ➡️ **TIẾP NỐI 2026-08-06:** user duyệt phương án (C) ở mục 4 và nó **ĐÃ ÁP** (job
> `Taylor_20260806_033014`) — kết quả: **6/6 ca hụt về 0, 6/6 ca mua đủ nguyên lệnh**. Báo cáo:
> `jit_unpark_roundup_c_20260806.md`. Mục 3 dưới đây (0/6 ca) là trạng thái **chỉ có (B)**, giữ
> nguyên làm bằng chứng lịch sử — **không còn mô tả hành vi hiện hành**.

**Trạng thái: ĐÃ SỬA + selfcheck 57/57 + replay xanh, CHƯA WIRE.** Không đụng `bot_execute.py`,
`golive_recommend_v23.py`, `context_planning_mini.md`. Chờ Mike dispatch quant-skeptic verify.

> ⚠️ **Đọc mục 3 trước khi coi việc này là xong.** Thay đổi đã áp ĐÚNG như user duyệt và đúng về
> đại số, nhưng **mục tiêu "hụt tiền về 0" CHƯA đạt**: đo trên sổ thật, **0/6 ca** hết hụt và
> **6/6 ca lệnh mua vẫn co đúng 1 lô**. Lý do không phải làm sai — mà là phí ma sát chỉ là **một
> trong hai** nguồn gây hụt, và (B) theo thiết kế chỉ khử được nguồn thứ nhất.

## 1. Đã sửa đúng 1 biểu thức, không gì khác

`mike/bin/compute_jit_unpark.py:388`

```python
# TRƯỚC
needed = min(tv0 - max(cash, 0.0), day_cap_remaining)
# SAU
needed = min((tv0 - max(cash, 0.0)) / (1.0 - ETF_FRICTION), day_cap_remaining)
```

`ETF_FRICTION = 0.0015` là hằng số đã PORT sẵn (`pt_v23_audit_2014.py:1946`) — **không thêm tham
số mới**. Ngoài dòng này chỉ có docstring + khối chú thích giải thích tại chỗ. Mọi ranh giới khác
giữ nguyên, đã kiểm bằng test: trần `etf_day_cap` (T03/T12b), FIFO theo lô (T02d), pro-rata theo
trọng số (T02c), `excluded_tickers` (T04), CAPIT `stop_exempt`/`slot_exempt` + LAG/BAL (T05/T05b),
`availableCash` không `totalCash` (đọc thẳng `park_holdings`), trần per-name + T+2 (T11).

⚠️ **Ghi lại vì ảnh hưởng tính toàn vẹn file**: Mike lỡ dispatch **2 job trùng nhau** cho việc này
(`Taylor_20260806_025532` lúc 09:55:33 và `_025613` lúc 09:56:14). Job `_025532` bị đánh dấu
`aborted` ở sổ job **nhưng tiến trình `claude -p` của nó vẫn sống và vẫn đang ghi cùng file**
(mtime nhảy 09:58:24 giữa lúc tôi đang sửa). Tôi đã `kill` tiến trình mồ côi đó rồi **đọc lại
TOÀN BỘ 546 dòng** file, đối chiếu từng dòng với bản gốc: file = bản gốc + đúng 2 vùng chủ ý
(docstring + công thức), không có sửa đổi lạ nào khác. Hai job ra cùng một công thức nên kết quả
không mâu thuẫn, nhưng **đây là lỗ hổng điều phối thật** — job `aborted` phải kill được tiến trình
con của nó, nếu không hai phiên ghi đè lẫn nhau trên file production-candidate. Đề nghị Mike/Wags
xử lý riêng.

## 2. Selfcheck — 57/57 PASS, digest đồng nhất 4 múi giờ (+ cwd/PATH tối thiểu)

`python3 mike/bin/compute_jit_unpark_selfcheck.py` — **digest đổi `ab132dbe41213d29` →
`5f23cdeec1dd9897`** (đúng như dự kiến: hành vi đổi).

```
TZ=<unset>          exit=0 digest=5f23cdeec1dd9897 [57 PASS / 0 FAIL]
TZ=Asia/Ho_Chi_Minh exit=0 digest=5f23cdeec1dd9897 [57 PASS / 0 FAIL]
TZ=UTC              exit=0 digest=5f23cdeec1dd9897 [57 PASS / 0 FAIL]
TZ=America/New_York exit=0 digest=5f23cdeec1dd9897 [57 PASS / 0 FAIL]
✅ MA TRẬN TZ: mọi môi trường PASS và digest ĐỒNG NHẤT
```

Theo skill `verify-before-done` bước 2-3, TZ không phải phụ thuộc môi trường duy nhất — chạy thêm
2 biến thể khắc nghiệt, **digest y hệt**: `cwd=/tmp` và `cd / && env -i PATH=/usr/bin:/bin` (bỏ
sạch biến môi trường, kể cả TZ).

**Test đã sửa** (2 test cũ ghim công thức cũ, phải đổi — không phải test hỏng):
`T01b2`, `T02` nay ghim `needed = (tv0 − cash)/(1 − friction)`. Chú thích của `T02a1` đã viết lại
(bản cũ nói "giữ NGUYÊN công thức engine, KHÔNG tự gross-up" — nay sai).

**Test MỚI — 3 mức giá đã đo (100k / 30k / 12k):**
- **T18a** — `needed` đúng bằng `(tv0 − cash)/(1 − friction)`.
- **T18b** — bất biến tách nguồn hụt: `tv0 − bp = (needed − gross) × (1 − friction)`. Số hạng
  friction **biến mất hẳn** ⇒ phần hụt còn lại thuần tuý là dư chưa phân bổ được của chân bán.
  Đây là bằng chứng chặt nhất rằng (B) làm đúng việc của nó.
- **T18c** — gross-up **không bao giờ tệ hơn** công thức cũ (A/B recompute độc lập bằng chính
  `allocate()`/`build_pool()` trên đúng cùng rổ). Cả 3 mức giá đều in ra "KHÔNG ĐỔI".
- **T18e** — chứng minh **hướng sửa (C)** ở mục 4 là đúng chỗ: thêm ĐÚNG 1 lô bán rẻ nhất là đủ
  đưa sức mua ≥ target.

## 3. 🔴 Kết quả đo — mục tiêu "hụt về 0" CHƯA đạt

`mike/agents/Taylor/jit_unpark_grossup_ab_20260806.py` (A/B trên **sổ THẬT** 2026-08-05; chân A =
công thức cũ, tái lập độc lập ngay trong script bằng `allocate()`/`build_pool()`, không cần
checkout bản cũ).

| acct | ref_price | qty kế→chốt | hụt A (cũ) | hụt B (mới) | Δ | mất tiền | % lệnh |
|---|---|---|---|---|---|---|---|
| SpaceX | 100.000 | 800→700 | 296.350đ | **1.792đ** | −294.558đ | 10,00tr | **12,50%** |
| SpaceX | 30.000 | 2.600→2.500 | 547.967đ | 547.967đ | **0** | 3,00tr | 3,85% |
| SpaceX | 12.000 | 6.600→6.500 | 674.580đ | 674.580đ | **0** | 1,20tr | 1,52% |
| ZaloPay | 100.000 | 800→700 | 1.150.856đ | 1.150.856đ | **0** | 10,00tr | 12,50% |
| ZaloPay | 30.000 | 2.600→2.400 | 1.577.211đ | 1.577.211đ | **0** | 6,00tr | 7,69% |
| ZaloPay | 12.000 | 6.600→6.500 | 350.856đ | 350.856đ | **0** | 1,20tr | 1,52% |

**0/6 ca hụt về 0 · 5/6 ca gross-up là NO-OP đúng 0 đồng · 6/6 ca lệnh mua vẫn co 1 lô.**

**Vì sao (chứng minh đại số, không phải suy đoán).** Có HAI nguồn làm sức mua hụt so với target:

1. **phí ma sát** — bán `needed` chỉ thu về `needed×(1−f)`. ← (B) khử HẲN nguồn này.
2. **rời rạc lô bán** — `allocate()` làm tròn XUỐNG lô và **dừng trước khi vượt `needed`**, nên
   luôn `gross ≤ needed`; phần dư có thể tới gần 1 lô bán (0,3–1,6tr trên rổ thật).

Đặt `gap = tv0 − bp`. Nếu headroom mới (`needed×f`, chỉ ~0,15%) **không đủ nhét thêm 1 lô bán
nào** thì `gross` giữ nguyên, và:

```
gap_B = (needed_A/(1−f) − gross)·(1−f) = needed_A − gross·(1−f) = gap_A
```

⇒ **no-op ĐÚNG BẰNG 0 đồng**. Gross-up chỉ ăn tiền khi 0,15% đó tình cờ đủ 1 lô bán — đúng 1/6 ca
(SpaceX @100k nhét thêm được lô TPB 1,48tr, gap 296.350đ → 1.792đ).

**Và ngay cả ca "thành công" nhất cũng không cứu được lệnh mua**: hụt **1.792 đồng** vẫn làm mất
**trọn 10.000.000 đồng** lệnh mua. Vì chân mua là

```python
qf = round_lot(min(tv, bp) / px_ref)          # compute_jit_unpark.py:439
```

`min(tv, bp)` **không có dung sai**: `bp` thấp hơn `tv0` dù chỉ 1 đồng cũng làm `round_lot` rơi
xuống lô dưới. Đây là hàng rào an toàn live cố ý (không đặt lệnh vượt sức mua thật, DNSE sẽ từ
chối) — không nên nới.

## 4. Đề xuất (C) — việc còn lại, KHÔNG tự làm

Điều kiện **đủ** để hết hụt là `gross ≥ needed`, tức cho `allocate()` **làm tròn LÊN**: thêm đúng
1 lô bán rẻ nhất còn dư địa. Theo đúng điều kiện dừng hiện tại (mọi lô còn lại đều ĐẮT HƠN phần
dư), 1 lô đó **chắc chắn** đưa `gross` vượt `needed` ⇒ thu ròng ≥ `tv0 − cash` ⇒ sức mua ≥ target.
Chi phí có cận trên chặt: **bán dư tối đa đúng 1 lô PARK** (T18e đo được 2,70tr trên rổ mẫu; đổi
lấy việc không mất 10tr lệnh mua).

**Tôi KHÔNG tự áp (C)** vì hai lẽ, cả hai đều là quyết định của user chứ không phải kỹ thuật:
1. Dispatch ghi rõ "CHỈ đổi đúng 1 biểu thức `needed`, không sửa gì khác".
2. (C) **đảo một bất biến đang được kiểm**: `Σ bán ≤ needed` ("không bán thừa") — có trong cả
   selfcheck lẫn replay. Bán dư PARK 1 lô để mua đủ là đánh đổi có thật, phải người quyết.
   Đồng thời phải giữ trần `etf_day_cap`/per-name/`sellable` làm trần CỨNG (lô thêm vào vẫn phải
   lọt các trần đó, nếu không thì không thêm được và ca đó vẫn co lệnh).

Nếu user chốt (C): sửa trong `allocate()`, ~5 dòng, kèm 3 test đảo chiều bất biến trên. Ước tính
1 lượt dispatch.

## 5. Đã đụng file nào

| File | Thay đổi |
|---|---|
| `mike/bin/compute_jit_unpark.py` | 1 biểu thức `needed` (dòng 388) + docstring + chú thích tại chỗ |
| `mike/bin/compute_jit_unpark_selfcheck.py` | sửa 2 assert cũ + chú thích T02a1; thêm T18a/b/c + T18e (47→57 case) |
| `mike/agents/Taylor/jit_unpark_grossup_ab_20260806.py` | **mới** — A/B đo trên sổ thật, 3 mức giá |
| `mike/agents/Taylor/jit_unpark_replay_*.json` | chạy lại (artifact) |
| `mike/agents/Taylor/research/jit_unpark_L2_build_20260806.md` | §3 trỏ sang báo cáo này |

`jit_unpark_replay_20260806.py` **không sửa** — chạy lại nguyên trạng, **20/20 bất biến GIỮ** trên
cả 2 account (chỉ bán sổ PARK · không đụng CAPIT/LAG/BAL/DISCRETIONARY · không đụng
`excluded_tickers` (DGC ở ZaloPay) · không đụng UNVERIFIED · không quá số giữ · không quá
`sellable` T+2 · ≤ trần TỔNG/phiên · ≤ `needed` · bội số lô · không bán sạch mã nào).

Production **không bị đụng**: `git status` chỉ có các file trên + artifact; `bot_execute.py`,
`golive_recommend_v23.py`, `trading_rules.json` sạch.
