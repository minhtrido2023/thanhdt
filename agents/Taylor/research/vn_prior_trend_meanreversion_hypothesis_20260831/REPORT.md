# Giả thuyết mean-reversion theo độ dài/mạnh xu hướng tăng TRƯỚC khủng hoảng — kiểm định N=6

> Job `Taylor_20260831_053055` · 2026-08-31 · RESEARCH-ONLY, không wire production, không đổi
> DT5G/CAPIT. Tiếp nối 5 job cùng chuỗi ngày 2026-08-31 (2009/2012/2020-2022 recovery-trigger +
> top-divergence + margin-signature-recheck) — lấy lại ngày đỉnh/đáy đã xác định, KHÔNG đo lại.
> Nguồn dữ liệu: `data/VNINDEX.csv` (Close hàng ngày, cùng nguồn 5 job trước).

## Tóm tắt 1 dòng

**Giả thuyết KHÔNG được N=6 ủng hộ như một quy luật chung.** Correlation Pearson (N=6) cho tín
hiệu ủng hộ vẻ ngoài (r=-0,805, p=0,053 giữa 12mo-return và độ sâu drawdown) nhưng **biến mất hoàn
toàn khi bỏ 1 điểm cực đoan** (2007-2009, r rơi về +0,019) — tức là "bằng chứng" chỉ đến từ 1 case.
**Phát hiện phá vỡ giả thuyết mạnh nhất**: case 07/2026 (được user dùng làm đối lập với 2022) và
case 2018 (outcome XẤU) **GIỐNG HỆT NHAU trên mọi thước đo prior-trend** (12mo return 48% vs 65%,
tháng-không-điều-chỉnh 1,3 vs 1,8 tháng) nhưng có kết cục HOÀN TOÀN TRÁI NGƯỢC (07/2026 hồi phục
nhanh nhất trong 6 case; 2018 không hồi phục được trước khi COVID ập tới). Phần giả thuyết SỐNG
SÓT: 2 case có tỷ suất tích luỹ "từ đáy khủng hoảng trước" LỚN NHẤT (2009→2012 +165%, 2020→2022
+131,9%) đều dẫn tới đợt khủng hoảng kế tiếp thuộc loại nặng/hồi phục chậm nhất — nhưng đây là N=2,
và cơ chế thật (STRUCTURAL credit 2012, cascade-nested-in-crisis 2022) đã được framework 3-archetype
giải thích tốt hơn, không cần viện tới "độ dài xu hướng tăng".

---

## Bước 1+2 — Bảng đầy đủ: prior-trend vs severity/recovery, 6 episode

| Episode | Peak (Close) | 12mo return trước đỉnh | 24mo return trước đỉnh | Tháng uptrend liên tục không correction >-10%* | Drawdown đỉnh→đáy | Thời gian giảm | Recovery (đáy→đỉnh kế) | Thời gian hồi | Breadth-healing (phiên)** |
|---|---|---|---|---|---|---|---|---|---|
| **2007-2009 Wave1** | 2007-03-12 (1170,67) | **+182,52%** | **+393,93%** | 3,8 tháng | **-79,88%** | 715 ngày (23,5th) | **+165,01%** | 240 ngày (7,9th) | 10 |
| **2011-2012 Wave2/3** | 2009-10-22 (624,10) | +66,47% | -42,52%¹ | 2,8 tháng² | -46,05% (đáy giả) / -39,87% (đáy thật) | 806-1107 ngày (26,5-36,4th) | +40,69% (từ đáy thật) | 217 ngày (7,1th) | 32 (leg1) / **91 (leg2, chậm nhất)** |
| **2018** | 2018-04-09 (1204,33) | +65,44% | +110,42% | 1,8 tháng | -26,21% | 204 ngày (6,7th) | **+11,56%** (KHÔNG hồi về đỉnh cũ) | 449 ngày (14,8th) | N/A (chưa đo) |
| **2020 COVID** | 2020-01-22 (991,46) | +9,37% | -8,75%¹ | **14,8 tháng²** (không hề có correction >-10% trong toàn bộ leg từ đáy 2018) | -33,51% | 62 ngày (2,0th) | +131,88% (tới đỉnh kế 2022) / +36,53% (tới đỉnh nông đầu tiên) | 653 / 78 ngày | **12 (nhanh)** |
| **2022** | 2022-01-06 (1528,57) | +33,71% | +59,93% | 5,3 tháng | -40,34% | 313 ngày (10,3th) | +36,58% | 295 ngày (9,7th) | 47 (chậm) |
| **07/2026** | 2026-05-18 (1927,94) | +48,14% | +51,44% | **1,3 tháng** | **-13,46%** (nông nhất) | 65 ngày (2,1th) | +9,80% (ĐANG DIỄN RA, right-censored, 27/38 phiên/ngày tính tới 28/08) | 38 ngày (đang tiếp diễn) | **~5 (nhanh nhất)** |

