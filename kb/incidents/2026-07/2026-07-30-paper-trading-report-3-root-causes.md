---
kind: incident
date: 2026-07-30
topic: paper-trading-report-3-root-causes
title: >-
  2026-07-30: paper-trading report "báo không hoạt động" — 3 root causes tìm + sửa cùng phiên (không phải 1 bug, 3 bug độc lập chồng lên nhau)
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-30: paper-trading report "báo không hoạt động" — 3 root causes tìm + sửa cùng phiên (không phải 1 bug, 3 bug độc lập chồng lên nhau)

**Bối cảnh:** User báo các báo cáo paper-trading gần đây "không hoạt động", yêu cầu điều tra
cẩn thận toàn bộ thay vì chỉ tin báo cáo tự report. Điều tra trực tiếp (không dispatch) từ
crontab → log → dữ liệu nguồn, không dừng ở lần lỗi đầu tiên tìm thấy.

**Sự cố A (NGHIÊM TRỌNG, ĐANG SỐNG lúc phát hiện) — `PaperBroker.place_order()` thiếu tham số
`cash_only`, harness paper-main crash 100% cả ngày 07-30.** Commit `4d63daa`/`3b2d2c3` (fix
TV1 loanPackageId 07-28, xem entry `spacex-loanpackageid-order-reject`) thêm `cash_only=False`
vào `BrokerBase`/`PHSBroker`/`DNSEBroker.place_order()` nhưng BỎ SÓT `PaperBroker` — trong khi
`executor.py` gọi `broker.place_order(..., cash_only=...)` không phân biệt broker. Kết quả: mọi
lệnh paper-main từ 10:46 ICT hôm nay đều `PLACE_FAIL`/`ATC_FAIL` với
`TypeError: unexpected keyword argument 'cash_only'` — phiên sáng chạy 386 lần retry tới khi
`pkill` trưa giết, phiên chiều 45 lần retry tới khi tự hết phiên (14:44 ICT). Đây là TÁI DIỄN
đúng lớp lỗi đã có tiền lệ 2 ngày trước (entry `spacex-loanpackageid-order-reject`, 07-28) —
selfcheck gốc lúc đó chỉ test `DNSEBroker`, không test các subclass khác của `BrokerBase`.
**Fix:** thêm `cash_only=False` vào `PaperBroker.place_order()` (`trading_bot/brokers.py`).
**Prevention:** mở rộng `cash_only_loan_package_selfcheck.py` — thêm bài test tổng quát duyệt
MỌI subclass của `BrokerBase` xác nhận signature `place_order` không thiếu tham số nào so với
lớp cha, thay vì chỉ test riêng `DNSEBroker`. Verify: replay trực tiếp `make_broker()` với đúng
lệnh HPG đã fail hôm nay → thành công; selfcheck 3/3 broker class PASS.

**Sự cố B (DATA INTEGRITY, tồn tại từ khi SpaceX/ZaloPay go-live 07-01) — mục "Fill-timing
window" trong `paper_programs_daily_report` đo NHẦM dữ liệu LIVE thay vì paper.**
`execution_quality_review.py` (nguồn probe của mục 4) đọc fills từ `dnse_raw_*.jsonl` — file
này CHỈ chứa lệnh broker DNSE thật (SpaceX/ZaloPay/RocketX), paper "main" dùng `PaperBroker`
không bao giờ ghi vào đây. Vì account "main" có `account_id=None` trong config, cờ `--account`
không dùng được cho nó (sẽ `sys.exit`) → registry gọi script KHÔNG filter gì → mọi số liệu
"BUY window adherence"/"SELL window adherence"/"rejected orders" hiển thị trong báo cáo hàng
ngày thực ra là đo TOÀN BỘ lệnh giao dịch thật của SpaceX/ZaloPay/RocketX, không liên quan gì
tới harness paper-main mà mục này được thiết kế để đánh giá — giải thích tại sao "BUY window
adherence" gần như luôn ~0-3% (lệnh thật không có lý do rơi vào khung giờ test của paper
harness). Đây là biến thể của pattern đã ghi ở `coding_guidelines.md` §12 (file dùng chung
nhiều account, thiếu filter) — khác ở chỗ đây là LIVE lẫn vào PAPER, không phải live-vs-live.
**Fix:** khi không truyền `--account`, loại trừ tường minh mọi account có `mode=live` trong
`secrets/trading_bot_accounts.json` (thay vì "không filter = show hết"), đúng nguyên tắc §12
"thiếu account_no trong scope là dấu hiệu thiếu tham số, không phải lý do bỏ lọc". Verify: sau
fix, mục A/B chỉ còn hiện số liệu từ `exec_main_*_journal.csv` (đúng nguồn paper), mục C hiện
"no completed fills yet" (đúng — paper chưa từng ghi fill theo format này) thay vì số liệu live
nhầm lẫn.

**Sự cố C (nhẹ hơn, ẩn lỗi thật) — mục C (Directional Fill Sanity) crash âm thầm ~55% số lần
chạy vì `bq_local_cache.get_cache()` trả `None` khi cache "unverified", nhưng caller gọi thẳng
`lc.query()` không kiểm tra `None` → `AttributeError` bị bắt bởi `except Exception` rộng, in ra
`(skipped vs-open: 'NoneType' object has no attribute 'query')` — trông như lỗi ngẫu nhiên thay
vì tình trạng cache-chưa-verify đã biết. Đo được: 10/18 lần chạy trong lịch sử log bị skip kiểu
này. **Fix:** kiểm tra `lc is None` tường minh, in thông báo rõ ràng thay vì để crash vào
except chung (không tự implement fallback BQ thật — ngoài phạm vi, và sau fix B mục này hầu như
sẽ luôn "no completed fills yet" nên ít quan trọng hơn).

