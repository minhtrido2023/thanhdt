# Kiểm kê ĐẦY ĐỦ mọi điều chỉnh mạnh (drawdown ≥15%) trong lịch sử VNINDEX

> Job `Taylor_20260831_063413` · 2026-08-31 · Bước 1/2 của chuỗi Taylor(liệt kê) → Mike(quyết
> định) → Bobby(phân tích vĩ mô episode MỚI). **Đây là bước LIỆT KÊ + PHÂN LOẠI thuần tuý — KHÔNG
> kết luận gì về cơ chế/nguyên nhân vĩ mô**, đó là việc của Bobby ở bước sau.
> Nguồn dữ liệu: `data/VNINDEX.csv` (Close hàng ngày). 6 episode đã nghiên cứu lấy nguyên ngày
> đỉnh/đáy/số liệu từ `mike/agents/Taylor/research/vn_prior_trend_meanreversion_hypothesis_20260831/REPORT.md`
> (KHÔNG đo lại), đối chiếu cross-check số Close tại đúng các ngày đó khớp 100%.

## ⚠️ Giới hạn dữ liệu cần biết trước khi đọc bảng

1. **`data/VNINDEX.csv` chỉ có đến 2026-05-26** (8 phiên sau đỉnh 07/2026 = 2026-05-18). Đợt
   điều chỉnh 07/2026 (đã nghiên cứu ở job khác, dd đo được -13,46%, đáy + hồi phục nằm sau
   05-26) **hoàn toàn không nằm trong phạm vi file này** — số liệu 07/2026 dưới đây lấy 100% từ
   report cũ, không tính lại. Không có dữ liệu mới nào sau 2026-05-26 để quét thêm ở job này.
2. **07/2026 chỉ đạt dd -13,46% — DƯỚI ngưỡng ≥15% của job này.** Nó vẫn được liệt kê (vì là 1
   trong 6 episode đã nghiên cứu, cần đối chiếu) nhưng về mặt thuần thuật toán, nếu quét độc lập
   nó sẽ KHÔNG lọt vào bảng "điều chỉnh mạnh ≥15%".
3. VN market **mỏng trước ~2008** (CLAUDE.md: 2006≈19 mã, 2008≈105 mã) — mọi episode có đỉnh
   trước 2007 (2001-2006) mang rủi ro nhiễu thanh khoản cao hơn nhiều so với episode sau 2008;
   đánh dấu riêng ở bảng dưới, KHÔNG loại bỏ (dispatch yêu cầu liệt kê đầy đủ, không bỏ sót).

## Phương pháp

Thuật toán **zigzag pivot** (ngưỡng đảo chiều 10%) chạy trên toàn bộ chuỗi Close 2000-07-28 →
2026-05-26 (6.283 phiên), tách chuỗi giá thành các cặp đỉnh(H)→đáy(L) liên tiếp, sau đó lọc mọi
cặp có `dd_pct ≤ -15%`. Đây là phương pháp **thuần cơ học, không lookahead, không cherry-pick** —
khác với cách nhóm "peak → đáy cuối cùng trước khi hồi về đúng ATH cũ" (method dùng cho 6 episode
biên, gộp nhiều chân zigzag liên tiếp thành 1 "làn sóng" macro như Wave1/Wave2-3/2022) — cả 2 cách
đều đúng, chỉ khác ĐƠN VỊ đếm: zigzag cho "chân điều chỉnh" (leg) hẹp; 6 episode biên cho "làn
sóng macro" (nhiều leg gộp lại theo domain-context, ví dụ Wave2/3 gộp 5 chân zigzag 2009→2012 vì
thị trường không hồi lại ATH cũ giữa các chân đó).

Kết quả: **36 chân zigzag** thoả `dd ≥15%`, trong đó **19 chân** nằm bên trong cửa sổ ngày-tháng
của 5 episode biên đã nghiên cứu (Wave1=10, Wave2/3=5, 2018=1, COVID=1, 2022=2) → **17 chân còn
lại là MỚI** (chưa từng xuất hiện trong bất kỳ nghiên cứu nào của fleet cho tới hôm nay), trong đó
12 chân đủ dài (≥20 phiên) để đáng xét thêm, 5 chân quá ngắn xếp noise.

