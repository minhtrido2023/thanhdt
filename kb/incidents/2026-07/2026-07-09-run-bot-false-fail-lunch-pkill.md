---
kind: incident
date: 2026-07-09
topic: run-bot-false-fail-lunch-pkill
title: >-
  2026-07-09 — run_bot fail-branch báo ❌ giả + dispatch ops_autofix khi cron lunch-pkill 11:30 dừng bot theo lịch (rc=143)
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-09 — run_bot fail-branch báo ❌ giả + dispatch ops_autofix khi cron lunch-pkill 11:30 dừng bot theo lịch (rc=143)

**Hiện tượng:** 11:30 ICT, run_bot ZaloPay "thoát rc=143 sau 145 phút" → Discord báo
"❌ Bot gặp lỗi và dừng" + bus event `error/bot-fail` + tự dispatch ops_autofix
(job `Winston_20260709_043002`). Thực tế bot khoẻ hoàn toàn: journal cho thấy làm
việc liên tục tới 11:29:44 (3 FILL sáng: TCM 300+2000 @19.950, VCB 700 @61.400; phần
TCM còn lại WAIT_QUOTA), rồi bị cron `pkill` nghỉ trưa (crontab dòng 59, chạy từ
2026-07-06) giết đúng thiết kế — SIGTERM = rc=143.

**Root cause:** fail-branch của `run_bot.sh` (wire ops_autofix 2026-07-08) coi MỌI
rc≠0 là lỗi, không phân biệt SIGTERM từ lunch-pkill theo lịch. Hôm nay là ngày đầu
lộ bug: các ngày trước bot khớp xong plan thoát rc=0 trước 11:30 (hoặc plan 0 lệnh
thoát ngay), chưa lần nào còn sống tới lúc pkill.

**Fix (`run_bot.sh`):** thêm nhánh trước fail-branch — rc=143 VÀ giờ kết thúc trong
cửa sổ 11:25–12:59 ICT → Discord "⏸️ tạm dừng nghỉ trưa theo lịch, quay lại 13:00" +
bus `status/bot-lunch-stop`, KHÔNG dispatch ops_autofix, KHÔNG event error. rc=143
ngoài cửa sổ trưa (kill tay/BOT_STOP bất thường) vẫn vào nhánh fail như cũ.

**Verify:** sandbox stub (bot giả `exit 143`, notify/bus/autofix stub echo) chạy lúc
11:35 ICT thật → vào đúng nhánh ⏸️, không dispatch autofix; stub rc=2 → vẫn vào nhánh
❌ + autofix như cũ. Test biên cửa sổ: 11:24→fail, 11:25/12:59→lunch, 13:00→fail.

**Ghi chú cùng phiên (KHÔNG phải sự cố):** journal có `GHOST_ORDER TCM 10:22:36` —
đó là ghost guard bắt ĐÚNG lệnh test tay của user (id=172621, bán 10cp TCM lẻ
@20.000, đặt qua app trong vụ điều tra odd-lot ở entry trên) → TCM pause hết phiên
sáng theo thiết kế human-in-the-loop. Phiên chiều 13:00 bot restart với fix odd-lot
`f7f9f52`; chừng nào lệnh tay 172621 còn mở, guard tiếp tục pause TCM (tránh double-
sell 10cp — fail-safe đúng); lệnh tay khớp/hủy xong thì guard tự nhả, bot tự bán nốt
10cp lẻ bằng code mới nếu còn.

**Cập nhật 2026-07-28 (lần đầu nhánh fail rc=143-ngoài-trưa bắn thật — BENIGN):**
run_bot SpaceX plan 2026-07-28 "thoát rc=143 sau 114 phút" (09:05→10:59) → tự dispatch
ops_autofix (job `Winston_20260728_035952`). Điều tra: rc=143 KHÔNG phải crash — một
**phiên Claude interactive** (`ppid 1192926`, shell-snapshot) chạy tay `kill 3125444`
(chính là run_bot cron 09:05) rồi `nohup run_bot.sh --account SpaceX restart` lúc
10:59:52. Vì 10:59 NGOÀI cửa sổ trưa 11:25–12:59 → fail-branch coi là bất thường và
dispatch ops_autofix — **đúng thiết kế** (entry 2026-07-09 cố ý giữ nhánh này cho
"kill tay/BOT_STOP bất thường"). Bot hồi phục sạch: state file idempotent, resume
WAIT_QUOTA liền mạch (10:59:54, 11:00:14…), KHÔNG đặt trùng (vẫn đúng 2 child
35091/57151 status=closed filled=0 released=True, parent done=False). **0 fill, 0 rủi
ro vốn, không BOT_STOP.** WAIT_QUOTA của TV1 là throttle thanh khoản THẬT (ratio
38.46%≥1%ADV, cap tham gia 10% KLGD — TV1 mỏng, chưa đủ volume để 1 slice khớp trong
cap), KHÔNG phải bug round_lot (qty 300 = lô chẵn; bug đó đã fix `f7f9f52`).
**Bài học triage:** rc=143 + có run_bot mới sống lại trong vài giây + parent `ppid` là
claude shell-snapshot = restart tay lành, không cần điều tra sâu. Cost-note: mỗi lần
restart tay run_bot ngoài giờ trưa vẫn nuốt trọn 1 phiên ops_autofix (Opus) —
cân nhắc mở rộng nhánh benign của run_bot.sh nếu tái diễn (chưa sửa: rủi ro che mất
kill bất thường thật; giữ nguyên hành vi hiện tại).
