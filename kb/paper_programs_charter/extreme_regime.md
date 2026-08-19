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
- ✅ (pass) ZERO false-trigger qua ~4 tuần benign trên account paper main — 2026-08-19 (job Taylor_20260819_110954) — ĐẠT, kèm caveat phạm vi bắt buộc đọc kèm. 25/20 phiên EVIDENCE (quy tắc: journal có >=1 PLACE thành công; 28 file 07-07→08-19 trừ 07-08/07-09 chỉ GHOST_ORDER và 07-30 toàn PLACE_FAIL). Quy tắc này tái lập ĐÚNG con số 15 của checkpoint 08-04 ⇒ không đổi định nghĩa giữa chừng. Phiên thứ 20 = 2026-08-11. 0 marker/25 phiên (quét chuỗi CHÍNH XÁC EXTREME_PAUSE / EXTREME_FLOOR_GUARD / 'EXTREME_DOWN sell-to-floor' ở CẢ event lẫn note; kiểm lỏng 'EXTREME' cũng 0). Gate verified ARMED qua load_config()+load_accounts(): main(paper) extreme_regime_enabled=True, cả 3 account live = False ⇒ '0 marker' KHÔNG rỗng. Buy-path 20/25 phiên (5 phiên chỉ-BÁN: 07-31/08-04/08-06/08-12/08-19). Trigger (ii) sạch M5 22/25 (loại 07-07/07-10/07-13; fix Winston commit 16309166 lúc 2026-07-13 21:44:33+07, SAU phiên 07-13). ⚠️ CAVEAT PHẠM VI — ĐO ĐƯỢC, không còn là văn xuôi: (A) trigger (i) cận sàn CHƯA TỪNG trong tầm với — trên toàn bộ 242 dòng PLACE có giá, headroom trên sàn NHỎ NHẤT = 4,43% vs extreme_band 3,00%, 0/242 dòng trong band; 3 phiên rổ probe THỰC SỰ vào band trong ngày (07-15 FPT low +2,17% trên sàn, 07-20 HPG +0,88%, 07-22 HDB +1,34%) nhưng lúc executor còn sống giá cách sàn 7,03-7,73%. (B) trigger (ii) 3-sigma phần lớn KHÔNG THỂ với tới do CẤU TRÚC: tuổi thọ executor TRUNG VỊ 20 GIÂY, 20/28 phiên chạy <15' (=dip_window_min) ⇒ _r15 trả None ⇒ fail-safe False; r15 chỉ tính được 49/242 dòng, giá trị âm nhất từng thấy −0,90% vs ngưỡng LỎNG NHẤT −2,42% (VNM tại rvol_20d min 0,807%) ⇒ mới đi ~37% quãng đường. ⇒ Bằng chứng là MỘT CHIỀU: chứng minh gate không kêu bậy khi lành tính, KHÔNG chứng minh gate xử lý đúng khi sập (phần đó hiện chỉ có stress-injection gate 1 bảo chứng). Chi tiết: mike/agents/Taylor/research/paper_gates_checkpoint_20260819.md
- ✅ (pass) Không can thiệp NORMAL-path — 2026-08-04 (job Taylor_20260804_124404): 0 marker/15 phiên ⇒ 0 lần can thiệp thực tế. Cô lập code: _extreme_regime/_floor_guard_buy/_extreme_slice_mult đều return sớm khi extreme_regime_enabled=False; stress section 6g resolve cfg THẬT của SpaceX/ZaloPay qua load_config()/load_accounts() và chứng minh trực tiếp slice mua vẫn đặt bình thường trên live với cùng quote PNJ khoá sàn. | 2026-08-19 (job Taylor_20260819_110954): xác nhận lại trên 25 phiên evidence — vẫn 0 marker ⇒ 0 lần can thiệp thực tế.
- ⏳ (pending) User sign-off trước khi bật live — 2026-08-19 (job Taylor_20260819_110954): KHUYẾN NGHỊ trình user xin chữ ký — 3/4 gate đã pass. BẮT BUỘC trình kèm nguyên văn caveat phạm vi ở gate 2 (cả hai nhánh trigger chưa từng tới gần ngưỡng: 4,43% vs band 3,00%; −0,90% vs −2,42%). Taylor KHÔNG tự bật live. Nếu user muốn evidence mạnh hơn cho nhánh (ii) trước khi ký: phải kéo dài tuổi thọ executor probe (>=20-30' thay vì trung vị 20s) — đó là thay đổi HARNESS, không phải thay đổi gate.

## ℹ️ Ghi chú vận hành

Evidence tích lũy CHỈ khi executor chạy phiên trên account main — 0 phiên = 0 evidence, không tính là PASS. Từ 2026-07-07: probe harness chạy paper main mỗi ngày T2-T6 (cron 08:52 sinh plan mike/bin/paper_main_probe_plan.py, executor 09:10 + 13:05, log mike/logs/run_bot_main_*.log). | 2026-08-04 (job Taylor_20260804_124404) — CHECKPOINT: 15/20 phiên evidence (thiếu 5). Luồng evidence đứng 8 ngày 07-28→08-04 do bug netting probe harness, ĐÃ GỠ sáng 08-04 (job Taylor_20260804_094514) → chạy lại từ phiên 08-05, ước đủ 20 phiên ~2026-08-11 (~08-14 nếu muốn 20 phiên sạch cho CẢ nhánh trigger ii). Phiên 07-30 MẤT HẲN (386 PLACE_FAIL: PaperBroker.place_order() thiếu kwarg cash_only, đã fix commit 2af4abd). 07-31 + 08-04 chỉ có lệnh SELL (dư netting) ⇒ buy-path KHÔNG được đánh giá 2 phiên đó. | ⚠️ SỬA LỖI REGISTRY: probe.markers cũ khai EXTREME_SELL/EXTREME_UP (KHÔNG tồn tại trong code, chỉ có trong fixture paper_report_render_selfcheck.py) và THIẾU EXTREME_FLOOR_GUARD (marker THẬT, executor.py:1026, chính là marker vá lỗ hổng PNJ) ⇒ nếu floor-guard bắn thật thì báo cáo paper hằng ngày sẽ KHÔNG thấy. Đã đổi markers thành 3 chuỗi khớp code thật. | CASE PNJ (user nêu 'thấy hiệu quả'): KHÔNG xác nhận được — PNJ chưa bao giờ trong rổ probe (0 dòng PNJ/18 journal), và case-study 07-13 (Taylor_20260713_075836) đã kết luận NGƯỢC LẠI: hệ thống không mua PNJ nhờ VÒNG CHỌN MÃ (cả 4 nguồn loại), không nhờ gate; replay còn lộ lỗ hổng poll-1 khiến slice đầu (= toàn bộ lệnh @NAV 1B) vẫn khớp tại sàn — chính lỗ hổng này sinh ra _floor_guard_buy (commit 74f5daa). Báo cáo đầy đủ: mike/agents/Taylor/research/extreme_regime_checkpoint_20260804.md | 2026-08-19 (job Taylor_20260819_110954) — CHECKPOINT ĐẠT NGƯỠNG: 25/20 phiên evidence, 0 marker. HAI phát hiện mới định lượng hoá caveat phạm vi (trước đây chỉ là văn xuôi): (A) 0/242 dòng PLACE nằm trong extreme_band, min headroom 4,43%; 3 phiên (07-15 FPT/07-20 HPG/07-22 HDB) giá CÓ vào band trong ngày nhưng executor đã tắt (lúc chạy giá cách sàn 7,03-7,73%). (B) executor probe sống TRUNG VỊ 20 GIÂY, 20/28 phiên <15' ⇒ _r15=None ⇒ trigger (ii) fail-safe False do cấu trúc, không phải do thị trường lành tính; r15 đo được 49/242, âm nhất −0,90% vs ngưỡng lỏng nhất −2,42%. Hệ quả: caveat M5 (3 phiên rvol stale) là mối lo NHỎ so với (B). Muốn evidence trigger (ii) có nghĩa phải sửa HARNESS (kéo dài phiên), không phải sửa gate. Báo cáo: mike/agents/Taylor/research/paper_gates_checkpoint_20260819.md

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/exec_main_*_journal.csv`
- `secrets/trading_bot_accounts.json (extreme_regime_enabled=true, chỉ paper main)`
- `stress_extreme_regime.py`
