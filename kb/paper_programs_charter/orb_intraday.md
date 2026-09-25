# Charter — ORB intraday VN30F (ring-fenced) (`orb_intraday`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-06-09 · **Kết thúc dự kiến:** mở (event-anchored)

## 🎯 Mục đích

Chiến lược opening-range-breakout VN30F (sign OR 09:00-09:30 → giữ tới 14:30, no stop) có sống sót qua regime BẤT LỢI không? Verdict quant-skeptic 2026-07-01: NO-integrate — n≈17-21 phiên toàn NEUTRAL uptrend benign, Sharpe cao là artifact mẫu nhỏ; walk-forward 2024 lỗ cả năm chưa được giải quyết. Paper tích lũy tiếp để có bằng chứng đủ mạnh.

## 📅 Nghiệm thu / mốc kết thúc

Re-eval lần sau CHỈ chạy khi ĐỦ CẢ HAI điều kiện (chốt 2026-09-25, user duyệt): (a) đã xuất hiện ít nhất MỘT đoạn DT5G ra khỏi NEUTRAL — tức BEAR hoặc CRISIS — trong cửa sổ paper (hiện 0 đoạn: 75/75 phiên NEUTRAL, zero transition); VÀ (b) số phiên tiến tới khoảng 290–430 (hiện 75), là số cần để đạt power t=1,64–2,0 ở effect size đã đo (+9,06bps/phiên, sd 93,6bps). Thiếu một trong hai ⇒ KHÔNG re-eval. Lý do: re-eval 2026-09-25 (job Taylor_20260925_052050) với N=74 đã cho verdict B = CONTINUE PAPER, và chạy lại trên cùng một regime với N tương tự sẽ ra kết luận y hệt — lặp lại chỉ tốn công. Không có deadline lịch: điều kiện là REGIME + POWER, không phải số ngày.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) ≥60 phiên paper GỒM ít nhất một đoạn DT5G NGOÀI NEUTRAL (BEAR/CRISIS). Số phiên: ĐẠT (75 @2026-09-25). Điều kiện regime: KHÔNG ĐẠT — 75/75 phiên NEUTRAL, zero transition, state_raw cũng NEUTRAL (không lần nào macro cap can thiệp) — re-eval 2026-09-25 job Taylor_20260925_052050 → verdict B = CONTINUE PAPER; lưu ý nhãn DT5G trước 2026-07-24 là backfill 1 lần — xem Ghi chú vận hành
- ❌ (fail) Walk-forward 2024 full-year loss được giải thích / không lặp lại trong forward window → FAIL 2026-09-25: config GỐC (cái duy nhất từng validate: exit 14:00, stop 0,7%, |OR|≥0,2%, TC 2,5bps) chạy forward trên đúng 74 phiên live cho n=35, mean −11,20bps/phiên, Sharpe −3,05, cum −3,90% — cùng dấu với lỗ 2024 (−5,93bps, −4,50%) và lớn hơn tính trên mỗi phiên. Khoản lỗ KHÔNG được giải thích và ĐÃ lặp lại — artifact agents/Taylor/research/orb_reeval_20260925/orig_config_forward.md (job Taylor_20260925_095910 item 2/6); giới hạn: n=35, p=0,264, CI chứa 0 ⇒ chắc chắn là DẤU, không phải độ lớn. User đã duyệt TIẾP TỤC PAPER, đây KHÔNG phải quyết định NO-GO
- ⏳ (pending) Hạ tầng phái sinh: tài khoản VSD margin + đường thực thi VN30F (bot hiện CASH-EQUITY ONLY — chưa thể live dù edge có thật)
- ⏳ (pending) Nếu tích hợp: sleeve RIÊNG vốn riêng ≤5% NAV + quant-skeptic + user sign-off

## ℹ️ Ghi chú vận hành

Section ORB trong Telegram 18:00 (telegram_recommend.py) đã GỠ 2026-07-07 để hết trùng — report này là kênh duy nhất. Verdict đầy đủ: bus event Taylor 2026-07-01 (job Taylor_20260701_113638). ⚠️ NHÃN DT5G TRƯỚC 2026-07-24 LÀ BACKFILL MỘT LẦN, KHÔNG PHẢI NHÃN REAL-TIME. Đo trực tiếp trên `tav2_bq.vnindex_5state_dt5g_live` ngày 2026-09-25: 3.131/3.174 dòng (98,6%), phủ 2014-01-02→2026-07-23, đều mang asof_date = 2026-07-30 — tức được viết trong MỘT batch; chỉ từ 2026-07-24 trở đi bảng mới được ghi tăng dần theo phiên. Hệ quả: mọi nghiên cứu điều kiện theo nhãn DT5G LỊCH SỬ — gồm chính gate criterion #1 ('regime') của re-eval 2026-09-25 và bảng edge-theo-regime trong FINDINGS.md — thực chất là điều kiện trên một construct FULL-SAMPLE, không phải nhãn đã có sẵn real-time tại thời điểm đó. Đây KHÔNG phải look-ahead trong chuỗi giá (đã kiểm: lag nhãn 1-2 ngày không đổi kết luận), nhưng nhãn regime KHÔNG point-in-time — đừng đọc nó như bằng chứng 'hệ thống đã nhìn thấy regime này ngay lúc đó'. Nguồn: FINDINGS.md C7 (job Taylor_20260925_052050) + đo lại bằng bq trong job Taylor_20260925_095910.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/orb_pt_status.json`
- `data/orb_pt_log.csv (orb_pt.py, papertrade_daily.sh 15:30 ICT)`
