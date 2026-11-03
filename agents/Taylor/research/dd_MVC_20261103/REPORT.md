# DD — MVC (CTCP Vật liệu và Xây dựng Bình Dương) · r8 · as-of 03/11/2026 · job `Taylor_20261103_134709`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. r7 lưu `REPORT_r7_20261103.md`; r6 `REPORT_r6_20261103.md` (BCTC/nguồn/kiểm kê dự án mới — vẫn là gốc);
> báo cáo NĐT r7 lưu `archive_internal/MVC_DD_investor_report_20261103_rev6_r7.md`.
> **Nguyên tắc user 03/11:** dự án MỚI base = sổ sách/NPV 0 (mỏ mới 438,4 − trễ GP = 389,7; đất 30; cụm CN, mua NNC 51% NPV 0 — GIỮ NGUYÊN); giảm trừ base cần cơ sở,
> ĐỐI XỨNG; chu kỳ MỎ HIỆN HỮU (Tân Lập + Mũi Tàu) chuẩn hoá theo cơ sở độc lập.
> **Thứ tự chạy — trung thực:** `r8/calc/model_r8.py` không dùng giá thị trường làm đầu vào; khoá `r8/calc/LOCK_md5_r8.txt` 20:58:31 ICT trước `compare_r8.py`.
> r1–r7 đã biết giá 13.300 và brief nêu tham chiếu skeptic ≈16,5–16,9k ⇒ khoá chỉ chứng minh THỨ TỰ CHẠY.
> **Hồ sơ riêng nội bộ:** nhãn RẺ (dưới P10 lưới) ≠ QUALIFY §2.5 (chu kỳ ở đỉnh; P/E 4,3 là P/E đỉnh biên; nợ ròng ≈1.070 tỷ 2028; NOPAT nhánh CYC 2028 55 ≈ lãi 60). Bản NĐT không mang nhãn này.

## 0. Kết luận (sửa theo `SKEPTIC_R7_20261103.md`)
**Tâm = 16.702 đ/cp** (tham chiếu skeptic ≈16,5–16,9k: trong dải) = 0,20×STRUCTURAL **23.690** + 0,45×ADMIN_GATED **15.191** + 0,35×CYCLICAL **14.652**; V_NNC đồng thời 61.567.
Cầu nối r7 → r8 (`model_r8_out.txt` §1): r7 tái lập **18.392** → ADMIN trễ 1 năm (V_NNC r5) **16.912** (= skeptic) → định phí Tân Lập chỉ ở ADMIN/CYC (cách skeptic) 16.712
(−200; skeptic −347 trên nền r7) → định phí ĐỐI XỨNG mọi kịch bản (tâm) **16.702**.
- (1) ADMIN = NNC r5: stress 0,5 năm 2028 → 1,0 từ 2029, áp CẢ Tân Lập. Trục: 0,5 vĩnh viễn 18.182 · trễ 1 năm 16.702 · 1,0 từ 2028 16.460.
- (2) Định phí Tân Lập: costTL(v) = costA 145,2 × unit_cost_NNC(v)/unit_cost_NNC(1,30) (VAR 110/FIX 70 của NNC; 1,30 = SL hiệu chỉnh costA — GIẢ ĐỊNH); +3,3% ở SL 1,18.
  Biên Tân Lập ở trần: 0,91×249,7 = 227,2k vs chi phí 150,0k ⇒ **34,0%** (NNC 34,3%; r7 36,1% — đã hết nghịch lý "bán rẻ hơn mà biên cao hơn").
- (3) **Biên chu kỳ Tân Lập: CHƯA KIỂM.** Không có dữ liệu mảng đá riêng: thuyết minh HN/riêng Q3/2026 VI.1–2 gộp "doanh thu bán hàng / giá vốn hàng đã bán"
  (đá+gạch+xăng), BCTN 2025 + tài liệu ĐHĐCĐ 2026 không tách bộ phận; txt/ đã quét "đá xây dựng/bộ phận/segment". GPM toàn công ty 2017–21 7–15% (lẫn mảng).
  Trục {25%, 30%, ≈NNC}: tâm 15.565 (−1.138) · 16.110 (−592) · **16.702**; nhánh CYC 13.175 / 13.884 / 14.652. Tâm giữ ≈NNC vì neo GIÁ cụm (0,91× trần NNC) + CHI PHÍ
  riêng Tân Lập có định phí — có cơ sở; 25/30% không có dữ liệu bộ phận ⇒ trục lưới + độ nhạy. Lưu ý: ở chế độ 25/30% trần giá chạy theo chi phí nên lưới ít nhạy với ±15% chi phí.
- Lưới **118.098** (= r7 13.122 × ADMIN 3 × biên Tân Lập 3; thang ĐĂNG KÝ TRƯỚC trong docstring): P10 **14.486** · P25 **15.411** · P50 16.715 · P75 **18.295** · P90 **19.913**
  (min 12.020, max 27.743). Thang: RẺ ≤14.486 · RẺ CÓ ĐK –15.411 · HỢP LÝ –18.295 · NGHIÊNG ĐẮT –19.913 · ĐẮT ≥19.913.
  Theo biên Tân Lập: 25% P10/P50 14.275/16.284 · 30% 14.746/16.776 · ≈NNC 14.483/17.122.
- **So giá (sau khoá): 13.300 (DNSE close G1 03/11) ⇒ RẺ (dưới P10, −8,2%); 0,91% lưới dưới giá (25%: 0,97%; ≈NNC 1,61%); 0,80× tâm; P/B 0,86.**
- **Hoà vốn (100% hồi biên, biên Tân Lập ≈NNC):** giá NNC 233k (Tân Lập 212k) ⇒ biên Tân Lập 29,4% / NNC 29,6% ở SL năm thường; SL 1,40: 221k (Tân Lập 201k, 29,6%).
  NNC có **3/14 năm GPM dưới mức hoà vốn này** (2013 21,2%; 2022 21,4%; 2023 27,9% — GPM_NNC BQ trong `r6/calc/model_r6.py`).
