# dividend_adjusted_return.py — vòng 4 arch-review: lookup_failed có consumer (2026-09-24)

Dispatch: `Taylor_20260924_033534` (attempt 2/2, tiếp nối `dividend_broker_qty_and_vendor_lookup_20260924.md`).
Nhánh `fix/dividend-broker-qty-vendor-label` (worktree `mike/agents/Taylor/wt-dividend-fix`).
Commit: `f3b5b96b`. **CHƯA LAND** — cho Mike arch-review vòng 5.

Arch-review độc lập vòng 4 xác nhận V1 (`085bd6cb`) SẠCH về hành vi (đo lại đúng 3 mã BID/MBB/VCB,
135 cặp ZaloPay, SpaceX 0 cặp, `--resolve` byte-identical cả hai cây, 1/8 sự kiện qua cổng công
bố và KHÔNG đổi ⇒ không cần đính chính). V2 (`5a95864e`) đúng hướng nhưng **NEEDS_CHANGES**: nhãn
`lookup_failed` không có consumer nào — nó DỜI sự im lặng lên một tầng, không xoá nó.

## R1 (CHẶN V2) — `lookup_failed` không có consumer, và tự sinh chẩn đoán sai §29

`entitled_gross()` chỉ `if a.vendor_check == "lookup_failed": continue` — cổ tức mất khỏi kỳ
vọng công bố mà KHÔNG kênh nào tới Winston (khác nhánh `mismatch` vốn có `mismatches.append(...)`
+ dòng máy đọc `VENDOR_MISMATCH_ALERT`). Nặng hơn: mã đó `gross=0` bật nhánh `fails_no_div` khiến
`report_return_gate.py` in "KHÔNG có cổ tức ⇒ lệch KHÔNG phải do thiếu cộng cổ tức... sai CƠ SỞ
GIÁ" — SAI CỨNG theo đúng lớp lỗi §29 mà reviewer đã biết trước (nhánh mismatch tự vô hiệu hoá
câu đó ở cùng vị trí, `lookup_failed` thì chưa).

**Sửa** (`bin/report_return_gate.py`):
1. `entitled_gross()` nổi `lookup_failed` lên `mismatches` với reason cố định `"lookup_failed"`
   (không đọc `vendor_mismatch_reason` — trường đó chỉ có nghĩa cho nhánh mismatch thật).
