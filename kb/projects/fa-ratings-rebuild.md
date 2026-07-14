# fa_ratings/8L re-tune + rebuild builder
> Dự án đã đóng — tách khỏi context_pack 2026-07-12. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. Re-tune 8L NO-GO (16/16); rebuild fa_ratings builder HOÀN TẤT, BQ-write-identity fixed.

## fa_ratings → fa_ratings_8l: user CHỐT hướng (c) — dự án re-tune SIGNAL_V11 bucket trên 8L (2026-07-11)

**Quyết định user (không phải quyết định thay user)**: sau khi backtest drop-in swap bị bác (cả 2
mapping tier8l/rating8l đều kém baseline R3, OOS -3.55pp/-2.20pp, LOO âm mọi năm — xem finding
Taylor_20260711_094714, quant-skeptic CONFIRMED), user chọn **hướng (c): re-tune bucket logic
SIGNAL_V11 trên nền thang rating gốc của 8L (1-5), coi đây là ứng viên THAY THẾ CORE thật sự nếu
kết quả tốt** — KHÔNG chọn (a) giữ static vá tạm, KHÔNG chọn (b) hybrid fallback chắp vá. Lý do user
nêu rõ: "return phải dựa trên dữ liệu thật và đầy đủ... không né tránh... không dùng bất kỳ hình
thức nào chỉ để chữa cháy mà không giải quyết vấn đề tận gốc."

**Đây là dự án R&D đầy đủ, không phải patch nhanh** — 3 giai đoạn user yêu cầu: (1) team bàn luận
cẩn thận lên plan, (2) chuẩn bị dữ liệu tốt, (3) cập nhật lại model. Đang ở giai đoạn 1+2 song song:
- Taylor (fable, dispatch async): thiết kế phương pháp re-tune bucket (C/D momentum vs A/B
  compounder vs E avoid) trên thang rating 8L gốc — không map cưỡng ép sang A-E như thử nghiệm vừa
  bác. Phải theo đúng multiple-testing discipline (N trials khai báo, DSR/PBO, walk-forward IS/OOS,
  per-year LOO) trước khi coi là ứng viên production.
- data-ops/Winston (dispatch song song): chuẩn bị dữ liệu — fix cadence refresh `fa_ratings_8l`
  hiện đang THỦ CÔNG (lần cuối 06-20), đây là rủi ro đã bị nhắc lại nhiều lần (mọi finding trước đều
  flag "nếu migrate mà không wire refresh tự động = đổi bảng đóng băng lấy bảng đóng-băng-chậm-hơn").
  Đề xuất cron + freshness-check, KHÔNG tự cài crontab — trình diff cho user duyệt trước.

**Deadline nghiệp vụ thật vẫn còn nguyên**: `fa_ratings` đóng băng 05-10, sẽ sai dần khi BCTC
Q2/2026 về (~cuối tháng 7) — dự án này cần có tiến độ rõ trước đó, dù không cần vội đổi ngay hôm nay.

**Trước khi wire production**: bắt buộc qua đủ walk-forward IS/OOS + DSR/PBO + LOO + quant-skeptic
CONFIRMED + user sign-off cuối cùng — không khác gì mọi thay đổi signal khác trong hệ thống.

**Tiến độ (2026-07-11, cùng ngày, làm nhanh theo yêu cầu ưu tiên của user):**
- Cron weekly refresh `fa_ratings_8l` (Winston đề xuất) → **user duyệt + đã cài** (commit dd7feb9,
  thứ Bảy 08:30 ICT). Test tay thất bại vì phiên interactive Mike dùng service account read-only
  (`bq-reader-8l`) — CHƯA rõ cron thật (crontab) chạy identity nào, xác nhận quanh lần chạy đầu
  tiên **thứ Bảy 07-18**.
- **Phase 0 XONG — CP0 = GO** (quant-skeptic CONFIRMED, high confidence): attribution ladder tách
  được degradation của lần drop-in trước = do THANG ĐO (−2.29pp FULL/−4.34pp OOS), còn coverage
  rộng hơn của 8L thực ra DƯƠNG (+0.88pp FULL/+1.34pp OOS) → giữ full coverage, dồn thiết kế vào
  bucket rating=GATE theo ngữ cảnh. Lưu ý cần mang sang Phase 2: hiệu ứng coverage dương tập trung
  nhiều ở năm 2021 — cần LOO loại bỏ năm đó trước khi tin hẳn.
