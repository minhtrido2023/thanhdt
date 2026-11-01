# Work-Tree Dashboard — Pha 1 phần B (server + UI) — 2026-11-01
Spec: `work-tree-dashboard-spec-20261101.md`. Nhánh `session/1566395318575169687`.

- `bin/work_tree_server.py` — stdlib `ThreadingHTTPServer`, cổng `WT_PORT` (8610), bind 0.0.0.0. Token ở `secrets/work_tree_token` (0600, tự sinh; đã thêm `secrets/` vào `.gitignore`). `/?k=` → cookie HttpOnly. POST cần cookie + `X-WT: 1`, 30/phút/IP, body ≤64KB. `/file?p=` chỉ đọc: `.md/.json/.csv/.html`, trong ROOT hoặc `WorkingClaude/`, chặn `..`, đường dẫn tuyệt đối, `secrets/`, file ẩn; trả `text/plain` (không render HTML).
- Ghi qua `work_ledger` (import): `add_note / set_priority / set_status / new_user_item`; nếu import lỗi → adapter ghi ledger trực tiếp. Sau mỗi POST gọi `work_tree_build.build_and_write|build_merged|build` nếu có, không thì `_fallback_rebuild` gấp ledger lên merged.json cũ. **Mike khi merge: chốt tên hàm build thật của Phần A** (hiện chưa có `work_tree_build.py` trong cây).
- `webui_work_tree/` — SPA vanilla (DOM `textContent`, không innerHTML), 5 khối "Cần anh quan tâm" mở sẵn, cây `<details>` nhớ trạng thái ở localStorage, panel chi tiết, tìm kiếm, chip lọc, tab NO-GO, form đề xuất.
- `systemd/mike-work-tree.service` — unit user, KHÔNG enable/cài.
- `bin/work_tree_server_selfcheck.py` — 33 check (401/200, cookie, POST note/priority/status/new, validate, 413, 9 kiểu path traversal, secret-grep, rate-limit 429); state cô lập trong tmp. PASS dưới `env -u TZ` và `TZ=America/New_York`.
- Fixture: `tests/fixtures/work_tree_merged.json` (không nằm trong `state/`).
- Chưa làm (ngoài phạm vi B): cài service, `base_url` config (phần D), `/api/ack`.