¹ 24mo return của 2011-2012 và 2020 là số **GÂY NHIỄU** — cửa sổ 24 tháng của chúng đi NGƯỢC qua
đúng đỉnh của khủng hoảng TRƯỚC đó (2007 và 2018), nên phản ánh "còn cách ATH cũ bao xa", không
phải "thị trường vừa tăng nóng bao nhiêu". Xem Bước 4/5 để tách riêng.

² Với 2 case này, "tháng uptrend" tính bằng running-max TOÀN LỊCH SỬ (anchor mặc định) cho ra 0,0
tháng vô nghĩa (vì peak vẫn thấp hơn ATH cũ 2007/2018 rất xa nên luôn ở trạng thái "correction >
-10%" ngay tại chính điểm peak) — đã SỬA bằng cách neo lại running-max từ đúng đáy của khủng hoảng
NGAY TRƯỚC đó (2009-02-24 cho case 2011-2012; 2018-10-30 cho case 2020), khớp đúng câu hỏi thật
("xu hướng tăng liên tục NGAY TRƯỚC đỉnh này dài bao lâu").

\* Định nghĩa: đếm ngược từ ngày đỉnh, tìm ngày GẦN NHẤT mà Close đã giảm ≥10% so với running-max
tính TỪ mốc trough neo (xem cột 2); số tháng = khoảng cách từ ngày correction đó tới đỉnh.

\*\* Số phiên để %oversold (universe_pit D_RSI<0,30) hồi về ≤ baseline calm riêng từng episode —
lấy nguyên từ 5 job trước, KHÔNG đo lại.

## Bước 3 — Correlation (Pearson + Spearman, N nhỏ, không đủ mạnh cho suy luận thống kê chặt)

### N=6 đầy đủ (bao gồm 07/2026 recovery còn dang dở/right-censored)

| Cặp biến | Pearson r | p | Spearman ρ | p |
|---|---|---|---|---|
| 12mo-return vs drawdown_pct | **-0,805** | 0,053 | -0,543 | 0,266 |
| 24mo-return vs drawdown_pct | -0,717 | 0,109 | -0,143 | 0,787 |
| tháng-uptrend vs drawdown_pct | -0,031 | 0,954 | -0,486 | 0,329 |
| 12mo-return vs thời-gian-giảm | +0,517 | 0,293 | +0,771 | 0,072 |
| tháng-uptrend vs thời-gian-hồi-phục | +0,790 | 0,061 | +0,657 | 0,156 |
| 12mo-return vs tốc-độ-hồi-phục (%/ngày) | **+0,835** | 0,039 | +0,257 | 0,623 |

### N=5, loại bỏ 2007-2009 (thị trường mỏng — bẫy CLAUDE.md; nghi ngờ outlier khác chất)

| Cặp biến | Pearson r | p | Spearman ρ | p |
|---|---|---|---|---|
| 12mo-return vs drawdown_pct | **+0,019** | 0,976 | -0,200 | 0,747 |
| tháng-uptrend vs drawdown_pct | -0,259 | 0,674 | -0,600 | 0,285 |
| 12mo-return vs tốc-độ-hồi-phục | -0,347 | 0,568 | -0,300 | 0,624 |

**Phát hiện then chốt của Bước 3**: correlation "ủng hộ" giả thuyết ở N=6 (r=-0,805 giữa 12mo-return
và drawdown) **sụp đổ hoàn toàn khi bỏ đúng 1 điểm** (2007-2009) — từ -0,805 xuống +0,019, đổi cả
dấu. Với N=6 vốn đã quá mỏng để tin cậy (Pearson nhạy điểm ngoại lai bậc nhất trong thống kê), một
correlation mà 100% "sức mạnh" đến từ 1/6 điểm dữ liệu **không phải bằng chứng, đó là hiện tượng
"driven-by-one-outlier"** phải bị loại theo đúng kỷ luật N nhỏ. Correlation **"12mo-return vs
tốc-độ-hồi-phục" (+0,835, p=0,039)** cũng đi NGƯỢC chiều giả thuyết user (hồi nhanh hơn khi prior-
trend mạnh hơn) — nhưng đọc kỹ: đây chính là case 2007-2009 (+182% prior, hồi +165% trong 8 tháng)
— và "hồi phục" đó **KHÔNG BỀN VỮNG**, nó tự nó là một đợt tái-bùng-nổ dẫn thẳng tới khủng hoảng
STRUCTURAL 2011-2012 tệ hơn (đã ghi trong job 2009: "gói kích thích 2009 bôi thêm dầu vào lửa cho
Wave2"). Recovery "nhanh" ở đây là ảo — không nên tính chung thước đo với V-recovery THẬT (07/2026,
2020) đưa thị trường về trạng thái ổn định lâu dài.

