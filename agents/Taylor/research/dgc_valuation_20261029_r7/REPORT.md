# DGC định giá VÒNG 7 — áp phản biện fundamental-skeptic trên r6 (REFUTED, medium)

Job `Taylor_20261029_104456`. r1-r6 KHÔNG sửa; mọi đính chính r6 nằm ở ĐÂY. READ-ONLY, không phải khuyến nghị đặt lệnh. Tỷ đồng, đ/cp. **[UL]** = giả định tự đặt / ước lượng. Tái lập: `python3 model.py` (assert r4 33.766, r5 40.302, **r6 A 29.817 / B 34.695**; log r7 `run_stdout_r7.txt`, log r6 `run_stdout.txt`; md5 `LOCK.txt`). BCTC Q3 CHƯA soát xét. Luật pháp lý 27/09: phân tích bình thường, chỉ WARNING.
Giá tham chiếu 32.900 (28/10).

## Kết luận (12 dòng)
1. **Verdict: NON theo discriminator §2/§2.5** (3 tiêu chí ❌ độc lập: tài sản lõi dính vụ án — mỏ 25 dừng, khai thác apatit là một tội danh; CFO/LNST 9T **0,55×**; lợi thế chi phí suy yếu vì phải nhập quặng). Dải định giá chỉ là lớp hai và **KHÔNG cứu được verdict**: giá nằm TRONG dải, không có biên an toàn.
2. **Dải r7: A7 32.182 (−2,2% vs giá) · B7 37.060 (+12,6%)**; C7 39.026 chỉ là độ nhạy. A7 tăng +2.365 so r6 A: Nghi Sơn +163, PE lõi +2.202 (§1).
3. **Giá 32.900 KHÔNG nằm dưới dải.** Nó chỉ cao hơn A7 2,2%. ⇒ Nhìn thuần định giá thì verdict KHÔNG lật sang "rẻ". Chỉ discriminator giữ NON, và theo luật thì discriminator là đủ.
4. Biên 2027-28 ±2pp quanh nền r4 (dải đối xứng): A7 **29.345 – 35.017**, B7 34.223 – 39.894. Dự phòng 200: đọc R1 (lặp lại ~100/quý) → A7 **30.598**; đọc R2 (một lần) → A7 **36.663**.
5. **Đính chính r6 về lưu huỳnh**: theo Bobby, ME FOB T10 là 820-890 $/t (đỉnh 947 ở T7). Forecast Qatar ~650 (T1/27) và ~580 (T4/27). Vậy giả định 700 cho 2027 là chiều GIẢM chi phí so với Q3, không phải tăng như r6 viết. Nhưng Bobby đọc "**A về hướng, B về mức**", tức chi phí ở mức cao kéo dài. Ràng buộc cơ học: biên 2027 cơ sở **15,6–19,7%** tuỳ giá S và tỷ trọng S trong giá vốn [UL 6/12%] (§2).
6. **Đính chính dữ kiện tài khoản**: DGC chỉ bị excluded ở **ZaloPay** (`excluded_tickers` ['DGC','PNJ']); SpaceX chỉ có ['PNJ'] (đọc `secrets/trading_bot_accounts.json`). Câu r6 "giá trị tính cho fleet = 0" là SAI. ZaloPay đang giữ **10.000 cp**, giá vốn 39.775, giá thị trường 32.900 ⇒ 329,0 tr = **35,8% NAV** (919,93 tr, ngày 28/10), lỗ −17,3% (DNSE positions 29/10 16:04).
7. **Mức 35,8% NAV gấp ~24 lần trần sizing sleeve** (≤1,5%/tên, tổng ≤3% NAV — §12 của backstop). §12#1 yêu cầu catalyst xác nhận trong 6-9 tháng, nếu không thì THOÁT. Vị thế mở ngày 26/06 ⇒ cửa sổ đó là 26/12/2026 – 26/03/2027.
8. **Đề xuất HARD ABANDON (7 trigger) + time-stop 31/03/2027** cho 10.000 cp ZaloPay (§6). Đây CHỈ là đề xuất, **user quyết**. Nếu đổi nhãn AMBIGUOUS-nghiêng-constructive (user chốt 16/10) → NON thì cũng cần user xác nhận.
9. **WARNING mới**: dự án Đắk Nông 60,09 → 0 qua dòng "Giảm khác" 63,38 (note 11, ảnh p30 đã kiểm). Không có thuyết minh xoá sổ hay bán. Con số 63,38 **không** giải được độ lệch 48,23 của LCTT (§4).
10. **WARNING đã biết (không mới sau 16/10)**: soát xét H1/2026 của UHY bị **ngoại trừ** vì "đang phối hợp cung cấp hồ sơ cho CQĐT" (nguoiquansat 04/09, ghi ở backstop lượt 11/09). Kiểm toán 2025 cũng ngoại trừ, do 950,9 tỷ tồn kho không chứng kiến kiểm kê.
11. Mốc khoá trước (§5): BCTC soát xét Q3, DGC trả lời về dự phòng 200, HOSE gỡ hạn chế (~11-12/2026), BCTC kiểm toán 2026.
12. Số skeptic xác nhận trên ảnh gốc giữ nguyên: tiền ròng 8.370,2 · LNST mẹ Q3 478,162 · dự phòng 200 · LCTT lệch 48,227 (= 332,293 − 284,064).

