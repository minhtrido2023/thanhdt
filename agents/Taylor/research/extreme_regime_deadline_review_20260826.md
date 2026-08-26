# extreme_regime — review tại hạn (job Taylor_20260826_004002, 2026-08-26)

**Kết luận một dòng: chương trình ĐÃ TỐT NGHIỆP từ 2026-08-22 (go-live, có user sign-off).
Gate 4 không phải "chưa ai đi kiểm tra" — nó đã đạt 3 ngày trước deadline, chỉ là registry
không được cập nhật, nên checker báo động quá hạn cho một chương trình đã xong.**

## 1. Vì sao checker fire

`bin/paper_checkpoint_escalation.sh` so `end (2026-08-24) < today` và thấy gate_criteria[3]
= `pending` ⇒ escalate. Nhưng registry `updated` vẫn là **2026-08-19**, trong khi go-live xảy ra
**2026-08-22**. Drift 4 ngày.

Bằng chứng go-live — commit `mike@08af2637`, 2026-08-22 04:24:48Z:

```
go-live: extreme_regime + fill_timing_hybrid on SpaceX & ZaloPay (2026-08-22)
User sign-off received. Two gates flipped live simultaneously:
- extreme_regime_enabled=true → both SpaceX and ZaloPay overrides
- fill_timing_live_gate=false + fill_timing_hybrid_live_gate=false → both accounts
Gate chain: 6/6 PASS (selfcheck + quant-skeptic CONFIRMED high, TZ fix 70acee62, stress 40/40 PASS).
```

`secrets/trading_bot_accounts.json` mtime **2026-08-22 11:17 ICT**, khớp cùng cửa sổ với các
journal `exec_STRESSTEST_*` sinh lúc 11:00-11:30 (lần chạy stress kiểm chứng go-live).

## 2. Kiểm lại 6 điều kiện go-live của charter — đo hôm nay, không chép lại số cũ

| # | Điều kiện | Kết quả 2026-08-26 |
|---|---|---|
| 1 | Gate ARMED, verify qua `load_config()`+`load_accounts()` | ✅ main(paper)=True · **SpaceX(live)=True · ZaloPay(live)=True** · RocketX(live, enabled=False)=False · ab_cross/ab_dip=False. `probe_linger_live_gate`=True (paper-only, gate riêng, không bị flip) |
| 2 | ZERO false-trigger trên TỔNG phiên evidence, **gồm phiên linger mới** | ✅ **28 phiên** (không tái dùng 25) — xem §3 |
| 3 | Stress-injection PASS | ✅ **40/40 PASS**, chạy lại hôm nay (bộ đã nở 24→40 ca) |
| 4 | Cả hai trigger reachable VÀ đo được | ✅ đo được — xem §4 |
| 5 | Selfcheck (bộ phụ thuộc `executor.py`) | ✅ 20/21 PASS đồng nhất qua 3 môi trường TZ; 1 FAIL không liên quan — xem §5 |
| 6 | quant-skeptic sign-off | ✅ CONFIRMED 2026-08-22T02:58Z (medium) + 2026-08-19T13:09Z (CONFIRMED) |

## 3. Đếm lại gate 2 — 28 phiên, 0 marker

Quy tắc GIỮ NGUYÊN (journal `exec_main_*` có ≥1 `PLACE` thành công), không đổi giữa chừng:
31 file 2026-07-07→2026-08-24, trừ 07-08/07-09 (chỉ `GHOST_ORDER`) và 07-30 (386 `PLACE_FAIL`)
⇒ **28 phiên evidence**, tăng từ 25 chốt ngày 08-19 nhờ 3 phiên linger **08-20 / 08-21 / 08-24**
— đúng khuyến nghị quant-skeptic 08-19 ("KHÔNG tái dùng con số 25").

