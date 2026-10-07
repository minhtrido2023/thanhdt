---
kind: config
status: CANONICAL-PROXY (single-anchor, bootstrapped 2026-10-01)
source: cctg_rate_vn.py (CCTG_EVENTS + data/cctg_rate_vn_events.csv append-only)
group: macro
role: DISPLAY-ONLY input (kill-switch A, Value Radar — ĐỌC THẲNG effective_deposit_rate()/CCTG,
  KHÔNG qua knob dưới đây) PLUS, từ 2026-10-01 (job Taylor_20261001_054110, user-approved), LIVE
  qua deposit_rate_vn.consumer_deposit_rate() vào ĐÚNG 5 consumer: rating_8l.py NEUTRAL tilt +
  chuỗi DCF (dcf_valuation/dcf_refresh_gate/custom30_yield_labels/due_diligence). Rollback knob:
  env DEPOSIT_RATE_CCTG_OVERLAY=0 tắt cả 5 — nhưng KHÔNG phải "1 từ" ở MỌI launch context, xem
  bẫy #6.
writer: 1 mốc frozen 2026-10-01 (job Taylor_20261001_032954) + CSV append-only cho mốc tương lai
verified_by: Taylor, job Taylor_20261001_032954 (kill-switch A) + Taylor_20261001_054110 +
  Taylor_20261001_064225 round-2 + Taylor_20261001_073836 round-4 (arch-review r2 follow-up:
  selfcheck path-trap fix + M15 mutant-kill + doc inventory corrections + FV delta table
  re-reproduced byte-identical, branch wire/deposit-rate-wire-rating-dcf-20261001, code đã merge
  main qua commit d87a6f89 — doc này đã áp vào registry 2026-10-01 bởi Mike, §13)
---

# `cctg_rate_vn.py` — Big-4 CHỨNG CHỈ TIỀN GỬI (CCTG), kỳ hạn 6 tháng

**Status: CANONICAL-PROXY, single anchor.** Series MỚI, tách biệt hoàn toàn khỏi
`deposit_rate_vn.py` (Big-4 12M term-deposit, [[deposit_rate_vn]]) — không ghi đè, không gộp,
không restate lịch sử.

## Là gì
Lãi suất CCTG nhóm Big-4 (VCB/BIDV/CTG/Agribank), kỳ hạn **6 tháng** — KHÁC kỳ hạn với chuỗi
12M đang dùng, một dấu hiệu cần giữ nguyên khi hiển thị (đường cong đảo khi 6M > 12M là tín hiệu
thị trường thật, không phải lỗi).

## Dữ liệu
Mốc duy nhất: `2026-09-30, 7.5%` — nguồn VietnamNet 30/09/2026 (nhóm Big-4; một số NH cổ phần tới
9,4% nhưng NGOÀI phạm vi chuỗi này, giữ nhất quán Big-4-only với `deposit_rate_vn.py`).

## Pháp lý (nguồn thứ cấp, CHƯA re-verify độc lập bởi legal-vn session riêng)
CCTG ≈ tiết kiệm về bảo hiểm tiền gửi (Luật 111/2025, hạn mức 350 triệu VND), lãi miễn thuế TNCN,
lãi suất kỳ hạn ≥6 tháng do thị trường quyết định (không trần SBV). Đây là tóm tắt do user relay
2026-10-01, CHƯA được legal-vn agent độc lập xác nhận trong phiên này — re-verify trước khi trích
dẫn trong tài liệu gửi khách hàng.

## Cơ chế kết hợp
`deposit_rate_vn.effective_deposit_rate(asof, check_freshness=...)` = max(Big-4 12M, CCTG 6M)
**CHỈ KHI** CCTG fresh (ngưỡng 45 ngày) và trong khoảng hợp lệ [0.5%, 30%] — không bao giờ lấy
trung bình, không bao giờ để CCTG lấn Big-4 khi CCTG đang stale/thiếu. Trước 2026-09-30,
`current_cctg_rate()` trả `None` cho mọi asof ⇒ mọi backtest pin trước ngày này **byte-identical**
với thế giới chưa có module này.

