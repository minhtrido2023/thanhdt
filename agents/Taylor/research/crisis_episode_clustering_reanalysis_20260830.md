# crisis_episode_clustering_reanalysis_20260830 — gộp 7 episode theo cụm, đo lại đúng điểm neo

Job `Taylor_20260830_103253`. Mở lại nhánh nghiên cứu ĐÃ ĐÓNG SỔ
(`kb/projects/margin-valuation-spread-20260823.md` NO-GO mọi sizing/gate) — **CHỈ để làm rõ phân
loại/đo lường**, KHÔNG đề xuất wire cơ chế sizing/margin nào. `custom_basket.py`/production KHÔNG
đụng. Việc bắt nguồn từ "Đính chính 2026-08-24" trong file trên (§79-127) — đọc trước, KHÔNG lặp
lại nội dung ở đây, chỉ trích khi cần.

## VERDICT NGẮN

Gộp 3 sóng 2007-04→2009-02, 2009-11→2010-08, 2011-05→2012-01 thành **1 cụm cơ cấu duy nhất
2007-2012** là đúng theo tiêu chí khách quan (khoảng cách <18 tháng VÀ vĩ mô vẫn xấu đi giữa 2
lần). **N độc lập thật giảm từ 7 xuống 5** (không phải 4 như dự kiến — 2018-05 KHÔNG gộp được vào
đâu, xem dưới). Đo lại forward-return từ đúng điểm cụm cơ cấu bắt đầu được xử lý thật (không phải
từ lần dd52 chạm ngưỡng đầu tiên) cho kết quả **yếu hơn hẳn** mọi episode phòng-thủ-có-mục-tiêu —
khung 2 trục của user tách bạch forward return **rõ ràng hơn** phân loại nhị phân cũ, kể cả với
N nhỏ. Đây là **mô tả định tính có căn cứ, KHÔNG phải kết luận thống kê** (N=5, không p-value).

---

## 1. Tiêu chí gộp cụm (khách quan, áp trước khi nhìn forward return của cụm)

> Hai lần `dd52<=-20%` liên tiếp gộp thành 1 cụm nếu: khoảng cách giữa đáy lần trước và cánh tay
> lần sau **<18 tháng** VÀ chỉ báo vĩ mô (CPI YoY, lãi suất chính sách/liên ngân hàng, PE
> percentile) **vẫn đang xấu đi** (không phải đã đảo chiều cải thiện) trong khoảng giữa.

| Cặp | Khoảng cách | Vĩ mô giữa 2 lần | Gộp? |
|---|---|---|---|
| 2009-02-24 (đáy sóng 1) → 2009-11-26 (arm sóng 2) | 9 tháng | Tín dụng vẫn tăng nóng do gói kích cầu/cấp bù lãi suất 4pp (chính cái làm ra cú sốc 11/2009 khi phải rút lại); CPI bắt đầu tái tăng tốc cuối 2009 → XẤU ĐI | **CÓ** |
| 2010-08-25 (đáy sóng 2) → 2011-05-23 (arm sóng 3) | 9 tháng | CPI tiếp tục leo thang suốt 2010→2011 (đỉnh CPI YoY ~23% tháng 08/2011), NQ11 (24/02/2011) siết mạnh hơn hẳn đợt 11/2009 → XẤU ĐI RÕ | **CÓ** |
| 2012-01-06 (đáy sóng 3) → 2012-08-27 (arm ACB) | 8 tháng | SBV bắt đầu **hạ** lãi suất (cắt refinancing 15%→14%, 13/03/2012 — xác nhận bằng BQ dưới), CPI YoY giảm mạnh từ đỉnh 23% (08/2011) xuống ~7% (cuối 2012); PE percentile market đã hồi từ 0,7%ile (đáy 01/2012) lên 31%ile (arm 08/2012, `episodes_dd52.csv`) → **ĐANG CẢI THIỆN, không xấu đi** | **KHÔNG** |