## 1. Dải r7 và waterfall r6 → r7 (`out_r7_tiers.csv`, `out_r7_waterfall.csv`)
| Bước | A | Δ | B | Δ |
|---|---|---|---|---|
| r6 (tái lập) | 29.817 | | 34.695 | |
| 1 Nghi Sơn XDCB 1.408,8 (note 11) thay 1.352,9 ⇒ capex còn lại 991 | 29.980 | +163 | 34.858 | +163 |
| 2 PE peer áp LNST LÕI (bỏ lãi tiền gửi) + cash_adj như SOTP | 31.040 | +1.060 | 35.918 | +1.060 |
| 3 PE DGC 10y áp LNST LÕI + cash_adj | **32.182** | +1.142 | **37.060** | +1.142 |

| Tầng | EV | vs 32.900 | thuận / cơ sở / nghịch |
|---|---|---|---|
| **A7** (A r6 + 3 bước trên) | **32.182** | −2,2% | 44.213 / 33.778 / 21.501 |
| **B7** (A7 + uplift khai trường 25/19B, không có mốc) | **37.060** | +12,6% | 57.012 / 38.414 / 21.501 |
| C7 (B7 + biên cao r5, chỉ độ nhạy) | 39.026 | +18,6% | 60.767 / 40.121 / 22.707 |

- **Cơ chế bước 2-3**: r6 nhân PE với LNST mẹ ĐÃ GỒM lãi tiền gửi (cơ sở 375 trên 1.318). Như vậy tiền ròng chỉ được định giá ở mức PE × lãi sau thuế / tiền ròng = **0,34 / 0,37 / 0,39** (cột `cash_value_in_pe`). r7 tách ra: PE × LNST lõi (cơ sở 944) + cash_adj. Cash_adj gồm tiền ròng trừ phần PAT-CĐKKS 274, trừ haircut 3/9/29%, cộng lõi Q4, trừ dự phòng 200 và quỹ KTPL 592,8, trừ capex Nghi Sơn còn lại 991. Đây đúng là cách SOTP và DCF đang làm.
- Tầng A7 cơ sở theo phương pháp: SOTP 32.916 · DCF 33.072 · PE DGC 10y **36.101** · PE peer **36.859** · P/B 33.074 (`out_r7_A_summ.csv`).
- **Caveat chiều lạc quan**: PE DGC 10y (8,34) được đo trên LNST lịch sử vốn ĐÃ gồm lãi tiền gửi. Khi áp nó lên LNST lõi thì hơi rộng tay. Nếu PE lõi = 7 (như SOTP) thì nhánh PE gần với SOTP (~33k). Vì vậy A7 nằm trong khoảng ~32-33k, không thấp hơn.
- Dự phòng × quỹ KTPL (trừ 0/50/100%) trên A7: từ 34.328 (không trừ gì) đến **32.182** (trừ cả hai) (`out_r7_prov_x_fund.csv`).
- Nếu nghĩa vụ vụ án lớn hơn mức 200 đã trừ (trigger T1), trừ thẳng vào tiền: +200 → A7 31.655 · +500 → 30.865 · +1.000 → 29.549 (`out_r7_extra_liab.csv`).

