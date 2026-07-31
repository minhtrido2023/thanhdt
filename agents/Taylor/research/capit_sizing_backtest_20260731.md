# CAPIT sizing — backtest toàn lịch sử fire (2014-2026) + nguồn tài trợ khi thiếu tiền

Job `Taylor_20260731_094324` (nối tiếp `Taylor_20260731_085810` — job đó chạy xong 6 leg nhưng
hết lượt thao tác trước khi trích được số; job này dùng lại nguyên 6 CSV đó, không chạy lại).

Pre-registration: `research/capit_sizing_PREREG_20260731.md` (viết TRƯỚC khi xem leg nào).

## 0. Điều kiện chạy (đóng cứng, giống nhau mọi leg)

`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate` (đúng snapshot đã dùng cho lần re-pin R3
2026-07-29 ⇒ so sánh cùng vintage), `NAV_TOTAL_B=50`, `ETF_LIQ=custompitg`, `BASKET_WT=namecap`,
`BASKET_SELECT=yieldcombo`, `PARK_STATES=3:0.7`, `AUDIT_END=2026-06-19`, threads=1, `$DNA_PYEXE`.
Runner: `data/capit_sizing_20260731/run_leg.sh`.

**Kiểm chứng control**: leg `ctrl` (base=`cash`) tái lập ĐÚNG số pin R3 hiện hành trên **cả bốn**
chỉ tiêu — CAGR 27,60% / Sharpe 1,84 / MaxDD −17,5% / Calmar 1,58 (pin: 27,60% / 1,84 / −17,5% /
1,58) ⇒ engine + snapshot đúng, mọi leg so sánh được. **10/10 leg EXIT=0, self-check cash-flow
identity = 0 VND ở CẢ HAI sổ (BAL+LAG).** (Mọi Sharpe trong tài liệu này là `Sharpe(252)` — cùng
quy ước với số pin.)

## 1. N_trials khai báo (multiple-testing discipline, §Quy chuẩn 5)

Pre-reg khai 6. Job này thêm **4 leg** (2 cho Việc 2 dose-response, 2 cho họ conviction-scaled).
**N_trials thật của họ này = 10.** Mọi DSR/PBO nếu tính phải tính trên đủ 10, không phải 6.

## 2. VIỆC 1 — panel mọi lần CAPIT fire (2014-2026)

**18 sự kiện washout, 15 sự kiện thực sự vào lệnh** (2 sự kiện size=0 do gate maturity/postbull:
2022-04-19 và 2022-09-28; 1 sự kiện không đủ tên). Bảng dưới: `cash`/`idle` = tỷ lệ tiền
rảnh / (tiền rảnh + custom30V đang gửi) trên NAV **từng sổ**; ba cột cuối = **% NAV TỔNG** thực
sự triển khai theo mỗi công thức.

| E | ngày | state_size | cashB | idleB | cashL | idleL | %NAV `cash` | %NAV `idle` | %NAV LIVE |
|---|------|-----------|-------|-------|-------|-------|------------|------------|-----------|
| 0 | 2014-05-08 | 1,000 | 1,00 | 1,00 | 0,76 | 0,76 | 87,4% | 87,4% | 51,9% |
| 2 | 2015-08-24 | 0,375 | 0,30 | 1,00 | 0,00 | 0,01 | 4,4% | 14,6% | 23,1% |
| 3 | 2016-01-18 | 0,750 | 0,25 | 0,83 | 0,30 | 1,00 | 21,1% | 70,2% | 46,3% |
| 4 | 2018-05-28 | 1,000 | 0,39 | 0,39 | 0,02 | 0,02 | 18,7% | 18,7% | 54,5% |
| 5 | 2018-07-05 | 0,375 | 0,30 | 1,00 | 0,30 | 1,00 | 11,2% | 37,5% | 20,7% |
| 6 | 2020-02-03 | 0,750 | 0,20 | 0,78 | 0,16 | 0,74 | 13,2% | 56,6% | 39,7% |
| 7 | 2020-03-11 | 0,250 | 0,85 | 0,85 | 0,55 | 0,55 | 17,2% | 17,2% | 13,1% |
| 8 | 2020-07-27 | 0,375 | 0,14 | 0,47 | 0,09 | 0,64 | 4,2% | 20,9% | 18,7% |
| 10 | 2022-06-15 | 0,250 | 1,00 | 1,00 | 1,00 | 1,00 | 25,0% | 25,0% | 11,2% |
| 12 | 2023-10-30 | 1,000 | 1,00 | 1,00 | 0,05 | 0,05 | 55,9% | 55,9% | 46,5% |
| 13 | 2024-04-17 | 0,500 | 0,03 | 0,03 | 0,92 | 0,92 | 23,3% | 23,3% | 24,4% |
| 14 | 2024-08-05 | 0,500 | 1,00 | 1,00 | 0,00 | 0,00 | 26,7% | 26,7% | 23,3% |
| 15 | 2025-04-03 | 0,500 | 0,00 | 0,00 | 1,00 | 1,00 | 25,9% | 25,9% | 25,9% |
| 16 | 2025-10-20 | 0,750 | 0,12 | 0,39 | 0,16 | 0,72 | 10,4% | 41,3% | 37,0% |
| 17 | 2026-03-09 | 0,750 | 0,00 | 0,00 | 0,02 | 0,06 | **0,7%** | 2,2% | 35,1% |

