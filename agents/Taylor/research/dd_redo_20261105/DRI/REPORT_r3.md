# DRI — DD redo VÒNG 3 (08/11/2026, job Taylor_20261108_153743)

**Kết luận (HEADLINE ở cỡ CK tham chiếu 5 tỷ; số từ `calc/dri_redo_r3_out.txt`, MỨC KẾT CỤC, 54 kết cục = 27 ô × 2 đường giá):**
tâm **15.257 đ/cp sau CK** (15.568 trước CK) · **P10 12.908 · P50 15.293 · P90 17.549** sau CK (min 11.247).
Giá đóng cửa **06/11/2026 13.100** (BQ `tav2_bq.ticker`) ⇒ thấp hơn tâm 14,1% ⇒ **TRONG vùng, sát cạnh dưới** (cao hơn P10 1,5%); **12,5% trọng số kết cục nằm dưới giá**.
Luật 4 (giá ≤ 0,85 × tâm = 12.969): **không đạt** (giá cao hơn ngưỡng 1,0%) ⇒ **KHÔNG đủ điều kiện fear-buy §2.5**.
So r2: tâm 14.092 → **15.257 (+1.165, +8,3%)**; nhãn giữ TRONG vùng.

**Cỡ sleeve thật (dòng riêng, không phải headline):** CK 10–40 triệu chỉ 0,09–0,18% ⇒ tâm 15.554 / 15.541, P10 **13.160 / 13.148** ⇒ ở cỡ này giá 13.100 **thấp hơn P10 0,4%, tức DƯỚI vùng**. Nhãn đổi theo cỡ chỉ vì khoản CK 2,00% ở cỡ 5 tỷ; khoảng cách tới P10 rất mỏng ở cả hai cỡ.

**Thiên lệch xác nhận (ghi rõ):** DRI đã bán hết ngày 02/11. Định giá này **không neo vào quyết định bán**. Bản r2 chỉ áp thông tin mới (NQ15) theo chiều giảm, trong khi bỏ qua bằng chứng về mật độ vườn đã có sẵn. r3 sửa cả hai chiều: tâm mới cao hơn giá bán, và số liệu cứ để như vậy.

Engine `dri_val_supply_adj_r4_20261027/model.py` được exec nguyên văn, không sửa. Giả định khoá ở `calc/assumptions_r3.json`. `calc/LOCK_r3_md5.txt` (giả định + script + 17 file upstream + dữ liệu giá 06/11) được chốt **TRƯỚC** lần chạy đầu. Script v2 chỉ thêm 2 dòng báo cáo, giả định không đổi; md5 của v2 ghi nối tiếp trong LOCK. Chạy 2 lần trùng byte (txt/json/grid). Có ba selfcheck:
- (a) hàm khối mới với q=1 cho đúng giá trị engine;
- (b) cấu hình r2 tái lập **14.092 / 12.006 / 16.146** (assert);
- (c) tái lập số của skeptic (xem đính chính 2).

