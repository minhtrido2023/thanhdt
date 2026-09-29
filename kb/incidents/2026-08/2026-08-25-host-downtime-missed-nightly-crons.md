# 2026-08-25 — retro 2026-08-24 mất vì HOST TẮT ~18 tiếng, không phải bug script

**Triệu chứng.** ops_health_check (run account=ZaloPay) flag: thiếu
`kb/incidents/retro/retro-2026-08-24.md`, kèm chẩn đoán ĐÃ VIẾT SẴN trong thông điệp —
"nghi cron 00:30 ICT đêm qua crash/không hoàn tất, đúng lớp lỗi 08-01: quoting bug".

**Chẩn đoán — sai cả 2 giả thuyết được gợi ý (08-01 quoting, 08-20 transport).** `daily_retro.sh`
không chạy, không chết, không log gì cả. Máy TẮT.

Bằng chứng:

```
$ tail logs/daily_retro.log
[2026-08-24T00:38:47+0700] === daily_retro DONE ...        # lần chạy CUỐI, review 08-23
                                                            # KHÔNG có dòng START nào cho 08-24

$ last -x | head
reboot   system boot   Tue Aug 25 09:45   still running
trido    pts/11        Mon Aug 24 13:50 - 13:57

$ find mike/logs -newermt "2026-08-24 16:00" ! -newermt "2026-08-25 09:45"
(rỗng — KHÔNG file log nào được ghi trong cả cửa sổ)
```

Ghi log cuối cùng trước khi tắt: `logs/papertrade_daily.log` 2026-08-24 15:30 ICT. Ghi đầu
tiên sau khi bật: `logs/daily_refresh_recovery_20260825.log` 2026-08-25 10:12 ICT.
⇒ **host down ~2026-08-24 15:30 → 2026-08-25 09:45 ICT (≈18 tiếng)**, cron 00:30 chưa từng fire.

**Phạm vi thật rộng hơn retro — CẢ LOẠT cron đêm bị bỏ lỡ.** Sáng nay đã có recovery thủ công cho
`daily_refresh`, `sync_bq_cache`, `paper_report`. Nhưng tính tới 12:45 ICT vẫn CHƯA chạy bù (mtime
log còn đứng ở 08-24): `kb_nightly.sh` (02:05 08-24), `corp_action_daily.sh` (07:32 08-24),
`check_report_cadence.sh` (08:30 08-24). Winston đã chạy bù `corp_action_daily.sh` (thuộc remit
data-ops, hôm nay 08-25 là phiên giao dịch nên quét corp-action không được thiếu); 2 cái còn lại
để Mike/user quyết vì chạm KB + kênh gửi báo cáo.

**Lỗi thiết kế thật sự: checker ĐOÁN nguyên nhân và viết thẳng phán đoán vào cảnh báo.**
Thông điệp check#9 hardcode "nghi quoting bug 08-01" từ 2026-08-01. Nó đã dẫn ops-autofix đi sai
hướng **hai lần liên tiếp**:
- 2026-08-20 → thật ra là lỗi TRUYỀN TẢI API (script chạy trọn vẹn, abort có kiểm soát).
- 2026-08-25 (ca này) → thật ra host tắt, script chưa từng chạy.

Đây đúng chữ ký `coding_guidelines §28`: suy nguyên nhân từ **sự vắng mặt** của một artifact
(file retro không có) thay vì tra artifact xác nhận (log có dòng START không).

**Đã sửa (commit `52eb62ea`).** check#9 giờ đọc `logs/daily_retro.log` và phân đúng 3 nhánh, mỗi
nhánh chỉ tới đúng chỗ cần nhìn:

| Log có `START (reviewing <ngày>` | Kết luận in ra |
|---|---|
| CÓ | script ĐÃ chạy nhưng không hoàn tất ⇒ đọc `daily_retro_draft_*.log`, phân lớp usage-limit / transport / lạc đề |
| KHÔNG | cron **KHÔNG hề chạy** (máy tắt / cron không fire) — xác nhận bằng `last -x` + mtime `mike/logs/`, **đừng đi tìm bug trong script**; mọi cron khác cùng cửa sổ cũng đã bị bỏ lỡ |
| không đọc được log | khai **KHÔNG BIẾT**, kiểm thủ công |

+3 ca hồi quy trong `ops_health_check_selfcheck.py` khoá cả 3 nhánh; toàn bộ selfcheck PASS dưới
4 TZ (UTC / ICT / Sydney / New_York).

**Bài học.** Cảnh báo được phép nói *cái gì thiếu*; nó chỉ được nói *tại sao thiếu* khi đã tra một
artifact phân biệt được các giả thuyết. Một câu "nghi ..." viết cứng trong checker sống lâu hơn
sự cố sinh ra nó, và mỗi ngày nó tồn tại là một lần nó có thể dẫn người xử lý đi sai đường.

**Còn hở (không sửa trong ca này — chạm crontab, ngoài quyền autofix):** không có cơ chế
`@reboot` catch-up nào cho các cron đêm của fleet. Sau mỗi lần downtime, việc phát hiện + chạy bù
hoàn toàn thủ công, và chỉ những pipeline có checker riêng mới được phát hiện. Đề xuất để user
quyết: một `@reboot` script so mtime log với lịch cron và báo danh sách job đã bị bỏ lỡ.
