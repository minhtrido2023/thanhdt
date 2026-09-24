# D1 — nhánh con `stock_leg_ignored` · job `Taylor_20260924_010622`

Vào: `9bf8550a` (arch-review NEEDS_CHANGES high, D1-D5) → ra: **`5f9a531d`**
Nhánh **`fix/vendor-mismatch-d1-stockleg`** · worktree `mike/wt-vendor-d1` · `git status --porcelain` **RỖNG**
**KHÔNG land.**

---

## 0. VIỆC ĐẦU TIÊN PHẢI ĐỌC — Mike dispatch TRÙNG hai job vào CÙNG worktree

Mike cảnh báo tôi ở MỤC 0 rằng nhánh của tôi là "mục tiêu đang di chuyển". Sự thật ngược lại:
**chính Mike là người làm nó di chuyển.**

| Job | Dispatch lúc | Spec | Ghi vào |
|---|---|---|---|
| `Taylor_20260924_010622` (tôi) | 01:06 | VÒNG 2 — **D1**…D5 | `wt-vendor-mismatch` |
| `Taylor_20260924_010833` | 01:08 (**2 phút sau**) | VÒNG 3 — **CHỈ** W1/W2/W3 + N1/N2 | **CÙNG** `wt-vendor-mismatch` |

Bằng chứng cơ khí, không suy diễn:
- `ps` lúc 08:14 — PID 3358736, `claude -p "[DISPATCH từ Mike | job=Taylor_20260924_010833] VÒNG 3 …"`, tuổi 02:28.
- `jobs.sh list` — **cả hai `running`** cùng lúc (`_010833` age 236s, `_010622` age 368s).
- Worktree dùng chung: lúc tôi vào (08:07) `git status` **RỖNG**; đến 08:12 xuất hiện
  `M bin/vendor_mismatch_alert.sh` (mtime 08:10:44) + `?? bin/vendor_mismatch_alert_selfcheck.sh`
  (mtime 08:12:02) — **không phải tôi viết**.
- Trong thời gian đó `agents/Taylor/exp_vendor_mismatch/k1_rows.json` **bị xoá** (có lúc 07:01, mất lúc 08:16).

**Hệ quả nghiêm trọng hơn việc tranh file: VÒNG 3 ĐÁNH RƠI D1.** Nguyên văn spec `_010833`:

> "CHỈ CÒN 3 VIỆC, tất cả ở `bin/vendor_mismatch_alert.sh`. **KHÔNG đụng
> `dividend_adjusted_return.py` / `report_return_gate.py` nữa.**"

D1 — mục Mike tự gắn nhãn **BLOCKING**, lỗ hổng công bố một khoản cổ tức KHÔNG TỒN TẠI — nằm ĐÚNG
trong 2 file đó, và VÒNG 3 **không nhắc tới nó một lần nào**. Nếu chỉ VÒNG 3 chạy, D1 biến mất im
lặng. W1/W2/W3 của VÒNG 3 = D2/D3/D4 của VÒNG 2, không hơn; D1 và D5 chỉ tồn tại ở VÒNG 2.

**Tôi đã làm gì:** rời khỏi worktree dùng chung để không tranh file với `_010833`. Cụ thể:
`git checkout --` 2 file tôi đang sửa (trả worktree về đúng trạng thái `_010833` kỳ vọng, KHÔNG
đụng 2 file của nó), dựng worktree riêng `wt-vendor-d1` từ cùng base `9bf8550a`, `git apply` bản vá
D1 vào đó, commit trên nhánh riêng. Đã ghi bus event `error/XUNG-DOT-DISPATCH hai job cung worktree`.

**Việc Mike phải làm:** merge **CẢ HAI** nhánh trước khi land —
`fix/vendor-mismatch-unverified` (D2/D3/D4 do `_010833`) + `fix/vendor-mismatch-d1-stockleg` (D1+D5).
Base chung `9bf8550a`, file rời nhau (tôi: `dividend_adjusted_return.py` + `report_return_gate.py`;
nó: `vendor_mismatch_alert.sh` + selfcheck mới + `report_return_gate_selfcheck.py:20` docstring) ⇒
merge sạch. **Một mình nhánh nào cũng KHÔNG đủ.**

