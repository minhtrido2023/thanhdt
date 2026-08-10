# PENDING — nới trần entry LAG phiên 2/3: `anchor` → `anchor × 1,03`

- **Job**: `Taylor_20260810_101717` · **Ngày**: 2026-08-10 · **Owner**: Taylor
- **Trạng thái**: **CHƯA ÁP DỤNG, CHỜ DUYỆT.** `git status --porcelain trading_bot/` rỗng.
- **Báo cáo**: `mike/agents/Taylor/research/lag_anchor_widen_nav_backtest_20260810.md`
- **Tiền đề**: `mike/agents/Taylor/research/lag_entry_window_execution_20260810.md` §5.4

## ⛔ ĐỌC DÒNG NÀY TRƯỚC MỌI DÒNG KHÁC

**Backtest NAV KHÔNG ủng hộ thay đổi này.** Patch được soạn theo yêu cầu dispatch (việc #4) để
sẵn sàng NẾU user quyết định tiến trên **luận cứ vận hành**. **TUYỆT ĐỐI không trích bất kỳ con số
backtest nào để biện minh cho việc áp patch này.**

| Đo được ở mức NAV | Giá trị |
|---|---|
| Δ CAGR (`×1,03` vs `= anchor`) | **+0,08pp** (29,01% → 29,09%) |
| Block-bootstrap 95% CI | **[−0,563; +0,667]pp** — **chứa 0** |
| `P(Δ > 0)` | **0,546** (≈ tung đồng xu) |
| Sign test theo năm | 8/13, **p = 0,581** |
| **PBO (CSCV)** | **0,775** — cao, dạng reshuffle-luck |
| Sharpe | **1,91 → 1,91** (không đổi) |
| Calmar / MaxDD | **1,60 → 1,59** / **−18,1% → −18,3%** (xấu hơn) |
| Đường liều-đáp cap 0→1→2→3→5% | 29,01 / 29,02 / 28,98 / **29,09** / 28,78 — **KHÔNG đơn điệu** |

Event-study gốc nói **+0,84pp/sự kiện**; ở mức NAV còn **+0,08pp**. §5.4 báo cáo gốc đã dự báo
đúng điều này (sổ LAG oversubscribe ~6× ⇒ fill thêm mã KHÔNG tạo thêm vốn).

## Patch này làm gì — và KHÔNG làm gì

| | |
|---|---|
| ✅ Làm | `trading_bot/plan.py`: thêm hằng `LAG_ANCHOR_CEILING_MULT = 1.03`; `load_plan()` suy `hard_no_chase_ceiling_vnd = anchor × MULT` |
| ✅ Làm | `hard_no_chase_ceiling_selfcheck.py`: cập nhật I2/I5b/I5c/I6 lên **công thức** (import hằng số), thêm ca ngược **I2b** |
| ❌ **KHÔNG** làm | sửa `executor.py` — **cơ chế §24 giữ nguyên tuyệt đối** |
| ❌ **KHÔNG** làm | đụng BAL / CAPIT / discretionary — chúng không mang `entry_anchor_price` nên khối này bỏ qua hoàn toàn |
| ❌ **KHÔNG** làm | đụng LAG **phiên 1** — phiên chuẩn không có anchor, chính nó ĐẶT RA anchor |

Phạm vi tự động đúng vì `entry_anchor_price` **chỉ** được
`mike/bin/filter_lag_entry_window.py::_apply_anchor_gate()` gắn cho ứng viên LAG **phiên 2/3**.

## Cổng đã qua / chưa qua

| Cổng | Kết quả |
|---|---|
| Backtest NAV (`pt_v23_audit_2014.py`, lệnh pin R3 nguyên văn, `$DNA_PYEXE`, threads=1) | ✅ đã chạy **9 chân**, **self-check 0 VND cả 9** |
| Chân đối chứng tái lập pin R3 | ✅ **BYTE-IDENTICAL** md5 `7d053e6201c9d107685ff4d1dd9d2d2a` với CSV pin registry 08-03 |
| **Kết quả backtest có ủng hộ không** | ❌ **KHÔNG** (bảng trên) |
| Selfcheck phạm vi (`hard_no_chase_ceiling_selfcheck.py`) sau vá | ✅ ngưỡng mới đúng: I2 = 13.390, I6 8/8 lệnh thật PASS |
| **Quét rộng §23** (`plan.py` = module lõi, 23 file theo `selfcheck_scope_map.sh`) | ✅ **23/23 giống hệt chân chưa vá** ⇒ patch gây **0 hỏng mới** |
| quant-skeptic | ✅ **CONFIRMED / confidence cao** (`mike/logs/verify_20260810_110722_3041901.log`) — xác nhận **kết luận NO-GO**, không phải xác nhận nên áp patch. ⚠️ Event bus ghi "INCONCLUSIVE" là **bug parser JSON trailing-comma**, KHÔNG phải verdict. 2 lỗi người kiểm bắt (số fill-event §3, thiếu artifact bootstrap) **đã sửa** — báo cáo §8.1 |
| Paper rehearsal | ❌ **CHƯA** — kế hoạch ở báo cáo §9 |
| **User duyệt** | ❌ **CHƯA** |

## ⚠️ 2 điều phải biết trước khi áp

**1. Có 4 selfcheck ĐANG HỎNG SẴN trên HEAD, không do patch này** (báo cáo §6, đã bisect):
`extreme_regime` (1), `paper_main_window` (3), `t2_settlement` (2), `hard_no_chase_ceiling` E4 (1).
Thủ phạm: commit HYBRID `0f54cb7` + flip cờ `717307f` (cả hai 2026-08-10). Ở `0f54cb7^` cả 4 PASS.
**Trong số đó, E4 nghĩa là event kiểm toán `HARD_CEILING_BLOCK` KHÔNG CÒN ĐƯỢC GHI khi hybrid bật**
— tức cơ chế mà patch này chạm vào đang mất khả năng quan sát. **Nên sửa §6 TRƯỚC.**

**2. Muốn quay về hành vi cũ: đặt `LAG_ANCHOR_CEILING_MULT = 1.0`** — không cần revert patch, không
có state nào phải dọn. Selfcheck đã assert lên công thức nên tự đi theo hằng số (ca I2b tự bỏ qua
khi `MULT == 1.0`).

## Cách áp (phiên interactive, sau khi user duyệt)

```bash
cd /home/trido/thanhdt/WorkingClaude
git apply --check mike/agents/Taylor/pending_lag_anchor_widen_20260810/lag_anchor_widen.patch
git apply         mike/agents/Taylor/pending_lag_anchor_widen_20260810/lag_anchor_widen.patch

# VERIFY ĐỘC LẬP — exit code 0 của git apply KHÔNG phải bằng chứng đã ghi file (§22):
grep -n 'LAG_ANCHOR_CEILING_MULT' trading_bot/plan.py     # phải thấy: = 1.03

TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python hard_no_chase_ceiling_selfcheck.py
# kỳ vọng: I2 = 13390.0 ; chỉ còn ĐÚNG 1 FAIL = E4 (lỗi có sẵn của §6, không phải hồi quy)
mike/bin/selfcheck_scope_map.sh trading_bot/plan.py        # rồi chạy đủ 23 file, so với baseline

git add trading_bot/plan.py hard_no_chase_ceiling_selfcheck.py
git commit -m "LAG entry-window: trần no-chase phiên 2/3 = anchor x1.03 (job Taylor_20260810_101717)"
```

## Đã verify TRƯỚC khi giao patch (chạy thật, không phải đọc-thấy-hợp-lý)

Áp `patch -p1` vào **git worktree tạm** (`/tmp/anchwt`, `data` symlink sang repo thật để I6 đọc plan
thật), chạy selfcheck THẬT, rồi `patch -R` để lấy baseline **cùng môi trường** — 23/23 khớp. Worktree
đã gỡ (`git worktree remove --force`). Repo thật: `git status --porcelain trading_bot/` **rỗng**.

## Rollback

```bash
git apply -R mike/agents/Taylor/pending_lag_anchor_widen_20260810/lag_anchor_widen.patch
```
Hoặc đơn giản hơn: `LAG_ANCHOR_CEILING_MULT = 1.0`.
