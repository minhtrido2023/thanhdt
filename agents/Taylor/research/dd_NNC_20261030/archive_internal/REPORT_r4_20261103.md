# DD — NNC (CTCP Đá Núi Nhỏ) · r4 · as-of 03/11/2026 · job `Taylor_20261103_132045`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. Bản 30–31/10 lưu ở `archive_internal/REPORT_v2_20261031.md` (gốc số BCTC/nguồn trang).
> Báo cáo NĐT r3 (rev1 sổ mức giá) lưu ở `archive_internal/NNC_DD_investor_report_20261103_rev1.md`.
> **Nguyên tắc user 03/11:** dự án MỚI base = sổ sách/NPV 0; mọi giảm trừ base cần cơ sở độc lập, ĐỐI XỨNG cộng/trừ; đứng vai doanh nghiệp;
> NHƯNG chu kỳ của MỎ HIỆN HỮU (biên, sản lượng Mũi Tàu/Tân Lập) KHÔNG phải dự án mới ⇒ chuẩn hoá chu kỳ theo cơ sở độc lập (r4 sửa đúng điểm này —
> `SKEPTIC_R3_20261103.md` lỗi 1–6).
> **Mù giá — trung thực:** `r4/calc/model_r4.py` không đọc giá/vốn hoá/P-E NNC hay MVC; khoá md5 `r4/calc/LOCK_md5_r4.txt` 20:24:58 ICT, so giá sau
> (`r4/calc/compare_r4.py`). r1–r3 đã biết giá (~46–47k) và brief nêu tham chiếu skeptic ~66.400 ⇒ khoá chỉ chứng minh THỨ TỰ CHẠY.

## 0. Kết luận

**Tâm (trộn 3 trạng thái biên theo Bobby §4: STRUCTURAL 0,20 / ADMIN_GATED 0,45 / CYCLICAL 0,35; mỗi trạng thái W 25/50/20/5 × g2031/thực 50:50,
r13%, K 0,97) = 67.596 đ/cp** (tham chiếu skeptic ~66.400: lệch +1,8%, trong dải 62–72k).
| Trạng thái | w | Biên/SL từ 2028 | V_NNC | V_MVC (giải đồng thời) |
|---|---|---|---|---|
| STRUCTURAL | 0,20 | biên đỉnh bền (stress 0), SL NNC 1,40, Tân Lập 1,30 (= tâm r3) | 90.742 | 23.755 |
| ADMIN_GATED | 0,45 | hồi biên một nửa (stress 0,5), SL năm thường NNC & Tân Lập 1,10 (2028–30)/1,20 (2031+) | 68.446 | 18.726 |
| CYCLICAL | 0,35 | hồi biên trọn (stress 1,0), trần 249,7k/m³ (tiền 2026), SL năm thường | 53.278 | 14.898 |

Lưới 1.458 (thang ĐĂNG KÝ TRƯỚC trong docstring `r4/calc/model_r4.py`): P10 **57.220** · P25 **62.065** · P50 68.037 · P75 **74.614** · P90 **80.784** (min 46.533, max 98.606).
Thang: RẺ ≤57.220 · RẺ CÓ ĐIỀU KIỆN 57.220–62.065 · HỢP LÝ 62.065–74.614 · NGHIÊNG ĐẮT 74.614–80.784 · ĐẮT ≥80.784.

