# Báo cáo trading ngày 2026-08-11 — SpaceX + ZaloPay

*Nguồn: `verify_account_snapshot.py` → `daily_nav_snapshot.py` → `reconcile_equity.py` →
`dividend_adjusted_return.py`/`report_return_gate.py` (coding_guidelines §6 + §21). NAV dùng bản
`daily_nav_snapshot.py` mới nhất (sau fix commit 36846b8 — gộp vị thế trùng lặp trong DNSE raw,
vá lỗi NAV ZaloPay thiếu ~24tr).*

⚠️ **Rerun lần 2** — lần dispatch trước (12:47 ICT) bị hết lượt giữa bước tính cổ tức per-ticker
qua BigQuery (chưa gửi report nào cho hôm nay). Báo cáo này chạy lại từ đầu, đúng pipeline chuẩn.

## 1. DT5G market regime

**BULL** (state=3/4, target tỷ trọng 100%) — chốt phiên **2026-08-10** (bản mới nhất publish;
chưa có bản 08-11). `macro_health.json`: status **HEALTHY**, `recommended_state_source=DT5G_macro`,
market stress = False (VIX không elevated, VNINDEX trên MA200).

## 2. NAV & tình trạng tài khoản

| Account | NAV hôm nay (08-11, 19:52 ICT) | mtm_stock | cash | So với điểm dữ liệu gần nhất |
|---|---:|---:|---:|---|
| **SpaceX** | 967.624.956đ | 821.092.750đ | 146.532.206đ | so với 08-07 (961.311.265đ): **+6.313.691đ (+0,66%)** |
| **ZaloPay** | 953.799.018đ | 884.080.300đ | 69.718.718đ | so với 08-05 (912.854.495đ): **+40.944.523đ (+4,49%)** |

⚠️ **Khoảng trống dữ liệu đã biết**: `nav_history_SpaceX.csv` thiếu bản ghi 08-10 (Thứ Hai, có giao
dịch thật — `exec_SpaceX_2026-08-10_journal.csv` tồn tại), nên số so sánh SpaceX ở trên **gộp cả
2 phiên 08-10+08-11**, không phải thuần "so ngày liền trước". `nav_history_ZaloPay.csv` thiếu cả
08-06, 08-07, 08-10 — số so sánh ZaloPay gộp **4 phiên** (08-06→08-11), không nên đọc như lợi
nhuận 1 ngày. Nguyên nhân nghi là lỗi pipeline-4 trong `bq_freshness_check.sh` dispatch SpaceX lần
hai bị fail im lặng (đã ghi finding trên bus 2026-08-10, thuộc phạm vi Wags/ops sửa cron, không
sửa trong report này).

## 3. Giao dịch hôm nay (2026-08-11)

Cả 2 account đều **CHỈ MUA** (không có lệnh bán), theo plan đã được **user (John) duyệt qua
Discord real-time 2026-08-11**. 2 nhóm lệnh: **PARK_ADD** (nạp thêm sổ PARK theo L2 cash-redesign)
+ **DISCRETIONARY_SPECIAL** (top-up TV1/DRI, ngoài book V2.4, đã duyệt riêng).

| Account | Số lệnh khớp | Số mã | Tổng giá trị MUA |
|---|---:|---:|---:|
| **SpaceX** | 34 | 17 (15 PARK_ADD + TV1/DRI) | 158.945.000đ |
| **ZaloPay** | 23 | 12 (11 PARK_ADD + DRI) | 82.675.000đ |

**Điểm đáng chú ý**: DRI là mã mua nhiều nhất trong ngày ở cả 2 account (rải nhiều lô nhỏ theo
%ADV suốt phiên, đúng cơ chế TWAP) — SpaceX 3.700cp (~49,07tr), ZaloPay 1.900cp (~25,20tr), tiếp
tục top-up theo mục tiêu 5% NAV/mã đã chốt 2026-08-10/11.

## 4. Vị thế đang giữ — tỉ suất ĐÃ ĐIỀU CHỈNH CỔ TỨC (per coding_guidelines §21)

