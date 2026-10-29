# DD — PVT (Tổng CTCP Vận tải Dầu khí / PV Trans, HOSE) · 2026-10-29 · job `Taylor_20261029_035644`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua, không lệnh, không wire. User quyết.
> Nguồn: **[Q3]** = text trích từ PDF "BCTC hợp nhất Q3/2026 + CV 983 NTDK-TCKT" (`src/q3_pvt_hopnhat_text.txt`, CHƯA soát xét;
> bảng trong text bị xáo cột → **ráp lại bằng hằng đẳng thức**, mọi ô đã ráp đều qua self-check = 0 trong `out.txt`);
> **[TMxx]** = thuyết minh số xx trong cùng file; **[CV]** = CV giải trình 983 ngày 28/10/2026; **[BQ]** = `tav2_bq.ticker`
> (giá tới 28/10) / `ticker_financial` (LNST mẹ theo quý tới 2026Q2); **[DNSE]** = `dnse_api` secdef/latest_trade 10:59 29/10;
> **[web]** = báo chí (nguồn thứ cấp, §12). Phép tính: `calc.py` → `out.txt`. Số tự đặt gắn **(ước lượng)**.
> Nền ngành: Bobby `kb/data_registry/market-state/sector_read_oil_gas_shipping_20261029.md` (đọc TRƯỚC khi kết luận; không sửa).
> **KHÔNG có**: PDF gốc (11,8MB), BCTC bán niên 2026 soát xét, BCTC năm 2025 kiểm toán (ý kiến kiểm toán) — không tìm được qua web
> trong phiên này; pvtrans.com/ir stale (2021–23). Mọi kết luận về ý kiến ngoại trừ/nhấn mạnh = **chưa kiểm**.

## 0. Kết luận

**Verdict: NON tại 21.300 (giá sàn, 10:59 29/10/2026 [DNSE]; tham chiếu 22.850).** Lợi nhuận tăng là **THẬT và chất lượng khá**
(CFO 9T 2.733 tỷ = 1,73× LNST; không có lãi bán tàu; nợ ròng giảm 2.694 → 619 tỷ), nhưng:
(i) đây là **đỉnh lợi nhuận** — 9T đã đạt 132% kế hoạch LNST năm, ngành đang "cuối đỉnh" theo Bobby (cả hai nhánh BIMCO kéo cước
2027 xuống); (ii) **Q3 đã giảm so với Q2**: LNTT −26,5% QoQ, biên gộp vận tải 20,7% vs 24,6% bình quân 6T; (iii) giá hiện tại
= PE TTM 7,2 trên LNST đỉnh, PB 1,12 **cao hơn trung vị PB lịch sử 0,91** [BQ 2018–]; (iv) giá trị kỳ vọng có trọng số
**≈ 18.000 (ước lượng)**, tức hiện tại cao hơn ~18%. Không phải ca fear-buy (§9).

**Vùng giá:** chỉ đáng chạy lại DD ở **≤ ~15.300** (biên an toàn 15% dưới giá trị kỳ vọng) — giá chạm ngưỡng **KHÔNG tự đổi verdict**.

| Tiêu chí (`calculated_fear_state_backstop.md`) | Áp dụng? | Phán quyết | Bằng chứng |
|---|---|---|---|
| §2 (scandal cá nhân) | **Không** | n/a | Không có khởi tố/điều tra; chỉ thay TGĐ 2 lần + chủ tịch đăng ký bán 200k cp rồi KHÔNG bán (§10) |
| §2.5 #1 Chu kỳ, không cấu trúc | Có | ✅ ngành chu kỳ | Bobby: CYCLICAL 0,55 / ADMIN_GATED 0,30 / STRUCTURAL 0,15 |
| §2.5 #2 Sống sót qua đáy | Có | ✅ | Nợ ròng 619 tỷ vs EBITDA 9T 3.838 tỷ; CFO 2.733 tỷ [out.txt] |
| §2.5 #3 Leader chi phí thấp | Một phần | ⚠️ không kiểm được | Lớn nhất nội địa, nhưng không có số chi phí/ngày tàu; đội tàu VN già (~17,7 năm, Bobby) |
| §2.5 #4 Sàn tài sản PB ≲ 1 | Có | ❌ | PB 1,12 trên VCSH mẹ 9.856 tỷ; trung vị lịch sử 0,91 |
| §2.5 "Đáy chưa tới" | **Ngược chiều** | ❌ | Đây là **đỉnh** chu kỳ lợi nhuận, không phải đáy — §2.5 được thiết kế cho mua ở ĐÁY |