Tổng hợp %NAV tổng: `cash` median **18,7%** (min 0,7% – max 87,4%); `idle` median **25,9%**
(2,2% – 87,4%); LIVE (`size × NAV_book_LAG`) median **25,9%** (11,2% – 54,5%).

> **Đây là phát hiện quan trọng nhất của Việc 1**: spec đã-backtest (`cash`) KHÔNG phải một quyết
> định phân bổ rủi ro — nó là "bao nhiêu tiền mặt tình cờ đang nằm đó", dao động 0,7% → 87,4% NAV
> giữa các sự kiện GIỐNG NHAU về mức tin cậy. Công thức LIVE (`booknav`) ổn định hơn hẳn
> (11–55%, không bao giờ ~0) — nhưng cũng lớn hơn, tối đa 54,5% NAV tổng vào một rổ deep-value.

### 2.1 Chất lượng tín hiệu CAPIT (đo lại từ chính TX của leg ctrl, không phải số vay mượn)

15 sự kiện, lợi suất rổ theo sự kiện: **win-rate 73,3%**, lãi trung bình khi thắng **+24,76%**,
lỗ trung bình khi thua **−1,91%** ⇒ **payoff 13,0×**; trung bình +17,65%, trung vị +13,80%,
độ lệch chuẩn 19,26%. Lỗ sâu nhất từng ghi nhận: −4,7% (2020-02-03).

Kelly thô trên panel này: `f* = 0,713` NAV (half-Kelly 0,356). Kelly liên tục `μ/σ²` = 4,76 (>1).
**Cả hai đều vô nghĩa để dùng trực tiếp** — n=15, và mẫu KHÔNG chứa một lần washout thật sự đi
tiếp xuống sâu (nhờ chính các gate maturity/postbull chặn 2 sự kiện 2022 xuống size=0). Kelly ở
đây chỉ nói được 1 điều đúng: **ràng buộc thực sự của CAPIT không phải Kelly** (Kelly còn cho phép
lớn hơn cả công thức LIVE), mà là thanh khoản/tập trung và rủi ro đuôi chưa quan sát được.

Kelly có làm thận trọng (giả định lỗ xấu nhất hợp lý −30% thay vì −1,91% quan sát được, giữ
nguyên win-rate 73,3% và lãi +24,8%): `b = 0,825` ⇒ `f* = 0,409`, **half-Kelly ≈ 0,20 NAV**.
Đây là con số duy nhất từ nhánh (c) mà tôi coi là dùng được — và nó nằm ngay trong khoảng
trung vị của cả `cash` (18,7%) lẫn LIVE (25,9%).

### 2.2 Kết quả 6+4 leg (toàn kỳ 2014-01-02 → 2026-06-19, 3107 phiên)

