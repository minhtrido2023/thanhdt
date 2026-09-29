# Tổng kết sử dụng tuần qua (2026-08-30)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 104 |
| Compute ước tính | 16.6h |
| Log KB | 192 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 13 attempt |
| Commits | 275 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-08-23) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 104 | 152 | -48 | -32% |
| Compute h | 16.6 | 30.7 | -14.1 | -46% |
| Log KB | 192 | 287 | -95 | -33% |
| Commits | 275 | 488 | -213 | -44% |
| Claude sonnet | 1 | 5 | -4 | -80% |
| Claude opus | 26 | 75 | -49 | -65% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 77 | 72 | +5 | +7% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-08-30_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-08-30_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 50 | 10.5 | 92 | default=72%, opus=26%, sonnet=2% |
| Production | 11 | 0.8 | 10 | default=100% |
| Ops | 20 | 2.4 | 44 | default=50%, opus=50% |
| Other | 23 | 2.9 | 46 | default=87%, opus=13% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-08-30_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-08-30_commits.png)

## Token / retry watch

- Cache hit: **93%** của prompt tokens (861,281,779 read / 922,524,084 total).
- Retry / duplicate compute: **13 job** chạy attempt >1, **13 attempt** thêm; 0 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- ⚠ Có 13 job chạy attempt >1, 13 lần compute thêm (12% của tổng job).

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **16.6h** trên 104 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job giảm 48 và compute giảm 14.1h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường cần hành động**: Có 13 job chạy attempt >1, 13 lần compute thêm (12% của tổng job)..
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
