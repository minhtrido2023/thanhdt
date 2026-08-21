# Mike fleet — context planning (DollarBill only)
> Phần CHUYÊN BIỆT cho việc lập plan T+1 — không lặp lại safety core (đã import riêng ở
> CLAUDE.md), không có chi tiết phương pháp backtest/DSR/PBO (việc của Taylor, chỉ cần
> KẾT QUẢ để lập plan, không cần cách tính ra). Cần domain khác ngoài đây (backtest chi
> tiết/pháp lý/thực thi)? Đọc `kb/context_pack.md` qua Read tool nếu tự tin đúng chỗ, hoặc
> escalate Mike — đừng đoán.
>
> Mục tình huống (tần suất thấp hơn) đã tách sang `context_planning_ext.md` (2026-08-19, OKF
> split khi vượt 40KB) — file đó KHÔNG auto-load, đọc bằng Read tool khi gặp đúng tình huống:
> DRI/TV1 khung giá rải bậc, LAG entry EXCLUDE list, `book_note`/`book_breakdown_current`,
> FLOOR_FAIL, WATCH cao su RSS3.

## V2.4 — chiến lược production (tóm tắt, không phải phương pháp)
2 book: **BAL** (momentum SIGNAL_V11, yieldcombo 1/PE+1/PCF) + **LAG** (PEAD/earnings drift).
Allocator `w_LAG` theo regime: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
**NEUTRAL parking = custom30V**, target **80%** phần idle cash khi BAL/LAG rỗng (cấu hình **F1**,
user chốt 2026-08-04, thay mức 70% cũ — `trading_rules.json` v2.3 `neutral_parking`). Số đúng phải
trích (cùng 1 vintage `universe_pit`/`LAG_ADV_BASIS=price`, nguồn
`agents/Taylor/research/park_wiring_two_options_20260804.md`): **70% = CAGR 28,86% / Sharpe 1,90 /
MaxDD −17,8% / Calmar 1,62** · **80% (F1) = 29,85% / 1,87 / −18,3% / Calmar 1,63** (đỉnh Calmar cả
dải) · 85% = 30,51% / 1,86 / −18,9% / 1,62. **KHÔNG trích bảng cũ** `measured_tradeoff_job_130720`
(Sharpe 1,78 vs 1,66 / DD −16,5%) — vintage 07-03 khác cơ sở và không hề có mức 80%.
Đổi target khỏi **80%** cần field `risk_dial_confirmed_by_user` + `risk_dial_warning_acknowledged`
trong `trading_rules.json`, thiếu 1 trong 2 → Mafee tự block plan. Plan chạy đúng mặc định 80%
thì **không cần** 2 field đó.
✅ **Đồng bộ engine xong 2026-08-04T11:34 ICT**: `golive_recommend_v23.py:96 ETF_PARK` đổi
`{3:0.7}`→`{3:0.8}` (user xác nhận qua Mike) — đường MUA và đường BÁN (L1) giờ cùng nhắm 0,80.
Còn nợ xác minh: lần chạy live kế tiếp (09:05 ICT) phải in ra `etf_park_frac=0.8` trong
`golive_v23_status.json` — kiểm tra thật, đừng suy từ việc đã đổi dòng code.

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

## TV1 — KHÔNG tự viết lệnh nữa, injector sở hữu (ĐỔI 2026-08-12, job Taylor_20260812_161457)
**TV1 là mã DUY NHẤT hiện có cơ chế tự động.** Từ 2026-08-12, lệnh mua TV1 của CẢ HAI account do
`mike/bin/discretionary_accumulation_inject.py` (cron 20:30 ICT, SAU khi bạn ghi plan ~19:0x) tự
sinh từ state file `data/trade_plans/discretionary/state_TV1_{SpaceX,ZaloPay}.json`.

**Bạn PHẢI:**
1. **KHÔNG đưa lệnh TV1 nào vào `orders[]`** — không qty, không `ref_price`, và tuyệt đối không
   `hard_no_chase_ceiling_vnd` gõ tay. Trần giá nay là TRẦN ĐỘNG tính lại mỗi phiên
   (`mean(giá đóng 5 phiên) × 1,03`, kẹp ≤25.000đ user duyệt); mọi con số bạn nhớ được đều đã cũ.
   Bạn viết một lệnh TV1 vào plan = injector thấy trùng và **im lặng bỏ qua** (dedup theo
   ticker+book) ⇒ trần cũ 20.000đ quay lại và lệnh lại không khớp.
