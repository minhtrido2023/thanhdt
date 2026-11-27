---
kind: ops-playbook
title: "Playbook: Phanh lỗ NAV, Cổng DT5G suy giảm & VN-Index TR"
owner: Mike
status: canonical
updated: 2026-11-27
---

# Playbook: Phanh lỗ NAV, Cổng DT5G suy giảm & VN-Index TR

> Tách nguyên văn từ [`../ops_runbook.md`](../ops_runbook.md) (2026-11-27, giữ trần <40 KB).

## Phanh lỗ NAV — `nav_loss_brake_monitor.py` (CHỈ CẢNH BÁO)

Monitor đo ba phanh mỗi tối (cron 22:05 + lượt hai 00:20 ICT, cài 2026-10-13) trên **NAV toàn tài khoản** của từng account
(giá đơn vị quỹ, `nav_unit_ledger.build_ledger`) và **không bao giờ** tạo `data/BOT_STOP`, không huỷ
lệnh, không gọi broker. Dừng giao dịch hay không là quyết định của user. `excluded_tickers` của
account KHÔNG ảnh hưởng gì tới monitor. Đầu vào/đầu ra: `kb/data_registry/trading-bot/loss_brake_state.md`.
Cron: `kb/cron_registry.md` hàng 22:05 / 00:20.

### Mỗi loại tin thì NGƯỜI làm gì

