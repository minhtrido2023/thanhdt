# DD REDO VÒNG 2 — MBB · 05/11/2026 · job `Taylor_20261105_020013`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị. Áp `STANDARD_r2.md` (12 điều). Mô hình RI (kịch bản, BCTC gốc HN-Q3) **chép nguyên** vòng 1 (`calc/mbb_redo.py` dòng 2–57); vòng 2 chỉ đổi tầng lưới/kết cục/thanh khoản/báo cáo.
> **Tái lập:** `$DNA_PYEXE -I calc/mbb_r2.py > calc/mbb_r2_out.txt` — chạy 2 lần, md5 4 file đầu ra trùng byte (`calc/LOCK_r2_outputs_md5.txt`). Mọi số dưới đây lấy từ `calc/mbb_r2_out.txt` / `SUMMARY.json` (vòng 1 backup: `SUMMARY_r1.json`, `REPORT.md`).
> Bối cảnh ngân hàng, giả thuyết, chất lượng tài sản: giữ nguyên `REPORT.md` §2–§4 (không có BCTC mới sau Q3).

## 1. Kết luận

| Chỉ số (sau CK thanh khoản @5 tỷ) | Vòng 2 | Vòng 1 |
|---|---|---|
| Giá 04/11/2026 [BQ `tav2_bq.ticker`] | **19.250** | 19.250 |
| r | 13,50% (neo 13,5% @ lãi huy động 12T 7,40% `cctg_12m(2026-11-02)`) | 13,50% |
| **Tâm** = kỳ vọng trọng số lưới kết cục | **23.804** | 23.494 |
| P10 / P50 / P90 (mức kết cục, `_shared/wpct.py`) | **14.444 / 22.765 / 35.860** | 14.456 / 23.214 / 36.126 |
| n kết cục · % trọng số dưới giá · min kết cục | **180 · 32,3% · 11.194** | 45 · — · — |
| Giá vs tâm | **−19,1%** | −18,1% |
| **Nhãn** | **TRONG vùng** (P10–P90 mức kết cục; CK ở cỡ 5 tỷ) | TRONG vùng |

Nhãn không đổi; vùng định nghĩa không đổi (P10–P90) ⇒ không có đổi nhãn do đổi định nghĩa (điều 7).

## 2. Ba con số tách bạch (điều 4)
- **Tâm** (kỳ vọng lưới) **23.804**; **P50** **22.765**; **giá trị tại tham số trung tâm** (CƠ SỞ, ΔROE 0, Δg 0, MBV NPV 0) **24.068**.
- Tâm > P50 vì phân phối lệch phải: terminal RI lồi theo g và ROE (ô ΔROE +3pp × Δg +1pp kịch bản TỐT lên tới 51.815). Phần lồi này làm tâm lưới (bỏ trục MBV) = 24.082 cao hơn kỳ vọng kịch bản tại tham số trung tâm của vòng 1 (23.494) — chênh do lồi, không do thay giả định.
- **P10 do nhánh XẤU quyết định** (kết cục quanh P10 ±5%: 87,5% trọng số từ XẤU, 12,5% CƠ SỞ); **P90 do CƠ SỞ 53,5% / TỐT 46,5%**.

## 3. Lưới kết cục (điều 1, 2)
Mỗi ô tất định (không có xác suất kết cục con bên trong ô) ⇒ kết cục = ô; trọng số = tích trọng số các trục. n = 3 × 5 × 3 × 4 = **180**. File: `calc/grid_mbb_r2.csv`.

| Trục | Điểm (trọng số) | Chiều |
|---|---|---|
| Kịch bản | XẤU 0,35 / CƠ SỞ 0,45 / TỐT 0,20 (DD 31/10, skeptic CONFIRMED) | hai chiều |
| ΔROE 2027–29 + terminal | −3 / −1,5 / 0 / +1,5 / +3 pp (đều) | hai chiều |
| Δg terminal | −1 / 0 / +1 pp (đều) | hai chiều |
| **MBV (MỚI vòng 2)** | −3.500 tỷ (ưu đãi lợi, LÊN) 0,15 / 0 (NPV 0) 0,50 / +3.500 (mất trắng góp) 0,25 / +15.688 (bù lỗ luỹ kế 2024) 0,10 — trừ vào VCSH cuối 2026 **[UL]** | hai chiều, lệch xuống |

