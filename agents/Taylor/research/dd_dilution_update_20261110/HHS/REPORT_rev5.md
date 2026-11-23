# HHS — DD rev5 (23/11/2026, job Taylor_20261123_001050)

Bản này dựng lại r4 (`../HHS_r4.md`, 10/11) theo phản biện DD_GENERAL r1 (`skeptic/r1_raw.md`, INCONCLUSIVE medium, 22/11). Định giá doanh nghiệp **không làm lại**: phân phối giá trị/cp hiện tại kế thừa nguyên r3 (`dd_redo_20261105/HHS/REPORT_r3.md`, mù giá, r = 13,5%). rev5 sửa phép biến đổi pha loãng, bổ sung hạng mục thiếu và đọc các nguồn mới (BCTC Q3/2026 thuyết minh, CBTT 20/11/2026).

- Giả định khoá: `rev5/calc/assumptions.json` (md5 ban đầu `228d217b…`; sau skeptic r2 thêm 2 khoá nguồn/độ nhạy không đổi base ⇒ md5 mới ở phụ lục `LOCK_md5.txt`; `bin/dd_assumptions_lint.py` 0 vi phạm). Calc: `rev5/calc/calc_rev5.py` (md5 `96629ed7…`), chạy 2 lần, `run1.txt` = `run2.txt` = `d3604e9b…`. Output `rev5/calc/calc_rev5_out.json`.
- LOCK: `rev5/calc/LOCK_md5.txt`, ghi 07:17:15 ICT 23/11/2026, **trước** khi đọc giá/ADV. Pha sau khoá: `rev5/calc/post_lock.py` → `post_lock_out.json`.
- Nguồn đầu vào phân phối r3: `../calc/dilution_out.json` (md5 `0450ba0aee972c6c4ec97847fe2de68c`, được calc_rev5 assert). Các file `assumptions_r3.json` / `SUMMARY.json` của r3 **đã mất khỏi đĩa** (đối chiếu `dd_redo_20261105/HHS/calc_r3/LOCK_md5.txt`); không chạy lại được lưới r3. Số tâm/P10/P50/P90 (13.969 / 12.422 / 13.917 / 15.564) có trong ba bản ghi: REPORT_r3 §0, bus finding 2026-11-08T18:11Z, `dilution_out.json` — ba bản ghi của CÙNG một lần chạy, không phải tái lập độc lập. Tâm được kế thừa, không dựng lại.

## 0. Kết luận

**Tâm sổ (CUM, cp hiện tại) giữ 13.969 (vùng 12.422–15.564), dịch 0% so với r4. Nhãn DƯỚI vùng không đổi** ở giá 9.700 (BQ 20/11/2026). Cơ sở EX (sau quyền 60% + cổ tức CP 7%, phát hành đủ, k = 1): tâm **11.615** (10.711–12.546), TERP sau cổ tức **9.171** ⇒ DƯỚI vùng.

| Cơ sở | Tâm | P10 | P50 | P90 | Giá so sánh | Nhãn | Luật 4 (giá ≤ 0,85 × tâm) |
|---|---|---|---|---|---|---|---|
| **CUM — headline (CK holding 0%, base theo V4)** | **13.969** | **12.422** | 13.917 | **15.564** | 9.700 (BQ 20/11/2026) | **DƯỚI vùng** | ĐẠT (ngưỡng 11.874) |
| CUM — song song CK holding 27% [UL, độ nhạy] | 10.761 | 8.624 | 10.559 | 13.207 | 9.700 | TRONG vùng | KHÔNG (9.147) |
| EX đủ 100%, k = 1 | 11.615 | 10.711 | 11.584 | 12.546 | TERP sau cổ tức 9.171 | DƯỚI vùng | ĐẠT (9.873); hoà vốn k = 0,761 |
| EX chỉ TCH (58,31%), k = 1, phần thiếu vay | 12.060 | 10.989 | 12.024 | 13.164 | 9.171 | DƯỚI vùng | ĐẠT |
| EX chỉ TCH, k = 0,8 (**sửa**: k áp lên đủ 2.591,9 tỷ) | 11.240 | 10.169 | 11.204 | 12.345 | 9.171 | DƯỚI vùng | ĐẠT |
| EX không phát hành quyền (chỉ cổ tức 7%) | 13.055 | 11.609 | 13.007 | 14.546 | 9.065 (= 9.700/1,07) | DƯỚI vùng | ĐẠT |
| EX song song CK holding 27%, k = 0,73 | 8.808 | 7.560 | 8.690 | 10.237 | 9.171 (+4,1% trên tâm) | TRONG vùng | KHÔNG (7.487) |

