# DD — NNC (CTCP Đá Núi Nhỏ) · r5 · as-of 03/11/2026 · job `Taylor_20261103_134709`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. r4 lưu `archive_internal/REPORT_r4_20261103.md`; báo cáo NĐT r4 lưu
> `archive_internal/NNC_DD_investor_report_20261103_r4.md`. Bản 30–31/10: `archive_internal/REPORT_v2_20261031.md` (gốc số BCTC/nguồn trang).
> **Nguyên tắc user 03/11:** dự án MỚI base = sổ sách/NPV 0; giảm trừ base cần cơ sở độc lập, ĐỐI XỨNG cộng/trừ; chu kỳ MỎ HIỆN HỮU chuẩn hoá theo cơ sở độc lập.
> **Thứ tự chạy — trung thực:** `r5/calc/nnc_model_r5.py` không dùng giá thị trường làm đầu vào của mô hình; khoá md5 `r5/calc/LOCK_md5_r5.txt` 20:49:47 ICT,
> so giá sau (`r5/calc/compare_r5.py`). r1–r4 đã biết giá (46.100) và brief nêu tham chiếu skeptic ~61.700 ⇒ khoá chỉ chứng minh THỨ TỰ CHẠY.

## 0. Kết luận (sửa theo `SKEPTIC_R4_20261103.md`)

**Tâm = 61.666 đ/cp** (tham chiếu skeptic ≈61.700: khớp, lệch −0,05%). Đổi duy nhất về tâm so r4: **ADMIN_GATED** = nghẽn hành chính TẠM THỜI gỡ được 6–18 tháng
(Bobby §4, `sector_read_da_xay_dung_nam_bo_20261030.md:181,185`); cơ chế sàn giá cao BỀN (đấu giá, mỏ xa) đã nằm trong STRUCTURAL ⇒ giữ nửa premium ở ADMIN là đếm
trùng. Ánh xạ cơ sở mới: stress 0,5 năm 2028, 1,0 từ 2029 (hồi trọn, trễ 1 năm).

| Trạng thái | w | Biên/SL từ 2028 | V_NNC | V_MVC (giải đồng thời) |
|---|---|---|---|---|
| STRUCTURAL | 0,20 | biên đỉnh bền (stress 0), SL NNC 1,40, Tân Lập 1,30 | 90.742 | 23.755 |
| ADMIN_GATED | 0,45 | stress 0,5 (2028) → 1,0 (2029+), SL năm thường 1,10/1,20 (NNC & Tân Lập) | 55.268 | 15.437 |
| CYCLICAL | 0,35 | stress 1,0 từ 2028, trần 249,7k/m³ (tiền 2026), SL năm thường | 53.278 | 14.898 |

Trục ánh xạ ADMIN (đủ 3 mức, đưa vào lưới): 0,5 vĩnh viễn (= r4) **67.596** · trễ 1 năm (tâm) **61.666** · 1,0 từ 2028 **60.770** (skeptic: 60.770 / 61.666 — khớp).
Lưới **4.374** (= lưới r4 1.458 × 3 ánh xạ ADMIN; thang ĐĂNG KÝ TRƯỚC trong docstring): P10 **53.044** · P25 **57.944** · P50 63.982 · P75 **70.691** · P90 **76.981**
(min 42.229, max 98.606). Theo ánh xạ: 0,5 vĩnh viễn P10/P50/P90 57.220/68.037/80.784 · trễ 1 năm 52.232/62.403/74.531 · 1,0 51.354/61.575/73.590 (= lưới skeptic
51.354/55.893/61.575/67.851/73.590 — khớp). Lưới đầy đủ so tham chiếu skeptic: P50 +3,9% (do giữ mức 0,5 vĩnh viễn làm 1/3 lưới) — <10%.
Thang: RẺ ≤53.044 · RẺ CÓ ĐIỀU KIỆN 53.044–57.944 · HỢP LÝ 57.944–70.691 · NGHIÊNG ĐẮT 70.691–76.981 · ĐẮT ≥76.981.