| Tin (đầu tin / dòng) | Nghĩa | Việc của người |
|---|---|---|
| 🚨 **PHANH LỖ NAV ĐÃ CHẠM** | Số CHỐT đã qua ngưỡng (ngày ≤ −5% · từ đỉnh ≤ −25% · từ điểm vào episode ≤ −15%) | User quyết. Muốn dừng: chạy đúng dòng `touch …/data/BOT_STOP` in trong tin. Monitor không làm hộ. Phiên sau còn vi phạm ⇒ báo lại |
| 🚨 **SỐ TẠM TÍNH ĐÃ VƯỢT NGƯỠNG (chưa phải số chốt)** | Có số nhưng chưa phải giá chốt đã kiểm — và số đó ĐÃ qua ngưỡng | Coi như phanh chạm cho tới khi chứng minh ngược lại: đọc lý do sau chữ "chưa phải số chốt", kiểm NAV thật của phiên đó, rồi user quyết như dòng trên |
| ⚠️ **KHÔNG ĐO ĐƯỢC** — "nav_history không có dòng …" | NAV phiên đó chưa ghi (cổng chặn rc=5/rc=6 — tin trích `gate_verdict` — hoặc EOD chưa chạy). Không có số tạm tính | Runbook "NAV thiếu dòng `nav_history`". Lượt 00:20 tự đo lại khi dòng về |
| ⚠️ … "chụp số dư lúc … TRƯỚC giờ đóng cửa / SAU giờ mở cửa phiên kế" | Dòng NAV (của phiên, của mốc so, hoặc của điểm vào episode) không phải giá chốt | Ghi lại dòng NAV đúng giờ nếu còn làm được (`daily_nav_snapshot.py --from-raw`); không thì chấp nhận phiên đó + phiên kế chỉ có số tạm tính |
| ⚠️ … "thiếu dòng của phiên liền trước … ⇒ con số là **gộp nhiều phiên**" | Dòng trước đó trong chuỗi cách hơn một phiên ⇒ "lỗ một ngày" thật ra là lỗ của nhiều phiên cộng lại | Vá dòng NAV của phiên thiếu (`--from-raw`). Số gộp mà đã vượt −5% thì tin là 🚨 tạm tính vượt ngưỡng — xử như dòng 🚨 |
| ⚠️ … "mang cờ nav_is_estimate" | Dòng backfill ước tính | **Luật giảm tin (user duyệt 2026-10-12 21:31):** nếu đây là lý do DUY NHẤT và số tạm tính còn cách ngưỡng HƠN 2,0 điểm % thì KHÔNG có tin tối — chỉ hiện ở `status.json` + dòng kiểm sáng (`KHÔNG đẩy tin tối …`). Nhận được tin loại này nghĩa là số tạm tính đang cách ngưỡng ≤ 2,0pp hoặc còn lý do khác ⇒ đọc số, kiểm NAV thật |
| ⚠️ … "**KHÔNG có sổ dòng tiền** …" / "sổ dòng tiền … không đọc được" | `data/account_cash_flows.json` mất hoặc hỏng ⇒ số tạm tính KHÔNG trừ nạp/rút (một lần rút sẽ hiện như lỗ) | Khôi phục file từ bản sao lưu (`fleet_backup`). KHÔNG tạo file rỗng để tin biến mất: file rỗng = khẳng định "chưa từng nạp/rút" |
| ⚠️ … "dòng tiền **TREO** …" | Có bản ghi nạp/rút mà chưa dòng NAV nào chụp sau thời điểm tiền vào/ra ⇒ số tạm tính chưa tính dòng tiền đó | Thường tự hết ở lượt 00:20 / tối hôm sau khi có dòng NAV mới. Còn treo qua 1 phiên ⇒ kiểm `date`/`time_ict` của bản ghi trong `account_cash_flows.json` |
| ⚠️ `❌ phanh '…' KHÔNG ĐO ĐƯỢC ngay từ cấu hình (**THIẾU NGƯỠNG** / sổ hỏng)` | `data/trading_rules.json` thiếu/sai khoá ngưỡng (`risk_circuit_breakers.daily_loss_limit_pct`, `macro_kill_switches.C_episode_drawdown_breaker.episode_drawdown_limit_pct`, `capit_margin_lever.loan_package_id`), hoặc khoá số episode LỆCH câu chữ `trigger`, hoặc `episodes.json` hỏng. Phanh đó vẫn kèm số tạm tính nhưng không so được ngưỡng | Sửa đúng khoá nêu trong tin. Đổi GIÁ TRỊ ngưỡng cần user duyệt; monitor không có mặc định ngầm và không chọn hộ khi hai nơi lệch nhau |
| ⚠️ episode — "broker có vị thế dưới gói vay … nhưng KHÔNG có episode" | Đang vay mà phanh −15% không canh. Tin nêu các bản duyệt margin ĐỌC ĐƯỢC và vì sao chưa bản nào mở được episode (hoặc nói rõ không thấy bản duyệt nào) | Xác minh bản duyệt + ngày giải ngân, rồi `--open-episode <TK> --opened-date … --opened-by … --reason …` (điểm vào mặc định = giá chốt phiên trước ngày mở; đổi bằng `--entry-ref-date`) |
| ⚠️ episode — "đang mở nhưng broker KHÔNG còn vị thế nào dưới gói vay" | Đã tất toán mà episode chưa đóng | `--close-episode <TK> --closed-by … --reason …`. Phiên của chính ngày đóng VẪN đo với episode; từ phiên sau mới thôi |
| ⚠️/🚨 episode — "có bản duyệt margin MỚI ngày … trong lúc episode … còn mở" | Có thể là lần vay MỚI (điểm vào khác). Tin in cả hai số; số đem so ngưỡng là số XẤU hơn | Cùng episode (giải ngân thêm) ⇒ `--ack-approval <TK> --approval-date … --acked-by … --reason …` (bản duyệt phải có thật, ngày ≤ hôm nay). Lần vay mới ⇒ `--close-episode` rồi `--open-episode` |
| ⚠️ episode — "KHÔNG kiểm được broker có vị thế dưới gói vay" | Không có bản ghi `positions` sau 14:45 của phiên đó, hoặc bản ghi không có danh sách `payload.positions` | Việc vận hành: vì sao `dnse_raw_<ngày>.jsonl` thiếu bản ghi tối (EOD 19:10 / park 23:30) |
| ghi chú "phanh episode đo theo điểm vào XẤU hơn trong hai mốc …" | Lúc tự mở, phiên của ngày duyệt không đọc được positions ⇒ không biết vị thế có từ ngày duyệt hay phiên kế; monitor đo theo mốc xấu hơn | Biết ngày giải ngân thật ⇒ `--close-episode` rồi `--open-episode --entry-ref-date <mốc đúng>` |
| 📝 **LỆNH TAY** `--open-episode` / `--close-episode` / `--ack-approval` | Có người vừa đổi state của monitor (một lệnh tay có thể làm phanh episode xanh). Tin ghi ai, lý do, trước/sau; lượt đo kế nhắc lại trong notes | Người KHÔNG ra lệnh đó đọc và xác nhận là đúng. Sai ⇒ sửa bằng lệnh ngược lại (không mổ `episodes.json` tay) |
| 🛑 **MONITOR PHANH LỖ NAV LỖI** | Monitor tự hỏng (cấu hình/sổ không đọc được, không ghi được state-dir…); đêm đó không phanh nào được đo | Việc vận hành — sửa đúng lỗi in trong tin rồi chạy lại monitor |
| "sổ đã-gửi … không đọc được … tin này có thể trùng" | `alerts_sent.json` hỏng; monitor vẫn gửi và tự dựng lại sổ (bản hỏng cất ở `alerts_sent.json.corrupt.*`) | Không cần làm gì; xem vì sao file hỏng nếu lặp lại |