### Một cái bẫy merge tôi đã chủ động tránh
Bản đầu của tôi thêm **trường thứ 8** (`reason`) vào dòng `VENDOR_MISMATCH_ALERT|…`. Nếu land cùng
bản `vendor_mismatch_alert.sh` của `_010833` — script đó đọc bằng
`while IFS='|' read -r _tag acct tk ex broker vendor published` — thì `read` **gộp mọi trường dư
vào biến CUỐI**: `published` thành `"1|stock_leg_ignored"`, `[ "$published" = "1" ]` FAIL, và cảnh
báo nói **"báo cáo vẫn gửi"** đúng lúc báo cáo đang bị **CHẶN**. Đã đổi sang **dòng TAG RIÊNG**
`VENDOR_MISMATCH_REASON|<acct>|<mã>|<ex>|<reason>|<vendor_stock>`: reader cũ neo
`^VENDOR_MISMATCH_ALERT\|` nên bỏ qua, hợp đồng 7-trường giữ **NGUYÊN BYTE**. Có assertion
(`gate_vendor_reason_routing`) + 1 check neo đúng 7 trường.

---

## 1. D1 — đã vá. Lỗ hổng, discriminator, và vì sao nó không phải hạ cấp mù

**Chuỗi `if/elif` trước bản vá** (`dividend_adjusted_return.py`, nhánh `kind == "CASH_CONFIRMED"`):
`vendor_cash <= 0` → gán nhãn **lành tính** `broker_only`, **GIỮ** `CASH_CONFIRMED` ⇒
`cash_per_share` vẫn > 0 ⇒ **CÔNG BỐ**. Ca G1 reviewer dựng:

| | giá trị |
|---|---|
| vendor `corporate_action` | `ISS` tỉ lệ 0,2604 · `value_per_share` NULL ⇒ `vendor_cash = 0` |
| solver | `CASH_CONFIRMED` **1.000đ/cp**, `share_multiplier = 1,0` |
| code cũ | `vendor_check=broker_only`, `kind=CASH_CONFIRMED`, **công bố 1.000đ/cp cổ tức không tồn tại, 0 cảnh báo** |

Vendor **NÓI THẲNG** "đây là ISS, không có tiền" và code vứt bằng chứng đó đi. Đây đúng là nhánh con
còn mở của cùng lỗ hổng chính sách 2026-09-24 — bản vá vòng trước chỉ đóng nhánh `vendor_cash > 0`.

**Trước đây LATENT nhờ lá chắn ở HÀM KHÁC**, không phải nhờ chính chỗ này: `solve_from_broker`
(a1 `credit_frame` `pre_credit`, a2 KL đổi tại ex-date) hạ sự kiện xuống `STOCK_SUSPECTED` trước.
Lá chắn đó **trượt được** — credit muộn + thiếu bản ghi `dnse_raw` ⇒ cả hai dấu hiệu im lặng. Phòng
thủ đang **BẤT ĐỐI XỨNG**: tầng vendor có bằng chứng phủ định trong tay mà không dùng.

**Discriminator — ba mảnh bằng chứng ĐANG CẦM, §29-compliant:**

```python
kind == "CASH_CONFIRMED" and vendor_cash <= 0 and vendor_stock > 0 and share_multiplier == 1.0
⇒ vendor_check = "mismatch" (reason="stock_leg_ignored") · kind = "UNVERIFIED" · gọi Winston
```

`share_multiplier == 1.0` là mảnh quyết định: nó nói **solver chưa hề biết đến chân cổ phiếu mà
vendor xác nhận** ⇒ con số nó giải ra gần như chắc chắn là **giá rơi chia tách bị đọc thành cổ tức**.
Không phải "vendor nói 0 nên hạ cấp" — đó mới là hạ cấp mù.

