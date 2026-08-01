---
kind: incident
date: 2026-08-01
topic: weekly-monthly-report-dead
title: >-
  2026-08-01: báo cáo tuần/tháng SpaceX+ZaloPay chết 2 tuần liền — WARN chạy đúng nhưng bị
  chôn trong ops_health_check 4 lần/ngày, không có forcing function nào khiến ai action
status: fixed
category: reporting-cadence
origin: >-
  ops_health_check.sh §7 (thêm 2026-07-13 sau sự cố tương tự lần 1) chỉ IN 1 dòng WARN vào
  message chạy 4 lần/ngày (2 khung giờ x 2 account) — thiết kế "cảnh báo" nhưng không có ai/
  cái gì THỰC SỰ hành động khi thấy WARN, và bản thân báo cáo tuần/tháng vẫn hoàn toàn phụ
  thuộc Mike tự nhớ tự soạn trong 1 phiên sống
recorder: >-
  Mike, user hỏi thẳng "2 task báo cáo tuần/tháng chết mà không ai quản lý" — phát hiện đúng
---

# 2026-08-01: báo cáo tuần/tháng chết 2 tuần liền

**Bối cảnh phát hiện:** user hỏi thẳng "2 task gửi report báo cáo tuần và tháng hiện nay chết mà
không ai quản lý" — không phải Mike tự phát hiện, user đã nhận ra trước.

**Xác nhận thật (không đoán):**
- Báo cáo tuần gần nhất: `mike/reports/SpaceX_ZaloPay_weekly_report_2026-07-13_to_2026-07-17.md`
  (gửi 2026-07-19). **2 tuần liên tiếp bị bỏ sót**: 2026-07-20→07-24 và 2026-07-27→07-31.
- Báo cáo tháng: **chưa từng có file `*_monthly_report_*.md` nào** trong `mike/reports/`. Tháng
  go-live đầu tiên (2026-07) đã đóng hoàn toàn (hôm nay 08-01) mà chưa có báo cáo tháng nào.
- `logs/ops_health.log` xác nhận WARN đã CHẠY ĐÚNG: dòng "⚠️ Báo cáo tuần quá hạn — tuần
  2026-07-20→2026-07-24 chưa có báo cáo" xuất hiện **4 lần/ngày liên tục từ 2026-07-27 đến
  2026-08-01** (~20 lần) — và `notify_thread.sh` xác nhận message này ĐÃ post vào Discord
  Trading Daily mỗi lần. Không phải "cơ chế không chạy" — cơ chế cảnh báo chạy đúng, nhưng bị
  chôn trong 1 message tổng hợp 4 lần/ngày (2 khung giờ x 2 account) lẫn với BQ freshness/
  circuit breaker/anomaly scan/corp-action — không ai tách riêng dòng này ra để hành động.
- Root cause gốc: cơ chế cũ (từ 2026-07-13, sau sự cố tương tự lần 1: tuần 07-06→07-10 bị bỏ
  sót) chỉ là WARN — báo cáo vẫn hoàn toàn phụ thuộc Mike (phiên sống) tự đọc log/Discord rồi
  TỰ TAY dispatch Taylor soạn. Không có phiên Mike nào chủ động đọc và hành động trong 5 ngày.

**Fix (2026-08-01):**
1. Dispatch ngay Taylor (`Taylor_20260801_080509`, opus/high) soạn + gửi CẢ 3 báo cáo còn thiếu:
   tuần 07-20→07-24, tuần 07-27→07-31, tháng 2026-07 — dùng đúng pipeline
   `verify_account_snapshot.py --account-no` + đối chiếu `nav_history_{account}.csv` thật.
2. Gỡ §7 khỏi `ops_health_check.sh` (chỉ để lại pointer + giữ `today_d`/`_date`/`_timedelta`
   cho các mục sau vẫn cần dùng biến này).
3. Script mới **`mike/bin/check_report_cadence.sh`** (cron riêng 08:30 ICT T2-T6, SAU
   `cron_health_check_daily.sh` 08:25):
   - Liệt kê **MỌI** tuần đã đóng đủ (qua hết thứ Sáu + buffer 3 ngày) còn thiếu báo cáo kể từ
     báo cáo tuần gần nhất — KHÔNG chỉ tuần liền trước hôm nay (bug thiết kế đã tự bắt + tự sửa
     trong lúc viết: bản đầu chỉ tính "tuần liền trước today" nên nếu lỡ 1 tuần, tuần cũ hơn sẽ
     KHÔNG BAO GIỜ được nhắc lại — chính là cách sự cố này đã xảy ra).
   - Khi quá hạn: **TỰ dispatch Taylor `--bg --model opus --effort high`** soạn+gửi báo cáo
     (không chỉ cảnh báo) + post escalation riêng vào **Trading report topic**
     (`1522576692638388364`, không phải Trading Daily bị chôn) + bus event `question`.
   - Idempotent qua `state/report_cadence_dispatched.json` (khoá theo period+ngày) — không
     dispatch trùng trong ngày, nhưng tự retry ngày sau nếu báo cáo vẫn chưa xuất hiện (không
     cần người nhắc lại).
4. Cập nhật `kb/cron_registry.md` (dòng 08:30 mới) + `kb/current_ops.md` (bảng cron) cùng commit.

**Verify đã làm (không chỉ đọc lại code):**
- `bash -n` cả 2 script (`check_report_cadence.sh`, `ops_health_check.sh` sau khi sửa) — pass.
- Chạy thật `ops_health_check.sh` sau khi sửa để xác nhận không vỡ (§8/§9 vẫn cần `today_d`) —
  phát hiện NameError ngay ở lần chạy đầu (do quên giữ lại định nghĩa `today_d`), sửa xong chạy
  lại sạch. **Lưu ý phụ**: lần chạy thật này vô tình kích hoạt `ops_autofix.sh`/`wags_autofix`
  cho 2 vấn đề tồn tại từ trước (không liên quan sửa của tôi) — chấp nhận được vì đó đúng cơ chế
  tự-phát-hiện-tự-sửa đang hoạt động, không phải tác dụng phụ có hại.
- Test độc lập logic Python (liệt kê tuần thiếu) với `today` giả lập 2026-08-01 và 2026-08-05 —
  xác nhận bắt đúng CẢ 2 tuần thiếu khi giả lập trường hợp xấu nhất (không có báo cáo mới nào).
- Crontab: `diff` trước/sau khi thêm dòng mới — xác nhận chỉ thêm đúng 1 dòng, không đổi gì khác.

**Còn treo:** chờ xác nhận `Taylor_20260801_080509` hoàn tất + đối chiếu NAV/% với
`nav_history_{account}.csv` trước khi báo "xong" cho user (đúng kỷ luật verify-artifact, không
tin self-report).
