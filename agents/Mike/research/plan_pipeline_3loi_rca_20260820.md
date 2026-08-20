# RCA + Plan fix — 3 lỗi pipeline lập plan T+1 (2026-08-20)

> Điều tra theo yêu cầu user 2026-08-20 19:51 ICT. Mọi kết luận dưới đây có bằng chứng log/code
> chạy trong cùng phiên điều tra, không suy đoán.

## TL;DR

| # | Lỗi | Nguyên nhân gốc | Tầng cần fix |
|---|---|---|---|
| 1 | 2 task gần đồng thời làm "cùng một việc" | Fan-out per-account là **cố ý**; nhưng mỗi job tự bắn wake push riêng → N phiên Mike song song trên 1 thread | `dispatch.sh` (batch-aware wake) + ccdb (session-running dedupe) |
| 2 | 2 account hiểu "Trứng vàng" khác nhau | **Bất đối xứng prompt**: chỉ ZaloPay được trỏ tới `compute_active_nav.py` (nơi lộ `egg`), SpaceX thì không | `bq_freshness_check.sh` + gate cơ học |
| 3 | Vẫn lập lệnh mua VPI dù đã chốt paper-track | Ranh giới chỉ nằm ở `kb/current_ops.md` — file **DollarBill không import**; registry khai `feature_flag: N/A` = không cưỡng chế gì | Cơ chế `signal_holds` mới + gate deterministic |

**Không có tiền nào đang bị rủi ro tối nay**: `plan_ZaloPay_2026-08-21.json` có
`approved_by: None`, `requires_user_approval: True` → bot 09:05 sẽ không thực thi lệnh VPI khi
chưa duyệt. Nhưng plan vẫn nằm đó chờ duyệt và **nội dung đang sai ranh giới**.

---

## Lỗi 1 — N account → N task → N phiên Mike

### Cơ chế thật

`bin/bq_freshness_check.sh:590` là vòng lặp **per-account** cố ý:

```bash
for ACCT in $LIVE_LABELS; do
  ...
  "$ROOT/bin/dispatch.sh" DollarBill "Lập plan T+1 cho tài khoản $ACCT..." --bg
done
```

Đây **không phải bug ngẫu nhiên** — nó chạy mỗi phiên giao dịch. Đo trên `bus/jobs/`: đúng
**2 job DollarBill mỗi ngày** suốt 08-05 → 08-20.

Vấn đề nằm ở tầng đánh thức. Mỗi job xong, `_bg_wrapper` tự gọi `wake_thread.sh` **độc lập**:

```
2026-08-18 19:09:22  job DollarBill_20260818_120602 → task 1764   ← cách nhau 31 giây
2026-08-18 19:09:53  job DollarBill_20260818_120604 → task 1765
2026-08-20 19:10:56  job DollarBill_20260820_120551 → task 1864   ← cách nhau 83 giây
2026-08-20 19:12:19  job DollarBill_20260820_120550 → task 1865
```

⇒ **Tái diễn ít nhất 2 lần (08-18 và 08-20), không phải một lần.**

CCDB có cưỡng chế "tối đa 1 one-shot wakeup **pending** mỗi thread"
(`delete_pending_one_shot_by_thread()`). Nhưng bất biến đó chỉ phủ **hàng đợi**, không phủ
**phiên đang chạy**: task 1864 được consume → không còn pending → task 1865 tới 83 giây sau
không thấy gì để xoá → tạo phiên B **song song với phiên A vẫn đang chạy**.

Bằng chứng 2 phiên song song trong `plan channel` (12:14:55Z và 12:15:21Z là **2 lần
auto-compaction riêng biệt** — một phiên không thể compact 2 lần cách nhau 26 giây):

```
12:14:55Z  -# 🗜️ Context compacted (auto)     ← phiên A
12:15:21Z  -# 🗜️ Context compacted (auto)     ← phiên B
12:15:24Z  "Exit 0 — tôi là người đầu tiên claim."   ← A claim job SpaceX
12:15:46Z  "Exit 0 — claim thành công."              ← B claim job ZaloPay
12:17:41Z  [post plan đầy đủ, 1200 ký tự]            ← A
12:17:48Z  [post plan đầy đủ, 846 ký tự]             ← B
12:17:50Z  "Đã post Discord. Tóm tắt tình huống..."  ← A
12:17:54Z  "Đã post. Tóm tắt tình huống..."          ← B
```

`claim-reply` **hoạt động đúng** — A claim job SpaceX, B claim job ZaloPay, không ai claim trùng.
Cơ chế anti-double-reply được thiết kế cho "cùng 1 job bị reply 2 lần"; ca này là "2 job khác
nhau, 2 phiên khác nhau, cùng 1 chủ đề" — nằm ngoài phạm vi nó bảo vệ.