- **Nhãn DƯỚI phụ thuộc quy ước CK holding** — xem §2.1. rev5 xử lý theo luật V4 (khoản giảm trừ trong base phải có cơ sở dữ liệu độc lập; 27% không có nguồn) ⇒ base 0%, 27% là độ nhạy. Hai nhãn được ghi song song; **quyết định cuối về quy ước này vẫn là của user** (escalate trong bus finding).
- **Không đổi quyết định:** HHS nằm trong `forensic_flags` EXCLUDE ⇒ không vào candidate plan bất kể nhãn; không đủ điều kiện §2.5. Sizing V8 (2–4% NAV/mã) **không áp** khi còn EXCLUDE; nếu user gỡ EXCLUDE, đề xuất trần **2% NAV** (đầu dưới) vì nhãn phụ thuộc quy ước và thanh khoản (§5).
- ⚠ **WARNING tăng vốn** (quyền mua 60% — tăng vốn thật). ⚠ **WARNING mới:** NQ HĐQT 10/NQ-HĐQT 20/11/2026 lấy ý kiến cổ đông bằng văn bản (ĐKCC 04/12, thực hiện 14–25/12/2026), **nội dung chưa công bố** (§1). Nếu sửa phương án chào bán/mục đích tiền ⇒ làm lại bản này.

## 1. Nguồn mới đọc trong rev5

| Nguồn | Nội dung | Ảnh hưởng |
|---|---|---|
| BCTC Q3/2026 HN (`dd_HHS_20261101/src/20261029_…Hop_nhat.pdf`), **TM38** (tr.41, render `rev5/png/hn_p42.png`) | "Không có sự kiện trọng yếu nào xảy ra sau ngày kết thúc kỳ kế toán đòi hỏi phải được điều chỉnh hay công bố" | Đóng hạng mục "thuyết minh sự kiện sau kỳ chưa đọc". BCTC Q3 tự lập, không soát xét |
| Cùng file, **TM40** (tr.42–43, `hn_p43.png`, `hn_p44.png`) | Bên liên quan 9T/2026: **HHS vay TCH 39 tỷ và đã trả 39 tỷ**; CRV vay TCH 30 tỷ, đã trả 30 tỷ; chi phí lãi trả TCH 138,9 tr (HHS) / 304,1 tr (CRV). **Chuyển nhượng hợp đồng tiền gửi TCH ↔ CRV 215,5 tỷ, ↔ NĐL 636,6 tỷ** (tổng 852,0 tỷ). Kỳ trước CRV chia cổ tức cho TCH 153,7 tỷ | Sửa nhận định r4 "khoản vay TCH chưa rút tại Q3": khoản này **đã rút một phần (39 tỷ) và đã trả hết**. TM37 (tr.41): vay và nợ 30/09/2026 = 0 (01/01: 390 tỷ) |
| Cùng file, **TM1.5** (tr.12, `hn_p13.png`) | NĐL: HHS **lợi ích 51,14% / biểu quyết 58,53%** tại 30/09/2026 (CRV, Đại Thịnh Vượng 51,15% / 58,53%) | Thay 51,01% / 58,56% (TT08) trong tính k |
| Cùng file, LCTT (tr.9, `hn_p10.png`) | CFO 9T/2026 = **−2.110,2 tỷ** (HTK tăng 1.908,6 tỷ); trả gốc vay 390 tỷ; dòng 33 "tiền thu từ đi vay" = 0 | Khoản vay/trả TCH 39 tỷ ở TM40 **không thấy** trên dòng 33/34 LCTT (dòng 34 = đúng 390 tỷ ngân hàng) ⇒ lệch trình bày 69 tỷ cấp nhóm, không đối chiếu được (WARNING nhỏ). V6 dùng CFO âm |
| `rev5/src/nq_hdqt_xyk_20261120.pdf` (md5 `6688f665…`, tải từ hoanghuyhhs.vn mục Hoạt động HĐQT) | CBTT bất thường 34/HHS-CV + **NQ 10/NQ-HĐQT 20/11/2026**: lấy ý kiến cổ đông bằng văn bản, ĐKCC 04/12/2026, thời gian 14–25/12/2026, nội dung "các nội dung thuộc thẩm quyền ĐHĐCĐ" | **Không kiểm chứng được** nội dung. Trang CBTT (truy cập 23/11) không có GCN UBCKNN, ĐKCC quyền mua, hay bản cáo bạch 2026 |
| Trang CBTT HHS 23/11 (`rev5/web/cong-bo-thong-tin.html`) | Mới sau 10/11: thay đổi nhân sự thư ký HĐQT (20/11) | Không ảnh hưởng định giá |
| Quét tin (WebSearch 23/11, "Hoàng Huy HHS tháng 11 2026 chào bán…") | Chỉ ra các bài 08/2026 đã dẫn ở r4; không có tin mới về đợt chào bán hay lấy ý kiến | — |

