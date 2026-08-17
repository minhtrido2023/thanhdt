# Cài chuỗi cron PARK-merge: L1 19:30 → L2 19:40 → merge 20:20 ICT

**Job** `Taylor_20260814_142151` · 2026-08-14 · Taylor · thực thi §6 của
[`park_merge_wire_20260811.md`](park_merge_wire_20260811.md) sau khi user (John) duyệt.
**Commit**: `f44b5e23` (3 wrapper `.sh` + backup crontab) + `3a807740` (2 file `kb/`, xem §6) +
`8ea1c50f` (đính chính quy chiếu commit).
**quant-skeptic**: **CONFIRMED (`high`)** — tự chạy lại cả 4 selfcheck, tự đọc `crontab -l`, tự đo
lại mtime artifact; bắt được 1 sai sót cosmetic đã vá (§6).

---

## 1. Kết luận ngắn

| Việc | Kết quả |
|---|---|
| 3 mục treo #1/#3/#6 có chặn không? | **KHÔNG** — cả 3 vẫn nguyên trạng như 08-11, đo lại bằng `grep` (§2) |
| 3 dòng crontab | **ĐÃ CÀI** — `30 12` / `40 12` / `20 13` (UTC) = 19:30 / 19:40 / 20:20 ICT, T2-T6 |
| `kb/cron_registry.md` + `CHANGELOG.md` | ĐÃ cập nhật, 4 câu hỏi §11 cho cả 3 script |
| Test end-to-end trên dữ liệu SỐNG hôm nay | **CÓ** — sandbox, 0 file production bị đụng (§4) |
| quant-skeptic verify việc CÀI CRON (khác vòng verify code 08-11) | CONFIRMED `high` |

---

## 2. Ba mục treo — xác nhận lại, không mục nào chặn

| # | Việc | Trạng thái 2026-08-14 | Bằng chứng |
|---|---|---|---|
| 1 | `send_plan_report.sh` hiển thị TRÙNG | **vẫn chưa làm** | `grep -E "_merged_into_orders\|merged_from\|merge_owner" mike/bin/send_plan_report.sh` = **0 hit** |
| 3 | Bản vá kế toán PARTIAL | **vẫn chưa áp** | `grep -c reconcile_partial`: prod `compute_park_trim.py` = **0**, `merge_park_orders.py` = 5 ⇒ nhánh PARTIAL của merge nằm im |
| 6 | Hợp đồng namespace `jit_*` | **vẫn chưa ghi** | `grep -rn jit_unpark_note` = chỉ `merge_park_orders.py` + selfcheck của chính nó ⇒ 0 consumer thật |

Mục #1 nay **hiển thị mỗi ngày** thay vì thi thoảng (merge chạy hằng phiên) — vẫn là lỗi trình
bày, không phải lỗi tiền; nhưng nên đẩy lên ưu tiên cao hơn so với lúc 08-11.

## 3. Cái ĐÃ ĐỔI từ 08-11 — 4 điều, không điều nào bác kết luận cũ

1. **L1 chạy hằng ngày rồi, nhưng BẰNG TAY.** `park_trim_<acct>_<T+1>.json` sinh đều ~19:04 ICT mọi
   phiên từ 08-11, cả 2 account — do dispatch EOD của DollarBill, không phải cron (`grep` toàn repo:
   0 script/cron gọi `compute_park_trim`). Đúng như §6 mô tả.
2. **L2 KHÔNG chạy từ 08-11.** `jit_unpark_*.json` mới nhất là `2026-08-11` ⇒ merge hôm nay luôn
   REFUSED vì thiếu artifact L2 — đúng nhánh fail-closed của bản vá 4b.
3. **Plan T+1 KHÔNG luôn được ghi trước 19:40.** Đo mtime 08-05→08-14: **2/5 phiên ghi SAU 21:00**
   (08-11 lúc 23:25; 08-13 lúc 21:31). Những ngày đó L2 no-op fail-closed ⇒ merge REFUSED ⇒ plan
   nguyên vẹn. **An toàn nhưng chuỗi không giao gì.** Đây là khiếm khuyết có sẵn của khâu DollarBill,
   KHÔNG phải hồi quy do 3 dòng cron này — nhưng nó đặt trần lên giá trị thực tế của chuỗi, phải
   nói ra thay vì để người đọc tưởng chuỗi chạy đủ 5/5 phiên.
