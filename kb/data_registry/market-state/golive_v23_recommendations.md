---
kind: script-output
status: DERIVED
source: golive_v23_recommendations_<date>.csv + data/golive_v23_status.json
group: market-state
writer: golive_recommend_v23.py (đọc dt5g_live)
role: ẢNH CHỤP CỦA PHIÊN — status JSON bị GHI ĐÈ mỗi lần chạy; lịch sử đọc ở BQ recommend_v23
---

# golive_v23_recommendations_<date>.csv + data/golive_v23_status.json

**Status: DERIVED**

## Là gì
Khuyến nghị BAL/LAG/CAPIT hàng ngày (CSV + MD, tên CÓ ngày) và **`data/golive_v23_status.json`** —
ảnh chụp trạng thái allocator/CAPIT/breadth của **RIÊNG phiên vừa chạy** (tên file KHÔNG có ngày).

## Ai ghi / cadence
`golive_recommend_v23.py`, đọc `dt5g_live` (đã fix 2026-07-11, trước đó đọc nhầm base).
Chạy trong `bq_freshness_check.sh` [pipeline-2] ~19:00 ICT T2-T6.

## ⚠️ Bẫy #1 — `golive_v23_status.json` là SNAPSHOT BỊ GHI ĐÈ, KHÔNG phải sổ lịch sử
File bị **ghi đè toàn bộ mỗi phiên**. Mọi field trong đó là **điều kiện/kết quả TÍNH LẠI TỪ ĐẦU
cho ngày chạy**, không mang trạng thái tích luỹ nào:
- `capit_signal_today` (tên cũ `capit_fired`, còn giữ làm alias) = gate breadth **của riêng ngày
  chạy**. Breadth rớt dưới `washout_gate` ⇒ cờ về `false` và `basket`/`capit_size`/
  `n_capit_basket` về rỗng/0 **NGAY**, kể cả khi vị thế THẬT vẫn đang giữ.
- Đây là nguyên nhân sự cố visibility 2026-07-29→07-31: mọi kênh báo cáo gate theo cờ này ⇒ im
  lặng hoàn toàn về CAPIT trong khi còn đủ 5 mã (NCT/PVT/SAB/SIP/VNM) ở cả 2 account (verify DNSE
  07-31). Chi tiết: `mike/agents/Taylor/research/capit_state_visibility_gap_20260731.md`.
- **Muốn biết "CÓ ĐANG GIỮ CAPIT không" ⇒ đọc [`capit_episode.md`](capit_episode.md)**
  (`data/capit_episode.json`, và key `capit_episode_open` được bơm vào chính status JSON từ
  2026-07-31), **KHÔNG** đọc `capit_signal_today`. Gate báo cáo đúng =
  `capit_signal_today OR capit_episode_open`.

## ⚠️ Bẫy #2 — cần số của NGÀY KHÁC hôm nay thì KHÔNG có ở đây
Không tồn tại `golive_v23_status_<date>.json`. Nguồn lịch sử chuẩn tắc =
**[`recommend_v23_bq.md`](recommend_v23_bq.md)** (BQ `recommend_v23.status` / `.recommendations`,
partition theo `signal_date`, do [pipeline-3] push mỗi phiên). CSV/MD `_<date>` trong
`deploy_golive_dt5g_v4/out/` vẫn có tên theo ngày nhưng là artifact trên đĩa (có thể bị dọn hoặc
bị chạy-lại ghi đè — coding_guidelines §8), không phải sổ lịch sử được bảo đảm.

## Bẫy #3 — state source
Kiểm tra `state_source` field = `DT5G_macro`, không phải suy đoán.

↩ [Nhóm market-state](index.md)
