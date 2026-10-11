# Arch-review LẦN 2 `feat/fund-unit-ledger-20261011` @75060709 — NEEDS_CHANGES (1 lỗi chặn) (2026-10-11)

Mike chép lại từ báo cáo arch-reviewer (agent a52c9ff32388c4f5b). Cùng thư mục: `probe/{k1,fuzz,b1,
edge,n11,n11b,n3,gate,fuzz_fix,edge_fix,fixk1}.py`, `mut/{mutants,mutants2,mutants3,run}.py` +
`results*.json`, `fix/b1_prototype.patch` (76 dòng diff, gồm B1 + L1). Đường dẫn sandbox gốc
`/tmp/ar2/` có thể đã mất — sửa đường dẫn khi chạy lại.

## Đã đóng (reviewer tự chạy lại — không cần làm lại)
K1 (kịch bản gốc), K2, N1–N10 ĐÓNG. N11 ĐÓNG MỘT PHẦN (số + định dạng đúng; còn L2, L3, L5).
Nghiệm thu khớp: SpaceX −1,33/1,024/0,519, ZaloPay −4,907/−1,162/−2,01; 226 (tài khoản, ngày) ×
khoá cũ = 3.519 giá trị 0 lệch với master. Selfcheck xanh ở 4 múi giờ. Ca biên D1 (đúng 14:45, đúng
phút chụp, nghỉ lễ giữa tuần, hai dòng tiền quanh một lần chụp, treo, ZaloPay 07-27, trước inception,
chuỗi 6 dòng tiền, rút hết) đều đúng luật. Chốt "dòng nguồn chụp trước đóng cửa ⇒ từ chối" của tác
giả: CHẤP NHẬN. `report_delivery_gate.py` sửa đúng hướng fail-closed; hạ `tz_anchor_baseline` là hạ
nợ thật; lý do `SKIP=tz-anchor-gate` là thật (bug có sẵn của `tz_anchor_gate.baseline_key` dưới
GIT_DIR của worktree `WorkingClaude/wt-*` — sửa RIÊNG, ngoài nhánh).

## LỖI CHẶN

### B1 — thiếu dòng nav_history của một phiên ⇒ giá đơn vị sai, không lỗi, không cảnh báo
Chỗ: `bin/account_cash_flows.py:298-321` (`assign_flow`). Dòng cho giá là `rows[i-1]` (bod) hoặc
`rows[i]` (eod) nhưng không kiểm đó có phải phiên đóng cửa GẦN NHẤT trước thời điểm tiền vào.
Tái hiện (`probe/b1.py`): phiên T +10%, nạp 220tr 16:00 ngày T, T+1 đứng yên.
| nav_history | Giá đơn vị | Tỉ suất |
|---|---|---|
| đủ dòng T | 10.000 → 11.000 → 11.000 | +10,0% (đúng) |
| thiếu dòng T | 10.000 → 10.819,7 | +8,197%, `pending=[]`, cổng 5% trả `[]` |
Không phải ca giả định: (1) dữ liệu thật THIẾU dòng 2026-08-06 ở cả hai tài khoản
(`dnse_raw_2026-08-06.jsonl` có balances tới 19:10 nhưng chưa từng backfill); (2) 4/28 báo cáo ngày
SpaceX đã gửi (08-26, 08-28, 09-22, 10-02) in "so với hôm trước" so với 2 phiên trước vì dòng phiên
liền trước lúc đó chưa có; (3) cổng 15% tự tạo ca này: nạp >15% NAV sau đóng cửa chưa kịp khai trước
19:10 ⇒ tối T `nav_jump_verdict` ok=False (rc=3, không ghi dòng T); tối T+1 đã khai ⇒ ok=True, dòng
T+1 được ghi, dòng T thiếu luôn.
Mô phỏng: 764/3.000 ca sai im lặng (lệch tới 10,6%) ở cấu hình thiếu dòng phiên; các cấu hình khác 0.

required_change:
1. Trong `assign_flow`, sau khi có `(i, timing)`: tính `L` = phiên gần nhất có giờ đóng cửa ≤ thời
   điểm tiền vào (T2–T6 và không `trading_bot.vn_market.is_holiday`, import lười). Ngày dòng cho giá
   = `rows[i][0]` nếu eod, `rows[i-1][0]` nếu bod và i>0, `baseline_date` nếu i==0. Ngày đó < `L` ⇒
   `CashFlowError` nêu tên phiên thiếu + lệnh `daily_nav_snapshot.py --date L --from-raw`.
