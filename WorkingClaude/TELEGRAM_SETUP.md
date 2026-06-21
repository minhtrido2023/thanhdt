# BA-system Telegram Daily Notifier — Setup Guide

Daily watchlist tự động gửi qua Telegram lúc **18:00** mỗi ngày làm việc (Mon-Fri).

## 📋 Tổng quan

```
15:00 — VN market close
16:00 — ticker_1m table cập nhật xong
18:00 — Task Scheduler chạy telegram_run_daily.bat
       → telegram_recommend.py
       → bq query (latest ticker_1m + FA + 5-state)
       → format watchlist
       → POST to Telegram bot API
```

## 🚀 Quick setup (1 lần duy nhất)

### Bước 1 — Tạo Telegram bot

1. Mở Telegram, search **@BotFather**
2. Gõ `/newbot`, đặt tên (ví dụ "BA System Notifier")
3. BotFather trả về **bot_token** dạng `1234567890:ABCdefGHI...` — lưu lại

### Bước 2 — Lấy chat_id của bạn

1. Nhắn tin bất kỳ cho bot vừa tạo (mở chat với bot, gõ "/start")
2. Mở URL trong browser: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Thay `<TOKEN>` bằng bot_token thực
3. Tìm field `"chat":{"id":123456789,...}` → đó là **chat_id**
4. Lưu lại số `chat_id` (integer, có thể âm nếu là group)

### Bước 3 — Cấu hình credentials

```bash
# Trong WORKDIR
copy telegram_config.template.json telegram_config.json
# Edit telegram_config.json, điền bot_token + chat_id thực
```

⚠ **KHÔNG commit `telegram_config.json` lên git** — chứa secret.

### Bước 4 — Test gửi tay

```bash
cd C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
python telegram_recommend.py --dry-run     # build message, không gửi
python telegram_recommend.py               # send to Telegram thật
```

Sẽ thấy log:
```
[1/4] Target signal date: 2026-05-08
[2/4] Loading TA v10 + 5-state…
      428 tickers scored
      Market state: NEUTRAL (state=3)
[3/4] Building Telegram message…
[4/4] Sending to Telegram chat 123456789…
  Chunk 1/1 (951 chars): ✓ sent
  Attachment ba_book_bal_2026-05-08.csv: ✓ sent
  Attachment ba_book_vn30_2026-05-08.csv: ✓ sent

✓ Done.
```

Mở Telegram → bạn sẽ thấy message + 2 file CSV attachments.

### Bước 5 — Đăng ký scheduled task (18:00 hàng ngày)

**Option A: PowerShell (recommended)**

```powershell
# Right-click PowerShell → "Run as Administrator"
cd C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
powershell -ExecutionPolicy Bypass -File telegram_register_task.ps1
```

Hoặc chỉ đơn giản double-click `telegram_register_task.ps1` (chọn Run with PowerShell).

**Option B: Task Scheduler GUI thủ công**

1. Mở **Task Scheduler** (gõ `taskschd.msc`)
2. Right-click "Task Scheduler Library" → "Create Task..."
3. **General tab:**
   - Name: `BA-System Telegram Daily 18:00`
   - Run only when user is logged on (đảm bảo có access tới BQ)
4. **Triggers tab:** New →
   - Weekly, every 1 week
   - On: Monday, Tuesday, Wednesday, Thursday, Friday
   - At: 18:00:00
5. **Actions tab:** New →
   - Program: `C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude\telegram_run_daily.bat`
   - Start in: `C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude`
6. **Settings tab:**
   - Allow task to run on demand ✓
   - Run task as soon as possible after missed start ✓
   - Stop task if runs longer than: 30 minutes
7. Save (sẽ hỏi password user).

### Bước 6 — Verify task hoạt động

```powershell
# Liệt kê task
Get-ScheduledTask -TaskName "BA-System Telegram Daily 18:00"

# Chạy ngay để test
Start-ScheduledTask -TaskName "BA-System Telegram Daily 18:00"

# Xem log run
Get-Content telegram_run_2026-05-11.log
```

## 📨 Tùy chỉnh message

Edit `telegram_config.json`:
```json
{
  "bot_token": "...",
  "chat_id": "...",
  "send_charts": false,            // chưa hỗ trợ, để false
  "include_universe_stats": true,  // hiển thị distribution stats
  "include_f_overlay": true        // hiển thị F-system overlay info
}
```

