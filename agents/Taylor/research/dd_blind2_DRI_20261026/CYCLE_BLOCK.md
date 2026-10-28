# CYCLE_BLOCK — DRI (CTCP Đầu tư Cao su Đắk Lắk) · DD mù bước 1 · job `Taylor_20261026_054006` · 2026-10-26

> Mẫu: `research/dd_template_v2_20261026/TEMPLATE.md` (v2). READ-ONLY, không phải khuyến nghị, không verdict.
> Q = 2026Q3 (CHƯA công bố, dự kiến 30/10/2026) · Q−1 = 2026Q2. Mọi số tài chính dừng ở 30/06/2026.
> Giá tham chiếu **15.400 đ (đóng cửa 23/10/2026, BQ `ticker`)** · 73.200.000 CP ⇒ vốn hoá **1.127,3 tỷ**.
> Nhãn: [BQ] `tav2_bq` · [BCTC] BCTC hợp nhất Q2/2026 gốc (dri.com.vn, phê duyệt 27/07/2026, bản scan) ·
> [GT] công văn giải trình LN Q2/2026 · [BCTN] Báo cáo thường niên 2025 (vietstock static, 14/04/2026) ·
> [FEED] file `data/` · [UL] ước lượng của tôi (có công thức).

```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có  (BCTC Q3/2026 chưa tồn tại tại thời điểm viết)
  da_doc_DD_cu_cua_ma_nay          : không
  da_biet_verdict_truoc            : không
  quy_Q (mới nhất đã công bố)      : 2026Q3 theo dispatch = quý SẮP công bố   ngày công bố dự kiến: 2026-10-30
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2
  cycle_block_md5                  : xem LOCK.txt (md5 tính trên chính file này)
  cycle_block_commit               : chưa commit (dispatch chỉ yêu cầu khoá md5 + giờ ICT)
  thoi_diem_khoa (ICT)             : xem LOCK.txt
  ghi_chu_mu:
   - Không mở mike/kb/projects, kb/memory, research/dd_*/sector_frames_* (ngoài dd_template_v2), events_buffer,
     discretionary_funnel*. Không tìm bus về DRI. 4 file data/rubber_cyclical*.md|csv, rubber_watch.md,
     fertchem_rubber_verdict.json có chữ "DRI" (grep -c) ⇒ KHÔNG mở; chỉ dùng rubber_monthly.csv/rubber_weekly.csv.
   - Context tự nạp (CLAUDE.md/coding_guidelines §27) có nhắc "case TV1/DRI 2026-08-11" về đối soát fill lệnh —
     không chứa nhận định/verdict cơ bản về DRI.
   - WebSearch 2 lần, từ khoá "...DRI báo cáo tài chính quý 2 năm 2026" và "...website ... báo cáo tài chính pdf 2026"
     (không chứa quý 3/Q3/khuyến nghị/giá mục tiêu/KQKD). Tóm tắt trả về số Q2/2026 + Q2/2025 và tiêu đề tin
     "lãi bán niên kỷ lục" (Q2/H1, không phải Q3); KHÔNG lộ số Q3/2026, KHÔNG lộ khuyến nghị/giá mục tiêu CTCK.
   - Có đọc BCTN 2025 gồm cả phần kết quả năm 2025 (năm trước Q, mẫu cho phép BCTC kiểm toán năm trước) và
     kế hoạch 2026 của ĐHĐCĐ (thông tin công bố trước Q).
```

**Loại ngành:** chu kỳ hàng hoá (cao su thiên nhiên; 1 pháp nhân con 100% tại Champasak, Lào — Daklaoruco,
8.592,3 ha cao su, 465,67 ha điều, 30,48 ha sầu riêng mới; nhà máy 18.000 tấn/năm) [BCTN]. Cao su ≈ 93,6%
doanh thu 2025 (661,70/707,12 tỷ) [BCTN]; Q2/2026 100% doanh thu là mủ cao su [BCTC 6.1].

