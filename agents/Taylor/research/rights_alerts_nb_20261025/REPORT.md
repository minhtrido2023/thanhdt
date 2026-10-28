# Rights alert NB — 4 cảnh báo còn mở (job `Taylor_20261025_092232`, user duyệt 25/10 16:20)

Nguồn nguyên văn: verdict arch-review N1 vòng 2 (22/10, phiên Mike `a914df38…`, mục "NON-BLOCKING mới" 1–2
+ "Các mục tác giả không sửa" NB2/NB4) và vòng 1 (NON-BLOCKING 2, 4). Tóm tắt nguồn ở
`agents/Taylor/research/lag_rights_n1_20261022/REPORT.md` mục "Non-blocking còn lại".

Nhánh `fix/rights-alerts-nb-20261025` (worktree `/home/trido/thanhdt/WorkingClaude/wt-rights-alerts-nb-20261025`),
base `fe2af8d30`. CHƯA merge, không cài cron.

| # | Commit | Mục |
|---|---|---|
| 2 | `d347b0bb4` | send_plan_report: chỉ hạ ⚠️→ℹ️ khi phần cắt do CP chờ niêm yết giải thích TRỌN + in `rights_diag` |
| 1 | `847ef7490` | auto_exit_inject: `listing_date >= plan_date` ⇒ còn khoá (tối T−1) |
| 3 | `ccdefb50e` | reconcile_equity: vế phải + phải thu CP quyền đã nộp tiền chưa về broker |
| 4 | `f2cc65b58` | dividend_adjusted_return.credit_frame: truyền `pending_rights` (N4) |

## 1. auto_exit_inject.py — `>` → `>=` (CHẠM LỆNH SELL)
Lỗi: auto_exit chạy tối T−1 với plan_date = listing_date; broker chưa nhả lô quyền ⇒ `ld > plan_date` sai ⇒
lô hết khoá ⇒ ⚠️ "đã tới ngày niêm yết… broker vẫn chưa cho bán" giả mỗi đợt niêm yết.

Test biên ĐO TRƯỚC/SAU (cùng selfcheck mới, code cũ vs mới; `rights_subscription_selfcheck.py`):

| Ca | Code cũ (`>`) | Code mới (`>=`) |
|---|---|---|
| P18 plan_date = listing_date, broker 5.000/0 | ⚠️ cắt 5.000→0 kèm chẩn đoán | ℹ️ khoá 5.000, không ⚠️, không lệnh |
| P18c 1 book, held 19.000 / sellable 14.000 | lệnh 14.000 + ⚠️ cắt 19.000→14.000 | lệnh 14.000, ℹ️ khoá 5.000 |
| P18d mã có thêm 10.000 ở book khác (held 29.000 / sellable 24.000) | lệnh LAG **19.000** | lệnh LAG **14.000**, lô quyền 5.000 bán phiên sau |
| P12 plan_date = listing_date + 1 phiên (đối chứng) | ⚠️ cắt kèm chẩn đoán | không đổi |

**Hành vi đổi:** chỉ đúng một đêm (plan_date = listing_date). Mã chỉ ở 1 book ⇒ lệnh y hệt (arch-review 22/10
nói "lệnh không đổi" — đúng cho ca này). Mã CÓ ở book khác còn sellable dư ⇒ lệnh tối T−1 nhỏ hơn đúng KL lô quyền
khoá (bản cũ bán 19.000 = ăn 5.000 sellable của book kia); lô quyền tự đề xuất lại tối sau. Chiều đổi = bán ÍT hơn,
không nới trần nào. Arch-review 22/10 bỏ sót ca P18d.
Chữ chẩn đoán đổi "≤ plan_date… đã tới" → "< plan_date… đã qua"; runbook bước 6 (REPORT N1) sửa tương ứng.

## 2. send_plan_report.sh:1007-1015 — hạ ⚠️ sai
Nguyên nhân gốc: điều kiện hạ ⚠️→ℹ️ là "mã CÓ MẶT trong `_lk_pending`" (cấp mã), không phải "phần cắt DO khoá
gây ra" ⇒ che ⚠️ của lý do khác (P13: SELL book khác chiếm sellable; lô quyền hết hạn khoá 10 phiên). Dòng ⚠️
cũng không in `rights_diag` (runbook nói có).
Sửa: `locked_shares.split_capped(capped, pending, orders)` — hạ chỉ khi (a) không có `rights_diag`, (b) KL bị cắt
≤ KL khoá của mã, (c) plan không có SELL cùng mã ở book KHÁC. Dòng ⚠️ in `rights_diag`.
Test: `locked_shares.py --selfcheck` +6 ca; `send_plan_report_aei_notes_selfcheck.py` T9a/b/c chạy script THẬT
(sandbox, corp_action_lib stub ⇒ fallback registry, không chạm BQ): trên base T9a/T9b **FAIL** (RED), nhánh 16/16.

