---
kind: incident
date: 2026-08-02
topic: nav-cum-dividend-double-count
title: >-
  daily_nav_snapshot.py đếm 2 lần cổ tức tiền mặt vào tối ngày chốt quyền (last-cum-date) —
  NAV lịch sử SpaceX/ZaloPay sai 6 dòng trên 5 phiên, tự triệt tiêu nên sống sót mọi đối soát
status: fixed
source: bus (Winston_20260802_082040, Winston_20260802_085555), commit 354eaa88
---

# NAV đếm 2 lần cổ tức tiền mặt vào tối ngày chốt quyền (last-cum-date)

## Sự cố

DNSE ghi `cashDividendReceiving` vào `totalCash` ngay TỐI ngày cuối còn hưởng quyền
(last-cum-date), trong khi giá đóng cửa phiên đó VẪN CÒN quyền (chưa trừ cổ tức) — nên
`NAV = cổ phiếu(giá cum) + tiền(đã gồm khoản phải thu)` đếm trùng phần giá trị cổ tức 1 lần.
Phiên sau (ex-date), giá rớt đúng bằng cổ tức, khoản trùng tự triệt tiêu — **NAV cuối tháng vẫn
đúng**, đây chính là lý do lỗi sống sót qua mọi đối soát trước giờ (không ai bắt được vì mọi
check chỉ nhìn NAV tại 1 mốc xa, không nhìn per-day quanh ex-date).

**Cùng họ nguyên tắc với `coding_guidelines.md §21`** (tỉ suất per-position phải cộng lại cổ
tức tiền mặt) nhưng khác tầng: §21 là lỗi ở BÁO CÁO tỉ suất per-position; sự cố này là lỗi ở
chính **NAV lịch sử ghi vào `nav_history_{account}.csv`** — nguồn mà mọi báo cáo/backtest paper
đọc lại.

## Phát hiện

Winston, job `Winston_20260802_082040` (finding `fix-nav-dem-2-lan-co-tuc-cum-date`,
08:37:15Z) — không qua alert tự động nào, phát hiện trong lúc làm việc khác liên quan cổ tức
(cùng ngày với saga Price/Close, §21 vừa ship).

## Root cause (chi tiết)

- Bản ghi `balances` cuối cùng của phiên T (>=16:00) đã có `cashDividendReceiving` tăng, nhưng
  giá đóng cửa phiên T mà hệ thống dùng để MTM vẫn là giá **cum-dividend** (giá thật, ex-date là
  phiên T+1) → cộng cả khoản phải thu VÀ giá trị cổ phiếu chưa trừ quyền = đếm 2 lần.
- Bug phụ phát hiện khi viết fix: `dividend_adjusted_return.py`'s BQ query mặc định chỉ trả
  100 dòng và **CẮT ÂM THẦM** — batch nhiều mã chỉ nhận về 4 mã đầu bảng chữ cái, bỏ sót ex-date
  thật của NCT/VCB. Fix: thêm `--max_rows=200000` + raise khi chạm trần (không âm thầm cắt).

## Fix

- `daily_nav_snapshot.py`: thêm `cum_dividend_double_count()` + `previous_balance()` — loại
  khoản phải thu cổ tức CHƯA qua ex-date khỏi cash dùng để tính NAV; thêm cột
  `cum_dividend_excl` vào `nav_history_*.csv` để minh bạch số đã loại. Bất biến giữ nguyên:
  `nav = mtm_stock + cash - margin_debt + offbook_assets`.
- `dividend_adjusted_return.py`: refactor về 1 cài đặt duy nhất
  (`_price_ratio_rows`/`_scan_jumps`/`detect_adjustments_batch`) cho logic tỉ số Close/Price,
  fix bug cắt-100-dòng ở trên.