**Bổ sung phát hiện chéo cùng phiên (không phải bug mới, chỉ audit thêm để loại trừ):**
crontab report cron (đổi 15:20→16:00 từ Sự cố 4 RETRO 07-29) đang chạy đúng; `papertrade_daily.sh`
chain 0 FAIL trong 2 tuần gần nhất; `papertrade_weekly_report.py`/`paper_trade_weekly_report.py`
đã dead từ 06-14 nhưng ĐÃ được audit + chấp nhận trước đó (`Winston_20260712_151206`), không
phải regression mới.

**Cơ chế phát hiện mới thêm (đúng yêu cầu "tránh lỗi mà không biết"):** `paper_programs_daily_report.py`
giờ scan output của mọi probe "type: command" tìm marker `FAIL|ERROR|Reject...: <N>` (N>0) hoặc
Python traceback, và chèn dòng `⚠️ CẦN CHÚ Ý` ngay đầu section đó nếu khớp — Sự cố A (431
FAIL/ERROR events) đáng lẽ đã hiện NGAY trong báo cáo hôm nay nếu cơ chế này có từ trước, thay
vì nằm lẫn trong một khối text dài không ai rà.

- **a. Mới hay tái diễn?** Sự cố A = TÁI DIỄN (cùng lớp lỗi với `spacex-loanpackageid-order-reject`
  07-28, khác broker class). Sự cố B = MỚI, tồn tại âm thầm từ 07-01 (go-live), chưa từng có
  entry. Sự cố C = MỚI nhưng nhẹ.
- **b. Fix hoàn chỉnh hay còn hở?** Cả 3 đã fix + verify trong phiên (replay lệnh thật cho A,
  so sánh output trước/sau cho B/C, chạy lại `paper_programs_daily_report.py` full 8 mục exit=0
  cho cơ chế cảnh báo mới). Chưa qua quant-skeptic/Wags độc lập — nên làm trước khi coi "đóng
  hoàn toàn" vì A chạm `executor.py`/`brokers.py` (lõi thực thi, dù chỉ ảnh hưởng nhánh paper).
- **c. Đơn lẻ hay pattern?** A nối dài pattern "thêm kwarg vào lớp cha, quên 1 subclass" — đã
  2 lần trong 2 ngày (07-28 DNSEBroker, 07-30 PaperBroker); B là pattern mới trong nhóm lớn
  §12 (shared-file-thiếu-filter) nhưng hướng live→paper thay vì live→live.

**File đổi:** `trading_bot/brokers.py` (PaperBroker.place_order + cash_only), `execution_quality_review.py`
(account-scope exclude LIVE mặc định + None-check rõ ràng cho BQ cache), `cash_only_loan_package_selfcheck.py`
(test tổng quát mọi BrokerBase subclass), `mike/bin/paper_programs_daily_report.py` (attention-flag scan
cho mọi probe "command").

**Addendum (cùng ngày) — review độc lập thay vì quant-skeptic:** user hỏi có cần quant-skeptic
verify không. Đánh giá: KHÔNG phù hợp — checklist 7-attack của quant-skeptic (look-ahead,
OOS, panel-curation, param-overfit, capacity/ADV, arithmetic CAGR/Sharpe) toàn bộ nhắm vào
claim R&D/backtest, không áp dụng cho bug plumbing (không có claim định lượng nào để bác bỏ).
Thay vào đó dispatch review độc lập (agent tổng quát, không thấy lý luận gốc, tự chạy lại mọi
thứ) nhắm đúng vào correctness — và tìm ra 1 gap thật: **4 file selfcheck khác
(`churn_guard_selfcheck.py`, `extreme_regime_selfcheck.py`, `tick_retry_selfcheck.py`,
`t2_settlement_selfcheck.py`) dùng `FakeBroker`/`_RecordingBroker` test double cũng thiếu tham
số `cash_only`** — cùng lỗ hổng như PaperBroker nhưng bản test double, đã bị hỏng ÂM THẦM từ
07-28 (khi `executor.py` thêm `cash_only=` vào lời gọi) không ai biết, đúng tinh thần "lỗi mà
không biết" của điều tra hôm nay. Đã tự verify độc lập (chạy lại cả 4, thấy đúng lỗi) rồi fix
cùng pattern (`cash_only=False`, bỏ qua) — cả 4 giờ PASS 100%. Commit `ac62143` (repo
WorkingClaude). 1 mục KHÔNG fix hôm nay (pre-existing, không liên quan sự cố này): assertion
"engine order cash_only=True" trong `cash_only_loan_package_selfcheck.py` đọc thẳng file state
mutable `data/trade_plans/discretionary/state_TV1_SpaceX.json` — TV1 đã chuyển `status:
completed` (chương trình xong 07-29) nên assertion tự nhiên FAIL, không phải regression; nên
đóng băng 1 bản fixture riêng cho test này thay vì đọc state sống, nhưng để dành việc đó cho
lúc khác (không thuộc phạm vi điều tra hôm nay).
