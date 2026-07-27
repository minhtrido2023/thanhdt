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
`research/netting_wiring.patch`. **KHÔNG đụng plan hôm nay** (đã duyệt/thực thi).
