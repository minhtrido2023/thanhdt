# DD VCP — REV 3b (CTCP Xây dựng và Năng lượng VCP, UPCoM) · dd_date 2026-11-12 · rev3b 23/11/2026 · job `Taylor_20261123_063642`

> NGHIÊN CỨU READ-ONLY. Không khuyến nghị, không đặt lệnh, không email. User quyết.
> Bản này THAY `REPORT.md` (vòng 2, tâm 40.273) và `REPORT_rev3.md` (tâm 34.522). Skeptic r1 (trên REPORT.md) và r2 (trên REPORT_rev3.md) đều INCONCLUSIVE; mục §1 liệt kê xử lý từng hạng mục của CẢ HAI vòng. Bản cũ giữ nguyên.
> Định giá MÙ giá: `calc_rev3/assumptions_rev3b.json` + `calc_rev3/model_rev3b.py` khoá md5 (`calc_rev3/LOCK_prerun_rev3b.txt`) TRƯỚC khi đọc giá; giá/ADV đọc SAU (`calc_rev3/px_vcp_post_lock.csv`).
> Nguồn: **[KT25]** BCTC HN 2025 kiểm toán AASC (`src/bctc_hn_2025_audited.pdf`; ảnh `img2/kt25_p08.png` KQKD, `img2/kt25_p09.png` LCTT) · **[H1]** `src/bctc_hn_h1_2026_reviewed.pdf` · **[Q3]** `src/bctc_hn_q3_2026.pdf` ·
> **[BCTN25]** Báo cáo thường niên 2025 (`src_rev3/bctn_2025_vn.pdf`, tải vcpholdings.com.vn 23/11/2026, md5 `72ae0e11a278c7044362203c87e8b481`; text `src_rev3/bctn_2025_vn.txt`) ·
> **[BCTN23]** BCTN 2023 (`src_rev3/bctn_2023_vn.pdf`, md5 `86d84c13aa7934f965ed9628ac347f9c`) · **[BQ]** `tav2_bq.ticker_financial`.
> Toàn bộ `src/`, `img*/`, `calc/` của vòng 1–2 đã bị dọn ngày 19/11 (commit `ff5fe27cd`, weekly orphan review) và được **khôi phục từ git `ff5fe27cd^`** — md5 143 file ở `RESTORED_MD5_20261123.txt`. Số không đo được ghi **(ước lượng)**.

## 0. Kết luận

**Tâm 33.837 đ/cp trước chiết khấu thanh khoản; 32.605 đ/cp sau chiết khấu (vị thế 1 tỷ, 3,64%).**
**Vùng [21.832 ; 46.990]** trước CK = bear/bull; **sau CK [21.037 ; 45.280]**. r = 13,5%, terminal RONIC = Ke.

| | Rev2 (12/11) | Rev3 (23/11, skeptic r2) | **Rev3b (23/11)** |
|---|---|---|---|
| Tâm trước / sau CK | 41.560 / 40.273 | 35.826 / 34.522 | **33.837 / 32.605** (−19,0% so với rev2 sau CK) |
| Bear / Base / Bull (trước CK) | 21.669 / 40.475 / 67.385 | 26.525 / 32.988 / 52.097 | **21.832 / 34.532 / 46.990** |
| N base (LNST mẹ, tỷ) | 441,5 | 315,4 | **332,8** |

**Giá 37.400 (đóng cửa 20/11/2026, đọc SAU khoá) = +14,7% so với tâm sau CK** ⇒ **TRONG VÙNG, TRÊN TÂM — không có biên an toàn** (0,85 × tâm = 27.715).
Sizing V8 (2–4% NAV): **không đề xuất vị thế** ở giá hiện tại; thanh khoản nền (ADV60 trung vị 0,37 tỷ/phiên) giới hạn vị thế thực tế ≲ 0,3 tỷ.

