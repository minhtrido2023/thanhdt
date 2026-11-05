# DRI — DD redo mùa BCTC Q3/2026 (05/11/2026, job Taylor_20261105_014135)

**Kết luận (số từ `calc/dri_redo_out.txt`):** tâm (kỳ vọng trọng số 2 kịch bản) **14.329 đ/cp SAU chiết khấu thanh khoản** (14.621 trước; CK 2,00% cho 5 tỷ). Lưới chuẩn hoá 18 ô có trọng số: **P10 11.255 · P50 14.296 · P90 17.422** sau CK (trước: 11.485 / 14.587 / 17.777). Giá **04/11/2026 = 13.500** ⇒ −5,8% so tâm, +19,9% so P10, −22,5% so P90 ⇒ **TRONG vùng, dưới tâm nhẹ** (43,8% trọng số lưới < giá). Tâm gần như không đổi so với sổ mức giá 03/11 (14.360, −0,2%).

Nguồn: BCTC HN Q3/2026 (ký 22/10/2026, dri.com.vn; trích `dd_DRI_20261027/extract_q3_bctc.md`) — đã có, không tải lại; BCTC HN bán niên soát xét (AFC) + CV 52/CV-CT; SXKD 9T (29/BC-CT, 20/10). Engine `dri_val_supply_adj_r4_20261027/model.py` exec nguyên văn (md5 `calc/LOCK_upstream_md5.txt` khớp `r5/calc/LOCK_md5_r5.txt`), dữ liệu snapshot 03/11 (RSS3 World Bank, CPI-U FRED, USD/VND). Sector read: `kb/data_registry/market-state/vn_sector_read_rubber_20261027.md` (Bobby, mù). Số BCTC dưới đây chép từ `REPORT_Q3_UPDATE.md` / `investor_report_v4` (đã qua skeptic R4) — không đọc lại PDF.

## 1. Giả thuyết
"Vườn cao su Lào + tiền ròng lớn; giá trị bền ngay cả khi giá cao su về giữa chu kỳ" — **nửa đúng**: ở mid thực 2,22 $/kg (Q3/26 2,753 = phân vị 89% chuỗi thực 2014–26, +24% so mid), base NPV0 = 15.860 trước CK; nhưng nếu tái canh bị buộc với kinh tế thận trọng (20%, nhận định) ⇒ 11.924.

## 2. Chất lượng lợi nhuận
| tỷ đ (BCTC HN) | Q3/26 | Q3/25 | 9T/26 | 9T/25 |
|---|---|---|---|---|
| Doanh thu | 136,00 | 184,12 | 622,00 | 487,59 |
| Biên gộp | 34,2% | 35,5% | 39,3% | 37,9% |
| LNST mẹ | 25,98 | 38,98 | 167,75 | 116,80 |
- Q3 yếu do **sản lượng bán** (2.369 t, −44% YoY) chứ không do giá (55,75 tr/t, +29%): chế biến 4.086 t ⇒ tồn thêm ~1.717 t (ước lượng; thành phẩm 64,99 → 138,81 tỷ). Mưa: khai thác T8 đạt 71,7% KH.
- Điều chỉnh soát xét H1: LNST −4,50 tỷ (giá vốn giao dịch nội bộ). CFO 9T 125,3 tỷ = 0,75× LNST; thưởng 2026 chưa trích (rủi ro Q4).

## 3. Bảng cân đối / net cash thật (30/09/2026)
Tiền 72,57 + tiền gửi có kỳ hạn 271,81 = 344,4 tỷ; vay 107,64; cổ tức phải trả 73,92 (chi từ 20/10). ~197 tỷ tiền nằm tại Lào — engine giữ lại 15% tiền Lào + khấu trừ thuế chuyển lợi nhuận, quỹ dự phòng. XDCB dở dang 72,71 tỷ (tái canh, sầu riêng) **theo giá vốn (NPV 0)** = 993 đ/cp. Vườn cây nguyên giá 567,43 / còn lại 250,74 tỷ.

## 4. Ghi nhận doanh thu
Bán mủ theo giao hàng (không POC). Q4 là quý bán hàng; kế hoạch công ty bán 4.168 t Q4 (giải phóng tồn kho).

## 5. Cổ đông / thanh khoản
- Dakruco ~45%; free float ~55%. Đang phấn đấu chuyển HOSE Q4/2026 (chưa chấp thuận).
- Thanh khoản (BQ `tav2_bq.ticker`, 250 phiên 03/11/2025–04/11/2026): ADV trung vị **8,33 tỷ** (60 phiên 13,82), σ 2,58%. Thoát 5 tỷ: 6 / 3 phiên ở 10% / 20% ADV. CK (hệ số 0,5/1,0/1,5): 1 tỷ 0,4/0,9/1,3% · **5 tỷ 1,0/2,0/3,0%** · 10 tỷ 1,4/2,8/4,2%.

