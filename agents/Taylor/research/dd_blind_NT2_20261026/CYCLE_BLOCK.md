# KHỐI CHU KỲ — NT2 (CTCP Điện lực Dầu khí Nhơn Trạch 2, HOSE) — viết mù 2026-10-26

```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có
  da_doc_DD_cu_cua_ma_nay          : không
  da_biet_verdict_truoc            : không (không biết verdict của fleet; xem vi_pham_vo_tinh về khuyến nghị CTCK lọt qua tóm tắt tìm kiếm)
  quy_Q (mới nhất đã công bố)      : 2026Q3       ngày công bố: 2026-10-20..22
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2
  cycle_block_md5                  : xem LOCK.txt
  cycle_block_commit               : xem LOCK.txt
  thoi_diem_khoa (ICT)             : 2026-10-26T12:03+07:00 (thời điểm soạn; khoá thật xem LOCK.txt)
  vi_pham_vo_tinh                  : có, mức nhẹ, không phải nội dung KQKD Q3/2026:
     (1) Tóm tắt WebSearch tự in ra khuyến nghị CTCK về NT2: ACBS "MUA, giá mục tiêu 2026 26.700đ" (bản cập nhật Q2/26)
         và tiêu đề "NT2: Khuyến nghị khả quan, giá mục tiêu 26.000đ" (thuonghieucongluan, không rõ ngày, KHÔNG mở).
         Không mở các file ACBS/ABS/BSC/Mirae; chỉ dùng số bảng cân đối Q2/26 mà tóm tắt trích từ chúng.
     (2) Đã mở báo cáo MBS 01/04/2016 (để lấy kỳ hạn PPA, hợp đồng khí, lịch khấu hao) — có giá mục tiêu
         năm 2016 (37.300đ), cũ 10 năm, không dùng.
     (3) TEMPLATE.md có sẵn 1 con số của NT2 (Cash BCTC 5.374 tỷ, không rõ kỳ) — không dùng.
     Không đọc BCTC Q3/2026, không đọc bài/nhận định nào về KQKD Q3 hay 9T/2026. Giá cổ phiếu dùng tới 23/10/2026
     (đã gồm phản ứng giá sau công bố Q3, đúng như mẫu cho phép).
```

**Loại ngành:** annuity hợp đồng (PPA với EVN/EPTC theo cơ chế Qc×Pc cost-plus + Qm theo giá thị trường), có **thành phần chu kỳ**
là mức huy động (thủy văn) và giá khí neo dầu. Vì Qc chiếm 87% sản lượng H1/26 (1,87/2,14 tỷ kWh [WEB-2]), tôi vẫn điền đủ B và C
nhưng C bị khoá ở "không xác định" do thiếu chuỗi đầu ra (xem B).

## A. Biên hiện tại so với lịch sử chính mã (dữ liệu đến 2026Q2)
- Cửa sổ: `2013Q1–2026Q2, N = 54 quý TTM` (doanh thu bắt đầu 2011Q4; 2012Q1 thiếu dòng ⇒ TTM đầu tiên đủ 4 quý là 2013Q1).
  Số chu kỳ thấy được **k ≈ 2** (đỉnh 2015–16 → đáy 2024 → lên 2025–26) ⇒ phân vị chỉ là **mô tả**.
- **Biên LNST TTM = 14,3%** (NP TTM 1.350 tỷ / DT TTM 9.446 tỷ), phân vị **82** [BQ `ticker_financial` NP_P0, Revenue_P0;
  UL tổng 4 quý, script `src_step1/calc_A_E.py`].
- **Biên gộp TTM = 16,2%**, phân vị **77** [BQ GPM_P0]. ⚠️ Kiểm GPM_P0: BQ từ 2018Q1 là TTM, trước 2018 là quý đơn lẻ (tôi
  tự quy về TTM); 2021Q4 trùng y 2021Q3 (dòng stale). So với số năm: 2024 BQ 0,87% vs [BC] LN gộp 51,5 tỷ/DT ≈5.957 tỷ = 0,86% → khớp;
  2025 BQ 15,7% vs [BC] 1.093/7.803 = 14,0% → **lệch 1,7đ%** (DT BQ 7.958 vs 7.803, chênh ≈155 tỷ, trùng cỡ với khoản bù tỷ giá 155 tỷ
  được nhắc ở [WEB-1]; NP 2025 BQ 1.130 vs [BC] "gần 1.000"). Chưa lấy được BCTC 2025 kiểm toán ⇒ **dùng biên LNST làm chỉ số chính**.