- **Gordon nhất quán ánh xạ (ADMIN = CYC ở năm điển hình):** ROE 20,7% · 7,4% · 7,4% ⇒ 27.364 · 6.785 · 6.785; trộn 10,1% ⇒ **10.901 (giá cao hơn 22%)**. Giá hàm ý ROE 11,6%; tâm 13,8%.
  **DCF-CYC 14.652 vs Gordon-CYC 6.785 (2,2×):** DCF-CYC = 44,07% NNC nội tại 5.135 + sổ sách/NPV0 (mỏ mới, đất, LK, Q4, tài chính ròng) 4.530 + vận hành (Tân Lập+BOT+gạch)
  4.987 đ/cp; ROE hàm ý DCF-CYC 12,5%. Gordon 7,4% (TB 2017–25, gồm 2021 lỗ, gạch lỗ, giá đá thấp) ngầm định TOÀN BỘ vốn chủ — kể cả cổ phần NNC (định giá nội tại P/B≈1,8) và
  tài sản mới theo sổ sách (nguyên tắc user: 1,0×) — chỉ đáng 0,44× sổ sách vĩnh viễn ⇒ hai thước đo khác ở cách đối xử tài sản không phụ thuộc biên MVC, không phải lỗi số.
- 3 trạng thái × đường giá (g2031 / thực): STRUCTURAL 21.964 / 25.416 · ADMIN 13.964 / 16.418 · CYCLICAL 13.441 / 15.864.
- NNC trong hệ MVC: V_NNC 61.567 (NNC r5 tâm 61.666 tính với MVC chưa định phí — lệch −99, <0,2%, chưa dựng lại NNC).

## 1. Cầu nối kỳ vọng (tỷ; đ/cp = ×10; `r8/calc/model_r8_out.json` bridge_ty)
Tân Lập 487,3 · mỏ mới 389,7 · BOT 93,7 · gạch/xăng 41,5 · đất 30,0 · LK nhỏ/ICD 99,9 · Q4 50,0 · nợ ròng −116,6 ⇒ trực tiếp 1.075,5; phần NNC 594,7 ⇒ 1.670,2.
Tân Lập + NNC + mỏ mới theo vốn đã chi = 14.717 đ/cp > giá 13.300.

## 2. Độ nhạy (so tâm 16.702; `model_r8_out.txt` §6)
Biên Tân Lập 25/30% −1.138/−592 · ADMIN 0,5 vv +1.480 / 1,0 −242 · trần SL 1,40 −875 · trọng số nghiêng STRUCT +1.754 / CYC −506 · chỉ CYC 14.652 · chỉ STRUCT 23.690 ·
SL 1,05 +76 / 1,20–1,30 −41 · upside đối thủ 2034 +1.219 · GP Tân Lập 2035 −764 / 2045 +608 · chi phí Tân Lập ±15% −1.528/+1.673 · REL 0,88 +256 / 0,95 −339 ·
r 11/15% +976/−832 · PW ±529 · phẳng danh nghĩa 13.854 · mỏ mới hai phía −2.027, bỏ trễ +510 · holding 15/30% −928/−1.843 · độ dốc **966 đ/cp / +10.000 V_NNC**;
V_NNC = thị giá NNC 46.100 (tham chiếu, không vào tâm) ⇒ 15.208 (−1.494).

## 3. Nợ ròng theo lộ trình (ước lượng; NOPAT − lãi vay sau thuế; chưa tính khấu hao/vốn lưu động; mỏ mới chưa có dòng tiền 2028)
Lãi suất **GIẢ ĐỊNH 7%/năm** trên nợ ròng bình quân (đo: lãi vay 9T/2026 12,23 tỷ [BCTC HN Q3 KQKD dòng 24] trên vay NH BIDV+khác 256,8 → 461,8 tỷ [V.20] ⇒ hiệu dụng
≈4,5%/năm, ước lượng thô dư nợ 2 đầu kỳ — cận dưới; vay dự án dài hạn chưa công bố). Cuối 2026 67 · 2027 **608** (lãi 24) · 2028 kỳ vọng **1.069** (STRUCT 987 / ADMIN 1.070 /
CYC 1.115); lãi 2027+2028 ≈82 tỷ (4,5%: 52; nợ 2028 1.045). NOPAT 2028: STRUCT 179 / ADMIN 99 / **CYC 55 vs lãi 60**. Biên Tân Lập 25%: 2028 kỳ vọng 1.080, CYC 1.135.
**Ngưỡng cảnh báo: nợ ròng > lộ trình + 150 tỷ (2027 > 758; 2028 > 1.219) HOẶC lãi vay 4 quý > 50% LN gộp đá 4 quý.**

## 4. Sản phẩm & kiểm
- Báo cáo NĐT `investor_report/MVC_DD_investor_report_20261103.{md,pdf,html}` (đè r7): 12 trang, thân ≈1.807 từ; grep luật 18/4/12 + "QUALIFY/§2.5" rỗng (md + subject);
  dry-run email `--html-out`: 16 ảnh, 8,6 MB, 16/16 alt; **KHÔNG gửi**. md5 PDF bc4e3897bd42e2ca753cd2e290c025b7.
- Sổ mức giá: MVC@2026-11-03#7 (supersedes #6; #6 trỏ archive `_rev6_r7.md`); selfcheck 0 lỗi.
- fundamental-skeptic CHƯA chạy trên r8.
