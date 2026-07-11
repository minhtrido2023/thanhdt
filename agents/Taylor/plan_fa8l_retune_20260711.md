# PLAN — Re-tune SIGNAL_V11 bucket logic trên nền fa_ratings_8l (hướng c, ứng viên THAY CORE)
> Job: Taylor_20260711_104100 · Soạn: 2026-07-11 · Trạng thái: CHỜ USER DUYỆT trước khi chạy Phase 1+
> Bối cảnh: user bác drop-in swap (job Taylor_20260711_094714, quant-skeptic CONFIRMED) và chốt hướng (c)
> = thiết kế lại bucket logic cho thang 8L GỐC, không ép map. Đây là plan, KHÔNG phải kết quả.

## 0. Chẩn đoán vì sao drop-in fail (đã đo + 2 probe mới 2026-07-11, feasibility-level)

1. **Khác semantics thang đo.** Legacy `fa_ratings.tier` = per-quarter percentile của composite score
   có CẢ valuation + growth (cột `score_valuation`, `score_growth` trong bảng) → "C/D" nghĩa là
   mid-composite, đúng chất liệu momentum-candidate. 8L `rating` 1–5 = trục durability /
   permanent-capital-impairment THUẦN (spec `rating_8l.py` ghi rõ "NOT a buy signal"), value nằm ở
   axis 2 riêng (screener). Ép 1–5 → A–E chỉ giữ 33–38% overlap là hệ quả tất yếu, không phải lỗi map.
2. **Universe/NULL-shift ngầm (probe coverage mới).** Legacy chỉ phủ **144–518 mã/năm**; 8L phủ
   **655–1281 mã/năm** → as-of coverage trên prune rows ≈ **99%**. Dưới legacy, đa số mã có
   `fa_tier=NULL` → rơi qua nhánh generic (MOMENTUM_S/A/PASS), KHÔNG bị `AVOID_faE`. Dưới 8L, nhánh
   NULL gần như biến mất + E-gate chặn thêm hàng trăm mã. Drop-in test đã conflate 2 hiệu ứng
   (đổi thang + đổi coverage) — plan này phải tách ra đo riêng.
3. **Probe IC nhanh** (monthly-sampled, fwd 2M profit_2M, prune universe, as-of join — CHƯA phải kết
   quả cuối): spearman(rating, fwd) yếu −0.03..−0.05; mean fwd theo rating KHÔNG monotonic (rating 2≈3
   thường > 1; rating 5 nhiễu); hit-rate OOS momentum-ctx monotonic nhẹ **55.8% (r1) → 47.5% (r4)**.
   Khớp tri thức đã pin: "8L rating = binary gate ≤3, KHÔNG phải return-tilt". → Hướng redesign: dùng
   rating làm **GATE** + `route` làm sector-adjust; KHÔNG tái tạo semantics C/D-momentum từ rating.

## 1. Inventory điểm chạm fa_tier (phải có design decision cho TỪNG cái)

| # | Điểm chạm | Logic hiện tại (legacy A–E) |
|---|---|---|
| T1 | `AVOID_faE` | `fa_tier='E'` → loại tuyệt đối |
| T2 | MEGA / MOMENTUM / MOMENTUM_N | `fa_tier IN ('C','D')` + ta≥170/155 |
| T3 | MOMENTUM_QUALITY | `fa_tier IN ('A','B')` + ta≥155 |
| T4 | COMPOUNDER_BUY | `A/B` + pe_z<−0.5 + ta≥95 + NOT warn_ext |
| T5 | DEEP_VALUE_RECOVERY | `C` + ta≥100 + growth>20% |
| T6 | COMPOUNDER_HOLD / WAIT | `A/B` + dải ta thấp |
| T7 | ta-adjust ICB8 | ICB8 & D → +10; ICB8 & A → −10 |
| T8 | pt_v23 D1 CTE (`pt_v23_audit_2014.py:564`) | `adv_yoy>0.5 & tier C/D` |
| T9 | custompitg/q basket tilt | ĐÃ dùng fa_ratings_8l sẵn — không đổi |

Nguồn dữ liệu (tra data_registry xong): dùng `tav2_bq.fa_ratings_8l` cột **`rating` (1–5) + `route`**;
cột `tier` của bảng 8L là panel A–E built-for-purpose KHÁC spec — chỉ dùng làm 1 biến thể đối chứng
trong family, không phải mặc định. KHÔNG join `data/rating_8l.csv` (snapshot hôm nay) vào quá khứ.

## 2. Các Phase