## 2. Đính chính so với rev trước (r4) — từng hạng mục skeptic r1

| # | Hạng mục skeptic | Chiều | Xử lý rev5 | Loại | Ảnh hưởng tâm |
|---|---|---|---|---|---|
| 1 | Nhãn DƯỚI dựa trên CK holding 0% chưa được user phán xử; 27% ⇒ EX 8.808 TRONG (−24%) | quá cao? | §2.1: áp luật V4 — 27% là tham số tự đặt [UL] r2, **không có nguồn dữ liệu độc lập**; mức "giá đang ngụ ý 33,5%" bị cấm vì là suy từ giá. Base 0%, 27% giữ ở bản song song với nhãn riêng (TRONG). **Không có bằng chứng dữ liệu cho cả hai chiều:** cổ tức CRV 153,7 tỷ kỳ trước (TM40) trả cho **TCH**, không cho HHS ⇒ KHÔNG phải bằng chứng cho 0% ở cấp HHS (đính chính câu rev5 bản đầu); BCTC riêng HHS 9T/2026 doanh thu tài chính chỉ **21,6 tỷ** (`rev5/png/rg_p07.png`) ⇒ chưa thấy cổ tức CRV về HHS. Nhãn DƯỚI vì vậy là hệ quả của quy ước V4 (thiếu cơ sở cho giảm trừ), không phải của bằng chứng tiền về HHS. Quyết định quy ước: **chờ user**, nêu ở bus | (b) độ nhạy | 0 (base); bản song song −23,0% CUM |
| 2 | Kịch bản "chỉ TCH" đếm thiếu lỗ: r4 áp k lên c × tiền; thực tế HHS cam kết bơm đủ 2.591,9 tỷ và vay phần thiếu | quá cao | **Sửa công thức:** ΔVCSH = k × 2.591,9 − (1 − c) × 2.591,9 (nợ ghi theo mệnh giá, lãi thị trường = NPV0). Ở k = 0,8: tâm EX chỉ TCH 11.582 → **11.240** (−342 đ/cp cuối; đếm thiếu 216,1 tỷ, khớp skeptic ~216 tỷ). Ở k = 1 không đổi (12.060). Thêm độ nhạy chênh lãi vay − lợi suất dự án 2pp × 3 năm (ước lượng): −64,8 tỷ ≈ **−102 đ/cp** EX | (a) sửa cơ học | 0 (base k = 1); kịch bản k = 0,8 −3,0% |
| 3 | Thiếu: phần vốn I.14 còn lại (tổng 6.223,3 tỷ) — gọi vốn thêm / nợ NĐL trước 2028 | quá cao | Định lượng khoảng trống: 6.223,3 − 1.820,1 (VĐL NĐL) − 2.600 = **1.803,2 tỷ**. (i) Vay tại NĐL theo lãi thị trường = NPV0 ⇒ base không đổi. (ii) Nếu HHS gọi thêm phần mình (79,88% × 1.803,2 = 1.440,4 tỷ) bằng quyền mua @10.000: tâm EX 11.615 → **11.329 (−2,5%)**; người thực hiện quyền không mất giá trị (k = 1), người không thực hiện chịu pha loãng. Không có văn bản nào về đợt gọi vốn thứ hai ⇒ **không gán xác suất, không vào base**. Ngoài ra tiền khách hàng ứng trước khi mở bán có thể tài trợ một phần (chưa có giấy phép xây dựng ⇒ không lượng hoá) | (b) kịch bản | 0 (base); −2,5% EX nếu xảy ra |
| 4 | Thiếu: thuyết minh sự kiện sau kỳ Q3/2026; trạng thái khoản vay 100 tỷ TCH chưa tự kiểm | — | **Đã đọc** TM38 (không có sự kiện trọng yếu) và TM40 (vay TCH 39 tỷ đã trả hết; số dư vay 0 tại 30/09). Sửa câu r4 "chưa rút tại Q3" | (a) | 0 |
| 5 | Thiếu: hạn hiệu lực phương án / thời hạn phân phối | — | **Không kiểm chứng được** từ văn bản công ty: NQ ĐHĐCĐ 01/2026, NQ 07/NQ-HĐQT không ghi ngày hết hạn; GCN UBCKNN chưa cấp (CBTT 23/11). Thời hạn phân phối theo luật chỉ chạy sau khi có GCN. Ảnh hưởng: chỉ dời mốc ex, không đổi tâm CUM. Thêm: phiên lấy ý kiến 14–25/12/2026 có thể sửa phương án | (c) | 0 |
| 6 | k = 0,946 "chiều xuống có cơ sở" sai: nếu HHS kết thúc ở 75,41% thì bên khác mua ~25,9 tr cp NĐL @10.000 < BV ⇒ k ≈ 1,02 | quá thấp | **Bỏ k = 0,946.** Mô hình tường minh (NĐL 182,01 tr cp, BV 11.210, HHS lợi ích trước 51,14% theo TM1.5): đọc 75,41% ⇒ bên khác mua **26,2 tr cp**, HHS lãi **+53,5 tỷ, k = 1,0206**; đọc "NĐL chỉ phát hành cho HHS" ⇒ HHS 79,88%, **+63,3 tỷ, k = 1,0243**. Mọi cách đọc cho k ≥ 1. Base giữ k = 1 vì BV 11.210 không kiểm toán (luật 20/V4: lệch khỏi NPV0 cần cơ sở độc lập). k = 0,8 giữ làm **stress không có cơ sở** | (b) độ nhạy lên | 0 (base); +0,6% EX ở k = 1,02 |
| 7 | Nguồn: BV NĐL 11.210 từ BCTC tự lập 31/12/2025, chưa kiểm toán | — | **Không kiểm chứng được** (không có BCTC NĐL kiểm toán công khai). Chỉ ảnh hưởng phần k > 1 (độ nhạy lên), không ảnh hưởng base k = 1 | (c) | 0 |
| 8 | Nguồn: tỷ lệ TCH 38,19% trực tiếp tại NĐL "theo skeptic" | — | BCTC Q3 TM1.5 chỉ cho tỷ lệ của **nhóm HHS** tại NĐL (51,14% / 58,53%); không có số TCH trực tiếp ⇒ bỏ con số 38,19% khỏi rev5 (**không kiểm chứng được**; không dùng trong tính toán) | (c) | 0 |
| 9 | Nguồn: V_pre 13.969 kế thừa r3, không dựng lại | — | File giả định r3 đã mất; kế thừa với md5 nguồn + đối chiếu 3 nguồn (đầu file). Dựng lại lưới r3 nằm ngoài phạm vi rev pha loãng | (c) ghi rõ | 0 |
| 10 | Chưa quét tin ngoài website 01–10/11 | — | Đã quét web 23/11 + trang CBTT/HĐQT công ty (§1). Phát hiện NQ 10/NQ-HĐQT 20/11 | (a) | 0 |

