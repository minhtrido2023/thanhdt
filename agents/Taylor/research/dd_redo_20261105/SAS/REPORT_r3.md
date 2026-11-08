# DD REDO VÒNG 3 — SAS (SASCO, UPCoM) · job `Taylor_20261108_153740` · 08/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị, không đặt lệnh. Áp `../TOP5B_CORRECTIONS_20261108.md` §SAS (user duyệt) sau khi **kiểm từng điểm bằng calc + ảnh BCTC gốc**; chuẩn `../STANDARD_r2.md`.
> Số: `calc_r3/model_sas_r3.py` → `calc_r3/model_sas_r3_out.txt/json`; `calc_r3/make_summary_r3.py` → `SUMMARY.json` (r2 backup `SUMMARY_r2.json`). Giả định khoá `calc_r3/assumptions_r3.json`; `calc_r3/LOCK_r3_md5.txt` (17 file upstream, gồm file giả định) chốt **trước** khi chạy so giá — script assert md5 trước khi tính. Chạy 2 lần trùng byte (txt `b321b12a…`, json `1c245cc4…`).
> Giá tham chiếu **34.200 đ** = đóng cửa 06/11/2026, BQ `tav2_bq.ticker` (`calc_r3/px_sas_r3.sql`). r = 13,5% + 1,0×(7,40% − 7,40%) = **13,5%** (lãi huy động 12T hiệu dụng 06/11 = CCTG 12M 7,40%, 02/11). Đơn vị tỷ đồng.

## 0. Kết luận — headline ở cỡ CK tham chiếu 5 tỷ (mức KẾT CỤC)

| | đ/cp |
|---|---|
| **Tâm** = kỳ vọng lưới (trước / sau CK 5,93%) | 33.652 / **31.658** |
| **P50** kết cục (sau CK) | 31.402 |
| Giá trị tại tham số trung tâm (Δ −25%, N0 479,7, r 13,5%, g 3%; sau CK) | 31.477 |
| **P10 / P90** kết cục (sau CK) | **25.083 / 38.043** |
| n kết cục · % trọng số dưới giá · thấp nhất | 135 · **73,0%** · 20.656 |
| Giá 34.200 so tâm | **+8,0% ⇒ TRONG vùng (nửa trên)** — nhãn không đổi so r2 |

**Dòng riêng — cỡ sleeve thật 40 triệu** (CK 0,53%, 6,6% ADV250, trong vùng hiệu chỉnh): tâm 33.474, P10/P90 26.521/40.225, giá/tâm +2,2%, 58,1% trọng số dưới giá ⇒ TRONG vùng.

Tâm r2 31.066 → r3 **31.658 (+1,9%)**; so vùng cũ 26/10 (32.600): −2,9%. Ba con số: tâm 31.658 > tham số trung tâm 31.477 > P50 31.402 (cả ba trong khoảng 256 đ) — lệch phải nhẹ do Gordon lồi theo g/r; không nhánh trọng số nhỏ nào quyết định P10/P90.
Kết luận skeptic "tâm bị kéo thấp bởi giả định một chiều" **đúng một phần**: đính chính 1 (thuế cổ tức) lại kéo tâm XUỐNG −1.716; đính chính 2–3 kéo lên +2.394; hai điểm tôi thêm khi kiểm (trích KTPL 9T −445, LN Q4/26 bị bỏ trống +332) gần bù nhau. Ròng +592 đ/cp.

## 1. Kiểm từng đính chính (không chép mù)

