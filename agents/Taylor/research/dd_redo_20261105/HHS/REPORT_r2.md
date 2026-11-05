# DD REDO VÒNG 2 — HHS · 05/11/2026 · job `Taylor_20261105_020013`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị. Áp `STANDARD_r2.md`. Mô hình NAV holding (BCTC gốc Q3HN 30/09/2026 + tham số DD TCH v2) **chép nguyên** vòng 1 (`calc/hhs_redo.py` dòng 2–40).
> **Tái lập:** `$DNA_PYEXE -I calc/hhs_r2.py > calc/hhs_r2_out.txt` — 2 lần trùng byte (`calc/LOCK_r2_outputs_md5.txt`). Số từ `calc/hhs_r2_out.txt` / `SUMMARY.json` (vòng 1: `SUMMARY_r1.json`, `REPORT.md`).
> Giả thuyết, chất lượng LN, cổ đông: giữ `REPORT.md` §2–§4.

## 1. Kết luận

| Chỉ số (sau CK @5 tỷ) | Vòng 2 | Vòng 1 |
|---|---|---|
| Giá 04/11/2026 | **9.550** | 9.550 |
| r | 13,50% | 13,50% |
| **Tâm** (kỳ vọng lưới kết cục) | **10.387** | 10.611 |
| P10 / P50 / P90 (mức kết cục, `wpct`) | **8.252 / 10.194 / 12.827** | 8.415 / 10.615 / 13.010 |
| n kết cục · % trọng số dưới giá · min | **5.400 · 35,2% · 6.070** | 45 · — · — |
| Giá vs tâm | **−8,1%** | −10,0% |
| **Nhãn** | **TRONG vùng** (P10–P90 mức kết cục; CK ở cỡ 5 tỷ — xem §5: cỡ này NGOÀI vùng hiệu chỉnh) | TRONG vùng |

Định nghĩa vùng không đổi ⇒ nhãn không đổi do định nghĩa (điều 7).

## 2. Ba con số (điều 4)
- **Tâm 10.387** · **P50 10.194** · **giá trị tại tham số trung tâm** (CƠ SỞ, Δthặng dư 0, **CK holding 0 = NAV thuần**, quản trị 0, BĐSĐT 0, I.14 NPV 0, ký quỹ 0) **13.731**; cùng tham số nhưng CK holding 25% (tham số trung tâm vòng 1) = **10.805**.
- Khoảng cách tham số trung tâm ↔ tâm (−3,3k) gần như toàn bộ là **CK holding** (trục có xác suất, kỳ vọng 27%) cộng CK quản trị (kỳ vọng 4%).
- P10 không do một nhánh: quanh P10 ±5% TIÊU CỰC 49% / CƠ SỞ 46%; quanh P90 CƠ SỞ 49% / TÍCH CỰC 35% / TIÊU CỰC 16% — phân tán do nhiều trục độc lập, không có đuôi một nhánh.

## 3. Lưới kết cục (điều 1, 2)
Ô tất định ⇒ kết cục = ô. n = 3 × 5 × 5 × 4 × 3 × 3 × 2 = **5.400**. File `calc/grid_hhs_r2.csv`.

| Trục | Điểm (trọng số) | Chiều |
|---|---|---|
| Kịch bản | TIÊU CỰC 0,30 / CƠ SỞ 0,50 / TÍCH CỰC 0,20 (biên backlog 30/33,5/36%, thặng dư HTK cũ 15/40/55%, ô tô LNST×P/E 25×5 / 35×6 / 50×8) | hai chiều |
| Δ thặng dư HTK CRV cũ | −15 / −7,5 / 0 / +7,5 / +15 pp | hai chiều |
| **CK holding (tách khỏi kịch bản)** | 0% 0,10 / 15% 0,15 / 25% 0,30 / 35% 0,30 / 45% 0,15 [UL] (kỳ vọng 27%; vòng 1 gắn kịch bản 35/25/15 ±5pp, kỳ vọng 26%) | hai chiều |
| **CK quản trị (MỚI vào lưới)** | 0 0,55 / 5% 0,20 / 10% 0,15 / 15% 0,10 [UL] — điểm = mức DD 01/11 | chỉ xuống (không tồn tại "phần bù quản trị") |
| **Thặng dư BĐSĐT CRV (MỚI)** | 0 / 50% / 100% thực hiện (đều) [UL]; 100% = +967 đ/cp trước CK holding (cận dưới chênh sổ 2.459,74 − 1.438,45, sau thuế) | lên |
| **I.14 (MỚI vào lưới)** | −15% 0,25 / 0 0,50 / +40% 0,25 [UL]; +40% = +379 đ/cp trước CK holding | hai chiều |
| **Ký quỹ cá nhân 28,4 tỷ (MỚI)** | 0 0,70 / mất trắng 0,30 [UL]; mất trắng = −66 đ/cp | xuống |

