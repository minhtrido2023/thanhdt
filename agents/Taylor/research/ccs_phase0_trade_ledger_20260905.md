# CCS Phase 0 — trade ledger BAL/LAG + PIT feature panel

> Taylor, job `Taylor_20260905_135003`, 2026-09-05. Đề cương: `mike/reports/research_proposal_conviction_sizing_20260905.md` (user duyệt 2026-09-05 20:49 ICT).
> **Phase 0 = TRÍCH XUẤT DỮ LIỆU.** Không kết luận hypothesis nào, không đo win-rate/expectancy, không đổi một dòng logic production nào. Scripts cố tình KHÔNG tính bất kỳ thống kê return theo bucket nào — in ra bây giờ là vô hiệu hoá chính phần pre-registration §5 của đề cương.

## Kết quả một dòng

Cả **3 cổng ra của Phase 0 đều ĐẠT**. Bảng per-trade tồn tại (2.056 entry BAL+LAG, 2014-01-24 → 2026-05-29), self-check khớp NAV pin R3 ở mức **0 VND** trên cả hai sổ, và 70 bucket của H1–H6 đã được đếm theo episode độc lập — **28/70 bucket dưới ngưỡng ~30 episode ⇒ chỉ mô tả, không kết luận** ở Phase 1.

## 1. Nguồn dữ liệu (tra `kb/data_registry/` trước, §9 coding_guidelines)

| Thứ | Nguồn | Status registry |
|---|---|---|
| Sổ giao dịch | `data/v23_..._advprice_exp_repin0803_price_univpit.csv` — **artifact của chính lần RE-PIN R3 2026-08-03** (md5 `7d053e6201c9d107685ff4d1dd9d2d2a`, self-check 0 VND, 17.660 dòng) | pin registry `## 2026-08-03 — ⭐ RE-PIN R3 …` |
| Feature PIT | snapshot đóng cứng `data/bq_cache_asof20260729_postrestate` (`ticker`, `universe_pit_q`, `fa_ratings_8l`, `vnindex_5state_dt5g_live`) — **đúng vintage mà pin được đo** | `price-volume/universe_pit.md` CANONICAL · `market-state/vnindex_5state_dt5g_live.md` CANONICAL |
| Panel tín hiệu | `dump/{sig_bal,sig_lag,lag_cand}.parquet` từ probe chạy lại **đúng lệnh pin** | — |

`tav2_bq.vnindex_5state` (base v3.4b, TRAP) **không được đọc ở bất kỳ đâu** — kiểm tra cơ học trong PIT audit.

**Bản chạy lại tái lập file pin BYTE-IDENTICAL.** Probe chạy đúng lệnh pin nguyên văn trên cùng snapshot đóng cứng cho ra CSV có **md5 `7d053e6201c9d107685ff4d1dd9d2d2a` — trùng tuyệt đối với artifact pin 2026-08-03**, và `diff` trên toàn file (sau khi chuẩn hoá hậu tố `EXP_TAG` trong tên đường dẫn) trả về **0 dòng khác biệt**. Headline in ra khớp từng chỉ tiêu: Final NAV 1.178,01B / CAGR 28,86% / Sharpe 1,90 / MaxDD −17,8% / Calmar 1,62, self-check 0 VND cả hai sổ.

Đáng ghi lại vì suýt bị đọc nhầm: 2 input NGOÀI BQ đã được refresh **2026-09-04** (`data/earnings_surprise_data.pkl`, `data/earnings_events_classified.csv`), và bản chạy hôm nay sinh **5.319** tín hiệu LAG thay vì **5.317** như log lần pin. Nhưng ledger **không đổi một byte** ⇒ 2 sự kiện thêm vào không bao giờ thành lệnh (bị chặn bởi trần vị thế / thanh khoản / đã nắm giữ). Drift là THẬT ở panel ứng viên nhưng **trơ hoàn toàn** với sổ giao dịch. Vẫn lấy ledger từ file pin — không phải vì nghi ngờ bản chạy mới, mà vì đó là artifact được registry pin.

