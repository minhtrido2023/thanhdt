# aria-F1 — Phí giao dịch THẬT DNSE (job Taylor_20260913_064536, 2026-09-13)

## Kết luận
**ĐỦ bằng chứng ⇒ đã đổi 0,075% → 0,097% mua/bán** trên đường KẾ TOÁN (`bin/dnse_fee_rates.py`,
`bin/reconcile_equity.py`). Phí là CÔNG THỨC xác định, không phải số trung bình:
**phí DNSE 0,070% (cả 2 chiều) + phí trả sở theo sàn: HOSE 0,027% / UPCOM 0,018%**. Thuế TNCN bán 0,1% tách riêng.

## a) Coverage
- `fetch_all_khoplenh.py` (phân trang; tool canonical chỉ quét 20 email mới nhất): **25 email**, 01/07→17/08/2026, 400 dòng khớp.
- So với fill trong `dnse_raw` (`dnse_fill_events`, 01/07→12/09): **SpaceX 15/15 phiên, ZaloPay 18/18 phiên** có email; 0 phiên chỉ-raw, 0 phiên chỉ-email.
  Từ 18/08→12/09 dnse_raw KHÔNG có fill sàn nào (08-28 chỉ là đăng ký quyền mua MBB) ⇒ không có email là đúng.
- Lệch duy nhất theo mã/chiều: **ZaloPay 10/07 VHC bán — email 1.800cp, dnse_raw 1.200cp** (thiếu lệnh 600cp @57.500 = 34,5tr) → xem F2.
- Kiểm chứng nguồn thứ 3: sao kê tiền tháng 07/2026 (email "Báo cáo tài khoản Chứng khoán tháng", PDF/tiểu khoản, `parse_ledger.py`, chuỗi số dư khớp 100%):
  phí DNSE+sở ZaloPay T7 = 918.667đ (email 918.671), SpaceX T7 = 2.438.259đ (email 2.438.263); thuế bán ZaloPay 529.764 = email.

## b) Phân phối (chi tiết `fee_analysis_out.md`)
- BÁN: N=130 fill — **100%** trong ±0,002pp của 0,097% (DNSE 100% @0,070, sở HOSE 100% @0,027).
- MUA: N=270 fill — 75,6% @0,097% + 24,4% @0,088% ⇒ **KHÔNG đạt "1 tỷ lệ/chiều" theo nghĩa đen**; nhưng tách theo sàn thì 100%:
  DNSE 270/270 @0,070, sở HOSE 204/204 @0,027, UPCOM 66/66 @0,018 (DRI/TV1/SCL). UPCOM = 7,9% giá trị mua; phí VW mua 0,0963%.
  ⇒ Hằng số theo chiều = HOSE 0,097% (lệch ≤0,009pp trên phần UPCOM, về phía thận trọng); `EXCHANGE_FEE_PCT` giữ riêng UPCOM. HNX: chưa có fill nào.
- Theo account×tháng: phí VW 0,0920–0,0970% (thấp hơn ở T8 do tỷ trọng UPCOM), không account nào khác biểu phí.
- Thuế bán: 128/130 fill đúng 0,100%; 2 dòng TCM 09/07 ZaloPay gộp thuế CK quyền 55.000đ.
- Email KHÔNG có cột lãi vay margin. Sao kê T7 có: SpaceX giải ngân 409,32tr / trả nợ 410,13tr; ZaloPay (cash) **phí ứng trước tiền bán UTTB ≈202,5k đ/T7** — chi phí thật chưa có trong reconcile. Phí CKCK 0,3đ/cp bán (~0,001%). Sao kê T08/2026 KHÔNG có mục V. Sao kê.

## c) Thay đổi
| file:dòng (trước sửa) | xử lý |
|---|---|
| `mike/bin/reconcile_equity.py:158` default `--fee-rate-pct 0.075` (+docstring :15, :37; `SELL_TAX_RATE` :26) | → `dnse_fee_rates` mua/bán tách; `--fee-rate-pct` giờ = ép cả 2 chiều |
| `mike/bin/reconcile_equity_realized_selfcheck.py:136,190-191` hardcode 0,075 | → hằng số dùng chung + test hằng số |
| `mike/bin/broker_fill_confirm_selfcheck.py:221-223` nhãn "KHÁC 0,075%" | nhãn |
| `trading_bot/plan_funding_gate.py:118` `FEE_RATE = 0.00075` | **KHÔNG sửa** — cấm chạm trading_bot/; gate tiền lệnh thật |
| `mike/bin/merge_park_orders.py:551` `fee_est_vnd = val*0.00075` | **KHÔNG sửa** — `approve_plan_simple.sh:86,94` dùng trong kiểm tiền duyệt plan; phải đổi CÙNG LÚC với plan_funding_gate, cần user duyệt |
| `mike/bin/bq_freshness_check.sh:657` prompt DollarBill "trừ phí 0.075%" | **KHÔNG sửa** — cùng nhóm sizing plan |
| `pt_v23_*.py`/`converge_fullharness_test.py` `VOLMANAGE_TC 0.00075` | backtest TC (quy ước CLAUDE.md 0,1%) — ngoài phạm vi |
Tác động đường thực thi nếu giữ 0,075%: hụt 0,022pp/lệnh (22k đ/100tr) — nhỏ hơn biên giá, không gấp.

Reconcile (snapshot aria-A1, offbook như A1):
| | residual trước | sau | dư sau diễn giải trước | sau |
|---|---|---|---|---|
| SpaceX 08-28 | +4,380tr (0,445%) | +4,189tr (0,426%) | +1,377tr (0,140%) | **+0,701tr (0,071%)** |
| SpaceX 09-11 | +3,985tr (0,413%) | +3,795tr (0,393%) | +0,978tr (0,101%) | **+0,302tr (0,031%)** |
Selfcheck: `reconcile_equity_realized_selfcheck` 32 PASS (23 cũ + 9 mới; env -u TZ, cwd /tmp, TZ=America/New_York + $DNA_PYEXE), 6/6 mutation bị giết;
`nav_cum_dividend_selfcheck` 38 PASS; `nav_scripts_2account_selfcheck` PASS; `broker_fill_confirm_selfcheck` 51 PASS.