**CỐ Ý KHÔNG chạm** (mỗi ca có assertion CÓ TÊN, không chỉ đếm FAIL):
- `share_multiplier > 1` → solver **ĐÃ** chứng minh chân cổ phiếu bằng KL, `_cash_ratio_ref` đã trừ
  phần đó ra trước khi nhận nghiệm ⇒ chân tiền dương là hợp lệ, vendor chỉ thiếu dòng DIV.
  (`vendor_stock_leg_no_overreach`)
- `vendor_stock == 0` → vendor thiếu hẳn dòng DIV là **chuyện thường** ⇒ hạ cấp là **mất số oan**.
  (`vendor_missing_div_row_still_published` — tôi **thêm mới** assertion này, xem §3.)
- 25 ca `unavailable`, 3 nhánh `CASH_VENDOR` / `STOCK_CONFIRMED` / `broker_only`: không đổi hành vi.

**Mã lý do chuẩn hoá** `vendor_mismatch_reason ∈ {cash_mismatch, stock_leg_ignored}` — không phải
trang trí. Ở ca D1 `vendor_cash = 0`, nên câu cũ *"broker giải 1.000đ/cp vs vendor 0đ/cp — lệch
100,0%"* mời Winston hiểu **"vendor không có dữ liệu"**, trái hẳn sự thật (vendor có dữ liệu RÕ
RÀNG và đang nói sự kiện này không có tiền) ⇒ điều tra sai hướng ngay dòng đầu (§29). Cổng rẽ câu
chẩn đoán theo **mã**, không theo câu văn xuôi (§28).

---

## 2. Số đo THẬT của ĐÚNG commit cuối `5f9a531d`

Dưới `$DNA_PYEXE` (`/home/trido/thanhdt/wc_venv/bin/python`), chạy qua **3 TZ**
(`TZ=Asia/Ho_Chi_Minh` / `env -u TZ` / `TZ=Pacific/Kiritimati`) — **kết quả giống nhau cả 3**:

| Selfcheck | Vào vòng này | Ra |
|---|---|---|
| `dividend_adjusted_return.py --selfcheck` | 137/0 | **147 PASS / 0 FAIL** |
| `report_return_gate.py --selfcheck` | 66/66 | **71/71 ca** |
| `report_return_gate_selfcheck.py --root-only` | 10/10 | **10/10, rc=0** |

Pre-commit chạy thật lúc commit, **7 gate PASS / 2 skip** (skip vì không có `.sh` nào trong
changeset): shellcheck(skip) · commit-collision · discord-id · utc-text · diagnosis-evidence(skip) ·
ruff-ratchet · tz-anchor. **Không bypass, không `SKIP=`.**

### Mutation — 5/5 CHẾT bằng assertion CÓ TÊN

| # | Mutation | Assertion giết nó |
|---|---|---|
| M1 | Xoá hẳn nhánh D1 (về nguyên bản `9bf8550a`) | `vendor_stock_leg_ignored` |
| M2 | Bỏ điều kiện `share_multiplier` (hạ cấp mù) | `vendor_stock_leg_no_overreach` |
| M3 | Bỏ điều kiện `vendor_stock > 0` | `vendor_missing_div_row_still_published` |
| M4 | Cổng phát CÙNG một câu cho cả 2 mã lý do | `gate_vendor_reason_routing` |
| M5 | Xoá dòng TAG RIÊNG `VENDOR_MISMATCH_REASON` | `gate_vendor_reason_routing` |

**D5 (Mike yêu cầu xác nhận) — CÒN CHẾT trên nhánh này:** đổi `report_return_gate.py:195`
`"mismatch"` → `"MISMATCH_TYPO"` ⇒ assertion `entitled_gross_detect_mismatch`, và **runner ngoài
`report_return_gate_selfcheck.py --root-only` trả rc=1** (bản sạch rc=0). Đo bằng rc thật, không
đọc qua `tail` (`$?` sau pipe là rc của `tail`, không phải của script).

### K1 real-data — D1 là NO-OP thuần trên 6 tháng dữ liệu thật

Chạy lại `measure_k1.py` trỏ vào `wt-vendor-d1/bin` (39 mã × 2026-03-24→09-24, 62 sự kiện):

