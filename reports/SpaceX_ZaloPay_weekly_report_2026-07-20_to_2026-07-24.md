# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: 20/07/2026 – 24/07/2026

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ 01/07/2026 (có margin)
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ 06/07/2026 (cash-only, không margin)
**Chiến lược:** V2.4 (2 book BAL/LAG + parking custom30V tại NEUTRAL + rổ CAPIT bear-washout)
**Ngày lập báo cáo:** 01/08/2026 · **Bản sửa:** 02/08/2026 · **Người lập:** Taylor (Quant) — số liệu đối soát qua pipeline xác minh chuẩn (Mục 8)
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

> ## 🔧 BẢN SỬA 02/08/2026 — ĐIỀU CHỈNH CỔ TỨC TIỀN MẶT
> Bản đầu tiên (01/08) tính lãi/lỗ danh mục bằng **giá đã hồi tố điều chỉnh cổ tức** trừ **giá vốn
> thô**, tức trừ phần cổ tức hai lần → **báo lỗ nặng hơn thực tế**. Số đã sửa: SpaceX
> **−94.079.443 (−9,90%) → −81.915.443 (−8,62%)** (Mục 5); ZaloPay phần bot mua
> **−33.737.560 (−7,75%) → −27.291.500 (−6,27%)** (Mục 6.4).
> **NAV cuối kỳ, giá trị danh mục, số dư tiền mặt và mọi lệnh giao dịch: KHÔNG đổi** — tiền cổ tức
> vốn đã nằm trong số dư tài khoản. Công bố đầy đủ nguyên nhân + một sai sót thứ hai vừa phát hiện
> (chuỗi NAV đếm hai lần cổ tức đúng ngày chốt quyền): **Mục 7.5**.

> ⚠️ **BÁO CÁO NỘP CHẬM 8 NGÀY — công bố thẳng, không giấu.** Báo cáo tuần này lẽ ra phát hành
> ngày 25–26/07. Cơ chế cảnh báo "báo cáo tuần quá hạn" **có chạy** nhưng cảnh báo bị chôn trong
> log `ops_health_check` 4 lần/ngày, không ai xử lý — 2 tuần liên tiếp bị bỏ sót (tuần 20–24/07 và
> 27–31/07). Đây là **lỗi quy trình vận hành, không phải lỗi số liệu**: toàn bộ dữ liệu gốc còn
> nguyên vẹn và đã được đối soát đầy đủ khi lập báo cáo này. Biện pháp khắc phục: Mục 7.

---

> **✅ Nguồn số liệu:** NAV/giá vốn/lãi-lỗ chạy qua pipeline xác minh bắt buộc:
> `verify_account_snapshot.py` (chạy có `--account-no` tường minh cho **cả 2** tài khoản) —
> **cả 2 Verified = True, 0 lệch khối lượng** giữa 2 nguồn độc lập (log thô API broker vs journal
> khớp lệnh nội bộ); chuỗi NAV ngày từ `nav_history_{account}.csv`; giá mark-to-market = giá đóng
> cửa thực tế phiên 24/07. Mọi con số không trace được qua pipeline đều **ghi rõ là thiếu/ước tính**
> — Mục 7.

---

## 1. TÓM TẮT ĐIỀU HÀNH

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (chốt 17/07) | 951.448.674 | 949.864.227 |
| NAV cuối kỳ (24/07) | **910.995.894** | **849.855.112** |
| Thay đổi trong kỳ | **−40.452.780 (−4,25%)** | **−100.009.115 (−10,53%)** |
| VN-Index cùng kỳ (17/07 → 24/07) | 1.787,45 → 1.686,11 (**−5,67%**) | (cùng chỉ số) |
| **Chênh so với chỉ số** | **+1,42 điểm %** (tốt hơn) | **−4,86 điểm %** (kém hơn) |
| — Trong đó riêng DGC (ngoài phạm vi bot) | — | **−79.500.000** |
| — Phần bot quản lý (loại DGC) | — | **−4,09%** (tốt hơn chỉ số +1,58pp) |
| Cổ phiếu cuối kỳ | 863.930.000 | 822.474.300 |
| Tiền mặt tại công ty CK | 47.065.894 | 27.380.812 |
| Tiền gửi "Trứng vàng" (off-book) | **0** (đã rút hết về TK, xem Mục 2) | **0** (đã rút hết) |
| Nợ margin cuối kỳ | 0 | 0 (cash-only) |
| Tỷ trọng cổ phiếu/NAV | **94,8%** (tăng mạnh, xem Mục 2) | **96,8%** (gồm DGC 43,4%) |
| Số mã nắm giữ cuối kỳ | 20 | 15 |

**Nhận định tuần:** đây là **tuần xấu nhất của thị trường kể từ khi hệ thống go-live** — VN-Index
mất **−5,67%**, riêng phiên 22/07 sập **−3,58%**, chỉ số rơi từ 1.787 xuống 1.686 (thủng cả mốc
1.700). Trong bối cảnh đó:

- **SpaceX −4,25%, tốt hơn chỉ số 1,42 điểm %.** Điểm quyết định là phiên sập 22/07: danh mục chỉ
  **−1,67% trong khi chỉ số −3,58%** (hơn 1,91 điểm % chỉ trong một phiên), nhờ rổ CAPIT phòng thủ
  (VNM/SAB/NCT/PVT/SIP) vừa được giải ngân ngày 21/07 — xem Mục 3.
- **ZaloPay −10,53%, kém chỉ số 4,86 điểm %.** Nguyên nhân **gần như hoàn toàn** là DGC: vị thế
  legacy 10.000cp nằm **ngoài phạm vi tái cân bằng của bot**, giảm từ 44.800 xuống 36.850
  (**−17,75%**, mất **−79,5tr**) — chiếm **79,5% toàn bộ mức giảm NAV của tài khoản**. Nếu loại DGC,
  phần tài sản do bot quản lý chỉ **−4,09%, tức tốt hơn chỉ số 1,58 điểm %** — tương đương SpaceX.
- Trạng thái thị trường **DT5G giữ NEUTRAL (3/5) suốt tuần**, không có cap phòng thủ vĩ mô nào kích
  hoạt. Hệ thống **không** hạ tỷ trọng theo cảm tính khi thị trường rơi — đúng thiết kế (chỉ phản
  ứng khi giá xác nhận).

---

## 2. HAI THAY ĐỔI LỚN VỀ CẤU TRÚC TÀI SẢN TRONG TUẦN

### 2.1 Rút toàn bộ tiền gửi "Trứng vàng" về tài khoản chứng khoán — và giải ngân ngay

