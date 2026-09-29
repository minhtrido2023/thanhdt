# Kiểm kê fail-open toàn cục — 2026-09-28

**Job**: `Taylor_20260928_005930` · **Phạm vi**: `WorkingClaude` (trừ `wt-*`, `.claude/worktrees`,
`archive/`, `*/research/`) + `WorkingClaude/mike/bin` · **Chỉ code ĐANG DÙNG** (đường live, đường
sinh số PIN, cron đang chạy).

> **CHỈ LIỆT KÊ — KHÔNG SỬA FILE NÀO NGOÀI THƯ MỤC NÀY.** Không merge, không dispatch tiếp.

---

## 0. Kết quả một dòng

Con số "~12 call-site" **KHÔNG tái lập được** — quét lại có phương pháp cho **867 hit thô** trên
**228 file `.py` + 88 file `.sh` đang chạy**. Nhưng **phần lớn không phải lỗi**: đọc từng dòng
tier A cho thấy đa số là **fail-CLOSED có chủ đích + có docstring giải thích** (đã sửa từ các sự cố
trước). Số call-site **thật sự fail-open theo chiều KHÔNG an toàn** trên đường tiền/đường số pin,
sau khi đọc code, là **9** (chi tiết §4, TOP 5 ở §5).

Vì vậy: **đừng dùng lại con số 12, cũng đừng dùng con số 867 như "867 bug".** Con số đáng hành động
là 9.

---

## 1. Phương pháp quét (tái lập được)

Mọi script nằm cùng thư mục này. Chạy từ `WorkingClaude`:

```bash
# B1 — seed đường LIVE: mọi path .sh/.py xuất hiện trong crontab + package trading_bot
crontab -l | grep -oE '/home/trido/thanhdt/WorkingClaude[^ >|;]*\.(sh|py)' | sort -u  > /tmp/seed.txt
crontab -l | grep -oE 'python3? +[A-Za-z0-9_/.-]+\.py' | awk '{print $2}'            >> /tmp/seed.txt
ls trading_bot/*.py                                                                  >> /tmp/seed.txt

# B2 — nở transitive 4 hop (import nội bộ + tham chiếu .py/.sh trong chuỗi shell),
#      loại wt-*/ .claude/worktrees/ archive/ */research/ __pycache__/
python3 repro_expand_liveset.py       # -> scope_live_py.txt (228)  scope_live_sh.txt (88)

# B3 — L1/L2/L3 bằng AST (KHÔNG regex: `except Exception:` vs `except ValueError:` và
#      `return None` vs `return x` chỉ phân biệt được ở tầng cú pháp)
$DNA_PYEXE repro_scan_ast.py scope_live_py.txt /tmp/ast_hits.json
$DNA_PYEXE repro_tier.py A            # gán tier ảnh hưởng + dump context

# B4 — L4 (shell)
while read -r f; do grep -nE '2>/dev/null' "$f" | grep -E '\|\| *(true|:|rc=|echo)'; done < scope_live_sh.txt

# B5 — L5 bằng AST: `if not os.path.exists(p): <return/assign giá trị>` mà nhánh đó
#      KHÔNG raise/print/log/exit  (script inline trong §3.5)
```

Định nghĩa dùng trong B3 (để ai đọc lại biết tại sao 1 dòng bị/không bị tính):
- **broad** = `except:` trần, `except Exception`, `except BaseException` (kể cả trong tuple).
  `except ValueError:`, `except OSError:`, `except json.JSONDecodeError:` **KHÔNG** tính — đó là
  bắt lỗi có chủ đích, không phải fail-open.
- **L1** = handler chỉ có `pass` / `continue` / docstring.
- **L2** = handler không `raise`, không `exit`, và (gán giá trị rỗng `{} [] 0 None ""` **hoặc**
  chỉ print/log rồi đi tiếp **hoặc** rơi thẳng qua).
