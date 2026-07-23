# Mike fleet — context planning (DollarBill only)
> Phần CHUYÊN BIỆT cho việc lập plan T+1 — không lặp lại safety core (đã import riêng ở
> CLAUDE.md), không có chi tiết phương pháp backtest/DSR/PBO (việc của Taylor, chỉ cần
> KẾT QUẢ để lập plan, không cần cách tính ra). Cần domain khác ngoài đây (backtest chi
> tiết/pháp lý/thực thi)? Đọc `kb/context_pack.md` qua Read tool nếu tự tin đúng chỗ, hoặc
> escalate Mike — đừng đoán.

## V2.4 — chiến lược production (tóm tắt, không phải phương pháp)
2 book: **BAL** (momentum SIGNAL_V11, yieldcombo 1/PE+1/PCF) + **LAG** (PEAD/earnings drift).
Allocator `w_LAG` theo regime: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
**NEUTRAL parking = custom30V**, target **70%** phần idle cash khi BAL/LAG rỗng (đã backtest xác
nhận thắng risk-adjusted so với 93.8-94.7% go-live gốc — Sharpe 1.78 vs 1.66, DD -16.5% vs -18.8%).
Đổi target 70% cần field `risk_dial_confirmed_by_user` + `risk_dial_warning_acknowledged` trong
`trading_rules.json`, thiếu 1 trong 2 → Mafee tự block plan.

## DT5G — market regime, ĐỌC ĐÚNG BẢNG (bẫy đã gây sự cố thật)
Chỉ đọc **`tav2_bq.vnindex_5state_dt5g_live`** qua `get_gated_state()`. **KHÔNG đọc bare
`vnindex_5state`** — đó là v3.4b BASE (không DT-gate, không macro-cap, ~153 transitions), KHÁC
production (~49 transitions). Sự cố thật 2026-07-11: 4 script canonical đọc nhầm bảng base, khiến
1 book paper vào lệnh trên tín hiệu BULL giả trong khi state thật là NEUTRAL.

## 8L Rating — dùng làm gate, không phải tilt
Composite v3 (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor bắt buộc:
ROE_Min3Y≥0 ∧ CF_OA_3Y>0. Rating là **binary gate ≤3**, không dùng để xếp hạng liên tục.

## excluded_tickers — sizing phải dùng active_nav
Khi account có `excluded_tickers` (vd ZaloPay/DGC — xem safety core), lập plan phải size theo
`active_nav` (= total NAV trừ market_value của mã bị loại), KHÔNG dùng total NAV — dùng
`bin/compute_active_nav.py --account <label>` để tính, không tự suy ra từ NAV tổng.

## Same-day pricing — DNSE API, KHÔNG BAO GIỜ BigQuery (bright-line rule)
BQ (`tav2_bq.ticker`/`ticker_1m`) chỉ sync qua đêm (`sync_bq_cache_daily.sh`, 23:45 ICT) — script
chạy TRƯỚC giờ đó mà đọc BQ cho giá "hôm nay" luôn là giá HÔM QUA, cấu trúc chứ không phải thỉnh
thoảng. Sự cố thật 2026-07-09: 1 lệnh trong plan T+1 định giá lệch +5.7% do đọc nhầm BQ close cũ.
Mọi tính toán same-day (ref price cho plan, NAV/exposure live) PHẢI đọc DNSE (`dnse_api.py`
secdef/latest_trade/positions/balances), không phải BQ.

## Plan file — tên chính thức, không dùng suffix
File plan CHÍNH THỨC là `plan_<account>_<date>.json` — bot (`load_plan()`) chỉ đọc đúng tên này.
Sửa/duyệt lại 1 plan đã có → ghi ĐÈ đúng tên file gốc, KHÔNG tạo bản `_v2`/suffix khác (bot sẽ
không thấy bản mới, chạy nhầm bản cũ — sự cố thật 2026-07-06).

## Lịch lập plan (T2-T6, giờ ICT)
17:30 BQ freshness check → dispatch DollarBill lập plan T+1 → 19:30 gửi plan report vào Discord
(topic DollarBill plan channel) → user duyệt trước 08:45 sáng hôm sau (preflight). Plan T+1 KHÔNG
sẵn sàng trước deadline → **escalate thật** (Telegram + Discord + bus event `question`
`plan-t1-not-ready`), KHÔNG tự retry/re-dispatch — quyết định bước tiếp theo là của người.

## 2 tài khoản LIVE hiện tại — xem safety core (SpaceX margin, ZaloPay cash-only+excluded DGC).

## LAG entry EXCLUDE list — kiểm tra TRƯỚC khi đưa mã LAG mới vào plan (cập nhật 2026-07-23)
Trước khi thêm bất kỳ mã LAG_HI/LAG_LO nào vào plan, luôn hỏi: mã này có từng bị user loại
tường minh không? Case đã biết (KHÔNG được tự ý mua lại trừ khi user ra chỉ đạo mới):
- **IVS**: loại 2026-07-21 (phương án C, user quyết) — thanh khoản mỏng (ADV3T ~175-180M, phải
  ADV-cap xuống ~10% mới mua được), ngoài `universe_pit`, chất lượng yếu (ROE_Trailing 1,89%,
  surprise +136,7% phồng cơ học do nền lỗ). Sự cố thật 2026-07-23: DollarBill vẫn đưa IVS vào
  plan LAG 07-24 (cả SpaceX 1800cp lẫn ZaloPay 2750cp) vì file này chưa có exclude list — đã sửa.
- **TMG**: loại cùng lúc 07-21 — `Volume_3M_P50=0`, ngoài mô hình backtest hoàn toàn. ADV-cap sẽ
  tự chặn 100% (ADV=0) nếu ai đó vẫn đưa vào, nhưng đừng đưa vào từ đầu.
Nếu chưa chắc 1 mã LAG mới có nằm trong danh sách loại không (danh sách này có thể còn cập nhật
thêm) → escalate hỏi Mike trước khi đưa vào plan, đừng tự suy đoán từ tier gốc.

## Trứng vàng DNSE — ĐÃ RÚT HẾT VĨNH VIỄN cả 2 account (cập nhật 2026-07-23)
SpaceX + ZaloPay đều `manual_offbook_assets_vnd=0` — **không phải "tạm hết", là đã đóng hẳn
nguồn này**. TUYỆT ĐỐI không giả định/đề xuất "user rút thêm Trứng vàng" để bù cash gap khi lập
plan — đây không phải một ATM có thể yêu cầu nạp lại theo nhu cầu plan. Nếu 1 ngày tổng giá trị
lệnh muốn đặt vượt quá cash thực có (`cash_vnd` trong nav_basis), PHẢI tự SHRINK/loại bớt lệnh
theo đúng cash thực — không viết "user cần rút X triệu hôm nay" như một điều kiện của plan. Sự cố
thật 2026-07-23: DollarBill lập plan SpaceX 07-24 với 6 lệnh tổng 177,2M trong khi cash chỉ
~49,1M, rồi yêu cầu user tự rút thêm ~128-134M "Trứng vàng" — nguồn đã xác nhận không còn tồn
tại. Nếu user báo có nạp tiền mới (không phải Trứng vàng, có thể là chuyển khoản khác) → đó là
fact mới, hỏi rõ nguồn trước khi đưa vào plan như đã xác nhận.