## 2. Bảng per-trade — `trade_ledger_bal_lag_exp.csv`

`mike/agents/Taylor/research/ccs_phase0_Taylor_20260905_135003/trade_ledger_bal_lag_exp.csv` (tên **không canonical**, §8).
**2.056 dòng** = 505 BAL + 1.551 LAG (trong đó 106 dòng thuộc nhánh CAPIT). Rổ parking custom30V (526 lot) tách riêng ra `trade_ledger_all_incl_parking_exp.csv` — nó là phương tiện đỗ tiền, không phải entry của book.

Một dòng = một `holding_id` (gộp mọi phiên fill của cùng một lệnh vào/ra).

**Định danh & thời gian:** `book · ticker · holding_id · play_type · is_capit_arm · entry_fill_date · signal_date · last_fill_date · n_fill_days · exit_date · exit_reason · closed · holding_days` (lịch) `· holding_sessions` (phiên).

**Feature PIT tại ngày vào** — tất cả đo tại `signal_date` = **phiên cuối cùng TRƯỚC phiên fill đầu tiên** (engine thực thi T+1 Open, nên đây mới là ngày hệ thống thật sự "biết"):

| Cột | Nội dung | Cho | Coverage |
|---|---|---|---|
| `dd52` | Close/max(Close 252 phiên) − 1 | H1 | 100,0% |
| `ey`, `PE`, `ey_pct`, `ey_tercile`, `ey_xsec_n` | 1/PE + phân vị/tercile cắt ngang trong universe_pit cùng ngày | H2/H4 | 94,1% |
| `rating_8l`, `rating_asof`, `rating_src` | 8L rating point-in-time | — | 98,2% |
| `pct_adv`, `adv_vnd` | vốn lệnh / (Volume_3M_P50 × COALESCE(Price,Close)) — đúng `LAG_ADV_BASIS=price` của production | capacity | 99,0% |
| `sector` | ICB level-1 = FLOOR(ICB_Code/1000), giống `sec_map` của engine | — | 100,0% |
| `dt5g_state` | state COMMITTED, `vnindex_5state_dt5g_live` | H5 | 100,0% |
| `sessions_since_dt5g_upgrade` | số phiên từ lần upgrade state gần nhất | H5 | 98,2% |
| `breadth_tm1`, `breadth_pct252_tm1`, `breadth_tercile_tm1` | breadth **t−1**, tercile = phân vị trong 252 phiên TRƯỚC | H3 | 100,0% |
| `sig_rank`, `sig_n_cands`, `sig_rank_pct`, `sig_rank_tercile` | thứ hạng tín hiệu trong book hôm đó | H6 | **100%** ngoài nhánh CAPIT |
| `sig_signal_date`, `entry_queue_sessions` | ngày tín hiệu gốc + số phiên lệnh nằm chờ trong hàng đợi | audit | 100% ngoài CAPIT |
| `lag_surprise`, `lag_surprise_tercile` | độ lớn earnings surprise | H4 | **100%** của LAG ngoài CAPIT |

**Outcome:** `cost_vnd` (mua + phí) · `proceeds_vnd` (bán − phí) · `contribution_vnd` · `ret` · `r_multiple_stop` · `r_multiple_vol` · `fee_vnd`. Chi phí đã nằm sẵn trong `fee` của engine theo quy ước pin — ledger **không** áp thêm lớp phí nào lên trên (làm thế là tính hai lần và sẽ phá ngay self-check 0 VND).

**Hai định nghĩa R-multiple, cố ý tách:** `r_multiple_stop = ret / 0,20` chỉ có nghĩa cho **BAL** (engine gọi `simulate(..., stop_loss=-0.20)`); **LAG chạy `stop_loss=-0.99` = thực chất không có stop**, nên cột này để trống cho LAG chứ không mượn con số 20% sang. `r_multiple_vol = ret / (σ_60d_PIT × √holding_sessions)` là đơn vị rủi ro dùng chung được cho cả hai sổ (σ tính từ 60 phiên kết thúc tại `signal_date`).

