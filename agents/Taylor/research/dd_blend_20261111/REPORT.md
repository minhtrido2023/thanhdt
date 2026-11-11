**KẾT LUẬN:** Theo tiêu chí KHOÁ TRƯỚC (K3n), w* = 0 ở cả 4 chân trời, tức hỗn hợp **KHÔNG vượt** baseline production.
Tuy nhiên chính K3n có lỗi thiết kế, tôi chỉ phát hiện sau khi thấy số (§2). Phần hậu kiểm nằm NGOÀI prelock, nên chỉ có
giá trị **gợi ý**: **w = 0,5 hằng số** (dải 0,5–0,8) giảm sai số tuyệt đối (AEdm) 0,13–0,20 log (18–29%) và nhân β hội tụ
lên 2,3–2,7 lần, CI loại trừ 0 trên OOS ở cả 12/24/36/60 tháng. **Dữ liệu KHÔNG ủng hộ** giả thuyết "lợi nhuận đúng
hơn ở ngắn hạn, dòng tiền đúng hơn ở dài hạn": w tốt nhất không đổi theo chân trời. Đề xuất: DD trình bày V_ngắn,
V_dài và V_hài hoà với w=0,5, kèm cờ phân kỳ. Muốn wire vào engine thì cần một prelock mới chấm forward.

Job Taylor_20261111_040113 · 2026-11-11 · Taylor · CHỈ NGHIÊN CỨU (không sửa dcf_valuation.py, skill, dd_price_zones hay moat_tags).

## 0. Mẫu, định nghĩa, và 3 điểm quant-skeptic yêu cầu sửa
- **Mẫu chính:** universe_pit, không-tài-chính, rating_8l ≤ 3, as-of cuối quý 2016Q1–2025Q4, có cả V_ngắn > 0 lẫn
  V_dài > 0. Ra **4.128 dòng · 386 mã · 40 quý**. Thêm 2.047 dòng chỉ có V_ngắn (FCFE ≤ 0 hoặc trượt cổng CFO) và
  323 dòng chỉ có V_dài: nền lợi nhuận phủ rộng hơn hẳn.
- **V_dài** = engine production (FCFE 3 năm, `domestic_v2`, cap_rf). Tái dựng vector hoá khớp engine với độ lệch
  tối đa 0,0. Đã thử FCFE 5 năm và loại theo luật khoá trước: IQR log nhỏ hơn (1,26 so với 1,33) nhưng K3n36 kém
  hơn (1,165 so với 1,138).
- **V_ngắn** = NI_chuẩn hoá × (1 − g/ROE), dùng cùng r, g_exp, g_T của engine. NI_chuẩn hoá là trung vị TTM của 3
  năm gần nhất (PIT). ROE = ROE3Y vendor. Tỉ lệ tái đầu tư g/ROE cắt trong [0, 1].
- **Fade ROIC→Ke theo moat và luật dự án mới NPV=0: KHÔNG kiểm định được**, vì moat_tags là nhãn hiện tại, không có
  lịch sử PIT. Trong backtest, V_dài là engine thuần, không thưởng moat.
- **(1) Share-basis, đã sửa.** So sánh ở đơn vị VND: V là giá trị vốn chủ, MC0 = Price_asof × số CP fiinprox tại
  đúng ngày as-of (chuỗi neo ex-right; registry ghi là đúng cho câu hỏi "vốn hoá tại ngày t"). Mã ngoài fiinprox
  (2,0% số dòng) thì quy giá về hệ CP của quý fin. **6,1%** số dòng lệch > 5% so với cách cũ. Kết luận cũ không
  đổi: K3a cũ 1,009 → 1,007; FV/P trung vị 1,21 → 1,19. Chạy lại với chỉ dòng có fiinprox (350 mã) cũng cho cùng
  lựa chọn (w*=0 mọi N; PBO 0,17).
- **(2) K3 trung lập drift.** K3n_N = median|log(MC0·TR_N / (V·(1+r)^{N/12}))| ÷ median|log(MC0/V)|, trong đó TR là
  tổng lợi suất (gồm cổ tức) và V tiến theo r. Chỉ số phụ K3u: V cập nhật tại t+N so với vốn hoá giá-thuần tại t+N.
- **(3) Nhãn.** CI chứa 1 (với K3) hoặc chứa 0 (với Δ) thì ghi "chưa kết luận".

