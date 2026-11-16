# ORB futures sleeve VN30F — đường thực thi LIVE SpaceX (spec, 16/11/2026)

Job `Taylor_20261116_162132` + vòng 2 `Taylor_20261116_165006` (sửa theo arch-review NEEDS_CHANGES + quant-skeptic REFUTED số rủi ro). Trạng thái: **CODE trên nhánh, CHƯA merge, CHƯA cài cron, cờ TẮT, 0 lệnh thật.**
Nhánh `feat/orb-futures-live-20261116` ở CẢ HAI repo:
- repo ngoài (`/home/trido/thanhdt`, worktree `WorkingClaude/wt-orb-futures-20261116`): `trading_bot/orb_futures.py`, `orb_futures_selfcheck.py`
- repo mike (worktree `agents/Taylor/wt-orb-futures-20261116`): `bin/orb_futures_run.sh`, khối ORB trong `bin/send_plan_report.sh`,
  `bin/send_plan_report_orb_wire_selfcheck.py`, nghiên cứu stop `agents/Taylor/research/orb_futures_stop_20261116/`, file này.

## 1. Quyết định user (16/11 23:20 ICT, decided_by: user — không hỏi lại)
1 HĐ VN30F · sleeve 100tr (nới trần 5% NAV) · stop thảm hoạ CHỌN THEO THỐNG KÊ · alpha giữ nguyên `orb_pt.py` ·
plan = duyệt trước LUẬT, hướng đi báo khi vào/thoát (Trading Daily + journal) · thiếu ký quỹ ⇒ báo nộp như quy trình Trứng vàng.

## 2. Stop thảm hoạ = ±2,5% từ giá khớp vào
Tiêu chí cố định cho MỌI lần đổi sau: `agents/Taylor/research/orb_futures_stop_20261116/PREREG_stop_selection.md` (commit riêng `2a6ddf10c`).
Chọn bằng tiêu chí khai TRƯỚC khi nhìn PnL: **mức nhỏ nhất có tỉ lệ phiên chạm ≤3%** (cầu chì hiếm). **N trial = 6**
(1,0/1,5/2,0/2,5/3,0/4,0%). Tape: 1.163 phiên 2022-02-17→2026-11-16 (FiinX 384 phiên chỉ có min/max; vnstock/VCI 779 phiên
bar 1m). Config mô phỏng = `orb_pt.py` (sign OR 09:00–09:30, vào close 09:30, slip 1 tick + 0,6bps); **thoát close bar 14:29 cho CẢ HAI
đoạn** (vòng 2 đồng nhất — bản 1 dùng 14:30 cho đoạn bar, 14:29 cho FiinX). Bảng dưới = số chạy lại vòng 2.
measured_by: `agents/Taylor/research/orb_futures_stop_20261116/stop_study.py` → `stop_study_result.json`.

MAE trong phiên (từ giá vào): p50 0,40% · p90 1,43% · p95 2,01% · p97 2,38% · p99 3,32% · max 10,71% (2022-11-16, short 865 → đỉnh 957,6).

| stop | chạm (toàn tape) | 2022-23 | 2023-26 | gap qua stop (bar 1m) | mean bps | Sharpe | cum | MaxDD lũy kế | lỗ 1 phiên tệ nhất |
|---|---|---|---|---|---|---|---|---|---|
| không | – | – | – | – | 6,04 | 0,88 | +88,1% | −31,4% | −946bps |
| 1,0% | 19,86% | 26,04% | 16,82% | 3 lần, max 2,2bps | 7,79 | 1,33 | +135,4% | −20,1% | −104bps |
| 1,5% | 9,11% | 13,80% | 6,80% | 2 lần, max 5,8bps | 8,09 | 1,32 | +142,5% | −21,0% | −158bps |
| 2,0% | 5,07% | 8,59% | 3,34% | 0 | 7,52 | 1,19 | +126,1% | −27,4% | −203bps |
| **2,5%** | **2,58% (30)** | 3,91% | 1,93% | **0** | 7,24 | 1,12 | +118,3% | −23,7% | **−253bps** |
| 3,0% | 1,46% | 2,34% | 1,03% | 0 | 7,05 | 1,08 | +113,2% | −24,8% | −303bps |
| 4,0% | 0,69% | 1,30% | 0,39% | 0 | 6,41 | 0,96 | +97,4% | −26,2% | −403bps |

