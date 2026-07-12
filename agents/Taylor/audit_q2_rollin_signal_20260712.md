# Audit: rủi ro tầng TÍN HIỆU khi BCTC Q2/2026 roll-in dần dần
Job: Taylor_20260712_121642 · 2026-07-12 · READ-ONLY (không sửa gì) · Taylor

Bối cảnh: MBS công bố Q2 ngày 2026-07-08 (xác nhận trong `earnings_surprise_data.pkl`, mã duy nhất
sau 2026-05-04); các mã khác sẽ roll-in dần tới hạn chót ~07-30. Đây là mùa BCTC LIVE ĐẦU TIÊN của
V2.4 (go-live 07-01) — mùa Q1 kết thúc 05-04, trước go-live.

## R1 — CRITICAL · GAP THẬT: pipeline LAG/PEAD live MÙ với event mới hơn ~30 phiên, entry là T+5

**Cơ chế lỗi (2 mảnh ghép mâu thuẫn nhau):**
1. `refresh_lagged_caches.py` (writer daily của `data/earnings_events_classified.csv`, chạy trong
   `papertrade_daily.sh` 15:30 ICT) chỉ ghi event khi ĐỦ CẢ 4 mốc giá — kể cả `p_p30` = Close tại
   release+30 phiên: `if any(pd.isna(p) for p in [p_pre30, p_m1, p_p5, p_p30]): continue`.
   → Event released hôm nay chỉ xuất hiện trong CSV sau ~30 phiên giao dịch (~6 tuần).
2. `deploy_golive_dt5g_v4/golive_recommend_v23.py` (MONEY-PATH — pipeline 17:30
   `bq_freshness_check.sh` → golive_recommend → DollarBill lập plan) lấy candidate LAG **duy nhất**
   từ CSV này (dòng ~194), entry = release + 5 phiên. Các nhánh code "UPCOMING T+N phiên tới" /
   `entry > LATEST` **không bao giờ fire được** với writer hiện tại — event chỉ vào CSV khi entry
   T+5 đã qua ~25 phiên, và nhánh `lag_recent` (entry trong [LATEST-5d, LATEST]) cũng đã trượt →
   event bị bỏ qua **im lặng, vĩnh viễn**.

**Bằng chứng dữ liệu thật (2026-07-12):**
- `earnings_events_classified.csv`: 51.209 rows, max Release_Date = **2026-05-04**.
- `earnings_surprise_data.pkl` (refresh daily, OK): max Release_Date = **2026-07-08** (MBS 2026Q2,
  NP_R=+36.0%). Duy nhất 1 release sau 05-04 → CSV max 05-04 khớp chính xác giả thuyết "chỉ chứa
  event đủ cửa sổ", không phải do thiếu dữ liệu nguồn.
- `earnings_px.pkl` max time = 2026-07-09 → p_p5/p_p30 của MBS chưa tồn tại → bị `continue`.

**Tác động:** LAG book = 50–65% NAV target theo allocator (w_LAG edge-conditional vừa fix 07-12).
Nếu không sửa trước khi Q2 releases dồn về (~2 tuần nữa), **100% entry LAG mùa Q2 sẽ vắng mặt trong
plan DollarBill** (SpaceX + ZaloPay). "LAG refill cuối tháng 7" (job Taylor_20260704_033932) sẽ
KHÔNG xảy ra qua money-path. Mùa Q1/2026 không lộ vì kết thúc trước go-live; hiện tại **chưa mất
trade nào** (xem R6 — MBS không qualify), còn cửa sổ sửa.

**Hiệu ứng che khuất (quan trọng khi đối soát):** backtest (`pt_v23_audit_2014.py`) và paper
(`pt_v22_dt5g.py`) đọc cùng CSV nhưng là **full-replay** — event cũ ≥30 phiên luôn đủ cửa sổ nên sim
"đã vào lệnh" tại T+5 lịch sử. Paper NAV sẽ hiển thị các deal LAG mà tài khoản live không thể biết
đúng lúc → live-vs-paper diverge trong mùa BCTC và gap này tự ẩn đi sau ~6 tuần. Thông tin thị
trường tại release là public — đây là lỗi PLUMBING (pipeline trễ 30 phiên), không phải lỗi
methodology backtest.

**Tác động phụ:** trigger reverse-unwind của DC-book waterfall paper đọc `golive_v23_status.json`
→ `n_lag_upcoming` (cùng nguồn mù) → mốc review event-anchored "khi LAG refill chu kỳ đầu hoàn tất"
cũng bị lệch nếu không sửa.

**Hướng sửa (KHÔNG làm trong audit này, cần plan + verify riêng):** candidacy LAG chỉ cần
Release_Date + NP_R + lịch sử prior (prior_n_good/pa_HL3 tính từ event CŨ đã đủ cửa sổ) +
surprise_B_MA — tất cả biết được ngay tại ngày release từ `earnings_surprise_data.pkl` (đã fresh
daily). Có thể: (a) nới writer cho phép event mới có rel/post = NaN (giữ nguyên classify cho event
đủ cửa sổ), hoặc (b) golive_recommend sinh schedule trực tiếp từ pkl. Phải giữ nguyên semantics
backtest (chỉ đổi nguồn schedule live).

## R2 — MEDIUM · tradeoff đã document, cần theo dõi: tuần đầu Q2 publish, fa_ratings tier tính trên cohort một phần

