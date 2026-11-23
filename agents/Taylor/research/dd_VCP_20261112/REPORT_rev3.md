# DD VCP — REV 3 (CTCP Xây dựng và Năng lượng VCP, UPCoM) · dd_date 2026-11-12 · rev3 23/11/2026 · job `Taylor_20261123_063642`

> NGHIÊN CỨU READ-ONLY. Không khuyến nghị, không đặt lệnh, không email. User quyết.
> Bản này THAY `REPORT.md` (vòng 2, tâm 40.273) sau skeptic DD_GENERAL r1 = INCONCLUSIVE (`skeptic/r1.json`). Bản cũ giữ nguyên.
> Định giá MÙ giá: `calc_rev3/assumptions_rev3.json` + `calc_rev3/model_rev3.py` khoá md5 (`calc_rev3/LOCK_prerun_rev3.txt`) TRƯỚC khi đọc giá; giá/ADV đọc SAU (`calc_rev3/px_vcp_post_lock.csv`).
> Nguồn: **[KT25]** BCTC HN 2025 kiểm toán AASC (`src/bctc_hn_2025_audited.pdf`; ảnh `img2/kt25_p08.png` KQKD, `img2/kt25_p09.png` LCTT) · **[H1]** `src/bctc_hn_h1_2026_reviewed.pdf` · **[Q3]** `src/bctc_hn_q3_2026.pdf` ·
> **[BCTN25]** Báo cáo thường niên 2025 (`src_rev3/bctn_2025_vn.pdf`, tải vcpholdings.com.vn 23/11/2026, md5 `72ae0e11a278c7044362203c87e8b481`; text `src_rev3/bctn_2025_vn.txt`) ·
> **[BCTN23]** BCTN 2023 (`src_rev3/bctn_2023_vn.pdf`, md5 `86d84c13aa7934f965ed9628ac347f9c`) · **[BQ]** `tav2_bq.ticker_financial`.
> Toàn bộ `src/`, `img*/`, `calc/` của vòng 1–2 đã bị dọn ngày 19/11 (commit `ff5fe27cd`, weekly orphan review) và được **khôi phục từ git `ff5fe27cd^`** — md5 143 file ở `RESTORED_MD5_20261123.txt`. Số không đo được ghi **(ước lượng)**.

## 0. Kết luận

**Tâm 35.826 đ/cp trước chiết khấu thanh khoản; 34.522 đ/cp sau chiết khấu (vị thế 1 tỷ, 3,64%).**
**Vùng [26.525 ; 52.097]** trước CK = bear/bull; **sau CK [25.559 ; 50.201]**. r = 13,5%, terminal RONIC = Ke.

| | Rev2 (12/11) | **Rev3 (23/11)** |
|---|---|---|
| Tâm trước / sau CK | 41.560 / 40.273 | **35.826 / 34.522** (−14,3% sau CK) |
| Bear / Base / Bull (trước CK) | 21.669 / 40.475 / 67.385 | **26.525 / 32.988 / 52.097** |
| N base (LNST mẹ, tỷ) | 441,5 (2025 nguyên trạng) | **315,4** (2025 chuẩn hoá thuỷ văn, thuế KH2026, trừ quỹ KT-PL) |

**Giá 37.400 (đóng cửa 20/11/2026, đọc SAU khoá) = +8,3% so với tâm sau CK** ⇒ **TRONG VÙNG, TRÊN TÂM — không có biên an toàn** (ngưỡng 0,85 × tâm = 29.344).
Sizing V8 (2–4% NAV): **không đề xuất vị thế** ở giá hiện tại; thanh khoản nền (ADV60 trung vị 0,37 tỷ/phiên) giới hạn vị thế thực tế ≲ 0,3 tỷ.

