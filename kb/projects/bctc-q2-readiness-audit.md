# Audit sẵn sàng mùa BCTC Q2/2026
> Dự án đã đóng — tách khỏi context_pack 2026-07-12. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. KHÉP KÍN — fix CRITICAL LAG-blind + MEDIUM freshness + 3 mục nhỏ, đều verified.

## Sẵn sàng mùa BCTC Q2/2026 — audit + fix CRITICAL/MEDIUM đã khép kín trong ngày (2026-07-12)
User yêu cầu rà soát sau khi phát hiện MBS đã công bố BCTC Q2 (08/07) — xác nhận mùa Q2 đã bắt đầu
thật (n=1 hiện tại). Dispatch song song Taylor (góc tín hiệu) + Winston (góc hạ tầng), cả 2 audit
độc lập không trùng việc.

**CRITICAL (Taylor) — ĐÃ FIX, CONFIRMED cả kỹ thuật (quant-skeptic) lẫn rủi ro vận hành (Spyros/
risk-auditor)**: sổ LAG (PEAD, 50-65% NAV khi active) bị mù với sự kiện BCTC mới <30 phiên trong khi
entry là T+5 — 100% entry LAG mùa Q2 sẽ bị bỏ lỡ trong im lặng nếu không sửa. Fix: module mới
`lag_live_schedule.py` (commit `f7463e3`) tách nguồn — identity/NP_R từ pkl fresh-daily (biết ngay
tại ngày release), điều kiện phụ vẫn từ CSV cũ (luôn đủ dữ liệu vì nhìn về quá khứ). Backtest pin R3
byte-identical (không đổi số 27.84/1.84/-18.2/1.53). Bonus: fix còn dọn thêm 1 look-ahead 30-phiên
ẩn khác trong logic cũ (sibling cùng ngày dùng giá trị tương lai) mà không ai từng phát hiện.

**MEDIUM (Winston) — ĐÃ FIX, CONFIRMED**: freshness-check `ticker_financial` đo bằng MAX(time) toàn
bảng, 1 mã early-filer (MBS) đủ để cả check báo "xanh" dù 1254/1255 mã còn lại chưa công bố — nguy
cơ vendor stall giữa mùa im lặng tới 90 ngày. Fix: breadth-probe WARN-only theo mùa BCTC (commit
`1b2fd13`), có guard chống false-positive đầu/cuối mùa.

**3 mục nhỏ Spyros phát hiện thêm — ĐÃ XỬ LÝ HẾT TRONG NGÀY, quant-skeptic CONFIRMED (2026-07-12)**:
- **M1 (MEDIUM) — ĐÃ FIX**: field `lag_source_error` mới trong `golive_v23_status.json` (commit
  `a5f3810`) phân biệt "0 upcoming vì thật sự không có gì" vs "0 vì pkl lỗi". Kèm probe `lag-pkl`
  WARN-only (commit `f84b995`) — dùng "stateful catch-up" (so pkl với chính lịch sử của nó, không so
  tức thời với BQ) để tránh báo giả khi lệch giờ refresh bình thường (15:30 pkl → 19:00 check).
- **L2 (LOW) — ĐÃ FIX** (commit `853080d`): nhãn `ENTERED`/"Đã vào" đổi thành `WINDOW_PASSED`/"Cửa sổ
  entry đã qua — đối chiếu vị thế thực" ở cả 2 bề mặt hiển thị, tránh DollarBill hiểu nhầm là đã có
  vị thế. Xác nhận không code nào parse chuỗi cũ trong pipeline sống.
- **L1 (LOW) — không cần code**, đã document. quant-skeptic **tự tái hiện được đúng** tình huống lỗi
  này (pandas hệ thống không đọc được pkl format mới) khi verify, xác nhận cảnh báo là có căn cứ
  thật, không phải lý thuyết suông.

**KẾT LUẬN: toàn bộ chuỗi audit sẵn sàng mùa BCTC Q2/2026 đã khép kín 100%** — CRITICAL + MEDIUM +
3 mục nhỏ, tất cả đã fix và verify (quant-skeptic + risk-auditor độc lập). Không còn issue nào tồn
đọng trước tuần giao dịch tới. Chi tiết đầy đủ: trace bus `Taylor_20260712_121642` (audit gốc) →
`Taylor_20260712_124834` (fix CRITICAL) → `Spyros_20260712_131501` (phản biện) →
`Taylor_20260712_135148` (fix 3 mục nhỏ); song song `Winston_20260712_122313` →
`Winston_20260712_124928` (fix MEDIUM).

Chi tiết đầy đủ: bus trace `Taylor_20260712_121642` → `Taylor_20260712_124834` (fix) và
`Winston_20260712_122313` → `Winston_20260712_124928` (fix), phản biện `Spyros_20260712_131501`.
