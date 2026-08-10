# HYBRID fill-timing — triển khai vào executor (paper-gated, mặc định TẮT)

**Job**: `Taylor_20260810_034544` · **Owner**: Taylor · **Ngày**: 2026-08-10
**Yêu cầu**: John (thread 1521735922066919515) qua Mike — *"thiết kế + viết logic thực thi HYBRID
vào executor.py, paper-gated, mặc định TẮT, live cần duyệt riêng"*.
**Nguồn thiết kế (KHÔNG backtest lại)**: `research/twap_vs_window_execution_20260804.md` §6+§10
(job `Taylor_20260804_124836`, 663 phiên độc lập, nến 15', 33 mã ta thật sự giao dịch).

---

## 0. Kết luận 1 đoạn

Đã viết xong cơ chế, **mặc định TẮT**, **không đụng LIVE**. Điều đáng báo nhất **không phải** là
code chạy được, mà là **diễn tập paper bắt được một lỗ hổng thiết kế mà bản thân tôi đã bỏ sót**:
bản đầu tiên chỉ đặt **trần khối lượng theo block** — chạy trên PaperBroker thật thì **58% khối
lượng lệnh MUA vẫn đi ra TRƯỚC 11:00**, đúng vào khung sáng đắt nhất, và chân BÁN vẫn gom về mở
cửa. Lý do: `fill_timing_outside_mult` chỉ **làm chậm** (8'→32') chứ **không dừng** — lệnh cứ 32
phút lại rỉ ra một slice. Trần KL một mình **không thực thi được lịch**. Phải thêm cổng hoãn
`_hybrid_defer` mới ra đúng lịch. Nếu chỉ chạy unit-test theo mốc block (như tôi làm trước đó) thì
tất cả đều PASS và lỗ hổng này đi thẳng vào paper.

---

## 0b. Vòng quant-skeptic thứ nhất: **REFUTED** — 2 lỗi thật, đã vá

Bản nộp lúc 11:06 ICT bị quant-skeptic **REFUTED (confidence medium)** lúc **04:11:49Z**. Đây là
phần đáng giá nhất của job: reviewer **không đọc-thấy-hợp-lý mà chạy code thật** (dựng `Executor`
thật, gọi thẳng hàm) và tái lập được **2 lỗi giao thoa** mà bộ selfcheck cũ — vốn kiểm từng cờ
**độc lập** — không thể chạm tới. Cả hai đều nằm đúng vào **hai điểm tôi tự tuyên bố là "đã kiểm,
không xung đột"** ở §3. Bài học: *ca kiểm bật-một-cờ không bao giờ chứng minh được giao thoa
hai-cờ; phải có ca bật ĐỒNG THỜI.*

**Lỗi (1) — HYBRID bóp lệnh BÁN khẩn cấp của EXTREME_regime.** `EXTREME_DOWN` armed sinh lệnh
bán-về-sàn khẩn; cửa sổ BÁN của HYBRID (09:15-10:15) **trùm lên** đúng khoảng đó. Tái lập: nhịp bị
**chậm 1,875×** so với nền 1.0× trước khi có HYBRID, và trần block cắt KL còn
`ceil(8000/3)=2600` thay vì xả trọn 8000. Tức là **HYBRID làm lệnh khẩn chậm hơn cả thời chưa có
HYBRID** — phản lại đúng docstring "không xung đột" của chính nó. Suýt bị bỏ qua vì chiều MUA thật
sự vô hại (`EXTREME_PAUSE` đã dừng mua) và tôi đã suy rộng kết luận của chiều MUA sang chiều BÁN.

> **Vá**: thêm `_extreme_armed(o, now)` vào `_hybrid_bypass`. `_extreme_armed` tách riêng để đọc
> **state đã armed**, KHÔNG gọi quote lại ⇒ gọi được từ mọi chỗ, và là **nguồn duy nhất** dùng
> chung cho cả `_extreme_slice_mult` lẫn cổng bypass (không thể lệch nhau).
> Ca kiểm mới **O1a-O1e**, gồm ca **chứng minh ngược** O1e (`extreme_regime_enabled=False` ⇒ state
> armed KHÔNG mở bypass, nhịp về lại 1,875×) — để "chặn được" không phải khẳng định suông.

**Lỗi (2) — cache gap-override trễ đúng 1 tick.** `_last_gap_override` **chỉ** được nạp trong
`_place_slices`, nhưng trong cùng một `step()` thì **`_cancel_stale` chạy TRƯỚC** — nên nhánh
`_cancel_stale → _would_be_unchanged → _child_qty` đọc dict **của tick trước**. Ở tick chuyển
trạng thái, hai đường tính ra hai KL khác nhau ⇒ **huỷ + đặt lại thừa 1 lần**, mất ưu tiên FIFO vô
ích. Đây đúng là thứ mà chính §3 tuyên bố đã phòng (cùng truyền `now`) nhưng chỉ phòng được nửa:
`now` thì cùng, **state đọc từ dict** thì không.

> **Vá**: tách điều kiện ra **hàm thuần** `_gap_override_active(o, now)` — tính thẳng từ
> `_gap_z_cache` + giờ, **không đọc `_last_gap_override`**; cả hai đường đi đều gọi nó nên **không
> còn phụ thuộc thứ tự gọi trong `step()`**. Dict giữ nguyên vai trò cũ (nguồn ghi chú journal
> `GAP_OPEN_OVERRIDE`) nên không mất thông tin vận hành.
> Ca kiểm mới **O2a-O2g**: O2a mô phỏng đúng nhánh `_cancel_stale` chạy trước (dict CHƯA nạp),
> O2d khẳng định hai đường ra **cùng một KL** ở cùng tick, O2f là ca chứng minh ngược.

**Ba mục "narrative" reviewer nêu, đã sửa nốt**: số ca selfcheck (báo 66/66, thực tế reviewer đếm
81/81 — thành **93/93** sau khi thêm 12 ca O1/O2, và **99/99** sau 6 ca P ở §0c);
`selfcheck_scope_map.sh` trả **13** selfcheck
chứ không phải 12; và file báo cáo này lúc đó **chưa tồn tại** trong repo dù đã được trích dẫn là
tài liệu bắt buộc đọc (nay đã có, chính là file bạn đang đọc).

**Không có blast radius**: cả 2 lỗi chỉ hiện khi bật **đồng thời hai cờ** mà **cả hai đều đang mặc
định TẮT**; không có phiên LIVE hay paper nào từng chạy đường code này.

---

## 0c. Vòng quant-skeptic thứ hai: **REFUTED (confidence HIGH)** — lỗi thứ 3, nặng hơn cả 2 lỗi trước

Bản đã vá 2 lỗi trên **vẫn bị bác**, và lần này là lỗi **do chính bản vá vòng 1 sinh ra**. Đây là
kết quả đáng giá nhất của cả job, nên ghi đủ:

**Lỗi (3) — deadlock khởi động: EXTREME không bao giờ ARM được trong lúc đang HOÃN.**
Cổng `_hybrid_bypass` đọc `_extreme_armed`, mà `_extreme_armed` chỉ True nếu `_extreme_state` đã
được nạp — và đường **DUY NHẤT** nạp nó là lời gọi `_extreme_regime` nằm **PHÍA DƯỚI** trong
`_place_slices`. Nhưng `_hybrid_defer` `continue` **TRƯỚC** đó. `_cancel_stale` cũng không cứu
được: nó chỉ poll lại cho lệnh **đã có con đang mở**, thứ mà lệnh bị hoãn **không bao giờ có**.

> Vòng 1 vá *"armed mà không bypass"*. Bản vá đó mở một lỗ mới: **"không bao giờ armed được"** —
> và đây là lỗ **nặng hơn**: đóng băng **0 lệnh** thay vì lệnh-bị-bóp-nhưng-vẫn-sống.

Reviewer tái lập bằng code thật: lệnh **BÁN cắm sàn từ mở cửa**, HYBRID bật ⇒ **0 lệnh** và
`_extreme_state=None` suốt **09:00-09:15**; cùng kịch bản với HYBRID tắt ⇒ **xả trọn 8000 ngay
09:00**. Tức HYBRID **tệ hơn hẳn nền cũ** đúng vào cửa sổ nguy hiểm nhất (gap-down ở mở cửa) —
phản lại chính khẳng định tiêu đề của §0b.

**Vì sao 93/93 không bắt được, và đây mới là bài học thật**: ca O1 **nạp thẳng**
`_extreme_state` (already-armed) rồi kiểm bypass. Nó trả lời "armed thì có bypass không?" nhưng
**không bao giờ hỏi "làm sao nó armed được?"**. *Ca kiểm nạp tay trạng thái sẽ mù đúng cái cơ chế
tạo ra trạng thái đó.* Cùng họ với bài học ở §0: unit-test theo mốc thì xanh, chạy đường thật mới
lòi.

> **Vá**: poll `_extreme_regime` **TRƯỚC** khi hoãn (chỉ khi `extreme_regime_enabled`), rồi **hỏi
> lại** `_hybrid_defer` — vừa arm xong thì bypass mở, rơi xuống đặt lệnh bình thường như nền cũ.
> An toàn khỏi **đếm-đôi** bộ đếm 2-poll: `_extreme_regime` đã memoize theo `(ticker, now)` nên
> poll thêm ở đây và lời gọi phía dưới trong CÙNG chu kỳ chỉ tính 1 lần (có ca kiểm P5).

**Ca kiểm mới P1-P6** — viết theo đúng khuyến nghị reviewer, đi **đường thật** (`_place_slices`
theo từng tick 09:00→09:14), **KHÔNG nạp tay state**:

| Ca | Nội dung |
|---|---|
| P1 | **Nền** (hybrid TẮT) xả được 8000 trong 09:00-09:15 — mốc so sánh, không phải giả định |
| P2 | EXTREME **arm được** dù đang trong khoảng hoãn (`n=2`, `until` có giá trị) |
| P3 | HYBRID **không được tệ hơn nền** — cũng xả được |
| P4 | Xả **đủ KL** như nền (8000 = 8000), không bị trần block cắt |
| P5 | **Không đếm-đôi** bộ đếm 2-poll (memoize còn hiệu lực) |
| P6 | **CHỨNG MINH NGƯỢC**: ngày thường ⇒ **VẪN hoãn** trước 09:15 — bản vá chỉ mở đường cho lệnh KHẨN, không vô hiệu hoá lịch trải |

**Ca P đã được chứng minh là BẮT ĐƯỢC lỗi, không phải chỉ xanh cho đẹp**: gỡ bản vá ra (neuter
đúng 1 dòng điều kiện) rồi chạy lại ⇒ **P2/P3/P4 FAIL** với đúng chữ ký reviewer mô tả
(`state=None`, `hybrid=0` vs `nền=8000`); lắp lại ⇒ xanh. Đây là điều kiện cần để gọi một ca kiểm
là hồi quy thật (skill `verify-before-done`).

---

## 0d. Vòng quant-skeptic thứ ba: **CONFIRMED** (medium) — cơ chế đứng vững, còn 1 chi phí thật

Reviewer **tự chạy lại** thay vì tin báo cáo: 99/99 khớp chính xác, `extreme_regime_selfcheck` +
`churn_guard_selfcheck` PASS, và **trace tay** `_place_slices`/`_cancel_stale`/`_extreme_regime`
xác nhận bản vá §0c đúng về logic: hai đường poll thao tác trên **tập lệnh rời nhau** trong cùng
`step()` (`_place_slices` bỏ qua lệnh có con đang mở; `_cancel_stale` chỉ xử lý lệnh CÓ con đang
mở) ⇒ memoize `(ticker, now)` mà bản vá dựa vào **không thể bị đếm đôi**. Reviewer cũng tự xác
minh biến `interval` tính trước lời gọi poll là **stale-nhưng-vô-hại** (chỉ dùng khi
`ps["children"]` khác rỗng — không bao giờ đúng với lệnh còn đang hoãn).

**Nhưng CONFIRMED ở mức *medium*, vì một chi phí tôi hỏi mà chính tôi không đóng** (điểm (c) trong
prompt vòng 3): bản vá §0c mở lại đường `get_quote` **mỗi chu kỳ 20s cho mỗi lệnh đang hoãn**.
`PHSBroker.get_quote` chỉ cache **TTL 3s** < `poll_interval_sec=20` ⇒ gần như mọi chu kỳ đều là
một lời gọi mạng thật.

**Tôi đã ĐO thay vì ước lượng** (`_place_slices` theo chu kỳ 20s, 09:00→11:00):

| Cấu hình | get_quote/phiên (10 lệnh MUA) |
|---|---|
| Nền trước HYBRID | **10** (1/lệnh) |
| HYBRID + bản vá §0c, **không** throttle | **3.600** |
| HYBRID + throttle 60s (**đang dùng**) | **120** |

**Reviewer nói đúng một điểm tôi đã kiểm sai lúc đầu**: tôi tra `secrets/trading_bot_accounts.json`
ở **tầng gốc** và kết luận "không account nào bật `extreme_regime_enabled`". Sai — cờ nằm trong
khối **`overrides`**, và paper `main` **đã bật sẵn** `extreme_regime_enabled: true` *và*
`gap_adaptive_enabled: true`. Tức là **ngay khi patch paper được áp, `main` chạy cả hai cờ cùng
lúc** — chi phí trên rơi ngay, không phải giả định.

> **Vá**: throttle poll **theo TICKER** (không theo lệnh — nhiều lệnh cùng mã trong 1 chu kỳ nay
> chỉ tốn 1 quote) bằng knob mới `extreme_defer_poll_sec` (**mặc định 60s**, đặt `0` = tắt
> throttle). Bộ đếm 2-poll-confirm **không cần** độ phân giải 20s ⇒ đánh đổi: **arm chậm nhất
> ~2 phút** để đổi lấy tải API **về đúng bậc độ lớn cũ** (giảm 30×). Throttle chỉ sống trong
> nhánh HOÃN — đường đặt lệnh thường không đổi một dòng nào.
> Ca kiểm **Q1-Q6**, trong đó **Q2 cố ý tái lập lại chính sự cố** (tắt throttle ⇒ 3.600 lời gọi)
> để con số này là **đo được**, không phải lời hứa; **Q5** chứng minh throttle **không tái sinh
> deadlock** (vẫn arm + xả trọn 8000); **Q6** là ca chứng minh ngược.

**Còn tồn dư, nói thẳng**: throttle là bản vá của TÔI **sau** vòng 3, nên chưa qua quant-skeptic
lúc viết đoạn này. Nó đã được review riêng ở vòng 4 — và **bị bác** (§0e).

---

## 0e. Vòng quant-skeptic thứ tư (chỉ throttle): **REFUTED (high)** — lỗi thứ 4, cùng họ deadlock

*Log: `mike/logs/verify_20260810_051022_2683275.log` (REFUTED) → vá → `verify_20260810_052344_2696911.log`
(**CONFIRMED high**, vòng 5). Job `Taylor_20260810_051847`.*

**Lỗi**: throttle đóng dấu `self._extreme_defer_poll[o.ticker] = now` **TRƯỚC** khi kiểm
`q_ext.ok()`. `PHSBroker.get_quote` (`brokers.py:297`) `return None` khi có exception — hành vi
**đã có sẵn trong code**, không phải giả thuyết. Nên **một** lần quote lỗi "tiêu" trọn cửa sổ 60s
mà bộ đếm 2-poll-confirm **không nhích một bước nào**. Dưới chuỗi lỗi lặp đúng nhịp 60s (cộng
hưởng với chính throttle), lệnh BÁN khẩn kẹt **sạch** cửa sổ hoãn — đúng deadlock vòng 2 (§0c),
chỉ khác lối vào: vòng 2 là "không có lời gọi poll nào", vòng 4 là "có lời gọi nhưng lời gọi lỗi
cũng bị tính là đã poll". Reviewer tái lập trên `Executor` thật với broker stub luôn trả `None`,
chạy đúng cửa sổ BÁN 09:00–09:15 nhịp 20s: **15 lần thử, `_extreme_state` = None, 0 lệnh đặt**.

**Vì sao không ca nào bắt được**: `FakeBroker.get_quote` của toàn bộ selfcheck **không bao giờ
lỗi**. Cả bộ Q (viết riêng cho throttle) cũng chạy trên broker luôn thành công ⇒ nhánh hỏng chưa
từng được chạm. Đây là bài học lặp lại của §0c dưới dạng khác: ca kiểm chứng minh được cơ chế
**hoạt động**, nhưng không ca nào ép nó **thất bại**.

**Bản vá (1 dòng, đúng đề xuất của reviewer)**: chuyển dòng đóng dấu **vào trong** nhánh
`if q_ext is not None and q_ext.ok():` — chỉ đóng dấu khi poll **thành công**; lần lỗi được thử
lại ngay chu kỳ sau.

> **Vì sao không chọn "backoff ngắn 5–10s cho lần lỗi"** (phương án 2 reviewer nêu): `_place_slices`
> chỉ được gọi mỗi `poll_interval_sec` = **20s**, nên **mọi** backoff <20s cho ra **đúng một** hành
> vi — "thử lại chu kỳ sau" — chỉ khác là thêm 1 knob làm người đọc tưởng có thể tinh chỉnh. Đóng
> dấu-khi-thành-công đạt cùng kết quả, ít code hơn, và nói đúng ngữ nghĩa: throttle giãn nhịp POLL
> **đã đo được giá**, không giãn nhịp **THỬ**.

**Trần chi phí không đổi**: quote lỗi liên tục ⇒ thử lại mỗi chu kỳ = **đúng nhịp nền trước khi có
throttle** (không tệ hơn), và khi ấy đường đặt lệnh thường cũng đang `NO_QUOTE` — không tồn tại
tình huống "HYBRID kẹt mà nền chạy được".

**11 ca R mới** (`hybrid_fill_timing_selfcheck.py`, tổng file 105 → **116/116 PASS**):

| Ca | Nội dung |
|---|---|
| R1/R1b/R1c | quote lỗi **cộng hưởng** đúng nhịp throttle 60s ⇒ vẫn arm (09:01:20, có TRẦN ≤3') + xả đủ 8000 |
| R2 | **cơ chế**: poll LỖI **không** đóng dấu throttle (assert thẳng vào nguyên nhân gốc, không chỉ triệu chứng) |
| R3 | quote lỗi 100% ⇒ thử lại **mỗi chu kỳ** (45/45), không bị throttle khoá |
| R3b | **chứng minh ngược**: broker chết ⇒ nền (HYBRID TẮT) **cũng** 0 lệnh ⇒ lỗi là của broker, không phải HYBRID tệ hơn nền |
| R4 | **chứng minh ngược**: quote bình thường ⇒ throttle **vẫn cắt** (3/45), bản vá không vô hiệu hoá throttle |
| R5 ×4 | chập chờn từng phần (xen kẽ 1/2, 2/3, 3/4, 4/5) ⇒ arm lúc 09:01:40 / 09:01:40 / 09:02:20 / **09:03:00** — xuống cấp **mượt**, luôn có trần (vòng 5 yêu cầu bổ sung) |

**Đã chứng minh bộ R thật sự phân biệt được** (không phải ca trang trí): tạm đảo ngược đúng 1 dòng
về thứ tự cũ ⇒ **5/7 ca R FAIL** (R1 `armed_at=None`, R2 `stamp` có entry, R3 `15/45`), rồi khôi
phục bản vá. Vòng 5 reviewer **tự làm lại đúng thí nghiệm này** và ra cùng kết quả.

**Quét rộng §23 chạy lại SAU khi sửa code** (không tin lần quét trước): `bin/selfcheck_scope_map.sh
trading_bot/executor.py` = **14 selfcheck**, chạy lại toàn bộ ⇒ **14/14 rc=0, 0 dòng FAIL**.

**Còn nợ (không chặn, vòng 5 đề nghị)**: mọi bằng chứng hiện tại là mô phỏng `FakeBroker`. Sau khi
bật paper, bắt **1 phiên 09:00–09:15 có lỗi quote PHS thật** rồi đối chiếu thời điểm arm với trần
~2' ở trên.

---

## 1. Lịch block — lấy ĐÚNG số đã đo, không tự chia đều

| Chiều | Block (nhãn nến 15') | Số block | mean vs day-VWAP | t | sd |
|---|---|---|---|---|---|
| MUA | 11:00 · 11:15 · 13:00 · 13:15 · 13:30 | 5 | **−6,94 bps** | −6,80 | 26,3 |
| BÁN | 09:15 · 09:30 · 09:45 · 10:00 | 4 | **+8,89 bps** | 4,64 | 49,4 |

**Đây không phải "chia đều N điểm trong khoảng"** — đó là điểm dễ làm sai nhất. Hai kiểm chứng:

1. **Tái lập số**: trung bình cộng các block trong bảng §2 báo cáo gốc ra **chính xác** con số §6:
   BUY `(−3,53 −7,37 −12,21 −7,74 −3,87)/5 = −6,944`; SELL `(9,27+9,06+9,38+7,88)/4 = 8,8975`.
   Nếu tôi chia đều 5 điểm theo đồng hồ trong "11:00-13:30" thì sẽ rơi vào 11:37/12:15/12:52 —
   **giờ HOSE nghỉ trưa (11:30-13:00), thị trường đóng cửa**, và không tái lập được số nào.
2. **Không phải chọn-sau-khi-nhìn-bảng**: cực trị của bảng là 13:00 (−12,21 bps), KHÔNG nằm ở đầu
   hay cuối dải block; dải block được lấy nguyên khối liền mạch quanh vùng rẻ, không cắt tỉa để
   đẹp số. Bằng chứng ổn định của dải này đã có sẵn từ nghiên cứu gốc: cùng dấu **4/4 năm**,
   **30/33 mã**, và **mọi** nhóm điều kiện phiên (kể cả nhóm ngày lặng, nơi hiệu ứng hướng phiên
   bị khử).

---

## 2. Cơ chế — 3 lớp, mỗi lớp giải quyết đúng 1 thất bại đã quan sát được

| Lớp | Hàm | Giải quyết cái gì | Bằng chứng buộc phải có lớp này |
|---|---|---|---|
| 1. **Hoãn ngoài block** | `_hybrid_defer()` | lệnh rỉ ra ngoài khung thuận lợi | diễn tập paper bản chỉ-có-trần: 58% KL MUA đi trước 11:00 (§0) |
| 2. **Trần KL theo block** | `_hybrid_block_cap()` | "trải" chỉ trên giấy | checkpoint `Taylor_20260804_091703`: **151/153 lệnh khớp TRỌN trong 1 slice** ⇒ đổi riêng interval là NO-OP |
| 3. **Nhịp 1 slice/block** | `_hybrid_mult()` | 1 block 15' nuốt 2 slice (mặc định 8') | số học: `interval = 8' × 1,875 = 15'` |

**Trần KL** = `ceil(remaining / blocks_left)`, tối thiểu 1 lô. Ba tính chất cố ý:
- **tự sửa sai** — lỡ block nào (thiếu quote / WAIT_CASH / không ai bán) thì phần dư dồn sang các
  block sau (đo: lỡ 11:00+11:15 ⇒ 13:00 đặt `ceil(5000/3)=1667` → làm tròn lô **1600**, không phải 1000);
- **block cuối hết trần** (`blocks_left=1` ⇒ `None`) — đi nốt, không để lại đuôi;
- **sàn 1 lô** — lệnh 300cp chia 5 block ⇒ trần 100cp, không bao giờ sinh lệnh 0.

**Cổng hoãn TỰ KẾT THÚC** — chỉ hoãn khi `blocks_left > 0`. Hết cửa sổ (MUA sau 13:45 / BÁN sau
10:15) ⇒ **không bao giờ hoãn nữa**, phần dư chạy bình thường suốt phần còn lại của phiên + quét
ATC như cũ. Trần hoãn tối đa: MUA ~09:15→11:00, BÁN ~09:00→09:15. **Không có kịch bản kẹt hàng vì
lịch** — có ca kiểm chứng minh trực tiếp (§4, ca N').

**Cổng bật/tắt** (`_hybrid_active`) dùng lại **đúng bộ cổng sẵn có** của layer fill-timing, không
thêm tầng thứ hai: `fill_timing_enabled` ∧ `fill_timing_hybrid_enabled` ∧ `urgency != "high"` ∧
`¬(fill_timing_live_gate ∧ mode != "paper")`. Tắt master `fill_timing_enabled` ⇒ cờ hybrid **bị bỏ
qua hoàn toàn** (fail-safe theo chiều an toàn: về uniform, không có đường nào lọt).

---

## 3. Ranh giới — cái gì KHÔNG đổi

- **Không phá/thay cơ chế fill_timing hiện có.** HYBRID là **một chế độ** của cùng layer; cờ TẮT ⇒
  `_fill_timing_mult` chạy đúng nhánh cũ (kiểm bằng ca A, gồm cả nhánh "phiên chiều 13:00+ = 1.0").
  Checkpoint fill_timing đang chờ ETA 08-14/08-17 **không bị đụng tới**.
- **LIVE byte-identical.** `fill_timing_live_gate=True` (mặc định) ⇒ mọi hàm HYBRID trả về giá trị
  trung tính khi `mode="live"` — có ca kiểm riêng cho cả 3 hàm quyết định.
- **Không đụng**: allocator, chọn mã, sizing, `hard_no_chase_ceiling_vnd`, participation cap
  (ADV20 + realized), T+2 sellable cap, EXTREME-regime, gap-adaptive, `_atc_sweep`.
- **`_child_qty(now=None)`** giữ chữ ký cũ hoạt động y nguyên — mọi caller ngoài (selfcheck) không
  truyền `now` thì không có trần.

**Giao thoa đã kiểm, không né:**
- *gap-adaptive*: đặt HYBRID **sau** override down-gap ⇒ override vẫn thắng; và khi override đang
  bật thì **bỏ cả trần lẫn hoãn** (tốc độ đã được quyết ở tầng trên, trải lệnh sẽ đá nhau).
- *EXTREME*: ~~chiều MUA vốn đã `EXTREME_PAUSE` ⇒ không xung đột, rủi ro tồn dư ~0~~ — **KHẲNG ĐỊNH
  NÀY SAI, quant-skeptic tái lập được** (xem §0b). Chiều **BÁN** khẩn *nằm trong* cửa sổ BÁN
  09:15-10:15 nên **bị chính HYBRID bóp**: nhịp chậm 1,875× và trần KL cắt còn ~1/3 phần dư. Nay
  đã vá bằng `_hybrid_bypass` (EXTREME armed ⇒ HYBRID tạm ngưng hoàn toàn).
- *`_would_be_unchanged`*: **cùng truyền `now`** nên hai đường tính ra CÙNG KL — nếu chỉ một bên áp
  trần thì mỗi chu kỳ đều thấy "khác" và huỷ+đặt lại, mất ưu tiên FIFO vô ích. Có ca kiểm.
  ⚠️ Điều kiện gap-override phải đọc qua **hàm thuần** `_gap_override_active`, KHÔNG đọc dict
  `_last_gap_override` — xem §0b lỗi (2).

**Nguyên tắc rút ra, áp cho mọi layer thực thi sau này:** HYBRID là tối ưu **chi phí**
(~0,1-0,3%/năm); **mọi tầng RỦI RO đều thắng nó, không có ngoại lệ**. Cổng `_hybrid_bypass` là chỗ
DUY NHẤT biểu diễn luật đó, và cả 3 hàm quyết định (`_hybrid_mult`/`_hybrid_defer`/
`_hybrid_block_cap`) đều phải đi qua nó — thiếu một hàm là hở một lối.

---

## 4. Kiểm chứng đã chạy (không phải đọc-thấy-hợp-lý)

**`hybrid_fill_timing_selfcheck.py` — 116/116 PASS** (81 ca bản đầu + **12 ca O1/O2** §0b +
**6 ca P** §0c + **6 ca Q** §0d + **11 ca R** §0e). Ca A→R, gồm **10 ca chứng minh ngược** (tắt cờ ⇒ lệnh đi TRỌN 1 lần / bypass KHÔNG mở)
để mọi khẳng định "chặn được" đều có phản chứng, không chỉ khẳng định suông.
Chạy dưới **`TZ=Asia/Ho_Chi_Minh` / `TZ=America/New_York` / `TZ` rỗng** và **2 interpreter**
(`wc_venv` + system `python3`) — kết quả giống hệt (§16 + skill `verify-before-done`).

> Con số **66/66** ở bản báo cáo đầu là **SAI** (reviewer đếm được 81/81 khi tự chạy). Ghi lại ở
> đây thay vì sửa lặng lẽ — số ca là thứ người đọc dùng để tin phần còn lại.

**Quét rộng theo `coding_guidelines` §23** (executor.py **và** config.py đều là module lõi dùng
chung — 13 và 17 selfcheck phụ thuộc). Lấy danh sách bằng `bin/selfcheck_scope_map.sh`, chạy
**HẾT** cả hai phạm vi, cộng `test_trading_bot.py` (chạm thẳng `_fill_timing_mult`):

| Phạm vi | Selfcheck | rc | dòng FAIL |
|---|---|---|---|
| `executor.py` (13) | book_tagging 40 · capit_lever 188 · capit_participation_cap 17 · churn_guard 15 · dcf_check · discretionary_participation_cap 23 · extreme_regime 14 · ghost_order 13 · hard_no_chase_ceiling 56 · **hybrid_fill_timing 105** · paper_main_window 10 · t2_settlement 7 · tick_retry 15 | **0** | **0** |
| `config.py` (4 cái còn lại) | approval_gate 19 · concurrent_lock 5 · dc_book_waterfall 61 · lag_adv_cap | **0** | **0** |
| bổ sung | test_trading_bot | **0** | **0** |

**18/18 rc=0, tổng 0 dòng `[FAIL]`.** `extreme_regime_selfcheck` (14/14) và `churn_guard_selfcheck`
(15/15) là hai bộ sát sườn nhất với 2 lỗi vừa vá — cả hai vẫn xanh ⇒ bản vá không đánh đổi hành vi
cũ của chính hai layer đó.

**Diễn tập paper** (`exp_hybrid_fill_20260810/paper_rehearsal_hybrid.py`) — PaperBroker THẬT, phiên
mô phỏng 09:00→14:30 bước 1 phút, đồng hồ bơm vào (chạy được mọi lúc, kể cả cuối tuần):

```
S1  09:15  1,000 | S1  09:30  1,000 | S1  09:45  1,000 | S1  10:00  1,000
B1  11:00  1,000 | B1  11:15  1,000 | B1  13:00  1,000 | B1  13:15  1,000 | B1  13:30  1,000
PLACE_FAIL 0 · NO_QUOTE 0 · WAIT_CASH 0 · WAIT_QUOTA 0 · WAIT_T2_SETTLEMENT 0
```

Đúng 5 block MUA + 4 block BÁN, đủ KL, **0 reject**. Đây là bằng chứng **cơ chế**, KHÔNG phải bằng
chứng edge — PaperBroker khớp 100% tại giá đặt nên không thể sinh dữ liệu fill thật (lý do đã ghi
trong `research/fill_timing_checkpoint_20260804.md`).

⚠️ **Bản đầu tiên FAIL diễn tập này** (§0) — giữ lại trong báo cáo vì đó là bằng chứng cái gate
này có tác dụng thật, không phải nghi thức.

---

## 5. Caveat mang theo (chép từ §8 báo cáo gốc — đã ghi vào comment code)

1. **Không đo được impact của chính lệnh ta** — nến lịch sử không chứa lệnh của ta. Con số bps là
   *hình dạng giá nội phiên lịch sử*, không phải impact.
2. **Không có điều kiện tín hiệu** — mẫu là **mọi** ngày của 33 mã, không riêng ngày có tín hiệu
   LAG/BAL. Ngày sau tin BCTC có thể có hình dạng nội phiên khác. **Chưa kiểm được.**
3. **Cache `intraday_full.pkl` STALE, hết 2026-05-12** — 2026 chỉ 84 phiên; dấu vẫn nhất quán
   nhưng đoạn gần nhất mỏng nhất.
4. **Giá thực thi là xấp xỉ `(H+L+C)/3` của block**, không phải fill thật; giả định price-taker
   khớp ở giá trung bình block (hợp lý ở mức tham gia <1%, lạc quan ở lệnh lớn).
5. **Bỏ ATC 14:45** khỏi phép đo ⇒ `_atc_sweep` giữ nguyên, không đưa vào lịch HYBRID.
6. **Quy mô kinh tế ~0,1-0,3%/năm** (vòng quay ~3×NAV/năm, bậc độ lớn) — **vệ sinh chi phí**,
   KHÔNG phải đòn bẩy alpha. So với CAGR 28,86%: đừng đánh đổi rủi ro/độ phức tạp để lấy.

---

## 6. Trạng thái & bước tiếp theo

| Việc | Trạng thái |
|---|---|
| Code + cờ config mặc định TẮT | ✅ xong, `git diff` sạch ngoài phạm vi này |
| Selfcheck mới **105/105** + quét rộng **18/18** (executor 13 + config 4 + test_trading_bot, tổng 588 PASS) | ✅ |
| Diễn tập paper (đúng lịch, 0 reject) | ✅ |
| quant-skeptic vòng 1 | ❌ **REFUTED** (2 lỗi giao thoa thật) — xem §0b |
| Vá 2 lỗi + 12 ca hồi quy O1/O2 | ✅ |
| quant-skeptic vòng 2 | ❌ **REFUTED (high)** — lỗi thứ 3, nặng hơn — xem §0c |
| Vá lỗi 3 + 6 ca hồi quy P (đã chứng minh bắt được lỗi) | ✅ |
| quant-skeptic vòng 3 | ✅ **CONFIRMED (medium)** — cơ chế đứng vững; nêu 1 chi phí API thật — xem §0d |
| Throttle `extreme_defer_poll_sec` + 6 ca Q (đo 3.600 → 120 lời gọi) | ✅ soạn xong |
| quant-skeptic vòng 4 (chỉ throttle) | ❌ **REFUTED (high)** — đóng dấu throttle TRƯỚC khi kiểm `q_ext.ok()` ⇒ 1 quote lỗi tiêu trọn 60s ⇒ tái sinh deadlock vòng 2 (reviewer tái lập: 0 lệnh suốt 09:00-09:15) — xem §0e |
| Vá (chỉ đóng dấu khi poll THÀNH CÔNG) + 11 ca R, đã chứng minh phân biệt được (đảo lại 1 dòng ⇒ 5/7 ca FAIL) | ✅ |
| quant-skeptic vòng 5 | ✅ **CONFIRMED (high)** — reviewer tự chạy lại selfcheck + tự đảo ngược dòng vá + tự quét 14/14; không tìm thấy đường nào khác khoá EXTREME quá 1 chu kỳ throttle |
| Patch bật trên PAPER (chưa áp) | ✅ soạn sẵn: `pending_paper_enable_hybrid_fill_20260810/` |
| Bật LIVE | ❌ **KHÔNG** — cần user duyệt riêng, xem README của thư mục patch |

**Cờ chưa bao giờ được flip lên True trong bất kỳ commit nào của job này** (kiểm bằng
`git diff` — dòng `"fill_timing_hybrid_enabled": False`).

---

## 7. Đề xuất (KHÔNG làm ngay) — theo dõi sức khoẻ hình dạng phiên theo quý

Hình dạng giá nội phiên **không phải hằng số của vũ trụ** — nó là hành vi thị trường, đổi được khi
cấu trúc vi mô đổi (KRX go-live, T+2→T+1, tỉ trọng NĐT nước ngoài, phiên ATC/ATO đổi luật). Nghiên
cứu gốc dừng ở 2026-05-12; nếu cửa sổ suy yếu mà không ai đo lại thì ta vẫn cứ trải lệnh theo một
lịch đã hết hiệu lực — **im lặng**, không có triệu chứng nào.

**Đề xuất tối thiểu, không xây thêm hạ tầng:**
- **Script**: tái dùng nguyên `mike/agents/Taylor/exp_twap_20260804/twap_vs_window.py` (đã có, đã
  tái lập được) — chỉ cần refresh nguồn nến. **Nút thắt thật là DỮ LIỆU, không phải code**:
  `intraday_full.pkl` là research-static, không có cron refresh. Việc thật cần làm trước là **hỏi
  Winston (data-ops) xem có đường refresh nến 15' được không**; không có thì đề xuất này chết ở
  đây và nên nói thẳng thay vì lên lịch một cron không bao giờ có dữ liệu mới.
- **Tần suất**: **hàng quý** (không dày hơn) — mẫu 1 quý ≈ 60 phiên, mỏng; đọc theo **dấu và
  dose-response** (sáng đắt → đầu chiều rẻ còn đơn điệu không), **không** đọc theo t-stat 1 quý.
- **Nơi đặt**: **không tạo cron mới**. Móc vào `bin/bq_monthly_pin.py` (đã chạy ngày 1) với điều
  kiện tháng ∈ {1,4,7,10}, hoặc để **Friday KB editorial review** nhắc — cùng tinh thần §8b.
- **Ngưỡng báo động (khai TRƯỚC, không chọn sau)**: dấu của chân MUA **đảo** (dương) trong 2 quý
  liên tiếp, HOẶC dose-response sáng→chiều biến mất. Chạm ⇒ **tắt cờ**, không phải re-tune lịch.

---

## Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python hybrid_fill_timing_selfcheck.py
TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python \
    mike/agents/Taylor/exp_hybrid_fill_20260810/paper_rehearsal_hybrid.py
bash mike/bin/selfcheck_scope_map.sh trading_bot/executor.py   # 13 selfcheck phải chạy
bash mike/bin/selfcheck_scope_map.sh trading_bot/config.py     # +4 cái nữa (17 tổng, 13 trùng)
```