- Quét chuỗi CHÍNH XÁC `EXTREME_PAUSE` / `EXTREME_FLOOR_GUARD` / `EXTREME_DOWN sell-to-floor`:
  **0 hit / 28 phiên**. Quét LỎNG chỉ `EXTREME`: cũng **0**.
- Tầng bằng chứng thứ hai (probe tick log): **1.980 tick** (08-20: 462 · 08-21: 678 · 08-24: 840),
  `trig_ii_would_fire` = **0**, `in_band` = **0**.

**Hai lỗ hổng dữ liệu phải đọc kèm:**

- **(a) Phiên 2026-08-25 — đúng ngày deadline — MẤT.** Host tắt ~18 tiếng (08-24 15:30 →
  08-25 09:45 ICT, `kb/incidents/2026-08/2026-08-25-host-downtime-missed-nightly-crons.md`);
  cron 08:52 không sinh plan main nên `logs/run_bot_main_2026-08-25*.log` chỉ ghi
  "không có plan cho 2026-08-25". **Không phải lỗi gate.**
- **(b) Toàn bộ 28 phiên là PAPER main.** Sau go-live 08-22, journal live gần nhất là
  `exec_SpaceX/ZaloPay_2026-08-14`; plan live 08-20/21/24/26 đều **0 lệnh**. ⇒ Gate đang ARMED
  trên tiền thật nhưng **chưa một phiên live nào chạy qua nó**. "0 hit EXTREME trên 35 journal
  live" là số đúng nhưng RỖNG về mặt thống kê cho giai đoạn sau go-live.

## 4. Gate 4 — hai nhánh trigger giờ đo được tới đâu

Harness `probe_linger_min=30` + `probe_tick_log` (wire 08-19) đã vá đúng hai gap:

| Nhánh | Trước linger (08-19) | Sau linger (08-20→08-24) |
|---|---|---|
| (ii) `r15` 3-sigma | đo được 49/242 dòng (**20%**), phần lớn `None` vì phiên sống trung vị 20 GIÂY | đo được **1.716/1.980 tick (86,7%)** — hết mù do cấu trúc |
| (ii) khoảng cách ngưỡng | r15 âm nhất −0,90% vs ngưỡng lỏng nhất −2,42% (~37% quãng đường) | r15 âm nhất **−1,51%** (08-24) — gần hơn nhưng **chưa từng tiệm cận** |
| (i) band-proximity | suy gián tiếp từ OHLC ngày; 0/242 dòng PLACE trong band, min headroom 4,43% | đo **TRỰC TIẾP tại giây executor còn sống**, n=1.980: min headroom **5,90%** vs `extreme_band` 3,00%, `in_band` **0** |

⚠️ Trung thực về hướng số: min headroom đo bằng tick log (5,90%) **XA hơn** con số 4,43% đo trên
dòng PLACE ngày 08-19, vì linger lấy mẫu khung giờ khác. **Không được đọc là "thị trường an
toàn hơn"** — chỉ là mẫu khác.

**⇒ Bằng chứng vẫn MỘT CHIỀU:** chứng minh gate không kêu bậy khi thị trường lành tính.
KHÔNG chứng minh gate xử lý đúng khi sập thật — phần đó tới giờ vẫn chỉ có stress-injection
(40/40) bảo chứng. Đây là giới hạn đã biết và user đã chấp nhận khi ký (chính sách 08-19:
gate là BẢO HIỂM, thiếu sự kiện sập thật không phải blocker).

## 5. Selfcheck — sweep §23 trên `executor.py`

`bin/selfcheck_scope_map.sh trading_bot/executor.py` → 21 file. Chạy đủ 21 file × 3 môi trường:

| Môi trường | Kết quả |
|---|---|
| TZ mặc định | **20/21 PASS** |
| `env -u TZ` | **20/21 PASS** |
| `TZ=America/New_York` | **20/21 PASS** |

