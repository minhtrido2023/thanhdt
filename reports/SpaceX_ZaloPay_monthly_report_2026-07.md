# BÁO CÁO THÁNG — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: THÁNG 07/2026 (01/07 – 31/07/2026)
### *Tháng đầu tiên vận hành thật — SpaceX go-live 01/07, ZaloPay go-live 06/07*

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ **01/07/2026** (có margin) · vốn ban đầu **1.000.000.000 VND**
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ **06/07/2026** (cash-only) · tiếp nhận danh mục có sẵn
**Chiến lược:** V2.4 — 2 book tín hiệu (BAL momentum + LAG hậu-công-bố-lợi-nhuận), parking custom30V khi thị trường NEUTRAL, rổ CAPIT khi có bán tháo kiệt quệ
**Ngày lập báo cáo:** 01/08/2026 · **Người lập:** Taylor (Quant)
**Đối tượng:** Báo cáo hiệu suất & vận hành tháng — chuẩn mực quản lý tài sản, có thể chia sẻ với nhà đầu tư

---

## MỤC LỤC
1. Tóm tắt điều hành · 2. Hiệu suất MTD/QTD/YTD vs chỉ số · 3. Phân rã nguồn lãi/lỗ (attribution) ·
4. Chỉ số rủi ro · 5. Phí & chi phí · 6. Nhật ký sự kiện tháng · 7. Danh mục cuối tháng ·
8. Công bố sự cố & khoảng trống số liệu · 9. Triển vọng & việc cần làm · 10. Phụ lục phương pháp

---

## 1. TÓM TẮT ĐIỀU HÀNH

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| Ngày bắt đầu quản lý | 01/07/2026 | 06/07/2026 |
| Cơ sở đầu kỳ | **1.000.000.000** (vốn góp) | **987.865.567** (NAV bàn giao, chốt 06/07) |
| NAV cuối tháng (31/07) | **938.435.711** | **888.828.498** |
| **Lãi/lỗ trong kỳ** | **−61.564.289** | **−99.037.069** |
| **Tỷ suất trong kỳ (MTD = QTD = từ khi bắt đầu)** | **−6,16%** | **−10,03%** |
| VN-Index cùng khung thời gian | −6,68% (30/06→31/07) | −5,84% (06/07→31/07) |
| **Chênh so với chỉ số** | **+0,52 điểm %** ✅ | **−4,19 điểm %** ❌ |
| — riêng DGC (ngoài phạm vi bot) | — | **−71.500.000 (−15,46%)** |
| — **phần bot quản lý (loại DGC)** | — | **−5,24%** → **+0,60 điểm %** ✅ |
| Biến động (năm hoá, 20–22 phiên) | 17,3% | 26,5% (ex-DGC: **19,5%**) |
| Sụt giảm tối đa trong tháng | −9,96% | −16,12% (ex-DGC: **−10,39%**) |
| Số lệnh khớp trong tháng | 57 | 33 |
| Giá trị giao dịch (mua + bán) | 2.056.440.400 | 912.562.217 |
| Tổng phí + thuế ước tính | ~2.302.281 (0,23% vốn) | ~1.124.689 (0,11% NAV) |
| Nợ margin cuối tháng | 6.212 (phí, không phải vay) | 7.196 (phí) |

### Kết luận điều hành

**Tháng 7 là một tháng thị trường giảm mạnh** — VN-Index mất **−6,68%**, từ 1.860,01 xuống 1.735,78,
với chuỗi 3 tuần giảm liên tiếp và một phiên sập **−3,58%** (22/07). Đây là bối cảnh khắc nghiệt cho
một danh mục vừa mới xây từ tiền mặt.

**SpaceX: −6,16%, tốt hơn chỉ số 0,52 điểm %, với biến động và mức sụt giảm đều thấp hơn chỉ số.**
Chiến lược làm đúng những gì được thiết kế: không đoán đáy, không bán tháo, giảm bớt mức rơi nhờ cấu
hình phòng thủ. **Nhưng cần nói thẳng: đây vẫn là tháng lỗ 61,6tr, và 22 phiên giao dịch là quá ngắn
để kết luận bất cứ điều gì về chất lượng chiến lược.**

**ZaloPay: −10,03%, kém chỉ số 4,19 điểm %** — nhưng con số này **không phản ánh chất lượng chiến
lược**, vì **72,2% mức lỗ đến từ một mã duy nhất mà hệ thống không được phép động vào**: DGC, vị thế
legacy 10.000cp, mất −15,46% (−71,5tr) sau khi lãnh đạo doanh nghiệp bị khởi tố và HOSE hạn chế giao
dịch. **Phần tài sản do hệ thống thực sự quản lý: −5,24%, tức tốt hơn chỉ số 0,60 điểm %, với biến
động 19,5% và sụt giảm tối đa −10,39% — đều thấp hơn chỉ số.** Hai tài khoản do đó cho kết quả **nhất
quán với nhau** một khi loại bỏ yếu tố ngoài tầm kiểm soát.

**Ba việc lớn đã diễn ra trong tháng:**
1. **Go-live và khắc phục sự cố mua trùng lệnh (02/07 → 09/07)** — sự cố đã công bố, đã xử lý dứt
   điểm, nợ margin phát sinh đã trả hết. Mục 6.1.
2. **Rổ CAPIT "bear-washout" kích hoạt 21/07** — giải ngân 432,0tr trên cả 2 tài khoản vào 5 mã phòng
   thủ, giữ khoá 60 phiên. Đây là thay đổi hồ sơ rủi ro lớn nhất tháng. Mục 6.3.
3. **Book LAG (đón sóng sau công bố lợi nhuận) kích hoạt lần đầu 27–28/07** — mùa BCTC Q2 đánh thức
   kênh tín hiệu vốn rỗng suốt tháng. Mục 6.4.

**Trạng thái thị trường DT5G = NEUTRAL (3/5) toàn bộ 22 phiên của tháng**, không đổi một lần nào,
không có cap phòng thủ vĩ mô nào kích hoạt.

---

