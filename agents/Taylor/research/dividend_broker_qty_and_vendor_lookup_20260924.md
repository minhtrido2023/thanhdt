# dividend_adjusted_return.py — 2 bug cùng file, 2 nhánh riêng (2026-09-24)

Dispatch: `Taylor_20260924_024940`. Nhánh `fix/dividend-broker-qty-vendor-label`
(worktree `mike/agents/Taylor/wt-dividend-fix`). **CHƯA LAND** — cho Mike arch-review.

## VIỆC 1 — `broker_qty()` lấy LÔ CUỐI thay vì TỔNG LÔ

**Đã commit riêng: `085bd6cb`.** Tóm tắt (đầy đủ trong commit message):
- Đo thật ZaloPay: 135 cặp (mã, ngày) lệch (BID/MBB/VCB, mọi ca có ≥2 gói vay margin), lệch
  25,0%–66,7%. Ca cụ thể: BID 14/08 báo 320 (chỉ `loanPackageId=1258`) trong khi tổng thật 2 lô
  (+`loanPackageId=1826`=107) là 427.
- Sửa: gộp lô TRONG bản ghi MỚI NHẤT của mỗi ngày — cùng quy ước với
  `daily_nav_snapshot.raw_positions` (dùng bởi `credit_frame`), tránh vừa cộng chéo giữa hai bản
  ghi khác thời điểm của cùng ngày.
- Tác động số ĐÃ CÔNG BỐ: kiểm cả 8 sự kiện `detect_adjustments()` của BID/MBB/VCB trong 2026 —
  per_share/kind giống hệt trước/sau vá ở MỌI ca (các ẩn bị ảnh hưởng chỉ từng rơi vào
  STOCK_SUSPECTED hoặc UNVERIFIED, chưa từng đạt CASH_CONFIRMED qua qtys lỗi) → **KHÔNG cần đính
  chính số đã gửi nhà đầu tư**.
- Selfcheck mục 25: fixture hình dạng thật (107+320=427), 2 assertion có tên
  (`broker_qty_last_lot_wins`, `broker_qty_cross_record_double_count`), cả 2 mutation chết. 148→151
  PASS/0 FAIL.

## VIỆC 2 — `bq_corp_action` nuốt exception ⇒ 2 lá chắn D1 tắt IM LẶNG khi BQ hỏng

**Chưa commit tại thời điểm viết báo cáo này** (đang trong cùng phiên, sẽ commit ngay sau).

### Vấn đề
`bq_corp_action()` (dòng ~417 bản cũ) có `except Exception: return None` — giống hệt nhánh "0
dòng" (`if not rows: return None`). Hệ quả: BQ lỗi mạng/auth/quota → `vendor_check = "unavailable"`,
**y hệt nhãn** dùng cho "vendor XÁC NHẬN không có sự kiện". `resolve_dividends` chỉ có 1 nhánh xử lý
`vendor_check == "unavailable"` → cả 2 lá chắn vendor-mismatch (D1 `stock_leg_ignored` +
`cash_mismatch`, chính sách LIVE từ `07288554`) **không bao giờ được kích hoạt** cho sự kiện đó
— báo cáo công bố số broker y như trước khi có chính sách, không một cảnh báo.

### Sửa — tách 2 nhãn, fail-closed đúng mức
1. **`bq_corp_action`**: bỏ `try/except` nuốt lỗi — để exception của `_bq()` NÉM LẠI cho người gọi.
   Docstring viết rõ: `None` = vendor XÁC NHẬN 0 dòng (truy vấn CHẠY THÀNH CÔNG); exception = KHÔNG
   tra được (mạng/auth/quota).
