# Tổng kết sử dụng tuần qua (2026-08-23)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 147 |
| Compute ước tính | 28.8h |
| Log KB | 268 |
| Offload provider khác Claude | 2 job (1%) |
| Retry / compute thêm | 30 attempt |
| Commits | 466 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-08-16) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 147 | 197 | -50 | -25% |
| Compute h | 28.8 | 42.3 | -13.5 | -32% |
| Log KB | 268 | 829 | -561 | -68% |
| Commits | 466 | 541 | -75 | -14% |
| Claude sonnet | 5 | 4 | +1 | +25% |
| Claude opus | 72 | 121 | -49 | -40% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 68 | 54 | +14 | +26% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-08-23_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-08-23_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 64 | 13.7 | 138 | codex=2%, default=30%, opus=62%, sonnet=6% |
| Production | 14 | 0.9 | 15 | default=79%, opus=14%, sonnet=7% |
| Ops | 45 | 12.3 | 80 | codex=2%, default=36%, opus=62% |
| Other | 24 | 2.0 | 35 | default=92%, opus=8% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-08-23_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-08-23_commits.png)

## Token / retry watch

- Cache hit: **94%** của prompt tokens (1,556,432,640 read / 1,650,325,008 total).
- Retry / duplicate compute: **30 job** chạy attempt >1, **30 attempt** thêm; 4 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- ⚠ Có 30 job chạy attempt >1, 30 lần compute thêm (20% của tổng job).

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **28.8h** trên 147 job, offload provider khác Claude chiếm 1% job.
- **So với tuần trước**: job giảm 50 và compute giảm 13.5h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường cần hành động**: Có 30 job chạy attempt >1, 30 lần compute thêm (20% của tổng job)..
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
