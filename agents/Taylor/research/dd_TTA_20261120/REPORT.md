# DD — TTA (CTCP Đầu tư XD & Phát triển Trường Thành, HOSE) · 2026-11-20 · job `Taylor_20261120_041933`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua. Không đặt lệnh, không wire. User quyết.
> **Nguồn** — **[Q3]** = BCTC **tổng hợp** Q3/2026, có ký, duyệt 28/10/2026, tải từ truongthanhgroup.com.vn/co-dong/bao-cao-tai-chinh
> (`src/BCTC-quy-3.2026-TV.pdf`, scan, đọc bằng ảnh `png/q3_*.png`); **[KT25]** = BCTC tổng hợp kiểm toán 2025 (`src/BCKT-TTA-2025-Viet.pdf`);
> **[GT]** = CV 362/TTA-CV giải trình LNST 6T/2026 (12/08/2026); **[NQ]** = NQ ĐHĐCĐ 23/04/2026; **[HĐQT]** = NQ HĐQT 29/06/2026;
> **[TX]** = báo cáo sở hữu nhóm Thuỷ điện Trà Xom 25/08/2026; **[BQ]** = `tav2_bq.ticker_financial`/`ticker`; **[Bobby]** = sector read
> `kb/data_registry/market-state/sector_read_dien_mat_troi_thuy_dien_nho_20261120.md`; báo chí ghi tên cạnh số. Mô hình: `model/dcf_tta.py`
> (md5 `d866bd0a761d99fddb5222f7a709c919`). Số tự đặt gắn **(ước lượng)**.
> ⚠️ TTA **không có công ty con** ⇒ không có BCTC hợp nhất/riêng; chỉ có BCTC **tổng hợp** (gồm chi nhánh Ninh Thuận) [Q3 tr.10]. Giải trình
> LNST Q3/2026 riêng **không có** trên website (chỉ có giải trình bán niên 12/08) — không tìm thấy, không suy diễn.

## 0. Kết luận

**Verdict: KHÔNG RẺ ở 10.250 đ (19/11/2026) — giả thuyết "P/B 0,77, P/E 7 = rẻ" là SAI ở phần lớn, ĐÚNG chỉ nếu giá FIT được giữ nguyên.**
Lý do một dòng: *~51% doanh thu và ~55% lợi nhuận gộp 9T/2026 đến từ 2 nhà máy mặt trời Ninh Thuận mà Thanh tra Chính phủ đã kết luận
hưởng giá FIT **sai quy định** (Bầu Ngứ FIT1, Núi Một 1 FIT2); EPTC đã ngừng trả khoảng một nửa tiền điện (phải thu EPTC 237,7 → 399,6 tỷ
trong 9T), trong khi lãi kế toán vẫn ghi đủ FIT.*

| Kịch bản (giá trị MÙ giá) | P | VCSH (tỷ) | đ/cp |
|---|---|---|---|
| A — giữ FIT cả 2, thu đủ phải thu, Phước Hoà = sổ sách | 0,25 (ước lượng) | 2.264 | **12.679** |
| B — Bầu Ngứ FIT1→FIT2 từ 2027 + hồi tố ~394 tỷ (bù trừ phải thu bị giữ); Núi Một 1 giữ FIT2 | 0,50 (ước lượng) | 1.578 | **8.836** |
| C — cả 2 về trần chuyển tiếp 1.184,90 + hồi tố ~1.149 tỷ + thuỷ văn −15% 2027 + lãi vay +1pp | 0,25 (ước lượng) | 321 | **1.800** |
| **Trọng số** | | | **≈ 8.040** (trước chiết khấu thanh khoản) |
| **Sau chiết khấu thanh khoản 10%** (ước lượng, §6.6) | | | **≈ 7.240** |

**Vùng đọc (sau thanh khoản):** ≤ **6.150** (= 0,85 × tâm) vùng có biên an toàn · 6.150–8.040 hợp lý · > 8.840 (= giá trị kịch bản B
trước thanh khoản) là trả giá cho xác suất giữ FIT cao hơn mức cơ sở. Giá 10.250 ngầm định thị trường đặt ~60–70% xác suất cho kịch
bản A (ước lượng, chỉ để đọc — không dùng giá để chỉnh mô hình).
**Pháp lý: WARNING** (FIT sai đối tượng — chưa có quyết định cuối; giao dịch bên liên quan nhỏ; chuyển giao tài sản của cựu Chủ tịch). Kiểm
toán 2025 **chấp nhận toàn phần**, không ngoại trừ/nhấn mạnh [KT25 tr.6].
**Moat: NONE** (§5) — không thưởng, không trừ.