## 2. HIỆU SUẤT MTD / QTD / YTD SO VỚI CHỈ SỐ

| | SpaceX | ZaloPay (tổng) | ZaloPay (ex-DGC) | VN-Index |
|---|---:|---:|---:|---:|
| **MTD (tháng 7)** | **−6,16%** | **−10,03%** | **−5,24%** | −6,68% |
| **QTD (Q3/2026, bắt đầu 01/07)** | −6,16% | −10,03% | −5,24% | −6,68% |
| **YTD 2026** | −6,16%* | −10,03%* | −5,24%* | (không so sánh được**) |

\* **MTD = QTD = YTD** vì cả hai tài khoản mới bắt đầu được quản lý trong tháng 7. **Đây KHÔNG phải
tỷ suất cả năm** — chỉ là 22 (SpaceX) và 20 (ZaloPay) phiên giao dịch. Không được ngoại suy ra tỷ
suất năm.
\*\* VN-Index YTD 2026 không đưa vào bảng vì khung thời gian khác nhau sẽ gây hiểu nhầm; so sánh chỉ
có ý nghĩa trên **đúng khung thời gian quản lý** (đã ghi rõ ở Mục 1).

**Diễn biến theo tuần** (để thấy hình dạng của tháng, không chỉ điểm đầu–cuối):

| Tuần | SpaceX | ZaloPay | ZaloPay ex-DGC | VN-Index |
|---|---:|---:|---:|---:|
| 01–03/07 (go-live) | −1,14%¹ | — | — | +0,11% |
| 06–10/07 | −1,71% | −0,96%² | −1,72% | −1,81% |
| 13–17/07 | −2,08% | −2,91% | −2,80% | −2,24% |
| **20–24/07** | **−4,25%** | **−10,53%** | **−4,09%** | **−5,67%** |
| 27–31/07 | **+3,01%** | **+4,59%** | **+3,42%** | **+2,95%** |
| **Cả tháng** | **−6,16%** | **−10,03%** | **−5,24%** | **−6,68%** |

¹ Tính từ vốn góp 1.000.000.000 đến NAV chốt 03/07 (988.629.520). Giai đoạn này bị ảnh hưởng bởi sự
cố mua trùng lệnh 02/07 (Mục 6.1). ² Từ NAV bàn giao 06/07.

**Nhận xét:** hình dạng của tháng là **"rơi ba tuần rồi bật lại một tuần"**. Cả 2 tài khoản đều **rơi
ít hơn chỉ số ở tuần xấu nhất** (20–24/07: SpaceX −4,25% vs chỉ số −5,67%; ZaloPay ex-DGC −4,09%) và
**bật nhiều hơn chỉ số ở tuần hồi** (27–31/07). Đây là mẫu hình mong muốn — nhưng với 5 tuần dữ liệu,
**không thể phân biệt được với may mắn**.

---

## 3. PHÂN RÃ NGUỒN LÃI/LỖ (ATTRIBUTION)

### 3.1 SpaceX — phân rã theo cấu phần kế toán

| Cấu phần | VND | Ghi chú |
|---|---:|---|
| Vốn góp ban đầu (01/07) | 1.000.000.000 | |
| **Lãi/lỗ chưa thực hiện trên danh mục cuối tháng** | **−62.610.443** | ✅ đã xác minh từng mã |
| Phần còn lại: lãi/lỗ **đã thực hiện** ròng + cổ tức − phí/thuế | **+1.046.154** | ⚠️ **chưa tách được** — xem dưới |
| **= NAV 31/07** | **938.435.711** | ✅ khớp từng đồng với sổ broker |

**⚠️ Nói rõ điều chưa làm được:** dòng **+1.046.154** là một **số dư gộp**, không phải một con số đã
được kiểm chứng riêng lẻ. Nó chứa ít nhất bốn thứ đan vào nhau: (a) lãi/lỗ đã thực hiện của **23 lệnh
bán ngày 06/07** và lệnh bán HPG 15/07; (b) **cổ tức tiền mặt** đã nhận và đang chờ về (9.775.000đ
tại 31/07); (c) phí giao dịch + thuế bán đã trừ; (d) chênh lệch quy ước giá vốn giữa hệ thống và
broker. **Không tách được chính xác nếu chưa có sao kê chính thức của DNSE** — đã đưa vào việc cần
làm (Mục 9), và **không thay bằng số ước lượng** trong báo cáo này.

### 3.2 SpaceX — phân rã lãi/lỗ chưa thực hiện theo nhóm ngành (đã xác minh 100%)

| Nhóm | Giá trị TT 31/07 | % NAV | Lãi/lỗ chưa TH | % tổng lỗ chưa TH |
|---|---:|---:|---:|---:|
| **Ngân hàng** (11 mã) | 534.870.000 | 57,0% | **−56.220.442** | **89,8%** |
| Chứng khoán (VIX, VND, SHS) | 17.120.000 | 1,8% | −3.900.000 | 6,2% |
| **Rổ CAPIT** (SIP, PVT, VNM, SAB, NCT) | 290.235.000 | 30,9% | −1.640.000 | 2,6% |
| Bất động sản (VHM) | 74.050.000 | 7,9% | −850.000 | 1,4% |
| TV1 (ngoài V2.4) | 7.840.000 | 0,8% | 0 | 0,0% |
| **Tổng** | **924.115.000** | **98,5%** | **−62.610.443** | 100% |

**Kết luận attribution rõ ràng: gần **90% khoản lỗ chưa thực hiện đến từ nhóm ngân hàng**, chiếm 57%
NAV.** Nguyên nhân: danh mục ngân hàng được xây trong 2 phiên đầu tháng (01–02/07) ở vùng giá cao
nhất của tháng, ngay trước nhịp giảm; nhóm ngân hàng cũng dẫn dắt đà giảm của thị trường trong tháng.

**Đóng góp tích cực rõ nhất là rổ CAPIT** — chiếm gần 31% NAV nhưng chỉ gánh 2,6% mức lỗ, nhờ mua vào
ở vùng giá thấp cuối tháng và thuộc nhóm ngành phòng thủ.