⇒ 2012-08 (ACB) **ở NGOÀI** cụm cơ cấu — nó là cú sốc niềm tin/bank-run xảy ra TRÊN NỀN đã bắt
đầu hồi phục, đúng như đính chính 08-24 đã đọc (nhãn "HỖN HỢP", tự giải quyết). Không đổi.

## 2. Điểm "bắt đầu xử lý thật" của cụm 2007-2012 — không phải 2007-04

Dùng NQ11 (24/02/2011) làm mốc chính sách PIT rõ nhất: lần đầu tiên chính phủ công khai thừa
nhận và tấn công trực diện gốc rễ (siết tăng trưởng tín dụng <20%, cắt tín dụng BĐS/CK) thay vì
các đợt siết-nới xen kẽ nửa vời 2008-2010. Nhưng NQ11 là điểm BẮT ĐẦU tấn công, không phải điểm
tấn công đã CÓ HIỆU LỰC — thị trường tiếp tục giảm 8 tháng sau đó tới đáy 2012-01-06.

Hai điểm neo khách quan, đo bằng dữ liệu thật (không suy đoán):

**(a) Đáy capitulation sâu nhất của cụm — 2012-01-06.** PE percentile tại đáy này = **0,7%ile**
(gần rẻ nhất lịch sử, `episodes_dd52.csv` cột `pe_pit_trough`), so với đáy giữa cụm 2010-08-25 chỉ
**22,5%ile** — xác nhận độc lập bằng dữ liệu định giá rằng đáy 2010-08 KHÔNG phải điểm washout
thật của cụm (đúng như đính chính 08-24 đọc định tính), còn 2012-01-06 mới là.

**(b) Điểm chính sách đảo chiều xác nhận — 2012-03-13** (SBV cắt lãi suất tái chiết khấu lần đầu
của chu kỳ, 15%→14%). Verify bằng BQ: VNINDEX **429,39** ngày đó — đã **cao hơn +27,5%** so với
đáy 2012-01-06 (336,7) → thị trường đã đi trước, phục hồi PHẦN LỚN TRƯỚC KHI chính sách chính thức
xác nhận đảo chiều.

## 3. Forward return đo từ đúng điểm neo (không phải từ lần dd52 chạm ngưỡng đầu tiên)

Tất cả số dưới đây tính bằng cùng 1 methodology `q_trough_stock.sql`
(`extreme_bottom_recognition_20260823/`) — rổ `tav2_mike.universe_pit` đóng băng tại ngày neo,
`Close` từ `tav2_bq.ticker`, median theo mã.

| Điểm neo | VNI fwd12 | VNI fwd24 | **Stock median fwd12** | Stock median fwd24 | n mã |
|---|---:|---:|---:|---:|---:|
| 2007-04-23 (lần dd52 chạm ngưỡng ĐẦU TIÊN — SAI, đã biết) | −44,2% | +110,7% | +130,0%* | +88,9% | 131 |
| 2012-01-06 (đáy capitulation sâu nhất của cụm) | +7,2% | +28,9% | **+21,2%** | +51,2% | 187 |
| 2012-03-13 (chính sách xác nhận đảo chiều — MỚI, query hôm nay) | +10,2% | +38,6% | **−0,6%** | +35,5% | 188 |

*số 2007-04 bị nhiễu bởi đáy toàn cầu GFC 03/2009 (đính chính 08-24 đã chỉ rõ), KHÔNG dùng làm số
đại diện cụm.

**Đọc kết quả:** dù chọn neo tại đáy capitulation hay tại điểm chính sách xác nhận, forward return
của cụm cơ cấu 2007-2012 đo đúng **yếu hơn hẳn** con số bịa từ lần chạm ngưỡng đầu tiên (+130%).
Đáng chú ý: neo muộn hơn (03/2012, sau khi chính sách đã xác nhận) cho kết quả STOCK-LEVEL còn
**âm nhẹ** ở 12 tháng — vì phần lớn upside đã bị thị trường ăn trước trong giai đoạn 01→03/2012
(VNI +27,5%). Đây là bằng chứng trực tiếp cho bài học đính chính 08-24: đo quá SỚM (2007-04) hay
quá MUỘN (03-2012, sau khi giá đã chạy) đều cho số sai lệch theo hai hướng ngược nhau; đáy
capitulation (dd52 trough của SÓNG CUỐI trong cụm — không phải sóng đầu) là điểm neo cân bằng
nhất có sẵn trong dữ liệu.

