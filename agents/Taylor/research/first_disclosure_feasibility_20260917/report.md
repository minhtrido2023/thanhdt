# first_disclosure_datetime — kiểm định khả dụng cho Announcement Day (NHÁNH B, READ-ONLY)

Ngày 2026-09-17 · Nguồn: `tav2_bq.corporate_action` (36.373 dòng, đọc 2026-09-17), `tav2_mike.corporate_action_snapshots`,
`tav2_bq.stock_news`, `tav2_bq.ticker_prune`. Không ghi BQ, không commit, không ghi bus.
Chạy lại: `run.sh qNN_*` (từng SQL) → `python3 analyze.py` → `python3 feasibility.py`.

## TL;DR — **CHƯA UNBLOCK. Tối đa: UNBLOCK CÓ ĐIỀU KIỆN cho một nghiên cứu MÔ TẢ, định nghĩa lại event.**
Field có ích (DIV phủ ~95%+ từ 2018, gần như không vi phạm ex-date), nhưng có 4 lỗi đã chứng minh bằng artifact:
1. **Là giá trị hậu nghiệm, KHÔNG PIT**: toàn bộ 36.373 dòng được ghi lại 1 batch 2026-09-13 18:13 UTC; `stock_news`
   (nguồn tin) cũng crawl 1 lần 2026-09-02/09-13, bắt đầu đúng 2015-03-02 = MIN(fd). Field **bị sửa giữa các vintage**
   (58 lần sửa trong 2 vintage 09-16/09-17).
2. **Sai-muộn khi public_date bị ghi đè**: trên 111 sự kiện DIV có public_date bị ghi đè quan sát được qua snapshot,
   fd = **public_date ĐÃ GHI ĐÈ (muộn)** ở **31 (28%)**, lọt giữa gốc và ghi đè thêm 12 (11%); 19 sự kiện có
   **snapshot thấy sự kiện TRƯỚC fd** (bất khả thi). Case động lực **DGC** sai: vendor có dòng từ vintage 09-06 với
   public_date 09-03, fd = 2026-09-08.
3. **TZ trộn 2 quy ước**: batch lịch sử lưu giờ ICT dán nhãn UTC; từ ingest 2026-09-16 các dòng mới đổi sang UTC thật (−7h).
4. **Ngữ nghĩa ≠ "ngày công bố cổ tức"**: lead median 13 ngày trước ex-date, tin link toàn là "Ngày ĐKCC trả cổ tức" —
   tức là thông báo chốt quyền, không phải NQ ĐHĐCĐ/HĐQT phê duyệt mức cổ tức.

## 1. Coverage (q01, q02, q03)
| event_code | n | fd non-null | sid non-null | fd có mà sid NULL | sid có mà fd NULL |
|---|---:|---:|---:|---:|---:|
| DIV | 17.187 | 10.693 (62%) | 9.149 | 1.765 | 221 |
| ISS | 11.747 | 3.610 (31%) | 3.848 | 858 | 1.096 |
| AIS | 4.935 | 1.233 (25%) | 3.136 | 229 | 2.132 |
| SUSP / MOVE / NLIS / MA | 685/431/1.371/17 | 227/39/31/4 | 498/288/624/7 | | |

DIV theo năm exright (fd %): ≤2014 **0%** · 2015 21% · 2016 78% · 2017 82% · 2018 93% · 2019 95% · 2020 97% · 2021 97% ·
**2022 83%** · 2023 98% · 2024 98% · 2025 99% · 2026 98%. MIN(fd) = 2015-03-02 cho mọi code.
Theo status DIV: announced 84/115 (73%), executed 10.609/17.072 (62%, do phần trước 2015).
- Dip 2022 trùng dip số tin `stock_news` (2021: 11.248 tin → 2022: 3.958) ⇒ coverage phụ thuộc crawl tin.
- `ingested_at`: 36.261/36.373 dòng = batch 2026-09-13 18:1x UTC; sau đó chỉ 14/10/583 dòng ingest 09-14/15/16.
  ⇒ **backfill một lần** (không suy được dòng nào có fd từ lúc thật). Snapshot: vintage ≤09-13 fd = 0 (cột NULL do
  ALTER), **vintage đầu có fd = 2026-09-15** (15.823 dòng), 09-16: 15.827, 09-17: 15.837.

