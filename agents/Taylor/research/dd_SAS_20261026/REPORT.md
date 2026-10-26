# DD — SAS (CTCP Dịch vụ Hàng không Sân bay Tân Sơn Nhất, SASCO) · 2026-10-26 · job `Taylor_20261026_012530`

> NGHIÊN CỨU READ-ONLY, không phải khuyến nghị mua. User quyết. Khung: `calculated_fear_state_backstop.md`
> §2.5 (nhóm (d) gián đoạn / chuyển dịch hạ tầng) + quét §2 (pháp lý/quản trị). Pháp nhân đã xác minh: mã SAS
> (UPCoM) = SASCO, Chủ tịch HĐQT Johnathan Hạnh Nguyễn, khai thác thương mại tại sân bay Tân Sơn Nhất (TSN).
>
> Nguồn: **[BQ]** = `tav2_bq.ticker_financial` (CANONICAL theo `kb/data_registry/fundamentals/ticker_financial.md`)
> và `tav2_bq.ticker`; **[BC-BCTC]** = báo chí trích BCTC Q3/2026 công bố 21/10/2026 (DNSE Senses/Người Đưa Tin,
> index.vn); **[ĐHĐCĐ]** = vietnambiz 25/06/2026; **[ĐHĐCĐ-BT]** = DNSE Senses 09/10/2026 (ĐHĐCĐ bất thường 08/10);
> **[Q2]** = baophapluat (BCTC Q2/2026). Tính toán: `src/val.py` → `src/val_out.txt`.
> ⚠️ **Giới hạn**: KHÔNG tải được file PDF BCTC Q3/2026 gốc trong phiên này — số dòng BCTC là qua báo chí trích dẫn,
> đã đối chiếu với BQ ở những chỗ có thể (NP, DT, vốn chủ khớp). Số không đo được gắn **(ước lượng)**.

## 0. Kết luận

**Verdict: NON** (tại giá 37.000 đ, phiên 23/10/2026). SAS **không ở trạng thái khủng hoảng** — lợi nhuận đang ở
mức kỷ lục — và cái "rẻ" PE 5,4x là ảo giác của (i) lợi nhuận một lần trong 4 quý gần nhất, (ii) thu nhập cổ tức
đầu tư không đều, và (iii) thị trường chiết khấu một rủi ro **CẤU TRÚC** chứ không phải chu kỳ: ~90% chuyến bay
quốc tế rời TSN sang Long Thành giai đoạn 2027–2028, trong khi mảng sinh lời nhất của SASCO (miễn thuế, phòng chờ
quốc tế) gắn với khách quốc tế tại TSN, và suất kinh doanh ở Long Thành phải qua đấu thầu cạnh tranh — chưa có gì
trong tay.

| Tiêu chí §2.5 | Phán quyết | Bằng chứng chính |
|---|---|---|
| Có "khủng hoảng" để mua sợ hãi? | ❌ Không | LN 9T/26 539,5 tỷ (+64,4% YoY) [BC-BCTC]; LN 2025 kỷ lục 844 tỷ LNTT [ĐHĐCĐ]. Giá −28% từ đỉnh 51.700 (02/2025) [BQ] là co định giá, không phải sập lõi |
| #1 Chu kỳ, không cấu trúc | ❌ Rủi ro chính là CẤU TRÚC | Chuyển chuyến bay quốc tế TSN→Long Thành (Cục HK: 28/3/2027–25/3/2028, trừ đường bay <1.000 km của hãng VN) — mất vĩnh viễn phần lớn khách quốc tế tại TSN, không phải cầu giảm tạm |
| #2 Sống sót qua đáy | ✅ MẠNH | Không vay nợ; tiền + tiền gửi ngắn hạn ~945 tỷ = 40% tổng tài sản; VCSH 1.878 tỷ [BC-BCTC, khớp BQ BVPS×CP] |
| #3 Leader chi phí thấp | ⚠️ Leader nhưng KHÔNG chuyển được | Vị thế độc quyền thực tế ở TSN đến từ hợp đồng mặt bằng với ACV (lịch sử giao thẳng không đấu thầu — §6), không phải lợi thế chi phí mang sang sân bay mới |
| #4 Sàn tài sản thực PB≲1 | ❌ | PB **2,61** [BQ]; giá trị nằm ở quyền khai thác mặt bằng, không ở tài sản hữu hình thanh lý được |

**Định giá (§4):** kỳ vọng có trọng số ≈ **32.600 đ** (−12% so giá) — xác suất kịch bản là chủ quan (ước lượng).
PE trên LN chuẩn hoá ≈ **8,1–8,5x** (không phải 5,4x).

**Điều kiện đổi verdict:** §5. **Pháp lý: WARNING** (§6) — không có vụ án đang mở, nhưng có rủi ro hợp đồng/đất
đai và giao dịch bên liên quan.

