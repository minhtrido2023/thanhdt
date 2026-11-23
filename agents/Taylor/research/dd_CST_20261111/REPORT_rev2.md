# DD — CST (CTCP Than Cao Sơn – TKV, HNX) · REV 2 · 2026-11-23 · job `Taylor_20261123_001043`

> NGHIÊN CỨU READ-ONLY, không phải khuyến nghị mua; người quyết là user. Rev 2 dựng lại sau phản biện
> fundamental-skeptic DD_GENERAL r1 (22/11/2026, REFUTED, `skeptic/r1.json`). Bản rev 1 (`REPORT.md`, 11/11) giữ nguyên,
> không ghi đè. Mục nào rev 2 không viết lại thì **giữ nguyên nội dung rev 1** và ghi rõ "xem REPORT.md §x".
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
> - Mô hình: `calc_rev2/model_rev2.py` → `calc_rev2/model_out_rev2.json`; giả định khoá `calc_rev2/assumptions_rev2.json`
>   md5 **`72300e340e9e774f492b359e30bd0814`**; toàn bộ md5 ở `calc_rev2/MD5_LOCK.txt`. `px_cst.csv` (dữ liệu thanh khoản đến
>   11/11) bị mất cùng đợt TRIM, khôi phục từ git, md5 `c34c4e9f0bbcee540ea653f74235f31a`.
> - `bin/dd_assumptions_lint.py` chạy: 20 cảnh báo schema v1 (file dùng định dạng cũ của rev 1), rc=0 chế độ cảnh báo; khoá bằng md5.
> - **Mù giá:** giả định khoá trước khi đọc giá mới. Giá chỉ đọc ở pha sau khoá (§8): đóng cửa 20/11/2026 = 14.100 [BQ `ticker`].

## 0. Kết luận

**Tâm giá trị mới: 4.563 đ/cp trước chiết khấu thanh khoản, 4.422 sau chiết khấu (cỡ 0,3 tỷ).** Rev 1: 13.084 / 12.681 ⇒ **−65%**.
- **Vùng (sau CK 0,3 tỷ):** bi quan **2.097** — lạc quan **7.448**. Ngưỡng luật 0,85×tâm = **3.759**.
- **Nhãn (pha sau khoá):** giá 14.100 (20/11) **TRÊN vùng** — cao hơn cả kịch bản lạc quan ~89%, gấp ~3,2 lần tâm. Không có biên an toàn.
- **Nguyên nhân giảm (một hạng mục quyết định):** rev 1 dùng N = LNST gộp. BCTC kiểm toán cho thấy **quỹ khen thưởng phúc lợi
  (KTPL) lấy đi 63–64% LNST hai năm gần nhất** (82,3/130,0 và 52,8/82,7 tỷ) và được trích TRƯỚC cổ tức. Phần LN thực sự thuộc
  cổ đông ≈ đúng bằng cổ tức đã chi (42,8 và 30,0 tỷ). Rev 2 dùng N cổ đông = LNST − trích KTPL − dòng tiền ra tuân thủ (ký quỹ
  môi trường).
- **Bản chất doanh nghiệp không đổi so với rev 1:** đơn vị gia công khai thác theo giá vốn cộng lãi cho TKV (97% DT nội bộ), mỏ
  hữu hạn tới 08/2045, moat NONE.
- **Chiều tăng còn mở (không vào base):** chia 130,7 tỷ LN tích luỹ ở ĐHĐCĐ bất thường 20–30/12 (+~1.459 đ/cp nếu chia hết, vay
  để chia, không trích KTPL); r thấp hơn (r=11% ⇒ 5.671). Không kịch bản hợp lý nào trong §8c đưa tâm lên gần giá hiện tại.

## 1. Đính chính so với rev 1 — từng hạng mục skeptic r1 → xử lý

