# WIRE `merge_park_orders` vào pipeline thật + vá báo động giả `MERGE_STALE_SRC`

**Job** `Taylor_20260810_185646` · 2026-08-11 · Taylor · nối tiếp chuỗi
`Taylor_20260810_131833` → `_142416` → `_172111` (commit `da7d5cc2`).
**Trạng thái**: code đã vào `mike/bin/`, đường merge cũ đã GỠ. **Chưa cài cron nào** — xem §6.

---

## 0. Kết luận ngắn

| Việc | Kết quả |
|---|---|
| Vá `MERGE_STALE_SRC` báo động giả ở `preflight_check.sh` | XONG — 12/12, chứng minh ngược trên HEAD cũ đỏ ĐÚNG 1 ca |
| `merge_park_orders.py` → `mike/bin/` | XONG (`git mv`, giữ lịch sử) |
| Gỡ đường merge cũ ở `approve_plan_with_jit.sh` | XONG — gỡ HẲN, thay bằng cổng fail-closed + uỷ quyền duyệt |
| Approval gate giữ nguyên (`requires_user_approval`, không tự ký) | XÁC NHẬN còn đúng sau khi lắp — G2/G8/G9 |
| A/B 08-07 qua đường TÍCH HỢP | KHỚP 6.900cp SpaceX / 2.500cp ZaloPay, cả chân A lẫn chân B |
| Cron cho bước merge | **CHƯA CÀI — cần user quyết** (§6) |

**Hai khuyết tật THẬT phát sinh ở tầng tích hợp, cả hai đã vá.** Cả hai đều vô hình với 10
vòng quant-skeptic trước vì 10 vòng đó verify script **đứng riêng**.

---

## 1. Khuyết tật #1 — artifact VẮNG MẶT ⇒ merge xoá sạch lệnh bán, báo `status=OK`

`main()` đọc artifact bằng `_read_json()`; file thiếu ⇒ `None` ⇒ `_layer_state()` trả
*"không có artifact — bỏ qua tầng này (không phải lỗi)"*. Nhưng bước 1 vẫn **xoá toàn bộ vùng
sở hữu**, gồm cả lệnh **nhận nuôi** của writer khác. Đo thật trước khi vá:

```
plan: 1.300cp bán PARK (VHM 300 + BID 1.000) + 1 lệnh mua DRI 2.000cp
merge(l1=None, l2=None)  →  status: OK
                            orders sau: [('BUY-DRI-01', 'buy', 2000)]
                            Σ bán: 1300 → 0
```

`status=OK` ⇒ `--write` **ghi đè**. Đây đúng hình dạng mất-phiên **08-06** (lệnh mua còn,
nguồn tài trợ biến mất), và nguy hiểm hơn vì **L1/L2 hiện không có cron** ⇒ artifact vắng mặt
là trạng thái THƯỜNG chứ không phải ngoại lệ.

**Vì sao 10 vòng trước không thấy:** người chạy tay đọc báo cáo sẽ thấy dòng "L1: không có
artifact" ngay trên màn hình. Một bước pipeline thì **không ai đọc**. Cùng một hành vi, hai
mức nguy hiểm khác hẳn — và chỉ mức thứ hai mới tồn tại sau khi wire.

**Bản vá (bước 4b)** — phân biệt dứt khoát hai thứ bản cũ gộp làm một:

| Tình huống | Bản cũ | Bản mới |
|---|---|---|
| artifact **CÓ MẶT**, nói "không bán" (`NO_JIT`/`BLOCKED_RECONCILE`) | xoá | **xoá** — phát biểu có thẩm quyền |
| artifact **VẮNG MẶT** | xoá (im lặng) | **REFUSED**, plan nguyên vẹn |

Chặn theo **lượng mất per-ticker**, không theo "có drop hay không" — nhờ vậy chạy lại lần 2
với cùng artifact vẫn dựng lại đủ lượng ⇒ **không mất** ⇒ tính idempotent còn nguyên (ca A6e).