**So giá (sau khoá): đóng cửa 03/11/2026 = 46.100** (DNSE `dnse_close_prices` G1, 'dnse_g1_today') ⇒ **RẺ (dưới P10, −19,4%); 0/1.458 bộ dưới giá (min 46.533 chỉ +0,9%).**
**Điều kiện an toàn (giá đá hoà vốn):** tâm = giá khi 100% hồi biên với trần **228k/m³** (tiền 2026) ở SL năm thường ⇒ biên đá **27,9%**; ở SL 1,40 trần 216k
(biên 28,3%); ở SL 1,05 trần 234k. Trên chi phí @1,40 thì 228k ≈ biên 31,9% (= số ~32% của skeptic). Tức **dưới TB chu kỳ 34,3%** — KHÔNG phải "đáy lịch sử"
(GPM NNC 2013/2022 21%). Đối chiếu: năm thường 2024 giá 245,2k danh nghĩa (≈260k tiền 2026), SL 1,05, biên đá 30,7%.
**Biên MỎNG ở trạng thái xấu:** CYCLICAL 53.278 (+16% so giá); CYCLICAL với trần tính ở SL 1,40 48.827 (+6%); CYCLICAL + giá danh nghĩa phẳng 41.663 (−10%).
Gordon P/B (r13 g3, BVPS 29.915) với ROE CHUẨN HOÁ theo trạng thái: khoá (NNC tự thân, không lãi tiền) 27,1/16,7/11,6% ⇒ trộn 17,0% ⇒ 41.838; bổ sung sau khoá
(cộng LN tài chính sau thuế 16,6 tỷ/năm, DT tài chính 9T 15,60 nâm hoá) 29,6/19,3/14,1% ⇒ trộn 19,5% ⇒ **49.429**. Giá hàm ý ROE bền 18,4%; tâm hàm ý 25,6%.
§2.5: NNC ở ĐỈNH chu kỳ, P/B 1,54 ⇒ không phải fear-buy.

| 3 kịch bản NĐT (= 3 trạng thái) | g2031 | thực |
|---|---|---|
| Biên đỉnh bền (20%) | 83.805 | 97.678 |
| Hồi biên một nửa (45%) | 62.892 | 74.001 |
| Về TB chu kỳ (35%) | 48.536 | 58.019 |

## 1. Kiểm kê khoản cộng/trừ gắn dự án mới & giả định (hiệu ứng = đưa khoản đó vào/bỏ ra khỏi tâm r3, đ/cp NNC; số: `r3/calc/model_r3_out.txt` mục "Kiem ke")


**Kiểm kê r4 (bổ sung cho bảng dưới — bảng giữ nguyên từ r3; dòng "Cắt sản lượng" và "Mốc giá 320 + stress" ĐÃ ĐỔI xử lý):**

| Khoản | Hiệu ứng (so tâm r4) | Cơ sở dữ liệu độc lập | Xử lý r4 |
|---|---|---|---|
| Chu kỳ biên mỏ hiện hữu (Mũi Tàu + Tân Lập) | r3→r4: −23.146 (chỉ STRUCTURAL = 90.742) | CÓ: Bobby §4 phân loại 0,20/0,45/0,35, pha "ĐỈNH → bình nguyên"; GPM NNC 2012–25 TB 34,2% (BQ) | **Trộn 3 trạng thái**; lưới 3 bộ trọng số (40/35/25, 15/35/50 = điều kiện đổi nhãn Bobby) |
| SL năm thường 1,10/1,20 ở nhánh hồi biên (cả Tân Lập) | 1,05: −508 · 1,20/1,30: +500 · Tân Lập giữ 1,30: +130 | CÓ: 2024 = 1,05 tr m³ (FPTS) ở giá 245,2k, GV TP kiểm toán 178,29/DT 257,44 [KT25 7.2] = 74% trần | Gắn với hồi biên; SL 1,40 chỉ ở STRUCTURAL |
| Trần chu kỳ: biên đá TP chu kỳ 34,3% trên chi phí mô hình ở SL của nhánh | tính ở SL 1,40 (236,1k): −2.559 | CÓ: GPM toàn cty TB 34,2% + chênh đá TP vs toàn cty TB 2024/25 (−0,9/+1,0 ⇒ +0,1pp); chi phí mô hình khớp GV kiểm toán (2024: 161,5 vs 169,8k/m³) | Trần 249,7k (SL TB 1,181); kiểm: trần @1,05 = 260,6k ≈ giá 2024 tiền 2026 260,1k (khớp) |
| Upside đối thủ hết GP (TL2 ~2033, TL3 ~2035; FPTS 07/01/2026) | +3.828 | CÓ về chiều/thời điểm (FPTS: Mũi Tàu hơn TL3 8 năm, TL2 10 năm); KHÔNG về độ lớn | Độ nhạy (từ 2034 stress ×0,5) — đối xứng với chiều xuống |

