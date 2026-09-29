# VIỆC 2 — quét selfcheck nào KHÁC cùng backup/restore FILE THẬT

Job `Taylor_20260927_131720` · 2026-09-27 · branch `fix/selfcheck-realtree-residue-2709`
(worktree `mike/agents/Taylor/wt-scresidue-2709`, commit `6e9f11f1`, **CHƯA MERGE**)

## Kết quả một dòng

Quét **186 selfcheck** (`mike/bin/*selfcheck*.py` 99 file + `WorkingClaude/*selfcheck*.py` 87 file)
bằng **AST**. **KHÔNG còn file nào khác** thuộc đúng lớp lỗi `7b14e3e8` (selfcheck backup/restore
một FILE THẬT rồi tính gốc cây bằng ĐẾM CẤP `dirname`) — `nav_scripts_2account_selfcheck.py` là ca
DUY NHẤT, đã vá. Tìm được **2 defect lớp nhẹ hơn nhưng THẬT** (đã vá + chứng minh 2 chiều) và **1
tồn đọng hệ thống** cần user/Mike quyết.

## Cách quét (không phải grep)

`scan_writes.py` — AST, bắt: `open(...,"w"/"a"/"x"/"+")`, `to_csv/to_json/to_parquet/to_pickle/
to_feather/to_excel`, `Path.write_text/write_bytes`, `shutil.copy*/move/copytree`,
`os.replace/rename`, `os.mkdir/makedirs`. Phân loại đích **SAFE** nếu biểu thức đích — hoặc biến mà
nó dẫn xuất từ, truy vết lan truyền trong file đến khi ổn định — chạm `tempfile` / `mkdtemp` /
`TemporaryDirectory` / `NamedTemporaryFile` / `gettempdir` / `/tmp` / `TMPDIR`.

Kết quả thô: **24/186 file** có ≥1 điểm ghi mà scanner không chứng minh được là thư mục tạm
(`scan_writes.json`). Phần lớn là **âm tính giả** vì taint không đi qua biên hàm (đích là tham số
`workdir`/`path` do caller truyền, mà caller tạo bằng `mkdtemp`) — nên mỗi ca được kiểm tiếp bằng
`probe_realtree.sh`: chụp md5 cây THẬT (`data/trade_plans`, `data/execution_logs`,
`data/discretionary`, `data/state`, `mike/bin`, `mike/kb`) + tên/size/mtime `data/` gốc, trước và
sau khi chạy thật selfcheck đó.

> ⚠️ **Hai phiên bản đầu của probe cho kết quả DIRTY GIẢ** và tôi đã gần báo sai: `md5sum` (nhiều
> tiến trình do `xargs` chia lô) và `find` cùng ghi vào MỘT pipe ⇒ output xen vào nhau ⇒ diff nhiễu
> hàng trăm dòng. Bản đang dùng ghi mỗi nguồn ra FILE RIÊNG rồi nối. Ai tái dùng script này đừng gộp
> pipe lại.

## Phân hạng 24 ca

| Hạng | Nghĩa | Số ca | Ai |
|---|---|---|---|
| **(a)** ghi/để rác vào **cây đường tiền THẬT** | phải vá | **2** | `concurrent_lock_selfcheck.py`, `plan_check_field_schema_selfcheck.py` |
| **(b)** ghi artifact **research/baseline/source** thật (có chủ đích, hoặc có dọn) | ghi rõ, không vá | 5 | `mike/bin/annualization_basis_selfcheck.py` (baseline `kb/annualization_basis_baseline.json`, CHỈ khi `--update-baseline`) · `mike/bin/selfcheck_baseline_diff.py` (là CÔNG CỤ baseline-diff, không phải selfcheck; ghi baseline + result thật + post bus/Discord) · `mike/bin/reconcile_equity_egg_selfcheck.py` (ghi file mutation `_mut_reconcile_equity_*.py` vào `mike/bin` rồi `os.remove` trong `finally`) · `immutable_publish_selfcheck.py` (ghi `data/_ipsc_forged_*.csv` rồi `os.unlink`; còn publish vào bảng BQ sandbox) · `mike/bin/report_delivery_ledger_selfcheck.py` |
| **(c)** chỉ ghi thư mục tạm | an toàn | 17 | `cursor_advance`, `mike_json_has_event_prefix`, `worktree_stale_check`, `freshness_ops`, `edge_wlag_gate`, `quote_l2_logging`, `expected_volume_pacing`, `discretionary_accumulation`, `discretionary_participation_cap`, `netting_recon`, `rule_a_ceiling`, `hard_no_chase_ceiling`, `approval_gate`, `sync_cache_lock`, `screen_sort_direction`, `basket_price_basis` (khớp giả: `Series.replace`), `discretionary_margin_gate` |

Chứng cứ cho hạng (c): `probe_realtree.sh` báo **CLEAN** (md5 cây thật không đổi) cho
`approval_gate`, `concurrent_lock` (đường PASS), `discretionary_participation_cap`,
`rule_a_ceiling`, `hard_no_chase_ceiling`, `netting_recon`, `edge_wlag_gate`,
`expected_volume_pacing`, `discretionary_accumulation`, `screen_sort_direction`. Các ca còn lại
kết luận bằng đọc mã (biến đích đến từ `mkdtemp` của caller).

