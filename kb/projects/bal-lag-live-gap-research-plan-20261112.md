# Kế hoạch nghiên cứu — BAL/LAG: backtest tốt, live kém, so với gửi tiết kiệm (2026-11-12)

> Trạng thái: **DỰ THẢO chờ user duyệt**. Người lập: Mike. Yêu cầu user 12/11 17:19 ICT.
> Nguồn số: `nav_period_returns.py` 11/11, `panel_v23_vs_live_nav_20260926.md`, `bal_loss_attribution_20261022/REPORT.md`,
> `lag-adv-filter-tracking.md`, `execution_alpha_20260925/FINDINGS.md`, `amh-adaptivity-review-20260910.md`, `edge_health_block.md`.

## 0. Sự thật đã có trên sổ (không cần nghiên cứu lại)

| Chỉ số 01/07→11/11/2026 (133 ngày) | SpaceX | ZaloPay | Ghi chú |
|---|---|---|---|
| Live (unit ledger / TWR) | −3,86% | −7,51% | ZaloPay gánh DGC legacy |
| VN-Index giá | −6,08% | −5,24% | live THẮNG chỉ số |
| Gửi tiết kiệm hiệu dụng 7,4%/năm (CCTG 12T Big-4) | **+2,70%** | +2,70% | live THUA tiết kiệm ~6,6–10pp |
| Panel paper V2.3 @50B cùng cửa sổ | −7,53% | — | live thắng paper +4–6pp (chọn mã), thua ở exposure |
| Backtest pin V2.4 (CAGR 12 năm, park 0) | 22,12% sàn … 25,42% trần | | **chưa từng chạy trên cửa sổ live** (`audit_end` 2026-06-19) |

Bốn điều đã biết, định hình plan:
1. **Backtest V2.4 chưa bao giờ được chạy trên 07→11/2026.** Mọi so sánh "23% vs −4%" là so CAGR 12 năm với 4 tháng mùa xấu (VNI −6%). Shadow BAL theo tháng trên cache sống: 07 +0,88 / 08 +7,27 / 09 −3,79 / 10 −4,91 — backtest cũng lỗ T9-T10.
2. **Hệ live KHÔNG phải hệ đã pin.** Luật chỉ có ở live: sàn ADV 2 tỷ (08-10), park 0 (10-01), CAPIT lever tắt (10-13), loại mã có cờ (11-02), LAG DD-zone gate (11-09), excluded_tickers, bán tay DRI/TV1/SCL, sleeve discretionary (VGS/NNC/FPT). BAL live = **1 deal (VPI)**; 79% NAV nằm ở Trứng vàng.
3. **Pin LAG @50B "chưa chứng minh thực thi được"**: biến thể thực tế D3AK10 = 18,1–20,8% (không phải 23%); slot leak 2,2–2,6pp nằm sẵn trong pin; fill thật LAG lớn nhất 0,45% ADV.
4. **Edge theo thời gian, không theo regime**: mom_200 (xương sống BAL) dương 8/8 scope IS, ≈0 8/8 OOS sau 2020 — "the break is TIME, not regime". Breadth-tercile/radar/DT5G không tách được tín hiệu (0/27, 0/24, 0/12). LAG edge 12M đang TROUGH (pctile 6). Value/quality IC đang MẠNH LÊN (PE −0,116, ROE_Min5Y +0,192).

⇒ Câu hỏi đúng không phải "tại sao backtest sai" mà là **ba câu tách biệt**: (A) phần nào của gap là THỊ TRƯỜNG, (B) phần nào là HỆ LIVE ≠ HỆ PIN + thực thi, (C) deal nào / lúc nào xác suất thắng tiết kiệm đủ cao để đáng mạo hiểm.

## 1. Thước đo chung (Giai đoạn 0 — 1 tuần, Mike + Taylor, không cần BQ nặng)

- **Hurdle = lãi tiết kiệm hiệu dụng PIT** = max(Big-4 12T, CCTG 12T) (`deposit_rate_vn.py`, chuỗi `fiinprox_deposit_1m_big4` 2019-02→2026-09 cho lịch sử; trước 2019 = chuỗi phục dựng, ghi rõ). Mọi lợi suất trong plan này báo bằng **excess so với hurdle**, không phải tuyệt đối, không phải so VN-Index.
- **Đơn vị đo deal** = excess return trên kỳ nắm giữ của chính deal (LAG 25 phiên; BAL tới tín hiệu bán), quy về cùng kỳ hurdle. N = số deal độc lập (gộp cùng mã cùng cụm ngày), không phải số dòng.
- **Việc cơ học kèm theo** (cần user duyệt vì chạm báo cáo NĐT): thêm dòng "so với gửi tiết kiệm cùng kỳ" vào bảng hiệu suất (`fund-unit-performance-policy` hiện chỉ có VN-Index); vá cột `book` trống trong journal tháng 7; chạy lại kiểm tra fill-vs-open (quy ước 08-26 "mỗi ~10 phiên" chưa từng có kết quả nào kể từ đó).

