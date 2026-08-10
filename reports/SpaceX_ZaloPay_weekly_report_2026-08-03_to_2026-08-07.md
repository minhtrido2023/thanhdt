# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: 03/08/2026 – 07/08/2026

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ 01/07/2026 (có margin)
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ 06/07/2026 (cash-only, không margin)
**Chiến lược:** V2.4 (2 book BAL/LAG + parking custom30V tại NEUTRAL + rổ CAPIT bear-washout)
**Ngày lập báo cáo:** 10/08/2026 · **Người lập:** Taylor (Quant) — số liệu đối soát qua pipeline xác minh chuẩn (Mục 8)
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

> ⚠️ **Báo cáo nộp trễ** (lẽ ra tối 07/08 hoặc sáng 08/08). Phát hiện tự động bởi
> `check_report_cadence.sh`, dispatch Taylor soạn bù ngày 10/08. Trong lúc dựng số liệu, phát hiện
> **4 vấn đề chất lượng dữ liệu thật trong tuần** — tất cả đã điều tra, đối soát 2 nguồn độc lập, và
> công bố đầy đủ ở Mục 7. Không có vấn đề nào ảnh hưởng đến lệnh giao dịch thật hay tiền thật của
> nhà đầu tư — toàn bộ là sai sót ở tầng **ghi chép/báo cáo NAV**.

---

## ⛔ ĐÍNH CHÍNH 10/08/2026 — TỈ SUẤT TỪNG MÃ CỦA BẢN PHÁT HÀNH ĐẦU TIÊN BỊ SAI (BÁO LỖ NẶNG HƠN THỰC TẾ)

> **Bản đầu tiên của báo cáo này (gửi 10/08/2026 lúc ~01:52) công bố tỉ suất lãi/lỗ từng mã CHƯA
> CỘNG CỔ TỨC TIỀN MẶT đã nhận.** Nhà đầu tư đã phát hiện khi đối chiếu với giá hoà vốn hiển thị
> trên app DNSE. **Đây là lần thứ HAI cùng một loại lỗi** (lần đầu 02/08/2026, đã sửa 3 báo cáo
> tháng 7). Số NAV, số dư tiền, số lượng cổ phiếu và mọi lệnh giao dịch **KHÔNG bị ảnh hưởng** —
> tiền cổ tức vẫn luôn nằm trong NAV; sai sót nằm ở **cách quy tỉ suất về từng mã**.
>
> **Vì sao lọt lần 2 (khác nguyên nhân lần 1 — đây là KHOẢNG TRỐNG PHẠM VI, không phải quên):**
> bản đầu kiểm tra `cum_dividend_excl` = 0 mọi ngày trong tuần 03–07/08 rồi kết luận "không mã nào
> trả cổ tức trong tuần ⇒ không cần điều chỉnh". Chỉ báo đó **đúng nhưng trả lời sai câu hỏi**: nó
> đo cổ tức PHÁT SINH trong đúng tuần báo cáo (dùng cho kế toán tiền/NAV của tuần), trong khi cái
> cần hỏi là **"giá vốn của vị thế ĐANG GIỮ đã trừ cổ tức nhận từ các tuần TRƯỚC chưa"**. Sáu sự
> kiện có ngày chốt quyền **trước** kỳ báo cáo (MBB 09/07 · BID 17/07 · CTG và VCB 23/07 · NCT
> 27/07 · SAB 28/07) vẫn nằm nguyên trong giá vốn của các vị thế còn giữ đến 07/08.
>
> **Ba nguồn độc lập cùng xác nhận** (chi tiết Mục 11): (1) `costPrice` của DNSE trong sổ vị thế —
> broker tự trừ cổ tức khỏi giá vốn, lệch đúng bằng cổ tức ở đúng 6 mã; (2) `cashDividendReceiving`
> của broker tại 07/08 — SpaceX 9.775.000đ và ZaloPay 6.453.500đ **khớp từng đồng** với tổng cổ tức
> tính lại; (3) `dividend_adjusted_return.py` giải cổ tức từ tiền mặt broker thật — cả 6 sự kiện
> đều `CASH_CONFIRMED`.
>
> **Ngoài ra, một lỗi thứ hai không liên quan cổ tức**: giá vốn **LPB của SpaceX** bị tính 52.583,3đ
> thay vì 51.466,7đ — vị thế LPB cũ đã bán sạch ngày 06/07 nhưng bình quân gia quyền của
> `verify_account_snapshot.py` **không reset về 0**, nên lô mua lại ngày 15/07 bị trộn với lô đã tất
> toán.
>
> **Tác động (số cũ → số đúng, cổ tức tính RÒNG sau thuế TNCN 5%):**
>
> | Chỉ tiêu | Số CŨ (sai) | Số ĐÚNG | Chênh |
> |---|---:|---:|---:|
> | SpaceX — lãi/lỗ chưa thực hiện (Mục 4.2) | −25.723.600 (−3,28%) | **−15.180.766 (−1,94%)** | **+10.542.834 / +1,34pp** |
> | SpaceX — lỗ đã thực hiện 13 lệnh bán 07/08 (Mục 3.2) | −13.911.850 | **−11.883.426** | +2.028.424 |
> | ZaloPay — lãi/lỗ chưa thực hiện, 14 mã bot (Mục 5.3) | −3.401.800 (−0,75%) | **+2.729.025 (+0,60%)** | +6.130.825 / **đảo dấu** |
> | Mã bị đảo dấu | SAB −5,53% · SAB(ZLP) −5,69% | **SAB +0,49% · SAB(ZLP) +0,32%** | |
> | Mã lệch lớn nhất | NCT −12,46% | **NCT −4,41%** | +8,05pp |
>
> **NAV, tiền mặt, số lượng cổ phiếu, danh sách lệnh: KHÔNG THAY ĐỔI.**
>
> **Cơ chế chống tái diễn (đã triển khai cùng ngày, không phải lời hứa):**
> `mike/bin/report_return_gate.py` — cổng **CHẶN CỨNG** chạy tự động trong `send_report_email.py`:
> mọi tỉ suất per-position công bố (trong bảng lẫn trong văn xuôi) được dựng lại độc lập từ
> `costPrice` của broker + cổ tức đã xác minh; lệch quá 0,15 điểm % ⇒ **không gửi được báo cáo**.
> Chạy trên chính bản sai này, cổng chặn đúng **9/9** sai sót và không báo nhầm mã nào.
>
> *Các bảng bên dưới đã được sửa; số cũ giữ nguyên trong cột "số cũ" ở Mục 11 để đối chiếu.*

---

> **✅ Nguồn số liệu:** `verify_account_snapshot.py` (chạy có `--account-no` cho **cả 2** tài khoản,
> asof 07/08) — **cả 2 Verified = True, 0 lệch khối lượng, 0 warning**. Giá trị cổ phiếu cuối kỳ tính
> lại **độc lập** từ sổ vị thế broker (dnse_raw 07/08, đọc lúc 19:05:27) × giá đóng cửa BigQuery khớp
> **từng đồng** với NAV dùng trong báo cáo này ở cả 2 tài khoản (SpaceX 757.655.000; ZaloPay
> 938.446.500 gồm cả DGC/VPB legacy). **3 dòng NAV bị thiếu trong `nav_history_*.csv`** (SpaceX
> 06/08; ZaloPay 06/08 và 07/08) đã được **dựng lại độc lập** cho báo cáo này bằng đúng công thức của
> `daily_nav_snapshot.py` (vị thế broker thật × giá đóng cửa BigQuery + tiền mặt broker thật), đối
> soát khớp 2 nguồn — chi tiết đầy đủ + việc cần Winston làm để ghi chính thức vào CSV: Mục 7.

---

## 1. TÓM TẮT ĐIỀU HÀNH

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (chốt 31/07) | 938.435.711 | 888.828.498 |
| NAV cuối kỳ (07/08) | **961.311.265** | **950.719.172**ᴮ |
| Thay đổi trong kỳ | **+22.875.554 (+2,44%)** | **+61.890.674 (+6,96%)** |
| VN-Index cùng kỳ (31/07 → 07/08) | 1.735,78 → 1.768,06 (**+1,86%**) | (cùng chỉ số) |
| **Chênh so với chỉ số** | **+0,58 điểm %** | **+5,10 điểm %** |
| — Trong đó riêng DGC (ngoài phạm vi bot) | — | **+51.000.000 (+13,04%)** |
| — Phần còn lại (bot quản lý + VPB legacy + tiền) | — | **+10.890.674 (+2,19%)** |
| Cổ phiếu cuối kỳ (giá đóng cửa 07/08) | 757.655.000 | 938.446.500 |
| Tiền mặt tại công ty CK | 203.656.265 | 12.272.672 |
| Nợ margin cuối kỳ | 0 | 0 |
| Tỷ trọng cổ phiếu/NAV | **78,8%** | **98,7%** (gồm DGC 46,5%) |
| Số mã nắm giữ cuối kỳ | 20 | 16 |

ᴮ **NAV cuối kỳ ZaloPay là số dựng lại** — dòng 07/08 gốc bị thiếu trong `nav_history_ZaloPay.csv`
vì `eod_trading_report.sh` thoát sớm khi phát hiện "không có state file thực thi", trước khi kịp gọi
`daily_nav_snapshot.py`. Số dựng lại dùng đúng vị thế broker + giá đóng cửa BigQuery ngày 07/08 (vị
thế không đổi so với 06/08 — cả tuần ZaloPay không khớp lệnh nào, xem Mục 3 và 7.3). Chi tiết đầy đủ
+ đối soát 2 nguồn: Mục 7.

