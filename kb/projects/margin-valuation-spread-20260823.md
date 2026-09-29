# Margin theo khoảng cách định giá + nhận diện đáy cực rẻ (11/2022)
> Dự án ĐÓNG 2026-08-23 (1 ngày, 5 vòng nghiên cứu liên tiếp trên cùng tập 7 episode dd52≤−20%).
> Status: **NO-GO cho mọi cơ chế sizing/gate mới. `capit_margin_lever` (dd52≤−20%, f=1,3, CAPIT-only,
> SpaceX) GIỮ NGUYÊN, live từ 2026-08-24.** Sau ngày này KHÔNG mở thêm biến thể nào trên cùng tập
> episode — bằng chứng mới chỉ đến từ thời gian thật (shadow-log spread trong EOD report).
>
> ⚠️ **ĐÍNH CHÍNH 2026-08-24 (user phản biện, có căn cứ số liệu — xem §"Đính chính" cuối file):**
> bộ phân loại nhị phân LIQUIDITY_POLICY/FUNDAMENTAL_REAL của vòng "mechanism-classifier" THIẾU một
> trục quan trọng — phân biệt khủng hoảng PHÒNG THỦ CÓ MỤC TIÊU (dễ hồi) với khủng hoảng CƠ CẤU TỰ
> CỘNG DỒN (không xử lý nhanh được). Việc này **không đổi verdict NO-GO của Phase 1 engine** (đó là
> giới hạn công cụ, không phụ thuộc cách gộp episode) — nhưng đổi cách đọc "phản ví dụ 2010-08-25":
> nó không phải bằng chứng chống giả thuyết, mà là **N=7 đếm thừa** (2 trong 7 rất có thể là 2 đợt
> sóng của CÙNG một khủng hoảng cơ cấu 2007-2012, không độc lập). Đọc kỹ mục đính chính trước khi
> dùng bảng 7-episode ở bất kỳ nghiên cứu tương lai nào.

## Mandate user (nguyên văn, 2026-08-23)
"Có nhiều thời điểm việc sử dụng margin sẽ nâng cao hiệu quả đầu tư hơn hẳn, nhất là trong những giai
đoạn thị trường đã suy giảm mạnh làm gap giữa earnings của thị trường so với tiết kiệm lớn rõ rệt. Tôi
nhớ có những giai đoạn tỉ lệ cổ tức tiền mặt đều vượt lãi suất huy động 1 năm... Hãy nghiên cứu lại cách
vận hành để thực sự đưa margin vào thành một cơ chế hợp lý chứ không lảng tránh nó." Bổ sung: "cuối
tháng 11/2022 cũng là thời điểm rất rẻ... phân tích kỹ các điều kiện để nhận ra những thời điểm như vậy".

