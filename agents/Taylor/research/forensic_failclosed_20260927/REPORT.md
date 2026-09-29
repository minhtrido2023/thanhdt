# VÁ fail-open `forensic_flags.csv` → FAIL-CLOSED (`custom_basket.py`) — job `Taylor_20260927_145418`

Branch `fix/forensic-flags-fail-closed`, commit **`e548fd73`** (worktree
`mike/agents/Taylor/wt-forensic-failclosed-2709`). **CHƯA MERGE.** Không đặt lệnh.
User duyệt 21:52 ICT 2026-09-27.

## 1. Bản vá

| | Trước | Sau |
|---|---|---|
| Thiếu / không đọc được file | `print("[forensic exclude] none ({e})")` rồi ĐI TIẾP (fail-OPEN) | **SystemExit** — trích exception THẬT từng đường dẫn (§29), nêu hệ quả + 3 lối thoát |
| Nơi tìm file | CHỈ cây của module (`__file__`) | cây module → **cây canonical** qua `git rev-parse --git-common-dir` (không hardcode) |
| Muốn chạy KHÔNG lọc | không có cách nào ngoài… để file thiếu | `BASKET_FORENSIC_FLAGS=` rỗng (rỗng ≠ thiếu file) |
| env trỏ một path | — | dùng ĐÚNG path đó; thiếu/hỏng ⇒ chặn, **không** âm thầm rơi về canonical |

Fallback canonical cùng khuôn `basket_price_basis_selfcheck._ca_snapshot_candidates()` (merge
`07d5b4ad`). Một sửa nhỏ so với khuôn gốc: `--git-common-dir` có thể trả đường dẫn TƯƠNG ĐỐI và nó
tương đối với `cwd=here`, không phải cwd của process ⇒ join với `here` trước khi normalise
(khuôn gốc dùng `os.path.abspath` nên phụ thuộc cwd; ở đây `cwd == here` nên không cắn, nhưng bản
này không phụ thuộc).

## 2. KHÔNG mâu thuẫn với `lag_forensic_filter.py:67` (fail-open CÓ CHỦ Ý)

Hai hàm trả hai thứ khác nhau, nên hai fail-mode khác nhau là đúng:

- `lag_forensic_filter` = **cổng chặn lệnh runtime** book LAG. Dưới nó còn sàn `BANNED` (hằng số
  trong CODE, không thể hỏng) và nó **trả error string** cho `status.json` ⇒ không im lặng.
  Fail-closed ở đó = chặn TOÀN BỘ book LAG vì một file lỗi.
- `custom_basket` = **tầng dựng UNIVERSE** của backtest/re-pin. KHÔNG có sàn nào phía dưới, đầu ra
  là một CON SỐ ghim vào `data/results_registry.md`. Fail-open ở đây không chặn ai — nó sinh số SAI
  trông như đúng.