## A. Biên hiện tại so với lịch sử chính mã (dữ liệu đến 2026Q2)
- Cửa sổ: **2017Q1–2026Q2, 38 quý, 35 cửa sổ TTM**; số chu kỳ giá thấy được k ≈ 1,5 (đỉnh 2017 → đáy 2019–20
  → nhịp 2021 → đáy 2023 → lên 2024–26). k ≤ 3 ⇒ phân vị là MÔ TẢ.
- **Kiểm `GPM_P0` thất bại** ⇒ không dùng biên gộp BQ: Q2/2026 BQ 0,392 vs BCTC **44,52%** (93,560/210,147);
  Q2/2025 BQ 0,432 vs BCTC **34,11%** (38,653/113,320). Dùng biên LNST.
- **Biên LNST TTM** (BQ, `NP_P0/Revenue_P0` cộng 4 quý) = **25,5%**, phân vị **94,3** (min 2,2% TTM 2020Q2,
  trung vị 13,4%, max 26,3% TTM 2025Q2). Sửa Q2/2026 theo BCTC (LNST CĐ mẹ 68,289 tỷ thay vì BQ 63,79):
  TTM = (38,98+40,60+78,42+68,29)/(184,12+196,75+279,77+210,15) = 226,3/870,8 = **26,0% ⇒ cao nhất chuỗi (p=100)**.
- Biên gộp từ BCTC (chỉ có vài điểm): Q2/26 44,5% · H1/26 41,6% · H1/25 39,4% · Q2/25 34,1%.
- Đổi mô hình cần ghi: năng suất tăng 1,34 → 1,81 tấn/ha (2024→2025) [BCTN], do cây trưởng thành + tái tổ chức
  Daklaoruco ⇒ một phần biên cao là SẢN LƯỢNG (cấu trúc) chứ không chỉ giá. Kế hoạch 2026 hạ năng suất về
  1,69 tấn/ha, khai thác 13.800 tấn (2025: 15.152,83) [BCTN] — không cắt chuỗi, nhưng phân vị bị đẩy lên bởi yếu tố này.

## B. Giá đầu ra / đầu vào so 5–10 năm
| Biến | Vai trò | Gần nhất | Trung vị 5 năm | Phân vị 10 năm | Nguồn |
|---|---|---|---|---|---|
| Cao su RSS3 (WB CMO, USD/kg) | ĐẦU RA (~94% DT) | 2,75 (09/2026); TB Q3/26 2,753 vs Q3/25 2,163 (+27%); Q2/26 2,687 | 2,075 | **98,3** (20 năm: 78,5; đỉnh 2011 TB năm 4,82) | [FEED] `data/rubber_monthly.csv` |
| TSR20 (USD/kg) — sát SVR10/20 của DRI | ĐẦU RA | 2,564 (16/10/2026); 2,293 (19/06/2026) ⇒ +11,8% trong Q3 | CHUỖI THIẾU (feed từ 06/2026) | CHUỖI THIẾU | [FEED] `data/rubber_weekly.csv` |
| Giá bán thực hiện DRI (tr.đ/tấn) | ĐẦU RA | 2025: 47,24; Q2/26 YoY ≈ +18% [UL: (210,15/111,18)/1,5982] | — | — | [BCTN], [GT] (+59,82% sản lượng, +85,45% DT) |
| Giá vốn đơn vị cao su (tr.đ/tấn) | ĐẦU VÀO tổng hợp (lương, phân bón, KH vườn cây) | 2025: 33,11; Q2/26 YoY ≈ −0,7% [UL: (116,59/73,48)/1,5982] ; KH 2026: 1.430 USD/tấn | — | — | [BCTN], [BCTC 6.2], [GT] |
| Urea (WB, USD/t) | ĐẦU VÀO phụ (phân bón) | 407,5 (09/2026) | 403,75 | 73,3 | [FEED] `data/urea_monthly.csv` |
| LAK/VND (chi phí nội địa Lào) | ĐẦU VÀO (lương ~7,46 tr.đ/người/tháng) | VND/LAK 0,8470 (30/06/26) vs 0,8248 (KQKD H1/25) | CHUỖI THIẾU | CHUỖI THIẾU | [BCTC] |
| USD/VND (VCB bán) | quy đổi doanh thu XK (49% XK 2025) | TB Q3/26 26.344 | CHUỖI THIẾU (feed từ 07/2026) | CHUỖI THIẾU | [FEED] `data/vcb_fx_rate.csv` |

