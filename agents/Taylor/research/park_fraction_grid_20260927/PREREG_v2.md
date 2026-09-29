# PREREG v2 — chọn MỘT mức park fraction custom30V (NEUTRAL) trên plateau

**Viết TRƯỚC khi chạy/đọc bất kỳ số nào của vòng 2.** Job `Taylor_20260927_074727`.
Paper-only. **`trading_rules.json` KHÔNG đổi** (vẫn 0.8). Engine **KHÔNG chạy lại** — chỉ
tái dùng 12 CSV leg đã sinh ở vòng 1 (job `Taylor_20260927_064747`, cây `main@f2cfb124`).

## 0. Vì sao có vòng 2
quant-skeptic (`quant-skeptic_20260927_072455`) **REFUTED** tuyên bố "đỉnh nội thật 30%".
Phần ĐỨNG VỮNG sau phản biện, giữ nguyên làm tiền đề vòng 2:
- Mọi mức **≥40% FAIL ràng buộc DD** (5th-pct MaxDD bootstrap kém hơn mức 0% quá 2,0pp).
- **80% (LIVE) bị 30% áp đảo trên 81% đường bootstrap**, và không thắng năm nào.
- **Plateau 0–30% PHẲNG theo Calmar**: P(30>0)=0,47 · P(argmax=30)=0,14 · P(argmax=0)=0,38.
⇒ Câu hỏi vòng 2 KHÔNG còn là "đỉnh ở đâu" (dữ liệu không phân biệt được) mà là
**"chọn mức nào trên plateau, theo quy tắc nào khai báo trước"**.

## 1. Tiêu chí chọn — khai báo TRƯỚC, một tiêu chí duy nhất
**Chọn x tối đa hoá KỲ VỌNG Calmar dưới paired block bootstrap — `E[Calmar_x]` —
KHÔNG phải Calmar của một đường lịch sử duy nhất.**
Lý do chọn kỳ vọng thay vì giá trị lịch sử: Calmar lịch sử là 1 điểm rút từ phân phối rất
rộng (vòng 1: MaxDD lịch sử −14,4% vs 5th-pct −25,1% ở cùng mức 30%), argmax của nó gần như
là nhiễu — đó chính là lỗi vòng 1 mà skeptic bắt được.

**Ràng buộc DD giữ NGUYÊN như PREREG v1** (không nới để cứu mức nào):
`5th-pct MaxDD_x ≥ 5th-pct MaxDD_{x=0} − 2,0pp`. Mức không qua ⇒ LOẠI, không xét tiếp.

## 2. Tie-break — khai báo TRƯỚC (đây là điểm PREREG v1 nói Sharpe, v2 đổi có chủ ý)
PREREG v1 tie-break bằng **Sharpe**. PREREG v2 tie-break bằng **mức THẤP HƠN**:
> Trong tập mức qua cổng DD, nếu `|E[Calmar_x] − E[Calmar_best]| < 0,03` thì chọn **x NHỎ NHẤT**
> trong nhóm đó.

**Chọn "mức thấp hơn" chứ KHÔNG chọn Sharpe, và nói rõ trước khi đọc số.** Ba lý do:
(a) tie-break phải là một nguyên tắc ngoài dữ liệu, không phải metric thứ hai cũng rút từ cùng
mẫu — thêm metric = thêm một lần dò; (b) park fraction thấp hơn = ít cơ khí hơn, ít phụ thuộc
thanh khoản ETF/custom30V hơn, ít hành động hơn khi hệ sai; (c) hướng thận trọng trùng với
bản chất "chốt rủi ro, không phải công cụ tăng lợi nhuận".
Ngưỡng 0,03 Calmar giữ nguyên con số PREREG v1 đã khai báo (không tinh chỉnh lại).

**Hệ quả đã biết trước và chấp nhận:** nếu 0% và 30% không phân biệt được thống kê thì luật
này trả về **0%**, tức "bỏ parking". Khai báo trước để không ai đổi luật sau khi thấy số.

## 3. Sáu phân tích sẽ chạy (cố định, không thêm bớt sau khi đọc kết quả)
1. **Paired block bootstrap** — CÙNG chuỗi block index áp cho cả 12 leg (L=21, B=4000,
   seed 12345), quy ước lịch = `bootstrap_nav.py` (calendar years). Bảng cho 12 mức:
   `P(argmax Calmar = x)`, `P(Calmar_x > Calmar_0)`, `E[Calmar_x]`, `E[MaxDD_x]`,
   `5th-pct MaxDD_x`, `E[CAGR_x]`. Paired = so sánh cùng thế giới, không phải 12 bootstrap độc lập.
2. **Episode-aware leave-out**: bỏ {2019+2020}, bỏ {2018}, bỏ {2018-2020}, bỏ {2022} —
   xếp hạng Calmar mỗi ca.
3. **Độ nhạy ngưỡng DD** 1,5 / 2,0 / 3,0pp — tập mức qua cổng có đổi không (40% fail 2,0pp
   chỉ 0,4pp, nên phải kiểm).
4. **Minimax regret CAGR** trên 0–30%: mức nào thua mức tốt nhất ít nhất trong tình huống xấu
   (bootstrap 5th-pct CAGR).
5. **Kết luận MỘT SỐ** theo §1+§2, kèm câu "plateau 0–30%, chọn X vì …", và **nói thẳng** nếu
   kết luận do tie-break quyết chứ không phải dữ liệu.
6. Sửa chữ registry mục park-fraction: "ĐỈNH NỘI THẬT/ROBUST" → "plateau 0-30%, ≥40% bị loại"
   (giữ nguyên mọi con số).

## 4. Cái này KHÔNG chứng minh được
Không kết luận mức nào "tốt hơn" theo nghĩa thống kê trên plateau — plateau phẳng là chính
kết quả. Bootstrap chỉ là bất định LẤY MẪU trên phân phối lịch sử, không mô hình hoá vỡ chế độ.
Không đổi production trong job này.