| # | Đính chính skeptic | Kiểm (nguồn) | Kết luận | Δ tâm (đ/cp, sau CK 5 tỷ) |
|---|---|---|---|---|
| 1 | Cổ tức miễn thuế, r2 đánh thuế 20% lên cả 195 thu nhập TC | KQKD tr.5 (`img/p11`): LNTT 638,03; thuế hiện hành 98,13 ⇒ phần không chịu thuế = 638,03 − 98,13/20% = **147,4** (cổ tức báo chí 135,8). N0 = (LNTT − TC ròng 188,28) × 0,8 × 4/3 = **479,7** (biến thể qua cổ tức 135,8: 482,2) | **ĐÚNG — áp** | −1.716 |
| 2 | Vốn lưu động một chiều | CĐKT tr.1/tr.3 (`img/p07`, `p09`): phải thu NH 165,8 (mã 130), HTK 204,3 (140), TSNH khác 256,0 (160, gồm thuế GTGT được khấu trừ 240,6 mã 162) vs nợ NH 495,8 (310) ⇒ VLĐ ngoài tiền **+130,3**. r2 trừ phải trả NLĐ + thuế (là VLĐ vận hành) mà bỏ tài sản VLĐ | **ĐÚNG — áp bản "chỉ trừ quỹ KTPL"** (+ cổ tức phải trả 2,06, mã 313, MỚI). VLĐ vận hành đã nằm trong N0 ⇒ bản "gộp đủ VLĐ ròng" chỉ là độ nhạy chiều lên | +1.335 |
| 3 | XDCB 118,0 + BĐS ĐT 32,2 đang = 0 | CĐKT tr.2 (`img/p08`): mã 252 = 118,04; mã 240 = 32,24, hao mòn luỹ kế 5,009 **không đổi** trong 9T ⇒ BĐS nắm giữ chờ tăng giá, không cho thuê ⇒ không nằm trong N0, không đếm hai lần. Mã số skeptic đúng | **ĐÚNG — áp (luật 20)** | +1.059 |
| 4 | Trục chiều lên: vốn hoá cổ tức đầu tư | Đầu tư DH 253,8 = LDLK 161,4 + góp vốn khác 107,2 − dự phòng 14,8 (`img/p08`). Bên trả cổ tức + mức đều đặn **CHƯA KIỂM** (thuyết minh V.2c/V.27 không có trong ảnh trích) | **ĐÚNG hướng — chỉ độ nhạy**, không vào base | — (xem §3) |
| 5 | Giá 34.200 (06/11) | BQ 06/11 đóng cửa 34.200 ✓. r2 ở giá mới: tâm 31.094, giá/tâm +10,0%, 73,3% dưới giá (skeptic +10,1% / 73,3%) | **ĐÚNG** | +27 |
| 6 | WARNING thiếu (20 lô đất, IPP 194, bên trả cổ tức, KTPL 9T) | VCSH 1.878 không đổi đầu năm→30/09; LNST chưa phân phối 539,3 = LN 9T ⇒ chưa trích quỹ 2026 | **ĐÚNG** — 3 cờ ghi §6; **KTPL 9T đưa vào BASE** (−63,1 tỷ = (1−0,883)×539,5; cùng cơ sở hệ số 0,883 đã áp cho LN tương lai — nhất quán, có dữ liệu) | −445 |
| 7 | Δ Long Thành, 57% DT quốc tế là [UL]; Gordon không trừ tái đầu tư giữ quy ước 08/11 | — | **GHI NHẬN**; bản chặt-3c 22.002 (ADDENDUM_5F) tính trên mô hình r2, chỉ là độ nhạy rủi ro, không tính lại | — |
| + | **MỚI khi kiểm**: r2 lấy CĐKT 30/09 nhưng chiết khấu dòng tiền từ gốc 31/12/2026 ⇒ **bỏ trống LN vận hành Q4/2026** (giả định một chiều cùng loại skeptic nêu) | + N0/4 × 0,883 = 105,9 tỷ; mọi dòng tiền tương lai chiết khấu thêm 55 ngày (31/12 → 06/11) | áp | +332 |

Điểm skeptic 31.731 tái lập: bản A1 (đính chính 1–3, không S5/S6) = **31.771** (lệch +40 do giá/ADV 06/11 và trừ cổ tức phải trả). Thanh khoản skeptic (ADV250 0,59; 847% ADV) là số 04/11; ở 06/11: ADV250 0,61 tỷ, 5 tỷ = 823% ADV, CK 5,93%.

## 2. Lưới (giữ r2) + bridge r2 → r3
4 trục, 135 ô, mỗi ô 1 kết cục tất định, phân vị `_shared/wpct.py`: Δ Long Thành từ 2028 {−55;−40;−25;−10;+5}% (0,1/0,2/0,4/0,2/0,1) [UL], 2027 nửa tác động · N0 ±10% quanh **479,7** · r {12,5;13,5;14,5}% · g {2;3;4}% (trục phụ 1/4–1/2–1/4).
Tài sản cố định trong base (theo sổ): tiền+tiền gửi 945,2 − quỹ KTPL 99,7 − cổ tức phải trả 2,1 + đầu tư DH 253,8 + phải thu DH 242,0 + XDCB 118,0 + BĐS ĐT 32,2 − trích KTPL 9T 63,1; + LN vận hành Q4/26 105,9. LN × 0,883.

