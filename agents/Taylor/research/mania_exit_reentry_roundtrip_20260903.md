# Mania exit → re-entry: round-trip backtest ("cơ chế rút có bảo toàn vốn thật không?")

> Job `Taylor_20260903_170018` (follow-up thứ 5, tiếp `Taylor_20260903_154921`). **RESEARCH-ONLY,
> không wire.** Đọc trước: `mania_deep_dive_2006_2007_and_cracking_20260903.md` §2 (DIVERGE_DAY),
> §2.5 (base rate), §3 (kết luận "cảnh giác, không timing"); `top_detection_technical_signals_20260903.md`
> (RSI_DIVERGE_3M — chỉ báo bắt-đỉnh tốt nhất đã thử, vẫn không có nội dung timing).

**Bối cảnh đổi khung**: user đọc 4 vòng trước và đặt lại câu hỏi — "cơ chế này vẫn hiệu quả trong
bảo toàn vốn dù không đo được rớt bao nhiêu; đo BAO LÂU THÌ THỊ TRƯỜNG ỔN ĐỂ VÀO." Dispatch yêu cầu
**kiểm chứng trước khi tin**: mệnh đề "bảo toàn vốn" chưa hề được đo trực tiếp — §3 trước chỉ đo độ
trễ/biên độ điều chỉnh SAU tín hiệu, không đo NAV round-trip so với mua-giữ.

**Trả lời ngắn (§5 đầy đủ): mệnh đề "bảo toàn vốn" KHÔNG được xác nhận.** Round-trip NAV (rút theo
tín hiệu, vào lại theo 1 trong 6 rule) **không vượt được kiểm soát "rút vào ngày ngẫu nhiên cùng tần
suất" trong 8/12 tổ hợp**, và **không vượt mua-và-giữ về Sharpe/Calmar ở bất kỳ tổ hợp nào một cách
nhất quán** — tốt nhất là ngang bằng, phần lớn là kém hơn (đặc biệt với RSI_DIVERGE_3M). Rule tái vào
"tốt nhất" trong benchmark thô (R4_dt5g) gần như KHÔNG hành động (median 1 phiên chờ) nên biên độ
"tốt hơn" của nó phần lớn phản ánh việc gần-như-luôn-ở-trong-thị-trường, không phải một cơ chế timing
thật.

---

## §1. Thiết kế Việc A — round-trip engine, N_TRIALS, PIT

### 1.1 Nguồn dữ liệu — tái dùng, không dựng lại

- Giá + DIVERGE_DAY: `crack/crack_daily.csv` (panel A, 2008-06-02→2026-09-03, 4.558 phiên) — cột
  `vnindex_close`, `diverge_day`, `breadth_pct252` dùng NGUYÊN VĂN từ job trước.
- RSI_DIVERGE_3M(margin=0,02): tái tạo NGUYÊN CÔNG THỨC từ `toptech/analyze_toptech.py` (merge
  `toptech/vnindex_tech.csv` cột `D_RSI`/`D_RSI_Max3M`, `new_high_126 & (D_RSI_Max3M-D_RSI>=0,02)`) —
  không viết lại logic, chỉ tái dùng.
- **Dữ liệu MỚI cho R3/R4** (`roundtrip/capit_dt5g_hist.csv`, BQ, 35MB quét): `tav2_bq.ticker_prune`
  (oversold = %mã D_RSI<0,3; above_ma200 = %mã Close≥MA200) JOIN `tav2_bq.vnindex_5state_dt5g_live`
  (bảng ĐÚNG theo CLAUDE.md §DT5G bẫy nhãn bảng — không phải `vnindex_5state`).
  **Giới hạn dữ liệu phát hiện được**: bảng DT5G chỉ có dữ liệu từ **2014-01-02** (khớp CLAUDE.md
  "warm-up từ 2014"), không phải từ 2008-06 như panel A → **panel B** = 2014-01-02→2026-09-03
  (3.158 phiên). Không mất episode nào của DIVERGE_DAY (episode đầu tiên 2016-09-26, tất cả 13
  episode nằm trong panel B); RSI_DIVERGE_3M mất 9/45 episode trước 2014 (còn 36 trong panel B).