*Nguồn: `report_return_gate.py` (giá vốn = `costPrice` broker DNSE, đã trừ cổ tức gộp sẵn theo
quy ước broker; cổ tức RÒNG các sự kiện có ex-date ≤ 08-11 cộng thêm vào tử số theo công thức §21).
Cột `div` = cổ tức GỘP đồng/cp đã cộng (0 = không có sự kiện trong 120 ngày lookback).*

### SpaceX (tổng: giá vốn thô 831.099.638đ · lãi/lỗ ròng **−1.022.638đ (−0,12%)**)

| Mã | KL | Giá vốn | Giá hiện tại | Tỉ suất % (đã cộng cổ tức) |
|---|---:|---:|---:|---:|
| VIX | 400 | 16.238 | 14.200 | −12,55% |
| TPB | 500 | 16.800 | 14.700 | −12,50% |
| TCB | 1.000 | 33.900 | 31.000 | −8,55% |
| VPB | 1.200 | 27.746 | 25.500 | −8,10% |
| BID | 1.100 | 42.269 | 39.100 | −7,47% (div 450) |
| VND | 300 | 17.800 | 16.900 | −5,06% |
| MBB | 1.565 | 21.406 | 20.350 | −4,94% (div 1.000) |
| NCT | 500 | 86.360 | 82.400 | −4,62% (div 8.000) |
| CTG | 1.200 | 33.806 | 32.300 | −4,46% (div 450) |
| VHM | 900 | 74.900 | 72.100 | −3,74% |
| SHB | 800 | 12.281 | 11.900 | −3,10% |
| VCB | 700 | 61.464 | 59.800 | −2,72% (div 450) |
| SCL | 1.500 | 23.600 | 23.300 | −1,27% |
| EVF | 100 | 12.550 | 12.450 | −0,80% |
| HPG | 1.200 | 22.200 | 22.050 | −0,68% |
| VIB | 500 | 14.900 | 14.800 | −0,67% |
| DRI | 3.700 | 13.262 | 13.200 | −0,47% |
| VRE | 300 | 25.550 | 25.450 | −0,39% |
| ACB | 900 | 22.656 | 22.650 | −0,02% |
| MSB | 500 | 16.250 | 16.250 | 0,00% |
| HDB | 800 | 26.709 | 26.900 | +0,71% |
| TV1 | 500 | 19.640 | 20.100 | +2,34% |
| SAB | 1.100 | 44.368 | 45.650 | +2,39% (div 3.000) |
| LPB | 400 | 52.183 | 53.700 | +2,91% |
| VNM | 900 | 58.600 | 62.000 | +5,80% |
| SIP | 1.700 | 47.059 | 50.900 | +8,16% |
| PVT | 3.500 | 17.100 | 19.700 | +15,20% |

### ZaloPay (tổng: giá vốn thô 416.064.710đ · lãi/lỗ ròng **+7.934.165đ (+1,91%)**, DGC bỏ qua — excluded_tickers chính thức)

| Mã | KL | Giá vốn | Giá hiện tại | Tỉ suất % (đã cộng cổ tức) |
|---|---:|---:|---:|---:|
| MBB | 232 | 21.417 | 20.350 | −4,98% |
| NCT | 373 | 86.400 | 82.400 | −4,66% (div 8.000) |
| VPB | 1.300 | 26.745 | 25.500 | −4,65% |
| BID | 300 | 40.317 | 39.100 | −3,04% (div 450) |
| VHM | 300 | 74.317 | 72.100 | −2,98% |
| LPB | 352 | 54.843 | 53.700 | −2,08% |
| TCB | 356 | 31.611 | 31.000 | −1,93% |
| VCB | 100 | 60.913 | 59.800 | −1,85% (div 450) |
| SHB | 300 | 12.100 | 11.900 | −1,65% |
| SCL | 1.000 | 23.590 | 23.300 | −1,23% |
| HPG | 500 | 22.200 | 22.050 | −0,68% |
| TPB | 100 | 14.800 | 14.700 | −0,68% |
| VIB | 200 | 14.900 | 14.800 | −0,67% |
| DRI | 1.900 | 13.263 | 13.200 | −0,48% |
| VRE | 100 | 25.550 | 25.450 | −0,39% |
| ACB | 300 | 22.700 | 22.650 | −0,22% |
| MSB | 200 | 16.250 | 16.250 | 0,00% |
| CTG | 450 | 32.133 | 32.300 | +0,44% (div 450) |
| VIX | 100 | 13.950 | 14.200 | +1,79% |
| SAB | 744 | 44.450 | 45.650 | +2,21% (div 3.000) |
| HDB | 459 | 25.891 | 26.900 | +3,90% |
| VNM | 601 | 58.700 | 62.000 | +5,62% |
| SIP | 749 | 47.140 | 50.900 | +7,98% |
| CSV | 1.000 | 19.750 | 22.350 | +13,16% |
| PVT | 2.071 | 17.248 | 19.700 | +14,21% |

