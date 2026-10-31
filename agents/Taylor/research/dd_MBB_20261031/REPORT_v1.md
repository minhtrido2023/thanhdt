# DD — MBB (Ngân hàng TMCP Quân đội) · v1 · as-of 31/10/2026 · job `Taylor_20261031_142133`

> NGHIÊN CỨU READ-ONLY, trung dung. Không phải khuyến nghị mua/bán, không gắn QUALIFY/NON. Khung NGÂN HÀNG (không net cash/GPM/tồn kho).
> Chưa qua fundamental-skeptic (bước 5 skill due-diligence là việc của Mike).
>
> **Nguồn gốc (đã lấy được BCTC GỐC Q3/2026)** — PDF scan tải từ `static2.vietstock.vn` (không đụng mbbank.com.vn), render pymupdf, đọc ẢNH trang:
> **[HN-Q3]** BCTC hợp nhất Q3/2026 (ký 20/10/2026, CBTT 1470/MB-HĐQT 30/10) · **[RL-Q3]** BCTC riêng Q3/2026 (ký 14/10) ·
> **[HN-Q2]/[RL-Q2]** Q2/2026 · **[HN-Q1]** Q1/2026 · **[HN-Q4/25]**, **[HN-Q3/25]**, **[HN-Q2/25]** · **[KT25]** BCTC hợp nhất 2025 kiểm toán
> (KPMG, 07/03/2026) · **[SX6T]** BCTC hợp nhất 6T/2026 soát xét (KPMG, 01/08/2026) · **[BCTN25]** Báo cáo thường niên 2025 (lớp text) ·
> **[BQ]** `tav2_bq.ticker` tới 30/10/2026 · **[NGÀNH]** `kb/data_registry/market-state/sector_read_ngan_hang_20261031.md` (Bobby, mù) ·
> **[WEB]** `src/web_facts.md` (báo/CTCK, mỗi dòng có URL + ngày, **thứ cấp**).
> Sổ đọc ảnh: `calc/notes_read.md` (số + trang). Tính toán: `python3 -I calc/mbb_calc.py > calc/mbb_calc_out.txt`.
> Đơn vị: tỷ đồng. Số tự tính ghi rõ; giả định tương lai gắn **(ước lượng)**.

## 1. Kết luận

- **Lợi nhuận tăng thật, kéo bởi khối lượng; chất lượng tài sản xấu đi TĂNG TỐC trong Q3.** LNTT Q3 10.330 (+42,5%), 9T 30.518
  (+31,9%, 77% KH 39.408) [HN-Q3]. Nhưng **nợ nhóm 2 hợp nhất +42% chỉ trong Q3** (11.990 → 17.014), **nhóm 2 NH mẹ +67% QoQ**
  (7.720 → 12.899; gấp 2,3 lần đầu năm), NPL hợp nhất 1,45% → 1,67%, **bao phủ 93,6% → 84,7% trong một quý** [HN-Q2, HN-Q3, RL-Q2, RL-Q3].
  H1 nhóm 2 chỉ +17%, nên Q3 là điểm gãy, không phải xu hướng đều.
- **NIM chưa bị nén mạnh như tiêu đề "chi phí lãi +115%" gợi ý**: NIM tự tính Q3 **4,07%** vs Q2 4,16% (−9 bp) vs Q3/25 4,02% (+5 bp).
  Lợi suất tài sản tăng 6,90% → 8,61% YoY, đủ bù chi phí lãi/TSSL 2,87% → 4,55%. Nhưng chiều QoQ đã quay xuống, và CV 9608
  (giảm lãi cho vay) chưa vào số. Q4 nghiêng giảm.
- **Cấu trúc vốn đổi chất:** tín dụng +204.109 (+18,8% YTD) được tài trợ **56% bằng giấy tờ có giá** (CCTG 140.830 → 248.416; lãi
  CCTG tới **11,18%/năm**), chỉ 36% bằng tiền gửi KH (+7,9%). Tiền gửi không kỳ hạn **giảm tuyệt đối** 339.353 → 326.389;
  tỷ trọng 36,8% → 32,8%. Đây là chi phí vốn biên cao và "dính", đúng mô tả tầng C của Bobby.
- **Vốn là ràng buộc 2027:** tăng trưởng tín dụng ~25%/năm (annualized) > khả năng tự sinh vốn ~13–15%/năm (ROE ~20% × giữ lại
  65–75%). Tier 1 riêng lẻ 9,02% (30/06, [WEB] thứ cấp), đúng ngưỡng cờ CET1 < 9% của Bobby. Đã phát hành quyền mua 805,5 triệu CP
  (+8.055 tỷ VĐL) [HN-Q3 tr.36 + WEB]; còn 200 triệu CP riêng lẻ chờ phát hành.
- **Định giá:** giá 19.300 = **P/B 1,24x** (BVPS 15.594 tại 30/09), **P/E TTM 5,97x**. Vùng tham chiếu **18.000–26.000, tâm ~22.000 (ước lượng)**.
  Giá nằm ở nửa dưới vùng (−12% so với tâm), **không rẻ rõ rệt** nếu chấp nhận Ke thị trường đang ngụ ý (14–16%). RI theo khung Ke
  12,3–13,4% của user ra 24–30 nghìn. Khoảng cách này là **chiết khấu toàn ngành**, không riêng MBB: trung vị P/B 13 NH là 1,18x.