**Ba thay đổi lớn nhất so với rev2:**
1. **Năm gốc 2025 là năm thuỷ văn đỉnh — nay ĐO được.** [BCTN25 tr.33–37]: sản lượng hợp nhất 2025 **1.009,6 triệu kWh = 132% kế hoạch** (KH 762); Cửa Đạt **591,4 triệu kWh so với Etb thiết kế 417 (142%)**. Thuỷ điện 2025 = 988,0 triệu kWh so với Etb 748,3 (**1,32×**). Chuẩn hoá về mức bình thường k = 1,081 × Etb (trung bình 2023–2025) ⇒ **−104,4 tỷ LNST mẹ** khỏi N.
2. **Thuế suất tăng đã nằm trong kế hoạch của chính công ty:** KH hợp nhất 2026 thuế 86,0 / LNTT 562,2 = **15,3%** (2025: 11,15%); riêng Cửa Đạt KH 2026 thuế **20%** (29,9/149,5) so với 15,0% năm 2025 [BCTN25 tr.37–38]. Áp vào base (×0,953).
3. **Tài sản/dự án 2026 cộng theo giá sổ (V4a, NPV = 0)** thay vì cách đọc A; terminal RONIC = Ke (D4) thay cho "ROE 17,1% > Ke vĩnh viễn". Hai thay đổi này đi theo chiều ngược nhau; xem §8.

**Rủi ro số 1 vẫn là phân bổ vốn** (cho vay cá nhân 823,4 tỷ 30/06/2026; 46,8% cp VCP cầm cố cho trái phiếu; lãi cho vay phần lớn dồn tích — §3 rev2 giữ nguyên). Pháp lý chỉ WARNING.

## 1. Đính chính so với rev trước (từng hạng mục skeptic r1)