## 2. Lead time & TZ (q06, q07, analyze_output.txt)
Lead = exright − DATE(fd) (đọc fd như giờ ICT, xem TZ bên dưới):
| code | n | p5 | p25 | median | p75 | p95 | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIV vs exright | 10.636 | 5 | 9 | 13 | 19 | 39 | 16,3 |
| DIV vs record | 10.636 | 6 | 11 | 15 | 21 | 41 | 17,8 |
| ISS vs exright | 3.210 | 5 | 13 | 25 | 57 | 95 | 37,7 |
DIV median ổn định 12–15 ngày mọi năm 2015–2026.

**TZ**: phân bố giờ (UTC-label) đỉnh 08–11h và 13–17h, **trũng đúng 12h** ⇒ là giờ hành chính VN ⇒ batch lịch sử
lưu **giờ ICT dán nhãn UTC**. Nếu áp `DATE(fd,'Asia/Ho_Chi_Minh')` như đề bài sẽ dời ngày **3.161/15.837 dòng** (giờ ≥17h).
Nhưng dòng ingest 2026-09-16 cho sự kiện 09/2026 xuất hiện giờ 01–05 UTC, và q05 thấy **33 dòng bị dời đúng −7h** giữa
vintage 09-15→09-16 (ACG 17:10→10:10, DGC 17:34→10:34, SBM 08:09→01:09…) ⇒ vendor vừa đổi sang UTC thật cho dòng mới.
**Quy ước hiện TRỘN**; 80% timestamp có giây=0 (độ phân giải phút kiểu trang tin).

## 3. PIT nghiêm ngặt (pit_violations_all.csv — 440 dòng)
| code | fd>ex | fd=ex | fd>record | fd=record | DATE(fd)>public_date | fd>ingested_at |
|---|---:|---:|---:|---:|---:|---:|
| DIV | **0** | 1 (CTT 6708f3e40ec61045ab7fc5a2, ex 2018-09-20) | 0 | 0 | 236 | 0 |
| ISS | 76 | 13 | 76 | 14 | 86 | 0 |
| AIS/SUSP/MOVE/NLIS | – | – | SUSP 2 | – | 18/4/3/6 | 0 |
(Đọc theo UTC→ICT: DIV fd>public tăng lên 619, fd=ex 2.)
Ví dụ ISS: APH 6708f3f50ec61045ab8001cb fd 2020-12-18 vs ex 2018-02-28 (−1.024 ngày); CII 6708f3f60ec61045ab800376 −24;
FSC 6708f3f30ec61045ab7ffbf7 −21 — đều là fd = public_date (ngày cập nhật sau), không phải công bố.
Không dòng nào fd > ingested_at. **DIV "0 dòng sau ex-date" đúng — nhưng không chứng minh PIT** (xem §4a, §4e).

## 4. Case SAI
**(a) fd trùng ngày public_date**: DIV 3.676/10.693 = **34,4%** (ISS 12%, AIS 20%, SUSP 32%). Nhóm này lead median
**8 ngày** (41,5% ≤7 ngày) so với 15 ngày ở nhóm fd<public (3,3% ≤7) ⇒ khớp chữ ký "chép public_date". Tỉ lệ 34% lịch sử
gần bằng tỉ lệ 28% "fd = public_date đã ghi đè" đo được trực tiếp ở §4e ⇒ nghi phần lớn là lỗi, không kiểm chứng được từng dòng.