7 ca mới `A6a–A6g`, gồm 3 ca **chứng minh cổng không chặn oan** (A6d artifact có mặt nói
"không bán" ⇒ vẫn xoá; A6e idempotent; A6g plan chỉ-mua). Mutation test: đặt `absent = []`
⇒ **đúng 4 ca A6 chết** (A6a/A6b/A6c/A6f), 3 ca "không được chặn" vẫn xanh.

## 2. Khuyết tật #2 — `_merged_into_orders` là QUY ƯỚC DÙNG CHUNG, không phải bằng chứng

Bản đầu của cổng trong `approve_plan_with_jit.sh` bám vào dấu `_merged_into_orders` để trả
lời "plan này đã qua merge chưa". A/B tích hợp bác ngay: chạy cổng trên
`plan_SpaceX_2026-08-07.json` **thật** ⇒ `rc=0`, **cho qua và ký**.

Nguyên nhân: script one-off cũ `agents/DollarBill/merge_three_in_one_20260807.py` ghi **Y HỆT**
chuỗi `"✅ ĐÃ MERGE vào orders[]…"` vào cùng khoá đó. Nghĩa là cổng công nhận một plan gộp bằng
**đúng cơ chế đã gây sự cố 08-07**.

Đây là **lần thứ hai trong cùng dự án** vấp lớp lỗi "quy ước ≠ bất biến" — lần đầu là vòng 5
quant-skeptic REFUTED (neo #6 bằng danh sách tên literal).

**Bản vá:** đổi bằng chứng sang khoá cấp plan **`merge_park_orders.owner == "park_merge_v1"`**
— khối nhật ký mà **chỉ** cơ chế mới ghi. Đã đo: plan 08-07 thật **không** có khoá này.
Ca `G10` ghim đúng hình dạng đó (dấu ✅ + thiếu khoá ⇒ phải từ chối).

## 3. Vá `MERGE_STALE_SRC` báo động giả (Phần 1 của dispatch)

Merge **cố ý** giữ lệnh bán của writer khác cùng mã (bất biến I5, ca S3) ⇒ một mã hợp lệ có
2 lệnh bán, một mang `merged_from` ⇒ nhánh (a) đọc thành "còn sót lệnh nguồn" ⇒ ĐỎ giả.
Đỏ giả lặp lại = tầng dưới học cách bỏ qua, đúng cách một lưới an toàn chết trong im lặng.

**Chọn hướng (a)** — thu hẹp nhánh (a) — nhưng **không** thu hẹp theo cách quant-skeptic gợi ý
nguyên văn ("bỏ qua lệnh mang `merge_owner=park_merge_v1`"). Bỏ qua theo NHÃN SỞ HỮU sẽ mất độ
phủ cho ca "ai đó thêm lệnh PARK sau khi merge chạy". Thu hẹp theo **MIỀN**:

```python
_stale = {tk for (sd, tk), v in _by_key.items()
          if len(v) > 1 and any(o.get("merged_from") for o in v)
          and sum(1 for o in v if _merge_domain(o)) > 1}   # ≥2 lệnh THUỘC MIỀN merge
```

`_merge_domain` = có `merge_owner=park_merge_v1` **hoặc** `merged_from` **hoặc** `play_type ∈
{PARK_TRIM, JIT_UNPARK, PARK_TRIM+JIT_UNPARK}`. Cố ý **không** đòi `book=PARK`: lệnh sót thật
ngày 08-07 (`SELL-JIT-PARK-<mã>-01`) nhận diện được bằng `play_type`.

**Vì sao thu hẹp (a) là an toàn:** nhánh **(b) `SELL_GT_SELLABLE` không đổi một chữ**, và nó
mới là nhánh chặn RỦI RO TIỀN (bán vượt lô sở hữu) — vẫn chạy trên mọi lệnh kể cả lệnh merge
(ca #12 canh đúng điều đó). (a) chỉ là heuristic cấu trúc, và cơ chế merge nay thay nó bằng
một bảo đảm mạnh hơn (1 lệnh/`(sell,ticker)` trong miền, dựng lại mỗi lần chạy).

**Chứng minh ngược** (`PF_SRC` trỏ vào bản HEAD cũ): chạy bộ 12 ca mới trên preflight CŨ ⇒
**đúng 1 ca đỏ, là #10** (ca báo động giả). #11 (độ phủ 08-07) và #12 (nhánh b) vẫn xanh trên
cả hai bản ⇒ bản vá đụng đúng cái cần đụng, không đụng gì khác.

⚠️ **Đổi hành vi phụ, khai báo rõ:** ca #7 (lệnh bán không có `play_type`/`book` đứng cạnh lệnh
gộp) trước báo `MERGE_STALE_SRC`, nay không. Đúng ý đồ — lệnh không mang dấu nào của miền merge
là lệnh của writer khác, tức ca S3 hợp lệ. Assertion của #7 (không crash) không đổi.

## 4. `approve_plan_with_jit.sh` — gỡ merge, thêm cổng

Gỡ **HẲN** đường merge (không phải tắt bằng cờ): giữ hai writer trên cùng một vùng là tái lập
đúng cấu hình sinh ra 08-07. Nhưng **gỡ mà không thêm cổng = đổi lớp lỗi 08-07 lấy lớp 08-06**:
duyệt một plan còn đề xuất bán PARK chưa gộp ⇒ plan có lệnh MUA mà thiếu lệnh BÁN tài trợ.
Nên script giờ làm đúng 2 việc: **cổng** (§2) + **uỷ quyền** phần duyệt cho
`approve_plan_simple.sh`.

Uỷ quyền chứ không chép: `approve_plan_simple.sh` đã có sẵn kiểm trùng ticker, kiểm Σ nguồn
tài trợ ≥ Σ mua, atomic write, bus event, Discord notify. Nhân bản logic duyệt ra hai file là
đúng cái bẫy §10 cảnh báo — và hai script duyệt gần trùng nhau chính là thứ đã có sẵn trong
`mike/bin/` từ 08-07.

## 5. A/B TÍCH HỢP trên dữ liệu thật 08-07 — qua CLI, không gọi hàm

`mike/agents/Taylor/exp_park_merge_wire_20260811/ab_integrated_0807.sh` (chỉ đọc; mọi thứ chép
sang `/tmp`). Kết quả:

```
CỔNG DUYỆT TRƯỚC KHI GỘP (phải TỪ CHỐI)
  SpaceX : rc=2 · approved_by=None          ZaloPay: rc=2 · approved_by=None
CHÂN A (plan người đã sửa đúng) + CHÂN B (dựng lại trạng thái HỎNG)
  chân A SpaceX : merge THẬT SỰ chạy=True  khớp người duyệt=True  Σ 6900/6900
  chân A ZaloPay: merge THẬT SỰ chạy=True  khớp người duyệt=True  Σ 2500/2500
  chân B SpaceX : merge THẬT SỰ chạy=True  khớp người duyệt=True  Σ 6900/6900
  chân B ZaloPay: merge THẬT SỰ chạy=True  khớp người duyệt=True  Σ 2500/2500
CỔNG DUYỆT SAU KHI GỘP (phải CHO QUA + ghi chữ ký)
  SpaceX : rc=0 · approved_by='user (test A/B)' · Σ bán 6900 (không đổi)
  ZaloPay: rc=0 · approved_by='user (test A/B)' · Σ bán 2500 (không đổi)
```

⚠️ **Lần chạy ĐẦU của chính harness này cho một kết quả TRÔNG NHƯ HỢP LỆ mà sai** — đáng ghi
lại vì nó là bài học về harness, không phải về code:
- khối "cổng trước khi gộp" chạy thẳng trên thư mục plan dùng chung ⇒ khi cổng (bản đầu, còn
  bám dấu ✅) cho qua, nó **KÝ** plan ⇒ mọi chân merge sau đó REFUSED vì "plan đã duyệt";
- REFUSED trả plan **nguyên vẹn**, mà plan đó là bản người đã sửa đúng ⇒ `Σ = 6900/2500`
  ⇒ dòng "khớp người duyệt=True" vẫn in ra, **trong khi merge chưa hề chạy**.

Cùng họ với khuyết tật "PASS vô căn cứ" ở §5b tài liệu trước. Đã sửa hai chỗ: cổng chạy trên
**bản sao riêng**, và điều kiện khớp đòi thêm **`merge_park_orders.owner` có mặt + rc=0**
(bằng chứng merge THẬT SỰ chạy), không chấp nhận mỗi "Σ khớp".

## 6. ⛔ CHƯA CÀI CRON — cần user quyết (KHÔNG tự đoán)

Đã tra: **không có cron nào** chạy `compute_park_trim.py` (L1) hay `compute_jit_unpark.py` (L2),
và **không script nào gọi chúng** (grep toàn repo, `crontab -l`). Hai artifact đó tới nay do
DollarBill chạy tay trong dispatch EOD.

⇒ Cài cron cho **riêng** bước merge là vô nghĩa: ngày thường không có artifact để gộp. (Nhờ
bước 4b, nó nay **từ chối an toàn** thay vì xoá lệnh — nhưng "an toàn" ≠ "hữu ích".)

**Đề xuất chuỗi** (đúng khuôn `inject_discretionary_orders.sh` đã ổn định từ 2026-07-24):

```
DollarBill ghi plan ~19:0x
  → 19:3x  compute_park_trim.py (L1) + compute_jit_unpark.py --l1-json … (L2)   [CHƯA có cron]
  → 20:2x  merge_park_orders.py --write                                         [BƯỚC MỚI]
  → 20:30  inject_discretionary_orders.sh   (đã có)
  → 21:00  send_plan_report.sh              (đã có)
```

Ràng buộc cứng: **phải sau 15:00 ICT** — L1/L2 lấy giá qua DNSE `close_price()`, trả 0 khi
phiên chưa đóng (đúng cái đã xảy ra 08-07). Chạy qua `for_each_live_account.sh`.

**Vì sao tôi dừng ở đề xuất:** (a) đây là 2 dòng cron **thực thi thật** chạm đường sinh lệnh
của cả 2 account — `current_ops.md` ghi rõ loại này luôn phải hỏi user trước; (b) §11 buộc cập
nhật `kb/cron_registry.md` **cùng commit**, và phải trả lời 4 câu hỏi bắt buộc cho **cả hai**
script L1/L2 — đó là quyết định về lịch của script **người khác sở hữu**, không phải của bước
merge.

## 7. Việc trước khi wire — trạng thái từng mục (7 mục ở README cũ)

| # | Việc | Trạng thái |
|---|---|---|
| 1 | `send_plan_report.sh` hiển thị TRÙNG (chưa đọc `_merged_into_orders`) | ⛔ **CHƯA LÀM** — file người khác; selfcheck của nó đang 6 PASS/14 FAIL **từ trước** (đo trên worktree HEAD sạch: y hệt) |
| 2 | L1/L2 chưa có cron | ⛔ chưa — §6, cần user quyết |
| 3 | Bản vá kế toán PARTIAL áp trước/cùng lúc | ⛔ chưa áp (`pending_park_trim_partial_reconcile_20260810/` vẫn chờ duyệt). Merge đọc `reconcile_partial`; chưa có ⇒ nhánh PARTIAL không kích hoạt — **an toàn nhưng vô ích**, không chặn việc wire |
| 4 | Gỡ merge khỏi `approve_plan_with_jit.sh` (+ clamp `max(0,…)`) | ✅ XONG |
| 5 | Quyết định `MERGE_STALE_SRC` | ✅ XONG (§3) |
| 6 | Ghi hợp đồng namespace `jit_*` ở script sinh plan | ⛔ chưa — file người khác; bán kính ảnh hưởng đo được **= 0** (chỉ `jit_unpark_note`, 0 consumer) |
| 7 | Chặn nhánh REFUSED ở CHỖ GỌI | ✅ đúng sẵn — `main()` chỉ ghi khi `status == "OK"`; cổng 4b nay thêm một lớp nữa vào chính nhánh đó |

## 8. Kiểm chứng

| Bộ | Kết quả |
|---|---|
| `merge_park_orders_selfcheck.py` | **120/120** (113 cũ + 7 ca A6). Mutation `absent=[]` ⇒ 4/4 ca A6 chết đúng |
| `approve_plan_with_jit_selfcheck.py` | **27/27** (mới) — chạy script THẬT trong cây giả, không mock. (Bản báo cáo đầu ghi "22"; số thật lúc đó **21** — quant-skeptic đếm lại đúng. 27 = 21 + 6 ca G11–G16 thêm sau verdict.) |
| `preflight_order_invariants_selfcheck.py` | **12/12** (9 cũ + 3 mới). Chứng minh ngược trên HEAD cũ: đúng 1 ca đỏ |
| Quét §23 subsystem | `compute_park_trim` / `compute_jit_unpark` / `compute_active_nav` / `corp_action` / `book_tagging` ✅ PASS; `send_plan_report_park_jit` 6/14 — **baseline y hệt trên HEAD sạch**, 0 do bản này |
| Môi trường | 3 selfcheck × {TZ ICT / NY / UTC / `-u TZ` / `env -i`} = **15/15 exit 0** |
| ShellCheck gate | `preflight_check.sh`, `approve_plan_with_jit.sh` — exit 0 |
| A/B tích hợp 08-07 | §5 — 6.900 / 2.500 khớp tuyệt đối cả 2 chân |

**md5 tại mốc verify** (bài học vòng 10 — ghi md5 ngay tại mốc, đừng neo bằng mtime):

| file | md5 |
|---|---|
| `mike/bin/merge_park_orders.py` | `26ffe6f87a7c7be12250b0422658a299` |
| `mike/bin/merge_park_orders_selfcheck.py` | `364c5c874f0bd364b211e06905f26ce2` |
| `mike/bin/approve_plan_with_jit.sh` | `0ba8c735d993f8c1cd61e018757cab3b` |
| `mike/bin/approve_plan_with_jit_selfcheck.py` | `05345b3a537a7f10f2793670e18b06b2` |
| `mike/bin/preflight_check.sh` | `8eb2631ea13cfc2b1bb7374e6c3098e0` |
| `mike/bin/preflight_order_invariants_selfcheck.py` | `4646b41334c77a3abbcd5a3a229f67f8` |

## 9. Giới hạn — cái này KHÔNG giải quyết

- **Chưa chạy trên dữ liệu SỐNG.** A/B đứng trên 08-07 lịch sử. Lần gọi thật đầu tiên (sau
  15:00 ICT, khi có L1/L2 mới) vẫn là "phiên shadow" còn thiếu — xuất báo cáo, đối chiếu, và
  **không** đưa vào plan production nếu có gì khác kỳ vọng.
- **Không** làm đề xuất L1/L2 đúng hơn; sai từ L1/L2 vẫn đi thẳng vào plan.
- ~~`approve_plan_simple.sh` chặn oan ca S3~~ — **ĐÃ VÁ** sau verdict (§10 mục 2).
- **n=1 ngày dữ liệu thật.** Không có ý nghĩa thống kê nào ở đây và cũng không cần — đây là
  bất biến cơ chế, không phải edge.


---

## 10. Vòng quant-skeptic (2026-08-11) — **CONFIRMED (`high`)**, và 2 việc phải sửa sau verdict

Reviewer tự tái lập **mọi** con số từ shell sạch (6/6 md5 khớp; 120/120; 12/12; chứng minh
ngược đúng 1 ca đỏ; mutation `absent=[]` giết đúng 4 ca A6 và để nguyên 3 ca must-not-block;
A/B 6900/6900 + 2500/2500 cả hai chân; ma trận môi trường 15/15), và tự đo lại **cả hai khuyết
tật** thay vì tin báo cáo. Nhưng phá được **1 chỗ THẬT chưa công bố** + 2 mục nhỏ:

### (1) KILLER OBJECTION — cổng chỉ nhìn khối trong plan, mà L1/L2 chỉ ghi ra FILE

`compute_park_trim.py` / `compute_jit_unpark.py` ghi ra **artifact file** (`--out`), chúng
**không bao giờ** ghi khối `*_proposal` vào plan — trong chuỗi cron ở §6, khối đó do **chính
merge** ghi (bước 6). ⇒ một plan "có lệnh mua, **chưa merge lần nào**" là plan KHÔNG khối,
KHÔNG dấu ⇒ cổng bản trước **cho qua**. Reviewer tự dựng đúng hình dạng đó và chạy cổng thật:
in `✅ cổng gộp` rồi uỷ quyền duyệt, `rc=0`, **merge chưa hề chạy**.

Cổng chỉ "có răng" hôm nay vì luồng chạy tay hiện tại ghi khối bằng script one-off — tức là
nó **mất răng đúng lúc cron ở §6 được cài**, thời điểm nó cần răng nhất.

**Đã vá:** cổng nay đọc **artifact trên đĩa** (`park_trim_{acct}_{date}.json` /
`jit_unpark_{acct}_{date}.json` cạnh plan) làm nguồn bằng chứng độc lập, `n = max(khối, file)`;
file có mà đọc không được ⇒ fail-closed. 4 ca mới `G11–G14`, trong đó **G13/G14 là ca chứng
minh không-chặn-oan**. Mutation (đổi `if os.path.exists(art_path)` → `if False`) ⇒ **đúng
G11+G12 chết**, G13/G14 vẫn xanh.

⚠️ Reviewer cũng đúng rằng ca `G6` ("plan không khối ⇒ không chặn") mã hoá đúng giả định làm
hỏng cổng. G6 nay chỉ còn đúng trong phạm vi hẹp **không có artifact nào trên đĩa** — G11/G12
là ca đối trọng của nó.

### (2) `approve_plan_simple.sh:49` chặn oan ca S3 — reviewer xác nhận CÓ THẬT ⇒ đã vá luôn

Tôi đã công bố mục này ở §9 như "chưa vá, ngoài phạm vi". Reviewer xác nhận nó sẽ **chặn một
plan hợp lệ sau merge** và xếp vào việc phải xong **trước lần chạy live đầu tiên**. Vì
`approve_plan_with_jit.sh` nay uỷ quyền thẳng sang script đó, để nguyên = biết đường mình vừa
lắp đang hỏng ⇒ vá luôn, cùng cách đã dùng cho `MERGE_STALE_SRC`: so theo **(side, ticker)** và
chỉ tính lệnh **thuộc miền merge**. Ca `G15` (không chặn oan) + `G16` (chứng minh ngược: 2 lệnh
cùng miền ⇒ VẪN chặn).

### (3) Hai mục nhỏ

- **Đếm sai: báo "22/22", số thật 21.** Đây là **lần thứ ba** trong cùng chuỗi dự án một khẳng
  định sai vì **đếm gián tiếp** thay vì đo trực tiếp thứ cần đo (lần 1: `grep -c` dôi 1 vì
  `print_report`; lần 2: bộ lọc rỗng PASS vô căn cứ). Nay đếm bằng số tick THẬT SỰ in ra:
  **27** (21 + 6 ca mới).
- **ShellCheck**: không cài trên host của reviewer ⇒ mục đó reviewer để "chưa verify được".
  Trên host này gate chạy thật: `preflight_check.sh` / `approve_plan_with_jit.sh` /
  `approve_plan_simple.sh` đều **exit 0**.

### Chạy lại sau khi vá (toàn bộ, không chỉ phần đụng)

```
selfcheck : preflight 12/12 · merge 120/120 · approve 27/27 · compute_park_trim ·
            compute_jit_unpark · compute_active_nav · corp_action · book_tagging — exit 0 hết
môi trường: 3 selfcheck × {ICT, NY, UTC, -u TZ, env -i} = 15/15 exit 0
shellcheck: 3/3 gate exit 0
A/B 08-07 : cổng trước rc=2 không ký · chân A+B merge THẬT SỰ chạy, 6900/6900 + 2500/2500 ·
            cổng sau rc=0 ký được, Σ bán không đổi
```
