# Phase 1 → Option C: nhãn quan sát đã wire (2026-08-18)

**Job** `Taylor_20260818_134610` · user (John) chọn **C** từ `FINDINGS.md` §6.
Commit: `WorkingClaude@9ed56854` (code) + `mike@a6ea3f06` (registry).

## Đã làm gì

| | |
|---|---|
| `custom30_yield_labels.py` (mới) | panel BATCH 2 query → `{(ticker, rebal_date): (note, is_stable)}`. Ngữ nghĩa = ĐÚNG `_yield_floor()`; ngưỡng import thẳng từ `due_diligence` (không chép số). |
| `custom30_history.py` | gọi `label_basket()` **sau** khi `rows` đã đóng → 2 cột `yield_floor_note`, `is_stable_payer`. |
| `custom30_yield_labels_selfcheck.py` (mới) | A) tương đương `_yield_floor()`; B) fail-open; C) không nhãn rỗng. |
| `kb/paper_programs_registry.json` | entry `yield_floor_custom30v_observe`, `end` 2027-02-05, review 2027-02-10. |

**Vì sao batch chứ không per-ticker**: `custom30_history.py` dựng lại 49 kỳ MỖI NGÀY ⇒ spec gốc
("gọi `_yield_floor()` cho từng mã") = ~3.000 query BQ/ngày. Panel = 2 query.

**Vì sao KHÔNG cần `ALTER TABLE`** (Bước 2 của dispatch): writer đã dùng `bq load --replace`, lệnh
này ghi lại **cả schema lẫn dữ liệu**. Xác minh thật: bảng scratch nạp code CŨ (8 cột) rồi nạp code
MỚI (10 cột) — cột mới hiện ra, `is_stable_payer` về đúng `true/false/NULL`.

## Bằng chứng "selection logic KHÔNG ĐỔI"

A/B chạy thật, cùng env (`wc_env.sh` + `$DNA_PYEXE`), code TRƯỚC vs SAU, đích scratch:

| kiểm tra | kết quả |
|---|---|
| 8 cột gốc, 1.470 dòng / 49 kỳ, đường **custom30V** (yieldcombo) | **IDENTICAL** |
| 8 cột gốc, đường **custom30 blend** (env mặc định, step [6]) | **IDENTICAL** |
| bản "TRƯỚC" vs CSV production 15:32 hôm nay | **IDENTICAL** ⇒ A/B ổn định, không phải trùng hợp |

Selfcheck (`$DNA_PYEXE custom30_yield_labels_selfcheck.py`), chạy lại dưới `TZ=America/New_York`
và `env -u TZ` + `python3` hệ thống, PASS cả ba lần:
- **A** batch vs `_yield_floor()` gọi thật: **30/30** trên rổ 2026-08-05.
- **B** `bq` ném lỗi ⇒ toàn bộ `("NO_DATA", None)`, KHÔNG raise (pipeline rổ không chết vì nhãn).
- **C** 0 nhãn NULL/rỗng; `is_stable_payer` NULL đúng **377/1.470** = số dòng `BANKING_EXCLUDED`.

## Rổ hiện tại (2026-08-05) và phân bố 49 kỳ

`BANKING_EXCLUDED 13 · NO_DATA 10 · BELOW_FLOOR 4 (IDC, DDV, DGC, VGC) · ABOVE_FLOOR 3 (VHC, DCM, PNJ)`

Toàn bộ 1.470 dòng: `NO_DATA 554 · BANKING_EXCLUDED 377 · ABOVE_FLOOR 332 · BELOW_FLOOR 193 · NEAR_FLOOR 14`.

## Cách đo gate #2 ở kỳ review 2027-02-10

1. Lấy nhãn tại 2 rebal: `SELECT rebal_date, ticker, weight, yield_floor_note FROM tav2_bq.custom30v_8l
   WHERE rebal_date IN ('2026-11-05','2027-02-05')`.
2. Tìm episode drawdown VNINDEX ≥5% trong 2026-08-18→2027-02-05.
3. Với mỗi episode: MDD từng mã trong rổ, so **trung vị nhóm BELOW_FLOOR vs ABOVE_FLOOR** (chỉ so
   TRONG rổ — cùng gate 8L≤3, cùng pool thanh khoản, nên đã kiểm soát phần lớn nhiễu).
4. n sẽ RẤT nhỏ (4 vs 3 mã ở kỳ này) ⇒ đây là **quan sát định hướng, không phải test có power**.
   Đừng đọc nó như bằng chứng thống kê; nó chỉ để quyết định có đáng bỏ 1 job backtest cho B không.

## Hai điều phải mang theo khi đọc nhãn

1. **BELOW_FLOOR không phải tín hiệu mua.** Research REFUTED chân H1 (BHAR60 t=0,67, **median âm
   −0,97pp**); chỉ CONFIRMED chân H2 (ΔMDD60 +3,46pp) ở độ tin cậy TRUNG BÌNH.
2. **Nhãn lịch sử không point-in-time tuyệt đối**: dedup DIV lấy `public_date` mới nhất, nên một
   đính chính công bố SAU `asof` vẫn được dùng (đúng y như `_yield_floor()` production). Không ảnh
   hưởng tiền — cột thuần quan sát — nhưng đừng dùng chuỗi lịch sử này làm feature backtest mà
   không dựng lại bản point-in-time thật.
