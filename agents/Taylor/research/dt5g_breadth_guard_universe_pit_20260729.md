# DT5G breadth-decoupling guard → `universe_pit` (point-in-time)

**Job**: `Taylor_20260729_152031` · **Ngày**: 2026-07-29 · **Tác giả**: Taylor
**Trạng thái**: PATCH SẴN SÀNG — **CHƯA MERGE** vào `macro_state_live.py` đang chạy cron.
**Kết luận 1 dòng**: đổi nguồn breadth `ticker_prune`(DISTINCT-ever, có look-ahead) →
`universe_pit`(per-day) làm đổi **0/3135 phiên** state DT5G cuối cùng; state hôm nay
2026-07-29 = **NEUTRAL(3)** không đổi; chỉ có 1 episode 13 phiên (01-02/2016) macro-cap đổi
theo hướng **thận trọng hơn** và **không binding**.

---

## 1. Vấn đề (nguồn: Winston_20260729_132257 §2/§4)

`macro_state_live.py:158` (guard breadth-decoupling trên Pillar B, thêm 2026-05-29):

```sql
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)   -- KHÔNG có time
```

Hai lỗi:

- **(a) Look-ahead + non-reproducible**: vị từ không có điều kiện thời gian ⇒ một mã được nạp
  vào `ticker_prune` HÔM NAY được đếm vào breadth của MỌI ngày lịch sử. Hệ quả nặng hơn: mỗi lần
  `ticker_prune` bị TRUNCATE/rebuild (vừa xảy ra 2026-07-29, xoá 58 mã khỏi toàn bộ lịch sử) thì
  chuỗi breadth lịch sử **bị viết lại**, tức DT5G không tái lập được theo thời gian.
  ⚠️ Lưu ý sắc thái: điều kiện `t.MA200 IS NOT NULL` che bớt phần look-ahead thô nhất (mã chưa
  niêm yết không có dòng trong `ticker` nên không bị đếm). Phần còn lại — và là phần thật —
  là *tiêu chí thành viên*: dùng danh sách curated của HÔM NAY để phán quyết một ngày của QUÁ KHỨ.
- **(b) Không có trong `mike/kb/data_registry/`**: consumer này sót lại từ trước dự án migrate
  `ticker_prune`→`universe_pit` (cutover chính thức 2026-07-22 cho R3/due-diligence/custom30V).

User đã chốt: migrate guard này sang `universe_pit`.

## 2. Thiết kế patch

Theo đúng khuôn mẫu đã có trong repo (`golive_recommend_v23.py`: `UNIVERSE_SOURCE` /
`CAPIT_BREADTH_SOURCE` + hàm sinh SQL), KHÔNG tự nghĩ lại:

```python
BREADTH_SOURCE = "pit"          # "pit" | "prune"  ← ROLLBACK ĐÚNG 1 DÒNG
UNIVERSE_PIT_TABLE = "lithe-record-440915-m9.tav2_mike.universe_pit"

def _breadth_sql(qstart, end):   # "pit":
    JOIN `universe_pit` u ON u.ticker=t.ticker AND u.time=t.time AND u.in_universe
```

Quyết định thiết kế và lý do:

| Điểm | Chọn | Lý do |
|---|---|---|
| Bảng | `universe_pit` (KHÔNG phải `universe_pit_quality`) | Breadth = sức khoẻ thị trường rộng, không phải rổ chất lượng. `universe_pit_q` (view) join `in_universe` cho ĐÚNG cùng tập thành viên như `universe_pit` — kiểm chứng bằng view DDL. |
| Ngưỡng `breadth_th=0.50`, `breadth_min_univ=100` | **GIỮ NGUYÊN** | Đúng chỉ đạo: không trộn re-tune vào migration nguồn dữ liệu (nếu sau này hồi quy, không tách được nguyên nhân). |
| Không dùng top-N như CAPIT | Đúng, không dùng | CAPIT cần top-250 vì mẫu số co giãn làm trôi *ngưỡng đã hiệu chuẩn tiền thật*; ở đây tác động đo được = **0 phiên đổi state**, thêm một tham số N nữa là thêm bậc tự do không có lợi ích đo được. |
| Env var? | KHÔNG — hằng số module | `coding_guidelines` §11 (sự cố C1 07-12: env kế thừa qua process). |
| Fail-safe khi thiếu ngày | Giữ nguyên `try/except` + NaN → guard False | Thiếu dữ liệu ⇒ **không suppress** ⇒ US cap vẫn bắn = hướng THẬN TRỌNG. Khác CAPIT (ở đó breadth cũ cho phép một lệnh mua thật nên phải fail-CLOSED); ở đây không cần abort. |

