# PREREG — GĐ3 thời điểm an toàn V2.4 vs gửi tiết kiệm (job Taylor_20261112_132954)
Ghi lúc: **2026-11-12 20:32:59 +07** (lệnh `TZ=Asia/Ho_Chi_Minh date`), TRƯỚC khi chạy mọi phép thử điều kiện. md5 file này ghi ở `PREREG.md5` ngay sau khi ghi. Không thêm biến/ngưỡng/thước đo sau khi thấy kết quả; mọi sai khác sẽ ghi ở REPORT §Lệch PREREG.

## Dữ liệu
- NAV: dòng DAILY `combined_nav` của ledger engine sạch (code vá mergesort `live_gap_phase1b_20261112/sb_liq`, data sandbox đóng băng, LIQ_ZERO_BLOCK=lag, NAV 50B, BASKET_WT=namecap, BASKET_SELECT=yieldcombo, IDLE_CARRY_TIER=off, AUDIT_END 2026-06-19, threads=1).
  Chân **P0** = PARK_STATES=3:0 (dựng mới, ledger `_exp_gap_p3_p0_liqz`) — CHÍNH cho phần điều kiện. Chân **P30** = PARK_STATES=3:0.3 (ledger GĐ2B md5 151bd903…) — baseline + độ nhạy.
- Tiết kiệm (chỉ làm NHÃN ex-post): lãi 12T `deposit_rate_vn.merge_deposit` (26 mốc neo hồi tố), cộng dồn theo ngày lịch actual/365. Độ nhạy nhãn: fiinprox dep1m 2019-02+ (mốc tháng T dùng từ ngày 1 tháng T+1).
- Kết quả: excess_H(t) = NAV(s+H)/NAV(s) − 1 − [tiết kiệm cộng dồn s→s+H], s = phiên KẾ TIẾP sau t (điều kiện đọc ở đóng cửa t, vào từ T+1), H = 3/6/12 tháng LỊCH (phiên cuối ≤ s+H). H=12T là thước đo chính.

## Bước 1 — baseline vô điều kiện (mô tả, không phép thử)
Mọi ngày khởi đầu có đủ H: phân phối excess_H, P(excess>0), trung vị excess khi thua, MaxDD trong cửa sổ khi thua; theo năm khởi đầu và era IS (khởi đầu 2014-01..2018-12) / đệm 2019 / OOS (2020-01..hết). CI 90% của P(thắng) bằng block bootstrap theo tháng (khối 12 tháng, 1000 lần) trên mẫu tháng.

