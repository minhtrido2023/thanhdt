# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: 27/07/2026 – 31/07/2026

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ 01/07/2026 (có margin)
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ 06/07/2026 (cash-only, không margin)
**Chiến lược:** V2.4 (2 book BAL/LAG + parking custom30V tại NEUTRAL + rổ CAPIT bear-washout)
**Ngày lập báo cáo:** 01/08/2026 · **Người lập:** Taylor (Quant) — số liệu đối soát qua pipeline xác minh chuẩn (Mục 8)
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

> ⚠️ **Báo cáo nộp chậm 1 ngày** (lẽ ra 31/07–01/08). Cùng nguyên nhân quy trình đã nêu ở báo cáo
> tuần 20–24/07 Mục 7.1: cảnh báo "báo cáo quá hạn" bị chôn trong log kiểm tra vận hành. Dữ liệu gốc
> nguyên vẹn, đã đối soát đầy đủ.

> ## 🔧 BẢN SỬA — phát hành lại ngày 02/08/2026
> **Bản đầu tiên (01/08) tính THIẾU lãi/lỗ của 6 mã có trả cổ tức tiền mặt trong tháng 7.** Giá cổ
> phiếu giảm đúng bằng cổ tức vào ngày chốt quyền, nhưng báo cáo không cộng phần tiền cổ tức trở lại
> → % lãi/lỗ của các mã đó bị **báo lỗ nặng hơn thực tế** (NCT ghi −11,6% trong khi thật là −3,1%).
> **Toàn bộ số NAV, giá trị danh mục và tiền mặt trong bản cũ vẫn ĐÚNG** — tiền cổ tức đã nằm sẵn
> trong NAV; sai sót chỉ ở phần **% lãi/lỗ của từng mã** và **phân rã theo nhóm**.
> Chi tiết đầy đủ số cũ/số mới/nguyên nhân: **Mục 11 — ĐIỀU CHỈNH CỔ TỨC**. Mục 11 cũng công bố
> thêm một sai sót thứ hai vừa phát hiện (chuỗi NAV đếm hai lần cổ tức đúng ngày chốt quyền).

> ## 🔧 BẢN SỬA #2 — phát hành lại lần hai, cùng ngày 02/08/2026
> **Bản sửa #1 (sáng 02/08) cộng cổ tức theo số GỘP — chưa trừ thuế thu nhập cá nhân 5%.** Cổ tức
> tiền mặt của nhà đầu tư cá nhân bị khấu trừ **5% tại nguồn** khi công ty chứng khoán chi trả, nên
> số thực về tài khoản chỉ bằng **95%** mệnh giá công bố (VD: NCT 8.000đ/cp → thực nhận 7.600đ/cp).
> Bản sửa #1 vì vậy báo lãi/lỗ **tốt hơn thực tế một chút**, ngược chiều với sai sót của bản gốc.
> **Ảnh hưởng: SpaceX −5,1% → −5,2%; ZaloPay (phần bot mua) −1,63% → −1,71%.** Ba mã vượt ngưỡng
> đáng công bố: **NCT −0,42pp · SAB −0,32pp · MBB −0,19pp**.
> **NAV, giá trị danh mục, tiền mặt và mọi lệnh giao dịch: vẫn KHÔNG đổi.** Chi tiết + căn cứ pháp
> lý + bằng chứng đo từ tiền thật: **Mục 11.6**.

---

> **✅ Nguồn số liệu:** NAV/giá vốn/lãi-lỗ chạy qua pipeline xác minh bắt buộc:
> `verify_account_snapshot.py` (chạy có `--account-no` tường minh cho **cả 2** tài khoản) —
> **cả 2 Verified = True, 0 lệch khối lượng**; chuỗi NAV ngày từ `nav_history_{account}.csv`; giá
> mark-to-market = giá đóng cửa 31/07. **Kiểm tra độc lập: giá trị cổ phiếu tính lại từ sổ vị thế
> broker × giá đóng cửa 31/07 khớp TỪNG ĐỒNG với chuỗi NAV ở cả 2 tài khoản** (SpaceX 924.115.000;
> ZaloPay 876.598.100). Một lỗi số liệu thật đã được phát hiện và sửa trong quá trình lập báo cáo —
> Mục 7.1.

---

## 1. TÓM TẮT ĐIỀU HÀNH

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (chốt 24/07) | 910.995.894 | 849.855.112 |
| NAV cuối kỳ (31/07) | **938.435.711** | **888.828.498** |
| Thay đổi trong kỳ | **+27.439.817 (+3,01%)** ᴬ | **+38.973.386 (+4,59%)** ᴬ |
| VN-Index cùng kỳ (24/07 → 31/07) | 1.686,11 → 1.735,78 (**+2,95%**) | (cùng chỉ số) |
| **Chênh so với chỉ số** | **+0,06 điểm %** | **+1,64 điểm %** |
| — Trong đó riêng DGC (ngoài phạm vi bot) | — | **+22.500.000 (+6,11%)** |
| — Phần bot quản lý (loại DGC) | — | **+3,42%** (tốt hơn chỉ số +0,47pp) |
| Cổ phiếu cuối kỳ (giá đóng cửa 31/07) | 924.115.000 | 876.598.100 |
| Tiền mặt tại công ty CK | 14.326.923 | 12.237.594 |
| Nợ margin cuối kỳ | 6.212 | 7.196 (phí, không phải vay) |
| Tỷ trọng cổ phiếu/NAV | **98,5%** | **98,6%** (gồm DGC 44,0%) |
| Số mã nắm giữ cuối kỳ | 21 | 16 |

ᴬ **NAV đầu kỳ (24/07) bị ghi cao hơn thực tế** do cổ tức NCT bị đếm hai lần đúng phiên chốt quyền
(SpaceX 4,0tr · ZaloPay 2,98tr). Sau khi trung hoà, mức tăng thật cả tuần là **SpaceX +3,47%** và
**ZaloPay +4,95%** — tức **tốt hơn** số ghi trong bảng. Chi tiết Mục 11.5. Bảng giữ số gốc để khớp
với sổ NAV đã ghi.

**Nhận định tuần:** thị trường **bật lại mạnh sau ba tuần rơi liên tiếp** — VN-Index +2,95%, riêng
phiên 30/07 tăng +2,35%. Cả 2 tài khoản đều **tăng nhiều hơn chỉ số**:

- **SpaceX +3,01%** (+0,06pp so với chỉ số) — đúng như kỳ vọng với một danh mục gần như đầu tư toàn
  bộ (98,5% cổ phiếu). Đáng chú ý là **nhóm CAPIT dẫn dắt đà hồi**: PVT +8,6%, SIP +3,0%, VNM +3,4%
  trong tuần.
- **ZaloPay +4,59%** (+1,64pp) — DGC hồi mạnh (+6,11%, +22,5tr) sau cú sập tuần trước, cộng thêm
  phần bot quản lý +3,42%. Cả hai cấu phần đều đóng góp dương.
- **Đây là tuần đầu tiên kể từ go-live mà book LAG (đón sóng sau công bố lợi nhuận) phát tín hiệu
  thật và được thực thi** — 2 lệnh trên ZaloPay (VPB và CSV), Mục 3.2. Mùa báo cáo tài chính Q2/2026
  đã "đánh thức" kênh tín hiệu vốn rỗng suốt tháng.
- **DT5G giữ NEUTRAL (3/5) cả 5 phiên.** Không có cap phòng thủ vĩ mô nào kích hoạt.

**Bối cảnh cần giữ trong đầu:** mức hồi phục tuần này **chưa bù lại** mức mất của tuần trước. Tính
gộp 2 tuần (17/07 → 31/07): SpaceX **−1,37%**, ZaloPay **−6,43%**, VN-Index **−2,89%**.

---

## 2. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

