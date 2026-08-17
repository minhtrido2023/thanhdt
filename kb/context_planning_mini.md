# Mike fleet — context planning (DollarBill only)
> Phần CHUYÊN BIỆT cho việc lập plan T+1 — không lặp lại safety core (đã import riêng ở
> CLAUDE.md), không có chi tiết phương pháp backtest/DSR/PBO (việc của Taylor, chỉ cần
> KẾT QUẢ để lập plan, không cần cách tính ra). Cần domain khác ngoài đây (backtest chi
> tiết/pháp lý/thực thi)? Đọc `kb/context_pack.md` qua Read tool nếu tự tin đúng chỗ, hoặc
> escalate Mike — đừng đoán.

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

## DRI + TV1 discretionary — target 5% NAV/mã MỖI account, khung giá rải bậc (chốt 2026-08-10/11)
User chốt 2026-08-10 tối: nâng size DRI + TV1 (PECC1) từ 1,5% → **5% NAV/mã, cho CẢ 2 account**
(SpaceX + ZaloPay), discretionary ngoài book V2.4. Đã thực thi trong plan 2026-08-11 (play_type
`DISCRETIONARY_ADD`): SpaceX TV1 400→2400cp (≈47,68tr/974,28tr NAV ≈4,90%), SpaceX DRI 0→3700cp
(≈48,84tr ≈5,01%); ZaloPay TV1 0→1300cp (≈25,87tr/513,89tr active_nav ≈5,03%), ZaloPay DRI
0→1900cp (≈25,08tr ≈4,88%) — lệch ~0,1pp là do lot-size tròn 100cp, KHÔNG cần rải thêm để chỉnh
cho khớp tuyệt đối 5,00%.

⚠️ **ĐÍNH CHÍNH 2026-08-12 — "đã đạt 5%" chỉ ĐÚNG với DRI.** Câu "coi như ĐÃ ĐẠT mục tiêu 5%"
trước đây đọc số lượng ĐẶT trong plan, không phải số KHỚP (§27 coding_guidelines). Đối soát thật:
**DRI khớp đủ cả 2 account**, nhưng **TV1 gần như không khớp gì** — SpaceX 500cp (1,04% NAV, chứ
không phải 2.400cp), ZaloPay **0cp**. Nguyên nhân: trần `hard_no_chase_ceiling_vnd=20.000đ` gõ tay
trong khi thị trường 20.200–20.300 suốt 2 phiên. Đã xử lý bằng trần động + state file (mục TV1 ở
trên); **DRI vẫn do bạn viết tay và vẫn coi là đã đạt**. Kiểm tra tỷ trọng bằng vị thế THẬT
(`compute_active_nav.py` / `positions` trong `dnse_raw_<date>.jsonl`), không bao giờ bằng qty
trong plan; dùng active_nav đúng account (ZaloPay có DGC excluded ⇒ active_nav 516tr ≠ NAV 954tr).
Chỉ rải thêm nếu vị thế rơi RÕ RỆT dưới 5%, không rải thêm chỉ vì lệch do lot-size.

**Khung giá rải bậc (user cung cấp 2026-08-11, discretionary reference — chưa qua DSR/PBO, N=1
mã, không phải khuyến nghị cứng):**

| Mã | Vùng MUA (rải bậc) | Vùng BÁN/chốt lời (rải bậc) | Ghi chú |
|---|---|---|---|
| **DRI** (UPCOM, giá ref 13.200đ 2026-08-10) | T1 12.800–13.200 · T2 (nếu về hỗ trợ) 11.900–12.300 · ngừng mua nếu thủng <11.900 | T1 (kỹ thuật) 14.000–14.200 · T2 (target chính, PE reversion) 15.500–17.000 · T3 (stretch, cần EPS fwd FY2026 xác nhận 4.000-4.300đ) 17.500–18.000 | PE_MA5Y (9,44x) KHÔNG dùng làm target (méo bởi chu kỳ cao su cũ); thanh khoản UPCOM mỏng (200k-1,6M cp/phiên) → rải lệnh |
| **TV1/PECC1** (giá ref ~19.900-20.200đ 2026-08-10) | T1 (40%) 19.800–20.200 · T2 (35%) 18.300–19.400 · T3 (25%, dự phòng, chỉ mua nếu không có tin xấu mới) 16.500–17.500 | T1 (30%) 24.500–26.000 · T2 (40%) 29.000–32.000 · T3 (30%) 35.000–37.700 (KHÔNG target lại đỉnh đầu cơ 39.400 — spike bất thường) | PE_MA5Y (11,54x) KHÔNG dùng làm neo (méo bởi khủng hoảng LN 2019-2021); thanh khoản ~0,634 tỷ/ngày → chia lệnh nhỏ |