### 3.3 SpaceX — 5 vị thế tốt nhất & 5 tệ nhất (lãi/lỗ chưa thực hiện, 31/07)

| Tốt nhất | VND | % | | Tệ nhất | VND | % |
|---|---:|---:|---|---|---:|---:|
| PVT | **+4.200.000** | +7,0% | | TCB | **−9.900.000** | −14,6% |
| VNM | +2.070.000 | +3,9% | | BID | −9.483.478 | −11,6% |
| SIP | +1.770.000 | +2,2% | | CTG | −8.456.607 | −10,7% |
| TV1 | 0 | 0,0% | | MBB | −8.040.000 | −13,0% |
| VHM | −850.000 | −1,1% | | VPB | −7.162.857 | −11,2% |

**Cả 3 vị thế lãi đều thuộc rổ CAPIT. Cả 5 vị thế lỗ nặng nhất đều là ngân hàng.**

### 3.4 ZaloPay — phân rã theo nguồn (đây là phần quan trọng nhất của báo cáo này)

| Cấu phần | 06/07 | 31/07 | Thay đổi | % |
|---|---:|---:|---:|---:|
| **DGC** — 10.000cp, legacy, **ngoài phạm vi bot** | 462.500.000 | 391.000.000 | **−71.500.000** | **−15,46%** |
| **Phần bot quản lý** (13 mã + tiền) | 525.365.567 | 497.828.498 | **−27.537.069** | **−5,24%** |
| **Tổng NAV** | 987.865.567 | 888.828.498 | −99.037.069 | −10,03% |

**DGC chiếm 72,2% toàn bộ mức lỗ của tài khoản**, dù chỉ chiếm 46,8% NAV đầu kỳ.

**Vì sao DGC nằm ngoài phạm vi bot:** HOSE hạn chế giao dịch mã này sau khi lãnh đạo doanh nghiệp bị
khởi tố (17/03/2026); ước tính gỡ hạn chế khoảng 11–12/2026. Vị thế được giữ theo luận điểm riêng của
nhà đầu tư và đã được **khai báo chính thức trong cấu hình** (`excluded_tickers`) — bot **không thể**
đặt lệnh với mã này ngay cả khi kế hoạch có sai sót. Mọi phép định cỡ vị thế của chiến lược tính trên
`active_nav` (NAV trừ DGC), không tính trên NAV tổng.

**Diễn biến DGC trong tháng:** 46.250 (06/07) → 44.800 (17/07, giảm đều) → **36.850 (24/07, sập
−17,75% chỉ trong một tuần)** → 39.100 (31/07, hồi 6,1%). Cú sập tập trung ở phiên 23/07 và đã được
bộ phận giám sát rủi ro (Spyros) thẩm định ngay trong ngày với kết luận **KHÔNG dừng giao dịch, GIỮ
vị thế**.

### 3.5 ZaloPay — lãi/lỗ chưa thực hiện phần bot mua (đã xác minh)

Giá vốn thật 454.848.300 → thị giá 31/07 440.958.100 = **−13.890.200 (−3,05%)**.
Vị thế lãi tốt nhất: **CSV +7,3%** · PVT +6,1% · VNM +3,8% · SIP +2,0%.
Vị thế lỗ nặng nhất: NCT −11,7% · TCB −8,4% · SAB −8,2% · MBB −8,5%.

**Lãi/lỗ đã thực hiện trong tháng — chương trình giảm tập trung VPB:** bán tổng **4.000cp** (5 lệnh,
15/07 → 27/07) với giá vốn broker 27.886,67, hiện thực hoá lỗ **≈ −11,1tr gồm thuế/phí**. Đây là
**khoản lỗ có chủ đích**: VPB legacy từng chiếm **38,8% active NAV**, vượt xa trần chính sách 10%/mã.
Cuối tháng vị thế về **9,0% active NAV** — chương trình hoàn tất. Ngoài ra tháng 7 còn có các lệnh bán
danh mục cũ (MSH, TLG, TCM, VHC, VIB) trong 5 ngày chuyển tiếp 07–13/07; **lãi/lỗ đã thực hiện của các
mã này không tính được** vì không có giá vốn đã xác minh (vị thế có trước khi bot quản lý) — Mục 8.3.

---

## 4. CHỈ SỐ RỦI RO

| Chỉ số | SpaceX | ZaloPay (tổng) | ZaloPay (ex-DGC) | VN-Index |
|---|---:|---:|---:|---:|
| Số phiên có dữ liệu | 22 | 20 | 20 | 23 |
| Biến động ngày | 1,093% | 1,678% | **1,234%** | 1,345% |
| **Biến động năm hoá** | **17,3%** | 26,5% | **19,5%** | **21,3%** |
| **Sụt giảm tối đa (MaxDD)** | **−9,96%** | −16,12% | **−10,39%** | **−10,64%** |
| Ngày chạm đáy | 27/07 | 27/07 | 27/07 | 22/07 |
| Tỷ trọng cổ phiếu cuối tháng | 98,5% | 98,6% | — | — |

**Đọc bảng này cho đúng:**
- **SpaceX có biến động thấp hơn chỉ số (17,3% vs 21,3%) và sụt giảm nhẹ hơn (−9,96% vs −10,64%)**,
  đồng thời tỷ suất tốt hơn. Trên mọi trục đo, danh mục đều nhỉnh hơn chỉ số trong tháng đầu.
- **ZaloPay phần bot quản lý cũng vậy** (19,5% vs 21,3%; −10,39% vs −10,64%). Con số 26,5% / −16,12%
  của NAV tổng **là do DGC**, không phải do chiến lược.
- **KHÔNG báo cáo Sharpe/Sortino/Calmar trong kỳ này.** Với 20–22 phiên, các tỷ số này không có ý
  nghĩa thống kê và sẽ gây hiểu nhầm nghiêm trọng nếu công bố. Sẽ bắt đầu báo cáo khi có tối thiểu
  ~6 tháng dữ liệu NAV ngày.
