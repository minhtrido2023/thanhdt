# Cổng biên độ ×3 cho `corp_action_daily.py` — WARN, KHÔNG ẩn số (phương án C của user)

**Job** `Taylor_20260814_003610` (attempt 2) · **Ngày** 2026-08-14 · **Commit** xem cuối file
**Tiền đề**: ROUND5 §Việc 4 — cổng `SANITY_FACTOR=3` chỉ sống trong `oshares_pit.py` (policy của
riêng consumer đó), KHÔNG áp cho `corp_action_daily.py` vốn gọi thẳng `oshares_at()`. Đo trên
1.070 mã × 48 quý: **279 ô / 34 mã** lọt qua cổng chứng nhận nhưng lệch >3 lần so với
`ticker_financial`, trong đó **2 mã ĐANG GIỮ THẬT: VHM và VND**.

**User chọn C** trong 3 phương án (A = chặn cứng, ẩn số 34 mã lịch sử · B = không đổi gì ·
C = mở rộng WARN, KHÔNG tự ẩn/chặn số nào), lý do nguyên văn: *"C mới phát hiện được vấn đề thay
vì im lặng từ chối trả lời như A"*.

---

## 1. Đã làm gì

Cổng biên độ chạy ở **cả ba điểm gọi `oshares_at()`** của file, mỗi cờ mang `where` riêng:

| `where` | Điểm gọi | Số so với |
|---|---|---|
| `publish` | `cur = oshares_at(track, asof)` — bộ số ĐƯỢC CÔNG BỐ | dòng quý gần nhất ≤ `asof` |
| `retro` | `back = oshares_at(…, prev_asof)` dùng cho `check_retro()` | dòng quý gần nhất ≤ `prev_asof` |
| `crosscheck` | `oshares_at([tk], qd)` bên trong `crosscheck()` | `ticker_financial` của chính bản ghi đó |

Điểm gọi `crosscheck` **tái dùng bản ghi `crosscheck()` đã có** (`sanity_warns_from_crosscheck`),
không truy vấn lại — nó đã lấy đúng dòng quý và đã gọi `oshares_at` tại ngày dòng quý; hai con số
cần để so nằm sẵn trong bản ghi. Điểm gọi `retro` tính `back` **một lần** trong `run()` rồi truyền
vào `check_retro(back=…)` (tham số mới, mặc định `None` ⇒ mọi caller cũ không đổi một chữ).

**Kênh cảnh báo** — đi đúng đường Discord/Telegram sẵn có, nhãn RÕ KHÁC hai nhóm cũ:

| Nhãn | Nghĩa | Số công bố |
|---|---|---|
| 🚨 | bất biến số CP bị vi phạm | **ĐÃ BỊ GIẤU** |
| ⚠️ | hai nguồn nói khác nhau tại ngày dòng quý | giữ nguyên |
| **📏 (mới)** | **sai BẬC ĐỘ LỚN so với dòng quý** | **giữ NGUYÊN VẸN — chỉ đánh dấu** |

Câu *"⚠️ SỐ VẪN ĐƯỢC CÔNG BỐ NGUYÊN VẸN, đây CHỈ là dấu hỏi, KHÁC dòng 🚨 nơi số đã bị GIẤU"* nằm
NGAY TRONG TIÊU ĐỀ (ca MG9 khoá vị trí <200 ký tự), và **mã ĐANG GIỮ tách riêng** ở cả tiêu đề
(`N mã, K ĐANG GIỮ`) lẫn thân dòng (`**ĐANG GIỮ** — …`) — 2/34 mã lọt là VHM/VND, đó mới là nhóm
chạm tiền.

Cũng đi ra **snapshot** (`magnitude_warns`/`magnitude_suspect`/`magnitude_suspect_held`/
`magnitude_factor`/`magnitude_policy`), **log** (`[gate-4c biên độ]`) và **bus**
(`n_magnitude_suspect`, `magnitude_suspect_held`, `magnitude_suppressed_any_value: False`).

### Ba lựa chọn thiết kế, có lý do

1. **Ngưỡng dùng CHUNG `_pit.SANITY_FACTOR`, đọc tại LÚC GỌI** (không `from … import`, không hằng
   số riêng). Lập luận ủng hộ hằng số riêng — "sweep `OSHARES_SANITY_FACTOR=<x>` khi audit
   custom30 sẽ lặng lẽ đổi độ nhạy cảnh báo hàng ngày" — không đứng: sweep chạy trong TIẾN TRÌNH
   KHÁC, không chạm tiến trình cron này. Rủi ro hai hằng số trôi khỏi nhau thì có thật. Ca MG14
   khoá tính chất "đọc tại lúc gọi" (monkeypatch → hành vi đổi).
