# Kiểm kê fail-open — ĐỢT 2: đóng 4 lỗ mà §2 của REPORT.md tự khai chưa phủ

**Job**: `Taylor_20260928_030132` · **Tiếp nối**: `REPORT.md` (job `Taylor_20260928_005930`)
**Ranh giới**: CHỈ LIỆT KÊ. Không sửa file nào ngoài thư mục này. Không merge, không dispatch.

---

## 0. Kết quả một dòng

Bốn lỗ đã đọc hết trong phạm vi đã khai. **11 hit thật mới** (7 ở LỖ 1, 4 ở LỖ 2), **2 kết luận
"an toàn" chốt được** (LỖ 3), **1 nhánh over-order KHÔNG có lưới nào che** (LỖ 4, `executor.py:1959`).

Nặng nhất — cả ba đều cùng một hình dạng **"bộ sinh CẢNH BÁO hỏng ⇒ sự VẮNG MẶT của cảnh báo bị
đọc là 'mọi thứ ổn'"**:

1. `pt_8l_daily.sh:46` — checker độ tươi DT5G crash ⇒ script in **"DT5G tươi (publisher của ta đã
   xác nhận hôm nay)"**. Không phải im lặng — là **khẳng định SAI chủ động**.
2. `golive_recommend_v23.py:731` — `rating8l.fillna(0) >= 4` ⇒ mã **thiếu** 8L rating được coi là
   KHÔNG yếu ⇒ ăn trọn `POS_PCT` thay vì `WEAK_PCT`, và nhánh này chỉ chạy khi state ∈ {CRISIS, BEAR}.
3. `trading_bot/executor.py:1959` — `cancel_order` fail ⇒ `except Exception: pass` ⇒ lệnh LO **vẫn
   sống trên sổ sàn** rồi vẫn đặt tiếp ATC cho TOÀN BỘ phần còn lại ⇒ **bán vượt kế hoạch**.
   `atc_remainder_sell = True` trong `config.py:144` ⇒ nhánh này ĐANG BẬT cho chiều BÁN.

---

## 0b. ⚠️ Số dòng của REPORT.md đợt 1 ĐÃ DRIFT — phải re-anchor

`hits_L4_full.tsv` sinh lúc **08:10**; batch-1 merge vào cây làm việc lúc **08:58**
(`mike` @ `afc1e6b5`). Hệ quả đo được:

| | đợt 1 (08:10) | đợt 2 (re-scan HEAD, 10:05) |
|---|---:|---:|
| Tổng dòng L4 | 295 | **294** |