## 1. Kiểm từng đính chính (TOP5B_CORRECTIONS_20261108 §DRI)
| # | Đính chính | Kết luận kiểm | Tác động lên tâm (cầu nối tuần tự) |
|---|---|---|---|
| 1 | Nhánh NQ15-KINH TẾ 0,20 chỉ là nhận định | **CHẤP NHẬN.** Không có dữ liệu cho xác suất 20%. Theo luật 20 + STANDARD_r2 điều 3, tái canh đợt 1 (NQ15 Đ.3) là dự án mới ⇒ NPV0. Nhánh KINH TẾ chuyển sang độ nhạy | 14.092 → 14.288 (**+196**; khớp số skeptic 14.288) |
| 2 | Khối 1.975 ha bị coi năng suất bằng trung bình (q=1) | **CHẤP NHẬN hướng, SỬA cách mô hình.** BCTN25 tr.44 ghi "thanh lý sớm do không đảm bảo mật độ khai thác" ⇒ khối này có năng suất/ha dưới trung bình, nên q=1 là cận trên. Skeptic đặt q cho TOÀN vườn cũ (diện tích thật = A0/q = 9.607 ha @0,85), vượt **tổng diện tích cao su 8.592,3 ha** (BCTN25 tr.20) ⇒ mâu thuẫn dữ liệu. r3 chỉ đặt q cho KHỐI thanh lý và giữ tổng diện tích cạo A0 = 8.166 ha. Phần còn lại có năng suất bù sao cho 2026 vẫn ra 13.800 t: q 0,85 ⇒ 1,77 t/ha; q 0,7 ⇒ 1,85 t/ha (2025 thực tế 1,81). Trục q {0,7/0,85/1} (.25/.5/.25): độ lớn là [UL], hướng có dữ liệu | 14.288 → 14.923 (**+635**). Bản skeptic (q toàn vườn) = 15.207, chênh với r3 −50 |
| 3 | wht 10% > mức quan sát 7,0/8,3%; "chưa dẫn nguồn" | **CHẤP NHẬN MỘT PHẦN.** (i) Nguồn luật CÓ: thuế cổ tức Lào 10% theo Luật thuế thu nhập 67/NA 2019 (Wendy, nguồn thứ cấp) và Hiệp định VN–Lào 1996 Điều 10 trần 10% (đã xác minh văn bản) — `dri_val_supply_adj_r2_20261027/REPORT.md:106`. Câu "chưa dẫn nguồn" trong SUMMARY r2 là SAI. (ii) Nhưng engine trừ 10% trên TOÀN FCF, trong khi KTPL (10,6%) và quỹ dự phòng TC Lào (7,8%) đã trừ riêng và không được chuyển về ⇒ cơ sở chịu thuế = 1 − KTPL − TAU ⇒ **wht hiệu dụng 8,16%**, nằm trong dải quan sát 7,0–8,3%. Skeptic ước +300 khi dùng thẳng mức quan sát; r3 dùng 8,16% (+258). Nếu lấy mức thấp nhất 7,04% thì cộng thêm +159 — để ở độ nhạy | 14.923 → 15.181 (**+258**) |
| 4 | wp PEAK 0,6/0,4 lệch xuống | **CHẤP NHẬN.** 0,6 lấy từ Bobby CYCLICAL_PEAK (r3 PREREG.md:47), tức là nhận định ⇒ theo quy tắc chung 08/11 phải ra khỏi base. Dùng 0,5 trung tính | 15.181 → **15.257** (**+76**; khớp số skeptic +74) |
| 5 | Giá 06/11 13.100; price_date null; tỷ giá LAK chưa có nguồn | **CHẤP NHẬN.** Giá 13.100 lấy từ BQ (`calc/r3data/px_dri_20261106.csv`; 293 phiên trùng file 04/11 không lệch). Đã điền price_date. **Nguồn tỷ giá: BCTC HN Q3/2026 hn_01**, CĐKT 30/09/2026 in "VND/LAK 0,8769" (độ lớn = LAK/VND) ⇒ 1 LAK = 1/0,8769 = **1,1404 VND** (`dd_DRI_20261027/extract_q3_bctc.md:9,221`). CK tính theo dữ liệu 06/11: 2,00% (tâm r2 không đổi khi đo lại) | 0 |
| 6 | WARNING thiếu | **CHẤP NHẬN** — §5 | — |
| 7 | Thiên lệch xác nhận | **CHẤP NHẬN** — đã ghi ở đầu báo cáo | — |

Tái lập số skeptic theo cách q toàn vườn (NPV0, wht 10%, wp 0,6, CK 04/11): q 0,85 / 0,7 / 0,5 ⇒ **14.855 / 15.502 / 16.617**, so với skeptic 14.902 / 15.519 / 16.348. **Không trùng** (lệch −47 / −17 / +269). Spec lưới của skeptic không ghi rõ nên **chưa kiểm được**; hướng và cỡ tác động thì khớp. Tâm skeptic "≈14.900" trùng bước 2 của cầu nối r3 (14.923).

