# DD DRI — r4 (job `Taylor_20261103_152938`, 03/11/2026) — NỘI BỘ

> Bản trước (DD 27/10 + định giá vòng 4 POST-HOC, tâm 10.500, cơ sở 9.078–11.116): `archive_internal/REPORT_20261027_truoc_r4.md`;
> cập nhật Q3: `REPORT_Q3_UPDATE.md` (giữ nguyên). Calc: `r4/calc/` (khoá `LOCK_md5_r4.txt` 22:36:11 ICT TRƯỚC bước thanh khoản + so giá).
> Báo cáo NĐT: `investor_report_v4/DRI_DD_investor_report_20261103.{md,pdf,html}` — **CHƯA gửi email** (dry-run OK, 18 ảnh, 8,7MB).
> **Trạng thái nắm giữ:** DRI đang ở diện ĐÃ BÁN HẾT theo quy tắc cờ (không giữ). DD làm bình thường; dòng này chỉ ở bản nội bộ.
> **CHƯA chạy fundamental-skeptic trên r4.**

## 0. Kết quả
| | Trước CK thanh khoản | Sau CK (5 tỷ, Y=1, −2,0%) |
|---|---|---|
| Tâm (mid 2,341, L27, r 13,5%) | **16.950** | **16.610** |
| Thang P10/P25/P50/P75/P90 (lưới 27 ô, trọng số) | 14.414 / 15.857 / 16.950 / 19.222 / 23.175 | 14.125 / 15.540 / 16.610 / 18.837 / 22.711 |
| Bình quân 3 kịch bản (20/60/20, điểm giữa dải) | 17.053 | **16.712** |
| Kịch bản tái canh bị buộc (T1 engine cũ @ mid thấp–tâm) | 10.928–11.971 | 10.709–11.732 |
| Kỳ vọng 80% base / 20% bị buộc (khai trước trong model) | 15.954 | 15.634 |
- So bản cũ: tâm 10.500 → **16.610 sau CK (+58%)**. Cầu nối @r12%, mid 1,97 → chuẩn hoá: T1 cũ 9.078 | tái canh NPV0 **+4.018** | XDCB 72,71 tỷ theo giá vốn **+993** | r 12%→13,5% **−514** | mid 1,97→2,341 thực **+3.375** ⇒ 16.950.
- **Giá đóng 03/11: 13.400** (DNSE ohlc 1D, `dd_audit_newproject_20261103/close_20261103.md`) ≤ P10 sau CK (14.125; 1 tỷ: 14.285; 10 tỷ: 14.006) ⇒ nhãn đăng ký trước **RẺ** (≤P10) ở mọi quy mô 1/5/10 tỷ. Giá −19% so tâm sau CK.
- Điều kiện của nhãn: (i) tái canh = NPV 0 (luật user 03/11); nếu bị buộc với kinh tế giả định cũ ⇒ giá trị 10,7–11,7k < giá; (ii) RSS3 2027–28 về 1,60 $/kg ⇒ 13,9k ≈ giá; (iii) đời cạo 22 năm ⇒ 14,1k.
- Độ nhạy lãi huy động (β1): −100/−50/+50/+100bp ⇒ +3,1/+1,5/−1,5/−2,9% (sau CK 17.128/16.865/16.364/16.126); β0,5: ±0,8/±1,5%. Thấp vì dòng tiền có hạn tới 2054.

## 1. Tái canh có phải nghĩa vụ tô nhượng? — KHÔNG có bằng chứng
- BCTN 2025 (tr. chiến lược + kế hoạch HĐQT) và BCTN 2024: tái canh "phù hợp với hợp đồng tô nhượng đất và chất lượng vườn cây"; "thanh lý và trồng tái canh vườn cao su KÉM HIỆU QUẢ, phù hợp với thời hạn của hợp đồng tô nhượng"; "nếu tính hiệu quả cao" (xưởng gỗ). ⇒ ngôn ngữ quyết định kinh doanh có điều kiện hiệu quả, không phải nghĩa vụ. Phương án quản lý rừng bền vững 2024–2054 (NQ 03/NQ-HĐQT 19/03/2024) = FSC.
- Giấy đăng ký tô nhượng sửa đổi lần 4 số 01616/KĐ/DDT4 (30/03/2016) — **không công khai, CHƯA XÁC MINH** điều khoản.
- legal-vn (03/11, có nguồn): Luật KK Đầu tư Lào 14/NA (2016) trần tô nhượng 50 năm, gia hạn được; Luật Đất đai 70/NA (2019) thuê tối đa 50 năm; chỉ nghĩa vụ chung "sử dụng đất đúng thoả thuận, không bỏ hoang" (lệnh 02/2019 thu hồi giấy phép nhà đầu tư không phát triển); **không thấy** điều luật/MoU buộc tái canh cao su; không thấy tiền lệ DN cao su VN ở Lào bị buộc tái canh/thu hồi vì không trồng lại (Campuchia 2019: HAGL bị thu hồi 742 ha đất chưa phát triển). 2004+50 = 2054 khớp "tầm nhìn 2054" (suy luận).
- Phần đất rừng bảo tồn Đông Huê Sáo: cam kết trả về rừng khi hết chu kỳ 1 ⇒ mất khỏi sản xuất; ở base không ảnh hưởng (tái canh NPV 0).
- ⇒ **Base = NPV 0**; kịch bản "tái canh bị buộc (dùng-hoặc-mất-đất) + kinh tế như giả định cũ (capex 172,6 tr/ha từ chi phí chăm sóc, NS cây mới 1,69, chưa nguồn)" = 20% chủ quan, ngoài base.