### Mã thoát
**Lượt chạy:** 0 cả ba phanh OK · 1 có phanh chạm / tạm tính vượt / không đo được (việc của NGƯỜI) ·
3 monitor lỗi hoặc không gửi được cảnh báo · **4 khoá bận** — một lượt khác (hoặc một lệnh tay) đang
giữ `data/loss_brake/.lock` quá 60s; lượt này bỏ, KHÔNG ghi status, không gửi. Một lần là bình
thường (lượt kia làm đúng việc đó); lặp lại ⇒ tìm tiến trình treo đang giữ khoá.

**`--health-line`:** 0 ✅ · 1 không đo được · **5 phanh chạm / tạm tính vượt** · 2 monitor không chạy
(file thiếu/cũ/hỏng) · 3 monitor lỗi / không gửi được cảnh báo.

### Chạy tay — hai điều dễ nhầm
- **Chạy tay TRƯỚC 21:50 ICT là đo phiên TRƯỚC**, không phải phiên hôm nay: phiên mặc định =
  phiên gần nhất mà NAV chốt PHẢI đã có (`NAV_EXPECTED_AFTER_ICT` = 21:50, sau lượt `nav_sync_retry`
  cuối 21:45). Muốn xem phiên hôm nay trước giờ đó: `--date <hôm nay>` (chạy khô).
- `--date` của một phiên khác phiên mặc định là CHẠY KHÔ (không ghi, không gửi) trừ khi thêm
  `--write-backdated`. `--now` bị TỪ CHỐI trên state sống — chạy thử thì thêm `--state-dir <tạm>`.

### Dòng buổi sáng trong ops_health (khối LOSSBRAKE)
rc=0 ✅ · rc=1 ⚠️ `[WARN-ONLY]` (không đo được — user quyết, KHÔNG route autofix; ca thuộc luật giảm
tin cũng nằm ở đây, kèm số tạm tính) · **rc=5 dòng 🔴 `PHANH LỖ NAV CHẠM NGƯỠNG — USER QUYẾT`** (phanh
chạm / tạm tính vượt; không mang `[WARN-ONLY]`, không route autofix, vẫn tính 1 warn) · rc=2 ⚠️ monitor
không chạy · rc=3 ⚠️ monitor có chạy nhưng lỗi, hoặc không gửi được cảnh báo. rc=2 và rc=3 là lỗi
vận hành ⇒ tới autofix.

### `ops_autofix` ĐƯỢC và KHÔNG ĐƯỢC làm gì
ĐƯỢC (chỉ với rc=2 / rc=3):
- chạy lại `python3 mike/bin/nav_loss_brake_monitor.py` cho phiên mặc định (idempotent; cảnh báo đã
  gửi không gửi lại; cảnh báo gửi lỗi được gửi bù);
- sửa lỗi hạ tầng quanh nó: cron không chạy, khoá `.lock` kẹt do tiến trình chết, thiếu thư mục log,
  biến `MIKE_LOSS_BRAKE_ALERT_SINK` lọt vào môi trường cron (monitor báo "tin CHỈ đi vào file sink").

KHÔNG ĐƯỢC (mọi rc):
- tạo/xoá `data/BOT_STOP`; sửa ngưỡng trong `data/trading_rules.json`, `DD_THRESHOLD` hay
  `QUIET_ESTIMATE_MARGIN_PP`;
