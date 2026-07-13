# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: 06/07/2026 – 10/07/2026 (Tuần giao dịch đầy đủ đầu tiên sau go-live)

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ 01/07/2026 (có margin)
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ 06/07/2026 (cash-only, không margin)
**Chiến lược:** V2.4 (2 book BAL/LAG + parking custom30V tại trạng thái NEUTRAL)
**Ngày lập báo cáo:** 13/07/2026 · **Người lập:** Taylor (Quant) — số liệu đối soát qua pipeline xác minh chuẩn (xem Mục 7)
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

---

> **✅ Nguồn số liệu:** toàn bộ NAV/giá vốn/lãi-lỗ trong báo cáo này chạy qua pipeline xác minh bắt
> buộc: `verify_account_snapshot.py` (giá khớp thật broker-native, cross-check với journal nội bộ —
> cả 2 account **Verified = True**, 0 lệch số lượng), chuỗi NAV ngày từ `nav_history_{account}.csv`
> (đã đối soát API DNSE thật từng ngày), giá thị trường mark-to-market = giá đóng cửa 10/07 (BigQuery).
> Con số nào không trace được qua pipeline được ghi rõ là ước tính/thiếu — không tự suy đoán.

---

## 1. TÓM TẮT ĐIỀU HÀNH (Executive Summary)

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ | 988.629.520 (chốt 03/07) | 986.585.454 (chốt EOD đầu tiên 07/07)* |
| NAV cuối kỳ (10/07) | **971.690.659** | **978.346.744** |
| Thay đổi trong kỳ | **−16.938.861 (−1,71%)** | **−8.238.710 (−0,84%)*** |
| VN-Index cùng kỳ (03/07 → 10/07) | 1.862,08 → 1.828,34 (**−1,81%**) | — |
| Cổ phiếu cuối kỳ (giá đóng cửa 10/07) | 670.145.000 | 926.140.000 |
| Tiền mặt cuối kỳ | 301.545.659 | 52.206.744 |
| Nợ margin cuối kỳ | **0** (đã trả hết 09/07) | 0 (cash-only) |
| Tỷ trọng cổ phiếu/NAV | 69,0% (đúng mục tiêu ~70% NEUTRAL) | 94,7% (gồm DGC excluded 47,2%) |
| Số mã nắm giữ cuối kỳ | 15 | 6 |

\* ZaloPay go-live sáng 06/07; bản đọc API tại 07:42 ngày 06/07 (trước giờ mở cửa, định giá theo giá
đóng cửa 03/07) ghi nhận tổng NAV **1.011.470.378đ**. Chuỗi NAV cuối ngày đã xác minh chỉ bắt đầu từ
07/07 (ngày giao dịch đầu tiên của bot trên account này), nên "% thay đổi trong kỳ" của ZaloPay đo từ
EOD 07/07 → EOD 10/07. Khoảng chênh giữa baseline 07:42 và EOD 07/07 (−24,9tr) chủ yếu là biến động giá
thị trường 2 phiên 06–07/07 trên danh mục sẵn có (riêng DGC 10.000cp: giá 47.700 → 45.850 = −18,5tr).

**Nhận định tuần:** thị trường giảm khá mạnh (VN-Index −1,81%, đóng tuần ở đáy 1.828,34). Cả 2 account
giảm theo beta thị trường nhưng **giảm ít hơn chỉ số**: SpaceX −1,71% (đã về đúng cấu hình phòng thủ
NEUTRAL ~70% cổ phiếu sau trim 06/07), ZaloPay −0,84%. Trạng thái thị trường theo hệ thống DT5G giữ
nguyên **NEUTRAL (3/5)** suốt tuần, không có tín hiệu phòng thủ vĩ mô nào kích hoạt. Hai book tín hiệu
chủ động (BAL/LAG) tiếp tục rỗng — toàn bộ phần cổ phiếu là parking custom30V theo đúng thiết kế.