**So giá (sau khoá): đóng cửa 03/11/2026 = 46.100** (DNSE `dnse_close_prices` G1) ⇒ **RẺ (dưới P10, −13,1%); 0,7% bộ lưới dưới giá (min 42.229).**
**Biên hoà vốn:** 100% hồi biên, giá trị = giá khi giá đá **≈228k/m³** tiền 2026 ở SL năm thường; theo SL **216–234k** ⇒ biên đá **≈27–28%** (SL 1,40: 216k/28,3%;
1,10/1,20: 228k/27,9%; 1,20/1,30: 223k/28,3%; 1,05: 234k/26,8%). Dưới TB chu kỳ 34,3%.
**Biên 34,3% ở trần chỉ "giữ giá trị thực" trên đường thực**; trên đường g2031 (giá danh nghĩa phẳng tới 2030, chi phí +3%/năm) biên năm 2030 ≈**26,0%**.
**Biên MỎNG ở trạng thái xấu:** CYCLICAL 53.278 (+16%), ADMIN 55.268 (+20%); CYCLICAL trần SL 1,40 48.827 (+6%); CYCLICAL + giá danh nghĩa phẳng 41.663 (−10%).
**Gordon (r13 g3, BVPS 29.915), nhất quán ánh xạ (ADMIN = CYC ở năm điển hình 2031+), CẢ HAI chiều:** bản khoá (không LN tài chính) ROE 27,1/11,6/11,6% ⇒ trộn 14,7% ⇒
**34.913** (giá cao hơn 32%); bản bổ sung (+LN tài chính sau thuế 16,6 tỷ/năm) 29,6/14,1/14,1% ⇒ trộn 17,2% ⇒ **42.504** (giá cao hơn 8%). Giá hàm ý ROE bền 18,4%;
tâm hàm ý 23,6%. ⇒ Theo Gordon, giá KHÔNG còn biên an toàn nếu biên về TB; nhãn RẺ dựa vào DCF hữu hạn (giữ giá đá cao tới 2027 + tiền 1/3 vốn chủ).
Định vị: NNC ở ĐỈNH chu kỳ **biên** (GPM 53%, cao nhất 15 năm). P/B 1,54 KHÔNG phải đỉnh lịch sử (2026: 1,32–3,0, trung vị 1,72 — số skeptic, chưa đo lại trong r5).

| 3 kịch bản NĐT (= 3 trạng thái) | g2031 | thực |
|---|---|---|
| Biên đỉnh bền (20%) | 83.805 | 97.678 |
| Hành chính được gỡ, hồi trọn trễ 1 năm (45%) | 50.468 | 60.068 |
| Chu kỳ dự án, về TB chu kỳ (35%) | 48.536 | 58.019 |

## 1. Kiểm kê khoản cộng/trừ gắn dự án mới & giả định (hiệu ứng = đưa khoản đó vào/bỏ ra khỏi tâm r3, đ/cp NNC; số: `r3/calc/model_r3_out.txt` mục "Kiem ke")


**Kiểm kê r4 (bổ sung cho bảng dưới — bảng giữ nguyên từ r3; dòng "Cắt sản lượng" và "Mốc giá 320 + stress" ĐÃ ĐỔI xử lý):**