## 1. Kiểm chứng số Mike đã đọc

| Mike đọc | Kiểm | Kết quả |
|---|---|---|
| LNST HN Q3 489.354.181.631 vs 348.963.594.761 (+40,23%) | [CV] = [Q3] KQKD mã 60 | ✅ khớp tới đồng (diff 0) |
| 9T 1.581.763.465.461 vs 984.853.277.829 (+60,61%) | [CV] = [Q3] | ✅ |
| Q2 DT 5.714, 6T LNTT 1.366 [báo chí] | 9T − Q3: LNTT 6T = **1.366,8**; DT 6T 9.915 ⇒ Q1 DT 4.201 | ✅ khớp; BQ Q2 DT 5.713,8 |
| 9T vượt KH LNST 1.200 | LNST HN 9T = **131,8%** KH; LNTT 132,0% KH 1.500; DT 94,1% KH 16.500 | ✅ (KH là số **hợp nhất**: báo chí ghi Q1 LNST 387 = 32% KH) |
| Lý do "tàu mới + hiệu quả khai thác" | §2 | ✅ một phần — doanh thu vận tải +40% là khối lượng/đội tàu; biên **không** tăng ở Q3 |
| BCTC Q3 chưa soát xét | [Q3] TM3: số so sánh KQKD/LCTT là Q3/2025 chưa kiểm toán; BCĐKT đầu kỳ đã kiểm toán | ✅ |

**Self-check (out.txt):** 4 cột KQKD × 5 hằng đẳng thức = 0; TTS − (NPT+VCSH) = 0 hai kỳ; TTS − (TSNH+TSDH) = 0; tổng 4 bộ phận
= DT/GVHB = 0 cả 4 cột; tiền đầu kỳ + LCT thuần + FX = tiền cuối kỳ BCĐKT (0); LNST mẹ + CĐTS = LNST.
**Lệch ngày ký:** BCĐKT ký 28/10/2026; trang thuyết minh cuối ký **20/10/2026**; LCTT "20…/10" (OCR mờ); KQKD OCR "1…/10";
CV 983 ngày 28/10. ⇒ BCTC hoàn tất ~20/10, CV + bộ công bố ngày 28/10. Ghi nhận, không phải cờ đỏ tự thân (ký nhiều ngày khác nhau).
**Lệch nhỏ BQ vs BCTC:** LNST mẹ Q1+Q2 theo BQ = 871,9; 9T − Q3 theo BCTC = 897,2 (**+25,2 tỷ**) — có thể H1 điều chỉnh sau soát xét;
**không xác định từ text**.

## 2. (A) Tăng trưởng từ đâu — theo bộ phận [TM34]

| Bộ phận | DT Q3/26 vs Q3/25 | LN gộp Q3 | Biên Q3 | DT 9T YoY | LN gộp 9T | Biên 9T |
|---|---|---|---|---|---|---|
| **Vận tải** | 3.515 vs 2.504 (**+40,4%**) | 728 vs 529 | **20,7% vs 21,1%** | +34,9% | 2.220 vs 1.434 (+54,8%) | 23,2% vs 20,2% |
| Kho nổi (FSO) | 152 vs 143 | 43 vs 39 | 28,4% | −2,7% | 130 vs 179 (**−27,5%**) | 29,9% vs 40,1% |
| Thương mại | 1.678 vs 1.209 | 5,0 vs 5,4 | 0,3% | +50,3% | 18,5 vs 12,3 | 0,4% |
| Khác | 265 vs 563 | 17 vs 10 | 6,5% | −24,6% | 31 vs 46 | 5,7% |
| **Tổng** | 5.610 vs 4.419 (+26,9%) | 794 vs 584 | 14,1% | +34,2% | 2.399 vs 1.672 (+43,5%) | 15,5% |

- **Vận tải 6T/2026 (suy ra):** DT 6.067, LNG 1.492, biên **24,6%** → Q3 biên **20,7%**; LNG Q3 thấp hơn bình quân quý 6T **2,4%**.
- **Đọc:** Q3 tăng YoY gần như hoàn toàn nhờ **khối lượng** (DT vận tải +40%, biên đi ngang YoY). Phần "cước cao" thể hiện ở **H1**
  (biên 24,6%), **không** ở Q3 — dù cước giao ngay quốc tế lập đỉnh 06/10 (Bobby §3.1). Phù hợp nhãn ADMIN_GATED: phần lớn doanh
  thu không bám cước giao ngay. Giả thuyết cho biên Q3 giảm (chi phí nhiên liệu VLSFO 959 USD/t, chuyến chạy dài, dry-dock): **suy đoán**,
  BCTC không tách.
