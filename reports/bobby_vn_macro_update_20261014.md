# Cập nhật vĩ mô VN: tài chính và BĐS, tầm nhìn 6-12 tháng (Bobby, 2026-10-14)

> **Chế độ đọc**: PROSPECTIVE. Caller không cung cấp forward-return hay giả thuyết backtest nào, và tôi
> không dùng thứ gì như vậy. Có dùng giá VNINDEX ĐÃ xảy ra (tới 13/10) làm bối cảnh, vì đó là dữ kiện
> point-in-time ai cũng biết. Mọi xác suất trong file này là **JUDGMENT**, không phải thống kê: số
> episode so sánh được rất nhỏ.
> **Mốc so sánh**: thesis 2026-08-26 (`kb/projects/vn-realestate-structural-risk-20260826.md`,
> `reports/bobby_vietnam_realestate_risk_20260826.md`), interim tháng 10
> (`kb/projects/vn_realestate_monthly_checks/2026-10.md`), phụ lục đa-proxy
> (`.../2026-10-multiproxy.md`).
> **Phạm vi ghi**: tôi chỉ ghi file này, theo đúng yêu cầu caller. CHƯA cập nhật registry
> `kb/data_registry/market-state/vn_macro_regime_history.md` và CHƯA ghi bus event. Hai việc đó để
> orchestrator làm.

