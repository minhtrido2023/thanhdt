# Nhánh 5 — `first_disclosure_datetime` có dùng làm ngày công bố cổ tức tiền (PIT) được không?

Job `Taylor_20261009_030802` · 2026-10-09 · READ-ONLY (không sửa production, không cron, không chạy event study).
Nguồn: `tav2_mike.corporate_action_snapshots` (52 vintage 2026-08-17→10-09; fd có từ vintage 09-15 = 25 vintage),
web (16/22 sự kiện mẫu có bằng chứng ngày, qua sub-agent tìm kiếm). Kế thừa + cập nhật study tiền khả thi
`../first_disclosure_feasibility_20260917/report.md` (3 vintage, chưa từng lên bus — nay đã thành 25 vintage).

## KẾT LUẬN: **(C) KHÔNG tin được làm ngày công bố PIT ⇒ giữ mốc 2027-08, snapshot chạy tiếp.**

Field là giá trị **hậu nghiệm, bị ghi lại, ngữ nghĩa không nhất quán**. Sai số ngày đo được (cả sớm lẫn muộn, hàng
ngày đến hàng tháng) lớn hơn chính cửa sổ sự kiện mà announcement study cần đo. Không có filter nào trong dữ liệu
tách được dòng đúng khỏi dòng sai (sai-muộn và sai-sớm đều trông "hợp lệ": fd < ex, fd ≤ record).

## 1. Độ ổn định qua vintage (từ 09-15)
`changed_values.csv`, `vintage_coverage.csv`
- DIV: 10.741 id có fd; **39 id (0,36%) đổi giá trị** — ISS 29/3.627, AIS/SUSP/MOVE 0.
- Hai dạng đổi:
  - **Đúng −7h (48 lần)**: vendor chuẩn hoá ICT-naive → UTC thật **khi dòng bị rewrite** (DGC/PNC 09-16, BIC 10-08 khi lật
    executed, AIG 10-06). ⇒ quy ước TZ trộn và **còn đang tự trôi** theo lịch rewrite, không theo batch cố định.
  - **Nhảy XA về phía sau khi vendor đổi `source_news_id`** (fd đi theo tin link mới nhất, không phải MIN): DIV ADP
    06-18→09-18, NTH 06-15→09-11→06-17→09-16 (lật qua lại 3 lần), DRL 07-06→09-30, DHC 07-03→09-25, MWG 07-16→09-25 (~+90
    ngày); ISS PGB +155 ngày, BAF +117. ⇒ **tên "first" không đúng**: fd bị ghi đè bằng tin muộn hơn.
- **Flap NULL**: 5 vintage (09-20, 09-22, 09-25, 10-04, 10-06) mất 130–670 giá trị rồi vintage sau có lại (1.646 lần
  val→NULL). Dấu hiệu vendor ghi 2 bước, snapshot chụp giữa chừng. ⇒ phải pin vintage, và không coi NULL là "không có".

## 2. Tính PIT + độ trễ vendor (sự kiện DIV mới, first_seen > 08-17) — `pit_new_div.csv`
| nhóm first_seen | n | có fd | seen−fd (ngày) p5/p50/p95 | **thấy TRƯỚC fd** | fd=public_date gốc | fd có ngay lúc first-sight |
|---|---:|---:|---|---:|---:|---:|
| 08-18..09-15 | 103 | 99 | −4 / +2 / +4 | **22 (22%)** | 52 | 1 (cột chưa tồn tại) |
| 09-16..10-09 | 73 | 55 | −2 / +2 / +5 | **7 (13%)** | 35 | **26/55** |
- "Thấy trước fd" = vendor đã có dòng sự kiện trong bảng TRƯỚC "lần công bố đầu" ⇒ fd **muộn hơn ngày thật**, bất khả thi
  nếu fd là PIT. Không dòng nào fd > ingested_at.
- fd chỉ có sẵn lúc dòng xuất hiện ở **26/55** sự kiện mới; còn lại được điền 1–N ngày sau ⇒ ngay cả với sự kiện mới, fd
  là **giá trị điền sau**.
- Độ trễ vendor (snapshot đầu tiên thấy − fd): median **+2 ngày**, p95 +5.

**Ca DGC (cổ tức 5.000 + 3.000 = 8.000đ, ex 2026-09-14)** — `dgc_history.csv`: vendor có 2 dòng từ vintage **09-06** với
`public_date` **09-03**; sau đó public_date bị ghi đè thành 09-08, và fd = **2026-09-08 17:34 ICT** (09-16 bị dời thành
10:34 UTC). ⇒ fd = ngày public_date đã ghi đè, **muộn ≥3 ngày** so với lúc vendor đã biết, ≥5 ngày so với công bố 09-03. **SAI.**
**Ca BIC (1.200đ, ex 10-07)**: thấy lần đầu 08-27 với public_date 08-28, fd = 08-24 17:23 ICT (10-08 dời −7h khi lật
executed). fd < first_seen, hợp lý — không bác được.

