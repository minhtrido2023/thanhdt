# Vì sao gross BULL/EX-BULL thấp hơn NEUTRAL — V2.4 R3 park=0.80

**Job**: Taylor_20260825_134238 · **Nguồn**: CSV production
`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-80_wtnamecap_advprice_exp_agg_F1_t80_univpit.csv`
(park=0.80, F1, kể từ 2026-08-04, root `WorkingClaude/`, không phải `agents/Taylor/`).
**Method**: đọc trực tiếp từ log audit — `record_type=DAILY` đã có sẵn cột `state` (1=CRISIS,
2=BEAR, 3=NEUTRAL, 4=BULL, 5=EX-BULL) và `nav_bal_ref/nav_lag_ref/bal_stocks_ref/bal_etf_ref/
lag_stocks_ref/lag_etf_ref` — không cần join BQ DT5G riêng. `record_type=TX` không mang state
trực tiếp, join theo `ymd` với DAILY để lấy state cho từng transaction.

## 1. Xác nhận hiện tượng (full period 2014→now, N phiên theo state)

| State | N phiên | gross combined |
|---|---:|---:|
| CRISIS | 489 | 0.315 |
| BEAR | 241 | 0.189 |
| **NEUTRAL** | 1895 | **0.774** |
| BULL | 422 | 0.606 |
| EX-BULL | 60 | 0.627 |

Đúng như dispatch mô tả: BULL/EX-BULL gross thấp hơn NEUTRAL, dù đây là 2 regime "tốt nhất". Xác
nhận **KHÔNG** phải do khác CSV/park (đã dùng đúng production park=0.80).

## 2. Phân rã BAL vs LAG — tìm ra thủ phạm

| State | gross_bal | gross_lag | bal_cash_pct | lag_cash_pct |
|---|---:|---:|---:|---:|
| CRISIS | 0.135 | 0.531 | 0.865 | 0.469 |
| BEAR | 0.146 | 0.279 | 0.854 | 0.721 |
| **NEUTRAL** | 0.801 | 0.865 | 0.199 | 0.135 |
| BULL | **0.911** | **0.437** | 0.089 | 0.563 |
| EX-BULL | **0.940** | **0.414** | 0.060 | 0.586 |

**BAL book (momentum) đúng như kỳ vọng: gross TĂNG dần NEUTRAL→BULL→EX-BULL (0.80→0.91→0.94)** —
momentum book deploy vốn mạnh hơn khi thị trường xác nhận bull, không phải nguyên nhân.

**LAG book (PEAD/earnings drift) là thủ phạm: gross SỤT mạnh NEUTRAL→BULL→EX-BULL (0.87→0.44→0.41)**
— LAG book ngồi ~56-59% tiền mặt trong BULL/EX-BULL, so với chỉ ~13.5% trong NEUTRAL. Hai hướng
đối lập nhau và LAG thắng thế vì tỷ trọng NAV hai book gần bằng nhau (~45/55).

**Kiểm chứng bằng decomposition số học** (`gross_combined ≈ nav_bal_share×gross_bal +
nav_lag_share×gross_lag`, nav_lag_share ổn định 0.44-0.53 mọi state):
- BULL: 0.44×0.91 + 0.46×0.44 ≈ 0.60 — khớp gross_combined thực đo 0.606.
- EX-BULL: 0.46×0.94 + 0.45×0.41 ≈ 0.61 — khớp 0.627.
- NEUTRAL: 0.40×0.80 + 0.53×0.87 ≈ 0.78 — khớp 0.774.

## 3. Loại trừ nguyên nhân (đo trực tiếp từ data, không suy đoán)

- **(c) Allocator design — LOẠI.** `w_lag_tgt` mean theo state: NEUTRAL 0.558, BULL 0.613,
  EX-BULL 0.650 — target weight cho LAG **CAO HƠN** trong BULL/EX-BULL, không thấp hơn. Nếu
  allocator là nguyên nhân thì LAG phải deploy NHIỀU hơn, ngược với quan sát. Loại giả thuyết này.
- **(b) Custom30V parking lấp trần 0.80 — không phải nguyên nhân của khoảng gap LAG.** Parking
  custom30V chỉ chạy trên **BAL** book trong NEUTRAL — nhưng chính BAL lại là book có gross THẤP
  NHẤT ở NEUTRAL (0.80) so với BULL/EX-BULL (0.91/0.94), nghĩa là parking không "lấp trần" theo
  hướng làm BULL/EXBULL thấp hơn — hướng ngược lại. Không giải thích được hiện tượng đang hỏi.
- **(a) Signal scarcity trên LAG book — ỦNG HỘ, bằng chứng trực tiếp.** Tần suất lệnh MUA thực tế
  của LAG (buy/100 phiên, đếm từ `record_type=TX`, join state theo `ymd`):
  - NEUTRAL: 167.8/100 phiên
  - BULL: 147.9/100 phiên
  - EX-BULL: **86.7/100 phiên** (giảm gần một nửa so với NEUTRAL)

  Ngược lại, BAL buy rate TĂNG mạnh: NEUTRAL 37.3 → BULL 191.2 → EX-BULL 176.7/100 phiên — xác
  nhận BAL không thiếu signal trong bull; chỉ LAG thiếu.
- **(d) BAL vs LAG mix — đây CHÍNH LÀ cơ chế**, không phải nguyên nhân độc lập với (a): LAG book
  giữ tỷ trọng NAV gần bằng BAL (~50/50) nên cash-drag của nó kéo gross combined xuống đủ để lấn
  át phần BAL deploy thêm.

## 4. Kết luận

Không phải artifact của sizing/allocator (target weight LAG thực ra CAO hơn trong BULL/EX-BULL).
Đây là **hành vi thật của signal PEAD/earnings-drift**: khi DT5G đã xác nhận BULL/EX-BULL (thị
trường đã chạy, giá đã re-rate), setup "earnings surprise + underreaction chưa được giá" hiếm hơn
hẳn — LAG filter (SUE-based) tìm được ít cơ hội hơn, book ngồi tiền mặt nhiều hơn dù allocator
sẵn sàng cấp vốn nhiều hơn cho nó. Đây là vấn đề CẤU TRÚC của factor PEAD (well-known trong
literature: post-earnings-drift alpha co lại khi thị trường đã hưng phấn/re-rated rộng), không
phải bug engine.

**Giới hạn của phân tích này**: CSV chỉ ghi lệnh MUA đã THỰC HIỆN (`TX` rows), không ghi log số
lượng ứng viên bị lọc loại/không đạt ngưỡng SUE mỗi ngày — nên buy-rate là proxy CẬN DƯỚI cho
"số signal khả dụng", không phải đếm trực tiếp candidate pool. Đủ để xác nhận hướng và độ lớn của
hiệu ứng, không đủ để tách bạch "ít candidate" vs "candidate có nhưng bị lọc chặt hơn".

**Không phải vấn đề cần sửa** — gross thấp hơn ở BULL/EX-BULL phản ánh đúng chỗ LAG book KHÔNG có
gì để mua, không phải hệ thống bỏ lỡ cơ hội có sẵn. Nếu muốn khai thác phần cash-drag này (vd.
route sang BAL hoặc parking basket khi LAG cạn signal) — đó là hướng research MỚI, cần Mike/user
quyết định phạm vi trước khi Taylor tự dispatch thêm.
