# Đối soát panel V2.3-book vs NAV live SpaceX/ZaloPay — job Taylor_20260926_042824

**Ngày**: 2026-09-26 · **Cửa sổ**: 2026-07-02 (SpaceX go-live) / 2026-07-07 (ZaloPay) → 2026-09-24
**Nguồn**: `data/papertrade_compare5.csv` (cột `V23`, `VNI_BH`) · `data/execution_logs/nav_history_{SpaceX,ZaloPay}.csv`
(cột `nav`) · `data/execution_logs/dnse_raw_2026-*.jsonl` (kind=`positions`, LỌC `account_no` trước mọi phép tính
theo §12) · `data/pt_v22_dt5g_{logs,transactions,open_positions}.csv` · `data/papertrade_run_2026-09-25.log`
**Bảng ngày-qua-ngày**: `/tmp/nav_compare.csv` · **Vị thế theo ngày**: `/tmp/positions_daily.csv`

---

## A. Charter SAI — đã sửa

Charter `kb/paper_programs_charter/engine_room_oos.md` viết: *"V2.3-book (NGUỒN TÍN HIỆU của live V2.4 —
trading_bot/strategies.py đọc pt_v22_dt5g_open_positions.csv để build plan thật)"*. **Sai cả hai vế.**

| Khẳng định | Bằng chứng phản bác |
|---|---|
| `strategies.py` đọc CSV panel | `trading_bot/strategies.py:1-11` docstring: lớp strategy V2.3 (`StrategyBase`/`V23Strategy`/`REGISTRY`/`get_strategy`, entry `bot_prepare_plan.py`) **đã GỠ 2026-09-13** (cq-20260913-remove-v23, user duyệt). File giờ chỉ còn 5 hàm helper DCF lens; 0 `read_csv`, 0 `import pandas`. |
| CSV panel là nguồn tín hiệu | `grep -rn pt_v22_dt5g_open_positions --include=*.py --include=*.sh` (trừ worktree/archive) = **3 hit**: `pt_v22_dt5g.py:154` + `:897` (nơi GHI), và `trading_bot/netting_recon.py:17` — **chỉ là DOCSTRING**, 4 lệnh `open()` trong file đó đều trỏ tới `journal_file` / file audit-trail, không tới CSV panel. **Không một dòng code live nào đọc file đó.** |

**Đường tín hiệu THẬT** (crontab 19:00 ICT → `mike/bin/bq_freshness_check.sh`):
```
[pipeline-1]  publish_gated_state.py
[pipeline-1b] build_universe_pit.py            (BLOCK nếu rỗng)
[pipeline-1c] build_universe_pit_quality.py    (BLOCK nếu fail)
[pipeline-2]  deploy_golive_dt5g_v4/golive_recommend_v23.py
[pipeline-3]  mike/agents/Mafee/push_recommend_v23_to_bq.py
              _assert_fresh_artifact(golive_state_today.json, out/golive_v23_recommendations_*.csv)
[pipeline-4]  dispatch DollarBill lập plan T+1 cho MỌI live account
```
DollarBill (LLM) đọc `golive_state_today.json` + `out/golive_v23_recommendations_<DATE>.csv` +
`compute_active_nav.py --account <X>` + vị thế TỔNG thật từ DNSE positions API.

**Quan hệ panel↔live**: `golive_recommend_v23.py:32` — *"Point-in-time snapshot of the SAME logic as
pt_v22_dt5g.py — NOT a NAV backtest."* Hai bản cài đặt **anh em cùng gốc logic V2.3**, không phải
producer→consumer. Panel = NAV backtest daily-advance; live = recommender point-in-time.

**Đã sửa**: `mike/kb/paper_programs_registry.json` mục `engine_room_oos` — field `objective` +
`gate_criteria[1]` (câu "PRODUCTION DEPENDENCY — plan live scale từ sổ này" cũng sai, đã đổi thành
panel-integrity). Chạy lại `mike/bin/paper_programs_daily_report.py` (rc=0) → charter .md regen đúng.

---

## B. Phương pháp "NAV trừ egg" của Mike SAI — kết quả đảo dấu

`egg_assets`/`offbook_assets` là **một túi BÊN TRONG NAV**, không phải vốn ngoài. Tiền chạy
broker-cash ↔ egg là **TRANSFER giữa 2 túi cùng nằm trong nav** ⇒ chuỗi `nav − egg` bị đứt gãy bởi
transfer, không phải chuỗi lợi nhuận.