## 2. Lưu huỳnh và biên — viết lại r6 §2 theo Bobby (`kb/data_registry/market-state/sector_read_fertilizer_dap_20261028.md` §1, §3, §6)
- **Mức hiện tại** (Bobby §1, SMM 08/10): ME FOB T10 Qatar **835**, KPC 820, ADNOC 890 $/t. T9 suy ngược là 880/865/960. Index ME đạt đỉnh **947 ở T7**. TE nội địa TQ đã giảm −38% từ đỉnh tháng, nhưng nhà NK VN mua theo giá ME CFR, nên chi phí của họ giảm ít hơn nhiều.
- **Forecast khoá trước** (Bobby §6): Qatar QSP **~650 (T1/2027)**, **~580 (T4/2027)**, P(<835) = 0,75. Kịch bản K1 (p 0,55) là 650-800; K2 thoả thuận (p 0,30) là 400-600; K3 leo thang (p 0,15) là >900.
- **Phân loại** (Bobby §3): "**A về hướng, B về mức**" (B ~70/30). Đỉnh cấp tính đã qua, nhưng mức chi phí vẫn cao kéo dài. Mức "bình thường" 150-300 $/t khó quay lại trước Q3/2027 (P ≈ 0,25).
- **Sửa r6**: r6 viết "~700 $/t 2027 so với ~500 hiện nay là chiều tăng giá vốn". Câu đó **SAI** vì mốc so sánh 500 lấy từ `data/sulfur_anchors.csv` (điểm cuối 05/2026, basis lẫn lộn, file cũ — không dùng nữa). So với giá Q3/2026 ~900 [UL, suy từ T7-T9 ở trên], 700 là chiều **GIẢM** chi phí.
- **Ràng buộc cơ học** (`out_r7_sulfur_bridge.csv`): lấy giá vốn Q3×4 = 7.852, điều chỉnh theo tỷ trọng S trong giá vốn [UL 6% / 12%; BCTC không công bố] × (S 2027 / 900 − 1). Doanh thu 2027 cơ sở của model là 9.261.
 | S 2027 ($/t) | tỷ trọng S 6% | 12% |
 |---|---|---|
 | 835 (giữ T10) | 15,6% | 15,9% |
 | 700 (giả định r6) | 16,3% | 17,5% |
 | ~615 (trung vị Bobby T1-T4/27) | 16,8% | 18,4% |
 | 500 (K2 xả hàng) | 17,5% | 19,7% |
 Lưu huỳnh là đuôi gió thuận +0,4 đến +4,5pp. Nhưng phía bán có rủi ro ngược chiều cùng cỡ: giá P4 xuất khẩu −5/−10% làm mất −2,7/−5,5pp (r6 `out_price_shock_margin.csv`); DAP theo Bobby trung vị 770 (T1/27), P(<802,5) = 0,60. Vì vậy **nền vẫn là biên r4 16,5/17,5%**, và **dải ±2pp ĐỐI XỨNG** quanh nền là phần chính thức của dải, không chỉ là "độ nhạy" (`out_r7_margin_band.csv`):
 | Δ biên 2027-28 | −2 | −1 | 0 | +1 | +2 |
 |---|---|---|---|---|---|
 | A7 | 29.345 | 30.763 | 32.182 | 33.603 | 35.017 |
 | B7 | 34.223 | 35.641 | 37.060 | 38.479 | 39.894 |
