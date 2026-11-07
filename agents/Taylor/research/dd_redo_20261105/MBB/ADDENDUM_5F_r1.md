# ADDENDUM 5F (bước 3c) — MBB · 07/11/2026 · job `Taylor_20261107_130206`

Bổ sung cho `REPORT_r2.md` (05/11/2026), KHÔNG thay nó. **Kết luận: moat NARROW / COST+REGULATORY, làm MỚI (chưa có audit 5F), KHÔNG bền** (fail (i) ở cửa sổ 10 năm và (iii) lực thứ 6 đang chạy). **Mô hình hiện hành KHÔNG nhất quán với luật 3c**: terminal giữ ROE_T 14/16/18% > Ke 13,5% vĩnh viễn VÀ cho RI tăng g_T 6–8% (RONIC ngầm > Ke) — tức thưởng moat WIDE ngầm. Hiện hành: tâm **23.804** · P10 14.444 · P50 22.765 · P90 35.860, TRONG vùng. **BẢN CHẶT-3C (NARROW: RONIC=Ke + ROE fade 5 năm về TB chu kỳ ngành 14,98%): tâm 20.459 (−14,1%) · P10 14.417 · P50 20.364 · P90 27.723 · 44,3% trọng số dưới giá · nhãn TRONG (giữ) — quy ước chờ Mike/user duyệt.**

Tái lập: `$DNA_PYEXE -I calc_5f/mbb_5f.py > calc_5f/mbb_5f_out.txt` (bản CUR tái lập đúng tới đồng 23.804/14.444/22.765/35.860 của `calc/mbb_r2.py`; script KHÔNG ghi SUMMARY/grid cũ). Peer: `calc_5f/peer_roe_bq_20261107.csv` (BQ `tav2_bq.ticker_financial`, quý mới nhất 2026Q3 mỗi mã). LOCK md5 cuối `mbb_5f_out.txt`.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng hay làm mới:** làm MỚI. `data/moat_tags.csv` không có MBB; `REPORT_r2.md`, `dd_MBB_20261031/REPORT.md`, `kb/projects/mbb-dd-20261031.md` không có mục 5F/moat. Tầng (a) ngành: Bobby `kb/data_registry/market-state/sector_read_ngan_hang_20261031.md` (ADMIN_GATED 0,45 / CYCLICAL 0,35 / STRUCTURAL 0,20).
**Loại hình DN:** NHTM cổ phần tư nhân quy mô lớn, hệ sinh thái (MCredit, MBS, MIC, MB Ageas), cổ đông nhà nước/quân đội (Viettel, SCIC, Trực thăng, Tân Cảng — số 2024–25 [WEB thứ cấp]). Ngân hàng ⇒ ROIC không áp dụng (BQ `ROIC5Y/Min5Y/10Y` = 0 cho MỌI mã NH — cột không tính cho NH); dùng **ROE vs Ke** (nợ là nguyên liệu kinh doanh).

| Lực | Đánh giá (số + nguồn) |
|---|---|
| Gia nhập mới | Rào cản CAO: giấy phép NHNN, vốn điều lệ tối thiểu, room ngoại 30% (49% cho NH nhận chuyển giao bắt buộc) [Bobby §3, NỀN]. Mốc "không cấp phép NH nội mới nhiều năm": **cần kiểm chứng**. Fintech/ví điện tử là đe doạ ở mảng thanh toán, chưa ở tín dụng. |
| Nhà cung cấp (người gửi tiền) | Quyền lực ĐANG TĂNG: TG KH +7,9% vs tín dụng +18,8% YTD; CCTG lên 11,18% nguồn vốn; KKH/TG KH 36,8% → 32,8% trong 9T26; chi phí lãi Q3 +115% YoY [REPORT 31/10 §3–4, HN-Q3]. Ngành: CASA 20,2% Q2, 22/27 NH giảm [Bobby §3]. |
| Khách vay | Trung bình: bán lẻ phân tán, nhưng KD BĐS +48,3% YTD; top-10/20 KH và bên liên quan **chưa kiểm** (WARNING 4 REPORT_r2). |
| Sản phẩm thay thế | Trung bình: TPDN/chứng khoán hút tiền gửi KKH khi lãi suất kỳ hạn cao; kênh vay TPDN cho DN lớn. |
| Cạnh tranh nội ngành | CAO: 27 NH niêm yết, Big-4 neo giá huy động thấp (6,8% online) ⇒ tư nhân trả premium 1–1,6pp [Bobby §3]; room tín dụng do NHNN cấp (ADMIN_GATED) ⇒ thị phần không tự do mở rộng theo lợi thế. |
| **Lực thứ 6 (Nhà nước)** | ĐANG CHẠY: (1) chuyển giao bắt buộc MBV (OceanBank) — Nhà nước dùng NH khoẻ để gánh NH yếu, lỗ luỹ kế MBV 15.688 tỷ (2024) [WEB], đã là trục lưới REPORT_r2 §3; (2) CV 9608/9736 ép lãi huy động −0,5pp / cho vay ưu tiên −1,5–2pp; TT 50 LDR 95% từ 01/12; Basel III 2030, LCR/NSFR 2028–33 ⇒ nhu cầu vốn cấp 1 cao vĩnh viễn [Bobby §4]. Đây là cơ chế đánh thuế phần ROE siêu ngạch, không phải sự kiện một lần. |

