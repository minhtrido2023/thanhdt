# PENDING — `merge_park_orders.py`: gộp L1 park_trim + L2 jit_unpark vào `orders[]`, chạy lặp được

**Job** `Taylor_20260810_131833` · 2026-08-10 · Taylor
**Trạng thái: CHỜ DUYỆT. 0 dòng production bị sửa** — đây là **FILE MỚI**, không phải patch lên
file đang chạy.

> ⚠️ **Bằng chứng "0 dòng production" phải chạy đúng repo.** Bản nháp đầu dẫn
> `git status -- trading_bot/ mike/bin/ data/trade_plans/` trả rỗng — **bằng chứng RỖNG**:
> `.gitignore` giấu `mike/` (repo lồng), `git ls-files mike/bin/ | wc -l` = **0**, nên lệnh đó
> không bao giờ báo gì về `mike/bin/` dù có sửa hay không. Đúng cùng lớp lỗi "bộ lọc rỗng ⇒
> khẳng định vô căn cứ" mà chính tài liệu này chẩn đoán ở khuyết tật #1 (quant-skeptic vòng 2).
> **Bằng chứng đúng:**
>
> ```
> $ git -C mike status --short -- bin/ agents/Taylor/pending_park_merge_20260810/
>  M bin/cli_provider_selfcheck.sh      ← 4 file này BẨN SẴN từ đầu phiên,
>  M bin/dispatch.sh                       là fleet infra KHÔNG liên quan việc này
>  M bin/kb_nightly.sh
>  M bin/remember.sh
> ?? agents/Taylor/pending_park_merge_20260810/   ← toàn bộ việc của tôi: UNTRACKED, file mới
> $ git status --short -- trading_bot/ data/trade_plans/     # 2 đường này repo NGOÀI có theo dõi thật
> (rỗng)
> ```

## Vấn đề cần giải

Không có đường TỰ ĐỘNG nào đưa `park_trim_proposal` (L1) và `jit_unpark` (L2) vào `orders[]`.
Mỗi lần đều viết script một-lần (`write_park_trim_into_plan_20260807.py`,
`merge_three_in_one_20260807.py`, phần merge trong `approve_plan_with_jit.sh`). Khâu này đã hỏng
**hai kiểu khác nhau trong hai ngày liên tiếp**:

| Ngày | Hỏng kiểu gì | Hậu quả |
|---|---|---|
| **2026-08-06** | cổng `reconcile_ok` thô chặn **cả tài khoản** vì 1 mã lệch sổ | 0 lệnh cả 2 account đúng **phiên entry chuẩn** của 6 mã LAG — mất không phục hồi |
| **2026-08-07** | merge tay cộng lệnh gộp **nhưng không xoá lệnh JIT gốc** | thừa **1.200cp SpaceX + 400cp ZaloPay**; Wags bắt lúc 05:48 ICT, **cách giờ đặt lệnh 15 phút** |

Hai thất bại này là **cùng một nguyên nhân gốc: khâu này không có cơ chế, chỉ có script tay**.
Không phải thiếu một con số đúng.

## Nguyên nhân gốc 08-07 — dedup theo `id` là sai cơ chế

```
merge_three_in_one_20260807.py   ghi id  SELL-{TK}-PARK-{i:02d}
approve_plan_with_jit.sh         ghi id  SELL-JIT-PARK-{TK}-01
                                 dedup   if oid in existing_ids: continue
```

Hai namespace id khác nhau ⇒ phép dedup **không bao giờ khớp** ⇒ cùng một lô bị đề xuất bán hai
lần. `id` là thứ **người viết đặt**; nó không phải danh tính kinh tế của lệnh. Danh tính kinh tế
là `(ticker, side, nguồn-sinh-ra)`.

## Cơ chế: SỞ HỮU MỘT VÙNG + DỰNG LẠI, không THÊM VÀO

1. **Sở hữu.** Lệnh do merge sinh ra mang `merge_owner="park_merge_v1"`. Bước đầu tiên của **mỗi**
   lần chạy là **xoá sạch vùng đó rồi dựng lại** từ L1/L2 hiện tại → idempotent *by construction*
   (§5), không phải nhờ nhớ kiểm tra trùng.
2. **Nhận nuôi lệnh di sản.** Vùng sở hữu bao gồm cả lệnh bán PARK do script CŨ ghi (nhận theo
   `side=sell ∧ book=PARK ∧ play_type ∈ {PARK_TRIM, JIT_UNPARK, PARK_TRIM+JIT_UNPARK}`), **kể cả
   khi không có dấu**. Nhờ vậy chạy merge mới SAU một script cũ thì **hội tụ**, không nhân đôi.
3. **Bất biến hậu kiểm trên TOÀN BỘ `orders[]`**, không chỉ phần mình sinh: Σ qty bán mỗi mã (mọi
   book, mọi writer) ≤ `sellable`. Vi phạm ⇒ **trả plan nguyên vẹn, không ghi file**.

⚠️ **Hai cơ chế (2) và (3) KHÔNG thay thế nhau — cần cả hai.** Bằng chứng từ chính dữ liệu 08-07:
phần thừa 1.200cp của **SpaceX KHÔNG hề vi phạm trần sellable** (dư địa còn đủ) ⇒ bất biến (3) mù
với ca đó, chỉ (2) bắt được. Ngược lại ZaloPay/VHM 400>300 thì (3) bắt được kể cả khi lệnh thừa do
một writer hoàn toàn xa lạ ghi vào — thứ (2) không biết tới. Bỏ bất kỳ cái nào là để hở đúng một lối.