**Thanh khoản (ràng buộc thực thi, độc lập với verdict):** free float ≈ 4,4% (ACV 49,07% + nhóm IPP 46,50%)
[ĐHĐCĐ-BT]; TB 20 phiên 11/9–8/10 ≈ 20.125 cp/phiên ≈ 0,7 tỷ [ĐHĐCĐ-BT]; TB tháng 10 đến 23/10 = 1,76 tỷ/phiên
nhưng bị kéo bởi phiên 09/10 (5,45 tỷ, sau tin chuyển HOSE) [BQ].

---

## 1. Giả thuyết đã lập và kiểm chứng

| # | Giả thuyết | Kết quả |
|---|---|---|
| H1 | Q3 thấp hơn Q2 vì mùa vụ/lõi yếu đi | **Bác bỏ phần lớn.** Chênh NP Q2→Q3 = 47,0 tỷ [BQ]. Thu nhập tài chính Q2 = 114 tỷ (cổ tức 88) [Q2] vs Q3 ~60 tỷ (cổ tức 47,8) [BC-BCTC] ⇒ ~54 tỷ trước thuế chênh chỉ do **thời điểm nhận cổ tức đầu tư**. DT Q2 775,0 vs Q3 779,7 [BQ] — lõi đi ngang. Q3 không phải quý yếu theo mùa (Q3/25 106,9; Q3/24 180,6 [BQ]) |
| H2 | PE 5,4x phóng đại do một lần | **Xác nhận.** TTM 906,9 tỷ gồm Q4/25 = 367,4 tỷ [BQ], quý có "khoản bù lợi nhuận mảng bán hàng miễn thuế" (đối tác cũ DFS kết thúc HĐ 31/12/2025) [vietstock 01/2026; ĐHĐCĐ] — **chưa có số tiền khoản bù** (không tìm được). Ban lãnh đạo cũng loại ~40 tỷ hoàn nhập quỹ lương 2025 khi so sánh [ĐHĐCĐ] |
| H3 | Mất đối tác DFS làm lõi miễn thuế suy yếu | **Một phần.** DT miễn thuế Q3 >224 tỷ, **−21,5% YoY**, nhưng biên gộp 21,5%→32,9% do tự nhập-tự bán [BC-BCTC]. Đổi lại: không còn LN bảo đảm từ đối tác, hàng tồn kho 204,3 tỷ (~3x đầu năm, hàng hoá 57,3→191,4 tỷ, chưa trích lập) [BC-BCTC]. Chủ tịch nói tự vận hành "không thể kéo dài"; đã ký đối tác mới để không gián đoạn, đang đàm phán nhà cung cấp cho 2027 [ĐHĐCĐ, ĐHĐCĐ-BT] — điều khoản chưa công bố |
| H4 | Long Thành là rủi ro cấu trúc lớn nhất | **Xác nhận (định tính), chưa lượng hoá được bằng số công ty.** Xem §3 |
| H5 | Chất lượng LN kém (dòng tiền) | **Có cảnh báo.** CFO 9T/26 = 294,2 tỷ vs LNST 539,5 (0,55x), giảm từ 483,5 cùng kỳ — do tồn kho miễn thuế + 124,7 tỷ thuế TNDN đã nộp [BC-BCTC]. Theo quý [BQ CF_OA_P0]: 126,9 / 97,7 / 88,6 vs NP 155,1 / 215,7 / 168,7. Q4/25 CFO **−20,7** vs NP 367,4 [BQ] ⇒ khoản bù DFS chưa thành tiền trong quý đó. Điểm tích cực: phải thu IPP Group Pte 194 tỷ đã thu xong [BC-BCTC] |

## 2. Cơ cấu doanh thu Q3/2026 [BC-BCTC] — tổng 779,2 tỷ, khớp DT BQ 779,7

| Mảng | DT Q3/26 | YoY | Phụ thuộc khách quốc tế TSN (ước lượng định tính) |
|---|---|---|---|
| Miễn thuế (duty-free) | >224 tỷ (~29%) | −21,5% | Gần như toàn bộ |
| Phòng chờ (lounge) | 219,1 tỷ (~28%) | ~0% | Cao (phòng chờ quốc tế; có một phần nội địa) |
| Khác (F&B, dịch vụ…) | 227,3 tỷ (~29%) | +12,6% | Trộn; T3 (nội địa) hỗ trợ |
| TTTM & chi nhánh | 108,8 tỷ (~14%) | +12,8% | Thấp hơn |

Không có LN gộp/LN theo mảng ⇒ **không đo được** tỷ trọng lợi nhuận phụ thuộc quốc tế. Ước lượng thô: 40–60% LN
gộp (ước lượng) — đây là biến lớn nhất trong định giá và là chỗ yếu nhất của báo cáo này.
Biên gộp toàn công ty: 58,1% → 65% (Q3 YoY) [BC-BCTC]; BQ `GPM_P0` = 0,682 — **lệch** với 65% của báo chí, chưa
giải thích được (có thể BQ dùng định nghĩa khác/trượt quý); báo cáo dùng số báo chí trích BCTC.