4. **BID: sổ lô lệch broker, phát hiện đúng tối nay.** Xem §7.

## 4. Kiểm chứng

| Bộ | Kết quả |
|---|---|
| ShellCheck 0.11.0, 3 file mới | **0 finding**; pre-commit gate PASS lúc commit thật |
| `merge_park_orders_selfcheck.py` | 120/120 |
| `compute_park_trim_selfcheck.py` | 63 PASS / 0 FAIL |
| `compute_jit_unpark_selfcheck.py` | PASS + ma trận TZ digest đồng nhất |
| `approve_plan_with_jit_selfcheck.py` | 27/27 |
| `preflight_order_invariants_selfcheck.py` | 16/16 |
| **E2E dữ liệu SỐNG** | sandbox `PARK_CHAIN_PLAN_DIR=/tmp/park_chain_test_20260814` (bản sao plan 08-17 thật). L1+L2 gọi DNSE thật 21:30-21:31 ICT. **dry-run ⇒ plan y hệt TỪNG BYTE** (md5 không đổi). **`--write` ⇒ `orders[]` KHÔNG đổi** (giữ 1 lệnh mua TV1 SpaceX, 0 lệnh ZaloPay), `approved_by=None`, `requires_user_approval=True`; chỉ thêm khoá `merge_park_orders` + làm mới 2 khối proposal. **0 file production bị đụng.** |
| Chứng minh ngược guard giờ/ngày | trích NGUYÊN VĂN đoạn guard từ `park_trim_daily.sh` bằng `sed`, chạy với đồng hồ giả: 14:59→`BEFORE_1500_ICT` · 15:00→`2026-08-17` · T7 08-15→`NOT_TRADING_DAY` · 02-09 Quốc khánh→`NOT_TRADING_DAY` · T5 08-13 20:00→`2026-08-14` |
| Chứng minh ngược fail-closed L2 | sandbox thiếu artifact L1 ⇒ rc=1, **0 artifact sinh ra**; sandbox thiếu plan T+1 ⇒ rc=1, 0 artifact |
| Ma trận TZ | `park_trim_daily.sh` chạy thật dưới `{env -u TZ, TZ=America/New_York, TZ=UTC, env -i}` = **4/4** cùng `plan_date` + cùng đồng hồ ICT. **Phép thử có sức phân biệt**: system TZ = `Etc/UTC`, lúc chạy UTC-hour = 14 (<15) ⇒ guard không neo ICT sẽ TỪ CHỐI chạy |

## 5. Quyết định thiết kế đáng ghi

- **KHÔNG dùng `for_each_live_account.sh`.** Wrapper đó chỉ biết nối `--account <label>` + extra
  args CỐ ĐỊNH; 3 script này cần tham số **per-account-per-date** (`--out park_trim_<acct>_<T+1>.json`,
  `--plan-date <T+1>`). Dùng khuôn TỰ LẶP `live_dnse_labels()` của `inject_discretionary_orders.sh`
  (20:30) và `compute_active_nav_all.sh` (20:15) — cùng một pattern đã ổn định, thêm account mới
  vẫn tự có.
- **Ràng buộc "sau 15:00 ICT" cưỡng chế BẰNG CODE**, không chỉ bằng giờ cron: giờ cron một mình
  không chặn được chạy tay, sửa giờ, hay đổi TZ. `now_ict()` của `trading_bot.vn_market` tự neo ICT
  (§16). `NOT_TRADING_DAY` ⇒ exit **0** (skip sạch, không làm nhiễu `cron_health_check`);
  `BEFORE_1500_ICT` ⇒ exit **1** (nghĩa là cron bị cấu hình sai — phải nhìn thấy).