---

## 1. Kiểm chứng số Mike đọc từ BQ + giả thuyết

| Chỉ tiêu | BQ (Mike) | BCTC gốc | Kết quả |
|---|---|---|---|
| DT Q3/26 / Q3/25 | 210,2 / 206,4 | **210,16 / 206,39** [Q3 tr.6] | Khớp |
| LNST Q3/26 / Q3/25 | 74,3 / 80,9 | **74,35 / 81,17** [Q3 tr.7] | Khớp (Q3/25 lệch 0,27 — BQ lấy bản trước điều chỉnh?) |
| NP_P0 = LNST mẹ? | ? | **= LNST tổng hợp TRƯỚC chia lợi nhuận HTKD và quỹ KTPL** | ⚠️ LN thuộc cổ đông thấp hơn ~18% (§2.2) |
| 9T/26 DT / LNST | — | **575,33 / 206,71** (9T/25: 542,42 / 188,46), +6,1% / +9,7% | |
| Vốn hoá 1.890 tỷ / P/B 0,77 | báo chí | 178,56 tr cp × 10.250 = **1.830 tỷ**; BVPS 14.197 ⇒ P/B **0,72** | |
| "HOSE nhắc nhở nợ vượt ~1.720 tỷ" | brief | **SAI tiền đề**: HOSE nhắc nhở vì **chậm CBTT miễn nhiệm TV HĐQT Trần Huy Thiệu** (nhận 03/06/2026). "1.726 tỷ" chỉ là **tổng nợ phải trả 31/3/2026** báo chí gắn vào tiêu đề (doanhnghiephoinhap.vn, nguoiquansat.vn) | Không có vi phạm covenant nào được nêu |
| Pá Hu "đang xây" | brief | **Đã vận hành từ 10/2020**, 26 MW (web công ty; khoản vay Pá Hu đang trả gốc [Q3 tr.23-24]) | Sửa brief |
| ĐHĐCĐ 2026 | LN −22%, không cổ tức | KH LNST **180 tỷ**; cổ tức 2025 **0%**; LN chuyển sang 2026 565,7 tỷ [NQ] | 9T đã đạt **115%** KH |

**Giả thuyết "P/B 0,77, P/E 7 = rẻ": SAI ở phần lớn.**
- P/E 7 dựa trên LNST tổng hợp. LN thuộc cổ đông theo chính BCTC (EPS) = 949,68 đ/cp 9T; TTM = 949,68 + 195,8 (Q4/25 = 1.044,94 − 849,10)
  = **1.145 đ** ⇒ P/E **8,9x**. Nếu Bầu Ngứ về FIT2 (kịch bản B): LN thuộc cổ đông ~133 tỷ/năm (ước lượng) ⇒ ~745 đ ⇒ P/E **~13,8x**.
- P/B: sổ sách chứa doanh thu FIT đã ghi nhưng chưa thu (§3). Trừ hồi tố kịch bản B (394 tỷ) ⇒ BV ~2.141 tỷ = 11.990 đ ⇒ P/B **0,85**; C ⇒ BV
  ~1.386 tỷ ⇒ P/B **1,32**. Peer IPP đòn bẩy cao cũng P/B thấp: GEG 0,63, HDG 0,68, PC1 0,80 [BQ 2026Q3] ⇒ P/B thấp là chuẩn ngành, không phải
  dấu hiệu rẻ riêng.
- Đúng một nửa: nếu FIT được giữ (A), giá trị 12.679 > giá — đó là toàn bộ luận điểm "rẻ", và nó là cược nhị phân vào quyết định hành chính.

## 2. Chất lượng lợi nhuận

