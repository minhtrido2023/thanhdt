# DD — MSB (NHTMCP Hàng Hải Việt Nam) · **r4** (dựng lại sau skeptic DD_GENERAL r1 22/11 + r2 23/11, cả hai REFUTED) · as-of 23/11/2026 · job `Taylor_20261122_234430`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị, không đặt lệnh. Khung NGÂN HÀNG (RI trên VCSH; không net cash/FCFE).
> Bản trước: `REPORT_r3.md` (23/11, tâm 14.621; skeptic `skeptic/r2.json` REFUTED, report_md5 `eee0bc9f…`) · `REPORT.md` (r2, 09/11, tâm 13.018; skeptic `skeptic/r1.json` REFUTED) · `REPORT_r1.md`.
>
> **Nguồn:**
> - **[KT25]** `src/bctn_2025.pdf` — Báo cáo thường niên 2025, tải lại 23/11/2026 từ `msb.com.vn/msb-website/BAO-CAO-THUONG-NIEN-MSB-2025.pdf` (md5 `159da757…`), có lớp text (`src/bctn_2025.txt`, trích theo trang P*n*). Gồm **BCTC hợp nhất 2025 kiểm toán EY** (P73 trở đi) + bảng chỉ tiêu 2022–25.
> - **[HN-Q3] / [RL-Q3] / [SX6T] / [IR-Q3]** — BCTC HN + riêng Q3/2026, BCTC 6T/2026 soát xét KPMG, tài liệu IR Q3. Số do agent đọc ảnh ngày 09/11, ghi theo trang ở `calc/notes_read.md`. **PDF gốc KHÔNG còn trong `src/`, và hôm nay không tải lại được** (danh sách tài liệu IR của msb.com.vn chỉ trả qua AJAX, lệnh gọi bị chặn trong phiên này). Đối chiếu độc lập: BQ `ticker_financial` 2026Q3 (VCSH 46.857, LNST Q3 1.649), báo chí cho LNTT Q3 2.017 / NII 3.422 / TTS ~440 nghìn tỷ ([vnba](https://vnba.org.vn/vi/msb--loi-nhuan-truoc-thue-quy-iii-dat-2-017-ty-dong--tang-27-1-24122.htm), [mekongasean](https://mekongasean.vn/msb-tang-thu-lai-va-dich-vu-loi-nhuan-quy-3-vuot-2000-ty-dong-61401.html), [cafef](https://cafef.vn/msb-tang-truong-loi-nhuan-truoc-thue-hon-27-trong-quy-iii-188261030155423323.chn)) — tất cả khớp.
> - **[BQ]** `calc/bq_msb_fin_r3.csv` (VCSH, LNST theo quý 2022Q4–2026Q3) · `calc/bq_msb_px_r3.csv` (chỉ dùng SAU khoá).
>
> **Khoá giả định:** `calc/assumptions_r4.json` **md5 `f39391ea1153fb1fdf0925b53ccd2100`** · `calc/model_r4.py` md5 `6d294fcb…` · `calc/LOCK_r4.txt`. Khoá r3 mù giá (`calc/assumptions_r3.json` md5 `56483511…`, `LOCK_r3_prerun.txt`, lập TRƯỚC khi đọc giá) là gốc. **r4 là KHOÁ LẠI có lý do, lập SAU khi đã thấy giá ở pha sau khoá r3.** Lý do khoá lại: skeptic r2 yêu cầu làm sạch ROE nền. Mọi thay đổi r4 neo vào số BCTC/BQ (Phụ lục E); không thay đổi nào dựa vào giá — người đọc cần biết thứ tự này. File khoá v1 schema: `calc/lock_v1_r3.json` (lint rc=0; ROE trong file đó là bản r3).
> Tái lập: `python3 -I calc/model_r4.py` (chỉ đọc file khoá) → `python3 -I calc/postlock_r4.py` (thanh khoản + nhãn). Đơn vị tỷ đồng; giả định tương lai = **(ước lượng)**.

## 1. Kết luận

- **Giá trị nội tại: tâm 13.042 đ/cp** (sau chiết khấu thanh khoản; 13.090 trước CK; vị thế 5 tỷ, CK 0,37%). **P10 9.144 / P50 13.119 / P90 17.062.** Đây là giá trị trên CP **CON QUYỀN** (3.744 tr CP; quyền mua 25% @10.000 đã tính vào BV).
  - **Tương đương SAU QUYỀN: tâm 12.433, P10 9.315, P90 15.650** — dùng khi so với giá đã giao dịch không quyền (ngày chốt quyền chưa xác định).
  - Vùng tham chiếu (con quyền) **9.100–17.100, tâm ~13.000**.
- **So với các bản trước:**
  - r2 (09/11): tâm 13.018.
  - r3 (23/11 sáng): tâm 14.621, REFUTED.
  - r4 ≈ r2 về con số, nhưng **cơ sở khác hẳn**: r2 đúng số vì hai lỗi bù nhau. Lỗi thứ nhất: ROE quy ước bình quân nhân trên VCSH đầu kỳ (kéo xuống ~13%). Lỗi thứ hai: không trừ phần lãi dồn tích.
- **Cơ sở ROE r4 (đầu kỳ, khớp số học của mô hình):**
  - CƠ SỞ dài hạn **14,1%** = ROE 2026E quan sát 14,4% ((4.414 + 1.700)/42.446) − 0,3pp làm sạch dòng lãi dự thu vượt chuẩn.
  - **Không giả định hồi phục** về 15,3% (2025) hay 17,6% (2024), vì ROE đang giảm 17,6 → 15,3 → 14,4% và CASA 28,3 → 20,4%.
  - Biên độ XẤU/TỐT ±2,3pp đối xứng: 11,8% / 16,4%.
- **Pha sau khoá:** giá 16.550 (đóng cửa 20/11, BQ; giá con quyền) nằm **TRONG vùng, phần trên**: cao hơn tâm +26,9%, có 82% trọng số giá trị nằm dưới giá. Luật 4 (giá ≤ 0,85×tâm = 11.085) **không đạt**. Giá ngụ ý Ke 11,63%, tức lãi huy động 12T ~5,5%, thấp hơn mức thực 7,40% gần 1,9pp.
- **Điểm yếu lớn nhất: chất lượng tài sản và chất lượng ghi nhận thu nhập.**
  - Lãi phải thu tín dụng / dư nợ: 1,85% (2024) → 3,31% (2025) → ~3,5% (06/26).
  - Lãi thực thu / ghi nhận: 2025 chỉ 76% (2024: 101%; 9T26: 91%).
  - Lãi phải thu chứng khoán: 1,84% → 2,24% AFS.
  - NPL 2,70%, nhóm 2 +66% YTD, bao phủ 47%.
  - Phải thu bán nợ 4.101.
  - LC mua miễn truy đòi 9.229.
- **Kiểm toán FY2025 (đọc gốc):** EY Việt Nam, **chấp nhận toàn phần, không có đoạn nhấn mạnh** (26/03/2026) [KT25 P73]. 6T/2026 KPMG soát xét, chấp nhận toàn phần. Lý do đổi kiểm toán viên: không kiểm chứng được.
- **Bên liên quan / TPDN / vốn:** không trọng yếu — cho vay người liên quan 142,6 tỷ; TPDN 1.961 tỷ (4,6% VCSH); CAR 12,49% / CAR cấp 1 11,87% (2025).
- **Pháp lý:** không WARNING (kế thừa r2).
- **Sizing (V8, 2–4% NAV/mã):** giá cao hơn tâm 27% ⇒ **đề xuất discretionary 0%**. Giá ≤ 11.085 (con quyền) ⇒ có thể xét tranche 2% NAV, cần user duyệt. LAG mua theo luật hệ thống thì giữ khẩu phần LAG chuẩn. Thanh khoản không ràng buộc (mục 8).

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
| Lãi phải thu từ đầu tư CK / AFS | 1.208 / 65.605 (**1,84%**) | 2.180 / 97.308 (**2,24%**) | 2.576 (AFS chưa tách) | KT25 TM 11.1, 15.2; SX6T |
| CK nợ TCKT (TPDN) AFS | 900 | **1.961** (LS 9,45–12,85%) | n/a | KT25 TM 11.1 |
| Cho vay HĐQT/BĐH/BKS + người liên quan | 273,1 | **142,6** | n/a | KT25 TM 42 |
| CAR / CAR cấp 1 / VCSH/TTS | 12,39% / 12,81% / 11,50% | **12,49% / 11,87% / 10,41%** | CAR HN 11,67% (30/09) | KT25 bảng chỉ tiêu P21; IR-Q3 |

**Đọc:**
- **(1) Lãi dự thu là cờ thật.** Tỷ lệ trên dư nợ tăng ~1,8 lần trong 2025, lãi thu bằng tiền chỉ 76% lãi ghi nhận. Phần vượt tỷ lệ 2024 là **~3.831 tỷ** (8,2% VCSH), dùng làm cơ sở cho trục haircut (mục 5).
  - Đối trọng: 9T26 thu tiền đã cải thiện lên 91%.
  - Một phần tăng có thể do kỳ trả lãi của cho vay trung dài hạn (DH +22% YTD) — chưa tách được.
- **(2) Phải thu bán nợ 4.101 đã GIẢM từ 5.786 (2024) xuống 4.001 (2025)**, tức đã thu hồi được một phần — thông tin hai chiều mà r2 chưa có. Q3 tăng lại +100.
- **(3) LC mua miễn truy đòi là bộ chứng từ theo L/C do chính MSB phát hành** [KT25 P28: "mua hẳn miễn truy đòi Bộ chứng từ theo L/C do MSB phát hành"]. Rủi ro tín dụng nằm ở KH nhập khẩu của MSB, nhưng khoản này hạch toán là phải thu (dự phòng chung 38 tỷ), không phải cho vay. Đây là rủi ro room (CV 9608) và rủi ro phân loại, không phải tổn thất đã thấy.
- **(4) Lãi phải thu từ đầu tư chứng khoán [MỚI r4, theo skeptic r2]** tăng 1.208 → 2.180. Phần lớn đi theo quy mô AFS (+48%; danh mục chủ yếu là TPCP 47.424 và giấy tờ có giá của TCTD 47.922, chỉ 1.961 TPDN). Phần vượt tỷ lệ 2024 là **388 tỷ**, đã gộp vào trục haircut lãi dự thu.
- **(5) TPDN và bên liên quan nhỏ**, không phải nguồn rủi ro trọng yếu.

## 4. Vị thế & lợi thế cạnh tranh (5F) — TÁI DÙNG r2 (làm 09/11/2026, <12 tháng, luật V5) + kiểm nhanh

moat_tier **NONE** (NARROW-ứng viên không bền); rủi ro số 1 là chất lượng tài sản. Đầy đủ ở `REPORT.md` mục 4. **Kiểm nhanh r3:**
- (i) ROE đầu kỳ 2023–25 là 17,4% / 17,6% / 15,3% [BQ + KT25], 2026E 14,4%. Tức là vượt Ke nhưng **đang giảm dần**.
- (ii) CASA 28,3% (2024, KT25) → 26,7% (2025) → 20,4% (30/09/26): lợi thế nguồn vốn tiếp tục mòn.

⇒ Giữ NONE: không thưởng RONIC > Ke, terminal RONIC = Ke. KHÔNG ép ROE dự báo về Ke (luật 08/11). r4 neo ROE CƠ SỞ vào mức 2026E quan sát, KHÔNG giả định hồi phục; phép thử nửa đường về Ke nằm ở độ nhạy.

## 5. Q2 — Giá trị nội tại (RI)

**Phương pháp** (giữ r3):
- RI 3 năm 2027–29, terminal RONIC = Ke.
- **ROE tính trên VCSH ĐẦU KỲ**, nhân với BV đầu năm.
- BV đầu = VCSH 30/09 46.857 + LNST Q4/26 theo kịch bản + quyền mua 9.360 tỷ (trừ PV tiền nộp 38/365 năm).
- Chia cho 3.744 tr CP (**con quyền**); payout 0.
- **Quy đổi sau quyền:** (V×3.744 + 10.000×936)/4.680.

**r = Ke 13,5%** = 13,5% + 1,0×(7,40% − 7,40%). Lãi huy động 12T hiệu dụng = CCTG 12M 7,40% (02/11), `deposit_rate_vn` 23/11; neo 03/11/2026.
- **Vì sao 13,5% nằm ngoài dải 12,3–13,4%:** theo luật V1, r dùng cho TÂM là 13,5% + β×Δ lãi huy động. Dải nội địa 12,3–13,4% (V2/D4) là phần BÁO KÈM, không thay r của tâm (kb/projects/dd-upgrade-final-action-20261122.md §4). Hai đầu dải: Ke 12,3% → 15.219 (+16,3%); Ke 13,4% → 13.251 (+1,2%).

| Kịch bản (w) | Q4/26 LNST | ROE đầu kỳ 2027/28/29 → T | (r3) | Giá trị con quyền (trước CK) | P/B ngụ ý |
|---|---|---|---|---|---|
| XẤU (0,275) | 1.350 | 9,5 / 10,1 / 10,6 → **11,8%** | 12,8% | 9.628 | 0,77x |
| CƠ SỞ (0,45) | 1.700 | 12,3 / 13,5 / 14,1 → **14,1%** | 15,1% | 13.393 | 1,07x |
| TỐT (0,275) | 1.950 | 14,1 / 15,8 / 16,4 → **16,4%** | 17,4% | 17.125 | 1,37x |

**Cơ sở ROE (đầu kỳ, BQ + bảng chỉ tiêu KT25):** 2023: 17,4% · 2024: 17,6% · 2025: 15,3% · TTM Q3/26: 15,4% · **2026E CƠ SỞ: 14,4%**.
- **Làm sạch lãi dự thu trong ROE nền (−0,3pp):**
  - Dòng lãi phải thu tín dụng vượt tốc độ dư nợ trong H1/26: +1.300,6 thực tế − 6.802,7×(+12,3% dư nợ) = **464,9 tỷ/6 tháng** [SX6T TM 15.2; KT25].
  - Quy năm, sau thuế: 744 tỷ. Nhân tổn thất kỳ vọng 17,5% (chính trọng số trục haircut) ra 130 tỷ/năm, tức **0,31pp** trên VCSH 42.446.
  - Dùng tốc độ 2026, KHÔNG dùng tốc độ 2025 (2.998 tỷ vượt ⇒ −1,1pp), vì 9T26 thu tiền đã hồi lên 91%. Tốc độ 2025 nằm ở độ nhạy: **11.439 (−12,6%)**.
- **Phần tồn lãi dự thu trên bảng cân đối được xử lý ở trục haircut, không đếm hai lần.** ROE nền chỉ trừ dòng tương lai; trục haircut xoá phần tồn đã tích luỹ.
- Hình dạng path giữ r3: 2027 thấp do VCSH +20% từ quyền mua. Tất cả **(ước lượng)**.

**Lưới 81 điểm** = 3 kịch bản × 3 trục rủi ro, đưa vào như kịch bản có xác suất, không vào tham số trung tâm (V4):
1. Dịch ROE ±1pp (0,25/0,5/0,25).
2. Haircut phải thu bán nợ 4.101 tỷ 0/25/50% (0,5/0,3/0,2).
3. **Haircut lãi dự thu vượt chuẩn 4.218,6 tỷ** 0/25/50% (0,5/0,3/0,2), sau thuế. Gồm tín dụng 3.830,6 (vượt tỷ lệ 2024 1,854% × dư nợ 30/06/26) và **chứng khoán 388,0** (vượt tỷ lệ 2024 1,841% × AFS 31/12/25) [KT25 TM 15.2, 11.1; SX6T].

| | Tâm | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|---|
| Trước CK (con quyền) | 13.090 | 9.178 | 10.795 | 13.167 | 15.018 | 17.125 |
| **Sau CK 5 tỷ (con quyền)** | **13.042** | **9.144** | 10.756 | 13.119 | 14.963 | **17.062** |
| Sau CK 5 tỷ, **tương đương sau quyền** | 12.433 | 9.315 | | | | 15.650 |
| Sau CK 40 triệu (con quyền) | 13.085 | 9.175 | | | | 17.119 |

Tham số trung tâm (CƠ SỞ, không haircut) sau CK: 13.344.

**V1 — độ nhạy lãi huy động (tâm trước CK 13.090):**

| | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β=1 | 14.834 (+13,3%) | 13.926 (+6,4%) | 12.317 (−5,9%) | 11.601 (−11,4%) |
| β=0,5 | 13.926 | 13.499 | 12.696 | 12.317 |

**Độ nhạy khác (trước CK; không vào base):**

| Phép thử | Tâm | Δ |
|---|---|---|
| **Đối chứng: path r3 (ROE hồi phục về 15,1%, chưa làm sạch)** | 14.660 | +12,0% |
| Tốc độ lãi dự thu 2025 (−1,1pp ROE) | 11.439 | −12,6% |
| Không có trục lãi dự thu | 13.247 | +1,2% |
| ROE hội tụ nửa đường về Ke | 12.696 | −3,0% |
| Bao phủ 80% | 12.637 | −3,5% |
| Không quyền mua | 12.993 | −0,7% |
| Terminal g 6%, RONIC = ROE_T (tương đương WIDE) | 13.809 | +5,5% |
| LC 9.229: chi phí tín dụng 0,89% × 1 năm | 13.072 | −0,1% |
| LC 9.229: tổn thất 5% | 12.991 | −0,8% |
| Phải thu khác Q3 +4.620 mất 25% (không kiểm chứng được) | 12.843 | −1,9% |

**V6** không áp (ngân hàng: RI, không FCFE). **V4:** không có dự án XDCB trọng yếu; quyền mua là dòng vốn vào.

## 6. Q3 — Rủi ro lớn nhất & điều đổi nhận định CẢ HAI chiều

**Rủi ro số 1:** đệm dự phòng mỏng (bao phủ 47%) cộng chất lượng ghi nhận thu nhập. Phải thoái lãi dự thu và xây lại bao phủ cùng lúc ⇒ về vùng XẤU, ~9.600.

| Chiều | Điều kiện (mốc kiểm) | Tác động (con quyền, trước CK) |
|---|---|---|
| ↑ | Lãi huy động 12T −100bp bền | ~14.800 (+13%) |
| ↑ | BCTC KT 2026: lãi phải thu TD/dư nợ ≤ 2,5% **và** thu/ghi nhận ≥ 95% | bỏ trục + bỏ làm sạch 0,3pp ⇒ ~+3–4% (ước lượng) |
| ↑ | ROE đầu kỳ 2026 thực tế ≥ 15% và Q4/26 nhóm 2 giảm, bao phủ ≥ 60% | path r3 thành trung tâm ⇒ ~14.700 |
| ↑ | ROE đầu kỳ ≥ 17% hai năm liền sau quyền mua | TỐT ⇒ ~17.100 |
| ↓ | Lãi phải thu TD > 3,5% dư nợ hoặc thu/ghi nhận < 85% | tốc độ 2025 ⇒ ~11.400 (−12,6%) |
| ↓ | Nhóm 2 + NPL Q4/26 > +20% QoQ, hoặc DP Q4 < 400 khi NPL tăng | XẤU ⇒ ~9.600 |
| ↓ | Lãi huy động +100bp; NHNN hạ room 2027 cho NH dùng kênh LC | ~11.600 |
| ↓ | Room 2026 hết (10,69% > 10,45%) ⇒ LNST Q4 < 1.700 | −350 tỷ ⇒ ≈ −93 đ/cp trực tiếp (ước lượng) |

Mốc kiểm: BCTC Q4/2026 (cuối 01/2027) · BCTC KT 2026 (KPMG, ~03/2027) · ngày chốt quyền mua 25% · room 2027.

## 7. Q4 — Cờ tự động

| Cờ | Kết luận | Lý do |
|---|---|---|
| Gordon P/B CHEAP (1,50x từ ROE5Y 17,2%) | **NHIỄU** | ROE5Y gồm đỉnh 2021–24. CƠ SỞ ROE_T 14,1% @Ke 13,5%, g 6% ⇒ 1,08x = 13.516 ≈ tâm RI |
| FSCORE 3 | ít ý nghĩa với NH | mục 3 |
| D/E 8,39 | bình thường | VCSH/TTS 10,7%, CAR 11,67% |

## 8. Q5 — Thanh khoản & sizing (SAU khoá)

- **Thanh khoản [BQ, 18/11/2025–20/11/2026, `calc/postlock_r4_out.txt`]:** ADV trung vị 250 phiên **96,0 tỷ** (60 phiên 128,2; 20 phiên 139,5); σ ngày 1,60%.
- **Chiết khấu thanh khoản:** CK = σ·√(Q/ADV250). Vị thế 5 tỷ ⇒ **0,37%** (5,2% ADV; 0,52 phiên ở tham gia 10%, 0,26 phiên ở 20%). Vị thế 40 triệu ⇒ 0,03%.
- **V8:** 2–4% NAV/mã nằm trong vài phiên ADV, nên thanh khoản không ràng buộc. **Ràng buộc là định giá:** đề xuất 0% discretionary tại giá hiện tại. Nếu giá ≤ 11.085 (con quyền; ~10.600 sau quyền) ⇒ có thể xét tranche 2%, cần user duyệt.
- **Overhang cung:** quyền mua 25% @10.000; cổ đông nhà nước muốn thoái vốn (nguồn mỏng, kế thừa r2).

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
  - ESOP 2026 — không thấy trong BCTN; NQ ĐHĐCĐ chưa đọc. Ảnh hưởng ước lượng: ESOP thường ≤1% số CP ⇒ ≤ −1% tâm.
  - Ngày chốt quyền mua 25% — chưa xác định; tâm báo theo cơ sở CON QUYỀN, kèm số tương đương SAU QUYỀN (mục 5).
  - Thanh tra NHNN gần nhất.
- **PDF Q3/6T/IR gốc** không còn trong `src/`. Số Q3 truy về `calc/notes_read.md` (đọc ảnh 09/11) và đã được đối chiếu BQ cùng 3 báo. Tải lại cần gọi AJAX của msb.com.vn (`msb_investor_v2_load`), việc này bị chặn trong phiên — **cần user/Mike cho phép hoặc tải tay**.
- **Lint khoá:** cảnh báo L7 (capital_commitments có quyền mua 9.360 trong khi projects rỗng) là **dương tính giả**. Quyền mua là dòng vốn vào, không phải dự án/capex.
- **CET1:** báo cáo không công bố CET1 riêng. CAR cấp 1 2025 = 11,87% là proxy gần nhất, vì VCSH MSB thuần cổ phần phổ thông.

## Phụ lục E — Đính chính so với rev trước

### E.1 r2 → r3, theo skeptic DD_GENERAL r1 (22/11, REFUTED medium)

| # | Hạng mục skeptic | Loại | Xử lý r3 | Tác động tâm (trước CK) |
|---|---|---|---|---|
| 1 | **ROE bình quân (BQ `ROE_Trailing`) nhân trên VCSH đầu kỳ ⇒ ngầm ép ROE về ~13,1% < Ke** (killer) | thiên lệch chiều RẺ, định lượng được | (a) VÀO BASE: quy đổi mọi điểm ROE sang đầu kỳ; cơ sở = ROE đầu kỳ thực tế 2023–26E tự tính (BQ + KT25) | **+13,0%** (12.989 → 14.674 trên cùng lưới r3). Quy ước đầu kỳ GIỮ ở r4; mức neo ROE thì sửa ở E.2 |
| 2 | Lãi dồn tích (thu 20.394 vs ghi nhận 22.349; lãi phải thu TD +19% vs dư nợ +12%), không haircut | thiên lệch chiều ĐẮT | (b) KỊCH BẢN XÁC SUẤT: trục haircut 0/25/50% trên phần vượt tỷ lệ 2024 (3.831 tỷ, cơ sở EY 2024). Bổ sung số kiểm toán 2025: thu/ghi nhận 76%, lãi phải thu TD 3.273 → 6.803 | **−1,0%** |
| 3 | LC miễn truy đòi 9.229 + phải thu khác 18.501 (Q3 +4.720) chỉ có DP chung 38 tỷ | ĐẮT, chưa định lượng | LC: bản chất = bộ chứng từ L/C do MSB phát hành [KT25] ⇒ (b) ĐỘ NHẠY −0,1% / −0,7%. Phải thu khác Q3: (c) KHÔNG KIỂM CHỨNG ĐƯỢC, độ nhạy −1,7% (mất 25%). Không vào base (không có tổn thất quan sát) | 0 (độ nhạy) |
| 4a | Cho vay bên liên quan chưa kiểm | thiếu hạng mục | ĐÃ KIỂM [KT25 TM 42]: 142,6 tỷ (0,07% dư nợ) — không trọng yếu | 0 |
| 4b | TPDN chưa kiểm | thiếu | ĐÃ KIỂM [KT25 TM 11.1]: 1.961 tỷ (4,6% VCSH), DP chung 14,7. 30/09 chưa tách (c) | 0 |
| 4c | CET1 chưa kiểm | thiếu | CAR cấp 1 2025 11,87%, CAR 12,49% [KT25]; CET1 riêng không công bố (c) | 0 |
| 4d | ESOP chưa kiểm | thiếu | BCTN 2025 chỉ có ESOP 2022; KH 2026 = thưởng 20% + quyền mua 25% (đã vào model); ESOP 2026 (c) không kiểm chứng được, ước lượng ≤ 0 | 0 |
| 5 | Ý kiến kiểm toán FY2025 lấy từ nguồn thứ cấp; lý do đổi kiểm toán viên | provenance | ĐÃ ĐỌC GỐC: EY chấp nhận toàn phần, không nhấn mạnh, 26/03/2026 [KT25 P73]. Lý do đổi EY→KPMG: (c) không kiểm chứng được | 0 |
| 6 | `src/*.pdf`, `bq_msb_px.csv`, `*_out`, `LOCK_*` thiếu ⇒ không tái lập | provenance | Thêm `src/bctn_2025.pdf` (+ txt), `calc/bq_msb_fin_r3.csv`, `calc/bq_msb_px_r3.csv`, `model_r3_out.txt/json`, `postlock_r3_out.txt/json`, `LOCK_r3_prerun.txt`, `LOCK_r3_post.txt`. Mô hình r3 chạy lại được từ file khoá. **PDF Q3/6T/IR vẫn thiếu** (tải bị chặn) — mục 10 | 0 |
| 7 | (ngoài skeptic) cập nhật ngày định giá 09/11 → 23/11; ADV/σ 250 phiên mới | cơ học | T0 38/365; ADV250 90,2 → 96,0 tỷ; CK 0,38% → 0,37% | ≈ +0,3% (gộp trong đối chứng #1) |


### E.2 r3 → r4, theo skeptic DD_GENERAL r2 (23/11, `skeptic/r2.json`, REFUTED medium, report_md5 `eee0bc9f…`)

| # | Hạng mục skeptic r2 | Loại | Xử lý r4 | Tác động tâm (trước CK) |
|---|---|---|---|---|
| 1 | ROE nền neo vào LN 2025–26 chưa loại phần lãi dồn tích (thu tiền 76%); chỉ haircut một lần trên số dư | ĐẮT, killer | (a) VÀO BASE có cơ sở độc lập: CƠ SỞ ROE_T = 2026E quan sát 14,4% − 0,3pp (dòng lãi dự thu vượt chuẩn H1/26 × tổn thất kỳ vọng 17,5%). Tốc độ 2025 (−1,1pp) để ở độ nhạy (−12,6%), vì 9T26 thu tiền 91% | gộp với #2 |
| 2 | Path CƠ SỞ đi lên 13,3 → 15,1% trong khi ROE thực giảm 17,6 → 15,3 → 14,4% và CASA mòn | thiên lệch lạc quan | (a) VÀO BASE: bỏ giả định hồi phục, neo T vào 2026E quan sát; XẤU/TỐT ±2,3pp đối xứng (11,8% / 16,4%) | #1 + #2 = **−11,9%** (14.660 → 13.090) |
| 3 | Lãi phải thu từ đầu tư CK 1.208 → 2.180 không xem xét | ĐẮT, thiếu | (a)+(b): phần vượt tỷ lệ 2024 = 388 tỷ [KT25 TM 15.2/11.1], cộng vào trục haircut lãi dự thu (3.830,6 → 4.218,6). Phần còn lại đi theo AFS +48% (chủ yếu TPCP + giấy tờ có giá TCTD) | −0,1% |
| 4 | Cơ sở số CP con quyền/sau quyền không ghi nhãn | trình bày | Ghi nhãn "con quyền"; báo kèm tương đương sau quyền (tâm 12.433); ngày chốt quyền: (c) không kiểm chứng được | 0 (nhãn) |
| 5 | Ke 13,5% nằm ngoài dải 12,3–13,4% | ngược chiều (RẺ) | Giải trình theo luật V1/D4 (mục 5): r của tâm = 13,5%, dải là báo kèm; hai đầu dải +16,3% / +1,2% | 0 |
| 6 | ESOP 2026 chưa kiểm | thiếu | (c) không kiểm chứng được; ước lượng ≤ −1% | 0 |
| 7 | LC 9.229 + phải thu khác 18.501 chỉ một nguồn (PDF Q3/6T thiếu) | provenance | (c) vẫn thiếu: tải lại cần gọi AJAX msb.com.vn, bị chặn trong phiên; LC 2.383 tại 31/12/25 có trong EY | 0 |

**Tổng (sau CK, 5 tỷ, con quyền):**

| | r2 | r3 | r4 |
|---|---|---|---|
| Tâm | 13.018 | 14.621 | **13.042** |
| P10 | 9.675 | 10.538 | **9.144** |
| P90 | 16.373 | 18.796 | **17.062** |
| Luật 4 (0,85×tâm) | 11.065 | 12.428 | 11.085 |

- r4 so với r3: **−10,8%**. r4 so với r2: **+0,2%**.
- Nhãn sau khoá (giá 16.550 @20/11): TRONG vùng, phần trên (82% trọng số < giá); luật 4 KHÔNG đạt — **không đổi lớp nhãn so với r2/r3**.
- Lưu ý thứ tự: khoá r4 lập SAU khi đã thấy giá (pha sau khoá r3). Lý do khoá lại là skeptic r2, mỗi thay đổi có nguồn BCTC/BQ ghi ở bảng trên.