- mở/đóng episode, `--ack-approval` — mỗi cái là một khẳng định về đòn bẩy cần người + bằng chứng;
- tạo `data/account_cash_flows.json` rỗng, hay sửa nó, để tin "KHÔNG có sổ dòng tiền" biến mất;
- xoá/sửa `alerts_sent.json`, `episodes.json`, `human_actions.jsonl` để "làm sạch" cảnh báo;
- dùng `--date … --write-backdated` (ghi đè status + gửi cảnh báo cho phiên cũ);
- xử lý dòng rc=1 / rc=5 dưới bất kỳ hình thức nào ngoài việc để nguyên cho người đọc.

### Cài lần đầu (sau khi merge commit monitor)
KHÔNG có bước seed — vòng 3 đã gỡ chuỗi mã loại trừ, sổ khai `managed_sleeve_flows.json` và 27 bản
khai máy sinh. `data/loss_brake/` tự tạo ở lượt chạy đầu.
```bash
cd /home/trido/thanhdt/WorkingClaude
R=mike/agents/Taylor/research/nav_loss_brake_20261012
# 1) phải ra đúng bảng trong $R/replay_full_history.txt (cho tới ngày cuối của file đó) — chỉ đọc
python3 mike/bin/nav_loss_brake_monitor.py --replay
# 2) một lượt chạy thử KHÔNG chạm state sống, cảnh báo vào file thay vì Discord
T=$(mktemp -d); MIKE_LOSS_BRAKE_ALERT_SINK=$T/sink.jsonl python3 mike/bin/nav_loss_brake_monitor.py --state-dir $T
# 3) cài cron (kb/cron_registry.md.proposed); lượt cron đầu tiên tự tạo data/loss_brake/
```

### Việc còn mở (không nằm trong nhánh này)
- **K12** (reviewer vòng 2) — ghi lại làm việc sau, chưa làm.
- **N13** `strategy_fit_dashboard.py` (@aaaf60a3b:879-908) vẫn grep chữ `risk_monitor` để kết luận phanh
  lỗ có ai canh — phải đổi sang đọc `data/loss_brake/status.json` sau khi monitor này cài xong.
- **N14** `data/loss_brake/` phải nằm trong phạm vi `fleet_backup.sh` + `backup_freshness_check.sh`
  (`episodes.json`, `human_actions.jsonl`, `alerts_sent.json` không dựng lại được từ nguồn khác).
- Bộ máy "phần bot quản lý" (chuỗi mã loại trừ, bẫy sleeve, `--correct-excluded`, công cụ backfill)
  đã gỡ; còn khôi phục được từ nhánh `backup/nav-loss-brake-r2-managed-20261012` (@e650f7ce0).

## Nhận tin "🟡 CỔNG DT5G SUY GIẢM" thì làm gì

**Tin này là gì.** Lượt `publish_gated_state` của chuỗi 19:00 (`bq_freshness_check.sh`
[pipeline-1]) vừa ghi `deploy_golive_dt5g_v4/golive_state_today.json` với `source` khác
`DT5G_macro`. Plan T+1 sẽ lập trên state đó. **Chỉ cảnh báo — pipeline và plan KHÔNG bị chặn**;
`DT4_only` là fail-closed đúng thiết kế (bỏ macro cap, giữ base + DT 4-gate). Tin đến qua 3
đường: Discord Trading Daily (1 tin/ngày/nguồn), bus `error` topic
`dt5g-gate-source-degraded-<ngày>`, và dòng ⚠️ trong báo cáo plan 21:00. Sáng hôm sau check 13
của `ops_health_check.sh` (08:20) nhắc lại nếu còn.

**Bước 1 — đọc bằng chứng ngay trong tin** (không đoán nguyên nhân):
- `dòng cổng tự in: «[get_gated_state] …»` = lý do cổng tự nêu ở chính lượt đó.
- `data/macro_health.json: status=…, ts=…` = báo cáo sức khoẻ feed cổng đã đọc.
- Tin ghi "không tìm thấy dòng [get_gated_state]" / "KHÔNG đọc được" ⇒ không có bằng chứng,
  xem `mike/logs/bq_freshness.log` quanh `[pipeline-1]`.

