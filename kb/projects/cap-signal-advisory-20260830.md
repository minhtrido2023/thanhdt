# CAP_SIGNAL advisory tracking — quyết định 2026-08-30 (decided_by: user)

## Quyết định
User duyệt (2026-08-30 21:10 ICT, job Taylor_20260830_141109) dùng **CAP_SIGNAL composite**
(DIVERGE VN-vs-EM + xác nhận DXY/UST) làm **tín hiệu ADVISORY THAM KHẢO**, không wire vào
production, với cơ chế tự tích luỹ case mới + tự đề xuất nâng cấp khi đủ số lượng.

**Nguồn gốc**: `agents/Taylor/research/diverge_indicator_strategy_backtest_round2_20260830.md`
— quant-skeptic **CONFIRMED (medium confidence)** round 2: dấu dương thật, sống sót
leave-one-out (18/18 không đổi dấu, dù mất 46-57% giá trị khi loại top episode), IS/OOS đều
dương. **Killer objection còn đứng**: N thật chỉ **~6 cụm macro độc lập trong 15 năm** —
quá mỏng cho DSR/PBO chính thức → KHÔNG đủ điều kiện wire kỹ thuật.

## Định nghĩa composite (PRE-REGISTERED, KHÔNG re-tune)
```
diverge     = EM_dd60 <= -8%  AND  VNI_dd60 >= -3%
cap_signal  = diverge  AND  (DXY_mom60 >= 5%  OR  TNX(UST10Y) >= 3.0)
```
Khớp `production_mechanism_2009_2018_20260830.md` §B.2 và
`agents/Taylor/exp_insider/cap_signal_grid_test_round2.py`.

## 1. Khả thi dữ liệu SỐNG — verify 2026-08-30
- `data/tier2_macro_panel.csv` (nguồn backtest gốc) **ĐÓNG BĂNG 2026-05-15**, không cron refresh
  — không dùng được cho advisory sống. Không phải "không khả thi" nói chung — chỉ file cache cũ
  chết, pipeline gốc (`tier2_global_proxies.py`, dùng `yfinance`) vẫn chạy được.
- **VNI** (VNINDEX Close): `tav2_bq.ticker` — verified sống, dữ liệu tới 2026-08-28 (2 ngày trễ
  cuối tuần, bình thường theo lịch sync 23:45 ICT hàng ngày trong tuần).
- **EEM / DXY (`DX-Y.NYB`) / TNX (`^TNX`)**: `yfinance` qua `$DNA_PYEXE`
  (`/home/trido/thanhdt/wc_venv/bin/python`, đã có `yfinance==1.4.1` sẵn) — verified sống 2026-08-30,
  kéo được 10 ngày gần nhất mỗi mã. **Bẫy đã xử lý**: dòng ngày CUỐI có thể NaN nếu phiên Mỹ
  chưa đóng cửa tại giờ fetch (VN đi trước múi Mỹ) — script `dropna` trước khi tính rolling.
- **Kết luận**: khả thi đầy đủ, KHÔNG bị chặn ở bước 1.

## 2. Implementation
`mike/agents/Taylor/cap_signal_advisory_check.py` — tính composite từ dữ liệu SỐNG (BQ + yfinance,
không đọc `tier2_macro_panel.csv`), fire → ghi 1 dòng vào registry
`kb/data_registry/market-state/cap_signal_advisory_log.csv` (đã có OKF entry riêng — xem
`kb/data_registry/market-state/cap_signal_advisory_log.md` cho schema/bẫy đầy đủ).

Cụm hoá: fire cách fire gần nhất **<=60 ngày lịch** → cùng cụm; ngược lại → cụm mới. N cho
ngưỡng nâng cấp = `cluster_id.nunique()` (khớp cách đếm N=6 trong nghiên cứu, đơn vị là cụm
macro độc lập chứ không phải số lần fire).

**Test 2026-08-30 (dry-run + print-block)**: trạng thái hiện tại = **quiet** (không fire).
EM_dd60=-5,1~5,7% (chưa chạm -8%), VNI_dd60=-2,4~2,5%, DXY_mom60≈0%, TNX≈4,67-4,72 (đã > 3.0
nhưng điều kiện `diverge` chưa thoả nên composite không fire). Registry hiện N_clusters=0 (chưa
có case sống nào — 6 cụm trong nghiên cứu đều là lịch sử 2011-2026 đã biết).

## 3. Ngưỡng nâng cấp
**N_clusters >= 10** (tăng từ 6 hiện có — tham khảo cỡ mẫu tối thiểu thường dùng để bắt đầu chạy
DSR/PBO có ý nghĩa theo `.claude/skills/quant-research/`; 6 quá mỏng, 10-12 là ngưỡng khởi điểm
hợp lý). Khi `n_independent_clusters() >= 10`, script tự bắn 1 bus **`question`**
(topic `cap-signal-upgrade-threshold-reached`) đề xuất quant-skeptic + user xem xét wire —
**KHÔNG tự động wire**. Do tốc độ tích luỹ lịch sử (~6 cụm/15 năm ≈ 1 cụm mỗi 2,5 năm), ngưỡng
này realistically mất nhiều năm để chạm — đúng tinh thần "advisory dài hạn", không phải cơ chế
sẽ tự kích hoạt sớm.

## 4. Hiển thị hàng ngày/tuần
**CHƯA wire vào `dna_report.py`/cadence sản xuất trong job này** — cố ý, để tách rủi ro khỏi
report pipeline đang chạy production. Đề xuất tái dùng pattern §6b `coding_guidelines.md`
(`build_dt_gate_line()`/`build_value_radar_line()`, DISPLAY-ONLY): hàm
`build_advisory_line()` đã có sẵn trong `cap_signal_advisory_check.py`, chỉ cần
`from cap_signal_advisory_check import build_advisory_line` trong `dna_report.py` khi user
duyệt wire hiển thị. KHÔNG cần cron riêng — chạy 1 lần/ngày cùng nhịp report EOD hiện có là đủ
(tần suất W=60-phiên nên không cần realtime).

## Ranh giới
Không đụng `custom_basket.py`/`signal_v11_sql.py`/`macro_state_live.py`/`trading_rules.json`/
`plan.py`/`executor.py`. Registry ghi vào file riêng, không ghi đè bất kỳ file production nào.