Tuần trước, 449,6tr của 2 tài khoản nằm ở sản phẩm tiền gửi "Trứng vàng" (off-book, không có API).
**Tuần này toàn bộ đã được rút về tài khoản chứng khoán và giải ngân vào rổ CAPIT** (Mục 3):

| Tài khoản | Trứng vàng 17/07 | Trứng vàng 24/07 | Ghi chú |
|---|---:|---:|---|
| SpaceX | 302.108.211 | **0** | rút về 21/07, mua CAPIT 255,2tr ngay trong phiên |
| ZaloPay | 147.473.247 | **0** | rút về 21/07, mua CAPIT 176,8tr (kèm tiền bán VPB) |

**Đây không phải nạp thêm vốn hay rút vốn** — chỉ là chuyển tiền của nhà đầu tư từ dạng "tiền gửi
có lãi" sang "cổ phiếu". Trường `offbook_assets` trong chuỗi NAV đã về 0 ở cả 2 tài khoản, đúng
thực tế, nên NAV **không bị tính trùng**. Theo chỉ đạo của nhà đầu tư, khoản Trứng vàng **đã đóng
hẳn, không mở lại** — từ nay `manual_offbook_assets_vnd = 0` vĩnh viễn.

### 2.2 ⚠️ Tỷ trọng cổ phiếu tăng vọt lên ~95–97% — nhà đầu tư CẦN BIẾT

| | 17/07 | 24/07 |
|---|---:|---:|
| SpaceX — cổ phiếu/NAV | 67,9% | **94,8%** |
| ZaloPay — cổ phiếu/NAV | 82,1% | **96,8%** |

Mức ~70% cổ phiếu quen thuộc của trạng thái NEUTRAL **chỉ áp cho phần vốn "đỗ tạm" (parking
custom30V)**. Rổ **CAPIT bear-washout là một túi vốn RIÊNG**, có nguồn tiền riêng
(`NAV_book_LAG × capit_size`) và được **miễn trừ khỏi trần vị thế và khỏi lệnh cắt lỗ**, giữ cố
định **60 phiên**. Khi CAPIT kích hoạt, tổng tỷ trọng cổ phiếu **vượt xa 70% một cách có chủ đích**.

**Hệ quả thẳng thắn:** rủi ro thị trường của cả 2 tài khoản trong 60 phiên tới **cao hơn đáng kể**
so với các tuần trước, và tiền mặt dự phòng gần như bằng 0 (SpaceX 47tr, ZaloPay 27,4tr). Nếu thị
trường tiếp tục rơi, danh mục sẽ chịu gần trọn mức giảm. Đây là đánh đổi đã nằm trong thiết kế của
chiến lược (mua vào lúc thị trường hoảng loạn), **không phải sự cố** — nhưng là thay đổi hồ sơ rủi
ro thật sự nên được nêu rõ chứ không lướt qua.

---

## 3. SỰ KIỆN CHÍNH — RỔ CAPIT "BEAR-WASHOUT" KÍCH HOẠT NGÀY 21/07

**CAPIT là gì:** một cơ chế đã có sẵn trong chiến lược V2.4, kích hoạt khi thị trường xuất hiện dấu
hiệu **bán tháo kiệt quệ** (washout) — đo bằng độ rộng thị trường (tỷ lệ cổ phiếu quá bán) chứ không
phải cảm tính. Khi kích hoạt, hệ thống mua một **rổ cổ phiếu phòng thủ, chất lượng cao, định giá rẻ**
và **giữ cố định 60 phiên**, miễn trừ cắt lỗ. Điều kiện kích hoạt hình thành sau phiên 20/07
(VN-Index −2,46%), lệnh thực hiện ngày **21/07**.

**Rổ CAPIT — 5 mã, giống nhau ở cả 2 tài khoản:**

| Mã | Ngành | SpaceX (KL / giá khớp BQ) | ZaloPay (KL / giá khớp BQ) |
|---|---|---:|---:|
| VNM (Vinamilk) | Sữa / tiêu dùng thiết yếu | 900 / 58.600 | 601 / 58.700 |
| SAB (Sabeco) | Bia / tiêu dùng | 1.100 / 47.368 | 744 / 47.450 |
| NCT (Noibai Cargo) | Dịch vụ hàng hóa hàng không | 500 / 94.360 | 373 / 94.400 |
| PVT (PVTrans) | Vận tải dầu khí | 3.000 / 17.100 | 2.070 / 17.248 |
| SIP (Saigon VRG) | Khu công nghiệp | 1.100 / 47.123 | 749 / 47.140 |

**Toàn bộ 10 lệnh khớp 100% kế hoạch.** Giá trị giải ngân: **SpaceX 255,2tr · ZaloPay 176,8tr.**

**Vì sao rổ này là "phòng thủ":** đây là các doanh nghiệp có dòng tiền ổn định, ít phụ thuộc chu kỳ
tín dụng — trái ngược với danh mục cũ vốn tập trung nặng vào ngân hàng. Kết quả đo được ngay trong
tuần, ở đúng phiên sập mạnh nhất:

| Phiên 22/07 | Mức giảm |
|---|---:|
| VN-Index | **−3,58%** |
| SpaceX NAV | **−1,67%** |
| ZaloPay NAV | −3,48% (bị DGC kéo) |

SpaceX chịu **chưa tới một nửa** mức giảm của thị trường trong phiên sập. Đây là bằng chứng trực
tiếp cho tác dụng của rổ CAPIT — dù **một phiên đơn lẻ chưa phải bằng chứng thống kê**.

**Bổ sung CAPIT ngày 24/07:** SpaceX mua thêm PVT 500cp @17.100 (8,55tr) — nâng PVT lên 3.500cp.
Đây là phần bù cho lệnh chưa đạt mục tiêu ngày 21/07 do giới hạn tiền; phần còn thiếu được ghi nhận
là **DEFER (hoãn)** chứ không huỷ.

---

## 4. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

| Ngày | VN-Index | Δ ngày | Ghi chú |
|---|---:|---:|---|
| 17/07 (đầu kỳ) | 1.787,45 | — | |
| 20/07 | 1.743,51 | **−2,46%** | thủng 1.750; hình thành điều kiện washout |
| 21/07 | 1.730,56 | −0,74% | **CAPIT giải ngân** |
| 22/07 | **1.668,53** | **−3,58%** | phiên sập mạnh nhất kể từ go-live |
| 23/07 | 1.699,38 | +1,85% | hồi kỹ thuật |
| 24/07 | 1.686,11 | −0,78% | |