Trục bị loại (có lý do) + bản song song:

| Bản | n | Tâm | P10 | P50 | P90 | % dưới giá |
|---|---|---|---|---|---|---|
| **Chính** (có MBV) | 180 | 23.804 | 14.444 | 22.765 | 35.860 | 32,3% |
| Không trục MBV (= vòng 1 tính lại theo kết cục) | 45 | 24.082 | 14.456 | 23.214 | 36.126 | 30,0% |
| Thêm trục r 12,5/13,5/14,5% (0,25/0,5/0,25 [UL]) | 540 | 24.154 | 14.147 | 22.704 | 36.748 | 34,9% |

- **r**: loại khỏi lưới chính vì luật 03/11 neo r vào lãi huy động (không phải bất định riêng của công ty); bản có trục r ở trên — nhãn không đổi.
- **Ưu đãi MBV** (trần tín dụng 35%/năm × 4, room ngoại 49% theo NĐ 69/2025 [WEB]): không có dữ liệu tách ⇒ nằm trong điểm −3.500 của trục MBV và trục ΔROE.
- Vòng 1 để MBV làm độ nhạy ngoài lưới — đó là trục chỉ lệch xuống bị loại ⇒ vi phạm điều 2; vòng 2 đưa vào. Tác động lên tâm: −278 đ/cp (23.804 vs 24.082).

## 4. Base so với sổ sách (điều 3)
- **MBV ở base = 0 (NPV 0, giá sổ)**. Cơ sở dữ liệu: BCTC HN-Q3 thuyết minh tr.2 (PDF p9) — MB chưa góp vốn MBV tại 30/09/2026, không hợp nhất. Mọi lệch khỏi NPV 0 chỉ nằm ở trục có xác suất (§3), không ở tham số trung tâm.
- Không có khoản trừ nào khác trong base (không haircut khoản vay, không CK quản trị).

## 5. Thanh khoản (điều 6)
| | ADV 250 phiên | ADV 60 phiên |
|---|---|---|
| ADV trung vị (Price × Volume) | 353,7 tỷ | 210,5 tỷ |
| CK @ **5 tỷ** (tham chiếu, Y=1) | **0,192%** | 0,192% (σ 60 phiên thấp hơn bù ADV thấp hơn) |
| CK @ sleeve thật 10 / 40 triệu (NAV SpaceX ≈ 0,94 tỷ) | 0,0086% / 0,0172% | — |

5 tỷ = 1,41% ADV250 — trong vùng hiệu chỉnh luật căn bậc hai (ước lượng ~0,1–20% ADV). Cỡ sleeve 10–40 triệu = 0,003–0,011% ADV — **dưới vùng hiệu chỉnh**; CK thật ở cỡ này chủ yếu là nửa spread (chưa đo). Nhãn tính ở cỡ 5 tỷ.