2. **Biên là `>3`, không phải `>=3`** — gọi thẳng `_pit._sane` nên `ratio == 3,0` chẵn là HỢP LỆ,
   cùng vị ngữ với phép đo 279 ô/34 mã của ROUND5 (nó cũng đo bằng `_sane`). MG4/MG4b khoá.
3. **`value is None` ⇒ bỏ qua** — mã fail-closed đã được đếm ở dòng 🔇 (`none_value_watch`); gắn
   cờ ở đó là đếm CÙNG một mã ở hai dòng cảnh báo như hai vấn đề. Vì thế `sanity_warns` chạy SAU
   `withhold_suspect()`.
4. `crosscheck()` chuyển sang dùng `_quarterly_at()` — **một** định nghĩa "dòng quý gần nhất ≤
   ngày" cho cả lớp 2 lẫn lớp 4c.

---

## 2. Bằng chứng

### 2.1 Hồi quy: KHÔNG ca nào đổi

`corp_action_daily_selfcheck.py` **153/153 trước patch → 178/178 sau patch** (153 cũ + 25 mới
`MG1…MG16`), PASS dưới **4 môi trường TZ**: `env -u TZ`, `UTC`, `America/New_York`,
`Asia/Ho_Chi_Minh` (§16). *Dispatch ghi "142 ca" — số đã cũ, bộ đã lớn lên; mốc đúng là 153.*

### 2.2 A/B trên DỮ LIỆU THẬT: 0/35 số publish đổi

`run(asof=2026-08-14, dry_run=True)` chạy hai chân, chân control = đúng `HEAD`:

```
rc: 0 -> 0
field MOI (chỉ thêm):  magnitude_factor, magnitude_policy, magnitude_suspect,
                       magnitude_suspect_held, magnitude_warns
field BỊ MẤT:          []
field CŨ ĐỔI GIÁ TRỊ:  ['generated_at']   ← chỉ vì hai lượt chạy khác giờ
số mã: 35 == 35, cùng tập mã
MÃ CÓ `value` ĐỔI:     KHÔNG CÓ — 0/35
field thêm vào từng bản ghi mã: không có
[gate-4c biên độ] 0 mã lệch >×3 — không mã nào đang giữ
```

Hôm nay 0 cảnh báo ⇒ **không thêm nhiễu nào vào tin nhắn 07:30**.

### 2.3 Ca thật, chạy trên BigQuery THẬT (không phải fixture)

`_fetch` + `oshares_at` + `sanity_warns` production trên dữ liệu thật:

| Mã | Ngày | live | dòng quý | ratio đo được | ROUND5 ghi | value đổi? |
|---|---|---|---|---|---|---|
| VHM | 2021-12-31 | 4.354.367 | 4.354.367.488 | `0.000999999887928614` | `0.000999999887928614` | **KHÔNG** |
| VND | 2022-03-31 | 1.587.097.216,8 | 434.942.782 (dòng 2022-02-07) | `3.6489793197671685` | `3.6489793197671685` | **KHÔNG** |

Khớp **tuyệt đối tới chữ số cuối** với phép đo độc lập ở ROUND5, và **hai mã nằm ở HAI PHÍA của
ngưỡng** (×0,001 và ×3,65) ⇒ cổng không mù một phía. Chuỗi Discord thật sinh ra:

```
📏 **Số CP lệch BẬC ĐỘ LỚN so với `ticker_financial`** (1 mã, 1 ĐANG GIỮ — ⚠️ SỐ VẪN ĐƯỢC
CÔNG BỐ NGUYÊN VẸN, đây CHỈ là dấu hỏi, KHÁC dòng 🚨 nơi số đã bị GIẤU): **ĐANG GIỮ** —
VHM@2021-12-31 [publish] 4,354,367 vs dòng quý 2021-10-29 4,354,367,488 (×0.001, ngưỡng ×3,
nhãn AIS_EXACT)
```

### 2.4 Mutation: 6/6 giết, và 1 ca tự công bố là KHÔNG giết được

| Mutation | Kết quả |
|---|---|
| biên `>3` → `>=3` | **giết** (MG4, rc=1) |
| WARN → SUPPRESS (`value = None` sau khi gắn cờ) | **giết** (rc=1, nổ ngay tại `float(r["value"])`) |
| chỉ bắt một phía (`ratio > F`, bỏ nghịch đảo) | **giết** (MG1b — ca VHM nằm ở phía nghịch đảo) |
| bỏ tách mã ĐANG GIỮ | **giết** (MG9c + MG10) |
| bỏ câu "CÔNG BỐ NGUYÊN VẸN" khỏi tiêu đề | **giết** (MG9 + MG11) |
| chép tay bất đẳng thức thay vì gọi `_pit._sane` | **giết** (MG14 + MG15) |
| bỏ dòng `if r.get("value") is None: continue` | **KHÔNG giết** — 178/178 |

