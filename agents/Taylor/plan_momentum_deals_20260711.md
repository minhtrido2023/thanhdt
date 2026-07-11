# PLAN — Phân tích deal thành công lịch sử của book Momentum → tìm pattern thật
> Taylor, 2026-07-11 · job Taylor_20260711_163023 · trạng thái: **USER ĐÃ DUYỆT · CP0 = GO (Phase 0 xong, job Taylor_20260711_165407) — chờ duyệt sang Phase 1**
> Khuôn kỷ luật: giống plan_fa8l_retune_20260711.md — plan trước, pre-register trước, mới đốt compute.

## 0. Bối cảnh & mandate (từ user, 2026-07-11)
- Phase 2 fa8l re-tune NO-GO cho thấy trục **MOMENTUM_N** (kênh entry chính của BAL dưới NEUTRAL)
  không tái tạo được trên nền 8L — dấu hiệu pattern momentum cũ **dựa vào 1 "quality filter ngầm"
  tình cờ** của tier legacy, dễ vỡ/overfit.
- Chỉ đạo user: **KHÔNG cố giữ momentum vì quen thuộc**. Quay lại soi các deal thành công lịch sử
  của book, tìm đặc điểm fundamentals (dùng **8L**, không quay lại fa_tier cũ) + technical thật sự
  phân tách thành công/thất bại. Nếu số liệu không ủng hộ momentum → bỏ, tìm pattern mới.
- Đây là dự án ĐỘC LẬP với rebuild fa_ratings (đang chạy song song, không đụng nhau).
- **Kết quả "không có pattern" cũng là kết quả hợp lệ** — khi đó khuyến nghị sẽ là thu hẹp/đóng
  kênh MOM_N và tái phân bổ vốn, không phải cố nặn ra pattern.

## 1. Nguồn dữ liệu (đã tra `mike/kb/data_registry.md` trước khi chọn — §9 guidelines)
| Nguồn | Vai trò | Trạng thái registry | Ghi chú |
|---|---|---|---|
| `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv` | **Sổ deal book chính** (round-trip thật của harness R3, 2014→2026-06, re-pin DT5G 07-11) | CANONICAL (pin R3 28.82/1.90/−15.7/1.83) | Đọc-only; mọi output experiment ghi ra `data/momdeal_exp/` (§8) |
| `data/ba_v11_unified_12y_sig.pkl` | Universe signal V11 (mọi lần play_type fire, kể cả book không nhận) | Research cache, **frozen 2026-06-16** | Phase 0 PHẢI rebuild (`build_state_free_signals.py`) — pkl hiện tại built TRƯỚC fix F3 (state có thể là base, không phải DT5G) + thiếu 1 tháng cuối. Đọc bằng `$DNA_PYEXE` (pandas 3) |
| `tav2_bq.vnindex_5state_dt5g_live` | Regime tại entry | CANONICAL | KHÔNG đọc bare `vnindex_5state` (TRAP) |
| `tav2_bq.fa_ratings_8l` | Fundamentals lens: rating 1–5, route, tier, forensic | CANONICAL (as-of PIT; cadence cron chờ verify Sat 07-18) | Theo chỉ đạo user: dùng 8L, KHÔNG dùng fa_tier legacy làm feature. Join as-of đúng PIT |
| `tav2_bq.ticker` / `ticker_prune` | Technical features tại entry + label forward (`profit_2M/3M` — CHỈ làm label, không bao giờ làm feature/filter) | CANONICAL | Qua BQ local cache (DuckDB, threads=1) |
| `data/pt_v22_dt5g_transactions.csv` + execution logs SpaceX/ZaloPay | Deal live/paper thật | CANONICAL nhưng chỉ từ ~06/2026 | **Quá ngắn để phân tích** — chỉ dùng làm go-forward validation sau này, KHÔNG nằm trong dataset lịch sử |

## 2. Khảo sát sơ bộ N — ĐÃ ĐO HÔM NAY (số thật, không ước)
**(a) Deal book đóng (round-trip, CSV canonical R3, 2014→2026-06):** tổng 2.258 closed; BAL-entry family:

