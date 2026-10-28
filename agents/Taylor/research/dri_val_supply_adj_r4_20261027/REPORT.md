# DRI — định giá vòng 4: đường sản lượng dựng từ dữ liệu công bố (job `Taylor_20261027_123420`, 27/10/2026)

> Chỉ nghiên cứu: không lệnh, không wire, không pin. PREREG commit `fe9e49391` TRƯỚC khi chạy số. `python3 model.py` → `out.txt`
> (md5 `97940c0c…`, giống từng byte dưới `env -u TZ` và `TZ=America/New_York`). Hàm r1–r3 được `exec` nguyên văn từ
> `../dri_val_supply_adj_r3_20261027/model.py`, không sửa file cũ.
> Nhãn: [BCTN25] BCTN 2025 (trang PDF) · [BCTN24] BCTN 2024 (NQ HĐQT trích trong BCTN) · [BCTC3] BCTC HN Q3/26 · [UL] giả định
> chưa có nguồn · [SL] suy luận từ số công bố · [NỀN] hiểu biết ngành. **Bản chờ skeptic, không phải kết luận chốt.**

## 0. Trả lời thẳng
**Skeptic r3 đúng về hướng.** Dựng từ diện tích và lịch tái canh công bố, tổng sản lượng tự khai thác 2027–2054 chỉ còn **~227–228 nghìn t**
ở cả ba đường, so với **314 nghìn t** của đường r3 (−27%). Từ ~2036, sản lượng chỉ còn khoảng một nửa mức 2026.
Nguyên nhân: dự án tái canh chỉ có **4.081,64 ha**, tức 48% diện tích đang cạo. Phần còn lại (~4.216 ha) khi hết chu kỳ 1 không
có kế hoạch trồng lại nào được công bố.

**Tâm theo PREREG cho FV gần như sụp** (đ/cp, 60/40):

| Đường | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| r3 tâm (đối chiếu) | 10.521 | 11.863 | 13.206 | 14.548 |
| r4 NHANH (thanh lý/tái canh 2027–34) | −1.070 | −195 | 680 | 1.554 |
| r4 TRUNG BÌNH (2029–36) | 521 | 1.439 | 2.358 | 3.277 |
| r4 CHẬM (kẹt gỗ tới 2030; 2031–38) | 1.735 | 2.698 | 3.660 | 4.623 |

Con số này **chủ yếu do hai sai lệch cơ học mà chính r4 tạo ra**, không phải do sản lượng:
1. Hàm chi phí r3 (giữ theo PREREG) coi 50% giá vốn là cố định cấp công ty, tức ~212 tỷ/năm. Khoản này giữ nguyên cả khi một nửa
   diện tích đã rời sổ. SGA đã được tách riêng trong model, nên phần "cố định" trong GVHB thực chất là chi phí theo ha (chăm sóc,
   bảo vệ, khấu hao vườn).
2. C_ref của r3 chứa khấu hao vườn 34,9 tỷ/năm [BCTC3 5.8] như một chi phí tiền mặt. r4 lại trừ thêm capex tái canh tường minh,
   nên khoản đầu tư bị trừ hai lần.

**Đã hiệu chỉnh (POST-HOC, ngoài PREREG, chưa qua skeptic).** Ba thay đổi: chi phí cố định co theo diện tích cạo; cộng lại khấu hao
vườn; tiền thu gỗ thanh lý ~20,9 tr/ha (`ước lượng` từ 9T/26):

| Đường (L_tap 27, capex m7) | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| NHANH | 6.920 | 7.903 | 8.886 | 9.869 |
| **TRUNG BÌNH** | **8.058** | **9.078** | **10.097** | **11.116** |
| CHẬM | 8.906 | 9.961 | 11.015 | 12.070 |
| Lưới 27 ô (3 đường × L_tap × capex): min – trung vị – max | 3.853 – 7.871 – 10.926 | 4.705 – 8.919 – 12.057 | 5.557 – 9.771 – 13.188 | 6.409 – 10.623 – 14.319 |
| Số ô ≥ 14.400 | 0/27 | 0/27 | 0/27 | 0/27 |

