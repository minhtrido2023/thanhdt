# Charter — Capitulation-sleeve shadow (DT5G × 8L washout) (`capitulation_shadow`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-06-10 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Sleeve dự trữ 50B nằm CASH, deploy vào rổ 8L quality+golden khi có tín hiệu washout (rule v2 2026-06-10, crisis_playbook.md §0b/§1), giữ 60 phiên rồi về cash — forward NAV là bằng chứng OOS cho overlay khi có khủng hoảng thật. Point-in-time: basket FREEZE tại ngày signal, không hindsight.

## 📅 Nghiệm thu / mốc kết thúc

EVENT-DRIVEN — đánh giá sau sự kiện washout THẬT đầu tiên (đến nay chưa có: mode CASH liên tục). Không có deadline lịch; sleeve rẻ, chạy chờ event.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) Sự kiện washout đầu tiên được xử lý đúng point-in-time (basket freeze tại signal date, entry price log đủ)
- ⏳ (pending) Fwd NAV sleeve qua trọn chu kỳ deploy→60 phiên→cash beat cash (kỳ vọng nghiên cứu: fwd60 +7%/81% winrate vùng WASHED-OUT)
- ⏳ (pending) Audit độc lập sau event trước khi cân nhắc wire overlay live

## ℹ️ Ghi chú vận hành

crisis_alert_push.py (cùng pipeline 15:30) là CÒI Telegram của cùng signal — chỉ kêu khi WATCH/STRONG, im lặng ngày thường → là alert vận hành, KHÔNG phải report trùng, giữ nguyên. VINTAGE: pt_capitulation_shadow.py query BQ LIVE (ticker_prune + dt5g_live), mà BQ chưa có close phiên T lúc 15:30 → last_date LUÔN = T-1. Đây là SÀN CẤU TRÚC, không phải stale: muốn asof=T phải chờ ingest ~17:30 / sync 23:45, tức dời report sang tối hoặc sáng hôm sau.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/pt_capitulation_state.json`
- `data/pt_capitulation_logs.csv + baskets.csv (pt_capitulation_shadow.py, papertrade_daily.sh)`