- Hai cách đọc dự phòng 200 (nếu khoản này nằm trong giá vốn): R1 (lặp lại) cho biên 15,2/16,5% → A7 **30.598** / B7 35.476. R2 (một lần) cho biên 19,5/20,7% → A7 **36.663** / B7 41.539 (`out_r7_prov_readings.csv`).

## 3. NEO verdict vào discriminator (`research/calculated_fear_state_backstop.md` §2, §2.5) — lớp MỘT
DGC thuộc cả nhóm (a) scandal, nhóm (b) chu kỳ phốt pho và nhóm (d) gián đoạn mỏ 25. Theo ghi chú áp dụng chéo, case phải vượt discriminator của **TỪNG** nhóm.
| Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|
| §2#1 Scandal CÁ NHÂN, không lan vào lõi | **❌ FAIL** | Ba tội danh gồm khai thác apatit trái phép (tài sản lõi = mỏ) và vi phạm kế toán (tính toàn vẹn của BCTC). Mỏ 25 đang dừng. Soát xét H1 bị ngoại trừ vì đang phối hợp CQĐT. Gạch ❌ "lan vào pháp nhân/tài sản lõi". |
| §2#2 NN chi phối | FAIL (không bắt buộc, §6) | Tư nhân. |
| §2#3 CF_OA ≥ NP | **❌ FAIL** | 9T: CFO 755,6 / LNST hợp nhất 1.369,4 = **0,55×**. Q3 riêng là ~996 > 506,7 (CFO H1 lấy từ BQ, [UL]), nhưng tồn kho 9T tăng 421,7, chưa đủ 2 quý bền. |
| §2#4 / §2.5#2 Solvent, sống qua đáy | ✅ PASS | Tiền ròng 8.370,2; không có vay dài hạn. |
| §2#5 / §2.5#4 Sàn định giá | ✅ PASS (cơ học) | VCSH mẹ 13.073,9 / 379,78 tr cp = BVPS 34.426 ⇒ **PB 0,96**. Phần lớn sàn là TIỀN (~19.400 đ/cp sau PAT và haircut 9%), không phải tài sản sản xuất. |
| §2.5#1 Chu kỳ, không cấu trúc | **⚠ chưa đạt** | Bobby: "B về mức". Mất quặng tự khai thác thì kéo dài cho tới khi mỏ mở lại, mà mỏ chưa có mốc. Đây là gián đoạn (d) không có thời hạn. |
| §2.5#3 Dẫn đầu chi phí thấp | **❌ FAIL (suy yếu)** | Phải dùng quặng nhập thay mỏ 25. Biên gộp 9T 20,7% so với 31-36% của 5 quý trước vụ án (backstop §6). |
| §2.5 ❌ "đáy chu kỳ chưa xác định" | ⚠ | DAP đang ở p97 của 10 năm, P4 Q3 −16% so Q2. Đây là đỉnh giá đầu ra chứ không phải đáy. |
⇒ Có ít nhất 3 tiêu chí ❌, mà chỉ cần **một** là đủ loại ⇒ **NON**. Lớp hai (định giá §1) cho giá nằm trong dải A7–B7, sát cận dưới. Lớp hai không tạo ra biên an toàn để bù cho lớp một.