## 6. Đối chiếu (không vào tâm) (điều 10)
- Gordon P/B (BVPS 30/09 15.594): ROE TTM 20,7% ⇒ 30.624 (g 6%) / 32.936 (g 7%); ROE terminal cơ sở 16% ⇒ 20.793 / 21.592. Ngân hàng: lãi tiền gửi/cho vay là nghiệp vụ lõi ⇒ không có biến thể "bỏ lãi tiền gửi".
- RI tại tham số trung tâm ở Ke 14,5% = 20.223; **Ke 15% = 18.933** (trước CK). Skeptic 31/10 ghi "~20,5k @15%", vòng 1 ghi "≈18,7k (DD cũ)" — số đo lại hôm nay ở mô hình hiện hành là 18.933; con số 20,5k của skeptic không tái lập được bằng mô hình này (có thể đo trên blend cũ — chưa kiểm). Kết luận giữ: ở Ke ngụ ý ~15% giá ≈ giá trị ⇒ phần "dưới tâm 19%" chủ yếu là khoảng cách khung r 13,5% vs Ke thị trường cho cả ngành.
- Q4/26: LNTT ngụ ý XẤU 8.500 / CƠ SỞ 12.000 / TỐT 14.500. Cơ sở 12.000 vs Q4/25 (≈10.950 LNTT, ước lượng từ LNST 8.762,6/0,8) — nhận xét skeptic "cả 3 kịch bản thấp so đà 9T +32%" vẫn đúng một phần cho XẤU; giữ vì nhóm 2 Q3 +42% QoQ.

## 7. Tham số tự đặt [UL] (điều 3)
Trọng số kịch bản 0,35/0,45/0,20; đường ROE/ROE_T/g_T từng kịch bản; PPOP/DP Q4; biên trục ΔROE ±3pp, Δg ±1pp, trọng số đều; **trục MBV: điểm −3.500/0/+3.500/+15.688 và trọng số 0,15/0,50/0,25/0,10**; trục r ±1pp trọng số 0,25/0,5/0,25 (bản song song); payout 30%; thuế 20%; NCI 2,5%; free float 60%; Y = 1.

## 8. Mốc đổi nhận định HAI chiều + HARD ABANDON (điều 8)
Bộ M1–M8 khoá ngày 31/10 giữ nguyên (chấm 15/02/2027 bằng BCTC Q4/26; xem `REPORT.md` §7).
- **Xấu đi** (⇒ w 0,45/0,35/0,20, tâm trước CK 22.837 vòng 1): nhóm 2 HN Q4 > 20.000 hoặc nhóm 2–5 > 3,5%; bao phủ < 75%; Tier1 riêng lẻ < 8,5%; NIM Q4 bỏ TG NHNN < 3,85%; MB phải hỗ trợ/trích lập MBV > 5.000 tỷ; lãi huy động 12T +100bp.
- **Tốt lên** (⇒ w 0,25/0,40/0,35, tâm 25.653 vòng 1): nhóm 2 HN < 13.000 và bao phủ ≥ 90%; KKH tăng lại; phát hành riêng lẻ ở P/B ≥ 1,3x; LNTT Q4 ≥ 14.000 với DP ≥ 5.000; lãi huy động −100bp.
- **HARD ABANDON** (bỏ hồ sơ, dựng lại từ đầu): CAR HN < 9% hoặc NHNN yêu cầu tăng vốn bắt buộc; nhóm 3–5 > 3%; công bố MB gánh lỗ MBV > 15.688 tỷ (vượt điểm xấu nhất của trục); kết luận thanh tra/khởi tố liên quan tín dụng BĐS hoặc bên liên quan.
- Ngưỡng nhãn: DƯỚI vùng nếu giá < 14.444; TRÊN vùng nếu > 35.860.
- **Không đủ điều kiện sleeve fear-buy §2.5**: không có trạng thái sợ hãi/cú sốc đặc thù (giá P/B 1,23x, không scandal); nhãn chỉ là định giá.

