# BÁO CÁO THÁNG — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: THÁNG 07/2026 (01/07 – 31/07/2026)
### *Tháng đầu tiên vận hành thật — SpaceX go-live 01/07, ZaloPay go-live 06/07*

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ **01/07/2026** (có margin) · vốn ban đầu **1.000.000.000 VND**
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ **06/07/2026** (cash-only) · tiếp nhận danh mục có sẵn
**Chiến lược:** V2.4 — 2 book tín hiệu (BAL momentum + LAG hậu-công-bố-lợi-nhuận), parking custom30V khi thị trường NEUTRAL, rổ CAPIT khi có bán tháo kiệt quệ
**Ngày lập báo cáo:** 01/08/2026 · **Bản sửa:** 02/08/2026 · **Người lập:** Taylor (Quant)
**Đối tượng:** Báo cáo hiệu suất & vận hành tháng — chuẩn mực quản lý tài sản, có thể chia sẻ với nhà đầu tư

---

> ## 🔧 BẢN SỬA 02/08/2026 — ĐIỀU CHỈNH CỔ TỨC TIỀN MẶT
>
> **Bản đầu tiên (01/08) tính THIẾU lãi/lỗ của 6 mã có trả cổ tức tiền mặt trong tháng 7.** Vào ngày
> chốt quyền, giá cổ phiếu trên sàn giảm đúng bằng mức cổ tức, nhưng báo cáo chỉ tính phần giá mà
> **quên cộng lại phần tiền cổ tức** — làm những mã trả cổ tức cao bị **báo lỗ nặng hơn thực tế**.
> Sai lệch lớn nhất: **NCT −11,6% → −3,1%** (8,5 điểm %) và **SAB −8,1% → −1,7%** (6,4 điểm %).
>
> **Toàn bộ NAV, tỷ suất tháng (−6,16% / −10,03%), giá trị danh mục và số dư tiền mặt trong bản cũ
> vẫn ĐÚNG, không đổi một đồng** — tiền cổ tức đã nằm sẵn trong số dư tài khoản (`totalCash` của
> DNSE bao gồm cả khoản cổ tức chờ về). Sai sót **chỉ nằm ở phần phân rã lãi/lỗ theo từng mã và
> theo nhóm ngành (Mục 3)** — tức phần *giải thích* kết quả, không phải bản thân kết quả.
>
> **Một kết luận trong bản cũ bị SAI VỀ DẤU và đã sửa:** rổ CAPIT được mô tả là "chỉ gánh 2,6% mức
> lỗ" — thực tế rổ này **LÃI +5.660.000đ** trong tháng sau khi cộng cổ tức.
>
> Các mục đã sửa: **3.1, 3.2, 3.3, 3.5** · Công bố đầy đủ nguyên nhân, số cũ/số mới: **Mục 8.4** ·
> Cạm bẫy số liệu ghi thêm: **Mục 10.2**.

> ## 🔧 BẢN SỬA #2 — phát hành lại lần hai, cùng ngày 02/08/2026
>
> **Bản sửa #1 (sáng 02/08) cộng cổ tức theo số GỘP — chưa trừ thuế thu nhập cá nhân 5%.** Cổ tức
> tiền mặt của nhà đầu tư cá nhân bị khấu trừ **5% ngay tại nguồn** khi công ty chứng khoán chi trả,
> nên số thực về tài khoản chỉ bằng **95%** mệnh giá công bố (VD: NCT 8.000đ/cp → thực nhận
> 7.600đ/cp). Bản sửa #1 vì vậy báo lãi/lỗ **tốt hơn thực tế một chút** — ngược chiều với sai sót
> của bản gốc, và nhỏ hơn nhiều về độ lớn.
>
> **Ảnh hưởng:** SpaceX lãi/lỗ chưa thực hiện **−50.435.443 (−5,11%) → −51.044.193 (−5,17%)** ·
> ZaloPay **−7.436.700 (−1,63%) → −7.759.375 (−1,71%)**. Ba mã vượt ngưỡng đáng công bố:
> **NCT −0,42pp · SAB −0,32pp · MBB −0,19pp**.
>
> **Kết luận rổ CAPIT có lãi vẫn ĐỨNG VỮNG** — thuế làm mỏng khoản lãi (**+5.660.000 → +5.295.000**)
> nhưng không đảo dấu. **NAV, tỷ suất tháng, giá trị danh mục, tiền mặt và mọi lệnh giao dịch: vẫn
> KHÔNG đổi.**
>
> Các mục sửa thêm: **3.1, 3.2, 3.3, 3.5** · Căn cứ pháp lý + bằng chứng đo từ tiền thật: **Mục 8.6**.

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