| # | Hạng mục skeptic r1 | Xử lý rev3 | Loại | Tác động tâm (trước CK) |
|---|---|---|---|---|
| P | **Không truy được nguồn**: thiếu `src/`, `img*/`, `model_out.json`, `px_vcp.csv`, CSV comp | Khôi phục 143 file từ git `ff5fe27cd^` (md5 `RESTORED_MD5_20261123.txt`); md5 `calc/assumptions.json` 22d79a28… và `model.py` 198b5fad… khớp phụ lục A rev2. Nguồn mới BCTN 2023/2025 lưu `src_rev3/` + md5 | (a) | 0 |
| 1 | Ngày hết ưu đãi thuế (mô hình vĩnh viễn hoá ~11%) | **Base**: thuế theo KH hợp nhất 2026 = 15,3% [BCTN25 tr.38] (cơ sở độc lập: kế hoạch đã ĐHCĐ thông qua). **Ngày hết ưu đãi từng nhà máy: KHÔNG kiểm chứng được** — KT25 2.25 (PDF tr.19–20) chỉ nêu cơ chế "miễn 4 năm, giảm 50% 9 năm" cho Bái Thượng, Nậm La, Xuân Minh, Đak Robaye, Ngôi Sao Xanh và 10% cho thuỷ điện, không nêu năm; BCTN 2023/2025 không công bố. ⇒ độ nhạy 20% dài hạn | (a)+(c) | base ×0,953; độ nhạy 20% từ năm 0/5/10: **34.125 / 34.923 / 35.347** (−4,7% … −1,3%) |
| 2 | Hạn PPA Cửa Đạt + giá sau trả nợ | **Không kiểm chứng được** (HĐ 06/2012HĐ-NMĐ-Cửa Đạt + PL số 11 [KT25 TM9(6)] không công bố hạn/giá; BCTN không nêu). Giá bán Cửa Đạt 2025 = 429,07 tỷ / 591,42 triệu kWh = **725,5 đ/kWh** [BCTN25 tr.37]. Độ nhạy: Pc giảm 20% (ước lượng) từ năm 0 / năm 5 | (c) | **31.227 / 33.384** (−12,8% / −6,8%) |
| 3 | Thời hạn nhượng quyền xử lý rác Ngôi Sao Xanh (Bắc Ninh 62,5% DT) | **Không kiểm chứng được.** Đo được quy mô: NSX 2025 doanh thu + thu nhập khác **1.439,7 tỷ, LNST 174,15 tỷ** (KH 170), SL điện rác 21,58 triệu kWh [BCTN25 tr.36]; điện mặt trời mái NSX là BOT 20 năm chuyển giao NSX [BCTN25 tr.28]. Độ nhạy: nhượng quyền hết sau 20 năm (ước lượng) | (c) | **34.631** (−3,3%) |
| 4 | Giấy phép nước và đất | **Không kiểm chứng được** (không có trong BCTC/BCTN). Gộp trong rủi ro (2)/(3); không định lượng riêng | (c) | — |
| 5 | Capex còn lại Thác Ba / Đắk Lô | **Đo được TMĐT** [BCTN25 tr.28]: Đak Lô 1 **426** + Đak Lô 3 **787** (khởi công 03/2025, phát điện Q1/2027 và Q2/2028, vay MB), Đak Lô 4 **373**, Thác Ba **634** (BCTN23: 585) = **2.220 tỷ**; XDCB 30/09 = 540,1 [Q3] ⇒ còn lại **≈1.680 tỷ (ước lượng**, XDCB có thể gồm khoản khác). Là dự án TĂNG TRƯỞNG ⇒ **NPV = 0 (V4a)**; không phải capex tuân thủ (V4b). Tài trợ bằng vay ⇒ nợ vay/EBITDA tăng (hiển thị) | (a) | 0 (NPV0) |
| 6 | Trích quỹ khen thưởng phúc lợi | **Đo được, vào base**: phân phối LN 2022 của công ty mẹ: quỹ KT-PL 7,184 tỷ + phụ cấp HĐQT/BKS 0,336 tỷ [BCTN23 tr.47 PL06] / LNST mẹ 2022 408,6 [BQ] = **1,84%**. KT25 2.26 xác nhận EPS tính sau trích quỹ KT-PL và quỹ thưởng Ban điều hành | (a) | base ×0,9816 |
| 7 | One-off năm gốc: lãi cho vay dồn tích trong N base | **Đo được năm 2025**: DT tài chính 54,29 tỷ [KT25 KQKD mã 21] vs tiền thu lãi 23,25 tỷ [KT25 LCTT mã 27] ⇒ **31,0 tỷ chưa thu (57%)**, sau thuế 20% ≈ 24,8 tỷ. Chưa thu ≠ tổn thất ⇒ **độ nhạy**, tổn thất gốc nằm ở bear | (b) | **34.286** (−4,3%) |
| 8 | Base vĩnh viễn hoá thuỷ văn đỉnh La Niña | **Đo được, vào base** (BCTN25 per-plant + Etb thiết kế BCTN23/25): xem §2 | (a) | **−8.476 so với không chuẩn hoá** (42.302 → 35.826) |
| 9 | ROE 17,1% > Ke vĩnh viễn, trái với moat ≈ NONE | Terminal **RONIC = Ke** (D4): V_core = N/r, không có giá trị tăng trưởng. Không ép ROE giai đoạn dự báo (V5). ROE base trên B cuối 2025 sau chuẩn hoá = **14,7%** (gần Ke). Hiển thị cách cũ (RONIC = ROE): 36.932 | (a) | xem §8 |
| 10 | Chiều rẻ: N 2025 chưa có Đắk Lô 1-3/Linh Linh mà B0 đã gồm (cách đọc B) | **Áp vào base**: B cuối 2025 (2.146,8) sinh N chuẩn hoá; ΔB = 427,9 tỷ (2.574,7 − 2.146,8) cộng theo giá sổ (V4a NPV0) | (a) | + (đã gộp) |
| 11 | Chiều rẻ: DT điện 9T/26 792,5 ≈ cả năm 2025 | Ghi nhận ở bull (bull không chuẩn hoá thuỷ văn, giữ khả năng năm nước tốt lặp lại). KH 2026 công ty cũng ở mức cao: 879 triệu kWh, LNST HN 476,1 tỷ [BCTN25 tr.38] — dùng làm kiểm chéo bull | (b) | — |
| 12 | Bear vốn hoá N 2024 vĩnh viễn quá khắt khe; El Niño nên là cú sốc 1–2 năm | **Áp**: bear = base − PV cú sốc El Niño 2 năm (sản lượng = 88,45% Etb, mức 2023 [BCTN23 tr.18]) − lỗ cho vay 50% (401,9, giữ rev2) | (a)+(b) | bear 21.669 → **26.525** |

Loại: (a) định lượng có nguồn độc lập ⇒ base · (b) kịch bản/độ nhạy · (c) không kiểm chứng được + ảnh hưởng ước lượng.

## 2. Chuẩn hoá thuỷ văn (hạng mục 8)

