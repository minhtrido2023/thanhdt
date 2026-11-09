# HHS — DD REDO vòng 3 (09/11/2026, job Taylor_20261108_180130)

Bản này áp đính chính của fundamental-skeptic (`TOP5D_CORRECTIONS_20261108.md`, mục HHS) lên `REPORT_r2.md`. Giả thuyết, chất lượng lợi nhuận và cổ đông vẫn lấy theo `REPORT.md` §2–§4. Số liệu lấy từ `calc_r3/hhs_r3.py`; script chạy 2 lần, output trùng byte (`calc_r3/run1.md5` = `run2.md5`). Giả định nằm ở `calc_r3/assumptions_r3.json` (A1–A16) và đã chốt vào `calc_r3/LOCK_md5.txt` lúc 01:08:22 ICT, **trước** lần chạy đầu. LOCK có một phụ lục 01:09:05 ghi việc sửa lỗi đơn vị ở dòng độ nhạy ô tô; lỗi này không làm đổi tâm hay lưới. Giá 06/11 = **9.990** (BQ `tav2_bq.ticker`, `calc_r3/px_hhs_r3_20261106.csv`). r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,50%**.

## 0. HAI BẢN — user phán xử (đính chính #5)

| Bản | Tâm | P10 | P50 | P90 | % trọng số dưới 9.990 | Nhãn (5 tỷ) | Nhãn (40 tr) | Luật 4 (giá ≤ 0,85×tâm) |
|---|---|---|---|---|---|---|---|---|
| **HEADLINE r3: CK holding 0% (luật user, tiền lệ DRI#1/PVT#1/TCH#1)** | **13.969** | **12.422** | 13.917 | **15.564** | **0,0%** | **DƯỚI vùng** | DƯỚI vùng (tâm 14.151, P10 12.583, P90 15.766) | ĐẠT (5 tỷ: ngưỡng 11.874; 40 tr: 12.029) |
| Song song: CK holding theo trục r2 0/15/25/35/45% (kỳ vọng 27%) | 10.761 | 8.624 | 10.559 | 13.207 | 36,6% | TRONG vùng | TRONG vùng | KHÔNG ĐẠT (ngưỡng 9.147) |
| Song song: CK holding + CK quản trị trục r2 | 10.331 | 8.171 | 10.135 | 12.796 | 46,7% | TRONG vùng | TRONG vùng | KHÔNG ĐẠT |

- **Nhãn đổi chỉ vì một quy ước: có hay không có CK holding.** Mọi trục khác (y, s, trọng số, BĐSĐT, r) đều giữ nhãn DƯỚI ở bản headline. Trong bản có CK holding, nhãn vẫn TRONG ở cả y=2,5 và y=4.
- **Giá ngụ ý:** giá 9.990 tương đương một CK holding cố định **33,5%**. Ở bản headline, nó cần y = 8,7 năm, quá xa miền 2,5–4. Ở bản có CK holding, nó cần y = **4,35 năm**, hoặc s thấp hơn 0,227 (tức s ≈ 0,47).
- ⚠ **Không phải ứng viên plan:** HHS đang nằm trong danh sách `forensic_flags` exclude, nên theo luật 02/11 nó bị loại khỏi candidate plan bất kể nhãn. Mã cũng **không đủ điều kiện sleeve fear-buy §2.5** (§8).

## 1. Kiểm từng đính chính (bằng calc, không chép mù)

| # | Đính chính | Kết quả kiểm | Áp? | Bước bridge |
|---|---|---|---|---|
| 1 | Giá gốc HTK cũ 6.009,8 tỷ thu ngay năm 0, thặng dư ở pv(4) ⇒ mô hình ngầm cho vốn sinh đủ Ke | **ĐÚNG.** Đây cũng là lỗi mà ADDENDUM_5F §2 đã nêu. Calc lại: phần giá gốc phải nhân (1−pv(y)). Riêng #1 cho −1.161 (y=2,5) và −2.035 (y=4); tái lập đúng số skeptic khi bỏ hệ số CK quản trị. Bản của tôi giữ hệ số đó nên ra −1.541 ở trục y 2,5/3,25/4. | Có. y base 3,25, trục {2,5; 3,25; 4} đều nhau [UL] (A2) | −1.541 |
| 2 | s = 40% cắt một chiều biên quan sát của NC-II | **ĐÚNG.** s=40% vốn được đặt giữa biên NC-II và quỹ đất mới mỏng (150 Tô Hiệu, `dd_TCH REPORT:267`). Nhưng 150 Tô Hiệu là HTK của TCH mẹ, không nằm trong khối CRV, còn I.14 đã được tách ra theo NPV0. Vì vậy khối 6.009,8 chỉ còn NC-II, và s_obs = 0,8×(52,05%−10%)/(1−52,05%) = **0,7016** (công thức `tch_valuation_v2.py:99-101`). Lệch theo kịch bản đổi sang đối xứng ±0,15 (A4). | Có | +1.083 |
| 1+2 | Skeptic báo 10.752 (y=2,5) và 9.684 (y=4) | **KHÔNG tái lập được.** Giữ phần còn lại như r2, calc của tôi ra 10.344 và 9.319 (`/tmp` scratch, biến thể "C": s CO_SO=0,699, giữ lệch r2). Hai bên lệch khoảng 400 đ/cp vì skeptic bỏ hệ số (1−CK quản trị) và ngầm dùng Δs ≈ 0,41–0,43 thay vì 0,30. Chiều của đính chính vẫn đúng. | — | — |
| 3 | CK quản trị (kỳ vọng −4%) nằm trong tâm, trái luật | **ĐÚNG.** Docstring r2 dòng 4 tự tuyên bố đã bỏ khoản này khỏi base, nhưng trục vẫn vào tâm. | Có, chuyển sang độ nhạy (−558 nếu thêm lại) | +414 |
| 4 | I.14 −15/0/+40% (kỳ vọng +6,25%) trái luật 20; ký quỹ p=0,30 không có văn bản | **ĐÚNG.** | I.14 đổi sang ±15% đối xứng; ký quỹ chuyển sang độ nhạy (−19) | −23 |
| 5 | CK holding 27% hoàn toàn [UL] và là trục quyết định nhãn | **ĐÚNG theo luật user.** Skeptic tính base 0% ra 13.203 / P10 11.638; bản của tôi ra 13.969 / P10 12.422. Phần chênh đến từ BĐSĐT theo sổ, trọng số đối xứng và y=3,25. Cả hai bản đều cho nhãn DƯỚI. | Có, headline; bản có CK holding chạy song song | +3.208 |
| 6 | Trọng số 0,30/0,50/0,20 lệch xuống; BĐSĐT 50% so với sổ 100%; ô tô | Trọng số: **ĐÚNG.** Căn cứ lệch xuống (đọc ngành Bobby) là nhận định, nên đổi sang 0,25/0,50/0,25 (+89). BĐSĐT: luật base = sổ sách và sổ hợp nhất mang PPA, nên base 100%, trục 50/100/150% (+348, khớp số skeptic). Ô tô: giữ r2, vì skeptic 01/11 C8 lập luận theo chiều ngược lại; độ nhạy LNST 42 × P/E 7,4 cho **+230**. | Trọng số và BĐSĐT áp; ô tô để ở độ nhạy | +89 / +348 |
| 7 | "Vay 390 tỷ đáo hạn 18/11/2026" là lỗi lẫn năm | **ĐÚNG.** BQ `ticker_financial` HHS: 2025Q4 vay dài hạn 390 tỷ, 2026Q3 vay ngắn hạn 0 và dài hạn 0; `dd_HHS REPORT.md:21,190` ghi "trả vay 390". Khoản này không ảnh hưởng NAV vì đã nằm trong VCSH. | Sửa văn bản: REPORT_r2 §9.10, ADDENDUM_5F lực 6c + dòng moat_tags, SUMMARY | — |
| 8 | Giá 9.990, forensic exclude, LN Q3 chưa soát xét, quét tin | Giá đã xác nhận từ BQ. Các mục còn lại là WARNING (§6). Chưa quét tin 01–08/11 vì phiên headless này không có nguồn tin, nên mục này còn MỞ. | WARNING | — |

## 2. Bridge r2 → r3 (cộng dồn, sau CK 5 tỷ)

| Bước | Tâm | Δ | P10 | P90 | % dưới giá | n |
|---|---|---|---|---|---|---|
| 0 r2 (giá 9.550, 04/11) — control tái lập 10.387 / 8.252 / 12.827 (assert) | 10.387 | | 8.252 | 12.827 | 35,2% @9.550 | 5.400 |
| 1 giá + thanh khoản 06/11 | 10.391 | +4 | 8.255 | 12.831 | 45,4% | 5.400 |
| 2 #1 giá gốc pv(y) | 8.850 | −1.541 | 6.927 | 11.008 | 77,7% | 16.200 |
| 3 #2 s = biên quan sát | 9.933 | +1.083 | 7.844 | 12.308 | 55,8% | 16.200 |
| 4 #3 CK quản trị ra khỏi tâm | 10.347 | +414 | 8.287 | 12.719 | 46,4% | 4.050 |
| 5 #4 I.14 ±15%, ký quỹ ra khỏi tâm | 10.324 | −23 | 8.281 | 12.695 | 46,6% | 2.025 |
| 6 #6 trọng số đối xứng | 10.413 | +89 | 8.342 | 12.795 | 44,5% | 2.025 |
| 7 BĐSĐT theo sổ (= **bản có CK holding**) | 10.761 | +348 | 8.624 | 13.207 | 36,6% | 2.025 |
| 8 #5 CK holding base 0% = **HEADLINE** | **13.969** | +3.208 | **12.422** | **15.564** | **0,0%** | 405 |

## 3. Ba con số (điều 4)
- **Tâm** (kỳ vọng của lưới, sau CK 5 tỷ) = 13.969. **P50** = 13.917. **Giá trị tại tham số trung tâm** (CO_SO, ds 0, y 3,25, BĐSĐT 100%, I.14 0) = 13.893. Trước CK: 14.169.
- Kết cục thấp nhất là 10.994, vẫn cao hơn giá. Ở bản headline, không có kết cục nào dưới giá.

## 4. Lưới headline (n = 405 kết cục, phân vị tính bằng `_shared/wpct.py`)
Các trục:
- Kịch bản TIÊU CỰC / CƠ SỞ / TÍCH CỰC, trọng số 0,25/0,50/0,25 [UL]. Mỗi kịch bản có s = 0,55/0,70/0,85, biên backlog 30/33,5/36%, ô tô 25×5 / 35×6 / 50×8.
- ds −15..+15pp (5 điểm).
- y 2,5/3,25/4.
- BĐSĐT 50/100/150%.
- I.14 −15/0/+15%.

Bản headline đặt CK holding, CK quản trị và ký quỹ bằng 0; ba khoản này chỉ còn ở độ nhạy. Các bản song song khác (tâm / P10 / P90, nhãn):
- Trọng số r2: 13.859 / 12.384 / 15.446, DƯỚI
- Lệch s r2 (−0,25/+0,15): 13.853 / 12.128 / 15.564, DƯỚI
- BĐSĐT r2 (0/50/100%): 13.492 / 11.945 / 15.087, DƯỚI
- y cố định 2,5: 14.734; y cố định 4: 13.229. Cả hai DƯỚI.
- Có trục CK quản trị: 13.411 / 11.682 / 15.165, DƯỚI
- Có trục ký quỹ: 13.950; có trục r ±1pp: 13.972

## 5. Thanh khoản (điều 6)
- ADV250 = 16,22 tỷ, ADV60 = 9,50 tỷ.
- CK ở cỡ 5 tỷ là 1,410% (theo ADV60: 1,455%). Cỡ 5 tỷ bằng ~30,8% ADV250, **TRÊN vùng hiệu chỉnh** của luật căn bậc hai, nên CK này có thể bị đánh giá thấp.
- Sleeve thật: 10 tr có CK 0,063% (DƯỚI vùng hiệu chỉnh), 40 tr có CK 0,126%.
- Nhãn giống nhau ở cả hai cỡ.

## 6. WARNING (pháp lý/quản trị chỉ WARNING; giữ đủ 14 mục của REPORT_r2 §9, sửa và thêm như sau)
- **§9.10 đã sửa:** khoản vay 390 tỷ VietinBank của CRV **đã trả trong 9T/2026**. Hiện CRV và HHS **không còn nợ vay** (BQ 2026Q3).
- **Forensic exclude:** HHS bị loại khỏi candidate plan (luật 02/11).
- **LN Q3 chưa soát xét:** 6T từng bị hạ −34% sau soát xét. Nếu Q3 bị hạ tương tự, ảnh hưởng khoảng −90 đ/cp (ước lượng của skeptic, chưa đo). Ảnh hưởng qua NAV nhỏ.
- **Chi phí hoàn thiện NC-II còn lại chưa có dự toán (G10).** Nếu HTK chưa gồm chi phí hoàn thiện thì s_obs bị cao. Đây là rủi ro một chiều xuống chưa lượng hoá được: không có số nên chưa đưa vào lưới. MỞ.
- **Cao tầng HH1–HH4** (2.494 căn, đang làm hầm) có thể có biên thấp hơn thấp tầng. Đây là nhận định, đã nằm trong trục ds và kịch bản ±.
- **Lịch sử dao động tâm** theo quy ước: v1 11.900 → r2 10.387 → 5F chặt-3c 8.393–9.700 → r3 13.969 (CK holding 0) hoặc 10.761 (có CK holding). Biên độ dao động chủ yếu do CK holding và cách chiết khấu giá gốc, không phải do dữ liệu mới.
- Chưa quét tin 01–08/11, chưa truy cập ssc.gov.vn. MỞ.

## 7. Tham số tự đặt [UL]
y (A2) · lệch s ±0,15 theo kịch bản (A4) · ds ±15pp (A5) · trọng số 0,25/0,50/0,25 (A6) · trục BĐSĐT ±50pp (A11) · I.14 ±15% (A9) · ô tô (A12) · trục CK holding r2 trong bản song song (A7). CPBH 10% DT và thuế 20% dùng trong công thức s_obs (A3).

## 8. Mốc HAI chiều + HARD ABANDON
Giữ M1–M7 của `REPORT_r2.md` §8. Thêm hai mốc:
- **Lên:** có cổ tức tiền CRV về HHS ⇒ bằng chứng chống lại CK holding, củng cố headline. Có lịch bàn giao HH1–HH4 sớm ⇒ y kéo về 2,5.
- **Xuống:** có dự toán chi phí hoàn thiện NC-II làm s thực tế < 0,47, tức là mức giá đang ngụ ý ở bản có CK holding. Hoặc lịch HH1–HH4 lùi > 2030.

HARD ABANDON giữ nguyên như r2: kiểm toán ngoại trừ PPA/HTK; người bán HHS Capital là bên liên quan; CRV mất kiểm soát; khởi tố pháp nhân trong nhóm.

Ngưỡng nhãn headline: DƯỚI vùng nếu giá < 12.422, TRÊN vùng nếu giá > 15.564. **Không đủ điều kiện sleeve §2.5.** Nếu có vị thế 5 tỷ thì phải chia tranche ≤ 3,2 tỷ/đợt (20% ADV250), hoặc ≤ 1,9 tỷ/đợt (theo ADV60).

## 9. LOCK
`calc_r3/LOCK_md5.txt` có 21 file upstream: script, assumptions, extra, SQL/CSV giá, `r2common.py`, `bq_px_liq_20261104.csv`, `wpct.py`, `hhs_r2.py`, `hhs_redo.py`, `SUMMARY_r2.json`, `TOP5D_CORRECTIONS`, `STANDARD_r2`, deposit/cctg (.py + events.csv), `tch_valuation_v2.py`, `dd_TCH REPORT.md`, `dd_HHS SKEPTIC_20261101.md`, `dd_HHS REPORT.md`. md5 output nằm ở `calc_r3/run1.md5` / `run2.md5`.
