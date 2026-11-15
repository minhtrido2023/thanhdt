# AI-momentum M2 — second_opinion.sh chế độ raw + chẩn đoán deepseek (Wags, 2026-11-15)
Job `Wags_20261115_154609` · nhánh `wags/m2-wrapper-20261115` (worktree `/tmp/wt-m2wrap`) · CHƯA merge main.

## 1. Chẩn đoán — M2 FAIL 3/3 KHÔNG phải lỗi provider tạm thời
**Nguyên nhân gốc: model đã bị gỡ khỏi Zen.** `opencode/deepseek-v4-flash-free` (default_model trong
`kb/cli_providers.json`) không còn trong catalogue (`opencode models opencode` chỉ còn
`deepseek-v4.1-flash-free`). Gọi model cũ → `UnknownError: Unexpected server error` sau ~2s.
Bằng chứng (đo thật, opencode 1.18.25):
- `deepseek-v4-flash-free`, `ling-3.0-flash-free`, `nemotron-3-ultra-free` (cả 3 trong danh sách config): đều fail `UnknownError` 2s, lặp lại 5 lần — **xác định, không phải flake**; log `~/.local/share/opencode/log` không có chi tiết lỗi (chỉ log khởi tạo).
- `opencode/deepseek-v4.1-flash-free`: **chạy được** (prompt 1 dòng 2–11s; 20KB 12s).
- `opencode-go/deepseek-v4.1-flash`: API key hết hạn; `cliproxyapi/deepseek-v4-flash`: thiếu header x-opencode-session — không dùng được.
- Retry/backoff không có ích với nguyên nhân này; chỉ đổi model mới sửa được.
Sửa: `kb/cli_providers.json` đổi `deepseek-v4-flash-free`→`deepseek-v4.1-flash-free` (default_model + danh sách).
⚠️ Các model khác trong danh sách config (ling/nemotron/mimo-v2.5/laguna/north-mini) có thể cũng đã bị gỡ — chưa kiểm từng cái; `opencode models opencode` là nguồn đúng. Selfcheck cũ (`cli_provider_selfcheck.sh`, `dispatch_token_telemetry_selfcheck.py`) còn tên cũ nhưng chỉ làm đối số mock.

## 2. Chế độ raw
```
bin/second_opinion.sh --raw-prompt-file P --out R.jsonl [--text-out T] [--model M] [--timeout S=180] [--retries N=2] [--no-bus]
```
Prompt nguyên văn từ file; KHÔNG khung 3-điểm; KHÔNG bus/job record/dispatch.sh; chạy trong thư mục
rỗng tạm (không nạp CLAUDE.md/KB ⇒ mù thật); `OPENCODE_PERMISSION` deny bash/edit/write/webfetch/
websearch/external_directory. `--out` = luồng sự kiện JSON thô; `--text-out` = text trích. Retry backoff 5s/15s/45s.
Exit: **0** có text · **2** sai tham số · **10** lỗi provider sau hết retry · **11** chạy xong text rỗng · **12** timeout. Fail-open là việc của caller.
Chế độ cũ (positional SUBJECT) giữ nguyên byte-logic — selfcheck chứng minh.

## 3. Hai bẫy đo được (caller PHẢI biết)
1. **Prompt có chữ "ghi kết quả…schema_M2.json" ⇒ model gọi tool `glob` rồi TREO** (không output, đến hết timeout; 2 lần liên tiếp rc=12 với `blind_input.md` gốc, 240–420s). Thêm 1 dòng "KHÔNG gọi tool nào, trả lời trực tiếp bằng JSON" ⇒ chạy xong **142s, rc=0**, 7,5KB. Wrapper không tự chèn dòng này (giữ prompt nguyên văn) ⇒ **Taylor thêm dòng đó vào prompt M2**.
2. **Đừng deny read/glob/grep/list (hay `"*":"deny"`) trong OPENCODE_PERMISSION** — opencode TREO khi mọi tool bị deny (đo: 40–100s không phản hồi, kể cả prompt "OK?"). Bộ deny hiện tại (ghi/chạy/web) đã đủ an toàn.
Giữ timeout ≥ 200s cho gói 10 sự kiện (đo 142s).

## 4. Chạy thật
Prompt = `agents/Taylor/research/ai_momentum_20261115/m2/blind_input.md` (+1 dòng no-tool, bản sao ở /tmp, không sửa file Taylor), model default `deepseek-v4.1-flash-free`: **rc=0, 142s, text 7.582 byte, JSON parse được, 10 phần tử `diem_dang_ngo`** (blind_driver + view_20s/60s + evidence). Chất lượng nội dung chưa chấm (việc của Taylor/PREREG).

## 5. Selfcheck — `bin/second_opinion_selfcheck.sh`
Stub opencode/dispatch/append_event trong ROOT giả; không chạm mạng/bus thật. PASS dưới TZ=UTC, Asia/Ho_Chi_Minh, America/New_York (18 check). Mutation đã chứng minh test bắt được:
raw mode lỡ post bus ⇒ FAIL ("raw goi bus", "raw loi goi bus"); bỏ `exec dispatch.sh` ở chế độ cũ ⇒ FAIL ("che do cu bi pha").
Phủ: raw không bus, prompt nguyên văn, không khung 3-điểm, model default từ config, permission, exit 0/2/10/11/12, retry hồi phục, chế độ cũ còn dispatch+khung+lệnh bus.