- **Q3 vs Q2:** DT −1,8%, LNTT **−26,5%** (613 vs 834). Thiếu BCTC Q2 riêng nên **không xác định** khoản nào làm Q2 cao (LN gộp vận tải
  Q2 tách khỏi Q1 không có trong text).
- **Tách dầu thô / sản phẩm / LPG / nội địa vs quốc tế: BCTC KHÔNG trình bày** (bộ phận chỉ theo 4 mảng trên; không có bộ phận địa lý).
- **"Tàu mới":** nguyên giá TSCĐ phương tiện vận tải +979,6 tỷ trong 9T (mua trong kỳ) [TM12]; năm 2025 vốn có đợt mua lớn (DT Q2/25
  nhảy 2.789 → 4.313 [BQ]) — số tàu/dwt **không có trong BCTC**.

## 3. (B) Chất lượng lợi nhuận [TM26–29, LCTT]

| Khoản | 9T/26 | 9T/25 | Ghi chú |
|---|---|---|---|
| Lãi tiền gửi | 251,0 | 157,6 | Trên tiền+HTM bình quân ~5.646 tỷ ⇒ ~5,9%/năm. **12,7% LNTT**; bền chừng nào còn giữ tiền |
| Lãi/lỗ tỷ giá ròng | **−38,7** | −10,2 | Lãi 30,3; lỗ thực hiện 64,9 + đánh giá lại 4,1 (ráp cột, xem caveat) |
| Lãi liên kết (PTSC POS 49%) | 18,1 | 15,9 | Nhỏ |
| Thu nhập khác ròng | 93,5 | 64,5 | Bồi thường 42,1; khác 55,6; **thanh lý TSCĐ chỉ ~0,05 tỷ** |
| **Lãi bán tàu** | **≈ 0** | ≈ 0 | Mục 8 Bobby (lãi thanh lý một lần) **không áp dụng** 9T/26 — kiểm được |
| Hoàn nhập dự phòng (LCTT mã 03) | **−85,4** | +9,5 | Phi tiền mặt; ~4,3% LNTT — xem TT99 dưới |
| LNTT lõi (trừ lãi gửi, LK, khác ròng) | **1.617,5** | 977,4 | **+65,5%** — tăng trưởng lõi thật |
| LNST CĐTS (NCI) | 309,5 | 213,0 | 19,6% LNST HN; LNST **mẹ** 9T 1.272,3 (+64,8%) |

⚠️ **Đổi chuẩn mực kế toán (TT99/2025 + TT43/2026, áp dụng phi hồi tố từ 01/01/2026)** [Q3 TM3–4]: công ty **ngừng trích trước
chi phí sửa chữa lớn tàu (dry-dock)**; số dư dự phòng cũ xử lý theo chuyển tiếp, chi phí mới vốn hoá vào "chi phí chờ phân bổ" rồi
phân bổ. Hệ quả: dự phòng dry-dock **541,0 → 427,1** tỷ, chi phí sửa chữa lớn trả trước DH **241,5 → 391,1** tỷ. Năm 2025 có khoản trích
trước vào GVHB, năm 2026 không có ⇒ **biên 9T/26 không so sánh được hoàn toàn với 9T/25**, có thiên lệch tăng. **Độ lớn không xác
định từ text** (cần thuyết minh H1 soát xét hoặc BCTC năm 2025). Cận dưới thấy được: hoàn nhập 85,4 tỷ phi tiền mặt. Khoản "điều
chỉnh khác" LCTT 9T/25 = **155,7 tỷ** (9T/26: 8,7) cũng chưa giải thích được — có thể liên quan trích trước cũ (suy đoán).
→ Đây là câu hỏi số 1 cho fundamental-skeptic / bước tiếp theo.

## 4. (C) Bảng cân đối, dòng tiền [BCĐKT, LCTT, TM20]

