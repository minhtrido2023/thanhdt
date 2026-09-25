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
- ❌ (fail) Walk-forward 2024 full-year loss được giải thích / không lặp lại trong forward window → vẫn FAIL (viết lại 2026-09-25 cho ĐÚNG ĐỐI TƯỢNG, job Taylor_20260925_111203). (1) ĐÍNH CHÍNH ĐỐI TƯỢNG: khoản lỗ 2024 thuộc config GỐC (exit 14:00, stop 0,7%, |OR|≥0,2%, TC 2,5bps) — config đó ĐÃ BỊ THAY THẾ và forward-test riêng của nó vẫn FAIL (n=35, −11,20bps/phiên, Sharpe −3,05, cum −3,90%). Config ĐANG CHẠY trong orb_pt.py KHÁC trên 4 trục (OR tới 09:30, exit 14:30, KHÔNG stop, KHÔNG lọc |OR|) — số paper thật đang đo config này, không phải config gốc. (2) CONFIG ĐANG CHẠY, trên cửa sổ dữ liệu vendor cũ (vnstock, 2023-09-11→2026-09-25, 745 phiên): KHÔNG có năm lỗ nào (4/4 năm dương), Sharpe 1,59, MaxDD −7,8%, PSR 0,9967, DSR(N=20) 0,9234 (vừa dưới ngưỡng fleet 0,95). (3) NHƯNG với dữ liệu XA HƠN (FiinProX/FiinX MCP, +389 phiên 2022-02-17→2023-09-08; tape ghép 1.129 trade 2022-02→2026-09): xuất hiện NĂM LỖ — 2023 −14,2% (Sharpe −0,95), trong đó đoạn 2023-01..09 lỗ −12,99bps/phiên (Sharpe −2,10, cum −19,7%). Drawdown sâu nhất −30,47% kéo dài 206 phiên (2022-10-27→2023-09-06) — KẾT THÚC ĐÚNG 3 PHIÊN TRƯỚC khi cửa sổ dữ liệu cũ bắt đầu. Toàn mẫu: Sharpe 0,89, MaxDD −31,8%, PSR 0,9679, **DSR(N=20) 0,4914** (trước: 0,9234). ⇒ tiêu chí 'lỗ không lặp lại' KHÔNG đạt: nó chỉ có vẻ đạt vì cửa sổ dữ liệu cũ bắt đầu ngay sau một drawdown 30%. — Artifact: agents/Taylor/research/orb_deployed_config_validation_20260925/ (validate config đang chạy, job Taylor_20260925_103217) + agents/Taylor/research/orb_fiinx_vn30f1m_20260925/ (mở rộng tape, job Taylor_20260925_111203, commit mike 220c70bd). GIỚI HẠN DỮ LIỆU CÒN LẠI: phủ 4,6/9,1 năm đời hợp đồng VN30F1M (2017-08-10→nay) — vendor FiinProX KHÔNG có bar 1 phút trước 2022-02-17 (đã đo trực tiếp: 2022-02-16 rỗng, 2022-02-17 có 257 bar; 2018 và COVID-2020 rỗng cả với VN30F1M lẫn mã hợp đồng tháng), vnstock không có trước 2023-09-11. Vẫn KHÔNG test được sụt 2018 và sập COVID 2020. ĐỘ TIN CỦA PHẦN MỞ RỘNG: đối soát 76 phiên trùng hai vendor — c_first/entry/max-high khớp 76/76 tuyệt đối, dấu vị thế khớp 75/75, nhiễu vendor ở mức kết quả ~0,6bps/phiên (nhỏ hơn 1 bậc độ lớn so với hiệu ứng −13bps tìm thấy). Quirk duy nhất: FiinX thu gọn bar 14:30 về một giá ⇒ báo cáo dùng exit 14:29 cho CẢ HAI đoạn (trên đoạn vnstock: Sharpe 1,57 với 14:29 vs 1,58 với 14:30). ĐỌC CẨN THẬN: khác biệt giữa hai đoạn KHÔNG có ý nghĩa thống kê (Welch p=0,266; cần ~2.500 quan sát/nhóm để phát hiện delta 8,7bps với sd 110bps) ⇒ KHÔNG kết luận 'regime đã đổi'; kết luận đúng là ước lượng mean hợp nhất thấp hơn nhiều và CI rộng hơn nhiều so với con số 745-phiên. CHƯA TỰ SỬA (cần Mike/user quyết): điều kiện re-eval ở end_or_trigger (~290–430 phiên) tính theo effect size +9,06bps/phiên đo trên cửa sổ cũ; với ước lượng hợp nhất +6,16bps con số phiên cần sẽ LỚN HƠN đáng kể. Không tự đổi trigger trong job này.
- ⏳ (pending) Hạ tầng phái sinh: tài khoản VSD margin + đường thực thi VN30F (bot hiện CASH-EQUITY ONLY — chưa thể live dù edge có thật)
- ⏳ (pending) Nếu tích hợp: sleeve RIÊNG vốn riêng ≤5% NAV + quant-skeptic + user sign-off

## ℹ️ Ghi chú vận hành

Section ORB trong Telegram 18:00 (telegram_recommend.py) đã GỠ 2026-07-07 để hết trùng — report này là kênh duy nhất. Verdict đầy đủ: bus event Taylor 2026-07-01 (job Taylor_20260701_113638). ⚠️ NHÃN DT5G TRƯỚC 2026-07-24 LÀ BACKFILL MỘT LẦN, KHÔNG PHẢI NHÃN REAL-TIME. Đo trực tiếp trên `tav2_bq.vnindex_5state_dt5g_live` ngày 2026-09-25: 3.131/3.174 dòng (98,6%), phủ 2014-01-02→2026-07-23, đều mang asof_date = 2026-07-30 — tức được viết trong MỘT batch; chỉ từ 2026-07-24 trở đi bảng mới được ghi tăng dần theo phiên. Hệ quả: mọi nghiên cứu điều kiện theo nhãn DT5G LỊCH SỬ — gồm chính gate criterion #1 ('regime') của re-eval 2026-09-25 và bảng edge-theo-regime trong FINDINGS.md — thực chất là điều kiện trên một construct FULL-SAMPLE, không phải nhãn đã có sẵn real-time tại thời điểm đó. Đây KHÔNG phải look-ahead trong chuỗi giá (đã kiểm: lag nhãn 1-2 ngày không đổi kết luận), nhưng nhãn regime KHÔNG point-in-time — đừng đọc nó như bằng chứng 'hệ thống đã nhìn thấy regime này ngay lúc đó'. Nguồn: FINDINGS.md C7 (job Taylor_20260925_052050) + đo lại bằng bq trong job Taylor_20260925_095910.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/orb_pt_status.json`
- `data/orb_pt_log.csv (orb_pt.py, papertrade_daily.sh 15:30 ICT)`
