# VIỆC 1 — cổng phát hiện cột `Price` bị ĐÓNG BĂNG trên diện rộng

Job `Taylor_20260927_103434` · 2026-09-27 · branch `fix/data-gates-20260927` (repo `mike`, CHƯA MERGE)

## Kết quả

Thêm `_check_price_freeze()` vào `mike/bin/bq_freshness_check.sh`, gọi ngay sau depth-check
của `ticker_prune` (trước gate DT5G). Ngưỡng **50%**, đo từ **4.171 phiên** ticker_prune
(2010-01-05 → 2026-09-25), **0 false positive / 3.174 phiên 2014+**, bắt **4/4** phiên bất
thường đã biết.

## Vì sao 3 gate giá hiện có đều mù

| Gate hiện có | Đo gì | Vì sao mù với lỗi này |
|---|---|---|
| `_check "ticker_prune (EOD price)"` | `MAX(time)` | ngày vẫn advance bình thường |
| depth-check `MIN_PRUNE_NAMES=200` | số mã ngày mới nhất | vẫn ~250 mã đủ |
| cache-vs-live | so cache với BQ | cache == live ⇒ không phải lỗi cache |

## Phiên bất thường ĐO ĐƯỢC (không phải giả định)

`A` = tỉ lệ mã có `Price[t] == Price[t-1]`; `AB` = tỉ lệ mã phẳng CẢ `Price` VÀ `Close`.

| Phiên | n_tot | A | AB | mã phẳng có Close vẫn đổi | Diễn giải |
|---|---|---|---|---|---|
| 2025-02-03 | 258 | **1.000** | 0.093 | 234/258 | Price thô đóng băng TOÀN universe |
| 2026-01-30 | 256 | **0.992** | 0.125 | 222/254 | Price thô đóng băng TOÀN universe |
| 2018-01-24 | 221 | 0.792 | **0.787** | 1/175 | CẢ dòng giá là bản sao T-1 |
| 2018-01-23 | 220 | 0.755 | 0.455 | 66/166 | chữ ký PHA TRỘN |

**2025-02-03 là phát hiện MỚI của job này** — ticket 2 chỉ biết vùng 30/01–02/02/2026. Trong
dữ liệu live hiện tại chỉ **2026-01-30** đóng băng (02-02 bình thường ở 6,25%), không phải 3 phiên.

### Bẫy đã cắn ngay trong chính job này
Bản đầu của query calibration định nghĩa "phiên trước" là *`LAG` cách ≤ 7 ngày lịch*. Nghỉ Tết
VN dài **10–12 ngày lịch** ⇒ phiên ĐẦU sau Tết bị loại khỏi series, và **2025-02-03 rơi đúng
vào đó** — một trong hai phiên đóng băng thật đã bị chính công cụ đo che mất. Bản dùng thật:
"phiên liền kề của BẢNG" (`LAG` trên danh sách ngày `DISTINCT`) ⇒ không còn điểm mù, và phiên
đầu sau Tết 2026 (2026-02-23) vẫn đo được sạch (14/259 = 5,4%).

## Ngưỡng: đo từ phân bố, không bốc số

3.174 phiên 2014+, metric A: `p50=0,136 · p90=0,216 · p99=0,291 · p99,9=0,381`
→ rồi **khoảng trống rỗng** → `0,755 / 0,792 / 0,992 / 1,000`.

`0,50` nằm GIỮA khoảng trống `[0,381 ; 0,755]`; ≈ `med + 6,7·robustSD` (1,4826·MAD).
Metric AB cùng ngưỡng: `p99,9 = 0,353`, giá trị lớn nhất không thuộc phiên bất thường `= 0,377`.

Tái lập: `$DNA_PYEXE agents/Taylor/research/price_freeze_gate_20260927/calibrate.py` (query BQ
sinh series nằm trong docstring).

## Hai chữ ký, hai mức phản ứng (§29 — rẽ nhánh theo bit script vừa ĐỌC)

- **Price phẳng, Close vẫn đổi** → **WARN** (Discord, không chặn). `Close` là cột production
  đọc; `Price` thô không có consumer production (kết luận ticket 2).
- **Phẳng CẢ hai cột** → **BLOCK** (Telegram + Discord + `FAILED=1`). Nguyên dòng giá là bản
  sao T-1 ⇒ `[pipeline-1b/1c] build_universe_pit(_quality)` và chấm custom30V NGAY DƯỚI trong
  cùng script sẽ ăn dữ liệu chết.

Dòng cảnh báo trích số script vừa đọc (`n_flat/n_tot`, `n_cm/n_flat`, 2 ngày cụ thể) và rẽ
nhánh diễn giải theo `n_cm` — không có nguyên nhân viết cứng.

**Fail-safe**: `n_tot < 50` cặp mã so được ⇒ in `KHÔNG đủ dữ liệu để kết luận`, **không**
`OK`, **không** báo động. `bq` rc≠0 và `bq` rc=0-nhưng-rác là **hai** nhánh riêng với hai
thông điệp nguyên nhân khác nhau (§28), cả hai nói rõ *"ĐÂY KHÔNG PHẢI kết luận dữ liệu sạch"*.

## Kiểm chứng

- **Selfcheck**: `$DNA_PYEXE bin/bq_price_freeze_gate_selfcheck.py --mutations`
  → **156 assertion, 0 fail** trên **4 môi trường** TZ (`Asia/Ho_Chi_Minh`, `UTC`,
  `America/New_York`, TZ **gỡ hẳn**) · **12/12 mutation bị giết**.
  Hàm được TRÍCH bằng regex từ file thật mỗi lần chạy (không phải bản copy) ⇒ mutation có nghĩa.
  `bq` + `notify*.sh` đều stub trong sandbox `/tmp` ⇒ selfcheck KHÔNG tra BQ, KHÔNG gửi Discord.
  Case 1 dùng đúng số THẬT của 2026-09-25 (31/209); case 2–4 replay đúng số 3 phiên bất thường.
  Mutation `bothflat-gt->ge` lúc đầu SỐNG SÓT (case biên chỉ có AB=2%) → đã thêm case
  `boundary-bothflat-exactly-50pct` để giết.
- **Smoke query THẬT trên BQ** (stub không phủ được SQL): trả
  `OK ticker_prune Price-freeze: 31/209 mã Price phẳng (14% ≤50%) phiên 2026-09-25 vs 2026-09-24`.
  Đối soát độc lập: `INTERSECT DISTINCT` số mã có cả 2 phiên với `Price`/`Close` non-null = **209** ✓,
  và dòng 2026-09-25 của series = `209,31` ✓.
- `bash -n` OK · `bin/shellcheck_gate.sh` không sinh finding nào trong code mới (4 finding còn
  lại đều ở dòng 46/675/740/750 — tồn tại trước thay đổi này).

## Còn mở

- Gate chỉ đặt trên `ticker_prune`. `ticker_1m` (live screening) và `ticker` (full) cùng ETL
  nguồn nên cùng bị — 2026-01-30 trên `ticker` là 1235/1250 (98,8%). Chưa thêm gate cho 2 bảng
  đó: `ticker_prune` là universe production đọc, thêm 2 query nữa mỗi tối là chi phí không có
  bằng chứng cần. Nếu muốn phủ, dùng cùng hàm với ngưỡng calibrate RIÊNG (baseline `ticker`
  cao hơn hẳn: ~0,42 vs ~0,14 vì đuôi mã không thanh khoản).
- Nguyên nhân gốc nằm ở ETL upstream (ngoài tầm repo này) — gate chỉ PHÁT HIỆN, không sửa.