---

## Bảng TỔNG HỢP — mọi đợt điều chỉnh ≥15%, sắp theo thời gian

Cột `status`: **DA_NGHIEN_CUU** = nằm trong 1 trong 6 episode Bobby-ready đã có phân tích vĩ mô
đầy đủ · **MOI_DANG_XET** = chân MỚI, dd≥15% VÀ kéo dài ≥20 phiên giao dịch (~1 tháng) → đáng để
Bobby phân tích thêm · **NOISE_NHO** = chân MỚI nhưng quá ngắn (<20 phiên) — khả năng cao là biến
động thị trường bình thường / thanh khoản mỏng, không đáng gọi "điều chỉnh mạnh" theo nghĩa
khủng hoảng/sự kiện.

| # | Đỉnh (ngày, Close) | Đáy (ngày, Close) | DD đỉnh→đáy | Số phiên giảm | Hồi phục (đáy→đỉnh cũ) | Status | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1 | 2001-07-20, 466,67 | 2001-08-06, 350,69 | -24,85% | 7 | không đo (thị trường sơ khai) | **NOISE_NHO** | Thị trường mỏng, VN-Index mới niêm yết ~1 năm |
| 2 | 2001-08-10, 394,18 | 2001-08-29, 261,35 | -33,70% | 8 | không đo | **NOISE_NHO** | ⚠️ thị trường mỏng — chồng lấn thời gian với #1, chuỗi giảm gần như liên tục 07-2001→10-2001 |
| 3 | 2001-09-07, 307,76 | 2001-10-05, 203,12 | -34,00% | 12 | không đo | **NOISE_NHO** | ⚠️ thị trường mỏng — cùng chuỗi giảm với #1-2, đỉnh sau chỉ là hồi kỹ thuật ngắn |
| 4 | 2001-11-19, 301,09 | 2002-03-11, 180,73 | -39,97% | 47 | không đo | **MOI_DANG_XET** | ⚠️ thị trường mỏng nhưng đủ dài (2,3 tháng) để không phải noise thuần |
| 5 | 2002-05-06, 214,23 | 2003-04-01, 139,64 | -34,82% | 226 | không đo | **MOI_DANG_XET** | ⚠️ thị trường mỏng, kéo dài gần 1 năm — "bear thị trường sơ khai" đáng chú ý nhất trước 2007 |
| 6 | 2003-05-13, 158,54 | 2003-10-24, 130,90 | -17,43% | 116 | không đo | **MOI_DANG_XET** | ⚠️ thị trường mỏng, gần đáy tuyệt đối lịch sử VNINDEX (130,90) |
| 7 | 2004-04-01, 279,71 | 2004-08-09, 213,74 | -23,59% | 90 | không đo | **MOI_DANG_XET** | ⚠️ thị trường mỏng |
| 8 | 2006-04-25, 632,69 | 2006-05-10, 520,82 | -17,68% | 9 | không đo | **NOISE_NHO** | Đầu giai đoạn bùng nổ 2006-2007, chân giảm rất ngắn |
| 9 | 2006-05-15, 590,25 | 2006-08-02, 399,80 | -32,27% | 57 | không đo | **MOI_DANG_XET** | "Mini-crash" giữa 2 đợt bùng nổ 2006/2007 — đáng chú ý, thị trường lúc này đã ~19-40 mã (còn mỏng nhưng đỡ hơn 2001-2004) |
| 10 | **2007-03-12, 1170,67** | **2009-02-24, 235,50** | **-79,88%** | 483 (715 ngày lịch, 23,5th) | +165,01% (240 ngày) | **DA_NGHIEN_CUU** | = "Wave1" — bao 10 chân zigzag con (2007-05, 2007-10, 2008-02/03/04/08/09/11, 2009-01), report đã phân tích đầy đủ |
| 10b | 2009-06-09, 512,50 | 2009-07-20, 412,90 | -19,43% | 29 | không đo | **MOI_DANG_XET** | Nằm NGAY GIỮA Wave1 (đáy 2009-02-24) và Wave2/3 (đỉnh 2009-10-22) — trong nhịp hồi phục Wave1, KHÔNG thuộc cửa sổ của episode nào đã nghiên cứu. Đáng chú ý vì nằm trong giai đoạn "hồi phục nhờ kích thích 2009" mà report Wave2/3 mô tả là "bôi thêm dầu vào lửa" — case này có thể là dấu hiệu sớm |
| 11 | **2009-10-22, 624,10** | **2012-01-06 (đáy giả, 336,73) / 2012-11-02 (đáy thật, 375,26)** | **-46,05% (giả) / -39,87% (thật)** | tới 1107 ngày lịch (36,4th) | +40,69% từ đáy thật (217 ngày) | **DA_NGHIEN_CUU** | = "Wave2/3" — bao 5 chân zigzag con (2009-06, 2010-05, 2011-02, 2011-09, 2012-05), report đã phân tích đầy đủ |
| 12 | 2014-03-24, 607,55 | 2014-05-13, 513,91 | -15,41% | 32 | không đo | **MOI_DANG_XET** | Biên độ sát ngưỡng 15% — cần xem lại có đáng phân tích hay không |
| 13 | 2014-09-03, 640,75 | 2014-12-17, 518,22 | -19,12% | 75 | không đo | **MOI_DANG_XET** | Trùng giai đoạn giá dầu sụp 2014 (giả thuyết, CHƯA kiểm chứng — việc của Bobby) |
| 14 | 2015-07-14, 638,69 | 2015-08-24, 526,93 | -17,50% | 29 | không đo | **MOI_DANG_XET** | Trùng giai đoạn Trung Quốc phá giá NDT + chứng khoán TQ sụp 08-2015 (giả thuyết, CHƯA kiểm chứng) |
| 15 | 2015-11-05, 615,18 | 2016-01-21, 521,88 | -15,17% | 54 | không đo | **MOI_DANG_XET** | Biên độ sát ngưỡng 15% |
| 16 | **2018-04-09, 1204,33** | **~2018-10-30, 888,69** | **-26,21%** | 204 ngày lịch (6,7th) | +11,56% (KHÔNG hồi về đỉnh cũ, 449 ngày) | **DA_NGHIEN_CUU** | Đã phân tích đầy đủ (outcome XẤU, không V-recover trước khi COVID ập tới) |
| 17 | **2019-11-06 (proxy), 1024,91 [đỉnh chính thức report: 2020-01-22, 991,46]** | **2020-03-24, 659,21** | **-33,51% (từ 991,46) / -35,68% (từ 1024,91)** | 62 ngày lịch (2,0th) | +131,88% (tới đỉnh 2022, 653 ngày) | **DA_NGHIEN_CUU** | = COVID 2020, đã phân tích đầy đủ. Chênh đỉnh do zigzag bắt đỉnh sớm hơn 2,5 tháng (2019-11 vs 2020-01), chỉ khác định nghĩa "đỉnh", KHÔNG đổi kết luận |
| 18 | **2022-01-06, 1528,57** | **2022-11-15, 911,90** | **-40,34%** | 313 ngày lịch (10,3th) | +36,58% (295 ngày) | **DA_NGHIEN_CUU** | Đã phân tích đầy đủ — bao 2 chân zigzag con (2022-01→05, 2022-08→11) |
| 19 | 2023-09-06, 1245,50 | 2023-10-31, 1028,19 | -17,45% | 39 | không đo | **MOI_DANG_XET** | Chưa có phân tích vĩ mô nào trong fleet |
| 20 | 2025-03-17, 1336,26 | 2025-04-09, 1094,30 | -18,11% | 16 | không đo | **NOISE_NHO** | ⚠️ Trùng thời điểm Mỹ công bố thuế đối ứng "Liberation Day" 04/2025 (giả thuyết thô, CHƯA kiểm chứng) — nhưng chân giảm RẤT ngắn (16 phiên) nên xếp noise theo tiêu chí thời lượng; **Mike/Bobby có thể cân nhắc nâng lên MOI_DANG_XET nếu coi cú sốc thuế quan là sự kiện đủ lớn bất kể thời lượng ngắn** |
| 21 | 2026-01-13, 1902,93 | 2026-03-23, 1591,17 | -16,38% | 44 | +9,80%* | **MOI_DANG_XET** | *Hồi phục đo được: đỉnh kế tiếp 2026-05-18 (1927,94, +21,17% từ đáy) đã có trong 6 episode biên (đây chính là đỉnh khởi đầu của "07/2026"). Bản thân đợt giảm 01-03/2026 này CHƯA được phân tích vĩ mô độc lập — chỉ mới coi 07/2026 (giảm SAU đỉnh 05-2026) là episode nghiên cứu |
| 22 | **2026-05-18, 1927,94** [báo cáo cũ] | chưa xác định trong CSV này (ngoài phạm vi dữ liệu) | **-13,46%** (từ report cũ, DƯỚI ngưỡng 15% của job này) | 65 ngày lịch (2,1th) | +9,80% (đang tiếp diễn, right-censored tới 28/08) | **DA_NGHIEN_CUU** | = "07/2026", đã phân tích đầy đủ ở job khác. Liệt kê ở đây chỉ để đối chiếu — về thuật toán ngưỡng 15% của job này, nó KHÔNG lọt bảng nếu quét độc lập |