**Bốn thay đổi lớn nhất so với rev2:**
1. **Năm gốc 2025 là năm thuỷ văn đỉnh — ĐO được.** [BCTN25 tr.33–37]: sản lượng hợp nhất 2025 **1.009,6 triệu kWh = 132% kế hoạch** (KH 762); Cửa Đạt **591,4 so với Etb thiết kế 417 (142%)**. Thuỷ điện 2025 = 988,0 so với Etb 748,3 (**1,32×**). Mức bình thường k = **1,127 × Etb** = trung bình 4 năm quan sát 2022–2025 ⇒ **−85,7 tỷ LNST mẹ** khỏi N.
2. **Thuế suất tăng đã nằm trong kế hoạch công ty:** KH hợp nhất 2026 thuế 86,0 / LNTT 562,2 = **15,3%** (2025: 11,15%); Cửa Đạt KH 2026 **20%** (29,9/149,5) so với 15,0% năm 2025 [BCTN25 tr.37–38]. Áp vào base (×0,953).
3. **Base: tài sản 2026 theo giá sổ (V4a NPV0) + terminal RONIC = Ke (D4).** Bull không cộng ΔB (TTM đã gồm LN tài sản 2026).
4. **Bear thêm lỗ 50% trên ~1.000 tỷ góp vốn 9T/26 chưa thuyết minh** (gồm TS ngắn hạn khác 696,5) — ngoài lỗ cho vay 401,9.

**Rủi ro số 1 vẫn là phân bổ vốn** (cho vay cá nhân 823,4 tỷ 30/06/2026; ~1.000 tỷ góp vốn Q3 chưa thuyết minh; 46,8% cp VCP cầm cố cho trái phiếu; lãi cho vay phần lớn dồn tích — §3 rev2). Pháp lý chỉ WARNING.

## 1. Đính chính so với rev trước

### 1a. Hạng mục skeptic r1 (trên REPORT.md rev2)