2. **Trừ trước ngân sách TV1 khỏi cash khả dụng** trước khi size lệnh V2.4, đúng như luật cũ
   (sự cố thật 07-24: V2.4 45,9M + TV1 3,98M = 49,9M > cash 49,1M). Ước lượng ngân sách =
   `5% × active_nav − giá_trị_thị_trường(TV1 đang giữ)`, sàn 0. Không trừ ⇒ gate tiền của
   injector tự SHRINK/bỏ lệnh TV1 (nó chạy sau nên nó là bên nhường) và chương trình đứng hình.
3. **Ghi 1 dòng trong `notes`** nói rõ đã trừ bao nhiêu cho TV1 và rằng lệnh do injector chèn —
   để người duyệt lúc 21:00 biết lệnh TV1 sẽ xuất hiện, không tưởng là thiếu.

**Nếu plan 21:00 KHÔNG có lệnh TV1** mà tỷ trọng đang dưới 5%: đọc `discretionary_inject_notes`
trong chính file plan (injector ghi lý do fail-safe vào đó) — nguyên nhân hay gặp nhất là
`data/execution_logs/active_nav_<account>.json` không phải của HÔM NAY. Chạy
`python3 mike/bin/compute_active_nav.py --account <acct>` rồi
`python3 mike/bin/discretionary_accumulation_inject.py --account <acct>`. ĐỪNG tự gõ lệnh bù.

**DRI thì NGƯỢC LẠI: vẫn do bạn viết tay** (chưa có state file) — mục dưới vẫn áp dụng đầy đủ cho
DRI. Đừng suy rộng luật TV1 sang DRI rồi bỏ sót DRI khỏi plan.

## DRI + TV1 discretionary — target 5% NAV/mã, khung giá rải bậc → `context_planning_ext.md`
Tóm tắt: target 5% NAV/mã mỗi account (chốt 2026-08-10/11), DRI khớp đủ/TV1 từng gần như không
khớp (đã xử lý bằng trần động injector). Chi tiết đầy đủ (khung giá rải bậc T1/T2/T3, cách kiểm
tỷ trọng thật) → đọc `context_planning_ext.md` § "DRI + TV1 discretionary" khi cần rải thêm/kiểm
tỷ trọng DRI, hoặc khi giá chạm vùng bán/chốt lời.

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

## LAG entry EXCLUDE list — kiểm tra TRƯỚC khi đưa mã LAG mới vào plan → `context_planning_ext.md`
Danh sách hiện tại: **IVS**, **TMG** (cả hai loại 2026-07-21). Đọc `context_planning_ext.md` § "LAG entry
EXCLUDE list" trước khi đưa BẤT KỲ mã LAG_HI/LAG_LO mới nào vào plan.

## Trứng vàng DNSE (manual off-book tracking) — ĐÃ RÚT HẾT VĨNH VIỄN cả 2 account (cập nhật 2026-07-23)
SpaceX + ZaloPay đều `manual_offbook_assets_vnd=0` — **không phải "tạm hết", là đã đóng hẳn
nguồn này**. TUYỆT ĐỐI không giả định/đề xuất "user rút thêm Trứng vàng" để bù cash gap khi lập
plan — đây không phải một ATM có thể yêu cầu nạp lại theo nhu cầu plan. Nếu 1 ngày tổng giá trị
lệnh muốn đặt vượt quá cash thực có (`cash_vnd` trong nav_basis), PHẢI tự SHRINK/loại bớt lệnh
theo đúng cash thực — không viết "user cần rút X triệu hôm nay" như một điều kiện của plan. Sự cố
thật 2026-07-23: DollarBill lập plan SpaceX 07-24 với 6 lệnh tổng 177,2M trong khi cash chỉ
~49,1M, rồi yêu cầu user tự rút thêm ~128-134M "Trứng vàng" — nguồn đã xác nhận không còn tồn
tại. Nếu user báo có nạp tiền mới (không phải Trứng vàng, có thể là chuyển khoản khác) → đó là
fact mới, hỏi rõ nguồn trước khi đưa vào plan như đã xác nhận.

