# DGC định giá VÒNG 4 — áp BCTC hợp nhất Q2/2026 GỐC (27/10/2026)

Job `Taylor_20261026_181244`. r3/r2/r1/FORECAST Q3 KHÔNG sửa. READ-ONLY, không phải khuyến nghị. Tỷ đồng, đ/cp. **[UL]** = ước lượng. Tái lập: `python3 model.py` (log `run_stdout.txt`); md5 ở `LOCK.txt`. Số gốc: `MIKE_EXTRACT_BCTC_Q2_2026.md` — tôi mở lại ảnh p05, p06, p41 và khớp: tiền 37,3 + tiền gửi 10.884,2; cho vay 819,0 (cột Note trống); dự phòng 100,0; VCSH 16.241,4 gồm CĐKKS 417,6; note 29 lịch ưu đãi. Giữ luật pháp lý 27/09: WARNING, không phải cổng chặn; không đưa tin pháp lý T8–T10 (user xác nhận không có).
BCTC này là bản công ty tự lập, CHƯA soát xét (soát xét bán niên: LNST hợp nhất −8 tỷ, ngoại trừ vì vụ án). BCTC Q3 chưa công bố.

## Kết luận (10 dòng)
1. **Kỳ vọng r4 = 33.766 đ/cp (r3 32.650, +1.116)**; cơ sở **34.781**, thuận **52.860**, nghịch **19.346**. So giá 32.100: **+5,2%**; so TB 5 phiên 33.500: **+0,8%**. Cơ sở +8,4% / +3,8%; nghịch −39,7% / −42,2%.
2. **Mức tăng ròng +1.116 = thuế + VCSH mẹ −516, lãi phải thu 326 +764, cho vay 819 +1.139, dự phòng 100 −271.** Lõi không cải thiện; kỳ vọng nằm trên giá chủ yếu nhờ khoản 819 chưa rõ bên vay. Bỏ 819 (haircut 100% = 32.688; bỏ hẳn khoản này = **32.628**, ≈ r3, +1,6% so giá 32.100, −2,6% so TB 33.500).
3. **Cho vay ngắn hạn 819,0 (mã 135) = 2.157 đ/cp, bên vay/lãi suất/kỳ hạn không công bố.** Đề xuất haircut **50%** (nền): bên vay ẩn, mới phát sinh trong H1 (31/12/2025 = 0), BCTC chưa soát xét, không nằm trong "bên liên quan" duy nhất được công bố (Van Minh). Bảng nhạy: haircut 0/25/50/100% ⇒ **34.845 / 34.306 / 33.766 / 32.688**. KHÔNG kết luận gì về pháp lý hay bên vay.
4. **Khoản 819 giải thích đúng việc "tiền giảm":** tiền + tiền gửi 13.105,8 → 10.921,5 (−2.184,3). Cầu dựng từ chênh lệch bảng cân đối (`h1_cash_bridge.py`): CFO xấp xỉ **+127** (tồn kho thuần +778 ăn tiền; thuế phải nộp −223) − cổ tức H1 1.251 + vay +324 − XDCB 516 − cho vay 819 = −2.135; dư −49 không giải thích. Bỏ 819 thì tiền chỉ giảm 1.365. ⇒ **10.921 đã là số SAU cho vay**, số dư 30/09 dựng lại không phải chỉnh vì khoản này. Nhưng CFO Q3 giả định +300 so với CFO H1 ≈ +127 (~64/quý) là **lạc quan**: CFO Q3 = 100 ⇒ **33.345** (−421); = 0 ⇒ **33.135**. Giữ 300 ở nền để so được với r3; đây là độ lệch xuống có hướng, chưa chỉnh.
5. **Lãi tiền gửi phải thu 326,2 (859 đ/cp) — xử lý không đếm đôi:** là số dư lãi đã GHI NHẬN vào lợi nhuận quá khứ nhưng chưa thu (330,9 → 326,2, gần như phẳng ⇒ lãi tiền mặt thu H1 ≈ lãi ghi nhận). Tiền 10.921 là gốc, không gồm lãi này. Cho nên: (i) tính 326 như tài sản riêng × (1 − haircut pháp lý cùng mức với tiền); (ii) giả định CFO Q3 +300 và thu nhập tài chính dự phóng (lãi suất × gốc) chỉ là lãi MỚI, giữ số phải thu phẳng đến 30/09, không đếm thêm khoản thu 326; (iii) loại 326 khỏi VCSH lõi trong P/B. Cộng +764. Bỏ khoản này: **33.002**.
6. **Dự phòng ngắn hạn 100,0 (mới, không rõ nội dung):** trừ 100% như nợ = −263 đ/cp (−271 EV). Có thể đã nằm trong haircut pháp lý (cơ sở 9% ≈ 490 tỷ) nên trừ đủ là bảo thủ; không trừ: 34.037; trừ 50%: 33.902.
7. **Thuế (đúng hướng bạn nêu, nhưng tác động ròng nhỏ và có một phán đoán lớn):** (a) lãi tiền gửi 20%: **−113**; (b) lõi theo lịch ưu đãi (9,2% 2026 → 9,6% → 10,5% 2028 → 13,7% 2029-30 → 15,3% 2031 → 19% 2033-34 → 20%): **+421**; (c) terminal lõi 20% (nền cũ 13%): **−211** (DCF cơ sở 36.668 → 35.998, −671; nhạy 17%: +135 ⇒ 33.901); (d) chuẩn hoá thuế lõi cho PE lõi/P-B/PE peer về TB lịch 2027-34 = **14,9%**: **−643** (SOTP cơ sở: giá trị lõi 18.593 đ/cp, so 19.003 của r3). Tổng thuế −546. (d) là phán đoán của tôi, không do dữ liệu quyết định: PE 7x áp lên lợi nhuận đang hưởng thuế 9,6–10,5% sẽ vốn hoá ưu đãi sắp hết; chuẩn hoá ở 20% cho 33.080 (−686 nữa), không chuẩn hoá: 34.410.
8. **VCSH mẹ:** 16.241,4 − 417,6 = **15.823,9 ⇒ BVPS mẹ 41.666** (BQ 42.744 gồm CĐKKS); sau cổ tức 8.000: **33.666 ⇒ P/B 0,95** (30/09 dựng lại 34.511 ⇒ 0,93), thay cho "0,90" r3 in ra. r3 còn một lỗi phụ: VCSH lõi trong phương pháp P/B gồm cả CĐKKS (không trừ) ⇒ sai +417,6; sửa ⇒ P/B lõi +30 EV (cơ học: nền vốn nhỏ hơn ⇒ ít vốn tái đầu tư). Bắt buộc cập nhật trong mọi chỗ dùng VCSH.
9. **Tồn kho 2.459,9 (+778):** nguyên liệu 1.555,9 (+467, +43%), thành phẩm 679,5 (+220, +48%), dự phòng giảm giá 292,9 (còn giảm từ 331,3 trong khi tồn kho +46%). XDCB 1.320,9 (+516 trong 6T ≈ 258/quý), khớp Nghi Sơn 1.221 + ~100 khác, nên capex NS còn lại 929 và Q3 250 **không chỉnh**. Doanh thu 6T: nội địa 735 (16%) / xuất khẩu 3.805 (84%) ⇒ giá và tỷ giá USD quyết định; bên liên quan chỉ Van Minh (bán 136, mua 84).
10. **MI lõi:** số gốc CĐKKS/LNST hợp nhất = 11,8% (Q2) và 8,4% (6T) so với 10% đang dùng ⇒ 33.343 / 34.142; kịch bản "17,8%" cũ của r3 không còn cơ sở. Xác suất đạt 1.600: mẹ 8,6%, hợp nhất 31,7% ⇒ 0,7/0,3 ≈ 24,8% (không vào giá).