**Dùng khi nào**: (a) **cho DRI** — nếu vị thế chưa đạt 5% NAV/mã thì rải mua theo tranche T1
trước, chỉ xuống T2/T3 nếu giá thật sự điều chỉnh về vùng đó (với **TV1 khung giá này chỉ còn là
THAM CHIẾU ĐỌC**: giá đặt do trần động của injector quyết, bạn không viết lệnh TV1);
(b) khi giá chạm vùng BÁN/chốt lời → đưa vào cân nhắc trim (discretionary,
không tự động, cần user duyệt riêng như mọi lệnh bán ngoài V2.4); (c) không tự nội suy khung giá
khác — hết giá trị tham chiếu (giá thị trường vượt xa dải trên/dưới) thì hỏi lại user, đừng tự chế.

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

⚠️ **Cùng lỗi tái diễn ở field `book_breakdown_current` (phát hiện 2026-08-17,
`plan_SpaceX_2026-08-17.json` viết 08-14)**: field này KHÔNG có script nào sinh ra — DollarBill tự
gõ tay mỗi lần lập plan, và đã lấy PARK từ `compute_park_trim.py` (chỉ tính rổ custom30V) rồi coi
mọi mã tồn dư không khớp làm "phần dư ngoài custom30V" thay vì tra đúng book của nó → SCL 1500cp
(book LAG thật, `play_type=LAG_HI`, mua 2026-08-10 theo journal) bị ghi thành `LAG: {mv_vnd: 0,
"0 vị thế LAG"}`. **Nguồn ĐÚNG để viết `book_breakdown_current` mỗi lần lập plan**:
```bash
python3 mike/bin/park_holdings.py --account <SpaceX|ZaloPay> --json
```
Đọc field `by_book` (đã gộp bootstrap snapshot + toàn bộ fill journal sau ngày bootstrap, mới hơn
và đầy đủ hơn đọc thẳng file bootstrap tĩnh) — dùng đúng `mv_vnd`/`qty` theo từng book nó trả về,
KHÔNG tự suy "mã không nằm trong rổ compute_park_trim.py thì là phần dư ngoài PARK". Field này
chỉ ảnh hưởng báo cáo (cosmetic), không đụng `orders[]`/executor.

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

## "FLOOR_FAIL" KHÔNG phải gate cứng cho LAG — TRÍCH lăng kính ngành có sẵn, đừng đọc dở CSV (thêm 2026-08-04, đính chính + chuyển code cùng ngày)
`FLOOR_FAIL` là chữ DollarBill tự viết để mô tả 1 mã trượt "golden floor" (ROE_Min3Y≥0 ∧ CF_OA_3Y>0)
— KHÔNG phải gate cứng cho LAG (LAG chỉ gate cứng ở 8L rating≤3, `lag_filter_low_rating()`).

**Đính chính root cause** (bản đầu 2026-08-04 sai): lăng kính ngành (Gordon P/B ngân hàng, P/B+ROE
chứng khoán...) **không hề thiếu** — `alt_valuation_lens.py` có từ 07-20, và `golive_recommend_v23.
py` đã **in sẵn** kết luận CHEAP/RICH vào đúng ô CSV mà cả 2 phiên cùng đọc. Sự cố 07-28
(`plan_ZaloPay_2026-07-28.json` skip EVF/PSI/VCI trong khi SpaceX mua) không phải "1 bên biết áp
lăng kính, bên kia không" — mà là **ZaloPay đọc dở ô dữ liệu**, không đọc tới phần kết luận đã có
sẵn ở cuối. Xem `mike/agents/Taylor/research/deterministic_plan_decisions_20260804.md`.

**Quy trình bắt buộc**: đừng tự đọc/diễn giải cột DD, TRÍCH bằng script (51/51 selfcheck PASS):
```bash
python3 mike/bin/sector_valuation_lens.py --floor-fail-only --json
```
Output trả về đúng 1 trong: `CHEAP` (mua bình thường), `RICH` (skip, cần `dcf_override_reason` nếu
muốn override), `SKIP_CO_CAN_CU` (skip có bằng chứng, vd ngoài universe_pit), `CAN_NGUOI_QUYET`
(không đủ dữ liệu áp lăng kính, escalate). Áp dụng NHẤT QUÁN cho CẢ 2 account — cùng CSV phải cho
ra cùng kết luận, khác nhau là dấu hiệu 1 bên dùng sai tham số.

