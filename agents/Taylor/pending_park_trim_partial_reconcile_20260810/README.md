# PENDING — cổng đối soát park_trim/JIT: chặn TỪNG MÃ thay vì chặn CẢ TÀI KHOẢN

**Job** `Taylor_20260810_113500` · 2026-08-10 · Taylor
**Trạng thái: CHỜ DUYỆT. 0 dòng production bị sửa** (đã verify bằng `git status` sau mỗi vòng test).

## Vá cái gì

`compute_trim()` (L1) và `build_jit_unpark()` (L2) đều mở đầu bằng cùng một cổng:

```python
if not h["reconcile"]["ok"]:
    out["decision"] = "BLOCKED_RECONCILE"
    return out
```

Một mã lệch sổ ⇒ **0 lệnh cho cả tài khoản**, ở **cả hai** đường cấp vốn. Ngày **2026-08-06**
(VHM chia cổ tức CP 1:1 chưa vào `data/corp_actions.json`) điều đó khoá sạch vốn của **cả hai**
tài khoản đúng **PHIÊN ENTRY CHUẨN** của 6 mã LAG — mất không phục hồi được (phiên 2/3 bị trần
anchor, hết phiên 3 là `WINDOW_PASSED`).

Trong khi đó **tầng loại theo TỪNG MÃ đã tồn tại sẵn** ngay bên dưới: `unverified_tickers` →
`blocked[]` với lý do `sổ UNVERIFIED — cấm sinh lệnh (§21)`. Cổng 0 là **một tầng thô chặn trước
một tầng mịn vốn đã làm đúng việc**. Bản vá không dựng cơ chế mới — nó để tầng mịn làm việc, và
giữ cổng thô cho đúng những ca tầng mịn KHÔNG che được.

## Hai hướng lệch có hậu quả NGƯỢC NHAU (lý do bản vá không phải là "bỏ cổng đi")

`tgt_i = w'_i × 0,8 × (cash + park_mv)` với `w'_i` là trọng số rổ mục tiêu (không phụ thuộc ta
đang giữ gì); `want_i = mv_i − tgt_i`:

| Hướng | `park_mv` | `tgt_i` | `want_i` | Hệ quả | Xử lý |
|---|---|---|---|---|---|
| `diff > 0` — SỔ nhiều hơn broker (ghost order, fill sót journal) | phồng | phồng | co | trim ÍT hơn đúng — sai an toàn, nhưng KHÔNG phải chữ ký corp action | **giữ chặn cứng** |
| `diff < 0` — BROKER nhiều hơn sổ (chia tách/thưởng/cổ tức CP) | **thiếu** | **thiếu** | **phồng** | **OVER-TRIM trên CÁC MÃ KHÁC** | chạy tiếp, **nhưng phải hiệu chỉnh mẫu số** |

⚠️ Đây là điểm dễ làm sai nhất: tầng `unverified_tickers` chỉ cấm bán **chính mã lệch** — nó
**không** chặn được việc over-trim các mã khác. Vì vậy **nới cổng mà không sửa mẫu số là một bản
vá HỎNG**. L1 hiệu chỉnh `park_mv` theo **số lượng của broker** (broker là nguồn sự thật về số
lượng — §6/§25); phần chênh chỉ cộng cho mã đang nằm trong sổ PARK.

Bất định còn lại — phần cp tăng thêm có thật sự thuộc book PARK không — **không cần đoán đúng**:
cộng nhầm vào PARK ⇒ `park_mv` phồng ⇒ rơi về đúng nhánh `diff>0` = trim ÍT hơn. **Cả hai giả
thuyết đều cho hướng sai an toàn.**

**L2 KHÔNG cần hiệu chỉnh mẫu số** — `park_mv_vnd` ở L2 chỉ dùng để IN RA; cỡ lệnh suy từ nhu cầu
tiền của từng lệnh mua và số cp bán được của từng mã. Đã kiểm bằng đọc code, không suy đoán.

