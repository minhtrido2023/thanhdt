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

## TV1 discretionary (SpaceX) — PHẢI trừ cash trước khi tính plan V2.4 hàng ngày (thêm 2026-07-23)
SpaceX có 1 chương trình gom TV1/PECC1 riêng (`data/trade_plans/discretionary/plan_TV1_SpaceX_discretionary_20260723.json`, book=DISCRETIONARY_SPECIAL, ngoài V2.4, đã user duyệt) — tranche
07-24 (200cp≈3,98M) + 07-27 (200cp≈3,98M). File này KHÔNG tự động trừ vào `cash_vnd` khi lập
plan V2.4 hàng ngày vì nó tách file cố ý (không bị EOD clobber). TRƯỚC khi tính size lệnh V2.4
cho SpaceX ngày nào trùng lịch tranche TV1, PHẢI trừ trước số tiền tranche đó khỏi cash khả dụng
— nếu không, tổng nhu cầu 2 nguồn có thể vượt cash thực (sự cố thật 07-24: V2.4 45,9M + TV1
3,98M = 49,9M > cash 49,1M, thiếu ~0,78M). Luôn check file discretionary trước khi chốt size.

## LAG entry — GATE CỨNG rating≤3, TỰ ĐỘNG LOẠI rating≥4, KHÔNG escalate nữa (CHỐT 2026-07-27)
User đã CHỐT LUẬT (2026-07-27, sau 2 case liên tiếp TRC rồi MST cùng rating≥4): mọi ứng viên LAG
PHẢI có 8L rating ≤3 mới được đưa vào orders[]. Rating≥4 (RATING_FAIL) → TỰ ĐỘNG loại khỏi plan,
KHÔNG cần escalate Mike/user từng lần nữa (khác quy tắc cũ trước 07-27). Ghi vào `deferred_orders[]`
hoặc mục riêng với lý do "RATING_FAIL — auto-excluded per user policy 2026-07-27", không phải
orders[] và không phải trạng thái "chờ quyết định".
⚠️ **Đánh đổi đã biết, user đã được thông báo trước khi chốt**: backtest cùng ngày (job
Taylor_20260723_131958) test đúng biến thể "gate rating≤3 chặn cứng cho LAG" và kết quả NO-GO ở
cấp trung bình lịch sử (IS-negative, Sharpe 0,95→0,80) — nghĩa là luật này đánh đổi hiệu suất đo
được trong backtest để lấy bảo vệ khỏi rủi ro cá biệt (mã cụ thể chất lượng rất kém dù tín hiệu
PEAD kích hoạt, kiểu TRC rating=4/D và MST rating=4/E — PE 39x, ROE_Trailing 2,55%). Đây là quyết
định rủi ro/risk-tolerance của user, không phải sai số kỹ thuật — không tự ý đảo ngược nếu thấy
"backtest nói ngược lại", vì user đã biết và chấp nhận đánh đổi này.
Case cũ TRC (07-23) và MST (07-27) áp dụng hồi tố theo luật mới: cả 2 giữ nguyên KHÔNG mua.
✅ **ĐÃ MERGE VÀO MAIN, ACTIVE (2026-07-27, commit d7417a2)**: gate là `lag_rating_filter.
lag_filter_low_rating()` gọi trong `golive_recommend_v23.py` NGAY SAU bộ lọc thanh khoản, LOẠI THẬT
ứng viên LAG rating≥4 khỏi `lag_up`/`lag_recent` (điểm-thời-gian, rating tra `time≤LATEST`, không
look-ahead). Không chỉ gắn cờ nữa. Bị loại → ghi `status.json.lag_rating_excluded`. Self-check:
`lag_rating_filter_selfcheck.py` (20/20, verify TRC@07-21 + MST@07-27 bị loại, mã ≤3 giữ). CHỈ LAG,
BAL/CAPIT/custom30V không đụng. Gate này đang hoạt động thật — DollarBill không cần tự check rating
LAG nữa (đã lọc sẵn ở nguồn), nhưng NẾU thấy 1 mã rating≥4 lọt qua thì đó là bug thật, escalate ngay.

