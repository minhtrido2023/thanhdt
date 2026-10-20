# Survivorship replay BAL/LAG trên mã lớn đã biến mất (job Taylor_20261020_094204, EXPLORATORY)

Không sửa pin, registry hay pin_ledger. Không kết luận lại số R3/V2.4, không đề xuất đổi luật.
PREREG `PREREG.md` (md5 `21165fd1…`, commit `9b0b27912`) viết trước khi tính. Mọi số dưới đây lấy từ `out_summary_table.csv` /
`out_replay_results.csv`. Dải số là min…max qua 4 chân pin (park 0,3/0 × pin0%/pin1M). Δ = R3 có phantom − R3 pin;
ΔCAGR âm nghĩa là R3 thiệt.

## Kết luận
1. **Nhãn theo PREREG** (chân chính: X-liq, kịch bản Z, MIX, tập M 14 mã): **"vượt sàn nhiễu ở cận trên, dưới sàn ở cận dưới"**.
   Nhưng chỗ vượt ở cận trên là **chiều LỢI**: +0,68pp ở 1/4 chân (p0_pin0), dải UB là +0,03…+0,68pp. Theo chiều THIỆT, MIX không
   chạm −0,46pp ở chân chính nào. Cận dưới (cổng LAG thật của engine, dựng từ BCTC VNDirect) cho MIX +0,14…+0,32pp.
2. **Hai book đi ngược chiều.** BAL được lợi (UB +0,81…+1,31pp): pha bơm giá của các mã này lọt vào momentum. LAG chịu thiệt
   (UB −0,48…−1,27pp, **riêng LAG vượt sàn**; cận dưới −0,22…−0,30pp).
3. **Không có vị thế nào bị kẹt đến hủy niêm yết ở mô hình chính** (0 lô, tập M, mọi biến thể). Có ba lý do. Exit 25 phiên của
   LAG và stop −20% của BAL thoát trước cú rơi cuối. Universe B4 đẩy mã ra khi thanh khoản cạn. Allocator BEAR (`w_lag_tgt=0`)
   chặn sự kiện LAG cuối của ROS/FLC/HAI (2022-08-05).
4. **Độ nhạy ALLOC (KHÔNG prereg, sát cơ chế engine hơn) xấu hơn rõ ở cận trên:** MIX UB −1,69…−2,67pp, ΔMaxDD −9,1…−10,9pp,
   2–3 lô kẹt (ROS, FLC, HAI vào 2022-08-05). Ở cận dưới vẫn dưới sàn: MID −0,26…+0,02pp, LIVE −0,17…−0,05pp.
   **Cơ chế (đã đo, `logs/decomp_p30_pin0.json`, LAG UB p30_pin0):** KHÔNG phải band trễ — `cap_lag` = 0 ở cả 241/241 ngày
   `w_lag_tgt=0` (đính chính bản nháp trước nói "2022-05-05 target=0 mà LAG còn vốn": sai, ngày đó là CRISIS, target 0,5).
   Engine chạy book LAG tham chiếu (`nav_lag_ref`) **liên tục, kể cả BEAR**; phơi nhiễm combined = vị thế trong book ×
   `cap_lag/combined`. Lô mở lúc BEAR có trọng số combined 0 khi vào, nhưng nếu kẹt đến hủy thì khoản xoá sổ ăn vào NAV khi
   allocator trả vốn về LAG. Phân rã chênh −1,52pp (chính −0,48 → ALLOC −2,00): gộp sự kiện BEAR ở sizing chính đã −1,38
   (thêm −0,90); sizing/overlay theo book không có BEAR −1,25 (thêm −0,77, dù w hiệu dụng median 2,46% < 3,02% chính);
   bỏ các lô kẹt khỏi ALLOC còn −1,55 ⇒ 3 lô kẹt góp −0,45pp. Hai thành phần không cộng tuyến tính. Quy tắc "bỏ sự kiện nếu
   target = 0" trong PREREG vì vậy **đánh giá thấp** phơi nhiễm LAG ở cận trên.
