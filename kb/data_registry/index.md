---
kind: registry-index
title: Data Registry — mọi nguồn dữ liệu hệ thống đang dùng
owner: Winston (data-ops)
format: OKF (Open Knowledge Format) — markdown + YAML frontmatter, 1 nguồn = 1 file
last_full_audit: 2026-07-11
migrated_from: kb/data_registry.md (single-file, migrate → OKF 2026-07-28 job Winston_20260728_104434)
---

# Data Registry — mọi nguồn dữ liệu hệ thống đang dùng

> Lập theo yêu cầu user 2026-07-11, sau sự cố SIGNAL_V11 đọc nhầm bảng `vnindex_5state`
> (base, KHÔNG phải DT5G) khiến sổ production `pt_v22_dt5g` vào lệnh theo trạng thái BULL
> GIẢ (xem `kb/INCIDENTS.md`). Đây là danh sách CHÍNH THỨC mọi nguồn dữ liệu (bảng BQ, file
> local, file trạng thái publish) đang được paper-trading/production/nghiên cứu dùng.

> **Last full audit: 2026-07-11** (seed + Taylor codebase sweep + `bin/data_registry_audit.sh` xây
> mới, chạy sạch FAIL=0/WARN=0). Cập nhật dòng này mỗi lần review định kỳ (Friday) hoặc audit thủ
> công chạy xong — xem mục 3 dưới. (Trong cấu trúc OKF, dòng "Last full audit" giữ ở frontmatter
> `last_full_audit` của file này.)

## Cấu trúc thư mục (OKF)

Mỗi nguồn dữ liệu = 1 file `.md` với frontmatter tối thiểu (`kind`, `status`, `source`, `group`).
Grep vẫn hoạt động: `grep -rn "<tên nguồn>" mike/kb/data_registry/`.

| Nhóm | Thư mục | Nội dung |
|---|---|---|
| Market state / regime (rủi ro cao nhất) | [`market-state/`](market-state/) | DT5G production, base trap, các CSV/bảng lineage 5-state |
| Giá / khối lượng cổ phiếu | [`price-volume/`](price-volume/) | DNSE live, `ticker`/`ticker_1m`/`ticker_prune`, `universe_pit`, shares/corp-action |
| Fundamentals / tài chính | [`fundamentals/`](fundamentals/) | `ticker_financial`, PE/PB/PCF, ROE/ROIC/FSCORE, risk_rating |
| Vĩ mô | [`macro/`](macro/) | VIX/SPX, SBV refi, macro_health, breadth, deposit_rate, CPI, GDP |
| 8L Rating / Composite v3 | [`rating-8l/`](rating-8l/) | `fa_ratings`, `fa_ratings_8l`, rating_8l.csv, moat/forensic tags |
| Custom30 parking baskets | [`custom30/`](custom30/) | `custom30v_8l` (prod), `custom30_8l` (trap), publish csv |
| BQ local cache | [`bq-cache/`](bq-cache/) | `data/bq_cache/*.parquet` mirror |
| LAG book (PEAD) caches | [`lag-book/`](lag-book/) | 4 pickle/csv cache cho paper sims |
| Research caches lớn | [`research-caches/`](research-caches/) | ba_v11 pkl, VNINDEX.csv, panel static |
| Trading bot / execution | [`trading-bot/`](trading-bot/) | accounts/rules/plan/exec-log/nav — money-path thật |
| Paper-trading harness | [`paper-harness/`](paper-harness/) | account `main` + sleeves (DC-book, ORB) |
| Feeds hàng hóa / FX / khác | [`feeds/`](feeds/) | FX, BDI, hog, commodity, foreign-flow candidates |
| Cấu hình chiến lược / meta | [`config-meta/`](config-meta/) | filter.json, bigquery_dictionary, results_registry |

**Điều hướng thêm:**
- [`_universe-selection-rules.md`](_universe-selection-rules.md) — quy tắc chọn universe (ticker vs universe_pit vs ticker_prune vs ticker_1m).
- [`_todo.md`](_todo.md) — phần còn thiếu thật sau sweep (Cần bổ sung).
- [`CHANGELOG.md`](CHANGELOG.md) — lịch sử biên tập registry (provenance, không phải INCIDENTS).

Mỗi thư mục có `index.md` riêng liệt kê các nguồn trong nhóm + status.

---

## Nguyên tắc bắt buộc

1. **Trước khi dùng 1 nguồn dữ liệu trong nghiên cứu/code MỚI — tra bảng này trước.** Nếu
   nguồn chưa có trong danh sách, KHÔNG coi mặc định là an toàn — thêm vào danh sách này
   (hoặc hỏi người review) trước khi wire vào bất kỳ paper-trading/production nào.