## 4. WARNING + câu hỏi mới cho DGC
- **Đắk Nông** (note 11, ảnh `source_pages/p30.png`, số trang in là 29, đã mở lại): XDCB "Dự án nhà máy Đắk Nông" đi từ **60,089 (31/12/25) → để trống (30/09/26)**. Dòng biến động có "**Giảm khác (63,378)**", không ghi đối ứng. "Khác" tăng 26,11 → 43,98. Không có thuyết minh về bán, xoá sổ hay chuyển đi. Câu hỏi: 63,38 đã đi đâu? Ghi vào chi phí khác hay giá vốn (Q3 chi khác chỉ 38,42)? Bán cho ai? Có liên quan đến điều tra không?
- **63,38 có phải lời giải cho dòng 22 LCTT không? KHÔNG khớp số học**: 284,06 (NBV TSCĐ thanh lý) + 63,38 = 347,44 ≠ 332,29; và 63,38 ≠ 48,23. Có thể đọc là "Đắk Nông bán được 48,23 (lỗ 15,15)", tức dòng 22 = 284,06 + 48,23 tự nhất quán. Nhưng khi đó tổng CFI in ra (vốn khớp tiền cuối kỳ) lại không chứa 48,23, nên phải có MỘT dòng khác lệch −48,23. ⇒ Khả dĩ nhưng **chưa chứng minh được**. Hỏi DGC.
- **Soát xét H1/2026 ngoại trừ** (UHY, lý do: phối hợp CQĐT — nguoiquansat 04/09, ghi ở backstop lượt 11/09; tôi không mở lại ducgiangchem.vn trong phiên này). Kiểm toán 2025: ngoại trừ 950,9 tỷ tồn kho. ⇒ Mọi số trong model đều nằm dưới hai ý kiến ngoại trừ này.
- Các câu hỏi r6 §6 vẫn mở: dự phòng 200, thanh lý 332,3 (bên mua), cách tất toán 819/326, quỹ KTPL, khai trường 25/19B, Nghị quyết ĐHĐCĐ.

## 5. Dải cuối + điều kiện đổi verdict (mốc khoá trước)
- **Dải trình user: A7 32.182 – B7 37.060.** Biên ±2pp kéo A7 thành 29,3k–35,0k. R1 → 30,6k, R2 → 36,7k. Giá 32.900 nằm trong dải, sát A7.
| Mốc (khoá 29/10) | Nếu xảy ra | Tác động |
|---|---|---|
| DGC trả lời về dự phòng 200 | Một lần, không liên quan vụ án (R2) | A7 → ~36,7k; discriminator vẫn NON (CFO, mỏ) |
| | Nghĩa vụ/phạt của pháp nhân trong vụ án | **HARD ABANDON T1** |
| BCTC soát xét Q3 / BCTC Q4 (~01/2027) | CFO ≥ LNST 2 quý liên tiếp (Q3 + Q4) | §2#3 chuyển PASS ⇒ có thể xét lại AMBIGUOUS |
| HOSE gỡ hạn chế (~11-12/2026) | Gỡ thật | Thanh khoản trở lại; KHÔNG đổi discriminator |
| Khai trường 25/19B có mốc mở lại bằng văn bản | Có | §2#1 / §2.5#3 cải thiện; B7 trở thành cơ sở |
| BCTC kiểm toán 2026 (~03/2027) | Ý kiến chấp nhận toàn phần | Gỡ cổng audit; xét lại nhãn |
- **Verdict đổi từ NON lên AMBIGUOUS chỉ khi** (CFO ≥ LNST 2 quý) **VÀ** (dự phòng 200 không phải nghĩa vụ vụ án) **VÀ** (không có trigger T1-T7).

