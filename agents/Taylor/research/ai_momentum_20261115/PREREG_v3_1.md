# PREREG v3.1 — phụ lục M2 (viết TRƯỚC mọi lần chạy forward)
Chỉ thêm/đổi cách gọi M2; **không đổi** ngưỡng, schema, T1/T2/T3, M1. Khoá md5 của PREREG_v3.md / prereg_v3.json / events_v3.csv giữ nguyên (không cần cập nhật).
- M2 = `bin/second_opinion.sh --raw-prompt-file` (Wags, nhánh `wags/m2-wrapper-20261115`), model mặc định của wrapper (`deepseek-v4.1-flash-free`; model cũ `deepseek-v4-flash-free` đã bị Zen gỡ → M2 FAIL 3/3 ở P1 trước là do đó).
- Prompt M2 = nội dung `prompt_M2_blind.md` / `prompt_M2_challenge.md` (không đổi) **+ đúng 1 dòng** do adapter chèn: `KHONG goi tool nao, tra loi truc tiep bang JSON ...`. Lý do (Wags đo): thiếu dòng này model gọi tool `glob` rồi TREO đến hết timeout.
- 1 sự kiện/lần gọi; blind chạy TRƯỚC và không nhận JSON M1; challenge nhận gói + JSON M1. Timeout 240s.
- Mọi lỗi (exit 10/11/12/2, timeout, parse, schema, event_id lệch) ⇒ `m2_status=FAIL`, fail-open: T1/T2 vẫn chấm, loại khỏi T3. Raw text M2 lưu trong ledger (`m2_raw`).
- **Khung định dạng (thêm sau retro lần 1, 16/11)**: adapter chèn thêm 1 khung JSON chính xác theo `schema_M2.json` (tên trường + enum). Lý do đo thật: không có khung, deepseek tự bịa (`claim` thay `item`, `m1`/`field` thay `m1_field`, nhãn `FUNDAMENTAL` ngoài enum) ⇒ FAIL schema 2/2. Có khung: 2/2 OK. Không đổi nội dung câu hỏi/giả thuyết của prompt.
- `schema_M2.json` không đổi; `validate()` bổ sung kiểu `boolean` (trước đó ném KeyError với `verifiable`).