| # | Hạng mục skeptic r1 | Bằng chứng độc lập rev 2 | Xử lý |
|---|---|---|---|
| 1 | **Quỹ KTPL / LN rời VCSH ngoài cổ tức** (killer objection) | KT25 tr.30 TM17 + Q3 p4 + BQ (§2) | **(a) VÀO BASE**: N_cổ đông = N − min(0,64·N; 82,3). Tâm 13.084 → 4.563 |
| 2 | Vốn còn phải chi dự án mở rộng Cao Sơn (1.829,5 tỷ) chưa có số; NPV=0 mâu thuẫn ROE<r | KT25 tr.19: tổng mức 1.829,5, 70% vay, XDCBDD dự án 29,5 tại 31/12/25; capex 2023–9T/26 cộng ~810 (gồm cả duy tu) | **(b) ĐỘ NHẠY**, không vào base (V4a: dự án tăng trưởng NPV=0). Phần còn phải chi ≥~1.020 tỷ **(ước lượng)**; nếu 30% vốn chủ (~306) chỉ sinh ROE 7,9% ⇒ **−3.017 đ/cp**. Xác suất không định lượng được |
| 3 | Nghĩa vụ hoàn nguyên/đóng mỏ ngoài ký quỹ 212 | KT25 tr.18 TM6b: ký quỹ gốc Cao Sơn 112,79 → 118,00 (+5,21/2025), Khe Chàm II 42,31 không đổi; lãi ký quỹ 41,94 | **(a) VÀO BASE phần đo được**: nộp ký quỹ 5,21 tỷ/năm = capex tuân thủ (V4b), trừ khỏi N suốt vòng đời (−819 đ/cp). **(c) Không kiểm chứng được**: dự toán chi phí phục hồi tổng và số năm còn phải nộp (QĐ 3928/QĐ-BTNMT không có trong src). Lãi ký quỹ ~5,9 tỷ/năm ghi vào thu nhập nhưng bị khoá ⇒ độ nhạy −928 đ/cp |
| 4 | Thuế suất tài nguyên chưa đọc | Q3 p43 (báo cáo nghĩa vụ NSNN, mẫu 19-TM-TKV): thuế tài nguyên phải nộp lũy kế 9T/26 **605,1 tỷ** = 10,9% DT 9T 5.566,7 (tự tính) | **(c)** Thuế suất theo biểu không ghi trong BCTC ⇒ không kiểm chứng được từ nguồn gốc. Không đổi base: theo cơ chế giá vốn cộng lãi, thuế tài nguyên nằm trong giá giao TKV; rủi ro là thay đổi biểu thuế mà TKV không bù (độ nhạy định tính) |
| 5 | Chiều RẺ: r=13,5% có thể cao cho đơn vị cost-plus | `effective_deposit_rate('2026-11-23')` = 7,40% (cctg_12m 02/11) = neo | **Giữ r=13,5%** cho tâm (luật V1, β=1). Báo kèm r=11% ⇒ 5.671 (+24%), dải Ke 12,3–13,4% ⇒ 5.048–4.600 (§8b) |
| 6 | Kịch bản bi quan dựa trên báo chí; mâu thuẫn −28%/−56% chưa giải | Thời báo Tài chính: KH 2026 "hơn 36 tỷ, giảm hơn 28% so với thực hiện 2025", bài cùng nêu **ước LN 2025 ~51 tỷ** (trước kiểm toán) | **Đã giải mâu thuẫn**: −28% là so ước thực hiện chưa kiểm toán (~51), không phải 82,75 kiểm toán. NQ ĐHĐCĐ gốc vẫn không có ⇒ nguồn vẫn là báo chí; kiểm chéo: LNST 9T/26 thực tế 15,88 [Q3 p5] thấp hơn nhịp kế hoạch. Giữ N bi quan 35, trọng số 30% |
| 7 | Data provenance: src bị TRIM, không mở lại được BCTC gốc | Khôi phục nguyên byte từ git, md5 ở đầu báo cáo; đọc lại trực tiếp TM17, BCĐKT, TM6, TM8 | Đã khắc phục |
| 8 | N theo chu kỳ (~106) làm đảo nhãn (rev 1 tự nêu) | Với KTPL: N=106 ⇒ N cổ đông 106−67,8−5,2 = 33,0 ⇒ ~6.200 đ/cp (tự tính cùng công thức) | Không còn đảo nhãn |

Thay đổi khác: B₀ trừ thêm 10,16 tỷ = 0,64 × LNST 9T/26 15,884 (phần LN đã nằm trong VCSH 30/9 sẽ bị trích KTPL khi phân phối;
ảnh hưởng ≈ −11 đ/cp vì hệ số của B trong mô hình chỉ 0,045, xem §8a).

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
  kiểm toán thực tế, không phải văn bản. Độ nhạy: tỷ lệ cố định 37% (TB 5 năm) ⇒ 7.787; cố định 50 tỷ ⇒ 4.389; cố định 70 tỷ ⇒ 1.243.

## 3. Bảng cân đối, dòng tiền, quyền khai thác, TKV, cổ đông, thanh khoản

Không đổi so với rev 1 — xem REPORT.md §2–§6 (số đã được skeptic r1 đối chiếu BQ: VCSH 961,3 / 1.028,2 khớp). Bổ sung rev 2:
- **Ký quỹ môi trường** [KT25 tr.18]: gốc 160,31 (Khe Chàm II 42,31; Cao Sơn 118,00) + lãi phải thu 41,94 = 202,26 tại 31/12/25;
  212,2 tại 30/9/26 [Q3 p25]. Theo QĐ 1752/QĐ-BTNMT (2013) và 3928/QĐ-BTNMT (30/12/2022).