## 2. Lưới (mức kết cục) — trục và giả định [UL]
| Trục | Mức | Trọng số | Cơ sở |
|---|---|---|---|
| Đọc NQ15 | NPV0 | 1,0 | luật 20; nhánh KINH TẾ chỉ là độ nhạy |
| mid RSS3 thực 2014-01..2026-09 | P25 1,924 / TB 2,221 / P75 2,432 USD2025/kg | .25/.5/.25 | đối xứng (skeptic R4) |
| Đời cạo L | 22 / 27 / 32 | .25/.5/.25 | **giả định**, không có định mức nguồn |
| Mật độ q khối thanh lý | 0,7 / 0,85 / 1 | .25/.5/.25 | hướng: BCTN25 tr.44; độ lớn **[UL]** |
| Trong ô: đường giá 2027–28 | PEAK / MID | 0,5 / 0,5 | trung tính (0,6 Bobby → độ nhạy) |
| FCF = 90% LN lõi | — | — | **[UL]** engine r3 |
| wht | 8,16% = 10% × (1 − KTPL − TAU) | — | Luật 67/NA + DTA; khớp dải quan sát |

Ba con số tách bạch: tâm = kỳ vọng lưới **15.568** trước CK (15.257 sau). P50 kết cục sau CK **15.293**. Giá trị tại tham số trung tâm (TB, L27, q 0,85, wp 0,5) **15.946** trước CK; con số này cao hơn tâm vì L22 (−1.672 so với L27) và mid P25 (−2.198 so với TB) kéo xuống mạnh hơn mức L32 (+818) và P75 (+1.559) kéo lên. Đuôi dưới P10 (sau CK < 12.908; 8 kết cục, 10,9% trọng số) gồm toàn mid P25: L22 × PEAK (q 1 / 0,85 / 0,7) và L22 × MID (q 1 / 0,85); L27 × PEAK (q 1 / 0,85); L32 × PEAK × q 1. Ô P25 × L27 × PEAK × q 0,7 (13.408) và P25 × L22 × MID × q 0,7 (13.250) KHÔNG nằm dưới P10; không còn nhánh trọng số nhỏ nào chi phối đuôi dưới. (Kiểm lại từ `calc/grid_dri_redo_r3.csv` × (1 − CK 2,00%).)

Theo q (sau CK): q 1 ⇒ 14.605 (P10 12.354, 21,9% dưới giá) · q 0,85 ⇒ 15.257 · q 0,7 ⇒ 15.909 (3,1% dưới giá).

## 3. Biến thể song song + độ nhạy (tâm sau CK 5 tỷ; headline 15.257)
| Biến thể | Tâm | P10 / P50 / P90 | % dưới giá |
|---|---|---|---|
| **HEADLINE r3** | **15.257** | 12.908 / 15.293 / 17.549 | 12,5% |
| Skeptic: q toàn vườn cũ | 15.207 | 12.912 / 15.264 / 17.331 | 12,5% |
| q = 1 (không có trục mật độ) | 14.605 | 12.354 / 14.682 / 16.616 | 21,9% |
| q khối 0,5 | 16.779 | 14.219 / 16.829 / 19.136 | 3,1% |
| Nhánh KINH TẾ 0,1 / 0,2 / 0,3 | 15.093 / 14.928 / 14.763 | (0,2: 12.437 / 15.072 / 17.302) | 15,0 / 17,5 / 20,0% |
| Chỉ nhánh KINH TẾ (tái canh phá giá trị 100%) | 13.611 | 10.980 / 13.695 / 15.941 | 37,5% |
| Bản cũ bỏ qua NQ15 (giữ vườn L27 0,8 + bị buộc 0,2) | 15.938 | 12.861 / 16.160 / 18.983 | 12,5% |
| Moat NONE½ (biên về ½ gap ngành) — chỉ độ nhạy rủi ro | 13.640 | 11.481 / 13.631 / 15.757 | 39,1% |
| Moat NONE (biên về trung vị ngành 11,70pp) — chỉ độ nhạy rủi ro | 12.022 | 9.742 / 12.099 / 14.050 | 74,2% |