- **Kiểm toán sạch** (KPMG: chấp nhận toàn phần 2025, soát xét 6T không ngoại trừ). Không tìm thấy vụ pháp lý/thanh tra 2025–26
  (agent web tìm, xem mục 11) ⇒ **không gắn WARNING pháp lý**. Rủi ro quản trị cần theo dõi là MBV (OceanBank cũ, lỗ luỹ kế 15.688 cuối 2024).
- **Một câu:** ngân hàng sinh lời cao, định giá ở mức trung vị ngành, nhưng đang **đi vào chu kỳ xấu đi chất lượng tài sản sớm hơn và
  nhanh hơn phần còn lại** (theo đúng mô tả CYCLICAL của Bobby), với nguồn vốn đắt hơn và trần vốn gần. Biến số quyết định là
  nhóm 2 Q4/2026 (mốc M1).

## 2. Kiểm lại số Mike đọc từ báo chí (đối chiếu BCTC gốc)

| Số Mike | BCTC gốc | Kết quả |
|---|---|---|
| LNTT Q3 10.330 (+42,5%); 9T 30.518 (+31,9%); LNST Q3 8.252 | 10.330,1 / 7.249,9 (+42,5%); 30.518,4 / 23.139,2 (+31,9%); 8.251,9 [HN-Q3 p6] | ĐÚNG |
| NII Q3 17.836 (+37%), 9T 49.643 (+34%) | 17.836,0 (+37,3%); 49.642,7 (+34,0%) | ĐÚNG |
| DV thuần Q3 1.678 (+26,5%) | 1.677,8 / 1.326,6 (+26,5%) | ĐÚNG |
| Chi phí lãi Q3 19.957 (+115%) | 19.956,6 / 9.275,4 (+115,2%); thu nhập lãi +69,7% | ĐÚNG |
| CIR 9T 26,3% | 15.494 / 58.956 = 26,3% | ĐÚNG |
| Dự phòng Q3 5.241 (+38%) | 5.241,3 / 3.801,5 (+37,9%) | ĐÚNG |
| CV KH +18,8% YTD; TG KH 993.988 (+7,9%) | 1.288.128 vs 1.084.019 (+18,8%); 993.988 vs 921.368 (+7,9%) [p3–4] | ĐÚNG (1,288 triệu tỷ là gộp, gồm 16.696 margin MBS) |
| KKH 326.389 (−3,8%), 32,8% từ 36,8% | 326.389 vs 339.353; 32,8% / 36,8% [p35] | ĐÚNG, nhưng đây là **KKH/TG KH**, không phải CASA theo cách MB công bố (BCTN25: CASA 2025 = 37,8%, 348 nghìn tỷ ⇒ định nghĩa MB rộng hơn) |
| GTCG 302.399 (+61,5%), CCTG 248.416 | 302.399 / 187.236 (+61,5%); CCTG 248.417 [tr.36] | ĐÚNG |
| Vay TCTD 102.412 (+59%) | Tiền vay TCTD 102.412 vs 64.382 (+59,1%) [tr.34]; tổng TG+vay TCTD 265.848 (+7,2%) | ĐÚNG (chỉ dòng "tiền vay") |
| NPL 21.474 (+53%), 1,29% → 1,67%; nhóm 3 7.231 (×2,2); bao phủ 93,7% → 84,7% | 21.474 / 14.027 (+53,1%); 7.231 / 3.276 (×2,21); 18.182/21.474 = 84,7% [tr.23, 26] | ĐÚNG |
| BĐS 179.756 (+48,3%; 13,95%) | 179.756 / 121.189 (+48,3%); 13,95% [tr.25] | ĐÚNG (chỉ ngành "KD BĐS"; không gồm vay mua nhà hộ gia đình) |
| Ngoại hối 9T 467 (−68,8%); phái sinh lỗ 1.066 | 467,0 / 1.496,5 (−68,8%); phái sinh thuần 4.503,0 − 5.569,0 = **−1.066** [tr.39] | ĐÚNG |
| CK kinh doanh 41.443 (×8,8) | 41.443,7 vs 4.653,2 (×8,9) [p3] | ĐÚNG về số, **SỬA về bản chất**: NH mẹ 39.875 = **100% chứng khoán nợ do TCTD trong nước phát hành** [RL-Q3 tr.19], không phải cổ phiếu |
| Tổng tài sản ~1,84 triệu tỷ | 1.837.857 | ĐÚNG |

## 3. Câu 1 — NIM và chi phí vốn

**Bảng 5 quý (hợp nhất, tự tính: NII annualized / TS sinh lãi BQ đầu–cuối quý; TSSL = TG NHNN + TCTD + CKKD + CVKH gộp + mua nợ + CKĐT)**

| Quý | NII | TSSL BQ | NIM | Lợi suất TSSL | Chi phí lãi/TSSL |
|---|---|---|---|---|---|
| Q3/25 | 12.991 | 1.280.624 | 4,02% | 6,90% | 2,87% |
| Q4/25 | 14.555 | 1.434.109 | 4,03% | 7,23% | 3,20% |
| Q1/26 | 14.913 | 1.570.096 | 3,85% | 7,49% | 3,63% |
| Q2/26 | 16.894 | 1.629.980 | 4,16% | 8,37% | 4,21% |
| Q3/26 | 17.836 | 1.740.574 | **4,07%** | 8,61% | 4,55% |

Nguồn: [HN-Q3/25, HN-Q4/25, HN-Q1, HN-Q2, HN-Q3] p3/p6; `calc/mbb_calc_out.txt` mục 1. NIM 9T26 = 4,01%. Đối chiếu: Vietcap ghi MB
công bố NIM Q2 4,1%, H1 3,9% [WEB]; Elibook ghi Q2 4,16% [WEB]. Cùng bậc với số tự tính, nhưng định nghĩa khác nhau.

