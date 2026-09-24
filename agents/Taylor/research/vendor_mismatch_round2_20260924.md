# fix/vendor-mismatch-unverified — VÒNG 2 (V1/V2/V3)

Job `Taylor_20260924_005111` · nhánh `fix/vendor-mismatch-unverified` · worktree `mike/wt-vendor-mismatch`
Vào: `4beb093e` (NEEDS_CHANGES high) → ra: **`9bf8550a`**. `git status --porcelain` RỖNG. **KHÔNG land.**

## Commit
| SHA | Mục | Nội dung |
|---|---|---|
| `29a6e5a5` | V1+V2 | test cho CHÍNH `entitled_gross` + nối bộ assertion nhúng vào runner |
| `bdd9888d` | V3 | dòng máy đọc + `bin/vendor_mismatch_alert.sh` + wire 2 shell caller |
| `9bf8550a` | V2 (siết) | vỏ bộ nhúng đòi SỐ CA thật, không nhận `rc=0` trơn |

## Số đo (committed HEAD, chạy dưới CẢ `env -u TZ` LẪN `TZ=Pacific/Kiritimati`, `$DNA_PYEXE`)
| | kết quả |
|---|---|
| `dividend_adjusted_return.py --selfcheck` | **137 PASS / 0 FAIL** |
| `report_return_gate.py --selfcheck` | **66/66** (vào vòng 2 là 60) |
| `report_return_gate_selfcheck.py --root-only` | **10/10** (vào vòng 2 là 7), 0,8s |
| acceptance end-to-end (E1) | **17/17 PASS**, 3 ca |
| lân cận §23 | eod_delivery_wiring 9/9 · check_report_cadence 27/27 · report_delivery_gate 12/12 · eod_account_filter 15/15 |

## Mutation TỰ BẮN LẠI trên HEAD sạch — 4/4 CHẾT
| Mutation | Trước vòng 2 | Sau |
|---|---|---|
| Xoá khối `if a.vendor_check == "mismatch"` (`report_return_gate.py:195-197`) | SỐNG (137+60 vẫn xanh) | **CHẾT** — `AssertionError: MUTATION-GUARD entitled_gross_detect_mismatch` |
| Bỏ `continue` sau `mismatches.append` (`:197`, M-A2) | SỐNG | **CHẾT** — `MUTATION-GUARD entitled_gross_mismatch_excluded` |
| Xoá dòng máy đọc `VENDOR_MISMATCH_ALERT` | (mới) | **CHẾT** — 2 FAIL, 64/66 |
| Thay lời gọi bộ nhúng bằng hằng số `(0, "…0/0 ca")` | SỐNG ở bản vá đầu của tôi | **CHẾT** sau `9bf8550a` |

> ⚠️ Nit về số dòng: reviewer gọi khối đó là `:193-196`; trên `4beb093e` nó thật sự ở **`:195-197`**
> (`:193-194` là chốt `_qty_at`). Không đổi nội dung yêu cầu — chỉ ghi lại để lần sau bắn mutation
> đúng dòng ngay từ đầu.

## V1 — làm gì
3 check + 2 MUTATION-GUARD chạy **thân hàm `entitled_gross` thật**, patch TẦNG DƯỚI
(`dar.resolve_dividends` / `dar.broker_qty` / `dar._qty_at`), **không** patch `entitled_gross`.
Rổ 5 sự kiện: (1) mismatch đã bị hạ UNVERIFIED · (2) match → phải vào `out` · (3) ex-date > asof →
bỏ · (4) không nắm giữ → bỏ · (5) **phòng thủ nhiều tầng**: giả định `dar` hồi quy để nguyên
`CASH_CONFIRMED` cho một sự kiện lệch nguồn (`cash_per_share` > 0) ⇒ cổng VẪN phải loại. Ca (5)
chính là cái giết M-A2 — không có nó thì bỏ `continue` vô hại vì tầng dưới đã hạ cấp hộ.