```
CASH_CONFIRMED  vendor_check=match       : 6
CASH_VENDOR     vendor_check=vendor_only : 17
STOCK_CONFIRMED vendor_check=vendor_only : 14
UNVERIFIED      vendor_check=unavailable : 25
```

**Phân bố GIỐNG HỆT master** ⇒ không mã nào mất số, không báo động giả nào sinh ra.
- Hình dạng D1 (`CASH_CONFIRMED ∧ vendor_cash≤0 ∧ vendor_stock>0 ∧ mult==1`): **0/62** ⇒ **0 dương tính giả**.
- `vendor_check == "mismatch"`: **0/62** (cửa vẫn 100% LATENT).

**ĐIỀU KIỆN LAND của Mike — báo cáo tuần thứ Sáu không mã nào mất số — GIỮ.** 6 ca `CASH_CONFIRMED`
đều `match`, gồm toàn bộ mã cổ tức của tuần: MBB 07-09 (1.000), CTG 07-23 (450), VCB 07-23 (450),
NCT 07-27 (8.000), SAB 07-28 (3.000), DGC 09-14 (8.000).

---

## 3. Hai chỗ Mike yêu cầu tôi SỬA TRONG BÁO CÁO — cả hai ĐÚNG, đã sửa

**SAI 1 — "ca đầu tiên có thể là VPB ex-date 24/09".** Nhận. VPB 2026-09-24 chỉ có chân `ISS`
(`value_per_share` NULL ⇒ `vendor_cash = 0`), nhánh mismatch cũ đòi `vendor_cash > 0` ⇒ VPB **không
bao giờ** là ca mismatch, kể cả sau khi vendor flip `announced → executed`.
**Nhưng Mike nói tiếp đúng hơn cả tôi:** đúng HÌNH DẠNG VPB (`vendor_cash=0 ∧ vendor_stock>0`) là
lỗ hổng D1 — và đó là lý do bản vá này tồn tại. Chỗ tôi sai là gọi VPB là ca *mismatch*; chỗ tôi
đúng là nói hình dạng đó thường gặp.

**SAI 2 — cột `broker=` trong `measure_k1.py` là TAUTOLOGY.** Nhận, đã xác minh bằng dòng code:
`dividend_adjusted_return.py:1036` gán `adj.per_share = adj.vendor_cash` **TRƯỚC** khi in, cho mọi
dòng `CASH_VENDOR`. Nên 17 dòng "khớp" đó **không phải** đối soát hai nguồn.
**Cơ sở bằng chứng độc lập = 6 ca `CASH_CONFIRMED`, KHÔNG phải 23.** Đã đổi nhãn cột thành
`per_share=` + ghi cảnh báo vào docstring `measure_k1.py`.
*(Bản K1 chạy lúc 08:18 đã load script trước khi tôi sửa nhãn nên log của nó còn in `broker=`;
nhãn mới áp dụng từ lần chạy sau. Số liệu không đổi.)*

---

## 4. D1-D5 có chỗ nào SAI không — NÓI THẲNG

Mike nói spec đã sai 7 lần trong tuần. Lần này **hướng D1-D5 đều ĐÚNG**, nhưng có **4 số/nhãn sai**
và **1 hệ quả bị nói NGƯỢC HƯỚNG**. Tất cả đo lại trên K1 tươi + sandbox thực nghiệm.

**[a] `broker_only` KHÔNG hề tồn tại trong dữ liệu thật — 0/62 dòng.** Mike viết *"25 ca
unavailable + họ `broker_only` được neo chống over-downgrade"*. Sai: họ `broker_only` được neo
**DUY NHẤT** bởi fixture selfcheck `a24e`, không bởi một dòng dữ liệu thật nào. Quan trọng vì nó
đổi việc phải làm: tôi **thêm assertion CÓ TÊN** `vendor_missing_div_row_still_published` cho `a24e`
(trước đó chỉ là `same()` mềm — mutation M3 chỉ ra "146 PASS / 1 FAIL", không có assertion nào
chết). Giờ M3 chết bằng tên.

