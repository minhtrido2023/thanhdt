# DT5G BULL-giả bug → audit freshness toàn hệ thống
> Dự án đã đóng — tách khỏi context_pack 2026-07-13. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. KHÉP KÍN — EW-leg path fix + CRITICAL custom30V basket fix + F3 re-pin; live không sai.

## DT5G BULL-giả bug → audit freshness toàn hệ thống → CRITICAL basket fix → re-pin baseline R3
### CHUỖI ĐÃ KHÉP KÍN HOÀN TOÀN (2026-07-11), chỉ còn 3 mục chờ xác nhận qua cron thứ Hai 07-13

**Khởi nguồn**: user nghi ngờ candidate BULL sắp commit của DT5G (breadth/thanh khoản yếu, không
giống bull thật). Điều tra ra: reorg 06-21 (`10ae395`) làm writer `vnindex_5state_ew_v1.py:519` ghi
lệch path, EW-leg đóng băng từ 06-22 → base v3.4b rơi về chấm điểm index-only → BULL GIẢ (streak
9/10, thiếu 1 phiên mới commit). **Live KHÔNG bị ảnh hưởng sai** — `dt5g_live` chưa từng commit
BULL. Fix 1 dòng (`498c3a6`) + quant-skeptic CONFIRMED.

**Mở rộng audit** (theo yêu cầu user "rà soát freshness toàn hệ thống 8L/production, không chỉ
DT5G") phát hiện thêm, TẤT CẢ đã fix + verify (mỗi bước đều quant-skeptic CONFIRMED):
- **CRITICAL**: rổ "custom30V" production thực ra là rổ BLEND (env-default sai), lệch 14/30 mã so
  với rổ yieldcombo đã backtest — writer bảng thật `custom30v_8l` chết từ 06-18. Fix: hồi sinh
  writer + trỏ advisory đúng bảng (`e02a75b`).
- **HIGH**: `compute_active_nav.py` dùng giá BQ không gate cho sizing ZaloPay; `bq_freshness_check.sh`
  có bug `-le`/`MAX_STATE_LAG` khiến báo FRESH giả (lý do bug gốc sống 3 tuần không ai biết).
- **MEDIUM**: field `close` (BQ stale) rò vào context DollarBill không code-enforce; `risk_monitor.py`
  HALT không check provenance; freshness-check chỉ phủ 3/8 bảng cần thiết; chuỗi 8L/papertrade
  FAIL im lặng không alert.
- **F3 (phát hiện lớn nhất)**: `signal_v11_sql.py` (dùng chung, entry gate BAL book) đọc bảng BASE
  thay vì `dt5g_live` — sổ tín hiệu production (pt_v4/pt_v22, paper) đã mua theo BULL giả
  (PVD/TVN/VCG/TLD/TPB/ASP). Fix tracker (`0537514`) — sổ **tự sửa sạch qua full-replay**, xác nhận
  thực nghiệm, không cần can thiệp tay (`9149c0f`). Baseline R3 đã pin cũng dùng bảng base → **re-pin
  lại** (`09724bc`): **CAGR 28.05%→28.82%, Sharpe 1.86→1.90, MaxDD -17.5%→-15.7%, Calmar 1.60→1.83**
  — cải thiện toàn diện, DSR=1.0000/PBO=0.209 không suy giảm. Backup CSV cũ + banner SUPERSEDED
  trong `data/results_registry.md`. `pt_v12_live.py` xác nhận KHÔNG phải production consumer (chết
  từ 05-19), không cần vá.

**⚠️ Số tham chiếu V2.4 chính thức đã đổi** — CLAUDE.md/canonical.md ghi "R3 NEUTRAL-only @50B:
CAGR 28.05%..." **ĐÃ LỖI THỜI**, cần cập nhật thành 28.82%/1.90/-15.7%/1.83 ở lần sửa KB tiếp theo.

**✅ XÁC NHẬN XONG (2026-07-13, sau cron 18:30 ICT) — mục 1-2 đã kiểm chứng trực tiếp bằng BQ:**
1. ✅ `vnindex_5state_dt5g_live` + bảng gốc: NEUTRAL(3) liên tục 07-06→07-13, có đủ dòng 07-10/07-13
   mới, episode BULL giả đã biến mất hoàn toàn — khớp chính xác counterfactual đã verify trước đó.
   User tự phát hiện report vẫn hiện "9/10→BULL" lúc 16:00 ICT (TRƯỚC giờ cron) — đã giải thích rõ
   đó là dữ liệu cũ do report được xem trước khi cron chạy, không phải fix thất bại.
2. ✅ `custom30v_8l` writer đã hồi sinh, republish đúng lịch (lastModified 15:32 ICT hôm nay, qua
   cron papertrade riêng — khác giờ cron DT5G).
3. **Còn lại**: `19:00 ICT freshness-check 8 bảng` chạy thật lần đầu — CHƯA tới giờ kiểm tra (hiện
   18:37 ICT), Mike cần tự kiểm tra sau 19:00 xem có 2 WARN hợp lệ, 0 false-block không.