---

## 2. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

- **VN-Index:** 1.862,08 (03/07) → 1.828,34 (10/07), **−1,81%**; giảm mạnh nhất vào 06/07 (−1,00%) và
  2 phiên cuối tuần 09–10/07 (−0,70%/−0,67%).
- **Trạng thái thị trường (DT5G):** NEUTRAL (3/5) toàn bộ tuần — mục tiêu phân bổ 70% cho phần vốn
  parking. Không có cap phòng thủ vĩ mô (SBV ổn định, VIX/SPX bình thường).
- Không có sự kiện vĩ mô bất thường trong tuần ảnh hưởng đến khung phân bổ.

---

## 3. TÀI KHOẢN SPACEX — HOẠT ĐỘNG & DANH MỤC

### 3.1 Diễn biến NAV theo ngày (chuỗi đã xác minh, `nav_history_SpaceX.csv`)

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ ngày | Ghi chú |
|---|---:|---:|---:|---|
| 03/07 (đầu kỳ) | 988.629.520 | — | — | Nợ margin 409,86tr |
| 06/07 | 982.867.365 | −0,58% | −1,00% | **Trim 23 lệnh bán ~711tr** (xem 3.2) |
| 07/07 | 985.137.381 | +0,23% | +0,26% | Nợ margin còn 188,79tr (T+2 đợt 1 về) |
| 08/07 | 987.312.381 | +0,22% | +0,29% | HOLD |
| 09/07 | 979.764.020 | −0,76% | −0,70% | **Nợ margin về 0** (T+2 đợt 2 về) |
| 10/07 (cuối kỳ) | 971.690.659 | −0,82% | −0,67% | HOLD |

Cả tuần: **−1,71%** vs VN-Index **−1,81%** — bám sát thị trường, chênh lệch nhỏ chưa có ý nghĩa
thống kê (track record mới 8 phiên).

### 3.2 Hoạt động giao dịch

**Thứ Hai 06/07 — thực thi kế hoạch trim đã duyệt (khắc phục dứt điểm sự cố double-buy 02/07):**
- **23/23 lệnh bán khớp đủ 100%**, giá trị thực hiện **711 triệu VND** (kế hoạch 710tr) — nguồn:
  execution report chính thức `exec_SpaceX_2026-07-06_report.md`.
- Kết quả đúng thiết kế: tỷ trọng cổ phiếu từ ~141% NAV về **~70% NAV** (mức NEUTRAL parking đã được
  backtest xác nhận và user duyệt); dọn sạch 8 mã ngoài giỏ mục tiêu (LPB, MSB, VHC, HAH, VIB, VGC,
  DCM, MBS).
- **Nợ margin 409,86tr đã trả hết bằng tiền bán về theo chu kỳ T+2**: còn 188,79tr sau 07/07 và về
  **0 từ 09/07**. Từ 09/07 tài khoản không còn vay, tiền mặt 301,5tr (31% NAV).

**07/07 – 10/07 — HOLD (không có lệnh):** BAL/LAG rỗng, danh mục parking đã đúng target, không phát
sinh nhu cầu tái cân bằng. Đây là hành vi đúng của chiến lược, không phải hệ thống dừng hoạt động.

**Chi phí giao dịch trong tuần (ước tính, chưa đối soát sao kê DNSE):** phí 0,075%/lượt trên 711tr
≈ 0,53tr; thuế bán 0,1% trên giá trị bán ≈ 0,71tr; lãi margin tích lũy giai đoạn 03–09/07 trên dư nợ
giảm dần (409,86tr → 0) chưa được post đầy đủ vào tài khoản — sẽ đối chiếu khi có sao kê tháng.

### 3.3 Danh mục cuối kỳ (10/07, giá vốn THẬT đã xác minh × giá đóng cửa 10/07)