`refresh_fa_ratings.py`: quý mới chỉ append khi cohort ≥ MIN_COHORT=30; trước đó consumer as-of
extend tier quý cũ (đúng thiết kế). NHƯNG khi vừa vượt 30 (vd 35 mã cuối tháng 7), tier của các mã
đó tính bằng percentile trên cohort 35 early-filers (thiên lệch cấu trúc: broker/bank công bố sớm)
thay vì ~500+ mã cuối mùa → `SIGNAL_V11` fa_tier gate (AVOID_faE, COMPOUNDER_BUY A/B, MEGA/MOMENTUM
C/D) có thể flip vài mã trong 2–4 tuần roll-in. Cơ chế tự hội tụ: open-quarter re-rank weekly (cron
thứ Bảy 09:15). Điểm cần biết: **backtest R3 dùng bảng frozen full-cohort — live lần đầu tiên chạy
trên chế độ dữ liệu partial-cohort mà backtest chưa từng thấy.** Bounded, không phải bug; ghi nhận
để không hoảng khi thấy tier lạ giữa roll-in.

## R3 — LOW · đã an toàn ở production, latent trap cho research: fa_ratings_8l KHÔNG có cohort gate

`rating_8l_history.py` (cron thứ Bảy 08:30, full-replace): field `rating` 1–5 = scorecard TUYỆT ĐỐI
per-row → miễn nhiễm cohort size. Mọi production consumer đều đọc `rating`: custom30/custom30V gate
`rating_asof<=3` (`custom_basket.py`), golive weak-flag `rating>=4` half-size BEAR/CRISIS,
DC-book double-confirm `rating<=2`. NHƯNG field `tier` của route COMPOUNDER = percentile per-q_time
KHÔNG gate cohort → sau cron 07-18, rows 2026Q2 sẽ có tier rác (cohort n nhỏ). Không consumer
production nào đọc `tier` (nhánh SIGNAL_V11-8L re-tune đã NO-GO) — chỉ cần 1 dòng cảnh báo trong
`data_registry.md` cho research sau này (đề xuất cho Winston, không sửa trong audit).

## R4 — LOW · không có rủi ro trộn cohort ở valuation signal

`SIGNAL_V11` pe_z = (PE − PE_MA5Y)/PE_SD5Y — z-score TỰ THÂN per ticker, không cross-sectional →
mã có EPS Q2 mới so với chính lịch sử 5Y của nó, không so với rổ mixed-vintage. `rating_8l.py`
(screen live) dùng percentile cross-section "latest report per ticker" — mixed vintage trong mùa
roll-in là inherent với mọi point-in-time screen, distortion transient nhỏ, không phải bug và không
nằm trên money-path entry.

## R5 — OK · câu hỏi 4 (race condition cohort 15–29): KHÔNG có

Grep toàn repo: không script nào đọc staging dir `data/fa_ratings_refresh/`; publish = DELETE+INSERT
trong 1 BQ transaction; canonical CSVs chỉ rewrite SAU publish thành công; consumers chỉ đọc bảng BQ
hoặc canonical CSV. Cohort 15–29 → quý đơn giản là chưa tồn tại với mọi consumer. Cron weekly tự
bắt kịp (hạn chót BCTC ~07-30 → cohort nhảy vọt cuối tháng, kỳ vọng publish lần đầu cron 07-25
hoặc 08-01).

## R6 — timeline MBS end-to-end (câu hỏi 3)

- Tầng ingest: ✅ tự động — release 07-08 đã có trong `earnings_surprise_data.pkl` (refresh daily
  papertrade step 0), `ticker_financial` có row time=Release_Date=2026-07-08.
- Gate LAG: MBS **KHÔNG qualify**: NP_R=+36% ≥15 ✓, prior_n_good=23 ≥4 ✓, nhưng **pa_HL3=4.06 < 5 ✗**
  (lịch sử post-release của MBS gần đây toàn âm: 2025Q3 −11.8%, 2025Q4 −9.6%, 2026Q1 −4.8%).
  → Không có trade nào bị miss ở event này, kể cả khi R1 đã fix.
- Timeline giả định nếu qualify: entry T+5 = 2026-07-15, hold 25td → exit ~2026-08-19. Với R1 chưa
  fix, event chỉ vào classified CSV ~2026-08-20 — SAU cả exit → minh họa sống của gap.
- `lag_edge_health.csv`: sẽ tự nối dài khi event Q2 hoàn tất entry+25 phiên (~cuối tháng 8 trở đi) —
  đúng bản chất trailing (khớp kết luận Winston 07-12 "không stale"); không cần can thiệp.

## R7 — tiền lệ mùa trước (câu hỏi 5)

`kb/INCIDENTS.md` không có incident nào thuộc lớp "roll-in dần dần" — backfill incidents bắt đầu
~06-22, mùa Q1 kết thúc 05-04, đều trước go-live 07-01. Mùa Q2 này là mùa BCTC live đầu tiên → mọi
bài học phải phòng ngừa trước (R1) thay vì tra hồi cứu. Chuỗi bài học liên quan duy nhất là
fa_ratings staleness (đã đóng 07-12, cron + freshness check hoạt động).

## Tổng kết ưu tiên
| # | Mức | Kết luận | Hành động đề xuất (chờ Mike/user) |
|---|-----|----------|-----------------------------------|
| R1 | CRITICAL | Gap thật, live chưa từng exercised, ~2 tuần trước khi bị dồn releases | Sửa nguồn schedule LAG live trước ~07-25; quant-skeptic verify; KHÔNG đổi semantics backtest |
| R2 | MEDIUM | Tradeoff có chủ đích, tự hội tụ weekly | Theo dõi tier flip trong 2-4 tuần roll-in; không sửa gì |
| R3 | LOW | Production an toàn (rating tuyệt đối); tier = trap research | 1 dòng note data_registry (Winston) |
| R4 | LOW | Không có rủi ro trộn cohort ở pe_z | Không |
| R5 | OK | Race condition không tồn tại | Không |