- **Đổi mô hình — cắt chuỗi:** máy móc khấu hao 14 năm từ 2011 (kéo từ 10→14 năm Q3/2014 [WEB-3]) ⇒ hết khấu hao ~2025:
  khấu hao H1/26 76,5 tỷ vs H1/25 343,5 tỷ [WEB-2]. Tiết kiệm ≈534 tỷ/năm trước thuế ≈ 4,5đ% doanh thu TTM (UL: 534×0,8/9.446).
  **Biên LNST TTM loại hiệu ứng hết khấu hao ≈ 9,8% (ước lượng) ⇒ phân vị ≈ 44** (24/54 quý thấp hơn). Chuỗi sau đổi mô hình mới 2–4 quý,
  không đủ để tính phân vị riêng. Ngoài ra nợ dài hạn = 0 từ 2020Q2 [BQ LtDebt_P0] — một lần đổi mô hình khác (hết chi phí lãi vay dài hạn).

## B. Giá đầu ra và đầu vào chính
| Biến | Vai trò | Gần nhất | Trung vị 5 năm | Phân vị 10 năm | Nguồn |
|---|---|---|---|---|---|
| Giá bán bình quân (ASP) | ra | ≈2.334 đ/kWh H1/26 (−8,9% yoy) | **CHUỖI THIẾU** | — | [WEB-2] |
| Giá thị trường điện (VWEM/SMP) | ra (phần Qm 10–25%) | — | **CHUỖI THIẾU** | — | không có feed |
| Qc (sản lượng hợp đồng) | ra (khối lượng) | 1,87 tỷ kWh H1/26 (+17,8%) | **CHUỖI THIẾU** (2025 tổng SL 3,12 tỷ kWh [WEB-1]; 2015 5,5 tỷ kWh [WEB-3]) | — | [WEB-2] |
| Giá khí đầu vào NT2 | vào (lớn nhất; pass-through vào Pc) | ≈9,98 USD/MMBTU H1/26 (+4,4%) | **CHUỖI THIẾU** (2015: 5,4–6,1 USD [WEB-3]) | — | [WEB-2] |
| Brent tháng (proxy giá khí neo dầu/HSFO) | vào | 116,8 USD (2026-09); TB 12T 86,4 | 82,7 (tháng); 82,4 (TB12T) | **97,9** (tháng); 87,9 (TB12T) | [FEED brent_monthly.csv] |
| ONI (proxy thủy văn; dương = El Niño = khô ⇒ huy động nhiệt điện tăng) | cầu huy động | +2,16 (JAS-2026) | −0,28 | **98,0** | [FEED oni_index.csv] |
| USD/VND (giá khí & giá điện tính theo USD [WEB-3]) | trung tính | 25.650 (VCB CK mua 26/10) | **CHUỖI THIẾU** (feed từ 2026-07) | — | [FEED vcb_fx_rate.csv] |

## C. Pha chu kỳ: **KHÔNG XÁC ĐỊNH** (nghiêng GIỮA-LÊN về huy động; biên cao một phần là CẤU TRÚC, không phải chu kỳ)
- Luật cơ học 80/20: A (biên LNST) = 82 ≥ 80, nhưng biến đầu ra (ASP, VWEM, Qc) đều **CHUỖI THIẾU** ⇒ theo mẫu không được kết luận
  ĐỈNH/ĐÁY. Không lệch khỏi luật.
- Ủng hộ "đang ở nửa trên/đi lên": (1) sản lượng H1/26 2,14 tỷ kWh +56% yoy, Qc +17,8% [WEB-2]; (2) ONI +2,16, phân vị 98/10 năm
  [FEED] ⇒ El Niño mạnh, mùa khô 2027 thủy điện yếu ⇒ huy động khí cao kéo dài tới ~2027Q2.