| Mã | KL | Giá vốn thật | Giá 10/07 | Giá trị TT (VND) | Lãi/lỗ chưa TH | % |
|---|---:|---:|---:|---:|---:|---:|
| VCB | 1.300 | 62.300 | 60.500 | 78.650.000 | −2.340.000 | −2,89% |
| BID | 1.900 | 42.991 | 41.000 | 77.900.000 | −3.783.478 | −4,63% |
| CTG | 2.300 | 34.477 | 33.700 | 77.510.000 | −1.786.607 | −2,25% |
| VHM | 500 | 149.800 | 147.000 | 73.500.000 | −1.400.000 | −1,87% |
| TCB | 2.000 | 33.900 | 32.400 | 64.800.000 | −3.000.000 | −4,42% |
| VPB | 2.300 | 27.914 | 26.700 | 61.410.000 | −2.792.857 | −4,35% |
| MBB | 2.400 | 25.850 | 24.650 | 59.160.000 | −2.880.000 | −4,64% |
| HPG | 2.200 | 23.500 | 22.950 | 50.490.000 | −1.210.000 | −2,34% |
| HDB | 1.500 | 26.675 | 27.000 | 40.500.000 | +487.500 | +1,22% |
| ACB | 1.500 | 22.650 | 22.550 | 33.825.000 | −150.000 | −0,44% |
| SHB | 1.500 | 13.550 | 13.150 | 19.725.000 | −600.000 | −2,95% |
| TPB | 800 | 16.800 | 15.950 | 12.760.000 | −680.000 | −5,06% |
| VIX | 700 | 17.000 | 15.450 | 10.815.000 | −1.085.000 | −9,12% |
| VND | 300 | 17.800 | 18.000 | 5.400.000 | +60.000 | +1,12% |
| SHS | 200 | 18.900 | 18.500 | 3.700.000 | −80.000 | −2,12% |
| **Tổng** | | **giá vốn 691.385.443** | | **670.145.000** | **−21.240.443** | **−3,07%** |

**Phân bổ ngành:** Ngân hàng 526,2tr (54,2% NAV) · Bất động sản 73,5tr (7,6%) · Thép 50,5tr (5,2%) ·
Chứng khoán 19,9tr (2,0%) · Tiền mặt 301,5tr (31,0%). **Toàn bộ 15 mã dưới trần tập trung 10%/mã**
(lớn nhất: VCB 8,1%) — danh mục đã tuân thủ đầy đủ chính sách rủi ro sau trim, khắc phục xong tình
trạng 4 mã vượt trần của tuần trước.

---

## 4. TÀI KHOẢN ZALOPAY — GO-LIVE & TUẦN CHUYỂN TIẾP

### 4.1 Bối cảnh go-live (06/07)

Account nhận quản lý với **7 vị thế có sẵn** (không do bot mua): DGC/MSH/TCM/TLG/VHC/VIB/VPB.
- **DGC (10.000cp, ~47% NAV) được loại trừ vĩnh viễn khỏi tái cân bằng** (`excluded_tickers`, chặn
  cứng ở tầng executor): đang bị HOSE hạn chế giao dịch, giữ vì luận điểm đầu tư riêng (target
  70–75k/12–18 tháng), không phải kẹt thanh khoản.
- Cơ sở phân bổ V2.4 là **active NAV (loại DGC)**, không phải tổng NAV.
- Kế hoạch chuyển tiếp 5 ngày (07/07 → 13/07, user duyệt, phương án A): bán dần MSH/TLG/TCM/VHC/VIB,
  mua dần giỏ custom30V thay thế. **Tuần báo cáo này gồm ngày 1–4; ngày 5 (13/07) nằm ngoài kỳ và đã
  hoàn tất sáng nay** (xem Mục 6).

