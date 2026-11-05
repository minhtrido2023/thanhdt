# DD REDO — SAS (SASCO, UPCoM) · mùa BCTC Q3/2026 · job `Taylor_20261105_014133` · 05/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Số định giá: `calc/model.py` → `calc/model_out.txt/json`; `SUMMARY.json` sinh tự động (`_common/summary.py`).
> **Nguồn BCTC (mới tải, gốc)**: `src/Q3_2026_tonghop_kemgiaitrinh.pdf` — https://assets.sasco.com.vn/.../261021045045764-vie_bctc-q3_full_merged_sign.pdf (CBTT HNX 20/10/2026): **BCTC TỔNG HỢP giữa niên độ Q3/2026** + giải trình LNST. Scan, đọc từ ảnh `img/p04` (giải trình), `img/p07–p12` (BCTC in tr.1–6). Chưa đọc thuyết minh. H1/2026 đã kiểm toán: `src/H1_2026_kiemtoan.pdf` (chưa đọc).
> DD cũ 26/10 dùng báo chí trích BCTC; bản này **đối chiếu lại bằng file gốc** — các số báo chí chính khớp (LNST 9T 539,5; tiền + TG 945; VCSH 1.878; CFO 294,2; HTK 204,3).
> **Thiếu sector read** (dịch vụ hàng không/sân bay — chưa có trong `kb/data_registry/market-state/`).
> **Giá 34.700 đ, đóng cửa 04/11/2026** [BQ `tav2_bq.ticker`]. Đơn vị tỷ đồng.

## 0. Kết luận

| | đ/cp |
|---|---|
| Tâm TRƯỚC chiết khấu thanh khoản (kỳ vọng 30/45/25) | **31.029** |
| Chiết khấu thanh khoản (vị thế 5 tỷ) | **6,0%** |
| **Tâm SAU chiết khấu thanh khoản** | **29.164** |
| P10 / P50 / P90 SAU (lưới n=45) | **22.047 / 29.133 / 36.230** |
| P10 / P90 TRƯỚC | 23.456 / 38.546 |
| Giá 34.700 so tâm / P10 / P90 | **+19,0%** / +57,4% / −4,2% ⇒ **TRONG vùng, sát cận trên** |

Giá cao hơn giá trị kỳ vọng ~19%: thị trường định giá gần kịch bản "giữ được phần lớn LN sau Long Thành". Tâm cũ 32.600 ⇒ mới **−10,5% (>10%)**, chủ yếu do chiết khấu thanh khoản mới (−1.865 đ) + dựng lại cấu trúc từ BCTC gốc; xem Phụ lục.

## 1. Giả thuyết [DD 26/10 §1, kiểm lại bằng file gốc]
- Q3 thấp hơn Q2 do thời điểm nhận cổ tức đầu tư, lõi đi ngang: **ĐÚNG** — giải trình (img/p04): LN SXKD Q3 141,22 (+20,8%); LN tài chính 56,06 (+356,7%, "cổ tức được chia từ các khoản đầu tư góp vốn bên ngoài"); LNST 168,66 (+57,75%).
- PE 5,4x bị phóng đại bởi LN một lần (Q4/2025 khoản bù DFS) + thu nhập tài chính: **ĐÚNG** — LN vận hành 9T (loại thu nhập tài chính ròng sau thuế 150,6) = **388,8**, năm hoá **518,4**.
- Long Thành là rủi ro CẤU TRÚC lớn nhất: **ĐÚNG (định tính)**; chưa có số theo mảng để lượng hoá ⇒ biến chính của lưới.

## 2. Chất lượng lợi nhuận [KQKD in tr.5]
| | Q3/2026 | Q3/2025 | 9T/2026 | 9T/2025 |
|---|---|---|---|---|
| DT thuần | 779,6 | 804,9 | 2.333,1 | 2.339,3 |
| LN gộp | 507,1 (65,0%) | 467,5 (58,1%) | 1.556,1 (66,7%) | 1.387,6 |
| DT tài chính | 59,8 | 18,6 | 195,0 | 58,2 |
| CP bán hàng + QLDN | 365,9 | 350,5 | 1.114,2 | 1.032,4 |
| LNST | 168,7 | 106,9 | **539,5** | 328,1 |
- Doanh thu đi ngang, biên gộp tăng (tự vận hành miễn thuế sau khi đối tác DFS kết thúc 31/12/2025).
- **CFO 9T 294,2 = 0,55x LNST** [LCTT tr.6]: HTK tăng 135,4 (68,9 → 204,3, tự nhập hàng miễn thuế, chưa trích lập) + thuế TNDN nộp 124,7. Cảnh báo chất lượng LN nhẹ, không phải dấu hiệu sai lệch (phải thu giảm 153).