- **Nén đến đâu:** YoY chưa nén (+5 bp); QoQ −9 bp. Chi phí lãi/TSSL +34 bp QoQ, lợi suất +24 bp QoQ ⇒ **đầu ra đã chậm lại so với
  đầu vào**. Chi phí lãi tiền gửi 9T26 = 4,91%/năm trên TG KH BQ (tự tính); chi phí GTCG = 6,22%/năm.
- **NH mẹ:** NII Q3 +44,5% YoY; chi phí lãi +112,8% [RL-Q3]. NIM riêng lẻ 9T **3,54%** là số thô (ước lượng), vì chỉ có 2 mốc
  BCĐKT (31/12 và 30/09). Phần chênh với hợp nhất là MCredit/MB Cambodia/MBS.
- **Q4/2026 (ước lượng):** CV 9608 đòi giảm lãi cho vay SXKD 1,5–2 pp. MB có 59% dư nợ là tổ chức kinh tế [HN-Q3 tr.24], nặng hơn
  nhóm "NH tư nhân thiên bán lẻ < 30% SXKD" của Bobby, nên **ít được miễn trừ hơn**. Phía vốn: 152.313 CCTG ≤12 tháng sẽ tái tục ở
  mặt bằng mới. NIM Q4 dự kiến **3,85–4,05%** (ước lượng), trung tâm khoảng −10 bp QoQ.

## 4. Câu 2 — Huy động, CASA, LDR

| 31/12/25 → 30/09/26 | Số | Nguồn |
|---|---|---|
| TG KH | 921.368 → 993.988 (+72.620) | [HN-Q3 tr.35] |
| — KKH | 339.353 → 326.389 (VND −6,7%; ngoại tệ +21%) | tr.35 |
| — có kỳ hạn | 573.483 → 653.688 | tr.35 |
| — theo đối tượng: TCKT / cá nhân | 402.398 → 429.767 / 518.971 → 564.221 | tr.35 |
| GTCG: CCTG ≤12T / >12T / trái phiếu | 76.253 → 152.313 / 64.577 → 96.104 / 46.406 → 53.982 | tr.36 |
| Lãi suất CCTG / trái phiếu | 4,70–11,18% / 5,40–9,20% | tr.36 |
| Tiền vay TCTD (VND / ngoại tệ) | 14.074 → 30.980 / 50.308 → 71.432 | tr.34 |
| TG NHNN (giảm) | 68.494 → 15.823 (−52.672, nguồn tài trợ 26%) | p3 |
| CV KH / TG KH (thô) | 117,7% → **129,6%** | tự tính |
| CV KH / (TG KH + GTCG) | 97,8% → 99,4% | tự tính |

- **Ai tài trợ +204.109 tín dụng:** TG KH 36%, GTCG 56%, rút TG NHNN 26%, VCSH 11% (tự tính; tổng > 100% vì phía tài sản còn tăng
  CKKD/CKĐT).
- **CASA tách cá nhân/DN: CHƯA KIỂM ĐƯỢC.** BCTC không tách KKH theo đối tượng. Theo Vietcap, MB công bố CASA Q2 = 34,6% [WEB].
  Số Q3 theo chuẩn MB không tìm thấy.
- **LDR theo quy định:** TT22, Q2 = 82,8% (trần 85%) [WEB Elibook, thứ cấp]. ACBS ước LDR theo TT50 = 87,2% (trần 95% từ 01/12)
  [WEB vnbusiness 02/10]. Q3 theo quy định: **không có số**. Tôi không tự tính được, vì công thức TT22/TT50 cần trọng số GTCG và
  tiền gửi KBNN không có trong BCTC. Suy luận: tốc độ CV (+4,9% QoQ) vượt TG KH (+3,1% QoQ, 963.815 [WEB thứ cấp, chưa đọc BCĐKT Q2 dòng này] → 993.988), nên dư địa
  TT22 trong Q3 hẹp lại. TT50 nới trần từ 01/12 (Bobby F11 P 0,85).

## 5. Câu 3 — Chất lượng tài sản

| | 31/12/25 | 30/06/26 | 30/09/26 |
|---|---|---|---|
| HN nhóm 2 (tỷ lệ) | 10.210 (0,94%) | 11.990 (0,98%) | **17.014 (1,32%)** |
| HN NPL nhóm 3–5 | 14.027 (1,29%) | 17.797 (1,45%) | **21.474 (1,67%)** |
| HN nhóm 2–5 | 2,24% | 2,43% | **2,99%** |
| HN bao phủ (DP cho vay / NPL) | 93,7% | 93,6% | **84,7%** |
| Mẹ nhóm 2 | 5.556 (0,54%) | 7.720 (0,66%) | **12.899 (1,05%)** |
| Mẹ NPL | 11.690 (1,13%) | 15.412 (1,31%) | 18.915 (1,54%) |
| Mẹ bao phủ | 99,5% | n/a | 86,9% |

Nguồn: [HN-Q3 tr.23, 26], [HN-Q2 tr.23], [RL-Q3 tr.19], [RL-Q2 tr.19].

- **Xoá nợ 9T26 (sử dụng dự phòng): 7.877** (cả năm 2025: 12.185) [HN-Q3 tr.26]. **NPL hình thành mới 9T = ΔNPL + xoá = 15.324 =
  1,73%/năm dư nợ BQ** (tự tính).