### Cách đọc `exit_reason` — đừng bỏ qua
| book | ABANDONED_REFUND | TIME | STOP | MTM_UNREALIZED |
|---|---|---|---|---|
| BAL | 191 | 280 | 33 | 1 |
| LAG | 853 | 698 | 0 | 0 |

**`ABANDONED_REFUND` chiếm 55% số dòng LAG.** Đó là lệnh bị bỏ dở giữa chừng khi fill nhiều phiên rồi hoàn lại vị thế — round-trip thật, nhưng thời gian giữ rất ngắn và bản chất là ràng buộc thanh khoản, không phải một "kèo" của chiến lược. Phase 1 phải quyết định tường minh có tách nhóm này ra không; gộp chung vào win-rate sẽ pha loãng đúng cái đang muốn đo.

## 3. Cổng #2 — SELF-CHECK 0 VND

Đọc cho đúng kiến trúc trước: META `combination_note` của chính engine ghi *"books are independent 25B reference ledgers; the allocator scales their RETURN STREAMS into combined NAV"*. ⇒ **đóng góp VND chỉ cộng được ở cấp SỔ**, không cộng thẳng lên combined NAV. Tuyên bố "tổng contribution tái lập 1.178,01B" là sai kiến trúc; con số đúng để kiểm là NAV tham chiếu từng sổ, rồi mới tới combined NAV lấy từ allocator.

| Kiểm tra | BAL | LAG |
|---|---|---|
| 25B + Σ dòng tiền TX − `*_cash_ref` cuối | **+0,000580 VND** | **+0,001923 VND** |
| cash cuối + Σ MTM − `nav_*_ref` cuối | **+0,000488 VND** | **+0,001953 VND** |
| **25B + Σ `contribution_vnd` của ledger − NAV sổ cuối** | **−0,000061 VND** | **0,000000 VND** |
| NAV sổ cuối | 519,4867B | 590,7588B |

Sai số lớn nhất là **1,95 mili-VND trên 590,76 tỷ VND** (2×10⁻¹⁵ tương đối) — cùng bậc với self-check của chính engine (`cash_flow_identity_max_err_vnd_LAG = 7,6e-05`), tức là nhiễu dấu phẩy động float64, không phải chênh lệch kế toán.

Combined NAV cuối đọc từ dòng DAILY cuối = **1.178.009.871.755,57 VND = 1.178,0099B**, khớp pin **1.178,01B**; METRIC trong chính file: `cagr = 0,2886266` (28,86%), `sharpe_252 = 1,8999`, `max_dd = −17,785%`, `calmar = 1,6229`, `combination_replay_err_vnd = 0,0`. **Khớp pin R3 tuyệt đối.**

### Một chỗ phải sửa mới đóng được identity — ghi lại vì nó sẽ cắn người sau
Ban đầu LAG lệch **−770.867.164 VND**. Không phải lỗi làm tròn, không phải chi phí bỏ sót: engine phát ra **đúng một** dòng exit với `holding_id = VCR_20200427_?` (hậu tố seq không resolve được — `shn.py:1301` fallback `entry.get("seq_id", "?")`), trong khi các dòng buy của cùng vị thế mang `VCR_20200427_1409`. Sell mồ côi ⇒ cả cụm bị tính là chưa thoát. Đã vá bằng cách ghép theo tiền tố `<TICKER>_<ngày>_` **và chỉ khi** tiền tố đó resolve ra đúng MỘT cụm buy có tổng shares khớp tuyệt đối (74.185,117836 shares — khớp đến chữ số cuối); có `assert` chặn nếu còn dòng mồ côi nào không ghép được. Đây là artifact đánh nhãn của engine, **không** ảnh hưởng NAV/số pin (dòng tiền vẫn nằm trong `cash_after`).

## 4. Cổng #3 — N episode độc lập per bucket

`n_episode_by_bucket_exp.csv`, 70 bucket. **Episode = cụm entry cùng bucket cách nhau ≤ 10 phiên**; trade trong một cụm chia sẻ cùng cửa sổ thị trường nên không phải mẫu độc lập. Cột `ep_gap5`/`ep_gap21` in kèm để không kết luận nào phụ thuộc vào lựa chọn 10 phiên. Với bucket cấp THỊ TRƯỜNG (H3, H5) có thêm dòng `CALENDAR` đếm block liên tục trên lịch phiên — theo đúng quy ước `b2_neff` 2026-08-22.