## 1. Kết quả THEO PRELOCK (tiêu chí chính)
K3n với CI95 bootstrap cụm mã (B=1000; CI cụm quý cho cùng kết luận). Lựa chọn trên IS và chấm trên OOS (2020+).

| N | OOS n/mã | w=0 (production) | w=1 (LNST) | w=0,5 | Δ(chọn − LNST) | Δ(chọn − 0,5) |
|---|---|---|---|---|---|---|
| 12 | 2.704/330 | 1,036 [0,99–1,09] | 1,024 [0,97–1,09] | 1,023 [0,96–1,10] | [−0,07; 0,08] | [−0,05; 0,07] |
| 24 | 2.254/299 | 1,043 [0,97–1,12] | 1,104 [1,01–1,21] | 1,063 [0,97–1,17] | [−0,17; 0,05] | [−0,10; 0,05] |
| 36 | 1.819/275 | 1,057 [0,97–1,16] | 1,177 [1,04–1,31] | 1,113 [0,99–1,23] | [−0,25; 0,03] | [−0,14; 0,05] |
| 60 | 777/184 | 1,274 [1,11–1,49] | 1,320 [1,10–1,55] | 1,409 [1,18–1,62] | [−0,30; 0,23] | [−0,31; 0,08] |

- **w*_IS = 0 ở cả 4 N.** G (hình học) và B (w theo chất lượng lợi nhuận q1/q2) trên IS đều dồn về w=0 (B chọn
  w_lo=w_hi=0). C (lấy min(V_ngắn, V_dài) khi phân kỳ) cho IS kém hơn và trung vị V/P 0,74–0,79, sát hoặc dưới ngưỡng
  0,75. **Không cấu trúc nào thay được A.** Kết luận theo prelock: **KHÔNG vượt baseline** (mọi CI của Δ đều chứa 0).
- Hội tụ theo K3n: **không mức w nào** có CI trên < 1. Ở 12–36 tháng là "chưa kết luận"; ở 60 tháng tất cả > 1 có ý
  nghĩa, tức khoảng cách giá–V đã trung lập drift vẫn GIÃN ra. K3u (V cập nhật tại t+N) thì < 1 ở 60 tháng
  (0,75–0,81), nghĩa là giá và V đương thời có gặp nhau.
- Walk-forward phụ (IS 2016–21 / OOS 2022+): w*=0 ở N 12/24/36. LOYO: N 24/36/60 luôn ra 0; N=12 dao động 0–0,8
  (không ổn định). PBO (CSCV 70 cách chia, 72 trial, N=36) = **0,11**.
- **H1 theo prelock: KHÔNG ủng hộ** (w* = 0 ở mọi N, không có độ dốc theo chân trời).

## 2. Vì sao K3n là tiêu chí SAI để so các V khác nhau (phát hiện SAU khi thấy số)
K3n là tỉ số mà mẫu số là khoảng cách ban đầu của **chính V đó**. Một V vốn đã gần giá hơn có mẫu số nhỏ hơn, nên bị
phạt dù sai số tuyệt đối nhỏ hơn. Ví dụ N=36, OOS: w=0 có |gap₃₆| trung vị 0,699 và |gap₀| 0,661 (suy ra
0,699/1,057). w=0,5 có |gap₃₆| **0,528** (nhỏ hơn 24%) và |gap₀| 0,474, nên tỉ số 1,113 lại "xấu hơn". K3n đo "mỗi V
tự đóng được bao nhiêu phần khoảng cách của nó", không đo "V nào đặt tâm gần nơi giá sẽ tới". Đây là lỗi thiết kế
prelock của tôi. Tôi **không** sửa kết luận chính thức ở §1. Mọi thứ ở §3 là hậu kiểm.

## 3. HẬU KIỂM (ngoài prelock, +88 trial): sai số tuyệt đối và β
AE = median|log(MC0·TR_N/(V(1+r)^{N/12}))|. AEdm giống AE nhưng drift lấy theo trung vị log TR của cùng quý as-of (bỏ
drift chung của thị trường). β là hệ số dốc của log TR_N theo log(V/MC0). Số OOS:

| N | w | AE | AEdm | β | Spearman | chạm khi V<P |
|---|---|---|---|---|---|---|
| 12 | 0 · 0,5 · 0,8 · 1 | 0,71 · 0,49 · 0,42 · 0,45 | 0,69 · 0,49 · 0,43 · 0,46 | 0,05 · 0,14 · 0,17 · 0,12 | 0,13 · 0,22 · 0,26 · 0,25 | 0,18 · 0,26 · 0,29 · 0,24 |
| 24 | 0 · 0,5 · 0,8 · 1 | 0,70 · 0,51 · 0,48 · 0,49 | 0,70 · 0,53 · 0,46 · 0,50 | 0,06 · 0,16 · 0,20 · 0,16 | 0,13 · 0,20 · 0,25 · 0,26 | 0,24 · 0,35 · 0,39 · 0,34 |
| 36 | 0 · 0,5 · 0,8 · 1 | 0,70 · 0,53 · 0,50 · 0,54 | 0,68 · 0,53 · 0,48 · 0,53 | 0,06 · 0,14 · 0,18 · 0,14 | 0,12 · 0,18 · 0,23 · 0,23 | 0,30 · 0,42 · 0,46 · 0,40 |
| 60 | 0 · 0,5 · 0,8 · 1 | 0,86 · 0,71 · 0,64 · 0,63 | 0,75 · 0,61 · 0,56 · 0,58 | 0,08 · 0,18 · 0,22 · 0,16 | 0,14 · 0,20 · 0,24 · 0,21 | 0,29 · 0,45 · 0,52 · 0,47 |

Δ so với w=0 trên OOS, CI95 cụm mã (B=1000):

| N | w=0,5: ΔAEdm | w=0,5: Δβ | w=0,8: ΔAEdm | w=0,8: Δβ |
|---|---|---|---|---|
| 12 | [−0,24; −0,15] | [+0,07; +0,11] | [−0,33; −0,21] | [+0,09; +0,15] |
| 24 | [−0,23; −0,12] | [+0,07; +0,14] | [−0,31; −0,16] | [+0,10; +0,19] |
| 36 | [−0,21; −0,09] | [+0,05; +0,12] | [−0,29; −0,12] | [+0,07; +0,18] |
| 60 | [−0,24; −0,06] | [+0,03; +0,20] | [−0,32; −0,07] | [+0,02; +0,27] |

- **Chọn trên IS:** cực đại β cho w=**0,5** (N 12/24/36) và 0,6 (N 60). Cực tiểu AEdm cho w=**0,8** ở cả 4 N. Không
  có độ dốc theo chân trời ⇒ **H1 bị bác** ở cả hai thước đo.
- Pha trộn tốt hơn **cả hai** nền thuần. Trên IS, w=1 gần như không có thông tin (β 0,00–0,06) và w=0 yếu (β
  0,02–0,10); w=0,5 cho β 0,03–0,17. Hai nền nhiễu theo những cách khác nhau, nên trộn lại có lợi.
- **Không V nào dự báo giá tốt hơn chính giá hiện tại:** AEdm của V(0,5) lớn hơn của "V=giá" thêm 0,12–0,36 log, CI
  loại trừ 0. V là giá trị, không phải dự báo giá N tháng. β 0,14–0,22 nghĩa là sau 1–5 năm giá chỉ đi được khoảng
  15–20% quãng đường log về phía V.
- **Vì sao đề xuất 0,5 chứ không 0,8:** AE thưởng cho V nằm gần nơi giá sẽ tới, tức là "để thị trường dẫn". Đó đúng
  là điều user muốn tránh cho góc nhìn dài hạn. β (cực đại tại 0,5 trên IS) ít bị thiên lệch đó hơn, và 0,5 cũng là
  prior không fit. Thêm nữa: Spearman trên IS ở N=36 phẳng ~0,15 tới w=0,5 rồi giảm (0,11 ở 0,8; 0,05 ở 1); chỉ OOS
  tăng theo w. Vì vậy không nên đẩy w lên cao.
- **Mức:** trung vị V/P 1,08 (IS) / 1,10 (OOS) với w=0,5, nằm trong [0,75; 1,25]. Không tune r/g.

## 4. Cấu trúc B, C và cờ phân kỳ
- **B (w theo chất lượng lợi nhuận):** theo prelock, trên IS không cải thiện gì (dồn về w=0). Hậu kiểm không thử lại
  B ⇒ chưa có bằng chứng cho việc w phụ thuộc chất lượng lợi nhuận.