### 4.2 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | Ghi chú |
|---|---:|---:|---|
| 06/07 07:42 | 1.011.470.378 | — | Baseline go-live (đọc API trước giờ mở cửa, giá 03/07) |
| 07/07 | 986.585.454 | —* | Ngày giao dịch 1: bán MSH, mua VCB |
| 08/07 | 996.802.048 | +1,04% | Ngày 2: bán TLG, mua VHM |
| 09/07 | 990.078.413 | −0,67% | Ngày 3: bán hết TCM (cả 10cp lô lẻ), mua VCB |
| 10/07 | 978.346.744 | −1,18% | Ngày 4: bán hết VHC 1.800cp, mua VHM+MBB; lệnh mua BID không khớp |

\* Không có bản ghi EOD 06/07 đã xác minh cho account này (bot bắt đầu giao dịch từ 07/07) — % ngày
đầu không tính được qua pipeline chuẩn nên không báo cáo.

Cả kỳ (EOD 07/07 → 10/07): **−0,84%**, trong bối cảnh VN-Index cùng đoạn giảm ~−1,08%; DGC (vị thế
lớn nhất, ngoài phạm vi bot) đi ngược thị trường, tăng nhẹ 45.850 → 46.200 (+0,76%) đỡ một phần NAV.

### 4.3 Giao dịch tuần chuyển tiếp (ngày 1–4) — tất cả khớp qua execution report chính thức

**Bán vị thế cũ** (lãi/lỗ thực hiện so với **giá vốn do broker DNSE báo** — vị thế hình thành trước
khi bot quản lý, hệ thống không có lịch sử khớp nội bộ):

| Ngày | Mã | KL bán | Giá KL bq | Tiền về (VND) | Giá vốn broker | Lãi/lỗ thực hiện |
|---|---|---:|---:|---:|---:|---:|
| 07/07 | MSH | 200 | 32.500 | 6.500.000 | 35.000 | −500.000 (−7,1%) |
| 08/07 | TLG | 200 | 49.000 | 9.800.000 | 49.950 | −190.000 (−1,9%) |
| 09/07 | TCM | 2.310 | 19.950 | 46.084.000 | 21.305 | −3.131.000 (−6,4%) |
| 10/07 | VHC | **1.800** | 57.694 | 103.850.000 | 60.189 | −4.490.000 (−4,1%) |
| | **Tổng** | | | **166.234.000** | | **≈ −8.311.000** |

*Ghi chú VHC:* execution report trong phiên ghi 1.200/1.800 (67%) vì 600cp cuối khớp ATC **sau** thời
điểm sinh report (14:45); sổ vị thế broker cuối ngày xác nhận **đã bán đủ 1.800cp**, giá đóng bình quân
57.694 (`closedQuantity=1800`). Số trong bảng là số broker xác nhận.

**Mua giỏ mới** (giá vốn thật đã xác minh qua `verify_account_snapshot.py`):

| Mã | KL lũy kế | Giá vốn thật | Giá 10/07 | Lãi/lỗ chưa TH |
|---|---:|---:|---:|---:|
| VCB | 800 | 61.362 | 60.500 | −690.000 (−1,41%) |
| VHM | 300 | 148.633 | 147.000 | −490.000 (−1,10%) |
| MBB | 1.000 | 24.700 | 24.650 | −50.000 (−0,20%) |
| **Tổng** | | **118.380.000** | **117.150.000** | **−1.230.000** |

Lệnh mua BID 900cp ngày 10/07 **không khớp** (0%) — đã được đưa lại vào plan ngày 5 (13/07) và khớp
sáng nay. Tổng giá trị giao dịch trong kỳ ≈ 284,6tr (bán 166,2tr + mua 118,4tr); phí ước tính 0,075%
≈ 0,21tr + thuế bán 0,1% ≈ 0,17tr (chưa đối soát sao kê).

### 4.4 Danh mục cuối kỳ (10/07, giá đóng cửa 10/07)

