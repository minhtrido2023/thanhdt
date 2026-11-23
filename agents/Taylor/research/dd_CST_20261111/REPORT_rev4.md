# DD — CST (CTCP Than Cao Sơn – TKV, HNX) · REV 4 · 2026-11-23 · job `Taylor_20261123_120252`

> NGHIÊN CỨU READ-ONLY, không phải khuyến nghị mua; người quyết là user. **Rev 4 = rev 3 + đính chính theo skeptic r3 (REFUTED, `skeptic/r3.json`) — §1c.** Rev 3 = rev 2 (dựng lại sau skeptic r1 REFUTED,
> `skeptic/r1.json`) + đính chính theo skeptic r2 (INCONCLUSIVE, `skeptic/r2.json`, chạy trên `REPORT_rev2.md`). Bản rev 1
> (`REPORT.md`) và rev 2 (`REPORT_rev2.md`) giữ nguyên, không ghi đè. Mục nào rev 2 không viết lại thì **giữ nguyên nội dung rev 1** và ghi rõ "xem REPORT.md §x".
>
> **Nguồn** (mỗi số ghi nguồn; số không đo được gắn **(ước lượng)**):
> - **[KT25]** BCTC 2025 đã kiểm toán (AASC, chấp nhận toàn phần), `src_restored/VI_BaoCaoTaiChinh_KiemToan_2025.pdf`
>   md5 `383226e174248bd16aa27eded8febea3`. `tr.` = số trang in; trang PDF = tr. + 3. Ảnh trang: `src_restored/img_kt25/pNN.png`.
> - **[Q3]** BCTC riêng Q3/2026 (HNX CBTT 22/10/2026, chưa soát xét), `src_restored/000000016954303_VI_BaoCaoTaiChinh_Q3_2026.pdf`
>   md5 `34d9d36fc65c95ee0a127e79cae451ce`; `p` = trang PDF; ảnh `src_restored/img_q3/`.
> - **[6T]** BCTC 6T/2026 soát xét (PKF-TTG), `src_restored/VI_BaoCaoTaiChinh_SauSoatXet_6T_2026.pdf` md5 `6ec2b8e33d3a1b8e0548cfff5b0b1138`.
> - Ba PDF trên bị dọn khỏi `src/`, `src_q3/` ngày 19/11 (commit `d036dc335` TRIM_DD); rev 2 **khôi phục nguyên byte từ git**
>   (`git show d036dc335^:<path>`) — cùng file rev 1 đã đọc, không phải bản tải mới.
> - **[BQ]** `tav2_bq.ticker_financial` (CST, NP_P0 = LNST quý, VCSH = BVPS×OShares, Dividend_1Y), 2020Q4–2026Q3.
> - Mô hình rev 4: `calc_rev4/model_rev4.py` (= rev 3 + khối độ nhạy `sens_rev4`) → `calc_rev4/model_out_rev4.json`; giả định khoá `calc_rev4/assumptions_rev4.json`
>   md5 **`9965cf0163000043b726ccf380690697`** (= rev 3, đổi cơ sở `payout_retained`, thêm `sens_rev4`; không đổi tham số base); toàn bộ md5 ở `calc_rev4/MD5_LOCK.txt`. Rev 3: `calc_rev3/` md5 `028e67b909a87f091a6924dd4c0c582a`. `px_cst.csv` (dữ liệu thanh khoản đến
>   11/11) bị mất cùng đợt TRIM, khôi phục từ git, md5 `c34c4e9f0bbcee540ea653f74235f31a`.
> - `bin/dd_assumptions_lint.py` chạy trên `assumptions_rev4.json`: 20 cảnh báo schema v1 (file dùng định dạng cũ của rev 1), rc=0 chế độ cảnh báo; khoá bằng md5.
> - **Mù giá:** rev 4 không truy vấn giá mới; giả định khoá trước pha so giá. Giá 14.100 kế thừa rev 3.
> - (rev 3) Giả định khoá trước khi đọc giá mới. Giá chỉ đọc ở pha sau khoá (§8): đóng cửa 20/11/2026 = 14.100 [BQ `ticker`].

## 0. Kết luận

**Tâm giá trị: 6.022 đ/cp trước chiết khấu thanh khoản, 5.837 sau chiết khấu (cỡ 0,3 tỷ).** Rev 1: 13.084 / 12.681 (−54%);
rev 2: 4.563 / 4.422; rev 3: 6.022 / 5.837. **Rev 4 giữ nguyên tâm 6.022 / 5.837 và vùng** — hạng mục quyết định của skeptic r3
(khoản chia 130,66 tỷ có bị trích KTPL không) được kiểm lại trên chính TM17 kiểm toán: quỹ ĐTPT 2025 = **đúng 30,000% LNST 2024**,
nên các quỹ được tính trên LN NĂM, phần LN tích luỹ 34,1 tỷ vào đợt chia 2025 đi **100% vào cổ tức** (§2b). Cơ sở mới là số học
của BCTC kiểm toán, không phải báo chí. Rủi ro ĐHĐCĐ bất thường (chưa biểu quyết) giữ ở độ nhạy: trích KTPL 49,95% ⇒ 4.499–5.293.
- **Vùng (sau CK 0,3 tỷ):** bi quan **3.511** — lạc quan **8.862**. Ngưỡng luật 0,85×tâm = **4.961**.
- **Nhãn (pha sau khoá):** giá 14.100 (20/11) **TRÊN vùng** — cao hơn kịch bản lạc quan ~59%, gấp ~2,4 lần tâm. Không có biên an toàn.
- **Nguyên nhân giảm (một hạng mục quyết định):** rev 1 dùng N = LNST gộp. BCTC kiểm toán cho thấy **quỹ khen thưởng phúc lợi
  (KTPL) lấy đi 63–64% LNST hai năm gần nhất** (82,3/130,0 và 52,8/82,7 tỷ) và được trích TRƯỚC cổ tức. Phần LN thực sự thuộc
  cổ đông ≈ đúng bằng cổ tức đã chi (42,8 và 30,0 tỷ). Rev 2 dùng N cổ đông = LNST − trích KTPL − dòng tiền ra tuân thủ (ký quỹ
  môi trường).
