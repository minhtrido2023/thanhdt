# ADDENDUM 5F — NT2 · bước 3c (5F tầng b + moat vào mô hình) · job `Taylor_20261107_172009` (resume của `Taylor_20261107_131635`) · 07–08/11/2026

> Bổ sung cho `REPORT_r2.md` (giữ nguyên mọi phần khác; `calc/model_r2.py` md5 `9c8f76f2…` khớp `calc/LOCK_r2_md5.txt` — không sửa). Số mới: `calc/model_5f.py` → `model_5f_out.txt/json`; `calc/model_5f_peer.py` → `model_5f_peer_out.txt`; `calc/model_5f_ebitda.py` → `model_5f_ebitda_out.txt`. BQ đo 07–08/11/2026 (`tav2_bq.ticker_financial`, `SELECT DISTINCT`, dòng Q4 của EBITM_P0/GPM_P0 = cả năm — biên là TTM, bài học A đính chính 07/11). Giá 22.650 đ (04/11, ex-div). Đơn vị tỷ đồng.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **LÀM MỚI** (không có dòng NT2 trong `data/moat_tags.csv`, không có `kb/projects/nt2-dd-*.md`, DD 26/10 không có mục 5F)
**Loại hình**: IPP nhiệt điện khí 1 nhà máy, bán điện cho người mua duy nhất (EVN/EPTC) theo PPA + một phần thị trường (FMP); mua khí từ 1 nhà cung cấp (PV Gas, GSA). Không tái đầu tư, có thời hạn.

| Lực | Đánh giá | Bằng chứng (nguồn) |
|---|---|---|
| Người mua | **RẤT MẠNH** (độc quyền mua) | 1 khách EVN/EPTC; Qc phân bổ hằng năm bởi NSMO/BCT: Qc Q3/26 1.073 tr kWh (+24%), 2024 Qc thấp ⇒ LNST cả năm 83 tỷ (DD 26/10 §3 [CTCK, BQ]); phải thu KH 4.252 (BCTC 30/09/26 tr.2) |
| Nhà cung cấp | **MẠNH** | 1 nguồn khí PV Gas (GSA đến 31/12/2036 — 1 nguồn, **cần kiểm chứng**); khí nội địa suy giảm từ ~2031 (DD 26/10 §5); pass-through nhiên liệu cho phần Qc, phần vượt Qc bán FMP ~1.426–1.430 đ/kWh < chi phí khí ~1.940 đ/kWh (DD 26/10 §2 [substack 13/10]) |
| Gia nhập mới | TRUNG BÌNH | cần giấy phép/QHĐ VIII + PPA; nhưng EVN chủ động gọi thầu nguồn mới (LNG, NLTT) — rào cản không thuộc về NT2 |
| Thay thế | MẠNH, tăng dần | NLTT + LNG mới cạnh tranh thứ tự huy động; Qc/Qm Q3/26 ~92% [CTCK] nhưng biến động lớn theo năm |
| Cạnh tranh nội ngành | TRUNG BÌNH | huy động theo giá trên thị trường điện; NT2 EBITM TB 2015–25 **12,0%** vs peer nhiệt điện nội địa 5,4–12,6% (bảng §2) |
| **Lực 6 — đồng hồ** | **CÓ, cứng** | PPA hết ~10/2036, GSA 31/12/2036 (1 nguồn, cần kiểm chứng) ⇒ ≤10 năm; khí nội địa cạn dần |