| 11 | (skeptic r2) Thiếu: chi phí hoàn thiện NC-II (G10, mở từ r3) — một chiều xuống, có thể >5% | quá cao | BCTC không công bố dự toán (GAPS G10); chi phí phải trả 30/09 chỉ 28,1 tỷ (TM37) nên không có trích trước lớn. **Độ nhạy định lượng** (nếu một phần chi phí hoàn thiện, tính theo % giá gốc HTK NC-II 6.009,8 tỷ, KHÔNG sinh biên): 5% ⇒ **−351** đ/cp CUM (−2,5%); 10% ⇒ **−702** (−5,0%); 20% ⇒ **−1.403** (−10,0%); EX đủ: −205 / −410 / −820. Không vào base vì không có số (V4); errata r3: nếu biên 52% áp trên TỔNG chi phí thì chi phí hoàn thiện sinh biên và không trừ — rủi ro thật nằm ở biên cao tầng HH1–HH4 (đã ở trục ds ±15pp). Nhãn CUM vẫn DƯỚI ở 20% (P10 dịch ≈ 12.422 − 1.403 = 11.019 > 9.700) | (b) độ nhạy | 0 (base); −5,0% ở 10% |
| 12 | (skeptic r2) Số dư HTM 30/09 chưa đọc | — | **Đã đọc** CĐKT Q3 HN (`rev5/png/hn_p05.png`): tiền 181,9 tỷ + đầu tư nắm giữ đến đáo hạn ngắn hạn **848,6 tỷ** = **1.030,6 tỷ** cấp nhóm (01/01: 3.229,1). So phần thiếu 1.080,6 tỷ ở kịch bản chỉ TCH: nhóm gần tự tài trợ được (thiếu ~50 tỷ), nhưng tiền nằm rải ở công ty con 51% ⇒ độ nhạy chênh lãi −102 đ/cp có thể không xảy ra (thiên về phía tốt) | (a) | 0 |