| | 30/9/2026 | 31/12/2025 |
|---|---|---|
| Tiền + tương đương | 2.060,2 | 1.902,0 |
| Tiền gửi HTM ngắn hạn | 4.285,0 | 3.044,0 |
| Vay NH (gồm dài hạn đến hạn) | 1.420,8 | 1.394,2 |
| Vay DH | 5.543,7 | 6.245,4 |
| **Nợ ròng** | **619,3** | **2.693,6** |
| VCSH mẹ / CĐTS | 9.855,6 / 3.007,4 | 8.673,0 / 2.817,2 |
| Phải thu KH NH | 1.913,2 (+26%) | 1.517,8 |
| Phải trả PVN tiền mua tàu 104.000 DWT | 232,7 (77,6 NH + 155,1 DH) | 232,7 |

- **CFO 9T 2.733,4** (vs 2.235,4) dù phải thu tăng 905; capex 947,0; **FCF 1.786** (vs 1.297). Vay trả ròng 674 tỷ. Cổ tức tiền mặt
  của mẹ 9T/26 ≈ 0 (trả cổ phiếu 10%), mã 36 LCTT ≈ 0 — ráp cột, độ tin trung bình.
- **Capex/KH = 0,52**: khấu hao 1.829 tỷ/9T nhưng capex chỉ 947 ⇒ FCF hiện tại **cao hơn mức bền** nếu đội tàu cần thay thế (đội tàu
  già; capex thay thế chuẩn hoá ≈ KH là giả định thận trọng — **ước lượng**). Mục 7 Bobby (dồn mua trước khi hết miễn VAT NK tàu
  31/12/2026, mua ở đỉnh giá tàu cũ): **chưa thấy trong 9T** (XDCB dở dang chỉ 62,4 tỷ, trả trước người bán 184 tỷ); Q4 cần theo dõi.
- **Nợ theo đồng tiền / lãi cố định–thả nổi / covenant: KHÔNG có trong text** (TM20 chỉ liệt kê ngân hàng). Bên cho vay gồm
  Kasikorn (TL), OCBC Singapore, Cathay United, CTBC, HSBC, Woori, Shinhan ⇒ phần lớn có thể là **USD** (**suy đoán**). Tiền gốc USD
  nắm giữ: **30,65 triệu USD** (31/12/25: 20,42 triệu) [TM23c] ⇒ phòng ngừa một phần.
- Thu xếp vay "Cổ đông" (cổ đông thiểu số công ty con) ~190 tỷ; vay PVN có dòng đến hạn — chi tiết từng dòng **không ráp chắc chắn**.

## 5. (D) Doanh thu, khách hàng, hợp đồng [TM4, TM33]

- Ghi nhận doanh thu dịch vụ theo phần việc hoàn thành; cho thuê hoạt động theo đường thẳng; **doanh thu cho thuê tàu nhận trước**
  101,1 tỷ (73,2 đầu năm) [TM18].
- **Tập trung PVN:** doanh thu từ đơn vị thuộc PVN 9T **3.482,5 tỷ = 22,4%** DT (9T/25: 2.373,0); riêng Q3 **1.780,8 = 31,7%** DT Q3
  (Q3/25: 901,8). **Phải thu thương mại từ đơn vị PVN 1.144,7 tỷ** (31/12: 497,8; **+130%**) ≈ 60% phải thu KH. Đây là phần lớn
  nguyên nhân phải thu tăng 905 tỷ trong LCTT. Không phải rủi ro tín dụng cao (cùng hệ sinh thái), nhưng là **WARNING về vốn lưu động**.
- **TC/thuê chuyến/giao ngay, danh sách HĐ, lịch đáo hạn 2026–27: KHÔNG có trong BCTC** (mục 6.A1–2 Bobby — biến quan trọng nhất —
  **chưa kiểm được**). Gián tiếp: biên vận tải Q3 không tăng dù cước đỉnh ⇒ tỷ trọng giao ngay quốc tế thấp (**suy luận**).
- FSO: 9T LNG −27,5% (biên 40,1% → 29,9%) — mục 19 Bobby (rủi ro HĐ FSO theo đời mỏ): có dấu hiệu suy giảm, chi tiết HĐ không có.

## 6. (E) Cổ đông, cổ phiếu, thanh khoản

- **PVN 51%** (263,6 triệu cp) [TM22b]. **Cổ phiếu lưu hành 516.918.938** (31/12/25: 469.931.235) — phát hành ~47 triệu cp cổ tức
  10% (kết thúc 08/06/2026 [web]), vốn điều lệ 5.169,2 tỷ ✅ khớp tin "trên 5.100 tỷ".
