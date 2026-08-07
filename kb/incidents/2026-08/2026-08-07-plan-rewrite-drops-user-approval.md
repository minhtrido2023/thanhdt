# 2026-08-07 — Script sửa plan sau khi user đã duyệt LÀM MẤT `approved_by` → bot chặn cả 2 account giữa phiên chiều

**Hiện tượng.** `run_bot.sh` cron phiên chiều 13:00 ICT thoát `rc=2` cho CẢ ZaloPay và SpaceX:
`APPROVAL_GATE_BLOCK — requires_user_approval=true nhưng approved_by trống`. Không lệnh nào được
đặt, không lệnh kẹt (journal `exec_ZaloPay_2026-08-07` chưa tồn tại, chỉ có file `.lock` rỗng),
BOT_STOP clear.

**Root cause — REGRESSION DE-APPROVAL (bằng chứng file, không suy đoán).**

| Thời điểm (ICT) | Sự kiện |
|---|---|
| 12:36:53 | User (John) duyệt THẬT cả 2 plan — bus `decision` `plan-approval-with-jit-{SpaceX,ZaloPay}-2026-08-07`, `decided_by=user` |
| 12:45, 12:51 | `preflight_check.sh` GREEN, `approved=user (John) - Discord, duyet mua DRI + ban PARK JIT tai tro` |
| 12:47 | Wags báo `error`: plan chứa bug BÁN TRÙNG LÔ JIT_UNPARK (1.200cp SpaceX + 400cp ZaloPay) |
| 12:49 | Job `DollarBill_20260807_054858` backup plan → `agents/DollarBill/backup_20260807/*.bak_dup` |
| **12:52** | **Job đó GHI ĐÈ plan để gỡ 4 lệnh trùng — và reset `approved_by`/`approved_at` về `None`** |
| 13:00 | Cron chiều chạy → approval gate chặn ĐÚNG THIẾT KẾ → `rc=2` |

Đối chiếu backup 12:49 vs plan hiện tại 12:52 (ZaloPay):
- BAK: `approved_by='user (John) - Discord…'`, `approved_at='2026-08-07T12:36:53+07:00'`, 13 lệnh.
- CUR: `approved_by=None`, `approved_at=None`, 9 lệnh.
- Diff lệnh: CUR = BAK **trừ đúng 4 lệnh L2 JIT bán trùng lô** (BID/MBB/VCB/VHM). 9 lệnh còn lại
  (8 BÁN PARK + 1 MUA DRI) **giống hệt** bản đã duyệt → là TẬP CON thật sự của phạm vi duyệt.

**Không phải bug của gate.** Approval gate (`trading_bot/plan.py::approval_block_reason`) chặn
đúng — đây là fail-safe hoạt động như thiết kế, KHÔNG phải RED giả kiểu `MAFEE_NOT_AUTH` (07-06 /
07-15). Bug nằm ở **script ghi đè plan không bảo toàn trường approval**. Script gây lỗi là đoạn
python inline trong phiên DollarBill (không có file `.py` nào mtime 12:49–12:52) → không có
artifact bền để vá.

**Xử lý.** Winston KHÔNG tự ghi `approved_by` (vùng CẤM: sửa trade plan). Escalate:
bus `question` `ops-autofix-unresolved: run-bot-fail-ZaloPay-2026-08-07` (trace
`Winston_20260807_060009`) + notify `trading_daily` và `plan_approval`, deadline 14:30 ICT.
Câu hỏi cho user: bản 9 lệnh (đã gỡ 4 lệnh trùng) có còn trong phạm vi duyệt 12:36 không.

⚠️ Lưu ý an toàn đã ghi rõ khi escalate: **autoheal retry mỗi 5 phút** — vừa stamp `approved_by`
là lệnh chạy THẬT trong ≤5 phút, đang giờ giao dịch.

## Lỗ hổng lớn hơn phát hiện kèm — chiều NGƯỢC LẠI fail UNSAFE (chưa vá, cần quyết định)

Hôm nay fail **SAFE** (mất duyệt → bot từ chối). Chiều ngược lại fail **UNSAFE** và hiện **không
có cơ chế nào bắt**: nếu một script sửa `orders[]` sau khi user duyệt mà **GIỮ NGUYÊN**
`approved_by`, bot sẽ thực thi những lệnh user chưa bao giờ nhìn thấy.

- `approval_block_reason` (plan.py:1790) chỉ kiểm tra `approved_by` **có trống hay không**.
- `preflight_check.sh:101` cũng chỉ `if not approved`.
- **Không chỗ nào so nội dung plan với nội dung ĐÃ ĐƯỢC DUYỆT.**

**Cố ý KHÔNG tự vá trong job này**, vì:
1. Check ngây thơ `mtime > approved_at` sẽ tạo **RED giả**: có pattern thật ghi field
   display-only vào plan sau khi duyệt (vd `park_trim_proposal`, job Taylor hôm nay) — đúng cái
   bẫy "fail-flag trên field không phản ánh gate thật" của incident 07-15.
2. Bản đúng phải hash **riêng `orders[]`** và ghim `approved_orders_hash` lúc duyệt → cần sửa
   **writer của luồng duyệt plan** + gate executor = vùng CẤM của Winston.

**Đề xuất (cần user/Wags/Taylor quyết):** lúc ghi `approved_by`, ghim thêm
`approved_orders_hash` = hash canonical của riêng `orders[]`; gate executor từ chối khi hash
hiện tại ≠ hash đã duyệt, thông báo rõ "plan đã bị sửa sau khi duyệt". Cho phép sửa field
display-only mà không phá duyệt, nhưng mọi thay đổi LỆNH đều phải duyệt lại.

**Bài học.** Bất kỳ script nào sửa plan **sau khi đã duyệt** phải hoặc (a) bảo toàn
`approved_by`/`approved_at` khi chỉ gỡ/không đổi lệnh, hoặc (b) xoá duyệt **và báo ngay cho
người duyệt** rằng duyệt đã bị vô hiệu hoá — chứ không im lặng reset rồi để cron phát hiện.
