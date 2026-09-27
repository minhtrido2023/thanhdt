---
kind: snapshot
status: CANONICAL-PIT (phạm vi xác minh giới hạn — xem §Đối chiếu)
source: FiinPro-X (FiinXMCP) — client.economy.interest_rate.list_state_bank_interest_rates + client.economy.open_market.list_operations(Monthly)
upstream_true: Ngân hàng Nhà nước (NHNN/SBV) — bảng "Diễn biến lãi suất của TCTD đối với khách hàng" (tháng) + bảng "Lãi suất bình quân liên ngân hàng" (dttktt.sbv.gov.vn, PHIÊN/ngày)
group: macro
upstream: FiinPro-X trial, HẾT HẠN 2026-09-28 — snapshot MỘT LẦN 2026-09-27 16:4x ICT, không có nguồn nối tiếp
writer: Mike (tay), không cron
verified_by: Taylor, job Taylor_20260927_101337, 2026-09-27
consumer: idle_rate_proxy.py (R&D only, KHÔNG wire vào engine)
---

# FiinPro rates snapshot 2026-09-27 — lãi suất huy động (NHNN) + lãi suất BQ liên ngân hàng

**Status: CANONICAL-PIT, phạm vi xác minh 2025-11 → 2026-09.** Đối chiếu chéo ĐẠT cổng
`custom30v-revalidation-plan-20260927.md` §2.3 (≥3 mốc/chuỗi, lệch >0,2pp ⇒ hạ UNVERIFIED): lệch
thực tế **0,00pp trên 3/3 mốc mỗi chuỗi**. **Đoạn 2011-01 → 2025-10 chưa có nguồn thứ hai** —
dùng được cho R&D/backtest, nhưng ai pin một con số công bố dựa vào đoạn đó phải nói rõ điều này.

## File
`mike/agents/Taylor/research/idle_cash_proxy_20260927/`
- `fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv` — 358 dòng, `period` (YYYY-MM) 2011-01→2026-08,
  2 series "(cao nhất)"/"(thấp nhất)", %/năm.
- `fiinprox_interbank_avg_rate_monthly_2014_2026.csv` — 2.142 dòng, `period` (YYYY-MM-DD **phiên cuối
  tháng**) 2014-01-31→2026-09-25, 14 series: 7 tenor lãi suất (%/năm) + 7 tenor doanh số (VND).

Schema chung: `period,series,rate_pct` (long format).

## Đối chiếu (Taylor, 2026-09-27)
**Tiền gửi — 3/3 mốc, lệch 0,00pp:** 2025-11 `4,9/6,2` (báo cáo NHNN 11/2025) · 2026-01 `5,1/6,5`
(NHNN 01/2026) · 2026-06 `5,9/7,3` (bảng NHNN 6/2026 in nguyên văn).
**Liên ngân hàng — 3/3 mốc, 9 quan sát tenor, lệch 0,00pp:** 2026-09 (`2026-09-25`) khớp **7/7 tenor**
với bảng chính thức SBV `dttktt.sbv.gov.vn/webcenter/portal/vi/menu/rm/ls/lsttlnh` phiên 24/09/2026
(O/N 1,10 · 1W 5,06 · 2W 5,35 · 1M 6,25 · 3M 7,20 · 6M 7,55 · 9M 8,00) · 2026-08 O/N `1,19` khớp
báo chí dẫn SBV cuối tháng 8 · phiên 27/08 O/N 1,20 nhất quán chiều giảm.
**Không tìm được nguồn độc lập cho 2014-2024**: URL `sbv.gov.vn/.../ShowProperty` 404, CEIC /
TradingEconomics / FXEmpire trả 403-404 khi không đăng nhập, báo cáo tháng NHNN thời kỳ đó không còn
index công khai.

## Vì sao cần
Mọi pin R3 tới 2026-09-27 giả định tiền nhàn rỗi = 0%/năm. Carry egg đo thật 8,543% (Job U
`Taylor_20260927_085628`) là spot 09/2026, cao hơn cả đầu mút cao 7,6% của NHNN 08/2026 — áp cho
2014-2026 là ngược thời gian. Chuỗi `deposit_rate_vn.py` là 26 mốc neo hồi tố (không PIT). Đây là 2
chuỗi PIT thật duy nhất phủ đủ 2014-2026.

## Bẫy
1. **Nhãn "bình quân trên 12 tháng" SAI HAI LẦN.** (a) Không phải bình quân — là **hai đầu mút của
   KHOẢNG lãi suất phổ biến** NHNN công bố. (b) Là dòng **"Trên 12 tháng đến 24 tháng"**, **KHÔNG**
   gồm dòng "Trên 24 tháng" (6/2026: 7,1-7,8%; 11/2025: 6,7-7,4%). Đọc theo nhãn sẽ dùng số thấp hơn
   thực tế ở kỳ hạn dài nhất.
2. **Chuỗi liên NH KHÔNG phải bình quân tháng** — là bản in của **MỘT phiên cuối tháng** (bằng chứng:
   2026-09 khớp 7/7 tenor với bảng SBV NGÀY 24/09). Lãi O/N VN dao động 0%–16,39% trong 2026 ⇒ một
   phiên không đại diện cho tháng. Dùng như **kịch bản**, không phải ước lượng trung tâm; ưu tiên
   tenor 1M/3M thay vì O/N.
3. **Tenor dài mỏng thanh khoản**: doanh số trung vị 9M = **830 tỷ**, 6M = 4.863 tỷ (vs O/N 896.204
   tỷ, 1W 220.126 tỷ). Giá 9M/6M là single-print — không dùng cho quyết định.
4. Liên NH là lãi giữa ngân hàng, không phải lãi khách hàng nhận — **SÀN stress**, không phải baseline.
5. Doanh số liên NH nằm CÙNG cột `rate_pct` nhưng mang đơn vị VND tuyệt đối — **lọc `series` trước
   khi tính**, nếu không cột % sẽ nhận giá trị ~1e13 (mutation M5 của selfcheck neo đúng lỗi này).
6. Không có nguồn nối tiếp sau 28/09/2026 — mốc mới phải lấy từ NHNN/SBV trực tiếp (bảng
   `dttktt.sbv.gov.vn` còn sống, chỉ là không có API) hoặc mua subscription.
7. **Đoạn 2011-01→2025-10 chưa được nguồn thứ hai xác minh** (xem §Đối chiếu). Không tuyên bố
   "CANONICAL" cho toàn chuỗi.

## Consumer & haircut đã hiệu chỉnh
`idle_rate_proxy.py` (WorkingClaude root, R&D-only) dùng chuỗi này qua `r_idle(date, tier)`:
`baseline` = SBV thấp nhất − **2,04pp** · `floor` = max(0, liên NH 1M) · `spot` = 8,543% (chỉ
2026-08-18→2027-03-31, ngoài khoảng raise). Haircut 2,04pp = **median(SBV thấp nhất − liên NH 3M)**
đo trên 143 tháng 2014-01→2026-08 (p25 +0,36 / p75 +3,15 / mean +1,59 / sd 1,92 / 21,0% tháng âm) —
thay con số quy ước 1,0pp của bản kế hoạch, vốn quá nhỏ và nghiêng kết luận về phía "tiền có lợi".
Selfcheck `idle_rate_proxy_selfcheck.py`: 50 assertion PASS, mutation 7/7 bị giết, PASS dưới
`env -u TZ` + 3 TZ ngoại. Số liệu đầy đủ: `idle_cash_proxy_20260927/REPORT.md`.
