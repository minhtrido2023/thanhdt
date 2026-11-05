# DD REDO — HPG (CTCP Tập đoàn Hòa Phát) · mùa BCTC Q3/2026 · 05/11/2026 · job `Taylor_20261105_014125`

> NGHIÊN CỨU, trung dung. Không phải khuyến nghị.
> **Nguồn:** BCTC GỐC hợp nhất + riêng mẹ Q3/2026 (ký 29/10), soát xét 6T/2026, KT25 — đã có ở `dd_HPG_20261031/src/`, KHÔNG tải lại. Số BCTC và đường LN kịch bản lấy từ DD v3 31/10 (`dd_HPG_20261031/REPORT.md`, `calc/hpg_valuation_v2.py`; đã qua fundamental-skeptic CONFIRMED medium + 2 vòng GAPS).
> Sector read Bobby (mù): `kb/data_registry/market-state/sector_read_thep_20261031.md`.
> **Tính lại:** `$DNA_PYEXE -I calc/hpg_redo.py > calc/hpg_redo_out.txt` (tất định, md5 trùng 2 lần). Mọi số §1, §6–§8 từ `calc/hpg_redo_out.txt` / `SUMMARY.json`.

## 1. Kết luận (số chuẩn hoá liên mã)

| Chỉ số | Giá trị |
|---|---|
| Giá 04/11/2026 [BQ] | **21.700** (P/B 1,23x BVPS 17.624) |
| r | **13,50%** (neo 13,5% @ 7,40% `cctg_12m(2026-11-02)`; 04/11 không đổi) |
| Tâm TRƯỚC / SAU CK thanh khoản | 16.361 / **16.337** |
| P10 / P50 / P90 SAU CK | **9.261 / 16.706 / 23.577** (trước: 9.274 / 16.731 / 23.612) |
| Giá vs tâm / P10 / P90 | **+32,8%** / +134,3% / −8,0% |
| **Nhãn** | **TRONG vùng** — nhưng ở phần TRÊN (giữa P75 19.680 và P90) |

Một câu: Q3 gấp đôi thật ở cấp vận hành (DQ2), nhưng ở r 13,5% kịch bản trung lập chỉ đáng ~16,7k vì ROE terminal sau khi hết ưu đãi thuế (11,8%) thấp hơn r. Giá 21.700 ngụ ý **r ≈ 11,27%** (tâm sau CK = giá) — tức thị trường đang chiết khấu HPG thấp hơn khung r 13,5% khoảng 220bp.

## 2. Giả thuyết kiểm chứng (BCTC gốc; không đổi vì chưa có BCTC mới)

| Giả thuyết | Số | Kết quả |
|---|---|---|
| "LN gấp đôi" | LNST Q3 8.265 (+106%); lõi Q3 ~7,7–8,0k (+116–120% so lõi Q3/25 ~3,6k); 9T +104% gồm lãi thoái vốn BĐS 4.929 trước thuế một lần ⇒ lõi 9T ≈ 19,2k ± 0,4k | ĐÚNG ở lõi Q3; 9T thổi bởi một lần |
| "Biên tăng nhờ spread" | Biên gộp Q3 19,16% vs 16,72%; spread HRC thô đi ngang ~240–250 USD/t; khối lượng Q3 +54% | SAI: nhờ khối lượng/hấp thụ chi phí cố định DQ2 + mix HRC |
| "P/E 6,5x là rẻ" | P/E TTM báo cáo 6,5x; lõi sau trích quỹ ~8,0x | NỬA ĐÚNG: rẻ theo LN đỉnh, không rẻ theo ROE chuẩn hoá thuế 20% |