Kế hoạch ACV/SASCO cho TSN 2026: 46,3 triệu khách (+10%), quốc tế 19,9 triệu (+13%, ~43% tổng) [ĐHĐCĐ].

## 3. Long Thành — vì sao là CẤU TRÚC, không phải chu kỳ

- Lộ trình mới nhất (Cục Hàng không): bay quốc tế đường dài + hàng hoá chuyển 28/3–29/10/2027; phần quốc tế còn lại
  30/10/2027–25/3/2028; ngoại lệ đường bay <1.000 km do hãng VN khai thác (Người Quan Sát). Đề xuất trước của ACV
  sớm hơn (từ mùa đông 2026), báo chí nêu ~90% chuyến quốc tế chuyển vào 2027 (VnExpress). **Chưa xác minh được
  bản nào là quyết định chính thức** — ghi rõ lệch, không chọn im lặng; cả hai đều rơi vào 2027–2028.
- SASCO: "đã chuẩn bị concept, nhân sự, tài chính, hồ sơ dự thầu" cho miễn thuế/F&B/bán lẻ tại Long Thành, **chưa có
  thông tin gói thầu chính thức**; tự nhận cạnh tranh cao hơn và thị phần sẽ thấp hơn ở TSN [ĐHĐCĐ, ĐHĐCĐ-BT].
- Hàm ý: thu nhập mảng quốc tế tại TSN không "hồi lại" sau khi chuyển — nó chỉ được thay bằng hợp đồng mới ở Long
  Thành NẾU thắng thầu, với điều khoản (phí nhượng quyền/chia doanh thu) chưa biết. Đây đúng là dạng
  "mất giấy phép/vị trí hoạt động" trong danh sách loại của §2.5, không phải cầu giảm tạm.
- Đối trọng: ACV vừa là cổ đông lớn nhất SASCO (49,07%) vừa là chủ đầu tư/khai thác Long Thành ⇒ có động cơ để SASCO
  tham gia, nhưng bị ràng buộc bởi đấu thầu (§6). Đây là lý do kịch bản bear không phải xác suất áp đảo.

## 4. Định giá — trên LN chuẩn hoá, không dùng Q3 đơn lẻ (`src/val_out.txt`)

Vốn hoá tại 37.000 đ × 133,45 triệu CP = **4.938 tỷ**.

| Cơ sở LN | LN (tỷ) | PE |
|---|---|---|
| TTM 4 quý [BQ] | 906,9 | 5,44 |
| FY2026e = 9T 539,5 + Q4 150–180 (ước lượng; KH LNTT 802 tỷ, 9T đạt 79,6%) | 690–720 | 6,9–7,2 |
| FY2026e trừ cổ tức đầu tư 9T (135,8 tỷ × 0,8 sau thuế) | 581–611 | **8,1–8,5** |

Tỷ lệ EPS/LNST 2025 = 0,883 (EPS 4.602 [ĐHĐCĐ] vs 695,6 tỷ/133,45 tr CP [BQ]) — phần trích quỹ không thuộc cổ đông.

**Kịch bản** (chiết khấu r=14%, EPS chuẩn hoá 4.301 đ = LN 650 tỷ × 0,883 / CP; cộng ~3.500 đ/CP tiền thừa — ước lượng
~50% của 945 tỷ tiền+TG, phần còn lại coi là vốn lưu động mảng miễn thuế tự vận hành):

| Kịch bản (từ 2028) | Giá trị/CP | Xác suất (chủ quan) |
|---|---|---|
| Bull — thắng thầu lớn ở Long Thành, LN +5% | 43.300 | 25% |
| Base — thị phần nhỏ hơn ở Long Thành, LN −25% | 33.000 | 45% |
| Bear — trượt thầu chính, LN −50% | 23.000 | 30% |
| **Kỳ vọng** | **32.600 (−12%)** | |

Độ nhạy base: r=12% → 39.300; r=16% → 28.600. Cổ tức là đỡ giá chính: 2025 chia tiền 46,24% (4.624 đ/CP, >617 tỷ)
[ĐHĐCĐ] = 12,5% lợi suất tại 37.000 — nhưng phần này đã gồm LN một lần 2025 và có thể không lặp lại ở mức đó.
**Không có biên an toàn** ở giá hiện tại.

## 5. Điều kiện đổi verdict

- → **AMBIGUOUS/xem xét lại**: (a) SASCO công bố trúng thầu miễn thuế và/hoặc phòng chờ tại Long Thành với điều khoản
  rõ (thời hạn, phí nhượng quyền) — khi đó rủi ro cấu trúc giảm; hoặc (b) giá ≤ ~23.000 (≈ giá trị kịch bản bear)
  trong khi lõi TSN chưa suy giảm.