- **Bản chất doanh nghiệp không đổi so với rev 1:** đơn vị gia công khai thác theo giá vốn cộng lãi cho TKV (97% DT nội bộ), mỏ
  hữu hạn tới 08/2045, moat NONE.
- **Khoản chia 130,7 tỷ (ĐHĐCĐ bất thường 20–30/12) trong base** ở mức thận trọng +1.459 đ/cp (giả định vay để chia); chia bằng
  tiền nhàn rỗi ⇒ +1.951; TKV bù chi phí vốn trong giá ⇒ +2.774 (tâm 7.337). Độ nhạy lớn nhất còn lại: tỷ lệ trích KTPL α (0,50 ⇒ 7.677) và dự án mở rộng (−3.017 nếu sinh lời dưới r).
  Không kịch bản nào trong §8c–8d đưa tâm lên gần giá hiện tại (cao nhất 9.246 khi rò 37%).

## 1. Đính chính so với rev 1 — từng hạng mục skeptic r1 → xử lý

| # | Hạng mục skeptic r1 | Bằng chứng độc lập rev 2 | Xử lý |
|---|---|---|---|
| 1 | **Quỹ KTPL / LN rời VCSH ngoài cổ tức** (killer objection) | KT25 tr.30 TM17 + Q3 p4 + BQ (§2) | **(a) VÀO BASE**: N_cổ đông = N − min(0,64·N; 82,3). Tâm 13.084 → 4.563 (rev 2; rev 3 cộng khoản chia 130,7 ⇒ 6.022) |
| 2 | Vốn còn phải chi dự án mở rộng Cao Sơn (1.829,5 tỷ) chưa có số; NPV=0 mâu thuẫn ROE<r | KT25 tr.19: tổng mức 1.829,5, 70% vay, XDCBDD dự án 29,5 tại 31/12/25; capex 2023–9T/26 cộng ~810 (gồm cả duy tu) | **(b) ĐỘ NHẠY**, không vào base (V4a: dự án tăng trưởng NPV=0). Phần còn phải chi ≥~1.020 tỷ **(ước lượng)**; nếu 30% vốn chủ (~306) chỉ sinh ROE 7,9% ⇒ **−3.017 đ/cp**. Xác suất không định lượng được |
| 3 | Nghĩa vụ hoàn nguyên/đóng mỏ ngoài ký quỹ 212 | KT25 tr.18 TM6b: ký quỹ gốc Cao Sơn 112,79 → 118,00 (+5,21/2025), Khe Chàm II 42,31 không đổi; lãi ký quỹ 41,94 | **(a) VÀO BASE phần đo được**: nộp ký quỹ 5,21 tỷ/năm = capex tuân thủ (V4b), trừ khỏi N suốt vòng đời (−819 đ/cp). **(c) Không kiểm chứng được**: dự toán chi phí phục hồi tổng và số năm còn phải nộp (QĐ 3928/QĐ-BTNMT không có trong src). Lãi ký quỹ ~5,9 tỷ/năm ghi vào thu nhập nhưng bị khoá ⇒ độ nhạy −928 đ/cp |
| 4 | Thuế suất tài nguyên chưa đọc | Q3 p43 (báo cáo nghĩa vụ NSNN, mẫu 19-TM-TKV): thuế tài nguyên phải nộp lũy kế 9T/26 **605,1 tỷ** = 10,9% DT 9T 5.566,7 (tự tính) | **(c)** Thuế suất theo biểu không ghi trong BCTC ⇒ không kiểm chứng được từ nguồn gốc. Không đổi base: theo cơ chế giá vốn cộng lãi, thuế tài nguyên nằm trong giá giao TKV; rủi ro là thay đổi biểu thuế mà TKV không bù (độ nhạy định tính) |
| 5 | Chiều RẺ: r=13,5% có thể cao cho đơn vị cost-plus | `effective_deposit_rate('2026-11-23')` = 7,40% (cctg_12m 02/11) = neo | **Giữ r=13,5%** cho tâm (luật V1, β=1). Báo kèm r=11% ⇒ 6.771 (+12%), dải Ke 12,3–13,4% ⇒ 6.349–6.047 (§8b; số rev 3) |
| 6 | Kịch bản bi quan dựa trên báo chí; mâu thuẫn −28%/−56% chưa giải | Thời báo Tài chính: KH 2026 "hơn 36 tỷ, giảm hơn 28% so với thực hiện 2025", bài cùng nêu **ước LN 2025 ~51 tỷ** (trước kiểm toán) | **Đã giải mâu thuẫn**: −28% là so ước thực hiện chưa kiểm toán (~51), không phải 82,75 kiểm toán. NQ ĐHĐCĐ gốc vẫn không có ⇒ nguồn vẫn là báo chí; kiểm chéo: LNST 9T/26 thực tế 15,88 [Q3 p5] thấp hơn nhịp kế hoạch. Giữ N bi quan 35, trọng số 30% |
| 7 | Data provenance: src bị TRIM, không mở lại được BCTC gốc | Khôi phục nguyên byte từ git, md5 ở đầu báo cáo; đọc lại trực tiếp TM17, BCĐKT, TM6, TM8 | Đã khắc phục |
| 8 | N theo chu kỳ (~106) làm đảo nhãn (rev 1 tự nêu) | Với KTPL: N=106 ⇒ N cổ đông 106−67,8−5,2 = 33,0 ⇒ ~6.200 đ/cp chưa gồm khoản chia; ~7.640 gồm khoản chia +1.459 (tự tính cùng công thức) | Không còn đảo nhãn (giá 14.100) |

### 1b. Đính chính rev 3 theo skeptic r2 (INCONCLUSIVE)

