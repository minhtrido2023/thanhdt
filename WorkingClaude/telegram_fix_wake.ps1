# Fix Windows wake-from-sleep for BA-system Telegram daily task.
#
# Issue: scheduled task doesn't fire when laptop is asleep at trigger time.
# Causes:
#   1. Windows power plan disables "Allow wake timers"
#   2. Modern Standby may suppress wake (newer laptops)
#   3. Task missing "Run task as soon as possible after a scheduled start is missed"
#   4. User logged out (task with "Run only when logged on" won't trigger)
#
# This script: enables wake timers in power plan + re-registers task with stronger settings.
# Run with admin privileges if possible (some settings need elevation).

$TaskName = 'BA-System Telegram Daily 1800'

Write-Host "=== Diagnostic ===" -ForegroundColor Cyan

# Check current power plan wake timer setting
Write-Host "`n1) Current wake timer setting in active power plan:"
$activePlan = (powercfg /getactivescheme) -replace '.*GUID: ', '' -replace '\s.*', ''
Write-Host "   Active plan GUID: $activePlan"

# Wake timer GUID is bd3b718a-0680-4d9d-8ab2-e1d2b4ac806d
# AC = on power, DC = on battery
Write-Host ""
Write-Host "   Wake timer on AC (plugged in):"
powercfg /query SCHEME_CURRENT SUB_SLEEP bd3b718a-0680-4d9d-8ab2-e1d2b4ac806d | Select-String "Current AC"
Write-Host "   Wake timer on DC (battery):"
powercfg /query SCHEME_CURRENT SUB_SLEEP bd3b718a-0680-4d9d-8ab2-e1d2b4ac806d | Select-String "Current DC"

# Check Modern Standby
$standby = powercfg /a
Write-Host ""
Write-Host "2) Sleep states available:"
$standby | ForEach-Object { Write-Host "   $_" }

Write-Host ""
Write-Host "=== Apply fixes ===" -ForegroundColor Cyan

# Enable wake timers on both AC and DC
Write-Host "`n3) Enabling wake timers (AC + DC):"
powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP bd3b718a-0680-4d9d-8ab2-e1d2b4ac806d 1
powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP bd3b718a-0680-4d9d-8ab2-e1d2b4ac806d 1
powercfg /setactive SCHEME_CURRENT
Write-Host "   OK Wake timers enabled" -ForegroundColor Green

# Show current wake timers scheduled
Write-Host "`n4) Currently scheduled wake timers:"
$waketimers = powercfg /waketimers
$waketimers | ForEach-Object { Write-Host "   $_" }

# Verify task exists
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $task) {
    Write-Host ""
    Write-Host "WARNING: Task '$TaskName' not found." -ForegroundColor Yellow
    Write-Host "Run telegram_register_task.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n5) Current task settings:"
$task.Settings | Select-Object WakeToRun, StartWhenAvailable, AllowStartIfOnBatteries, DisallowStartIfGoingOnBatteries | Format-List

# Update task to ensure WakeToRun + StartWhenAvailable are set
Write-Host "`n6) Updating task settings (WakeToRun + StartWhenAvailable + battery OK):"
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -StartWhenAvailable `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Set-ScheduledTask -TaskName $TaskName -Settings $Settings | Out-Null
Write-Host "   OK Task settings updated" -ForegroundColor Green

# Verify
$task2 = Get-ScheduledTask -TaskName $TaskName
Write-Host "`n7) Verified task settings after update:"
$task2.Settings | Select-Object WakeToRun, StartWhenAvailable, AllowStartIfOnBatteries | Format-List

Write-Host ""
Write-Host "=== Final notes ===" -ForegroundColor Cyan
Write-Host @"

If task still doesn't fire after sleep, check:
  a) Run 'Get-ScheduledTaskInfo -TaskName "$TaskName"' to see LastRunTime
  b) Check Event Viewer:
     Applications and Services Logs - Microsoft - Windows - TaskScheduler - Operational
  c) Modern Standby laptops (Surface, newer Dell/HP): wake timers may not fire
     during S0 standby. Solution: don't fully sleep at 18:00, OR use a desktop.
  d) Ensure you are logged in. Task is set 'Run only when user is logged on'.
     If you log out, task won't trigger.

To test wake-up:
  - Set short trigger (e.g., 2 minutes from now): Modify task in Task Scheduler GUI
  - Force sleep: rundll32.exe powrprof.dll,SetSuspendState 0,1,0
  - Wait for wake + task fire
"@
