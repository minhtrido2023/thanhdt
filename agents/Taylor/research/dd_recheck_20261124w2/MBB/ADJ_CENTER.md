# MBB — Tâm kỳ vọng điều chỉnh (E17, 24/11/2026, job Taylor_20261124_131354)

Phương pháp: `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`), `calc/calc_adj.py` assert cả hai. Chạy lại mô hình RI r3 (khôi phục `/tmp/ddrestore_MBB`, CONTROL 21.069) cho từng hạng mục và cho TỔ HỢP. Chạy 2 lần: `adj_run1.txt` = `adj_run2.txt` md5 `83d4bf15…`. MÙ GIÁ. Tâm gốc 21.069 (proposal rev4 = sổ rev3). `skeptic_final` REFUTED_OPEN = trạng thái phản biện, không phải quan điểm đầu tư.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 20.587 đ/cp (dải 19.245–21.061; −2,29% so với tâm base); căn cứ 3 hạng mục bậc B/C+.**
Tổ hợp chạy lại mô hình (Σ tuyến tính −2,24%, khớp). Không có quyền cổ tức tiền chưa GDKHQ trong nguồn đã đọc (payout 30% nằm trong RI).

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| 1 | Rò LN sang quỹ KTPL (clean-surplus): dư LNCPP 2.378 tỷ = 8,9% LN 2025; cận bảo thủ ½ = 4,45%/năm | ↓ | −5,89 [−11,58; −5,89] | C+ | 0,50 [0,25; 0,75] | −2,94 |
| 2 | Đường ROE 2027–29 +1,5/+1/+1pp (TTM 20,7%; ROE_T giữ 16%) | ↑ | +2,75 | B (Bneg: chi phí tín dụng Q3 1,65%, nhóm 2 +67%, bao phủ 84,7%) | 0,35 [0,15; 0,55] | +0,96 |
| 3 | Phát hành riêng lẻ 200 tr CP, giá BVPS…1,3×BVPS | ↓ | −0,51 [−0,51; −0,08] | B | 0,50 [0,25; 0,75] | −0,25 |
| | **Σ tuyến tính / tổ hợp** | | | | | **−2,24 / −2,29** |

Không đếm hai lần: xây lại bao phủ (−0,91%) đã nằm trong nhánh XẤU ⇒ chỉ độ nhạy; #2 chỉ dịch pha dự báo, ROE_T (tham số luật) không động.

## 2. Chỉ độ nhạy (C / LUẬT) — không vào tâm
| Hạng mục | Độ nhạy | Lý do |
|---|---|---|
| [LUẬT] chênh ROE_T−Ke vĩnh viễn trên sổ 2029 | ROE_T = Ke ⇒ 17.961 (−14,75%) | quy ước user 08/11 (NARROW không thưởng/không trừ) |
| [LUẬT] r 13,5% vs dải Ke (E15) | 12,3% ⇒ 23.659 (+12,30%) | V1 |
| Xây lại bao phủ 93,7% (1.940 tỷ DP) | 20.877 (−0,91%) | trùng nhánh XẤU |
| Nhu cầu vốn/CAR 30/09 | chưa định lượng | C thuần |
| Phải thu MBV 11.248 (bản E) | 20.983 (−0,41%) | C |
| Nghĩa vụ lỗ MBV ≥15.688 | CO_SO 18.969 | cờ HARD ABANDON |
| Pháp lý sau 05/11 | — | chỉ WARNING |

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
| Sự kiện | Khi nào | Đổi gì | Tâm adj |
|---|---|---|---|
| **NQ ĐHĐCĐ 2026 / thuyết minh VCSH: tỷ lệ trích KTPL thật từ LN 2025** | đọc được ngay (đã công bố 04/2026) | #1 C+→A, p 0,9 | k 4,45% ⇒ ≈20.102 (−2,36% so với tâm adj); k 0 ⇒ ≈21.218 (+3,06%); k 8,9% ⇒ ≈19.023 (−7,60%) (tuyến tính từ các case chạy mô hình) |
| BCTC Q4/26: ROE quý ≥20%, chi phí tín dụng ≤1,46% | ≤ cuối 01/2027 | #2 p 0,35→0,65 | +0,8% |
| BCTC Q4/26: nhóm 2 HN >20.000 hoặc bao phủ <75% | ≤ cuối 01/2027 | trọng số 0,35/0,45/0,20 (−3,1%), #2 p→0,15 | ≈ −3,7% |
| CBTT giá phát hành riêng lẻ | khi có | #3 B→A | −0,08…−0,51% |
| CAR 30/09 + kế hoạch tăng vốn 2027 | ĐHĐCĐ 2027 | C→B | theo số |
| Lãi huy động 12T ±50bp | liên tục | r (V1) | −4,47% / +4,83% |
| Văn bản nghĩa vụ MBV ≥15.688 | khi có | HARD ABANDON | CO_SO 18.969 |

**Điều kiện đổi số quan trọng nhất:** tỷ lệ trích KTPL thật của MBB (NQ ĐHĐCĐ 2026) — hạng mục C+ lớn nhất, đọc được ngay, quyết định tâm adj trong khoảng ≈19.000–21.200.
