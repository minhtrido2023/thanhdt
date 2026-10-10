# /tmp/arch_rev2/mymut.py sau vòng 3 — 89 mutant: 69 chết (0 chết do crash), 1 sống, 19 hỏng neo

Sống: **M25_unknown_method_frame_ok** — TƯƠNG ĐƯƠNG (reviewer đã ghi nhận): `_assign_frames` chạy sau và đặt lại
`frame_ok=False` cho mọi sự kiện có `frame_note` (`_known()` trả False), nên dòng `adj.frame_ok = False` ở nhánh
`unknown_methods` không quyết định kết quả nào.

Hỏng neo (dòng gốc đã đổi vì gom về một hàm dùng chung) → bản tương đương trong `bin/total_return_mutants.py`
(197 mutant, 197 chết bằng assertion):

| mutant reviewer | vì sao neo đổi | bản tương đương (đều CHẾT) |
|---|---|---|
| M01_orphan_never_vetoes | `_broker_touched` hỏi `cash_witness` thay vì đọc `orphan` 2 đầu mút | noise_ignores_orphan_cash |
| M02_orphan_no_holding_check | "giữ mã" đọc từ chuỗi giá vốn (mọi bản ghi) thay `qmap` 2 ngày | noise_cash_of_account_not_holding |
| M06_touch_step_any_date | cửa sổ theo CẶP bản ghi giao (`meets`) | Rv_M06_touch_step_any_date, Z40_touch_pair_only_by_end_day |
| M06b_touch_only_cash_steps | dòng `if` gộp một dòng | Rv_M06b_touch_only_cash_steps |
| M06c_touch_ignores_owned | như trên | noise_owned_step_counts |
| M07_orphan_only_lastcum, M07b_orphan_only_ex | không còn vòng lặp 2 đầu mút; cửa sổ ±CASH_SLIP_DAYS nằm trong `cash_witness` | Rv_R02_witness_window_lo_zero, Rv_R02_witness_window_hi_zero |
| M08_lagged_also_asks_broker | NAY LÀ CODE (C2) | đột biến ngược: Rv_M08_lagged_skips_broker |
| M08b_lagged_vendor_window_wide | lagged dùng CÙNG cửa sổ [cum, ex], chỉ trừ dòng của sự kiện gốc | Rv_M08b_root_row_vetoes_itself, Z21_vendor_hit_no_lower_bound |
| M10_net_same_sign | điều kiện dấu đã GỠ vì thừa (|a|>tol và |a+b|≤tol ⇒ trái dấu) | — (không còn dòng để đột biến) |
| M10b_net_any_amount | như trên | Rv_M10b_net_any_amount |
| M18_entitle_unknown_becomes_no | "no" chỉ khi sổ có bản ghi ở ngày cuối còn quyền | no_ledger_read_as_not_held, Rv_M18_entitle_unknown_becomes_no |
| M18b_entitle_no_becomes_unknown | như trên | Rv_M18b_entitle_no_becomes_unknown |
| M18c_entitle_only_lastcum_day | NAY LÀ CODE | đột biến ngược: Rv_M18c_entitle_ex_day_record_is_enough |
| M30_vendor_hit_ignores_window | `vendor_hit(a, root)` | Rv_M30_vendor_hit_only_ex_date |
| R01_mask_no_cover_check | thân `_mask_doubt` chuyển sang `dar.cash_witness` | mask_no_cash_coverage_ok, Rv_R01_gate_ignores_witness |
| R02_mask_window_zero | như trên | Rv_R02_witness_window_lo_zero, Rv_R02_witness_window_hi_zero |
| R02b_mask_window_30d | như trên | Rv_R02b_witness_window_hi_30d |
| R02c_mask_window_lo_60d | như trên | Rv_R02c_witness_window_lo_60d |

32 mutant sống ở review lần 2 → nay: M04, M05, M05b, M09b, M09c, M15, M15b, M15c, M15d, M15f, M16, M16b, M16c, M19,
M27, M27b, M33, R07, R12, R20, R22 chết NGUYÊN NEO trong mymut.py; M06b, M07, M08, M08b, M10b, M18c, M30, R02, R02b
chết qua bản tương đương ở bảng trên; M10 đã gỡ; M25 tương đương.
