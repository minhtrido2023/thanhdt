# Tổng kết sử dụng tuần qua (2026-09-13)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 74 |
| Compute ước tính | 12.8h |
| Log KB | 133 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 5 attempt |
| Commits | 219 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-09-06) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 74 | 119 | -45 | -38% |
| Compute h | 12.8 | 20.3 | -7.5 | -37% |
| Log KB | 133 | 191 | -58 | -30% |
| Commits | 219 | 242 | -23 | -10% |
| Claude sonnet | 1 | 6 | -5 | -83% |
| Claude opus | 21 | 16 | +5 | +31% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 52 | 97 | -45 | -46% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-09-13_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-09-13_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 28 | 7.6 | 57 | default=54%, opus=43%, sonnet=4% |
| Production | 10 | 0.4 | 5 | default=100% |
| Ops | 15 | 2.9 | 28 | default=53%, opus=47% |
| Other | 21 | 1.9 | 43 | default=90%, opus=10% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-09-13_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-09-13_commits.png)

## Token / retry watch

- Cache hit: **95%** của prompt tokens (687,797,419 read / 724,021,210 total).
- Retry / duplicate compute: **5 job** chạy attempt >1, **5 attempt** thêm; 0 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **12.8h** trên 74 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job giảm 45 và compute giảm 7.5h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
