# ABSORPTION TEST cho neo `ticker_financial` + cổng phiên bản `live=` — job `Taylor_20260820_043511`

Tiếp nối `Taylor_20260820_015520` (WC `675c34a1` / mike `ef91e5af`).
Ngày: 2026-08-20. Nhánh: `session/oshares-absorb-20260820` (CẢ HAI repo).

---

## VẤN ĐỀ (user nêu 2026-08-20 ~11:30 ICT)

> *"Ngày ra BCTC ví dụ 28.07 chỉ phản ánh dữ liệu đúng đến 30.06 (quý-end). Sự kiện từ 01.07 trở
> đi CHƯA được phản ánh đầy đủ trong báo cáo."*

Một dòng `ticker_financial` mang **NGÀY CÔNG BỐ**, còn con số `OShares` trong nó có thể là số chốt
tại **QUÝ-END**. Khi dòng quý làm neo (`FIN_FALLBACK` / `ANCHOR_UNVERIFIED`), `_pending_iss` chỉ
lăn ISS có `exright_date > anchor_date` ⇒ mọi sự kiện rơi vào `(quý-end, ngày công bố]` bị **mặc
định** là đã nằm trong neo. Nếu vendor chép nguyên số quý-end thì đó là **UNDERCOUNT ÂM THẦM** cho
tới khi AIS về.

**Không sửa được bằng một luật cắt-ngày khác** — vendor KHÔNG nhất quán, đo được cả hai phía:

| Ca | Dòng quý | Sự kiện trong cửa sổ | Kết luận |
|---|---|---|---|
| `HHV` (thật, BQ) | 2026-07-31 = 574.511.888 | cổ tức CP 5% ex 07-09, `issue_volumn` 27.345.592 | base khai `B` = 546.911.840; `B×1,05` = 574.257.432, lệch **+0,044%** ⇒ **ĐÃ GỒM** |
| `ABW` (thật, BQ) | 2026-07-20 | 1 ISS | khớp "đã gồm" lệch **−0,000%** ⇒ **ĐÃ GỒM** |
| `FPT` (registry) | 2025-07-22 | thưởng 15% ex 07-21 | mang số SAU sự kiện ⇒ vendor cập nhật tới ngày công bố |

⇒ Cái tách được hai ca là **SỐ HỌC**, và số học đó do CHÍNH sự kiện khai ra.

## GIẢI PHÁP — `_absorption_test()` (`oshares_live.py`)

`B_k = issue_volumn_k / exercise_ratio_k` = số CP TRƯỚC sự kiện thứ k theo lời khai của tổ chức
phát hành ⇒ `B_k` chính là số CP SAU khi đã gồm `k−1` sự kiện đầu. Với n sự kiện trong cửa sổ
(sắp theo `exright_date` tăng dần):

    H_k ("dòng quý gồm đúng k sự kiện đầu"),  k = 0..n
        k < n :  kỳ vọng = B_{k+1}
        k = n :  kỳ vọng = B_n × (1 + ratio_n)

So `row_value` với từng kỳ vọng trong `EXPLAIN_TOL` (0,1%):

- **(a) khớp ĐÚNG MỘT `H_k`** ⇒ lăn các sự kiện `k+1..n` bằng `issue_volumn` (số ĐẾM, không phải
  tỉ lệ). `k = n` ⇒ không lăn gì (ca `HHV`, `verdict = ABSORBED`).
- **(b) khớp `H_k` với `k < n`** ⇒ `verdict = ROLLED`, số được sửa lên.
- **(c) không khớp cái nào / khớp nhiều cái / thiếu `ratio`|`issue_volumn`** ⇒ **GIỮ NGUYÊN HÀNH
  VI CŨ (không lăn)** + `verdict = WINDOW_AMBIGUOUS`, note nêu **CẢ n+1 con số giả thuyết**.

**Cửa sổ chặn hai đầu:** `(max(AIS gần nhất ≤ row_time, row_time − ABSORB_WINDOW_DAYS), row_time]`,
`ABSORB_WINDOW_DAYS = 120`. Lấy `max` = cửa sổ HẸP NHẤT = gần hành vi cũ nhất. Chặn dưới bằng AIS
gần nhất để không mở lại lỗi "orphan event cưỡi lên mọi câu trả lời sau" đã đo ở `_unabsorbed_iss`.