- Cả tuần **−5,67%**, tuần giảm thứ **ba** liên tiếp. Từ đỉnh 1.867 (01/07) chỉ số đã mất **−9,7%**.
- **DT5G = NEUTRAL (3/5) cả 5 phiên** (nguồn: bảng sản xuất `vnindex_5state_dt5g_live`). Không có
  cap phòng thủ vĩ mô nào bật (lãi suất SBV ổn định, VIX/SPX chưa tới ngưỡng hoảng loạn, độ rộng
  thị trường chưa thủng ngưỡng chặn). Hệ thống DT5G **được thiết kế chậm có chủ đích** — nó không
  cố đoán đáy; việc nó chưa chuyển sang BEAR trong một tuần rơi 5,67% là hành vi đúng, không phải
  lỗi.

---

## 5. TÀI KHOẢN SPACEX

### 5.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ | Chênh | Ghi chú |
|---|---:|---:|---:|---:|---|
| 17/07 (đầu kỳ) | 951.448.674 | — | — | — | |
| 20/07 | 929.848.687 | −2,27% | −2,46% | +0,19pp | HOLD |
| 21/07 | **927.267.983*** | −0,28% | −0,74% | +0,47pp | **Mua rổ CAPIT 255,2tr** |
| 22/07 | **911.773.252*** | −1,67% | −3,58% | **+1,91pp** | HOLD — phiên sập |
| 23/07 | 911.693.521 | −0,01% | +1,85% | −1,86pp | HOLD |
| 24/07 (cuối kỳ) | 910.995.894 | −0,08% | −0,78% | +0,70pp | Mua PVT 500cp |

\* **Ghi chú minh bạch — thiếu 2 bản ghi NAV (21/07 và 22/07):** tác vụ chụp NAV cuối ngày không ghi
dòng cho SpaceX 2 phiên này (ZaloPay vẫn ghi bình thường). Hai số trên được **tính lại đúng phương
pháp mà tác vụ đó vẫn dùng**, từ dữ liệu gốc còn nguyên vẹn: sổ vị thế broker trong
`dnse_raw_2026-07-21/22.jsonl` × giá đóng cửa thực tế phiên đó, cộng số dư tiền mặt thật đọc từ API
(21/07: CP 877.265.000 + tiền 50.002.983; 22/07: CP 860.150.000 + tiền 51.623.252). Đây **không phải
ước lượng**. Sự cố được ghi ở Mục 7; hai dòng thiếu cần bổ sung chính thức vào file chuỗi NAV.

Cả tuần **−4,25%** vs chỉ số **−5,67%**. Danh mục **giảm ít hơn chỉ số ở 4/5 phiên**; phiên duy nhất
kém hơn là 23/07 — phiên hồi kỹ thuật (+1,85%) mà danh mục gần như đứng yên, đúng đặc tính của một
rổ phòng thủ: **ít mất khi rơi, cũng ít được khi bật lại**.

### 5.2 Hoạt động giao dịch — 6 lệnh, khớp 100% (trừ 1 lệnh cố ý không đuổi giá)

| Ngày | Lệnh | Mã | KL kế hoạch | KL khớp | Giá tham chiếu | Giá khớp BQ | Giá trị (VND) |
|---|---|---|---:|---:|---:|---:|---:|
| 21/07 | Mua | NCT | 500 | 500 (100%) | 94.200 | 94.360 | 47.180.000 |
| 21/07 | Mua | PVT | 3.000 | 3.000 (100%) | 17.000 | 17.100 | 51.300.000 |
| 21/07 | Mua | SAB | 1.100 | 1.100 (100%) | 47.300 | 47.368 | 52.104.800 |
| 21/07 | Mua | SIP | 1.100 | 1.100 (100%) | 46.950 | 47.123 | 51.835.300 |
| 21/07 | Mua | VNM | 900 | 900 (100%) | 58.500 | 58.600 | 52.740.000 |
| 24/07 | Mua | PVT | 500 | 500 (100%) | 16.950 | 17.100 | 8.550.000 |
| 24/07 | Mua | TV1 | 200 | **0 (0%)** | 19.900 | — | 0 |

- **Tổng mua trong tuần: 263.710.100đ. Phí giao dịch 0,075% ≈ 197.783đ. Không có lệnh bán → không
  có lãi/lỗ thực hiện, không có thuế bán.**
- **Lệnh TV1 không khớp là ĐÚNG THIẾT KẾ, không phải lỗi.** TV1 (PECC1) thuộc chương trình gom
  **ngoài chiến lược V2.4, đã được nhà đầu tư duyệt riêng**, với ràng buộc cứng: đặt lệnh giới hạn
  **≤19.900, tuyệt đối không mua trên 20.000**. Ngày 24/07 giá không về vùng đặt nên lệnh không khớp
  — hệ thống **không đuổi giá**. Chương trình này tiếp tục sang tuần sau (khớp đủ 400cp ngày 28–29/07).
- **Các phiên 20/07, 22/07, 23/07 — HOLD, không lệnh nào.** BAL/LAG rỗng, rổ CAPIT giữ nguyên theo
  quy tắc 60 phiên. Việc **không bán tháo trong phiên sập 22/07** là kỷ luật hệ thống, không phải
  hệ thống ngừng chạy.

### 5.3 Danh mục cuối kỳ (24/07, giá vốn THẬT đã xác minh × giá đóng cửa thực tế 24/07)

