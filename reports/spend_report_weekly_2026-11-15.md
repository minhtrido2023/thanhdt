# Tổng kết sử dụng tuần qua (2026-11-15)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 204 |
| Compute ước tính | 32.3h |
| Log KB | 652 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 14 attempt |
| Commits | 385 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-11-08) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 204 | 230 | -26 | -11% |
| Compute h | 32.3 | 30.0 | +2.3 | +8% |
| Log KB | 652 | 583 | +69 | +12% |
| Commits | 385 | 439 | -54 | -12% |
| Claude haiku | 0 | 0 | +0 | N/A |
| Claude sonnet | 17 | 29 | -12 | -41% |
| Claude opus | 105 | 129 | -24 | -19% |
| Claude fable | 1 | 0 | +1 | N/A |
| Claude default | 81 | 72 | +9 | +12% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-11-15_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-11-15_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 123 | 26.5 | 421 | default=21%, fable=1%, opus=66%, sonnet=12% |
| Production | 15 | 0.5 | 36 | default=80%, opus=13%, sonnet=7% |
| Ops | 35 | 2.8 | 68 | default=37%, opus=60%, sonnet=3% |
| Other | 31 | 2.6 | 127 | default=97%, opus=3% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-11-15_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-11-15_commits.png)

## Chi phí theo tầng model / effort

| Model (default≡sonnet) | Effort | Job | Chi phí | % | TB/job | Chạy lại |
|---|---|---|---|---|---|---|
| opus | medium | 92 | $297.2 | 69% | $3.23 | 4/92 |
| sonnet | medium | 94 | $74.1 | 17% | $0.79 | 8/94 |
| opus | high | 13 | $47.1 | 11% | $3.62 | 2/13 |
| sonnet | high | 4 | $6.2 | 1% | $1.55 | 0/4 |
| fable | medium | 1 | $4.0 | 1% | $4.02 | 0/1 |

Opus chiếm **80%** chi phí. Luật 2026-10-18: Opus chỉ cho phản biện / chạm tiền-cổng an toàn / thiết kế mới / lỗi chưa rõ nguyên nhân; việc còn lại Sonnet.

## Token / retry watch

- Cache hit: **96%** của prompt tokens (1,131,594,116 read / 1,175,267,406 total).
- Retry / duplicate compute: **14 job** chạy attempt >1, **14 attempt** thêm; 8 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **32.3h** trên 204 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job giảm 26 và compute tăng 2.3h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