| play_type | N | win% | avg ret | median | Phân bố năm đáng chú ý |
|---|---|---|---|---|---|
| MOMENTUM_N (+_W) | 55+22=**77** | 56.4/54.5% | +7.9/+8.9% | +0.4/+0.9% | rải 12 năm, 2022-24 gần như trống |
| MOMENTUM_S (+_W) | 35+11=**46** | 45.7/54.5% | +6.1/+5.9% | −1.2/+6.2% | dồn 2021 (18/35) |
| MOMENTUM / MEGA | 10+0 | 90% | +13.8% | — | N quá nhỏ |
| DEEP_VALUE_RECOVERY (+_W) | 180+67=**247** | 55.6/50.7% | +5.8/+2.1% | +1.0/+0.1% | dồn 2021 (57) + 2025 (45) |
| RE_BACKLOG_BUY (+_W) | 106+30=**136** | 54.7/50.0% | +6.5/+7.6% | +0.5/−0.2% | đều hơn |
| (so sánh: LAG_HI/LO) | 844/784 | 47/44.8% | +2.3/+1.1% | ~0 | book LAG, không thuộc scope chính |

**(b) Episode signal V11 (mọi lần fire, gap>7 ngày = episode mới, pkl frozen 06-16):**
MOMENTUM_N **87** · MOMENTUM_S **513** · MOMENTUM 129 · MEGA 10 · DVR **1.077**.
Phân bố năm MOM_N: 2020+2021 = 36/87; 2022-24 gần trống (1+2+0). MOM_S: 2021 = 217/513 (42%!).

**Hệ quả thống kê — định hình toàn bộ thiết kế:**
1. **MOM_N một mình KHÔNG đủ N** (87 episode / 77 deal) để mine pattern riêng với >3-4 feature —
   mọi phân tích phải chạy ở cấp **BAL-entry family** (MOM_N+S+MOMENTUM+MEGA ≈ 739 episode signal,
   ~169 deal book) với DVR/RE_BACKLOG (~1.2k episode) làm cohort đối chứng "kênh đang chạy được".
2. **2021 chiếm tỉ trọng cực lớn** (MOM_S 42%, DVR 38%) — mọi kết luận bắt buộc per-year LOO,
   đặc biệt ex-2021 (đúng bài học F12 ở fa8l).
3. Deal live thật (từ 07-01) N<20 — không dùng được cho phân tích lịch sử.

## 3. Định nghĩa "deal thành công" (pre-registered, 2 tầng label)
- **L1 — book-level (đơn vị: round-trip trong CSV canonical):** return net phí của holding_id
  (đã đo được chính xác từ ledger). `SUCCESS` = net ret ≥ **+10%**; `FAIL` = net ret ≤ **0%**;
  giữa (0,+10%) = neutral, loại khỏi contrast chính (làm sensitivity). Ưu điểm: phản ánh exit rules
  thật. Nhược: N nhỏ, nhiễu bởi capacity/path của portfolio (deal bị nhận/từ chối tùy cash).
- **L2 — signal-level (đơn vị: episode fire, ngày đầu episode):** forward **profit_2M** (T+40,
  cột có sẵn, CHỈ dùng làm label — không bao giờ dùng làm feature/filter, đúng quy tắc no-look-ahead).
  `SUCCESS` = profit_2M ≥ **+10%**; `FAIL` ≤ **0%**. Sensitivity: profit_3M và ngưỡng +7%/+15%.
  Ưu điểm: N lớn hơn ~5×, không nhiễu capacity. Nhược: bỏ qua exit rules.
- **Label chính để kết luận = L2** (đủ N); **L1 là consistency check** — pattern tìm được trên L2
  phải KHÔNG mâu thuẫn dấu trên L1, nếu mâu thuẫn → nghi ngờ artifact của exit rules, điều tra thêm.