## 6. Đề xuất HARD ABANDON + time-stop cho 10.000 cp DGC ZaloPay — CHỈ ĐỀ XUẤT, user quyết
Bối cảnh: lỗ −17,3%, chiếm 35,8% NAV ZaloPay. Mã nằm trong `excluded_tickers` nên bot KHÔNG tự bán; thực thi thủ công qua Mafee sau khi user duyệt. HOSE đang hạn chế giao dịch DGC; khung giờ khớp lệnh dưới diện hạn chế **chưa xác minh** (hỏi Wendy/Mafee trước khi lập plan).
**Trigger HARD ABANDON** — chỉ cần một cái, bán 100% ở phiên khả dụng đầu tiên, không chờ giá:
- T1. Dự phòng 200 (hoặc khoản trích mới) được xác nhận là nghĩa vụ/phạt của **pháp nhân** DGC trong vụ án; hoặc Q4 trích thêm ≥100 mà không có thuyết minh.
- T2. Thu hồi/rút giấy phép mỏ (25, 19B), hoặc chấm dứt dự án Đắk Nông do vi phạm.
- T3. Kê biên/phong toả tài sản của pháp nhân DGC (không tính tài sản cá nhân bị can).
- T4. HOSE nâng từ hạn chế lên kiểm soát đặc biệt/ngừng giao dịch/đình chỉ.
- T5. BCTC kiểm toán 2026 tiếp tục ngoại trừ, từ chối, hoặc nộp chậm.
- T6. Phát hiện tài sản (thanh lý 332,3, Đắk Nông, khoản 819) đã bán hoặc cho bên liên quan vay.
- T7. Pháp nhân DGC bị khởi tố.
**Time-stop**: **31/03/2027** (cuối cửa sổ 6-9 tháng của §12#1 tính từ 26/06). Nếu tới ngày đó chưa có ĐỦ cả hai điều: (a) CFO ≥ LNST 2 quý, và (b) một trong hai — HOSE gỡ hạn chế hoặc ý kiến kiểm toán 2026 chấp nhận toàn phần — thì thoát toàn bộ.
**Size**: mức 35,8% NAV vượt trần sleeve (≤1,5%/tên, ≤3% tổng). Lựa chọn giảm dần về trần khi hết hạn chế là **câu hỏi riêng cho user** (tôi không đề xuất mức cụ thể vì sẽ phải bán ở giá −17%, và đó là quyết định có tính tiền thật).
**Lịch sử nhãn**: AMBIGUOUS (17/07) → gần-NON (23/07, sau Q2) → RE-DO cùng ngày: QUALIFIED YES ở `dgc-tv1-fearbuy-discretionary.md` / AMBIGUOUS-nghiêng-constructive ở backstop (23/07) → **AMBIGUOUS-nghiêng-constructive (user chốt 16/10)** → **đề xuất NON (29/10)**.
Thông tin MỚI kể từ 16/10 làm đổi nhãn: (1) BCTC Q3 (28/10): CFO/LNST 9T 0,55×; dự phòng tăng thêm +100 trong Q3 lên 200, không thuyết minh; Đắk Nông 60 → 0; LCTT tự lệch 48,23; thanh lý TSCĐ 332 không nêu bên mua. (2) Bobby 28/10: chi phí S/NH3 "B về mức". (3) r7: sau khi sửa, giá vẫn nằm trong dải ⇒ không có biên an toàn để bù rủi ro. **Không mới**: ngoại trừ soát xét H1 (04/09), ngoại trừ kiểm toán 2025 — hai điểm này user đã biết khi chốt 16/10.

## 7. Đính chính r6 (không sửa file r6)
- r6 REPORT dòng 67, "Giá trị tính cho tài khoản fleet = 0 vì DGC đang excluded": **SAI**. Chỉ ZaloPay excluded, và ZaloPay đang giữ 10.000 cp (35,8% NAV). Excluded nghĩa là bot không giao dịch, không có nghĩa giá trị bằng 0.
- r6 §2, "lưu huỳnh ~700 2027 so với ~500 là chiều tăng": **SAI chiều**. Xem §2.
- r6 dùng Nghi Sơn 1.352,9; note 11 ghi **1.408,8** (+163 đ/cp, nay đã vào nền).
- r6 nhánh PE chỉ tính tiền ròng ~37% ⇒ A bị đánh giá thấp 2.202 đ/cp. Đã sửa.
- r6 kết luận 2 "giá nằm GIỮA dải A-B": nay giá vẫn trong dải, nhưng sát cận dưới A7 (−2,2%).