### Phase 0 — Foundation & attribution (KHÔNG đốt trial selection) — ~1.5 ngày (07-13 → 07-14)
- **0a** Grep toàn codebase mọi consumer fa_ratings còn lại ngoài bảng trên (hoàn thiện inventory).
- **0b Attribution ladder** cho drop-in fail: chạy 2 run DIAGNOSTIC trên harness pin — (i) tier8l
  nhưng **mask NULL ngoài footprint legacy** (đổi thang, giữ coverage cũ); (ii) legacy tier + chỉ mở
  E-gate/NULL theo coverage 8L ở mức có thể. Mục đích: tách degradation "do thang" vs "do universe
  shift". Đếm vào N tổng (minh bạch) nhưng không phải candidate.
- **0c IC/hit-rate đầy đủ theo context** (thay probe nhanh): per bucket-context thật (ta≥170/155/140/
  125 × state5 × route), fwd 2W/1M/2M/3M, IS/OOS tách, cho cả `rating`, `route`, và `tier` 8L.
  Descriptive stats làm nền chọn ngưỡng — không phải selection trên backtest metric.
- **0d PIT audit fa_ratings_8l**: xác nhận eff_date không look-ahead (rating tại eff chỉ dùng BCTC đã
  công bố; forensic override append-at-flag-date đã đúng chuẩn theo registry); check warm-up gap
  (8L bắt đầu 2014-07-09, audit bắt đầu 2014-01) và định nghĩa policy NULL đầu kỳ.
- **GO/NO-GO CP0**: nếu 0c cho thấy rating 8L không có separation dùng được trong BẤT KỲ context nào
  (IC ~0 cả IS+OOS, hit-rate flat) → DỪNG SỚM, khuyến nghị fallback, không đốt trial vô ích.

### Phase 1 — Pre-registered candidate family + proxy prune — ~2 ngày (07-15 → 07-17)
- **Pre-register family TRƯỚC khi chạy** (trình Mike/user duyệt danh sách 07-15). Trục thiết kế
  (ngưỡng cuối chỉnh theo 0c, nguyên tắc: rating=gate, route=sector-adjust):
  - T1 avoid-gate: {rating=5} vs {rating≥4} vs {rating≥4 có điều kiện route}
  - T4/T6 compounder: rating≤2 (khớp precedent DC-book double-confirm ≤2) vs ≤3
  - T2/T3 momentum: **bỏ hẳn điều kiện tier** (ta-only + avoid-gate) vs rating 3–4 làm proxy
  - T7 ta-adjust: thay ICB8×tier bằng route BANK/SECURITIES × rating vs **drop hẳn**
  - T5: giữ bằng rating=3 + growth vs gộp vào nhánh momentum
  - T8 D1: mirror quyết định T2
  Family cap **≤12 config** có lý thuyết đứng sau (không grid 2^k mù). **N khai báo = 12 + 2
  diagnostic (0b) + 2 drop-in đã chạy (094714) = 16 trials cùng họ.**
- Proxy evaluation (signal-level composition + fwd-return của signal set, light sim nếu cần) →
  prune còn 2–3 finalist. Mọi config đo đều đếm N.
- **GO/NO-GO CP1**: ≥1 candidate proxy-OOS ≥ control legacy → tiếp; không → NO-GO kèm evidence.

### Phase 2 — Full-harness validation finalists (2–3 config) — ~1.5-2 ngày (07-18 → 07-21)
- `pt_v23_audit` 50B, **ĐÚNG lệnh pin R3** (`$DNA_PYEXE`, threads=1, BQ_CACHE_THREADS=1,
  NAV_TOTAL_B=50, ETF_LIQ=custompitg, BASKET_WT=namecap, BASKET_SELECT=yieldcombo, PARK_STATES="3:0.7",
  AUDIT_END pinned), **OUT_CSV riêng theo guidelines §8** (`data/fa8l_exp/*_retune_probe_*`),
  self-check 0 VND + byte-reproducibility 2 process độc lập.
- Đánh giá vs baseline R3 MỚI **28.82% / 1.90 / −15.7% / 1.83** (OOS 31.59%): Full + IS/OOS +
  per-year LOO + bootstrap tail (5th-pct CAGR, MaxDD, P(DD<−30%)) + DSR (N=16) + PBO CSCV (family ≥8).
- **GO/NO-GO CP2 (tiêu chí wire, cứng, khai báo trước):**
  1. OOS CAGR ≥ baseline-OOS − 0.5pp **và** OOS Calmar ≥ baseline-OOS Calmar;
  2. per-year LOO: edge KHÔNG âm khi bỏ bất kỳ năm nào (bài học 094714 + H8a);
  3. tail không xấu hơn: P(DD<−30%) ≤ baseline + 0.5pp;
  4. PBO < 0.5;
  5. edge không đảo dấu dưới CẢ 2 universe-policy (footprint legacy vs full 8L coverage).
  Fail bất kỳ điều nào → NO-GO → fallback (giữ fa_ratings static + xử lý staleness riêng, hoặc
  hybrid E-gate-only, hoặc rebuild legacy builder — trình user chọn).