## CẤM field `funding_required: true` — plan phải tự SHRINK theo cash thực, không list-rồi-đợi-tiền (thêm 2026-07-27)
Đây là TÁI PHẠM đúng lỗi Trứng vàng 07-23 (context "Trứng vàng DNSE" ở trên) — lần này núp dưới field
mới `funding_required: true` thay vì đòi rút Trứng vàng trực tiếp, nhưng bản chất giống hệt: đưa lệnh
vào `orders[]` như đã quyết, ghi chú "cần thêm tiền" thay vì tự defer/shrink. Sự cố thật 2026-07-27:
plan SpaceX 07-28 có 7/8 lệnh `funding_required:true`, tổng 460,7M trong khi cash thực chỉ ~12,4M —
thiếu ~450M. CÙNG NGÀY, plan ZaloPay 07-28 xử lý ĐÚNG (chỉ giữ 1 lệnh CSV vừa đủ ppse 25,5M, tự bỏ
EVF/PSI/VCI dù cùng nguồn `golive_recommend_v23.py`) — chứng minh 2 dispatch riêng biệt cho ra 2 kỷ
luật khác nhau cho CÙNG một danh sách ứng viên.
QUY TẮC: `orders[]` CHỈ được chứa lệnh mà tổng giá trị ≤ cash thực có (`available_cash_vnd`/`ppse`,
không phải `total_cash` nếu có phần chưa settle). Lệnh không đủ tiền → KHÔNG đưa vào `orders[]`,
chuyển sang `deferred_orders[]` hoặc note riêng ghi rõ "DEFERRED — thiếu X VND", KHÔNG có field
`funding_required` hay bất kỳ cách diễn đạt nào ngụ ý "cứ lên plan rồi tính". Ưu tiên khi phải chọn
lệnh nào giữ/bỏ khi cash không đủ cho tất cả: LAG có deadline T+1/T+2 cứng > CAPIT top-up không
deadline > lệnh discretionary đã duyệt trước. Áp dụng NHẤT QUÁN cho CẢ 2 account — nếu 1 account
defer 1 mã vì thiếu cash, account kia gặp đúng tình huống thiếu cash cho đúng mã đó cũng phải defer,
không tự ý khác nhau giữa 2 lần dispatch.
⚠️ **TÁI PHẠM LẦN 3 (2026-07-28)**: dù đã cấm field `funding_required`, DollarBill vẫn đưa 4 lệnh
146,5M vào `orders[]` khi cash chỉ 10,41M — lần này núp dưới **văn xuôi tự nhiên** "user sẽ nạp
136M" thay vì field. Một job khác (`DollarBill_20260728_152001`) tự bắt và sửa trước khi tới Mike.
BÀI HỌC: lệnh cấm KHÔNG giới hạn ở tên field cụ thể — BẤT KỲ hình thức nào (field, câu văn, giả định
ngầm) coi `orders[]` như đã được cấp vốn thêm đều VI PHẠM. Tự kiểm tra bằng 1 câu hỏi duy nhất trước
khi hoàn tất plan: "tổng `orders[]` có ≤ cash thực CÓ SẴN NGAY BÂY GIỜ không, không giả định gì thêm?"
— nếu câu trả lời cần bất kỳ chữ "nếu"/"khi user nạp"/"sau khi có thêm" thì lệnh đó KHÔNG được ở
trong `orders[]`, phải nằm trong `deferred_orders[]`.

## LAG entry mới trong giai đoạn thị trường dễ vỡ — PHẢI ghi rõ rủi ro BEAR-liquidation (thêm 2026-07-27)
Allocator đã có sẵn cơ chế w_LAG=0 khi DT5G=BEAR (toàn bộ LAG book bị bán khi rơi BEAR — xác nhận
qua nghiên cứu regime 07-23, disc_c4/c5 NO-GO vì cơ chế này đã đủ, không cần gate thêm). NHƯNG khi
viết note cho 1 lệnh LAG mới lúc thị trường đã washout nhiều lần gần đây (CAPIT fired lặp lại, breadth
xấu) mà DT5G vẫn NEUTRAL (chưa xác nhận BEAR), PHẢI ghi rõ trong note: "Nếu regime chuyển BEAR, vị thế
này sẽ bị bán theo allocator (w_LAG=0)" — không để user phải tự hỏi lại. Đây là công khai rủi ro đã
biết, không phải đề xuất cơ chế mới (đã NO-GO, không mở lại trừ khi user yêu cầu).

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

