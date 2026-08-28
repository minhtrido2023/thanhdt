# 2026-08-28 — Guard JSON của `append_event.sh` ĐOÁN MÒ "bị cắt cụt" cho mọi ca ⇒ dispatch ops-autofix mở đầu bằng chẩn đoán sai

**Phát hiện:** `ops_health_check.sh --account SpaceX` (02:02Z) báo 1 bản ghi cách ly trong 24h,
agent `Taylor`, lý do chép nguyên văn từ `append_event.sh`: *"payload bắt đầu bằng '{' hoặc '['
nhưng KHÔNG phải JSON hợp lệ — nhiều khả năng bị cắt cụt."* Dispatch tới Winston qua `ops_autofix`
(job `Winston_20260828_020258`).

## Sự thật 1: KHÔNG mất event

Bản ghi bị chặn là `answer` của Taylor, topic
`Wags/capit-lever-selfcheck-stale-pin-needs-taylor`, job `Taylor_20260828_012307`,
ts `2026-08-28T01:48:25Z`. Taylor tự ghi lại thành công **29 giây** sau — event
`6c3a5654-e770-47dd-bc45-7484d057d9d3` (`2026-08-28T01:48:54Z`), cùng topic, cùng trace_id.
Đối chiếu: đủ 8 key top-level (`verdict`, `quyet_dinh_pin_nao_dung`,
`cong_NGUOI_thu_hai_KHONG_bi_bo`, `da_va`, `con_do_2_ca`, `patch_de_xuat_cho_L2_L3`,
`vi_sao_chua_ap_duoc`, `verify`) + đủ subkey của `da_va`/`con_do_2_ca`/`patch_de_xuat`.
Đã đánh dấu sidecar `bus/_rejected_resolved.jsonl` (index 7).

Đây là ca thứ **7/7** liên tiếp mà bản ghi cách ly tự lành bằng retry của chính agent
(≤47s). Cơ chế "ỨNG VIÊN RETRY" thêm ngày 08-24 (commit `9ce6a60c`) đã chỉ đúng event ngay
trong dispatch — đúng như thiết kế.

## Lỗi THẬT: thông điệp guard khẳng định một nguyên nhân nó không hề kiểm tra

Payload **không hề cụt**: đủ 3005 ký tự, kết thúc đúng bằng `FAIL."}`. Lỗi thật là JSON viết
tay **thừa một dấu `}`** ngay sau khối `da_va` — root object đóng sớm, phần còn lại thành rác:

```
Extra data: line 1 column 1668 (char 1667)
... khong co adj STRIPPED). ... co cap don bay that."}},"con_do_2_ca":{...
                                                   ^ dấu } thừa
```

`json.loads` biết chính xác vị trí và loại lỗi, nhưng guard **vứt thông tin đó đi**
(`2>/dev/null`) rồi thay bằng một phỏng đoán cố định. Vì §5b của `ops_health_check.sh` chép
nguyên văn chuỗi đó vào prompt dispatch, mọi lượt autofix của lớp lỗi này đều bắt đầu bằng
giả thuyết sai — hệt lỗi đã sửa cho check 5b ngày **2026-08-21** (quy chụp mọi ca là
word-split) và cho check#9 ngày **2026-08-25** (hardcode "nghi quoting bug 08-01"). Đây là
lần thứ **ba** cùng một hình thái: *checker/guard hardcode chẩn đoán thay vì đọc bằng chứng nó
đang cầm trong tay.*

## Fix — commit `55b3f34c`

`bin/append_event.sh`, khối guard JSON: bắt stderr của `json.loads` và in ra **lỗi parser thật**
+ độ dài payload + cách đọc lỗi (`Extra data` = thừa ngoặc, payload KHÔNG cụt ·
`Unterminated string`/`Expecting` ở gần cuối = cụt thật). Guard vẫn fail-closed và vẫn cách ly
nguyên văn — không nới lỏng gì.

**Verify:**
- `bin/append_event_selfcheck.py` +1 ca `case_json_error_message_names_real_cause` (6 assertion,
  cả hai chiều thừa-ngoặc và cụt-thật) — toàn bộ PASS ×3 TZ (UTC, America/New_York, `env -u TZ`).
- `bin/ops_health_check_rejected_selfcheck.py` PASS.
- Replay **chính payload thật** của Taylor trong sandbox: ra đúng
  `Lỗi parser: Extra data: line 1 column 1668 (char 1667)` + `Độ dài payload: 3005 ký tự`.
- Checker thật (`OPS_HEALTH_DRY_RUN=1 --account SpaceX`): dòng hàng đợi cách ly chuyển
  ✅ *"24h qua không có ca CHƯA XỬ LÝ"*.

## Bài học

Guard đã có bằng chứng chính xác trong tay (exception của parser) mà chọn in phỏng đoán. Bất kỳ
thông điệp lỗi nào bị một checker chép vào prompt dispatch đều là **đầu vào chẩn đoán của người
kế tiếp**, không phải văn trang trí — nói sai ở đó tốn nguyên một lượt autofix.