| Khoản | Hiệu ứng (so tâm r4) | Cơ sở dữ liệu độc lập | Xử lý r4 |
|---|---|---|---|
| Chu kỳ biên mỏ hiện hữu (Mũi Tàu + Tân Lập) | r3→r4: −23.146 (chỉ STRUCTURAL = 90.742) | CÓ: Bobby §4 phân loại 0,20/0,45/0,35, pha "ĐỈNH → bình nguyên"; GPM NNC 2012–25 TB 34,2% (BQ) | **Trộn 3 trạng thái**; lưới 3 bộ trọng số (40/35/25, 15/35/50 = điều kiện đổi nhãn Bobby) |
| SL năm thường 1,10/1,20 ở nhánh hồi biên (cả Tân Lập) | 1,05: −508 · 1,20/1,30: +500 · Tân Lập giữ 1,30: +130 | CÓ: 2024 = 1,05 tr m³ (FPTS) ở giá 245,2k, GV TP kiểm toán 178,29/DT 257,44 [KT25 7.2] = 74% trần | Gắn với hồi biên; SL 1,40 chỉ ở STRUCTURAL |
| Trần chu kỳ: biên đá TP chu kỳ 34,3% trên chi phí mô hình ở SL của nhánh | tính ở SL 1,40 (236,1k): −2.559 | CÓ: GPM toàn cty TB 34,2% + chênh đá TP vs toàn cty TB 2024/25 (−0,9/+1,0 ⇒ +0,1pp); chi phí mô hình khớp GV kiểm toán (2024: 161,5 vs 169,8k/m³) | Trần 249,7k (SL TB 1,181); kiểm: trần @1,05 = 260,6k ≈ giá 2024 tiền 2026 260,1k (khớp) |
| Upside đối thủ hết GP (TL2 ~2033, TL3 ~2035; FPTS 07/01/2026) | +3.828 | CÓ về chiều/thời điểm (FPTS: Mũi Tàu hơn TL3 8 năm, TL2 10 năm); KHÔNG về độ lớn | Độ nhạy (từ 2034 stress ×0,5) — đối xứng với chiều xuống |

**Kiểm phép quy đổi skeptic (242,5k = biên 36%):** chi phí mô hình @1,40 = 155,2k/m³ ⇒ 242,5k = biên 36,0% (đúng số học). Nhưng biên chu kỳ ĐO được là 34,3%
(không phải 36%), và chi phí cố định/m³ phụ thuộc SL: ở SL năm thường 1,18 chi phí 164,2k ⇒ 242,5k chỉ còn biên 32,3%. Trần 242,5k (neo SL 1,40) và
249,7k (neo SL nhánh) là HAI CÁCH NEO HỢP LỆ, không phải "trừ hai lần": r5 giữ 249,7k ở tâm; 242,5k −1.820, 236,1k −3.446 (so tâm r5; so tâm r4 skeptic đo −1.352/−2.559). Peers TB 2012–25: KSB 40,4%, DHA 26,0%, VLB 24,7%.
r3 ghi "GPM về TB 2012–25" cho trần 270k (`r3/calc/model_r3.py:142`, REPORT r3 :17–18,:29) là SAI NHÃN: 270k ≈ biên 42,4% trên chi phí mô hình @1,40.

