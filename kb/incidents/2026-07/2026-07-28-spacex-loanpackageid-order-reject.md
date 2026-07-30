---
kind: incident
date: 2026-07-28
topic: spacex-loanpackageid-order-reject
title: >-
  2026-07-28 — `spacex-loanpackageid-order-reject`: SpaceX (margin) TV1 buy orders bị DNSE từ chối `HTTP 400: loanPackageId is required` suốt ~30' phiên chiều, fix mid-session bằng commit 3b2d2c3
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-28 — `spacex-loanpackageid-order-reject`: SpaceX (margin) TV1 buy orders bị DNSE từ chối `HTTP 400: loanPackageId is required` suốt ~30' phiên chiều, fix mid-session bằng commit 3b2d2c3

**What happened:** Phiên chiều 13:43:38→14:12:54 ICT, 88 lần `PLACE_FAIL` liên tiếp cho lệnh
`BUY-TV1-DISC-03` (TV1, 100cp @19.600) với lỗi broker `HTTP 400: loanPackageId is required`
(journal `data/execution_logs/exec_SpaceX_2026-07-28_journal.csv` dòng 488→575). Không lệnh nào
được broker chấp nhận → không có orphan/dup (3 child_oid phân biệt, các fail trả 400 nên không tạo
order). Bot bị restart ~14:13 để deploy fix → SIGTERM tiến trình cũ = **rc=143** (chính là dấu hiệu
checker ops_autofix bắt được, job `Winston_20260728_071310`).

**Root cause:** commit 4d63daa (10:58 ICT) "Add per-order cash_only override to bypass account
default loanPackageId" **bỏ hẳn** field `loanPackageId` khi order gắn cờ `cash_only`. Nhưng SpaceX
là tài khoản **margin** — DNSE bắt buộc `loanPackageId` cho mọi lệnh, kể cả cash-only → 400. Lỗi
nằm ở **executor/broker order-placement logic** (ngoài ranh giới Winston, không chạm).

**Fix:** commit **3b2d2c3** @ 14:12:50 ICT "Fix cash_only to resolve per-symbol loanPackageId
instead of omitting it" (do phiên interactive/Mike thực hiện, KHÔNG phải Winston). Restart bot lúc
14:13 → **14:13:12 PLACE thành công (child_oid 326751) → 14:13:32 FILL** 100 TV1 @19.600. Sau đó
0 lỗi loanPackageId, bot sống khoẻ (pid 3282913).

**Lesson:** (1) `cash_only` override KHÔNG được omit `loanPackageId` trên tài khoản margin —
per-symbol resolve, đừng bỏ trắng. (2) rc=143 hôm nay có 2 nguồn KHÁC nhau cùng ngày: sáng =
restart thủ công lành tính (job `Winston_20260728_035952`); chiều = restart để deploy fix cho lỗi
đặt lệnh THẬT — checker gộp chung nhưng phải phân biệt. (3) Winston: root cause ở trading path →
không sửa, chỉ ghi nhận + xác minh fix đã fill; fix đã có sẵn (commit 3b2d2c3) và confirmed working.
