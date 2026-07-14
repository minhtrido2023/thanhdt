# LAG-weight (tăng tỷ trọng PEAD)
> Dự án đã đóng — tách khỏi context_pack 2026-07-12. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. ĐÓNG — chấp nhận kết luận mô tả, không tăng trần w_LAG.

## LAG-weight (tăng tỷ trọng PEAD trong allocator) — ĐÓNG, chấp nhận câu trả lời mô tả (2026-07-12)
User chấp nhận kết luận mô tả của Taylor (`plan_lag_weight_20260712.md`) là đủ — KHÔNG chạy family
backtest N=5. Tóm tắt: "LAG bền hơn MOM" đúng một nửa (bền hơn về bề rộng lịch sử, nhưng 2026 hiện
là đáy sâu nhất mẫu); allocator adaptive sẵn có đang nói nên hạ về 50% chứ không phải tăng; capacity
LAG book giới hạn bởi deal-flow (chỉ deploy ~42% vốn) nên tăng trần phần lớn không có tác dụng thật.
Phần fix bug đi kèm (spec-drift w_LAG trong `golive_recommend_v23.py`) đã xong + quant-skeptic
CONFIRMED riêng (commit `a776a9a`). Không mở N-budget mới cho hướng này trừ khi có dữ liệu mới.