- **Dự án mở rộng Cao Sơn** [KT25 tr.19]: tổng mức đầu tư 1.829,52 tỷ, 70% vay thương mại / 30% vốn chủ, khởi công 09/2023,
  hoạt động tới 08/2045; XDCBDD dự án 29,48 (31/12/25). Dự án xưởng sửa chữa ô tô 107,68 tỷ, XDCBDD 72,89.
- **Thuế tài nguyên** lũy kế 9T/26 605,1 tỷ, đã nộp 628,6 [Q3 p43].
- Lịch sử cổ tức tiền (đ/cp): 1.200 (2021), 1.500 (2022–23), 2.000 (2024), 1.000 (2025), 700 (2026) [BQ Dividend_1Y; TM17].

## 4. Pháp lý và quản trị — chỉ WARNING (không vào base)

Không đổi so với rev 1 §7: tái cơ cấu TKV (đề án hạn 27/11/2026), giao dịch bên liên quan chiếm phần lớn, đổi kiểm toán AASC →
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

### 8b. Chi phí vốn (V1)
- **r = 13,5%**: `effective_deposit_rate('2026-11-23')` = **7,40%** (cctg_12m ngày 02/11/2026; Big-4 6,8%) = mức neo ⇒ Δ = 0, β = 1.
- Độ nhạy: −100bp ⇒ 4.961 (+8,7%); −50bp ⇒ 4.755 (+4,2%); +50bp ⇒ 4.383 (−3,9%); +100bp ⇒ 4.214 (−7,6%).
  β = 0,5 ⇒ Δ lãi huy động 1 điểm chỉ dịch r 0,5 điểm ⇒ biên độ bằng nửa dòng ±50bp.
- Báo kèm dải Ke nội địa (D4): r = 12,3% ⇒ 5.048; r = 13,4% ⇒ 4.600. r = 12% ⇒ 5.182; r = 11% ⇒ 5.671 (chiều rẻ skeptic).

### 8c. Kịch bản (trọng số chủ quan, ước lượng — giữ nguyên rev 1)

| Kịch bản | Trọng số | N (LNST, tỷ/năm) | Rò KTPL | C | **N cổ đông** | Cơ sở N | Giá trị/cp | Sau CK 0,3 tỷ |
|---|---|---|---|---|---|---|---|---|
| Bi quan | 30% | 35 | 22,4 | 5,21 | **7,39** | KH 2026 >36 (báo chí); 9T/26 thực 15,88 | 2.163 | **2.097** |
| Cơ sở | 45% | 75 | 48,0 | 5,21 | **21,79** | LNST TTM Q4/25–Q3/26 = 75,2 [KT25, Q3] | 4.428 | 4.292 |
| Lạc quan | 25% | 130 | 82,3 | 5,21 | **42,49** | LNST 2024 kiểm toán 130,02 | 7.684 | **7.448** |
| **Tâm** | | | | | | | **4.563** | **4.422** |

Đối chiếu thực tế: N cổ đông lạc quan 42,5 ≈ cổ tức thật chi từ LN 2024 (42,85); cơ sở 21,8 vs cổ tức từ LN 2025 29,99.

### 8d. Độ nhạy khác (không vào base)

| Hạng mục | Tâm (trước CK) | Δ đ/cp | Loại |
|---|---|---|---|
| Rò = 37% cố định (TB 5 năm) | 7.787 | +3.224 | (b) độ nhạy quy tắc KTPL |
| Rò cố định 50 tỷ / 70 tỷ | 4.389 / 1.243 | −174 / −3.320 | (b) |
| Bỏ C (không coi ký quỹ là dòng tiền ra) | 5.382 | +819 | (b) |
| Lãi ký quỹ 5,9 tỷ/năm bị khoá (không thuộc cổ đông) | 3.635 | −928 | (c) không kiểm chứng được dự toán phục hồi |
| Đóng mỏ 2030 (T=4) | 8.244 | +3.681 | (b) — cao hơn base vì N cổ đông ≪ r·B; phụ thuộc mạnh vào giả định thu hồi 50% sổ sách (ước lượng) |
| ρ = 1,0 / ρ = 0 | 5.564 / 3.562 | +1.001 / −1.001 | (b) |
| Chia hết 130,7 LN tích luỹ (ĐHĐCĐ 12/2026), vay 8%/năm để chia (ước lượng), không trích KTPL | — | **+1.459** | (b) chiều tăng; tỷ lệ chia và phần KTPL từ khoản này chưa công bố |
| Dự án mở rộng: 30% vốn chủ của ~1.020 tỷ còn lại (ước lượng) chỉ sinh ROE 7,9% | — | **−3.017** | (b) chiều giảm; V4a giữ NPV=0 trong base |

