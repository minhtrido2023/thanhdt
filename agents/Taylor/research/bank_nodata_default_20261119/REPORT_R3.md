# REPORT_R3 — bank-nodata, vòng 3 (Mike tự sửa theo arch-reviewer NEEDS_CHANGES, user duyệt hướng A 19/11 22:53 ICT)

Nhánh `session/bank-nodata-fail-closed-20261119`, trên `d2fe7a2d5`. Chưa merge, chưa regen csv, không ghi BQ/bus thật.

## Thay đổi (rating_8l_history.py + selfcheck cổng)
1. **G4 xét `bad` (nodata ∪ noROE)** thay vì chỉ `nodata` — noROE = mã CÒN trong lens nhưng ROE NaN, G2 không thấy được.
   Tái hiện của reviewer (MBB 2→4, không cảnh báo) nay bật G4, MBB giữ 2.
2. **Snapshot = `live_map | (lens − nodata_map)`**: noROE dai dẳng không vào snapshot ⇒ G4 không dính vĩnh viễn.
3. **Lời khai bus sửa đúng phạm vi** (docstring `_bank_gate_bus_event`): event `warning` chỉ vào events_buffer.md + tóm tắt
   #mike; KHÔNG vào delta-append (mike_json.py chỉ finding/answer/decision/verification), ops_health_check không quét.
   ⇒ **REPORT_R2 §4 ("kênh Mike/ops đã quét") SAI — đọc bản này thay thế.** Kênh chủ động vẫn là Discord.
4. Comment ngưỡng G3 sửa: mất ROE 1-2 mã do G4 bắt.

## Selfcheck
- Cổng: 69 → 81 ok / 0 fail. Thêm T14 (noROE 3 ngày, kèm assert snapshot KHÔNG bị ghi đè khi cổng bật), T15 (noROE dai dẳng).
- 3 đột biến mới đều bị bắt: "G4 chỉ dùng nodata" (3 fail), "snapshot ghi cả khi cổng bật" (1 fail — đột biến Mike tìm ra, vòng 2 chưa có assert),
  "snapshot không trừ nodata_map" (3 fail).
- Cả 4 selfcheck PASS dưới `env -u TZ` và `TZ=Asia/Tokyo` (nodata 14/0, bank_aq PASS, eff_guard 51/0); `tz_anchor_gate.py` rc=0.

## Còn mở (không chặn)
- G4 đã bật thì dính tới khi sửa snapshot bằng tay; chưa có mục runbook. Discord không dedup (post mỗi run live khi cổng dính).
