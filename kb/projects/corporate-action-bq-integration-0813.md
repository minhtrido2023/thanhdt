---
kind: project
status: DONG (crontab da cai, dang burn-in alert-only + 1 muc mo Viec B)
date: 2026-08-13
---

# corporate_action BQ integration + paper-report bug fix (2026-08-13)

User yêu cầu nghiên cứu bảng BQ mới `tav2_bq.corporate_action` (per-event corp-action, refresh
hàng ngày từ 08-13). Duyệt (a) dùng làm nguồn đo cổ tức/ex-rights + (b) build Oshares "live".

## Kết quả (6 vòng dispatch Taylor + quant-skeptic)

1. **Nghiên cứu + đăng ký**: `kb/data_registry/price-volume/corporate_action_bq.md` (status TRAP —
   AIS lag ~7 tuần so exright_date, cần tự verify freshness mỗi lần đọc).
2. **Việc A** (nguồn đo cổ tức) — `dividend_adjusted_return.py` dùng `corporate_action.DIV` phân
   loại DIV/ISS, tiền broker vẫn là nguồn số chính thức. **CONFIRMED**.
3. **Việc B** (`oshares_live.py`) — thiết kế đầu **REFUTED** (anchor look-ahead qua
   `ticker_financial.OShares` restated; roll-forward no-op trên 75% ISS không-accrue) → vá lại
   (anchor chỉ AIS, fail-closed khi ratio∈{0,NULL}) → **CONFIRMED**. **CHƯA WIRE vào consumer nào**
   — chưa xác định phạm vi (backtest point-in-time vs report/rating live hôm nay), cần user chọn
   trước khi dispatch tiếp.
4. **Việc C** (bug thật): `alphalens_report.py`/`converge_report.py` so `entry_price` thô đóng
   băng với `Close` đã điều chỉnh hồi tố (Bẫy 2, `ticker_close_vs_price_dividend_adj.md`) — mọi
   sự kiện quyền sau ngày vào lệnh bị tính thành lỗ giá oan. Case thật: MBB (pha loãng 25%,
   exright 2026-08-11) báo −18,8% thay vì đúng convention accrue-only −2,9%. Sửa bằng
   `paper_entry_adjust.py` (rebase entry theo `Close/Price` tại ngày chụp giá) + làm rõ convention
   accrue-only (không giả định đã subscribe rights). **CONFIRMED** qua 2 lớp hiệu chỉnh.
5. **Việc D** (cổng chặn tái phát bug) — `report_return_gate.py` nối vào ĐÚNG kênh
   `newdeals_daily_report.py`→`notify_thread.sh` (không phải chỉ qua email), qua 5 vòng thu hẹp
   residual risk (marker tautology, dual rc=3 producer, banner đếm sai, hardcode thread ID).
   **CONFIRMED** vòng 5.

6. **Việc E** (vòng 7, job `Taylor_20260813_091128`) — **cron hàng ngày** `mike/bin/corp_action_daily.py`
   + `.sh` + `corp_action_daily_selfcheck.py` (61 ca, hermetic). Đây là điểm wire ĐẦU TIÊN của Việc B:
   mỗi mã được cập nhật vào ĐÚNG ngày sự kiện của nó (`exright_date` cho DIV/ISS; `AIS.effective_date`
   cho lúc số CP chính thức đổi, trễ tới ~7 tuần), 4 cổng chặn (selfcheck nền / freshness feed / bất
   biến số CP / đối soát 2 nguồn) + cảnh báo proactive ≤10 ngày cho mã ĐANG GIỮ. Không có bước LLM
   nào ở runtime. **Crontab CHƯA CÀI** — chờ quant-skeptic + user duyệt. Chi tiết:
   `agents/Taylor/research/corp_action_daily_cron_20260813.md`.

## Vòng 7 (2026-08-13 chiều) — quant-skeptic **REFUTED** vòng 1 của Việc E, đã vá