## Waterfall r3 → r4 (kỳ vọng, đ/cp; thuận/cơ sở/nghịch: `out_waterfall.csv`)
| Bước | Kỳ vọng | Δ |
|---|---|---|
| r3 (tái lập đúng) | 32.650 | |
| 1a thuế lãi tiền gửi 20% | 32.537 | −113 |
| 1b lõi theo lịch ưu đãi (Q4/26–2031) | 32.958 | +421 |
| 1c terminal lõi 20% | 32.747 | −211 |
| 1d chuẩn hoá thuế PE lõi/P-B/PE peer (14,9%) | 32.104 | −643 |
| 2 VCSH mẹ (bỏ CĐKKS) | 32.134 | +30 |
| 4a lãi phải thu 326,2 | 32.898 | +764 |
| 4b cho vay 819, haircut 50% | 34.037 | +1.139 |
| 5 dự phòng 100 trừ 100% | **33.766** | −271 |

Theo phương pháp (cơ sở, `out_waterfall_methods_coso.csv`): DCF 36.889 → 35.998 (thuế) → 37.594 (sau 3 khoản mới); SOTP 33.229 → 32.840 → 34.437; P/B 32.886 → 32.415 → 32.686 → 34.977.

Lịch thuế lõi [UL] (`out_tax_schedule.csv`): tỷ trọng LNTT lõi theo dự án là ước lượng của tôi (lò 1-2 + silicate 25% ở 20%; DCP/MAP/TSP 27%; lò 6 18%; axit TP GĐ1 10%, GĐ2 8% giả định 10%; PAT 12%), hiệu chỉnh để 2026 = 9,15% khớp phép thử 6T (131,3 − 20%×366,4)/(1.004,3 − 366,4) = 9,10%. Lịch 2031-34 của tôi (15,3 → 19,2%) cao hơn khoảng bạn nêu (15–17%) vì lò 6 hết ưu đãi sau 2031 theo note. Nghi Sơn mới giữ NPAT trực tiếp [UL: có thể có ưu đãi riêng, ngoài terminal 20%].

