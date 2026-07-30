---
kind: incident
date: 2026-07-17
topic: preflight-depth-check-false-alarm-ticker-prune
title: >-
  2026-07-17 — Preflight depth-check báo động giả "ticker_prune moi ruột" vì upstream ETL ghi dở partition hôm nay ngay trong phiên
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-17 — Preflight depth-check báo động giả "ticker_prune moi ruột" vì upstream ETL ghi dở partition hôm nay ngay trong phiên

**What happened:** ops_health_check 12:45 ICT (ZaloPay) cảnh báo `ticker_prune ngày mới nhất
chỉ có 1 mã (<200)` — pattern giống hệt sự cố moi ruột 07-14/15. Điều tra BQ live: mọi ngày
hoàn chỉnh đều khoẻ (07-16 = 262 mã, 07-08→07-15 = 264-267 mã); "ngày mới nhất" là partition
**2026-07-17 (hôm nay) đang được upstream ghi dở dang giữa phiên** — lớn dần theo thời gian
thực (1 → 2 mã trong vài phút; bảng `ticker` 5 → 7 mã). Không có corruption, không mất dữ liệu.

**Root cause:** depth-check trong `preflight_check.sh` (thêm 07-15) đo depth của `MAX(time)`
tuyệt đối. Hành vi mới của upstream (ghi từng dòng intraday cho ngày T thay vì chỉ ghi sau
đóng cửa) làm MAX(time)=hôm nay với depth ~1 → check sáng/trưa fail oan, dù dữ liệu EOD mà
ref_price/screening thực dùng (T-1) hoàn toàn khoẻ.

**Fix:** `preflight_check.sh` đo lag + depth trên **ngày hoàn chỉnh gần nhất**
(`time < CURRENT_DATE('Asia/Ho_Chi_Minh')`), ngưỡng giữ nguyên. Verify: chạy lại preflight
ZaloPay → `lag=1d, 262 mã ✓`. `bq_freshness_check.sh` (19:00, cần dữ liệu ngày T đầy đủ trước
khi chạy pipeline EOD) **cố ý giữ nguyên** ngữ nghĩa MAX(time) — nếu 19:00 mà ngày T vẫn thin
thì FAIL là đúng.

**Lesson:** check "ngày mới nhất" phải nói rõ vintage nó cần — checker chạy TRONG phiên đo
ngày hoàn chỉnh gần nhất; checker gate pipeline EOD đo ngày T. Cùng một câu SQL không phục vụ
được cả hai. Job `Winston_20260717_054509`.