- **C (cờ, mô tả, V=0,5):** D = |ln(V_ngắn/V_dài)|. Có cờ khi D > ln2 ở **46%** số dòng, D > ln3 ở **29%**. Dòng có
  cờ có sai số lớn hơn rõ: AEdm 0,60–0,73 so với 0,43–0,50 ở dòng không cờ. Tuy nhiên Δβ (không cờ − có cờ) có CI
  chứa 0 ở mọi ô (ví dụ N=36 OOS: [−0,05; +0,19]). ⇒ Cờ báo **độ bất định cao**, không báo "sẽ không hội tụ". Dùng cờ
  để MỞ RỘNG vùng và bắt buộc giải thích, không dùng để đổi công thức tâm (C-min đã trượt).

## 5. Ngành (mô tả, ALL)
Trung vị V/P theo nhóm của V_dài so với V_ngắn: BĐS 1,67 / 0,90 · Tài nguyên-chu kỳ 1,50 / 0,92 · Tiện ích 1,53 / 0,94 ·
XD-VLXD 1,10 / 1,02 · Công nghiệp khác 1,16 / 0,99 · Tiêu dùng-bán lẻ 0,88 / 1,00 · Khác 0,72 / 0,85. Như vậy **FCFE
lệch mức theo ngành** (dải 0,72–1,67), còn nền lợi nhuận đều hơn nhiều (0,85–1,02). Đây là thêm một lý do để trộn.
w chọn theo nhóm trên IS (12 tháng: BĐS 0,8, tài nguyên 0,5, tiện ích 1,0, khác 0,6, còn lại 0) có Δ OOS so với w chung với CI
chứa 0 ở mọi nhóm, theo cả K3n lẫn N 12/36. ⇒ **Không đề xuất w theo ngành.** Nhóm công nghệ không đủ 150 dòng.

## 6. Rule mua "vốn hoá ≤ 0,85×tâm" (theo phiên, PIT, 254.739 phiên · 350 mã)
| w | % phiên kích hoạt | mã không bao giờ | mã > 80% phiên | phương sai giữa mã | Δ lợi suất 12 tháng (kích hoạt − không, trừ trung vị quý) | Δ 36 tháng |
|---|---|---|---|---|---|---|
| 0 | 47,9% | 26,9% | 28,6% | 47,7% | +0,026 [0,002; 0,059] | +0,077 [0,011; 0,162] |
| 0,5 | 47,0% | 29,1% | 23,7% | 45,3% | +0,022 [0,000; 0,052] | +0,066 [0,006; 0,149] |
| 0,8 | 41,8% | 32,3% | 16,3% | 42,6% | +0,037 [0,011; 0,065] | +0,063 [0,001; 0,149] |
| 1 | 37,1% | 37,1% | 12,3% | 40,4% | +0,018 [−0,004; 0,048] | +0,047 [−0,016; 0,139] |

Pha trộn giảm nhóm "luôn rẻ" (từ 29% xuống 24% số mã), nhưng **gần một nửa phương sai kích hoạt vẫn đến từ danh
tính mã** ở mọi w. Phần lợi suất vượt khi kích hoạt nhỏ, dương, CI sát 0 và gần như như nhau giữa các w. Vì vậy rule
0,85× là **bộ lọc biên an toàn yếu**, không phải tín hiệu thời điểm. Đổi w không làm nó mạnh hơn.

## 7. Đề xuất quy trình DD (không code; Mike + user duyệt)
1. **Trình bày 3 số trong mọi báo cáo DD:**
   - **V_ngắn (nền lợi nhuận):** LNST chuẩn hoá (trung vị TTM 3 năm, hoặc phán đoán loại một-lần có giải thích) ×
     (1 − g/ROE), cùng r, g với DCF.
   - **V_dài (nền dòng tiền):** DCF FCFE hiện hành, cộng các lớp moat-fade (chỉ thưởng, luật 11-08) và dự án mới
     NPV=0 (luật 11-03).
   - **V_hài hoà = 0,5·V_ngắn + 0,5·V_dài.** Ghi rõ "w=0,5 (dải nhạy 0,5–0,8)".