Vòng 1 để CK quản trị (xuống), BĐSĐT (lên), I.14 (hai chiều) làm độ nhạy ngoài lưới ⇒ vi phạm điều 2 cả hai chiều; vòng 2 đưa cả vào.

| Bản song song | n | Tâm | P10 | P50 | P90 | % dưới giá |
|---|---|---|---|---|---|---|
| **Chính** | 5.400 | 10.387 | 8.252 | 10.194 | 12.827 | 35,2% |
| Không CK holding (NAV thuần) | 1.080 | 13.506 | 11.823 | 13.509 | 15.181 | 0,0% |
| Không trục quản trị | 1.350 | 10.820 | 8.703 | 10.612 | 13.261 | 25,5% |
| Không trục BĐSĐT | 1.800 | 10.053 | 8.014 | 9.871 | 12.373 | 42,6% |
| Không trục I.14 | 1.800 | 10.346 | 8.225 | 10.152 | 12.745 | 36,1% |
| Không trục ký quỹ | 2.700 | 10.406 | 8.275 | 10.218 | 12.840 | 35,0% |
| Thêm trục r ±1pp | 16.200 | 10.388 | 8.253 | 10.196 | 12.823 | 35,1% |
| Lưới vòng 1 tính lại bằng `wpct` | 45 | 10.611 | 8.415 | 10.615 | 13.010 | 28,0% |

**Trục quyết định nhãn là CK holding**: bỏ nó (NAV thuần) thì 0% trọng số dưới giá, giá thấp hơn P10. Mức CK holding hoàn toàn là [UL] (§4).

Trục loại có lý do: **r** (NAV gần như không nhạy — bản có trục r gần như trùng); **KL 08 Pruksa** (điều chỉnh giá bán NƠXH — không có số để lượng hoá) và **N01 tiền SDĐ bổ sung 7,87 tỷ** (≈ 9 đ/cp — không trọng yếu) ⇒ WARNING; **điều chỉnh soát xét LN Q3** ⇒ WARNING + mốc M1.

## 4. Base so với sổ sách (điều 3)
| Khoản | Tham số trung tâm | Cơ sở · nguồn |
|---|---|---|
| **CK holding** | **0** (vòng 1: 25% ở base) | Mức 25% **không có cơ sở dữ liệu định lượng** (vòng 1 tự ghi "ước lượng") ⇒ theo điều 3 **chuyển khỏi base**, chỉ còn ở trục có xác suất. Cơ sở định tính cho việc có CK: CRV chưa trả cổ tức tiền về HHS 9T/2026 [Q3HN LCTT]; tiền NC-II lên HHS qua 2 tầng; tiền mẹ 171 tỷ. |
| CRV theo giá gốc (GTHL 15.818 − thặng dư PPA sau thuế 8.083) | có | Thuế hoãn lại 2.020,76 [Q3HN]; lãi đánh giá lại PPA là ghi nhận kế toán nội bộ nhóm, không phải giá trị kinh tế [GAPS_FILL:30–50] |
| Thặng dư HTK cũ 40% (CƠ SỞ) | có | biên NC-II quan sát 51,9–52,2% (base có đệm) |
| I.14 1.329 tỷ | 0 (giá sổ, NPV 0) | chưa mở bán; HTK TM18 |
| CK quản trị | 0 | pháp lý/quản trị = WARNING; mức chỉ ở trục |

## 5. Thanh khoản (điều 6) — ⚠ cỡ tham chiếu NGOÀI vùng hiệu chỉnh
| | ADV 250 phiên | ADV 60 phiên |
|---|---|---|
| ADV trung vị | 16,2 tỷ | 8,9 tỷ |
| CK @ **5 tỷ** | **1,443%** | 1,535% |
| CK @ sleeve 10 / 40 triệu | 0,0645% / 0,1291% | — |

- **5 tỷ = 30,8% ADV250 (56,1% ADV60) — TRÊN vùng hiệu chỉnh** luật căn bậc hai (ước lượng ~0,1–20% ADV) ⇒ CK 1,44% có thể **đánh giá thấp**. Nhãn vẫn tính ở 5 tỷ để đồng nhất liên mã; ngay cả khi CK ở 5 tỷ gấp đôi (2,89%), P10 = 8.373 × (1 − 2,89%) = 8.131 vẫn dưới giá ⇒ nhãn không nhạy với điểm này.
- Sleeve 40 triệu = 0,25% ADV (trong vùng); 10 triệu = 0,06% (dưới vùng, nửa spread chưa đo). Free float 36,6% (1 − TCH 58,31% − nhóm Đinh Quang Chiến 5,12%).