- **13 phiên NaN `vnindex_close`** (2008-06/08/09 + 2009-12-07, rải rác, không trùng episode nào) —
  forward-fill (carry giá đóng cửa gần nhất), ghi rõ trong code, không lặng lẽ vá.

### 1.2 Engine — thực thi T+1 causal (khớp quy ước CLAUDE.md §Backtest)

Vị thế cho phiên `t` quyết định bằng thông tin tới hết phiên `t-1` (không nhìn trước): nếu đang IN
và `exit_flag[t-1]` bật → OUT từ phiên `t`; nếu đang OUT và `reentry_rule(t-1)` thoả → IN từ phiên
`t`. Đổi trạng thái tốn `0,1%` (CLAUDE.md §Backtest, mỗi chiều). OUT hưởng lãi tiền gửi nhàn rỗi
**0%/năm** (đúng quy ước, không phải giả định optimistic). CAGR tính trên **thời gian lịch**
(`365,25/số ngày lịch`), không phải số phiên.

### 1.3 N_TRIALS — khai trước khi xem kết quả

- 2 exit trigger tái dùng (không phải trial mới): DIVERGE_DAY, RSI_DIVERGE_3M(m=0,02) — đã
  pre-registered ở 2 job trước.
- 6 biến thể re-entry (R1 3 điểm K∈{21,63,126} + R2 1 ngưỡng + R3 1 rule + R4 1 rule) × 2 exit
  trigger = **12 tổ hợp MAIN**, trình đủ cả 12, không chọn đẹp.
- Mỗi tổ hợp có 2 control (bootstrap N=200 mỗi control) → không phải trial thêm, là kiểm chứng bắt
  buộc theo dispatch.

---

## §2. Việc A — Round-trip backtest: MAIN vs 3 control

### 2.1 Bảng đầy đủ 12 tổ hợp (MAIN / CTRL2 random-exit / CTRL3 random-reentry) + Buy&Hold