- Ngưỡng +10%/0% khai báo TRƯỚC khi nhìn bất kỳ contrast nào theo feature (hôm nay mới chỉ nhìn
  aggregate return của play_type — chưa nhìn phân phối theo feature nào).

## 4. Bộ đặc điểm pre-registered (13 feature — KHÔNG vơ hết cột, mỗi feature có lý thuyết đứng sau)
**Fundamentals — 8L (5):**
| # | Feature | Lý thuyết |
|---|---|---|
| F1 | `rating` 8L (1–5) tại entry (as-of PIT) | Câu hỏi trung tâm: chất lượng 8L có phân tách deal thắng/thua không — thay thế "quality filter ngầm" |
| F2 | `route`/lens 8L (categorical) | User tin route-specific lens chính xác hơn; kiểm chứng route nào momentum ăn/không ăn |
| F3 | ROIC_Trailing | Chất lượng sinh lời thật, trục Quality cốt lõi |
| F4 | CF_OA_P0 (>0 hay không + magnitude) | Tiền thật vs lợi nhuận kế toán — ứng viên số 1 của "quality filter ngầm" (golden floor hiện có đã dùng CF_OA_3Y) |
| F5 | Revenue_YoY_P0 | Momentum giá có doanh thu đỡ ≠ momentum trơ |

**Technical (5):**
| # | Feature | Lý thuyết |
|---|---|---|
| T1 | `ta` score tại entry (có sẵn trong signal) | Điểm kỹ thuật tổng hợp hệ đang dùng — baseline |
| T2 | D_RSI tại entry | Entry lúc quá mua vs còn room |
| T3 | Volume ngày entry / Volume_3M_P50 | Breakout có dòng tiền xác nhận vs không |
| T4 | C_L1M (vị trí giá vs đáy 1M) | Mua đuổi đỉnh vs mua nền |
| T5 | Close/Res_1Y | Còn kháng cự trên đầu vs đã thoát đỉnh 1 năm |

**Liquidity/context (3):**
| # | Feature | Lý thuyết |
|---|---|---|
| C1 | log(Trading_Value_1M_P50) | Nghi vấn chính từ fa8l post-mortem: filter ngầm loại "junk NHỎ" — size/liquidity có thể chính là pattern |
| C2 | DT5G state tại entry (dt5g_live) | Momentum ăn theo regime nào |
| C3 | days_since_release | Gần công bố BCTC (PEAD overlap) vs momentum "trơn" |

Quy tắc cứng: **13 feature này là toàn bộ danh sách Phase 1** — thêm bất kỳ feature nào = mở
N-ledger mới, ghi rõ lý do, không thêm quá 3. Không đưa `profit_*`/bất kỳ cột forward nào vào
feature. Mọi feature tính tại T-1 hoặc entry-day-open information set.