**Bằng chứng lợi nhuận siêu ngạch (điều kiện (i)) — cả hai phía** [BQ `ticker_financial` 2026Q3; ROE năm = `ROE_Trailing` quý Q4]:

| Chỉ số MBB | Giá trị | vs Ke 13,5% |
|---|---|---|
| ROE_Min5Y / ROE5Y | **20,67% / 22,69%** | > Ke (thuận) |
| ROE_Min3Y / ROE3Y | 20,67% / 22,10% | > Ke |
| ROE10Y (TB 10 năm) | 19,83% | > Ke |
| **ROE_Min10Y** | **12,02%** | **< Ke (nghịch)** |
| ROE năm 2011→2017 | 17,8 / 16,8 / 15,0 / 14,8 / **12,8 / 11,5 / 12,6** | 3 năm liền < Ke (2015–17) |
| ROE năm 2018→2025 | 19,1 / 21,7 / 18,3 / 22,9 / 25,0 / 23,5 / 21,2 / 20,7 | > Ke, đỉnh 2022, đang giảm dần |
| ROA_P0 (TTM) | 1,92% | peer: TCB 2,30 · VPB 2,17 · LPB 1,94 · HDB 1,88 · VCB 1,61 · ACB 1,52 |

So peer (ROE10Y, bỏ MBB): toàn ngành niêm yết trung vị **14,98%** / TB 13,95% (23 mã, bỏ NVB ROE âm; 24 mã gồm NVB: TB 12,96%); nhóm lớn 11 mã (VCB BID CTG TCB VPB ACB HDB LPB STB SHB VIB — chọn theo quy mô, **cần kiểm chứng** danh sách theo tổng tài sản) trung vị **18,94%** / TB 17,75%. MBB ROE_Min5Y xếp 2/25 (sau HDB 22,0%). Chênh MBB vs nhóm lớn chỉ +0,9pp (ROE10Y) ⇒ siêu ngạch so với NH cùng cỡ là nhỏ; so với toàn ngành +4,9pp. Peer đều là đối thủ nội địa trực tiếp; NVB loại khỏi số chính vì ROE âm do tái cơ cấu (ngoại lai), báo kèm.

**Cơ chế rào cản (ii):** gọi tên được — **chi phí vốn thấp** nhờ CASA cao (CASA MB công bố 37,8% 2025 [BCTN25], 34,6% Q2/26 [WEB Vietcap] vs ngành 20,2%) từ hệ sinh thái quân đội/Viettel + app bán lẻ (số người dùng: **cần kiểm chứng**), CIR 26,3% 9T26 (thấp), NIM 4,0–4,2% (CTG 2,88% Q2 [WEB]); cộng giấy phép (REGULATORY, chung cả ngành). Nhưng cơ chế ĐANG MÒN: KKH/TG KH −4,0pp trong 9 tháng.
**Đồng hồ cắt hào (iii):** có — lực thứ 6 ở trên (MBV, trần lãi suất hành chính, Basel III) + CASA mòn. Không phải đồng hồ có ngày hết hạn, nhưng là cơ chế lặp lại đánh vào ROE siêu ngạch.

