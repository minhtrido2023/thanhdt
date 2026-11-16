# ORB futures sleeve VN30F — đường thực thi LIVE SpaceX (spec, 16/11/2026)

Job `Taylor_20261116_162132`. Trạng thái: **CODE trên nhánh, CHƯA merge, CHƯA cài cron, cờ TẮT, 0 lệnh thật.**
Nhánh `feat/orb-futures-live-20261116` ở CẢ HAI repo:
- repo ngoài (`/home/trido/thanhdt`, worktree `WorkingClaude/wt-orb-futures-20261116`): `trading_bot/orb_futures.py`, `orb_futures_selfcheck.py`
- repo mike (worktree `agents/Taylor/wt-orb-futures-20261116`): `bin/orb_futures_run.sh`, khối ORB trong `bin/send_plan_report.sh`,
  `bin/send_plan_report_orb_wire_selfcheck.py`, nghiên cứu stop `agents/Taylor/research/orb_futures_stop_20261116/`, file này.

## 1. Quyết định user (16/11 23:20 ICT, decided_by: user — không hỏi lại)
1 HĐ VN30F · sleeve 100tr (nới trần 5% NAV) · stop thảm hoạ CHỌN THEO THỐNG KÊ · alpha giữ nguyên `orb_pt.py` ·
plan = duyệt trước LUẬT, hướng đi báo khi vào/thoát (Trading Daily + journal) · thiếu ký quỹ ⇒ báo nộp như quy trình Trứng vàng.

## 2. Stop thảm hoạ = ±2,5% từ giá khớp vào
Chọn bằng tiêu chí khai TRƯỚC khi nhìn PnL: **mức nhỏ nhất có tỉ lệ phiên chạm ≤3%** (cầu chì hiếm). **N trial = 6**
(1,0/1,5/2,0/2,5/3,0/4,0%). Tape: 1.163 phiên 2022-02-17→2026-11-16 (FiinX 384 phiên chỉ có min/max; vnstock/VCI 779 phiên
bar 1m). Config mô phỏng = `orb_pt.py` (sign OR 09:00–09:30, vào close 09:30, thoát 14:30, slip 1 tick + 0,6bps).
measured_by: `agents/Taylor/research/orb_futures_stop_20261116/stop_study.py` → `stop_study_result.json`.

MAE trong phiên (từ giá vào): p50 0,40% · p90 1,43% · p95 2,01% · p97 2,38% · p99 3,32% · max 10,71% (2022-11-16, short 865 → đỉnh 957,6).

| stop | chạm (toàn tape) | 2022-23 | 2023-26 | gap qua stop (bar 1m) | mean bps | Sharpe | cum | MaxDD | lỗ 1 phiên tệ nhất |
|---|---|---|---|---|---|---|---|---|---|
| không | – | – | – | – | 6,10 | 0,88 | +89,4% | −31,7% | −946bps |
| 1,0% | 19,95% (232) | 26,0% | 16,9% | 4 lần, max 6,6bps | 7,95 | 1,35 | +139,7% | −20,1% | −109bps |
| 1,5% | 9,20% (107) | 13,8% | 6,9% | 2 lần, max 5,8bps | 8,12 | 1,32 | +143,2% | −21,4% | −158bps |
| 2,0% | 5,07% (59) | 8,6% | 3,3% | 0 | 7,59 | 1,19 | +127,8% | −27,8% | −203bps |
| **2,5%** | **2,58% (30)** | 3,9% | 1,9% | **0** | 7,31 | 1,13 | +120,0% | −24,0% | **−253bps** |
| 3,0% | 1,46% (17) | 2,3% | 1,0% | 0 | 7,11 | 1,08 | +114,5% | −25,2% | −303bps |
| 4,0% | 0,69% (8) | 1,3% | 0,4% | 0 | 6,48 | 0,96 | +98,8% | −26,5% | −403bps |

- PnL chỉ để minh bạch, **không dùng để chọn**: 1,0/1,5% có Sharpe cao hơn nhưng chạm 20%/9% số phiên = cắt vì nhiễu, bị loại theo tiêu chí.
  Mọi dòng có stop đều "đẹp hơn" không stop — ĐỪNG đọc đó là edge mới: 6 trial trên cùng tape, không OOS riêng.