Ca cuối được **ghi thẳng vào comment của MG6**: `sanity_flag(None, …)` tự trả `None` nên dòng
guard đó là phòng thủ chồng lớp, không phải chỗ duy nhất giữ tính chất. Không để nó trông như một
bằng chứng bao phủ mà nó không phải.

### 2.5 Hai ca test đầu tiên của tôi SAI, và tự bắt được

* `MG9b` bản đầu grep `"đã bị GIẤU):"` ⇒ đỏ vì chính câu ĐỐI CHIẾU trong tiêu đề — phạt đúng cái
  phải có. Sửa: grep đúng cụm KHẲNG ĐỊNH mà dòng 🚨 in ra (`"không publish giá trị"`), đồng thời
  assert `"KHÁC dòng 🚨"` PHẢI có mặt.
* `MG15` bản đầu đếm `src.count("_pit._sane")` ⇒ đỏ vì một dòng DOCSTRING nhắc tên hàm. Sửa: đếm
  ĐIỂM GỌI `"_pit._sane("`.

Cả hai đều là lỗi ASSERTION, không phải lỗi hành vi — và cả hai chỉ lộ ra vì ca được chạy thật
chứ không đọc lại (§19 verify-before-done).

---

## 3. Đây có phải patch tách biệt, review nhanh được không? **CÓ**

Bất biến kiểm được bằng MỘT phép so, không cần đọc hết code: **`run()` cùng `asof` trên cùng dữ
liệu phải trả về snapshot Y HỆT trước patch, trừ 5 field mới thuần cộng thêm** — đã chạy ở §2.2
và cho `0/35` mã đổi `value`. Người review chỉ cần tái lập đúng lệnh đó.

Ba tính chất còn lại đều có ca chuyên trách + ca chứng minh ngược + mutation tương ứng:
biên `>3` (MG4/MG4b), nhãn phân biệt được với 🚨/⚠️ (MG9/MG11), mã ĐANG GIỮ tách riêng
(MG10/MG10b). Không chạm `oshares_live.py` / `oshares_pit.py` / `corp_action_lib.py`.

## 4. Rủi ro tồn dư — công bố

1. **Chưa chạy LIVE lần nào.** Hôm nay 0 cảnh báo nên đường 📏 → Discord **chưa từng gửi thật**
   (mới chỉ chứng minh qua `--no-alert` in ra chuỗi + selfcheck). Lượt cron đầu tiên có mã dính
   mới xác nhận được đầu-cuối.
2. **Không đo lại 279 ô/34 mã sau cổng chứng nhận AIS vòng 4-6.** Phép đo ROUND5 (23:47 hôm
   trước) có thể đã lệch khỏi hiện trạng — chính ca VHM với fixture 1 dòng AIS nay ra
   `AIS_UNCERTIFIED`. Con số 279/34 nên đọc là **cận trên**, không phải số mã sẽ kêu hàng ngày.
   Muốn số đúng phải chạy lại `probe_sanity_direct_call.py` — chưa làm, ngoài phạm vi dispatch.
3. **Tần suất cảnh báo chưa biết.** Nếu nhóm này kêu mỗi ngày trên vài mã, nó thành nhiễu nền và
   mất tác dụng — cần 5-10 phiên thật rồi xem lại, giống kỷ luật đã áp cho `FEED_DEAD_DAYS`.

## 5. Va chạm dispatch — đã giải quyết, không mất việc của ai

Hai job Taylor được dispatch cách nhau 52 giây cùng sửa file này
(`Taylor_20260814_003518` và `_003610`). Job `_003518` **tự nhường Việc 1** (bus event
2026-08-14T00:43:27Z) và chuyển sang việc khác, để lại phần đã viết dưới dạng patch
(`taylor_003518_warn.patch`). Bản wire này **kế thừa thư viện của patch đó** (`_quarterly_at`,
`sanity_flag`, `sanity_warns`, tham số `back=`) — công sức không bị vứt — và bổ sung phần patch đó
chưa kịp làm: điểm gọi `crosscheck`, `_fmt_magnitude`, tách mã ĐANG GIỮ, wire vào
`run()`/snapshot/Discord/bus, và toàn bộ 25 ca test. Nhật ký va chạm:
`../oshares_gate_move_20260813/COLLISION_20260814_dup_dispatch.md`.