## ⚠️ Cơ chế này KHÔNG phải lưới duy nhất — đã có một lưới khác, ở tầng khác

`mike/bin/preflight_check.sh:73-93` **đã có sẵn** hai cờ `MERGE_STALE_SRC` + `SELL_GT_SELLABLE`,
thêm ngày **2026-08-07 cho đúng sự cố này**, kèm selfcheck riêng
(`bin/preflight_order_invariants_selfcheck.py`). Hai lưới **bổ sung nhau, không trùng lặp**:

| | `preflight_check.sh` (đã có) | `merge_park_orders.py` (đề xuất) |
|---|---|---|
| Tầng | **thực thi** — phát hiện sau khi plan đã soạn xong | **soạn plan** — ngăn không cho sinh ra |
| Kết quả | gắn cờ cảnh báo | không ghi lệnh sai ngay từ đầu |
| Ca SpaceX 08-07 (không vượt sellable) | `MERGE_STALE_SRC` bắt được (2 lệnh cùng `(sell,ticker)` có `merged_from`) | lớp **nhận nuôi** bắt được |

Chúng **ăn khớp**: merge ghi `merged_from.sellable_at_calc` — đúng field mà nhánh (b) của preflight
bám vào. Nêu ra vì bản nháp đầu của tài liệu này tự trình bày như lưới duy nhất; **nó là lưới thứ
hai** (quant-skeptic nêu 2026-08-10). Không phải lý do bỏ bất kỳ lưới nào: ngăn ở tầng soạn rẻ hơn
phát hiện lúc 09:05, còn preflight vẫn bắt được lệnh do writer tương lai ghi vào.

## Cổng đối soát — KHÔNG kế thừa `assert reconcile_ok is True`

quant-skeptic đã cảnh báo cụ thể: `merge_three_in_one_20260807.py:32` hard-assert
`l2["reconcile_ok"] is True` sẽ **dừng sai đúng ngày PARTIAL** mà bản vá kế toán
(`pending_park_trim_partial_reconcile_20260810/`) vừa cứu được. Ở đây:

```
chấp nhận  ⇔  reconcile_ok is True  OR  reconcile_partial is True
từ chối    ⇔  reconcile_ok is False AND reconcile_partial is not True
```

Và từ chối **theo TẦNG, không theo tài khoản**: L1 hỏng thì L2 vẫn cấp vốn, và ngược lại (ca P3).
Đây chính là bài học 08-06 — một cổng thô chặn cả gói là cách **mất phiên**, không phải cách an toàn.

## Thứ tự cắt khi vượt `sellable`: L1 trước, L2 sau

L1 = tuân thủ trần PARK, hoãn được 1 phiên, hướng sai là "trim ít hơn" = an toàn.
L2 = cấp vốn cho lệnh MUA cùng plan; cắt ⇒ P0 `check_plan_funding` chặn ⇒ mất phiên entry.
Buộc phải cắt vào L2 ⇒ gắn `jit_underfunded=true` lên lệnh mua để **người duyệt thấy trước**,
không để P0 phát hiện hộ lúc 09:05. Làm tròn **xuống** bội 100.

## Bằng chứng — A/B trên DỮ LIỆU THẬT phiên 2026-08-07

| Account | Chân | Kết quả |
|---|---|---|
| SpaceX | **A** — chạy merge trên plan người đã sửa đúng | **KHỚP TUYỆT ĐỐI** 14 mã / 6.900cp |
| SpaceX | **B** — dựng lại trạng thái HỎNG (thêm lại 11 lệnh JIT gốc → 8.100cp) | hội tụ về **6.900cp**, khớp người sửa tay |
| ZaloPay | **A** — plan người đã sửa đúng | **KHỚP TUYỆT ĐỐI** 8 mã / 2.500cp |
| ZaloPay | **B** — trạng thái HỎNG (2.900cp, **VHM 400 > 300 sellable**) | hội tụ về **2.500cp**, khớp người sửa tay |

Chênh chân B đúng bằng con số sự cố đã ghi nhận: **+1.200cp SpaceX, +400cp ZaloPay**.
Tái lập: xem `research/park_merge_mechanism_20260810.md` §Tái lập.

## quant-skeptic — 5 vòng; vòng 5 **REFUTED** (đúng), đã sửa lại; 6 khuyết tật + 1 bản neo hỏng

**Vòng 5 — REFUTED (confidence `high`), và nó ĐÚNG.** Nó tách đôi tuyên bố của tôi: bản vá **#6
(khối đề xuất) đứng vững** — tái lập trên dữ liệu thật cả hai chiều (mất artifact ⇒ khối bị xoá +
cảnh báo, tổng bán rơi về L1-only 5700/2100; artifact có nhưng bị từ chối ⇒ khối còn, dán ⛔) —
nhưng **bản neo #6b thì hỏng**:

> `_annotate_buy()` chỉ nổ **khi có người GỌI nó**, và ca `S5d` cũ chỉ grep **3 tên literal** đang
> có. Nhãn thứ 4 gán thẳng `tgt["jit_x"] = …` **lọt qua CẢ HAI**, không bao giờ bị bước 0 xoá, và
> sống sót vào đúng lần chạy L2 bị từ chối. Nó chứng minh bằng cách vá **đúng 1 dòng** vào bước 5:
> selfcheck **vẫn xanh 84/84** trong khi `jit_funding_tier="FUNDED_BY_JIT"` sống sót qua một lần
> chạy L2 bị từ chối trên dữ liệu SpaceX 08-07 thật ⇒ **tái lập nguyên văn khuyết tật #5**.

Đây là bài học đáng giữ hơn cả bản vá: tôi đã sửa **quy ước** (phải nhớ gọi helper, phải nhớ khai
báo tên) và gọi nó là "neo". Quy ước không phải bất biến.

**Bản vá đúng — xoá theo KHÔNG GIAN TÊN, không theo danh sách.** Bước 0 nay xoá **mọi khoá bắt đầu
bằng `jit_`** trên mọi lệnh. Tập XOÁ do đó **luôn là tập CHA của mọi tập GHI, theo cấu trúc** —
không còn danh sách nào để trôi, không cần ai nhớ gọi hàm nào. `_annotate_buy` bị **xoá bỏ** (máy
móc thừa, §2): gán thẳng lại là đúng.

**Nghiệm thu bằng chính probe của quant-skeptic** (chép repo ra `/tmp`, vá thêm dòng
`tgt["jit_funding_tier"] = …` vào bước 5, chạy trên artifact SpaceX 08-07 thật):

| | trước bản vá | sau bản vá |
|---|---|---|
| chạy 1 (L2 nhận) | `jit_funding_tier="FUNDED_BY_JIT"` | `jit_funding_tier="FUNDED_BY_JIT"` |
| chạy 2 (**L2 TỪ CHỐI**) | **vẫn "FUNDED_BY_JIT"** ⇒ khuyết tật #5 | **0 nhãn `jit_*` còn lại** ✅ |
| selfcheck trên bản đã vá dòng đó | 84/84 xanh (không thấy gì) | **ĐỎ ở `S5d`** — tripwire báo tập ghi đã đổi |

Ca `S5d` mới kiểm **TÍNH CHẤT hành vi**, không đọc mã nguồn: một nhãn `jit_*` **lạ hoàn toàn** (kể
cả nhãn lồng cấu trúc) nằm sẵn trên lệnh mua phải biến mất, trong khi khoá **không** thuộc `jit_*`
(`total_with_fee_vnd`, `id`, `qty`) **không bị đụng** — chứng minh ngược cho "xoá bừa".