FAIL duy nhất, **giống hệt ở cả 3 môi trường** (nên không phải lỗi TZ):
`capit_lever_selfcheck.py` — 5 ca (A7, C20, G1, L2, L3) assert
`data/trading_rules.json :: capit_margin_lever.enabled == false`, trong khi giá trị LIVE đã là
`true` **từ 2026-08-22**. Đây đúng anti-pattern `coding_guidelines §23 hệ luận 1` ("selfcheck
KHÔNG được assert lên trạng thái SỐNG"), **không liên quan gì tới `extreme_regime`** — file
không import và không đụng tới gate. Cần đóng băng fixture, nhưng là việc riêng.

Tin tốt: 2 file mà quant-skeptic 08-22 báo TZ-flaky (`ghost_order_selfcheck.py`,
`paper_main_window_selfcheck.py`) **nay PASS cả 3 môi trường** — khớp với "TZ fix 70acee62"
ghi trong commit go-live.

Selfcheck chuyên trách `extreme_regime_selfcheck.py` (repo root): **ALL PASS**, gồm chứng minh
ngược D1–D4 (HYBRID bật + EXTREME armed ⇒ `EXTREME_PAUSE`; HYBRID bật + EXTREME tắt ⇒
`HYBRID_DEFER`, không có `EXTREME_PAUSE`).

## 6. Hai vấn đề quy trình phát hiện được (không đảo quyết định)

**(A) Dấu vết sign-off chỉ nằm ở COMMIT MESSAGE.** Không có event `answer`/`decision` nào trên
bus ghi lại chữ ký user (grep toàn bộ `kb/events_buffer.md` + `kb/archive/2026-08-2*-nightly.md`
quanh 08-22 = 0 hit go-live). `secrets/` nằm trong `.gitignore` nên chính file cấu hình bị flip
**không có lịch sử git** — mtime 2026-08-22 11:17 là bằng chứng thời điểm duy nhất. Theo
`coding_guidelines §20`, đó là provenance mỏng cho một quyết định chạm tiền thật.
→ Đề xuất: user/Mike bổ sung 1 event `decision` hồi tố kèm `decided_by: "user"`.

**(B) `fill_timing` dính ĐÚNG lỗi này, và VẪN đang fire báo động giả.** Cùng commit `08af2637`
đã flip `fill_timing_live_gate=false` + `fill_timing_hybrid_live_gate=false` trên cả SpaceX và
ZaloPay, nhưng registry vẫn ghi gate 5 = `pending` ("quant-skeptic → user sign-off mới flip
fill_timing_live_gate"). Escalation 2026-08-26 00:40 đã bắn question
`Mike/paper-checkpoint-overdue-fill_timing`. **Tôi KHÔNG tự sửa** — ngoài phạm vi dispatch này
và 4 gate còn lại của nó cần verify riêng.

**Luật rút ra: flip một live gate là phải cập nhật registry TRONG CÙNG LƯỢT.** Nếu không,
checker sẽ báo động quá hạn cho chương trình đã tốt nghiệp — mà báo động giả lặp lại chính là
lớp lỗi `close-the-loop` / §26 mà fleet đã trả giá nhiều lần.

## 7. Đã làm trong job này

- Cập nhật `kb/paper_programs_registry.json`: gate 4 `pending`→`pass` (kèm bằng chứng commit +
  2 caveat), bổ sung ghi chú đo-lại cho gate 1/2/3, `status="graduated-live 2026-08-22"`,
  `progress.count_current` 25→28, viết lại `review_short`, `updated`→2026-08-26.
- Sync lại `kb/paper_programs_charter/extreme_regime.md` bằng `sync_charter()` (không sửa tay).
- Chạy lại `paper_checkpoint_escalation.sh` ⇒ `OK — không có checkpoint quá hạn bị bỏ ngỏ`.
- **KHÔNG chạm bất kỳ live gate nào.** Không sửa `secrets/trading_bot_accounts.json`,
  không sửa `trading_bot/`, không sửa registry của chương trình khác.