### 2.1 Tách theo mảng — 9T/2026 [Q3 tr.29-30, báo cáo bộ phận]
| Mảng | DT | LN gộp | Biên gộp | KH + phân bổ | Ghi chú |
|---|---|---|---|---|---|
| Yên Bái (thuỷ điện NH2, NH2A, Pá Hu) | 279,8 | 150,9 | 53,9% | 69,0 | |
| Ninh Thuận (mặt trời Bầu Ngứ + Núi Một 1) | 295,5 | 185,9 | 62,9% | 88,0 | **51% DT, 55% LN gộp** |
| Tổng | 575,3 | 336,8 | 58,5% | 157,0 | QLDN 16,2 không phân bổ |
- Doanh thu tài chính 9T: **0,48 tỷ** (lãi tiền gửi 0,06 + lãi cho bên liên quan vay 0,42) — không đáng kể. Chi phí lãi vay 98,7 tỷ.
- Lãi/lỗ liên kết: không ghi theo vốn chủ (BCTC tổng hợp, giá gốc); Phong điện Phương Mai 35%, giá gốc 115,5 − dự phòng **16,1** (tăng 1,3 tỷ 9T) [Q3 tr.20].
- Một lần: thu nhập khác 0,01; chi phí khác 1,23 (phạt hành chính 0,43). LN 9T gần như **toàn bộ là vận hành**.
- Động lực Q3: DT +1,8% nhưng giá vốn +11,8% (92,1 vs 82,4) ⇒ LNST −8,4% YoY. Giải trình 6T: tăng do "thuỷ văn và bức xạ thuận lợi" [GT].
- Thuế TNDN thực 6,0% (13,1/219,8) nhờ ưu đãi: NH2A, Pá Hu, Bầu Ngứ, Núi Một 1 thuế suất 10% 15 năm, miễn 4 năm, giảm 50% 9 năm [Q3 tr.21].

### 2.2 Rò rỉ lợi nhuận NGOÀI báo cáo KQKD — hợp đồng hợp tác kinh doanh (HTKD)
[Q3 tr.22] 6 cá nhân góp vốn vào từng nhà máy và **hưởng % LNST của chính nhà máy đó**, chia thẳng qua VCSH (không qua KQKD):
Ngòi Hút 2: **25,22%** (Cao Đăng Kiểu 20,44% + Trâu Kiến Hoa 1,28% + Daniel Triệu 2,59% + Tô Thanh Hà 0,91%); Ngòi Hút 2A: **31,21%**
(Kiểu 23,49 + Hoa 0,79 + Triệu 1,58 + Nguyễn Duy Viễn 5,35); Bầu Ngứ: 0,51% (Phạm Mạnh Thắng). Vốn góp ghi "phải trả dài hạn khác" 125,3 tỷ.
Chia LN HTKD: 2025 **31,0 tỷ**, 9T/26 **23,1 tỷ**; + quỹ KTPL/BĐH 14,0 tỷ [Q3 tr.26]. ⇒ LN thuộc cổ đông 9T = 206,7 − 23,1 = **183,6 tỷ** (BCTC tr.28).
Thời hạn HTKD và điều khoản thoái vốn: **không có trong BCTC — cần kiểm chứng**. Mô hình trừ 12% EBITDA thuỷ điện (≈ mức 2025) suốt đời (ước lượng).

### 2.3 CFO thật vs lãi
| | 2024 | 2025 | 9T/2025 | 9T/2026 |
|---|---|---|---|---|
| LNTT | 248,9 | 248,8 | 201,9 | 219,8 |
| CFO (sau lãi vay đã trả) | **355,0** | **236,3** | 182,6 | **159,0** |
| Tăng phải thu | −19,6 | **−174,9** | −146,5 | **−167,3** |
[KT25 tr.12; Q3 tr.8]. Phải thu ngắn hạn [BQ AR_P0]: ~170–190 tỷ (2023) → 244,6 (Q4/24) → 306,9 (Q4/25) → **466,3** (Q3/26). Riêng EPTC: **237,7 → 399,6 tỷ**
trong 9T [Q3 tr.18]. DT mặt trời 9T 295,5 tỷ (×1,08 VAT ≈ 319 tỷ hoá đơn) mà phải thu EPTC tăng 162 ⇒ **EPTC chỉ trả ~51% số đã xuất hoá đơn** (suy luận
từ số dư; lý do giữ tiền KHÔNG được BCTC giải thích — cần kiểm chứng; khớp với cơ chế EVN tạm thanh toán cho dự án bị kết luận FIT sai, nhưng chưa có văn bản).
⇒ **~160 tỷ/năm LN kế toán là doanh thu FIT chưa thu được tiền.** Phần phải thu EPTC vượt mức bình thường (~2 tháng ≈ 70 tỷ) ≈ **330 tỷ (ước lượng)**.

## 3. Giá bán từng nhà máy & rủi ro tính lại giá