### 8e. Thanh khoản (V3) — `calc_rev2/px_cst.csv` (khối lượng thật BQ, đến 11/11/2026)
σ ngày 2,04%; ADV60 0,132 tỷ; ADV250 0,199 tỷ. Chiết khấu = σ·√(Q/ADV60).

| Cỡ | CK | Tâm sau CK | Bi quan / Lạc quan sau CK | Số phiên thoát @10–20% ADV60 |
|---|---|---|---|---|
| 1,0 tỷ | 5,6% | 4.306 | 2.042 / 7.253 | 38–76 |
| 0,3 tỷ | 3,1% | **4.422** | **2.097 / 7.448** | 11–23 |
| 0,1 tỷ | 1,8% | 4.482 | 2.125 / 7.548 | 4–8 |

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
- Vùng đọc mở rộng (hiển thị): [3.767; 11.098]. Tâm/vùng/nhãn/luật 0,85×tâm vẫn từ mô hình §8c; không trộn hai nền.
- C4 / D2: chưa qua tiêu chí khoá trước, chỉ theo dõi — không tính lại ở rev 2 (xem REPORT.md §8).

### 8g. Pha sau khoá — so với giá
- Giá đóng cửa 20/11/2026 **14.100** [BQ `ticker`; dữ liệu lịch sử, không phải cùng ngày]. Rev 1 dùng 14.900 (11/11).
- 14.100 / 4.422 = 3,19 lần tâm; cao hơn lạc quan sau CK 7.448 khoảng 89% ⇒ **TRÊN vùng**.
- Định giá ngược: để giá trị = 14.100 cần N cổ đông ≈ 14.100 × 0,042847 / 6,739 − 0,045 × 951 / 6,739 ≈ **83,3 tỷ/năm** thuộc cổ
  đông, tức LNST ≈ **171 tỷ/năm** sau khi trừ rò 82,3 và C 5,2 (tự tính) — cao hơn LNST mọi năm 2024–26 (130,0 / 82,7 / TTM 75,2),
  chỉ đạt được ở năm đỉnh 2022–23 (339,9 / 293,1).
- Giá có thể đang định giá cổ tức đặc biệt (rev 1 §6): chia hết 130,7 ≈ 3.050 đ/cp tiền mặt; kể cả cộng toàn bộ vào tâm thì tổng
  vẫn dưới 7.500.

## 9. Sizing (V8)
Chuẩn 2–4% NAV/mã — **không áp dụng**: giá trên vùng, không có biên an toàn. Ràng buộc thanh khoản riêng: cỡ >0,3 tỷ cần >11–23
phiên để thoát. Không đề xuất vị thế.

## 10. Mốc khoá trước và điều kiện đổi nhận định (cả hai chiều)
- **Tăng tâm (khoá lại, rev mới):** (i) NQ ĐHĐCĐ bất thường (20–30/12/2026) công bố tỷ lệ chia 130,7 tỷ và phần KTPL từ khoản này
  ⇒ đưa vào B₀/dòng tiền gần; (ii) quy chế trích KTPL của TKV cho thấy tỷ lệ 64% là một lần ⇒ hạ α; (iii) LNST năm 2026 kiểm toán
  > 130 tỷ.
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
| Ước LN 2025 ~51 tỷ, KH 2026 >36 tỷ | thoibaotaichinhvietnam.vn bài "Than Cao Sơn - TKV đặt mục tiêu lợi nhuận 2026 chỉ hơn 36 tỷ đồng" (báo chí, không phải NQ gốc) |

## Phụ lục B — Chưa làm / giới hạn
- NQ ĐHĐCĐ thường niên 2026 gốc và quy chế trích quỹ của TKV: không có ⇒ α = 0,64 dựa trên số thực tế 2 năm, không phải văn bản.
- Dự toán chi phí phục hồi môi trường và lịch ký quỹ còn lại (QĐ 3928/QĐ-BTNMT): không có.
- Vốn còn phải chi dự án mở rộng: chỉ ước lượng (~1.020 tỷ).
- Biểu thuế suất tài nguyên: không đọc được trong BCTC.
- Chưa tra pháp lý bên ngoài (UBCKNN/HNX/báo chí) — giữ như rev 1.
