# Bank-nodata phương án B — fail-closed ở đường tiền (job Taylor_20261119_145312)

## KẾT LUẬN (đọc trước)

1. **Code đã đạt ý định fail-closed ở đường tiền, nhưng CHƯA LIVE.** Commit `be7b01fa5` trên nhánh
   `session/bank-nodata-fail-closed-20261119` (worktree sparse `/home/trido/thanhdt/WorkingClaude/wt-bank-nodata-20261119`,
   nằm trên `d0a14445e` của phương án A). Chưa merge, chưa regen `data/rating_8l_history.csv`, chưa ghi BQ.
   Sau khi merge và cron tiếp theo chạy `rating_8l_history.py` (17:30 ICT trong cửa sổ KQKD, hoặc thứ Bảy
   08:30), `tav2_bq.fa_ratings_8l` mới đổi theo.
2. **Tác động live khi áp: đúng 5 mã ngân hàng đổi hạng, đều từ ≤3 lên 4** (ABB 3→4, PCB 3→4, VAB 3→4,
   VBB 3→4, KLB 2→4). Cả 5 đang `in_universe=true` trong `universe_pit` (19/11). **Không mã nào đang giữ**
   ở SpaceX/ZaloPay (`dnse_raw_2026-11-19.jsonl`), **không có trong plan tháng 11 nào** (0/44 file). BAB/BVB/PGB
   (4) và NVB/SGB (5) không đổi. Hệ quả: cổng LAG (tầng tín hiệu + ORDER), custom30V và cờ yếu BAL sẽ chặn
   mua mới 5 mã này. Lệnh bán không bị ảnh hưởng.
3. **Cổng chặn (rủi ro chính):** khi lens đọc lỗi/rỗng (G1), lens mâu thuẫn với nhãn (G2), tỉ lệ nodata
   >45% (G3), hoặc có mã từng có lens ở snapshot kỳ trước nay thành nodata (G4) ⇒ run đó **KHÔNG hạ hạng mã
   nào** và gửi cảnh báo vào Trading Daily kèm bằng chứng thật. Trong mọi nhánh này cổng **fail-OPEN** về
   hành vi trước phương án B. Lý do: hạ hàng loạt khi lens hỏng sẽ chặn mua LAG cả MBB/VPB/VIB đang giữ.
4. **Rủi ro còn lại:** (a) khi cổng bật, 5 mã trên quay lại 3/2 và lại lọt cổng ≤3 cho tới khi người
   sửa xong lens. Lúc đó cảnh báo là lớp bảo vệ duy nhất. (b) Snapshot G4 (`data/bank_lens_ticker_snapshot.json`)
   chỉ được tạo sau run canonical đầu tiên sau merge. Từ giờ tới lúc đó G4 không kiểm được gì, còn G2
   phủ ca lens đọc lỗi. (c) Cần quant-skeptic và arch-reviewer duyệt (đường tiền), sau đó user duyệt riêng.
5. **Mục 3 (hạng 3 bịa khi ROE trống trong lịch sử): 0/1.009 dòng BANK giai đoạn 2014-06→2026-11 bị dính**
   (28 mã). Lens live cũng không có dòng `bank-noROE` nào (0/18). ⇒ Đề xuất **không sửa lịch sử**: không có
   lệnh pin nào chịu ảnh hưởng. Ở dòng live, `bank-noROE` được đưa vào cùng luật sàn 4 và cùng cổng chặn
   (hiện tác động bằng 0, chỉ để chặn trước).

## 1. Thay đổi code (`git diff d0a14445e be7b01fa5`, 5 file, +440/−53)

- `rating_8l_history.py::override_current_bank_aq(out, live_run=False)`: với dòng live mang nhãn `bank-nodata` hoặc
  `bank-noROE`, dòng có `eff_date` mới nhất của mã đó = **max(proxy, live, BANK_NODATA_FLOOR=4)**. Kết quả
  không bao giờ tốt hơn proxy. Có sàn 4 cố định nên đúng ngay cả khi `rating_8l.py` chưa đổi (A/B chạy trên
  `data/rating_8l.csv` thật, nơi nodata vẫn =3). Mã có lens thật vẫn nhận hạng live như cũ. Không có cột
  `note` ⇒ vẫn loại mọi override (§28).