**(b) Dùng chung**: 1.072 nhóm (ticker, sid) >1 dòng (2.393 dòng; phần lớn DIV/ISS cùng một tin — hợp lý), nhưng
**8 nhóm DIV trải ≥2 ex-date khác nhau** (26 dòng): KWA sid 11406437 cho 6 kỳ cổ tức 2018–2023; MTX 11296163 5 kỳ;
CCC 11262486 4 kỳ; BMK 11407611 3 kỳ (`div_shared_sid_distinct_exdates.csv`). (ticker, fd) trùng qua ≥2 ex-date:
**116 nhóm / 239 dòng** DIV (ADP 2017-09-19 08:56 cho ex 2017-09-28 và 2017-12-07; ANV 2019-03-20 cho ex 04-11 và 06-26…)
— có thể đúng (1 NQ 2 đợt) nhưng fd khi đó là ngày NQ, không phải công bố đợt 2. 16 sid dùng cho >1 ticker.

**(c) Join sid→stock_news.news_id** (INT, cast STRING): DIV 8.787/9.149 join được (96%), 8.776 cùng ticker; ISS 2.373/3.848;
AIS 518/3.136; MOVE 0/288. Tiêu đề: 100% tin DIV join được có từ khoá cổ tức/ĐKCC (mẫu 16 dòng, `news_title_sample.csv`:
"TQN: Ngày đăng ký cuối cùng trả cổ tức bằng tiền mặt", "CLW: Thông báo ngày ĐKCC chi trả cổ tức đợt 1 năm 2024"…) ⇒ tin
đúng chủ đề. Nhưng **public_datetime của tin = fd chỉ 3.229 (37%)**; **5.515 (63%) tin muộn hơn fd** (median +5,9 ngày,
p95 +22) — vd DHG 6708f3e20ec61045ab7fbd5e fd 2017-03-27 vs tin 2017-04-25; PJC fd 2021-02-24 vs tin 2021-03-09.
⇒ `source_news_id` KHÔNG phải tin sinh ra fd; fd lấy MIN từ nguồn khác không truy vết được (1.765 DIV có fd mà không có sid).
public_datetime của tin trùng giá trị fd theo giờ ICT-naive (không lệch 7h) — xác nhận §2.

**(d) Lead bất thường**: DIV: 0 dòng >180, 0 âm; max lead DIV 142 ngày. ISS: 29 dòng >180, 76 âm (`abnormal_lead.csv`).

**(e) So vintage** (q11, q13, `snapshot_firstseen_vs_fd.csv`): 112 sự kiện first_seen > 2026-08-17 (không bị kiểm duyệt trái)
có fd: DIV (n=106) first_seen − fd median +2, p5 −3, p95 +5 ngày. **19 DIV có first_seen < DATE(fd)** — vendor đã có dòng
trước "lần công bố đầu": BLN 6a9226ef1578f9da77bdce0e (thấy 08-30, pd gốc 08-28, fd 09-03), DGC 6a9b613c1578f9da77c882c1/c2
(thấy 09-06, pd gốc 09-03, fd 09-08), TW3, DVN, GTA, SBM, ACG, PVP, VLA, LPT, AVC, PMB, TSG, PHR, TFC, BMI, MVC, DTP.
Sự kiện có public_date bị ghi đè qua vintage (194; 175 có fd): DIV fd = pd GỐC 52 · fd < pd gốc 16 · **fd giữa 12 ·
fd = pd ĐÃ GHI ĐÈ 31**. ISS: 10 / 21 / 25 / 8.
Revision fd (q05): 09-15→09-16: 45 dòng (33 dời −7h; NTH 6aa49b5303bfaa031b0c5639 fd 06-15→09-11→06-17 qua 3 vintage;
FPT ISS 06-15→06-29; KHX ISS fd bị xoá); 09-16→09-17: 13 dòng (chủ yếu sid điền/đổi).

