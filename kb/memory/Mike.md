# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Cập nhật lần cuối: 2026-08-16T17:09Z

## Quyết định người dùng đã ghi (không cần theo dõi thêm)
- **GDKHQ D1-D3**: Chọn (b) dry-run trace 08-17 (BID/MBB/SSI/VIX). Đã ghi bus: `decision/GDKHQ-D1-D3-pipeline-decision` (decided_by: user, 2026-08-16).
- **wakeup-miss pattern**: User chọn Option A (wait and measure, không lint tự động). Đã ghi bus: `answer/retro-pattern-recurring-wakeup-miss-2days`.

## Việc còn hở (chưa xử lý)
2. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
3. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
5. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.
6. Cân nhắc file `kb/incidents/` tổng hợp "cost-basis sai báo cáo" nếu có ca thứ 3.
7. rollup-of-agent-ownership-bug-20260816 — bug trong _same_ref khi rollup_of có sub thuộc agent
   khác; finding đã ghi bus. Chưa fix (rollup_of chưa dùng production, KHÔNG khẩn). Chờ user quyết.

## Cơ chế mới LIVE (2026-08-16) — ghi để nhớ qua restart
- **check 9b trong ops_health_check.sh**: scan `## PENDING_DECISION: <topic>` trong Mike.md,
  cảnh báo [WARN-ONLY] nếu không có bus question backing. Selfcheck PASS.
- **PENDING_DECISION protocol**: Mọi quyết định đang chờ user PHẢI được mở bus question TRƯỚC,
  rồi mới ghi vào working memory dạng: `## PENDING_DECISION: <exact-topic-trên-bus>`.
  Working memory chỉ trỏ đến topic — KHÔNG phải nơi lưu nội dung quyết định.

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill — dùng cho MỌI prompt dispatch có backtick/code snippet.
- CASH_VENDOR gate: giữ ĐÓNG (user duyệt 08-15), mở lại chỉ khi >=1 sự kiện ISS/hỗn hợp VÀ qua
  2026-09-13. commit dce25180.
- CAPIT margin: `enabled=false`. Pilot = canary 100cp đầu tiên trong chính phiên CAPIT signal thật
  (đã discuss 08-11), KHÔNG đặt lệnh ngẫu nhiên để test. Chờ signal thật.

## 2026-08-16 — sự kiện quan trọng
- cron_health_check false-alarm root-cause XONG (commit f3863f54/a6516c7e + coding_guidelines §29).
- Bus backlog 10→2 pending qua 4 vòng arch-review (d65167a9/8e9affc3/522e29d2/517261ac).
- Wags_20260816_111706 tự đóng 7 câu hỏi thật.
