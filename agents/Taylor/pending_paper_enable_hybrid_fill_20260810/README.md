# PENDING — bật lịch HYBRID **trên PAPER** (`fill_timing_hybrid_enabled`)

- **Job**: `Taylor_20260810_034544` · **Ngày**: 2026-08-10 · **Owner**: Taylor
- **Trạng thái**: **CHƯA ÁP DỤNG, CHỜ DUYỆT.** Code đã ship, cờ **mặc định TẮT** — patch dưới đây
  chỉ bật trên **paper**, không bật LIVE.
- **Báo cáo**: `mike/agents/Taylor/research/hybrid_fill_timing_implementation_20260810.md`
- **Thiết kế gốc**: `mike/agents/Taylor/research/twap_vs_window_execution_20260804.md` §6+§10

## Patch này làm gì — và KHÔNG làm gì

| | |
|---|---|
| ✅ Làm | `fill_timing_hybrid_enabled` `False` → `True` (1 khoá, `trading_bot/config.py`) |
| ❌ **KHÔNG** làm | bật LIVE. `fill_timing_live_gate=True` vẫn chặn **mọi** account `mode="live"` |

**Muốn chạy LIVE là một quyết định RIÊNG, chưa soạn patch, chưa duyệt**: phải tắt
`fill_timing_live_gate`, mà cờ đó gác **cả layer fill-timing** (kể cả cơ chế gom-cửa-sổ cũ đang
chờ checkpoint ETA 08-14/08-17), không riêng HYBRID. **Đừng gộp hai việc.**

## Cổng đã qua / chưa qua

