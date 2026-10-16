# Đặc tả cài đặt — bước 4 phần 2 (làm SAU khi bước 3 merge)

Người cài đặt đọc `README.md` trước (số liệu, công thức, cạm bẫy). Nguyên mẫu `tr_build.py` và
`zalopay_bot_series.py` là hành vi tham chiếu: bản cài phải ra đúng số của chúng trên cùng dữ liệu.
Mọi mục "MẶC ĐỊNH ĐỀ XUẤT" phụ thuộc câu hỏi ở cuối file — chưa có trả lời thì cài theo mặc định và để
cờ cấu hình.

## Phần A — VN-Index có cổ tức

### A1. File mới
| File | Vai trò |
|---|---|
| `mike/bin/vnindex_total_return.py` | thư viện + CLI. Một công thức duy nhất |
| `mike/bin/vnindex_total_return_selfcheck.py` | selfcheck khép kín (không BQ, không mạng) |
| `mike/bin/hose_membership_refresh.py` | chụp bảng sàn, ghi snapshot có ngày |
| `data/benchmark/vnindex_tr_daily.csv` | chuỗi ngày, chỉ-ghi-thêm |
| `data/benchmark/hose_membership_<YYYY-MM-DD>.json` + `hose_membership_latest.json` | bảng sàn theo vintage |
| `mike/kb/data_registry/price-volume/vnindex_total_return.md`, `hose_membership.md` | registry (bản nháp ở `proposed_kb/`) |

Cột `vnindex_tr_daily.csv`: `date, vnindex, vnindex_src2, y_gross, n_members, mc_members_vnd,
div_cash_vnd, tr_gross, tr_net, k2_synth_pr, status(provisional|sealed), membership_vintage,
ca_max_ingested_at, built_at_ict`.

### A2. Hàm (trong `vnindex_total_return.py`)
- `load_membership(path) -> spells[ticker] = [(start, end)]` — theo `tr_build.hose_spells`.
- `dividends(ca_df) -> (ticker, ex_date, div_gross)` — chỉ `event_code='DIV'`, `event_status='executed'`,
  bỏ trùng HOÀN TOÀN trên (mã, ex-date, số tiền, năm, đợt), CỘNG các đợt khác nhau cùng ngày
  (DGC 14/09/2026 có 2 dòng 3.000 + 5.000 là hai đợt thật).
- `div_yield_daily(panel, spells, divs) -> DataFrame[date, y, n, mc, div_cash, k2_synth_pr]` — vốn hoá
  ĐẦY ĐỦ phiên t-1 (`Price_{t-1} × OShares_{t-1}`); loại mã-ngày mà phiên liền trước của mã không phải
  phiên liền trước của chỉ số.
- `chain(prev_tr, idx_ratio, y, k)`; `build_series(...)`; `append_series(path, rows)` (khoá `flock`,
  file tạm + `os.replace`).
- `period_return(series, start_date, end_date, kind in {"price","tr_gross","tr_net"}) -> float` — kỳ
  `(start, end]`, `start` là NGÀY MỐC (giá chốt ngày đó), cùng quy ước với `nav_unit_ledger`.
- CLI: `--update` (dựng các phiên còn thiếu + dựng lại các phiên `provisional`), `--check` (chạy cổng,
  rc≠0 nếu hỏng), `--period A B`, `--selfcheck`.

Thuế: `tr_net` dùng 5% (TT 111/2013 Đ.10; Luật 109/2025 giữ nguyên) — hằng số có tên, không rải số.

### A3. Lịch cập nhật (tra `kb/cron_registry.md` trước khi thêm — §11)
- `corporate_action` nạp ~22:22–22:48 ICT; BQ `ticker` sync 23:45 ICT ⇒ `--update` chạy **sau** cổng
  `bq_freshness_check.sh` của đêm đó (đề xuất 00:30 ICT, T3–T7).
- Chỉ số giá ngày T lấy từ BQ hàng `ticker='VNINDEX'` cột `Price`, đối chiếu DNSE
  (`services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol=VNINDEX`) — cột `vnindex_src2`.
- Dòng mới ghi `provisional`; chuyển `sealed` sau **5 phiên**. Lý do: dòng DIV có thể vào bảng sau ngày
  GDKHQ. Dựng lại một dòng `sealed` mà `y_gross` đổi > 0,1 điểm cơ bản ⇒ rc=2, không ghi (cùng tinh thần
  sổ đơn vị); đường đính chính dùng cơ chế bước 3.
