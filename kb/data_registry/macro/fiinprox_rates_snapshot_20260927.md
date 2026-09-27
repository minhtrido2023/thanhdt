---
kind: snapshot
status: UNVERIFIED-PIT-CANDIDATE
source: FiinPro-X (FiinXMCP) — client.economy.interest_rate.list_state_bank_interest_rates + client.economy.open_market.list_operations(Monthly)
group: macro
upstream: FiinPro-X trial, HẾT HẠN 2026-09-28 — snapshot MỘT LẦN 2026-09-27 16:4x ICT, không có nguồn nối tiếp
writer: Mike (tay), không cron
---

# FiinPro rates snapshot 2026-09-27 — lãi suất huy động BQ (NHNN) + lãi suất BQ liên ngân hàng

**Status: UNVERIFIED-PIT-CANDIDATE** — ứng viên proxy lãi tiền nhàn rỗi cho backtest (thay giả định 0%),
chưa đối chiếu chéo với nguồn gốc. Dùng nghiên cứu; KHÔNG wire vào bất kỳ số công bố nào cho tới khi
Taylor đối chiếu ≥3 mốc/chuỗi (kế hoạch `kb/projects/custom30v-revalidation-plan-20260927.md` §2.3).

## File
`mike/agents/Taylor/research/idle_cash_proxy_20260927/`
- `fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv` — 358 dòng, `period` (YYYY-MM) 2011-01→2026-08,
  2 series: "Lãi suất huy động bình quân trên 12 tháng (cao nhất)" / "(thấp nhất)", %/năm.
- `fiinprox_interbank_avg_rate_monthly_2014_2026.csv` — 2.142 dòng, `period` (YYYY-MM-DD cuối tháng)
  2014-01-31→2026-09-25, 14 series: "Lãi suất BQ liên NH kỳ hạn {qua đêm,1 tuần,2 tuần,1 tháng,3 tháng,
  6 tháng,9 tháng}" (%/năm) + "Doanh số kỳ hạn ..." (VND, số tuyệt đối).

Schema chung: `period,series,rate_pct` (long format).

## Vì sao cần
Mọi pin R3 tới 2026-09-27 giả định tiền nhàn rỗi = 0%/năm. Carry egg đo thật 8,55% (Job U) là spot
09/2026, cao hơn cả mức "cao nhất" 12M của NHNN (7,6% 08/2026) — áp cho 2014-2026 là ngược thời gian.
Chuỗi `deposit_rate_vn.py` hiện có là 26 mốc neo hồi tố (không PIT). Đây là 2 chuỗi PIT thật duy nhất
đang có trong tay phủ đủ 2014-2026.

## Bẫy
1. **Chưa đối chiếu** — FiinPro có thể restate; kiểm ≥3 mốc với báo cáo NHNN/SBV gốc trước khi tin.
2. "Trên 12 tháng" là kỳ hạn dài; egg là T+1 không kỳ hạn ⇒ phải trừ haircut kỳ hạn, không dùng thẳng.
3. Liên NH là lãi giữa ngân hàng, không phải lãi khách hàng nhận — dùng làm SÀN stress, không phải baseline.
4. Doanh số liên NH cột `rate_pct` mang đơn vị VND tuyệt đối (không phải %), lọc theo `series` trước khi tính.
5. Không có nguồn nối tiếp sau 28/09/2026 — mốc mới phải lấy từ NHNN/SBV trực tiếp hoặc mua subscription.
