# DD REDO — FPT (CTCP FPT) · mùa BCTC Q3/2026 · 05/11/2026 · job `Taylor_20261105_014125`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị.
> **Nguồn:** BCTC GỐC hợp nhất + riêng Q3/2026 (fpt.com 28/10, đã có ở `dd_FPT_20261101/src/`, KHÔNG tải lại); số chép đã qua fundamental-skeptic (REFUTED mức văn bản → v2 áp đủ; số BCTC đúng) — `dd_FPT_20261101/REPORT.md`, `calc/notes_q3_bctc.md`.
> Sector read Bobby (mù): `kb/data_registry/market-state/sector_read_cntt_vienthong_giaoduc_vn_20261101.md`.
> **Tính lại:** `$DNA_PYEXE -I calc/fpt_redo.py > calc/fpt_redo_out.txt`. FOX/FRT thị giá 04/11: `calc/assoc_px_20261104.csv` (BQ). Mọi số §1, §6–§8 từ `calc/fpt_redo_out.txt` / `SUMMARY.json`.
> ⚠️ Phạm vi hợp nhất đổi từ 01/01/2026: FTEL (FOX, 45,66%) theo vốn chủ sở hữu (CV 1906, Bộ Công an) — so cùng kỳ dùng số FPT tự điều chỉnh.

## 1. Kết luận (số chuẩn hoá liên mã)

| Chỉ số | Giá trị |
|---|---|
| Giá 04/11/2026 [BQ] | **53.900** (còn quyền cổ tức tiền 1.000đ, chốt 30/11) |
| r | **13,50%** (neo 13,5% @ 7,40% `cctg_12m(2026-11-02)`; 04/11 không đổi) — MỘT r cho mọi kịch bản |
| Tâm TRƯỚC / SAU CK thanh khoản | 52.281 / **52.183** |
| P10 / P50 / P90 SAU CK | **30.520 / 53.699 / 72.235** (trước: 30.577 / 53.800 / 72.370) |
| Giá vs tâm / P10 / P90 | **+3,3%** / +76,6% / −25,4% |
| **Nhãn** | **TRONG vùng** (sát tâm) |

Một câu: lãi tăng thật (+13,3% 9T) và tiền ròng 12.233 tỷ là thật, nhưng tiền 9T chưa về (conv −0,12) và xuất khẩu Q3 chậm. Giá ≈ kỳ vọng có trọng số. Phần "rẻ" chỉ hiện ra nếu CFO Q4/26 kéo conv về ≥0,6.

## 2. Giả thuyết kiểm chứng (BCTC gốc; không đổi vì chưa có BCTC mới)

| Giả thuyết | Số | Kết quả |
|---|---|---|
| "LN tăng trưởng hai chữ số bền" | LNST mẹ 9T 7.778 (+13,3%), Q3 2.723 (+11,8%); bỏ lãi liên kết LNST 9T chỉ **+5,2%** (thuế hiệu dụng 11,1% → 15,2%); liên kết = 52% mức tăng LNTT | NỬA ĐÚNG |
| "Xuất khẩu vẫn tăng tốc" | DT CNTT nước ngoài Q3 +8,2% (6T +13,4%); ký mới NN Q3 **+3,6%** (6T +32,3%); hợp đồng >1 triệu USD 9T +29,4% | SAI ở Q3, chiều ngược có thật |
| "Lãi thành tiền" | conv 9T/26 **−0,12** (9T/25 0,34; FY25 0,60; FY24 1,07); CFO Q3 2.097 < ngưỡng PREREG 2.600 | CHƯA |

## 3. Chất lượng LN · bảng cân đối · ghi nhận DT
- **Tiền ròng THẬT 30/09:** tiền 7.377 + HTM 21.452 − vay 16.597 = **12.233 tỷ (6.487 đ/cp)**, chưa trừ cổ tức 1.000đ (giá còn quyền). Tiền khách ứng trước (học phí 1.609 + người mua trả trước 761 = 2.370) là float theo mùa — không trừ ở tâm.
- **Vốn lưu động:** phải thu khách hàng đi ngang (10.851 → 10.847); **chi phí SXKD dở dang 1.021 → 1.811 (+782)** = tiền kẹt chờ nghiệm thu (không phồng LN). DSO (định nghĩa PREREG) 86,5 ngày.
- **Ghi nhận DT:** dự án theo nghiệm thu/tiến độ; mã 134 (phải thu theo tiến độ) đi ngang 302 → 280. Q4 lịch sử là quý thu tiền chính (tử số conv Q4/25 ≈ 3.329).
- **Capex 9T 2.029**, 56% ở khối GD (khuôn viên Bình Dương 415, Hoà Lạc 247, Quy Nhơn 61, Long An 37 dở dang).
- Chi tiết + trang: `dd_FPT_20261101/REPORT.md` §3–§5.

