# 2026-09-26 — guard JSON của `append_event.sh` TỪ CHỐI payload HỢP LỆ khi thiếu helper chẩn đoán

**status**: fixed
**severity**: medium (latent trong production hôm nay — 0 cây thật đang hỏng; hiện thực CHẮC CHẮN trong sandbox selfcheck)
**phát hiện bởi**: weekly-ops-audit 2026-09-26 (job `Mike_20260925_204425`), mục 8 — FAIL của `bin/append_event_selfcheck.py`

## Triệu chứng
`bin/append_event_selfcheck.py` FAIL 3 assertion + crash `IndexError` từ 2026-09-25, vào
`kb/selfcheck_baseline.json` dưới nhãn `auto: true`. Dòng lỗi thật:

```
Lỗi parser: python3: can't open file '/tmp/append_event_selfcheck_*/bin/json_payload_diag.py': [Errno 2] No such file or directory
```

## Nguyên nhân gốc
Commit 2026-09-25 tách phần chẩn đoán của guard JSON ra file mới `bin/json_payload_diag.py`
(đúng tinh thần §29). Nhưng nó gộp HAI việc vào MỘT lệnh:

```bash
_jerr="$(printf '%s' "$payload" | python3 "$ROOT/bin/json_payload_diag.py" 2>&1 >/dev/null)" \
  || die "payload ... KHÔNG phải JSON hợp lệ. Lỗi parser: $_jerr"
```

`python3` trả rc≠0 vì HAI lý do khác hẳn nhau — (a) JSON thật sự hỏng, (b) helper KHÔNG tồn tại
(rc=2, "can't open file"). Cả hai rơi vào cùng nhánh `die`. Hệ quả:

1. **Payload JSON HỢP LỆ bị TỪ CHỐI** khi cây thiếu helper.
2. Dòng `Lỗi parser:` in thông báo thiếu file **như thể đó là lỗi parser** — đúng lớp lỗi §29
   ("khẳng định nguyên nhân chưa hề đọc bằng chứng") mà chính guard này sinh ra để chống. Lần
   thứ **ba** cùng hình thái trên cùng một guard (08-28 `Extra data` bị gọi là "cắt cụt";
   09-25 mọi lỗi `Expecting` bị gọi là "cụt thật"; nay lỗi thiếu file bị gọi là "lỗi parser").

## Tái hiện (đo thật, không suy đoán)
```bash
T=$(mktemp -d); mkdir -p "$T/bin" "$T/kb"
cp mike/bin/append_event.sh mike/bin/mike_json.py "$T/bin/"; echo 1 > "$T/kb/version.txt"
"$T/bin/append_event.sh" Mike finding repro '{"a":1}' Mike_20260101_000000
# TRƯỚC khi vá: rc=1, "KHÔNG phải JSON hợp lệ" cho payload hoàn toàn hợp lệ
```

## Phạm vi thật (KHÔNG phóng đại)
Quét toàn bộ 86 bản `append_event.sh` trên đĩa: **0 cây đang hỏng**. Các worktree cũ mang bản
`append_event.sh` CŨ (chưa gọi helper) nên tự nhất quán; `bin/json_payload_diag.py` **đã được
git track** nên mọi `git worktree add` mới đều có nó. Ô rủi ro còn lại là các bản copy
KHÔNG-phải-git của `bin/` (sandbox test, restore từ tarball) — đúng chỗ selfcheck đang đứng.
28/42 call site bọc `2>/dev/null || true`, nên nếu ca này trúng cây sống thì event mất **im lặng**.

## Bản vá
1. `bin/append_event.sh` — phán quyết "hợp lệ hay không" nay do **parser inline không phụ thuộc
   file ngoài** quyết định; `json_payload_diag.py` CHỈ còn làm giàu thông điệp khi payload đã
   biết chắc là hỏng. Helper vắng ⇒ vẫn chặn đúng ca hỏng, và nói THẲNG "cây này không có
   helper ⇒ thiếu phần chẩn đoán ĐO ĐƯỢC; lỗi trên là của parser JSON".
2. `bin/append_event_selfcheck.py` — `mksandbox()` copy thêm `json_payload_diag.py` để sandbox
   đo ĐÚNG script production (bài học cùng lớp với bẫy đường dẫn selfcheck 2026-09-24).

## Verify bằng CHẠY THẬT
- sandbox thiếu helper + `{"a":1}` ⇒ `appended finding/repro-ok`, rc=0 (trước: rc=1).
- sandbox thiếu helper + `{"a":1` ⇒ rc=1, `Expecting ',' delimiter: line 1 column 7` + ghi chú
  helper vắng. Chặn đúng, chẩn đoán trung thực.
- `python3 bin/append_event_selfcheck.py` ⇒ **toàn bộ assertion PASS, rc=0**.

## Bài học
Một guard chỉ đáng tin khi **phán quyết** của nó không phụ thuộc vào thứ chỉ dùng để **giải
thích** phán quyết đó. Tách chẩn đoán ra file riêng là đúng; nhưng nếu file đó đồng thời là
nguồn của verdict thì sự vắng mặt của nó biến thành một verdict SAI — và sai theo hướng
fail-closed im lặng, tệ nhất cho đường ghi bus.
