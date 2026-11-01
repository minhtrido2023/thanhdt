# SPEC — Work-Tree Dashboard (webapp tương tác) — user duyệt hướng 2026-11-01 17:35 ICT

Kế hoạch gốc (Fable): `kb/projects/work-tree-dashboard-plan-20261101.md`. File này = hợp đồng cho người dựng.
Mọi code nằm trong worktree `/home/trido/thanhdt/wt-1566395318575169687` (= gốc repo mike, có `kb/`, `bin/`), nhánh
`session/1566395318575169687`. KHÔNG sửa cây `/home/trido/thanhdt/WorkingClaude/mike` trực tiếp. Mike merge sau.

## Quyết định của user (đã chốt, không hỏi lại)
1. **Webapp tương tác**, MỘT đường link/ngày, gắn vào topic ngày của Discord (cron 08:00 `bin/daily_decision_topic.py`).
   Discord CHỈ là kênh đưa link. Mọi tương tác (ghi chú, đổi ưu tiên, đóng/mở hướng, thêm ý tưởng) làm TRONG webapp.
2. Mục mở đầu = **"Cần anh quan tâm"**.
3. Có **tóm tắt 1-2 dòng** mỗi mục + bấm vào ra **trang/panel chi tiết giải thích** (vì sao, kết luận, bước kế, link tài liệu, lịch sử).
4. Đơn giản nhất có thể. Không `!wt`, không nút phức tạp.
5. Mike (quản lý) tự quyết cây và model; Haiku được dùng backfill.

## Cây (Mike chốt)
Gốc: **Research** · **Operation** (gồm hạ tầng fleet, báo cáo, corp-action, sự cố) · **Portfolio** · **Watch/Macro**.
Tầng 2 ví dụ: Research/{Tín hiệu & chiến lược, Thực thi, Dữ liệu & PIT, Paper programs, DD cổ phiếu};
Operation/{Báo cáo & cadence, Cron-hạ tầng-KB, Corp-action, Sự cố & retro}; Portfolio/{Tài khoản live, Rủi ro & gate, Sleeve discretionary, Hiệu suất};
Watch/{Vĩ mô & cấu trúc, Mốc định kỳ}. Branch là chuỗi `"Research/DD cổ phiếu"`.
Đầu trang (không phải nhánh) = 5 khối "Cần anh quan tâm": (1) Chờ anh quyết (`needs_user`) (2) Quá hạn / treo (3) Mới & vừa đổi 7 ngày
(4) Ý tưởng cần nghiên cứu thêm (`status=idea`) (5) Anh đã gửi — chờ team xử lý (`source=user`, chưa `ack`). Thêm tab "Thư viện NO-GO" (đừng đề xuất lại).

## Schema 1 item (ledger + merged)
```
id            "proj:<stem file kb/projects>" | "paper:<id>" | "busq:<agent>/<topic>" | "sbw:<id>" | "wl:<slug>" | "user:<slug>"
branch, title, summary(≤160 ký tự, 1-2 dòng cho người không đọc code), detail(markdown ngắn: vì sao/kết luận/bước kế)
type          research|ops|portfolio|watch
status        idea|active|waiting|GO|NO-GO|live|closed
priority      1|2|3 (mặc định 3)
owner, opened, updated, due (ISO date|null)
verdict       null | {label, text}          # NO-GO|GO|INCONCLUSIVE|IMPLEMENTED|KHÔNG WIRE
waiting_on    null | {who, what, since}     # who ∈ user|<agent>|data|date
needs_user    bool
links[]       [{label, path}]               # path tương đối ROOT mike hoặc WorkingClaude; builder kiểm tồn tại → `missing`
depends_on[], aliases[]
notes[]       [{ts, by(user|agent|mike), text}]     # ghi chú tích luỹ, KHÔNG xoá
source        "curated" | "derived:<nguồn>" | "user"
ack           bool (chỉ cho source=user: Mike đã nhận chưa)
confidence    high|med|low                  # chỉ bản backfill
stale         bool (builder tính)
```
Ledger `kb/work_ledger.jsonl`: append-only, mỗi dòng 1 bản ghi đầy đủ-hoặc-một-phần của 1 `id`; bản sau trường nào thắng trường đó
(upsert theo id, `notes` nối thêm). Ghi qua CLI `bin/work_ledger.py` (flock + append atomic), KHÔNG sửa tay.