## 4. N độc lập sau khi gộp — và một phát hiện KHÔNG khớp dự kiến của dispatch

Dispatch dự kiến N giảm còn 4-5. Kết quả thật: **N=5**, nhưng **KHÔNG** phải "4 standalone + 1 cụm"
đơn giản — **2018-05 không gộp được vào cụm cơ cấu 2007-2012** (cách nhau >6 năm, không thoả tiêu
chí khoảng cách) **và cũng không thuộc nhóm phòng-thủ-có-mục-tiêu** (trigger là dòng vốn ngoại rút
khỏi EM + chiến tranh thương mại Mỹ-Trung + Fed thắt chặt — VN không kiểm soát được, không có MỘT
hành động chính sách cụ thể nào chấm dứt được nó, kéo dài hết 2018-2019).

⇒ Khung 2 trục của user thực ra sinh ra **3 nhóm**, không phải 2:

| Nhóm | Episode (N độc lập) | Đặc điểm trục 1/2 |
|---|---|---|
| **A. Cơ cấu tự cộng dồn** | Cụm 2007-2012 (gộp 3 sóng) | Cung tín dụng/CPI dư thừa thật, đa năm |
| **B. Phòng thủ có mục tiêu** | 2012-08 (ACB), 2020-03 (COVID), 2022-05 (SCB/VTP) | Cú sốc niềm tin/ngoại sinh, MỘT hành động chính sách cụ thể chặn được trong vài tuần-tháng |
| **C. Ngoại sinh không kiểm soát được, không có hành động chặn** | 2018-05 (EM outflow + trade war) | Không phải cung tiền VN dư thừa (trục 1 = KHÔNG cơ cấu), nhưng cũng không có 1 hành động chính sách VN nào chấm dứt được nó (trục 2 = KHÔNG tự giải quyết nhanh) |

Nhóm C không phải lỗi phân loại — nó là **hệ quả logic đúng** của việc hỏi 2 câu độc lập thay vì
1 câu nhị phân: trục 1 (nguồn gốc trong/ngoài nước) và trục 2 (có chặn nhanh được không) không
nhất thiết cùng chiều. 2018-05 là ô "không cơ cấu trong nước NHƯNG cũng không chặn nhanh được".

## 5. Khung 2 trục có tách bạch forward return tốt hơn nhị phân cũ không?

**Có, rõ ràng — kể cả với N nhỏ.** So sánh stock-median fwd12 (đo từ đáy/điểm neo phù hợp mỗi ca):

| Nhóm | Episode | Stock median fwd12 | Stock median fwd24 |
|---|---|---:|---:|
| B. Phòng thủ có mục tiêu | 2012-08 | +26,3% | +92,9% |
| B. Phòng thủ có mục tiêu | 2020-03 | **+96,7%** | +206,9% |
| B. Phòng thủ có mục tiêu | 2022-05 | +42,4% | +49,4% |
| A. Cơ cấu (đáy capitulation) | Cụm 2007-2012 | +21,2% | +51,2% |
| A. Cơ cấu (điểm chính sách xác nhận) | Cụm 2007-2012 | −0,6% | +35,5% |
| C. Ngoại sinh không chặn được | 2018-05 | +0,8% | +35,2% |