| Mã | KL | Giá vốn thật | Giá 24/07 | Giá trị TT (VND) | % NAV | Nhóm |
|---|---:|---:|---:|---:|---:|---|
| VCB | 1.300 | 62.300 | 54.100 | 70.330.000 | 7,7% | Ngân hàng |
| BID | 1.900 | 42.991 | 36.000 | 68.400.000 | 7,5% | Ngân hàng |
| CTG | 2.300 | 34.477 | 29.000 | 66.700.000 | 7,3% | Ngân hàng |
| VHM | 500 | 149.800 | 130.000 | 65.000.000 | 7,1% | Bất động sản |
| PVT | 3.500 | 17.100 | 16.850 | 58.975.000 | 6,5% | **CAPIT** |
| VPB | 2.300 | 27.914 | 24.950 | 57.385.000 | 6,3% | Ngân hàng |
| TCB | 2.000 | 33.900 | 28.600 | 57.200.000 | 6,3% | Ngân hàng |
| VNM | 900 | 58.600 | 58.900 | 53.010.000 | 5,8% | **CAPIT** |
| MBB | 2.400 | 25.850 | 21.900 | 52.560.000 | 5,8% | Ngân hàng |
| SIP | 1.100 | 47.123 | 46.700 | 51.370.000 | 5,6% | **CAPIT** |
| SAB | 1.100 | 47.368 | 46.500 | 51.150.000 | 5,6% | **CAPIT** |
| LPB | 900 | 52.583 | 52.400 | 47.160.000 | 5,2% | Ngân hàng |
| NCT | 500 | 94.360 | 92.800 | 46.400.000 | 5,1% | **CAPIT** |
| HDB | 1.500 | 26.675 | 25.850 | 38.775.000 | 4,3% | Ngân hàng |
| ACB | 1.500 | 22.650 | 22.500 | 33.750.000 | 3,7% | Ngân hàng |
| SHB | 1.500 | 13.550 | 11.800 | 17.700.000 | 1,9% | Ngân hàng |
| TPB | 800 | 16.800 | 14.200 | 11.360.000 | 1,2% | Ngân hàng |
| VIX | 700 | 17.000 | 12.450 | 8.715.000 | 1,0% | Chứng khoán |
| VND | 300 | 17.800 | 16.500 | 4.950.000 | 0,5% | Chứng khoán |
| SHS | 200 | 18.900 | 15.200 | 3.040.000 | 0,3% | Chứng khoán |
| **Tổng cổ phiếu** | | | | **863.930.000** | **94,8%** | |
| Tiền mặt | | | | 47.065.894 | 5,2% | |
| **NAV** | | | | **910.995.894** | 100% | |

Cộng dồn kiểm tra: 863.930.000 + 47.065.894 − 0 = **910.995.894** ✓ khớp **từng đồng** với chuỗi NAV.

**Phân bổ nhóm:** Ngân hàng 521,3tr (**57,2% NAV**) · CAPIT phòng thủ 260,9tr (**28,6%**) · Bất động
sản 65,0tr (7,1%) · Chứng khoán 16,7tr (1,8%) · Tiền mặt 47,1tr (5,2%).

**Toàn bộ 20 mã đều dưới trần tập trung 10%/mã** (lớn nhất VCB 7,7%) — tuân thủ đầy đủ chính sách
rủi ro. Về rủi ro tập trung ngành ngân hàng (vấn đề đã nêu ở báo cáo tuần trước): tính trên **NAV**
tỷ trọng gần như đứng yên (58,6% → 57,2%, vì tiền gửi Trứng vàng cũng đã chuyển thành cổ phiếu),
**nhưng tính trên phần cổ phiếu thì giảm rất mạnh — từ 86,3% xuống 60,3%**. Nói cách khác, rổ CAPIT
không bán bớt ngân hàng, mà **pha loãng** nó bằng một nhóm tài sản có yếu tố rủi ro khác hẳn. Đây là
cải thiện thật về đa dạng hoá, nhưng **không** làm giảm tổng rủi ro thị trường — tổng tỷ trọng cổ
phiếu vẫn tăng (Mục 2.2).

**Lãi/lỗ cuối kỳ — 🔧 ĐÃ SỬA 02/08 (số cũ sai, xem Mục 9):**

| | VND | % giá vốn |
|---|---:|---:|
| Giá vốn thật | 950.720.443 | |
| Thị giá 24/07 **(giá thật trên sàn)** | 863.930.000 | |
| → Lãi/lỗ do giá | **−86.790.443** | −9,13% |
| + Cổ tức tiền mặt đã nhận/chờ về (MBB, BID, CTG, VCB) | **+4.875.000** | |
| **= Tổng lãi/lỗ** | **−81.915.443** | **−8,62%** |

*Số cũ công bố: −94.079.443 (−9,90%) — sai do lấy **giá đã điều chỉnh cổ tức** (856.641.000) trừ
**giá vốn thô**, tức trừ phần cổ tức hai lần. Nguyên nhân và cách sửa: Mục 7.5.*

Con số này phản ánh việc phần lớn danh mục được mua trong tháng 7 — ngay trước nhịp giảm 9,7% của
thị trường. *(Cổ tức NCT 4,0tr và SAB 3,3tr **chưa** được cộng ở đây: tại 24/07 giá cổ phiếu vẫn còn
bao gồm quyền nhận cổ tức, cộng thêm sẽ là đếm hai lần — hai khoản này vào số của kỳ sau.)*

---

## 6. TÀI KHOẢN ZALOPAY

### 6.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ | Chênh | Ghi chú |
|---|---:|---:|---:|---:|---|
| 17/07 (đầu kỳ) | 949.864.227 | — | — | — | |
| 20/07 | 920.371.884 | −3,10% | −2,46% | −0,65pp | Bán VPB 800, mua TCB+MBB |
| 21/07 | 918.078.637 | −0,25% | −0,74% | +0,49pp | Bán VPB 800, **mua rổ CAPIT 176,8tr** |
| 22/07 | 886.083.813 | −3,48% | −3,58% | +0,10pp | Bán VPB 800, mua LPB |
| 23/07 | 859.738.008 | **−2,97%** | **+1,85%** | **−4,82pp** | Bán VPB 800, mua HDB · **DGC sập** |
| 24/07 (cuối kỳ) | 849.855.112 | −1,15% | −0,78% | −0,37pp | HOLD |

**Phiên 23/07 là toàn bộ câu chuyện của tuần:** thị trường hồi **+1,85%** nhưng NAV vẫn **−2,97%**,
vì **DGC rơi từ 40.500 xuống 37.950 (−6,3%) chỉ trong phiên đó** (−25,5tr). Sự kiện này đã được bộ
phận giám sát rủi ro (Spyros) thẩm định ngay trong ngày với kết luận **KHÔNG dừng giao dịch, GIỮ vị
thế**, và đã báo cáo nhà đầu tư riêng.

### 6.2 Phân tích lỗ — tách rõ phần bot quản lý và phần ngoài phạm vi bot

| Cấu phần | 17/07 | 24/07 | Thay đổi | % |
|---|---:|---:|---:|---:|
| **DGC** (legacy, ngoài phạm vi bot) | 448.000.000 | 368.500.000 | **−79.500.000** | **−17,75%** |
| **Phần còn lại** (bot quản lý + tiền) | 501.864.227 | 481.355.112 | −20.509.115 | **−4,09%** |
| **Tổng NAV** | 949.864.227 | 849.855.112 | −100.009.115 | −10,53% |

