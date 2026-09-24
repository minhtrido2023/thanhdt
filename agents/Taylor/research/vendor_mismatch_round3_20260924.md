# vendor-mismatch — VÒNG 3 (job Taylor_20260924_010833)

**Nhánh** `fix/vendor-mismatch-unverified` · worktree `mike/wt-vendor-mismatch`
**HEAD** `e8d86b18` (3 commit: `592c52cf` W1+W2+N2 · `cc9bcd52` W3 · `e8d86b18` N1)
**CHƯA LAND** — chờ arch-review vòng 3 + Mike/user.
Phạm vi: CHỈ `bin/vendor_mismatch_alert.sh` + selfcheck mới + 1 dòng docstring. KHÔNG đụng
`dividend_adjusted_return.py` / `report_return_gate.py`.

## Số đo (ĐO SAU KHI COMMIT, `git status --porcelain` RỖNG)

| Bộ | Kết quả |
|---|---|
| `vendor_mismatch_alert_selfcheck.sh` (MỚI) | **39/39 PASS × 4 TZ**, **4/4 mutant bị giết bằng assertion CÓ TÊN** |
| `dividend_adjusted_return_selfcheck.py` (hồi quy) | **137 PASS / 0 FAIL × 4 TZ** |
| `report_return_gate.py --selfcheck` (hồi quy) | **66/66 ca × 4 TZ** |
| `report_return_gate_selfcheck.py --root-only` | PASS |
| Consumer: `check_report_cadence_selfcheck.py` / `eod_delivery_wiring_selfcheck.py` / `eod_trading_report_account_filter_selfcheck.py` | rc=0 · 9/9 · 15/0 |
| pre-commit | shellcheck_gate + diagnosis_evidence_gate + ruff + tz_anchor: **Passed**, không SKIP |

4 TZ = TZ thường · `env -u TZ` · `Pacific/Kiritimati` · `America/New_York`.

## W1 — fail-silent (ĐÃ SỬA)
(a) de-dup state chỉ ghi SAU KHI `notify_thread.sh` trả 0; hỏng ⇒ KHÔNG ghi ⇒ lượt sau thử lại.
(b) bỏ `2>/dev/null` trên CẢ HAI kênh, in LỖI THẬT ra stderr (§29).
(c) phân tầng: `append_event` hỏng = nêu lỗi rồi ĐI TIẾP (bus là kênh phụ); `notify_thread` hỏng
= KHÔNG được coi là đã cảnh báo.

## W2 — ghi state không atomic (ĐÃ SỬA) — nhưng đề bài THIẾU một nửa
tmp + `fsync` + `os.replace`, dọn tmp khi lỗi.
⚠️ **Sửa đúng như W1 mô tả (chỉ nhánh GHI) thì CA 3 của chính W3 vẫn TRƯỢT.** Nhánh ĐỌC de-dup
(`json.load` ở :62) cũng nổ trên JSON cụt — và nó chạy TRƯỚC khi gửi, nên state hỏng làm câm
cảnh báo qua đúng cái đường W2 định vá. Đã sửa cả hai: nhánh đọc fail-open về phía GỬI + nêu lỗi
parser thật; nhánh ghi dựng lại từ `{}` nếu state cũ hỏng (thà mất de-dup còn hơn mất cảnh báo).

## W3 — selfcheck (ĐÃ VIẾT) — và một lỗ trong chính đề bài W3
`bin/vendor_mismatch_alert_selfcheck.sh`. Sandbox `$TMP/mike/bin/` + **symlink chính script thật**
⇒ `ROOT=dirname($BASH_SOURCE)/..` trỏ vào sandbox ⇒ state/ và 2 lời gọi side-effect đều rơi vào
STUB. Chạy đúng code production, không monkeypatch, không post thật.

Đủ 4 ca bắt buộc (1/2/3/4) + 2b (bus hỏng, Discord sống) + 5 (`published=0`) + 6 (`--dry-run`).

⚠️ **Mutation mà W3 yêu cầu chỉ phủ W1, KHÔNG phủ W2.** Đảo (a) thì CA 2 chết — đúng. Nhưng đảo
W2 về `json.dump(state, open(path,'w'))` thì **toàn bộ bộ ca vẫn XANH**: đếm rác `.tmp` không
phân biệt được atomic với không-atomic. Nên W2 sẽ nằm đó KHÔNG CÓ TEST. Đã thêm **CA 7**: shim
`python3` trên PATH giết tiến trình ĐÚNG lúc đã ghi dở nội dung nhưng CHƯA `os.replace` — mô
phỏng kill thật, không vá code sản xuất. Mutant m3 chết ở đúng assertion đó.