⚠️ **KHÔNG nhầm với `egg.totalValue`** (mục "`egg.totalValue` (Trứng vàng)" bên dưới) — đó là
field API riêng (live từ 2026-08-18) phản ánh số dư THẬT hiện có trong sản phẩm Trứng vàng của
DNSE, ĐỘC LẬP với biến `manual_offbook_assets_vnd` (cơ chế nhập tay cũ, đã khoá về 0 ở mục này).
Mục này nói "đừng ĐỀ XUẤT rút thêm ngoài kế hoạch"; mục egg nói "đừng BỎ QUA số dư egg thật đang
có khi giải thích lý do thiếu tiền" — hai lỗi ngược chiều nhau, đọc đúng mục theo tình huống.

## LAG entry window — CHẠY SCRIPT, KHÔNG tự lọc bằng mắt (thêm 2026-08-03, chuyển sang code 2026-08-04)
Root cause cũ (sự cố 08-03/08-04): lọc `status` T+1 vs T+2/T+3 trong `golive_v23_recommendations_
*.csv` từng là judgment call thủ công mỗi lần dispatch — 1 phiên lọc đúng, phiên kia lẫn T+2/T+3
vào như đã tới hạn + bỏ sót ứng viên T+1 thật. Đã chuyển thành quyết định CƠ HỌC.

**Quy trình bắt buộc mỗi lần lập plan** (43/43 selfcheck PASS, `mike/agents/Taylor/research/
deterministic_plan_decisions_20260804.md`):
```bash
python3 mike/bin/filter_lag_entry_window.py --account <SpaceX|ZaloPay> --json
```
- Output liệt kê đúng danh sách T+1 (đưa vào `orders[]`/`deferred_orders[]` hôm nay) và T+2/T+3
  (xếp vào `lag_upcoming_for_next_plans`, ghi `entry_date` script trả về). **KHÔNG tự lọc lại bằng
  mắt, không sửa danh sách script trả về.**
- Script **fail-closed theo lịch**: nếu `plan_date` không khớp phiên kế tiếp thật của
  `signal_date`, script thoát exit 2 thay vì đoán — thấy lỗi này thì dừng lại kiểm tra ngày, đừng
  tự suy diễn cho qua.
- Kết quả từ script cho 2 account CÙNG 1 CSV phải cho ra CÙNG danh sách T+1 — nếu thấy khác nhau,
  đó là dấu hiệu 1 trong 2 lần chạy dùng sai `--signal-date`, dừng lại kiểm tra tham số.

## `book_note`/`book_breakdown_current` — dùng bootstrap snapshot + `park_holdings.py`, KHÔNG tự đoán → `context_planning_ext.md`
Nguồn ĐÚNG: `python3 mike/bin/park_holdings.py --account <X> --json`, field `by_book` — KHÔNG tự
suy loại book theo tên mã (bug tái diễn 2 lần: VPB/VND 08-04, SCL 08-17). Đọc
`context_planning_ext.md` § "book_note" trước khi tự gõ tay field này.

## L1 park-trim — MỖI LẦN lập plan phải chạy `compute_park_trim.py` trước (thêm 2026-08-04, ĐÃ BẬT)

> **TRẠNG THÁI: BẬT từ 2026-08-04.** Cả 3 điều kiện đã đủ: (a) quant-skeptic CONFIRMED cao
> (2026-08-04T03:16Z), (b) Mike đọc lại diff `executor.py`, (c) target 0,80 đã được ghi nhận là
> **mặc định mới** trong `trading_rules.json` v2.3 (job `Taylor_20260804_034133`).
> ⚠️ **Script vẫn tự in dòng "CỔNG CHƯA MỞ"** vì nó so target 0,80 với `etf_park_frac=0,70` mà
> engine `golive_recommend_v23.py` còn publish. Dòng đó nói về **đường MUA của engine chưa đồng bộ**
> (`neutral_parking.pending_engine_consistency`), KHÔNG phải cổng chính sách — cổng chính sách đã
> mở. Cứ chạy và đính `park_trim_proposal` như dưới, nhưng **chép nguyên dòng cảnh báo đó vào
> `notes` của plan** để user thấy hệ đang ở trạng thái lai (mua tới 70%, chỉ trim khi vượt 80%).

