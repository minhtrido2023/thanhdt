# Charter — EXTREME-regime gate (`extreme_regime`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Gate phòng thủ intraday (arm 2-poll, sell-to-floor, buy-pause, cadence ×0.25) có ZERO false-trigger trong thị trường benign không? (stress-injection đã PASS 24/24)

## 📅 Nghiệm thu / mốc kết thúc

20 phiên EVIDENCE (executor chạy thật trên paper main) từ phiên thật đầu tiên 2026-07-07 → ước ~2026-08-03. Mốc cũ 2026-07-28 bỏ — 07-01→07-06 flag bật nhưng 0 phiên executor = 0 evidence, không đếm. | 2026-08-04: đứng 8 ngày do netting probe (đã gỡ 08-04), đếm lại → ước đủ 20 phiên ~2026-08-11.

## ✅ Tiêu chí GO/NO-GO

- ✅ (pass) Stress-injection 24/24 PASS (arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls) — stress_extreme_regime.py, week-1
- ⏳ (pending) ZERO false-trigger qua ~4 tuần benign trên account paper main — 2026-08-04 (job Taylor_20260804_124404): 0/15 phiên có bất kỳ marker EXTREME nào (quét chuỗi 'EXTREME' ở CẢ cột event lẫn note, 18/18 file journal). NHƯNG mới 15/20 phiên evidence — và nhánh trigger (ii) 3-sigma chỉ có 12/20 phiên sạch: 07-07/07-10/07-13 đọc rvol_20d từ monolith ticker_prune.parquet đóng băng 06-26 (M5, Winston fix tối 07-13 commit 1630916). Đo mức lệch: 5/18 ticker-session rvol STALE THẤP hơn thật (VNM 3 phiên tới −33,6%, MBB 2 phiên) ⇒ ngưỡng CHẶT hơn, gate NHẠY hơn mà vẫn không bắn ⇒ 5 ca này bằng chứng MẠNH hơn; 13/18 còn lại rvol STALE CAO hơn (ACB 07-10 +58,6%) ⇒ ngưỡng lỏng, 'không bắn' là bằng chứng YẾU hơn (rủi ro false-NEGATIVE, không phải false-positive). Trigger (i) cận sàn + _floor_guard_buy chỉ đọc quote sống ⇒ M5 KHÔNG ảnh hưởng, đủ 15/20. ⚠️ Phạm vi: rổ probe 6 large-cap chưa bao giờ tới gần sàn — 'zero false-trigger' chỉ chứng minh gate không kêu bậy trong điều kiện lành tính, KHÔNG chứng minh gate xử lý đúng khi sập.
- ✅ (pass) Không can thiệp NORMAL-path — 2026-08-04 (job Taylor_20260804_124404): 0 marker/15 phiên ⇒ 0 lần can thiệp thực tế. Cô lập code: _extreme_regime/_floor_guard_buy/_extreme_slice_mult đều return sớm khi extreme_regime_enabled=False; stress section 6g resolve cfg THẬT của SpaceX/ZaloPay qua load_config()/load_accounts() và chứng minh trực tiếp slice mua vẫn đặt bình thường trên live với cùng quote PNJ khoá sàn.
- ⏳ (pending) User sign-off trước khi bật live

## ℹ️ Ghi chú vận hành

Evidence tích lũy CHỈ khi executor chạy phiên trên account main — 0 phiên = 0 evidence, không tính là PASS. Từ 2026-07-07: probe harness chạy paper main mỗi ngày T2-T6 (cron 08:52 sinh plan mike/bin/paper_main_probe_plan.py, executor 09:10 + 13:05, log mike/logs/run_bot_main_*.log). | 2026-08-04 (job Taylor_20260804_124404) — CHECKPOINT: 15/20 phiên evidence (thiếu 5). Luồng evidence đứng 8 ngày 07-28→08-04 do bug netting probe harness, ĐÃ GỠ sáng 08-04 (job Taylor_20260804_094514) → chạy lại từ phiên 08-05, ước đủ 20 phiên ~2026-08-11 (~08-14 nếu muốn 20 phiên sạch cho CẢ nhánh trigger ii). Phiên 07-30 MẤT HẲN (386 PLACE_FAIL: PaperBroker.place_order() thiếu kwarg cash_only, đã fix commit 2af4abd). 07-31 + 08-04 chỉ có lệnh SELL (dư netting) ⇒ buy-path KHÔNG được đánh giá 2 phiên đó. | ⚠️ SỬA LỖI REGISTRY: probe.markers cũ khai EXTREME_SELL/EXTREME_UP (KHÔNG tồn tại trong code, chỉ có trong fixture paper_report_render_selfcheck.py) và THIẾU EXTREME_FLOOR_GUARD (marker THẬT, executor.py:1026, chính là marker vá lỗ hổng PNJ) ⇒ nếu floor-guard bắn thật thì báo cáo paper hằng ngày sẽ KHÔNG thấy. Đã đổi markers thành 3 chuỗi khớp code thật. | CASE PNJ (user nêu 'thấy hiệu quả'): KHÔNG xác nhận được — PNJ chưa bao giờ trong rổ probe (0 dòng PNJ/18 journal), và case-study 07-13 (Taylor_20260713_075836) đã kết luận NGƯỢC LẠI: hệ thống không mua PNJ nhờ VÒNG CHỌN MÃ (cả 4 nguồn loại), không nhờ gate; replay còn lộ lỗ hổng poll-1 khiến slice đầu (= toàn bộ lệnh @NAV 1B) vẫn khớp tại sàn — chính lỗ hổng này sinh ra _floor_guard_buy (commit 74f5daa). Báo cáo đầy đủ: mike/agents/Taylor/research/extreme_regime_checkpoint_20260804.md

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/exec_main_*_journal.csv`
- `secrets/trading_bot_accounts.json (extreme_regime_enabled=true, chỉ paper main)`
- `stress_extreme_regime.py`