- Chống: loại hiệu ứng hết khấu hao thì biên LNST TTM chỉ ≈9,8% (phân vị ≈44, ước lượng) — tức biên *chu kỳ* đang ở **giữa**, phần cao là
  cấu trúc; ASP giảm 8,9% yoy; Brent nhảy lên 116,8 (phân vị 98) đẩy giá khí, phần Qm bị trần khung giá (3.410,64 đ/kWh [WEB-2]) ép biên.
- Cơ chế cú sốc: đáy 2024 là **cầu/huy động sập** (DT Q1/24 chỉ 262 tỷ, NP −158 tỷ [BQ]; biên gộp năm 0,9%). Rủi ro hiện tại là loại khác:
  **chi phí đầu vào tăng** (dầu) khi giá bán bị trần — với Qc thì phần lớn chuyển vào Pc, nên tác động chủ yếu lên Qm và lên biên % (mẫu số
  phình). So PB đáy chỉ nên so với đáy 2024 (cùng loại "cầu").
- Cung: Nhơn Trạch 3&4 (LNG, 1.624 MW, cùng cụm Nhơn Trạch) COD ~11–12/2025, H1/26 đã phát ≈2,5 tỷ kWh [WEB-4] ⇒ cạnh tranh huy động
  trực tiếp 12–24 tháng tới. Nguồn khí hiện hữu của NT2 dự kiến cạn ~2030 [WEB-2]. Tồn kho ngành: không áp dụng.

## D. Neo chính sách và rủi ro cấu trúc
| Neo/rủi ro | Loại | Ngày | Chu kỳ / cấu trúc | Nguồn |
|---|---|---|---|---|
| Nhà máy CCGT 750 MW vận hành thương mại | hạ tầng | 2011 (tuổi ~15 năm) | cấu trúc (vòng đời) | [WEB-3] |
| Hợp đồng khí dài hạn PV GAS, 25 năm | hợp đồng | ký 2010 ⇒ hết ~2035 (ước lượng) | cấu trúc | [WEB-3] |
| Cơ chế giá khí theo thị trường | hợp đồng/chính sách | từ 08/2015 | chu kỳ (neo dầu) | [WEB-3] |
| PPA số 07/2012/HĐ-NMĐ-NT2 với EVN/EPTC; giá chính thức PL sửa đổi số 04 | hợp đồng | PL04 ngày 28/05/2014; kỳ hạn gốc 10 năm 2011–2020; **trạng thái sau 2020: CHƯA XÁC MINH** | cấu trúc | [WEB-3], [WEB-5] |
| Trả hết nợ vay dài hạn | tài chính | 2020Q2 (LtDebt_P0 = 0) | cấu trúc | [BQ] |
| Hết khấu hao máy móc (14 năm) | kế toán | ~2025 (H1/26 KH 76,5 vs 343,5 tỷ); nguyên giá 8.353 tỷ tại 30/06/2026 | cấu trúc (+LN, nhưng báo hiệu tài sản già) | [WEB-2], [WEB-3] |
| Nguồn khí hiện hữu cạn kiệt | đầu vào | dự kiến ~2030 | cấu trúc — **rủi ro dòng tiền có thời hạn** | [WEB-2] |
| PL13 HĐ khí: bổ sung Hải Thạch–Mộc Tinh 2026–2039, 7,38 USD/MMBTU +2%/năm; phần của NT2 chưa công bố | hợp đồng (chờ ĐHCĐ) | 2026 (bài 12/08/2026) | cấu trúc | [WEB-2] |
| Khung giá phát điện 2026 CCGT tối đa 3.410,64 đ/kWh (khí 11,98 USD) | chính sách | năm 2026 | chu kỳ (năm) | [WEB-2] |
| NT3&4 LNG 1.624 MW vào vận hành | cạnh tranh | COD ~11–12/2025 | cấu trúc | [WEB-4] |
| Thuế TNDN thực tế ≈20% (LNTT 503,8 → LNST 403,0 tỷ Q2/26); ưu đãi cũ đã hết | thuế | Q2/2026 | cấu trúc | [BCTC Q2/26 tr.2] |
| Kế hoạch cổ tức tiền 2025: 20%; 2026–27: 25%; 2028: 30% | chính sách công ty | công bố ~03/2026 | — | [WEB-1] |
- **Dòng tiền lõi CÓ thời hạn**: tài sản 15 tuổi, hợp đồng khí tới ~2035, khí hiện hữu cạn ~2030 ⇒ E định giá theo dòng tiền có thời hạn.
  Không thấy rủi ro "mất giấy phép" kiểu §2.5; rủi ro là **cạn nhiên liệu/giá khí mới cao hơn** và mất thứ tự huy động trước LNG.