5. **λ_replay so với λ\* v2.** Đo bằng mã-năm nằm trong cửa sổ sụp [LT−365 ngày, DL] chia cho 12,46 năm:
   - cận trên, chính: 0,29–0,33;
   - cận trên, ALLOC: 0,35–0,46;
   - cận dưới (MID): 0,04–0,05;
   - LIVE: 0,00.

   λ\* v2 của MIX là 0,11–0,15 ở L=−100% và 0,19–0,25 ở L=−50%. Cận trên vượt λ\* về **thời gian** nằm trong vùng sụp, nhưng
   ΔCAGR thực nhỏ hơn mức λ\* hàm ý, vì các lô thoát trước đáy. λ\* giả định nắm trọn 12 tháng rồi mất L; replay cho thấy giả
   định đó quá bi quan với BAL/LAG. Cận dưới thấp hơn λ\* khoảng 3–5 lần.
6. **Đọc kết quả thực dụng.** Rủi ro survivorship của nhóm mã lớn đã mất phụ thuộc gần như hoàn toàn vào **cổng BCTC của LAG**.
   Với cổng thật (NP_R≥15%, prior_n_good≥4, pa_HL3≥5), thiệt hại nằm dưới sàn nhiễu ở mọi biến thể đã chạy. Chỉ khi bỏ cổng đó
   (UB = coi mọi quý là sự kiện LAG) thì thiệt hại mới vượt sàn. Riêng LAG ở cận dưới, biến thể ALLOC, chân park 0: −0,50/−0,51pp,
   chạm sàn.

## Bảng chính (tập M = 14 mã, X-liq, Z; dải qua 4 chân)
| Biến thể | Book | ΔCAGR pp | ΔSharpe | ΔMaxDD pp | λ_replay | lô | kẹt |
|---|---|--:|--:|--:|--:|--:|--:|
| UB | BAL | +0,81…+1,31 | −0,01…−0,00 | −0,65…+0,00 | 0,12–0,13 | 76–78 | 0 |
| UB | LAG | −1,27…−0,48 | −0,26…−0,12 | −1,98…−0,80 | 0,16–0,21 | 242–271 | 0 |
| UB | **MIX** | **+0,03…+0,68** | −0,29…−0,14 | −3,86…−1,49 | 0,29–0,33 | 318–349 | 0 |
| MID/LB-R3 | BAL | +0,42…+0,53 | +0,02 | +0,00…+1,00 | 0,01 | 30 | 0 |
| MID/LB-R3 | LAG | −0,30…−0,22 | −0,04…−0,02 | −0,24…−0,00 | 0,02–0,04 | 36–39 | 0 |
| MID/LB-R3 | **MIX** | **+0,14…+0,32** | −0,03…−0,01 | −0,24…+0,86 | 0,04–0,05 | 66–69 | 0 |
| LIVE | MIX | −0,03…+0,02 | −0,00 | −0,24…+0,00 | 0,00 | 22 | 0 |
| UB_ALLOC* | LAG | −2,95…−1,94 | −0,35…−0,21 | −6,64…−4,53 | 0,23–0,34 | 249–279 | 2–3 |
| UB_ALLOC* | **MIX** | **−2,67…−1,69** | −0,42…−0,25 | −10,85…−9,11 | 0,35–0,46 | 326–357 | 2–3 |
| MID_ALLOC* | LAG | −0,51…−0,39 | −0,04…−0,03 | −0,24…+0,00 | 0,02–0,04 | 36–39 | 0 |
| MID_ALLOC* | **MIX** | **−0,26…+0,02** | −0,03…−0,01 | −0,24…+0,86 | 0,04–0,06 | 66–69 | 0 |
| LIVE_ALLOC* | MIX | −0,17…−0,05 | −0,01…−0,00 | −0,24…−0,00 | 0,00 | 22 | 0 |