- **Chi phí tín dụng** (DP KQKD / dư nợ BQ, annualized): 9T 1,46%, Q3 1,65%, 2025 1,48% (tự tính). Trích dự phòng **thấp hơn tốc
  độ hình thành nợ xấu** (1,46% < 1,73%), nên bao phủ rơi. Muốn giữ bao phủ 93,7% thì cần thêm khoảng **1.940** dự phòng, ≈ 19% LNTT
  một quý (tự tính).
- **Nợ ngoại bảng / nợ cơ cấu TT02 / Pillar 3: CHƯA KIỂM ĐƯỢC.** BCTC quý không thuyết minh các mục này.
- **Lãi dự thu** (lãi, phí phải thu): 13.549 → 19.828 (+46% so với dư nợ +19%); bằng 1,08% TTS [HN-Q3 p3]. Dưới ngưỡng 2% của Bobby,
  nhưng **tăng nhanh hơn dư nợ ⇒ cờ**.
- **Phải thu miễn truy đòi theo bộ chứng từ** (mua lại LC, đối tượng CV 9608 trừ khỏi room): 8.046 → **13.597 (+69%)**, bằng 1,06%
  dư nợ [HN-Q3 tr.34]. Nếu bị trừ room 2026, ăn khoảng 1,1 điểm tăng trưởng tín dụng (ước lượng).
- **Công ty con** (HN − mẹ; gồm MCredit, MB Cambodia, margin MBS 16.696 nhóm 1, MBV nếu hợp nhất): dư nợ 56.353; NPL 2.559 (đầu
  năm 2.337); nhóm 2 4.115 (đầu năm 4.654); **NPL/dư nợ trừ margin 6,5%**; DP 1.752 (tự tính). **Rủi ro mới nằm ở NH mẹ, không phải
  MCredit.** MCredit: LNST 2025 93,6; NPL H1/2025 6,7% [WEB thứ cấp]; 9T/2026 không tìm thấy. Phần MBV có trong số hợp nhất hay không:
  chưa kiểm được (xem mục 11).
- Dự phòng 9T trong KQKD 12.943, trong đó cho vay KH 12.909 (cụ thể 11.401, chung 1.509) [tr.26].

## 6. Câu 4 — Tín dụng BĐS, tập trung

- KD BĐS **179.756 (+48,3% YTD, 13,95%)**, tăng **2,6 lần nhanh hơn tăng trưởng chung** ⇒ vi phạm đúng tinh thần chỉ đạo "BĐS không vượt
  tăng trưởng chung" mà Bobby dẫn [NGÀNH 1b]. Theo cờ của Bobby: tỷ trọng chưa vượt 15%, nhưng tốc độ **vượt** ⇒ **CỜ**. Xây dựng
  51.287 (3,98%). Hộ gia đình (gồm vay mua nhà, không tách) 294.116 (22,8%, +23%) [HN-Q3 tr.25].
- Cơ cấu chủ đầu tư vs người mua nhà; TPDN BĐS nắm giữ; top-10/20 khách hàng; cho vay bên liên quan: **CHƯA KIỂM ĐƯỢC** (BCTC quý
  không thuyết minh; cần BCTC năm/Pillar 3). CKĐT 252.454 (AFS) chủ yếu là TPCP và TCTD theo thuyết minh trang 27–28. Chưa tách được
  phần TPDN.
- Cho vay trung + dài hạn 50,5% dư nợ (đầu năm 44,4%); dài hạn +34% YTD [tr.23]. **Sai kỳ hạn tăng**, trong khi vốn tăng thêm chủ
  yếu là CCTG ≤12 tháng.

## 7. Câu 5 — Thu ngoài lãi, chất lượng lợi nhuận (9T26 vs 9T25, [HN-Q3 tr.38–40])

| Khoản | 9T26 | 9T25 | Ghi chú |
|---|---|---|---|
| NII | 49.643 | 37.055 | 84% TOI |
| DV thuần | 5.192 | 4.478 | thu thanh toán 3.796 (+30%); BH: thu 7.423 − chi KD BH 5.264 = 2.158 (9T25 2.197, đi ngang) |
| Ngoại hối giao ngay + vàng thuần | 1.533 | 2.329 | |
| Phái sinh tiền tệ thuần | −1.066 | −832 | vay TCTD ngoại tệ +21.124 ⇒ lỗ phái sinh **nhiều khả năng là chi phí swap tài trợ ngoại tệ** (suy luận, chưa có thuyết minh), tức chi phí vốn trá hình, không phải lỗ đầu cơ |
| CKKD / CKĐT | 530 / 12 | 588 / 768 | |
| Thu nợ đã xử lý | 2.080 | 2.912 | −29% |
| Thu nhập khác | 895 | 581 | |
| OPEX | 15.494 | 13.452 | +15%; nhân viên +11% |

- **Phần một lần / không bền** (thu nợ đã xử lý + CK) = 2.621 = **8,6% LNTT 9T**, dưới ngưỡng 25% của Bobby ⇒ **LN chủ yếu từ lõi**.
  Lưu ý chiều ngược: thu nợ đã xử lý **giảm**, nên LN 9T26 không được "đỡ" bởi khoản này.
- Cờ "CIR giảm cùng DP giảm" của Bobby: CIR giảm (27,9% → 26,3%) nhưng DP **tăng** (+11,8%) ⇒ không cờ. Tuy vậy, Q4/25 DP chỉ 2.169
  [HN-Q4/25], **nền Q4 thấp bất thường** cho so sánh Q4/26.