| Nhà máy | Loại | Công suất | COD | Giá/cơ chế | Hết FIT/PPA | Vay còn (30/9/26) [Q3 tr.23-25] | Trạng thái pháp lý |
|---|---|---|---|---|---|---|---|
| **Bầu Ngứ** (Ninh Thuận) | Mặt trời trên hồ thuỷ lợi | 61,77 MWp (phê duyệt 50 MW) | **12/11/2019** | **FIT1 9,35 USc ≈ 2.408 đ** | ~11/2039 | BIDV 2018: **332,0** (tổng mức ĐT 1.426–1.457 tỷ; hạn 132 tháng) | ⚠️ KL TTCP: thuộc **14 dự án hưởng FIT1 sai đối tượng** (khoản 3 Đ5 QĐ 13/2020) (nguoiquansat.vn 01/01/2024; theleader.vn 26/03/2024). Báo NN&MT: chưa có giấy phép hoạt động theo Luật Thuỷ lợi |
| **Núi Một 1** (Ninh Thuận) | Mặt trời trên hồ | 50 MWp | **12/2020** (đóng điện 06/11/2020) | **FIT2 7,09 USc ≈ 1.826 đ** | ~12/2040 | BIDV 2020: **415,5** (tổng mức ĐT 1.036 tỷ; hạn 156 tháng) | ⚠️ KL TTCP: hưởng FIT2 **trái TB 402/2019** (theleader.vn) |
| **Ngòi Hút 2** (Yên Bái) | Thuỷ điện | 48 MW (>30 MW) | 2015 | Cơ chế >30 MW (thị trường/CfD — **chưa kiểm**) | — | BIDV 2021: 95,0; BIDV 2025: 208,0 ("vay vốn tự có hình thành tài sản NH2") | HTKD 25,22% LN |
| **Ngòi Hút 2A** | Thuỷ điện | 8,4 MW | 2016 | Biểu giá chi phí tránh được (≤30 MW) | ~2036 (20 năm, ước lượng) | Agribank: 28,2 (tất toán 30/9/2027) | HTKD 31,21% LN |
| **Pá Hu** (Trạm Tấu) | Thuỷ điện | 26 MW | 10/2020 | Chi phí tránh được, QĐ 392/2026: Bắc 702–726 đ | ~2040 | Agribank 2017: 383,6; Agribank 2025-PH: **310,6** (231 đến hạn trong 12 tháng) | |
| Phương Mai 1 (liên kết 35%) | Gió | 30 MW (COD 24 MW) | — | — | — | — | Giá gốc 115,5, DP 16,1 |
| Phước Hoà | Tích năng | 1.200 MW (đề xuất) | — | **Không có cơ chế giá/PPA** [Bobby §2d] | — | CPXDCBDD **95,7 tỷ** (+19,9 trong 9T) | Quyền chọn hành chính |

**Hai rủi ro KHÁC NHAU — đừng gộp:** (i) [Bobby] nhóm 173 nhà máy **thiếu văn bản chấp thuận nghiệm thu (CCA)**; (ii) nhóm **FIT sai đối tượng**
(KL TTCP về QHĐ VII) — TTA có bằng chứng thuộc nhóm (ii) cho cả 2 nhà máy. Bầu Ngứ/Núi Một 1 **có nằm trong danh sách 173 CCA không: không tìm được
nguồn — cần kiểm chứng**. QĐ 618/QĐ-BCT (05/03/2025) đưa cả 2 vào kế hoạch thực hiện QHĐ VIII (alias.vn) — gỡ vướng quy hoạch, **không** chốt giá.
Kết quả xử lý cuối: **chưa có văn bản** đến 20/11/2026 (Bobby S1: P=0,35 chốt trước 30/06/2027).

**Quy đổi độ lớn (tỷ giá 25.755):** FIT1→FIT2 −24% (Bầu Ngứ −57 tỷ DT/năm); FIT1→trần chuyển tiếp −51% (−120 tỷ); FIT2→trần −35% (Núi Một 1 −54 tỷ).
Hồi tố từ COD: Bầu Ngứ→FIT2 ~**394 tỷ**; cả 2 về trần ~**1.149 tỷ** (= 45% VCSH). Bù trừ được với ~330 tỷ phải thu EPTC đang giữ (ước lượng).
**Curtailment:** BCTC không công bố kWh/cắt giảm — **chưa đo**. **Thuỷ văn:** 9T/26 thuận [GT]; El Niño 2026-27 tác động Bắc Bộ yếu hơn [Bobby §2c] —
mô hình C: −15% thuỷ điện 2027 (ước lượng). Sản lượng 3-5 năm theo nhà máy: **không công bố** — cần BCTN.

## 4. Bảng cân đối, nợ vay, DSCR [Q3 tr.2-5, 23-26]

- Vay **1.554,5 tỷ** (ngắn hạn 292,3, trong đó đến hạn trong 12T 279,9; dài hạn 1.262,3) − tiền 34,9 − tiền gửi/cho vay HTM 132,0 = **nợ ròng 1.387,6**.
  Lãi suất bình quân ~**8,4%/năm** (lãi 98,7 tỷ 9T / dư nợ ~1.560). Toàn bộ VND, BIDV Yên Bái + Agribank Sơn La/Lạng Sơn.
