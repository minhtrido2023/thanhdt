# HHS — cập nhật pha loãng r4 (10/11/2026, job Taylor_20261110_034232)

Vòng 2 (10/11): áp required_change của fundamental-skeptic (CONFIRMED medium) — không làm lại mô hình.
Nền: `dd_redo_20261105/HHS/REPORT_r3.md` + `ERRATA_final_skeptic_20261109.md`. Định giá doanh nghiệp **không làm lại**: dùng nguyên phân phối r3 (mù giá). Bản này chỉ biến đổi theo số cổ phiếu và tiền thu từ đợt phát hành.
Calc: `calc/dilution_calc.py` (md5 `bbf89372…`), chạy 2 lần, output trùng byte (`run1.txt` = `run2.txt` = `25525b71…`). Kết quả nằm ở `calc/dilution_out.json`.

## 0. Kết luận

**Nhãn DƯỚI không đổi. Đợt phát hành chưa thực hiện. Giá trị/cp giảm −16,9% (13.969 → 11.615), TERP chỉ giảm −6,5% (10.000 → 9.346): tâm/giá nới từ 1,397 lên 1,243 so với TERP — tức khoảng cách tới vùng RỘNG hơn nếu so cum, HẸP lại khi so ex (1,397 → 1,243).**

⚠ Nhãn DƯỚI phụ thuộc 2 điều kiện: (a) quy ước **CK holding 0%** (errata r3, chờ user phán xử — bản CK holding 27% cho TRONG); (b) pha loãng 60% @thị giá là điều kiện trượt §2.5 (luật 4 chỉ đạt có điều kiện, xem §2 điểm hoà vốn). Mọi nhãn DƯỚI ở file này đọc kèm hai điều kiện đó.

| Cơ sở | Tâm | P10 | P50 | P90 | Giá so sánh | Nhãn | Luật 4 (≤ 0,85 × tâm) |
|---|---|---|---|---|---|---|---|
| **CUM (hiện tại, chưa có ngày GDKHQ)**: giá trị / 1 cp hiện tại, cổ đông thực hiện đủ quyền, k = 1, **CK áp lên cả phần tiền** (quy ước nhất quán các dòng EX) | **13.884** | 12.337 | 13.832 | 15.479 | 9.990 (BQ 09/11) | **DƯỚI vùng** | ĐẠT (11.801) |
| CUM, **không** áp CK lên phần tiền (= phân phối r3 nguyên bản, dùng cho ledger) | 13.969 | 12.422 | 13.917 | 15.564 | 9.990 (BQ 09/11); DNSE 10/11 10:46 khớp 10.000 — theo skeptic là lệnh đơn 50 cp, tôi CHƯA lưu bản ghi nên ledger dùng 9.990 | **DƯỚI vùng** | ĐẠT (11.874) |
| **EX cả hai đợt**, phát hành đủ, k = 1, 739,56 tr cp | **11.615** | 10.711 | 11.584 | 12.546 | TERP 9.346 (từ 10.000) | **DƯỚI vùng** | ĐẠT (9.873) — **chỉ khi k ≥ 0,8207** |
| EX đủ, **k = 0,946** (HHS giữ 75,41% NĐL như công ty nêu; −141 tỷ) | 11.428 | 10.525 | 11.398 | 12.360 | TERP 9.346 | DƯỚI | ĐẠT (9.714) |
| EX, bao phủ một phần (chỉ TCH 58,31%) | 12.060 | 10.989 | 12.024 | 13.164 | — | DƯỚI | — |
| EX, không phát hành quyền (chỉ cổ tức 7%) | 13.055 | 11.609 | 13.007 | 14.546 | 9.336 (9.990 / 1,07) | DƯỚI | — |
| Song song CK holding 27% [UL], EX đủ, k = 0,73 | 8.808 | 7.560 | 8.690 | 10.237 | TERP 9.346 | TRONG | KHÔNG (7.487) |

