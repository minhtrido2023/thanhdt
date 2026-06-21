---
name: papertrade-3sys-2026q2q3
description: "Paper-trade A/B/C 3-system comparison infrastructure running 2026-04-01 → 2026-08-31, daily refresh 15:30 via Windows scheduled task. Decision input for go-live choice in Sept 2026."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6d58b49e-467c-45d3-95b9-fd5f82cecaee
---

3-system paper-trade so sánh để quyết định go-live bản nào trước Sep 2026.

**Why:** memory `[[tam-quan-v3-4b-dinh-tam]]` cho thấy v3.4b backtest 12y win (+3.56pp CAGR FULL, +7.60pp OOS 24-26), nhưng integrated sim 2025-01-01 → 2026-05-19 trên cả V11 (Song Sinh) và V12 (Âm Dương) đều thua LIVE Ngũ Hành Tinh Tế (`vnindex_5state`) về CAGR (+0.47-0.73pp) VÀ DD (-4.7 đến -6.5pp). User yêu cầu paper-trade forward 5 tháng để có thêm dữ liệu trước go-live.

**How to apply:** Khi user hỏi về tiến độ paper-trade hoặc kết quả 3 hệ thống, đọc `data/papertrade_compare3.md` và `data/papertrade_compare3.csv`. Không invent số, không re-run sim trừ khi user yêu cầu. Daily refresh tự động qua scheduled task, baseline accumulate dần qua các ngày.

**Architecture:**
- Window: 2026-04-01 → 2026-08-31 (~5 months, ~110 trading days expected)
- 3 systems, mỗi cái start fresh 50B all-cash 2026-04-01:
  1. **V11 Song Sinh + Tam Quan v3.4b** (`pt_v11_tq34b.py`) — 25B BAL + 25B VN30
  2. **V12 Âm Dương + Tam Quan v3.4b** (`pt_v12_tq34b.py`) — 25B BAL + 25B LAGGED HL3y
  3. **V12 Âm Dương + LIVE Tinh Tế** (`pt_v12_live.py`) — 25B BAL + 25B LAGGED, dùng `tav2_bq.vnindex_5state` production
- Helper: `pt_dates.py` — START="2026-04-01", `detect_end_date()` returns min(today-1, lagged_pos_ov.pkl max, BQ 5state max) — currently caps at 2026-05-19
- Comparison: `papertrade_compare.py` → `data/papertrade_compare3.md` (headline metrics + delta vs V12 LIVE + weekly NAV snapshot) + `data/papertrade_compare3.csv`
- Benchmark: VNINDEX rebased 50B (passive B&H)

**Refresh cadence**: Windows scheduled task `PaperTrade3Sys` daily 15:30 (sau ATC), batch `papertrade_daily.bat` runs all 4 scripts sequentially. Verify: `schtasks /Query /TN "PaperTrade3Sys" /V /FO LIST`. Log per-run: `data/papertrade_run_<date>.log`.

**Initial baseline (2026-04-01 → 2026-05-19, 33 trading days)**:
| System | Final NAV | Total Ret | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|---|---|
| V11 + TQ v3.4b | 51.66B | +3.32% | +28.18% | +3.60 | -1.81% | +15.60 |
| V12 + TQ v3.4b | 50.48B | +0.96% | +7.52% | +1.82 | -1.43% | +5.27 |
| **V12 + LIVE Tinh Tế** | 50.94B | +1.88% | +15.23% | +1.45 | -1.83% | +8.33 |
| VNI B&H | 56.17B | **+12.33%** | +142.27% | +5.33 | -1.64% | +86.71 |

**Initial observation**: cả 3 hệ thống thua VNI B&H đáng kể trong 6 tuần đầu (-8.5 đến -11.4pp vs index +12.33%). Window quá ngắn để statistically significant; CAGR/Calmar extrapolated nhiều. Quan sát thận trọng:
- V11 leading nhóm system (+3.32% vs +1.88% LIVE vs +0.96% TQ34b)
- Nhưng V11 dùng v3.4b state — không thể attribute cho v3.4b vì memory đã chứng minh v3.4b thua LIVE trên window dài hơn
- LAGGED leg của V12 chưa kích hoạt nhiều trong window này (Q1 release earnings còn ít event qualifying HL3y)

**Decision criteria for go-live (target Sept 2026)**:
- Cần ≥80 trading days để có signal có ý nghĩa
- Ưu tiên DD và Calmar > CAGR đơn lẻ (volatile window)
- Reconciliation 4-gate phải PASS mọi ngày (cash trajectory, NAV check)

**Cache constraints**:
- `intraday_full.pkl` lags ~T-5: HYBRID BUY fills work to its max date, T+1 Open fallback sau đó
- `lagged_pos_ov.pkl` + `earnings_events_classified.csv`: cần refresh tay khi BQ ticker_financial có data mới
- `tav2_bq.vnindex_5state` (LIVE): auto-update từ pipeline khác
- Khi cache cũ → `detect_end_date()` tự cap END_DATE, không crash

**Files (all in `C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude`)**:
- `pt_dates.py`, `pt_v11_tq34b.py`, `pt_v12_tq34b.py`, `pt_v12_live.py`
- `papertrade_compare.py`, `papertrade_daily.bat`
- Outputs: `data/pt_*_{logs,transactions,open_positions,report}.csv/md`
- Combined: `data/papertrade_compare3.{md,csv}`
- Scheduled task: `PaperTrade3Sys` (daily 15:30)

Related: [[tam-quan-v3-4b-dinh-tam]] [[ba-v12-am-duong-spec]] [[ngu-hanh-tinh-te]]
