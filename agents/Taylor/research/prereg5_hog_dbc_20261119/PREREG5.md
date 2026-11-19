# PREREG-5 — Paper forward: nowcast KQKD DBC từ biên heo (họ 2) · Taylor · 19/11/2026 · job Taylor_20261119_095518

Viết + commit TRƯỚC mọi nowcast forward (quý forward đầu tiên 2026Q4 chỉ tính được từ 01/2027). PAPER-ONLY: không lệnh,
không plan, không `trading_rules.json`/`filter.json`/LAG/BAL, không cron tự cài. KHÔNG sửa PREREG-4 (md5 `6c5642c1…`).
Phạm vi do user duyệt 19/11: CHỈ họ 2, CHỈ DBC (BAF banned ⇒ không đo, không giao dịch). Họ 8/9 không làm; 10/11 đóng băng.

## 0. KẾT LUẬN (đọc trước)
1. **Trong 2 năm (8 quý), chương trình này KHÔNG đủ power để xác nhận gì. Nó chỉ đủ để BÁC BỎ nếu nowcast hỏng nặng.**
   Nếu tương quan thật là 0,53 (đúng mức DBC-only 12 quý gần nhất), xác suất qua ngưỡng "đủ điều kiện xin xét" ở mốc 8 quý
   chỉ **0,28–0,30**. Muốn có power ~0,5 phải 16 quý (mốc cuối ~11/2030).
2. **Câu hỏi về tiền (drift sau BCTC, giá trị cho LAG) KHÔNG trả lời được** với 1 mã: drift vượt trội nhỏ nhất phát hiện được
   (80% power) là **11,7pp (1 tháng) / 17,3pp (3 tháng)** sau 8 sự kiện. Sổ chỉ ghi drift để mô tả, không kiểm định.
3. **Tác động NAV tối đa rất nhỏ:** trong ledger pin0% DBC chỉ có **3/695 lệnh LAG (0,43%) và 1/299 lệnh BAL (0,33%)**.
   Dù nowcast hoàn hảo, nó chạm khoảng 1 lệnh mỗi 2 năm.
4. **Khuyến nghị: chạy sổ (rẻ), kỳ vọng thẳng là "tiếp tục theo dõi" hoặc "đóng".** Chi phí: 1 lần nowcast + 1 lần outcome mỗi
   quý, dữ liệu đã có cron sẵn. Phương án rẻ hơn nữa là **đóng ngay**, nếu user cho rằng câu hỏi 1 mã không đáng giữ 4 năm.
   Không có đường nào dẫn tới wire LAG/BAL trước mốc 12 quý (~11/2029), và kể cả lúc đó chỉ là "đủ điều kiện XIN xét".
5. Trial: **+1 ⇒ dòng hàng hoá/ngành 29 → 30.**

## 1. Giả thuyết nhân quả, và điểm mới so với "SUE đã biết trước"
**Cơ chế.** DBC có mảng chăn nuôi heo và TACN. Lợi nhuận mảng heo ≈ (giá heo hơi − chi phí thức ăn/kg hơi) × sản lượng.
Giá heo VN (3tres3) và giá ngô/khô đậu là dữ liệu công khai **trong quý**. Vì vậy biến động lợi nhuận YoY của DBC phải
nhìn thấy được trước khi BCTC công bố, khoảng 12–31 ngày sau `sig_day` (đo trên 27 quý lịch sử).

**SUE đã biết trước.** LAG vào lệnh SAU công bố, theo SUE `surprise_B_MA` (`lag_live_schedule.py`). Nếu np_d dự báo được từ
giá công khai thì một phần "bất ngờ" thực ra đã biết trước. Theo lý thuyết PEAD, phần đó lẽ ra được định giá trước ngày công
bố. PREREG-4 kiểm điều này cho 25 mã tier A; **DBC không có trong đó** vì PREREG-4 map dùng `lean_hogs` CME (sai hàng).
- **Điểm mới (H-a, kiểm được):** một biến số công khai, ghi lại TRƯỚC ngày công bố, dự báo đúng hạng và dấu np_d của DBC
  **forward**, chứ không chỉ trong mẫu A4 đã thấy.