Ngoài ra ~6 tin "thinking leak" (12:15:37, 12:15:57, 12:16:33, 12:17:20, 12:17:36) là suy luận
nội bộ bị đẩy ra Discord — nhân đôi vì có 2 phiên.

### Fix

**F1.1 — Batch-aware wake (repo mike, tự làm được, ưu tiên cao).**
`dispatch.sh` nhận `--batch-id <id>`; `bq_freshness_check.sh` truyền cùng một batch-id cho mọi
account trong vòng lặp. `_bg_wrapper` khi kết thúc chỉ gọi `wake_thread.sh` nếu nó là job
**cuối cùng** của batch còn chưa terminal (test-and-set nguyên tử trên file batch, cùng kiểu
khoá `claim-reply` đang dùng). ⇒ N account → **đúng 1** wake, đúng tinh thần MIKE.md §8
"fan-out → 1 lượt poll cho CẢ batch".
Fail-safe: nếu 1 job treo, job cuối terminal vẫn bắn wake (không bao giờ nuốt mất wake).

**F1.2 — CCDB session-running dedupe (repo bridge, cần restart).**
`POST /api/tasks` với `run_immediately=true`: nếu thread đó đang có phiên `running`, **không mở
phiên mới** — ghi task vào hàng đợi để phiên hiện tại nhận ở lượt kế, hoặc no-op nếu prompt
trùng. Đây là fix TỔNG QUÁT: F1.1 chỉ vá nguồn `_bg_wrapper` của mike, còn F1.2 chặn mọi nguồn
push (reconciler, cron khác, agent khác) gây double-session.

**F1.3 — Ngưng leak suy luận ra Discord.** 5-6 tin ở trên là `notify_thread.sh` gọi cho tiến độ
nội bộ. Quy tắc: progress post chỉ khi **>60 giây** kể từ post trước và phải là trạng thái
người đọc cần, không phải dòng suy nghĩ.

> ⚠️ **Không đề xuất gộp 2 account thành 1 task.** Tách per-account là hàng rào chống
> cross-account contamination (sự cố thật 2026-07-19, `kb/incidents/index.md`). Gộp lại sẽ đổi
> một lỗi hiển thị lấy một lỗi kế toán tiền — sai hướng. Fix đúng chỗ là tầng wake, không phải
> tầng dispatch.

---

## Lỗi 2 — Hai account hiểu "Trứng vàng" ngược nhau

### Cơ chế thật

Đây **không phải** hai LLM tuỳ hứng. Hai account nhận **prompt khác nhau**.

`bq_freshness_check.sh:592-606` dựng `NAV_NOTE` có điều kiện:

```bash
HAS_EXCL=...    # 'yes' nếu account có excluded_tickers
OFFBOOK_VND=... # manual_offbook_assets_vnd
if [ "$HAS_EXCL" = "yes" ] || [ "${OFFBOOK_VND:-0}" != "0" ]; then
  NAV_NOTE=" ...dùng `bin/compute_active_nav.py --account $ACCT` để lấy NAV khả dụng..."
fi
```

Trạng thái thật hôm nay (đo bằng `load_accounts()`):

| Account | `excluded_tickers` | `manual_offbook_assets_vnd` | ⇒ `NAV_NOTE` |
|---|---|---|---|
| ZaloPay | `['DGC']` | 0 | **CÓ** — được trỏ tới `compute_active_nav.py` |
| SpaceX | `[]` | 0 | **KHÔNG** — không có dòng nào |

Và `compute_active_nav.py:156,311,317` chính là nơi `egg.totalValue` lộ ra:

```
Trứng vàng (tự đọc từ egg.totalValue trong balances API): ...
ℹ️ Trứng vàng ... đã cộng vào NAV tự động — KHÔNG phải sức mua đặt lệnh ngay.
```

⇒ **ZaloPay được chỉ đường tới công cụ hiển thị egg; SpaceX không.** Kết quả trong log đúng
như vậy:

- `dispatch_DollarBill_20260820_120550.log` (ZaloPay): *"L1/L2 xác nhận đủ tiền (cash+egg
  39,17tr ≥ 25,4tr) … cần user rút egg trước phiên"* → sinh lệnh mua VPI.
- `dispatch_DollarBill_20260820_120551.log` (SpaceX): **0 lần** nhắc chữ `egg`/`Trứng vàng`.
  Chỉ *"Sức mua tức thời chỉ còn ~816 nghìn đồng… vẫn thiếu tiền"* → HOLD.

