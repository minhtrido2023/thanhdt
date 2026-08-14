# Reconcile P1 (trần động) ↔ quy trình lập plan TV1 của DollarBill

**Job** `Taylor_20260812_161457` · **ngày** 2026-08-12 · nối tiếp `IMPLEMENTATION.md` §7 mục 3
(user đã chốt `max_no_chase_ceiling = 25.000đ`, rào cản chính sách cuối của P1 → đóng).

## 1. Vấn đề: cơ chế đã có, nhưng chương trình đang chạy KHÔNG đi qua nó

| | Chương trình GỐC (07-24) | Chương trình HIỆN TẠI (từ 08-10) |
|---|---|---|
| Mục tiêu | 400cp cố định | **5% active_nav/mã**, CẢ 2 account |
| State file | `state_TV1_SpaceX.json` (`status=completed` từ 07-29) | **KHÔNG CÓ** (ZaloPay chưa từng có) |
| Ai sinh lệnh | injector 20:30 | **DollarBill gõ tay mỗi ngày** |
| Trần no-chase | state (20.000đ, đúng ở thời điểm duyệt) | **hardcode 20.000đ trong plan JSON** |

`load_active_states()` chỉ đọc state `status="active"` ⇒ file completed vô hình ⇒ injector no-op
⇒ toàn bộ P1 (trần động) không chạm được TV1 dù code đã LIVE từ `ec0120c`.

**Giá phải trả, đo được:** trần gõ tay 20.000đ trong khi thị trường 20.200–20.300đ hai phiên liền
⇒ SpaceX khớp **100/2.000cp** (08-11), ZaloPay **0/1.300cp**. Vị thế thật: SpaceX 500cp = **1,04%
NAV** (không phải 4,90% như plan tưởng), ZaloPay **0cp**. Đây đúng là kịch bản mà P1 sinh ra để
chặn: *"trần cố định là một SỐ chốt tại ngày duyệt; nó đúng cho tới khi giá đi khỏi vùng đó rồi
IM LẶNG biến chương trình gom thành không bao giờ khớp"*.

## 2. Thiết kế: target là TỶ TRỌNG, không phải số cổ phiếu

`target_qty` cố định sai về bản chất khi mục tiêu là "5% NAV": active_nav đổi mỗi ngày. Thêm
`target_pct_active_nav` — **field riêng, cưỡng chế ở một chỗ** (`resolve_target_qty`, engine
thuần), theo đúng §24: KHÔNG bẻ cong `target_qty` bằng cách ghi đè một con số mỗi sáng.

```
target_qty(phiên) = floor_to_lot( target_pct × active_nav ÷ giá_phiên_hoàn_tất_gần_nhất , lot )
```

**Ba lựa chọn thiết kế + lý do:**

1. **Mẫu số = GIÁ THỊ TRƯỜNG, không phải trần no-chase.** "5% NAV" là mệnh đề về giá trị thị
   trường ⇒ đo tại giá thị trường. Neo mẫu vào trần sẽ làm QUY MÔ mục tiêu nhúc nhích theo một
   núm CHÍNH SÁCH — đúng lỗi §24. Bờ trên của sai lệch: khớp toàn bộ ở đúng trần động ⇒ vượt mục
   tiêu ≤ τ (3%) của phần mua ≈ **≤0,15% NAV**; tiền thật vẫn bị chặn bởi gate P0 + cash-gate.
2. **Đủ tỷ trọng ⇒ `skip`, KHÔNG `completed`.** Chương trình duy trì tỷ trọng mà tự đóng khi đủ
   hàng thì hôm sau NAV tăng/giá giảm là tụt dưới mục tiêu mà **không còn state active nào để
   phát hiện** — đúng cái bẫy vừa xảy ra. Công tắc dừng duy nhất là `hard_expiry` (catalyst
   phi-giá). Chế độ `target_qty` cố định **giữ nguyên** hành vi `completed` cũ (ca hồi quy G1/G2).
3. **Deadband `topup_min_gap_pct_active_nav = 0,005`.** Mã hoá chỉ đạo user *"không rải thêm chỉ
   vì lệch do lot-size, chỉ rải thêm nếu rơi RÕ RỆT dưới 5%"* — §22: luật suy dẫn thuần từ dữ
   liệu sẵn có thì phải là CODE, không phải văn xuôi để mỗi lượt LLM diễn giải một kiểu.

### ⚠️ Tính chất PHẢI công bố (không phải bug — là chính sách)

