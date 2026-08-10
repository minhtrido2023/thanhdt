# REFRESH_SKIP chết cứng khi trần participation binding — chẩn đoán + fix

**Job** `Taylor_20260810_042759` · 2026-08-10 · file `trading_bot/executor.py`
**Trạng thái**: fix đã nằm trong working tree (có hiệu lực ở lần restart kế tiếp), **CHƯA COMMIT** —
lý do ở §7, cần Mike quyết.

---

## 1. Kết luận 1 dòng

Root cause Mike nêu (**race giữa 2 lần `get_quote()`**) **KHÔNG phải nguyên nhân** — nó bị chặn bởi
TTL cache 3s của broker và, kể cả nếu xảy ra, cũng không giải thích được dữ liệu. Nguyên nhân thật
là **`_would_be_unchanged()` đếm chính lệnh con sắp huỷ như quota của người khác**: nó gọi
`_child_qty()` mà không trừ phần *reservation* của lệnh đó trong `self.shared`, trong khi huỷ thật
thì `_release_child()` nhả reservation ra **trước** khi `_place_slices()` tính KL mới. Hệ quả tất
định: **khi trần participation là ràng buộc binding, REFRESH_SKIP không bao giờ kích được.**

## 2. Bác bỏ giả thuyết race 2-quote (bằng chứng, không phải ý kiến)

| Bằng chứng | Nội dung |
|---|---|
| `brokers.py:254` / `:377` | `self._quote_ttl = 3.0` — `get_quote()` có TTL cache 3s cho **cả** `DNSEBroker` lẫn `PHSBroker`. Journal cho thấy `_cancel_stale` 09:23:**15** và `_place_slices` 09:23:**16** ⇒ cách nhau ~1s ⇒ gần như luôn trả về **cùng một object Quote**. |
| `executor.py:1116-1124` | `_extreme_regime()` **đã có** wrapper memoize `(ticker, now)` với docstring nói thẳng: hai đường đi trong cùng 1 chu kỳ phải nhất quán. Tức tác giả đã nhận diện đúng lớp vấn đề này và đã xử lý cho phần *stateful*; phần bị bỏ sót là `self.shared`. |
| `_child_qty` docstring | Ghi rõ ý định: "Hai call-site thật … đều truyền `now` để hai đường đi tính ra **CÙNG một KL**". Bug là vi phạm ý định đã tuyên bố, không phải đánh đổi có chủ ý. |
| Định lượng | Kể cả nếu quote lệch thật, muốn đổi KL thì `round_lot(int(0,10×day_volume))` phải vượt ranh giới 100cp ⇒ cần **1.000cp khớp trong <1 giây** trên DRI (mã UPCOM khớp ~2.300cp **cả buổi sáng**). Trong khi đó độ lệch do reservation là **đúng 200cp**, tất định, mọi chu kỳ. |

→ Trả lời câu hỏi 1 của dispatch (*có lý do CHỦ Ý nào để 2 chỗ gọi `get_quote()` riêng không?*):
lý do là **TTL cache 3s đã làm cho lần gọi thứ hai gần như miễn phí và gần như luôn đồng nhất**, và
chỗ duy nhất mà gọi-hai-lần thật sự nguy hiểm (bộ đếm 2-poll của EXTREME) **đã** được memoize riêng.
Không cần refactor "1 snapshot/chu kỳ" — và quan trọng hơn: **refactor đó KHÔNG sửa được bug này**
(xem §3, allowance vẫn = 26 < 1 lô dù dùng chung 1 quote y hệt).

## 3. Root cause thật

`self.shared[ticker]` = KL fleet **đã khớp + đang TREO** (`seed_shared`, executor.py:253-265).
Khi `_cancel_stale` chạy, lệnh con vẫn `status="open"`, chưa `released` ⇒ 200cp của **chính nó** vẫn
nằm trong `shared`. `_would_be_unchanged` gọi `_child_qty` ⇒