## 6. Đối chiếu (điều 10)
Gordon/ROE: **không áp dụng** (NAV holding, không có dòng ROE ổn định; LN Q3 chưa soát xét). Đối chiếu P/B TCH 0,98x VCSH mẹ ⇒ 11.385 (vòng 1 §6).

## 7. Tham số tự đặt [UL]
Trọng số kịch bản 0,30/0,50/0,20; biên backlog, thặng dư HTK cũ, LNST ô tô, P/E ô tô từng kịch bản; Δthặng dư ±15pp (đều); **CK holding 0/15/25/35/45% và trọng số**; **CK quản trị 0/5/10/15% và trọng số**; **BĐSĐT 0/50/100% (đều)**; **I.14 −15/0/+40% (0,25/0,5/0,25)**; **ký quỹ 0/100% (0,7/0,3)**; I.14 nằm trong HTK CRV còn lại 7.338,8 (chưa đối chiếu dòng); free float; Y = 1.

## 8. Mốc HAI chiều + HARD ABANDON (điều 8)
Giữ M1–M7 (`REPORT.md` §7):
- **Lên**: M1 BCTC 2026 kiểm toán (03/2027) — LNST mẹ 9T không bị điều chỉnh >10%, kiểm toán sạch; M3 cổ tức tiền CRV về HHS ≥ 500 tỷ toàn CRV (31/12/2027) ⇒ dồn trục CK holding về 0–15%; M2 xe Q4: DT ≥ 200, HTK < 450; I.14 có giá mở bán kiểm được ⇒ dồn trục I.14 lên.
- **Xuống**: M1 điều chỉnh >10% hoặc ngoại trừ/nhấn mạnh PPA/HTK; không có cổ tức CRV ⇒ dồn trục CK holding lên 35–45%; xe DT < 150 và HTK > 600 hoặc trích DP; M4 danh tính người bán HHS Capital là bên liên quan / M7 QĐ phạt-khởi tố mới ⇒ dồn trục quản trị lên 10–15%.
- **HARD ABANDON**: kiểm toán từ chối/ngoại trừ trọng yếu về PPA hoặc HTK CRV; người bán HHS Capital xác nhận là bên liên quan của TCH; CRV mất quyền kiểm soát (biểu quyết < 50% khi hết uỷ quyền 7,53%); khởi tố pháp nhân trong nhóm TCH–HHS–CRV.
- Ngưỡng nhãn: DƯỚI vùng nếu giá < 8.252; TRÊN vùng nếu > 12.827.
- **Không đủ điều kiện sleeve fear-buy §2.5**: không có cú sốc sợ hãi đặc thù đang diễn ra; chiết khấu là cấu trúc holding. Cỡ vị thế 5 tỷ vượt vùng thanh khoản (§5) ⇒ nếu có vị thế lớn phải chia tranche (≤ 20% ADV/đợt ≈ ≤ 3,2 tỷ theo ADV250, ≤ 1,8 tỷ theo ADV60).