Đây là mục tiêu **duy trì tỷ trọng**, KHÔNG phải hạn mức chi phí tích luỹ. Giá giảm ⇒ số cp mục
tiêu TĂNG ⇒ mua thêm để giữ 5% ⇒ **tổng tiền đã chi có thể vượt 5% NAV** (bình quân giá xuống).
Đây đúng là việc DollarBill đã làm tay từ 08-11 (size theo GAP tới 5% mỗi ngày) nên **không phải
hành vi mới** — nhưng nó nay chạy tự động mỗi phiên, và TV1 `no_price_stop_loss: true`. Nếu user
muốn một trần chi phí tích luỹ thì đó là **quyết định chính sách riêng**, chưa có trong cơ chế này.

## 3. Nguồn active_nav + cổng tươi (§14)

`data/execution_logs/active_nav_<account>.json` (do `compute_active_nav.py` ghi, cơ sở tiền
`totalCash − totalDebt` §25, đã fail-closed sẵn). Chọn nó thay vì tự tính lại vì nó chạy **ngay
trong chuỗi lập plan ~19:0x** ⇒ injector 20:30 dùng ĐÚNG cơ sở NAV mà phần còn lại của plan hôm
đó đã dùng. Cổng tươi đọc `computed_at` **trong nội dung** (mtime tươi ≠ nội dung tươi — bẫy thật
`lag_edge_health` 07-12) và đòi **đúng ngày hôm nay ICT**; cũ hơn ⇒ **không chèn lệnh**, và lý do
được ghi thẳng vào `plan["discretionary_inject_notes"]` để người duyệt 21:00 đọc được — vì từ nay
injector là chủ sở hữu duy nhất, một lần fail-safe im lặng = lệnh biến mất không ai thấy.

## 4. Kết quả dry-run trên ĐƯỜNG THẬT (2026-08-12, plan bản sao trong /tmp)

anchor = 5 phiên đã đóng `[19.500, 19.700, 19.800, 20.200, 20.300]` → mean **19.900** → trần động
`floor(19.900×1,03)` = **20.497đ** (chưa chạm trần tuyệt đối 25.000), resting kéo theo **20.394đ**.

| | active_nav | target | đang giữ | lệnh | giá | chi phí | sức mua |
|---|---:|---:|---:|---:|---:|---:|---:|
| SpaceX | 974.337.205 | 2.300cp | 500 | **1.800cp** | ≤20.394 | 36.709.200 | 459.058.903 (gói 1122) |
| ZaloPay | 516.017.365 | 1.200cp | 0 | **1.200cp** | ≤20.394 | 24.472.800 | 63.264.900 (gói 1258) |

Kiểm tay: `0,05 × 974.337.205 = 48.716.860 ÷ 20.300 = 2.399,8 → 2.300` (floor lô) ✓;
`0,05 × 516.017.365 = 25.800.868 ÷ 20.300 = 1.271,0 → 1.200` ✓. Gói vay resolve theo MÃ ra 1122
cho UPCOM ✓ (bug TV1 07-28 / DRI 08-07 không tái diễn).

## 5. Selfcheck

`discretionary_target_pct_selfcheck.py` — **75/75 PASS** (chạy lại lượt 2 SAU khi vá bug 6b), và **75/75 y hệt** dưới `env -u TZ`,
`TZ=America/New_York`, `TZ=UTC` (§16). Hồi quy: `discretionary_accumulation_selfcheck.py` 33/33,
`dynamic_no_chase_ceiling_selfcheck.py` PASS, `cash_only_loan_package_selfcheck.py` PASS,
`discretionary_participation_cap_selfcheck.py` PASS (bản đồ `selfcheck_scope_map.sh` cho
`trading_bot/discretionary_accumulation.py` = đúng 4 file này + file mới).

Điểm đáng chú ý trong bộ test:
- **D2 ca chứng minh ngược**: bỏ deadband ⇒ lệnh 100cp THẬT SỰ xuất hiện — không có ca này thì
  "D1 chặn được" có thể chỉ là một fail-safe khác đang chặn hộ.
- **A6**: mục tiêu < 1 lô trả `None` chứ KHÔNG trả 0 — trả 0 sẽ bị tầng trên đọc là "đã gom đủ"
  và đóng chương trình.
- **F2/F3**: active_nav cũ / thiếu file ⇒ 0 lệnh + note trong plan; không có đường fail-OPEN nào.

## 6. Bug phát sinh trong lúc làm (đã vá tại chỗ)