## 5. Phương pháp & validation
**Phase 1 — descriptive contrast (không tuning):**
- Univariate: mỗi feature so phân phối SUCCESS vs FAIL (rank-sum + effect size Cliff's delta),
  **FDR Benjamini-Hochberg cho 13 test** — chỉ feature sống sót FDR 10% mới được nói tới.
- Ổn định thời gian: contrast tính riêng IS (2014-19) vs OOS (2020+) **và ex-2021** — feature chỉ
  phân tách nhờ 2021 = loại.
- 1 multivariate check duy nhất: logistic regularized trên 13 feature, walk-forward theo năm, chỉ
  báo AUC trung bình + độ ổn định — KHÔNG tune hyperparameter (mặc định cố định, khai báo trước).
- Cohort đối chứng: cùng phân tích trên DVR/RE_BACKLOG (kênh đang chạy được) — nếu 1 feature phân
  tách ở MOM mà không ở DVR → thông tin cấu trúc; nếu phân tách ở mọi kênh → đó là filter chung
  (ứng viên đưa vào golden floor thay vì rule momentum riêng).

**Phase 2 — chỉ khi CP1 pass:** đóng gói ≤3 candidate rule (pre-registered từ feature sống sót) →
full harness `pt_v23` vs control R3 28.82/1.90/−15.7/1.83, đúng chuẩn: walk-forward IS/OOS,
per-year LOO (kể cả ex-2021), DSR/PBO (CSCV nếu family ≥8), bootstrap tail P(DD<−30%), self-check
0 VND, threads=1, output ra `data/momdeal_exp/` (§8 — không bao giờ đụng filename canonical).

**N-trials ledger (mở từ hôm nay):** N=0 trial backtest. Phase 1 = 13 univariate + 1 multivariate
= khai báo 14 test thống kê (FDR-controlled, không phải trial backtest). Phase 2 dự kiến ≤3 trial
harness — chốt con số chính xác tại CP1, không mở thêm sau đó.

## 6. Checkpoints & go/no-go
| CP | Nội dung | Điều kiện GO | Nếu NO-GO |
|---|---|---|---|
| **CP0** (cuối Phase 0) | Dataset dựng xong: rebuild signal cache (state DT5G + đủ tới hiện tại), join 8L as-of PIT + technical, labels L1/L2, audit no-look-ahead (spot 20 deal bằng tay), N khớp con số khảo sát §2 ±10% | Dataset sạch, coverage 8L tại entry ≥80% episode (nếu <80% → báo user trước khi tiếp) | Sửa data, không sang Phase 1 |
| **CP1** (cuối Phase 1) | Contrast 13 feature + AUC walk-forward | ≥1 feature sống sót FDR 10% **và** giữ dấu ở cả IS/OOS/ex-2021, effect size không tầm thường (\|Cliff's δ\| ≥ 0.15) | **Kết luận "không có pattern tách được"** → khuyến nghị đóng/thu hẹp kênh MOM, dự án dừng ĐÚNG QUY TRÌNH (như fa8l CP2) |
| **CP2** (cuối Phase 2) | ≤3 rule qua full harness | OOS ≥ control (CAGR & Calmar), LOO không âm mọi năm kể cả ex-2021, tail không xấu hơn control, PBO<0.5 | Quay về khuyến nghị CP1-NO-GO hoặc đề xuất hướng khác, chờ user |
| **CP3** | quant-skeptic verify + user sign-off + paper trading | Theo chuẩn chung mọi thay đổi production | — |

Mỗi CP: ghi finding lên bus + cập nhật plan doc này + **DỪNG chờ duyệt** trước khi sang phase sau
(đúng chỉ đạo "tuần tự, chắc chắn từng bước").

## 7. Timeline đề xuất
- **Phase 0**: ~1 ngày làm việc (nặng nhất: rebuild signal cache + join PIT 8L). Có thể bắt đầu
  ngay sau khi user duyệt plan.
- **Phase 1**: ~1 ngày (phân tích thuần pandas trên dataset Phase 0, không harness run).
- **Phase 2**: 1-2 ngày (≤3 harness run + bộ validation đầy đủ, mỗi run ~30-60').
- Không có deadline nghiệp vụ cứng riêng (khác fa_ratings staleness); nhưng nếu CP1-NO-GO dẫn tới
  khuyến nghị đóng kênh MOM thì quyết định đó NÊN có trước rebal quý ~08-05.

## 8. Rủi ro & caveat khai báo trước
1. **N mỏng ở chính kênh cần cứu** (MOM_N 87 episode) — vì vậy đơn vị phân tích là family + cohort
   đối chứng; mọi claim riêng cho MOM_N sẽ nói rõ giới hạn N.
2. **2021 dominance** — LOO/ex-2021 là điều kiện cứng ở cả CP1 lẫn CP2, không phải tùy chọn.
3. **8L coverage lịch sử**: as-of PIT nhưng cần verify độ phủ tại các entry cũ (2014-2019) ở CP0 —
   nếu 8L trống nhiều ở giai đoạn sớm, contrast fundamentals chỉ chạy được trên OOS-era, phải nói rõ.
4. **Survivorship của sổ book**: deal book bị chọn bởi capacity/cash path → label chính là L2
   (signal-level) để tránh bias này; L1 chỉ consistency check.
5. **Label bằng profit_2M có noise exit**: không phản ánh trailing-stop thật — chấp nhận ở Phase 1
   (tìm phân tách thô), Phase 2 harness mới là thước đo thật.
6. Nếu pattern tìm được hóa ra = "liquidity/size floor" (C1) — tức xác nhận giả thuyết quality
   filter ngầm — hành động đúng có thể là **thêm 1 floor vào golden floor chung** thay vì cứu kênh
   momentum riêng; quyết định đó thuộc user tại CP1.

## CP0 — KẾT QUẢ PHASE 0 (2026-07-11/12, job Taylor_20260711_165407) — **VERDICT: GO**

**Scripts**: `mike/agents/Taylor/momdeal/{rebuild_pkl_dt5g.py, momdeal_phase0_build.py, spotcheck_20deals.py}`
**Outputs**: `data/momdeal_exp/{momdeal_episodes_phase0.csv (2.938 rows), momdeal_deals_phase0.csv (519 rows), phase0_report.txt}`

### CP0 gate — cả 3 điều kiện PASS
| Điều kiện | Kết quả |
|---|---|
| Dataset sạch (rebuild + PIT joins + audit no-look-ahead) | ✅ PASS — chi tiết dưới |
| Coverage 8L tại entry ≥80% episode | ✅ **100.0%** MOM_FAMILY (789 ep) · 98.1% ALL (2.938 ep, phần thiếu = 53 ep DVR trước 2014-07-09 là ngày 8L bắt đầu) · 100.0% deals L1 |
| N khớp khảo sát §2 ±10% | ✅ PASS — **CHÍNH XÁC TUYỆT ĐỐI 0% lệch** trên like-for-like (xem dưới) |

### 1. Rebuild signal cache `ba_v11_unified_12y_sig.pkl` — pkl cũ ĐÚNG LÀ bị base-leak
- Nghi ngờ trong plan **xác nhận đúng**: pkl frozen 06-16 built TRƯỚC fix F3 — state5 bên trong là bảng
  BASE `vnindex_5state`. Rebuild bằng pattern F3 (`.replace` sang `vnindex_5state_dt5g_live`, giống
  commit 0537514), END mở rộng 2026-05-15→**2026-07-10**. Backup: `.bak_predt5g_20260711`.
- **Verify state source (gate cứng trong script, abort nếu fail)**: trên 1.085 ngày dt5g≠base (2014+),
  pkl mới khớp dt5g **1.085/1.085, khớp base 0/1.085**. Cửa sổ BULL-giả 06-29→07-09: state5=[3] đúng.
- Registry ghi SAI builder của pkl này (`build_state_free_signals.py` — script đó build bản state-FREE
  khác, chỉ ĐỌC pkl unified làm đối chứng). Builder thật: `build_pkl_v11_current.py` (nay thêm bản DT5G
  `momdeal/rebuild_pkl_dt5g.py`). Đã sửa registry.

### 2. N reconciliation — tách bạch 2 tầng để so đúng like-for-like
Khảo sát §2(b) đo trên pkl base 06-16 → so trên **pkl backup base** (like-for-like): MOM_N **87/87**,
MOM_S **513/513**, MOMENTUM **129/129**, MEGA **10/10**, DVR **1.077/1.077** — khớp chính xác 100%.
Deals từ CSV canonical: MOM_N **77/77**, MOM_S **46/46**, RE_BACKLOG **136/136**, DVR **247/247**;
closed ex-parking 2.259 vs khảo sát 2.258 (lệch 1 = 0,04%; 2.816 tổng closed gồm 557 ETF_PARK/parking).

**Dataset thật (pkl DT5G) — dịch chuyển ĐÃ LƯỜNG TRƯỚC, root cause = đổi nguồn state (đúng mục đích
rebuild) + 1 tháng dữ liệu thêm:** MOM_N 87→**153**, MOM_S 513→**486**, MOMENTUM 129→**136**, MEGA
10→**14**, DVR 1.077→**912**, và MOMENTUM_S_N (twin state-3 của MOM_S, ngoài family pre-registered)
876→**1.237**. Cơ chế: DT5G nhiều ngày NEUTRAL hơn base (DT-gate kẹp cực trị) → tín hiệu dồn từ nhánh
state-4/5 (S) sang nhánh state-3 (N/S_N). Family MOM tổng = **789 episode** (thay vì ~739), N contrast
L2 có label = 786 (343 SUCCESS / 293 FAIL / 150 neutral-band) — đủ N như thiết kế.
S_N được giữ trong CSV với cờ `cohort=DIAG_S_N` (KHÔNG thuộc family, chỉ diagnostic — đưa vào family
hay không là quyết định mở rộng scope, thuộc user, không tự quyết).

### 3. PIT joins + labels
- 8L as-of `eff_date ≤ feature_date` (ASOF duckdb); technical tại ngày signal (episode) / T-1 (deal);
  fundamentals as-of **Release_Date** (không phải quarter-end — chống leak BCTC chưa công bố).
- **Bug bắt được khi build (đã sửa trước khi chốt)**: `profit_2M` đơn vị **PHẦN TRĂM** không phải
  decimal (verify thực nghiệm khớp chính xác `LEAD(Close,40)/Close−1 ×100`; cột này KHÔNG có trong
  `bigquery_dictionary.json` — dictionary thiếu toàn bộ họ `profit_*`). Ngưỡng label L2 đã sửa ≥10.0/≤0.0.
- Linkage deal↔signal: pkl play_type tại T-1 == book play_type **100%** cho cả 4 kênh SIGNAL_V11
  (MOM_N/S/MOMENTUM/DVR; RE_BACKLOG 0% — đúng, RE không phải play_type của SIGNAL_V11, entry từ sleeve RE riêng).

### 4. Audit no-look-ahead (spot-check tay, seed cố định 20260711)
- **20/20 deal PASS + 5/5 episode PASS** qua code path ĐỘC LẬP (pandas thuần per-ticker, không dùng
  ASOF join của builder): tech row ≤ feature_date và là row cuối; 8L đúng row cuối ≤ feature_date và
  row kế tiếp > feature_date; fin Release_Date ≤ feature_date; sig_date < entry_date (mua T+1).
- **1 deal đối chiếu tay với BigQuery LIVE** (không qua cache): PDR_20150306_8 — D_RSI/C_L1M/Res_1Y/8L
  rating/route khớp từng chữ số; điều kiện MOMENTUM_N tự tái lập đúng (ta=166≥155, state5=3, tier C,
  days_since_release=31≤60).

### 5. Bất thường ghi nhận (không chặn GO)
1. Registry sai builder pkl (đã sửa, xem mục 1).
2. `bigquery_dictionary.json` thiếu định nghĩa họ cột `profit_*` (đơn vị %) — nên bổ sung (việc nhỏ, Winston).
3. Composition shift dưới DT5G (mục 2) — Phase 1 PHẢI per-year LOO như đã khai báo; lưu ý thêm: phần
   lớn tăng MOM_N nằm ở era 2020+ (family 2014-19 chỉ 118 ep vs 671 ep 2020+) → contrast IS-era sẽ mỏng,
   đã lường trong caveat §8.3.

**DỪNG theo đúng quy trình — chờ Mike/user duyệt mới sang Phase 1** (contrast 13 feature, FDR 10%,
IS/OOS/ex-2021, 1 logistic walk-forward; không mở thêm trial).

## 9. Việc user cần quyết để bắt đầu
1. Duyệt định nghĩa label (§3 — ngưỡng +10%/0%, L2 chính + L1 check).
2. Duyệt 13 feature pre-registered (§4) — đặc biệt xác nhận: dùng 8L rating/route làm trục
   fundamentals, không dùng fa_tier legacy.
3. Duyệt khung CP0→CP3 (§6) + chấp nhận trước rằng CP1-NO-GO = khuyến nghị đóng/thu hẹp kênh MOM.