**RÀNG BUỘC ĐÃ GIỮ:**
- Chỉ chạy khi `live=True` **và** neo là `ticker_financial` **và** neo CHƯA verified. **Nhánh PIT
  (`live=False`) không đổi một số nào** — backtest đang ghim.
- Neo dòng quý ĐÃ verified không bị chạm: `_explain_quarterly` đã đối chiếu xong bằng
  `_unabsorbed_iss` (subset matching); hỏi lại là hai lời đáp cho một câu hỏi.
- Sự kiện được lăn luôn có `issue_volumn > 0` ⇒ **không bao giờ biến thành blocker** ⇒ không có
  đường nào một câu trả lời đang có số bị đẩy về `UNKNOWN_RATIO`.
- Kết luận **luôn** được ghi ra field `absorption_test` (kể cả ca không lăn) — im lặng ở đây là
  đúng lỗi mà bản vá đi sửa.

### ⚠️ Tỉ lệ NHỎ tự đẩy ca về nhánh (c), có chủ đích
`exercise_ratio` làm tròn 4–5 chữ số ⇒ sai số tương đối của `B` ≈ `5e-6/ratio`: ratio 0,05 cho
0,01% (TRONG `EXPLAIN_TOL`), nhưng ESOP ratio 0,00225 cho ~0,22% (NGOÀI). Không giả thuyết nào
khớp ⇒ `WINDOW_AMBIGUOUS`, không lăn. Đó là kết quả ĐÚNG: `B` không đủ độ phân giải để trả lời,
và nói "không biết" rẻ hơn đoán.

---

## ĐO TÁC ĐỘNG — `absorption_impact_probe.py`

Rổ `ticker_prune` tại 5 mốc `asof`, `live=True`:

| asof | rổ | ABSORBED | **ROLLED** | WINDOW_AMBIGUOUS | N/A |
|---|---:|---:|---:|---:|---:|
| 2026-08-19 | 208 | 2 | **0** | 0 | 206 |
| 2026-05-15 | 240 | 1 | **0** | 3 | 236 |
| 2026-02-15 | 259 | 2 | **0** | 4 | 253 |
| 2025-11-15 | 281 | 3 | **0** | 3 | 275 |
| 2025-08-15 | 305 | 3 | **0** | 5 | 297 |
| **TỔNG** | **1.293 ô** | **11** | **0** | **15** | **1.267** |

**KẾT LUẬN THẲNG: trên rổ đã đo, bản vá KHÔNG đổi MỘT SỐ NÀO.** Ca (b) — hình dạng user cảnh báo —
**không quan sát được** trên `ticker_prune` ở 5 mốc này. Cái bản vá thực sự giao:

1. **11 ca xác nhận hành vi cũ ĐÚNG bằng số học**, không còn là mặc định im lặng. Hai ca khớp
   ngoạn mục (`HHV` +0,044%, `ABW` −0,000%) là bằng chứng dương rằng vendor CÓ cập nhật tới ngày
   công bố ở ca cổ tức CP.
2. **15 ca `WINDOW_AMBIGUOUS` nay HIỆN RA** thay vì trôi qua âm thầm — gồm `KBC`, `PDR`, `SJS`,
   `TDC`, `BSR`, `HDB`, `KSF`, `ABB`, `DXG`, `GEG`, `NVL`, `HAH`, `NAF`, `VTP`, `STK`. Phần lớn là
   phát hành riêng lẻ thiếu `exercise_ratio` (không dựng nổi `B`) hoặc ESOP ratio nhỏ.
3. **Detector cho ca (b)**: nếu vendor đổi cách chép (hoặc một mã ngoài rổ prune rơi vào), nó sẽ
   được sửa và ghi nhãn `ROLLED` thay vì thiếu âm thầm.

Số phải nhắc lại khi ai đó muốn siết/nới cửa sổ hay `EXPLAIN_TOL` là **0 số đổi / 15 nhãn mới**,
không phải "vá một undercount đã xảy ra".

---

## VIỆC 2 — cổng phiên bản `live=` (`mike/bin/corp_action_daily.py`)