## 3. reconcile_equity.py — credit ≠ payment
Khoảng `payment_date ≤ ngày balance` và `credit_date > asof snapshot`: tiền đã rời totalCash, snapshot chưa có lô
⇒ bản cũ residual **+62.500.000** (fixture R4, đo bằng mutant M26 = hành vi cũ). Sửa: vế phải cộng
`rights_paid_not_credited` = Σ KL × giá phát hành (giá vốn, lãi/lỗ 0), in dòng riêng, có trong JSON. Cổng dung
sai/kết luận (§6) không đổi. credit = payment ⇒ 0 (R1c). R4 residual ≈ R1.

## 4. dividend_adjusted_return.py — N4 chưa wire
`credit_frame` gọi `classify_qty_residual` không truyền `pending_rights` ⇒ cổ tức CP credit sớm trong khoảng
chờ VSDC thành `unknown`. Sửa: cùng sổ + cùng phép như `daily_nav_snapshot.main` (`pending_qty` tại ex-date);
KL hưởng quyền pre_credit trừ lô chờ. Test F0 (đối chứng không khai báo ⇒ unknown), F1 (khai ⇒ pre_credit 14.000),
F2 (đã ghi nhận ⇒ 19.000), F3 (broker credit cả lô chờ ⇒ vẫn unknown).
**§21 số công bố:** production chưa có `data/lag_rights/` ⇒ pending 0 ⇒ y hệt theo cấu trúc. Đo thêm:
`dividend_adjusted_return.py --selfcheck` base vs nhánh 347 PASS / 0 FAIL cả hai (khác duy nhất thứ tự in dict ở 1
dòng PASS không liên quan); `portfolio_status.py` SpaceX/ZaloPay × 2026-10-23, 2026-09-30: tỉ suất từng mã y hệt.
(Lưu ý: chạy song song base+nhánh làm `value_radar` ghi lại cache `data/value_radar_series.csv` 16:34 — race tmp,
một lượt fail-safe bỏ dòng radar; file còn nguyên, dòng cuối 2026-10-23. Không phải do code nhánh.)

## Selfcheck (python `$DNA_PYEXE`, `MIKE_BOT_TEST_MODE=1`)
- `rights_subscription_selfcheck.py`: **75/75** dưới `env -u TZ`, `TZ=America/New_York`, `TZ=Pacific/Kiritimati`;
  `--mutants` **29/29 killed** cả 3 TZ (mới: M25 `>=`→`>`, M26/M27 reconcile, M28/M29 credit_frame).
- `send_plan_report_aei_notes_selfcheck.py` 16/16; `locked_shares.py --selfcheck` PASS.
- Hồi quy: xem mục Sweep dưới.
- Sweep hồi quy (`regress_selfcheck_list.txt`, 48 selfcheck = danh sách N1 22/10 trừ `nav_scripts_2account` +
  mọi selfcheck nhắc tới 5 module đã sửa, bỏ 4 file chỉ nhắc tên trong text: notify_discord, code_quality_autodispatch,
  sunday_plan_round, ops_health_check), `env -u TZ`, tuần tự, base `fe2af8d30` (worktree tạm trong cây WC, đã gỡ)
  vs nhánh chạy cùng lúc: **48/48 rc=0 cả hai; 45 giống hệt (rc, #PASS, #FAIL)**; 3 lệch chỉ do ca test mới
  (locked_shares, rights_subscription, aei_notes). Nhóm send_plan_report/gate_block_question chạy lại trên HEAD
  `52d0804af`: giống base. Bảng: `regress_base_fe2af8d30.tsv`, `regress_branch.tsv`, `regress_branch_head_52d0804af_sendplan.tsv`.

## Arch-review (Opus high)
Vòng 1: **APPROVED** (CONFIRMED, high), 0 BLOCKING. Xác nhận mục 1 chỉ làm SELL NHỎ đi (giới hạn bởi held−sellable),
không mất SELL im lặng; mục 3 không đếm 2 lần; mục 4 không đổi số công bố khi chưa có `data/lag_rights/`.
3 NON-BLOCKING, đã sửa ở `52d0804af`:
- NB1 split_capped đếm khoá 2 lần (lô quyền auto_exit đã trừ khỏi desired vẫn nằm trong held−sellable) ⇒ trừ
  `rights_locked` của entry auto mới nhất. Test locked_shares + T9d.
- NB2 mục cắt CAPIT ("chỉ bán phần CAPIT") bị hạ ℹ️ "tự bán phiên sau" sai ⇒ CAPIT không bao giờ hạ.
- NB3 split_capped không bọc try ⇒ lỗi giữ mọi ⚠️ + stderr.
6 mutant thủ công cho vòng 2 đều bị giết. Không chạy arch-review vòng 2 (chỉ NB hiển thị, không chạm lệnh).