| Mã | KL | Giá trị TT (VND) | % tổng NAV | % active NAV | Ghi chú |
|---|---:|---:|---:|---:|---|
| DGC | 10.000 | 462.000.000 | 47,2% | — | **Excluded** — ngoài phạm vi bot |
| VPB | 7.500 | 200.250.000 | 20,5% | **38,8%** | Legacy, chờ tái cân bằng (quá trần 10%) |
| VIB | 9.200 | 146.740.000 | 15,0% | 28,4% | Legacy — đã bán hết ngày 13/07 (ngoài kỳ) |
| VCB | 800 | 48.400.000 | 4,9% | 9,4% | Bot mua |
| VHM | 300 | 44.100.000 | 4,5% | 8,5% | Bot mua |
| MBB | 1.000 | 24.650.000 | 2,5% | 4,8% | Bot mua |
| Tiền mặt | | 52.206.744 | 5,3% | | |
| **Tổng NAV** | | **978.346.744** | 100% | | Active NAV (loại DGC): **516.346.744** |

Cộng dồn kiểm tra: 926.140.000 (cổ phiếu) + 52.206.744 (tiền) = 978.346.744 — khớp từng đồng với
chuỗi NAV đã xác minh. **Lưu ý tập trung:** VPB 38,8% active NAV vượt xa trần 10%/mã — đây là tồn dư
legacy đã nhận diện, kế hoạch tái cân bằng riêng đang được lập (Mục 6); VIB đã xử lý xong ngày 13/07.

---

## 5. CÔNG BỐ SỰ CỐ VẬN HÀNH TRONG TUẦN — TÓM TẮT

Nguyên tắc: chỉ liệt kê sự cố ảnh hưởng thật đến NAV/giao dịch/số liệu công bố. Các lỗi điều phối
nội bộ giữa agent (không chạm tiền, không chạm số công bố) được xử lý riêng trong quy trình vận hành
nội bộ, không đưa vào đây.

1. **Trim SpaceX 06/07** — không phải sự cố mới, là **thực thi kế hoạch khắc phục đã duyệt** cho sự cố
   double-buy 02/07 (đã công bố ở báo cáo tuần trước). Hoàn tất 100%, margin về 0 ngày 09/07 đúng chu
   kỳ T+2. Sự cố gốc khép lại hoàn toàn, không phát sinh thiệt hại ngoài dự kiến.
2. **Xung đột file kế hoạch (06/07, trước giờ mở cửa):** bản kế hoạch v2 đã duyệt (23 lệnh, 70%) nằm ở
   tên file mà bot không đọc; nếu không phát hiện, bot sẽ chạy nhầm bản v1 cũ (11 lệnh, 94,7%). Bắt được
   **~15 phút trước giờ chạy**, promote đúng file, phiên chạy đúng kế hoạch đã duyệt. Đã sửa quy trình
   đặt tên file.
3. **Bot chưa hiểu quy tắc T+2 của DNSE (06/07, phiên sáng):** cổ phiếu mua 02/07 chỉ được bán từ
   **phiên chiều** 06/07 — bot lặp lệnh bị broker từ chối ~2.000 lần trong phiên sáng. Không thiệt hại
   (lệnh bị từ chối, không khớp sai); phần lớn lệnh trim khớp phiên chiều đúng kế hoạch. Đã vá executor
   đọc số dư khả dụng thật trước khi đặt.
4. **Hai lần NAV sai được đăng lên kênh báo cáo rồi đính chính trong ngày:**
   - 06/07: NAV SpaceX nhiễm số dư của account ZaloPay (log broker dùng chung chưa gắn nhãn account) —
     đính chính cùng tối, vá tận gốc tầng ghi log.
   - 07/07: NAV ZaloPay báo −98% (bỏ sót toàn bộ vị thế legacy không có lịch sử khớp nội bộ), đính
     chính lần 1 vẫn lệch 6,1tr (chụp số dư giữa 2 cú khớp lệnh) — user phát hiện cả 2 lần. Đã đổi
     nguồn NAV sang đọc thẳng sổ vị thế broker + thêm invariant chặn tính NAV khi số dư cũ hơn cú khớp
     cuối. **Số trong báo cáo này dùng chuỗi đã sửa và xác minh lại.**