⇒ **moat_tier NARROW · moat_type COST/REGULATORY · moat_durable = false** ((i) chỉ qua ở cửa sổ ≤5 năm — một chu kỳ tín dụng 2018–25; 10 năm có 2015–17 < Ke; (iii) fail). **Rủi ro số 1:** xói mòn CASA/chi phí vốn biên (CCTG, KKH giảm) đúng lúc Nhà nước giao gánh MBV và chất lượng tài sản xấu đi (nhóm 2 HN +42% QoQ Q3) ⇒ ROE về mức ngành.

## 2. Moat trong mô hình
Rà soát `calc/mbb_r2.py` (= `mbb_redo.py` dòng 2–57) — **KHÔNG nhất quán**, hai kênh ngầm:
- **(R) RONIC:** `ri_ps()` terminal `(ROE_T−Ke)·BV/(Ke−g_T)` với g_T 6/7/8% khi ROE_T ≥ Ke ⇒ vốn mới tái đầu tư vĩnh viễn ở ROE_T > Ke (RONIC > Ke). Luật NPV 03/11 trong code chỉ chặn phía ROE_T < Ke (một chiều). Bản chặt: g_RI = 0 **mọi ô** (đối xứng; ô dưới Ke vốn đã 0).
- **(M) ROE terminal:** ROE_T kịch bản 14/16/18% (+ΔROE ±3pp) giữ vĩnh viễn; CƠ SỞ 16% > TB ngành 14,98%. Bản chặt: sau 2027–29 (giữ nguyên đường ROE kịch bản), fade tuyến tính về ROE_ind + ΔROE trong N = 5 năm (NARROW; NONE: về Ke trong 2 năm — cùng quy ước SCL/SZL), rồi RI terminal không tăng. Áp ΔROE vào cả đích ⇒ trục ΔROE giữ đối xứng; XẤU (14%) được kéo LÊN về 14,98% — đối xứng, không cắt một chiều. Trục Δg mất tác dụng (như SCL).
- **Đã đúng luật:** MBV base NPV 0; không bội số premium; không giảm trừ pháp lý nào trong base (không có vụ án; MBV là trục có xác suất, không đếm lại ở đây). Quy ước năm (H): năm 1 = 2027 chiết khấu 1 kỳ từ 31/12/2026, các năm fade nối tiếp số mũ 4..3+N, TV chiết khấu (1+Ke)^(3+N); cuối cùng chiết khấu DAYS về 04/11 — y hệt mô hình.
- Tham số: **ROE_ind = 14,98%** (cơ sở: moat NARROW không bền ⇒ luật 3c "về TB chu kỳ ngành"; bằng chứng: trung vị ROE10Y 23 NH niêm yết bỏ NVB, BQ 2026Q3); **N = 5** (cơ sở: NARROW; độ nhạy N=10 bên dưới); **RONIC = Ke** (cơ sở: không WIDE).

## 3. Độ nhạy WIDE / NARROW / NONE và cách chọn peer (sau CK 5 tỷ; lưới 180 kết cục; giá 19.250)

| Bản | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn 5 tỷ | Nhãn 40 tr (P10/P90) |
|---|---|---|---|---|---|---|---|
| WIDE = Hiện hành REPORT_r2 | **23.804** | 14.444 | 22.765 | 35.860 | 32,3% | TRONG | TRONG (14.470/35.923) |
| chỉ (R) RONIC=Ke | 20.169 | 14.444 | 20.076 | 26.122 | 46,2% | TRONG | TRONG |
| chỉ (M) ROE→ngành trung vị, giữ g | 22.658 | 14.417 | 21.999 | 33.505 | 41,2% | TRONG | TRONG |
| **HEADLINE NARROW: R+M, ngành trung vị 14,98%, N5** *(chờ duyệt)* | **20.459** | **14.417** | **20.364** | **27.723** | 44,3% | **TRONG** | TRONG (14.442/27.771) |
| ↳ ngành TB 13,95% | 19.010 | 13.216 | 18.914 | 26.046 | 50,8% | TRONG | TRONG |
| ↳ nhóm lớn TB 17,75% | 24.582 | 17.844 | 24.499 | 32.899 | 23,4% | TRONG | TRONG |
| ↳ nhóm lớn trung vị 18,94% | 26.463 | 19.410 | 26.405 | 35.258 | 8,6% | DƯỚI — **ranh giới** (P10 cách giá +0,8%) | DƯỚI ranh giới (19.444) |
| ↳ ngành trung vị, fade N10 | 21.680 | 14.221 | 21.372 | 31.169 | 43,4% | TRONG | TRONG |
| NONE: RONIC=Ke + ROE→Ke N2 | 17.638 | 15.109 | 17.550 | 19.983 | 78,7% | TRONG | TRONG (15.135/20.018) |