Ngưỡng dispatch: **< ~30 episode ⇒ "không đủ sức thống kê, chỉ mô tả"**. Kết quả: **28/70 bucket THIN**.

Bucket đủ N (ep_gap10 ≥ 30), gộp cả hai sổ:

| H | Bucket | trades | ep_gap10 | năm |
|---|---|---|---|---|
| H1 | dd52 ≤ −20% | 702 | 68 | 13 |
| H1 | dd52 > −20% | 1.353 | 75 | 13 |
| H2 | ey=CHEAP, không-recovery | 699 | 64 | 13 |
| H3 | breadth_t−1 = LOW | 868 | 39 | 13 |
| H3 | breadth_t−1 = MID / HIGH | 610 / 578 | 42 / 33 | 13 / 12 |
| H4 | cả 9 ô surprise×ey (LAG) | 62–243 | 32–50 | 12–13 |
| H5 | > 10 phiên sau upgrade | 1.626 | 70 | 13 |
| H6 | rank TOP / MID / BOTTOM | 1.098 / 544 / 308 | 69 / 68 / 57 | 13 |

**Ba chỗ THIN cần biết TRƯỚC khi thiết kế Phase 1** (đây là ràng buộc thiết kế, không phải kết luận về hypothesis):

1. **H5 là bucket mỏng nhất, và mỏng đúng ở phía "được upsize".** "≤10 phiên sau upgrade DT5G" chỉ có **21 episode** (394 trade, 75 phiên lịch, 38 block lịch). DT5G cố tình chỉ có 49 transition trong toàn mẫu — số episode này là **trần cấu trúc**, không phải thiếu dữ liệu, và không mở rộng mẫu được bằng bất cứ cách nào. Nhánh đối chứng ">10 phiên" thì 70 episode.
2. **H2 tách theo recovery làm vỡ cả 3 ô recovery=True** (BAL 15, LAG 11, BOTH 20 episode) — vì nó là H5 nhân với một tercile. Muốn H2 có N, phải định nghĩa "recovery" bằng một trục khác trục DT5G-upgrade (ví dụ breadth thoát tercile đáy), hoặc chấp nhận H2 chỉ chạy ở dạng vô điều kiện — mà bản vô điều kiện thì §3.1 của đề cương đã cấm.
3. **H3 mất N khi tách theo book.** Gộp thì LOW/MID/HIGH đều ≥ 30 episode, nhưng riêng **BAL** cả ba tercile đều 24–27 episode, và ô "LOW & đang quay đầu" chỉ 12 episode / 5 năm. H3 chỉ trả lời được ở mức gộp hai sổ hoặc ở book LAG.

## 5. Feature không lấy được / lấy được nhưng có điều kiện

**Không có feature nào trong dispatch bị thiếu.** Trên **1.950 entry ngoài nhánh CAPIT**, `sig_rank` và `lag_surprise` phủ **100,00%**. Ba chỗ khuyết còn lại đều đã truy được nguyên nhân và không phải lỗi join:

1. **`sig_rank` trống cho 106 dòng — toàn bộ là nhánh CAPIT** (`play_type` `CAPITB_*`/`CAPITL_*`). Đúng theo cấu tạo: `add_capit_arm()` bơm tín hiệu CAPIT thành panel riêng với `ta = 500` cố định, chúng không dự bảng xếp hạng cạnh tranh của book nên không có thứ hạng để đọc. Đánh dấu bằng cột `is_capit_arm` + bucket riêng `H6 rank=n/a (CAPIT arm)`.
2. **`ey_tercile` trống 5,9%** — mã không có PE > 0 tại `signal_date`. Cách tính cần đọc kỹ: cross-section tham chiếu là universe_pit hôm đó, nhưng mã được chấm điểm **kể cả khi bản thân nó không phải thành viên** — ứng viên LAG đến từ panel earnings chứ không từ universe_pit, siết theo thành viên sẽ đánh rơi ~một nửa sổ LAG khỏi H2/H4.
3. **`sessions_since_dt5g_upgrade` trống 1,8%** — entry trước lần upgrade DT5G đầu tiên trong mẫu (warm-up). Không định nghĩa được, không phải khuyết dữ liệu.