*DGC (10.000cp, MTM 441.000.000đ, `unrealized ~−36,75tr` theo giá thô — legacy, excluded_tickers
chính thức của ZaloPay per safety core, KHÔNG rebalance qua bot) không tính vào bảng trên.*

## 5. Ghi chú rủi ro / đối soát

- **`reconcile_equity.py` residual — ĐÃ TRUY ĐƯỢC NGUỒN GỐC, KHÔNG PHẢI lỗi NAV**:
  - **ZaloPay** residual 527,4tr (110,6% RHS) là do `mtm_stock` trong `reconcile_equity.py` lấy
    từ `verify_account_snapshot.py` — script này **loại hẳn** DGC/VIB/VPB khỏi `total_mtm_value`
    (không chỉ khỏi P&L) vì thiếu lịch sử fill trong journal (giới hạn đã biết, coding_guidelines
    §7 mục 4). DGC một mình đã là 441tr trong tổng 477tr gap. NAV thật (dùng
    `daily_nav_snapshot.py`, đọc TRỰC TIẾP vị thế broker, không qua journal) **không bị ảnh
    hưởng** — 953.799.018đ ở trên là số đúng.
  - **SpaceX** residual 22,4tr (2,3%) nhiều khả năng là lãi/lỗ ĐÃ THỰC HIỆN từ 4 vị thế về 0 rồi
    mua lại trong lịch sử (HPG/LPB/MSB/VIB — `verified_snapshot` gắn cờ INFO "cost_basis_lot_
    resets"), khoản này không nằm trong `unrealized_pnl` mà công thức đối soát giả định. Cũng
    không phải lỗi NAV — chỉ là công thức chưa cộng phần lãi/lỗ đã chốt của các lần reset đó.
  - Không cần hành động sửa gấp — đây là hạn chế công thức đã biết, không phải lệch sổ thật.
    Nếu cần số reconcile chính xác tuyệt đối cho báo cáo kỳ sau, cần Taylor mở rộng
    `reconcile_equity.py` dùng nguồn `mtm_stock` như `report_return_gate.py` đang dùng (broker
    `costPrice`/`marketPrice` trực tiếp, phủ mọi vị thế kể cả legacy) thay vì
    `verify_account_snapshot.py`.

- **CÂU HỎI CÒN MỞ trên bus** (`zalopay-l1-blocked-reconcile`, đăng 12:09 ICT hôm nay, **chưa có
  trả lời**): `compute_park_trim.py` cho ZaloPay 08-12 trả `BLOCKED_RECONCILE` — sổ lô lệch broker
  ở BID (400 vs 300), MBB (632 vs 232), VCB (300 vs 100). Cần Taylor/Winston xác nhận có corp-action
  mới không (tương tự ca MBB cổ tức cổ phiếu tỷ lệ 15 phần trăm đã xử lý 08-10) trước khi L1 park-trim ZaloPay
  chạy lại cho plan 08-12. **Không chặn lệnh mua** — chỉ chặn cơ chế trim tuân thủ trần PARK.

## 6. Plan ngày mai

`plan_ZaloPay_2026-08-12.json` đã có (job trước 12:03 ICT hôm nay): 0 lệnh BAL/LAG (book rỗng/cửa
sổ đã qua), 1 lệnh RETRY TV1 1.200cp @ LO 20.000–20.200, DRI giữ nguyên (đã đạt ~5,17% NAV). Đang
chờ user duyệt trước 08:45 ICT mai. `plan_SpaceX_2026-08-12.json` chưa dựng — sẽ chạy trong lượt
lập plan cuối ngày tiếp theo.