Tách chênh hiện hành → headline (−3.345): chỉ RONIC = Ke **−3.636**; thêm fade ROE về 14,98% **+290** (kéo XẤU 14% lên bù phần kéo CƠ SỞ/TỐT xuống — tương tác). Tức gần như toàn bộ phần "moat ngầm" của mô hình nằm ở **g_T của RI terminal**, không ở mức ROE_T. P90 nhạy nhất: 35.860 → 27.723 (−22,7%); P10 gần như không đổi (do nhánh XẤU, vốn ROE_T ≈ ngành).
Nhãn TRONG giữ ở WIDE/NARROW/NONE và mọi cách chọn peer trừ "nhóm lớn trung vị" (DƯỚI ranh giới — chỉ đứng được nếu coi MBB chỉ cần ngang NH lớn thành công nhất, tức peer chọn theo kết quả ⇒ thiên lệch sống sót). Khoảng hợp lý tâm theo peer: **19,0k–26,5k**; headline 20,5k.

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị, KHÔNG đổi nhãn (nếu duyệt quy ước chặt-3c).** REPORT_r2/SUMMARY.json giữ nguyên, KHÔNG ghi `dd_price_zones`. Theo luật 3c: tâm **23.804 → 20.459 (−14,1%)**, P10 14.444 → 14.417, P50 22.765 → 20.364, P90 35.860 → 27.723; % dưới giá 32,3% → 44,3%; giá vs tâm −19,1% → −5,9%; nhãn TRONG → TRONG (cả 5 tỷ và 40 tr). Ngưỡng TRÊN vùng hạ từ 35.860 xuống 27.723. Phần "giá thấp hơn tâm 19%" của REPORT_r2 phần lớn đến từ RI terminal tăng trưởng vĩnh viễn ở ROE > Ke — luật 3c không cho phép khi moat không bền. Đối chiếu: headline 20,5k gần Gordon P/B ROE_T 16% (20,8–21,6k, REPORT_r2 §6) và RI @ Ke 14,5% (20.223). Quy ước chờ Mike/user: (1) TB ngành = trung vị 23 NH niêm yết (bỏ NVB) (vs nhóm lớn); (2) fade N=5; (3) ΔROE áp cả vào đích.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
MBB,NARROW,COST/REGULATORY,M,"Low-cost funding (CASA 37.8% 2025 vs sector ~20%, CIR 26%) via military/Viettel ecosystem + licence = real edge; ROE_Min5Y 20.7% but ROE_Min10Y 12.0% < Ke (2015-17 11.5-12.8%) and only +0.9pp ROE10Y vs large-bank peers; #1 risk: CASA erosion (KKH/TG 36.8->32.8% 9M26, CCTG 11%) + state-imposed rescue (compulsory MBV/OceanBank transfer, admin rate caps, Basel III) taxing excess ROE, NPL group-2 +42% QoQ Q3/26",2026-11-07,5f,N
```
`entry = M` = độ hấp dẫn cấu trúc NGÀNH (moat_5f.py schema): rào gia nhập cao nhưng ADMIN_GATED, nhà cung cấp vốn mạnh lên, ROE trung vị ngành 14,98% chỉ nhỉnh Ke. `moat_upgrade = N`. `src = 5f` (chưa qua validate cạnh tranh/skeptic).

## 6. Ghi chú
- WARNING pháp lý: không có vụ án/điều tra; giữ nguyên 11 mục §9 REPORT_r2 (MBV, ưu đãi MBV, ngoại bảng…). Không dùng mục nào để ép ROE/fade.
- 5F dựa một phần trên kiến thức LLM + WEB ⇒ non-point-in-time, CHỈ cho DD sống, cấm đưa vào backtest.
- Chưa qua fundamental-skeptic (Mike chạy). Không đụng candidate/plan/lệnh, không email.