| Nhà máy | Etb thiết kế (tr kWh) | TH 2025 | TH/Etb | DT/kWh 2025 (đ) | Thuế 2025 | Sở hữu |
|---|---|---|---|---|---|---|
| Cửa Đạt 97 MW | 417,0 | 591,4 | 1,42 | 725,5 | 15,0% | 100% (chi nhánh) |
| Nậm La + Tắt Ngoẵng | 129,3 | 159,7 | 1,24 | 1.225 | 4,7% | 82,76% |
| Bảng 1 (Xuân Minh/Đak Glun) | 66,1 | 80,7 | 1,22 | 1.032 | 10% (ước lượng; bảng ghi 52% bất thường) | 66,9% (ước lượng) |
| Bảng 2 (Đak Glun/Xuân Minh) | 75,8 | 74,0 | 0,98 | 1.091 | 4,4% | 66,9% (ước lượng) |
| Bái Thượng | 24,7 | 30,5 | 1,23 | 1.059 | 5,0% | 51% |
| Đak Robaye (COD 2024) | 35,4 | 51,7 | 1,46 | 1.102 | 4,0% | 100% |
| **Cộng thuỷ điện** | **748,3** | **988,0** | **1,320** | | | |

Nguồn: Etb [BCTN23 tr.10–12; BCTN25 tr.13–16]; TH, DT, LNTT/LNST từng đơn vị [BCTN25 tr.34–36]; sở hữu [BCTN25 tr.10 lịch sử: Bái Thượng 51%, Xuân Minh 51%, Nậm La 82,76%]. Gán "bảng 1/bảng 2" cho Xuân Minh/Đak Glun là ước lượng (BCTN không ghi tên trên bảng); tổng không đổi.
- **Mức bình thường k = 1,081 × Etb** = trung bình TH/Etb của 2023 (0,8845 = 630,58/712,9, El Niño, BCTN23 tr.18 và tr.10–11) · 2024 (1,039 — **ước lượng**: 779 triệu kWh tổng [BCTN25 tr.33] trừ NSX ~20 và Đak Robaye nửa năm) · 2025 (1,320). Dùng trung bình 3 năm quan sát thay vì Etb thiết kế vì công ty lập KH 2026 ở 1,15 × Etb (thuỷ điện 858,7) — tức Etb có thể thấp so với thực tế dài hạn.
- Phần vượt mỗi nhà máy × DT/kWh × (1 − chi phí biên 14,6%) × (1 − thuế) × sở hữu. Chi phí biên 14,6% = Cửa Đạt KH vs TH 2025: DT +132,94, chi phí +19,39 tỷ [BCTN25 tr.34] (ước lượng cho các nhà máy khác).
- **Kết quả: −104,4 tỷ LNST mẹ** (nếu k = 1, Etb thiết kế: −140,9 ⇒ tâm 33.560). Kiểm chéo: 2024 sản lượng ≈ Etb, N 2024 = 306,5 [BQ/KT25]; N base rev3 = 315,4.
- N base = (441,46 − 104,4) × 0,9532 (thuế 15,3%) × 0,9816 (KT-PL) = **315,4 tỷ**.

## 3. Bảng cân đối, dòng tiền, phân bổ vốn

Giữ nguyên §3 `REPORT.md` (rev2) — số đã đối chiếu lại với bản gốc khôi phục. Bổ sung đo năm 2025 [KT25 LCTT]: CFO 342,7 tỷ; capex 84,1; **chi cho vay 972,9, thu hồi 288,6**; góp vốn 496,2; vay mới 2.322,8, trả 994,0; cổ tức 67,8.
Capex cam kết còn lại ≈ 1.680 tỷ (ước lượng, §1 mục 5) tài trợ bằng vay ⇒ dư nợ 4.282 tỷ (30/09) có thể lên ~5.900 tỷ trước khi Đak Lô 1/3 phát điện (ước lượng, chỉ hiển thị).

## 4–7. Thuỷ điện, cổ đông, ngành, pháp lý

Giữ nguyên §4–§7 rev2. Bổ sung từ BCTN25: KH 2026 hợp nhất SL 879,2 triệu kWh, DT+thu nhập 2.435,8 tỷ, LNTT 562,2, LNST 476,1 tỷ; Cửa Đạt KH 2026 500,7 triệu kWh, LNTT 149,5 (2025: 242,9). Pháp lý: chỉ WARNING, không vào base.

## 8. Định giá — mù giá thị trường

**Công thức:** V = N / r + ΔB. N/r = giá trị phần tài sản cuối 2025 với terminal RONIC = Ke (D4: tăng trưởng không tạo giá trị); ΔB = 427,9 tỷ tài sản/dự án 2026 theo giá sổ (V4a NPV0). r = 13,5% (V1: lãi huy động 12T hiệu dụng 7,40% ngày 23/11/2026 = CCTG 12M 02/11, bằng điểm neo ⇒ Δ = 0; β = 1 là giả định). g = 2% không ảnh hưởng vì RONIC = Ke.

