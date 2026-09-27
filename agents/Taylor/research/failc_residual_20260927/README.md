# FAIL-C — 2 tồn dư cùng lớp lỗi (nhãn `entry` thay vì `known_date`)

Job `Taylor_20260927_100121`. Branch `fix/lag-edge-residual-live-negstreak`, worktree
`/home/trido/thanhdt/wt-lagedge-residual`. **CHƯA MERGE — chờ user sign-off.**

Cả hai đều **BENIGN hôm nay** (đo thật, không suy luận) ⇒ đây là **vá phòng ngừa + đúng nhãn**,
KHÔNG phải sự cố. Chuỗi `data/lag_edge_health.csv` **không đổi một byte** — chỉ nhãn dùng để
index và phép tính `neg_streak` đổi.

## Bối cảnh: FAIL-C là gì

`lag_edge_health.csv` có 1 dòng / sự kiện earnings, với 2 mốc thời gian:
- `entry` = ngày VÀO lệnh (T+5 sau release)
- `known_date` = `entry` + **25 phiên** = ngày `ret` của sự kiện đó mới thực sự ĐỌC ĐƯỢC

`mean12` (trailing-12M mean post-return) của một dòng chỉ tồn tại từ `known_date`. Index chuỗi
trên `entry` + `ffill` ⇒ đọc giá trị **25 phiên trước khi nó có thể tồn tại**. FAIL-C gốc
(2026-09-27, đã vá + re-pin) chỉ chạm nhánh **BACKTEST** (`pt_v23_audit_2014.py:2062-2066`).

## (1) Đường LIVE — `deploy_golive_dt5g_v4/golive_recommend_v23.py::w_lag_target`

**Trước:** `parse_dates=["entry"]` + `set_index("entry")` (dòng 293-294).
**Sau:** `key = "known_date" if "known_date" in eh.columns else "entry"`, mirror đúng pattern đã
vá ở `pt_v23_audit_2014.py`, **kèm FALLBACK**: thiếu cột ⇒ rơi về `entry` + in cảnh báo to.

Vì sao fallback chứ không fail-closed: đây là allocator **tiền thật**; `known_date` chỉ là cột
HIỂN THỊ đối với con số w_LAG. Một cột hiển thị thiếu không được phép hạ cả đường lập plan.

### A/B — 4 ô (BEFORE=`main`, AFTER=worktree) × (file mới, file backup pre-FAIL-C)

as-of `2026-09-27`, state=3 NEUTRAL, `EDGE_THR=1.0%` — log: `log_ab_prepost.txt`

| file | bản | w_LAG | label_col | mean12 | as-of nhãn của chuỗi |
|---|---|---|---|---|---|
| MỚI (có `known_date`) | BEFORE | **0,50** | `entry` | −0,6% | 2026-08-14 |
| MỚI (có `known_date`) | AFTER | **0,50** | `known_date` | −0,6% | **2026-09-23** |
| BACKUP (không có cột) | BEFORE | **0,50** | `entry` | −0,6% | 2026-08-14 |
| BACKUP (không có cột) | AFTER | **0,50** | `entry` + WARNING | −0,6% | 2026-08-14 |

**Kết luận:** `w_LAG` **0,50 ở cả 4 ô ⇒ 0 regression trên tiền.** Cái đổi là **mốc as-of in vào
báo cáo**: `2026-08-14` → `2026-09-23`, tức bản cũ trễ hơn thực tế **25 phiên (~40 ngày lịch)**.
Nhánh backup chứng minh fallback hoạt động: không crash, w_LAG giữ nguyên, cảnh báo in rõ.

Lý do live benign: live luôn đọc **dòng CUỐI** của chuỗi, và ở dòng cuối cả 2 nhãn cùng trả
`mean12 = −0,6048%` (cùng dưới ngưỡng 1,0%) ⇒ cùng `w_LAG 0,50`.

## (2) `edge_health_monitor.py::neg_streak` — nhãn resample

**Trước (dòng 188):** `d.set_index("entry")["mean12"].resample("ME").last()`.
**Sau:** helper module-level `neg_month_streak(d, label)`, gọi với `known_date`; nhãn `entry` chỉ
còn được tính để **in đối chiếu** (`neg_streak_entry_legacy`), KHÔNG bao giờ điều khiển `act`.