`oshares_live.py` ở repo `WorkingClaude`, `corp_action_daily.py` ở repo `mike` — hai repo git
merge độc lập. Kwarg `live` ra đời 2026-08-20 và CẢ BA điểm gọi truyền nó ⇒ merge lệch một repo cho
`TypeError` thô ném ra từ giữa `run()`, sau khi đã truy vấn BQ. Nay kiểm bằng
`inspect.signature(oshares_at)` ngay lúc import và `SystemExit` sớm với chỉ dẫn merge cả hai repo +
2 lệnh `git log` để tự tra. (Khuyến nghị của quant-skeptic vòng CONFIRMED 04:14, job
`Taylor_20260820_015520`.)

---

## NGHIỆM THU

| Bộ | Kết quả |
|---|---|
| `oshares_live.py --selfcheck` (TZ=ICT mặc định) | **PASS 69/69** (61 → 69, thêm 8 ca AB*) |
| …dưới `env -u TZ` | **PASS 69/69** |
| …dưới `TZ=America/New_York` | **PASS 69/69** |
| `corp_action_daily_selfcheck.py` (WORKDIR_8L thật) | **PASS 201/201** |
| `oshares_pit.py --selfcheck` | 47/48 — ca đỏ `A4b` (VNM 2016-09-20) **CÓ SẴN TRƯỚC BẢN VÁ**: chạy lại nguyên văn trên `master` chưa vá cho ĐÚNG một ca đỏ đó. `oshares_pit.py` không truyền `live` ở đâu cả (`grep -c live` = 0) ⇒ PIT không bị chạm theo thiết kế |
| Cổng phiên bản — ca ÂM (module giả không có `live`) | thoát rc=1 kèm thông báo chỉ dẫn merge |
| Cổng phiên bản — ca DƯƠNG (module thật) | import thành công |

**8 ca selfcheck mới** (`AB1`–`AB6`): `AB1/AB1b` ca THẬT `HHV` chạm BQ (a); `AB2` fixture số quý-end
(b) → `ROLLED` 574.257.432; `AB2b` cùng fixture dưới `live=False` → **không đổi, không có field
`absorption_test`**; `AB3` mơ hồ vì số không khớp; `AB3b` note nêu cả hai giả thuyết; `AB3c` mơ hồ
vì thiếu `exercise_ratio` (và KHÔNG bị biến thành `UNKNOWN_RATIO`); `AB4` hấp thụ MỘT PHẦN n=2
(chặn bản cài chỉ-xét-sự-kiện-cuối); `AB5`/`AB5b` chặn dưới cửa sổ + đối chứng ngược; `AB6` neo
không phải dòng quý-chưa-verified thì không có field.

### ⚠️ Ghi lại một cái bẫy phát hiện được nhưng KHÔNG sửa (ngoài phạm vi)
`corp_action_daily_selfcheck.py` ca `SC2` dùng `runner=lambda p: R(1 if "oshares" in p else 0)` —
khớp **chuỗi con trên ĐƯỜNG DẪN**. Chạy trong worktree tên `wt-oshares-absorb` thì đường dẫn của
`corp_action_lib` cũng chứa `"oshares"` ⇒ FAIL giả (`[('corp_action_lib', 1), ('oshares_live', 1)]`).
Chạy lại với `WORKDIR_8L` thật: 201/201 PASS. Đúng họ lỗi §28 (so chuỗi mô tả thay vì giá trị chuẩn
hoá); sửa = khớp trên `name` chứ không trên `path`. Không đụng ở job này vì §3 (surgical).

---

## ATTEMPT 2 (2026-08-20, cùng job) — một BUG THẬT trong code của attempt 1

Attempt 1 hết lượt khi `verify_finding.sh` đang chạy (log rỗng, không có verdict). Khi rà lại code
trước khi merge, **khẳng định của attempt 1 rằng "sự kiện được lăn luôn có `issue_volumn` > 0 ⇒
không bao giờ thành blocker" là SAI**, và nó sai theo cách tự chứng minh được:

Một sự kiện thiếu **cả ba** trường cỡ (`shares_delta`, `issue_volumn`, `exercise_ratio`) có giả
thuyết `H_k` của CHÍNH nó là `None` nên không bao giờ được khớp — nhưng một giả thuyết `k' < k`
khớp thì nó **vẫn bị kéo vào `extra`**. Đo thật trên fixture n=2 (`row = 500.000.000`, ISS 07-05 đủ
trường, ISS 07-20 rỗng cỡ):