## C. Pha chu kỳ: **ĐỈNH** (mặc định cơ học: A p≈94–100 ≥ 80 **và** B đầu ra p10y 98,3 ≥ 80)
- Ủng hộ 1: biên LNST TTM 26,0% = cao nhất 9,5 năm; biên gộp Q2/26 44,5% là điểm BCTC cao nhất tôi thấy được.
- Ủng hộ 2: RSS3 ở phân vị 98 của 10 năm, +33% trên trung vị 5 năm; spread giá bán − giá vốn mở rộng do giá vốn
  đơn vị phẳng (−0,7% YoY) trong khi giá bán +18%.
- **Chống:** theo 20 năm RSS3 chỉ ở phân vị 78,5 và còn thấp hơn ~43% so TB 2011 (4,82) — danh nghĩa, chưa tính lạm
  phát; giá chưa gãy (TSR20 còn +11,8% từ 06→10/2026, RSS3 07–09 đi ngang 2,73–2,78) ⇒ có thể vẫn là GIỮA-LÊN muộn.
- Cơ chế cú sốc nếu đảo chiều: **giá bán (cầu/nhập khẩu TQ)**, không phải chi phí — đầu vào phẳng/giảm (LAK yếu).
  Đáy cũ 2019–20 và 2023 cũng là đáy GIÁ ⇒ so PB đáy cùng loại được.
- Cung ngành 12–24 tháng (công suất mới, tồn kho Thanh Đảo/SHFE): **CHUỖI THIẾU** trong phiên này — không đo.
- Cung riêng DRI: vườn trồng ~2005–2010 [UL, từ thoả thuận dự án 19/11/2004] ⇒ bắt đầu tái canh (37,77 ha 2026);
  sản lượng KH 2026 thấp hơn 2025 ~9% ⇒ biên đỉnh đi kèm sản lượng không tăng tiếp.

