# DD — MSB (NHTMCP Hàng Hải Việt Nam) · **r3** (dựng lại sau skeptic DD_GENERAL r1 22/11 = REFUTED) · as-of 23/11/2026 · job `Taylor_20261122_234430`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị, không đặt lệnh. Khung NGÂN HÀNG (RI trên VCSH; không net cash/FCFE).
> Bản trước: `REPORT.md` (r2, 09/11, tâm 13.018) · `REPORT_r1.md`. Verdict skeptic đã đọc: `skeptic/r1.json` + `skeptic/r1_raw.md` (report_md5 `dfb6cab1…`).
>
> **Nguồn:**
> - **[KT25]** `src/bctn_2025.pdf` — Báo cáo thường niên 2025, tải lại 23/11/2026 từ `msb.com.vn/msb-website/BAO-CAO-THUONG-NIEN-MSB-2025.pdf` (md5 `159da757…`), có lớp text (`src/bctn_2025.txt`, trích theo trang P*n*). Gồm **BCTC hợp nhất 2025 kiểm toán EY** (P73 trở đi) + bảng chỉ tiêu 2022–25.
> - **[HN-Q3] / [RL-Q3] / [SX6T] / [IR-Q3]** — BCTC HN + riêng Q3/2026, BCTC 6T/2026 soát xét KPMG, tài liệu IR Q3. Số do agent đọc ảnh ngày 09/11, ghi theo trang ở `calc/notes_read.md`. **PDF gốc KHÔNG còn trong `src/`, và hôm nay không tải lại được** (danh sách tài liệu IR của msb.com.vn chỉ trả qua AJAX, lệnh gọi bị chặn trong phiên này). Đối chiếu độc lập: BQ `ticker_financial` 2026Q3 (VCSH 46.857, LNST Q3 1.649), báo chí cho LNTT Q3 2.017 / NII 3.422 / TTS ~440 nghìn tỷ ([vnba](https://vnba.org.vn/vi/msb--loi-nhuan-truoc-thue-quy-iii-dat-2-017-ty-dong--tang-27-1-24122.htm), [mekongasean](https://mekongasean.vn/msb-tang-thu-lai-va-dich-vu-loi-nhuan-quy-3-vuot-2000-ty-dong-61401.html), [cafef](https://cafef.vn/msb-tang-truong-loi-nhuan-truoc-thue-hon-27-trong-quy-iii-188261030155423323.chn)) — tất cả khớp.
> - **[BQ]** `calc/bq_msb_fin_r3.csv` (VCSH, LNST theo quý 2022Q4–2026Q3) · `calc/bq_msb_px_r3.csv` (chỉ dùng SAU khoá).
>
> **Khoá giả định (mù giá):** `calc/assumptions_r3.json` **md5 `564835112d45356275bdd5b812542c9e`** · file khoá v1 `calc/lock_v1_r3.json` md5 `6891d0c2…` (lint `dd_assumptions_lint.py` rc=0, 1 cảnh báo L7 — xem mục 10) · `calc/model_r3.py` md5 `19c39ce0…` · `calc/LOCK_r3_prerun.txt` (khoá lúc 23/11, trước khi đọc giá) · `calc/LOCK_r3_post.txt`.
> Tái lập: `python3 -I calc/model_r3.py` (chỉ đọc file khoá) → `python3 -I calc/postlock_r3.py` (thanh khoản + nhãn). Đơn vị tỷ đồng; giả định tương lai = **(ước lượng)**.

## 1. Kết luận

- **Giá trị nội tại (mù giá): tâm 14.621 đ/cp sau chiết khấu thanh khoản** (14.674 trước CK; vị thế 5 tỷ, CK 0,37%). **P10 10.538 / P50 14.698 / P90 18.796.**
  Vùng tham chiếu **10.500–18.800, tâm ~14.600**. r2: tâm 13.018, vùng 9.675–16.373 ⇒ **tâm +12,3%**.
- **Vì sao tâm tăng:** sửa lỗi quy ước ROE mà skeptic chỉ ra. r2 lấy ROE 14% từ `ROE_Trailing` của BQ, vốn tính trên VCSH **bình quân**, nhưng mô hình lại nhân ROE với VCSH **đầu kỳ**. Hệ quả: ROE dài hạn của kịch bản CƠ SỞ thực chất chỉ ~13,1% tính theo bình quân, thấp hơn Ke, tức đã ngầm ép ROE về Ke. r3 quy đổi mọi điểm ROE sang **đầu kỳ**. CƠ SỞ dài hạn thành 15,1%, nằm giữa mức thực tế 2025 (15,3%) và 2026E (14,4%), cùng quy ước. Bước sửa này đóng góp **+13,0%** (đối chứng: giữ quy ước r2 trên cùng lưới r3 cho 12.989). Trục mới **haircut lãi dự thu** kéo **−1,0%**.
- **Pha sau khoá:** giá 16.550 (đóng cửa 20/11, BQ) nằm **TRONG vùng, nửa trên**: cao hơn tâm **+13,2%**, có 71% trọng số giá trị nằm dưới giá. Luật 4 (giá ≤ 0,85×tâm = 12.428) **không đạt**. Giá ngụ ý Ke 12,49%, tức lãi huy động 12T ~6,4%, thấp hơn mức thực 7,40% khoảng 1pp.
- **Điểm yếu lớn nhất vẫn là chất lượng tài sản và chất lượng ghi nhận thu nhập:**
  - NPL hợp nhất 2,70%, nhóm 2 +66% YTD, bao phủ 47%.
  - **Lãi phải thu từ tín dụng tăng gấp đôi trong 2025**: 3.273 lên 6.803, rồi 8.103 tại 30/06/26; tỷ lệ trên dư nợ đi 1,85% → 3,31% → ~3,5%.
  - **Lãi thực thu / lãi ghi nhận 2025 chỉ 76%** (2024: 101%), 9T26 phục hồi lên 91% [KT25 LCTT; HN-Q3 p8].
  - Phải thu có tính chất tín dụng 4.101.
  - LC mua miễn truy đòi 9.229 (30/06).
  - Phải thu khác Q3 +4.620 không tách được.
- **Kiểm toán FY2025 — nay đã đọc từ BCTC gốc:**
  - **EY Việt Nam, chấp nhận toàn phần, không có đoạn nhấn mạnh**, ký 26/03/2026 (số tham chiếu 11635584/E-69214045-HN) [KT25 P73].
  - 6T/2026 KPMG soát xét, chấp nhận toàn phần.
  - Lý do đổi EY→KPMG: **không kiểm chứng được** (chưa đọc được NQ ĐHĐCĐ 2026). Ảnh hưởng ước lượng tới định giá: 0, vì không có ý kiến ngoại trừ ở cả hai kỳ.
- **Bên liên quan / TPDN / vốn:** không trọng yếu. Cụ thể:
  - Cho vay HĐQT/BĐH và người liên quan 142,6 tỷ (0,07% dư nợ).
  - TPDN 1.961 tỷ (4,6% VCSH) tại 31/12/25.
  - CAR 2025 12,49%, CAR cấp 1 11,87%; Q3/26 CAR HN 11,67% [KT25 TM42, TM11.1, bảng chỉ tiêu P21].
- **Pháp lý:** không có vụ việc ⇒ không WARNING (kế thừa r2, chưa tìm lại).
- **Sizing (V8, chuẩn 2–4% NAV/mã):** giá nằm trên tâm và không đạt luật 4 ⇒ **đề xuất 0% discretionary tại giá hiện tại**. Nếu LAG mua theo luật hệ thống thì giữ khẩu phần LAG chuẩn, không cộng thêm phần discretionary. Thanh khoản không ràng buộc ở 2–4% NAV (mục 8).

## 2. Q1 — Vì sao LAG chọn (tái dùng r2 mục 2; số Q3 không đổi)

LNST Q3 1.649 (+29,4% YoY); 9T 4.414 (+16,9%); động lực là NII +607 tỷ. PPOP +17,7% là phần bền; khoảng 4pp tăng trưởng đến từ dự phòng Q3 thấp hơn Q3/25 trong khi NPL tăng. Bảng đầy đủ: `REPORT.md` mục 2 [HN-Q3 p7].
**Kiểm nhanh r3:** quý tăng tốc này có một phần là lãi dồn tích: TN lãi ghi nhận 9T 22.349 so với thực thu 20.394, chênh 1.955. Đổi lại, tỷ lệ thu/ghi nhận 9T26 (91%) đã **tốt hơn** cả năm 2025 (76%). Vì vậy chất lượng thu nhập 2026 không xấu thêm so với 2025, nhưng phần tồn đọng 2025 vẫn còn trên bảng cân đối (mục 3).

## 3. Chất lượng tài sản, vốn, nguồn vốn (khung Bobby §7)

Bảng r2 (`REPORT.md` mục 3) giữ nguyên: NPL 2,70%, nhóm 2 1,68%, bao phủ 47,2%, TNEX NPL 8,0%, CASA 20,4%, CAR 11,67%, LDR 64,9%. **Bổ sung r3 từ BCTC kiểm toán 2025 [KT25]:**

| Chỉ tiêu | 31/12/24 | 31/12/25 | 30/06/26 | Nguồn |
|---|---|---|---|---|
| Lãi phải thu từ tín dụng | 3.272,7 | 6.802,7 | 8.103,3 | KT25 TM 15.2; SX6T TM 15.2 |
| Dư nợ KH | 176.493 | 205.209 | 230.420 (mẹ, IR) | KT25 BCĐKT; IR-Q3 p9 |
| Lãi phải thu TD / dư nợ | **1,85%** | **3,31%** | ~3,52% | tự tính |
| Lãi thực thu / ghi nhận (năm/9T) | 101% (18.910/18.681) | **76%** (16.497/21.601) | 91% (9T26: 20.394/22.349) | KT25 LCTT + KQKD; HN-Q3 p8 |
| Phải thu có tính chất tín dụng (bán nợ cho đối tác) | 5.786 | 4.001 | 4.001 → **4.101 (30/09)** | KT25 TM 15.1; SX6T; HN-Q3 p36 |
| Tạm ứng + phải thu khác | 1.228 | 6.511 (gồm LC 2.383, cọc VP 3.310) | 13.881 (LC 9.229) → **18.501 (30/09)** | KT25 TM 15.1; SX6T TM 15.1.2 |
| CK nợ TCKT (TPDN) AFS | 900 | **1.961** (LS 9,45–12,85%) | n/a | KT25 TM 11.1 |
| Cho vay HĐQT/BĐH/BKS + người liên quan | 273,1 | **142,6** | n/a | KT25 TM 42 |
| CAR / CAR cấp 1 / VCSH/TTS | 12,39% / 12,81% / 11,50% | **12,49% / 11,87% / 10,41%** | CAR HN 11,67% (30/09) | KT25 bảng chỉ tiêu P21; IR-Q3 |

**Đọc:**
- **(1) Lãi dự thu là cờ thật.** Tỷ lệ trên dư nợ tăng ~1,8 lần trong 2025, lãi thu bằng tiền chỉ 76% lãi ghi nhận. Phần vượt tỷ lệ 2024 là **~3.831 tỷ** (8,2% VCSH), dùng làm cơ sở cho trục haircut (mục 5).
  - Đối trọng: 9T26 thu tiền đã cải thiện lên 91%.
  - Một phần tăng có thể do kỳ trả lãi của cho vay trung dài hạn (DH +22% YTD) — chưa tách được.
- **(2) Phải thu bán nợ 4.101 đã GIẢM từ 5.786 (2024) xuống 4.001 (2025)**, tức đã thu hồi được một phần — thông tin hai chiều mà r2 chưa có. Q3 tăng lại +100.
- **(3) LC mua miễn truy đòi là bộ chứng từ theo L/C do chính MSB phát hành** [KT25 P28: "mua hẳn miễn truy đòi Bộ chứng từ theo L/C do MSB phát hành"]. Rủi ro tín dụng nằm ở KH nhập khẩu của MSB, nhưng khoản này hạch toán là phải thu (dự phòng chung 38 tỷ), không phải cho vay. Đây là rủi ro room (CV 9608) và rủi ro phân loại, không phải tổn thất đã thấy.
- **(4) TPDN và bên liên quan nhỏ**, không phải nguồn rủi ro trọng yếu.

## 4. Vị thế & lợi thế cạnh tranh (5F) — TÁI DÙNG r2 (làm 09/11/2026, <12 tháng, luật V5) + kiểm nhanh

moat_tier **NONE** (NARROW-ứng viên không bền); rủi ro số 1 là chất lượng tài sản. Đầy đủ ở `REPORT.md` mục 4. **Kiểm nhanh r3:**
- (i) ROE đầu kỳ 2023–25 là 17,4% / 17,6% / 15,3% [BQ + KT25], 2026E 14,4%. Tức là vượt Ke nhưng **đang giảm dần**.
- (ii) CASA 28,3% (2024, KT25) → 26,7% (2025) → 20,4% (30/09/26): lợi thế nguồn vốn tiếp tục mòn.

⇒ Giữ NONE: không thưởng RONIC > Ke, terminal RONIC = Ke. KHÔNG ép ROE dự báo về Ke (luật 08/11). Đây chính là chỗ r2 vi phạm ngầm và r3 đã sửa.

## 5. Q2 — Giá trị nội tại (RI, mù giá)

**Phương pháp:**
- RI 3 năm tường minh 2027–29, terminal `TV = (ROE_T − Ke)·BV_N/Ke` (RONIC = Ke).
- **ROE tính trên VCSH ĐẦU KỲ, nhân với BV đầu năm — đúng quy ước số học của mô hình.**
- BV đầu = VCSH 30/09 46.857 + LNST Q4/26 theo kịch bản + quyền mua 936 tr CP @10.000 (9.360 tỷ; trừ PV tiền nộp 38/365 năm).
- Chia cho 3.744 tr CP; payout tiền 0.

**r = Ke 13,5%** = 13,5% + 1,0×(7,40% − 7,40%). Lãi huy động 12T hiệu dụng = CCTG 12M 7,40% ngày 02/11 (`deposit_rate_vn.effective_deposit_rate('2026-11-23')`, cập nhật 16/11). Neo 03/11/2026, β = 1.

| Kịch bản (w) | Q4/26 LNST | ROE đầu kỳ 2027/28/29 → T | (r2, bình quân) | Giá trị (trước CK) | P/B ngụ ý |
|---|---|---|---|---|---|
| XẤU (0,275) | 1.350 | 10,5 / 11,1 / 11,6 → **12,8%** | 10/10,5/11 → 12 | 11.014 | 0,88x |
| CƠ SỞ (0,45) | 1.700 | 13,3 / 14,5 / 15,1 → **15,1%** | 12,5/13,5/14 → 14 | 14.971 | 1,20x |
| TỐT (0,275) | 1.950 | 15,1 / 16,8 / 17,4 → **17,4%** | 14/15,5/16 → 16 | 18.865 | 1,51x |

**Cơ sở ROE (đầu kỳ, tự tính từ BQ, đối chiếu bảng chỉ tiêu KT25):**

| Năm | LNST / VCSH đầu kỳ | ROE đầu kỳ |
|---|---|---|
| 2023 | 4.645 / 26.654 | 17,4% |
| 2024 | 5.519 / 31.298 | 17,6% |
| 2025 | 5.628 / 36.818 | 15,3% |
| TTM Q3/26 | 6.265 / 40.556 | 15,4% |
| 2026E CƠ SỞ | 6.114 / 42.446 | 14,4% |

- Quy đổi r2→r3: ROE_đầu kỳ = ROE_bq/(1 − ROE_bq/2), áp cơ học, giữ nguyên ý kinh tế của từng kịch bản.
- CƠ SỞ 2027 thấp hơn (13,3%) vì VCSH +20% từ quyền mua.
- TỐT 17,4% = vùng 2023–24 đã quan sát; XẤU 12,8% = chi phí tín dụng tăng + NIM nén.
- Trọng số đối xứng (tiền lệ MBB/FPT), không có dữ liệu độc lập để nghiêng. Tất cả **(ước lượng)**.

**Lưới 81 điểm** = 3 kịch bản × 3 trục rủi ro. Các trục là rủi ro cụ thể quan sát được, nên được đưa vào như kịch bản có xác suất, **không vào tham số trung tâm** (V4):
1. **Dịch ROE** ±1pp, trọng số 0,25/0,5/0,25.
2. **Haircut phải thu bán nợ 4.101 tỷ** 0/25/50%, trọng số 0,5/0,3/0,2, sau thuế 20%.
3. **[MỚI r3] Haircut lãi dự thu vượt chuẩn 3.831 tỷ** 0/25/50%, trọng số 0,5/0,3/0,2, sau thuế.
   - Cơ sở độc lập: tỷ lệ lãi phải thu tín dụng/dư nợ 2024 = 1,854% (EY) × dư nợ 30/06/26 230.420 = 4.273, so với thực tế 8.103.
   - Thận trọng: 230.420 là dư nợ ngân hàng mẹ, còn 8.103 là số hợp nhất ⇒ phần vượt hơi cao.

| | Tâm | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|---|
| Trước CK thanh khoản | 14.674 | 10.576 | 12.259 | 14.752 | 16.716 | 18.865 |
| **Sau CK (5 tỷ, 0,37%)** | **14.621** | **10.538** | 12.214 | 14.698 | 16.655 | **18.796** |
| Sau CK (40 triệu, 0,03%) | 14.670 | 10.573 | | | | 18.858 |

Tham số trung tâm (CƠ SỞ, không haircut) sau CK: 14.917.

**V1 — độ nhạy lãi huy động (tâm trước CK 14.674):**

| | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β=1 | 16.592 (+13,1%) | 15.594 (+6,3%) | 13.825 (−5,8%) | 13.038 (−11,2%) |
| β=0,5 | 15.594 | 15.125 | 14.241 | 13.825 |

**D4 — hai đầu dải Ke nội địa:** Ke 12,3% → 17.015 (+16,0%); Ke 13,4% → 14.852 (+1,2%). Tâm vẫn dùng 13,5%.

**Độ nhạy khác (tâm trước CK; KHÔNG vào base):**

| Phép thử | Tâm | Δ |
|---|---|---|
| ROE hội tụ nửa đường về Ke (thông tin rủi ro moat NONE) | 12.898 | −12,1% |
| Đối chứng: quy ước ROE bình quân r2 trên lưới r3 | 12.989 | −11,5% |
| Không có trục lãi dự thu | 14.818 | +1,0% |
| Bao phủ lên 80% | 14.177 | −3,4% |
| Không quyền mua | 14.324 | −2,4% |
| Terminal g 6%, RONIC = ROE_T (tương đương WIDE) | 16.453 | +12,1% |
| LC 9.229: chi phí tín dụng 0,89%/năm × 1 năm | 14.657 | −0,1% |
| LC 9.229: tổn thất 5% một lần | 14.576 | −0,7% |
| Phải thu khác Q3 +4.620 (không tách được) mất 25% | 14.428 | −1,7% |

**V6 (hai nền FCFE) — không áp.** Ngân hàng định giá bằng RI trên VCSH; khung FCFE/tái đầu tư g/ROE của V6 không có nghĩa với ngân hàng. Kiểm Gordon P/B thay thế ở mục 7.
**V4:** không có dự án XDCB trọng yếu. Quyền mua là dòng vốn VÀO (đã mô hình hoá), không phải capex tuân thủ.

## 6. Q3 — Rủi ro lớn nhất & điều làm nhận định đổi theo CẢ HAI chiều

**Rủi ro số 1:** chu kỳ tài sản xấu đi gặp đệm dự phòng mỏng (bao phủ 47%), cộng với **chất lượng ghi nhận thu nhập** (lãi dự thu 3,5% dư nợ, thu tiền 76% năm 2025). Nếu phải thoái lãi dự thu và xây lại bao phủ cùng lúc, giá trị về vùng XẤU, khoảng 10.500–11.000.

| Chiều | Điều kiện (mốc kiểm) | Tác động |
|---|---|---|
| ↑ | Lãi huy động 12T −100bp bền | ~16.600 (+13%) |
| ↑ | BCTC KT 2026: lãi phải thu TD/dư nợ ≤ 2,5% **và** thu/ghi nhận lãi ≥ 95% | bỏ trục lãi dự thu ⇒ +1,0% |
| ↑ | Q4/26: nhóm 2 giảm QoQ, bao phủ ≥ 60%, phải thu 4.101 giảm tiếp | trọng số sang CƠ SỞ/TỐT ⇒ 15.000–16.500 |
| ↑ | ROE đầu kỳ ≥ 17% hai năm liền sau phát hành quyền mua | TỐT thành trung tâm ⇒ ~18.800 |
| ↓ | Lãi phải thu TD tiếp tục > 3,5% dư nợ, hoặc thu/ghi nhận < 85% (BCTC Q4/26 hoặc KT 2026) | haircut 50% thay cho kỳ vọng 17,5% ⇒ −266 đ/cp (−1,8%); cân nhắc dịch trọng số sang XẤU |
| ↓ | Nhóm 2 + NPL Q4/26 > +20% QoQ, hoặc DP Q4 < 400 khi NPL tăng | XẤU chiếm ưu thế ⇒ ~11.000 |
| ↓ | Lãi huy động +100bp; NHNN hạ room 2027 cho NH dùng kênh LC | ~13.000 hoặc thấp hơn |
| ↓ | Room 2026 đã dùng 10,69% > 10,45% được giao ⇒ Q4/26 tăng trưởng ~0; LNST Q4 < 1.700 | Q4 = 1.350 thay vì 1.700 ⇒ −350 tỷ/3.744 tr CP ≈ −93 đ/cp trực tiếp (−0,6%; ước lượng, chưa tính lan truyền qua BV) |

Mốc kiểm: BCTC Q4/2026 (cuối 01/2027) · BCTC kiểm toán 2026 (KPMG, ~03/2027) · kết quả chào bán 25% · NHNN giao room 2027.

## 7. Q4 — Cờ tự động

| Cờ | Kết luận | Lý do |
|---|---|---|
| Gordon P/B CHEAP (1,50x từ ROE5Y 17,2%) | **NHIỄU một phần** | Dùng CƠ SỞ ROE_T đầu kỳ 15,1% @Ke 13,5%, g 6% ⇒ 1,21x = 15.185; ROE_Trailing (bình quân) 14,1% ⇒ 1,08x = 13.500. Nhất quán với tâm RI 14.600 |
| FSCORE 3 | ít ý nghĩa với NH | xem mục 3 |
| D/E 8,39 | bình thường | VCSH/TTS 10,7%, CAR 11,67% |

## 8. Q5 — Thanh khoản & sizing (SAU khoá)

- **Thanh khoản [BQ, 18/11/2025–20/11/2026, `calc/postlock_r3_out.txt`]:** ADV trung vị 250 phiên **96,0 tỷ** (60 phiên 128,2; 20 phiên 139,5); σ ngày 1,60%.
- **Chiết khấu thanh khoản:** CK = σ·√(Q/ADV250). Vị thế 5 tỷ ⇒ **0,37%** (5,2% ADV; 0,52 phiên ở mức tham gia 10%, 0,26 phiên ở 20%). Vị thế 40 triệu ⇒ 0,03%.
- **V8:** 2–4% NAV/mã với NAV quy mô hiện tại của sleeve vẫn nằm trong vài phiên ADV, nên thanh khoản không ràng buộc. **Ràng buộc là định giá:** giá cao hơn tâm 13%, không đạt luật 4 ⇒ đề xuất discretionary 0% tại giá hiện tại. Nếu giá ≤ 12.428 (0,85×tâm) thì có thể xét tranche đầu 2% NAV — cần user duyệt.
- **Overhang cung:** quyền mua 25% @10.000; cổ đông nhà nước muốn thoái vốn [WEB, kế thừa r2].

## 9. Kiểm số & nguồn (bổ sung r3)

| Số | Nguồn gốc | Kết quả |
|---|---|---|
| VCSH 31/12/23, 24, 25 = 31.298 / 36.818 / 42.446 | KT25 bảng chỉ tiêu vs BQ | KHỚP |
| LNST 2024 / 2025 = 5.519 / 5.629 | KT25 bảng chỉ tiêu vs BQ tổng 4 quý (5.519 / 5.628) | KHỚP (lệch làm tròn 1) |
| Dư nợ KH 31/12/25 205.208,8 | KT25 BCĐKT P74 vs notes_read p4 | KHỚP |
| Phải thu có tính chất TD 31/12/25 4.001.159 | KT25 TM 15.1 vs SX6T | KHỚP |
| Lãi phải thu TD 31/12/25 6.802.719 | KT25 TM 15.2 vs SX6T cột so sánh | KHỚP |
| VCSH 30/09/26 46.857; LNST Q3 1.649; LNTT Q3 2.017 | notes_read vs BQ vs báo chí | KHỚP |

## 10. Phụ lục — chưa làm / không kiểm chứng được

- **Không kiểm chứng được:**
  - Lý do đổi kiểm toán EY→KPMG — ảnh hưởng ước lượng 0, vì cả hai kỳ đều chấp nhận toàn phần.
  - Cơ cấu phải thu khác Q3 +4.620 — độ nhạy −1,7% nếu mất 25%.
  - TPDN và lãi phải thu theo nhóm nợ tại 30/09 — Q3 không tách; tại 31/12/25 TPDN chỉ 4,6% VCSH.
  - ESOP 2026 — không thấy trong BCTN; NQ ĐHĐCĐ chưa đọc.
  - Thanh tra NHNN gần nhất.
- **PDF Q3/6T/IR gốc** không còn trong `src/`. Số Q3 truy về `calc/notes_read.md` (đọc ảnh 09/11) và đã được đối chiếu BQ cùng 3 báo. Tải lại cần gọi AJAX của msb.com.vn (`msb_investor_v2_load`), việc này bị chặn trong phiên — **cần user/Mike cho phép hoặc tải tay**.
- **Lint khoá:** cảnh báo L7 (capital_commitments có quyền mua 9.360 trong khi projects rỗng) là **dương tính giả**. Quyền mua là dòng vốn vào, không phải dự án/capex.
- **CET1:** báo cáo không công bố CET1 riêng. CAR cấp 1 2025 = 11,87% là proxy gần nhất, vì VCSH MSB thuần cổ phần phổ thông.

## Phụ lục E — Đính chính so với rev trước (r2 → r3), theo skeptic DD_GENERAL r1 (22/11, REFUTED medium)

| # | Hạng mục skeptic | Loại | Xử lý r3 | Tác động tâm (trước CK) |
|---|---|---|---|---|
| 1 | **ROE bình quân (BQ `ROE_Trailing`) nhân trên VCSH đầu kỳ ⇒ ngầm ép ROE về ~13,1% < Ke** (killer) | thiên lệch chiều RẺ, định lượng được | (a) VÀO BASE: quy đổi mọi điểm ROE sang đầu kỳ; cơ sở = ROE đầu kỳ thực tế 2023–26E tự tính (BQ + KT25) | **+13,0%** (12.989 → 14.674 trên cùng lưới r3); khớp ước tính skeptic "+1pp ⇒ +11,9%" |
| 2 | Lãi dồn tích (thu 20.394 vs ghi nhận 22.349; lãi phải thu TD +19% vs dư nợ +12%), không haircut | thiên lệch chiều ĐẮT | (b) KỊCH BẢN XÁC SUẤT: trục haircut 0/25/50% trên phần vượt tỷ lệ 2024 (3.831 tỷ, cơ sở EY 2024). Bổ sung số kiểm toán 2025: thu/ghi nhận 76%, lãi phải thu TD 3.273 → 6.803 | **−1,0%** |
| 3 | LC miễn truy đòi 9.229 + phải thu khác 18.501 (Q3 +4.720) chỉ có DP chung 38 tỷ | ĐẮT, chưa định lượng | LC: bản chất = bộ chứng từ L/C do MSB phát hành [KT25] ⇒ (b) ĐỘ NHẠY −0,1% / −0,7%. Phải thu khác Q3: (c) KHÔNG KIỂM CHỨNG ĐƯỢC, độ nhạy −1,7% (mất 25%). Không vào base (không có tổn thất quan sát) | 0 (độ nhạy) |
| 4a | Cho vay bên liên quan chưa kiểm | thiếu hạng mục | ĐÃ KIỂM [KT25 TM 42]: 142,6 tỷ (0,07% dư nợ) — không trọng yếu | 0 |
| 4b | TPDN chưa kiểm | thiếu | ĐÃ KIỂM [KT25 TM 11.1]: 1.961 tỷ (4,6% VCSH), DP chung 14,7. 30/09 chưa tách (c) | 0 |
| 4c | CET1 chưa kiểm | thiếu | CAR cấp 1 2025 11,87%, CAR 12,49% [KT25]; CET1 riêng không công bố (c) | 0 |
| 4d | ESOP chưa kiểm | thiếu | BCTN 2025 chỉ có ESOP 2022; KH 2026 = thưởng 20% + quyền mua 25% (đã vào model); ESOP 2026 (c) không kiểm chứng được, ước lượng ≤ 0 | 0 |
| 5 | Ý kiến kiểm toán FY2025 lấy từ nguồn thứ cấp; lý do đổi kiểm toán viên | provenance | ĐÃ ĐỌC GỐC: EY chấp nhận toàn phần, không nhấn mạnh, 26/03/2026 [KT25 P73]. Lý do đổi EY→KPMG: (c) không kiểm chứng được | 0 |
| 6 | `src/*.pdf`, `bq_msb_px.csv`, `*_out`, `LOCK_*` thiếu ⇒ không tái lập | provenance | Thêm `src/bctn_2025.pdf` (+ txt), `calc/bq_msb_fin_r3.csv`, `calc/bq_msb_px_r3.csv`, `model_r3_out.txt/json`, `postlock_r3_out.txt/json`, `LOCK_r3_prerun.txt`, `LOCK_r3_post.txt`. Mô hình r3 chạy lại được từ file khoá. **PDF Q3/6T/IR vẫn thiếu** (tải bị chặn) — mục 10 | 0 |
| 7 | (ngoài skeptic) cập nhật ngày định giá 09/11 → 23/11; ADV/σ 250 phiên mới | cơ học | T0 38/365; ADV250 90,2 → 96,0 tỷ; CK 0,38% → 0,37% | ≈ +0,3% (gộp trong đối chứng #1) |

**Tổng (sau CK, 5 tỷ):**

| | r2 | r3 | Δ |
|---|---|---|---|
| Tâm | 13.018 | **14.621** | +12,3% |
| P10 | 9.675 | **10.538** | |
| P90 | 16.373 | **18.796** | |
| Ngưỡng luật 4 | 11.065 | 12.428 | |

Nhãn (sau khoá, giá 16.550 @20/11): **TRONG vùng** (r2 với giá 16.350 @06/11: "TRONG vùng, biên trên, không phân biệt được với TRÊN") ⇒ nhãn vẫn TRONG vùng, nhưng không còn sát P90. Luật 4 vẫn KHÔNG đạt. Tâm dịch >5% ⇒ bắt buộc phản biện lại đầy đủ (B2).