- **Cảnh báo về rủi ro phía trước, không phải rủi ro đã qua:** tỷ trọng cổ phiếu cuối tháng
  **98,5%/98,6%**, tiền mặt gần cạn (SpaceX 14,3tr trong đó 9,8tr là cổ tức chờ về; ZaloPay 12,2tr).
  Các chỉ số rủi ro đo được ở trên hình thành khi danh mục còn giữ **30–32% tiền mặt**; **tháng 8 sẽ
  KHÔNG có lớp đệm đó**. Nếu thị trường giảm tiếp, mức sụt giảm nhiều khả năng **lớn hơn** những gì
  bảng này thể hiện.

---

## 5. PHÍ & CHI PHÍ

| Khoản mục | SpaceX | ZaloPay |
|---|---:|---:|
| Giá trị mua trong tháng | 1.296.489.400 | 472.295.317 |
| Giá trị bán trong tháng | 759.951.000 | 440.266.900 |
| **Tổng giá trị giao dịch** | **2.056.440.400** | **912.562.217** |
| Vòng quay danh mục (giao dịch / NAV bình quân) | **~206%** | **~97%** |
| Phí giao dịch ước tính (0,075%/lượt) | 1.542.330 | 684.422 |
| Thuế bán ước tính (0,1% giá trị bán) | 759.951 | 440.267 |
| **Tổng phí + thuế** | **~2.302.281** | **~1.124.689** |
| **% trên vốn/NAV đầu kỳ** | **0,23%** | **0,11%** |
| Lãi vay margin ước tính (12,5%/năm) | **~0,70–0,83tr** ⚠️ | 0 (cash-only) |
| Lãi/phí đã ghi nhận chính thức trên API | 6.720 | 7.619 |
| Phí quản lý / phí hiệu suất | **0** | **0** |

**Ba điều cần nói rõ về chi phí:**

1. **Vòng quay 206% của SpaceX là bất thường và mang tính một lần.** Nó gồm: xây danh mục từ tiền mặt
   (492,6tr ngày 01/07 + 457,8tr ngày 02/07), **tái cấu trúc khắc phục sự cố mua trùng lệnh** (bán
   ~711tr ngày 06/07), và giải ngân CAPIT (255tr ngày 21/07). **Không nên coi đây là tỷ lệ vận hành
   thường xuyên** — vòng quay ở trạng thái ổn định dự kiến thấp hơn nhiều, vì rổ CAPIT khoá 60 phiên
   và parking custom30V tái cân bằng theo quý.

2. **Lãi vay margin ~0,70–0,83tr là ƯỚC TÍNH, chưa xác minh** (khoảng giá trị tuỳ cách đếm số ngày
   tính lãi — không chốt một con số vì chưa có sao kê). Dư nợ 409,86tr tồn tại từ 02/07 đến 09/07
   (phát sinh từ sự cố mua trùng lệnh, đã trả hết đúng chu kỳ T+2). Lãi suất 12,5%/năm là **số nhà đầu
   tư cung cấp, chưa đối chiếu hợp đồng DNSE**; số đã ghi nhận chính thức trên API mới chỉ 6.720đ, cho
   thấy lãi được post theo chu kỳ chứ không hằng ngày. **Cần đối soát sao kê chính thức** (Mục 9).

3. **Toàn bộ số phí/thuế trên là ước tính từ biểu phí, chưa đối soát sao kê.** Mức phí 0,075%/lượt đã
   được xác nhận với biểu phí tài khoản; thuế bán 0,1% theo quy định. Khi có sao kê DNSE, các con số
   này sẽ được thay bằng số thật và chênh lệch (nếu có) sẽ được công bố.

---

## 6. NHẬT KÝ SỰ KIỆN THÁNG

### 6.1 Go-live SpaceX & sự cố mua trùng lệnh (01–09/07) — ĐÃ XỬ LÝ DỨT ĐIỂM
Ngày 01/07 hệ thống xây danh mục đợt 1 (492,6tr, 12/23 lệnh khớp). Ngày 02/07 **sự cố kỹ thuật khiến
phần lệnh chưa khớp bị đặt lại trùng**, đẩy giá trị cổ phiếu lên **1.398.485.000 (141% NAV)** và tạo
**nợ vay margin thật 409.863.737đ**. Sự cố đã được công bố đầy đủ trong báo cáo tuần 03/07 (kèm đính
chính một khẳng định sai trước đó rằng "dư nợ vay = 0"). Khắc phục: **23 lệnh bán ~711tr ngày 06/07**
theo kế hoạch đã duyệt, đưa danh mục về đúng mục tiêu V2.4; **nợ margin trả hết ngày 09/07** đúng chu
kỳ T+2. Chi phí thật của sự cố: phí/thuế của vòng bán bổ sung (~1,24tr) + ~0,70–0,83tr lãi vay ước tính. **Không có
lệnh bán ép giá, không có gọi ký quỹ bổ sung.**

### 6.2 Tiếp nhận ZaloPay & chuyển tiếp danh mục (06–13/07)
Tài khoản được bàn giao với danh mục có sẵn (DGC, VPB, VIB, VHC, TCM, TLG, MSH...). Kế hoạch chuyển
tiếp **5 ngày** (07/07 → 13/07) bán dần danh mục cũ và xây danh mục V2.4, hoàn tất đúng hạn. **DGC
được loại khỏi phạm vi bot** ngay từ đầu (Mục 3.4).

### 6.3 Rổ CAPIT "bear-washout" kích hoạt (21/07) — thay đổi hồ sơ rủi ro lớn nhất tháng
Sau phiên 20/07 (VN-Index −2,46%), điều kiện **bán tháo kiệt quệ** hình thành theo thước đo độ rộng
thị trường. Ngày 21/07 hệ thống mua **rổ 5 mã phòng thủ** trên cả 2 tài khoản: **VNM, SAB, NCT, PVT,
SIP** — tổng **432,0tr** (SpaceX 255,2tr + ZaloPay 176,8tr), bổ sung thêm 36,7tr ngày 24 và 27/07.
Nguồn vốn: **rút toàn bộ tiền gửi "Trứng vàng" off-book** (449,6tr) về tài khoản chứng khoán.

