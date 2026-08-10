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

- ⏳ (pending) BUY window adherence cao (lệnh dồn 10:45-11:15)
- ⏳ (pending) SELL window adherence cao (lệnh tại open 09:15-09:45)
- ⏳ (pending) 0 rejects/fails (hoặc từng cái được giải thích)
- ⏳ (pending) BUY fill không tệ hơn open đáng kể; SELL không thấp hơn open đáng kể
- ⏳ (pending) quant-skeptic → user sign-off mới flip fill_timing_live_gate

## ℹ️ Ghi chú vận hành

Mechanics (window adherence) đo được sớm; EDGE bps cần nhiều tuần — không gate sớm trên bps. FIX 2026-08-10 (job Taylor_20260810_032034, xác nhận độc lập Mike): gate 1 (BUY-window adherence) đứng im 4/5 từ 2026-07-23 (18 ngày) vì cron bằng chứng (T3/T5 10:46 ICT) trúng đúng 2 ngày net-SELL của BUY_VALUE_FACTOR gốc — P(có lệnh mua)=0 tuyệt đối, không phải mẫu chưa đủ. Đã xoay BUY_VALUE_FACTOR 1 ngày trong mike/bin/paper_main_probe_plan.py (up-day T2/T3/T5), verify selfcheck 6/6 PASS. ETA dự kiến: phiên thứ 5 khả năng cao 2026-08-11, chắc chắn tới 2026-08-13 → quant-skeptic + user sign-off ~2026-08-14, chậm nhất 2026-08-17. Chi tiết: mike/agents/Taylor/research/fill_timing_eta_investigation_20260810.md. CẬP NHẬT 2026-08-10 (sau khi mốc ETA/gate-1 ở trên vẫn đang chạy độc lập): user chốt thiết kế HYBRID (trải block trong khung thuận lợi thay vì gom 1 điểm, nguồn: research/twap_vs_window_execution_20260804.md) và đã BẬT TRÊN PAPER (fill_timing_hybrid_enabled=True, commit WorkingClaude 0f54cb7+717307f, job Taylor_20260810_034544 + _051847, 5 vòng quant-skeptic — 3 REFUTED tìm ra lỗi thật (giao thoa EXTREME, deadlock arm, deadlock qua quote lỗi), vòng cuối CONFIRMED cao). fill_timing_live_gate VẪN True — không account live nào bị ảnh hưởng. Theo dõi phiên paper đầu tiên (account main đã có sẵn extreme_regime_enabled+gap_adaptive_enabled nên cả 3 cơ chế chạy chung lần đầu). Chi tiết: mike/agents/Taylor/research/hybrid_fill_timing_implementation_20260810.md.

## 🔍 Nguồn dữ liệu kiểm chứng

- `execution_quality_review.py`
- `data/execution_logs/exec_*_journal.csv (ft-notes)`