| # | Hạng mục | Xử lý | Loại | Tác động / độ nhạy (tâm trước CK) |
|---|---|---|---|---|
| P | Không truy được nguồn (thiếu `src/`, `img*/`, `model_out.json`, `px_vcp.csv`, CSV comp) | Khôi phục 143 file từ git `ff5fe27cd^` (md5 `RESTORED_MD5_20261123.txt`); md5 `calc/assumptions.json` 22d79a28… và `model.py` 198b5fad… khớp phụ lục A rev2. Nguồn mới BCTN 2023/2025 ở `src_rev3/` + `src_rev3/MD5.txt` | (a) | 0 |
| 1 | Ngày hết ưu đãi thuế | **Base**: thuế theo KH hợp nhất 2026 = 15,3% [BCTN25 tr.38]. **Ngày hết ưu đãi từng nhà máy: KHÔNG kiểm chứng được** — KT25 2.25 (PDF tr.19–20) chỉ nêu cơ chế "miễn 4 năm, giảm 50% 9 năm" (Bái Thượng, Nậm La, Xuân Minh, Đak Robaye, Ngôi Sao Xanh) và 10% cho thuỷ điện, không nêu năm; BCTN 2023/2025 không công bố | (a)+(c) | base ×0,953; độ nhạy 20% dài hạn từ năm 0/5/10: **32.246 / 32.992 / 33.388** |
| 2 | Hạn PPA Cửa Đạt + giá sau trả nợ | **Không kiểm chứng được** (HĐ 06/2012HĐ-NMĐ-Cửa Đạt + PL số 11 [KT25 TM9(6)] không công bố hạn/giá). Giá bán Cửa Đạt 2025 = 429,07 tỷ / 591,42 triệu kWh = **725,5 đ/kWh** [BCTN25 tr.37]. Độ nhạy Pc −20% (ước lượng) từ năm 0 / 5 | (c) | **29.043 / 31.292** |
| 3 | Thời hạn nhượng quyền rác Ngôi Sao Xanh | **Không kiểm chứng được.** Quy mô đo được: NSX 2025 DT + thu nhập khác **1.439,7 tỷ, LNST 174,15 tỷ**, SL điện rác 21,58 triệu kWh [BCTN25 tr.36]. Độ nhạy: hết sau 20 năm (ước lượng) | (c) | **32.641** |
| 4 | Giấy phép nước/đất | Thời hạn dự án **50 năm** cho Thác Ba, Đak Robaye, Đak Lô 4 [BCTN23 tr.35 TM11]; ở r = 13,5%, 50 năm = 99,8% giá trị vĩnh viễn ⇒ bỏ qua. Giấy phép các nhà máy đang chạy: **không kiểm chứng được** | (a)+(c) | ≈ 0 |
| 5 | Capex còn lại Thác Ba / Đắk Lô | **TMĐT đo được** [BCTN25 tr.28]: Đak Lô 1 **426** + Đak Lô 3 **787** (khởi công 03/2025, phát điện Q1/2027 và Q2/2028, vay MB), Đak Lô 4 **373**, Thác Ba **634** = **2.220 tỷ**; XDCB 30/09 = 540,1 [Q3] ⇒ còn lại **≈1.680 tỷ (ước lượng)**. Dự án TĂNG TRƯỞNG ⇒ NPV0 (V4a); không phải capex tuân thủ (V4b) | (a) | 0 |
| 6 | Trích quỹ KT-PL | **Vào base**: quỹ KT-PL 7,184 + phụ cấp HĐQT/BKS 0,336 tỷ [BCTN23 tr.47 PL06] / LNST mẹ 2022 408,6 [BQ] = **1,84%**; KT25 2.26 xác nhận EPS tính sau trích quỹ | (a) | base ×0,9816 |
| 7 | Lãi dồn tích trong N base | **Đo năm 2025**: DT tài chính 54,29 [KT25 KQKD mã 21] vs tiền thu lãi 23,25 [KT25 LCTT mã 27] ⇒ 31,0 tỷ chưa thu, sau thuế 24,8. Chưa thu ≠ tổn thất ⇒ độ nhạy | (b) | **32.296** |
| 8 | Thuỷ văn đỉnh La Niña vĩnh viễn hoá | **Vào base** (§2) | (a) | không chuẩn hoá ⇒ 39.154 |
| 9 | ROE > Ke vĩnh viễn trái moat ≈ NONE | Terminal **RONIC = Ke** (D4): V_core = N/r. Không ép ROE giai đoạn dự báo (V5). Hiển thị RONIC = ROE: 35.063 | (a) | — |
| 10 | Cách đọc B (N 2025 chưa có tài sản 2026) | **Base**: ΔB = 427,9 tỷ (2.574,7 − 2.146,8) cộng giá sổ (V4a) | (a) | + |
| 11 | DT điện 9T/26 ≈ cả năm 2025 | Bull không chuẩn hoá thuỷ văn; k nay dùng 4 năm (§2) | (b) | — |
| 12 | Bear: El Niño là cú sốc 1–2 năm | Bear = base − PV El Niño 2 năm (SL 88,45% Etb, mức 2023) − lỗ cho vay 401,9 − lỗ pool chưa thuyết minh (1b mục A) | (a)+(b) | — |

### 1b. Hạng mục skeptic r2 (trên REPORT_rev3.md)