Patch: `mike/agents/Taylor/exp_dt5g_breadth_pit/dt5g_breadth_pit.patch`
File đề xuất đầy đủ: `.../macro_state_live.PROPOSED.py`

## 3. Phương pháp đo (harness variant + self-check n-diff, không suy đoán)

`exp_dt5g_breadth_pit/run_ab.py`: **cùng MỘT bản copy engine** chạy 2 lần, chỉ khác câu SQL
breadth ⇒ mọi khác biệt quy được về nguồn dữ liệu. Live BQ (`BQ_LOCAL_CACHE` bị pop), cửa sổ
2014-01-01 → 2026-07-29 (3.135 phiên), đo cả 4 tầng: base v3.4b → DT-4gate → macro-gate →
`get_gated_state`.

**Parity self-check** (bắt buộc, chống lỗi "harness khác production"): bản copy chạy nhánh
`prune` phải trùng **byte** với module production đang chạy → 0 diffs trên cả 4 cột.

## 4. Kết quả

```
sessions=3135  2014-01-02 -> 2026-07-29
  breadth         : 3132 diffs (99.90%)   ← chuỗi số đổi (đương nhiên, đổi mẫu số)
  guard(decoup)   :  229 diffs ( 7.30%)
  macro cap       :   13 diffs ( 0.41%)
  DT4 base        :    0 diffs
  DT5G state      :    0 diffs  ← KẾT LUẬN
```

- **State cuối cùng: 0/3135 phiên đổi.** Không có episode nào, lớn hay nhỏ.
- **Hôm nay 2026-07-29: KHÔNG ĐỔI** — NEUTRAL(3), `source=DT5G_macro`, cả 43 phiên gần nhất
  0 diff qua `get_gated_state`.
- Chuỗi breadth: mean |Δ| = 2,4pp, max |Δ| = 17,4pp; mẫu số trung bình 2026: 446 (prune) → 403 (pit).
- Guard flip 229 phiên, **lệch về phía thận trọng**: 161 phiên True→False (bỏ suppress, tức để
  US cap bắn) vs 68 phiên False→True.
- **Cap khác nhau đúng 1 episode**: 2016-01-26 → 2016-02-18, 13 phiên, nhánh `pit` áp cap
  NEUTRAL(3) mà nhánh cũ không áp (breadth pit ~0,48-0,54 quanh ngưỡng 0,50 trong khi prune
  ~0,50-0,58). **Không binding**: base DT4 lúc đó đã là NEUTRAL(3) nên `min(3,3)=3`.
- Phân bố cap: `{no-cap 2818, BEAR 173, NEUTRAL 95, CRISIS 49}` → `{2805, 173, 108, 49}`.
  Số phiên CRISIS/BEAR cap **y hệt** — migration không chạm tầng bảo vệ nặng.

**Quan sát phụ đáng ghi** (không phải lỗi): với nguồn `pit`, có 52 phiên năm 2016 mẫu số < 100
(prune: 34 phiên) ⇒ `breadth_min_univ=100` thật sự kích hoạt và chặn suppress. Đây đúng công
dụng thiết kế của ngưỡng đó ("nascent/small universe → no suppression"), và là hướng an toàn.

`universe_pit` phủ 2000-07-28 → 2026-07-29 (6.345 phiên) ⇒ kể cả lời gọi nghiên cứu pre-2014
cũng có dữ liệu, không rơi vào nhánh NaN.

## 5. Self-check trên chính file PROPOSED (`proposed_selfcheck.py`) — 4/4 PASS