- `hose_membership_refresh.py` chạy tuần một lần; in diff (mã vào/ra HOSE) lên Trading Daily.

### A4. Cổng fail-closed (CẤM rơi im lặng về chỉ số giá)
`--check` và mọi consumer phải từ chối (rc≠0, nêu đúng giá trị đã đọc — §29) khi:
| # | Điều kiện | Ngưỡng |
|---|---|---|
| G1 | chuỗi thiếu phiên cuối của kỳ được hỏi, hoặc thiếu phiên ở giữa | 0 phiên thiếu |
| G2 | `vnindex` vs `vnindex_src2` lệch tại bất kỳ phiên nào trong kỳ | > 0,01% (đo: bình thường 0; ca hỏng 2025-04-09 lệch 3,5%) |
| G3 | feed `corporate_action` không FRESH (`corp_action_lib.feed_freshness`) | STALE/DEAD |
| G4 | `n_members` đổi so với phiên trước | > 5 mã, hoặc `mc_members` đổi > 3% ngoài biến động chỉ số |
| G5 | `k2_synth_pr` luỹ kế 60 phiên lệch chỉ số chính thức | > 0,5 điểm % (đo 2020–2025: ≤ 0,2/năm) |
| G6 | một khoản cổ tức > 30% giá phiên trước | chặn tới khi có người xác nhận |
| G7 | snapshot bảng sàn cũ | > 35 ngày |
| G8 | `OShares` thiếu ở mã chiếm > 0,5% vốn hoá rổ | chặn |

Consumer không lấy được số ⇒ ô hiển thị ghi rõ `chưa có số (lý do)` — KHÔNG in số chỉ số giá vào cột
có cổ tức, KHÔNG bỏ cột.

### A5. Nối vào báo cáo (không đổi cách tính số danh mục)
- `nav_period_returns.py`: thêm khối `benchmark` cho mỗi kỳ: `{anchor_date, vnindex_price_pct,
  vnindex_tr_gross_pct, vnindex_tr_net_pct, status, reason}`. `anchor_date` = ngày của dòng sổ đơn vị
  làm mốc kỳ (dòng 0 = `inception_date`) ⇒ mốc chỉ số KHÔNG còn do người soạn chọn (đóng lỗi 03/07 ↔
  06/07 ở README). Tỉ suất danh mục, `pnl_vnd`, `mwr_pct` giữ nguyên từng byte.
- Bảng 3.2 "Hiệu suất lũy kế" (weekly/monthly, §31 ext): 2 cột chỉ số + 2 cột chênh, số lấy NGUYÊN từ CLI:

  `| Giai đoạn | <TK> | VN-Index (giá) | VN-Index có cổ tức | Chênh so giá | Chênh so có cổ tức |`

  Chú thích dưới bảng (cố định): chỉ số có cổ tức do đội tự tính từ cổ tức tiền mặt của cổ phiếu HOSE,
  tái đầu tư tại ngày GDKHQ, trước thuế; HOSE không công bố bản có cổ tức của VN-Index.
- `report_delivery_gate.py`: (i) ô chỉ số trong bảng 3.2 phải bằng đầu ra CLI (dung sai làm tròn 0,005
  điểm %); (ii) cột có cổ tức mang `chưa có số` ⇒ MẶC ĐỊNH ĐỀ XUẤT: weekly/monthly CHẶN gửi, daily không
  có cột này. Giữ nguyên tắc cổng đã có: CLI rc≠0 = chặn.
- Biểu đồ "lợi nhuận lũy kế so với VN-Index": thêm đường thứ ba (có cổ tức); không thay đường giá.

### A6. Test (selfcheck khép kín, chạy dưới `env -u TZ` và một TZ lạ — §16/§19)
1. Rổ 3 mã tự chế, 1 khoản cổ tức: `y` và `TR` tính tay.
2. Hai đợt cổ tức cùng ngày ⇒ cộng; hai dòng trùng hoàn toàn ⇒ một.
3. Mã rời HOSE giữa kỳ / mã mới lên sàn ⇒ ra vào rổ đúng phiên.
4. Mã ngừng giao dịch 3 phiên rồi nối lại ⇒ phiên nối lại không vào `y`.
5. Mỗi cổng G1–G8: một ca nổ + một ca sát ngưỡng không nổ; kiểm thông điệp trích đúng giá trị.
6. Dòng `sealed` bị dựng lại khác đi ⇒ rc=2, file không đổi (so md5).
7. `period_return` với mốc trùng ngày nghỉ ⇒ từ chối (không tự lùi).
8. Mutation: đổi vốn hoá t-1 → t; bỏ lọc `executed`; đổi `k` ⇒ mỗi mutant phải làm ≥ 1 ca đỏ.
9. Hồi quy trên dữ liệu thật (không thuộc selfcheck khép kín; lệnh ghi trong registry): năm 2023
   `y`=1,68; 2025 `y`=1,62; kỳ 2026-07-01→10-13 chênh gộp 0,64 (dung sai 0,02 — số CP có thể được vendor
   sửa lùi).