| # | Hạng mục | Xử lý rev3b | Tác động tâm (trước CK) |
|---|---|---|---|
| A | **~1.000 tỷ góp vốn 9T/26 + TS ngắn hạn khác 696,5 chưa thuyết minh, không bị haircut ở kịch bản nào** (killer) | Bản chất: **KHÔNG kiểm chứng được** (Q3 chưa soát xét không thuyết minh; BCTC soát xét/kiểm toán gần nhất là H1/26, trước khi khoản này phát sinh). Pool = LCTT 9T "góp vốn" −1.545,7 trừ Linh Linh 545,7 [H1 TM3] ≈ **1.000 tỷ**; TS ngắn hạn khác 696,5 nằm TRONG pool (rev2 §3), không cộng riêng. **Bear: lỗ 50%** (= 500 tỷ, ước lượng, cùng tỷ lệ lỗ cho vay). Base giữ giá sổ theo luật V4a (không có cơ sở độc lập để giảm) | bear −5.967 đ; tâm −1.790; độ nhạy lỗ 0% / 100%: **35.627 / 32.046** |
| B | Bull đếm trùng ΔB với TTM | Bull = N_bull / r, **không cộng ΔB** | bull −5.107; tâm −1.277 |
| C | Sở hữu nhà máy Etb 75,81 = 82,76% × 50,06% | Sửa: Đak Glun **41,43%** (Nậm La sở hữu 50,06% CTCP Thiết bị phụ tùng Sài Gòn [BCTN25 tr.14]); Xuân Minh 51% [BCTN25 tr.10] | nhỏ |
| D | Thời hạn dự án 50 năm có trong BCTN23 | Đã trích (1a mục 4) | ≈ 0 |
| E | k = 1,081 dựa 3 năm, có 2025 | **k = 1,127** = trung bình **4 năm 2022–2025**: thêm 2022 = (630,58/0,70)/712,9 = **1,264** từ BCTN23 tr.18 ("sản lượng 2023 toàn hệ thống chỉ bằng 70% năm 2022"). Gần KH công ty 1,15 × Etb. BCTN23 tr.18 cũng nêu lưu lượng về hồ Cửa Đạt 2023 ≈ 65% trung bình nhiều năm | k 1,081 / 1,15 / 1,0: **32.639 / 34.445 / 30.501** |
| F | ΔB đảo lập luận rev2 (cách đọc A) "không có thông tin mới" | Đúng — thay đổi không do thông tin mới mà do áp **luật user V4a** (dự án/đầu tư mới base NPV0 theo giá sổ; lệch khỏi 0 chỉ khi có cơ sở độc lập ⇒ vào kịch bản). Rủi ro của pool chưa thuyết minh chuyển sang bear (mục A), không ở base | — |

Loại: (a) định lượng có nguồn độc lập ⇒ base · (b) kịch bản/độ nhạy · (c) không kiểm chứng được + ảnh hưởng ước lượng.

## 2. Chuẩn hoá thuỷ văn

| Nhà máy | Etb (tr kWh) | TH 2025 | TH/Etb | DT/kWh 2025 (đ) | Thuế 2025 | Sở hữu hiệu dụng VCP |
|---|---|---|---|---|---|---|
| Cửa Đạt 97 MW | 417,0 | 591,4 | 1,42 | 725,5 | 15,0% | 100% (chi nhánh) |
| Nậm La + Tắt Ngoẵng | 129,3 | 159,7 | 1,24 | 1.225 | 4,7% | 82,76% |
| Xuân Minh (bảng 1) | 66,1 | 80,7 | 1,22 | 1.032 | 10% (ước lượng; bảng ghi 52% bất thường) | 51% |
| Đak Glun (bảng 2) | 75,8 | 74,0 | 0,98 | 1.091 | 4,4% | 41,43% |
| Bái Thượng | 24,7 | 30,5 | 1,23 | 1.059 | 5,0% | 51% |
| Đak Robaye (COD 2024) | 35,4 | 51,7 | 1,46 | 1.102 | 4,0% | 100% |
| **Cộng thuỷ điện** | **748,3** | **988,0** | **1,320** | | | |

Nguồn: Etb [BCTN23 tr.10–12; BCTN25 tr.13–16]; TH, DT, LNTT/LNST từng đơn vị [BCTN25 tr.34–36]; sở hữu [BCTN25 tr.10, tr.14]. Gán bảng 1/2 cho Xuân Minh/Đak Glun theo Etb gần nhất (ước lượng; BCTN không ghi tên trên bảng).
- **k = 1,127** = trung bình TH/Etb: 2022 **1,264** (BCTN23 tr.18) · 2023 **0,8845** (630,58/712,9, El Niño; BCTN23 tr.18) · 2024 **1,039 (ước lượng**: 779 triệu kWh [BCTN25 tr.33] trừ NSX ~20 và Đak Robaye nửa năm) · 2025 **1,320**. Chuỗi 4 năm gồm 1 năm El Niño và 2 năm nước nhiều; KH 2026 của công ty = 1,15 × Etb.
- Phần vượt mỗi nhà máy × DT/kWh × (1 − chi phí biên 14,6%) × (1 − thuế) × sở hữu. Chi phí biên 14,6% = Cửa Đạt KH vs TH 2025: DT +132,94, chi phí +19,39 tỷ [BCTN25 tr.34] (ước lượng cho nhà máy khác).
- **Kết quả: −85,7 tỷ LNST mẹ** (k = 1: −139,5). Kiểm chéo: 2024 sản lượng ≈ 1,04 × Etb, N 2024 = 306,5 [BQ/KT25].
- **N base = (441,46 − 85,7) × 0,9532 (thuế 15,3%) × 0,9816 (KT-PL) = 332,8 tỷ.**