**Ba điều kiện moat bền (bài học B — cả hai phía):**
(i) Lợi nhuận siêu ngạch nhiều chu kỳ — **KHÔNG ĐẠT**. NT2 (BQ, quý 2026Q3): ROIC5Y **12%**, ROIC10Y **12%**, ROIC_Min5Y **−1%**, ROIC_Min10Y **−1%** (năm 2024) vs Ke/WACC 13,5% (NT2 gần không vay ⇒ WACC≈Ke). ROE riêng: ROE5Y 14%, ROE3Y 13%, ROE_Min5Y 2%. Phía thuận: EBITM 2018–2022 ổn định 11–13%, 2025 15%; phía nghịch: 2016 6%, 2023 7%, 2024 −0%. (`ROIC_Trailing` BQ cho 0,57–0,87 các năm 2018–25 — bất thường, KHÔNG dùng.)
(ii) Cơ chế rào cản gọi tên được — **có nhưng là của hợp đồng, không phải của DN**: PPA/GSA + vị trí cụm Nhơn Trạch–đường ống khí (CONTRACT/LOCATION).
(iii) Không có đồng hồ — **KHÔNG ĐẠT**: hợp đồng hết 2036.

**moat_tier = NONE · moat_type = CONTRACT/LOCATION · moat_durable = false.**
**Rủi ro số 1**: Qc do EVN/NSMO phân bổ hằng năm (người mua độc quyền) + đồng hồ PPA/GSA 2036 — biến LN thành dao động theo Qc/thuỷ văn chứ không phải annuity.

## 2. Moat trong mô hình — **NHẤT QUÁN luật 3c trên cơ sở so sánh được (EBITDA); mô hình KHÔNG đổi**
- Kênh RONIC: r2 không tái đầu tư, giá trị sau thời hạn = 0 ⇒ **không có kênh RONIC >Ke** (đúng luật).
- Kênh biên — kiểm theo bài học C, **hai cơ sở cho kết luận ngược nhau**:
  - Cơ sở EBIT: LNST trung tâm 800 ⇒ biên EBIT ngầm **11,06%** (DT chuẩn hoá 7.137 = TB 2016–25 tổng Revenue_P0 4 quý) > EBITM TB ngành 9,2–10,5% ⇒ *có vẻ* giữ biên riêng.
  - Nhưng NT2 đã **khấu hao hết máy chính từ cuối 2025** (KH 556 → 153 tỷ/năm, DD 26/10 §2 [BC]); EBITM peer vẫn chứa khấu hao vốn đầu tư ban đầu (D&A/DT TB: POW 10,2%, HND 12,2%, QTP 12,2%, PGV 10,8%; NT2 lịch sử 8,0%). So EBIT ⇒ **trừ khấu hao hai lần**.
  - Cơ sở EBITDA (`calc/model_5f_ebitda_out.txt`; BQ EBITDA_P0 dòng Q4 = TTM cả năm / tổng DT 4 quý, 2015–25): mô hình **13,2%** (= 11,06% + KH 2,14%) vs peer trung vị **20,2%** / trung bình **17,1%** (6 peer); bỏ PPC (EBITDA<EBIT — dữ liệu lạ) 20,8/19,3%; chỉ POW (khí) 19,5%; NT2 tự thân 20,1%. **Mô hình thấp hơn TB ngành 6,3–8,3 điểm** ⇒ không giữ biên trên ngành; khoảng chênh đủ lớn để peer có capex duy trì 2–5% DT vẫn không đảo (capex duy trì peer **cần kiểm chứng**).
- ⇒ Không thưởng moat (NONE), không cộng premium, **không cần ép thêm**. Chiết khấu giữ quy ước r2 (năm 1 = t=1 cuối năm, tái dùng nguyên `val` — bài học H). Cờ pháp lý vẫn chỉ WARNING, không chạm base (bài học E).

| Peer nhiệt điện **nội địa** (TB 2015–25) | POW | PPC | QTP | HND | PGV | BTP |
|---|---|---|---|---|---|---|
| EBITM (dòng Q4) | 9,3% | 7,9% | 12,6% | 10,1% | 10,0% | 5,4% |
| Biên EBITDA | 19,5% | 6,2% | 24,7% | 22,3% | 20,8% | 9,2% |
Peer không phải đối thủ cùng loại PPA khí (chỉ POW có nhà máy khí; PPC/QTP/HND than; PGV hỗn hợp; BTP khí-dầu cũ) ⇒ kết luận nêu theo khoảng peer.