## Bước 4 — Kiểm chứng RIÊNG case 07/2026 (điểm kiểm chứng quan trọng nhất theo dispatch)

**KẾT QUẢ: KHÔNG khớp khung "nền bình thường" mà user mô tả — 12mo/24mo return trước đỉnh
18/05/2026 đều CAO, không hề thấp hơn 2018/2022:**

| Metric | 07/2026 | 2018 (outcome XẤU) | 2022 (outcome XẤU) |
|---|---|---|---|
| 12mo return trước đỉnh | +48,14% | +65,44% | +33,71% |
| 24mo return trước đỉnh | +51,44% | +110,42% | +59,93% |
| Tháng uptrend liên tục (không correction >-10%) | 1,3 tháng | 1,8 tháng | 5,3 tháng |

**07/2026 và 2018 GẦN NHƯ TRÙNG KHỚP trên cả 3 thước đo prior-trend** (48% vs 65% ở 12mo; 1,3 vs
1,8 tháng uptrend-liền-trước — chênh lệch nằm trong biên độ nhiễu, không phải khác biệt định tính)
— nhưng outcome của 2 case đối lập hoàn toàn: 07/2026 hồi phục NHANH NHẤT trong 6 case (breadth
lành ~5 phiên, +63,1% khoảng cách giảm chỉ trong 27 phiên); 2018 KHÔNG hồi phục được (chỉ +11,56%
trong 449 ngày, vẫn thấp hơn đỉnh cũ 17,7% khi COVID ập tới 15 tháng sau). **Đây là bằng chứng TRỰC
TIẾP phản bác phần quan trọng nhất của giả thuyết**: nếu prior-trend-strength là biến quyết định,
2 case giống hệt nhau ở input phải cho outcome giống nhau — nhưng chúng không.

**Điều THẬT SỰ phân biệt 07/2026 với 2018** (đã xác lập ở `vn_2022_2018_margin_signature_recheck_20260831`
và `vn_top_divergence_and_margin_selloff_20260831`, KHÔNG phải job này phát hiện lại): 07/2026 chỉ
có **1 cụm margin-cascade duy nhất** rồi V-recover ngay; 2018 có cụm cấp tính RỒI KHÔNG V-recover mà
chuyển sang chế độ "grind" kéo dài không rõ nguyên nhân margin. external_flag sạch ở cả 2. Sự khác
biệt nằm ở **"điều gì xảy ra SAU cluster"** (đã là kết luận job trước), không nằm ở độ dài/mạnh xu
hướng tăng đưa tới cluster đó.

## Bước 5 — Kiểm chứng claim cụ thể của user về 2020 COVID