**Rổ CAPIT giữ khoá 60 phiên (tới ~giữa 10/2026), được miễn trừ cắt lỗ và miễn trừ trần vị thế theo
thiết kế.** Hệ quả: tỷ trọng cổ phiếu tăng từ ~68%/82% lên **98,5%/98,6%**.

**Bằng chứng sớm về tác dụng:** phiên sập 22/07, VN-Index **−3,58%** nhưng SpaceX chỉ **−1,67%**
(hơn 1,91 điểm % trong một phiên). Cuối tháng rổ CAPIT chỉ gánh 2,6% khoản lỗ chưa thực hiện dù chiếm
31% NAV. **Một tháng chưa đủ để kết luận** — cần theo dõi hết chu kỳ khoá 60 phiên.

### 6.4 Book LAG kích hoạt lần đầu trên tiền thật (27–28/07)
Mùa báo cáo tài chính Q2/2026 đánh thức kênh tín hiệu **hậu-công-bố-lợi-nhuận** (PEAD) vốn rỗng suốt
tháng. Hai vị thế đầu tiên, đều trên ZaloPay: **VPB 700cp** (lợi nhuận ròng +72% so với cùng kỳ, công
bố 20/07) và **CSV 1.000cp** (khớp 19.750 trong khi giá đóng cửa phiên đó 20.750 — thấp hơn 4,8%; đến
31/07 lãi **+7,3%**). Đây là **lần đầu kênh này chạy trên tiền thật** — chất lượng tín hiệu cần theo
dõi 4–6 tuần tới trước khi kết luận.

### 6.5 Chương trình mua TV1 (PECC1) — ngoài chiến lược V2.4, nhà đầu tư duyệt riêng
SpaceX gom **400cp TV1 @19.600 (7,84tr = 0,84% NAV)** trong các phiên 24–29/07, theo luận điểm "mua
khi thị trường sợ hãi có tính toán", với **ràng buộc cứng không mua trên 20.000**. Ngày 24 và 27/07
giá không về vùng đặt → lệnh không khớp, **hệ thống không đuổi giá**. Quy mô rất nhỏ, mang tính thăm dò.

### 6.6 Đóng hẳn tiền gửi "Trứng vàng" (21–23/07)
Toàn bộ 449,6tr đã rút về tài khoản chứng khoán và giải ngân. Theo chỉ đạo của nhà đầu tư, **khoản này
đóng hẳn, không mở lại** — trường `offbook_assets` về 0 vĩnh viễn ở cả 2 tài khoản. **Không phải nạp
thêm hay rút vốn**, chỉ chuyển hình thái tài sản; NAV không bị ảnh hưởng.

---

## 7. DANH MỤC CUỐI THÁNG (31/07/2026)

### 7.1 SpaceX — 21 mã, 924.115.000đ (98,5% NAV)

| Nhóm | Mã | Giá trị TT (VND) | % NAV |
|---|---|---:|---:|
| **Ngân hàng** (57,0%) | VCB 77,1tr · BID 72,2tr · CTG 70,8tr · TCB 57,9tr · VPB 57,0tr · MBB 54,0tr · LPB 46,6tr · HDB 37,8tr · ACB 32,9tr · SHB 17,3tr · TPB 11,3tr | 534.870.000 | 57,0% |
| **CAPIT** (30,9%) | SIP 81,8tr · PVT 64,1tr · VNM 54,8tr · SAB 47,9tr · NCT 41,7tr | 290.235.000 | 30,9% |
| Bất động sản | VHM | 74.050.000 | 7,9% |
| Chứng khoán | VIX 9,1tr · VND 5,0tr · SHS 3,0tr | 17.120.000 | 1,8% |
| Ngoài V2.4 | TV1 | 7.840.000 | 0,8% |
| Tiền mặt (gồm 9,8tr cổ tức chờ về) | | 14.326.923 | 1,5% |
| Phí phải trả | | −6.212 | — |
| **NAV** | | **938.435.711** | **100%** |

**Vị thế lớn nhất: SIP 8,7% NAV** — toàn bộ 21 mã đều **dưới trần tập trung 10%/mã**, tuân thủ đầy đủ
chính sách rủi ro.

### 7.2 ZaloPay — 16 mã, 876.598.100đ (98,6% NAV)

| Nhóm | Mã | Giá trị TT (VND) | % NAV | % active NAV |
|---|---|---:|---:|---:|
| **Excluded** | **DGC** (10.000cp) | 391.000.000 | **44,0%** | — |
| Ngân hàng | VCB 47,4tr · VPB 44,6tr · BID 34,2tr · CTG 32,3tr · TCB 27,7tr · MBB 24,8tr · LPB 18,2tr · HDB 16,6tr | 245.931.600 | 27,7% | 49,4% |
| **CAPIT** | PVT 37,9tr · VNM 36,6tr · SIP 36,0tr · SAB 32,4tr · NCT 31,1tr | 174.036.500 | 19,6% | 34,9% |
| Bất động sản | VHM | 44.430.000 | 5,0% | 8,9% |
| **LAG** (mới) | CSV | 21.200.000 | 2,4% | 4,3% |
| Tiền mặt | | 12.237.594 | 1,4% | |
| Phí phải trả | | −7.196 | — | |
| **NAV** | | **888.828.498** | **100%** | Active NAV: **497.828.498** |

**Tất cả vị thế bot đều dưới trần 10% active NAV** (lớn nhất VCB 9,5%). VPB 9,0% — chương trình giảm
tập trung đã hoàn tất (đỉnh 38,8%).

### 7.3 Ghi chú về rủi ro tập trung (cùng chính sách cho cả 2 tài khoản)