## Phần B — Chuỗi ZaloPay "phần bot quản lý"

### B1. File mới
| File | Vai trò |
|---|---|
| `mike/bin/nav_sleeve.py` | dựng chuỗi (b) + đối soát; CLI |
| `mike/bin/nav_sleeve_selfcheck.py` | selfcheck khép kín |
| `data/execution_logs/nav_sleeve_history_<account>.csv` | 1 dòng/ngày nav_history: phần ngoài bot |
| `data/sleeve_transfers.json` | dòng tiền giữa phần ngoài bot ↔ bot (người xác nhận, có bằng chứng) |
| `data/sleeve_scope.json` | phạm vi "ngoài bot" theo khoảng ngày |
| registry `trading-bot/nav_sleeve_history.md`, `sleeve_transfers.md`, `sleeve_scope.md` | |

`sleeve_scope.json` — KHÔNG đọc `excluded_tickers` (đó là danh sách cấm giao dịch: có PNJ vị thế 0, và
nó có thể đổi mà không ai nghĩ tới chuỗi hiệu suất):
```json
{"ZaloPay": [{"ticker": "DGC", "from": "2026-07-06", "to": null,
              "note": "legacy, HOSE hạn chế giao dịch; user duyệt <ngày>"}]}
```
Cột `nav_sleeve_history`: `date, nav_a, outside_mv, outside_recv, nav_b, outside_qty_json,
price_source, balance_ts, positions_ts, recon_diff, nav_is_estimate`.

### B2. Hàm
- `positions_at(account_no, date, balance_ts) -> {ticker: qty}` — lọc `account_no` ở DÒNG ĐẦU (§12);
  **cộng mọi lô cùng mã** (cạm bẫy thật: MBB/BID/VCB hai lô, thiếu 24,4tr); chỉ nhận bản ghi trong ±10
  phút quanh `balance_ts` (cùng luật N3 của `cash_identity`), ngoài ra ⇒ dòng mang cờ `positions_stale`.
- `outside_value(date, qty, scope) -> (mv, recv)`:
  - giá = đúng giá `daily_nav_snapshot` đã dùng cho dòng đó. Việc cần làm ở phần 2: cho
    `daily_nav_snapshot.py` GHI giá trị + KL của từng mã trong `sleeve_scope` vào `nav_snapshot_*.json`
    (thêm trường, không đổi `nav`) để `nav_sleeve` không định giá lại. Backfill lịch sử dùng BQ `Price`
    (nguyên mẫu: 54/68 ngày khớp từng đồng; ngày lệch đều do mã trong bot).
  - `recv` = cổ tức GỘP phải thu của mã ngoài bot đang nằm trong `cash` của dòng nav_history: từ ngày
    GDKHQ tới trước ngày tiền về. Ngày trước GDKHQ mà `cum_dividend_excl` đã loại khoản đó khỏi NAV ⇒
    `recv` = 0 (ca thật 11/09).
- `detect_transfers(account) -> list[proposal]` — ĐỀ XUẤT, không tự ghi:
  - cổ tức: dòng DIV của `corporate_action` cho mã ngoài bot × KL giữ ngày đăng ký; tiền về = phiên mà
    `cashDividendReceiving` giảm ≥ số gộp. Số ròng = gộp × 0,95.
  - bán/mua: KL mã ngoài bot đổi giữa hai dòng ⇒ đọc bản ghi `orders` cùng ngày trong `dnse_raw` (lọc
    account, cộng `fillQuantity × averagePrice`), trừ phí 0,097% + thuế bán 0,1% (`dnse_fee_rates.py`).
  - KL đổi mà không có lệnh khớp tương ứng (thưởng CP, quyền mua, chuyển khoản CK) ⇒ đề xuất mang nhãn
    `needs_human`, không mang số tiền.
- `build_sleeve_rows(...)`; `build_sleeve_ledger(account)` = `nav_unit_ledger.build_ledger(rows_b,
  flows_b, inception_date, starting_capital − outside_mv(inception))` — KHÔNG viết lại công thức.