- **EPS:** BCTC dùng 516,9 tr cp (EPS 9T 2.461); EPS 9T/25 công bố 1.643 **chưa điều chỉnh hồi tố** cho cổ phiếu thưởng (đúng ra ≈ 1.493
  trên 516,9 tr cp) ⇒ tăng trưởng EPS thật ≈ **+65%**, không phải +50%. Mọi định giá trong file dùng **516,9 tr cp**.
- Lịch sử pha loãng thường xuyên (cp lưu hành 323,7 → 356,0 → 469,9 → 516,9 triệu 2023–2026 [BQ]) — chủ yếu cổ tức cổ phiếu, không
  pha loãng giá trị, nhưng **giá theo BQ chưa chắc điều chỉnh đủ** (BQ `Close`=`Price` trong 2026).
- **Thanh khoản:** ADV20 **171,5 tỷ**, ADV60 143,2 tỷ [BQ]. Sizing tiền lệ 0,5–1,0% NAV không có vấn đề capacity.
- Room ngoại: **chưa kiểm** (không có trong BCTC; không tra được trong phiên).

## 7. (F) Định giá tại 21.300 [out.txt]

| Chỉ số | Giá trị |
|---|---|
| LNST mẹ TTM (9T/26 + Q4/25 BQ) | 1.538,2 tỷ → EPS 2.976 → **PE 7,16** |
| Q3/26 năm hoá | EPS 2.903 → PE 7,34 |
| BVPS mẹ | 19.066 → **PB 1,12** |
| EV (vốn hoá 11.010 + nợ ròng 619 + CĐTS sổ sách 3.007) | 14.637 tỷ; **EV/EBITDA (9T năm hoá) 2,86** |
| PVT lịch sử 2018– [BQ] | PE p25/med/p75 **7,5 / 8,5 / 9,7**; PB **0,82 / 0,91 / 1,01** |
| Peers 28/10 [BQ] | PVP PE 6,5 PB 1,00 · VOS 4,8 / 0,79 · VTO 5,1 / 0,72 · GSP 8,8 / 0,80 |

Tanker niêm yết khu vực: **không lấy được số tin cậy** trong phiên (không có nguồn sống) — bỏ, không đoán.
PE TTM < p25 lịch sử nhìn "rẻ", nhưng đó là **PE trên lợi nhuận đỉnh chu kỳ** — chính cái bẫy §2.5 #4 cảnh báo; PB thì **đắt hơn** lịch sử.

**Kịch bản 2027 (LNST mẹ, PE — tất cả là ước lượng):**

| Kịch bản | P | LNST mẹ | Lý do | PE | Giá trị/cp |
|---|---|---|---|---|---|
| Xấu | 0,35 | 1.000 | ≈ 2025 (1.039): cước về mức 2023–25/BIMCO giữa 2027, KH tàu mua 2025–26 đè lên, lãi tiền gửi giảm khi dùng tiền | 6,5 (de-rate đỉnh) | 12.575 |
| Cơ sở | 0,45 | 1.250 | Giữ khối lượng tàu mới (đội tàu lớn hơn 2025), biên vận tải về ~20% như Q3 nhưng mất phần cước H1 | 8,0 | 19.345 |
| Tốt | 0,20 | 1.500 | Q3 năm hoá giữ được (Hormuz K1/K3 kéo dài, TC gia hạn ở đỉnh) | 8,5 | 24.665 |
| **Kỳ vọng** | | | | | **≈ 18.040 (−15% vs 21.300)** |

Độ nhạy: trọng số 0,25/0,50/0,25 và PE cơ sở 8,5 ⇒ ≈ 19.600 — **vẫn dưới giá hiện tại**. Vùng mua (biên an toàn 15%): **≤ ~15.300**
(≈ PB 0,80, PE 6,3 trên kịch bản cơ sở). Kịch bản dùng LNST mẹ; không cộng lại phần CĐTS.

**Phản ứng giá quanh sự kiện:** 20/10 24.200 → 28/10 22.850 (−5,6% trước CV) → 29/10 **sàn 21.300** (−6,8%, KL khớp 1,46 tr cp lúc 10:59
[DNSE]). Đỉnh năm 27.910 (06/03), đầu năm 17.090 [BQ]. Thị trường bán **sau** số Q3 dù YoY +40% ⇒ đang chiết khấu QoQ giảm và đỉnh
cước (**suy luận**; không loại trừ yếu tố thị trường chung — chưa kiểm VNINDEX hôm nay).