- **L3** = handler `return` giá trị rỗng (`None` / `{}` / `[]` / `0` / `""` / `False`).
  Một handler có thể vào 2 lớp (vd vừa gán rỗng vừa return) — vì vậy Σ lớp > số handler.

### Tier ảnh hưởng (gán theo FILE, `repro_tier.py`)
| Tier | Nghĩa | File |
|---|---|---|
| **A** | tiền thật / đường đặt lệnh / NAV công bố | `trading_bot/*` (executor, plan, brokers, funding_gate, cash_commitment, due_diligence, strategies), `bot_execute.py`, `mike/bin/{daily_nav_snapshot,verify_account_snapshot,compute_active_nav,compute_jit_unpark,compute_park_trim,merge_park_orders,reconcile_equity,nav_period_returns,report_return_gate,dividend_adjusted_return,discretionary_*}.py` |
| **B** | số được PIN / input model / regime | `rating_8l*.py`, `macro_state_live.py`, `macro_healthcheck.py`, `dna_report.py`, `dna_card.py`, `lag_forensic_filter.py`, `pt_v2*.py`, `rank_8l*.py`, `unified_screener.py`, `dcf_*.py`, `golive_recommend_v23.py`, `publish_gated_state.py`, `dc_book_waterfall_paper.py`, `edge_health_monitor.py`, `sector_lens_monitor.py`, `capit_episode.py`, … |
| **C** | chỉ nội bộ (bus, dispatch, log, Discord, spend, retro) | `mike_json.py`, `discover_sessions.py`, `resume_pending.py`, `bus_question_audit.py`, `spend_report*.py`, … |
| **S** | selfcheck / test | `*selfcheck*.py` |

---

## 2. ⚠️ Nói thẳng: những gì lần quét này KHÔNG phủ (§29)