⚠️ **"Fresh" là PIT-CAUSAL theo `asof` được truyền vào, không phải theo giờ hệ thống** — và điều
này chỉ ĐÚNG ĐỒNG LOẠT cho cả 5 consumer kể từ round-2 fix (2026-10-01, job
Taylor_20261001_064225, R1 BLOCKING). Trước fix: `effective_deposit_rate()`'s `check_freshness`
mặc định `asof is None`, nên 3 consumer gọi với `asof` tường minh (`dcf_valuation.discount_rate`,
`dcf_refresh_gate`'s drift monitor, `custom30_yield_labels` qua `dep_cache`) **không bao giờ**
coi CCTG là cũ — chỉ `rating_8l.py` (gọi không truyền `asof`) mới thực sự được age-out. Đo thật:
`consumer_deposit_rate('2026-11-16')` bản cũ trả 7,5 (CCTG chưa bao giờ hết hạn) trong khi
`effective_deposit_rate('2026-11-16', check_freshness=True)` tính đúng đã trả 6,8 (Big-4-only) —
mốc chuyển tươi→cũ thật là **2026-11-15** (anchor 2026-09-30 + 46 ngày). Nay cả 5 consumer gọi
qua `consumer_deposit_rate_detail()` luôn truyền `check_freshness=True` tường minh, PIT-causal
theo `asof`.

`macro_killswitch_a_status()` (`deposit_rate_vn.py`) đã wire overlay này — hôm nay (2026-10-01,
asof production với CSV thật) effective=7,5% (CCTG đang là driver), trigger `>` 7,5% strict ⇒
**CLEAR đúng ngưỡng** (không armed). Lưu ý: trong worktree R&D (`wt-depgate75-1001`) CSV Big-4 thật
bị `.gitignore` ẩn nên gọi không-asof trả stale=True — đây là giới hạn môi trường worktree, KHÔNG
phải bug; production đọc đúng CSV thật (`data/deposit_rate_vn_events.csv`, mốc 2026-09-04) sẽ
không stale.

## Kiểm kê consumer `current_deposit_rate()`/`merge_deposit()` + quyết định wiring (2026-10-01)

| Consumer | File | Loại | Quyết định |
|---|---|---|---|
| Kill-switch A (`macro_kill_switches.A_sbv_rate_suspend`) | `deposit_rate_vn.py::macro_killswitch_a_status` | DISPLAY + kill-switch, KHÔNG sizing/order (sleeve nó gate là PROPOSED/paper) | **WIRED** 2026-10-01 |
| Value Radar | `value_radar.py` | DISPLAY-ONLY (CLAUDE.md §6b — không phải tín hiệu mua/bán) | **WIRED** 2026-10-01 |
| `rating_8l.py` NEUTRAL-only deposit tilt | `rating_8l.py:881-885` | **LIVE daily** (±0.03 trên `value_score_v3`, chạy `pt_8l_daily.sh` **19:20 ICT** — đổi từ 17:45 ngày 2026-07-15, xem crontab comment — validated 2026-06-19) | **WIRED 2026-10-01** (job Taylor_20261001_054110, round-2 fix job Taylor_20261001_064225, qua `consumer_deposit_rate_detail()` — print line giờ kèm driver) — bảng diff THỰC ĐO ở dưới |
| `trading_bot/due_diligence.py` YIELD_FLOOR (`_yield_floor()`) | fear-buy backstop sleeve, live QUALIFY/NON cho BUY order bị flag | **LIVE DAILY** (round-4 fix, job Taylor_20261001_073836, arch-review r2: bảng cũ "dispatch headless không cron" SAI). 3 call site hàng ngày: `deploy_golive_dt5g_v4/golive_recommend_v23.py:1183` (`run_due_diligence`, mắt xích pipeline 19:00-19:03), `mike/bin/send_plan_report.sh:~792/~802` (21:00, cùng `run_due_diligence`, hiển thị cho user duyệt plan), `mike/bin/eod_trading_report.sh:~377-388` (19:10, cùng hàm) | **WIRED 2026-10-01**, round-2 fix (job Taylor_20261001_064225) — giờ gọi CHUNG `consumer_deposit_rate_detail()` thay vì tự lặp logic đọc knob (bản cũ lặp logic chính là nguồn bug R1 riêng của site này); giữ `rate_source` driver thật trong field `deposit_rate_source`, không gộp mù |
| `custom30_yield_labels.py` | batch-equivalent của `_yield_floor()` (đã verify khớp 120/120, job Taylor_20260818_131745). **LIVE DAILY** (round-4 fix, job Taylor_20261001_073836: bảng cũ "ad hoc/dispatch, KHÔNG có cron riêng" SAI) — `papertrade_daily.sh` step `[6] custom30_history` chạy **15:30 ICT T2-T6** (`kb/cron_registry.md`), import `custom30_yield_labels` và ghi cột `yield_floor_note` vào BQ `tav2_bq.custom30v_8l` | Phải đi CÙNG với due_diligence.py để giữ bất biến khớp-số | **WIRED 2026-10-01** — qua `consumer_deposit_rate()`, cùng chuỗi với due_diligence.py |
| `dcf_valuation.py` (discount rate r = Big-4+CCTG effective + ERP; hàm `fair_value()`) | feeds `due_diligence.py` fear-buy DCF leg + research, **VÀ** 2 call site hiển thị-cho-user mỗi ngày: `mike/bin/send_plan_report.sh:~780` (`_dcf_check_for_order`, 21:00 plan report user duyệt — flag CHEAP/RICH, buộc `dcf_override_reason` khi RICH trước khi duyệt BUY) + `mike/bin/eod_trading_report.sh:~360` (cùng hàm, 19:10 EOD report); executor còn tự bắn event `finding/dcf-rich-fill` (`trading_bot/executor.py:1225`) khi 1 BUY fill ở mã đang RICH theo DCF — round-4 bổ sung (job Taylor_20261001_073836, arch-review r2: bảng cũ thiếu hẳn 2 call site này, đây là consumer DCF **user-visible nhất**, không phải chỉ feed due_diligence) | **LIVE** (3 đường: due_diligence chain + 2 report trên + executor event) | **WIRED 2026-10-01** — qua `consumer_deposit_rate()` |
| `dcf_refresh_gate.py` | giám sát drift cho chain DCF ở trên, cron **08:10 ICT ngày 11 hàng tháng** (`cd WorkingClaude && /home/trido/thanhdt/wc_venv/bin/python dcf_refresh_gate.py` — chạy python TRỰC TIẾP, **KHÔNG `source wc_env.sh`**, xem bẫy #6) | Cùng chain DCF | **WIRED 2026-10-01** — qua `consumer_deposit_rate()`, phải khớp 1:1 với `dcf_valuation.py` để delta-vs-last-used-rate không lệch |
| `dcf_rate_robustness.py` | robustness probe: hindsight bias của chuỗi Big-4 LỊCH SỬ (2014-2026 window-mean, monkeypatch `discount_rate`) | KHÔNG đọc rate "hiện tại" — chỉ đọc `deposit_events_df()` lịch sử | **KHÔNG WIRE** (cố ý — khác mục đích với 5 consumer trên, không phải sót) |
| `deploy_golive_dt5g_v4/golive_recommend_v23.py:991` (`_pit_deposit_rate`, cổng `capit_margin_lever`, ngưỡng `CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD=9.0`) | **LIVE daily** — mắt xích pipeline 19:00-19:03 ICT (`publish_gated_state.py` rồi file này, xem `trading_bot/plan.py:1047`), gate margin thật trên sleeve CAPIT (`enabled=true`, user confirmed 2026-08-22) | Dùng `deposit_rate_vn.merge_deposit()` — Big-4-ONLY | **NGOẠI LỆ CÓ CHỦ Ý, CHƯA WIRE** — khác hẳn `macro_confidence_regime.py`/research bên dưới (đó KHÔNG sống lặp lại); đây là consumer tiền thật mỗi ngày. KHÔNG tự wire trong job này — bề mặt chạm margin thật, cần user quyết riêng (so với các cổng hiển thị/backtest, một thay đổi ở ngưỡng 9,0% có thể đổi hành vi vay margin thật) |
| `macro_confidence_regime.py` | RESEARCH/DISPLAY-ONLY, chạy một lần, "writes nothing to production paths" (tự khai trong docstring) | Không phải consumer sống lặp lại | Ngoài phạm vi — không cần quyết |
| `append_deposit_rate.py`, các `pt_v23_*`/`probe_*`/`backtest_*`/`engine_*` research | công cụ ghi chuỗi Big-4 / backtest lịch sử điểm-trong-thời-gian | Không phải consumer sống lặp lại | Ngoài phạm vi — không cần quyết |

### Diff THỰC ĐO sau khi wire (2026-10-01) — bản SỬA LẠI (round-2 fix, job Taylor_20261001_064225)
**Bảng gốc dưới job Taylor_20261001_054110 dùng 108 mã + báo 2 zone flip — KHÔNG tái lập được**:
quant-skeptic chạy thật `rating_8l.py` 2 lần (knob=0 vs knob=1) ra file tạm, baseline khớp
**TUYỆT ĐỐI** (md5 giống hệt) với file LIVE trên đĩa ngày 30/09 (`data/rating_8l_screener.csv`,
**102 mã**, không phải 108) — Mike tự chạy lại diff từ 2 file tạm đó (`/tmp/qs_8l_0`,
`/tmp/qs_8l_1`, cả hai 102 dòng) và xác nhận số của quant-skeptic đúng. Bảng dưới đây = số đã
verify lại, thay thế hoàn toàn bảng cũ.

Deposit hôm đo (2026-09-30): Big-4-only 6,8% vs effective 7,5% (CCTG driver), delta **+0,7pp**.

**rating_8l.py NEUTRAL tilt** — **102 mã scored, đúng 6 mã đổi `value_score_v3`** (tất cả
DOWNGRADE đúng −0,03, KHÔNG có mã nào upgrade — khớp lý thuyết: deposit tăng → hurdle tăng → chỉ
siết, không nới). Cột `zone` = zone hiển thị chính (cột `zone` trong screener, KHÔNG phải
`zone_v2` percentile-rank nội bộ):

| ticker | v3 Big-4 | v3 effective | value_pct Big-4 | value_pct effective | zone Big-4 | zone effective |
|---|---|---|---|---|---|---|
| CTR | 0.653 | 0.623 | 0.535 | 0.505 | 1_BUY-NOW | 1_BUY-NOW (không đổi zone) |
| MZG | 0.607 | 0.577 | 0.475 | 0.444 | 2_ACCUMULATE | 2_ACCUMULATE |
| QNS | 0.538 | 0.508 | 0.354 | 0.313 | 2_ACCUMULATE | 2_ACCUMULATE |
| PLX | 0.532 | 0.502 | 0.343 | 0.303 | 2_ACCUMULATE | 2_ACCUMULATE (cách ngưỡng 0,30 đúng 0,003 — SÁT nhưng KHÔNG flip) |
| HVN | 0.490 | 0.460 | 0.283 | 0.247 | 3_WATCH-RICH | 3_WATCH-RICH (HVN = BANNED ticker vĩnh viễn, không ảnh hưởng thực thi) |
| GEE | 0.364 | 0.334 | 0.162 | 0.141 | 3_WATCH-RICH | 3_WATCH-RICH |

**KHÔNG có zone flip nào** (bảng cũ báo PLX flip 2_ACCUMULATE→3_WATCH-RICH là SAI — zone của PLX
không đổi ở cả 2 bảng gốc lẫn re-verify). `DPM` (CYCLICAL) cũng được kiểm tra riêng vì có rank
ripple: `value_score_v3` KHÔNG đổi (0.515→0.515, DPM không nằm trong 6 mã bị tilt), nhưng
`value_pct` nhích 0.303→0.323 (rank ripple thuần do PLX/5 mã kia tụt hạng) — **vẫn `2_ACCUMULATE`
ở cả hai**, không flip. Không mã nào rời/vào top30 hay buynow
(`rating_8l_top30.csv`/`rating_8l_buynow.csv` knob=0 vs knob=1: giống hệt tuyệt đối theo ticker
set). Không mã nào trong 6 mã bị tilt đang là vị thế nắm giữ của SpaceX/ZaloPay.

**DCF chain** — discount rate 13,30%→14,00% (+0,70pp đúng bằng spread CCTG−Big4, test trực tiếp
`dcf_valuation.discount_rate()`). Fair-value/share, 5 mã mẫu (DGC/TV1 = sleeve discretionary +
VNM/FPT/MWG đối chứng; HPG bị gate CF_OA<0, không áp dụng):

| ticker | FV Big-4 (VND) | FV effective (VND) | delta |
|---|---|---|---|
| DGC | 76,501 | 75,942 | −0.73% |
| TV1 | 130,537 | 129,375 | −0.89% |
| VNM | 60,984 | 60,477 | −0.83% |
| FPT | 79,333 | 78,627 | −0.89% |
| MWG | 79,386 | 78,679 | −0.89% |

Đồng nhất, nhỏ (−0,7 đến −0,9%) — margin-of-safety (giá thị trường thật so với FV) KHÔNG đổi dấu
cho DGC/TV1 ở delta nhỏ này; mẫu đối chứng gần biên nhất là **VNM, MoS +2,6%→+1,8%** (vẫn dương,
không flip QUALIFY→NON). Đưa số FV delta này làm INPUT cho verdict QUALIFY/NON của
fundamental-skeptic khi due-diligence DGC/TV1 kỳ tới, không tự kết luận QUALIFY/NON thay agent đó.
**Re-reproduced round-4 (job Taylor_20261001_073836, arch-review r2: "quant-skeptic chưa tái
hiện")** — gọi trực tiếp `dcf_valuation.fair_value(ticker, "2026-10-01")` dưới cả 2 giá trị knob
cho đúng 5 mã trên: **byte-identical với bảng đã công bố** (DGC −0.73%, TV1 −0.89%, VNM −0.83%,
FPT −0.89%, MWG −0.89%).

**Lịch sử KHÔNG đổi** — `consumer_deposit_rate()` byte-identical với `current_deposit_rate()` cho
424 ngày mẫu rải 2014-01-01→2026-09-29 (0 lệch, đây là sample của `cctg_deposit_wiring_selfcheck.py`
RIÊNG — xem rõ nguồn dưới, KHÔNG phải cùng con số với "300 ngày" ở cuối đoạn này), và test trực
tiếp `discount_rate()`/`_deposit_rate_pct()` cho asof trước mốc anchor cũng byte-identical cả 2
giá trị knob — mọi số pin registry (R3 23,37%/25,71%, ledger md5...) không bị ảnh hưởng vì period
pin kết thúc trước 2026-09-30.

Selfcheck `WorkingClaude/cctg_deposit_wiring_selfcheck.py` (round-4 fix, job
Taylor_20261001_073836 — sửa path-trap sys.path khiến 3/5 consumer module từng load nhầm bản
PRODUCTION thay vì worktree + thêm 2 assertion hành vi kill mutant M15 `rating_8l` tính `_dep` từ
`current_deposit_rate()` thay vì `_dep_detail["rate_pct"]`): **54/54 PASS** (đếm thật bằng chạy,
không suy đoán), dưới cả python3 và `$DNA_PYEXE`, × 4 TZ (`env -u TZ`, `TZ=Pacific/Kiritimati` —
foreign TZ xa ICT hơn `America/New_York` cũ, cùng tinh thần `verify-before-done`), output 4 lượt
byte-identical cho nhau (gồm cả regression R1 PIT-causal-freshness + R2 silent-swallow + 2 mutant
bị bắt trước đó + mutant M15 mới). `cctg_overlay_selfcheck.py` (selfcheck KHÁC, cho mechanism
kill-switch A/overlay — không phải cho 5 consumer wiring ở trên): **63/63 PASS** (đếm thật, chạy
lại 2026-10-01, T18 cập nhật nhãn `rate_source` mới). "300 ngày lịch sử ngẫu nhiên + 26 mốc anchor
Big-4 ±1 ngày: 0 lệch byte-identical" là số từ job kill-switch A gốc (Taylor_20261001_032954) —
**CHƯA tìm được script cố định tái lập được** (có vẻ là verification ad-hoc trong phiên đó, không
lưu thành file selfcheck thường trú); giữ lại số này làm tư liệu lịch sử nhưng KHÔNG coi là đã
re-verify trong round này — 26 ở đây là số **DEPOSIT_EVENTS anchor Big-4 lịch sử** hardcode trong
`deposit_rate_vn.py` (khác tầng với các con số selfcheck PASS/FAIL phía trên).

## Bẫy
1. **Tenor mismatch 6M vs 12M** — max() là CỐ Ý (đường cong đảo là tín hiệu thật), nhưng MỌI báo
   cáo trích effective rate phải nói rõ driver (`rate_source`/`deposit_rate_source` field) — đừng
   gộp mù thành "lãi suất tiền gửi" chung chung. (`dna_report.build_macro_killswitch_a_line()` và
   `value_radar.build_value_radar_line()`/CLI debug print đều đã gắn tenor vào dòng hiển thị
   2026-10-01 — quant-skeptic round-2 fix 2/4.)
2. **Chỉ 1 mốc dữ liệu (2026-09-30)** — chưa có lịch sử CCTG, không dùng cho backtest trước ngày
   này (sẽ luôn trả `None`/fallback Big-4, đúng thiết kế, không phải thiếu sót cần "làm giàu thêm
   lịch sử" một cách hồi tố).
3. **Pháp lý chưa re-verify độc lập** — xem mục Pháp lý ở trên.
4. **Value Radar đổi NHÃN ngay ngày CCTG trở thành driver (2026-09-30), không phải lỗi dữ liệu.**
   Trước overlay: spread EY−Big-4-12M = +2,02pp, label CHEAP. Sau overlay (CCTG 7,5% > Big-4
   6,8% ⇒ driver đổi): spread EY−CCTG-6M = +1,32pp (−0,7pp, đúng bằng chênh lệch 2 tenor),
   `score` (rolling-10Y) 26,6 vẫn CHEAP nhưng sát biên; `score_expanding` nhảy lên FAIR cùng ngày
   (p_sp 26→44). Đây là bước nhảy RỜI RẠC do đổi tenor driver tại đúng mốc CCTG xuất hiện, không
   phải do thị trường đổi hướng — bất kỳ ai đọc lịch sử Value Radar quanh 2026-09-30 phải biết sự
   kiện này, không tự suy diễn thành "định giá đổi chiều". Pin parity selfcheck
   (`value_radar.py --selfcheck`, 25,9/36,0) KHÔNG bị ảnh hưởng vì mốc đối chiếu của nó
   (`exp_value_radar/radar.csv`, tới 2026-07-30) nằm trước mốc CCTG đầu tiên.
5. **Fail-open trên `macro_killswitch_a_status()` đã vá qua 3 vòng (round-2 fix 1, round-3 fix 2,
   round-6 — mỗi vòng đóng một khe bất đối xứng còn sót, xem docstring đầy đủ trong
   `deposit_rate_vn.py` thay vì tóm tắt lại ở đây vì đã đổi lần cuối 2026-10-01).** Trạng thái
   HIỆN TẠI (round-6, KHÔNG phải mô tả round-2/round-3 đã lỗi thời): một lỗi đọc CCTG, một giá trị
   ngoài khoảng, HOẶC một reading STALE — **bất kể lần đọc CCTG cuối từng ≤ hay > 7,5%** — đều ép
   thẳng `armed=True` (không chỉ `stale=True`), đối xứng với nhánh Big-4 (`big4_stale` cũng ép
   `armed=True` vô điều kiện, không có ngoại lệ "giá trị cuối đã an toàn"). Diễn giải cũ ("CCTG
   stale MÀ lần đọc cuối > 7,5% ⇒ ép armed") chỉ đúng với round-3, đã lỗi thời.
6. **Rollback `DEPOSIT_RATE_CCTG_OVERLAY=0` phủ ĐÚNG 5 consumer — Kill-switch A và Value Radar
   KHÔNG đọc knob này** (chúng gọi thẳng `effective_deposit_rate()`/CCTG, không qua
   `consumer_deposit_rate_detail()`) — bảng cũ ghi "6 consumer" là sai.
   **Và "1 từ" KHÔNG đúng ở MỌI launch context** — đo thật lại 2026-10-01 (round-4, job
   Taylor_20261001_073836, grep trực tiếp từng script, không đoán): **TẤT CẢ 5 launcher LIVE
   hàng ngày đều `source wc_env.sh`** — `pt_8l_daily.sh` (`rating_8l.py`), `refresh_deposit_rate_vn.sh`,
   `mike/bin/papertrade_daily.sh:11` (chain `custom30_history.py`→`custom30_yield_labels.py`),
   `mike/bin/send_plan_report.sh:27`, `mike/bin/eod_trading_report.sh:12-14` (2 report gọi
   `_dcf_check_for_order`/`run_due_diligence`) — set `DEPOSIT_RATE_CCTG_OVERLAY=0` trong
   `wc_env.sh` SẼ tới được cả 4 consumer này qua các launcher trên. `deploy_golive_dt5g_v4/
   golive_recommend_v23.py` (consumer thứ 5, qua `run_due_diligence` dòng 1183) không có dòng
   `source wc_env.sh` trực tiếp trong file — nó chạy trong mắt xích pipeline 19:00-19:03 do
   `mike/bin/bq_freshness_check.sh` (có `source wc_env.sh` ở dòng 46) dispatch; **CHƯA xác nhận**
   được liệu tiến trình dispatch cụ thể (qua Agent/claude session riêng cho DollarBill) có kế
   thừa env đó hay tự nạp lại — đây là khoảng CHƯA ĐO, không phải đã xác nhận an toàn.
   Ngoại lệ DUY NHẤT đã đo chắc: crontab của `dcf_refresh_gate.py`
   (`10 1 11 * * cd WorkingClaude && /home/trido/thanhdt/wc_venv/bin/python dcf_refresh_gate.py`)
   chạy python TRỰC TIẾP, KHÔNG `source wc_env.sh` — set `DEPOSIT_RATE_CCTG_OVERLAY=0` trong
   `wc_env.sh` sẽ KHÔNG tới được process này. Một rollback THẬT phải xác nhận riêng từng launch
   context này (không giả định set 1 biến ở 1 chỗ là đủ cho MỌI nơi, dù nay đã đo được 4/5 launcher
   LIVE hàng ngày đi qua cùng `wc_env.sh`) — KHÔNG sửa crontab trong job này (nằm ngoài phạm vi
   job wiring, xem §11 `kb/cron_registry.md`). **Phương án rollback một bước thật, đề xuất (CHƯA
   LÀM, cần user duyệt riêng)**: thêm dòng `DEPOSIT_RATE_CCTG_OVERLAY=0` vào ĐẦU crontab, cùng
   cách `TZ=Asia/Ho_Chi_Minh` đang được export cho toàn bộ cron (§16) — `cron`'s global
   `VAR=value` export áp dụng cho MỌI job kể cả `dcf_refresh_gate.py` (không `source wc_env.sh`
   nhưng vẫn kế thừa env của crontab daemon), nên phủ được cả ngoại lệ duy nhất đã biết; vẫn
   KHÔNG phủ được nhánh dispatch-to-DollarBill (môi trường của session đó không chắc kế thừa
   crontab's env). Hướng đổi `DEPOSIT_RATE_CCTG_OVERLAY` từ env-var sang hằng số module-level
   (cùng pattern `BREADTH_SOURCE` trong `macro_state_live.py`) vẫn là lựa chọn triệt để hơn nhưng
   chưa làm ở vòng này (sẽ phải viết lại phần lớn `cctg_deposit_wiring_selfcheck.py`, hiện dựa vào
   `with_overlay()` set/pop env var để test cả 2 nhánh knob trong CÙNG process) — ghi nhận làm
   theo dõi, không phải sót.
7. **Silent-swallow trên `effective_deposit_rate()` (đường dùng chung cho 5 consumer LIVE, khác
   bẫy #5 ở trên là của `macro_killswitch_a_status()`) đã vá round-2 (2026-10-01, job
   Taylor_20261001_064225, R2).** Trước đó: một lỗi CCTG (CSV hỏng, exception) hoặc một reading
   stale đều rơi về `rate_source="big4_12m"` — một label KHÔNG PHÂN BIỆT được với trường hợp bình
   thường "CCTG chưa có dữ liệu" (§29: chẩn đoán phải nói rõ bằng chứng), và không log gì. Nay:
   log WARNING thật + `rate_source` ghi rõ nguyên nhân (`big4_12m(cctg_unavailable: <lỗi>)` /
   `big4_12m(cctg_stale: <tuổi>d)`); `rating_8l.py`'s print line + `due_diligence.py`'s
   `deposit_rate_source` field đều hiển thị nguyên nhân thật này.

## Chuỗi phụ CCTG 6 THÁNG — `data/cctg_rate_vn_6m_events.csv` (thêm 2026-10-07, user duyệt)
- Ghi bằng `append_cctg_rate.py --series 6m` (CÙNG mọi guard của chuỗi 12M; sidecar URL riêng
  `cctg6m_rate_last_auto_sources.json`), do cron tuần `refresh_deposit_cctg_weekly.sh` (chuỗi 3).
- Định nghĩa: CCTG 6 tháng cao nhất trong các Big-4 có phát kỳ 6 tháng (dải "6-11 tháng" tính là có).
  Mốc đông cứng trong writer: 2026-09-30 = 7,5% (VCB 6M — chính anchor gốc trước rebase 12M 05/10).
- Status: **CANONICAL cho phân tích đa-proxy (Bobby/Macro Watch), DISPLAY-ONLY.** KHÔNG consumer
  production nào đọc: không vào `effective_deposit_rate()`, kill-switch A, rating_8l, DCF. Muốn
  wire vào đâu ⇒ quant-skeptic + user duyệt riêng.
- Chưa có loader Python; đọc thẳng CSV (header `effective_date,cctg_rate,collected_date,source,note`).
  File chưa tồn tại cho tới lần ghi đầu tiên (sớm nhất cron 12/10/2026).