**Nhận định tuần:** thị trường **tăng nhẹ 4/5 phiên rồi hạ nhiệt cuối tuần** — VN-Index +1,86% cả
tuần, đỉnh tuần ở phiên 04/08 (1.777,23) rồi rung lắc nhẹ 2 phiên cuối. Cả 2 tài khoản **gần như
không giao dịch** — **4/5 phiên đầu tuần là HOLD hoàn toàn ở cả 2 tài khoản** (không phải lỗi, đúng
thiết kế: BAL rỗng, rổ CAPIT giữ nguyên theo lịch, không tín hiệu LAG nào tới hạn):

- **SpaceX +2,44%** (+0,58pp so với chỉ số) — HOLD 4 phiên, rồi **Thứ Sáu 07/08 tái cơ cấu lớn**: bán
  13 mã ngân hàng/chứng khoán (189,4tr, hiện thực hoá lỗ ròng ≈ −14,2tr sau phí/thuế) để tài trợ mua
  DRI (cao su, LAG_HI) — **lệnh mua DRI và lệnh bán VHM đều KHÔNG khớp** (giá không về vùng đặt), nên
  danh mục kết thúc tuần với **203,7tr tiền mặt chưa giải ngân được (21,2% NAV)**, xem Mục 4.3.
- **ZaloPay +6,96%** (+5,10pp) — **DGC hồi rất mạnh +13,04%** (391,0tr → 442,0tr) chiếm gần hết mức
  tăng; phần còn lại (bot quản lý + VPB legacy + tiền, không giao dịch cả tuần) **+2,19%**, khớp với
  đà tăng của thị trường. **ZaloPay không đặt được lệnh nào trong cả 5 phiên** — không phải lỗi hệ
  thống mà vì kế hoạch giao dịch 07/08 (9 lệnh) chưa được nhà đầu tư duyệt trước giờ chạy cả 2 phiên
  sáng lẫn chiều; đã được Winston root-cause ngay trong ngày, xem Mục 7.3.
- **DT5G giữ NEUTRAL (3/5) cam kết cả 5 phiên** — không cap phòng thủ nào kích hoạt. Ở tầng bên dưới,
  bộ đếm ứng viên DT-gate đã âm thầm tích luỹ hướng **CRISIS 7/25 → 10/25** từ 03/08 đến 06/08, rồi
  **base đổi ngày 06/08** và bộ đếm chuyển hướng theo dõi **BEAR (2/10)** vào 07/08 — chưa đủ để commit
  ở cả hai hướng, thuần tuý là dữ liệu theo dõi (xem Mục 2).
- **🔴 Một số NAV không chính xác đã được gửi tự động tối 05/08** trước khi hệ thống tự phát hiện và
  sửa — chi tiết đầy đủ ở Mục 7.1. Toàn bộ số trong báo cáo này dùng bản đã sửa.

---

## 2. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

| Ngày | VN-Index | Δ ngày | Ghi chú |
|---|---:|---:|---|
| 31/07 (đầu kỳ) | 1.735,78 | — | |
| 03/08 | 1.762,84 | +1,56% | |
| 04/08 | 1.777,23 | +0,82% | đỉnh tuần |
| 05/08 | 1.776,46 | −0,04% | gần như đi ngang |
| 06/08 | 1.764,78 | −0,66% | |
| 07/08 (cuối kỳ) | 1.768,06 | +0,19% | |

- Cả tuần **+1,86%**, tiếp nối đà hồi phục của tuần trước (27–31/07: +2,95%). Xu hướng tích luỹ nhẹ,
  không có phiên biến động mạnh (biên độ ngày lớn nhất chỉ ±1,56%).
- **DT5G committed = NEUTRAL (3/5) toàn bộ tuần** (nguồn: `vnindex_5state_dt5g_live`). Bộ đếm DT-gate
  (điều kiện cần để CHUYỂN trạng thái, không phải trạng thái hiện tại):

  | Ngày | Candidate | Đếm | Base giữ từ |
  |---|---|---:|---|
  | 03/08 | CRISIS | 7/25 | 24/07 |
  | 04/08 | CRISIS | 8/25 | 24/07 |
  | 05/08 | CRISIS | 9/25 | 24/07 |
  | 06/08 | CRISIS | 10/25 | 24/07 |
  | 07/08 | BEAR | 2/10 | 06/08 |

  Đọc đúng: đây là bộ đếm **thuần theo dõi**, KHÔNG phải cảnh báo — CRISIS cần đủ 25 phiên liên tục
  mới commit (mới đi được 10/25 rồi bộ đếm bị reset khi base đổi hướng ngày 06/08); BEAR chỉ cần 10
  phiên, hiện mới 2/10. Trạng thái sống (`state`) người dùng thấy trong mọi báo cáo khác vẫn là
  **NEUTRAL** suốt tuần — không có hành động phòng thủ nào được kích hoạt.

---

## 3. HOẠT ĐỘNG GIAO DỊCH TRONG TUẦN

### 3.1 Tổng quan — 4/5 phiên HOLD hoàn toàn ở cả 2 tài khoản

| Ngày | SpaceX | ZaloPay |
|---|---|---|
| 03/08 | HOLD (không lệnh) | HOLD (không lệnh) |
| 04/08 | HOLD (không lệnh) | HOLD (không lệnh) |
| 05/08 | HOLD (không lệnh) | HOLD (không lệnh) |
| 06/08 | HOLD (không lệnh) | HOLD (không lệnh) |
| 07/08 | **13/15 lệnh khớp** (tái cơ cấu + LAG) | **0/9 lệnh khớp** (approval gate chặn cả ngày) |

Không có tín hiệu BAL nào phát sinh trong tuần; rổ CAPIT giữ nguyên theo lịch 60 phiên; book LAG chỉ
có 1 ứng viên tới hạn (DRI, cao su) và chỉ tới cửa vào thứ Sáu.

### 3.2 SpaceX 07/08 — tái cơ cấu lớn (funding cho DRI), DRI + VHM không khớp

| Lệnh | Mã | KL kế hoạch | KL khớp | Giá khớp BQ | Giá trị (VND) | Mục đích |
|---|---|---:|---:|---:|---:|---|
| Bán | CTG | 800 | 800 (100%) | 32.600 | 26.080.000 | Park-trim (funding DRI) |
| Bán | VCB | 400 | 400 (100%) | 60.500 | 24.200.000 | Park-trim |
| Bán | MBB | 900 | 900 (100%) | 24.250 | 21.825.000 | Park-trim |
| Bán | LPB | 400 | 400 (100%) | 52.200 | 20.880.000 | Park-trim |
| Bán | VPB | 800 | 800 (100%) | 24.850 | 19.880.000 | Park-trim |
| Bán | BID | 500 | 500 (100%) | 39.150 | 19.575.000 | Park-trim |
| Bán | TCB | 600 | 600 (100%) | 29.200 | 17.520.000 | Park-trim |
| Bán | HDB | 600 | 600 (100%) | 26.600 | 15.960.000 | Park-trim |
| Bán | ACB | 400 | 400 (100%) | 22.250 | 8.900.000 | Park-trim |
| Bán | SHB | 500 | 500 (100%) | 11.650 | 5.825.000 | Park-trim |
| Bán | SHS | 200 | 200 (100%) — **thoát hẳn vị thế** | 15.700 | 3.140.000 | Park-trim |
| Bán | TPB | 200 | 200 (100%) | 14.500 | 2.900.000 | Park-trim |
| Bán | VIX | 200 | 200 (100%) | 13.750 | 2.750.000 | Park-trim |
| Bán | VHM | 400 | **0 (0%)** — không khớp | — | 0 | Park-trim |
| Mua | DRI | 3.500 | **0 (0%)** — không khớp | 12.900 (LO) | 0 | **LAG_HI** (đón sóng RSS3/cao su) |

**Tổng bán khớp: 189.435.000đ / kế hoạch 263.7tr (72%).** Phí giao dịch 0,075% ≈ 142.076đ, thuế bán
0,1% ≈ 189.435đ.

**Vì sao bán 13 mã cùng lúc:** đây là bước "park-trim" gộp với "JIT-unpark" (bán vị thế parking để
tài trợ ngay cho lệnh mua LAG mới, cơ chế L1+L2 đã mô tả trong báo cáo trước) — tài trợ cho lệnh mua
DRI (LAG_HI, tín hiệu PEAD ngành cao su sau khi giá RSS3 tăng mạnh Q2/2026, đã qua due-diligence: DCF
CHEAP MoS +37,8%, ROE5Y 15,8%, FSCORE 6, D/E 0,28, PE 4,21, không dính cờ bất thường).

**⚠️ Cả DRI (mua) và VHM (bán) đều KHÔNG khớp trong phiên** — giá đặt không về đúng vùng limit
(DRI đặt mua LO 12.900, VHM đặt bán tại vùng giá không chạm). Kết quả: **tiền đã rút ra khỏi 13 vị
thế ngân hàng/chứng khoán nhưng KHÔNG được tái triển khai vào DRI** — danh mục kết thúc tuần với một
khoản tiền mặt lớn (203,7tr, 21,2% NAV) **chưa sinh lời**, thay vì hoán đổi rủi ro như kế hoạch. Đây
không phải lỗi thực thi (lệnh đặt đúng, không khớp vì giá thị trường không tới) nhưng là điều nhà đầu
tư cần biết — xem Mục 4.3.