> **CẬP NHẬT 2026-09-28 10:15 — ĐỢT 2 đã đóng lỗ 1 và một phần lỗ 2.**
> Xem **`REPORT_DOT2.md`** (job `Taylor_20260928_030132`). Tóm tắt trạng thái:
> **§2.1 ✅ ĐÓNG** (123 dòng đã đọc hết → 7 hit thật mới) ·
> **§2.2 🟡 ĐÓNG MỘT PHẦN** (~106/396 dòng đã đọc → 4 hit thật; còn hở: cấu hình qua HÀM HELPER
> >1 hop, 179 dòng bị bộ lọc từ khoá loại, `try/except FileNotFoundError`, `.get()` trên dict
> API broker) · **§2.3 🟡 không đụng** · **§2.4 🟡 nhích** (thêm tier B lớp `.get/fillna`;
> tier C vẫn 0 dòng).
> **§6 cũng đã đóng 2 mục treo**: `plan.py:1390` fail-CLOSED an toàn · `plan.py:1787` kêu to
> nhưng hậu quả BẤT ĐỐI XỨNG · `executor.py` 4/5 handler có lưới `_ghost_tickers`,
> **`:1959` KHÔNG có lưới nào** (cancel fail ⇒ ATC đặt chồng lên LO còn sống).
>
> ⚠️ **SỐ DÒNG TRONG BÁO CÁO NÀY ĐÃ DRIFT.** Bảng `hits_L4_full.tsv` sinh 08:10; batch-1 merge
> 08:58 (`mike` @ `afc1e6b5`). Ví dụ `check_sbv_weekly.sh:32/38` ở §4a (#7/#8) **không còn tồn
> tại** — đã fail-CLOSED, dòng tương ứng giờ ở `:38-45`. Dùng `hits_L4_rescan_HEAD.tsv` (294 dòng,
> quét lại 10:05) cho mọi tham chiếu `file:line` L4.


**Không được tuyên bố "đã quét hết".** Bốn lỗ đã biết:

1. **L4 trong bash không phân biệt được cơ học "vô hại" với "nguy hiểm".** 295 dòng khớp mẫu;
   tôi tách bằng heuristic (`notify|append_event|discord` = vô hại, 114 dòng) rồi **đọc tay 53 dòng
   dạng `|| echo <giá-trị>`**. 128 dòng còn lại (`|| true` trên lệnh KHÔNG phải notify) **chưa đọc
   từng dòng** — có thể còn hit thật trong đó.
2. **L5 chỉ bắt mẫu `os.path.exists`/`isfile`/`Path.exists`.** KHÔNG bắt:
   `dict.get(key, <default>)` trên file config, `df.fillna(<hằng số>)`, `or <default>` trên giá trị
   đọc từ file, `try: open(...) except FileNotFoundError: <default>`. Đây là lỗ **lớn nhất** —
   `.get(k, default)` là mẫu phổ biến nhất của "giá trị mặc định im lặng" mà tôi không có cách
   phân biệt cơ học với `.get()` hợp lệ.
3. **Tier gán theo FILE, không theo hàm.** Một hàm chỉ-hiển-thị nằm trong file tier A vẫn được
   tính tier A (và ngược lại). Cột đánh giá ở §4 tôi sửa tay cho những hit đã ĐỌC; **các hit
   chưa đọc trong `hits_L1_L3_full.csv` giữ tier theo file — đừng coi tier đó là kết luận.**
4. **Chỉ có tier A (110 hit) được đọc HẾT từng dòng.** Tier B đọc **~35/164** (chọn theo tên hàm
   dính số pin/regime/NAV). Tier C (200) **không đọc dòng nào** — chỉ đếm.

Hệ quả thực dụng: **§4 là danh sách đã xác minh; `hits_L1_L3_full.csv` là danh sách CHƯA xác minh.**

---

## 3. Số lượng theo lớp

### 3.1–3.3 L1/L2/L3 (AST, 228 file `.py` live, 0 file không parse được)

| Lớp | Tổng | A (tiền thật) | B (số pin) | C (nội bộ) | S (selfcheck) |
|---|---:|---:|---:|---:|---:|
| **L1** `except: pass\|continue` | **143** | 21 | 34 | 75 | 13 |
| **L2** báo-rồi-đi-tiếp / gán rỗng | **236** | 59 | 100 | 69 | 8 |
| **L3** `return None/{}/[]/0` | **119** | 30 | 30 | 56 | 3 |
| **Σ hit** | **498** | 110 | 164 | 200 | 24 |

Top file (đếm thô, **không** = xếp hạng rủi ro): `mike_json.py` 44 (C) · `executor.py` 30 (A) ·
`job_cancel_guard_selfcheck.py` 21 (S) · `due_diligence.py` 17 (A) · `brokers.py` 16 (A) ·
`dna_report.py` 15 (B) · `macro_healthcheck.py` 14 (B) · `unified_screener.py` 12 (B) ·
`golive_recommend_v23.py` 11 (B) · `plan.py` 10 (A).

### 3.4 L4 — shell (88 file `.sh` live)

| Phân lớp | Số dòng | Trạng thái |
|---|---:|---|
| Tổng dòng khớp `2>/dev/null` + triệt tiêu rc | **295** | — |
| `\|\| true` trên `notify*.sh`/`append_event.sh`/discord | 114 | **vô hại** (kênh thông báo hỏng không được làm sập pipeline) — không đề xuất sửa |
| `\|\| echo <giá-trị mặc định>` | **53** | đã đọc tay từng dòng → 4 hit thật (§4) |
| `\|\| true` trên lệnh KHÁC notify | 128 | **CHƯA đọc từng dòng** (xem §2.1) |

### 3.5 L5 — giá trị mặc định im lặng khi THIẾU FILE

**74 site** khớp mẫu trên 228 file live. Đọc tay 12 site nằm trên đường tiền/đường số pin →
**3 hit thật** (§4). Phần lớn 74 site là **lành**: chúng trả kèm CHUỖI LỖI cho caller
(`return None, f'không có {path}'`) hoặc `return out` với `out['reason']` đã set — tức có kênh báo,
không im lặng.

---

## 4. Bảng hit ĐÃ XÁC MINH (đọc từng dòng)

Cột `an toàn?`: **AN TOÀN** = lỗi đẩy về phía mua thiếu / chặn oan · **KHÔNG AN TOÀN** = mua nhầm /
sizing vượt / công bố số sai.

### 4a. Fail-open thật, chiều KHÔNG AN TOÀN — 9 call-site

| # | file:line | lớp | Dữ liệu bị bỏ im lặng | Ảnh hưởng | Chiều | Đề xuất | Ranh giới cứng? |
|---|---|---|---|---|---|---|---|
| 1 | `deploy_golive_dt5g_v4/golive_recommend_v23.py:441` | L1 | `data/execution_logs/active_nav_<label>.json` không đọc được (thiếu/stale/JSON hỏng) → `except: pass`, **không log gì** | **TIỀN THẬT** — đây là NAV basis sinh slot target CAPIT/LAG | **KHÔNG AN TOÀN**: rơi xuống fallback `nav_history` = **TỔNG NAV chưa trừ `excluded_tickers`** (≥ active_nav) ⇒ sizing LỚN hơn vốn triển khai thật | **FAIL-CLOSED** (hoặc tối thiểu: log to + ghi `nav_basis_degraded` vào `golive_v23_status.json` để `plan.py` thấy) | Không (nhưng output feed thẳng vào `plan.py`) |
| 2 | `deploy_golive_dt5g_v4/golive_recommend_v23.py:448` | L1 | `nav_history_<label>.csv` cũng không đọc được → `except: pass` → `return None` | **TIỀN THẬT** | KHÔNG AN TOÀN theo nghĩa khác: 2 lần `pass` liên tiếp ⇒ **không phân biệt được** "thiếu file" / "JSON hỏng" / "NAV ≤ 0" khi đi chẩn đoán (§29) | giữ fail-open nhưng **LOG to** (2 lý do riêng biệt) | Không |
| 3 | `trading_bot/plan.py:648` | L2 | `asof`/`data_date` không parse được ISO → `lag_days = None` | **TIỀN THẬT** — gate LAG %ADV | **KHÔNG AN TOÀN**: điều kiện kế tiếp là `if lag_days is not None and lag_days > MAX` ⇒ `None` **BỎ QUA HẲN** gate ADV-stale ⇒ size lệnh theo ADV cũ của mã có thể đã ngừng GD/huỷ niêm yết | **FAIL-CLOSED** (`lag_days=None` ⇒ `_block("không xác định được độ cũ ADV")`) | Có — trong `plan.py` ⇒ **chỉ liệt kê** |
| 4 | `mike/bin/compute_jit_unpark.py:241` | L2 | y hệt #3 | **TIỀN THẬT** — L2 JIT-unpark | KHÔNG AN TOÀN (gate ADV-stale bị bỏ qua) | FAIL-CLOSED | Không |
| 5 | `mike/bin/compute_park_trim.py:703` | L2 | y hệt #3 | **TIỀN THẬT** — L1 park-trim | KHÔNG AN TOÀN (gate ADV-stale bị bỏ qua) | FAIL-CLOSED | Không |
| 6 | `mike/bin/account_cash_flows.py:78` | L5 | `account_cash_flows.json` thiếu → `return []`, **không log** | **BÁO CÁO NHÀ ĐẦU TƯ** — `nav_period_returns.py` (§31) trừ nạp/rút khỏi tỉ suất | **KHÔNG AN TOÀN**: nạp tiền thật bị coi như lãi ⇒ WTD/MTD/"từ khi bắt đầu" **cao hơn thật** và gate §21/`report_delivery_gate` không biết | **FAIL-CLOSED** cho đường báo cáo (thiếu file ⇒ raise/`UNVERIFIED`); giữ `[]` chỉ cho đường không công bố | Không |
| 7 | `mike/bin/check_sbv_weekly.sh:32` | L4 | `from sbv_macro_overlay import SBV_REFI_EVENTS` fail → `\|\| echo "4.5"` — **lãi suất refi SBV hardcode** | **SỐ ĐƯỢC PIN** — trụ tiền tệ của macro gate DT5G | **KHÔNG AN TOÀN**: so lãi suất fetch được với **4.5 cứng** thay vì giá trị đang dùng thật ⇒ nếu overlay đổi/hỏng, thay đổi lãi suất **không sinh alert**, `SBV_REFI_EVENTS` không được cập nhật, DT5G chạy bằng regime tiền tệ cũ | **FAIL-CLOSED** (import fail ⇒ exit ≠0 + alert, KHÔNG đoán giá trị) — §29 | Không (nhưng là cron) |
| 8 | `mike/bin/check_sbv_weekly.sh:38` | L4 | y hệt #7 với `CURRENT_DATE` → `\|\| echo "2023-06-19"` | SỐ ĐƯỢC PIN | KHÔNG AN TOÀN (ngày event bịa ⇒ `sbv_age` sai ⇒ nhánh reminder sai) | FAIL-CLOSED | Không |
| 9 | `mike/bin/bot_heartbeat.sh:124` | L4 | `plan_<acct>_<date>.json` hỏng JSON → `N_ORDERS=0` → `exit 0` **im lặng cả ngày** | **TIỀN THẬT (gián tiếp)** — heartbeat là kênh duy nhất báo bot sống/khớp lệnh mỗi 5' | **KHÔNG AN TOÀN**: bot có thể đang chạy & khớp lệnh mà **không nhịp nào** tới Discord; đúng cái user cấm ("im lặng hoàn toàn = không phân biệt được với pipeline chết") | **FAIL-CLOSED**: phân biệt "plan 0 lệnh" (im lặng đúng) với "không parse được plan" (phải báo) | Không (nhưng là cron) |

### 4b. Fail-open CÓ CHỦ ĐÍCH + đã báo to — KHÔNG SỬA, nhưng cần xác nhận alarm tới người

| file:line | lớp | Dữ liệu | Ảnh hưởng | Chiều | Ghi chú |
|---|---|---|---|---|---|
| `lag_forensic_filter.py:153` | L2 | `data/forensic_flags.csv` không đọc được → cờ forensic KHÔNG áp (BANNED vẫn áp) | TIỀN THẬT | KHÔNG AN TOÀN **về bản chất**, nhưng có 3 kênh báo: `print WARNING`, `lag_forensic_filter_error` trong `golive_v23_status.json`, và dòng ⚠️ trong report (`golive_recommend_v23.py:1305`) | **KHÔNG SỬA** — đây chính là lớp mà `pt_v23_audit_2014.py:1082` vừa được sửa THÀNH. Việc cần làm là **verify 1 lần rằng dòng ⚠️ thật sự tới user** trong plan 21:00, không phải đổi code |
| `trading_bot/plan.py:834` | L2 | nguồn 8L rating hỏng toàn bộ → giữ nguyên lệnh LAG | TIỀN THẬT | KHÔNG AN TOÀN; nhưng trả bản ghi `action="FAIL_OPEN"` + "CẦN NGƯỜI KIỂM TRA" | **CHỈ LIỆT KÊ** — `plan.py`, ranh giới cứng. Gate `rating≤3` là gate user CHỐT CỨNG 2026-07-27 ⇒ nếu quyết định siết, đây là chỗ user tự chọn |
| `trading_bot/plan.py:920` | L2 | gate quản trị LAG (BANNED/user-exclude/forensic) không chạy được | TIỀN THẬT | như trên, `action="FAIL_OPEN"` | **CHỈ LIỆT KÊ** — `plan.py` |
| `macro_state_live.py:199` | L2 | BQ breadth (`universe_pit`) hỏng → breadth guard inactive | SỐ ĐƯỢC PIN | **AN TOÀN**: guard tắt ⇒ trụ Mỹ KHÔNG bị bypass ⇒ cap ÁP nhiều hơn = bảo thủ hơn. Đúng fail-safe CLAUDE.md | giữ fail-open; chỉ `print` (cron log) — **nâng lên bus/Telegram** thì tốt, không bắt buộc |
| `trading_bot/due_diligence.py:768, 987, 994, 1014` | L2/L3 | insider net-sell, yield_floor, recent_iss, DCF lens | chỉ nội bộ (DISPLAY_ONLY từ 2026-08-18/08-21, **không** sinh cờ đỏ, **không** đụng `has_red_flag`) | AN TOÀN | **KHÔNG SỬA** — đã `_log.warning` đủ |
| `sector_lens_monitor.py:434,437` → `dc_book_waterfall_paper.py:404` | L5/L3 | `rating_8l.csv` thiếu → `{}` ⇒ cross-check hiện `R?` | SỐ ĐƯỢC PIN (paper DC-book) | KHÔNG AN TOÀN nhẹ: `load_double_confirm` lọc theo rating, ratings rỗng ⇒ tầng lọc rating **biến mất im lặng** | giữ fail-open nhưng **LOG to** ở `load_double_confirm` |
| `capit_episode.py:54` | L5 | ledger episode thiếu → `{"episodes": []}` | SỐ ĐƯỢC PIN | KHÔNG AN TOÀN nhẹ: episode đang mở thành vô hình ⇒ có thể vào lại CAPIT | giữ fail-open nhưng LOG to (phân biệt "chưa từng có" với "đọc không được") |

### 4c. Đã kiểm tra và KẾT LUẬN ỔN — fail-CLOSED đúng, không cần làm gì

Ghi lại để lần sau không phải đọc lại (đây là phần lớn 110 hit tier A):

| file:line | Vì sao ổn |
|---|---|
| `plan_funding_gate.py:422` | `except: cash = 0.0` ⇒ `bound` NHỎ hơn ⇒ dễ **BLOCK** hơn = bảo thủ |
| `plan_funding_gate.py:349` | `bp=None` ⇒ nhóm vào `unmeasured` ⇒ đi nhánh cận ngoài đã thiết kế, có ghi `error` vào rec |
| `plan_cash_commitment.py:261` | `cash=None` ⇒ `basis="unknown"` + "fail-safe KHÔNG chèn" |
| `brokers.py:666,684,1214,1225` | `get_buying_power`/`get_max_buy_qty` → `None`, docstring ghi rõ "KHÔNG suy ra từ get_cash()", caller tự fail-safe |
| `plan.py:493` (`cap_capit_orders`) | `err` set ⇒ **mọi** lệnh CAPIT không có cap bị `BLOCKED`. Fail-CLOSED đúng |
| `daily_nav_snapshot.py:608` (`broker_positions`) | in stderr + `return None` ⇒ `main()` `return 2`, "KHÔNG tính NAV (tránh đăng số thiếu vị thế)" |
| `macro_state_live.py:312` | health không đọc được ⇒ `DT4_only`. Đúng `get_gated_state` fail-CLOSED |
| `macro_state_live.py:336` | freshness check fail ⇒ `stale=True` ⇒ fail-CLOSED DT4 **+ `_alert()`** |
| `macro_state_live.py:320` | `live_lag=0` ⇒ RƠI VÀO nhánh kiểm freshness (bảo thủ), không thoát |
| `macro_healthcheck.py:200` | import `SBV_REFI_EVENTS` fail ⇒ `add_check("sbv_import", False, "SEV1")` ⇒ health FAILED ⇒ DT5G tự tắt. **Tương phản rõ với #7** — cùng dữ liệu, một bên fail-closed, một bên hardcode 4.5 |
| `publish_gated_state.py:88,97` | `publish_ok=False` ⇒ in `!!! PUBLISH ABORT/FAILED` ⇒ `sys.exit(1)` (dòng 121-123); CSV mirror **không** được chạy trước BQ |
| `report_return_gate.py:367` | `excluded_tickers` rỗng ⇒ gate kiểm **THÊM** mã ⇒ nghiêm hơn = an toàn; có in stderr |
| `executor.py:1690` `_floor_guard_buy` | fail-safe `False` có docstring: 1 quote lỗi chỉ trễ slice mua 1 chu kỳ; và gated bởi `extreme_regime_enabled` (paper `main` only, LIVE byte-identical) |
| `executor.py:1703` `_extreme_armed` | `False` = "coi như bình thường", docstring ghi rõ; cùng cổng paper-only |
| `marginability_check.py:64` | `{}` = cache miss ⇒ **probe lại DNSE**; có tri-state `UNKNOWN`, không bịa `YES` |
| `account_cash_flows.py` (schema) | bản ghi sai schema ⇒ `raise CashFlowError` (chỉ **thiếu file** mới im lặng → đó là #6) |

---

## 5. TOP 5 nên sửa trước

Xếp theo (ảnh hưởng × chiều không an toàn × khả năng xảy ra âm thầm).

1. **`golive_recommend_v23.py:441` — NAV basis rơi ngầm sang TỔNG NAV.** Hai `except: pass` liền
   nhau, **không một dòng log**, trên chính con số sinh slot target tiền thật; fallback được code
   tự ghi là "chưa trừ excluded" ⇒ luôn sizing LỚN hơn. `compute_active_nav_all.sh` chạy 20:15 còn
   golive chạy trong chuỗi 19:00 ⇒ điều kiện `0 <= age <= ACTIVE_NAV_MAX_AGE_D` là thứ duy nhất
   đứng giữa, và nó **fail im lặng**.
2. **Lớp `lag_days = None` (3 call-site: `plan.py:648`, `compute_jit_unpark.py:241`,
   `compute_park_trim.py:703`).** Cùng một dòng code copy 3 chỗ, cùng một hệ quả: `None` làm
   **câu lệnh gate kế tiếp không bao giờ chạy** ⇒ gate ADV-stale (chống mã ngừng GD/huỷ niêm yết)
   biến mất. Đúng lớp "§22 luật văn xuôi áp sai → chuyển thành code": sửa 1 chỗ không đủ.
   ⚠️ `plan.py:648` là **ranh giới cứng** — chỉ user quyết.
3. **`check_sbv_weekly.sh:32/38` — hardcode `4.5` / `2023-06-19`.** Chính xác mẫu §29 ("vứt bằng
   chứng rồi đoán"). Cả cron tuần này tồn tại để PHÁT HIỆN lãi suất SBV đổi; khi import hỏng nó
   so với hằng số bịa và báo "unchanged". `macro_healthcheck.py:200` đọc **cùng** nguồn và
   fail-closed SEV1 — bằng chứng rằng fail-closed ở đây là khả thi, không phải đánh đổi.
4. **`account_cash_flows.py:78` — thiếu file ⇒ `[]` im lặng.** Nạp/rút không được trừ ⇒ tỉ suất
   WTD/MTD/từ-đầu **cao hơn thật** trong báo cáo gửi nhà đầu tư, mà §21/§31/`report_delivery_gate`
   đều không có cách biết. Sai theo hướng có lợi cho mình = hướng tệ nhất để sai.
5. **`bot_heartbeat.sh:124` — plan JSON hỏng ⇒ im lặng cả phiên.** Không mất tiền trực tiếp, vào
   TOP 5 vì nó **xoá mất khả năng phát hiện** mọi sự cố khác trong giờ giao dịch, và vi phạm trực
   tiếp quy ước user đã chốt (quiet-heartbeat: im lặng hoàn toàn ≠ phân biệt được với chết).

---

## 6. Ranh giới cứng — CHỈ LIỆT KÊ, không đề xuất patch

Không đề xuất sửa; chỉ mô tả hậu quả nếu lỗi im lặng xảy ra, để user tự quyết.

| Vị trí | Nếu lỗi im lặng xảy ra thì sao |
|---|---|
| `trading_bot/plan.py:1651` (L1, `apply_capit_lever`) | `capit_slot_targets` không đọc lại được ⇒ nhánh kiểm chéo target-levered **không chạy**; plan vẫn giữ lệnh CAPIT đã áp đòn mà không có bước đối chiếu trần slot |
| `trading_bot/plan.py:1756` (L1, `_lever_ledger_merge`) | ledger gói vay đã cấp không merge được ⇒ tập `granted` **thiếu** ⇒ một mã đã được cấp gói vay có thể bị coi như chưa, hoặc ledger ghi lại thiếu ⇒ audit `LEVER_PACKAGE_UNAUTHORIZED` mất dấu |
| `trading_bot/plan.py:648` (L2, `cap_lag_orders`) | xem #3 §4a: gate ADV-stale bị bỏ qua ⇒ sizing theo ADV của mã có thể đã ngừng giao dịch |
| `trading_bot/plan.py:834 / 920` | gate rating 8L≤3 / gate quản trị BANNED-forensic **fail-open có báo động**: lệnh LAG đi qua nguyên vẹn, kèm bản ghi `FAIL_OPEN` "CẦN NGƯỜI KIỂM TRA". Nếu không ai đọc bản ghi đó ⇒ mua mã rating≥4 hoặc mã BANNED |
| `trading_bot/plan.py:493 / 1390 / 1787` | cap CAPIT %ADV + áp đòn + ghi ledger. `:493` đã fail-CLOSED (BLOCKED). `:1390`/`:1787` chưa đọc hết — **chưa kết luận** |
| `trading_bot/executor.py:855, 1893, 1959, 1995, 2008` | mọi handler quanh `place_order`/`cancel_order`. Rủi ro **không phải** fail-open gate mà là **§5 idempotency**: lỗi xảy ra SAU khi sàn nhận lệnh nhưng TRƯỚC khi ghi state ⇒ lần chạy kế đặt lại. Có `_ghost_tickers` + `_save_state` nguyên tử che phần lớn; **chưa audit từng nhánh** trong job này |
| **crontab** | `check_sbv_weekly.sh` (#7/#8) và `bot_heartbeat.sh` (#9) là dòng crontab đang chạy — sửa file thì lịch không đổi, nhưng thay đổi hành vi (fail-closed ⇒ exit≠0) sẽ làm log cron có rc mới. Cần user biết trước |

---

## 7. Lớp "selfcheck hardcode gốc canonical" — 1 dòng theo yêu cầu

Không tìm thêm file mới thuộc lớp này trong lần quét này. 24 hit tier S đều là broad-except trong
chính selfcheck (`job_cancel_guard_selfcheck.py` 21/24), không phải hardcode đường dẫn canonical.

---

## 8. Artifact

| File | Nội dung |
|---|---|
| `hits_L1_L3_full.csv` | **toàn bộ 498 hit** — `file,line,lop,tier,func,except_type,hanh_vi_handler,try_body`. Tier theo FILE, **chưa xác minh** (xem §2.3) |
| `hits_L4_full.tsv` | toàn bộ 295 dòng L4 (gồm 114 notify vô hại + 128 chưa đọc) |
| `scope_live_py.txt` / `scope_live_sh.txt` | tập file live đã dùng (228 / 88) |
| `repro_expand_liveset.py` / `repro_scan_ast.py` / `repro_tier.py` | script tái lập B2/B3 |

Không file nào ngoài thư mục này bị sửa.