## D. Neo chính sách và rủi ro cấu trúc
| Neo/rủi ro | Loại | Ngày | Chu kỳ / cấu trúc | Nguồn |
|---|---|---|---|---|
| Dự án cao su 4 tỉnh Nam Lào, thoả thuận với CP Lào | giấy phép/đất | ký 19/11/2004; tầm nhìn chiến lược tới **2054** ⇒ thời hạn đất ~50 năm (ước lượng, chưa thấy văn bản thời hạn) | cấu trúc — dòng tiền CÓ THỜI HẠN ~28 năm | [BCTC 5.17], [BCTN] |
| Tiền thuê đất 6 USD/ha/năm (miễn 7 năm đầu, nộp từ 2012) | thuế-phí | đang hiệu lực | cấu trúc (rẻ) | [BCTC 5.17] |
| CIT Lào 20% sau 2 năm miễn kể từ cạo mủ; thuế khấu trừ khi chuyển LN về VN (11,17 tỷ ghi nhận H1/26) | thuế | đang hiệu lực | cấu trúc | [BCTC 5.17] |
| Tái canh / thanh lý vườn già (gỗ thanh lý = thu nhập một lần) | vòng đời tài sản | tái canh 37,77 ha 2026; GĐ 2027–2030 | cấu trúc (sản lượng giảm dần khi vườn qua tuổi ~25–30, ước lượng) | [BCTN] |
| EUDR (EU) — 784,32 tấn bán chuẩn EUDR/FSC 2025, premium 130 USD/tấn | quy chuẩn XK | ngày áp dụng cho DN lớn: theo hiểu biết của tôi 30/12/2026 (CHƯA kiểm lại trong phiên) | cấu trúc nhỏ | [BCTN] |
| Tỷ giá LAK: chênh lệch quy đổi luỹ kế **−355,0 tỷ** trong VCSH (−335,0 tỷ đầu năm) | FX | liên tục | cấu trúc — VCSH sổ sách bị bào mòn khi LAK mất giá | [BCTC CĐKT 417] |
| **Cổ đông chi phối: CTCP Cao su Đắk Lắk (Dakruco), 45% (32,94 tr CP, 01/08/2025)**; còn lại 6.716 CĐ, NN 0,75% | quản trị | — | cấu trúc | [BCTN] |
| **Dakruco VAY DRI**: HĐ 01/2023/HĐVV ngày 22/05/2023, 80 tỷ ⇒ còn **40 tỷ** (trả 40 tỷ Q2/26), 9%/năm, 60 tháng (đáo hạn ~05/2028), TSĐB 6 tr CP DRI do Dakruco sở hữu; DRI còn gửi 70 tỷ tại Quỹ TDND cao su Đắk Lắk | xung đột lợi ích | đáo hạn ~05/2028 | cấu trúc | [BCTC 5.2, 5.12, 7.1] |
- Dòng tiền lõi CÓ thời hạn (quyền đất Lào ~2054, ước lượng) ⇒ E không dùng PE vĩnh viễn làm neo duy nhất.
- Nhu cầu vốn của cổ đông chi phối: Dakruco đi vay DRI ⇒ có nhu cầu tiền mặt; hướng cổ tức cao (KH 2026 10% VĐL,
  2025 10%) phù hợp lợi ích Dakruco, nhưng kênh cho vay nội bộ là rủi ro rút tiền khỏi CĐ thiểu số. Đã thu hồi 1/2.
- Không thấy rủi ro "mất giấy phép" cụ thể có ngày trong tài liệu đã đọc.

## E. PE/PB trên LN chuẩn hoá (bảng cân đối 30/06/2026, BCTC gốc)
- **Net cash [BCTC]** = tiền 61,09 + tiền gửi có kỳ hạn ngắn hạn 303,50 − vay 77,22 − vay dài hạn 22,66 = **264,7 tỷ**
  (KHÔNG tính khoản cho Dakruco vay 40 tỷ). ⚠️ BQ `Cash_P0` = 61,09 ⇒ **thiếu 303,5 tỷ tiền gửi** (đúng bẫy mẫu §3).
- VCSH CĐ mẹ = 805,42 − 5,46 = **799,97 tỷ** ⇒ BVPS 10.929 đ ⇒ **PB 1,41x** (TS vô hình 5,4 tỷ ⇒ P/TB ≈ 1,42x).
- LN chuẩn hoá — 3 cách, CHỌN cách (2):
  1. Trung vị LNST năm 2017–2025 [BQ, 9 năm] = **74,1 tỷ** (2025 BQ 157,4; BCTN 158,16). Lệch xuống vì năng suất tăng cấu trúc.
  2. **[UL] Kinh tế đơn vị giữa chu kỳ ≈ 94 tỷ**: giá giữa chu kỳ 47,24 × 2,075/2,18 = 44,96 tr/tấn; giá vốn 33,11 tr/tấn;
     sản lượng 13.800 tấn (KH 2026) ⇒ LN gộp cao su 163,5 tỷ + ~10 tỷ sầu riêng/khác (ước lượng) − BH&QLDN 75 tỷ
     (18,76/quý Q2/26 ×4) + thu tài chính 17,7 tỷ − lãi vay 2,1 tỷ ⇒ LNTT ~114 ⇒ LNST ~94 tỷ (thuế hiệu dụng 17,5% Q2/26).
     Lý do chọn: phản ánh sản lượng hiện tại thay vì 2018–2020 năng suất thấp.
  3. LN lõi TTM = 226,3 − (LCTG 3,27 + thu nhập khác 1,55 của Q2; Q1 không tách) ≈ **221 tỷ** (= 2,35x cách 2; 3,0x cách 1).