**(a) `active_nav = inf`** làm `int(math.floor(inf))` ném `OverflowError` **giữa vòng lặp
injector** ⇒ một state rác giết luôn việc chèn lệnh của mọi state khác cùng account, thay vì
fail-safe. Vá: `_pos_num` loại inf/nan (`math.isfinite`). Do chính selfcheck mới bắt được.

**(b) `load_active_states()` đổi sang trả TUPLE mà caller chưa cập nhật** — lượt làm đầu bị cắt
giữa chừng đúng ở đoạn này, để lại `states = load_active_states(account)` (không unpack) ăn khớp
với một hàm nay trả `(out, skipped)`. Hậu quả **KHÔNG phải một lỗi rìa**: `if not states` luôn
sai (tuple 2 phần tử luôn truthy) rồi `for _, s in states` ném `ValueError: not enough values to
unpack` ⇒ **injector chết ngay lối vào, mọi account, mọi state** — tức toàn bộ cơ chế này sẽ im
lặng không sinh lệnh nào ở lần chạy 20:30 đầu tiên.

Đã vá ở lượt 2 và **chứng minh ngược**: dựng lại đúng bản trước khi vá (`/tmp/inj_broken.py`)
rồi chạy lại selfcheck ⇒ nổ đúng `ValueError` ở dòng 343; khôi phục ⇒ 75/75 xanh (md5 khớp
`be8b943c…`). Đây là ca ủng hộ §19 `verify-before-done`: bản thân dry-run trước đó "đã chạy đúng"
chỉ vì nó chạy **trước** khi hàm đổi chữ ký — báo cáo cũ không sai lúc viết, nhưng đã hết hiệu
lực trước khi việc kết thúc.

Nhân tiện hoàn tất phần dùng `skipped` mà chữ ký mới hứa: state bị bỏ qua (completed/hỏng/sai
account) nay được ghi vào `plan["discretionary_inject_notes"]` (dedup theo `state_file`+lý do).
Chính xác đó là thứ đã vắng mặt suốt 07-29→08-12: state TV1 nằm im ở `completed`, injector bỏ qua
ĐÚNG LUẬT và im lặng, không artifact nào người duyệt plan đọc được nhắc rằng có một chương trình
gom đang không sinh lệnh.

## 6b. Vòng quant-skeptic 1 — CONFIRMED (medium) + hai chỗ đã sửa sau khi bị bác

Verdict CONFIRMED, `mike/logs/verify_20260812_165551_908751.log`. Reviewer tái lập ĐỘC LẬP từng
con số (trần 20.497/resting 20.394, target 2.300/1.200cp, target_value 48.716.860/25.800.868), và
tìm được **hai bằng chứng tôi chưa trích**: log injector có **12 lần liên tiếp** `status=completed
→ no-op` (08-05→08-12) — biến chẩn đoán từ suy luận thành SỰ KIỆN LOG; và
`exec_SpaceX_2026-08-12_report.md` cho thấy **phiên thứ BA** trắng tay (1.900 đặt / 0 khớp), tôi
mới nêu hai phiên. Hai chỗ bị bác đúng, đã sửa trong lượt này:

1. **Trụ "trần ngân sách" được rao mà KHÔNG có test nào trong toàn repo** (grep
   `SESSION_BUDGET_CAP_SLACK` chỉ ra đúng file cài đặt), trong khi báo cáo lại tự đặt chuẩn
   "mọi claim chặn được phải có ca chứng minh ngược" cho deadband. Đúng — và đây là lớp DUY NHẤT
   đứng giữa feed sai đơn vị và lệnh phình 100×. Đã thêm khối **[I] 9 ca** (+ **[J] 3 ca** hồi quy
   chữ ký cho bug 6b): **93/93 PASS**, cả 4 điều kiện TZ.
2. **Hai magnitude 8,40% / 14,78% chỉ sống trong comment mã nguồn**, không truy được về ca nào.
   Đúng — tôi không tái lập được chúng, nên **không giữ lại con số mồ côi**: comment nay trích số
   ĐO LẠI từ ca chạy được — rơi nhanh **7,39% NAV** (I1) → 5,49% khi có trần (I2); sai đơn vị
   **51,26% NAV** (I6) → 5,31% (I7); và **I8** chứng minh mặt kia của bờ: ở lệnh hợp lệ thật
   (1.800cp) trần này KHÔNG bind — nếu nó bind ở ca thật thì nó là núm sizing lén, không phải lưới.

## 6c. Vòng quant-skeptic 2 — CONFIRMED, và một ĐÍNH CHÍNH bắt buộc tôi phải nhận

