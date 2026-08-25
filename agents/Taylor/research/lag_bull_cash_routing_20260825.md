# Route tiền mặt LAG idle trong BULL → BAL hay parking basket?

**Job**: Taylor_20260825_135818 · **Nguồn**: CSV production
`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-80_wtnamecap_advprice_exp_agg_F1_t80_univpit.csv`
(root `WorkingClaude/`). **Method**: đọc trực tiếp `record_type=DAILY` (state, nav/cash refs) +
`record_type=TX` (đếm lệnh mua/ngày, join theo `ymd`) + `record_type=CUSTOM_BASKET` (giá trị basket
`CUSTOM_VN30EXVIC_PITG` — vehicle parking hiện tại). Kế thừa method từ
`gross_by_state_lag_cash_drag_20260825.md` (job trước, cùng ngày). **Phạm vi: chỉ BULL (state=4),
EX-BULL ngoài phạm vi theo chỉ đạo user.**

## 1. Đo tiềm năng (upper bound, không ràng buộc)

BULL: N=422 phiên, trong đó **330 phiên (78,2%) LAG không có lệnh mua nào** (`lag_buy_today=0`,
đếm từ `TX` book=LAG action=buy). Trên các phiên idle này, LAG ngồi trung bình **62,1% NAV của
chính book LAG** bằng tiền mặt (so với 35,7% trên các phiên có mua).

Tính theo % NAV combined: LAG cash idle trung bình = **28,3% combined NAV** trên các phiên idle
(median 41,3% — lệch phải, vài giai đoạn LAG gần như toàn cash).

**Upper bound tuyệt đối** (giả định 100% cash idle này được deploy hết, gross_lag→~1.0 trên các
phiên idle, không ràng buộc thanh khoản/concentration nào): gross_combined BULL tăng từ hiện tại
**0,701** (trung bình theo ngày, không trọng số NAV — khác cách tính pooled-by-NAV của job trước
nên số tuyệt đối lệch, nhưng chiều và độ lớn khớp) lên **0,923** — tức **+22,1pp**. Đây là **trần
lý thuyết, không phải mục tiêu khả thi** — mọi route thực tế đều bị chặn bởi capacity/concentration
dưới đây.

## 2. Hướng A — Route sang BAL: KHÔNG khả thi ở dạng đơn giản

- BAL trong BULL đã gross **0,911** (chỉ 8,9% NAV BAL là cash) — book gần như đã deploy hết theo
  đúng tín hiệu momentum của nó. Đây **không phải capacity dư sẵn có** để "rót thêm tiền vào" —
  `cap_bal`/`cap_lag` trong CSV là NAV mục tiêu của allocator (`combined_nav = cap_bal + cap_lag`,
  xác nhận từ `pt_v23_audit_2014.py:2403`), không phải trần thanh khoản.
- **Nút thắt thật**: `MAX_POS_V11 = 12` (`pt_v23_audit_2014.py:688`) — BAL chỉ giữ tối đa 12 vị
  thế. Route thêm ~140 tỷ VND (trung bình idle-cash mỗi phiên idle) vào BAL nghĩa là **tăng size
  bình quân mỗi vị thế +66%** (17,6 tỷ → 29,3 tỷ/vị thế, giả định 12 tên đang có), KHÔNG phải mua
  thêm tên mới (BAL không có tên mới đạt ngưỡng momentum để mua thêm — nếu có, nó đã tự mua qua
  cơ chế hiện tại).
- Hệ quả: ép w_bal_tgt tăng trong BULL-idle-LAG sẽ (a) vi phạm tinh thần `wtnamecap` (trần tỷ
  trọng/tên), (b) đẩy concentration + ADV risk lên đúng 12 tên đang giữ, (c) làm BAL không còn là
  "chọn theo tín hiệu" mà thành "bồn chứa cash cưỡng bức" — thay đổi bản chất book.
- **Kết luận A: LOẠI**, trừ khi đi kèm nới `MAX_POS_V11` (mở rộng số tên BAL được giữ) — đó là
  thay đổi kiến trúc lớn hơn hẳn phạm vi "route cash", cần nghiên cứu riêng (ảnh hưởng tới chính
  chất lượng tín hiệu momentum_V11 khi pha loãng xuống tên yếu hơn trong ranking).

## 3. Hướng B — Route sang parking basket (custom30V): khả thi về cơ chế, có tín hiệu ủng hộ

- **Cơ chế đã có sẵn, chỉ chưa bật cho BULL.** `PARK_STATES_DICT` (config production hiện tại
  `{3: 0.80}`) là dict `{state: frac}` — thêm entry `4: x` là thay đổi 1 dòng config, không phải
  xây cơ chế mới (`pt_v23_audit_2014.py:1523,1750`: `base.get(st, 0.0)` — state không có trong
  dict = mặc định **0** parking, đúng là hiện trạng BULL bây giờ).
- **Capacity tốt hơn BAL nhiều**: custom30V là rổ **30 mã, cap 0,10/mã** (theo KB) — pha loãng tự
  nhiên, không dồn vào 12 vị thế như BAL. Route ~140 tỷ VND vào rổ 30 mã tăng size bình quân mỗi
  mã ít hơn nhiều lần so với route vào BAL.