- **Nhóm B tách BẠCH hoàn toàn khỏi nhóm A+C ở mốc 12 tháng**: min(B)=+26,3% > max(A∪C)=+21,2%.
  Đây là tách hoàn toàn theo đúng tiêu chí PREREG §5 của classifier gốc — **điều mà nhị phân cũ
  KHÔNG làm được** (nhị phân cũ nhét cả 2020-03 lẫn 2009-11/2018-05 vào chung
  `LIQUIDITY_POLICY`, cho khoảng −46,8%→+96,7%, không tách được gì).
- Ở mốc 24 tháng, tách bạch yếu đi (A đuổi kịp một phần — +51,2% so với B thấp nhất +49,4%) —
  hợp lý về mặt cơ chế: khủng hoảng cơ cấu cần NHIỀU thời gian hơn để phần thưởng "đã xử lý xong"
  phản ánh vào giá, đúng định nghĩa "tự cộng dồn, đa năm" chứ không mâu thuẫn với khung 2 trục.
- Nhóm C (2018-05) nằm SÁT nhóm A ở cả 2 mốc thời gian (không phải giữa A và B) — ủng hộ trực
  tiếp cho trực giác trục-2: cái quyết định tốc độ hồi phục không phải "trong nước hay ngoài
  nước" (trục 1) mà là "có bị chặn nhanh bằng MỘT hành động cụ thể hay không" (trục 2). 2018-05
  thua trục 1 (không cơ cấu) nhưng thua CẢ trục 2 (không ai chặn được Fed/chiến tranh thương mại)
  → kết quả yếu giống nhóm cơ cấu, không giống nhóm phòng thủ.

## 6. Thành thật về N

**N=5 episode độc lập** (Cụm 2007-2012, 2012-08, 2018-05, 2020-03, 2022-05), trong đó **nhóm A
(cơ cấu) chỉ có N=1** — không thể nói gì về phân phối/độ lệch chuẩn, chỉ có 1 điểm dữ liệu duy
nhất cho toàn bộ định nghĩa "khủng hoảng cơ cấu tự cộng dồn" trong 26 năm lịch sử BQ. Nhóm B có
N=3 (đủ để nói "tách bạch" theo nghĩa min>max giữa 2 nhóm, không đủ để nói gì về phân phối bên
trong nhóm B). Nhóm C có N=1.

**Đây là mô tả định tính có căn cứ (qualitative pattern, evidence-based), KHÔNG phải kết luận
thống kê.** Không tính p-value, không DSR/PBO (không áp dụng — đây không phải backtest tham số
hoá, không có gì để overfit). Sự tách bạch min(B)>max(A∪C) ở N=7 tổng (3+1+3, đã gộp đúng) là
bằng chứng ĐỊNH HƯỚNG mạnh hơn hẳn nhị phân cũ, nhưng 1 episode mới thuộc bất kỳ nhóm nào (vd 1
đợt cơ cấu mới trong tương lai) hoàn toàn có thể phá vỡ kết luận này — không có cơ sở để tuyên bố
"confirmed" hay đặt ngưỡng phân loại số cứng.

## 7. Không đổi gì so với đính chính 08-24

- Verdict Phase 1 (`extreme_bottom_mechanism_classifier_20260823`) vẫn **NO-GO** — không đảo
  ngược, không tính vào N_trials của project margin-valuation-spread nào.
- KHÔNG đề xuất wire bất kỳ cơ chế sizing/gate/margin nào theo giai đoạn thị trường. Mục đích
  thuần là nền tảng nhận thức cho nghiên cứu sau (đúng phạm vi dispatch).
- `custom_basket.py`/production không bị đụng tới trong job này.

---

*Nguồn dữ liệu*: `extreme_bottom_mechanism_classifier_20260823/classification.csv` (nhãn A/B gốc,
nguồn tin tức đã cite), `extreme_bottom_recognition_20260823/episodes_dd52.csv` +
`trough_stock_forward.csv` (7 episode gốc, PE percentile), 2 truy vấn BQ mới hôm nay (VNINDEX +
stock-level forward return anchor tại 2012-03-13, dùng lại nguyên `q_trough_stock.sql` template).