## Kết luận — 5 vòng, thứ tự thời gian
| Vòng | Job | Câu hỏi | Kết quả |
|---|---|---|---|
| 0 | `Taylor_20260823_075808` | Spread EY/DY vs deposit có thật không, carry sau lãi vay | User nhớ ĐÚNG: DY(payer)>deposit ở 4 episode (2012-13/2015-16/2020-03/2020-07), đỉnh 11/2012 DY 11,5% vs 9,0%. Ở cấp chỉ số cap-weighted KHÔNG BAO GIỜ. Carry ròng sau lãi vay ≥0 có thật (net12 median +30,2pp trục DY, +8,7pp trục EY; dose-response đơn điệu). **Bẫy đo được**: ngưỡng PERCENTILE PIT đảo chiều kết quả — chỉ dùng mốc TUYỆT ĐỐI neo lãi suất. |
| 0b | data-ops native | `Dividend_1Y` có gộp cổ tức cổ phiếu? | KHÔNG — cash-only (verify OCB/MBB), dùng thẳng. |
| 0c | `Mafee_20260823_083327` | Tỷ lệ ký quỹ thật gói 1840 | **maintenance 40% / liquidation 30% / lãi 12,5%/năm** (DNSE API live). Ghi `kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md`. |
| 1 | `Taylor_20260823_083709` | Điều kiện nhận diện đáy 11/2022; có định thời điểm trong episode được không | **Đính chính premise**: VNINDEX từ đáy 15/11/2022 +23,1%/12 tháng (KHÔNG x2); cấp cổ phiếu median +42,4%, chỉ 18,1% mã x2; chỉ 2/7 đáy (2009-02, 2020-03) có median mã x2; phản ví dụ 2010-08-25 median mã **−46,8%**. Tín hiệu phân biệt 09/2022 vs 11/2022 CÓ THẬT (PE pctile 0,80→0,16, PB 1,15→0,66, %>MA200 10%→3,7%) nhưng KHÔNG định thời điểm được (cùng ngưỡng fire −228…+55 ngày quanh đáy khác). **Lỗi đo phát hiện**: spread theo THÁNG bỏ sót 11/2022; theo NGÀY spread dương +2,04pp, khớp 5/7 đáy. Đề xuất V8 tranche theo độ sâu. |
| 2 | `Taylor_20260823_110750` | Phân loại cơ chế sốc THANH KHOẢN/CHÍNH SÁCH vs CƠ BẢN THẬT (prereg trước outcome, ROE/NP PIT) | **NO-GO — bằng chứng đi NGƯỢC**: 2010-08-25 nhãn SẠCH liquidity/policy (lợi nhuận giữ, ROE +3,6%) nhưng median mã −46,8%; 2022-11 thu nhập thiệt hại NẶNG NHẤT 7 episode (ROE −42,6%) nhưng median mã +42,4%. GFC 2008 thiệt hại thu nhập NHẸ NHẤT trong 3 ứng viên — cơ chế là de-rating từ bong bóng, không phải thu nhập sập. Spearman ρ(thiệt hại LN, lợi suất fwd)=+0,29. **Không sửa V8 theo điều kiện "thu nhập còn giữ"** — điều kiện đó đúng ở chính ca tệ nhất. |
| 3 | `Taylor_20260823_120317` | **Phase 1 ENGINE** V0-V8, spread theo ngày, lãi thật 12,5%, margin-call 40/30%, 6 cổng prereg (`e27e5ec1`), quant-skeptic | **NO-GO, CONFIRMED high** (`verify_20260823_132019`, 7/7 check, recompute độc lập khớp chữ số thứ 4). H1 "spread có thêm thông tin ngoài dd52": KHÔNG — V7<V0 ở cả 3 mức lãi, khác biệt = 1 sự kiện (2016-01-18) làm xấu đi. 3/6 cổng FAIL (G1, G3, G6). V8 trùng V0 tới 0 VND (5/5 sự kiện armed đều T1; 11/2022 dd52 −40,3% KHÔNG sinh washout event ⇒ T3 không tồn tại). 0/27 leg margin call, equity mỏng nhất 87,24% — ràng buộc thật là KHÔNG CÓ EDGE, không phải ký quỹ. |

## Phát hiện phương pháp (mang đi, áp cho MỌI nghiên cứu trên harness này)
1. **Đo NGƯỠNG NHIỄU của harness TRƯỚC khi đặt cổng thống kê.** Cách đo: quét một tham số chỉ được
   phép tác động MỘT CHIỀU (lãi vay chỉ được làm giảm CAGR) và lấy biên độ vi phạm đơn điệu làm sàn nhiễu.
   Đo được: **0,3854pp CAGR** (V3: +0,28pp@10% → +0,66pp@12,5%; truy ra 1 sự kiện 2020-02-03 đảo dấu).
   Hiệu ứng đang đo 0,0086pp ⇒ nhiễu gấp **45×** tín hiệu. Mọi tuyên bố "biến thể X hơn Y +0,08pp" trong
   họ này đều dưới ngưỡng phân giải. Đây là **giới hạn CÔNG CỤ**, KHÔNG phải bằng chứng "hiệu ứng = 0".
2. **Cổng G3 (DSR≥0,95 trên chuỗi excess) tự đặt ra là SAI CHỖ**: FAIL cho TẤT CẢ kể cả V0 đang LIVE ⇒
   không phân biệt được gì. DSR trên chuỗi của chính leg ~1,0 cho mọi leg kể cả control — cũng không
   phân biệt. (Taylor tự đính chính trong finding.)
3. **Đo spread theo NGÀY, không theo THÁNG** — cuối tháng chỉ số đã hồi ⇒ spread tháng âm trong khi
   25 phiên giữa tháng spread dương thật.
4. **Percentile PIT expanding ≠ percentile full-sample**: bản đầu đẹp là look-ahead; bản PIT arm lúc
   spread vẫn âm tuyệt đối (2011-16). Chỉ dùng mốc tuyệt đối neo lãi suất.
5. **Phase 0 KHÔNG bị bác bỏ**: bằng chứng cấp cổ phiếu (net12 +30,2pp) không chết vì sai — nó không
   truyền lên cấp danh mục vì kênh CAPIT quá nhỏ (đòn bẩy chỉ nhân 0,272 NAV-book, trên 1/2 book).
   Đây là giới hạn NĂNG LỰC TRUYỀN DẪN của kênh — hướng còn mở duy nhất là cấp CỔ PHIẾU (xem dưới).