**Lãi/lỗ thực hiện từ 13 lệnh bán** *(đã sửa 10/08 — giá vốn THÔ + cổ tức RÒNG nhận trên chính số
cổ phiếu đã bán; xem ĐÍNH CHÍNH đầu báo cáo và Mục 11):*

| Mã | KL | Giá vốn thô | Giá bán | Cổ tức ròng/cp | Lãi/lỗ | % |
|---|---:|---:|---:|---:|---:|---:|
| CTG | 800 | 34.476,80 | 32.600 | 427,5 | −1.159.429 | −4,20% |
| VCB | 400 | 62.300,00 | 60.500 | 427,5 | −549.000 | −2,20% |
| MBB | 900 | 25.850,00 | 24.250 | 950,0 | −585.000 | −2,51% |
| LPB | 400 | 51.466,67ᴰ | 52.200 | — | +293.333 | +1,42% |
| VPB | 800 | 27.914,30 | 24.850 | — | −2.451.429 | −10,98% |
| BID | 500 | 42.991,30 | 39.150 | 427,5 | −1.706.902 | −3,97% |
| TCB | 600 | 33.900,00 | 29.200 | — | −2.820.000 | −13,86% |
| HDB | 600 | 26.675,00 | 26.600 | — | −45.000 | −0,28% |
| ACB | 400 | 22.650,00 | 22.250 | — | −160.000 | −1,77% |
| SHB | 500 | 13.550,00 | 11.650 | — | −950.000 | −14,02% |
| SHS | 200 | 18.900,00 | 15.700 | — | −640.000 | −16,93% |
| TPB | 200 | 16.800,00 | 14.500 | — | −460.000 | −13,69% |
| VIX | 200 | 17.000,00 | 13.750 | — | −650.000 | −19,12% |
| **Tổng** | | | | | **−11.883.426** | |

ᴰ LPB: giá vốn sửa từ 52.583,30 → **51.466,67** (lô LPB cũ đã bán sạch 06/07, bình quân gia quyền
phải reset — xem ĐÍNH CHÍNH). Không liên quan cổ tức.

*Số cũ của bảng này (bản phát hành đầu) là **−13.911.850**; chênh +2.028.424 hoàn toàn do cộng lại
cổ tức của 4 mã trên + sửa giá vốn LPB. Số cổ phiếu bán và giá bán không đổi.*

Trừ phí (142.076đ) + thuế (189.435đ) → **lỗ thực hiện ròng ≈ −12.214.937đ (−1,27% NAV)** *(số cũ:
−14.243.361đ / −1,48%)*. Đây là chi
phí cắt lỗ các vị thế ngân hàng/chứng khoán mua từ đầu tháng 7 để giải phóng vốn cho LAG — hợp lý về
mặt chiến lược (đưa vốn từ nhóm hiệu suất kém sang tín hiệu mới), nhưng khoản lỗ là **thật, đã hiện
thực hoá**, không phải biến động giá tạm thời.

### 3.3 ZaloPay — 0 lệnh khớp cả tuần (không phải lỗi 4 phiên đầu, xem Mục 7.3 cho phiên 07/08)

Không có giao dịch nào. 4 phiên đầu là HOLD đúng thiết kế (không tín hiệu). Phiên 07/08 có kế hoạch 9
lệnh (park-trim + JIT-unpark tài trợ mua DRI, cùng logic với SpaceX) nhưng **toàn bộ bị approval gate
chặn cả 2 lần chạy (sáng 09:05 và chiều 13:00)** vì kế hoạch chưa được nhà đầu tư duyệt trước giờ
chạy — chi tiết root-cause Mục 7.3.

---

## 4. TÀI KHOẢN SPACEX

### 4.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ | Chênh | Ghi chú |
|---|---:|---:|---:|---:|---|
| 31/07 (đầu kỳ) | 938.435.711 | — | — | — | |
| 03/08 | 959.726.244 | +2,27% | +1,56% | +0,71pp | HOLD |
| 04/08 | 965.416.271 | +0,59% | +0,82% | −0,23pp | HOLD |
| 05/08 | 960.116.297 | −0,55%ᶜ | −0,04% | −0,51pp | HOLD |
| 06/08 | **950.871.297**ᴬ | −0,96% | −0,66% | −0,30pp | HOLD (dựng lại) |
| 07/08 (cuối kỳ) | 961.311.265 | +1,10% | +0,19% | +0,91pp | Tái cơ cấu (Mục 3.2) |

ᴬ Dòng 06/08 **dựng lại độc lập** — dòng gốc thiếu trong `nav_history_SpaceX.csv` vì API broker bị
timeout khi `eod_trading_report.sh` chạy (Mục 7.2). Vị thế 06/08 = vị thế 05/08 (HOLD, không lệnh),
định giá theo giá đóng cửa BigQuery ngày 06/08: cổ phiếu 936.275.000 + tiền mặt 14.596.297 = NAV
950.871.297. Đối soát: 21 vị thế khớp `verified_snapshot_SpaceX_2026-08-06.json` (đã có trên đĩa từ
lúc `verify_account_snapshot.py` chạy như một bước con trong lần thử NAV thất bại đó).

ᶜ Số **05/08 đã sửa** — bản gốc gửi Discord tối đó ghi **+7,38% (NAV 1.036.656.297)**, sai do lỗi giá
liên quan sự kiện VHM chia thưởng cổ phiếu 1:1 cùng ngày. Chi tiết đầy đủ + cơ chế: Mục 7.1.

Cả tuần **+2,44%** vs chỉ số **+1,86%**. Đặc điểm: HOLD phẳng lặng 4 phiên đầu (biến động ngày sát với
chỉ số, trừ 05/08 vốn dĩ gần như đi ngang thật), rồi bứt lên +0,91pp so với chỉ số ở phiên tái cơ cấu
07/08 — nhưng mức bứt lên này phần lớn đến từ việc **chuyển 189,4tr từ cổ phiếu (đã giảm giá) sang
tiền mặt (không giảm)**, không phải từ chọn đúng cổ phiếu tăng giá.

### 4.2 Danh mục cuối kỳ (07/08 — giá vốn THÔ đã xác minh × giá đóng cửa 07/08, **đã cộng cổ tức**)

*Bảng này đã được SỬA ngày 10/08 — xem ĐÍNH CHÍNH đầu báo cáo. Cột `%` là **tỉ suất tổng** =
(giá 07/08 + cổ tức RÒNG − giá vốn thô) / giá vốn thô, đúng theo coding_guidelines §21.*

| Mã | KL | Giá vốn thô | Giá 07/08 | Cổ tức ròng/cp | Giá trị TT (VND) | Lãi/lỗ chưa TH | % | % cũ (sai) | Nhóm |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| SIP | 1.700 | 47.058,80 | 50.900 | — | 86.530.000 | +6.530.000 | **+8,16%** | +8,16% | CAPIT |
| VHM | 1.000 | 74.900,00 | 73.000 | — | 73.000.000 | −1.900.000 | −2,54% | −2,54% | Bất động sản |
| PVT | 3.500 | 17.100,00 | 18.350 | — | 64.225.000 | +4.375.000 | **+7,31%** | +7,31% | CAPIT |
| VNM | 900 | 58.600,00 | 62.000 | — | 55.800.000 | +3.060.000 | **+5,80%** | +5,80% | CAPIT |
| BID | 1.400 | 42.991,30 | 39.050 | 427,5 | 54.670.000 | −4.919.326 | −8,17% | −9,17% | Ngân hàng |
| VCB | 900 | 62.300,00 | 59.700 | 427,5 | 53.730.000 | −1.955.250 | −3,49% | −4,17% | Ngân hàng |
| SAB | 1.100 | 47.368,20 | 44.750 | 2.850,0 | 49.225.000 | **+255.000** | **+0,49%** | −5,53% | CAPIT |
| CTG | 1.500 | 34.476,80 | 32.500 | 427,5 | 48.750.000 | −2.323.929 | −4,49% | −5,73% | Ngân hàng |
| TCB | 1.400 | 33.900,00 | 29.700 | — | 41.580.000 | −5.880.000 | −12,39% | −12,39% | Ngân hàng |
| NCT | 500 | 94.360,00 | 82.600 | 7.600,0 | 41.300.000 | −2.080.000 | −4,41% | −12,46% | CAPIT |
| VPB | 1.500 | 27.914,30 | 25.000 | — | 37.500.000 | −4.371.429 | −10,44% | −10,44% | Ngân hàng |
| MBB | 1.500 | 25.850,00 | 24.150 | 950,0 | 36.225.000 | −1.125.000 | −2,90% | −6,58% | Ngân hàng |
| LPB | 500 | 51.466,67ᴰ | 52.900 | — | 26.450.000 | +716.667 | +2,78% | +0,60% | Ngân hàng |
| ACB | 1.100 | 22.650,00 | 22.400 | — | 24.640.000 | −275.000 | −1,10% | −1,10% | Ngân hàng |
| HDB | 900 | 26.675,00 | 26.550 | — | 23.895.000 | −112.500 | −0,47% | −0,47% | Ngân hàng |
| SHB | 1.000 | 13.550,00 | 11.700 | — | 11.700.000 | −1.850.000 | −13,65% | −13,65% | Ngân hàng |
| TPB | 600 | 16.800,00 | 14.600 | — | 8.760.000 | −1.320.000 | −13,10% | −13,10% | Ngân hàng |
| TV1 | 400 | 19.600,00 | 19.700 | — | 7.880.000 | +40.000 | +0,51% | +0,51% | Ngoài V2.4 |
| VIX | 500 | 17.000,00 | 13.600 | — | 6.800.000 | −1.700.000 | −20,00% | −20,00% | Chứng khoán |
| VND | 300 | 17.800,00 | 16.650 | — | 4.995.000 | −345.000 | −6,46% | −6,46% | Chứng khoán |
| **Tổng cổ phiếu** | | **782.820.266** | | | **757.655.000** | **−15.180.766** | **−1,94%** | −3,28% | |
| Tiền mặt | | | | | 203.656.265 | | | | |
| Phí phải trả | | | | | 0 | | | | |
| **NAV** | | | | | **961.311.265** | | | | |

