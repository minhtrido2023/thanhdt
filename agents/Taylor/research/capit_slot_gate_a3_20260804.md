# A3 — Cổng CAPIT slot targets có đủ ngăn tái phạm bug 07-21 không?

**Job** `Taylor_20260804_155443` · 2026-08-04 · **KHÔNG build script đọc-only như đề xuất — lý do bên dưới; build 1 patch KHÁC, chờ duyệt**

---

## 0. Trả lời thẳng câu hỏi dispatch

Dispatch hỏi hai nhánh: (a) bắt DollarBill đọc `status['capit_slot_targets']` qua một script
đọc-only kiểu `filter_lag_entry_window.py`, hay (b) kết luận cổng WARN hiện tại đã đủ và đóng.

**Câu trả lời là không nhánh nào.** Đo được:

1. **Cổng WARN hiện tại BẮT ĐƯỢC đúng ca 07-21** — chạy thật, không suy luận: −27,0%, kèm
   đúng câu chẩn đoán "kiểm tra đã nhân capit_size hai lần chưa". Nhánh (b) sai ở chỗ khác.
2. **Nhưng cổng TỐI trên mọi phiên TOP-UP** — `capit_slot_targets` chỉ được publish khi
   `capit_signal_today=true`. Hôm nay: episode `CAPIT-2026-07-20` **đang mở**,
   `capit_sessions_held=11`, `capit_slot_targets={}`, `n_capit_basket=0`. Tức cổng canh cỡ
   deploy bị mù **đúng trong lúc deploy đang diễn ra**.
3. **⇒ Script đọc-only theo đề xuất sẽ mù y hệt**, vì nó đọc CHÍNH cái field rỗng đó. Xây nó
   là tạo cảm giác đã che, trong khi 11/11 phiên gần nhất nó trả về `{}`. Đây là lý do KHÔNG
   build nhánh (a) — không phải vì "gate hiện tại đã đủ".

Cái đáng xây là mốc so ĐÚNG cho phiên top-up: `capit_episode_remaining_qty` (số CP còn thiếu
/mã/account) — engine **đã publish sẵn**, chỉ chưa ai đọc.

---

## 1. Phương pháp — chạy chính văn bản production, không đọc rồi phán

`mike/agents/Taylor/research/capit_warn_gate_replay_20260804.py` **trích khối python của cổng
ra khỏi `mike/bin/send_plan_report.sh`** (giữa hai mốc văn bản trong chính file đó) rồi `exec`
nó trên dữ liệu plan THẬT. Ai đổi ngưỡng/câu chữ bên production thì test thấy ngay — nó chạy
văn bản đó, không phải bản chép tay. **26/26 PASS.**

---

## 2. Cổng hiện tại làm được gì (đo, không đoán)

| Kiểm | Kết quả |
|---|---|
| Replay plan THẬT `plan_SpaceX_2026-07-21.json` (5 lệnh, Σ 254.425.000đ) vs mục tiêu 348,4tr | **⚠️ lệch −27,0%**, nêu đúng nguyên nhân nghi ngờ |
| Plan đúng cỡ (Σ == mục tiêu) | ✅ im, không kêu oan |
| Biên ngưỡng: 9,5% → im · 10,5% → kêu | đúng (đúng 10,0% là điểm dấu-phẩy-động, không assert) |

Và một sự thật về mức độ tin cậy của cổng: **nó chưa từng chạy thật trên plan có lệnh CAPIT
lần nào**. Cổng thêm 2026-07-31 (commit `d3aa3f05`); plan có lệnh CAPIT gần nhất là 2026-07-27.
Không có bằng chứng sống nào — cùng khuôn với A1 (shadow log đúng 1 dòng). Replay ở trên là
bằng chứng duy nhất hiện có, và nó là bằng chứng chạy-thật chứ không phải đọc-code.

---

## 3. Hai điểm mù đo được

### 3.1 Mù theo PHIÊN — nghiêm trọng hơn, là lý do bác nhánh (a)
`capit_slot_targets` chỉ có khi `capit_signal_today=true`. Trong một episode đang mở, hầu hết
phiên là top-up ⇒ mọi plan top-up rơi vào nhánh *"chưa publish `capit_slot_targets` — KHÔNG
đối chiếu được"*. Đối chứng chạy thật trên status LIVE hôm nay: bản cũ trả đúng câu đó.