4 mutant, mỗi cái chạy TRỌN bộ ca (`SC_TARGET_SRC`) và chỉ tính là **bị giết** khi bộ ca FAIL ở
ĐÚNG assertion CÓ TÊN mong đợi — rc≠0 trơn (crash/syntax error/ca khác fail) KHÔNG tính:

| Mutant | Assertion giết nó |
|---|---|
| m1 ghi state vô điều kiện dù notify hỏng | `MUTATION-GUARD vendor_alert_no_state_on_notify_fail` |
| m2 nuốt stderr của notify (`2>/dev/null`) | `stderr mang LỖI THẬT của notify (§29)` |
| m3 ghi state không nguyên tử | `MUTATION-GUARD vendor_alert_atomic_state_write` |
| m4 bus hỏng chặn luôn đường Discord | `bus hỏng KHÔNG chặn đường tới user` |

Mutation **BẬT MẶC ĐỊNH**: `run_selfchecks.sh` tự dò `*selfcheck*.sh` và chạy KHÔNG THAM SỐ — để
mutation sau một cờ opt-in là nó không bao giờ chạy trong lượt tuần (cả bộ ~3s). Lượt CON tự tắt
nhờ `SC_TARGET_SRC` (chống đệ quy). `--no-mutations` để chạy riêng bộ ca.

## N1 (ĐÃ SỬA) · N2 (CHỌN PHƯƠNG ÁN "chấp nhận", có căn cứ)
N1: docstring `report_return_gate_selfcheck.py:20` sửa thành đúng sự thật — file NÀY là runner của
bộ assertion nhúng (`:163`), bỏ nó khỏi `run_selfchecks.sh` là bộ đó ngừng chạy mà không ai báo.

N2: khai ở header script rằng `state/vendor_mismatch_alerted.json` **tăng không trần, CÓ CHỦ Ý**,
KHÔNG cài cron dọn. Căn cứ: (1) tốc độ tăng đo thật ~0 — K1 đếm **0 lệch nguồn / 62 sự kiện cổ
tức 6 tháng**, key chỉ sinh khi có lệch THẬT; (2) tiền lệ y hệt `state/report_delivery_incomplete_alerted.json`
(`check_report_cadence.sh:61`) cũng không TTL/không chủ dọn — đã `grep -rl` xác nhận nó xuất hiện
ở ĐÚNG 1 file, không có pruner nào. **KHÔNG** thêm dòng vào `kb/cron_registry.md`: bảng đó là
bảng CRON JOB, file state này không phải cron job — thêm vào là làm bẩn đúng cái registry §11 bảo vệ.

## PHẢN BIỆN — W1/W2/W3 có chỗ nào sai?

1. **W1 đánh giá THẤP phạm vi.** Đề bài nói mất cảnh báo vĩnh viễn ở nhánh sweep
   (`check_report_cadence.sh:91`). Nhưng nhánh `eod_trading_report.sh:72` chạy MỘT LẦN mỗi lượt
   sinh báo cáo EOD và cũng không bao giờ quay lại file đó ⇒ mất vĩnh viễn trên **CẢ HAI** đường,
   không chỉ sweep.
2. **Đề bài không nói gì về mã thoát, và đó là chỗ dễ sửa sai.** Tôi GIỮ `exit 10` cả khi notify
   hỏng, đổi ĐỊNH NGHĨA trong header: 10 nói về **SỰ TỒN TẠI của lệch nguồn**, không hứa "đã gửi
   được". Lý do: hai caller dùng `-eq 10` để quy ĐÚNG nguyên nhân/người xử lý (§29) — đổi sang mã
   khác mà không sửa đồng thời cả hai caller thì thông điệp tới user tụt về câu chung chung
   "delivery chưa đủ kênh", tức tái lập đúng lỗi §29 mà nhánh này sinh ra để sửa. **Khuyến nghị:
   ĐỪNG tách mã thoát** ở vòng này; muốn tách thì phải sửa 2 caller trong cùng một thay đổi.
3. **W2 thiếu nhánh ĐỌC** (mục W2 ở trên) — sửa đúng chữ của đề bài thì CA 3 của đề bài trượt.
4. **W3 thiếu mutation cho W2** (mục W3 ở trên) — W2 sẽ không có test nào nếu làm đúng chữ.
5. Ngoài phạm vi, ghi lại để không mất: hợp đồng dòng máy đọc dùng `IFS='|'`; nếu về sau một
   trường nào đó của marker chứa `|` thì parse lệch im lặng. Hiện các trường đều là enum/số đã
   chuẩn hoá nên rủi ro thấp — **không sửa trong vòng này**, chỉ nêu.