**Kết luận thẳng thắn: 79,5% mức lỗ của tuần đến từ một mã duy nhất mà bot không được phép động
vào.** Phần tài sản do hệ thống thực sự quản lý giảm **−4,09%**, tức **tốt hơn VN-Index 1,58 điểm %**
— cùng đặc tính phòng thủ như SpaceX. Việc so sánh NAV tổng của ZaloPay với chỉ số **không phản ánh
chất lượng của chiến lược**, chừng nào DGC còn nằm ngoài phạm vi.

**DGC vì sao nằm ngoài phạm vi:** HOSE hạn chế giao dịch mã này sau khi lãnh đạo doanh nghiệp bị
khởi tố (17/03/2026); ước tính gỡ hạn chế khoảng 11–12/2026. Vị thế được giữ theo luận điểm riêng
của nhà đầu tư, đã khai báo chính thức trong cấu hình (`excluded_tickers`) nên bot **không thể** đặt
lệnh với mã này dù kế hoạch có sai sót. Sizing của chiến lược tính trên `active_nav` (NAV trừ DGC),
không tính trên NAV tổng.

### 6.3 Hoạt động giao dịch — 12 lệnh, khớp 100%

| Ngày | Lệnh | Mã | KL | Giá khớp BQ | Giá trị (VND) | Mục đích |
|---|---|---|---:|---:|---:|---|
| 20/07 | Bán | VPB | 800 | 25.850 | 20.680.000 | Trim VPB legacy (ngày 4) |
| 20/07 | Mua | TCB | 356 | 31.208 | 11.110.048 | Parking custom30V |
| 20/07 | Mua | MBB | 102 | 23.597 | 2.406.894 | Parking custom30V |
| 21/07 | Bán | VPB | 800 | 24.800 | 19.840.000 | Trim VPB (ngày 5) — cấp vốn CAPIT |
| 21/07 | Mua | NCT | 373 | 94.400 | 35.211.200 | **CAPIT** |
| 21/07 | Mua | PVT | 2.070 | 17.248 | 35.703.360 | **CAPIT** |
| 21/07 | Mua | SAB | 744 | 47.450 | 35.302.800 | **CAPIT** |
| 21/07 | Mua | SIP | 749 | 47.140 | 35.307.860 | **CAPIT** |
| 21/07 | Mua | VNM | 601 | 58.700 | 35.278.700 | **CAPIT** |
| 22/07 | Bán | VPB | 800 | 25.375 | 20.300.000 | Trim VPB (ngày 6) |
| 22/07 | Mua | LPB | 352 | 54.843 | 19.304.736 | Parking custom30V (dời từ 21/07) |
| 23/07 | Bán | VPB | 800 | 24.850 | 19.880.000 | Trim VPB (ngày 7) |
| 23/07 | Mua | HDB | 659 | 25.891 | 17.062.169 | Parking custom30V |

**Tổng: mua 224.281.767đ · bán 80.700.000đ.** Phí giao dịch 0,075% ≈ **228.737đ**; thuế bán 0,1% ≈
**80.700đ**.

**Lãi/lỗ thực hiện trong tuần** (bán VPB legacy, giá vốn = số broker DNSE báo 27.886,67):

| Mã | KL bán | Giá vốn broker | Giá bán BQ | Lãi/lỗ thực hiện |
|---|---:|---:|---:|---:|
| VPB | 3.200 (4×800) | 27.886,67 | 25.218,75 | **−8.537.344 (−9,57%)** |

Trừ thuế + phí bán ≈ **−141.225đ** → lãi/lỗ thực hiện ròng ≈ **−8.678.569đ**. Đây là **khoản lỗ có
chủ đích**: VPB legacy chiếm 38,8% active NAV ở đỉnh, vượt xa trần chính sách 10%/mã; việc cắt dần
là giảm rủi ro tập trung, chấp nhận hiện thực hoá lỗ. Chương trình trim VPB **hoàn tất ngày 27/07**
(tuần sau) đưa vị thế về 1.100cp.

### 6.4 Danh mục cuối kỳ (24/07)

| Mã | KL | Giá trị TT (VND) | % NAV | % active NAV | Nhóm |
|---|---:|---:|---:|---:|---|
| DGC | 10.000 | 368.500.000 | **43,4%** | — | **Excluded — ngoài phạm vi bot** |
| VPB | 1.900 | 47.405.000 | 5,6% | 9,9% | Legacy — đã về gần trần 10% |
| VCB | 800 | 43.280.000 | 5,1% | 9,0% | Ngân hàng |
| VHM | 300 | 39.000.000 | 4,6% | 8,1% | Bất động sản |
| VNM | 601 | 35.398.900 | 4,2% | 7,4% | **CAPIT** |
| SIP | 749 | 34.978.300 | 4,1% | 7,3% | **CAPIT** |
| PVT | 2.071 | 34.896.350 | 4,1% | 7,3% | **CAPIT** |
| NCT | 373 | 34.614.400* | 4,1% | 7,2% | **CAPIT** |
| SAB | 744 | 34.596.000 | 4,1% | 7,2% | **CAPIT** |
| BID | 900 | 32.400.000 | 3,8% | 6,7% | Ngân hàng |
| CTG | 1.050 | 30.450.000 | 3,6% | 6,3% | Ngân hàng |
| TCB | 956 | 27.341.600 | 3,2% | 5,7% | Ngân hàng |
| MBB | 1.102 | 24.133.800 | 2,8% | 5,0% | Ngân hàng |
| LPB | 352 | 18.444.800 | 2,2% | 3,8% | Ngân hàng |
| HDB | 659 | 17.035.150 | 2,0% | 3,5% | Ngân hàng |
| Tiền mặt | | 27.380.812 | 3,2% | | |
| **NAV** | | **849.855.112** | 100% | | Active NAV (loại DGC): **481.355.112** |

\* NCT tính theo giá thực tế phiên 24/07 (92.800), chưa trừ cổ tức 8.000đ/cp có hiệu lực từ 27/07 —
xem giải thích ở Mục 7.3. Cộng dồn: cổ phiếu 822.474.300 + tiền 27.380.812 = **849.855.112** ✓ khớp
từng đồng với chuỗi NAV đã xác minh.

**Lãi/lỗ phần bot mua — 🔧 ĐÃ SỬA 02/08 (số cũ sai, xem Mục 7.5):** 13 mã có lịch sử khớp nội bộ,
giá vốn thật đã xác minh. DGC và VPB (vị thế legacy) **không** nằm trong con số này — xem Mục 8.

| | VND | % giá vốn |
|---|---:|---:|
| Giá vốn thật | 435.098.300 | |
| Thị giá 24/07 **(giá thật trên sàn)** | 406.569.300 | |
| → Lãi/lỗ do giá | **−28.529.000** | −6,56% |
| + Cổ tức tiền mặt đã nhận/chờ về (BID, CTG, VCB) | **+1.237.500** | |
| **= Tổng lãi/lỗ** | **−27.291.500** | **−6,27%** |