2. **Trường "status" là điều quan trọng nhất, đọc trước khi dùng:**
   - `CANONICAL` — nguồn đúng, dùng trực tiếp được.
   - `TRAP` — tên/vị trí DỄ NHẦM với 1 nguồn canonical khác, đã có tiền lệ bug thật. Đọc kỹ
     phần "Bẫy" trước khi động vào.
   - `DERIVED` — tính từ 1 nguồn canonical khác, an toàn nếu nguồn gốc còn đúng.
   - `DEPRECATED/DEAD` — không còn được cập nhật hoặc không nên dùng nữa, chỉ giữ để tham
     chiếu lịch sử.
3. **Người review + tần suất:** Winston (data-ops) giữ danh sách này tươi — cập nhật ngay
   khi phát hiện nguồn dữ liệu mới trong lúc làm việc khác (không cần đợi review định kỳ).
   Review định kỳ TOÀN BỘ danh sách gắn vào **review KB thứ Sáu hàng tuần** (`kb_nightly.sh`
   Phase 5, dispatch Mike headless) — cơ chế nay có 2 phần cụ thể, không chỉ là kế hoạch:
   (a) chạy `bin/data_registry_audit.sh --bus` (script, không phải LLM tự đoán) — kiểm tra
   CƠ HỌC 2 việc: (i) các file từng bị bug base-leak/mislabel (`signal_v11_sql.py`,
   `pt_v4/pt_v22/pt_v23_audit`, `golive_recommend_v23.py`) chưa regress lại; (ii) freshness
   thật của 3 nguồn rủi ro cao nhất (`vnindex_5state_dt5g_live`, `custom30v_8l`,
   `fa_ratings_8l`) qua `bq show` trực tiếp, không suy đoán từ cache/mtime file phụ; (b) Mike
   đọc kết quả FAIL/WARN, xử lý theo mục 5 dưới nếu là vấn đề obsolete/regression, cập nhật
   `last_full_audit` ở frontmatter file `index.md`. Ai muốn chạy tay ngoài lịch:
   `bin/data_registry_audit.sh` (thêm `--bus` để ghi bus event, mặc định chỉ in ra màn hình).
4. **Khi dispatch Taylor cho R&D mới:** prompt phải nhắc "tra `mike/kb/data_registry/` (index.md)
   trước khi chọn nguồn dữ liệu, đặc biệt bảng market-state/regime" — giống quy tắc đã có
   cho DollarBill (DNSE-vs-BQ, `coding_guidelines.md` §6).
5. **Đánh dấu obsolete khi quyết định migrate khỏi 1 nguồn** (user chỉ đạo 2026-07-11, sau
   phát hiện fa_ratings có thể bị thay bởi fa_ratings_8l) — BẮT BUỘC làm CẢ 3 bước sau CÙNG
   lúc với commit cutover, không để thành TODO làm sau (nếu tách rời, đúng lúc đó là lúc dễ
   dùng nhầm bản cũ nhất — bài học SIGNAL_V11 base-leak):
   - (a) Đổi `status` của nguồn cũ → `DEPRECATED` kèm dòng **⚠️ SUPERSEDED BY `<nguồn mới>`
     ON `<ngày cutover>`** ngay trong phần "Bẫy" của file nguồn đó, không chỉ đổi mỗi trường status.
   - (b) Chạy sweep xác nhận (grep toàn codebase + `bin/data_registry_audit.sh`) KHÔNG còn
     script production nào đọc nguồn cũ — nếu còn, liệt kê rõ tên file + lý do (vd "chỉ
     script research lịch sử, không sửa"). Không được nói "chắc không còn ai đọc" mà không
     grep thật.
   - (c) Ghi 1 dòng vào [`CHANGELOG.md`](CHANGELOG.md): ngày cutover, nguồn cũ→mới, ai duyệt, có
     PBO/DSR/quant-skeptic verify hay không (nếu là migration signal như fa_ratings→8l).
   Ràng buộc riêng cho case `fa_ratings` cụ thể: quyết định migrate PHẢI qua backtest song
   song + quant-skeptic + user sign-off trước (xem `rating-8l/fa_ratings.md` +
   `rating-8l/fa_ratings_8l.md` — đây là ĐỔI SIGNAL, 66% tier khác nhau, không phải data
   refresh đơn thuần), KHÔNG được đánh dấu obsolete trước khi có kết quả đó.
