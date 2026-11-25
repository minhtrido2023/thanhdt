# PRELOCK ĐỀ XUẤT — G1 "trạng thái thừa nhận + lực kéo" (CHƯA khoá; chờ user duyệt chạy G1 và quant-skeptic vòng 2 TRƯỚC khi chạy)

Bản gốc (job Taylor_20261125_104308) nằm ở commit `7294cf0d1`. Bản này = bản gốc **sửa sau skeptic vòng 1 + user duyệt 25/11 18:44 ICT** (job
Taylor_20261125_114526). Mọi mục đánh dấu **[POST-HOC, sau skeptic]** là mới; chúng KHÔNG đổi số pilot đã khoá (`PRELOCK_PILOT.md`, commit `3597bc9e2`).
**Dữ liệu 2015–2025 đã bị pilot nhìn** cho `hi52`, `cgo`, đà, E/P, `lv_ENS2` ⇒ mọi phép thử G1 trên cùng giai đoạn là bán-ngoài-mẫu; bằng chứng sạch chỉ
đến từ §3 (mẫu giữ lại 2009–2012) và §7 (theo dõi về sau). **Cảnh báo NO-GO dự kiến:** s0 − N1 quy về `lv_ENS2` vs E/P (B3−B2 pilot: h=12 IS −0,027,
OOS +0,001; h=24 IS +0,003, OOS −0,047) ⇒ (a) dự kiến NO-GO 1 (`PLAN.md` §0.5, §7).

## 1. Đối tượng thử (đếm trước, không thêm sau khi thấy số)
- **Q0 (chính, KHÔNG có tham số ước lượng):** điểm thừa nhận `a` = hạng `hi52` trong tháng; điểm nội tại `v` = hạng `lv_ENS2`.
  Bốn ô theo trung vị tháng của `v` và `a`. Điểm xếp hạng liên tục: `s0 = v + a` (trọng số bằng nhau).
- **[POST-HOC] Xếp hạng `v` cho ngân hàng — khoá cách làm:** hạng `v` tính TRONG nhóm route BANK riêng (3.085 dòng-tháng route BANK trong panel) và trong
  nhóm phi-BANK riêng, rồi ghép lại thành phần trăm trong nhóm; `a` xếp hạng trên toàn universe (không phụ thuộc ngành). Mỗi nhóm cần ≥ 15 mã/tháng, thiếu ⇒
  dùng hạng toàn universe cho tháng đó và đếm số tháng như vậy. Phép thử phụ: lặp lại với hạng toàn universe, báo hiệu số. **Cờ "đổi cấu trúc" (kiểu VCS 2015):**
  ĐƯA RA KHỎI G1 — chỉ là nhắc hiển thị, ngưỡng không được đặt hay tinh chỉnh trong G1.
- Đối chứng: **N1** = hạng E/P + hạng `hi52` · **N2** = hạng E/P đơn · **N3** = đà 12-1 đơn · **N4** = hạng `hi52` đơn · **RW** = không dự báo.
- Biến thể phụ (mỗi cái MỘT phép thử, thêm theo đúng thứ tự, dừng ở cái đầu tiên không đạt §4-c): (i) `a` = trung bình hạng `hi52` và `cgo`
  — **[POST-HOC]** `cgo` PHẢI dùng N theo ngày kiểu sửa mc V3.1 (N tại từng ngày, ffill thuần PIT, KHÔNG lấp ngược) HOẶC chạy trên OShares trước biến thể (i);
  lấp ngược N ở pilot (`calc/p1_features.py:31-32`, 4,37% dòng-ngày) là LỆCH so với `PRELOCK_PILOT.md` §2, G1 không được lặp lại; (ii) + phạt chú ý: trừ hạng
  `n_up60`; (iii) + phạt xổ số: trừ hạng `max21`; (iv) hệ số ước lượng cuốn chiếu (mô hình F của pilot) với ridge — **[POST-HOC] lưới λ liệt kê trước:**
  λ ∈ {0; 0,1; 1; 10; 100} (hạng co [−0,5; +0,5], chuẩn hoá bằng số dòng/tháng), chọn trên IS theo khối năm, mỗi giá trị λ tính là một trial; (v) khối ngoại
  ròng 60 phiên / vốn hoá (chỉ OOS 2019+, nhãn "không có IS").
