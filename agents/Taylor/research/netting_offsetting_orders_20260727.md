# Netting lệnh ngược chiều cùng mã — thiết kế & triển khai (2026-07-27)

Job `Taylor_20260727_032906`. Case gốc: plan ZaloPay 2026-07-27 có SELL VPB 800
(book `custom30V_parking`, trim) + BUY VPB 700 (book `LAG`, entry) trong **cùng 1
plan/ngày/account** — 2 lệnh ngược chiều cùng mã gửi độc lập ra broker. Phí thật: bán
14.940 + mua 13.073 = **28.013đ**; nếu net thành 1 lệnh SELL 100cp chỉ tốn **1.868đ** →
lãng phí **26.145đ** + 1 lượt đi qua spread bid-ask.

## Chẩn đoán gốc
- Broker (DNSE) chỉ thấy **TỔNG** số cp một mã trong một account. "Book" (BAL/LAG/CAPIT/
  custom30V_parking/…) là **sổ sách nội bộ**, không phải sub-account. 2 book mua/bán ngược
  chiều cùng mã = có thể chuyển nội bộ ở cùng giá TT (0 phí/spread), chỉ phần chênh lệch
  cần chạm thị trường.
- `V23Strategy.build_plan` (strategies.py:311-409) **tự net sẵn**: gom 1 `target[t]`/mã rồi
  diff vs vị thế thật → tối đa 1 lệnh/mã, không bao giờ sinh 2 chiều. Case cần gộp **chỉ đến
  từ plan LLM-authored của DollarBill** (mỗi book sinh lệnh độc lập, không consolidate).
  → Netting là **lưới an toàn ở tầng chuẩn hoá plan**, không phải sửa strategy.
