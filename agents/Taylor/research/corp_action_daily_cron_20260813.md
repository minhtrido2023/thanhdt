# Cron cập nhật cổ tức + Oshares theo corp-action — thiết kế, số đo, §11 (2026-08-13)

Job `Taylor_20260813_091128`. Yêu cầu user: cron hàng ngày cập nhật **cash dividend + Oshares**,
corp-action làm anchor, **trigger vào đúng ngày sự kiện của từng mã**, và **không có bước LLM tính
số nào trong vòng lặp runtime** (LLM viết code một lần, cron chạy lại đúng file đó).

## File

| File | Vai trò | Trạng thái |
|---|---|---|
| `mike/bin/corp_action_daily.py` | toàn bộ logic — lịch trigger, 4 cổng, đối soát, cảnh báo | MỚI |
| `mike/bin/corp_action_daily.sh` | vỏ cron (chỉ để `source wc_env.sh` lấy `CLOUDSDK_CONFIG`) | MỚI |
| `mike/bin/corp_action_daily_selfcheck.py` | 61 ca, **hermetic** (không BQ/Discord) | MỚI |
| `oshares_live.py`, `corp_action_lib.py`, `dividend_adjusted_return.py` | **KHÔNG SỬA** — dùng lại nguyên | cũ, đã CONFIRMED |

Không một công thức tài chính mới nào nằm trong code mới. `oshares_at` / `_roll` / `_dedup_iss` /
`bq_corp_action` / `is_price_adjusting` đều được **import**, không chép lại.

## §11 — bốn câu hỏi bắt buộc trước khi đặt lịch

**1) Đọc gì + vintage.**

| Nguồn | Vintage | Ghi chú |
|---|---|---|
| `tav2_bq.corporate_action` | **T-1 tối** | BQ LIVE — `BQ_LOCAL_CACHE` bị `os.environ.pop()` ngay đầu file (§11: script publish không đọc cache T-1) |
| `tav2_bq.ticker_financial.OShares` | theo QUÝ, trễ tới ~3 tháng | chỉ dùng để ĐỐI SOÁT, không bao giờ dùng làm số công bố |
| `data/execution_logs/active_nav_<label>.json` | **T-1 tối** (cron 20:15 ICT) | chỉ lấy danh sách mã + qty; không đọc field tiền nào (§25 không áp dụng) |

**2) Nguồn tươi lúc nào — ĐO THẬT, không tin comment.** `MAX(ingested_at)` của
`corporate_action` = `2026-08-12 15:22:57 → 15:48:52 UTC` = **22:22 → 22:48 ICT**. Đó là lô nạp
đầu tiên và duy nhất tính tới 2026-08-13 16:30 ICT. **n=1** ⇒ không được biến thành giả định về
lịch: script **tự đo lại mỗi lần chạy** và phân loại `FRESH / STALE / DEAD`.

**3) Cần T hay T-1.** **T-1 là đủ.** Mọi câu hỏi ở đây là "ngày ex-right / effective là ngày nào"
— thuộc tính CẢ NGÀY, công bố trước, không đổi trong phiên. Không có phép tính nào cần giá/tiền
same-day ⇒ **không chạm bright-line §6** (same-day thì phải hỏi DNSE chứ không phải BQ): script cố
ý không đặt câu hỏi nào same-day.

**4) Ai tiêu thụ + deadline.** Hôm nay: **NGƯỜI** — cảnh báo Discord `trading_daily` về sự kiện
quyền ≤10 ngày trên mã đang giữ, phải tới **trước `preflight_check.sh` 08:45** (lúc user duyệt
plan). Snapshot `data/corp_action_daily/*.json` là artifact cho consumer MÁY tương lai (backtest
point-in-time, report/rating live) — **chưa có consumer máy nào**, và consumer bắt buộc đọc cờ
`usable`.

