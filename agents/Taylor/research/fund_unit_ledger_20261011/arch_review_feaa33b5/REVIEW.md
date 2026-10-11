# Arch-review `feat/fund-unit-ledger-20261011` @feaa33b5 — NEEDS_CHANGES (2026-10-11)

Mike chép lại từ báo cáo arch-reviewer (agent a449beef06f10ae7d). Probe + mutant của reviewer nằm
cùng thư mục: `probe/p1.py` (K1), `probe/p2.py` (K2), `probe/p3.py` (N3), `mut/mutants.py`,
`mut/run.py`, `mut/results*.json`, `equiv.py` (3000 ca so với `_twr_factor` master). Sandbox gốc
`/tmp/archrev_fu/` có thể đã mất — sửa đường dẫn trong probe khi chạy lại.

## Đã xác nhận (không cần làm lại)
- Số asof 2026-10-09 khớp master (SpaceX −1,33/1,024/0,519 · ZaloPay −4,907/−1,162/−2,01); 203
  ngày lịch × 3 kỳ × 2 TK 0 lệch; 3000 ca ngẫu nhiên có dòng tiền 0 lệch với `_twr_factor` master.
- KHÔNG bit-for-bit ở mức thô (lệch tối đa 1 ulp 2,2e-16; sau `round(…,3)` 0/4626 khác).
- 2880 assertion PASS dưới `env -u TZ`, New_York, UTC, Kiritimati.
- `nav_period_returns.py --selfcheck` đỏ sẵn trên master; `report_delivery_ledger_selfcheck.py`
  đỏ từ mọi worktree — có sẵn, không do nhánh.
- Lưu ý: từ worktree, `report_delivery_gate.ROOT` trỏ cây canonical ⇒ `report_delivery_gate_selfcheck`
  chạy trong worktree thực ra gọi `nav_period_returns.py` của MASTER. Muốn thử CLI của nhánh với
  cổng phải dựng sandbox (bản sao `bin/` nhánh + bản sao dữ liệu).

## LỖI CHẶN

### K1 — eod mặc định không bắt khai giờ ⇒ giá đơn vị sai vĩnh viễn + lãi ảo ngày rút
Chỗ: `account_cash_flows.py:59` (mặc định eod), `:148-158` (`time_ict` chỉ bắt với bod),
`nav_unit_ledger.py:124` (thiếu `time_ict`/`balance_ts` ⇒ bỏ kiểm im lặng), `:128-129`
(`balance_ts` không parse được ⇒ bỏ kiểm im lặng), `:167-169` (chỉ kiểm với eod).
Tái hiện (thị trường đứng yên, NAV chụp 19:10):
| Bản ghi | asof T | asof T+1 trở đi |
|---|---|---|
| Nạp 200tr lúc 20:00 ngày T, mẫu mặc định (không timing, không time_ict) | −20,0% | −4,0% vĩnh viễn (giá 9.600) |
| Cùng bản ghi theo mặc định cũ (bod ngày T) | −16,667% | 0,0% |
| Rút 200tr lúc 20:00 ngày T, mẫu mặc định | inception +20,0%, WTD +20,0%, pnl +200tr | −4,0% vĩnh viễn |
| Có khai `time_ict: "20:00"` | CashFlowError đúng | — |
Không cổng nào bắt (NAV ngày T không nhảy; `_check_period_returns` so với chính số sai). Ví dụ
docstring `account_cash_flows.py:23-24` + template đang là đúng hình dạng nguy hiểm. `balance_ts`
thật KHÔNG cố định 19:10: 135 dòng trải 04:49 … 23:50; ZaloPay 2026-07-27 có balance_ts =
2026-07-28T09:15. bod hiện bắt `time_ict` nhưng KHÔNG dòng code nào đọc nó: bod 20:00 ngày T được
nhận, ra −16,667% asof T.

### K2 — Sổ lệch làm TẮT cổng tỉ suất báo cáo (fail-open), không có lối ra
Chỗ: `nav_period_returns.py:209-213`, `:239-241` (LedgerDriftError ⇒ rc=1 như mọi lỗi);
`report_delivery_gate.py:190-199` (mọi rc≠0 ⇒ WARN fail-open); `daily_nav_snapshot.py:1456` (chạy
lại là ghi đè dòng ngày đó). Tái hiện: `--seal` 70 dòng → dòng 2026-10-09 đổi +1.234đ → CLI rc=1,
`--seal` rc=2 → báo cáo ghi "+9,99%" KHÔNG bị chặn. Sổ khớp thì cùng báo cáo đó bị BLOCK.
`kb/data_registry/trading-bot/nav_unit_ledger.md` mục "Trạng thái" đọc ra là được chốt ngay.

## LỖI KHÔNG CHẶN
- **N1** `nav_period_returns.py:196` vứt `info` của `build_ledger` ⇒ dòng tiền treo/bị loại vô hình
  ở JSON công bố. Ca: NAV +40tr (4%), bản ghi gõ nhầm 07-13 thay 07-03 ⇒ return +4,0%, không khoá
  nào nhắc pending, cổng 5% im.
- **N2** `nav_unit_ledger.py:270` rồi `:280-282`: `seal()` đọc file 2 lần, không khoá ⇒ 2 tiến
  trình xen nhau sinh dòng trùng, sổ không đọc lại được. Kèm: nav_history 2 dòng trùng ngày ⇒
  `build_ledger` áp dòng tiền 2 lần (10.000 → 8.333).