## 2. Giai đoạn 1 — Thác nước gap trên cửa sổ live (2 tuần, Taylor opus/medium → quant-skeptic)

Mục tiêu: một bảng **waterfall pp NAV** từ "backtest pin chạy đúng 07-01→11-12" đến "live thật", mỗi bậc chỉ đổi MỘT trục (luật §8c, `pin_ledger.py compare`):

| Bậc | Đổi gì | Trả lời |
|---|---|---|
| W0 | Chạy `pt_v23_audit_2014.py` AUDIT_START=2026-07-01, AUDIT_END=2026-11-12, cấu hình pin park 0, NAV 50B | Thị trường 4 tháng này backtest được bao nhiêu? (so hurdle +2,7%) |
| W1 | NAV_TOTAL_B=1 (vốn thật) | Capacity 50B→1B đáng bao nhiêu |
| W2 | + sàn ADV 2 tỷ, loại mã cờ, LAG DD-zone gate, excluded_tickers, CAPIT off | Luật live-only cộng/trừ bao nhiêu |
| W3 | + thay quyết định hệ bằng lệnh tay thật (DRI/TV1/SCL bán, VGS/NNC/FPT mua) | Phần "người" |
| W4 | + fill thật thay close T+1 (`dnse_raw_*`, +5,5bps/lệnh đã đo) | Thực thi |
| W5 | + tỷ trọng tiền thật (egg 79%) thay cash lý thuyết | Cash drag / exposure |

Điều kiện tiên quyết đã biết: (a) engine KHÔNG tất định theo `AUDIT_END` (sort không ổn định `regime_size_overlay.py:47`) → vá trước, (b) LAG cache trộn cơ sở điều chỉnh giá sau 06-19 (`lag-cache-adjusted-20261110.md` chưa merge) → merge trước, (c) dùng snapshot `tav2_pin.*_pin_YYYYMM` thay cache sống đã restate. Hai account chạy riêng (ZaloPay tách DGC qua `nav_sleeve_history_ZaloPay.csv`).

**Cổng dừng**: nếu W0 ≈ live (gap chủ yếu ở W0) ⇒ vấn đề là kỳ vọng/thị trường, Giai đoạn 3 (timing) ưu tiên hơn Giai đoạn 2. Nếu W1–W2 ăn phần lớn ⇒ hệ live đã trôi khỏi hệ pin, phải re-pin "V2.4-live" trước khi nghiên cứu gì thêm. Nếu W3 lớn ⇒ vấn đề kỷ luật, không phải mô hình.

## 3. Giai đoạn 2 — Phân loại deal (3–4 tuần, Taylor; Bobby gắn nhãn vĩ mô MÙ; quant-skeptic)

Dựng **panel sự kiện** mọi deal BAL + LAG trong ledger backtest 2014→2026 (hàng nghìn deal) + toàn bộ deal live (ít, nhưng là OOS thật). Mỗi deal gắn **đặc trưng tại ngày vào, PIT, không nhìn tương lai**:

| Nhóm | Đặc trưng (nguồn đã có trong `data_registry`) |
|---|---|
| Vi mô / cơ bản | 8L rating, composite v3 (ey/cfy/ps), PE·PB·PCF vs sàn 3Y/5Y, ROE_Min5Y, ROIC5Y, FSCORE, CF_OA, SUE (LAG), moat/forensic tag |
| Kỹ thuật | mom_200, D_RSI, D_CMF, khoảng cách đỉnh 52T, rvol 20 phiên, ADV %NAV của lệnh |
| Trạng thái thị trường | DT5G state + candidate clock, dd52, breadth tercile `universe_pit`, Value Radar zone (display-only → đây là lần đầu kiểm nó như biến giải thích deal, không phải tín hiệu), VNINDEX PE |
| Vĩ mô | hurdle PIT (mức + xu hướng 3T), spread ey − hurdle (Fed-model), CPI, SBV refi, VIX/SPX dd, USD/VND, tín dụng (`fiinprox_money_credit` UNVERIFIED → chỉ mô tả) |
| Hàng hoá (theo ngành của deal) | hog, cao su, BDI, SunSirs LPG/FO/NH3, WB CMO (thép/dầu/urê); ONI/ENSO cho thuỷ điện |
| Sức khoẻ edge | IC causal tháng trước của chính tín hiệu×ngành (`edge_health_matrix`), LAG 12M pctile (`known_date`), capit edge |

Nhãn: excess vs hurdle trên kỳ nắm giữ; hit = excess > 0.

