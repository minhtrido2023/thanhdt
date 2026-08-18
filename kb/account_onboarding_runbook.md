# Runbook: giao quyền quản lý 1 tài khoản mới cho team Mike

> Kích hoạt khi user nói dạng "giao quyền quản lý tài khoản X cho team Mike" — làm theo
> đúng thứ tự dưới đây, không bỏ bước. Viết ra sau khi tổng quát hoá pipeline từ ca ZaloPay
> (2026-07-06) — xem `kb/coding_guidelines.md` §7 cho phần cơ chế `excluded_tickers`.

## 0. Cơ chế nền — đọc 1 lần, áp dụng mọi account

Từ 2026-07-06, các script cron dùng-chung (`preflight_check.sh`, `ops_health_check.sh`,
`send_plan_report.sh`, `eod_trading_report.sh`, `bq_freshness_check.sh`) **không còn
hardcode "SpaceX"** — chúng lặp qua `trading_bot.config.live_dnse_labels()` (mọi account
trong `secrets/trading_bot_accounts.json` có `enabled:true, mode:"live", broker:"dnse"`)
thông qua `bin/for_each_live_account.sh <script> [args]` (đã wire sẵn trong crontab).

**Nghĩa là:** một khi account mới có `enabled:true, mode:"live", broker:"dnse"` trong file
config, nó **tự động** được đưa vào: preflight sáng, ops-health-check 08:20/12:45, gửi plan
T+1 21:00 (second-chance 23:00), dispatch DollarBill lập plan (bước [pipeline-4] của
`bq_freshness_check.sh`), và báo cáo EOD 19:10 — **không cần sửa cron/code gì thêm** cho các
bước này.

**KHÔNG tự động** (vẫn cần 1 dòng cron riêng, vì đây là tiến trình thực thi lệnh thật, mỗi
account 1 tiến trình độc lập, không "lặp" được như các script trên):
- `run_bot.sh --account <label> --auto-otp` (09:05 sáng + 13:00 chiều)
- `bot_heartbeat.sh <label>` (mỗi 5 phút 09:00–14:55)
- `pkill -f "[b]ot_execute.py --account <label>"` (11:30, dừng giờ nghỉ trưa)

Đây là **bước cuối cùng, cố ý KHÔNG tự động hoá** — thêm 4 dòng cron này = bật đặt lệnh
thật, không người duyệt giữa chừng (chỉ có buffer 20' giữa preflight 08:45 và run_bot 09:05
để người xem cảnh báo). Với account CHƯA TỪNG có plan/thực thi trước đó, đây là lần đầu bot
tự chủ hoàn toàn trên tài khoản đó — **luôn hỏi lại user xác nhận rõ ràng trước khi thêm 4
dòng này**, dù mọi bước khác ở trên có thể tự làm không cần hỏi.

## 1. Xác định hồ sơ tài khoản (luôn cần, không thể tự động hoá — cần biết thực tế)

- Broker, account_id (tiểu khoản DNSE/PHS), cash-only hay có margin (package/loan_package_id).
- Có vị thế cũ (legacy) từ trước khi bot quản lý không? Nếu có: liệt kê mã + số lượng qua
  API thật (`positions()`), KHÔNG suy đoán.
- Với mỗi vị thế cũ: giữ hay bán? Nếu giữ vì lý do đặc thù (đang hạn chế giao dịch, thesis
  đầu tư riêng, chờ sự kiện) → đây là ứng viên cho `excluded_tickers` (xem bước 3).

## 2. Thêm account vào `secrets/trading_bot_accounts.json`

```json
{
  "label": "<Tên>",
  "enabled": true,
  "mode": "live",
  "broker": "dnse",
  "account_id": "<số tiểu khoản>",
  "credentials_file": null,
  "strategy": "V2.4",
  "excluded_tickers": ["..."],
  "note": "<bối cảnh: vì sao onboard, vị thế cũ, lý do exclude nếu có, ngày quyết định>"
}
```

`excluded_tickers` mặc định rỗng — chỉ điền khi bước 1 xác định có vị thế cần loại khỏi
rebalancing. Cơ chế enforce đã tổng quát sẵn ở `trading_bot/plan.py::filter_excluded_tickers()`
(gọi từ `bot_execute.py` ngay sau `load_plan()`) — không cần sửa code cho account mới.