2. **`resolve_dividends`**: bọc lời gọi trong `try/except`. Khi bắt exception:
   - `adj.vendor_check = "lookup_failed"` (nhãn MỚI, tách khỏi `"unavailable"`).
   - `adj.vendor_note` in **lỗi thật** (`str(e)[:300]`, §29 — không đoán nguyên nhân).
   - **Chỉ hạ `CASH_CONFIRMED → UNVERIFIED`** (fail-closed cho đúng nhánh có nguy cơ công bố sai);
     các `kind` khác (chưa giải được, `unresolved`) giữ nguyên — không có gì để "hạ thêm", và
     KHÔNG được promote lên `CASH_VENDOR`/`STOCK_CONFIRMED` (những nhãn đó chỉ hợp lệ khi vendor
     THỰC SỰ trả dữ liệu).
   - `continue` cho ĐÚNG sự kiện đó — không crash cả `resolve_dividends`. Lý do chọn scope hẹp
     (không phải chặn toàn bộ ngay khi thấy 1 lỗi): một đợt BQ hỏng thật sẽ khiến NHIỀU/mọi mã
     trong rổ cùng rơi vào `lookup_failed` cùng lúc — báo cáo tự hiện rõ "toàn UNVERIFIED" (chặn ở
     tầng công bố §21/report gate), thấy được LỚN hơn so với nuốt lỗi và công bố sai trong im lặng.

### Quyết định fail-closed — chọn CHẶN (không chọn "công bố kèm cảnh báo")
Cân nhắc cả hai phương án theo yêu cầu dispatch:
- **Chặn công bố** (đã chọn): downgrade về `UNVERIFIED` → `report_return_gate`/§21 tự loại khỏi
  báo cáo gửi nhà đầu tư. Rủi ro: 1 đợt BQ hỏng làm mất số của MỌI sự kiện `CASH_CONFIRMED` chưa
  qua đối soát vendor trong lần chạy đó.
- **Công bố kèm cảnh báo** (không chọn): giữ `kind` cũ, chỉ nổi cảnh báo `lookup_failed` cho người
  đọc. Rủi ro: đúng lỗ hổng gốc mà chính sách 2026-09-24 sinh ra để chặn — "cảnh báo nổi lên nhưng
  số vẫn đi ra" đã từng chứng minh KHÔNG đủ (case gốc arch-review: 0 cảnh báo, giờ nếu có cảnh báo
  vẫn không ai đảm bảo người đọc dừng lại trước khi gửi).

**Lý do chọn chặn:** cổng §21 vốn đã fail-closed theo thiết kế (báo cáo không gửi được → THẤY
NGAY, ai đó phải chạy lại), trong khi công bố số sai là lỗi ÂM THẦM — đúng logic mà arch-review
2026-09-24 đã dùng để chốt toàn bộ chính sách vendor-mismatch. Không có lý do đối xử khác với
nhánh "không tra được" so với nhánh "tra được nhưng lệch".

### Đo trên dữ liệu thật (yêu cầu (e))
K1 gốc (62 sự kiện, 39 mã, 2026-03-24→2026-09-24, đo BẰNG CODE CŨ — nuốt exception):
25/62 = `unavailable`, không phân biệt được "0 dòng" vs "lỗi tra cứu" (2 nhãn trộn chung).

**Đo lại HÔM NAY bằng code ĐÃ VÁ** (cùng 62 sự kiện, cùng cửa sổ,
`exp_vendor_mismatch/k1_v2_rerun.log`):

| vendor_check | số sự kiện |
|---|---|
| `unavailable` (0 dòng, THÀNH CÔNG) | 25 |
| `lookup_failed` (không tra được) | **0** |

**Không thể xác nhận hồi tố cho từng lần chạy LỊCH SỬ** trước đây (code cũ trộn 2 trạng thái vào
cùng 1 nhãn, không lưu log chi tiết từng lần gọi `_bq()` để soi lại) — nói thẳng theo yêu cầu.
Bằng chứng gián tiếp duy nhất: chạy lại NGAY BÂY GIỜ với code đã vá cho đúng bộ 62 sự kiện đó ra
**0/62 lookup_failed**, tức BQ khoẻ tại thời điểm đo lại. Không đủ để khẳng định BQ khoẻ ở MỌI thời
điểm 62 lần resolve trước đây từng chạy, nhưng không có bằng chứng ngược lại — và từ nay, việc
tách nhãn khiến bất kỳ lần hỏng thật nào trong tương lai sẽ TỰ HIỆN thay vì trộn lẫn.

