---
kind: incident
date: 2026-07-11
topic: fa-ratings-8l-silent-write-failure
title: >-
  2026-07-11 — fa_ratings_8l weekly-refresh wrapper bắt đúng 1 lần BQ write "thành công giả" (silent write failure) khi test tay bằng identity read-only — hoạt động ĐÚNG thiết kế, nhưng identity của cron THẬT vẫn chưa xác nhận
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-11 — fa_ratings_8l weekly-refresh wrapper bắt đúng 1 lần BQ write "thành công giả" (silent write failure) khi test tay bằng identity read-only — hoạt động ĐÚNG thiết kế, nhưng identity của cron THẬT vẫn chưa xác nhận

**Bối cảnh:** trong lúc chuẩn bị cron weekly refresh `fa_ratings_8l` (đề xuất Winston job
`Winston_20260711_104135`, user duyệt cùng ngày), Mike chạy tay `bin/refresh_fa_ratings_8l.sh`
để kiểm tra script trước khi commit. Script gọi `rating_8l_history.py` — hàm
`refresh_bq_table()` trong file đó chạy mọi `bq` subprocess với `capture_output=True` và
**không hề check returncode**, nên in ra dòng "refreshed BQ table tav2_bq.fa_ratings_8l"
ngay cả khi lệnh `bq load`/`CREATE OR REPLACE` thất bại thật (permission denied vì phiên
Mike dùng service account **read-only** `bq-reader-8l`).

**Vì sao KHÔNG bị lừa:** `refresh_fa_ratings_8l.sh` được thiết kế đúng nguyên tắc MIKE.md
#2 ("trust the artifact, not the self-report") — sau khi gọi python, wrapper tự `bq show`
lại chính bảng `tav2_bq.fa_ratings_8l`, so `lastModifiedTime` với `START_EPOCH` của chính
lần chạy này. Bảng KHÔNG hề nhích (`lastModified` vẫn là 2026-06-20, cũ hơn giờ chạy) →
wrapper tự kết luận `FAIL_REASON` đúng, bắn `bin/append_event.sh Winston error
fa_ratings_8l-refresh-failed` (bus event `73a3d13a…`, 2026-07-11T11:32:31Z = 18:32:31 ICT)
+ Discord Trading Daily — **không hề tin dòng in "refreshed" giả của python script**.
Wrapper này chỉ được commit sau đó 13 phút (`dd7feb9`, 18:45:14 ICT) — nghĩa là test tay
này chạy trên bản wrapper CHƯA commit, đúng lúc đang xác minh nó hoạt động trước khi đưa
vào cron thật.

**Root cause của LẦN FAIL cụ thể này:** không phải bug — đây là **permission mismatch của
phiên test tay**, không phải của cron. Phiên interactive Mike mặc định dùng
`bq-reader-8l` (service account read-only, an toàn theo thiết kế cho mọi truy vấn tương
tác) — không đủ quyền ghi bảng. Cron THẬT (crontab dòng `30 1 * * 6 …` = 08:30 ICT thứ Bảy,
cài cùng ngày) chưa từng chạy lần nào (lần đầu tiên sẽ là thứ Bảy **2026-07-18**), nên
**identity mà cron thật sự dùng khi Mike không ngồi tương tác vẫn CHƯA được xác nhận** —
nếu cron cũng chạy dưới identity read-only (vd nếu service account mặc định của toàn máy
là read-only, chỉ phiên Mike mới override), thì fa_ratings_8l sẽ tiếp tục KHÔNG BAO GIỜ
refresh được, chỉ khác là giờ sẽ FAIL ỒN ÀO (đúng thiết kế) thay vì lặng lẽ đứng yên như
trước 2026-07-11.

**Còn treo:** xác nhận identity cron thật dùng để ghi BQ — chỉ quan sát được khi cron tự
chạy lần đầu thứ Bảy 07-18 (ghi vào `logs/fa_ratings_8l_refresh.log` + bus event
`fa_ratings_8l-refresh-ok`/`-failed`). Nếu THẤT BẠI lần đầu vì cùng lý do quyền → cần cấp
quyền ghi cho identity chạy cron (không phải sửa lại script — script đã đúng).

**Bài học:** đây là ví dụ THỰC TẾ, CÙNG NGÀY của chính nguyên tắc mà `coding_guidelines.md`
§9 vừa mới viết ra sau vụ SIGNAL_V11 base-leak buổi sáng — "đừng tin self-report, verify
artifact thật". `refresh_fa_ratings_8l.sh` là wrapper ĐẦU TIÊN trong hệ thống áp dụng công
thức này CHO CHÍNH BƯỚC GHI BQ (không chỉ đọc) — và nó bắt được lỗi thật ngay lần chạy thử
đầu tiên. Không phải sự cố cần "sửa", mà là bằng chứng cơ chế phòng thủ hoạt động — nhưng
câu hỏi vận hành gốc (quyền ghi BQ cho tiến trình cron không tương tác) vẫn mở, giống hệt
tình trạng đã ghi trong `kb/current_ops.md` cho `fa_ratings` append-only refresh (cron
09:15 ICT thứ Bảy, cùng vấn đề, chờ giải chung).