## 3. Bảng cân đối, dòng tiền, phân bổ vốn

Giữ §3 `REPORT.md` (rev2) — số đã đối chiếu lại với bản gốc khôi phục. Bổ sung năm 2025 [KT25 LCTT]: CFO 342,7 tỷ; capex 84,1; **chi cho vay 972,9, thu hồi 288,6**; góp vốn 496,2; vay mới 2.322,8, trả 994,0; cổ tức 67,8.
Pool chưa thuyết minh 9T/26 ≈ 1.000 tỷ (§1b mục A) ≈ 11.900 đ/cp. Capex cam kết còn lại ≈ 1.680 tỷ (ước lượng) tài trợ bằng vay ⇒ dư nợ 4.282 tỷ (30/09) có thể lên ~5.900 tỷ trước khi Đak Lô 1/3 phát điện (ước lượng, chỉ hiển thị).

## 4–7. Thuỷ điện, cổ đông, ngành, pháp lý

Giữ §4–§7 rev2. Bổ sung từ BCTN25: KH 2026 hợp nhất SL 879,2 triệu kWh, DT+thu nhập 2.435,8 tỷ, LNTT 562,2, LNST 476,1 tỷ; Cửa Đạt KH 2026 500,7 triệu kWh, LNTT 149,5 (2025: 242,9) [tr.37–38]. Pháp lý: chỉ WARNING, không vào base.

## 8. Định giá — mù giá thị trường

**Công thức:** V = N / r (+ ΔB ở base/bear). N/r = giá trị tài sản cuối 2025 với terminal RONIC = Ke (D4). ΔB = 427,9 tỷ tài sản/dự án 2026 theo giá sổ (V4a NPV0). r = 13,5% (V1: lãi huy động 12T hiệu dụng 7,40% ngày 23/11/2026 = CCTG 12M 02/11, bằng điểm neo ⇒ Δ = 0; β = 1 giả định). g = 2% không ảnh hưởng vì RONIC = Ke.

| Kịch bản | w | N (tỷ) | Cơ sở | Giá trị (tỷ) | đ/cp |
|---|---|---|---|---|---|
| Bear | 0,30 | 332,8 | Base − PV El Niño 2 năm (97,9 tỷ/năm = SL từ 1,127 xuống 0,8845 × Etb; PV 162,3) − lỗ cho vay 50% × 803,7 = 401,9 [H1 PL01] − lỗ 50% pool 1.000 chưa thuyết minh = 500 | 1.829,3 | **21.832** |
| Base | 0,45 | **332,8** | §2: 2025 chuẩn hoá thuỷ văn, thuế KH2026, KT-PL; + ΔB 427,9 | 2.893,4 | **34.532** |
| Bull | 0,25 | 531,5 | (TTM Q3/26 700,8 − biên phế liệu vượt thường 74,9 − lãi dồn tích chưa thu 57,8) × thuế KH2026 × KT-PL; không chuẩn hoá thuỷ văn; **không cộng ΔB**. Kiểm chéo: KH LNST HN 2026 476,1 × 91,8% phần mẹ = 437 | 3.937,3 | **46.990** |
| **Tâm** | | | Trọng số 0,30/0,45/0,25 giữ rev2 (**ước lượng**, không có cơ sở định lượng) | | **33.837** |