- **Bằng chứng return ủng hộ hướng này** (đo trực tiếp từ `CUSTOM_BASKET` value, ticker
  `CUSTOM_VN30EXVIC_PITG`, N=422 phiên BULL):
  - Basket return trung bình phiên BULL: **+0,238%/ngày (≈+59,9%/năm hoá thô)**, cao hơn hẳn VNI
    cùng giai đoạn (+0,104%/ngày ≈ +26,3%/năm) và cao hơn cả chính basket trong NEUTRAL
    (+0,130%/ngày ≈ +32,6%/năm, N=1895).
  - Trên đúng các phiên LAG idle (nơi cash đang nằm không): basket ret **+0,267%/ngày
    (≈+67%/năm)**, còn cao hơn cả trung bình BULL — tức nếu route cash idle vào parking đúng lúc
    này, lịch sử cho thấy basket không hề yếu đi khi LAG cạn tín hiệu.
  - Đây là bằng chứng **directional mạnh**, không phải kết luận đã kiểm định đầy đủ (basket return
    ở đây là RAW, chưa trừ TC route-in/route-out, và có thể phần lớn là **beta thị trường** (rổ
    30 mã VN30exVIC vẫn là cổ phiếu, hưởng lợi trực tiếp khi VNI tăng) chứ chưa chắc alpha ròng —
    không tách được 2 phần này chỉ từ CSV này.
- **Câu hỏi chưa trả lời (đúng như dispatch nêu)**: rổ NEUTRAL parking (`custom30V` cap 0,10) đã
  tối ưu CHO NEUTRAL — chưa có bằng chứng nó là lựa chọn tối ưu cho BULL cụ thể (có thể cửa sổ
  rebalance, chọn mã, hay tỷ trọng cap khác sẽ tốt hơn trong regime này). Cần backtest thật, không
  suy diễn từ raw basket return.
- **Kết luận B: hướng promising nhất, cần backtest xác nhận trước khi wire.**

## 4. Hướng C — Không làm gì: bằng chứng YẾU, không đủ mạnh để kết luận

Kiểm định "LAG idle cash trùng đúng lúc forward return thấp hơn → cash discipline là tín hiệu
đúng, không phải bỏ lỡ cơ hội":

- **Ở mức phiên (daily, N=330 idle vs N=92 active, pseudo-replicated vì các phiên liền kề tương
  quan cao)**: fwd 20 phiên VNI return trung bình idle=1,42% vs active=3,62%, Welch t=−3,21 (có vẻ
  "significant" nếu tính ngây thơ).
- **Ở mức episode độc lập** (gộp các chuỗi ngày liên tục cùng flag thành 1 sự kiện — đúng chuẩn
  "N là số sự kiện độc lập, không phải số dòng" theo skill quant-research): chỉ có **N=19 episode
  idle vs N=18 episode active** trong toàn bộ lịch sử 2014→nay. Trung bình fwd20 idle=3,17% vs
  active=4,99%, nhưng Welch t=−1,07 (df=34,9) — **KHÔNG significant** (|t|<2).
- Chiều dấu vẫn nghiêng ủng hộ "cash discipline không tệ" (idle thấp hơn active, đúng hướng lo
  ngại thấp), nhưng N=19 episode là quá nhỏ và các episode tập trung vào vài giai đoạn bull lịch
  sử (2017-18, 2020-21, 2024-2026 — không độc lập hoàn toàn về mặt regime vĩ mô) để kết luận chắc
  chắn theo hướng nào.
- **Kết luận C: không có bằng chứng đủ mạnh để khẳng định cash idle là "tín hiệu đúng" — nhưng
  cũng không có bằng chứng nó sai.** Đây là INCONCLUSIVE, không phải NO-GO cho B/A.

## 5. Khuyến nghị

**Ưu tiên Hướng B (parking route sang custom30V), loại Hướng A, không kết luận dứt khoát cho C.**

Lý do chọn B trên A: cơ chế đã có sẵn (`PARK_STATES_DICT`), capacity tốt hơn hẳn (30 mã cap 0,10
vs BAL 12 vị thế), và basket return lịch sử trong BULL (+60%/năm thô, kể cả trên đúng các phiên
LAG idle) mạnh hơn nhiều so với việc ép BAL nhận thêm size trên 12 tên đã đầy.

**Đề xuất backtest cụ thể (không tự chạy, báo Mike quyết định)**:
- Config: `ETF_PARK` / `PARK_STATES_DICT = {3: 0.80, 4: X}` với X thử **{0.3, 0.5, 0.65}** (thấp
  hơn NEUTRAL vì BULL vốn LAG đã ít cash hơn NEUTRAL nên không cần trần cao bằng).
- Output **KHÔNG ghi đè CSV canonical** — dùng suffix mới (vd. `_park3-80-4-XX`) theo §8 coding
  guidelines.
- So sánh CAGR/Sharpe/DD/Calmar walk-forward IS(2014-19)/OOS(2020+) vs baseline park3-80 hiện tại,
  cộng self-check 0 VND.
- Nếu promising: bắt buộc qua quant-skeptic (look-ahead trong logic parking JIT sell/buy khi state
  đổi, capacity/ADV thật của 30 mã khi cần deploy đột ngột) trước khi đề xuất wire production.

**Không đề xuất Hướng A tiếp tục nghiên cứu** trừ khi user muốn mở rộng phạm vi sang đổi
`MAX_POS_V11` (thay đổi kiến trúc BAL, ngoài phạm vi "route cash").