- Tài sản đảm bảo: TSCĐ còn lại **3.461 tỷ đã thế chấp** (≈ 100% TSCĐ) + quyền đất + **quyền đối với vốn góp của cổ đông** (khoản NH2A) + HĐ tiền gửi BIDV.
- Vi phạm covenant: **không có thông tin** trong BCTC; kiểm toán 2025 không nêu hoạt động liên tục.
- ⚠️ 2025 vay mới 518 tỷ "**cho vay vốn tự có** hình thành tài sản" (BIDV 208 + Agribank 310) trên nhà máy đã chạy = rút vốn chủ ra bằng nợ; Q3/26 vay 227 tỷ
  rồi gửi kỳ hạn **116 tỷ** (BIDV 70, MB 46) — trong đó HĐ tiền gửi BIDV làm tài sản đảm bảo hạn mức bảo lãnh 70 tỷ.
- **Net debt/EBITDA**: 1.387,6 / 603 (EBITDA TTM = 9T 472,9 + Q4/25 130,5) = **2,3x**.
- **DSCR 2027** (ước lượng, lịch trả gốc suy từ kỳ hạn vay): nợ phải trả = lãi ~131 + gốc ~280 = 411 tỷ.
  A: (EBITDA 588 − thuế 15 − capex 30)/411 = **1,32**. B: ~**1,18** trước hồi tố, **~0,99** nếu trả hồi tố 79 tỷ/năm. C: **~0,78** trước hồi tố, **<0,3** sau ⇒ cần tái cấp vốn/giãn nợ.
- Phải thu EVN: EPTC 399,6 + EVNNPC 44,0. Dở dang 108,6 (Phước Hoà 95,7). Bảo lãnh cho bên ngoài: không thấy trong BCTC.

## 5. Vị thế & lợi thế cạnh tranh (5F tầng b) — `data/moat_tags.csv` chưa có TTA ⇒ làm đầy đủ

- Loại hình: IPP vừa nhỏ, bán 100% cho 1 người mua (EVN/EPTC/EVNNPC) theo biểu giá/PPA hành chính.
- Bằng chứng: ROIC_Min5Y **4,6–8,4%**, ROIC5Y **9,7%**, ROE5Y **9,2%** [BQ] < Ke 13,5% nhiều năm ⇒ **không** có lợi nhuận siêu ngạch bền. Biên gộp cao
  (58%) là đặc tính tài sản tái tạo (chi phí biến đổi ~0), không phải hào. Quyền mặc cả người mua: tuyệt đối (EVN đang giữ ~51% tiền mặt trời).
  Lực thứ 6: FIT có thể bị thu hồi; PPA thuỷ điện nhỏ hết hạn ~2036–2040 sang TT 54/2025; nghẽn 110 kV Tây Bắc [Bobby §2c].
- **moat_tier = NONE**, moat_type = — , rủi ro số 1 = tính lại giá FIT hồi tố. Không thưởng/không trừ; mô hình giữ biên vận hành hiện hành.
- **Đề xuất dòng mới (KHÔNG sửa file):**
  `TTA,NONE,—,L,"IPP Yên Bái+Ninh Thuận, single buyer EVN; ROIC_Min5Y 4.6-8.4% < Ke; 51% DT từ 2 NM mặt trời bị KL TTCP hưởng FIT sai (Bầu Ngứ FIT1, Núi Một 1 FIT2), EPTC giữ ~51% tiền; HTKD chia 25-31% LN thuỷ điện cho cá nhân",2026-11-20,dd_TTA_20261120`

## 6. Định giá (MÙ giá thị trường)

### 6.1 Chi phí vốn
r = **13,5%**. Lãi huy động 12T hiệu dụng `deposit_rate_vn.effective_deposit_rate('2026-11-20')` = **7,40%** (CCTG 12M 02/11; Big-4 6,8%) = mức neo 03/11 ⇒ không điều chỉnh. β=1.
Độ nhạy (kịch bản B): −100bp **9.322** · −50bp 9.072 · 0 **8.836** · +50bp 8.611 · +100bp **8.398** đ/cp (β=0,5: 9.072 / 8.611 ở ±100bp) — ~±250 đ/50bp.