## 3. Nếu có `excluded_tickers`: tính NAV khả dụng, KHÔNG dùng tổng NAV

```bash
bin/compute_active_nav.py --account <label>
```

Đây là cơ sở duy nhất đúng để size chiến lược V2.4 khi 1 phần NAV bị khoá trong vị thế
legacy. `bq_freshness_check.sh`'s dispatch DollarBill đã tự thêm ghi chú nhắc dùng lệnh này
khi phát hiện account có `excluded_tickers` khác rỗng — không cần nhắc tay DollarBill mỗi
lần.

## 4. Kiểm tra pháp lý/hạn chế giao dịch nếu có mã đặc thù

Nếu vị thế cũ đang bị HOSE cảnh báo/hạn chế (QĐ 544/QĐ 448) hoặc có sự kiện pháp lý — dispatch
`legal-vn` (native agent) để xác nhận tình trạng + điều kiện gỡ, đừng tự suy đoán. Ghi lại
nguồn (ngày nghiên cứu, agent) vào `note` của account profile.

## 5. Backtest/verify cẩn thận trước khi coi là "sẵn sàng" (yêu cầu chuẩn của user)

- Chạy `excluded_tickers_selfcheck.py` (mở rộng file này nếu cơ chế đổi, đừng viết file
  test song song mới — xem bài học ở `kb/coding_guidelines.md` §7 cuối).
- Nếu account có margin: xác minh `loan_package_id`, lãi suất, tỷ lệ ký quỹ qua API thật
  (Mafee probe), không lấy từ tài liệu cũ.
- Backtest chiến lược trên NAV khả dụng thật của account (không phải NAV giả định 1B mặc
  định) nếu quy mô khác biệt đáng kể so với account đã kiểm chứng (SpaceX).

## 6. Xác nhận Discord routing

Mọi account dùng CHUNG 3 kênh đã có (Trading Daily / DollarBill plan channel / Trading
report) — không cần kênh riêng per-account trừ khi user yêu cầu tách. Tên account luôn xuất
hiện trong tiêu đề message (đã tự động sau bản vá 2026-07-06 — preflight/ops-health-check đều
in `${ACCOUNT}` trong message).

## 7. Chạy thử pipeline lập-kế-hoạch trước khi bật thực thi

Sau bước 2 xong, `bq_freshness_check.sh` (17:30 ICT) sẽ **tự động** dispatch DollarBill lập
plan T+1 cho account mới cùng lúc với account đã có. Xem plan đầu tiên này kỹ trước khi bật
thực thi (bước 8) — đây là plan CHƯA từng được ai review cho account này.

## 8. Bật thực thi thật — LUÔN hỏi user trước (xem §0)

Sau khi user xác nhận, thêm 4 dòng cron (mẫu SpaceX, đổi `--account SpaceX` /
`bot_heartbeat.sh SpaceX` / log tên file → account mới):

```
5 2 * * 1-5 mike/bin/run_bot.sh --account <label> --auto-otp >> mike/logs/run_bot_<label>_$(date +\%Y-\%m-\%d).log 2>&1
*/5 2-7 * * 1-5 mike/bin/bot_heartbeat.sh <label> >> mike/logs/bot_heartbeat.log 2>&1
30 4 * * 1-5 pkill -f "[b]ot_execute.py --account <label>" >> mike/logs/lunch_stop.log 2>&1
0 6 * * 1-5 mike/bin/run_bot.sh --account <label> --auto-otp >> mike/logs/run_bot_<label>_$(date +\%Y-\%m-\%d)_afternoon.log 2>&1
```

## 9. Cập nhật KB

- `kb/current_ops.md` mục "Đang trading (LIVE)": thêm entry account mới theo mẫu SpaceX/
  ZaloPay đã có.
- Memory (`bin/remember.sh` hoặc file memory tương ứng) nếu có quyết định/lý do đáng nhớ
  cho lần sau.

---

**Lược sử:** viết 2026-07-06 sau khi tổng quát hoá automation từ ca ZaloPay (account thứ 2,
trước đó mọi script hardcode "SpaceX"). Helper: `trading_bot.config.live_dnse_labels()`,
`bin/for_each_live_account.sh`. Xem `kb/incidents/2026-07/` (các file `2026-07-06-*`) cho bối cảnh đầy đủ.