> 🔧 **Bảng này ĐÃ SỬA 02/08.** Cổ tức tiền mặt được **tách ra thành một dòng riêng** thay vì nằm lẫn
> trong số dư gộp cuối bảng. Tổng vẫn khớp NAV từng đồng như cũ; điều thay đổi là **giờ đã tách được**
> phần lãi/lỗ đã thực hiện, vốn trước đây bị cổ tức che khuất. Xem Mục 8.4.

| Cấu phần | VND | Ghi chú |
|---|---:|---|
| Vốn góp ban đầu (01/07) | 1.000.000.000 | |
| **Lãi/lỗ do GIÁ trên danh mục cuối tháng** | **−62.610.443** | ✅ đã xác minh từng mã |
| **+ Cổ tức tiền mặt được hưởng trong tháng (gộp)** | +12.175.000 | ✅ 6 mã, đối soát khớp sổ broker |
| **− Thuế TNCN 5% khấu trừ tại nguồn** | **−608.750** | 🔧 bản sửa #2 — xem Mục 8.6 |
| **+ Cổ tức RÒNG thực nhận** | **+11.566.250** | |
| **= Lãi/lỗ chưa thực hiện (tổng, gồm cổ tức ròng)** | **−51.044.193** | **−5,17%** trên giá vốn |
| Lãi/lỗ **đã thực hiện** ròng − phí/thuế | **−11.128.846** | ⚠️ số dư gộp — xem dưới |
| **= NAV 31/07** | **938.435.711** | ✅ khớp từng đồng với sổ broker |

**Cổ tức 12.175.000đ nằm ở đâu trong tài khoản:** 2.400.000đ (MBB, chốt 09/07) **đã về tiền mặt**;
9.775.000đ còn lại vẫn là **khoản phải thu cổ tức** tại 31/07 (DNSE ghi trong `cashDividendReceiving`,
đã tính vào NAV). Chi tiết 6 sự kiện: Mục 8.4.

**⚠️ Nói rõ điều chưa làm được:** dòng **−11.128.846** vẫn là một **số dư gộp**, không phải con số đã
được kiểm chứng riêng lẻ. Nó chứa: (a) lãi/lỗ đã thực hiện của **23 lệnh bán ngày 06/07** và lệnh bán
HPG 15/07; (b) phí giao dịch + thuế bán đã trừ; (c) chênh lệch quy ước giá vốn giữa hệ thống và
broker. **Không tách được chính xác nếu chưa có sao kê chính thức của DNSE** — đã đưa vào việc cần
làm (Mục 9), và **không thay bằng số ước lượng** trong báo cáo này. *(Bản cũ ghi dòng này là
**+1.046.154** vì cổ tức 12,175tr bị gộp chung vào đây; tách cổ tức ra cho thấy phần đã thực hiện
thực chất là một khoản **lỗ** ≈ −11,1tr, chủ yếu từ 23 lệnh bán ngày 06/07.)*

### 3.2 SpaceX — phân rã lãi/lỗ chưa thực hiện theo nhóm ngành (đã xác minh 100%)

> 🔧 **Bảng này ĐÃ SỬA 02/08** — thêm cột **Cổ tức**. Kết luận về rổ CAPIT trong bản cũ **SAI VỀ
> DẤU** (mô tả là "gánh 2,6% mức lỗ", thực tế **có lãi**). Số cũ và lý do: Mục 8.4.

| Nhóm | Giá trị TT 31/07 | % NAV | Lãi/lỗ do giá | + Cổ tức gộp | − Thuế 5% | **= Lãi/lỗ tổng (ròng)** |
|---|---:|---:|---:|---:|---:|---:|
| **Ngân hàng** (11 mã) | 534.870.000 | 57,0% | −56.220.442 | +4.875.000 | −243.750 | **−51.589.192** |
| Chứng khoán (VIX, VND, SHS) | 17.120.000 | 1,8% | −3.900.000 | 0 | 0 | **−3.900.000** |
| **Rổ CAPIT** (SIP, PVT, VNM, SAB, NCT) | 290.235.000 | 30,9% | −1.640.000 | **+7.300.000** | −365.000 | **+5.295.000** ✅ |
| Bất động sản (VHM) | 74.050.000 | 7,9% | −850.000 | 0 | 0 | **−850.000** |
| TV1 (ngoài V2.4) | 7.840.000 | 0,8% | 0 | 0 | 0 | **0** |
| **Tổng** | **924.115.000** | **98,5%** | **−62.610.443** | **+12.175.000** | **−608.750** | **−51.044.193** |

