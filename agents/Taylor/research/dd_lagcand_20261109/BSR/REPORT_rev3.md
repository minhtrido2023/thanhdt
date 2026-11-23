# DD — BSR (Tổng Công ty Lọc hoá dầu Việt Nam, NMLD Dung Quất) · **rev3 · 23/11/2026** · job `Taylor_20261123_050001` (resume `Taylor_20261123_003452`)

Bản trước: `REPORT.md` (rev2 09/11, tâm 17.496, skeptic DD_GENERAL r1 22/11 = **INCONCLUSIVE**, `skeptic/r1.json`). Bản này KHÔNG ghi đè rev2.
Chỉ nghiên cứu, không đặt lệnh/wire. Định giá **mù giá thị trường**: giả định khoá ở `calc/assumptions_rev3.json` (md5 `f12ab0822ab47c6cae9eb745a68d3929`, `calc/LOCK_prerun_md5_rev3.txt`) TRƯỚC khi chạy mô hình; rev3 không truy vấn giá mới — giá tham chiếu vẫn là 26.250 (BQ 06/11, cùng file `calc/px_bsr.csv` của rev2), chỉ dùng để dán nhãn.
Nhãn nguồn: **[BCTC]** đọc từ PDF gốc · **[QĐ968]** · **[BQ]** · **[UL]** ước lượng/giả định tự đặt · **[Bobby]** sector read mù 09/11.

## 0. Kết luận

| (đ/cp) | rev2 (09/11) | **rev3 trước CK** | **rev3 sau CK (vị thế 5 tỷ)** | rev3 sau CK (40 tr) |
|---|---|---|---|---|
| Tâm (kỳ vọng có trọng số, 243 kết cục) | 17.496 | 16.186 | **16.112** | 16.180 |
| P10 / P50 / P90 | 13.093 / 17.350 / 23.345 | 11.438 / 16.007 / 22.013 | **11.385 / 15.933 / 21.911** | 11.433 / 16.000 / 22.004 |
| Nhãn @ 26.250 (06/11) | TRÊN vùng | TRÊN vùng | **TRÊN vùng** (+63% trên tâm, +20% trên P90) | TRÊN vùng |

- **Vùng giá rev3:** rẻ (luật 4, 0,85×tâm) ≤ **13.695** · hợp lý **11.400–21.900** (P10–P90) · trên 21.900 là trả cho biên lọc cao kéo dài.
- **Tâm giảm −1.384 đ/cp (−7,9%)** so với rev2: (i) dự án mở rộng có phần **tuân thủ** → dòng tiền ra (kỳ vọng tỷ trọng 30,25% ⇒ −1.885 đ/cp); (ii) sửa lệch TA hai chiều + bỏ phần cộng +370 (+501 đ/cp ròng). Nhãn không đổi.
- **Giá 26.250 ngụ ý:** Ke **4,67%** (vs 13,5%), hoặc LN lõi vĩnh viễn **11.048 tỷ/năm = 3,2 lần** lõi 2023-25 (3.493) ≈ GRM cao hơn CƠ SỞ **+5,6 USD/thùng mãi mãi**. Bobby xếp STRUCTURAL p=0,15.
- **Một câu:** LN 9T/2026 kỷ lục là đỉnh chu kỳ (Hormuz + crack diesel + lãi tồn kho); giá trị nội tại ≈ tiền ròng 9.012 + nhà máy ở biên chuẩn hoá ~5.800 + LN vượt 2026Q4–2028 ~2.000 − phần tuân thủ của dự án mở rộng ~1.900 (kỳ vọng). **DD không ủng hộ mua theo cơ bản ở giá tham chiếu.**
- **Sizing (V8):** chuẩn sleeve 2–4% NAV/mã chỉ áp khi giá ≤ vùng hợp lý; ở TRÊN vùng DD đề xuất **0% discretionary**. Nếu LAG vẫn mua theo luật cơ học thì đó là cược PEAD/đà giá, theo luật sleeve LAG, không phải DD.

## 1. Đính chính so với rev2 — từng hạng mục skeptic r1

