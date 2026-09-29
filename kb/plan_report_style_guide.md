# Plan/report style guide — render layer cho báo cáo & plan-note

**Phạm vi (2 consumer, CÙNG 1 chuẩn, không phải 2 chuẩn riêng):**
(a) `bin/send_plan_report.sh` (report renderer gửi user duyệt hằng ngày — Discord/email);
(b) mọi script sinh `notes[]`/text hiển thị bên trong plan JSON mà (a) echo lại nguyên văn —
`bin/compute_park_trim.py`, `bin/merge_park_orders.py`, `bin/compute_jit_unpark.py`, và bất kỳ
script tương tự sau này. Nội dung do (b) tạo ra HIỂN THỊ TRONG (a) — không tách biệt được, nên
cùng 7 luật dưới áp dụng cho cả hai.

**Nguồn**: rút từ audit `agents/Taylor/research/plan_report_audit_20260928/report.md` +
quyết định user tối 2026-09-28→29 (duyệt hướng đề xuất §3 report đó, mockup Case A/B). Viết
kiểu `coding_guidelines.md` — LUẬT + cơ chế, không kể chuyện; chuyện/case cụ thể ở report gốc.

---

## 1. Không hardcode số/tham số có thể đổi ở nơi khác

Mọi con số MÔ TẢ một giá trị động (ngưỡng %, hệ số đòn bẩy, trần cấu hình...) phải ĐỌC từ biến/
config thật đang có sẵn cùng scope — không viết literal mô tả lại giá trị đó bằng lời.

- **Ca gốc (đã fix, merge `98a9d633`)**: `send_plan_report.sh` hardcode "trần PARK 80%" trong khi
  `target_park` đã đổi 0.80→0.30 ở config — sửa thành đọc `park_trim.get("target_park")`.