| Khoản | Hiệu ứng | Cơ sở dữ liệu độc lập (nguồn) | Xử lý r3 |
|---|---|---|---|
| CIP Tam Lập 1 khu II 83,5 tỷ chỉ ở tốt/cơ sở (v2: xấu/rất xấu = 0) | −998 nếu giữ | KHÔNG (không có tín hiệu huỷ dự án) | **Sổ sách mọi kịch bản** |
| Chi phí trễ GP Tam Lập 1 khu II (P trễ 0/1/2 năm = 0,30/0,40/0,30) | −443 (giữ) | CÓ: Bobby F6 P(GP mỏ đấu giá trước 06/2027)=0,30; đối xứng với mỏ mới MVC r6 | Trong base (chi phí kỳ vọng 9,3 tỷ) |
| Upside Tam Lập 1 khu II (sản lượng thêm) | không định lượng | KHÔNG: chưa có GP/trữ lượng/công suất/capex công bố (AWM thứ cấp) | 0 ở base, chỉ định tính |
| Dự phòng truy thu CQ 15,58 + thuê đất 2019 Núi Nhỏ 5,95 + CQ Mũi Tàu 0,84 | −1.021 (giữ) | CÓ: BCTC Q3 V19a | Trừ ở tiền ròng |
| Đối xứng BCĐKT: ký quỹ PHMT 4,57 + thuế hoãn lại 4,31 (v2 trừ dự phòng nhưng không cộng tài sản đối ứng) | +424 | CÓ: BCTC Q3 V9 / tr.2 | **Cộng vào base** |
| Trả trước dài hạn CN Bình Phước 59,2 (phân bổ 3,2/quý, phi tiền mặt trong chi phí hiệu chỉnh) | +2.146 nếu cộng | CHƯA XÁC MINH bản chất (r5 thử lại nguồn: BCTC scan không đọc được) | Độ nhạy |
| Máy nghiền 350 t/h (CIP 24,5; mua từ NHC) | +1.171 nếu cộng | Thay thế/duy trì năng lực ⇒ nằm trong dòng tiền DCF | Độ nhạy; giao dịch NHC = WARNING |
| Vách giá cơ sở 380→300 (2028–30), nhãn FPTS "cung mới" | −2.740 nếu giữ | Chiều: CÓ (cung mới cụm định lượng được: mỏ MVC ~2,1 tr m³ TP/năm + Tam Lập 1 khu II); độ lớn: KHÔNG | Trượt 360/340/320; vách = độ nhạy |
| Mốc giá 320 từ 2031 + trục stress biên | — | CÓ: GPM NNC 2012–25 TB 34,1% vs 53,3% (BQ `ticker_financial`, `r3/calc/sector_gpm_roe.csv`) | r4: trộn 3 trạng thái (xem bảng r4) |
| Cắt sản lượng co_so 1,10 (2028–30)/1,20 (2031+) | −6.874 nếu giữ | KHÔNG về độ lớn (FPTS base 0,8 không nêu lý do) | r3: base 1,40 — **r4: mỏ HIỆN HỮU ⇒ gắn với nhánh hồi biên (xem bảng r4)** |
| Trọng số kịch bản 25/50/20/5 | (v2 20/45/25/10: −8.710) | CÓ: Bobby F2 P(giá Q2/27 >+7%)=0,30, <−7%=0,15 | Giữ; lưới 3 bộ |
| Đường giá phẳng danh nghĩa trong tâm (10/50/40) | −2.498 nếu giữ | KHÔNG: 2012–25 không mã đá ĐNB nào đi theo (SKEPTIC2 C) | Chỉ stress (72.697) |
| Cổ phần MVC theo thị giá × (1−15% thanh khoản) − vòng chéo bằng giá NNC (v2) | v2 ~3.814 đ/cp vs r3 ~11.400 | D1: không dùng thị giá trong định giá NNC | **Giải hệ nhất quán** V_N = N_ex + 0,103·V_M; V_M = D_M + 0,4407·V_N |
| Holding MVC→NNC 15% | −643 | KHÔNG về độ lớn | 0 ở base; độ nhạy |
| NHC thị giá 13,2 → sổ sách 14,1 | +41 | Không dùng thị giá (kém thanh khoản) | Sổ sách |
| Mở rộng công suất (dây chuyền 1.000 t/h, đá 1x1, cát nghiền) | 0 | KHÔNG có IRR | NPV 0 (không capex, không lãi) |
| LN gộp cho thuê Núi Nhỏ 11,13 tỷ/năm tới 2043 | +3.500 (giữ); nếu chỉ tới 2030: −2.133 | CÓ số LN: KT25 7.1–7.2. THỜI HẠN tới 2043: CHƯA XÁC MINH (BCTC Q3/2026 + KT25 là PDF scan, không trích được text trong phiên — pdftoppm/pypdf không có; BCTN 2025 không nêu) | Base; độ nhạy thời hạn |
| Chi phí K 0,97 (GV kiểm toán 2024–25) | ±6,6–6,7k (±10%) | CÓ: KT25 7.2 | Base; lưới |
| r 13% | −7,0k/+8,4k (15/11%) | Khung user (Ke nội địa) | Base; lưới |

