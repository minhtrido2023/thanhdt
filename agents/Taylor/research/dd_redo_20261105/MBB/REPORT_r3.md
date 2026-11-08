# MBB — DD REDO VÒNG 3 · 08/11/2026 · job `Taylor_20261108_164331`

Áp đính chính fundamental-skeptic 08/11 (`TOP5C_CORRECTIONS_20261108.md` mục MBB), user đã duyệt. Bản trước: `REPORT_r2.md`, `SUMMARY_r2.json`. Số trong file này lấy từ `calc_r3/run2.txt` (`$DNA_PYEXE -I calc_r3/mbb_r3.py`, chạy 2 lần, trùng byte: run.txt `1c79f8d0…`, grid `ceebe256…`, out.json `ba2b2e1f…`, SUMMARY.json `ffccfa4d…`).

## 1. Kết luận
- **Tâm 21.069 đ/cp** (sau CK 5 tỷ) · **P10 14.729 · P50 20.903 · P90 27.577** (mức kết cục, wpct mid-block, n = 45 kết cục) · giá 06/11 **19.250** (BQ `tav2_bq.ticker`) ⇒ **TRONG vùng**; giá thấp hơn tâm 8,6%; **38,6%** trọng số kết cục nằm dưới giá; kết cục thấp nhất 12.124.
- So r2: tâm **23.804 → 21.069 (−2.735, −11,5%)**; P90 35.860 → 27.577 (đuôi trên bị cắt, vì thưởng moat ngầm ở terminal bị gỡ); P10 14.444 → 14.729. Nhãn không đổi (TRONG → TRONG).
- Số của tôi tái lập đúng điểm của skeptic (21.069). P10/P90 lệch skeptic 14.775/27.488 khoảng 50–90 đ: tôi bỏ trục g_T (sau khi gỡ thưởng moat thì trục này không còn tác dụng), nên mỗi bộ 3 kết cục trùng giá trị gộp lại thành 1 khối. Phân phối kết cục giữ nguyên; chỉ phép nội suy mid-block đổi. Với trục g_T giữ lại, tôi ra 14.776/27.488 (bridge bước 4), trùng skeptic.
- Giá ngụ ý (tâm = 19.250): **Ke 14,50%** (lãi huy động 12T cần tăng ~100bp), hoặc **ROE_T kịch bản cơ sở 14,44%** (−1,56pp; ở kịch bản cơ sở ROE_T 16%, ROE 10 năm của MBB 19,8%, trung vị ngành 13,0%), hoặc cả đường ROE 2027–29 cùng ROE_T giảm 1,05pp.
- Nếu cho phép RONIC > Ke (giữ thưởng moat ngầm, trái quy ước 08/11): tâm 25.317 (bản song song A).
- Không đủ điều kiện sleeve fear-buy §2.5: không có cú sốc đặc thù, P/B ≈ 1,23x. Nhãn chỉ phản ánh định giá.

## 2. Ba con số tách bạch
| | Giá trị (sau CK) |
|---|---|
| Tâm = kỳ vọng có trọng số của lưới | **21.069** |
| P50 mức kết cục | 20.903 |
| Giá trị tại tham số trung tâm (CO_SO, ΔROE 0, MBV 0) | 20.944 |
P10 do riêng nhánh XẤU quyết định (100% trọng số kết cục quanh P10 ±5% thuộc XẤU). P90 gồm 71% TỐT và 29% CO_SO.

