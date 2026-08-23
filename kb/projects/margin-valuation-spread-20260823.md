# Margin theo khoảng cách định giá + nhận diện đáy cực rẻ (11/2022)
> Dự án ĐÓNG 2026-08-23 (1 ngày, 5 vòng nghiên cứu liên tiếp trên cùng tập 7 episode dd52≤−20%).
> Status: **NO-GO cho mọi cơ chế sizing/gate mới. `capit_margin_lever` (dd52≤−20%, f=1,3, CAPIT-only,
> SpaceX) GIỮ NGUYÊN, live từ 2026-08-24.** Sau ngày này KHÔNG mở thêm biến thể nào trên cùng tập
> episode — bằng chứng mới chỉ đến từ thời gian thật (shadow-log spread trong EOD report).

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