## Ca (a) #1 — `concurrent_lock_selfcheck.py`

Mẫu dọn-TRƯỚC là `exec_{TAG}*_.lock` — dấu `_` đặt SAU dấu `*` — nên **không bao giờ** khớp tên
thật `exec_selfcheck-lock_2099-01-01.lock` mà `_acquire_account_lock()` tạo ⇒ nhánh "tự lành sau
lần chạy trước bị đứt" là **no-op im lặng**. Thân file cũng không có `try/finally` ⇒ một check FAIL
giữa đường để lại 2–3 file `.lock` trong `data/execution_logs/` THẬT.

**Vá:** glob đúng + `atexit.register` (phủ cả đường `raise` giữa file) + 2 check MỚI đo **bằng
chứng trên đĩa**: `A2` file lock thật vừa tạo có tồn tại trong EXEC_DIR mà selfcheck đang dọn, `A2b`
`_LOCK_GLOB` có KHỚP file đó. Bản nháp đầu của tôi so hằng số `EXEC_DIR` hai bên — **guard vô
nghĩa**, vì `bot_execute` import đúng hằng số ấy từ `trading_bot.config` nên phép so luôn đúng theo
cấu trúc; đã thay bằng 2 check bằng-chứng ở trên.

## Ca (a) #2 — `plan_check_field_schema_selfcheck.py`

Chỉ có vòng dọn TRƯỚC khi chạy ⇒ sau **mỗi** lần chạy còn lại đúng một
`exec_selfcheck_chkfield_2026-08-14_journal.csv` trong EXEC_DIR THẬT (đo bằng md5 trước/sau: nội
dung ĐỔI mỗi lần chạy — nó thật sự được ghi lại, không phải file cũ nằm im). Thêm một hình dạng
`7b14e3e8` đang NGỦ: `_EXEC_DIR` tự tính theo vị trí FILE NÀY, còn `Executor` ghi theo
`trading_bot.config.EXEC_DIR` — mà `config.py:13` cho `TRADING_BOT_RUNTIME_ROOT` **ghi đè gốc**, nên
đặt biến đó là hai bên tách đôi im lặng.

**Vá:** lấy đường dẫn từ CHÍNH module bị kiểm (`trading_bot.config.EXEC_DIR`) + **fail-closed** khi
nó lệch cây của file này mà KHÔNG có `TRADING_BOT_RUNTIME_ROOT` giải thích + `atexit` dọn.

## Chứng minh 2 CHIỀU (đo thật, không suy luận)

| | bản CŨ | bản MỚI |
|---|---|---|
| `concurrent_lock` + tiêm `raise` giữa đường + gieo sẵn 1 file rác `..._1999-01-01.lock` | residue **2** | residue **0** |
| mutation: trả glob về đúng typo gốc | — | **A2b FAIL** (bị giết) |
| mutation: bỏ `atexit.register` + tiêm `raise` | — | residue **1** (bị giết) |
| `plan_check_field_schema` chạy bình thường | residue **1** | residue **0** |
| `plan_check_field_schema` trên canonical | `Ran 14 tests OK` | `Ran 14 tests OK` + dọn luôn file rác tồn sẵn |

Cả hai bản mới: **3 môi trường TZ** (`Asia/Ho_Chi_Minh`, `America/New_York`, **gỡ hẳn** `TZ`) đều
PASS và residue=0, chạy dưới `$DNA_PYEXE`. Không file nào dùng `datetime.now()`/`date.today()` nên
§16 không áp.

## Tồn đọng HỆ THỐNG — cần user/Mike quyết, TÔI KHÔNG TỰ XOÁ

`data/execution_logs/` THẬT hiện chứa **~70 file sentinel** của selfcheck/stress-test còn tồn từ
tháng 7 tới 04:31–04:58 hôm nay (`exec_selfcheck-*`, `exec_selfcheck_*`, `exec_tickcheck-*`,
`exec_STRESSTEST*`, `probe_ticks_selfcheck-*`, `exec_dbg_2099-*`, `exec_rehearsal-*`). Chúng
**diff-vô-hình**: đã có mặt cả trước và sau khi chạy nên snapshot md5 báo CLEAN — đúng cái bẫy khiến
lớp lỗi này sống lâu.

Mức nguy hiểm đã **kiểm chứ không đoán**: 3 consumer glob rộng trong EXEC_DIR
(`mike/bin/park_holdings.py:129` `exec_*_journal.csv`, `daily_nav_snapshot.py:158`,
`verify_account_snapshot.py:631`) — **cả 3 đều lọc theo `label`/`account` NGAY sau glob**, nên rác
hiện tại KHÔNG chảy vào số báo cáo. Vì vậy đây là **rác, không phải nhiễm bẩn**. Đề xuất (chưa làm):
(1) dọn một lần theo danh sách tiền tố sentinel; (2) đưa mẫu `atexit`-dọn của 2 file vừa vá thành
khuôn chung cho mọi selfcheck ghi vào EXEC_DIR/PLAN_DIR.

## Artifact

`mike/agents/Taylor/research/selfcheck_write_scan_20260927/`: `scan_writes.py`, `scan_writes.json`,
`probe_realtree.sh`, `probe_logs/`, `probe{2,3,4}.out`, `REPORT.md` (file này).