- **Không kiểm được (H-b):** "DBC drift sau BCTC đến từ phần SUE không đoán trước được". Với 1 mã, N quá nhỏ (§3.2).

Số mô tả trong mẫu (ĐÃ THẤY, không phải bằng chứng forward; đo từ `a4_panel.csv`, chỉ dòng DBC): n=27 quý 2020Q1–2026Q3,
Spearman(c, np_d) **0,783**, trùng dấu **23/27**, hai nửa 0,76/0,58. **12 quý gần nhất (2023Q4→): 0,53, trùng dấu 10/12.**
8 quý gần nhất: 0,60, trùng dấu 7/8. Tự tương quan bậc 1: c 0,76, np_d 0,49. Chu kỳ ASF 2020–21 chi phối mẫu. Quant-skeptic
CONFIRMED mức vừa cho họ 2 (IC 0,83 gộp DBC+BAF, n_eff ~11, 8 quý đầu chỉ có DBC, hệ số FCR/khẩu phần là giả định khoá trước,
plateau 0,82–0,84). **Mức neo cho power là 0,53, không phải 0,83.**

## 2. Đối tượng đo (ĐÓNG BĂNG)
- **Tín hiệu `c`**: nguyên văn `a4_nowcast.py` họ 2 (md5 `0a51c805dd057774b9d3de48a7f260d5`) + PREREG_ADDENDUM A1
  (md5 `6d30494832b2458a4aef0e65e2cf9e0d`). Cụ thể:
  feed = 0,65·corn/100/25,4·usdvnd + 0,25·SBM/1000·usdvnd/usdcny; M = hog_q − 2,8·feed_q; c = (M_q − M_{q−4})/hog_{q−4}.
  Ngưỡng: heo ≥ 10 quan sát/quý, feed ≥ 40. Nguồn: `data/hog_price_vn.csv` (TB 3 miền), `commodity_prices` daily với
  **đúng bộ lọc 11 mã của `fetch_data.py`**, `macro_indicator` cho tỷ giá.
  Đo được: lấy 2 mã thay vì 11 thì chỉ mục ngày đổi, `ffill(limit=7)` đổi theo, và c lệch tới 0,0014. Vì vậy bộ lọc là một
  phần của định nghĩa.
- **Đối chứng tái lập (selfcheck):** `signal()` của sổ tái lập c của A4 cho **đủ 27 quý DBC, lệch < 1e-9**, trên snapshot
  19/11 (`commodity_snapshot_20261119.parquet` md5 `79617a2c…`, `macro_snapshot_20261119.parquet` md5 `f45dbe9e…`).
- **np_d_hat** = −0,000367 + 0,257436·c. Đây là OLS trên 27 quý DBC, CHỈ dùng để mô tả mức; cổng §3 chỉ dùng c.
- **Đích** np_d = (NP_P0 − NP_P4)/Revenue_P4, cắt ±0,5 (= sue1 PREREG-4). Lấy bản công bố ĐẦU TIÊN: thấy lần đầu thì giữ.
- **Ghi kèm, chỉ mô tả:** sue2 (= SUE LAG live, trùng tracker PREREG-4, selfcheck so 3 ca), drift log DBC − VNINDEX ở
  H = 20 và 60 phiên, tính từ t0 = phiên cuối ≤ ngày công bố.
  Rủi ro biết trước: Close điều chỉnh corp-action bị khoá ở lần thấy đầu, giống PREREG-4 addendum mục 4. Mốc 12 quý sẽ đối
  chiếu lại.
- **Quý forward:** 2026Q4 trở đi. Quý < 2026Q4 bị script từ chối, vì chúng đã thấy trong A4.