**Kết luận attribution rõ ràng: toàn bộ khoản lỗ chưa thực hiện đến từ nhóm ngân hàng**, chiếm 57%
NAV. Nguyên nhân: danh mục ngân hàng được xây trong 2 phiên đầu tháng (01–02/07) ở vùng giá cao
nhất của tháng, ngay trước nhịp giảm; nhóm ngân hàng cũng dẫn dắt đà giảm của thị trường trong tháng.
Cổ tức từ 4 mã ngân hàng (MBB, BID, CTG, VCB) bù lại được 4,6tr **sau thuế**, đưa mức lỗ nhóm này
từ −56,2tr xuống **−51,6tr**.

**Rổ CAPIT LÃI +5.295.000đ trong tháng (sau thuế TNCN 5%)** — chiếm gần 31% NAV. Phần giá gần như đi ngang (−1,6tr),
và **cổ tức 7,3tr gộp / 6,9tr ròng (NCT 4,0tr + SAB 3,3tr) đưa cả rổ sang trạng thái lãi** — thuế
làm mỏng khoản lãi (+5,66tr → +5,30tr) nhưng **không đảo dấu kết luận**. Rổ này nhận **60% toàn bộ
cổ tức của tài khoản** dù chỉ chiếm 31% NAV — đúng đặc tính thiết kế: CAPIT chọn cổ phiếu phòng thủ,
định giá rẻ, cổ tức cao. *(Bản cũ mô tả rổ này "chỉ gánh 2,6% mức lỗ" — đúng về phần giá nhưng bỏ
sót toàn bộ phần cổ tức, làm sai dấu kết luận.)*

**Vì sao tách "lãi/lỗ do giá" và "cổ tức" thành hai cột:** hai khoản nằm ở hai chỗ khác nhau trong
tài khoản — phần giá nằm trong giá trị cổ phiếu, phần cổ tức đã chuyển thành **tiền mặt** (hoặc
khoản phải thu). Cộng gộp một cột sẽ không đối chiếu được với sổ broker.

*Ghi chú làm tròn: cột "lãi/lỗ do giá" giữ nguyên số đã công bố (tính trên giá vốn có phần thập
phân). Tính lại chi tiết từng mã với giá vốn làm tròn cho rổ CAPIT **+5.294.900đ ròng** (gộp
+5.659.900đ) — chênh 100đ so với bảng, thuần tuý do làm tròn.*

### 3.3 SpaceX — 5 vị thế tốt nhất & 5 tệ nhất (lãi/lỗ chưa thực hiện, 31/07)

