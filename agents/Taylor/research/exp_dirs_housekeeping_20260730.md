# Housekeeping `agents/Taylor/exp_*` + `probe_*` — quyết định & thực thi

**Job**: `Taylor_20260730_125303` · **Ngày**: 2026-07-30
**Nguồn**: audit `agents/Wags/research/fleet_housekeeping_audit_20260730.md` §5 mục B (job `Wags_20260730_112912`)
**Commit**: `20b88ac5` (repo `mike`, branch `master`)

---

## 1. Kết quả một dòng

| | Trước | Sau | Δ |
|---|---|---|---|
| `.git` (repo `mike`) | **244 MB** | **139 MB** | **−105 MB** (`git gc` thường, KHÔNG rewrite) |
| File track trong `exp_*`/`probe_*` | 315 file, **~201 MB** | 279 file, **7,3 MB** | **−36 file / −194 MB** |
| File trên **đĩa** trong `exp_*`/`probe_*` | 203 MB | **203 MB** | **0 — KHÔNG XOÁ FILE NÀO** |

**0 thư mục XOÁ THẬT. 0 byte dữ liệu mất.** Tất cả là ARCHIVE (`git rm --cached` + `.gitignore`) — file
nằm nguyên trên đĩa, chỉ gỡ khỏi git tracking.

## 2. Vì sao KHÔNG xoá thật thư mục nào (dù nhiều thí nghiệm đã có report đầy đủ)

Tiêu chí XOÁ THẬT trong dispatch có 3 vế, vế thứ 3 **KHÔNG thoả với bất kỳ thư mục nào**:

> "kết luận đã có đầy đủ trong report ∧ không còn giá trị audit-trail ∧ **tái tạo được nếu cần bằng
> cách chạy lại script gốc**"

Panel thô ở đây **không tái tạo được**. Chúng dựng từ `tav2_bq.ticker` / `ticker_prune` /
`ticker_financial` tại một *vintage* cụ thể; mà theo đúng `coding_guidelines.md` §8b:
BQ time-travel đã tắt, `ticker`/`ticker_prune` bị TRUNCATE+rebuild mỗi ngày, corp-action restate
~2-3%/tuần. Chạy lại `fetch.py` hôm nay ra **số khác**, không phải số đã sinh ra kết luận trong
report. Đây chính xác là bài học đã đóng thành chính sách sau vụ re-pin R3 07-29 (`ticker_prune`
TRUNCATE làm bay 58 mã khỏi toàn bộ lịch sử).

⇒ Panel thô = **bằng chứng audit-trail duy nhất** cho các con số đã pin. Giá trị của nó không giảm
đi khi report đã viết xong — nó là cái để *kiểm chứng lại* report.

## 3. Chính sách áp dụng (ghi vào `.gitignore` của repo `mike`)

Trong `agents/Taylor/exp_*/` và `probe_*/`:
- **GIỮ TRACK**: script `.py`, report `.md`, bảng kết quả nhỏ (<512KB) — 279 file / 7,3 MB. Đây là
  phần *đọc được* và *tái lập được* của mỗi thí nghiệm.
- **KHÔNG TRACK** (vẫn trên đĩa): panel thô ≥512KB + **mọi** `.parquet`/`.pkl` — 36 file / 194 MB.
  Pattern `.parquet`/`.pkl` là wildcard nên panel binary tương lai tự động không lọt vào git; CSV
  lớn liệt kê tường minh (tránh vô tình nuốt mất 1 bảng kết quả nhỏ trong tương lai).

## 4. Bảng quyết định từng thư mục (bằng chứng đã grep thật, không đoán theo tên)

`ARCHIVE*` = có file bị untrack. `GIỮ NGUYÊN` = toàn bộ dưới ngưỡng, không đụng gì.