- **Bản song song CK holding: giá đã VƯỢT tâm.** r3 (cum): giá 9.990 so tâm 10.761 = **−7,2%** (dưới tâm, TRONG). r4 (ex): TERP 9.346 so tâm 8.808 = **+6,1%** (trên tâm, vẫn TRONG vì ≤ P90 10.237). Pha loãng làm bản này chuyển từ "dưới tâm" sang "trên tâm". (Số −7,7% trong nhận xét skeptic không tái hiện được: đo −7,2% trên SUMMARY r3.)

- Theo luật 20, phần tiền bơm vào NĐL được tính NPV 0 (k = 1). Với k = 1, giá trị CUM của cổ đông thực hiện đủ quyền **giữ nguyên 13.969**. Tâm trên mỗi cổ phiếu cuối giảm 13.969 → 11.615 (−16,9%). Giá thị trường tính theo TERP cũng giảm theo cùng cơ chế: 10.000 → 9.346 (−6,5%).
- Nhãn DƯỚI bền với k: ở **k = 0,8** (vốn bơm vào dự án mất 20%), tâm EX đủ 10.924, P10 10.020 > TERP 9.346, vẫn DƯỚI. **Luật 4 (giá ≤ 0,85 × tâm) trên cơ sở EX: điểm hoà vốn k = 0,8207** — ĐẠT ở k = 0,946/1,0/1,024, **TRƯỢT ở k = 0,8** (ngưỡng 9.285 < TERP 9.346). Vì vậy "Luật sổ ĐẠT" chỉ có điều kiện k ≥ 0,82.
- Ở bản song song có CK holding, nhãn TRONG vẫn giữ (r3 cũng TRONG).
- **Không đổi quyết định:** HHS vẫn nằm trong `forensic_flags` EXCLUDE, nên bị loại khỏi candidate plan bất kể nhãn. Mã cũng không đủ điều kiện §2.5.
- ⚠ **WARNING tăng vốn (luật 29/10):** đợt quyền mua 60% là tăng vốn thật trong chu kỳ, phải WARNING user. Cổ tức cổ phiếu 7% chỉ là INFO.

## 1. Nguồn gốc (đã đọc văn bản gốc, PDF scan, đọc bằng ảnh)

| Đợt | Văn bản | Nội dung chính |
|---|---|---|
| Quyền mua 60% | **NQ ĐHĐCĐ 01/NQ-ĐHĐCĐ ngày 24/04/2026**, Điều 11, theo **Tờ trình 08/TT-HĐQT**. File `src_hhs/nq_dhdcd_2026.pdf` (tải từ hoanghuyhhs.vn, 247 tr). Phần TT08 nằm ở tr.108–118 | 259.191.580 cp, tỷ lệ 5:3, **giá 10.000 đ**, tổng 2.591.915.800.000 đ. Không có tỷ lệ chào bán thành công tối thiểu. Cổ phiếu không bán hết được chào cho nhà đầu tư khác @10.000, những cổ phiếu này bị hạn chế chuyển nhượng 1 năm. Thiếu vốn thì bù bằng vay ngân hàng hoặc trái phiếu. Quyền được chuyển nhượng 1 lần. |
| | **NQ HĐQT 07/NQ-HĐQT ngày 26/08/2026** (`src_hhs/hhsnqhdqttrienkhaichaobancophieu26082026.pdf`), kèm NQ HĐQT thông qua hồ sơ đăng ký chào bán cùng ngày | Triển khai giữ nguyên các điều khoản trên. **Thời gian dự kiến Quý IV/2026 – Quý I/2027, sau khi UBCKNN cấp Giấy chứng nhận đăng ký chào bán.** Room ngoại tối đa 50%; nước ngoài đang giữ 1.035.355 cp (0,24%, VSD 25/08/2026). |
| Mục đích tiền | TT08 §III + NQ 07 Điều 2 | Toàn bộ 2.591,9 tỷ dùng **mua 260.000.000 cp phát hành thêm của CTCP Phát triển Nhà Đại Lộc (NĐL) @10.000**, giải ngân Q4/2026–Q1/2027. Vốn đầu tư vào dự án hỗn hợp cao tầng **lô I.14/CTHH-01, Bắc sông Cấm, Thủy Nguyên**: tổng mức đầu tư 6.223,3 tỷ, gồm 1.322,3 tỷ tiền sử dụng đất. Phần còn thiếu lấy từ vốn tự có và vốn vay. NĐL: vốn điều lệ 1.820,1 tỷ, CRV giữ 99,99%; **HHS có 58,56% quyền biểu quyết / 51,01% lợi ích, sau giao dịch tăng lên 75,41%** theo công ty. Giá trị sổ sách NĐL 11.210 đ/cp (BCTC tự lập 31/12/2025). |
| Cổ tức CP 7% | NQ ĐHĐCĐ Điều 12, theo **Tờ trình 09/TT-HĐQT** (tr.118–120) | 48.382.428 cp = 7% × **691.177.548**, tức số cp **sau** đợt quyền mua. Tỷ lệ thực hiện 100:7; nguồn là LNST chưa phân phối đến 31/12/2025. **Phát hành SAU khi kết thúc chào bán quyền mua**, trong năm 2026, sau khi UBCKNN xác nhận hồ sơ. |

