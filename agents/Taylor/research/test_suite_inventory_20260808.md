# Kiểm kê & quản trị bộ test — 2026-08-08

- **Job**: `Taylor_20260808_035850` · **Owner**: Taylor · **Phần**: B (research + đề xuất)
- **Phần A** (fix bug test ghi bus production) đã xong riêng: commit WorkingClaude `f172282`,
  mike `8e7333a2` — xem finding `fix-test-bus-pollution-guard-MIKE_BOT_TEST_MODE`.
- **Đã CHẠY THẬT** toàn bộ 51 selfcheck ở repo root (không chỉ đọc code) — bảng §2 là kết quả đo,
  không phải suy đoán.

---

## 1. Kiểm kê — bức tranh tổng thể

| Nhóm | Số file | Thực chất là gì | Ai chạy |
|---|---:|---|---|
| `*selfcheck*.py` ở **repo root** | **51** | **Bộ regression THẬT** của money-path (executor, plan, gate, broker) | Agent trước khi commit |
| `mike/bin/*selfcheck*.py` | 19 | Regression cho hạ tầng fleet (bus, cron, NAV, park/JIT) | Agent fleet-ops |
| `mike/agents/*/…selfcheck*.py` | 18 | Selfcheck **cục bộ theo job R&D** (bằng chứng 1 lần, không phải suite) | Không ai — inert |
| `trading_bot/` | **0** | Không có test nào nằm cạnh code production | — |
| **root `test_*.py` / `*_test.py`** | **165** | ⚠️ **KHÔNG PHẢI TEST** — là script **backtest/R&D** (`test_kelly_q3_v2.py`, `test_v3_1_full.py`, `value_sleeve_test.py`…). Đặt tên `test_` là do lịch sử, chạy tốn hàng phút–giờ và gọi BQ | Không ai — artifact nghiên cứu |
| `stockquery/…/build/lib/**` | 63 | Rác build của package vendor, **lồng 7 tầng** `build/lib/build/lib/…`, 24MB, **0 file được git theo dõi** | Không ai |

**Phát hiện #1 — cũng là câu trả lời trực tiếp cho lo ngại của user.**
Cảm giác "có rất nhiều test case" phần lớn đến từ **165 file `test_*.py` không phải test**. Bộ
regression thật chỉ **51 file** ở root (+19 fleet-ops). 154/165 file `test_*.py` không được đụng
tới kể từ 2026-06-21 (ngày import repo). Đây là **rác không gian tên**, không phải nợ kỹ thuật của
bộ test: chúng là bằng chứng nghiên cứu (coding_guidelines §10 mục 4 **cấm** archive loại này).
Vấn đề là **cái tên**, không phải sự tồn tại — `grep test_` hay "chạy bộ test" đều vấp phải chúng.

---

## 2. Runnability — đo thật, 51/51 selfcheck root

`MIKE_BOT_TEST_MODE=1`, `timeout 150s`, tuần tự, `$DNA_PYEXE`.

| Kết quả | Số | Files |
|---|---:|---|
| ✅ PASS (rc=0) | **39** | (danh sách đầy đủ ở §2.3) |
| ❌ FAIL (rc=1) | **9** | anomaly_gate, capit_lever, cash_only_loan_package, dcf_selector, freshness_ops, sync_cache_lock, universe_pit_p2, universe_pit_p4 |
| ⏱ TIMEOUT >150s | **3** | eyrisk_selector, v4final_selector, immutable_publish (đều query BQ) |

### 2.1 Phát hiện #2 — 9/51 selfcheck đang ĐỎ, và 6 trong số đó ĐỎ *theo thiết kế*

Phân loại nguyên nhân (đã đọc log + code từng ca, không đoán):

**(i) Assertion neo vào TRẠNG THÁI SỐNG có thể thay đổi — 6 ca.** Đây là lớp lỗi chính:

