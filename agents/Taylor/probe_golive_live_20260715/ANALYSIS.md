# golive_recommend_v23 — BQ live vs BQ_LOCAL_CACHE: điều tra + đề xuất
Job `Taylor_20260715_103016` · Taylor · 2026-07-15 · **CHƯA ÁP DỤNG GÌ — chờ Mike/user quyết**

---

## 0. Kết luận ngắn (đọc dòng này trước)

Vấn đề THẬT nghiêm trọng hơn "lệch pha 1 ngày": **nguồn dữ liệu của golive_recommend_v23 đang
TỰ LẬT qua lại giữa live BQ và cache theo từng ngày**, phụ thuộc đêm hôm trước sync có verify
pass hay không. Đây là **coin-flip**, không phải một tradeoff cache-vs-live.

Bằng chứng từ log production thật (không phải suy luận):

| Phiên | Cache verified đêm trước? | golive đọc gì | `signal_date` xuất cho DollarBill |
|---|---|---|---|
| 07-13 | FAILED | **LIVE** (fail-open) | 2026-07-13 = **hôm đó** ✅ |
| 07-14 | OK | **CACHE** | 2026-07-13 = **T-1** ❌ |
| 07-15 (tối nay) | FAILED (07-14 23:53) | **LIVE** | dự kiến 07-15 ✅ |

Chi phí chuyển hẳn sang live: **+14 giây/phiên** và **$0.60/năm**. Buffer tới hạn chót là **2 giờ**.
→ Đề xuất **Phương án A: pop `BQ_LOCAL_CACHE` process-local trong đúng golive_recommend_v23.py**
(y hệt mẫu C1 đã verify), KHÔNG tắt cache toàn cục, KHÔNG làm routing theo bảng.

---

## 1. Phạm vi thật — grep code, không đoán

Chuỗi pipeline-2: `bq_freshness_check.sh` → `$DNA_PYEXE deploy_golive_dt5g_v4/golive_recommend_v23.py`
→ import `simulate_holistic_nav.bq` (điểm duy nhất route cache) + `signal_v11_sql.SIGNAL_V11`
+ `custom30.current()` + `lag_live_schedule.live_lag_candidates()`.

**9 query BQ/phiên** (đo thật bằng traced probe, không đếm tay). Bảng đọc qua `BQ_LOCAL_CACHE`:

| # | secs (live) | GB quét | Bảng |
|---|---|---|---|
| q1 | 4.48 | 0.310 | SIGNAL_V11: ticker, ticker_1m, ticker_prune, ticker_financial, fa_ratings, vnindex_5state_dt5g_live |
| q2 | 2.55 | 0.012 | D1 RE_BACKLOG: cùng nhóm trên |
| q3 | 2.24 | 0.003 | ticker (VNINDEX overheat) |
| q4 | 2.02 | 0.000 | vnindex_5state_dt5g_live |
| q5 | 2.09 | 0.001 | **fa_ratings_8l** |
| q6 | 2.02 | 0.053 | ticker (sec_map ICB — full-table, không lọc time) |
| q7 | 2.17 | 0.001 | ticker_prune (breadth oversold) |
| q8 | 2.05 | 0.003 | ticker (VNINDEX dd52w/rv10) |
| q9 | 2.18 | 0.000 | **custom30v_8l** (rổ parking) |

**8 bảng riêng biệt**: `ticker`, `ticker_1m`, `ticker_prune`, `ticker_financial`, `fa_ratings`,
`fa_ratings_8l`, `vnindex_5state_dt5g_live`, `custom30v_8l`.
`lag_live_schedule` KHÔNG đọc BQ (pkl + CSV local) → ngoài phạm vi.

## 2. Hiệu năng & chi phí — đo thật, không ước

Đo bằng probe copy (`golive_probe.py`, output đổi hướng sang thư mục probe — production artifact
KHÔNG bị chạm, mtime vẫn 07-14 19:01):

- **Cache-on** (bản copy cache ép `verified=true`, cô lập): **9.4s**
- **Live** (pop `BQ_LOCAL_CACHE`): **22.7s** — trong đó 21.8s là 9 query, mỗi query ~2s overhead `bq` CLI
- **Delta: +13.3s/phiên**
- **Chi phí: 0.384 GB/phiên → $0.0024/phiên → $0.60/năm** (on-demand $6.25/TB, dry-run từng query)