| # | Hạng mục skeptic r2 | Bằng chứng | Xử lý rev 3 |
|---|---|---|---|
| r2-1 | Quy tắc KTPL min(0,64N; 82,3) không khớp cách NQ đặt quỹ (49,95% của quỹ phân phối 164,155 gồm cả LN tích luỹ); thiếu cơ sở pháp lý | TM17: 49,95% là tỷ lệ trên **quỹ phân phối 2025** (LN 2024 130,02 + 34,1 tích luỹ). Theo ND 167/2024 (báo chí, §2b) LN còn lại phải chia hết hằng năm ⇒ từ nay quỹ phân phối ≈ N. Năm duy nhất quỹ = N đúng bằng LN năm (2026: 82,749) cho KTPL **63,8%** ⇒ giữ α = 0,64. | Giữ base; thêm độ nhạy **α = 0,50** (tỷ lệ 49,95% áp lên N) ⇒ **7.677**. Văn bản quy chế quỹ của TKV/ND về trần KTPL: **không kiểm chứng được** (không có trong src, bài báo không nêu). Dải thực tế thu hẹp: rò cố định 70 tỷ (2.702) bị bác bởi số 2026 (KTPL co lại 52,8 khi LN 82,7) — giữ chỉ để tham khảo |
| r2-2 | Dự án mở rộng 1.829,5 tỷ làm nền T=19 nhưng NPV=0 khi ROE cổ đông ~2,3% | KT25 tr.19 (đã đọc lại). Không có số vốn còn phải chi, lịch giải ngân, cơ chế TKV hoàn khấu hao + lãi vay trong giá giao | **(b)** giữ V4a base NPV=0 (luật user 03/11: cấm "đầu tư mới ⇒ giảm giá trị" khi chưa có cơ sở độc lập). Thêm dòng **hiển thị** "tâm điều chỉnh rủi ro dự án" P=0,3 (ước lượng chủ quan) × −3.017 ⇒ **5.117** (§8d); không vào sổ. Ghi chú đối chiều: kịch bản không mở rộng/đóng 2030 cho 8.882 > base ⇒ giả định 19 năm không phải chiều lạc quan của mô hình |
| r2-3 | Q4/25 = 59,35 chiếm 79% TTM 75,2 — chưa kiểm một lần | Quyết toán giá với TKV dồn vào Q4 mỗi năm (hợp đồng phối hợp kinh doanh, "doanh thu, chi phí quyết toán với Tập đoàn cuối năm" [Q3 p8]); tỷ trọng Q4 trong LN năm: 2023 61% (179,9/293,1), 2024 5% (6,7/139,7 BQ), 2025 72% (59,35/82,75) [BQ] | Không phải một lần: mọi số năm đều chứa đúng một Q4 quyết toán; base 75 ≈ LNST 2025 kiểm toán 82,75 (−9%). Biến động Q4 đã được phủ bởi bi quan 35 / lạc quan 130 |
| r2-4 | Tiền mặt so với khoản chia 130,7 (giả định vay) chưa kiểm | Q3 p4: tiền 195,9, vay dài hạn 129,5, tiền ròng +66,4 tại 30/9/26; cuối năm theo mùa thấp (1,9 tại 31/12/25 [KT25]) vì dự phòng 333,5 và tồn kho đảo chiều khi quyết toán | Base giả định **vay 8%/năm (ước lượng; chi phí lãi vay 2025 30,4 tỷ [KT25 TM22] trên dư nợ 255–485)** ⇒ +1.459; chia từ tiền nhàn rỗi (4%/năm sau thuế) ⇒ +1.951 (độ nhạy) |
| r2-5 | ρ = 0,5 chưa kiểm (±22%) | Không có lịch thanh lý tài sản cuối đời mỏ | **(c) không kiểm chứng được**; ρ=1 ⇒ 7.023, ρ=0 ⇒ 5.021 (±1.001 đ/cp, ±17% tâm rev 3) |

Thay đổi khác: B₀ trừ thêm 10,16 tỷ = 0,64 × LNST 9T/26 15,884 (phần LN đã nằm trong VCSH 30/9 sẽ bị trích KTPL khi phân phối;
ảnh hưởng ≈ −11 đ/cp vì hệ số của B trong mô hình chỉ 0,045, xem §8a).

### 1c. Đính chính rev 4 theo skeptic r3 (REFUTED, medium) — từng hạng mục