5. **OTP race (08/07, 09:05):** 2 account khởi động cùng giây tranh nhau mã OTP — ZaloPay chết lúc
   khởi động, **tự hồi phục lúc 09:10** qua cơ chế giám sát, cả 2 lệnh trong ngày khớp đủ. Không ảnh
   hưởng kết quả.
6. **Lô lẻ TCM 10cp (09/07):** phần lô lẻ suýt bị bỏ quên vĩnh viễn do quy tắc làm tròn lô — phát hiện
   và bán ngay trong ngày (13:16). Đã vá logic cho các lần sau.
7. **Kế hoạch T+1 tính nhầm ngày (10/07, chiều):** kế hoạch cho "ngày mai" bị ghi thành thứ Bảy 11/07
   (không phải ngày giao dịch) thay vì thứ Hai 13/07. Phát hiện qua đối soát tự động tối 10/07, sửa lại
   trong đêm; **sáng 13/07 kế hoạch đúng đã được duyệt và chạy đúng giờ, không mất phiên nào**. Từ nay
   ngày T+1 do code tính và truyền sẵn, không để hệ thống lập kế hoạch tự suy luận lịch; đồng thời đã
   thêm 2 lớp bảo vệ mới (gửi lại duyệt tự động 23:00 nếu plan bị sửa muộn + chốt chặn trong bot: plan
   yêu cầu duyệt mà chưa duyệt thì bot từ chối chạy, hiệu lực từ 14/07).

---

## 6. KẾ HOẠCH TUẦN TỚI (13/07 – 17/07/2026)

- **ZaloPay — hoàn tất chuyển tiếp (ĐÃ XONG sáng 13/07, ngày 5/5):** bán hết VIB 9.200cp + mua BID
  900cp (bù lệnh không khớp ngày 4). Danh mục bot sau chuyển tiếp: BID/MBB/VCB/VHM + VPB (legacy) +
  DGC (excluded). Từ nay ZaloPay vận hành thường lệ như SpaceX.
- **ZaloPay — kế hoạch tái cân bằng VPB:** vị thế legacy VPB đang chiếm 38,8% active NAV (trần chính
  sách 10%/mã) — sẽ lập kế hoạch giảm dần riêng, trình user duyệt trước khi thực hiện.
- **SpaceX:** vận hành thường lệ; BAL/LAG vẫn rỗng ở NEUTRAL nên mặc định HOLD quanh mức parking ~70%
  trừ khi có tín hiệu mới.
- **Các chương trình paper-trading đang chạy** (không bật gì ở live khi chưa có sign-off): EXTREME-regime
  gate (dự kiến kết thúc ~28/07) · chase-cap vol-scale (~14/07, sắp đến hạn review) · fill-timing khung
  giờ (~cuối tháng 7) · DC-book idle-cash waterfall (review theo sự kiện).
- **Thay đổi mô hình sau kỳ báo cáo (cuối tuần 11–12/07, đã qua đầy đủ quy trình kiểm định + duyệt):**
  đóng 2 kênh tín hiệu momentum phụ (MOM_N/MOM_S) trong allocator sau chuỗi R&D chứng minh hiệu quả
  lịch sử của chúng chủ yếu do dồn mẫu giai đoạn 2020–21, không lặp lại được. Baseline chính thức mới
  của V2.4: CAGR 27,84% / Sharpe 1,84 / MaxDD −18,2% (backtest 50 tỷ, 2014→nay). **Không ép thoát vị
  thế nào đang mở** — chỉ ảnh hưởng entry mới. Đồng thời đã khép kín đợt rà soát sẵn sàng mùa BCTC
  Q2/2026 (mùa công bố bắt đầu ~cuối tháng 7).