### 6.2 DCF FCFE vòng đời HỮU HẠN từng nhà máy (`model/dcf_tta.py`) — không terminal vô hạn
Giả định (đều **ước lượng** trừ khi ghi nguồn): DT thuỷ điện nền 330 tỷ/năm (9T 279,8 [Q3]), chi phí tiền mặt 80 tỷ +3%/năm; sau 2036 −15% giá (hết PPA chi phí tránh
được, TT 54/2025); dòng tiền thuỷ điện tới **2060**. Mặt trời: Bầu Ngứ 98 GWh, Núi Một 1 85 GWh (web công ty 80–98), suy giảm 0,5%/năm, FIT tới 2039/2040, sau đó
1.100 đ/kWh (≈ khung năm 2026 miền Nam/Trung 1.104–1.293 [Bobby §3b]) tới hết đời 25 năm (2044/2045). Kiểm chéo: EBITDA mô hình 2027 = 588 vs 2025 thực 583 [KT25].
G&A 22; capex duy trì 30 (+60 thay inverter 2032); thuế 6% →2030, 10% 2031–34, 20% sau; HTKD 12% EBITDA thuỷ điện; quỹ 6% LNST + 2; trả gốc 280 tỷ 2027 rồi
đều tới 2033; lãi 8,4%. Cộng: tiền + tiền gửi 150,9; Phương Mai 99,4 (giá gốc − DP); cho vay bên liên quan 15; phải thu EPTC vượt mức ~330.

| Khoản cộng/trừ trong BASE (B) | Giá trị | Cơ sở dữ liệu + nguồn |
|---|---|---|
| Hồi tố Bầu Ngứ FIT1→FIT2 | −394 tỷ (trả 5 năm) | KL TTCP nhóm 14 dự án (nguoiquansat 01/01/2024); (2.408−1.826)×98 GWh×6,9 năm |
| Bầu Ngứ FIT2 từ 2027 | −57 tỷ DT/năm | như trên |
| Phải thu EPTC vượt mức | +330 tỷ | [Q3 tr.18] 399,6 − ~70 bình thường (ước lượng) |
| Phước Hoà 95,7 tỷ | **0** | Tăng trưởng KHÔNG có hợp đồng đầu ra kiểm được (không cơ chế giá tích năng [Bobby §2d], chưa chủ trương đầu tư) ⇒ luật 20/11: không tự cho NPV=0; A tính theo sổ sách |
| HTKD chia LN cá nhân | −12% EBITDA thuỷ điện | [Q3 tr.22, 26] 31,0 tỷ 2025 |
| Phương Mai 1 | +99,4 | [Q3 tr.20], liên kết, không có BCTC riêng để định giá |
Phân loại capex: không có capex TUÂN THỦ đã biết; inverter 2032 = **sửa chữa** (không tạo doanh thu mới, tính đủ chi phí); Phước Hoà = tăng trưởng không đầu ra kiểm được.

### 6.3 Kịch bản & độ nhạy
- A 12.679 · B 8.836 · C 1.800 ⇒ **trọng số 8.040** (0,25/0,50/0,25 — xác suất chủ quan, neo Bobby S1/S2: P(chốt trước 06/2027)=0,35, P(có hồi tố | chốt)=0,75).
- **Giá mặt trời giảm đồng đều** (không hồi tố / có hồi tố): 0% **12.143** · −25% **9.243 / 6.605** · −51% **6.226 / 846**.
- Thuỷ điện ±20% (B): 6.823 / 8.836 / 10.826. Lãi +1pp (B): 8.614. Không thu được phải thu vượt (B): 6.988.

### 6.4 Hai nền giá trị (hiển thị, không đổi tâm)
| Nền | Giá trị | đ/cp |
|---|---|---|
| V_ngắn: LN thuộc cổ đông chuẩn hoá 186,6 tỷ (2025: 231,6 − HTKD 31,0 − quỹ 14,0; trung vị 3 năm LNST = 2025) × (1 − 2%/7,4%) / (13,5% − 2%) | 1.184 | **6.632** |
| V_dài: DCF FCFE kịch bản B / trọng số | 1.578 / 1.436 | **8.836 / 8.040** |
| C4 (chỉ theo dõi, chưa qua tiêu chí khoá trước 2/4 chân trời): CFO3 TB 268 (355,0; 236,3; TTM 212,9) − min(capex 30, KH 205) = 238 | 1.511 | 8.460 |
| D2 (chỉ theo dõi, 0/9 nền qua): 268 − 7% (trung vị capex/DT 13 peer [BQ]) × 761 = 215 | 1.365 | 7.644 |
D = |ln(6.632/8.040)| = **0,19** < ln2 ⇒ không cờ. ⚠️ V_ngắn dựa trên LN ghi đủ FIT ⇒ phóng đại nếu bị tính lại giá; CFO (C4/D2) đã phản ánh một phần việc EPTC giữ tiền.