- **FV trung tâm đề xuất (POST-HOC, đường TRUNG BÌNH) ≈ 9,1k – 10,1k ở mid 1,97 – 2,075.** Khoảng theo ba đường và bốn mid là 6,9k – 12,1k.
  Giá 14.400 (đóng 27/10) cao hơn FV đường TB **+79 / +59 / +43 / +30%** ở mid 1,865 / 1,97 / 2,075 / 2,18.
  **Không ô nào trong lưới 27 ô (cả tâm PREREG lẫn POST-HOC) đạt ≥ 14.400, nhưng điều này chỉ đúng KHI DRI thực hiện tái canh** (xem §9: nếu DRI hoãn/cắt chương trình, FV có thể vượt 14.400).
- **Ngưỡng giá có biên ≥ 15% (FV/1,15), bản POST-HOC:**

| | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| CHẬM | ≤ 7.744 | ≤ 8.661 | ≤ 9.578 | ≤ 10.496 |
| TRUNG BÌNH | ≤ 7.007 | ≤ 7.894 | ≤ 8.780 | ≤ 9.666 |
| NHANH | ≤ 6.017 | ≤ 6.872 | ≤ 7.727 | ≤ 8.582 |
| min lưới 27 ô | ≤ 3.351 | ≤ 4.092 | ≤ 4.832 | ≤ 5.573 |
| TB trên đường đáy RSS3 1,60 (2027–28) | ≤ 5.203 | ≤ 5.949 | ≤ 6.694 | ≤ 7.440 |

  Theo tâm PREREG (không hiệu chỉnh), ngưỡng ở đường TB chỉ còn ≤ 453 / 1.252 / 2.051 / 2.850.
  ⇒ **Vùng mua r3 "≤ 9.000" chỉ còn đủ biên 15% ở đường CHẬM/TB với mid ≥ 2,075, và chỉ ở bản POST-HOC.** Với mid 1,97, ngưỡng là ~7,9k (TB).
- **Về mid:** 1,865 và 2,075 là trung vị DANH NGHĨA của 10 năm và 5 năm. Khung thực neo **~2,18** (trung vị thực 10 năm 2,185); đọc cột mid 2,18 là cột chính theo khung thực, các cột còn lại là độ nhạy.
- **Ba trục nhạy nhất của r4** (biên độ FV quanh tâm PREREG, mid 1,97): **L_tap** 22/27/32 năm cạo: 4.0k · **capex/ha** m 4/7/10: 3.6k ·
  **tốc độ thanh lý** 2027/29/31: 2.9k · **cách xử lý chi phí cố định**: +4,3k (công ty → theo diện tích). Cả bốn đều là [UL] hoặc [SL].