Đây là **cùng gốc** với lỗ hổng đã ghi trong `current_ops.md` ("từ 07-29 mọi kênh báo cáo im
lặng về CAPIT vì gate theo `capit_fired`"). Nửa engine đã sửa — `capit_episode_*` đã publish,
comment trong `golive_recommend_v23.py:1086-1088` nói thẳng *"Mọi gate báo cáo phải nhìn
`capit_signal_today OR capit_episode_open`"*. **Cổng ở `send_plan_report.sh` chưa làm theo.**

### 3.2 Mù theo SỐ MÃ
Mốc so là `_slot × SỐ LỆNH TRONG PLAN`. Plan viết thiếu mã ⇒ mốc tự co lại theo. Đo được:
3/5 mã đúng cỡ slot → cổng in **"✅ khớp mục tiêu (lệch +0.0%)"** trong khi 40% vốn không được
triển khai. `n_capit_basket` đã publish sẵn, cổng không đọc.

---

## 4. Đã build (chờ duyệt) — `capit_gate_topup_coverage.patch`

Một patch, hai thay đổi, **vẫn WARN-only, không chặn gì**:

1. **Nhánh top-up mới**: episode mở + chưa có `capit_slot_targets` ⇒ đối chiếu từng mã với
   `capit_episode_remaining_qty`. Kêu khi **mua vượt phần còn thiếu** hoặc có **mã ngoài rổ
   episode**; ngược lại xác nhận rõ đã đối chiếu theo cơ sở nào.
2. **Dòng phủ rổ**: `phủ 3/5 mã của rổ — 2 mã KHÔNG có lệnh; lệch ~0% KHÔNG có nghĩa đã triển
   khai đủ vốn`. Vẫn để WARN-only vì thiếu mã CÓ THỂ đúng (đã giữ đủ, trần %ADV = 0, DD loại)
   — máy không phân biệt được, người duyệt phân biệt được.

Verify (đều chạy thật, trên bản copy trong tmpdir — **production 0 file thay đổi**):
`git apply --check` sạch · `bash -n` OK · `mike/bin/shellcheck_gate.sh` rc=0 · ca 07-21 **vẫn
bị bắt** (không hồi quy) · top-up đúng → ✅ trên status LIVE hôm nay · mua vượt → ⚠️ nêu đúng mã
· mã ngoài rổ → ⚠️ · không episode + không target → vẫn fail-open, tự khai.

---

## 5. Vì sao KHÔNG build script đọc-only, nói cho hết

Ngoài lý do "nguồn rỗng" ở §0, còn hai lý do nữa:

- **Helper không wire = vẫn dựa vào trí nhớ LLM.** `filter_lag_entry_window.py` giải một bài
  toán DollarBill phải TỰ TÍNH (offset ngày). Ở đây con số **đã được tính sẵn và đã in ra**
  trong báo cáo golive kèm đúng câu "DÙNG THẲNG SỐ NÀY, KHÔNG TỰ NHÂN LẠI". Thêm một script
  nữa để in lại cùng con số không thêm ràng buộc cơ học nào; nó chỉ thêm một bước phải nhớ.
- **Hàng rào cơ học ở tầng dữ liệu đã có**: cột CSV bị đặt tên
  `NAV_book_LAG__DA_GOM_capit_size__KHONG_NHAN_LAI` — cùng kỹ thuật đã chứng minh hiệu quả với
  `close_bq_stale_DO_NOT_USE_AS_REFPRICE`. Đúng con đường đã gây lỗi 07-21 thì đã được rào.

**Điều KHÔNG kết luận**: không kết luận "cổng WARN-only là đủ". Nó reactive theo nghĩa hẹp
(bắt sau khi plan viết xong) nhưng nằm ở **21:00, trước khi user duyệt và trước khi tiền chạy
09:05** — chỗ cuối cùng còn sửa được miễn phí. Nâng lên gate CHẶN là quyết định chính sách của
user, không phải dọn dẹp kỹ thuật, và tôi không đề xuất nó ở đây.

## 6. Đề nghị Mike

1. Áp `capit_gate_topup_coverage.patch` (sau quant-skeptic).
2. **Không** build script đọc-only `capit_slot_targets` — lý do §0/§5.
3. Ghi vào mục CAPIT của `current_ops.md`: cổng WARN chưa từng chạy thật trên plan có lệnh
   CAPIT; lần tới có plan CAPIT là dịp đầu tiên xác nhận nó chạy đúng trong đời thật.
