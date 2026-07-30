# AUDIT — "dispatch xong = tin exit-code/non-empty, KHÔNG verify NỘI DUNG"

**Job**: `Wags_20260730_044459` · **Ngày**: 2026-07-30 · **Loại**: audit read-only (KHÔNG sửa gì)
**Bài học gốc**: commit `01a7f99` — `daily_retro.sh` Bước 1 nhận rc=0 + file non-empty nhưng nội
dung lạc đề (session-collision). Checker cũ `[ -s "$DRAFT_FILE" ]` không bắt được; phải thêm
content-shape gate `_draft_valid()` (grep header `## RETRO — <date>`) mới bắt.

Audit này tìm chỗ **nguyên tắc đã có** (MIKE.md §Quy chuẩn #2 "verify ARTIFACT không tin
self-report", ops_runbook "không tin self-report của agent/job status") **CHƯA được cơ khí hoá
thật sự** — tức verify tồn-tại/đúng-schema nhưng không verify nội-dung-đúng-việc.

## Phạm vi đã quét
44 script `mike/bin/*.sh` + shell gốc `WorkingClaude/*.sh` + toàn bộ `crontab -l`.
**8 call-site thật sự dispatch 1 headless agent** (grep `dispatch.sh` loại trừ lib/self-reference):

| # | Call site | Target | Mode | Verify sau dispatch |
|---|---|---|---|---|
| 1 | `bq_freshness_check.sh:495` | DollarBill (plan T+1, mọi account live) | `--bg` | **KHÔNG GÌ** (`\|\| echo "[WARN]"`) |
| 2 | `ops_autofix.sh:87` | Winston (opus, sửa lỗi vận hành) | `--bg` | **KHÔNG GÌ** |
| 3 | `kb_nightly.sh:612` | Mike (KB weekly editorial, thứ Sáu) | `&` (background, không `wait`) | **KHÔNG GÌ** (kể cả exit code) |
| 4 | `daily_retro.sh:210` (bước 2) | Wags (verify draft retro) | sync | rc≠0 **hoặc output rỗng** — non-empty = tin |
| 5 | `daily_retro.sh:237` (bước 3) | Mike (finalize → INCIDENTS.md) | `--bg` | gián tiếp: leftover-draft scanner |
| 6 | `eod_trading_report.sh:393` | Spyros (audit lệch broker≠state) | `--bg` | **KHÔNG GÌ** (`\|\| true`) |
| 7 | `fearbuy_weekly_scan.sh:61` | Taylor (recon fear-buy tuần) | `--bg` | **KHÔNG GÌ** |
| 8 | `refresh_deposit_rate_vn.sh:107` | Winston (crosscheck lãi suất) | sync | ✅ **post-condition check** (mẫu tốt) |

Cộng 2 pipeline có **content gate đúng chuẩn** (không nằm trong bảng vì gate đã có):
- `wags_autofix.sh` — parse `<<<VERDICT_JSON>>>` của arch-reviewer (không `tail -1` mù, sự cố
  2026-07-08), + đòi bus finding topic `wags-fix: <label>` có field `files_changed`.
- `verify_finding.sh` — cùng cơ chế VERDICT_JSON, thiếu block ⇒ verdict "no parseable block".

Ngoài phạm vi (deterministic, không phải agent): `inject_discretionary_orders.sh`,
`check_sbv_weekly.sh`, `data_registry_audit.sh`, `refresh_fa_ratings*.sh`, `paper_*`,
`sync_bq_cache_daily.sh` (nó chỉ *gọi* `ops_autofix.sh` — rủi ro nằm ở #2).

---

## Xếp hạng theo rủi ro thật

### 🔴 P1 — `bq_freshness_check.sh` → plan T+1 của DollarBill (CHẠM TIỀN THẬT)

Đây là chỗ **nguy hiểm hơn draft retro nhiều bậc**, đúng như giả thuyết trong đề bài.

**Hiện trạng**: dispatch `--bg`, không chờ, không verify. Lỗi dispatch chỉ `echo "[WARN]"` vào
`logs/bq_freshness.log` lúc 19:00 — không ai đọc, không notify.

**Gate hạ nguồn có thật nhưng chỉ kiểm SHAPE**, đúng đẳng cấp `[ -s $DRAFT_FILE ]` một tầng trên:
- `send_plan_report.sh` (21:00): file tồn tại · `plan_date == T+1` · có key `orders`. Hết.
- `preflight_check.sh` (08:45): file tồn tại · `approved_by` khác rỗng · số lệnh · est value ·
  echo `state_name`/`state_source`.

**KHÔNG có gate cơ khí nào ở đâu trong fleet** cho:
1. **`ref_price` đúng nguồn/hợp lý** — grep toàn repo: `ref_price` chỉ được *dùng* (chase cap
   trong `executor.py`, render report), không chỗ nào **đối chiếu** với nguồn thứ 2. Quy tắc
   "phải lấy DNSE live, TUYỆT ĐỐI KHÔNG dùng BQ close" hiện được cưỡng chế bằng **~800 ký tự
   văn bản trong prompt**, không bằng code.
2. `plan["account"]` khớp account đích (chỉ khớp theo TÊN FILE).
3. `state`/`state_source` trong plan khớp DT5G thật của ngày đó (chỉ echo lại, không so
   `golive_state_today.json` — đúng file mà prompt bảo Bill đọc).
4. `nav_basis` so với snapshot broker đã verify.

**Rủi ro cụ thể**: sự cố này ĐÃ XẢY RA — plan ZaloPay 07-10, 2/4 mã (BID, MBB) dùng BQ close
07-08 lệch **+5,7%** so giá đóng cửa thật, 2 mã còn lại dùng đúng DNSE. Plan sai kiểu này
**đúng schema, đúng ngày, có đủ `orders`** → mọi gate hiện tại cho qua. Tệ hơn draft retro ở 2
điểm: (a) artifact được `bot_execute.py` tiêu thụ bằng tiền thật; (b) **gate người (duyệt 21:00)
đọc bản render của CHÍNH những con số chưa verify đó** — plan shape-đúng/content-sai nhìn y hệt
plan tốt với người duyệt, nên "user duyệt" không phải một lớp phòng thủ độc lập ở đây.

**Gate cơ khí đề xuất** (đặt trong `send_plan_report.sh`, ngay trước khi render/gửi — nó đã là
artifact gate duy nhất chạy trước mắt người, rẻ nhất và không đụng surface đặt lệnh):
- **(1a) Price-plausibility gate**: mỗi order, so `ref_price` với nguồn ĐỘC LẬP thứ 2 (DNSE live
  quote qua `dnse_api.py` — chính nguồn plan *bắt buộc* phải đã dùng; fallback BQ cache last
  close nếu DNSE lỗi). Lệch > ngưỡng (đề xuất 3%, hoặc ngoài band ±tick) → escalate `question`
  + **không gửi như plan duyệt được**, đi đúng đường `plan_date_stale` đã có. Gate này bắt CHÍNH
  XÁC sự cố 07-10.
- **(1b) Nửa bước rẻ hơn nếu (1a) nặng**: bắt buộc mỗi order mang field provenance hiển
  (`ref_price_source:"DNSE_live"` + timestamp); thiếu field ⇒ reject. Prompt đã yêu cầu Bill ghi
  chú "THIẾU GIÁ LIVE" — biến field thành bắt buộc để **im lặng trở thành fail cứng**.
- **(1c)** Thêm 2 assert 3 dòng: `plan["account"] == $ACCOUNT`, và `state`/`state_source` khớp
  `deploy_golive_dt5g_v4/golive_state_today.json` → lệch = escalate.

### 🟠 P2 — `ops_autofix.sh` → Winston (tự sửa lỗi vận hành): tự-chữa-lành có thể là lời nói dối

**Hiện trạng**: `--bg`, không post-condition. Nghiêm trọng hơn: **cooldown được stamp TRƯỚC khi
fixer chạy** (`echo "$NOW" > "$STAMP_FILE"` rồi mới dispatch), và ngay trước đó đã notify user
*"🔧 đã tự động cử agent chẩn đoán + sửa — sẽ báo kết quả khi xong"*. Nếu fixer lạc đề/chết im,
**không gì phản bác câu đó**, và label vừa mua trọn 1 giờ im lặng.

**Giảm nhẹ có thật**: checker tự phát hiện lại kỳ sau → in "TÁI DIỄN trong cooldown (fix trước
có thể chưa ăn)". Nhưng chỉ hiệu lực với checker chạy lại sớm (ops_health 08:20/12:45). Với label
**1 lần/ngày hoặc 1 lần/tuần** thì mù hẳn — điển hình `bq-cache-sync-verify` (23:45), tức đúng
label sinh ra từ sự cố "cache thối 10 ngày âm thầm → false-SEV1 macro". Off-topic fixer ở đó =
issue đứng ≥24h trong lúc user đã được báo là đã xử lý.

**Gate đề xuất**: bê nguyên pattern `refresh_deposit_rate_vn.sh:110` (post-condition theo
`RUN_START_UTC` + khớp CẢ topic LẪN event_type):
- Đặt hợp đồng đầu ra tường minh trong prompt: kết thúc phải có `append_event.sh Winston
  finding "ops-autofix-done: <label>"` (hoặc `question` nếu chạm ranh giới cứng).
- Vì là `--bg`: check ở **lần gọi sau** (`ops_autofix.sh` tự soát stamp trước đó: có stamp mà
  không có event khớp trong khoảng đó ⇒ notify *"autofix lần trước KHÔNG có kết quả xác nhận
  được — cần người xem"* thay vì im lặng), hoặc thêm subshell `jobs.sh wait` rồi grep bus.
- **KHÔNG stamp cooldown đầy đủ khi chưa có post-condition** (hoặc chỉ stamp nửa cooldown) — để
  fixer lạc đề không mua được trọn giờ im lặng.

### 🟡 P3 — `kb_nightly.sh` Friday editorial: đã im lặng chết ~2 tuần, nguyên nhân thứ 2 vẫn còn

**Hiện trạng**: `--timeout 900 >> "$LOG" 2>&1 &` — background, không `wait`, không exit code,
không artifact check. **Chính comment trong file thừa nhận**: từ 2026-06-27 đến 2026-07-09 mỗi
thứ Sáu dispatch này im lặng fail (self-dispatch guard) *"và nobody noticed because it launches
in background with `&` and no exit-code check"*. Nguyên nhân `DISPATCH_FROM` đã fix; **nguyên
nhân thiếu-verify thì chưa**.

**Rủi ro**: việc 1-10 của prompt gồm nhiệm vụ correctness thật (đọc output
`data_registry_audit.sh` — FAIL = regression nguồn TRAP/DEAD bị đọc lại, phải escalate; model-mix
drift; schedule-drift docs vs `crontab -l`). Một tuần no-op/lạc đề = những check đó âm thầm không
xảy ra, trong khi fleet tin là KB đã được review.

**Gate đề xuất**: prompt đã bắt buộc `append_event.sh Mike decision 'kb-weekly-editorial'` ở cuối
⇒ hợp đồng đầu ra CÓ SẴN, chỉ thiếu người đọc. Vì dispatch background và kb_nightly thoát ngay,
kiểm ở **nightly kế tiếp (thứ Bảy)**: không có event `Mike/decision/kb-weekly-editorial` trong
24h sau mốc dispatch thứ Sáu → log + notify. Rẻ, không phải chờ, không đụng luồng chính.

---

## Phần còn lại (rủi ro thấp hơn — ghi nhận, chưa cần đề xuất chi tiết)

- **`daily_retro.sh` bước 2 (Wags verify)** — fix hôm nay chỉ phủ **bước 1**. Bước 2 vẫn gate ở
  mức `rc≠0 || output rỗng`; output non-empty được truyền nguyên văn sang job finalize để Mike
  tự đọc là CONFIRMED/NEEDS_CHANGES. Một output lạc đề non-empty ⇒ INCIDENTS.md gắn nhãn verify
  sai. Gate rẻ: đòi output chứa token `CONFIRMED|NEEDS_CHANGES|REFUTED` (cùng họ với
  VERDICT_JSON của `wags_autofix.sh`). Rủi ro: báo cáo nội bộ, không tiền thật.
- **`daily_retro.sh` bước 3 (finalize)** — `--bg` không verify, NHƯNG có gate gián tiếp: draft
  không bị xoá ⇒ leftover-draft staleness scanner báo. Coi như đã phủ (chấp nhận được).
- **`eod_trading_report.sh` → Spyros** — `--bg || true`. Việc bị bỏ = audit lệch broker≠state
  thật không bao giờ diễn ra. Money-adjacent nhưng read-only. Đáng lo hơn kỳ vọng ở 1 điểm:
  `MISMATCH_FILE` theo từng ngày nên **chỉ trigger 1 lần cho ngày đó, không tự re-flag** — mất là
  mất hẳn. Nên có post-condition (bus event của Spyros cùng `plan_date`) ở vòng sau.
- **`fearbuy_weekly_scan.sh` → Taylor** — `--bg`, không verify. Prompt có mandate quiet-heartbeat
  (*"im lặng hoàn toàn KHÔNG được"*) nhưng không có gì cơ khí kiểm tra scan đã ra kết quả. Gate
  rẻ sau này: bus finding tồn tại HOẶC `backstop.md` đổi mtime trong 24h. Chỉ là recon R&D.

## Mẫu tốt để copy (đã có trong repo, không cần phát minh lại)
1. `refresh_deposit_rate_vn.sh:110-145` — post-condition theo `RUN_START_UTC`, khớp **cả topic
   lẫn event_type**, phân biệt rc=5 (usage-limit → resume tự động, KHÔNG phải fail) với
   "rc=0 nhưng agent không làm gì" → fallback nhắc thủ công.
2. `wags_autofix.sh` / `verify_finding.sh` — `<<<VERDICT_JSON>>>` block bắt buộc; thiếu/không
   parse được ⇒ verdict fail tường minh, không đoán từ `tail -1`.
3. `daily_retro.sh:_draft_valid()` (hôm nay) — content-shape gate rẻ nhất: grep đúng header mà
   prompt đã ra lệnh viết.

**Nguyên tắc chung rút ra**: mọi dispatch có prompt yêu cầu "ghi X" đều đã có sẵn một *hợp đồng
đầu ra* — chi phí gate chỉ là đọc lại đúng thứ prompt đã đòi. Chỗ nào prompt đòi mà không ai
đọc, chỗ đó là lỗ.
