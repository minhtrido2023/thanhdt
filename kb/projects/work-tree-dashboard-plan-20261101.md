# Kế hoạch: Dashboard cây quản lý công việc toàn fleet (Fable lập, 2026-11-01)

Trạng thái: **KẾ HOẠCH — chờ user duyệt 5 câu hỏi cuối file**. Chưa code.

## 1. Chẩn đoán
Không có sổ cái trung tâm; trạng thái việc rải ≥7 nơi, mỗi nơi một schema:
- `kb/projects/INDEX.md` (verdict nằm trong **bold** văn xuôi); chỉ 4/99 file `kb/projects/*.md` có frontmatter.
- `kb/projects/rnd-pipeline-tracker.md` (mốc ngày chôn trong câu).
- `kb/paper_programs_registry.json` (15 chương trình; `status`/`review_date` chỉ có ở một số mục).
- `kb/dashboard_watchlist.json` (seed tay 10-15), `kb/structural_break_watch.json`, `kb/memory/*.md` (xoá khi xong ⇒ mất lịch sử), `kb/current_ops.md` (tay).
- Bus: 3.579 event (envelope nhất quán, payload tự do), 1.432 job — nhật ký, không gắn "dự án".
- `bin/daily_dashboard.py` (08:00 ICT, topic `dd.mm`) chỉ là bản tin phẳng, không cây, không link.
Thiếu **khoá chung (id)** nối project ↔ bus question ↔ paper program ↔ job ↔ mốc.

## 2. Mô hình dữ liệu (lai)
- `kb/work_ledger.jsonl` (git, append-only, upsert theo `id`): chỉ phần người/agent chốt (nhánh, trạng thái, verdict, mốc, chờ user).
- Lớp **derived** merge lúc build (không ghi ngược): paper registry, watchlist, structural watch, bus question/verification/decision, jobs 30 ngày.
- Schema: `id` (proj:/paper:/busq:/sbw:/wl:/user:), `branch`, `title`, `type` (research|ops|portfolio|infra|watch), `status` (idea|active|waiting|GO|NO-GO|live|closed), `owner`, `opened/updated/due`, `verdict`, `links[]`, `depends_on[]`, `waiting_on{who,what,since}`, `needs_user`, `source` (curated|derived), `aliases[]`, `confidence`.
- Ghi qua CLI `bin/work_ledger.py upsert|close|note|merge` (không sửa JSONL tay). Builder `bin/work_tree_build.py` → `reports/work_tree.html`.

## 3. Cây
- **Research**: Tín hiệu & chiến lược (ta-schools NO-GO, bal_maxpos NO-GO, margin-spread NO-GO, V2.5 DISABLED, LAG ADV mốc 12-15, DT5G/EXTREME) · Thực thi (order_book shadow, opening-window, fill_timing, expvol_pacing) · Dữ liệu & PIT (universe-pit, cash-div, adjfactor, oshares-live) · Paper programs (15) · DD cổ phiếu (HHS, TV2, SCL, FPT, SIP…).
- **Operation**: Báo cáo & cadence · Cron/hạ tầng/KB/selfcheck · Corp-action · Sự cố/retro (219 incident).
- **Portfolio Management**: Tài khoản live (SpaceX, ZaloPay, exclusions) · Rủi ro & gate (nav-loss-brake, EXTREME gate, margin discretionary, CAPIT) · Sleeve discretionary · Hiệu suất (results_registry).
- **Watch/Macro**: structural_break_watch, Bobby quý, Livermore.
- View xuyên nhánh: **Cần bạn quyết · Treo quá hạn · Mới 7 ngày · NO-GO đừng đề xuất lại**.