| # | Hạng mục skeptic r3 | Bằng chứng độc lập rev 4 | Loại | Xử lý rev 4 | Ảnh hưởng tâm |
|---|---|---|---|---|---|
| r3-1 | **(killer)** 130,66 tỷ có thể bị trích KTPL ~50% như tiền lệ 2025 (TM17: 49,95% của quỹ 164,155 gồm 34,1 tích luỹ) | KT25 tr.30 TM17 (ảnh `img_kt25/p33.png`), đọc lại số đến đồng: ĐTPT **39.005.960.171 = 0,30000 × LNST 2024 130.019.867.238** (khớp đến đơn vị nghìn đồng); LN 2024 − ĐTPT − KTPL 81.987.625.000 − QL 314.568.000 = **8,712 tỷ**; cổ tức 42.846.773.000 = 8,712 + **34,135** (đúng bằng phần LN tích luỹ thêm vào quỹ 164,155). Hai năm KTPL/LN năm: 63,06% (2025) và 63,8% (2026) — ổn định; KTPL/quỹ phân phối: 49,95% vs 63,8% — không ổn định. ⇒ quỹ được tính trên LN NĂM; phần tích luỹ vào phân phối 2025 chia **100% cổ tức, 0% quỹ**. Tỷ lệ 49,95% là cách trình bày trên tổng quỹ, không phải tỷ lệ trích trên LN tích luỹ. 130,66 = phần còn lại LN các năm trước, đã trích quỹ ở năm phân phối tương ứng (2023: KTPL 83,5; 2024: 77,58 — §2) | (a) | Giữ base +1.459 (không trích KTPL), nay có cơ sở là số học BCTC kiểm toán thay cho báo chí. **Rủi ro sự kiện còn lại** (ĐHĐCĐ bất thường 20–30/12 chưa biểu quyết; đã hoãn chia 2 lần — ĐHĐCĐ 2025 và 2026) ⇒ độ nhạy, không trọng số chủ quan: KTPL 23,76% ⇒ 5.297; **49,95% ⇒ 4.499** (cả phần KTPL phải chi tiền, vay 8%) / 5.293 (cách skeptic: chỉ phần cổ tức chịu chi phí vốn); 63,8% ⇒ 4.076 / 5.091; không chia ⇒ 4.563. Văn bản ND 167/2024 bản gốc / quy chế quỹ TKV: **không kiểm chứng được** (tìm 23/11 chỉ ra báo chí; luật hiện hành có thể đã đổi theo ND 135/2025) | 0 (base); dải độ nhạy −1.946…0 |
| r3-2 | Rev2→rev3 +32% không có tài liệu gốc mới | Đúng cho rev 3 (dựa báo chí). Rev 4 thay cơ sở bằng TM17 số học (r3-1) — tài liệu có từ trước nhưng đọc khác: rev 3 khẳng định "đã trích quỹ" mà không chứng minh; rev 4 chứng minh bằng ĐTPT = 30,000% × LN 2024 | (a) | Như r3-1 | 0 |
| r3-3 | Bi quan có thể quá nhẹ: KTPL gần cố định theo quỹ lương (2022: 55,9 trên LN 106,6) | KT25 TM17 + Q3 p4: KTPL 82,30 (LN 130,02) → 52,76 (LN 82,75): mức tuyệt đối giảm 36% cùng chiều LN, tỷ lệ giữ 63,3% / 63,8% ⇒ hai năm gần nhất tỷ lệ, không cố định. Số 52,76 là số suy từ BCĐKT (LNST chưa PP 213,41 + 15,884 LN 9T − 146,55 = 82,744 đã phân phối; ĐTPT không đổi; − cổ tức 29,99) — khớp LN 2025 82,749 tới 0,005 tỷ, nhưng số trích KTPL công bố riêng: **không kiểm chứng được** | (b) | Giữ quy tắc; độ nhạy cố định 50 / 70 tỷ ⇒ 5.848 / 2.702 (rev 3 §2 ghi sai số rev 2 — đã sửa, r3-7) | 0 |
| r3-4 | Thiếu kịch bản tái cơ cấu TKV (đề án hạn 27/11/2026) — thoái vốn/hoán đổi theo sổ sách | Giá trị sổ sách/cp = 961,32 tỷ / 42.846.773 = **22.436 đ** [Q3 p4]. Không có đề án, tỷ lệ hoán đổi hay phương pháp định giá công bố | (c) | **Không kiểm chứng được**; chỉ hiển thị, không vào base/vùng: nếu xác suất thoái vốn ở giá sổ sách 5% / 10% / 20% ⇒ 6.843 / 7.663 / 9.305. Chiều ngược (sáp nhập hoán đổi theo thu nhập ⇒ ≈ tâm mô hình) không làm giảm thêm | +821…+3.283 (hiển thị) |
| r3-5 | Chi phí vay 8% × 19 năm cho khoản chia có thể quá nặng (giá cost-plus có thể bù lãi vay) | Không có hợp đồng phối hợp kinh doanh/quy chế giá TKV trong src; Q3 p8 chỉ nêu "doanh thu, chi phí quyết toán với Tập đoàn vào cuối năm" | (b) | Giữ base vay 8% (chiều rẻ, thận trọng). Độ nhạy: tiền nhàn rỗi 4% ⇒ 6.515; TKV bù toàn bộ chi phí vốn ⇒ **7.337** | 0 (base); +493…+1.315 |
| r3-6 | Giấy phép / phương án phục hồi Khe Chàm II (ký quỹ 42,31) | KT25 tr.18 TM6b (`img_kt25/p21.png`): ký quỹ Khe Chàm II 42.312.942.141 **không đổi** 01/01/25 → 31/12/25 (không nộp thêm trong 2025); dự án "Khai thác lộ thiên mỏ Khe Chàm II" của CTCP Than Tây Nam Đá Mài theo QĐ 1752/QĐ-BTNMT 23/09/2013; lãi ký quỹ 11,82 tỷ | (c) | Thời hạn giấy phép, dự toán phục hồi tổng: **không kiểm chứng được** (không có trong BCTC). Không thấy dòng tiền ra định kỳ ⇒ không đổi C | 0; nếu phải nộp thêm 42 tỷ một lần ≈ −1.000 đ/cp (ước lượng, = 42,3 tỷ / 42,85 tr cp) |
| r3-7 | §2 còn số độ nhạy rev 2 (7.787 / 4.389 / 1.243) | `calc_rev4/model_out_rev4.json` `sens` | (a) | Sửa thành 9.246 / 5.848 / 2.702 | 0 |
| r3-8 | Vốn còn phải chi dự án mở rộng ~1.020 tỷ chỉ là ước lượng | Không có lịch giải ngân trong src | (c) | Giữ như rev 3: độ nhạy −3.017, hiển thị P 0,3 ⇒ 5.117; **không kiểm chứng được** | 0 |

**Chiều thay đổi tâm rev 4:** không đổi (6.022 trước CK / 5.837 sau CK). Không hạng mục nào có cơ sở độc lập buộc đổi base: r3-1 được xác
nhận chiều giữ; r3-4, r3-5 (chiều tăng) và rủi ro sự kiện ĐHĐCĐ (chiều giảm) chỉ ở độ nhạy.

## 2. Quỹ khen thưởng phúc lợi — bằng chứng và quy tắc rò rỉ (hạng mục quyết định)

**Phân phối lợi nhuận đã kiểm toán / đã công bố** (tỷ đồng):

| Năm phân phối | LN năm trước được chia | Trích KTPL + thưởng quản lý | % LN | Cổ tức tiền | Trích ĐTPT (giữ trong VCSH) | Nguồn |
|---|---|---|---|---|---|---|
| 2022 | 2021: 106,6 [BQ] | 55,9 (suy từ chuỗi VCSH) | 52% | 64,3 (1.500 đ) | — | BQ: LN − cổ tức − ΔVCSH |
| 2023 | 2022: 339,9 [BQ] | 83,5 (suy từ chuỗi VCSH) | 25% | 64,3 | — | BQ |
| 2024 | 2023: 293,1 | **77,58** = 247,41 − 84,14 ĐTPT − 85,69 cổ tức | 26,5% | 85,69 (2.000 đ) | 84,14 | **KT25 tr.30 TM17** (cột năm trước) |
| 2025 | 2024: **130,02** | **82,30** = KTPL 81,99 + thưởng QL 0,31 | **63,3%** | 42,85 (1.000 đ) | 39,01 | **KT25 tr.30 TM17** (NQ ĐHĐCĐ 01/NQ-TCS-ĐHĐCĐ 25/04/2025) |
| 2026 | 2025: **82,749** | **52,76** = 82,749 − 29,99 cổ tức (ĐTPT không đổi 386,31) | **63,8%** | 29,99 (700 đ) | 0 | **Q3 p4** BCĐKT: LNST chưa PP 213,41 → 146,55; ĐTPT 386,31 cả hai kỳ |