## 9. WARNING pháp lý / quản trị — đầy đủ (điều 5)
Nguồn rà: `dd_MBB_20261031/SKEPTIC_20261031.md`, `REPORT.md`, `REPORT_v1.md`, `dd_redo_20261105/MBB/REPORT.md`.
1. **MBV (OceanBank cũ)** — ngoài bảng (điểm c k.1 Đ.185 Luật TCTD 2024); QĐ góp 3.500 ngày 01/10/2026 [WEB, thứ cấp]; phải thu bán nợ từ MBV 11.248 (31/12/25) [BCTN25]; lỗ luỹ kế 15.688 (2024) [WEB]. Nay là trục lưới (§3). MỞ.
2. Ưu đãi MBV (trần tín dụng, room ngoại 49%, NĐ 69/2025) [WEB] — chưa kiểm văn bản gốc. MỞ.
3. Nợ ngoại bảng, nợ cơ cấu TT02, Pillar 3 — chưa kiểm. MỞ.
4. Cho vay bên liên quan, top-10/20 khách hàng, TPDN BĐS nắm giữ, phân rã chủ đầu tư vs người mua nhà — chưa kiểm; dư nợ KD BĐS +48,3% YTD. MỞ.
5. CAR/CET1/Tier1 30/09 chưa có số gốc; **Tier1 9,02% là số 30/06, trước khi nhận ~8k quyền mua, và Tier1 ≠ CET1**. MỞ.
6. Cổ đông tổ chức Viettel/SCIC/Trực thăng/Tân Cảng (số 2024–25) — có thể có sở hữu chéo, chưa kiểm. MỞ.
7. Phát hành 2026 (200 triệu CP riêng lẻ, cổ tức CP, quyền mua): tách 15% + 10% chỉ từ WEB, BCTC tr.36 chỉ cho tổng +20.137,5; **nghị quyết ĐHĐCĐ/HĐQT gốc chưa đọc** ⇒ chưa đưa được vào mô hình (pha loãng ở giá riêng lẻ chưa biết; M8 theo dõi). MỞ.
8. Lỗ phái sinh −1.066 (swap tài trợ ngoại tệ) là suy luận, chưa có thuyết minh. MỞ.
9. Quota tín dụng NHNN 2026, CASA chuẩn Q3, MCredit 9T — chưa kiểm. MỞ.
10. Kiểm toán KPMG 2025 chấp nhận toàn phần, soát xét 6T không ngoại trừ (chỉ đọc trang ý kiến). Hạ cấp.
11. **"Chưa thấy xử phạt/khởi tố 2025–26"**: nguồn = web search của DD 31/10/2026 (`dd_MBB_20261031/REPORT.md`); **chưa quét lại 01–05/11/2026, chưa tra trực tiếp ssc.gov.vn / sbv.gov.vn**. Tìm không thấy ≠ không có.

## 10. LOCK md5 (điều 9) — mọi file script thực thi hoặc đọc
`calc/mbb_r2_out.txt` dòng `LOCK …`: `MBB/calc/mbb_r2.py`, `MBB/calc/mbb_redo.py` (nguồn phần mô hình), `_common_014125/common.py`, `_common_014125/r2common.py`, `_common_014125/bq_px_liq_20261104.csv`, `_shared/wpct.py`, `WorkingClaude/deposit_rate_vn.py`, `WorkingClaude/cctg_rate_vn.py`, `data/deposit_rate_vn_events.csv`, `data/cctg_rate_vn_events.csv`, `mike/kb/dd_price_zones.json` (chỉ đọc vùng cũ). Đầu ra: `calc/LOCK_r2_outputs_md5.txt`.

## 11. Thay đổi so vòng 1 và lý do
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| Phân vị | `common.wq` trên 45 ô | `_shared/wpct.py` trên 180 kết cục | điều 1 |
| MBV | độ nhạy ngoài lưới | trục 4 điểm có trọng số | điều 2 (trục lệch xuống không được loại) |
| Tâm | 23.494 (kỳ vọng kịch bản @ tham số trung tâm) | 23.804 (kỳ vọng lưới) | điều 4: định nghĩa tâm = kỳ vọng lưới; +588 do lồi terminal, −278 do MBV |
| P10/P50/P90 | 14.456/23.214/36.126 | 14.444/22.765/35.860 | trục MBV |
| Thanh khoản | ADV250, 1/5/10 tỷ | + ADV60, + sleeve 10/40 triệu, ghi vùng hiệu chỉnh | điều 6 |
| Nhãn | TRONG vùng | TRONG vùng | không đổi |

Chưa qua fundamental-skeptic vòng 2 (Mike chạy). Không sửa `kb/dd_price_zones.json`, không PDF/email.
