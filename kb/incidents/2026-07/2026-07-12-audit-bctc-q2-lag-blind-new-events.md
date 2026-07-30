---
kind: incident
date: 2026-07-12
topic: audit-bctc-q2-lag-blind-new-events
title: >-
  2026-07-12 — Audit sẵn sàng BCTC Q2/2026 bắt LAG live-candidate pipeline mù sự kiện mới <30 phiên (R1 CRITICAL) + freshness ticker_financial bị 1 mã early-filer reset đồng hồ cả bảng (F1 MEDIUM)
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-12 — Audit sẵn sàng BCTC Q2/2026 bắt LAG live-candidate pipeline mù sự kiện mới <30 phiên (R1 CRITICAL) + freshness ticker_financial bị 1 mã early-filer reset đồng hồ cả bảng (F1 MEDIUM)

**Hiện tượng:** user yêu cầu rà soát sau khi phát hiện MBS đã công bố BCTC Q2 (08/07) —
xác nhận mùa Q2 đã bắt đầu thật. Dispatch song song Taylor (góc tín hiệu) + Winston (góc
hạ tầng).

- **R1 CRITICAL (Taylor_20260712_121642)** — sổ LAG (PEAD, 50-65% NAV khi active) tính
  candidate LIVE từ nguồn không biết sự kiện BCTC mới <30 phiên, trong khi entry thật là
  T+5 — nghĩa là **100% entry LAG mùa Q2 sẽ bị bỏ lỡ trong im lặng** nếu không sửa trước
  khi mùa cao điểm tới (~cuối 07).
- **F1 MEDIUM (Winston_20260712_122313)** — freshness-check `ticker_financial` đo bằng
  `MAX(time)` toàn bảng; 1 mã early-filer (MBS) đủ để cả check báo "xanh" dù 1254/1255 mã
  còn lại chưa công bố gì — nguy cơ vendor stall giữa mùa im lặng tới 90 ngày mà không ai
  biết.

**Fix R1:** module mới `lag_live_schedule.py` (commit `f7463e3`, repo WorkingClaude) tách
nguồn — identity/NP_R từ pkl fresh-daily (biết ngay tại ngày release), điều kiện phụ vẫn
từ CSV cũ (luôn đủ dữ liệu vì nhìn về quá khứ). Backtest pin R3 byte-identical (không đổi
số). Bonus: fix còn dọn thêm 1 look-ahead 30-phiên ẩn khác trong logic cũ (sibling cùng
ngày dùng giá trị tương lai) mà không ai từng phát hiện trước đó.

**Fix F1:** breadth-probe WARN-only theo mùa BCTC vào `bq_freshness_check.sh` (commit
`1b2fd13`, repo mike, job `Winston_20260712_124928`) — đếm `COUNT(DISTINCT ticker)` của
quý vừa kết thúc, WARN nếu đứng yên ≥5 ngày trong cửa sổ mùa, có guard chống false-positive
đầu/cuối mùa.

**Review vòng 2 (Spyros/risk-auditor, job `Spyros_20260712_131501`) phát hiện thêm 3 mục
nhỏ, cả 3 đã xử lý trong ngày:**
- M1 MEDIUM: field `lag_source_error` mới trong `golive_v23_status.json` (commit
  `a5f3810`) phân biệt "0 upcoming vì thật không có gì" vs "0 vì pkl lỗi" + probe
  `lag-pkl` WARN-only (commit `f84b995`, dùng stateful catch-up để tránh báo giả lệch giờ
  refresh).
- L2 LOW: nhãn "Đã vào"/`ENTERED` đổi thành "Cửa sổ entry đã qua — đối chiếu vị thế thực"/
  `WINDOW_PASSED` (commit `853080d`), tránh DollarBill hiểu nhầm đã có vị thế.
- L1 LOW: không cần code, chỉ document — quant-skeptic tự tái hiện được đúng lỗi pandas
  hệ thống không đọc được pkl format mới khi verify, xác nhận cảnh báo có căn cứ thật.

**Verify:** quant-skeptic CONFIRMED cho cả R1 fix (job `Taylor_20260712_124834`, verify
13:19:24) và bộ fix M1/L2 (job riêng `Taylor_20260712_135148`, verify 14:13:09) — 2 job
KHÁC NHAU, verify độc lập từng job, không phải 1 job gộp cả 2. Spyros/risk-auditor review
vòng 2 xác nhận KHÔNG có rủi ro chặn còn lại.

**Bài học:** một pipeline "as-of correct" (không look-ahead) vẫn có thể bị **BLIND** với
dữ liệu vừa xuất hiện nếu nguồn phụ dùng cửa sổ lookback cố định (30 phiên) không tính
tới trường hợp sự kiện MỚI xảy ra bên trong cửa sổ đó — khác hẳn look-ahead (nhìn tương
lai), đây là "nhìn quá khứ nhưng khoảng nhìn quá hẹp cho case biên mùa vụ". Audit chủ động
TRƯỚC mùa cao điểm (thay vì đợi entry đầu tiên fail rồi mới điều tra) là điều làm đúng ở
đây — không có thiệt hại thật nào xảy ra.