**Giờ chọn: 07:30 ICT (= `30 0 * * 1-5` UTC), T2-T6.** Sau lô vendor ~22:2x ICT hôm trước 9 tiếng
(chịu được trượt), sau `compute_active_nav_all.sh` 20:15 ICT hôm trước, trước `ops_health_check.sh`
08:20 và `preflight_check.sh` 08:45. Không đụng slot nào đang dùng. Thời gian chạy đo thật **58s**.

## Lịch trigger — sự kiện tự chọn ngày của nó

Một sự kiện chạm hệ thống **HAI lần**, và cả hai đều được ghi:

* `exright_date` (DIV/ISS) — giá tách quyền; Oshares nhảy theo **ước lượng** (`ISS_ESTIMATE`).
  Sự kiện KHÔNG điều chỉnh giá (ESOP/riêng lẻ/chuyển đổi TP) vẫn có `exright_date` trong bảng, nên
  vẫn vào nhóm này — chúng không làm giá nhảy nhưng vẫn tăng số CP.
* `AIS.effective_date` — CP mới chính thức vào lưu hành, **trễ tới ~7 tuần** (Bẫy 1). Ước lượng
  được thay bằng số của sở (`AIS_EXACT`).

Đúng cái khoảng giữa hai lần đó là khoảng `ticker_financial.OShares` sai — và là khoảng có số.

## Ngưỡng — hai con số, neo bằng số đo

* **0,1%** = "bằng nhau về mặt vật chất" cho mọi phép so số CP. **Import `oshares_live.EXPLAIN_TOL`
  chứ không chép lại** — hai ngưỡng cho cùng một khái niệm là cách sinh hai kết luận trái nhau trên
  cùng dữ liệu. Neo: sai số hợp lệ lớn nhất đo được là làm tròn CP lẻ của FPT **0,0013%**; ca
  RESTATE thật của HAH **10,05%**. 0,1% cách mỗi đầu hai bậc độ lớn.
* **`SYSTEMIC_MIN=3` mã VÀ `SYSTEMIC_FRAC=5%`** = ranh giới "một sự cố" ↔ "feed hỏng". 1 mã vi
  phạm ⇒ giấu số của RIÊNG mã đó, phần còn lại vẫn publish. Nhiều mã cùng lúc ⇒ lỗi ở nguồn ⇒
  không publish gì. Sàn 3 để track-set nhỏ (5 mã) không bị 1 vi phạm đẩy thành "feed hỏng".
  **Đếm theo MÃ, không theo DÒNG vi phạm** — một mã sinh được 2 vi phạm (JUMP + RETRO).
* **Bất biến KHÔNG dùng ngưỡng "%/ngày".** Thưởng 1:1 là +100% hợp lệ; +3% không sự kiện là sai.
  Ngưỡng đúng là **sai số so với kỳ vọng đã lăn sự kiện** — kỳ vọng dựng bằng CHÍNH `_roll()`.
* **Feed DEAD > 5 ngày lịch** (nghỉ lễ 4 ngày + 1 ngày trượt). FRESH/STALE phân theo **phiên giao
  dịch liền trước**, không theo ngày lịch — nếu không thì sáng thứ Hai nào cũng báo động giả.
* **Chuỗi ngày im lặng**: 1 ngày = QUIET (bảng chỉ ~4 dòng/ngày trung bình, im lặng 1 ngày là
  bình thường), 2-4 = WARN Discord, ≥5 = Telegram. Cùng tinh thần `dt5g_writer_watch.py`.

## Đối soát chéo — vì sao không so thẳng hai số hôm nay

So `oshares_live(hôm nay)` với dòng quý mới nhất là so hai thời điểm khác nhau; lệch là ĐÚNG (đó
là lý do module tồn tại). Phép so có nghĩa là **tại ngày của chính dòng quý**:
`oshares_at(mã, q.time) ↔ q.OShares`. Lệch > 0,1% ⇒ hoặc dòng quý bị RESTATE, hoặc mô hình sai —
**không phân biệt được từ phía này ⇒ báo cả hai số, cả hai ngày, KHÔNG chọn**.