> 🔧 **ĐÃ SỬA 02/08 (bản sửa #2)** — các số dưới đây là **lãi/lỗ tổng đã cộng cổ tức RÒNG sau thuế
> TNCN 5%**, xếp theo VND. Thứ tự xếp hạng **không đổi** so với bản sửa #1.

| Tốt nhất | VND | % | | Tệ nhất | VND | % |
|---|---:|---:|---|---|---:|---:|
| PVT | **+4.200.000** | +7,0% | | TCB | **−9.900.000** | −14,6% |
| VNM | +2.070.000 | +3,9% | | BID | −8.670.650 | −10,6% |
| SIP | +1.769.700 | +2,2% | | CTG | −7.473.850 | −9,4% |
| TV1 | 0 | 0,0% | | VPB | −7.162.200 | −11,2% |
| LPB | −704.700 | −1,5% | | MBB | −5.760.000 | −9,3% |

*(Bốn mã ở cột "tốt nhất" cùng TCB/VPB **không trả cổ tức** trong tháng nên không đổi. BID/CTG/MBB
giảm đúng bằng thuế 5% của phần cổ tức: −42.750 / −51.750 / −120.000.)*

**Cả 3 vị thế lãi đều thuộc rổ CAPIT. Cả 5 vị thế lỗ nặng nhất đều là ngân hàng.** *(Kết luận này
không đổi sau khi sửa.)*

**Hai mã rời khỏi danh sách tệ nhất sau khi cộng cổ tức:** **NCT** (−11,6% → **−3,1%**, cổ tức
8.000đ/cp) và **SAB** (−8,1% → **−1,7%**, cổ tức 3.000đ/cp) — bản cũ xếp cả hai vào nhóm lỗ nặng.
Ba mã ngân hàng còn trong danh sách cũng bớt lỗ: BID −11,6% → −10,6%, CTG −10,7% → −9,4%,
**MBB −13,0% → −9,1%**.

### 3.4 ZaloPay — phân rã theo nguồn (đây là phần quan trọng nhất của báo cáo này)

| Cấu phần | 06/07 | 31/07 | Thay đổi | % |
|---|---:|---:|---:|---:|
| **DGC** — 10.000cp, legacy, **ngoài phạm vi bot** | 462.500.000 | 391.000.000 | **−71.500.000** | **−15,46%** |
| **Phần bot quản lý** (13 mã + tiền) | 525.365.567 | 497.828.498 | **−27.537.069** | **−5,24%** |
| **Tổng NAV** | 987.865.567 | 888.828.498 | −99.037.069 | −10,03% |

**DGC chiếm 72,2% toàn bộ mức lỗ của tài khoản**, dù chỉ chiếm 46,8% NAV đầu kỳ.

> ✅ **Bảng 3.4 KHÔNG bị ảnh hưởng bởi lỗi cổ tức** (kiểm tra lại 02/08): đây là bảng tính theo
> **NAV** (giá trị tài khoản, đã bao gồm tiền mặt), mà tiền cổ tức đã nằm sẵn trong tiền mặt — nên
> **−5,24%** của phần bot quản lý vốn đã là con số đúng. Lỗi cổ tức chỉ chạm bảng 3.5 dưới đây (tính
> theo giá vốn từng mã).

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

> 🔧 **ĐÃ SỬA 02/08 (bản sửa #2)** — bản gốc thiếu toàn bộ phần cổ tức (**−13.890.200 / −3,05%**);
> bản sửa #1 cộng cổ tức **gộp** (−7.436.700 / −1,63%); bản này trừ thêm **thuế TNCN 5%**.

| | VND | % giá vốn |
|---|---:|---:|
| Giá vốn thật (14 mã) | 454.848.300 | |
| Thị giá 31/07 | 440.958.100 | |
| → Lãi/lỗ do giá | −13.890.200 | −3,05% |
| **+ Cổ tức tiền mặt gộp (5 mã: NCT, SAB, CTG, BID, VCB)** | +6.453.500 | |
| **− Thuế TNCN 5% khấu trừ tại nguồn** | **−322.675** | |
| **+ Cổ tức RÒNG thực nhận** | **+6.130.825** | |
| **= Tổng lãi/lỗ chưa thực hiện (ròng)** | **−7.759.375** | **−1,71%** |

Vị thế lãi tốt nhất: **CSV +7,3%** · PVT +6,1% · VNM +3,7% · SIP +2,0% *(bốn mã này không có cổ tức
trong kỳ nên thuế không ảnh hưởng)*.
Vị thế lỗ nặng nhất **(sau khi cộng cổ tức ròng)**: **MBB −8,5%** · TCB −8,4% · LPB −5,5% · CTG −4,2%.

**Thay đổi đáng kể nhất so với bản gốc:** NCT **−11,7% → −3,6%** và SAB **−8,2% → −2,2%** — bản gốc
xếp hai mã này đứng đầu danh sách lỗ, sau khi sửa cả hai đều rời khỏi nhóm đó. *(Bản sửa #1 ghi
−3,2% và −1,9% theo cổ tức gộp; chênh lệch đúng bằng thuế 5%.)*

⚠️ **Một chi tiết dễ tính nhầm — MBB của ZaloPay KHÔNG được hưởng cổ tức:** tài khoản này mua MBB
**sau** ngày chốt quyền 09/07, nên dù MBB có trả 1.000đ/cp trong tháng, ZaloPay không nhận đồng nào
(SpaceX thì có). Đã kiểm chứng bằng số dư cổ tức phải thu của broker. Vì vậy tổng cổ tức ZaloPay là
**6.453.500đ trên 5 mã**, không phải 6 mã như SpaceX.

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
(hơn 1,91 điểm % trong một phiên). Cuối tháng rổ CAPIT **có lãi +5.295.000đ (sau thuế)** dù chiếm 31% NAV —
phần giá gần như đi ngang (−1,6tr) và cổ tức 7,3tr gộp / 6,9tr ròng (NCT + SAB) đưa cả rổ sang trạng
thái lãi *(🔧 sửa 02/08: bản gốc ghi "chỉ gánh 2,6% khoản lỗ", thiếu phần cổ tức — Mục 8.4; bản sửa
#2 trừ thêm thuế TNCN 5% — Mục 8.6)*. **Một tháng chưa đủ để kết
luận** — cần theo dõi hết chu kỳ khoá 60 phiên.

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
| 3 | **Không tách được lãi/lỗ đã thực hiện vs phí/thuế** của SpaceX (dòng −11.128.846, Mục 3.1). 🔧 *Cập nhật 02/08: phần **cổ tức** đã tách xong (12.175.000đ), khoảng trống thu hẹp lại còn realized vs phí* | Không ảnh hưởng NAV; ảnh hưởng độ chi tiết attribution | Taylor | báo cáo tháng 8 |
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

### 8.4 🔴 Sai sót số liệu phát hiện sau khi phát hành — THIẾU ĐIỀU CHỈNH CỔ TỨC TIỀN MẶT

**Phát hiện:** 02/08/2026, do nhà đầu tư nêu vấn đề. **Trạng thái:** đã sửa trong bản này.

**Cơ chế của lỗi.** Trong tháng 7, **6 mã trong danh mục trả cổ tức tiền mặt**. Vào ngày chốt quyền
(ngày giao dịch không hưởng quyền), giá cổ phiếu trên sàn **giảm đúng bằng mức cổ tức** — đây là cơ
chế bình thường của thị trường, không phải cổ phiếu mất giá: giá trị được chuyển từ *giá cổ phiếu*
sang *tiền mặt trong tài khoản*. Bản báo cáo đầu tiên tính lãi/lỗ từng mã theo công thức
`(giá cuối kỳ − giá vốn) / giá vốn`, tức **chỉ bắt phần giá và bỏ quên phần tiền**. Hệ quả: mã nào
trả cổ tức càng lớn thì bị **báo lỗ oan càng nhiều**.

**Sáu sự kiện cổ tức trong tháng và mức ảnh hưởng:**

> 🔧 **Bản sửa #2 (02/08)** thêm hai cột cuối: cổ tức bị khấu trừ **thuế TNCN 5% tại nguồn** (Mục 8.6),
> nên cột **% RÒNG** mới là số nhà đầu tư thực nhận.

| Mã | Ngày chốt quyền | Cổ tức/cp | SpaceX: KL → tiền gộp | % CŨ (sai) | % gộp (sửa #1) | Thuế 5% | **% RÒNG (đúng)** |
|---|---|---:|---|---:|---:|---:|---:|
| MBB | 09/07 | 1.000 | 2.400cp → 2.400.000 | −13,0% | −9,1% | −120.000 | **−9,3%** |
| BID | 17/07 | 450 | 1.900cp → 855.000 | −11,6% | −10,6% | −42.750 | **−10,6%** |
| CTG | 23/07 | 450 | 2.300cp → 1.035.000 | −10,7% | −9,4% | −51.750 | **−9,4%** |
| VCB | 23/07 | 450 | 1.300cp → 585.000 | −4,8% | −4,1% | −29.250 | **−4,1%** |
| **NCT** | 27/07 | **8.000** | 500cp → 4.000.000 | −11,6% | −3,1% | −200.000 | **−3,6%** |
| **SAB** | 28/07 | **3.000** | 1.100cp → 3.300.000 | −8,1% | −1,7% | −165.000 | **−2,0%** |
| | | | **Tổng SpaceX: 12.175.000** | −6,35% | −5,11% | **−608.750** | **−5,17%** |

Với **ZaloPay**, 5 mã được hưởng (**tổng gộp 6.453.500đ**, thuế **−322.675đ**, ròng **6.130.825đ**) —
MBB không được hưởng vì tài khoản mua **sau** ngày chốt quyền 09/07. Tổng phần bot quản lý:
**−3,05% (bản gốc) → −1,63% (gộp) → −1,71% (ròng)**.

**Vì sao khẳng định đây là cổ tức TIỀN MẶT chứ không phải chia tách cổ phiếu** (hai loại sự kiện này
đều làm giá tham chiếu giảm, nhưng ý nghĩa hoàn toàn khác): đã kiểm chứng bằng **ba nguồn độc lập** —
(i) **số lượng cổ phiếu tại broker KHÔNG đổi** qua mọi ngày chốt quyền (chia tách sẽ làm số lượng
tăng); (ii) **số dư cổ tức phải thu** của DNSE (`cashDividendReceiving`) tăng đúng bằng
`số lượng × cổ tức` từng lần, cộng dồn khớp từng đồng với số dư cuối kỳ; (iii) **giá vốn do broker
báo** đã bị trừ đúng phần cổ tức (ví dụ MBB: 24.850 + 1.000 = 25.850 = giá mua thật).

**Điều KHÔNG thay đổi — quan trọng với nhà đầu tư:**
- **NAV cuối tháng, tỷ suất tháng (SpaceX −6,16%, ZaloPay −10,03%), giá trị danh mục và số dư tiền
  mặt: giữ nguyên, vẫn đúng.** Tiền cổ tức đã nằm trong số dư tài khoản từ đầu (`totalCash` của DNSE
  bao gồm cả khoản cổ tức chờ về) — đã kiểm chứng lại bằng số học trên bản ghi số dư gốc.
- Các mục 2 (hiệu suất vs chỉ số), 4 (rủi ro), 5 (phí), 6 (nhật ký), 7 (danh mục) **không đổi**.
- Sai sót nằm ở **Mục 3 — phần giải thích/phân rã kết quả**, không phải bản thân kết quả.

**Một kết luận bị sai về dấu:** rổ CAPIT trong bản gốc được mô tả là "chỉ gánh 2,6% mức lỗ" — sau khi
cộng cổ tức, rổ này thực chất **LÃI +5.660.000đ gộp / +5.295.000đ ròng sau thuế** (Mục 8.6). Đây là
sai sót có ý nghĩa vì nó đảo ngược nhận định về cấu phần phòng thủ quan trọng nhất của danh mục
(31% NAV) — và kết luận "có lãi" **đứng vững cả sau thuế**.

**Chống tái diễn:** đã viết công cụ dùng chung `mike/bin/dividend_adjusted_return.py` — tự phát hiện
sự kiện cổ tức từ cơ sở dữ liệu thị trường, **bắt buộc đối soát với sổ broker** trước khi đưa vào báo
cáo (sự kiện chưa đối soát bị gắn cờ `UNVERIFIED` và không được dùng), kèm bộ tự kiểm 16 phép thử.
Mọi báo cáo từ kỳ sau bắt buộc dùng công cụ này.

### 8.5 🔴 Sai sót thứ hai, phát hiện khi rà soát — chuỗi NAV đếm hai lần cổ tức đúng ngày chốt quyền

Khi kiểm tra lỗi trên, phát hiện thêm một vấn đề **độc lập** trong cách ghi NAV hằng ngày:
DNSE ghi khoản cổ tức phải thu vào **cuối ngày cuối cùng còn hưởng quyền**, trong khi giá cổ phiếu
dùng để định giá danh mục ngày đó **vẫn là giá còn quyền** (đã bao gồm giá trị cổ tức). Công cụ ghi
NAV (`daily_nav_snapshot.py`) lấy tiền mặt = `totalCash` (đã gồm cổ tức phải thu) → **cộng hai lần**
giá trị cổ tức đúng phiên đó, và tự triệt tiêu ở phiên kế tiếp.

| Tài khoản | Ngày | NAV đã ghi | Đếm trùng | NAV đúng |
|---|---|---:|---:|---:|
| SpaceX | 16/07 | 957.558.637 | 855.000 | 956.703.637 |
| SpaceX | **24/07** | 910.995.894 | **4.000.000** | **906.995.894** |
| SpaceX | 27/07 | 900.428.641 | 3.300.000 | 897.128.641 |
| ZaloPay | 16/07 | 953.593.885 | 405.000 | 953.188.885 |
| ZaloPay | **24/07** | 849.855.112 | **2.984.000** | **846.871.112** |

**Ảnh hưởng tới báo cáo THÁNG này: BẰNG KHÔNG** — cả hai đầu kỳ (01/07 và 31/07) đều không rơi vào
ngày chốt quyền, nên tỷ suất tháng **−6,16% / −10,03% không đổi**. Ảnh hưởng chỉ nằm ở **tỷ suất
TUẦN** của hai tuần 20–24/07 và 27–31/07 (dịch lãi/lỗ *giữa* hai tuần, tổng hai tuần không đổi) — đã
công bố trong hai báo cáo tuần tương ứng.

**Chưa tự sửa chuỗi NAV lịch sử** (`nav_history_*.csv` là dữ liệu vận hành production, sửa cần quy
trình riêng) — đã công bố ở đây và đề xuất khắc phục vào việc cần làm Mục 9.4.

---

### 8.6 🔴 Sai sót thứ ba (bản sửa #2, 02/08) — cổ tức phải trừ thuế TNCN 5%

**Phát hiện:** 02/08/2026, do nhà đầu tư nêu vấn đề (lần thứ hai trong ngày). **Trạng thái:** đã sửa
trong bản này.

**Cơ chế.** Bản sửa #1 sáng nay cộng cổ tức theo **số GỘP** (mệnh giá công bố). Nhưng cổ tức tiền mặt
trả cho **nhà đầu tư cá nhân** bị khấu trừ **thuế thu nhập cá nhân 5% ngay tại nguồn** — công ty
chứng khoán trừ trước khi tiền vào tài khoản. Nhà đầu tư **không phải tự kê khai** và **không quyết
toán lại** theo biểu lũy tiến: 5% là mức khoán, xong nghĩa vụ. Vì vậy số thực nhận chỉ bằng **95%**:

| Mã | Cổ tức công bố | Thực nhận sau thuế |
|---|---:|---:|
| NCT | 8.000đ/cp | **7.600đ/cp** |
| SAB | 3.000đ/cp | **2.850đ/cp** |
| MBB | 1.000đ/cp | **950đ/cp** |
| CTG · BID · VCB | 450đ/cp | **427,5đ/cp** |

Lưu ý **chiều của sai sót**: bản gốc báo lỗ **nặng hơn** thực tế (bỏ quên cổ tức); bản sửa #1 báo
**tốt hơn** thực tế (quên thuế). Sai sót lần này **nhỏ hơn nhiều** về độ lớn (−0,06pp ở mức danh mục
so với +1,24pp của lần trước), nhưng vẫn công bố vì ba mã vượt ngưỡng: **NCT −0,42pp · SAB −0,32pp ·
MBB −0,19pp** — đúng những mã mà bản sửa #1 vừa lấy làm tiêu đề đính chính.

**Đây không phải giả định — đã đo được bằng tiền thật.** Ngày **17/07/2026**, cổ tức MBB của SpaceX là
khoản **duy nhất trong tháng 7 đã thực sự chi trả** (5 khoản còn lại tới 02/08 vẫn là *phải thu*):

| | 16/07 | 17/07 | Chênh |
|---|---:|---:|---:|
| Cổ tức phải thu | 3.255.000 | 855.000 | **−2.400.000** *(= 2.400cp × 1.000đ, đúng mệnh giá ⇒ ghi GỘP)* |
| Tiền thật vào tài khoản | | | **+2.280.000** |
| **Chênh lệch = thuế** | | | **120.000 = đúng 5,0000%** |

*(Cùng ngày có khoản rút tiền 302.108.211đ — đã hoàn nguyên; con số này được xác nhận độc lập bởi hai
nguồn có trước phép tính: bản chụp tài sản ngoài sổ 17/07 và trường "tiền được phép rút" 16/07. Danh
mục cổ phiếu hai ngày **không đổi một mã nào** nên không có dòng tiền nào khác gây nhiễu. Giả thuyết
cạnh tranh "đây là phí thu hộ cổ tức" đã bị loại: con số đúng bằng 5,0000% chứ không phải một biểu
phí cố định, và DNSE không công bố loại phí này.)*

**Căn cứ pháp lý:** Thông tư 111/2013/TT-BTC — Điều 10 (thuế suất 5% với thu nhập từ đầu tư vốn),
Điều 25 (khấu trừ tại nguồn, thời điểm khấu trừ là **lúc chi trả thật**, không phải lúc ghi nhận phải
thu). Luật Thuế TNCN mới **109/2025/QH15** (hiệu lực **01/07/2026**, áp dụng cho toàn bộ 6 sự kiện
này) **giữ nguyên mức 5%** cho thu nhập từ đầu tư vốn — luật mới chỉ sửa biểu lũy tiến của thu nhập
từ tiền lương. Cả hai tài khoản đều đứng tên **cá nhân**, đúng đối tượng chịu mức 5%.

*(Ưu đãi giảm 50% thuế của Luật 109/2025 chỉ áp dụng cho lợi tức chia từ **quỹ đầu tư**; danh mục hiện
tại là **cổ phiếu trực tiếp** nên giữ 5%. Đây là lý do thuế suất được cài đặt thành **tham số** trong
công cụ tính, không cố định cứng.)*

#### Ảnh hưởng tới NAV — khoản thuế sẽ bị trừ trong tương lai

Tại 31/07, phần cổ tức **chưa được chi trả** vẫn nằm trong số dư theo **số gộp**, nên NAV công bố cao
hơn thực tế đúng bằng khoản thuế sẽ bị khấu trừ khi tiền về:

| Tài khoản | Cổ tức còn phải thu (gộp) | Thuế sẽ bị trừ | NAV đã công bố | NAV sau điều chỉnh | Tỉ lệ |
|---|---:|---:|---:|---:|---:|
| SpaceX | 9.775.000 | −488.750 | 938.435.711 | 937.946.961 | 0,052% |
| ZaloPay | 6.453.500 | −322.675 | 888.828.498 | 888.505.823 | 0,036% |

Khoản này **chắc chắn sẽ mất** (nghĩa vụ thuế theo luật), không phải rủi ro ước lượng — nên công bố dù
nhỏ. Các bảng NAV trong báo cáo giữ nguyên số gốc để khớp sổ đã ghi; **tỷ suất tháng −6,16% / −10,03%
không đổi**.

**Giới hạn cần nói rõ:** phép đo 5,00% dựa trên **một** sự kiện đã chi trả (n=1). Khi khoản thứ hai về
tiền sẽ lặp lại đúng phép đo này để xác nhận. Mức 5% đồng thời khớp với luật định nên rủi ro còn lại
thấp — nhưng vẫn được ghi nhận là n=1.

**Công cụ đã cập nhật:** `mike/bin/dividend_adjusted_return.py` thêm tầng thuế (tham số
`--div-tax-rate`, mặc định 5%), **luôn hiển thị cả số gộp lẫn số ròng** để đối chiếu. Tự kiểm
**58/58 đạt**, tái lập được dưới nhiều môi trường khác nhau.

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
| 5 | Tách nốt lãi/lỗ đã thực hiện vs phí/thuế của SpaceX (dòng gộp −11.128.846; phần cổ tức đã tách xong 02/08) | **Taylor** | **báo cáo tháng 8** |
| 5b | 🔧 **MỚI 02/08** — sửa `daily_nav_snapshot.py` để không đếm hai lần cổ tức đúng ngày chốt quyền (Mục 8.5), và hiệu chỉnh 5 dòng NAV lịch sử đã nêu | **Winston / Taylor** | **08/08/2026** |
| 5c | 🔧 **MỚI 02/08** — bắt buộc mọi báo cáo kỳ sau dùng `mike/bin/dividend_adjusted_return.py`; đưa quy tắc vào tài liệu chuẩn của đội | **Taylor** | **đã xong 02/08** |
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

### 10.2 Năm cạm bẫy số liệu đã gặp trong tháng — ghi lại để ai kiểm tra lại không nhầm
1. **Journal khớp lệnh ghi khối lượng LUỸ KẾ theo lệnh con** — cộng dồn thẳng các dòng FILL sẽ ra số
   **lớn hơn thực tế**. Số trong báo cáo lấy từ **báo cáo thực thi từng phiên + sổ vị thế broker**
   (hai nguồn đã đối chiếu khớp nhau).
2. **Giá lịch sử bị hồi tố điều chỉnh cổ tức** — NCT giao dịch không hưởng quyền từ **27/07** (8.000đ/cp)
   và SAB từ **28/07** (3.000đ/cp). Nếu tính lại NAV ngày 24/07 bằng giá đã điều chỉnh hôm nay, kết quả
   sẽ thấp hơn 7.289.000đ (SpaceX) / 5.208.560đ (ZaloPay) so với NAV thật đã ghi nhận. **NAV đã ghi là
   số đúng** (giá thực tế trên bảng điện phiên đó). *(🔧 Sửa 02/08: bản cũ ghi SAB "27/07, 2.990đ" —
   sai cả ngày lẫn số tiền, xem cạm bẫy #4.)*
3. **Báo cáo thực thi ngày 01/07 không có cột giá khớp bình quân** (định dạng ngày đầu go-live) — giá
   trị giao dịch ngày đó (492.630.000đ) phải lấy từ journal, không đọc từ báo cáo.
4. **🔴 Suy ra cổ tức bằng phép TRỪ hai cột giá là SAI** — cơ sở dữ liệu thị trường có hai cột giá:
   `Price` (giá thô, đúng giá trên bảng điện) và `Close` (đã hồi tố điều chỉnh cổ tức). Quan hệ giữa
   chúng là **phép NHÂN (tỉ số), không phải phép trừ**: tỉ số `Close/Price` là hằng số giữa hai ngày
   chốt quyền và nhảy về 1,0 đúng ngày chốt quyền. Lấy hiệu `Close − Price` sẽ cho số **biến thiên
   theo mức giá** — chính cái bẫy này tạo ra con số "SAB 2.990đ" ở cạm bẫy #2 (giá trị thật là đúng
   **3.000đ**; 2.990 là kết quả của việc áp tỉ số lên giá ngày 24/07 thay vì ngày 27/07). Công thức
   đúng: `cổ tức/cp = P_ngày_cuối_còn_quyền × (1 − tỉ_số_còn_quyền / tỉ_số_sau_chốt)`. Đã đóng gói
   trong `mike/bin/dividend_adjusted_return.py`.
5. **🔴 Trộn hai hệ quy chiếu giá = phạt cổ tức hai lần** — lấy **thị giá đã điều chỉnh** (`Close`)
   trừ **giá vốn thô** (giá khớp thật đã trả) sẽ trừ phần cổ tức hai lần. Quy tắc: giá vốn thô thì
   phải so với giá **thô** (`Price`), rồi **cộng cổ tức vào tử số**. Lỗi này đã thực sự xảy ra trong
   báo cáo tuần 20–24/07 (đã sửa trong bản 02/08 của báo cáo đó).

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
