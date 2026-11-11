# 2026-11-11 — Newline trong `approved_by` ⇒ preflight SpaceX RED giả + decision duyệt plan không lên bus

**Phát hiện:** check 5b `ops_health_check.sh --account ZaloPay` (01:20Z) báo 2 bản ghi cách ly; job `Winston_20261111_012010`.

| idx | agent | nguyên nhân THẬT | kết quả |
|---|---|---|---|
| 30 | Taylor | JSON viết tay thừa 1 `}` (đóng sớm trước `measured_by`) | tự retry +11s cùng topic, nội dung khớp ⇒ không mất |
| 31 | Mike | `approve_plan_simple.sh:163` dựng JSON bằng nối chuỗi; `APPROVED_BY` = `"user\n\n(John) …"` ⇒ `Invalid control character` | **KHÔNG retry** ⇒ decision `plan-approval-SpaceX-2026-11-11` mất khỏi bus |

**Hệ quả thứ hai (live, trước giờ mở cửa):** cùng text có newline được ghi vào `plan_SpaceX_2026-11-11.json.approved_by`.
`preflight_check.sh` in kết quả 1 dòng rồi `IFS='|' read` ⇒ newline cắt cụt ⇒ `_flags` rỗng ≠ `OK` ⇒
**RED giả** 01:20:17Z (`❌ Plan SpaceX:  — orders= approved=user mafee=`). Cổng thật của bot
(`trading_bot/plan.py approval_block_reason`) chỉ cần `approved_by.strip()` khác rỗng ⇒ bot KHÔNG bị chặn.

**Sửa:** (1) `preflight_check.sh` làm phẳng `approved` (whitespace→space, `|`→`/`) CHỈ khi in, sau khi đã xét hợp lệ trên giá trị gốc.
(2) `approve_plan_simple.sh` dựng payload bằng `json.dumps` (test với newline + `"` + `\`). (3) Ghi lại decision: Winston `6a429698` (relayed).
Không đụng plan file (ranh giới cấm).

**Verify:** preflight chạy lại 01:21Z: SpaceX GREEN, ZaloPay GREEN. Shellcheck không tăng cảnh báo so HEAD.

**Bài học:** text tự do của người (duyệt, ghi chú) đi qua kênh 1-dòng (bash `read`, JSON nối chuỗi) phải được serialize/làm phẳng ở biên, không tin người gõ không xuống dòng.