- **N3** nạp 200tr thứ Bảy, bản ghi mặc định, snapshot thứ Hai +20%: master `ok=True`; nhánh
  `ok=False`, chặn ghi dòng NAV thứ Hai (rc=3), tiêu đề `daily_nav_snapshot.py:887-890` in
  "account_cash_flows.json KHÔNG ĐỌC ĐƯỢC" (sai — file đọc được). Bản ghi hợp lệ lúc CN thành lỗi
  tối thứ Hai trong cron không người trực; `portfolio_status.py:613-620` nuốt bằng `except: pass`.
- **N4** `account_cash_flows.py:193-197` luôn bảo "khai lại bod + time_ict"; làm theo mà giữ ngày
  thứ Bảy thì `unexplained_nav_jumps` (`:211`, `:221`, so theo NGÀY GHI thô) chặn oan bước nhảy thứ
  Hai. Thông điệp không phân biệt "ngày không phiên" với "ngày có phiên nhưng snapshot hỏng" (§29).
- **N5** `nav_unit_ledger_selfcheck.py:165` bỏ cả khối "ra đúng số đã công bố" khi account có bất kỳ
  bản ghi nào sau inception: thêm 1 `market_only` amount=0 ⇒ 2880 → 2201 assertion, vẫn in OK. Số
  công bố viết cứng `:148` đọc từ `data/` sống ⇒ đỏ khi bước 3 đính chính hợp lệ.
- **N6** `nav_unit_ledger.py:46` `WC_ROOT = dirname×3` ⇒ sập ở độ sâu worktree khác
  (`mike/agents/wt-*/bin`). Dùng `wc_paths.find_wc_root(__file__)`.
- **N7** IRR: `nav_period_returns.py:116-117` ghi chú luôn nói "dòng tiền đổi dấu nhiều lần" — sai
  ở ca 0 nghiệm do lỗ >99,9% và ca nghiệm kép (§29). `:132` bod lấy `row.date − 1 ngày lịch` (bod
  thứ Hai tính từ CN) trong khi sổ coi là giá chốt thứ Sáu — chốt một quy ước.
- **N8** `diff_against_sealed:258-262` cột suy ra bị sửa thành nan/inf ⇒ `diffs=[]`.
  `nav_unit_ledger.py:192` env `NAV_UNIT_LEDGER_DIR` nằm trên đường production. Câu "nguồn duy nhất"
  trong `nav_unit_ledger.md` nên là "bản đối chứng" (tỉ suất luôn tính từ chuỗi trong bộ nhớ).
- **N9** số mũ quy năm dùng `365.0/days`; quy ước repo cho backtest là 365,25.
- **N10** reviewer chưa chạy `tz_anchor_gate`/`code_quality_gate` trên nhánh.
- **N11** (ngoài diff, có sẵn) `daily_nav_snapshot.py:1470-1478` "Từ go-live" = `nav /
  --starting-capital − 1`, mặc định 1 tỷ, không caller nào truyền ⇒
  `reports/ZaloPay_daily_report_2026-10-09.md:6` in −6,06% trong khi chuẩn là −4,907%; không có số
  hạng dòng tiền. `portfolio_status.py:611` "Hôm nay %" = tỉ số NAV thô.

## Mutant của reviewer: 136 áp được · 95 chết assertion · 3 chết do sập · 38 sống (30 sống thật)
Chết do sập: P08b (IndexError), A09, A17 (RuntimeError cổng không được bắt).
Sống thật, sửa trước:
- **P14** `nav_period_returns.py:128` `ledger[i0+1:i1]` — bỏ dòng tiền đúng ngày cuối kỳ; không ca
  thử nào có flow trên `to_date`.
- **U20** `nav_unit_ledger.py:130` bỏ `snap.date() == row[0]` — nhánh "snapshot chụp sáng hôm sau".
- **U23** `:103` `== "True"` → `!= "False"` — 86/135 dòng thật có cờ rỗng; assertion selfcheck
  `:163` là hằng đúng.
- **U49** `:298` `require_file=True → False`. **U54/U55** `:333`/`:330` thông báo pending/dropped.
- **U56/U70** `:290`/`:285` bỏ `os.replace` — tính nguyên tử không có test. **U28** `:227` `<=`→`<`.
- **P22** `nav_period_returns.py:137` `mwr_annualized_pct` lấy nhầm hệ số TWR (ca ≥365 ngày không
  có dòng tiền). **P36/P36b** `:153`/`:152`, **P41b** `:142`, **P45** `:148` — trường đầu ra không
  ai assert.
- **A16** `account_cash_flows.py:114` `cfg.get("SpaceX")` — bỏ lọc account (§12) sống qua 6 selfcheck.
Sống thật, mức thấp: U12 `:176` (nav = eod bằng nhau ⇒ ZeroDivisionError thay vì ValueError), U17
`:155`, U18 `:130` (biên cùng phút), U24 `:105`, U29 `:220`, U50 `:148`; P17 `:132`, P38 `:159`,
P40 `:186`, P46 `:105`; A08 `:221` (`abs(chg)`→`chg`: rút lớn không bị cổng 5% bắt), A10b `:71`,
A11 `:140`, A12 `:142`, A13 `:161`.
Tương đương/vô hại (7): U34b, U38, U45, P10b, P18, P25, P27. Không thử được: U69 (bỏ fsync).

## Reviewer KHÔNG kiểm được
65 mutant của tác giả; ~20/27 selfcheck của broad_scan; `portfolio_status_selfcheck` treo trong
sandbox reviewer; Python 3.12; cổng pre-commit; `daily_nav_snapshot.py` sống; hành vi thật DNSE
(tiền chuyển lúc X giờ có vào `balances` trước lần chụp không); `balance_ts` là ICT chỉ suy từ
`vn_market.now_ict()`.