| Kịch bản | w | N (tỷ) | Cơ sở | Giá trị (tỷ) | đ/cp |
|---|---|---|---|---|---|
| Bear | 0,30 | 315,4 | Base − PV El Niño 2 năm (84,3 tỷ/năm = SL 88,45% Etb, PV 139,7) − lỗ cho vay 50% × 803,7 = 401,9 | 2.222,5 | **26.525** |
| Base | 0,45 | **315,4** | §2: 2025 chuẩn hoá thuỷ văn, thuế KH2026 15,3%, KT-PL 1,84% | 2.764,1 | **32.988** |
| Bull | 0,25 | 531,5 | TTM Q3/26 700,8 − biên phế liệu vượt thường 74,9 − lãi dồn tích chưa thu 57,8 (đều rev2 §0) = 568,1, × thuế KH2026 × KT-PL; **không** chuẩn hoá thuỷ văn. Kiểm chéo: KH LNST HN 2026 476,1 × 91,8% phần mẹ = 437 | 4.365,2 | **52.097** |
| **Tâm** | | | Trọng số 0,30/0,45/0,25 giữ rev2 (**ước lượng**, không có cơ sở định lượng) | | **35.826** |

Output: `calc_rev3/model_out_rev3.json`.

**Độ nhạy tâm (trước CK, đ/cp):**

| Biến | Giá trị |
|---|---|
| Lãi huy động −100 / −50 / +50 / +100bp, β=1 | 38.433 (+7,3%) / 37.079 (+3,5%) / 34.663 (−3,2%) / 33.580 (−6,3%) |
| Lãi huy động ±50 / ±100bp, β=0,5 | −50: 36.441 · +50: 35.234 · −100: 37.079 · +100: 34.663 |
| Ke dải nội địa (D4) 12,3% / 13,4% | 39.005 / 36.069 |
| Chuẩn hoá k = 1 (Etb thiết kế) / không chuẩn hoá | 33.560 / 42.302 |
| Thuế 20% dài hạn từ năm 0 / 5 / 10 | 34.125 / 34.923 / 35.347 |
| Cửa Đạt Pc −20% từ năm 0 / 5 (ước lượng) | 31.227 / 33.384 |
| NSX nhượng quyền hết sau 20 năm (ước lượng) | 34.631 |
| Base trừ lãi dồn tích 2025 chưa thu (24,8 tỷ sau thuế) | 34.286 |
| Lỗ cho vay bear 0% / 100% | 37.265 / 34.388 |
| Trọng số 0,35/0,45/0,20 · 0,40/0,40/0,20 · 0,25/0,45/0,30 | 34.548 · 34.225 · 37.105 |
| RONIC = ROE (cách rev2, ngầm thưởng; chỉ hiển thị) | 36.932 |

**V6 — hai nền (chỉ hiển thị, đầu vào rev2):** V_ngắn 37.394 · V_dài (FCFE mẹ 301,3/(r−g)) 31.269 · D = 0,179 < ln2 ⇒ không cờ. Base rev3 (32.988) nay nằm giữa hai nền; rev2 base (40.475) nằm trên cả hai. C4 = V_dài (capex < KH); D2 47.374 — "chưa qua tiêu chí khoá trước, chỉ theo dõi".

### Pha SAU KHOÁ — giá và thanh khoản (V3)

Đọc sau khi khoá md5 (`calc_rev3/px_vcp_post_lock.csv`, BQ `tav2_bq.ticker` tới 20/11/2026):
- Giá đóng cửa 20/11/2026 **37.400**. Biến động gần: 44.000 (17/11) → 37.200 (18/11) → 35.100 (19/11) → 37.400.
- Giá trị giao dịch trung vị: 250 phiên **0,273 tỷ**, 60 phiên **0,37 tỷ**, 20 phiên 10,3 tỷ (đột biến sau KQ Q3). σ ngày 250 phiên 2,22%.

| Vị thế | Phiên thoát (10% / 20% ADV60) | Chiết khấu σ√(Q/ADV60) | Tâm sau CK |
|---|---|---|---|
| **1,0 tỷ** (headline) | 27 / 13,5 | **3,64%** | **34.522** |
| 0,3 tỷ | 8,1 / 4,1 | 1,99% | 35.113 |
| 0,1 tỷ | 2,7 / 1,4 | 1,15% | 35.414 |