| Exit trigger | Reentry rule | Panel | n_ev | n_trades | | CAGR | maxDD | Sharpe | Calmar | %OUT |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| DIVERGE_DAY | R1_K21 | A | 13 | 30 | **MAIN** | 7,96% | −58,08% | 0,485 | 0,137 | 6,9% |
| | | | | | CTRL2 | 8,02% | −58,09% | 0,486 | 0,138 | 5,7% |
| | | | | | CTRL3 | 7,68% | −58,08% | 0,483 | 0,132 | 14,2% |
| DIVERGE_DAY | R1_K63 | A | 13 | 18 | **MAIN** | 7,74% | −58,08% | 0,481 | 0,133 | 12,4% |
| | | | | | CTRL2 | 7,36% | −58,08% | 0,467 | 0,127 | 15,0% |
| | | | | | CTRL3 | 7,77% | −58,08% | 0,488 | 0,134 | 14,2% |
| DIVERGE_DAY | R1_K126 | A | 13 | 14 | **MAIN** | 6,85% | −58,08% | 0,451 | 0,118 | 19,4% |
| | | | | | CTRL2 | 6,39% | −58,11% | 0,432 | 0,110 | 25,9% |
| | | | | | CTRL3 | 7,78% | −58,08% | 0,489 | 0,134 | 14,4% |
| DIVERGE_DAY | R2_breadth050 | A | 13 | 45 | **MAIN** | 8,67% | −58,08% | 0,528 | 0,149 | 10,9% |
| | | | | | CTRL2 | 8,98% | −58,08% | 0,542 | 0,155 | 10,5% |
| | | | | | CTRL3 | 7,74% | −58,08% | 0,487 | 0,133 | 14,3% |
| DIVERGE_DAY | R3_capit | B | 13 | 14 | **MAIN** | 7,38% | −40,19% | 0,524 | 0,184 | 19,4% |
| | | | | | CTRL2 | 7,54% | −42,25% | 0,537 | 0,183 | 26,8% |
| | | | | | CTRL3 | 9,38% | −37,10% | 0,650 | 0,260 | 20,2% |
| DIVERGE_DAY | R4_dt5g | B | 13 | 102 | **MAIN** | 10,43% | −45,98% | 0,665 | 0,227 | 8,6% |
| | | | | | CTRL2 | 10,65% | −44,61% | 0,669 | 0,240 | 4,8% |
| | | | | | CTRL3 | 9,54% | −37,06% | 0,661 | 0,264 | 20,2% |
| RSI_DIVERGE_3M | R1_K21 | A | 45 | 98 | **MAIN** | 4,06% | −58,08% | 0,310 | 0,070 | 22,6% |
| | | | | | CTRL2 | 6,67% | −58,11% | 0,436 | 0,115 | 17,0% |
| | | | | | CTRL3 | 3,68% | −58,10% | 0,307 | 0,063 | 40,9% |
| RSI_DIVERGE_3M | R1_K63 | A | 45 | 56 | **MAIN** | 2,07% | −58,08% | 0,208 | 0,036 | 38,7% |
| | | | | | CTRL2 | 5,80% | −58,10% | 0,418 | 0,100 | 37,2% |
| | | | | | CTRL3 | 3,77% | −58,10% | 0,313 | 0,065 | 40,9% |
| RSI_DIVERGE_3M | R1_K126 | A | 45 | 39 | **MAIN** | 6,83% | −58,08% | 0,542 | 0,118 | 54,2% |
| | | | | | CTRL2 | 4,31% | −58,09% | 0,353 | 0,074 | 53,3% |
| | | | | | CTRL3 | 3,69% | −58,16% | 0,307 | 0,064 | 40,5% |
| RSI_DIVERGE_3M | R2_breadth050 | A | 45 | 317 | **MAIN** | 6,68% | −58,08% | 0,438 | 0,115 | 17,5% |
| | | | | | CTRL2 | 8,85% | −58,08% | 0,563 | 0,152 | 23,7% |
| | | | | | CTRL3 | 4,11% | −58,10% | 0,334 | 0,071 | 40,9% |
| RSI_DIVERGE_3M | R3_capit | B | 36 | 30 | **MAIN** | 6,37% | −44,70% | 0,518 | 0,142 | 45,5% |
| | | | | | CTRL2 | 5,11% | −39,79% | 0,428 | 0,133 | 47,9% |
| | | | | | CTRL3 | 4,21% | −39,17% | 0,382 | 0,111 | 46,4% |
| RSI_DIVERGE_3M | R4_dt5g | B | 36 | 296 | **MAIN** | 7,99% | −45,02% | 0,540 | 0,177 | 13,6% |
| | | | | | CTRL2 | 10,32% | −43,47% | 0,671 | 0,242 | 9,8% |
| | | | | | CTRL3 | 4,31% | −39,27% | 0,392 | 0,113 | 46,9% |
| **Buy&Hold** | — | A | — | 0 | | **8,56%** | **−58,08%** | **0,504** | **0,147** | 0% |
| **Buy&Hold** | — | B | — | 0 | | **10,70%** | **−45,26%** | **0,655** | **0,236** | 0% |

(CTRL2 = trung bình 200 draw rút ngày NGẪU NHIÊN cùng số episode, cùng reentry rule; CTRL3 = trung
bình 200 draw giữ nguyên exit signal THẬT, chờ tái vào NGẪU NHIÊN Uniform[1,126] phiên.)

### 2.2 Đọc bảng — 3 phát hiện, đúng thứ tự ưu tiên của dispatch

**(a) MAIN không vượt CTRL2 (rút ngẫu nhiên cùng tần suất) trong 8/12 tổ hợp (67%).** Đây là phép
thử quan trọng nhất: nó hỏi "biết THỜI ĐIỂM rút bằng tín hiệu có hơn rút mù cùng tần suất không?"
Với DIVERGE_DAY: thắng 2/6 (R1_K63, R1_K126), thua 4/6. Với RSI_DIVERGE_3M: thắng 2/6 (R1_K126,
R3_capit), thua 4/6, có 2 ca thua nặng (R1_K21 4,06% vs 6,67%; R1_K63 2,07% vs 5,80% — tín hiệu THẬT
tệ hơn ngẫu nhiên rõ rệt). **Kết luận: nội dung "biết khi nào rút" của cả 2 tín hiệu, đo trên NAV
round-trip thật, không phân biệt được có ý nghĩa với việc rút mù cùng tần suất.**