**Trạng thái tại 10/11/2026:** **CHƯA thực hiện** cả hai đợt.
- Trang CBTT và trang Hoạt động HĐQT của HHS (truy cập 10/11) có văn bản mới nhất về chào bán là NQ ngày 26/08. Chưa có thông báo ngày ĐKCC, chưa có Giấy chứng nhận UBCKNN, chưa có bản cáo bạch 2026. Thông báo mới nhất trên trang CBTT là ngày 26/10 (báo cáo cổ đông lớn).
- BQ `corporate_action` ghi 2 dòng ISS `announced`, chưa có ngày, khớp với thực tế. DNSE secdef 10/11 có giá tham chiếu 9.990 = giá đóng cửa 09/11, nên chưa có điều chỉnh ex.
- **Hết hạn:** NQ không ghi ngày hết hạn. Lịch dự kiến kéo đến Q1/2027. Theo Luật Chứng khoán, có thời hạn phân phối sau khi được cấp Giấy chứng nhận, nhưng giấy này chưa được cấp. Thời hạn cụ thể **không xác định được** từ nguồn đã đọc.
- Báo chí đưa tin cùng số liệu: [vnfinvest](https://vnfinvest.vn/dich-vu-hoang-huy-hhs-trien-khai-chao-ban-gan-260-trieu-co-phieu-von-dieu-le-vuot-6900-ty-dong-73391.html), [baophapluat](https://doanhnhan.baophapluat.vn/hoang-huy-hhs-huy-dong-gan-2-600-ty-dong-tu-co-dong-don-luc-gom-co-phan-nha-dai-loc.html), [tinnhanhchungkhoan](https://www.tinnhanhchungkhoan.vn/dich-vu-hoang-huy-hhs-len-ke-hoach-chao-ban-co-phieu-moi-du-kien-huy-dong-hon-2590-ty-dong-post396752.html). Có một tin [stockbiz](https://stockbiz.vn/tin-tuc/hhs--dat-muc-tieu-doanh-thu-3000-ty-chia-co-tuc-7/39674873) ghi "~48 triệu cp 100:7": con số này khớp với TT09 vì gốc tính là 691 tr chứ không phải 432 tr.

Chưa đọc: thuyết minh sự kiện sau kỳ trong BCTC Q3/2026. Bản PDF ở `dd_HHS_20261101/src` là ảnh scan; trong phiên này chưa render các trang thuyết minh, nên mục này còn MỞ.

## 2. Cơ chế định giá

- Ký hiệu: V_pre là giá trị / cp hiện tại (phân phối r3, sau CK 5 tỷ 1,41%). c là tỷ lệ bao phủ. k là giá trị của mỗi đồng bơm vào NĐL.
- V_final = (V_pre × 431,99tr + (1 − CK) × k × c × 2.591,9 tỷ) / (431,99tr + c × 259,19tr) / 1,07.
- Công thức tuyến tính tăng theo V, nên tâm và phân vị biến đổi **chính xác**.
- **Cơ sở chọn k = 1:** luật 20 (dự án mới: base = sổ sách / NPV 0, cấm giả định "đầu tư mới ⇒ giảm giá trị"). Không có cơ sở độc lập cho k khác 1. Độ nhạy:
  - **k = 0,8**: kịch bản "thị trường chiết khấu dự án 20%". Độ nhạy xuống, không gán nhãn "không có cơ sở".
  - **k ≈ 0,946**: giữ nguyên tỷ lệ **công ty nêu** (HHS 51,01% → **75,41%** lợi ích NĐL) khi mua 260 tr cp @10.000 vs BV 11.210: HHS **thiệt −141 tỷ** (từ 2.600 tỷ nộp, giá trị sổ nhận về thấp hơn). Đây là chiều xuống CÓ cơ sở (số công ty tự nêu).
  - **k = 1,024**: nếu NĐL chỉ phát hành 260 tr cho HHS, tỷ lệ tự tính **79,8%** (lệch 75,41%), HHS hưởng **+63,5 tỷ**. Hai tỷ lệ mâu thuẫn ⇒ cấu trúc phát hành NĐL chưa rõ ⇒ độ nhạy hai chiều: k ∈ [0,946; 1,024], base giữ k = 1 (luật 20).
  - Tâm EX đủ: k=0,946 → 11.428; k=1 → 11.615; k=1,024 → 11.698.
- **Bản song song CK holding 27%:** áp k = 0,73. Lý do: tiền rời HHS để vào công ty con thì chịu cùng chiết khấu holding.

### Bảng đầy đủ — HEADLINE (CK holding 0)

| Kịch bản | k | Tâm EX | P10 | P50 | P90 | Giá trị CUM/cp hiện tại (người thực hiện đủ) | Ngưỡng luật 4 EX |
|---|---|---|---|---|---|---|---|
| Không phát hành (cổ tức 7% vẫn có) | — | 13.055 | 11.609 | 13.007 | 14.546 | 13.969 | 11.097 |
| Chỉ TCH (58,31%) | 1,0 | 12.060 | 10.989 | 12.024 | 13.164 | 14.646 | 10.251 |
| Bao phủ 50% | 1,0 | 12.169 | 11.057 | 12.131 | 13.315 | 14.833 | 10.343 |
| **Đủ 100%** | **1,0** | **11.615** | **10.711** | **11.584** | **12.546** | **13.884** | **9.873** |
| Đủ 100% | 0,8 | 10.924 | 10.020 | 10.893 | 11.855 | 12.701 | 9.285 |
| Đủ 100% | 0,946 | 11.428 | 10.525 | 11.398 | 12.360 | 13.565 | 9.714 |
| Đủ 100% | 1,024 | 11.698 | 10.794 | 11.667 | 12.629 | 14.026 | 9.943 |

Ghi chú:
- Cột CUM ở dòng đủ 100% (13.884) lệch 85 đ so với 13.969. Lý do: CK thanh khoản 1,41% áp cả lên phần tiền 6.000 đ đã nộp. Quy ước CK-trên-tiền nhất quán: các dòng CUM (đủ) là **13.884 / P10 12.337 / P90 15.479**; 13.969 / 12.422 / 15.564 là phân phối r3 nguyên bản (không CK trên tiền). Dòng CUM của ghi sổ ledger dùng bản nguyên bản; sự lệch 0,6% không đổi nhãn.
- Dòng "Không phát hành", "Chỉ TCH", "50%" cột CUM dùng cùng quy ước CK-trên-tiền (c>0).
- Bao phủ một phần làm giá trị **tăng** cho người thực hiện quyền. Lý do: giá phát hành 10.000 thấp hơn giá trị ước tính, nên người không mua bị chuyển giá trị sang người mua.

### TERP / giá quyền ngầm định
- Giá 10.000 (DNSE 10/11 10:46) bằng đúng giá chào bán. **Giá trị quyền theo thị trường ≈ 0**: TERP quyền = 10.000, sau cổ tức 7% còn **9.346**. Với giá BQ 09/11 9.990, quyền theo thị trường ≈ −10 đ/cp mới, TERP sau cổ tức 9.340.
- Hệ quả: nếu thị giá lúc GDKHQ vẫn ≤ 10.000, **nhà đầu tư nhỏ lẻ không có động cơ thực hiện quyền**, và không có tỷ lệ thành công tối thiểu. Bao phủ phụ thuộc vào TCH (58,31%, cần ≈1.511 tỷ — ước lượng = 58,31% × 2.591,9). Kịch bản "chỉ TCH" vì vậy là kịch bản thực tế, không phải đuôi. Phần thiếu **1.080,6 tỷ** (đo: 41,69% × 2.591,9 tỷ) HHS phải vay hoặc dùng vốn tự có. Theo r3, HHS và CRV hiện **không còn nợ vay** (BQ 2026Q3).

### ⚠ WARNING quản trị — vòng tiền qua bên liên quan
- **Đã đọc** NQ HĐQT **06/NQ-HĐQT 21/07/2026** (`src_hhs/png/blq.png`, ảnh scan): HHS vay **tối đa 100 tỷ** từ công ty mẹ (CTCP Đầu tư Dịch vụ Tài chính Hoàng Huy = TCH), lãi thả nổi, kỳ hạn 1 năm, bổ sung vốn lưu động, giải ngân trong 2026. Theo fundamental-skeptic **chưa rút tại Q3** (tôi chưa tự đối chiếu BCTC Q3).
- Tiền thu từ quyền mua đi vào **NĐL (CRV 99,99%; TCH giữ 38,19% trực tiếp, theo skeptic/BCTN)** qua chuỗi bên liên quan; HĐQT **tự phân bổ** cp không bán hết @10.000, khoá 1 năm (không có tỷ lệ thành công tối thiểu).
- Kịch bản **chỉ TCH thực hiện** (58,31% = **1.511,3 tỷ**): HHS phải tự lo phần còn lại **1.080,6 tỷ** để đủ 2.591,9 tỷ vào NĐL, so với tiền mặt Q3 **181,9 tỷ** ⇒ thiếu **~898,7 tỷ** (= 1.080,6 − 181,9), tức nợ ~900 tỷ nếu bù bằng vay (số cuối là suy ra, chưa kiểm cấu trúc tài trợ). Đây là WARNING, không đổi nhãn.
- Theo định giá r3 (V > 10.000), quyền có giá trị **1.489 đ/cp cũ** ở tâm = 0,6 × (V_quyền 12.481 − 10.000). Người không thực hiện quyền mất phần này: giá trị / cp hiện tại = 1,07 × 11.615 = 12.428, so với 13.884 nếu thực hiện.

## 3. Mốc hai chiều (bổ sung cho r3 §8)
- **Xuống:** UBCKNN cấp phép + ĐKCC trong khi thị giá ≤ 10.000. Khi đó bao phủ thấp và HHS phải vay để mua NĐL. Thêm nữa, rủi ro tập trung vào I.14: đây là dự án mới, chưa có giấy phép xây dựng và mở bán, giai đoạn bàn giao dự kiến từ 2028. Nếu NĐL đổi giá mua khác 10.000, hoặc đổi mục đích sử dụng tiền, thì làm lại bản này.
- **Lên:** TCH cam kết mua hết phần của mình hoặc bảo lãnh phần dư. Có báo cáo tiến độ sử dụng vốn và giấy phép xây dựng I.14.
- **HARD ABANDON (bổ sung):** NĐL phát hành cho bên khác giá thấp hơn mà HHS không tham gia; hoặc tiền thu được không vào NĐL.

## 4. Còn mở
- Thuyết minh sự kiện sau kỳ trong BCTC Q3/2026 (ảnh scan) chưa đọc.
- Hạn hiệu lực của phương án / thời hạn phân phối không xác định được.
- Cấu trúc phát hành NĐL lệch giữa 75,41% và 79,8%.
- NQ HĐQT 21/07/2026 (06/NQ-HĐQT, vay tối đa 100 tỷ từ TCH) **đã đọc** qua `src_hhs/png/blq.png` — xem WARNING quản trị §2.
- Chưa quét tin 01–10/11 ngoài website công ty.