**Claim của user ĐÚNG, thậm chí đúng RÕ RÀNG HƠN cả mô tả gốc.** Từ đỉnh 2018 (09/04/2018, 1204,33)
đến đỉnh ngay trước COVID (22/01/2020, 991,46): **cumulative return = -17,68%** qua 653 ngày (21,5
tháng) — thị trường 2020 bước vào khủng hoảng COVID khi **còn đang ở dưới đỉnh cũ 17,7%**, không hề
"tăng nóng". Đo chặt hơn (từ đáy 2018 30/10/2018, 888,69, tới đỉnh trước COVID): **+11,56% trong
449 ngày (14,8 tháng), và KHÔNG hề có 1 correction nào ≥-10% xảy ra trong suốt leg đó** (running-max
neo lại đáy 2018 không bao giờ bị phá vỡ 10%+ cho tới chính ngày đỉnh 22/01/2020). Đây là mức tăng
**yếu nhất trong toàn bộ 6 case** — hoàn toàn khớp claim user "gần đi ngang", và là case KHÔNG bị đè
nén bởi xu hướng tăng nóng nào — sau đó hồi phục nhanh và mạnh nhất (+131,88% trong 21,5 tháng tới
đỉnh 2022, breadth lành chỉ 12 phiên). Đây là bằng chứng ỦNG HỘ MẠNH cho nửa "không đè nén = hồi
nhanh" của giả thuyết.

## Bước 6 — Tổng hợp: giả thuyết đúng phần nào, đề xuất LEAD-6

**Không đủ N=5-6 nhất quán để coi robust — đúng kỷ luật N nhỏ đã dùng xuyên suốt 5 job trước.**
Bảng phân loại case-by-case (không chỉ dựa correlation, vì N quá nhỏ để correlation có ý nghĩa):

| Case | Prior-trend mạnh/dài? | Outcome nặng/chậm? | Khớp giả thuyết? |
|---|---|---|---|
| 2020 COVID | KHÔNG (yếu nhất, +11,56%/14,8th, 0 correction) | KHÔNG (hồi nhanh nhất trừ 07/2026) | **KHỚP RÕ** |
| 2009→2012 (dùng khung "từ đáy trước") | CÓ (rally +165%/8th mạnh nhất) | CÓ (dẫn tới STRUCTURAL crisis nặng nhất, healing 91 phiên chậm nhất) | Khớp CHIỀU, nhưng cơ chế thật đã biết là STRUCTURAL credit (Resolution 11), không phải "hấp thụ cung margin" |
| 2020→2022 (dùng khung "từ đáy trước") | CÓ (rally +131,9%/21,5th, lớn thứ 2) | CÓ (dd -40,34% sâu nhất modern, healing 47 phiên chậm thứ 2) | Khớp CHIỀU, nhưng cơ chế thật đã biết là cascade-nested-in-external-crisis (SCB+Fed), không phải riêng "prior trend" |
| 2018 | CÓ (65%/12th, 110%/24th — mạnh) | CÓ (không V-recover, weak 14,8th) | Khớp CHIỀU cho phần "hot→bad", nhưng KHÔNG PHÂN BIỆT ĐƯỢC với 07/2026 |
| **07/2026** | **CÓ (48%/12th — TƯƠNG ĐƯƠNG 2018, KHÔNG "nền bình thường")** | **KHÔNG (hồi nhanh nhất)** | **PHẢN BÁC TRỰC TIẾP** — input gần giống 2018 nhưng output đối lập |

**Kết luận**: giả thuyết có vẻ đúng ở 2 đầu cực trị rõ ràng nhất của phân phối (2020 = yếu nhất/hồi
nhanh nhất; 2009,2022 = 2 rally "từ đáy" LỚN NHẤT/hồi chậm nhất) — nhưng những 2 case cực trị đó
ĐÃ có lời giải thích khác tốt hơn (external shock sạch cho 2020; STRUCTURAL credit cho 2012;
cascade-nested-in-crisis cho 2022). Ở VÙNG GIỮA (12mo return 33-65%, nơi 2018/2022/07/2026 đều rơi
vào) — đúng vùng quyết định thực tế nhất cho 1 trigger sớm — **giả thuyết hoàn toàn KHÔNG phân biệt
được case tốt (07/2026) khỏi case xấu (2018)**. Một tín hiệu chỉ phân biệt được ở 2 đầu cực trị (nơi
đã có tín hiệu khác tốt hơn) nhưng mù ở vùng giữa (nơi cần phân biệt nhất) có giá trị THỰC TẾ RẤT
THẤP làm LEAD indicator độc lập.