## 5. Khả thi cho `cash_dividend_announcement_premium_20260904`
Sprint gốc không đặt ngưỡng N cứng; mốc tham chiếu = gate proxy cùng thư mục: N=434 (IS 2014-19 = 136, OOS = 298),
tiêu chí prereg H1 Wilcoxon p<0,05 median >+1%, cluster theo ticker, LOYO. Sprint proxy dùng toàn bộ mã có giá; bảng dưới
cả hai universe. DIV `value_per_share>0`, không `not_executed`, ex 2014-01→2026-09.
Loại: PIT (fd≥ex, fd>record, DATE(fd)>public_date, ex NULL) · fd=public_date · (ticker,sid)/(ticker,fd) dùng chung qua ≥2 ex-date · lead>120.

| universe | seg | DIV | có fd | hợp lệ | dedup mã×quý | mã | tuần công bố | max share 1 tuần |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ticker_prune (ex±30d) | IS 2014-19 | 1.093 | 796 | 591 | **562** | 218 | 207 | 2,0% |
| ticker_prune | OOS 2020+ | 1.374 | 1.348 | 1.031 | **1.004** | 280 | 309 | 1,2% |
| mọi mã | IS 2014-19 | 6.188 | 4.072 | 2.087 | 2.017 | 779 | 231 | 1,9% |
| mọi mã | OOS 2020+ | 6.864 | 6.562 | 4.460 | 4.350 | 1.055 | 347 | 1,0% |
Theo năm (prune, hợp lệ): 2014 **0** · 2015 29 · 2016 127 · 2017 148 · 2018 146 · 2019 141 · 2020 149 · 2021 185 · 2022 135 ·
2023 139 · 2024 163 · 2025 168 · 2026 92 (`feasibility_by_year.csv`). Nếu giữ dòng fd=public: prune IS 733 / OOS 1.326.
Lead các sự kiện hợp lệ (prune): median 16, p5 9, p95 50 ngày; 404/1.622 không có sid.

**Về N**: đủ và dư so với mốc 136/298 — kể cả sau gate regime/yield/prior_3y (ước chừng bằng tỉ lệ gate cũ 434/10.876 ≈ 4%
thì prune chỉ còn ~25/~40 ⇒ **gate hẹp trên prune thì THIẾU**; toàn mã thì ~80/~175). Clustering theo tuần không đáng lo
(≤2%/tuần). **Nhưng N không phải điểm nghẽn — độ đúng của ngày mới là nghẽn.**
IS thực chất là 2016-19 (2014 = 0, 2015 = 29).

**Rủi ro còn lại (không loại được bằng filter):**
- **Hậu nghiệm/survivorship**: fd dựng từ crawl tin 2026-09 (coverage theo năm bám số tin crawl được; dip 2022). Sự kiện
  mà tin gốc đã mất khỏi web sẽ có fd muộn hơn (lấy tin kế tiếp) hoặc NULL — lệch có hướng về phía "fd muộn".
- **Sai-muộn không nhận diện được trong lịch sử**: loại fd=public_date bắt được nhóm 28%, nhưng nhóm "giữa" (11% mẫu 2026)
  và "snapshot thấy trước fd" vẫn lọt. Ước lượng thô từ mẫu 2026: ~15% sự kiện còn lại có fd muộn hơn ngày thật (12/80),
  mẫu nhỏ, chỉ gồm sự kiện CÓ ghi đè — không suy rộng chắc được.
- **Sai khái niệm**: fd ≈ ngày thông báo ĐKCC/NQ HĐQT (median ex−13…16 ngày), không phải ngày ĐHĐCĐ duyệt mức cổ tức
  (thường sớm hơn hàng tháng). Cửa sổ proxy cũ [ex−14, ex−1] đã chứa median fd ⇒ nghiên cứu mới gần như là tách
  cửa sổ proxy cũ ra trước/sau fd, không phải một thông tin mới hoàn toàn.