| Thư mục | Đĩa | Untrack | Kết luận đã viết ở đâu | Tham chiếu sống (grep) | QĐ |
|---|---|---|---|---|---|
| `exp_pb_exvic` | 105M | 101,9M | `research/market_regime_probability_20260729.md` | `exp_valframe/build_metrics.py`; `kb/events_buffer.md` | ARCHIVE* |
| `exp_valframe` | 34M | 32,3M | `research/fundamental_valuation_framework_20260729.md` | — | ARCHIVE* |
| `exp_roe` | 21M | 20,1M | `research/market_regime_probability_20260729.md` | `kb/memory/Taylor.md` | ARCHIVE* |
| `exp_insider` | 16M | 15,5M | `research/insider_transaction_scoping_20260729.md` | **DỰ ÁN ĐANG SỐNG** — cron 18:45 `insider_flags.py`, `kb/cron_registry.md:65`, review ~2026-08-29 | ARCHIVE* |
| `probe_fa_rebuild` | 6,4M | 6,1M | `kb/projects/fa-ratings-rebuild.md` (ĐÓNG) | chỉ `kb/archive/*-nightly.md` | ARCHIVE* |
| `exp_dividend` | 6,3M | 6,3M | `data/results_registry.md:3062` | ⚠️ `dividend_upgrade_test.py:21` **đọc file thật** (hardcode `EXPDIR`) | ARCHIVE* |
| `exp_pe2006` | 4,3M | 1,1M | `research/pe_history_floor_2006_2008_20260729.md` | — | ARCHIVE* |
| `exp_capitgate` | 3,4M | 3,3M | `exp_capitgate/RESULT.md` + `PREREG.md` | `exp_capitexit/build_panel.py` | ARCHIVE* |
| `exp_market_prob` | 2,9M | 2,6M | `research/market_regime_probability_20260729.md` | 6 script trong `exp_pb_exvic`/`exp_roe` đọc chéo | ARCHIVE* |
| `exp_breadth` | 1,7M | 1,6M | `factor_gap_audit_20260718.md` | — | ARCHIVE* |
| `exp_depgate` | 1,2M | 0,2M | `kb/projects/wc-deposit-rate-gate.md` (NO-GO) | ⚠️ `results_registry.md:3056` **"Treo: G5 quant-skeptic verify cả cụm D0-D3"** → artifacts phải còn | ARCHIVE* |
| `exp_capitexit` | 632K | 0,5M | `exp_capitexit/RESULT.md` | `deploy_golive_dt5g_v4/golive_recommend_v23.py:309` trích §3a | ARCHIVE* |
| `exp_capittrig` | 244K | 0,2M | `exp_capittrig/RESULT.md` | — | ARCHIVE* |
| `exp_capitdcf` | 276K | 0,03M | `exp_capitdcf/` (csv kết quả giữ track) | — | ARCHIVE* |
| `exp_dt5g_breadth_pit` | 616K | 0 | `research/dt5g_breadth_guard_universe_pit_20260729.md` | `macro_state_live.py:63` (**production**) trích A/B | GIỮ NGUYÊN |
| `exp_capit_breadth` | 504K | 0 | `research/ticker_prune_replacement_plan.md` | — | GIỮ NGUYÊN |
| `probe_golive_live_20260715` | 228K | 0 | `kb/archive/2026-07-19-nightly.md` | — | GIỮ NGUYÊN |
| `probe_capit_div` | 156K | 0 | `capit_dividend_gate_framework.md` | — | GIỮ NGUYÊN |
| `exp_capitadvcap` | 68K | 0 | `exp_capitadvcap/REPORT.md` | `trading_bot/plan.py:287` (**production**) trích selfcheck | GIỮ NGUYÊN |
| `exp_capit_dcf` | 44K | 0 | `exp_capit_dcf/capit_dcf_report.md` | — | GIỮ NGUYÊN |

**Không có tham chiếu nào bị gãy**: 6 tham chiếu từ code production (`macro_state_live.py`,
`trading_bot/plan.py`, `golive_recommend_v23.py`, `insider_flags.py`) đều là **comment/docstring
trích số**, không đọc file. Consumer duy nhất đọc-file-thật là `dividend_upgrade_test.py` — và
`git rm --cached` giữ file trên đĩa nên nó chạy y nguyên (đã smoke-test đọc lại được).