\* không prereg. Mã-năm trong cửa sổ sụp theo năm (UB, MIX, p30_pin0): 2017 0,30 · 2018 0,23 · 2021 1,55 · 2022 1,34 ·
2023 0,24 · 2024 0,46. MID: 2017 0,19 · 2018 0,15 · 2021 0,20 · 2022 0,13. Tổng hợp từ cột `expo_by_year`.

**Các tập khác (MIX, chính):**
| Tập | UB | MID | LIVE | UB_ALLOC |
|---|--:|--:|--:|--:|
| M−KSA | +0,47…+1,05 | +0,13…+0,25 | −0,03…+0,02 | −2,16…−1,31 |
| A (9 mã hạng A) | −0,14…+0,23 | +0,06…+0,14 | −0,09…−0,06 | −1,83…−1,14 |
| E (21 mã mở rộng, giá chưa đối chiếu) | −1,25…−1,02 | −0,04…−0,00 | −0,10…−0,04 | −2,03…−1,89 |
| M+E (35 mã) | −0,98…−0,45 | +0,10…+0,30 | −0,13…−0,03 | −4,54…−3,56 |
| HVG (hạng C, báo riêng) | −0,54…−0,30 | −0,18…−0,13 | 0,00 | −0,58…−0,35 |

Mở rộng sang 35 mã: cận trên MIX vượt sàn theo chiều thiệt (−0,45…−0,98; ALLOC −3,6…−4,5). Cận dưới vẫn dưới sàn
(+0,10…+0,30; ALLOC −0,12…−0,41). Ở E có 1 lô kẹt ở UB (IBC).

## Tổn thất đến từ đâu (UB, p30_pin0, đóng góp từng lô theo điểm % NAV tại lúc vào, không phải CAGR)
- **LAG thiệt:** ROS −5,07, HAI −5,04, KSA −2,87, TTB −2,72, KLF −1,23, PSH −1,23.
- **LAG lợi:** TGG +8,83 (lô 2021-08-06 tăng ×4,4 tương đối so với NAV trong 25 phiên), GAB +4,67, AMD +2,74.
- **BAL** lợi ở 10/13 mã: ART +2,17, TGG +1,74, ROS +1,33…
- Kết quả bị chi phối bởi vài lô cực đoan trong pha bơm/xả. Ví dụ: chênh pin0 và pin1M ở chân park 0 (LAG UB −0,58 so với −1,27)
  đến từ 11 lô bị bỏ theo luật khớp ≥30%, vì NAV cao hơn làm mục tiêu lớn hơn. Đây là độ nhạy theo đường đi, không phải nhiễu
  ngẫu nhiên.

## Thiết kế đã chạy (tóm tắt; chi tiết ở PREREG)
- **Dữ liệu:** 15 mã của Winston KHÔNG có dòng nào trong `ticker`, `ticker_financial`, `fa_ratings*` và `universe_pit_q`.
  Mọi thứ dựng lại từ VNDirect finfo: giá `delisted-…d/prices*`, BCTC `fin_raw.csv` của Winston, cộng 21 mã E tải cùng cách
  (`svr_fetch.py`, `data/fin_raw_live_ext.csv`). Bảng `data_registry` không có mục cho nguồn này; nguồn được ghi ở
  `kb/projects/delisted-big-vanished-prices-20261020.md`.
- **Engine thật được bắt chước:**
  - BAL: tín hiệu SIGNAL_V11 phần giá, tier MEGA/MOMENTUM/DVR, chặn EX-BULL, chặn overheat, liq ≥1e9, universe ngày, hold 45,
    stop −20%.
  - LAG: Release+5, hold 25, `NP_R≥0,15 ∧ prior_n_good≥4 ∧ pa_HL3≥5`.
  - Khớp lệnh: ≤20% ADV mỗi phiên, tối đa 5 phiên, bỏ nếu khớp <30%. Phí 0,1% mỗi chiều.
  - Exit X-liq: ≤20% GTGD thực mỗi phiên.
  - Halt: kẹt ở giá khớp cuối, xoá sổ tại DL.
