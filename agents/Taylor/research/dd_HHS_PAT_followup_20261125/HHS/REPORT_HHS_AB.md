# HHS — Phương án A/B biên hàng tồn kho cũ (25/11/2026, job Taylor_20261125_080257)

**CHỈ PHÂN TÍCH — KHÔNG ghi sổ, KHÔNG merge, KHÔNG email, KHÔNG wire.** User chọn A/B và có ghi rev9 hay không.
Sổ hiện hành (master ff4e5c744): HHS rev8 tâm **10.805** (CK holding 26,63%); dải CK holding 0…+20% DISPLAY-ONLY (`kb/projects/ck-hhs-reference-range-20261124.md`).
Mù giá: không tính lại mô hình, không đọc giá mới. Mọi tâm đọc từ lưới đã khoá của đợt 3 `dd_recheck_20261125w3/HHS/calc/adj_run1.txt` (md5 `82f1f00451ea3595a5f15abc28d755ca`, sinh bởi `calc_adj_hhs.py`, chạy 2 lần trùng byte; CONTROL base 13.969 assert). Bảng dưới do `calc/ab_table.py` in ra (`calc/ab_table_out.txt`).

## 0. Kết luận

**Khuyến nghị: PHƯƠNG ÁN A (giữ biên quan sát 52,05%) và GHI rev9 — tâm base 13.969 (12.422–15.564), center_adj E17 11.593 (dải 11.593–13.969).** B giữ làm độ nhạy rủi ro hiển thị, không vào headline. Vì HHS đang bị `forensic_flags` EXCLUDE, chọn A hay B đều **không đổi hành động giao dịch**. Lựa chọn chỉ đổi số và nhãn hiển thị.

| Phương án | Biên HTK cũ | Tâm base (CK 0%) [P10–P90] | vs 10.805 | **center_adj E17 (CK +20%)** [P10–P90] | vs 10.805 | Dải adj | EX k=1 base / adj |
|---|---|---|---|---|---|---|---|
| **A** | s_obs 52,05% | **13.969** [12.422–15.564] | +29,3% | **11.593** [10.322–12.876] | +7,3% | 11.593–13.969 | 11.615 / 10.227 |
| **B1** (luật 3c, TB peer) | 37,7% | 12.357 [10.940–13.839] | +14,4% | 10.303 [9.121–11.553] | −4,6% | 10.303–12.357 | 10.673 / 9.473 |
| **B2** (luật 3c, TCH) | 29,9% | 11.774 [10.390–13.240] | +9,0% | 9.837 [8.701–11.078] | −9,0% | 9.837–11.774 | 10.333 / 9.201 |

B so A: base −11,54% (B1) / −15,71% (B2); adj −11,13% (B1) / −15,15% (B2). Đây là khoảng "−11…−16%" trong brief.
Nhãn (giá 9.700 BQ 20/11 kế thừa, gắn sau khoá): A base DƯỚI (P10 12.422), adj DƯỚI (P10 10.322) · B1 base DƯỚI (P10 10.940), luật 4 0,85×12.357 = 10.503 ĐẠT; adj TRONG (P10 9.121) · B2 adj TRONG (P10 8.701).