## 3. Chất lượng LN · bảng cân đối · dòng tiền
- **Một lần 9T:** lãi chuyển nhượng công ty con BĐS 4.929 (Q1), LN khác thuần Q3 286,6 (không thuyết minh). Lãi vay vốn hoá giảm 1.877 (2025) → 162 (6T/26): KH + lãi vay DQ2 đã vào P&L.
- **Nợ ròng 30/09:** vay 105.737 − tiền 6.853 − HTM 39.276 = **59.608** (cận dưới); không trừ tiền gửi cầm cố 8.294 ⇒ 67.902 (**1,54x EBITDA lõi TTM 44.235**); + phải trả NB dài hạn 3.829 ⇒ 1,62x. Dưới ngưỡng cờ 3x.
- **CFO 9T 20.936** = 1,09x LN lõi, có hoàn VAT một lần +5.136; bỏ ra ⇒ 0,82x. Capex 9T 14.607.
- **Dự án đang đầu tư:** XDCB 16.113 (DQ 11.146), cam kết vốn ~19.472. **Luật dự án mới:** RI dựng trên BV0 theo giá sổ (XDCB ở giá vốn), capex tương lai không bị trừ như "mất" ⇒ NPV 0 ngầm định trong base.
- Chi tiết + trang: `dd_HPG_20261031/REPORT.md` §3–§4.

## 4. Cổ đông · room · thanh khoản
- Nhóm ông Trần Đình Long ~35,46% ⇒ free float ~64,5% (ước lượng). NN 21,8%, room còn 27,2% [WEB 30/10]. Cầm cố: vay NH bảo đảm một phần bằng cổ phiếu HPG của cá nhân (số lượng không công bố).
- **Thanh khoản [BQ 250 phiên tới 04/11]:** ADV trung vị **602,1 tỷ**; σ ngày 1,65%; Amihud 1,50e−05. Vị thế 5 tỷ thoát 0,08 phiên (10%) / 0,04 (20%). **CK @5 tỷ = 0,15%** (1 tỷ 0,07%; 10 tỷ 0,21%). Phương pháp chung liên mã.

## 5. Pháp lý / quản trị — WARNING (nặng, không loại)
- Kiểm toán Deloitte: KT25 + soát xét 6T chấp nhận toàn phần (hạ khỏi danh sách cờ). Không tìm thấy khởi tố/xử phạt 2025–26 ("không tìm thấy" ≠ sạch).
- **⚠ WARNING TLSH (hệ Đại Quang Minh):** 3 lớp phơi nhiễm — cổ phần TLSH 9.915 tỷ (1.920 tiền + 7.995 bằng cổ phần BĐS HP ở ~10.271 đ/cp ≈ mệnh giá, phương án trước là 32.000 đ/cp); 26,55% BĐS HP; thành viên liên danh BT Đại lộ cảnh quan sông Hồng. Giao dịch hoán đổi không thuyết minh như bên liên quan; bên mua khoản lãi 4.929 không công bố; ~1,4–1,9 nghìn tỷ góp vốn chưa rõ đích. HĐQT đủ thẩm quyền (2,8–3,1% TTS < 35%); cờ nằm ở công bố thông tin và giá.
  Theo luật: không trừ vào base (RI trên sổ). **Đuôi trái:** mất 50% khoản TLSH = **−587 đ/cp**; rủi ro chuyển giá trị 0 – ~1.500 đ/cp (ước lượng, DD cũ).
- Ưu đãi thuế: thời hạn không công bố; nếu DQ2 bị xếp "mở rộng" có rủi ro truy thu (CV 377/TCT-CS). Thuế terminal 20% đã đưa vào mô hình.

## 6. Định giá
### 6.1 Mô hình
RI: BV0 = VCSH mẹ 30/09 148.796; LNST mẹ Q4/26 + 2027–29 theo kịch bản; payout 20%; ROE terminal **suy ra nhất quán** = LN 2029 × (1+g) × (0,80/0,88) / BV 2029 (hết ưu đãi thuế từ 2030); giá trị tại 30/09 dồn tới 04/11. **r = 13,50%.**
**Terminal (luật 03/11 — vốn mới NPV 0):** nếu ROE_T < r thì RI terminal **không tăng** (g_RI = 0): không giả định HPG tái đầu tư vĩnh viễn ở ROE dưới chi phí vốn. Bản cũ cho g 5% áp lên RI âm (khuếch đại phá giá trị). Kịch bản giữ nguyên v3 — toàn bộ **(ước lượng)**:

