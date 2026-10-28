# Giám sát độ tươi theo mã — `tav2_bq.commodity_prices` (2026-10-26, Winston)
Job Winston_20261026_073850 (user duyệt). Code `bin/commodity_freshness_monitor.py` + selfcheck
`bin/commodity_freshness_monitor_selfcheck.py`. State `data/commodity_freshness_state.json` (root WorkingClaude).
**CHƯA cài cron, CHƯA gửi kênh nào** — đề xuất ở cuối, chờ user duyệt qua Mike.

## Luật (mỗi khoá `metric_key|source|cadence` tự học)
- gaps = khoảng ngày lịch giữa 2 quan sát liên tiếp, cửa sổ 365 ngày tính ngược từ quan sát CUỐI (mã đang đứng không làm méo phân phối học).
- age = ref − last_obs; ref = hôm nay ICT, chỉ thấy dữ liệu nạp tới 23:00 hôm trước.
- **STALE**: age > max(3×median_gap, p90_gap + 2). Daily → 5 ngày, tuần → 21, tháng → 93, GDT → 42.
- **Lễ theo mùa**: nếu chính mã đó năm trước có gap phủ (ref−364) ± 25 ngày dài hơn ngưỡng, ngưỡng nâng lên gap đó + 2 (Tết/Quốc khánh TQ).
- **FROZEN_VALUE**: số quan sát cuối CÙNG giá ≥ max(3, 2×run dài nhất đã hoàn tất trong cửa sổ + 1). Run 2 ngày (TE mang giá sang ngày lễ, vd BDI 3157 08-31/09-01) CỐ Ý không bắt — quá phổ biến để báo.
- **LOW_SAMPLE**: < 8 gap → không báo.
- Báo cáo stdout CHỈ khi trạng thái đổi (mới cảnh báo / hồi phục / mã mới / mã mất). Ghi json atomic.

## Backtest 12 tháng (2025-10-27 → 2026-10-26, replay từng ngày, 229 khoá)
Lệnh: `python3 bin/commodity_freshness_monitor.py --backtest 2025-10-27 2026-10-26` (1 query BQ ~3,6 MB).
Định nghĩa: STALE GIẢ = mã tự có quan sát mới ≤7 ngày sau lúc báo; FROZEN: không có ca dương tính đã biết ⇒ mọi episode tự hết đều tính GIẢ.

| cấu hình (K, pad, frozen_mult) | STALE giả | FROZEN giả | giả/tuần | tea | salmon |
|---|---|---|---|---|---|
| 3, 2, 1 (công thức gốc) | 6 | 39 (+2 treo) | 0,86 | 10-25 | sót |
| 2, 2, 1 | **270** | 38 (+11) | 5,91 | | |
| 3, 1, 2 | 48 (+3 thật?) | 5 | 1,02 | | |
| 3, 2, 1,5 | 6 | 15 (+1) | 0,40 | | |
| **3, 2, 2 (CHỌN)** | **6** | **5** | **0,21** | **10-25 (age 22)** | **sót tới ≥11-07** |
| 3, 3, 2 | 3 | 5 | 0,15 | +1 ngày trễ mọi mã daily | |

- **Đổi duy nhất so với đề xuất gốc**: frozen_mult 1→2. Lý do: run giá đứng của nhóm TQ/kim loại hiếm (cobalt, phosphorus, molybden…) thường dài hơn mọi run trước đó trong năm → mult=1 báo giả 0,75/tuần riêng phần FROZEN. Cái giá: FROZEN chỉ bắt đóng băng THÔ (≥2× kỷ lục của mã).
- K=2 không dùng được: WB tháng ra số trễ ~35 ngày ⇒ age chạm 63 trước khi có số mới ⇒ 2×31 báo giả cả 22 mã WB mỗi tháng.
- pad=3 giảm 3 báo giả (Tết) nhưng trễ 1 ngày cho MỌI mã daily — giữ pad=2.
- 6 STALE giả: Tết 2026 dài hơn năm trước (aluminum_alloy ×2 khoá, rubber 02-19), palm_oil 03-24, aluminum_alloy ×2 ngày 05-06 (1 ngày). 5 FROZEN giả: phosphate_rock WB (giá phẳng 9 tháng — thật ra WB niêm yết đứng), barley 03-03→16, rhodium 1 ngày, cobalt daily+monthly 07→09.
- **Báo sót đã biết**: tea (dừng sau 10-03, tuần) báo 10-25 = sau 3 kỳ trống. **salmon (cuối 10-16) KHÔNG báo trong kỳ** — 1 kỳ tuần trễ (age 10 < 21); sẽ báo từ 11-07 nếu vẫn không có số. Trade-off của K=3 với mã tuần: nâng độ nhạy cho mã tuần = phải tách luật theo cadence (chưa làm, không tune cho đẹp).
- Giới hạn: replay dùng snapshot bảng HIỆN TẠI (TE backfill một lượt, `fetched_at` không dùng được) ⇒ không tái hiện được những lần TE từng trễ rồi được backfill; số giả/tuần thực tế có thể cao hơn. Lag WB 35 ngày là giả định (CMO ra đầu tháng).

## Hiện trạng 26/10 (ref 2026-10-26)
229 khoá: **228 OK, 1 STALE = `tea|trading_economics|daily`** (last 10-03, age 23 > 21). 0 FROZEN, 0 LOW_SAMPLE. salmon OK (age 10/21). Sát ngưỡng (age 4–5/5, cuối 10-21/22): cobalt, coking_coal, ethanol daily; cobalt_hydroxide, germany_natural_gas_the, scrap_steel, aluminum_alloy, phosphorus monthly — sẽ thành STALE sáng mai nếu lượt nạp 23:00 không có số.

## Đề xuất (CHỜ USER DUYỆT — không tự cài)
- Cron: `30 7 * * * cd /home/trido/thanhdt/WorkingClaude && /usr/bin/python3 mike/bin/commodity_freshness_monitor.py >> mike/logs/commodity_freshness.log 2>&1` (TZ=Asia/Ho_Chi_Minh đã export trong crontab). Trả lời 4 câu hỏi `cron_registry/_adding-cron-policy.md` trước khi cài.
- Kênh: Telegram/Discord Trading Daily chỉ khi stdout không rỗng (mặc định im). Nhiều mã cùng nguồn STALE cùng sáng (vd Tết) ⇒ nên gộp 1 dòng ở tầng gửi.