## 8. Đối chiếu 20 mục DD của Bobby (§6 sector read)

| # | Mục | Trạng thái | Kết quả |
|---|---|---|---|
| 1 | Tỷ trọng TC/voyage/spot/COA | ❌ không có trong BCTC | Gián tiếp: biên Q3 không theo cước ⇒ spot thấp (suy luận) |
| 2 | HĐ TC, lịch đáo hạn 2026–27 | ❌ không có | Cần BCTN/IR |
| 3 | Khách cùng hệ thống, bên liên quan | ✅ | PVN 22,4% DT 9T, 31,7% Q3; phải thu PVN 1.145 tỷ (+130%) |
| 4 | Nội địa vs quốc tế | ❌ | Không có bộ phận địa lý |
| 5 | Bảng đội tàu, tuổi | ❌ | Chỉ có KH phương tiện 3–20 năm [TM4] |
| 6 | Lịch dry-dock, hạch toán | ⚠️ một phần | **Đổi hạch toán TT99** (vốn hoá thay trích trước) — §3; lịch không có |
| 7 | Mua/đóng tàu, giá đỉnh, VAT 31/12/26 | ⚠️ | 9T mua 979,6 tỷ phương tiện; chưa thấy dồn mua; Q4 theo dõi |
| 8 | Lãi thanh lý tàu | ✅ | ≈ 0 trong 9T/26 |
| 9 | Khấu hao, thay đổi ước tính, impairment | ⚠️ | TM5 nêu xem xét thời gian hữu dụng mỗi kỳ, không công bố thay đổi; impairment chưa có |
| 10 | CII/EEXI, tàu >15–20 tuổi | ❌ | Không có |
| 11 | Nợ theo đồng tiền, cố định/thả nổi | ❌/⚠️ | Không có; bên cho vay nước ngoài ⇒ có thể USD (suy đoán) |
| 12 | Tỷ giá | ✅ | Lỗ ròng ~38,7 tỷ 9T; giữ 30,65 tr USD tiền |
| 13 | Lãi vay/EBITDA, nợ ròng/EBITDA chuẩn hoá | ✅ | Lãi vay 9T 345,6/EBITDA 3.838 = 9%; nợ ròng/EBITDA ≈ 0,1 — an toàn kể cả EBITDA giảm một nửa |
| 14 | Tiền, cổ tức, dùng LN đỉnh | ✅ | Tích tiền + trả nợ; cổ tức cp 10% |
| 15 | Nhiên liệu, war-risk | ❌ | Không tách |
| 16 | Off-hire, sự cố, tranh chấp | ⚠️ | TM5: dự phòng nghĩa vụ hợp đồng "một số vấn đề đang xử lý với đối tác" — không định lượng; bồi thường thu 42 tỷ |
| 17 | Trừng phạt | ❌ | Không có thông tin |
| 18 | Cabotage | — | Thuộc ngành (Bobby) |
| 19 | FSO | ⚠️ | LNG kho nổi 9T −27,5% |
| 20 | TA nhà máy lọc dầu 2027 | ❌ | Không có |

**8/20 mục không kiểm được từ BCTC** — đó là khoảng trống lớn nhất của DD này (cần BCTN 2025 / tài liệu NĐT).

## 9. Vì sao KHÔNG phải ca fear-buy (§2 / §2.5)

§2 (scandal cá nhân): **không khớp** — không có khởi tố. §2.5: ngành **chu kỳ** (✅) và DN **sống sót tốt** (✅), nhưng §2.5 là
khung mua ở **đáy** chu kỳ với sàn PB ≲ 1. PVT đang ở **đỉnh** lợi nhuận, PB 1,12 > trung vị lịch sử. Gò PVT vào §2.5 là sai khung.
Nếu cước sập 2027 và giá về PB ≲ 0,8 trong khi CFO còn dương → **khi đó** mới là ứng viên §2.5.

## 10. Pháp lý / quản trị — WARNING (luật fleet 27/09: phân tích bình thường, chỉ cảnh báo)