**Killer objection (đúng, và là bug thật):** `_all_events_on` lọc `event_status = "executed"`, mà
vendor chỉ đổi `announced → executed` trong lô reload rơi ~22:2x ICT **của chính ngày sự kiện** —
tức ~15 tiếng SAU khi cron 07:30 của ngày đó đã chạy xong trên lô tối hôm trước. ⇒ trigger
ngày-sự-kiện trả **0 dòng MỖI NGÀY**, không có lượt nào quay lại ngày đã lỡ, và **im lặng** (trông
y hệt "hôm nay không có sự kiện"). Toàn bộ nửa cổ-tức của job coi như chết: 11 ex-date cổ tức tiền
mặt trên mã đang giữ trong 3 tháng qua (VHM 6.000đ, NCT 8.000đ, SAB 3.000đ, VNM 1.850đ…) lẽ ra
được ghi 0 lần. Bộ hồi quy cũ mù vì `T1`/`T2` bơm `rows=` vào `triggered_today` — **đi vòng qua
mệnh đề WHERE**, tức kiểm bộ lọc SAU truy vấn trong khi bug nằm TRONG truy vấn.

**Đã vá:**
- `_events_on_sql()` tách khỏi hàm chạy (kiểm được hình dạng truy vấn), lọc `!= "not_executed"`
  (chỉ loại đã huỷ) và **mang `event_status` theo từng dòng**.
- `confirm_prior_triggers()` — vòng xác nhận D+1 đọc lại ngày D với MỌI trạng thái:
  `CONFIRMED` / `STILL_ANNOUNCED` / **`CANCELLED`** / **`VANISHED`** (2 loại sau đẩy Telegram).
  Đây là cái giá phải trả cho việc ghi trên `announced`, không phải tuỳ chọn.
- Số cổ tức ngày D mang nhãn ***(dự kiến)*** ngay cạnh từng mã, không phải một chú thích chung.
- `bq_corp_action(..., include_announced=False)` — **mặc định KHÔNG đổi**, §21 (đo lợi nhuận trên
  sự kiện ĐÃ XẢY RA) giữ nguyên `executed`; cờ chỉ mở cho câu hỏi "hôm nay có gì chốt quyền".
- 2 mục `_secondary`: `stale_streak` nhận chữ ký `max_ingested_utc or max_ingested` (nhánh DEAD
  parse-lỗi trả tên khoá khác ⇒ chữ ký lặng lẽ thành None đúng lúc feed hỏng); cờ
  `invariant_evaluated` ra snapshot + bus để `0 vi phạm` khi `n_compared=0` không bị trích là PASS.

**Bằng chứng (không phải tự nhận):** selfcheck **79/79** (72 hermetic + 7 `--live`).
`L6`/`L7` chạy CHÍNH hàm production trên bảng thật ngày 2026-08-13 ⇒ **4 dòng BCF/DHN/HGM/SAC**,
đúng chỗ quant-skeptic đo bản cũ ra 0. **Mutation test**: khôi phục `= "executed"` ⇒ 6 ca đỏ
(`Q1 Q2 L1 L4 L6 L7`), `L6` tái lập chính xác con số 0-dòng. Dry-run lịch sử: **SAB 2026-07-28
3.000đ/cp** → SpaceX 1.100cp = 3.300.000đ, ZaloPay 744cp = 2.232.000đ (khớp tay). Vòng xác nhận
chạy thật trên mốc 08-13 → 4 × `STILL_ANNOUNCED` (feed chưa nạp lô mới, đúng như mong đợi).

⚠️ **Rủi ro tồn dư đã công bố, KHÔNG tự nhận là đã đóng**: `FEED_DEAD_DAYS=5` và phân tầng
QUIET/WARN/Telegram (1 / 2-4 / ≥5) vẫn **chưa được kiểm chứng** bằng phiên thật — cần 5-10 phiên.
Giả định lịch nạp vendor vẫn là **n=1 quan sát**; script tự đo `MAX(ingested_at)` mỗi lần chạy nên
không neo cứng vào giả định đó, nhưng nhãn *(dự kiến)* chỉ đúng chừng nào vòng D+1 thật sự chạy —
tức nó phụ thuộc vào cron chạy ĐỀU, không phải chạy một lần.