2. **Tâm DD = V_hài hoà.** Đề xuất `center_kind = "blend_w050"` cho dd_price_zones, lưu thêm `v_short`, `v_long`, `w`,
   `divergence_D`.
   - Khi V_dài không xác định (FCFE ≤ 0 hoặc trượt cổng CFO; ~1/3 mẫu) thì dùng `center_kind="earn_only"`, tâm =
     V_ngắn, và bắt buộc giải thích vì sao dòng tiền âm (chu kỳ capex hay chất lượng lợi nhuận).
3. **Cờ phân kỳ:**
   - D > ln2 (V_ngắn và V_dài lệch nhau quá 2 lần): vùng = [min, max] của hai nền, và phải giải thích nguồn chênh
     (capex chu kỳ, vốn lưu động, một-lần, OShares).
   - D > ln3: cờ "phân kỳ mạnh". Rule 0,85×tâm KHÔNG tự kích hoạt, cần Mike/user phán đoán.
4. **Rule mua 0,85×tâm dùng V_hài hoà.** Tần suất thực nghiệm ~47% phiên, gần như bằng production (48%). Ghi nhận
   đây là biên an toàn, không phải tín hiệu thời điểm (§6).
5. **Không** đổi w theo chân trời hay theo ngành; **không** tune r/g_T.
6. P3 (từ báo cáo trước) vẫn là cách duy nhất kiểm lớp phán đoán: chấm forward tâm DD có rev theo AE/β/K3u. **Prelock
   mới cho pha forward:** dùng AEdm và β (không dùng K3n tỉ số), khoá w=0,5 làm giả thuyết.

## 8. Áp thử 25 mã sổ DD (as-of 2026-11-10, CHỈ BÁO CÁO, không ghi sổ) — `out/apply_dd.csv`
Per share = V / OShares của dòng fin mới nhất. **Chưa** đối chiếu sự kiện CP sau fin_time (fiinprox chỉ có tới
2026-09-25). Có 22/25 mã ra V_hài hoà (16 mã có đủ 2 nền, 6 mã chỉ có V_ngắn). Loại: MBB, MSB (ngân hàng) và TV2 (ROE
5,4% < g ⇒ tái đầu tư 100%, V_ngắn = 0). **15/22 mã lệch > 30% so với tâm DD.** IQR log của V_hài hoà/giá là **0,87**,
của tâm DD/giá chỉ **0,36**: tâm DD vẫn bám giá hơn máy nhiều.

| Mã | Giá | Tâm DD | V_ngắn | V_dài | V_hh | V_hh/DD | Lý do lệch chính |
|---|---|---|---|---|---|---|---|
| TV1 | 20.400 | 16.740 | 68.382 | 127.694 | 98.038 | 5,86 | Cả hai nền ≫ giá. Nghi OShares/NI (TRAP OShares) ⇒ kiểm dữ liệu trước khi đọc |
| DDV | 15.200 | 15.911 | 29.229 | 68.749 | 48.989 | 3,08 | FCFE3y cao bất thường so với LNST (D=0,86, cờ) |
| DGC | 33.000 | 41.849 | 84.931 | 74.747 | 79.839 | 1,91 | Hai nền đồng thuận. DD thấp hơn do lớp phán đoán (kịch bản/pháp lý) |
| HHS | 9.990 | 13.969 | 15.352 | 35.963 | 25.657 | 1,84 | FCFE cao (D=0,85, cờ). Tâm DD ≈ V_ngắn |
| NT2 | 22.200 | 24.003 | 20.350 | 57.794 | 39.072 | 1,63 | FCFE thời khấu hao cao (D=1,04, cờ). DD ≈ V_ngắn |
| DRI | 13.100 | 15.257 | 27.746 | 20.430 | 24.088 | 1,58 | Hai nền > DD: DD chiết khấu (thanh khoản/rủi ro) |
| DCM | 33.000 | 24.326 | 37.826 | – | 37.826 | 1,55 | Chỉ V_ngắn (FCFE ≤ 0 do capex) |
| SIP | 50.100 | 54.466 | 83.997 | – | 83.997 | 1,54 | Chỉ V_ngắn (capex KCN) |
| SAS | 34.200 | 31.658 | 54.673 | 42.122 | 48.398 | 1,53 | Hai nền > DD |
| BSR | 26.250 | 17.496 | 3.471 | 21.359 | 12.415 | 0,71 | ROE 8,6% < g ⇒ V_ngắn rất thấp (D=1,82, phân kỳ mạnh); lệch 29%, sát ngưỡng |
| MVC | 13.500 | 16.241 | 8.108 | 13.114 | 10.611 | 0,65 | ROE 9% thấp ⇒ V_ngắn thấp |
| SZL | 27.700 | 25.165 | 31.011 | 1.335 | 16.173 | 0,64 | FCFE ≈ 0 vì capex mở rộng (D=3,15). Đúng ca luật NPV=0, nên DD ≈ V_ngắn là hợp lý |
| SCL | 28.000 | 21.339 | 13.644 | – | 13.644 | 0,64 | Chỉ V_ngắn |
| HPG | 21.200 | 21.338 | 12.577 | – | 12.577 | 0,59 | ROE 10,2% < g_exp 12,8% ⇒ tái đầu tư 100% ở pha 1. DD tính dự án mới theo NPV=0 |
| PVP | 18.000 | 23.099 | 15.585 | 10.021 | 12.803 | 0,55 | DD cao hơn cả hai nền máy (lớp phán đoán: tài sản đội tàu?) |
| TCH | 13.500 | 15.864 | 2.728 | – | 2.728 | 0,17 | ROE 7% < r, cổng CFO trượt. Nền máy không đại diện |