**Vấn đề nó vá** (`mike/agents/Taylor/research/park_unpark_live_wiring_20260803.md` §A5): engine mô
phỏng có BA đường vào/ra sổ PARK, live chỉ có MỘT — và nó là đường MUA. Không có đường bán nào ⇒
tỷ trọng PARK live trôi lên trên trần mà chính backtest của nó đã mô phỏng. Đo thật 08-03: SpaceX
giữ PARK vượt trần **+189,4tr** trong khi cùng ngày plan ghi `HOLD ALL — chờ user nạp vốn` cho 2
lệnh cần 171,1tr. Đây KHÔNG phải rule mới — là **live đang vi phạm một rule đã có**.

**Quy trình bắt buộc mỗi lần lập plan (khi đã bật):**
1. Chạy TRƯỚC khi viết `orders[]`, cho ĐÚNG account đang lập plan:
   ```bash
   python3 mike/bin/compute_park_trim.py --account <SpaceX|ZaloPay> \
       --out data/trade_plans/park_trim_<account>_<plan_date>.json
   ```
2. `decision == "NO_TRIM"` → không làm gì thêm, KHÔNG thêm field nào vào plan.
3. `decision == "TRIM"` → đưa nguyên `orders[]` của nó vào plan JSON dưới key riêng
   **`park_trim_proposal`** (KHÔNG trộn vào `orders[]` của V2.4 — nguồn khác nhau, cơ chế duyệt phải
   thấy được nó là đề xuất tuân-thủ-trần chứ không phải tín hiệu mua/bán của book BAL/LAG):
   ```json
   "park_trim_proposal": {
     "source": "mike/bin/compute_park_trim.py",
     "asof": "<asof>", "decision": "TRIM",
     "target_park": 0.80, "park_mv_vnd": ..., "pool_vnd": ...,
     "trim_total_vnd": ..., "trim_proposed_vnd": ..., "trim_shortfall_vnd": ...,
     "risk_dial_override": "<id/ghi chú xác nhận của user — CHƯA CÓ thì để null và KHÔNG đề xuất>",
     "orders": [ { "ticker": ..., "side": "sell", "qty": ..., "ref_price": ...,
                   "book": "PARK", "play_type": "PARK_TRIM", "reason": "..." } ],
     "blocked": [ ... ], "notes": [ ... ]
   }
   ```
4. `decision` bắt đầu bằng `BLOCKED_` → **KHÔNG tự sửa, KHÔNG tự bỏ qua**: ghi nguyên `decision` +
   `notes` vào plan dưới `park_trim_proposal` và báo lên bus. `BLOCKED_RECONCILE` nghĩa là sổ lô
   lệch sổ broker — đó là việc phải có người xem, không phải lý do để im lặng.

**Ranh giới CỨNG — không được nới trong bất kỳ plan nào:**
- Lệnh trong `park_trim_proposal` **vẫn phải qua đúng cơ chế duyệt như mọi lệnh khác**: user duyệt
  plan → Mafee plan-bound. Script CHỈ ĐỌC, tự nó không đặt gì.
- **Không sửa `qty`/`ticker`** mà script đề xuất, cũng không thêm mã script đã bỏ qua. Pro-rata theo
  trọng số + FIFO theo lô là ĐÚNG cơ chế engine đã backtest; bán sạch vài mã "cho gọn" = đổi cấu
  trúc rổ = đi ra ngoài thứ đã đo (§B4 báo cáo gốc).
- **Chỉ sleeve PARK.** CAPIT (stop_exempt/slot_exempt), LAG, BAL, DISCRETIONARY_SPECIAL và
  `excluded_tickers` (DGC ở ZaloPay) KHÔNG BAO GIỜ nằm trong đề xuất này. Thấy chúng xuất hiện =
  bug, dừng lại báo, đừng sửa tay cho qua.
- Tiền thu từ trim là dry powder cho LAG/BAL — nhưng nó **không tạo quyền mua**: mọi lệnh mua vẫn
  đi qua gate hiện có (DD, 8L rating≤3, `cap_lag_orders` %ADV, `filter_lag_rating_orders`).

## L2 JIT-unpark — MỖI LẦN lập plan có lệnh BAL/LAG phải chạy `compute_jit_unpark.py` trước khi defer (thêm 2026-08-06, ĐÃ BẬT)