ᴰ LPB: giá vốn sửa 52.583,30 → **51.466,67** (lỗi không-reset bình quân gia quyền, không liên quan
cổ tức — xem ĐÍNH CHÍNH).

Cộng dồn kiểm tra: 757.655.000 + 203.656.265 = **961.311.265** ✓ khớp **từng đồng** với chuỗi NAV,
đồng thời khớp phép tính lại độc lập từ sổ vị thế broker × giá đóng cửa BigQuery. **NAV không đổi so
với bản đầu** — cổ tức luôn nằm sẵn trong NAV (mục `cashDividendReceiving` của broker); đính chính
chỉ đổi cách quy tỉ suất về từng mã.

**Cổ tức đã cộng vào các vị thế đang giữ: 9.984.500đ ròng.** Sáu sự kiện có ngày chốt quyền TRƯỚC kỳ
báo cáo (MBB 09/07 · BID 17/07 · CTG và VCB 23/07 · NCT 27/07 · SAB 28/07), tất cả `CASH_CONFIRMED`
qua `dividend_adjusted_return.py`. **Lưu ý thuế:** 9.775.000đ trong số dư tiền mặt cuối kỳ vẫn là
**khoản phải thu ghi GỘP** — thuế TNCN 5% (**488.750đ**, ≈0,051% NAV) sẽ được khấu trừ khi chi trả,
nên NAV cuối kỳ đang **cao hơn thực nhận đúng khoản đó**. Tỉ suất trong bảng đã trừ 5%.

**Phân bổ nhóm:** Ngân hàng 367,9tr (**38,3% NAV**) · CAPIT phòng thủ 297,1tr (**30,9%**) · Bất động
sản (VHM) 73,0tr (7,6%) · Chứng khoán 11,8tr (1,2%) · TV1 7,9tr (0,8%) · **Tiền mặt 203,7tr (21,2%)**.
Toàn bộ 20 mã dưới trần 10%/mã (lớn nhất SIP 9,0%).

### 4.3 ⚠️ 21,2% NAV bằng tiền mặt chưa giải ngân — hệ quả của lệnh DRI không khớp

Khác hẳn tuần trước (tiền mặt cạn 1,5% NAV), tuần này SpaceX kết thúc với **203,7tr tiền mặt** — gần
như toàn bộ đến từ 189,4tr bán ra ngày 07/08 để tài trợ mua DRI, nhưng **lệnh mua đó không khớp**.

- Đây **không phải quyết định phòng thủ có chủ đích** — nó là tác dụng phụ của một lệnh mua bị trượt
  giá trong khi 13 lệnh bán tài trợ cho nó đã khớp đủ. Danh mục hiện đang **thiếu 21,2pp tỷ trọng cổ
  phiếu** so với thiết kế bình thường.
  - Nếu DRI không khớp trong phiên tới, cần xem lại: đặt lại lệnh DRI ở vùng giá khác, hay tái phân
    bổ số tiền này sang mục tiêu khác? Đây là **quyết định cần Dollar Bill/nhà đầu tư**, không phải
    việc hệ thống tự xử lý.
- Rổ CAPIT (297,1tr, 30,9% NAV) vẫn miễn trừ cắt lỗ, giữ tới ~giữa tháng 10/2026 theo thiết kế.

---

## 5. TÀI KHOẢN ZALOPAY

### 5.1 Diễn biến NAV theo ngày

| Ngày | NAV (VND) | Δ ngày | VN-Index Δ | Chênh | Ghi chú |
|---|---:|---:|---:|---:|---|
| 31/07 (đầu kỳ) | 888.828.498 | — | — | — | |
| 03/08 | 901.985.831 | +1,48% | +1,56% | −0,08pp | HOLD |
| 04/08 | 906.684.413 | +0,52% | +0,82% | −0,30pp | HOLD |
| 05/08 | 912.854.495 | +0,68%ᶜ | −0,04% | +0,72pp | HOLD |
| 06/08 | **937.070.045**ᴬ | +2,65% | −0,66% | **+3,31pp** | HOLD (dựng lại) — DGC +6,9% |
| 07/08 (cuối kỳ) | **950.719.172**ᴬ | +1,46% | +0,19% | +1,27pp | HOLD, chặn approval gate (Mục 7.3) |

ᴬ Hai dòng 06/08 và 07/08 **dựng lại độc lập** — cả hai thiếu trong `nav_history_ZaloPay.csv` (lý do
khác nhau mỗi ngày, xem Mục 7.2/7.3). Vị thế không đổi trong cả 2 ngày (HOLD), định giá theo giá đóng
cửa BigQuery: 06/08 = 924.797.500 (cổ phiếu, gồm DGC 433.500.000 + VPB 45.270.000 + 14 mã bot
446.027.500) + 12.272.545 (tiền) = 937.070.045; 07/08 = 938.446.500 (cổ phiếu) + 12.272.672 (tiền) =
950.719.172. Đối soát 07/08 khớp **từng đồng** với `verify_account_snapshot.py` (14 mã có journal) +
giá DGC/VPB tính tay từ BQ — xem cách kiểm chứng lại ở Mục 7.2.

ᶜ Số **05/08 đã sửa** — bản gốc gửi Discord tối đó ghi **+5,74% (NAV 958.754.495)**, cùng nguyên nhân
lỗi giá VHM chia thưởng cổ phiếu với SpaceX. Chi tiết Mục 7.1.

Cả tuần **+6,96%** vs chỉ số **+1,86%** — chênh **+5,10 điểm %**, gần như toàn bộ đến từ DGC (Mục 5.2).
Đáng chú ý: **06/08 tăng +2,65% trong khi VN-Index giảm −0,66%** — hoàn toàn do DGC nhảy vọt (BQ Close
40.550→43.350, +6,9% một phiên) khi phần còn lại của danh mục không đổi vị thế; đây chính là chênh
lệch khiến broker báo giá thị trường (`marketPrice`) của DGC bị lệch >5% so với giá đóng cửa BigQuery
và khiến `daily_nav_snapshot.py` từ chối tự ghi NAV hôm đó (Mục 7.2).

### 5.2 Phân tích — tách phần DGC và phần còn lại

| Cấu phần | 31/07 | 07/08 | Thay đổi | % |
|---|---:|---:|---:|---:|
| **DGC** (legacy, ngoài phạm vi bot) | 391.000.000 | 442.000.000 | **+51.000.000** | **+13,04%** |
| **Phần còn lại** (bot quản lý + VPB legacy + tiền, không giao dịch) | 497.828.498 | 508.719.172 | +10.890.674 | **+2,19%** |
| **Tổng NAV** | 888.828.498 | 950.719.172 | +61.890.674 | +6,96% |

DGC tiếp tục hồi phục mạnh sau đợt sập tháng 7 (tuần trước +6,11%, tuần này +13,04% — cộng dồn 2 tuần
+20,03%), nhưng **vẫn thấp hơn đỉnh trước khủng hoảng**. Phần bot quản lý +2,19%, sát với đà tăng thị
trường (+1,86%), hợp lý vì không có giao dịch nào thay đổi cấu trúc danh mục trong tuần.

**DGC vẫn là rủi ro đơn lẻ lớn nhất** (46,5% NAV cuối kỳ, tăng từ 44,0% tuần trước do giá tăng nhanh
hơn phần còn lại — ngoài tầm can thiệp của bot cho tới khi HOSE gỡ hạn chế giao dịch, ước ~11–12/2026).

### 5.3 Danh mục cuối kỳ (07/08)