## 1. Dữ liệu: cái gì CÔNG BỐ, cái gì SUY LUẬN
| Hạng mục | Công bố | Suy luận / bất định |
|---|---|---|
| Diện tích cạo | KH26 13.800 t / 1,69 t/ha [BCTN25 tr.46] | ⇒ **8.165,7 ha**. Đối chiếu: 2025 15.152,83/1,81 = 8.371,7 [tr.40]; 2024 11.116/1,34 = 8.295,5 [BCTN24]; FSC 6.148,03/0,7407 = 8.300,3 [tr.6]; EUDR "kinh doanh" 8.299,83 [BCTN24 tr.32]; KH25 khai thác 8.201,66 [BCTN24 tr.56]. Các nguồn khớp trong ±2,5%. |
| Tổng cao su | 8.592,3 ha [BCTN25 tr.20] | không cạo 426,6 ha = KTCB tái canh 2025–26 (132,33) + phần khác |
| Năm trồng / tuổi | **KHÔNG có bảng.** Chỉ có mốc "2015: 80% diện tích đã khai thác" [tr.6] | Năm mở cạo: 80% trải 2011–15, 20% trải 2016–18 (trồng ~2004–11), ±2 năm |
| Nguyên giá / khấu hao vườn | NG 567,43 tỷ, HMLK 316,69 (55,8%), GTCL 250,74, KH 9T 26,20 tỷ [BCTC3 tr.21] | Theo tốc độ hiện tại, GTCL về 0 sau ~7,2 năm (~2034). NQ HĐQT yêu cầu xin Lào cho "trích khấu hao hợp lý để khi thanh lý GTCL ~0" [tr.58] ⇒ cho thấy **ý định thanh lý sớm hơn lịch khấu hao hiện tại**. Phương pháp/thời gian khấu hao: chưa thấy |
| Tô nhượng | thoả thuận 19/11/2004; "tầm nhìn 2054"; tái canh "phù hợp thời hạn tô nhượng" [tr.26, 49, 51] | Văn bản thời hạn chưa thấy; giữ END = 2054 như r3 |
| Tái canh | 2025: 94,56 ha [BCTN24 tr.55]; 2026: 37,77 ha [tr.46]; dự án 4.081,64 ha (NQ 01/2025) [tr.57]; thanh lý hàng loạt chờ liên doanh nhà máy gỗ [tr.39, 49] | 132,33 ha của 2025–26 thuộc dự án [UL]. Không có lịch theo năm ⇒ 3 cửa sổ 8 năm (2027/2029/2031) |
| Phần không tái canh ~4.216 ha | Có cam kết khoanh nuôi tái sinh rừng phần đất quy hoạch Rừng bảo tồn Đông Huê Sáo khi hết chu kỳ 1 [tr.35] (diện tích không nêu) | Rời sổ không trồng lại khi tới năm mở cạo + L_tap, L_tap ∈ {22, 27, 32} |
| Đời kinh tế | không công bố | L_tap 27 năm cạo [NỀN/UL] |
| Capex tái canh | chăm sóc KTCB KH25: 9.542,65 tr / 387,04 ha = **24,655 tr/ha/năm** [BCTN24 tr.57] | m × 24,655 tr/ha, m ∈ {4, 7, 10} = 98,6 / 172,6 / 246,6 tr/ha, rải 7 năm [UL đối xứng]. Dự toán dự án chưa thấy. **Đã kiểm lại với PDF BCTN 2024 tải từ dri.com.vn (`src/BCTN2024.pdf`, không commit): trang PDF 57, mục 3.3.1 "Cao su 9.542,65 triệu đồng, với diện tích 387,04 ha, chi phí đầu tư bình quân là 24.655.477 đồng/ha" — KHỚP** (9.542,65/387,04 = 24,655). Lưu ý đây là chi phí chăm sóc KTCB bình quân KH 2025 của vườn đang KTCB (nhiều tuổi), không phải dự toán trồng mới. |
| Gỗ thanh lý | NQ giá sàn 12/2025 (không có số) [tr.59]; 9T/26 thu 1,13 tỷ trên NG 3,58 tỷ [BCTC3] | ~54 ha ⇒ ~20,9 tr/ha (`ước lượng`) |
| Năng suất cây mới | không công bố | mở cạo năm 7 sau trồng; năm 1/2/3 = 0,9/1,2/1,5, sau đó 1,69 [UL/NỀN] |
| Lão hoá cây cũ | — | giữ đúng r3: −2%/năm từ 2030 |

## 2. Đường sản lượng (tấn, tự khai thác, L_tap 27; out §2)
| | 2026 | 2028 | 2030 | 2032 | 2034 | 2036 | 2038 | 2040 | 2045 | 2054 | Σ2027–54 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r3 tâm | 14.000 | 14.000 | 13.720 | 13.177 | 12.655 | 12.154 | 11.672 | 11.210 | 10.133 | 8.449 | 314.023 |
| NHANH | 13.800 | 12.131 | 10.254 | 8.362 | 7.072 | 8.187 | 8.660 | 8.305 | 6.898 | 6.898 | 228.489 |
| TRUNG BÌNH | 13.800 | 13.800 | 11.889 | 9.933 | 8.136 | 6.854 | 6.991 | 6.636 | 6.804 | 6.898 | 227.906 |
| CHẬM | 13.800 | 13.800 | 13.524 | 11.503 | 9.645 | 7.858 | 5.658 | 4.968 | 6.172 | 6.898 | 226.884 |
| TB, L_tap 22 / 32 | | | | | 5.593 / 8.136 | 2.895 / 6.854 | | 3.669 / 9.375 | 6.804 / 9.486 | | 196.836 / 254.900 |

Capex tái canh (m7) cả dự án là 698,8 tỷ thực, đỉnh 85,2 tỷ/năm. Để so sánh, mức "10% tái đầu tư" r3 trừ năm 2030 (mid 1,97, đường TB)
chỉ là 6,6 tỷ ⇒ r3 không hề chứa khoản tái canh cỡ này.