## E. PE/PB trên LN chuẩn hoá (bảng cân đối 30/06/2026)
- Vốn hoá = 24.100 đ (đóng cửa 23/10/2026, BQ `ticker`) × 287,876 tr cp [BQ OShares] = **6.938 tỷ**.
- Net cash = tiền + tiền gửi **4.727 tỷ** [WEB-6: ABS/Mirae trích BCTC Q2/26; BQ Cash_P0 chỉ 5,2 tỷ — thiếu tiền gửi] − vay **1.661 tỷ**
  [BQ StDebt_P0 = DNSE WEB-7] = **3.066 tỷ**. ⚠️ Vay ngắn hạn tài trợ phải thu EVN; chưa rõ cổ tức 2025 (2.000 đ/cp ≈ 576 tỷ) đã chi chưa.
- Lãi ròng trên net cash sau thuế ≈ 3.066 × 6,8% × 0,8 = **167 tỷ** (ước lượng; 6,8% = Big4 12T [FEED deposit_rate_vn_events.csv]).
- **LN chuẩn hoá (chọn: trung vị LNST năm 2013–2025, 13 năm, cùng cửa sổ A)** = **760 tỷ** [BQ, UL]; loại một lần: 2014 có hồi tố giá điện
  658 tỷ [WEB-3] ⇒ 2014 dùng ≈308 tỷ (ước lượng); 2025 dù 1.000 hay 1.130 đều nằm nửa trên, không đổi trung vị.
  Biến thể cấu trúc (cộng tiết kiệm khấu hao 534×0,8): **≈1.187 tỷ (ước lượng)**.
- **PE thô** = 6.938/760 = 9,1x. **PE chuẩn hoá ex-cash** = (6.938 − 3.066)/(760 − 167) = **6,5x**; biến thể hết-khấu-hao: 3.872/(1.187−167) = **3,8x (ước lượng)**.
- **Định giá dòng tiền có thời hạn** (vì D): FCF lõi ≈ LN lõi (khấu hao ≈ capex duy trì, ước lượng), 9 năm tới ~2035, chiết khấu 12%, không
  giá trị cuối: hệ số 5,33 ⇒ 593×5,33 = 3.160 tỷ (cơ sở) … 1.020×5,33 = 5.435 tỷ (hết-KH) + net cash 3.066 ⇒ **6.226–8.501 tỷ ≈ 21.600–29.500 đ/cp**
  (ước lượng) vs giá 24.100. Rủi ro lớn nhất của dải này: lượng khí sau 2030.
- **PB** = 24.100 / BVPS 18.709 [BQ 2026Q2] = **1,29x** (tài sản vô hình không đáng kể — chưa đối chiếu BCTC, ước lượng PB hữu hình ≈1,29x).
  Đáy cùng loại (huy động sập 2024–25): PB TB quý 2024Q4 1,34 (min 1,26); 2025Q2 1,23 (min 1,09) [BQ, `src_step1/pb_history.txt`].
  ⇒ PB hiện tại ngang vùng đáy 2024–25 dù biên TTM ở phân vị 82 (nếu cổ tức 2025 chưa chi, BVPS sau chi ≈16.700 ⇒ PB ≈1,44, ước lượng).