- **Phase 1 XONG — CP1 = PASS**: family 12 config đo bằng proxy BQ thật, 12/12 vượt baseline OOS.
  **User đã chọn 3 finalist đưa vào Phase 2: F12_dvr_23, F1_gate_lean, F6_n_strict** (N-ledger đã
  đóng 16/16 — Phase 2 chỉ kiểm chứng lại, không mở thêm trial mới).
- **Chỉ đạo user cho Phase 2 (quan trọng)**: đánh giá phải nhìn TỔNG THỂ — cách 3 finalist phối hợp
  với nhau và với framework hiện có, không chỉ so OOS đơn lẻ. Làm tuần tự, kiểm chứng chắc chắn từng
  bước trước khi qua bước sau — tránh làm ẩu phải sửa lại sau.
- **Phase 2 XONG — CP2 = NO-GO CẢ 3 FINALIST** (quant-skeptic CONFIRMED, high confidence, tự tái
  lập khớp chính xác). F1/F6/F12 đều fail tiêu chí OOS + LOO (âm mọi năm kể cả ex-2021) + tail. Root
  cause: trục MOMENTUM_N (kênh entry chính của BAL dưới NEUTRAL — state phổ biến nhất DT5G) gãy vì
  thang rating 1-5 không tái tạo được "quality filter ngầm" mà tier C/D cũ vô tình tạo ra (loại được
  junk nhỏ mà rating không loại được). F12 kết quả full-năm đẹp thực ra bị kéo bởi 1 năm outlier 2021
  (+20.95pp riêng năm đó) — đúng lo ngại quant-skeptic nêu từ Phase 0.
- **KẾT LUẬN DỰ ÁN hướng (c)**: đã đo trung thực và bị bác — re-tune bucket trên thang 8L gốc (theo
  đúng pre-registered family, N=16/16, không mở thêm trial) KHÔNG cho ra ứng viên thay core khả thi.
  Quy trình hoạt động ĐÚNG như thiết kế (bắt được hướng không khả thi trước khi wire production, không
  phải thất bại của quy trình).
- **3 fallback chờ user chọn** (không quyết thay user):
  (i) giữ `fa_ratings` static, xử staleness riêng — caveat: edge control đo trên bảng lúc còn fresh,
      không bảo chứng cho bảng đóng băng sau BCTC Q2/2026;
  (ii) hybrid E-gate-only (chỉ thay T1 avoid bằng rating=5, giữ nguyên phần còn lại) — CHƯA ĐO, đây
      LÀ trial mới cần user duyệt mở N-budget riêng nếu muốn thử;
  (iii) rebuild legacy builder `fa_ratings` (builder gốc không còn trong repo) — giải quyết tận gốc
      staleness, giữ nguyên semantics đã tune.
  Deadline nghiệp vụ không đổi: BCTC Q2/2026 về ~cuối tháng 7, rebal quý ~08-05.

**User CHỐT (iii) — rebuild legacy `fa_ratings` builder (2026-07-11).** Kèm chỉ đạo chiến lược lớn
hơn, QUAN TRỌNG cho hướng nghiên cứu sắp tới:
- Bản thân **book Momentum (MOM_N) hiện tại đã KHÔNG hiệu quả** (không riêng gì việc không tái tạo
  được trên 8L) — cần làm lại chiến lược này, không chỉ vá cho hợp với nguồn dữ liệu mới.
- User KHÔNG đồng ý với khung "8L kém hơn vì mất quality-filter ngầm" — quan điểm user: 8L áp dụng
  lens riêng cho từng route/ngành nên rating PHẢI chính xác hơn, không phải kém đi. Nếu momentum
  không tái tạo được trên nền 8L, đó là dấu hiệu bản thân pattern momentum cũ dễ vỡ/overfit
  (dựa vào 1 "quality filter ngầm" tình cờ của tier cũ), KHÔNG phải lỗi của 8L.
- **Hướng nghiên cứu tiếp theo (sau khi (iii) xong và verified)**: quay lại phân tích các deal
  THÀNH CÔNG trong lịch sử của book — soi kỹ đặc điểm fundamentals + technical thật để tìm 1 pattern
  hiệu quả, KHÔNG cố giữ momentum chỉ vì nó từng "vô tình" chạy được. Đây là dự án R&D riêng, MỚI,
  không phải phần của việc rebuild fa_ratings.