## 4. Cập nhật hằng ngày (cơ học)
1. Cron 07:50 ICT build (trước `daily_decision_topic.py` 08:00); thêm `kb/cron_registry.md` cùng commit.
2. Derived tự động từ 5 nguồn; bus question chưa đóng; verification/decision gắn item theo topic/alias.
3. Cổng: pre-commit (file `kb/projects/*.md` đổi ⇒ phải có dòng ledger `status`+`updated`), `work_ledger_selfcheck.py` vào `run_selfchecks.sh`, badge STALE (>30 ngày research / >14 ngày ops / due đã qua), audit tuần.
4. Backfill 1 lần: parser xác định cho INDEX.md + paper + watchlist + bus question; 99 file còn lại: Haiku/Sonnet đọc 20 dòng đầu → `.proposed` có `confidence`; Mike duyệt, user chỉ xem `confidence=low` (~20–30).
5. Trùng lặp: id canonical + aliases, cảnh báo cặp giống ≥0,85.

## 5. Giao diện
MVP = **HTML tĩnh tự chứa** (vanilla JS, không build), đính kèm email EOD + tóm tắt 3 số trong topic Discord 08:00. Trái: cây `<details>` + ô tìm kiếm + nhớ trạng thái mở/đóng; phải: panel chi tiết (verdict, owner, mốc, chờ ai, link, hoạt động gần đây); đầu trang 3 ô cảnh báo; chip lọc trạng thái/owner/nhánh/type; badge màu. Không số tiền/vị thế/số tài khoản. Nâng cấp pha 3 → web app cục bộ nếu cần nút bấm. (Notion/GDocs/Claude Docs: yếu cho cây 150+ lá, drift ngoài git.)

## 6. Tương tác hai chiều
Gõ trong Discord: `!wt note <id> …`, `!wt prio <id> 1`, `!wt close <id> NO-GO …`, `!wt new <nhánh> "<tiêu đề>"` → Mike chạy `work_ledger.py` + bus `decision decided_by:user` + commit. Pha 2: HTML có nút "copy lệnh".

## 7. Lộ trình & nghiệm thu
- **Pha 1 (1 phiên, Sonnet medium, ~150–250k token)**: schema + CLI + builder + HTML + selfcheck + cron + email/Discord. Nghiệm thu: ≥99 proj + 15 paper + mọi bus question pending có mặt; selfcheck PASS; build <10s; tìm "NO-GO" ra ≥5 mục; 0 số tài khoản/NAV trong file.
- **Pha 2 (2–3 phiên)**: backfill 99 file, pre-commit gate, lệnh `!wt`, dedup, link incidents. Nghiệm thu: 100% proj có branch+status; arch-reviewer spot-check 15 mục ≥14 đúng; 7 ngày không stale giả.
- **Pha 3**: timeline từ git diff ledger, workload theo agent, host nội bộ/app.
- Rủi ro: backfill đọc sai verdict (confidence + review); drift (pre-commit + stale badge); nhạy cảm (selfcheck grep chặn `0002023347|0001743768|availableCash`).
- Phân việc: Mike chủ sổ cái; Sonnet coder dựng; Haiku/Sonnet backfill; Wags cron/selfcheck/pre-commit; Taylor xác nhận mapping 15 paper; arch-reviewer 1 vòng (Opus high) cho schema + gate + `!wt`.

## 8. Câu hỏi cần user quyết
1. Kênh chính: email EOD đính kèm + Discord 08:00, hay cần host nội bộ mở port?
2. 4 nhánh gốc + view "Cần bạn quyết" đủ chưa; có tách "Hạ tầng fleet" riêng?
3. Chỉ tiêu đề/verdict/link (khuyến nghị) hay kèm số pp/CAGR?
4. Chấp nhận lệnh `!wt` qua Discord (không nút) ở MVP?
5. Chấp nhận Haiku gán nhánh/trạng thái 99 dự án cũ, user chỉ duyệt `confidence=low`?

## Chưa kiểm chứng
Nội dung đầy đủ 99 file projects; ccdb có serve static HTML không; mức khớp `prompt_summary` job với tên dự án; chi phí token backfill thực tế.
