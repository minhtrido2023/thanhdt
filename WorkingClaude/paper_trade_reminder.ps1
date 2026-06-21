Add-Type -AssemblyName PresentationFramework
$msg = @"
Paper-trade test BA-system Layer 3 timing rules đã chạy đủ 1 tháng.

Hôm nay (12/06/2026) là lúc review:
  • Miss rate thực tế vs backtest 0.03-1.6%
  • Fill savings vs OPEN baseline
  • Round-trips đầu tiên (entries ngày đầu vừa đủ 45d)

ACTION:
  Mở Claude Code, nói: "check paper trade"
  hoặc: "kiểm tra kết quả paper trade"

Files để xem nhanh:
  paper_trade_entries.csv
  paper_trade_exits.csv
"@
[System.Windows.MessageBox]::Show($msg, "Paper-Trade Review Reminder", "OK", "Information")
