# PREREG-2 — "Pha đầu chu kỳ hàng hoá": ô R=P/MA12 cắt lên **1,05**, chân trời **3 tháng** (job Taylor_20261025_062825)

ĐÓNG BĂNG lúc commit file này (trước khi tracker được viết). Đây là **lần kiểm OOS TƯƠNG LAI DUY NHẤT**
cho ô (1,05 / 3M). Không đổi ngưỡng, chân trời, nhóm mã, đối chứng, tiêu chí sau khi thấy dữ liệu mới.
Muốn thử ô khác = PREREG-3 mới + số lần thử tăng, KHÔNG phải sửa file này.

## 0. Gốc gác và cách đọc
Ô này được **chọn sau khi thấy kết quả** (post-hoc, REPORT.md mục 2 của job Taylor_20261025_061240):
ô tốt nhất trong lưới 9 ô, 28 sự kiện / 11 cụm, TB cụm +12,0pp, Bonferroni×9 p=0,021; nhưng phai ở 6M
(+8,7pp, p_bonf 0,69) và lưới không đơn điệu ⇒ nghi nhiễu chọn ô. Biến thể ĐÃ GHI TRƯỚC (1,10/6M) trượt 6/6.
Dữ liệu 2014–2026-03 đã bị dùng để CHỌN ô ⇒ nó **không còn là bằng chứng**; chỉ dữ liệu theo §6 mới tính.
Chương trình là PAPER-ONLY: không lệnh, không sizing, không `trading_rules.json`, không plan.

## 1. Tín hiệu (copy nguyên từ `run.py` của job 061240, đổi duy nhất ngưỡng thành 1,05)
- Giá hàng hoá = WB CMO monthly (`data/_wb_cache/CMO-Historical-Data-Monthly.xlsx`, `feeds/commodity_wb_cmo.md`
  CANONICAL). Chuỗi: rubber `Rubber, RSS3` · crude oil `Crude oil, average` · urea `Urea ` · DAP `DAP` ·
  sugar `Sugar, world`.
- `R_m = P_m / mean(P_{m-11..m})`. **Sự kiện** tại tháng m ⇔ `R_m ≥ 1,05` VÀ `R_{m-1} < 1,05` VÀ không có
  sự kiện nào của cùng hàng hoá trong 12 tháng trước (`(m − last).n > 12`, `last` tính trên TOÀN lịch sử).
- Tín hiệu m chỉ biết được từ **ngày 11 tháng m+1** (PIT, giống bản gốc).

## 2. Nhóm phơi nhiễm / đối chứng (ĐÓNG BĂNG)
- Bản đồ: `commodity_map.csv` cùng thư mục, **md5 `cf4bef531aba172309e433113261b957`** (= file của job 061240,
  commit 103df32e4). Họ tham gia = các dòng `in_primary=Y`: rubber (DRI PHR DPR TRC GVR TNC DRG) · crude oil
  (PVS PVD PVC PVB GAS) · urea (DPM DCM) · DAP (DDV LAS) · sugar (SBT LSS SLS QNS). **KHÔNG thêm/bớt mã** sau
  khi thấy kết quả — kể cả MSR (không có chuỗi giá), cước (PVT…), thép, cá tra… Muốn thêm họ ⇒ PREREG-3.
- Chân phơi nhiễm = bình quân đều `Close_{t+63}/Close_t − 1` các mã của họ có `in_universe` (`universe_pit`)
  tại ngày vào t. Chân đối chứng = bình quân đều cùng phép đo trên mã `in_universe` tại t, cùng 2 chữ số đầu
  ICB (supersector) với họ, LOẠI mọi mã có trong bản đồ; < 5 mã ⇒ fallback toàn universe_pit trừ mã trong bản đồ
  (đánh dấu `fallback`). **X = r_exp − r_ctrl.** Giá = cột `Close` (điều chỉnh) của `data/bq_cache/ticker`.

## 3. Ngày vào lệnh (PIT) — quy tắc ĐÓNG BĂNG
- Sự kiện FORWARD (§6) được ghi vào sổ khi tracker thấy lần đầu (`first_seen`, ICT) và `first_seen` ≥ ngày 11
  tháng m+1. `entry_date` = **phiên giao dịch đầu tiên ≥ max(ngày 11 tháng m+1, first_seen + 1 ngày lịch)**.
  Tức nếu tracker chạy trễ thì vào lệnh trễ theo (không nhìn lùi giá).