| `CAPIT_SIZE_BASE` | ý nghĩa | CAGR | Sharpe | MaxDD | Calmar | IS 14-19 | OOS 20-26 |
|---|---|---|---|---|---|---|---|
| `cash` **(baseline)** | spec pin R3 — size × tiền mặt rảnh mỗi sổ | 27,60% | 1,84 | −17,5% | **1,58** | 23,38% | 28,49% |
| `idle` | size × (cash + toàn bộ custom30V) | **27,92%** | 1,85 | **−17,4%** | **1,60** | 23,68% | 28,59% |
| `booknav` | **CÔNG THỨC LIVE** — size × NAV sổ LAG, chỉ sổ LAG | 27,34% | 1,82 | −18,0% | **1,52** | 22,37% | 28,76% |
| `nav:0.10` | cố định 10% NAV tổng (bỏ conviction) | **26,72%** | 1,79 | −17,3% | 1,54 | 22,79% | 27,37% |
| `nav:0.20` | cố định 20% NAV tổng (bỏ conviction) | 27,25% | 1,82 | −17,3% | 1,57 | 23,11% | 27,94% |
| `idlecap:0.30` | size × idle, trần 30% NAV sổ | 27,53% | 1,83 | −17,7% | 1,55 | 23,32% | 28,20% |
| `park:0.25` | size × (cash + 0,25 × park) | 27,69% | 1,84 | −17,5% | **1,58** | 23,49% | 28,42% |
| `park:0.50` | size × (cash + 0,50 × park) | 27,99% | 1,86 | −17,9% | 1,57 | 23,60% | 28,87% |
| `navsize:0.25` | conviction-scaled: state_size × 25% NAV tổng | 27,30% | 1,83 | −17,5% | 1,56 | 22,90% | 28,23% |
| `navsize:0.40` | conviction-scaled: state_size × 40% NAV tổng | 27,90% | 1,86 | −18,0% | 1,55 | 23,22% | 29,00% |

**Đọc bảng — 4 điểm, theo thứ tự quan trọng:**

1. **Toàn bộ họ 10 leg nằm trong dải CAGR 26,72–27,99% (1,27pp) và Calmar 1,52–1,60 (0,08).**
   Đây mới là kết quả chính của Việc 1: **cơ sở sizing CAPIT gần như KHÔNG phải một đòn bẩy ở tầng
   danh mục.** CAPIT chỉ bắn 15 lần trong 12 năm; đổi hẳn công thức từ "tiền mặt tình cờ có" sang
   "% NAV cố định" dịch chuyển kết quả ít hơn cả sai số vintage dữ liệu đã đo được lần re-pin
   07-29 (+0,47pp CAGR chỉ do trôi dữ liệu). Mọi kết luận dưới đây phải đọc trong bối cảnh đó.
2. **Chỉ `idle` vượt cổng pre-registered** (Calmar ≥ baseline ∧ MaxDD không tệ hơn 1,0pp ∧ giữ dấu
   cả IS lẫn OOS): Calmar 1,60 ≥ 1,58, MaxDD −17,4% (tốt hơn), dIS +0,30pp ∧ dOOS +0,10pp. Nhưng
   biên vượt là **+0,02 Calmar / +0,32pp CAGR trên n=15 sự kiện** — đúng nghĩa nằm trong nhiễu.
   `park:0.25` hoà Calmar nhưng đổi dấu IS(+0,11)/OOS(−0,08) ⇒ trượt. `park:0.50`, `navsize:0.40`,
   `idlecap:0.30`, cả họ `nav:*` đều Calmar < baseline ⇒ trượt.
3. **Bỏ conviction-scaling là thứ DUY NHẤT gây thiệt hại rõ.** `nav:0.10` (10% NAV phẳng, mọi sự
   kiện như nhau) là leg TỆ NHẤT: −0,88pp CAGR, và tệ ở CẢ IS (−0,60pp) lẫn OOS (−1,13pp) — dấu
   nhất quán, không phải nhiễu một chiều. `nav:0.20` cũng âm cả hai vế. Ngược lại cặp
   `navsize:*` (giữ nguyên state_size, chỉ đổi cơ sở sang %NAV tổng) bám sát baseline. ⇒ **`state_size`
   {0,25/0,375/0,5/0,75/1,0} đang mang thông tin thật; cơ sở nhân với nó thì không mấy quan trọng.**