## WATCH — luận điểm PEAD ngành cao su (GVR/PHR/DPR/DRI/TRC/HRC), ngưỡng RSS3 (thêm 2026-08-06, user duyệt)
Đây là **ghi chú theo dõi, KHÔNG phải gate cứng** — không có trong `trading_rules.json`, không chặn
lệnh nào một cách cơ học. Mục đích: khi ngưỡng dưới đây chạm, phải DỪNG LẠI đánh giá lại luận điểm
ngành trước khi cấp thêm vốn LAG cho nhóm này, thay vì cứ cấp vốn theo tín hiệu PEAD như thường lệ.

**Ngưỡng kích hoạt xét lại: RSS3 thủng 2,26 USD/kg.**
- Chạm ngưỡng → đánh giá lại luận điểm PEAD ngành cao su cho CẢ nhóm **GVR / PHR / DPR / DRI / TRC /
  HRC** TRƯỚC khi đưa thêm bất kỳ mã nào trong nhóm vào `orders[]` LAG (mã đang giữ thì đánh giá
  trước khi top-up). Không tự động loại — chỉ bắt buộc xét lại có chủ đích và ghi rõ kết luận vào
  `notes` của plan.
- **Nguồn đối chiếu ngưỡng: `data/rubber_monthly.csv` (World Bank monthly), đọc TAY.** KHÔNG dùng
  lại nhãn "phá đáy 52 tuần" của `rubber_weekly.py` — nhãn đó đã được xác nhận là BUG đo lường
  (2026-08-06, Taylor `Taylor_20260806_081258` + DollarBill `DollarBill_20260806_081312` tìm ra độc
  lập): band 52 tuần chỉ tính trên dòng `src != "wb_seed"` (bắt đầu 2026-06-19) nên cửa sổ thật chỉ
  ~6,6 tuần, mọi giá dưới ~2,61 đều bị gắn nhãn "đáy 52 tuần mới" sai. Chừng nào `rubber_weekly.py`
  chưa sửa, mọi nhãn "52 tuần" từ feed đó là **chưa đáng tin**.
- **Gốc con số 2,26 (kiểm chứng 2026-08-06, để lần sau khỏi suy lại):** 2,26 = giá tháng **2026-02**,
  cũng là **min của TOÀN BỘ `data/rubber_weekly.csv`** (file chỉ bắt đầu 2026-02-15 → đây là đáy của
  chuỗi weekly hiện có, không phải đáy 12 tháng). **Đáy 12 tháng THẬT của chuỗi monthly WB là 2,00**
  (2025-10; 2025-11 = 2,03, 2025-12 = 2,06). Ngưỡng chốt là **2,26** (cao hơn 2,00) → cố ý kích hoạt
  SỚM và thận trọng hơn đáy thật, không phải nhầm lẫn. Tham chiếu lúc chốt: spot 2026-08-04 = **2,596**
  (−9,2% từ đỉnh 2026-06 là 2,86; vẫn +29,8% trên 2,00 và +14,9% trên 2,26).
- Bằng chứng đầy đủ: `mike/agents/Taylor/research/rubber_alert_20260806.md`.

**Nhắc lại cơ chế ĐÃ CÓ, không cần cơ chế mới:** nếu regime chuyển **BEAR** thì allocator tự đặt
`w_LAG=0` — toàn bộ vị thế LAG nhóm này bị bán theo cơ chế sẵn có (xem mục "LAG entry mới trong giai
đoạn thị trường dễ vỡ"). Ghi chú WATCH này CHỈ bổ sung cho trường hợp **regime KHÔNG đổi (vẫn
NEUTRAL/BULL) nhưng giá hàng hoá đảo chiều thật** — chỗ mà allocator không nhìn thấy gì cả.

**Bối cảnh lúc lập note (2026-08-06):** 0 vị thế cao su ở cả 2 account; DRI giữ nguyên trong hàng đợi
LAG bình thường (DCF CHEAP MoS +36,3%, PE 4,30, qua 8L gate), KHÔNG hạ ưu tiên — vì lý do từng được
viện dẫn để hạ ("phá đáy 52 tuần") là artifact. GVR/PHR đã bị gate DCF RICH tự chặn.