### Phase 3 — Skeptic + user + deployment — ~1 ngày effort + thời gian skeptic/user (07-22 → 07-25)
- quant-skeptic verify (Mike dispatch) + sensitivity ±1 step quanh mọi ngưỡng chọn (yêu cầu plateau,
  bác đỉnh nhọn).
- User sign-off. Nếu GO: cutover theo **data_registry mục 5** (3 bước obsolete-marking CÙNG commit),
  sửa `signal_v11_sql.py` + D1 + re-pin baseline mới + **dual-run paper diff** trên
  golive_recommend/pt_v4/pt_v22 ~1–2 tuần trước khi flip live.

## 3. Timeline vs deadline nghiệp vụ
Deadline thật: BCTC Q2/2026 về ~cuối 07 (fa_ratings static ngày càng sai) + rebal quý ~08-05.
- 07-13→14 Phase 0 · 07-15 duyệt family · 07-15→17 Phase 1 · 07-18→21 Phase 2 · 07-22→25 skeptic+user.
- Nếu GO: dual-run paper từ ~07-27, flip khi sạch. Chấp nhận fa_ratings static thêm 1–2 tuần đầu mùa
  BCTC (rủi ro đã biết); interim option nếu user muốn: hybrid E-gate-only.
- Slip guard: CP0/CP1 NO-GO → báo ngay, còn ~2 tuần cho user chọn fallback trước 08-05.

## 4. Phụ thuộc & rủi ro chính
1. **Winston auto-refresh fa_ratings_8l** (Mike dispatch song song): backtest validation KHÔNG bị chặn
   (AUDIT_END 06-19 < MAX(time) 06-28 của bảng) nhưng **KHÔNG wire production khi bảng còn refresh
   tay** — validation ≠ production reality nếu rating stale sau mùa BCTC. Điều kiện wire bắt buộc.
2. **Confounder coverage/universe** — first-order risk; xử bằng 0b attribution ladder + CP2 điều kiện 5.
3. **Semantics risk**: 8L rating là durability gate — có khả năng THẬT là không tồn tại bucket-mapping
   tốt cho momentum plays → kết quả trung thực có thể là "gate-only" hoặc NO-GO. Plan cho phép kết
   luận đó; không ép ra GO.
4. **Multiple-testing**: N=16 khai báo trước, DSR/PBO/LOO bắt buộc, proxy prune vẫn đếm trial.
5. **PIT risk bảng 8L** (0d): nếu phát hiện look-ahead trong eff_date → mọi số làm lại sau khi sửa bảng.
6. **Republish drift**: bảng 8L republish làm as-of lệch nhẹ (registry đã ghi) → pin snapshot input
   (parquet cache ngày cố định) cho MỌI run trong dự án, so sánh nội bộ nhất quán.

## 5. Phase 0 — KẾT QUẢ (2026-07-11, jobs Taylor_20260711_114557 + _121933) — **CP0 = GO**

### 0a — Inventory consumer fa_ratings (hoàn chỉnh, verified bằng grep toàn codebase + crontab)
Kiến trúc TỐT HƠN lo ngại — bucket logic T1–T7 chỉ có **1 nguồn**:
- **Nhóm A (bucket T1–T7, single-source)**: `signal_v11_sql.py::SIGNAL_V11` — TẤT CẢ consumer chính
  đều `import` (golive_recommend_v23, pt_v4_dt5g, pt_v22_dt5g, pt_v23_audit_2014, pt_v11_tq34b,
  pt_v12_macro). Retune T1–T7 = sửa đúng 1 file.
- **Nhóm B (D1 CTE / T8 `adv_yoy>0.5 & tier C/D → RE_BACKLOG_BUY`, COPY INLINE — phải vá CÙNG COMMIT
  hoặc extract về signal_v11_sql khi cutover, bài học base-leak §9)**: 6 copy active =
  `pt_v23_audit_2014.py:563` · `golive_recommend_v23.py:86` (LIVE money-path) · `pt_v4_dt5g.py:194` ·
  `pt_v22_dt5g.py:246` (sổ tín hiệu prod) · `pt_v11_tq34b.py:196` · `pt_v12_macro.py:148` (2 paper A/B
  step [7]/[8] còn chạy). +2 KHÔNG active: `pt_dt4_vs_tq34b_ab.py:175` (step [18] retired),
  `sim_v11_live_window.py:175` (ad-hoc). **Khuyến nghị cutover: extract D1 CTE thành constant chung
  trong signal_v11_sql.py** thay vì vá 6 chỗ.
- **Nhóm C (tool ad-hoc, logic riêng, KHÔNG trong cron nào — verified 0 call-site)**:
  `recommend_tomorrow.py` (T7-style ICB8×tier adjust dòng 76–77), `ta_score_daily.py` (dùng cả cột
  `total_score` của fa_ratings — **cột này cần check tồn tại trong fa_ratings_8l ở Phase 1**, nếu
  không có thì tool này freeze-legacy). Ưu tiên thấp, quyết định khi cutover.