Output: `calc_rev3/model_out_rev3b.json`.

**Độ nhạy tâm (trước CK, đ/cp):**

| Biến | Giá trị |
|---|---|
| Lãi huy động −100 / −50 / +50 / +100bp, β=1 | 36.534 (+8,0%) / 35.133 (+3,8%) / 32.633 (−3,6%) / 31.512 (−6,9%) |
| Lãi huy động −100 / −50 / +50 / +100bp, β=0,5 | 35.133 / 34.473 / 33.224 / 32.633 |
| Ke dải nội địa (D4) 12,3% / 13,4% | 37.127 / 34.088 |
| k = 1,0 (Etb) / 1,081 (rev3) / 1,15 (KH công ty) / không chuẩn hoá | 30.501 / 32.639 / 34.445 / 39.154 |
| Thuế 20% dài hạn từ năm 0 / 5 / 10 | 32.246 / 32.992 / 33.388 |
| Cửa Đạt Pc −20% từ năm 0 / 5 (ước lượng) | 29.043 / 31.292 |
| NSX nhượng quyền hết sau 20 năm (ước lượng) | 32.641 |
| Base trừ lãi dồn tích 2025 chưa thu (24,8 tỷ sau thuế) | 32.296 |
| Lỗ cho vay bear 0% / 100% | 35.276 / 32.398 |
| Lỗ pool chưa thuyết minh ở bear 0% / 100% | 35.627 / 32.046 |
| Trọng số 0,35/0,45/0,20 · 0,40/0,40/0,20 · 0,25/0,45/0,30 | 32.579 · 31.944 · 35.095 |
| RONIC = ROE (ngầm thưởng; chỉ hiển thị) | 35.063 |

**V6 — hai nền (chỉ hiển thị, đầu vào rev2):** V_ngắn 37.394 · V_dài (FCFE mẹ 301,3/(r−g)) 31.269 · D = 0,179 < ln2 ⇒ không cờ. Base rev3b (34.532) nằm giữa hai nền. C4 = V_dài (capex < KH); D2 47.374 — "chưa qua tiêu chí khoá trước, chỉ theo dõi".

### Pha SAU KHOÁ — giá và thanh khoản (V3)

Đọc sau khi khoá md5 (`calc_rev3/px_vcp_post_lock.csv`, BQ `tav2_bq.ticker` tới 20/11/2026):
- Giá đóng cửa 20/11/2026 **37.400**. Biến động gần: 44.000 (17/11) → 37.200 (18/11) → 35.100 (19/11) → 37.400.
- Giá trị giao dịch trung vị: 250 phiên **0,273 tỷ**, 60 phiên **0,37 tỷ**, 20 phiên 10,3 tỷ (đột biến sau KQ Q3). σ ngày 250 phiên 2,22%.

| Vị thế | Phiên thoát (10% / 20% ADV60) | Chiết khấu σ√(Q/ADV60) | Tâm sau CK |
|---|---|---|---|
| **1,0 tỷ** (headline) | 27 / 13,5 | **3,64%** | **32.605** |
| 0,3 tỷ | 8,1 / 4,1 | 1,99% | 33.164 |
| 0,1 tỷ | 2,7 / 1,4 | 1,15% | 33.448 |

Free float, room ngoại: chưa đo (rev2 §5). Nhãn theo giá trị sau CK 1 tỷ: **37.400 = +14,7% trên tâm 32.605; trong vùng [21.037 ; 45.280]; trên 0,85 × tâm = 27.715 ⇒ không có biên an toàn.**

## 9. Vị thế & lợi thế cạnh tranh (5F) — V5

DD đầy đủ 12/11/2026 (< 12 tháng) ⇒ tái dùng §9 rev2: **moat_tier NARROW (cơ chế giấy phép), định lượng ≈ NONE**; rủi ro số 1 = phân bổ vốn. Kiểm nhanh 23/11: (i) BCTN25 xác nhận 2025 là năm thuỷ văn bất thường (132% KH) — biên gộp điện cao là cấu trúc tài sản, không phải hào; (ii) NSX LNST 174 tỷ — nhượng quyền địa phương là đồng hồ cắt hào chưa đo được. Không có tham số moat trong mô hình (RONIC = Ke chỉ ở terminal, D4).