## Vòng 3 của Việc E (2026-08-13, job `Taylor_20260813_104511`) — vá lỗi khoá trùng, quant-skeptic CONFIRMED

`confirm_prior_triggers()` dùng khóa không duy nhất (ticker, event_code, exright_date,
effective_date) — case thật MBB 2026-08-11 (2 sự kiện: quyền mua 10% + cổ tức CP 15%) gộp nhầm,
kết quả CONFIRMED/CANCELLED phụ thuộc thứ tự dòng BQ trả về. Vá bằng khoá 2 lớp (vendor `id` +
khoá nội dung 8-field) + tệ-nhất-trước (`_KIND_RANK`) để huỷ không bao giờ bị nuốt. Thêm
carry-forward (`pending_confirmations`, N=5 lượt mới timeout). Commit `WorkingClaude@f844b800`.
quant-skeptic **CONFIRMED cao** — đo được bug cũ NẶNG HƠN báo cáo (2.164 lần trùng toàn bảng, 250
nhóm có status khác nhau thật sự phụ thuộc thứ tự BQ, không phải lý thuyết). 2 điểm sửa nhỏ: đếm
selfcheck đúng là 104/104 (không phải 103/103); khoá mới vẫn còn 460 nhóm trùng dư (49 khác
status) nhưng an toàn 1 chiều (chỉ lệch về CANCELLED giả, không nuốt CANCELLED thật) nhờ
`_KIND_RANK` — không phủ định kết luận.

**Rủi ro còn lại DUY NHẤT quant-skeptic nói rõ, CHƯA vá** (khuyến nghị #5 từ vòng 2, Taylor cố ý để
ngoài phạm vi 3 việc được giao vòng 3): **missed-run/backfill gap** — nếu cron tự nó KHÔNG chạy
một ngày nào đó (crash/lỗi hạ tầng), sự kiện exright ngày đó không bao giờ được ghi và không có
đường quay lại bù — `prev_asof` cách `asof` hơn 1 phiên phải tự phát hiện + backfill, hiện chưa có.

## Vòng 4 của Việc E (2026-08-13, job `Taylor_20260813_115210`) — vá missed-run/backfill, quant-skeptic CONFIRMED

User chọn hướng 2 (vá trước khi cài). Thêm LỚP 7 (3 hàm mới, nối vào bộ máy vòng 3 không nhánh
riêng): phát hiện phiên bị lỡ bằng mốc `prior_snapshot` (KHÔNG dùng `state.last_run` — mốc này ghi
TRƯỚC cả nhánh feed DEAD nên sẽ nhảy qua ngày chạy-hỏng vĩnh viễn), đếm theo lịch giao dịch VN,
backfill lại đúng truy vấn sự kiện-trong-ngày cho từng ngày bị lỡ, trần 10 phiên/lượt không cap
im lặng (hàng hoãn tự rút dần). Idempotent — tái dùng khoá duy nhất vòng 3, không phát minh lại.
Commit `WorkingClaude@5fe35e2f`. **CONFIRMED cao**, không có gap blocking mới — quant-skeptic tự
dựng 5 kịch bản đối kháng riêng (kể cả outage 32 phiên, rút hết trong 4 vòng, 0 trùng lặp), cơ chế
là "control-flow certainty" (đọc code xác nhận được, không phải suy luận từ mẫu nhỏ). Điểm duy
nhất còn treo: bằng chứng BQ thật test trên ngày mô phỏng ở TƯƠNG LAI (chưa có ngày lỡ THẬT trong
quá khứ để quan sát vendor chuyển announced→executed qua đường backfill) — không phải lỗi thiết
kế, chỉ là cần thời gian trôi qua, sẽ tự xác nhận trong đợt burn-in alert-only đã lên kế hoạch.

Taylor cũng tự bắt + tự vá 1 lỗi trong CHÍNH bộ test mutation của mình (harness chấm nhầm do cache
`.pyc` trùng byte-size/giây khiến 2 mutation khác nhau trông cùng kết quả) — minh bạch báo cáo.