- **TZ trộn** + tin sau 15h ICT ⇒ ngày phản ứng phải là phiên kế tiếp; 471 sự kiện hợp lệ prune có ngày khác nhau giữa 2 cách đọc TZ.
- **Field không ổn định**: vendor đang sửa fd/sid/TZ hằng ngày ⇒ mọi kết quả phải pin vintage snapshot cụ thể (vd 2026-09-17).

## 6. Kết luận
**CHƯA UNBLOCK cho H1/H2/H3 như prereg** (announcement_day PIT). Có thể **UNBLOCK CÓ ĐIỀU KIỆN** một nghiên cứu mô tả,
nhãn rõ "record-date-notice day (vendor first_disclosure, hậu nghiệm)", nếu đủ TẤT CẢ:
1. Đọc từ `corporate_action_snapshots` pin 1 vintage (≥2026-09-17), không đọc bảng live.
2. Loại: fd≥exright, fd>record, DATE(fd)>public_date, **fd = public_date**, (ticker,sid)/(ticker,fd) dùng chung qua ≥2 ex-date, lead>120.
3. Chuẩn hoá TZ theo quy ước từng batch (ICT-naive cho dòng lịch sử; UTC cho dòng đã bị dời −7h) — xin vendor/bq_admin xác nhận
   quy ước chính thức trước; tin ≥15:00 ICT → ngày phản ứng = phiên kế.
4. Negative control bắt buộc như sprint proxy (STOCK_DIV ISS cùng định nghĩa fd) + kiểm độ nhạy: kết quả phải giữ khi (i) giữ
   nhóm fd=public, (ii) dịch fd sớm hơn 1–5 phiên (mô phỏng lỗi sai-muộn).
5. IS = 2016-19 (khai rõ 2014-15 thiếu), OOS 2020+; nếu dùng gate regime/yield thì dùng universe mọi mã (prune quá mỏng sau gate).
6. Xin vendor/bq_admin: định nghĩa fd (nguồn, min của tin nào), vì sao 37% không khớp tin link, có lấy thời điểm crawl hay thời điểm
   đăng tin; và xác nhận có sửa ngược lịch sử không.
7. Kết quả chỉ "định hướng"; không wire production trước khi snapshot tích luỹ fd PIT thật (theo dõi fd của sự kiện first_seen >2026-09-15,
   so với ngày tin thật) — quant-skeptic CONFIRMED vẫn là điều kiện cần.

## Giới hạn
- Snapshot có fd chỉ 3 vintage (09-15..17) ⇒ §4e dựa trên sự kiện 08-17→09-16, n≈106 DIV, thiên về sự kiện gần đây.
- "fd = public_date ⇒ lỗi" là suy luận thống kê (khớp tỉ lệ + lead ngắn), không kiểm chứng từng dòng bằng nguồn ngoài.
- ticker_prune membership = có ≥1 ngày trong prune trong [ex−30, ex]; không kiểm giá/thanh khoản như gate cũ (c14≥10k…).
- Không đối chiếu tin gốc trên web (HOSE/HNX) cho mẫu; không chạy outcome/return nào.

## Files (`/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/first_disclosure_feasibility_20260917/`)
SQL+CSV: q01_overview · q02_coverage_year_status · q03_ingest_pattern · q04_snapshot_vintages · q05_fd_revisions · q06_hour_of_day ·
q07_tz_recent · q08_news_join · q10_master_extract · q11_snapshot_first_seen · q12_prune_membership · q13_public_date_overwrites.
Phân tích: analyze.py → analyze_output.txt, pit_violations_all.csv, abnormal_lead.csv, fd_vs_news_join.csv, news_title_sample.csv,
div_shared_sid_distinct_exdates.csv, div_shared_fd_distinct_exdates.csv, snapshot_firstseen_vs_fd.csv · feasibility.py →
feasibility_by_year.csv, feasibility_is_oos.csv, div_events_flagged.csv · run.sh.