- Ledger từng book **không** suy từ lệnh đã gửi: `executor.py` book-agnostic (journal FILL
  không ghi `book`); sổ book nằm ở tầng trên (paper-mirror / record DollarBill). ⇒ gộp ở
  tầng đặt lệnh **không đụng** kế toán/báo cáo từng book (đúng yêu cầu #2).

## Thiết kế — `trading_bot.plan.net_offsetting_orders(plan) -> (plan, adj)`
Cùng chữ ký/pattern với `cap_capit_orders`/`cap_lag_orders`/`filter_excluded_tickers`.
- Gom order theo ticker. Chỉ net khi 1 mã có **CẢ** buy lẫn sell. Một chiều (kể cả nhiều
  lệnh cùng chiều) → **giữ nguyên**, đúng thứ tự (yêu cầu #5).
- `net = Σqty_buy − Σqty_sell`; `internal = min(Σbuy, Σsell)`.
  - `net = 0` → **0 lệnh** ra broker (100% nội bộ); adj ghi `INTERNAL_ONLY` (yêu cầu #3).
  - `net ≠ 0` → **đúng 1 lệnh** theo chiều bên lớn, qty=`|net|`, `book` = book của **leg lớn
    nhất bên dominant** (phần dư của bên lớn sau khi cấp nội bộ cho bên nhỏ) (yêu cầu #4).
    Kế thừa `ref_price/play_type/priority(min bên dom, giữ sell-first)/urgency(high nếu có)`;
    `dcf_check`/`dcf_override_reason` giữ khi net là BUY, bỏ khi net là SELL.
- `note` lệnh net + `adj` ghi đủ `buy_legs`/`sell_legs` (book+qty+note gốc) → audit/báo cáo
  không mất thông tin book (yêu cầu #2).

## Thứ tự pipeline (yêu cầu #6): filter_excluded → **NET** → cap_capit → cap_lag → approval
Net **TRƯỚC** các trần %ADV, có chủ đích: trần %ADV đo **tác động thị trường**, mà chỉ phần
NET mới thật sự chạm thị trường (phần nội bộ tiêu thụ 0 thanh khoản). Kiểm chứng bằng
selfcheck F/F2: bên bán lớn → net SELL → trần %ADV (chỉ áp buy) không đụng (đúng, chỉ bán
|net|cp ra thị trường); bên mua lớn → net BUY → `cap_lag` **vẫn** áp trần lên phần dư (chứng
minh bằng trần cực nhỏ → BLOCK). Thuần plan.py, **KHÔNG** đụng executor.py (`_child_qty`,
participation cap…) — chỉ giảm SỐ LƯỢNG lệnh gửi ra broker.

## Selfcheck — `net_offsetting_orders_selfcheck.py`, 35/35 PASS
A case thật VPB · B net=0 · C bên mua lớn (dcf giữ) · D khác mã/1 chiều giữ nguyên ·
E bảo toàn kinh tế (Δbroker = ΣΔbook) · F/F2 tích hợp thứ tự vs cap_lag · G nhiều leg/bên.
Regression: lag_adv_cap 29/29, excluded_tickers, approval_gate, capit_participation_cap — PASS.
Demo trên plan ZaloPay thật (read-only): 2 lệnh → 1 lệnh SELL 100cp, phí 28.013→1.868đ.

## Trạng thái wiring (AN TOÀN)
Hàm nằm sẵn trong `plan.py` (INERT — chưa ai gọi ở live). **Chưa wire vào `bot_execute.py`**
(giữ live path nguyên vẹn tới khi verify) — đúng norm "verify trước, wire+commit sau" như
`cap_lag_orders` đã làm. Diff wiring 6 dòng để Mike áp SAU khi quant-skeptic CONFIRMED:
`mike/agents/Taylor/research/netting_wiring.patch` (đường dẫn đầy đủ từ WORKDIR — bản trước
ghi tắt `research/...` gây nhầm; đính chính 2026-07-27 job Taylor_20260727_040719). **KHÔNG
đụng plan hôm nay** (đã duyệt/thực thi).

## Reconciliation post-fill — trả lời killer objection quant-skeptic (2026-07-27, job Taylor_20260727_040719)

**Objection**: netting gộp SELL 800 park + BUY 700 LAG → broker chỉ thấy −100; ai ghi phần
chuyển nội bộ (park −700 / LAG +700) vào sổ từng book? Nếu wire mà không có bước này, sổ từng
book lệch khỏi broker theo thời gian.

**Kết quả điều tra (chứng cứ trên code hiện có — KHÔNG bịa kiến trúc):** ở LIVE **không tồn
tại sổ vị thế từng book tích-luỹ-từ-fill** để mà "lệch":
- Journal FILL (`executor._journal`) book-agnostic (cột: ts/event/parent_id/ticker/side/
  child_oid/qty/price/filled_total/note — không có `book`).
- Tầng kế toán/NAV (`daily_nav_snapshot.py`/`compute_active_nav.py`/`reconcile_equity.py`)
  book-agnostic: NAV = mtm_stock(TỔNG broker) + cash − debt + offbook. Mọi chữ "book" ở đó là
  "off-book" (Trứng vàng), không phải per-book.
- Vị thế "từng book" chỉ tồn tại: (a) paper-mirror `pt_v22_dt5g_open_positions.csv` — do engine
  mô phỏng ghi, tái dựng + scale NAV MỖI ngày rồi diff vs vị thế TỔNG broker (không đọc fill);
  (b) field `book` trên PlannedOrder — chỉ routing tier/khoá trần %ADV/hiển thị, vòng đời 1 plan.
- DollarBill lập plan T+1 tái dựng từ recommend CSV + vị thế TỔNG thật + active_nav — không đọc
  sổ per-book bền nào.
- **Bất biến bảo toàn** (đã test, case E netting selfcheck): net = Σbuy − Σsell = TỔNG Δ per-book
  dự kiến ⇒ vị thế TỔNG broker luôn = tổng-các-book dự kiến; target ngày mai tái dựng từ
  (paper-mirror) − (TỔNG broker) tự hấp thụ cả khớp một phần. Netting **trong suốt** với bước này.
- Khớp MỘT PHẦN khiến "chẻ fill về từng book" không định nghĩa được → thêm lý do vì sao sổ
  per-book-từ-fill vừa không có vừa không nên bịa.

⇒ Dựng một "sổ vị thế per-book" sẽ là **bịa kiến trúc không tồn tại, không có consumer, và
false-fire trên khớp một phần** — đúng thứ dispatch cấm. Thay vào đó, dựng phần lõi HỢP LỆ &
ĐỊNH NGHĨA ĐƯỢC của objection:

**`trading_bot/netting_recon.py` — `reconcile_netted_fills(adj, get_net_fill, ref_price_of,
broker_net_delta=None)`** (INERT, chưa wire, giống `net_offsetting_orders` khi mới viết). Chạy
SAU khi có FILL THẬT:
1. Audit-trail: mỗi mã netted ghi 2 leg gốc (book+qty) định giá CÙNG MỘT giá — NET≠0 dùng giá
   khớp THẬT của lệnh net (từ xác nhận khớp broker/journal FILL, §6 — KHÔNG phải giá đặt lệnh);
   NET=0 (không có lệnh net) dùng ref_price plan (2 leg bù trừ, P&L gộp=0 dù giá nào). Objection #1/#2/#3.
2. Conservation guard FAIL-LOUD: phần THẬT chạm broker (khớp có dấu) = Σ Δ book chạm-thị-trường;
   nếu caller cấp `broker_net_delta` (đọc positions API sau−trước) phải khớp — lệch ⇒ raise +
   để caller báo Mike/user, KHÔNG tự gộp (§5/§6). Objection #4 dạng mạnh.
3. `write_recon_log()` ghi JSONL atomic (tmp+os.replace) `netting_recon_<acct>_<date>.jsonl`.

**Điểm wiring đề xuất** (bot_execute.py, cuối `run()` sau phiên đóng & fills chốt): đọc
(filled_qty, avg_price) của parent `NET-<ticker>-<SIDE>` từ xác nhận khớp broker; tuỳ chọn đọc
positions API để cấp `broker_net_delta` (cross-check mạnh nhất). failures non-empty → bus event
+ notify Mike/user, KHÔNG tự thực thi tiếp.

**Selfcheck `netting_recon_selfcheck.py` — 44/44 PASS**: NET≠0 khớp đủ @ giá thật · NET=0 @ ref
bù trừ · FAIL LOUD khi thiếu giá khớp · FAIL LOUD khi Σ(book)≠broker · khớp một phần không
false-fail · FAIL LOUD NET=0 thiếu ref · FAIL LOUD NET=0 ghost broker-delta · NET BUY dấu dương ·
lệnh net 0-filled @ref · adj hỏng · write_recon_log atomic/append/rỗng→None. net_offsetting_orders_selfcheck 35/35 giữ nguyên.