## 10. Điều kiện đổi nhận định (hai chiều)

| Mốc | Nâng | Hạ |
|---|---|---|
| BCTC Q4/2026 (≤ 30/01/2027) | LN gộp ngoài điện ≥ 100 tỷ có thuyết minh; thuyết minh pool 1.000 tỷ là tài sản sinh lời | Biên ngoài điện ≤ 5%; trích lập cho vay / pool |
| BCTC KT 2026 (≤ 31/03/2027) | Chấp nhận toàn phần; dư nợ cho vay cá nhân ≤ 400 tỷ | Ngoại trừ/nhấn mạnh ⇒ bear thành trung tâm |
| BCTN 2026 / NQ ĐHCĐ 2027 | Công bố hạn PPA Cửa Đạt / nhượng quyền NSX dài | Hết ưu đãi thuế sớm; Pc Cửa Đạt giảm |
| Sản lượng 2026 | ≥ 1,15 × Etb (KH công ty) | El Niño ≤ 0,9 × Etb |
| Lãi huy động 12T | −50bp ⇒ +3,8% | +50bp ⇒ −3,6% |

## Phụ lục A — Khoá và nguồn

- Khoá rev3b (trước khi đọc giá): `calc_rev3/assumptions_rev3b.json` md5 **`8d93c85bd812d4841090ca0c80f40dac`**, `calc_rev3/model_rev3b.py` md5 **`ee7bf53e66855f3bdd3d3fbd57d38ba1`** (`calc_rev3/LOCK_prerun_rev3b.txt`). Chạy `OMP_NUM_THREADS=1 python3 calc_rev3/model_rev3b.py`.
- Rev3 (skeptic r2): `assumptions_rev3.json` fd9d6dd31dfde0c31600377473eb3c85, `model_rev3.py` 2bb3eef5380f4306459673b200a0ad86. Rev2 (khôi phục): `calc/assumptions.json` 22d79a2869f2f66a84d332c3e85069b7, `calc/model.py` 198b5fad0d76ce8fadb3d400c3c784a5.
- Giá/ADV đọc SAU khoá rev3 (fd9d6dd3…); thay đổi rev3b chỉ dựa trên phản biện r2 và nguồn BCTN (không dùng giá). Số trang BCTN = chỉ số `=====PAGE n` trong `src_rev3/bctn_2025_vn.txt` / `bctn_2023_vn.txt`.

## Phụ lục B — Còn mở / không kiểm chứng được

1. Bản chất ~1.000 tỷ góp vốn 9T/26 và TS ngắn hạn khác 696,5 — chờ BCTC KT 2026 (bear đã trừ 50%; độ nhạy 0–100%: 35.627–32.046).
2. Ngày hết ưu đãi thuế từng nhà máy (độ nhạy −1,3% … −4,7%).
3. Hạn PPA Cửa Đạt và giá sau trả nợ (độ nhạy −7,5% … −14,2%; mức cắt 20% là ước lượng).
4. Thời hạn nhượng quyền rác NSX; giấy phép các nhà máy đang chạy (độ nhạy NSX −3,5%).
5. Gán tên bảng 1/2 BCTN25 và tỷ lệ 2024 của k là ước lượng; trọng số kịch bản là ước lượng.

## Phụ lục E — Phản biện

Skeptic DD_GENERAL r1 (22/11, REPORT.md): INCONCLUSIVE medium. r2 (23/11, REPORT_rev3.md, 1,03 USD): INCONCLUSIVE medium — killer: pool 1.000 tỷ chưa haircut; bull đếm trùng ΔB. Rev3b xử lý ở §1b. Skeptic r3 (vòng cuối của job): chạy bằng `bin/dd_skeptic_run.py` trên bản này.