- Gap qua stop đo trên 779 phiên bar 1m: ở ≥2% chưa lần nào mở bar vượt mức stop. **Trượt TRONG bar không đo được** (không có tick);
  thực thi = LO đối ứng ở giá sàn/trần ⇒ khớp ở giá tốt nhất hiện có, cộng độ trễ poll 5s. Trường hợp xấu nhất: thị trường khoá
  trần/sàn (biên ±7% quanh tham chiếu) ⇒ stop KHÔNG khớp được, lỗ bị chặn bởi biên độ chứ không bởi stop.
- Quy ra tiền (ước lượng, notional 1 HĐ = 1.843 × 100.000 = 184,3tr ngày 16/11): stop chạm ≈ −4,6tr/phiên; phiên tệ nhất lịch sử không
  stop −9,46% ≈ −17,4tr.

**Stop đặt ở đâu — bot giám sát (chọn) vs lệnh STOP phía sàn:**
- **Đang dùng: bot giám sát** `latest_trade` (board G1) mỗi 5s, chạm ⇒ LO ngược chiều ở sàn/trần. Rủi ro: bot chết ⇒ không có stop
  tới khi cron watchdog (đề xuất mỗi 10') khởi động lại (resume từ state, không vào lại).
- **Lệnh STOP phía DNSE**: docs DNSE (developers.dnse.com.vn guide trading_order) ghi có `orderCategory=STOP` cho CẢ phái sinh (fields
  `stopPrice`, `conditionOperator` >=/<=, `durationType` chỉ GTD, lệnh kích hoạt LO/MTL), không sửa được, chỉ huỷ khi New; và
  `OCO` chỉ cho phái sinh. **CHƯA xác minh bằng lệnh thật**, `dnse_api.place_order` hiện chưa có các field này. Nếu dùng song song
  với bot phải chống đóng kép (2 lệnh đóng cùng khớp ⇒ mở vị thế ngược). Đề xuất: sau khi verify, thay bot-stop bằng STOP sàn hoặc
  dùng STOP sàn làm lớp dự phòng khi bot chết — quyết định của user/Mike, chưa làm.

## 3. Probe DNSE chỉ-đọc (16/11, TK 0002023347) — measured_by `agents/Taylor/research/orb_futures_stop_20261116/probe_dnse_derivative_{1,2,3}.py` (+ `probe_dnse_derivative_1_out.json`, đã bỏ khối accounts có PII)
| Mục | Kết quả |
|---|---|
| TK phái sinh | `accounts`: 0002023347 `derivative.status=ACTIVE` |
| Số dư phái sinh | `balances.derivative`: remainSecure/usedSecure/pendingSecure/holdTaxAndFee/totalLoanDebt/pendingDepositWithdraw đều **0** |
| Positions / sổ lệnh / lịch sử 10–11 | rỗng (`marketType=DERIVATIVE`; `orderCategory=CONDITIONAL` cũng rỗng) |
| Mã HĐ | **mã KRX**, không phải `VN30F2611`: `instruments(market_id="DVX")` ⇒ `41I1GB000` symbolType `VN30F1M` (HĐ T11, đáo hạn 19/11 = thứ Năm thứ 3), `41I1GC000` = VN30F2M (T12), `41I1H3000` = 1Q, `41I1H6000` = 2Q. `secdef("VN30F2611")` trả `[]` |
| secdef 41I1GB000 | tham chiếu 1843, trần 1972, sàn 1714 (±7%), OI 33.063, `finalTradeDate` = null (API không trả) |
| Gói vay phái sinh | **1 gói id 1306**: initialRate **18,48%**, maintenanceRate 17,71%, liquidRate 17,35% (thay cho 17% ước cũ) |
| Phí DNSE | `tradingFee` "Phí linh hoạt" PROGRESSIVE: **1.000đ/HĐ** (1–99 HĐ) cho `progressTradingFee` và `progressDailyCloseTradingFee` |
| ppse phái sinh | `qmaxBuy=qmaxSell=0` (vì ký quỹ 0) — endpoint chạy với `marketType=DERIVATIVE, loanPackageId=1306` |
| Ngày giao dịch | `working_dates()` dùng được (không có 24/11/2026 trong danh sách — chưa rõ lý do) |
| Chuyển tiền cơ sở→phái sinh | **KHÔNG có API** (docs DNSE: chỉ balances đọc). User làm TAY trên app |

**CHƯA XÁC MINH** (không probe được khi chưa có tiền/vị thế/lệnh — không đoán):
1. Ngữ nghĩa từng field `balances.derivative` (đâu là "tổng tiền ký quỹ"); code tạm ước = remainSecure+usedSecure+pendingSecure và gắn nhãn.
2. Schema dòng `positions` phái sinh (tên field số lượng/chiều) — code fail-safe: không parse được ⇒ PAUSED.
3. Field `order_detail` phái sinh (fillQuantity/averagePrice/orderStatus giả định giống cơ sở).
4. Loại lệnh phái sinh hợp lệ: docs chỉ có bảng HOSE/HNX/UPCOM; code chỉ dùng **LO** (docs "đóng vị thế" = LO ngược chiều ở sàn/trần).
   MTL/MAK/MOK/ATC cho phái sinh: chưa xác minh. LO có được nhận trong phiên ATC 14:30–14:45 không: chưa xác minh.
5. Phí sở/VSD (quản lý vị thế, ký quỹ), thuế TNCN phái sinh, ý nghĩa `progressDailyCloseTradingFee`.
6. Lệnh STOP/OCO phía sàn (mục 2).
7. Hành vi `VN30F1M` liên tục của DNSE ohlc ngày đáo hạn/roll (giả định: ngày đáo hạn vẫn là HĐ đáo hạn). Code có chốt chặn:
   giá HĐ thật lệch close VN30F1M >0,5% ⇒ PAUSED.

## 4. Dữ liệu same-day
- Tín hiệu live đọc `DNSEClient.ohlc("VN30F1M", resolution="1", type="derivative")` — §6 bright-line (DNSE, không BQ).
- Đối chiếu DNSE vs VCI (nguồn của `orb_pt.py`) trên **30 phiên 2026-10-06→11-16**: c0/entry/exit trùng tuyệt đối, sig khớp **30/30**,
  OR lệch 0bps; số bar 241 (2 ngày DNSE 242). `compute_signal` của executor trên bar DNSE vs `data/orb_pt_log.csv`: **30/30** cùng dấu.
  ⇒ đổi nguồn không đổi tín hiệu trên mẫu này. measured_by `agents/Taylor/research/orb_futures_stop_20261116/xfeed_dnse_vs_vci.py` (bar DNSE lưu `dnse_vn30f1m_1m_30d.csv`).
- Registry: nguồn mới chưa có entry `kb/data_registry/` (cần Winston/Mike thêm `dnse ohlc derivative VN30F1M`, CANONICAL cho same-day).

## 5. Executor `trading_bot/orb_futures.py` (tách biệt, không import executor cổ phiếu)
Vòng đời 1 phiên (state `data/orb_futures/state_SpaceX_<date>[_dry].json`, atomic):
INIT → (09:31:05, bar 09:30 phải có; 09:33 nới về bar cuối ≤09:30; quá 09:40 ⇒ SKIPPED) → tín hiệu 0 ⇒ FLAT ·
khác 0 ⇒ resolve HĐ VN30F1M (KRX) + secdef (trạng thái NRM) + chốt lệch giá 0,5% + gói 1306 + ppse qmax ≥1 (LIVE) +
**đối chiếu positions/sổ lệnh broker** ⇒ ghi ENTRY_PENDING ⇒ place LO (giá trần +0,3% so với giá khớp gần nhất) ⇒ ghi oid ngay ⇒
chờ khớp thật 60s (không khớp ⇒ huỷ ⇒ SKIPPED) ⇒ OPEN (stop = giá khớp × (1 ∓ 2,5%)) ⇒ poll 5s, bỏ qua 11:30–13:00 ⇒
STOP hoặc 14:29:00 ⇒ đối chiếu ⇒ EXIT_PENDING ⇒ LO đối ứng sàn/trần ⇒ chưa khớp 30s ⇒ huỷ + đặt lại ⇒ CLOSED.
14:45 còn vị thế ⇒ báo ĐỎ đóng tay (không bao giờ giữ qua đêm có chủ đích).
An toàn: flock không chặn · `data/BOT_STOP` ⇒ 0 lệnh (kể cả lệnh đóng — báo ĐỎ 5'/lần nếu đang có vị thế) · vị thế/lệnh lạ ⇒ PAUSED ·
restart ở *_PENDING ⇒ PAUSED, ở *_PLACED ⇒ chờ oid cũ · stage lạ ⇒ PAUSED · raw log có `account_no` (§12) · giờ neo ICT aware (§16) ·
journal riêng `data/orb_futures/journal_SpaceX[_dry].csv` (cùng cột journal executor, `book=ORB_FUT`, `play_type=LIVE|DRY`) — KHÔNG
trộn vào `exec_*_journal.csv` để kế toán cổ phiếu không đọc nhầm FILL phái sinh.
Cờ: `orb_futures.enabled` ở **cấp profile** (không ở `overrides` ⇒ không đụng `config.py`), chỉ literal `true` mới bật; TẮT ⇒ DRY:
đọc giá thật, chạy đủ vòng đời, ghi `DRY_PLACE_*` + khớp giả lập, KHÔNG gọi place/cancel. LIVE còn cần `mode=live` + trading-token
còn hạn (do `run_bot` 09:05 tạo; thiếu ⇒ bỏ phiên, báo).

**Selfcheck** `orb_futures_selfcheck.py` (FakeClient, `MIKE_BOT_TEST_MODE=1` trước import): 20 kịch bản / 38 assertion PASS dưới
`env -u TZ`, `TZ=Asia/Ho_Chi_Minh`, `TZ=America/New_York`, `TZ=Pacific/Kiritimati`. Đột biến (mutation) bị bắt: bỏ chặn lệnh lạ, DRY
gọi broker, đảo chiều stop, bỏ strict bar 09:30, bỏ ân hạn feed 09:33. (Đột biến "bỏ PAUSE khi restart ở _PENDING" KHÔNG làm test fail
vì lớp thứ hai — vòng lặp gặp stage lạ ⇒ PAUSED — cho cùng kết quả; đó là phòng thủ 2 lớp, không phải lỗ test.)
Smoke thật chỉ-đọc 16/11 23:36: DRY `--once` ⇒ SKIPPED (lỡ cửa sổ), reconcile đọc broker OK; `--plan-block` đọc DNSE thật OK.

## 6. Plan + vốn
- `send_plan_report.sh` SpaceX thêm khối "ORB futures sleeve": luật duyệt trước + kiểm ký quỹ; FAIL-OPEN (lỗi/rỗng/treo ⇒ 1 dòng cảnh
  báo). Selfcheck mới 5/5; 5 selfcheck send_plan_report cũ vẫn PASS (17, 5, 5, 74, 16). Không đổi orders/sizing cổ phiếu.
- Ký quỹ: tối thiểu = ký quỹ ban đầu 1 HĐ theo gói (18,48% × notional ≈ 34,1tr) + 2 × lỗ chạm stop (≈ 9,2tr) ≈ **43,3tr**; đích **100tr**.
  Thiếu ⇒ báo **"CẦN NỘP KÝ QUỸ PHÁI SINH ≥ X tr trước 09:25"** kèm số Trứng vàng (hôm nay: thiếu 100,0tr, Trứng vàng 752,3tr).
- Thao tác user (không có API): app DNSE — Trứng vàng → tiền cơ sở → **Nộp ký quỹ phái sinh**.
- `--funding-alert`: chỉ chạy khi cờ BẬT; gửi Trading Daily; báo "✅ đủ" 1 lần/ngày. Chưa nối Telegram (egg_transfer_alert dùng
  notify.sh + notify_thread + notify_telegram — đề xuất làm giống khi go-live).

## 7. Kế toán / NAV (chỉ PHÁT HIỆN — chưa sửa, vì ngữ nghĩa field chưa xác minh)
1. **`mike/bin/daily_nav_snapshot.py:1807`** `nav = mtm_stock + cash - debt + offbook + egg_value` — KHÔNG có tiền ký quỹ phái sinh.
   Ngày user nộp 100tr Trứng vàng → ký quỹ: egg −100tr, NAV báo tụt −100tr ⇒ cổng NAV-jump/TWR coi như lỗ hoặc rút vốn — SAI cho báo
   cáo NĐT ngoài. **Phải sửa TRƯỚC lần nộp ký quỹ đầu tiên**: cộng `derivative_equity` (tiền ký quỹ + lãi/lỗ chưa tất toán; EOD vị thế
   luôn 0 ⇒ chỉ còn tiền ký quỹ) đọc từ cùng bản ghi `balances` (`bal.payload.derivative`), có cột riêng `derivative_assets` trong
   `nav_history_SpaceX.csv` (thêm cột cuối, reader DictReader).
2. **`mike/bin/reconcile_equity.py:362`** vế trái/phải: thêm realized PnL phái sinh (từ `journal_SpaceX.csv` FILL ORB_FUT) − phí
   phái sinh (vế trái) và `derivative_equity` (vế phải), nếu không identity lệch đúng bằng PnL phái sinh.
3. **`nav_period_returns.py` / `account_cash_flows.json`**: chuyển egg → ký quỹ là chuyển NỘI BỘ, KHÔNG phải dòng tiền NĐT — khi (1)
   đã cộng `derivative_equity` thì không cần ghi flow; nếu chưa sửa (1) mà đã nộp, KHÔNG được vá bằng flow giả.
4. Báo cáo tuần/tháng SpaceX: dòng "Hợp đồng tương lai" trong bảng phân bổ + PnL sleeve ORB tách riêng (§21 không áp: không cổ tức).
5. Các reader `dnse_raw_*.jsonl` (§12): raw log ORB nằm FILE RIÊNG `data/orb_futures/orb_futures_raw_<date>.jsonl` ⇒ không ảnh hưởng.
Sửa (1)+(2) cần: probe 1 lần SAU khi nộp ký quỹ để biết field nào là tổng tiền (remainSecure? usedSecure?), rồi selfcheck nav_jump
(`nav_jump_flow_gate_selfcheck.py`, `reconcile_equity_egg_selfcheck.py`). Đề xuất giao Taylor làm ngay sau probe đó.

## 8. Rủi ro (nói thẳng — user đã chấp nhận có chủ đích, không tranh luận lại)
- 1 HĐ ≈ 184,3tr notional ≈ **1,84× sleeve 100tr** (dispatch ghi ≈1,9× ở giá 186).
- MaxDD lịch sử −31,8% trên notional, không stop (`orb_fiinx_vn30f1m_20260925/README` §3) ⇒ ≈ **−59tr** (ước lượng ở 186tr); với stop
  2,5% backtest −24,0% ⇒ ≈ −44tr (ước lượng). Drawdown sâu nhất kéo dài 206 phiên (2022-10→2023-09).
- **Gate #2 registry FAIL; DSR(N=20) 0,49** (dưới 0,95) — edge chưa chứng minh được ngoài cửa sổ 2023-09+.
- Bot giám sát stop là điểm hỏng đơn; khoá trần/sàn làm stop vô hiệu; lệnh đóng LO sàn/trần chưa test thật.
- Ký quỹ duy trì 17,71%: lỗ 2,5% không gọi ký quỹ nếu tiền ≥ tối thiểu ở trên; dưới ~43tr thì rủi ro call/thanh lý.

## 9. Checklist go-live (ai duyệt)
1. Mike: arch-review + quant-skeptic trên nhánh (cả 2 repo). 2. User duyệt merge. 3. Cài cron (Mike, theo §11 cron_registry) — DRY:
   - `30 2 * * 1-5` `bin/orb_futures_run.sh run` (09:30 ICT; Python tự chờ 09:31:05) → `logs/orb_futures_SpaceX_<date>.log`
   - `*/10 3-7 * * 1-5` cùng lệnh = watchdog (flock ⇒ không trùng; resume state).
   - `30,45 1 * * 1-5` + `0,15 2 * * 1-5` `bin/orb_futures_run.sh funding-alert` (chỉ có tác dụng khi cờ BẬT).
4. **DRY-run tối thiểu 10 phiên** (đề xuất; Mike/user có thể đổi): journal DRY vs `orb_pt_log.csv` — sig khớp 100%, giá vào/thoát lệch
   bao nhiêu bps; 0 PAUSED vô cớ. 5. Sửa NAV (mục 7) + selfcheck, merge. 6. User nộp ký quỹ 100tr ⇒ Taylor probe field `derivative` +
   ppse qmax ⇒ chốt mapping. 7. User bật cờ: diff đề xuất cho SpaceX profile trong `secrets/trading_bot_accounts.json`:
   `"orb_futures": {"enabled": true}` (thêm cạnh `"overrides"`, KHÔNG trong overrides). 8. Phiên LIVE đầu: Mike theo dõi; xác minh
   positions schema, order_detail, LO sàn/trần, phí thật từ email khớp lệnh (§27) — cập nhật mục 3 "chưa xác minh".