## 🔧 Format của message

**Khi state = BULL/EX-BULL/NEUTRAL với signals:**
```
🏆 BA-SYSTEM LIVE — 2026-02-02
Sent: 2026-05-11 18:00 (next session T+1 entry)

Market regime: 🟢 BULL (state=4)
Strategy: 50% BAL+Fin/RE-max-4 + 50% VN30_BAL
PM: max=10pos · hold=45d · stop -20% · BL20 · T+3 min hold
ETF parking: 70% idle cash → VN30 ETF (NEUTRAL state only)

📋 BOOK A — BAL+Fin/RE-max-4 (50% NAV) (9 mã)
[table ticker / tier / close / score / FA / RSI]

📋 BOOK B — VN30_BAL (50% NAV) (1 mã)
[table]

🔄 F-system overlay (optional 20% capital)
   F_HAdapted target: +1.00x VN30 (LONG)
   Net VN30F exposure: +20.0% of total NAV

📊 Universe distribution
   BA-core: 9 mã | Compounder/info: 20 mã

💡 Execution checklist (T+1 next session)
   • BAL: 9 pos × 5% NAV = 45% deployed
   • VN30: 1 pos × 5% NAV = 5% deployed
   • Cash dư → deposit (defensive)  [hoặc → 70% VN30 ETF nếu NEUTRAL]
   • Stop -20%, hold 45d, BL20 after stop
```

**Khi state = BEAR/CRISIS:**
```
🏆 BA-SYSTEM LIVE — 2026-03-30
Market regime: 🔴 BEAR (state=2)
❌ BEAR/CRISIS regime — BA-system goes to cash. No new entries.
→ All capital defensive deposit.

F-system overlay (optional 20%):
  F_HAdapted target: -0.20x VN30 (SHORT)
  Net VN30F exposure: -4.0% of total NAV
```

**Kèm 2 file CSV** (BAL book + VN30 book) cho chi tiết đầy đủ.

## 📁 Files liên quan

| File | Mục đích |
|---|---|
| `telegram_recommend.py` | Script main — chạy engine + gửi message |
| `telegram_config.template.json` | Template, copy → `telegram_config.json` |
| `telegram_config.json` | **Secret credentials (DO NOT commit)** |
| `telegram_run_daily.bat` | Wrapper batch (Task Scheduler gọi này) |
| `telegram_register_task.ps1` | PowerShell script đăng ký scheduled task |
| `telegram_run_<date>.log` | Log file per day (auto-rotate 30 ngày) |

## 🐛 Troubleshooting

**Bot không gửi message:**
- Verify `bot_token` đúng (test qua `curl https://api.telegram.org/bot<TOKEN>/getMe`)
- Verify đã chat ít nhất 1 lần với bot (bot không thể gửi tin trước)
- Verify `chat_id` đúng kiểu (string vs int — JSON dùng string an toàn nhất)

**Task không chạy:**
- Task Scheduler History tab → xem lỗi
- Verify user còn login (task config "Run only when logged on")
- Verify Python in PATH (test `where python` trong cmd)
- Check `telegram_run_<today>.log` cho stack trace

**BQ query timeout:**
- ticker_1m query mất ~5-15s thường lệ
- Nếu mất > 30s, check internet + `bq.cmd` accessible

**Message bị split:**
- Nếu universe rất nhiều mã > limit 4000 chars, script tự split thành nhiều message
- Mỗi chunk có 0.5s delay để tránh rate limit

## 🔒 Bảo mật

- `telegram_config.json` chứa bot_token và chat_id — **secret**
- Add `telegram_config.json` vào `.gitignore`
- Nếu lỡ commit, REVOKE bot ngay qua @BotFather: `/revoke`, tạo bot mới

## 📅 Lưu ý timing

- VN ticker_1m thường update trong vòng ~30-60 phút sau market close (15:00)
- 18:00 chạy → đảm bảo data 2026-05-08 (Friday) sẽ có đủ ở 18:00 hôm sau session
- Có thể giảm xuống 16:30 nếu BQ data cập nhật sớm hơn
- Edit trigger time trong Task Scheduler hoặc re-run `telegram_register_task.ps1` sau khi modify