**(b) maxDD gần như KHÔNG cải thiện trên panel A** (−58,08% giống hệt buy-hold ở 4/6 tổ hợp
DIVERGE, tất cả 4/6 tổ hợp RSI đầu) — vì **drawdown lớn nhất mẫu (khủng hoảng 2008, panel A bắt đầu
giữa khủng hoảng) xảy ra TRƯỚC KHI DIVERGE_DAY từng fire lần đầu (2016-09-26)** — không có tín hiệu
nào tồn tại để tránh nó. Đây là giới hạn dữ liệu, không phải bằng chứng chỉ báo tệ, nhưng **cũng có
nghĩa "bảo toàn vốn" ở panel A không kiểm chứng được cho chính cú sập lớn nhất mẫu.**
Trên panel B (2014+, loại bỏ cú sập 2008 không thể tránh) — maxDD MAIN có cải thiện nhẹ ở 2/4 tổ hợp
(DIVERGE×R3_capit: −40,2% vs buy-hold-B −45,3%, ~5pp) nhưng **XẤU HƠN buy-hold ở DIVERGE×R4_dt5g
(−46,0% vs −45,3%) và cả 2 tổ hợp RSI×R3/R4** — không nhất quán theo hướng "luôn bảo toàn".

**(c) Sharpe/Calmar so với mua-và-giữ: cao nhất chỉ NGANG BẰNG, không có tổ hợp nào vượt rõ rệt.**
Tổ hợp tốt nhất tuyệt đối là DIVERGE×R4_dt5g (Sharpe 0,665 vs buy-hold-B 0,655 — chênh 0,010,
trong biên độ nhiễu với N=13) nhưng **Calmar của nó (0,227) còn THẤP HƠN buy-hold-B (0,236)**. Mọi
tổ hợp RSI_DIVERGE_3M đều Sharpe THẤP HƠN buy-hold panel tương ứng, có ca kém xa (R1_K63 Sharpe
0,208 vs buy-hold-A 0,504).

**Trả lời trực tiếp phần lõi**: **cơ chế rút KHÔNG bảo toàn vốn theo nghĩa "vượt trội mua-giữ hay
vượt trội rút-mù-cùng-tần-suất."** Đúng như dispatch cảnh báo trước khi làm — chi phí cơ hội (thời
gian OUT + phí giao dịch mỗi lần đổi trạng thái) ăn gần hết phần drawdown "tránh được", và phần
drawdown lớn nhất mẫu xảy ra ngoài tầm với của tín hiệu. Đây là kết quả quan trọng nhất của việc
này — nó ĐẢO NGƯỢC giả định ban đầu của user, không xác nhận nó.

---

## §3. Việc B — Re-entry rules: định nghĩa causal + phân phối thời gian

Cả 4 rule đều dùng thông tin tới hết phiên `t-1` (không hậu nghiệm).

- **R1 thời gian cố định**: `sessions_out >= K`, K∈{21,63,126}.
- **R2 breadth phục hồi**: `breadth_pct252[t-1] >= 0,50` (ngưỡng trung tính/median, không grid-search
  — 1 điểm có lý do rõ, ảnh gương của ngưỡng p90 dùng cho DIVERGE).
- **R3 CAPIT/washout** — **tái tạo được**, dùng lại đúng công thức `crisis_capitulation_signal.py`:
  `oversold(D_RSI<0,3 trên ticker_prune)>=0,30` HOẶC (`DT5G=CRISIS` VÀ `oversold>=0,057`).
  ⚠️ **Đơn giản hoá có chủ đích**: bỏ BEAR-guard (VNINDEX rv10 cooling vs đỉnh 30 ngày) — guard đó
  trong bản gốc chỉ có tác dụng biến 1 lần "fire" thành "BEAR_SKIP" (tức làm capit_fire NGHIÊM
  NGẶT HƠN, không bao giờ nới lỏng hơn), nên bản tái tạo ở đây là cận trên hơi rộng của rule thật.
  Sanity check: `capit_fire` nổ 6,6% số phiên panel B, tập trung đúng các năm khủng hoảng đã biết
  (2020 COVID 20 ngày, 2022 sập 77 ngày) — không suy biến.
- **R4 DT5G trở lại risk-on**: `state[t-1] ∈ {NEUTRAL, BULL, EX-BULL}` (3,4,5), đọc từ
  `tav2_bq.vnindex_5state_dt5g_live` (bảng ĐÚNG).

