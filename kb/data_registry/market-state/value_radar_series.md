---
kind: local-file
status: CANONICAL (DISPLAY-ONLY — cấm mọi consumer ra quyết định)
source: data/value_radar_series.csv
group: market-state
role: KHÔNG money-path — chỉ hiển thị cạnh DT5G ở dna_report NOW + eod_trading_report
writer: value_radar.py (2026-07-30, job Taylor_20260730_164533) — tự cập nhật tăng dần khi được đọc; KHÔNG có cron riêng
selfcheck: `python3 value_radar.py --selfcheck` (parity với Phụ lục C, exp_value_radar/radar.csv)
---

# `data/value_radar_series.csv` (+ module `value_radar.py`)

**Status: CANONICAL cho "Value Radar"** — và **DISPLAY-ONLY theo thiết kế**.

## Là gì
Chuỗi thô theo phiên `time, n, pe_cap10, pb_cap10` (rổ top-100 vốn hoá, capped-weight 10%/mã),
floor **2008-01-01**, 4.633 phiên tính đến 2026-07-30. Module `value_radar.py` đọc file này, ghép
lãi suất huy động (`deposit_rate_vn.deposit_events_df()`, merge_asof backward = nhân quả), rồi quy
3 thành phần (P/E, P/B, spread EY−lãi suất **đảo chiều**) về **phân vị rolling 10 năm (2500 phiên,
min 500)** và lấy trung bình ⇒ điểm 0-100 + nhãn **RẺ <33 · TRUNG TÍNH 33–67 · ĐẮT >67**.

Cửa sổ rolling-10Y là **lựa chọn PHƯƠNG PHÁP của user** (2026-07-30) — ưu tiên giai đoạn gần thay
vì cân bằng cả lịch sử 2008+. Bản expanding-2008 vẫn tính song song (`score_expanding`) để đối chiếu.

## Ai ghi / cadence
`value_radar.py` tự cập nhật **tăng dần** mỗi lần được đọc: query `tav2_bq.ticker` từ (phiên cuối
trong cache − 10 phiên) rồi ghi đè phần đuôi (BQ `ticker` bị TRUNCATE+rebuild mỗi ngày ⇒ đuôi có
thể restate, không tin cache mù quáng). Ghi nguyên tử (`tmp` + `os.replace`). **Không có cron
riêng** — cache tự tươi theo nhịp 2 consumer hiển thị.

Dựng lại toàn bộ (~1,36M dòng, ~2 phút): `python3 value_radar.py --rebuild` — thao tác **TƯỜNG
MINH**. Thiếu cache ⇒ `update_cache` **raise**, KHÔNG tự rebuild (nếu không, 1 tin nhắn Telegram có
thể kích hoạt query 1,36M dòng).

## Bẫy
1. **CẤM wire vào quyết định giao dịch.** Phụ lục C (`mike/agents/Taylor/research/
   market_regime_probability_20260729.md`): **0/17 lăng kính** qua BH(FDR 10%)/Bonferroni; hiệu
   RẺ−ĐẮT p=0,049 chưa hiệu chỉnh đa kiểm định; **đầu RẺ không đơn điệu** (dải 0-20 tệ hơn dải
   20-33) ⇒ "càng rẻ càng nên mua" là SAI. Consumer hợp lệ **duy nhất**: `dna_report.py`
   (`build_value_radar_line`, khối NOW) + `mike/bin/eod_trading_report.sh`. KHÔNG
   `golive_recommend_v23.py`, KHÔNG `bot_execute.py`, KHÔNG sizing CAPIT/LAG/BAL. Cùng tiền lệ
   **DT4-gate clock** — thuần hiển thị, không phải gate.
2. **Radar KHÔNG phải 3 nguồn bằng chứng độc lập.** corr(P/E, P/B) thô = 0,913; VIF cao nhất 4,97;
   `radar2` (bỏ spread) chênh 0,6 điểm so với `radar3` ⇒ thực chất ~1,5–2 chiều thông tin. Ai đọc
   "3 lăng kính cùng nói rẻ" là **đếm trùng**.
3. **Thành phần spread là yếu nhất** — caveat (b) của [[deposit_rate_vn]]: 26 mốc lãi suất neo hồi
   tố **1 lần** ngày 2026-06-19 ⇒ phân vị lịch sử mang bias "biết trước". Chỉ mốc từ 2026-06 mới PIT thật.
4. **Vintage = T-1** cho tới khi `sync_bq_cache_daily.sh` 23:45 chạy. Mọi dòng hiển thị đã đóng dấu
   "dữ liệu tới `<asof>`". Không vướng bright-line DNSE-vs-BQ (coding_guidelines §6 chỉ áp cho số
   same-day dùng để đặt lệnh/định giá lệnh) — nhưng **đừng trích như số của hôm nay** nếu asof là T-1.
5. **Nhãn lật qua lại quanh biên**: 07-30 rolling-10Y **25,9 RẺ** trong khi expanding-2008 **36,0
   TRUNG TÍNH** — cùng ngày, cùng công thức, chỉ khác cửa sổ. Trích 1 nhãn mà không nói cửa sổ là
   trình bày sai độ chắc chắn.

## Sandbox nghiên cứu (audit trail, KHÔNG phải nguồn sống)
`mike/agents/Taylor/exp_value_radar/` (`fetch.py`/`v1_pe.py`/`v2v3.py`/`v4_radar.py` → `radar.csv`)
— giữ nguyên làm bằng chứng gốc + đích parity của `--selfcheck`. Đừng đọc nó trong code sống.

## Self-check parity (2026-07-30, job Taylor_20260730_164533) — PASS
`python3 value_radar.py --selfcheck` trên 4.633 phiên chung với `exp_value_radar/radar.csv`:
lệch **NHÃN 0/4.134 phiên**; hôm nay rolling-10Y **25,9 RẺ** / expanding **36,0** khớp đúng số pin
ở Phụ lục C §C.4.5; chỉ **31/4.134 phiên (0,75%)** lệch >1e-9 (max 0,62 điểm), đúng hiện tượng
**đồng hạng vốn hoá khi cắt top-100** mà Phụ lục B/C đã ghi nhận (trung vị lệch = 0).