- MBS 9T LNTT khoảng 1.140 (+11%); MIC 9T 350,6 (−9%), Q3 −31,5% [WEB thứ cấp]. Công ty con chiếm khoảng 9% LN tập đoàn H1 [WEB Vietcap].
  NH mẹ nhận cổ tức con 9T 1.758 [RL-Q3].
- **DuPont 9T26** (/TTS BQ, annualized): NII 3,84% + ngoài lãi 0,72% − OPEX 1,20% − DP 1,00% = LNTT 2,36%; ROA 1,89%; đòn bẩy 11,2x;
  **ROE 21,7%** (LNST NH / VCSH mẹ BQ). ROE trước DP và trước thuế 39,6% (tự tính).

## 8. Câu 6 — Vốn

- VĐL 80.550 → **100.687** (+20.138 = cổ tức CP 15% ≈ 12.082 + quyền mua 805,5 triệu CP × 10.000 ≈ 8.055) [HN-Q3 tr.36 + WEB].
  VCSH hợp nhất 164.142, mẹ 157.017. Cổ tức tiền 10% (≈ 8.055 khi trả trên VĐL cũ, ước lượng). LNCPP đã dùng 28.463 trong 9T.
- CAR: 2025 hợp nhất **11,0%**, vốn cấp 1 chiếm 89% vốn tự có [BCTN25, Basel II]. 30/06/26: hợp nhất 10,7% (Tier1 9,9%); riêng lẻ
  10,28% (**Tier1 9,02%**) [WEB thứ cấp]. CAR 30/09/26: **không có số**. Phương pháp TT14/2025 hay TT41: chưa rõ.
- **Sức chứa 2027:** tự sinh vốn ≈ ROE × (1 − tỷ lệ trả tiền) = 13–15%/năm (ROE 20%, trả 25–35%; tự tính). Mục tiêu tín dụng MB
  30–35%/năm [WEB, ĐHCĐ] (được nới tới 35%/năm × 4 năm vì nhận MBV) ⇒ **cần vốn ngoài liên tục**: 200 triệu CP riêng lẻ (≈2% pha
  loãng), cấp 2 10–15 nghìn tỷ H2/2026 [WEB Vietcap], room ngoại đã kín (đang tìm cổ đông chiến lược, trần có thể lên 49% theo NĐ 69/2025
  [WEB]). Thị trường đang ngụ ý: P/B 1,24x với ROE 21,7% ⇒ hoặc ROE bền vững thấp hơn nhiều (13–15%), hoặc Ke cao (mục 9).

## 9. Câu 7 — Kiểm toán, cổ đông, pháp lý

- **KPMG**: BCTC hợp nhất 2025, ý kiến **chấp nhận toàn phần** (báo cáo 25-02-00061-26-7, 07/03/2026), không thấy đoạn nhấn mạnh trên trang
  ý kiến [KT25 PDF p9]. Soát xét 6T/2026: **kết luận không ngoại trừ** (26-02-00092-26-2, 01/08/2026) [SX6T p9]. Chênh LN trước/sau kiểm
  toán 2025: chưa đối chiếu (thiếu BCTC Q4/25 so với KT25 cùng dòng). Q4/25 LNTT 34.268 khớp BCTN25.
- Cổ đông: Viettel khoảng 14,7% trước đợt quyền mua 2026; SCIC khoảng 9,8%; Trực thăng khoảng 8,4%; Tân Cảng khoảng 7,1% (số 2024–25,
  **chưa cập nhật** sau phát hành) [WEB thứ cấp]. Room ngoại: MB nói đã dùng hết [WEB].
- Nhân sự: Chủ tịch Lưu Trung Thái, TGĐ Phạm Như Ánh (ký BCTC Q3). Không tìm thấy thay đổi 2025–26.
- **Pháp lý/thanh tra 2025–26: không tìm thấy** (agent web; tìm không thấy ≠ không có) ⇒ không WARNING. **MBV:** 100% sở hữu, vốn 3.500,
  lỗ luỹ kế 15.688 cuối 2024, MB có thể góp thêm tới 5.000 [WEB]. Nghĩa vụ hỗ trợ vs ưu đãi room là **rủi ro ẩn có tên**. Số liệu MBV
  2025–26: chưa kiểm được.

## 10. Câu 8 — Định giá (giá 19.300, đóng cửa 30/10/2026 [BQ])

**Mốc:** BVPS 30/09 = 157.017 / 10.068,75 triệu CP = **15.594 đ** ⇒ **P/B 1,24x**. LNST NH TTM (Q4/25 + 9T26) 32.547 ⇒ EPS 3.232 ⇒
**P/E TTM 5,97x**. Chưa tính 200 triệu CP riêng lẻ.

**3 kịch bản (toàn bộ (ước lượng); `calc/mbb_calc.py` mục 5)**

| | Xấu (w 0,30) | Cơ sở (w 0,50) | Tốt (w 0,20) |
|---|---|---|---|
| Q4/26 PPOP / DP | 15.000 / 7.000 | 15.800 / 5.500 | 16.300 / 4.500 |
| **LNTT 2026** | 38.518 (+12%; 98% KH) | **40.818 (+19%; 104% KH)** | 42.318 (+24%) |
| 2027: tăng CV / NIM / chi phí tín dụng / CIR | 12% / 3,6% / 2,2% / 28% | 18% / 3,9% / 1,7% / 27% | 24% / 4,1% / 1,3% / 26% |
| **LNTT 2027** | 29.083 (−25%) | **43.197 (+6%)** | 55.164 (+30%) |
| ROE 2027 / P/E 2027 | 13,0% / 8,6x | 18,6% / 5,8x | 23,0% / 4,5x |
| ROE 2027–29 → ROE terminal / g | 13→15% → 14% / 6% | 18,5→17% → 16% / 7% | 22→20% → 18% / 8% |