## 3. Kết quả (sau CK thanh khoản 5 tỷ; nhãn = giá so P10/P90)
| Bản | LNST tâm | Tâm | P10 / P50 / P90 | % trọng số < giá | Giá/tâm | Nhãn |
|---|---|---|---|---|---|---|
| **r2 hiện hành = headline 3c (không đổi)** | 800 | **23.617** | 18.386 / 23.669 / 28.278 | 37,5% | −4,1% | **TRONG** |
| (cận dưới, đếm 2 lần KH) ép EBIT về trung vị 6 peer | 719 | 22.151 | 16.846 / 22.194 / 26.970 | 57,5% | +2,3% | TRONG |
| (cận dưới) ép EBIT về TB 6 peer / khoảng theo chọn peer | 695 / 699–768 | 21.701 / 21.787–23.035 | 16.373 / 16.464–17.774 | 45–67,5% | +4,4…−1,7% | TRONG |
| (tham chiếu) EBIT về TB riêng NT2 12,0% | 854 | 24.594 | 19.412 / 24.650 / 29.148 | 30,0% | −7,9% | TRONG |
Bản ép-EBIT tịnh tiến CẢ lưới (đối xứng hai phía). Cỡ sleeve thật 10–40 tr: r2 23.817–23.827, cận dưới 22.338–22.347 — nhãn không đổi. Giá cách P10 ≥ ~4.300 đ và cách P90 ≥ ~3.900 đ ở mọi bản ⇒ **không ở ranh giới**.

## 4. Độ nhạy WIDE / NARROW / NONE (nếu moat bị đánh giá sai)
| Moat giả định | Cách mô hình hoá | Tâm sau CK | P10 / P90 | Nhãn |
|---|---|---|---|---|
| WIDE | sau 2036 dòng tiền vận hành tiếp VÔ HẠN ở RONIC=Ke (g=0) | 28.266 (+19,7%) | 21.012 / 34.981 | TRONG |
| NARROW / NONE (không bền ⇒ không thưởng) | = r2 (biên EBITDA đã dưới ngành, TV=0) | 23.617 | 18.386 / 28.278 | TRONG |
| NONE + chọn cơ sở EBIT (bảo thủ nhất) | ép EBIT về ngành | 21.701–23.035 | 16.373–17.774 / 26.568–27.758 | TRONG |
Nhãn TRONG vững trên mọi giả định moat; chỉ tâm dịch (−8% … +20%).

## 5. Thay đổi so với báo cáo hiện hành
**Không đổi**: tâm 23.617, P10/P50/P90 18.386/23.669/28.278, nhãn TRONG vùng. Moat NONE (làm mới) ⇒ không thưởng; mô hình r2 đã không chứa premium moat (TV=0 sau 2036; biên EBITDA ngầm 13,2% < TB ngành ~17–21%). Điểm cần Mike/user chọn: **cơ sở so biên** — nếu duyệt "EBIT" (không hiệu chỉnh khấu hao đã hết) thì cận dưới tâm 21.701–23.035, nhãn vẫn TRONG. Không sửa REPORT_r2/SUMMARY, không ghi dd_price_zones. 5F non-PIT ⇒ chỉ DD sống, không backtest.

## 6. Đề xuất dòng `data/moat_tags.csv` (chỉ ĐỀ XUẤT, không ghi)
```
NT2,NONE,CONTRACT/LOCATION,L,"Single-plant gas IPP: single buyer EVN sets annual Qc (2024 full-year NP 83bn), single gas supplier PV Gas, PPA ~10/2036 + GSA 12/2036 clock (1 source, verify), domestic gas declining from ~2031; ROIC5Y 12%/ROIC_Min5Y -1% vs Ke 13.5% - no multi-cycle excess return",2026-11-07,5f_dd_taylor,N
```
entry = L (ngành phát điện bán cho người mua độc quyền, giá điều tiết — kém hấp dẫn cấu trúc; bài học G). moat_upgrade = N.