**Bước 2 — phân loại theo bằng chứng:**

| Thấy gì | Nghĩa là | Làm gì |
| --- | --- | --- |
| `health report N min old (> 1440)` | `macro_healthcheck` không chạy/không ghi trong 24h | Winston (data-ops): xem `daily_refresh` step healthcheck + log; chạy lại healthcheck, rồi chạy lại publisher |
| `status` khác `HEALTHY` | feed vĩ mô (SBV/VIX/SPX/breadth) bị báo không tin được | Winston sửa feed; KHÔNG ép cổng về DT5G bằng tay |
| `DT4_STALE` | bản DT4 đang dùng cũng cũ | Coi như sự cố dữ liệu: Winston kiểm `daily_refresh` trước khi tin state |
| nguồn lạ / thiếu trường `source` / file hỏng | publisher hoặc file state bất thường | Taylor (chủ `macro_state_live.py`) kiểm; không xác nhận được có áp macro cap hay không |

**Bước 3 — quyết định về plan (của user).** Plan không bị chặn. Khác biệt thực tế chỉ có khi
macro cap ĐANG siết: so `state` với `macro_state_dt5g` trong tin — bằng nhau ⇒ hôm nay cap không
đổi gì; `state` cao hơn `macro_state_dt5g` ⇒ plan đang chạy tỷ trọng cao hơn mức cổng đầy đủ cho
phép, cân nhắc khi duyệt.

**KHÔNG làm:** `touch`/sửa tay `golive_state_today.json` hay `macro_health.json` (đều là bằng
chứng của gate chặn tiền thật); không re-tune tham số cổng; không xoá
`data/gate_source_alert.json` để "tắt" tin.

**Không thấy tin dù nghi cổng suy giảm:** đọc trường `source` của `golive_state_today.json`; trong
`mike/logs/bq_freshness.log` tìm `WARN gate-source` (đã phát hiện), `gửi … THẤT BẠI` (kênh hỏng,
không có lượt tự gửi lại cùng ngày) hoặc `SKIP gate-source` (lượt publish không ghi file state —
khi đó `_assert_fresh_artifact` đã chặn và báo riêng).

## VN-Index có cổ tức (vnindex_total_return) — đọc 🔒, ack, đính chính, undo (áp 2026-10-21)

- **🔒 "seal bị chặn"** (từ `fund_bench_cron.sh`): `--update` rc=0 nhưng cổng G1/G4 giữ dòng ở `provisional`. Đầu tin có dòng
  "Cặp cần ack (ngày + giá trị)" — đó là thứ cần xem; bên dưới là bằng chứng (cắt 900 ký tự). Cảnh báo **lặp mỗi ngày T3-T7**
  tới khi dòng được seal (BQ lấp dữ liệu) hoặc có ack. G1 (không nối được) KHÔNG ack được — điều tra dữ liệu.
- **Ack G4 số mã / G4_MC** — sửa `data/benchmark/vnindex_tr_acks.json` (người xác nhận, chỉ khi mã thiếu không có GDKHQ cổ tức
  tiền ở D và D+1). Khoá ràng NGÀY + đúng giá trị đã xem; dựng lại ra số khác ⇒ ack mất hiệu lực:
  `"G4": [{"date":"2026-10-14","n_prev":100,"n":94,"confirmed_by":"<tên, giờ>","reason":"<lý do>"}]`
  `"G4_MC": [{"date":"2026-10-14","mc_prev":123456789012,"mc":130000000000,"confirmed_by":"…","reason":"…"}]`
  Mỗi mục phải là list các object; sai dạng ⇒ ValueError rõ ràng (cron báo lỗi, không seal theo giả định).
- **Đính chính dòng sealed** (đường DUY NHẤT): `--restate-sealed DATE… --reason "<số thật>" --confirmed-by "<tên, giờ>"` (thử
  trước bằng `--dry-run`). Từ chối nếu thiếu lý do/người, ngày không phải dòng sealed, dòng sealed khác cũng lệch, hoặc còn
  nổ G1/G4. Sổ `vnindex_tr_restatements.jsonl` chỉ-thêm, ghi TRƯỚC khi thay file; chạy lại sau crash (cùng ngày+lý do+người)
  được gắn `retry_of`.