- `bank_nodata_gate(lb)` gồm 4 nhánh. Bất kỳ nhánh nào bật ⇒ cả run không hạ hạng, đồng thời gọi `_bank_gate_alert`:
  | Nhánh | Điều kiện | Hướng | Vì sao |
  |---|---|---|---|
  | G1 | `data/bank_lens_v3.csv` đọc lỗi, rỗng, hoặc thiếu cột `ticker` | fail-open (giữ proxy) | `rating_8l.py:551-556` chỉ print ⇒ MỌI bank thành nodata ⇒ hạ cả MBB/VPB/VIB đang giữ |
  | G2 | mã mang nhãn `bank-nodata` nhưng CÓ trong lens file | fail-open | 2 nguồn mâu thuẫn (lens đọc lỗi lúc 19:20, hoặc `rating_8l.csv` cũ hơn lens). In mtime cả 2 file; nguyên nhân để ngỏ (§29) |
  | G3 | (nodata ∪ noROE)/số mã BANK > **45%**, hoặc 0 dòng BANK | fail-open | xem ngưỡng bên dưới |
  | G4 | mã có lens ở snapshot kỳ trước nay `bank-nodata`, hoặc snapshot đọc lỗi | fail-open | bắt trường hợp mất lens từng mã, kể cả khi file lens vẫn đọc được |
- **Ngưỡng G3 = 45%, không phải 35%.** Hiện trạng là 10/28 = 35,7%, và đây là con số CẤU TRÚC (18 mã có
  lens trên 28 mã BANK). Ngưỡng 35% như đề xuất ban đầu sẽ bật cổng ngay hôm nay. Mức 45% còn chừa chỗ cho
  2-3 mã bank mới niêm yết chưa có lens (12/30 = 40,0%, 13/31 = 41,9%), và vẫn bật khi mất từ 3 mã lens
  (13/28 = 46,4%). Mất 1-2 mã lens thì G2/G4 bắt.
- **Cảnh báo:** luôn in banner vào log. Biến `R8L_BANK_GATE_ALERT_SINK` cho phép ghi ra file (dùng cho
  selfcheck). Gửi `mike/bin/notify_thread.sh "<msg>" trading_daily` **chỉ** khi `live_run` (đích ghi là
  canonical, hoặc `R8L_HIST_BQ_REFRESH=1`) và không ở `MIKE_BOT_TEST_MODE=1`. Đây là cùng cơ chế mà
  `fa_ratings_ticker_gate.sh`/`refresh_fa_ratings_8l.sh` đang dùng. Nếu gửi lỗi, script in rc và stderr thật.
- Snapshot lens được ghi atomic (tmp + `os.replace`) **chỉ** khi `live_run` và cổng không bật. Khi cổng
  bật thì giữ snapshot cũ, nên lần chạy sau vẫn bật tiếp cho tới khi người sửa.
- `main()`: phần tính `path`/`_canon` được dời lên trước override (thuần tính toán) để truyền `live_run`.
  Logic refresh BQ không đổi.
- Docstring override (mục 5): đã viết lại theo luật mới (nodata/noROE ⇒ hạ hạng, sàn 4; proxy noROE ở
  lịch sử vẫn trả 3). Comment ở `rating_8l.py:421-424` cũng đã cập nhật.

## 2. A/B trên dữ liệu thật — `b/ab_run.py`, `b/ab_diff.txt`

Chạy `main()` của bản HEAD (`d0a14445e`) và bản mới trên CÙNG dữ liệu BQ (pull một lần, dùng `bq()` memo),
ra `/tmp`, với `R8L_HIST_NO_BQ_REFRESH=1` + `MIKE_BOT_TEST_MODE=1`. Đọc `data/rating_8l.csv` thật (nodata =3).

- 54.870 vs 54.870 dòng. **Có đúng 5 dòng khác, và cả 5 đều là dòng mới nhất của mã đó:** ABB 2026-10-22 3→4,
  KLB 2026-10-26 2→4, VAB 2026-10-27 3→4, VBB 2026-10-29 3→4, PCB 2026-11-02 3→4. Chỉ cột `rating`/`tier` đổi.
  Mọi dòng lịch sử khác giống từng byte (`diff` chỉ ra 5 hunk).
- Cổng không bật trên dữ liệu hôm nay: lens đọc được 18 mã, 10 nodata không mã nào nằm trong lens, tỉ lệ
  35,7%, chưa có snapshot.
- Mã nodata còn lại giữ nguyên: BAB/BVB/PGB = 4, NVB/SGB = 5 (vì max với proxy).

## 3. Mục 3 — hạng 3 bịa khi ROE trống (`b/measure_noroe.py`, `b/noroe_rows.csv`)