Verdict CONFIRMED (`mike/logs/verify_20260812_171207_919655.log`); reviewer tái lập độc lập 93/93
× 4 điều kiện TZ, hồi quy 4/4, và khớp từng số (I2 5,49% · I7 5,31% · I8 1.800cp/36.709.200đ ·
ZaloPay 1.200cp/24.472.800đ/4,74%). Nhưng **một tuyên bố của tôi bị bác đúng**:

- ❌ **"Trần ngân sách là lớp DUY NHẤT đứng giữa feed sai đơn vị và lệnh phình 100×" — SAI thứ tự
  lớp.** `cap_vnd = per_session_cap_pct_adv × adv_ref_vnd` (72,0tr) là bờ tính bằng **TIỀN**, nên
  nó **miễn nhiễm với lỗi đơn vị GIÁ**. Con số 51,26% chỉ đạt được vì harness thổi `adv_ref` lên
  5 tỷ (~7× thật) để **cô lập** lớp — đúng cho việc đo riêng, nhưng tôi đã bê nó vào comment
  production mà không mang theo điều kiện đó, khiến bán kính vụ nổ đọc ra **nặng gấp ~7 lần thực
  tế**. Đã sửa: thêm cặp ca ở `adv_ref` THẬT — **I10/I11** (bờ NGOÀI một mình giữ ở **7,35% NAV**,
  và neo bất biến `worst_cost ≤ cap_vnd` để ai nới `per_session_cap_pct_adv`/`adv_ref_vnd` sau này
  không lặng lẽ gỡ mất lưới còn lại) và **I12** (bờ TRONG siết tiếp **7,35% → 5,31%**). Comment
  trong `discretionary_accumulation.py` nay nói rõ **hai bờ và thứ tự của chúng**. Số reviewer
  đưa ra tôi tái lập khớp tuyệt đối. **96/96 PASS.**
- ✏️ **"12 lần liên tiếp `status=completed`" — thiếu chính xác, đã sửa.** Trong log có **9** dòng
  `status=completed` (SpaceX) và 22 dòng no-op; phần ZaloPay là **no-op vì CHƯA CÓ state**, không
  phải `completed`. Chẩn đoán không đổi, nhưng hai cách hỏng khác nhau thì không được gộp số.
- ✅ **Reviewer sai một điểm, tôi giữ nguyên:** `data/execution_logs/exec_SpaceX_2026-08-12_report.md`
  **CÓ tồn tại** (351 byte, 14:45 ngày 08-12; dòng `BUY-TV1-DISC-01 | TV1 | buy | 1,900 | 0 | 0%`).
  Reviewer báo không có và trích journal thay thế — kết luận trùng nhau nên không đổi gì về nội
  dung, nhưng trích dẫn của tôi đúng và giữ nguyên.
3. **Vi phạm §23 quy ước 1** (20 assertion đè lên state file SỐNG): đã tách — file thật chỉ kiểm
   **bất biến** (validate, account/ticker khớp tên file, trần ≤ 25.000, anchor 99.000 vẫn bị kẹp),
   còn **giá trị** cấu hình đã duyệt kiểm trên fixture đóng băng
   `data/fixtures/state_TV1_{acct}_pct_20260812.json`. Bản cũ sẽ đỏ đúng vào ngày `halted=true`
   HỢP LỆ — tức phạt đúng lúc cơ chế dừng hoạt động đúng thiết kế.

## 7. Việc CÒN MỞ (không tự làm trong lượt này)