## 3. Kiểm từng đính chính (calc, không chép mù)
| # | Đính chính skeptic | Kiểm | Quyết định | Tác động lên tâm |
|---|---|---|---|---|
| 1 | g_RI terminal = 0 ở mọi ô (RONIC = Ke) | **ĐÚNG.** `mbb_r2.py:42` chỉ đặt g_RI = 0 khi ROE_T < Ke, mà ROE_T 14/16/18% đều > Ke 13,5%, nên RI terminal vẫn tăng 6–8%/năm vĩnh viễn. Như vậy vốn mới được ngầm giả định sinh lời trên Ke mãi mãi, mâu thuẫn với ADDENDUM_5F (moat NARROW, không bền). Theo quy ước user 08/11, moat không bền thì không được thưởng, nhưng cũng không bị trừ: ROE_T vẫn giữ 14/16/18% trên sổ sách cuối 2029 (không ép về trung bình ngành); chỉ phần vốn tăng thêm sau 2029 sinh lời đúng bằng Ke. | Áp | **−3.638** (tâm 20.183; trùng số skeptic) |
| 1b | Trục Δg mất tác dụng | **ĐÚNG.** Sau đính chính 1, g_T chỉ còn đi vào terminal với g_RI = 0 ⇒ ba điểm của trục cho cùng một giá trị. | Bỏ trục (n 135 → 45); bản song song A giữ trục | 0 |
| 2 | Trọng số kịch bản 0,35/0,45/0,20 → 0,275/0,45/0,275 | **ĐÚNG.** Ba nhánh của Bobby (ADMIN 0,45 / CYCLICAL 0,35 / STRUCTURAL 0,20, `sector_read_ngan_hang_20261031.md:169-171`) là các loại chế độ, không phải các mức xấu–cơ sở–tốt. STRUCTURAL là nhánh **bất lợi** (chi phí vốn và nhu cầu vốn cấp 1 cao lên vĩnh viễn), nhưng r2 lại gán xác suất 0,20 của nó cho nhánh TỐT. Đồng thời ROE_T ở mọi nhánh đã được hạ dưới lịch sử vì Basel III/TT14 (`mbb_calc.py:133`), tức STRUCTURAL đã được tính một lần trong ROE_T; gán nó thêm vào trọng số là đếm hai lần. Về độ lớn, độ lệch của hai nhánh so với nhánh cơ sở gần đối xứng (XẤU −4.308 / TỐT +4.359, tính trước CK ở tham số trung tâm), nên khi không có thông tin thêm, trọng số đối xứng là mặc định đúng. | Áp | **+643** (skeptic +650) |
| 3 | Trục MBV đối xứng ±3.500; điểm 15.688 chuyển thành cờ HARD ABANDON | **ĐÚNG.** Điểm 15.688 là lỗ luỹ kế năm 2024 [WEB], không có văn bản nào ghi nghĩa vụ MB phải bù. Theo luật 03/11, khoản này không đủ cơ sở để vào base hay lưới chính. | Áp: −3.500/0/+3.500 với trọng số 0,25/0,50/0,25 [UL]. Cờ: CO_SO + 15.688 = 18.969 | **+243** (skeptic tính riêng +278; tôi đo sau khi đã áp 1 và 2) |
| 4 | Phải thu bán nợ 11.248 từ MBV bị mất khỏi lưới r2 | **ĐÚNG**: lưới r2 thiếu trục này và `axes_excluded` cũng không ghi. | Đưa vào `axes_excluded`, có lý do: khoản này ghi theo sổ sách, không có dữ liệu suy giảm, và chỉ có thể lệch xuống (không thu được quá sổ sách). Kèm **bản song song E** (mất 30% × xác suất 0,20 [UL]): tâm 20.983, P10 14.580, nhãn TRONG | headline 0; E −86 |
| 5 | Độ nhạy ROE_T ±2pp | Đo trên base r3: −2pp ⇒ tâm **18.742** (P10 12.617; **TRONG**; 58,6% dưới giá); +2pp ⇒ **23.396**. Trùng số skeptic (18.742 / 23.395). | Báo cáo (F/G) | — |
| 6 | LNTT Q4/25 ≈10.950 → 11.129 | **ĐÚNG.** `mbb_calc.py:106` ghi PPOP Q4/25 = 11.129 + 2.169, trong đó 11.129 là LNTT. r2 tính ngược từ LNST/0,8 nên ra số sai. | Sửa chữ: LNTT Q4/26 ngụ ý ở kịch bản cơ sở 12.000, so với Q4/25 thật 11.129 (+7,8%) | 0 |
| 7 | Giá 06/11, price_date; NPL chưa tự kiểm | Giá 06/11 = **19.250** (BQ, `calc_r3/px_mbb_r3_20261106.csv`), bằng giá 04/11. Bước 1 của bridge (giá, thanh khoản, chiết khấu thời gian) chỉ làm tâm +17. | NPL / nợ nhóm 2 / tỷ lệ bao phủ Q3/26: **chưa kiểm** (BQ không có cột; chưa đọc ảnh BCTC HN-Q3) | +17 |

Không có đính chính nào sai. Tất cả số skeptic nêu đều tái lập được (sai lệch ≤ 35 đ, do đo sau các bước trước).

