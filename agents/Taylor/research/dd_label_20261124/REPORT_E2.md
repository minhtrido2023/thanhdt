# E2 — nâng cấp `bin/dd_history_label.py` theo quant-skeptic (CONFIRMED/medium) — job Taylor_20261124_034215

Display-only. Không sửa skill, không đổi luật 4 (cổng giá ≤0,85×tâm), không sizing, không email, không cron, không merge.
Nhánh `session/Taylor_20261124_034215`, worktree `wt-Taylor_20261124_034215`. REPORT_E.md giữ nguyên (bản v1).

## Kết quả
- **Nhãn v2 hạ mạnh**: v1 có 25 nhãn xác định (RẺ 17 / TRUNG TÍNH 5 / ĐẮT 3) + 11 KHÔNG CHẮC. v2 còn **8 nhãn xác định**
  (RẺ 5 / TRUNG TÍNH 3 / ĐẮT 0) + 28 KHÔNG CHẮC. **17/25 nhãn xác định bị hạ.** Không còn mã ĐẮT nào.
- Lý do hạ (17 mã): chỉ k ngoài dải **6** · chỉ N_eff<2,5 **9** · cả hai **2**. Tổng cờ k = 8, cờ N_eff = 11.
  (Cờ k bật ở 10 mã, nhưng CST và TCH vốn đã là KHÔNG CHẮC ở v1 nên không bị hạ thêm.)
- Mã còn nhãn xác định: DCM, DDV, PVT, TTA, VLB (RẺ); BSR, PVP, SZL (TRUNG TÍNH). VLB mang cờ ĐỈNH (ROE TTM/5Y 2,31).
- Bảng trước/sau 36 mã: `out/before_after_v2_2026-11-20.csv` (cột label_v1, label, reasons). Dòng hiển thị: `display_line()`.

## Đã làm (theo từng mục skeptic)
- **(a)** Hạ nhãn khi k_fade hoặc k_hold ∉ [0,5; 2] → `KHÔNG CHẮC (proxy lệch DD, k=a–b)`. Hằng số `K_BAND`, ghi rõ do skeptic
  đề xuất. Khớp đúng 10 mã skeptic nêu (CST, CSV, DGC, HHS, MVC, PAT, PNJ, QTP, TCH, TV1) — selfcheck 7a.
- **(b)** Cờ đối xứng `LỢI NHUẬN SỤT?` khi ROE TTM/ROE5Y ≤ 1/1,3 = 0,769. Sổ thật bật ở CST, DGC, HHS, PAT, PNJ. Cờ này
  chỉ **cảnh báo** (không hạ nhãn) như brief yêu cầu; 4 mã trong đó (DGC, HHS, PAT, PNJ) v1 là RẺ — cả 4 đã bị hạ nhờ cờ k.
- **(c)** Cổng `N_eff(hold) < 2,5` → `KHÔNG CHẮC (N hiệu dụng thấp, x,xx)`. Cổng 36 tháng thô vẫn giữ nhưng **không bao giờ
  ràng buộc** (min 53 tháng, PAT) — chỉ còn là chốt an toàn. Cổng N_eff mới mới là cổng ràng buộc thật.
- **(d)** Dòng hiển thị không còn "trung vị 10 năm ≈ …× tâm"; thay bằng "thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm
  DD". Docstring dòng 2-5 đổi thành "nhãn CƠ HỌC so với lịch sử chính mã". `giá/tâm` và `hist_med_*` vẫn ở CSV, ngoài dòng hiển thị.

## Sửa câu chữ REPORT_E (cho bản mới)
- **E:19** Hướng thiên lệch của cờ đỉnh: ĐẮT **3/3** có ⚠ đỉnh (MVC, NNC, TV2) vs RẺ **4/17** (SAS, TV1, VLB, QTP).
  Cờ đỉnh đi cùng nhãn ĐẮT, nên ĐẮT hay là hệ quả của ROE5Y thấp so với lợi nhuận hiện tại. MVC: ROE5Y = **6,94%** (đo
  từ panel) < r 13,5% ⇒ RI âm ⇒ proxy thấp ⇒ ĐẮT. Đó là proxy lệch chứ không phải tín hiệu giá đắt.
- **E:24-27** Số mã k ngoài [0,5; 2] = **10/36** (không phải "k<0,3 ở vài mã"; đề xuất đã thành cờ ở (a)).
- **E:98** k-bất-biến chỉ ảnh hưởng **THANG hiển thị** (hist_med theo bội số tâm), không ảnh hưởng nhãn v1. Nhưng ở v2 k
  ảnh hưởng **cờ hạ nhãn** (k ngoài dải) — tức là tâm DD vẫn chạm vào kết quả qua cờ này, theo hướng làm nhãn thận trọng hơn.
  Đo: FPT với tâm ×3 giữ nhãn v1 RẺ nhưng k_hold = 2,90 ⇒ bị hạ (selfcheck 7k).