## 3. Cầu nối r3 → r4 tâm PREREG (đường TB; cộng dồn; mỗi mid riêng, PEAK và MID cùng một mid, không ghép mid; out §5)
| Bước | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| r3 tâm | 10.521 | 11.863 | 13.206 | 14.548 |
| mức 14.000 → 13.800 (KH26) | −376 | −400 | −424 | −448 |
| hết chu kỳ 1 theo cohort (L27), chưa tái canh | −5.090 | −5.464 | −5.838 | −6.212 |
| thanh lý khối tái canh 2029–36 | −4.259 | −4.572 | −4.885 | −5.198 |
| sản lượng cây tái canh | +3.908 | +4.196 | +4.483 | +4.770 |
| capex tái canh m7 | −4.184 | −4.184 | −4.184 | −4.184 |
| **r4 tâm PREREG** | **521** | **1.439** | **2.358** | **3.277** |
| POST-HOC (a) cộng lại KH vườn | → 3.877 | → 4.796 | → 5.714 | → 6.633 |
| + chi phí cố định co theo diện tích | → 7.116 | → 8.135 | → 9.155 | → 10.174 |
| + gỗ thanh lý ~20,9 tr/ha | → **8.058** | → **9.078** | → **10.097** | → **11.116** |
- Hai bước "hết chu kỳ 1" và "thanh lý" phóng đại vì chi phí cố định ~212 tỷ/năm vẫn chạy khi sản lượng → 0. Đây chính là sai lệch (1) ở §0.
- **Tái canh làm mất giá trị trong model, không "gần hoà vốn"** (POST-HOC, đường TB, L27, m7, mid 1,97; out §12):
  thanh lý khối rồi trồng lại với capex m7 là **9.078**; thanh lý khối nhưng không trồng lại là **10.939** ⇒ trồng lại mất **−1,9k**/cp.
  Cả chương trình (thanh lý + trồng lại + capex) so với không thanh lý gì (13.096) mất **−4,0k** (13.096 → 9.078). Capex m7 một mình là −4,2k (13.261 → 9.078).
  Lệnh gọi ban đầu ghi ~−4,3k/13.405 cho mốc "không thanh lý gì"; tôi đo được 13.096 (L27, không capex), chưa đối chiếu được cách skeptic dựng 13.405.
  - **Mốc 2054 không phải nguyên nhân**: kéo dài tô nhượng tới 2064 chỉ +0,2k (9.078 → 9.295).
  - **Nguyên nhân là biên mỗi ha không trả nổi capex.** Biên ròng ha cây mới trưởng thành @mid 1,97 theo hàm chi phí r3 là
    22,9 tr/ha/năm trước thuế, 18,5 sau thuế `[SL]` (skeptic đo ~14–17). Capex m7 là 172,6 tr/ha rải 7 năm (PV 136 tr/ha ở r thực 8,74%),
    trong khi PV biên sau thuế 22 năm cạo chỉ 108 tr/ha, và con số này đã bỏ qua 3 năm năng suất thấp nên còn là cận trên.
  - Vì vậy đường CHẬM > TB > NHANH: hoãn capex có lợi hơn mất sản lượng cây cũ. Model không có rủi ro cây già sụp nhanh hơn −2%/năm.

## 4. Biến thể và dòng riêng (không vào tâm; out §6, §7)
| Biến thể quanh tâm PREREG TB | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| quỹ ĐTPT tự tài trợ (tiền −96,97 tỷ, capex −96,97 tỷ đầu tiên) | 59 | 978 | 1.897 | 2.815 |
| quỹ ĐTPT trừ thẳng [ĐẾM HAI LẦN, chỉ để xem] | −804 | 115 | 1.033 | 1.952 |
| capex THAY 10% tái đầu tư (0,9 → 1,0) | 646 | 1.665 | 2.685 | 3.705 |
| chi phí cố định co theo diện tích | 4.676 | 5.695 | 6.714 | 7.734 |
- **Quỹ ĐTPT 96,97 tỷ** [BCTC3 mã 418]; BCTN nói trích "nhằm đảm bảo kế hoạch tái canh" [tr.51]. Quỹ là một dòng trong VCSH, tiền
  tương ứng đã nằm trong tiền ròng ⇒ tâm không trừ thêm. Nếu coi quỹ là tiền bị khoá để tự tài trợ thì chỉ mất giá trị thời gian
  (~−460 đ/cp).