- ⚠️ **Thay TGĐ 2 lần trong 4 tháng**: Trần Ngọc Nguyên (bổ nhiệm 21/04/2026) xin từ nhiệm, miễn nhiệm từ **01/07/2026**, vẫn ở HĐQT;
  **Nguyễn Thanh Bình** (nguyên Chủ tịch PV GAS 04–07/2026) làm TGĐ từ **03/08/2026** — chính là người ký BCTC Q3 [web: Báo Pháp Luật,
  CafeF, Báo Đầu Tư]. Lý do từ nhiệm không công bố. Rủi ro: thay đổi chiến lược đầu tư tàu/phân phối LN — chưa có dấu hiệu.
- ⚠️ "Chủ tịch muốn bán ở vùng đỉnh": thực tế Chủ tịch **Phạm Việt Anh đăng ký bán 200.000 cp (0,043%) 11/03–09/04/2026 và KHÔNG bán**
  (24hMoney 13/04/2026). Tiêu đề "vùng đỉnh" là diễn giải báo chí; quy mô không trọng yếu. Không tìm thấy bài Vietstock gốc.
- Phát hành cổ tức cp 10% (~47 triệu cp) đã hoàn tất — đã phản ánh trong EPS (§6). Không phải pha loãng giá trị.
- Phải thu khó đòi cũ liên quan **Huỳnh Thị Huyền Như** (PVTrans Pacific, từ 2011) 73,1 tỷ — đã dự phòng 100% từ 2012 [TM8].
- Ý kiến kiểm toán BCTC 2025 / soát xét H1/2026: **không có trong tay** — chưa kiểm.

## 11. Điều kiện đổi verdict + mốc khoá trước

| Mốc | Cần thấy | Hướng |
|---|---|---|
| BCTC năm 2026 (≈ T1–T3/2027) | Thuyết minh định lượng tác động TT99; lợi nhuận Q4 ≥ Q3 (biên vận tải ≥ 21%) | Q4 < 300 tỷ LNST mẹ ⇒ củng cố NON; tác động TT99 > 150 tỷ ⇒ hạ kịch bản |
| **Bobby F1 — 31/03/2027** (BDTI trung vị ~4.200) | Nếu BDTI ≤ 4.200 mà biên vận tải PVT Q1/27 vẫn ≥ 20% ⇒ ADMIN_GATED đúng, lợi nhuận bền hơn | nâng kịch bản cơ sở lên 1.400 ⇒ FV ~20k (ước lượng) |
| **Bobby F2 — 30/09/2027** (BDTI ~2.800) | LNST mẹ 9T/27 vs 9T/26 1.272 | ≤ 900 ⇒ đúng kịch bản xấu |
| Giá | **≤ ~15.300** | Chạy lại DD (không tự QUALIFY) |
| Công bố TC/đội tàu (BCTN 2025, ĐHCĐ 2027) | ≥ 60% ngày tàu là TC dài hạn đến 2028 | Giảm trọng số kịch bản xấu |
| Q4/2026 capex | Mua tàu lớn ở đỉnh trước 31/12/2026 | Cờ đỏ (KH cao nhiều năm, mục 7 Bobby) |

## 12. Điểm yếu tự nhận (cho fundamental-skeptic tấn công)

1. Bảng trong text bị xáo — KQKD/BCĐKT/LCTT/bộ phận đã khớp hằng đẳng thức nên tin cao; **TM20 (vay theo ngân hàng), TM27 (chi tiết
   chi phí tài chính), TM30 (chi phí theo yếu tố), TM31 (thuế)** ráp không chắc ⇒ không dùng số từ đó ngoài tổng. TM31 9T có số PBT
   1.113,2 không khớp KQKD 1.980 — **lỗi trình bày hoặc lỗi ráp**, không dùng.
2. Phân bổ cột dự phòng dry-dock DH (23,6 vs 274,0) suy từ tổng NPT DH — khớp tổng, nhưng thứ tự dòng là suy luận.
3. LNST mẹ Q4/2025 lấy từ BQ (265,9), không phải BCTC kiểm toán.
4. Kịch bản LNST 2027 và PE mục tiêu là **ước lượng**; không có dữ liệu TC/đội tàu để neo.
5. Q2/2026 không có BCTC riêng ⇒ không giải thích được vì sao Q2 LNTT 834 cao hơn Q3 613.
6. Chưa kiểm VNINDEX phiên 29/10 để tách phản ứng giá riêng PVT.

## 13. Nguồn web

