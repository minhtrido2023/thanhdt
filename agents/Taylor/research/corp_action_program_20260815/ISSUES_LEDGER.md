# ISSUES LEDGER — Sprint 1 (`Taylor_20260815_114954`, 2026-08-15)

Sổ ghi **quy tắc đã thử rồi KHÔNG dùng**, **sai sót của chính lần đo này**, và **câu hỏi chưa trả
lời**. Mục đích: người làm Sprint 2 không mất thời gian đi lại đúng ngõ cụt, và không trích nhầm
một con số đã bị chính tác giả bác bỏ.

---

## A. Quy tắc đã THỬ rồi LOẠI — kèm lý do đo được

| # | Quy tắc đã thử | Vì sao loại | Bằng chứng |
|---|---|---|---|
| A1 | Dedup theo `(ticker, exright_date, event_code)` | **Phá dữ liệu thật.** Gộp 404 nhóm DIV / 829 dòng, nhưng phần lớn là các ĐỢT cổ tức khác nhau cùng ngày ex. | PHN 2026-06-05: "2025 Đợt 3" 1.000đ **và** "2026 Đợt 1" 1.000đ — cùng giá trị, khác quyền, cả hai trả thật. Gộp = âm thầm chia đôi cổ tức. |
| A2 | Coi `value_per_share` khác nhau là dấu hiệu nhận biết đợt | Sai — có đợt **trùng giá trị**. `nv=1` (giá trị giống hệt) vẫn có 104 nhóm DIV là 2 đợt thật. | `out/dup_naive_key.csv`; mẫu PHN/CAT/ANV/BTT ở A1 |
| A3 | Dùng `event_title_vi` để **gán** subtype ISS | Tiêu đề được vendor **ghép máy** từ chính `issue_method_name_vi` (`"Phát hành cổ phiếu - " + tên [+ " tỉ lệ x%"]`) ⇒ không phải nguồn độc lập; "0 xung đột" là **vô nghĩa**, không phải xác nhận. | `SPRINT1.md` §4.1 |
| A4 | Suy subtype cho 15 dòng `BBOD` | Không có bằng chứng: `issue_method_name_vi`, `event_title_vi`, `event_description_vi` **đều NULL**, `exercise_ratio=0` trên cả 15. Đoán = biến lỗ hổng dữ liệu thành nhãn trông chắc chắn. | truy vấn trực tiếp; giữ `UNKNOWN`, chặn khỏi actionable (T7c) |
| A5 | Dùng `ref_price` làm giá tham chiếu ex-right | **NULL 100%** trên DIV và ISS. Chỉ tồn tại ở NLIS/MOVE (giá tham chiếu ngày niêm yết/chuyển sàn). | `out/missingness.csv` |
| A6 | `AIS.effective_date` thay `exright_date` để neo sự kiện | Lệch tới **~7 tuần** (FPT 2025: ex 07-21 vs AIS 09-12). | registry `corporate_action_bq.md` Bẫy (1), tái xác nhận |
| A7 | `id_created_date` (ObjectId) làm `known_date` | **89,4%** bản ghi tạo cùng ngày backfill 2024-10-11 ⇒ với đa số dòng nó chỉ là ngày vendor nạp lịch sử, không phải ngày thị trường biết tin. Giữ làm tie-break. | `out/id_creation_epoch.csv` |
| A8 | Coi `exercise_ratio` NULL/0 là "không pha loãng" | `0` là no-op im lặng — nhân `(1+0)` trông như đã tính. 42,3% dòng ISS rơi vào đây. Phải **fail closed**. | `out/ratio_zero_vs_null.csv` |
| A9 | Cắt mẫu từ 2014 để né `public_date` xấu | Không cứu được: tỉ lệ `public_date ≥ exright_date` **không phải tật của thời kỳ đầu**, vẫn còn ở các năm gần đây. | `out/pit_public_vs_exright_by_year.csv` |
| A10 | Coverage theo **sàn** (HOSE/HNX/UPCOM) | Bảng **không có cột sàn**. `icb_code_lv1` là mã NGÀNH. Không bịa bằng cách suy từ mã CK. | schema 35 cột, `SPRINT1.md` §3.2 |

---

## B. Sai sót của chính lần đo này — ghi lại để không ai trích nhầm