**Chính sách quỹ KHÔNG đặt trần theo ngành**, vì chất lượng doanh nghiệp niêm yết Việt Nam vốn tập
trung theo ngành. Kiểm soát rủi ro được thực hiện qua **trần 10%/mã** và **trạng thái thị trường
DT5G**. Tuy vậy, đây là **nguồn rủi ro tập trung thật cần theo dõi**: 11 mã ngân hàng của SpaceX
(57% NAV) cùng chịu chung một yếu tố rủi ro ngành — và trong tháng 7, chính yếu tố đó gây gần 90%
khoản lỗ chưa thực hiện. Rổ CAPIT đã **pha loãng** phần cổ phiếu (tỷ trọng ngân hàng trong danh mục
cổ phiếu giảm từ 86,3% xuống 60,3%) nhưng **không làm giảm tổng rủi ro thị trường**.

---

## 8. CÔNG BỐ SỰ CỐ & KHOẢNG TRỐNG SỐ LIỆU

Nguyên tắc: công bố mọi sự cố ảnh hưởng đến NAV/giao dịch/số liệu, kể cả khi đã tự khắc phục.
**Không có sự cố nào trong tháng 7 gây thiệt hại tiền thật ngoài sự cố 02/07 đã công bố** (Mục 6.1).

### 8.1 Sự cố đã đóng trong tháng (chi tiết ở báo cáo tuần tương ứng)
| Ngày | Sự cố | Trạng thái |
|---|---|---|
| 02/07 | Mua trùng lệnh → 141% NAV cổ phiếu + nợ margin 409,86tr | ✅ Đã khắc phục 06–09/07 |
| 03/07 | Báo cáo trước khẳng định sai "nợ margin = 0" | ✅ Đã đính chính công khai |
| 06/07 | Bot chưa hiểu quy tắc T+2 của DNSE (lệnh bị từ chối ~2.000 lần) | ✅ Đã sửa, không thiệt hại |
| 06/07 | NAV SpaceX nhiễm số dư ZaloPay (log broker dùng chung) | ✅ Đã sửa (lọc theo tài khoản) |
| 03/07 | Báo cáo dùng giá vốn **ước tính** thay vì giá vốn thật | ✅ Đã lập pipeline xác minh bắt buộc |
| 09/07 | Kế hoạch định giá 2/4 lệnh theo dữ liệu qua đêm (lệch +5,7%) | ✅ Đã ra quy tắc cứng: số liệu cùng ngày phải lấy từ API broker |
| 13–17/07 | Công cụ đối soát không lọc theo tài khoản | ✅ Đã vá, kỳ này chạy đúng |

### 8.2 🔴 Sự cố số liệu MỚI phát hiện khi lập báo cáo này — NAV ZaloPay 27/07 sai 32,0tr
Ngày 27/07, API số dư của DNSE trả về **toàn bộ bằng 0** ở hai lần đọc buổi tối, và tác vụ chụp NAV
**chấp nhận số 0 đó** làm tiền mặt → ghi NAV = 804.077.200 thay vì **836.088.620** (sai −32.011.420,
−3,83%).

**Bằng chứng:** cùng ngày, hai lần đọc buổi sáng trả về 27.380.812 bình thường; sáng 28/07 đọc lại là
32.011.420; kiểm tra ngược 32.011.420 − (mua CSV 19,75tr + phí) = 12.237.435 **đúng bằng** số dư cuối
phiên 28/07 đã ghi nhận → chuỗi tiền mặt khớp liền mạch.

**Ảnh hưởng:** không chạm tiền thật, không ảnh hưởng lệnh nào; nhưng tạo cặp biến động giả −5,39% /
+5,13%, **thổi phồng biến động năm hoá từ 26,5% lên 37,7% và sụt giảm tối đa từ −16,12% lên −19,33%**.
**Mọi con số trong báo cáo tháng này đã dùng bản đã sửa.** Đã rà toàn bộ chuỗi NAV tháng 7 của **cả 2
tài khoản**: chỉ có **1 trường hợp duy nhất** này.

### 8.3 Khoảng trống số liệu còn tồn tại (KHÔNG che giấu, không ước lượng thay thế)

| # | Khoảng trống | Ảnh hưởng | Người phụ trách | Hạn |
|---|---|---|---|---|
| 1 | **Chuỗi NAV SpaceX thiếu 2 dòng (21/07, 22/07)** — đã tái dựng đúng phương pháp từ dữ liệu gốc (927.267.983 / 911.773.252) nhưng file chính thức vẫn khuyết | Không ảnh hưởng NAV cuối tháng; ảnh hưởng chuỗi ngày | Winston | 08/08/2026 |
| 2 | **NAV ZaloPay 27/07 sai** (Mục 8.2) — cần sửa file + thêm chốt chặn từ chối bản ghi số dư rỗng | Đã điều chỉnh trong báo cáo; file gốc chưa sửa | Winston | 08/08/2026 |
| 3 | **Không tách được lãi/lỗ đã thực hiện, cổ tức và phí** của SpaceX (dòng +1.046.154, Mục 3.1) | Không ảnh hưởng NAV; ảnh hưởng độ chi tiết attribution | Taylor | báo cáo tháng 8 |
| 4 | **Không tính được lãi/lỗ vị thế legacy ZaloPay** (DGC, VPB cũ, và các mã đã bán trong chuyển tiếp) — không có giá vốn đã xác minh | Không thể so sánh **tỷ suất sinh lời** ZaloPay với SpaceX trên cơ sở như nhau | Winston / Taylor | chưa chốt |
| 5 | **Đẳng thức đối soát hai chiều của ZaloPay chưa lập được** — công cụ ra +532,6tr và kết luận "lệch vượt ngưỡng"; con số này **vô nghĩa và không được dùng** vì vế phải chỉ tính 14 mã có lịch sử khớp nội bộ, bỏ qua DGC (391,0tr) và VPB legacy (44,6tr) | Vế phải thật vẫn xác minh đầy đủ, khớp từng đồng | Winston / Taylor | chưa chốt |
| 6 | **Phí/thuế/lãi margin chưa đối soát sao kê chính thức DNSE** — tất cả là ước tính từ biểu phí | Sai số ước tính chưa đo được | Taylor | báo cáo tháng 8 |
| 7 | **Đẳng thức SpaceX còn dư −1.792.918 (−0,19% NAV)** — ✅ đạt ngưỡng dung sai nhưng chưa khép kín tuyệt đối | Không ảnh hưởng NAV (đã đối chiếu độc lập khớp từng đồng) | Taylor | báo cáo tháng 8 |
| 8 | **Báo cáo tuần 20–24/07 và 27–31/07 nộp chậm** — cảnh báo có chạy nhưng bị chôn trong log vận hành 4 lần/ngày, không ai xử lý | Không ảnh hưởng số liệu | Mike | 08/08/2026 |

