---
kind: incident
date: 2026-07-07
topic: eod-nav-zalopay-minus-98
title: >-
  2026-07-07 — EOD report đăng NAV ZaloPay -98,25% (17,5tr) lên Trading report
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-07 — EOD report đăng NAV ZaloPay -98,25% (17,5tr) lên Trading report

**What happened:** EOD report 15:00 cho ZaloPay in NAV **17.536.701đ (-98,25%)** — user
nhìn phát hiện ngay. Phần khớp lệnh/đối soát của cùng report ĐÚNG (2/2 lệnh, broker khớp
state); chỉ NAV sai.

**Root cause:** `daily_nav_snapshot.py` lấy `mtm_stock` từ `verify_account_snapshot.py` —
tái dựng vị thế TỪ LỊCH SỬ FILL journal. Đúng với account clean-slate (SpaceX, mọi vị thế
đều do bot mua từ 07-01), nhưng ZaloPay có 6 vị thế legacy (DGC/VPB/VIB/VHC/TCM/TLG,
~976tr) KHÔNG có fill history → bị bỏ sót toàn bộ; NAV chỉ còn VCB 100cp mua hôm nay
(6,13tr) + cash. Đây chính là "known gap" đã ghi từ hôm onboarding (kb/coding_guidelines.md
§7.4, current_ops) — biết trước mà KHÔNG enforce: pipeline vẫn chạy cho account legacy và
đăng số rác thay vì từ chối in. Vi phạm nguyên tắc của chính mình ("số không trace được →
n/a, không đăng"). Lỗi thứ 2 độc lập: KHÔNG có tầng sanity nào chặn một con số -98%/ngày
trước khi auto-publish.

**Fix (cùng ngày, commit repo mike):**
1. NAV đổi nguồn vị thế: **API broker thật** (`DNSEBroker.get_positions()`) × giá đóng cửa
   verified (DNSE ATC G1 hôm nay / BQ ngày quá khứ) — journal-reconstruction chỉ còn là
   cross-check advisory cho cost-basis, NAV không phụ thuộc nữa. Nguyên tắc: NAV đo TÀI SẢN
   THẬT → hỏi broker; journal đo LỊCH SỬ GIAO DỊCH → dùng cho P&L attribution.
2. `broker_positions()` gọi kèm `get_cash()` để ngày HOLD (bot không đặt lệnh, không có
   balance record) vẫn có bản ghi balance tươi kèm account tag.
3. **Sanity guard**: |ΔNAV| > `NAV_SANITY_MAX_PCT` (mặc định 15%)/ngày → TỰ CHẶN không ghi
   history/không in NAV, in cảnh báo đòi người kiểm tra (nạp/rút tiền thật → chạy lại với
   ngưỡng cao hơn). Test: ngưỡng 0.1% chặn đúng, ngưỡng mặc định cho qua -0.73% thật.
4. Số đúng đã verify + đính chính gửi vào đúng topic Trading report: **ZaloPay 992.702.201đ**,
   SpaceX 985.272.365đ. `nav_history_ZaloPay.csv` dòng rác đã thay bằng số đúng.

**Lesson:** một "known gap" được ghi vào tài liệu nhưng không được ENFORCE trong code là
một bug hẹn giờ — tài liệu không chặn được cron 15:00. Nếu biết pipeline không xử lý được
một class account, pipeline phải TỰ TỪ CHỐI class đó (fail loudly) cho tới khi được sửa,
không phải chạy tiếp và in số sai. Và mọi số client-facing cần một sanity bound độc lập
với nguồn tính — guard 10 dòng rẻ hơn nhiều lần một con số -98% đến tay user.