### 3.1 Phân phối thời gian-tới-tái-vào (probe độc lập từng episode DIVERGE_DAY, không phải engine
cộng dồn — đo "rule này giữ bạn OUT bao lâu" cho từng episode riêng lẻ)

| Rule | Panel | n_episode | n chưa fire hết panel | median | p25 | p75 | min | max |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| R1_K21 | A | 13 | 0 | 21 | 21 | 21 | 21 | 21 |
| R1_K63 | A | 13 | 0 | 63 | 63 | 63 | 63 | 63 |
| R1_K126 | A | 13 | 1 | 126 | 126 | 126 | 126 | 126 |
| R2_breadth050 | A | 13 | 1 | **2,5** | 1 | 9,5 | 1 | 147 |
| R3_capit | B | 13 | 0 | **63** | 48 | 142 | 3 | 187 |
| R4_dt5g | B | 13 | 0 | **1** | 1 | 1 | 1 | 152 |

**Đọc bảng**: R4_dt5g median=1 phiên vì DT5G ở NEUTRAL/BULL/EX-BULL **76,9%** số ngày trong panel B
(state=CRISIS/BEAR chỉ 23,1%) — sau phần lớn episode mania-top, DT5G **KHÔNG** rơi vào BEAR/CRISIS,
nên rule gần như luôn "đã sẵn sàng" ngay lập tức → **không phải một cơ chế timing thật, mà gần một
no-op** (giải thích tại sao nó có %OUT thấp nhất §2.1 và Sharpe cao nhất — chủ yếu vì gần như luôn
ở trong thị trường, giống buy-hold). R3_capit ngược lại — median 63 phiên, đòi một washout THẬT
(hiếm, 6,6% ngày) nên giữ bạn OUT rất lâu ở đa số episode, và tail dài (187 phiên ~9 tháng) ở case
không có washout genuine sau đỉnh. R2_breadth050 có phân phối 2 đỉnh rõ: đa số episode breadth phục
hồi rất nhanh (p25=1) nhưng 1 case kéo dài 147 phiên (~7 tháng, khớp episode 2022-01-06 — breadth
không phục hồi nhanh sau đỉnh mọi thời đại).

**Trả lời trực tiếp "rule nào tốt nhất, bao lâu"**: **không có rule nào vừa timing-thật vừa hiệu
quả round-trip đồng thời** (§2.2). Nếu buộc chọn 1: **R2_breadth050 (median 2,5 phiên, IQR 1-9,5)**
là rule có nội dung thông tin thật nhất (§2.1 MAIN vs CTRL3: 8,67% > 7,74%, tức reentry rule ĐÓNG
GÓP thật so với chờ ngẫu nhiên) nhưng vẫn KHÔNG vượt buy-hold hay CTRL2. R4_dt5g cho số tuyệt đối
đẹp nhất nhưng vì lý do sai (gần no-op), R3_capit đúng tinh thần "CAPIT/mania mirror" nhất về mặt
khái niệm nhưng round-trip yếu nhất (Sharpe thấp nhất trong 3 rule đo được trên panel B khi ghép
DIVERGE_DAY).

---

## §4. Việc C — Mô tả hậu nghiệm "vùng nguy hiểm kéo dài bao lâu" (KHÔNG dùng để giao dịch)

⚠️ **ĐÂY LÀ MÔ TẢ HẬU NGHIỆM (ex-post), không phải rule.** Đo: số phiên từ t0 (ngày exit đầu tiên
của episode) tới ngày ĐẦU TIÊN VNINDEX vượt lại giá tại t0 VÀ giữ trên đó liên tục ≥21 phiên.

| Trigger | n (loại truncate) | median | p25 | p75 | min | max |
|---|---:|---:|---:|---:|---:|---:|
| DIVERGE_DAY | 12 (1 truncate) | **17** | 6 | 76 | 0 | **890** |
| RSI_DIVERGE_3M | 44 (1 truncate) | **24** | 6 | 144 | 0 | **1.198** |