| Ngày | VN-Index | Δ ngày | Ghi chú |
|---|---:|---:|---|
| 24/07 (đầu kỳ) | 1.686,11 | — | |
| 27/07 | 1.669,01 | −1,01% | đáy của nhịp giảm |
| 28/07 | 1.680,62 | +0,70% | |
| 29/07 | 1.704,68 | +1,43% | lấy lại mốc 1.700 |
| 30/07 | 1.744,66 | **+2,35%** | phiên tăng mạnh nhất tháng |
| 31/07 (cuối kỳ) | 1.735,78 | −0,51% | chốt tháng |

- Cả tuần **+2,95%**, chấm dứt chuỗi 3 tuần giảm. Tuy vậy chỉ số vẫn thấp hơn **−6,68%** so với cuối
  tháng 6 (1.860,01).
- **DT5G = NEUTRAL (3/5) toàn bộ tuần** (nguồn: `vnindex_5state_dt5g_live`) — không đổi trạng thái
  suốt tháng 7. Hệ thống **không** chuyển sang phòng thủ trong nhịp giảm, và cũng **không** tăng
  đòn bẩy trong nhịp hồi. Kỷ luật này chính là thứ giữ cho danh mục ở lại thị trường đúng lúc hồi.

---

## 3. HOẠT ĐỘNG GIAO DỊCH TRONG TUẦN

### 3.1 SpaceX — 3 lệnh khớp, 1 lệnh không khớp (đúng thiết kế)

| Ngày | Lệnh | Mã | KL kế hoạch | KL khớp | Giá tham chiếu | Giá khớp BQ | Giá trị (VND) | Mục đích |
|---|---|---|---:|---:|---:|---:|---:|---|
| 27/07 | Mua | SIP | 600 | 600 (100%) | 47.200 | 46.942 | 28.165.200 | **CAPIT** bổ sung |
| 27/07 | Mua | TV1 | 400 | **0 (0%)** | 19.800 | — | 0 | TV1 (giá không về) |
| 28/07 | Mua | TV1 | 400 | 100 (25%) | 19.600 | 19.600 | 1.960.000 | TV1 |
| 29/07 | Mua | TV1 | 300 | 300 (100%) | 19.400 | 19.600 | 5.880.000 | TV1 |

- **Tổng mua: 36.005.200đ. Phí giao dịch 0,075% ≈ 27.004đ. Không có lệnh bán → không có lãi/lỗ thực
  hiện, không có thuế bán.**
- **SIP bổ sung 27/07:** nâng vị thế CAPIT SIP từ 1.100cp lên 1.700cp (giá vốn bình quân mới 47.059).
  Đây là phần bù cho mục tiêu chưa đạt ngày 21/07 do giới hạn tiền. Vẫn còn **thiếu ~33,2tr** so với
  mục tiêu đầy đủ của mã này — phần thiếu được ghi nhận **DEFER (hoãn)**, không huỷ, do tiền mặt đã
  cạn.
- **Chương trình gom TV1 (PECC1) — HOÀN TẤT 400cp, giá bình quân 19.600.** Đây là khoản mua **ngoài
  chiến lược V2.4**, do nhà đầu tư duyệt riêng theo luận điểm "mua khi thị trường sợ hãi có tính
  toán", với ràng buộc cứng **không mua trên 20.000**. Ngày 27/07 giá không về vùng đặt → **không
  khớp, hệ thống không đuổi giá**; ngày 28–29/07 khớp đủ. Giá trị vị thế 7,84tr (**0,84% NAV**) —
  quy mô rất nhỏ, mang tính thăm dò.
- **Phiên 30/07 và 31/07 — HOLD, không lệnh nào.** BAL rỗng, rổ CAPIT giữ theo quy tắc 60 phiên.
  Danh mục **không bán ra để chốt lời** trong 2 phiên tăng mạnh nhất — đúng kỷ luật, không phải bỏ
  lỡ do lỗi.

### 3.2 ZaloPay — 3 lệnh, khớp 100%; book LAG kích hoạt lần đầu

| Ngày | Lệnh | Mã | KL | Giá khớp BQ | Giá trị (VND) | Mục đích |
|---|---|---|---:|---:|---:|---|
| 27/07 | Bán | VPB | 800 | 24.900 | 19.920.000 | **Hoàn tất** trim VPB legacy |
| 27/07 | Mua | VPB | 700 | 24.950 | 17.465.000 | **LAG_LO** — tín hiệu sau công bố LN |
| 28/07 | Mua | CSV | 1.000 | 19.750 | 19.750.000 | **LAG_HI** — tín hiệu sau công bố LN |

**Tổng: mua 37.215.000đ · bán 19.920.000đ.** Phí giao dịch 0,075% ≈ **42.851đ**; thuế bán 0,1% ≈
**19.920đ**.

**⚠️ Giải thích lệnh "bán VPB rồi mua lại VPB cùng ngày 27/07" — KHÔNG phải lỗi, KHÔNG phải giao
dịch vòng vo.** Đây là hai quyết định độc lập từ hai cơ chế khác nhau tình cờ rơi vào cùng phiên:

1. **Bán 800cp** = bước cuối của chương trình giảm vị thế VPB legacy đã được duyệt từ 23/07 (VPB
   từng chiếm 38,8% active NAV, vượt xa trần 10%/mã). Sau lệnh này VPB legacy về **1.100cp**, tức
   **dưới trần** — chương trình kết thúc.
2. **Mua 700cp** = một **tín hiệu mới hoàn toàn** từ book LAG: VPB công bố lợi nhuận ngày 20/07 với
   **lợi nhuận ròng tăng 72% so với cùng kỳ**, vượt kỳ vọng đủ mạnh để lọt bộ lọc PEAD (hiệu ứng
   trôi giá sau công bố lợi nhuận). Quy mô 17,5tr = 8% của book LAG, hoàn toàn khác vai trò với vị
   thế legacy cũ.

Kết quả ròng: VPB 1.900cp → **1.800cp** (giá vốn bình quân mới 26.745). **Chi phí của việc "bán rồi
mua"**: chênh giá bán/mua 50đ/cp trên 700cp (35.000đ) + phí/thuế ≈ 48.000đ → **tổng ≈ 83.000đ
(0,009% NAV)** — không đáng kể, nhưng ghi rõ để nhà đầu tư kiểm chứng được. *Ghi nhận cải tiến khả
thi: nếu hai cơ chế biết đến nhau, có thể bù trừ nội bộ 700cp và chỉ bán ròng 100cp. Đây là đề xuất
tối ưu hoá, không phải lỗi vận hành.*

**CSV (Hoá chất Cơ bản Miền Nam) — tín hiệu LAG_HI, khớp rất tốt:** đặt mua theo tín hiệu ngày
28/07, khớp toàn bộ 1.000cp ở **19.750**, trong khi giá thấp nhất phiên là 19.250 và giá đóng cửa
**20.750** — tức khớp thấp hơn giá đóng cửa **−4,8%**. Đến 31/07 CSV đạt 21.200, **lãi chưa thực
hiện +1.450.000đ (+7,3%)**, là vị thế sinh lời tốt nhất tuần.

**Lãi/lỗ thực hiện trong tuần** (bán VPB legacy, giá vốn broker 27.886,67):

| Mã | KL bán | Giá vốn broker | Giá bán | Lãi/lỗ thực hiện |
|---|---:|---:|---:|---:|
| VPB | 800 | 27.886,67 | 24.900 | **−2.389.336 (−10,71%)** |

Trừ thuế + phí bán ≈ **−34.860đ** → lãi/lỗ thực hiện ròng ≈ **−2.424.196đ**. Cộng với 4 lệnh tuần
trước, tổng chương trình trim VPB đã hiện thực hoá lỗ **≈ −11,1tr** — cái giá của việc đưa một vị
thế quá tập trung (38,8% active NAV) về đúng chính sách rủi ro.

---

## 4. TÀI KHOẢN SPACEX