## 1. Dữ kiện dùng
**Biên A, 52,05% = bình quân hai số đo kế toán độc lập trên cùng dự án NC-II** (`dd_redo_20261105/HHS/REPORT_r3.md` §1 #2: s_obs = 0,8×(52,05%−10%)/(1−52,05%) = 0,7016):
- HHS hợp nhất Q3/2026, biên BĐS bỏ PPA 52,2% = (272,38 + 638,7)/1.746,23. Phần PPA qua giá vốn 638,7 tỷ được suy từ thu nhập thuế hoãn lại 127,74 tỷ với thuế suất 20%, nên đây là **ước lượng** (`dd_HHS_20261101/REPORT.md:149`, C7).
- Biên NC-II ở TCH 51,9% (`dd_HHS_20261101/REPORT.md:23`).
- Khối HTK cũ 6.009,8 tỷ chỉ còn NC-II, là đất mua theo giá gốc và đã bán trước 3.099,2 tỷ (`REPORT_r3.md` §1 #2; `ADDENDUM_5F_r1.md` §2).

**Peer cho B**: đo lại 25/11 từ BQ `tav2_bq.ticker_financial` (`GPM_P0`, dòng Q4 = cả năm, 2016Q4–2025Q4) → `calc/bq_gpm_q4_20261125.csv` (md5 `3ea3a44b…`), `calc/peer_gpm_recheck.py` → `calc/peer_gpm_recheck_out.txt` (md5 `e3a89cc4…`). File `5F/peer_stats_out.txt` của 07/11 không còn trong kho, nên phải đo lại; kết quả tái lập **khớp từng chữ số** với ADDENDUM_5F_r1 §2:
- 14 CĐT (VHM, NLG, KDH, DXG, PDR, DIG, HDG, HDC, NTL, CEO, SCR, NVL, KHG, AGG): TB-của-TB **37,7%**, trung vị **37,9%**, IQR **30,3–47,2%**. Biên từng mã chênh nhau rộng: SCR 16,2 · KHG 26,7 · DIG 27,3 … KDH 46,8 · HDG 48,3 · DXG 54,1 · PDR 55,3. NTL và SCR có năm âm (−35,9 / −33,5).
- TCH: TB **29,9%** (min 19,0, max 38,4, n = 10 năm). Đây là biên **toàn danh mục** TCH, không phải biên riêng NC-II.

## 2. Độ tin cậy từng phương án
| | Số có đúng không | Số có liên quan tới HTK còn lại không | Điểm yếu |
|---|---|---|---|
| **A** | TRUNG BÌNH. Ước lượng bỏ PPA dựa trên một giả định thuế; chỉ có 1 quý; BCTC Q3 chưa soát xét. Bù lại, hai nguồn kế toán độc lập trùng nhau (52,2 / 51,9). | **CAO.** Đo trên chính dự án; giá vốn đất là số đã chốt từ quá khứ, không phải giả định moat. | Phần còn lại của NC-II có thể bán ở giá khác phần đã bán. Chi phí hoàn thiện G10 chưa có số. Cơ cấu HH1–HH4 đã nằm trong trục ds. |
| **B1** | CAO. Tái lập chính xác từ BQ. | **THẤP.** Đây là hỗn hợp nhiều thế hệ quỹ đất với giá vốn khác nhau, phân tán rộng (IQR ~17pp), và 4/14 peer có biên ≥ 46,8%, gần mức A. | Ép một dự án có giá vốn đã biết về mức trung bình ngành. |
| **B2** | CAO. | **THẤP–TB.** TCH là đối thủ trực tiếp tại Hải Phòng, nhưng 29,9% là biên toàn danh mục, gồm cả dự án mua đất theo giá thị trường. | Như B1. Biên NC-II riêng của TCH (51,9%) lại ủng hộ A. |

## 3. Lý do khuyến nghị A
1. **Luật hiện hành không cho B vào headline.** Skill due-diligence (`SKILL.md:47`; `SKILL_ext.md` §E3, user chốt 08/11 10:50) quy định: moat NARROW/NONE thì *không thưởng, KHÔNG TRỪ ở giai đoạn dự báo: không ép biên/ROE về TB ngành*. Nếu thấy mô hình ngầm thưởng moat thì chỉ ghi rõ và báo độ nhạy, **không đổi headline**. Killer (2) của skeptic r1 đợt 3 và phần kết luận "luật 3c ⇒ biên về TB ngành" trong ADDENDUM_5F_r1 (07/11) đều đi theo cách đọc **trước** ngày 08/11. Áp B thì lại đúng vào phép trừ mà user đã bỏ.
2. **52% là dữ kiện đo được, không phải tham số moat.** HTK còn lại là đất NC-II mua theo giá gốc. Thặng dư đến từ giá vốn đã chốt và giá bán quan sát được trên cùng dự án. Luật 3c nhắm vào biên của tương lai hoặc dự án mới, mà I.14 đã đối xứng (kỳ vọng 0) từ r3.
3. **Peer phân tán quá rộng để làm neo.** Một con số TB 37,7% trên dải 16–55% cho cùng ngành không đủ đại diện cho một khối đất có giá vốn đã biết.
4. **Sổ đang mang một số không còn nhất quán.** 10.805 dựa trên CK holding 26,63% (N = 6). Số này đã bị phép đo v5 thay thế và nằm ngoài dải 0…+20% user chốt ngày 24/11. Giữ 10.805 nghĩa là sổ dùng một CK mà chính quyết định 24/11 không bao gồm. Ghi rev9 sẽ sửa điều đó, dù chọn A hay B.
5. Chống lật qua lại: r3 đã chuyển sang s_obs theo một skeptic trước. Lật ngược lần nữa mà không có dữ kiện mới thì lặp đúng vòng dao động mà lịch sử tâm HHS đã trải qua 6 lần.

**Điều kiện đảo khuyến nghị sang B:** BCTC năm 2026 (kiểm toán) của CRV hoặc HHS cho thấy biên NC-II bỏ PPA ≤ 40%, hoặc giá bán các đợt NC-II còn lại thấp rõ so với các đợt đã bán. Ngược lại, nếu BCTC xác nhận khoảng 52% thì độ tin của A tăng (bảng điều kiện trong `ADJ_CENTER.md` đợt 3).

## 4. Về center_adj
A: center_adj **11.593**, tức đổi nền CK về mốc **đo** hiện tại +20% (v5 19,7%, khoảng 15–23%); Σ p×m hạng mục = 0. Phương án thay thế nếu user coi đây là "đưa CK vào ledger" (trái chữ DISPLAY-ONLY): center_adj = 13.969 (= base). Tôi giữ khuyến nghị 11.593, vì file quyết định ghi 0% là "cận trên có lợi cho HHS, không phải tâm đo được". B1 tương ứng: center_adj 10.303, dải 10.303–12.357.

## 5. Artifact
- A: dùng nguyên `dd_recheck_20261125w3/HHS/LEDGER_PROPOSAL_HHS.json` (rev9) + `adj.json` (md5 `a6d09227…`). Không lập bản mới.
- B1: `LEDGER_PROPOSAL_HHS_B.json` + `adj_B.json` (thư mục này), chỉ dùng nếu user chọn B.
- Selfcheck sổ trên bản tạm (3 TZ): `selfcheck/` (§ SUMMARY).

*Phân tích, không phải khuyến nghị đầu tư. Pháp lý (tăng vốn 60%, NQ 10, TB 2124, KL 08) chỉ ở mức WARNING, giữ như rev9 §5.*