**Nghịch lý cay đắng**: câu "vẫn thiếu tiền" của SpaceX chính là **đúng cách viết mà luật ngày
08-19 vừa được thêm để dập**. `kb/context_planning_mini.md:337-341` (thêm 2026-08-19, sinh ra từ
đúng case VPI này) dạy: *"egg_value đủ bù phần thiếu → đổi cách viết lý do… đừng viết 'tài khoản
không đủ tiền'"*. ZaloPay áp luật đó **đúng**; SpaceX **không áp** — vì prompt của nó không dẫn
tới chỗ nhìn thấy egg.

Đây đúng chữ ký `coding_guidelines §22`: *hai phiên áp cùng luật ra hai kết quả khác nhau →
chuyển luật văn xuôi thành code.*

### Fix

**F2.1 — Gỡ bất đối xứng prompt (1 dòng, làm ngay).** `egg.totalValue` là dữ liệu API **live cho
mọi account**, không liên quan gì tới `excluded_tickers`/`offbook`. Tách khối egg ra khỏi điều
kiện `HAS_EXCL`, phát **vô điều kiện** cho mọi live account. Điều kiện `HAS_EXCL` chỉ nên gate
phần *active_nav vs NAV tổng* (đúng ngữ nghĩa gốc của nó).

**F2.2 — Gate cơ học "lý do thiếu tiền" (§22, §28).** Script deterministic chạy sau khi plan
được ghi (chèn vào chuỗi 19:30 L1, trước `send_plan_report`): đọc plan + `egg.totalValue` live;
nếu plan có mã bị HOLD/defer với lý do khớp `thiếu tiền|không đủ|sức mua ~0|cash ~0` **mà**
`egg_value ≥ số tiền thiếu` → **FAIL**, buộc sửa cách diễn đạt. So bằng **giá trị số**, không so
chuỗi mô tả (§28). Đây là thứ luật văn xuôi 08-19 đáng lẽ phải là ngay từ đầu.

**F2.3 — Thêm một dòng vào bảng §25 `coding_guidelines`.** Bảng "consumer nào dùng field tiền
nào" hiện có `compute_active_nav.py`, `compute_park_trim.py`, `compute_jit_unpark.py`… nhưng
**không có dòng nào cho prompt sinh plan của DollarBill** — trong khi đó cũng là một consumer
tiền. Thiếu dòng đó nên bất đối xứng trên không ai bắt được.

---

## Lỗi 3 — Vẫn lập lệnh mua VPI dù đã chốt paper-track

### Cơ chế thật

Ranh giới user chốt 2026-08-19 nằm ở `kb/current_ops.md:41-54`:

> **Ranh giới**: KHÔNG tự resume mua VPI (hay bất kỳ tín hiệu BAL mới nào ở mức tương tự) cho
> tới khi có checkpoint đánh giá rõ ràng + user xác nhận lại.

**DollarBill không bao giờ đọc file này.** `agents/DollarBill/CLAUDE.md` import đúng 3 file:

```
@kb/context_safety_core.md
@kb/context_planning_mini.md
@kb/coding_guidelines.md
```

`current_ops.md` **không** nằm trong đó. Kiểm chứng bằng grep:

| File | DollarBill đọc? | Có chữ "VPI"/"paper-track"? |
|---|---|---|
| `kb/current_ops.md` | ❌ KHÔNG | ✅ có, đầy đủ ranh giới |
| `kb/context_planning_mini.md` | ✅ CÓ | ❌ **không có ranh giới** — chỉ có luật *cách viết lý do* (dòng 342-344) |

⇒ Bản vá ngày 08-19 đã dạy DollarBill **cách GIẢI THÍCH tiền cho đúng**, nhưng **chưa bao giờ
nói với nó là ĐỪNG MUA**. Hai việc khác nhau, và chỉ việc thứ nhất được wire.

Tệ hơn: registry `kb/paper_programs_registry.json` mục `bal_signal_recent_performance` tự khai:

```json
"feature_flag": "N/A — không đổi hành vi live/paper nào;
                 bal_shadow_paper.py là script R&D độc lập,
                 không chạm plan/executor/BAL book thật"
```

Nghĩa là quyết định của user được ghi nhận như một **chương trình quan sát**, hoàn toàn **không
có cơ chế cưỡng chế** nào trên đường plan thật. Grep toàn bộ `trading_bot/*.py` + `mike/bin/*.py`
cho `blocked_signals|blocked_books|paper_only|hold_until` → **rỗng**. Không tồn tại khái niệm
"tạm giữ tín hiệu này" trong code.

`excluded_tickers` có tồn tại nhưng ngữ nghĩa khác: nó dành cho **vị thế legacy đang giữ, loại
khỏi rebalancing** (DGC), không phải "cấm MỞ MỚI theo tín hiệu tới hạn X".