Phương pháp (theo thứ tự, cố ý KHÔNG bắt đầu bằng ML):
1. Bảng tầng đơn biến: hit-rate và excess trung vị theo decile/nhãn mỗi đặc trưng, IS 2014–19 / OOS 2020+, BH-FDR, N sự kiện độc lập. Kỳ vọng từ prior: breadth/radar/DT5G ~0 (đã thử 0/27), value/quality dương và mạnh lên, momentum chết sau 2020.
2. Tương tác 2 chiều đã có giả thuyết: (H1) LAG × SUE-cao × PE-rẻ; (H2) BAL × ey−hurdle > ngưỡng; (H3) deal ngành hàng hoá × giá hàng hoá đang tăng 3T; (H4) deal vào khi LAG edge pctile < 20 có thua tiết kiệm không; (H5) deal vào khi hurdle đang TĂNG (2011, 2022-23) thua hệ thống.
3. Một mô hình diễn giải được (cây nông ≤3 tầng hoặc logistic ràng buộc đơn điệu), leave-one-year-out; so với baseline "mọi deal" và placebo hoán vị nhãn. PBO/DSR cho họ cấu hình thử.
Deliverable: **bảng phân lớp deal 3 bậc (ĐÁNG / TRUNG TÍNH / BỎ) với luật đọc được bằng mắt**, kèm số deal mỗi lớp mỗi năm — không phải điểm số đen.

## 4. Giai đoạn 3 — Thời điểm an toàn vs tiết kiệm (2–3 tuần, Taylor; Bobby classify regime MÙ trước)

Cấp danh mục: với mỗi ngày t 2008→2026, lợi suất 12T tới của V2.4 (ledger W0-kiểu, chạy liên tục) trừ hurdle PIT; điều kiện theo trạng thái quan sát được tại t (DT5G, dd52, radar, mức & xu hướng hurdle, LAG edge pctile, VIX, breadth). Kết quả = **bảng P(thắng tiết kiệm 12T | trạng thái)** + kích thước thua trung vị khi thua.
Đánh giá như một CHÍNH SÁCH: "về tiết kiệm khi P < x" walk-forward, so với placebo tắt ngẫu nhiên cùng tần suất (đúng cách `amh-adaptivity-review` đã lật tẩy BAL edge-gate) và so với DT5G hiện hành. Prior thẳng thắn: BAL monthly gate NO-GO, DT5G là bảo hiểm không phải máy tăng lợi nhuận ⇒ khả năng cao kết luận là **"mức hurdle tự nó là gate"** (hurdle > ~8–9% thì ey−hurdle âm, cổ phiếu khó thắng tiền gửi) hơn là một bộ lọc regime mới. Nếu đúng vậy, deliverable chỉ là 1 ngưỡng + 1 dòng cảnh báo, không phải cơ chế.

## 5. Giai đoạn 4 — Quyết định (1 tuần, user)

Ba hướng có thể mở ra, user chọn, không tự wire:
- (a) Giữ V2.4, thêm hurdle vào báo cáo + luật "tiền nhàn rỗi mặc định = tiết kiệm/egg, chỉ ra khi deal thuộc lớp ĐÁNG".
- (b) Thu hẹp BAL về lớp ĐÁNG (nếu Giai đoạn 2 xác nhận momentum chết theo thời gian, thay selector bằng value/quality theo `custom30v-selector-roadmap`).
- (c) Re-pin "V2.4-live" (hệ đang chạy thật) làm số tham chiếu mới, bỏ số 23% khỏi mọi kỳ vọng.
Mọi thay đổi production vẫn qua quant-skeptic CONFIRMED + DSR/PBO + IS/OOS.

## 6. Nguồn lực, thứ tự, rủi ro

- Thứ tự cứng: **0 → 1 → (2 ∥ 3) → 4**. Giai đoạn 1 quyết định trọng tâm của 2 và 3; không chạy 2/3 trước 1.
- Tổng ~8–10 tuần lịch; Taylor headless (opus/medium thiết kế, sonnet chạy lặp), Bobby (macro, mù), Winston (merge LAG cache, snapshot pin, vá sort), quant-skeptic sau mỗi giai đoạn, Mike tổng hợp.
- Rủi ro lớn nhất: **N nhỏ** — live chỉ 4 tháng, BAL live 1 deal; mọi kết luận "live" phải nói rõ là 1 mẫu, bằng chứng thật nằm ở panel 2014→2026 + OOS 2020+. Rủi ro thứ hai: data mining qua ~40 đặc trưng × 2 book — khai N trials, PBO, placebo bắt buộc.
- Không làm: không re-tune DT5G, không đổi tham số V2.4 giữa chừng, không dùng `profit_*`/`_center_*` làm feature, không dùng `ticker_prune` cho universe (dùng `universe_pit`).
