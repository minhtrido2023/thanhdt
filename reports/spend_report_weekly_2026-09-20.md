# Tổng kết sử dụng tuần qua (2026-09-20)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 88 |
| Compute ước tính | 14.9h |
| Log KB | 195 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 6 attempt |
| Commits | 298 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-09-13) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 88 | 75 | +13 | +17% |
| Compute h | 14.9 | 13.0 | +1.9 | +15% |
| Log KB | 195 | 135 | +60 | +44% |
| Commits | 298 | 218 | +80 | +37% |
| Claude sonnet | 2 | 1 | +1 | +100% |
| Claude opus | 42 | 21 | +21 | +100% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 44 | 53 | -9 | -17% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-09-20_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-09-20_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 31 | 7.7 | 95 | default=13%, opus=81%, sonnet=6% |
| Production | 11 | 0.7 | 7 | default=100% |
| Ops | 25 | 4.6 | 55 | default=40%, opus=60% |
| Other | 21 | 1.9 | 38 | default=90%, opus=10% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-09-20_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-09-20_commits.png)

## Token / retry watch

- Cache hit: **97%** của prompt tokens (1,027,587,680 read / 1,063,648,223 total).
- Retry / duplicate compute: **6 job** chạy attempt >1, **6 attempt** thêm; 0 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **14.9h** trên 88 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job tăng 13 và compute tăng 1.9h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
