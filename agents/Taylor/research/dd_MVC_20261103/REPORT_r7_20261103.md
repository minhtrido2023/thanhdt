# DD — MVC (CTCP Vật liệu và Xây dựng Bình Dương) · r7 · as-of 03/11/2026 · job `Taylor_20261103_132045`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. r6 lưu `REPORT_r6_20261103.md` (BCTC/nguồn/kiểm kê dự án mới — vẫn là gốc);
> báo cáo NĐT r6 lưu `archive_internal/MVC_DD_investor_report_20261103_rev5_r6.md`.
> **Nguyên tắc user 03/11:** dự án MỚI base = sổ sách/NPV 0 (mỏ mới 438,4, đất 30, cụm CN, mua NNC 51% — GIỮ NGUYÊN như r6); giảm trừ base cần cơ sở độc lập,
> ĐỐI XỨNG; chu kỳ MỎ HIỆN HỮU (Tân Lập + NNC Mũi Tàu) KHÔNG phải dự án mới ⇒ chuẩn hoá chu kỳ (r7 sửa lỗi tâm stress 0 của r6 — SKEPTIC_R3 "Hệ quả MVC").
> **Mù giá — trung thực:** `r7/calc/model_r7.py` không đọc giá; khoá `r7/calc/LOCK_md5_r7.txt` 20:33:44 ICT trước `compare_r7.py`. r1–r6 đã biết giá 13.700/13.300,
> và giá MVC 03/11 hiện ra trong phiên khi đọc giá NNC (20:26, cùng lệnh) — SAU khi NNC r4 (chứa MVC đồng thời 18.392) đã khoá ⇒ khoá chỉ chứng minh THỨ TỰ CHẠY.

## 0. Kết luận
**Tâm = 18.392 đ/cp** (tham chiếu skeptic vòng 4: 18.305, lệch +0,5%) = 0,20×STRUCTURAL **23.755** + 0,45×ADMIN_GATED **18.726** + 0,35×CYCLICAL **14.898**
(Bobby §4; mỗi trạng thái W 25/50/20/5 × g2031/thực 50:50, r13, holding 0). V_NNC giải đồng thời trong từng trạng thái ⇒ kỳ vọng **67.596** = tâm NNC r4.
- STRUCTURAL: biên đỉnh (stress 0), Tân Lập 1,30 / NNC 1,40. ADMIN: stress 0,5, SL năm thường Tân Lập & NNC 1,10 (2028–30)/1,20. CYCLICAL: stress 1,0,
  trần NNC 249,7k (biên đá 34,3% ở SL năm thường) ⇒ Tân Lập 0,91× = 227,2k, chi phí 145,2k ⇒ biên Tân Lập 36,1% (đỉnh 2026 58,0%).
- Lưới 13.122 (đăng ký trước, docstring model_r7): P10 **15.597** · P25 **16.765** · P50 18.276 · P75 **19.997** · P90 **21.723** (min 12.854, max 27.781).
  Thang: RẺ ≤15.597 · RẺ CÓ ĐK 15.597–16.765 · HỢP LÝ 16.765–19.997 · NGHIÊNG ĐẮT 19.997–21.723 · ĐẮT ≥21.723.
- **So giá (sau khoá): 13.300 (DNSE close G1 03/11) ⇒ RẺ (dưới P10, −14,7%); 0,1% lưới dưới giá; 0,72× tâm; P/B 0,86.**
- **Điều kiện an toàn (giá đá hoà vốn, 100% hồi biên):** giá NNC 231k/m³ tiền 2026 (Tân Lập 210k) ⇒ biên Tân Lập 30,8% / NNC 28,8% ở SL năm thường;
  SL trần: 223k (Tân Lập biên 28,4%). Dưới TB chu kỳ 34,3% — không phải đáy lịch sử.