## 3. Câu hỏi kiểm định, power, dừng sớm, đóng
### 3.1 Trả lời được (H-a, chỉ theo hướng bác bỏ/duy trì)
Thống kê trên ĐÚNG K quý `counts=True` đầu tiên, tại các mốc K ∈ {8, 12, 16}. Script từ chối `review` ngoài mốc, và ghi
audit mọi lần gọi:
- S_K = số quý có c·np_d > 0; ρ_K = Spearman(c, np_d).
- Ngưỡng ρ = phân vị 95% của ρ dưới H0 khi cả hai chuỗi AR(1) φ=0,6 (c thật có φ 0,76). Mô phỏng 4.000 lần, seed 20261119:
  n8 **0,69**, n12 **0,61**, n16 **0,53**. Ngưỡng S theo nhị thức một phía ≤ 0,04: 7/8 (p 0,035), 10/12 (0,019), 12/16 (0,038).

| Mốc (ước tính theo lịch BCTC) | CLOSE nếu | CONTINUE_ELIGIBLE nếu | còn lại |
|---|---|---|---|
| K=8: 2026Q4→2028Q3, ~11/2028 | S ≤ 4 hoặc ρ ≤ 0 | S ≥ 7 **và** ρ ≥ 0,69 | CONTINUE |
| K=12: →2029Q3, ~11/2029 | S ≤ 7 hoặc ρ ≤ 0 | S ≥ 10 **và** ρ ≥ 0,61 | CONTINUE |
| K=16: →2030Q3, ~11/2030 (mốc cuối) | mọi trường hợp không ELIGIBLE | S ≥ 12 **và** ρ ≥ 0,53 | — |

### 3.2 Power, nói thẳng
Power của "ELIGIBLE" theo ρ: mô phỏng AR(1) φ=0,6 (φ=0 trong ngoặc), 4.000 lần:

| ρ thật | K=8 | K=12 | K=16 |
|---|---|---|---|
| 0,30 | 0,14 (0,15) | 0,17 (0,21) | 0,20 (0,28) |
| 0,50 | 0,28 (0,30) | 0,33 (0,46) | 0,44 (0,61) |
| 0,70 | 0,48 (0,57) | 0,63 (0,78) | 0,75 (0,91) |
| 0,83 | 0,69 (0,77) | 0,84 (0,95) | 0,94 (0,99) |

Theo trùng dấu, với p_hit = tỷ lệ trúng thật: P(S8 ≥ 7) = 0,59 / 0,26 / 0,04 khi p_hit = 0,83 / 0,70 / 0,50.
P(S8 ≤ 4, tức CLOSE) = 0,03 / 0,19 / 0,64.
⇒ Ở mốc 8: nếu nowcast vô dụng, khả năng ĐÓNG đúng là 64%; nếu nó tốt như lịch sử, khả năng đóng nhầm là 3%. Khả năng
xác nhận được một nowcast tốt vừa phải (ρ 0,5) thì thấp. **Hai năm không đủ để có ý nghĩa xác nhận.**

Drift (H-b, chỉ mô tả): SD excess DBC − VNINDEX sau 26 sự kiện lịch sử là 0,119 (20 phiên) và 0,175 (60 phiên).
MDE 80%/hai phía 0,05 = 2,8·SD/√n ⇒ **11,7pp / 17,3pp ở n=8**, 8,3pp / 12,2pp ở n=16. Không mốc nào kiểm định drift.

### 3.3 Dừng sớm (cơ học, script in cờ)
- **3 quý counted liên tiếp trượt dấu** (c·np_d ≤ 0) ⇒ `EARLY_STOP_3_MISS` ⇒ báo user, đề xuất ĐÓNG.
  Xác suất xảy ra trong 8 quý: 0,026 nếu p_hit 0,83; 0,12 nếu 0,70; 0,42 nếu 0,50.