Trong lệch ≤ 30% có FPT, NNC, PVT, CSV, GAS và VGS (0,75). Hai bài học: (a) ROE thấp hơn g làm V_ngắn sụp, vì g_exp
của engine thường chạm trần ~12,8%. Đây là độ nhạy lớn nhất của V_ngắn, DD phải tự kiểm g so với ROE. (b) Nhiều ca
lệch lớn chính là ca có cờ phân kỳ, khớp với đề xuất §7.3.

## 9. Kỷ luật
- **N trials = 394**: 306 khai trong prelock (A 44, G 44, B 200, C 8, B+C 8, chọn 3y/5y 2) + 88 hậu kiểm (11 w × 4 N ×
  2 thước đo).
- PBO 0,11 (fiin-only 0,17) cho K3n. DSR không áp dụng vì metric không phải lợi suất. Không đề xuất wire engine nên
  không có cổng DSR/PBO cho wire.
- Tái lập: chạy `analyze.py` và `posthoc.py` hai lần cho cùng md5: summary `7502fab287ea64a3a1c8c5c4a49f544c`, posthoc
  `763461894c4ec7bd46f8637266bcd11e` (`out/md5_run1.txt`, `md5_run2.txt`).
- PIT: `build_panel` assert fin.time ≤ as-of, và tái dựng r/g khớp engine trên mọi dòng engine ok. Giá chỉ dùng làm
  nhãn. Không dùng profit_*, không dùng ticker_prune.
- quant-skeptic chưa chạy (Mike sẽ chạy).

## 10. Hạn chế
- Kết luận dương (w=0,5) là **hậu kiểm**: thước đo được chọn sau khi đã thấy bảng K3n và β của IS lẫn OOS. Hiệu ứng
  lớn và đồng nhất ở 4 chân trời, nhưng vẫn cần xác nhận forward.
- Không kiểm được lớp phán đoán DD (moat, NPV=0, comps, chiết khấu thanh khoản), cũng như lựa chọn "loại một-lần" thủ
  công.
- V_ngắn nhạy với g/ROE khi ROE gần g. g_exp lấy từ engine (trần 20%, shrink 0,5) nên thường ở ~12,8%.
- ROE3Y là số vendor (PIT theo fin.time; có rủi ro restate giống OShares, chưa đo). fiinprox là snapshot UNVERIFIED-PIT
  (khớp ex-date 85,7%) và dừng ở 2026-09-25, nên MCN của 2025Q3+ thiếu (chỉ ảnh hưởng K3u).
- N hiệu dụng bị ràng buộc bởi số mã (~180–330 mã mỗi ô OOS). 60 tháng OOS chỉ có as-of 2020–21 (777 dòng).

## 11. Tái lập
```
cd agents/Taylor/research/dd_blend_20261111/calc ; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY build_panel.py            # -> out/panel.parquet (~4 phút, cache local)
$PY analyze.py                # -> out/summary.json, trials.csv (prelock)
$PY analyze.py --fiin-only    # kiểm bền share-basis
$PY posthoc.py                # -> out/posthoc.json, posthoc_grid.csv (HẬU KIỂM)
$PY trigger.py ; $PY apply_dd.py
```