| | XẤU (w 0,25) | TRUNG LẬP (w 0,50) | TỐT (w 0,25) |
|---|---|---|---|
| LNST mẹ Q4/26 · 2027 · 2028 · 2029 | 5,5k · 16k · 15k · 16k | 7,0k · 26k · 26k · 27k | 8,0k · 31k · 33k · 35k |
| Nội dung | AD HRC bị cắt sau rà soát, spread 150–200 (mức 2022–23) | 15 tr t, LN/tấn 1,87 → ~1,73 | LN/tấn ~2,0, 15,5–16 tr t |
| ROE terminal sau thuế 20% / g | 7,9% / 3% | 11,8% / 5% | 14,3% / 5% |
| **RI @13,5%** | **9.769** (P/B 0,55x) | **16.731** (0,95x) | **22.215** (1,26x) |

Cơ sở dữ liệu kịch bản XẤU: LN/tấn 2022–23 ~1,05 tr đ [DD cũ], rà soát AD QĐ 1902 đang diễn ra. Kỳ vọng **16.361** trước CK ⇒ **16.337** sau CK. Độ nhạy trọng số: (0,15/0,50/0,35) 17.606; (0,35/0,50/0,15) 15.117.

### 6.2 Lưới P10–P90
n = 45 = 3 kịch bản (w 0,25/0,50/0,25) × hệ số đường LNST (≈ LN/tấn) **0,8/0,9/1,0/1,1/1,2** × dịch g terminal **−1/0/+1 pp** (đều); r cố định 13,5%; cùng quy tắc terminal NPV 0. File ô `calc/grid_hpg.csv`.

| | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| TRƯỚC CK | 9.274 | — | 16.731 | — | 23.612 |
| SAU CK | **9.261** | 12.290 | **16.706** | 19.680 | **23.577** |

### 6.3 Độ nhạy r theo lãi huy động 12T (trước CK, kỳ vọng)

| Δ lãi huy động | β = 0,5 | β = 1,0 |
|---|---|---|
| −100bp | 13,00% → 17.287 (+926; +5,7%) | 12,50% → **18.311 (+1.950; +11,9%)** |
| −50bp | 13,25% → 16.813 (+452; +2,8%) | 13,00% → 17.287 (+926; +5,7%) |
| +50bp | 13,75% → 15.931 (−431; −2,6%) | 14,00% → 15.520 (−842; −5,1%) |
| +100bp | 14,00% → 15.520 (−842; −5,1%) | 14,50% → **14.792 (−1.569; −9,6%)** |

**r ngụ ý bởi giá:** tâm sau CK = 21.700 khi r = **11,27%** (lãi huy động phải giảm ~220bp ở β 1).

### 6.4 Đối chiếu (không vào tâm)
EV/EBITDA lõi TTM hiện tại **5,31x**; EV/EBITDA 5x trên EBITDA 2027 theo kịch bản = **22.025 đ/cp** (≈ giá). Comp VN 11,1x / khu vực 7,8x tính trên EBITDA đáy chu kỳ (DD cũ). Nghĩa là giá đang khớp với "bội số thị trường đang trả", còn RI ở khung r 13,5% thấp hơn — khoảng cách nằm ở r và ROE terminal sau thuế 20%, không ở lợi nhuận gần.