### Selfcheck — mục 26 (mới), 3 nhóm test + assertion có tên
1. `lookup_failed_downgrade` + `lookup_failed_label` + `lookup_failed_real_error`: BQ ném lỗi khi
   đã `CASH_CONFIRMED` ⇒ hạ `UNVERIFIED`, `vendor_check="lookup_failed"`,
   `vendor_note` chứa lỗi thật (fixture `RuntimeError("BQ 403 PERMISSION_DENIED: quota exceeded...")`).
2. `lookup_failed_no_promote`: BQ ném lỗi khi broker CHƯA giải ⇒ không bị ép lên
   `CASH_VENDOR`/`STOCK_CONFIRMED`.
3. `lookup_failed_not_over_eager` + `unavailable_still_published`: `bq_corp_action` trả `None`
   (0 dòng, THÀNH CÔNG, không exception) ⇒ vẫn `"unavailable"`, KHÔNG bị lẫn `"lookup_failed"`,
   `kind` KHÔNG bị hạ oan.

**151 → 159 PASS/0 FAIL.** 5 mutation dựng thủ công (chạy TRONG worktree, không copy ra ngoài —
xem "Harness" bên dưới), cả 5 chết bằng đúng assertion có tên tương ứng:
- mutant nhãn (`lookup_failed`→`unavailable` trong except) → chết ở `lookup_failed_label`.
- mutant bỏ downgrade → chết ở `lookup_failed_downgrade`.
- mutant xoá lỗi thật khỏi `vendor_note` → chết ở `lookup_failed_real_error`.
- mutant gắn nhầm nhánh `unavailable` (0 dòng) thành `lookup_failed` → chết ở
  `lookup_failed_not_over_eager`.

## Hồi quy toàn bộ battery (>=3 môi trường, gồm `env -u TZ`)

| Script | Kết quả | default | `env -u TZ` | `TZ=America/New_York` |
|---|---|---|---|---|
| `dividend_adjusted_return.py --selfcheck` | 159/0 (từ 148) | PASS | PASS | PASS |
| `report_return_gate.py --selfcheck` | 75/75 | PASS | PASS | PASS |
| `report_return_gate_selfcheck.py --root-only` | PASS | PASS | PASS | PASS |
| `vendor_mismatch_alert_selfcheck.sh` | 57/0 | PASS | PASS | PASS |

`git status --porcelain` sau toàn bộ lượt chạy: chỉ `bin/dividend_adjusted_return.py` (đã commit),
không rác state/bus.

**Harness note (§ dispatch cảnh báo):** mọi lần chạy selfcheck/mutation đều thực hiện TRONG
worktree (`mike/agents/Taylor/wt-dividend-fix`), không copy ra `/tmp` — thử copy ra `/tmp` một lần
để dựng mutant đầu tiên, xác nhận ĐÚNG như cảnh báo: `find_wc_root`/import `daily_nav_snapshot`
lệch, mutant "chết bằng crash import" thay vì assertion. Chuyển sang sửa-chạy-phục hồi trực tiếp
trong worktree (backup ra `/tmp/dar_control_backup.py`, không phải chạy TỪ đó) — control run sau
khi phục hồi (159/0) xác nhận harness lành trước khi tin bất kỳ kết quả mutant nào.

## Còn mở
- R1 cũ (arch-review vòng 2, `dar:421-422`) — chính là việc này, nay đã sửa.
- Không có việc mới phát sinh ngoài phạm vi dispatch.
