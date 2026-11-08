# Tổng kết sử dụng tuần qua (2026-11-08)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 230 |
| Compute ước tính | 29.9h |
| Log KB | 583 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 11 attempt |
| Commits | 439 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-11-01) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 230 | 208 | +22 | +11% |
| Compute h | 29.9 | 53.8 | -23.9 | -44% |
| Log KB | 583 | 704 | -121 | -17% |
| Commits | 439 | 536 | -97 | -18% |
| Claude haiku | 0 | 0 | +0 | N/A |
| Claude sonnet | 29 | 9 | +20 | +222% |
| Claude opus | 129 | 103 | +26 | +25% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 72 | 96 | -24 | -25% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-11-08_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-11-08_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 173 | 26.6 | 493 | default=17%, opus=66%, sonnet=17% |
| Production | 14 | 0.5 | 22 | default=86%, opus=14% |
| Ops | 26 | 1.9 | 43 | default=54%, opus=46% |
| Other | 17 | 1.0 | 25 | default=94%, opus=6% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-11-08_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-11-08_commits.png)

## Chi phí theo tầng model / effort

| Model (default≡sonnet) | Effort | Job | Chi phí | % | TB/job | Chạy lại |
|---|---|---|---|---|---|---|
| opus | medium | 121 | $379.0 | 76% | $3.13 | 2/121 |
| sonnet | medium | 99 | $88.5 | 18% | $0.89 | 5/99 |
| opus | high | 8 | $27.7 | 6% | $3.46 | 4/8 |
| sonnet | high | 2 | $3.9 | 1% | $1.93 | 0/2 |

Opus chiếm **81%** chi phí. Luật 2026-10-18: Opus chỉ cho phản biện / chạm tiền-cổng an toàn / thiết kế mới / lỗi chưa rõ nguyên nhân; việc còn lại Sonnet.

## Token / retry watch

- Cache hit: **96%** của prompt tokens (1,182,482,825 read / 1,229,875,027 total).
- Retry / duplicate compute: **11 job** chạy attempt >1, **11 attempt** thêm; 20 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **29.9h** trên 230 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job tăng 22 và compute giảm 23.9h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
