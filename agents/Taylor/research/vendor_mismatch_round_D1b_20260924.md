# vendor-mismatch D1b — arch-review NEEDS_CHANGES → 3 required change XONG

Nhánh `fix/vendor-mismatch-d1-stockleg`, worktree `mike/wt-vendor-d1`. HEAD `77837876`
(base `dc147859`, sau khi Mike rebase). CHƯA LAND — chờ arch-review vòng kế + Mike/user.

## Bối cảnh
Attempt 1 (job `_020630`) đã bị cắt/timeout nhưng để lại code cho cả 3 R ở dạng uncommitted
diff trong worktree — attempt 2 (job này) không viết lại từ đầu, chỉ kiểm chứng code đã có,
tìm và sửa 1 lỗi trong chính selfcheck, chạy đủ 4 môi trường, rồi commit riêng từng R.

## R1 — bin/vendor_mismatch_alert.sh (commit `853385e9`)
Trước: script phát MỘT câu cố định "hai số KHÁC nhau" / "đối soát cho khớp lại" cho MỌI mã
lý do — sai cho `stock_leg_ignored` (không có "hai số" để so; việc cần làm là tìm chân cổ
phiếu bị bỏ sót). Sửa: đọc dòng `VENDOR_MISMATCH_REASON|<acct>|<mã>|<ex>|<reason>|<vendor_stock>`
(tag riêng, KHÔNG đổi 7 trường của dòng `ALERT` gốc), ghép bằng khoá `acct|mã|ex`, rẽ 3 nhánh
Discord + "Việc cần làm": `stock_leg_ignored` / `cash_mismatch` / mã lý do thiếu-rỗng-lạ →
fail-closed "không xác định được — kiểm thủ công", không đoán.

**Bug tìm thấy VÀ SỬA trong chính selfcheck** (không phải trong code sản xuất): CA 10 của
`vendor_mismatch_alert_selfcheck.sh`, nhánh `bad()` của assertion MUTATION-GUARD chính dùng
tên RÚT GỌN so với nhánh `ok()` (thiếu đuôi "— 3 mã lý do KHÔNG bị gộp thành 1 câu chung").
Hệ quả: `kill_check` của MUTATION 6 grep đúng text từ `ok()` nhưng khi mutant thật sự làm
assertion FAIL (đi qua nhánh `bad()`), text bị cụt nên `grep -qF` không khớp → mutant BÁO
"chết SAI chỗ" dù đã chết ĐÚNG chỗ. Đồng bộ lại text 2 nhánh, xác nhận bằng debug harness
tách riêng (in `$out` ra file trước khi grep) — sau sửa: `MUTANT m6 ... chết bằng ASSERTION`.

Selfcheck: **48 → 57 ca**, mutation MỚI (m6: xoá dòng đọc REASON → cả 3 mã lý do gộp về
"unknown") giết bằng assertion có tên.

## R2 — bin/report_return_gate.py (commit `6d13ad60`)
`entitled_gross`'s `getattr(a, "vendor_mismatch_reason", "") or "cash_mismatch"` đoán mò khi
field thiếu/rỗng → đổi default "unknown". `run_gate` thêm nhánh thứ ba (ngoài
stock_leg_ignored/cash_mismatch): "không xác định được mã lý do — kiểm thủ công". "VIỆC CẦN
LÀM" giờ rẽ theo TẬP `reasons_present` (có thể in cả 2-3 mục cùng lúc nếu báo cáo gộp nhiều
loại). Selfcheck: **71 → 75 ca** (ca FFF: Adjustment không set `vendor_mismatch_reason`, 2
assertion có tên: `gate_vendor_reason_unknown_no_guess` + `gate_vendor_reason_failclosed`).

## R3 — bin/dividend_adjusted_return.py (commit `77837876`)
2 lỗi trong COMMENT (không phải logic):
- Ví dụ VNM 2026-06-25 cho nhánh `broker_only` SAI — mã đó `row` không tồn tại → rơi vào
  nhánh `unavailable`, không phải `broker_only`. Sửa lại đúng: K1 thực tế 0/62 sự kiện là ca
  `broker_only` thật.
- Mẫu số "K1 62 sự kiện ⇒ 0 dương tính giả" mượn uy tín của 62 cho phép đo mà nhánh vá D1
  chỉ CÓ THỂ chạy khi `kind == CASH_CONFIRMED` — ô rủi ro thật là **6/62** (MBB, CTG, VCB,
  NCT, SAB, DGC), không phải 62. Sửa lại đúng mẫu số.

Thêm 1 assertion có tên (`vendor_stock_leg_check_label`) neo `vendor_check == "mismatch"`
đơn lẻ — trước đây mutation "mismatch→broker_only" chỉ chết bằng dòng got/want của `same()`
(đếm FAIL, không dừng), dù hệ quả thật là cảnh báo biến mất TRONG IM LẶNG (nhãn `broker_only`
không bị `entitled_gross` chặn). Selfcheck: **147 → 148 ca**.

## Verify — 4 môi trường TZ, tất cả PASS
| Selfcheck | TZ=Asia/Ho_Chi_Minh | env -u TZ | TZ=Pacific/Kiritimati | TZ=America/Los_Angeles |
|---|---|---|---|---|
| `dividend_adjusted_return.py --selfcheck` | 148/0 | 148/0 | 148/0 | 148/0 |
| `report_return_gate.py --selfcheck` | 75/75 | 75/75 | 75/75 | 75/75 |
| `vendor_mismatch_alert_selfcheck.sh` (+mutations) | 57/0 | 57/0 | 57/0 | 57/0 |

`report_return_gate_selfcheck.py --root-only`: PASS (đường EXEC_DIR/WC_ROOT worktree-safe,
6 ca RED-control).

## 4 mutation bắn lại thủ công — tất cả chết bằng assertion có tên
1. Bỏ `vendor_stock > 0` khỏi điều kiện D1 → `MUTATION-GUARD vendor_missing_div_row_still_published`
2. Bỏ `share_multiplier == 1.0` khỏi điều kiện D1 → `MUTATION-GUARD vendor_stock_leg_no_overreach`
3. `mismatch` → `broker_only` (dòng gán `vendor_check`) → `MUTATION-GUARD vendor_stock_leg_check_label`
4. Xoá dòng đọc `VENDOR_MISMATCH_REASON` trong `.sh` → `MUTATION-GUARD vendor_alert_reason_routing`
   (MUTATION 6 trong `vendor_mismatch_alert_selfcheck.sh`)

Mỗi mutation: áp bằng `sed`/python vào bản backup, chạy selfcheck xác nhận AssertionError
đúng tên, rồi khôi phục nguyên bản (đã diff-check `restored OK`).

## git status
`git status --porcelain` RỖNG sau toàn bộ quá trình chạy selfcheck + mutation (không rác
state/bus, không leftover temp file trong worktree).

## Chưa xong / ngoài phạm vi R1-R3
- R1 dar:421-422 `except Exception` (vòng 2, detector tắt im lặng khi BQ hỏng) — chưa mở nhánh.
- `kb/projects/cash-vendor-gate-tracking.md.proposed` — chờ Mike duyệt.
- KHÔNG LAND nhánh này — chờ arch-review vòng kế.
