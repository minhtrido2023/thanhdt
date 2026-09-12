# 2026-09-12 — `report_return_gate.py` tính gốc cây bằng ĐẾM CẤP: chạy từ worktree là chặn báo cáo nhà đầu tư

**Status**: fixed (commit `dd2c0d28` + vòng 2 sau arch-review)
**Phát hiện bởi**: bus question `Mike/report-return-gate-worktree-root-chan-bao-cao-nha-dau-tu`; user duyệt fix 2026-09-12 12:18 ICT
**Ảnh hưởng**: client-facing. Cổng tỉ suất §21 fail-closed ⇒ **báo cáo nhà đầu tư không gửi được** —
5 ca thật: 2026-07-03, 07-24, 07-31, 08-07 + 1 lần Errno 2. Không sai số tiền, chỉ không giao hàng.

## Root cause

`ROOT = os.path.dirname×3(__file__)` đúng cho BẢN GỐC `mike/bin/` (→ `WorkingClaude`), nhưng mọi
bản sao chạy từ worktree `mike/agents/wt-*/bin/` cho `ROOT = WorkingClaude/mike/agents` ⇒
`EXEC_DIR = mike/agents/data/execution_logs` **không tồn tại** ⇒
`FileNotFoundError: thiếu .../dnse_raw_<date>.jsonl — CHẶN (fail-closed)`. 3/3 worktree kiểm tra
đều lệch. Phép đếm cấp mã hoá một giả định — "script luôn nằm ở đúng độ sâu đó" — mà chính cơ chế
worktree của fleet phá vỡ mỗi ngày.

## Fix

`bin/wc_paths.py` · `find_wc_root()`: env `WC_ROOT` (đã KIỂM CHỨNG) > đi lên từ `__file__` tới thư
mục chứa **`wc_env.sh`** > fallback đếm cấp (cây bị cắt rời). Wire vào 5 file trên đường báo cáo §6:
`report_return_gate.py`, `verify_account_snapshot.py`, `daily_nav_snapshot.py`,
`send_report_email.py`, `reconcile_equity.py`.

**Bẫy quan trọng nhất, do arch-reviewer bắt được (vòng 1 = NEEDS_CHANGES):** `bin/dispatch.sh` tự
tính `WC_ROOT="$(cd "$ROOT/.." && pwd)"` — ĐÚNG phép đếm cấp vừa bị kết luận là sai — rồi
**export xuống mọi phiên agent con**. Bản sao dispatch.sh trong worktree export
`WC_ROOT=.../mike/agents`. Bản vá đời đầu tin env vô điều kiện ⇒ chạy dưới env đó là **tái hiện sự
cố 1:1, sau khi đã vá**. Đã vá cả hai đầu: `wc_paths` chỉ nhận env khi thư mục đó thật sự có
`wc_env.sh` (không thì cảnh báo stderr + tự tìm marker), `dispatch.sh` neo marker khi phép đếm cấp
trượt. Bài học chung: **một bản vá "tìm gốc cây" chưa xong chừng nào mọi nguồn sinh ra gốc cây —
kể cả biến môi trường của chính hệ điều phối — chưa được vá theo.**

## Verify

`bin/report_return_gate_selfcheck.py` — dựng worktree GIẢ THẬT `mike/agents/wt-fake-*/bin`
(mkdtemp, đúng độ sâu, copy file thật), chạy như production, có RED control lấy THẲNG TỪ GIT
(quét `rev-list` tìm blob còn dirname×3 — không hardcode `HEAD~`, để một commit chen vào không
biến RED control thành bản đã vá). Chạy dưới `env -u TZ` và bỏ `WC_ROOT` cho nhánh marker.

## Còn treo — KHÔNG sửa trong phạm vi này, nhưng phải biết

1. **17 bản sao worktree vẫn là code TIỀN-VÁ** (`agents/wt-*`, `WorkingClaude/wt-*`:
   `grep -c wc_paths` = 0). `report_delivery_gate.py:116` gọi `ROOT/bin/report_return_gate.py` với
   `ROOT` là cây đang chạy ⇒ delivery chạy TỪ worktree cũ vẫn dính bug. Worktree chỉ khỏi khi
   rebase/merge master. Không có checker nào phát hiện "worktree đang chạy bản tiền-vá".
