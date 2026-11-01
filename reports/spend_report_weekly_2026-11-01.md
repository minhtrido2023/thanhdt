# Tổng kết sử dụng tuần qua (2026-11-01)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 208 |
| Compute ước tính | 53.7h |
| Log KB | 704 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 9 attempt |
| Commits | 536 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-10-25) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 208 | 135 | +73 | +54% |
| Compute h | 53.7 | 26.6 | +27.1 | +102% |
| Log KB | 704 | 383 | +321 | +84% |
| Commits | 536 | 398 | +138 | +35% |
| Claude haiku | 0 | 0 | +0 | N/A |
| Claude sonnet | 9 | 3 | +6 | +200% |
| Claude opus | 103 | 48 | +55 | +115% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 96 | 84 | +12 | +14% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-11-01_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-11-01_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 125 | 30.7 | 440 | default=22%, opus=74%, sonnet=3% |
| Production | 15 | 0.5 | 25 | default=93%, sonnet=7% |
| Ops | 35 | 1.6 | 83 | default=63%, opus=26%, sonnet=11% |
| Other | 33 | 21.0 | 156 | default=97%, opus=3% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-11-01_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-11-01_commits.png)

## Chi phí theo tầng model / effort

| Model (default≡sonnet) | Effort | Job | Chi phí | % | TB/job | Chạy lại |
|---|---|---|---|---|---|---|
| opus | medium | 97 | $423.8 | 80% | $4.37 | 5/97 |
| sonnet | medium | 102 | $68.3 | 13% | $0.67 | 4/102 |
| opus | high | 6 | $29.7 | 6% | $4.95 | 0/6 |
| sonnet | high | 3 | $7.0 | 1% | $2.34 | 0/3 |

Opus chiếm **86%** chi phí. Luật 2026-10-18: Opus chỉ cho phản biện / chạm tiền-cổng an toàn / thiết kế mới / lỗi chưa rõ nguyên nhân; việc còn lại Sonnet.

## Token / retry watch

- Cache hit: **97%** của prompt tokens (1,579,107,698 read / 1,631,694,158 total).
- Retry / duplicate compute: **9 job** chạy attempt >1, **9 attempt** thêm; 0 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **53.7h** trên 208 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job tăng 73 và compute tăng 27.1h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