## 3. Bảng cân đối / net cash thật [in tr.1–4]
| Khoản | 30/09/2026 |
|---|---|
| Tiền (110) + tiền gửi đáo hạn ngắn hạn (123) | 280,7 + 664,5 = **945,2** |
| Vay | **0** |
| − Phải trả người lao động (315) / quỹ KTPL (323) / thuế phải nộp (314) | −141,2 / −99,7 / −50,2 |
| **Tiền thừa (dùng trong định giá)** | **654,1 (4.900 đ/cp)** |
| Đầu tư tài chính dài hạn (260, giá sổ: LD-LK 161,4 + khác 107,2 − dự phòng 14,8) | 253,8 (1.902 đ/cp) |
| Phải thu dài hạn khác (215) — **chưa đọc thuyết minh, không tính** | 242,0 |
- VCSH 1.878,3 (không đổi từ đầu năm — LN 2025 đã chia hết); LNST chưa phân phối 539,3 = LN 9T 2026 ⇒ nguồn cổ tức 2027.
- Vốn lưu động không kể tiền dương (phải thu 165,8 + HTK 204,3 + thuế GTGT được khấu trừ 240,6 > nợ ngắn hạn còn lại) ⇒ không cần giữ lại tiền cho vận hành.

## 4. Ghi nhận doanh thu
Bán lẻ/dịch vụ tại sân bay TSN ghi nhận khi bán; không có backlog. Thu nhập phụ thuộc hợp đồng mặt bằng với ACV (cổ đông 49,07%).

## 5. Cổ đông, room, thanh khoản [`_common/liq.py`]
- ACV 49,07%; nhóm IPP 46,50% ⇒ **free float ~4,4%** [DD 26/10, ĐHĐCĐ bất thường 08/10].
- **ADV trung vị 0,59 tỷ/phiên** (16.188 cp; 250 phiên 03/11/2025–04/11/2026, BQ), σ ngày 2,07%.
| Vị thế | CK thanh khoản Y 0,5 / 1 / 1,5 | Số phiên thoát @20–10% |
|---|---|---|
| 1 tỷ | 1,3% / 2,7% / 4,0% | 8–17 |
| **5 tỷ (tham chiếu nhãn)** | 3,0% / **6,0%** / 9,0% | **42–85** |
| 10 tỷ | 4,2% / 8,5% / 12,7% | 85–169 |
Thanh khoản là ràng buộc thực thi thật: 5 tỷ cần 2–4 tháng giao dịch để thoát.

## 6. ⚠️ WARNING pháp lý/quản trị — không loại, không trừ vào base
- Mặt bằng ACV giao trực tiếp không qua đấu thầu (TTCP 2017); lô đất chưa hoàn tất thủ tục; truy thu tiền thuê đất 2015–2024 hạch toán Q4/2025. Mặt bằng Long Thành gần như chắc phải đấu thầu.
- Bên liên quan nhóm IPP (cổ đông + đối tác); lịch sử phải thu LD Nhà Việt ~292 tỷ, trích lập ~251 tỷ.
- Kế hoạch chuyển HOSE + có thể phát hành thêm (pha loãng, đồng thời là catalyst thanh khoản).

## 7. Định giá
**r** = 13,5% + β·(lãi huy động 12T hiệu dụng − 7,40%), β=1 (giả định). Lãi huy động hiệu dụng 04/11/2026 = **7,40%** (CCTG 12M 02/11/2026; Big-4 6,8%) ⇒ **r = 13,5%** (Ke nội địa, không CRP).
Giá trị/cp = [tiền thừa 654,1 + đầu tư dài hạn giá sổ 253,8 + PV(LN vận hành × 0,883)] / 133,48 tr cp.
- 0,883 = tỷ lệ EPS/LNST 2025 (trích quỹ KTPL; EPS 4.602 vs 695,6 tỷ) [DD 26/10, ĐHĐCĐ].
- LN 2027 = N0 × (1 + Δ/2) (lộ trình chuyển chuyến bay quốc tế 28/3/2027–25/3/2028, Cục HK; ước lượng nửa tác động); từ 2028 = N0 × (1 + Δ), Gordon g = 3% (≤ GDP danh nghĩa).
- **Không có dự án đầu tư mới/cam kết vốn** trong BCTC; hồ sơ dự thầu Long Thành chưa có cam kết vốn ⇒ luật NPV=0 không áp. Khoản giảm trừ duy nhất trong base là Δ (cơ sở dữ liệu: lộ trình Cục HK chuyển ~toàn bộ chuyến quốc tế, trừ đường bay <1.000 km hãng VN; doanh thu miễn thuế + phòng chờ ~57% DT Q3 gắn khách quốc tế [DD 26/10 §2–3]).