Cơ chế lệch không phải "dịch đều": bước lùi 25 phiên **đổi dòng nào là "dòng cuối tháng"**, nên
dấu của tháng có thể đảo.

### Đo thật trên file production (log: `log_lag_edge_health_rerun.txt`)

```
neg_streak=1 (anchor=known_date, CAUSAL — dùng cho ngưỡng hành động)
neg_streak_entry_legacy=2 (anchor=entry, nhãn CŨ trung bình sớm 25 phiên — chỉ đối chiếu)
{ "mean12": -0.6, "win12": 35.5, "n12": 566, "pctl": 5.0, "asof": "2026-09-23",
  "neg_streak": 1, "neg_streak_anchor": "known_date", "neg_streak_entry_legacy": 2,
  "verdict": "NEGATIVE",
  "act": "canh bao: ha w_LAG .65->.50 neu keo dai 3 thang (dang 1, moc known_date)" }
```

Tháng cuối chuỗi, 2 trục (log `log_ab_label.txt`):
- trên `entry`: `2026-07 = −0,158` · `2026-08 = −0,605` → **streak 2**
- trên `known_date`: `2026-08 = +0,431` · `2026-09 = −0,605` → **streak 1**

⇒ ngưỡng hành động `neg_streak >= 3` (HẠ `w_LAG` .65→.50 + treo entry LAG mới) trên nhãn cũ sẽ
chạm **sớm ~1,2 tháng** so với đúng. Hôm nay benign vì cả 2 đều < 3.

**Chuỗi CSV không đổi:** sinh lại ra `/tmp/failc_residual_lag_edge_health_20260927.csv` cho md5
**y hệt** `data/lag_edge_health.csv` (`dc4ce3a9bd35152c5a344a4fe90d0554`). Canonical **KHÔNG bị
ghi đè** (`md5sum -c` OK sau khi chạy) — Mike đã promote bản đúng, backup `.bak_20260927_prefailc`.

### Dòng verdict mới (ghi rõ mốc + số legacy)

```
📮 LAG edge: NEGATIVE (12M -0.60%/win 36%, n=566, pctile 5, asof 2026-09-23 [moc=known_date],
   neg_streak 1 [nhan cu 'entry': 2]) → canh bao: ha w_LAG .65->.50 neu keo dai 3 thang (dang 1, moc known_date)
```

## (3) Selfcheck — `failc_residual_selfcheck.py`

`$DNA_PYEXE failc_residual_selfcheck.py [--all-tz]` · log: `log_selfcheck_3tz.txt`

**19 assertion · 2/2 mutant KILLED · PASS ở cả 4 môi trường**
(`UTC`, `Asia/Ho_Chi_Minh`, `America/New_York`, `env -u TZ` — tất cả rc=0).

| Test | Kiểm |
|---|---|
| T1 | LIVE `w_lag_target` dùng `known_date`; mutation `key="entry"` ⇒ **CHẾT** |
| T1b | thiếu cột ⇒ fallback `entry` + cảnh báo + w_LAG hợp lệ, **không crash** |
| T1c | file THẬT: 2 nhãn cùng `w_LAG` (benign) nhưng **khác** as-of (bug nhãn có thật) |
| T2 | `neg_month_streak` neo `known_date`; mutation nhãn `entry` ⇒ **CHẾT** |
| T2b | thiếu cột ⇒ `(None, None)`, không crash |
| T2c | hợp đồng return dict + `resample` trên `entry` đã biến mất khỏi file |

**Fixture là bảng DỰNG TAY, không sinh máy móc** — và đó là một finding của chính selfcheck này:
bản đầu dùng chuỗi dạng bậc thang (dương rồi âm) thì **cả 2 nhãn cho streak = 3**, mutant "chết"
vì guard fixture chứ không vì assertion thật. Muốn 2 trục thực sự không đồng ý thì dấu `mean12`
phải **xen kẽ** quanh ranh giới tháng. Bảng hiện tại: `entry` → streak **3** (VƯỢT ngưỡng ≥3),
`known_date` → streak **1** ⇒ mutation không chỉ lệch số mà **đổi QUYẾT ĐỊNH** hạ w_LAG.