## 4. Bridge r2 → r3 (cộng dồn, sau CK 5 tỷ)
| Bước | Tâm | Δ | P10 | P90 | % dưới giá | n |
|---|---|---|---|---|---|---|
| 0 r2 tái lập (giá 04/11; control trùng 23.804 / 14.444 / 35.860) | 23.804 | — | 14.444 | 35.860 | 32,3% | 180 |
| 1 giá + thanh khoản 06/11, chiết khấu từ 06/11 | 23.821 | +17 | 14.454 | 35.886 | 32,3% | 180 |
| 2 D1: g_RI terminal = 0 ở mọi nhánh | 20.183 | −3.638 | 14.454 | 26.140 | 46,2% | 180 |
| 3 D2: trọng số đối xứng 0,275/0,45/0,275 | 20.826 | +643 | 14.559 | 27.488 | 40,6% | 180 |
| 4 D3: trục MBV đối xứng ±3.500 | 21.069 | +243 | 14.776 | 27.488 | 38,6% | 135 |
| 5 bỏ trục g_T (không còn tác dụng) | **21.069** | 0 | **14.729** | **27.577** | 38,6% | 45 |

## 5. Lưới headline và các biến thể song song (sau CK 5 tỷ, giá 19.250)
Lưới gồm: kịch bản XẤU/CO_SO/TỐT (0,275/0,45/0,275) × ΔROE 2027–29 và ROE_T −3..+3pp (5 điểm đều) × MBV −3.500/0/+3.500 (0,25/0,50/0,25). Phương pháp RI: BV0 = VCSH mẹ 30/09 + LN Q4/26 theo kịch bản; payout tiền 30%; g_RI = 0.

| Bản | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **HEADLINE r3** | **21.069** | 14.729 | 20.903 | 27.577 | 38,6% | **TRONG** |
| A: RONIC > Ke (g_RI như r2) + trọng số và MBV đối xứng | 25.317 | 14.776 | 23.831 | 37.049 | 26,2% | TRONG |
| B: chỉ D1 (trọng số r2, MBV r2) | 20.183 | 14.325 | 20.090 | 26.366 | 46,2% | TRONG |
| C: D1 + D2, giữ điểm MBV 15.688 | 20.826 | 14.598 | 20.706 | 27.349 | 40,6% | TRONG |
| D: D1 + D3, trọng số r2 | 20.419 | 14.407 | 20.479 | 26.547 | 44,2% | TRONG |
| E: thêm trục phải thu MBV (mất 30%, p = 0,20) | 20.983 | 14.580 | 20.867 | 27.493 | 38,9% | TRONG |
| F: ROE_T −2pp | 18.742 | 12.617 | 18.610 | 25.050 | 58,6% | TRONG |
| G: ROE_T +2pp | 23.396 | 16.840 | 23.179 | 30.104 | 25,5% | TRONG |
| H: không trục MBV (NPV0) | 21.069 | 14.883 | 20.944 | 27.606 | 40,0% | TRONG |
| Có trục r ±1pp (0,25/0,5/0,25) | 21.145 | 14.781 | 20.863 | 28.126 | 39,1% | TRONG |
Độ nhạy của tâm theo r: −100bp 23.191 · −50bp 22.087 · +50bp 20.126 · +100bp 19.252. Ở 3c chặt (ROE → trung vị ngành), số trong ADDENDUM_5F §3 (17.677) vẫn đo trên base r2 và **chưa chạy lại trên base r3**; theo quy ước 08/11 đó chỉ là độ nhạy rủi ro.

## 6. Base so với sổ sách
MBV: base = 0 (NPV0, sổ sách; HN-Q3 tr.2 ghi MB chưa góp vốn tại 30/09). Phải thu bán nợ MBV 11.248: base = sổ sách (BCTN25; **số dư 30/09/26 chưa kiểm**). Base không có khoản nào lệch khỏi sổ sách. Mọi giả định khoá, kèm cơ sở từng cái, nằm ở `SUMMARY.json → assumptions` (khoá md5 trước khi đọc kết quả, file `calc_r3/summary_r3_extra.json`).

## 7. Thanh khoản
ADV250 349,1 tỷ, ADV60 210,5 tỷ. CK ở cỡ 5 tỷ là 0,191% theo ADV250 (0,195% theo ADV60); cỡ 5 tỷ bằng 1,4% ADV250, nằm trong vùng hiệu chỉnh của luật căn bậc hai. Cỡ sleeve 10–40 triệu nằm dưới vùng hiệu chỉnh: CK thật xấp xỉ nửa spread, chưa đo. Trước CK: tâm 21.109, P10 14.757, P90 27.630. Nhãn giống nhau ở cả hai cỡ.