| Kịch bản (ước lượng) | P | Δ LN từ 2028 | Trước CK TK | Sau CK TK |
|---|---|---|---|---|
| Xấu — trượt thầu chính ở Long Thành | 0,30 | −50% | 23.457 | 22.047 |
| Cơ sở — thị phần Long Thành nhỏ hơn TSN | 0,45 | −25% | 31.029 | 29.164 |
| Tốt — thắng thầu lớn | 0,25 | +5% | 40.115 | 37.705 |
| **Kỳ vọng** | | | **31.029** | **29.164** |
Trọng số giữ như DD 26/10 (chủ quan; nghiêng xấu vì đấu thầu cạnh tranh).
**Lưới P10–P90** (n=45): Δ {−55; −40; −25; −10; +5}% (0,1/0,2/0,4/0,2/0,1) × N0 {466,6; 518,4; 570,2} (1/4–1/2–1/4) × r {12,5; 13,5; 14,5}% (1/4–1/2–1/4).

## 8. Độ nhạy r theo lãi huy động (tâm trước CK)
| Δ lãi huy động | β=1,0 | β=0,5 |
|---|---|---|
| −100bp | +2.507 đ (+8,1%) | +1.191 đ (+3,8%) |
| −50bp | +1.191 đ (+3,8%) | +581 đ (+1,9%) |
| +50bp | −1.083 đ (−3,5%) | −554 đ (−1,8%) |
| +100bp | −2.072 đ (−6,7%) | −1.083 đ (−3,5%) |
(Nhạy cao vì Gordon vô hạn.)

## 9. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| Kết quả thầu mặt bằng thương mại Long Thành | khi công bố (dự kiến trước 3/2027) | trúng miễn thuế/phòng chờ với điều khoản rõ ⇒ nhánh tốt (37.700 sau CK) | trượt gói chính ⇒ nhánh xấu (22.000) |
| BCTC Q4/2026 (~20/01/2027) | 31/01/2027 | LN vận hành Q4 ≥ 140 + CFO > LNST (HTK giảm) | HTK tiếp tục phình + trích lập ⇒ hạ N0 10% (P10 nhánh) |
| Chuyển sàn HOSE / phát hành tăng free float | 2027 | ADV ≥ 3 tỷ ⇒ CK thanh khoản 5 tỷ về ~2,7% ⇒ tâm sau CK +~1.036 đ (σ·√(5/3), cùng tâm trước CK) | phát hành giá thấp ⇒ pha loãng |
| Quyết định chính thức lộ trình chuyển chuyến bay | khi có | giữ nhiều chuyến <1.000 km tại TSN | chuyển sớm hơn 2027 ⇒ 2027 chịu toàn bộ tác động |

## Phụ lục — cái gì ĐỔI so với DD 26/10 và vì sao
| Mục | DD 26/10 | Redo 05/11 | Lý do |
|---|---|---|---|
| Nguồn | báo chí trích BCTC | **BCTC tổng hợp Q3/2026 gốc** (sasco.com.vn) | skill bước 2 |
| r | 14% | **13,5%** neo lãi huy động 7,40% | luật 03/11 |
| LN nền | LN gộp 650 (gồm thu nhập TC) | **LN vận hành 518,4** (9T BCTC gốc năm hoá, loại thu nhập TC) | tách để không trộn cổ tức đầu tư không đều |
| Tiền thừa | ~3.500 đ/cp (ước lượng 50% của 945) | **4.900 đ/cp** (945,2 − phải trả NLĐ − quỹ KTPL − thuế, số gốc) | có cơ sở BCTC |
| Đầu tư dài hạn | ngầm trong LN | **giá sổ 253,8** (1.902 đ/cp) | tách tài sản |
| Chiết khấu thanh khoản | không (chỉ ghi chú) | **6,0%** (5 tỷ) | luật 03/11 |
| Vùng | 3 kịch bản 23.000/33.000/43.300 | P10–P90 lưới 22.047–36.230 | không dùng min/max |
**Cầu tâm (đo bằng model.py)**: 32.600 → +1.083 (r 14→13,5%) → −2.654 (cấu trúc mới từ BCTC gốc) = 31.029 trước CK → −1.865 (CK thanh khoản 6,0%) → **29.164** (−10,5%). Trên cùng cơ sở trước chiết khấu thanh khoản: −4,8%.

Giới hạn: Δ Long Thành và trọng số là ước lượng; chưa đọc thuyết minh (phải thu dài hạn 242, bên trả cổ tức); chưa qua fundamental-skeptic (Mike chạy).