**[b] VNM 2026-06-25 là `unavailable`, KHÔNG phải `broker_only`.** Mike dùng nó làm ví dụ cho họ
`broker_only`. Thật: `bq_corp_action` trả rỗng ⇒ `vendor_check = unavailable`, `kind = UNVERIFIED`.
Và "broker 1.850" cũng không chính xác: 1.850 là **ước lượng tỉ số tầng 1**, `cash_per_share = 0`,
**chưa từng được công bố**. Hai nhãn khác nhau đi hai nhánh code khác nhau — tôi vẫn giữ nguyên ý
Mike (không hạ cấp khi `vendor_stock == 0`) vì ý đó đúng, chỉ ví dụ là sai nhãn.

**[c] "14/62 sự kiện" → hình dạng D1 lân cận đúng là **12/62**.** 14 là tổng `STOCK_CONFIRMED`;
2 trong đó (**TCM 2026-05-25** cash 500 + stock 0,05; **ACB 2026-06-15** cash 700 + stock 0,13) là
sự kiện HỖN HỢP thật, `vendor_cash > 0`. Không đổi kết luận, đổi con số.

**[d] D2 — chiều (a)+(b) CONFIRMED bằng thực nghiệm, KHÔNG phải đọc code.** Sandbox `/tmp/vma_sb`
(copy script + stub `notify_thread.sh`/`append_event.sh`, không post thật), chạy bản **committed
`9bf8550a`**:

| Ca | Đo được |
|---|---|
| `NOTIFY_RC=7` (notify tạch), state sạch | rc=10 · **stderr RỖNG** (bị `2>/dev/null` nuốt) · state **VẪN ghi** `{"rep.md":"2026-09-24"}` ⇒ **de-dup chặn lần sau = MẤT CẢNH BÁO** |

Đúng nguyên văn Mike. Fix (a)+(b) là bắt buộc.

**[e] D2 chiều (c) — hệ quả của state CỤT bị nói NGƯỢC HƯỚNG.** Spec VÒNG 3 (W2) viết: *"lần sau
`json.load` nổ và **script chết trước khi cảnh báo được gì**"*. Đo thật với state cụt (`{"a":`) +
notify OK:

> rc=**10** · `append_event` **ĐÃ gọi** · `notify_thread` **ĐÃ gọi** · state giữ nguyên cụt

Script **KHÔNG chết** — `set -uo pipefail` **không có `-e`**, nên `$(python3 -c …)` hỏng chỉ trả
chuỗi rỗng, `ALREADY=""`, script đi tiếp và **cảnh báo bình thường**. Hệ quả thật của state cụt là
**SPAM mỗi lượt** (de-dup không bao giờ bám được), **không phải im lặng**. Vẫn nên vá atomic (§5)
vì nó chặn state cụt từ gốc — nhưng **sai hướng hậu quả ⇒ sai mức ưu tiên**: đây là lỗi ồn, không
phải lỗi mất cảnh báo. Lỗi mất cảnh báo là [d], và nó nằm ở chiều (a) chứ không phải (c).
*(Cái thật đáng vá ở ca này theo §29: stderr hiện ra là **traceback Python trần**, không phải câu
chẩn đoán — bản in-flight của `_010833` đã thêm câu thật, đúng hướng.)*

**D3 — ĐÚNG, không sửa gì.** Script 88 dòng chưa từng đi qua gate nào là vấn đề thật.
**D4 — ĐÚNG, và tiền đề kiểm được:** `state/report_delivery_incomplete_alerted.json`
(`check_report_cadence.sh:61`) thật sự **không TTL, không chủ dọn** ⇒ tiền lệ "tăng vô hạn có chủ ý"
là có thật, không phải Mike nhớ sai. Cả D3 và D4 do `_010833` sở hữu (W3/N2) — tôi **không** viết
chồng.