### 4.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ | Chênh | Ghi chú |
|---|---:|---:|---:|---:|---|
| 24/07 (đầu kỳ) | 910.995.894 | — | — | — | |
| 27/07 | 900.428.641 | −1,16% | −1,01% | −0,15pp | Mua SIP 600cp |
| 28/07 | 903.966.973 | +0,39% | +0,70% | −0,30pp | Mua TV1 100cp |
| 29/07 | 909.881.823 | +0,65% | +1,43% | −0,78pp | Mua TV1 300cp |
| 30/07 | 936.651.848 | **+2,94%** | +2,35% | **+0,60pp** | HOLD |
| 31/07 (cuối kỳ) | 938.435.711 | +0,19% | −0,51% | **+0,70pp** | HOLD |

Cả tuần **+3,01%** vs chỉ số **+2,95%**. Đặc điểm rõ: danh mục **tụt lại ở 3 phiên đầu** (nhóm ngân
hàng hồi chậm) rồi **bứt lên ở 2 phiên cuối** khi nhóm CAPIT và tiêu dùng chạy. Chuỗi NAV tuần này
**đầy đủ, không thiếu dòng nào**.

### 4.2 Danh mục cuối kỳ (31/07 — giá vốn THẬT đã xác minh × giá đóng cửa 31/07)

> 🔧 **Bảng này ĐÃ SỬA ngày 02/08.** Thêm cột **Cổ tức** (tiền mặt đã nhận/chờ về trong kỳ nắm giữ)
> và cột **% tổng** = (giá cuối kỳ + cổ tức − giá vốn) / giá vốn. Bản cũ chỉ có cột "%" tính theo
> giá, làm 6 mã có cổ tức bị **báo lỗ nặng hơn thực tế**. Số cũ ghi ở Mục 9.

> 🔧 **CẬP NHẬT BẢN SỬA #2 (02/08):** cột **Cổ tức** dưới đây là số **RÒNG sau thuế TNCN 5%** (số
> gộp theo mệnh giá công bố ghi trong ngoặc), và cột **% tổng** tính theo số ròng. Xem Mục 11.6.

| Mã | KL | Giá vốn thật | Giá 31/07 | Giá trị TT (VND) | Lãi/lỗ do giá | Cổ tức ròng *(gộp)* | % tổng | Nhóm |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| SIP | 1.700 | 47.059 | 48.100 | 81.770.000 | **+1.770.000** | — | +2,2% | CAPIT |
| VCB | 1.300 | 62.300 | 59.300 | 77.090.000 | −3.900.000 | +555.750 *(585.000)* | **−4,1%** | Ngân hàng |
| VHM | 500 | 149.800 | 148.100 | 74.050.000 | −850.000 | — | −1,1% | Bất động sản |
| BID | 1.900 | 42.991 | 38.000 | 72.200.000 | −9.483.478 | +812.250 *(855.000)* | **−10,6%** | Ngân hàng |
| CTG | 2.300 | 34.477 | 30.800 | 70.840.000 | −8.456.607 | +983.250 *(1.035.000)* | **−9,4%** | Ngân hàng |
| PVT | 3.500 | 17.100 | 18.300 | 64.050.000 | **+4.200.000** | — | **+7,0%** | CAPIT |
| TCB | 2.000 | 33.900 | 28.950 | 57.900.000 | −9.900.000 | — | −14,6% | Ngân hàng |
| VPB | 2.300 | 27.914 | 24.800 | 57.040.000 | −7.162.857 | — | −11,2% | Ngân hàng |
| VNM | 900 | 58.600 | 60.900 | 54.810.000 | **+2.070.000** | — | +3,9% | CAPIT |
| MBB | 2.400 | 25.850 | 22.500 | 54.000.000 | −8.040.000 | +2.280.000 *(2.400.000)* | **−9,3%** | Ngân hàng |
| SAB | 1.100 | 47.368 | 43.550 | 47.905.000 | −4.200.000 | +3.135.000 *(3.300.000)* | **−2,0%** | CAPIT |
| LPB | 900 | 52.583 | 51.800 | 46.620.000 | −705.000 | — | −1,5% | Ngân hàng |
| NCT | 500 | 94.360 | 83.400 | 41.700.000 | −5.480.000 | +3.800.000 *(4.000.000)* | **−3,6%** | CAPIT |
| HDB | 1.500 | 26.675 | 25.200 | 37.800.000 | −2.212.500 | — | −5,5% | Ngân hàng |
| ACB | 1.500 | 22.650 | 21.900 | 32.850.000 | −1.125.000 | — | −3,3% | Ngân hàng |
| SHB | 1.500 | 13.550 | 11.500 | 17.250.000 | −3.075.000 | — | −15,1% | Ngân hàng |
| TPB | 800 | 16.800 | 14.100 | 11.280.000 | −2.160.000 | — | −16,1% | Ngân hàng |
| VIX | 700 | 17.000 | 13.000 | 9.100.000 | −2.800.000 | — | −23,5% | Chứng khoán |
| TV1 | 400 | 19.600 | 19.600 | 7.840.000 | 0 | — | 0,0% | Ngoài V2.4 |
| VND | 300 | 17.800 | 16.600 | 4.980.000 | −360.000 | — | −6,7% | Chứng khoán |
| SHS | 200 | 18.900 | 15.200 | 3.040.000 | −740.000 | — | −19,6% | Chứng khoán |
| **Tổng cổ phiếu** | | **986.725.443** | | **924.115.000** | **−62.610.443** | **+11.566.250** *(12.175.000)* | **−5,2%** | |
| Tiền mặt *(đã gồm cổ tức)* | | | | 14.326.923 | | | | |
| Phí phải trả | | | | −6.212 | | | | |
| **NAV** | | | | **938.435.711** | | | | |

Cộng dồn kiểm tra: 924.115.000 + 14.326.923 − 6.212 = **938.435.711** ✓ khớp **từng đồng** với chuỗi
NAV. Đây cũng là kết quả tính lại **độc lập** từ sổ vị thế broker × giá đóng cửa BigQuery — hai
nguồn hoàn toàn khác nhau cho ra cùng một con số.

**Phân bổ nhóm:** Ngân hàng 534,9tr (**57,0% NAV**) · CAPIT phòng thủ 290,2tr (**30,9%**) · Bất động
sản + KCN (VHM) 74,1tr (7,9%) · Chứng khoán 17,1tr (1,8%) · TV1 7,8tr (0,8%) · Tiền mặt 14,3tr
(1,5%). **Toàn bộ 21 mã dưới trần 10%/mã** (lớn nhất SIP 8,7%).

**Đọc bảng này cho đúng:** lãi/lỗ **do giá −62,6tr** cộng **cổ tức +12,2tr** = **−50,4tr (−5,1%)**
so với giá vốn, không phải so với NAV. Đa số danh mục được mua trong tháng 7 — ngay trước nhịp giảm
6,7% của thị trường. **Toàn bộ 4 vị thế đang lãi đều là mã CAPIT hoặc mua gần đây** (SIP, PVT, VNM);
các khoản lỗ lớn nhất tập trung ở nhóm ngân hàng mua đầu tháng.

**Vì sao tách "lãi/lỗ do giá" và "cổ tức" thành hai cột:** hai khoản này nằm ở hai chỗ khác nhau
trong tài khoản — phần giá nằm trong giá trị cổ phiếu, phần cổ tức đã chuyển thành **tiền mặt**
(hoặc khoản phải thu). Cộng lại mới ra tỉ suất thật của đồng vốn đã bỏ ra. Bản báo cáo cũ chỉ hiển
thị cột đầu, nên với NCT (cổ tức 8.000đ/cp trên giá vốn 94.360đ) sai lệch lên tới **8,5 điểm %**.

### 4.3 ⚠️ Tỷ trọng cổ phiếu 98,5% — tiền mặt đã cạn

Tiền mặt còn **14,3tr (1,5% NAV)**, trong đó **9,775tr là cổ tức đang chờ về**, tiền thực sự dùng
được chỉ **4,55tr**. Hệ quả thực tế:

- Nếu hệ thống phát tín hiệu mua mới trong 1–2 tuần tới, **gần như không còn tiền để thực hiện** —
  đúng như trường hợp SIP còn thiếu 33,2tr phải hoãn.