4. **Công thức LIVE (`booknav`) là leg YẾU NHẤT về rủi ro của cả họ**: Calmar 1,52 (thấp nhất),
   MaxDD −18,0% (sâu nhất, cùng `navsize:0.40`), IS 22,37% (−1,01pp so baseline — thấp nhất họ).
   ⚠️ **Không quy toàn bộ khoản thiệt này cho công thức**: leg này cố ý ép `wt=0` cho sổ BAL để khớp
   hình dạng live (1 sổ thay vì 2 — xem §5), nên nó lẫn hai hiệu ứng. Kết luận trung thực rút ra
   được: **công thức đang chạy LIVE chưa từng là công thức được backtest, và ở dạng gần-live nhất
   đo được thì nó không tốt hơn spec `cash` ở bất kỳ chỉ tiêu rủi ro nào.**

## 3. VIỆC 2 — nguồn tài trợ: có nên bán custom30V không?

### 3.1 Đính chính cơ chế (quan trọng, đọc trước khi diễn giải số)

Trong engine, **parking ĐÃ LUÔN được bán để tài trợ lệnh mua khi thiếu tiền**, ở MỌI leg kể cả
`ctrl` — `simulate_holistic_nav.py:1119` (JIT ETF-sell, FIFO, bán đúng bằng phần thiếu, có trần
thanh khoản `_etf_day_cap`). Vậy nên:

- Việc 2 (a) vs (b) **không phải** là "được phép bán parking hay không" — mà là **nhắm size bao
  nhiêu**. Cận `X%` custom30V là một ràng buộc **SIZING**, không phải ràng buộc funding.
- Họ `park:f` (`wt = size × (cash + f × park)`) chính là đường dose-response của Việc 2:
  `f=0` ≡ `cash` (spec pin, không tính parking vào cơ sở size), `f=1` ≡ `idle` (tính toàn bộ).

### 3.2 Bán parking chỉ giúp được ở MỘT PHẦN sự kiện

Từ bảng §2: parking chỉ tồn tại khi state=NEUTRAL (`PARK_STATES=3:0.7`). Ở các washout sâu nhất
(state CRISIS/BEAR) **không có custom30V để bán**. Phân loại 15 sự kiện:

- **Parking giúp đáng kể** (idle ≫ cash ở ít nhất 1 sổ): E2, E3, E5, E6, E8, E16 — 6/15 (40%).
- **Parking KHÔNG giúp** (cash≈idle, tiền đã nằm trong deal BAL/LAG hoặc rỗng hẳn): E0, E4, E7,
  E10, E12, E13, E14, E15 — 8/15.
- **Không gì giúp được** (cả cash lẫn parking ≈ 0, sổ đã full deal): **E17 2026-03-09** —
  `cash` chỉ triển khai được **0,7% NAV** trong khi LIVE nhắm 35,1%. Đây là ca cực đoan cho thấy
  spec `cash` có thể "bỏ lỡ" gần như trọn một tín hiệu.

### 3.3 Dose-response: cho phép tính bao nhiêu % custom30V vào cơ sở size

| f (`park:f`) | ý nghĩa | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|
| 0,00 | ≡ `cash` — KHÔNG tính parking (spec pin) | 27,60% | 1,77 | −17,46% | **1,58** |
| 0,25 | bán tối đa 25% parking | 27,69% | 1,77 | −17,50% | **1,58** |
| 0,50 | bán tối đa 50% parking | 27,99% | 1,78 | −17,87% | 1,57 |
| 1,00 | ≡ `idle` — bán không giới hạn | 27,92% | 1,77 | −17,41% | **1,60** |

Đọc: CAGR tăng đơn điệu-yếu theo f (+0,09 / +0,39 / +0,32pp), **Calmar gần như phẳng
(1,57–1,60)**, MaxDD dao động ±0,4pp không có xu hướng. Tức là **bán custom30V để tài trợ CAPIT
KHÔNG làm xấu rủi ro**, và lợi ích lợi nhuận là dương nhưng nhỏ — nằm trong sai số của n=15 sự kiện.

### 3.4 Trùng tên giữa rổ CAPIT và rổ parking = 16,7%