**Một điểm Mike tự nhận sai, tôi xác nhận reviewer đúng:** K2 `rc=2` là lỗi argparse
(`main()` chỉ nhận `--report`), nên cổng **chưa từng chạy** và "byte-identical" chỉ là hai thông
điệp usage. Bằng chứng NO-OP thật nằm ở **K1** (0 mismatch / 62 sự kiện — tôi đã chạy lại trên
nhánh D1, xem §2), không ở K2.

---

## 5. VIỆC LÀM SAU — ghi nhận, KHÔNG sửa ở nhánh này

Nguyên văn V1-V4 của Mike, cộng 2 mục tôi thấy thêm khi làm D1:

- **V1** `position_total_return()` — đường CLI một-mã KHÔNG chạy đối soát vendor lần nào.
- **V2** Miền cổ tức NHỎ ~90-300đ/cp (DRI/SCL/TV1) chưa test với `ABS=1,0đ`; 6 ca neo đều ≥450đ/cp
  (đã xác nhận trên K1: thấp nhất là CTG/VCB 450). Ở miền đó ABS chi phối, tổng dung sai ~1%.
- **V3** Nợ cũ cổng §21: `report_return_gate.py:535` unmatched · F2 bảng không cột KL · F3 văn xuôi
  dạng câu (`:217 PROSE_RE`) · F4 bảng chỉ có VND không có % ⇒ rc=0 không chặn.
- **V4** Bảng công bố lãi/lỗ bằng VND tuyệt đối không có % ⇒ cổng §21 không phủ; dòng TỔNG kỳ vọng
  trừ mất khoản đó không chú thích.
- **V5 (tôi thêm)** `R1` của vòng 2 vẫn là mục đáng làm sớm nhất và **bản vá D1 làm nó nặng thêm**:
  `dividend_adjusted_return.py` `except Exception: return None` ⇒ BQ hỏng không phân biệt được với
  "không có sự kiện". Detector mới cũng dựa vào `vendor_stock` ⇒ **BQ hỏng là D1 tắt im lặng** y như
  nhánh cũ. Cần `vendor_check="error"` riêng. 25/62 sự kiện đang `unavailable` — không ai biết bao
  nhiêu trong đó là LỖI.
- **V6 (tôi thêm)** `share_multiplier == 1.0` là so **float tuyệt đối**. Hiện an toàn (chỉ được đặt
  bởi `max(float(p["multiplier"]))` từ KL nguyên, hoặc giữ default `1.0`), nhưng nếu về sau có
  nguồn nào đặt `share_multiplier = 1.0000000001` thì guard **im lặng tắt**. Nếu muốn chắc:
  `abs(share_multiplier - 1.0) < 1e-9`. KHÔNG sửa ở nhánh này vì chưa có nguồn nào như vậy —
  ghi lại để không phải phát hiện lại.

---

## 6. Trạng thái để Mike quyết

| Mục | Ai | Trạng thái |
|---|---|---|
| **D1** nhánh con `stock_leg_ignored` | tôi | **XONG** `5f9a531d`, nhánh `fix/vendor-mismatch-d1-stockleg` |
| **D5** xác nhận coupling mutant còn chết | tôi | **XONG** (assertion + runner rc=1) |
| SAI 1 / SAI 2 sửa lại trong báo cáo | tôi | **XONG** (§3) |
| **D2** fail-silent `vendor_mismatch_alert.sh` | `_010833` (W1/W2) | in-flight — tôi đã **đo xác nhận** chiều (a), **bác hướng hệ quả** của (c) |
| **D3** selfcheck cho script 88 dòng | `_010833` (W3) | in-flight (`vendor_mismatch_alert_selfcheck.sh` mtime 08:12) |
| **D4** khai chủ dọn state | `_010833` (N2) | in-flight — tiền lệ `SWEEP_ALERTED_STATE` đã kiểm, có thật |

**KHÔNG TỰ LAND.** Cần Mike **merge cả hai nhánh** rồi mới land — một mình nhánh nào cũng thiếu.
Không đụng file production nào trong khung 08:45-09:30 ICT: toàn bộ việc nằm trong worktree
`wt-vendor-d1`, không ghi vào `data/` hay `reports/`.