2. Thêm `baseline_date=None` cho `assign_flow` và `attach_flows_to_rows`; `build_ledger`
   (`nav_unit_ledger.py:141`) truyền `inception_from`.
3. Selfcheck mới, MỖI cái kèm mutant: thiếu dòng phiên + tiền sau đóng cửa phiên đó ⇒ từ chối; tiền
   trong chính phiên thiếu dòng ⇒ vẫn bod ở giá phiên trước; ngày nghỉ lễ thật không bị bắt oan; ca
   i==0.
Bản vá thử `fix/b1_prototype.patch` — reviewer đã chạy: 6.000 ca hỗn hợp 0 sai im lặng; 4604 + 179
+ PASS + 9 assertion hiện có vẫn xanh không sửa test nào; 226 (tài khoản, ngày) lịch sử 0 thay đổi;
dữ liệu thật: nạp 16:00 ngày 08-06 bị từ chối đúng tên phiên, nạp 10:00 vẫn qua.

## LỖI KHÔNG CHẶN
| # | Chỗ | Vấn đề | Sửa |
|---|---|---|---|
| L1 | `account_cash_flows.py:61` | "`balance_ts` tăng theo ngày" chỉ là giả định trong docstring. Dòng T2 sửa tay bằng số dư chụp sáng T4, nạp 20:00 T3 ⇒ eod trên T2, giá 7.800 thay 11.000, im lặng. | ~8 dòng trong `attach_flows_to_rows` (đã có trong bản vá thử). |
| L2 | `daily_nav_snapshot.py:870`, `account_cash_flows.py:193-208` | `except (ValueError, KeyError, OSError)` hẹp: `"date": null`/số, file JSON là list, `inception_date: null`, `starting_capital` là list ⇒ traceback SAU khi đã ghi nav_history: rc=1, không in dòng 💰, không ghi `nav_snapshot_*.json`; `nav_snapshot_daily.sh` báo "NAV KHÔNG ghi được" dù đã ghi. Trước N11 file này chỉ đọc khi nhảy >15%, nay mỗi tối. | `except Exception` ở `:870` (đường hiển thị); bắt thêm `TypeError` ở `:207` + kiểm `isinstance(cfg, dict)`. |
| L3 | `daily_nav_snapshot.py:59` | import `nav_period_returns` ở mức module; `exdate_frame.py:190` (mẫu số sizing), `dividend_adjusted_return.py:1249` (§21), `discretionary_margin_gate.py:249` đều `import daily_nav_snapshot` ⇒ lỗi import code hiển thị kéo theo cả ba. | chuyển import vào trong `unit_price_performance`, trong khối try. |
| L4 | `nav_flow_term_selfcheck.py:166-186` | Hồi quy độ phủ so với master: khối "10 bản ghi hỏng" chỉ kiểm kiểu exception và các bản ghi thiếu `time_ict` nên đều rơi vào lỗi "thiếu giờ". 3 mutant chết trên master nay sống: bỏ kiểm evidence rỗng (`:216`), kind lạ (`:210`), date sai nhận mặc định (`:208`). | thêm `"time_ict": "10:00"` vào bản ghi không thử về giờ + kiểm chuỗi trong thông điệp. |
| L5 | bảng mutant dưới | Lỗ test trên code mới vòng 2. | mỗi cái 1–5 dòng test. |
| L6 | `account_cash_flows.py:292-297`, `:314-320`, `account_cash_flows.md` | Thông điệp bảo "chạy lại snapshot ngày đó"; với 08-24 không làm được (`dnse_raw_2026-08-24.jsonl` chỉ có 1 bản ghi balances mỗi TK lúc 04:49/04:50). | sửa câu chữ: chỉ được khi dnse_raw ngày đó có balances sau đóng cửa; lối ra thật thuộc bước 3. |
| L7 | `account_cash_flows.py:212-215`, `report_delivery_gate.py:~201` | `amount_vnd: NaN` được nhận: dòng NAV "+nan%", CLI `return_pct: NaN`, cổng in "PASS: +9.99% vs canonical +nan%". Có sẵn trên master. | `math.isfinite` mỗi chỗ. |
| L8 | `account_cash_flows.py:313` | Dòng NAV của ngày KHÔNG phiên chụp trước 14:45 bị coi "chụp trước đóng cửa" ⇒ từ chối oan. | 1 dòng sau khi có lịch phiên của B1. |
| L9 | `daily_nav_snapshot.py:~968` | Bản ghi cùng ngày nhưng giờ khai sau lần chụp, NAV +20%: chặn đúng nhưng thông điệp nói "KHÔNG có bản ghi nào gán vào 07-06 (gần nhất: 2026-07-06)" — không nói bản ghi bị đẩy sang phiên sau vì giờ khai (§29). | 2–3 dòng. |
| L10 | `nav_unit_ledger.py:140` | ZaloPay: mốc khởi điểm là NAV đêm trước phiên 07-06 nên tiền vào tối 07-06 không nằm trong vốn khởi điểm mà vẫn bị loại (hiện ở `dropped_flows`). | ghi chú tài liệu. |
Giới hạn cố hữu (không phải lỗi code, lớp bắt là bước 2): giờ khai sau lần chụp trong khi số dư đã
chứa tiền (19:10:01 vs chụp 19:10:00) ⇒ +20% ngày T rồi +2,857% về sau; khoản <5% NAV lọt cổng.

