---
kind: bigquery-table
status: TRAP
source: tav2_bq.ticker_prune
group: price-volume
issue: đã thay bằng universe_pit cho mọi cổng quyết định (cutover 2026-07-22)
risk_type: silent drift (trôi dần), KHÔNG phải frozen
writer: bq_admin (3 đường ghi độc lập, ngoài tầm kiểm soát team Mike)
---

# tav2_bq.ticker_prune

**Status: ⚠️ TRAP cho code MỚI — đã thay bằng `universe_pit` cho mọi cổng quyết định** (cutover chính thức 2026-07-22, xem [`universe_pit.md`](universe_pit.md) / [`universe_pit_quality.md`](universe_pit_quality.md))

## Là gì
Universe cũ cho backtest + chọn rổ, **KHÔNG còn là nguồn khuyến nghị**. bq_admin xác nhận (QA
`agents/Taylor/research/ticker_prune_universe_QA_bq_admin_20260722.md`): không tồn tại hệ quản trị
universe — bảng bị ghi bởi 3 đường độc lập (rebuild `WRITE_TRUNCATE` từ `hit_ticker_list.csv` 453 mã
thủ công / daily append cửa sổ 7 ngày từ `ticker_list.csv` / per-ticker replace toàn lịch sử
event-driven theo BCTC). Bộ lọc thật = `Volume_3M_P50*Price/Inflation_7 > 1e9`.

## Ai ghi / cadence
3 đường ghi trên vẫn ĐANG CHẠY (bq_admin, ngoài tầm kiểm soát team Mike) — bảng KHÔNG đứng yên.

## Bẫy
⚠️ **RỦI RO KHÁC với file đông cứng đã gặp trước đây (vụ `ticker_prune.parquet` monolith đóng băng
06-26): đây là "trôi dần" (silent drift), không phải "chết đứng" (frozen).** Một file đông cứng dễ
bắt (mtime cũ, staleness-check báo ngay). `ticker_prune` thì NGƯỢC LẠI — vẫn được ghi liên tục,
`mtime`/freshness-check vẫn "xanh" mỗi ngày, nên KHÔNG có tín hiệu nào tự động báo "bảng này đang
lệch dần khỏi `universe_pit`". Nó chỉ càng ngày càng khác `universe_pit` vì: circular-selection-bias
(`hit_ticker_list` suy từ chính kết quả backtest cũ), lịch sử bị ghi đè âm thầm (đo được +10.630 dòng
2014-2025 trong 8 ngày), và không tái lập point-in-time (`n_union` một mốc lịch sử đã tự trôi 459→381
chỉ trong vài ngày quan sát). **Code còn đọc bảng này sẽ không báo lỗi gì cả — chỉ lặng lẽ cho số
khác `universe_pit` ngày càng nhiều, đúng kiểu lỗi khó phát hiện nhất.** 496 chỗ trong repo từng viết
`IN (SELECT DISTINCT ticker FROM ticker_prune)` KHÔNG có điều kiện time (look-ahead 1,6-2,6×) — hầu
hết là research/backtest có TRƯỚC dự án migrate, KHÔNG bắt buộc sửa hết ngay, nhưng auto-cảnh giác:
**bất kỳ code MỚI nào cần universe/liquidity filter → PHẢI dùng `universe_pit`/`universe_pit_quality`,
KHÔNG viết mới tham chiếu `ticker_prune`.** **Consumer LIVE có chủ đích, đã ghi rõ điều kiện
gỡ** (audit 2026-07-22, dispatch job Mike — ⚠️ **danh sách này ĐẾM THIẾU, xem ĐÍNH CHÍNH 2026-07-29
bên dưới**): (a) `golive_recommend_v23.py:215` (CAPIT pool
selection) + `:354` (CAPIT ADV cap) — ghim chờ (i) `capit_fired` về false VÀ (ii) quyết định riêng về
sàn thanh khoản pool (ADV thay vì turnover-1-ngày); (b) `trading_bot/executor.py:588-603` đọc cache
`ticker_prune` cho 3 tính năng R&D (`gap_adaptive_enabled`/`extreme_regime_enabled`/
`chase_cap_vol_scale_enabled`) — **hiện TẮT trên cả SpaceX/ZaloPay** (chỉ bật ở account paper), nhưng
đang trên lộ trình lên live — **PHẢI migrate executor.py sang `universe_pit` TRƯỚC KHI bật bất kỳ cờ
nào trong 3 cờ này cho live**, đây là gap MỚI phát hiện, chưa nằm trong 4 phase P1-P4 migration gốc.
Vẫn cần giữ freshness-monitoring của `ticker_prune` (`preflight_check.sh`/`bq_freshness_check.sh`)
chừng nào các consumer live trên còn tồn tại.

## ⚠️ ĐÍNH CHÍNH 2026-07-29 — audit trên ĐẾM THIẾU: có **4 consumer LIVE-cron nữa**, KHÔNG chủ đích
Job `Winston_20260729_132257` (báo cáo đầy đủ:
`mike/agents/Winston/research/ticker_prune_hidden_risk_audit_20260729.md`).
Câu "2 consumer LIVE còn lại" ở trên **SAI** — rà cron thật ra thêm 4 chỗ **sót lại từ trước
migration**, không ai cố ý giữ:

| File | Dùng làm gì | Mức |
|---|---|---|
| **`macro_state_live.py:158`** | **breadth-decoupling guard của DT5G** (`daily_refresh_v34b_linux.sh` 18:30) — đúng pattern look-ahead `IN (SELECT DISTINCT ticker …)` **không** điều kiện `time` | 🔴 đường regime PRODUCTION |
| `dna_report.py:91,129` | 2 trục breadth trong report Telegram + `eod_trading_report.sh` | 🟠 báo cáo |
| `update_shares_live.py:49` | `SCAN_UNIVERSE` quét ex-date corp-action (cron 18:40) — mã rớt prune ⇒ ngưng phát hiện corp-action mã đó | 🟠 |
| `ta_score_daily.py:142` | universe chấm điểm TA, pattern look-ahead y hệt | 🟡 |