- **[POST-HOC] N trials cho DSR — đếm lại, rộng hơn:** 1 chính + 5 phụ + 7 mô hình pilot × 2 kỳ hạn (14) + họ V3/V3.1 đã thử trên cùng panel
  (ENS1, ENS1w, ENS2, D0) **4** + cận sống sót h0/h50/h100 **3** + lưới λ ridge **5** + hai trục thừa nhận (F-hành-vi, hi52) **2** = **34**; nếu thêm biến thể sau
  khi thấy số thì cộng vào trước khi tính DSR. (Số 20 của bản gốc bỏ sót họ V3.x, cận h và lưới λ.) Họ ≥ 8 biến thể ⇒ PBO bằng CSCV theo khối năm.
- **[POST-HOC] DSR tính trên chuỗi NAV nào / giai đoạn nào:** chuỗi NAV hằng tháng của chân S-Q0, hiệu số với S-N1 làm kiểm phụ; giai đoạn **OOS 2020-01→2025-10 duy
  nhất** (IS dùng để chọn λ và biến thể, không đưa vào DSR); Sharpe tính trên lợi suất tháng; T = số tháng OOS; khai kèm độ lệch/độ nhọn thực của chuỗi.

## 2. Khung (giữ nguyên khung V3.1 đã qua skeptic V3)
Panel `out_F/vp2.parquet`; một vintage giá; nhãn `fwd12_h50` (chính), `fwd24_h50` (phụ), báo kèm h0/h100; cổng `in_universe`; không `profit_*`, không
`ticker_prune`. IS as-of 2014-01→2019-12; OOS 2020-01→2025-10 (h=12), →2024-10 (h=24).
- **[POST-HOC] Chặn/báo chồng lấn nhãn IS/OOS:** nhãn 12T của as-of 2019-01→2019-12 kéo tới 2020-12, trùm lên giai đoạn OOS; nhãn 24T của as-of 2018-01→2019-12
  cũng vậy. Quy tắc: (1) mọi hệ số/λ/lựa chọn mô hình chỉ dùng các tháng s với s + h ≤ mốc đóng băng (h=12: s ≤ 2018-12; h=24: s ≤ 2017-12 — đúng như pilot); (2)
  IS dùng để BÁO CÁO phải cắt (purge) cùng mốc ấy: **IS báo cáo = as-of ≤ 2018-12 (h=12), ≤ 2017-12 (h=24)**; as-of 2019 báo riêng, nhãn "chồng nhãn với OOS";
  (3) mọi bảng IS/OOS in cột "nhãn đóng đến". Pilot dùng IS tới 2019-12 — số pilot không đổi, nhưng ở G1 số IS phải là bản cắt.
- **[POST-HOC] CI — quyết theo CI RỘNG NHẤT trong ba:** (1) bootstrap khối NĂM as-of (B = 2000); (2) **t(n−1) trên trung bình theo năm** (n = 5–6 cụm; báo
  n); (3) **bản 1 tháng mỗi năm không chồng lấn nhãn** (với mỗi tháng lịch m = 1..12 lấy chuỗi qua các năm, t(n−1); báo tháng rộng nhất và tỉ lệ tháng có CI loại 0).
  Cộng bootstrap theo MÃ. CI chồng lấn 11/12 giữa tháng liền kề nên (1) hẹp giả tạo; **bản 1 tháng/năm là bản bảo thủ** (script mẫu `calc/p5_interaction.py`).
  N độc lập: 5–6 năm IS, 6 năm OOS (h=12) — nói rõ khi báo.