## 4. Cổ đông · room · thanh khoản
- Trương Gia Bình 6,89% · SCIC 5,67% · PYN 3,67% · Bùi Quang Ngọc 1,76% · Trương Thị Thanh Thanh 1,48% [BCTN25] ⇒ free float ~80% (ước lượng). Sở hữu NN 28,6%/trần 49%. ESOP 10,82 triệu cp đã phát hành 26/06 (không pha loãng sắp tới).
- **Thanh khoản [BQ 250 phiên tới 04/11]:** ADV trung vị **566,1 tỷ**; σ ngày 1,99%; Amihud 1,92e−05. Vị thế 5 tỷ thoát 0,09 phiên (10%) / 0,04 (20%). **CK @5 tỷ = 0,19%** (1 tỷ 0,08%; 10 tỷ 0,26%). Cùng phương pháp liên mã (`_common_014125/common.py`).

## 5. Pháp lý / quản trị — WARNING (THẤP–TRUNG BÌNH, không loại)
- PwC soát xét 6T/2026 chấp nhận toàn phần. Phạt thuế 0,244 tỷ đã nộp (không trọng yếu).
- **WARNING FTEL:** Nhà nước (Bộ Công an) nắm ~50,16% FTEL; FPT không còn kiểm soát ⇒ cổ tức/tăng vốn FTEL do bên khác quyết; free float FOX ≤ ~4,2% (rủi ro tư cách đại chúng). Định giá phần FTEL: thị giá 04/11 (55.700 × 738,8 triệu cp × 45,66% = **18.789 tỷ, 9.964 đ/cp**) trừ chiết khấu 30/15/0% theo kịch bản.
- **Câu hỏi mở:** "chi phí phát triển khách hàng" 618,8 tỷ chưa thuyết minh (có từ 30/06; không phải nguyên nhân CFO Q3 yếu).

## 6. Định giá
### 6.1 Mô hình (SOTP)
Giá trị = DCF FCFE lõi vận hành (LN lõi TTM **6.705 tỷ**, ước lượng) + FTEL thị giá × (1 − CK) + FRT thị giá 04/11 × 0,8 (11.984 tỷ trước CK) + liên kết khác theo sổ 1.500 (ước lượng) + TPBank/FPTS giá gốc 945 + **XDCB dở dang khuôn viên GD 760 theo giá sổ (NPV 0 — luật dự án mới; +403 đ/cp)** + tiền ròng 12.233. Thị trường đang trả cho lõi **8,3x** LN.
**r = 13,50% cho mọi kịch bản** (bản cũ: Ke 13,4/12,85/12,3% gắn theo kịch bản). Kịch bản giữ nguyên 01/11 — toàn bộ **(ước lượng)**:

| | XẤU (w 0,35) | CƠ SỞ (w 0,45) | TỐT (w 0,20) |
|---|---|---|---|
| Tăng LN lõi 5 năm / conv / g dài hạn | 3% / **0,40** / 3,0% | 9% / 0,75 / 4,0% | 14% / 0,85 / 4,0% |
| CK FTEL | 30% | 15% | 0% |
| **FV @13,5%** | **34.198** (TV 62%) | **57.418** (TV 67%) | **72.370** (TV 69%) |

Cơ sở dữ liệu của kịch bản XẤU (vì nó là "đầu tư không sinh lời" — luật 03/11 đòi nguồn): conv quan sát 9T/26 −0,12, FY25 0,60, FY24 1,07 [BCTN25 tr.168/170; Q3HN p10]; ký mới NN Q3 +3,6% [KQKD9T]. Không có trong base.
Kỳ vọng **52.281** trước CK ⇒ **52.183** sau CK. Độ nhạy trọng số: (0,45/0,40/0,15) 49.211; (0,25/0,45/0,30) 56.098.

### 6.2 Lưới P10–P90
n = 45 = 3 kịch bản (w 0,35/0,45/0,20) × dịch conv **−0,20/−0,10/0/+0,10/+0,20** (sàn 0,10) × dịch g dài hạn **−1/0/+1 pp** (đều); r cố định 13,5%. File ô `calc/grid_fpt.csv`. Conv là biến số trọng yếu nhất (dải quan sát 2024–26: −0,12…1,07).

| | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| TRƯỚC CK | 30.577 | — | 53.800 | — | 72.370 |
| SAU CK | **30.520** | 37.882 | **53.699** | 63.906 | **72.235** |

### 6.3 Độ nhạy r theo lãi huy động 12T (trước CK, kỳ vọng trọng số)