**Đề xuất LEAD-6 (yếu, CHỈ dùng bổ trợ, không thay 3-archetype framework)**: dùng "cumulative return
từ đáy khủng hoảng liền trước tới đỉnh hiện tại" (không phải 12/24mo cố định) làm **CẢNH BÁO PHỤ**
khi vượt ngưỡng thô ~**+120-130%** (2 case duy nhất vượt mốc này đều dẫn tới outcome nặng/chậm) —
nhưng với ngưỡng dựng từ N=2, đây là giả thuyết MÔ TẢ, không phải ngưỡng production. Dưới ngưỡng đó
(mọi case 30-65%, gồm cả 07/2026 lẫn 2018), **LEAD-6 không có giá trị phân biệt** — bắt buộc phải
quay lại 3-archetype framework (external_flag tại thời điểm cluster + điều gì xảy ra SAU cluster,
đã có ở `vn_2022_2018_margin_signature_recheck_20260831`) làm công cụ chính, prior-trend không thay
thế được nó.

## Giới hạn phải mang theo

1. **N=6 (hoặc N=5 sau khi loại 2007-2009) quá mỏng cho MỌI suy luận thống kê chặt** — p-value
   trong bảng Bước 3 chỉ để tham khảo độ nhạy, không phải bằng chứng ý nghĩa thống kê; đúng kỷ luật
   đã dùng xuyên suốt 5 job trước.
2. Recovery của 07/2026 **right-censored** (còn đang diễn ra tại thời điểm dữ liệu cutoff 28/08/2026)
   — số +9,80%/38 ngày là chặn dưới, không phải kết quả cuối cùng; nếu tiếp tục hồi mạnh hơn hoặc
   đảo chiều lại, một số so sánh trong bảng Bước 1-2 cần cập nhật.
3. 24mo-return của 2 case (2011-2012, 2020) là số GÂY NHIỄU (đi ngược qua đỉnh khủng hoảng trước) —
   đã tách riêng và cảnh báo ở Bước 3, KHÔNG dùng trực tiếp 2 số này cho bất kỳ ngưỡng nào.
4. "Tháng uptrend liên tục" dùng ngưỡng correction -10% VÀ 2 cách neo running-max khác nhau (toàn
   lịch sử vs từ trough gần nhất) tuỳ case — đây là lựa chọn PHƯƠNG PHÁP LUẬN của job này để tránh
   bẫy peak-thấp-hơn-ATH-cũ, chưa formalize thành 1 công thức duy nhất áp được mọi trường hợp tương
   lai mà không cần xét lại thủ công.
5. Không có dữ liệu định lượng về "nguồn cung niêm yết mới" (IPO/số lượng cổ phiếu mới listing) để
   kiểm định trực tiếp cơ chế "hấp thụ cung" mà user đề xuất cho case 2018 — giả thuyết CƠ CHẾ này
   (không phải giả thuyết THỐNG KÊ prior-trend) vẫn CHƯA được test trong job này, nằm ngoài phạm vi
   dữ liệu VNINDEX.csv/BQ hiện có.
6. Breadth-healing của 2018 KHÔNG được đo trong bất kỳ job nào của chuỗi 5 job trước (chỉ có
   speed_flag/breadth-jump lúc xảy ra cluster, không có "tốc độ lành sau đó") — ô N/A trong bảng
   Bước 1-2 là giới hạn dữ liệu thật, không phải 0.

## Artifact

- `compute_prior_trend.py`, `correlate.py`, `build_table.py` — script tái lập toàn bộ số trong
  report này từ `data/VNINDEX.csv` (Close hàng ngày), chạy bằng `$DNA_PYEXE`
  (`/home/trido/thanhdt/wc_venv/bin/python`, có pandas+scipy; python3 hệ thống KHÔNG có scipy).