> **TRẠNG THÁI: BẬT từ 2026-08-06.** Chuỗi build A(port công thức engine)+B(gross-up phí ma sát
> 0,15%)+C(làm tròn LÊN 1 lô khi chắc chắn đủ tiền) đều quant-skeptic CONFIRMED cao cùng ngày
> (`Taylor_20260806_015739`/`_025613`/`_033014`). User chốt chính sách 2 điểm: (1) chọn Phương án
> B thay vì A gốc (A một mình để hụt tới 12,5% lệnh mua do làm tròn phí); (2) chọn thêm Phương án
> C trên nền B (B một mình vẫn để 5/6 ca hụt nguyên do làm tròn LÔ — C đưa về 6/6 hết hụt, đo thật
> trên dữ liệu 2026-08-05).

**Vấn đề nó vá**: L1 chỉ trim PARK theo TRẦN TUÂN THỦ (vượt 80% pool thì trim), không liên quan gì
đến việc có lệnh BAL/LAG cụ thể đang thiếu tiền hay không. Trước 08-06, hệ **defer nguyên lệnh**
khi thiếu tiền dù PARK còn dư dả — đây chính là hành vi thụ động user chỉ ra 08-03 (PARK 579M/61%
NAV trong khi LAG chỉ cần 171M). Cơ chế backtest thật (đã pin 28,86%) dùng đúng bước "bán PARK
NGAY LÚC mua BAL/LAG" — xem `mike/agents/Taylor/research/book_attribution_funding_order_20260805.md`
Q1 (0 lệnh bị bỏ trong bản pin, PARK bị bán 8.789,4 tỷ để nuôi deal suốt 12,46 năm).

**Quy trình bắt buộc mỗi lần lập plan (khi đã bật):**
1. **Chạy L1 TRƯỚC** (mục trên) — dù `NO_TRIM` cũng phải chạy để có file `--out` dùng cho bước 2.
2. Viết đầy đủ `orders[]` BAL/LAG (mọi lệnh mua dự kiến trong plan) như bình thường. Sau đó chạy
   ĐÚNG 1 LẦN cho CẢ plan (script tự quét mọi lệnh mua book BAL/LAG bên trong, không phải gọi riêng
   từng mã) — **luôn truyền `--l1-json` trỏ đúng file L1 vừa xuất** để tránh 2 lớp đề xuất bán
   trùng cùng cổ phiếu:
   ```bash
   python3 mike/bin/compute_jit_unpark.py --account <SpaceX|ZaloPay> \
       --plan data/trade_plans/plan_<account>_<plan_date>.json \
       --l1-json data/trade_plans/park_trim_<account>_<plan_date>.json \
       --out data/trade_plans/jit_unpark_<account>_<plan_date>.json
   ```
   `--margin-room` KHÔNG truyền (mặc định 0 = đúng cấu hình R3 đã pin, V2.5 DISABLED) — đổi khác
   là thay đổi chính sách, cần user duyệt riêng.
3. `decision == "NO_JIT_NEEDED"` (mọi lệnh đã đủ cash) → không làm gì thêm, không thêm field nào.
   `decision == "NO_SELL_POSSIBLE"` hoặc `"BLOCKED_ALL_NAMES"` → giữ nguyên hành vi cũ (lệnh mua bị
   co/defer theo sức mua hiện có, đọc rõ lý do trong `notes`), không tự chế đường bán nào khác.
4. `decision == "JIT"` → đưa nguyên `orders[]` (đề xuất bán PARK) VÀ `buy_amendments[]` (chi tiết
   từng lệnh mua: `status` FUNDED_BY_JIT/SHRINK/DROP, `needed_vnd`, `jit_sell_vnd`,
   `jit_proceeds_net_vnd`, `qty_final`) vào plan JSON dưới key riêng **`jit_unpark_proposal`**
   (KHÔNG trộn `orders[]` của L2 vào `orders[]` của V2.4/`park_trim_proposal` của L1 — nguồn khác
   nhau, cơ chế duyệt phải phân biệt được đề xuất tài trợ với tín hiệu mua/bán book hay trim tuân
   thủ). Copy nguyên cấu trúc JSON script `--out` sinh ra, đừng viết tay lại.