- → **QUALIFY**: chỉ khi có một cú sốc tạm thời thật sự (vd gián đoạn lưu lượng/hàng không ngắn hạn) đánh sập giá
  xuống vùng bear trong khi Long Thành đã được bảo đảm — hiện không có.
- Cần đọc thêm khi có: BCTC Q3/26 gốc (thuyết minh LN theo mảng, khoản bù DFS Q4/25, tên khoản đầu tư trả cổ tức),
  điều khoản đối tác miễn thuế mới, quyết định chính thức lộ trình chuyển chuyến bay.

## 6. Pháp lý & quản trị — WARNING (không có vụ việc hình sự/khởi tố liên quan SASCO được tìm thấy)

- **Hợp đồng mặt bằng không qua đấu thầu**: Thanh tra Chính phủ (kết luận 2017) chỉ ra ACV giao trực tiếp phần lớn
  mặt bằng dịch vụ sân bay từ 2010 không đấu thầu; một số lô đất ACV/SASCO dùng chưa hoàn tất thủ tục giao/thuê;
  Bộ Tài chính (2019) ghi nhận SASCO quản lý 20 lô đất >7,2 triệu m² (anninhthudo, thuonghieucongluan — tin cũ,
  chưa thấy kết quả xử lý cuối cùng). Hệ quả đã thấy: tiền thuê đất **truy thu 2015–2024** "hàng chục tỷ" hạch toán
  Q4/2025 [vietstock]. Rủi ro: thêm truy thu; và mặt bằng mới (Long Thành) gần như chắc phải đấu thầu.
- **Giao dịch bên liên quan / xung đột lợi ích**: nhóm IPP (IPPG 24,98%, ACFC 14,89%, DAFC 4,92%, DAT 1,71%)
  [ĐHĐCĐ-BT] vừa là cổ đông vừa là bên giao dịch (phải thu IPP Group Pte 194 tỷ — đã thu; lịch sử phải thu liên doanh
  Nhà Việt ~292 tỷ, trích lập ~251 tỷ phải thu dài hạn đến 2024 [tinnhanhchungkhoan 10/2024]). Nguồn cổ tức đầu tư
  (88 + 47,8 tỷ) chưa xác định được bên trả — cần đọc thuyết minh.
- **Backstop NN**: ACV 49,07% (<50%, không chi phối đơn độc) — §2 trụ #2 không thoả nếu xét theo khung nhóm (a).
- Kế hoạch chuyển HOSE + có thể phát hành thêm CP tăng free float (chưa có lịch) [ĐHĐCĐ-BT] — pha loãng/cung cổ
  phiếu là rủi ro giá ngắn hạn, đồng thời là catalyst thanh khoản.

## 7. Lệch dữ liệu ghi nhận (không tự chọn im lặng)

- BQ `Cash_P0` Q3/26 = 280,7 tỷ vs báo chí "tiền + tiền gửi ngắn hạn ~945 tỷ" — BQ thiếu đầu tư ngắn hạn (cùng bẫy
  như DDV). Dùng 945.
- BQ `GPM_P0` 0,682 vs biên gộp 65% báo chí trích BCTC — chưa giải thích.
- BQ `EPS` = 0 cho mọi quý SAS — cột hỏng cho mã này; dùng EPS từ ĐHĐCĐ.
- "LN cốt lõi 9T 666 tỷ" (lời Chủ tịch [ĐHĐCĐ-BT]) > LNTT 9T 638 tỷ [BC-BCTC] — định nghĩa "cốt lõi" của DN không
  đối chiếu được.
- Funnel 8L ghi thanh khoản 1,1 tỷ/phiên; BQ TB tháng 10 = 1,76 tỷ (phiên tin HOSE kéo lên), TB 20 phiên trước đó ≈ 0,7
  tỷ — dùng dải 0,7–1,8 tỷ.
- Lộ trình Long Thành: hai phương án (ACV sớm hơn vs Cục HK 2027–28) — chưa rõ bản nào chính thức.

Nguồn web: dnse.com.vn/senses (SASCO lãi tăng mạnh… hàng tồn kho phình to; Sếp Sasco muốn cổ phiếu bớt cô đặc;
ĐHĐCĐ Sasco), vietnambiz.vn (ĐHĐCĐ 25/06/2026), vietstock.vn (01/2026, Q4/2025), doanhnhan.baophapluat.vn (Q2/2026),
nguoiquansat.vn / vov.vn / vnexpress.net (lộ trình Long Thành), anninhthudo.vn / thuonghieucongluan.com.vn (thanh tra
ACV), tinnhanhchungkhoan.vn (Q3/2024).