- Danh mục sẽ chịu **gần trọn** mức biến động của thị trường theo cả hai chiều.
- Rổ CAPIT (30,9% NAV) **được miễn trừ cắt lỗ và giữ cố định tới ~giữa tháng 10/2026** theo thiết kế
  — đây là cam kết đã định trước, không phải quên xử lý.

Đây là hồ sơ rủi ro **cao hơn rõ rệt** so với cấu hình ~70% cổ phiếu của các tuần đầu tháng. Trạng
thái này là hệ quả có chủ đích của việc CAPIT kích hoạt, nhưng nhà đầu tư cần biết rõ.

---

## 5. TÀI KHOẢN ZALOPAY

### 5.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ | Chênh | Ghi chú |
|---|---:|---:|---:|---:|---|
| 24/07 (đầu kỳ) | 849.855.112 | — | — | — | |
| 27/07 | **836.088.620*** | −1,62% | −1,01% | −0,61pp | Bán VPB 800 + mua VPB 700 (LAG) |
| 28/07 | 845.328.035 | +1,11% | +0,70% | +0,41pp | Mua CSV 1.000 (LAG) |
| 29/07 | 859.640.167 | +1,69% | +1,43% | +0,26pp | HOLD |
| 30/07 | 886.256.349 | **+3,10%** | +2,35% | +0,75pp | HOLD |
| 31/07 (cuối kỳ) | 888.828.498 | +0,29% | −0,51% | +0,80pp | HOLD |

\* **Số đã SỬA — bản ghi gốc ngày 27/07 bị SAI.** Chuỗi NAV lưu 804.077.200 cho ngày 27/07 vì API số
dư của công ty chứng khoán **trả về toàn số 0** ở thời điểm chụp buổi tối, và hệ thống đã chấp nhận
số 0 đó làm tiền mặt. Số đúng là **836.088.620**. Chi tiết + bằng chứng: Mục 7.1. Số sai này tạo ra
một cặp biến động giả **−5,39% rồi +5,13%** không hề xảy ra trên thực tế; báo cáo này dùng **số đã
sửa** ở mọi phép tính.

Cả tuần **+4,59%** vs chỉ số **+2,95%** — tốt hơn 1,64 điểm %, và **tăng nhiều hơn chỉ số ở 4/5
phiên**.

### 5.2 Phân tích — tách phần bot quản lý và phần ngoài phạm vi bot

| Cấu phần | 24/07 | 31/07 | Thay đổi | % |
|---|---:|---:|---:|---:|
| **DGC** (legacy, ngoài phạm vi bot) | 368.500.000 | 391.000.000 | **+22.500.000** | **+6,11%** |
| **Phần còn lại** (bot quản lý + tiền) | 481.355.112 | 497.828.498 | +16.473.386 | **+3,42%** |
| **Tổng NAV** | 849.855.112 | 888.828.498 | +38.973.386 | +4,59% |

Tuần này **cả hai cấu phần đều dương** — khác hẳn tuần trước khi DGC gánh 79,5% mức lỗ. DGC hồi
+6,11% sau khi mất −17,75% tuần trước, tức **mới lấy lại được khoảng 28% mức đã mất**. Phần bot quản
lý +3,42%, tốt hơn chỉ số 0,47 điểm %.

**DGC vẫn là rủi ro đơn lẻ lớn nhất** (44,0% NAV, ngoài tầm can thiệp của bot cho tới khi HOSE gỡ
hạn chế giao dịch, ước ~11–12/2026).

### 5.3 Danh mục cuối kỳ (31/07)

| Mã | KL | Giá 31/07 | Giá trị TT (VND) | % NAV | % active NAV | Nhóm |
|---|---:|---:|---:|---:|---:|---|
| DGC | 10.000 | 39.100 | 391.000.000 | **44,0%** | — | **Excluded — ngoài phạm vi bot** |
| VCB | 800 | 59.300 | 47.440.000 | 5,3% | 9,5% | Ngân hàng |
| VPB | 1.800 | 24.800 | 44.640.000 | 5,0% | 9,0% | Legacy 1.100cp + LAG 700cp |
| VHM | 300 | 148.100 | 44.430.000 | 5,0% | 8,9% | Bất động sản |
| PVT | 2.071 | 18.300 | 37.899.300 | 4,3% | 7,6% | CAPIT |
| VNM | 601 | 60.900 | 36.600.900 | 4,1% | 7,4% | CAPIT |
| SIP | 749 | 48.100 | 36.026.900 | 4,1% | 7,2% | CAPIT |
| BID | 900 | 38.000 | 34.200.000 | 3,8% | 6,9% | Ngân hàng |
| SAB | 744 | 43.550 | 32.401.200 | 3,6% | 6,5% | CAPIT |
| CTG | 1.050 | 30.800 | 32.340.000 | 3,6% | 6,5% | Ngân hàng |
| NCT | 373 | 83.400 | 31.108.200 | 3,5% | 6,2% | CAPIT |
| TCB | 956 | 28.950 | 27.676.200 | 3,1% | 5,6% | Ngân hàng |
| MBB | 1.102 | 22.500 | 24.795.000 | 2,8% | 5,0% | Ngân hàng |
| CSV | 1.000 | 21.200 | 21.200.000 | 2,4% | 4,3% | **LAG** (mới) |
| LPB | 352 | 51.800 | 18.233.600 | 2,1% | 3,7% | Ngân hàng |
| HDB | 659 | 25.200 | 16.606.800 | 1,9% | 3,3% | Ngân hàng |
| **Tổng cổ phiếu** | | | **876.598.100** | 98,6% | | |
| Tiền mặt | | | 12.237.594 | 1,4% | | |
| Phí phải trả | | | −7.196 | — | | |
| **NAV** | | | **888.828.498** | 100% | | Active NAV (loại DGC): **497.828.498** |

Cộng dồn kiểm tra: cổ phiếu 876.598.100 + tiền 12.237.594 − 7.196 = **888.828.498** ✓ khớp **từng
đồng**, đồng thời khớp với phép tính lại độc lập từ sổ vị thế broker × giá đóng cửa BigQuery.

**VPB đã về dưới trần chính sách:** 9,0% active NAV (từ đỉnh 38,8%) — chương trình giảm tập trung
**hoàn tất**. Lưu ý cách đọc: 1.100cp là phần legacy còn lại, 700cp là vị thế LAG mới hoàn toàn khác
mục đích.