1. **Promote `mike/kb/context_planning_mini.md.proposed`** (§13 — Mike duyệt rồi `mv` + commit).
   ⚠️ **ĐÍNH CHÍNH quan trọng (quant-skeptic bắt, tôi nói sai ở bản trước):** lý lẽ "chưa promote
   thì cơ chế vô hiệu vì injector thấy trùng lệnh" **CHỈ ĐÚNG CHO SpaceX** — plan SpaceX có sẵn
   order `book=DISCRETIONARY_SPECIAL` nên `already_injected()` khớp tuyệt đối. **ZaloPay KHÔNG có
   lá chắn đó** (plan 08-13 có 0 lệnh). Cron `20:30 ICT T2-T6` vẫn sống, và cả hai state nay
   `status=active` ⇒ **lần chạy 20:30 ngày 2026-08-13 sẽ chèn ~1.200cp (~24,47tr, ~4,74%
   active_nav) vào plan ZaloPay 08-14** — **CÓ ĐIỀU KIỆN**, xem mục 1b ngay dưới — dù KB chưa
   promote.
   - Đó **đúng là kết cục dispatch yêu cầu** ("lần kế tiếp DollarBill lập plan sẽ tự đọc đúng
     nguồn"), cổng duyệt người lúc 21:00 còn nguyên, và cash-gate vẫn trừ phần V2.4 đã dự chi —
     nên đây là **thiếu sót CÔNG BỐ, không phải tiền tự đi**. Nhưng nó rơi đúng vào account đang
     giữ **0cp**, nên phải nói ra.
   - **Hệ quả BẤT ĐỐI XỨNG cần Mike quyết TRƯỚC 20:30 hôm nay:** chưa promote ⇒ DollarBill vẫn gõ
     tay TV1 cho SpaceX với trần cứng 20.000đ ⇒ **SpaceX tiếp tục không khớp** (đã 3 phiên) trong
     khi ZaloPay chạy trần động đúng. Cùng một luận điểm, hai account thực thi lệch nhau. Khuyến
     nghị: **promote KB** (gỡ bất đối xứng theo chiều đúng) thay vì hạ `status` ZaloPay — hạ
     ZaloPay chỉ kéo dài đúng cái hỏng mà job này sinh ra để sửa. Đã ghi `question` lên bus.
1b. **`compute_active_nav.py` KHÔNG CÓ CRON** — phát hiện của quant-skeptic vòng 2, tôi đã tự
   kiểm (`crontab -l | grep -c compute_active_nav` = **0**). Đây là §14 đúng nghĩa: cổng tươi
   `computed_at == hôm nay` của injector treo vào một producer **chạy tay/ad-hoc trong chuỗi lập
   plan ~19:0x**, không ai giám sát.
   - **Hệ quả TỨC THÌ, làm dịu mục 1**: ngay lúc này cả hai file đọc `computed_at=2026-08-12`
     trong khi hôm nay đã là **2026-08-13** ⇒ nếu không ai chạy lại producer trong chuỗi lập plan
     chiều nay thì **20:30 hôm nay injector FAIL-CLOSED (không chèn gì)**, chỉ ghi note vào plan.
     Tức câu "SẼ chèn" phải đọc là **"sẽ chèn NẾU chuỗi lập plan chạy producer như thường lệ"** —
     hỏng an toàn theo chiều tốt, nhưng đó là may mắn của thiết kế fail-closed chứ không phải một
     bảo đảm ai đó đã cân nhắc.
   - **Việc thật cần làm** (chưa làm, ngoài phạm vi dispatch này): hoặc cron hoá producer, hoặc
     cho injector **ESCALATE** (không chỉ ghi note) khi fail-closed **hai ngày liên tiếp** — vì
     hiện tại một chương trình gom có thể im lặng đứng hình nhiều phiên mà chỉ để lại note trong
     plan, đúng lớp lỗi mà job này sinh ra để chấm dứt.
2. **Bug đơn vị turnover** (riêng, chưa sửa): `latest_trade.totalVolumeTraded` ở đơn vị **10 CP**
   — đo 2026-08-12: TV1 trả 3.950 khi KL thật 39.500; DRI 101.160 vs 1.011.600; đối chiếu
   `grossTradeAmount` 0,8044 (tỷ) khớp `39.500 × 20.300`. ⇒ `prev_session_market()` khai thiếu
   turnover **10×** ⇒ cờ `opportunistic` (boost ×2 khi người bán xuất hiện) **không bao giờ kích
   hoạt**. An toàn một chiều (mua ÍT hơn) và với TV1 trần cap vốn không bind nên **không đổi lệnh
   nào hôm nay** — nhưng doctrine "gom nhiều khi người bán xuất hiện" đang là code chết. Sửa cần
   tự xác minh đơn vị trên ≥2 mã + quant-skeptic riêng.
3. **DRI chưa có state file** — vẫn do DollarBill viết tay, vẫn hardcode được trần. Cùng lớp vấn
   đề, chưa làm vì ngoài phạm vi dispatch (và DRI đã khớp đủ 5%, không gấp).
4. **Trần %ADV tính RIÊNG từng account** — 2 leg cùng mua TV1 trong 1 phiên thì %ADV thật là tổng
   hai bên. Ở size hiện tại không bind; nâng size thì phải chia trần như CAPIT đang làm.
5. **`hard_no_chase_ceiling_selfcheck.py` E4 FAIL** (journal `HARD_CEILING_BLOCK`) — **có từ
   trước, không do lượt này**: file đó không import module tôi sửa; E1–E3 (hành vi an toàn thật)
   vẫn PASS, chỉ assertion về dấu vết journal đỏ. Của chủ file P1/§24.