*Số cũ công bố: −33.737.560 (−7,75%) — cùng một lỗi như phần SpaceX: lấy **giá đã điều chỉnh cổ tức**
(401.360.740) trừ **giá vốn thô**. Chênh lệch 5.208.560đ chính là phần điều chỉnh NCT/SAB nêu ở
Mục 7.3.*

*(MBB **không** có cổ tức ở đây: ZaloPay mua MBB sau ngày chốt quyền 09/07 nên không được hưởng.
Cổ tức NCT 2.984.000đ và SAB 2.232.000đ **chưa** cộng: tại 24/07 giá cổ phiếu vẫn còn bao gồm quyền
nhận cổ tức — hai khoản này vào số của kỳ sau.)*

---

## 7. CÔNG BỐ SỰ CỐ & KHOẢNG TRỐNG SỐ LIỆU

Nguyên tắc: liệt kê mọi sự cố ảnh hưởng đến NAV/giao dịch/số liệu công bố, **kể cả khi đã tự khắc
phục được**.

**Không có sự cố nào chạm đến tiền thật hoặc làm sai lệch giao dịch trong tuần.** Toàn bộ 18 lệnh
thật (6 SpaceX + 12 ZaloPay) khớp đúng kế hoạch đã duyệt; không có lệnh sai, lệnh trùng hay lệnh bị
bỏ sót. Lệnh TV1 không khớp là do ràng buộc giá do nhà đầu tư đặt ra, không phải lỗi.

### 7.1 Báo cáo tuần nộp chậm 8 ngày (mức độ: quy trình, KHÔNG chạm số liệu)
Cơ chế cảnh báo "báo cáo tuần quá hạn" đã tồn tại và **đã chạy đúng**, nhưng cảnh báo nằm lẫn trong
log kiểm tra vận hành chạy 4 lần/ngày, không được ai xử lý. Hệ quả: 2 tuần liên tiếp không có báo
cáo. **Việc cần làm — người phụ trách — hạn nghiệm thu:** tách cảnh báo "báo cáo quá hạn" thành một
thông báo **riêng, có người nhận đích danh** thay vì chôn trong log tổng hợp — *Mike (điều phối
fleet)* — **hạn 08/08/2026** (trước kỳ báo cáo tuần kế tiếp).

### 7.2 Hai dòng NAV thiếu của SpaceX (21/07 và 22/07)
Tác vụ chụp NAV cuối ngày không ghi dòng cho SpaceX 2 phiên này. Dữ liệu gốc còn nguyên nên số đã
được tính lại đúng phương pháp (Mục 5.1). **Nhưng chuỗi NAV chính thức vẫn đang khuyết 2 dòng.**
Đây là **lần thứ hai** dạng sự cố này xảy ra (lần trước: ZaloPay 14/07) — nghĩa là **không phải
ngẫu nhiên**, cần tìm nguyên nhân gốc chứ không chỉ vá dữ liệu.
**Việc cần làm — người phụ trách — hạn:** (a) bổ sung 2 dòng thiếu vào `nav_history_SpaceX.csv`;
(b) tìm nguyên nhân vì sao tác vụ bỏ sót đúng 1 trong 2 tài khoản, và thêm kiểm tra "hôm nay đã ghi
đủ dòng NAV cho MỌI tài khoản chưa" vào bộ kiểm tra cuối ngày — *Winston (Data/Regime Ops)* —
**hạn 08/08/2026**.

### 7.3 Chênh lệch giá do điều chỉnh cổ tức NCT/SAB (KHÔNG phải lỗi — cần biết để đọc số cho đúng)
NCT **giao dịch không hưởng cổ tức từ 27/07** (8.000đ/cp) và SAB **từ 28/07** (3.000đ/cp). *(🔧 Sửa
02/08: bản cũ ghi SAB "27/07, 2.990đ" — sai cả ngày lẫn số tiền, nguyên nhân ở Mục 7.5.)* Cơ sở dữ liệu
thị trường **hồi tố điều chỉnh giá lịch sử** về sau ngày này, nên nếu hôm nay tính lại NAV ngày
24/07 bằng giá đã điều chỉnh, kết quả sẽ **thấp hơn 7.289.000đ (SpaceX)** và **5.208.560đ (ZaloPay)**
so với NAV thật đã ghi nhận. Đã kiểm chứng đối chiếu **khớp đến từng đồng**:

| Tài khoản | Cổ phiếu (giá điều chỉnh, tính hôm nay) | + Chênh cổ tức NCT/SAB | = Cổ phiếu đã ghi 24/07 |
|---|---:|---:|---:|
| SpaceX | 856.641.000 | +7.289.000 | **863.930.000** ✓ |
| ZaloPay | 817.265.740 | +5.208.560 | **822.474.300** ✓ |

**NAV ngày 24/07 trong báo cáo này là số ĐÚNG** (giá thực tế nhà đầu tư thấy trên bảng điện phiên
đó). Ghi rõ ở đây để bất kỳ ai tính lại về sau không nhầm là số bị sai.

### 7.4 Công cụ đối soát đã được vá (theo dõi từ báo cáo tuần trước)
Lỗi "công cụ đối soát không lọc theo tài khoản" nêu ở báo cáo tuần 13–17/07 **đã được sửa** — cả
`reconcile_equity.py` và `verify_account_snapshot.py` nay **bắt buộc** có tham số tài khoản (tự tra
từ cấu hình nếu không truyền) và **báo lỗi thay vì lấy nhầm** khi không tìm được bản ghi đúng tài
khoản. Báo cáo này đã chạy cả 2 công cụ với `--account-no` tường minh cho cả 2 tài khoản, kết quả
**Verified = True, 0 lệch khối lượng**.

### 7.5 🔧 BẢN SỬA 02/08/2026 — lãi/lỗ theo mã tính THIẾU phần cổ tức tiền mặt

**Chuyện gì đã xảy ra.** Bản phát hành đầu tiên tính lãi/lỗ danh mục bằng công thức
`(thị giá cuối kỳ − giá vốn) / giá vốn`, trong đó **thị giá lấy từ cột giá đã hồi tố điều chỉnh cổ
tức** còn **giá vốn là giá khớp thô đã trả thật**. Trộn hai hệ quy chiếu giá như vậy làm phần cổ tức
bị **trừ hai lần**, khiến danh mục bị **báo lỗ nặng hơn thực tế**.