- **Ca cùng lớp, CHƯA fix lúc audit** (`send_plan_report.sh:481-483`): `"1,3× vốn"` viết literal
  trong khi khối này thuộc nhánh `preview_margin_day` KHÔNG có `orders` (granted rỗng) — đúng lúc
  đó `_pv['lever_f']` LUÔN LÀ `None` (`trading_bot/plan.py:1714` khởi tạo `None`, early-return
  dòng 1725 trước khi gán giá trị khác), nên `f"{_pv['lever_f']:g}×"` sẽ NÉM `TypeError` ngay
  trong `try/except` của khối này — except bắt lỗi sẽ THAY TOÀN BỘ cảnh báo bằng câu lỗi chung,
  tức xoá mất cảnh báo an toàn "sizing theo đòn bẩy nhưng chạy vốn tự có" mà audit trước (finding
  #3a) đã thêm. Sửa ĐÚNG (code thật đã làm): import `CAPIT_LEVER_APPROVED_F` từ `trading_bot.plan`
  (cùng hằng số `apply_capit_lever` dùng để neo, `plan.py:1504`) và render
  `f"{CAPIT_LEVER_APPROVED_F:g}×"` — hằng số cấu hình đòn bẩy được duyệt, không phụ thuộc nhánh
  nào của `preview_margin_day` đang chạy. Đúng hôm audit vì `CAPIT_LEVER_APPROVED_F = 1.3` trùng
  khớp ngẫu nhiên với literal cũ — đổi gói đòn bẩy (có tiền lệ đặt tên f=1.5) sẽ lập tức sai mà
  không ai phát hiện.
- **KHÔNG áp dụng** cho hằng số **tự sở hữu** bởi chính đoạn code đó (không có bản sao ở nơi khác
  để lệch theo) — vd `PRICE_TOLERANCE`, ngưỡng lệch CAPIT sizing nội bộ. Phân biệt: hỏi "giá trị
  này có đọc được từ 1 biến/config Python đã tồn tại trong cùng file/scope không?" — có thì phải
  đọc, không thì được viết literal (nhưng nên đặt tên hằng số ở đầu file, không rải rác).
- **Kiểm tra khi review**: mọi chuỗi f-string mô tả % / hệ số / trần trong renderer — grep xem có
  biến cùng tên/cùng giá trị đã tồn tại trong scope không trước khi chấp nhận literal.

## 2. Không lặp nguyên văn 1 câu N lần khi N lệnh cùng lý do

Khi N lệnh trong cùng report có CÙNG lý do (cùng target %, cùng ngày, cùng loại), viết **1 câu áp
dụng chung** thay vì lặp câu đó N lần theo từng lệnh.

- Ca thật: 19 lệnh PARK_TRIM ngày 2026-09-29, mỗi lệnh in nguyên văn `"↳ ℹ️ Lý do: tuân thủ trần
  PARK 30% (park-trim), KHÔNG liên quan tới việc tài trợ lệnh mua trong plan này."` → lặp 19 lần.
- Sửa: 1 dòng "Lý do (áp dụng CHUNG cho cả N lệnh): ..." đặt ngay dưới danh sách mã, không lặp
  theo từng dòng lệnh.
- **Ranh giới**: chỉ gộp khi lý do THẬT SỰ giống hệt cho cả nhóm. Lệnh có lý do khác nhóm (vd 1
  lệnh PARK_TRIM thuần trong lúc các lệnh khác FUNDED_BY_JIT) phải tách nhóm riêng, không gộp ép.

## 3. Không liệt kê CÙNG một danh sách mã 2 lần dưới 2 định dạng khác nhau trong 1 report

Nếu một tập mã đã xuất hiện trong `orders[]`, KHÔNG lặp lại đúng tập mã đó (dù format khác) ở một
khối riêng khác trong cùng report.

- Ca thật (plan 2026-08-07): 11/14 mã BÁN PARK liệt kê cả trong danh sách lệnh chính lẫn trong
  khối "L2/JIT tài trợ" riêng — cùng 1 lượng bán mô tả 2 lần.
- Sửa: gộp thành 1 khối theo VAI TRÒ (vd "mã tài trợ MUA" vs "mã trim thuần"), mỗi mã xuất hiện
  đúng 1 lần trong thân report; ai cần đối chiếu qty/giá riêng lẻ thì xem phụ lục (mục 5).

## 4. Nội dung compliance/provenance bắt buộc — GIỮ khi có bất thường, BỎ HẲN khi thuần xác nhận

**Sửa 2026-09-29 21:48 ICT** (user, lần phàn nàn thứ 2): "Không đưa những câu vô nghĩa không cần
thiết vào report cho xong trách nhiệm. Cái nào cần giải thích mới viết ra, không phải chép những
câu ngày này qua ngày khác." — chỉ đạo này SIẾT hơn bản 09-28→29 dưới đây: kể cả dạng rút gọn 1
dòng/icon cũng là "chép mỗi ngày" nếu ngày nào cũng in. Từ nay:
- Khối THUẦN XÁC NHẬN — không có gì để người duyệt quyết định khác đi (state khớp DT5G, giá đã
  xác minh ĐỦ 100% lệnh) → **BỎ HẲN, không giữ cả icon**. "Không thấy gì" = đã qua, không cần nói.
- Khối có bất thường thật (⚠️/🛑: state/price KHÔNG khớp hoặc CHƯA xác minh đủ, mismatch, overdue,
  vượt ngưỡng, BLOCKED_*, funding note "Tiền đâu ra" 💧, margin, Trứng vàng, CAPIT lệch >10%) →
  **GIỮ NGUYÊN, mở rộng đầy đủ** như cũ — đây vẫn là chỗ hiếm nhất, chính xác nhất.
- Logic verify bên dưới KHÔNG đổi — chỉ đổi NGƯỠNG hiển thị (từ "luôn in, chỉ đổi độ dài" sang
  "chỉ in khi lệch khỏi bình thường"). Ranh giới bắt buộc: verify PHẢI dựa trên **bất biến thật**
  (vd `verified_n < tổng`), KHÔNG được dùng sự hiện diện của emoji trong chuỗi văn bản làm proxy —
  arch-review 2026-09-29 bắt đúng lỗi này ở price-verify (ternary chỉ tách theo `if verified_n`,
  không có nhánh ⚠️ cho PARTIAL, nên `"⚠️" in text` bỏ sót ca 1/9 verified).
- Quiescent decision string (vd `NO_TRIM`/`SKIP_STATE` của L1, `NO_JIT_NEEDED`/`NO_TRIGGER` của
  L2) cũng được BỎ HẲN theo nguyên tắc trên — NHƯNG chỉ khi `notes[]` đi kèm không chứa cảnh báo
  thật (`⚠️` ở bất kỳ đâu trong text, không chỉ ký tự đầu) — bỏ theo DECISION không được nuốt luôn
  WARNING gắn kèm. Và KHÔNG được gộp một quiescent-thật với một "bế tắc thật" cùng nhóm chỉ vì tên
  gần giống — vd `NO_TRIM_STRUCTURE` (PARK vượt trần nhưng không mã nào trim được) là cùng bản
  chất với `BLOCKED_ALL_NAMES` (vẫn in đậm), KHÔNG phải ngày yên ổn.
- DCF/DD disclaimer §6b: văn bản phương pháp luận cố định, không đổi theo quyết định hôm nay →
  BỎ khỏi report hàng ngày, giữ nguyên trong module nguồn (`dcf_valuation.DCF_DISCLAIMER`,
  `due_diligence.DD_DISCLAIMER`) cho ai cần tra lại phương pháp — không phải nội dung compliance
  bắt buộc theo nghĩa "phải xuất hiện mỗi lần", vì bản thân giá trị DCF/DD từng dòng (đổi theo
  ticker/ngày) vẫn hiển thị đầy đủ, chỉ bỏ đoạn giải thích PHƯƠNG PHÁP.
- **KHÔNG đề xuất xoá** (danh sách chốt từ audit, đều tồn tại vì sự cố thật, LUÔN hiện khi có nội
  dung): funding note "Tiền đâu ra", cảnh báo BLOCKED_*, mismatch state/price, cảnh báo margin,
  cảnh báo Trứng vàng cần rút, cảnh báo Σ CAPIT lệch >10%.

## 5. Không đẩy nguyên khối dữ liệu kỹ thuật vào kênh duyệt chính

Dữ liệu ticker-by-ticker chi tiết (rổ mục tiêu 11-17+ mã với công thức target/lô, bảng giá/giá
trị từng mã) → **tóm tắt 1 dòng** trong kênh duyệt (Discord/email), chi tiết đầy đủ vẫn nằm ở
artifact gốc (log script, plan JSON) cho ai cần đào sâu — KHÔNG mất thông tin, chỉ không đẩy vào
kênh mà CEO đọc mỗi tối để duyệt quyết định.

- Ca thật: `compute_park_trim.py` sinh note "rổ mục tiêu kỳ ...: 19/30 mã khả thi, bỏ 11 mã..."
  liệt kê đủ công thức cho từng mã bị bỏ — `send_plan_report.sh` echo nguyên khối (truncate 300
  ký tự thô, không phải tóm tắt có chủ đích).
- Sửa ở NGUỒN sinh note (`compute_park_trim.py`), không phải ở renderer: nguồn nên tự tóm tắt
  ("N mã dưới 1 lô, xem log để biết chi tiết") thay vì generate wall-of-text rồi để renderer cắt
  ngẫu nhiên theo ký tự.

## 6. Không dùng ngôn ngữ mập mờ/phỏng đoán khi có thể nói thẳng sự thật đã xác nhận

Áp dụng tinh thần §29 `coding_guidelines.md` (chẩn đoán phải trích bằng chứng, không đoán) CHO VĂN
BẢN report/plan-note, không chỉ log lỗi:
- Nói thẳng trạng thái đã xác nhận ("state=3 khớp golive_state_today.json as_of=...") thay vì mô
  tả mập mờ ("có thể đã cũ", "khả năng cao đúng").
- Không xác nhận được → nói rõ "chưa xác nhận được X" (kèm lý do nếu biết), KHÔNG đoán hộ hoặc im
  lặng bỏ qua.
- Test nhanh khi review 1 câu render: "câu này khẳng định điều gì; code có ĐỌC được giá trị nào để
  biết điều đó không?" — không trả lời được bằng 1 biến/1 lần đọc cụ thể ⇒ viết lại.

---

## 7. Cấu trúc chuẩn cho report/plan-note

Mọi report gửi duyệt (daily plan report) và mọi note[] hiển thị trong đó theo thứ tự:

1. **DANH SÁCH QUYẾT ĐỊNH** lên đầu — mỗi lệnh/nhóm lệnh đồng nhất 1 dòng (nhóm PARK_TRIM cùng lý
   do gộp 1 dòng theo mục 2, không liệt kê lại theo mục 3).
2. **LÝ DO** ngắn ngay cạnh quyết định — không lặp công thức tính, không lặp giữa các lệnh cùng lý
   do (mục 1, 2).
3. **CẢNH BÁO** (⚠️/🛑, mismatch, BLOCKED_*, margin, Trứng vàng, CAPIT lệch) nổi bật riêng, tách
   khỏi luồng quyết định chính — không chìm giữa các dòng thông tin thường (mục 4).
4. **PHỤ LỤC** ở cuối — chi tiết kỹ thuật đầy đủ (giá/qty từng mã, provenance state/price/park
   compliance, disclaimer DCF/DD) cho ai cần đối chiếu, không cần đọc để ra quyết định duyệt/từ
   chối (mục 4, 5).

Mockup cụ thể (Case A: 19 lệnh PARK_TRIM thuần; Case B: FUNDED_BY_JIT) — xem
`agents/Taylor/research/plan_report_audit_20260928/report.md` §3, dùng số liệu thật đã gửi user
xem qua Discord 2026-09-29 (user đã duyệt hướng này).

---

## Việc ĐÃ/CHƯA đổi (cập nhật khi implement — PHẦN B)

- **DGC `excluded_dividend_receivable` đã bỏ khỏi `secrets/trading_bot_accounts.json` 2026-09-29
  00:03 ICT** (user chốt, không thuộc phạm vi sửa của guideline này) → hệ quả cơ học đã verify:
  `compute_active_nav.py::excluded_dividend_pending()` đọc `dividend_receivable_config` rỗng cho
  ZaloPay ⇒ `excl_div_pending` = 0 ⇒ note "ℹ️ cổ tức excluded — ..." trong `compute_park_trim.py`
  (dòng ~542) tự động không xuất hiện nữa cho tới khi có entry mới. KHÔNG cần sửa code cho việc
  này — chỉ cần biết để không tưởng nhầm đây là 1 hạng mục PHẦN B.
- `state_verify_note` (audit §2b) — đã kiểm tra lại: không liên quan tới thay đổi DGC ở trên, mô
  tả trong audit gốc vẫn đúng (in mỗi ngày regime không đổi) → áp dụng mục 4 (rút gọn khi PASS)
  như audit đề xuất, không có mâu thuẫn cần điều chỉnh.
- **Mục 3 (Case B — không liệt kê 2 lần) đã được giải quyết TRƯỚC audit này, bởi `d23aef0e`
  (2026-08-15, "avoid duplicate merged PARK orders")**: `_already_merged()` +
  `pt_merged`/`jit_merged` (`send_plan_report.sh:549-554`) đã tắt hẳn khối "MỤC RIÊNG 1/2" khi
  `merge_park_orders.py` đã gộp proposal vào `orders[]` cùng ngày — luồng vận hành THẬT hiện tại
  (cron merge chạy mỗi ngày trước report) không còn tái lập được ca duplicate 08-07 nữa. Mockup
  Case B ở audit report.md §3b vẫn đúng NGUYÊN TẮC (không liệt kê 2 lần) nhưng minh hoạ bằng dữ
  liệu LỊCH SỬ từ TRƯỚC khi `d23aef0e` tồn tại — không cần sửa code thêm cho mục 3; chỉ còn áp
  dụng cho ca hiếm khi marker `_merged_into_orders` thiếu/hỏng (fail-open, giữ hiển thị cũ AN
  TOÀN — không giấu lệnh — đây là lựa chọn có chủ đích, không phải lỗ hổng cần vá).

## PHẦN B — trạng thái implement (2026-09-29, worktree `wt-planreportstyle-2909`)

1. `bin/send_plan_report.sh`: đã sửa mục 1 (hardcode `"1,3× vốn"` → `f"{CAPIT_LEVER_APPROVED_F:g}×"`,
   dòng ~469-483) và mục 2 (19 dòng "Lý do" PARK_TRIM lặp → 1 dòng tổng, dòng ~687-800). Mục 7
   (cấu trúc DANH SÁCH→LÝ DO→CẢNH BÁO→PHỤ LỤC theo đúng mockup Case A/B compact) **CHƯA làm** —
   đó là restructure lớn hơn (viết lại toàn bộ vòng lặp render lệnh, đụng DCF/DD/funding-note
   lồng trong từng lệnh) với rủi ro cao hơn nhiều so với 2 bug cụ thể đã sửa; để lại cho 1 job
   riêng có đủ turn budget thay vì làm vội trong job này.
2. `bin/compute_park_trim.py`: đã sửa mục 5 — note "rổ mục tiêu kỳ..." rút còn 1 dòng tóm tắt,
   chi tiết từng mã (ticker/weight/reason) vẫn nguyên vẹn trong `basket_dropped` (không mất
   thông tin).
3. Mọi nội dung compliance/provenance bắt buộc GIỮ NGUYÊN — không đụng.
4. Selfcheck: `send_plan_report_park_jit_selfcheck.py` +2 test mới (T10 mở rộng, T11 mutation-
   guard cho fix hardcode 1,3×) PASS dưới TZ=Asia/Ho_Chi_Minh (24/26, 2 fail PRE-EXISTING không
   liên quan — xem dưới). `compute_park_trim_selfcheck.py` +2 test mới (T7c/T7d) PASS 116/116 cả
   3 TZ (ICT/UTC/no-TZ). Regression `send_plan_report_state_gate_selfcheck.py` PASS 9/9.
5. ⚠️ **Phát hiện ngoài phạm vi task này**: `send_plan_report_park_jit_selfcheck.py` KHÔNG
   TZ-robust — dưới `TZ=UTC` hoặc `env -u TZ`, phần lớn test suite fail (không phải do thay đổi
   trong job này: đã xác nhận bằng cách stash sạch về baseline `777734db` và chạy lại, fail set
   giống hệt). 2 test cụ thể ("env -u TZ: 4 mục vẫn đủ", "TZ=America/New_York: 4 mục vẫn đủ")
   fail NGAY CẢ dưới TZ=Asia/Ho_Chi_Minh ở baseline — pre-existing, không phải do PHẦN B. Việc
   sửa cần điều tra riêng (khả năng: fixture ngày cố định lệch theo "hôm nay" tính theo TZ) —
   không sửa trong job này vì ngoài phạm vi style guide.