Lệnh: pull `HIST_SQL`+`ICB_SQL` thật, route BANK, lọc dòng có `ROE_Trailing`, `ROE5Y`, `ROE3Y` đều NULL.
Kết quả: **0 dòng trên 1.009 dòng BANK, 28 mã, giai đoạn 2014-06-30→2026-11-18**. Dòng mới nhất hôm nay: 0 mã.
`data/bank_lens_v3.csv`: 0/18 mã có ROE trống ⇒ hôm nay không có nhãn `bank-noROE` nào.
⇒ Chưa có cặp (mã, quý) nào chạm cổng ≤3 vì nhánh này, nên **không lệnh LAG/BAL pin nào từng mua theo nó**.
Đề xuất: giữ nguyên `rate_bank_hist`/`rate_bank_proxy` (đổi chỉ là phòng hờ, mà lại chạm chuỗi backtest).
Phía live đã xử lý trong cùng cổng (noROE ⇒ sàn 4).

## 4. Selfcheck — `b/selfcheck_runs.log`

| Selfcheck | env -u TZ | TZ=Asia/Tokyo |
|---|---|---|
| `rating_8l_history_bank_nodata_gate_selfcheck.py` (MỚI) | PASS 33/0 | PASS 33/0 |
| `rating_8l_bank_nodata_selfcheck.py` (sửa test 4) | PASS 14/0 | PASS 14/0 |
| `rating_8l_history_bank_aq_selfcheck.py` (sửa test 4; real panel 0 gate flip) | PASS 34/0 | PASS 34/0 |
| `rating8l_eff_guard_selfcheck.py` | PASS | PASS |
| `rating8l_icb_pit_selfcheck.py` (`$DNA_PYEXE` 3.12) | 16 PASS / 2 SKIP | 16 PASS / 2 SKIP |

- Selfcheck mới phủ: T1 proxy 3/2/5 + live 4 ⇒ 4/4/5; live 3 ⇒ vẫn 4/4/5 (nhờ sàn); noROE ⇒ 4. T2 lens vắng,
  rỗng, hoặc hỏng ⇒ không hạ + cảnh báo G1. T3 4/7 = 57% ⇒ không hạ (G3); 4/9 = 44,4% ⇒ hạ bình thường.
  T4 G2. T5 snapshot mất mã, snapshot hỏng ⇒ G4. T6 153 dòng lịch sử giống từng byte, proxy 5 không bao giờ
  bị nâng. T7 live_run gọi notify giả + chỉ ghi snapshot khi cổng tắt; run thí nghiệm không gửi, không ghi.
  **T8 đầu-cuối (đúng chỗ arch-reviewer chỉ ra là còn thiếu):** dùng history canonical thật + `rating_8l.csv`
  thật + lens thật ⇒ dedup kiểu `fa_ratings_8l` (`ROW_NUMBER` theo ticker,eff_date, `ORDER BY q_time DESC`) +
  đọc as-of mới nhất ⇒ cả 10 mã nodata >3 (ABB/BAB/BVB/KLB/PCB/PGB/VAB/VBB = 4, NVB/SGB = 5).
- **Đột biến:** (a) `max→proxy-only` ⇒ 3 assertion FAIL; (b) bỏ cổng chặn ⇒ 14 assertion FAIL. Cả hai đều bị bắt.
- `rating8l_icb_pit_selfcheck.py` dưới `python3` 3.10 bị SyntaxError ở dòng 158 (f-string chứa backslash).
  **Lỗi này có sẵn**: bản HEAD cũng lỗi y hệt, và đây là lỗi riêng của interpreter, không do thay đổi này.
  Với `$DNA_PYEXE` thì PASS.
- Notify trong selfcheck luôn trỏ tới script giả (`R8L_BANK_GATE_NOTIFY`), nên không bao giờ gửi Discord thật.

## 5. Mục 5 — `rating_8l_screener.csv` (`b/screener_diff.txt`)

Đã tái sinh `rating_8l.py` bản cũ (`d0a14445e~1`) và bản mới vào 2 WORKDIR tạm `/tmp/taylor_r8l_ab/{old,new}`,
lệnh `OSHARES_RECONCILE=0 $DNA_PYEXE rating_8l.py`. File thật không bị ghi (mtime vẫn 19/11 19:20).
- `rating_8l.csv` khác đúng 9 mã (3→4): ABB, BAB, BVB, NVB, PCB, PGB, SGB, VAB, VBB. KLB vốn đã =4 ở cả 2 chân.
- `rating_8l_screener.csv` có 100 → 96 dòng (rớt ABB, BVB, NVB, VAB). Trên **96 dòng còn lại**:
  `value_yield_pct` đổi **16/96** (14 BANK do rank trong route, cộng NT2 [POWER] và BVH [INSURANCE] vì 2 route này
  <5 mã nên rơi về rank toàn cục), `value_pct` đổi **91/96** (|Δ| max 0,063, trung vị 0,010), `zone` đổi
  **1/96**: **HAH 1_BUY-NOW → 2_ACCUMULATE** (value_pct 0,701 → 0,683, sát mép 0,70).