**KHÉP KÍN — không còn gap nào cần vá thêm trước khi cài crontab.** Còn 2 điều CHỈ kiểm chứng được
bằng thời gian (không phải code): `FEED_DEAD_DAYS=5` + tầng cảnh báo (bảng chỉ có 1 ngày ingest),
và đường backfill trên ngày lỡ THẬT — cả hai đúng là lý do đợt burn-in alert-only 5-10 phiên tồn
tại. **Chờ user duyệt giờ chạy cài crontab.**

## Crontab ĐÃ CÀI (2026-08-13, user duyệt)

`30 0 * * 1-5` (07:30 ICT T2-T6) → `mike/bin/corp_action_daily.sh`. Backup crontab trước khi sửa:
`/tmp/crontab_backup_before_corp_action.txt`, diff xác nhận chỉ THÊM 3 dòng, không mất gì cũ.
`kb/cron_registry.md` cập nhật cùng commit (§11), phản ánh đúng vòng 4 (selfcheck 134/134, LỚP 7
backfill) thay vì mô tả cũ vòng 1.

⚠️ **ĐANG Ở ĐỢT ALERT-ONLY 5-10 phiên đầu** (từ 2026-08-13) — chưa quan sát được lần chuyển lô
vendor thật hay ngày cron tự lỡ thật nào. KHÔNG tin tuyệt đối tầng `FEED_DEAD_DAYS=5`/backfill cho
tới khi thấy ít nhất 1 lần trong dữ liệu sống. Verify `MAX(ingested_at)` mỗi phiên.

## Việc A+B wire (2026-08-13 chiều-tối, job Taylor_20260813_125526 → 6 vòng quant-skeptic) — ĐÃ XONG

User duyệt wire Oshares vào 2 consumer: **A** = backtest point-in-time (`custom30_core_select_audit.py`,
bản sao tự chứa, KHÔNG đụng `custom_basket.py` production), **B** = rating live (`rating_8l.py`, qua
wrapper đối chiếu bq_admin, chỉ dùng số mới khi khớp ≤0,1% — tự rơi về số cũ khi lệch).

- **Vòng 1**: REFUTED — lỗi vendor thật (AIS `shares_total_after` sai 10× ở IDC), Taylor tự phát hiện.
- **Vòng 2 (thiết kế lại cẩn thận theo yêu cầu user)**: REFUTED lần 2 — case FPT 2020-05-05 (vendor có
  2 chuỗi AIS đan xen, gate cũ cho qua số sai −32,3% ở nhãn tin cậy cao nhất). Vá bằng đổi triết lý từ
  "bộ dò lỗi" (phục vụ trừ khi chứng minh sai) sang "bộ chứng nhận" (chỉ phục vụ khi đối chiếu được) —
  quét toàn bảng: 220/2.505 giao dịch AIS bị lỗi hình dạng này, không phải 2 ca cá biệt.
- **Vòng 3**: CONFIRMED.
- **Vòng 4**: dời cổng chứng nhận vào NGAY BÊN TRONG `oshares_live.py` (trước đó chỉ ở lớp bọc
  `oshares_pit.py`, ai gọi thẳng vẫn nhận số sai) — CONFIRMED, nhưng phát hiện ảnh hưởng tới
  `corp_action_daily.py` (cron LIVE) mất phủ 2/33 mã (EVF đúng, SHB báo oan).
- **Vòng 5**: sửa gấp lỗi hiển thị Discord (4 mã đang giữ EVF/SHB/TCB/VPB bị hiện "0,00% khớp" giả khi
  thực ra là "từ chối trả lời" — lỗi có từ trước, không phải do các vòng trên). Phát hiện thêm:
  **SANITY_FACTOR CẦN THIẾT** — 279 ô/34 mã lọt cổng chứng nhận mà cổng biên độ ×3 chặn được, gồm
  **VHM** (lỗi vendor ×1000, phục vụ ở tin cậy cao nhất suốt 13 quý) và VND đang giữ thật. KHÔNG tự
  wire cổng biên độ vào (sẽ đổi số lịch sử đã công bố — để user quyết theo §22). CONFIRMED.