| # | Hạng mục skeptic r1 | Xử lý rev3 | Loại | Ảnh hưởng tâm (đ/cp, sau CK) |
|---|---|---|---|---|
| 1 | **Thiếu phân loại tăng trưởng/tuân thủ dự án mở rộng 39.004,5 tỷ** (killer objection) | Tải QĐ 968/QĐ-BSR 28/3/2024 (`src_rev3/`, md5 `821ab1af…`). Tách: tăng công suất + nâng cơ cấu sản phẩm = tăng trưởng (NPV0, V4a); cụm môi trường "lộ trình bắt buộc" = tuân thủ (dòng tiền ra, V4b/D3). Tỷ trọng chi phí không công bố ⇒ trục 0,10/0,40/0,75 (p 0,50/0,35/0,15) — mục 3.2 | (a) phân loại có nguồn; (b) tỷ trọng là kịch bản | **−1.885** (kỳ vọng 30,25%) |
| 2 | Nguồn gốc: `src/` + file calc vắng; E1–E4 chưa đối chiếu PDF | `src/` đã khôi phục, md5 6 PDF khớp `src/SRC_md5.txt`. **Đọc lại PDF gốc (ảnh trang trong `rev3/png/`)**: E1 TM24/25 tr.34, E2 TM7 tr.22 + BS tr.4, E3 TM5 tr.20, E4 BS tr.5 — **khớp toàn bộ** (bảng mục 2) | (a) | 0 |
| 3 | CƠ SỞ cao hơn neo +370 tỷ/năm (chiều đắt) | **Bỏ** +370: CƠ SỞ neo đúng lịch sử bóc lãi | (a) | −550 (ước theo skeptic) |
| 4 | TA đếm hai lần (chiều rẻ) | Cửa sổ 2023-25 chứa TA5 trọng 1/3 vs chu kỳ ~4 năm: chi phí TA5 = TB(2023,2025) − 2024 = **6.230,5 tỷ** [BQ] ⇒ lõi +TA/12 = **+519,2**; LN vượt 2027 (đã trừ trọn TA6) cộng lại TA/4 = **+1.557,6** để không đếm hai lần | (a) | +1.051 (gộp với #3: **+501** ròng) |
| 5 | "Capex 3.155 tỷ chưa giải thích" | **Đóng:** khớp trả trước người bán ngắn hạn tăng 372 → 3.009 (+2.637), trong đó 2.601,1 ứng China Chengda 2.120,1 + Beijing Petrochemical Engineering 481,1 [BCTC TM7] — đã ghi sổ ở E2 | (a) | 0 |
| 6 | Nguồn vốn 15.601,8 tỷ VCSH chưa nêu | QĐ968 mục 13: VCSH/vay 40/60; VCSH từ khấu hao + LN, **phát hành CP chỉ khi không đủ**; vay ECA + NH thương mại. Tiền ròng 45.126 tỷ > 15.601,8 ⇒ base **không pha loãng**; phát hành = kịch bản xác suất thấp, không vào base | (a) | 0 |
| 7 | Chưa trích ý kiến kiểm toán FY2025 | BCTC KT 2025 **không có trong thư mục**; tìm web 23/11 không ra bản gốc ⇒ **không kiểm chứng được**; ghi `audited_fy_missing=true` (D5). Có soát xét 6T/2026 Deloitte (chấp nhận, nhấn mạnh quyết toán CPH). Ảnh hưởng ước: thấp với giá trị (BCTC Q3/26 + 6T soát xét là nguồn số), cao với cổng sổ (không vào Bậc 1 watch) | (c) | 0 |
| 8 | Quyết toán CPH / nộp NSNN chưa lượng hoá | Giữ **WARNING**, không vào base (luật pháp lý). Không có số công bố ⇒ **không kiểm chứng được** | (c) | 0 |
| 9 | Tin pháp lý sau 03/11 chưa quét | Đã tìm web 23/11 (2 truy vấn): không thấy tin T11/2026 về CPH/MBV/BSR. **Không kiểm chứng đầy đủ** (công cụ tìm web hạn chế, không phải CBTT HOSE) | (c) | 0 |

Luỹ kế: rev2 17.496 → bỏ +370 & sửa TA (#3+#4, chưa trừ tuân thủ) **17.997** → trừ tuân thủ kỳ vọng (#1) **16.112**.

## 2. Đối chiếu số liệu với PDF gốc (BCTC HN Q3/2026, `src/BCTC_HN_Q3_2026.pdf` md5 `7be32745…`)

| Khoản (tỷ) | Mô hình | PDF gốc | Trang |
|---|---|---|---|
| Tiền + TĐT (110) / HTM (123) / Vay NH (321) | 1.758,4 / 56.892,8 / 13.525,0 | 1.758,392 / 56.892,821 / 13.525,007 | BS tr.4–5 |
| Tiền ròng | **45.126 (9.012 đ/cp)** | — | tính |
| XDCB (252) / Trả trước dài hạn (212) | 2.525,9 / 546,3 | 2.525,899 / 546,307 | BS tr.4 |
| Quỹ KHCN (344) / KTPL (323) / NCI (429) | 844,0 / 441,6 / 32,0 | 843,965 / 441,645 / 31,961 | BS tr.5 |
| Ứng trước nhà thầu (TM7) | 2.601,2 | 2.120,083 + 481,054 = 2.601,1 | tr.22 |
| MBV tạm dừng giao dịch (TM5) | 2.735,6 | 2.735,630 | tr.20 |
| DT tài chính 9T/25 (TM24) | lãi gửi 940,7 + TG 521,7 + cổ tức 0,28 | 940,735 + 521,735 + 0,280 = 1.462,750 | tr.34 |
| Chi phí vay / lỗ TG 9T/25 (TM25) | 199,4 / (TG ròng 335) | 199,369 / 186,653 ⇒ TG ròng 335,1 | tr.34 |

LN năm 2019–25 và số CP 5.007,3 tr: [BQ], model tự assert lại từ `calc/bq_bsr_fin.csv`; skeptic r1 đã tự kiểm khớp.

## 3. Định giá (mù giá)

### 3.1 Khung (giữ rev2, chỉ đổi các mục đính chính)
Giá trị = (a) nhà máy: LN lõi (không gồm lãi tiền gửi/tỷ giá) / Ke, RONIC = Ke, trừ phần thuế 10%→20% sau 2039 · + (b) PV LN VƯỢT nền 2026Q4–2028 · + (c) tiền ròng + XDCB + khoản ghi sổ mở rộng (NPV0 phần tăng trưởng) − quỹ KHCN − quỹ KTPL − NCI · + (d) giải phóng WC vượt (trục) · **− (e) phần TUÂN THỦ của dự án mở rộng (mới)**.

| Tham số | XẤU | CƠ SỞ | TỐT | Cơ sở |
|---|---|---|---|---|
| Trọng số | 0,30 | 0,50 | 0,20 | Bobby 09/11 (K2+ADMIN / K1 / STRUCTURAL+K3); bản đối xứng 0,275/0,45/0,275 |
| LN lõi chuẩn hoá (tỷ/năm) | 2.611,9 | **4.011,9** | 6.111,9 | **rev3:** neo 2023-25 sau bóc lãi/tỷ giá 4.784,7 − 1.292 = 3.492,7 [BQ+BCTC TM24/25] + TA/12 519,2 [BQ]. Bỏ +370 rev2. XẤU/TỐT giữ khoảng cách −1.400 / +2.100 (≈+1,66 USD/thùng × 1.266 tỷ) [UL] |
| ± trục LN lõi | −20/0/+20% (0,25/0,5/0,25) | | | [UL] |
| LN vượt Q4/26 · 2027 · 2028 (tỷ) | −2.000 · +557,6 · 0 | 4.000 · 5.557,6 · 1.000 | 7.000 · 13.557,6 · 5.000 | rev2 + TA/4 (1.557,6) cho 2027 (TA6 2027 tính 0,75 TA vì lõi đã gồm 1/4 TA/năm); Bobby F1–F4, D2/D3 [UL]; hệ số 0,5/1/1,5 |
| Ke (r, V1) | 13,50% | | | 13,5% + 1,0×(lãi huy động 12T hiệu dụng 7,40% `cctg_12m` 02/11 − neo 7,40% 03/11) |
| Thuế TNDN | 10% đến 2039, 20% sau | | | TM thuế HN Q3/26 (QĐ 952/QĐ-TTg) |
| **Tỷ trọng tuân thủ dự án mở rộng** | 0,10 (p 0,50) · 0,40 (p 0,35) · 0,75 (p 0,15) | | | mục 3.2 |

### 3.2 Dự án nâng cấp mở rộng NMLD Dung Quất — phân loại (V4)
**Nguồn:** QĐ 968/QĐ-BSR 28/3/2024 (CBTT; bản tiếng Anh `src_rev3/bsr_2024_03_29_board_decision.docx`) + NQ 5795/NQ-BSR 06/11/2026 PL2 (tổng mức hiện hành **39.004,5 tỷ**, vay 23.402,7 / VCSH 15.601,8; KH chi 2026 7.787,3; vận hành 2028) [src].
- **Mục tiêu [QĐ968]:** (1) công suất 148 → **171 nghìn thùng/ngày (+15,5%)**; (2) sản phẩm **Euro V**; (3) đạt chuẩn môi trường **theo lộ trình bắt buộc** của Chính phủ; (4) linh hoạt dầu thô; (5) tăng hiệu quả đầu tư.
- **Phân xưởng mới:** GHDT, DHDT (xử lý lưu huỳnh xăng/diesel), ALK (alkyl hoá), HGU (hydro), SRU3/4 (thu hồi lưu huỳnh) + SWS2, ARU2 (nước chua/amine); cải hoán CDU, RFCC, NHT, ISOM, CCR, PRU…
- **Cơ cấu sản phẩm/ngày [QĐ968]:** FO 7 → **0** nghìn thùng; Jet 5,3 → 13,1; xăng 65,9 → 79,7; DO 53,2 → 59,2; propylene 462 → 685 tấn; lưu huỳnh 13 → 56,7 tấn.
- **Phân loại:**
  - **Tăng trưởng (NPV0 giá sổ, V4a):** tăng công suất + chuyển FO giá trị thấp sang Jet/xăng/PP + linh hoạt dầu thô — TẠO doanh thu.
  - **Tuân thủ (dòng tiền ra, V4b/D3):** cụm môi trường SRU3/4 + SWS2 + ARU2 (mục tiêu 3 "lộ trình bắt buộc") — không tạo doanh thu.
  - **Euro V nhiên liệu:** QCVN 01:2022/BKHCN (TT 16/2022, bắt buộc từ 15/6/2023) vẫn cho lưu thông nhiều mức chất lượng; **chưa tìm thấy văn bản bắt buộc mức 5 với nhà sản xuất** ⇒ không xếp tuân thủ ở mức 0,10; nếu trở thành bắt buộc ⇒ GHDT/DHDT/HGU tính tuân thủ (mức 0,40). Mức 0,75 = giả thuyết "phần lớn là tuân thủ" của skeptic r1.
- **Tỷ trọng chi phí từng cụm không công bố** (phụ lục tổng mức đầu tư QĐ968 không đính kèm) ⇒ các mức 0,10/0,40/0,75 và xác suất 0,50/0,35/0,15 là **[UL]**; đây là trục kịch bản, không phải số đo.
- **Cách trừ:** tỷ trọng s × (phần đã ghi sổ 5.285,2 [CIP mở rộng 2.137,7 + ứng nhà thầu 2.601,2 + GPMB 546,3] + phần còn chi 33.719,3 chiết khấu 1,5 năm ở Ke) × 0,945 (lá chắn thuế khấu hao 10% [UL]). Theo đ/cp: **s=0,10 ⇒ −626 · 0,40 ⇒ −2.504 · 0,75 ⇒ −4.695**; kỳ vọng 30,25%.
- Không có IRR/hợp đồng đầu ra kiểm được ⇒ không cho NPV dương ở phần tăng trưởng (giữ NPV0).

### 3.3 Cấu phần (đ/cp, Ke 13,5%)
Tiền ròng 9.012 · cố định (tiền ròng + CIP + khoản ghi sổ mở rộng − KHCN − KTPL − NCI) **9.884** · nhà máy XẤU 3.781 / CƠ SỞ **5.808** / TỐT 8.848 · LN vượt XẤU −284 / CƠ SỞ **1.960** / TỐT 4.662 · WC vượt 10.413 tỷ (trục 0/27%/54%) · tuân thủ kỳ vọng −1.885.
Kịch bản giữa trục (tuân thủ kỳ vọng): **XẤU 12.048 · CƠ SỞ 16.319 · TỐT 22.062**.

### 3.4 Độ nhạy (sau CK 5 tỷ)
- **r (V1) theo lãi huy động:** +100bp 15.736 (−2,3%) · +50bp 15.917 (−1,2%) · −50bp 16.321 (+1,3%) · −100bp 16.547 (+2,7%). Dải Ke nội địa 12,3–13,4% (V2) = −120bp…−10bp so với 13,5% ⇒ tâm ~16.150–16.600 (ước lượng nội suy từ các điểm trên). Nhạy thấp vì ~61% giá trị là tiền ròng + khoản ghi sổ.
- **Tỷ trọng tuân thủ cố định:** 0 ⇒ 17.997 · 0,10 ⇒ 17.373 · 0,40 ⇒ 15.504 · 0,75 ⇒ 13.323 · 1,0 ⇒ 11.765. **Nhãn TRÊN vùng ở mọi mức.**
- **Bản A (giữ lãi tỷ giá trong lõi, +402):** 16.691 (P10 11.964 / P90 22.483). **MBV mất trắng:** 15.568; bản A + MBV 16.147. Bản trọng số đối xứng: 16.647 (P90 23.114). Nếu giữ +370 rev2: 16.645. Moat WIDE giả định (RONIC 20%, g 4%): 16.920 (+808, thông tin).
- 1 USD/thùng GRM bền ≈ 1.266 tỷ LN/năm ≈ **1.870 đ/cp**.

### 3.5 Hai nền (V6) — chỉ HIỂN THỊ
- **V_ngắn** = LNST chuẩn hoá (trung vị 3 năm 2023-25 = 5.213,6 tỷ [BQ]) × (1 − g/ROE)/(r − g), g = 0 (RONIC = Ke) ⇒ **7.713 đ/cp**.
- **V_dài (FCFE DCF): không tính** — mô hình là tổng-các-phần, không phải DCF FCFE; FCFE 2026-28 bị chi phối bởi capex mở rộng 39 nghìn tỷ.
- Chênh V_ngắn vs tâm 16.112: ln(2,09) = 0,74 > ln2. **Nguồn chênh:** V_ngắn vốn hoá cả lãi tiền gửi (sau thuế ~3–4%/năm) ở Ke 13,5%, tức định giá 45 nghìn tỷ tiền ròng chỉ ~25% mệnh giá; mô hình DD cộng tiền ròng theo mệnh giá. Vùng đọc mở rộng [7.713; 21.911] — vẫn TRÊN vùng ở giá tham chiếu. Tâm/vùng/nhãn vẫn từ mô hình DD.

## 4. Cờ tự động của hệ

| Cờ | Kết luận | Lý do bằng số |
|---|---|---|
| DCF auto RICH 21.359 | **THẬT** về hướng | Tâm DD 16.112, P90 21.911 < giá 26.250 |
| PE TTM 4,74 "rẻ" | **NHIỄU** | LN TTM 27.754 tỷ ≈ 6,9–7,9 lần LN lõi 3.493–4.012; PE chuẩn hoá (vốn hoá − tiền ròng)/4.012 ≈ 21,5 |
| LAG_HI | **THẬT về số, KHÔNG BỀN** | +888% YoY do crack + tồn kho; giá sau công bố −8,7% (28/10 → 06/11) |
| ADV | **THẬT** | ADV250 trung vị 260,6 tỷ, ADV60 257,1 tỷ [BQ] |

## 5. Rủi ro & điều đổi nhận định (HAI chiều)
**Rủi ro số 1:** biên lọc mean-revert (Hormuz mở, K2 p0,35) + TA6 2027 + lỗ tồn kho; KH 2026 điều chỉnh LNST 18.579 < 9T thực 24.902 (đọc là kế hoạch hành chính, XẤU dùng Q4 −2.000 vượt nền).
**Rủi ro số 2 (mới):** tỷ trọng tuân thủ dự án mở rộng ≥ 0,40 (Euro V hoá bắt buộc / cụm môi trường đắt hơn giả định) ⇒ tâm 13.300–15.500.

**Đổi lên:** giá ≤ 21.900 ⇒ TRONG vùng; ≤ 13.695 ⇒ luật 4 · crack TE ≥ 45 bền đến Q3/2027 sau khi Hormuz mở ≥ 2 quý (~+1,5 USD/thùng ≈ +2.800 đ/cp) · BSR công bố IRR/hợp đồng đầu ra dự án mở rộng hoặc cơ cấu tổng mức đầu tư cho thấy cụm môi trường < 10% ⇒ tâm tới 17.373–17.997 · thuế NK MFN xăng dầu khôi phục 01/01/2027.
**Đổi xuống:** crack TE T3/2027 < 35 hoặc ULSD−Brent T9/2027 < 50 (F4 p0,65) · Q4/2026 lỗ ≤ −3.000 tỷ · văn bản bắt buộc Euro V nhiên liệu cho nhà sản xuất · tổng mức đầu tư tăng tiếp (36.397 → 39.004,5 đã +7,2% từ 3/2024) · nhà nước thu LN bất thường · quyết toán CPH ra số phải nộp (WARNING).

## 6. Vị thế & lợi thế cạnh tranh (5F, V5)
Làm đầy đủ 09/11/2026 (< 12 tháng) ⇒ **tái dùng** rev2 mục 6: `moat_tier = NARROW`, `moat_type = ADMIN/LOCATION`, không bền ⇒ RONIC = Ke. Kiểm nhanh 23/11: (i) ROIC_Min5Y −1,0% [BQ] không đổi ⇒ vẫn trượt điều kiện ROIC−Ke dương liên tục; (ii) dự án mở rộng (+15,5% công suất, xong 2028) nâng rào cản quy mô nhưng không đổi vị thế người nhận giá MOPS. Rủi ro số 1 của moat: Lực 6 Nhà nước (thuế NK/BVMT, lệnh chạy tối đa, PVN 92,12%). Đề xuất dòng `moat_tags.csv` giữ như rev2 (không tự sửa file).

## 7. Thanh khoản & sizing (V3, V8)
ADV250 trung vị 260,6 tỷ, σ ngày 3,34% [BQ]. CK thanh khoản σ·√(Q/ADV): 5 tỷ **0,46%** (1,9% ADV, thoát 1 phiên ở 10–20% tham gia); 40 tr 0,04%. Free float ~7,9% nhưng thanh khoản thực cao ⇒ thanh khoản không phải ràng buộc. Nhãn theo giá trị SAU CK (vị thế 5 tỷ). Sizing: xem mục 0 (0% discretionary khi TRÊN vùng; chuẩn 2–4% NAV chỉ khi về trong vùng).

## 8. Pháp lý / quản trị — chỉ WARNING (không vào base)
- Deloitte soát xét 6T/2026 chấp nhận; **nhấn mạnh** quyết toán CPH (2018) chưa được phê duyệt. FY2025 KT: không có bản gốc trong thư mục (`audited_fy_missing=true`).
- MBV (ex-OceanBank) 2.735,6 tỷ tạm dừng giao dịch; BĐH đánh giá sẽ giao dịch lại khi có quy định NHNN [TM5]. Base giữ nguyên; độ nhạy mất trắng −544 đ/cp.
- SOE PVN 92,12%; giao dịch bên liên quan lớn (PV OIL 21,9% DT 9T).

## 9. Còn mở / không kiểm chứng được
- Tỷ trọng chi phí cụm môi trường vs tăng trưởng trong 39.004,5 tỷ: **không kiểm chứng được** (phụ lục không công bố) ⇒ trục kịch bản; ảnh hưởng ±1.900 đ/cp quanh tâm (0,10 → 0,75).
- Chi phí TA6 giả định = TA5 (6.230,5 tỷ, gồm cả tác động biên chu kỳ 2024): [UL]; nếu TA6 chỉ bằng 60% TA5 thì LN vượt 2027 tăng ~2.490 tỷ (≈ +460 đ/cp sau chiết khấu 0,64 năm, ước lượng).
- Chu kỳ TA 4 năm: [UL] (TA4 2022? → TA5 2024 → TA6 2027 không đều).
- BCTC KT FY2025 + tin pháp lý T11/2026: không kiểm chứng được (mục 1 #7, #9).
- Lint `dd_assumptions_lint.py`: 24 cảnh báo (rc=0, chế độ cảnh báo) — file khoá theo định dạng rev2 cũ, chưa chuyển schema v1; 4 cảnh báo L9 là dương tính giả (`adv_312` = người mua trả trước, `adv_engineering` = ứng trước nhà thầu, không phải ADV thị trường).

## 10. File
`src/` (6 PDF, md5 khớp `src/SRC_md5.txt`) · `src_rev3/` (QĐ968, `SRC_rev3_md5.txt`) · `rev3/png/` (ảnh trang PDF đã đối chiếu) · `calc/assumptions_rev3.json` (md5 `f12ab082…`) · `calc/model_bsr_rev3.py` (md5 `d6b3e278…`, chạy 2 lần, `model_out_rev3.json` md5 `f87b20d3…` trùng) · `calc/LOCK_post_md5_rev3.txt`. Chạy: `cd calc; OMP_NUM_THREADS=1 /home/trido/thanhdt/wc_venv/bin/python -I model_bsr_rev3.py` (biến thể: `BSR_COMP_SHARE=`, `BSR_CORE_ADD=402`, `BSR_MBV_LOSS=1`).