Đuôi cực dài đến từ đúng 2 case "đỉnh mọi thời đại": episode 2022-01-06 (VNI 1.528,57) mất **890
phiên (~3,6 năm)** để vượt lại và GIỮ trên mức đó ≥21 phiên liên tục — khớp thực tế lịch sử VNINDEX
không hồi phục bền vững qua ATH cũ tới tận 2025. Case RSI tương ứng (2022-01-04) mất 891 phiên,
nhất quán. Case cực đoan nhất là RSI-episode 2009-10-12 (đỉnh phụ giữa khủng hoảng 2008-2009): 1.198
phiên (~4,8 năm) — thị trường mất gần nửa thập kỷ để "ổn định thật" sau đỉnh đó. **Thông điệp cho
user**: "vùng nguy hiểm" median chỉ vài tuần (17-24 phiên) nhưng phân phối RẤT lệch phải — không có
cách biết trước tại t0 case nào rơi vào đuôi dài, nên bất kỳ rule cố định thời gian nào (R1) đều
đánh cược vào việc không rơi đúng 1 trong ~15-20% case đuôi dài này.

---

## §5. Trả lời trực tiếp 2 câu hỏi của dispatch

**(1) Cơ chế rút có bảo toàn vốn thật không?** **KHÔNG được xác nhận, bằng chứng nghiêng về "không."**
Ba mảnh bằng chứng độc lập, cùng hướng:
- Round-trip NAV thật KHÔNG vượt rút-ngẫu-nhiên-cùng-tần-suất trong 8/12 tổ hợp (§2.2a).
- maxDD chỉ cải thiện ở 2/4 tổ hợp đo được trên panel sạch (2014+, loại cú sập 2008 tín hiệu không
  với tới) — 2/4 tổ hợp còn lại maxDD XẤU HƠN mua-giữ (§2.2b).
- Sharpe/Calmar cao nhất chỉ NGANG mua-giữ (chênh trong biên độ nhiễu N=13), phần lớn tổ hợp
  RSI_DIVERGE_3M kém RÕ RỆT hơn mua-giữ (§2.2c).

Kết luận không mâu thuẫn với §3 của job trước ("DIVERGE_DAY là cảnh giác, không phải timing") —
job này ĐO SÂU HƠN ở mức NAV round-trip và cho kết quả nhất quán, mạnh hơn: không chỉ "không đo
được độ sâu", mà **cả biên round-trip thật cũng không có edge đáng tin với N hiện có.**

**(2) Rule tái vào nào tốt nhất, bao lâu?** **Không có rule nào vừa timing thật vừa round-trip tốt
đồng thời** — trade-off rõ giữa 3 rule đo được:
- **R2_breadth050** (breadth_pct252≥0,50): rule có nội dung thông tin thật nhất (thắng CTRL3 ở cả
  2 trigger), median **2,5 phiên** nhưng đuôi tới 147 phiên ở case xấu nhất.
- **R4_dt5g** (state trở lại NEUTRAL/BULL/EX-BULL): số tuyệt đối đẹp nhất (Sharpe cao nhất) nhưng
  vì gần-như-no-op (median **1 phiên**, do DT5G ở risk-on 77% thời gian) — không phải cơ chế timing.
- **R3_capit** (washout tái tạo từ `crisis_capitulation_signal.py`): đúng tinh thần "ảnh gương
  mania" nhất, đòi washout THẬT nên median **63 phiên** (đuôi tới 187), nhưng round-trip yếu nhất
  trong 3 rule khi ghép DIVERGE_DAY.

Nếu buộc khuyến nghị 1 con số cho "bao lâu thì ổn để vào" theo tinh thần dispatch, câu trả lời trung
thực nhất không phải một con số cố định mà là: **median ~2-3 tuần (breadth-based) tới ~3 tháng
(washout-based), với xác suất đáng kể (~15-20% case) kéo dài nhiều tháng tới vài năm (§4)** — và
KHÔNG rule nào trong 4 rule đã thử biến điều đó thành một cơ chế sinh lời vượt trội mua-và-giữ có
thể kiểm chứng được với N hiện có.

---

## §6. Giới hạn

1. **N nhỏ ở mọi tổ hợp** (13-45 episode/trigger, 36 cho combo panel B) — không tính DSR/PBO (không
   đề xuất wire). Chênh lệch CAGR 1-3pp giữa MAIN/CTRL2/CTRL3 ở nhiều tổ hợp nằm trong biên độ có
   thể chỉ là nhiễu bootstrap, không phải hiệu ứng thật — đọc bảng §2.1 với tinh thần đó.