- Quỹ KTPL là **nợ phải trả** (BCĐKT mã 322/323: 53,7 tại 31/12/25; 60,9 tại 30/9/26), chi cho người lao động — không thuộc cổ đông.
- Thứ tự thực tế 2026: KTPL được trích trước, cổ tức nhận phần còn lại, ĐTPT bằng 0 ⇒ KTPL ưu tiên trước cổ đông.
- Tổng 5 năm: rò 352,1 / LN 952,4 = **37,0%** (khớp ước của skeptic). Hai năm gần nhất ổn định ở **63–64%**, mức tuyệt đối 52,8–82,3.

**Quy tắc khoá trong base:** `rò = min(0,64 × N; 82,3)` tỷ/năm.
- 0,64 = tỷ lệ 2 năm gần nhất (63,3% và 63,8%); trần 82,3 = mức tuyệt đối cao nhất đã kiểm toán (2025). Năm LN lớn (2022–23)
  tỷ lệ chỉ 25–27% vì quỹ bị chặn theo mức tuyệt đối — đúng hình dạng min(tỷ lệ; trần).
- Kiểm tra quy tắc trên số thật: N=130,02 ⇒ rò 82,3 (thật 82,30); N=82,75 ⇒ rò 52,96 (thật 52,76); N=293,1 ⇒ rò 82,3 (thật 77,58).
- Không có quy chế trích quỹ của TKV trong src ⇒ cơ chế pháp lý của tỷ lệ 64% **không kiểm chứng được**; quy tắc dựa trên số
  kiểm toán thực tế, không phải văn bản. Độ nhạy (số rev 3/rev 4, gồm khoản chia 130,66): tỷ lệ cố định 37% (TB 5 năm) ⇒ 9.246; cố định 50 tỷ ⇒ 5.848; cố định 70 tỷ ⇒ 2.702.

### 2b. Khoản 130,7 tỷ LN tích luỹ — đã trích quỹ, chờ chia cổ tức (VÀO BASE từ rev 3; cơ sở thay ở rev 4)
- **Rev 4 — bằng chứng số học từ TM17 kiểm toán** (NQ 01/NQ-TCS-ĐHĐCĐ 25/04/2025, "phân phối lợi nhuận năm 2024"):

| Khoản (VND) | Số tiền | / LNST 2024 130.019.867.238 | / quỹ 164.154.926.171 |
|---|---|---|---|
| Trích ĐTPT | 39.005.960.171 | **30,000%** | 23,76% |
| Trích KTPL | 81.987.625.000 | 63,06% | 49,95% |
| Thưởng quản lý | 314.568.000 | 0,24% | 0,19% |
| Cổ tức | 42.846.773.000 | 32,95% | 26,10% |
| LN 2024 còn lại sau 3 quỹ | 8.711.714.067 | | |
| Phần LN tích luỹ đưa vào (164,155 − 130,020) | 34.135.058.933 | | |
| 8,712 + 34,135 | **42,847 = cổ tức** | | |

  ĐTPT khớp 30% LN năm tới từng nghìn đồng ⇒ các quỹ tính trên LN năm; phần tích luỹ chỉ đi vào cổ tức. Đọc ngược của skeptic r3
  (49,95% áp cả lên phần tích luỹ) cho ĐTPT = 23,76% × 164,155 = 39,006 — trùng số, nên tỷ lệ trên quỹ không phân biệt được hai cách;
  điểm phân biệt là ĐTPT = đúng 30,000% LN năm (mức trần phổ biến của quỹ ĐTPT), còn 23,76% không phải tỷ lệ tròn. Đây là suy luận
  từ số kiểm toán, không phải văn bản quy chế — mức tin cậy: trung bình-cao.
- Rev 3 (giữ để đối chiếu):
- KT25 tr.7 BCĐKT: LNST chưa phân phối lũy kế đến cuối năm trước (421a) **130,66** tại 31/12/25; không đổi tại 30/9/26 (420a, Q3 p4).
- Nguồn gốc: năm 2025 quỹ 294,82 (LN tích luỹ 164,8 + LN 2024 130,02) → trích ĐTPT 39,01 + KTPL 81,99 + QL 0,31 = **121,31** và
  cổ tức 42,85 [KT25 tr.30 TM17] ⇒ còn 130,66 = phần **đã qua trích quỹ**.
- Tài liệu ĐHĐCĐ 2025 (theo Markettimes/Stockbiz 24/04/2025, báo chí): "Phần lợi nhuận còn lại chưa phân phối là 130 tỷ đồng sẽ
  thực hiện chi trả cổ tức vào kỳ ĐHĐCĐ thường niên tiếp theo"; bài dẫn **ND 167/2024/NĐ-CP**: doanh nghiệp Nhà nước nắm >50% phải
  chia hết LN còn lại sau trích quỹ bằng tiền/cổ phiếu (văn bản ND chưa đọc trực tiếp).
- ĐHĐCĐ 2026 chưa chia khoản này (chỉ chia LN 2025). NQ HĐQT 40/NQ-TCS-HĐQT 06/11/2026: ĐHĐCĐ bất thường "thông qua phương án
  phân phối lợi nhuận và chi trả cổ tức" theo công văn TKV 7788/TKV-KSNB (rev 1 §6, file gốc đã đọc 11/11).
- ⇒ Base: chia **130,66 tỷ (≈3.050 đ/cp) tiền mặt, không trích thêm KTPL** (quỹ đã trích trên LN năm tương ứng; tiền lệ 2025: phần tích luỹ 100% cổ tức).
- Rủi ro sự kiện (độ nhạy, không vào base): ĐHĐCĐ bất thường quyết khác — xem §8d. Vì khung mô hình coi B₀ bị khoá tới
  2045 (hệ số 0,045), khoản chia được ghi nhận riêng: +D − (lãi vay sau thuế 6,4% × D × annuity) − D·(1+r)^−19 = **+1.459 đ/cp**.

## 3. Bảng cân đối, dòng tiền, quyền khai thác, TKV, cổ đông, thanh khoản

