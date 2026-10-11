# Tổng kết sử dụng tuần qua (2026-10-11)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 107 |
| Compute ước tính | 26.6h |
| Log KB | 279 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 18 attempt |
| Commits | 366 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-10-04) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 107 | 214 | -107 | -50% |
| Compute h | 26.6 | 53.5 | -26.9 | -50% |
| Log KB | 279 | 454 | -175 | -39% |
| Commits | 366 | 521 | -155 | -30% |
| Claude sonnet | 13 | 13 | +0 | +0% |
| Claude opus | 54 | 72 | -18 | -25% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 40 | 129 | -89 | -69% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-10-11_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-10-11_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 50 | 21.4 | 171 | default=4%, opus=82%, sonnet=14% |
| Production | 10 | 0.3 | 11 | default=100% |
| Ops | 27 | 3.1 | 58 | default=33%, opus=44%, sonnet=22% |
| Other | 20 | 1.8 | 39 | default=95%, opus=5% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-10-11_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-10-11_commits.png)

## Token / retry watch

- Cache hit: **96%** của prompt tokens (1,290,228,573 read / 1,337,423,786 total).
- Retry / duplicate compute: **18 job** chạy attempt >1, **18 attempt** thêm; 1 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- ⚠ Có 18 job chạy attempt >1, 18 lần compute thêm (17% của tổng job)

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **26.6h** trên 107 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job giảm 107 và compute giảm 26.9h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường cần hành động**: Có 18 job chạy attempt >1, 18 lần compute thêm (17% của tổng job).
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