- `rating_8l_buynow.csv` và `rating_8l_top30.csv` giống từng byte.
- Screener chỉ dùng để hiển thị/discretionary. HAH đổi zone là hệ quả cơ học của việc tập percentile co lại,
  không phải tín hiệu.

## 6. Tác động LIVE lên `fa_ratings_8l` nếu áp

| Mã | fa_ratings_8l hiện (proxy) → mới | universe_pit 19/11 (lần đầu vào) | Đang giữ | Plan T11 |
|---|---|---|---|---|
| ABB | 3 → 4 | true (từ 2021-03-29) | không | không |
| KLB | 2 → 4 | true (2021-01-12) | không | không |
| PCB | 3 → 4 | true (2026-11-06, mới vào) | không | không |
| VAB | 3 → 4 | true (2021-10-13) | không | không |
| VBB | 3 → 4 | true (2021-05-31) | không | không |
| BAB/BVB/PGB/NVB/SGB | không đổi (4/4/4/5/5) | BVB, NVB true; BAB, PGB, SGB false | không | không |

Nguồn: BQ `tav2_mike.universe_pit` (MAX(time) = 2026-11-19). Vị thế lấy từ `positions` cuối trong
`data/execution_logs/dnse_raw_2026-11-19.jsonl`, lọc theo account, không gọi DNSE: SpaceX = FPT HT1 MBB MCH NNC
VGS VIB VPB, ZaloPay = thêm DGC. Plan: `grep -lE` 10 mã trong `data/trade_plans/plan_*_2026-11-*.json` ⇒ 0/44 file.

**Lợi suất các lệnh pin từng mua (MÔ TẢ, không phải backtest wire)** — `b/pin_trades.py`, `b/pin_trades.txt`,
ledger `2026-11-13__ladderA3-L3P-advsrcpit-{pin0pct,pin1M}`. Lợi suất mỗi holding = (bán − phí)/(mua + phí) − 1.
| Tập | pin0% (SÀN) | pin1M (TRẦN) |
|---|---|---|
| 5 mã đổi hạng | 7 holding (LAG 5 / BAL 2), **0 holding đi hết vòng** (đều ABANDONED_REFUND); TB theo vốn **+1,96%**, vốn 31,39 tỷ | 11 holding (LAG 7 / BAL 4), 2 đi hết vòng (ABB LAG 2025-08 **−6,50%**, ABB BAL 2025-08 **+2,38%**); TB theo vốn **−0,89%**, vốn 73,32 tỷ |
| Cả 10 mã nodata | 13 holding, TB **−0,24%** | 17 holding, TB **−1,06%** |

Đọc số: N rất nhỏ, phần lớn là lệnh vào dở rồi bị hoàn (ABANDONED_REFUND). Không rút ra được edge âm hay
dương nào. Phương án B **không đổi** các số pin vì chuỗi lịch sử giữ nguyên. Nó chỉ chặn mua mới từ nay.

## 7. Còn phải làm (không thuộc job này)

- quant-skeptic + arch-reviewer duyệt `be7b01fa5` (đường tiền), sau đó user duyệt riêng rồi Mike merge.
- **Worktree sparse ⇒ pre-commit KHÔNG chạy** (`PRE_COMMIT_ALLOW_NO_CONFIG=1`). Khi merge vào checkout đầy đủ
  phải chạy `pre-commit run --files rating_8l_history.py rating_8l.py rating_8l_history_bank_nodata_gate_selfcheck.py
  rating_8l_history_bank_aq_selfcheck.py rating_8l_bank_nodata_selfcheck.py`. Đã chạy tay
  `mike/bin/tz_anchor_gate.py` trên cả 5 file: rc=0 (đầu dò `datetime.now()` cố ý thì bị bắt, tức gate có chạy).
- Sau merge: lần chạy canonical đầu tiên sẽ tạo `data/bank_lens_ticker_snapshot.json`. Nên kiểm log thấy dòng
  `downgrade-only ... đổi 5` và không có banner CỔNG CHẶN.
- Worktree được GIỮ lại để Mike review. `/tmp` của job đã dọn. 209 thư mục `/tmp/r8l_*` có từ trước 21:50,
  không phải của job này, nên không xoá.