## Độ nhạy (đo bằng `sensitivity_e2.py`; "giữ" = nhãn y hệt cấu hình gốc 10Y, tercile 33/67)
| Biến thể | giữ nhãn v1 | giữ nhãn v2 | trong 25 mã v1 xác định, giữ v1 |
|---|---|---|---|
| cửa sổ 5Y | 23/36 | 12/36 | 18/25 |
| cửa sổ 7Y | 27/36 | 13/36 | 22/25 |
| tercile 25/75 (thay 33/67) | 28/36 | 28/36 | 22/25 |
Số 23/27/28 trùng số skeptic nêu (đọc "cắt 25/75" = ngưỡng tercile 25/75; chưa xác nhận lại cách hiểu với skeptic). Nhãn v2
giữ ít hơn ở 5Y/7Y vì đổi cửa sổ làm N_eff (hold) đổi, kéo theo cổng N_eff bật/tắt — không phải nhãn gốc bất ổn thêm.

## Caveat SIP (đã đo, KHÔNG khớp số skeptic)
Brief nêu cổ tức tiền 4.500đ ex 19/11 trước asof 20/11 trong khi BVPS còn quý trước. Tôi trừ 4.500 khỏi BV/cp (23.726,
suy từ Price/PB) **chỉ ở dòng asof**, tâm + lịch sử giữ: p [fade 2, hold 13] → **[21, 39]**, nhãn v1 RẺ → KHÔNG CHẮC
(rẻ…trung tính). Skeptic nêu [2,13]→[8,21] và "nhãn RẺ giữ" — **không tái hiện được**; kết quả của tôi cho thấy
nhãn RẺ của SIP KHÔNG giữ nếu hiệu chỉnh đúng như vậy. Khác biệt có thể do cách hiệu chỉnh (khoản 4.500đ tôi lấy từ brief, chưa tự
đối soát nguồn cổ tức). Ở v2 SIP vốn đã KHÔNG CHẮC (N_eff 1,88) nên không ảnh hưởng nhãn hiển thị; cần skeptic xác nhận cách đo.

## Kiểm
- Selfcheck mở rộng 18 → **32 kiểm**, ALL PASS dưới `env -u TZ` VÀ `TZ=Asia/Ho_Chi_Minh` (output giống hệt ngoài dòng TZ).
  Mới: 7a-7l (cờ k-band khớp 10 mã; hạ nhãn; cổng N_eff; không hạ khi trong ngưỡng; biên cờ SỤT 0,76/0,78 và đỉnh 1,31/1,29;
  mutation nới/siết cổng; tâm ×3; dòng hiển thị sạch). 4d giữ (tâm ×1,3 ⇒ nhãn v1/phân vị không đổi — đổi so sánh từ `label`
  sang `label_v1` vì v2 phụ thuộc k).
- Parity D2: FPT k_hold 0,96637 / k_fade 1,6396 / giá/tâm 0,78518; VCB 0,67765 / 0,93869 / 1,4101 — như v1 (2b PASS).
- Tất định: CSV `dd_history_label_all` md5 `56ed118a3b7f7d4fe9fee116e8590a31` (chạy 2 lần trùng, cả trong selfcheck 6);
  before_after `73f38687…`, sensitivity `445e8e2b…` đều trùng 2 lần. threads=1.

## Caveat mang theo
Giữ nguyên caveat REPORT_E (k bất biến không kiểm được; Big-4 hồi tố; ROE5Y PIT chưa kiểm trước 2020; OShares/BVPS; proxy
"thô"; 1 mặt cắt 36 mã). Thêm: v2 chủ yếu là một thước **"KHÔNG CHẮC"** (28/36) — đó là hệ quả trung thực của N hiệu dụng ≈ 3
chu kỳ/10 năm, không phải lỗi. Ngưỡng 0,5/2 và 2,5 là do skeptic đề xuất, chưa tối ưu và không nên tinh chỉnh theo kết quả này.
Chỉ 8 mã còn nhãn xác định — nếu đưa vào DD, nên hiển thị như thông tin phụ, không dùng làm cổng.

## Tái lập
```
cd <wt>; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY bin/dd_history_label.py --all-ledger
$PY agents/Taylor/research/dd_label_20261124/sensitivity_e2.py
env -u TZ $PY bin/dd_history_label_selfcheck.py; TZ=Asia/Ho_Chi_Minh $PY bin/dd_history_label_selfcheck.py
```