- **Mua ngoài 2.000 t/năm** (biên gộp [UL] 0 / 1,5 / 3,0 tr/t): **+0 / +226 / +452 đ/cp**. Đây là biên trên mủ mua, không phải sản lượng
  tự có. Nó chỉ bù được định phí chế biến (BCTN tr.50), không bù được diện tích mất.
- **Sầu riêng Lào 238,12 ha tới 2030** [UL: năng suất 5,35 t/ha lấy từ CNC 760 t / 142,17 ha; biên 8,581 tr/t KH26; ra quả năm 5–7]:
  LN gộp đỉnh 10,9 tỷ/năm, PV +446 đ/cp. Trừ capex trồng 178,5 tr/ha (chưa gồm chăm sóc KTCB) ⇒ ròng **+176 đ/cp**. Không cộng vào FV.
  Khoản này cũng không bù cho cao su: quy mô < 3% diện tích, và đất lấy từ điều/cao su.

## 5. Self-check (out §0–§1)
- Tái lập 10.878 / 11.031 (model_q3), 14.301 (r1), hàng r2 11.061 / 12.481 / 13.901 / 15.321, **r3 tâm 10.521 / 11.863 / 13.206 / 14.548**
  (hàm `fv4` của r4 với hàm sản lượng r3; ngoài ra assert `fv4 ≡ fv1` r3 tới 1e-6).
- Mốc đường PHẲNG 14.000 t tới 2054 (không lão hoá): 13.967 / 15.563 / 17.159 / 18.755. Đây là mức skeptic gọi là lạc quan; tâm r3
  đã thấp hơn nhờ giả định −2% từ 2030.
- 13.800 / 1,69 = 8.165,7 ha, khớp các nguồn diện tích trong ±2,5% (§1).
- Mọi hằng số trong `model.py` đều có chú thích nguồn hoặc nhãn [UL]/[SL] ngay cạnh.

## 6. Hạn chế
- **Tâm PREREG và bản POST-HOC lệch nhau 7–8k đ/cp.** Bản POST-HOC sửa các sai lệch có cơ chế rõ, nhưng nó được chọn SAU khi đã thấy
  kết quả ⇒ cần skeptic xét riêng từng hiệu chỉnh (a), (b) và farea.
- Hiệu chỉnh (a) là cận trên: giả định khấu hao chu kỳ 2 tiếp tục tạo lá chắn thuế, và toàn bộ khấu hao vườn là phi tiền mặt.
  Farea cũng là cận trên: giả định toàn bộ phần f là chi phí theo ha; định phí nhà máy thực tế có tồn tại (BCTN tr.50).
- Model không có quyền dừng hay thu hẹp bộ máy khi lỗ (giống r3). Không có phase 2 tái canh cho ~4.216 ha còn lại: **đây là giả định CÓ LỢI cho FV** (§10: thêm phase 2 làm FV giảm ~1,5k). Nếu DRI có phase 2
  thì đường sản lượng sau 2040 cao hơn nhưng capex cao hơn nhiều, và model cho giá trị ròng âm.
- Phân bố tuổi là suy luận từ một mốc duy nhất (2015: 80%).

## 7. Dữ liệu cần lấy (BCTC Q3 chi tiết ~30/10 hoặc hỏi DRI), xếp theo mức đổi FV
1. **Cơ cấu giá thành theo yếu tố và theo ha:** định phí nhà máy so với chi phí/ha (CP SXKD theo yếu tố trong thuyết minh). Đây là chỗ
   lệch ±4,3k giữa tâm PREREG và farea.
2. **Dự án tái canh 4.081,64 ha** (NQ 01/2025 và hồ sơ dự án): suất vốn/ha, nguồn vốn, lịch theo năm. Thêm: có phase 2 cho ~4.500 ha
   còn lại không, hay đất trả lại / thành rừng (Đông Huê Sáo). Trục capex dao động ±1,8k; L_tap −2,5k/+1,5k @1,97.