## Đã wire (DISPLAY-ONLY, không sizing/gate)
`dna_report.build_margin_spread_line()` → EOD report: EY_med(universe_pit) − lãi vay thật (đọc
`trading_rules.json`, không hardcode). Commit WorkingClaude `5028becb` + mike `e1c0416f`. Test thật
2026-08-23: 9,24% − 12,5% = **−3,26pp** (không có tín hiệu hiện tại). Mục đích: tích luỹ PIT thật cho
episode kế tiếp (chuỗi deposit hiện tại neo hồi tố 2026-06-19, không PIT).

## Mắt xích yếu còn mang theo (không sửa được bằng backtest thêm)
(a) `deposit_rate_vn` 26 mốc neo hồi tố cùng lúc ⇒ không PIT thật; (b) lãi margin LỊCH SỬ là giả định
deposit+5pp (nay chỉ số HIỆN TẠI 12,5% là thật); (c) thiên lệch sống sót: mã huỷ niêm yết bị xoá khỏi
`tav2_bq.ticker` (0 dòng FLC) ⇒ số cấp cổ phiếu là CẬN TRÊN; (d) harness chỉ từ 2014 ⇒ 3/9 episode
có bằng chứng engine-tier.

## Hướng còn mở — KHÔNG phải "nghiên cứu lại margin theo giai đoạn thị trường"
User gợi ý 2026-08-23 20:46: margin đi vào **từng lựa chọn cổ phiếu** (kiểu TV1 hiện tại, HPG/DGC dưới
book 11/2022) thay vì chọn giai đoạn thị trường. Khớp phát hiện #5 (edge ở cấp cổ phiếu không truyền
lên danh mục). Nếu mở: ràng buộc cứng phải có trước — (1) mã phải nằm trong danh sách margin DNSE
(TV1/UPCOM nhiều khả năng KHÔNG); (2) universe kiểm phải là TOÀN BỘ mã PB<1 trong episode (kể cả
FLC/NVL/HPX không bật lại), không phải các mã nhớ được; (3) gắn vào sleeve fear-buy discretionary đã có
(QUALIFY + fundamental-skeptic CONFIRMED) — không tạo đường margin thứ hai.

## Artifact
- Plan prereg: `agents/Taylor/plan_margin_valuation_spread_20260823.md`
- Phase 0: `agents/Taylor/research/margin_valuation_spread_20260823/`
- Nov-2022: `agents/Taylor/research/extreme_bottom_recognition_20260823/`
- Mechanism: `agents/Taylor/research/extreme_bottom_mechanism_classifier_20260823/` (prereg `538b4df4`, kết quả `0ab449e8`)
- Phase 1: `agents/Taylor/research/margin_valuation_spread_phase1_20260823/` (prereg `e27e5ec1`, kết quả `bd834070`, verify `95af3268`)
- Bus: `margin-valuation-spread-phase0` · `extreme-bottom-recognition-nov2022` · `extreme-bottom-mechanism-classifier-20260823` · `margin-valuation-spread-phase1` · `margin-package-1840-maintenance-ratio` · `dividend-cash-vs-stock-distinction`
- Liên quan đã đóng trước: `v2.5-leverage-nogo.md` (lever theo regime), `wc-deposit-rate-gate.md` (deposit trend de-risk)

## Đính chính 2026-08-24 — thiếu trục "phòng thủ có mục tiêu" vs "cơ cấu tự cộng dồn"
> User phản biện trực tiếp (kèm số liệu CPI/lãi suất liên ngân hàng 10/2010 thật, nguồn Vietstock/
> Tiền Phong): bộ phân loại 2 nhánh (LIQUIDITY_POLICY / FUNDAMENTAL_REAL) của vòng mechanism-classifier
> **thô quá** — không phân biệt được khủng hoảng NHÂN TẠO do cú sốc niềm tin (chính sách phòng thủ có
> MỤC TIÊU cụ thể, xử lý nhanh vì gốc rễ không phải kinh tế thật) với khủng hoảng THẬT do cung tiền/
> tín dụng dư thừa dẫn tới lạm phát cao (cơ cấu, TỰ CỘNG DỒN, không xử lý nhanh được — phải mất nhiều
> NĂM để kéo cung tiền/lạm phát về lại mức bền vững).