Không đổi so với rev 1 — xem REPORT.md §2–§6 (số đã được skeptic r1 đối chiếu BQ: VCSH 961,3 / 1.028,2 khớp). Bổ sung rev 2:
- **Ký quỹ môi trường** [KT25 tr.18]: gốc 160,31 (Khe Chàm II 42,31; Cao Sơn 118,00) + lãi phải thu 41,94 = 202,26 tại 31/12/25;
  212,2 tại 30/9/26 [Q3 p25]. Theo QĐ 1752/QĐ-BTNMT (2013) và 3928/QĐ-BTNMT (30/12/2022).
- **Dự án mở rộng Cao Sơn** [KT25 tr.19]: tổng mức đầu tư 1.829,52 tỷ, 70% vay thương mại / 30% vốn chủ, khởi công 09/2023,
  hoạt động tới 08/2045; XDCBDD dự án 29,48 (31/12/25). Dự án xưởng sửa chữa ô tô 107,68 tỷ, XDCBDD 72,89.
- **Thuế tài nguyên** lũy kế 9T/26 605,1 tỷ, đã nộp 628,6 [Q3 p43].
- Lịch sử cổ tức tiền (đ/cp): 1.200 (2021), 1.500 (2022–23), 2.000 (2024), 1.000 (2025), 700 (2026) [BQ Dividend_1Y; TM17].

## 4. Pháp lý và quản trị — chỉ WARNING (không vào base)

Kịch bản tái cơ cấu TKV đã thêm ở §8d (hiển thị, không kiểm chứng được). Không đổi so với rev 1 §7: tái cơ cấu TKV (đề án hạn 27/11/2026), giao dịch bên liên quan chiếm phần lớn, đổi kiểm toán AASC →
PKF-TTG (cả hai ý kiến sạch), dòng 17 LCTT 9T dấu bất thường, chưa tra UBCKNN/HNX. Không có vụ án/xử phạt trong tài liệu đã đọc.
Bổ sung: **ưu tiên KTPL trước cổ đông** là rủi ro quản trị cho cổ đông thiểu số (TKV 65,14% quyết phân phối) — đã định lượng ở §2.

## 5. Vị thế và lợi thế cạnh tranh (5F, V5)

Đánh giá đầy đủ làm ngày 11/11/2026 (<12 tháng) ⇒ tái dùng REPORT.md §9: **moat_tier NONE**, moat_type: không (nhà thầu giá vốn
cộng lãi cho một khách hàng nội bộ), rủi ro số 1: TKV quyết giá chuyển giao và phân phối. Kiểm nhanh rev 2: (i) TM17 xác nhận
thêm quyền thặng dư thuộc người lao động trước cổ đông — củng cố NONE; (ii) 97,2% DT 9T/26 bán cho đơn vị TKV [Q3 p21–22] không đổi.
Không thưởng, không trừ (V5).

## 8. Định giá — mù giá; tâm do mô hình quyết

### 8a. Khung (giữ nguyên rev 1, chỉ đổi N)
- Thu nhập thặng dư hữu hạn tới 08/2045, T = 19, thu hồi 50% sổ sách cuối kỳ (ước lượng), g = 0.
- V = ρ·B₀·(1+r)^−T + N_cổ đông × [1 − (1+r)^−T]/r. Đây là dạng rút gọn đại số của công thức rev 1
  (B₀ + Σ(N − rB₀)/(1+r)^t − (1−ρ)B₀(1+r)^−T); kiểm tái lập: với rò = 0, C = 0, B₀ = 961,3 ⇒ **13.084** = tâm rev 1 (khớp).
- Hệ số annuity 6,739; hệ số của B₀ chỉ 0,045 ⇒ giá trị gần như hoàn toàn đến từ N cổ đông.
- B₀ = 961,32 − 10,16 = 951,16 tỷ. C (capex tuân thủ, ký quỹ) = 5,21 tỷ/năm.
- Cộng khoản chia 130,66 (§2b): +1.459 đ/cp ở mọi kịch bản (tính lại theo r khi chạy độ nhạy r).

### 8b. Chi phí vốn (V1)
- **r = 13,5%**: `effective_deposit_rate('2026-11-23')` = **7,40%** (cctg_12m ngày 02/11/2026; Big-4 6,8%) = mức neo ⇒ Δ = 0, β = 1.
- Độ nhạy: −100bp ⇒ 6.291 (+4,5%); −50bp ⇒ 6.152 (+2,2%); +50bp ⇒ 5.901 (−2,0%); +100bp ⇒ 5.787 (−3,9%).
  β = 0,5 ⇒ Δ lãi huy động 1 điểm chỉ dịch r 0,5 điểm ⇒ biên độ bằng nửa dòng ±50bp.
- Báo kèm dải Ke nội địa (D4): r = 12,3% ⇒ 6.349; r = 13,4% ⇒ 6.047. r = 12% ⇒ 6.440; r = 11% ⇒ 6.771 (chiều rẻ skeptic r1).

### 8c. Kịch bản (trọng số chủ quan, ước lượng — giữ nguyên rev 1)

| Kịch bản | Trọng số | N (LNST, tỷ/năm) | Rò KTPL | C | **N cổ đông** | Cơ sở N | Giá trị/cp (gồm +1.459 chia 130,7) | Sau CK 0,3 tỷ |
|---|---|---|---|---|---|---|---|---|
| Bi quan | 30% | 35 | 22,4 | 5,21 | **7,39** | KH 2026 >36 (báo chí); 9T/26 thực 15,88 | 3.622 | **3.511** |
| Cơ sở | 45% | 75 | 48,0 | 5,21 | **21,79** | LNST TTM Q4/25–Q3/26 = 75,2 [KT25, Q3] | 5.887 | 5.706 |
| Lạc quan | 25% | 130 | 82,3 | 5,21 | **42,49** | LNST 2024 kiểm toán 130,02 | 9.143 | **8.862** |
| **Tâm** | | | | | | | **6.022** | **5.837** |

Đối chiếu thực tế: N cổ đông lạc quan 42,5 ≈ cổ tức thật chi từ LN 2024 (42,85); cơ sở 21,8 vs cổ tức từ LN 2025 29,99.

### 8d. Độ nhạy khác (không vào base)