**Điều KHÔNG có khoảng trống:** NAV cuối tháng của **cả 2 tài khoản đã được xác minh bằng hai nguồn
độc lập và khớp TỪNG ĐỒNG** — (i) chuỗi NAV do hệ thống ghi hằng ngày, và (ii) phép tính lại độc lập
từ sổ vị thế broker × giá đóng cửa 31/07 từ cơ sở dữ liệu thị trường. Giá vốn của **toàn bộ 21 mã
SpaceX và 14 mã bot của ZaloPay** đã cross-check giữa log gốc API broker và journal khớp lệnh nội bộ:
**Verified = True, 0 lệch khối lượng**.

---

## 9. TRIỂN VỌNG & VIỆC CẦN LÀM

### 9.1 Bối cảnh vĩ mô & trạng thái hệ thống bước sang tháng 8

- **DT5G = NEUTRAL (3/5)**, không đổi suốt tháng 7. Không có cap phòng thủ vĩ mô nào kích hoạt: lãi
  suất điều hành SBV ổn định, VIX/SPX chưa tới ngưỡng hoảng loạn, độ rộng thị trường chưa thủng ngưỡng
  chặn. **Hệ thống sẽ chỉ chuyển trạng thái khi giá xác nhận** — chậm có chủ đích, không đoán đáy/đỉnh.
- **VN-Index đóng tháng ở 1.735,78**, thấp hơn 7,0% so với đỉnh tháng (1.867,21 ngày 01/07) nhưng đã
  hồi 4,0% từ đáy 1.668,53 (22/07).
- **Mùa báo cáo tài chính Q2/2026 đang cao điểm** — kênh tín hiệu LAG vừa hoạt động trở lại và có thể
  phát thêm tín hiệu trong tháng 8.

### 9.2 ⚠️ Vấn đề cần nhà đầu tư quyết định: tiền mặt đã cạn

Cả 2 tài khoản chỉ còn **~1,4–1,5% NAV tiền mặt**, trong đó phần lớn của SpaceX là **cổ tức chưa về
tài khoản**. Hệ quả cụ thể, đã xảy ra thật: lệnh bổ sung CAPIT cho SIP ngày 27/07 **thiếu 33,2tr và
phải hoãn**.

**Nếu hệ thống phát tín hiệu LAG mới trong tháng 8, gần như chắc chắn không thực hiện được.** Ba lựa
chọn, đây là **quyết định của nhà đầu tư**, hệ thống không tự xử lý:
1. **Nạp thêm vốn** để hệ thống bắt được tín hiệu mùa BCTC;
2. **Chấp nhận bỏ lỡ** tín hiệu mới cho tới khi rổ CAPIT mở khoá (~giữa 10/2026);
3. **Cho phép bán bớt một phần danh mục parking** để lấy tiền — *lưu ý: điều này đi ngược thiết kế
   hiện tại và cần thay đổi quy tắc chính thức, không phải quyết định trong phiên.*

### 9.3 Rủi ro chính bước sang tháng 8

| Rủi ro | Mức độ | Ghi chú |
|---|---|---|
| **Tỷ trọng cổ phiếu 98,5%/98,6%, không còn lớp đệm tiền mặt** | **Cao** | Danh mục sẽ chịu gần trọn biến động thị trường theo cả hai chiều |
| **DGC 44,0% NAV ZaloPay, ngoài tầm can thiệp** | **Cao** | Chờ HOSE gỡ hạn chế ~11–12/2026 |
| **Rổ CAPIT khoá 60 phiên, miễn trừ cắt lỗ** | Trung bình | 290,2tr SpaceX / 174,0tr ZaloPay tới ~15/10/2026 |
| **Tập trung ngành ngân hàng 57% NAV SpaceX** | Trung bình | Đã gây ~90% lỗ chưa thực hiện tháng 7 |
| **Book LAG lần đầu chạy tiền thật** | Trung bình | Cần 4–6 tuần theo dõi chất lượng tín hiệu |
| Track record 22 phiên | — | Chưa đủ để đánh giá chiến lược bằng bất kỳ thước đo nào |

### 9.4 Việc cần làm — có người phụ trách và hạn nghiệm thu

| # | Việc | Người phụ trách | Hạn nghiệm thu |
|---|---|---|---|
| 1 | Sửa NAV ZaloPay 27/07 + thêm chốt chặn từ chối bản ghi số dư rỗng trong `daily_nav_snapshot.py` | **Winston** | **08/08/2026** |
| 2 | Bổ sung 2 dòng NAV SpaceX 21–22/07 + kiểm tra "đủ dòng NAV cho MỌI tài khoản" mỗi ngày | **Winston** | **08/08/2026** |
| 3 | Tách cảnh báo "báo cáo quá hạn" khỏi log vận hành, gửi đích danh có người nhận | **Mike** | **08/08/2026** |
| 4 | Lấy sao kê chính thức DNSE tháng 7 → đối soát phí/thuế/lãi margin thật vs ước tính | **Taylor** | **báo cáo tháng 8** |
| 5 | Tách được lãi/lỗ đã thực hiện + cổ tức + phí của SpaceX (dòng gộp +1.046.154) | **Taylor** | **báo cáo tháng 8** |
| 6 | Xây khả năng hạch toán giá vốn vị thế legacy (điều kiện để so sánh tỷ suất 2 tài khoản) | **Winston / Taylor** | chưa chốt |
| 7 | Trình nhà đầu tư quyết định về tiền mặt (Mục 9.2) | **DollarBill / Mike** | **trong tuần 04–08/08** |
| 8 | Theo dõi chất lượng tín hiệu LAG (VPB, CSV) — mùa BCTC Q2 | **Taylor** | báo cáo tháng 8 |
| 9 | Giữ rổ CAPIT đủ 60 phiên — không cắt lỗ, không bán sớm | Hệ thống (tự động) | ~15/10/2026 |