## 5. `.git` 244MB → 139MB: `git gc` thường, đã tự chạy

`git count-objects` trước: **214 MB loose objects** vs chỉ 27 MB in-pack — nghĩa là phần lớn dung
lượng là object rời chưa nén. `git gc` (18 giây, không rewrite, không xoá dữ liệu) gói lại còn
1 pack 138 MB. Đây là phần "miễn phí" của bài toán và đã lấy xong.

## 6. ĐỀ XUẤT LÊN USER — rewrite history: **KHUYẾN NGHỊ KHÔNG LÀM**

Đo thật (`git rev-list --objects --all` + `cat-file --batch-check`):

- Tổng blob trong history: **136,3 MB**
- Phần thuộc `agents/Taylor/exp_*`/`probe_*`: **99,8 MB (73%)**
- ⇒ `git filter-repo` gỡ các path này khỏi history sẽ đưa `.git` **139 MB → ~40 MB (−100 MB)**

**Nhưng cái giá cụ thể, đo được:**

1. **52 commit hash đang được KB trích dẫn làm bằng chứng sẽ thành dangling.** Grep `kb/` +
   `agents/*/research/` + `CLAUDE.md` ra 95 chuỗi dạng hash, trong đó **52 cái là commit CÓ THẬT
   trong repo `mike`**. Đây không phải trích dẫn trang trí — chúng là bằng chứng neo cho các thay
   đổi production (vd `d64717f` domain-constraint P1 LIVE, `8f95895` CAPIT breadth cutover,
   `dcee252`, `ce7d457`, `0bfbdfe`, `4995262`…). Rewrite = **mọi hash sau điểm rewrite đổi hết**,
   toàn bộ 52 trích dẫn trỏ vào hư không. Muốn giữ đúng phải sửa tay 52 chỗ trong KB — và bản thân
   việc sửa hàng loạt bằng chứng audit-trail lại là rủi ro lớn hơn 100 MB đĩa.
2. **Backup GitHub `minhtrido2023/thanhdt` (branch `mike-fleet`, cron 00:00 ICT) sẽ cần force-push**,
   phá lịch sử bản backup — tức là hy sinh chính cái lưới an toàn DR để tiết kiệm dung lượng.
3. **Không giải quyết vấn đề gì đang đau.** 139 MB `.git` không gây chậm, không gần giới hạn nào.

**Khuyến nghị: KHÔNG rewrite.** Chốt chặn tăng trưởng đã đặt xong (`.gitignore` §3) — đó mới là
nguyên nhân gốc. Nếu về sau `.git` lại phình, chạy lại `git gc` (miễn phí) trước khi tính rewrite.

**Nếu user vẫn muốn rewrite** — cần duyệt riêng, và điều kiện tối thiểu: (a) clone backup nguyên
trạng trước khi chạy; (b) map hash cũ→mới rồi sửa 52 trích dẫn KB trong cùng 1 commit; (c) thông
báo mọi worktree/clone khác phải re-clone.

## 7. Verify đã chạy

- `git status` sau commit: chỉ còn 3 file sửa **có sẵn từ trước, không thuộc job này**
  (`research/r3_repin_post_restate_20260729.md`, `kb/fleet_status.md`, `kb/memory/Mike.md`) — không
  commit nhầm.
- 36/36 file vẫn tồn tại trên đĩa sau commit (check `test -f` từng file).
- `du` thư mục `exp_*`/`probe_*`: 203 MB trước = 203 MB sau.
- `.gitignore` hoạt động: `git status --untracked-files=all` trên các thư mục này ra **0 dòng**
  (không bị hiện lại thành untracked).
- Smoke-test đọc lại 2 file bị untrack quan trọng nhất (`exp_dividend/panel_monthly.csv` consumer
  thật, `exp_insider/panel2.csv` dự án đang sống) — đọc OK bằng `$DNA_PYEXE` pandas.
