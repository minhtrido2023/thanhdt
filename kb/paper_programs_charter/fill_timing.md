# Charter — Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45) (`fill_timing`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-07-01 · **Kết thúc dự kiến:** 2026-07-31

## 🎯 Mục đích

Edge backtest (BUY 11:15 rẻ hơn open +17.6bps t=12.0; SELL tại open +11.8bps vs ATC) có capture được NET-of-noise trên fill thật không? (noise 110-220bps >> edge 17bps → cần nhiều tuần)

## 📅 Nghiệm thu / mốc kết thúc

Checkpoint ~cuối tháng 7 (cần ~3-4 tuần fill tích lũy)

## ✅ Tiêu chí GO/NO-GO

- ✅ (pass) BUY window adherence cao (lệnh dồn 10:45-11:15) — ĐO 2026-08-11 (job Taylor_20260811_091002) bằng TIMESTAMP thật, không bằng string-match nhãn: 5 phiên probe 10:46 có lệnh MUA (07-14/07-16/07-21/07-23/08-11), 28/28 lệnh đặt trong 10:45-11:15, 28/28 khớp. ĐẠT ngưỡng ≥5 phiên. ⚠️ 08-11 là phiên HYBRID ĐẦU TIÊN — 4 phiên kia là cơ chế gom-cửa-sổ CŨ.
- ✅ (pass) SELL window adherence cao (lệnh tại open 09:15-09:45) — ĐO 2026-08-11 bằng timestamp: 10 phiên probe 09:15 có lệnh BÁN (07-13→08-05), 50/50 lệnh trong 09:15-09:45, 50/50 khớp. Vượt xa ngưỡng ≥5.
- ✅ (pass) 0 rejects/fails (hoặc từng cái được giải thích) — 431 lỗi = 386 PLACE_FAIL + 45 ATC_FAIL, TOÀN BỘ ngày 2026-07-30, 1 root cause (PaperBroker.place_order thiếu cash_only), fix+verify cùng ngày, incident 2026-07/2026-07-30-paper-trading-report-3-root-causes.md. 0 lỗi trong 9 phiên kể từ 07-31. Ngoài ra 18 GHOST_ORDER (07-08/07-09/08-07) = guard idempotency khi chạy LẠI harness trong cùng ngày với state mới — đúng thiết kế, không phải reject của broker.
- ✅ (pass) BUY fill không tệ hơn open đáng kể; SELL không thấp hơn open đáng kể — SANITY ĐẠT (KHÔNG phải bằng chứng edge). Đo 2026-08-11 từ journal fill + Open BQ ticker_1m: BUY in-window day-mean −1,7 bps vs open (n=4 ngày, sd_ngày 97,8, t=−0,03); SELL in-window −9,1 bps (n=9 ngày, sd_ngày 6,1) ≈ dưới 1 bước giá (tick 50/22.600 = 22 bps). Không có dấu hiệu fill tệ hơn open một cách hệ thống ⇒ đạt tiêu chí 'không tệ hơn đáng kể'. ⚠️ EDGE 17,6 bps KHÔNG đo được: se ngày 48,9 bps. ⚠️ Mục C của probe execution_quality_review.py KHÔNG BAO GIỜ tính được cái này (đọc dnse_raw_*.jsonl mà paper không bao giờ ghi) — số trên đo thủ công.
- ⏳ (pending) quant-skeptic → user sign-off mới flip fill_timing_live_gate — 4/4 gate cơ học ĐÃ ĐẠT 2026-08-11 ⇒ hết vướng về dữ liệu, chỉ còn quyết định. KHUYẾN NGHỊ Taylor: CHƯA flip. Cái sẽ lên live là HYBRID (bật paper 2026-08-10) nhưng mới có ĐÚNG 1 phiên paper (08-11), trong khi 5 phiên của gate 1 là 4 cũ + 1 hybrid; và qty probe (100 cp) quá nhỏ nên hybrid khớp trọn ở block đầu — cơ chế TRẢI BLOCK chưa từng được thực chứng trên paper. Đề xuất: gom thêm 4 phiên BUY hybrid (cron T3/T5: 08-13, 08-18, 08-20, 08-25) → quant-skeptic ~08-26 → user sign-off. User có quyền chốt sớm nếu coi gate cơ học là bất biến theo cơ chế.

## ℹ️ Ghi chú vận hành

Mechanics (window adherence) đo được sớm; EDGE bps cần nhiều tuần — không gate sớm trên bps. FIX 2026-08-10 (job Taylor_20260810_032034, xác nhận độc lập Mike): gate 1 (BUY-window adherence) đứng im 4/5 từ 2026-07-23 (18 ngày) vì cron bằng chứng (T3/T5 10:46 ICT) trúng đúng 2 ngày net-SELL của BUY_VALUE_FACTOR gốc — P(có lệnh mua)=0 tuyệt đối, không phải mẫu chưa đủ. Đã xoay BUY_VALUE_FACTOR 1 ngày trong mike/bin/paper_main_probe_plan.py (up-day T2/T3/T5), verify selfcheck 6/6 PASS. ETA dự kiến: phiên thứ 5 khả năng cao 2026-08-11, chắc chắn tới 2026-08-13 → quant-skeptic + user sign-off ~2026-08-14, chậm nhất 2026-08-17. Chi tiết: mike/agents/Taylor/research/fill_timing_eta_investigation_20260810.md. CẬP NHẬT 2026-08-10 (sau khi mốc ETA/gate-1 ở trên vẫn đang chạy độc lập): user chốt thiết kế HYBRID (trải block trong khung thuận lợi thay vì gom 1 điểm, nguồn: research/twap_vs_window_execution_20260804.md) và đã BẬT TRÊN PAPER (fill_timing_hybrid_enabled=True, commit WorkingClaude 0f54cb7+717307f, job Taylor_20260810_034544 + _051847, 5 vòng quant-skeptic — 3 REFUTED tìm ra lỗi thật (giao thoa EXTREME, deadlock arm, deadlock qua quote lỗi), vòng cuối CONFIRMED cao). fill_timing_live_gate VẪN True — không account live nào bị ảnh hưởng. Theo dõi phiên paper đầu tiên (account main đã có sẵn extreme_regime_enabled+gap_adaptive_enabled nên cả 3 cơ chế chạy chung lần đầu). Chi tiết: mike/agents/Taylor/research/hybrid_fill_timing_implementation_20260810.md. CHECKPOINT 2026-08-11 (job Taylor_20260811_091002): đã kiểm 5/5 gate bằng dữ liệu thật (journal exec_main_*, không suy đoán) — gate 1-4 PASS, gate 5 pending vì lý do THIẾT KẾ chứ không phải thiếu dữ liệu (hybrid mới 1 phiên paper; block-spreading chưa được thực chứng vì probe qty=100 khớp trọn block đầu). Cũng xác nhận lại 2 hạn chế của công cụ đo: (a) nhãn ft:in-window = 'mult==1.0' chứ KHÔNG phải 'nằm trong cửa sổ' (9 ca đếm dư: 6× 07-07 14:19 luật phiên chiều + 3× 07-15 GAP_OPEN_OVERRIDE) — mọi kết luận adherence phải đo bằng timestamp; (b) mục C của execution_quality_review.py cấu trúc KHÔNG tính được vs-open cho paper (đọc dnse_raw mà PaperBroker không ghi). Chi tiết: mike/agents/Taylor/research/fill_timing_checkpoint_20260811.md.

## 🔍 Nguồn dữ liệu kiểm chứng

- `execution_quality_review.py`
- `data/execution_logs/exec_*_journal.csv (ft-notes)`