5. `decision` bắt đầu bằng `BLOCKED_` (RECONCILE/NO_PLAN/DAYCAP/SHARE/BOOK_INVARIANT) →
   **KHÔNG tự sửa, KHÔNG tự bỏ qua**: ghi nguyên `decision` + `notes` vào plan dưới
   `jit_unpark_proposal` và báo lên bus. `BLOCKED_RECONCILE` nghĩa là sổ lô lệch sổ broker.

**Ranh giới CỨNG — giống hệt L1, không được nới trong bất kỳ plan nào:**
- Lệnh trong `jit_unpark_proposal` **vẫn phải qua đúng cơ chế duyệt như mọi lệnh khác**: user duyệt
  plan → Mafee plan-bound. Script CHỈ ĐỌC, tự nó không đặt gì.
- **Chỉ sleeve PARK.** CAPIT (stop_exempt/slot_exempt), LAG, BAL, DISCRETIONARY_SPECIAL và
  `excluded_tickers` (DGC ở ZaloPay) KHÔNG BAO GIỜ nằm trong đề xuất này.
- **Bán dư tối đa đúng 1 lô/lệnh mua** (đặc tính Phương án C, đã duyệt) — không phải "bán tuỳ ý cho
  chắc". Nếu 1 plan có nhiều lệnh BAL/LAG cùng thiếu tiền, mỗi lệnh có thể dư tối đa 1 lô riêng —
  chưa có ca thật đo tổng dư nhiều lệnh cùng lúc, để ý khi gặp.
- Tiền thu là để tài trợ ĐÚNG lệnh đang thiếu — không tạo quyền mua mới: lệnh vẫn qua mọi gate hiện
  có (DD, 8L rating≤3, `cap_lag_orders` %ADV, `filter_lag_rating_orders`, funding gate A1).

Chi tiết cơ chế + số đo đầy đủ: `mike/agents/Taylor/research/jit_unpark_L2_build_20260806.md` (A),
`jit_unpark_grossup_20260806.md` (B), `jit_unpark_roundup_c_20260806.md` (C).

## `BLOCKED_RECONCILE` — kiểm corp-action TRƯỚC khi báo "lệch không rõ lý do" (thêm 2026-08-19, ca VIX)
Thấy `BLOCKED_RECONCILE` (sổ lô lệch broker), đừng chỉ báo "lệch, không hiểu lý do" rồi defer — 90%
ca thật (VHM 08-06, MBB 08-11, BID 08-17, VIX 08-20) là GDKHQ đã biết trước, KHÔNG phải lỗi kế toán.
Trước khi báo lên bus, tự kiểm 2 việc rẻ:
1. `data/corp_action_daily/corp_action_daily_<today>.json` → mục `upcoming_events_held`/`events_today`
   có ticker đang lệch không (cron 07:30 hằng ngày quét sẵn, thường đã cảnh báo TRƯỚC vài ngày).
2. Hệ số lệch (broker_qty / ledger_qty) có khớp `exercise_ratio` của sự kiện đó không, VÀ tổng giá
   vốn (`costPrice × qty`) có bất biến qua 2 phía không (dấu hiệu phân biệt corp action với fill sót
   journal — fill sót sẽ LÀM TĂNG tổng giá vốn, corp action thì giữ nguyên tới đồng).