| Bước (mỗi bước đổi MỘT thứ) | Tâm sau CK 5 tỷ | Δ | P10 / P50 / P90 | % dưới giá |
|---|---|---|---|---|
| S0 tái lập r2 (giá 04/11) | 31.066 | — | 23.751 / 30.806 / 38.022 | 73,6% |
| S1 giá + ADV 06/11 | 31.094 | +27 | 23.772 / 30.833 / 38.055 | 73,3% |
| S2 N0 cổ tức miễn thuế (đc 1) | 29.377 | −1.716 | 22.602 / 29.136 / 35.819 | 83,8% |
| S3 VLĐ nhất quán (đc 2) | 30.712 | +1.335 | 23.937 / 30.471 / 37.153 | 74,2% |
| S4 XDCB + BĐS ĐT theo sổ (đc 3) | 31.771 | +1.059 | 24.996 / 31.530 / 38.213 | 72,7% |
| S5 trích KTPL LN 9T (đc 6) | 31.326 | −445 | 24.551 / 31.085 / 37.768 | 73,3% |
| **S6 khớp ngày định giá (mới) = HEADLINE** | **31.658** | +332 | **25.083 / 31.402 / 38.043** | **73,0%** |

(Δ cột làm tròn từng bước; tổng Δ S0→S6 = +592.)

## 3. Headline vs biến thể song song (CK 5 tỷ, cùng lưới)

| Biến thể | Tâm | P10 / P90 | % dưới giá | Giá/tâm |
|---|---|---|---|---|
| **Headline (S6)** | **31.658** | 25.083 / 38.043 | 73,0% | +8,0% |
| A1 điểm skeptic (đc 1–3, không S5/S6) | 31.771 | 24.996 / 38.213 | 72,7% | +7,6% |
| A2 gộp đủ VLĐ ròng +130,3 (chiều lên) | 33.293 | 26.718 / 39.678 | 58,3% | +2,7% |
| A3 không trích KTPL 9T | 32.103 | 25.527 / 38.488 | 71,7% | +6,5% |
| A4 không khớp ngày (bỏ Q4/26) | 31.326 | 24.551 / 37.768 | 73,3% | +9,2% |
| A5 N0 qua cổ tức báo chí 135,8 (N0 482,2) | 31.770 | 25.161 / 38.188 | 73,0% | +7,6% |
| A6 bỏ phải thu DH 242 (chiều xuống) | 29.952 | 23.377 / 36.337 | 81,1% | +14,2% |
| A7 bỏ trục g (g 3%) | 31.571 | 25.083 / 37.943 | 74,4% | +8,3% |
| A8 vốn hoá cổ tức đầu tư 71 / 100 / 140 tỷ/năm (×0,883 / r, g 0, thay sổ 253,8) | 33.151 / 34.491 / 36.340 | 26.573–29.801 / 39.789–43.153 | 58,6% / 48,1% / 36,2% | +3,2% / −0,8% / −5,9% |

Mọi biến thể đều TRONG vùng. A8: skeptic 140 tỷ ⇒ 37.253 vì không nhân 0,883 (phần trích quỹ) và trên nền r2; ở đây 36.340. **Chưa kiểm** bên trả cổ tức/mức đều đặn ⇒ A8 không vào base.

**Giá ngụ ý** (đổi riêng một biến để tâm sau CK 5 tỷ = 34.200): tâm Δ Long Thành **−15,3%** (base −25%), hoặc r **12,38%**, hoặc cổ tức đầu tư vốn hoá **94 tỷ/năm** (thay sổ 253,8), hoặc N0 **536 tỷ** (+12%). Skeptic: −16% / 12,4% / ~71 tỷ (nền khác, không nhân 0,883).

## 4. Cross-check Gordon (Δ −25% vĩnh viễn, g 3%, trước CK)
A — vốn hoá cả thu nhập TC sau thuế 240,1/năm (lãi tiền gửi + cổ tức, cổ tức miễn thuế), không cộng tiền/đầu tư: **39.501** (không dùng: vốn hoá lãi tiền gửi vĩnh viễn với g 3%). B — không thu nhập TC, cộng tiền + tài sản theo sổ (= cách base): **33.355**.

