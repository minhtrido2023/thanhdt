# 2026-09-25 — Gợi ý chẩn đoán JSON của `append_event.sh` quy CHỤP "cụt thật", ca thật chỉ thiếu 1 dấu `}`

**Phát hiện:** `ops_health_check.sh --account ZaloPay` (01:20Z) báo 2 bản ghi cách ly trong 24h
(Taylor + Mike). Dispatch tới Winston qua `ops_autofix` (job `Winston_20260925_012008`).

## Sự thật: KHÔNG mất event nào (3/3 tự lành ≤43s)

| index | ts bị chặn | agent | nguyên nhân THẬT | retry |
|---|---|---|---|---|
| 14 | 2026-09-12T02:34:25Z | Taylor | (tồn đọng, chưa đối chiếu từ 09-23) | `17d8fe14` +22s |
| 17 | 2026-09-24T06:13:45Z | Taylor | JSON viết tay **THIẾU 1 dấu `}`** (mở 2 / đóng 1) | `1259f10a` +43s |
| 18 | 2026-09-24T14:37:15Z | Mike | word-split THẬT (argc=11, payload bọc nháy ĐƠN có `'` bên trong) | `7522187f` +18s |

Cả 3 đã đối chiếu nội dung khớp (index 17: cùng trace `Taylor_20260924_055050`, cùng PhanA/B/C,
commit `8fd73366`+`166b4364`; index 18: cùng số liệu FPT ratio 0.9091 chỉ áp 09-15→09-18 + đối
chứng MBB 08-11) và đã đánh dấu sidecar. Ca **18/18** liên tiếp tự lành ≤60s.

## Lỗi THẬT: dòng gợi ý inline vẫn ĐOÁN nguyên nhân — lần 2 trên cùng guard

Guard JSON của `append_event.sh` in kèm câu:

> `'Extra data'` = THỪA dấu đóng }/] … `'Unterminated string'`/`'Expecting'` ở gần cuối = **cụt
> thật (word-split hoặc bị cắt)**.

Index 17 phản chứng trực tiếp: parser báo `Expecting ',' delimiter … (char 2452)` = đúng ký tự
cuối, nhưng payload **đủ 2452 ký tự**, `argc=5` (không hề word-split), kết thúc đúng `"}` — lỗi
thật là **thiếu một dấu `}`** của object lồng. Gợi ý cũ đẩy người xử lý đi tìm word-split không
tồn tại; checker §5b chép nguyên văn nó vào dispatch, nên dòng đầu dispatch đã sai hướng.

Đây là lần **thứ 2** cùng hình thái trên chính guard này (lần 1: 2026-08-28, commit `55b3f34c`,
ca `Extra data` bị gọi là "cắt cụt") và là lần thứ N của lớp `coding_guidelines` §29 —
"chẩn đoán phải trích bằng chứng đang cầm trong tay".

## Fix: ĐO thay vì đoán — `bin/json_payload_diag.py`

Đếm dấu cấu trúc `{[` / `]}` **ngoài chuỗi** (bỏ escape) + kiểm tra chuỗi cuối có đóng hay không.
Bốn nhánh, mỗi nhánh là một bit cơ khí đọc được từ chính payload:
- chuỗi còn mở ở cuối ⇒ **CẮT giữa chuỗi** (word-split / truncate);
- mở > đóng ⇒ **THIẾU n dấu đóng** (lệch ngoặc, không cụt) — in luôn ký tự cuối làm bằng chứng;
- đóng > mở ⇒ **THỪA n dấu đóng**;
- cân bằng + mọi chuỗi đóng ⇒ lỗi cú pháp bên trong (thiếu phẩy/hai chấm, nháy đơn).

Die-message của `append_event.sh` nay chỉ in: lỗi parser thật + chẩn đoán đo được + độ dài/đuôi.
Không còn câu suy diễn nào.

**Verify (5 ca, đo thật):** index 8 (`Extra data`, ca 08-28) → "THỪA 1" ✓ · index 17 → "THIẾU 1,
ký tự cuối `}`" ✓ · index 19 (word-split Mike) → "CHUỖI CHƯA ĐÓNG ⇒ CẮT" ✓ · synthetic
`{"a":"hello wor` → CẮT ✓ · `{'a':1}` → "cân bằng, lỗi cú pháp bên trong" ✓ · JSON hợp lệ → rc=0 ✓.
E2E qua `append_event.sh` thật: nhánh reject in đúng dòng mới, nhánh happy path (heartbeat) vẫn ghi
được lên bus.
