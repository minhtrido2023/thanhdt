# Resolve `git stash@{0}` — "hybrid+refresh_skip_fix WIP 20260810"

**Job**: `Taylor_20260814_142128` · **Ngày**: 2026-08-14 (ngoài giờ giao dịch) · **Tác giả**: Taylor
**Repo**: `/home/trido/thanhdt` (root THẬT — không phải `WorkingClaude/`, cũng không phải `mike/` subrepo)

## KẾT LUẬN 1 DÒNG

**Stash là BẢN SAO ĐÃ LỖI THỜI — 100% nội dung của nó đã landed đúng cách trên `main` bằng 3
commit, chỉ 4 phút SAU khi stash được tạo. `git stash pop` sẽ là một CUỘC LÙI BƯỚC (regression):
nó tái lập đúng con deadlock mà quant-skeptic đã REFUTED vòng 4 và bắt phải vá. Hành động đúng =
DROP, không apply.** Đã drop; SHA ghi lại bên dưới để khôi phục được nếu cần.

## 1. Danh tính stash

```
stash@{0}  SHA = 4bbc3947e94a26e4b45c4cbe86e19ddb87877a04
base       SHA = 024d5ca4045c2e4d806739932c7177c0c086ac14
tạo lúc        = 2026-08-10 12:03:36 +0700
nhánh gốc      = session/1520374161971875940-rubber
nội dung       = WorkingClaude/trading_bot/config.py    (+31)
                 WorkingClaude/trading_bot/executor.py  (+283/−22)
```

Khớp CHÍNH XÁC mô tả trong dispatch: (a) HYBRID fill-timing, (b) fix REFRESH_SKIP
(`exclude_reserved`) của job `Taylor_20260810_042759`, cộng thêm phần throttle
`extreme_defer_poll_sec` mà mô tả không nêu.

## 2. Vì sao stash tồn tại — dòng thời gian đóng kín

| Thời điểm (+0700) | Sự kiện |
|---|---|
| 2026-08-10 **12:03:36** | **stash được tạo** (ảnh chụp WIP) |
| 2026-08-10 **12:07:45** | `031680b` fix(executor): REFRESH_SKIP kích được cả khi trần participation BINDING |
| 2026-08-10 **12:48:53** | `0f54cb7` HYBRID fill-timing: implement spread-within-window (paper-gated, default OFF) |
| 2026-08-10 **12:50:16** | `717307f` hybrid fill-timing: **enable on PAPER** (`fill_timing_hybrid_enabled` → True) |
| 2026-08-12 11:23 | `49c819e` TV1 thin-liquidity: P1 dynamic ceiling + **P2 expected-volume pacing** + P5 |
| 2026-08-14 15:17 | `9a9dbb1` fix(plan,executor): dd_check/dcf_check sai kiểu không làm hỏng polling |

⇒ Stash **không phải việc bị bỏ quên**. Nó là ảnh chụp trước-khi-commit, bị vượt mặt **4 phút**
sau đó, rồi bị bồi thêm 3 commit nữa. Đây là lý do nó "trông giống việc chưa landed" khi nhìn từ
xa nhưng thực tế thì ngược lại.

## 3. Chứng minh CƠ HỌC: HEAD ⊇ stash

Lấy MỌI dòng `+` mà stash thêm vào base, kiểm từng dòng có tồn tại **nguyên văn** trong file HEAD
hôm nay không:

| File | Dòng stash thêm | KHÔNG có nguyên văn trong HEAD |
|---|---:|---:|
| `config.py` | 31 | **2** |
| `executor.py` | 261 | **7** |
| | **292** | **9** |

9 dòng "thiếu" đó, đọc từng dòng một, **đều là bản CŨ ĐÃ BỊ THAY BẰNG BẢN TỐT HƠN** — không dòng
nào là chức năng bị mất:

| # | Dòng trong stash | Trạng thái trong HEAD |
|---|---|---|
| 1 | `"fill_timing_hybrid_enabled": False,` | HEAD = **`True`** (`717307f` — chính là việc dispatch muốn, HEAD đã đi XA HƠN stash) |
| 2 | 1 dòng comment `extreme_defer_poll_sec` | HEAD có bản 4 dòng nói rõ "chỉ tính từ lần poll THÀNH CÔNG" |
| 3–5 | 3 dòng comment `self._extreme_defer_poll = {}` | HEAD có bản 5 dòng giải thích lần quote lỗi KHÔNG đóng dấu |
| 6–8 | 3 dòng comment throttle trong `_place_slices` | HEAD có bản 15 dòng, ghi rõ "vá quant-skeptic REFUTED vòng 4" |
| **9** | **`self._extreme_defer_poll[o.ticker] = now`** (đặt TRƯỚC `get_quote`) | **HEAD dời câu lệnh này VÀO TRONG nhánh `q_ext is not None and q_ext.ok()`** |

Dòng **#9 là dòng nguy hiểm**. Chỉ nó là code thật (8 dòng kia là comment). Nó chính là con bug
mà quant-skeptic REFUTED ở vòng 4 ngày 2026-08-10: đóng dấu throttle TRƯỚC khi biết quote có chạy
được không ⇒ **1 lần `get_quote` lỗi tiêu trọn cửa sổ 60s mà bộ đếm 2-poll-confirm không nhích**
⇒ dưới chuỗi lỗi lặp đúng nhịp 60s, **lệnh BÁN khẩn kẹt sạch cả cửa sổ hoãn** (`PHSBroker.get_quote`
`return None` khi exception — `brokers.py:297`, hành vi có sẵn, không phải giả thuyết).

## 4. Chứng minh THỰC NGHIỆM: apply stash ⇒ 3 bộ selfcheck ĐỎ

Dựng thư mục thăm dò cô lập `/tmp/stash_probe_20260814` (copy `trading_bot/` + 5 selfcheck,
symlink `data/`+`mike/`), **KHÔNG đụng một byte nào của repo thật**, rồi ghi đè 2 file bằng đúng
phiên bản trong stash (`git show stash@{0}:…`). A/B trong CÙNG môi trường:

| Selfcheck | HEAD (control) | Nội dung STASH |
|---|---|---|
| `extreme_regime_selfcheck.py` | rc=0 | rc=0 |
| `refresh_skip_participation_selfcheck.py` | rc=0 | rc=0 |
| **`hybrid_fill_timing_selfcheck.py`** | rc=0 | **rc=1 — 9 FAIL** |
| **`expected_volume_pacing_selfcheck.py`** | rc=0 | **rc=1 — `AttributeError: 'Executor' object has no attribute '_expected_vol_frac'`** |
| **`plan_check_field_schema_selfcheck.py`** | rc=0 | **rc=1** |

**Chân control 5/5 rc=0 trong CHÍNH thư mục thăm dò đó** ⇒ 3 lỗi trên quy được cho nội dung stash,
không phải hiện vật môi trường thăm dò (§19 `verify-before-done`).

9 FAIL của `hybrid_fill_timing_selfcheck.py` gọi thẳng tên con deadlock:

```
[FAIL] mặc định trong DEFAULTS là BẬT (PAPER 2026-08-10)
[FAIL] R1  quote lỗi lặp ĐÚNG NHỊP throttle 60s ⇒ EXTREME VẪN arm được (không deadlock) — armed_at=None
[FAIL] R1b arm trong thời gian CÓ TRẦN (≤3 phút) — armed_at=None
[FAIL] R1c arm xong thì lệnh bán khẩn xả ĐỦ KL ngay trong cửa sổ hoãn — placed=0
[FAIL] R2  poll LỖI KHÔNG đóng dấu throttle — stamp={'TST': 2099-01-01 09:00}
[FAIL] R3  quote lỗi 100% ⇒ thử lại MỖI chu kỳ — 15/45
[FAIL] R5  chập chờn (lỗi 2/3, 3/4, 4/5) ⇒ arm được, có TRẦN ≤4 phút, xả đủ KL  ×3
```