### Một cái bẫy join đã bắt được — đáng mang đi
Bản đầu ghép trade với panel tín hiệu bằng khớp ĐÚNG ngày (`signal_date` = phiên liền trước phiên fill đầu tiên). BAL khớp 452/452, nhưng **LAG hụt 6/1.498**. Chẩn đoán đầu tiên đổ cho drift vintage earnings — **sai**. Nguyên nhân thật: `shn.simulate()` xếp lệnh vào `pending_entries`, và trần vị thế / thanh khoản 0 có thể đẩy **phiên fill đầu tiên** lùi vài phiên so với phiên tín hiệu. Phân bố đo được: `entry_queue_sessions` = {0: 1.944, 1: 3, 2: 2, 3: 1}. Đã sửa thành backward as-of theo mã, dung sai 5 phiên (= `max_fill_days`), và ghi luôn `sig_signal_date` + `entry_queue_sessions` vào ledger để kiểm được. Sau khi sửa: **100% khớp**.

Bài học chung: khi một join "gần đúng" hụt vài phần nghìn, đừng gán cho nguyên nhân đang có sẵn trong đầu (ở đây là drift vintage vừa phát hiện 10 phút trước) — đo cái khoảng lệch rồi mới kết luận. Drift vintage có thật, nhưng nó không phải nguyên nhân của ca này, và mục 1 đã chứng minh nó trơ hoàn toàn với ledger.

## 6. Audit point-in-time — `pit_audit_exp.json`, 9/9 PASS

| # | Kiểm tra | Kết quả |
|---|---|---|
| 1 | Không tham chiếu cột `profit_*` ở bất kỳ đâu trong code trích xuất | PASS, 0 hit |
| 2 | `signal_date` < `entry_fill_date` mọi dòng | PASS, 0/2.056 vi phạm |
| 3 | `exit_date` ≥ `entry_fill_date` | PASS |
| 4 | `dd52` tái lập từ CHỈ các Close ≤ `signal_date` (mẫu 200, seed 12345) | PASS, max\|Δ\| = 9,7e-17 |
| 5 | Breadth thật sự dùng t−1 | PASS: corr(pct252_t−1, r_VNI_t) = **+0,0300** vs cùng phiên **+0,1105** |
| 6 | DT5G chỉ đọc `vnindex_5state_dt5g_live`, không đọc bảng base | PASS |
| 7 | `universe_pit_q.rating_asof` ≤ phiên — quét **toàn bảng** | PASS, 0/1.070.731 |
| 8 | `rating_asof` ≤ `signal_date` trong ledger | PASS, 0/1.314 |
| 9 | Fallback `fa_ratings_8l` dùng giá trị as-of lùi | PASS, 0/706 |

Check #5 là con số đáng chú ý: +0,0300 vs +0,1105. Đúng cỡ tương quan dư mà `b2_breadth` 2026-08-22 đã ghi cho breadth cùng phiên (+0,109) — xác nhận cơ học rằng độ trễ đã được áp thật, không phải chỉ đổi tên cột.

**Một bug đã bắt được nhờ chính check #9** (và là lý do check này đáng tồn tại): bản đầu nối 8L rating fallback bằng `pd.merge_asof` rồi gán ngược bằng `.to_numpy()` vào frame CHƯA sắp xếp — `merge_asof` trả về theo thứ tự sort của nó, nên rating bị xáo giữa các dòng. Không crash, không lệch coverage, chỉ sai giá trị: **528/706 dòng fallback sai rating**. Sửa bằng cách giữ index gốc rồi gán theo index. Bài học chung: gán kết quả `merge_asof`/`groupby` ngược lại bằng vị trí là im lặng sai — luôn đi qua index.