**Lịch vận hành tiêu chuẩn không đổi** (T2–T6): kiểm tra dữ liệu (17:30) → lập kế hoạch T+1 (19:30,
thêm vòng gửi duyệt lại 23:00) → kiểm tra sẵn sàng (08:45) → phiên sáng (09:05) → phiên chiều (13:00)
→ báo cáo cuối ngày (15:00), giám sát tự động mỗi 5 phút trong giờ giao dịch.

---

## 7. PHỤ LỤC — PHƯƠNG PHÁP LUẬN & LƯU Ý

- **Pipeline xác minh bắt buộc** (không đổi so với báo cáo trước): (1) `verify_account_snapshot.py` —
  giá vốn/khối lượng thật từ log gốc API broker (`dnse_raw_*.jsonl`, field `averagePrice`/
  `fillQuantity` do DNSE trả về), cross-check với journal khớp lệnh nội bộ; tuần này cả SpaceX (15 mã,
  ngày khớp 01–02/07 + 06/07) và ZaloPay (3 mã bot mua, 07–10/07) đều **Verified = True, 0 lệch khối
  lượng**. (2) NAV ngày đọc từ `nav_history_{account}.csv` — chuỗi do `daily_nav_snapshot.py` ghi mỗi
  15:00 từ số dư/vị thế API thật (các dòng từng sai ngày 06–07/07 đã được sửa và xác minh lại — xem
  Mục 5.4). (3) Giá mark-to-market = giá đóng cửa 10/07 (BigQuery); đối chiếu độc lập: tổng cổ phiếu
  tính lại từ khối lượng × giá đóng cửa khớp từng đồng với `mtm_stock` trong chuỗi NAV ở cả 2 account.
- **Giá vốn vị thế legacy ZaloPay** (MSH/TLG/TCM/VHC/VIB/VPB/DGC): hệ thống không có lịch sử khớp nội
  bộ (mua trước khi bot quản lý) nên lãi/lỗ thực hiện trong Mục 4.3 dùng **giá vốn do broker DNSE báo**
  (`costPrice` trong sổ vị thế) — nguồn broker-native nhưng là số broker tự tính, chưa đối soát được
  với chứng từ gốc của các giao dịch cũ. Lãi/lỗ chưa thực hiện của DGC/VPB/VIB vì vậy không đưa vào
  P&L hợp nhất; NAV không bị ảnh hưởng (chỉ phụ thuộc khối lượng × giá thị trường).
- **Phí/thuế:** phí giao dịch 0,075%/lượt (đã xác nhận với biểu phí tài khoản); thuế bán 0,1% áp trên
  giá trị bán theo quy định. Các con số phí/thuế/lãi margin trong báo cáo là **ước tính từ biểu phí**,
  chưa đối soát sao kê chính thức DNSE — sẽ đối soát trong báo cáo tháng. Đẳng thức kiểm toán 2 chiều
  đầy đủ (như báo cáo tuần trước) tuần này **chưa lập lại được** vì cần hạch toán lãi/lỗ thực hiện của
  đợt trim + chuyển tiếp (script hiện tại mới xử lý lãi/lỗ chưa thực hiện) — ghi nhận là việc còn thiếu,
  không thay bằng số ước lượng.
- **Track record vẫn rất ngắn** (SpaceX 8 phiên, ZaloPay 4 phiên): mọi so sánh với VN-Index chỉ mang
  tính mô tả, chưa đủ ý nghĩa thống kê để đánh giá chiến lược.
- **Đây không phải khuyến nghị đầu tư.** Kết quả quá khứ (kể cả backtest) không đảm bảo kết quả tương lai.

---
*Báo cáo tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn (DNSE API) và cơ sở
dữ liệu thị trường (BigQuery). Người phụ trách quỹ rà soát trước khi phát hành cho nhà đầu tư.*