`placed=0` = **lệnh bán khẩn không đặt được một cổ phiếu nào** trong cả cửa sổ hoãn. Đây là tổn
hại THẬT, không phải lỗi cosmetic của test.

## 5. Verify riêng phần REFRESH_SKIP (yêu cầu (4) của dispatch)

Ý đồ gốc job `Taylor_20260810_042759` — báo cáo
`mike/agents/Taylor/research/refresh_skip_participation_bug_20260810.md`, commit `031680b`:

> `_would_be_unchanged` hỏi "huỷ RỒI đặt lại có ra đúng giá+KL cũ không" nhưng gọi `_child_qty`
> mà KHÔNG trừ reservation của CHÍNH lệnh con sắp bị huỷ ⇒ khi trần participation BINDING,
> allowance tụt đúng bằng KL đang treo ⇒ `_child_qty` trả 0 ⇒ REFRESH_SKIP **không bao giờ**
> kích được. Ca thật SpaceX 2026-08-10 BUY-DRI-LAG-01: 15/15 chu kỳ CANCEL_STALE rồi đặt lại y
> hệt 13.000đ × 200cp, mất ưu tiên FIFO vô ích trên đúng mã UPCOM mỏng nhất plan.

Đọc lại code HEAD hôm nay — fix có mặt ĐỦ 3 chỗ đúng như thiết kế, chữ ký công khai không đổi:

1. `_child_qty(self, o, ps, q, px, now=None, exclude_reserved=0)` — mặc định `0`
   ⇒ `_place_slices` byte-identical.
2. Trừ `exclude_reserved` khỏi `fleet_filled` ở **CẢ HAI** nhánh (CAPIT ADV20-paced *và* non-CAPIT
   `day_volume`).
3. `_would_be_unchanged` truyền KL chưa khớp của lệnh sắp huỷ:
   `reserved = 0 if c.get("released") else c["qty"] - c.get("filled", 0)`.

`refresh_skip_participation_selfcheck.py` **ALL PASS (31/31)** trên HEAD, và cũng PASS trên nội
dung stash — tức phần REFRESH_SKIP là chỗ DUY NHẤT stash và HEAD tương đương. Không có gì để cứu.

## 6. Ranh giới LIVE — kiểm bằng số, không bằng đọc code

Dispatch cấm bật HYBRID cho SpaceX/ZaloPay. `fill_timing_hybrid_enabled=True` nằm trong `DEFAULTS`
(dùng chung), nên phải kiểm **giá trị hiệu dụng từng account**, không phải giá trị cờ:

```
main       enabled=True  mode='paper'  live_gate=True  ft=True  hybrid_flag=True  => HYBRID_EFFECTIVE=True
ab_cross   enabled=True  mode='paper'  live_gate=True  ft=True  hybrid_flag=True  => HYBRID_EFFECTIVE=True
ab_dip     enabled=True  mode='paper'  live_gate=True  ft=True  hybrid_flag=True  => HYBRID_EFFECTIVE=True
ZaloPay    enabled=True  mode='live'   live_gate=True  ft=True  hybrid_flag=True  => HYBRID_EFFECTIVE=False
SpaceX     enabled=True  mode='live'   live_gate=True  ft=True  hybrid_flag=True  => HYBRID_EFFECTIVE=False
RocketX    enabled=False mode='live'   live_gate=True  ft=True  hybrid_flag=True  => HYBRID_EFFECTIVE=False
```

Cổng: `executor.py:1077` + `:1207` — `fill_timing_live_gate=True` AND `mode != "paper"` ⇒ trả 1.0 /
bypass HYBRID. **LIVE sạch.** Tôi không đổi gì ở đây; đây là trạng thái đã landed từ `717307f`.