Tương tự, `pick_discriminating_asof()` ưu tiên ngày mà **cả hai** nhãn đọc được số thực: ca
"một bên NaN" (đầu chuỗi `known_date` chưa có dữ liệu) cũng phân biệt được 2 nhãn nhưng là
discriminator **YẾU** — mutant chết vì thiếu dữ liệu, không vì sai dấu. Ca mạnh đang dùng:
as-of `2026-07-28` → `known_date` cho `w_LAG 0,65`, `entry` cho `0,50`.

## (5) Grep sweep — còn call-site nào index vào `entry`?

Liệt kê, **KHÔNG tự sửa lan** (ngoài phạm vi dispatch). Sau khi loại worktree (`wt-*`,
`mike_paseo`, `.claude/worktrees/`) và snapshot thí nghiệm (`data/*_exp`, `agents/*/exp_*`,
`agents/*/research/*`), các file canonical còn `parse_dates=["entry"]` + `set_index("entry")`:

| File | Dòng | Loại | Ghi chú |
|---|---|---|---|
| `pt_v22_dt5g.py` | 777-778 | engine paper V2.2 DT5G | `reindex(common, method="ffill")` — **cùng hình dạng look-ahead như FAIL-C backtest** |
| `pt_v23_audit_ddpark.py` | 736-737 | harness DD/park | |
| `pt_v23_lagcap_research.py` | 2061-2062 | research LAG capacity | |
| `pt_v23_lagqual_research.py` | 2084-2085 | research LAG quality | |
| `lag_dnpr_harness.py` | 1695-1696 | harness DNPR | |
| `converge_fullharness_test.py` | 1831-1832 | harness hội tụ | |
| `data/research_edge_alloc_walkforward.py` | 12 | research walk-forward | chính là nghiên cứu **dựng ra** allocator edge-conditional |
| `data/research_edge_conditional_allocator.py` | 24 | research | như trên |

**Đã đúng rồi (không cần chạm):** `pt_v23_audit_2014.py:2062-2066` (canonical, đã vá FAIL-C +
re-pin), và 2 file của job này.

**Đọc con số này thế nào:** đây đều là engine **backtest/research**, không phải đường live — nên
chúng KHÔNG đụng tiền. Nhưng `pt_v22_dt5g.py` dùng đúng `reindex(..., ffill)` trên nhãn `entry`,
tức cùng hình dạng look-ahead mà FAIL-C đã buộc phải re-pin R3. **Bất kỳ số nào những file này
từng in ra mà được dùng để so sánh/pin đều mang cùng thiên lệch.** Đề xuất (chờ chỉ đạo): vá
`pt_v22_dt5g.py` trước (nó là engine paper đang chạy), 7 file còn lại vá theo lô kèm re-run.

## Chạy lại

```bash
cd /home/trido/thanhdt/wt-lagedge-residual/WorkingClaude
$DNA_PYEXE failc_residual_selfcheck.py --all-tz          # 19 assertion, 2/2 mutant, 4 TZ
$DNA_PYEXE mike/agents/Taylor/research/failc_residual_20260927/ab_live_prepost.py   # A/B 4 ô
LAG_EDGE_OUT=/tmp/x.csv $DNA_PYEXE -c "import importlib.util as u; s=u.spec_from_file_location('m','edge_health_monitor.py'); m=u.module_from_spec(s); s.loader.exec_module(m); print(m.lag_edge_health())"
```

`$DNA_PYEXE = /home/trido/thanhdt/wc_venv/bin/python` (pandas 3 — bắt buộc cho
`data/earnings_px.pkl`, xem coding_guidelines §8).

---

## ⚠️ ĐIỀU KIỆN TIÊN QUYẾT TRƯỚC KHI MERGE — `edge_wlag_gate_selfcheck.py` check G

Selfcheck có sẵn `edge_wlag_gate_selfcheck.py` (§23, đúng phạm vi cái vừa sửa): **12/13 PASS**.
Check **G** FAIL sau khi vá. Đã truy đến gốc — **KHÔNG phải regression của bản vá**, mà là
**baseline của tripwire đã cũ**.