- **Nhóm D (infra, không cần đổi logic)**: `sync_bq_cache.py` (mirror CẢ 2 bảng — giữ mirror legacy
  đến hết transition), `mike/bin/bq_freshness_check.sh` (đã WARN-only fa_ratings_8l lastModified≤9d),
  `mike/bin/refresh_fa_ratings_8l.sh` (**cron weekly Sat 08:30 ICT ĐÃ CÀI — commit dd7feb9, user
  approved 2026-07-11 → phụ thuộc #1 mục 4 ĐÃ GIẢI QUYẾT**, run schedule đầu tiên Sat 07-18).
- Còn lại (~180 file match) = research/screen/archive, không phải production consumer.

### 0b — Attribution ladder (2 run DIAGNOSTIC full-harness pin R3, dt5g_live, KHÔNG đốt candidate)
| run | thang | coverage | FULL CAGR/Sh/DD/Calmar | OOS CAGR/Calmar |
|---|---|---|---|---|
| control legacy | legacy | legacy | 28.82%/1.83/−15.7/1.83 | 31.59%/2.01 |
| diag_maskleg | **8L** | legacy | 26.53%/1.69/−17.7/1.50 | 27.25%/1.54 |
| diag_legcov8l | legacy | **8L (COALESCE)** | 29.70%/1.88/−15.8/1.89 | 32.94%/2.09 |
| tier8l drop-in | 8L | 8L | 27.15%/1.73/−17.7/1.53 | 28.04%/1.59 |

**Kết luận attribution**: degradation drop-in = **hiệu ứng THANG ĐO** (scale −2.29pp FULL / −4.34pp
OOS / OOS-Calmar −0.47); **coverage 8L thực ra DƯƠNG** (+0.88pp FULL / +1.34pp OOS / Calmar +0.08).
Xấp xỉ cộng tính (interaction −0.26pp). Per-year: maskleg thua đậm đúng các năm bull-momentum
(2020 −9.1 / 2021 −9.0 / 2025 −15.2pp) — khớp chẩn đoán semantics (C/D-momentum không tái tạo được
từ trục durability). Caveat: edge coverage dồn 2021 (+22.4pp) — coverage không phải candidate độc
lập, chỉ là design input. **Hàm ý thiết kế Phase 1: giữ FULL coverage 8L (bỏ lo NULL-branch), toàn
bộ effort đổ vào redesign bucket theo hướng rating=GATE.** Script: `data/fa8l_exp/
fa8l_diag_compare_0b_20260711.py`, CSV `v23_fa8l_diag_{maskleg,legcov8l}_20260711.csv`.

### 0c — IC/hit-rate theo context (512 cells, 142.6k obs BQ thật, weekly-sampled, IS/OOS tách)
rating8l CÓ separation thật, context-dependent: bull-momentum ctx IC âm nhất quán IS+OOS (ta140_s45
OOS −0.066..−0.111; hit r1 69.7%/r2 74.8% vs r5 48.0% @profit_2M) + compounder ctx (−0.04..−0.05);
NEUTRAL momentum FLIP DẤU (+0.10 OOS ta140_s3) → gate phải context/route-conditional, không phải
tilt toàn cục. File: `data/fa8l_exp/ic_context_8l_20260711.csv` + `run_0c_ic_20260711.log`.

### 0d — PIT audit fa_ratings_8l: SẠCH (0 dup, 87.7% khớp Release_Date, 10.7% fiscal+45, 0 gap âm,
879 rows republish-drift → xử bằng pin snapshot input, mục 4.6).

### Verdict CP0 (theo tiêu chí khai báo trước, không nới): **GO**
Điều kiện DỪNG-SỚM ("IC ~0 cả IS+OOS mọi context, hit-rate flat") KHÔNG xảy ra — separation tồn tại
và nhất quán IS+OOS ở các context cụ thể. N-ledger sau Phase 0: 2 drop-in (đã bác) + 2 diagnostic
(0b) = 4/16 trial đã dùng; còn 12 slot cho family Phase 1 như khai báo.

### Ghi chú môi trường (cho Mike báo user, ngoài phạm vi Phase 0)
Headless session (Taylor dispatch) auth = `dtienthanh@gmail.com` (owner, CÓ quyền ghi BQ) ≠ phiên
interactive Mike (service account `bq-reader-8l`, READ-ONLY — lý do Mike test tay
refresh_fa_ratings_8l.sh bị Access Denied). CHƯA rõ cron weekly (chạy độc lập cả 2 phiên) dùng
identity nào — cần xác nhận trước/sau run đầu tiên Sat 07-18 08:30 ICT.
