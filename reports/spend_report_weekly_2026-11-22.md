# Tổng kết sử dụng tuần qua (2026-11-22)

Báo cáo cho CEO — quản lý chi phí token/compute của đội. Số liệu được lấy từ `bus/jobs/*.json` và `git log` trong 7 ngày gần nhất; biểu đồ và so sánh tuần trước được tạo tự động.

## Tóm tắt

| Chỉ số | Giá trị |
|---|---|
| Số job headless dispatch | 136 |
| Compute ước tính | 14.3h |
| Log KB | 321 |
| Offload provider khác Claude | 3 job (2%) |
| Retry / compute thêm | 4 attempt |
| Commits | 329 |

## So sánh với tuần trước

| Chỉ số | Tuần này | Tuần trước (2026-11-15) | Thay đổi | % |
|---|---|---|---|---|
| Số job | 136 | 204 | -68 | -33% |
| Compute h | 14.3 | 32.4 | -18.1 | -56% |
| Log KB | 321 | 652 | -331 | -51% |
| Commits | 329 | 384 | -55 | -14% |
| Claude haiku | 0 | 0 | +0 | N/A |
| Claude sonnet | 19 | 17 | +2 | +12% |
| Claude opus | 42 | 105 | -63 | -60% |
| Claude fable | 2 | 1 | +1 | +100% |
| Claude default | 70 | 81 | -11 | -14% |

## Phân bổ compute / job theo nhóm

![Compute hours by category](charts/spend_report_weekly_2026-11-22_hours.png)

![Jobs by category](charts/spend_report_weekly_2026-11-22_jobs.png)

## Chi tiết theo nhóm

| Nhóm | Jobs | Compute h | Log KB | Model mix |
|---|---|---|---|---|
| Research | 76 | 11.2 | 226 | default=24%, fable=3%, opencode=4%, opus=47%, sonnet=22% |
| Production | 14 | 0.3 | 17 | default=100% |
| Ops | 29 | 2.1 | 47 | default=76%, opus=17%, sonnet=7% |
| Other | 17 | 0.7 | 31 | default=94%, opus=6% |

## Model / provider mix

![Model/provider mix](charts/spend_report_weekly_2026-11-22_models.png)

## Commits by type

![Commits by type](charts/spend_report_weekly_2026-11-22_commits.png)

## Chi phí theo tầng model / effort

| Model (default≡sonnet) | Effort | Job | Chi phí | % | TB/job | Chạy lại |
|---|---|---|---|---|---|---|
| opus | medium | 36 | $129.9 | 54% | $3.61 | 0/36 |
| sonnet | medium | 88 | $67.1 | 28% | $0.76 | 4/88 |
| opus | high | 6 | $25.9 | 11% | $4.32 | 0/6 |
| fable | high | 2 | $15.1 | 6% | $7.56 | 0/2 |
| sonnet | high | 1 | $0.4 | 0% | $0.40 | 0/1 |

Opus chiếm **65%** chi phí. Luật 2026-10-18: Opus chỉ cho phản biện / chạm tiền-cổng an toàn / thiết kế mới / lỗi chưa rõ nguyên nhân; việc còn lại Sonnet.

## Token / retry watch

- Cache hit: **96%** của prompt tokens (691,120,690 read / 721,794,824 total).
- Retry / duplicate compute: **4 job** chạy attempt >1, **4 attempt** thêm; 2 job có prompt resume/re-dispatch.

## Cảnh báo effort / model / retry

- Không có cảnh báo nào vượt ngưỡng effort, fable hoặc retry.

## Nhận xét của quản lý

Với góc nhìn quản lý chi phí, tôi đánh giá tuần này như sau:

- **Mức sử dụng**: tổng compute ước tính là **14.3h** trên 136 job, offload provider khác Claude chiếm 2% job.
- **So với tuần trước**: job giảm 68 và compute giảm 18.1h. Cần theo dõi nếu compute tăng nhanh hơn số job.
- **Tiến bộ**: pipeline đo lường đã tách provider offload khỏi quota Claude, báo cáo tuần đã tự động so sánh WoW và có biểu đồ. Việc này giúp CEO nhìn xu hướng thay vì chỉ đọc bảng số.
- **Bất thường**: chưa phát hiện bất thường lớn ngoài biến động thường theo khối lượng công việc.
- **Đề xuất**: giữ mặc định `effort=medium` cho việc audit/fix thường; chỉ dùng `effort=high` hoặc model cao hơn cho việc thực sự phức tạp. Tuần sau script sẽ tự so tiếp với tuần này để phát hiện drift sớm.

---
Báo cáo tự động bởi `bin/spend_report_weekly.py`. Nếu email miss, kiểm tra `state/spend_report_emailed.json` và `logs/spend_report_weekly.log`.
