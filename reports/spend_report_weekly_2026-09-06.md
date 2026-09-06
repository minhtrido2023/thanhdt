# Tổng kết sử dụng tuần qua (2026-09-06)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 110 |
| Compute ước tính | 18.8h |
| Log KB | 183 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 6 attempt |
| Commits | 225 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-08-30) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 110 | 128 | -18 | -14% |
| Compute h | 18.8 | 19.3 | -0.5 | -2% |
| Log KB | 183 | 232 | -49 | -21% |
| Commits | 225 | 279 | -54 | -19% |
| Claude sonnet | 6 | 1 | +5 | +500% |
| Claude opus | 15 | 21 | -6 | -29% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 89 | 106 | -17 | -16% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-09-06_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-09-06_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 62 | 13.7 | 97 | default=82%, opus=8%, sonnet=10% |
| Production | 4 | 0.2 | 2 | default=100% |
| Ops | 21 | 3.1 | 26 | default=62%, opus=38% |
| Other | 23 | 1.9 | 58 | default=91%, opus=9% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-09-06_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-09-06_commits.png)

## Token / retry watch

- Cache hit: **92%** của prompt tokens (899,796,960 read / 980,450,344 total).
- Retry / duplicate compute: **6 job** chạy attempt >1, **6 attempt** thêm; 0 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **18.8h** trên 110 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job giảm 18 và compute giảm 0.5h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