Đo trực tiếp trên 14 sự kiện có dữ liệu rổ parking cùng thời điểm: **10/60 tên CAPIT đã nằm sẵn
trong rổ custom30V** (E2 HPG+PVS, E4 TCM, E8 KSB+NT2, E10 HPG, E13 QNS, E14 VNM, E15 TNG, E17 VGC)
— trung bình ~0,7 tên/sự kiện. Với các tên này, bán parking rồi mua lại chính nó ở arm CAPIT là
**round-trip vô ích**: mất ~2× phí + chênh giá mà vị thế ròng gần như không đổi.



## 4. Đề xuất

### 4.1 Kết luận thẳng cho 2 câu hỏi được giao

**Việc 1 — công thức sizing nào?** Bằng chứng **KHÔNG đủ để yêu cầu đổi spec đã backtest**. Không
leg nào tách khỏi baseline quá nhiễu n=15; leg duy nhất qua cổng (`idle`) hơn +0,02 Calmar. Nếu
tiêu chí là "có nên thay đổi thứ đã được pin R3 không" → **câu trả lời là KHÔNG**.

Nhưng câu hỏi thực tế đang cần trả lời không phải vậy — mà là **LIVE đang chạy `booknav`, thứ chưa
từng được backtest**. Ở khung đó thì có đề xuất rõ:

> **Đề xuất (chờ quant-skeptic): CAPIT target = `state_size × 25% NAV TỔNG`** (leg `navsize:0.25`).
> Cụ thể theo state_size hiện hành: 1,0 → **25%** NAV · 0,75 (grind) → **18,75%** · 0,5 → **12,5%** ·
> 0,375 → **9,4%** · 0,25 → **6,25%**.

Lý do chọn đúng mức 25% — bốn đường độc lập hội tụ, không phải chọn điểm tốt nhất trên grid:
- Trung vị %NAV tổng thực tế đã triển khai suốt 15 sự kiện: `idle` 25,9%, LIVE 25,9% (§2).
- Half-Kelly **thận trọng** (giả định lỗ xấu nhất −30% thay vì −1,91% quan sát được): ≈ **0,20 NAV** (§2.1).
- Trong cặp conviction-scaled, `navsize:0.25` **trội hơn `navsize:0.40` về rủi ro** ở cả hai chỉ tiêu
  chính pre-reg: Calmar 1,56 > 1,55 và MaxDD −17,5% > −18,0%. Pre-reg chốt trước là ưu tiên
  Calmar/MaxDD, không phải CAGR ⇒ chọn 0,25 dù CAGR thấp hơn 0,60pp.
- So với thứ **đang thực sự chạy LIVE** (`booknav`), nó **tốt hơn**: Calmar 1,56 vs 1,52, MaxDD
  −17,5% vs −18,0%, IS 22,90% vs 22,37%. So với spec pin `cash` thì gần như hoà (−0,30pp CAGR,
  −0,02 Calmar).

Cái đổi lấy được, và là lý do thật để cân nhắc: **tính xác định**. Spec `cash` triển khai từ 0,7%
đến 87,4% NAV giữa các sự kiện *cùng mức tin cậy* — E17 (2026-03-09) chỉ vào được **0,7% NAV** vì
sổ tình cờ hết tiền, tức gần như bỏ lỡ trọn tín hiệu. `booknav` thì ngược lại, có lần nhắm **54,5%**
NAV tổng vào một rổ deep-value. `navsize:0.25` chặn cả hai đuôi: sàn 6,25%, trần 25%.

**Việc 2 — có nên bán custom30V để tài trợ?** **CÓ, và không cần đặt trần.** Ba căn cứ:
- Dose-response f = 0 → 0,25 → 0,50 → 1,0 cho Calmar **1,58 / 1,58 / 1,57 / 1,60** và MaxDD dao động
  ±0,4pp không xu hướng ⇒ **bán parking để tài trợ CAPIT không làm xấu rủi ro**, kể cả bán không giới hạn.
- Lợi ích lợi nhuận dương nhưng nhỏ (+0,09 / +0,39 / +0,32pp CAGR) và không đơn điệu ⇒ đọc là
  "vô hại + hơi có lợi", KHÔNG phải "tối ưu tại f=0,5".