LNTT 2027 có trọng số: 41.356. Kịch bản xấu = chi phí tín dụng 2,2% (bằng tốc độ hình thành NPL hiện tại 1,73% cộng xây lại bao phủ)
kèm NIM −45 bp. Đây là bản đồ "CYCLICAL + ADMIN_GATED" của Bobby, không phải đuôi cực đoan.

**Chuẩn hoá chi phí tín dụng chu kỳ:** 1,7% (cơ sở) cao hơn 2025 (1,48%) và 9T26 (1,46%), vì 9T26 trích **thấp hơn** hình thành NPL (1,73%).
P/E forward chuẩn hoá (cơ sở 2027) = **5,8x**.

**RI 3 giai đoạn** (BV0 = VCSH mẹ cuối 2026 theo kịch bản; trả tiền 30%; chiết khấu 2 tháng; giá trị/CP; tỷ trọng terminal trong ngoặc)

| Ke | Xấu | Cơ sở | Tốt | Có trọng số |
|---|---|---|---|---|
| 12,3% | 20.614 (19%) | 29.749 (38%) | 42.920 (53%) | 29.642 |
| 12,8% | 18.964 (14%) | 27.011 (33%) | 38.212 (48%) | 26.837 |
| 13,4% | 17.282 (7%) | 24.294 (26%) | 33.717 (42%) | 24.075 |

**Gordon P/B = (ROE−g)/(Ke−g)** (× BVPS cuối 2026 cơ sở; xem out mục 5): ROE 16% → 1,41–1,86x (22,6k–29,9k); ROE 18% → 1,72–2,33x.
**Ngược lại:** giá 19.300 ngụ ý **ROE bền vững 13,3–14,7%** (Ke 12,3–13,4%, g 8%), hoặc **Ke ngụ ý 14,1–17,5%** (ROE 16–20%, g 6–7%).

**Tương đối** ([BQ] 30/10/2026; P/B và ROE5Y theo cột BQ, chưa đối chiếu BCTC từng NH):

| NH | P/B | P/E | ROE5Y |
|---|---|---|---|
| LPB | 2,31 | 8,9 | 21,9% |
| VCB | 1,89 | 11,3 | 20,4% |
| HDB | 1,62 | 7,6 | 23,8% |
| BID | 1,31 | 8,1 | 17,9% |
| **MBB** | **1,24** | **6,5** (BQ; tự tính TTM 5,97) | **22,7%** |
| CTG | 1,18 | 5,9 | 18,1% |
| ACB | 1,17 | 7,6 | 23,0% |
| VPB | 1,15 | 7,4 | 14,8% |
| VIB | 1,04 | 6,7 | 23,6% |
| TPB | 0,81 | 5,3 | 18,6% |
| TCB | 0,78 | 5,3 | 17,4% |
| SHB | 0,76 | 4,7 | 17,8% |
| STB | 1,95 | 81,9 (méo do xử lý nợ) | 14,7% |

Hồi quy P/B ~ ROE5Y (12 NH, bỏ STB): R² 0,17 (yếu). MBB dự báo 1,44x (22,5k). Trung vị P/B 1,18x (18,3k). Lịch sử P/B MBB [BQ]:
TB năm 2023 1,06x, 2024 1,23x, 2025 1,38x, 2026 YTD 1,39x (min 1,16, max 1,71); 2018 đỉnh 2,26x, 2021 TB 1,80x ⇒ ×BVPS = 16,5k–21,7k
cho dải 2023–26. NIM/CASA/NPL theo NH cùng ngày: **không có bảng đầy đủ** (WEB mục 6: CTG NIM Q2 2,88%, NPL 1,2%; VCB NPL 0,6%;
MBB/TCB/VCB CASA > 30%; bảng ROE/P/B MAS 18/09 tự mâu thuẫn với nguồn khác ở dòng MBB).

**Vùng tham chiếu: 18.000–26.000, tâm ~22.000 (ước lượng)** = TB của RI có trọng số @Ke 13,4% (24,1k), hồi quy comp (22,5k) và giữa dải
P/B lịch sử 2023–26 (1,25x ≈ 19,5k). Biên dưới ≈ RI xấu / trung vị comp; biên trên ≈ RI có trọng số @Ke 12,8%. Giá −12% so với tâm.
**Đọc trung dung:** RI theo khung Ke của user cho MBB "rẻ", nhưng cũng cho gần như MỌI NH VN "rẻ". Thị trường áp Ke ngành khoảng 14–17% từ
2023 (P/B 1,1–1,4x với ROE > 20%). Nếu bất đồng đó không đóng lại, upside của MBB phải đến từ **chất lượng tài sản ổn lại**, không phải
từ chênh lệch mô hình. Ở quý này, chất lượng tài sản đang đi **ngược** chiều đó.

## 11. Câu 9 — Giá, thanh khoản, sizing [BQ, `calc/mbb_calc_out.txt` mục 7]