## 5. Thanh khoản (điều 6)
| Cỡ | ADV250 0,61 tỷ (σ 2,07%) | ADV60 0,78 tỷ (σ 1,82%) |
|---|---|---|
| 10 / 20 / 40 tr (sleeve) | 0,27% / 0,37% / **0,53%** (40 tr = 6,6% ADV, trong vùng) | 0,21% / 0,29% / 0,41% |
| **5 tỷ (headline)** | **5,93%** — Q/ADV 823%, **NGOÀI xa vùng hiệu chỉnh**, 41–82 phiên @20–10% | 4,59% (637%, ngoài) |
Tâm theo cỡ (ADV250): 10 tr 33.563 · 40 tr 33.474 · 1 tỷ 32.760 · 5 tỷ 31.658 · 10 tỷ 30.832 — nhãn TRONG ở mọi cỡ. Free float ~4,4% ⇒ cỡ 5 tỷ phi thực tế với mã này; CK ở cỡ đó chỉ là quy ước.

Độ nhạy lãi huy động (tâm sau CK 5 tỷ, dịch cả trục r): β=1: −100bp 33.897 (+7,1%) · −50bp 32.720 (+3,4%) · +50bp 30.695 (−3,0%) · +100bp 29.818 (−5,8%); β=0,5: +3,4% / +1,6% / −1,6% / −3,0%.

## 6. ⚠️ WARNING pháp lý/quản trị (không trừ base)
1. Mặt bằng ACV giao trực tiếp không đấu thầu (KL TTCP 2017); lô đất chưa hoàn tất thủ tục; truy thu tiền thuê đất 2015–2024 "hàng chục tỷ" hạch toán Q4/2025 [vietstock] — rủi ro truy thu thêm. **20 lô đất >7,2 triệu m² (Bộ Tài chính 2019)** theo skeptic — **chưa kiểm bản gốc**. Mặt bằng Long Thành gần như chắc phải đấu thầu.
2. Bên liên quan nhóm IPP (IPPG 24,98% / ACFC 14,89% / DAFC 4,92% / DAT 1,71% = 46,5%) vừa cổ đông vừa đối tác; phải thu IPP Group Pte 194 tỷ (đã thu, DD 26/10); lịch sử phải thu LD Nhà Việt ~292 tỷ, trích lập ~251 tỷ.
3. **Bên trả cổ tức đầu tư (135,8–147 tỷ/9T) chưa xác định** — đầu tư DH gồm LDLK 161,4 + góp vốn khác 107,2; nếu bên trả là bên liên quan IPP thì là kênh chuyển giá trị cần xem.
4. Free float ~4,4%; Chủ tịch nói tự vận hành miễn thuế "không thể kéo dài", đối tác mới chưa công bố điều khoản. Kế hoạch chuyển HOSE + có thể phát hành thêm (chưa lịch).
5. Nhân sự: TGĐ Dư Kim Thăng bổ nhiệm 03/08/2026, TGĐ cũ về ACV [cafef 04/08/2026].
6. "Không thấy vụ việc hình sự/khởi tố liên quan SASCO": nguồn = DD 26/10/2026 + web search 05/11/2026 (cafef, dnse, baophapluat); **không tra lại 08/11** (vòng này chỉ kiểm calc).
7. Kỳ giữa niên độ không trích quỹ KTPL trên LN 9T — r3 đã trừ 63,1 tỷ trong base (S5).