- Báo Pháp Luật 03/07/2026 — TGĐ từ nhiệm, cổ tức cp, KH 2026: https://doanhnhan.baophapluat.vn/tong-giam-doc-pvtrans-pvt-xin-tu-nhiem-sau-hon-2-thang-giu-chuc.html
- Tân TGĐ: https://doanhnhan.baophapluat.vn/pvtrans-pvt-co-tan-tong-giam-doc.html · https://cafef.vn/pvtrans-co-tan-tong-giam-doc-188260804205041383.chn · https://nongnghiepmoitruong.vn/pvtrans-bo-nhiem-tan-tong-giam-doc-d824819.html
- Chủ tịch đăng ký bán, không bán (24hMoney 13/04/2026): https://24hmoney.vn/news/chu-tich-pvt-thoi-ban-co-phieu-khi-gia-da-ha-nhiet-c1a2771633.html
- Mekong ASEAN: https://mekongasean.vn/tong-giam-doc-pvtrans-tu-nhiem-sau-hon-2-thang-nham-chuc-56903.html

---
## 14. ĐÍNH CHÍNH SAU PHẢN BIỆN (fundamental-skeptic, 29/10/2026 — Mike ghi; mục 0–13 giữ nguyên để audit)

**Verdict skeptic: CONFIRMED cho phân loại NON; lớp ĐỊNH GIÁ bị REFUTED (confidence medium).** Các mục dưới ĐÈ lên §0 (iii)(iv), §7, §11:
1. **PB sai gốc.** PB 1,12 dùng VCSH MẸ (9.856); trung vị 0,91/p25 0,82 và PB peers lấy từ BQ tính trên VCSH GỒM NCI (BVPS 2025Q4 × 469,93tr cp = 11.490,2 = 8.673,0 + 2.817,2). Cùng gốc: PB = 11.010/12.862,9 = **0,86** (giữa p25 0,82 và trung vị 0,91). ⇒ lý do (iii) "PB đắt hơn lịch sử" **SAI, bỏ**; PVT rẻ hơn lịch sử cả PE (7,16 < p25 7,5) lẫn PB.
2. **Kịch bản chồng bi quan.** Cơ sở 1.250 mâu thuẫn lý do "biên ~20% như Q3" (Q3 năm hoá ≈ 1.500 = kịch bản TỐT); xấu 1.000 ≈ LN 2025 mà PE 6,5 trong khi BQ cho PE 8,80 ngày 31/12/2025 trên chính LN đó (cắt cả LN lẫn PE). Tính lại (skeptic): xấu PE 8,5 → 16.444; cơ sở 1.450 @ 8,0 → 22.441; trọng số cũ ⇒ **FV ≈ 20.800 (−2% vs 21.300)**; cơ sở PE 8,5 + trọng số 0,25/0,50/0,25 ⇒ ≈ 21.200. **Kết luận trung thực: ≈ giá hợp lý, KHÔNG có biên an toàn** (không phải "đắt 15%"). FV khoảng **19,4–21,2k (ước lượng)**.
3. **Vùng chạy lại DD ≤15.300 KHÔNG tin cậy** (suy từ FV 18.040 lỗi). Tính lại: −15% của ~20k ≈ **~17.000 (ước lượng)**, vẫn KHÔNG tự đổi verdict.
4. **NON vẫn đúng** vì khung §2.5: đỉnh chu kỳ lợi nhuận (❌ "đáy chưa tới"), drawdown từ đỉnh 52 tuần −23,7% < ngưỡng T1 >35%, PB mẹ >1. Giá rẻ trên bội số nhưng trên LN đỉnh.
5. Số lõi khớp src (LNST mẹ Q3 375,13 / 9T 1.272,29; CFO 2.733,35; 516.918.938 cp; VCSH 12.862,9, NCI 3.007,4). Q3 giảm QoQ thật: BQ LNST mẹ Q2 552,9 → Q3 375,1 (−32%). CFO KHÔNG bị thổi bởi vốn lưu động (WC ròng −375; CFO trước WC 3.816).
6. Bổ sung Bobby mục 7: `calculated_fear_state_backstop.md` ghi PVT Logistics xin phê duyệt phát hành cổ phần mở rộng đội tàu ngày 05/10 (rủi ro mua tàu ở đỉnh + pha loãng NCI) — DD ghi "chưa thấy" là thiếu, cần theo dõi.
7. Còn mở: TT99 dry-dock (lượng hoá khi có BCTC 2026), 8/20 mục Bobby không kiểm được, ý kiến kiểm toán 2025/soát xét H1 chưa có.