- **Thiếu dữ liệu:** nowcast trả WAIT (heo < 10 quan sát, hoặc dữ liệu chưa phủ cuối quý) mà tới ngày công bố vẫn không ghi
  được ⇒ quý MISSING (không tính, không phải trượt). 2 quý MISSING liên tiếp ⇒ báo user. Nếu feed 3tres3 chết hẳn ⇒ ĐÓNG.

### 3.4 Hệ số hết hiệu lực (cờ, KHÔNG tự đóng)
`struct_flag` trên dòng nowcast bật khi 2,8·feed_q/hog_q nằm ngoài [0,159; 0,432], hoặc hog_q ngoài [46.154; 80.032] VND/kg
(dải 2020Q1–2026Q3, đo 19/11). Cờ bật thì quý VẪN tính, nhưng phải báo user. Bật 2 quý liên tiếp ⇒ đề xuất đóng, vì FCR
2,8 và khẩu phần 65/25 là giả định cho cấu trúc giá cũ.
Thay đổi cấu trúc doanh nghiệp DBC (tách/bán mảng heo, M&A đổi tỷ trọng doanh thu; nguồn: Winston corp-action/tin) ⇒ báo
user, đề xuất đóng.

### 3.5 ĐÓNG chương trình khi
CLOSE ở bất kỳ mốc nào; hoặc user chấp nhận đề xuất ở §3.3/3.4; hoặc DBC vào danh sách BANNED / huỷ niêm yết; hoặc hết mốc 16.
Khi đóng: ghi `decision` lên bus và cập nhật registry. Không mở lại họ 2 bằng biến thể (hệ số, độ trễ, mã), trừ khi có một
trial mới được đăng ký riêng.

## 4. GO / NO-GO — không có đường wire
Đầu ra hợp lệ chỉ có: **tiếp tục theo dõi** (CONTINUE / CONTINUE_ELIGIBLE) hoặc **đóng** (CLOSE).
CONTINUE_ELIGIBLE (sớm nhất ở mốc 8, nhưng power thấp) KHÔNG phải GO. Nó chỉ cho phép VIẾT một PREREG sử dụng RIÊNG (ví dụ
hiển thị cạnh lệnh LAG của DBC), và PREREG đó cần quant-skeptic CONFIRMED + user duyệt.
Mọi wire vào LAG/BAL/sizing/gate trước khi có ≥ 8 quý + quant-skeptic + user đều bị cấm. Theo power ở §3.2, Taylor sẽ không
đề xuất wire trước mốc 12.

## 5. Sổ append-only và vận hành
Script: `prereg5_hog_ledger.py` (md5 tại commit này: xem bus/finding; mỗi dòng sổ tự ghi `script_md5` + `prereg_md5`).
Sổ mặc định ở `ledger/` trong thư mục này. **Đề xuất** chuyển sang `data/prereg5_hog_dbc_*.csv` khi Mike duyệt; không tự đặt.
- `nowcast.csv`: quarter, qend, run_ts_utc, run_date_ict, status (ON_TIME/LATE), counts, release_seen, hog_q, hog_q4, n_hog,
  feed_q, feed_q4, n_feed, margin_q, margin_q4, c, np_d_hat, struct_flag, hog_max_date, feed_max_date, inputs_sha256,
  script_md5, prereg_md5. Khoá = quarter. Ghi rồi thì chạy lại không đổi byte nào.
  Nowcast không in c ra màn hình.