### 2b. SỐ RỦI RO công bố lại (vòng 2, theo quant-skeptic REFUTED bản 1) — measured_by `stop_study.py` khối `v2_risk` trong `stop_study_result.json`
Chuẩn: **MaxDD CỘNG DỒN cho 1 HĐ cố định** (lãi/lỗ mỗi phiên = return × notional 184,3tr = 1.843 × 100.000, tham chiếu 16/11;
KHÔNG lãi kép trên notional — 1 HĐ không tự lớn lên). Bản 1 trích MaxDD lũy kế (lãi kép) = sai chuẩn cho sleeve 1 HĐ.
| Chỉ tiêu | Không stop | Stop 2,5% |
|---|---|---|
| Lỗ 1 phiên tệ nhất — khớp đúng mức stop | −946bps (2022-11-16) | **−253bps** |
| Lỗ 1 phiên tệ nhất — khớp ở CỰC TRỊ bar chạm stop | – | **−421bps** (2025-09-24, bar 14:22 vượt stop 169bps trong bar) |
| MaxDD cộng dồn (% notional / VND) | **−35,5% / −65,4tr** | **−25,5% / −47,0tr** |
| Như trên, theo sleeve 100tr | −65,4% | **−47,0%** |
| Độ nhạy phí +2bps khứ hồi (phí sở + thuế TNCN phái sinh CHƯA xác minh) | −39,9% / −73,5tr | −29,8% / **−54,9tr** |
Quant-skeptic tái lập độc lập (bản quy ước cũ): −26,0%/−48tr có stop, −36,0%/−66tr không stop, ≈−56tr với +2bps — lệch ≤1,1tr là do đổi
thoát về 14:29. **Chưa gồm** kịch bản khoá trần/sàn (stop không khớp được — lỗ chặn bởi biên ±7% quanh tham chiếu, không bởi stop).

**Stop = bảo hiểm, KHÔNG phải edge.** Toàn bộ cải thiện của stop nằm ở đoạn FiinX 2022-23 (384 phiên, chỉ có min/max ⇒ khớp lý tưởng,
không đo được trượt): MaxDD cộng dồn −34,3% → −24,3%, mean 0,40 → 3,96bps. Trên **779 phiên có bar 1m**: mean 8,81 → 8,85bps (không đổi),
MaxDD −8,0% → −7,1% (cộng dồn; lũy kế −7,8 → −7,0%). **Từ 2024 (704 phiên) stop hơi GIẢM mean 8,67 → 8,50bps.** Đừng trích cột
Sharpe/cum/MaxDD có stop ở bảng trên như bằng chứng hiệu quả.

- PnL chỉ để minh bạch, **không dùng để chọn**: 1,0/1,5% có Sharpe cao hơn nhưng chạm 20%/9% số phiên = cắt vì nhiễu, bị loại theo tiêu chí.
  Mọi dòng có stop đều "đẹp hơn" không stop — ĐỪNG đọc đó là edge mới: 6 trial trên cùng tape, không OOS riêng.
- Gap qua stop đo trên 779 phiên bar 1m: ở ≥2% chưa lần nào mở bar vượt mức stop. **Trượt TRONG bar không đo được** (không có tick);
  thực thi = LO đối ứng ở giá sàn/trần ⇒ khớp ở giá tốt nhất hiện có, cộng độ trễ poll 5s. Trường hợp xấu nhất: thị trường khoá
  trần/sàn (biên ±7% quanh tham chiếu) ⇒ stop KHÔNG khớp được, lỗ bị chặn bởi biên độ chứ không bởi stop.
- Quy ra tiền (notional 1 HĐ = 184,3tr ngày 16/11): stop chạm khớp hoàn hảo −253bps ≈ −4,7tr/phiên; khớp ở cực trị bar −421bps ≈ −7,8tr;
  phiên tệ nhất lịch sử không stop −946bps ≈ −17,4tr (≈ 1 ngày khoá trần/sàn).