## 7. Quan sát thô — CHƯA QUA GATE, không được dùng làm căn cứ gì

Ghi theo đúng yêu cầu dispatch ("nếu tình cờ thấy pattern"). Đây **không** phải kết quả kiểm định, không có return nào được so, và mọi thứ dưới đây có thể biến mất ở Phase 1:

- **H1 có mặt cắt rộng bất ngờ**: 702/2.055 entry (34%) vào lúc mã đã dd52 ≤ −20%, trải 13 năm, 68 episode. Nghĩa là "washout cấp mã" **không hiếm** trong hai sổ hiện có — nếu H1 có nội dung thì nó không bị chặn bởi cỡ mẫu. Đây là phát biểu về **N**, không phải về edge.
- **H6 lệch phân bố mạnh về TOP** (1.098 TOP / 544 MID / 308 BOTTOM). Cấu tạo thôi: engine mua từ đầu bảng xuống, trần 12 vị thế. ⇒ Phase 1 phải so TOP-vs-BOTTOM **có kiểm soát số ô trống trong book** (`sig_n_cands`), không so hai nhóm cỡ khác nhau 3,5 lần rồi đọc chênh lệch như tín hiệu.
- **H5 mỏng ở đúng phía muốn upsize** — đã nói ở mục 4.1. Đây là cảnh báo thiết kế, và cũng là lý do đề cương xếp H1/H2 có cơ sở cấu trúc mạnh hơn H5.

## 8. File

Thư mục `mike/agents/Taylor/research/ccs_phase0_Taylor_20260905_135003/`:

| File | Nội dung |
|---|---|
| `trade_ledger_bal_lag_exp.csv` | **deliverable chính** — 2.056 entry × 45 cột |
| `trade_ledger_all_incl_parking_exp.csv` | 2.582 dòng, gồm 526 lot parking (dùng cho self-check) |
| `n_episode_by_bucket_exp.csv` | 70 bucket H1–H6 × {trades, entry-days, tickers, years, ep@5/10/21, verdict} |
| `selfcheck_exp.json` | số self-check 0 VND + coverage từng feature + METRIC pin |
| `pit_audit_exp.json` | 9 check PIT + số đo drift vintage LAG |
| `probe.log` | log đầy đủ bản chạy lại (headline + self-check + annual) |
| `breadth_pit_frozen_exp.csv` | breadth + pct252 + tercile, tính lại từ snapshot đóng cứng |
| `ccs_phase0_{ledger,nepisode,pit_audit}.py` | script tái lập |
| `ccs_probe_engine.py`, `run_probe.sh` | bản sao engine + 2 khối dump gated bằng `CCS_DUMP_DIR`, chạy bằng đúng lệnh pin → CSV **byte-identical với artifact pin** (md5 `7d05…2d2a`). `diff` sau khi bỏ các dòng chứa `CCS` cho thấy code production không đổi một ký tự. |
| `dump/` | `sig_bal.parquet` (773.148 dòng), `sig_lag.parquet`, `lag_cand.parquet`, `rs_tier_weights.json` |

Không file canonical nào bị đụng: mọi output mang hậu tố `_exp`, engine chạy dưới `EXP_TAG=ccsp0`, `pt_v23_audit_2014.py` không sửa một ký tự.

## 9. Cần trước khi mở Phase 1

1. **Chốt cách xử lý `ABANDONED_REFUND`** (55% dòng LAG) — tách riêng hay gộp. Quyết trước khi nhìn số, không phải sau.
2. **H2 cần định nghĩa "recovery" thứ hai** không phải DT5G-upgrade, nếu không cả 3 ô recovery=True chết vì N (11–20 episode).
3. **H3 chỉ chạy ở mức gộp hai sổ hoặc LAG**; riêng BAL không đủ N ở cả ba tercile.
4. Giữ nguyên `N_trials = 6` của đề cương. Mọi bucket phái sinh thêm trong lúc chạy (ví dụ "LOW & đang quay đầu" của H3) là **amend đề cương + tăng N trials công khai**, không phải phát hiện.