- **Vòng 6 (khép chuỗi)**: sửa lời giải thích sai (TCB "thoát" vì neo bq_admin — SAI, thực ra neo 1
  dòng AIS MỚI đã chứng nhận), hợp nhất vị ngữ `refused()`, phòng báo động giả 08-14 do đổi thành viên
  track-set. **CONFIRMED** — 1 câu bằng chứng sai nhỏ trong báo cáo (đọc nhầm `max(public_date)` thành
  ngày nạp — không đổi kết luận, quant-skeptic tự chứng minh lại bằng A/B code cũ-vs-mới) + 1 khoảng
  hở thiết kế cho TƯƠNG LAI (`model_version()` chưa phủ logic bất biến của `corp_action_daily.py`
  chính nó — không ảnh hưởng gì hôm nay, chỉ cần nhớ khi sửa file đó sau này).

**Kết quả cuối:** Việc A/B đã wire, an toàn, đã qua 6 vòng phản biện độc lập. `oshares_live.py`/
`oshares_pit.py`/`corp_action_lib.py` không đổi gì từ vòng 4. Không số đặt lệnh/NAV nào bị ảnh hưởng.

⚠️ **07:30 ICT 2026-08-14 sẽ có 1 cảnh báo 🔇 THẬT (không phải lỗi)** cho EVF/SHB — do chính bản vá
hôm nay siết chặt mô hình, không phải feed hỏng. Đã chứng minh bằng A/B (code cũ chạy trên feed hôm
nay vẫn tái lập đúng số cũ; code mới từ chối) — tự hết từ 08-15 khi baseline có `model_version`.

## Việc còn mở (rất nhẹ, không khẩn)

1. Việc B — consumer MÁY thứ 2/3 nếu muốn mở rộng thêm (đã có A=backtest, B=rating; còn use case
   khác nếu phát sinh) — không phải việc treo, chỉ là chưa có yêu cầu mới.
2. `SANITY_FACTOR` cho `corp_action_daily.py` (gọi trực tiếp, không qua `oshares_pit`) — **cần user
   quyết định chính sách**: có mở cổng biên độ ×3 không (sẽ ẩn số ở 34 mã lịch sử, gồm VHM/VND đang
   giữ, để an toàn hơn)? Hiện chỉ có WARN, không tự chặn.
3. Vòng 6 cũ (rc=1 + import-time KeyError của Việc D) — **CHỦ ĐỘNG BỎ QUA** (quyết định user
   2026-08-13, xác suất thấp + đã có backstop `cron_health_check_daily.sh`).
4. `corporate_action` freshness — verify tiếp qua đợt burn-in 5-10 phiên đang chạy.
5. `model_version()` chưa phủ logic bất biến riêng của `corp_action_daily.py` — chỉ cần nhớ khi
   sửa file đó lần sau (không phải bug, không hành động ngay).

## Commit chính
`WorkingClaude@2037e5c`, `mike@91434457` (vòng 1) · `WorkingClaude@abd7cd6`, `mike@60085443`
(vòng 3 Việc D) · `WorkingClaude@7790fd6`, `mike@17d0c749` (vòng 4 Việc D) ·
`WorkingClaude@e0ff1fb`, `mike@066df954` (vòng 5 Việc D) · `WorkingClaude@129f2779` (Việc E build) ·
`WorkingClaude@f844b800` (Việc E vòng 3 — vá khoá trùng) · `WorkingClaude@5fe35e2f` (Việc E vòng 4
— vá missed-run/backfill) · `WorkingClaude@1e35fba` (Việc A/B wire vòng 1) ·
`WorkingClaude@8908640` (vòng 3 — chứng nhận AIS trong `oshares_pit`) · `mike@e5a408d4`
(vòng 4 — dời cổng vào `oshares_live`) · `mike@9d5b9e24` (vòng 5 — sửa hiển thị Discord) ·
`mike@898390ad` (vòng 6 — khép chuỗi).

↩ [Về index dự án](INDEX.md)