```
fleet_filled = shared["DRI"] = 200          # ← chính lệnh sắp huỷ
allowance    = int(0,10 × day_volume) − 200
```

Còn `_place_slices` chạy **sau** khi `_release_child()` đã trừ 200 ⇒ `fleet_filled = 0`.
Hai đường đi đứng trên hai sổ khác nhau.

**Khi trần participation binding** (`qty == round_lot(10%×day_volume)`), theo định nghĩa
`int(0,10×dv) − qty ∈ [0, 100)` ⇒ **luôn < 1 lô** ⇒ `_child_qty` trả `0` ⇒ `qty < LOT` ⇒ `False`
⇒ CANCEL_STALE. Không phải "gần như vô hiệu" mà là **P = 0 tuyệt đối** trong chế độ binding.

### Tái lập số học từ journal thật (7/7 chu kỳ khớp chính xác)

`ratio` trong note journal = `remaining / day_volume` ⇒ back-out được `day_volume`. Với
`remaining = 2800` (KL plan DRI), `qty = round_lot(int(0,10 × day_volume))` tái lập **đúng cả 7**
giá trị KL đã đặt:

| Giờ | ratio (journal) | day_volume suy ra | KL đúng | KL journal | KL đường KIỂM TRA (bug) |
|---|---:|---:|---:|---:|---:|
| 09:15 | 127,19% | 2.201 | 200 | **200** ✓ | — |
| 09:23 | 123,40% | 2.269 | 200 | **200** ✓ | 226−200 = 26 → **0** |
| 09:31 | 108,21% | 2.588 | 200 | **200** ✓ | 258−200 = 58 → **0** |
| 09:39 | 105,84% | 2.646 | 200 | **200** ✓ | 264−200 = 64 → **0** |
| 09:47 | 92,36% | 3.032 | 300 | **300** ✓ | (đổi thật 200→300, huỷ ĐÚNG) |
| 09:55 | 91,48% | 3.061 | 300 | **300** ✓ | 306−300 = 6 → **0** |
| 10:03 | 90,62% | 3.090 | 300 | **300** ✓ | 309−300 = 9 → **0** |

### Đối chứng nội tại trong CÙNG journal (mạnh hơn mọi lập luận)

Cùng phiên, cùng cơ chế, **POW và SSI vẫn REFRESH_SKIP bình thường** (09:39, 09:47, 09:55, 10:03).
Khác biệt duy nhất: chúng thanh khoản dày ⇒ allowance **không** binding (`min(remaining, by_value)`
mới là ràng buộc) ⇒ trừ 2.800 reservation vẫn còn dư ⇒ hai đường đi ra cùng KL.
POW còn cho thấy **cả hai chế độ trên cùng một mã trong một buổi sáng**: CANCEL_STALE lúc 09:23 và
09:31 (lúc `0,1×dv` còn nhỏ, binding sau khi trừ), rồi REFRESH_SKIP từ 09:39 (khi `dv` đủ lớn).
Đó là chữ ký của **ràng buộc participation**, không phải của một race thời gian.

⚠️ **Đính chính số liệu trong dispatch** (đếm đủ cả buổi sáng, tới 11:27 khi phiên sáng đóng):
"cả 15 chu kỳ sáng nay đều CANCEL_STALE, KHÔNG lần nào REFRESH_SKIP kích hoạt" — đúng **cho riêng
DRI** nhưng không đúng ở mức hệ thống. Con số chính xác:

| Mã | CANCEL_STALE | REFRESH_SKIP | Ghi chú |
|---|---:|---:|---|
| DRI | **16** | **0** | trong 16 lần huỷ, **10 lần là lãng phí** (đặt lại y hệt giá **và** KL); 6 lần còn lại KL đổi thật (200→300→700→800→900→1500→1700) nên huỷ là ĐÚNG |
| POW | 2 | **14** | 2 lần huỷ đầu (09:23, 09:31) là lúc allowance còn binding sau khi trừ reservation |
| SSI | 0 | **16** | thanh khoản dày, chưa bao giờ binding |

