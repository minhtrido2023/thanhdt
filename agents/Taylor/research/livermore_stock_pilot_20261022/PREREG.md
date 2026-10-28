# PREREG — Thí điểm Livermore đọc kỹ thuật CỔ PHIẾU cho candidate BAL/LAG (Mike ghi 2026-10-22 ~17:55 ICT, TRƯỚC khi sinh case / chạy agent)

User duyệt làm việc 2 (22/10 17:43 ICT). Chỉ đọc, KHÔNG sửa production, KHÔNG pin registry, KHÔNG wire.

## Câu hỏi duy nhất
Một người đọc cấu trúc giá+khối lượng cổ phiếu (agent Livermore) có cho **thông tin tăng thêm** về rủi ro đuôi
của candidate BAL/LAG **ngoài** các đặc trưng cơ học đã biết (VOL60, RUN20, DIST52) không?
Lý do hỏi: Taylor 22/10 (`entry_risk_tech_20261022`) đã chứng minh nhóm G_VOL (biến động 60 phiên cao) có đuôi xấu
thật (HIT15 30,5% vs 12,8% trên 5.361 sự kiện LAG) nhưng chỉ dùng để CẢNH BÁO. Nếu Livermore chỉ lặp lại G_VOL thì vô ích.

## Mẫu (cố định trước)
- Nguồn: `../entry_risk_tech_20261022/lag_events_features.csv` (LAG-event, cột `entry`, `G_VOL`, `HIT15`, `MAE`, `Y`) và
  `positions_features.csv` với `tag=pin0`, `book=BAL` (vị thế BAL, cột `e`, `G_VOL`, `HIT15`, `MAE`, `ret`).
- Chỉ lấy sự kiện có ngày vào >= 2015-03-01 VÀ mã có >= 250 phiên dữ liệu `tav2_bq.ticker` TRƯỚC ngày vào.
- Phân tầng theo `G_VOL` (đúng cột có sẵn, KHÔNG tính lại): **150 sự kiện G_VOL=True + 150 sự kiện G_VOL=False**,
  mỗi tầng 100 LAG-event + 50 BAL-position. Rút ngẫu nhiên seed=20261022. Tối đa 3 sự kiện/mã; không 2 sự kiện cùng mã
  cách nhau < 40 phiên. Nếu thiếu đủ thì hạ đều, báo rõ n thực tế (KHÔNG bù bằng tầng khác).
- Tổng N = 300 (nếu đủ). Trộn thứ tự, nhãn E001…E300; agent không biết book, tầng, nhãn kết quả.

## Dữ liệu agent được thấy (ẩn danh, TỰ CHỨA trong prompt — agent chạy KHÔNG có công cụ)
- 250 phiên của cổ phiếu kết thúc tại **phiên giao dịch cuối cùng TRƯỚC ngày vào** (as-of; lệnh khớp ở Open phiên kế).
  O/H/L/C **chia cho Close phiên đầu cửa sổ ×100** (cùng một hệ số); Volume chia cho median 250 phiên; thay ngày bằng chỉ số
  phiên 0..249 (as-of = 249). KHÔNG tên mã, KHÔNG ngày lịch, KHÔNG VNINDEX, KHÔNG fundamentals/loại sự kiện/book, KHÔNG outcome.
- Dùng giá `Close`/OHL đã điều chỉnh corp-action đúng nguồn Taylor đã dùng cho feature (ghi rõ cột trong REPORT);
  kiểm 0 nhảy giá >30% do tách/cổ tức chưa chỉnh trong cửa sổ — nếu có, loại sự kiện đó và nêu số loại.

## Câu hỏi cho agent (cố định) — đọc xong KHOÁ rồi mới chấm
Agent đóng vai Livermore nhưng KHÔNG gọi công cụ nào; output đúng khuôn:
- `P_HIT15`: xác suất 0-1 rằng trong thời gian nắm giữ (vài tuần đến vài tháng sau khi vào ở Open phiên kế), giá Low
  chạm ≤ −15% so với giá vào.
- `RISK`: LOW / MED / HIGH (bucket thô).
- `P_POS`: xác suất 0-1 lợi suất giao dịch cả kỳ > 0.
- `INVALIDATION`: 1 dòng.
- `CONTAMINATION`: nhận ra chuỗi giá là cổ phiếu/giai đoạn lịch sử cụ thể nào không (nêu mã+giai đoạn nếu có; KHÔNG dùng vào dự báo).
Mỗi case chạy ĐỘC LẬP (một lần gọi `claude -p --model opus` riêng, không chia ngữ cảnh, không công cụ, cwd `/tmp`),
song song tối đa 6 tiến trình (container 40GB). Lỗi kỹ thuật chạy lại CÙNG prompt. **Không chạy lại, không đổi prompt
sau khi thấy outcome.** Sau khi đủ 300 kết quả: ghi `reads.csv`, tính md5, GHI md5 vào log TRƯỚC khi join outcome.

## Chấm điểm (cơ khí, tính SAU khi `reads.csv` đã khoá md5)
Outcome = `HIT15` (chính), `Y` hoặc `ret` > 0 (phụ). Mọi cụm bootstrap theo **mùa/quý** (cụm = quý vào lệnh), 5.000 lần.
1. **AUC trong-tầng gộp** (chính): AUC của `P_HIT15` với `HIT15` tính RIÊNG trong tầng G_VOL=True và G_VOL=False, rồi trung bình
   có trọng số theo số dương tính hiếm của mỗi tầng (nêu công thức). Đây là phần tăng thêm *ngoài* G_VOL.
2. **Tăng thêm so với đặc trưng cơ học**: logistic `HIT15 ~ VOL60 + RUN20 + DIST52` (liên tục) vs thêm `logit(P_HIT15)`;
   so ΔAUC bằng 5-fold CV phân tầng, cụm theo quý; kèm LR test.
3. **Baseline**: B0 = P=base rate (AUC 0,5); B1 = logistic cơ học ở (2); B2 = chỉ cờ G_VOL.
4. Phụ: Brier và AUC của `P_POS` với dấu `Y`/`ret`; so với B0.
5. Độ nhiễm: báo kết quả (1)(2) cả khi LOẠI case agent khai CONTAMINATION có mã cụ thể.

## Tiêu chí (cố định)
- **GO-LẠI (đáng tiếp tục thử forward, KHÔNG phải wire)** nếu ĐỒNG THỜI: (a) AUC trong-tầng gộp >= 0,58 và CI95 cụm
  loại trừ 0,5; (b) ΔAUC so với B1 > 0 với CI95 cụm loại trừ 0; (c) kết quả (a) giữ nguyên dấu khi loại case nhiễm.
- **NO-GO** nếu (a) hoặc (b) hụt, hoặc AUC trong-tầng gộp <= 0,52. Còn lại **INCONCLUSIVE** (nêu cần bao nhiêu n nữa
  theo CI đo được; KHÔNG tự mở rộng mẫu).
- Dù GO-LẠI: hành động tối đa là **dòng cảnh báo hiển thị** trong due diligence, không sizing, không gate; qua quant-skeptic
  và PREREG forward riêng trước khi nối. Kết quả KHÔNG suy ra cho thị trường (VNINDEX) — đó là gate riêng của Livermore.

## Chi phí & ràng buộc
~300 lần gọi Opus (ước ~3-4 triệu token). Nếu quá nửa số lần gọi lỗi/usage-limit: dừng, báo, KHÔNG diễn giải phần đã chạy.
Mọi output vào thư mục này, tên non-canonical. Chạy pipeline trên Python `/home/trido/thanhdt/wc_venv/bin/python`.