**Phải vá cả hai cùng lúc.** Hai cổng đọc CÙNG một `h["reconcile"]`. Vá mỗi L1 ⇒ có lệnh trim
nhưng đường cấp vốn JIT cho lệnh MUA vẫn chết ⇒ vẫn không vào được lệnh phiên chuẩn.

## KHÔNG đổi giá trị `decision` ở nhánh chạy tiếp

`send_plan_report.sh:629` chỉ render danh sách lệnh BÁN khi `decision == "TRIM"`. Đặt một giá trị
mới (`PARTIAL_RECONCILE`) ⇒ lệnh rơi vào nhánh `elif pt_dec:` một dòng ⇒ **user không thấy để
duyệt** = đúng lớp lỗi mất-lệnh-im-lặng mà cổng này sinh ra để chặn. Trạng thái xuống cấp báo qua:
`reconcile_ok=false` (đã có sẵn) + `reconcile_partial=true` (mới) + note **đặt đầu** `notes[]`
(báo cáo chỉ in `notes[:2]`).

## Cưỡng chế "cấm bán mã lệch" TẠI CHỖ, không giả định đầu vào

`book_tagging_selfcheck.py::C1` dựng đúng tổ hợp *mismatch mà không unverified* — bản vá vòng 1
của tôi trượt ca này (nó tin caller đã khai). `park_holdings` production có khai, nhưng
`compute_trim`/`build_pool` còn nhận `holdings=` bơm tay từ 5 selfcheck và có thể từ caller tương
lai. Cấm bán mã lệch là **điều kiện an toàn của chính nhánh này** ⇒ phải cưỡng chế tại chỗ. L2 suy
thẳng từ `h["reconcile"]` trong `build_pool` — hàm duy nhất dựng rổ bán, nên không đường gọi nào
lách được.

## Bằng chứng — A/B trên DỮ LIỆU THẬT ngày 2026-08-06

Chân đối chứng = registry đã ký (hôm nay). Chân sự cố = `corp_actions=[]`, tái lập **chính xác**
trạng thái registry lúc pipeline chạy 2026-08-05 19:07.

| Account | Chân | OLD (production) | NEW (bản vá) |
|---|---|---|---|
| SpaceX | registry đã ký (**đối chứng**) | `TRIM` 14 lệnh **100,34tr** | `TRIM` 14 lệnh **100,34tr** ✅ *y hệt* |
| SpaceX | registry rỗng (**ca thật 08-06**) | `BLOCKED_RECONCILE` **0đ** | `TRIM` 13 lệnh **92,69tr** |
| ZaloPay | registry đã ký (**đối chứng**) | `TRIM` 6 lệnh **30,64tr** | `TRIM` 6 lệnh **30,64tr** ✅ *y hệt* |
| ZaloPay | registry rỗng (**ca thật 08-06**) | `BLOCKED_RECONCILE` **0đ** | `TRIM` 5 lệnh **22,99tr** |

- **Chân đối chứng trùng khớp tuyệt đối** ⇒ bản vá không đổi hành vi đường bình thường.
- Chênh đúng bằng chân bán VHM: `100,34 − 92,69 = 7,65tr` và `30,64 − 22,99 = 7,65tr` — VHM bị
  cấm bán đúng như thiết kế, không mã nào khác đổi.
- `pool` ở chế độ PARTIAL = **658,70tr / 292,58tr** = **đúng bằng** pool khi sổ đã đúng hoàn toàn
  ⇒ phép hiệu chỉnh mẫu số CHÍNH XÁC, không còn dư địa over-trim.
- Thu hồi: **92,69 + 22,99 = 115,68tr / 130,98tr = 88,3%** sức mua lẽ ra có được.

Tái lập: `mike/agents/Taylor/research/park_trim_partial_reconcile_20260810.md` §Tái lập.

## Selfcheck

Phạm vi theo §23 = **mọi selfcheck import `park_holdings`/`compute_park_trim`** (`grep -rln`, 5
file) + 2 file đọc artifact `park_trim_*.json`. **6/6 PASS** với cả hai bản vá:

```
book_tagging_selfcheck.py                          PASS   (C1a–C1e mới)
mike/bin/compute_park_trim_selfcheck.py            PASS
mike/bin/compute_jit_unpark_selfcheck.py           PASS   (T07a–T07c mới, ×3 TZ)
mike/bin/corp_action_selfcheck.py                  PASS
mike/bin/compute_active_nav_selfcheck.py           PASS
mike/bin/preflight_order_invariants_selfcheck.py   PASS
```

Ca mới — **mọi ca "chặn được" đều có ca chứng minh NGƯỢC** (§24), không khẳng định suông:

| Ca | Nội dung |
|---|---|
| `C1a` | `diff>0` ⇒ vẫn `BLOCKED_RECONCILE`, 0 lệnh |
| `C1b` | `diff<0` ⇒ không chặn cả tài khoản; mã lệch bị cấm bán **dù caller không khai** `unverified_tickers` |
| `C1c` | 1 mã lệch KHÔNG chặn mã khớp — BID vẫn bán, ACB thì không |
| `C1d` | **pool PARTIAL == pool khi sổ đã đúng** (chứng minh không over-trim) |
| `C1e` | lệch mà thiếu `marketPrice` để hiệu chỉnh ⇒ quay về `BLOCKED_RECONCILE` |
| `T07a` | L2, `diff>0` ⇒ chặn |
| `T07b` | L2, `diff<0` ⇒ vẫn cấp vốn; AAA không bị bán |
| `T07c` | **chứng minh ngược**: sổ khớp thì AAA CÓ bị bán ⇒ T07b chặn thật, không phải rổ rỗng giả |

⚠️ **Phát hiện ngoài lề, KHÔNG do bản vá này**: `mike/bin/send_plan_report_park_jit_selfcheck.py`
**FAIL sẵn ở baseline** (production sạch, chưa patch) — 9 assertion chép cứng số đếm/số tiền đã
mốc (§23 hệ luận 1). Cần chủ file xử lý riêng; tôi không đụng.

## Cách áp (khi được duyệt)

```bash
cd /home/trido/thanhdt/WorkingClaude
patch -p1 --dry-run < mike/agents/Taylor/pending_park_trim_partial_reconcile_20260810/park_trim_partial_reconcile.patch
patch -p1          < mike/agents/Taylor/pending_park_trim_partial_reconcile_20260810/park_trim_partial_reconcile.patch
# §22: `git apply` exit 0 KHÔNG phải bằng chứng đã ghi file — verify độc lập:
grep -n "reconcile_partial" mike/bin/compute_park_trim.py mike/bin/compute_jit_unpark.py
for f in book_tagging_selfcheck.py mike/bin/compute_park_trim_selfcheck.py \
         mike/bin/compute_jit_unpark_selfcheck.py mike/bin/corp_action_selfcheck.py \
         mike/bin/compute_active_nav_selfcheck.py mike/bin/preflight_order_invariants_selfcheck.py; do
  python3 "$f" >/dev/null 2>&1 && echo "PASS $f" || echo "FAIL $f"; done
```

**Rollback 1 dòng**: đổi `if over:` thành `if True:` ở cả hai cổng ⇒ hành vi cũ y nguyên.

## Cổng chưa qua

| # | Cổng | Trạng thái |
|---|---|---|
| 1 | quant-skeptic CONFIRMED | ⛔ chưa |
| 2 | User/Mike duyệt — chạm đường cấp vốn LIVE của cả 2 account | ⛔ chưa |
| 3 | 1 phiên shadow (in ra, chưa đưa vào plan) | ⛔ chưa |

**Đây là sửa CƠ CHẾ AN TOÀN, không phải sửa chiến lược** — không có tham số nào được tune theo
lịch sử, không có backtest NAV nào đứng sau, nên không áp chuẩn DSR/PBO. Bằng chứng là A/B trên
đúng một ngày dữ liệu thật + 8 ca selfcheck có chứng minh ngược.
