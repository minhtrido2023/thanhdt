---
kind: snapshot
status: CANONICAL-PIT cho đoạn 2019-02→2026-09 (SỐ THẬT) · đoạn trước 2019-02 là DỰNG LẠI, KHÔNG phải số công bố
source: FiinPro-X (FiinXMCP) — client.economy.interest_rate.get_other_banks_interest_rates(date=..., individual=True), dòng "Lãi suất bình quân nhóm Big 4", cột "1 Tháng"
upstream_true: các NHTM nhóm Big 4 (VCB/BIDV/Agribank/VietinBank) — biểu lãi suất huy động niêm yết cho khách CÁ NHÂN, kỳ hạn 1 tháng
group: macro
upstream: FiinPro-X trial — HẾT HẠN 2026-09-28. Snapshot MỘT LẦN 2026-09-27 ~23:5x ICT. KHÔNG có nguồn nối tiếp, KHÔNG kéo lại được.
writer: Mike (tay), không cron
verified_by: Taylor, job Taylor_20260927_170645, 2026-09-28
consumer: idle_rate_proxy.py tier `dep1m` (R&D + số pin registry; KHÔNG wire vào engine live)
---

# FiinPro — lãi suất huy động 1 THÁNG, khách cá nhân, bình quân Big 4 (snapshot 2026-09-27)

Chuỗi này là **cơ sở của quy ước tiền nhàn rỗi mà user chốt 23:58 ICT 2026-09-27** (Discord):
*"Tiền mặt thì neo theo lãi suất huy động 1 tháng. Lấy căn cứ này làm số pin"*.

## File
`mike/agents/Taylor/research/idle_cash_proxy_20260927/fiinprox_deposit_1m_big4_monthly_2019_2026.csv`
- 92 dòng dữ liệu + header. Schema: `period,asof,series,rate_pct`.
- `period` = `YYYY-MM` **2019-02 → 2026-09** (92 tháng, KHÔNG khuyết tháng nào).
- `asof` = **ngày 15 của chính tháng đó** (mốc chụp; cột này ghi rõ, đừng đoán).
- `series` = `big4_1m_individual` (một series duy nhất — **lọc tường minh**, đừng giả định).
- `rate_pct` = %/năm, khoảng thực tế **1,6 … 4,9**.

## Vì sao chọn Big 4 (không phải "Trung bình" toàn hệ thống)
(a) khớp quy ước sẵn có của đội (`deposit_rate_vn.py` cũng Big-4); (b) là **đầu THẬN TRỌNG**.
Chuỗi "Trung bình" toàn hệ thống **CÓ trong nguồn nhưng THỦNG 2021-2022** ⇒ **không dùng làm chuỗi
chính**.

## Bẫy
1. **Chuỗi KHÔNG phủ cửa sổ backtest.** Bắt đầu 2019-02, cửa sổ pin bắt đầu 2014-01. Route FiinPro
   trả **HTTP 500 cho MỌI ngày ≤ 2018-12** (Mike dò 2014/2015/2016/2018 đều rỗng) ⇒ đoạn
   **2011-01 → 2019-01 trong `idle_rate_proxy` là SỐ DỰNG LẠI**, không phải số công bố. Ai trích một
   con số cho giai đoạn trước 2019-02 **phải nói đó là dựng lại**.
2. **Cách dựng lại đã chốt:** `dep1m(t) = sbv_low(t) + median(dep1m − sbv_low)` = `sbv_low − 2,525pp`,
   clip ≥ 0. Đo trên 90 tháng overlap 2019-02…2026-08: median −2,525 / mean −2,857 / sd **0,883** /
   p25 −3,400 / p75 −2,300 / corr **+0,619**.
3. **KHÔNG bắc cầu bằng lãi suất liên ngân hàng.** `dep1m − liên NH 1M`: median −0,240 nhưng
   sd **2,472** (2,8× cầu `sbv_low`) và corr **−0,141** (ÂM). Đây là kết luận đã đo, không phải sở
   thích — `measure_dep1m_offset(ref="ib_1 tháng")` giữ lại chính phép đo đó làm bằng chứng.
4. **8 tháng trong đoạn dựng lại khuyết `sbv_low`** (2015-02, 2016-02, 2016-08, 2017-01…03, 2017-05,
   2017-09) ⇒ được **forward-fill** mốc tháng trước, KHÔNG nội suy tương lai. Đếm được bằng cột
   `dep1m_src` (`real` / `recon` / rỗng=ff) và `dep1m_coverage()`.
5. **Không phải carry egg DNSE.** Egg đo thật **8,543%/năm** (spot 09/2026) — cao hơn cả đầu mút cao
   thống kê NHNN ~1pp, là **spread SẢN PHẨM**, DNSE không cam kết mức lãi. Chuỗi này là lãi thị
   trường = đầu thận trọng. Đừng thay bằng 8,543% cho lịch sử.
6. **Upstream đã chết** sau 28/09/2026. Mốc mới phải lấy từ biểu lãi suất Big-4 trực tiếp (không API)
   hoặc mua subscription. Không có freshness-check nào cứu được — file này là **snapshot đông cứng**.
7. **PIT**: mốc tháng T chỉ dùng từ ngày đầu tháng T+1 (luật của `idle_rate_proxy`, không phải của
   file). Hệ quả vận hành đã cắn: một cửa sổ "chỉ dùng số thật" phải bắt đầu **2019-03-01**, không
   phải 2019-02-01 — mọi phiên tháng 02/2019 vẫn đọc mốc 01/2019 (= số dựng lại).

## Phạm vi xác minh
- **Nội bộ (đã làm, job `Taylor_20260927_170645`)**: 92 tháng liên tục không khuyết; 1 series duy
  nhất; khoảng giá trị 1,6–4,9%/năm hợp lý; offset cầu đo lại **khớp** số Mike đưa
  (median/sd/p25/p75/corr); liên tục ở mối nối 2019-01 recon 4,075% → 2019-02 thật 4,500% (+0,43pp).
  Selfcheck `idle_rate_proxy_selfcheck.py`: **102 assertion PASS, 15/15 mutation bị giết**, PASS dưới
  4 TZ + `env -u TZ`; T9 so **từng giá trị** với chính CSV này, T15 fixture chứng minh mask
  chống-back-fill thật sự chặn.
- **CHƯA có nguồn thứ hai độc lập** cho bất kỳ mốc nào của chuỗi này (khác `sbv_low`/liên NH đã đối
  chiếu được 2025-11→2026-09). Ai cần "đã xác minh chéo" thì phải đối chiếu biểu lãi suất Big-4 lịch
  sử — chưa làm.

## Consumer
`idle_rate_proxy.py` tier **`dep1m`** (`r_idle(d, tier="dep1m")`), qua knob
`IDLE_CARRY_TIER=dep1m` của `pt_v23_audit_2014.py` (`IDLE_DEP1M_OFFSET_PP` ghi đè offset cho chân
sensitivity, là **trục đối số ⇒ vào tên file** theo §8). Số pin R3 dùng chuỗi này:
`results_registry` mục **(septies) 2026-09-28** (đang ở dạng `.proposed`, chờ duyệt) — CAGR 25,71% /
DD 5th-pct −23,6%. Báo cáo: `mike/agents/Taylor/research/repin_dep1m_20260928/REPORT.md`.
Liên quan: [[fiinprox_rates_snapshot_20260927]].