- 1 năm: đỉnh 23.230 (11/02/2026), đáy 18.030 (27/07/2026); 30/10 cách đỉnh −16,9%; YTD −4,7%; tháng 10 −1,8%.
- Quanh CV 9608 (18/10, Chủ nhật) và BCTC Q3 (ký 20/10): 16/10 → 21/10 **+0,8%**; 16/10 → 30/10 −2,8% ⇒ **không có phản ứng mạnh** với cả
  hai sự kiện. Thị trường chưa định giá lại theo nhóm 2 (công bố đầy đủ 30/10; phiên 30/10 −2,0%: 19.700 → 19.300).
- TT50 (30/09): không đo riêng được tác động giá (trùng nhiều sự kiện).
- ADV giá trị 20 phiên 221 tỷ, 60 phiên 234 tỷ. **Sizing tham chiếu 0,5–1,0% NAV**: mọi quy mô NAV của fleet đều < 1% ADV một phiên,
  nên thanh khoản không ràng buộc. Room ngoại kín ⇒ cầu ngoại thụ động (FTSE) **không vào được** cho tới khi mở room. Đó là kênh định giá
  bị chặn, không phải luận điểm.

## 12. Checklist ngành §7 (25 mục) bằng số MBB

| # | Mục | MBB | Cờ |
|---|---|---|---|
| 1 | NIM 8–12 quý, HN + riêng lẻ | HN 5 quý 3,85–4,16%; riêng lẻ chỉ 9T thô 3,54% | Riêng lẻ YoY: **chưa kiểm** |
| 2 | Cơ cấu vốn | GTCG 56% vốn tăng thêm; CCTG tới 11,18% | **CỜ** (chi phí biên) |
| 3 | CASA tách cá nhân/DN | KKH/TG KH 32,8%; tách: chưa kiểm | chưa kiểm |
| 4 | CIR + DP | CIR ↓, DP ↑ | không |
| 5 | Ngoài lãi; thu nợ + CK > 25% LNTT | 8,6% | không |
| 6 | ROE/ROA; PPOP/VCSH | 21,7% / 1,89% / 39,6% | — |
| 7 | Nhóm 2 > 2% hoặc +> 20% QoQ | HN **+42% QoQ**, mẹ **+67% QoQ** | **CỜ** |
| 8 | Bao phủ < 70% hoặc −> 15 pp/năm | 93,6 → 84,7 (−8,9 pp trong 1 quý) | **CỜ** (tốc độ) |
| 9 | Chi phí tín dụng vs hình thành NPL | 1,46% < 1,73% | **CỜ** (trích thiếu) |
| 10 | Xoá nợ / ngoại bảng / cơ cấu | xoá 7.877; ngoại bảng + cơ cấu: chưa kiểm | chưa kiểm |
| 11 | Lãi dự thu | 1,08% TTS; +46% vs dư nợ +19% | **CỜ** (tốc độ) |
| 12 | LC miễn truy đòi | 13.597 (+69%), 1,06% dư nợ | theo dõi (trừ room) |
| 13 | BĐS > 15% hoặc > tăng trưởng chung | 13,95%; +48% vs +19% | **CỜ** |
| 14 | TPDN nắm giữ | chưa tách được | chưa kiểm |
| 15 | Tập trung / bên liên quan | chưa kiểm | chưa kiểm |
| 16 | Tiêu dùng / CTTC | con: NPL 6,5% dư nợ trừ margin; nhóm 2 con giảm | không (rủi ro ở mẹ) |
| 17 | LDR | TT22 Q2 82,8% (thứ cấp); TT50 ACBS 87,2% | gần trần cũ |
| 18 | CAR / CET1 < 9% | Tier1 riêng lẻ 9,02% (Q2, thứ cấp) | **CỜ** (sát ngưỡng) |
| 19 | Cấp 2 / GTCG, pha loãng | 200 triệu CP chờ; cấp 2 10–15 nghìn tỷ | theo dõi |
| 20 | Room tín dụng | ưu đãi tới 35%/năm (MBV); quota 2026 cụ thể: không tìm thấy | chưa kiểm |
| 21 | Đóng góp con | khoảng 9% LN H1 (thứ cấp); cổ tức con về mẹ 1.758 | — |
| 22 | CTCK con | margin MBS 16.696 (nhóm 1) | không |
| 23 | Bảo hiểm con | MIC Q3 −31,5%; BH thuần đi ngang | nhẹ |
| 24 | Room ngoại | kín | — |
| 25 | Kiểm toán | KPMG sạch 2025 + 6T | không |

**7 cờ / 25 mục; 7 mục chưa kiểm được.** Cờ dồn vào khối B (chất lượng tài sản), đúng biến số số 1 của Bobby.

## 13. Mốc khoá trước — HAI CHIỀU (lập 31/10/2026; P = (ước lượng); chấm bằng nguồn công bố đầu tiên ≤ ngày chấm)

| # | Mệnh đề | P | Ngày chấm | Nguồn |
|---|---|---|---|---|
| M1 | Nhóm 2 HN 31/12/26 **≥ 17.014** (không giảm so với 30/09) | 0,55 | 2027-02-15 | BCTC HN Q4/26 thuyết minh cho vay |
| M2 | NPL HN 31/12/26 trong [1,5%; 2,0%] | 0,70 | 2027-02-15 | như trên |
| M2b | NPL HN 31/12/26 > 2,0% | 0,20 | 2027-02-15 | như trên |
| M3 | Bao phủ HN 31/12/26 ≥ 85% | 0,45 | 2027-02-15 | như trên |
| M4 | LNTT HN 2026 ≥ 39.408 (đạt KH) | 0,70 | 2027-02-15 | BCTC Q4/26 |
| M5 | NIM tự tính Q4/26 (cùng công thức) ≤ 4,07% | 0,65 | 2027-02-15 | BCTC Q4/26 + `mbb_calc.py` |
| M6 | TG KH 31/12/26 ≥ +12% YTD (≥ 1.031.932) | 0,40 | 2027-02-15 | BCTC Q4/26 |
| M7 | CAR HN 31/12/26 ≥ 10,5% (số MB công bố) | 0,60 | 2027-04-30 | BCTN 2026 / BCTC |
| M8 | Hoàn tất phát hành 200 triệu CP riêng lẻ trước 30/06/2027 | 0,50 | 2027-07-15 | CBTT HOSE |