| Δ lãi huy động | β = 0,5 | β = 1,0 |
|---|---|---|
| −100bp | 13,00% → 54.019 (+1.739; +3,3%) | 12,50% → **55.961 (+3.680; +7,0%)** |
| −50bp | 13,25% → 53.127 (+846; +1,6%) | 13,00% → 54.019 (+1.739; +3,3%) |
| +50bp | 13,75% → 51.478 (−803; −1,5%) | 14,00% → 50.715 (−1.566; −3,0%) |
| +100bp | 14,00% → 50.715 (−1.566; −3,0%) | 14,50% → **49.297 (−2.984; −5,7%)** |

Độ nhạy thấp hơn MBB vì **21.740 đ/cp** (kịch bản cơ sở: tiền ròng + FTEL/FRT thị giá sau CK + liên kết khác + XDCB) không phụ thuộc r.

### 6.4 Đối chiếu (không vào tâm)
PE TTM ~9,7 (thấp nhất ~8 năm; p10 10 năm 10,5 [BQ weekly, DD cũ]); comp CMG 10,9, ELC 9,3, FOX 10,9 [BQ 30/10]. SOTP PE lõi 8–12x cho 48–66k (DD cũ).

## 7. Mốc khoá trước + điều kiện đổi nhận định (HAI chiều)
Giữ nguyên bảng mốc DD 01/11 §10:
- **BCTC Q4/2026 (cuối 01/2027)** — mốc quyết định. **Nâng:** CFO cả năm ≥ 6.000 tỷ (conv ≥ 0,6) và dở dang < 1.200 ⇒ chuyển xác suất XẤU → CƠ SỞ (w 0,25/0,45/0,30 ⇒ tâm trước CK 56.098). **Hạ:** CFO cả năm < 3.400 (conv < 0,2) hoặc dở dang + phải thu tiếp tục tăng ⇒ XẤU thành trung tâm (w 0,45/0,40/0,15 ⇒ 49.211; nếu XẤU là trung tâm thật ~34k).
- KQKD tháng 10–11: ký mới NN luỹ kế ≥ +20% và ≥ 2 hợp đồng >10 triệu USD (nâng) / < +15% (hạ).
- Nhật theo JPY cả năm < +15% (hạ; Q3 đã ~+15,3%); Mỹ ≥ +10%, APAC hết âm (nâng).
- FTEL: cổ tức FTEL 2026 ≥ 2.000 đ/cp (nâng) / tăng vốn-pha loãng FTEL, FOX mất tư cách đại chúng (hạ).
- Lãi huy động 12T hiệu dụng ±100bp: ∓2.984 / +3.680 đ/cp (β 1).
- Nhãn đổi sang DƯỚI vùng nếu giá < 30.520; TRÊN vùng nếu > 72.235.

## 8. Phụ lục — ĐỔI gì so với DD cũ (01/11) và vì sao

| Mục | Cũ (01/11) | Mới (05/11) | Lý do |
|---|---|---|---|
| Ke / r | 13,4% / 12,85% / 12,3% theo kịch bản | **13,50%** mọi kịch bản | luật 03/11 (r gắn lãi huy động); kịch bản không được tự hạ Ke |
| FTEL/FRT | thị giá 30/10 (FOX 55.400; FRT 148.700) | thị giá 04/11 (55.700; 144.000) | giá mới |
| XDCB dở dang GD | không tính riêng | +760 tỷ theo giá sổ (NPV 0) | luật dự án mới |
| Tâm | 54.800 (kỳ vọng; giá 52.700) | **52.183** sau CK | cầu nối: 54.800 → LK 04/11 −161, XDCB +403 ⇒ 55.042 → r 13,5% **−2.761** (chủ yếu TỐT mất Ke 12,3%) ⇒ 52.281 → CK −98 ⇒ 52.183. **Lệch −4,8% (< 10%)** |
| Vùng | 55,0–66,7k = 1 trục g × Ke của kịch bản CƠ SỞ | P10–P90 lưới n=45: 30.520–72.235 | định nghĩa chuẩn hoá liên mã (có trục conv + kịch bản) |
| Nhãn | DƯỚI vùng cơ sở (giá 52.700) | TRONG vùng, +3,3% vs tâm (giá 53.900) | đổi định nghĩa vùng; tâm cũ/mới đều ≈ giá |
| CK thanh khoản | không định lượng | 0,19% @5 tỷ | luật 03/11 |

## 9. Lỗ hổng mở
Lãi liên kết không tách theo công ty, Q4/25 lãi LK 600 tỷ (ước lượng); conv 2021–23 chưa đo cùng định nghĩa; liên kết khác theo sổ 1.500 (ước lượng); XDCB chỉ 4 khuôn viên đã liệt kê (có thể trùng một phần với g1); chưa quét tin 02–04/11/2026; BC quản trị 6T chưa đọc. Chưa qua fundamental-skeptic vòng này.