2. **`state/report_delivery.json` phân mảnh theo worktree** — `report_delivery_gate.py:22-23` lấy
   `ROOT = parent.parent` (cây đang chạy), mà `state/` bị gitignore. Đã có thật:
   `WorkingClaude/wt-1540947310874198108/state/report_delivery.json` (2 entry, có
   `SpaceX_daily_report_2026-08-21.md`) và `mike/agents/wt-1522576692638388364/state/` — trong khi
   sổ canonical `mike/state/report_delivery.json` có 66 entry. `check_report_cadence.sh:44` chỉ đọc
   sổ canonical ⇒ **một lần giao hàng từ worktree là vô hình với cadence check ⇒ có thể gửi TRÙNG
   báo cáo cho nhà đầu tư**; `report_delivery.json.lock` cũng theo ROOT nên hai cây không loại trừ
   nhau. Trước bản vá, cổng tỉ suất fail-closed vô tình CHẶN đường này; vá xong thì đường đó thông
   ⇒ rủi ro trùng-gửi từ latent thành với tới được. Quyết định cố ý KHÔNG sửa `report_delivery_gate.py`
   trong commit này (§3 surgical, nó không thuộc lớp lỗi "đường dẫn không tồn tại"); cần một việc
   riêng: pin `DEFAULT_STATE` về cây canonical hoặc gộp sổ.
3. **Bề mặt quyền của sandbox codex nới rộng khi dispatch phát TỪ worktree** (arch-review vòng 2).
   `dispatch.sh:1063` dùng `--add-dir "$WC_ROOT"` làm writable root cho nhánh `codex`, và chú thích
   :1052-1060 nói rõ cấp cả cây thì `secrets/` + `data/trading_rules.json` ghi được. Trước bản vá,
   dispatch phát từ bản sao worktree có `WC_ROOT=.../mike/agents` ⇒ sandbox hẹp (và vốn đã hỏng:
   không ghi nổi bus); sau bản vá nó là cả cây `WorkingClaude` — tức KHÔI PHỤC đúng ngữ nghĩa user
   chốt 2026-08-10, không phải lỗ hổng mới. Nhưng câu "giữ nguyên hành vi từng byte" chỉ đúng cho
   đường canonical, nên ghi lại ở đây.
4. **Gợi ý rẻ chưa làm**: khi env `WC_ROOT` hợp lệ (có `wc_env.sh`) nhưng KHÁC gốc suy từ
   `__file__` — vd trỏ vào một cây `WorkingClaude` ANH EM có marker nhưng `data/` rỗng — hiện guard
   cho qua im lặng. Không tệ hơn hiện trạng (trước guard cũng nhận, và `dirname×3` từ trong cây anh
   em cũng ra đúng cây đó; các cây đó có 0 `dnse_raw_*` nên cổng vẫn fail-closed chứ không PASS
   trên số liệu rác). Rủi ro còn lại là GHI sai đích (vd `nav_history_*.csv`). Một dòng cảnh báo
   stderr là đủ — làm khi có việc đụng tới.
5. **~28 file `bin/*.py` khác cùng lớp lỗi** (đếm cấp ra gốc cây) — chỉ liệt kê, không sửa vì không
   nằm trên đường báo cáo: `compute_active_nav.py`, `compute_jit_unpark.py`, `compute_park_trim.py`,
   `corp_actions.py`, `corp_action_auto_confirm.py`, `park_holdings.py`, `merge_park_orders.py`,
   `marginability_check.py`, `approve_margin_day.py`, `discretionary_{margin_gate,candidate_funnel,
   accumulation_inject}.py`, `dc_candidate_feeder.py`, `filter_lag_entry_window.py`,
   `lag_entry_anchor.py`, `sector_valuation_lens.py`, `expvol_shadow_probe.py`,
   `capture_upcom_vwap_eod.py`, `code_quality_baseline_build.py`, `forensic_flag_review_check.py`
   (có env override nên đỡ hơn) + các selfcheck tương ứng. Chúng chỉ cắn khi chạy từ worktree;
   cách vá đã có sẵn (`from wc_paths import find_wc_root`), làm dần khi đụng tới.