Liên kết Bobby: M2/M3/M5 là phiên bản cấp NH của F6/F7/F8. Nếu NH mục tiêu xấu hơn ngành ở cả F7 lẫn M3, kịch bản xấu được nâng trọng số.

**Điều kiện đổi nhận định:**
- **Xấu đi** (nâng w kịch bản xấu lên ≥ 0,45, vùng còn 16–22k): nhóm 2 HN Q4 > 20.000 **hoặc** nhóm 2–5 > 3,5%; bao phủ < 75%; DP Q4 <
  4.000 trong khi NPL tăng (trích thiếu); Tier1 riêng lẻ < 8,5%; KKH tiếp tục giảm tuyệt đối; NIM Q4 < 3,8%.
- **Tốt lên** (nâng w kịch bản tốt lên ≥ 0,35, tâm lên khoảng 24k): nhóm 2 HN giảm về < 13.000 (chuyển ngược về nhóm 1, không phải lên
  nhóm 3–5) **và** bao phủ ≥ 90%; TG KH Q4 tăng > 5% QoQ, KKH tăng lại; phát hành cấp 2/riêng lẻ hoàn tất với giá ≥ P/B 1,3x; NIM Q4 ≥ 4,0%.

## 14. Điểm yếu / lỗ hổng chưa kiểm được

| Mục | Trạng thái |
|---|---|
| CASA theo chuẩn MB, tách cá nhân/DN (Q3) | Chưa kiểm. BCTC không tách; MB IR deck Q3 không tìm thấy; Q2 34,6% là thứ cấp (Vietcap) |
| CAR/CET1/Tier1 30/09/2026; CAR theo TT14 hay TT41 | Chưa kiểm. Số Q2 10,7% / 10,28% / 9,02% là **thứ cấp** (Elibook, Vietcap), chưa đối chiếu bản gốc |
| LDR theo TT22 và TT50 tại 30/09 | Chưa kiểm. 82,8% (Q2) và 87,2% (ACBS) là thứ cấp |
| NIM riêng lẻ theo quý | Chỉ có 9T thô 3,54% (thiếu BCĐKT riêng lẻ 31/03, 30/06; chưa đọc) |
| Nợ ngoại bảng, nợ cơ cấu TT02, Pillar 3 | Chưa kiểm (không có trong BCTC quý; cần KT25 thuyết minh, chưa đọc trang đó) |
| Tập trung top-10/20 KH, bên liên quan, TPDN BĐS nắm giữ | Chưa kiểm |
| Phân rã BĐS: chủ đầu tư vs người mua nhà | Chưa kiểm (BCTC chỉ có ngành KD BĐS) |
| MBV: có trong hợp nhất không, lỗ/lãi 2025–26, cam kết hỗ trợ | Chưa kiểm (suy từ sở hữu 100% ⇒ hợp nhất; chưa thấy dòng riêng) |
| MCredit 9T/2026 NPL, LN | Chưa kiểm (chỉ suy từ HN − mẹ, gộp nhiều con) |
| Lỗ phái sinh = chi phí swap tài trợ | Suy luận, chưa có thuyết minh xác nhận |
| % sở hữu Viettel/SCIC/Tân Cảng, % sở hữu ngoại sau phát hành 2026 | Chưa kiểm (thứ cấp 2024–25) |
| Quota tín dụng 2026 NHNN giao MB | Chưa kiểm |
| Comp NIM/CASA/NPL Q3/2026 10 NH | Thiếu bảng cùng ngày; P/B và ROE5Y từ BQ chưa đối chiếu BCTC từng NH (TCB 0,78x cần kiểm cột BVPS) |
| Ý kiến kiểm toán: chỉ đọc trang ý kiến/kết luận | Không đọc toàn bộ báo cáo kiểm toán; "không có nhấn mạnh" = không thấy trên trang ý kiến |
| Đọc số từ ảnh scan | Rủi ro đọc nhầm chữ số. Đã kiểm chéo tổng (NPL 21.474 = 7.231 + 4.778 + 9.465; NII = TN − CP lãi; 9T = 6T + Q3) |
| Mọi giả định 2026–2029, Ke, g | (ước lượng) |

## Ghi chú cho Mike
- Chưa qua fundamental-skeptic. Đề xuất skeptic tấn công: (a) suy luận "phái sinh = swap tài trợ"; (b) cách tự tính NIM (mẫu số gồm TG NHNN
  biến động mạnh: 68.494 cuối 2025); (c) trọng số kịch bản xấu 0,30 có quá thấp sau Q3 hay không; (d) tâm 22k có đang ăn theo khung Ke mà
  thị trường không chấp nhận hay không.
- Bobby rò snippet "một NH tư nhân lớn: LN tăng nhờ tín dụng, áp lực nhóm 2" (mục 0b). Mô tả khớp MBB, nên đọc ngành không hoàn toàn mù
  với mã này.
