# Đề xuất đăng ký theo dõi paper — `behav_cell_ledger` (CHỜ Mike duyệt; job Taylor_20261125_114526)

User duyệt đăng ký 25/11 18:44 ICT. Tôi KHÔNG sửa `mike/kb/paper_programs_registry.json` (repo lồng, ngoài worktree này), KHÔNG cài cron, KHÔNG merge.
- Entry JSON đề xuất (khuôn lấy từ `macro_stress_ledger`): `paper_registry_entry_proposed.json` (cùng thư mục). Mike chèn vào `programs[]` + cập nhật `updated`.
- Script: `calc/paper_cell_monthly.py` (nhánh `session/Taylor_20261125_104308`). Sổ mặc định `out/paper_cell_ledger.csv` (đổi bằng `PCM_LEDGER`/`--ledger`).
  **Vị trí sổ đề xuất sau merge:** `mike/kb/data_registry/market-state/behav_cell_ledger.csv` + 1 trang data_registry (CANONICAL khi có dữ liệu) — Winston/Mike tạo.

## Đã chứng minh chạy được (đọc trên dữ liệu hiện có, `out/log_paper_cell.txt`)
- `--asof-ym 2026-10`: as-of 2026-10-30, n = 333 mã (universe_pit in_universe 339; 5–6 mã thiếu lv_ENS2), ô: RE_CHUA_THUA_NHAN 91 · DAT_CON_NEO 90 ·
  RE_DUOC_THUA_NHAN 77 · DAT_DANG_NGUOI 75; panel_time_match 1,000; hi52 tính lại độc lập bằng vòng lặp thuần cho 8 mã: 0/8 lệch (|Δ| < 1e-9).
- Chạy lại cùng tháng ⇒ `SKIP` rc=0 (idempotent). `--asof-ym 2026-11` ⇒ **FAIL-CLOSED rc=3** vì universe_pit cache mới tới 2026-11-20 < ngày as-of 2026-11-23 — đúng thiết kế.
- Bắt được 1 lỗi của chính tôi trong lúc test (căn chỉnh chỉ số rolling ⇒ n=193 sai) — đã sửa, n=333. File thử `out/paper_cell_TEST_2026-10.csv` KHÔNG phải sổ thật.

## Phụ thuộc phải giải quyết TRƯỚC khi cài cron (chưa giải quyết)
1. **`lv_ENS2` cần panel V3.1 dựng lại hằng tháng** (`b_panel.py` đọc BCTC + giá + mã vắng BQ). Hiện panel chỉ là sản phẩm nghiên cứu (as-of mới nhất 2026-11-23, universe_pit
   chưa phủ). Chưa đo chi phí dựng lại; cần Mike/Winston quyết ai dựng và khi nào, hoặc tôi viết bản `lv_ENS2` incremental (job riêng). Không có cái này cron vô nghĩa.
2. as-of là NGÀY GIAO DỊCH CUỐI THÁNG; cần `data/bq_cache/universe_pit` và `ticker` đã sync tới ngày đó (BQ sync 23:45 ICT; universe_pit 19:00 ICT) ⇒ chạy từ ngày làm việc 1–2 của tháng sau.

## Lệnh cron đề xuất (CHƯA cài; Mike duyệt; host TZ=Asia/Ho_Chi_Minh theo §16; tra `kb/cron_registry.md` trước — §11)
```
# 08:10 ICT ngày làm việc đầu tiên (T2–T6, ngày 1–3) của tháng; script tự SKIP nếu tháng trước đã có, FAIL-CLOSED nếu universe_pit chưa phủ
10 8 1-3 * 1-5  cd /home/trido/thanhdt/WorkingClaude/wt-.../agents/Taylor/research/dcf_vn_behavioral_20261125 && /home/trido/thanhdt/wc_venv/bin/python calc/paper_cell_monthly.py --asof-ym $(TZ=Asia/Ho_Chi_Minh date -d "$(date +%Y-%m-01) -1 day" +\%Y-\%m) >> /home/trido/thanhdt/WorkingClaude/mike/logs/paper_cell_monthly.log 2>&1
```
(Đường dẫn sau merge phải đổi sang vị trí chính thức; `date -d` khi chạy ngày 1–3 trả đúng tháng trước.) Tôi không chạy lệnh này.
