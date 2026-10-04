# Tổng kết sử dụng tuần qua (2026-10-04)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 214 |
| Compute ước tính | 53.5h |
| Log KB | 454 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 48 attempt |
| Commits | 523 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-09-27) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 214 | 119 | +95 | +80% |
| Compute h | 53.5 | 16.3 | +37.2 | +228% |
| Log KB | 454 | 217 | +237 | +109% |
| Commits | 523 | 352 | +171 | +49% |
| Claude sonnet | 13 | 1 | +12 | +1200% |
| Claude opus | 72 | 45 | +27 | +60% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 129 | 73 | +56 | +77% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-10-04_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-10-04_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 138 | 37.1 | 276 | default=53%, opus=41%, sonnet=7% |
| Production | 15 | 1.0 | 13 | default=93%, sonnet=7% |
| Ops | 32 | 3.5 | 50 | default=44%, opus=47%, sonnet=9% |
| Other | 29 | 11.9 | 115 | default=97%, opus=3% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-10-04_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-10-04_commits.png)

## Token / retry watch

- Cache hit: **97%** của prompt tokens (2,929,104,575 read / 3,012,011,031 total).
- Retry / duplicate compute: **48 job** chạy attempt >1, **48 attempt** thêm; 12 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- ⚠ Có 48 job chạy attempt >1, 48 lần compute thêm (22% của tổng job)

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **53.5h** trên 214 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job tăng 95 và compute tăng 37.2h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường cần hành động**: Có 48 job chạy attempt >1, 48 lần compute thêm (22% của tổng job).
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