Giá DRI đứng nguyên **13.000đ** ở cả 16 chu kỳ (trần cứng), nên chỉ KL mới quyết định.
⇒ Thiệt hại thật của bug: **10 lần mất chỗ xếp hàng FIFO vô ích** trên mã mỏng nhất trong plan.
Chi tiết POW/SSI không làm nhẹ bug — chính nó là chìa khoá chẩn đoán: nếu cơ chế hỏng toàn cục
thì POW/SSI đã không skip được 30 lần.

## 4. Fix

`trading_bot/executor.py`, 3 chỗ, không đổi chữ ký công khai nào:

```python
def _child_qty(self, o, ps, q, px, exclude_reserved=0):
    ...
    fleet_filled = self.shared.get(o.ticker, 0) - exclude_reserved   # ×2 nhánh (ADV20 + day_volume)
```
```python
# _would_be_unchanged: mô phỏng đúng thứ tự "huỷ (release) rồi mới đặt"
reserved = 0 if c.get("released") else c["qty"] - c.get("filled", 0)
qty = self._child_qty(o, ps, q, px, exclude_reserved=max(0, reserved))
```

**Tại sao KHÔNG chọn cách "1 snapshot quote/chu kỳ"** (đề xuất trong dispatch): (a) nó không sửa
được bug (§2); (b) `_place_slices` xử lý nhiều mã trong 1 lần gọi nên cache phải per-ticker, và
memo hoá một quote `None`/lỗi cho cả chu kỳ sẽ **xấu hơn** hành vi hiện tại (mất cơ hội retry trong
cùng chu kỳ); (c) `executor.py` là module lõi đang chạy tiền thật — mở rộng blast radius để đổi lấy
một rủi ro tồn dư đã đo là hiếm + lành tính thì không đáng (§2/§3 coding_guidelines).