| # | Sai | Đúng | Bài học |
|---|---|---|---|
| B1 | So cổ tức (VND thô) với `Close` (đã hồi tố) khi kiểm bước điều chỉnh giá → báo **6,6%** khớp | Dùng `Price` **thô** làm giá cum → **85,4%** khớp trong ±0,2% | Đúng cái bẫy "trộn `Price` thô với `Close` hồi tố" mà dispatch cấm — tôi tự dẫm vào ở chính metric dùng để đánh giá dữ liệu. **6,6% là lỗi đo, KHÔNG được trích.** |
| B2 | `bq --format=json` render mọi số thành **chuỗi**; `exercise_ratio in (None, 0, 0.0)` không bao giờ khớp → báo **48** dòng ratio không dùng được | Ép kiểu bằng `ca_lib.num()` → **4.661** | Một bộ đếm sai kiểu **không báo lỗi** — nó trả về con số nhỏ trông "sạch". Đã đưa `num()` thành hàm bắt buộc + comment ngay chỗ dùng. |
| B3 | Dung sai chính xác tuyệt đối khi so tỉ lệ trong tiêu đề với cột số → báo **1.132 (17%)** lệch | Dung sai ±0,05pp (= đúng độ chính xác tiêu đề in ra) → **0 lệch / 6.669** | Kiểm tay 12 ca trước khi kết luận "17% dữ liệu mâu thuẫn". **17% KHÔNG được trích.** |
| B4 | Cộng nhầm tổng coverage theo năm (12.354) | 12.583 | Tổng phải tính bằng máy từ CSV, không cộng tay. |

---

## C. Câu hỏi CHƯA trả lời — chuyển sang Sprint 2 hoặc cho Winston

| # | Câu hỏi | Vì sao chưa đóng được | Đề xuất |
|---|---|---|---|
| C1 | **Tỉ lệ amendment/revision thật là bao nhiêu?** | Cần ≥2 vintage; hôm nay mới có 1. | Chạy lại `build_event_ledger.py` sau ~4 tuần, join 2 file vintage theo `id`, so `payload_sha1`. **Điều kiện cần để mở lại announcement study.** |
| C2 | **182 sự kiện DIV (2,1%) có cổ tức nhưng chuỗi giá KHÔNG điều chỉnh gì** — vì sao? | Chưa truy nguyên từng ca. | Sprint 2 lấy từ `out/div_price_step_detail.csv.gz` (`observed_factor ≈ 1`), kiểm 10 ca tay; nghi vấn: mã thanh khoản mỏng không có phiên giao dịch quanh ex-date. |
| C3 | **15 ca cổ tức > giá cum** (0,09%) — lỗi ở đâu? | Đã kiểm hết 15 ca (không còn là câu hỏi mở về phía cổ tức). Toàn bộ 15 ca chỉ thuộc **3 mã: DNN (9), BCB (4), PTX (3)**, với `Price` cum đứng ở **200 / 400 / 700 / 900đ** suốt nhiều năm — DNN giữ nguyên 200đ từ 2021→2025. ⇒ hỏng ở **chuỗi GIÁ**, không phải ở `value_per_share`. | Báo Winston/bq_admin về `ticker.Price` của DNN/BCB/PTX. Sprint 2 loại 3 mã này hoặc lọc `cum_price_raw < 1.000đ`. |
| C4 | **Ai là writer của bảng, cadence thật ra sao?** | Mới có 3 batch để suy (08-12 / 08-13 / 08-14). `MAX(ingested_at)` lúc chạy job = `2026-08-14 15:49 UTC`; **chưa có batch 08-15 — nhưng đó là BÌNH THƯỜNG**, cửa sổ nạp đo được là 22:22–22:48 ICT còn job này chạy ~19:00 ICT. **Không kết luận là đứt feed.** | Winston theo dõi `MAX(ingested_at)` vài ngày để có cadence thật; mọi consumer vẫn phải tự gọi freshness check, không suy từ lịch. |
| C5 | **`value_per_share` có khớp tiền THẬT về tài khoản không?** | Sprint 1 chỉ đối soát với chuỗi giá, chưa với sổ broker. | Đối soát với `cashDividendReceiving`/sao kê DNSE cho vài mã đang giữ. §21 `coding_guidelines` **không đổi** cho tới khi có kết quả này. |
| C6 | **Coverage theo sàn** | Không có cột sàn (A10). | Nối nguồn khác nếu cắt theo sàn thực sự cần cho kết luận; nếu không thì bỏ chiều này. |
| C7 | **Cụm theo mã trong thống kê** — 3.032 sự kiện trên universe PIT nhưng bao nhiêu mã độc lập? | Chưa đo. | Sprint 2 phải khai N theo **số mã/số sự kiện độc lập**, không phải số dòng (`coding_guidelines` §18 / skill `quant-research`). |
| C8 | Thuế cổ tức 5% TNCN | `div_total_on_exdate` là số **GỘP**. | Sprint 2 quyết định nghiên cứu trên gộp hay ròng và **nói rõ** trong mọi kết luận. |