- Gordon (r13 g3, BVPS 15.460) ROE chuẩn hoá theo trạng thái 20,7% (Q3/26 TTM) · 14,0% · 7,4% (TB 2017–25) ⇒ 27.364 · 17.075 · 6.785; trộn 13,0% ⇒ **15.531**.
  Giá hàm ý ROE 11,6%; tâm hàm ý 14,9%.
- 3 trạng thái × đường giá (g2031 / thực): STRUCTURAL 22.026 / 25.484 · ADMIN 17.308 / 20.144 · CYCLICAL 13.684 / 16.113.

## 1. Cầu nối kỳ vọng (tỷ; đ/cp = ×10; `r7/calc/model_r7_out.json` bridge_ty)
Tân Lập 598,1 · mỏ mới sổ sách sau trễ 389,7 · BOT 93,7 · gạch/xăng 41,5 · đất 30,0 · LK nhỏ/ICD 99,9 · Q4 50,0 · nợ ròng −116,6 ⇒ trực tiếp 1.186,3; phần NNC 652,9 ⇒ 1.839,2.

## 2. Độ nhạy (so tâm 18.392; `model_r7_out.txt` mục 5)
Trần tính ở SL 1,40 −662 · trọng số nghiêng STRUCT +1.389 / CYC −826 · chỉ CYCLICAL 14.898 · chỉ STRUCTURAL 23.755 (= r6 + V_NNC r3) · SL năm thường 1,05 −8 / 1,20–1,30 +24 ·
Tân Lập không cắt SL +276 · upside đối thủ hết GP 2034 +876 · GP Tân Lập 2035 −1.064 / 2045 +846 · chi phí Tân Lập ±15% ∓1.622/1.668 · REL 0,88 +216 / 0,95 −281 ·
r 11/15% +1.216/−1.032 · PW ±564 · phẳng danh nghĩa 15.104 · mỏ mới: upside tốt +278, NPV xấu −2.301, hai phía −2.023, bỏ trễ +510 · holding 15/30% −1.019/−2.023 ·
V_NNC cố định 77.656 +972 · độ dốc **966 đ/cp MVC / +10.000 NNC**; V_NNC = thị giá NNC 46.100 (trái D1, tham chiếu) ⇒ 16.316 (−2.076).

## 3. Nợ ròng theo lộ trình (ước lượng; chưa tính khấu hao/vốn lưu động; mỏ mới chưa có dòng tiền 2028)
Cuối 2026 67 · 2027 589 · 2028 **997** tỷ (CYCLICAL 1.040); CFO 2027 204, 2028 kỳ vọng 106 (STRUCT 179 / ADMIN 107 / CYC 63).
**Ngưỡng cảnh báo: nợ ròng > lộ trình + 150 tỷ (2027 > 739; 2028 > 1.147).**

## 4. Sản phẩm & kiểm
- Báo cáo NĐT `investor_report/MVC_DD_investor_report_20261103.{md,pdf,html}` (đè r6): 12 trang, thân 1.796 từ; grep luật 18 rỗng (md + subject);
  dry-run email `--html-out`: 16 ảnh, 8,6 MB, 16/16 alt; **KHÔNG gửi**. md5 PDF c7a09871092a84b166a06ed2b287d402.
- Sổ mức giá: MVC@2026-11-03#6 (supersedes #5; evidence #5 trỏ archive `_rev5_r6.md`); selfcheck 0 lỗi.
- fundamental-skeptic: **CHƯA CHẠY** trên r7.

## 5. Giới hạn
Xác suất 3 trạng thái là nhận định của Bobby; SL năm thường neo NNC 2024 (FPTS, thứ cấp) và áp cùng mức cho Tân Lập (cùng công suất ~1,4); trần chu kỳ tính
trên chi phí NNC, Tân Lập dùng REL 0,91 (biên Tân Lập ở trần 36,1% ≈ TB); lộ trình nợ là ước lượng thô; mọi giới hạn khác của r6 giữ nguyên.