3. **Bảng diện tích theo năm trồng / năm mở cạo** và phương pháp + thời gian khấu hao vườn (thuyết minh chính sách kế toán BCTC năm).
4. **Văn bản tô nhượng:** thời hạn, điều kiện gia hạn, xử lý tài sản trên đất khi hết hạn.
5. **Giá sàn gỗ (NQ 12/NQ-HĐQT 15/12/2025), kết quả đấu giá Nông trường 1, tình trạng liên doanh nhà máy gỗ / viên nén.**
6. Biên mủ mua ngoài (giá mua tiểu điền so với giá SVR10/20); năng suất thực của vườn tái canh 2025.

## 8. Cập nhật theo phản biện fundamental-skeptic (job `Taylor_20261027_154349`; code `model.py` §11–15, kết quả `out.txt`)
Chỉ THÊM code (hàm `build3`, `capex3`, `fvph`…); không đổi hàm cũ, không đổi tâm PREREG. Self-check: `build3` mặc định tái lập PH TB
8.058 / 9.078 / 10.097 / 11.116 đến 1e-6 (assert); phần `out.txt` cũ giữ nguyên từng byte; `out.txt` mới md5 `c455ba5a…`, giống từng byte
dưới `env -u TZ` và `TZ=America/New_York`. Mọi số dưới đây là POST-HOC (cấu hình farea + cộng KH vườn + gỗ thanh lý), chưa qua skeptic.

## 9. Trục "DRI thực hiện / hoãn / cắt chương trình tái canh 4.081 ha" (out §13)
FV đ/cp @ mid 1,865 / 1,97 / 2,075 / 2,18 (60/40). Cột phải: 14.400 cao hơn (+) / thấp hơn (−) FV.

| Kịch bản | 1,865 | 1,97 | 2,075 | 2,18 | 14.400 so FV @1,97 / @2,18 |
|---|---|---|---|---|---|
| T1. Thực hiện đầy đủ (TB 2029, L27, m7) | 8.058 | 9.078 | 10.097 | 11.116 | +59% / +30% |
| T2c. Không tái canh, vườn hết đời L27 | 12.057 | 13.096 | 14.134 | 15.172 | +10% / −5% |
| T2b. Không tái canh, GIỮ vườn q=1 (L99), KH vườn coi là chi phí duy trì | 10.145 | 11.463 | 12.782 | 14.100 | +26% / +2% |
| T2a. Như T2b nhưng cộng lại KH vườn (không có capex thay thế) | 13.501 | 14.819 | 16.138 | 17.457 | −3% / −18% |
| T3a. Chỉ thanh lý khối vườn thưa (q 0,5; 3.949 ha), không trồng lại, phần còn lại giữ (L99) | 13.575 | 14.734 | 15.893 | 17.052 | −2% / −16% |
| T3b. Như T3a, phần còn lại hết đời L27 | 12.035 | 12.968 | 13.901 | 14.834 | +11% / −3% |

- **Đây là đuôi trên DUY NHẤT có thể vượt 14.400.** Skeptic đo 13.225 @1,97 và 15.115 @2,18 cho "không tái canh, giữ vườn"; tôi **không tái lập
  đúng** số đó: bản của tôi nằm trong dải T2b–T2a (11.463–14.819 @1,97; 14.100–17.457 @2,18), tuỳ KH vườn có được cộng lại hay không. Chênh lệch do cách dựng
  (đời vườn, KH vườn, định phí theo ha); chưa đối chiếu từng bước với skeptic.
- Kết luận có điều kiện: **"không ô nào ≥ 14.400" chỉ đúng khi DRI thực hiện tái canh.** Nếu DRI hoãn hoặc cắt chương trình và vườn cũ vẫn cho
  1,69 t/ha với −2%/năm, FV đủ vượt giá thị trường ở mid 2,18 (và ở mid 1,97 với T2a/T3a).
- Cảnh báo cho đuôi này: T2a/T3a (L99) giả định vườn cao su không bao giờ hết đời trong khi BCTN 2025 tr.44 nói nhiều diện tích đã phải thanh lý sớm
  vì không đủ mật độ (§11). T2c (L27) là bản thực tế hơn của "không tái canh" và vẫn lệch đáng kể khỏi T1.
- NQ 01/2025 đã giao 4.081,64 ha; BCTN nói trích quỹ ĐTPT 96,97 tỷ cho kế hoạch này. Hoãn hay cắt phải là quyết định mới của HĐQT, chưa có tín hiệu công bố.