Tên trường là `err_pct_vs_ticker_financial` chứ không phải `err_pct` trung tính: chuỗi `reason` do
`oshares_live` sinh chia cho KỲ VỌNG, còn ở đây chia cho số `ticker_financial` — cùng một sự kiện
ra hai con số (EVF: 7,40% vs 8,00%).

## Kết quả chạy THẬT (2026-08-13, 29 mã đang giữ 2 account)

Cổng 1 selfcheck PASS (corp_action_lib 7 ca + oshares_live 22 ca). Cổng 2 freshness **FRESH**
(lô 08-12 22:48 ICT ≥ phiên trước 08-12). Cổng 3 bất biến 0 vi phạm. Cổng 4 đối soát **5/29 mã
lệch** — đều có lý do từ cổng giải thích, đều là dạng dòng quý bị RESTATE:

| Mã | ngày dòng quý | corp-action | ticker_financial | lệch |
|---|---|---|---|---|
| EVF | 2026-07-21 | 704.248.289 | 760.565.802 | 7,40% |
| VRE | 2026-07-29 | 2.328.818.410 | 2.272.318.410 | 2,49% (**dòng quý THẤP hơn** — CP quỹ?) |
| SHB | 2026-07-30 | 5.377.339.512 | 5.343.703.838 | 0,63% |
| TCB | 2026-07-21 | 7.064.851.739 | 7.086.240.414 | 0,30% |
| VPB | 2026-07-20 | — (fail-closed) | 7.933.923.601 | `NO_MODEL_VALUE` |

Nhãn phương pháp trên 29 mã: `ANCHOR_ONLY` 20 · `AIS_EXACT` 3 · `ISS_ESTIMATE` 3 ·
`ANCHOR_UNVERIFIED` 2 · `UNKNOWN_RATIO` 1.

**Cảnh báo ≤10 ngày: RỖNG — và đã kiểm chứng RỖNG THẬT**, không phải im lặng giả. Truy vấn SQL
độc lập (đường code khác, không qua `ca_events`) trên đúng 29 mã, cửa sổ `[2026-08-13, 2026-08-23]`,
`event_status != "not_executed"`: 0 dòng. **Đối chứng dương**: mở cửa sổ lên 400 ngày qua ĐÚNG hàm
production ⇒ tìm được BID (AIS 2027-03-24) và SIP (AIS 2027-08-30). Đường cảnh báo sống.

## Hai bug THẬT bị bắt trong lúc build (cả hai đều thuộc loại "cổng vẫn xanh mà không kiểm gì")

1. **`_event_dict` đổi tên `exercise_ratio` → `ratio`**, còn `_roll`/`_dedup_iss` đọc
   `exercise_ratio`. Đưa thẳng sự kiện đã-áp vào `_roll` ⇒ MỌI sự kiện thành blocker ⇒
   `check_invariants` lặng lẽ `continue` trên mọi mã và **không bao giờ báo vi phạm**. Vá bằng
   `_as_roll_event()`; ca `INV3` chứng minh ngược (raw ⇒ 1 blocker, qua hàm ⇒ 0 blocker + đúng
   115.000.000).
2. **Ghi đè `value_withheld`**: một mã dính 2 vi phạm (probe ACB: `UNEXPLAINED_JUMP` +
   `RETRO_CHANGE`) ⇒ vòng thứ hai chép `None` (giá trị vừa bị giấu) đè lên chính con số cần giữ
   làm bằng chứng. Output vẫn trông bình thường. Vá bằng `withhold_suspect()`; ca `W2`.

Cả hai được bắt bằng **positive control trên dữ liệu THẬT** (giả mạo giá trị hôm qua của ACB
+7% trong một `OUT_DIR` tạm rồi chạy `run()` thật), không phải bằng đọc lại code.