**Kiểm control:** calc_rev5 tái lập đúng tâm r4 EX đủ k = 1 = 11.615 (assert), và mọi dòng k = 1 khớp r4 tới đồng; chỉ các dòng c < 1 với k ≠ 1 đổi (đúng hạng mục 2).

### 2.1 Quy ước CK holding — cách xử lý
- Base 0%: theo V4 ("mọi khoản giảm trừ trong base phải có dòng cơ sở dữ liệu + nguồn, không có ⇒ chuyển sang độ nhạy") và tiền lệ DRI/PVT/TCH của r3. CRV/NĐL đã được hợp nhất và phần lợi ích thiểu số (≈49%) đã trừ trong NAV theo lợi ích kinh tế, nên CK holding là giảm trừ **thêm** trên phần đã thuộc HHS.
- 27% song song: tham số tự đặt của r2 (trục 0/15/25/35/45%), không có nguồn ngoài ⇒ không vào base.
- Mốc phân xử bằng dữ kiện (không bằng giá): cổ tức tiền từ CRV về HHS (củng cố 0%); hoặc tiền thu quyền mua bị giữ ở NĐL/TCH không về cổ đông HHS (củng cố có CK).

## 3. Cơ chế (sửa)
V_final = (V_pre × 431,99 tr + (1 − CK_tk) × [k × 2.591,9 − (1 − c) × 2.591,9] tỷ) / (431,99 tr + c × 259,19 tr) / 1,07, với c > 0; c = 0 ⇒ không bơm vốn. CK_tk = 1,41% (CK thanh khoản 5 tỷ của r3). Tuyến tính tăng theo V ⇒ tâm và phân vị biến đổi chính xác.

### Bảng EX đầy đủ (headline, CK holding 0%)

| Bao phủ | k | Tâm | P10 | P50 | P90 | Ngưỡng luật 4 | CUM người thực hiện đủ |
|---|---|---|---|---|---|---|---|
| Không phát hành | — | 13.055 | 11.609 | 13.007 | 14.546 | 11.097 | 13.969 |
| Chỉ TCH 58,31% | 1,0 | 12.060 | 10.989 | 12.024 | 13.164 | 10.251 | 14.646 |
| Chỉ TCH | 0,8 | 11.240 | 10.169 | 11.204 | 12.345 | 9.554 | 13.244 |
| Chỉ TCH | 1,0206 | 12.144 | 11.073 | 12.108 | 13.248 | 10.322 | 14.790 |
| 50% | 1,0 | 12.169 | 11.057 | 12.131 | 13.315 | 10.344 | 14.833 |
| 50% | 0,8 | 11.318 | 10.206 | 11.281 | 12.465 | 9.620 | 13.377 |
| **Đủ 100%** | **1,0** | **11.615** | **10.711** | **11.584** | **12.546** | **9.873** | **13.884** |
| Đủ 100% | 0,8 | 10.924 | 10.020 | 10.893 | 11.855 | 9.285 | 12.701 |
| Đủ 100% | 1,0206 | 11.686 | 10.782 | 11.656 | 12.618 | 9.933 | 14.006 |
| Đủ 100% | 1,0243 | 11.699 | 10.795 | 11.668 | 12.630 | 9.944 | 14.028 |