## 10. "Không phase 2" là giả định có lợi cho FV (out §14)
Mô phỏng tái canh nốt phần còn lại (~4.216 ha), trồng vào năm mỗi cohort hết L_tap, cùng KTCB 7 năm và capex m7:

| | 1,865 | 1,97 | 2,075 | 2,18 |
|---|---|---|---|---|
| TB L27, không phase 2 (tâm PH) | 8.058 | 9.078 | 10.097 | 11.116 |
| TB L27 + phase 2 | 6.521 | 7.609 | 8.697 | 9.784 |
| TB L22 + phase 2 | 5.176 | 6.210 | 7.245 | 8.279 |

Phase 2 làm FV giảm 1,47k @1,97 và 1,33k @2,18. Tâm PH hiện tại vì vậy không bi quan hơn thực tế ở trục này.

## 11. Chất lượng vườn / mật độ (q) và hai câu BCTN (out §15)
- BCTN 2025 tr.44 (rủi ro): "nhiều diện tích phải đưa vào thanh lý sớm, do không đảm bảo mật độ khai thác" (do biến đổi khí hậu, dịch bệnh).
- BCTN 2025 tr.10 (định hướng; BCTN 2024 tr.9 cùng ý): "Thực hiện lộ trình khai thác và trồng tái canh vườn cây cao su chu kỳ thứ hai,
  phù hợp với hợp đồng tô nhượng đất **và chất lượng vườn cây**".
- Hai câu cho thấy tiêu chí thanh lý là chất lượng/mật độ vườn chứ không chỉ tuổi, tức L_tap hiệu dụng có thể ngắn hơn 27 và lịch tái canh phụ thuộc vườn.
- Cách model hoá q của tôi: năng suất/ha của cây cũ = q·1,69, diện tích cây cũ = A0/q (2026 vẫn 13.800 t); cây tái canh đạt 1,69 đầy đủ.
  FV đường TB @1,97 (m7):

| | 1,865 | 1,97 | 2,075 | 2,18 | Δ so tâm @1,97 |
|---|---|---|---|---|---|
| Tâm (q 1, L27) | 8.058 | 9.078 | 10.097 | 11.116 | — |
| q 0,7, L27 | 9.539 | 10.651 | 11.762 | 12.873 | +1,57k |
| q 1, L22 | 7.049 | 7.931 | 8.813 | 9.695 | −1,15k |
| **q 0,7 + L22** | 8.375 | **9.315** | 10.254 | 11.193 | +0,24k |
| q 0,5, L27 | 10.708 | 11.880 | 13.052 | 14.225 | +2,80k |

  Skeptic đo q 0,7 = +1,37k, L22 = −1,15k, gộp = 9.185 @1,97. L22 khớp; q 0,7 của tôi cao hơn 0,2k và gộp cao hơn 0,13k (khác cách chia lại diện tích cây cũ).
  Chiều tác động: vườn thưa (q thấp) làm FV TĂNG, vì cùng 13.800 t phải gánh nhiều ha hơn nên chương trình thanh lý/tái canh thay vườn kém bằng vườn đủ mật độ.
  Bù trừ với đời vườn ngắn lại gần như triệt tiêu; gộp lại FV vẫn ~9,2–9,3k @1,97.

## 12. Hiệu chỉnh đối xứng skeptic đo (CHƯA tái lập trong model này; số của skeptic, lấy từ lệnh gọi)
Tác động lên FV @1,97 so với tâm PH:

| Hiệu chỉnh | Tác động |
|---|---|
| Định phí nhà máy KHÔNG co theo diện tích (nới lại giả định farea) | −0,4k … −0,85k |
| Thuế trên tiền bán gỗ | −0,28k |
| Lá chắn thuế sau 2034 | −0,17k |
| Chi phí bán hàng biến đổi | +0,38k |
| Năng suất cây mới 1,9 t/ha (thay 1,69) | +0,52k |

Các hiệu chỉnh ngược chiều nhau và nhỏ so với biên độ của các trục §9–11. **Kết luận: tin FV POST-HOC TB ở mức ±1k quanh 9,1k @1,97**,
tức khoảng 8,1k–10,1k; không tin vào độ chính xác hơn mức đó, và nhớ rằng khoảng này có điều kiện "DRI thực hiện tái canh theo kế hoạch".
