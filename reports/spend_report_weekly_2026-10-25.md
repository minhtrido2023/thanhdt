# Tổng kết sử dụng tuần qua (2026-10-25)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 135 |
| Compute ước tính | 26.6h |
| Log KB | 383 |
| Offload provider khác Claude | 0 job (0%) |
| Retry / compute thêm | 4 attempt |
| Commits | 398 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-10-18) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 135 | 110 | +25 | +23% |
| Compute h | 26.6 | 18.2 | +8.4 | +46% |
| Log KB | 383 | 291 | +92 | +32% |
| Commits | 398 | 355 | +43 | +12% |
| Claude haiku | 0 | 0 | +0 | N/A |
| Claude sonnet | 3 | 3 | +0 | +0% |
| Claude opus | 48 | 59 | -11 | -19% |
| Claude fable | 0 | 0 | +0 | N/A |
| Claude default | 84 | 48 | +36 | +75% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-10-25_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-10-25_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 68 | 22.1 | 212 | default=38%, opus=57%, sonnet=4% |
| Production | 16 | 0.3 | 28 | default=100% |
| Ops | 26 | 1.8 | 58 | default=69%, opus=31% |
| Other | 25 | 2.4 | 85 | default=96%, opus=4% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-10-25_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-10-25_commits.png)

## Chi phí theo tầng model / effort

| Model (default≡sonnet) | Effort | Job | Chi phí | % | TB/job | Chạy lại |
|---|---|---|---|---|---|---|
| opus | medium | 43 | $171.2 | 68% | $3.98 | 3/43 |
| sonnet | medium | 84 | $59.4 | 24% | $0.71 | 1/84 |
| opus | high | 5 | $15.2 | 6% | $3.04 | 0/5 |
| sonnet | high | 3 | $4.7 | 2% | $1.58 | 0/3 |

Opus chiếm **74%** chi phí. Luật 2026-10-18: Opus chỉ cho phản biện / chạm tiền-cổng an toàn / thiết kế mới / lỗi chưa rõ nguyên nhân; việc còn lại Sonnet.

## Token / retry watch

- Cache hit: **96%** của prompt tokens (952,902,395 read / 988,456,876 total).
- Retry / duplicate compute: **4 job** chạy attempt >1, **4 attempt** thêm; 1 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **26.6h** trên 135 job, offload provider khác Claude chiếm 0% job.
- **So với tuần trước**: job tăng 25 và compute tăng 8.4h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
