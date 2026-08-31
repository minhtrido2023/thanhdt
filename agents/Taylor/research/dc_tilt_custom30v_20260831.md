# DC-tilt trong custom30V parking — NO-GO bằng suy luận (không backtest)

Job `Taylor_20260831_014243` (dispatch Mike, user duyệt 2026-08-31 08:41 ICT, decided_by user).
Giả thuyết được giao: overweight (trong cap 0,10 hiện có) những mã trong custom30V (30 mã, yieldcombo
1/PE+1/PCF, parking NEUTRAL) mà ĐỒNG THỜI nằm trong 16-mã universe DC và double-confirm đang fire;
underweight phần còn lại, giữ tổng weight.

**Đúng theo chỉ đạo bước 2 của dispatch: đọc lại bảng gross-by-state TRƯỚC khi chạm dữ liệu, kết
luận NO-GO ngay bằng suy luận, không backtest.**

## Bằng chứng — bảng gross-by-state đã có sẵn (2 job trước, quant-skeptic CONFIRMED cả 2)

`dc_3book_factor_neutral_20260830.md` (job `Taylor_20260830_153823`, quant-skeptic CONFIRMED medium),
phân rã `bal_ret`/`lag_ret`/`dc_ret`/`baseline_ret` theo state, FULL 2014-08→2026-06:

| State | N | bal_ann | lag_ann | **dc_ann** | baseline_ann |
|---|---:|---:|---:|---:|---:|
| CRISIS | 443 | 3,48% | 10,40% | 7,48% | 6,48% |
| BEAR | 241 | 0,64% | 1,07% | **−16,82%** | −0,13% |
| **NEUTRAL** | **1.804** | **28,98%** | **29,25%** | **22,83%** | **29,71%** |
| BULL | 422 | 54,54% | 34,41% | 64,12% | 42,34% |
| EXBULL | 60 | 39,13% | 69,47% | 57,92% | 57,22% |

**custom30V parking chỉ active ở đúng state mà DC yếu nhất trong 3 state "bình thường" (loại BEAR
vì đó là sụp hẳn):** ở NEUTRAL, `dc_ann` (22,83%) THẤP HƠN cả `bal_ann` (28,98%), `lag_ann` (29,25%)
VÀ `baseline_ann` (29,71%) — DC không chỉ "không có edge", mà còn **kéo tụt** nếu trộn vào so với
để nguyên. File 08-30 đã ghi rõ nguyên văn: *"Ở NEUTRAL, ... DC không có edge trong NEUTRAL, chỉ có
edge trong BULL/CRISIS."* Job `dc_state_gated_bull_only_20260830.md` (quant-skeptic CONFIRMED lần 2,
sau khi tự sửa N=10→N=6 vì cluster COVID chiếm 85% edge) xác nhận thêm: toàn bộ giá trị DC tìm được
chỉ đứng vững ở BULL/EXBULL, và ngay cả ở đó bằng chứng cũng mỏng + tập trung 1 cụm lịch sử — kiến
trúc state-gated (chỉ active NGOÀI NEUTRAL) là khuyến nghị cuối cùng của 2 job đó, không phải "gate
theo tên bên trong NEUTRAL".

## Vì sao suy luận này áp được cho đúng giả thuyết custom30V-tilt (không phải đánh tráo câu hỏi)

Giả thuyết dispatch hỏi: "trong custom30V (parking NEUTRAL), tilt theo DC-fire có thêm giá trị
không?" Bảng trên đo ở mức BOOK (16 mã DC, cap 20%/tên, có gate) so với BAL/LAG/baseline — khác
universe (30 mã custom30V yieldcombo vs 16 mã DC) và khác cơ chế (tilt trong-universe vs book riêng).
Nhưng cùng một cơ chế nguyên nhân áp dụng cho cả hai: bản chất double-confirm gate (sector-lens BUY
∩ 8L rating≤2) là bộ lọc GIÁ TRỊ/CHẤT LƯỢNG tại một THỜI ĐIỂM, **không có override macro/state cho
chính nó** — 2 job trước đã chỉ ra alpha của nó chỉ biểu hiện rõ khi thị trường đang có xu hướng
mạnh (BULL/EXBULL momentum khuếch đại chất lượng đã chọn đúng) hoặc đáy sâu (CRISIS mean-reversion).
NEUTRAL là chế độ "đi ngang, không có xu hướng khuếch đại" — đúng chế độ mà 1 bộ lọc giá trị/chất
lượng tĩnh không có gì để cưỡi lên, khớp với con số dc_ann NEUTRAL thấp nhất trong 3 state thường.
Không có lý do cấu trúc nào để 16-mã-universe-DC hoạt động khác khi đặt lồng vào 30-mã-custom30V
thay vì đứng riêng — nếu có khác biệt, nó sẽ là do OVERLAP giữa 2 universe (bao nhiêu trong 16 mã DC
cũng nằm trong custom30V) hẹp đi nên nhiễu hơn, không phải mạnh lên.

## Nhất quán với lịch sử — không phải lần đầu custom30V-tilt bị bác

Đúng như cảnh báo trong dispatch, mọi tilt custom30V trước đều REFUTED/NO-GO: liq-tilt, permanent-
exclude 7 tên (−1,0pp), (30,0.15) bull parking (overfit), accrual-quality gate 3 biến thể (3/3
NO-GO, 08-30). DC-tilt sẽ là ca thứ 5 cùng lớp, và có LÝ DO CƠ CHẾ rõ ràng để dự đoán thất bại
trước khi chạy — không chỉ "khó cải thiện thêm" chung chung.

## Kết luận: NO-GO bằng suy luận — không chạy backtest

Theo đúng chỉ đạo bước 2 của dispatch: bảng gross-by-state cho thấy NEUTRAL là state DC yếu nhất
(dưới baseline lẫn cả 2 book khác), trong khi custom30V parking CHỈ active ở NEUTRAL. Tilt hướng
tới đúng tín hiệu yếu nhất tại đúng state nó active — không có cơ sở kỳ vọng thêm giá trị, nhiều khả
năng giống 5 tilt trước: kéo tụt hoặc lẫn nhiễu không ý nghĩa. Không backtest để tiết kiệm thời gian
— đúng permission dispatch cho phép ("kết luận NO-GO sớm bằng suy luận đúng thay vì chạy số vô ích").

**Không cần quant-skeptic** (điều kiện dispatch: chỉ bắt buộc khi GO). Đề xuất hướng đi tiếp nếu
muốn theo đuổi DC alpha: bám đúng khuyến nghị "giữ mở, chưa action" của job `dc_state_gated_bull_
only_20260830.md` — state-gated BULL/EXBULL overlay, KHÔNG phải tilt trong NEUTRAL parking.

**Không đụng file trading production.** Không có code mới — kết luận rút thẳng từ 2 file research
đã có, đúng cách "đọc trước, đừng chạy số vô ích" dispatch yêu cầu.