## V2 — làm gì
`run_embedded_selfcheck()` trong `report_return_gate_selfcheck.py`, chạy ở **cả `--root-only`**
(offline, 0,8s cả file) ⇒ 66 assertion nhúng hết tàng hình với cả 2 runner.
Một khác biệt CÓ CHỦ Ý so với phần còn lại của file: bộ nhúng chạy bản **nằm cạnh file selfcheck**
(`dirname(__file__)`), không phải `REAL_BIN`. Các test ROOT cố ý kiểm bản canonical ("bản canonical
có chạy được từ worktree không"); bộ nhúng hỏi "logic trong CÂY NÀY có đúng không" — chạy nó trên
canonical thì thay đổi đang phát triển trong worktree **không bao giờ được kiểm** (đo thật: bản đầu
của tôi trỏ `REAL_BIN` in ra `53/53` của cây canonical trong khi worktree đang là `63/63`).

## V3 — làm gì
1. `report_return_gate.py` in thêm dòng MÁY ĐỌC cạnh khối văn xuôi:
   `VENDOR_MISMATCH_ALERT|<acct>|<mã>|<ex>|<broker>|<vendor>|<đang_công_bố>` — giá trị đã chuẩn
   hoá, shell KHÔNG grep câu văn xuôi (§28). In cho **cả ca rc=0**.
2. `bin/vendor_mismatch_alert.sh` (mới): stdin → parse marker → de-dup 1 lần/file/ngày
   (`state/vendor_mismatch_alerted.json`, đúng khuôn `ALREADY_ALERTED`) → `append_event` +
   `notify_thread` với nguyên nhân thật + **Winston (data-ops)**. `exit 10` = có lệch nguồn.
   `--dry-run` để acceptance chạy được mà không bắn thật.
3. `eod_trading_report.sh::_deliver_eod` + `check_report_cadence.sh` sweep: capture output delivery
   gate (vẫn in nguyên văn ra ngoài để log không đổi), bơm vào helper ở **cả hai nhánh rc**. Dòng
   "Delivery INCOMPLETE" chọn thông điệp theo **bằng chứng** (`vendor_rc=10` ⇒ Winston), không phát
   một câu cố định (§29).
Cổng giữ **thuần** — không ghi bus từ trong gate (§5b).

## V1/V2/V3 có chỗ nào SAI không — nói thẳng
**Không. Cả 3 đều đúng và tái lập được**; tôi tự bắn lại từng mutation reviewer nêu và xác nhận
chúng SỐNG trước khi sửa. Bốn ghi chú, không cái nào bác bỏ yêu cầu:
1. **Số dòng `:193-196`** thực ra là `:195-197` (xem nit ở trên).
2. **V2 còn một lỗ reviewer không nêu** mà tôi tự tìm ra khi bắn mutation lên chính bản vá của
   mình: `rc=0` trơn không phân biệt "66 ca đều qua" với "không chạy ca nào". Đã siết ở `9bf8550a`.
3. **V3 sửa cả dòng "cần Taylor kiểm tra"** — reviewer chỉ ra nó SAI NGƯỜI nhưng không yêu cầu sửa
   câu chữ; tôi sửa vì để nguyên thì user vẫn nhận đúng một thông điệp sai người mỗi lần chặn.
4. **`report_delivery_ledger_selfcheck.py` FAIL 5/40 khi chạy từ worktree** — **KHÔNG phải do tôi**:
   dựng `git worktree` ở đúng commit cha `4beb093e` và chạy CÙNG file (`cmp` xác nhận y hệt byte)
   → cũng 35/40 FAIL với cùng 4/5 tên test; cây canonical 40/40 PASS. Là tật của selfcheck đó khi
   chạy ngoài cây canonical (nó đòi ROOT = cây đang chạy, trong khi script cố ý ghim canonical),
   có từ trước. KHÔNG sửa ở nhánh này.

## E2 — đọc "latent" cho đúng
Ca VPB 24/09 không đi qua cửa này (chỉ 1 chân ISS, không chân DIV; `event_status=announced` mà
`bq_corp_action` lọc `executed` ⇒ vendor rỗng) ⇒ cửa **vẫn 100% LATENT**. Nhưng trong chính rổ K1
có **2 sự kiện hỗn hợp THẬT**: TCM 2026-05-25 (cash 500 + stock 0,05) và ACB 2026-06-15 (cash 700 +
stock 0,13) — cả hai trước go-live nên broker không giải được. **"Latent" ở đây là may mắn về THỜI
ĐIỂM, không phải hiếm về bản chất**: vừa-tiền-vừa-cổ-phiếu là chuyện thường trong rổ này.

## VIỆC RIÊNG — ghi nhận, KHÔNG sửa ở nhánh này
- **R1** `dividend_adjusted_return.py:421-422` `except Exception: return None` ⇒ lỗi BQ không phân
  biệt được với "không có sự kiện", rồi `:969-970` khẳng định "không có sự kiện executed nào" (§29).
  Hệ quả cho CHÍNH chính sách mới: **một lần BQ hỏng là detector TẮT IM LẶNG**. Đang có 25/62 sự
  kiện ở `unavailable` — không ai biết bao nhiêu trong đó là LỖI. Đề xuất: thêm
  `vendor_check="error"` riêng. **Đây là việc ĐÁNG LÀM SỚM NHẤT trong 5 mục.**
- **R2** Cổng chỉ phủ vị thế ĐANG GIỮ; mismatch trên mã đã bán trước `asof` không bao giờ nổi lên.
- **R3** `unmatched += 1; continue` (:527-529) + `nocover` lọc `g>0` (:584-586) vẫn MỞ nguyên.
  ⚠️ LIVE với VPB: ISS cho `cash_per_share=0` ⇒ `g=0` ⇒ `nocover` bỏ qua VPB; cổng chỉ phủ qua
  đường bảng `(mã, KL)` mà KL vừa đổi 1.100 → 1.386.
- **R4** Ứng viên call-site mới, CHƯA dựng ca: `bin/verify_account_snapshot.py` nhận biết
  corp-action qua `data/corp_actions.json` `_status=CONFIRMED` — cơ chế KHÁC HẲN
  `credit_frame`/`classify_qty_residual`. Đêm broker credit sớm mà `auto_confirm` (19:25) chưa
  CONFIRMED thì multiplier=1 trong khi KL broker đã nhân.
- **R5** ĐÃ ghi: `kb/projects/cash-vendor-gate-tracking.md.proposed` (§13, chờ Mike duyệt) — mốc
  09-13 đã qua và dữ liệu đủ điều kiện dispatch đối soát mở rộng, NHƯNG K1=0/6-khớp-từng-đồng nói
  **không có cơ sở nới**; hỗn hợp **8** (khớp reviewer), ISS thuần 56 (tôi) vs 46 (reviewer) — lệch
  do khác cửa sổ/`event_status`, không đổi kết luận. `cash_per_share` KHÔNG bị chạm ⇒ bus question
  mở cổng `CASH_VENDOR` vẫn **MỞ**.

## Tái lập
```bash
cd /home/trido/thanhdt/WorkingClaude/mike/wt-vendor-mismatch
env -u TZ $DNA_PYEXE bin/report_return_gate.py --selfcheck                 # 66/66
env -u TZ $DNA_PYEXE bin/report_return_gate_selfcheck.py --root-only       # 10/10
env -u TZ $DNA_PYEXE bin/dividend_adjusted_return.py --selfcheck           # 137/0
env -u TZ $DNA_PYEXE ../agents/Taylor/exp_vendor_mismatch/acceptance_v3_endtoend.py "$PWD"  # 17/17
```
