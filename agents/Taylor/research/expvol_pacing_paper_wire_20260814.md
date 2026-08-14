# P2 (expected-volume pacing) — wire PAPER-ONLY + đăng ký paper trial

Job `Taylor_20260814_161511` · Taylor · 2026-08-14
Chỉ đạo: user John qua Mike — "đưa P2 vào paper trial NGAY, song song và độc lập với chương
trình order-book (P5)".

> **TRẠNG THÁI: LIVE KHÔNG ĐỔI HÀNH VI.** P2 bị khoá sau `expected_volume_pacing_live_gate`
> (mặc định True ⇒ chỉ ăn ở account `mode == "paper"`). Xác minh trên cấu hình THẬT:
> SpaceX / ZaloPay / RocketX → `_expvol_active() = False`; main / ab_cross / ab_dip → True.

---

## 1. Điểm xuất phát khác với giả định của dispatch

Dispatch mô tả việc là "implement P2 vào `_child_qty`". Đọc code trước khi viết thì thấy
**P2 đã được implement và commit từ 2026-08-12** (`49c819e`, quant-skeptic CONFIRMED, selfcheck
riêng 44 ca). Cái CÒN THIẾU đúng bằng cái dispatch nhấn mạnh nhất:

| | Trước job này | Sau job này |
|---|---|---|
| Cờ tính năng | `expected_volume_pacing_enabled = False` | `True` (bật cho paper) |
| Cổng LIVE | **KHÔNG CÓ** — flip cờ là P2 ăn thẳng trên tiền thật | `expected_volume_pacing_live_gate = True` |
| Nguồn số cho trial | không có | `EXPVOL_SHADOW` (đối chứng ghép cặp, log-only) |
| Đăng ký chương trình | không có | `expvol_pacing` trong `paper_programs_registry.json` |

Nên việc thật của job này là **cổng + cơ chế ĐO + đăng ký**, không phải viết lại thuật toán.

## 2. Ba thay đổi code

**(a) Cổng LIVE** — `_expvol_active()`, sao đúng khuôn `fill_timing_live_gate` đã dùng cho
HYBRID: cờ BẬT **và** không bị gate chặn. Fail-safe hai chiều: thiếu cờ ⇒ tắt, **thiếu gate ⇒
bật gate** (paper-only), không mở toang. Tách thành hàm riêng để đường HÀNH ĐỘNG
(`_expected_vol_basis`) và đường ĐO (`_expvol_shadow`) đọc CÙNG một điều kiện — hai nơi tự
đánh giá thì mẫu đối chứng có thể ghi số của một chế độ khác chế độ đang chạy (§28).

**(b) Đối chứng ghép cặp `EXPVOL_SHADOW`** — khi P2 KHÔNG hoạt động, executor vẫn tính
allowance mà P2 SẼ cho ở **cùng lệnh / cùng tape / cùng phút**, ghi journal, **không đụng KL**.
Toàn bộ nhánh bọc `try/except` nuốt lỗi: đây là nhánh đo lường nằm trên đường sinh KL của mọi
lệnh CAPIT/DISCRETIONARY_SPECIAL trên tiền thật, một `ZeroDivisionError` vì cấu hình rác mà làm
hỏng lệnh live là cái giá không tương xứng với một dòng log. Dedupe theo PHÚT (không theo ngày
như `EXPVOL_PACING`): cần chuỗi thời gian để đo, nhưng vẫn phải chặn 2 lời gọi `_child_qty`
trong cùng chu kỳ 20s thành 2 quan sát — đếm trùng thổi phồng N của chính trial.

**(c) `mike/bin/expvol_shadow_probe.py`** — đọc journal live, quy về **order-day**
(date × account × parent_id) làm đơn vị N, và **recompute độc lập** bất biến an toàn
`(F+X)/(V+X) ≤ 50%` từ chính số đã log thay vì tin field `p2_clamp`.

## 3. Phát hiện quyết định thiết kế của trial: paper một mình đo được SỐ 0

Nhánh ADV20-paced chỉ nhận **CAPIT buy ∪ DISCRETIONARY_SPECIAL buy**
(`executor.py::_adv20_basis_for`). Đếm trên toàn bộ plan đã sinh:

| account | book | số lệnh |
|---|---|---:|
| main (PAPER) | PROBE | **342** |
| main (PAPER) | CAPIT / DISCRETIONARY_SPECIAL | **0** |
| SpaceX | CAPIT · DISCRETIONARY_SPECIAL | 7 · 10 |
| ZaloPay | CAPIT · DISCRETIONARY_SPECIAL | 5 · 5 |

⇒ **Bật cờ trên paper một mình sẽ chạy 4 tuần rồi báo cáo 0 quan sát.** Đó chính là hình dạng
thất bại đã xảy ra với gate-1 của `fill_timing` (cron bằng chứng trúng đúng ngày net-SELL,
P(có lệnh mua) = 0 tuyệt đối — đứng im 18 ngày, `fill_timing_eta_investigation_20260810.md`).

Vì vậy nguồn số của trial là **journal LIVE qua `EXPVOL_SHADOW`**, không phải paper. Đây là mẫu
ghép cặp tốt nhất tồn tại: cùng order, cùng tape, cùng giây, khác đúng một biến. Cờ paper vẫn
bật để đường thật được chạy end-to-end nếu sau này có plan paper phát sinh CAPIT/DISC.

