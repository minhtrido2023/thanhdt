# Plan/report style guide — render layer cho báo cáo & plan-note

**Phạm vi (2 consumer, CÙNG 1 chuẩn, không phải 2 chuẩn riêng):**
(a) `bin/send_plan_report.sh` (report renderer gửi user duyệt hằng ngày — Discord/email);
(b) mọi script sinh `notes[]`/text hiển thị bên trong plan JSON mà (a) echo lại nguyên văn —
`bin/compute_park_trim.py`, `bin/merge_park_orders.py`, `bin/compute_jit_unpark.py`, và bất kỳ
script tương tự sau này. Nội dung do (b) tạo ra HIỂN THỊ TRONG (a) — không tách biệt được, nên
cùng 6 luật dưới áp dụng cho cả hai.

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
  trong khi `_pv['lever_f']` (biến số thật) đã có sẵn cùng scope, dùng đúng 10 dòng dưới ở dòng
  492. Sửa: `f"{_pv['lever_f']:g}×"`. Đúng hôm audit vì `CAPIT_LEVER_APPROVED_F = 1.3` trùng khớp
  ngẫu nhiên — đổi gói đòn bẩy (có tiền lệ đặt tên f=1.5) sẽ lập tức sai mà không ai phát hiện.
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

## 4. Nội dung compliance/provenance bắt buộc — GIỮ, RÚT GỌN khi không có bất thường

Các khối bắt buộc theo quy chuẩn khác (state-verify §28, price-verify, DCF/DD disclaimer §6b,
funding note "Tiền đâu ra" 💧, cảnh báo BLOCKED_*/mismatch/margin/Trứng vàng/CAPIT lệch) **KHÔNG
được xoá nội dung**, nhưng:
- Khi mọi thứ khớp/bình thường → rút thành **1 dòng/icon** (vd `"✅ state khớp · giá khớp"`), KHÔNG
  phải câu văn đầy đủ lặp lại mỗi ngày.
- Khi có bất thường thật (⚠️/🛑, mismatch, overdue, vượt ngưỡng) → **mở rộng đầy đủ thành câu văn**
  như hiện tại — đây là lúc thông tin chi tiết thật sự cần thiết.
- Đây là RÚT GỌN HIỂN THỊ, không phải giảm coverage: logic verify bên dưới không đổi, chỉ đổi cách
  render kết quả PASS vs FAIL.
- **KHÔNG đề xuất xoá** (danh sách chốt từ audit, đều tồn tại vì sự cố thật): funding note "Tiền
  đâu ra", cảnh báo BLOCKED_*, mismatch state/price, cảnh báo margin, cảnh báo Trứng vàng cần rút,
  cảnh báo Σ CAPIT lệch >10%.

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