- `first_seen` > ngày 11 tháng m+1 + **10 phiên** ⇒ `counts=False`, lý do `LATE` (sự kiện ghi nhưng KHÔNG vào N).
- Chân trời = **63 phiên** sau `entry_date` (cần đủ 63 phiên trong cache; thiếu ⇒ chưa trưởng thành, chờ).
- Sổ APPEND-ONLY: khoá (family, signal_month); giá trị lần đầu thấy là PIT, không ghi đè kể cả khi WB sửa giá.

## 4. Đơn vị độc lập và N kỳ vọng
- Đơn vị = **cụm**: sự kiện (khác hàng hoá) có `entry_date` cách nhau < 126 phiên gộp 1 cụm (xếp chuỗi, như bản gốc).
  Cụm mỗi cái = TB X của các sự kiện trong cụm. N thật = số cụm FORWARD `counts=True` đã trưởng thành.
- Lịch sử (đã đo từ `events_posthoc_105_3M.csv`): 28 sự kiện / 11 cụm trong 12,2 năm ⇒ ≈0,9 cụm/năm,
  SD giữa cụm = 0,1098 (11 cụm).
- **Trạng thái tại lúc đóng băng** (đo từ file WB 2026M09, `ước lượng` chỉ ở dòng "kỳ vọng"): sự kiện cuối cùng
  của mỗi họ: rubber 2026-02 · urea 2026-02 · crude 2026-03 · DAP 2026-05 · sugar 2026-08 ⇒ thời gian chết 12
  tháng khoá mỗi họ tới: rubber/urea tháng 2027-03 · crude 2027-04 · DAP 2027-06 · sugar 2027-09. Hơn nữa
  R hiện tại của crude 1,271 · sugar 1,215 · DAP 1,111 · rubber 1,13 đều đang Ở TRÊN 1,05 (urea 0,80 dưới) ⇒ họ
  trên ngưỡng phải rớt xuống <1,05 rồi cắt lên lại mới có sự kiện mới. **Kỳ vọng `ước lượng`: 0–2 cụm FORWARD
  tới hết 2027** (cấu trúc chặn, không chỉ ngẫu nhiên); ~3 cụm tới hết 2030.
- **MDE**: cần N cụm để power 80% (một phía 5%) với SD=0,1098: effect +12pp ⇒ N≈5,2 · +6pp ⇒ N≈21 · +5pp ⇒ N≈30
  (công thức `((1,645+0,84)·SD/effect)²`, đã tính). ⇒ Chương trình chỉ có khả năng xác nhận một effect LỚN (cỡ
  +12pp, tức đúng bằng giá trị đã chọn-ô, vốn nhiều khả năng bị thổi phồng); với effect thật cỡ +5–6pp thì
  KHÔNG BAO GIỜ đủ power trong chân trời thực tế. Khai trước: kết quả khả dĩ nhất là "không phân biệt được".

## 5. Tiêu chí (định lượng, ĐÓNG BĂNG). Chỉ tính cụm FORWARD `counts=True` đã trưởng thành.
- **SUCCESS** — chỉ được tuyên bố tại ngày xem xét CUỐI (§7), khi N ≥ **5** cụm, và TẤT CẢ:
  1. TB cụm của X ≥ **+5pp** và trung vị cụm > 0.
  2. Cận dưới CI90 bootstrap theo cụm (10.000 lần, seed 20261025) > 0.
  3. Số cụm X>0 ≥ 2/3 và sign test nhị thức một phía p < 0,10.
  4. LOCO: bỏ bất kỳ 1 cụm, TB còn > 0.
  5. TB X sự kiện > đường nền vô điều kiện 3M (đo ở review bằng đúng `measure` trên mọi ngày vào hàng tháng
     trong cửa sổ FORWARD, mix họ theo sự kiện) cộng ≥ +3pp.
  SUCCESS ⇒ chỉ là ứng viên R&D: cần quant-skeptic CONFIRMED + user duyệt trước mọi bước kế; vẫn KHÔNG tự wire.