| Test | Nội dung | Kết quả |
|---|---|---|
| T1 | `PROPOSED(pit)` == kết quả harness `pit` | 0 diffs / 4 cột |
| T2 | `PROPOSED(prune)` == `macro_state_live` LIVE | 0 diffs / 4 cột ⇒ **rollback 1 dòng là chính xác tuyệt đối** |
| T3 | SQL nhánh rollback trùng TEXT với SQL production hiện tại | PASS |
| T4 | `get_gated_state` live path, cả 2 nguồn | 0 diffs / 43 phiên; hôm nay 3→3, `DT5G_macro` |

## 5b. Bề mặt tác động THẬT của guard (chạy thêm theo đề nghị quant-skeptic)

Chạy thêm nhánh `BREADTH_SRC=off` (guard tắt hoàn toàn) để đo chính guard đó đáng bao nhiêu:

| So sánh | Phiên cap đổi | Phiên **state** đổi |
|---|---|---|
| guard OFF vs guard ON (`prune`, = production hôm nay) | 18 | **0** |
| guard OFF vs guard ON (`pit`, = patch) | 5 | **0** |

⇒ **Guard breadth-decoupling chưa từng đổi state DT5G lấy một phiên nào trong 12 năm**, với CẢ HAI
nguồn. Nó là bảo hiểm ngủ đông ở tầng state (chỉ chạm `cap` vài chục phiên, luôn ở chỗ base đã
thấp hơn cap). Điều này *củng cố* kết luận "0 diff" nhưng cũng đóng khung nó cho đúng: ta đang
migrate một cấu kiện hiện **dormant**, nên "0 phiên đổi" là kết quả tất yếu chứ không phải bằng
chứng hai nguồn tương đương trong một cơn US-panic tương lai. Rủi ro thật vẫn là §6 mục 1 và câu
trả lời cho nó là nhánh rollback 1 dòng, không phải thêm số liệu lịch sử.

## 6. Giới hạn / điều KHÔNG kết luận

1. **"0 diff state" không có nghĩa guard vô dụng** — guard chỉ có tác dụng khi Pillar B (VIX/SPX)
   đang muốn áp cap; 2818/3135 phiên không có cap nào. Kết luận đúng là: *trên toàn bộ lịch sử
   giao nhau giữa "US panic" và "breadth đổi", không có phiên nào lật state*. Nếu tương lai có
   một episode US-panic mà breadth nằm sát 0,50, hai nguồn CÓ THỂ cho kết quả khác nhau — đó là
   lý do vẫn phải giữ nhánh rollback.
2. Không đo lại backtest NAV (V4/V5) vì state input **không đổi 1 phiên nào** ⇒ NAV bất biến theo
   cấu tạo, chạy thêm chỉ tốn tài nguyên.
3. Không đụng ngưỡng, không đụng base v3.4b, không đụng DT-4gate, không đụng Pillar A/B —
   đúng phạm vi instruction hôm nay ("migrate breadth guard"), không phải toàn quyền sửa DT5G.
4. `ticker_prune` vẫn bị đọc ở nơi khác (CAPIT pool + ADV cap trong `golive_recommend_v23.py`) —
   CỐ Ý, ngoài phạm vi việc này.

## 7. Việc còn lại khi merge (Mike/user bấm nút)

0. **Sau khi áp patch**, chạy lại parity check trên chính module production đã merge (không phải
   file `.PROPOSED.py`) để bắt lỗi sao chép — đề nghị của quant-skeptic, 1 lệnh:
   `BREADTH_SRC` không còn dùng, chỉ cần `proposed_selfcheck.py` sửa T2 trỏ vào file đã merge.
1. Áp `dt5g_breadth_pit.patch` vào `macro_state_live.py`.
2. Cập nhật `CLAUDE.md` §DT5G mục 4 — câu "Breadth = % of `ticker_prune` above MA200" thành
   `universe_pit` + 1 dòng changelog 2026-07-29.
3. Republish `tav2_bq.vnindex_5state_dt5g_live` (không bắt buộc về mặt số — 0 phiên đổi — nhưng
   nên chạy để bảng và code cùng vintage).
4. `mike/kb/data_registry/`: đã cập nhật trong việc này (mục 8).
