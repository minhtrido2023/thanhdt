# REPORT_R2 — phương án B bank-nodata, vòng 2 (áp required_change của arch-reviewer)

**Kết luận:** cả 4 điểm đã sửa, commit `d2fe7a2d5` (nhánh `session/bank-nodata-fail-closed-20261119`, trên `be7b01fa5`).
Lỗi điểm 1 tái hiện được trên `be7b01fa5` (MBB 2→4 không cảnh báo) và bản sửa bắt được. Selfcheck cổng 69 ok/0 fail,
3 selfcheck cũ + `rating8l_eff_guard` PASS, cả `env -u TZ` và `TZ=Asia/Tokyo`; `tz_anchor_gate.py` rc=0.
Chưa merge, chưa regen `rating_8l_history.csv`, không ghi BQ, không gửi Discord/bus thật (notify + bus = script giả).

## 1. G4 vô hiệu do thứ tự cron
- **Trước (`be7b01fa5`):** `_write_lens_snapshot(lens)` chụp lens HÔM NAY trong khi nhãn csv là của 19:20 hôm trước.
  Test D0/D1/D2 chạy trên bản cũ: `FAIL: T10 D2 ... G4 BẬT` và `FAIL: T10 D2 MBB KHÔNG bị hạ 2→4`; log: `MBB 2->4(bank-nodata)`.
- **Sau:** chọn GIỮ G4, snapshot = `set(lens) | set(live_map)` (live_map = mã csv chấm bằng lens thật). Lý do: bỏ G4 sẽ mất
  lưới cho ca "mã vừa mất lens", và sửa 1 dòng là đủ, không thêm cơ chế. D1: snapshot giữ MBB (csv cũ còn chấm thật) ⇒ D2 G4 bật, MBB giữ 2.
- Đột biến `snapshot=lens-only` (= `be7b01fa5`): 2 assertion FAIL như mong đợi.
- Giới hạn còn lại: mã bank MỚI vào csv bằng nodata ngay lần đầu (chưa từng có lens) không có gì để G4 so — G2/G3 phủ.

## 2. Hai nhánh SKIPPED
- **Trước:** chỉ `print` + `return out` (5 mã giữ proxy ≤3 như cổng bật, không ai biết).
- **Sau:** gọi `_bank_gate_alert(..., send=live_run, reasons=[...])` kèm lý do thật (đường dẫn + `type(e).__name__: e`; hoặc danh sách cột thật).
- Test T11 cho 3 ca (csv vắng / csv 0 byte / thiếu cột `note`): sink có nội dung + nêu lỗi thật; live_run ⇒ notify + 1 bus event; run thí nghiệm ⇒ chỉ sink.

## 3. `_is_live_run`
- Tách hàm thuần `_is_live_run(path, canon, env)`. T12: canonical⇒True; `R8L_HIST_OUT=/tmp/x`⇒False; `R8L_HIST_BQ_REFRESH=1`⇒True; `=0`⇒False; symlink tới canonical⇒True.
- Wiring main() kiểm bằng AST (cấu trúc, không chạy main vì main cần BQ). Đột biến chạy thật:
  `live_run=False ở lệnh gọi` ⇒ wiring FAIL (bị bắt); `_live_run = False` ⇒ bị bắt.

## 4. Dấu vết bền
- Chọn **bus event** `append_event.sh Winston warning fa_ratings_8l-bank-nodata-gate '<json reasons>'` thay vì state file: không phải sửa
  checker nào, kênh Mike/ops đã quét. Chỉ ở live_run và không ở `MIKE_BOT_TEST_MODE=1`; payload có `notify_error` (rc+stderr thật hoặc exception) nếu notify hỏng.
- Dedup: marker `data/bank_gate_alert_marker.json` = sha1(reasons + ngày ICT + notify_lỗi?), ghi atomic SAU khi append rc=0. **Giới hạn:**
  sang ngày mới hoặc bộ lý do đổi thì ghi lại; dedup chỉ áp cho bus, Discord vẫn gửi mỗi run live.
- T13: event đúng 1 lần; dedup cùng ngày; reasons đổi ⇒ ghi mới; run thí nghiệm / TEST_MODE ⇒ 0 bus; notify rc=3 ⇒ event chứa `rc=3` + `BOOM-stderr`; notify không tồn tại ⇒ event chứa lỗi thật.

## Bằng chứng chạy (cuối output)
```
TZ=unset      rating_8l_history_bank_nodata_gate_selfcheck  PASS: 69 ok, 0 fail
TZ=Asia/Tokyo rating_8l_history_bank_nodata_gate_selfcheck  PASS: 69 ok, 0 fail
(cả 2 TZ) rating_8l_history_bank_aq_selfcheck VERDICT PASS · rating_8l_bank_nodata_selfcheck PASS: 14 ok · rating8l_eff_guard_selfcheck 51 PASS/0 FAIL
[T12] mutation live_run=False ở lệnh gọi / _live_run = False: wiring check FAIL như mong đợi
[T9] max→proxy-only: 3 FAIL · bỏ cổng chặn: 14 FAIL · [T10] snapshot=lens-only: 2 FAIL
[T8] e2e thật: ABB=4 BAB=4 BVB=4 KLB=4 NVB=5 PCB=4 PGB=4 SGB=5 VAB=4 VBB=4
tz_anchor_gate.py (2 file sửa) rc=0
```
Lưu ý merge: lần chạy live đầu chưa có snapshot ⇒ G4 bỏ qua (chỉ G2/G3); snapshot được tạo ở run live đầu khi cổng không bật.