- Lãi tiền gửi sau thuế ≈ 4,4 tỷ/quý × 4 × 0,8 ≈ 14,2 tỷ [UL]. EV-lõi = 1.127,3 − 264,7 = 862,6 tỷ.
- **PE chuẩn hoá ex-cash: 10,8x (cách 2)** · 14,4x (cách 1) · 4,2x (TTM lõi, KHÔNG dùng làm neo). PE trailing BQ 5,08x gây hiểu lầm.
- PB tại các đáy CÙNG loại (đáy giá cao su) [BQ `ticker_financial.PB`]: 2019Q3–2020Q2 **0,33–0,48x**; 2023Q1–Q3 0,94–1,16x
  (min giá 2023 6.100 đ / BVPS ~7.350 ≈ 0,83x). Hiện 1,41x ⇒ không ở vùng định giá đáy.

## F. DỰ BÁO CÓ THỂ BÁC BỎ
```
FORECAST (chính — BCTC Q3/2026 sắp ra, theo yêu cầu dispatch)
  indicator   : Biên LNST thuộc CĐ công ty mẹ Q3/2026 = chỉ tiêu 20 / chỉ tiêu 10, BCTC HỢP NHẤT, cột "Quý 3-2026"
  source      : BCTC hợp nhất Q3/2026 gốc trên dri.com.vn / HNX (KHÔNG dùng BQ NP_P0 — BQ đã lệch Q2/26 −4,5 tỷ)
  baseline    : Q2/2026 32,5% (68,289/210,147) · Q3/2025 21,2% (38,98/184,12 BQ — chấm lại bằng cột so sánh BCTC) · TTM 26,0%
  call        : LỚN HƠN HOẶC BẰNG 27,0%
  horizon     : quý 2026Q3
  due_date    : 2026-11-09 (công bố dự kiến 30/10 + 10 ngày)
  p           : 0,70
  persistence : giữ mức Q2/26 (32,5%) ⇒ HIT ; persistence cùng kỳ (21,2%) ⇒ MISS
  void_if     : BCTC Q3 chưa công bố tới 2026-11-20; đổi phạm vi hợp nhất/M&A; thu nhập khác (thanh lý vườn cây)
                > 10 tỷ trong quý — khi đó chấm trên (LNST − thu nhập khác ròng × 0,8)
  lý do       : RSS3 TB Q3 +27% YoY (USD), TSR20 +11,8% trong quý; giá vốn đơn vị phẳng YoY (Q2 −0,7%);
                Q3 là mùa cạo cao điểm ở Nam Lào ⇒ giá thành đơn vị thấp. Rủi ro: sản lượng bán thấp (KH 2026 bán 16.900 t,
                H1 đã xả tồn thành phẩm 153,2 → 65,0 tỷ), lỗ tỷ giá LAK, trích quỹ/lương, thuế khấu trừ chuyển LN.

FORECAST phụ 1 : LNST thuộc CĐ mẹ Q3/2026 (chỉ tiêu 20, BCTC hợp nhất gốc) ≥ 50,0 tỷ · p 0,70
                 baseline Q3/25 38,98 (BQ) · Q2/26 68,29 · persistence Q2 ⇒ HIT, cùng kỳ ⇒ MISS · cùng source/due/void
FORECAST phụ 2 : Biên gộp Q3/2026 (chỉ tiêu 20/chỉ tiêu 10, BCTC hợp nhất gốc) ≥ 42,0% · p 0,65
                 baseline Q2/26 44,5% · H1/26 41,6% · cùng source/due/void
FORECAST phụ 3 (đúng khung mẫu 2–3 quý): Biên LNST TTM thuộc CĐ mẹ tại 2027Q1 (4 quý Q2/26–Q1/27, BCTC gốc từng quý)
                 ≥ 24,0% · p 0,55 · due 2027-05-15 · persistence (26,0%) ⇒ HIT · void_if như trên
```