| Mã | KL | Giá 07/08 | Giá trị TT (VND) | % NAV | % active NAV | Nhóm |
|---|---:|---:|---:|---:|---:|---|
| DGC | 10.000 | 44.200 | 442.000.000 | **46,5%** | — | **Excluded — ngoài phạm vi bot** |
| VCB | 800 | 59.700 | 47.760.000 | 5,0% | 9,4% | Ngân hàng |
| VHM | 600 | 73.000 | 43.800.000 | 4,6% | 8,6% | Bất động sản |
| SIP | 749 | 50.900 | 38.124.100 | 4,0% | 7,5% | CAPIT |
| PVT | 2.071 | 18.350 | 38.002.850 | 4,0% | 7,5% | CAPIT |
| VNM | 601 | 62.000 | 37.262.000 | 3,9% | 7,3% | CAPIT |
| VPB | 1.800 | 25.000 | 45.000.000 | 4,7% | 8,8% | Legacy 1.100cp + LAG 700cp |
| BID | 900 | 39.050 | 35.145.000 | 3,7% | 6,9% | Ngân hàng |
| CTG | 1.050 | 32.500 | 34.125.000 | 3,6% | 6,7% | Ngân hàng |
| SAB | 744 | 44.750 | 33.294.000 | 3,5% | 6,5% | CAPIT |
| NCT | 373 | 82.600 | 30.809.800 | 3,2% | 6,1% | CAPIT |
| TCB | 956 | 29.700 | 28.393.200 | 3,0% | 5,6% | Ngân hàng |
| MBB | 1.102 | 24.150 | 26.613.300 | 2,8% | 5,2% | Ngân hàng |
| CSV | 1.000 | 22.000 | 22.000.000 | 2,3% | 4,3% | LAG |
| LPB | 352 | 52.900 | 18.620.800 | 2,0% | 3,7% | Ngân hàng |
| HDB | 659 | 26.550 | 17.496.450 | 1,8% | 3,4% | Ngân hàng |
| **Tổng cổ phiếu** | | | **938.446.500** | 98,7% | | |
| Tiền mặt | | | 12.272.672 | 1,3% | | |
| **NAV** | | | **950.719.172** | 100% | | Active NAV (loại DGC): **508.719.172** |

Cộng dồn kiểm tra: 938.446.500 + 12.272.672 = **950.719.172** ✓ khớp từng đồng, đồng thời khớp phép
tính lại độc lập (14 mã có journal qua `verify_account_snapshot.py` = 451.446.500 + DGC 442.000.000 +
VPB 45.000.000 = 938.446.500). Không mã nào thay đổi vị thế trong tuần.

**Lãi/lỗ chưa thực hiện phần bot quản lý** *(đã sửa 10/08 — cộng cổ tức RÒNG, xem ĐÍNH CHÍNH)*
(14 mã có lịch sử journal, không gồm DGC/VPB legacy): giá vốn thô 454.848.300 → giá thị trường
451.446.500 **+ cổ tức ròng 6.130.825** = **+2.729.025 (+0,60%)** *(số cũ sai: −3.401.800 / −0,75%
— **đảo dấu**)*. Cổ tức ròng 6.130.825đ = đúng 95% của khoản phải thu 6.453.500đ mà broker ghi nhận
tại 07/08 (BID 900cp · CTG 1.050cp · VCB 800cp × 450đ; NCT 373cp × 8.000đ; SAB 744cp × 3.000đ) —
khớp **từng đồng**, là bằng chứng độc lập cho phép cộng này.

Vị thế tốt nhất: **CSV +11,4%** · SIP +8,0% · **SAB +0,3%** *(cũ −5,7%)* · PVT +6,4% · VNM +5,6%.
Yếu nhất: **TCB −6,1%** · **NCT −4,4%** *(cũ −12,5%)* · LPB −3,5%. Không mã nào giao dịch trong tuần
nên biến động 100% do giá và cổ tức.

⚠️ ZaloPay **không** được hưởng cổ tức MBB ngày 09/07 (chưa nắm giữ tại ngày chốt quyền) — khác
SpaceX. Đã kiểm riêng từng tài khoản, không suy từ tài khoản kia.

---

## 6. TỔNG HỢP 2 TUẦN (27/07 → 07/08) — để không đọc lệch bức tranh

| | SpaceX | ZaloPay | VN-Index |
|---|---:|---:|---:|
| Tuần 27–31/07 | +3,01% | +4,59% | +2,95% |
| Tuần 03–07/08 | +2,44% | +6,96% | +1,86% |
| **Gộp 2 tuần** | **+5,52%** | **+11,87%** | **+4,86%** |

SpaceX **tốt hơn chỉ số 0,66 điểm %** qua 2 tuần liên tiếp gần như không giao dịch (chỉ 1 phiên tái
cơ cấu). ZaloPay **tốt hơn chỉ số 7,01 điểm %**, gần như toàn bộ nhờ DGC hồi phục 2 tuần liên tiếp
(+6,11% rồi +13,04%, cộng dồn **+19,95%**) — phần bot quản lý riêng chỉ **+5,68%** qua 2 tuần, vẫn tốt hơn
chỉ số nhưng khiêm tốn hơn nhiều so với con số tổng.

---

## 7. 🔴 CÔNG BỐ SỰ CỐ & KHOẢNG TRỐNG SỐ LIỆU — 4 vấn đề phát hiện trong tuần

**Không có sự cố nào khiến hệ thống đặt lệnh sai hoặc mất tiền thật.** Cả 4 vấn đề dưới đây đều ở
tầng **ghi chép/báo cáo NAV**, hoặc là **fail-safe hoạt động đúng thiết kế** (chặn lệnh khi chưa được
duyệt). Toàn bộ số liệu trong báo cáo này đã dùng bản đã sửa/dựng lại.

### 7.1 🔴 NGHIÊM TRỌNG NHẤT — NAV 05/08 bị thổi phồng do lỗi giá sự kiện VHM chia thưởng 1:1, ĐÃ GỬI Discord trước khi tự sửa

**Sự việc:** VHM thực hiện chia thưởng cổ phiếu tỷ lệ **1:1** có hiệu lực 05/08/2026 (SpaceX 500cp →
1.000cp, giá vốn 149.800 → 74.900/cp; ZaloPay 300cp → 600cp, giá vốn tương ứng giảm một nửa — đã xác
nhận số lượng cổ phiếu và giá vốn broker khớp chính xác tỷ lệ 1:1, không mất giá trị). Lần chạy
`daily_nav_snapshot.py` **đầu tiên** trong ngày (gửi vào EOD report Discord lúc 19:10 ICT) đã lấy
**số lượng cổ phiếu MỚI (1.000/600, sau chia thưởng)** nhưng định giá bằng **giá tham chiếu CŨ (trước
chia thưởng, ~152–153 nghìn/cp)** — kết quả riêng vị thế VHM bị tính giá trị gấp đôi thực tế.

| | Bản gửi Discord 19:10 05/08 (SAI) | Bản đã sửa (nav_history hiện tại) | Chênh |
|---|---:|---:|---:|
| SpaceX NAV | 1.036.656.297 (+7,38%) | **960.116.297 (−0,55%)** | −76.540.000 |
| ZaloPay NAV | 958.754.495 (+5,74%) | **912.854.495 (+0,68%)** | −45.900.000 |

**Bằng chứng số đã sửa mới đúng:** `verified_snapshot_SpaceX_2026-08-05.json` (tính độc lập bằng
`verify_account_snapshot.py`, dùng 500cp × giá ATC 153.000 = 76.500.000 — quy đổi tương đương của
1.000cp × 76.500) cho tổng giá trị cổ phiếu 945.560.000, khớp sát `nav_history` (945.520.000, chênh
40.000đ do làm tròn giá ATC/BQ). **Bản SAI dùng tương đương 1.000cp × ~153.000 = gấp đôi giá trị thật
của riêng vị thế VHM.**

**Nguyên nhân gốc đã có sẵn trong code** (comment tại `daily_nav_snapshot.py`, đúc kết từ chính sự cố
này): số lượng vị thế cập nhật đúng ngay trong ngày sự kiện, nhưng nguồn giá tham chiếu **chưa đồng
bộ hết với sự kiện doanh nghiệp**. Hệ thống đã **tự phát hiện và sửa trong cùng buổi tối** (dòng
`nav_history` hiện tại là bản đã sửa) — nhưng bản SAI **đã được gửi ra Discord** trước khi kịp sửa.
**Cũng chính sự cố này là lý do một chốt chặn giá cross-check mới được thêm vào script** — chốt chặn
đó lại là nguyên nhân của sự cố tiếp theo (Mục 7.2, phần DGC).

**Ảnh hưởng:** (a) KHÔNG ảnh hưởng lệnh nào — cả 2 tài khoản đều HOLD ngày 05/08; (b) NAV cuối tháng
7 dùng để chốt báo cáo tuần trước không bị ảnh hưởng (05/08 nằm ngoài kỳ đó); (c) diễn giải thị
trường "thị trường bật lại mạnh" trong bản gửi Discord tối 05/08 là **sai** — thực tế cả 2 tài khoản
gần như đi ngang, đúng với việc VN-Index cũng gần như đi ngang (−0,04%) hôm đó.

**Việc cần làm:** rà soát toàn bộ các mã có sự kiện chia tách/thưởng cổ phiếu sắp tới, xác nhận chốt
chặn cross-check (đã thêm) đủ để bắt các trường hợp tương lai — *Winston* — trước mùa ĐHCĐ tiếp theo.

### 7.2 SpaceX & ZaloPay 06/08 — 2 dòng NAV thiếu, 2 nguyên nhân khác nhau, đã dựng lại cho báo cáo này

**SpaceX:** API vị thế broker bị timeout khi `eod_trading_report.sh` gọi (`Read timed out
(read timeout=30)`) — script fail-safe đúng thiết kế, từ chối ghi NAV khi không lấy được vị thế thay
vì đoán. Đây là lỗi mạng tạm thời, không lặp lại các ngày khác trong tuần.

**ZaloPay:** chốt chặn cross-check giá vừa được thêm sau sự cố 7.1 lại **bắt nhầm** — DGC tăng giá
thật +6,9% trong phiên (BQ Close 40.550→43.350, đã xác nhận bằng chuỗi giá liên tục không đứt đoạn),
nhưng trường `marketPrice` của vị thế broker vẫn còn giữ giá **hôm trước** (40.550, do chưa refresh
kịp tại thời điểm chụp 15:13:52) → lệch >5% → script từ chối ghi. **Đây là false positive** (biến
động giá thật, không phải lỗi corporate-action), khác với 7.1 (đúng corporate-action nhưng giá sai).