## Mutant của reviewer: 201 áp được · 173 chết assertion · 4 chết do sập · 24 sống
Chết do sập: P18 `nav_period_returns.py:162` (KeyError), P42 `:211`, A66 `account_cash_flows.py:202`,
U62 `nav_unit_ledger.py:92`.
Sống thật trên code mới (10):
- **D03** `daily_nav_snapshot.py:869` `flows` → `flows or []`: đường production không còn đọc sổ dòng
  tiền mà không test nào đỏ (mọi test truyền `flows` tường minh).
- **S01, S02** `portfolio_status.py:618`, `:617`: "Hôm nay" lấy nhầm WTD, inception lấy nhầm MTD —
  fixture chỉ có một phiên nên mọi kỳ bằng nhau.
- **U22** `nav_unit_ledger.py:305` `LOCK_EX` → `LOCK_SH`.
- **A63** `account_cash_flows.py:313` bỏ chốt dòng nguồn khi R là dòng thứ hai.
- **D02b** `daily_nav_snapshot.py:870` bỏ `OSError` (thiếu file inception).
- **D17, D18, D21, D29** `daily_nav_snapshot.py:1583-1588`: bốn trường JSON không ai assert.
Sống do hồi quy độ phủ (3): A58, A61, A69 — xem L4.
Sống trên code có sẵn, mức thấp (5): A36 `account_cash_flows.py:355` (biên `start`), A67 `:200`,
A68 `:195`, U60 `nav_unit_ledger.py:105`, P54 `nav_period_returns.py:206`.
Tương đương (6): P17b, A62, A64, U59, P53, D31.

## Ý kiến 3 điểm tác giả khai
(a) cổng tỉ suất fail-open khi CLI rc≠0: KHÔNG chặn (có sẵn; đổi fail-closed ở bước 2). (b) cổng
chưa đọc `pending_flows`: không chặn và KHÔNG nên chặn cứng (dòng treo hợp lệ cho số đúng); nên cảnh
báo + từ chối bản ghi có ngày TƯƠNG LAI lúc load. (c) chưa chạy end-to-end thật: không chặn; lần
cron thật đầu tiên sau merge (19:10 ICT thứ Hai 12/10) cần người nhìn hai dòng 💰.

## Reviewer KHÔNG kiểm được
Hành vi thật DNSE; Python 3.12; hook pre-commit chạy thật; bộ mutant của tác giả; ~18/27 selfcheck
broad_scan; `report_delivery_gate_selfcheck` (ROOT canonical); parser `report_return_gate.py` chỉ
kiểm bằng đọc regex. `portfolio_status_selfcheck` không khép kín (gọi `value_radar.update_cache` ⇒
BigQuery + ghi `data/value_radar_series.csv`) — có sẵn, ngoài nhánh.
