# PLAN — Phân tích deal thành công lịch sử của book Momentum → tìm pattern thật
> Taylor, 2026-07-11 · job Taylor_20260711_163023 · trạng thái: **DRAFT chờ user duyệt** (chưa chạy Phase 0)
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

## 9. Việc user cần quyết để bắt đầu
1. Duyệt định nghĩa label (§3 — ngưỡng +10%/0%, L2 chính + L1 check).
2. Duyệt 13 feature pre-registered (§4) — đặc biệt xác nhận: dùng 8L rating/route làm trục
   fundamentals, không dùng fa_tier legacy.
3. Duyệt khung CP0→CP3 (§6) + chấp nhận trước rằng CP1-NO-GO = khuyến nghị đóng/thu hẹp kênh MOM.