- `outcomes.csv`: quarter, release_date, first_seen_utc, NP_P0, NP_P4, Revenue_P4, np_d, sue2, hit (khoá quarter).
- `drift.csv`: quarter, H, t0, tH, ret_dbc, ret_vni, excess, first_seen_utc (khoá quarter+H).
- `review_audit.csv`: mọi lần gọi review.
- Mốc ngày lấy theo ICT (`ZoneInfo`). `--now` chỉ chạy được khi có `PREREG5_SELFCHECK=1`, để không ghi lùi ngày.
- **Selfcheck** `prereg5_hog_ledger_selfcheck.py`: 45 assertion, PASS cả `env -u TZ` lẫn `TZ=Asia/Tokyo`. Gồm: đối chứng A4
  27 quý, hệ số OLS, sue2/np_d trùng tracker PREREG-4, cổng ICT, WAIT, append-only, LATE, outcome lấy bản đầu, drift
  20/60, review từ chối, luật quyết định, cờ dừng sớm. Mutation thủ công: 10/10 mutant bị bắt (FCR, ngưỡng heo,
  keep="first", counts, t0, cắt tại qend, ngưỡng CLOSE, 3-miss, cổng phủ dữ liệu, chặn quý lịch sử).
- **Tần suất ĐỀ XUẤT (không tự cài; host TZ=UTC):**
  - nowcast: `20 14 5-12 1,4,7,10 *` (21:20 ICT, ngày 5–12 tháng đầu quý). Cron heo chạy thứ Hai 09:00 ICT nên ngày 5 đã có
    tuần cuối. Lệnh idempotent.
  - outcome: `20 14 15 * *` (21:20 ICT ngày 15 hằng tháng).
  - Wrapper đề xuất: sau nowcast ghi được dòng thì `append_event.sh Taylor finding "prereg5-nowcast <Q>"` kèm sha256 của
    dòng. Giai đoạn đầu (2026Q4, 2027Q1) nên chạy tay để quan sát.
- **Entry đề xuất cho `kb/paper_programs_registry.json`** (Mike thêm; Taylor không tự sửa kb/):
```json
{"id": "prereg5_hog_dbc", "name": "PREREG-5 paper forward: nowcast KQKD DBC từ biên heo (họ 2)", "owner": "Taylor",
 "start": "2026-11-19", "end": null, "review_date": "2028-11-30", "reporting": false,
 "reporting_reason": "1 sự kiện/quý; chỉ báo tại mốc K=8/12/16 hoặc khi có cờ dừng sớm/struct_flag",
 "behavior_contract": "LOG_ONLY_NO_BROKER_PATH",
 "feature_flag": "N/A — sổ append-only; không chạm LAG/BAL/trading_rules/filter.json",
 "objective": "Kiểm forward nowcast np_d DBC (c họ 2 đóng băng A4+addendum) ghi TRƯỚC ngày công bố; spec agents/Taylor/research/prereg5_hog_dbc_20261119/PREREG5.md",
 "end_or_trigger": "Mốc 8/12/16 quý (~11/2028, 11/2029, 11/2030): CLOSE/CONTINUE/CONTINUE_ELIGIBLE theo §3.1; dừng sớm 3 trượt liên tiếp; ELIGIBLE ≠ GO — cần PREREG sử dụng riêng + quant-skeptic + user",
 "gate_criteria": [{"status": "pending", "text": "Mỗi quý: dòng nowcast ON_TIME có bằng chứng thời gian (git/bus sha256) trước Release_Date DBC"},
                   {"status": "pending", "text": "K=8: S>=7 và rho>=0.69 ⇒ ELIGIBLE; S<=4 hoặc rho<=0 ⇒ CLOSE"},
                   {"status": "pending", "text": "Không wire trước >=8 quý + quant-skeptic + user (Taylor không đề xuất trước K=12)"}],
 "data_sources": ["data/hog_price_vn.csv", "tav2_bq.commodity_prices (11 mã fetch_data.py)", "tav2_bq.macro_indicator (vn_usdvnd, cn_usdcny)", "tav2_bq.ticker_financial (DBC)", "tav2_bq.ticker (DBC, VNINDEX Close)"],
 "today_activity": "agents/Taylor/research/prereg5_hog_dbc_20261119/prereg5_hog_ledger.py nowcast|outcome",
 "review_short": "Đếm quý counted; mốc đầu K=8 ~11/2028", "notes": "Tạo 2026-11-19 job Taylor_20261119_095518; trial #30 dòng hàng hoá/ngành"}
```