Khớp cả 2 → đây gần chắc là corp action thật, nhưng **BẠN vẫn KHÔNG được tự ghi `CONFIRMED` vào
`data/corp_actions.json`** (đó là quyết định cần ≥2 nguồn độc lập xác nhận bởi Mike/Taylor/Winston,
xem `mike/bin/corp_actions.py` docstring + `§_rule` đầu file registry) — việc của bạn là báo CỤ THỂ
("VIX lệch 100→105, khớp đúng exercise_ratio=0.05 của sự kiện ISS exright_date=2026-08-20 trong
corp_action_daily hôm nay, tổng giá vốn bất biến") thay vì chỉ "lệch, không rõ lý do" — câu sau làm
người xử lý phải tự điều tra lại từ đầu những gì bạn đã có sẵn trong tay. Sau khi record được ghi
`CONFIRMED`, `park_holdings.py` tự áp lại và `reconcile.ok` trở về `true` — không cần bạn làm gì thêm.

## CAPIT exit (60 phiên) không còn bán oan phần custom30V cùng mã (fix 2026-08-21, commit `2baf6581`)
Khi 1 episode CAPIT paper đóng ở phiên 60 (`CAPIT_HOLD`), `strategies.py::build_plan()` diff step
trước đây tính `target=0` cho mã đó rồi sinh lệnh BÁN TOÀN BỘ vị thế broker — kể cả phần mã đó đang
nằm trong custom30V parking (case thật: PVT/SIP vừa là CAPIT vừa là parking). Đã vá bằng
`_capit_qty_per_ticker()`/`_capit_floor_diff()`: lệnh bán giờ chỉ floor đúng phần CAPIT-attributable
(theo `capit_episode.json` `qty_per_account`), phần custom30V còn lại giữ nguyên. Episode đang mở
hiện tại (`CAPIT-2026-07-20`, basket NCT/PVT/SAB/SIP/VNM) ở phiên 24/60, ETA chạm ngưỡng ~đầu
10/2026 — khi lập plan quanh mốc đó, KHÔNG cần tự thêm exit logic thủ công, cơ chế đã tự chạy đúng.

## `egg.totalValue` (Trứng vàng) — tiền THẬT, KHÔNG PHẢI sức mua hôm nay (thêm 2026-08-19)
Balances API DNSE trả thêm khối `egg` (`{"egg": {"totalValue": ...}}`, live từ 2026-08-18) — đây
CHÍNH LÀ "Trứng vàng"/tiền gửi thông minh của DNSE, một sản phẩm TÁCH RIÊNG khỏi `stock.totalCash`/
`availableCash`/`depositInterest`. `compute_active_nav.py`/`daily_nav_snapshot.py` đã cộng nó vào
NAV tự động (đúng — đó là vốn user sở hữu, câu hỏi "tôi sở hữu bao nhiêu" theo §25 coding_guidelines)
NHƯNG **không cộng vào `availableCash`/`ppse.pp0Buy`** — đúng, vì tiền trong egg cần RÚT (redeem)
trước, và theo user (2026-08-19): lệnh rút đêm nay/sáng sớm mới về `availableCash` kịp phiên sáng
hôm sau, KHÔNG kịp phiên hôm nay.
**Hệ quả cho việc lập plan:** khi 1 lệnh mua bị chặn/defer chỉ vì thiếu `availableCash`, TRƯỚC KHI
ghi lý do "thiếu tiền" — đọc `egg.totalValue` (balances API, hoặc dòng "Trứng vàng" trong output
`compute_active_nav.py --account <X>`). `egg_value` đủ bù phần thiếu → đổi cách viết lý do: "hôm
nay thiếu `availableCash` (Xtr) NHƯNG egg còn Ytr — nếu muốn mua, cần rút egg đêm nay/sáng mai
trước phiên" — đây là một QUYẾT ĐỊNH VỐN cần user xác nhận (có rút không), không phải một sự thật
"tài khoản không đủ tiền". Đừng tự ý đề xuất rút egg thay user; chỉ nêu rõ lựa chọn đang có.
Ca thật đã gây hiểu lầm: plan SpaceX/ZaloPay 2026-08-20 ghi "cash tức thời ~0" cho VPI trong khi
egg SpaceX ~100,2tr / ZaloPay ~38,8tr — đúng về mặt `availableCash` hôm đó nhưng đọc dễ hiểu lầm là
"tài khoản thiếu vốn", trong khi lý do THẬT user không mua VPI lần này là tín hiệu/hiệu suất BAL
gần đây, không phải thiếu tiền (xem `kb/current_ops.md`).

## "FLOOR_FAIL" — TRÍCH lăng kính ngành bằng script, không tự đọc CSV → `context_planning_ext.md`
KHÔNG phải gate cứng LAG. Chạy `python3 mike/bin/sector_valuation_lens.py --floor-fail-only --json`,
đừng tự diễn giải cột DD. Chi tiết đầy đủ → `context_planning_ext.md` § "FLOOR_FAIL".

## WATCH — luận điểm PEAD ngành cao su, ngưỡng RSS3 2,26 USD/kg → `context_planning_ext.md`
Ghi chú theo dõi (KHÔNG phải gate cứng): RSS3 thủng 2,26 → đánh giá lại nhóm GVR/PHR/DPR/DRI/TRC/HRC
trước khi cấp thêm vốn LAG. Chi tiết đầy đủ (nguồn dữ liệu, gốc con số, bối cảnh) →
`context_planning_ext.md` § "WATCH".