- **R3 backtest không có cổng 8L cho BAL/LAG.** Cổng LAG 8L là luật LIVE. Vì vậy:
  - "LIVE" = cận dưới thêm golden floor xấp xỉ (TTM NPAT ở 3 cuối năm ≥0, tổng CFO 12 quý >0). Đây là điều kiện CẦN của
    rating ≤3, nên LIVE là cận TRÊN của tập qua cổng 8L thật.
  - Các trục 8L còn lại (P/E, P/B, P/S, P/CF cần số cổ phiếu; percentile toàn thị trường) không dựng được.
- **Trọng số:** w median theo book của v2 (BAL 2,04–2,56%, LAG 2,92–4,07% NAV). ALLOC thay bằng tỉ trọng vị thế trong book
  ref (BAL 6,2–8,1%, LAG 4,8–6,4%) nhân `cap_b/combined` từng ngày (`out_replay_meta.json`).

## Kiểm định (`logs/validate.json`, 5 mã còn sống HPG, VNM, HQC, ITA, DLG; 2014-01-02→2026-06-19)
- **Universe replica so với `universe_pit_q`:** khớp 98,8–99,9% số ngày ở từng mã. **Đạt cổng ≥95%**, nên phần BAL không
  bị gắn nhãn "không đủ căn cứ".
- **Chỉ báo:**
  - D_RSI (Wilder 14), MA, Volume_3M_P50: sai lệch trung vị ≤0,05%. Dấu MACDdiff khớp 98,6–99,8%.
  - **ta_px khớp tuyệt đối 85,6% (gộp). TRƯỢT cổng mềm 90%.** Nguyên nhân: ID_HI_3Y (khớp nhị phân ≤5 ở 86–97%) và HI_3M_T1
    (90–98%). Cột BQ có vẻ cập nhật trễ/không theo ngày.
  - Điều kiện UB `ta_px≥44` khớp 98,8–99,8%, tức sai số ta không đổi tập tín hiệu UB đáng kể. Ở MID, sai số tới ±18 điểm ta
    ở ~14% ngày.
- **BCTC:** `npat_parent` khớp `NP_P0` BQ 99,5% (`npat` chỉ 55%). CFO VNDirect là CFO đơn quý, khớp `CF_OA_P0` 88,5% (nếu coi
  là luỹ kế thì chỉ 25%).
- **Control:** 4 chân R3 chạy lại byte-identical với kho pin (md5 4707bcbe / bcd0469f / 537e349b / a6ba34d8,
  `logs/control_md5.txt`). Self-check 0 VND cho BAL và LAG, 8/8 dòng. Overlay tái tạo METRIC cagr với sai số ≤1e−9. 4 CSV
  chạy lại đã xoá vì trùng byte với kho pin.
- **Kiểm điều chỉnh giá hạng B** (`logs/classB_check.txt`). Bước nhảy `adClose/close` >2% nằm trong cửa sổ phantom:
  - FLC: 2015-05-27, 2018-02-01, 2018-08-14
  - DAG: 2021-04-14
  - ART, GAB: không có
  - HVG: 2014-02-21, 2014-08-13

  Phantom dùng adClose liên tục; nếu hệ số của nhà cung cấp sai thì lô qua các ngày này lệch. Tập A (bỏ hạng B, KSA) không đổi
  kết luận.

## Lệch so với PREREG / giới hạn
- **Thêm ngoài PREREG** (gắn nhãn \*, không dùng cho nhãn chính): ALLOC; tập A.
- **Script bị lỗi ghi đè giữa chừng và đã viết lại.** Bản viết lại tái tạo 720/720 dòng kết quả cũ với chênh 0
  (`logs/out_replay_results_v0.csv`).