| Cổng | Kết quả |
|---|---|
| Bằng chứng edge (663 phiên, nến 15') | ✅ có sẵn từ `Taylor_20260804_124836` — **không** backtest lại |
| Selfcheck mới `hybrid_fill_timing_selfcheck.py` | ✅ **116/116 PASS** (105 + bộ **R** 11 ca quote-lỗi, thêm vòng 4), 3 biến thể TZ × 2 interpreter |
| Quét rộng §23 (13 selfcheck `executor.py` + 4 của `config.py` + `test_trading_bot.py`) | ✅ **18/18 rc=0, 0 dòng FAIL** (588 PASS) |
| Diễn tập paper (PaperBroker thật) | ✅ đúng 5 block MUA + 4 block BÁN, đủ KL, **0 reject** |
| quant-skeptic vòng 1 | ❌ REFUTED — 2 lỗi giao thoa, đã vá (§0b báo cáo) |
| quant-skeptic vòng 2 | ❌ REFUTED (high) — deadlock khởi động EXTREME, đã vá (§0c) |
| quant-skeptic vòng 3 | ✅ **CONFIRMED (medium)** — `mike/logs/verify_20260810_043304_*.log` |
| Throttle `extreme_defer_poll_sec` — quant-skeptic vòng 4 | ❌ **REFUTED (high)** `verify_20260810_051022_*.log` — throttle đóng dấu thời gian TRƯỚC khi biết quote có ok không ⇒ 1 quote lỗi tiêu trọn 60s mà bộ đếm 2-poll không nhích ⇒ tái sinh deadlock vòng 2 qua lối khác (reviewer tái lập: quote lỗi suốt 09:00-09:15 ⇒ **0 lệnh**). **ĐÃ VÁ** (chỉ đóng dấu khi poll THÀNH CÔNG) |
| Throttle — quant-skeptic vòng 5 (sau vá) | ✅ **CONFIRMED (high)** `verify_20260810_052344_*.log` — reviewer tự chạy lại selfcheck, tự đảo ngược đúng 1 dòng để xác nhận bộ R **thật sự phân biệt được** (5/7 ca FAIL trên code cũ), tự chạy lại 14/14 quét rộng; *"I found no additional path by which EXTREME could stay locked beyond one throttle cycle"* |
| **User duyệt** | ❌ **CHƯA** — cần John/Mike đồng ý bật trên paper |

## ⚠️ ĐỌC TRƯỚC KHI ÁP — 2 điều đã đo được, không phải giả định

**1. Áp patch này là bật ĐỒNG THỜI 3 cờ trên paper `main`.** `secrets/trading_bot_accounts.json`
khối **`overrides`** của `main` **đã bật sẵn** `extreme_regime_enabled: true` và
`gap_adaptive_enabled: true`. (Tra ở tầng gốc của file sẽ thấy `None` và kết luận SAI — đúng lỗi
tôi mắc lúc đầu, quant-skeptic vòng 3 bắt được.) Nghĩa là toàn bộ đường giao thoa mà 3 vòng review
vừa đào — HYBRID × EXTREME × gap-adaptive — sẽ **chạy thật ngay phiên đầu tiên**, không còn dormant.
Đó chính là lý do 3 lỗi ở §0b/§0c đáng để vá trước, và cũng là lý do cần theo dõi phiên đầu.

**2. Chi phí quote đã được đo, đã có throttle, và throttle NAY ĐÃ QUA REVIEW (vòng 4 REFUTED → vá
→ vòng 5 CONFIRMED).** Không throttle: **+3.590 lời gọi `get_quote`/phiên** (kế hoạch 10 lệnh MUA;
PHS cache TTL 3s < `poll_interval_sec` 20s). Có throttle `extreme_defer_poll_sec=60`: **~120**.
Muốn về hành vi cũ (poll mỗi chu kỳ): đặt `extreme_defer_poll_sec: 0`.

Bản throttle ĐẦU TIÊN có lỗi thật và đã bị vòng 4 bác: nó đóng dấu `_extreme_defer_poll[ticker]`
**trước** khi kiểm `q_ext.ok()`, nên một lần `get_quote` lỗi (`PHSBroker.get_quote` `return None`
khi exception — hành vi đã có sẵn) "tiêu" trọn cửa sổ 60s mà bộ đếm 2-poll-confirm không nhích;
dưới chuỗi lỗi lặp đúng nhịp 60s, lệnh BÁN khẩn kẹt sạch cửa sổ hoãn. **Bản vá:** chỉ đóng dấu khi
poll THÀNH CÔNG ⇒ lần lỗi được thử lại ngay chu kỳ sau. (Không chọn "backoff ngắn 5–10s cho lần
lỗi" vì `_place_slices` chỉ chạy mỗi 20s ⇒ mọi backoff <20s cho ra đúng một hành vi, chỉ thêm knob
gây hiểu nhầm.) Đo được sau vá — arm vẫn có TRẦN, xuống cấp mượt theo tỉ lệ lỗi:

| Tỉ lệ quote lỗi | 0% | xen kẽ 1/2 | 2/3 | 3/4 | 4/5 | 100% |
|---|---|---|---|---|---|---|
| EXTREME arm lúc | 09:01:00 | 09:01:40 | 09:01:40 | 09:02:20 | 09:03:00 | không arm* |

\* broker chết hẳn thì **nền (HYBRID TẮT) cũng đặt 0 lệnh** (ca R3b) — tức đó là lỗi broker, không
phải HYBRID tệ hơn nền; và lúc đó vẫn thử lại **mỗi chu kỳ** (45/45), không bị throttle khoá.

**Việc còn nợ sau khi bật paper** (quant-skeptic vòng 5 đề nghị, không chặn): bắt 1 phiên
09:00–09:15 có lỗi quote PHS THẬT rồi đối chiếu thời điểm arm với trần ~2' ở trên — mọi bằng chứng
hiện tại đều là mô phỏng `FakeBroker`, chưa có broker thật.

## Cách áp (phiên interactive, sau khi quant-skeptic CONFIRMED + user duyệt)

```bash
cd /home/trido/thanhdt/WorkingClaude
git apply --check mike/agents/Taylor/pending_paper_enable_hybrid_fill_20260810/enable_paper.patch
git apply         mike/agents/Taylor/pending_paper_enable_hybrid_fill_20260810/enable_paper.patch

# VERIFY ĐỘC LẬP — exit code 0 của git apply KHÔNG phải bằng chứng đã ghi file (§22):
grep -n '"fill_timing_hybrid_enabled"' trading_bot/config.py    # phải thấy: True

# selfcheck BẮT BUỘC sau khi áp (2 file dưới đây assert lên cờ, phải chạy lại):
TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python hybrid_fill_timing_selfcheck.py
TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python \
    mike/agents/Taylor/exp_hybrid_fill_20260810/paper_rehearsal_hybrid.py

git add trading_bot/config.py
git commit -m "hybrid fill-timing: enable on PAPER (fill_timing_hybrid_enabled -> True), job Taylor_20260810_034544"
```

⚠️ **Sau khi áp, selfcheck ca A sẽ FAIL 1 dòng** — `check("mặc định trong DEFAULTS là TẮT", ...)`.
Đó là **đúng thiết kế**, không phải hồi quy: ca đó tồn tại để bảo vệ trạng thái "chưa duyệt". Khi
áp patch, **sửa đúng dòng đó** trong `hybrid_fill_timing_selfcheck.py` thành `is True` kèm chú
thích ngày/job (y hệt cách `chase_cap_selfcheck.py` đã làm khi flip 2026-08-04) — **không xoá ca**.
(Đây chính là loại file thứ-N mà bản patch chase-cap đầu tiên suýt bỏ sót; ghi ra đây để lần này
không lặp lại.)

## Đã verify TRƯỚC khi giao patch (không phải đọc-thấy-hợp-lý)

Áp **thật** vào một bản sao tạm (`/tmp/patchtest/`, `patch -p1`) rồi **import module đã vá** để đọc
giá trị runtime — không tin `git apply --check`:

```
DEFAULTS sau patch: fill_timing_hybrid_enabled=True | fill_timing_live_gate=True
file THẬT trong repo: "fill_timing_hybrid_enabled": False   ← vẫn nguyên, chưa đụng
```

## Rollback

```bash
git apply -R mike/agents/Taylor/pending_paper_enable_hybrid_fill_20260810/enable_paper.patch
```
Hoặc đơn giản hơn: đặt lại `False`. Cờ không mang state — tắt là về hành vi cũ ngay chu kỳ sau,
không cần dọn dẹp gì.
