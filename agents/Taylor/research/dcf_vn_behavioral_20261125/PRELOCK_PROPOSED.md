# PRELOCK ĐỀ XUẤT — G1 "trạng thái thừa nhận + lực kéo" (CHƯA khoá; chờ user duyệt và quant-skeptic góp ý TRƯỚC khi chạy)

Bản này là đề xuất tiêu chí cho giai đoạn G1. Pilot G0 đã khoá riêng ở `PRELOCK_PILOT.md` (commit `3597bc9e2`) và đã chạy.
**Dữ liệu 2015–2025 đã bị pilot nhìn** cho `hi52`, `cgo`, đà, E/P, `lv_ENS2` ⇒ mọi phép thử G1 trên cùng giai đoạn với các
đặc trưng này là bán-ngoài-mẫu; bằng chứng sạch chỉ đến từ §3 (mẫu giữ lại 2009–2012) và §7 (theo dõi về sau).

## 1. Đối tượng thử (đếm trước, không thêm sau khi thấy số)
- **Q0 (chính, KHÔNG có tham số ước lượng):** điểm thừa nhận `a` = hạng `hi52` trong tháng; điểm nội tại `v` = hạng `lv_ENS2`.
  Bốn ô theo trung vị tháng: RẺ-ĐƯỢC THỪA NHẬN (v cao, a cao) · RẺ-CHƯA THỪA NHẬN (v cao, a thấp) · ĐẮT-CÒN NEO (v thấp, a cao) ·
  ĐẮT-ĐANG NGUỘI (v thấp, a thấp). Điểm xếp hạng liên tục: `s0 = v + a` (trọng số bằng nhau).
- Đối chứng: **N1** = hạng E/P + hạng `hi52` (cùng dạng, thay tâm nội tại bằng E/P) · **N2** = hạng E/P đơn · **N3** = đà 12-1 đơn ·
  **N4** = hạng `hi52` đơn · **RW** = không dự báo.
- Biến thể phụ (mỗi cái MỘT phép thử, thêm theo đúng thứ tự, dừng ở cái đầu tiên không đạt §4-c): (i) `a` = trung bình hạng
  `hi52` và `cgo`; (ii) + phạt chú ý: trừ hạng `n_up60`; (iii) + phạt xổ số: trừ hạng `max21`; (iv) hệ số ước lượng cuốn chiếu
  (mô hình F của pilot) với ridge λ chọn trên IS theo khối năm; (v) khối ngoại ròng 60 phiên / vốn hoá (chỉ OOS 2019+, nhãn
  "không có IS").
- Tổng số phép thử: 1 chính + 5 phụ + 7 mô hình × 2 kỳ hạn của pilot = **20** (dùng làm N trials cho DSR; họ ≥ 8 biến thể ⇒ tính PBO
  bằng CSCV theo khối năm).

## 2. Khung (giữ nguyên khung V3.1 đã qua skeptic V3)
Panel `out_F/vp2.parquet`; một vintage giá; nhãn `fwd12_h50` (chính), `fwd24_h50` (phụ), báo kèm h0/h100; cổng `in_universe`;
không `profit_*`, không `ticker_prune`. IS as-of 2014-01→2019-12; OOS 2020-01→2025-10 (h=12), →2024-10 (h=24). CI: bootstrap khối
NĂM as-of (B = 2000) và bootstrap theo MÃ; báo cả hai, quyết định theo cái rộng hơn. N độc lập: 6 năm IS, 6 năm OOS (h=12),
chồng lấn 11/12 giữa các tháng liền kề ⇒ nói rõ khi báo.

## 3. Mẫu giữ lại chưa nhìn: 2009-01→2012-12
Panel có `lv_ENS2` (3.014 → 6.373 dòng/năm) nhưng chưa có cổng. Dựng cổng thanh khoản theo ruleset v1 từ `Price × Volume` của
`px_pre2013_d.csv` (đúng hàm `gate` của `b_panel.py`). **Giới hạn khai trước:** không có mã đã huỷ niêm yết trước 2013 ⇒ thiên lệch
sống sót; thị trường mỏng (2009: 373 mã có giá). Vai trò: kiểm DẤU, không cộng vào mẫu chính.