### Fix

**F3.1 — Cơ chế `signal_holds` (mới, đây là fix triệt để).**
File máy đọc được `data/signal_holds.json`:

```json
[{ "scope": "ticker", "value": "VPI",
   "side": "buy", "until": "2026-09-16",
   "reason": "BAL paper-track — hiệu suất gần đây chưa đạt",
   "decided_by": "user", "decided_at": "2026-08-19",
   "ref": "paper_programs_registry:bal_signal_recent_performance" },
 { "scope": "book", "value": "BAL", "side": "buy", "until": "2026-09-16", ... }]
```

Cưỡng chế ở **hai tầng độc lập** (đúng mẫu P0/P1 đã dùng cho funding gate):
- **Tầng sinh plan**: `bq_freshness_check.sh` bơm hold đang hiệu lực vào prompt DollarBill
  nguyên văn → agent biết mà không cần suy diễn.
- **Tầng chặn cứng**: gate deterministic (kiểu `plan_funding_gate.check_plan_funding()`) chạy
  trước `send_plan_report` và lại một lần nữa trong `bot_execute.py` — có order vi phạm hold ⇒
  **loại order đó + ghi note**, không phụ thuộc LLM nhớ hay quên.

Vì sao phải là code chứ không phải thêm một đoạn văn nữa: đây là lần thứ **hai liên tiếp** cùng
một quyết định VPI bị trượt (08-19 sai cách diễn đạt → vá bằng văn xuôi; 08-20 sai hẳn hành vi
mua). Vá văn xuôi lần nữa là lặp lại đúng thứ vừa thất bại.

**F3.2 — Đồng bộ nguồn ranh giới.** Mọi ranh giới cấm/hoãn giao dịch phải nằm ở nơi **agent
thực thi thật sự đọc**. Hai việc:
- Thêm mục "Ranh giới đang hiệu lực" vào `kb/context_planning_mini.md` (file DollarBill đọc),
  sinh **tự động** từ `signal_holds.json` — không chép tay (chép tay là mốc).
- `paper_programs_registry.json`: khi `decided_by: user` và quyết định chạm hành vi mua/bán
  thật, `feature_flag: "N/A"` phải bị **cấm** — bắt buộc trỏ tới một hold entry hoặc một cờ thật.

**F3.3 — Checker ngược.** `paper_checkpoint_escalation.sh` (đã có, cron 16:10) mở rộng: mỗi
chương trình paper có `decided_by: user` mà **không** có hold tương ứng còn hiệu lực → escalate.
Bắt đúng lớp lỗi "đăng ký quan sát nhưng quên chặn".

---

## Thứ tự thi công đề xuất

| Ưu tiên | Việc | Vì sao trước | Ước lượng |
|---|---|---|---|
| **P0 — tối nay** | Xử lý lệnh VPI trong `plan_ZaloPay_2026-08-21.json` | Plan chưa duyệt nên chưa nguy hiểm, nhưng đang chờ duyệt với nội dung sai ranh giới | user quyết (A/B) |
| **P1** | F2.1 gỡ bất đối xứng prompt | 1 dòng bash, chặn ngay tái diễn sáng mai | ~15' |
| **P1** | F3.1 `signal_holds` + 2 tầng gate | Lỗi duy nhất chạm TIỀN THẬT | ~2-3h + arch-review |
| **P2** | F1.1 batch-aware wake | Lỗi hiển thị, tái diễn hằng ngày nhưng không mất tiền | ~1-2h |
| **P2** | F2.2 gate "lý do thiếu tiền" | Biến luật 08-19 thành code | ~1h |
| **P3** | F1.2 ccdb session dedupe | Cần restart ccdb → hẹn ngoài giờ | ~1h + cửa sổ restart |
| **P3** | F1.3, F2.3, F3.2, F3.3 | Chống mốc dài hạn | ~1h |

Mọi thay đổi chạm plan/executor đi qua `arch-reviewer` + `quant-skeptic` trước khi coi là wire
xong, theo chuẩn hiện hành.

## Câu cần user quyết trước khi tôi làm gì

1. **Lệnh VPI trong plan ZaloPay 2026-08-21**: gỡ ra (giữ ranh giới paper-track tới 09-16) hay
   giữ lại (override boundary)? — mặc định của tôi: **gỡ**, vì ranh giới do chính anh chốt và
   chưa tới checkpoint.
2. **Duyệt thi công P1-P3 ở trên?** Nếu gật, tôi làm P1 ngay tối nay để sáng mai không tái diễn,
   phần còn lại dispatch Wags/Taylor theo thứ tự.