## 3. Mẫu giữ lại chưa nhìn: 2009-01→2012-12
Panel có `lv_ENS2` (3.014 → 6.373 dòng/năm) nhưng chưa có cổng. Dựng cổng thanh khoản theo ruleset v1 từ `Price × Volume` của `px_pre2013_d.csv` (đúng hàm
`gate` của `b_panel.py`). **Giới hạn khai trước:** không có mã đã huỷ niêm yết trước 2013 ⇒ thiên lệch sống sót; thị trường mỏng (2009: 373 mã có giá).
Vai trò: kiểm DẤU, không cộng vào mẫu chính.
- **[POST-HOC] Điều kiện kiểm trước khi dùng:** (1) xác nhận bằng code + log rằng `lv_ENS2` giai đoạn 2009–2012 KHÔNG dùng tham số/hệ số ước lượng trên 2014+
  (đọc đường tính `lv_ENS2` trong `b_panel.py`/V3.1: các tham số ENS2 phải cố định a priori hoặc ước lượng chỉ trên dữ liệu ≤ as-of); nếu có ⇒ mẫu giữ lại
  KHÔNG sạch, hạ nhãn "bán-ngoài-mẫu" và nói thẳng; (2) "cùng dấu" phải kèm **số năm cùng dấu / tổng số năm** (4 năm 2009–2012) và sức mạnh: chỉ coi là xác nhận khi
  ≥ 3/4 năm cùng dấu và độ lớn ≥ 1/3 độ lớn OOS; 2/4 hoặc ít hơn ⇒ "không xác nhận".

## 4. Tiêu chí số hoá
**(a) Kỹ năng xếp hạng — phép thử chính:** ΔIC12(`s0` − N1) > 0 **và** ΔIC12(`s0` − N2) > 0, CI 95% (rộng nhất trong §2) không chứa 0 ở OOS, cùng dấu ở IS (bản
cắt) và ở mẫu giữ lại §3 (theo điều kiện §3). So với N1 dùng **CI cặp** (bootstrap cặp theo năm của hiệu IC theo tháng).
**(b) [POST-HOC, thay bản gốc] Phép thử TƯƠNG TÁC của bốn ô:** DiD = (RẺ-ĐƯỢC THỪA NHẬN − RẺ-CHƯA THỪA NHẬN) − (ĐẮT-CÒN NEO − ĐẮT-ĐANG NGUỘI) của lợi suất tương đối
12 tháng, **CI (rộng nhất trong §2) KHÔNG chứa 0 ở CẢ HAI era** (IS bản cắt và OOS); đồng thời hiệu RẺ-CAO − RẺ-THẤP ≥ +4 điểm log; **và** DiD lớn hơn DiD khi thay
`lv_ENS2` bằng E/P (N1), so bằng CI cặp. Lý do thay: pilot cho thấy bốn ô hiện là HAI HIỆU ỨNG CHÍNH CỘNG DỒN — DiD h=12 IS +0,015 [−0,103; +0,133],
OOS +0,037 [+0,013; +0,060] nhưng bản 1 tháng/năm OOS [−0,123; +0,216] (`PLAN.md` §0.4, `out/interaction.json`); tiêu chí cũ (hiệu hai cặp ≥ 4 điểm) không phân biệt
được "cộng dồn" với "tương tác". **Luật hoà: nếu DiD không loại 0 theo CI rộng nhất ⇒ NO-GO 2** (không gắn nhãn "tâm hành vi"; không đọc là "rẻ chỉ trả tiền khi đã thừa nhận").
**(c) Biến thể phụ được giữ** chỉ khi ΔIC12 so với bậc trước > 0 với CI (rộng nhất) không chứa 0 ở OOS và cùng dấu IS.
**(d) Mức giá (báo cáo, không quyết định):** user đã duyệt BỎ "giá kỳ vọng 12/24T" ⇒ không hiển thị; chỉ báo sai số tuyệt đối log trung vị so với RW để lưu hồ sơ.
**(e) Giá trị đầu tư (NAV, tái dùng `e_bt2.py`):** **[POST-HOC] khoá trước các tham số sau (không chọn sau khi thấy số):**
- sàn quyết định = **5 tỷ** (sàn 1 tỷ chỉ báo kèm làm độ nhạy, không dùng để quyết) — vì chân V3.1 ở 5 tỷ là cận gần 50B nhất;
- giai đoạn quyết định = **OOS 2020-01→2025-10** (IS bản cắt báo kèm);
- rổ quý, đều trọng số; **tháng tái cân bằng = tháng 3, 6, 9, 12 theo as-of cuối tháng**; **giá vào = giá đóng T+1 sau as-of** (mở lệnh phiên kế tiếp); TC 0,1%/chiều; **pin0%
  (đầu sàn)**; mã ngừng giao dịch mất 50%.