### 6.5 Bội số & comp [BQ 2026Q3, tham chiếu]
| | P/E | P/B | EV/EBITDA | ROE3Y | Nợ/VCSH |
|---|---|---|---|---|---|
| **TTA** | 7,5 (LN thuộc CĐ: 8,9) | 0,74 | 6,1 | 8,9% | 0,70 |
| Thuỷ điện ít nợ (SHP, VSH, TMP, SBH, S4A, CHP, AVC) | 7,6–12,3 | 1,9–2,5 | 6,3–7,8 | 16–25% | 0,04–0,59 |
| IPP đòn bẩy/tái tạo (GEG, HDG, PC1, REE) | 6,8–10,4 | 0,63–1,08 | 5,2–7,9 | 7–12% | 0,66–1,51 |
TTA định giá ngang nhóm IPP đòn bẩy (ROE ~9% ⇒ P/B<1 là hợp lý), không phải nhóm thuỷ điện chất lượng. EV/EBITDA 6,1 trên EBITDA ghi đủ FIT; EBITDA kịch bản B ~531 ⇒ ~6,9x.

### 6.6 Chiết khấu thanh khoản
ADV 62 phiên tới 19/11: trung vị **79.900 cp**, TB 146.263 cp; trung vị giá trị **0,94 tỷ/phiên** [BQ]. Free float ~30% (ước lượng: TNHH XD Trường Thành 23,63% + phía
ông Trần Huy Đức 23,26% (báo chí, chưa đối chiếu BCTN) + nhóm Đinh Quang Chiến 20,04% [TX]). Vị thế 1–2 tỷ ở 10–20% tham gia ⇒ **5–21 phiên** để thoát.
Chiết khấu **10% (ước lượng — không có cơ sở thực thi độc lập ⇒ chỉ là độ nhạy)**: 0% ⇒ 8.040 · 10% ⇒ **7.240** · 15% ⇒ 6.830. Sizing tiền lệ ≤0,5–1,0% NAV; với ADV này nên ≤0,5%.

## 7. Cổ đông, người liên quan, quản trị — WARNING

- **Nhóm Đinh Quang Chiến** (Phó CT HĐQT Lideco/NTL; CT HĐQT Thuỷ điện Trà Xom) gom liên tục T6–T8/2026 (9 báo cáo thay đổi sở hữu [web cty]): sau GD 25/08/2026
  Trà Xom 1,24% + Chiến **15,30%** + Lideco 3,17% + Đinh Thu Thuỷ 0,33% = **20,04%** [TX]. Mục đích không công bố. ⇒ có thể là tranh giành kiểm soát (catalyst hai chiều).
- **Cựu CT Trần Huy Đức**: [KT25 tr.3] "đã hoàn tất thủ tục chuyển giao quyền và nghĩa vụ đối với nợ phải trả của ông Trần Huy Đức cho các đối tượng có liên quan …
  đang thực hiện thủ tục chuyển giao quyền và nghĩa vụ đối với tài sản của ông Trần Huy Đức" — lý do không nêu; không suy diễn. Thay đổi HĐQT: miễn nhiệm Trần Huy
  Thiệu (đơn 21/04/2026, ĐHĐCĐ 23/04), CBTT trễ ⇒ HOSE nhắc nhở.
- **Giao dịch bên liên quan**: cho Cty TNHH Xây dựng Trường Thành (cổ đông lớn, GĐ là TV HĐQT) vay **15 tỷ** (lãi 9T 0,42 tỷ ≈ ~3–4%/năm, thấp hơn lãi TTA đi vay 8,4%)
  [Q3 tr.18, 29]; trả trước 4 tỷ + phải thu dịch vụ 0,32 tỷ Cty TNHH ĐT Xây lắp Trường Thành; **thuê biệt thự Imperia Garden của Chủ tịch Nguyễn Thị Ngọc** làm VPĐD
  [HĐQT 29/06/2026], giá thuê không công bố; 5 tỷ nhận từ bà Nguyễn Thị Thanh cho Phước Hoà [Q3 tr.22]. Quy mô nhỏ so với VCSH, nhưng chiều đi là có lợi cho người nội bộ.