**Trục thứ hai cần thêm — 2 câu hỏi, không phải 1:**
1. Gốc rễ có phải cung tiền/tín dụng THẬT SỰ dư thừa trong nước (lạm phát cầu-kéo tự thân) hay là
   một cú sốc niềm tin/thanh khoản riêng lẻ (bank-run, bắt giữ, dòng vốn ngoại rút, dịch bệnh)?
2. NẾU là cú sốc niềm tin — bản thân cú sốc đó có tự giải quyết được trong vài tháng bằng MỘT hành
   động chính sách có mục tiêu (bơm thanh khoản 1 ngân hàng, ổn định tỷ giá), hay nó gắn với một xu
   hướng bên ngoài kéo dài (chu kỳ Fed thắt chặt, chiến tranh thương mại) không do VN kiểm soát được?

**Xếp lại 7 episode theo 2 trục này** (dùng đúng dữ kiện A đã có trong finding gốc + số liệu user bổ
sung cho 10/2010 — KHÔNG chạy lại backtest, đây là đọc lại định tính):

| Episode (arm→đáy) | Trục 1: gốc rễ | Trục 2 (nếu niềm tin): trigger tự giải quyết? | Đọc lại | fwd12 median mã |
|---|---|---|---|---|
| 2007-04→2009-02-24 | **CƠ CẤU** — tín dụng 2007 tăng ~54%, bong bóng CK/BĐS, CPI 2008 ~23% | — | Sóng ĐẦU của khủng hoảng cơ cấu 2007-2012 (dưới). +130% đến từ ĐÁY TOÀN CẦU (GFC bottom 03/2009, thanh khoản Fed/G20), KHÔNG phải VN tự xử lý xong — lạm phát VN vẫn tái phát 2010-2011 | +130,0% (nhiễu bởi hồi phục toàn cầu) |
| 2009-11→2010-08-25 | **CƠ CẤU** (tiếp nối) — CPI 10/2010 +1,05% MoM (cao nhất nhiều năm cho tháng 10), luỹ kế 11T 9,58%→cả năm 11,75% (vượt mục tiêu <10%), liên NH qua đêm 7,3%/kỳ hạn 3T+ 11-11,56%. Vietstock gọi đây là **"bước đệm"** trước khi NHNN bỏ hẳn nới lỏng, thắt chặt toàn diện cuối 2010 + cả 2011 | — | Sóng GIỮA — khủng hoảng ĐANG SÂU THÊM tại thời điểm đo, chưa gần đáy thật (đáy cơ cấu thật rơi vào 2012, không phải 08/2010). fwd12 âm vì đo QUÁ SỚM trong một chu kỳ multi-year, không phải vì "thanh khoản/chính sách không mean-revert" | **−46,8%** ("phản ví dụ" cũ — nay đọc lại: KHÔNG mâu thuẫn giả thuyết, chỉ là đo sai điểm trong 1 chu kỳ dài |
| 2011-05→2012-01-06 | **CƠ CẤU** (đỉnh điểm) — NQ11 24/02/2011 siết tín dụng <20%, lãi vay 20-25%, BĐS đóng băng → nợ xấu 2012 | — | Sóng CUỐI — gần điểm cơ cấu thật sự bắt đầu được xử lý (SBV đã siết đủ lâu, phần tệ nhất bắt đầu phản ánh vào giá). KHÔNG độc lập với 2 dòng trên — cùng MỘT khủng hoảng 2007-2012, đo ở giai đoạn gần cuối hơn | +21,2% (khiêm tốn — hợp lý cho "đang xử lý dở", không phải "đã xong") |
| 2012-08→2012-11-02 | **HỖN HỢP** — trigger là niềm tin (bắt Nguyễn Đức Kiên, bank-run ACB, SBV bơm 17.000 tỷ) nhưng xảy ra giữa dư chấn cơ cấu 2010-2011 (nợ xấu vẫn đang lộ ra, ROE −45%) | **TỰ GIẢI QUYẾT** — SBV can thiệp trực tiếp ACB, dập tắt bank-run trong vài tuần | Trigger niềm tin containable ĐÈ lên nền cơ cấu còn yếu — giải thích hồi phục vừa phải, không bùng nổ | +26,3% |
| 2018-05→2019-01-03 | **KHÔNG cơ cấu trong nước** — dòng vốn ngoại rút khỏi EM, margin call sau nhịp +48%/+22%, chiến tranh thương mại, Fed thắt chặt | **KHÔNG tự giải quyết nhanh** — Fed tiếp tục thắt chặt hết 2018, chiến tranh thương mại kéo dài suốt 2019, VN không kiểm soát được | Cú sốc niềm tin/kỹ thuật nhưng TRIGGER BÊN NGOÀI không tắt nhanh — giải thích vì sao gần như KHÔNG hồi dù không phải khủng hoảng cơ cấu trong nước | +0,8% (gần như đi ngang, không phải phản ví dụ — trục 2 giải thích được) |
| 2020-03→2020-03-24 | **KHÔNG cơ cấu** — VN vào 2020 với lạm phát thấp, vĩ mô lành mạnh; cú sốc là đại dịch | **TỰ GIẢI QUYẾT nhanh** — chính sách tiền tệ+tài khoá phối hợp toàn cầu, cắt lãi suất, không có mất cân đối nội tại cần sửa | Mẫu hình chuẩn — không cơ cấu, trigger containable | +96,7% |
| 2022-05→2022-11-15 | **KHÔNG cơ cấu** (đúng như user chỉ ra) — CPI 2022 VN vẫn trong mục tiêu (~3-4%), thắt chặt là PHÒNG THỦ tỷ giá + chặn lây lan SCB/Vạn Thịnh Phát, không phải chống lạm phát cầu-kéo thật | **TỰ GIẢI QUYẾT** — SBV/nhà nước can thiệp trực tiếp SCB, siết quy tắc trái phiếu có mục tiêu, không lan thành khủng hoảng cung tiền | Mẫu hình chuẩn thứ hai — đúng lý do fwd12 mạnh dù thiệt hại thu nhập đo được lúc đó nặng nhất (thiệt hại là TẠM THỜI do đứt thanh khoản, không phải năng lực kiếm tiền thật bị phá) | +42,4% |

**Hệ quả quan trọng nhất — N thật còn mỏng hơn Taylor đã tính:**
3 dòng đầu (2007-2009, 2009-2010, 2011-2012) rất có thể là **3 SÓNG của MỘT khủng hoảng cơ cấu duy
nhất kéo dài 2007→2012**, không phải 3 episode độc lập. Nếu đúng, N độc lập thật của toàn bộ tập dữ
liệu chỉ còn khoảng **4-5** (1 khủng hoảng cơ cấu dài + 2012-ACB + 2018-19 + 2020 + 2022), không phải
7 — làm mọi phép thống kê đã chạy hôm qua (vốn đã yếu vì N nhỏ) yếu thêm nữa. Đây KHÔNG đổi verdict
NO-GO của Phase 1 (verdict đó dựa trên giới hạn công cụ — nhiễu harness gấp 45× tín hiệu — độc lập
với cách đếm N), nhưng đổi cách đọc episode 2010-08-25: nó không phải bằng chứng phản bác cơ chế
"khủng hoảng niềm tin containable thì an toàn hơn" — nó chỉ là bằng chứng **đo sai thời điểm trong
một chu kỳ cơ cấu dài**, hoàn toàn nhất quán với — chứ không mâu thuẫn — khung 2 trục ở trên.

**Việc cần làm nếu muốn kiểm lại đúng (KHÔNG làm ngay, ngày mai capit_margin_lever go-live lần đầu,
đây là candidate cho vòng nghiên cứu SAU, có prereg riêng nếu user muốn mở lại):**
1. Gộp episode theo CỤM KHỦNG HOẢNG LIÊN TỤC (không theo từng lần dd52 chạm ngưỡng riêng lẻ) — dùng
   tiêu chí khách quan (vd khoảng cách giữa 2 lần dd52≤−20% liên tiếp <18 tháng VÀ CPI/lãi suất chính
   sách vẫn đang xấu đi giữa 2 lần đó ⇒ tính là 1 cụm).
2. Đo forward-return từ ĐIỂM CƠ CẤU THẬT SỰ BẮT ĐẦU ĐƯỢC XỬ LÝ (vd đỉnh CPI/đỉnh lãi suất chính sách),
   không phải từ lần dd52 chạm ngưỡng đầu tiên trong cụm — đúng bài học "đo quá sớm trong chu kỳ dài".
3. Trục 2 (trigger tự giải quyết hay không) cần một biến số PIT khách quan, không phải phán đoán hồi
   tố — ứng viên: có phải chính sách phản ứng NHẮM VÀO một sự kiện/tổ chức cụ thể (bank run, 1 doanh
   nghiệp) hay là phản ứng với chỉ số vĩ mô TỔNG HỢP (CPI, cung tiền) — phân biệt được PIT bằng cách
   đọc văn bản chính sách/tuyên bố NHNN lúc đó, không cần biết trước kết quả.
