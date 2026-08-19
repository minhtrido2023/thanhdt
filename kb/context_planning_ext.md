# Mike fleet — context planning ext (DollarBill only) — đọc khi cần, KHÔNG auto-load

> Tách khỏi `context_planning_mini.md` 2026-08-19 (mandate OKF split khi file vượt 40KB — xem
> `MEMORY.md` "OKF split tự động khi file vượt 40KB"). Nội dung dưới đây ĐẦY ĐỦ, KHÔNG nén — chỉ
> chuyển vì tần suất cần thấp hơn (theo tình huống cụ thể, không phải mỗi lần lập plan).

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
`context_planning_mini.md`); **DRI vẫn do bạn viết tay và vẫn coi là đã đạt**. Kiểm tra tỷ trọng bằng vị thế THẬT
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
đoạn thị trường dễ vỡ" ở `context_planning_mini.md`). Ghi chú WATCH này CHỈ bổ sung cho trường hợp **regime KHÔNG đổi (vẫn
NEUTRAL/BULL) nhưng giá hàng hoá đảo chiều thật** — chỗ mà allocator không nhìn thấy gì cả.

**Bối cảnh lúc lập note (2026-08-06):** 0 vị thế cao su ở cả 2 account; DRI giữ nguyên trong hàng đợi
LAG bình thường (DCF CHEAP MoS +36,3%, PE 4,30, qua 8L gate), KHÔNG hạ ưu tiên — vì lý do từng được
viện dẫn để hạ ("phá đáy 52 tuần") là artifact. GVR/PHR đã bị gate DCF RICH tự chặn.