Độ nhạy một trục (tâm sau CK):
- wht: 10% phẳng (r2) 14.997 (−260) · 7,04% 15.416 (+159) · 8,30% 15.237 (−20).
- wht tách theo nguồn (từ skeptic, đã chạy lại, không đổi headline): engine (`dri_val_supply_adj_r4_20261027/model.py:90-91`) áp wht 8,16% cả cho tiền đấu giá gỗ lẫn phần capex dư, vốn không trừ KTPL/TAU nên đúng ra giữ 10%. Skeptic chạy lại: tâm **15.224 (−33)**, P10 **12.874**, nhãn TRONG vùng (sát cạnh dưới) không đổi. Không sửa engine/headline; ghi nhận là độ nhạy (thiên nhẹ về phía lạc quan, −33 đ/cp).
- wp PEAK: 0,4 → 15.334 · 0,6 → 15.181 · 0 → 15.639 · 1 → 14.876.
- FCF/LN lõi: 80% → 14.321 (−936) · 100% → 16.193 (+936).
- Dakruco: haircut 50% −268 · mất trắng −536. Giữ 15% tiền Lào −395.
- Giá gỗ: LAK ±10% ⇒ ±164 · giá gỗ cũ 20,87 tr/ha −807.
- Lãi huy động (β=1): −100bp 15.635 · −50bp 15.443 · +50bp 15.077 · +100bp 14.902 (−2,3%).
- CK Y 0,5 / 1,5: 15.413 / 15.102.

**Giá ngụ ý** (giải từng tham số một, các trục khác giữ như headline): giá 13.100 tương ứng **FCF/LN lõi 67%** (base 90%), hoặc **lãi huy động 12T 14,7%** (r 20,8%). Giá này KHÔNG đạt được bằng riêng trọng số nhánh KINH TẾ (100% ⇒ 13.611), riêng q (q=1 ⇒ 14.605) hay riêng wp (1,0 ⇒ 14.876). Nó khớp với giả thiết **lợi thế giá thành DRI không bền**: kịch bản biên về trung vị ngành (moat NONE) cho 12.022 < giá, NONE½ cho 13.640, cao hơn giá 4,1% (tức sát giá, vẫn nằm trên). Theo quy ước 08/11, moat không bền thì không cộng, không trừ ⇒ NONE chỉ là độ nhạy, không phải headline. Đây là kênh rủi ro lớn nhất mà headline không tính.

## 4. Thanh khoản
ADV trung vị 250 phiên **8,33 tỷ**, 60 phiên **13,82 tỷ**; σ 2,58% (cửa sổ 05/11/2025–06/11/2026).
- Cỡ tham chiếu **5 tỷ** (Q/ADV250 0,60×, trong vùng hiệu chỉnh): CK **2,00%** (theo ADV60: 1,55%). **Headline và nhãn tính ở cỡ này.**
- Cỡ sleeve thật 10–40 triệu: CK **0,09–0,18%** (ADV60 0,07–0,14%). Tâm 15.554 / 15.541, P10 13.160 / 13.148, 10,9% dưới giá ⇒ DƯỚI vùng (sát ranh giới). Vị thế thật = 0 (đã bán 02/11).