**Bất biến an toàn được giữ**: chỉ trừ reservation **của chính lệnh đó**, không trừ của account
khác ⇒ trần participation fleet-wide không bị nới. Có test chứng minh ngược (§5, ca C1').

### Rủi ro tồn dư (đã đo, công bố thẳng)
Nếu quote lệch **vượt ranh giới lô** đúng giữa lần kiểm tra và lần đặt, `_cancel_stale` sẽ giữ lệnh
theo snapshot lúc kiểm tra ⇒ KL cũ trễ **1 chu kỳ (8 phút)** so với KL tối ưu. Sai lệch tối đa
**±1 lô**, và luôn theo hướng **thấp hơn hoặc bằng** trần participation (không bao giờ vượt quota).
Ca F2 trong selfcheck ghim đúng hành vi này để nó không âm thầm đổi sau này.

## 5. Verify

**Selfcheck mới**: `refresh_skip_participation_selfcheck.py` — **31/31 PASS**, 7 nhóm A–G.
Mỗi ca "giữ được lệnh" đều kèm **ca chứng minh ngược** (chạy lại đúng nhánh cũ và xác nhận nó
*thật sự* huỷ), theo tiền lệ §24.

- **A** tái lập ca DRI 09:23 nguyên bản → REFRESH_SKIP; A1' chứng minh nhánh cũ trả 0.
- **B** không nới lỏng: KL đổi thật (200→300), giá đổi, đã khớp một phần, chưa quá 8' → vẫn xử như cũ.
- **C** bất biến fleet: chỉ trừ 200 của mình; C1' chứng minh trừ nhầm cả fleet sẽ giữ lệnh **sai**.
- **D** mã thanh khoản dày → cũ và mới ra **cùng** KL (regression byte-identical).
- **E** nhánh ADV20-paced (CAPIT/DISCRETIONARY): cả `floor_allow` lẫn `ceil_allow` cùng bệnh, cùng khỏi.
- **F** giả thuyết race: lệch trong cùng lô → vẫn skip; lệch vượt lô → ghim hành vi tồn dư.
- **G** end-to-end `_cancel_stale` + `_place_slices`: 0 huỷ/0 đặt; G3/G4 chứng minh nhánh cũ đẻ ra
  đúng cặp `CANCEL_STALE` + `PLACE` với **cùng 200cp @ 13.000đ** — trùng khít journal thật.

**Mutation test** (bắt buộc để test không tautology): revert đúng 1 dòng fix → **10/31 FAIL**.

> **Đính chính của chính tôi** (do quant-skeptic bắt được, 2026-08-10): bản đầu báo cáo ghi
> "34/34 PASS" và "10/34 FAIL" — sai, số ca thật là **31**. Tôi ghi con số đó theo ước lượng thay vì
> đếm (`grep -c '\[PASS\]'` = 31). Nội dung kỹ thuật không đổi; reviewer đã tự chạy lại toàn bộ và
> ra đúng 31/31 + 10/31.

**Độc lập môi trường** (§19 `verify-before-done`): PASS ở cả 4 biến thể —
`env -u TZ`, `TZ=UTC`, `TZ=America/New_York`, và cả `python3` hệ thống lẫn `$DNA_PYEXE`.
Selfcheck **không** đọc TZ hệ thống (mọi mốc thời gian là `datetime` naive tự dựng), không chạm
mạng/BQ/broker thật, chỉ ghi trong `tempfile.TemporaryDirectory()`. Đặt
`MIKE_BOT_TEST_MODE=1` theo §5b.

**Quét rộng §23** (executor.py = module lõi; `bin/selfcheck_scope_map.sh` liệt kê 14 selfcheck phụ
thuộc, trong đó 1 là chính file này): chạy lại **TRÊN NỀN SẠCH HEAD `024d5ca`** (sau khi gỡ tạm phần
HYBRID chưa duyệt ra `git stash`, xem §7) — **13/13 PASS, rc=0**: `refresh_skip_participation` (31/31)
+ `book_tagging`, `capit_lever`, `capit_participation_cap`, `churn_guard`, `dcf_check`,
`discretionary_participation_cap`, `extreme_regime`, `ghost_order`, `hard_no_chase_ceiling`,
`paper_main_window`, `t2_settlement`, `tick_retry`.

Cái thứ 14 — `hybrid_fill_timing_selfcheck.py` — **KHÔNG chạy được trên nền sạch và cố ý không chạy**:
nó test code HYBRID đang nằm ngoài git (chưa duyệt). Nó đã PASS trên bản gộp trước đó, và bản gộp đó
được khôi phục nguyên trạng vào working tree ở §7 bước cuối. Không tuyên bố gì thêm về nó.

Kiểm phụ thuộc môi trường (§16/§19): `refresh_skip_participation_selfcheck.py` PASS cả với `env -u TZ`
và `TZ=America/New_York`; `churn_guard_selfcheck.py` PASS với `TZ=UTC`.

## 6. Vì sao bộ test cũ không bắt được (bài học, không phải trách móc)

`churn_guard_selfcheck.py` — selfcheck sinh ra **đúng để bảo vệ REFRESH_SKIP** ("churn eliminated on
constant quote") — hardcode `day_volume=5_000_000` (dòng 54). Allowance ⇒ 500.000cp, **không bao giờ
binding**. Tức nó phủ đúng chế độ mà bug **không** biểu hiện, và pass 100% suốt thời gian bug sống.

→ Bài học tổng quát hoá được: **một guard có tham số ràng buộc thì test phải phủ CẢ chế độ ràng buộc
đó binding, không chỉ chế độ thoải mái.** Chọn một hằng số "rộng rãi cho tiện" trong fixture chính là
cách vô hiệu hoá bài test mà không ai thấy. (Cùng họ với §23 hệ luận 1, nhưng khác cơ chế: không phải
fixture *mốc theo thời gian*, mà fixture *chọn sai chế độ*.)

## 7. Tách commit — ĐÃ THỰC HIỆN (Mike chọn phương án (b), job `Taylor_20260810_050211`)

Bối cảnh khi soạn bản đầu: `trading_bot/executor.py` + `config.py` đã có sẵn thay đổi chưa commit
trước khi tôi bắt đầu — bản triển khai **HYBRID fill-timing** (job `Taylor_20260810_034544`, +~240
dòng, kèm `hybrid_fill_timing_selfcheck.py` chưa track, thư mục
`pending_paper_enable_hybrid_fill_20260810/`). Commit chung sẽ cuốn phần chưa duyệt vào git như thể
đã duyệt — đúng loại tai nạn `context_pack.md` ghi nhận tối 08-07.

**Đính chính bản đầu (Mike tự đọc lại `hybrid_fill_timing_implementation_20260810.md` §6 và bắt
đúng):** tôi viết "quant-skeptic đã REFUTED 2 lần" là **thiếu vòng 3**. Thực tế HYBRID có **3 vòng:
REFUTED → REFUTED-high → CONFIRMED-medium**. Lý do tách vẫn đứng vững nhưng phải nêu cho đúng: sau
vòng 3 CONFIRMED còn **một bản vá throttle (`extreme_defer_poll_sec`) CHƯA qua quant-skeptic** — đó
mới là phần chưa review, không phải cả khối HYBRID.

**Đã làm (phương án (b) — tách sạch):**
1. Sao lưu bản gộp: `git diff` → `/tmp/wip_hybrid_plus_fix_20260810.patch` (436 dòng, md5
   `bcf0bf339c9c266a35c3e7e640fdab6a`).
2. `git stash push -- trading_bot/executor.py trading_bot/config.py` (KHÔNG `git checkout` — giữ được
   đường lùi).
3. Viết lại **chỉ 3 chỗ sửa REFRESH_SKIP** trên HEAD sạch `024d5ca`. Khác bản gộp đúng một điểm:
   `_child_qty` **không có** tham số `now` (tham số đó là của HYBRID) ⇒ chữ ký committed là
   `_child_qty(self, o, ps, q, px, exclude_reserved=0)`. Selfcheck cũng bỏ đối số `NOW` truyền theo vị
   trí; `exclude_reserved` luôn truyền dạng **keyword** nên bộ test chạy đúng trên **cả hai** nền (khi
   HYBRID quay lại, `now=None` ⇒ không có trần hybrid ⇒ cùng kết quả).
4. Chạy lại toàn bộ trên nền sạch: 31/31 + 12 selfcheck lõi khác, xem §5. **Không** ship code chưa
   test tại chỗ.
5. Commit **chỉ** phần fix (executor.py + selfcheck + báo cáo này).
6. Khôi phục HYBRID vào working tree **nguyên trạng uncommitted** (`git checkout stash@{0} --` thay
   cho `stash pop`: pop sẽ conflict vì stash chứa cả phần fix nay đã nằm trong git; checkout-từ-stash
   đặt lại đúng byte nội dung gộp ban đầu, không cần giải conflict thủ công).

**Trạng thái sau khi xong:** fix REFRESH_SKIP nằm trong git history; HYBRID + bản vá throttle vẫn
uncommitted, **chưa được duyệt, không đổi gì về quyết định bật/tắt**. `fill_timing_hybrid_enabled`
vẫn `False` và `pending_paper_enable_hybrid_fill_20260810/` vẫn treo chờ user.

**Vận hành:** fix có hiệu lực ở lần restart kế tiếp (Python nạp từ working tree). Vì working tree
được khôi phục về bản gộp, lần restart đó vẫn nạp luôn code HYBRID (default OFF) — không đổi so với
trước job này.

## 8. Ranh giới đã giữ
Không restart bot, không đụng lệnh treo thật, không sửa `trading_rules.json`. Chỉ sửa code + thêm
selfcheck; commit **duy nhất** phần fix đã CONFIRMED, không commit phần HYBRID chưa duyệt.