2. **maxDD panel A bị chi phối bởi cú sập 2008** xảy ra trước khi DIVERGE_DAY từng tồn tại — không
   phải thất bại của tín hiệu, mà là giới hạn cấu trúc của khoảng dữ liệu; panel B (2014+) là phép
   thử công bằng hơn nhưng N càng nhỏ hơn (13 hoặc 36 episode).
3. **R3_capit là bản tái tạo ĐƠN GIẢN HOÁ** của `crisis_capitulation_signal.py` — bỏ BEAR-guard
   (chỉ khiến rule NGHIÊM NGẶT HƠN nếu có, không nới lỏng), và không dùng `rating_8l.csv`/lọc ngành
   (không liên quan tới câu hỏi TIMING của job này, chỉ liên quan tới CHỌN MÃ). Nếu muốn số chính
   xác 1:1 với sizing thật, cần chạy lại có guard đầy đủ — không ảnh hưởng tới kết luận §5 (guard
   chỉ làm R3 giữ bạn OUT LÂU HƠN, càng củng cố hướng "round-trip yếu" đã thấy).
4. **Cost giao dịch = 0,1%/chiều, không mô hình hoá slippage/thuế** — CAGR thật ước tính thấp hơn
   khoảng 1,5pp mỗi bên có giao dịch thường xuyên (CLAUDE.md §Backtest); các tổ hợp có `n_trades`
   cao (RSI×R2_breadth050: 317 lần đổi trạng thái) chịu drag thực tế LỚN HƠN con số đã trừ 0,1%,
   càng bất lợi hơn cho kết luận "MAIN vs buy-hold" đã trình ở đây (nghĩa là kết luận §5 THẬN TRỌNG,
   không phóng đại theo hướng có lợi cho cơ chế).
5. **Không kiểm định thống kê hình thức** (không có scipy trong môi trường job) — mọi so sánh MAIN
   vs CTRL2/CTRL3 chỉ bằng trung bình bootstrap, không p-value.
6. **RESEARCH-ONLY**, không qua quant-skeptic (không đề xuất production change).

---

## §7. Self-check

- **0-VND tương đương**: path luôn-IN (không exit_flag nào bật) tái lập CHÍNH XÁC buy-and-hold —
  `max abs error 5,77e-15`, `0 trades` (assertion trong code, không chỉ in ra quan sát).
- `capit_fire` sanity check: 6,6% ngày fire trên panel B, tập trung đúng 2020 (20 ngày) và 2022 (77
  ngày) — không suy biến (luôn/never fire).
- `dt5g_reentry` (state∈{3,4,5}) = 76,9% ngày panel B — khớp trực giác "phần lớn thời gian thị
  trường KHÔNG ở BEAR/CRISIS", giải thích trực tiếp vì sao R4 median=1 phiên (§3.1).
- Case định nghĩa 2022-01-06 tái xuất hiện nhất quán ở cả `roundtrip_results.csv`, `reentry_timing_dist.csv`
  (R2_breadth max=147 khớp đúng episode này), và `venc_stability_lag.csv` (lag=890, số lớn nhất mẫu,
  khớp lịch sử thật VNINDEX không vượt bền vững ATH cũ tới 2025).
- PIT causal: engine dùng `exit_flag[t-1]`/`reentry_rule` đọc thông tin tới `t-1` để quyết định vị
  thế phiên `t` — không có nhánh nào đọc `vni[t]` hay flag[t] trước khi quyết định vị thế `t`.

---

## Artifact

`roundtrip/capit_dt5g_hist.csv` (BQ pull mới, panel B) · `roundtrip/round_trip.py` (engine + MAIN +
2 control + self-check) · `roundtrip/roundtrip_results.csv` (bảng §2.1 đầy đủ) ·
`roundtrip/reentry_timing_dist.csv` (bảng §3.1) · `roundtrip/venc_stability.py` +
`roundtrip/venc_stability_lag.csv` (bảng §4, hậu nghiệm).
Bus: `mania-exit-reentry-roundtrip-verdict-20260903`.