## 2. Chuẩn hoá chu kỳ giá (tài sản hiện hữu)
- RSS3 WB tháng 2006-04→2026-09 quy USD 2025 bằng CPI-U (FRED; 2025-10 trống ⇒ nội suy). TB thực 2013–26 **2,341** (tâm), trung vị 2,221 (thấp), TB 2006–26 3,025 (cao, gồm siêu chu kỳ 2010–11). Danh nghĩa TB 2013–26 1,941. Q3/26 2,753 = phân vị 82% chuỗi thực 2013–26.
- Bản cũ dùng mid DANH NGHĨA 1,865–2,18 trong khung dòng tiền GIÁ THỰC 2025 ⇒ lệch đơn vị (thấp ~15–20%). Đây là phần lớn +3.375.
- Đường 2027–28: giữ PEAK 60/MID 40 của Bobby (`vn_sector_read_rubber_20261027.md`). Lưới không có trục giá DRI riêng; liên kết giá DRI–RSS3 qua P25 47,24 tr/t / RSS3 TB2025 (engine).
- Cửa sổ 2013–26 khai trước khi chạy; nhưng tôi biết hình dạng chuỗi danh nghĩa trước đó — ghi nhận (2013 thực 3,87 kéo TB lên; bỏ 2013 TB ≈2,25, chưa đo chính xác — `ước lượng`).

## 3. Các phần giá trị khác — đối xứng
- XDCB dở dang 72,71 tỷ (tái canh 132 ha KTCB + sầu riêng + XDCB-MMTB) cộng theo giá vốn (+993 đ/cp). Bản cũ không cộng (ngầm coi mất).
- Liên doanh nhà máy gỗ, sầu riêng 238 ha, cà phê liên kết, giai đoạn 2 tái canh: NPV 0 (không cộng +176 sầu riêng, không trừ −1,3…−1,5k giai đoạn 2).
- Gỗ thanh lý cuối đời vườn hiện hữu (~20,9 tr/ha, ước từ 9T/26): giữ (tài sản hiện hữu).
- Đất: tô nhượng, không cộng/trừ; gia hạn sau 2054: 0.
- Giữ nguyên từ engine (nguồn BCTC3): tiền ròng, Dakruco 50%, cắt 15% tiền Lào, quỹ dự phòng Lào, WHT, KTPL, Q4 Base, tồn 1.717 t.

## 4. Thanh khoản (`liquidity_r4.py`, sau khoá)
- 250 phiên 30/10/2025–02/11/2026 (bỏ dòng BQ 03/11 có thể chưa đồng bộ đủ): ADV trung vị **8,33 tỷ**, TB 13,04, trung vị 60 phiên 13,82; σ ngày 2,58%; 0 phiên KL=0; Amihud trung vị 0,0014/tỷ; free float ~55%.
- d = Y·σ·√(Q/ADV): 1/5/10 tỷ ⇒ 0,9/2,0/2,8% (Y0,5–1,5: 0,4–1,3 / 1,0–3,0 / 1,4–4,2%); thoát 15% ADV 0,8/4/8 phiên. Lệnh DRI của quỹ ~3.800 cp quá nhỏ để hiệu chỉnh Y.

## 5. r
- 13,5% danh nghĩa neo lãi huy động 12T 7,40% (CCTG 12M 02/11/2026; số theo dispatch, `deposit_rate_vn.macro_killswitch_a_status()` 03/11). Khung engine giá thực ⇒ r thực 10,19% (bản cũ 8,74% từ 12% danh nghĩa). Trục lưới 11,5/13,5/15,5%.
- r* thị trường 15,1% (panel 30/10, phân vị 75%); TPCP 10Y 4,58% (UNVERIFIED) — `dcf_rate_display.dcf_rate_lines('2026-11-03')`.

## 6. Giới hạn / việc mở
- CHƯA skeptic r4. Điểm nên tấn công: (a) cửa sổ 2013–26 và TB vs trung vị; (b) liên kết P_DRI ∝ RSS3 trong thực tế giá USD; (c) L27 không nguồn; (d) 20% xác suất bị buộc; (e) XDCB có phần không phải dự án.
- Hợp đồng tô nhượng 2004/2016: xin DRI trích điều khoản sử dụng đất/tái canh/gia hạn.
- SXKD tháng 10 (~10/11) — nowcast Q4.

## 7. Sổ mức giá
`kb/dd_price_zones.json` DRI@2026-11-03 rev mới: vùng 15.540–18.837 (P25–P75 sau CK), tâm kỳ vọng 16.712 sau CK (center_alt tâm 16.610), price_ref 13.400 @2026-11-03.
