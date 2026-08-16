# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Cập nhật lần cuối: 2026-08-16T17:45Z (dọn cuối ngày sau daily retro bước 3/3)

## Việc còn hở (chưa xử lý)
1. Selfcheck-masking E5 capit_lever — chưa xác nhận đã vá hay chỉ mới ĐO.
2. plan-dd-check-string fix (commit 9a9dbb1) — chờ xác nhận phiên LIVE 08-17.
3. EOD daily report chưa bao giờ gửi email — hỏi user có wire không.
4. Cân nhắc file `kb/incidents/` tổng hợp "cost-basis sai báo cáo" nếu có ca thứ 3.
5. **rollup-of-agent-ownership-bug-20260816** — bug trong `_same_ref` khi `rollup_of` có sub
   thuộc agent khác; finding đã ghi bus. CHƯA fix (`rollup_of` chưa dùng production, KHÔNG khẩn).
   Chờ user quyết fix-now-vs-defer. Bối cảnh: cơ chế này đã bị bắt 3 bug riêng trong <48h mà chưa
   từng dùng thật lần nào (retro-2026-08-16) — đáng cân nhắc PENDING_DECISION hoãn dùng.
6. **Pattern B rộng hơn §28** (retro-2026-08-16) — "fix chỉ dập đúng hình dạng lỗi đã thấy, chưa
   tổng quát hoá cho cả họ" vẫn tái diễn ở các bug KHÔNG thuộc dạng so-2-nguồn (vd
   `wags_verdict_parse.py` delimiter tự-trích-dẫn, `bus/_rejected.jsonl` 2 bug tự thân). §28 chỉ
   phủ nhánh so-2-nguồn. Chưa mở escalation mới (tránh lặp lỗi #5 hôm nay — mở trùng escalation) —
   để retro-08-17 xác nhận có tiếp diễn không rồi mới quyết có escalate hay không.

## Cơ chế mới LIVE (2026-08-16) — ghi để nhớ qua restart
- **check 9b trong ops_health_check.sh**: scan `## PENDING_DECISION: <topic>` trong Mike.md,
  cảnh báo [WARN-ONLY] nếu không có bus question backing. Selfcheck PASS.
- **PENDING_DECISION protocol**: Mọi quyết định đang chờ user PHẢI được mở bus question TRƯỚC,
  rồi mới ghi vào working memory dạng: `## PENDING_DECISION: <exact-topic-trên-bus>`.
  Working memory chỉ trỏ đến topic — KHÔNG phải nơi lưu nội dung quyết định.
- **`daily_retro.sh` bước 3** giờ tự đọc `bus/inbox/Mike.jsonl` từ mốc bắt đầu chạy để liệt kê
  escalation đã mở ở bước 1 — tránh mở trùng câu hỏi (fix sự cố #5 retro-08-16).

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill — dùng cho MỌI prompt dispatch có backtick/code snippet.
- CASH_VENDOR gate: giữ ĐÓNG (user duyệt 08-15), mở lại chỉ khi >=1 sự kiện ISS/hỗn hợp VÀ qua
  2026-09-13. commit dce25180.
- CAPIT margin: `enabled=false`. Pilot = canary 100cp đầu tiên trong chính phiên CAPIT signal thật
  (đã discuss 08-11), KHÔNG đặt lệnh ngẫu nhiên để test. Chờ signal thật.
- GDKHQ D1-D3: dry-run trace 08-17 (BID/MBB/SSI/VIX) — theo dõi kết quả dry-run ngày mai.

## 2026-08-16 — đã đóng trong ngày (không cần theo dõi thêm)
- Daily retro 2026-08-16 hoàn tất 3/3 bước, entry `kb/incidents/retro/retro-2026-08-16.md` —
  6 sự cố, Wags verify GAPS FOUND (2 gap: sự cố bỏ sót + status escalation stale), đã sửa xong.
- cron_health_check false-alarm root-cause XONG (commit f3863f54/a6516c7e + coding_guidelines §29).
- Bus backlog 10→~2 pending qua nhiều vòng arch-review (d65167a9/8e9affc3/522e29d2/517261ac).
- `selfcheck-red: send_plan_report_park_jit_selfcheck.py` fixed (commit 4cb89353), arch-review
  CONFIRMED.
- Pattern B escalation gốc (`retro-pattern-recurring-patternB-checker-wrong-representation`)
  xác nhận ĐÃ ĐÓNG 2026-08-14 với Prevention = coding_guidelines §28 (chỉ phủ nhánh so-2-nguồn,
  xem mục "Việc còn hở" #6 ở trên cho phần còn thiếu).