- `reconcile(table) -> dict` — ba phép đối soát của README.

Vì sao KHÔNG tự động đoán được dòng tiền khi DGC bán: `dnse_raw` cho biết ĐÃ bán bao nhiêu, giá nào,
nhưng không cho biết (i) tiền bán ở lại cho bot hay user rút đi (rút = dòng tiền NGOÀI của cả tài
khoản, phải khai ở `account_cash_flows.json`), (ii) giờ tiền thực sự dùng được, (iii) phí/thuế thật
(API không trả). Nên code đối soát được SỐ LƯỢNG và GIÁ từ `dnse_raw`, nhưng bản ghi chỉ có hiệu lực
khi có người xác nhận trong `sleeve_transfers.json` (schema = `account_cash_flows.json` + `ticker`,
`gross_vnd`, `fee_tax_vnd`, `source` ∈ dividend|sale|purchase).

### B3. Cổng fail-closed
| # | Điều kiện | Hành vi |
|---|---|---|
| S1 | có đề xuất của `detect_transfers` chưa được xác nhận / bác | chuỗi (b) từ ngày đó = `chưa có số`, nêu đề xuất; chuỗi (a) không bị ảnh hưởng |
| S2 | KL mã ngoài bot đổi mà không có đề xuất nào giải thích | như S1 |
| S3 | mã trong `sleeve_scope` không có giá ngày đó | từ chối dòng |
| S4 | `NAV_a − NAV_b − ngoài` ≠ 0 (đ) | rc≠0 |
| S5 | `recon_diff` vượt 0,05% NAV ở dòng KHÔNG mang `nav_is_estimate` và không có sự kiện quyền đã biết | cảnh báo Trading Daily (không chặn — nguyên nhân nằm trong bot, đã có `cash_identity`) |
| S6 | `sleeve_scope` đổi (thêm/bớt mã, đổi ngày) so với lần dựng trước | từ chối tới khi dựng lại cả chuỗi + ghi chú đính chính (bước 3) |
| S7 | `NAV_b` ≤ 0 hoặc mốc chuỗi (b) < 5% NAV_a | từ chối (tỉ suất trên mẫu số gần 0 — ca "legacy nghiêm ngặt") |

### B4. Nối vào báo cáo
- `nav_period_returns.py --account ZaloPay --sleeve bot` ⇒ cùng cấu trúc đầu ra, thêm `series: "bot"`,
  `outside_scope`. Mặc định (không cờ) vẫn là chuỗi (a), không đổi byte nào.
- Báo cáo ZaloPay bảng 3.2 — MẶC ĐỊNH ĐỀ XUẤT: số chính = (a); thêm một dòng
  `Phần bot quản lý (không gồm DGC)` cho ba kỳ, kèm chênh so với chỉ số; chú thích nêu DGC bao nhiêu % NAV.
- So sánh SpaceX ↔ ZaloPay (báo cáo tháng): dùng (b) và SpaceX **cùng cửa sổ từ 06/07**.
- `report_delivery_gate.py`: ô của dòng (b) phải bằng đầu ra CLI; (b) `chưa có số` ⇒ in đúng chữ đó,
  không chặn gửi báo cáo (số chính thức là (a)).

### B5. Test
1. Ca không có mã ngoài bot ⇒ (b) ≡ (a) từng dòng.
2. Ca DGC đứng yên ⇒ ra đúng nguyên mẫu: −0,790% (06/07 → 13/10), mốc 525.365.567, dòng vào 76.000.000.
3. Cổ tức: trước GDKHQ / giữa GDKHQ và ngày về / ngày về — `recv` và dòng tiền đúng từng dòng; lãi/lỗ
   ngoài bot ngày về = −thuế.
4. Bán một phần DGC: có lệnh khớp ⇒ đề xuất đúng số; chưa xác nhận ⇒ S1; xác nhận ⇒ giá đơn vị (b)
   không nhảy.
5. KL đổi không có lệnh ⇒ `needs_human`.
6. Hai lô cùng mã ⇒ cộng. Bản ghi vị thế lệch > 10 phút ⇒ cờ.
7. Chạy cho CẢ HAI tài khoản cùng ngày, kết quả phải khác nhau (§12).
8. `MIKE_BOT_TEST_MODE=1` không cần (không import `Executor`); không gọi broker; không ghi `data/`
   (nợ hạ tầng của `nav_scripts_2account_selfcheck.py` — đừng lặp lại).