Check G so `w_lag_target` của đường live với cột `w_lag_tgt` của một CSV pin, trên mọi ngày cột
đó ĐỔI GIÁ TRỊ ("flip day"). Nó đọc hằng
`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv`
— **mtime 2026-07-14**, tức sinh bởi engine **TRƯỚC FAIL-C**.

Đo trên 2 baseline, lọc state 3/4/5 (chỉ ở đó cổng edge mới có tác dụng):

| CSV pin | flip day | khớp nhãn `entry` | khớp nhãn `known_date` |
|---|---|---|---|
| `..._wtnamecap.csv` (Jul-14, **check G đang đọc**) | 25 | **25/25** | 13/25 |
| `..._park3-30_..._exp_failc_new_univpit.csv` (**anchor R3 (sexies)**, sinh 16:49 hôm nay bởi engine ĐÃ vá) | 24 | 22/24 | **24/24** |

**Đọc bảng này:** CSV Jul-14 khớp `entry` **25/25** ⇒ nó *encode chính nhãn look-ahead*. Anchor R3
hiện hành khớp `known_date` **24/24** ⇒ **bản vá tái tạo ĐÚNG production anchor đang dùng**, còn
bản CHƯA vá thì không (22/24). Nói cách khác check G FAIL là **bằng chứng ủng hộ** bản vá, không
phải chống lại — nó đang neo đường live vào một artifact tiền-FAIL-C.

12 flip day lệch (pinned vs live-known_date) đều là cùng một cơ chế — cổng `mean12 >= 4%` bị dịch
~25 phiên: `2015-08-10`, `2017-05-10`, `2017-07-19`, `2017-08-08`, `2017-10-26`, `2019-06-04`,
`2019-08-08`, `2020-10-28`, `2023-11-30`, `2025-05-12`, `2025-07-24`, `2025-11-10`.

**CỐ Ý KHÔNG sửa check G** — ngoài phạm vi dispatch, và nới một test cho vừa bản vá là đúng
anti-pattern. Hai lựa chọn, **cần user chọn**:

- **(A) — khuyến nghị.** Retarget `PINNED_CSV` của check G sang anchor R3 hiện hành
  (`..._park3-30_..._exp_failc_new_univpit.csv`), vì đó là baseline production thật sau FAIL-C +
  park 0,30. Check G sẽ PASS 24/24. Rủi ro: anchor đó mang hậu tố `_exp_`, tức theo §8 là tên
  **không canonical** — nên trước đó phải quyết định tên canonical mới cho pin R3.
- **(B).** Sinh lại `..._wtnamecap.csv` bằng engine đã vá theo ĐÚNG lệnh pin (§8: `$DNA_PYEXE`,
  không phải `python3`) rồi giữ nguyên check G. Nặng hơn, nhưng giữ được một tên canonical duy nhất.

Ghi chú: registry dòng ~7194 đã lưu ý chính file `..._wtnamecap.csv` "CŨNG đã bị ghi lại
2026-07-14" — nó **không còn là anchor R3 hiện hành** kể cả trước FAIL-C (anchor hiện hành là
cấu hình `park 0,30` + `advprice` + `univpit`). Vậy baseline của check G cũ **theo 2 chiều**, không
chỉ chiều nhãn.

Tình trạng còn lại của selfcheck cũ (worktree không có `data/` vì `.gitignore` ⇒ đã copy 2 file
đọc-only vào `wt-lagedge-residual/WorkingClaude/data/` để chạy được; các file này KHÔNG commit).

## §16 (TZ anchor) — gate fail-open ở worktree, đã tự kiểm tay

`tz_anchor_gate` fail-open khi commit: repo lồng `WorkingClaude/mike/` không có mặt ở checkout
worktree (`.gitignore` repo ngoài ẩn nó) ⇒ **3 file .py không được gate**, gate nói rõ ra stderr
(đúng thiết kế §16: KÊU chứ không im lặng). Tự kiểm tay: 3 vùng đã sửa **không có** lệnh lấy thời
gian hiện tại nào. Hit duy nhất trong cả file là `golive_recommend_v23.py:438`
`pd.Timestamp.now().normalize()` — **có trước, ngoài diff** (diff chỉ chạm 290-312), và `pd.Timestamp.now()`
là dạng §16 ghi rõ "CHƯA PHỦ". Không chạm (§3 surgical).