## 8. Đối chiếu (không vào tâm)
- Gordon P/B (BVPS 15.594): với g = 0 (nhất quán RONIC = Ke), ROE TTM 20,7% cho 23.944 và ROE_T 16% cho 18.482. Với g 6/7% (r2): ROE TTM 30.624/32.936; ROE_T 16% 20.793/21.592.
- LNTT Q4/26 ngụ ý: XẤU 8.500 / CƠ SỞ 12.000 / TỐT 14.500, so với Q4/25 thật 11.129.

## 9. Tham số tự đặt [UL]
Trọng số kịch bản 0,275/0,45/0,275; đường ROE, ROE_T và PPOP/DP Q4 của từng kịch bản (giữ bản 31/10); biên ΔROE ±3pp với trọng số đều; trục MBV ±3.500 với trọng số 0,25/0,50/0,25; bản song song E (30%, p = 0,20); payout 30%, thuế 20%, NCI 2,5%; Y = 1.

## 10. Mốc đổi nhận định HAI chiều + HARD ABANDON
Bộ M1–M8 khoá 31/10 giữ nguyên, chấm ngày 15/02/2027 bằng BCTC Q4/26. Các số dưới đây đo trên base r3:
- **Xấu đi** (về trọng số 0,35/0,45/0,20): tâm 20.419 (bản D). Kích hoạt khi: nợ nhóm 2 HN Q4 > 20.000 hoặc nhóm 2–5 > 3,5%; bao phủ < 75%; Tier1 riêng lẻ < 8,5%; NIM Q4 (bỏ TG NHNN) < 3,85%; MB phải hỗ trợ hoặc trích lập cho MBV > 5.000 tỷ; lãi huy động 12T tăng 100bp (tâm 19.252, ≈ giá).
- **Tốt lên**: nợ nhóm 2 HN < 13.000 và bao phủ ≥ 90%; KKH tăng lại; phát hành riêng lẻ ở P/B ≥ 1,3x; LNTT Q4 ≥ 14.000 với DP ≥ 5.000; lãi huy động giảm 100bp (tâm 23.191). Trọng số nghiêng về TỐT: chưa đo trên r3.
- **HARD ABANDON**: CAR HN < 9% hoặc NHNN yêu cầu tăng vốn bắt buộc; nợ nhóm 3–5 > 3%; **có văn bản buộc MB gánh lỗ luỹ kế MBV ≥ 15.688** (CO_SO tại điểm đó = 18.969 < giá); kết luận thanh tra hoặc khởi tố liên quan tín dụng BĐS hay bên liên quan.
- Ngưỡng nhãn: DƯỚI vùng nếu giá < 14.729; TRÊN vùng nếu giá > 27.577.

## 11. WARNING pháp lý / quản trị
Giữ nguyên 11 cờ MỞ của `REPORT_r2.md` §9 (MBV; ưu đãi MBV; nợ ngoại bảng/TT02; bên liên quan và top KH; CAR/CET1; sở hữu chéo; nghị quyết phát hành 2026 chưa đọc; lỗ phái sinh suy luận; quota tín dụng; kiểm toán; câu "chưa thấy xử phạt" dựa trên tra cứu 31/10). Thêm 3 cờ: (12) NPL, nợ nhóm 2, tỷ lệ bao phủ Q3/26 **chưa kiểm**; (13) số dư phải thu MBV tại 30/09/26 chưa kiểm; (14) pháp lý sau 05/11 chưa quét lại (tra cứu gần nhất: DD 31/10/2026).

## 12. LOCK md5
`calc_r3/LOCK_md5.txt` gồm: `mbb_r3.py`, `px_mbb_r3.sql`, `px_mbb_r3_20261106.csv`, `r2common.py`, `bq_px_liq_20261104.csv` (control), `_shared/wpct.py`, `MBB/calc/mbb_r2.py`, `MBB/calc/mbb_redo.py`, `dd_MBB_20261031/calc/mbb_calc.py`, `deposit_rate_vn.py`, `cctg_rate_vn.py`, `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn_events.csv`, `summary_r3_extra.json` (giả định khoá), `TOP5C_CORRECTIONS_20261108.md`, `STANDARD_r2.md`, `sector_read_ngan_hang_20261031.md`, cùng md5 các file đầu ra (dòng `OUT`). Bản sao `SUMMARY_r2.json` có md5 `46a7f2f3…`, trùng LOCK của r2.

r = 13,50% (lãi huy động 12T 06/11 = 7,40% = mức neo, nguồn cctg_12m 02/11). Không đặt lệnh, không sửa `kb/dd_price_zones.json`.