**Stop đặt ở đâu — bot giám sát (chọn) vs lệnh STOP phía sàn:**
- **Đang dùng: bot giám sát** `latest_trade` (board G1) mỗi 5s, chạm ⇒ LO ngược chiều ở sàn/trần. Rủi ro: bot chết ⇒ không có stop
  tới khi cron watchdog (vòng 2: mỗi 2' từ 09:32) khởi động lại (resume từ state, không vào lại).
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
An toàn (vòng 2):
- **BOT_STOP + vị thế mở (B1)**: không vào mới; KHÔNG ghi đè SKIPPED; vẫn theo dõi giá; hằng số `ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = False`
  (chờ user quyết) ⇒ KHÔNG đặt cả lệnh đóng, báo ĐỎ (Telegram+Discord) lặp ≤1 lần/60s trong tiến trình + mỗi lần watchdog gọi lại, báo
  ngay khi chạm stop/qua 14:29, nêu "vị thế mở, BOT_STOP đang bật, cần user đóng tay". `True` ⇒ cho đóng (stop/14:29), không bao giờ vào.
  `_place` là lớp chặn cuối (OrderRefused).
- **Trạng thái kết thúc vẫn nhìn broker (B2)**: mọi lần chạy (kể cả SKIPPED/PAUSED/CLOSED/FLAT) đọc READ-ONLY positions phái sinh; net≠0
  hoặc không đọc được ⇒ báo ĐỎ lặp. Sau 14:29 còn OPEN ⇒ báo lặp. Trạng thái lệnh: chỉ `Cancelled/Rejected/Expired` + khớp 0 là CHẾT
  (so tuyệt đối sau chuẩn hoá — `PendingCancel` chứa chữ "cancel" nhưng là SỐNG); lệnh vào không chắc chết sau huỷ ⇒ PAUSED (không SKIPPED);
  đặt lại lệnh đóng chỉ khi MỌI oid đóng trước đã CHẮC chết + khớp 0 VÀ positions còn đúng vị thế (2 nguồn độc lập; nếu CẢ order_detail
  lẫn positions cùng cũ thì vẫn có thể đóng kép — giới hạn còn lại, cần probe thật).
- **Thiếu giá khớp (B3)**: dùng LTP → giá lệnh, cờ `fill_px_estimated`/`exit_px_estimated`, báo ĐỎ; không crash.
- **Vòng giám sát (B4)** try/except, lỗi thoáng qua ⇒ thử lại chu kỳ sau; mỗi 3 lỗi liên tiếp ⇒ báo ĐỎ. Lỗi giữa intent và oid ⇒ stage
  *_PENDING ⇒ PAUSED (không đặt lại). **Không đặt lệnh từ 14:45 (M1)** — 2 lớp (`_exit` + `_place`). **Thiếu khoá `positions`/`orders`
  (M2)** ⇒ PAUSED, không coi là rỗng. **notify (M3)** đọc exit code từng kênh, lỗi in stderr; báo ĐỎ đi cả Telegram. **m1** đọc lại state
  sau flock. **m2** account `enabled≠true` ⇒ ORB tắt.
- Còn lại: flock không chặn · vị thế/lệnh lạ ⇒ PAUSED ·
restart ở *_PENDING ⇒ PAUSED, ở *_PLACED ⇒ chờ oid cũ · stage lạ ⇒ PAUSED · raw log có `account_no` (§12) · giờ neo ICT aware (§16) ·
journal riêng `data/orb_futures/journal_SpaceX[_dry].csv` (cùng cột journal executor, `book=ORB_FUT`, `play_type=LIVE|DRY`) — KHÔNG
trộn vào `exec_*_journal.csv` để kế toán cổ phiếu không đọc nhầm FILL phái sinh.
Cờ: `orb_futures.enabled` ở **cấp profile** (không ở `overrides` ⇒ không đụng `config.py`), chỉ literal `true` mới bật; TẮT ⇒ DRY:
đọc giá thật, chạy đủ vòng đời, ghi `DRY_PLACE_*` + khớp giả lập, KHÔNG gọi place/cancel. LIVE còn cần `mode=live` + trading-token
còn hạn (do `run_bot` 09:05 tạo; thiếu ⇒ bỏ phiên, báo).

**Selfcheck vòng 2**: 32 kịch bản / 73 assertion PASS dưới `env -u TZ`, `TZ=Asia/Ho_Chi_Minh`, `America/New_York`, `Pacific/Kiritimati`,
`Europe/London`; 11/11 mutant bị bắt (B1 BOT_STOP→SKIPPED, PendingCancel=chết, bỏ kiểm lệnh đóng trước, bỏ watch trạng thái kết thúc,
bỏ ước giá khớp, bỏ try/except, đặt lệnh sau 14:45, thiếu khoá=rỗng, không đọc lại state, báo ĐỎ không Telegram, bỏ qua hằng số=True).
**Selfcheck bản 1** `orb_futures_selfcheck.py` (FakeClient, `MIKE_BOT_TEST_MODE=1` trước import): 20 kịch bản / 38 assertion PASS dưới
`env -u TZ`, `TZ=Asia/Ho_Chi_Minh`, `TZ=America/New_York`, `TZ=Pacific/Kiritimati`. Đột biến (mutation) bị bắt: bỏ chặn lệnh lạ, DRY
gọi broker, đảo chiều stop, bỏ strict bar 09:30, bỏ ân hạn feed 09:33. (Đột biến "bỏ PAUSE khi restart ở _PENDING" KHÔNG làm test fail
vì lớp thứ hai — vòng lặp gặp stage lạ ⇒ PAUSED — cho cùng kết quả; đó là phòng thủ 2 lớp, không phải lỗ test.)
Smoke thật chỉ-đọc 16/11 23:36: DRY `--once` ⇒ SKIPPED (lỡ cửa sổ), reconcile đọc broker OK; `--plan-block` đọc DNSE thật OK.

## 6. Plan + vốn
- `send_plan_report.sh` SpaceX thêm khối "ORB futures sleeve": luật duyệt trước + kiểm ký quỹ; FAIL-OPEN (lỗi/rỗng/treo ⇒ 1 dòng cảnh
  báo). Selfcheck mới 5/5; 5 selfcheck send_plan_report cũ vẫn PASS (17, 5, 5, 74, 16). Không đổi orders/sizing cổ phiếu.
- Cờ TẮT (N1, vòng 2): khối plan CHỈ 1 dòng "ORB sleeve (VN30F): TẮT/DRY", không đọc broker, KHÔNG in "CẦN NỘP KÝ QUỸ".
- Ký quỹ (vòng 2): mức tối thiểu cũ 43,3tr (KQ ban đầu + 2×stop) **BỎ** — một ngày khoá trần/sàn ≈ −17,4tr kéo 43,3tr xuống ~25,9tr <
  KQ duy trì 17,71% × 184,3tr ≈ 32,6tr ⇒ bị gọi KQ. Nay tối thiểu = max(**55tr**; KQ ban đầu + 2×stop; KQ duy trì + 9,46%×notional ≈ 50,1tr).
  **Khuyến nghị: nộp đủ 100tr** (đích sleeve), không nộp sát mức tối thiểu.
  Cờ BẬT mà thiếu ⇒ báo **"CẦN NỘP KÝ QUỸ PHÁI SINH ≥ X tr trước 09:25"** kèm số Trứng vàng (hôm nay: thiếu 100,0tr, Trứng vàng 752,3tr).
- Thao tác user (không có API): app DNSE — Trứng vàng → tiền cơ sở → **Nộp ký quỹ phái sinh**.
- `--funding-alert`: chỉ chạy khi cờ BẬT; gửi Trading Daily + Telegram, đọc exit code; gửi hỏng ⇒ không latch, lần sau nhắc lại.

## 7. Kế toán / NAV — ⛔ BLOCKER TRƯỚC LẦN NỘP KÝ QUỸ ĐẦU TIÊN (chưa sửa trong vòng 2, có chủ đích)
**Kế hoạch**: user nộp 1 khoản NHỎ vào ký quỹ phái sinh ⇒ Taylor probe READ-ONLY `balances.derivative` (field nào là tổng tiền ký quỹ) +
ppse qmax ⇒ RỒI MỚI sửa `daily_nav_snapshot.py:1807`, `compute_active_nav.py:444/556`, `reconcile_equity.py` + selfcheck ⇒ merge ⇒ rồi
mới nộp đủ 100tr. Chưa sửa mà nộp 100tr ⇒ NAV SpaceX (báo cáo NĐT ngoài) tụt −100tr giả.
1. **`mike/bin/daily_nav_snapshot.py:1807`** `nav = mtm_stock + cash - debt + offbook + egg_value` — KHÔNG có tiền ký quỹ phái sinh.
   Ngày user nộp 100tr Trứng vàng → ký quỹ: egg −100tr, NAV báo tụt −100tr ⇒ cổng NAV-jump/TWR coi như lỗ hoặc rút vốn — SAI cho báo
   cáo NĐT ngoài. **Phải sửa TRƯỚC lần nộp ký quỹ đầu tiên**: cộng `derivative_equity` (tiền ký quỹ + lãi/lỗ chưa tất toán; EOD vị thế
   luôn 0 ⇒ chỉ còn tiền ký quỹ) đọc từ cùng bản ghi `balances` (`bal.payload.derivative`), có cột riêng `derivative_assets` trong
   `nav_history_SpaceX.csv` (thêm cột cuối, reader DictReader).
1b. **`mike/bin/compute_active_nav.py:444/556`** — cùng lỗi thiếu tiền ký quỹ phái sinh trong active NAV (arch-review vòng 1).
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
- **(Đính chính vòng 2 — số bản 1 −59tr/−44tr dùng MaxDD lãi kép, sai chuẩn.)** MaxDD CỘNG DỒN 1 HĐ: **−65,4tr không stop / −47,0tr có stop
  (= −47% sleeve 100tr)**; +2bps phí khứ hồi ⇒ −54,9tr. Lỗ 1 phiên có stop: −253bps (khớp hoàn hảo) … −421bps (cực trị bar). Xem §2b.
  Drawdown sâu nhất kéo dài 206 phiên (2022-10→2023-09, số bản 1).
- **Gate #2 registry FAIL; DSR(N=20) 0,49** (dưới 0,95) — edge chưa chứng minh được ngoài cửa sổ 2023-09+.
- Bot giám sát stop là điểm hỏng đơn; khoá trần/sàn làm stop vô hiệu; lệnh đóng LO sàn/trần chưa test thật.
- Ký quỹ duy trì 17,71% ≈ 32,6tr: dưới 55tr thì 1 ngày khoá trần/sàn đủ gây gọi ký quỹ/thanh lý — nộp đủ 100tr.

## 9. Checklist go-live (ai duyệt)
1. Mike: arch-review + quant-skeptic trên nhánh (cả 2 repo). 2. User duyệt merge. 3. Cài cron (Mike, theo §11 cron_registry) — DRY:
   (host TZ=UTC — giờ dưới là **UTC**, ICT = UTC+7; KHÔNG tự cài)
   - `30 2 * * 1-5` `bin/orb_futures_run.sh run` (09:30 ICT; Python tự chờ 09:31:05) → `logs/orb_futures_SpaceX_<date>.log`
   - watchdog cùng lệnh, **mỗi 2' từ 09:32 tới 14:50 ICT** (flock ⇒ không trùng; resume state; trạng thái kết thúc ⇒ chỉ đọc positions + báo nếu ≠0):
     `32-58/2 2 * * 1-5` · `*/2 3-6 * * 1-5` · `0-50/2 7 * * 1-5`
   - `30,45 1 * * 1-5` + `0,15 2 * * 1-5` `bin/orb_futures_run.sh funding-alert` (chỉ có tác dụng khi cờ BẬT).
4. **DRY-run tối thiểu 10 phiên** (đề xuất; Mike/user có thể đổi): journal DRY vs `orb_pt_log.csv` — sig khớp 100%, giá vào/thoát lệch
   bao nhiêu bps; 0 PAUSED vô cớ. 5. Sửa NAV (mục 7) + selfcheck, merge. 6. User nộp ký quỹ 100tr ⇒ Taylor probe field `derivative` +
   ppse qmax ⇒ chốt mapping. 7. User bật cờ: diff đề xuất cho SpaceX profile trong `secrets/trading_bot_accounts.json`:
   `"orb_futures": {"enabled": true}` (thêm cạnh `"overrides"`, KHÔNG trong overrides). 8. Phiên LIVE đầu: Mike theo dõi; xác minh
   positions schema, order_detail, LO sàn/trần, phí thật từ email khớp lệnh (§27) — cập nhật mục 3 "chưa xác minh".