## Bảng nhạy: haircut khoản 819 × thuế terminal lõi (kỳ vọng đ/cp)
| haircut 819 \ thuế terminal | 13% | 15% | 17% | **20%** |
|---|---|---|---|---|
| 0% | 35.159 | 35.069 | 34.979 | 34.845 |
| 25% | 34.620 | 34.530 | 34.440 | 34.306 |
| **50%** | 34.081 | 33.991 | 33.901 | **33.766** |
| 100% | 33.003 | 32.912 | 32.823 | 32.688 |

Thuế terminal đổi 7pp chỉ dịch ~315 đ/cp; haircut 819 dịch ~2.157 — khoản cho vay quan trọng gấp ~7 lần cả vấn đề thuế terminal. Tồn kho xoá thêm (SOTP cơ sở, haircut pháp lý 9%): 0 / 300 / 600 / 951 tỷ ⇒ 34.436 / 33.764 / 33.092 / 32.305 (`out_sotp_sens_haircut.csv`; 300 tỷ ≈ 13% nguyên liệu+thành phẩm gộp 2.235,4).

## Điều gì còn mở
- **Bên vay, lãi suất, kỳ hạn, thế chấp của 819** — câu hỏi số 1 cho DGC/BCTC Q3 thuyết minh. Nội dung dự phòng 100 (có liên quan vụ án/hay bảo hành/hợp đồng?).
- BCTC Q3: số dư 30/09 thật (nền dựng lại 6.063, CFO Q3 lạc quan ~+200 đến +300), tồn kho tiếp tục tăng hay không, XDCB Nghi Sơn.
- Tỷ trọng LNTT theo dự án và mức cơ sở của GĐ2 [UL]; phán đoán 1d (14,9%). Quỹ khen thưởng phúc lợi 405,7 và thuế phải nộp 129,1 là khoản phải trả không-nợ không có trong tiền ròng (coi là vốn lưu động, cả r3 lẫn r4).
- Lãi phải thu 326: một phần thuộc PAT (CĐKKS) chưa tách (nhỏ). Giả định khoản phải thu giữ phẳng đến 30/09.
- Khai trường 25, Nghị quyết 1.600, mốc Nghi Sơn: không đổi so r3. Chạy lại khi BCTC Q3 ra.
