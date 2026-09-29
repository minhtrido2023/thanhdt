# Tổng kết sử dụng tuần qua (2026-08-16)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 198 |
| Compute ước tính | 43.1h |
| Log KB | 834 |
| Offload provider khác Claude | 18 job (9%) |
| Commits | 541 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-08-09) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 198 | 156 | +42 | +27% |
| Compute h | 43.1 | 30.3 | +12.8 | +42% |
| Log KB | 834 | 601 | +233 | +39% |
| Commits | 541 | 368 | +173 | +47% |
| Claude sonnet | 4 | 0 | +4 | N/A |
| Claude opus | 122 | 105 | +17 | +16% |
| Claude fable | 0 | 1 | -1 | -100% |
| Claude default | 54 | 41 | +13 | +32% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-08-16_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-08-16_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 95 | 24.1 | 541 | codex=9%, default=14%, opencode=3%, opus=73%, sonnet=1% |
| Production | 25 | 4.3 | 41 | default=52%, opus=40%, sonnet=8% |
| Ops | 59 | 12.2 | 232 | codex=5%, default=22%, opencode=5%, opus=66%, sonnet=2% |
| Other | 19 | 2.5 | 20 | default=79%, opus=21% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-08-16_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-08-16_commits.png)

## Cảnh báo effort / model

- Không có cảnh báo nào vượt ngưỡng effort=high hoặc fable.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **43.1h** trên 198 job, offload provider khác Claude chiếm 9% job.
- **So với tuần trước**: job tăng 42 và compute tăng 12.8h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