| Bản | Kết quả |
|---|---|
| attempt 1 nguyên văn | `TypeError: float() argument must be ... not 'NoneType'` ném từ dòng `note` |
| chỉ gỡ guard, giữ `_size_hint` | KHÔNG crash, nhưng rơi về `UNKNOWN_RATIO`/`None` — **một câu trả lời đang CÓ SỐ bị đẩy thành "không biết"** |
| attempt 2 (đã vá) | `WINDOW_AMBIGUOUS`, không lăn, giữ nguyên 500.000.000 |

**Bản vá** (`_unsizable` + `_size_hint`, `oshares_live.py`): nếu bất kỳ sự kiện nào trong `extra`
mà `_roll` không định cỡ được ⇒ về nhánh (c) `WINDOW_AMBIGUOUS`. Không quyết được cỡ thì đúng là
"không quyết được". `_size_hint` đồng thời bỏ giả định `issue_volumn` luôn tồn tại trong `note` và
in ra ĐÚNG trường mà `_roll` sẽ dùng.

**Selfcheck**: `AB7` (ca dương) + `AB7b` (đối chứng ngược — cùng cửa sổ nhưng sự kiện thứ hai CÓ
`issue_volumn` thì vẫn `ROLLED` ⇒ AB7 không xanh nhờ luật chặn mọi ca n=2).

**Tác động số: KHÔNG ĐỔI.** Guard chỉ kích hoạt khi `extra` khác rỗng; cả 11 ca `ABSORBED` đo được
đều có `extra` rỗng và có 0 ca `ROLLED` ⇒ chạy lại probe `asof=2026-08-19` cho `detail` **khớp từng
byte** với attempt 1 (`{N/A: 206, ABSORBED: 2}`).

### Nghiệm thu attempt 2
`oshares_live.py --selfcheck` **PASS 71/71** dưới 4 TZ (ICT mặc định, `env -u TZ`,
`America/New_York`, `Asia/Tokyo`) · `corp_action_daily_selfcheck.py` **201/201** ·
`oshares_pit.py` 47/48 với ca đỏ `A4b` tái hiện ĐÚNG trên cây chưa vá (đối chứng) · cổng phiên bản
ca ÂM (stub không có kwarg `live`) `SystemExit` kèm chỉ dẫn merge, ca DƯƠNG import bình thường.

### ⚠️ Bẫy đo lường: `wc_env.sh:12` có `cd "$WORKDIR_8L"`
`source wc_env.sh` rồi chạy `python3 oshares_live.py --selfcheck` **KHÔNG chạy file trong worktree**
— nó đã `cd` sang repo chính và chạy bản CHƯA VÁ, in `PASS 58/58` một cách hoàn toàn thuyết phục.
Attempt 2 suýt đọc nhầm con số đó thành "bản vá làm mất 13 test". **Luôn `cd` lại vào worktree SAU
khi `source wc_env.sh`**, và đối chiếu số test với một lần chạy đối chứng trên cây chưa vá.

### quant-skeptic — **CONFIRMED** (confidence `medium`), 2026-08-20
Log: `mike/logs/verify_20260820_055201_3894488.log`. Reviewer tự chạy lại cả 3 selfcheck, truy vấn
BQ độc lập cho HHV và tái lập từng con số, đọc thẳng `absorption_impact_20260819.json`.

`medium` (không phải `high`) vì MỘT điểm: reviewer gỡ **đúng cái guard** rồi chạy lại và **không**
tái hiện được `TypeError` ⇒ nghi ngờ câu chuyện crash bị thổi phồng. **Reviewer đúng trong phạm vi
họ thử, và tôi cũng đúng** — bản vá gồm HAI nửa, gỡ một nửa thì nửa kia (`_size_hint`) vẫn đỡ:

* gỡ **chỉ guard** ⇒ `UNKNOWN_RATIO` im lặng (đúng như reviewer đo — và đây mới là regression
  nghiêm trọng hơn),
* gỡ **cả hai nửa** (= đúng hình dạng attempt 1) ⇒ `TypeError`, đã tái hiện lại ở `/tmp/att1`.

Bài học mang đi, đúng khuyến nghị của reviewer: **giữ diff TRƯỚC khi vá** (throwaway commit /
`git stash`) để câu chuyện lỗi tái hiện được thay vì phải kể từ trí nhớ.
