# Tổng kết sử dụng tuần qua (2026-10-18)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 108 |
| Compute ước tính | 17.6h |
| Log KB | 281 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 11 attempt |
| Commits | 346 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-10-11) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 108 | 106 | +2 | +2% |
| Compute h | 17.6 | 25.9 | -8.3 | -32% |
| Log KB | 281 | 269 | +12 | +4% |
| Commits | 346 | 357 | -11 | -3% |
| Claude haiku | 0 | 0 | +0 | N/A |
| Claude sonnet | 3 | 13 | -10 | -77% |
| Claude opus | 57 | 53 | +4 | +8% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 48 | 40 | +8 | +20% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-10-18_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-10-18_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 57 | 12.1 | 197 | default=18%, opus=81%, sonnet=2% |
| Production | 11 | 0.2 | 15 | default=82%, sonnet=18% |
| Ops | 24 | 4.8 | 44 | default=58%, opus=42% |
| Other | 16 | 0.5 | 25 | default=94%, opus=6% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-10-18_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-10-18_commits.png)

## Token / retry watch

- Cache hit: **96%** của prompt tokens (1,113,933,911 read / 1,155,745,316 total).
- Retry / duplicate compute: **11 job** chạy attempt >1, **11 attempt** thêm; 5 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- ⚠ Có 11 job chạy attempt >1, 11 lần compute thêm (10% của tổng job)

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **17.6h** trên 108 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job tăng 2 và compute giảm 8.3h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường cần hành động**: Có 11 job chạy attempt >1, 11 lần compute thêm (10% của tổng job).
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