- **Undo**: `--undo-last-restatement --reason … --confirmed-by …` (`--dry-run` trước). Chỉ hoàn tác đính chính CUỐI trong sổ,
  và chỉ khi md5 file hiện tại == `md5_after` của nó ⇒ dùng được TRƯỚC lần `--update` kế tiếp (cron T3-T7 sẽ đổi file). Ghi dòng
  `{"kind":"undo",…,"undoes":<md5_after>}`; không undo chồng. ⚠️ Undo đưa lại **byte-exact** cả những dòng đang nổ G4/G1 trước đính chính (không chạy lại seal-guard) và `--confirmed-by` là
  chữ tự do — chỉ người thật được điền.
- **Undo dở dang** (chết giữa ghi sổ và `os.replace`): sổ có dòng `undo` nhưng file chưa đổi; lệnh báo "undo đã GHI SỔ nhưng file CHƯA
  được thay" và từ chối chạy lại. Dữ liệu KHÔNG hỏng (file vẫn là bản sau đính chính, đã duyệt). Kiểm bằng md5: với `rows` = các dòng
  sổ, `cur` = bytes file, `V._md5(V.undo_restatement(rows[-2], cur)) == rows[-1]["md5_after"]` (True ⇒ có thể hoàn tất undo). Việc hoàn tất
  làm tay bởi Mike/Taylor (ghi tmp + `os.replace` dưới flock `vnindex_tr_daily.csv.lock`), KHÔNG xoá dòng sổ. Tương tự, đính chính chết
  trước khi thay file: lệnh báo "CHƯA từng được áp" — chạy lại `--restate-sealed` cùng lý do/người (sẽ gắn `retry_of`).
- Sổ restatements chỉ-thêm và có thể phình: đính chính một ngày sealed CŨ lưu toàn bộ phần sealed phía sau vào `rechained_sealed_before`
  (hàng trăm KB/dòng) — chấp nhận vì hiếm.
- **Dòng sổ 12:34 21/10 KHÔNG undo được bằng hàm** (ghi trước khi sổ giữ byte cũ; lệnh từ chối rõ ràng). Khôi phục từ
  `data/benchmark/vnindex_tr_daily.csv.bak_pre_restate_20261021` — bản sao này dọn được sau 24/10.

## NAV rc=2 "Tài sản phái sinh KHÔNG định giá được" — ký quỹ phái sinh (thêm 2026-11-17, branch feat/nav-deriv-margin-20261117, merge 8f51de633)
`daily_nav_snapshot.py` cộng `derivative.remainSecure` (SpaceX, sleeve ORB) vào NAV qua `bin/derivative_margin.live_gate`; cột `derivative_assets` cuối nav_history. **Fail-closed rc=2, KHÔNG ghi dòng** khi: (1) field chưa xác minh ≠ 0 (`usedSecure/pendingSecure/holdTaxAndFee/totalLoanDebt/pendingDepositWithdraw`), (2) có vị thế phái sinh MỞ (bỏ qua dòng CLOSED/openQuantity<=0 — `derivative_margin.py:74`; thống nhất định nghĩa với `orb_futures.net_position`), (3) có ký quỹ mà không đọc được vị thế. Xử lý: KHÔNG tự đoán — đọc stderr lý do, probe read-only `balances.derivative` + `positions(market_type=DERIVATIVE)`, xác minh công thức PnL/ký quỹ với DNSE rồi mới mở khoá field; backfill dùng `--from-raw` (không đọc vị thế). Chuyển tiền nội bộ cơ sở↔ký quỹ KHÔNG phải dòng vốn (triệt tiêu trong K); nạp từ account khác PHẢI khai `data/account_cash_flows.json` (cặp deposit/withdraw), thiếu ⇒ TWR lãi/lỗ giả ~±0,5%.
**Checklist go-live ORB (trước bật cờ LIVE):** probe `balances.derivative` + `positions` sau phiên LIVE đầu, TRƯỚC 19:00 ICT; chốt công thức NAV khi có vị thế mở (hiện rc=2 cố ý). Còn mở: `report_v2` chart_alloc chưa có phần ký quỹ phái sinh.