| Hạng mục | Tâm (trước CK) | Δ đ/cp | Loại |
|---|---|---|---|
| α = 0,50 (49,95% của TM17 áp lên N), trần 82,3 | 7.677 | +1.655 | (b) quy tắc KTPL — r2-1 |
| Rò = 37% cố định (TB 5 năm) | 9.246 | +3.224 | (b) |
| Rò cố định 50 tỷ / 70 tỷ | 5.848 / 2.702 | −174 / −3.320 | (b) — 70 tỷ trái số thật 2026 |
| Không chia 130,7 (như rev 2) | 4.563 | −1.459 | (b) |
| ĐHĐCĐ trích KTPL 23,76% / 49,95% / 63,8% từ khoản chia — cả phần KTPL phải chi tiền (vay 8%) | 5.297 / **4.499** / 4.076 | −725 / −1.523 / −1.946 | (b) rủi ro sự kiện r3-1 |
| Như trên, chỉ phần cổ tức chịu chi phí vốn (cách skeptic r3) | 5.675 / 5.293 / 5.091 | −347 / −729 / −931 | (b) |
| Như trên, chia từ tiền nhàn rỗi 4% | 5.791 / 4.992 / 4.570 | | (b) |
| TKV bù toàn bộ chi phí vốn khoản chia (cost-plus) | 7.337 | +1.315 | (b) r3-5 |
| Tái cơ cấu TKV: thoái vốn ở giá sổ sách 22.436 đ/cp, xác suất 5% / 10% / 20% | 6.843 / 7.663 / 9.305 | +821 / +1.641 / +3.283 | (c) r3-4, hiển thị |
| Khe Chàm II phải nộp thêm ký quỹ ~42 tỷ một lần (ước lượng) | ~5.035 | ~−987 | (c) r3-6 |
| Chia 130,7 từ tiền nhàn rỗi (4%/năm sau thuế) | 6.515 | +493 | (b) |
| Bỏ C (không coi ký quỹ là dòng tiền ra) | 6.841 | +819 | (b) |
| Lãi ký quỹ 5,9 tỷ/năm bị khoá (không thuộc cổ đông) | 5.094 | −928 | (c) không kiểm chứng được dự toán phục hồi |
| Đóng mỏ 2030 (T=4) | 8.882 | +2.860 | (b) — cao hơn base vì N cổ đông ≪ r·B; phụ thuộc giả định thu hồi 50% sổ sách (ước lượng) |
| ρ = 1,0 / ρ = 0 | 7.023 / 5.021 | +1.001 / −1.001 | (c) |
| Dự án mở rộng: 30% vốn chủ của ~1.020 tỷ còn lại (ước lượng) chỉ sinh ROE 7,9% | — | **−3.017** | (b) chiều giảm; V4a giữ NPV=0 trong base |
| **Hiển thị:** tâm điều chỉnh rủi ro dự án, P = 0,3 (ước lượng chủ quan) | **5.117** | −905 | chỉ hiển thị, không vào sổ |

### 8e. Thanh khoản (V3) — `calc_rev2/px_cst.csv` (khối lượng thật BQ, đến 11/11/2026)
σ ngày 2,04%; ADV60 0,132 tỷ; ADV250 0,199 tỷ. Chiết khấu = σ·√(Q/ADV60).

| Cỡ | CK | Tâm sau CK | Bi quan / Lạc quan sau CK | Số phiên thoát @10–20% ADV60 |
|---|---|---|---|---|
| 1,0 tỷ | 5,6% | 5.684 | 3.419 / 8.630 | 38–76 |
| 0,3 tỷ | 3,1% | **5.837** | **3.511 / 8.862** | 11–23 |
| 0,1 tỷ | 1,8% | 5.915 | 3.558 / 8.981 | 4–8 |

Free float tối đa 34,86% (TKV 65,14%). Nhãn theo giá trị SAU chiết khấu ở cỡ 0,3 tỷ.

### 8f. Hai nền + cờ phân kỳ (V6) — CHỈ HIỂN THỊ

| Nền | Giá trị/cp | Cách tính |
|---|---|---|
| V_ngắn | 3.767 | N cổ đông cơ sở 21,79 / r, g = 0 (tái đầu tư 0) |
| V_dài | 11.098 | FCFE TB 2024–25 = (84,76 + 43,63)/2 / r (công thức rev 1) |
| D = \|ln(V_ngắn/V_dài)\| | **1,08** | > ln2 (0,69), < ln3 (1,10) |

- **D > ln2 ⇒ giải thích nguồn chênh:** FCFE 2024–25 gồm **vay ròng +57,3 và +229,7 tỷ** (KT25 tr.9, tiền thu/trả gốc vay) để tài
  trợ capex dự án mở rộng; bỏ vay ròng, FCFE còn 27,4 và −186,1 ⇒ V_dài bị thổi bởi nợ, không phải dòng tiền bền. Chi KTPL đã nằm
  trong CFO nên V_dài không tính hai lần quỹ này.
- V_ngắn/V_dài không gồm khoản chia 130,7 (khoản một lần). Vùng đọc mở rộng (hiển thị): [3.767; 11.098]. Tâm/vùng/nhãn/luật
  0,85×tâm vẫn từ mô hình §8c; không trộn hai nền.
- C4 / D2: chưa qua tiêu chí khoá trước, chỉ theo dõi — không tính lại ở rev 2 (xem REPORT.md §8).

### 8g. Pha sau khoá — so với giá
- Giá đóng cửa 20/11/2026 **14.100** [BQ `ticker`; dữ liệu lịch sử, không phải cùng ngày]. Rev 1 dùng 14.900 (11/11).
- 14.100 / 5.837 = 2,42 lần tâm; cao hơn lạc quan sau CK 8.862 khoảng 59% ⇒ **TRÊN vùng**.
- Định giá ngược: để giá trị = 14.100 cần N cổ đông ≈ (604,1 − 0,045×951 − 62,5 khoản chia) / 6,739 ≈ **74,0 tỷ/năm**, tức LNST ≈
  **161,5 tỷ/năm** sau rò 82,3 và C 5,2 (tự tính) — cao hơn LNST mọi năm 2024–26 (130,0 / 82,7 / TTM 75,2), chỉ đạt ở năm đỉnh
  2022–23 (339,9 / 293,1).