---

## 10. PHỤ LỤC — PHƯƠNG PHÁP & LƯU Ý

### 10.1 Pipeline xác minh số liệu (bắt buộc, không có ngoại lệ)
1. **`verify_account_snapshot.py`** (chạy với `--account-no` tường minh cho **từng** tài khoản) — giá
   vốn/khối lượng thật từ log gốc API broker (`averagePrice`/`fillQuantity` do DNSE trả về),
   cross-check độc lập với journal khớp lệnh nội bộ. Kết quả tháng này: **SpaceX Verified = True**
   (21 mã), **ZaloPay Verified = True** (14 mã bot), **0 lệch khối lượng** ở cả hai.
2. **`daily_nav_snapshot.py`** → `nav_history_{account}.csv` — chuỗi NAV ngày từ số dư/vị thế API thật.
   **1 dòng sai đã phát hiện & điều chỉnh** (ZaloPay 27/07), **2 dòng thiếu đã tái dựng** (SpaceX
   21–22/07) — Mục 8.
3. **`reconcile_equity.py`** — đẳng thức hai chiều: SpaceX ✅ đạt ngưỡng (−0,19% NAV); ZaloPay chưa lập
   được, output của công cụ **bị loại bỏ có chủ đích** (Mục 8.3 #5).
4. **Đối chiếu độc lập bổ sung:** giá trị cổ phiếu 31/07 tính lại từ sổ vị thế broker × giá đóng cửa
   BigQuery khớp **từng đồng** với chuỗi NAV ở **cả 2** tài khoản (SpaceX 924.115.000; ZaloPay
   876.598.100).

### 10.2 Ba cạm bẫy số liệu đã gặp trong tháng — ghi lại để ai kiểm tra lại không nhầm
1. **Journal khớp lệnh ghi khối lượng LUỸ KẾ theo lệnh con** — cộng dồn thẳng các dòng FILL sẽ ra số
   **lớn hơn thực tế**. Số trong báo cáo lấy từ **báo cáo thực thi từng phiên + sổ vị thế broker**
   (hai nguồn đã đối chiếu khớp nhau).
2. **Giá lịch sử bị hồi tố điều chỉnh cổ tức** — NCT và SAB giao dịch không hưởng cổ tức từ 27/07
   (8.000đ và 2.990đ/cp). Nếu tính lại NAV ngày 24/07 bằng giá đã điều chỉnh hôm nay, kết quả sẽ thấp
   hơn 7.289.000đ (SpaceX) / 5.208.560đ (ZaloPay) so với NAV thật đã ghi nhận. **NAV đã ghi là số
   đúng** (giá thực tế trên bảng điện phiên đó).
3. **Báo cáo thực thi ngày 01/07 không có cột giá khớp bình quân** (định dạng ngày đầu go-live) — giá
   trị giao dịch ngày đó (492.630.000đ) phải lấy từ journal, không đọc từ báo cáo.

### 10.3 Quy ước
- **Giá mark-to-market** = giá đóng cửa phiên cuối kỳ. Số liệu **cùng ngày** (định giá lệnh, sức mua,
  NAV sống) luôn lấy từ **API DNSE trực tiếp**, không lấy từ cơ sở dữ liệu thị trường (chỉ đồng bộ
  qua đêm).
- **Giá vốn vị thế legacy ZaloPay** (DGC, phần VPB cũ): dùng giá vốn broker DNSE báo — broker-native
  nhưng do broker tự tính, chưa đối soát với chứng từ gốc. **NAV không bị ảnh hưởng** (chỉ phụ thuộc
  khối lượng × giá thị trường).
- **Biến động năm hoá** = độ lệch chuẩn lợi suất ngày × √250. **Sụt giảm tối đa** tính trên chuỗi NAV
  ngày (SpaceX tính từ vốn góp 1.000.000.000; ZaloPay tính từ NAV bàn giao 06/07).
- **Phí/thuế:** giao dịch 0,075%/lượt (đã xác nhận biểu phí); thuế bán 0,1% giá trị bán theo quy định;
  lãi margin ~12,5%/năm **do nhà đầu tư cung cấp, chưa xác minh với DNSE**. **Không có phí quản lý,
  không có phí hiệu suất.**

### 10.4 Công bố tuân thủ & giới hạn
- **Track record 22 phiên (SpaceX) / 20 phiên (ZaloPay) là quá ngắn để đánh giá chiến lược.** Mọi so
  sánh với VN-Index trong báo cáo này **mang tính mô tả, không có ý nghĩa thống kê**. Việc danh mục
  giảm ít hơn chỉ số trong tháng đầu **không chứng minh** chiến lược tốt.
- **Sharpe/Sortino/Calmar cố ý KHÔNG được báo cáo** trong kỳ này vì thiếu dữ liệu; sẽ bắt đầu khi có
  tối thiểu ~6 tháng NAV ngày.
- **Toàn bộ số liệu trong báo cáo trace được về nguồn gốc broker.** Bất kỳ con số nào không trace được
  đều đã ghi rõ là **thiếu hoặc ước tính** (Mục 8.3) thay vì ước lượng thầm.
- **Đây không phải khuyến nghị đầu tư.** Kết quả quá khứ (kể cả backtest) không đảm bảo kết quả tương
  lai. Đầu tư cổ phiếu có rủi ro mất vốn.

---
*Báo cáo tháng 07/2026 · Tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn
(DNSE API) và cơ sở dữ liệu thị trường (BigQuery). Người phụ trách quỹ rà soát trước khi phát hành
cho nhà đầu tư.*
*Báo cáo tuần chi tiết: `SpaceX_weekly_report_2026-07-03.md` · `..._2026-07-06_to_2026-07-10.md` ·
`..._2026-07-13_to_2026-07-17.md` · `..._2026-07-20_to_2026-07-24.md` · `..._2026-07-27_to_2026-07-31.md`*