Khung giờ: pipeline chạy **19:00**, hạn chót `send_plan_report` **21:00** → buffer **2 giờ**.
Toàn bộ bq_freshness_check hiện xong trong ~2 phút (log 07-14: header 19:00 → artifact 19:01:38).
**+13s là nhiễu, không phải rủi ro.** Live path cũng KHÔNG phải đường chưa thử — nó đã chạy
production thật ngày 07-13 (fail-open) và trong probe hôm nay, ra output hợp lệ đủ 30 dòng recs.

## 3. Hai lỗi cấu trúc bắt được trong lúc điều tra

### 3.1 Cache tái lập lại ĐÚNG con bug C1, ở bước ngay sau C1 — và làm reschedule 07-10 thành NO-OP
`publish_gated_state` (pipeline-1) ghi state hôm nay vào `vnindex_5state_dt5g_live` lúc ~19:01,
rồi `golive_recommend_v23` (pipeline-2) **đọc lại bảng đó qua cache = bản T-1**. Log production 07-14:

```
pipeline-1:  today: as_of=2026-07-14 state=3 source=DT5G_macro     ← vừa publish 07-14
pipeline-2:  latest signal date: 2026-07-13                        ← đọc cache, lùi 1 phiên
pipeline-3:  [push] signal_date=2026-07-13                         ← đẩy lên BQ partition 07-13
```

Việc dời cron 17:30→19:00 (2026-07-10) mục đích là "chạy SAU daily_refresh 18:30 để đọc DT5G HÔM NAY,
không phải hôm qua". **Trên những ngày cache verified, mục đích đó bị cache vô hiệu hoá hoàn toàn** —
đúng loại NO-OP như lần siết `MAX_STATE_LAG` 2→1.

### 3.2 Gate freshness kiểm bảng LIVE, consumer đọc CACHE
`bq_freshness_check.sh::_check` gọi thẳng `bq query` CLI → kiểm **live**. golive đọc **cache**.
Nghĩa là gate đang xác nhận độ tươi của dữ liệu mà consumer không hề dùng. Trên ngày cache-on,
gate ALL FRESH không nói gì về cái golive thực sự đọc.

## 4. Lệch pha có ĐỔI KẾT QUẢ không? — có, đo được hôm nay

Diff output cache-run vs live-run (cùng script, cùng phút, chỉ khác nguồn):

- `signal_date` 07-14 → **07-15**; `breadth_oversold` 16.6% → **18.2%**; `dd52w` −6.6 → **−7.6**
- **Rổ parking custom30V đổi thành viên: cache có VGC, live có PVS** (+ rating 8L đổi: VHM 2→3, HAH 1→2)

Cơ chế (verify trực tiếp trên BQ, không đoán): `custom30v_8l` được **republish lúc 15:33 ICT hôm nay**
(lastModifiedTime) sau khi Winston refresh `fa_ratings_8l` (06-20→07-14). Cache giữ snapshot 07-14 23:45.

| ticker | LIVE (07-15) | CACHE (07-14 23:45) |
|---|---|---|
| PVS | weight 0.007988, 8L=3 | **không có** |
| VGC | **không có** | weight 0.007449, 8L=2 |
| VHM | 8L=3 | 8L=2 |
| HAH | 8L=2 | 8L=1 |

Parking = **70% tiền nhàn rỗi trong NEUTRAL**, và là **cấu phần đáng tin nhất của V2.4 (+7.4pp Full)**.
Trên ngày cache-on, DollarBill được đưa một rổ có mã đã bị loại khỏi rổ production.

Lưu ý phụ (đáng 1 việc riêng, không nằm trong scope job này): sync verify `custom30v_8l` **chỉ đếm row**
(1440 vs 1440 → "OK"), nên **mù hoàn toàn với republish cùng số dòng khác nội dung** — đúng ca hôm nay.

## 5. Phương án

### A — pop `BQ_LOCAL_CACHE` process-local trong golive_recommend_v23.py ⭐ ĐỀ XUẤT
```python
# ngay TRƯỚC `from simulate_holistic_nav import bq`
os.environ.pop("BQ_LOCAL_CACHE", None)
```
Đúng mẫu C1 đã quant-skeptic CONFIRMED (`publish_gated_state.py`). Process-local: mỗi step trong
bq_freshness_check là subprocess riêng → KHÔNG leak sang papertrade/backtest/sector-screener.
`wc_env.sh` KHÔNG bị đụng.
- Được: hết coin-flip; state/giá/rổ parking đúng phiên hôm nay; reschedule 19:00 có tác dụng thật; gate freshness (live) và consumer (live) cuối cùng nói cùng một thứ.
- Mất: +13s/phiên, $0.60/năm.
- Rủi ro tồn dư: golive sẽ đọc `ticker_financial` live **đang hỏng** (max time 05-04) — xem §6.

