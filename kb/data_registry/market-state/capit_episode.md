---
kind: script-output
status: CANONICAL (quan sát thuần — KHÔNG có consumer quyết định)
source: data/capit_episode.json
group: market-state
writer: capit_episode.py — gọi từ golive_recommend_v23.py §6b (~19:00 T2-T6)
role: SỔ "ĐANG GIỮ CAPIT HAY KHÔNG" — câu hỏi mà capit_signal_today KHÔNG trả lời
---

# `data/capit_episode.json`

**Status: CANONICAL** cho câu hỏi *"có đang giữ vị thế CAPIT không"*. Mới từ **2026-07-31**
(commit `49858bd`, job Taylor_20260731_031434).

## Là gì
Sổ episode CAPIT: mở 1 episode khi gate breadth chuyển False→True (ghi `entry_signal_date`, rổ
GỐC, `size`, `qty_filled` theo account từ fill THẬT của broker), đóng khi có **bằng chứng vị thế
broker = 0 cho TOÀN BỘ rổ ở MỌI account live** (ảnh chụp ≤7 ngày) hoặc đóng tay
(`python capit_episode.py --close <episode_id> --note "..."`).
`golive_recommend_v23.py` bơm các field quan sát vào status JSON: `capit_episode_open`,
`capit_episode_id`, `capit_episode_entry_date`, `capit_episode_basket`, `capit_episode_size`,
`capit_sessions_held`, `capit_episode_remaining_qty`, `capit_episode_error`.

## Vì sao tồn tại
`capit_signal_today`/`capit_fired` là **điều kiện của ngày chạy**, tắt ngay khi breadth rớt dưới
gate ⇒ 07-29→07-31 mọi kênh báo cáo im lặng về CAPIT dù còn giữ đủ 5 mã ở 2 account. Xem
`mike/agents/Taylor/research/capit_state_visibility_gap_20260731.md` và
[`golive_v23_recommendations.md`](golive_v23_recommendations.md) §Bẫy #1.

## Ai đọc
- `telegram_recommend.py` — khối "CAPIT v2 monitor" (có **fallback đọc thẳng file này** khi status
  JSON chưa có key episode: telegram 18:00 chạy TRƯỚC golive 19:00 ⇒ status luôn là bản phiên trước).
- `mike/bin/bq_freshness_check.sh` — note CAPIT bơm vào prompt lập plan của DollarBill
  (gate `capit_signal_today OR capit_episode_open`, từ 2026-07-31).
- Hàm đọc-thuần cho consumer báo cáo: `capit_episode.observe()` (không gọi broker, không ghi,
  không raise).

## Bẫy #1 — QUAN SÁT THUẦN, cấm biến thành đầu vào quyết định
Module được gọi **bên NGOÀI** nhánh `if capit_signal_today:` và chỉ ĐỌC basket/size đã tính xong.
Không chọn mã, không tính size, không chặn lệnh. Đừng wire nó vào đường sinh lệnh.

## Bẫy #2 — auto-close cố ý CHẬM (sai về phía "hiện lâu hơn thực tế")
Vị thế broker không mang nhãn book: PVT/SIP vừa thuộc rổ CAPIT vừa thuộc custom30V parking ⇒
không tách được "bao nhiêu cổ là CAPIT". Vì vậy chỉ auto-close khi **cả rổ về 0 ở mọi account**.
Còn dư cổ vì lý do khác ⇒ episode **vẫn mở**. Đọc `capit_episode_open=true` là "chưa có bằng
chứng đã thoát hết", không phải "chắc chắn còn nguyên vị thế CAPIT".

## Bẫy #3 — exit CAPIT do NGƯỜI quyết
Đường LIVE không có dòng code nào bán vị thế CAPIT (`CAPIT_HOLD=60` chỉ sống trong backtest/paper).
Đừng suy ra ngày thoát từ quy tắc hold nào cả — chỉ tin bằng chứng vị thế broker.

## Bẫy #4 — rổ trong sổ là rổ GỐC lúc vào lệnh
`golive` tính LẠI rổ mỗi ngày và rổ co dần (5→4→3 trong 07-20→07-28). Sổ giữ rổ GỐC — đúng cho
câu hỏi "đã mua gì", KHÔNG dùng làm rổ khuyến nghị của hôm nay.

↩ [Nhóm market-state](index.md)