## F. DỰ BÁO CÓ THỂ BÁC BỎ
```
FORECAST
  indicator   : biên LNST TTM của NT2 = Σ NP_P0 / Σ Revenue_P0 của 4 quý 2026Q1–2026Q4
  source      : tav2_bq.ticker_financial (ticker='NT2', quarter 2026Q1..2026Q4; đối chiếu NPM_P0 quarter='2026Q4' và BCTC Q4/2026)
  baseline    : 14,3% (TTM 2025Q3–2026Q2: 1.350 / 9.446 tỷ)
  call        : lớn hơn hoặc bằng 12,0%
  horizon     : quý 2026Q4
  due_date    : 2027-01-31 (BCTC Q4 thường công bố ~20/01 + 10 ngày)
  p           : 0.60
  persistence : giữ phía hiện tại (≥ 12,0%) ⇒ call ĐÚNG; persistence và call trùng hướng — điểm chấm phải so với p, không với baseline
  void_if     : đổi chuẩn mực kế toán/hồi tố lớn (>200 tỷ, vd hồi tố giá điện hay bù tỷ giá ghi nhận một lần); M&A/sáp nhập nhà máy;
                đình chỉ giao dịch; NT2 dừng máy >60 ngày vì sự cố ngoài kế hoạch
```
Lý do p=0,60 (ước lượng): khấu hao thấp giữ ~4,5đ% biên; El Niño giữ huy động cao; nhưng Brent 116,8 (09/2026) phình doanh thu qua Pc
và ép phần Qm, Q4/2025 cơ sở có thể chứa khoản một lần (bù tỷ giá ≈155 tỷ) ⇒ TTM có thể tụt về 11–13%.

## Nguồn
- [BQ] `tav2_bq.ticker_financial` quarter ≤ '2026Q2' (`src_step1/nt2_fin_le2026Q2.csv`); `tav2_bq.ticker` Price (`src_step1/nt2_price_quarterly.csv`, đóng cửa 23/10/2026).
- [FEED] `data/brent_monthly.csv`, `data/oni_index.csv`, `data/vcb_fx_rate.csv`, `data/deposit_rate_vn_events.csv` (`src_step1/calc_B.py`).
- [BCTC Q2/26] https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%202/NT2_Baocaotaichinh_Q2_2026.pdf (CV 899/CPNT2-TCKT 20/07/2026; chỉ đọc được 3 trang giải trình, phần bảng là ảnh scan) — truy cập 26/10/2026.
- [WEB-1] https://doanhnhan.baophapluat.vn/dien-luc-dau-khi-nhon-trach-2-nt2-du-kien-tang-ty-le-co-tuc-len-30-tren-nen-tang-loi-nhuan-nghin-ty.html (02/03/2026; số năm 2025 [BC]) — truy cập 26/10/2026.
- [WEB-2] https://nhadautu.vn/san-luong-va-loi-nhuan-tang-manh-nt2-tim-them-nguon-khi-moi-d106917.html (12/08/2026; số H1/26) — truy cập 26/10/2026.
- [WEB-3] https://www.mbs.com.vn/media/v3gpiuha/nt2_bao-cao-lan-dau_01-april-2016.pdf (01/04/2016; PPA, khí, khấu hao) — truy cập 26/10/2026.
- [WEB-4] tóm tắt WebSearch về NT3&4 (tapchicongthuong.vn, vneconomy.vn, baodauthau.vn) — không mở trang, truy cập 26/10/2026.
- [WEB-5] tóm tắt WebSearch (KBSV/KIS 2022, baodautu.vn) — số hiệu PPA 07/2012/HĐ-NMĐ-NT2 — không mở trang.
- [WEB-6] tóm tắt WebSearch trích ABS (NT2_260730_Note) và Mirae: 4.727 tỷ tiền+tiền gửi 30/06/2026 — không mở file.
- [WEB-7] https://www.dnse.com.vn/senses/tin-tuc/bctc-quy-22026-nt2-loi-nhuan-sau-thue-cong-ty-me-q22026-tang-2353-so-voi-cung-ky-dat-403-ty-dong-35248825 (20/07/2026) — truy cập 26/10/2026.