- **"Scandal di cư"**: rủi ro FIT có thể di cư sang (a) hồi tố tiền đã nhận, (b) phải thu không thu được, (c) tài sản đảm bảo BIDV (Bầu Ngứ/Núi Một 1 thế chấp 1.126 + 294 tỷ)
  ⇒ áp lực covenant. Bầu Ngứ thêm vấn đề giấy phép Luật Thuỷ lợi (nongnghiepmoitruong.vn).
- **Đại Trường Thành Holdings**: KHÔNG có trong danh sách bên liên quan của BCTC Q3/2026 [tr.29]; không tìm thấy văn bản gốc liên kết ⇒ **không xác lập liên quan**.
- Kiểm toán: Nhân Tâm Việt (NTV, công ty nhỏ), 2025 chấp nhận toàn phần; tiếp tục 2026 [NQ, CV 18/06/2026]. Cổ tức: 0% 2025; không cam kết. Room ngoại: chưa đo.

## 8. Mốc khoá trước + điều kiện đổi nhận định (CẢ HAI chiều)

| Mốc | Ngày chấm | Đổi TỐT hơn nếu | Đổi XẤU hơn nếu |
|---|---|---|---|
| M1 BCTC Q4/2026 | ~30/01/2027 | Phải thu EPTC **giảm** < 300 tỷ (EVN trả phần giữ) ⇒ P(A) lên, tâm +~1.000 | Phải thu EPTC > 450 tỷ hoặc trích dự phòng/giảm DT ⇒ P(C) lên |
| M2 Văn bản xử lý FIT sai (Bobby S1) | 30/06/2027 | Giữ FIT cho dự án đã COD/chỉ điều chỉnh tương lai ⇒ tâm → ~12.000 | Hồi tố + trần chuyển tiếp ⇒ tâm → ~1.800–4.000, rủi ro tái cấp vốn |
| M3 Thời hạn/điều khoản HTKD | BCTN 2026 (~04/2027) | HTKD có hạn/được mua lại ⇒ +~300–500 đ | Mở rộng HTKD sang nhà máy khác |
| M4 Phước Hoà | bất kỳ | Có cơ chế giá công suất + chủ trương đầu tư + vốn đối ứng rõ | Cam kết vốn chủ lớn bằng nợ khi FIT chưa xong |
| M5 Nhóm Đinh Quang Chiến | liên tục | Chào mua công khai/tham gia HĐQT với kế hoạch cổ tức | Tranh chấp kiểm soát làm tê liệt quản trị |
| M6 Lãi huy động 12T | liên tục | −50bp ⇒ +~250 đ | +50bp ⇒ −~225 đ |

## Phụ lục — Checklist Bobby (21 mục) — trạng thái
1 Loại giá: ✅ (FIT1/FIT2, KL TTCP) · 2 Ghi nhận DT: ⚠️ ghi đủ FIT, tiền thu ~51% · 3 Sản lượng/cắt giảm: ❌ không công bố · 4 PPA điều khoản: ❌ · 5 Đấu nối: ❌ ·
6 BESS: không thấy kế hoạch · 7 Khung 2026: không áp cho NM có PPA · 8 Đất: ✅ Bầu Ngứ 73,7 ha, Núi Một 1 48,9 ha (GCN), ⚠️ giấy phép thuỷ lợi · 9 Ngưỡng 30MW: ✅ tách
(NH2 >30; NH2A, Pá Hu ≤30) · 10 Hết HĐ 2027-30: không có NM nào (NH2A ~2036) · 11 Sản lượng ≥10 năm: ❌ · 12 Pass-through: ✅ DT "thuế phí liên quan bán điện" 32,2 tỷ 9T
ghi cả DT và giá vốn (bên mua trả) · 13 Lưới 110kV: ❌ chưa đo · 14 Thiên tai: không thấy tổn thất 2026 · 15 Giấy phép: ❌ · 16 Tích năng pháp lý: ⚠️ chưa chủ trương ·
17 Vốn tích năng: ❌ chưa công bố · 18 Dư nợ/lịch trả: ✅ §4 · 19 DSCR xấu: ✅ §4 · 20 Bảo lãnh/cho vay liên quan: ✅ §7 · 21 Độ nhạy: ✅ §6.

## Phụ lục E — đính chính / giới hạn
- Chưa qua fundamental-skeptic (Mike gọi sau). Chưa ghi `dd_price_zones.json`.
- Không đọc thuyết minh BCTC soát xét 6T/2026 và Q2 chi tiết (đã tải `src/`); số 9T lấy từ Q3 luỹ kế.
- Sản lượng kWh từng nhà máy, giá bán thực, thời hạn HTKD, danh sách CCA 173: **chưa kiểm được**.