Bonus (không phải bug production, là bẫy cho người viết test sau này): `stale_streak` để
`state_path=STATE_PATH` làm **giá trị mặc định** ⇒ gán `cad.STATE_PATH = <tmp>` trong probe không
có tác dụng và probe **ghi đè state production thật** (đã xảy ra). Đổi sang phân giải trong thân
hàm; ca `INV13`.

## Selfcheck — 61 ca, hermetic

Không BQ, không Discord, không đọc file production; mọi cổng có điểm bơm (`runner=`, `fresh=`,
`rows=`, `nav_glob=`, `state_path=`). **Mỗi ca chặn có ca chứng minh ngược** (INV1 lọt vs INV2
chặn; X1 khớp vs X2 lệch; INV12 im vs INV11 báo) — "cổng bắt được X" một mình vô nghĩa vì
`return False` cũng bắt được mọi thứ.

Chạy lại dưới **4 môi trường TZ** (`Asia/Ho_Chi_Minh` / không có TZ / `America/New_York` / `UTC`):
kết quả giống hệt từng ký tự (§16 + skill `verify-before-done`). Ca `F6` neo đúng ranh giới nguy
hiểm: `18:30 UTC` = `01:30 ICT NGÀY HÔM SAU` — so ngày trên chuỗi UTC thô sẽ xếp STALE oan.

**Phạm vi §23**: chỉ chạy selfcheck của code MỚI + 2 module nền mà nó gọi. Không quét rộng —
không đụng module lõi dùng chung nào (`plan.py`/`config.py`/`executor.py`/`brokers.py`/
`plan_funding_gate.py`); các file mới không được import bởi bất kỳ script nào khác.

## Ranh giới — cái này KHÔNG làm

* **Không tính tỉ suất lợi nhuận.** Cổ tức ở đây là **GỘP, nguồn vendor, CHƯA đối soát tiền
  broker**; §21 vẫn buộc mọi tỉ suất per-position đi qua `dividend_adjusted_return.py`.
* Không đặt lệnh, không sửa plan, không đổi sizing.
* **Không tắt `update_shares_live.py`** (quyết định user: giữ đường reactive song song).
* Không tự chọn số nào đúng khi hai nguồn lệch.

## Rủi ro tồn dư (công bố, không giấu)

1. **n=1 quan sát về lịch nạp vendor.** Nếu vendor nạp INCREMENTAL (chỉ dòng mới) thay vì
   full-reload, thì ngày không có sự kiện mới nào sẽ ra `STALE` dù feed vẫn sống. Chuỗi im lặng
   phân tầng là để chịu đúng cái đó (1 ngày im = QUIET), nhưng **cần quan sát 5-10 phiên thật mới
   biết ngưỡng có đúng không**. Không backtest được, chỉ tích luỹ.
2. **`announced` có thể đổi ngày/huỷ.** Cảnh báo proactive buộc phải lấy `announced` (0 dòng
   `executed` có ngày tương lai), nên mỗi dòng cảnh báo mang nhãn "dự kiến, có thể đổi/huỷ".
3. **Anchor nhảy sang AIS đúng hôm nay** có thể sinh vi phạm bất biến hợp lệ-nhưng-gây-nhiễu nếu
   chênh > 0,1% (đã đo ca FPT: chỉ 0,0013%, nằm trong dung sai). Hệ quả là giấu số 1 mã 1 ngày +
   1 dòng Discord, không phải khoá cả ngày.
4. **Vị thế đọc từ artifact T-1** ⇒ mã mua trong phiên hôm nay chưa vào danh sách cảnh báo cho tới
   hôm sau. Có cờ `positions_stale` khi artifact cũ > 5 ngày, nhưng độ trễ 1 ngày là thiết kế.
5. **Snapshot chưa có consumer máy** ⇒ cờ `usable` chưa được cưỡng chế bởi code nào. Consumer đầu
   tiên phải kiểm cờ đó, và nên có selfcheck riêng chứng minh nó fail-closed.