- Đây vốn **đã là hành vi engine ở mọi leg** (JIT ETF-sell, `simulate_holistic_nav.py:1119`) — nên
  cái đang chốt ở đây là **cơ sở tính size**, không phải "có được phép bán hay không" (§3.1).

⚠️ Giới hạn quan trọng của kết luận này: parking chỉ tồn tại ở state NEUTRAL, nên nó **chỉ cứu được
6/15 sự kiện** (§3.2). Ở washout sâu (CRISIS/BEAR) không có custom30V để bán — và E17 cho thấy
*cả cash lẫn parking đều ≈ 0*. **Bán parking KHÔNG phải là lời giải cho bài toán thiếu tiền; đổi cơ
sở sizing sang %NAV mới là.**

### 4.2 Quy tắc ưu tiên bán khi cần tài trợ

1. **Loại trước tiên mọi tên custom30V đang có mặt trong rổ CAPIT sắp mua.** Đo được 16,7% trùng
   tên (10/60, §3.4) — bán rồi mua lại chính nó là round-trip mất ~2× phí + chênh giá mà vị thế
   ròng gần như không đổi. Đây là quy tắc rẻ nhất và chắc chắn đúng trong toàn bộ đề xuất này.
2. Trong phần còn lại, bán theo **thứ tự yieldcombo tăng dần** (tên rẻ nhất của rổ parking giữ lại
   sau cùng) — nhất quán với chính selector `BASKET_SELECT=yieldcombo` đang dùng để dựng rổ.
3. Chỉ bán **đúng bằng phần thiếu** (đã là hành vi FIFO của engine), tôn trọng trần thanh khoản
   `_etf_day_cap` — không bán trọn sleeve.

### 4.3 Việc bắt buộc TRƯỚC khi trình user quyết wire

- **`bin/verify_finding.sh` (quant-skeptic)** — chưa chạy. Đây là thay đổi chạm cơ chế CAPIT **đang
  giải ngân dở** (5 mã SAB/SIP/VNM/PVT/NCT còn giữ thật), nên không được bỏ qua cổng này.
- **DSR trên N_trials = 10** cho `navsize:0.25` (§1). Chưa tính. Với biên so baseline là ÂM
  (−0,30pp CAGR), lập luận wire **không phải** "cao hơn baseline" mà là "tính xác định + tốt hơn
  cái đang chạy live" — cần nói đúng như vậy khi trình, đừng trình như một cải thiện hiệu năng.
- Đối chiếu trần **%ADV thật** (`capit_adv_caps`): 25% NAV tổng ở NAV thật hiện tại có vượt sức
  hấp thụ của rổ 5-8 tên không. Backtest này không mô phỏng ràng buộc đó (§5) ⇒ 25% là **trần mong
  muốn**, không phải cam kết thực thi được.

## 5. Giới hạn đã biết

- **Engine cộng CAPIT vào CẢ HAI sổ** (BAL tag="B" + LAG tag="L"), trong khi LIVE chỉ tài trợ từ
  sổ LAG. Leg `booknav` cố ý ép `wt=0` cho sổ BAL để khớp live; các leg khác giữ hành vi 2 sổ của
  spec gốc. Khác biệt cấu trúc, không phải bug — nhưng nghĩa là leg `booknav` là leg DUY NHẤT
  mô phỏng đúng hình dạng LIVE.
- Backtest **không** mô hình hoá tài sản off-book (Trứng vàng) — nguồn vốn thật của đợt 07-21.
  Trứng vàng nay đã đóng hẳn cả 2 account (07-23) nên chênh lệch này thu hẹp về sau.
- n=15 sự kiện. Mọi kết luận về win-rate/payoff/Kelly có sai số lớn; mẫu không chứa ca washout
  thất bại nặng.
- Trần %ADV thật (`capit_adv_caps`) và pool `ticker_prune` (chưa cutover `universe_pit`) là ràng
  buộc LIVE mà backtest này không mô phỏng — size đề xuất là **trần mong muốn**, thực tế có thể
  bị ADV cap ép xuống.
- **Chưa qua `bin/verify_finding.sh` (quant-skeptic)** — bắt buộc TRƯỚC khi trình user quyết wire.