Free float, room ngoại: chưa đo (rev2 §5). Nhãn theo giá trị sau CK 1 tỷ: **37.400 = +8,3% trên tâm 34.522; trong vùng [25.559 ; 50.201]; trên 0,85 × tâm = 29.344 ⇒ không có biên an toàn.**

## 9. Vị thế & lợi thế cạnh tranh (5F) — V5

DD đầy đủ 12/11/2026 (< 12 tháng) ⇒ tái dùng §9 rev2: **moat_tier NARROW (cơ chế giấy phép), định lượng ≈ NONE**; rủi ro số 1 = phân bổ vốn. Kiểm nhanh 23/11: (i) BCTN25 xác nhận 2025 là năm thuỷ văn bất thường (132% KH), củng cố "biên gộp điện cao là cấu trúc tài sản, không phải hào"; (ii) NSX chiếm LNST 174 tỷ — nhượng quyền địa phương là lực thứ 6 (đồng hồ) chưa đo được. Tham số moat trong mô hình: không (RONIC = Ke chỉ ở terminal, D4).

## 10. Điều kiện đổi nhận định (hai chiều)

| Mốc | Nâng | Hạ |
|---|---|---|
| BCTC Q4/2026 (≤ 30/01/2027) | LN gộp ngoài điện ≥ 100 tỷ có thuyết minh khách hàng | Biên ngoài điện ≤ 5%; trích lập cho vay |
| BCTC KT 2026 (≤ 31/03/2027) | Chấp nhận toàn phần; dư nợ cho vay cá nhân ≤ 400 tỷ | Ngoại trừ/nhấn mạnh ⇒ bear thành trung tâm |
| BCTN 2026 / NQ ĐHCĐ 2027 | Công bố hạn PPA Cửa Đạt / nhượng quyền NSX dài | Hết ưu đãi thuế sớm; Pc Cửa Đạt giảm |
| Sản lượng 2026 | ≥ 1,15 × Etb (KH công ty) ⇒ k cao hơn | El Niño: ≤ 0,9 × Etb |
| Lãi huy động 12T | −50bp ⇒ +3,5% | +50bp ⇒ −3,2% |

## Phụ lục A — Khoá và nguồn

- Khoá rev3 (trước khi đọc giá): `assumptions_rev3.json` md5 **`fd9d6dd31dfde0c31600377473eb3c85`**, `model_rev3.py` md5 **`2bb3eef5380f4306459673b200a0ad86`** (`calc_rev3/LOCK_prerun_rev3.txt`). Chạy `OMP_NUM_THREADS=1 python3 calc_rev3/model_rev3.py`.
- Rev2 (khôi phục): `calc/assumptions.json` 22d79a2869f2f66a84d332c3e85069b7, `calc/model.py` 198b5fad0d76ce8fadb3d400c3c784a5, `calc/model_out.json`, `calc/px_vcp.csv`, `calc/peer_*.csv`.
- Nguồn mới: `src_rev3/MD5.txt`. Trích dẫn trang BCTN25 theo số trang in trong text trích xuất (`=====PAGE n` trong `src_rev3/bctn_2025_vn.txt`: KQ 2025 trang 33–36, KH 2026 trang 37–38, dự án trang 28; Etb trang 13–16; sở hữu/lịch sử trang 10).

## Phụ lục B — Còn mở / không kiểm chứng được

1. Ngày hết ưu đãi thuế từng nhà máy (độ nhạy −1,3% … −4,7%).
2. Hạn PPA Cửa Đạt và giá sau trả nợ (độ nhạy −6,8% … −12,8%, mức cắt 20% là ước lượng).
3. Thời hạn nhượng quyền rác NSX, giấy phép nước/đất (độ nhạy −3,3%).
4. Bản chất TS ngắn hạn khác 696,5 tỷ, ~1.000 tỷ góp vốn Q3 chưa thuyết minh, biên phế liệu Q3 — giữ như rev2 (bull đã trừ phần vượt thường).
5. Gán tên nhà máy cho bảng 1/2 BCTN25 và tỷ lệ 2024 của k là ước lượng.

## Phụ lục E — Phản biện

Skeptic DD_GENERAL r1 (22/11, trên `REPORT.md`): INCONCLUSIVE medium. Rev3 xử lý 12 hạng mục ở §1. Skeptic r2: chạy bằng `bin/dd_skeptic_run.py` trên bản này.