2. `run_gate()` phát dòng người-đọc RIÊNG ("KHÔNG TRA ĐƯỢC nguồn vendor... lỗi hạ tầng BQ, KHÔNG
   phải vendor xác nhận 0 sự kiện") + tag máy đọc MỚI `VENDOR_LOOKUP_FAILED|acct|mã|ex|broker|published`
   (5 trường — cố ý KHÔNG tái dùng `VENDOR_MISMATCH_ALERT` 7 trường: sentinel `vendor_ps=0.0` sẽ
   bị đọc nhầm thành "vendor xác nhận 0đ", tái tạo đúng §29).
3. Loại mã có `lookup_failed` khỏi câu "sai CƠ SỞ GIÁ" (nguyên nhân đúng đã in ở khối LỆCH NGUỒN
   VENDOR rồi — không chồng chẩn đoán sai lên chẩn đoán đúng).
4. `bin/vendor_mismatch_alert.sh` học tag mới: vòng đọc riêng (không REASON_MAP, không vendor_ps),
   tiêu đề Discord riêng khi CA THUẦN lookup_failed ("VENDOR LOOKUP THẤT BẠI — lỗi hạ tầng BQ", để
   không nói "hai nguồn bất đồng" cho ca chưa hề đối soát được), việc-cần-làm riêng ("chạy lại khi
   BQ khoẻ", không giao Winston đối soát số trừ khi lỗi lặp nhiều lượt).

## R2 (test-only) — 2 lỗi trong chính selfcheck, không phải bug sản xuất

- `check()` (dividend_adjusted_return) nổ `TypeError` khi `got=None` thay vì in FAIL — CHE assertion
  có tên đứng ngay sau trong cùng mục, vi phạm luật harness "mutation chết bằng assertion có tên".
  Sửa: `got is None` → in FAIL + đếm, return sớm.
- Fixture mục 25 ghi bản ghi CŨ (08:00) TRƯỚC bản MỚI (09:00) trong file ⇒ nhánh so-sánh
  `ts < day_last_ts[day]` không bao giờ fire (coverage 0% trên chính đường cần test); assertion
  `broker_qty_cross_record_double_count` VACUOUS vì cấu trúc gather-then-sum khiến cộng chéo bất
  khả thi bởi construction. Sửa: đảo thứ tự ghi file (CŨ đứng SAU) + thêm assertion có tên
  `broker_qty_latest_record_of_day` ghim đúng bất biến.

## R3 (không chặn, chỉ ghi nhận theo yêu cầu reviewer)

`bin/corp_action_daily.py:1643` gọi `bq_corp_action(tk, asof, include_announced=True)` KHÔNG bọc
try. Sau R1/V2 (bỏ nuốt exception), BQ lỗi hạ tầng làm exception nổi lên `main()`'s top-level
handler (dòng ~1930): `traceback.print_exc()` + Telegram/Discord `notify()` + `bus("error", ...)`
+ `rc=5`, KHÔNG publish snapshot corp-action 07:30 (cron LIVE, chạy TRƯỚC khi user duyệt plan).
Reviewer đánh giá: ồn ào + fail-closed là CHẤP NHẬN ĐƯỢC, còn TỐT HƠN hành vi cũ (`continue` lặng
lẽ ⇒ snapshot thiếu đúng cổ tức tiền của mã đang giữ). Không sửa trong phạm vi dispatch này — cần
một dispatch riêng nếu muốn wrap try quanh call-site này.

## Verify

- `dividend_adjusted_return.py --selfcheck`: 159/0 (148→151→159 qua 3 vòng).
- `report_return_gate.py --selfcheck`: 85/85 (75→85).
- `bin/vendor_mismatch_alert_selfcheck.sh`: 68/0 (57→68, mutation 7 mới ghim tag lookup_failed).
- `report_return_gate_selfcheck.py --root-only`: PASS.
- Cả 4 selfcheck trên chạy PASS ở **4 môi trường TZ**: mặc định (ICT), `env -u TZ`,
  `TZ=Pacific/Kiritimati`, `TZ=UTC`.
- `git status --porcelain` rỗng sau commit `f3b5b96b`.

### Tự bắn 4 mutation, xác nhận chết bằng ASSERTION CÓ TÊN (không phải crash)

| # | Mutation | Assertion chết |
|---|---|---|
| 1 | `"lookup_failed"` → `"unavailable"` (dòng gắn nhãn trong `bq_corp_action`'s except) | `MUTATION-GUARD lookup_failed_label` |
| 2 | Xoá nhánh `if a.vendor_check == "lookup_failed"` trong `entitled_gross()` | `MUTATION-GUARD entitled_gross_detect_mismatch` |
| 3 | `out[key] = out.get(key, 0.0) + float(...)` → `out[key] = float(...)` trong `broker_qty()` | `MUTATION-GUARD broker_qty_last_lot_wins` |
| 4 | `ts < day_last_ts[day]` → `ts > day_last_ts[day]` trong `broker_qty()` | `MUTATION-GUARD broker_qty_last_lot_wins` (bắt trước khi tới `broker_qty_latest_record_of_day` — cùng key/value 427.0, cả hai assertion đều hợp lệ cho ca này) |

Mỗi mutation đều có chân control (bản KHÔNG mutation, PASS đầy đủ) chạy ngay trước và sau, trong
worktree `wt-dividend-fix`.

## Còn mở (không thuộc phạm vi dispatch này)

- Mike duyệt `kb/projects/cash-vendor-gate-tracking.md.proposed` (từ vòng 2/3).
- `dar:421-422` (vòng 2) `except Exception` ở một call-site KHÁC — đã xử lý ở đúng call-site này
  (`bq_corp_action`) nhưng cần audit xem còn call-site nào khác nuốt lỗi tương tự không; chưa mở
  nhánh riêng.
- Dispatch riêng để wrap try quanh `corp_action_daily.py:1643` nếu Mike muốn giảm ồn cron 07:30.