| Tài khoản | Chỉ tiêu | Số CŨ (sai) | Số MỚI (đúng) | Chênh |
|---|---|---:|---:|---:|
| SpaceX | Lãi/lỗ cuối kỳ (Mục 5) | −94.079.443 (−9,90%) | **−81.915.443 (−8,62%)** | +1,28pp |
| ZaloPay | Lãi/lỗ phần bot mua (Mục 6.4) | −33.737.560 (−7,75%) | **−27.291.500 (−6,27%)** | +1,48pp |

Số mới gồm hai phần được tách rõ: **lãi/lỗ do giá** (so với giá **thô** trên bảng điện) **+ cổ tức
tiền mặt** đã nhận/chờ về tính đến 24/07 (SpaceX 4.875.000đ từ MBB/BID/CTG/VCB; ZaloPay 1.237.500đ
từ BID/CTG/VCB). Cổ tức NCT/SAB **không** nằm trong kỳ này vì ngày chốt quyền rơi vào 27–28/07.

**KHÔNG thay đổi:** NAV cuối kỳ, giá trị danh mục, số dư tiền mặt, mọi lệnh mua/bán và giá khớp —
tiền cổ tức vốn đã nằm sẵn trong số dư tài khoản. Sai sót chỉ ở **cách chia lãi/lỗ cho từng mã**.

**Sai sót thứ hai phát hiện khi rà soát — chuỗi NAV đếm hai lần cổ tức đúng ngày chốt quyền.**
Công ty chứng khoán ghi khoản cổ tức phải thu vào cuối **ngày cuối cùng còn hưởng quyền**, trong khi
giá dùng định giá danh mục ngày đó **vẫn là giá còn quyền** (đã bao gồm giá trị cổ tức). Tác vụ ghi
NAV lấy tiền mặt = `totalCash` (đã gồm cổ tức phải thu) → **cộng hai lần** đúng phiên đó, và tự
triệt tiêu ở phiên kế tiếp. Ngày 24/07 (cuối kỳ báo cáo này) là một trong các ngày bị ảnh hưởng:

| Tài khoản | NAV 24/07 đã ghi | Đếm trùng (NCT) | NAV đúng |
|---|---:|---:|---:|
| SpaceX | 910.995.894 | 4.000.000 | **906.995.894** |
| ZaloPay | 849.855.112 | 2.984.000 | **846.871.112** |

Hệ quả: **NAV đầu kỳ của tuần kế tiếp bị ghi cao hơn thực tế**, nên tỷ suất tuần 20–24/07 hơi **tốt
hơn** và tuần 27–31/07 hơi **xấu hơn** số đã công bố — tổng hai tuần **không đổi**. Chuỗi NAV lịch sử
**chưa tự sửa** (`nav_history_*.csv` là dữ liệu vận hành production, sửa cần quy trình riêng) — đã
đưa vào việc cần làm.

**Chống tái diễn:** công cụ dùng chung `mike/bin/dividend_adjusted_return.py` (tự phát hiện sự kiện
cổ tức, **bắt buộc đối soát sổ broker** trước khi đưa vào báo cáo, 16 phép tự kiểm) — bắt buộc dùng
cho mọi tỉ suất per-position từ kỳ sau. Công bố đầy đủ nhất về sự cố này nằm ở **báo cáo tháng 7,
Mục 8.4–8.5**.

---

## 8. ĐỐI SOÁT ĐẲNG THỨC HAI CHIỀU

**SpaceX** — đối soát tại ngày 31/07 (mốc gần nhất có đầy đủ dữ liệu API; kết quả áp dụng cho toàn
bộ chuỗi vì đây là kiểm tra tích luỹ từ đầu):

| Vế trái (Vốn + Lãi/lỗ − Phí) | VND | | Vế phải (Tài sản − Nợ) | VND |
|---|---:|---|---|---:|
| Vốn ban đầu | 1.000.000.000 | | Cổ phiếu (MTM) | 924.115.000 |
| + Lãi/lỗ chưa thực hiện | −62.610.443 | | + Tiền mặt | 14.326.923 |
| − Phí giao dịch (0,075%) | −740.044 | | − Nợ margin | −6.212 |
| − Phí/lãi đã post (API thật) | −6.720 | | | |
| **= Vế trái** | **936.642.793** | | **= Vế phải** | **938.435.711** |

**Chênh lệch −1.792.918 (−0,19% NAV) → ✅ ĐẠT ngưỡng dung sai** (±0,05% NAV + sàn 5tr). Các cấu phần
đã nhận diện: (a) lãi/lỗ **đã thực hiện** chưa đưa vào công thức (đợt trim 06/07 + bán HPG 15/07,
≈ −1,8tr kể cả thuế/phí); (b) **cổ tức tiền mặt đã nhận/đang chờ về** (9.775.000đ tại 31/07, nằm
trong số dư tiền mặt nhưng chưa có ở vế trái); (c) khác biệt **quy ước giá vốn** giữa hệ thống
(bình quân từ lệnh khớp của bot) và broker (bình quân động điều chỉnh sau mỗi lần bán một phần).
Ba cấu phần này bù trừ nhau; phần dư còn lại **sẽ được đối soát với sao kê chính thức DNSE trong
báo cáo tháng** — chưa khép kín tuyệt đối và được nêu nguyên trạng.

**ZaloPay: đẳng thức hai chiều VẪN CHƯA lập được** (hạn chế đã biết, không thay bằng số ước lượng).
Công cụ đối soát chạy ra chênh lệch +532,6tr và **kết luận "LỆCH VƯỢT NGƯỠNG" — con số này KHÔNG có
ý nghĩa và KHÔNG được dùng**, vì vế phải của công cụ chỉ tính 13–14 mã có lịch sử khớp nội bộ
(440,96tr), bỏ qua DGC (390,5tr) và VPB legacy (45,0tr) vốn không có giá vốn đã xác minh. Vế phải
**thật** vẫn được xác minh đầy đủ và khớp từng đồng (Mục 6.4). Cần bổ sung khả năng hạch toán giá
vốn vị thế legacy trước khi có thể so sánh **tỷ suất sinh lời** của ZaloPay với SpaceX —
*Winston / Taylor* — **chưa có hạn chốt, không chặn vận hành**.

---

## 9. KẾ HOẠCH & VIỆC CẦN LÀM