## 6. Pháp lý / quản trị — WARNING (không loại, không vào base)
- Cho Dakruco vay còn 40 tỷ (TSĐB 6 tr cp DRI). **Mới (crisis-DD ngày 4, 05/11):** NQ HĐQT 15 nghiên cứu mua Dakruwood từ Dakruco — giao dịch bên liên quan, HĐQT xét 12/2026.
- Tiền gửi Quỹ TDND Cao su Đắk Lắk 70 tỷ + góp vốn 3 tỷ (soát xét chưa xác định giá trị thu hồi khoản góp).
- ~197 tỷ tại Lào không thuyết minh nguyên tệ/lãi suất/kỳ hạn; văn bản tô nhượng chưa công khai; một phần đất thuộc quy hoạch rừng bảo tồn Đông Huê Sáo.

## 7. Định giá
**Khung.** Dòng tiền chủ sở hữu tới 2054 theo lớp tuổi vườn (L đời cạo, giả định), giá RSS3 2027–28 hội tụ về mid thực rồi giữ; trừ thuế Lào, WHT, quỹ dự phòng, giữ 15% tiền Lào; tái canh/dự án mới **NPV 0** (luật 03/11); XDCB theo giá vốn. Không terminal.

**r.** `deposit_rate_vn` asof 04/11 = **7,40%** (cctg_12m 02/11) = điểm neo ⇒ **r 13,5%**. Ke nội địa, không CRP. Dòng tiền có thời hạn ⇒ độ nhạy thấp:

| Lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| β=1,0 (tâm trước CK) | 15.042 (+2,9%) | 14.827 (+1,4%) | 14.423 (−1,4%) | 14.233 (−2,7%) |
| β=0,5 | 14.827 (+1,4%) | 14.723 (+0,7%) | 14.521 (−0,7%) | 14.423 (−1,4%) |

**Kịch bản (trọng số = nhận định, ước lượng):** cơ sở NPV0 80% (TB 15.383; điểm 15.860) · tái canh bị buộc 20% (TB 11.574; điểm 11.924). Độ nhạy p bị buộc 0/10/30%: 15.383 / 15.002 / 14.240 (trước CK). Diễn giải khác "thanh lý 2029–36 không trồng lại" 13.454 — không vào base. Stress RSS3 2027–28 = 1,60: 13.278 (r5).

**Lưới chuẩn hoá.** 18 ô = kịch bản (0,80/0,20) × mid RSS3 thực P25 1,924 / TB 2,221 / P75 2,432 (.25/.5/.25) × L 22/27/32 (.25/.5/.25); r cố định 13,5%.

| | P10 | P50 | P90 | Tâm |
|---|---|---|---|---|
| Trước CK | 11.485 | 14.587 | 17.777 | 14.621 |
| **Sau CK 2,0%** | **11.255** | **14.296** | **17.422** | **14.329** |

## 8. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
| Mốc | Thời điểm | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|---|
| SXKD tháng 10 | ~10/11/2026 | Bán ≥ ~1.390 t/tháng | Bán < 1.000 t; LNTT 10T < 9T |
| Chuyển sàn HOSE | Q4/2026 | Được chấp thuận | Chậm |
| BCTC Q4/2026 | ~20/01/2027 | Tồn kho giảm, CFO ≥ LNST | Tồn kho không giảm |
| HĐQT xét Dakruwood | 12/2026 | Không mua / giá ≤ sổ sách có thẩm định | Mua giá cao từ cổ đông lớn |
| ĐHĐCĐ 2027 | 2027 | Dự toán tái canh IRR ≥ r | Đẩy nhanh thanh lý, capex >170 tr/ha |
| Giá cổ phiếu | — | < P10 11.255 ⇒ DƯỚI vùng | > P90 17.422 ⇒ TRÊN vùng |

## Phụ lục — cái gì ĐỔI so với DD cũ (sổ mức giá DRI rev2, 03/11/2026: 13.300 / 14.360 / 16.490)
- **Tâm sau CK 14.360 → 14.329 (−0,2%)**: r giữ 13,5%; ADV 250 phiên vẫn 8,33 tỷ (CK 2,0%). Khác biệt nhỏ do r nay **cố định** (r5 lấy TB trên lưới có trục r 11,5/13,5/15,5, hàm lồi theo r kéo TB lên ≈+30 đ). Chân đối chứng: base r13,5 = 15.860 = pin r5.
- **Vùng đổi định nghĩa**: cũ = P25–P75 lưới base (13.300–16.490); mới = P10–P90 lưới có kịch bản là một trục (11.255–17.422). Cận dưới mới lệch −15% so cận dưới cũ — **>10%, nguyên nhân chính: lưới mới chứa nhánh tái canh bị buộc (20%)**, cũ chỉ lưới base.
- Giá 13.400 (03/11) → 13.500 (04/11). Nhãn cũ "HỢP LÝ, sát cận dưới" → "TRONG vùng".
- Cờ quản trị mới: Dakruwood (NQ HĐQT 15).

## Open issues
Hợp đồng tô nhượng 01616/KĐ/DDT4 chưa xác minh (p=20% là nhận định); L đời cạo là giả định; SXKD T10; HOSE; snapshot giá RSS3/USDVND 03/11 (không cập nhật trong redo). Chưa qua fundamental-skeptic vòng này.