**Đo thật** — số ngày chuỗi `nav−egg` nhảy khác `nav` tổng >1pp: SpaceX **6 ngày**, tổng |artifact|
tích luỹ **101,7%**; ZaloPay **5 ngày**, **53,5%**. Hai ví dụ cực đoan:

| Ngày | nav tổng | nav−egg | Nguyên nhân |
|---|---|---|---|
| 2026-07-17 (SpaceX) | −0,55% | **−32,13%** | `offbook_assets` 302.108.211 VND lần đầu được ghi nhận |
| 2026-07-21 (SpaceX) | −0,28% | **+47,72%** | offbook về 0, `mtm_stock` 624,58M→877,27M (+252,7M), cash 3,16M→50,00M — tiền từ Trứng vàng quay về và được triển khai |
| 2026-08-19 (SpaceX) | −0,08% | **−10,53%** | cash 109,98M→9,78M, egg 0→100,22M |

Cả 3 đều là bút toán. **NAV tổng là chuỗi liên tục, đúng để đo lợi nhuận.**

### Số đúng

| | SpaceX (từ 07-02) | ZaloPay (từ 07-07) |
|---|---|---|
| NAV gốc | 994.733.747 | 986.585.454 |
| NAV 2026-09-24 | 977.194.265 | 951.368.626 |
| **LIVE tổng NAV** | **−1,76%** | **−3,57%** |
| [Mike] nav − egg | −6,89% *(artifact)* | −4,36% *(artifact)* |
| PANEL V2.3-book cùng cửa sổ | −7,75% | −7,47% |
| VNINDEX B&H cùng cửa sổ | −4,89% | −3,96% |
| **GAP live − panel** | **+5,99pp** | **+3,90pp** |
| GAP live − VNINDEX | +3,13pp | +0,39pp |

**Kết luận ngược với giả thuyết ban đầu: CẢ HAI account đều THẮNG panel.** Sự trùng khớp −6,90 vs
−7,76 và −4,36 vs −4,38 là **ngẫu nhiên số học** — trừ egg tình cờ trừ đi ~5,1pp (SpaceX) và ~0,8pp
(ZaloPay).

Lãi Trứng vàng thực nhận (loại transfer >1trVND): SpaceX **740.176 VND = +0,074% NAV gốc**
(egg trung bình 38,2M, lãi suất ngụ ý ~8,4%/năm); ZaloPay **266.943 VND = +0,027%**. **Không đáng kể
theo cả hai chiều** — egg không giải thích được gì.

### Hai câu chuyện KHÁC NHAU (Mike đúng ở điểm này)

- **SpaceX**: gap phẳng ~−0,7pp suốt 07-03→07-21 (bám sát panel, drag nhẹ do phí). **Bước nhảy
  +4,5pp trong 5 phiên 07-28→08-03** (gap −0,19 → +3,99). Sau đó phẳng +3,4..+4,8pp suốt tháng 8,
  trôi lên +5,99 cuối tháng 9. Ngày đóng góp lớn nhất: 07-30 (+1,77pp/phiên), 07-28 (+1,05pp), 08-03 (+0,80pp).
- **ZaloPay**: gap ~0 đến 07-20, rồi **sụp −6,14pp trong 5 phiên 07-21→07-27** (nặng nhất 07-23
  −2,34pp/phiên), sau đó **hồi phục +9,58pp trong 7 phiên 07-28→08-07** lên +3,44. Kết +3,90pp.

Cả hai đợt đều xảy ra **TRƯỚC** mốc park 70→80 (2026-08-04): gap SpaceX đã là +4,00pp ngay 08-03.
⇒ **Chênh lệch park KHÔNG phải nguyên nhân chính.** (Mike đúng hướng ở điểm 3, lý do mạnh hơn.)

---

## C. Nguyên nhân thật của từng đợt phân kỳ

### C1. ZaloPay = DGC, gần như 100%

ZaloPay giữ **10.000 cp DGC** (mở 2026-06-26, `costPrice` 47.775) — vị thế legacy trong
`excluded_tickers`, **KHÔNG rebalance nhưng VẪN nằm trong NAV**, chiếm ~42-47% NAV
(454M/807M cổ phiếu ngày 07-15).

Phân bổ P&L mark-to-market theo mã (vị thế đầu phiên × Δ giá), lọc `account_no` theo §12:

| Cửa sổ | DGC | Tổng MTM | Gap panel thay đổi |
|---|---|---|---|
| 07-21→07-27 | **−61.500.000 VND = −6,70% NAV** | −76.498.100 = −8,33% | **−6,14pp** |
| 07-28→08-07 | **+82.000.000 VND = +9,70% NAV** | +94.151.300 = +11,14% | **+9,58pp** |

**DGC một mình giải thích ~gần trọn cả cú sụp lẫn cú hồi.** Mike giả thuyết (a) CONFIRMED — nhưng
cơ chế ngược chiều với suy đoán ban đầu: không phải ZaloPay *bỏ lỡ* DGC mà panel có, mà là ZaloPay
**MANG** một vị thế legacy tập trung khổng lồ mà panel không có.

### C2. SpaceX = chênh lệch DANH MỤC, không phải chênh lệch park

Tách gap thành hiệu ứng **EXPOSURE** (chênh tỷ trọng rủi ro) vs **SELECTION** (chênh danh mục),
cộng dồn khớp đúng gap thực tế:

| | SpaceX | ZaloPay |
|---|---|---|
| Tỷ trọng rủi ro TB — panel (cp + park) | 83,2% | 83,9% |
| Tỷ trọng rủi ro TB — live (cp) | 87,0% | 93,2% |
| Lợi suất/phiên TRÊN tài sản rủi ro — panel | −0,184% | −0,186% |
| Lợi suất/phiên TRÊN tài sản rủi ro — live | −0,067% | −0,091% |
| **Hiệu ứng EXPOSURE** | **−1,28pp** | **−2,28pp** |
| **Hiệu ứng SELECTION** | **+6,46pp** | **+5,64pp** |
| Tổng (≈ gap cộng dồn) | +5,18pp | +3,36pp |

**Gap do SELECTION chi phối.** Live ở mức rủi ro CAO hơn panel trong một thị trường đi xuống ⇒
exposure là DRAG; toàn bộ phần thắng đến từ danh mục khác nhau.

### C3. Vì sao danh mục khác nhau — SCALE 50B vs ~1B (Mike giả thuyết (b) CONFIRMED)

Cả hai bên đều park vào **cùng một rổ custom30V** (panel: `papertrade_run_2026-09-25.log:504-507`
`BASKET_SELECT=yieldcombo`, `[PARK custompitg/namecap10] ... 30 holdings`; live: 20/28 mã SpaceX và
19/28 mã ZaloPay nằm trong PARK basket của `golive_v23_recommendations_2026-09-25.csv`).
**Không có drift về phương tiện park** — chỉ khác MỨC (70% vs 80%).

Khác biệt nằm ở **sổ BAL/LAG ngoài park**, và nguyên nhân gốc là **sức chứa (ADV)**:

ADV 60 phiên (BQ `tav2_bq.ticker`, 2026-04-01→06-15) và % ADV cần cho một vị thế 10%:

| Mã | ADV (tỷ) | %ADV cần @panel 50B | %ADV cần @live 1B | Ai cầm |
|---|---|---|---|---|
| SCL | 1,03 | **484,3%** | 9,7% | chỉ LIVE |
| NCT | 1,12 | **446,5%** | 8,9% | cả hai |
| TV1 | 2,81 | **177,9%** | 3,6% | chỉ LIVE |
| MSH | 5,74 | 87,0% | 1,7% | chỉ LIVE |
| DRI | 9,30 | 53,7% | 1,1% | chỉ LIVE |
| VIC | 747,5 | 0,7% | 0,01% | chỉ PANEL |

Panel **chưa từng giao dịch SCL / DRI / TV1 / MSH một lần nào** kể từ 2026-06-11
(`pt_v22_dt5g_transactions.csv`). Và ở 50B, các tên nhỏ nó có chạm được thì bị ADV nén về gần 0:
DDN/TCI/SPM/PRC/VLG mua <0,005 tỷ, KHS 0,02, CLC 0,01, HAR 0,03 — so với size đầy đủ 2,5 tỷ.

**Danh mục panel ngoài park** nạp vào **công ty chứng khoán** + PNJ: HCM 2,46B, VND 2,40B, GEE 2,28B,
FTS 2,10B, BSI 1,78B, AGR 1,60B, BMS 0,76B, PNJ 1,91B. Lợi suất 07-02→09-24 của chính các mã đó:

| Chỉ PANEL cầm | | Chỉ LIVE cầm | |
|---|---|---|---|
| PNJ | **−47,2%** | SCL | **+39,8%** |
| FTS | −28,1% | DRI | +10,4% |
| BSI | −28,0% | TV1 | −11,9% |
| GEE | −20,4% | | |
| VND | −19,4% | | |
| AGR | −18,5% | | |
| BMS | −11,4% | | |
| VIC | +4,4% | | |

(cùng kỳ: E1VFVN30 −3,0%, PVT +10,1%, SIP 0,0%)

### C4. Timing/fill (Mike giả thuyết (c))

Panel dùng **"HYBRID alt-fill prices"** (`papertrade_run_2026-09-25.log:493` `[1] Building HYBRID
alt-fill prices`), live khớp giá broker thật. Quy ước phí panel 0,1%/chiều (CLAUDE.md) vs phí thật
DNSE 0,097%/chiều (`mike/bin/dnse_fee_rates.py`) — **chênh 0,003pp/chiều, bậc hai**, không phải
nguồn gap. Không tách riêng được hiệu ứng timing khỏi hiệu ứng selection bằng dữ liệu hiện có;
với biên độ khác biệt danh mục ở trên, timing chắc chắn không phải hạng mục chi phối.

---

## D. Kết luận & ước lượng đóng góp

**Gap panel-vs-live KHÔNG phải do cửa sổ lệch + egg asset.** Đó là hai LỖI ĐO, không phải hai
nguyên nhân: sửa cả hai làm gap **đảo dấu** — live thắng panel +5,99pp (SpaceX) / +3,90pp (ZaloPay).

Ước lượng đóng góp vào gap thực tế:

| Nguồn | SpaceX | ZaloPay |
|---|---|---|
| SELECTION (danh mục khác nhau, gốc = sức chứa ADV @50B vs @1B) | **+6,46pp** | **+5,64pp** |
| ↳ trong đó DGC legacy (excluded_tickers) | n/a | vòng xoay −6,70% rồi +9,70% NAV; chi phối hoàn toàn hai đợt phân kỳ tháng 7 |
| EXPOSURE (live rủi ro cao hơn trong tape giảm) | **−1,28pp** | **−2,28pp** |
| Lãi Trứng vàng (live có, panel giả định 0%/năm) | +0,07pp | +0,03pp |
| Chênh park 70% (panel) vs 80% (live) | không tách được riêng; **chắc chắn không chi phối** — gap đã +4,00pp ngày 08-03, TRƯỚC khi park đổi 08-04 | như SpaceX |
| Chênh phí 0,100% vs 0,097%/chiều | bậc hai | bậc hai |

### Hệ quả cho panel Engine-room OOS

Panel V2.3-book ở 50B và tài khoản live ở ~1B **không so sánh được như hai bản cài cùng chiến lược**
— chúng bị ràng buộc sức chứa khác nhau tới mức chọn ra hai danh mục khác hẳn (panel: CTCK +
micro-cap bị ADV nén; live: rổ custom30V + mid-cap). Panel vẫn hợp lệ cho đúng câu hỏi charter đặt
ra (V2.3 có bị V11/V12/V4 dominate không — cả 4 arm đều chạy ở 50B, so sánh công bằng), nhưng
**KHÔNG hợp lệ làm mốc kỳ vọng cho NAV live**.

### Việc còn mở (chưa làm trong job này)

1. **Nhãn sai trong artifact panel** — `audit_lib.py:34` và `:89` hardcode `"ticker": "E1VFVN30"`
   trong khi `pt_v22_dt5g.py:360` đặt `PARK_TICKER = "CUSTOM_VN30G"`. Hệ quả:
   `pt_v22_dt5g_open_positions.csv` hiện 26 dòng park mang nhãn `E1VFVN30` dù tài sản thật là rổ
   custom30V. `pt_v22_dt5g_transactions.csv` (qua `etf_to_tx` trong chính `pt_v22_dt5g.py:821`) ghi
   ĐÚNG `CUSTOM_VN30G` ⇒ hai artifact của cùng một engine mâu thuẫn nhau. Lỗi HIỂN THỊ, không ảnh
   hưởng NAV, nhưng đủ sức dẫn sai người đọc (đã dẫn sai trong chính job này trước khi truy ra log).
2. Danh mục live có 8-9 mã ngoài rổ recommend (DRI, NCT, SAB, SCL, SIP, TV1, VNM, VPI, CSV) — chưa
   truy xem từng mã đến từ nhánh nào (BAL pick / LAG / DISCRETIONARY_SPECIAL / legacy). Ngoài
   phạm vi dispatch này.