## 7. Mốc khoá trước + điều kiện đổi nhận định (HAI chiều)
Giữ nguyên H1–H10 (DD 31/10 §9, P đã khoá): H1 biên gộp Q4/26 vs 13,85% (↑ ≥ 18%; ↓ < 13,85%); H2 LNST lõi Q4/26 (↑ ≥ 8.000; ↓ < 5.500); H3 CFO 2026 trừ hoàn VAT / LN lõi (↑ ≥ 1,0x; ↓ < 0,7x); H4 AD HRC sau rà soát (↓ < 20% hoặc huỷ, chấm 31/03/2027); H5 biên Q1/27 vs 15,81%; H6 thị phần thép XD 2026; H7/H9/H10 thuyết minh TLSH, 1.500 tỷ liên danh, bên mua lãi 4.929 trong BCTC kiểm toán 2026 (15/04/2027).
- **LÊN** khi ≥ 2 trong {H1↑, H2↑, H5↑} và H4 không ↓ ⇒ trọng số 0,15/0,50/0,35 ⇒ tâm trước CK **17.606**; H7↑ + H9↑ bỏ đuôi TLSH. Lãi huy động −100bp ⇒ +1.950.
- **XUỐNG** khi H1↓ và H5↓ (2 quý liên tiếp biên thấp hơn cùng kỳ) hoặc H4↓ ⇒ 0,35/0,50/0,15 ⇒ **15.117**; H7↓/H9↓/H10↓ ⇒ thêm đuôi TLSH −587 đ/cp và nâng WARNING. Lãi huy động +100bp ⇒ −1.569.
- Nhãn sang TRÊN vùng nếu giá > 23.577 (cách giá 04/11 +8,6%); DƯỚI vùng nếu < 9.261.

## 8. Phụ lục — ĐỔI gì so với DD cũ (31/10) và vì sao — **LỆCH >10%**

| Mục | Cũ (31/10, v3) | Mới (05/11) | Lý do |
|---|---|---|---|
| Ke / r | **11,83%** = rf chuẩn hoá 6,75% + β đo 0,915 × ERP nội địa 5,55% | **13,50%** | luật 03/11: r neo 13,5% @ lãi huy động 12T hiệu dụng; không theo β riêng mã |
| Terminal RI | g 5%/3% áp lên mọi RI (kể cả âm) | ROE_T < r ⇒ g_RI = 0 | luật dự án/vốn mới NPV 0 |
| Tâm | **20.200** = (2·RI 19.221 + EV/EBITDA 5x)/3 | **16.337** = kỳ vọng RI thuần sau CK | định nghĩa chuẩn hoá liên mã; EV/EBITDA → đối chiếu |
| Lệch tâm | | **−19,1%** vs tâm cũ 20.200; **−15,0%** vs RI cũ 19.221 | **nguyên nhân chính = r**: cầu nối RI 19.221 (tái lập đúng) → dồn tới 04/11 19.428 (+207) → r 13,5% với terminal cũ 15.285 (**−4.143**) → terminal NPV 0 16.361 (+1.076) → CK −24 ⇒ 16.337; bỏ chân EV/EBITDA giải thích phần còn lại so với 20.200 |
| Vùng | 18.000–22.500 (tham chiếu tự chọn) | P10–P90 lưới n=45: 9.261–23.577 | định nghĩa lưới chuẩn hoá |
| Nhãn | TRONG vùng, nửa trên (+4% vs tâm, giá 21.000) | TRONG vùng, phần trên (+32,8% vs tâm, giá 21.700) | r cao hơn ⇒ tâm thấp hơn |
| CK thanh khoản | không định lượng | 0,15% @5 tỷ | luật 03/11 |
| Kịch bản / đường LN | | giữ nguyên | không có BCTC mới; không quét tin 31/10–04/11 |

## 9. Lỗ hổng mở
- **Luật r 13,5% đồng nhất mọi mã** — HPG β đo 0,84–0,93 (DD cũ) không được dùng; nếu khung cho phép β riêng mã thì giá trị cao hơn (ở Ke cũ 11,83% với terminal NPV 0: 19.882, đã dồn tới 04/11). Cần user/Mike xác nhận cách đọc luật.
- EBITDA slide lệch 361 tỷ chưa giải thích; free float 64,5% chỉ trừ nhóm TĐL; chưa quét tin 31/10–04/11/2026. Chưa qua fundamental-skeptic vòng này.