## 9. WARNING pháp lý / quản trị — đầy đủ (điều 5)
Nguồn rà: `dd_HHS_20261101/{SKEPTIC_20261101,GAPS,GAPS_FILL,BRIEF_gaps,REPORT,REPORT_v1}.md`, vòng 1.
1. **HHS Capital** mua 50.098.000 CP CRV 18/06/2025 giá 1.302,55 tỷ (26.000 đ/cp, cao hơn GTHL ~23.131 khoảng 12% ⇒ premium 143,5 tỷ ≈ 3,5% vốn hoá, ghi giảm LNST chưa phân phối); người bán không nêu tên; tờ trình 07/TT-HĐQT (31/03/2025) chỉ khẳng định "không phải người liên quan"; không định giá độc lập; Điều 10 ĐHĐCĐ 24/04/2025 99,459% tán thành, TCH được bỏ phiếu; BBTT 02/2025 (06/05/2025) trao quyền bổ nhiệm HĐQT/GĐ HHS Capital trước khi trả tiền; ngày lập HHS Capital lệch 31/03 vs 31/05/2025 chưa hoà giải [GAPS_FILL:10–28; GAPS G4, G15]. MỞ, trung bình. **Nghị quyết ĐHĐCĐ = dữ liệu, đã vào trục quản trị.**
2. **Sở hữu chồng tầng TCH 58,31% → HHS → ~51,15% lợi ích CRV**; uỷ quyền biểu quyết 7,37–7,53% CRV từ nhóm cổ đông không tên, không thời hạn; nhóm TCH kiểm soát 89,35% biểu quyết CRV; không uỷ quyền vẫn > 50% (biên 1,15đ%) [GAPS_FILL:20]. MỞ.
3. **KL 08/KL-TTTP (26/02/2026, Thanh tra TP Hải Phòng)** NƠXH Pruksa (HHS 90,17%): rà soát, điều chỉnh giá bán theo quyết toán; sau niên độ, kiểm toán không điều chỉnh. MỞ.
4. **TB 2124/TB-TTCP (11/10/2024)** đất khối đế toà N01 (Golden Land) của CRV: tiền SDĐ bổ sung tạm trích 7,87 tỷ, CRV chưa nhận văn bản chính thức [GAPS_FILL:84–88]. MỞ (MỚI mang theo vòng 2).
5. Chi phí "tax penalties and additional tax assessments" 2025 = 2,44 tỷ (2024: 0,04), không nêu QĐ/cơ quan [GAPS_FILL:81]. MỞ, nhỏ.
6. **Công ty mẹ TCH**: QĐ 1357/QĐ-XPHC 05/12/2024 (UBCKNN, 295 triệu); QĐ 1020/QĐ-XPHC thuế 20,21 tỷ (04/2026). WARNING ở công ty mẹ.
7. **Q3/2026 chưa soát xét**; 6T sau soát xét AASC bị hạ LNTT −29%, LNST mẹ −34% so tự lập ⇒ Q3 LNST mẹ 115,8 có rủi ro tương tự. MỞ (M1).
8. Ký quỹ 28,4 tỷ cho cá nhân Phạm Văn Xuân (31/12/2025 chỉ 3,77), mục đích không rõ — nay là trục lưới. MỞ.
9. Nhóm Đinh Quang Chiến + PT Đô thị Từ Liêm + Thuỷ điện Trà Xom 5,06% → 5,12% (19/10/2026); chưa đọc tỷ lệ sau 21/10. MỞ.
10. Bảo lãnh/mua lại xe: BCTC 2025 không thuyết minh ("không thuyết minh ≠ không có"); vay duy nhất 390 tỷ của CRV (VietinBank Ngô Quyền, **đáo hạn 18/11/2026**, thế chấp NC-II, HHS mẹ không bảo lãnh); phải trả Dongfeng 364,01 tỷ. Một phần.
11. PPA chỉ thuyết minh tổng; haircut là ước lượng. MỞ.
12. Dự toán chi phí còn lại để giao căn NC-II đã nhận tiền (3.099) chưa có ⇒ net cash thật chưa trừ khoản này (G10). MỞ.
13. Đại lý Dongfeng: không có từ "độc quyền", số xe/hợp đồng/thời hạn chưa có. MỞ.
14. **"Chưa thấy QĐ xử phạt HHS 2023–2026"**: nguồn = CBTT HHS trang 1–7, BCTN 2025, web search, ngày 01/11/2026 (`dd_HHS_20261101/GAPS_FILL.md`:80); **chưa truy cập ssc.gov.vn; chưa quét tin 01–05/11**.

## 10. LOCK md5 (điều 9)
Dòng `LOCK` trong `calc/hhs_r2_out.txt`: `hhs_r2.py`, `hhs_redo.py`, `_common_014125/{common.py,r2common.py,bq_px_liq_20261104.csv}`, `_shared/wpct.py`, `deposit_rate_vn.py`, `cctg_rate_vn.py`, `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn_events.csv`, `kb/dd_price_zones.json` (chỉ đọc).

## 11. Thay đổi so vòng 1 và lý do
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| CK holding | 25% ở base (kịch bản 35/25/15 ±5) | 0 ở tham số trung tâm; trục 5 điểm kỳ vọng 27% | điều 3 |
| CK quản trị | độ nhạy ngoài lưới | trục 4 điểm | điều 2 — tâm −433 |
| BĐSĐT CRV | upside ngoài tâm | trục 3 điểm | điều 2 — tâm +334 |
| I.14 | độ nhạy ngoài lưới | trục 3 điểm | điều 2 — tâm +41 |
| Ký quỹ cá nhân | WARNING | trục 2 điểm | điều 2 — tâm −19 |
| Phân vị | 45 ô | 5.400 kết cục, `wpct` | điều 1 |
| Tâm / P10 / P90 | 10.611 / 8.415 / 13.010 | 10.387 / 8.252 / 12.827 | các trục trên |
| Nhãn | TRONG vùng (−10,0%) | TRONG vùng (−8,1%) | không đổi |

Chưa qua fundamental-skeptic vòng 2. Không sửa `dd_price_zones.json`, không PDF/email.