**Lãi/lỗ phần bot mua** (14 mã có lịch sử khớp nội bộ, **không gồm DGC và toàn bộ VPB**) — 🔧 **đã
sửa 02/08 (bản sửa #2), cộng lại cổ tức RÒNG sau thuế**: giá vốn 454.848.300 → thị giá 440.958.100
(**−13.890.200** do giá) **+ cổ tức ròng 6.130.825** *(gộp 6.453.500 − thuế TNCN 5% là 322.675)*
= **−7.759.375 (−1,71%)**. *(Bản sửa #1 công bố −7.436.700 / −1,63% theo số gộp; bản gốc
−13.890.200 / −3,05% thiếu toàn bộ phần cổ tức.)*

Vị thế tốt nhất: **CSV +7,3%** · PVT +6,1% · VNM +3,7% · SIP +2,0% (bốn mã này **không có cổ tức**
trong kỳ nên thuế không ảnh hưởng). Vị thế yếu nhất **sau khi cộng cổ tức ròng**: TCB −8,4% ·
MBB −8,5% · LPB −5,5% (ba mã cũng không có cổ tức; MBB tại ZaloPay mua **sau** ngày chốt quyền 09/07
nên không được hưởng). Trước đây NCT và SAB đứng đầu danh sách lỗ — nay lần lượt còn **−3,6%** và
**−2,2%** *(bản sửa #1 ghi −3,2% và −1,9% theo cổ tức gộp; phần giảm đúng bằng thuế: NCT −400đ/cp,
SAB −150đ/cp)*. Ba mã cổ tức nhỏ còn lại dịch chuyển dưới 0,07pp: CTG −4,1% → **−4,2%**,
VCB −2,6% → **−2,7%**, BID giữ **−5,7%**. Lý do loại VPB khỏi con số này: hệ thống không tách được giá vốn
của 1.100cp legacy khỏi 700cp mua mới trong cùng một vị thế broker — xem Mục 8.

---

## 6. TỔNG HỢP 2 TUẦN (17/07 → 31/07) — để không đọc lệch bức tranh

| | SpaceX | ZaloPay | VN-Index |
|---|---:|---:|---:|
| Tuần 20–24/07 | −4,25% | −10,53% | −5,67% |
| Tuần 27–31/07 | +3,01% | +4,59% | +2,95% |
| **Gộp 2 tuần** | **−1,37%** | **−6,43%** | **−2,89%** |

> 🔧 **Ghi chú bản sửa 02/08:** con số **gộp 2 tuần không đổi** — cả hai đầu kỳ (17/07 và 31/07)
> đều không dính hiệu ứng đếm-trùng cổ tức nêu ở Mục 11.5; nó chỉ dịch lãi/lỗ **giữa** hai tuần
> (tuần 20–24 xấu hơn, tuần 27–31 tốt hơn), không đổi kết quả cả giai đoạn.

SpaceX **tốt hơn chỉ số 1,52 điểm %** trong cả giai đoạn biến động mạnh. ZaloPay **kém 3,54 điểm %**,
và chênh lệch đó **gần như toàn bộ là DGC**: qua 2 tuần DGC đi từ 448,0tr xuống 391,0tr = **−57,0tr
(−12,7%)**, trong khi phần bot quản lý chỉ đi từ 501,9tr xuống 497,8tr = **−0,80%** — tức **tốt hơn
chỉ số 2,09 điểm %**.

---

## 7. CÔNG BỐ SỰ CỐ & KHOẢNG TRỐNG SỐ LIỆU

**Không có sự cố nào chạm đến tiền thật hoặc làm sai lệch giao dịch trong tuần.** Toàn bộ 6 lệnh
thật (3 SpaceX + 3 ZaloPay) khớp đúng kế hoạch đã duyệt. Lệnh TV1 không khớp ngày 27/07 là do ràng
buộc giá do nhà đầu tư đặt ra, không phải lỗi.

### 7.1 🔴 LỖI SỐ LIỆU THẬT — NAV ZaloPay ngày 27/07 bị ghi sai, thiếu 32,0tr (đã phát hiện & sửa)

**Sự việc:** ngày 27/07, API số dư của DNSE cho ZaloPay trả về **toàn bộ bằng 0** ở hai lần đọc buổi
tối (19:04:59 và 19:10:20) — trong khi cùng ngày, hai lần đọc buổi sáng (09:25 và 09:50) trả về
27.380.812 hoàn toàn bình thường. Tác vụ chụp NAV cuối ngày **chấp nhận số 0 đó** làm tiền mặt và
ghi NAV = 804.077.200.

**Bằng chứng số 0 là sai, không phải tiền thật bằng 0:**
- Sáng hôm sau (28/07, 09:15) số dư đọc lại là **32.011.420** — không thể có chuyện tiền tự xuất
  hiện qua đêm khi tài khoản không nạp thêm.
- Kiểm tra ngược: 32.011.420 − (mua CSV 19.750.000 + phí) = 12.237.435, **đúng bằng** số dư cuối
  phiên 28/07 đã ghi nhận. Chuỗi tiền mặt khớp liền mạch nếu dùng 32.011.420.

**NAV đúng ngày 27/07 = 804.077.200 (cổ phiếu) + 32.011.420 (tiền) = 836.088.620.** Sai lệch của bản
ghi gốc: **−32.011.420 (−3,83%)**.

**Ảnh hưởng:** (a) **KHÔNG ảnh hưởng tiền thật, không ảnh hưởng lệnh nào** — chỉ là số ghi chép;
(b) tạo cặp biến động giả −5,39% / +5,13% trong chuỗi NAV, làm **thổi phồng độ biến động đo được**
của tài khoản (biến động năm hoá tính từ chuỗi sai: 37,7%; từ chuỗi đúng: **26,5%**) và **thổi phồng
mức sụt giảm tối đa** (từ −19,33% xuống **−16,12%**); (c) mọi số trong báo cáo này đã dùng bản đã sửa.

**Nguyên nhân gốc:** tác vụ chụp NAV **không kiểm tra tính hợp lý** của bản ghi số dư trước khi
dùng — một phản hồi rỗng/toàn-0 từ API bị coi như số thật. Đây đúng dạng lỗi mà quy tắc nội bộ về
kiểm tra nguồn dữ liệu đã cảnh báo: *tin vào một trường có giá trị "trông hợp lệ" thay vì xác minh
nó là số thật*.

**Việc cần làm — người phụ trách — hạn nghiệm thu:**
1. Sửa dòng 27/07 trong `nav_history_ZaloPay.csv` thành 836.088.620 (ghi rõ nguồn tái dựng) —
   *Winston (Data/Regime Ops)* — **hạn 08/08/2026**.
2. Thêm chốt chặn trong `daily_nav_snapshot.py`: **từ chối** bản ghi số dư có `totalCash = 0` **và**
   `availableCash = 0` **và** `cashDividendReceiving = 0` đồng thời (phản hồi rỗng), lùi về bản đọc
   hợp lệ gần nhất trong ngày và **báo cảnh báo**, thay vì ghi số 0 vào chuỗi NAV — *Winston* —
   **hạn 08/08/2026**.
3. Rà soát toàn bộ chuỗi NAV tháng 7 của **cả 2 tài khoản** tìm bản ghi tương tự (đã rà trong quá
   trình lập báo cáo này: **chỉ có 1 trường hợp duy nhất** là ZaloPay 27/07) — ✅ đã xong.

### 7.2 Hai dòng NAV thiếu của SpaceX (21/07, 22/07) — vẫn chưa bổ sung
Nêu tại báo cáo tuần 20–24/07 Mục 7.2. **Tính đến 01/08 vẫn chưa được bổ sung** vào file chuỗi NAV.
Cùng người phụ trách và hạn: *Winston* — **08/08/2026**. Gộp với việc 7.1 thành một lần sửa.

### 7.3 Báo cáo tuần nộp chậm — nguyên nhân quy trình
Xem báo cáo tuần 20–24/07 Mục 7.1. Việc khắc phục: *Mike* — **hạn 08/08/2026**.

### 7.4 Ghi nhận cải tiến (không phải lỗi): giao dịch bán-rồi-mua cùng mã trong một phiên
Trường hợp VPB ngày 27/07 (Mục 3.2). Chi phí thực tế ≈ 83.000đ. **Đề xuất:** bổ sung bước bù trừ nội
bộ giữa lệnh giảm-tập-trung và lệnh tín hiệu mới trên cùng một mã trước khi gửi ra thị trường —
*Taylor* — **không có hạn chốt, ưu tiên thấp** (giá trị tiết kiệm rất nhỏ, chỉ nên làm nếu không gây
rủi ro cho logic đặt lệnh).

---

## 8. ĐỐI SOÁT ĐẲNG THỨC HAI CHIỀU (31/07)

**SpaceX:**

| Vế trái (Vốn + Lãi/lỗ − Phí) | VND | | Vế phải (Tài sản − Nợ) | VND |
|---|---:|---|---|---:|
| Vốn ban đầu | 1.000.000.000 | | Cổ phiếu (MTM 31/07) | 924.115.000 |
| + Lãi/lỗ chưa thực hiện | −62.610.443 | | + Tiền mặt | 14.326.923 |
| − Phí giao dịch (0,075% × giá vốn thật) | −740.044 | | − Phí/nợ phải trả | −6.212 |
| − Phí/lãi đã post (API thật) | −6.720 | | | |
| **= Vế trái** | **936.642.793** | | **= Vế phải** | **938.435.711** |

**Chênh lệch −1.792.918 (−0,19% NAV) → ✅ ĐẠT ngưỡng dung sai** (±0,05% NAV + sàn 5tr). Cấu phần đã
nhận diện: (a) lãi/lỗ **đã thực hiện** chưa có trong công thức (đợt trim 06/07 + bán HPG 15/07,
≈ −1,8tr gồm thuế/phí); (b) **cổ tức tiền mặt đã nhận/đang chờ về 9.775.000đ** — nằm trong tiền mặt
ở vế phải nhưng chưa có ở vế trái; (c) khác biệt **quy ước giá vốn** giữa hệ thống (bình quân từ
lệnh khớp của bot) và broker (bình quân động, điều chỉnh sau mỗi lần bán một phần). Ba cấu phần này
bù trừ nhau. **Phần dư còn lại chưa khép kín tuyệt đối** và sẽ được đối soát với **sao kê chính thức
DNSE** — nêu nguyên trạng, không làm tròn.

**ZaloPay: đẳng thức hai chiều VẪN CHƯA lập được** (hạn chế đã biết từ khi tiếp nhận tài khoản).
Công cụ đối soát chạy ra chênh lệch **+532,6tr và kết luận "LỆCH VƯỢT NGƯỠNG" — con số này KHÔNG có
ý nghĩa và KHÔNG được dùng ở bất kỳ đâu trong báo cáo**, vì vế phải của công cụ chỉ tính 14 mã có
lịch sử khớp nội bộ (440.958.100đ), **bỏ qua DGC (390,5tr) và phần VPB legacy (45,0tr)** vốn không
có giá vốn đã xác minh. Vế phải **thật** vẫn được xác minh đầy đủ và khớp từng đồng (Mục 5.3). Cần
bổ sung khả năng hạch toán giá vốn vị thế legacy trước khi so sánh **tỷ suất sinh lời** của ZaloPay
với SpaceX — *Winston / Taylor* — **chưa có hạn chốt, không chặn vận hành**.

---

## 9. KẾ HOẠCH & VIỆC CẦN LÀM

| Việc | Người phụ trách | Hạn |
|---|---|---|
| Sửa NAV ZaloPay 27/07 + chốt chặn phản hồi API rỗng (Mục 7.1) | Winston | 08/08/2026 |
| Bổ sung 2 dòng NAV SpaceX 21–22/07 (Mục 7.2) | Winston | 08/08/2026 |
| Tách cảnh báo "báo cáo quá hạn" gửi đích danh (Mục 7.3) | Mike | 08/08/2026 |
| Giữ rổ CAPIT đủ 60 phiên — **không cắt lỗ, không bán sớm** | Hệ thống (tự động) | ~15/10/2026 |
| Theo dõi 2 vị thế LAG đầu tiên (VPB, CSV) — mùa BCTC Q2 | Hệ thống + Taylor | liên tục |
| Đối soát phí/thuế/lãi margin với sao kê chính thức DNSE | Taylor | báo cáo tháng 7 |
| Bù trừ nội bộ lệnh bán/mua cùng mã cùng phiên (Mục 7.4) | Taylor | ưu tiên thấp |

**Rủi ro cần theo dõi sát:**
1. **Tiền mặt cạn ở cả 2 tài khoản** (SpaceX 1,5% NAV, ZaloPay 1,4%). Tín hiệu mua mới sẽ **không
   thực hiện được** — đây là hạn chế thật, không phải hệ thống ngừng hoạt động. Nếu nhà đầu tư muốn
   hệ thống tiếp tục bắt tín hiệu LAG trong mùa BCTC, **cần cân nhắc nạp thêm vốn hoặc chấp nhận
   bỏ lỡ**; đây là **quyết định của nhà đầu tư**, không phải việc hệ thống tự xử lý.
2. **DGC (ZaloPay)** — 43,9% NAV, ngoài tầm can thiệp tới ~11–12/2026.
3. **Rổ CAPIT** — 290,2tr = 30,9% NAV SpaceX; 174,0tr = 19,6% NAV ZaloPay. Khoá 60 phiên tới ~giữa
   10/2026, không cắt lỗ.
4. **Mùa BCTC Q2/2026** — book LAG vừa "thức dậy". Cần theo dõi chất lượng tín hiệu trong 4–6 tuần
   tới, vì đây là lần đầu kênh này chạy trên tiền thật.

---

## 10. PHỤ LỤC — PHƯƠNG PHÁP & LƯU Ý

- **Pipeline xác minh bắt buộc:**
  1. `verify_account_snapshot.py` (chạy với `--account-no` tường minh) — **SpaceX Verified = True**
     (21 mã), **ZaloPay Verified = True** (14 mã bot), **0 lệch khối lượng** giữa log gốc API broker
     và journal khớp lệnh nội bộ.
  2. `daily_nav_snapshot.py` → `nav_history_{account}.csv` — **1 dòng sai đã phát hiện và sửa**
     (ZaloPay 27/07, Mục 7.1); 2 dòng thiếu tuần trước vẫn treo (Mục 7.2).
  3. `reconcile_equity.py` — SpaceX ✅ đạt (−0,19%); ZaloPay chưa lập được, output của công cụ **bị
     loại bỏ có chủ đích** (Mục 8).
  - **Đối chiếu độc lập:** giá trị cổ phiếu 31/07 tính lại từ sổ vị thế broker × giá đóng cửa
    BigQuery khớp **từng đồng** với chuỗi NAV ở **cả 2** tài khoản.
- **⚠️ Lưu ý cho người kiểm tra lại:** file journal khớp lệnh nội bộ ghi khối lượng **luỹ kế** cho
  mỗi lệnh con — cộng dồn thẳng các dòng FILL sẽ ra số **lớn hơn thực tế**. Số trong báo cáo lấy từ
  **báo cáo thực thi từng phiên + sổ vị thế broker** (hai nguồn đã đối chiếu khớp nhau).
- **Giá mark-to-market** = giá đóng cửa 31/07. Số liệu cùng ngày (định giá lệnh, sức mua) luôn lấy
  từ API DNSE trực tiếp.
- **Giá vốn vị thế legacy ZaloPay** (DGC, phần VPB cũ): dùng giá vốn broker DNSE báo — broker-native
  nhưng do broker tự tính, chưa đối soát với chứng từ gốc. **NAV không bị ảnh hưởng.**
- **Phí/thuế:** giao dịch 0,075%/lượt; thuế bán 0,1%. Lãi margin ~12,5%/năm là **số nhà đầu tư cung
  cấp, chưa xác minh với DNSE**. Các số phí/thuế là **ước tính từ biểu phí**, chưa đối soát sao kê.
- **Track record vẫn rất ngắn** (SpaceX 22 phiên, ZaloPay 18 phiên): mọi so sánh với VN-Index chỉ
  mang tính mô tả, **chưa đủ ý nghĩa thống kê**. Một tuần tăng hơn chỉ số không chứng minh điều gì.
- **Đây không phải khuyến nghị đầu tư.** Kết quả quá khứ (kể cả backtest) không đảm bảo kết quả
  tương lai.

---

## 11. 🔧 ĐIỀU CHỈNH CỔ TỨC — công bố phần đã sửa (bản phát hành lại 02/08/2026)

Mục này liệt kê **đầy đủ** những gì thay đổi so với bản phát hành ngày 01/08, kèm số cũ, số mới và
lý do. Không có chỗ nào bị sửa đè mà không ghi ở đây.

### 11.1 Chuyện gì đã xảy ra

Trong tháng 7, **6 mã trong danh mục trả cổ tức tiền mặt**. Ngày chốt quyền (ngày giao dịch không
hưởng quyền), giá cổ phiếu trên sàn **giảm đúng bằng mức cổ tức** — đó là cơ chế bình thường, không
phải mất tiền: phần giá trị đó chuyển từ cổ phiếu sang **tiền mặt** trong tài khoản.

Bản báo cáo cũ tính % lãi/lỗ theo công thức `(giá cuối kỳ − giá vốn) / giá vốn`, tức **chỉ nhìn phần
giá và bỏ quên phần tiền**. Hệ quả: mã nào trả cổ tức càng lớn thì bị **báo lỗ oan càng nhiều**.

### 11.2 Sáu mã bị ảnh hưởng — số cũ so với số mới

> 🔧 **Bản sửa #2 (02/08)** thêm hai cột cuối: cổ tức bị khấu trừ **thuế TNCN 5% tại nguồn**, nên
> cột **% RÒNG** mới là số nhà đầu tư thực nhận. Cột "% gộp" giữ lại để đối chiếu với bản sửa #1.

| Tài khoản | Mã | Ngày chốt quyền | Cổ tức | KL | Cổ tức gộp | % CŨ (sai) | % gộp (bản sửa #1) | Thuế 5% | **% RÒNG (đúng)** |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| SpaceX | **NCT** | 27/07 | 8.000đ/cp | 500 | 4.000.000 | −11,6% | −3,1% | −200.000 | **−3,6%** |
| SpaceX | **SAB** | 28/07 | 3.000đ/cp | 1.100 | 3.300.000 | −8,1% | −1,7% | −165.000 | **−2,0%** |
| SpaceX | **MBB** | 09/07 | 1.000đ/cp | 2.400 | 2.400.000 | −13,0% | −9,1% | −120.000 | **−9,3%** |
| SpaceX | **CTG** | 23/07 | 450đ/cp | 2.300 | 1.035.000 | −10,7% | −9,4% | −51.750 | **−9,4%** |
| SpaceX | **BID** | 17/07 | 450đ/cp | 1.900 | 855.000 | −11,6% | −10,6% | −42.750 | **−10,6%** |
| SpaceX | **VCB** | 23/07 | 450đ/cp | 1.300 | 585.000 | −4,8% | −4,1% | −29.250 | **−4,1%** |
| | | | | | **12.175.000** | **−6,3%** | **−5,1%** | **−608.750** | **−5,2%** |
| ZaloPay | **NCT** | 27/07 | 8.000đ/cp | 373 | 2.984.000 | −11,7% | −3,2% | −149.200 | **−3,6%** |
| ZaloPay | **SAB** | 28/07 | 3.000đ/cp | 744 | 2.232.000 | −8,2% | −1,9% | −111.600 | **−2,2%** |
| ZaloPay | **CTG** | 23/07 | 450đ/cp | 1.050 | 472.500 | −5,5% | −4,1% | −23.625 | **−4,2%** |
| ZaloPay | **BID** | 17/07 | 450đ/cp | 900 | 405.000 | −6,8% | −5,7% | −20.250 | **−5,7%** |
| ZaloPay | **VCB** | 23/07 | 450đ/cp | 800 | 360.000 | −3,4% | −2,6% | −18.000 | **−2,7%** |
| | | | | | **6.453.500** | **−3,05%** | **−1,63%** | **−322.675** | **−1,71%** |

**MBB của ZaloPay KHÔNG được điều chỉnh** — tài khoản này mua MBB *sau* ngày chốt quyền 09/07 nên
không được hưởng cổ tức. Đã kiểm chứng bằng số dư cổ tức phải thu của công ty chứng khoán (bằng 0
cho tới 15/07). Đây là lý do phải kiểm tra **từng tài khoản riêng**, không suy từ mã.

### 11.3 Những gì KHÔNG thay đổi (quan trọng với nhà đầu tư)

- **NAV cuối kỳ, giá trị danh mục, số dư tiền mặt: giữ nguyên, vẫn đúng.** Tiền cổ tức đã nằm sẵn
  trong số dư tài khoản (`totalCash` của DNSE bao gồm cả khoản cổ tức chờ về) — đã kiểm chứng số
  học trên bản ghi số dư gốc. Sai sót nằm ở **cách chia phần lãi/lỗ cho từng mã**, không ở tổng tài sản.
- **Mọi lệnh mua/bán, khối lượng, giá khớp: không đổi.**
- **So sánh với VN-Index ở Mục 1 và 2: không đổi** (trừ hiệu chỉnh nêu ở 11.5).

### 11.4 Hệ quả với phần phân rã (attribution) — có chỗ ĐỔI DẤU

Rổ CAPIT nhận **7,3tr trên tổng 12,2tr cổ tức của SpaceX** (NCT + SAB), vì đây là nhóm cổ phiếu
phòng thủ, cổ tức cao. Sau khi cộng lại:

| Nhóm (SpaceX, 31/07) | Lãi/lỗ do giá | Cổ tức gộp | Thuế 5% | Cổ tức ròng | **Tổng thật (ròng)** |
|---|---:|---:|---:|---:|---:|
| Ngân hàng (11 mã) | −56.220.442 | +4.875.000 | −243.750 | +4.631.250 | **−51.589.192** |
| Chứng khoán (VIX/VND/SHS) | −3.900.000 | — | — | — | −3.900.000 |
| **Rổ CAPIT** (SIP/PVT/VNM/SAB/NCT) | −1.640.000 | +7.300.000 | −365.000 | +6.935.000 | **+5.295.000 → LÃI** |
| Bất động sản (VHM) | −850.000 | — | — | — | −850.000 |
| **Tổng** | **−62.610.443** | **+12.175.000** | **−608.750** | **+11.566.250** | **−51.044.193** |

**Rổ CAPIT thực tế đang LÃI +5,30tr (sau thuế), không phải lỗ nhẹ như bản gốc mô tả.** Đây là thay
đổi **về dấu**, không chỉ về độ lớn — nhận định "CAPIT chỉ gánh 2,6% mức lỗ" ở bản gốc là **sai bản
chất**. Thuế 5% làm mỏng khoản lãi này (+5,66tr gộp → **+5,30tr ròng**) nhưng **không đảo lại dấu**:
kết luận rổ CAPIT có lãi trong tháng 7 vẫn đứng vững.

### 11.5 🔴 Sai sót thứ hai, vừa phát hiện khi rà soát — chuỗi NAV đếm hai lần cổ tức

**Độc lập với lỗi trên, và ảnh hưởng tới % thay đổi NAV theo tuần.**

Công ty chứng khoán ghi khoản **cổ tức phải thu** vào số dư ngay **tối ngày cuối cùng còn hưởng
quyền** — nhưng giá đóng cửa phiên đó **vẫn còn bao gồm quyền nhận cổ tức**. Tác vụ chụp NAV cuối
ngày lấy toàn bộ số dư tiền (đã gồm khoản phải thu) cộng với giá trị cổ phiếu theo giá đóng cửa hôm
đó → **cùng một khoản cổ tức bị đếm hai lần**, rồi tự triệt tiêu ở phiên kế tiếp khi giá rơi về
mức không hưởng quyền.

| Ngày | Tài khoản | NAV đã ghi | Đếm trùng | NAV trung tính |
|---|---|---:|---:|---:|
| 16/07 | SpaceX | 957.558.637 | 855.000 | 956.703.637 |
| 24/07 | SpaceX | 910.995.894 | **4.000.000** | 906.995.894 |
| 27/07 | SpaceX | 900.428.641 | **3.300.000** | 897.128.641 |
| 16/07 | ZaloPay | 953.593.885 | 405.000 | 953.188.885 |
| 24/07 | ZaloPay | 849.855.112 | **2.984.000** | 846.871.112 |

Vì **24/07 là ngày đầu kỳ của báo cáo tuần này**, NAV đầu kỳ bị ghi **cao hơn thực tế**, làm mức
tăng cả tuần bị **báo thấp đi**:

| Chỉ tiêu | Số đã công bố | Sau khi trung hoà | Chênh |
|---|---:|---:|---:|
| SpaceX tuần 27–31/07 | +3,01% | **+3,47%** | +0,46pp |
| ZaloPay tuần 27–31/07 | +4,59% | **+4,95%** | +0,36pp |
| *(tuần trước, 20–24/07 — sẽ sửa ở báo cáo tuần đó)* | −4,25% / −10,53% | −4,67% / −10,84% | −0,42 / −0,31pp |

**Cách đọc đúng:** con số "đã công bố" **không sai về tiền** — NAV cuối tháng và tiền mặt đều đúng;
đây là **hiệu ứng lệch thời điểm ghi nhận trong đúng một phiên**, tự triệt tiêu ngay phiên sau và
**bằng 0 khi tính cả tháng 7** (cả hai đầu kỳ 01/07 và 31/07 đều sạch). Báo cáo này giữ nguyên số
gốc trong các bảng để khớp với sổ đã ghi, và công bố số trung hoà ở đây để nhà đầu tư đối chiếu.

**Chưa sửa chuỗi NAV gốc** (`nav_history_*.csv`): đây là dữ liệu vận hành thật, việc ghi đè lịch sử
cần nhà đầu tư/người phụ trách quỹ đồng ý trước. Đề xuất xử lý ở 11.8.

### 11.6 🔴 Sai sót thứ ba (bản sửa #2, 02/08) — cổ tức phải trừ thuế TNCN 5%

**Bản sửa #1 sáng nay cộng cổ tức theo số GỘP.** Cổ tức tiền mặt trả cho **nhà đầu tư cá nhân** bị
khấu trừ **thuế thu nhập cá nhân 5% ngay tại nguồn** — công ty chứng khoán trừ trước khi tiền vào
tài khoản. Nhà đầu tư **không phải tự kê khai** và **không quyết toán lại** theo biểu lũy tiến: 5%
là mức khoán, xong nghĩa vụ.

Vậy con số thực nhận chỉ bằng **95%** mệnh giá công bố:

| Mã | Cổ tức công bố | Thực nhận sau thuế |
|---|---:|---:|
| NCT | 8.000đ/cp | **7.600đ/cp** |
| SAB | 3.000đ/cp | **2.850đ/cp** |
| MBB | 1.000đ/cp | **950đ/cp** |
| CTG · BID · VCB | 450đ/cp | **427,5đ/cp** |

**Đây không phải giả định — đã đo được bằng tiền thật.** Ngày **17/07/2026**, cổ tức MBB của SpaceX
là khoản **duy nhất trong tháng 7 đã thực sự chi trả** (5 khoản còn lại tới 02/08 vẫn là *phải thu*).
Số dư tài khoản hôm đó cho phép tách bạch từng đồng:

| | 16/07 | 17/07 | Chênh |
|---|---:|---:|---:|
| Cổ tức phải thu | 3.255.000 | 855.000 | **−2.400.000** *(= 2.400cp × 1.000đ, đúng mệnh giá ⇒ ghi GỘP)* |
| Tiền thật vào tài khoản | | | **+2.280.000** |
| **Chênh lệch = thuế** | | | **120.000 = đúng 5,0000%** |

*(Cùng ngày có một khoản rút tiền lớn 302.108.211đ — đã hoàn nguyên, và con số này được xác nhận
độc lập bởi hai nguồn có trước phép tính: bản chụp tài sản ngoài sổ ngày 17/07 và trường "tiền được
phép rút" ngày 16/07. Danh mục cổ phiếu hai ngày **không đổi một mã nào**, nên không có dòng tiền
nào khác gây nhiễu.)*

**Căn cứ pháp lý:** Thông tư 111/2013/TT-BTC — Điều 10 (thuế suất 5% với thu nhập từ đầu tư vốn) và
Điều 25 (khấu trừ tại nguồn, thời điểm khấu trừ là **lúc chi trả thật**, không phải lúc ghi nhận
phải thu). Luật Thuế TNCN mới **109/2025/QH15** (hiệu lực **01/07/2026**, tức áp dụng cho toàn bộ
6 sự kiện này) **giữ nguyên mức 5%** cho thu nhập từ đầu tư vốn — luật mới chỉ sửa biểu lũy tiến của
thu nhập từ lương. Cả hai tài khoản đều đứng tên **cá nhân**, đúng đối tượng chịu mức 5% này.

#### Ảnh hưởng tới NAV — khoản thuế sẽ bị trừ trong tương lai

Tại 31/07, phần cổ tức **chưa được chi trả** vẫn nằm trong số dư theo **số gộp**, nên NAV công bố
đang cao hơn thực tế một khoản đúng bằng thuế sẽ bị khấu trừ khi tiền về:

| Tài khoản | Cổ tức còn phải thu (gộp) | Thuế sẽ bị trừ | NAV đã công bố | NAV sau điều chỉnh | Tỉ lệ |
|---|---:|---:|---:|---:|---:|
| SpaceX | 9.775.000 | −488.750 | 938.435.711 | 937.946.961 | 0,052% |
| ZaloPay | 6.453.500 | −322.675 | 888.828.498 | 888.505.823 | 0,036% |

Khoản này **chắc chắn sẽ mất** (nghĩa vụ thuế theo luật), không phải rủi ro ước lượng — nên công bố
dù nhỏ. Các bảng NAV trong báo cáo giữ nguyên số gốc để khớp sổ đã ghi.

**Giới hạn cần nói rõ:** phép đo 5,00% dựa trên **một** sự kiện đã chi trả (MBB 17/07). Khi khoản
thứ hai về tiền, sẽ lặp lại đúng phép đo này để xác nhận. Mức 5% đồng thời khớp với luật định, nên
rủi ro còn lại là thấp — nhưng đây vẫn là n=1 và được ghi nhận như vậy.

### 11.7 Cách kiểm chứng lại (để bên thứ ba tái lập được)

Ba nguồn **hoàn toàn độc lập** cho cùng một kết quả:

1. **Cơ sở dữ liệu thị trường** — `tav2_bq.ticker` có cả giá thô (`Price`) và giá đã điều chỉnh
   (`Close`); tỉ số giữa hai cột nhảy về 1,0 đúng ngày chốt quyền, từ đó suy ra cổ tức/cp.
2. **Số dư của công ty chứng khoán** — trường "cổ tức phải thu" tăng đúng bằng *khối lượng × cổ tức*
   vào đúng ngày: SpaceX cộng dồn **9.775.000** (khớp từng đồng), ZaloPay **6.453.500** (khớp từng đồng).
3. **Giá vốn do công ty chứng khoán tự tính** — DNSE trừ đúng mức cổ tức khỏi giá vốn từng mã (ví dụ
   NCT 94.360 → 86.360). **Khớp 6/6 mã.**

Kiểm tra chéo mạnh nhất: dựng lại con số **454.848.300** (giá vốn 14 mã ZaloPay) và **−13.890.200
(−3,05%)** đã công bố, đi từ đường dữ liệu số 3 — ra **đúng từng đồng**, xác nhận cả phương pháp lẫn
mức cổ tức.

### 11.8 Việc cần làm để không tái diễn

| # | Việc | Trạng thái |
|---|---|---|
| 1 | Công cụ dùng chung `mike/bin/dividend_adjusted_return.py` — tự phát hiện ngày chốt quyền, tự đối soát với số dư công ty chứng khoán, **cảnh báo khi chưa xác minh được**; phân biệt cổ tức tiền mặt với chia tách cổ phiếu bằng biến động khối lượng | ✅ **đã làm** (tự kiểm 16/16 đạt; 11/11 vị thế thật xác minh khớp) |
| 2 | Ghi thành quy tắc bắt buộc trong tài liệu chuẩn nội bộ (`coding_guidelines.md` §21 + hồ sơ nguồn dữ liệu) để mọi báo cáo sau bắt buộc dùng | ✅ **đã làm** |
| 3 | Sửa tác vụ chụp NAV để không đếm hai lần cổ tức vào ngày chốt quyền, và quyết định có ghi lại 5 dòng NAV lịch sử hay không | ⏳ **chờ nhà đầu tư/người phụ trách quỹ duyệt** (chạm dữ liệu vận hành thật) |
| 4 | Rà soát các mã sẽ chốt quyền trong tháng 8 trước khi lập báo cáo kỳ tới | ⏳ đưa vào quy trình lập báo cáo |

---
*Báo cáo tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn (DNSE API) và cơ sở
dữ liệu thị trường (BigQuery). Người phụ trách quỹ rà soát trước khi phát hành cho nhà đầu tư.*
*Bản sửa 02/08/2026 — nội dung sửa công bố đầy đủ tại Mục 11.*