- Giá có thể đang định giá cổ tức đặc biệt ≈3.050 đ/cp (§2b) — đã nằm trong tâm (phần +1.459 sau chi phí vốn).

## 9. Sizing (V8)
Chuẩn 2–4% NAV/mã — **không áp dụng**: giá trên vùng, không có biên an toàn. Ràng buộc thanh khoản riêng: cỡ >0,3 tỷ cần >11–23
phiên để thoát. Không đề xuất vị thế.

## 10. Mốc khoá trước và điều kiện đổi nhận định (cả hai chiều)
- **Tăng tâm (khoá lại, rev mới):** (i) quy chế trích KTPL của TKV / NQ phân phối LN 2026 cho thấy α ≤ 0,50 ⇒ hạ α;
  (ii) LNST năm 2026 kiểm toán > 130 tỷ; (iii) chia 130,7 bằng tiền sẵn có không vay.
- **Giảm tâm:** (o) NQ ĐHĐCĐ bất thường KHÔNG chia 130,7 (⇒ −1.459) hoặc trích KTPL từ khoản này (49,95% ⇒ −729…−1.523).
- **Tăng tâm:** (iv) đề án tái cơ cấu TKV công bố thoái vốn/hoán đổi theo giá sổ sách (22.436 đ/cp).
- **Giảm tâm:** (i) BCTC 2026 kiểm toán cho LNST < 35 tỷ; (ii) dự toán phục hồi môi trường / lịch ký quỹ cho thấy nghĩa vụ > 5,2
  tỷ/năm; (iii) thông tin vốn còn phải chi dự án mở rộng và suất sinh lời dưới r ⇒ đưa kịch bản −3.017 vào trọng số.
- Hết hạn DD: BCTC Q4/2026 (~20/01/2027) hoặc 120 ngày.

## 11. Bối cảnh vĩ mô — chỉ hiển thị
Không đổi so với rev 1 §11 (lãi huy động 12T hiệu dụng 7,40% không đổi từ 02/11).

## Phụ lục A — Nguồn số mới của rev 2
| Số | Nguồn |
|---|---|
| Phân phối LN 2024: ĐTPT 39,006; KTPL 81,988; thưởng QL 0,315; cổ tức 42,847; tổng 164,155 | KT25 tr.30 TM17 (ảnh `img_kt25/p33.png`) |
| Biến động VCSH năm 2024: phân phối 247,41 trong đó ĐTPT 84,14; LN 2023 → VCSH | KT25 tr.30 TM17 cột năm trước; cổ tức 2.000 đ × 42.846.773 = 85,69 |
| LNST chưa PP 213,41 → 146,55; ĐTPT 386,31 không đổi; quỹ KTPL 53,72 → 60,94 | Q3 p4 (BCĐKT) |
| LNST 2025 82,749; 2024 130,020 | KT25 tr.30 TM17 |
| Ký quỹ môi trường theo dự án, lãi ký quỹ | KT25 tr.18 TM6b (`img_kt25/p21.png`) |
| Dự án mở rộng 1.829,52 tỷ, 70/30, 09/2023 → 08/2045 | KT25 tr.19 TM8 (`img_kt25/p22.png`) |
| Thuế tài nguyên 9T/26 605,1 | Q3 p43 |
| LNST quý, VCSH, cổ tức 2020Q4–2026Q3 | BQ `ticker_financial` (truy vấn trong phiên job này) |
| r neo 7,40% | `deposit_rate_vn.effective_deposit_rate('2026-11-23')` |
| 130 tỷ "sẽ chi trả cổ tức vào kỳ ĐHĐCĐ thường niên tiếp theo"; ND 167/2024 | stockbiz.vn (Markettimes) 24/04/2025 "CST: Trước thềm ĐHĐCĐ, Than Cao Sơn - TKV bị cổ đông phản đối phương án giữ lại 130 tỷ đồng lợi nhuận sau thuế" (báo chí) |
| Ước LN 2025 ~51 tỷ, KH 2026 >36 tỷ | thoibaotaichinhvietnam.vn bài "Than Cao Sơn - TKV đặt mục tiêu lợi nhuận 2026 chỉ hơn 36 tỷ đồng" (báo chí, không phải NQ gốc) |

## Phụ lục A2 — Nguồn số mới của rev 4
| Số | Nguồn |
|---|---|
| ĐTPT 39.005.960.171 = 30,000% × LNST 2024 130.019.867.238; KTPL 81.987.625.000; QL 314.568.000; cổ tức 42.846.773.000; quỹ 164.154.926.171 | KT25 tr.30 TM17 (`img_kt25/p33.png`), đọc lại 23/11 |
| Ký quỹ Khe Chàm II 42.312.942.141 không đổi 2025; QĐ 1752/QĐ-BTNMT 23/09/2013; lãi ký quỹ 11.815.348.509 | KT25 tr.18 TM6b (`img_kt25/p21.png`) |
| Giá trị sổ sách/cp 22.436 | VCSH 961,322 tỷ [Q3 p4] / 42.846.773 cp |
| Độ nhạy rev 4 | `calc_rev4/model_out_rev4.json` khóa `sens_rev4` |

## Phụ lục B — Chưa làm / giới hạn
- (rev 4) ND 167/2024 bản gốc và quy chế quỹ TKV: tìm web 23/11 chỉ ra báo chí ⇒ không kiểm chứng được; NQ ĐHĐCĐ bất thường chưa có.
- (rev 4) Thời hạn giấy phép/dự toán phục hồi Khe Chàm II; đề án tái cơ cấu TKV: không kiểm chứng được.
- NQ ĐHĐCĐ thường niên 2026 gốc và quy chế trích quỹ của TKV: không có ⇒ α = 0,64 dựa trên số thực tế 2026 (năm duy nhất quỹ
  phân phối = LN năm), không phải văn bản. ND 167/2024 chỉ đọc qua báo chí.
- Dự toán chi phí phục hồi môi trường và lịch ký quỹ còn lại (QĐ 3928/QĐ-BTNMT): không có.
- Vốn còn phải chi dự án mở rộng: chỉ ước lượng (~1.020 tỷ).
- Biểu thuế suất tài nguyên: không đọc được trong BCTC.
- Chưa tra pháp lý bên ngoài (UBCKNN/HNX/báo chí) — giữ như rev 1.