> **ĐÍNH CHÍNH 14/10 CHIỀU (theo chỉ đạo user).**
> - **Sai ở bản sáng:** tôi dùng số NHNN "lãi suất huy động bình quân giao dịch mới khoảng 6,4%" làm
>   số lãi huy động chính (mục 3 hàng A', đoạn "Đồng thuận", mục 9). Số đó là bình quân có trọng số
>   của MỌI kỳ hạn trên toàn hệ thống, kể cả nhóm dưới 6 tháng bị trần 4,75%, và công bố trễ khoảng 3
>   tuần. Team không theo dõi số này.
> - **Số lãi huy động chính, áp dụng từ bản này:** effective rate của team = max(Big-4 tiết kiệm 12M,
>   CCTG Big-4 12M) = **7,4%/năm, as-of 12/10/2026**. Cách tính: Big-4 12M = 6,8%; CCTG BIDV/VietinBank
>   12M = 7,4%. Số lấy từ `deposit_rate_vn.effective_deposit_rate()`, chạy lại 14/10. **Mức này thấp
>   hơn ngưỡng kill-switch A (>7,5%) đúng 0,1pp.**
> - **Số 6,4% vẫn giữ**, nhưng chỉ là proxy phụ (tầng A' mục 3). Nó đo một đại lượng khác, xem 3.0.
> - **Phần ĐỔI:**
>   - Thêm mục 3.0: số chính và bảng đa-proxy.
>   - Tầng D cập nhật liên ngân hàng tuần 05-09/10 (VBMA, ngoài dữ liệu team).
>   - Bảng 7 ngưỡng: ô #2 và ô #3 nay đã có số, cả hai đều KHÔNG chạm. Ô #5 có một vấn đề định nghĩa
>     cần user chốt.
>   - Tín hiệu #2 (mục 7) thêm kill-switch A: chỉ cần CCTG 12M lên 7,6% là ngưỡng này ARM.
>   - Kết luận chi phí vốn nói rõ khoảng cách 0,1pp tới kill-switch A. Bản sáng đã làm mờ chi tiết này.
> - **Phần KHÔNG đổi:** trục 1 và trục 2, giai đoạn GIỮA, mức tin cậy AMBIGUOUS, xác suất kịch bản.
>   Lý do: 6,4% chỉ là bằng chứng phụ cho "tăng ngầm nửa đầu năm". Các mức biên 7,4-9,2% đã nằm trong
>   lập luận của bản sáng.
> - **Kết quả kiểm ngưỡng:** 0/7 ngưỡng tăng ngầm bị chạm. Kill-switch A: CLEAR.
> - **Phát hiện phụ (chỉ báo cáo, không sửa):**
>   - Code ghi `rate_source = "cctg_6m(2026-10-12)"`, trong khi chuỗi đã chuyển sang kỳ hạn 12M từ
>     05/10. Đây là lỗi nhãn, số liệu không sai.
>   - Mục 4 và mục 9 ghi "kết quả FOMC 9/2026: không xác minh". Registry 13/10 lại ghi Fed 3,75-4,00%
>     từ 16/09. Hai chỗ này lệch nhau, nằm ngoài phạm vi đính chính và chưa được sửa.

---

## 0. Kết luận một câu

**GIỮ phân loại STRUCTURAL_ACCUMULATION (trục 1) và KHÔNG CONTAINABLE bằng một can thiệp (trục 2).
Độ tin cậy vẫn AMBIGUOUS, nhưng dời giai đoạn từ "sớm-giữa" sang "GIỮA".** Lý do: (a) chính NHNN nay
công khai gọi tên rủi ro lệch kỳ hạn, đồng thời lại nới trần LDR 85%→95%; (b) "bộ giáp ngoài" từng là
lợi thế lớn nhất so với Thái Lan 1997 đã mỏng đi rõ: 9 tháng nhập siêu 19,4 tỷ USD, cùng kỳ năm
trước xuất siêu 16,9 tỷ; (c) tồn kho BĐS tăng, giá thứ cấp nhích xuống, thanh khoản thấp, tức là đúng
kịch bản "đóng băng" mà playbook coi là nguy hiểm nhất với hệ mình. **Chưa có ngưỡng escalate định
lượng nào bị chạm.** Tỷ trọng tín dụng BĐS còn hơi GIẢM (25,5% → 25,39%). Vi phạm TPDN 12 tháng chỉ
0,24%. Lạm phát cơ bản đang giảm. Lãi huy động chính (effective rate của team) là **7,4%** tại 12/10,
thấp hơn kill-switch A (>7,5%) 0,1pp. Đây là số đã đính chính lúc chiều 14/10.

---

## 1. Sự kiện kích hoạt: họp Ban Chỉ đạo TW về nhà ở và thị trường BĐS, 13/10/2026

**Nguồn**: caller dẫn Tuổi Trẻ/Chinhphu.vn 13/10/2026. ⚠️ **Tôi chưa tự đọc được bài gốc.** WebSearch
14/10 chưa lập chỉ mục bài nào về phiên họp này. Tôi chỉ xác minh được bối cảnh: QĐ 1666/QĐ-TTg
(27/08/2026) kiện toàn Ban Chỉ đạo, PTT thường trực Phạm Gia Túc làm Trưởng ban, Bộ trưởng Xây dựng
làm Phó ban ([VietnamPlus](https://www.vietnamplus.vn/kien-toan-ban-chi-dao-trung-uong-ve-chinh-sach-nha-o-va-thi-truong-bat-dong-san-post1133206.vnp)).

**Kiểm tra nhất quán nội tại (tôi tự làm):**
- 5,21 triệu tỷ = 25,39% tổng dư nợ, suy ra tổng dư nợ khoảng 20,52 triệu tỷ tại 31/8. Số này nằm
  giữa 20,03 triệu tỷ (29/6) và 20,75 triệu tỷ (30/9, NHNN). **Khớp.**
- +9,49% so cuối 2025, suy ra gốc khoảng 4,76 triệu tỷ. Thesis 08-26 ghi cuối 2025 là 4,74 triệu tỷ.
  **Khớp.**
- Tôi coi bộ số này là đáng tin ở mức "nguồn chính thức qua báo chí, nhất quán nội tại".

**Đọc theo khung Bobby:**
1. **Tín dụng BĐS CHẬM LẠI tương đối trong tháng 7-8** (đây là dữ kiện mới quan trọng nhất về lượng).
   - Hết 6 tháng: BĐS +8,3% YTD, nhanh hơn tổng tín dụng (+7,73%).
   - Hết 8 tháng: BĐS +9,49%, CHẬM hơn tổng tín dụng (+10,24% tại 28/8).
   - Tức là trong tháng 7-8, tín dụng BĐS chỉ tăng khoảng 1,1%, còn tổng tín dụng tăng khoảng 2,3%.
     Điều này khớp với câu "tiếp cận tín dụng còn khó".
   - ⚠️ **Không biết**: các văn bản nới (30/05 loại NƠXH/KCN/KCX; CV 8509 ngày 16/09 loại phần tăng thêm
     cho khách sạn/du lịch/nghỉ dưỡng) có làm đổi cách THỐNG KÊ con số "dư nợ BĐS" hay chỉ đổi cách tính
     ROOM. Nếu đổi cả thống kê thì một phần của "chậm lại" là artifact đo lường.
2. **Cơ quan quản lý TỰ gọi tên rủi ro lệch kỳ hạn** (vốn ngắn hạn tài trợ tài sản dài hạn), đồng thời
   hướng tới đa dạng hoá huy động trung-dài hạn. Theo quy tắc của tôi, đây là thừa nhận áp lực vốn.
   Lời thừa nhận này đi CÙNG LÚC với Thông tư 50/2026/TT-NHNN nới trần LDR (mục 3E). Hai tín hiệu ngược
   hướng nhau: một bên nói rủi ro thanh khoản, một bên nới giới hạn lượng.
3. **Phía cầu nhà ở bị nghẽn, không phải phía cung tiền.**
   - Giá vượt khả năng chi trả. Giao dịch Q3 khoảng 92.004, bằng 92% quý trước (−8% QoQ; **YoY: không
     có số**).
   - Giá thứ cấp chung cư/đất nền "có xu hướng giảm nhưng vẫn cao".
   - Tồn kho 27/34 địa phương khoảng 51.950 căn/lô/nền và đang TĂNG. Số này do chủ đầu tư tự báo nên
     nhiều khả năng là cận dưới.
   - Đây là chữ ký của pha "tích tụ → chững". Nó chưa phải "đổ vỡ".
4. **Phản ứng chính sách là toàn hệ thống và đa đầu mối.** Gồm: rà soát tồn kho, tín dụng chính sách
   nhà ở, giao 1 đầu mối cho dự án tồn đọng (bí thư cấp uỷ chỉ đạo), sửa 3 luật. Không có biện pháp nào
   nhắm vào MỘT tổ chức hay MỘT sự kiện. Theo trục 2, đó là dấu hiệu của vấn đề KHÔNG containable bằng
   một hành động. Hướng chính sách vẫn là **gỡ và nới để giữ tăng trưởng**, không phải siết để xử lý
   mất cân bằng.

---

## 2. Bảng lead indicator so với ngưỡng (thesis 08-26)

| Chỉ báo | Ngưỡng cảnh báo / nguy hiểm | Mốc 08-26 | **Hiện tại (nguồn, ngày)** | Chạm? | Hướng |
|---|---|---|---|---|---|
| Tín dụng BĐS/tổng | >28% / >30% | 25,5% (30/6) | **25,39%** (31/8; NHNN tại họp 13/10, qua caller) | Không | Đi ngang, hơi giảm. ⚠️ số chính thức là CẬN DƯỚI |
| Vi phạm TPDN 12 tháng | >2% / >5% | 0,3% (Q2) | **0,24%** (T8/2026, VIS Rating qua báo chí) | Không | Thấp. Tồn đọng chưa khắc phục: 6,7% dư nợ chậm lãi, 3,1% chậm gốc |
| Volume giao dịch BĐS | −50% YoY 2 quý liên tiếp | — | Q3 = 92% Q2 (BXD, qua caller); **YoY không có số** | Không có số | Giảm nhẹ QoQ |
| Liên NH qua đêm | >6% đột biến | — | **4,52%** tại 09/10 (+179bp trong tuần; bình quân tuần 1,89%). Nguồn: VBMA tuần 05-09/10, **ngoài dữ liệu team** | Không | Giật lên cuối tuần. Đã từng có đỉnh 11% (01/06) và 6% (31/07) |
| NPL công bố | >3% / >5% | 1,97% (Q2) | **Q3 chưa công bố** | Chưa có số | Q1→Q2 tăng tốc |
| VND | mất giá >3%/tháng | — | VND **tăng giá khoảng 1,1% YTD** (NHNN, họp báo 07/10) | Không | Ổn định |
| Dự trữ ngoại hối | <60 tỷ USD | 87,6 tỷ (18/6) | **Không có số mới hơn 18/6** | Không | Không biết |
| Rollover TPDN BĐS | >100K tỷ thất bại/quý | — | Q4/2026: tổng đáo hạn khoảng 77K tỷ (VIS; 1 nguồn ghi 83K), BĐS dân cư khoảng 40K tỷ, **28K tỷ đã thuộc nhóm chậm trả/gia hạn** | Không thể chạm trong Q4 (tổng đáo hạn < ngưỡng) | Q2/2027 khoảng 84K tỷ |
| CPI | relapse trên trần 4,5% + core | 5,60% đỉnh (T5) | CPI chung **5,08%**, core **4,45%** đang giảm (T9, Cục Thống kê 02/10); bình quân 9 tháng 4,52% | Đã escalate T9, nay là chi phí đẩy, lệch trục | CPI chung ↑, core ↓ |

**Bảy ngưỡng "tăng ngầm" chi phí vốn (user duyệt 07/10 và 13/10):**

| # | Ngưỡng | Mốc | Hiện tại | Chạm? |
|---|---|---|---|---|
| 1 | Spread CCTG Big-4 − tiết kiệm 12M online ≥1,0pp hoặc nới ≥0,3pp | 12M 0,6 · 6M 0,7 | 12M 7,4−6,8 = **0,6** · 6M 7,5−6,8 = **0,7** (CSV nội bộ 12/10) | Không |
| 2 | Top-5 tư nhân 12M tăng ≥0,3pp/3 tháng hoặc ≥15 NH ≥7% | khoảng 7,2% · 10 NH | **Khoảng 7,2%** (10/10). Top-5 theo mức: Sacombank 7,5 · LPBank 7,2 · SaigonBank 7,2 · Bắc Á 7,1 · VPBank 7,1. Nguồn: khảo sát 37 NH của TCKTTC ngày 10/10, **ngoài dữ liệu team**. Có ≥9 NH ≥7% được nêu tên (bài không đếm đủ). ⚠️ Registry 13/10 ghi ACB online 12M 8,0% (khoảng 05/10), nhưng khảo sát 10/10 không có số này. Nếu tính ACB thì top-5 khoảng 7,4%. Tiêu đề "VPBank 7,9%" chưa kiểm | Không (+0,0 đến +0,2pp; dưới 15 NH) |
| 3 | Liên NH 3M bình quân tháng >7,5% | khoảng 6,9% | **6,75%** tại 09/10, bình quân tuần 6,58%. Bình quân tháng 9 khoảng 6,98% (registry 13/10). Tháng 10 chưa đủ tuần để tính bình quân tháng. Nguồn: VBMA, **ngoài dữ liệu team** | Không |
| 4 | Tín dụng YTD − huy động YTD ≥2pp (cùng phạm vi, cùng mốc) | −0,4pp (22/08, chỉ VND) | **+1,11pp** = 10,89% − 9,78% (cùng nguồn Cục Thống kê, cùng ngày 28/9, phạm vi toàn hệ thống) | Không. ⚠️ khác phạm vi mốc 22/08 nên KHÔNG kết luận được "nới rộng 1,5pp" |
| 5 | Tiền gửi lớn ≥10% kéo dài 2 tháng | PVcomBank 10% (07/09) | PVcomBank 10% (từ 2.000 tỷ, tại quầy, kỳ hạn 12-13 tháng). Xác nhận ngày 02/09 và 10/09 qua kết quả tìm kiếm Lao Động, chưa đọc thân bài. **Tháng 10: không có số** (tìm ngày 14/10 không ra bài nào) | Không có số. ⚠️ **Vấn đề định nghĩa:** mốc đã nằm ĐÚNG ở ngưỡng 10%. Tiêu đề Lao Động tháng 7 cũng ghi "cao nhất 10%" (chưa kiểm có phải PVcomBank không). Đọc theo chữ thì ô này có thể đã "chạm" từ trước khi ngưỡng được đặt. **Đề xuất user chốt**: tính ngưỡng từ mốc, tức cần >10% hoặc có NH thứ hai ≥10%. Bobby chỉ đề xuất, không tự đổi |
| 6 | CCTG nhóm sau Big-4, bậc 100tr ≥9,5% hoặc +0,3pp | VPB 9,2% (13/10) | Chưa có kỳ mới | Không |
| 7 | Trái phiếu cấp 2 Big-4: biên ≥2,75pp | CTG 10/2026 +2,25 (đang chào bán) | Không có đợt mới | Không |

**Kết quả (cập nhật chiều 14/10): 0/7 ngưỡng bị chạm.** Ô #5 vẫn không có số, kèm câu hỏi định nghĩa.
Ô #6 và #7 chưa có kỳ mới để so. Ô không có số thì không coi là an toàn. **Kill-switch A** (effective
>7,5%): CLEAR, effective đang ở 7,4%, còn cách 0,1pp.

---

## 3. Chi phí vốn và thanh khoản: bảng 5 tầng (dữ liệu tới 14/10)

### 3.0 Lãi huy động: số CHÍNH và bảng đa-proxy (đính chính 14/10 chiều)

**Số chính: effective rate của team = 7,4%/năm, as-of 12/10/2026.**
- Công thức: max(Big-4 tiết kiệm 12M, CCTG Big-4 12M) = max(6,8%; 7,4%).
- Code: `deposit_rate_vn.effective_deposit_rate()` và `macro_killswitch_a_status()`, chạy lại 14/10.
  Kết quả: `armed=False`, `age_days=2`.
- Dữ liệu: `data/deposit_rate_vn_events.csv` và `data/cctg_rate_vn_events.csv`, do cron tuần thứ Hai
  cập nhật. Lần chạy kế tiếp: 19/10, 08:05 ICT.
- Số liệu còn tươi (2 ngày).

| Proxy | Số | As-of | Nguồn | So với kill-switch A (>7,5%) | Ngưỡng "tăng ngầm" liên quan |
|---|---|---|---|---|---|
| Big-4 tiết kiệm 12M (lấy kênh cao nhất) | 6,8% online · 5,9% tại quầy | 12/10 · quầy 01/10 | CSV team | −0,7pp | Mẫu số của #1. Thesis "+0,3pp/tháng": không chạm |
| **Effective = max(Big-4 12M, CCTG Big-4 12M)** | **7,4%** (BIDV/CTG 12M) | **12/10** | code team | **−0,1pp, CLEAR** | — |
| CCTG Big-4 6M (tham chiếu) | 7,5% (VCB, chỉ phát hành 6M) | 12/10 | CSV team, kỳ hạn 6M | Bằng mức 7,5%, không vượt. KS-A dùng kỳ hạn 12M | #1: spread 6M 0,7pp |
| Spread CCTG Big-4 − tiết kiệm online | 12M 0,6pp · 6M 0,7pp | 12/10 | team | — | #1 (≥1,0pp hoặc nới ≥0,3pp): không chạm |
| Top-5 tư nhân, 12M biểu chuẩn | khoảng 7,2% (khoảng 7,4% nếu tính ACB 8,0%) | 10/10 (ACB khoảng 05/10) | TCKTTC, **ngoài dữ liệu team** | −0,3pp (hoặc −0,1pp) | #2: không chạm |
| CCTG nhóm 2 (tier-2) | VPB 9,2% (10tr và 100tr) · ACB 7,2% (3M) · MB 7,1% (6-9M) · TCB không có số | 13/10 | `data/cctg_rate_vn_tier2_events.csv` | VPB +1,7pp · ACB −0,3pp · MB −0,4pp | #6 (VPB 100tr ≥9,5% hoặc +0,3pp): không chạm |
| Liên NH 3M | 6,75% (bình quân tuần 6,58%) | 09/10 | VBMA tuần 05-09/10, **ngoài dữ liệu team** | −0,75pp | #3 (bình quân tháng >7,5%): không chạm |
| Liên NH 1M / 6M | 5,15% / 8,16% (kỳ 6M giao dịch rất mỏng) | 09/10 | VBMA | 6M +0,66pp | Vế phụ của #3 (1M > Big-4 12M): không chạm |
| Tiền gửi lớn | PVcomBank 10% (từ 2.000 tỷ, tại quầy) | **10/09, STALE hơn 1 tháng** | báo chí, qua kết quả tìm kiếm | +2,5pp | #5: tháng 10 không có số |
| *Proxy phụ:* NHNN, bình quân giao dịch mới | 6,38% (+1,15pp YTD) · 6,46% (+1,22pp, Bộ Tài chính) | 20/09 · 30/09 | NHNN họp báo 07/10 · BTC 09/10 | −1,1pp | Không phải ngưỡng |

**Vì sao 6,4% KHÔNG phải số chính:**
- Đó là bình quân có trọng số của toàn bộ giao dịch huy động MỚI, trên mọi kỳ hạn và toàn hệ thống.
- Nó gồm cả nhóm dưới 6 tháng bị trần 4,75%: 17/37 NH niêm yết kỳ hạn 3M đúng mức 4,75% (TCKTTC 10/10).
- Số này công bố trễ khoảng 3 tuần.
- Như vậy nó đo MẶT BẰNG BÌNH QUÂN. Nó không đo chi phí biên kỳ hạn 12M, là số team dùng cho
  kill-switch và hurdle.
- Nó vẫn hữu ích về HƯỚNG: mức +1,2pp YTD xác nhận lãi huy động đã tăng thật trong nửa đầu năm.
  Nhưng nó không dùng được để đọc MỨC.

| Tầng | Chỉ tiêu | Số (ngày, nguồn) |
|---|---|---|
| A | Big-4 tiết kiệm 12M online | **6,8%**. Agribank/VCB/BIDV/CTG đều 6,8% (CSV `deposit_rate_vn_events.csv` 12/10; Kenh14 09/10, Dân trí 05/10, VietnamNet 07/10) |
| A | Big-4 12M tại quầy | 5,9% (TTTCTT 01/10). Không có số mới hơn |
| A | Big-4 6M quầy / online | 3,5% quầy (01/10) · online 6,6% (registry 13/10, nguồn gốc chưa ghi rõ) |
| A' | *Proxy phụ, KHÔNG phải số chính:* lãi suất huy động bình quân giao dịch mới (toàn hệ thống, mọi kỳ hạn) | Khoảng 6,4% (6,38%) tại 20/9, +1,2pp so cuối 2025 (NHNN, họp báo Q3 07/10, [SGGP](https://www.sggp.org.vn/nhnn-tiep-tuc-dieu-hanh-chinh-sach-tien-te-linh-hoat-post875371.html)). 6,46% tại 30/9 (Bộ Tài chính 09/10, theo registry 13/10). Số này khác bản chất với số chính 7,4%, xem 3.0 |
| B | CCTG Big-4 | VCB 6M **7,5%** (chỉ phát 6M) · BIDV/CTG 12M **7,4%**, 6M 7,2% (CSV `cctg_rate_vn_*` 12/10) |
| B | Spread CCTG − tiết kiệm online | 12M +0,6pp · 6M +0,7pp. Không đổi so với 07/10 |
| C | CCTG nhóm sau Big-4 | VPB Super Thịnh Vượng **9,2%** (10tr và 100tr, user xác nhận 13/10) · MB 7,1% (6-9 tháng) · ACB 7,2% (3 tháng) · TCB không có số |
| C | Tư nhân 12M biểu chuẩn | Sacombank 7,5 · LPBank/SaigonBank 7,2 · Bắc Á/VPBank 7,1 · VCBNeo/MBV/PGBank/VIB 7,0. Big-4 tại quầy 5,9 (TCKTTC 10/10, khảo sát 37 NH, **ngoài dữ liệu team**). ACB online 8,0% (khoảng 05/10, registry 13/10). Spread top tư nhân − Big-4 online khoảng 0,7pp, không đổi |
| D | Liên NH | Ngày 09/10: ON **4,52** · 1W 4,94 · 2W 5,25 · 1M 5,15 · 3M **6,75** · 6M 8,16 · 9M 8,50. Bình quân tuần: ON 1,89, 3M 6,58. Ngày 02/10: ON 2,73 · 3M 6,73. Nguồn: VBMA "Báo cáo tuần thị trường tiền tệ 5/10-9/10/2026", số NHNN, **ngoài dữ liệu team** |
| D | OMO / TPCP | OMO lưu hành 133 nghìn tỷ (02/10) giảm còn **96,78 nghìn tỷ** (09/10). Trong tuần NHNN bơm 10,1 nghìn tỷ nhưng có 46,7 nghìn tỷ đáo hạn, nên hút ròng 36,6 nghìn tỷ. Lãi suất OMO 4,5%. NHNN **giữ nguyên lãi suất điều hành** (07/10). Phiên đấu thầu TPCP 07/10: trúng thầu kỳ hạn 5Y và 10Y đạt 100%, lãi suất không đổi, tức không có dấu hiệu Kho bạc neo giá như phiên 30/09 (trúng 33%) (VBMA) |
| D | USD/VND | VND +1,1% YTD (NHNN 07/10). Mức tỷ giá trung tâm tháng 10: **không xác minh** |
| E | Tín dụng | **+11,59% YTD, +16,69% YoY, khoảng 20,75 triệu tỷ** (30/9, PTĐ Phạm Thanh Hà, [VNBA 05/10](https://vnba.org.vn/vi/du-no-tin-dung-toan-he-thong-dat-khoang-20-75-trieu-ty-dong-tinh-den-30-9-2026-23786.htm)). Cùng nguồn Cục Thống kê ngày 28/9: tín dụng +10,89%, huy động +9,78% ([TCKTTC 05/10](https://tapchikinhtetaichinh.vn/tin-dung-tang-nhanh-hon-huy-dong-ap-luc-can-doi-nguon-von-168686.html)) |
| E | Kỳ vọng cả năm | TCTD kỳ vọng **16,4%**, vượt định hướng 15% (khảo sát NHNN Q4, [VnBusiness](https://vnbusiness.vn/nhu-cau-von-tang-cao-tang-truong-tin-dung-co-the-vuot-muc-tieu-dinh-huong-15.html)) |
| E | **Sự kiện nới lượng** | **TT 50/2026/TT-NHNN** (ký 30/09, hiệu lực 01/12/2026): trần LDR **85%→95%**, công thức mới (vốn chủ sở hữu và vốn vay nước ngoài vào mẫu số), LCR/NSFR theo lộ trình từ 01/10/2028. ⚠️ Điều khoản chuyển tiếp có 2 cách đọc trên báo, chưa đọc văn bản gốc ([TTTCTT](https://thitruongtaichinhtiente.vn/ngan-hang-nha-nuoc-dieu-chinh-ldr-len-95-tung-buoc-ap-dung-chuan-basel-iii-85975.html), [Thời báo TCVN](https://thoibaotaichinhvietnam.vn/ty-le-ldr-tang-theo-cong-thuc-moi-tran-95-van-rong-voi-phan-lon-ngan-hang-204924.html)). Ngoài ra có: CV 8509 (16/09); cơ chế loại trừ dư nợ dự án lớn/trọng điểm khỏi room; QĐ 1743 (trước đó) |

**Đồng thuận (sửa chiều 14/10):**
- Các proxy thống nhất HƯỚNG đi ngang:
  - Số chính (effective) giữ 7,4% từ 05/10 (lúc rebase) tới 12/10.
  - CCTG VCB 6M giữ 7,5% từ 04/2026.
  - Big-4 12M online giữ 6,8% từ tháng 6.
  - Top-5 tư nhân khoảng 7,2%, ngang mốc 07/10.
  - Liên NH 3M nhích nhẹ 6,73 lên 6,75.
- Proxy phụ của NHNN (6,38-6,46%, +1,2pp YTD) chỉ đồng thuận về HƯỚNG trong nửa đầu năm, tức xác
  nhận lãi huy động đã tăng thật. Nó không dùng để đọc MỨC.

**Phân kỳ và cơ chế:**
- (i) **MỨC**: số chính 7,4% cao hơn Big-4 niêm yết (6,8%) 0,6pp và cao hơn bình quân của NHNN
  khoảng 1,0pp. Tiền có điều kiện chịu 9,2-10%. Các khoảng chênh này không đổi so với 07/10.
- (ii) **Giá bị neo, nên lượng phải nới** *(suy luận)*. Lãi suất bị neo hành chính (CV 2342, TB 117,
  CV 3972), vì thế áp lực vốn không lộ qua giá mà lộ qua chuỗi văn bản nới LƯỢNG: LDR 95%, loại trừ
  room, QĐ 1743. Theo quy tắc của tôi, mỗi văn bản là một lần cơ quan quản lý gián tiếp thừa nhận áp
  lực vốn. Ngay sau đó NHNN lại nói thẳng về rủi ro lệch kỳ hạn tại họp 13/10. Hai chiều này cùng tồn
  tại, và đó là thông tin: hệ thống được cho phép kéo căng bảng cân đối thêm, chứ không được giảm tải.
- (iii) **Liên NH ngắn hạn giật lên vào cuối tuần 09/10**: ON bình quân tuần 1,89% nhưng cuối tuần
  4,52%; 1W lên 4,94%. Cùng tuần đó NHNN hút ròng 36,6 nghìn tỷ qua OMO. *Suy luận*: NHNN đang chủ
  động rút thanh khoản dư sau cuối quý, chưa phải stress. ON vẫn dưới mốc 6%, kỳ 6M giảm 84bp.

**Kết luận chi phí vốn (sửa chiều 14/10):**
- **HƯỚNG**: đi ngang. Độ tin cậy trung bình.
- **MỨC**: số chính là **7,4%**, cao hơn Big-4 niêm yết 0,6pp. Độ tin cậy trung bình-cao.
- **Khoảng cách tới kill-switch A (>7,5%) chỉ còn 0,1pp.** Bản sáng đã làm mờ điểm này khi đặt số
  6,4% lên đầu.
- Hiện không ngưỡng nào kêu. Nhưng chỉ cần BIDV hoặc CTG nâng CCTG 12M lên 7,6% là kill-switch A ARM.
  Kill-switch A là display-only, không code production nào đọc nó (current_ops).

---

## 4. Các số vĩ mô khác (đã kiểm nguồn)

| Chỉ tiêu | Số | Nguồn (ngày) |
|---|---|---|
| GDP Q3/2026 | **+9,95%** YoY (Q1 8,15%, Q2 8,81%); 9 tháng **+9,01%** (cao nhất khoảng 15 năm); CN-XD +12,50%; tích luỹ tài sản **+21,39%**; tiêu dùng cuối cùng +8,96% | Cục Thống kê 03/10 qua [VTC](https://vtcnews.vn/gdp-quy-iii-2026-tang-9-95-9-thang-tang-9-01-ar1043199.html), [TTTCTT](https://thitruongtaichinhtiente.vn/gdp-quy-iii-2026-tang-but-pha-9-95-dua-tang-truong-9-thang-dat-9-01-86006.html). Số ƯỚC TÍNH |
| CPI T9 | Chung 5,08% YoY, core 4,45%; bình quân 9 tháng 4,52% / core 4,26%; nhà ở-VLXD +6,47% YoY | Cục Thống kê 02/10 (đã đọc PDF trong interim 10-2026) |
| Thương mại 9 tháng | XK 434,3 tỷ USD (+24,5%), NK 453,7 tỷ (+36,7%), **nhập siêu 19,42 tỷ** (cùng kỳ 2025: xuất siêu 16,87 tỷ). T9 xuất siêu 1,27 tỷ, chấm dứt 9 tháng nhập siêu. Khu vực FDI **+14,86 tỷ**, trong nước **−34,28 tỷ**. NK điện tử +71,7% | Cục Thống kê qua [TTTCTT 12/10](https://thitruongtaichinhtiente.vn/xuat-sieu-tro-lai-trong-thang-9-tin-hieu-tich-cuc-cho-thuong-mai-86227.html) |
| Cán cân vãng lai 9 tháng | **Không có số** | — |
| Tổng vốn đầu tư 9 tháng | 3.109,6 nghìn tỷ, +15,1% (Q3 +16,7%) | Cục Thống kê qua TCKTTC 05/10 |
| Huy động qua TTCK 9 tháng | 731,6 nghìn tỷ, **+85,6%** YoY | Cục Thống kê qua TCKTTC 05/10 |
| FDI đăng ký/giải ngân 9 tháng | Tiêu đề "vượt 50 tỷ USD" nhưng thân bài **không xác nhận**. Giải ngân FDI và đầu tư công: **không xác minh** | [Mekong ASEAN](https://mekongasean.vn/fdi-dang-ky-vao-viet-nam-vuot-moc-50-ty-usd-sau-9-thang-60270.html) |
| Dự trữ ngoại hối | 87,6 tỷ USD (18/6). **Không có số mới hơn** | [Báo Đấu thầu](https://baodauthau.vn/den-186-du-tru-ngoai-hoi-dat-876-ty-usd-post201374.html) |
| Bên ngoài | Dầu >100 USD/thùng (gián đoạn Hormuz); Fed 3,50-3,75% (T7), thị trường đặt cược tăng tháng 9. **Kết quả FOMC 9/2026: không xác minh.** NHNN (07/10) kỳ vọng Fed "tăng thêm một lần" trước cuối năm | [VCCI](https://vcci.com.vn/tin-tuc/goldman-sachs-du-bao-fed-se-tang-lai-suat-trong-thang-9-2026), SGGP 07/10 |
| TPDN | Đáo hạn Q4/2026 khoảng 77K tỷ (1 nguồn 83K), Q1/2027 khoảng 31K, Q2/2027 khoảng 84K. BĐS dân cư Q4 khoảng 40K tỷ; 28K tỷ trong Q4 đã chậm trả/gia hạn | VIS Rating qua [Tiền Phong](https://tienphong.vn/trai-phieu-doanh-nghiep-chiu-ap-luc-dao-han-vao-quy-cuoi-nam-post1881328.tpo) |
| Chứng khoán | VNINDEX 1.853 (04/09) → 1.768,6 (30/09) → **1.719,4 (13/10)**, khoảng −7,2% từ đầu tháng 9 (BQ `tav2_bq.ticker`, giá quá khứ). Khối ngoại bán ròng YTD khoảng 92-95 nghìn tỷ (2 nguồn lệch, **chưa xác minh**). FTSE Secondary Emerging hiệu lực 21/09; vào rổ 4 đợt tới 09/2027 | BQ; [VFS qua TH&CL](https://thuonghieucongluan.com.vn/chuyen-gia-vfs-vn-index-buoc-vao-thang-10-trong-trang-thai-than-trong-a336335.html); FTSE 06/10 |
| Luật | Kỳ họp thứ Hai QH khoá XVI **khai mạc 17/10**. Luật Đất đai/Nhà ở/KDBĐS (sửa đổi) được trình. Thời điểm THÔNG QUA (kỳ này hay cuối năm) có 2 nguồn lệch nhau, **chưa xác minh** | [TTTCTT](https://thitruongtaichinhtiente.vn/hoan-thien-3-du-an-luat-ve-dat-dai-nha-o-bat-dong-san-de-khoi-thong-nguon-luc-dap-ung-yeu-cau-tang-truong-2-con-so-85421.html), [TCKTTC](https://tapchikinhtetaichinh.vn/thuc-day-nha-o-xa-hoi-nha-o-cho-thue-trinh-quoc-hoi-thong-qua-luat-nha-o-luat-kinh-doanh-bat-dong-san-sua-doi-vao-thang-102026-159371.html) |
| NƠXH | 47.000/97.000 căn (48% KH) 9 tháng (họp 13/10, qua caller). Chỉ tiêu cả năm theo NQ 07/NQ-CP là 158.700 căn: **hai mẫu số khác nhau, chưa đối chiếu được** | [Mekong ASEAN](https://mekongasean.vn/bo-xay-dung-thuc-tien-do-hoan-thanh-158700-can-nha-o-xa-hoi-nam-2026-54653.html) |

---

## 5. Phân loại lại (prospective)

### Trục 1: STRUCTURAL hay CONFIDENCE/LIQUIDITY? → **STRUCTURAL_ACCUMULATION, GIỮ NGUYÊN**

Bằng chứng mới **củng cố** tính cấu trúc. Các chỉ số này đã xấu đi nhiều quý TRƯỚC mọi biến động giá:
1. **Tín dụng/GDP tiếp tục tăng.** Tín dụng +16,7% YoY, trong khi GDP danh nghĩa khoảng +13-14%
   (GDP thực khoảng 9% cộng giảm phát GDP khoảng 4-5%; suy luận, chưa có số GDP danh nghĩa). Như vậy tỷ
   lệ 145% cuối 2025 gần như chắc đã cao hơn. Năm thứ hai liên tiếp tín dụng vượt định hướng (TCTD kỳ
   vọng 16,4% so với 15%).
2. **Dấu hiệu quá nhiệt kiểu nhu cầu đầu tư.**
   - Tích luỹ tài sản +21,4%, nhập khẩu +36,7%, nhập siêu trong nước −34,3 tỷ USD.
   - Phần lớn nhập khẩu là điện tử phục vụ FDI xuất khẩu (khu vực FDI vẫn xuất siêu). Phần đó KHÔNG
     phải mất cân bằng nội địa.
   - Nhưng thâm hụt của khu vực trong nước nới rộng mạnh. Đây đúng là kênh "tín dụng → đầu tư/BĐS →
     nhập khẩu".
3. **Cơ quan quản lý xác nhận** lệch kỳ hạn và tồn kho tăng. Phản ứng là sửa luật và nới LDR. Đó là
   quản lý mất cân bằng nhiều năm, không phải dập một cú sốc.

Bằng chứng **chống** việc nâng lên "đã crystallize":
1. Lạm phát cơ bản 4,45% và đang giảm. CPI chung vượt trần là do giá dầu (chi phí đẩy, lệch trục).
   Chưa có lạm phát cầu kéo diện rộng kiểu 2007-08 hay 2011.
2. Tỷ trọng tín dụng BĐS không tăng thêm từ tháng 6. Tín dụng BĐS trong tháng 7-8 tăng chậm hơn tổng.
3. Vi phạm TPDN 12 tháng 0,24%. VND tăng giá YTD. Liên NH qua đêm thấp đầu tháng 10.

### Trục 2: có containable bằng một hành động? → **KHÔNG, GIỮ NGUYÊN**

- Phản ứng 13/10 mang tính hệ thống và đa ngành: luật, tín dụng chính sách, đầu mối dự án, rà tồn kho.
- Không có một tổ chức hay một sự kiện nào để "backstop".
- Thêm vào đó, hai lực bên ngoài VN không kiểm soát đang đi NGƯỢC chiều: dầu >100 USD và Fed có khả
  năng tăng tiếp. Chúng hạn chế dư địa nới giá tiền, và đó cũng là lý do điều hành dồn sang nới lượng.

### Thay đổi so với 08-26
- Giai đoạn: **sớm-giữa → GIỮA.** Lý do: bộ đệm ngoài mỏng đi (thặng dư → thâm hụt thương mại), nhà
  chức trách thừa nhận lệch kỳ hạn, tồn kho tăng và giá thứ cấp nhích xuống.
- Độ tin cậy: **vẫn AMBIGUOUS.** Không nâng lên "clean" vì các chỉ báo thị trường (liên NH, VND, vi
  phạm TPDN) chưa xác nhận stress, còn số chính thức thì là cận dưới hoặc xác nhận muộn.
- Bảo vệ số 1 so với Thái Lan 1997 trong thesis 08-26 là "CA thặng dư 28 tỷ USD (2024)". **Phải hạ
  cấp**: 9 tháng 2026 nhập siêu hàng hoá 19,4 tỷ. CA 9 tháng không có số. Kiều hối có thể bù một phần,
  lợi nhuận FDI chuyển về thì trừ đi (*suy luận*). Dự trữ ngoại hối không có số sau 18/6. Các bảo vệ còn
  giữ nguyên: tỷ giá thả nổi có quản lý, nợ nước ngoài ngắn hạn thấp, FDI sản xuất.

---

## 6. Kịch bản 6-12 tháng (tới khoảng 10/2027). XÁC SUẤT LÀ JUDGMENT

| # | Kịch bản | Mô tả quan sát được | P (judgment) |
|---|---|---|---|
| A | **Tích tụ tiếp, chững có quản lý** (cơ sở) | Tín dụng cả năm 2026 khoảng 16%, tỷ trọng BĐS dao động 24,5-26,5%. Giá thứ cấp −5-10%, giao dịch đi ngang đến giảm nhẹ. NPL công bố nhích lên 2,0-2,5%. Lãi huy động chính (effective) đi ngang ở khoảng 7,4-7,5%, có thể chạm
kill-switch A một lần mà không thành xu hướng. Chính sách tiếp tục nới lượng. Không có sự kiện hệ thống | **50-55%** |
| B | **Đóng băng thanh khoản BĐS cục bộ** | Giao dịch −30-50% YoY. Vài chủ đầu tư vừa gia hạn hoặc chậm trả (một phần trong 28K tỷ Q4 + 84K tỷ Q2/2027). NPL >2,5%, nhóm 2 tăng. CCTG Big-4 >8% hoặc liên NH 3M >7,5%. Riêng việc effective vượt 7,5%
(kill-switch A ARM) mới là bước đầu, chưa đủ để gọi là kịch bản B. NHNN hỗ trợ có mục tiêu. **Nguy hiểm nhất với hệ mình** (không có crash để gate giá bắt, return bị nén) | **20-25%** |
| C | **Stress hệ thống có tên** | Một ngân hàng vừa bị rút tiền, hoặc rollover TPDN thất bại diện rộng, hoặc VND −3%/tháng do cú sốc ngoài (dầu/Fed) cộng thâm hụt thương mại | **5-10%** |
| D | **Hạ cánh mềm sớm hơn kỳ vọng** | Luật sửa đổi thông qua và gỡ được nguồn cung pháp lý. Giá giảm nhẹ nhưng giao dịch HỒI. Tồn kho giảm. Tín dụng BĐS dịch sang người mua ở thật/NƠXH | **15-20%** |

**Đính chính 14/10 chiều: xác suất ở bảng trên KHÔNG đổi.** Lý do: dùng số chính 7,4% thay cho 6,4%
không thêm thông tin nào về hướng đi. Các mức 7,4-9,2% vốn đã nằm trong lập luận của bản sáng. Số liệu
liên NH và top-5 tư nhân mới bổ sung đều cho cùng một kết luận: đi ngang.

Kịch bản dài hạn của 08-26 (3-7 năm): **tôi dịch nhẹ xác suất sang phía xấu.**
- S1 (điều chỉnh có kiểm soát 15-20%): từ 45-55% xuống **40-50%**.
- S2 (điều chỉnh mạnh 30-40%): từ 25-35% lên **30-35%**.
- S3 (khủng hoảng hệ thống, sau hiệu chỉnh opacity): giữ **10-20%**.
- Lý do duy nhất của việc dịch: bộ đệm ngoài mỏng đi. Các chỉ báo lượng trong nước không xấu thêm
  đáng kể.

---

## 7. Tín hiệu sớm và lịch 3 tháng tới

| Ngày (ICT) | Sự kiện | Nhìn vào gì |
|---|---|---|
| **17/10** | Khai mạc kỳ họp thứ Hai QH khoá XVI | Lịch biểu quyết 3 luật Đất đai/Nhà ở/KDBĐS (kỳ này hay lùi); nội dung định giá đất, điều tiết địa tô; chỉ tiêu tăng trưởng và tín dụng 2027 |
| **19/10 (08:05)** | Cron tuần deposit/CCTG (`refresh_deposit_cctg_weekly.sh`) | Effective có vượt 7,5% không (kill-switch A); CCTG 12M Big-4 có đợt mới không |
| **khoảng 20/10 → 30/10, chậm nhất khoảng 14/11** | Mùa BCTC Q3 (hạn 30 ngày; công ty mẹ hợp nhất 45 ngày theo TT96/2020) | Ngân hàng: NPL, **nợ nhóm 2**, coverage, % dư nợ BĐS, LDR theo công thức cũ. Chủ đầu tư: tồn kho, người mua trả trước (hụt = tín hiệu cầu yếu), nợ vay ngắn hạn |
| **khoảng đầu tháng 11** (ngày chính xác chưa xác minh) | Cục Thống kê: CPI/KT-XH T10 | Lạm phát cơ bản có tiếp tục dưới 4,5% không; nhóm nhà ở-VLXD |
| **07/11 (03:00)** | Cron interim tháng 11 | Bảng 7 ngưỡng; điền các ô "không có số" (top-5 tư nhân, liên NH 3M, tiền gửi lớn) |
| Giữa mỗi tháng | Báo cáo VIS Rating TPDN | Chậm trả mới trong 40K tỷ BĐS dân cư đáo hạn Q4; tỷ lệ 12 tháng so với ngưỡng 2% |
| **26/11** | Review quý (thesis) | Refresh toàn bảng và `structural_break_watch.json` |
| **01/12** | TT 50/2026 hiệu lực (LDR 95%) | Ngân hàng nào dùng room LDR để đẩy tín dụng BĐS; điều khoản chuyển tiếp thật |
| **Tháng 11-12** | Room tín dụng cuối năm | Có văn bản cấp thêm room (thêm một lần nới) không; tín dụng YTD so với huy động YTD |
| **FOMC cuối 10 / giữa 12** (ngày chưa xác minh) | Fed | Tăng thêm thì áp lực USD/VND tăng và dư địa nới giá tiền giảm |
| **12/2026-01/2027** | Mùa thanh khoản cuối năm và trước Tết | Liên NH 1M/3M, CCTG đợt mới. Đây là lúc lệch kỳ hạn thường lộ ra |
| 22/03/2027 | FTSE đợt 2 (10%→30%) | Ngoài cửa sổ 3 tháng; ghi để nối tiếp |

**5 tín hiệu ưu tiên** (đều là dạng market-based hoặc khó làm đẹp):
1. **Nợ nhóm 2 + coverage trong BCTC Q3 ngân hàng.** Nhóm 2 tăng tiếp cùng coverage giảm tiếp là bước
   kế của cơ chế "tín dụng 2025 → NPL 2026".
2. **Chi phí vốn chuyển thành giá.** Ba bậc, từ gần đến xa:
   - Gần nhất: **kill-switch A**, tức effective (CCTG Big-4 12M) từ 7,6% trở lên, chỉ cách +0,2pp.
     Cron tuần thứ Hai sẽ báo.
   - Tiếp theo: CCTG Big-4 12M ≥7,7%, hoặc VPB/CCTG nhóm 2 ≥9,5%.
   - Xa nhất: liên NH 3M >7,5% bình quân tháng.
   Cả ba là dấu hiệu lệch kỳ hạn bắt đầu lộ ra qua giá.
3. **Giao dịch BĐS YoY** (BXD Q4, công bố khoảng 01/2027) và **người mua trả trước** của chủ đầu tư
   niêm yết. Hai số này bắt kịch bản B.
4. **Chậm trả mới trong khối TPDN BĐS dân cư Q4 (40K tỷ).** Tỷ lệ 12 tháng vượt 1% đã đáng chú ý dù
   chưa tới ngưỡng 2%.
5. **Thương mại và tỷ giá.** Nhập siêu quay lại sau T9, cộng tỷ giá trung tâm tăng >1%/tháng, cộng dữ
   liệu dự trữ ngoại hối mới (hoặc tiếp tục không công bố).

---

## 8. Hàm ý định hướng cho các nhóm ngành (KHÔNG phải khuyến nghị giao dịch)

Không đề xuất đổi V2.4/DT5G/margin. Playbook 08-26 vẫn đúng: không pre-emptive derisk; khủng hoảng BĐS
nội địa thuộc Loại-1/AMBIGUOUS, nên sleeve margin bị chặn hoặc giảm size đúng thiết kế.

- **Ngân hàng: phân hoá mạnh hơn, không đồng loạt.**
  - Nới LDR và loại trừ room đỡ tăng trưởng tín dụng ngắn hạn.
  - Ngược lại, chi phí vốn biên cao (CCTG 7,4-9,2%, trái phiếu cấp 2 biên +2,25pp) ép NIM, nhất là
    ngân hàng phụ thuộc CCTG hoặc tiền gửi lớn.
  - Prior từ audit 08-26 giữ nguyên: TCB-profile (tỷ trọng BĐS cao) và HDB (coverage khoảng 50%) dễ
    tổn thương nhất. ACB/VCB-profile phòng thủ hơn. MBB cần theo dõi vintage.
  - BCTC Q3 là điểm kiểm tra thật.
- **BĐS dân dụng: nhóm chịu tác động trực tiếp nhất.**
  - Tồn kho tăng, giá thứ cấp nhích xuống, người mua khó vay.
  - Chính sách (đầu mối dự án tồn đọng, sửa luật) gỡ phía CUNG pháp lý, không gỡ khả năng chi trả.
  - Phân hoá: chủ đầu tư có dự án đủ pháp lý và đòn bẩy thấp khác hẳn chủ đầu tư có đáo hạn TPDN Q4/2026
    đến Q2/2027.
  - Giữ quy tắc: chủ đầu tư BĐS KHÔNG vào danh sách crisis-buy.
- **BĐS KCN: tương đối tách khỏi chu kỳ dân dụng.**
  - XK khu vực FDI +29%, NK điện tử +72%, KCN được loại khỏi room BĐS.
  - Rủi ro chính của nhóm này nằm ở bên ngoài (thương mại toàn cầu), không ở trục BĐS dân dụng.
- **Xây dựng và vật liệu: hai nửa khác nhau.**
  - Hạ tầng và đầu tư công: CN-XD +12,5%, vốn đầu tư +15%, giá vật liệu bảo dưỡng nhà ở +13% (bình quân
    9 tháng). Nhu cầu từ nhánh này còn mạnh.
  - Nhánh gắn nhà ở dân dụng sẽ chịu trước nếu xảy ra kịch bản B.
  - Lưu ý danh sách BANNED đã có (NKG, HSG, ...): không bàn lại.
- **Chứng khoán nói chung: vĩ mô vừa nóng vừa có đặc điểm cuối chu kỳ.**
  - Mặt nóng: GDP 9,95%.
  - Mặt cuối chu kỳ: tín dụng 16,7% YoY, nhập siêu, dầu >100 USD, Fed có thể tăng.
  - Nguồn cung cổ phiếu mới rất lớn (huy động qua TTCK +85,6%, rủi ro pha loãng). Khối ngoại bán ròng
    lớn YTD. Dòng FTSE vào theo 4 đợt nên tác động dàn trải.
  - Tôi không dự báo lợi suất. Các tác động này tới giá đã được xử lý cơ học qua gate giá (DT5G/breadth).

---

## 9. Đã biết / Suy luận / Không biết

**ĐÃ BIẾT** (có nguồn, ngày):
- Tín dụng 30/9 +11,59% YTD, +16,69% YoY.
- Tín dụng BĐS 31/8 = 5,21 triệu tỷ = 25,39%, +9,49% YTD (qua caller, nhất quán nội tại).
- GDP Q3 +9,95%.
- CPI T9 5,08%, core 4,45%.
- Nhập siêu 9 tháng 19,42 tỷ USD.
- Huy động 28/9 +9,78%.
- **Lãi huy động chính (effective của team) 7,4% tại 12/10** = max(Big-4 12M 6,8%; CCTG Big-4 12M 7,4%).
  Thấp hơn kill-switch A 0,1pp.
- Proxy phụ: lãi huy động bình quân giao dịch mới của NHNN 6,38% (20/9), +1,15pp YTD.
- Big-4 12M online 6,8%, CCTG 7,4-7,5% (6M VCB 7,5%).
- Liên NH 09/10: ON 4,52 · 1M 5,15 · 3M 6,75 · 6M 8,16 (VBMA, ngoài dữ liệu team).
- TT 50/2026 nới LDR 95% (hiệu lực 01/12).
- VND +1,1% YTD.
- TPDN: 12 tháng 0,24%; đáo hạn Q4 khoảng 77K tỷ.
- VNINDEX 1.719 (13/10).

**SUY LUẬN** (ghi rõ):
- Tín dụng/GDP đã vượt 145%.
- CA 2026 yếu hơn hẳn 2024.
- Nới lượng thay cho nới giá vì lãi suất bị neo hành chính.
- "Tín dụng BĐS chậm lại" có thể một phần là do đổi cách tính.
- Tồn kho tự báo là cận dưới.

**KHÔNG BIẾT** (không suy hộ):
- NPL và nợ nhóm 2 Q3.
- Dự trữ ngoại hối sau 18/6.
- CA 9 tháng.
- Tỷ giá trung tâm tháng 10.
- Liên NH sau 09/10.
- Top-5 NH tư nhân: chỉ có một khảo sát ngày 10/10, và số của ACB lệch giữa hai nguồn.
- Tiền gửi lớn ≥10% trong tháng 10.
- Giao dịch BĐS YoY.
- Kết quả FOMC 9/2026.
- Ngày thông qua 3 luật.
- Giải ngân FDI và đầu tư công 9 tháng.
- Điều khoản chuyển tiếp thật của TT 50.
- Bài gốc phiên họp 13/10 (chưa tự đọc).

---

## 10. Việc cho orchestrator (Bobby KHÔNG tự làm, theo phạm vi caller giao)
1. Thêm dòng vào `kb/data_registry/market-state/vn_macro_regime_history.md` cho episode "VN RE
   structural accumulation". Nội dung: re-read 2026-10-14, giữ trục 1/trục 2, giai đoạn → GIỮA, vẫn
   AMBIGUOUS. Ghi lãi huy động chính = effective 7,4% (12/10), cách
   kill-switch A 0,1pp. KHÔNG ghi 6,4% làm số chính (đính chính 14/10 chiều).
2. Bus event `macro-strategist finding "vn-macro-update-20261014"`.
3. Thêm 1 dòng pointer vào thesis `vn-realestate-structural-risk-20260826.md`: (a) hạ cấp bảo vệ "CA
   thặng dư"; (b) TT 50/2026 là sự kiện nới lượng mới.

_(16:2x ICT 14/10/2026 · đính chính số lãi huy động chính 17:0x ICT 14/10/2026)_