| File | Assertion hỏng | Vì sao |
|---|---|---|
| `anomaly_gate_selfcheck.py` | A4 rổ due-diligence phải loại PNJ | Cờ `anomaly_flags.json` của PNJ **TTL 30 ngày**, sắp/đã hết hạn (~08-23) → PNJ quay lại rổ. Test chép cứng danh sách 5 mã. |
| `cash_only_loan_package_selfcheck.py` | engine trả `cash_only=True` | Đọc file production THẬT `data/trade_plans/discretionary/state_TV1_SpaceX.json`; sleeve TV1 nay `decision=inactive` → không sinh order để assert. **KHÔNG phải regression từ fix loan-package tối 08-07** (3 assert của chính cơ chế đó đều OK). |
| `universe_pit_p2_selfcheck.py` | rổ ngày 2025-05-05 byte-identical | `universe_pit` rebuild → rổ lịch sử đổi (VÀO `BAF` / RA `TCM`). ⚠️ **Cần Winston xác nhận**: `universe_pit` là bảng *point-in-time*, rổ của một ngày QUÁ KHỨ đổi có thể là vi phạm PIT thật, không chỉ là test cũ. |
| `universe_pit_p4_selfcheck.py` | "mất đúng 7 ngày" / "fire_new = fire_old − 7" | Chép cứng con số đo tại 2026-07-21; nay đo tới 08-07 nên thành 9 ngày / 89→80. Test tự vô hiệu theo thời gian. |
| `freshness_ops_selfcheck.py` | S1 "ALL FRESH" | Chạy checker thật lên dữ liệu thật. **Đã verify BQ trực tiếp: `ticker_prune` max(time)=2026-08-07, 214 mã → KHÔNG có sự cố dữ liệu thật**; selfcheck đọc nguồn stub/cache mỏng. Báo động giả. |
| `sync_cache_lock_selfcheck.py` | C2 tập file cache giống bản cũ | So `set()` với `set()` — môi trường không có cache. |

**(ii) Harness hỏng (test tự gãy, không phải code sai) — 2 ca:**
- `capit_lever_selfcheck.py:1240` — `run_note()` **trích rồi `exec()`** đoạn `CAPIT_NOTE_SRC` từ
  `bin/send_plan_report.sh`; script production đã đổi → `NameError: name 'plan' is not defined`.
  102 assert TRƯỚC đó vẫn PASS. Cùng họ với bug CHECK5 (extract-and-test giòn theo file nguồn).