- **Thứ tự làm việc user yêu cầu**: tuần tự, "phần nào làm tốt phần đó trước" — (iii) rebuild
  fa_ratings builder trước, verify xong mới bắt đầu dự án phân tích momentum/deals.
- Nguyên tắc chốt cho cả 2 việc: dùng dữ liệu tươi, đánh giá đúng chuẩn mực (walk-forward IS/OOS,
  DSR/PBO, LOO, quant-skeptic) — "không nên thấy pattern dễ overfit như momentum mà bị lay động"
  (không giữ 1 pattern chỉ vì quen thuộc/lịch sử nếu số liệu thật không ủng hộ).

**Tiến độ (iii) rebuild fa_ratings builder (2026-07-11, cùng ngày):**
- Feasibility XONG (Taylor job Taylor_20260711_145129, quant-skeptic CONFIRMED high confidence):
  builder gốc **chưa hề mất** — là `fundamental_rating.py` (repo root), registry ghi nhầm "không có
  writer" (đã sửa). Lineage 100% khớp 12.367/12.367 rows lịch sử; reproduction test chạy lại hôm nay
  = 82.3% khớp tier chính xác / 99.9% trong ±1 bậc; phủ tới 2026-07-08 gồm cả 2026Q2.
- **Root cause phần lệch 18% (user xác nhận, 2026-07-11)**: BQ admin có điều chỉnh nhỏ tỉ lệ chia cổ
  tức tiền mặt → giá điều chỉnh (adjusted Close) đổi nhẹ hồi tố → percentile trôi nhẹ gần ranh giới
  tier. Đây là hiện tượng bình thường của nguồn dữ liệu, không phải lỗi công thức.
- **User CHỐT mức độ an toàn cho quý cũ (nới so với đề xuất ban đầu của quant-skeptic)**: KHÔNG cần
  đòi khớp tuyệt đối/byte-identical cho các quý đã đóng băng — "quý cũ nếu có thay đổi nhẹ vẫn đạt
  tỉ lệ thống kê thì cũng không vấn đề gì". Nghĩa là: thiết kế append-only vẫn giữ nguyên hướng
  (không chủ động re-rank lại quý cũ), nhưng nếu do dữ liệu giá gốc tự nhiên trôi (như trên) làm quý
  cũ lệch nhẹ khi build lại, đó là chấp nhận được miễn còn đạt ngưỡng thống kê tương đương đã đo
  (~82%/99.9%), KHÔNG cần chặn cứng bằng diff byte-để-byte như quant-skeptic đề xuất ban đầu.
- **User duyệt: cho Taylor tiến hành bước tiếp theo** — xây cơ chế refresh append-only + cron weekly
  (giống mẫu `fa_ratings_8l`) + wire freshness-check. (a) fix pandas-3 nhỏ: XONG (commit `7d89c28`).

**VẤN ĐỀ (b) BQ-write-identity ĐÃ GIẢI QUYẾT XONG (2026-07-12, sớm 6 ngày so với kế hoạch chờ cron
07-18)** — user duyệt trực tiếp cho test ghi thật ngay hôm nay thay vì chờ thụ động. Root cause xác
nhận: cả 2 wrapper `refresh_fa_ratings_8l.sh`/`refresh_fa_ratings.sh` thiếu dòng `source wc_env.sh`
(mọi script ghi-BQ-thành-công khác trong repo đều có dòng này để đặt `CLOUDSDK_CONFIG` sang tài
khoản read-write `dtienthanh@gmail.com`; thiếu nó → rơi về default read-only `bq-reader-8l`). Fix 1
dòng mỗi script (commit `a9716f6`, repo mike). **Test ghi THẬT (không phải dry-run) thành công cả 2
bảng**, verify bằng `bq show` độc lập: `fa_ratings_8l` lastModified 06-20→**07-12**, rows
52.433→52.449; `fa_ratings` lastModified 05-10→**07-12**, rows 12.367→12.406, invariant 48/48 quý
đóng băng giữ nguyên (net delta +39 = đúng tổng 2 quý mở re-rank, số học khớp chính xác). quant-
skeptic CONFIRMED độ tin cậy cao (tự tái hiện toàn bộ số liệu). Cron thứ Bảy 07-18 giờ chỉ là lần
chạy scheduled đầu tiên bình thường (kỳ vọng OK), không còn câu hỏi identity treo — **dự án fa_ratings
rebuild coi như hoàn tất**, chỉ còn theo dõi thụ động qua các lần chạy tự động.