- Selfcheck mới: `mike/bin/nav_cum_dividend_selfcheck.py` — 38/38 PASS trên dữ liệu THẬT (dnse_raw
  + BQ), chạy dưới `env -u TZ` (guidelines §16/§19). Ca âm quan trọng nhất: SpaceX 09/07
  `cashDivRecv +2.400.000` (MBB) nhưng 09/07 CHÍNH LÀ ex-date → KHÔNG được trừ — bản cài đặt
  ngây thơ kiểu "hễ tăng thì trừ" sẽ FAIL đúng ca này.
- **quant-skeptic CONFIRMED (high)** — tái lập độc lập qua 4 kênh không lấy từ Winston: broker
  jsonl delta, BQ Close/Price tươi cho cả 14 mã ZaloPay cửa sổ 20-26/07, vị thế trước/sau (loại
  khả năng chia tách cổ phiếu vì qty không đổi), giải hệ 2 phương trình cross-account residual 0.

## Dữ liệu đã sửa (verify độc lập 3 nguồn: broker raw delta / vị thế point-in-time / ex-date BQ)

| Ngày | Account | NAV cũ | NAV mới | Loại (VND) | Mã | Ex-date |
|---|---|---|---|---|---|---|
| 2026-07-16 | SpaceX | 957.558.637 | 956.703.637 | 855.000 | BID 1900×450 | 2026-07-17 |
| 2026-07-24 | SpaceX | 910.995.894 | 906.995.894 | 4.000.000 | NCT 500×8000 | 2026-07-27 |
| 2026-07-27 | SpaceX | 900.428.641 | 897.128.641 | 3.300.000 | SAB 1100×3000 | 2026-07-28 |
| 2026-07-16 | ZaloPay | 953.593.885 | 953.188.885 | 405.000 | BID 900×450 | 2026-07-17 |
| 2026-07-24 | ZaloPay | 849.855.112 | 846.871.112 | 2.984.000 | NCT 373×8000 | 2026-07-27 |
| 2026-07-22 | ZaloPay | 886.083.813 | 885.251.313 | 832.500 | CTG 1050+VCB 800×450 | 2026-07-23 |

Dòng cuối (ZaloPay 07-22) ban đầu **NGOÀI phạm vi 5 dòng user đã duyệt** — Winston ghi bus
question `nav-zalopay-2207-dong-thu-6-can-duyet`, user duyệt (`decided_by: "user"`, đúng
`coding_guidelines.md §20`), sửa xong 09:13:18Z, quant-skeptic CONFIRMED lần 2.

SpaceX 2026-07-09 (+2.400.000 MBB) **KHÔNG phải lỗi này** — đã kiểm tra kỹ, tiền vào đúng phiên
ex nên không đếm trùng.

Invariant `nav = mtm_stock + cash - margin_debt + offbook_assets` giữ đúng trên toàn bộ file sau
sửa (SpaceX 20/20 dòng, ZaloPay 19/19 dòng).

## Tác động

Tuần 20-24/07 của ZaloPay từng báo % biến động sai lệch nhẹ (NAV phình tạm 1 phiên rồi tự triệt
tiêu). NAV cuối tháng 7 KHÔNG bị ảnh hưởng (đã tự triệt tiêu trước khi tới điểm đối soát tháng).
Báo cáo tuần 20-24/07 đã gửi trước khi phát hiện — không tự động thu hồi/sửa lại (nợ đã biết,
không phải hành động mới trong sự cố này).

## Lesson

Đây là ví dụ nữa (thứ 3 trong ngày, sau saga Price/Close và LAG liquidity) của cùng một hình
dạng: **1 identity/invariant tổng (NAV cuối kỳ) đúng có thể che giấu 1 lỗi per-event bên trong**
— đối soát chỉ ở mốc xa không đủ, cần check tại đúng thời điểm sự kiện (ex-date) xảy ra. Xem
cross-link `coding_guidelines.md §21` (per-position return cùng họ cổ tức, khác tầng: báo cáo
thay vì NAV gốc).

## Việc treo

- Không có — cả 6 dòng đã sửa, đã user duyệt, quant-skeptic CONFIRMED cả 2 vòng.