- `dcf_selector_selfcheck.py` — assert bằng cách soi mã nguồn ("cả 2 call-site guard trên
  `dcf_at is not None`"); call-site đã đổi.

**(iii) Regression code thật: 0 ca.** Không có selfcheck nào đỏ vì logic production sai.

### 2.2 Vì sao điều này quan trọng hơn số lượng file
Một bộ test mà **9 đèn đỏ là bình thường** thì không còn phân biệt được regression thật với nhiễu.
Đây chính là cơ chế biến "chạy cả bộ" thành vô ích *đồng thời* tốn kém: agent chạy 51 file (~5 phút
+ 3 lần timeout BQ 150s), nhận 9 FAIL, rồi phải tự phán đoán cái nào đáng quan tâm — mỗi lần, lại
từ đầu.

### 2.3 Danh sách PASS (39)
anomaly_gate_prod_parity · approval_gate · basket_price_basis_audit · basket_price_basis ·
book_tagging · capit_participation_cap · churn_guard · concurrent_lock · custom30_publish_weight ·
dc_book_waterfall · dcf_check · dcf_refresh_gate · discretionary_accumulation ·
discretionary_participation_cap · dt5g_chain_freshness · due_diligence · edge_wlag_gate ·
excluded_tickers · extreme_regime · ghost_order · lag_adv_cap · lag_forensic_filter ·
lag_governance_order_gate · lag_liq_signal_filter · lag_live_schedule · lag_rating_filter ·
lag_rating_order_gate · loan_package_resolution · money_path_freshness · net_offsetting_orders ·
netting_recon · paper_main_window · paper_probe_netting · plan_cash_commitment ·
plan_funding_gate · route_selector · rubber_weekly · t2_settlement · tick_retry

---

## 3. Đánh giá trùng lặp / lỗi thời — 3 rổ

### Rổ (a) trùng lặp / bị thay thế → **0 ứng viên chắc chắn. KHÔNG archive gì.**
Ứng viên duy nhất trông giống trùng lặp đã được kiểm và **BÁC BỎ**:
`mike/agents/Taylor/pending_live_flip_chase_cap_20260804/new/{chase_cap_selfcheck.py,
dc_book_waterfall_selfcheck.py, stress_vol_scale_chase_cap.py}` — **byte-identical** với bản sống,
NHƯNG đây là **gói patch ĐANG CHỜ**: flip `chase_cap_vol_scale_enabled` sang LIVE đã có user
sign-off (John 08-04) mà chưa áp được vì auto-mode classifier chặn phiên headless. Archive =
phá một deliverable đang treo. **Giữ nguyên** — nhưng xem §5 mục treo.

### Rổ (b) test code chết cho cơ chế đã chết → **0 ứng viên chắc chắn.**
Đã kiểm 51 selfcheck root: mọi file đều trỏ tới một module production còn tồn tại (bản đồ ngược
ở §4). Không có "test cho cơ chế đã gỡ".

### Rổ (c) còn dùng được → 51 root + 19 `mike/bin`.

### Ngoài phạm vi "test" nhưng là rác thật (chỉ BÁO, không tự xử lý)
| Mục | Bằng chứng | Đề xuất |
|---|---|---|
| `stockquery/vnstock_stockquery/build/` | 24MB, 63 file `test_*.py` lồng 7 tầng `build/lib/build/lib/…`, **`git ls-files` = 0** (không file nào được theo dõi) | Rác build untracked của package vendor. Xoá được nhưng **không phải phạm vi tôi tự quyết** — không phải file của tôi, và tôi không xoá dữ liệu (ranh giới cứng). Đề nghị user/Mike duyệt `rm -rf`. |
| `.verify_a4_worktree` (+ `/tmp/a4_verify_wt`) | `git worktree list` → 2 worktree detached ở `bb8583c`, còn sót từ audit A4 08-04. Gây `git status` bẩn (`m .verify_a4_worktree`) mỗi lần commit | `git worktree remove` — thao tác an toàn, nhưng vẫn nên do người quyết vì có thể còn dở việc. |
| 165 root `test_*.py` | 154/165 không đụng từ 2026-06-21 | **KHÔNG archive** (coding_guidelines §10 mục 4: artifact nghiên cứu là bằng chứng inert). Xử lý bằng **quy ước tên**, không bằng xoá — xem §4. |

---

## 4. Đề xuất chính sách chạy-có-phạm-vi (nội dung cho `coding_guidelines.md` §23)

Bản đề xuất đầy đủ đã ghi ra **`mike/kb/coding_guidelines.md.proposed`** (theo §13 — KHÔNG sửa
tại chỗ, chờ Mike duyệt rồi `mv`). Tóm tắt cơ chế:

**Nguyên tắc**: *chạy cái LIÊN QUAN tới cái mình vừa sửa, không chạy cả bộ theo phản xạ* — TRỪ KHI
đụng vào module lõi dùng chung, lúc đó quét rộng là bắt buộc và phải nói rõ vì sao.

**Bản đồ ngược (dựng bằng máy từ import thật, không chép tay)** — module lõi dùng chung:

| Sửa file này | Số selfcheck phụ thuộc | ⇒ quét rộng? |
|---|---:|---|
| `trading_bot/plan.py` | **21** | ✅ BẮT BUỘC |
| `trading_bot/executor.py` | **11** | ✅ BẮT BUỘC |
| `trading_bot/config.py` | **15** | ✅ BẮT BUỘC |
| `trading_bot/brokers.py` | 7 | ✅ BẮT BUỘC |
| `trading_bot/plan_funding_gate.py` | 2 | ⚠️ ca 08-07 cho thấy phụ thuộc THẬT rộng hơn import (gate chạy trong luồng của 6+ selfcheck khác) |
| `trading_bot/vn_market.py` | 4 | tuỳ |
| `trading_bot/due_diligence.py`, `netting_recon.py`, `plan_cash_commitment.py`, `discretionary_accumulation.py` | 1–2 | ❌ chạy đúng file liên quan |
| `lag_*.py`, `dcf_*.py`, `custom_basket.py`, `anomaly_gate.py`, … | 1–6 | ❌ chạy đúng file liên quan |

Bảng đầy đủ (43 module → selfcheck) nằm trong `.proposed`. Nó **dựng lại được bằng lệnh**, không
phải bảng chép tay sẽ mốc:

```bash
# in ra: module production -> các selfcheck import nó
python - <<'PY'
import re, glob, collections
m = collections.defaultdict(set)
for f in sorted(glob.glob("*selfcheck*.py")):
    src = open(f, encoding="utf-8", errors="replace").read()
    for a, b in re.findall(r'from\s+(trading_bot[\w.]*)\s+import|import\s+(trading_bot[\w.]*)', src):
        m[a or b].add(f)
for k in sorted(m): print(f"{k:38s} <- {', '.join(sorted(m[k]))}")
PY
```

---

## 5. Việc cần NGƯỜI quyết (tôi không tự làm)

1. **`universe_pit_p2` FAIL — có thể là vi phạm point-in-time THẬT**, không chỉ test cũ: rổ của
   ngày quá khứ 2025-05-05 đã đổi (VÀO `BAF` / RA `TCM`). → dispatch **Winston** xác nhận.
2. **9 selfcheck đỏ**: sửa hay chấp nhận? Đề nghị nguyên tắc "**test không được assert lên trạng
   thái sống**" — 6/9 ca là vi phạm nguyên tắc đó (chép cứng rổ/số đếm/đọc file production). Sửa =
   đóng băng fixture. Đây là việc riêng, không nhét vào job này.
3. **Flip `chase_cap_vol_scale_enabled` sang LIVE** treo từ 08-04 (đã có sign-off user), cần 1 phiên
   interactive áp `pending_live_flip_chase_cap_20260804/flip_live.patch`.
4. **Rác**: `stockquery/…/build/` (24MB untracked) và 2 worktree `.verify_a4_worktree` /
   `/tmp/a4_verify_wt`.
5. **Duyệt `coding_guidelines.md.proposed`** (§23 chính sách chạy-có-phạm-vi).