Chính comment `lag_forensic_filter.py:71-73` đã gọi tên fail-mode này ("thiếu file ⇒ fail-open ⇒
im lặng thôi loại") khi giải thích vì sao KHÔNG thêm IVS/TMG vào file đó. Bản vá đóng nó ở đúng
call-site không có sàn — không đụng `lag_forensic_filter`.

## 3. ⚠️ PHÁT HIỆN QUAN TRỌNG HƠN BẢN VÁ — engine bỏ qua cây worktree

`pt_v23_audit_2014.py:41-42` **HARDCODE** `WORKDIR = r"/home/trido/thanhdt/WorkingClaude"` rồi
`sys.path.insert(0, WORKDIR)` ⇒ chạy engine từ worktree **vẫn import `custom_basket` của cây
CANONICAL** (`sys.path[0]` bị chèn trước cả dir của script và trước `PYTHONPATH`).

Hệ quả đo thật: chân đầu tiên chạy runner từ worktree (`exp_forxfailclosed_wt.log:22`) in **format
LOG CŨ** ⇒ bản vá không hề được nạp. Phải nạp module vá vào `sys.modules["custom_basket"]` TRƯỚC
rồi `runpy` engine canonical (`inject_patched_basket.py`) mới thật sự chạy được bản vá.
**Hệ quả rộng hơn: mọi "A/B trong worktree" trên bất kỳ module nào engine này import đều có nguy cơ
là NO-OP im lặng** — cùng lớp bẫy với fail-open đang vá, chỉ đổi chỗ từ DỮ LIỆU sang CODE.

## 4. Lệnh pin R3 (sexies) — KHÔNG ĐỔI, byte-identical

| | Pin (sexies) | Chân CONTROL (code canonical) | Chân **PATCHED** (module vá) |
|---|---|---|---|
| ledger md5 | `4707bcbeb7e801d49a4a851ffd91d5e7` | `4707bcbe…` | **`4707bcbe…`** |
| `cmp` vs pin | — | SẠCH | **SẠCH** |
| dòng | 16.633 | 16.633 | **16.633** |
| Final NAV / CAGR / Sharpe / MaxDD / Calmar | 684,52B / 23,37% / 1,88 / −14,6% / 1,60 | khớp | **khớp** |
| borrow-audit | 0 VND | 0 VND | **0 VND** |
| `extract_peryear.py` độc lập | 23,37 / 20,00 / 26,50 | — | **23,37 / 20,00 / 26,50** |

Env NGUYÊN VĂN pin: `$DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python`,
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`,
`BASKET_CA_SNAPSHOT=…/corp_action_share_20260927.parquet`, `NAV_TOTAL_B=50 ETF_LIQ=custompitg
BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 AUDIT_END=2026-06-19`,
`pt_v23_audit_2014.py v23a none postbull 0 edge`. EXP_TAG non-canonical (§8): `forxfc_patched`,
`exp_forxfailclosed_wt`. Runner: `run_leg.sh`, `run_leg_patched.sh`, `inject_patched_basket.py`.

Chân PATCHED chạy khi cây worktree **CỐ Ý KHÔNG có** `data/forensic_flags.csv` ⇒ đồng thời chứng
minh fallback cây canonical gánh được chính lệnh pin (log: `[forensic exclude]
/home/trido/thanhdt/WorkingClaude/data/forensic_flags.csv [cây canonical]` + đúng 8 mã).

**Xác nhận cảnh báo của Mike:** số pin R3 **PHỤ THUỘC** một file KHÔNG được git theo dõi. Nó tái
lập được hôm nay chỉ vì runner `cd` về canonical và engine hardcode `WORKDIR` về canonical. Từ một
clone sạch / máy khác, cùng commit + cùng lệnh sẽ cho số KHÁC mà không cảnh báo gì (trước bản vá).

## 5. Chứng minh 2 chiều (selfcheck `custom_basket_forensic_failclosed_selfcheck.py`)

**140 assertion × 4 TZ (Asia/Ho_Chi_Minh, America/New_York, UTC, `env -u TZ`) PASS · 6/6 mutation
bị giết · `$DNA_PYEXE` (3.12.13).**

- **T3 = 2 chiều trên CÙNG sandbox**, bản CŨ lấy **NGUYÊN VĂN từ `git show HEAD:…custom_basket.py`**
  (không chép tay): thiếu file ⇒ cũ trả `{}` + in "none" + đi tiếp, **mới TỪ CHỐI CHẠY**; có file ⇒
  **hai bản trả CÙNG một dict 8 mã**.
- T1 fallback canonical thật (worktree không có file → vẫn đủ 8 mã, in `[cây canonical]`).
- T2 thiếu ở mọi cây ⇒ SystemExit, thông điệp chứa `FileNotFoundError` thật + đường dẫn + 3 lối
  thoát + hệ quả (8 mã / BANNED).
- T4 env rỗng = opt-out tường minh. T5 env trỏ sai ⇒ chặn, KHÔNG rơi về canonical.
  T6 file hỏng lược đồ ⇒ chặn, trích `KeyError: 'severity'` thật.
- Mutation: M1 fail-open lại · M2 bỏ cây canonical · M3 env rỗng bị coi như thiếu file · M4 env sai
  rơi về canonical · M5 thông điệp không trích exception thật (§29) · M6 bỏ hệ quả khỏi thông điệp.
  Mutant được ghi vào **CÙNG cây** với module thật — bản đầu ghi vào `/tmp` nên MỌI mutant "bị
  giết" giả bởi T1 (ngoài git ⇒ không có cây canonical), tức harness vô nghĩa; đã sửa.

## 6. Quét call-site khác — **13 nơi, LIỆT KÊ, KHÔNG tự sửa**

Đường dẫn TƯƠNG ĐỐI (`"data/forensic_flags.csv"`) ⇒ phụ thuộc cwd, không chỉ cây:

| File:line | Fail-mode | Blast radius |
|---|---|---|
| `rating_8l.py:517-523` | `print("forensic_flags load fail (no overrides):", e)` + đi tiếp | **CAO NHẤT — LIVE.** Ép rating=5 cho mã bị cờ; mất override ⇒ mã bị cờ giữ rating thật ⇒ QUA gate ≤3 của BAL/custom30V/CAPIT. `WORKDIR_8L` override được ⇒ trỏ vào worktree là mất lọc |
| `pt_v23_audit_2014.py:1083-1085` | **`except Exception: pass`** (im lặng hoàn toàn) | engine sinh chính số pin R3 (leg LAG) |
| `pt_v22_dt5g.py:433-435` | `except Exception: pass` | engine backtest |
| `pt_v23_lagqual_research.py:1046-1048` | `except Exception: pass` | engine backtest |
| `pt_v23_lagcap_research.py:1046-1048` | `except Exception: pass` | engine backtest |
| `converge_fullharness_test.py:896-898` | `except Exception: pass` | harness hội tụ |
| `lag_dnpr_harness.py:784-786` | `except Exception: pass` | harness DNPR |
| `lag_dnpr_eventstudy.py:46-48` | `except Exception: pass` | event study |
| `rating_8l_history.py:600-612` | `print("  forensic_flags load fail:", e)` + đi tiếp | bảng rating lịch sử |
| `build_rating_8l_history.py:278-285` | `print("  forensic_flags load fail:", e)` + đi tiếp | builder bảng rating lịch sử |
| `lag_forensic_audit.py:46-47` | `except Exception: fset=set()` | công cụ audit (ad-hoc) |
| `forensic_screen.py:28-29` | `except Exception: fexist=set()` | công cụ screen (ad-hoc) |
| `lag_forensic_filter.py:67` | fail-open **CÓ CHỦ Ý, có tài liệu** | book LAG — xem §2, KHÔNG sửa |

**7 nơi dùng `except Exception: pass` = tệ hơn `custom_basket` trước vá** (không cả một dòng log).
Ưu tiên nếu user muốn xử: `rating_8l.py` (đường LIVE) → 7 engine `pass` → 2 builder history →
2 công cụ ad-hoc (fail-open chấp nhận được).

## 7. ĐỀ XUẤT (không tự làm) — đưa `forensic_flags.csv` vào git hay không?

**Nội dung có nhạy cảm không:** KHÔNG chứa credential/PII. Chứa **phán quyết forensic về doanh
nghiệp niêm yết**, gồm câu như PC1 "CONFIRMED criminal fraud: … MPS arrested entire C-suite" và
7 mã khác bị gán `pump_no_moat` / `related_party`. Rủi ro là **danh dự/pháp lý** (nếu rò ra ngoài),
không phải rủi ro bảo mật kỹ thuật.

**Mode 600 — không tìm được bằng chứng là có chủ ý.** File do người sửa tay (`forensic_screen.py:42`
"confirmed -> add to data/forensic_flags.csv"), không script nào `chmod` nó; mọi process của fleet
chạy dưới cùng user `trido` nên 600 không chặn ai trong hệ. Có vẻ là umask của editor, **nhưng đây
là suy luận từ sự vắng mặt — nên hỏi user xác nhận trước khi nới quyền** (§28).

**Khuyến nghị: A — `git add -f` để git THEO DÕI**, kèm 2 điều kiện:
1. Lý do quyết định: số pin R3 (và mọi số pin của V2.4) **phụ thuộc byte-for-byte** vào file này
   (§4). Một artifact quyết định con số pin mà không có version control thì con số **không tái lập
   được** ở clone khác, và **không có lịch sử ai đổi gì khi nào** cho một danh sách mang tính phán
   quyết. Thêm nữa, vì bị `.gitignore` nên nó **KHÔNG nằm trong backup GitHub hằng ngày** ⇒ hiện
   chỉ tồn tại trên một máy, không bản sao.
2. Trước khi `git add -f`: nhờ **Wendy (legal-vn)** soát rủi ro nêu trên, vì repo được mirror lên
   GitHub (private) hằng ngày — phán quyết "criminal fraud" về một công ty niêm yết nằm trong một
   repo có thể đổi quyền truy cập là rủi ro cần một câu trả lời, không phải một giả định.

**Nếu user KHÔNG muốn track** (hợp lệ, nhất là nếu Wendy cảnh báo): giữ ngoài git + fallback
canonical của bản vá này, **và thêm md5 của `forensic_flags.csv` vào mỗi mục pin trong
`data/results_registry.md`** — để một lần đổi file âm thầm sau này phát hiện được bằng số, thay vì
phải tin rằng nó không đổi.