## Thành phần & chủ
| # | File | Việc |
|---|---|---|
| A | `bin/work_ledger.py`, `bin/work_tree_build.py`, `bin/work_ledger_selfcheck.py`, cron 07:50 | CLI upsert/note/close/inbox/ack/merge; builder gộp ledger + derived (paper registry, dashboard_watchlist, structural_break_watch, bus question chưa đóng qua `bin/bus_question_audit.py --json`, INDEX.md parser, jobs 30 ngày) → `state/work_tree/merged.json`; tính `stale` (research>30d, ops>14d, due đã qua), dedup cảnh báo; selfcheck fixture-based, `env -u TZ`, secret-grep |
| B | `bin/work_tree_server.py`, `webui_work_tree/index.html` (+ `app.js`, `style.css`), `systemd/mike-work-tree.service` | Server stdlib `ThreadingHTTPServer`, 0 dependency (không có flask), cổng 8610 bind 0.0.0.0, token cookie; SPA vanilla JS |
| C | `kb/work_ledger_backfill.proposed.jsonl` (Haiku, theo lô 25 file) | 99 file `kb/projects/*.md` → item có `confidence`; Mike duyệt rồi nạp |
| D | sửa `bin/daily_decision_topic.py` | thêm 2 dòng: link webapp + 4 con số (chờ quyết / quá hạn / mới / chờ xử lý); link lấy từ `kb/work_tree_config.json` (`base_url`) |

## Hợp đồng API (B ↔ A)
- Đọc: `GET /api/tree` → nội dung `state/work_tree/merged.json` = `{generated_at, counts, attention:{need_user[],overdue[],recent[],ideas[],inbox[]}, items[], branches[]}`; `GET /api/item?id=` → item + `history[]` (từ git log ledger/bus/jobs, tối đa 30).
- Ghi (POST JSON, cần token, trả item mới): `/api/note {id,text}`, `/api/priority {id,priority}`, `/api/status {id,status,verdict?}`, `/api/new {branch,title,summary}` (tạo `user:<slug>` status=idea source=user ack=false). Mỗi POST gọi hàm trong `work_ledger.py` (import, không subprocess) rồi build lại merged.json.
- Auth: token ngẫu nhiên ở `secrets/work_tree_token` (0600, sinh nếu thiếu); `GET /?k=<token>` đặt cookie HttpOnly rồi redirect; thiếu/sai → 401. Mọi POST kiểm cookie + header `X-WT: 1`. Rate-limit thô 30 POST/phút.
- Link người dùng nhận: `{base_url}/?k=<token>`. `base_url` mặc định `http://192.168.100.7:8610` (LAN) — đổi trong `kb/work_tree_config.json` nếu có tunnel/VPN.

## UI (một trang, tiếng Việt, đọc tốt trên điện thoại)
Đầu trang: tiêu đề + "cập nhật HH:MM" + ô tìm kiếm + chip lọc (nhánh/trạng thái/owner/ưu tiên). Kế tiếp 5 khối "Cần anh quan tâm" (mở sẵn,
mỗi mục: badge trạng thái, tiêu đề, summary, owner, mốc, nút nhỏ Ghi chú / Ưu tiên / Đóng-NO-GO). Dưới: cây `<details>` theo nhánh,
nhớ mở/đóng trong localStorage, lá hiện badge + summary. Bấm tiêu đề → panel chi tiết (detail, verdict, waiting_on, links bấm được qua
`/file?p=` chỉ đọc, giới hạn trong ROOT, chỉ .md/.json/.csv/.html, chặn `secrets/`), ghi chú, lịch sử. Màu: NO-GO đỏ, GO/live xanh,
waiting vàng, idea tím, closed xám, stale viền cam. Form "＋ Đề xuất hướng nghiên cứu mới" cố định góc.
**Không hiện số tiền, vị thế, số tài khoản, NAV, CAGR.** (tóm tắt chữ chỉ nêu kết luận; user chọn "một ít thông tin tóm tắt").

## Nghiệm thu Pha 1
- merged.json chứa ≥99 `proj:*` (qua backfill đã nạp) + 15 `paper:*` + mọi bus question pending; build <10s; selfcheck PASS dưới `env -u TZ` và `TZ=America/New_York`.
- Server chạy thử cổng 8611 từ worktree: 401 khi không token; GET /api/tree 200; POST note → xuất hiện trong ledger + merged.json + panel; `/file?p=../secrets/x` bị chặn.
- grep merged.json + html không thấy `0002023347|0001743768|availableCash|NAV` (selfcheck).
- cron 07:50 thêm vào `kb/cron_registry.md` (luật §11) NHƯNG chưa cài crontab thật — Mike cài sau review.
- Không thêm văn xuôi vào CLAUDE.md/context_pack/MIKE.md.