## 5. WARNING pháp lý / quản trị (đầy đủ; mang từ r2 + bổ sung r3)
- **Vụ án Dakruco** (cổ đông ~45%, mã DRG): 2 cựu TGĐ bị khởi tố; 5 bị can bị truy tố 02/2025. Rủi ro lan sang DRI qua giao dịch bên liên quan.
- **ĐHĐCĐ 22/10/2026 nâng ngưỡng giao dịch bên liên quan** cần ĐHĐCĐ duyệt từ 10% lên 30% tổng tài sản, cùng ngày Tờ trình 40 (Dakruwood). legal-vn (daily_day4): mức 30% hợp pháp (điều lệ chỉ được đặt ngưỡng thấp hơn 35%, NĐ155 Đ293 k4b cộng dồn 12 tháng) và là nới quyền kiểm soát của cổ đông nhỏ.
- **NQ HĐQT 15**: nghiên cứu mua Dakruwood từ Dakruco (HĐQT xét 12/2026).
- **Đấu giá 1.975,23 ha**: bán một lô, giá cố định 4 năm, **không cấm bên liên quan mua** ⇒ theo dõi danh tính bên trúng.
- **[MỚI r3] Tiền lệ gia hạn khoản vay**: DRI đã **gia hạn** khoản vay 40 tỷ cho công ty mẹ Dakruco (Thời báo Tài chính, `thoibaotaichinhvietnam.vn/...-158125.html`, trích `data/intraday_watch/crisis_dd/DRI_2026-11-02/notes/daily_day4_taylor.md:42`). Điều này mâu thuẫn với cách viết "đang trả đúng hạn" của r2. Base vẫn ghi theo sổ sách (dư nợ 40 tỷ, TSĐB 6 triệu cp DRI) vì chưa có dữ liệu suy giảm; độ nhạy: haircut 50% −268, mất trắng −536.
- **[MỚI r3] Rủi ro cùng chiều (wrong-way) của tài sản đảm bảo**: tài sản đảm bảo của khoản vay 40 tỷ là **6 triệu cổ phiếu chính DRI** ⇒ nếu Dakruco/DRI gặp khó thì giá cổ phiếu DRI giảm đúng lúc cần thu hồi nợ, tức tài sản đảm bảo mất giá cùng lúc với khả năng trả nợ của bên vay. Độ nhạy haircut/mất trắng ở trên chưa phản ánh tương quan này (coi TSĐB là lớp đệm độc lập) nên có thể đánh giá thấp tổn thất.
- **[MỚI r3] Giấy nhượng đất 2016** (01616/KĐ/DDT4) **chưa xác minh** (SKEPTIC_R4_20261103 mục 4). Mô hình cho quyền đất tới 2054 (END engine) dù văn bản chưa công khai; một phần đất thuộc quy hoạch rừng bảo tồn.
- **[MỚI r3] Rủi ro tỷ giá tiền đấu giá**: LAK yếu ~6% trong 9T/2026 (0,8252 → 0,8769 LAK/VND); giá khởi điểm cố định bằng LAK trong 4 năm (±10% ⇒ ±164 đ/cp).
- Tiền gửi Quỹ TDND Cao su ĐL 70 tỷ + góp vốn 3 tỷ (soát xét chưa xác định giá trị thu hồi khoản góp). ~197 tỷ tại Lào không thuyết minh nguyên tệ/lãi/kỳ hạn.
- Liên hệ framework §3 **HARD ABANDON #4** (giao dịch bên liên quan chuyển giá trị ra cổ đông lớn).
- "Chưa thấy xử phạt/khởi tố DRI 2026": WebSearch **05/11/2026** (r2), **không tra lại ở r3**.

**Lưu ý skeptic chưa kiểm được:** (i) số q của skeptic không tái lập đúng (xem §1); (ii) độ lớn q thật không có số đo (chỉ có hướng); (iii) Luật 67/NA là nguồn thứ cấp, chưa tách được cơ sở chịu wht thật (LN chuyển về) từ BCTC. Độ nhạy tương ứng ở §3.