- **`--plan` PHẢI truyền tường minh cho L2**: mặc định của `compute_jit_unpark.py` là
  `plan_<acct>_<asof>.json` với `asof` = **HÔM NAY**, tức plan ĐÃ thực thi xong, không phải plan T+1.
  Bẫy thật nếu ai sau này "dọn" cờ này đi.
- **`--write` nằm ở DÒNG CRON, không nằm trong script**: `merge_park_orders.py` mặc định dry-run,
  nên chạy tay `merge_park_daily.sh` (không tham số) = phiên shadow an toàn — đúng ý §9 report cũ.
- **Cron của repo này viết theo UTC, không phải ICT.** Crontab có dòng `TZ=Asia/Ho_Chi_Minh` nhưng
  Vixie cron chỉ export biến đó vào **môi trường job**, không dùng để diễn giải lịch; system TZ =
  `Etc/UTC`. Mọi dòng hiện có đều UTC (vd `send_plan_report` 21:00 ICT = `0 14`). 3 dòng mới theo
  đúng quy ước.

## 6. Sai sót quant-skeptic bắt được — đã vá (`8ea1c50f`)

Finding + commit message nói *"kb/ cập nhật CÙNG COMMIT `f44b5e23`"*. Thực tế 2 file `kb/` đi theo
commit `consolidate` **`3a807740`** landed **14 giây TRƯỚC** — `consolidate.sh` chạy tự động ngay
sau `append_event.sh` và commit TOÀN BỘ `kb/`, nên tới lượt `git commit` của job thì 2 path đó
không còn gì để stage. Nội dung khớp đúng ý định §11 (cùng job, cùng phút, đều trên `master`),
nhưng ai truy vết bằng MỘT hash sẽ hụt.

**Bài học tổng quát cho mọi job cron/registry sau này** (đã ghi vào `kb/cron_registry/CHANGELOG.md`):
ở repo `mike`, hễ job gọi `append_event.sh` TRƯỚC `git commit` thì file `kb/` gần như chắc chắn đi
theo commit của consolidator. Muốn "cùng commit" theo nghĩa đen ⇒ commit `kb/` **trước** khi ghi
bus; không thì phải khai cả hai hash.

## 7. Việc chuyển cho người khác (không chặn, đã escalate)

- **BID sổ lô lệch broker** — bus `question` `BID-lot-ledger-lech-broker` + dispatch Winston.
  SpaceX BID ledger 1.100 vs broker **1.175** (+75cp); ZaloPay 400 vs **427** (+27cp), cùng tỷ lệ
  ~6,8% ⇒ rất giống CP thưởng/quyền BID vừa được ghi có. **Lúc 19:04 cùng ngày artifact production
  còn `NO_TRIM` với pool đầy đủ** ⇒ broker ghi có trong khoảng 19:04-21:30 ICT. Hệ quả: chuỗi cron
  sẽ CHẠY nhưng KHÔNG sinh lệnh nào (L1/L2 fail-closed) tới khi sổ lô được cập nhật — an toàn,
  vô ích. Cần kiểm cả việc `corp_action_daily.sh` 07:30 có bắt được sự kiện này không.
- **`shellcheck_gate.sh` FAIL-OPEN khi thiếu `shellcheck` trong PATH** (dòng 48-50: `command -v
  shellcheck` thất bại ⇒ `exit 0`). Cron có `/home/trido/.local/bin` trong PATH nên thực tế không
  hở, nhưng đây là lớp lỗi im lặng — đề xuất Wags/Mike xem. Không chặn việc này.
- 3 mục #1/#3/#6 ở §2 — vẫn thuộc file người khác / chờ duyệt.

## 8. Rollback

```bash
crontab -l | grep -v park_trim_daily.sh | grep -v jit_unpark_daily.sh \
           | grep -v merge_park_daily.sh | crontab -
```
Bản crontab trước khi đổi: `agents/Taylor/research/crontab_backup_20260814_before_park_chain.txt`
(113 dòng; sau khi cài = 121 dòng, `diff` xác nhận **0 dòng bị xoá**).