## 3. Đối chiếu nguồn ngoài (22 sự kiện DIV 2015–2025, 20 mã lớn) — `ext_sample.csv`, `ext_check.csv`
Tìm được bằng chứng ngày có nguồn cho 16/22. Năm 2015–2017 web gần như không còn tin (5/6 NA).
| kết quả so với bằng chứng công khai sớm nhất cho ĐÚNG khoản chi này | n |
|---|---:|
| Khớp ±1 phiên (BMP19, FPT21, BMP22, DPM23, FPT24, PNJ25, TCB25) | **7 (44%)** |
| fd MUỘN hơn (GMD18 +2, SAB24 +2, VNM21 ≥+3, PLX20 +8, PNJ22 +8 ngày) | **5 (31%)** |
| fd SỚM hơn hàng tuần–tháng — ngày ĐHĐCĐ/kế hoạch chứ không phải NQ chốt quyền (FPT17, SAB18, FPT19, PNJ23) | **4 (25%)** |
Một số "bằng chứng" là timestamp bài báo (proxy cho công bố), 2 dòng FPT là snippet chưa mở được trang — đã gắn nhãn.
Không tìm được ngày thông báo chính thức của HOSE/VSD cho dòng nào. Mẫu thiên về mã vốn hoá lớn (tin tốt nhất); mã nhỏ
khả năng còn kém hơn.

⇒ fd **không có một ngữ nghĩa**: lúc là ngày NQ HĐQT chốt quyền, lúc là ngày ĐHĐCĐ/kế hoạch, lúc là ngày tin được
crawl/public_date ghi đè. Sai cả hai chiều ⇒ không sửa được bằng một độ dịch hằng số.

## 4. Phủ — `coverage_by_year.csv`
- DIV có fd: 2014 **0%**, 2015 22%, 2016 78%, 2017 82%, 2018–21 93–97%, **2022 84%** (lỗ crawl tin), 2023–26 98–99%.
- Cổ tức CP (ISS có "cổ tức" trong issue_method): 2015 4%, 2016 35%, 2017 72%, 2018+ 82–99% ⇒ negative control STOCK_DIV
  bị mỏng hơn hẳn trước 2018.
- **Thiên lệch sống sót**: DIV của mã KHÔNG còn giá ở `ticker` từ 2026-05 (proxy hủy niêm yết) phủ thấp hơn mã còn sống:
  2016 61% vs 82%, 2017 71% vs 85%, 2022 74% vs 86%, các năm khác −3…−8pp. Thiếu có hướng ⇒ lệch về mã sống sót.
- `DATE(fd) = public_date` (chữ ký "chép public_date"): 24–47%/năm DIV.

## 5. Vì sao không chọn (B) "dùng có điều kiện"
Study 09-17 đề xuất (B) cho một nghiên cứu MÔ TẢ với 7 điều kiện. 3 tuần dữ liệu thêm làm yếu hẳn phương án đó:
(i) fd nhảy về sau khi đổi tin — không phải MIN, không ổn định ở cả sự kiện cũ; (ii) 25% mẫu web sớm hơn hàng tuần–tháng,
loại ca này không bị filter nào của 09-17 bắt (fd < ex, fd ≠ public_date); (iii) chỉ 44% khớp ±1 phiên. Với tỉ lệ sai
~56% và sai hai chiều, một kết quả "premium quanh ngày công bố" không phân biệt được với premium quanh ex-date mà study
proxy 09-04 đã đo. Chi phí chạy > giá trị thông tin.

## 6. Đường đi tiếp (không đổi)
- Snapshot tiếp tục; mốc mở lại **≥2027-08**. Ngày công bố PIT cho sự kiện MỚI nên định nghĩa
  `announce_pit = MIN(first_seen_snapshot, public_date tại first_seen)` — không dùng fd làm nguồn chính; fd chỉ là
  trường phụ (có sẵn lúc first-sight ở 26/55 ca).
- Lưu ý tính toán cho mọi consumer: `wc_env.sh` tự `cd` vào thư mục 8L ⇒ `source` nó trước khi `cd` vào thư mục làm việc.

## Files
`vintage_coverage.csv` · `changed_values.csv` · `q_pit_new.sql`/`pit_new_div.csv` · `dgc_history.csv` · `ext_sample.csv`
(mẫu từ BQ) · `ext_check.csv` (kết quả đối chiếu web + URL ở bus/REPORT) · `coverage_by_year.csv`.