**Ghi chú caveat (không đổi số):**
- Độ lớn q của khối thanh lý là giả định [UL], chưa có số đo (chỉ có hướng, BCTN25 tr.44), nhưng là bước đóng góp lớn nhất trong cầu nối (+635).
- Base giữ Cref riêng của DRI (30,22 tr/t) tới 2054. Rủi ro biên LN về mức ngành (moat NONE, tâm 12.022) là kênh lớn nhất mà headline không tính.
- Vị thế đã bán hết 02/11 ⇒ định giá này không được neo vào quyết định bán; không dùng để hợp thức hoá việc bán hay mua lại.
- wht: xem dòng "tách theo nguồn" ở §3 (−33, từ skeptic).

## 6. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Thời điểm | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|---|
| SXKD tháng 10 | ~10/11/2026 | Bán ≥ ~1.390 t/tháng | < 1.000 t |
| Kết quả đấu giá 1.975 ha | Q4/2026 | Giá trúng > khởi điểm, bên thứ ba | Bên trúng = Dakruco/Dakruwood; hoặc huỷ |
| Công bố mật độ/năng suất khối thanh lý | khi có | q đo < 0,85 | q ≈ 1 (−652 về bản q=1) |
| HĐQT xét Dakruwood | 12/2026 | Không mua / giá ≤ sổ sách có thẩm định | Mua giá cao từ cổ đông lớn |
| Khoản vay Dakruco 40 tỷ | đến hạn | Trả đủ | Gia hạn thêm / không lãi |
| BCTC Q4/2026 | ~20/01/2027 | Tồn kho giảm, CFO ≥ LNST; GPM giữ trên peer | GPM về gần peer (kênh moat NONE) |
| Giá cổ phiếu (cỡ 5 tỷ) | — | < P10 12.908 ⇒ DƯỚI vùng; ≤ 12.969 ⇒ đạt luật 4 | > P90 17.549 ⇒ TRÊN vùng |

**HARD ABANDON** (đề xuất, chờ user duyệt): (1) DRI mua Dakruwood/tài sản Dakruco giá > sổ sách hoặc không có thẩm định độc lập; (2) khoản vay Dakruco quá hạn, hoặc gia hạn lần nữa không lãi; (3) bên trúng đấu giá là bên liên quan với giá ≈ khởi điểm; (4) vụ án Dakruco mở rộng sang nhân sự/giao dịch DRI. Vị thế thật = 0 ⇒ không cần tranche.

## Phụ lục — cầu nối r2 → r3 (tâm sau CK 5 tỷ, tuần tự; `bridge_r2_to_r3` trong SUMMARY.json)
| Bước | Tâm | Δ |
|---|---|---|
| r2 công bố (giá 13.500 @04/11) | 14.092 | — |
| CK theo dữ liệu 06/11 (1,997% → 2,00%) | 14.092 | −0 |
| (1) bỏ nhánh KINH TẾ 0,20 → NPV0 1,0 | 14.288 | +196 |
| (2) trục q khối {0,7/0,85/1} | 14.923 | +635 |
| (3) wht 10% → 10% × (1 − KTPL − TAU) = 8,16% | 15.181 | +258 |
| (4) wp PEAK 0,6 → 0,5 = **r3** | **15.257** | +76 |

| | r2 | **r3** |
|---|---|---|
| Tâm sau CK | 14.092 | **15.257** |
| P10 / P50 / P90 sau CK | 12.006 / 14.235 / 16.146 | **12.908 / 15.293 / 17.549** |
| Giá tham chiếu | 13.500 (04/11) | **13.100 (06/11)** |
| % trọng số dưới giá | 35,2% | **12,5%** |
| Nhãn (cỡ 5 tỷ) | TRONG vùng | **TRONG vùng (sát cạnh dưới)** |
| n kết cục | 36 | 54 |

Không sửa `kb/dd_price_zones.json` (Mike ghi sổ sau phản biện cuối). Không đặt lệnh, không email, không PDF.