### B — routing theo từng bảng (live cho fa_ratings_8l/custom30v_8l/dt5g/ticker*, cache cho ticker_financial/fa_ratings)
**KHÔNG đề xuất.** Lý do: (1) tiết kiệm được ~13s và $0.60/năm — không đáng; (2) phải viết cơ chế
routing table-level mới trong `bq_local_cache` = code mới, failure mode mới, ngay trên đường tạo plan
tiền thật; (3) "cache che chở khỏi ticker_financial hỏng" là **tình cờ, không phải thiết kế** — cache
fail-open nên hôm nay nó KHÔNG che chở gì cả, và khi upstream sửa xong + sync lại thì lớp che đó bốc hơi.
Không nên xây machinery dựa trên một sự tình cờ.

### C — giữ nguyên
Nghĩa là chấp nhận nguồn dữ liệu của plan tiền thật do coin-flip quyết định. Không nên.

## 6. Điều kiện tiên quyết / sequencing (quan trọng)

`ticker_financial` **live đang hỏng** (MAX(time)=2026-05-04 vs cache 07-08; đang chờ user quyết
hướng khôi phục). Nó feed q1/q2 (SIGNAL_V11 + D1).

- Phương án A **KHÔNG làm hôm nay tệ đi**: cache đang fail-open từ 07-14 23:53 → golive **đã** đọc
  bản hỏng rồi. A chỉ biến hành vi từ *tình cờ* thành *tất định và đọc được trong log*.
- Nhưng đừng coi A là fix cho vụ ticker_financial. Hai việc độc lập.
- Gate hiện tại KHÔNG bắt được vụ này: `MAX_FIN_LAG=90` calendar-days, lag thực ~72d → PASS. (Ghi
  nhận để cân nhắc riêng, không tự sửa.)

## 7. Đề xuất trình user

1. **Duyệt A** — 3 dòng code, 1 file, đúng mẫu đã verify. Sau đó route qua quant-skeptic như C1.
2. Việc riêng (không gộp): sync verify content-hash cho custom30v_8l/custom30_8l (count-only đang mù).
3. Việc riêng (không gộp): cân nhắc fail-open của cache — production pipeline im lặng đổi nguồn theo
   trạng thái verify là nguồn gốc của non-determinism. A làm câu hỏi này thành vô nghĩa *cho golive*,
   nhưng consumer khác vẫn dính.

## 8. Công khai một sai sót của chính tôi trong lúc điều tra

Khi tạo bản copy cache để mô phỏng cache-on, tôi dùng `cp -al` (hard link) rồi ghi `verified=true`
vào manifest bản copy — **ghi xuyên qua hard link vào manifest THẬT**, khiến cache thật hiện
`verified=true` trong ~60 giây (17:34:28 → ~17:35:30). Nếu có consumer nào chạy đúng lúc đó, nó sẽ
tin một cache đã fail verification.
- Đã tự phát hiện ngay (in ra để tự kiểm chứng), khôi phục đầy đủ: `verified=false`,
  `verified_at=2026-07-14T16:53:05Z`, `verified_at_epoch` đúng, `indent=2` khớp `sync_bq_cache.py`,
  hard link đã cắt (links=1).
- Không có cron nào chạy trong khung 17:34-17:36 (gần nhất: 18:30 daily_refresh) → thực tế không ai đọc.
- Bài học: `cp -al` + ghi đè in-place = ghi vào bản gốc. Copy để thí nghiệm phải cắt link trước khi ghi.

## 9. Artifact (evidence, thư mục experiment — không phải canonical)
`mike/agents/Taylor/probe_golive_live_20260715/`
- `golive_probe.py` / `golive_probe_traced.py` — bản copy đã patch (OUTDIR + status → probe dir; `PROBE_LIVE=1` → pop cache)
- `out/` — kết quả LIVE + `trace.json` (timing từng query) · `out_cache/` — kết quả CACHE
- Production artifact KHÔNG bị chạm: `data/golive_v23_status.json` và `out/golive_v23_recommendations_2026-07-14.*` giữ nguyên mtime 07-14 19:01.