Bản song song CK holding 27% (k = 0,73): không phát hành 10.057; chỉ TCH 8.733 / 7.253 / 10.426; 50% 8.714; đủ 8.808 / 7.560 / 10.237.

## 4. Luật định giá
- **V1 (r):** r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,50%** (`effective_deposit_rate()` 23/11: CCTG 12T 7,40% ngày 02/11, Big-4 6,80%, cập nhật 16/11). Dải Ke nội địa 12,3–13,4% báo kèm. Độ nhạy: mô hình là NAV quỹ đất, r chỉ vào chiết khấu thời gian thực hiện; r3 đo trục r ±1pp cho tâm 13.972 (+3 đ/cp, REPORT_r3 §4) ⇒ ±50/±100bp ≈ 0 đ/cp (< 0,1%). Độ nhạy β 0,5/1,0: Δ lãi = 0 ⇒ không đổi.
- **V3 (thanh khoản, sau khoá):** giá trị TRƯỚC CK: tâm 14.169 (r3); SAU CK 5 tỷ (1,41%): 13.969 — nhãn theo giá trị sau CK. ADV 20/11/2026 (BQ `tav2_bq.ticker` Price × Volume): trung vị 60 phiên **10,35 tỷ**, TB 250 phiên **21,34 tỷ** ⇒ 5 tỷ = 48% ADV60 / 23% ADV250, **trên** vùng hiệu chỉnh căn bậc hai ⇒ CK 1,41% có thể thấp. Cỡ sleeve 40 tr: CK 0,126% (r3). Vị thế 5 tỷ (nếu có) phải chia tranche ≤ 2,1 tỷ/đợt (20% ADV60).
- **V4:** I.14 = dự án tăng trưởng, base NPV0 (k = 1); không có capex tuân thủ mới. Khoảng trống vốn 1.803,2 tỷ: SCENARIO_ONLY (§2 #3).
- **V5 (5F):** đầy đủ ngày 07–09/11/2026 (`dd_redo_20261105/HHS/ADDENDUM_5F.md`) < 12 tháng ⇒ tái dùng: **moat NONE / LOCATION (asset-play quỹ đất CRV Hải Phòng), không bền; rủi ro số 1 = thực hiện thặng dư quỹ đất + dòng tiền lên HHS qua 2 tầng holding.** Kiểm nhanh 23/11: không có dữ kiện mới về quỹ đất; đợt tăng vốn làm I.14 thành phần lớn hơn trong NAV (NPV0) ⇒ không đổi moat.
- **V6 (hai nền, chỉ hiển thị):** FCFE ≤ 0 (CFO 9T/2026 −2.110,2 tỷ LCTT HN; BQ CF_OA 2026Q1–Q3 −679,5 / −1.170,6 / −72,2 tỷ) ⇒ chỉ V_ngắn. V_ngắn = LNST TTM trung vị 3 năm **260,5 tỷ** (loại 2025Q2 3.507 tỷ lãi hợp nhất CRV một lần) / r 13,5%, g = 0 ⇒ **4.466 đ/cp** cum (2.609 đ/cp EX đủ). Giải thích chênh với tâm NAV 13.969: HHS là asset-play — giá trị nằm ở thặng dư HTK NC-II (giá gốc ~6.009,8 tỷ) và quỹ đất chưa bàn giao, chưa đi qua lợi nhuận; dòng tiền âm do đầu tư HTK (HTK +1.908,6 tỷ trong 9T). V_ngắn không phải dự báo giá, không vào tâm/vùng.
- **V7:** không dùng snapshot vĩ mô (rev pha loãng).
- **V8:** chuẩn 2–4% NAV/mã; **không áp** do EXCLUDE (§0).

## 5. Thị trường (sau khoá, 07:17 ICT 23/11)
- Giá 9.700 (BQ 20/11/2026; phiên 23/11 chưa mở, chưa poll DNSE). Giá quyền ngầm định = 9.700 − 10.000 = **−300 đ/cp mới** ⇒ cổ đông nhỏ lẻ không có động cơ thực hiện; **kịch bản "chỉ TCH" là thực tế**, không phải đuôi. TERP quyền 9.812, sau cổ tức 9.171.
- CUM headline: giá −30,6% so tâm, < P10 12.422. Bản CK holding: −9,9% so tâm 10.761, trong vùng.

## 6. WARNING (pháp lý / quản trị — chỉ WARNING, không vào base)
- **Tăng vốn 60%** (quyền 5:3 @10.000, không có tỷ lệ thành công tối thiểu; HĐQT tự phân bổ cp dư, khoá 1 năm). Kịch bản chỉ TCH: HHS cần tự lo **1.080,6 tỷ** (41,69% × 2.591,9) so với tiền 181,9 tỷ + HTM ngắn hạn 848,6 tỷ = **1.030,6 tỷ cấp nhóm** tại 30/09 (CĐKT HN; BQ `Cash_P0` 181,9 tỷ thiếu HTM) ⇒ nhóm gần tự tài trợ được, phần còn lại vay. BQ `StDebt_P0` 2026Q2 = 30 tỷ, 2026Q3 = 0 — nhất quán với vay/trả TCH ở TM40.
- **Bên liên quan:** chuyển nhượng HĐ tiền gửi 852,0 tỷ TCH ↔ CRV/NĐL trong 9T/2026; vay/trả TCH 69 tỷ cấp nhóm không thấy trên LCTT; tiền quyền mua chảy vào NĐL qua chuỗi TCH/CRV.
- **Lấy ý kiến cổ đông 14–25/12/2026** chưa rõ nội dung.
- Forensic EXCLUDE; LN Q3 chưa soát xét; **chi phí hoàn thiện NC-II chưa có dự toán (G10)** — độ nhạy §2 #11: −351 / −702 / −1.403 đ/cp ở 5/10/20%.

## 7. Mốc hai chiều + HARD ABANDON
- **Xuống:** công bố dự toán hoàn thiện NC-II/HH1–HH4 cho chi phí không sinh biên ≥10% giá gốc HTK (−702 đ/cp); phiếu lấy ý kiến 12/2026 hạ giá chào bán / đổi mục đích tiền / tăng quy mô; GCN UBCKNN + ĐKCC khi giá < 10.000 (bao phủ thấp, HHS vay); NĐL công bố gọi vốn thêm cho I.14; BCTC kiểm toán NĐL cho BV < 10.000 (k < 1 có cơ sở).
- **Lên:** cổ tức tiền CRV → HHS (bằng chứng chống CK holding); TCH cam kết mua hết hoặc bảo lãnh phần dư; giấy phép xây dựng / mở bán I.14.
- **HARD ABANDON:** NĐL phát hành cho bên khác giá thấp hơn mà HHS không tham gia; tiền thu không vào NĐL; kiểm toán ngoại trừ PPA/HTK; khởi tố pháp nhân trong nhóm (giữ từ r3/r4).

## 8. Còn mở (không kiểm chứng được tại 23/11/2026)
1. Quy ước CK holding 0% vs 27% — **chờ user** (quyết định nhãn CUM DƯỚI vs TRONG).
2. Nội dung phiên lấy ý kiến cổ đông 14–25/12/2026.
3. Hạn phân phối (GCN chưa cấp).
4. BV NĐL 11.210 chưa kiểm toán; tỷ lệ TCH trực tiếp tại NĐL.
5. Lưới r3 không chạy lại được (file giả định r3 mất); tâm kế thừa. "Ba nguồn" ở đầu file là ba bản ghi cùng một con số, không phải tái lập độc lập (đính chính theo skeptic r2). Dựng lại lưới r3 từ BCTC gốc = việc riêng, đề xuất làm khi có BCTC năm 2026 kiểm toán.
6. **Chi phí hoàn thiện NC-II (G10)** — chỉ có độ nhạy (§2 #11), không có dự toán công bố.
7. Quỹ khen thưởng phúc lợi: kế thừa r3, không tìm lại trong rev5 (ảnh hưởng nhỏ qua NAV, chưa đo).