Cũng lưu ý **phạm vi hẹp hơn mô tả trong dispatch**: dispatch viết "BAL/LAG/discretionary".
Lệnh BAL/LAG đi nhánh `max_participation × day_volume` KHÁC và **P2 không chạm**. Trong phạm vi
CAPIT+DISC thì đúng là mọi mã, không riêng TV1.

## 4. Tần suất cơ hội — cơ sở chọn độ dài trial

Đếm trên plan thật 2026-07-01 → 08-17: **27 lệnh ADV20-paced buy trên 10 ngày có lệnh**, gần
đây 1–2 lệnh/phiên (chương trình gom TV1). Mỗi lệnh sinh nhiều slice, nhưng slice trong cùng
một lệnh-phiên **không độc lập** ⇒ N đếm theo order-day (§18).

⇒ **20 phiên (08-17 → 09-11) kỳ vọng ~25–40 order-day.** Chốt: review **2026-09-15**, điều kiện
KÉP lấy mốc đến sau — ≥20 phiên **VÀ** ≥25 order-day. Thiếu order-day tại 09-15 = **gia hạn**,
không phải NO-GO (mẫu mỏng ≠ không có edge). Đề xuất gốc trong README là "≥4 tuần" chung chung;
20 phiên ≈ 4,3 tuần nên không mâu thuẫn, chỉ thêm điều kiện cỡ mẫu.

## 5. Gate criteria — vì sao KHÔNG có P&L

Cùng nguyên tắc đã áp cho order-book: fill cao hơn chỉ tốt khi bản thân quyết định mua là đúng,
đó là câu hỏi khác (DCF/DD). 5 gate: (1) an toàn — 0 vi phạm trần 50% tape + 0 `SHADOW_ERR`
(gate CHẶN); (2) LIVE không đổi hành vi; (3) cơ hội có thật — ≥10% slice `bind=ceil` và trung vị
delta > 0; (4) **cận trên** cơ hội bị bỏ lỡ (κ không neo được ⇒ không được đọc là fill sẽ thu
thêm); (5) quant-skeptic + user sign-off mới flip gate. Chi tiết + note từng gate:
`mike/kb/paper_programs_charter/expvol_pacing.md` (tự sinh từ registry).

## 6. Verify

- `expected_volume_pacing_selfcheck.py`: **59 ca PASS** (44 cũ + mục **L** cổng LIVE 6 ca +
  **M** đối chứng shadow 13 ca). Mục L có ca chứng minh ngược (paper thì P2 ăn thật) và ca
  thiếu-khoá-gate; mục M kiểm shadow ghi ĐÚNG số P2 thật, không đổi KL, và nuốt lỗi trên 4 cấu
  hình rác.
- **Sweep rộng 17/17 file selfcheck phụ thuộc `trading_bot.executor`** (`selfcheck_scope_map.sh`
  — bản đồ trả **17**, dispatch ghi 11; dùng số của công cụ), **694 ca PASS**.
- `expvol_shadow_probe_selfcheck.py`: **13 ca PASS**, chạy lại dưới `TZ=UTC`, `env -u TZ`,
  `TZ=America/New_York` (§16/§19).
- Cấu hình THẬT: 3/3 account live `_expvol_active()=False`, 3/3 paper `True`.

**Hai lỗi của chính tôi, do test bắt được, ghi lại vì cả hai đều là lỗi ĐO chứ không phải lỗi
code được đo:**
1. Bản nháp mục L so lưới paper-off với live-on và "bắt" 11/30 ô lệch — **toàn bộ do HYBRID**
   (đổi `mode` cũng tắt `fill_timing_live_gate`), 0 do P2. Sửa: tắt hẳn fill-timing trong lưới
   để chỉ còn đúng một biến.
2. Mục M ban đầu đọc `shadow_rows(...)[0]` trên journal DÙNG CHUNG giữa các executor ⇒ đọc phải
   dòng của executor trước; "PASS" chỉ vì hai fixture tình cờ trùng tham số, và FAIL M3d mới lộ
   ra. Sửa: journal riêng cho từng executor.
   Cùng loại: fixture của probe selfcheck ghi tay `p2_clamp` sai số học (V=800, F=500 ⇒ clamp
   thật −200, tôi ghi 300) — recompute độc lập bắt ngay. Fixture giờ suy ra từ công thức.

## 7. Còn mở / caveat mang theo

1. **Lợi ích kỳ vọng là +4,6pp fill, KHÔNG phải +7,7pp** như bảng §4 README — công thức clamp
   đã deploy khác bản đo trong nghiên cứu (caveat từ vòng verify 08-12, chưa đóng). An toàn
   không đổi.
2. **κ không neo được** ⇒ mọi con số của trial là cận trên/cơ hội, không phải fill sẽ thu thêm.
3. Entry `order_book_execution_shadow` (P5) hiện **chỉ nằm trên nhánh
   `session/1521113190405247057`** (commit `f4e96f28`), chưa merge master ⇒ người merge sẽ gặp
   xung đột JSON ở mảng `programs` (hai entry cùng thêm vào cuối). Hai track độc lập, không
   chặn nhau.
4. P1 (trần no-chase động) LIVE từ 08-13, **không thuộc phạm vi** job này, không đụng.