**Phạm vi phải khai báo — 3 tầng, đừng gộp** (bản đầu của mục này viết sai một câu; quant-skeptic
vòng 6 bắt được và **nó đúng**: câu "khoá `jit_*` cấp plan KHÔNG bị đụng" mâu thuẫn với chính bản
vá #6 mô tả cách đó vài dòng):

| Tầng | merge có sở hữu không? | Cụ thể |
|---|---|---|
| Khoá **cấp một của LỆNH** khớp `jit_*` | **CÓ, toàn bộ không gian tên** | bước 0 xoá sạch, bước 5 dựng lại ⇒ writer nào muốn nhãn sống qua merge thì **đừng đặt tên `jit_*`** |
| Khoá **cấp plan** `jit_unpark_proposal` | **CÓ — đúng một khoá** | bước 6 dựng lại, hoặc **XOÁ** khi vắng artifact (chính bản vá #6) |
| Mọi khoá `jit_*` **cấp plan** khác | **KHÔNG** | `jit_unpark_note` (có thật trong `plan_SpaceX_2026-08-10.json`) **không bị đụng**. Cố ý để ngoài phạm vi thay vì âm thầm mở rộng quyền sang khoá của writer khác — **cần quyết định riêng khi wire** |

**Ranh giới thứ hai — quét CẤP MỘT, không đệ quy.** Khoá `jit_` **lồng** trong dict con
(`o["meta"]["jit_x"]`) **không** bị bước 0 quét. Hôm nay vô hại (bước 5 chỉ ghi khoá cấp một, đã
grep toàn module xác nhận) — nhưng nay là **sự thật ĐÃ KIỂM** chứ không phải giả định ngầm: ca
`S5d` ghim nó lại, và comment `_JIT_PREFIX` nói thẳng "muốn thêm nhãn thì ghi cấp một, đừng ghi
lồng".

## quant-skeptic — 4 vòng đầu, cả bốn CONFIRMED (vòng 4: **high**); 6 khuyết tật ĐÃ SỬA

**Vòng 4** (trên bản vá #5) **CONFIRMED — confidence `high`**, mức cao nhất chuỗi này đạt được.
Nó tấn công bản vá **trên DỮ LIỆU THẬT chứ không phải fixture**: xác nhận cả 2 plan 08-07 thật
đang mang `jit_status="FUNDED_BY_JIT"` do script one-off cũ ghi, chạy lại với `reconcile_ok=False`
⇒ **0 nhãn `jit_*` còn lại trên cả 2 tài khoản**, qty lệnh mua giữ nguyên 1.800; đếm lại
selfcheck bằng profiler hook (**76/0-fail**, hết lệch 64/65 của vòng 3); tái lập 6 con số A/B; và
kiểm từng dòng tham chiếu trong comment `priority` đã sửa (`plan.py:124/149/292`,
`executor.py:1232`, `plan_funding_gate.py:194+`) — **đúng hết**. **Nhưng nó lại phá được một thứ
mới, đúng LỚP #5, ở tầng cao hơn:**

| # | Khuyết tật (vòng 4) | Sửa |
|---|---|---|
| 6 | **Khối ĐỀ XUẤT nhúng chỉ được ghi lại `if art is not None`**: chạy 1 có L2 ⇒ `p["jit_unpark_proposal"]` dán "✅ ĐÃ MERGE vào orders[]"; chạy 2 **mất file artifact** ⇒ `continue` để khối đó Y NGUYÊN trong khi `orders[]` chỉ còn phần L1 ⇒ người duyệt đọc một khối kiểm toán KHÔNG khớp lệnh thật. Cùng lớp "nhãn không hết hạn" như #5, chỉ ở tầng khối đề xuất | **ĐÃ SỬA**: `art is None` ⇒ **XOÁ** khối cũ khỏi plan (`p.pop(key)`) + ghi cảnh báo, thay vì `continue`. Nhóm ca `S5c` (5 ca) |
| 6b | **`_JIT_ANNOTATIONS` không được neo vào chỗ GHI**: hôm nay tuple đúng, nhưng *"nothing keeps it correct"* — thêm nhãn thứ 4 ở bước 5 trong tương lai sẽ **lặng lẽ tái lập #5** với selfcheck vẫn xanh | **BẢN VÁ ĐẦU HỎNG** (helper + grep 3 tên literal — quy ước, không phải bất biến; quant-skeptic vòng 5 REFUTED, xem mục trên). **Bản vá đúng**: bước 0 xoá theo **tiền tố `jit_`** ⇒ tập xoá là tập cha của mọi tập ghi theo cấu trúc; `_annotate_buy` đã xoá bỏ. Nhóm ca `S5d` (4 ca) kiểm tính chất hành vi, không đọc mã nguồn |

**Đính chính tuyên bố idempotent** (quant-skeptic vòng 4): *"byte-identical"* đúng cho **`orders[]`
trên đường bình thường** (plan chưa duyệt). Ngoại lệ: chạy với `--force-clear-approval`, lần 2
KHÔNG còn dòng cảnh báo tạm "XOÁ approved_by=…" trong `plan["merge_park_orders"]["warnings"]` (vì
lần 1 đã xoá chữ ký) — khác biệt nằm ở **khối báo cáo**, không phải ở lệnh. Nêu ngoại lệ, không
tuyên bố trần.

## quant-skeptic — 3 vòng đầu, cả ba CONFIRMED (medium); 5 khuyết tật ĐÃ SỬA

**Vòng 3** (trên bản đã sửa 4 khuyết tật) **CONFIRMED**: tái lập độc lập lại toàn bộ 6 con số A/B
từ artifact 08-07 thật, đếm lại số ca selfcheck **bằng profiler hook trên chính code object của
`check()`** (= 64, đúng như báo cáo; xác nhận luôn dòng `✘` dôi ra là của `print_report`), tái lập
census priority (43 plan hai chiều / 251 lệnh mua / dải 1–34 / **0** lệnh ở `priority ≤ 0`), và
xác nhận `preflight_check.sh` nhánh (a) đúng là báo động giả như tôi tự đính chính. **Nhưng nó phá
được một thứ vòng 2 không phá được — khuyết tật thứ 5:**

| # | Khuyết tật (vòng 3) | Sửa |
|---|---|---|
| 5 | **Cơ chế "sở hữu vùng + dựng lại" chỉ áp cho lệnh BÁN.** 3 nhãn `jit_status`/`jit_note`/`jit_underfunded` do bước 5 ghi lên lệnh **MUA** nằm NGOÀI vùng sở hữu ⇒ **không bao giờ bị xoá**. Chạy 1 với L2 đủ vốn ⇒ `jit_status="FUNDED"`; L2 sau đó bị **TỪ CHỐI** (reconcile fail) ⇒ chạy lại **vẫn hiện "FUNDED"**. Số lượng cổ phiếu vẫn đúng (I2 không phụ thuộc nhãn, lớp lỗi 08-07 vẫn đóng) — nhưng **người duyệt, cơ chế an toàn DUY NHẤT của thiết kế này, đọc trạng thái vốn SAI** | **ĐÃ SỬA** (bản vá thứ 5): bước **0** ở đầu `merge_park_orders()` xoá **VÔ ĐIỀU KIỆN** 3 nhãn khỏi **MỌI** lệnh trong `p["orders"]` ⇒ chúng theo đúng quy tắc của vùng bán: **dựng-lại-hoặc-vắng-mặt**. Nhóm ca `S5b` (7 ca) |
| 5b | **A4 nói quá phần đã kiểm**: nó so `set(layers)` trên 3 nhánh rồi gọi `print_report` đúng **một** lần ⇒ là proxy hình dạng, không phủ `dropped_owned`/`per_ticker`/`warnings`/`errors` mà `print_report` đọc thật | **ĐÃ SỬA**: A4 nay **gọi thật** `print_report()` trên **5 nhánh** (thêm `REFUSED-I1-dup` và `không-artifact`), bắt exception tại chỗ + kiểm output khác rỗng, kèm ca chứng minh ngược (bỏ id trùng ⇒ chính plan đó OK) |
| 5c | **Comment `priority` khẳng định quá**: "không nơi nào dùng nó ngoài khoá sắp xếp" bỏ sót `plan.py:149` (`:02d` trong id dự phòng) | **ĐÃ SỬA**: comment liệt kê đủ **3 loại** chỗ đọc (sắp xếp / so sánh số học `plan_funding_gate.py:194-214`, `plan.py:292` / định dạng chuỗi `plan.py:149`) và nêu rõ vì sao hệ quả bằng 0 (lệnh merge LUÔN có `id`) |

**Nhãn ở nhánh REFUSED — CỐ Ý không xoá.** `refuse()` trả `copy.deepcopy(plan)` (bản gốc chưa
đụng) nên nhãn cũ giữ nguyên; caller không ghi file ⇒ đĩa không đổi. Xoá nhãn ở nhánh đó sẽ phá
đúng bất biến "REFUSED ⇒ plan NGUYÊN VẸN" mà ca `S6` canh. Ca `S5b(e)` khoá hành vi này lại.

**Bằng chứng trên DỮ LIỆU THẬT** (không chỉ fixture): plan 08-07 thật của cả 2 tài khoản đang mang
`jit_note` do script one-off cũ (`merge_three_in_one_20260807.py`) ghi — chạy merge, nhãn đó bị
**thay bằng** nội dung của artifact L2 hiện tại chứ không phải sót lại; tổng qty **không đổi**
(SpaceX 6900, ZaloPay 2500), 2 lần chạy liên tiếp vẫn byte-identical.

**Vòng 2** (trên bản đã sửa) **CONFIRMED**: tái lập độc lập lại toàn bộ 6 con số A/B, tái lập CẢ
HAI chứng minh ngược của tôi (khôi phục clamp ⇒ đúng 3 ca V1b hỏng với thông điệp nguyên văn;
bỏ pre-init `layers` ⇒ `KeyError` trên đúng plan đã ký), chạy selfcheck xanh dưới 5 biến thể môi
trường. Kết luận: *"The substance holds and I could not break it."* Nó bác đúng **hai chỗ ghi
chép của tôi** (đã sửa ở trên: số ca 62→61→64, bằng chứng git rỗng) và nêu **hai tiềm ẩn**:

| Tiềm ẩn | Xử lý |
|---|---|
| **I4 bắt cả plan làm con tin**: qty lẻ (không bội lô) từ artifact ⇒ REFUSED toàn plan ⇒ 0 lệnh bán = **lại đúng hình dạng mất-phiên 08-06**, trong khi `_floor_lot` đã có sẵn trong file | **ĐÃ SỬA** (bản vá thứ 4): làm tròn xuống bội lô **vô điều kiện** ở bước sinh + hạ I4 xuống **cảnh báo**. Ca `V12`/`V12b`. Phơi nhiễm hiện tại bằng 0 (`compute_park_trim` dùng `round_lot()`, `compute_jit_unpark` cấp theo bội LOT) — nhưng đó là bất biến của **file khác**, không phải của file này |
| **`MERGE_STALE_SRC` báo động giả**: merge CỐ Ý giữ lệnh bán cùng mã của writer khác (ca `S3`) ⇒ `preflight_check.sh:86` nhánh (a) thấy 2 lệnh cùng `(sell,ticker)` trong đó 1 lệnh có `merged_from` ⇒ preflight **ĐỎ** trên một plan mà mọi bất biến merge đều PASS | **CHƯA sửa — thành việc #5 phải làm trước khi wire.** Không sửa ở đây vì `preflight_check.sh` là file của người khác (§3) và có selfcheck riêng. Phơi nhiễm 08-07 bằng 0 (`khác=0` mọi mã). Đính chính: câu "chúng ăn khớp" ở trên đúng cho nhánh (b), **KHÔNG** đúng cho nhánh (a) |

**Vòng 1** **CONFIRMED**: tái lập độc lập cả hai chân A/B trên artifact thật (khớp tới
từng cp), xác nhận nguyên nhân gốc có thật trong code (`approve_plan_with_jit.sh:47/56/57` vs
`merge_three_in_one_20260807.py`), và xác nhận luận điểm "cần cả hai lớp". Hai khuyết tật sống sót
đợt tấn công — **cả hai đã sửa, không phải khuyết tật của cơ chế mà của lớp kiểm chứng và một ca
biên**:

| # | Khuyết tật | Sửa |
|---|---|---|
| 1 | **Selfcheck V1b PASS vô căn cứ**: nó assert `all(...)` trên danh sách lệnh bán RỖNG của một plan bị REFUSED ⇒ `all([])` = True, che đúng cái nó tuyên bố kiểm | ca mới bắt buộc `status=="OK"` **và** tập lệnh bán khác rỗng trước khi so priority |
| 2 | **Lệnh MUA ở priority 0 ⇒ TỪ CHỐI CẢ PLAN**: `sell_pri = max(0, min(buy)-1)` clamp về 0 ⇒ bán = mua ⇒ bất biến I3 hỏng ⇒ 0 lệnh bán PARK = **đúng hình dạng mất-phiên 08-06** mà thiết kế này tuyên bố đã diệt | bỏ clamp — `priority` chỉ dùng làm khoá sắp xếp tăng dần (`executor.py:1232`, `plan.py:124`, đã kiểm), giá trị **âm hợp lệ**; bán rơi về −1. Thêm **I3b**: lệnh bán của writer KHÁC nằm sau lệnh mua ⇒ **cảnh báo, không chặn** (vấn đề có sẵn, merge không làm nặng thêm ⇒ từ chối cả plan chỉ tái lập đúng lỗi 08-06) |

**Khuyết tật thứ 3 — tôi tự tìm ra khi chạy CLI thật, sau khi selfcheck đã 58/58 xanh:** nhánh
`refuse()` ở cổng duyệt trả về **trước khi** `report["layers"]` được điền ⇒ `print_report` ném
`KeyError('L1')` trên đúng plan 08-07 (plan đó đã ký nên rơi vào nhánh này). Selfcheck **hàm thuần**
không thấy vì nó không bao giờ gọi `print_report`. Sửa: khởi tạo `layers`/`invariants` đủ khoá ngay
đầu hàm + ca `A4` chạy `print_report` thật trên cả 3 nhánh trả về. Đây đúng bài học skill
`verify-before-done`: **chạy đường THẬT, đừng chỉ test lõi** — 58/58 xanh không đồng nghĩa CLI chạy được.

**Chứng minh ngược cho bản vá (2)** — khôi phục clamp cũ rồi chạy lại: V1b **FAIL 3/3**, báo đúng
`I3: priority lệnh bán merge [0] không < mua [0]` và **0 lệnh bán**. Bỏ clamp ⇒ PASS. Phơi nhiễm
thực tế (đo lại, nêu rõ mẫu số vì vòng 1 tôi trích "0/42" không kèm định nghĩa): trong
`data/trade_plans/plan_*.json` có **43 plan chứa CẢ lệnh mua lẫn lệnh bán**, tổng **251 lệnh mua**,
`priority` chạy **1–34**, **0 lệnh** ở `priority ≤ 0` ⇒ ca này **tiềm ẩn, chưa từng nổ**. Vẫn phải
sửa vì nó mâu thuẫn với chính học thuyết "từ chối theo tầng" của thiết kế.

**Đính chính con số ca — và cách đếm SAI đã gây ra nó.** Bản ghi bus đầu nói "47"; số thật lúc
đó là **54** (quant-skeptic vòng 1 đếm). Sau ba bản vá tôi báo "62" — **cũng sai**, số thật là
**61** (quant-skeptic vòng 2). Nguyên nhân: tôi đếm bằng `grep -c "^  [✔✘]"` trên output, mà
`print_report()` **cũng in** một dòng bắt đầu `  ✘` ⇒ dôi 1. Đếm đúng = bọc chính hàm `check()`.
Sau khi thêm nhóm V12 (bản vá thứ 4): **64**, đo bằng cách bọc `check()`, không bằng grep.
Sau bản vá thứ 5 (nhóm `S5b` + A4 mở rộng): **76**, đo bằng **profiler hook trên code object
của `check()`** — đúng phương pháp quant-skeptic vòng 3 dùng để bác con số của tôi (vòng 4 tự
đếm lại, khớp **76**). Sau bản vá thứ 6 (nhóm `S5c` + `S5d`): **84**. Sau khi thay bản neo hỏng bằng xoá-theo-tiền-tố
(`S5d` viết lại): **85**. Sau 2 mục dư của vòng 6 (ranh giới quét cấp một): **86**.

## Selfcheck — 86/86 PASS

`merge_park_orders_selfcheck.py`. Mọi ca "chặn được" **đều có ca chứng minh NGƯỢC** (§24):

| Nhóm | Nội dung | Ca chứng minh ngược |
|---|---|---|
| **R** | regression 08-07: plan có CẢ lệnh gộp lẫn lệnh JIT gốc ⇒ hội tụ 1 lệnh/mã | `R0` đo được trạng thái đó **thật sự** bán 400cp > 300cp |
| **I** | chạy 2-3 lần cùng input ⇒ `orders[]` byte-identical | `I5` artifact đổi ⇒ ra số **mới**, không phải cũ+mới |
| **P** | PARTIAL (`reconcile_ok=false` + `reconcile_partial=true`) vẫn merge | `P2` bỏ cờ partial ⇒ tầng đó **thật sự** bị từ chối |
| **S** | trần sellable cắt tại merge, cắt L1 trước | `S2` sellable rộng ⇒ **không** cắt; `S5` ngược lại của `S1` |
| **A** | không tự duyệt; plan đã duyệt ⇒ REFUSED | `A2` `--force-clear-approval` chạy được nhưng **xoá** approved_by |
| **V** | 6 bất biến + biên (ref_price lệch, amendment mồ côi, artifact rác, plan rỗng, mua ở priority 0) | `V1b` khôi phục clamp cũ ⇒ FAIL 3/3; `V11` I3b sạch khi thứ tự đúng; `V10` plan đầu vào không bị mutate |

**Độc lập môi trường** (skill `verify-before-done`): bằng chứng THẬT là **module không có phụ
thuộc môi trường nào để mà hỏng** — chỉ `argparse, copy, json, os, sys`, không `datetime`, không
`TZ`, không env var, không mạng, không giờ. quant-skeptic vòng 5 nói đúng: chạy dưới nhiều `TZ`
với module này là bằng chứng **rỗng** — giữ lại như phép thử khói rẻ tiền, KHÔNG tính là bằng
chứng. Selfcheck PASS dưới **5 biến thể liệt kê tường minh** (không nói tổng, nói tên — quant-skeptic
vòng 3 bắt đúng chỗ này): mặc định · `TZ=UTC` · `TZ=America/New_York` · `env -u TZ` ·
`env -i` (môi trường trống hoàn toàn).

**§23 — phạm vi quét:** file MỚI, **0 selfcheck production phụ thuộc** (không import gì từ
`trading_bot/`). Không chạm `trading_bot/plan.py` ⇒ không kích hoạt 21 selfcheck phụ thuộc.

## Vị trí trong pipeline — đề xuất

**Giữ là script riêng ở `mike/bin/merge_park_orders.py`, KHÔNG đưa vào `trading_bot/plan.py`.**
Lý do: `plan.py` là module **đọc plan lúc THỰC THI** (`load_plan` gọi từ `bot_execute.py`); merge
là bước **soạn plan**. Nhét logic sửa plan vào module thực thi = mỗi lần bot chạy đều mang theo code
có khả năng ghi đè plan — sai tầng, và kéo theo 21 selfcheck phụ thuộc (§23) cho một việc không
thuộc về nó. Lõi vẫn là **hàm thuần** `merge_park_orders(plan, l1, l2)` (không I/O) nên test được
và gọi lại được từ bất kỳ đâu.

Khe cron đề xuất — **đúng khuôn `inject_discretionary_orders.sh` đã chạy ổn định từ 2026-07-24**:

```
DollarBill ghi plan ~19:0x
  → 19:3x  compute_park_trim.py (L1)  +  compute_jit_unpark.py --l1-json … (L2)   [CHƯA có cron]
  → 20:2x  merge_park_orders.py --write        ← BƯỚC MỚI
  → 20:30  inject_discretionary_orders.sh      (đã có)
  → 21:00  send_plan_report.sh                 (đã có)
```

Chạy qua `for_each_live_account.sh` để account mới tự có. **Chưa đề xuất cài cron ngay** — xem
"Cổng chưa qua".

## Chính sách cần Mike/user quyết — KHÔNG tự quyết

**Hỏi: sau khi merge, có tự publish thẳng vào `orders[]` mà không cần duyệt lại không?**

Thiết kế hiện tại chọn **giữ nguyên approval gate**, cụ thể:
- luôn đặt `requires_user_approval=true`, **không bao giờ** ghi `approved_by`;
- plan **đã có** `approved_by` ⇒ **TỪ CHỐI** sửa (sửa lệnh sau khi duyệt = vô hiệu hoá chữ ký);
  muốn sửa thật phải `--force-clear-approval`, và cờ đó **xoá** `approved_by` để buộc duyệt lại.

Khuyến nghị của tôi: **giữ nguyên** — merge chỉ chuyển đề xuất từ key phụ vào `orders[]`, nó
không làm cho đề xuất đó đúng hơn, và đây là đường sinh lệnh bán/mua tiền thật của cả 2 account.
Nhưng đây là **quyết định chính sách**, không phải kỹ thuật ⇒ user/Mike quyết, tôi chỉ đề xuất.

## Việc PHẢI làm trước khi wire (không phải tuỳ chọn)

1. **`send_plan_report.sh` sẽ hiển thị TRÙNG.** Nó render `park_trim_proposal`/`jit_unpark_proposal`
   thành mục riêng (`:629`, `:698`) **và** render `orders[]`. Sau merge, cùng một lệnh xuất hiện ở
   hai chỗ ⇒ người duyệt dễ đọc thành "bán 2 lần". Merge đã ghi `_merged_into_orders` vào 2 key đó,
   nhưng báo cáo **chưa đọc cờ này**. Phải sửa báo cáo (đọc `_merged_into_orders` → in "đã gộp vào
   orders[], không thực thi riêng") **trước** khi chạy live. Tôi CỐ Ý không sửa `send_plan_report.sh`
   trong bản này (§3 surgical; file của người khác, cần review riêng).
2. **L1/L2 chưa có cron.** Merge tự động vô nghĩa nếu artifact vẫn phải chạy tay. Cần quyết định
   cron cho `compute_park_trim.py`/`compute_jit_unpark.py` (§11: cập nhật `kb/cron_registry.md`
   **cùng commit** với dòng crontab). Lưu ý vintage: cả hai lấy giá qua DNSE `close_price()`, trả 0
   khi phiên chưa đóng ⇒ **phải chạy SAU 15:00 ICT**, nếu không rơi về giá BQ T-1 (đúng cái đã xảy
   ra 08-07, ghi trong `risk_notes` của plan hôm đó).
3. **Bản vá kế toán PARTIAL phải áp TRƯỚC hoặc CÙNG lúc.** Merge này đọc `reconcile_partial` —
   field đó chỉ tồn tại sau `pending_park_trim_partial_reconcile_20260810/`. Chưa áp thì nhánh
   PARTIAL không bao giờ kích hoạt (hành vi = từ chối tầng, an toàn nhưng vô ích).
4. **`approve_plan_with_jit.sh` phải gỡ phần merge** khi bước mới lên live, nếu không lại là hai
   writer cùng vùng — đúng cấu hình sinh ra 08-07. Cơ chế nhận nuôi khiến hậu quả **hội tụ** thay vì
   nhân đôi, nhưng đừng dựa vào lưới an toàn để giữ hai writer. **Gỡ luôn cả clamp `max(0, …)` ở
   `:49-52`** — chính clamp vừa bị bỏ ở đây; để lại thì hai tầng bất đồng về priority lệnh bán.
5. **Quyết định tương tác `MERGE_STALE_SRC`** (quant-skeptic vòng 2). Chọn một: (a) thu hẹp
   `preflight_check.sh:85-86` nhánh (a) để bỏ qua lệnh mang `merge_owner=park_merge_v1` — merge đã
   tự bảo đảm 1 lệnh/`(sell,ticker)` trong vùng của nó; hoặc (b) cho merge phát ra một field để
   preflight phân biệt. Không quyết ⇒ một plan hợp lệ có lệnh bán cùng mã của writer khác sẽ làm
   preflight ĐỎ. Đây là **sửa file của người khác** ⇒ cần dispatch riêng, không gộp vào bản này.
6. **Ghi HỢP ĐỒNG nhánh REFUSED tại CHỖ GỌI, không chỉ trong docstring** (quant-skeptic vòng 4).
   `merge_park_orders()` trả về plan **NGUYÊN VẸN** khi REFUSED — kể cả nhãn `jit_*` cũ. CLI hiện
   tại đúng (`main()` chỉ ghi khi `status == "OK"`), nhưng một caller lập trình tương lai ghi file
   trên trạng thái khác OK sẽ **mở lại khuyết tật #5 bằng cửa sau**. Khi wire vào pipeline, chặn
   điều đó ở chỗ gọi.

## Cách áp (khi được duyệt)

```bash
cd /home/trido/thanhdt/WorkingClaude
cp mike/agents/Taylor/pending_park_merge_20260810/merge_park_orders.py mike/bin/
cp mike/agents/Taylor/pending_park_merge_20260810/merge_park_orders_selfcheck.py mike/bin/
python3 mike/bin/merge_park_orders_selfcheck.py          # kỳ vọng: PASS (86 ca)
# dry-run trên plan thật, KHÔNG ghi (mặc định là dry-run):
python3 mike/bin/merge_park_orders.py --account SpaceX --plan-date <YYYY-MM-DD>
```

**Rollback**: `rm mike/bin/merge_park_orders.py` (+ gỡ dòng cron nếu đã cài). Không có file
production nào bị sửa nên không có gì phải hoàn nguyên. Rollback "mềm": bỏ `--write` ⇒ chỉ in
báo cáo, không đụng plan.

## Cổng chưa qua

| # | Cổng | Trạng thái |
|---|---|---|
| 1 | quant-skeptic vòng 1 | ✅ CONFIRMED (medium) — 2 khuyết tật, đã sửa |
| 1b | quant-skeptic vòng 2 trên bản đã sửa | ✅ CONFIRMED (medium) — "could not break it"; 2 lỗi ghi chép + 2 tiềm ẩn |
| 1c | quant-skeptic vòng 3 (sau bản vá I4 + đính chính ghi chép) | ✅ CONFIRMED (medium) — phá được **khuyết tật #5** (nhãn `jit_*` trên lệnh MUA không bao giờ hết hạn) + 2 việc phụ |
| 1d | quant-skeptic vòng 4 (sau bản vá #5 + A4 5 nhánh + comment priority) | ✅ CONFIRMED (**high**) — phá được **khuyết tật #6** (khối đề xuất nhúng không hết hạn) + `_JIT_ANNOTATIONS` không neo vào chỗ ghi |
| 1e | quant-skeptic vòng 5 (sau bản vá #6 + `_annotate_buy`) | ⚠️ **REFUTED (high)** — #6 đứng vững, bản neo #6b hỏng (quy ước ≠ bất biến). Đã thay bằng xoá-theo-tiền-tố |
| 1f | quant-skeptic vòng 6 (sau xoá-theo-tiền-tố) | ✅ **CONFIRMED (high)** — tự chạy lại probe vòng 5: nhãn thứ 4 KHÔNG còn sống sót, selfcheck ĐỎ đúng chỗ. 2 mục dư (câu phạm vi sai + ranh giới cấp một chưa có test) **đã sửa nốt sau verdict**, selfcheck 86/86 |
| 2 | User/Mike duyệt — chạm đường sinh lệnh LIVE cả 2 account | ⛔ chưa |
| 3 | Quyết định chính sách: giữ hay bỏ approval gate sau merge | ⛔ chưa (user quyết) |
| 4 | 5 việc "phải làm trước khi wire" ở trên | ⛔ chưa |
| 5 | ≥1 phiên shadow (chạy dry-run, đối chiếu với plan người duyệt) | ⛔ chưa |

**Đây là sửa CƠ CHẾ AN TOÀN, không phải chiến lược** — không tham số nào tune theo lịch sử, không
backtest NAV nào đứng sau ⇒ không áp chuẩn DSR/PBO. Bằng chứng = A/B trên đúng dữ liệu 2 tài khoản
phiên 2026-08-07 + 86 ca selfcheck có chứng minh ngược.

**n=1 ngày.** A/B đứng trên đúng một phiên (2 account). Không có ý nghĩa thống kê và cũng không cần
— đây là bất biến cơ chế, không phải edge. Nhưng nó cũng có nghĩa: **chưa từng có ngày PARTIAL thật
nào chạy qua đường này**; nhánh đó mới chỉ được chứng minh bằng selfcheck (`P1`/`P3`), chưa bằng dữ
liệu sống.