**Dựng lại cho báo cáo này (cả 2 tài khoản HOLD ngày 06/08, vị thế = 05/08):**
- SpaceX: 21 vị thế × giá đóng cửa BQ 06/08 = 936.275.000 (khớp `verified_snapshot_SpaceX_2026-08-06.json`,
  file này đã tồn tại sẵn vì được tạo như bước con của lần chạy thất bại) + tiền mặt broker thật
  14.596.297 (đọc từ `dnse_raw_2026-08-06.jsonl`, bản ghi 15:13:52) = **NAV 950.871.297**.
- ZaloPay: DGC 10.000cp × 43.350 = 433.500.000 + VPB 1.800cp × 25.150 (giá BQ 06/08) = 45.270.000 +
  14 mã bot (theo `verified_snapshot_ZaloPay_2026-08-06.json`) 446.027.500 = tổng cổ phiếu 924.797.500
  + tiền mặt broker thật 12.272.545 = **NAV 937.070.045**.

Cả 2 số đều nằm trong biên độ biến động hợp lý so với ngày liền kề (SpaceX −0,96%, ZaloPay +2,65% —
phù hợp với việc DGC tăng mạnh đúng ngày đó), không vượt ngưỡng cảnh báo ±15%/ngày của hệ thống.

**Việc cần làm — *Winston* — hạn 15/08/2026:**
1. Ghi chính thức 2 dòng trên vào `nav_history_SpaceX.csv` / `nav_history_ZaloPay.csv` (giá trị đã
   tính sẵn ở trên, cột `balance_ts` = 2026-08-06T15:13:52 / 2026-08-06T15:13:54).
2. Cân nhắc nới lỏng ngưỡng cross-check giá (hiện 5%) hoặc thêm logic phân biệt "giá hôm qua y hệt
   marketPrice" (dấu hiệu stale field, như ca DGC) với "giá lệch bất thường" (dấu hiệu corp-action
   thật, như ca VHM) — hai sự cố 7.1/7.2 là hai mặt của cùng một đánh đổi ngưỡng.
3. Xem xét retry tự động khi timeout API broker (SpaceX 06/08) thay vì bỏ qua cả ngày.

### 7.3 ZaloPay 07/08 — 0/9 lệnh khớp cả ngày; đã root-cause CÙNG NGÀY, KHÔNG phải bug mới