## 7. Giả định tự đặt [UL] (đầy đủ trong `SUMMARY.json.assumptions`)
5 mức Δ Long Thành + trọng số; nửa tác động 2027; N0 ±10%; trọng số trục r/g; β=1; thuế 20% trên toàn bộ LN vận hành; LN Q4/26 = N0/4 (không mùa vụ); hệ số 0,883 cho cả LN 9T đã có và LN tương lai.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| Kết quả thầu mặt bằng Long Thành | trước 3/2027 | trúng miễn thuế/phòng chờ ⇒ Δ về +5…−10% | trượt gói chính ⇒ Δ −40…−55% |
| Thuyết minh V.2c/V.27 (bên trả cổ tức) | BCTC năm 2026 | cổ tức đều từ bên độc lập ⇒ xét A8 vào base | từ bên liên quan/không đều ⇒ giữ sổ |
| BCTC Q4/2026 | 31/01/2027 | LN vận hành Q4 ≥ 120 (= N0/4), CFO > LNST | HTK phình + trích lập ⇒ N0 −10% |
| Thuyết minh phải thu DH 242 | BCTC năm 2026 | ký quỹ thu hồi được ⇒ giữ | không thu hồi ⇒ bản A6 (29.952) |
| Chuyển HOSE / phát hành | 2027 | ADV ≥3 tỷ ⇒ CK 5 tỷ thấp hẳn | phát hành giá thấp ⇒ pha loãng |
**HARD ABANDON**: (a) ACV chấm dứt/thu hồi mặt bằng TSN trước 2027; (b) khởi tố/kết luận thanh tra chạm pháp nhân SASCO hoặc hợp đồng mặt bằng; (c) chuyển tiền/cho vay bên liên quan IPP không bảo đảm. Sleeve 10–40 tr ⇒ không cần tranche (40 tr ≈ 6,6% ADV250 ⇒ 0,3–0,7 phiên @20–10% ADV).
**Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không khủng hoảng, giá trên tâm.

## 9. Mở / chưa kiểm
Thuyết minh V.2c/V.27 (bên trả + mức cổ tức đầu tư — quyết định A8) · V.5b phải thu DH 242 · 20 lô đất 7,2 triệu m² · khoản bù DFS Q4/2025 · thầu Long Thành · HTK 204,3 chưa trích lập · thiếu sector read · BQ `EPS`=0 mọi quý SAS. · **thuế GTGT được khấu trừ 240,6 (mã 162, thuyết minh V.27) — đang coi là VLĐ khoá vĩnh viễn, chưa kiểm** · **lãi Q4 trên 945 tỷ tiền gửi chưa cộng ở S6 (~−40…−70 đ/cp, skeptic)** · `img/p10` không nằm trong LOCK (chưa khoá) — xem §10. Chờ Mike phản biện cuối + ghi `dd_price_zones`.

## 10. Ghi chú bổ sung sau skeptic vòng 3 (08/11) — chỉ văn bản, KHÔNG đổi mô hình/headline/calc
1. **Lãi Q4 trên tiền gửi chưa cộng (S6)**: S6 cộng LN vận hành Q4/26 (N0/4 × 0,883 = 105,9) nhưng **không cộng lãi Q4 trên 945,2 tỷ tiền + tiền gửi** (base cộng tiền theo sổ 30/09, lãi 01/10→31/12 bỏ trống). Skeptic ước lệch **khoảng −40…−70 đ/cp** (tâm hiện hành có thể THẤP hơn thực khoảng đó; số của skeptic, chưa tính lại ở đây). Mới ghi vào độ nhạy chiều lên, không vào base; thêm vào danh sách §9.
2. **Thuế GTGT được khấu trừ 240,6 (mã 162) bị coi là VLĐ khoá vĩnh viễn — KHÔNG có cơ sở đã kiểm**: dòng đính chính 2 (§1) giữ nguyên TSNH khác 256,0 (mã 160, trong đó 240,6 là mã 162) nằm trong VLĐ vận hành đã chìm vào N0, tức mặc định số này không bao giờ thu hồi/hoàn. Đây là giả định chưa kiểm; biến thể A2 (gộp đủ VLĐ ròng +130,3 ⇒ 33.293) là cận trên nếu khoản này hoàn được. **Chưa kiểm**: thuyết minh V.27 và mã 162 (khấu trừ vs hoàn thuế, tuổi khoản).
3. **Nguồn `img/p10` không nằm trong LOCK (chưa khoá)**: `calc_r3/assumptions_r3.json` (khoá) dẫn `img/p09-p10` làm nguồn cho trích KTPL 9T (`ktpl_accrual_9m`), nhưng `LOCK_r3_md5.txt` chỉ có `img/p07, p08, p09, p11`. Số trích KTPL 63,1 tỷ tính từ LNST 9T (p11) × (1−0,883), VCSH 1.878 không đổi (p09) — không cần p10 để tái lập; p10 chưa được chốt md5. Không sửa LOCK/assumptions.
