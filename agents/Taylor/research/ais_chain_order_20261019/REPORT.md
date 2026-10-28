# AIS sai effective_date — luật chuỗi `_chain_redate` (job Taylor_20261019_052148, 2026-10-19)

Nhánh `feat/ais-chain-order-20261019` @ c22ce4c60 (repo /home/trido/thanhdt, worktree
`/home/trido/thanhdt/wt-Taylor_20261019_052148`). CHƯA merge.

## Luật (tổng quát, không theo mã)
Trên các AIS nhìn thấy tại asof (vendor `effective_date <= asof`):
1. Gộp theo `shares_total_after`; cùng total mà khác delta/khác ngày ⇒ không áp.
2. Xếp total tăng ngặt; mọi mắt xích `delta>0` và `|prev+delta-total|/total <= EXPLAIN_TOL`.
3. Dòng "sai ngày" = eff muộn hơn ngày của một dòng đứng sau nó trong chuỗi. Không có ⇒ không áp.
4. Gán `public_date` cho dòng sai ngày; dãy ngày dọc chuỗi phải tăng ngặt. Thiếu public ⇒ không áp.
Áp ⇒ mọi dòng `chain_certified` (verdict OK, dòng đầu NO_PRIOR) và downstream chạy trên ngày đã sửa.
Không áp ⇒ hành vi cũ từng byte (C4.* so với chính module tắt luật).
Duy nhất: delta>0 + total tăng ngặt ⇒ thứ tự liền mạch nào cũng là thứ tự theo total ⇒ không có 2
thứ tự liền mạch, không vòng. Dòng bịa giữa chuỗi cần 2 trùng hợp số học cùng lúc; ở đuôi chỉ là phép
thử (b) cũ.

## Tác động (measure.py, audit_unlock.py; diff_cells.csv, stat.json)
965 mã có AIS. 2026-10-19 live: 10 None→số, 0 đổi số, 0 số→None (ELC 117.748.108, DCF, HKT, HMS,
KSH, PSD, TAL, TCB 7.086.240.414, TLG, VTK). PIT: 13 None→số, 0 đổi.
PIT tháng 2014-01..2026-10 (148.610 ô): 867 None→số (AIS_EXACT 278 / ANCHOR_ONLY 198 /
FIN_FALLBACK 391), 9 đổi số, 0 số→None.
9 đổi số: CMX 2022-12..2023-02 100.998.990→101.898.990 và HAX 2022-12/2023-01 49.516.982→56.943.434,
2024-11..2025-01 93.427.565→107.439.681 — cũ phục vụ dòng AIS sai ngày làm neo mới nhất; AIS + quý
sau xác nhận số mới (sửa ĐÚNG). HAX 2023-02-01 49.516.982→71.943.434 FIN_FALLBACK: cả hai sai (thật
56.943.434; đợt 15tr ex 2023-02-13) — look-ahead đã biết của chính sách FIN_FALLBACK.
Chữ ký look-ahead trên 867 ô mở khoá: 104 ô; 45 FIN_FALLBACK (chi phí chính sách đã chấp nhận
2026-08-19), 40 là lăn ISS ex<=asof hợp lệ (AIS sau chỉ niêm yết trễ), 19 ANCHOR_ONLY (dòng quý đã
qua cổng giải thích).
R3 production basket (`custom_basket.py`) KHÔNG dùng oshares_live ⇒ pin R3 không đổi; chỉ
`custom30_core_select_audit.py` (audit) qua oshares_pit thấy các ô trên.

## Selfcheck
oshares_live 122/122 (102 cũ + 20 C*) × {unset, LA, Kiritimati}; quét rộng: oshares_pit 49/49,
oshares_wire 11/11, corp_action_daily 201/201, treasury monitor 41/41, canary 53/53, broker_detect
788/0, exdate_frame 63/63, discretionary_margin_gate 150/0, rating8l_icb_pit 17/0/2skip,
rating_8l_history_bank_aq PASS (py3.12) — cả 3 TZ. Mutation (mutate.py): 13/14 chết; M5 tương đương.

## Đề xuất monitor treasury (không sửa)
`treasury_buyback_window_monitor.py:150` xếp AIS theo `COALESCE(effective_date, public_date)`. Đồng bộ:
lấy thứ tự/ngày từ `oshares_live._visible_ais` (hoặc `_chain_redate` trên các dòng đã đọc) để
"AIS trước/sau" khớp với số oshares_at; hiển thị "(vendor eff X)" khi dòng bị dời.
