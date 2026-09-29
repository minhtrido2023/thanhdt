# 2026-09-03 — preflight false-warn "macro_health file cũ 21.2h / daily_refresh chưa chạy tối qua?" trong kỳ nghỉ Quốc khánh

**What happened.** ops_health_check 12:45 (account=ZaloPay) flag
`⚠️ macro_health OK (HEALTHY) nhưng file cũ 21.2h — daily_refresh chưa chạy tối qua?`.
Không có gì hỏng: nghỉ Quốc khánh 2026 nghỉ 31/08 + 01/09 + 02/09 (thị trường đóng),
`daily_refresh_v34b_linux.sh` VẪN chạy đúng 18:30 ICT cả 2 ngày và abort ĐÚNG ở step [0]
(`ticker_prune has 0 tickers ... after 6 attempts` — bằng chứng:
`data/refresh_v34b_linux_2026-09-01.log`, `..._2026-09-02.log`), nên `macro_health.json`
đứng yên hợp lệ ở bản 02/09 15:30 (papertrade ghi), macro_now.date=2026-08-28 = phiên
giao dịch gần nhất thật.

**Root cause (2 lỗi độc lập, cùng 1 dòng cảnh báo).**
1. **Ngưỡng tuổi theo NGÀY LỊCH** — `preflight_check.sh` §3 dùng `_max_age_h=20` (riêng
   thứ Hai 68h). Ngưỡng chỉ trừ cuối tuần, không trừ nghỉ lễ ⇒ mọi kỳ nghỉ dài đều
   false-warn. **Đúng cùng lớp lỗi đã vá hôm trước cho `ticker_prune`** (commit `0b83f507`,
   cùng kỳ nghỉ này) — vá 1 call-site không chặn được call-site thứ 2 trong cùng file.
2. **Đoán nguyên nhân (vi phạm coding_guidelines §29)** — thông điệp hardcode
   "daily_refresh chưa chạy tối qua?" trong khi script chưa hề đọc log refresh nào.
   Chẩn đoán SAI sự thật: nó đã chạy, đã abort có lý do, và lý do nằm sẵn trong log.

**Fix** (commit `81cc0428`, mike repo, chỉ `bin/preflight_check.sh`):
- Ngưỡng = số giờ trôi qua kể từ **18:30 ICT của PHIÊN GIAO DỊCH gần nhất đã qua giờ đó**
  + 3h ân hạn (step [0] có thể chờ tới ~1,5h trước khi macro_healthcheck ở step [14] ghi
  file). Lịch nghỉ lấy từ `trading_bot.vn_market.is_holiday` — cùng nguồn
  `bq_freshness_check.sh` và fix `0b83f507` dùng. Không tra được lịch nghỉ → fallback
  ngưỡng ngày lịch cũ **kèm lỗi thật đọc được**, không im lặng.
- Nhánh WARN trích `tail -1` của `data/refresh_v34b_linux_*.log` mới nhất thay vì đoán.

**Verify.** preflight ZaloPay 03/09 12:47 → `✅ macro_health: HEALTHY (DT5G_macro, file
21.3h tuổi ≤ ngưỡng 141.3h theo phiên 2026-08-28)`; sandbox ép ngưỡng 1h → WARN vẫn fire
và in nguyên văn dòng `!!! ABORT: ticker_prune still incomplete for 2026-09-02...` (nhánh
báo động thật không bị làm hỏng). `bash -n` OK, pre-commit 5 gate pass.

**Lesson.** Khi vá một check "ngày lịch → phiên giao dịch", **quét cả file** xem còn check
nào cùng lớp không — 0b83f507 vá §5 (`ticker_prune`) mà bỏ sót §3 (`macro_health`) ngay
phía trên, cùng file, cùng kỳ nghỉ, false-warn tiếp ngay ngày hôm sau.