**Kiểm phép quy đổi skeptic (242,5k = biên 36%):** chi phí mô hình @1,40 = 155,2k/m³ ⇒ 242,5k = biên 36,0% (đúng số học). Nhưng biên chu kỳ ĐO được là 34,3%
(không phải 36%), và chi phí cố định/m³ phụ thuộc SL: ở SL năm thường 1,18 chi phí 164,2k ⇒ 242,5k chỉ còn biên 32,3%. Ghép trần 242,5k với cắt SL
= tính khấu hao biên hai lần. r4 dùng trần ở SL của nhánh (249,7k); trần @1,40 (236,1k) là trục lưới + độ nhạy (−2.559). Peers TB 2012–25: KSB 40,4%, DHA 26,0%, VLB 24,7%.
r3 ghi "GPM về TB 2012–25" cho trần 270k (`r3/calc/model_r3.py:142`, REPORT r3 :17–18,:29) là SAI NHÃN: 270k ≈ biên 42,4% trên chi phí mô hình @1,40.

| Khoản | Hiệu ứng | Cơ sở dữ liệu độc lập (nguồn) | Xử lý r3 |
|---|---|---|---|
| CIP Tam Lập 1 khu II 83,5 tỷ chỉ ở tốt/cơ sở (v2: xấu/rất xấu = 0) | −998 nếu giữ | KHÔNG (không có tín hiệu huỷ dự án) | **Sổ sách mọi kịch bản** |
| Chi phí trễ GP Tam Lập 1 khu II (P trễ 0/1/2 năm = 0,30/0,40/0,30) | −443 (giữ) | CÓ: Bobby F6 P(GP mỏ đấu giá trước 06/2027)=0,30; đối xứng với mỏ mới MVC r6 | Trong base (chi phí kỳ vọng 9,3 tỷ) |
| Upside Tam Lập 1 khu II (sản lượng thêm) | không định lượng | KHÔNG: chưa có GP/trữ lượng/công suất/capex công bố (AWM thứ cấp) | 0 ở base, chỉ định tính |
| Dự phòng truy thu CQ 15,58 + thuê đất 2019 Núi Nhỏ 5,95 + CQ Mũi Tàu 0,84 | −1.021 (giữ) | CÓ: BCTC Q3 V19a | Trừ ở tiền ròng |
| Đối xứng BCĐKT: ký quỹ PHMT 4,57 + thuế hoãn lại 4,31 (v2 trừ dự phòng nhưng không cộng tài sản đối ứng) | +424 | CÓ: BCTC Q3 V9 / tr.2 | **Cộng vào base** |
| Trả trước dài hạn CN Bình Phước 59,2 (phân bổ 3,2/quý, phi tiền mặt trong chi phí hiệu chỉnh) | +2.146 nếu cộng | CHƯA XÁC MINH bản chất (có thể là tiền thuê đất đã trả trước) | Độ nhạy |
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
| LN gộp cho thuê Núi Nhỏ 11,13 tỷ/năm tới 2043 | +3.500 (giữ) | CÓ: KT25 7.1–7.2 | Base |
| Chi phí K 0,97 (GV kiểm toán 2024–25) | ±6,6–6,7k (±10%) | CÓ: KT25 7.2 | Base; lưới |
| r 13% | −7,0k/+8,4k (15/11%) | Khung user (Ke nội địa) | Base; lưới |

## 2. Mô hình (`r4/calc/model_r4.py`; tái dùng `r3/calc/model_r3.py` + MVC r6 KHÔNG SỬA — md5 ở LOCK_md5_r4)
- Cầu nối kỳ vọng (đ/cp, `r4/calc/extras_r4_out.json`): Mũi Tàu 2027–43 gồm thuê 41.579 · tiền ròng 10.202 · 10,3% MVC 8.642 · CIP Tam Lập 3.810 − trễ GP 423
  · Q4/26 2.737 · NHC sổ sách 645 · ký quỹ + thuế hoãn lại 405 ⇒ 67.596. Ngoài mỏ ≈26.017 ⇒ giá 46.100 trả ≈20.083 cho mỏ (kỳ vọng 41.579; CYCLICAL ≈28.900).