9. Mutation: bỏ `recv`; dùng số gộp thay ròng; đọc `excluded_tickers` thay `sleeve_scope`; ghi đè lô.

## Thứ tự làm đề xuất
1. A1–A4 + selfcheck (không chạm báo cáo). 2. B1–B3 + selfcheck. 3. `nav_period_returns.py` (khối
`benchmark`, cờ `--sleeve`). 4. Bảng 3.2 + cổng giao báo cáo. 5. Registry + cron. Mỗi bước qua
arch-review; đụng `nav_period_returns.py` / `report_delivery_gate.py` ⇒ quét selfcheck rộng (§23).

## Câu hỏi cần user quyết

| # | Câu hỏi | Mặc định đề xuất | Hệ quả đo được |
|---|---|---|---|
| Q1 | Đính chính mốc VN-Index ZaloPay 03/07 → 06/07 (3 báo cáo đã gửi, lệch 0,94–0,96 điểm % ở cột chỉ số)? Ngưỡng điểm 4 viết cho NAV/tỉ suất danh mục, chưa nói về cột mốc so sánh | sửa từ báo cáo kế tiếp + một dòng ghi chú; không phát hành lại | chênh "từ khi bắt đầu" tới 09/10: +1,91pp → +0,97pp |
| Q2 | Cột có cổ tức dùng số GỘP hay SAU THUẾ 5%? | gộp (quy ước chỉ số, bất lợi hơn cho danh mục) | lệch nhau 0,03 điểm % cho kỳ 07 → 10; ~0,1/năm |
| Q3 | Chấp nhận chỉ số có cổ tức TỰ DỰNG (HOSE không công bố cho VN-Index), hay đổi/ thêm mốc VN30-TRI / VNAllshare-TRI chính thức (cần nguồn dữ liệu trả phí + rà giấy phép)? | tự dựng, ghi chú rõ trong báo cáo | sai số ước ±0,1–0,2 điểm %/năm |
| Q4 | "Legacy" trong chính sách điểm 2 = chỉ DGC, hay cả 6 mã cũ đã giao cho bot 06/07? | chỉ DGC | biến thể loại cả 6 mã không dùng được (mốc 4,9tr) |
| Q5 | TV1/DRI (discretionary, bot đặt lệnh, có ở cả SpaceX) nằm trong chuỗi (b)? | có | loại ra: −1,38% thay vì −0,79% (ước lượng) |
| Q6 | Cổ tức DGC: vào chuỗi (b) số RÒNG tại ngày tiền về (thuế tính cho phần ngoài bot)? Giờ tiền về 25/09 không đo được | ròng, ngày tiền về, coi là trước giờ đóng cửa | sau đóng cửa: −0,707% thay vì −0,790% |
| Q7 | Khi DGC bán: tiền bán ròng = dòng vào (b) tại NGÀY KHỚP (tiền đã nằm trong `totalCash` từ ngày đó), trừ khi user rút đi? Ai xác nhận bản ghi? | ngày khớp; Mike trình, user xác nhận | — |
| Q8 | Báo cáo ZaloPay hiển thị cả (a) và (b), hay (b) chỉ ở phần so sánh với SpaceX? | (a) là số chính + một dòng (b) | — |
| Q9 | Cột có cổ tức thiếu số: chặn gửi weekly/monthly hay gửi với ô `chưa có số`? | chặn weekly/monthly | — |
| Q10 | Báo bq_admin sửa hàng `VNINDEX` 2025-04-09 (1.132,79, đúng 1.094,30)? Registry đang ghi hàng gốc "sạch" | báo + sửa registry | không ảnh hưởng số 2026 |

## Chưa kiểm được
- Chuỗi TRI chính thức nào của HOSE (không lấy được số) ⇒ chưa có phép so trực tiếp với nguồn công bố.
- Điều khoản dùng dữ liệu HOSE-Index TRI cho báo cáo nội bộ.
- Độ trễ thật giữa ngày GDKHQ và lúc dòng DIV xuất hiện trong `corporate_action` (cần
  `corporate_action_snapshots`, mới có vintage từ 2026-08-17) ⇒ số "5 phiên" ở A3 là đề xuất, chưa đo.
- 1.245 mã-ngày (2020+) phương pháp B thấy chênh mà A không có dòng DIV — chưa điều tra từng ca.
- Giờ tiền cổ tức DGC về ngày 25/09; phí/thuế thật khi bán DGC (chưa có ca).
- Nguyên nhân phần bot ZaloPay kém SpaceX 0,7 điểm % trong tháng 7.