Chân: S-Q0 (ô RẺ-ĐƯỢC THỪA NHẬN) so với chân đối chứng CHẠY LẠI trên cùng code: S7-E/P, S-N1, EW. Đạt khi CAGR(S-Q0) − CAGR(S-N1) có CI khối năm không chứa 0 **và** DSR (N trials
theo §1 = 34) ≥ 0,95 **và** PBO < 0,5. Self-check 0 VND + tính lại độc lập từ CSV holdings; 3 TZ cùng md5. **Nhãn gốc:** nhãn pilot = log(Close cuối tháng as-of+N / Close cuối tháng as-of) (`b_panel.py` mục 4, đã đọc) — mua ở đóng cửa ngày as-of, KHÔNG phải T+1 (cột `t1_close` có trong panel, chưa dùng cho nhãn). G1 PHẢI
báo thêm độ nhạy với **gốc T+1** (nhãn tính từ giá đóng phiên kế as-of) để khớp thực thi; nếu kết luận đổi dấu giữa hai gốc thì ghi "mong manh".
**(f) Độ trễ nguội:** với sự kiện ĐẮT-CÒN NEO (6 tháng liền, bấm lại sau 36 tháng — luật sự kiện của V3): trung vị số tháng tới khi `a` rơi dưới trung vị, và lợi suất tương
đối 12 tháng TÍNH TỪ lúc đó so với tính từ lúc cắm cờ đắt. Chỉ mô tả + CI.

## 5. Điều kiện NO-GO (ghi trước)
1. (a) không đạt ⇒ **không có mô hình hành vi**; giữ E/P + tâm nội tại như V3; đóng nhánh. **(dự kiến xảy ra — xem đầu file)**
2. (a) đạt nhưng (b) không hơn N1, hoặc DiD không loại 0 theo CI rộng nhất ⇒ kết luận "E/P × đỉnh 52 tuần là đủ / chỉ cộng dồn"; KHÔNG gắn nhãn "tâm hành vi".
3. (e) không đạt ⇒ chỉ là lens hiển thị (nếu (a)+(b) đạt), không đề xuất luật vào/ra, không sizing.
4. Dấu ở mẫu giữ lại §3 ngược hoặc không đủ số năm cùng dấu ⇒ hạ một bậc tin cậy và nói thẳng.
5. Mọi biến thể thêm sau khi thấy số ⇒ nhãn "giả thuyết", không vào kết luận.

## 6. Ca kiểm (khoá trước; báo cả ca hỏng)
VNM 2015-06 / 2015-12 / 2017-12, VCS 2015-06 / 2015-12, DGC 2016-06 / 2016-12, HPG 2019-06 / 2019-12 + 30 dòng ngẫu nhiên phân tầng theo ô (seed 20261125; pilot đã có 12 dòng
ở `out/cases.csv`). **Ca sai chiều đã thấy ở pilot: 5/9 sai chiều, 4/9 đúng chiều** — PHẢI giữ trong báo cáo: VNM 2015-06, VNM 2015-12, VNM 2017-12 (giá 12 tháng sau −0,341 log),
DGC 2016-06 (dự báo +0,089, thực −0,464), HPG 2019-06.

## 7. Sống sót, năng lực, theo dõi về sau
- Sống sót: chạy 3 cận h0/h50/h100 (pilot: ΔIC đổi ≤ 0,004; **DiD OOS h=12 đổi theo cận** — h100 CI chứa 0, `PLAN.md` §10); tách BQ-only so với có mã vắng BQ; đối chiếu GDKHQ
  cho mã vắng BQ còn mở từ V3.1 — không tự đóng ở đây. **G1b (bảng mã–sàn PIT, khối ngoại) hoãn theo user 25/11.**
- Năng lực: báo ở sàn 1 và 5 tỷ (quyết định theo 5 tỷ, §4(e)); V3.1 đã cho thấy ở 5 tỷ E/P-công-bằng thắng mô hình ⇒ kết quả chỉ đạt ở sàn 0/1 tỷ thì ghi "không đủ năng lực cho 50B".
- Theo dõi về sau (bằng chứng sạch duy nhất): user DUYỆT đăng ký 25/11. Ghi ô + điểm hi52 hàng tháng từ as-of 2026-11 bằng `calc/paper_cell_monthly.py` (display-only, không
  đụng sizing); đọc lần đầu khi nhãn 12 tháng đóng (2027-11). Entry registry + lệnh cron đề xuất chờ Mike duyệt (`PAPER_REGISTRY_PROPOSED.md`).