- **FAIL (dừng sớm, hợp lệ ở MỌI ngày xem xét)**: N ≥ **3** cụm và TB cụm ≤ 0; HOẶC N ≥ 5 và bất kỳ điều kiện
  1–5 trượt. FAIL ⇒ đóng chương trình, ghi "ô 1,05/3M là nhiễu chọn ô", không tìm biến thể cứu.
  (Chỉ dừng sớm vì FAIL, không dừng sớm vì SUCCESS ⇒ không thổi phồng dương giả do optional stopping.)
- **DỪNG hết hạn**: tới ngày xem xét cuối mà N < 5 (và không FAIL) ⇒ **"KHÔNG PHÂN BIỆT ĐƯỢC (thiếu N)"**,
  đóng chương trình, KHÔNG gia hạn tự động, không dùng làm bằng chứng cho hay chống. Gia hạn = quyết định mới của user.
- Số tháng/sự kiện `counts=False` (LATE / PRE_FREEZE) KHÔNG bao giờ vào thống kê, kể cả khi "có lợi".

## 6. Cửa sổ FORWARD (luật khởi tạo — áp đúng, không chọn có lợi)
- Sự kiện FORWARD ⇔ **tháng tín hiệu m ≥ 2026-10 và ≤ 2030-09**. Tháng ≤ 2026-09 = **PRE_FREEZE**: dữ liệu
  đã có trước ngày đóng băng (2026-10-25), nằm trong hoặc sát mẫu dùng chọn ô ⇒ ghi sổ để minh bạch nhưng
  `counts=False`, KHÔNG vào N.
- Hệ quả áp dụng đúng luật cho các tín hiệu hiện hành mà Mike nêu: **đường (sugar) R=1,215 — cắt 1,05 ở 2026-08 ⇒
  PRE_FREEZE, không tính; DAP R=1,111 — sự kiện 2026-05 ⇒ PRE_FREEZE; cao su R=1,13 — sự kiện 2026-02 (đã nằm trong
  28 sự kiện chọn ô) và đang trên ngưỡng ⇒ không có sự kiện mới tới khi rớt <1,05 rồi cắt lên; crude 1,271 — sự kiện
  2026-03 ⇒ PRE_FREEZE.** Cả 3 sự kiện sau cửa sổ backtest (crude 2026-03, DAP 2026-05, sugar 2026-08) được ghi sổ
  `PRE_FREEZE_BACKFILL`, chỉ mô tả; kết quả của chúng KHÔNG được dùng để nâng/hạ niềm tin vào ô.
  Không có sự kiện FORWARD nào tại thời điểm đóng băng (N=0).

## 7. Ngày xem xét — KHÔNG xem thống kê trước mốc
- Tracker CHỈ ghi nhật ký (sự kiện + kết quả X từng sự kiện); **không in** TB/CI/p. Script verdict
  `commodity_cycle_forward_review.py` từ chối chạy trước ngày xem xét (trừ cờ ghi rõ).
- Các mốc: **2028-01-31 · 2029-01-31 · 2030-01-31** (chỉ áp luật FAIL dừng sớm) và **2031-01-31 = CUỐI**
  (signal cuối 2030-09 ⇒ entry ≤ 2030-10 + 63 phiên ≈ 2031-01). Verdict SUCCESS/DỪNG-hết-hạn chỉ ở 2031-01-31.
- Tác giả không được xem X của sự kiện FORWARD để quyết định bất kỳ thay đổi nào; chỉ kiểm tra tracker còn chạy
  (số dòng sổ, log BLOCKED).

## 8. Kiểm tra tái lập / ranh giới
- Không có NAV ⇒ không có self-check 0 VND; thay bằng selfcheck tracker: tái dựng 28 sự kiện chọn-ô từ code
  tracker khớp `events_posthoc_105_3M.csv` (family, sig_month, entry, X ≤ 1e-9) + mutation test.
- Rủi ro tồn dư khai trước: vintage WB (hiện tại, không phải tại thời điểm); cache `Close` điều chỉnh theo
  bản hiện tại; `universe_pit` từ 2013; phơi nhiễm thương mại thật của mã không chỉ là 1 hàng hoá.
- Cron: CHƯA cài (Mike/user quyết). Không có cron thì sổ không tích luỹ ⇒ mốc LATE sẽ loại sự kiện (§3).