## 2. Mô hình (`r5/calc/nnc_model_r5.py`; tái dùng `r4/calc/model_r4.py` → `r3` + MVC r6 KHÔNG SỬA — md5 ở LOCK_md5_r5)
- Cầu nối kỳ vọng (đ/cp, `r5/calc/extras_r5_out.json`): Mũi Tàu 2027–43 gồm thuê 36.344 · tiền ròng 10.202 · 10,3% MVC 7.947 · CIP Tam Lập 3.810 − trễ GP 423
  · Q4/26 2.737 · NHC sổ sách 645 · ký quỹ + thuế hoãn lại 405 ⇒ 61.666. Ngoài mỏ ≈25.322 ⇒ giá 46.100 trả ≈20.778 cho mỏ (kỳ vọng 36.344; CYCLICAL ≈28.900).
- Độ nhạy (so tâm r5): ADMIN 0,5 vĩnh viễn +5.930 / 1,0 từ 2028 −896 · trọng số 40/35/25 +7.294 / 15/35/50 −2.072 · K ±10% −6.298/+6.410 · r 15/11% −3.612/+4.332 ·
  PW ±2.083 · trần 242,5k −1.820 / 236,1k −3.446 · upside đối thủ hết GP +5.326 · thuê Núi Nhỏ bỏ −3.500 / tới 2030 −2.133 · trả trước 59,2 +2.146 · phẳng 100% 48.739 ·
  SL 1,05 +324 / 1,20/1,30 −177 · holding 15% −437 · bỏ đối xứng BCĐKT −424.
- Hoà vốn tính lại sau khoá (`r5/calc/compare_r5.py`) — không phụ thuộc ánh xạ ADMIN (100% hồi biên).

## 3. V_NNC cho MVC r8
V_NNC r5 = **61.666** (MVC trong cùng hệ = **16.912**; khớp tham chiếu skeptic 61.700 / 16.900). MVC r8 dựng ở `dd_MVC_20261103/r8/`.

## 4. Điều kiện đổi nhận định (hai chiều; mốc khoá 03/11/2026)
- **Tiêu cực hơn:** biên gộp quý < 45% khi DT đi ngang (giá đá ≤228k/m³ tiền 2026 ⇒ giá trị ≈ giá); giá công bố Sở XD Q2/27 thấp hơn Q3/26 >7%; GP mỏ đấu giá trong cụm cấp sớm (trước 06/2027);
  truy thu/xử phạt mới >20 tỷ; MVC ≥51% kèm thoái MVC dưới giá trị; ĐHĐCĐ 2027 dồn tiền vào BĐS; thêm dòng tiền lớn với NHC; hợp đồng thuê Núi Nhỏ ngắn hơn 2043.
- **Tích cực hơn:** biên ≥55% ở Q4/26 + Q1/27 (nghẽn hành chính kéo dài hơn 18 tháng ⇒ ADMIN giống STRUCTURAL hơn); giá công bố Q2/27 cao hơn >7%; VĐ4 ≥20% khối lượng tới 30/06/2027;
  GP Tam Lập 1 khu II kèm trữ lượng/công suất; công bố sản lượng m³; cổ tức tiền cao hơn.
- Mốc: BCTC Q4/26 ~20/01/2027 · Q1/27 ~20/04/2027 · VĐ4 & GP mỏ cụm 30/06/2027 · giá Sở XD Q2/27 (kiểm 31/08/2027).

## 5. Sản phẩm & kiểm
- Báo cáo NĐT: `investor_report_v3/NNC_DD_investor_report_20261103.{md,pdf,html}` (đè bản r4; r4 lưu `archive_internal/..._r4.md`) — 11 trang; dry-run email
  (`--html-out`): 16 ảnh, 9,5 MB, 16/16 `<img>` alt; grep luật 18/4/12 rỗng trên md + subject; **KHÔNG gửi**. md5 PDF 97315bdd71dabe05e575a9f469c16642.
- Sổ mức giá: `kb/dd_price_zones.json` NNC@2026-11-03#3 (supersedes #2; #2 đổi con trỏ sang bản lưu); selfcheck 0 lỗi.
- ADV trung vị (BQ Price×Volume, đo trong r3): 20/60/120 phiên 1,43 / 1,38 / 1,39 tỷ.
- fundamental-skeptic CHƯA chạy trên r5.