## 4. Tiêu chí số hoá
**(a) Kỹ năng xếp hạng — phép thử chính:** ΔIC12(`s0` − N1) > 0 **và** ΔIC12(`s0` − N2) > 0, CI 95% không chứa 0 ở OOS, cùng dấu ở IS
và ở mẫu giữ lại §3.
**(b) Giá trị của bốn ô:** lợi suất tương đối 12 tháng: RẺ-ĐƯỢC THỪA NHẬN − RẺ-CHƯA THỪA NHẬN ≥ +4 điểm log và ĐẮT-ĐANG NGUỘI −
ĐẮT-CÒN NEO ≤ −4 điểm log, CI không chứa 0 ở cả IS và OOS; **và** hiệu này phải lớn hơn cùng hiệu khi thay `lv_ENS2` bằng E/P (N1)
— nếu không, bốn ô chỉ là "E/P × đỉnh 52 tuần".
**(c) Biến thể phụ được giữ** chỉ khi ΔIC12 so với bậc trước > 0 với CI không chứa 0 ở OOS và cùng dấu IS.
**(d) Mức giá (báo cáo, không quyết định):** sai số tuyệt đối log trung vị 12/24 tháng của "giá kỳ vọng" so với RW. Pilot đã cho
≈ 0 ⇒ **không hứa** cải thiện; nếu vẫn ≥ RW thì KHÔNG hiển thị con số mức giá.
**(e) Giá trị đầu tư (NAV, tái dùng `e_bt2.py`):** rổ quý, đều trọng số, khớp T+1, TC 0,1%/chiều, **pin0% (đầu sàn)**, sàn thanh khoản
1 và 5 tỷ, mã ngừng giao dịch mất 50%. Chân: S-Q0 (ô RẺ-ĐƯỢC THỪA NHẬN) so với chân đối chứng CHẠY LẠI trên cùng code: S7-E/P,
S-N1, EW. Đạt khi CAGR(S-Q0) − CAGR(S-N1) có CI khối năm không chứa 0 **và** DSR (N trials = 20) ≥ 0,95 **và** PBO < 0,5.
Self-check 0 VND + tính lại độc lập từ CSV holdings; 3 TZ cùng md5.
**(f) Độ trễ nguội:** với sự kiện ĐẮT-CÒN NEO (6 tháng liền, bấm lại sau 36 tháng — đúng luật sự kiện của V3): trung vị số tháng tới
khi `a` rơi dưới trung vị, và lợi suất tương đối 12 tháng TÍNH TỪ lúc đó so với tính từ lúc cắm cờ đắt. Chỉ mô tả + CI.

## 5. Điều kiện NO-GO (ghi trước)
1. (a) không đạt ⇒ **không có mô hình hành vi**; giữ E/P + tâm nội tại như V3; đóng nhánh.
2. (a) đạt nhưng (b) không hơn N1 ⇒ kết luận "E/P × đỉnh 52 tuần là đủ"; KHÔNG gắn nhãn "tâm hành vi".
3. (e) không đạt ⇒ chỉ là lens hiển thị (nếu (a)+(b) đạt), không đề xuất luật vào/ra, không sizing.
4. Dấu ở mẫu giữ lại §3 ngược ⇒ hạ một bậc tin cậy và nói thẳng.
5. Mọi biến thể thêm sau khi thấy số ⇒ nhãn "giả thuyết", không vào kết luận.

## 6. Ca kiểm (khoá trước; báo cả ca hỏng)
VNM 2015-06 / 2015-12 / 2017-12, VCS 2015-06 / 2015-12, DGC 2016-06 / 2016-12, HPG 2019-06 / 2019-12 + 30 dòng ngẫu nhiên phân tầng
theo ô (seed 20261125; pilot đã có 12 dòng ở `out/cases.csv`). Ca sai chiều đã thấy ở pilot (5/9) PHẢI giữ trong báo cáo: VNM 2015-06, VNM 2015-12, VNM 2017-12 (giá 12 tháng sau −0,341 log),
DGC 2016-06 (dự báo +0,089, thực −0,464), HPG 2019-06.

## 7. Sống sót, năng lực, theo dõi về sau
- Sống sót: chạy 3 cận h0/h50/h100 (pilot: ΔIC đổi ≤ 0,004); tách BQ-only so với có mã vắng BQ; việc đối chiếu GDKHQ cho mã vắng
  BQ còn mở từ V3.1 — không tự đóng ở đây.
- Năng lực: báo ở sàn 1 và 5 tỷ; V3.1 đã cho thấy ở 5 tỷ E/P-công-bằng thắng mô hình ⇒ kết quả chỉ đạt ở sàn 0/1 tỷ thì ghi "không
  đủ năng lực cho 50B".
- Theo dõi về sau (bằng chứng sạch duy nhất): ghi nhãn bốn ô hàng tháng từ 2026-11, đọc lần đầu khi nhãn 12 tháng đóng (2027-11).
  Đăng ký vào `paper_programs_registry.json` nếu user duyệt (không tự cài cron trong job này).