---

## C-bis. Trạng thái các câu hỏi C sau Sprint 2 (`Taylor_20260815_121850`)

| # | trạng thái sau Sprint 2 |
|---|---|
| C1 amendment | **CÒN MỞ.** Sprint 2 neo `exright_date` nên không phụ thuộc; announcement study **vẫn CẤM**. Chạy lại `build_event_ledger.py` ≈ **2026-09-12** để có vintage thứ 2. |
| C2 182 ca không có bước điều chỉnh | **CÒN MỞ.** Sprint 2 **chặn** chúng khỏi mẫu bằng bộ lọc X4 (loại 694/6.549 ca hệ số không xác định hoặc không ổn định) nhưng **KHÔNG truy nguyên**. Chặn ≠ giải thích. |
| C3 DNN/BCB/PTX | **ĐÃ ÁP DỤNG** — loại cứng trong X2 (selfcheck T11). Vẫn cần báo Winston về `ticker.Price`. |
| C5 đối soát tiền thật | **CÒN MỞ.** `coding_guidelines` §21 **không đổi**. |
| C6 coverage theo sàn | **ĐÓNG — bỏ chiều này.** Không có cột sàn; Sprint 2 không kết luận gì theo sàn. |
| C7 N theo mã độc lập | **ĐÓNG.** Mọi thống kê khai N theo **sự kiện + số mã + số tháng** (P-CORE: 2.619 / 465 / 150); CI dùng block bootstrap theo tháng ex-date. |
| C8 thuế cổ tức 5% | **ĐÓNG.** Nghiên cứu chạy trên số **GỘP**, nói rõ ở mọi kết luận; phép trừ thuế chỉ xuất hiện ở đúng một chỗ — cổng screening §6 của `SPRINT2_CASH_DIVIDEND.md`. |

## E. Sai sót của Sprint 2 — đầy đủ ở `SPRINT2_DEVIATIONS.md`

| # | sai | bài học |
|---|---|---|
| E1 | Selfcheck **T27** viết sai: assert "CI block-bootstrap rộng hơn CI theo sự kiện" trên dữ liệu tổng hợp **không có tương quan trong block** → FAIL. | Giả thuyết đầu tiên khi selfcheck fail là **"tôi viết sai test"**, không phải "code sai". Đã sửa test (thêm cú sốc chung theo block → 7,07×) + thêm T27b đo trên dữ liệu THẬT (1,46×). Không đụng estimator. |
| E2 | Prereg ngầm định **null của pipeline = 0**; placebo R5 trả về **+1,18% có ý nghĩa** → giả định sai. | Placebo tồn tại đúng để bắt chuyện này. Đã thêm baseline XA (R7, `ex−250`) + estimator ghép cặp (deviation D3), và **giữ primary ở bản THÔ** vì R7 không sống sót Holm. |
| E3 | `Index.level()` bản đầu ném `TypeError` khi gặp ngày thiếu (sự kiện chưa có T+h). | Đã sửa để trả **NaN** (fail-safe: sự kiện thiếu giá phải rơi khỏi mẫu, **không** được mượn giá phiên lân cận). Selfcheck **T22** khoá hành vi này. |

## D. Ranh giới đã giữ

- Không sửa gì ngoài `agents/Taylor/research/corp_action_program_20260815/`.
- Không tạo/sửa bảng, view, cron, trading rule, report pipeline, production code.
- Chỉ đọc `corp_action_lib.py` của cây chính (import read-only trong selfcheck T1) — không sửa.
- Không dispatch agent khác. Không chạy Sprint 2. Không wire tín hiệu nào.