**Tổng cộng: 23 dòng** (gộp các chân zigzag con vào episode mẹ cho 5/6 episode biên đã nghiên cứu
— trừ 07/2026 nằm ngoài phạm vi CSV) — trong đó: **6 DA_NGHIEN_CUU** (khớp đúng 6 episode dispatch
nêu) · **14 MOI_DANG_XET** · **3 NOISE_NHO** (2 sát mép, có thể nâng cấp theo phán đoán của Mike).

---

## Danh sách 17 chân zigzag KHÔNG nằm trong 6 episode biên (chi tiết thô, trước khi gộp)

Bảng trên đã gộp theo episode-mẹ cho phần DA_NGHIEN_CUU; dưới đây là **nguyên bản 17 chân zigzag
MỚI** (đã lọc dd≥15%, ngưỡng đảo chiều 10%) dùng để tra cứu lại nếu cần, cùng cờ lọc bước 5 của
dispatch (`dd≥15% AND decline_days≥20 phiên`). Kiểm chứng đếm: 36 chân zigzag tổng − 19 chân nằm
trong 5 cửa sổ episode biên (Wave1=10, Wave2/3=5, 2018=1, COVID=1, 2022=2) = **17 chân độc lập**,
khớp đúng số dòng dưới đây.

| Đỉnh | Đáy | DD% | Phiên giảm | Qua lọc ≥20 phiên? |
|---|---|---|---|---|
| 2001-07-20 | 2001-08-06 | -24,85% | 7 | KHÔNG → NOISE_NHO |
| 2001-08-10 | 2001-08-29 | -33,70% | 8 | KHÔNG → NOISE_NHO |
| 2001-09-07 | 2001-10-05 | -34,00% | 12 | KHÔNG → NOISE_NHO |
| 2001-11-19 | 2002-03-11 | -39,97% | 47 | CÓ → MOI_DANG_XET |
| 2002-05-06 | 2003-04-01 | -34,82% | 226 | CÓ → MOI_DANG_XET |
| 2003-05-13 | 2003-10-24 | -17,43% | 116 | CÓ → MOI_DANG_XET |
| 2004-04-01 | 2004-08-09 | -23,59% | 90 | CÓ → MOI_DANG_XET |
| 2006-04-25 | 2006-05-10 | -17,68% | 9 | KHÔNG → NOISE_NHO |
| 2006-05-15 | 2006-08-02 | -32,27% | 57 | CÓ → MOI_DANG_XET |
| 2009-06-09 | 2009-07-20 | -19,43% | 29 | CÓ → MOI_DANG_XET (nằm giữa Wave1 và Wave2/3, xem ghi chú #10b ở bảng trên) |
| 2014-03-24 | 2014-05-13 | -15,41% | 32 | CÓ → MOI_DANG_XET (biên độ sát ngưỡng) |
| 2014-09-03 | 2014-12-17 | -19,12% | 75 | CÓ → MOI_DANG_XET |
| 2015-07-14 | 2015-08-24 | -17,50% | 29 | CÓ → MOI_DANG_XET |
| 2015-11-05 | 2016-01-21 | -15,17% | 54 | CÓ → MOI_DANG_XET (biên độ sát ngưỡng) |
| 2023-09-06 | 2023-10-31 | -17,45% | 39 | CÓ → MOI_DANG_XET |
| 2025-03-17 | 2025-04-09 | -18,11% | 16 | KHÔNG → NOISE_NHO (nhưng khả năng trùng "Liberation Day" tariff shock — xem ghi chú #20 ở bảng trên) |
| 2026-01-13 | 2026-03-23 | -16,38% | 44 | CÓ → MOI_DANG_XET |

17 dòng: 5 NOISE_NHO (thời lượng <20 phiên) + 12 MOI_DANG_XET (thời lượng ≥20 phiên). Cộng với
5 episode-mẹ DA_NGHIEN_CUU (Wave1, Wave2/3, 2018, COVID, 2022) + 07/2026 (ngoài phạm vi CSV,
liệt kê riêng) = đúng 23 dòng ở bảng tổng hợp phía trên.

---

## Khuyến nghị sơ bộ cho Mike (KHÔNG phải phân tích vĩ mô — chỉ là gợi ý ưu tiên xét duyệt)

Ứng viên đáng cân nhắc dispatch Bobby nhất trong nhóm MOI_DANG_XET (dựa trên độ dài + độ sâu +
khả năng có sự kiện vĩ mô xác định được, thuần suy đoán bề mặt — Bobby phải tự kiểm chứng):

1. **2002-05-06 → 2003-04-01 (-34,82%, ~11 tháng)** — bear dài nhất trước 2007, đáy gần chạm đáy
   tuyệt đối lịch sử VNINDEX; dù thị trường mỏng, đây là "khủng hoảng sơ khai" đáng có 1 dòng.
2. **2014-09-03 → 2014-12-17 (-19,12%, 75 phiên)** và **2015-07-14 → 2015-08-24 (-17,50%, 29
   phiên)** — cả 2 trùng giai đoạn giá dầu sụp + Trung Quốc phá giá NDT/chứng khoán TQ sụp
   (giả thuyết thô, CHƯA kiểm chứng) — nếu đúng, đây là 2 case "external targeted shock" tốt để
   đối chiếu với khung 3-archetype đã dựng cho 2018/2022.
3. **2023-09-06 → 2023-10-31 (-17,45%, 39 phiên)** — hoàn toàn chưa có phân tích nào trong fleet,
   gần đây, dữ liệu vĩ mô dễ lấy nhất.
4. **2026-01-13 → 2026-03-23 (-16,38%, 44 phiên)** — liền kề trước episode 07/2026 đã nghiên cứu;
   Bobby phân tích riêng đợt này có thể giúp hiểu bối cảnh macro DẪN TỚI đỉnh 05-2026 (input cho
   câu hỏi "vì sao 07/2026 hồi nhanh" đang mở từ nghiên cứu trước).
5. **2025-03-17 → 2025-04-09 (-18,11%, chỉ 16 phiên nhưng biên độ sâu)** — nếu Mike xác nhận đây
   là tariff shock tháng 04/2025, nên nâng lên MOI_DANG_XET bất kể ngắn ngày, vì đây là loại
   "external targeted shock" nhanh — đúng dạng mẫu 07/2026 (07/2026 cũng chỉ 65 ngày, ngắn hơn
   nhiều so với các case structural).

Nhóm NOISE_NHO còn lại (2001 cụm 3 đợt liên tiếp, 2006-04, 2025-03) khuyến nghị **không dispatch
Bobby** trừ khi Mike có lý do cụ thể khác.