- Lưới 1.458: r 11/13/15 × K 0,87/0,97/1,07 × W 3 bộ × PW g2031:thực 70:30/50:50/30:70 × trọng số trạng thái {20/45/35, 40/35/25, 15/35/50}
  × SL năm thường {1,05; 1,10/1,20; 1,20/1,30} × cơ sở trần {SL nhánh; SL 1,40}. Theo trọng số: Bobby P50 67.095; nghiêng STRUCT 73.724; nghiêng CYC 63.285.
- Độ nhạy (so tâm): K ±10% −6.299/+6.410 · r 15/11% −4.373/+5.258 · cho thuê Núi Nhỏ −3.500 · PW ±2.218 · phẳng 100% 53.480 · holding 15% −479 · bỏ đối xứng BCĐKT −424.

## 3. V_NNC cho MVC r7
V_NNC r4 = **67.596** (giải đồng thời; MVC trong cùng hệ = **18.392**, ≈ tham chiếu skeptic 18.305). MVC r7 dựng tiếp ở `dd_MVC_20261103/r7/`.

## 4. Điều kiện đổi nhận định (hai chiều; mốc khoá 03/11/2026)
- **Tiêu cực hơn:** biên gộp quý < 45% khi DT đi ngang (giá đá ≤228k/m³ tiền 2026 ⇒ giá trị ≈ giá); giá công bố Sở XD Q2/27 thấp hơn Q3/26 >7%; GP mỏ đấu giá trong cụm cấp sớm (trước 06/2027);
  truy thu/xử phạt mới >20 tỷ; MVC ≥51% kèm thoái MVC dưới giá trị; ĐHĐCĐ 2027 dồn tiền vào BĐS; thêm dòng tiền lớn với NHC.
- **Tích cực hơn:** biên ≥55% ở Q4/26 + Q1/27; giá công bố Q2/27 cao hơn >7%; VĐ4 ≥20% khối lượng tới 30/06/2027; GP Tam Lập 1 khu II kèm trữ lượng/công suất công bố
  (khi đó mới định lượng upside); công bố sản lượng m³; cổ tức tiền cao hơn.
- Mốc: BCTC Q4/26 ~20/01/2027 · Q1/27 ~20/04/2027 · VĐ4 & GP mỏ cụm 30/06/2027 · giá Sở XD Q2/27 (kiểm 31/08/2027).

## 5. Sản phẩm & kiểm
- Báo cáo NĐT: `investor_report_v3/NNC_DD_investor_report_20261103.{md,pdf,html}` (đè bản r3; bản r3 lưu `archive_internal/..._rev1.md`) — 11 trang; thân ~1.290 từ;
  grep luật 18 + luật 4/12 rỗng trên md + subject; dry-run email (`--html-out`): 16 ảnh, 9,5 MB, 16/16 `<img>` alt; **KHÔNG gửi**. md5 PDF d7a83986b1346368703ee172be3c3f9a.
  Hình định giá 00/12/13/14/23 dựng mới từ `r4/calc/*.json`; banner tiêu đề dựng lại. Chi tiết `investor_report_v3/SELFCHECK.md`.
- Sổ mức giá: `kb/dd_price_zones.json` NNC@2026-11-03#2 (supersedes #1); selfcheck 0 lỗi.
- ADV trung vị (BQ Price×Volume, đo trong r3): 20/60/120 phiên 1,43 / 1,38 / 1,39 tỷ.
- fundamental-skeptic: **CHƯA CHẠY** trên r4.

## 6. Giới hạn
Không có sản lượng m³ công bố; đường giá 2028+ và xác suất là nhận định; trữ lượng còn lại và dữ liệu mỏ cạnh tranh thứ cấp; tham số kế thừa dựng khi đã biết giá;
Xác suất 3 trạng thái là nhận định của Bobby (không phải tần suất); Gordon chỉ đối chiếu thô (mỏ hữu hạn 2043, ~1/3 vốn chủ là tiền/đầu tư); giá trị 10,3% MVC phụ thuộc mô hình MVC r6 chưa qua skeptic
(theo thị giá MVC 03/11 13.300 thì phần này thấp hơn ~2.400 đ/cp NNC).