Ví dụ cụ thể: `check_sbv_weekly.sh:32/38` trong REPORT.md §4a (#7/#8) **không còn tồn tại** —
file đã fail-CLOSED, dòng tương ứng giờ ở `:38-45`. **Mọi `file:line` trong báo cáo NÀY neo vào
HEAD hiện tại**, artifact `hits_L4_rescan_HEAD.tsv`. Đừng trộn hai bảng.

---

## 1. LỖ 1 — 123 dòng L4 `|| true` trên lệnh KHÔNG phải notify

### 1.1 Phân hoạch lại (khác đợt 1, và vì sao)

Đợt 1 chia 295 = 114 notify + 53 `||echo` + 128 chưa đọc. Heuristic đó dựa trên **từ khoá xuất
hiện ở đâu đó trong dòng**, nên xếp nhầm cả 2 chiều: dòng nối tiếp của một lệnh `notify_thread.sh`
(từ khoá nằm ở dòng TRÊN) rơi vào nhóm "chưa đọc", còn dòng có chữ `discord_thread_id` trong tên
biến lại rơi vào nhóm "vô hại".

Phân hoạch đợt 2 trên HEAD, quyết bằng **lệnh thật sự bị triệt tiêu rc** (đọc ngược lên dòng đầu
của câu lệnh), không bằng từ khoá:

| Nhóm | Dòng | Xử lý |
|---|---:|---|
| **COMMENT** — dòng chú thích, không phải code | **12** | False-positive của mẫu grep. 7/12 chính là chú thích **cảnh báo về đúng antipattern này** từ sự cố trước (`consolidate.sh:121`, `cron_health_check_daily.sh:53`, `dispatch.sh:180/1702`, `ops_health_check.sh:1054/1440`, `vendor_mismatch_alert.sh:248`) |
| **NOTIFYCMD** — rc của `notify.sh`/`notify_thread.sh`/`append_event.sh` | **109** | Vô hại theo đúng lý do đợt 1 nêu |
| **ECHO** — `\|\| echo <giá trị>` | **50** | Đợt 1 đã đọc tay (53 ở HEAD cũ; batch-1 gỡ 2 ở `check_sbv_weekly.sh`) |
| **OTHER — đây là lỗ này** | **123** | **ĐỌC HẾT trong đợt 2** ↓ |

123 dòng OTHER chia 5 lớp: `A-SOURCEENV` 15 · `C-CLEANUP` 21 · `D-VAR` 31 · `E-CONT` 16 ·
`F-STMT` 40. Bảng đầy đủ kèm nhãn lớp: `hits_L4_dot2_classified.tsv`.

### 1.2 Hit thật — 7

| # | file:line | Lệnh bị triệt tiêu rc | Dữ liệu/bước bị bỏ im lặng | Ảnh hưởng | Chiều | Đề xuất |
|---|---|---|---|---|---|---|
| **L1-1** | `pt_8l_daily.sh:46` | `timeout 60 $PY dt5g_freshness.py --warn-line` | Checker crash/timeout ⇒ `DT5G_WARN=""`. Dòng `if [ -n "$DT5G_WARN" ]` ngay dưới đọc **rỗng = TƯƠI** ⇒ nhánh `else` in `"--- [0-fresh] DT5G tươi (publisher của ta đã xác nhận hôm nay) ---"` | **SỐ ĐƯỢC PIN** — chính comment ở `:42-45` nói bảng xếp hạng 8L + alert Telegram tối nay chạy theo regime này | **KHÔNG AN TOÀN** — không phải im lặng mà là **KHẲNG ĐỊNH SAI**: vận hành được báo "đã xác nhận" trong khi chưa xác nhận gì (§29 dạng 2) | Tri-state: rc≠0 ⇒ `DT5G_WARN="KHÔNG kiểm được độ tươi (rc=$rc): $_err"`, **không** rơi vào nhánh `else` |
| **L1-2** | `mike/bin/ops_health_check.sh:64` | `python3 -c "from trading_bot.config import live_dnse_labels …"` | Import lỗi ⇒ `RUNONCE_LABEL=""`. Ba check chạy-một-lần đều gác bằng `[ -n "$RUNONCE_LABEL" ]` (`:1716` anomaly_scan, `:1756` forensic_check, `:1778` worktree_stale) ⇒ **cả ba biến mất cho CẢ HAI account** | **TIỀN THẬT (gián tiếp)** — anomaly + forensic là cổng lọc mã | **KHÔNG AN TOÀN** — cấp dưới của chính ca mà comment `:60-63` đã tả ("bản cũ lặng lẽ KHÔNG chạy check nào cả"): họ vá nhánh `ls[0]` rỗng, **không** vá nhánh exception | Bắt `2>&1` vào biến; rỗng do LỖI ⇒ WARN vào report, khác rỗng do "không có account live" |
| **L1-3** | `telegram_run_daily.sh:22` | `csv_fresh_today.sh data/rating_8l.csv '⚠️ …'` | Script độ tươi lỗi ⇒ `EXTRA_WARN_HEADER=""` ⇒ dòng ⚠️ "8L rating có thể chưa cập nhật" **biến mất khỏi đầu tin Telegram** | **BÁO CÁO TỚI USER** — đúng cổng §14 mà job `Winston_20260731_062642` dựng ra | **KHÔNG AN TOÀN** — người nhận thấy rating cũ y hệt rating mới, không còn dấu hiệu nào | rc≠0 ⇒ set header thành "KHÔNG kiểm được độ tươi input" (vẫn gửi, nhưng nói thật) |
| **L1-4** | `mike/bin/eod_trading_report.sh:179` | `timeout 60 python3 dt5g_freshness.py --warn-line` | y như L1-1 nhưng dùng qua `${DT5G_WARN:+…}` ở `:296`/`:648` | **BÁO CÁO** | **KHÔNG AN TOÀN nhẹ** — chỉ MẤT dòng cảnh báo, không khẳng định ngược lại (nhẹ hơn L1-1) | cùng cách vá L1-1 |
| **L1-5** | `mike/bin/backup_freshness_check.sh:39` | `timeout 120 git fetch -q "$remote" "$branch"` | Fetch lỗi ⇒ `cat-file -e` vẫn fail ⇒ nhánh `else` chỉ thêm dòng thông tin `"remote <sha> (không đọc được tuổi)"` vào `LINES`, **KHÔNG** thêm gì vào `PROBLEMS` ⇒ báo cáo backup xanh | **nội bộ / DR** — script tồn tại để phát hiện backup chết | **KHÔNG AN TOÀN** — bất đối xứng ngay trong cùng hàm: `ls-remote` fail thì **CÓ** ghi PROBLEMS (`:34`), fetch fail thì không | Không đọc được tuổi ⇒ ghi PROBLEMS, đó chính là "backup không kiểm chứng được" |
| **L1-6** | `mike/bin/append_event.sh:70` | `python3 - … "$BUS/_rejected.jsonl" …` (ghi file cách ly) | Ghi cách ly fail ⇒ nuốt; nhưng `die()` ở `:76` vẫn in **"arg bị chặn đã lưu vào $BUS/_rejected.jsonl"** | **nội bộ** (pháp y bus) | **KHÔNG AN TOÀN** — §29 dạng 1 đúng nghĩa: thông điệp hứa một artifact có thể không tồn tại. Trớ trêu: docstring ngay trên (`:60-68`) là bài học từ đúng lớp lỗi này | Bắt rc; fail ⇒ đổi câu thành "KHÔNG lưu được vào …: <lỗi thật>" |
| **L1-7** | `mike/bin/worktree_cleanup_daily.sh:160` | `git -C "$wt" status --porcelain --untracked-files=normal` | `git status` lỗi (index.lock, repo hỏng, quyền) ⇒ chuỗi rỗng ⇒ **"không dirty"** ⇒ rơi xuống `worktree remove` + `branch -d` | **nội bộ** (mất việc dở) | **KHÔNG AN TOÀN về logic**, nhưng **thực tế thấp**: đã qua cổng `merge-base --is-ancestor` (chỉ nhánh đã merge), và `git worktree remove` **không** `--force` nên git tự từ chối nếu bẩn thật. Cái mất là **kế toán + chẩn đoán** (`N_KEPT_DIRTY` sai, không ai biết vì sao) | Phân biệt rc≠0 với "sạch"; rc≠0 ⇒ `KEEP unknown` |

### 1.3 Đã đọc và KẾT LUẬN ỔN (ghi lại để đợt sau khỏi đọc lại)

| Vị trí / lớp | Vì sao ổn |
|---|---|
| `worktree_cleanup_daily.sh:74` (`active_csv`) | **fail-CLOSED tường minh**: rỗng ⇒ `say "WARNING: không đọc được CCDB — fail-closed, sẽ không xoá gì"` |
| `preflight_check.sh:51` | `ls … \|\| true` nhưng ngay dưới `[ -z ] \|\| [ ! -f ] ⇒ _fail` ⇒ fail-CLOSED |
| `fearbuy_weekly_scan.sh:79` và `:92` | Rỗng ⇒ thay bằng khối text "KHONG SINH DUOC … TUYET DOI KHONG tu bia danh sach". Fail-soft NHƯNG **nói to vào đúng nơi LLM đọc** — đây là khuôn mẫu đúng |
| `ops_autofix.sh:71` | Gác bằng `[ -s "$STARTED_ISO_FILE" ]` + `[ -n "$LAST_ISO" ]` |
| `ops_health_check.sh:1779` | `2>&1 \|\| true` — **giữ** stderr vào biến ⇒ lỗi hiện trong report, không mất |
| `consolidate.sh:91`, `publish_context.sh:13` | `\|\| true` rồi `${ver:-0}` tường minh; version 0 là giá trị hợp lệ có ý nghĩa |
| `discretionary_candidate_funnel` / `check_sbv_weekly.sh:136` | Alert Telegram; python bên trong đã `except … print('FAILED')` ra **stdout** (không bị `2>/dev/null` ăn) |
| **Lớp `C-CLEANUP`** (21 dòng): `kill`, `rm -f`, `mkdir -p`, `disown`, `mv -f`, `systemctl reset-failed` | Dọn dẹp best-effort; thất bại không sinh quyết định sai. Ngoại lệ đã tách ra L1-6 |
| **Lớp `A-SOURCEENV`** (15 dòng): `[ -f wc_env.sh ] && source … 2>/dev/null \|\| true` | 10/15 nằm trên đường tiền (`run_bot.sh`, `preflight_check.sh`, `compute_active_nav_all.sh`, `jit_unpark_daily.sh`, `park_trim_daily.sh`, `merge_park_daily.sh`, `inject_discretionary_orders.sh`, `send_plan_report.sh`, `bot_heartbeat.sh`, `late_plan_catchup.sh`). **AN TOÀN theo hệ quả**: env thiếu ⇒ python/bq dưới hạ nguồn fail TO. Nhưng **nếu bao giờ sửa lớp này** thì sửa cả 15, đừng 1 chỗ (§22) |
| **Lớp `NOTIFYCMD`** (109) + **COMMENT** (12) | Không phải hit |

---

## 2. LỖ 2 — mẫu `.get(k, <mặc định>)` / `fillna(<hằng>)` / `or <mặc định>`

### 2.1 Phạm vi ĐÃ THU HẸP — và chính xác những gì BỊ BỎ (§29)

Đúng như đợt 1 nói: **không có cách cơ học** phân biệt `.get()` hợp lệ với `.get()` che file hỏng.
Thu hẹp đã dùng (script `repro_scan_L5b.py`, chạy bằng `$DNA_PYEXE`, AST không regex):

1. Chỉ file **tier A + tier B** trong `scope_live_py.txt` → **396 hit thô**
   (GET_DEFAULT 238 · OR_DEFAULT 140 · FILLNA 18; 0 file không parse được).
2. Lọc theo từ khoá ngữ nghĩa tiền/sizing/trần trong CHÍNH dòng code
   (`qty|price|cap|nav|cash|limit|pct|weight|rate|size|target|thresh|max|min|adv|slot|lever|fee|
   margin|rating|lag|age|day|notional|amount|balance|debt|exposure|alloc|band|floor`)
   → **217 dòng**.
3. Đọc tay: 5 GET_DEFAULT truy được 1-hop về `json.load`/`read_csv` · 12 FILLNA (toàn bộ) ·
   21 OR_DEFAULT có mặc định KHÁC 0 · 68 GET_DEFAULT nằm trong 16 file đường tiền.
   **≈106 dòng đã đọc từng dòng.**

**BỎ, và theo tiêu chí nào — đừng đọc phần này là "đã quét hết":**

| Bỏ | Số | Tiêu chí / vì sao |
|---|---:|---|
| Tier C + tier S | không đếm | Ngoài phạm vi dispatch |
| 396 → 217 bởi bộ lọc từ khoá | **179** | Dòng không có từ ngữ nghĩa tiền/sizing. **Đây là bỏ theo HÌNH THỨC chứ không theo hệ quả** — một `.get("x", 1)` đặt tên trung tính vẫn có thể vào công thức tiền |
| GET_DEFAULT không truy được về file trong **1 hop** | **121/126 tier A** | Máy dò chỉ bắt `v = json.load(...)` rồi `v.get(...)`. Cấu hình đi qua **hàm helper** (`_load_json(path)`, `load_rules()`) là **vô hình** với nó. Đây là lỗ phụ còn lại lớn nhất |
| `.get(k, None)`, `.get(k, {})`, `.get(k, [])` | không quét | Cố ý: đợt 1 đã phủ lớp "giá trị RỖNG" bằng L2/L3 |
| `try: open(...) except FileNotFoundError: <default>` | **không quét** | Đợt 1 khai là chưa phủ; đợt 2 **vẫn chưa phủ** |
| Mẫu `.get()` trên dict **trả về từ API broker** (không phải file) | nhiều | Ngoài phạm vi dispatch ("đọc từ FILE/JSON/CSV"). **Đây là một lớp riêng chưa ai kiểm kê** |

### 2.2 Hit thật — 4

| # | file:line | Mẫu | Hệ quả im lặng | Ảnh hưởng | Chiều | Đề xuất |
|---|---|---|---|---|---|---|
| **L2-1** | `deploy_golive_dt5g_v4/golive_recommend_v23.py:731` | `today["rating8l"].fillna(0).astype(float) >= 4` | `rating8l` map từ `rating_8l.csv`. Mã **thiếu** rating ⇒ NaN ⇒ **0** ⇒ `0 >= 4` False ⇒ **không bị coi là yếu** ⇒ dòng kế `np.where(weak & half_in_state, WEAK_PCT, POS_PCT)` cho nó **POS_PCT đầy đủ**. Mà `half_in_state = state_today in (1,2)` ⇒ **chỉ có tác dụng trong CRISIS/BEAR** | **TIỀN THẬT** — trọng số slot của book BAL | **KHÔNG AN TOÀN, và tệ đúng lúc**: cơ chế giảm size cho mã yếu biến mất **chính xác trong sụt giảm**, cho mã mà ta KHÔNG BIẾT chất lượng | `fillna(99)` (thiếu rating ⇒ coi là yếu). **Bằng chứng khả thi**: `mike/bin/discretionary_candidate_funnel.py:325` đã dùng đúng `cohort["rating"].fillna(99) <= RATING_MAX` trên **cùng trường** — hai file, hai chiều ngược nhau |
| **L2-2** | `deploy_golive_dt5g_v4/golive_recommend_v23.py:667` | `… if (sig["time"]==LATEST).any() else int(prov.get("state", 3))` | Bảng tín hiệu BQ không có dòng nào ở `LATEST` ⇒ đọc `prov` (provenance gated-state); **thiếu khoá `state`** ⇒ **3 = NEUTRAL** (`SNAME` `:326`) | **TIỀN THẬT** — `state_today` lái `w_LAG`, `ETF_PARK`, `half_in_state` | **KHÔNG AN TOÀN** — NEUTRAL (70%) cao hơn CRISIS(0%)/BEAR(20%). Nhánh này chạy **đúng lúc pipeline đã hỏng**, mà lại đoán một regime ở giữa thay vì dừng | Thiếu `state` ⇒ raise. Không có cơ sở nào để đoán regime |
| **L2-3** | `trading_bot/executor.py:542` | `mins = float(self.cfg.get("probe_linger_min", 0) or 0)` | `cfg` = `CONFIG` (config.py) + overrides `accounts.json`. `CONFIG["probe_linger_min"] = 30` (`config.py:257`, chú thích *"0 = tắt. 30' > 2,0×dip_window_min ⇒ r15 luôn có mẫu hợp lệ"*). Mặc định shadow ở executor là **0 = TẮT** | **TIỀN THẬT** (đường đặt lệnh) | **AN TOÀN theo hướng** (tắt probe = ít đuổi giá hơn) **nhưng là lỗi cấu hình thật**: hai nguồn sự thật cho một con số, và chúng **KHÁC nhau**. Kiểm hết 10 knob shadow trong `executor.py` — **9/10 trùng** `CONFIG`, mình `probe_linger_min` lệch | Bỏ mặc định shadow: `self.cfg["probe_linger_min"]` (KeyError = lỗi cấu hình, phải thấy). Áp cho cả 10 (§22) |
| **L2-4** | `deploy_golive_dt5g_v4/golive_recommend_v23.py:318` | `STATE_LAG_WEIGHT.get(int(state), 0.5)` | State ngoài 1..5 ⇒ `w_LAG = 0.50` | TIỀN THẬT | **KHÔNG AN TOÀN nhẹ** — `:103` đã map đủ 1..5 nên chỉ nổ khi state rác; 0.5 = giá trị của CRISIS, khá bảo thủ | Thấp. Nếu sửa: raise trên state ngoài miền |

### 2.3 Đã đọc và KẾT LUẬN ỔN

| Vị trí | Vì sao ổn |
|---|---|
| `mike/bin/discretionary_candidate_funnel.py:325` `rating.fillna(99) <= RATING_MAX` | **fail-CLOSED** — khuôn đúng, đối chứng của L2-1 |
| `macro_state_live.py:197` `df["univ"].fillna(0) >= breadth_min_univ` | Thiếu universe ⇒ 0 ⇒ `decoup=False` ⇒ guard **không chặn** cap ⇒ cap ÁP nhiều hơn = bảo thủ. Đúng fail-safe CLAUDE.md §4 |
| `rating_8l.py:770` `ROE_Min5Y.fillna(-9) > 0.10` | Thiếu ⇒ không được cộng điểm thưởng. Bảo thủ |
| `rating_8l.py:771` `value_yield_pct.fillna(0.5)` | 0,5 = trung vị thang percentile ⇒ mã thiếu định giá nhận điểm value TRUNG BÌNH. Đáng biết (1/PE là trục trội, IC +0,125) nhưng **không** là fail-open theo nghĩa che lỗi file — cột này NaN là trạng thái dữ liệu bình thường, không phải hỏng |
| `pt_v22_dt5g.py:519/770/771/816/817` | Engine backtest: `pct_change().fillna(0)` hàng đầu tiên, `diff().dt.days.fillna(999)` — số học chuỗi thời gian, không phải mặc định cấu hình |
| `golive_recommend_v23.py:1087` `ETF_PARK.get(state_today, 0.0)` | `ETF_PARK = {3: 0.30}` — **cố ý** chỉ park ở NEUTRAL; 0,0 là giá trị đúng |
| `plan.py:1708` `float(out["lever_f"] or 1.0)` | Thiếu/0 ⇒ **1,0 = không đòn bẩy**. Bảo thủ |
| `compute_jit_unpark.py:495` `sum(...) or 1.0` | Chặn chia-cho-0 |
| **Lớp `out[k] = out.get(k, 0) + x`** (`capit_episode`, `daily_nav_snapshot:401`, `merge_park_orders:463/603/723`, `report_return_gate:237`, `dividend_adjusted_return:589`, `executor:1902`) | **Thành ngữ cộng dồn dict**, không phải mặc định che lỗi. False-positive có hệ thống của bộ dò |
| **Lớp f-string hiển thị** (`plan.py:131-133`, `compute_park_trim:826/845`, `compute_jit_unpark:653/657/665/666`, `daily_nav_snapshot:868/869`) | Chỉ định dạng đầu ra |
| 92 OR_DEFAULT, trong đó 71 mặc định là 0/0.0 | Ép kiểu `float(x or 0)` — không phải fail-open |

---

## 3. LỖ 3 — `plan.py:1390` và `plan.py:1787`

**Ranh giới cứng: chỉ MÔ TẢ. Không đề xuất patch, không sửa.** (Hai chỗ này khác `:648/:1651/:1756`
mà Mike đang sửa trong worktree.) Dòng verify trên master HEAD hôm nay.

### `plan.py:1390` — `apply_capit_lever`, đọc `golive_v23_status.json`

```python
except Exception as ex:
    err = f"không đọc được {path}: {type(ex).__name__}: {ex} — KHÔNG áp đòn bẩy"
```

**Kết luận: fail-CLOSED. AN TOÀN.** Đợt 1 để ngỏ "chưa kết luận" — nay đóng được.

Nếu lỗi im lặng xảy ra: `err` được đặt ⇒ 8 dòng dưới, `authorized = bool(not err and lever.get("active")
is True and …)` ⇒ `authorized` thành `False` ⇒ **không áp đòn bẩy**. Chiều sai = mua thiếu. Thông
điệp `err` mang **loại + nội dung exception thật** (không phải nguyên nhân đoán sẵn — đạt §29).
Cùng khối này còn 2 nhánh fail-closed cùng tinh thần: thiếu `signal_date` ở **bất kỳ** bên nào
(`:1386`) và lệch `signal_date` (`:1389`).

### `plan.py:1787` — `_lever_ledger_merge`, ghi sổ cấp phép gói vay

```python
except Exception as ex:
    print(f"⚠ KHÔNG ghi được sổ cấp phép đòn bẩy {path} ({type(ex).__name__}: {ex}) — …")
```

**Kết luận: fail-open NHƯNG KÊU TO, và hậu quả BẤT ĐỐI XỨNG.** Không phải "an toàn" trọn vẹn —
đây là chỗ user nên biết cả hai chiều:

- **Chiều đã được nói trong chính thông điệp (an toàn)**: mất bản ghi CẤP ⇒ lượt chạy sau trong
  cùng phiên không kế thừa được tập mã đã cấp ⇒ lưới an toàn tầng lệnh báo
  `LEVER_PACKAGE_UNAUTHORIZED` **NHẦM** cho lệnh hợp lệ. Sai về phía CHẶN.
- **Chiều KHÔNG được nói (không an toàn)**: ghi là `tmp` + `os.replace` (nguyên tử, §5 đúng).
  Ghi fail ⇒ file **giữ nguyên nội dung CŨ**. Docstring `:1775-1778` nói rõ *"File đã tồn tại thì
  vẫn ghi (để `_strip` thu hồi được về rỗng)"* — tức đường **THU HỒI** cấp phép đi qua **đúng câu
  lệnh ghi này**. Ghi fail trên đường thu hồi ⇒ sổ vẫn liệt kê một mã **đã bị gỡ quyền** như còn
  được cấp ⇒ lưới an toàn cho lệnh đòn bẩy đó đi qua. Hiện **không có gì phân biệt** hai chiều:
  cùng một `except`, cùng một câu cảnh báo, và câu đó chỉ mô tả chiều chặn-oan.
- Thông điệp có `type(ex).__name__: ex` ⇒ §29 đạt. Nhưng in ra **stdout của tiến trình lập plan** —
  không có event bus, không Telegram.

---

## 4. LỖ 4 — 5 handler quanh `place_order`/`cancel_order` trong `executor.py`

Audit theo đúng câu hỏi §5: *"bị kill/exception ngay sau khi external call thành công nhưng trước
`_save_state` — lần chạy kế làm gì?"* **CHỈ LIỆT KÊ — ranh giới cứng, đây là logic đặt lệnh.**

### 4.1 Hai lưới hiện có, che được tới đâu

**`_save_state()` ngay sau mỗi `place_order`** (`:1927`, có chú thích; và `:1994` trong ATC) — thu
hẹp cửa sổ "đã đặt mà state chưa biết" từ 1 chu kỳ đa mã xuống 1 lần ghi JSON nguyên tử. **Thu hẹp,
không đóng.**

**`_ghost_tickers(updates)` (`:1144`), gọi ở đầu MỖI `step()` (`:2034`)** — đối chiếu `poll_orders()`
với oid trong state; oid lạ mà `filled>0` hoặc còn sống ⇒ TẠM DỪNG mã, journal `GHOST_ORDER`,
bắn bus `GHOST_ORDER_DETECTED`, unpause thủ công. Đây mới là lưới thật.

**Điều kiện để lưới đó hoạt động — và là chỗ nó hở:** lệnh "ma" phải **hiện ra trong
`poll_orders()` của chu kỳ KẾ TIẾP**. Nếu sàn nhận lệnh nhưng sổ lệnh broker chưa phản ánh trong
một chu kỳ (`slice_interval_min = 8` phút mặc định), chu kỳ đó không thấy ghost và `_place_slices`
đặt lại phần "còn thiếu". Không có cơ chế nào chặn cửa sổ này — DNSE không có idempotency-key
(docstring `:1151-1152` tự nói).

### 4.2 Từng nhánh

| # | file:line | Handler | §5: kill/exception sau khi sàn nhận, trước `_save_state` ⇒ lần chạy kế? | `_ghost_tickers` che? | Chiều |
|---|---|---|---|---|---|
| **E-1** | `:855` | `_retry_tick_mismatch` — `except Exception: overrides.pop(...); return None` quanh `place_order` **sàn thay thế** | Lệnh alt-exchange được nhận rồi response lỗi ⇒ caller journal `PLACE_FAIL` + `continue`, state trống | **CÓ** (oid lạ ở step kế) | AN TOÀN về tiền. **Nhưng có lỗ CHẨN ĐOÁN**: `except` này **hoàn toàn câm** — không journal gì. Vận hành chỉ thấy `PLACE_FAIL` với lỗi GỐC, không hề biết đã thử sàn thay thế và nó hỏng thế nào (§29) |
| **E-2** | `:1893` | `_place_slices` — `except Exception as e:` quanh `place_order` chính | (a) kill sau `place_order` trước `:1927` `_save_state` ⇒ **CÓ** ghost che. (b) sàn NHẬN nhưng client raise (timeout/parse) ⇒ `PLACE_FAIL` + `continue` ⇒ **CÓ** ghost che ở step kế | **CÓ**, trừ cửa sổ trễ-hiển-thị ở §4.1 | AN TOÀN trong thiết kế hiện tại. Đây là nhánh đã được gia cố kỹ nhất |
| **E-3** | `:1959` | `_atc_sweep` — `except Exception: pass` quanh `cancel_order(c["oid"])` | **KHÔNG PHẢI ca §5 — nặng hơn.** Cancel fail ⇒ `c["status"]` vẫn `"open"` (đúng), **nhưng luồng chạy tiếp**: `remaining = o.qty - ps["filled"]` rồi `place_order(..., order_type="ATC")` cho TOÀN BỘ `remaining`. **Phần đang treo ở lệnh LO còn sống KHÔNG bị trừ.** LO + ATC cùng khớp ⇒ tổng **vượt `o.qty`** | **KHÔNG** — cả hai oid đều nằm trong state, không có oid "lạ" nào | **KHÔNG AN TOÀN.** Và **câm tuyệt đối**: `pass`, không journal, không đếm. Đối chứng ngay dưới: `cancel_all_open` (`:2008+`) với **cùng lệnh `cancel_order`** thì journal `CANCEL_FAIL` — chứng minh journal ở đây là khả thi. **`config.py:144 atc_remainder_sell = True` ⇒ nhánh này ĐANG BẬT chiều BÁN** (`atc_remainder_buy = False`, `:145`) |
| **E-4** | `:1995` / `:2008` | `_atc_sweep` — `except Exception as e: self._journal("ATC_FAIL", o, note=str(e))` quanh `place_order` ATC | Sàn nhận ATC nhưng client raise ⇒ `ps["atc_sent"]` **không** được đặt ⇒ `_atc_sweep` lượt sau gửi ATC lần nữa ⇒ **ATC trùng**. `_save_state()` nằm TRONG `try`, ngay sau `atc_sent = True` — thứ tự đúng | **CÓ trên lý thuyết**, nhưng **hở theo thời điểm**: ATC chạy 14:30-14:45; có thể **không còn `step()` nào** trước khi đóng cửa ⇒ ghost không bao giờ được quét trong ngày, chỉ lộ ra ở đối soát hôm sau | KHÔNG AN TOÀN nhẹ, phụ thuộc thời điểm. Journal `ATC_FAIL` có mang `str(e)` (§29 đạt) |
| **E-5** | `:2008+` | `cancel_all_open` — `except Exception as e:` | Journal `CANCEL_FAIL` kèm `str(e)`; riêng `"closed session"` đặt `c["await_atc"] = True` giữ `open` để `run_session` poll lại (aria-K, ZaloPay VHC 2026-07-10) | n/a | **AN TOÀN** — kêu to, không tự kết luận "xong". Không cần làm gì |

---

## 5. Nên sửa trước — xếp theo (ảnh hưởng × chiều × khả năng xảy ra âm thầm)

Gộp cả 4 lỗ. **Ba mục đầu KHÔNG chồng lấn** với batch-1 đã merge, cũng không chồng với
`plan.py:648/1651/1756` Mike đang sửa.

| Hạng | Mục | Vì sao đứng đây |
|---|---|---|
| **1** | **`executor.py:1959`** (E-3) — cancel fail ⇒ `pass` ⇒ ATC đặt chồng lên LO còn sống | Hạng mục duy nhất trong cả 2 đợt mà **không có lưới nào che** (`_ghost_tickers` không thấy vì cả 2 oid đều hợp lệ), chiều sai là **bán/mua VƯỢT kế hoạch**, và nó **câm tuyệt đối** nên không phát hiện được sau đó. `atc_remainder_sell=True` ⇒ đang bật thật. ⚠️ **Ranh giới cứng — chỉ liệt kê** |
| **2** | **`golive_recommend_v23.py:731`** (L2-1) — `rating8l.fillna(0) >= 4` | Sai theo hướng **size LỚN hơn** cho mã KHÔNG BIẾT chất lượng, và chỉ có hiệu lực trong **CRISIS/BEAR**. Đối chứng cùng repo (`discretionary_candidate_funnel.py:325` dùng `fillna(99)`) chứng minh fail-closed khả thi, đúng khuôn `check_sbv_weekly` ↔ `macro_healthcheck` ở đợt 1 |
| **3** | **`pt_8l_daily.sh:46`** (L1-1) — DT5G freshness checker chết ⇒ in **"DT5G tươi"** | Là **khẳng định sai chủ động**, không phải im lặng. Bảng xếp hạng 8L + alert Telegram tối đó chạy trên regime chưa xác nhận **trong khi vận hành được báo là đã xác nhận** |
| **4** | **`golive_recommend_v23.py:667`** (L2-2) — `prov.get("state", 3)` ⇒ đoán NEUTRAL | Đoán một regime giữa đúng lúc pipeline tín hiệu đã hỏng; NEUTRAL 70% > BEAR 20% |
| **5** | **`ops_health_check.sh:64`** (L1-2) — 3 check chạy-một-lần biến mất cho CẢ 2 account | Xoá khả năng phát hiện (anomaly + forensic + worktree-stale), lặp lại đúng ca mà comment ngay trên nó đã tả |
| 6 | `telegram_run_daily.sh:22` (L1-3) | Cảnh báo dữ liệu cũ biến khỏi tin gửi user |
| 7 | `executor.py:542` (L2-3) — `probe_linger_min` 0 ≠ CONFIG 30 | Lệch cấu hình thật, đã xác minh 9/10 knob còn lại trùng. Nên sửa cả 10 một lượt (§22) |
| 8 | `backup_freshness_check.sh:39` (L1-5) · `eod_trading_report.sh:179` (L1-4) · `append_event.sh:70` (L1-6) | Cùng lớp "mất khả năng phát hiện", ảnh hưởng nội bộ |
| — | `executor.py:855` (E-1, thêm journal cho tick-retry) · `worktree_cleanup_daily.sh:160` (L1-7) · `golive:318` (L2-4) | Thấp |

---

## 6. Trạng thái 4 lỗ của §2 REPORT.md sau đợt 2

| Lỗ §2 | Trạng thái | Còn gì |
|---|---|---|
| **§2.1** — 128 dòng L4 chưa đọc | ✅ **ĐÓNG** | 123 dòng (phân hoạch lại trên HEAD) đã đọc hết. 7 hit thật |
| **§2.2** — `.get`/`fillna`/`or` | 🟡 **ĐÓNG MỘT PHẦN** | Đã đọc ~106/396 theo tiêu chí §2.1 báo cáo này. **Còn hở**: 121 GET_DEFAULT tier A không truy được về file trong 1 hop (cấu hình qua hàm helper) · 179 dòng bị bộ lọc từ khoá loại · `try/except FileNotFoundError` · lớp `.get()` trên dict **API broker** |
| **§2.3** — tier gán theo FILE | 🟡 không đụng tới trong đợt 2 | Các hit ĐÃ ĐỌC ở cả 2 đợt có tier sửa tay; `hits_L1_L3_full.csv` vẫn chưa xác minh |
| **§2.4** — chỉ tier A đọc hết | 🟡 nhích | Đợt 2 đọc thêm tier B ở lớp `.get/fillna`. Tier C (200 hit L1-L3) **vẫn 0 dòng** |
| **§6** `plan.py:1390/1787` | ✅ **ĐÓNG** | `:1390` fail-CLOSED an toàn · `:1787` kêu to, hậu quả bất đối xứng (§3) |
| **§6** `executor.py` 5 handler | ✅ **ĐÓNG** | 4/5 có lưới (`_ghost_tickers`) hoặc kêu to; **`:1959` không có lưới nào** |

**Lỗ MỚI đợt 2 tự khai:** `.get()` trên dict trả về từ **API broker** (DNSE) chưa ai kiểm kê —
cùng lớp rủi ro với `.get()` trên file nhưng nằm ngoài phạm vi dispatch này.

---

## 7. Artifact đợt 2

| File | Nội dung |
|---|---|
| `hits_L4_rescan_HEAD.tsv` | 294 dòng L4 quét lại trên HEAD 10:05 — **dùng cái này, không dùng `hits_L4_full.tsv`** (drift, §0b) |
| `hits_L4_dot2_classified.tsv` | 123 dòng OTHER + nhãn lớp (A-SOURCEENV / C-CLEANUP / D-VAR / E-CONT / F-STMT) |
| `hits_L5b_getdefault.json` | 396 hit thô GET_DEFAULT / FILLNA / OR_DEFAULT trên tier A+B |
| `repro_scan_L5b.py` | Script AST tái lập LỖ 2: `$DNA_PYEXE repro_scan_L5b.py out.json` (chạy từ `WorkingClaude`) |

Không file nào ngoài thư mục này bị sửa (ngoài mục §2 của `REPORT.md`, đúng yêu cầu dispatch).
