# Work-Tree Dashboard — Pha A (sổ cái + builder + selfcheck) — 2026-11-01

Spec: `work-tree-dashboard-spec-20261101.md`. Nhánh `session/1566395318575169687`. Chưa merge, chưa cài crontab.

## Đã có
- `bin/work_ledger.py` — CLI `upsert|note|close|status|inbox|ack|merge` (`--by`), `flock` + 1 lần `write` O_APPEND + fsync. Import cho server B:
  `upsert, add_note, set_priority, set_status, close_item, new_user_item, ack, merge_ids, inbox_items, fold, read_records`
  (đều nhận `path=` tuỳ chọn; mặc định `kb/work_ledger.jsonl`, env `WT_LEDGER`). Validate enum/id/ngày; summary tự cắt ≤160.
- `bin/work_tree_build.py` — `build(Cfg())`, `write_merged(Cfg())` → `state/work_tree/merged.json` (atomic, env `WT_OUT`). `state/` bị gitignore.
- `bin/work_ledger_selfcheck.py` — 51 check fixture + build thật vào file tạm + secret-grep; PASS dưới `env -u TZ` và `TZ=America/New_York`.
- `kb/cron_registry.md`: dòng 07:50 ICT (đề xuất, chưa cài). Dòng đề xuất: `50 0 * * *` UTC.

## Điểm B/D cần biết (hợp đồng)
- `attention.{need_user,overdue,recent,ideas,inbox}` là **danh sách ID** (`attention_format:"ids"`), tra trong `items`. Item có thêm `overdue`, `stale`, `recent_jobs[]`, `links[].missing`.
- Top-level thêm `warnings:{dups[],other[]}`, `build_seconds`. `branches[]` = khung 15 nhánh (kể cả rỗng) + nhánh lạ, mỗi dòng `{branch,root,sub,count,open_count}`.
- Bus: worktree không có `bus/` (gitignored) → builder dùng `bus/` của cây canonical (`WT_BUS_ROOT` ghi đè). Khi merge vào cây mike thì tự dùng `bus/` của chính nó.
- Ledger thắng derived theo từng trường; `merge` gộp alias (derived trùng alias bị loại). `add_note` cũng đặt `updated`=hôm nay (ghi chú = hoạt động).
- Mọi chuỗi qua `sanitize()`: số tài khoản `000\d{7}`, `availableCash`, `NAV`, `CAGR` bị che `[tk]`/`[ẩn]` (kể cả ghi chú user).
- Derived: paper summary dùng mẫu trung tính (không trích prose registry); `wl:` milestone/backlog; `sbw:`; `busq:` (needs_user trừ `selfcheck-red*`); `proj:` = parser INDEX.md (confidence med) + quét `kb/projects/*.md` chưa có trong INDEX (stub, confidence low, đợi backfill C). Jobs 30 ngày khớp theo stem/alias trong `prompt_summary`.

## Kết quả thật (cây hiện tại)
`140 item | chờ quyết 1 · quá hạn 17 · mới 30 · ý tưởng 4 · chờ xử lý 0 | jobs30d 598 | dup 3 | 0,92s`
proj 97 (34 INDEX + 63 stub; 3 mục INDEX trỏ file ngoài `kb/projects` nên chưa tính ⇒ ≥99 cần backfill/ledger) · paper 15 · busq 8 (= 8 pending của audit) · NO-GO 11.
grep `0002023347|0001743768|availableCash|NAV` trong merged.json = 0.

## Hạn chế
- `branch` của proj/stub là heuristic từ khoá (confidence low/med) — backfill C sẽ ghi đè qua ledger.
- 3 cặp dup cảnh báo là tiêu đề DD cùng mẫu (tch/hhs, dgc/scl) → khả năng dương tính giả, chỉ cảnh báo.
- Chưa có pre-commit gate / `run_selfchecks.sh` hook (Pha 2).