⚠️ **Một điểm cần Mike/user biết (không phải lỗi, là khác biệt so với chữ trong dispatch)**:
HYBRID áp cho **MỌI account paper** (`main`, `ab_cross`, `ab_dip`), không riêng `main`. Cơ chế là
cờ chung + live-gate, không phải allowlist theo account. Nếu muốn giới hạn đúng `main` thì cần một
thay đổi RIÊNG (override per-account), không nằm trong phạm vi job này.

## 7. Selfcheck — quét rộng §23 (executor.py = MODULE LÕI)

Bản đồ ngược lấy bằng lệnh, không chép tay: `bin/selfcheck_scope_map.sh trading_bot/executor.py`
⇒ **17 bộ**. Chạy đủ 17 trên HEAD, `MIKE_BOT_TEST_MODE=1` (§5b), `wc_venv/bin/python`:

```
rc=0  book_tagging_selfcheck.py                    rc=0  hard_no_chase_ceiling_selfcheck.py
rc=0  capit_lever_selfcheck.py                     rc=0  hybrid_fill_timing_selfcheck.py
rc=0  capit_participation_cap_selfcheck.py         rc=0  paper_main_window_selfcheck.py
rc=0  churn_guard_selfcheck.py                     rc=0  plan_check_field_schema_selfcheck.py
rc=0  dcf_check_selfcheck.py                       rc=0  refresh_skip_participation_selfcheck.py
rc=0  discretionary_participation_cap_selfcheck.py rc=0  t2_settlement_selfcheck.py
rc=0  dynamic_no_chase_ceiling_selfcheck.py        rc=0  tick_retry_selfcheck.py
rc=0  expected_volume_pacing_selfcheck.py
rc=0  extreme_regime_selfcheck.py
rc=0  ghost_order_selfcheck.py
```
**17/17 PASS.**

Đối kháng môi trường (§16 + §19) trên 4 bộ nhạy giờ — `hybrid_fill_timing`,
`refresh_skip_participation`, `paper_main_window`, `extreme_regime`:
`env -u TZ` **4/4 rc=0** · `TZ=America/New_York` **4/4 rc=0** · `TZ=UTC` **4/4 rc=0**.

## 8. Hành động đã làm / KHÔNG làm

| | |
|---|---|
| ✅ | `git stash drop stash@{0}` sau khi 17/17 xanh + đã chứng minh HEAD ⊇ stash |
| ❌ | **KHÔNG** `git stash pop`/`apply` — đó là regression, đã chứng minh cả cơ học lẫn thực nghiệm |
| ❌ | **KHÔNG** commit gì vào `trading_bot/` — working tree 2 file này SẠCH, không có gì để commit |
| ❌ | **KHÔNG** đụng cấu hình LIVE (SpaceX/ZaloPay) |
| ❌ | **KHÔNG** đụng repo thật khi thực nghiệm — chạy trong `/tmp/stash_probe_20260814` |

**Khôi phục được** nếu ai đó phản đối kết luận này (git giữ object ~90 ngày):
```bash
cd /home/trido/thanhdt
git show 4bbc3947e94a26e4b45c4cbe86e19ddb87877a04                 # xem lại
git stash store -m "restore WIP 20260810" 4bbc3947e94a26e4b45c4cbe86e19ddb87877a04   # dựng lại stash
```

## 9. Bài học đáng ghi (đề xuất, chưa wire)

Stash sống sót 4 ngày và tạo ra một dispatch "resolve việc chưa landed" trong khi việc **đã**
landed sau đó 4 phút. Gốc rễ giống §28 `coding_guidelines.md`: **suy diễn trạng thái từ SỰ VẮNG
MẶT của một kênh** ("có stash treo" ⇒ "có việc chưa vào") thay vì đối chiếu ARTIFACT (`git log`
của chính 2 file đó). Kiểm 30 giây đủ phân biệt:
`git diff stash@{0} HEAD -- <files>` — 0 dòng xoá có nghĩa ⇒ stash thừa.

---
*Selfcheck log lệnh + thư mục thăm dò `/tmp/stash_probe_20260814` giữ nguyên để quant-skeptic tái lập.*