- **U ≡ Z ở mọi ô.** Không lô kẹt nào có phiên UPCOM khớp lệnh sau DL. Ví dụ FLC: 709 dòng UPCOM đều KL=0.
- **X-eng (bán hết ở Open như engine) dễ chịu hơn X-liq:** +0,34…+1,06pp ở UB MIX tập M, +0,11…+0,16 ở MID.
- **UB bỏ qua cạnh tranh slot** (max 12 vị thế mỗi book): nhiều mã được nắm cùng lúc. ΔMaxDD của ALLOC UB (−9…−11pp) là hệ
  quả của việc đó. Không phải ước lượng thực tế.
- **Ngoài phạm vi:** rổ custom30 (có cổng 8L) và nhánh CAPIT. D1 RE_BACKLOG_BUY (cần AdvCust). Release date ước lượng (trễ
  p10–p90 18–34 ngày).
- **Khớp 20% ADV trong pha bơm/xả** (TGG, GAB…) có thể không làm được thật. Phần LỢI của BAL/LAG ở các mã này nên xem là lạc quan.
- **GAB:** ADV chưa kiểm chứng (KL VNDirect lệch Simplize ~7,7×), nhưng GAB đóng góp lớn ở LAG UB (+4,67). **KSA:** hạng
  chưa đối chiếu; M−KSA cho kết quả cùng chiều.
- **E:** giá chưa đối chiếu nguồn thứ hai. VIS, CAV, SIC, CEE là "mất tư cách đại chúng", không phải sụp, nên Z (xoá sổ) bi
  quan cho nhóm này.
- **Engine backtest thật sẽ giữ giá cũ của mã đã halt** (giá khớp cuối) mà không xoá sổ. Replay này đo tổn thất kinh tế thật,
  không phải con số engine sẽ in ra nếu có dữ liệu.

## Tái lập
```bash
O=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_replay_20261020; M=/home/trido/thanhdt/WorkingClaude
W=/home/trido/thanhdt/wt-Taylor_20261020_045223_repin/WorkingClaude; C=data/bq_cache_asof20260729_postrestate
# control (4 chân, như v2): $O/run_leg.sh $M $C svr_ctl_p30_off BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3  (… _p30_1m/_p0_off/_p0_1m như REPORT v1)
cd $M; for m in 4707bcbe… bcd0469f… 537e349b… a6ba34d8…; do python3 mike/bin/pin_ledger.py extract --out $O/raw/pin_<md5_8>.csv <md5>; done
cd $O; P=/home/trido/thanhdt/wc_venv/bin/python
$P svr_fetch.py                     # giá 5 mã sống + BCTC 26 mã (VNDirect) -> data/ ; bq_*.csv: truy vấn trong logs (BQ)
$P svr_validate.py wilder > logs/validate.json
$P svr_replay.py . p30_pin0=raw/pin_4707bcbe.csv p30_pin1M=raw/pin_bcd0469f.csv p0_pin0=raw/pin_537e349b.csv p0_pin1M=raw/pin_a6ba34d8.csv  # ~3 phút
```
Đầu ra: `out_replay_results.csv` (leg × var × scen × xmode × set × cfg), `out_replay_trades.csv` (từng lô),
`out_summary_table.csv`, `out_replay_meta.json` (LT/DL/U từng mã, w, book fraction).

## Đề xuất bước kế (chưa làm; cần Mike/user quyết)
(a) Nếu muốn một con số "thực" thay cho dải UB–LB: chạy BAL/LAG thật (có cạnh tranh slot) với 14 mã đã chèn vào bản sao panel
giá. Việc này đụng engine (bản sao, không pin). (b) Kiểm lại cách engine xử lý lô LAG mở trong BEAR (book tham chiếu vẫn
giao dịch, phơi nhiễm combined bật lại khi allocator trả vốn) — nguồn chênh lớn nhất giữa PREREG và ALLOC; câu hỏi về
engine, không riêng gì survivorship.