## Bước 2 — biến điều kiện (họ phép thử F, chỉ chân P0, H=12T)
Mẫu = phiên đầu tiên mỗi tháng. Lớp tại t chỉ dùng dữ liệu biết ở t (US: phiên Mỹ < t; LAG edge: known_date ≤ t; breadth: phiên ≤ t−1).
| # | Biến | Rời rạc hoá (CỐ ĐỊNH) |
|---|---|---|
| V1 | DT5G state (cột `state` ledger = `vnindex_5state_dt5g_live`) | {CRISIS,BEAR} / NEUTRAL / {BULL,EX-BULL} |
| V2 | dd52 VNINDEX = Close/max(Close 252 phiên) − 1 | mốc tự nhiên: > −10% / −10..−20% / ≤ −20% |
| V3 | breadth b200 universe_pit (SQL `macro_state_live._breadth_sql` source pit), giá trị t−1 | tercile theo phân vị của các mẫu tháng IS |
| V4 | SPX dd_1y (`data/us_market_history.csv`) | mốc tự nhiên: > −5% / −5..−15% / ≤ −15% |
| V5 | LAG edge `mean12` (`data/lag_edge_health.csv`, known_date ≤ t) | tercile IS |
| V6 | vol thực hiện VNINDEX 60 phiên (std log-ret ×√252) | tercile IS |
Mô tả, NGOÀI họ (không thể qua tiêu chí): Value Radar zone (RẺ<33/TRUNG TÍNH/ĐẮT>67, display-only, phân vị có bias neo hồi tố); dep1m xu hướng 3T và mức (chỉ 2019+, bước 4).
**Phép thử mỗi biến (1 phép/biến/era):** Δ = TB excess12 (lớp cao nhất) − TB excess12 (lớp thấp nhất) (V1: {BULL,EX} − {CRISIS,BEAR}). Nếu một lớp cực có < 3 mẫu tháng trong era → biến đó "không kiểm được" ở era đó (= không qua).
p-value: null dịch vòng (circular shift) chuỗi lớp so với chuỗi kết quả trong cùng era, độ dịch ngẫu nhiên ∈ [12, n−12] tháng, 2000 lần, hai phía.
**N trials = 6 biến × 2 era = 12**; BH-FDR áp riêng mỗi era trên 6 p.
**Tiêu chí QUA (cả 4):** (1) q<0,10 ở IS VÀ ở OOS, Δ cùng dấu; (2) hơn placebo hoán vị-trong-năm (hoán vị lớp giữa các tháng trong cùng năm, 500 lần): Δ thật vượt phân vị 90% của Δ placebo theo đúng dấu, ở CẢ hai era; (3) bỏ-từng-năm (năm khởi đầu): dấu Δ không đổi với mọi năm bị bỏ, cả hai era; (4) chính sách bước 3 (bên dưới) hơn phân vị 90% placebo về CAGR.
Báo kèm: P(thắng | lớp), trung vị excess | lớp, N tháng, **N episode** (cụm tháng liên tiếp cùng lớp) mỗi lớp mỗi era; CI block bootstrap (khối 12 tháng).
MDE mỗi biến/era = 2,8 × sd(Δ dưới null dịch vòng) (α 0,05 hai phía, lực 80%).
Độ nhạy (không đổi kết luận qua/không qua): chân P30; H=6T.

## Bước 3 — chính sách walk-forward
Chỉ cho biến QUA (1)–(3): "về tiết kiệm khi ở lớp cực tệ hơn" — quyết định đóng cửa t, áp từ phiên t+1; ngày ở tiết kiệm hưởng lãi 12T; mỗi lần đổi trạng thái tốn 0,1% (TC CLAUDE.md) trên toàn NAV. Lớp xác định hằng ngày theo cùng ngưỡng.
So: (a) engine P0 nguyên (DT5G hiện hành bên trong); (b) placebo tắt ngẫu nhiên cùng tỉ lệ ngày-tắt và cùng số đoạn tắt (vị trí đoạn ngẫu nhiên, 500 lần); báo CAGR/Sharpe/MaxDD/số lần đổi/chi phí.
Tham chiếu khai trước (KHÔNG phải ứng viên, chạy dù không biến nào qua, để trả lời "so với DT5G"): "tiết kiệm khi DT5G ∈ {CRISIS,BEAR}" vs placebo.
Nếu không biến nào qua: kết luận "không phát hiện điều kiện thời điểm bền", kèm MDE. Không thêm biến, không đổi ngưỡng.

## Bước 4 — ngưỡng lãi (2019+ riêng, mô tả, NGOÀI họ)
dep1m mức: cao/thấp theo trung vị dep1m 2019-02..2020-12 (cố định). dep1m xu hướng 3T: tăng (>0) / không tăng. Spread ey_mkt − dep1m, ey_mkt = 1/PE VNINDEX (`data/VNINDEX.csv` cột PE), cắt tại trung vị 2019-02..2020-12. Báo P(thắng 12T|lớp), trung vị, N tháng, N episode. Nhãn excess dùng hurdle 12T (chính) và dep1m (độ nhạy).

## Bước 5 — sizing tham chiếu (không đề xuất luật)
Danh mục w·V2.4(P0 và P30) + (1−w)·tiết kiệm 12T, cân lại hằng ngày, w ∈ {0,0.1,…,1}. Báo CAGR, MaxDD toàn kỳ; block bootstrap khối 12 tháng (1000 lần, độ dài = toàn kỳ) phân vị 5% CAGR và 5% MaxDD; w lớn nhất có MaxDD-5%-bootstrap ≥ −10% / −15% / −20%; P(thắng tiết kiệm 12T) theo w.