## LAG entry window — CHỈ T+1 vào plan hôm nay, T+2/T+3 để dành cho `lag_upcoming_for_next_plans` (thêm 2026-08-03)
`golive_v23_recommendations_*.csv` (nguồn CHUNG cho cả 2 account) gắn `status` đúng theo từng mã:
`UPCOMING T+1 phiên tới` / `T+2` / `T+3`. **KHÔNG có script nào tự sinh `window_analysis`/
`orders`/`deferred_orders` từ CSV này** — mỗi plan JSON là do DollarBill tự đọc CSV và viết tay
mỗi lần dispatch, nên window filter là judgment call thủ công, không phải phép tính cơ học sẵn có.
Đây chính là chỗ đã ra sai lệch: plan SpaceX 08-04 lọc ĐÚNG (chỉ đưa T+1 vào `deferred_orders`
của hôm nay, T+2/T+3 xếp riêng vào `lag_upcoming_for_next_plans` chờ đúng ngày mở), còn plan
ZaloPay 08-04 (cùng CSV, cùng ngày) lọc SAI — đưa thẳng DCM (T+2) và DRI/POW (T+3) vào
`deferred_orders` của hôm nay như thể đã tới hạn, ĐỒNG THỜI bỏ sót hẳn APF (T+1, đủ điều kiện
đúng hôm nay, DD sạch y hệt TV2) — không xuất hiện ở đâu trong plan, và không đánh giá MAC/TV3.
0 lệnh đặt thật (orders=0 cả 2 plan) nên không có sự cố live, nhưng bug data-accuracy.

**Quy tắc bắt buộc mỗi lần lập plan T+1 (áp dụng CẢ 2 account, nhất quán):**
1. Liệt kê TOÀN BỘ mã LAG_HI/LAG_LO có `status` chứa `T+1` trong CSV signal_date hôm nay — đây là
   danh sách ứng viên duy nhất được xét vào `orders[]`/`deferred_orders[]` của plan hôm nay. Đối
   chiếu số lượng T+1 candidate giữa 2 account phải BẰNG NHAU (cùng CSV nguồn) trước khi viết plan
   — nếu khác nhau, đó là dấu hiệu bỏ sót, dừng lại kiểm tra lại.
2. Mã `status` chứa `T+2`/`T+3` → CHỈ được đưa vào `lag_upcoming_for_next_plans` (ghi rõ
   `entry_date` = ngày mở cửa sổ thật), KHÔNG được vào `orders[]`/`deferred_orders[]` của plan
   hôm nay dù DD sạch đến đâu — cửa sổ entry chưa mở.
3. Trước khi hoàn tất plan, tự hỏi: "mọi mã trong `deferred_orders[]`/`orders[]` của tôi có đúng
   `status=T+1` trong CSV không, không có mã T+2/T+3 lẫn vào?" — nếu không chắc, grep lại CSV
   bằng ticker, đừng tin trí nhớ từ session trước.

## `book_note` trong `positions_snapshot_eod_*` — dùng bootstrap snapshot làm nguồn, KHÔNG tự đoán theo tên mã (thêm 2026-08-04)
Root cause (`mike/agents/Taylor/research/bootstrap_book_snapshot_20260804.md` §2): field `book_note`
mỗi ngày là DollarBill tự SUY LUẬN theo tên mã (không có script cơ học nào sinh ra nó) — VPB và VND
ở SpaceX bị gắn nhãn mơ hồ `"LAG/PARK"` liên tục nhiều ngày dù truy vết fill history thật (journal
+ `plan_*.json` gốc lúc mua) cho kết quả rõ ràng 100% PARK. Nhãn sai này nếu bị tin sẽ làm
`park_mv_live` tính thiếu (ảnh hưởng trực tiếp thiết kế L1 park-target compliance).

**Quy tắc bắt buộc**: khi viết `book_note`/phân loại book cho vị thế đang giữ, ĐỌC
`data/trade_plans/bootstrap_book_snapshot_<account>_<ngày mới nhất có file>.json` trước — đây là
nguồn xác nhận từ fill history thật + user đã duyệt (`_status: "APPROVED..."`), KHÔNG suy luận
lại theo tên mã hay theo "mã nào từng thấy trong rổ nào". Mã KHÔNG có trong snapshot (mua sau
ngày snapshot) → dùng đúng `book`/`play_type` đã ghi trên order lúc đặt lệnh (đã có sẵn trong
plan ngày đó), không đoán.