**Đã được Winston/Wags điều tra và đóng ngay trong ngày 07/08** (bus event
`Winston/question — ops-autofix-unresolved: run-bot-fail-SpaceX-2026-08-07` 02:07 UTC +
`incidents/2026-08/2026-08-07-plan-merge-left-stale-jit-orders-double-sell.md`) — báo cáo này chỉ
tổng hợp lại vì ảnh hưởng trực tiếp đến việc tuần này ZaloPay không giao dịch, và vì dòng NAV liên
quan cũng bị thiếu (do `eod_trading_report.sh` thoát sớm khi phát hiện "không có state file thực
thi", trước khi kịp gọi `daily_nav_snapshot.py`).

**Chuỗi sự kiện:** kế hoạch 07/08 (9 lệnh, park-trim + JIT-unpark tài trợ mua DRI, cùng cấu trúc với
SpaceX Mục 3.2) được nhà đầu tư duyệt lúc 12:36 ICT → 12:47 Wags phát hiện lỗi kỹ thuật (bước gộp lệnh
để sót 15 lệnh nguồn, gây bán trùng — không liên quan tới việc duyệt) → DollarBill sửa lúc 12:50:15,
giữ nguyên phê duyệt → theo log ghi lại, kế hoạch được xác nhận duyệt lại lúc 13:32:30. **Cả 2 lần bot
chạy trong ngày (09:05 sáng, 13:00 chiều) đều rơi vào cửa sổ TRƯỚC khi phê duyệt hoàn tất** → approval
gate (đúng thiết kế, không đoán/không tự bỏ qua) từ chối cả 9 lệnh cả 2 lần. Khác với SpaceX (có một
lần chạy lại thành công sau 13:32, xem Mục 3.2), **ZaloPay không có lần chạy lại thứ ba** trong ngày —
`ops_autofix` có dispatch một fixer cuối buổi chiều nhưng không kịp tạo phiên chạy mới trước khi hết
giờ giao dịch.

**Không phải bug logic gate** — approval gate hoạt động đúng thiết kế (chặn khi chưa duyệt, không tự
động đoán ý người dùng). Đây là **khoảng trống vận hành**: thiếu một bước retry tự động sau khi phê
duyệt về muộn trong ngày.

**Dựng lại NAV 07/08 cho báo cáo này** (vị thế = 06/08, không đổi): 14 mã bot (`verify_account_snapshot.py`
asof 07/08) 451.446.500 + DGC 10.000×44.200=442.000.000 + VPB 1.800×25.000=45.000.000 = tổng cổ phiếu
938.446.500 + tiền mặt broker thật (đọc 19:05:27) 12.272.672 = **NAV 950.719.172**.

**Việc cần làm:** thêm cơ chế retry `run_bot.sh` tự động khi phê duyệt về muộn trong phiên (đề xuất đã
ghi trong incident 07/08, chưa triển khai) — *Winston/Wags* — chưa có hạn chốt cụ thể, ưu tiên trung
bình (ảnh hưởng cơ hội, không ảnh hưởng an toàn vốn).

### 7.4 Ghi nhận nhỏ — lỗi đơn vị tham số `reconcile_equity.py --margin-rate-annual`

Trong lúc lập báo cáo này, phát hiện truyền `--margin-rate-annual 12.5` (nghĩa là 12,5%/năm) bị script
diễn giải thành **1250%/năm** trong dòng diễn giải residual (không ảnh hưởng đẳng thức chính, chỉ ảnh
hưởng dòng ước tính lãi margin tham khảo). Có thể do script kỳ vọng giá trị dạng thập phân (0.125)
thay vì phần trăm. *Taylor* — ưu tiên thấp, không chặn báo cáo (số ảnh hưởng bằng 0 vì cả 2 tài khoản
không có nợ margin cuối kỳ).

---

## 8. ĐỐI SOÁT ĐẲNG THỨC HAI CHIỀU (07/08)

**SpaceX** (chạy `reconcile_equity.py --account SpaceX --account-no 0002023347`):

| Vế trái (Vốn + Lãi/lỗ − Phí) | VND | | Vế phải (Tài sản − Nợ) | VND |
|---|---:|---|---|---:|
| Vốn ban đầu | 1.000.000.000 | | Cổ phiếu (MTM 07/08) | 757.655.000 |
| + Lãi/lỗ chưa thực hiện *(chỉ do GIÁ — xem ghi chú)* | −25.723.600 | | + Tiền mặt | 203.656.265 |
| − Phí giao dịch (0,075% × giá vốn thật) | −587.534 | | − Nợ margin | 0 |
| − Phí/lãi đã post (API thật) | −2.285 | | | |
| **= Vế trái** | **973.686.581** | | **= Vế phải** | **961.311.265** |

**Chênh lệch +12.375.316 (+1,29% NAV) → ❌ VƯỢT ngưỡng dung sai** (±0,05% NAV + sàn 5tr). Nguyên nhân
đã biết (giống hệt tuần trước, chưa xử lý): công cụ `reconcile_equity.py` **chỉ tính lãi/lỗ CHƯA thực
hiện của vị thế đang giữ**, không cộng dồn **lãi/lỗ ĐÃ thực hiện** từ toàn bộ lịch sử giao dịch kể từ
go-live (gồm cả khoản lỗ thực hiện −11,9tr tuần này, Mục 3.2, và các đợt trim trước đó). Đây là hạn
chế đã biết của công cụ, không phải tiền bị thất thoát

> **Ghi chú thêm sau đính chính 10/08:** con số −25.723.600 ở vế trái là output NGUYÊN BẢN của
> `reconcile_equity.py`, **chỉ tính chênh lệch GIÁ**, không gồm cổ tức — cố ý giữ nguyên để bảng
> phản ánh đúng cái công cụ in ra. Vì thế **khoản mục còn thiếu trong đẳng thức nay đã tách được
> làm hai**, không còn là một cục "chưa giải thích": (a) lãi/lỗ đã thực hiện luỹ kế (âm) và
> (b) **cổ tức tiền mặt đã nhận 12.175.000đ GỘP** — riêng (b) đã chiếm gần trọn khoảng chênh
> +12.375.316đ. Việc bổ sung CẢ HAI khoản vào công cụ vẫn treo cho Taylor (Mục 9). — **NAV vế phải là số thật, đã xác minh 2
nguồn độc lập** (Mục 4.2). Việc bổ sung sổ lãi/lỗ đã thực hiện luỹ kế vào công cụ đối soát vẫn đang
treo từ báo cáo trước — *Taylor* — chưa có hạn chốt.

**ZaloPay:** đẳng thức hai chiều **vẫn chưa lập được** (hạn chế đã biết, giống mọi báo cáo trước) — vế
phải công cụ chỉ tính 14 mã có lịch sử journal (451.446.500), bỏ qua DGC (442,0tr) và VPB legacy
(45,0tr) vốn không có giá vốn xác minh qua journal nội bộ. NAV **thật** vẫn xác minh đầy đủ và khớp
từng đồng qua 2 nguồn độc lập (Mục 5.3).

---

## 9. KẾ HOẠCH & VIỆC CẦN LÀM

| Việc | Người phụ trách | Hạn |
|---|---|---|
| Ghi chính thức 2 dòng NAV 06/08 (SpaceX + ZaloPay) vào nav_history CSV (Mục 7.2) | Winston | 15/08/2026 |
| Ghi chính thức dòng NAV 07/08 ZaloPay vào nav_history CSV (Mục 7.3) | Winston | 15/08/2026 |
| Rà soát ngưỡng cross-check giá + retry timeout broker (Mục 7.2) | Winston | chưa chốt hạn |
| Cơ chế retry run_bot khi phê duyệt về muộn trong phiên (Mục 7.3) | Winston/Wags | ưu tiên trung bình |
| Rà soát các mã có sự kiện chia tách/thưởng cổ phiếu sắp tới (Mục 7.1) | Winston | trước ĐHCĐ tiếp theo |
| Quyết định số phận lệnh DRI chưa khớp — đặt lại giá hay tái phân bổ 203,7tr tiền mặt SpaceX (Mục 4.3) | DollarBill/nhà đầu tư | phiên tới |
| Bổ sung sổ lãi/lỗ đã thực hiện luỹ kế vào reconcile_equity.py (Mục 8) | Taylor | chưa chốt hạn |
| Sửa đơn vị tham số --margin-rate-annual (Mục 7.4) | Taylor | ưu tiên thấp |

**Rủi ro cần theo dõi sát:**
1. **203,7tr tiền mặt SpaceX (21,2% NAV) chưa giải ngân** — hệ quả ngoài ý muốn của lệnh DRI không
   khớp, không phải quyết định phòng thủ. Cần quyết định hướng xử lý ở phiên tới.
2. **DGC (ZaloPay) tăng tỷ trọng lên 46,5% NAV** sau 2 tuần hồi liên tiếp — rủi ro tập trung đơn lẻ
   lớn nhất của tài khoản, ngoài tầm can thiệp tới ~11–12/2026.
3. **ZaloPay mất trọn 1 phiên giao dịch** (07/08) vì khoảng trống retry vận hành — nếu lặp lại, có
   thể làm lỡ nhiều tín hiệu LAG hơn trong mùa BCTC.
4. **Rổ CAPIT** — 297,1tr = 30,9% NAV SpaceX; 174,0tr (ước, không đổi) ≈ 18,3% NAV ZaloPay. Khoá 60
   phiên tới ~giữa 10/2026, không cắt lỗ.
5. **DT-gate candidate đang theo dõi BEAR (2/10)** kể từ 06/08 — chưa đủ để commit, thuần dữ liệu
   theo dõi, không cần hành động (Mục 2).

---

## 10. PHỤ LỤC — PHƯƠNG PHÁP & LƯU Ý

- **Pipeline xác minh bắt buộc:**
  1. `verify_account_snapshot.py` (chạy với `--account-no` tường minh) — **SpaceX Verified = True**
     (20 mã), **ZaloPay Verified = True** (14 mã bot), **0 lệch khối lượng, 0 warning**.
  2. `daily_nav_snapshot.py` → `nav_history_{account}.csv` — **3 dòng thiếu phát hiện và dựng lại độc
     lập trong quá trình lập báo cáo này** (Mục 7.2/7.3), **1 dòng đã được hệ thống tự sửa nhưng bản
     sai đã kịp gửi ra Discord trước đó** (Mục 7.1). Việc ghi chính thức 3 dòng dựng lại vào CSV giao
     cho Winston (Mục 9).
  3. `reconcile_equity.py` — SpaceX ❌ lệch +1,29% (nguyên nhân đã biết: thiếu lãi/lỗ đã thực hiện luỹ
     kế, Mục 8); ZaloPay chưa lập được (hạn chế đã biết, output bị loại bỏ có chủ đích).
  - **Đối chiếu độc lập:** giá trị cổ phiếu 07/08 tính lại từ sổ vị thế broker × giá đóng cửa BigQuery
    khớp **từng đồng** với NAV dùng trong báo cáo ở **cả 2** tài khoản.
- **Cách dựng lại 3 dòng NAV thiếu (Mục 7.2/7.3):** với mỗi ngày HOLD (không lệnh khớp), vị thế = vị
  thế ngày liền trước; định giá = giá đóng cửa BigQuery ngày đó; tiền mặt = bản ghi `balances` cuối
  cùng trong ngày từ `dnse_raw_{date}.jsonl` (đọc trực tiếp, không suy đoán). Đây là **đúng công thức**
  `daily_nav_snapshot.py` dùng khi chạy thành công — chỉ khác là chạy thủ công vì lần chạy tự động thất
  bại. Đối soát: SpaceX 06/08 khớp `verified_snapshot_SpaceX_2026-08-06.json` (file có sẵn từ bước con
  của lần chạy thất bại); ZaloPay 06/08 và 07/08 khớp `verified_snapshot_ZaloPay_2026-08-0{6,7}.json`
  cộng giá trị DGC/VPB tính tay (2 mã này không có journal fill history nên không nằm trong output của
  `verify_account_snapshot.py`).
- **Giá mark-to-market** = giá đóng cửa 07/08. Số liệu cùng ngày (định giá lệnh, sức mua) luôn lấy từ
  API DNSE trực tiếp.
- **Giá vốn vị thế legacy ZaloPay** (DGC, phần VPB cũ): dùng giá vốn broker DNSE báo — broker-native
  nhưng do broker tự tính, chưa đối soát với chứng từ gốc. **NAV không bị ảnh hưởng.**
- **Phí/thuế:** giao dịch 0,075%/lượt; thuế bán 0,1%. Lãi margin ~12,5%/năm là **số nhà đầu tư cung
  cấp, chưa xác minh với DNSE**. Cả 2 tài khoản không có nợ margin cuối kỳ nên không phát sinh.
- **Cổ tức — ĐÃ SỬA 10/08 (xem ĐÍNH CHÍNH đầu báo cáo):** bản đầu ghi "không có mã nào trả cổ tức
  tiền mặt trong tuần ⇒ không cần điều chỉnh §21". Câu đó **đúng về sự kiện trong tuần nhưng sai về
  kết luận**: 6 sự kiện có ngày chốt quyền TRƯỚC kỳ báo cáo vẫn nằm trong giá vốn của vị thế đang
  giữ. Toàn bộ tỉ suất per-position ở Mục 3.2 / 4.2 / 5.3 nay đã đi qua
  `mike/bin/dividend_adjusted_return.py` (6/6 sự kiện `CASH_CONFIRMED`, giải từ tiền mặt broker
  thật) và được **cổng chặn cứng** `mike/bin/report_return_gate.py` kiểm lại độc lập trước khi gửi.
- **Track record vẫn ngắn** (SpaceX 27 phiên, ZaloPay 23 phiên): mọi so sánh với VN-Index chỉ mang
  tính mô tả, **chưa đủ ý nghĩa thống kê**.
- **Đây không phải khuyến nghị đầu tư.** Kết quả quá khứ (kể cả backtest) không đảm bảo kết quả
  tương lai.

---

## 11. PHỤ LỤC ĐÍNH CHÍNH 10/08/2026 — BẰNG CHỨNG & NGUYÊN NHÂN GỐC

### 11.1 Sáu sự kiện cổ tức bị bỏ sót (tất cả `CASH_CONFIRMED`)

Giải trực tiếp từ **tiền mặt broker thật** (`cashDividendReceiving`) bằng hệ phương trình 2 tài
khoản — không suy từ tỉ số giá, không ước lượng:

| Mã | Ngày chốt quyền | GỘP (đ/cp) | RÒNG sau thuế 5% | SpaceX hưởng | ZaloPay hưởng |
|---|---|---:|---:|---:|---:|
| MBB | 09/07/2026 | 1.000 | 950,0 | 2.400 cp | **0** (chưa nắm giữ) |
| BID | 17/07/2026 | 450 | 427,5 | 1.900 cp | 900 cp |
| CTG | 23/07/2026 | 450 | 427,5 | 2.300 cp | 1.050 cp |
| VCB | 23/07/2026 | 450 | 427,5 | 1.300 cp | 800 cp |
| NCT | 27/07/2026 | 8.000 | 7.600,0 | 500 cp | 373 cp |
| SAB | 28/07/2026 | 3.000 | 2.850,0 | 1.100 cp | 744 cp |

**Đối soát khép kín (khớp từng đồng, không làm tròn):**
- SpaceX: MBB đã chi trả 17/07 = 2.400.000đ; còn phải thu tại 07/08 = 855.000 + 1.035.000 + 585.000
  + 4.000.000 + 3.300.000 = **9.775.000đ** = đúng `cashDividendReceiving` broker ghi tại 07/08.
- ZaloPay: 405.000 + 472.500 + 360.000 + 2.984.000 + 2.232.000 = **6.453.500đ** = đúng số broker ghi.
- Tổng cổ tức SpaceX 12.175.000đ GỘP → 11.566.250đ RÒNG, chia đúng làm hai phần không chồng lấn:
  **9.984.500đ** cho cổ phiếu còn giữ (Mục 4.2) + **1.581.750đ** cho cổ phiếu đã bán 07/08 (Mục 3.2).
  Số cổ phiếu hưởng quyền của từng mã bằng đúng (KL còn giữ + KL bán 07/08) — khớp cả với sổ lô của
  broker (ví dụ MBB: 2.400 = 1.500 giữ + 900 bán).

### 11.2 Đối chiếu độc lập với giá hoà vốn app DNSE (nguồn của nhà đầu tư)

DNSE **tự trừ cổ tức GỘP khỏi giá vốn**, nên `costPrice` của broker là nhân chứng độc lập:

| Mã | Giá vốn báo cáo (cũ) | `costPrice` broker 07/08 | Chênh | Giải thích |
|---|---:|---:|---:|---|
| MBB | 25.850,00 | 24.850,00 | 1.000 | = cổ tức MBB |
| BID | 42.991,30 | 42.541,30 | 450 | = cổ tức BID |
| CTG | 34.476,79 | 34.026,79 | 450 | = cổ tức CTG |
| VCB | 62.300,00 | 61.850,00 | 450 | = cổ tức VCB |
| NCT | 94.360,00 | 86.360,00 | 8.000 | = cổ tức NCT |
| SAB | 47.368,18 | 44.368,18 | 3.000 | = cổ tức SAB |
| **LPB** | **52.583,33** | **51.466,67** | **1.116,67** | ❗ **KHÔNG phải cổ tức** — lỗi giá vốn |
| 13 mã còn lại | — | — | **0** | khớp tuyệt đối |

Ảnh chụp app của nhà đầu tư ngày 10/08 (MBB giá hoà vốn 24.950 · NCT 86.622 · PVT 17.151) là
`breakEvenPrice` = `costPrice` + phí mua + phí/thuế bán ước tính, nên cao hơn `costPrice` một chút
(MBB 24.850 → 24.950) — hai con số **nhất quán**, không mâu thuẫn. Chênh khối lượng MBB
(1.500 trong báo cáo vs 1.100 trên app) đã kiểm bằng nhật ký thực thi: **giao dịch thật sáng 10/08**
(bán 400 MBB lúc 09:15:30, cùng 12 lệnh park-trim khác) — sau kỳ báo cáo, không phải sai lệch số liệu.

Ba con số trên ảnh chụp đều tái lập được từ `costPrice` broker, xác nhận cả khối lượng lẫn giá vốn
*(rà soát độc lập 10/08; ảnh chụp bị cắt mất KL của PVT nên KL được **giải ngược** từ lãi/lỗ hiển thị)*:

| Mã | `costPrice` 07/08 | KL | Giá app | Lãi/lỗ app | Giá vốn **giải ngược** | Hoà vốn app | Dư |
|---|---:|---:|---:|---:|---:|---:|---:|
| MBB | 24.850 | 1.100 | 24.100 | −933.592 | 24.948,7 | 24.950 | +98,7 |
| NCT | 86.360 | 500 | 83.100 | −1.757.276 | 86.614,6 | 86.622 | +254,6 |
| PVT | 17.100 | **3.500** | 18.350 | +4.189.371 | 17.153,0 | 17.151 | +53,0 |

PVT: giải ngược với **KL 3.500** cho giá vốn 17.153,0 — khớp giá hoà vốn app (17.151) trong vòng 2đ,
**xác nhận KL 3.500 của báo cáo là đúng** (PVT không có cổ tức nên giá vốn không đổi). Phần dư
**+53 đến +255đ/cp (0,30–0,40% giá vốn)** ở cả ba mã là **chi phí giao dịch trọn gói** (phí mua +
phí/thuế bán ước tính) trong quy ước `breakEvenPrice` của app — **không phải cổ tức**: nó cùng dấu và
cùng bậc ở cả mã CÓ cổ tức (MBB, NCT) lẫn mã KHÔNG có (PVT), trong khi chênh lệch cổ tức là
1.000–8.000đ/cp, lớn hơn 20–150 lần.

### 11.3 Hai nguyên nhân gốc (khác nhau, đều đã vá)

1. **Khoảng trống phạm vi của lần sửa 02/08.** Lần đó chỉ phủ cổ tức PHÁT SINH trong cửa sổ báo cáo.
   Báo cáo tuần này dùng `cum_dividend_excl` (cột của `daily_nav_snapshot.py`) làm tín hiệu — cột đó
   đo đúng cái nó phải đo (cổ tức chưa settle **trong tuần**, phục vụ kế toán NAV/tiền của tuần) và
   trả về 0 hoàn toàn chính xác. Sai ở chỗ **dùng nó để trả lời một câu hỏi khác**: "vị thế đang giữ
   đã từng nhận cổ tức nào chưa". Đó là câu hỏi về LỊCH SỬ VỊ THẾ, không phải về tuần.
2. **Bình quân gia quyền không reset (LPB).** `verify_account_snapshot.py` cộng dồn toàn bộ lệnh MUA
   trong mọi lịch sử và không đặt lại khi vị thế về 0. LPB mua 900cp ngày 01/07 rồi **bán sạch**
   06/07, mua lại 900cp ngày 15/07 → lô đã tất toán vẫn bị trộn vào giá vốn của lô mới. Chỉ LPB
   (SpaceX) dính; 19 mã còn lại và toàn bộ ZaloPay khớp broker tuyệt đối. *Cập nhật 10/08 — **đã vá
   tận gốc** (job `Taylor_20260810_044215`): `verify_account_snapshot.py` nay tính giá vốn theo lô
   đang sống (`CostBook`), rút cơ sở giá vốn theo tỉ lệ khi bán bớt và **đặt về 0 khi vị thế về 0**.
   Chạy lại toàn bộ 21 mã SpaceX + 15 mã ZaloPay (mốc 07/08 và 10/08): chỉ LPB đổi số, ra đúng
   51.466,67 khớp `costPrice` broker; mọi mã khác không đổi một đồng. Số trong báo cáo này KHÔNG
   phải sửa lại — đã dùng số đúng ngay từ bản đính chính.*

### 11.4 Cơ chế chống tái diễn — `mike/bin/report_return_gate.py` (ĐÃ LIVE)

Bài học lần 1 được ghi thành **văn xuôi** (coding_guidelines §21: "phải dùng
`dividend_adjusted_return.py`") và vẫn bị áp sai lần 2. Theo §22, luật loại này phải thành **code
chặn được**:

- Chạy **tự động bên trong `send_report_email.py`** trước khi gửi; **lệch > 0,15 điểm % ⇒ exit 3, KHÔNG
  gửi**. Bỏ qua phải khai lý do tường minh (`--skip-return-gate "<lý do>"`), có in ra log.
- Dựng lại kỳ vọng từ **hai nguồn độc lập với báo cáo**: `costPrice` của broker (bắt được CẢ lỗi
  thiếu cổ tức LẪN lỗi giá vốn kiểu LPB) + cổ tức `CASH_CONFIRMED` giải từ tiền mặt broker; **không**
  đọc `verified_snapshot_*.json` (chính là nguồn đã sinh ra số sai) — tránh tự kiểm chứng chính mình.
- Quyền hưởng cổ tức tính **riêng từng tài khoản** (ca thật: ZaloPay không hưởng cổ tức MBB).
- Kiểm cả tỉ suất nằm trong **văn xuôi**, không chỉ trong bảng — lỗi ZaloPay tuần này nằm ở một câu văn.
- **Kết quả kiểm chứng ngược:** chạy trên chính bản báo cáo sai → chặn đúng **9/9** sai sót thật;
  chạy trên bản đã sửa → **PASS**. Selfcheck riêng của cổng: **24/24 PASS**.
- **Bản thân cổng đã bị bắt lỗi một lần trước khi được tin** *(bổ sung sau rà soát độc lập chiều
  10/08 — công bố thay vì lặng lẽ sửa)*: bản đầu của cổng **chặn oan chính báo cáo đã sửa đúng**.
  Nguyên nhân: bảng tóm tắt của mục ĐÍNH CHÍNH nằm trong khối trích dẫn (`> | … |`), bộ đọc chỉ bỏ
  qua dòng bảng bắt đầu bằng `|` nên đọc nhầm thành văn xuôi, rồi bắt lỗi đúng các con số **CŨ (sai)**
  mà mục đính chính **buộc phải nhắc lại** để minh bạch. Đã vá hai lớp: bóc dấu trích dẫn trước khi
  phân loại bảng/văn xuôi, và thêm luật **"cũ → đúng" theo từng dòng** (một dòng có ít nhất một tỉ
  suất khớp kỳ vọng thì các số còn lại của mã đó trên chính dòng ấy là số đối chiếu lịch sử). Luật này
  **không tạo lỗ hổng**: muốn lách phải in con số ĐÚNG ngay cạnh — tức là đã công bố đúng. Nếu không
  vá, cổng sẽ chặn vĩnh viễn mọi báo cáo có đính chính và nhanh chóng bị bỏ qua như báo động giả.
- **Phạm vi cổng (nói thẳng, không cắt âm thầm):** chỉ phủ tỉ suất của **vị thế đang giữ cuối kỳ**.
  Bảng lãi/lỗ ĐÃ THỰC HIỆN (Mục 3.2) nằm ngoài — cổng in rõ số dòng nó không phủ, và dòng TỔNG kỳ
  vọng của từng tài khoản để người soạn đối chiếu tay.

---
*Báo cáo tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu sàn (DNSE API) và cơ sở
dữ liệu thị trường (BigQuery). Người phụ trách quỹ rà soát trước khi phát hành cho nhà đầu tư.*