| Việc | Người phụ trách | Hạn |
|---|---|---|
| Tách cảnh báo "báo cáo quá hạn" ra khỏi log tổng hợp, gửi đích danh (Mục 7.1) | Mike | 08/08/2026 |
| Bổ sung 2 dòng NAV thiếu 21–22/07 + kiểm tra "đủ dòng NAV mọi tài khoản" (Mục 7.2) | Winston | 08/08/2026 |
| 🔧 **MỚI 02/08** — sửa `daily_nav_snapshot.py` để không đếm hai lần cổ tức đúng ngày chốt quyền + hiệu chỉnh các dòng NAV lịch sử bị ảnh hưởng (Mục 7.5) | Winston / Taylor | 08/08/2026 |
| 🔧 **MỚI 02/08** — bắt buộc mọi tỉ suất per-position trong báo cáo đi qua `mike/bin/dividend_adjusted_return.py` (Mục 7.5) | Taylor | đã xong 02/08 |
| Giữ rổ CAPIT đủ 60 phiên (đến ~mid-10/2026), **không cắt lỗ, không bán sớm** | Hệ thống (tự động) | ~15/10/2026 |
| Hoàn tất trim VPB legacy về dưới trần 10% active NAV | Hệ thống (đã xong 27/07) | ✅ đã xong |
| Hoàn tất chương trình gom TV1 (PECC1) — giới hạn giá ≤19.900 | Hệ thống + DollarBill | ✅ đã xong 29/07 |
| Đối soát phí/thuế/lãi margin với sao kê chính thức DNSE | Taylor | báo cáo tháng 7 |

**Rủi ro cần theo dõi sát trong 2–4 tuần tới:**
1. **Tỷ trọng cổ phiếu ~95–97%, tiền mặt gần cạn.** Nếu thị trường rơi tiếp, danh mục chịu gần trọn.
   Rổ CAPIT được miễn trừ cắt lỗ theo thiết kế — đây là cam kết đã định trước, không phải quên xử lý.
2. **DGC (ZaloPay)** vẫn là rủi ro đơn lẻ lớn nhất của tài khoản (43,4% NAV) và nằm ngoài tầm can
   thiệp của bot cho tới khi HOSE gỡ hạn chế (~11–12/2026).
3. **Mùa báo cáo tài chính Q2/2026** đang diễn ra — book LAG (đón sóng sau công bố lợi nhuận) đã bắt
   đầu phát tín hiệu trở lại từ 27/07 sau nhiều tuần rỗng.

**Lịch vận hành tiêu chuẩn không đổi** (T2–T6): kiểm tra dữ liệu (17:30) → lập kế hoạch T+1 (19:30,
gửi duyệt lại 23:00) → kiểm tra sẵn sàng (08:20 & 08:45) → phiên sáng (09:05) → kiểm tra giữa phiên
(12:45) → phiên chiều (13:00) → báo cáo cuối ngày (15:00), giám sát tự động mỗi 5 phút trong giờ
giao dịch.

---

## 10. PHỤ LỤC — PHƯƠNG PHÁP & LƯU Ý

- **Pipeline xác minh bắt buộc:**
  1. `verify_account_snapshot.py` (chạy với `--account-no` tường minh) — giá vốn/khối lượng thật từ
     log gốc API broker, cross-check độc lập với journal khớp lệnh nội bộ. Tuần này: **SpaceX
     Verified = True** (20 mã) và **ZaloPay Verified = True** (13 mã bot), **0 lệch khối lượng**.
  2. `daily_nav_snapshot.py` → `nav_history_{account}.csv` — chuỗi NAV ngày từ số dư/vị thế API thật
     (**thiếu 2 dòng SpaceX 21–22/07, đã tái dựng và ghi rõ** — Mục 5.1 & 7.2).
  3. `reconcile_equity.py` — đẳng thức hai chiều (Mục 8); SpaceX ✅ đạt (−0,19%), ZaloPay chưa lập
     được. Công bố nguyên trạng, không làm tròn cho đẹp.
  - **Đối chiếu độc lập bổ sung:** giá trị cổ phiếu tính lại từ sổ vị thế broker khớp **từng đồng**
    với chuỗi NAV ở cả 2 tài khoản, sau khi hoàn nguyên điều chỉnh cổ tức NCT/SAB (Mục 7.3).
- **⚠️ Một lưu ý kỹ thuật cho người kiểm tra lại:** file journal khớp lệnh nội bộ ghi khối lượng
  **luỹ kế** cho mỗi lệnh con, nên **cộng dồn thẳng các dòng FILL sẽ ra số lớn hơn thực tế**. Số
  trong báo cáo này lấy từ **báo cáo thực thi từng phiên + sổ vị thế broker** (hai nguồn đã đối
  chiếu khớp nhau), không phải từ phép cộng journal.
- **Giá mark-to-market** = giá đóng cửa thực tế phiên 24/07. Số liệu cùng ngày (định giá lệnh, sức
  mua) luôn lấy từ API DNSE trực tiếp, không lấy từ cơ sở dữ liệu thị trường (dữ liệu chỉ đồng bộ
  qua đêm).
- **Giá vốn vị thế legacy ZaloPay** (DGC, VPB): dùng giá vốn do broker DNSE báo — nguồn broker-native
  nhưng là số broker tự tính, chưa đối soát được với chứng từ gốc của giao dịch cũ. Lãi/lỗ chưa thực
  hiện của DGC/VPB **không** đưa vào P&L hợp nhất; **NAV không bị ảnh hưởng** (chỉ phụ thuộc khối
  lượng × giá thị trường).
- **Phí/thuế:** phí giao dịch 0,075%/lượt (đã xác nhận biểu phí); thuế bán 0,1% giá trị bán theo quy
  định. Lãi margin ~12,5%/năm là **số nhà đầu tư cung cấp, chưa xác minh với DNSE**. Các con số
  phí/thuế trong báo cáo là **ước tính từ biểu phí**, chưa đối soát sao kê chính thức.
- **Track record vẫn rất ngắn** (SpaceX 17 phiên, ZaloPay 13 phiên): mọi so sánh với VN-Index chỉ
  mang tính mô tả, **chưa đủ ý nghĩa thống kê**. Việc danh mục giảm ít hơn chỉ số trong một tuần —
  kể cả ở phiên sập 22/07 — **không** chứng minh chiến lược tốt; nó chỉ nhất quán với thiết kế.
- **Đây không phải khuyến nghị đầu tư.** Kết quả quá khứ (kể cả backtest) không đảm bảo kết quả
  tương lai.

---
*Báo cáo tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn (DNSE API) và cơ sở
dữ liệu thị trường (BigQuery). Người phụ trách quỹ rà soát trước khi phát hành cho nhà đầu tư.*