**Đã đo blast radius của chỗ 🔴**: xoá 58 mã (xem mục dưới) làm breadth lệch **3.130/3.135 phiên**
(max 4,66pp), lật guard **79 phiên** — nhưng chỉ **2** phiên trùng lúc Pillar B (US panic) thực sự
bắn, cả 2 là singleton biệt lập nên `cap_commit=7` nuốt trọn ⇒ **0 phiên DT5G state đổi**.
**Kênh thật nhưng hiện TIỀM ẨN** — nó KHÔNG phải nguyên nhân vụ restate 71 phiên (nguyên nhân vẫn
là VNINDEX_PE backfill + corp-action, xem `dt5g_history_restate_rca_20260729.md`). Rủi ro sống:
guard là coin-flip quanh đúng ngưỡng `b200 = 0,50` (đa số lệch ±0,5pp) — một rebuild prune rơi vào
cửa sổ US panic sẽ lật nó **im lặng trên chuỗi live**. Đối chứng: `vnindex_5state_ew_v1.py`
**KHÔNG** dùng prune (breadth của nó tự tính từ `ticker`: ≥252 phiên + ADV60 ≥ 0,5 tỷ) ⇒ kênh
expanding-rank sạch với prune.

## ⚠️ 2026-07-29 — bảng bị TRUNCATE+rebuild: **58 mã biến mất khỏi TOÀN BỘ lịch sử**
`creation_time = 2026-07-29 07:27:05` ⇒ rebuild `--mode prune` (DROP+CREATE) đã chạy. So với
snapshot `ticker_prune_ttbackup_fresh_20260713` *(lưu ý tên: `_20260713`, không phải `_20260714` —
bản `_20260714` là của `ticker_financial`)*:
- **distinct ticker 513 → 455** (thêm mới: **0**). Live 455 ≈ `hit_ticker_list.csv` (1.819 B,
  **không đổi từ 2026-04-14**); `ticker_1m ∩ prune` = đúng **453** ⇒ khớp cơ chế bq_admin đã tự mô
  tả ở Câu 8 QA doc: *mã vào bằng đường daily-append bị xoá sạch ở mỗi rebuild toàn bộ*.
  **Đây là hành vi đã được cảnh báo trước, KHÔNG phải bug mới — và SẼ LẶP LẠI ở mọi rebuild sau.**
- **Lịch sử viết lại ở 20/27 năm, CẢ HAI CHIỀU** (2015 **+675** dòng, 2016 **+507**, 2009 −590,
  2022 −435, 2024 −341, 2021 −368…) — tính lại membership, không phải cắt đuôi.
- **Hố corruption 07-08→07-14 (INCIDENTS 2026-07-15) đã lành về ĐỘ SÂU** (7-10 mã → 219-221
  mã/ngày) **nhưng KHÔNG lành về MEMBERSHIP**: 07-13 live 220 mã vs backup 265, và live là **tập
  con NGHIÊM NGẶT** (`only_live = 0`). Không phải phục hồi — là thay bằng universe hẹp hơn.
- ⇒ **Khuyến nghị ĐÓNG quyết định treo "restore ticker_prune từ backup" theo hướng KHÔNG restore**
  (restore = nhét lại 58 mã upstream chủ động loại ⇒ bị TRUNCATE kế tiếp xoá lại). Giữ
  `ticker_prune_ttbackup_fresh_20260713` làm **mỏ neo nghiên cứu**. *(Quyết định thuộc user.)*
- ⚠️ **Số TIỀN THẬT cần rà (chủ: Taylor)**: `WASHOUT_GATE=0,30` + ADV cap CAPIT
  (`golive_recommend_v23.py:215,354`) hiệu chuẩn trên mẫu số `ticker_prune` — mẫu số đó vừa tự co
  **265 → 220 mã/ngày (−17%)** mà không ai đổi ngưỡng. Registry đã cảnh báo "đổi mẫu số mà giữ
  ngưỡng = đổi ngữ nghĩa gate"; cái mới là **mẫu số đã tự đổi**.
- ✅ **Upstream sạch**: không bảng bq_admin nào ta tiêu thụ bị prune-lọc — `ticker_1m` 1.262 mã
  (809 ngoài prune), `risk_rating` 1.279 mã (826 ngoài prune). `ticker_prune` là **ĐẦU RA** của
  họ (lọc từ `ticker`+`ticker_financial`), **không phải đầu vào**. *(Không đọc được SQL bq_admin:
  `INFORMATION_SCHEMA.JOBS_BY_PROJECT` = Access Denied, thiếu `bigquery.jobs.listAll` — kết luận
  dựa trên test cấu trúc, không tuyệt đối.)*
- 🪦 Phụ: cột `Pattern_Median_Profit_3Y`/`Pattern_Winrate_3Y`/`Pattern_Deal_Count_3Y` của
  `ticker_1m` **NULL 100%** cho cả 453 mã in-prune lẫn 809 mã ngoài — **cột chết, đừng dùng**.
- 🔧 Gap monitoring: depth-check hiện có (`bq_freshness_check.sh`/`preflight_check.sh`) bắt "moi
  ruột" nhưng **KHÔNG bắt "thay universe"** (depth 220 vẫn > ngưỡng 200 → xanh). Đề xuất thêm
  alert khi `COUNT(DISTINCT ticker)` toàn bảng đổi > ngưỡng giữa 2 ngày (hôm nay sẽ bắn ở −58).