## 6. Chống nhìn kết quả
- Mỗi quý: chạy nowcast trong khoảng [ngày 5 tháng đầu quý, ngày DBC công bố). Trong vòng 24h, hoặc trước ngày công bố
  (lấy mốc sớm hơn), phải có **git commit dòng sổ** **hoặc** **bus event kèm sha256 dòng**. Hai bằng chứng này là dấu thời gian
  độc lập với file.
- Dòng ghi khi BCTC đã có trong `ticker_financial` (đến ngày ICT hôm đó) ⇒ LATE, counts=False, không vào thống kê.
- **Lịch BCTC DBC (đo từ 27 quý lịch sử, `Release_Date` bản đầu):** Q1 17/04–04/05 · Q2 20/07–02/08 · Q3 14/10–29/10 ·
  Q4 21/01–31/01. Khoảng từ `sig_day` tới công bố: 12–31 ngày. Cửa sổ ghi nowcast cho mỗi quý vì vậy là ~1–3 tuần; quý đầu
  tiên 2026Q4: ghi trong 05/01–20/01/2027.
- Rủi ro: `Release_Date` trong BQ là ngày nạp/công bố theo nguồn dữ liệu, có thể muộn hơn ngày DBC đăng BCTC lên website.
  Nếu bằng chứng sau này cho thấy DBC công bố trước dòng nowcast thì quý đó LATE, ghi tay kèm nguồn.
- Không in c, ρ, S ngoài `review` tại mốc. Dòng sổ thì xem được, nhưng luật quyết định đã khoá ở đây.

## 7. Tác động tối đa lên NAV (số đo, không đoán)
Ledger R3-park0-pin0pct-SAN md5 `537e349b5589408c994f8aceafeb9a39`, qua `lag_bal_discriminators_20261025/features.csv`
(abandoned=0 & mtm=0):
- DBC = **3/695 lệnh LAG** (2020-07, 2020-10, 2023-08; pnl −0,39 / +0,18 / −2,00 tỷ) và **1/299 lệnh BAL** (2025-05, +2,81 tỷ).
  BAF: 0 LAG, 1 BAL.
- Thanh khoản DBC (`data/bq_cache/ticker/2026.parquet`, Trading_Value đến 18/11/2026): ADV 20 phiên **34,7 tỷ** (trung vị
  25,0), 60 phiên **28,7 tỷ** (trung vị 22,0), 120 phiên 28,1 tỷ. Capacity không phải ràng buộc. Ràng buộc là **tần suất**:
  ~1 lệnh LAG mỗi 2 năm.
- Kết luận: kể cả trong kịch bản tốt nhất, giá trị tiền của chương trình gần bằng 0. Giá trị của nó là KIẾN THỨC (nowcast
  KQKD forward có giữ được không), không phải NAV.

## 8. Khai báo trial
+1 trial (họ 2 forward, chỉ DBC) ⇒ dòng hàng hoá/ngành **29 → 30** (17 vòng 26/10 + 12 A4 + 1 PREREG-5). Không thêm trial
nào khác: tham số đều đóng băng từ A4, các ngưỡng §3 khai tại đây trước khi có dữ liệu forward.

## 9. Artifact
A4: `a4_nowcast.py` `0a51c805…`, PREREG.md `556059d1…`, ADDENDUM `6d304948…`, map_v2.csv `91bffcc8…`; PREREG-4 `6c5642c1…`
(không sửa). Power/MDE/lịch BCTC/ledger/ADV: đo trong phiên này bằng script inline trên `a4_panel.csv`,
`features.csv` và `data/bq_cache/ticker/*.parquet`. Seed mô phỏng 20261119 (power) và 1 (chuỗi trượt).
